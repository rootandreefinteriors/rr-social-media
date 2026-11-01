"""Day 10 — COMMENT episode: @second_degree_burn "Pick up a ring and take it to mordor" (Instagram, day 9 reel, 0 likes).
RE-CUT 2 on Justin's notes (2026-11-01): he never goes back to an old world (stays in Mordor); ADHD pacing; tension;
fan in-jokes; the story has to make sense and pay off (the ring is destroyed for good, the eye falls); >= 60 s.
Parody of the ring story: everything drawn by us, no characters. The ring is his own gold green-hill ring.

GRAB    Green hill. Reads the comment. One ring left in the grass. Snatch. RINGS 1.
RUN     Speed-game sprint past a MORDOR sign to the black gate: ONE DOES NOT SIMPLY WALK INTO MORDOR. Reads it. Us.
EAGLES  Pulls a whistle from his hip, tweets: a giant eagle swoops in and flies him over the wall.
SEARCH  The eye's searchlight sweeps the sky (heartbeat; cut: the eye scanning). It closes in. He looks at the ring...
        puts it on and VANISHES. The beam finds: a giant eagle carrying nothing but a floating ring. Locks on the eagle.
        Cut: the eye narrows. The eagle looks at its empty talons, at the eye - lets go and bolts. The ring drops
        straight down into the volcano.
LAVA    Thud on the ledge (only the ring visible). He takes it off: back. Holds it over the lava. Heartbeat. Lets go.
        RINGS 0. Eye twitch - speed-game reflex - he lunges after it and teeters on the edge, arms windmilling, while
        the ring sizzles and MELTS. He steadies. Rumble. The lava rises...
BOOM    The volcano erupts and fires him out. Cut: the eye shakes, bulges - and blows up. The tower collapses.
END     He crash-lands in the rubble at the tower's foot. A chunk lands next to him. The burnt-out eyeball rolls up and
        stops beside him. Then - now that it's all over - the eagle shows up and lands next to him. He looks at it.
        At us. The ask, in the ruins of Mordor (he lives here now), the eagle beside him.
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y
from ink import smooth
import numpy as np

# ---------------------------------------------------------------- places
SX0 = 22871.36                             # where day 9 left him (x 23411)
X0 = 540 + SX0
GOALX = 23061.36
PALMS = [(10150, 760), (12350, 880), (14100, 720), (18900, 860), (20600, 760)]
FLOWERS = [10350, 11650, 12900, 13650, 14800, 15400, 18400, 19700, 21300, 22400]
BORDER = 24900.0
SIGN_X = 24560.0
GATE_X = 27600.0
XG = GATE_X - 500
SXG = XG - 540
TX, TH = 32600.0, 1330.0                   # the eye tower
EYE = (TX, FLOOR_Y - TH + 40)
VX, VH, VW = 34200.0, 3600.0, 3400.0       # the volcano
VRIM = O.volcano_rim(VX, VH)
SXI = 49460.0                              # inside the volcano (x 50000)
XI = 540 + SXI
EDGE = XI + 150
LAVA_Y = FLOOR_Y + 900
XL = TX - 900                              # he lands in the rubble at the tower's foot
SXL = XL - 540
RING0 = (X0 - 150, FLOOR_Y - 16)
EAGLE_LAND = (XL - 520, FLOOR_Y)

# ---------------------------------------------------------------- timeline
T_PICK = 2.85
T_RUN, T_RUN1 = 4.1, 7.5
T_PULL = 9.5
T_BLOW = 12.25
T_SWOOP, T_GRAB = 13.0, 13.5
CUT_FLY = 14.2
CUT_E1, CUT_B1 = 16.0, 16.8                # cut: the eye scanning
T_RINGON, T_INVIS = 18.0, 18.4             # puts the ring on: gone
T_LOCK = 18.9                              # the beam locks on... the eagle
CUT_E2, CUT_B2 = 19.1, 19.8                # cut: the eye narrows
T_LETGO, T_FALL = 20.6, 21.0
CUT_IN = 21.8
T_ILAND = 22.3
T_OFF = 22.9                               # takes it off: back
T_REACH = 23.8
T_DROP = 26.0
T_LAVA = T_DROP + math.sqrt(2 * (LAVA_Y - 20 - 955) / 2600)
T_LUNGE, T_STEADY = 26.55, 28.5
T_MELT = T_LAVA + 1.1
T_RUMBLE = 29.4
CUT_OUT = 31.2
CUT_EYE, T_POP = 33.0, 34.1
CUT_T = 35.0
T_TLAND = 35.6
T_CHUNK = 36.2
T_ROLL0, T_ROLL1 = 36.9, 38.1              # the burnt-out eyeball rolls up
T_EAGLE0, T_EAGLE1 = 39.3, 40.1            # the eagle shows up. now.
T_STAND = 42.3
T_ASK = 43.2
ASK_HOLD = 11.0

S = M.Scene(x0=SX0)
S.auto_blinks = False
S.card("second_degree_burn", "Pick up a ring and take it to mordor", "0", t0=0.3)
CAM0 = (X0 + 20, 930, 1.12)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0
S.sfx(0.3, "tick", 0.04)

# ================================================================ flight path (hip target while the eagle has him)
P0, P1 = (XG + 700, -500.0), (VX - 100, -3000.0)
def hip_target(t):
    if t < T_GRAB: return None
    if t < CUT_FLY: return (XG, lerp(1118, -800, smooth(ramp(t, T_GRAB + 0.05, T_GRAB + 0.7))))
    if t < CUT_B2:
        u = ramp(t, CUT_FLY, CUT_B2, "linear")
        return (lerp(P0[0], P1[0], u), lerp(P0[1], P1[1], u) + 30 * math.sin(t * 9))
    if t < T_FALL: return (P1[0], P1[1])
    s = t - T_FALL
    return (P1[0], P1[1] + 0.5 * 2600 * s * s)

def beam_target(t):
    h = hip_target(t)
    if h is None: return None
    if t < T_LOCK:
        k = 1 - smooth(ramp(t, 15.0, T_LOCK - 0.3))
        return (h[0] + 1500 * k * math.sin(t * 2.6) + 120, h[1] + 500 * k * math.cos(t * 1.9) - 300 * smooth(ramp(t, T_INVIS, T_LOCK)))
    return (h[0] + 40, h[1] - 830) if t < T_LETGO else eagle_xy(t)

def eagle_xy(t):
    st = eagle_state(t)
    return (st[0], st[1] - 260) if st else (P1[0], P1[1])

POP_SHAKE = []
def eye_state(t):
    st = dict(look=0.6, look_y=0.0, lid=0.0, flare=1.0)
    if CUT_FLY <= t < CUT_IN:
        bt = beam_target(t)
        st.update(look=max(-1.0, min(1.0, (bt[0] - TX) / 1500)), look_y=-1.0)
        if CUT_E1 <= t < CUT_B1: st.update(look=math.sin((t - CUT_E1) * 7) * 0.8, lid=0.15)
        if t >= T_LOCK:
            st.update(look=0.0, lid=0.5 * smooth(ramp(t, CUT_E2 + 0.1, CUT_E2 + 0.5)), flare=lerp(1.0, 1.7, ramp(t, T_LOCK, CUT_E2 + 0.5)))
    elif CUT_IN <= t < CUT_T:                                     # the ring melts: the eye loses it
        k = ramp(t, CUT_EYE, T_POP)
        st.update(look=0.35 * math.sin(t * 41) * k, look_y=0.35 * math.cos(t * 37) * k, lid=0.0, flare=1.0 + 1.8 * k)
    return st

# ================================================================ worlds
def goal_sign(cr):
    x, yb = GOALX, FLOOR_Y
    L.sketch_rect(cr, x - 12, yb - 520, x + 12, yb, 5, sid=7300, fill=(0.62, 0.64, 0.68))
    cy = yb - 690
    L.sketch_ellipse(cr, x, cy, 165, 165, 7, sid=7301, fill=(0.45, 0.70, 1.0))
    cr.save(); cr.translate(x, cy)
    L.sketch_circle(cr, 0, 8, 105, 6, sid=7302)
    for ex in (-38, 38):
        L.sketch_circle(cr, ex, -5, 22, 4, sid=7303 + (ex > 0))
        cr.arc(ex + 3, -2, 8, 0, 2 * math.pi); cr.set_source_rgb(0.07, 0.07, 0.08); cr.fill()
    L.sketch_line(cr, [(-30, 55), (30, 55)], 5, sid=7305)
    O.sketch_curve(cr, (0, -97), (-10, -150), (18, -140), 5, sid=7306)
    cr.restore()

def ruins(cr, t):
    """the tower after the eye blew: a jagged smoking stump, rubble round the base."""
    x, yb = TX, FLOOR_Y; tw = 150
    top = yb - TH * 0.5
    pts = [(x - tw * 1.9, yb), (x - tw * 1.3, top + 90), (x - tw * 0.9, top - 40), (x - tw * 0.4, top + 60), (x, top - 90),
           (x + tw * 0.5, top + 40), (x + tw * 1.0, top - 20), (x + tw * 1.35, top + 110), (x + tw * 1.9, yb)]
    L.sketch_poly(cr, pts, 7, sid=7800, fill=(0.12, 0.10, 0.11), amp=0.4)
    for k in range(3):
        L.sketch_rect(cr, x - 18, top + 260 + 230 * k, x + 18, top + 310 + 230 * k, 3, sid=7801 + k, fill=(0.30, 0.25, 0.25))
    for k in range(4):
        a = (t * 0.25 + k / 4) % 1.0
        O.draw_smoke_puff(cr, x - 60 + 40 * k - 200 * a, top - 120 - 900 * a, 80 + 260 * a, alpha=(1 - a) * 0.85, dark=0.8)
    O.draw_flames(cr, [(x + 60, top + 10 - 30 * i) for i in range(6)], t, w=60)
    for i, (dx, r) in enumerate(((-420, 90), (-300, 60), (330, 110), (460, 70), (-560, 50), (580, 55))):
        L.sketch_poly(cr, [(x + dx - r, yb + 4), (x + dx - r * 0.6, yb - r * 0.9), (x + dx + r * 0.5, yb - r), (x + dx + r, yb + 4)],
                      5, sid=7810 + i, fill=(0.14, 0.12, 0.13))

def world(cr, t):
    if CUT_IN <= t < CUT_OUT:
        rise = 640 * smooth(ramp(t, T_RUMBLE + 0.3, CUT_OUT))
        O.draw_lava_chamber(cr, t, EDGE, LAVA_Y, rise=rise)
        return
    if t < CUT_FLY:
        O.draw_green_hill_world(cr, t, x0=9800, x1=BORDER, palms=PALMS, flowers=FLOWERS)
        goal_sign(cr)
        O.draw_signpost(cr, SIGN_X, "MORDOR")
    if t >= T_POP:
        O.draw_dark_land_world(cr, t, x0=BORDER, x1=45000, volcano=(VX, VH, VW), gate=GATE_X, tower=None)
        ruins(cr, t)
        return
    es = eye_state(t)
    O.draw_dark_land_world(cr, t, x0=BORDER, x1=45000, volcano=(VX, VH, VW), gate=GATE_X, tower=dict(x=TX, h=TH, **es))
S.background(world)

# ================================================================ GRAB: reads it, snatches the last ring
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(0.4, react="dead_stare", lines=2, dur=1.5, face="deadpan")
S.set(2.3, "stand", "dead_stare", dur=0.2, look=(-0.55, 0.95), tilt=-0.06)            # the ring in the grass
L.POSES["pick_l"] = dict(L.POSES["crouch"]); L.POSES["pick_l"].update(head=(440, 930), neck=(480, 1050), hip=(550, 1260),
                         lelb=(420, 1260), lhand=(392, 1432), relb=(580, 1150), rhand=(520, 1250), lhand_t="open")
L.POSES["hold_ring_l"] = dict(lelb=(430, 930), lhand=(390, 830), lhand_t="grip", swing=0.25)
S.set(2.55, "pick_l", "dead_stare", dur=0.25, look=(-0.6, 0.9))
S.set(T_PICK - 0.03, "pick_l", "dead_stare", dur=0.05, look=(-0.6, 0.9), lhand_t="grip")
S.set(T_PICK + 0.25, "hold_ring_l", "dead_stare", dur=0.3, look=(-0.7, -0.3))
S.set(T_PICK + 0.9, "hold_ring_l", "dead_stare", dur=0.25, look=(0.0, 0.0))            # us. RINGS 1.
S.camera(2.5, X0 - 60, 960, 1.12, 0.3); S.camera(T_PICK + 0.3, X0 + 20, 930, 1.12, 0.4)

# ================================================================ RUN to the black gate
S.set(T_RUN - 0.15, "hold_ring_l", "dead_stare", dur=0.12, look=(0.8, 0.0), stretch=-0.15)
S.set(T_RUN, "hold_ring_l", "deadpan", dur=0.15, run=1.0, look=(0.8, 0.0), lid=0.3, lean=0.12, lag=0.4)
S.xkeys.append((T_RUN, SXG, T_RUN1 - T_RUN, "linear")); S.x = SXG
L.POSES["skid"] = dict(hip=(500, 1130), neck=(470, 790), head=(455, 665), relb=(560, 880), rhand=(640, 820),
                       rhand_t="open", lelb=(400, 900), lhand=(390, 830), lhand_t="grip", lknee=(560, 1290), lfoot=(650, FLOOR_Y),
                       rknee=(620, 1300), rfoot=(720, FLOOR_Y), lfoot_dir=0.9, rfoot_dir=0.9, nowalk=1.0)
S.set(T_RUN1 - 0.05, "skid", "deadpan", dur=0.1, run=0.0, lag=0.0, lid=0.3)
S.set(T_RUN1 + 0.4, "hold_ring_l", "dead_stare", dur=0.3, ease="back", lag=1.0)
S.sfx(T_RUN, "whoosh", 0.05); S.sfx(T_RUN1 - 0.05, "skid", 0.08, dur=0.45)
def run_x(t): return 540 + lerp(SX0, SXG, ramp(t, T_RUN, T_RUN1, "linear"))
_ct = T_RUN - 0.1
while _ct < T_RUN1 + 0.5:
    x = run_x(_ct + 0.08)
    z = lerp(1.12, 0.78, smooth(ramp(_ct, T_RUN, T_RUN + 0.6)))
    S.camera(_ct, x + lerp(20, 380, smooth(ramp(_ct, T_RUN, T_RUN + 0.6))) - 130 * smooth(ramp(_ct, T_RUN1 - 0.3, T_RUN1 + 0.4)),
             lerp(930, 900, ramp(_ct, T_RUN, T_RUN + 0.6)), z, dur=1 / 15, ease="linear")
    _ct += 1 / 15
def run_fx(cr, t, p, ly):
    if ly != "back" or not (T_RUN + 0.2 <= t < T_RUN1 + 0.3): return
    h = p["hip"]
    for k, dy in enumerate((-430, -250, -60, 120)):
        L.motion_lines(cr, h[0] - 220, h[1] + dy, math.pi, n=1, length=420 + 120 * (k % 2), alpha=0.8, sid=7110 + k, width=6)
    a = (t * 5) % 1.0
    O.draw_smoke_puff(cr, h[0] - 120 - 200 * a, FLOOR_Y - 40 - 50 * a, 40 + 70 * a, alpha=0.7 * (1 - a), dark=0.3)
S.prop(run_fx)
CAM_GATE = (XG + 250, 900, 0.78)
S.camera(T_RUN1 + 0.5, *CAM_GATE, dur=0.4)
S.set(T_RUN1 + 0.6, "hold_ring_l", "dead_stare", dur=0.25, look=(0.6, -0.6), tilt=-0.05)       # the sign
def sign_read(tt, p):
    if T_RUN1 + 0.85 <= tt < T_RUN1 + 2.0:
        k = (tt - T_RUN1 - 0.85) / 0.55; u = k % 1.0
        p["look"] = (0.3 + 0.6 * smooth(u), -0.65 + 0.12 * int(k))
    return p
S.hook(sign_read)
S.set(T_RUN1 + 2.05, "hold_ring_l", "dead_stare", dur=0.25, look=(0.0, 0.0), tilt=0.0)          # us
S.blink(T_RUN1 + 2.6)

# ================================================================ EAGLES: the whistle
def whistle(cr, x, y, s, t, p):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    L.sketch_rect(cr, -70, -22, 10, 22, 5, sid=7400, fill=(0.80, 0.82, 0.86))
    L.sketch_circle(cr, 22, 6, 34, 5, sid=7401, fill=(0.80, 0.82, 0.86))
    cr.restore()
_k0 = len(S.keys)
S.pocket_pull(T_PULL, "whistle", whistle, (0, 0), held=True, offset=(-10, -40), narrow_w=0)
for i in range(_k0, len(S.keys)):                                 # keep the pull deadpan (no delighted faces)
    k = S.keys[i]; d = dict(k[1]); d.update(L.EXPR["deadpan"]); d["open"] = 0.0; d["eyescale"] = 1.0
    d["lhand"], d["lelb"], d["lhand_t"] = L.POSES["hold_ring_l"]["lhand"], L.POSES["hold_ring_l"]["lelb"], "grip"
    S.keys[i] = (k[0], d) + tuple(k[2:])
L.POSES["blow"] = dict(L.POSES["hold_ring_l"]); L.POSES["blow"].update(relb=(640, 840), rhand=(600, 700), rhand_t="grip")
S.set(T_BLOW, "blow", "deadpan", dur=0.2, look=(0.0, 0.0), lid=0.5)
S.set(T_BLOW + 0.75, "hold_ring_l", "dead_stare", dur=0.2, look=(-0.5, -0.9), tilt=-0.08)       # something's coming
S.hide("whistle", T_GRAB)
S.camera(T_BLOW + 0.3, XG + 200, 740, 0.62, 0.5)
L.POSES["hang"] = dict(lelb=(480, 570), lhand=(515, 470), relb=(600, 570), rhand=(565, 470), lhand_t="fist", rhand_t="fist",
                       lknee=(515, 1300), rknee=(575, 1300), lfoot=(505, 1460), rfoot=(585, 1460), nowalk=1.0, lag=0.0)
S.set(T_GRAB, "hang", "dead_stare", dur=0.08, ease="snap", look=(0.0, -0.3), lag=0.0)
S.set(T_GRAB + 0.4, "hang", "dead_stare", dur=0.3, look=(0.0, 0.0), lag=0.0)
S.shake(T_GRAB, 0.3, 10)
S.sfx(T_GRAB, "whoosh", 0.07)

def carried(tt, p):
    h = hip_target(tt)
    if h is None or tt >= CUT_IN - 1 / 30: return p
    dx, dy = h[0] - p["hip"][0], h[1] - p["hip"][1]
    for j in L.JOINTS: p[j] = (p[j][0] + dx, p[j][1] + dy)
    if tt >= T_FALL:                                              # falling: arms flail up
        p["lhand"] = (p["lhand"][0] - 40 * math.sin(tt * 30), p["lhand"][1]); p["rhand"] = (p["rhand"][0] + 40 * math.sin(tt * 27), p["rhand"][1])
    return p
S.hook(carried)


def eagle_state(t):
    """(talon x, talon y, alarm, look, flap, face) or None"""
    if t < T_SWOOP: return None
    if t < T_GRAB:
        u = smooth((t - T_SWOOP) / (T_GRAB - T_SWOOP))
        return (lerp(XG - 1500, XG, u), lerp(-300, 1118 - 648, u) - 250 * math.sin(math.pi * u), 0.0, 0.0, 1.3, 1)
    if t < T_LETGO:
        h = hip_target(t)
        alarm = smooth(ramp(t, CUT_B2, CUT_B2 + 0.15))
        look = 0.0
        if CUT_B2 <= t: look = 1.0 if (t < CUT_B2 + 0.3 or CUT_B2 + 0.65 <= t < CUT_B2 + 0.85) else -0.6   # talons... eye... talons
        return (h[0], h[1] - 648, alarm, look, 1.0, 1)
    if t < CUT_IN:
        s = t - T_LETGO
        return (P1[0] + 1600 * s, P1[1] - 648 - 1300 * s - 300 * s * s, 1.0, 1.0, 1.4, 1)
    if t < T_EAGLE0: return None
    if t < T_EAGLE1:                                              # shows up now that it's over
        u = smooth((t - T_EAGLE0) / (T_EAGLE1 - T_EAGLE0))
        return (lerp(EAGLE_LAND[0] - 1500, EAGLE_LAND[0], u), lerp(-700, EAGLE_LAND[1], u), 0.0, 0.0, 1.2 * (1 - u) + 0.15, 1)
    look = 0.8
    if T_EAGLE1 + 1.2 <= t < T_EAGLE1 + 2.4: look = -0.6                          # looks at the ruins
    if t >= T_ASK + ASK_HOLD * 0.35 + 6.9: look = 0.9
    return (EAGLE_LAND[0], EAGLE_LAND[1], 0.0, look, 0.06, 1)
def eagle(cr, t, p, ly):
    if ly != "front": return
    st = eagle_state(t)
    if st is None: return
    x, y, alarm, look, flap, face = st
    O.draw_eagle(cr, x, y, t, flap=flap, s=0.8, look=look, alarm=alarm, face=face)
    if T_LETGO <= t < T_LETGO + 1.2:                              # feathers everywhere
        rr = random.Random(7)
        for i in range(10):
            s = t - T_LETGO
            fx = P1[0] + rr.uniform(-300, 300) + rr.uniform(-200, 200) * s
            fy = P1[1] - 900 + rr.uniform(-200, 200) + 260 * s
            O.draw_eagle_feather(cr, fx, fy, t * 3 + i, sid=7500 + i)
S.prop(eagle)
S.sfx(T_SWOOP, "whoosh", 0.06)

# ================================================================ SEARCH: flight, beam, the ring goes on, lock, drop
S.cut(CUT_FLY - 1 / 30)
_ct = CUT_FLY - 1 / 30
CAM_E = (EYE[0], EYE[1] - 40, 1.5)
while _ct < CUT_IN - 1 / 30:
    if CUT_E1 - 1 / 30 <= _ct < CUT_B1 - 1 / 30: cam = (CAM_E[0], CAM_E[1], 1.45 + 0.1 * ramp(_ct, CUT_E1, CUT_B1))
    elif CUT_E2 - 1 / 30 <= _ct < CUT_B2 - 1 / 30: cam = (CAM_E[0], CAM_E[1], 1.55 + 0.35 * smooth(ramp(_ct, CUT_E2, CUT_B2)))
    else:
        h = hip_target(_ct + 1 / 30)
        cam = (h[0] + 700, h[1] + 20, 0.4)
    S.camkeys.append((_ct, cam, 1 / 30, "linear")); _ct += 1 / 30
for c in (CUT_E1, CUT_B1, CUT_E2, CUT_B2): S.cuts.append(c - 1 / 30)
S.set(CUT_FLY, "hang", "dead_stare", dur=0.0, look=(0.3, 0.6), lag=0.0)
S.set(15.6, "hang", "dead_stare", dur=0.3, look=(0.6, 0.9), lag=0.0)                 # the beam below
S.set(17.0, "hang", "dead_stare", dur=0.25, look=(-0.5, -0.6), lag=0.0)              # the ring on his wrist...
S.set(17.5, "hang", "dead_stare", dur=0.25, look=(0.0, 0.0), lag=0.0)                # us.
S.set(T_INVIS, "hang", "dead_stare", dur=0.0, show=0.0, lag=0.0)                    # gone
S.sfx(T_INVIS, "twinkle", 0.08)
L.POSES["hang_alone"] = dict(L.POSES["hang"])
S.set(T_LETGO + 0.05, "hang_alone", "dead_stare", dur=0.15, show=0.0, lag=0.0, lhand_t="open", rhand_t="open")
S.sfx(CUT_FLY, "wind", 0.04, dur=CUT_IN - CUT_FLY)
for k in range(9):                                                # heartbeat while the beam closes in
    tk = 15.2 + k * (0.42 - 0.02 * k)
    S.sfx(tk, "thud", 0.05 + 0.006 * k); S.sfx(tk + 0.16, "thud", 0.035 + 0.004 * k)
S.sfx(T_LOCK, "kaboom", 0.09, dur=2.0)
S.sfx(T_FALL, "slide_down", 0.07, dur=0.8)
def beam(cr, t, p, ly):
    if ly != "back" or not (15.0 <= t < CUT_IN): return
    if CUT_E1 <= t < CUT_B1 or CUT_E2 <= t < CUT_B2:
        bt = beam_target(t); O.draw_beam(cr, (EYE[0], EYE[1] - 40), (EYE[0] + (bt[0] - EYE[0]) * 0.3, EYE[1] - 1500), width=500,
                                         alpha=ramp(t, 15.0, 15.4), locked=float(t >= T_LOCK)); return
    O.draw_beam(cr, (EYE[0], EYE[1]), beam_target(t), width=620, alpha=ramp(t, 15.0, 15.4), locked=smooth(ramp(t, T_LOCK, T_LOCK + 0.2)))
S.prop(beam)

# ================================================================ LAVA: inside the volcano
CAM_IN = (EDGE + 100, 1500, 0.6)
S.cut(CUT_IN - 1 / 30, cam=CAM_IN, x=SXI)
S.set(CUT_IN - 1 / 30, "stand", "dead_stare", dur=0.0, lag=0.0, nowalk=1.0, show=0.0)
def drop_in(tt, p):
    if not (CUT_IN - 1 / 30 <= tt < T_ILAND): return p
    u = (tt - CUT_IN) / (T_ILAND - CUT_IN)
    dy = -2300 * (1 - max(0.0, u) ** 2)
    for j in L.JOINTS: p[j] = (p[j][0], p[j][1] + dy)
    return p
S.hook(drop_in)
S.sfx(T_ILAND, "thud", 0.18); S.shake(T_ILAND, 0.35, 14)
def land_in_fx(cr, t, p, ly):
    if ly == "front" and T_ILAND <= t < T_ILAND + 0.7: L.draw_poof(cr, XI, FLOOR_Y - 30, (t - T_ILAND) / 0.7, r=160, sid=31)
    if ly == "front" and T_OFF <= t < T_OFF + 0.5: L.burst_lines(cr, XI, 900, (t - T_OFF) / 0.5, r0=200, r1=360, n=10, sid=82)
S.prop(land_in_fx)
L.POSES["hold_ring_r"] = dict(relb=(650, 930), rhand=(690, 830), rhand_t="grip")
L.POSES["reach_r"] = dict(relb=(668, 935), rhand=(752, 905), rhand_t="grip")
S.set(T_OFF, "hold_ring_r", "dead_stare", dur=0.0, show=1.0, look=(0.0, 0.0), sweat=0.6)
S.sfx(T_OFF, "pop", 0.08)
S.set(T_OFF + 0.45, "hold_ring_r", "dead_stare", dur=0.25, look=(0.7, 0.9), sweat=0.7)       # the lava
S.set(T_REACH, "reach_r", "dead_stare", dur=0.3, look=(0.8, 0.35), sweat=0.8)
S.set(T_REACH + 0.9, "reach_r", "dead_stare", dur=0.3, look=(0.0, 0.0), sweat=0.85)          # us
S.set(T_REACH + 1.6, "reach_r", "dead_stare", dur=0.3, look=(0.8, 0.35), tilt=0.06, sweat=0.9)   # the ring. last look.
S.set(T_DROP, "reach_r", "dead_stare", dur=0.06, ease="snap", rhand_t="open", sweat=0.9)
S.set(T_DROP + 0.2, "reach_r", "dead_stare", dur=0.25, look=(0.8, 0.95), tilt=0.08, rhand_t="open", sweat=0.9, twitch=1.0)
for k in range(5):
    tk = T_REACH + 0.2 + k * 0.4; S.sfx(tk, "thud", 0.05); S.sfx(tk + 0.15, "thud", 0.035)
# the lunge: speed-game reflex. he teeters on the edge, arms windmilling, and does NOT go after it.
L.POSES["teeter"] = dict(lelb=(450, 760), lhand=(400, 640), relb=(640, 760), rhand=(690, 640), lhand_t="open", rhand_t="open",
                         lean=-0.3, tiptoe=1.0, nowalk=1.0)
S.set(T_LUNGE, "teeter", "dead_stare", dur=0.15, ease="snap", look=(0.6, 0.95), eyescale=1.15, sweat=1.0, lag=0.3)
S.set(T_STEADY - 0.3, "teeter", "dead_stare", dur=0.3, look=(0.6, 0.95), eyescale=1.15, sweat=1.0, lag=0.3, lean=-0.18)
S.set(T_STEADY, "stand", "dead_stare", dur=0.25, ease="back", look=(0.6, 0.95), sweat=1.0, lean=0.04)
S.set(T_STEADY + 0.5, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), sweat=0.9)            # us. phew.
def windmill(tt, p):
    if not (T_LUNGE + 0.1 <= tt < T_STEADY): return p
    k = 1 - ramp(tt, T_STEADY - 0.3, T_STEADY)
    for hd, el, ph in (("lhand", "lelb", 0.0), ("rhand", "relb", math.pi)):
        sx, sy = p["neck"][0] + (-40 if hd == "lhand" else 40), p["neck"][1] + 40
        a = tt * 15 + ph
        p[hd] = lerp(p[hd], (sx + 300 * math.cos(a), sy + 300 * math.sin(a)), k)
        p[el] = lerp(p[el], (sx + 160 * math.cos(a + 0.3), sy + 160 * math.sin(a + 0.3)), k)
    return p
S.hook(windmill)
S.sfx(T_LUNGE, "skid", 0.05, dur=0.3); S.sfx(T_LUNGE + 0.1, "whoosh", 0.03, dur=1.6)
S.sfx(T_LAVA, "sploosh", 0.05); S.sfx(T_LAVA + 0.1, "simmer", 0.05, dur=1.2)
S.sfx(T_MELT, "poof", 0.08)
# rumble. lava rises. eyes go wide.
S.set(T_RUMBLE + 0.4, "stand", "dead_stare", dur=0.4, look=(0.75, 0.9), tilt=0.05, sweat=1.0)
S.set(T_RUMBLE + 0.9, "stand", "dead_stare", dur=0.8, look=(0.75, 0.9), tilt=0.05, sweat=1.0, eyescale=1.22, pupil=0.5, lid=0.0)
S.set(CUT_OUT - 0.4, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), sweat=1.0, eyescale=1.25, pupil=0.45, lid=0.0)   # us
S.sfx(T_RUMBLE, "kaboom", 0.08, dur=2.6)
for i in range(6): S.shake(T_RUMBLE + 0.3 * i, 0.35, 3 + 3 * i)
def melt_fx(cr, t, p, ly):
    if ly == "front" and T_MELT <= t < T_MELT + 0.6:
        u = (t - T_MELT) / 0.6
        L.sketch_circle(cr, XI + 216 + 260 * 1.1, LAVA_Y - 10, 60 + 160 * u, 0.1, sid=7710, fill=O.LAVA_B, alpha=1 - u)
        L.burst_lines(cr, XI + 216 + 260 * 1.1, LAVA_Y - 10, u, r0=80, r1=230, n=10, sid=7711)
S.prop(melt_fx)

# ================================================================ BOOM: the volcano fires him out
CAM_OUT = (VX - 200, -2600, 0.4)
S.flash(CUT_OUT, 0.5)
S.sfx(CUT_OUT, "kaboom", 0.5, dur=2.6); S.shake(CUT_OUT, 1.2, 30)
S.cut(CUT_OUT - 1 / 30, cam=CAM_OUT, x=VX - 540)
S.set(CUT_OUT - 1 / 30, "cannonball", "dead_stare", dur=0.0, lag=0.0, nowalk=1.0, eyescale=1.2, lid=0.0)
S.sfx(CUT_OUT + 0.2, "whoosh", 0.06)
def fired(tt, p):
    if not (CUT_OUT - 1 / 30 <= tt < CUT_EYE - 1 / 30): return p
    u = max(0.0, (tt - CUT_OUT - 0.05) / 1.5)
    tx = VX - 2000 * u ** 0.8; ty = VRIM[2] - 150 - 5600 * u ** 1.5; a = -3 * 2 * math.pi * u
    h = p["hip"]; c, s_ = math.cos(a), math.sin(a)
    for j in L.JOINTS:
        dx, dy = p[j][0] - h[0], p[j][1] - h[1]
        p[j] = (tx + dx * c - dy * s_, ty + dx * s_ + dy * c)
    p["tilt"] = p.get("tilt", 0.0) + a
    return p
S.hook(fired)
_re = random.Random(10)
ROCKS = [(_re.uniform(-0.6, 0.6), _re.uniform(2600, 5200), _re.uniform(60, 130), _re.uniform(0, 0.5)) for _ in range(16)]
def eruption(cr, t, p, ly):
    if not (CUT_OUT <= t < CUT_EYE): return
    s = t - CUT_OUT; cx, cy = VX, VRIM[2]
    if ly == "back":
        h = 9000 * smooth(min(1.0, s / 0.5)); w = 640 + 70 * math.sin(t * 13)
        pts = [(cx + 40 * math.sin(i * 0.9 + t * 8), cy + 40 - h * i / 24) for i in range(25)]
        O.draw_stream(cr, pts, w=w, color=O.LAVA, lumps=True); O.draw_stream(cr, pts, w=w * 0.45, color=O.LAVA_B, lumps=False)
        for i in range(10):
            a = (s * 0.5 + i / 10) % 1.0
            O.draw_smoke_puff(cr, cx + (i - 4.5) * 300 * (0.6 + a), cy + 150 - 900 * a, 260 + 420 * a, alpha=(1 - a) * 0.9, dark=0.7)
    else:
        for i, (dxk, sp, r, d) in enumerate(ROCKS):
            v = s - d
            if v <= 0: continue
            x = cx + dxk * sp * v * 1.2; y = cy - sp * v * math.cos(dxk) + 2600 * v * v
            if y > FLOOR_Y: continue
            O.draw_flames(cr, [(x - dxk * 40 * k, y + 60 * k) for k in range(6)], t + i, w=r * 0.9)
            L.sketch_circle(cr, x, y, r, 5, sid=7600 + i, fill=O.DL_ROCK)
        if s < 0.8: L.draw_impact(cr, cx, cy, min(1.0, s * 3), r=900, sid=76)
S.prop(eruption)

# ================================================================ the eye: shakes, bulges, BLOWS UP
S.cut(CUT_EYE - 1 / 30, cam=(EYE[0], EYE[1] + 250, 1.0))
S.camera(CUT_EYE, EYE[0], EYE[1] + 250, 1.12, T_POP - CUT_EYE, ease="linear")
S.camera(T_POP, EYE[0], EYE[1] + 400, 0.8, 0.4)
for i in range(5): S.shake(CUT_EYE + 0.2 * i, 0.3, 4 + 3 * i)
S.sfx(CUT_EYE, "whine", 0.05, dur=T_POP - CUT_EYE)
S.sfx(T_POP, "kaboom", 0.45, dur=2.6); S.shake(T_POP, 1.0, 34); S.flash(T_POP, 0.35, color=(1.0, 0.85, 0.5))
_rp = random.Random(21)
DEBRIS = [(_rp.uniform(-math.pi, 0), _rp.uniform(900, 2200), _rp.uniform(30, 80)) for _ in range(22)]
def eye_pop(cr, t, p, ly):
    if ly != "front" or not (T_POP <= t < CUT_T + 1.4): return
    s = t - T_POP; ex, ey = EYE
    if s < 1.0:
        for i in range(14):                                       # a ball of fire
            a = 2 * math.pi * i / 14
            r = 900 * smooth(min(1.0, s * 3))
            O.draw_flames(cr, [(ex + math.cos(a) * r * k / 5, ey + math.sin(a) * r * k / 5) for k in range(6)], t + i, w=170 * (1 - s))
        L.draw_impact(cr, ex, ey, min(1.0, s * 3), r=700, sid=77)
    for i, (a, sp, r) in enumerate(DEBRIS):                       # tower chunks raining down
        x = ex + math.cos(a) * sp * s; y = ey + math.sin(a) * sp * s + 1800 * s * s
        if y < FLOOR_Y - r: L.sketch_rect(cr, x - r, y - r, x + r, y + r, 4, sid=7820 + i, fill=(0.12, 0.10, 0.11))
    for i in range(6):
        a = (s * 0.6 + i / 6) % 1.0
        O.draw_smoke_puff(cr, ex + (i - 2.5) * 200, ey - 300 * a, 200 + 400 * a, alpha=(1 - a) * 0.8 * max(0, 1 - s / 2.4), dark=0.8)
S.prop(eye_pop)

# ================================================================ END: crash-lands in the rubble. the dud eye. the eagle shows up.
CAM_T = (XL + 250, 860, 0.62)
S.cut(CUT_T - 1 / 30, cam=CAM_T, x=SXL)
S.set(CUT_T - 1 / 30, "cannonball", "dead_stare", dur=0.0, lag=0.0, nowalk=1.0)
S.set(T_TLAND - 0.12, "sit_floor", "dead_stare", dur=0.12, lag=0.0, nowalk=1.0)
S.sfx(T_TLAND - 0.5, "slide_down", 0.06, dur=0.5)
def drop_t(tt, p):
    if not (CUT_T - 1 / 30 <= tt < T_TLAND): return p
    u = (tt - CUT_T) / (T_TLAND - CUT_T)
    dy = -2400 * (1 - max(0.0, u) ** 2)
    for j in L.JOINTS: p[j] = (p[j][0], p[j][1] + dy)
    return p
S.hook(drop_t)
S.set(T_TLAND, "sit_floor", "dead_stare", dur=0.06, ease="snap", stretch=-0.3, nowalk=1.0)
S.set(T_TLAND + 0.15, "sit_floor", "dead_stare", dur=0.3, ease="back", stretch=0.0, nowalk=1.0)
S.sfx(T_TLAND, "thud", 0.18); S.shake(T_TLAND, 0.4, 14)
CHUNK = (XL + 260, FLOOR_Y)
def chunk(cr, t, p, ly):
    if ly != "front" or t < T_CHUNK - 0.4: return
    u = min(1.0, (t - T_CHUNK + 0.4) / 0.4)
    y = lerp(-900, CHUNK[1] - 70, u * u)
    L.sketch_rect(cr, CHUNK[0] - 80, y - 70, CHUNK[0] + 80, y + 70, 5, sid=7830, fill=(0.12, 0.10, 0.11))
    if T_CHUNK <= t < T_CHUNK + 0.6: L.draw_poof(cr, CHUNK[0], FLOOR_Y - 30, (t - T_CHUNK) / 0.6, r=150, sid=33)
S.prop(chunk)
S.sfx(T_CHUNK, "thud", 0.14); S.shake(T_CHUNK, 0.3, 10)
S.set(T_CHUNK + 0.3, "sit_floor", "dead_stare", dur=0.2, look=(0.7, 0.5), nowalk=1.0)       # the chunk
S.set(T_CHUNK + 0.75, "sit_floor", "dead_stare", dur=0.2, look=(0.0, 0.0), nowalk=1.0)      # us
# the burnt-out eyeball rolls up and stops beside him
DUD = (XL + 520, FLOOR_Y - 150)
def dud(cr, t, p, ly):
    if ly != "front" or t < T_ROLL0: return
    u = smooth(ramp(t, T_ROLL0, T_ROLL1))
    x = lerp(XL + 1500, DUD[0], u); ang = -(x - DUD[0]) / 150 + 0.25 * math.exp(-max(0, t - T_ROLL1) * 4) * math.sin((t - T_ROLL1) * 14)
    y = DUD[1]
    L.sketch_circle(cr, x, y, 150, 6, sid=7840, fill=(0.62, 0.48, 0.30))
    cr.save(); cr.translate(x, y); cr.rotate(ang)
    cr.save(); cr.scale(0.22, 1.0); cr.arc(0, 0, 110, 0, 2 * math.pi); cr.restore(); cr.set_source_rgb(0.2, 0.15, 0.12); cr.fill()
    for q in ([(-120, -40), (-60, -10), (-30, 40)], [(60, -110), (90, -50), (130, -30)]):
        L.sketch_line(cr, q, 4, sid=7841)
    cr.restore()
    k = (t * 0.7) % 1.0
    O.draw_smoke_puff(cr, x + 30, y - 170 - 200 * k, 30 + 50 * k, alpha=0.6 * (1 - k), dark=0.6)
S.prop(dud)
for k in range(5): S.sfx(T_ROLL0 + 0.2 + k * 0.2, "tok", 0.015)
S.sfx(T_ROLL1 + 0.05, "thud", 0.06)
S.set(T_ROLL0 + 0.6, "sit_floor", "dead_stare", dur=0.3, look=(0.85, 0.3), nowalk=1.0)     # the eye. what's left.
S.set(T_ROLL1 + 0.7, "sit_floor", "dead_stare", dur=0.3, look=(0.0, 0.0), nowalk=1.0)      # us
S.blink(T_ROLL1 + 1.0)
S.sfx(T_EAGLE0, "whoosh", 0.06); S.sfx(T_EAGLE1, "thud", 0.06)
S.set(T_EAGLE1 + 0.4, "sit_floor", "dead_stare", dur=0.5, look=(-0.85, 0.0), nowalk=1.0)    # the eagle. NOW it shows up.
S.set(T_EAGLE1 + 1.6, "sit_floor", "dead_stare", dur=0.4, look=(0.0, 0.0), nowalk=1.0)     # us
S.blink(T_EAGLE1 + 2.0)
S.stand(T_STAND, face="dead_stare")
S.camera(T_STAND, XL + 150, 880, 0.66, 0.8)
S.t = T_ASK
S.the_ask(T_ASK, hold=ASK_HOLD, push=False)

# ================================================================ the ring prop
def ring(cr, t, p, ly):
    if t < T_PICK:
        if ly == "back":
            O.draw_ring(cr, RING0[0], RING0[1], t, r=44, flat=0.75)
            O.draw_sparkle(cr, RING0[0] - 30, RING0[1] - 20, (t % 1.6) / 0.5, r=40)
        return
    if ly != "front": return
    if t < CUT_IN:
        if CUT_E1 <= t < CUT_B1 or CUT_E2 <= t < CUT_B2: return
        hx, hy = p["lhand"]
        if t < T_GRAB: O.draw_ring(cr, hx - 6, hy - 50, t, r=40, spin=0.0); L.draw_grips(cr, p); return
        k = smooth(ramp(t, T_RINGON, T_INVIS - 0.05))          # slides from his wrist onto his mitt
        O.draw_ring(cr, hx - 8 * (1 - k), hy + 52 * (1 - k), t, r=lerp(36, 46, k), spin=0.0)
        if t >= T_INVIS: O.draw_sparkle(cr, hx + 30, hy - 30, ((t - T_INVIS) % 0.9) / 0.5, r=35)
        return
    if t < T_OFF:                                                 # (invisible) on his hand, falling in, landing
        hx, hy = p["rhand"]; O.draw_ring(cr, hx, hy, t, r=40, spin=0.0); return
    if t < T_DROP:
        hx, hy = p["rhand"]
        O.draw_ring(cr, hx + 6, hy - 50 if t < T_REACH + 0.15 else hy + 50, t, r=40, spin=0.0); L.draw_grips(cr, p); return
    if t < T_LAVA:
        s = t - T_DROP; O.draw_ring(cr, XI + 216, 955 + 0.5 * 2600 * s * s, t, r=40, spin=3.0); return
    if t < T_MELT:                                                # floats on the lava, sinking, glowing, melting
        s = t - T_LAVA; k = s / (T_MELT - T_LAVA)
        O.draw_ring(cr, XI + 216 + 260 * s, LAVA_Y - 30 + 30 * k, 0.0, r=40 * (1 - 0.4 * k), flat=0.6)
        O.draw_splash(cr, XI + 216, LAVA_Y, s / 0.6, color=O.LAVA, n=8, r=120, sid=7700)
        O.draw_smoke_puff(cr, XI + 216 + 260 * s, LAVA_Y - 80 - 160 * (s % 0.5), 30 + 40 * (s % 0.5), alpha=0.6, dark=0.4)
S.prop(ring)

# ---------------------------------------------------------------- HUD: the RINGS counter (the running gag)
def hud(cr, t):
    if t < T_PICK or t > T_ROLL1 + 1.5: return
    a = ramp(t, T_PICK, T_PICK + 0.2) * (1 - ramp(t, T_ROLL1 + 1.0, T_ROLL1 + 1.5))
    if t >= T_DROP: n, warn = 0, (0.5 + 0.5 * math.cos((t - T_DROP) * 12)) if t < T_DROP + 2.5 else 1.0
    else: n, warn = 1, 0.0
    O.draw_ring_hud(cr, n, y=1420, alpha=a, warn=warn)
S.overlays.insert(0, hud)

# ---------------------------------------------------------------- episode sounds (synth): chime, whistle, screech, ring loss
SR = L.SR
def _t(d): return np.arange(int(d * SR)) / SR
def fm_note(f, d, idx=1.2, ratio=3.0, decay=0.1):
    tt = _t(d); env = np.minimum(1, tt / 0.004) * np.exp(-tt / decay)
    return (np.sin(2 * np.pi * f * tt + idx * np.exp(-tt / 0.1) * np.sin(2 * np.pi * f * ratio * tt)) * env).astype(np.float32)
def place(buf, sig, t0, g):
    i = int(t0 * SR)
    if 0 <= i < len(buf): m = min(len(sig), len(buf) - i); buf[i:i + m] += sig[:m] * g
def chime(buf, t0):
    place(buf, fm_note(2637, 0.07, decay=0.05), t0, 0.5); place(buf, fm_note(3520, 0.35, decay=0.12), t0 + 0.055, 0.5)
def whistle_s(buf, t0):
    for k, d in ((0, 0.16), (0.24, 0.32)):
        tt = _t(d); f = 2300 + 180 * np.sin(2 * np.pi * 38 * tt)
        place(buf, (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, tt / 0.01) * np.minimum(1, (d - tt) / 0.02)).astype(np.float32), t0 + k, 0.35)
def screech(buf, t0, d=0.7):
    tt = _t(d); f = 2600 - 1300 * tt / d + 140 * np.sin(2 * np.pi * 23 * tt)
    nz = np.random.default_rng(5).standard_normal(len(tt)) * 0.25
    sig = (np.sin(2 * np.pi * np.cumsum(f) / SR) + nz) * np.minimum(1, tt / 0.03) * np.exp(-tt / (d * 0.6))
    place(buf, sig.astype(np.float32), t0, 0.35)
def scatter(buf, t0):
    rr = random.Random(4)
    for k in range(14):
        tk = t0 + 0.7 * (k / 14) ** 1.3
        place(buf, fm_note(rr.choice((2093, 2349, 2637, 3136, 3520)) * 2 ** (-0.6 * k / 14), 0.2, idx=1.5, decay=0.07), tk, 0.5 - 0.02 * k)
def extra(n):
    buf = np.zeros(n, np.float32)
    chime(buf, T_PICK)
    whistle_s(buf, T_BLOW + 0.15)
    screech(buf, T_SWOOP - 0.1); screech(buf, CUT_B2 + 0.1, 0.5); screech(buf, T_EAGLE0 + 0.2, 0.4)
    scatter(buf, T_DROP + 0.05)
    return buf * 0.12
_orig_soften = L._soften
def _soften_plus(x): return _orig_soften(x) + extra(len(x))
L._soften = _soften_plus

if __name__ == "__main__":
    print(f"lava {T_LAVA:.2f} melt {T_MELT:.2f} end {S.t:.2f}", file=sys.stderr)
    S.render("day010.mp4")
