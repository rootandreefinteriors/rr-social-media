"""Day 8 — COMMENT episode: @second_degree_burn "Fly a plane" (Instagram, day 7 reel, 0 likes).
RE-CUT on Justin's notes (2026-10-30): no soot, green has to pay off (he pukes, back to normal), no wheel bonk, bigger:
he keeps climbing out of the atmosphere into space, then falls all the way back down. Generic plane, no brand.

SHOT 1  The empty white room (where the hat blasted him on day 7), the EXPELLED letter on the floor. Reads the
        comment. Stares. Slow blink.
WALK    He walks off to the right into an airfield: hangar, FLIGHT SCHOOL sign, windsock, a little red propeller plane.
        Looks at the plane. At the sign. At us.
COCKPIT CUT: he's in it. The engine coughs twice, catches. Taxi, lift-off, level flight. He looks at us.
LOOPS   A loop. Another, faster. Faster and faster. His face slowly goes green. Dead stare the whole time.
UP      Out of the last loop he pulls straight up and just keeps going: the sky goes dark blue, then black, stars.
SPACE   CUT: space, the curve of the Earth below. The plane drifts up into frame and slows to a stop. The propeller
        sputters (no air) and stops. Total silence. He looks down at the Earth. At us. His face is very green. He
        pukes: a big wobbly zero-g blob floats out in front of him. He's back to normal. Long, uncomfortable stare at
        us while the blob drifts past. Blink. Then gravity remembers: the plane drops out of frame. The blob hangs
        there a beat, then follows.
REENTRY CUT: falling nose-first, on fire, shaking, the flaming puke blob tumbling after him. Deadpan.
CRASH   CUT: the airfield. Whistle. The plane comes straight down into the field: BOOM, a giant dust cloud. He's
        flung out and lands on his butt. Beat. SPLAT: the still-burning puke lands right next to him and sizzles.
        He looks at it. At us.
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
XS, YS = 80000.0, 980.0         # space: the plane's resting seat; the Earth below
CAM_SPACE = (XS + 60, 820, 0.62)
XR, YR = 50000.0, 900.0         # re-entry shot
XI = 9000.0                     # where it plants, on the airfield
YI = FLOOR_Y + 200 - 625        # seat y once planted nose-down (nose 200 px into the ground)

# ---------------------------------------------------------------- timeline
T_WALK, T_ARR = 4.0, 9.0
CUT_IN = 12.0                   # in the cockpit
COUGH = (13.0, 13.6)
CATCH = 14.2                    # engine catches, prop blurs
TX0 = 15.4                      # taxi
TLIFT = 18.4                    # wheels off
TLV = 20.6                      # level
TL0 = 22.8                      # loops start
LOOPS = [2.4, 1.7, 1.25, 0.95, 0.75, 0.62, 0.55]
TL1 = TL0 + sum(LOOPS)
TPU = 0.5                       # pull-up into the vertical
CUT_SPACE = TL1 + 3.0
TARR_S = CUT_SPACE + 1.6        # drifts to a stop in space
TPROP0 = TARR_S - 0.3           # the prop sputters out (no air)
LOOKE = TARR_S + 1.2            # looks down at the Earth
PK0 = TARR_S + 2.6              # the puke
PK1 = PK0 + 1.0
TDROP = PK1 + 3.0               # gravity remembers
BDROP = TDROP + 0.55            # the blob follows
CUT_RE = TDROP + 1.0
CUT_LAND = CUT_RE + 2.8
TIMP = CUT_LAND + 0.55          # BOOM
TLAND = TIMP + 1.4              # he lands on his butt
TSPL = TLAND + 1.5              # the puke lands next to him
STAND = TSPL + 2.3
T_ASK = STAND + 0.9

V = 1300.0                      # cruising speed (px/s)
ACC = V / (TLIFT - TX0)
R = 560.0                       # loop radius
YC = -40.0                      # cruise altitude (seat y)
CLIMB = YG - YC
DRIFT = 260.0                   # loop centre drift (px/s)
R2 = 400.0                      # pull-up radius

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
    if t < TL1 + TPU:                                                # pulls up into the vertical
        th = (math.pi / 2) * (t - TL1) / TPU
        return (X_L1 + R2 * math.sin(th), YC - R2 * (1 - math.cos(th)))
    if t < CUT_SPACE:                                                # straight up, faster and faster
        u = t - TL1 - TPU
        return (X_L1 + R2, YC - R2 - (1300 * u + 900 * u * u))
    if t < TDROP:
        u = smooth(ramp(t, CUT_SPACE, TARR_S, "out"))
        return (XS, lerp(YS + 1900, YS, u) + 7 * math.sin(t * 1.7) * ramp(t, TARR_S, TARR_S + 1))
    if t < CUT_RE:
        s = t - TDROP
        return (XS, YS + 7 * math.sin(TDROP * 1.7) + 6000 * s * s)
    if t < CUT_LAND: return (XR, YR)
    if t < TIMP:
        s = (t - CUT_LAND) / (TIMP - CUT_LAND)
        return (XI, lerp(YI - 3200, YI, s ** 1.4))
    return (XI, YI)
def pitch(t):
    if t < TX0: return 0.0
    if t < CUT_SPACE:
        a, b = pos(t - 0.01), pos(t + 0.01)
        if math.hypot(b[0] - a[0], b[1] - a[1]) < 1e-3: return 0.0
        return math.atan2(b[1] - a[1], b[0] - a[0])
    if t < TDROP: return -math.pi / 2 * (1 - smooth(ramp(t, CUT_SPACE, TARR_S + 0.2)))
    if t < CUT_RE: return 0.6 * smooth(ramp(t, TDROP, TDROP + 0.4))
    if t < CUT_LAND: return 0.42 * math.pi + 0.05 * math.sin(t * 9)
    if t < TIMP: return math.pi / 2
    s = t - TIMP
    return math.pi / 2 + 0.14 * math.exp(-s * 3.5) * math.sin(s * 22)    # planted, wobbling
def judder(t):
    a = 0.0
    if CATCH <= t < TLIFT: a = 1.0
    for c in COUGH: a = max(a, 2.5 * pulse(t, c, 0.15))
    if TPROP0 <= t < TARR_S + 0.6: a = 1.6
    if CUT_RE <= t < CUT_LAND: a = 2.4
    return (a * 5 * math.sin(t * 61), a * 5 * math.cos(t * 47))
def prop_spin(t):                                                   # 0 stopped .. 1 blur
    if t < CATCH: return 0.0
    if t < TPROP0: return smooth(ramp(t, CATCH, CATCH + 0.6))
    return 1.0 - smooth(ramp(t, TPROP0 + 0.2, TARR_S + 0.6))
def prop_ang(t):
    a = 0.0
    for c in COUGH: a += math.pi * smooth(ramp(t, c, c + 0.35))
    a += 40 * (min(t, TPROP0) - CATCH) if t >= CATCH else 0.0
    if t >= TPROP0:                                                 # winds down, stops square
        T1 = TARR_S + 0.9
        u = ramp(t, TPROP0, T1, "linear")
        a += 20 * (T1 - TPROP0) * (u - u * u / 2)
        k = smooth(ramp(t, T1 - 0.3, T1))
        a = round(a / math.pi) * math.pi * k + a * (1 - k)
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
    if CUT_SPACE <= t < CUT_RE:
        O.draw_space(cr, t, XS, YS + 650 + 9000); return
    if CUT_RE <= t < CUT_LAND:                                      # falling through the sky, on fire
        for k in range(48):
            u = k / 47
            cr.rectangle(XR - 4000, YR - 2400 + k * 100, 8000, 104 if k < 47 else 4000)
            cr.set_source_rgb(*lerp((0.08, 0.10, 0.30), (0.55, 0.70, 0.95), u)); cr.fill()
        for k in range(5):                                          # clouds rushing up past him
            yy = YR + 2200 - ((t - CUT_RE) * 4200 + k * 900) % 4500
            O.draw_cloud(cr, XR - 900 + (k * 530) % 1800, yy, 1.1)
        for k in range(14):                                         # speed lines
            yy = YR + 2000 - ((t - CUT_RE) * 6000 + k * 330) % 4300
            xx = XR - 1400 + (k * 613) % 2800
            L.sketch_line(cr, [(xx, yy), (xx, yy - 500)], 5, sid=700 + k, amp=0.3, alpha=0.35, color=(1, 1, 1))
        return
    O.draw_airfield_world(cr, t, x0=BORDER, sign_x=2230, sock_x=1250, hangar_x=1950)
    if t < T_ARR + 1: O.draw_letter(cr, 700, FLOOR_Y - 14, 380, 30, ())       # the EXPELLED letter, left behind
S.background(world)

def plane(cr, t, p, ly):
    x, y, a = plane_state(t)
    if ly == "back":
        O.draw_plane(cr, x, y, a, t, part="back")
        if t < CUT_IN or t >= TIMP:
            O.draw_plane(cr, x, y, a, t, part="front", prop=prop_spin(t), prop_ang=prop_ang(t))
        return
    if CUT_IN <= t < TIMP:
        O.draw_plane(cr, x, y, a, t, part="front", prop=prop_spin(t), prop_ang=prop_ang(t))
def reentry_fire(cr, t, p, ly):
    if ly != "front" or not (CUT_RE <= t < CUT_LAND): return
    x, y, a = plane_state(t)
    for k, ly_ in enumerate((-60, 60, 160)):                        # tongues of fire streaming back from the nose
        pts = [O.plane_pt(x, y, a, 640 - 160 * i, ly_ + 30 * math.sin(t * 13 + i + k)) for i in range(9)]
        O.draw_flames(cr, pts, t + k, w=120 - 25 * k)

# ---------------------------------------------------------------- smoke: the coughs; the wreck smoulders
def _nose(t):
    x, y, a = plane_state(t); return O.plane_pt(x, y, a, 600, 0)
PUFFS = [(c + 0.05, 0) for c in COUGH] + [(TPROP0 + k * 0.3, 1) for k in range(3)]
def smoke(cr, t, p, ly):
    if ly != "back": return
    for t0, kind in PUFFS:
        a = t - t0
        life = (1.2, 1.5)[kind]
        if not (0 <= a < life): continue
        if kind == 1 and not (CUT_SPACE <= t < TDROP): continue
        x, y = _nose(t0)
        r = (70, 90)[kind] * (0.5 + 1.2 * a / life)
        O.draw_smoke_puff(cr, x - 60 * a + (40 * a if kind else 0), y - (90 * a if kind == 0 else 20 * a), r, alpha=(1 - a / life) ** 0.8, dark=0.85)
    if t >= TIMP + 0.8:                                             # the wreck smoulders
        for k in range(8):
            a = ((t - TIMP) * 0.55 + k / 8) % 1.0
            O.draw_smoke_puff(cr, XI - 40 + 60 * a + 30 * math.sin(k), FLOOR_Y - 150 - 700 * a, 60 + 110 * a,
                              alpha=(1 - a) * 0.7 * ramp(t, TIMP + 0.8, TIMP + 1.6), dark=0.55)

# ================================================================ SHOT 1: the white room. reads it. stares.
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(0.6, react="dead_stare", lines=1, face="deadpan")
S.set(2.9, "stand", "dead_stare", dur=0.3, lid=1.0)                         # slow blink
S.set(3.35, "stand", "dead_stare", dur=0.4)

# ================================================================ WALK right, into the airfield
S.xkeys.append((T_WALK, SXW, T_ARR - T_WALK, "smooth")); S.x = SXW
S.camera(T_WALK + 0.2, 1500, 960, 0.8, 2.2)
S.camera(T_WALK + 2.4, *CAM_FIELD, dur=T_ARR - T_WALK - 1.8)
S.set(T_WALK, "stand", "dead_stare", dur=0.3, look=(0.7, 0.0))
S.set(T_ARR + 0.1, "stand", "dead_stare", dur=0.3, look=(0.9, -0.1))       # the plane
S.set(T_ARR + 1.0, "stand", "dead_stare", dur=0.4, look=(-0.8, -0.6), tilt=0.04)   # FLIGHT SCHOOL.
S.set(T_ARR + 1.9, "stand", "dead_stare", dur=0.4, look=(0.0, 0.0), tilt=0.0)      # us
S.blink(T_ARR + 2.5)

# ================================================================ COCKPIT
L.POSES["pilot"] = dict(lelb=(455, 1000), lhand=(440, 925), relb=(625, 1000), rhand=(640, 925), lhand_t="grip", rhand_t="grip",
                        lknee=(390, 1150), rknee=(690, 1150), lfoot=(470, 1250), rfoot=(610, 1250), nowalk=1.0)
L.POSES["eject"] = dict(L.POSES["cannonball"])
S.cut(CUT_IN - 1 / 30, cam=CAM_PIT)
FLY = dict(lag=0.0, nowalk=1.0)
S.set(CUT_IN - 1 / 30, "pilot", "dead_stare", dur=0.0, look=(0.0, 0.0), **FLY)
S.set(COUGH[0] + 0.25, "pilot", "dead_stare", dur=0.2, look=(0.9, 0.1), **FLY)              # the prop
S.set(COUGH[1] + 0.3, "pilot", "dead_stare", dur=0.2, look=(0.9, 0.1), lid=0.4, **FLY)
S.set(CATCH + 0.4, "pilot", "dead_stare", dur=0.3, look=(0.0, 0.0), **FLY)                   # us
S.blink(CATCH + 0.9)
for c in COUGH: S.sfx(c, "poof", 0.05)
S.sfx(CATCH, "whine", 0.03, dur=0.7)
S.sfx(TX0 + 0.5, "wind", 0.03, dur=TLIFT - TX0)
S.sfx(TLIFT, "whoosh", 0.06)
S.set(TLV + 0.3, "pilot", "dead_stare", dur=0.4, look=(0.0, 0.0), curl=-0.35, **FLY)
S.blink(TLV + 1.2)
def cost(t): return ramp(t, TL0 + 1.0, TL1 + 2.0, "linear")      # the loops turn him green, slowly
k_t = TL0
for i, d in enumerate(LOOPS):
    c = cost(k_t + d)
    S.set(k_t, "pilot", "dead_stare", dur=d, ease="linear", look=(0.0, 0.0), curl=-0.35 - 0.3 * c,
          sick=0.85 * c, quiver=0.5 * c, sweat=0.4 * c, **FLY)
    if i < 3: S.sfx(k_t + d * 0.25, "whoosh", 0.03 + 0.01 * i)
    k_t += d
S.sfx(TL0 + 3.0, "wind", 0.04, dur=TL1 - TL0 - 3.0)
S.set(TL1, "pilot", "dead_stare", dur=1.5, look=(0.0, 0.0), curl=-0.6, sick=0.9, quiver=0.5, sweat=0.4, **FLY)
S.sfx(TL1 + 0.2, "whoosh", 0.06); S.sfx(TL1 + 0.6, "wind", 0.05, dur=CUT_SPACE - TL1 - 0.6)

def in_plane(tt, p):
    if not (CUT_IN - 1 / 30 <= tt < TIMP): return p
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
while _ct < CUT_SPACE - 0.05:
    x, y = cam_target(_ct)
    if _ct > TL1:                                                   # the climb: keep up with him
        k = smooth(ramp(_ct, TL1, TL1 + TPU + 0.3)); x2, y2 = pos(_ct)
        x, y = lerp(x, x2, k), lerp(y, y2 - 350, k)
    z = lerp(0.85, 0.6, smooth(ramp(_ct, TX0, TLIFT + 0.6)))
    S.camera(_ct, x + 120 * (1 - ramp(_ct, TL0, TL0 + 1.0)), min(y - 120, 1050), z, dur=0.1, ease="linear")
    _ct += 0.1

# ================================================================ SPACE. silence.
SICK = dict(sick=1.0, quiver=0.6, sweat=0.4)
S.cut(CUT_SPACE - 1 / 30, cam=CAM_SPACE)
S.camera(TARR_S + 0.5, XS + 60, 800, 0.74, PK0 - TARR_S - 0.5)        # slow creep in
S.camera(PK1 + 0.3, XS + 60, 780, 0.8, TDROP - PK1 - 0.3)
S.set(CUT_SPACE, "pilot", "dead_stare", dur=0.0, look=(0.0, 0.0), curl=0.0, **SICK, **FLY)
for k in range(3): S.sfx(TPROP0 + 0.05 + k * 0.3, "blub", 0.03)
S.set(TARR_S + 0.9, "pilot", "dead_stare", dur=0.3, look=(0.85, 0.2), **SICK, **FLY)        # the dead prop
S.set(LOOKE, "pilot", "dead_stare", dur=0.5, look=(0.0, 1.0), tilt=0.05, **SICK, **FLY)    # the Earth, down there
S.set(LOOKE + 0.9, "pilot", "dead_stare", dur=0.4, look=(0.0, 0.0), tilt=0.0, **SICK, **FLY)   # us
S.set(PK0 - 0.6, "pilot", "dead_stare", dur=0.5, look=(0.0, 0.0), **dict(SICK, quiver=1.0), mouth="wavy", **FLY)  # uh oh
S.set(PK0, "pilot", "dead_stare", dur=0.08, ease="snap", mouth="scream", open=1.0, lid=0.55, squash=0.15,
      **dict(SICK, quiver=0.0), **FLY)                                                           # HUURK
S.set(PK1, "pilot", "dead_stare", dur=0.25, look=(0.0, 0.0), sick=0.0, **FLY)                   # done. normal.
S.sfx(PK0, "sploosh", 0.06); S.sfx(PK0 + 0.35, "blub", 0.04)
S.blink(PK1 + 1.6)
S.set(PK1 + 2.0, "pilot", "dead_stare", dur=0.4, look=(0.5, -0.2), **FLY)                    # the blob, floating by
S.set(PK1 + 2.6, "pilot", "dead_stare", dur=0.3, look=(0.0, 0.0), **FLY)                     # us
S.sfx(TDROP, "slide_down", 0.05, dur=0.9)

def mouth_pt(p):
    hx, hy = p["head"]; tl = p.get("tilt", 0.0)
    return (hx - 55 * math.sin(tl), hy + 55 * math.cos(tl))
_MOUTH = {}
def blob_state(t, p=None):
    """(x, y, r, ang) of the zero-g puke."""
    if t < PK0: return None
    if t < PK1:
        if p is not None: _MOUTH["m"] = mouth_pt(p)
        mx, my = _MOUTH.get("m", (XS, YS - 420))
        u = (t - PK0) / (PK1 - PK0)
        r = 95 * smooth(u) ** 0.7 + 8
        return (mx + 70 + r * 1.05, my + 10 + r * 0.2, r, t * 0.6)
    mx, my = _MOUTH.get("m", (XS, YS - 420))
    bx, by = mx + 70 + 103 * 1.05, my + 10 + 103 * 0.2
    s = t - PK1
    x, y = bx + 70 * s, by - 35 * s
    if t >= BDROP: y += 6500 * (t - BDROP) ** 2
    return (x, y, 103, PK1 * 0.6 + 0.4 * s)
def puke(cr, t, p, ly):
    if ly != "front" or not (PK0 <= t < CUT_RE): return
    st = blob_state(t, p)
    if st is None: return
    x, y, r, a = st
    if t < PK1:                                                    # the stream, still coming out of his mouth
        mx, my = mouth_pt(p)
        k = 1 - smooth(ramp(t, PK1 - 0.25, PK1))
        if k > 0.02:
            O.draw_stream(cr, [(mx, my + 5), ((mx + x) / 2, (my + y) / 2 + 10), (x, y)], w=46 * k, color=O.PUKE, lumps=False)
    O.draw_puke(cr, x, y, r, t, a)
    if t < PK0 + 0.5: L.burst_lines(cr, x, y, (t - PK0) / 0.5, r0=r + 30, r1=r + 110, n=8, sid=33)

# ================================================================ RE-ENTRY: on fire
S.cut(CUT_RE - 1 / 30, cam=(XR + 120, 760, 0.6))
S.set(CUT_RE, "pilot", "dead_stare", dur=0.0, look=(0.0, 0.0), curl=0.6, **FLY)
S.sfx(CUT_RE, "wind", 0.08, dur=CUT_LAND - CUT_RE); S.sfx(CUT_RE + 0.05, "kaboom", 0.08, dur=2.6)
S.shake(CUT_RE, CUT_LAND - CUT_RE, 9)
S.blink(CUT_RE + 1.6)
def burning_blob(cr, t, p, ly):
    if ly != "front": return
    if CUT_RE <= t < CUT_LAND:                                     # the puke, tumbling after him, also on fire
        x, y = XR - 520 + 40 * math.sin(t * 3), YR - 1080 + 30 * math.cos(t * 4)
        O.draw_flames(cr, [(x + 10, y - 40 - 50 * i) for i in range(7)], t + 3, w=80)
        O.draw_puke(cr, x, y, 75, t, t * 2.0)

# ================================================================ CRASH on the airfield
SXL = int(XI - 1250 - 540)
LANDHIP = (540 + SXL, 1450)
S.cut(CUT_LAND - 1 / 30, cam=(XI - 380, 760, 0.52), x=SXL)
S.set(CUT_LAND, "pilot", "dead_stare", dur=0.0, look=(0.0, 0.0), curl=0.6, **FLY)
S.sfx(CUT_LAND, "slide_down", 0.06, dur=TIMP - CUT_LAND)
S.flash(TIMP, 0.4)
S.sfx(TIMP, "kaboom", 0.5, dur=2.6); S.sfx(TIMP, "thud", 0.2); S.shake(TIMP, 1.0, 30)
S.sfx(TIMP + 0.4, "boing", 0.04)
S.cut(TIMP - 1 / 30)
S.camera(TIMP + 0.6, XI - 760, 960, 0.58, 1.2)
S.camera(TLAND + 0.4, XI - 1250 + 80, 1000, 0.85, 1.0)
S.set(TIMP, "eject", "dead_stare", dur=0.0, eyescale=1.15, lid=0.0, lag=0.0, nowalk=1.0)
S.set(TLAND - 0.25, "sit_floor", "dead_stare", dur=0.25, lag=0.0, nowalk=1.0)
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
_rd = random.Random(12)
DUST = [(_rd.uniform(-1, 1), _rd.uniform(0.3, 1.0), _rd.uniform(0.6, 1.1)) for _ in range(16)]
def impact_fx(cr, t, p, ly):
    if ly == "front" and TIMP <= t < TIMP + 1.6:
        u = (t - TIMP) / 1.6
        a = 1 - smooth(ramp(u, 0.45, 1.0))
        for i, (dx, dy, sc) in enumerate(DUST):                    # a giant dust cloud that rolls out and clears
            r = (160 + 260 * sc) * (0.4 + 0.9 * smooth(min(1.0, u * 2.5)))
            x = XI + dx * 900 * smooth(min(1.0, u * 2)); y = FLOOR_Y - 80 - dy * 700 * smooth(min(1.0, u * 2))
            O.draw_smoke_puff(cr, x, y, r, alpha=a, dark=0.25)
        L.draw_impact(cr, XI, FLOOR_Y - 120, min(1.0, u * 4), r=300, sid=52)
        rnd = random.Random(5)
        for i in range(14):                                         # clods of dirt
            an = rnd.uniform(-math.pi * 0.95, -math.pi * 0.05); sp = rnd.uniform(900, 1700); v = t - TIMP
            x = XI + math.cos(an) * sp * v; y = FLOOR_Y + math.sin(an) * sp * v + 1600 * v * v
            if y < FLOOR_Y: L.sketch_circle(cr, x, y, rnd.uniform(16, 34), 4, sid=5300 + i, fill=(0.45, 0.33, 0.22))
    if ly == "back" and t >= TIMP:                                  # the dirt mound round the nose
        L.sketch_ellipse(cr, XI, FLOOR_Y + 10, 260, 50, 6, sid=5320, fill=(0.50, 0.37, 0.24))
S.set(TLAND, "sit_floor", "dead_stare", dur=0.06, ease="snap", stretch=-0.3)
S.set(TLAND + 0.15, "sit_floor", "dead_stare", dur=0.4, ease="back", stretch=0.0)
S.sfx(TLAND, "thud", 0.18); S.sfx(TLAND + 0.02, "bonk", 0.04); S.shake(TLAND, 0.4, 14)
def land_fx(cr, t, p, ly):
    if ly == "front" and TLAND <= t < TLAND + 0.8: L.draw_poof(cr, LANDHIP[0], FLOOR_Y - 40, (t - TLAND) / 0.8, r=200, sid=32)
S.set(TLAND + 0.8, "sit_floor", "dead_stare", dur=0.6, look=(0.0, 0.0))
S.blink(TLAND + 1.0)

# ---------------------------------------------------------------- SPLAT: the puke lands next to him, still burning
PX = LANDHIP[0] - 280
def splat(cr, t, p, ly):
    if t < TSPL - 0.35: return
    if t < TSPL:
        if ly != "front": return
        u = (t - TSPL + 0.35) / 0.35
        y = lerp(-400, FLOOR_Y - 60, u * u)
        O.draw_flames(cr, [(PX, y - 50 - 50 * i) for i in range(7)], t + 3, w=70)
        O.draw_puke(cr, PX, y, 65, t, t * 2)
        return
    if ly != "back": return
    s = t - TSPL
    sq = 0.85 - 0.25 * math.exp(-s * 8) * math.cos(s * 30)
    O.draw_puke(cr, PX, FLOOR_Y - 18, 75, t, 0.0, squash=min(0.95, sq))
    k = 1 - smooth(ramp(s, 0.6, 2.0))                               # a little flame, sizzling out
    if k > 0.02: O.draw_flames(cr, [(PX + 10, FLOOR_Y - 30 - 28 * i) for i in range(6)], t, w=55 * k)
    a = ramp(s, 0.4, 1.2) * (1 - ramp(s, 3.5, 5.0))
    for kk in range(3):
        u = ((s * 0.7) + kk / 3) % 1.0
        O.draw_smoke_puff(cr, PX + 20 * math.sin(kk + s), FLOOR_Y - 60 - 260 * u, 25 + 35 * u, alpha=a * (1 - u) * 0.6, dark=0.4)
S.sfx(TSPL, "splat", 0.09); S.sfx(TSPL + 0.15, "simmer", 0.03, dur=1.6)
S.set(TSPL + 0.35, "sit_floor", "dead_stare", dur=0.35, look=(-0.85, 0.5), tilt=0.04)      # it
S.set(TSPL + 1.3, "sit_floor", "dead_stare", dur=0.4, look=(0.0, 0.0), tilt=0.0)           # us
S.blink(TSPL + 1.9)

# ================================================================ stands. the ask, on the airfield.
S.stand(STAND, face="dead_stare")
S.t = T_ASK
S.camera(T_ASK - 0.9, LANDHIP[0] + 60, 930, 1.12, 0.9)
S.the_ask(T_ASK, hold=6.0)

# ---------------------------------------------------------------- draw order
S.props.insert(0, smoke); S.props.insert(1, plane)
for f in (reentry_fire, burning_blob, puke, impact_fx, land_fx, splat): S.prop(f)

if __name__ == "__main__":
    S.render("day008.mp4")
