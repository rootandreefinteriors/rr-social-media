"""Day 8 — COMMENT episode: @second_degree_burn "Fly a plane" (Instagram, day 7 reel, 0 likes).
Generic little red propeller plane, no airline/brand on screen.

SHOT 1  The empty white room (where the hat blasted him on day 7), sooty, the EXPELLED letter on the floor. Reads the
        comment. Stares. Slow blink.
WALK    He walks off to the right; the white room ends and an airfield begins: sky, grass, a runway, a hangar, a
        windsock, a FLIGHT SCHOOL sign, and a little red propeller plane. He looks at the plane. At the sign. At us.
COCKPIT CUT: he's sitting in it. The engine coughs twice (black puffs), catches, the propeller blurs. Judder.
FLY     Taxi, faster, lift-off, climb, level flight past the clouds. He looks at us. Then a loop. Then another, faster,
        and faster and faster, his head slowly filling up airsick green, sweat, quiver. Dead stare the whole time.
STALL   Levels out. The engine coughs, smokes, the propeller winds down and stops. The plane just hangs there in the
        sky. He looks at the propeller. At us. Slow blink.
DIVE    Nose drops: a spinning nosedive with a black smoke spiral, straight down into the field. BOOM: the plane is
        planted nose-first in the grass, tail in the air; he's flung out, tumbles, lands on his butt beside it.
        Beat. The landing wheel pops off and bonks him on the head. Nothing.
END     He stands. The ask, on the airfield next to the planted plane (where he lives now).
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y
from ink import smooth

BORDER = 1300                   # the white room ends here; the airfield starts
XP = 3700                       # the plane's seat, parked
YG = FLOOR_Y - O.PLANE_SEAT_H   # seat height on its wheels
SXW = 1960                      # where he stops, left of the plane's tail (x 2500)
CAM0 = (540, 930, 1.12)
CAM_FIELD = (3230, 720, 0.48)
CAM_PIT = (XP + 120, 900, 0.85)
SOOT = dict(soot=0.65, frizz=0.5)

# ---------------------------------------------------------------- timeline
T_WALK, T_ARR = 4.0, 9.0
CUT_IN = 12.0                   # in the cockpit
COUGH = (13.0, 13.6)
CATCH = 14.2                    # engine catches, prop blurs
TX0 = 15.4                      # taxi
TLIFT = 18.4                    # wheels off
TLV = 20.6                      # level
TL0 = 22.8                      # loops start
LOOPS = [2.6, 1.9, 1.4, 1.05, 0.85, 0.72, 0.62, 0.55, 0.5, 0.5]
TL1 = TL0 + sum(LOOPS)
TS0 = TL1 + 0.4                 # sputters
TSTOP = TS0 + 1.7               # stopped dead in the sky
TDROP = TSTOP + 2.4             # nose drops
TIMP = TDROP + 1.5              # BOOM
TLAND = TIMP + 1.4              # he lands on his butt
TW = TLAND + 1.7                # the wheel pops off
TBONK = TW + 0.7
STAND = TBONK + 1.9
T_ASK = STAND + 0.9

V = 1300.0                      # cruising speed (px/s)
ACC = V / (TLIFT - TX0)
R = 560.0                       # loop radius
YC = -40.0                      # cruise altitude (seat y)
CLIMB = YG - YC
DRIFT = 260.0                   # loop centre drift (px/s)

# ---------------------------------------------------------------- the plane's path: seat (x, y), pitch, prop
def _x_taxi(t): s = t - TX0; return XP + 0.5 * ACC * s * s
X_LIFT = _x_taxi(TLIFT)
X_LV = X_LIFT + V * (TLV - TLIFT)
X_L0 = X_LV + V * (TL0 - TLV)
_LS = [TL0]
for d in LOOPS: _LS.append(_LS[-1] + d)
def loop_phi(t):
    for i, d in enumerate(LOOPS):
        if t < _LS[i + 1]: return 2 * math.pi * (i + (t - _LS[i]) / d)
    return 2 * math.pi * len(LOOPS)
X_L1 = X_L0 + DRIFT * (TL1 - TL0)
SLOW = TSTOP - TL1
def _x_slow(t):                                                     # cruising on, slowing to a dead stop
    s = min(t, TSTOP) - TL1
    return X_L1 + V * 0.6 * (s - s * s / (2 * SLOW))
X_H = _x_slow(TSTOP)
XI = X_H + 300                  # where it plants
YI = FLOOR_Y + 200 - 625        # seat y once planted nose-down (nose 200 px into the ground)
def pos(t):
    if t < TX0: return (XP, YG)
    if t < TLIFT: return (_x_taxi(t), YG)
    if t < TLV:
        u = (t - TLIFT) / (TLV - TLIFT)
        return (X_LIFT + V * (t - TLIFT), YG - CLIMB * smooth(u))
    if t < TL0: return (X_LV + V * (t - TLV), YC)
    if t < TL1:
        ph = loop_phi(t); cx = X_L0 + DRIFT * (t - TL0)
        return (cx + R * math.sin(ph), YC - R + R * math.cos(ph))
    if t < TDROP: return (_x_slow(t), YC + 6 * math.sin(t * 3) * ramp(t, TSTOP, TSTOP + 0.5))
    if t < TIMP:
        s = (t - TDROP) / (TIMP - TDROP)
        return (lerp(X_H, XI, smooth(s)), lerp(YC, YI, s * s))
    return (XI, YI)
def pitch(t):
    if t < TX0: return 0.0
    if t < TL1 + 0.3:
        a, b = pos(t - 0.01), pos(t + 0.01)
        if math.hypot(b[0] - a[0], b[1] - a[1]) < 1e-3: return 0.0
        th = math.atan2(b[1] - a[1], b[0] - a[0])
        n = loop_phi(t) if TL0 <= t < TL1 else 0.0                   # unwrap: keep turning the same way
        k = round((-n - th) / (2 * math.pi)) if t >= TL0 else 0
        return th + 2 * math.pi * k
    if t < TDROP: return 0.0
    if t < TIMP:
        s = (t - TDROP) / (TIMP - TDROP)
        return math.pi / 2 * smooth(ramp(s, 0.0, 0.35)) + 2 * math.pi * smooth(ramp(s, 0.15, 1.0))
    s = t - TIMP
    return math.pi / 2 + 2 * math.pi + 0.14 * math.exp(-s * 3.5) * math.sin(s * 22)    # planted, wobbling
def judder(t):
    a = 0.0
    if CATCH <= t < TLIFT: a = 1.0
    for c in COUGH: a = max(a, 2.5 * pulse(t, c, 0.15))
    if TS0 <= t < TSTOP: a = 1.6
    return (a * 5 * math.sin(t * 61), a * 5 * math.cos(t * 47))
def prop_spin(t):                                                   # 0 stopped .. 1 blur
    if t < CATCH: return 0.0
    if t < TS0: return smooth(ramp(t, CATCH, CATCH + 0.6))
    return 1.0 - smooth(ramp(t, TS0 + 0.3, TSTOP - 0.2))
def prop_ang(t):
    a = 0.0
    for c in COUGH: a += math.pi * smooth(ramp(t, c, c + 0.35))
    a += 40 * max(0.0, t - CATCH) if t < TS0 else 40 * (TS0 - CATCH)
    if t >= TS0:                                                    # winds down, stops square
        u = ramp(t, TS0, TSTOP, "linear")
        a += 30 * (TSTOP - TS0) * (u - u * u / 2)
        a = round(a / math.pi) * math.pi * smooth(ramp(t, TSTOP - 0.3, TSTOP)) + a * (1 - smooth(ramp(t, TSTOP - 0.3, TSTOP)))
    return a
def plane_state(t):
    x, y = pos(t); jx, jy = judder(t)
    return x + jx, y + jy, pitch(t)

S = M.Scene(x0=0)
S.auto_blinks = False
S.card("second_degree_burn", "Fly a plane", "0", t0=0.35)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0
S.sfx(0.35, "tick", 0.04)

# ================================================================ worlds
def world(cr, t):
    O.draw_airfield_world(cr, t, x0=BORDER, sign_x=2230, sock_x=4300, hangar_x=1950)
    if t < T_ARR + 1: O.draw_letter(cr, 700, FLOOR_Y - 14, 380, 30, ())       # the EXPELLED letter, left behind
S.background(world)

def plane(cr, t, p, ly):
    x, y, a = plane_state(t)
    if ly == "back":
        O.draw_plane(cr, x, y, a, t, part="back")
        if t < CUT_IN or t >= TIMP:
            O.draw_plane(cr, x, y, a, t, part="front", prop=prop_spin(t), prop_ang=prop_ang(t), wheel=t < TW)
        return
    if CUT_IN <= t < TIMP:
        O.draw_plane(cr, x, y, a, t, part="front", prop=prop_spin(t), prop_ang=prop_ang(t))

# ---------------------------------------------------------------- smoke: coughs, the sputter, the spiral, the wreck
def _nose(t):
    x, y, a = plane_state(t); return O.plane_pt(x, y, a, 600, 0)
PUFFS = [(c + 0.05, 0) for c in COUGH] + [(TS0 + k * 0.28, 1) for k in range(6)]
_tt = TS0 + 1.7
while _tt < TIMP: PUFFS.append((_tt, 2)); _tt += 0.045
_r = random.Random(8)
def smoke(cr, t, p, ly):
    if ly != "back": return
    for t0, kind in PUFFS:
        a = t - t0
        life = (1.2, 1.5, 2.2)[kind]
        if not (0 <= a < life): continue
        x, y = _nose(t0)
        if kind == 2 and t0 < TDROP: continue
        r = (70, 110, 120)[kind] * (0.5 + 1.2 * a / life)
        O.draw_smoke_puff(cr, x - 60 * a, y - 90 * a, r, alpha=(1 - a / life) ** 0.8, dark=0.85)
    if t >= TIMP:                                                   # the wreck smoulders
        for k in range(8):
            a = ((t - TIMP) * 0.55 + k / 8) % 1.0
            O.draw_smoke_puff(cr, XI - 40 + 60 * a + 30 * math.sin(k), FLOOR_Y - 150 - 700 * a, 60 + 110 * a, alpha=(1 - a) * 0.7, dark=0.55)

# ================================================================ SHOT 1: the white room. reads it. stares.
S.set(0.0, "stand", "deadpan", dur=0.0, **SOOT)
S.read_card(0.6, react="dead_stare", lines=1, face="deadpan")
S.set(2.9, "stand", "dead_stare", dur=0.3, lid=1.0, **SOOT)                    # slow blink
S.set(3.35, "stand", "dead_stare", dur=0.4, **SOOT)

# ================================================================ WALK right, into the airfield
S.xkeys.append((T_WALK, SXW, T_ARR - T_WALK, "smooth")); S.x = SXW
S.camera(T_WALK + 0.2, 1500, 960, 0.8, 2.2)
S.camera(T_WALK + 2.4, *CAM_FIELD, dur=T_ARR - T_WALK - 1.8)
S.set(T_WALK, "stand", "dead_stare", dur=0.3, look=(0.7, 0.0), **SOOT)
S.set(T_ARR + 0.1, "stand", "dead_stare", dur=0.3, look=(0.9, -0.1), **SOOT)    # the plane
S.set(T_ARR + 1.0, "stand", "dead_stare", dur=0.4, look=(-0.8, -0.6), tilt=0.04, **SOOT)   # FLIGHT SCHOOL.
S.set(T_ARR + 1.9, "stand", "dead_stare", dur=0.4, look=(0.0, 0.0), tilt=0.0, **SOOT)      # us
S.blink(T_ARR + 2.5)

# ================================================================ COCKPIT
L.POSES["pilot"] = dict(lelb=(455, 1000), lhand=(440, 925), relb=(625, 1000), rhand=(640, 925), lhand_t="grip", rhand_t="grip",
                        lknee=(390, 1150), rknee=(690, 1150), lfoot=(470, 1250), rfoot=(610, 1250), nowalk=1.0)
L.POSES["eject"] = dict(L.POSES["cannonball"])
S.cut(CUT_IN, cam=CAM_PIT)
FLY = dict(lag=0.0, nowalk=1.0, **SOOT)
S.set(CUT_IN, "pilot", "dead_stare", dur=0.0, look=(0.0, 0.0), **FLY)
S.set(COUGH[0] + 0.25, "pilot", "dead_stare", dur=0.2, look=(0.9, 0.1), **FLY)              # the prop
S.set(COUGH[1] + 0.3, "pilot", "dead_stare", dur=0.2, look=(0.9, 0.1), lid=0.4, **FLY)
S.set(CATCH + 0.4, "pilot", "dead_stare", dur=0.3, look=(0.0, 0.0), **FLY)                   # us
S.blink(CATCH + 0.9)
for c in COUGH: S.sfx(c, "poof", 0.05)
S.sfx(CATCH, "whine", 0.03, dur=0.7)
S.sfx(TX0 + 0.5, "wind", 0.03, dur=TLIFT - TX0)
S.sfx(TLIFT, "whoosh", 0.06)
def cost(t): return ramp(t, TL0 + 1.5, TL1, "linear")             # what the loops are doing to him
S.set(TLV + 0.3, "pilot", "dead_stare", dur=0.4, look=(0.0, 0.0), curl=-0.35, **FLY)
S.blink(TLV + 1.2)
k_t = TL0
for i, d in enumerate(LOOPS):                                    # builds: green rising, sweat, quiver; still deadpan
    c = cost(k_t + d)
    S.set(k_t, "pilot", "dead_stare", dur=d, ease="linear", look=(0.0, 0.0), curl=-0.35 - 0.3 * c,
          heat_fill=0.95 * c, sick=1.0, sweat=0.8 * c, quiver=0.7 * c, pupil=0.82 - 0.3 * c, lid=0.3 - 0.15 * c, **FLY)
    if i < 3: S.sfx(k_t + d * 0.25, "whoosh", 0.03 + 0.01 * i)
    k_t += d
S.sfx(TL0 + 4.0, "wind", 0.04, dur=TL1 - TL0 - 4.0)
SICK = dict(heat_fill=0.95, sick=1.0, sweat=0.8, quiver=0.7, pupil=0.52, lid=0.15)
S.set(TS0, "pilot", "dead_stare", dur=0.5, look=(0.0, 0.0), curl=0.0, **SICK, **FLY)
for k in range(3): S.sfx(TS0 + 0.1 + k * 0.45, "blub", 0.04)
S.sfx(TS0 + 0.3, "slide_down", 0.03, dur=1.3)
S.set(TSTOP + 0.4, "pilot", "dead_stare", dur=0.3, look=(0.9, 0.1), **SICK, **FLY)        # the propeller
S.set(TSTOP + 1.2, "pilot", "dead_stare", dur=0.35, look=(0.0, 0.0), **SICK, **FLY)       # us
S.set(TSTOP + 1.75, "pilot", "dead_stare", dur=0.25, **dict(SICK, lid=1.0), **FLY)   # slow blink
S.set(TSTOP + 2.15, "pilot", "dead_stare", dur=0.25, **SICK, **FLY)
S.sfx(TSTOP + 0.2, "wind", 0.02, dur=2.0)
S.sfx(TDROP, "slide_down", 0.06, dur=TIMP - TDROP)
S.set(TDROP + 0.2, "pilot", "dead_stare", dur=0.3, eyescale=1.15, **dict(SICK, lid=0.0), **FLY)

def in_plane(tt, p):
    if not (CUT_IN <= tt < TIMP): return p
    x, y, a = plane_state(tt)
    h = p["hip"]; c, s_ = math.cos(a), math.sin(a)
    for j in L.JOINTS:
        dx, dy = p[j][0] - h[0], p[j][1] - h[1]
        p[j] = (x + dx * c - dy * s_, y + dx * s_ + dy * c)
    p["tilt"] = p.get("tilt", 0.0) + a
    return p
S.hook(in_plane)

# camera: follows the plane, a little behind (a moving average), wide enough for the loops
def cam_target(t):
    xs = ys = 0.0; n = 8
    for k in range(n):
        x, y = pos(t - 0.45 * k / n); xs += x; ys += y
    return xs / n, ys / n
_ct = TX0
while _ct < TIMP + 0.3:
    x, y = cam_target(_ct)
    z = lerp(0.85, 0.6, smooth(ramp(_ct, TX0, TLIFT + 0.6)))
    if _ct >= TDROP: z = lerp(0.6, 0.55, ramp(_ct, TDROP, TIMP))
    cy = y - 120 if _ct < TIMP else 900
    S.camera(_ct, x + 120 * (1 - ramp(_ct, TL0, TL0 + 1.0)), min(cy, 1050), z, dur=0.1, ease="linear")
    _ct += 0.1

# ================================================================ BOOM. flung out. lands on his butt.
SXL = int(XI - 820 - 540)
LANDHIP = (540 + SXL, 1450)
S.flash(TIMP, 0.35)
S.sfx(TIMP, "kaboom", 0.45, dur=2.2); S.sfx(TIMP, "thud", 0.2); S.shake(TIMP, 0.8, 26)
S.sfx(TIMP + 0.25, "boing", 0.04)
S.cut(TIMP, x=SXL)
S.camera(TIMP + 0.01, XI - 450, 900, 0.55, 0.01, ease="linear")
S.camera(TIMP + 0.3, XI - 520, 960, 0.62, 1.0)
S.set(TIMP, "eject", "dead_stare", dur=0.0, eyescale=1.2, **dict(SICK, lid=0.0), lag=0.0, nowalk=1.0)
S.set(TLAND - 0.25, "sit_floor", "dead_stare", dur=0.25, **SICK, lag=0.0, nowalk=1.0, **SOOT)
def flung(tt, p):
    if not (TIMP <= tt < TLAND): return p
    u = (tt - TIMP) / (TLAND - TIMP)
    sx, sy, sa = plane_state(TIMP)
    sx, sy = O.plane_pt(sx, sy, sa, 0, -200)
    tx = lerp(sx, LANDHIP[0], u); ty = lerp(sy, LANDHIP[1], u) - 1100 * 4 * u * (1 - u)
    a = -2 * 2 * math.pi * smooth(u) + (math.pi / 2) * (1 - smooth(u))
    h = p["hip"]; c, s_ = math.cos(a), math.sin(a)
    for j in L.JOINTS:
        dx, dy = p[j][0] - h[0], p[j][1] - h[1]
        p[j] = (tx + dx * c - dy * s_, ty + dx * s_ + dy * c)
    p["tilt"] = p.get("tilt", 0.0) + a
    return p
S.hook(flung)
S.sfx(TIMP + 0.1, "whoosh", 0.05)
def impact_fx(cr, t, p, ly):
    if ly == "front" and TIMP <= t < TIMP + 1.0:
        u = (t - TIMP) / 1.0
        L.draw_poof(cr, XI, FLOOR_Y - 60, u, r=420, sid=51)
        L.draw_impact(cr, XI, FLOOR_Y - 120, min(1.0, u * 2), r=260, sid=52)
        rnd = random.Random(5)
        for i in range(12):                                         # clods of dirt
            a = rnd.uniform(-math.pi * 0.95, -math.pi * 0.05); sp = rnd.uniform(700, 1400)
            x = XI + math.cos(a) * sp * u; y = FLOOR_Y + math.sin(a) * sp * u + 1600 * u * u
            if y < FLOOR_Y: L.sketch_circle(cr, x, y, rnd.uniform(14, 30), 4, sid=5300 + i, fill=(0.45, 0.33, 0.22))
    if ly == "back" and t >= TIMP:                                  # the dirt mound round the nose
        L.sketch_ellipse(cr, XI, FLOOR_Y + 10, 230, 46, 6, sid=5320, fill=(0.50, 0.37, 0.24))
S.set(TLAND, "sit_floor", "dead_stare", dur=0.06, ease="snap", stretch=-0.3, **SICK, **SOOT)
S.set(TLAND + 0.15, "sit_floor", "dead_stare", dur=0.4, ease="back", stretch=0.0, **SICK, **SOOT)
S.sfx(TLAND, "thud", 0.18); S.sfx(TLAND + 0.02, "bonk", 0.04); S.shake(TLAND, 0.4, 14)
def land_fx(cr, t, p, ly):
    if ly == "front" and TLAND <= t < TLAND + 0.8: L.draw_poof(cr, LANDHIP[0], FLOOR_Y - 40, (t - TLAND) / 0.8, r=200, sid=32)
CALM = dict(heat_fill=0.5, sick=1.0, sweat=0.3, quiver=0.2)
S.set(TLAND + 0.8, "sit_floor", "dead_stare", dur=1.0, look=(0.0, 0.0), **CALM, **SOOT)
S.blink(TLAND + 1.2)
S.set(TW + 0.1, "sit_floor", "dead_stare", dur=0.3, look=(0.8, -0.3), **CALM, **SOOT)     # a tok from the plane
S.set(TW + 0.4, "sit_floor", "dead_stare", dur=0.3, look=(0.3, -0.9), **CALM, **SOOT)     # it's coming

# ---------------------------------------------------------------- the wheel pops off. bonk.
def wheel_pos(t):
    x, y, a = plane_state(TW)
    w0 = O.plane_pt(x, y, a, O.WHEEL[0], O.WHEEL[1])
    head = (LANDHIP[0], 985 - 140)
    if t < TBONK:
        u = (t - TW) / (TBONK - TW)
        return (lerp(w0[0], head[0], u), lerp(w0[1], head[1], u) - 700 * 4 * u * (1 - u)), u * 9
    u = t - TBONK                                                   # bounces off to the left and rolls away
    yb = min(FLOOR_Y - 70, head[1] - 500 * u + 2600 * u * u)
    return (head[0] - 520 * u, yb), 9 - u * 8
def loose_wheel(cr, t, p, ly):
    if ly != "front" or t < TW: return
    (x, y), sp = wheel_pos(t)
    if x < LANDHIP[0] - 1600: return
    O.plane_wheel(cr, x, y, O.WHEEL[2], spin=sp)
    if TBONK <= t < TBONK + 0.4: L.draw_impact(cr, LANDHIP[0], 830, (t - TBONK) / 0.4, r=90, sid=61)
S.sfx(TW, "tok", 0.05); S.sfx(TBONK, "bonk", 0.1)
S.set(TBONK, "sit_floor", "dead_stare", dur=0.05, ease="snap", squash=0.3, lid=0.8, look=(0.0, 0.0), **CALM, **SOOT)
S.set(TBONK + 0.2, "sit_floor", "dead_stare", dur=0.3, ease="back", squash=0.0, look=(0.0, 0.0), **CALM, **SOOT)
S.blink(TBONK + 1.2)

# ================================================================ stands. the ask, on the airfield.
S.stand(STAND, face="dead_stare")
S.set(STAND, "stand", "dead_stare", dur=0.4, **CALM, **SOOT)
S.t = T_ASK
S.camera(T_ASK - 0.9, LANDHIP[0] + 60, 930, 1.12, 0.9)
S.the_ask(T_ASK, hold=6.0, keep=dict(SOOT, sick=1.0, heat_fill=0.4))
S.hook(lambda tt, p: (p.update(soot=0.65, frizz=max(p.get("frizz", 0.0), 0.5)) if tt >= 0 else None) or p)

# ---------------------------------------------------------------- draw order
S.props.insert(0, smoke); S.props.insert(1, plane)
for f in (impact_fx, land_fx, loose_wheel): S.prop(f)

if __name__ == "__main__":
    S.render("day008.mp4")
