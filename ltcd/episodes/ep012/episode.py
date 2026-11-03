"""Day 12 - COMMENT episode: @bloody_reckless_1995 "Take your cat to the theme park and go on rides, have fun"
(Instagram, day 11 reel, 0 likes). Warm and light: his kitten from day 11 rides on his head the whole time and stays a
calm little loaf through everything. The town is over: he runs out to the right into FUN PARK and lives there now.

LEAVE     The town, in front of the shelter. He reads the comment. A coaster rumble far off; the kitten's ears perk.
          He runs right, through the FUN PARK arch.
REVEAL    Ferris wheel, teacups, THE BIG ONE. The kitten's pupils go huge.
TEACUPS   He spins the wheel slowly. The kitten hops onto the wheel and bats it: faster... MUCH faster. He laughs.
          Dizzy after; the kitten is fine. It stares up at THE BIG ONE.
TALL      YOU MUST BE THIS TALL TO RIDE: short by a hair, tiptoes, still short. The kitten sits up: DING.
COASTER   Lap bar. KEEP ARMS AND LEGS INSIDE THE RIDE. Lift hill (clack clack), the hang at the top (heartbeat), the
          kitten slow-blinks at him, arms up. The drop, loop, airtime, loop 2, FLASH, brakes. Biggest real smile.
PHOTO     RIDE PHOTO: him screaming with joy, the kitten bored. It prints; the kitten keeps it in its mouth.
ASK       In the park in front of THE BIG ONE.
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import ramp, pulse, lerp, FLOOR_Y, Track
from ink import smooth, back_out
import numpy as np

FR = 1 / 30
NOW = [0.0]
KS = 0.62
# ---------------------------------------------------------------- places
SX0 = 34560.0; X0 = 540 + SX0                 # the town, in front of the shelter (day 11's ask spot)
SH = 35700.0; TREE = 36950.0; KBOX = 34800.0
BORDER = 38550.0                              # town ends / FUN PARK begins (hidden behind the gate)
XR = 39500.0; SXR = XR - 540                  # where he stops after the gate
TC = 40500.0                                  # teacup platform
FW = 40750.0                                  # ferris wheel
HS = 41950.0; LINE_Y = 370.0                  # YOU MUST BE THIS TALL sign (arm at y LINE_Y)
GATE_X = HS + 90
Y0 = FLOOR_Y - 40                             # track height in the stations

# ---------------------------------------------------------------- the coaster track
def catmull(knots, n=24):
    out = []
    P = [knots[0]] + list(knots) + [knots[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            u = k / n; u2, u3 = u * u, u * u * u
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u3) for j in (0, 1)))
    out.append(knots[-1]); return out
def loop_pts(cx, R, d, n=160):
    return [(cx + R * math.sin(th) + d * th, Y0 - R + R * math.cos(th)) for th in [2 * math.pi * k / n for k in range(n + 1)]]
L1X, L1R, L1D = 48000.0, 700.0, 80.0
L2X, L2R, L2D = 51200.0, 520.0, 70.0
EDGE_X = 45950.0
HANG_X = 45700.0
raw = catmull([(42500, Y0), (43350, Y0), (43750, Y0 - 220), (45300, Y0 - 1700), (45650, Y0 - 1890), (EDGE_X, Y0 - 1870),
               (46280, Y0 - 900), (46480, Y0 - 150), (46900, Y0), (L1X - 1, Y0)])
raw += loop_pts(L1X, L1R, L1D)
raw += catmull([(L1X + 2 * math.pi * L1D + 1, Y0), (49000, Y0), (49600, Y0 - 650), (50200, Y0), (L2X - 1, Y0)])[1:]
raw += loop_pts(L2X, L2R, L2D)
raw += catmull([(L2X + 2 * math.pi * L2D + 1, Y0), (52500, Y0), (55000, Y0)])[1:]
# resample to even spacing
TRK = [raw[0]]; SL = [0.0]
acc = 0.0
for a, b in zip(raw[:-1], raw[1:]):
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    if d < 1e-6: continue
    acc += d; TRK.append(b); SL.append(acc)
SL = np.array(SL); TX_ = np.array([p[0] for p in TRK]); TY_ = np.array([p[1] for p in TRK])
def track_at(s):
    s = max(0.0, min(SL[-1] - 1, s)); i = int(np.searchsorted(SL, s)) - 1; i = max(0, min(len(SL) - 2, i))
    u = (s - SL[i]) / max(1e-6, SL[i + 1] - SL[i])
    x = TX_[i] + (TX_[i + 1] - TX_[i]) * u; y = TY_[i] + (TY_[i + 1] - TY_[i]) * u
    j0, j1 = max(0, i - 3), min(len(SL) - 1, i + 4)
    ang = math.atan2(TY_[j1] - TY_[j0], TX_[j1] - TX_[j0])
    return x, y, ang
def s_of_x(x, after=0.0):
    for i in range(len(SL)):
        if SL[i] >= after and TX_[i] >= x: return SL[i]
    return SL[-1]
DRAW_TRK = TRK[::3]
S_START = s_of_x(43000)
S_EDGE = s_of_x(HANG_X)
S_BRAKE = s_of_x(52400, after=s_of_x(L2X + 600))
S_STOPX = 53400.0; S_STOP = s_of_x(S_STOPX, after=S_BRAKE)

# ---------------------------------------------------------------- timeline (first half fixed)
T_READ = 0.35
T_RUMBLE = 2.0
T_RUN, T_RUN1 = 2.7, 4.9
T_WOW = 5.2
CUT_CUPS = 6.3
T_HOP = 7.4
BATS = [7.95, 8.95]
T_SLOW = 10.7
T_HOPBACK = 11.45
CUT_DIZZY = 12.0
T_GAZE = 13.0
T_TILT = 13.5
CUT_SIGN = 15.5
T_UNDER = 16.3
T_TIPTOE = 17.2
T_KSIT = 18.4
T_DING = 18.65
CUT_BOARD = 20.7
T_BAR = 21.3
T_ROLL = 21.9
V_LIFT = 820.0
HANG = 2.9
G = 1250.0; KF = 80.0

# ---------------------------------------------------------------- simulate the ride
def simulate():
    dt = 1 / 600; t = T_ROLL; s = S_START; v = 0.0; out = [(T_ROLL, S_START)]
    t_hang = t_drop = t_stop = None; y_rel = s_rel = None; phase = "lift"
    while t < 80:
        if phase == "lift":
            tgt = V_LIFT if s < S_EDGE - 260 else max(40.0, V_LIFT * (S_EDGE - s) / 260)
            v += (tgt - v) * min(1.0, dt * 4); s += v * dt
            if s >= S_EDGE: s = S_EDGE; v = 0; phase = "hang"; t_hang = t
        elif phase == "hang":
            if t >= t_hang + HANG:
                phase = "ride"; t_drop = t; _, y_rel, _ = track_at(s); y_rel -= 140; s_rel = s; v = 60.0
        elif phase == "ride":
            _, y, _ = track_at(s)
            v2 = 60.0 ** 2 + 2 * G * (y - y_rel) - KF * (s - s_rel)
            v = math.sqrt(max(3600.0, v2)); s += v * dt
            if s >= S_BRAKE: phase = "brake"; vb = v; sb = s
        elif phase == "brake":
            a_ = vb * vb / (2 * (S_STOP - sb)); v = max(0.0, v - a_ * dt); s += v * dt
            if v <= 1.0 or s >= S_STOP: s = min(s, S_STOP); phase = "stop"; t_stop = t
        else:
            pass
        t += dt; out.append((t, s))
        if phase == "stop" and t > t_stop + 0.1: break
    return out, t_hang, t_drop, t_stop
_SIM, T_HANG0, T_DROP, T_STOP = simulate()
_ST = np.array([a for a, b in _SIM]); _SS = np.array([b for a, b in _SIM])
def car_s(t):
    if t <= T_ROLL: return S_START
    if t >= _ST[-1]: return _SS[-1]
    return float(np.interp(t, _ST, _SS))
def time_at_x(x, after):
    s0 = s_of_x(x, after=after)
    i = int(np.searchsorted(_SS, s0)); return float(_ST[min(i, len(_ST) - 1)])
def car_state(t): return track_at(car_s(t))
T_L1 = time_at_x(L1X - 300, S_EDGE)                 # into loop 1
T_AIR = time_at_x(49450, s_of_x(L1X + 600))         # airtime hill top
T_FLASH = time_at_x(L2X + 380, s_of_x(L2X + 200) + 1500)   # out of loop 2, the on-ride camera
T_BRAKE = time_at_x(52400, s_of_x(L2X + 600))

# ---------------------------------------------------------------- timeline (second half, from the ride)
CUT_FACE = T_HANG0 + 1.1
T_KLEAN = CUT_FACE + 0.35
T_ARMS = T_DROP - 0.35
CUT_PHOTO = T_STOP + 1.8
T_PLOOK = CUT_PHOTO + 0.3
T_KUP = CUT_PHOTO + 1.4
T_PRINT = CUT_PHOTO + 2.5
T_SHOW = T_PRINT + 0.7
T_GIVE = T_SHOW + 1.3
T_ASK = T_GIVE + 1.2
ASK_HOLD = 9.0
XE = S_STOPX + 880; SXE = XE - 540            # exit station: he stands here for the photo + the ask
SCREEN = (XE + 560, 830)

S = M.Scene(x0=SX0)
S.auto_blinks = False
S.floor = False
S.card("bloody_reckless_1995", "Take your cat to the theme park and go on rides, have fun", "0", t0=0.3)
CAM0 = (X0 + 230, 1010, 1.0)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0

# ================================================================ worlds
def spin_shift(t):
    """teacup scene: the background whips past as the cup spins."""
    if not (CUT_CUPS - FR <= t < CUT_DIZZY - FR): return 0.0
    return cup_phase(t) * 420.0

def park(cr, t):
    O.draw_park_world(cr, t, x0=BORDER, x1=70000)
    O.draw_ferris_wheel(cr, FW, FLOOR_Y, R=700, t=t)
    O.draw_bunting(cr, 39000, 39900, FLOOR_Y - 900, sid=12610)
    O.draw_bunting(cr, 41000, 41900, FLOOR_Y - 820, sid=12620)
    O.draw_track(cr, DRAW_TRK, FLOOR_Y)
    O.draw_cup_platform(cr, TC, FLOOR_Y, w=1500)
    for k, (dx, col) in enumerate(((-420, O.PARK_TEAL), (420, O.PARK_YEL))):
        if not (CUT_CUPS - FR <= t < CUT_DIZZY - FR):
            O.draw_teacup(cr, TC + dx, FLOOR_Y + 10, s=0.7, col=col, ph=t * 0.8 + k, sid=12880 + 20 * k)
    if not (CUT_CUPS - FR <= t < CUT_DIZZY - FR):
        O.draw_teacup(cr, TC, FLOOR_Y + 40, s=0.8, col=O.PARK_PINK, ph=t * 0.8, sid=12800)
    O.draw_height_sign(cr, HS, FLOOR_Y, line_y=LINE_Y, light=sign_light(t))
    O.draw_ride_gate(cr, GATE_X, FLOOR_Y, open_=smooth(ramp(t, T_DING + 0.25, T_DING + 0.8)))
    # stations
    for sx, label in ((43000, "THE BIG ONE"), (S_STOPX, "EXIT")):
        L.sketch_rect(cr, sx - 700, FLOOR_Y - 30, sx + 700, FLOOR_Y + 40, 5, sid=13200 + int(sx) % 7, fill=(0.75, 0.66, 0.58))
        for px in (sx - 650, sx + 650):
            L.sketch_rect(cr, px - 18, FLOOR_Y - 1000, px + 18, FLOOR_Y - 30, 5, sid=13210 + int(px) % 9, fill=(0.98, 0.95, 0.9))
        L.sketch_poly(cr, [(sx - 760, FLOOR_Y - 1000), (sx, FLOOR_Y - 1160), (sx + 760, FLOOR_Y - 1000)], 6, sid=13220 + int(sx) % 5, fill=O.PARK_TEAL)
        L.sketch_rect(cr, sx - 330, FLOOR_Y - 1080, sx + 330, FLOOR_Y - 940, 5, sid=13230 + int(sx) % 5, fill=(1, 1, 0.97))
        L.draw_text(cr, label, sx, FLOOR_Y - 1010, 84, color=(200, 50, 60), max_w=620)
    kx, ky = 42600, 560                                          # KEEP ARMS AND LEGS INSIDE (hangs from the roof)
    for dx in (-150, 150): L.sketch_line(cr, [(kx + dx, FLOOR_Y - 1000), (kx + dx, ky)], 3, sid=13240)
    L.sketch_rect(cr, kx - 230, ky, kx + 230, ky + 250, 6, sid=13241, fill=(1.0, 0.92, 0.35))
    for i, ln in enumerate(("KEEP ARMS", "AND LEGS", "INSIDE THE RIDE")):
        L.draw_text(cr, ln, kx, ky + 50 + i * 74, 48, color=(30, 30, 34))
    # the RIDE PHOTO booth at the exit
    O.draw_photo_screen(cr, SCREEN[0], SCREEN[1], w=640, h=480, inner=photo_inner)
    L.sketch_rect(cr, SCREEN[0] - 40, SCREEN[1] + 255, SCREEN[0] + 40, FLOOR_Y, 5, sid=13250, fill=(0.3, 0.3, 0.34))
    L.sketch_rect(cr, SCREEN[0] - 160, SCREEN[1] + 300, SCREEN[0] + 160, SCREEN[1] + 360, 5, sid=13251, fill=(0.22, 0.22, 0.26))  # print slot

def world(cr, t):
    NOW[0] = t
    sh = spin_shift(t)
    if sh:
        cr.save(); cr.translate(-(sh % 2600), 0)
        O.draw_park_world(cr, t, x0=TC - 6000, x1=TC + 9000)
        for k in range(-2, 5):
            O.draw_ferris_wheel(cr, TC + 900 + 2600 * k, FLOOR_Y, R=700, t=t)
            O.draw_bunting(cr, TC - 500 + 2600 * k, TC + 600 + 2600 * k, FLOOR_Y - 900, sid=12610)
        cr.restore()
        O.draw_cup_platform(cr, TC, FLOOR_Y, w=1500)
        return
    if t < T_RUN1 + 1.0:
        O.draw_town_world(cr, t, x0=20000, x1=BORDER)
        O.draw_tree(cr, TREE, FLOOR_Y, t, h=1900)
        O.draw_rescue_shelter(cr, SH, FLOOR_Y, t, window_cats=3, banner="ADOPTION DAY")
        O.draw_box(cr, KBOX, FLOOR_Y + 20, s=1.0, label="FREE KITTEN", sid=10300)
    park(cr, t)
    O.draw_park_gate(cr, BORDER, FLOOR_Y, t)
S.background(world)

def sign_light(t): return 1.0 if t >= T_DING else 0.0

# ================================================================ HIM: town -> park
S.set(0.0, "stand", "neutral", dur=0.0, smile=0.4)
S.read_card(T_READ, react="neutral", lines=2, dur=1.5, face="neutral")
S.set(T_RUMBLE + 0.35, "stand", "neutral", dur=0.25, look=(0.9, -0.3), smile=0.35)          # the rumble, off to the right
S.set(T_RUMBLE + 0.55, "stand", "neutral", dur=0.3, look=(0.9, -0.3), turn=0.5, brow=0.35, smile=0.45)
S.set(T_RUN - 0.12, "stand", "neutral", dur=0.1, look=(0.9, 0.0), turn=0.5, stretch=-0.15, smile=0.5)
S.set(T_RUN, "stand", "neutral", dur=0.15, run=1.0, look=(0.9, 0.0), turn=0.5, lean=0.12, smile=0.5)
S.xkeys.append((T_RUN, SXR, T_RUN1 - T_RUN, "smooth")); S.x = SXR
S.set(T_RUN1 - 0.1, "stand", "neutral", dur=0.15, run=0.0, look=(0.6, -0.5), stretch=-0.2, smile=0.5)
S.set(T_RUN1 + 0.1, "stand", "neutral", dur=0.3, ease="back", look=(0.7, -0.6), smile=0.5)
S.set(T_WOW + 0.3, "stand", "neutral", dur=0.4, look=(0.6, -0.7), smile=0.75, brow=0.45)
S.sfx(T_RUN, "whoosh", 0.05); S.sfx(T_RUN1 - 0.1, "skid", 0.05, dur=0.3)
def run_x(t): return 540 + lerp(SX0, SXR, smooth(ramp(t, T_RUN, T_RUN1)))
_ct = T_RUN - 0.05
while _ct < T_RUN1 + 0.3:
    S.camera(_ct, run_x(_ct + 0.05) + 230, 1010, lerp(1.0, 0.85, smooth(ramp(_ct, T_RUN, T_RUN + 0.4)) * (1 - smooth(ramp(_ct, T_RUN1 - 0.4, T_RUN1 + 0.3)))),
             dur=1 / 15, ease="linear")
    _ct += 1 / 15
S.camera(T_RUN1 + 0.35, XR + 1100, 700, 0.42, 0.9)                 # the reveal
def run_fx(cr, t, p, ly):
    if ly != "back" or not (T_RUN + 0.2 <= t < T_RUN1 - 0.2): return
    h = p["hip"]
    for k, dy in enumerate((-400, -200, 0)):
        L.motion_lines(cr, h[0] - 200, h[1] + dy, math.pi, n=1, length=360, alpha=0.7, sid=7110 + k, width=6)
S.prop(run_fx)

# ================================================================ TEACUPS
L.POSES["cup_sit"] = dict(head=(540, 772), neck=(540, 900), hip=(540, 1250), lelb=(470, 1010), lhand=(478, 1070),
                          relb=(610, 1010), rhand=(602, 1070), lhand_t="grip", rhand_t="grip",
                          lknee=(480, 1330), rknee=(600, 1330), lfoot=(500, 1420), rfoot=(580, 1420), nowalk=1.0)
WHEEL_Y = 1090
def cup_omega(t):
    w = 1.2
    w += 2.2 * smooth(ramp(t, BATS[0], BATS[0] + 0.3))
    w += 7.5 * smooth(ramp(t, BATS[1], BATS[1] + 0.5))
    return w * (1 - smooth(ramp(t, T_SLOW, CUT_DIZZY - 0.15)))
_CP = {}
def cup_phase(t):
    k = int(round((t - CUT_CUPS) * 60))
    if k <= 0: return 0.0
    if k in _CP: return _CP[k]
    ph = 0.0
    for i in range(k): ph += cup_omega(CUT_CUPS + i / 60) / 60
    _CP[k] = ph; return ph
CUPCAM = (TC, 1000, 0.92)
S.cut(CUT_CUPS - FR, cam=CUPCAM, x=TC - 540)
S.set(CUT_CUPS - FR, "cup_sit", "neutral", dur=0.0, look=(0.0, 0.2), smile=0.5, lag=0.3)
S.set(CUT_CUPS + 0.6, "cup_sit", "neutral", dur=0.4, look=(0.0, 0.6), smile=0.55, lag=0.3)
S.set(T_HOP + 0.1, "cup_sit", "neutral", dur=0.3, look=(0.0, 0.9), smile=0.5, brow=0.3, lag=0.3)      # the kitten hops down
S.set(BATS[0] + 0.2, "cup_sit", "neutral", dur=0.25, look=(0.0, 0.0), smile=0.6, brow=0.5, eyescale=1.08, lag=0.3)
S.set(BATS[1] + 0.25, "cup_sit", "delighted", dur=0.3, look=(0.0, 0.0), mouth="grin", lag=0.3)
S.set(BATS[1] + 0.9, "cup_sit", "laughing", dur=0.4, laugh=1.0, lag=0.3)
S.set(T_SLOW + 0.4, "cup_sit", "delighted", dur=0.5, laugh=0.0, lag=0.3)
def cup_hook(t, p):
    if not (CUT_CUPS - FR <= t < CUT_DIZZY - FR): return p
    w = cup_omega(t); ph = cup_phase(t)
    if w < 4.5:
        p["turn"] = 0.7 * math.sin(ph * 1.0) * min(1.0, 1.4 - w / 4.5 + 0.3)
    p["curl"] = p.get("curl", 0.0) - 0.08 * w
    sway = 10 * math.sin(ph * 2.0) * min(1.0, w / 3)
    for j in ("head", "neck"): p[j] = (p[j][0] + sway, p[j][1])
    wx = TC
    p["lhand"] = (wx - 75 + 8 * math.sin(ph * 2), WHEEL_Y + 6); p["rhand"] = (wx + 75 + 8 * math.sin(ph * 2 + 1), WHEEL_Y + 6)
    p["lhand_t"] = p["rhand_t"] = "grip"
    return p
S.hook(cup_hook)
S.sfx(CUT_CUPS + 0.2, "squeak", 0.02)
for bt in BATS: S.sfx(bt, "pat", 0.07); S.sfx(bt + 0.05, "whoosh", 0.04 + 0.03 * (bt > 8))
S.sfx(BATS[1] + 0.3, "wind", 0.04, dur=T_SLOW - BATS[1])
def cup_fx(cr, t, p, ly):
    if not (CUT_CUPS - FR <= t < CUT_DIZZY - FR): return
    ph = cup_phase(t); w = cup_omega(t)
    if ly == "back":
        O.draw_teacup(cr, TC, FLOOR_Y + 40, s=1.0, col=O.PARK_PINK, part="back", sid=12800)
        return
    O.draw_cup_wheel(cr, TC, WHEEL_Y, s=1.0, ang=ph * 3.0)
    O.draw_teacup(cr, TC, FLOOR_Y + 40, s=1.0, col=O.PARK_PINK, part="front", ph=ph * 2.0, sid=12800)
    if w > 4:                                                     # speed streaks
        a = min(1.0, (w - 4) / 4)
        for k, yy in enumerate((700, 900, 1250, 1400)):
            L.motion_lines(cr, TC - 380 + 760 * ((t * 3 + k * 0.37) % 1), yy, math.pi, n=1, length=320, alpha=0.6 * a, sid=7200 + k, width=6)
S.prop(cup_fx)

# ================================================================ DIZZY, the gaze up
XD = TC + 700
S.cut(CUT_DIZZY - FR, cam=(XD + 120, 1000, 0.95), x=XD - 540)
S.set(CUT_DIZZY - FR, "stand", "dizzy", dur=0.0, smile=0.5, lag=1.0)
S.set(T_GAZE - 0.25, "stand", "neutral", dur=0.3, look=(0.0, -0.3), smile=0.5)
S.set(T_GAZE + 0.25, "stand", "neutral", dur=0.3, look=(0.6, -0.9), tilt=-0.08, smile=0.4, brow=0.3)   # follows the kitten's gaze
S.set(T_TILT + 0.9, "stand", "neutral", dur=0.4, look=(0.6, -1.0), tilt=-0.12, smile=0.15, brow=0.55, eyescale=1.1)
S.sfx(T_TILT + 1.6, "gulp", 0.08)
def dizzy_hook(t, p):
    if not (CUT_DIZZY - FR <= t < T_GAZE): return p
    k = 1 - smooth(ramp(t, T_GAZE - 0.6, T_GAZE))
    p["lean"] = 0.0
    sw = 26 * math.sin((t - CUT_DIZZY) * 5.5) * k
    for j in ("head", "neck", "hip", "lelb", "relb", "lhand", "rhand"): p[j] = (p[j][0] + sw * (1.0 if j in ("head", "neck") else 0.5), p[j][1])
    p["tilt"] += 0.12 * math.sin((t - CUT_DIZZY) * 5.5) * k
    return p
S.hook(dizzy_hook)
S.camera(T_TILT, 44600, 300, 0.33, 1.4)                        # up... up... THE BIG ONE
S.sfx(CUT_DIZZY + 0.2, "boing", 0.03)

# ================================================================ YOU MUST BE THIS TALL
XH = HS - 255
SIGNCAM = (HS - 10, 900, 0.95)
S.cut(CUT_SIGN - FR, cam=SIGNCAM, x=XH - 540 - 500)
S.set(CUT_SIGN - FR, "stand", "neutral", dur=0.0, look=(0.8, 0.0), smile=0.5)
S.walk_to(CUT_SIGN + 0.05, XH - 540, T_UNDER - CUT_SIGN - 0.3)
S.set(T_UNDER, "stand", "neutral", dur=0.3, look=(0.5, -0.9), smile=0.45)                    # looks up at the arm
S.set(T_UNDER + 0.55, "stand", "neutral", dur=0.3, look=(0.8, -0.6), smile=0.2, brow=0.3)     # red light
S.sfx(T_UNDER + 0.45, "boop", 0.06)
S.set(T_TIPTOE, "stand", "neutral", dur=0.35, tiptoe=1.0, stretch=0.16, look=(0.4, -1.0), smile=0.2, brow=0.6, lhand_t="fist", rhand_t="fist")
S.sfx(T_TIPTOE + 0.5, "boop", 0.06)
S.set(T_TIPTOE + 0.9, "stand", "neutral", dur=0.3, tiptoe=1.0, stretch=0.16, look=(0.0, 0.0), smile=0.05, worry=0.4)        # still short. us.
S.set(T_KSIT + 0.1, "stand", "neutral", dur=0.25, tiptoe=1.0, stretch=0.16, look=(0.2, -1.0), smile=0.1, brow=0.4)
S.set(T_DING + 0.15, "stand", "neutral", dur=0.2, ease="back", look=(0.7, -0.6), smile=0.7, brow=0.5, eyescale=1.08)
S.sfx(T_DING, "ding", 0.12); S.sfx(T_DING + 0.3, "squeak", 0.03)
S.set(T_DING + 0.8, "stand", "neutral", dur=0.3, look=(0.0, -1.0), smile=0.75)               # looks up at the kitten
S.walk_to(T_DING + 1.4, XH - 540 + 520, CUT_BOARD - T_DING - 1.6)

# ================================================================ THE BIG ONE
L.POSES["rider"] = dict(lelb=(500, 1010), lhand=(590, 1040), relb=(600, 1010), rhand=(650, 1040), lhand_t="grip", rhand_t="grip",
                        lknee=(640, 1110), rknee=(660, 1125), lfoot=(720, 1230), rfoot=(740, 1245), nowalk=1.0)
L.POSES["rider_up"] = dict(L.POSES["rider"]); L.POSES["rider_up"].update(lelb=(450, 680), lhand=(420, 520), relb=(630, 680), rhand=(660, 520),
                                                                         lhand_t="open", rhand_t="open")
SEAT = (-60.0, -190.0)                                        # hip, car-local
RIDE = dict(lag=0.0, nowalk=1.0)
S.cut(CUT_BOARD - FR, cam=(43000, 1000, 0.8))
S.set(CUT_BOARD - FR, "rider", "neutral", dur=0.0, look=(0.6, 0.0), smile=0.65, turn=0.4, **RIDE)
S.set(T_BAR + 0.3, "rider", "neutral", dur=0.25, look=(0.0, 0.6), smile=0.6, turn=0.2, **RIDE)
S.sfx(T_BAR + 0.3, "clack", 0.08)
S.set(T_ROLL + 0.3, "rider", "neutral", dur=0.4, look=(0.0, 0.0), smile=0.65, **RIDE)
# lift hill: smile fades, nerves build
LIFT_END = T_HANG0
S.set(T_ROLL + 2.0, "rider", "neutral", dur=1.0, look=(-0.6, 0.8), smile=0.35, brow=0.2, turn=0.3, **RIDE)     # looks down
S.set(LIFT_END - 1.2, "rider", "neutral", dur=1.0, look=(0.0, 0.0), smile=0.0, brow=0.35, worry=0.5, sweat=0.4, quiver=0.3, **RIDE)
k_ = T_ROLL + 0.5
while k_ < T_HANG0 - 0.1:
    S.sfx(k_, "clack", 0.035); k_ += 0.2
# the hang: close-up, heartbeat, the kitten's slow blink
S.set(T_HANG0 + 0.2, "rider", "neutral", dur=0.4, look=(0.7, 0.9), smile=-0.1, brow=0.5, worry=0.7, sweat=0.7, quiver=0.5, eyescale=1.1, pupil=0.75, **RIDE)
for k in range(5):
    tk = T_HANG0 + 0.4 + k * 0.5
    S.sfx(tk, "thud", 0.05); S.sfx(tk + 0.16, "thud", 0.035)
S.set(T_KLEAN + 0.2, "rider", "neutral", dur=0.4, look=(0.0, -1.0), smile=0.0, brow=0.6, worry=0.5, sweat=0.6, quiver=0.3, **RIDE)   # looks up: the kitten
S.set(T_KLEAN + 1.1, "rider", "neutral", dur=0.4, look=(0.0, -1.0), smile=0.3, lid=0.9, brow=0.2, sweat=0.3, **RIDE)               # slow-blinks back
S.set(T_KLEAN + 1.6, "rider", "neutral", dur=0.3, look=(0.0, 0.0), smile=0.6, brow=0.3, **RIDE)
S.set(T_ARMS, "rider_up", "delighted", dur=0.25, ease="back", mouth="grin", brow=0.6, **RIDE)
S.sfx(T_ARMS + 0.1, "whoosh", 0.03)
# the ride
S.set(T_DROP + 0.15, "rider_up", "delighted", dur=0.2, mouth="scream", open=1.0, eyescale=1.2, brow=0.9, curl_up=1.0, **RIDE)
S.set(T_STOP - 0.3, "rider", "delighted", dur=0.5, mouth="grin", eyescale=1.05, brow=0.6, curl_up=0.6, breath_rate=2.6, **RIDE)
S.set(T_STOP + 0.8, "rider", "happy", dur=0.6, smile=1.0, breath_rate=1.8, look=(0.0, 0.0), **RIDE)
S.sfx(T_DROP, "slide_down", 0.06, dur=0.9)
S.sfx(T_DROP + 0.3, "wind", 0.06, dur=T_BRAKE - T_DROP)
S.sfx(T_L1, "whoosh", 0.07); S.sfx(T_AIR - 0.2, "whoosh", 0.05); S.sfx(T_FLASH - 0.6, "whoosh", 0.06)
S.sfx(T_FLASH, "tick", 0.12); S.sfx(T_FLASH + 0.02, "pop", 0.05)
S.flash(T_FLASH, 0.35)
S.sfx(T_BRAKE, "skid", 0.06, dur=0.9); S.sfx(T_BRAKE + 0.1, "poof", 0.05)
S.blink(T_STOP + 1.2)

def float_amt(t):
    """airtime: the rider (and more so the kitten) lifts off the seat."""
    return 50 * pulse(t, T_DROP + 0.25, 0.25) + 60 * pulse(t, T_AIR, 0.25)
def in_car(t, p):
    if not (CUT_BOARD - FR <= t < CUT_PHOTO - FR): return p
    x, y, a = car_state(t)
    c, s_ = math.cos(a), math.sin(a)
    fl = float_amt(t) * 0.5
    sx, sy = SEAT[0], SEAT[1] - fl
    X, Y = x + sx * c - sy * s_, y + sx * s_ + sy * c
    h = p["hip"]
    for j in L.JOINTS:
        dx, dy = p[j][0] - h[0], p[j][1] - h[1]
        p[j] = (X + dx * c - dy * s_, Y + dx * s_ + dy * c)
    p["tilt"] = p.get("tilt", 0.0) + a
    return p
S.hook(in_car)
def car(cr, t, p, ly):
    if t < CUT_BOARD - FR: x, y, a = track_at(S_START); bar = 0.0
    elif t >= CUT_PHOTO - FR: x, y, a = track_at(S_STOP); bar = 0.0
    else: x, y, a = car_state(t); bar = smooth(ramp(t, T_BAR, T_BAR + 0.3))
    if CUT_CUPS - FR <= t < CUT_DIZZY - FR: return
    if ly == "back": O.draw_coaster_car(cr, x, y, a, part="back")
    else: O.draw_coaster_car(cr, x, y, a, part="front", bar=bar, sign="THE BIG ONE")
S.prop(car)

# camera through the ride
def cam_ride(t):
    x, y, a = car_state(t)
    if t < T_HANG0:                                         # lift: follow, a little ahead
        u = smooth(ramp(t, T_ROLL, T_ROLL + 1.5))
        return (x + 250, y - 500 * u - 100, lerp(0.8, 0.58, u))
    if t < CUT_FACE: return (EDGE_X + 250, FLOOR_Y - 1350, 0.36)      # wide: the drop below him
    if t < T_DROP:                                                   # close-up on his face + the kitten
        c, s_ = math.cos(a), math.sin(a); hx_, hy_ = SEAT[0] + 20, SEAT[1] - 430
        return (x + hx_ * c - hy_ * s_ + 40, y + hx_ * s_ + hy_ * c + 60, 1.05)
    for cx, R in ((L1X, L1R), (L2X, L2R)):
        if cx - R - 300 < x < cx + R + 700 and t > T_DROP + 1.0:
            return (cx + 120, Y0 - R - 150, 0.55)
    return (x + 150, min(y - 450, 1000), 0.55)
S.cut(T_HANG0 - FR, cam=cam_ride(T_HANG0))
S.cut(CUT_FACE - FR, cam=cam_ride(CUT_FACE))
S.cut(T_DROP - FR, cam=(car_state(T_DROP)[0] + 150, car_state(T_DROP)[1] - 450, 0.55))
_ct = T_ROLL
while _ct < T_HANG0 - 0.05:
    S.camera(_ct, *cam_ride(_ct), dur=0.1, ease="linear"); _ct += 0.1
_ct = T_DROP
_prev = None
while _ct < CUT_PHOTO - 0.1:
    tgt = cam_ride(_ct)
    if _prev: tgt = tuple(lerp(_prev[i], tgt[i], 0.35) for i in range(3))
    S.camera(_ct, *tgt, dur=1 / 15, ease="linear"); _prev = tgt; _ct += 1 / 15

# ================================================================ RIDE PHOTO
S.cut(CUT_PHOTO - FR, cam=(XE + 330, 960, 0.9), x=SXE)
S.set(CUT_PHOTO - FR, "stand", "happy", dur=0.0, look=(0.9, -0.3), smile=0.9, turn=0.5, lag=1.0, nowalk=0.0)
S.set(T_PLOOK + 0.6, "stand", "neutral", dur=0.4, look=(0.9, -0.4), smile=0.6, turn=0.5, brow=0.4)
S.set(T_KUP, "stand", "neutral", dur=0.35, look=(0.0, -1.0), smile=0.4, brow=0.5)                    # up at the kitten
S.set(T_KUP + 0.6, "stand", "neutral", dur=0.35, look=(0.0, -1.0), smile=0.6, lid=0.85)              # slow blink back
S.set(T_PRINT - 0.2, "stand", "neutral", dur=0.3, look=(0.9, 0.3), smile=0.7, turn=0.4)
L.POSES["show_photo"] = dict(relb=(660, 880), rhand=(700, 760), rhand_t="grip")
L.POSES["give_up"] = dict(relb=(650, 700), rhand=(600, 540), rhand_t="grip")
S.set(T_SHOW, "show_photo", "happy", dur=0.3, ease="back", look=(0.0, 0.0), smile=0.95)
S.set(T_GIVE, "give_up", "happy", dur=0.35, look=(0.0, -0.9), smile=0.8)
S.set(T_GIVE + 0.6, "stand", "happy", dur=0.35, look=(0.0, 0.0), smile=0.75)
S.sfx(T_PRINT, "zip", 0.05); S.sfx(T_GIVE + 0.35, "pat", 0.05)
S.camera(T_PLOOK, SCREEN[0] - 60, 860, 1.3, 0.5)                   # the photo, big
S.camera(T_KUP - 0.2, XE + 200, 940, 1.0, 0.4)
S.camera(T_SHOW - 0.2, XE + 120, 960, 1.0, 0.5)

def photo_inner(cr, x0, y0, w, h):
    """the on-ride photo: him screaming with joy, arms up... the kitten loafed and bored."""
    cr.rectangle(x0, y0, w, h); cr.set_source_rgb(0.62, 0.82, 0.98); cr.fill()
    sc = h / 800.0
    cr.save(); cr.translate(x0 + w * 0.5, y0 + h * 1.28); cr.scale(sc, sc); cr.translate(-470, -FLOOR_Y)
    for k in range(3): O.draw_cloud(cr, 0 + 520 * k, FLOOR_Y - 850 + 90 * (k % 2), s=0.8)
    O.draw_track(cr, [(-900, FLOOR_Y - 20), (2200, FLOOR_Y - 20)], supports=False)
    q = L.pose("rider_up", "delighted", mouth="scream", open=1.0, eyescale=1.2, brow=0.9, nowalk=1.0)
    dx, dy = 540 + SEAT[0] - q["hip"][0], FLOOR_Y - 20 + SEAT[1] - q["hip"][1]
    for j in L.JOINTS: q[j] = (q[j][0] + dx, q[j][1] + dy)
    q = L.constrain(q); q["breath_ph"] = 0.0; q["curl"] = -0.4
    O.draw_coaster_car(cr, 540, FLOOR_Y - 20, 0.0, part="back")
    L.draw_guy(cr, 0.0, q, 0.0)
    hx, hy = q["head"]
    O.draw_cat(cr, hx + 5, hy - 104, s=KS, t=0.0, kind="loaf", col="black", look=(0.0, 0.3), blink=0.55, sid=2000, swish=0.0)
    O.draw_coaster_car(cr, 540, FLOOR_Y - 20, 0.0, part="front", bar=1.0, sign="THE BIG ONE")
    cr.restore()

# ================================================================ THE ASK (in the park, in front of the exit)
S.t = T_ASK
S.the_ask(T_ASK, hold=ASK_HOLD, keep=dict(mouth="auto", smile=0.55))

# ================================================================ the kitten (always on his head)
def kitten_spot(p, lift=0.0):
    hx, hy = p["head"]; a = p.get("tilt", 0.0)
    ox, oy = 5.0, -104.0 - lift
    return hx + ox * math.cos(a) - oy * math.sin(a), hy + ox * math.sin(a) + oy * math.cos(a), a
def kitten(cr, t, p, ly):
    if ly != "front": return
    look = (0.0, 0.0); kind = "loaf"; blink = 0.0; pupil = 1.0; lift = 0.0; tilt_k = 0.6
    if T_RUMBLE + 0.1 <= t < T_RUN + 0.6: look = (0.9, -0.4); kind = "sit"
    if T_RUN1 <= t < CUT_CUPS: look = (0.7, -0.6); kind = "sit"
    if CUT_DIZZY - FR <= t < T_TILT + 2.0:
        look = (0.0, 0.0) if t < T_GAZE else (0.9, -0.9)
        if CUT_DIZZY + 0.4 <= t < CUT_DIZZY + 1.2: blink = math.sin(math.pi * (t - CUT_DIZZY - 0.4) / 0.8)
    if CUT_SIGN - FR <= t < CUT_BOARD - FR:
        look = (0.3, -0.9) if t >= T_UNDER else (0.6, 0.0)
        if t >= T_KSIT: kind = "sit"; look = (0.4, -0.9); lift = 30 * smooth(ramp(t, T_KSIT, T_KSIT + 0.2)) * (1 - smooth(ramp(t, T_DING + 0.8, T_DING + 1.1)))
        if t >= T_DING + 0.8: look = (0.0, 0.9); kind = "loaf" if t >= T_DING + 1.3 else "sit"
    if CUT_BOARD - FR <= t < CUT_PHOTO - FR:
        lift = float_amt(t); tilt_k = 1.0
        if t >= T_DROP: look = (0.0, 0.0); blink = 0.45 + 0.4 * (T_AIR - 0.2 <= t < T_AIR + 0.4)
    if CUT_PHOTO - FR <= t:
        look = (0.6, 0.3) if t < T_KUP else (0.0, 0.9)
        if T_KUP + 0.3 <= t < T_KUP + 1.1: blink = math.sin(math.pi * (t - T_KUP - 0.3) / 0.8)
    # teacups: it hops down onto the wheel, bats it, rides it, hops back
    if CUT_CUPS - FR <= t < CUT_DIZZY - FR:
        hx, hy, a = kitten_spot(p)
        wx, wy = TC + 8, WHEEL_Y - 8
        if t < T_HOP:
            O.draw_cat(cr, hx, hy, s=KS, t=t, kind="loaf", col="black", look=(0.0, 0.9), sid=2000, tilt=a * 0.6); return
        if t < T_HOP + 0.4:
            u = (t - T_HOP) / 0.4; x = lerp(hx, wx, u); y = lerp(hy, wy, u) - 140 * 4 * u * (1 - u)
            O.draw_cat(cr, x, y, s=KS, t=t, kind="fall", col="black", look=(0.0, 0.8), sid=2000); return
        if t < T_HOPBACK:
            bat = max(pulse(t, BATS[0], 0.12), pulse(t, BATS[1], 0.12))
            O.draw_cat(cr, wx, wy, s=KS * 0.95, t=t, kind="sit", col="black", look=(-0.6 + 0.6 * bat, 0.9), sid=2000,
                       blink=0.5 if t > BATS[1] + 0.6 else 0.0)
            if bat > 0.05:
                px_, py_ = wx - 30 - 60 * bat, wy - 40 + 30 * bat
                L.sketch_line(cr, [(wx - 20, wy - 70), (px_, py_)], 14, sid=2390)
                L.sketch_ellipse(cr, px_, py_, 14, 11, 4, sid=2391, fill=O.CAT_COLS["black"][0])
            return
        if t < T_HOPBACK + 0.35:
            u = (t - T_HOPBACK) / 0.35; x = lerp(wx, hx, u); y = lerp(wy, hy, u) - 140 * 4 * u * (1 - u)
            O.draw_cat(cr, x, y, s=KS, t=t, kind="fall", col="black", look=(0.0, -0.8), sid=2000); return
        O.draw_cat(cr, hx, hy, s=KS, t=t, kind="loaf", col="black", look=(0.0, 0.0), blink=0.4, sid=2000, tilt=a * 0.6); return
    hx, hy, a = kitten_spot(p, lift)
    if CUT_FACE - FR <= t < T_DROP and t >= T_KLEAN:              # leans over his forehead and slow-blinks at him
        u = smooth(ramp(t, T_KLEAN, T_KLEAN + 0.35)) * (1 - smooth(ramp(t, T_DROP - 0.5, T_DROP - 0.2)))
        bl = math.sin(math.pi * min(1.0, max(0.0, (t - T_KLEAN - 0.5) / 0.9)))
        O.draw_cat(cr, hx + 30 * u, hy + 55 * u, s=KS, t=t, kind="loaf", col="black", look=(-0.2, 1.0), blink=bl, sid=2000,
                   tilt=a * 0.6 + 0.45 * u); return
    O.draw_cat(cr, hx, hy, s=KS, t=t, kind=kind, col="black", look=look, blink=blink, sid=2000, tilt=a * tilt_k)
    if t >= T_GIVE + 0.35:                                         # it keeps the ride photo (in its mouth)
        mini_photo(cr, hx - 85, hy - 30, 0.38, a * tilt_k - 0.35)
S.prop(kitten)

def mini_photo(cr, x, y, s, ang=0.0):
    cr.save(); cr.translate(x, y); cr.rotate(ang + 0.12); cr.scale(s, s)
    L.sketch_rect(cr, -90, -70, 90, 70, 5, sid=13300, fill=(1, 1, 1))
    cr.save(); cr.rectangle(-78, -58, 156, 100); cr.clip(); cr.translate(-78, -58)
    photo_inner(cr, 0, 0, 156, 100); cr.restore()
    cr.restore()

def printed_photo(cr, t, p, ly):
    if ly != "front" or not (T_PRINT <= t < T_GIVE + 0.35): return
    if t < T_SHOW:
        u = smooth(ramp(t, T_PRINT, T_PRINT + 0.4))
        mini_photo(cr, SCREEN[0], SCREEN[1] + 330 + 60 * u, 0.9)
    else:
        hx, hy = p["rhand"]
        mini_photo(cr, hx + 20, hy - 70, 0.9 if t < T_GIVE else lerp(0.9, 0.38, ramp(t, T_GIVE, T_GIVE + 0.35)))
S.prop(printed_photo)

# ---------------------------------------------------------------- sounds: mews, a distant park bell
SR = L.SR
def _t(d): return np.arange(int(d * SR)) / SR
def place(buf, sig, t0, g):
    i = int(t0 * SR)
    if 0 <= i < len(buf): m = min(len(sig), len(buf) - i); buf[i:i + m] += sig[:m] * g
def meow(f0=700, d=0.45):
    tt = _t(d); u = tt / d
    f = f0 * (0.85 + 0.35 * np.sin(np.pi * u ** 0.8)) * (1 + 0.02 * np.sin(2 * np.pi * 7 * tt))
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)
    env = np.minimum(1, tt / 0.03) * np.minimum(1, (d - tt) / 0.12) * (0.6 + 0.4 * np.sin(np.pi * u))
    return (sig * env * 0.35).astype(np.float32)
def bell(f=1046.5, d=0.9):
    tt = _t(d); return ((np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2.76 * f * tt)) * np.exp(-tt / 0.25) * 0.3).astype(np.float32)
def rumble(d=1.4):
    tt = _t(d); nz = np.random.default_rng(4).standard_normal(len(tt))
    lp = np.convolve(nz, np.ones(200) / 200, mode="same")
    return (lp * np.sin(np.pi * tt / d) ** 2 * 9.0).astype(np.float32)
def extra(n):
    buf = np.zeros(n, np.float32)
    place(buf, rumble(1.5), T_RUMBLE - 0.1, 0.35)
    place(buf, bell(1046.5), T_RUMBLE + 0.15, 0.25); place(buf, bell(1318.5), T_RUMBLE + 0.4, 0.22)
    place(buf, meow(1250, 0.3), T_RUMBLE + 0.3, 0.3)
    place(buf, meow(1350, 0.25), T_HOP + 0.05, 0.25)
    place(buf, meow(1300, 0.3), T_KSIT + 0.05, 0.3)
    place(buf, meow(1200, 0.35), T_KLEAN + 0.4, 0.22)
    place(buf, meow(1300, 0.3), T_KUP + 0.2, 0.22)
    place(buf, meow(1350, 0.25), T_GIVE + 0.45, 0.22)
    return buf * 0.5
_orig_soften = L._soften
def _soften_plus(x): return _orig_soften(x) + extra(len(x))
L._soften = _soften_plus

if __name__ == "__main__":
    print(f"hang {T_HANG0:.2f} drop {T_DROP:.2f} L1 {T_L1:.2f} air {T_AIR:.2f} flash {T_FLASH:.2f} brake {T_BRAKE:.2f} "
          f"stop {T_STOP:.2f} photo {CUT_PHOTO:.2f} ask {T_ASK:.2f} end {S.t:.2f}", file=sys.stderr)
    S.render("day012.mp4")
