"""Day 32: IG @cr1ms0n_h0rnet: "Make dinosaurs come back to life and ride one". See BEATS.md.
He reads it in the cemetery (the rose falls out of his teeth), runs right through the graveyard fog to the MUSEUM OF
NATURAL HISTORY at night. In the dinosaur hall: amber with a mosquito, a DNA syringe, a jab in the T. rex skeleton's
toe. Nothing. The water cup ripples. The bones glow, FLASH: a living T. rex. It steps down, sniffs him, ROARS (the bat
is blown off his curl). He pulls a saddle. He rides it bucking through the hall, out through the giant glass wall,
down the night street; three pterodactyls catch up. Red light: it stops. Its nose itches, its tiny arms can't reach;
he scratches it. The ask on the sidewalk with his T. rex.
"""
import sys, os, math, random, wave
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
import numpy as np
import moves as M
import ltcd as L
import objects as O
import character as C
from ltcd import Track, ramp, lerp, pulse, FLOOR_Y
from ink import smooth, sketch_line, draw_text

# the cemetery (day 31) is drawn with day 31's own code
_spec = importlib.util.spec_from_file_location("ep031_episode", os.path.join(HERE, "..", "ep031", "episode.py"))
E31 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(E31)
E31.T_GATE = -1e9                      # the gate is smashed open (day 31)

FR = 1 / 30
sk_rect, sk_poly, sk_circ, sk_ell = O.sketch_rect, O.sketch_poly, O.sketch_circle, O.sketch_ellipse
INKC = (0.07, 0.07, 0.09)
BONE = (0.93, 0.89, 0.78)
GLOWG = (0.45, 1.0, 0.45)

# ================================================================ places
GX = E31.GX
HIM3 = E31.HIM3                       # where he did the day 31 ask
FOG_C = GX + 8700.0                   # the graveyard fog (right edge of the cemetery)
PX = 11000000.0                       # the museum plaza (front)
P_FOG = PX - 1900.0; P_STOP = PX - 900.0
MX = 11100000.0                       # the dinosaur hall
SKX = MX + 900.0                      # the skeleton (near foot x) on its plinth
RS = 1.35                             # T. rex scale
PL = 110.0                            # plinth height
HIMX = SKX + 930.0                    # where he stands in the hall
DESK_X = SKX + 1480.0
CUP_X, CUP_Y = DESK_X - 130, FLOOR_Y - 330
POSTS = (SKX + 2000.0, SKX + 2350.0, SKX + 2700.0)
PTER_H = (MX + 4300.0, MX + 4700.0, MX + 5100.0)
NORUN_X = MX + 5600.0
GW = MX + 6600.0                      # the giant glass wall
X_STOP = GW + 6200.0                  # where the T. rex stops at the red light
LIGHT_X = X_STOP + 1150.0
AX = X_STOP + 680.0                   # him at the ask

def cam(x, z, fs=1530):
    return (x, FLOOR_Y - (fs - 960) / z, z)

# ================================================================ timeline
T_READ = 0.3
T_DROP = 2.5
T_TURN = 3.0; T_RUN = 3.2; CUT_PLAZA = 4.6
T_LOOKUP = 5.5
CUT_HALL = 6.4
T_AMBER = 7.8; POP_AMBER = T_AMBER + 2.1
T_SWAP = 10.9
T_SYR = 11.0; POP_SYR = T_SYR + 2.1
T_JAB = 13.6; T_FILL0, T_FILL1 = 13.8, 14.6
T_TOSS_A = 14.8
CUT_TOE = 15.2; T_PLUNGE0, T_PLUNGE1 = 15.5, 16.1
CUT_BACK = 16.3
T_US = 16.9; T_TOSS_S = 17.6
T_TWITCH = 18.6; T_RIP1 = 19.0; T_EYES = 19.3; T_RIP2 = 20.0; T_HEAD = 20.6
T_HEART1 = (19.8, 20.3, 20.8)
T_GLOW0 = 21.2; T_FLASH = 22.0; T_SMOKE1 = 22.9
T_PLAQUE = 22.4
T_LOOKAROUND = 22.6; T_LOOKDOWN = 23.2
T_STEP = ((23.6, 24.0), (24.2, 24.6))
T_STIFF = 24.4
T_SNIFF0 = 25.0; T_SNIFFS = (25.4, 25.9, 26.3)
T_ROAR0, T_ROAR1 = 26.6, 28.3
T_BLINK = 28.8; T_WIPE0, T_WIPE1 = 29.1, 29.7
T_HEADUP = 29.7; T_CARD = 29.9
T_SADDLE = 30.3; POP_SADDLE = T_SADDLE + 2.1
T_NARROW = 32.7; T_HEART2 = (32.8, 33.1)
CUT_RIDE = 33.4; T_HEART3 = (33.7, 34.0); T_REINS = 34.3
T_BOLT = 34.6
T_RODEO = 35.4
T_SEEGLASS = 38.0
T_SMASH = 38.8; T_LAND = 40.0
T_ARM2 = 41.0; T_SMILE = 41.6
T_PTER0 = 41.6
T_RED = 43.2; T_SKID0, T_SKID1 = 43.6, 44.4
T_PERCH = 44.6
T_ITCH0, T_ITCH1 = 45.0, 46.4
T_SCR0, T_SCR1 = 46.6, 47.8
T_GREEN = 47.9
CUT_ASK = 48.3
T_ASK = 48.6; HOLD = 9.5

# ================================================================ the T. rex (one timeline: skeleton -> alive -> ride)
X_BOLT0 = SKX + 220.0
X_GLASS = GW - 560.0
X_LEAP1 = GW + 1500.0
X_GAL1 = X_STOP - 300.0

def rex(t):
    """returns X (near foot), lift, pitch, face, st (DINO dict)."""
    st = dict(O.DINO); st.update(s=RS, look=(-0.5, 0.15), smile=0.0, lid=0.0, mouth=0.0, arms=0.0, walk=0.0)
    X, lift, pitch, face = SKX, PL, 0.0, 1
    if t < T_STEP[0][0]:
        pass
    elif t < CUT_RIDE:
        # two steps forward off the plinth
        (a0, a1), (b0, b1) = T_STEP
        if t < a1:
            u = ramp(t, a0, a1); X = SKX + 110 * smooth(u); lift = PL * (1 - smooth(u)) + 60 * math.sin(math.pi * u)
            st["walk"] = math.pi * u
        elif t < b0:
            X = SKX + 110; lift = 0.0
        elif t < b1:
            u = ramp(t, b0, b1); X = SKX + 110 + 110 * smooth(u); lift = 40 * math.sin(math.pi * u); st["walk"] = math.pi + math.pi * u
        else:
            X = SKX + 220; lift = 0.0
    else:
        X, lift = X_BOLT0, 0.0
    # --- the ride
    if CUT_RIDE <= t < T_BOLT:
        X = X_BOLT0
    elif T_BOLT <= t < T_SMASH:
        u = ramp(t, T_BOLT, T_SMASH, "linear")
        X = lerp(X_BOLT0, X_GLASS, u ** 1.35)
        st["walk"] = (t - T_BOLT) * 15.0
        pitch = 0.16 * math.sin((t - T_BOLT) * 2 * math.pi * 1.6) * min(1, (t - T_BOLT) * 2)
        lift = 70 * abs(math.sin((t - T_BOLT) * math.pi * 1.6))
    elif T_SMASH <= t < T_LAND:
        u = ramp(t, T_SMASH, T_LAND, "linear")
        X = lerp(X_GLASS, X_LEAP1, u); lift = 620 * 4 * u * (1 - u); pitch = lerp(-0.18, 0.15, u)
        st["walk"] = 0.0
    elif T_LAND <= t < T_SKID0:
        u = ramp(t, T_LAND, T_SKID0, "linear")
        X = lerp(X_LEAP1, X_GAL1, u)
        st["walk"] = (t - T_LAND) * 16.0
        land = math.exp(-(t - T_LAND) * 6)
        pitch = 0.22 * land + 0.06 * math.sin((t - T_LAND) * 16)
        lift = 40 * abs(math.sin((t - T_LAND) * 8))
    elif T_SKID0 <= t < CUT_ASK:
        u = ramp(t, T_SKID0, T_SKID1)
        X = lerp(X_GAL1, X_STOP, 1 - (1 - u) ** 2)
        pitch = 0.22 * math.sin(math.pi * u) * (1 if t < T_SKID1 else 0)
    elif t >= CUT_ASK:
        X = X_STOP
    # --- faces
    if T_FLASH <= t < CUT_RIDE:
        st["look"] = (-0.3, 0.0)
        if t >= T_LOOKAROUND: st["look"] = (-1.0, -0.2) if t < T_LOOKAROUND + 0.3 else ((0.6, -0.1) if t < T_LOOKDOWN else (-0.6, 0.9))
        if T_LOOKDOWN <= t: st["look"] = (-0.6, 0.9)
        if T_ROAR0 - 0.1 <= t < T_ROAR1: st["look"] = (-0.4, 0.6); st["brow"] = -0.5
        if t >= T_SADDLE + 1.0: st["look"] = (-0.3, 1.0)
        if t >= T_NARROW: st["lid"] = 0.42; st["brow"] = -0.4
        if T_FLASH + 0.25 <= t < T_FLASH + 0.42: st["lid"] = 1.0
    # head down to sniff / roar, back up after
    if T_SNIFF0 <= t < CUT_RIDE:
        down = smooth(ramp(t, T_SNIFF0, T_SNIFF0 + 0.5)) * (1 - 0.8 * smooth(ramp(t, T_HEADUP, T_HEADUP + 0.6)))
        pitch = 0.42 * down
        for ts in T_SNIFFS:
            pitch += 0.03 * pulse(t, ts, 0.08)
        if T_ROAR0 <= t < T_ROAR1:
            k = smooth(ramp(t, T_ROAR0, T_ROAR0 + 0.15)) * (1 - smooth(ramp(t, T_ROAR1 - 0.2, T_ROAR1)))
            st["mouth"] = k; pitch += -0.08 * k + 0.012 * math.sin(t * 40) * k
    if CUT_RIDE <= t < T_BOLT:
        st["look"] = (1.0, -0.3); st["lid"] = 0.3
    if T_BOLT <= t < T_SKID1:
        st["look"] = (-1.0, 0.0); st["brow"] = -0.3; st["mouth"] = 0.25 if t < T_LAND else 0.0
        if T_LAND <= t: st["smile"] = 0.5
    if T_SKID1 <= t < CUT_ASK:
        st["look"] = (-0.8, -0.6); st["smile"] = 0.2
        if T_ITCH0 <= t < T_ITCH1:
            st["arms"] = 1.0; st["look"] = (-1.0, 0.8); st["lid"] = 0.35; st["brow"] = -0.6; st["worry"] = 0.6
            pitch = 0.08 + 0.02 * math.sin(t * 30)
        if T_SCR0 <= t:
            st["eyes"] = "happy"; st["smile"] = 1.0; pitch = -0.06 * smooth(ramp(t, T_SCR0, T_SCR0 + 0.4))
        if t >= T_SCR1 + 0.3: st["eyes"] = "normal"; st["look"] = (-0.6, 0.0); st["smile"] = 0.8; pitch = 0.0
    if t >= CUT_ASK:
        st["look"] = (-0.5, 0.6); st["smile"] = 0.7; pitch = 0.05; st["eyes"] = "normal"
    return X, lift, pitch, face, st

def rex_world(X, lift, pitch, face, lx, h):
    """a point in the T. rex's own (draw_dino, left-facing, x=0) coords -> world."""
    s = RS
    px, py = 40 * s, FLOOR_Y - 400 * s
    x, y = lx * s, FLOOR_Y - h * s
    c, s_ = math.cos(-pitch), math.sin(-pitch)
    dx, dy = x - px, y - py
    x, y = px + dx * c - dy * s_, py + dx * s_ + dy * c
    return (X - face * x, y - lift)

def rex_pt(t, which):
    X, lift, pitch, face, st = rex(t)
    x, y = O.trex_pt(X, st, face, pitch, which)
    return (x, y - lift)

def seat(t):
    X, lift, pitch, face, st = rex(t)
    wb = O._walkbob(st)
    x, y = rex_world(X, lift, pitch, face, 215, 615)
    return (x, y - wb)

def alive(t): return t >= T_FLASH + 0.05

def draw_rex(cr, t):
    if not alive(t) or t < CUT_HALL: return
    X, lift, pitch, face, st = rex(t)
    cr.save(); cr.translate(0, -lift)
    blink = 0.0
    for b in (24.9, 30.9, 36.0, 42.8, 51.5, 55.0):
        if b <= t < b + 0.16: blink = math.sin(math.pi * (t - b) / 0.16)
    O.draw_trex(cr, X, st, t, face=face, pitch=pitch, blink=blink)
    cr.restore()
    if t >= CUT_RIDE - FR:
        draw_saddle_on(cr, t)

# ================================================================ the skeleton
def draw_skeleton(cr, t):
    if alive(t) or t < CUT_HALL - FR: return
    s = RS
    glow = 0.0
    if t >= T_GLOW0:
        glow = ramp(t, T_GLOW0, T_GLOW0 + 0.4) * (0.65 + 0.35 * math.sin(t * 30))
    jaw = 0.25 * pulse(t, T_RIP2, 0.12)
    tail = 0.10 * pulse(t, T_TWITCH, 0.12) + 0.05 * pulse(t, T_RIP2 + 0.1, 0.1)
    cr.save(); cr.translate(SKX, -PL); cr.scale(-1, 1)
    P = lambda dx, h: (dx * s, FLOOR_Y - h * s)
    hx, hy = -200 * s, FLOOR_Y - 900 * s
    def bone(pts, w, sid):
        if glow > 0.01:
            sketch_line(cr, pts, w * s + 26, sid=sid, amp=0.3, color=GLOWG, alpha=0.45 * glow)
        sketch_line(cr, pts, w * s + 9, sid=sid, amp=0.3, color=INKC)
        sketch_line(cr, pts, w * s, sid=sid, amp=0.3, color=BONE)
    # support rods (behind)
    for (dx, h) in ((60, 560), (380, 330)):
        x0, y0 = P(dx, h); sketch_line(cr, [(x0, y0), (x0, FLOOR_Y)], 8, sid=32010 + dx, amp=0.2, color=(0.25, 0.25, 0.3))
    # far leg
    bone([P(110, 410), P(100, 240), P(120, 60), P(60, 18)], 20, 32020)
    # tail (twitches at the tip) + spine
    sp = [P(150, 650), P(260, 560), P(380, 440), P(520, 300)]
    tip = P(660, 140); tip = (tip[0] + 260 * tail * s, tip[1] - 160 * tail * s)
    sp.append(tip)
    bone(sp, 18, 32030)
    for k in range(9):
        u = k / 9
        a, b = sp[min(3, int(u * 4))], sp[min(4, int(u * 4) + 1)]
        f = (u * 4) % 1
        x, y = lerp(a[0], b[0], f), lerp(a[1], b[1], f)
        sk_circ(cr, x, y - 10, (17 - 1.3 * k) * s, 4, sid=32040 + k, fill=BONE)
    # neck
    neck = [P(150, 650), P(70, 760), (hx + 60 * s, hy + 60 * s)]
    bone(neck, 22, 32050)
    # ribs
    for k in range(7):
        x0, y0 = P(-60 + 40 * k, 640 - 25 * k)
        bone([(x0, y0), (x0 - 40 * s, y0 + 120 * s), (x0 - 10 * s, y0 + (210 - 10 * k) * s)], 9, 32060 + k)
    # pelvis
    sk_ell(cr, *P(70, 430), 90 * s, 50 * s, 5, sid=32070, fill=BONE)
    # near leg
    bone([P(40, 420), P(10, 230), P(40, 60), P(-30, 16)], 24, 32080)
    for j in range(3):
        cx_, cy_ = P(-50 - 25 * j, 14)
        sketch_line(cr, [(cx_ + 30 * s, cy_), (cx_, cy_ + 12 * s)], 8, sid=32085 + j, color=INKC)
    # tiny arms
    bone([P(-150, 640), P(-190, 600), P(-200, 560)], 9, 32090)
    # skull + jaw
    sk_pts = [(hx + 95 * s, hy - 45 * s), (hx + 80 * s, hy - 118 * s), (hx - 20 * s, hy - 122 * s), (hx - 90 * s, hy - 96 * s),
              (hx - 185 * s, hy - 50 * s), (hx - 185 * s, hy + 14 * s), (hx - 150 * s, hy + 22 * s), (hx + 70 * s, hy + 22 * s)]
    if glow > 0.01:
        cr.save(); cr.move_to(*sk_pts[0])
        for q in sk_pts[1:]: cr.line_to(*q)
        cr.close_path(); cr.set_source_rgba(*GLOWG, 0.4 * glow); cr.set_line_width(40); cr.stroke(); cr.restore()
    cr.save(); cr.translate(hx + 70 * s, hy + 22 * s); cr.rotate(-jaw)
    sk_poly(cr, [(0, 0), (-212 * s, 0), (-190 * s, 40 * s), (-60 * s, 52 * s)], 6, sid=32101, fill=BONE)
    for k in range(5):
        tx_ = -195 * s + k * 36 * s
        sk_poly(cr, [(tx_, 0), (tx_ + 11 * s, -15 * s), (tx_ + 22 * s, 0)], 3, sid=32102 + k, fill=(1, 1, 1))
    cr.restore()
    sk_poly(cr, sk_pts, 7, sid=32110, fill=BONE)
    for k in range(4):
        tx_ = hx - 140 * s + k * 40 * s
        sk_poly(cr, [(tx_, hy + 21 * s), (tx_ + 10 * s, hy + 38 * s), (tx_ + 20 * s, hy + 21 * s)], 3, sid=32112 + k, fill=(1, 1, 1))
    sk_ell(cr, hx + 20 * s, hy - 58 * s, 30 * s, 34 * s, 5, sid=32120, fill=(0.08, 0.07, 0.09))
    if glow > 0.05:
        cr.arc(hx + 20 * s, hy - 58 * s, 13 * s, 0, 2 * math.pi); cr.set_source_rgba(*GLOWG, glow); cr.fill()
    sk_ell(cr, hx - 120 * s, hy - 40 * s, 30 * s, 20 * s, 4, sid=32121, fill=(0.08, 0.07, 0.09))
    sk_ell(cr, hx - 30 * s, hy - 40 * s, 24 * s, 26 * s, 4, sid=32122, fill=(0.08, 0.07, 0.09))
    cr.restore()
    # crackle
    if glow > 0.05:
        r = random.Random(int(t * 15))
        for k in range(4):
            a = rex_world(SKX, PL, 0.0, 1, r.uniform(-250, 500), r.uniform(100, 900))
            pts = [a]
            for j in range(4): pts.append((pts[-1][0] + r.uniform(-90, 90), pts[-1][1] + r.uniform(-90, 90)))
            sketch_line(cr, pts, 6, sid=32130 + k, amp=0.2, color=(0.75, 1.0, 0.7), alpha=glow)

def draw_flash_smoke(cr, t):
    if not (T_FLASH - 0.05 <= t < T_SMOKE1): return
    u = ramp(t, T_FLASH, T_SMOKE1)
    cx, cy = SKX - 100, FLOOR_Y - 700
    for k in range(14):
        a = k / 14 * 2 * math.pi
        r = 300 + 600 * u
        O.draw_smoke_puff(cr, cx + math.cos(a) * r * 0.9, cy + math.sin(a) * r * 0.6, 260 * (1 - 0.6 * u), alpha=0.9 * (1 - u) ** 1.3)
    if u < 0.5:
        O.draw_smoke_puff(cr, cx, cy, 700 * (1 - u), alpha=0.95 * (1 - 2 * u))

# ================================================================ the plinth + plaque
def draw_plinth(cr, t):
    if t < CUT_HALL - FR or t >= CUT_RIDE + 4: return
    x0, x1 = SKX - 1000, SKX + 420
    sk_rect(cr, x0, FLOOR_Y - PL, x1, FLOOR_Y, 6, sid=32200, fill=(0.40, 0.38, 0.45))
    sketch_line(cr, [(x0 + 10, FLOOR_Y - PL + 18), (x1 - 10, FLOOR_Y - PL + 18)], 3, sid=32201, color=(0.55, 0.53, 0.6))
def draw_plaque(cr, t):
    if t < CUT_HALL - FR: return
    px, py = SKX - 380, FLOOR_Y - PL / 2
    ang, dy = 0.0, 0.0
    sy = 1.0
    if t >= T_PLAQUE:
        u = ramp(t, T_PLAQUE, T_PLAQUE + 0.35)
        ang = 0.25 * math.sin(math.pi * u); dy = (FLOOR_Y - 20 - py) * u * u
        px -= 120 * u; sy = 1 - 0.7 * smooth(ramp(t, T_PLAQUE + 0.3, T_PLAQUE + 0.4))
    cr.save(); cr.translate(px, py + dy); cr.rotate(-ang); cr.scale(1, sy)
    sk_rect(cr, -280, -48, 280, 48, 5, sid=32210, fill=(0.80, 0.68, 0.36))
    if sy > 0.5:
        draw_text(cr, "T. REX", 0, -22, 34, color=(40, 30, 10))
        draw_text(cr, "EXTINCT. 66,000,000 YEARS", 0, 20, 28, color=(40, 30, 10))
    cr.restore()

# ================================================================ the cup of water on the guard desk
RIPS = (T_RIP1, T_RIP2, T_STEP[0][1], T_STEP[1][1], T_HEART1[0], T_HEART1[2])
BIG = (T_STEP[0][1], T_STEP[1][1])
def draw_desk(cr, t):
    if t < CUT_HALL - FR or t >= CUT_RIDE + 3: return
    sk_rect(cr, DESK_X - 330, FLOOR_Y - 300, DESK_X + 330, FLOOR_Y, 6, sid=32300, fill=(0.42, 0.30, 0.22))
    sk_rect(cr, DESK_X - 360, FLOOR_Y - 320, DESK_X + 360, FLOOR_Y - 290, 5, sid=32301, fill=(0.52, 0.38, 0.28))
    draw_text(cr, "SECURITY", DESK_X + 60, FLOOR_Y - 170, 40, color=(230, 220, 200))
    # desk lamp
    sketch_line(cr, [(DESK_X + 230, FLOOR_Y - 320), (DESK_X + 200, FLOOR_Y - 470), (DESK_X + 120, FLOOR_Y - 520)], 7, sid=32302)
    sk_poly(cr, [(DESK_X + 70, FLOOR_Y - 560), (DESK_X + 170, FLOOR_Y - 540), (DESK_X + 150, FLOOR_Y - 480), (DESK_X + 60, FLOOR_Y - 500)], 5, sid=32303, fill=(0.25, 0.45, 0.30))
    cr.move_to(DESK_X + 70, FLOOR_Y - 500); cr.line_to(DESK_X - 60, FLOOR_Y - 320); cr.line_to(DESK_X + 200, FLOOR_Y - 320); cr.line_to(DESK_X + 150, FLOOR_Y - 480)
    cr.close_path(); cr.set_source_rgba(1.0, 0.95, 0.7, 0.18); cr.fill()
    draw_cup(cr, t)
def draw_cup(cr, t):
    x, yb = CUP_X, CUP_Y
    jump = 0.0
    for tb in BIG:
        u = t - tb
        if 0 <= u < 0.35: jump = max(jump, 30 * math.sin(math.pi * u / 0.35))
    cr.save(); cr.translate(x, yb - jump * 0.3)
    wy = -80
    # water
    cr.move_to(-42, wy); cr.line_to(42, wy); cr.line_to(36, 0); cr.line_to(-36, 0); cr.close_path()
    cr.set_source_rgba(0.55, 0.78, 0.95, 0.85); cr.fill()
    # ripples on the surface (seen slightly from above)
    for tr in RIPS:
        u = (t - tr) / 0.9
        if 0 <= u < 1:
            for j in range(3):
                r_ = 8 + 40 * u - 12 * j
                if r_ > 3:
                    cr.save(); cr.translate(0, wy); cr.scale(1.0, 0.25); cr.arc(0, 0, r_, 0, 2 * math.pi); cr.restore()
                    cr.set_source_rgba(1, 1, 1, 0.9 * (1 - u)); cr.set_line_width(3); cr.stroke()
    if jump > 2:
        for k in range(4):
            cr.arc(-20 + 14 * k, wy - jump * (0.8 + 0.3 * (k % 2)), 6, 0, 2 * math.pi); cr.set_source_rgba(0.55, 0.78, 0.95, 0.9); cr.fill()
    # glass
    cr.move_to(-46, -125); cr.line_to(46, -125); cr.line_to(38, 0); cr.line_to(-38, 0); cr.close_path()
    cr.set_source_rgba(0.9, 0.95, 1.0, 0.25); cr.fill_preserve(); cr.set_source_rgb(*INKC); cr.set_line_width(5); cr.stroke()
    sketch_line(cr, [(-30, -110), (-24, -20)], 4, sid=32310, color=(1, 1, 1), alpha=0.8)
    cr.restore()

# ================================================================ props in his hands
def draw_amber(cr, x, y, s=1.0, empty=0.0, glint=0.0, sid=32400):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    if glint > 0.01:
        cr.arc(0, 0, 120, 0, 2 * math.pi); cr.set_source_rgba(1.0, 0.75, 0.25, 0.35 * glint); cr.fill()
    sk_poly(cr, [(-48, -10), (-30, -55), (18, -62), (52, -20), (44, 34), (0, 56), (-40, 38)], 5, sid=sid, fill=(0.95, 0.62, 0.15))
    sketch_line(cr, [(-26, -38), (-4, -48)], 4, sid=sid + 1, color=(1, 0.9, 0.6))
    if empty < 0.5:                                   # the mosquito
        sk_ell(cr, 0, 6, 16, 7, 3, sid=sid + 2, fill=(0.25, 0.15, 0.08))
        sketch_line(cr, [(14, 6), (34, 14)], 3, sid=sid + 3)
        for d in (-1, 1):
            sketch_line(cr, [(-4, 2), (-14, -18 * d - 2)], 3, sid=sid + 4, alpha=0.7)
        for k in range(3):
            sketch_line(cr, [(-6 + 6 * k, 10), (-14 + 8 * k, 26)], 2.5, sid=sid + 5 + k)
    cr.restore()

def amber_draw_r(cr, x, y, s, t, p):
    if t >= T_SWAP: return
    g = ramp(t, POP_AMBER + 0.3, POP_AMBER + 0.6) * (1 - ramp(t, T_SWAP - 0.4, T_SWAP - 0.1))
    draw_amber(cr, x, y - 40, 1.0 * s, glint=g)
def amber_draw_l(cr, x, y, s, t, p):
    if t >= T_TOSS_A + 0.05: return
    draw_amber(cr, x, y - 35, 1.0, empty=1.0 if t >= T_FILL1 else 0.0)

def syringe(cr, x, y, ang, fill=0.0, plunger=0.0, s=1.0, sid=32450):
    """a big cartoon syringe; (x, y) = where the hand holds the barrel; needle points along ang."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_line(cr, [(60, 0), (170, 0)], 4, sid=sid, color=(0.55, 0.55, 0.6))             # needle
    sk_rect(cr, -150, -26, 60, 26, 5, sid=sid + 1, fill=(0.92, 0.96, 1.0))
    if fill > 0.01:
        cr.rectangle(60 - 200 * fill, -20, 200 * fill, 40); cr.set_source_rgb(0.80, 0.12, 0.14); cr.fill()
    sk_rect(cr, -150, -26, 60, 26, 5, sid=sid + 1)
    draw_text(cr, "DNA", -45, 0, 30, color=(30, 30, 40))
    px = -150 - 90 * (1 - plunger)
    sketch_line(cr, [(px, 0), (-150, 0)], 8, sid=sid + 2)
    sk_rect(cr, px - 10, -34, px + 6, 34, 4, sid=sid + 3, fill=(0.85, 0.85, 0.9))
    sk_rect(cr, -160, -40, -146, 40, 4, sid=sid + 4, fill=(0.85, 0.85, 0.9))
    cr.restore()

def syr_fill(t):
    if t < T_FILL0: return 0.0
    if t < CUT_TOE: return ramp(t, T_FILL0, T_FILL1)
    return 1.0 - ramp(t, T_PLUNGE0, T_PLUNGE1)
def syr_draw(cr, x, y, s, t, p):
    if t >= T_TOSS_S: return
    if t < CUT_HALL: return
    if CUT_TOE - FR <= t < CUT_BACK - FR:
        syringe(cr, x - 10, y - 10, math.pi + 0.15, fill=syr_fill(t), plunger=1 - syr_fill(t), s=s)
    elif t >= T_JAB - 0.1:
        syringe(cr, x, y - 20, math.pi + 0.35, fill=syr_fill(t), plunger=1 - syr_fill(t), s=s)
    else:
        syringe(cr, x, y - 30, -1.2, fill=0.0, plunger=1.0, s=s)

def draw_tossed(cr, t):
    # the amber flies over his shoulder and lands on the floor
    if T_TOSS_A <= t < CUT_TOE - FR:
        u = ramp(t, T_TOSS_A, T_TOSS_A + 0.45)
        x = lerp(HIMX - 120, HIMX + 420, u); y = lerp(FLOOR_Y - 420, FLOOR_Y - 50, u) - 380 * math.sin(math.pi * u)
        draw_amber(cr, x, y, 0.8, empty=1.0, sid=32420)
    if CUT_BACK <= t < CUT_RIDE + 3:
        draw_amber(cr, HIMX + 420, FLOOR_Y - 50, 0.8, empty=1.0, sid=32420)
    if T_TOSS_S <= t < CUT_RIDE:
        u = ramp(t, T_TOSS_S, T_TOSS_S + 0.45)
        x = lerp(HIMX + 120, HIMX + 600, u); y = lerp(FLOOR_Y - 600, FLOOR_Y - 40, u) - 300 * math.sin(math.pi * u)
        syringe(cr, x, y, 6 * u, fill=0.0, plunger=1.0, s=0.8, sid=32460)

def draw_saddle(cr, x, y, ang=0.0, s=1.0, sid=32500, stirrups=True):
    """a western saddle; (x, y) = bottom-centre of the seat."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    if stirrups:
        for d, k in ((-1, 0), (1, 1)):
            sketch_line(cr, [(d * 40, 0), (d * 50, 150)], 7, sid=sid + k, color=(0.40, 0.24, 0.12))
            sk_rect(cr, d * 50 - 24, 145, d * 50 + 24, 170, 4, sid=sid + 2 + k, fill=(0.75, 0.75, 0.78))
    sk_poly(cr, [(-150, 10), (-140, -40), (-80, -50), (60, -40), (110, -90), (140, -80), (130, -20), (150, 10), (60, 40), (-90, 40)],
            6, sid=sid + 4, fill=(0.62, 0.38, 0.18))
    sk_circ(cr, 125, -95, 18, 4, sid=sid + 5, fill=(0.62, 0.38, 0.18))
    sketch_line(cr, [(-120, -20), (100, -20)], 3, sid=sid + 6, color=(0.4, 0.22, 0.1))
    cr.restore()

def saddle_held(cr, x, y, s, t, p):
    if t >= CUT_RIDE - FR: return
    draw_saddle(cr, x - 20, y + 40, 0.0, 0.85 * s)

def draw_saddle_on(cr, t):
    X, lift, pitch, face, st = rex(t)
    x, y = rex_world(X, lift, pitch, face, 215, 600)
    y -= O._walkbob(st)
    draw_saddle(cr, x, y + 10, -pitch * face * -1 + 0.08, 1.0, sid=32510, stirrups=False)

def draw_reins(cr, t, p):
    if not (CUT_RIDE - FR <= t < CUT_ASK): return
    if T_SCR0 <= t < T_SCR1 + 0.2:
        hand = p["lhand"]
    else:
        hand = ((p["lhand"][0] + p["rhand"][0]) / 2, (p["lhand"][1] + p["rhand"][1]) / 2)
        if t >= T_RODEO and t < T_SKID0: hand = p["lhand"]
    m = rex_pt(t, "mouth")
    X, lift, pitch, face, st = rex(t)
    mid = ((hand[0] + m[0]) / 2, max(hand[1], m[1]) + 60)
    cr.move_to(*hand); cr.curve_to(mid[0], mid[1], mid[0], mid[1], m[0] + 40, m[1] - 20)
    cr.set_source_rgb(0.35, 0.20, 0.10); cr.set_line_width(7); cr.stroke()

# ================================================================ pterosaurs (skeletons in the hall -> alive outside)
def bonk_t(i): return 36.1 + 0.22 * i
def draw_pter_skel(cr, i, t):
    x0, top = PTER_H[i], FLOOR_Y - 2300
    sw = 0.0
    bt = bonk_t(i)
    if t >= bt: sw = 0.45 * math.exp(-(t - bt) * 1.2) * math.sin((t - bt) * 7)
    y = FLOOR_Y - 1900
    cr.save(); cr.translate(x0, top); cr.rotate(sw); cr.translate(-x0, -top)
    cr.translate(x0, y); cr.scale(1.5, 1.5); cr.translate(-x0, -y)
    for d in (-1, 1):
        sketch_line(cr, [(x0 + 120 * d, top), (x0 + 60 * d, y)], 3, sid=32600 + (d > 0), color=(0.3, 0.3, 0.35))
    for d in (-1, 1):
        pts = [(x0, y), (x0 + 110 * d, y - 70), (x0 + 260 * d, y - 30), (x0 + 340 * d, y + 40)]
        sketch_line(cr, pts, 14, sid=32610 + (d > 0), color=INKC); sketch_line(cr, pts, 8, sid=32610 + (d > 0), color=BONE)
    sk_ell(cr, x0, y, 50, 20, 4, sid=32620, fill=BONE)
    sk_poly(cr, [(x0 + 40, y - 20), (x0 + 170, y - 10), (x0 + 50, y + 4)], 4, sid=32621, fill=BONE)
    sk_poly(cr, [(x0 + 50, y - 20), (x0 - 10, y - 70), (x0 + 30, y - 22)], 3, sid=32622, fill=BONE)
    cr.arc(x0 + 70, y - 10, 7, 0, 2 * math.pi)
    if t >= bt + 0.2: cr.set_source_rgb(*GLOWG)
    else: cr.set_source_rgb(*INKC)
    cr.fill()
    cr.restore()

def pter_alive(i, t):
    """(x, y, flap) of live pterodactyl i, or None."""
    if t < T_PTER0 + 0.15 * i: return None
    flap = t * 9 + i * 1.3
    X, lift, pitch, face, st = rex(min(t, CUT_ASK - FR))
    offs = ((-150, -1700), (380, -1880), (-650, -1580))[i]
    perch = (LIGHT_X - 120 + 140 * i, FLOOR_Y - 1335)
    u = ramp(t, T_PTER0 + 0.15 * i, T_PTER0 + 1.2 + 0.15 * i)
    start = (GW + 100, FLOOR_Y - 900 - 120 * i)
    fly = (X + offs[0] + 40 * math.sin(t * 2 + i), FLOOR_Y + offs[1] + 30 * math.sin(t * 3 + i))
    pos = (lerp(start[0], fly[0], smooth(u)), lerp(start[1], fly[1], smooth(u)))
    if t >= T_SKID0:
        v = ramp(t, T_SKID0 + 0.3 + 0.12 * i, T_PERCH + 0.12 * i)
        pos = (lerp(pos[0], perch[0], smooth(v)), lerp(pos[1], perch[1], smooth(v)))
        if v >= 1: flap = -math.pi / 2 + 0.15 * math.sin(t * 2 + i)
    return pos[0], pos[1], flap

def draw_pters(cr, t):
    for i in range(3):
        q = pter_alive(i, t)
        if q: O.draw_pterodactyl(cr, q[0], q[1], s=1.25, flap=q[2], facing=1, sid=32700 + 5 * i)

# ================================================================ worlds
NSKY = [(-4000, (0.08, 0.08, 0.18)), (0, (0.12, 0.12, 0.26)), (500, (0.17, 0.17, 0.33)), (850, (0.24, 0.22, 0.40))]
WALK_TOP = FLOOR_Y - 230
def night_sky(cr, x0, x1, y_bot, t):
    for i, (y, c) in enumerate(NSKY):
        y1 = NSKY[i + 1][0] if i + 1 < len(NSKY) else y_bot
        cr.rectangle(x0, y, x1 - x0, y1 - y + 1); cr.set_source_rgb(*c); cr.fill()
    cx, cy, z = L.cam_track.at(t)
    for k in range(22):
        sx = cx - 1200 + (k * 397) % 2400; sy = cy - 1600 + (k * 211) % 900
        if x0 < sx < x1:
            cr.arc(sx, sy, 4 + (k % 3) * 2, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.5 + 0.4 * math.sin(t * 2 + k)); cr.fill()
    mx, my = cx - 330 / z, cy - 470 / z
    if x0 < mx < x1:
        cr.arc(mx, my, 260, 0, 2 * math.pi); cr.set_source_rgba(0.95, 0.93, 0.85, 0.12); cr.fill()
        sk_circ(cr, mx, my, 170, 5, sid=32800, fill=(0.96, 0.95, 0.88))

def skyline(cr, x0, x1, seed, base):
    _s = random.Random(seed)
    bx = x0
    while bx < x1:
        w = _s.uniform(300, 560); h = _s.uniform(600, 1300)
        cr.rectangle(bx, base - h, w, h); cr.set_source_rgb(0.18, 0.17, 0.28); cr.fill()
        for r_ in range(int(h // 170)):
            for c_ in range(int(w // 140)):
                if _s.random() < 0.3:
                    cr.rectangle(bx + 40 + 140 * c_, base - h + 60 + 170 * r_, 50, 70); cr.set_source_rgb(0.95, 0.85, 0.5); cr.fill()
        bx += w + _s.uniform(20, 90)

def street(cr, x0, x1, t):
    cr.rectangle(x0, WALK_TOP, x1 - x0, FLOOR_Y - WALK_TOP + 1); cr.set_source_rgb(0.50, 0.48, 0.56); cr.fill()
    k0 = int((x0 - MX) // 300) - 1
    for k in range(k0, k0 + int((x1 - x0) // 300) + 3):
        xx = MX + 300 * k
        sketch_line(cr, [(xx, WALK_TOP + 10), (xx - 60, FLOOR_Y - 5)], 3, sid=32810 + (k % 7), color=(0.40, 0.38, 0.46), amp=0.4)
    cr.rectangle(x0, FLOOR_Y, x1 - x0, 1400); cr.set_source_rgb(0.20, 0.19, 0.24); cr.fill()
    k0 = int((x0 - MX) // 360) - 1
    for k in range(k0, k0 + int((x1 - x0) // 360) + 3):
        cr.rectangle(MX + 360 * k, FLOOR_Y + 190, 170, 16); cr.set_source_rgb(0.85, 0.78, 0.35); cr.fill()
    sketch_line(cr, [(x0, FLOOR_Y), (x1, FLOOR_Y)], 6, sid=32820, amp=0.3)

def draw_plaza(cr, t):
    x0, x1 = PX - 3200, PX + 2600
    night_sky(cr, x0, x1, WALK_TOP, t)
    skyline(cr, x0, PX - 1300, 11, WALK_TOP)
    # the museum facade
    fx0, fx1, top = PX - 1250, PX + 2400, FLOOR_Y - 1700
    sk_rect(cr, fx0, top, fx1, WALK_TOP, 7, sid=32900, fill=(0.78, 0.76, 0.72))
    sk_poly(cr, [(fx0 - 80, top), ((fx0 + fx1) / 2, top - 420), (fx1 + 80, top)], 7, sid=32901, fill=(0.74, 0.72, 0.68))
    sk_rect(cr, fx0 - 80, top, fx1 + 80, top + 170, 6, sid=32902, fill=(0.70, 0.68, 0.64))
    draw_text(cr, "MUSEUM OF NATURAL HISTORY", (fx0 + fx1) / 2, top + 88, 110, color=(60, 55, 50))
    for k in range(9):
        cx_ = fx0 + 120 + k * (fx1 - fx0 - 240) / 8
        sk_rect(cr, cx_ - 60, top + 170, cx_ + 60, WALK_TOP - 120, 5, sid=32910 + k, fill=(0.88, 0.86, 0.82))
        for j in range(3):
            sketch_line(cr, [(cx_ - 30 + 30 * j, top + 190), (cx_ - 30 + 30 * j, WALK_TOP - 140)], 2.5, sid=32920 + j, color=(0.6, 0.58, 0.55))
    # banners between the columns
    for k, (bx, txt) in enumerate(((PX - 380, "DINOSAUR"), (PX + 1450, "DINOSAUR"))):
        sk_rect(cr, bx - 110, top + 230, bx + 110, top + 900, 5, sid=32930 + k, fill=(0.55, 0.14, 0.12))
        draw_text(cr, "DINO", bx, top + 380, 56, color=(250, 230, 200))
        draw_text(cr, "SAUR", bx, top + 450, 56, color=(250, 230, 200))
        draw_text(cr, "HALL", bx, top + 560, 56, color=(250, 230, 200))
        # a little skull icon
        sk_poly(cr, [(bx - 60, top + 700), (bx + 40, top + 680), (bx + 70, top + 720), (bx + 50, top + 760), (bx - 60, top + 750)], 4, sid=32935 + k, fill=(0.95, 0.9, 0.8))
        cr.arc(bx + 20, top + 710, 10, 0, 2 * math.pi); cr.set_source_rgb(*INKC); cr.fill()
    # the doors (dark)
    sk_rect(cr, PX + 400, WALK_TOP - 700, PX + 800, WALK_TOP - 120, 6, sid=32940, fill=(0.12, 0.10, 0.10))
    # steps
    for k in range(3):
        sk_rect(cr, fx0 - 60 + 30 * k, WALK_TOP - 120 + 40 * k, fx1 + 60 - 30 * k, WALK_TOP - 80 + 40 * k, 4, sid=32950 + k, fill=(0.80, 0.78, 0.74))
    street(cr, x0, x1, t)
    # lamp posts
    for k, lx in enumerate((PX - 2200, PX - 1500)):
        sketch_line(cr, [(lx, FLOOR_Y), (lx, FLOOR_Y - 900)], 9, sid=32960 + k, amp=0.3)
        cr.arc(lx, FLOOR_Y - 930, 150, 0, 2 * math.pi); cr.set_source_rgba(1.0, 0.9, 0.6, 0.18); cr.fill()
        sk_circ(cr, lx, FLOOR_Y - 930, 34, 4, sid=32965 + k, fill=(1.0, 0.95, 0.75))

HALL_TOP = FLOOR_Y - 2800
def draw_hall(cr, t):
    x0, x1 = MX - 1500, GW
    vx0, vy0, vx1, vy1 = O._visible(cr)
    a, b = max(x0, vx0), min(x1, vx1)
    if b <= a: return
    cr.rectangle(a, HALL_TOP - 3000, b - a, 3000 + FLOOR_Y - 230 - HALL_TOP); cr.set_source_rgb(0.30, 0.29, 0.38); cr.fill()
    # tall arched windows with moonlight
    for k in range(int((a - MX) // 1100) - 1, int((b - MX) // 1100) + 2):
        wx = MX + 1100 * k + 300
        if not (x0 + 200 < wx < x1 - 300): continue
        sk_rect(cr, wx - 200, FLOOR_Y - 2300, wx + 200, FLOOR_Y - 900, 6, sid=33000 + k % 5, fill=(0.14, 0.16, 0.30))
        cr.arc(wx, FLOOR_Y - 2300, 200, math.pi, 2 * math.pi); cr.set_source_rgb(0.14, 0.16, 0.30); cr.fill_preserve()
        cr.set_source_rgb(*INKC); cr.set_line_width(6); cr.stroke()
        sketch_line(cr, [(wx, FLOOR_Y - 2480), (wx, FLOOR_Y - 900)], 5, sid=33010 + k % 5, amp=0.3)
        sketch_line(cr, [(wx - 200, FLOOR_Y - 1600), (wx + 200, FLOOR_Y - 1600)], 5, sid=33015 + k % 5, amp=0.3)
        cr.move_to(wx - 200, FLOOR_Y - 2300); cr.line_to(wx + 200, FLOOR_Y - 2300); cr.line_to(wx + 700, FLOOR_Y); cr.line_to(wx + 200, FLOOR_Y)
        cr.close_path(); cr.set_source_rgba(0.80, 0.85, 1.0, 0.07); cr.fill()
    # columns
    for k in range(int((a - MX) // 1100) - 1, int((b - MX) // 1100) + 2):
        cx_ = MX + 1100 * k + 850
        if not (x0 < cx_ < x1 - 200): continue
        sk_rect(cr, cx_ - 70, HALL_TOP, cx_ + 70, FLOOR_Y - 230, 5, sid=33020 + k % 5, fill=(0.40, 0.39, 0.48))
    # ceiling beam
    cr.rectangle(a, HALL_TOP - 200, b - a, 200); cr.set_source_rgb(0.22, 0.21, 0.28); cr.fill()
    # the floor
    cr.rectangle(a, FLOOR_Y - 230, b - a, 231); cr.set_source_rgb(0.50, 0.46, 0.50); cr.fill()
    for k in range(int((a - MX) // 260) - 1, int((b - MX) // 260) + 2):
        xx = MX + 260 * k
        sketch_line(cr, [(xx, FLOOR_Y - 225), (xx - 80, FLOOR_Y - 4)], 3, sid=33030 + k % 7, color=(0.42, 0.38, 0.42), amp=0.3)
    cr.rectangle(a, FLOOR_Y, b - a, 1400); cr.set_source_rgb(0.36, 0.33, 0.37); cr.fill()
    sketch_line(cr, [(a, FLOOR_Y), (b, FLOOR_Y)], 6, sid=33040, amp=0.3)
    # signs
    if a < SKX + 300 < b:
        sk_rect(cr, SKX - 700, FLOOR_Y - 2560, SKX + 500, FLOOR_Y - 2380, 6, sid=33050, fill=(0.55, 0.14, 0.12))
        draw_text(cr, "DINOSAUR HALL", SKX - 100, FLOOR_Y - 2470, 90, color=(250, 230, 200))

def draw_glass_wall(cr, t):
    """the giant glass wall at the end of the hall (seen side-on as a tall frame) + its shards."""
    if t < CUT_RIDE - 1: return
    x = GW
    sk_rect(cr, x - 40, HALL_TOP - 200, x + 40, HALL_TOP + 80, 5, sid=33100, fill=(0.22, 0.21, 0.28))
    sk_rect(cr, x - 40, FLOOR_Y - 60, x + 40, FLOOR_Y + 10, 5, sid=33101, fill=(0.22, 0.21, 0.28))
    if t < T_SMASH:
        cr.rectangle(x - 260, HALL_TOP + 80, 520, FLOOR_Y - 60 - HALL_TOP - 80); cr.set_source_rgba(0.75, 0.90, 1.0, 0.35); cr.fill()
        for k in range(5):
            yy = HALL_TOP + 80 + k * (FLOOR_Y - 140 - HALL_TOP) / 4
            sketch_line(cr, [(x - 260, yy), (x + 260, yy)], 6, sid=33110 + k, amp=0.2)
        for d in (-260, 0, 260):
            sketch_line(cr, [(x + d, HALL_TOP + 80), (x + d, FLOOR_Y - 60)], 6, sid=33120 + d % 7, amp=0.2)
        for k in range(4):
            yy = HALL_TOP + 400 + 500 * k
            sketch_line(cr, [(x - 200, yy + 120), (x - 80, yy)], 5, sid=33130 + k, color=(1, 1, 1), alpha=0.7)
    else:
        for d in (-260, 260):                                   # jagged leftovers
            pts = [(x + d, HALL_TOP + 80), (x + d * 0.6, HALL_TOP + 200), (x + d * 0.8, HALL_TOP + 420), (x + d, HALL_TOP + 500)]
            sk_poly(cr, pts, 4, sid=33140 + (d > 0), fill=(0.80, 0.92, 0.99))
            pts = [(x + d, FLOOR_Y - 60), (x + d * 0.7, FLOOR_Y - 180), (x + d * 0.9, FLOOR_Y - 300), (x + d, FLOOR_Y - 340)]
            sk_poly(cr, pts, 4, sid=33142 + (d > 0), fill=(0.80, 0.92, 0.99))
        u = t - T_SMASH
        if u < 2.0:
            O.draw_shards(cr, x, FLOOR_Y - 900, u, n=30, sid=33150, spread=1.4)
            O.draw_shards(cr, x, FLOOR_Y - 1700, u * 0.9, n=20, sid=33160, spread=1.8)
        for k in range(14):                                     # glass on the ground
            gx = x + 150 + (k * 263) % 1500; sk_poly(cr, [(gx, FLOOR_Y - 4), (gx + 30, FLOOR_Y - 20), (gx + 50, FLOOR_Y - 2)], 3, sid=33170 + k % 5, fill=(0.80, 0.92, 0.99))

def draw_outside(cr, t):
    x0 = GW
    vx0, vy0, vx1, vy1 = O._visible(cr)
    a, b = max(x0, vx0), vx1
    if b <= a: return
    night_sky(cr, a, b, WALK_TOP, t)
    skyline(cr, GW + 200, X_STOP + 3000, 23, WALK_TOP)
    # the museum's side wall (its glass end) seen from outside
    street(cr, a, b, t)
    # street lamps
    for k in range(int((a - GW) // 1400), int((b - GW) // 1400) + 2):
        lx = GW + 900 + 1400 * k
        if lx > X_STOP + 3000: continue
        sketch_line(cr, [(lx, FLOOR_Y), (lx, FLOOR_Y - 1000), (lx + 100, FLOOR_Y - 1040)], 9, sid=33200 + k % 5, amp=0.3)
        cr.arc(lx + 110, FLOOR_Y - 1000, 150, 0, 2 * math.pi); cr.set_source_rgba(1.0, 0.9, 0.6, 0.16); cr.fill()
        sk_circ(cr, lx + 110, FLOOR_Y - 1005, 32, 4, sid=33210 + k % 5, fill=(1.0, 0.95, 0.75))
    # crosswalk
    for k in range(6):
        cx_ = LIGHT_X - 250 + 110 * k
        cr.move_to(cx_, FLOOR_Y + 30); cr.line_to(cx_ + 60, FLOOR_Y + 30); cr.line_to(cx_ + 30, FLOOR_Y + 300); cr.line_to(cx_ - 30, FLOOR_Y + 300)
        cr.close_path(); cr.set_source_rgb(0.92, 0.92, 0.92); cr.fill()

def draw_light(cr, t):
    if t < T_LAND: return
    x = LIGHT_X
    sketch_line(cr, [(x, FLOOR_Y), (x, FLOOR_Y - 1250)], 12, sid=33300, amp=0.2)
    sk_rect(cr, x - 70, FLOOR_Y - 1280, x + 70, FLOOR_Y - 900, 6, sid=33301, fill=(0.15, 0.15, 0.18))
    state = "green"
    if T_RED - 0.6 <= t < T_RED: state = "yellow"
    elif T_RED <= t < T_GREEN: state = "red"
    for k, (nm, col) in enumerate((("red", (0.95, 0.15, 0.15)), ("yellow", (0.98, 0.80, 0.15)), ("green", (0.25, 0.90, 0.35)))):
        on = state == nm
        cy_ = FLOOR_Y - 1215 + 120 * k
        if on:
            cr.arc(x, cy_, 80, 0, 2 * math.pi); cr.set_source_rgba(*col, 0.3); cr.fill()
        sk_circ(cr, x, cy_, 42, 4, sid=33310 + k, fill=col if on else (0.30, 0.30, 0.32))

def draw_posts(cr, t):
    """brass rope posts; the T. rex sends them flying."""
    if t < CUT_HALL - FR or t >= T_SMASH + 1: return
    for i, px in enumerate(POSTS):
        hit = 35.0 + 0.18 * i
        x, y, ang = px, FLOOR_Y, 0.0
        if t >= hit:
            u = t - hit
            x = px + 1300 * u; y = FLOOR_Y - 1400 * u + 2600 * u * u; ang = 9 * u
            if y > FLOOR_Y + 200: continue
        cr.save(); cr.translate(x, y); cr.rotate(ang)
        sketch_line(cr, [(0, 0), (0, -260)], 10, sid=33400 + i, color=(0.80, 0.62, 0.20))
        sk_ell(cr, 0, -4, 50, 14, 4, sid=33405 + i, fill=(0.80, 0.62, 0.20)); sk_circ(cr, 0, -272, 18, 4, sid=33410 + i, fill=(0.85, 0.68, 0.25))
        cr.restore()
    if t < 35.0:
        for i in range(2):
            a_, b_ = POSTS[i], POSTS[i + 1]
            cr.move_to(a_, FLOOR_Y - 250); cr.curve_to(a_ + 100, FLOOR_Y - 160, b_ - 100, FLOOR_Y - 160, b_, FLOOR_Y - 250)
            cr.set_source_rgb(0.65, 0.12, 0.14); cr.set_line_width(12); cr.stroke()

def draw_norun(cr, t):
    if t < CUT_RIDE - 1 or t >= T_SMASH + 1: return
    hit = 37.0
    x = NORUN_X
    flat = smooth(ramp(t, hit, hit + 0.15))
    cr.save(); cr.translate(x, FLOOR_Y); cr.scale(1, 1 - 0.85 * flat)
    sketch_line(cr, [(0, 0), (0, -420)], 8, sid=33450)
    sk_rect(cr, -170, -620, 170, -400, 5, sid=33451, fill=(0.95, 0.95, 0.9))
    draw_text(cr, "NO", 0, -560, 60, color=(200, 30, 30)); draw_text(cr, "RUNNING", 0, -470, 50, color=(200, 30, 30))
    cr.restore()

def world(cr, t):
    if t < CUT_PLAZA - FR:
        E31.dark(cr, t)
        return
    if t < CUT_HALL - FR:
        draw_plaza(cr, t)
        return
    draw_outside(cr, t)
    draw_hall(cr, t)

# ================================================================ cemetery bits (day 31 leftovers)
def draw_wreck(cr, t):
    x = E31.CAR_END
    cr.save(); cr.rectangle(x - 3000, -6000, 6000, 6000 + FLOOR_Y + 4); cr.clip()
    E31.draw_hyper(cr, x, FLOOR_Y - 236, 1.15, 100.0, spin=0.0)
    cr.restore()
    gx = E31.GRAVE_X
    sk_poly(cr, [(gx - 230, FLOOR_Y + 6), (gx - 160, FLOOR_Y - 40), (gx + 170, FLOOR_Y - 45), (gx + 260, FLOOR_Y + 6)], 5, sid=31520, fill=(0.33, 0.24, 0.18))
    for k in range(5):
        uu = ((t + 30) * 0.35 + k / 5) % 1.0
        O.draw_smoke_puff(cr, gx - 120 + 60 * math.sin(k * 1.7), FLOOR_Y - 150 - 800 * uu, 60 + 140 * uu, alpha=0.5 * (1 - uu), dark=0.6)

def draw_rose_fall(cr, t, p):
    if t >= CUT_PLAZA - FR: return
    hx, hy = p["head"]; tn = p.get("turn", 0.0)
    if t < T_DROP:
        mx, my = hx + 20 * tn, hy + 62
        cr.save(); cr.translate(mx, my); cr.rotate(-1.45); E31.draw_black_rose(cr, 0, 0, s=0.55, ang=0.0); cr.restore()
        return
    u = ramp(t, T_DROP, T_DROP + 0.4)
    if not hasattr(draw_rose_fall, "start"): draw_rose_fall.start = (hx + 20 * tn, hy + 62)
    sx, sy = draw_rose_fall.start
    cr.save(); cr.translate(sx + 30 * u, lerp(sy, FLOOR_Y - 20, u * u)); cr.rotate(-1.45 - 0.2 * u)
    E31.draw_black_rose(cr, 0, 0, s=0.55, ang=0.0); cr.restore()

def bat_tip(p):
    hx, hy = p["head"]; tl = p.get("tilt", 0.0)
    return hx + 8 + math.sin(tl) * 200, hy - C.HEAD_R - 92
def draw_curl_bat(cr, t, p):
    if t < T_ROAR0 + 0.2:
        if CUT_RIDE - FR <= t: return
        tipx, tipy = bat_tip(p)
        sw = 0.12 * math.sin(t * 2.4) + (0.6 * math.sin(t * 40) * ramp(t, T_ROAR0, T_ROAR0 + 0.1) if t >= T_ROAR0 else 0.0)
        cr.save(); cr.translate(tipx, tipy); cr.rotate(sw)
        sketch_line(cr, [(-6, 0), (6, 0)], 4, sid=31660)
        E31.draw_bat(cr, 0, 60, 0.85, flap=0.15, sid=31650, hang=True)
        cr.restore()
        return
    if t < T_ROAR0 + 1.6:
        u = ramp(t, T_ROAR0 + 0.2, T_ROAR0 + 1.6, "linear")
        if not hasattr(draw_curl_bat, "s0"): draw_curl_bat.s0 = bat_tip(p)
        sx, sy = draw_curl_bat.s0
        cr.save(); cr.translate(sx + 1500 * u, sy + 60 - 500 * u + 200 * math.sin(u * 12) * (1 - u)); cr.rotate(u * 14)
        E31.draw_bat(cr, 0, 0, 0.85, flap=t * 22, sid=31650); cr.restore()

# ================================================================ roar wind
def draw_roar(cr, t, p):
    if not (T_ROAR0 + 0.1 <= t < T_ROAR1 - 0.1): return
    m = rex_pt(t, "mouth")
    hx, hy = p["head"]
    for k in range(9):
        u = ((t - T_ROAR0) * 2.6 + k / 9) % 1.0
        a = -0.5 + k * 0.12
        x0 = lerp(m[0] + 60, hx + 400, u); y0 = lerp(m[1], hy - 120 + 300 * (k / 8), u)
        sketch_line(cr, [(x0, y0), (x0 + 220, y0 + 40 * a)], 6, sid=33500 + k, amp=0.4, alpha=0.75 * math.sin(math.pi * u))
    for k in range(6):                                        # spit
        u = ((t - T_ROAR0) * 3.1 + k / 6) % 1.0
        cr.arc(lerp(m[0] + 60, hx + 200, u), lerp(m[1], hy + 40 * (k - 3), u) - 60 * math.sin(math.pi * u), 9, 0, 2 * math.pi)
        cr.set_source_rgba(0.75, 0.90, 1.0, 0.8 * (1 - u)); cr.fill()

def draw_sniff(cr, t, p):
    for ts in T_SNIFFS:
        u = (t - ts) / 0.35
        if 0 <= u < 1:
            n = rex_pt(t, "nose")
            hx, hy = p["head"]
            for k in range(3):
                f = (u + k * 0.33) % 1.0
                x = lerp(hx + 60, n[0], f); y = lerp(hy - 60 + 40 * k, n[1], f)
                sketch_line(cr, [(x, y), (x - 50, y + 4)], 4, sid=33520 + k, alpha=0.7 * (1 - u))

# ---- speed lines + dust
def draw_speed(cr, t):
    for (a, b) in ((T_BOLT + 0.3, T_SMASH), (T_LAND + 0.2, T_SKID0)):
        if a <= t < b:
            X, lift, pitch, face, st = rex(t)
            for k in range(8):
                yy = FLOOR_Y - 150 - 150 * k
                sketch_line(cr, [(X - 800 - 220 * (k % 3), yy), (X - 1500 - 170 * (k % 2), yy)], 6, sid=33600 + k, amp=0.3, alpha=0.55)
    for t0 in (T_LAND, T_SKID0):
        if t0 <= t < t0 + 1.4:
            X, lift, pitch, face, st = rex(t)
            for k in range(6):
                u = (t - t0) * 1.1 + k * 0.1
                if u < 1.4: O.draw_smoke_puff(cr, X - 300 + 140 * k - (0 if t0 == T_LAND else 200), FLOOR_Y - 50 - 60 * u, 70 + 110 * u, alpha=max(0.0, 0.75 - 0.5 * u))

# ================================================================ poses
def P_(name, **kw): L.POSES[name] = kw
P_("amber_up", relb=(650, 820), rhand=(690, 700), lelb=(478, 975), lhand=(468, 1142))
P_("amber_l", lelb=(450, 930), lhand=(430, 850), relb=(602, 975), rhand=(612, 1142))
P_("jab", lelb=(470, 930), lhand=(470, 880), relb=(640, 900), rhand=(640, 880))
P_("toss_back", lelb=(420, 860), lhand=(380, 760), relb=(602, 975), rhand=(640, 1060))
P_("toss_r", relb=(660, 830), rhand=(700, 730), lelb=(478, 975), lhand=(468, 1142))
P_("toe_jab", head=(560, 790), neck=(555, 915), hip=(560, 1255), lelb=(500, 1080), lhand=(520, 1200),
   relb=(470, 1060), rhand=(400, 1130), lknee=(500, 1335), rknee=(640, 1335), lfoot_dir=-0.6, rfoot_dir=0.6)
P_("stiff", lelb=(505, 975), lhand=(508, 1135), relb=(575, 975), rhand=(572, 1135), lhand_t="flat", rhand_t="flat")
P_("blown", lelb=(560, 960), lhand=(600, 1080), relb=(640, 960), rhand=(690, 1070), lhand_t="open", rhand_t="open")
P_("wipe", relb=(560, 880), rhand=(520, 700), rhand_t="flat", rhand_front=1.0)
P_("saddle_up", relb=(650, 860), rhand=(640, 760), lelb=(478, 975), lhand=(468, 1142))
P_("ride", lknee=(620, 1235), lfoot=(600, 1360), rknee=(630, 1225), rfoot=(612, 1350),
   lelb=(590, 1010), lhand=(660, 1040), relb=(600, 1000), rhand=(665, 1030), lhand_t="fist", rhand_t="fist",
   nowalk=1.0, lag=0.3, feet_lag=0.6)
P_("ride_rodeo", lknee=(620, 1235), lfoot=(600, 1360), rknee=(630, 1225), rfoot=(612, 1350),
   lelb=(590, 1010), lhand=(660, 1040), relb=(560, 830), rhand=(600, 700), lhand_t="fist", rhand_t="open",
   nowalk=1.0, lag=0.35, feet_lag=0.6)
P_("ride_reach", lknee=(620, 1235), lfoot=(600, 1360), rknee=(630, 1225), rfoot=(612, 1350),
   lelb=(590, 1010), lhand=(660, 1040), relb=(680, 900), rhand=(760, 860), lhand_t="fist", rhand_t="open",
   nowalk=1.0, lag=0.3, feet_lag=0.6)

# ================================================================ scene (him)
S = M.Scene(start_body="stand", start_face="deadpan", x0=HIM3 - 540)
S.auto_blinks = True
S.floor = False
S.card("cr1ms0n_h0rnet", "Make dinosaurs come back to life and ride one", "0", t0=0.3)
CAM_A = cam(HIM3 - 250, 0.62, fs=1640)
S.camkeys[0] = (0.0, CAM_A, 0); S.cam = CAM_A

# ---------------------------------------------------------------- A: the cemetery
S.read_card(T_READ, react="deadpan", lines=2)
S.set(T_DROP - 0.1, "stand", "deadpan", dur=0.15, mouth="o", open=0.25, look=(0.0, 0.0), eyescale=1.08)
S.set(T_DROP + 0.4, "stand", "deadpan", dur=0.25, look=(0.2, 0.9), tilt=0.06)
S.sfx(T_DROP + 0.4, "tap", 0.05)
S.set(T_TURN, "stand", "deadpan", dur=0.2, turn=0.8, look=(1.0, 0.0))
S.run_to(T_RUN, FOG_C + 150 - 540, dur=1.4)
S.camera(T_RUN + 0.1, *cam(FOG_C - 700, 0.62, fs=1640), 1.2)
S.sfx(T_RUN + 1.1, "whoosh", 0.07)

# ---------------------------------------------------------------- B: the museum plaza
S.cut(CUT_PLAZA - FR, cam=cam(P_FOG + 500, 0.55, fs=1640), x=P_FOG - 540)
S.set(CUT_PLAZA - FR, "stand", "deadpan", dur=0.0, turn=0.8, look=(1.0, 0.0), run=1.0)
S.run_to(CUT_PLAZA, P_STOP - 540, dur=0.8)
S.camera(CUT_PLAZA + 0.2, *cam(PX + 250, 0.40, fs=1650), 0.9)
S.set(T_LOOKUP, "stand", "deadpan", dur=0.4, turn=0.5, look=(0.6, -1.0), tilt=-0.08)
S.set(T_LOOKUP + 0.5, "stand", "dead_stare", dur=0.2, turn=0.5, look=(0.6, -1.0), tilt=-0.08, lid=0.25)

# ---------------------------------------------------------------- C: the hall
S.cut(CUT_HALL - FR, cam=cam(SKX + 350, 0.48, fs=1660), x=HIMX - 540)
S.set(CUT_HALL - FR, "stand", "deadpan", dur=0.0, turn=-0.6, look=(-0.7, -1.0), tilt=-0.08)
S.camera(CUT_HALL, *cam(SKX + 380, 0.50, fs=1660), 1.3)
S.set(7.0, "stand", "dead_stare", dur=0.5, turn=-0.7, look=(-1.0, -0.3), tilt=-0.03)
S.camera(7.5, *cam(HIMX + 40, 0.82, fs=1560), 0.5)
# amber
S.pocket_pull(T_AMBER, "amber", amber_draw_r, (0, 0), held=True)
S.set(POP_AMBER + 0.08, "amber_up", "deadpan", dur=0.3, turn=0.3, look=(0.6, -0.9))
S.sfx(POP_AMBER + 0.4, "twinkle", 0.05)
S.set(POP_AMBER + 0.6, "amber_up", "dead_stare", dur=0.3, turn=0.3, look=(0.6, -0.9), lid=0.2)
S.set(T_SWAP - 0.3, "amber_l", "deadpan", dur=0.3, look=(-0.4, 0.3))
S.place("amber_l", amber_draw_l, (0, 0), t_on=T_SWAP - 0.05, follow="lhand")
# syringe
S.pocket_pull(T_SYR, "syr", syr_draw, (0, 0), held=True)
S.set(POP_SYR + 0.08, "amber_l", "deadpan", dur=0.3, look=(0.3, -0.5), relb=(650, 850), rhand=(690, 760))
S.set(T_JAB - 0.3, "jab", "deadpan", dur=0.3, look=(-0.2, 0.6), tilt=0.06)
S.sfx(T_JAB, "tok", 0.07)
S.sfx(T_FILL0, "slurp", 0.05, dur=0.8)
S.set(T_FILL1 + 0.05, "jab", "dead_stare", dur=0.2, look=(0.0, 0.0), lid=0.3)
S.set(T_TOSS_A, "toss_back", "deadpan", dur=0.15, ease="snap", look=(0.0, 0.0))
S.sfx(T_TOSS_A + 0.45, "tok", 0.06)
S.set(T_TOSS_A + 0.25, "stand", "deadpan", dur=0.25, look=(0.0, 0.0), relb=(650, 850), rhand=(690, 760))
# the toe
S.cut(CUT_TOE - FR, cam=cam(SKX + 330, 0.72, fs=1560), x=SKX + 470 - 540)
S.set(CUT_TOE - FR, "toe_jab", "deadpan", dur=0.0, turn=-1.0, look=(-1.0, 0.4), nowalk=1.0)
S.sfx(CUT_TOE + 0.15, "tok", 0.06)
S.sfx(T_PLUNGE0, "squeak", 0.05)
S.set(T_PLUNGE1, "toe_jab", "dead_stare", dur=0.2, turn=-1.0, look=(-1.0, 0.3), nowalk=1.0, lid=0.3)
# back in front of it: nothing
S.cut(CUT_BACK - FR, cam=cam(SKX + 450, 0.50, fs=1660), x=HIMX - 540)
S.set(CUT_BACK - FR, "stand", "deadpan", dur=0.0, turn=-0.6, look=(-0.8, -0.9), tilt=-0.06, relb=(650, 850), rhand=(690, 760))
S.set(T_US, "stand", "dead_stare", dur=0.4, turn=0.0, look=(0.0, 0.0), lid=0.35, relb=(650, 850), rhand=(690, 760))
S.set(T_TOSS_S, "toss_r", "dead_stare", dur=0.15, ease="snap", lid=0.35)
S.sfx(T_TOSS_S + 0.45, "tok", 0.05)
S.set(T_TOSS_S + 0.3, "stand", "dead_stare", dur=0.3, lid=0.35)
S.camera(T_TOSS_S + 0.3, *cam(SKX + 600, 0.47, fs=1660), 3.0)
S.sfx(T_TWITCH, "clack", 0.06)
for tr in (T_RIP1, T_RIP2): S.sfx(tr, "drip", 0.06)
S.set(T_EYES, "stand", "dead_stare", dur=0.35, look=(1.0, 0.4), lid=0.2)
S.sfx(T_RIP2 + 0.05, "clack", 0.07)
for th in T_HEART1: S.sfx(th, "thud", 0.09); S.sfx(th + 0.14, "thud", 0.05)
S.set(T_HEAD, "stand", "dead_stare", dur=0.25, look=(-1.0, -0.6), lid=0.2)
S.set(T_HEAD + 0.25, "stand", "dead_stare", dur=0.7, turn=-0.7, look=(-1.0, -0.8), lid=0.2, tilt=-0.06)
# glow -> FLASH -> alive
S.sfx(T_GLOW0, "whine", 0.03, dur=0.9)
for k in range(5): S.sfx(T_GLOW0 + 0.15 * k, "tick", 0.04)
S.flash(T_FLASH, 0.5, color=(0.85, 1.0, 0.85)); S.sfx(T_FLASH, "kaboom", 0.25); S.shake(T_FLASH, 0.6, 16)
S.set(T_FLASH + 0.15, "stand", "shocked", dur=0.1, ease="snap", turn=-0.6, look=(-1.0, -0.9), eyescale=1.25, curl_up=1.0)
S.set(T_FLASH + 0.6, "stand", "dead_stare", dur=0.35, turn=-0.6, look=(-1.0, -0.9), lid=0.1)
S.sfx(T_PLAQUE + 0.35, "clack", 0.08)
S.camera(T_FLASH + 0.5, *cam(SKX + 650, 0.45, fs=1660), 1.0)
for (a0, a1) in T_STEP:
    S.sfx(a1, "thud", 0.2); S.shake(a1, 0.35, 12)
    S.sfx(a1 + 0.02, "drip", 0.05)
S.set(T_STIFF, "stiff", "dead_stare", dur=0.15, ease="snap", turn=-0.5, look=(-0.6, -0.9), lid=0.05, eyescale=1.1)
S.camera(T_STIFF, *cam(HIMX - 220, 0.62, fs=1600), 0.7)
S.set(T_STIFF + 0.6, "stiff", "dead_stare", dur=0.15, turn=-0.5, look=(0.4, 0.0), lid=0.05, eyescale=1.1)
S.set(T_STIFF + 1.1, "stiff", "dead_stare", dur=0.15, turn=-0.5, look=(-0.8, -0.7), lid=0.05, eyescale=1.1)
for ts in T_SNIFFS: S.sfx(ts, "whoosh", 0.05, dur=0.25)
S.set(T_SNIFFS[-1] + 0.3, "stiff", "dead_stare", dur=0.15, turn=-0.4, look=(-0.8, -0.6), lid=0.0, eyescale=1.15)
# the roar
ROAR_WAV = os.path.join(HERE, "roar.wav")
S.sfx(T_ROAR0, ROAR_WAV, 0.5)
S.shake(T_ROAR0, 1.6, 9)
S.set(T_ROAR0 + 0.12, "blown", "dead_stare", dur=0.15, ease="snap", turn=-0.3, look=(-0.4, -0.2), lid=0.75, lean=0.10, tilt=0.1)
S.set(T_ROAR1 + 0.1, "stand", "dead_stare", dur=0.35, turn=-0.3, look=(-0.6, -0.6), lid=0.3)
S.set(T_BLINK, "stand", "dead_stare", dur=0.3, turn=-0.3, look=(-0.6, -0.6), lid=1.0)
S.set(T_BLINK + 0.35, "stand", "dead_stare", dur=0.3, turn=-0.3, look=(-0.6, -0.6), lid=0.3)
S.set(T_WIPE0, "wipe", "dead_stare", dur=0.2, turn=-0.2, look=(-0.3, -0.3), lid=0.4)
S.set(T_WIPE1, "stand", "dead_stare", dur=0.25, turn=-0.2, look=(0.0, 0.0), lid=0.35)
S.sfx(T_WIPE0 + 0.15, "rummage", 0.04, dur=0.4)
S.set(T_CARD, "stand", "deadpan", dur=0.3, look=(0.7, -0.9), tilt=-0.05)
S.camera(T_SADDLE, *cam(HIMX - 150, 0.66, fs=1600), 0.6)
S.pocket_pull(T_SADDLE, "saddle", saddle_held, (0, 0), held=True)
S.set(POP_SADDLE + 0.08, "saddle_up", "deadpan", dur=0.3, turn=-0.5, look=(-1.0, -0.8))
for th in T_HEART2: S.sfx(th, "thud", 0.09); S.sfx(th + 0.14, "thud", 0.05)
S.set(T_NARROW + 0.2, "saddle_up", "dead_stare", dur=0.3, turn=-0.5, look=(-1.0, -0.8), lid=0.35)

# ---------------------------------------------------------------- D: the ride
def ride_cam(t):
    X, lift, pitch, face, st = rex(t)
    return X - 60
S.cut(CUT_RIDE - FR, cam=cam(X_BOLT0 - 80, 0.50, fs=1660), x=HIMX - 540)
S.set(CUT_RIDE - FR, "ride", "deadpan", dur=0.0, turn=0.9, look=(1.0, 0.0))
S.set(CUT_RIDE + 0.5, "ride", "dead_stare", dur=0.3, turn=0.2, look=(0.4, 0.0), lid=0.3)
for th in T_HEART3: S.sfx(th, "thud", 0.09); S.sfx(th + 0.14, "thud", 0.05)
S.set(T_REINS, "ride", "deadpan", dur=0.1, ease="snap", turn=0.9, look=(1.0, 0.0), lhand=(660, 1000), rhand=(665, 990))
S.sfx(T_REINS, "tap", 0.05)
S.set(T_REINS + 0.15, "ride", "deadpan", dur=0.15, turn=0.9, look=(1.0, 0.0))
S.sfx(T_BOLT, ROAR_WAV, 0.18); S.sfx(T_BOLT + 0.1, "whoosh", 0.10)
S.set(T_BOLT + 0.05, "ride", "deadpan", dur=0.12, ease="snap", turn=0.9, look=(1.0, 0.0), lean=-0.2, curl_up=1.0)
S.set(T_BOLT + 0.5, "ride", "deadpan", dur=0.3, turn=0.9, look=(1.0, 0.0), lean=-0.05)
S.set(T_RODEO, "ride_rodeo", "deadpan", dur=0.3, turn=0.9, look=(1.0, 0.0))
for i in range(3): S.sfx(35.0 + 0.18 * i, "clack", 0.06)
S.sfx(36.15, "bonk", 0.07)
S.sfx(37.0, "tap", 0.06)
for k in range(int((T_SMASH - T_BOLT) / 0.33)): S.sfx(T_BOLT + 0.2 + 0.33 * k, "thud", 0.07)
S.set(T_SEEGLASS, "ride_rodeo", "dead_stare", dur=0.15, ease="snap", turn=1.0, look=(1.0, 0.0), eyescale=1.25, lid=0.0)
S.set(T_SEEGLASS + 0.4, "ride", "dead_stare", dur=0.25, turn=1.0, look=(1.0, 0.0), eyescale=1.2, lid=0.0, lean=0.12)
SMASH_WAV = os.path.join(HERE, "smash.wav")
S.sfx(T_SMASH, SMASH_WAV, 0.45); S.shake(T_SMASH, 0.8, 26); S.flash(T_SMASH, 0.25)
S.set(T_SMASH + 0.2, "ride_rodeo", "deadpan", dur=0.2, turn=0.9, look=(1.0, 0.3), lean=-0.1)
S.sfx(T_LAND, "kaboom", 0.35); S.shake(T_LAND, 0.7, 24)
for k in range(int((T_SKID0 - T_LAND) / 0.3)): S.sfx(T_LAND + 0.3 + 0.3 * k, "thud", 0.07)
S.set(T_LAND + 0.1, "ride", "deadpan", dur=0.12, ease="snap", turn=0.9, look=(1.0, 0.0), squash=0.3)
S.set(T_ARM2, "ride_rodeo", "deadpan", dur=0.35, turn=0.9, look=(1.0, 0.0))
S.set(T_SMILE, "ride_rodeo", "deadpan", dur=0.6, turn=0.9, look=(1.0, 0.0), smile=0.45, lid=0.2)
S.sfx(T_PTER0 + 0.2, "whoosh", 0.06)
S.set(42.4, "ride_rodeo", "deadpan", dur=0.3, turn=0.5, look=(0.3, -1.0), smile=0.45, lid=0.2)
S.set(43.0, "ride", "deadpan", dur=0.3, turn=0.9, look=(1.0, 0.0), smile=0.3, lid=0.2)
S.sfx(T_SKID0, "skid", 0.14, dur=0.8)
S.set(T_SKID0 + 0.05, "ride", "dead_stare", dur=0.15, turn=0.9, look=(1.0, -0.3), lean=0.25)
S.set(T_SKID1, "ride", "dead_stare", dur=0.3, turn=0.9, look=(1.0, -0.5), lid=0.3)
for i in range(3): S.sfx(T_PERCH + 0.12 * i, "tap", 0.04)
S.set(T_ITCH0 + 0.5, "ride", "dead_stare", dur=0.3, turn=0.8, look=(1.0, 0.6), lid=0.3)
S.set(T_SCR0, "ride_reach", "deadpan", dur=0.35, turn=0.9, look=(1.0, 0.5), lean=0.35, lid=0.3)
S.sfx(T_SCR0 + 0.3, "rummage", 0.07, dur=1.0)
S.set(T_SCR1 + 0.1, "ride", "deadpan", dur=0.35, turn=0.6, look=(0.6, 0.2), lid=0.3, smile=0.2)
S.sfx(T_GREEN, "ding", 0.05)

# ---------------------------------------------------------------- E: the ask (on the sidewalk, his T. rex behind him)
S.cut(CUT_ASK - FR, cam=cam(AX - 120, 0.62, fs=1640), x=AX - 540)
S.set(CUT_ASK - FR, "stand", "deadpan", dur=0.0, turn=0.0, look=(0.0, 0.0), lid=0.3)
S.x = AX - 540
S.the_ask(T_ASK, hold=HOLD, push=False)
S.camera(T_ASK + 6.9, *cam(AX - 80, 0.68, fs=1640), 5.0)
T_END = S.t
S.blink(2.2, 9.0, 12.4, 17.9, 21.0, 31.0, 39.5, 45.5)

# camera follow during the ride (dense keys), replacing the placeholder
_ck = []
t_ = T_BOLT
while t_ < T_SKID1 + 0.2:
    X, lift, pitch, face, st = rex(t_)
    if t_ < T_SMASH:
        _ck.append((t_, cam(X + 250, 0.47, fs=1660), 0.1, "linear"))
    elif t_ < T_LAND:
        _ck.append((t_, cam(X + 200, 0.40, fs=1640), 0.1, "linear"))
    else:
        _ck.append((t_, cam(min(X + 300, X_STOP + 250), 0.44, fs=1660), 0.1, "linear"))
    t_ += 0.1
S.camkeys += _ck
S.camkeys.append((T_SKID1 + 0.3, cam(X_STOP + 150, 0.72, fs=1700), 0.8))
S.camkeys.sort(key=lambda k: k[0])

# ---------------------------------------------------------------- riding hook: his hip sits in the saddle
def ride_hook(t, p):
    if not (CUT_RIDE - FR <= t < CUT_ASK - FR): return p
    sx, sy = seat(t)
    hx, hy = p["hip"]
    dx, dy = sx - hx, sy - 30 - hy
    for k in L.JOINTS:
        p[k] = (p[k][0] + dx, p[k][1] + dy)
    if T_SCR0 + 0.25 <= t < T_SCR1:
        X, lift, pitch, face, st = rex(t)
        tx, ty = rex_world(X, lift, pitch, face, -150, 960)
        k = ramp(t, T_SCR0 + 0.25, T_SCR0 + 0.45)
        jx = 22 * math.sin(t * 34); jy = 10 * math.sin(t * 23)
        p["rhand"] = lerp(p["rhand"], (tx + jx, ty + jy), k)
        p["relb"] = lerp(p["relb"], ((p["neck"][0] + tx) / 2, (p["neck"][1] + ty) / 2 + 30), k)
        p["rhand_t"] = "open"
    return p
S.hook(ride_hook)

def sniff_hook(t, p):
    for ts in T_SNIFFS:
        v = pulse(t, ts + 0.05, 0.1)
        if v > 0.01: p["curl"] = p.get("curl", 0.0) - 0.5 * v
    if T_ROAR0 + 0.1 <= t < T_ROAR1:
        p["curl"] = p.get("curl", 0.0) + 0.55 + 0.1 * math.sin(t * 50)
    return p
S.hook(sniff_hook)

# ================================================================ draw order
def props_back(cr, t, p, ly):
    if ly != "back": return
    if t < CUT_PLAZA - FR:
        draw_wreck(cr, t)
        for i in range(3): E31.draw_girl(cr, 60.0 + t, i)
        return
    if t < CUT_HALL - FR: return
    draw_plinth(cr, t)
    draw_skeleton(cr, t)
    draw_plaque(cr, t)
    for i in range(3):
        if t < T_SMASH + 1: draw_pter_skel(cr, i, t)
    draw_desk(cr, t)
    draw_posts(cr, t)
    draw_norun(cr, t)
    draw_glass_wall(cr, t)
    draw_light(cr, t)
    draw_speed(cr, t)
    draw_rex(cr, t)
    draw_tossed(cr, t)
S.prop(props_back)
S.background(world)

def props_front(cr, t, p, ly):
    if ly != "front": return
    if t < CUT_RIDE:
        draw_curl_bat(cr, t, p)
    if t < CUT_PLAZA - FR:
        draw_rose_fall(cr, t, p)
        E31.draw_fog(cr, FOG_C, t, sid=32990)
    if CUT_PLAZA - FR <= t < CUT_HALL - FR:
        E31.draw_fog(cr, P_FOG, t, sid=32995)
    if CUT_HALL - FR <= t:
        draw_sniff(cr, t, p)
        draw_roar(cr, t, p)
        draw_flash_smoke(cr, t)
        draw_reins(cr, t, p)
        draw_pters(cr, t)
S.prop(props_front)

# ================================================================ sounds made for this episode
def _write_wav(path, sig, sr=48000):
    sig = np.clip(sig, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((sig * 32767).astype(np.int16).tobytes())
def make_sounds():
    sr = 48000; rng = np.random.default_rng(32)
    # roar: a growling low sawtooth stack with a wobble + breathy noise, swelling then dying
    dur = 1.7; tt = np.arange(int(dur * sr)) / sr
    f = 95 + 40 * np.sin(np.pi * tt / dur) - 25 * (tt / dur)
    ph = 2 * np.pi * np.cumsum(f) / sr
    saw = sum(np.sin(k * ph) / k for k in range(1, 12))
    am = 0.7 + 0.3 * np.sin(2 * np.pi * 28 * tt)
    nz = rng.standard_normal(len(tt)); acc = 0.0; lp = np.empty_like(nz)
    for i in range(len(nz)): acc += 0.08 * (nz[i] - acc); lp[i] = acc
    env = np.clip(tt / 0.12, 0, 1) * np.clip((dur - tt) / 0.5, 0, 1)
    roar = (saw * am * 0.5 + lp * 4.0) * env
    roar /= np.abs(roar).max() + 1e-9
    _write_wav(ROAR_WAV, roar * 0.9)
    # glass smash: a sharp crack + many little bright tinkles falling off
    dur = 1.6; tt = np.arange(int(dur * sr)) / sr
    crack = rng.standard_normal(len(tt)) * np.exp(-tt / 0.05)
    tink = np.zeros(len(tt))
    for k in range(40):
        t0 = rng.uniform(0.02, 1.2); fr = rng.uniform(2500, 6000); i0 = int(t0 * sr)
        n = min(len(tt) - i0, int(0.12 * sr)); u = np.arange(n) / sr
        tink[i0:i0 + n] += np.sin(2 * np.pi * fr * u) * np.exp(-u / 0.03) * rng.uniform(0.1, 0.35) * np.exp(-t0 * 1.5)
    sm = crack * 0.8 + tink
    sm /= np.abs(sm).max() + 1e-9
    _write_wav(SMASH_WAV, sm * 0.9)
if not (os.path.exists(ROAR_WAV) and os.path.exists(SMASH_WAV)):
    make_sounds()

if __name__ == "__main__":
    S.render("day032.mp4")
