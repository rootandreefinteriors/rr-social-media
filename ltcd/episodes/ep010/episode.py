"""Day 10 — COMMENT episode: @second_degree_burn "Pick up a ring and take it to mordor" (Instagram, day 9 reel, 0 likes).
RE-CUT on Justin's notes (2026-11-01): once he leaves a world he never goes back (he stays in Mordor); far faster
pacing, more tension, more in-jokes for fans of the ring story (parody: everything drawn by us, no characters).
The ring is his own gold green-hill ring (the RINGS counter is the running gag).

GRAB    Green hill, past the GOAL sign. Reads the comment. One ring left in the grass. Snatch. RINGS 1.
RUN     He runs right at speed-game speed, past a MORDOR sign into the dark land, skids to a stop at a giant black
        gate. The plank sign on it: ONE DOES NOT SIMPLY WALK INTO MORDOR. He reads it. Looks at us.
EAGLES  (the "why didn't they just use the eagles" joke) He digs at his hip, pulls out a whistle, tweets. A GIANT
        EAGLE swoops in, grabs him and hauls him over the wall.
SEARCH  Flying over the dark land. A searchlight beam from the giant eye sweeps the sky (cut: the eye, scanning).
        Heartbeat. The beam closes in... LOCKS ON. Cut: the eye narrows. The eagle sees it, looks at him, lets go
        and bolts. He hangs in mid-air one beat. Looks at us. Drops - straight into the volcano.
LAVA    Inside: he lands on the ledge over the lava. Holds the ring out. Heartbeat. Lets go. RINGS 0 (the game's
        ring-loss sound). His eye twitches. Speed-game reflex: he DIVES after it, snatches it off the lava -
        RINGS 1 - and a lava geyser fires him straight up and out of the volcano.
EYE     He crashes down on his butt at the foot of the eye's tower. The eye swings down onto him and flares.
        He looks at the eye. At the ring. At us. Puts the ring on - and vanishes (only the ring floats). The eye
        darts around, losing it. The ring tiptoes away. He takes it off - reappears right under the eye. It glares.
        He drops the ring at his feet. The ask, in Mordor, with the eye glaring over his shoulder (he lives here now).
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
XG = GATE_X - 500                          # where he skids to a stop, in front of the gate
SXG = XG - 540
TX, TH = 32600.0, 1330.0                   # the eye tower
EYE = (TX, FLOOR_Y - TH + 40)
VX, VH, VW = 34200.0, 3600.0, 3400.0       # the volcano
VRIM = O.volcano_rim(VX, VH)
SXI = 49460.0                              # inside the volcano (x 50000)
XI = 540 + SXI
EDGE = XI + 150
LAVA_Y = FLOOR_Y + 900
XL = TX - 850                              # he lands at the tower's foot
SXL = XL - 540
RING0 = (X0 - 150, FLOOR_Y - 16)

# ---------------------------------------------------------------- timeline
T_PICK = 2.85
T_RUN, T_RUN1 = 4.1, 7.5
T_PULL = 9.5
T_BLOW = 12.25
T_SWOOP, T_GRAB = 13.0, 13.5
CUT_FLY = 14.2
CUT_E1, CUT_B1 = 16.0, 16.8                # cut: the eye scanning
T_LOCK = 18.0
CUT_E2, CUT_B2 = 18.2, 19.0                # cut: the eye narrows
T_LETGO, T_FALL = 19.6, 20.1
CUT_IN = 20.9
T_ILAND = 21.4
T_REACH = 22.0
T_DROP = 24.0
T_LAVA = T_DROP + math.sqrt(2 * (LAVA_Y - 20 - 955) / 2600)
T_DIVE = 24.9
T_CATCH = 25.9
T_GEYSER = 26.0
CUT_OUT = 26.8
CUT_T = 28.4
T_TLAND = 29.0
T_SWIVEL = 29.4
T_ON, T_VANISH = 31.2, 31.7
T_BACK = 34.4
T_PUTDOWN = 35.3
T_ASK = 36.0

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
        k = 1 - smooth(ramp(t, 15.0, T_LOCK))                     # sweeps, closing in
        return (h[0] + 1500 * k * math.sin(t * 2.6), h[1] + 500 * k * math.cos(t * 1.9))
    return h

def eye_state(t):
    st = dict(look=0.6, look_y=0.0, lid=0.0, flare=1.0)
    if CUT_FLY <= t < CUT_IN:
        bt = beam_target(t)
        st.update(look=max(-1.0, min(1.0, (bt[0] - TX) / 1500)), look_y=-1.0)
        if CUT_E1 <= t < CUT_B1: st.update(look=math.sin((t - CUT_E1) * 7) * 0.8, lid=0.15)
        if t >= T_LOCK:
            st.update(look=0.0, lid=0.5 * smooth(ramp(t, CUT_E2 + 0.1, CUT_E2 + 0.5)), flare=lerp(1.0, 1.7, ramp(t, T_LOCK, CUT_E2 + 0.5)))
    elif t >= CUT_T:
        k = smooth(ramp(t, T_SWIVEL, T_SWIVEL + 0.3))
        hx = 540 + S.x if False else XL
        st.update(look=lerp(0.6, (XL - TX) / 1300, k), look_y=lerp(-0.6, 1.0, k), lid=0.3 * k, flare=1.0 + 0.5 * k)
        if T_VANISH <= t < T_BACK:                                # lost him: darts around, wide open
            st.update(look=0.9 * math.sin(t * 7.5), look_y=0.4 + 0.6 * math.sin(t * 5.1), lid=0.0, flare=1.3)
        if t >= T_BACK:
            k2 = smooth(ramp(t, T_BACK + 0.1, T_BACK + 0.3))
            st.update(look=lerp(0.5, (XL - 120 - TX) / 1300, k2), look_y=1.0, lid=0.0, flare=lerp(1.3, 1.9, k2))
            if t >= T_ASK + 9.0:                                  # ...eyes the ring on the ground
                st.update(look=lerp(st["look"], (XL + 10 - TX) / 1300, smooth(ramp(t, T_ASK + 9.0, T_ASK + 10.0))))
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

def world(cr, t):
    if CUT_IN <= t < CUT_OUT:
        rise = 0.0
        O.draw_lava_chamber(cr, t, EDGE, LAVA_Y, rise=rise)
        return
    if t < CUT_FLY:
        O.draw_green_hill_world(cr, t, x0=9800, x1=BORDER, palms=PALMS, flowers=FLOWERS)
        goal_sign(cr)
        O.draw_signpost(cr, SIGN_X, "MORDOR")
    es = eye_state(t)
    O.draw_dark_land_world(cr, t, x0=BORDER, x1=45000, volcano=(VX, VH, VW), gate=GATE_X,
                           tower=dict(x=TX, h=TH, **es))
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
    """(talon x, talon y, alarm, look) or None"""
    if t < T_SWOOP: return None
    if t < T_GRAB:
        u = smooth((t - T_SWOOP) / (T_GRAB - T_SWOOP))
        tgt = (XG, 1118 - 648)
        return (lerp(XG - 1500, tgt[0], u), lerp(-300, tgt[1], u) - 250 * math.sin(math.pi * u), 0.0, 0.0)
    if t < T_LETGO:
        h = hip_target(t)
        alarm = smooth(ramp(t, CUT_B2, CUT_B2 + 0.15))
        look = 0.0
        if CUT_B2 <= t: look = 1.0 if t < CUT_B2 + 0.35 else -0.2       # at the eye... at him
        return (h[0], h[1] - 648, alarm, look)
    s = t - T_LETGO
    return (P1[0] + 1600 * s, P1[1] - 648 - 1300 * s - 300 * s * s, 1.0, 1.0)
def eagle(cr, t, p, ly):
    if ly != "front": return
    st = eagle_state(t)
    if st is None or t >= CUT_IN: return
    x, y, alarm, look = st
    O.draw_eagle(cr, x, y, t, flap=1.0 if t > T_GRAB else 1.3, s=0.8, look=look, alarm=alarm)
    if T_LETGO <= t < T_LETGO + 1.2:                              # feathers everywhere
        rr = random.Random(7)
        for i in range(10):
            s = t - T_LETGO
            fx = P1[0] + rr.uniform(-300, 300) + rr.uniform(-200, 200) * s
            fy = P1[1] - 900 + rr.uniform(-200, 200) + 260 * s
            O.draw_eagle_feather(cr, fx, fy, t * 3 + i, sid=7500 + i)
S.prop(eagle)
S.sfx(T_SWOOP, "whoosh", 0.06)

# ================================================================ SEARCH: flight, beam, lock, drop
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
S.set(17.2, "hang", "dead_stare", dur=0.3, look=(0.0, 0.0), lag=0.0)                 # us
S.set(T_LOCK + 0.05, "hang", "dead_stare", dur=0.1, ease="snap", look=(0.6, 0.9), lag=0.0, eyescale=1.12)
S.set(CUT_B2 + 0.4, "hang", "dead_stare", dur=0.2, look=(0.5, -0.9), lag=0.0)       # up at the eagle
L.POSES["hang_alone"] = dict(L.POSES["hang"])
S.set(T_LETGO + 0.05, "hang_alone", "dead_stare", dur=0.15, look=(0.5, -0.9), lag=0.0, lhand_t="open", rhand_t="open")
S.set(T_LETGO + 0.25, "hang_alone", "dead_stare", dur=0.15, look=(0.0, 0.0), lag=0.0, lhand_t="open", rhand_t="open")   # us
S.set(T_FALL + 0.1, "hang_alone", "dead_stare", dur=0.2, look=(0.0, 0.6), lag=0.0, eyescale=1.15, lhand_t="open", rhand_t="open")
S.sfx(CUT_FLY, "wind", 0.04, dur=CUT_IN - CUT_FLY)
for k in range(10):                                               # heartbeat while the beam closes in
    tk = 15.2 + k * (0.42 - 0.02 * k)
    S.sfx(tk, "thud", 0.05 + 0.006 * k); S.sfx(tk + 0.16, "thud", 0.035 + 0.004 * k)
S.sfx(T_LOCK, "kaboom", 0.09, dur=2.0)
S.sfx(T_FALL, "slide_down", 0.07, dur=0.8)
def beam(cr, t, p, ly):
    if ly != "back" or not (15.0 <= t < CUT_IN): return
    if CUT_E1 <= t < CUT_B1 or CUT_E2 <= t < CUT_B2:
        bt = beam_target(t); O.draw_beam(cr, (EYE[0], EYE[1] - 40), (EYE[0] + (bt[0] - EYE[0]) * 0.3, EYE[1] - 1500), width=500,
                                         alpha=ramp(t, 15.0, 15.4), locked=float(t >= T_LOCK)); return
    bt = beam_target(t)
    O.draw_beam(cr, (EYE[0], EYE[1]), bt, width=620, alpha=ramp(t, 15.0, 15.4), locked=smooth(ramp(t, T_LOCK, T_LOCK + 0.2)))
S.prop(beam)

# ================================================================ LAVA: inside the volcano
CAM_IN = (EDGE + 100, 1500, 0.6)
S.cut(CUT_IN - 1 / 30, cam=CAM_IN, x=SXI)
S.set(CUT_IN - 1 / 30, "cannonball", "dead_stare", dur=0.0, lag=0.0, nowalk=1.0)
def drop_in(tt, p):
    if not (CUT_IN - 1 / 30 <= tt < T_ILAND): return p
    u = (tt - CUT_IN) / (T_ILAND - CUT_IN)
    dy = -2300 * (1 - max(0.0, u) ** 2)
    for j in L.JOINTS: p[j] = (p[j][0], p[j][1] + dy)
    return p
S.hook(drop_in)
S.set(T_ILAND - 0.05, "crouch", "dead_stare", dur=0.05, ease="snap", stretch=-0.3, lag=0.0, nowalk=1.0)
S.set(T_ILAND + 0.25, "stand", "dead_stare", dur=0.25, ease="back", lag=0.6, sweat=0.7)
S.sfx(T_ILAND, "thud", 0.18); S.shake(T_ILAND, 0.35, 14)
L.POSES["hold_ring_r"] = dict(relb=(650, 930), rhand=(690, 830), rhand_t="grip")
L.POSES["reach_r"] = dict(relb=(668, 935), rhand=(752, 905), rhand_t="grip")
S.set(T_ILAND + 0.5, "hold_ring_r", "dead_stare", dur=0.25, look=(0.7, 0.9), sweat=0.7)      # the lava
S.set(T_REACH, "reach_r", "dead_stare", dur=0.3, look=(0.8, 0.35), sweat=0.8)
S.set(T_REACH + 1.0, "reach_r", "dead_stare", dur=0.3, look=(0.0, 0.0), sweat=0.85)          # us
S.set(T_DROP, "reach_r", "dead_stare", dur=0.06, ease="snap", rhand_t="open", sweat=0.9)
S.set(T_DROP + 0.2, "reach_r", "dead_stare", dur=0.25, look=(0.8, 0.95), tilt=0.08, rhand_t="open", sweat=0.9)
S.set(T_DROP + 0.5, "stand", "dead_stare", dur=0.3, look=(0.8, 0.95), tilt=0.08, sweat=0.9, twitch=1.0)
S.set(T_DIVE - 0.12, "crouch", "dead_stare", dur=0.1, look=(0.8, 0.95), sweat=0.9, lag=0.0, nowalk=1.0)
S.set(T_DIVE, "cannonball", "dead_stare", dur=0.08, ease="snap", look=(0.6, 0.9), lag=0.0, nowalk=1.0, lid=0.0)
L.POSES["grab_down"] = dict(L.POSES["cannonball"]); L.POSES["grab_down"].update(relb=(620, 1200), rhand=(660, 1330), rhand_t="grip")
S.set(T_CATCH - 0.15, "grab_down", "dead_stare", dur=0.12, look=(0.4, 0.9), lag=0.0, nowalk=1.0)
S.set(T_GEYSER + 0.05, "cannonball", "dead_stare", dur=0.08, look=(0.0, 0.0), lag=0.0, nowalk=1.0, eyescale=1.2, lid=0.0)
for k in range(5):
    tk = T_REACH + 0.2 + k * 0.4; S.sfx(tk, "thud", 0.05); S.sfx(tk + 0.15, "thud", 0.035)
DIVE_END = (EDGE + 470, LAVA_Y - 300)
def dive(tt, p):
    if not (T_DIVE <= tt < CUT_OUT): return p
    h0 = (XI, 1118)
    if tt < T_CATCH:
        u = (tt - T_DIVE) / (T_CATCH - T_DIVE)
        tx, ty = lerp(h0[0], DIVE_END[0], 1 - (1 - u) ** 2.5), lerp(h0[1], DIVE_END[1], u * u) - 260 * math.sin(math.pi * u) * (1 - u)
        a = -2 * math.pi * smooth(u)
    elif tt < T_GEYSER:
        tx, ty, a = DIVE_END[0], DIVE_END[1], 0.0
    else:
        s = tt - T_GEYSER
        tx, ty, a = DIVE_END[0], DIVE_END[1] - 3800 * s * s - 400 * s, 0.0
    h = p["hip"]; c, s_ = math.cos(a), math.sin(a)
    for j in L.JOINTS:
        dx, dy = p[j][0] - h[0], p[j][1] - h[1]
        p[j] = (tx + dx * c - dy * s_, ty + dx * s_ + dy * c)
    p["tilt"] = p.get("tilt", 0.0) + a
    return p
S.hook(dive)
S.sfx(T_DIVE, "whoosh", 0.06)
S.sfx(T_LAVA, "sploosh", 0.05); S.sfx(T_LAVA + 0.1, "simmer", 0.04, dur=1.0)
S.sfx(T_GEYSER, "kaboom", 0.4, dur=2.6); S.shake(T_GEYSER, 0.8, 26)
S.camera(T_DIVE, EDGE + 160, 1650, 0.6, T_CATCH - T_DIVE)
def geyser(cr, t, p, ly):
    if ly != "back" or not (T_GEYSER - 0.15 <= t < CUT_OUT): return
    s = t - T_GEYSER
    if s < 0:                                                    # the lava bulges under him
        L.sketch_ellipse(cr, DIVE_END[0], LAVA_Y, 200 * (1 + s / 0.15), 60, 5, sid=7650, fill=O.LAVA_B); return
    top = LAVA_Y - 6000 * min(1.0, s / 0.5)
    pts = [(DIVE_END[0] + 30 * math.sin(i + t * 9), LAVA_Y + 40 - (LAVA_Y + 40 - top) * i / 20) for i in range(21)]
    O.draw_stream(cr, pts, w=330, color=O.LAVA, lumps=True); O.draw_stream(cr, pts, w=150, color=O.LAVA_B, lumps=False)
S.prop(geyser)

# ================================================================ BOOM: the volcano fires him out
CAM_OUT = (VX - 200, -2600, 0.4)
S.flash(CUT_OUT, 0.5)
S.sfx(CUT_OUT, "kaboom", 0.5, dur=2.6); S.shake(CUT_OUT, 1.2, 30)
S.cut(CUT_OUT - 1 / 30, cam=CAM_OUT, x=VX - 540)
S.set(CUT_OUT - 1 / 30, "cannonball", "dead_stare", dur=0.0, lag=0.0, nowalk=1.0, eyescale=1.2, lid=0.0)
S.sfx(CUT_OUT + 0.2, "whoosh", 0.06)
def fired(tt, p):
    if not (CUT_OUT - 1 / 30 <= tt < CUT_T - 1 / 30): return p
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
    if not (CUT_OUT <= t < CUT_T): return
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

# ================================================================ EYE: crash at the tower's foot. vanish. reappear. the ask.
CAM_T = (TX - 450, 850, 0.62)
S.cut(CUT_T - 1 / 30, cam=CAM_T, x=SXL)
S.set(CUT_T - 1 / 30, "cannonball", "dead_stare", dur=0.0, lag=0.0, nowalk=1.0)
S.set(T_TLAND - 0.12, "sit_floor", "dead_stare", dur=0.12, lag=0.0, nowalk=1.0)
S.sfx(T_TLAND - 0.55, "slide_down", 0.06, dur=0.55)
def drop_t(tt, p):
    if not (CUT_T - 1 / 30 <= tt < T_TLAND): return p
    u = (tt - CUT_T) / (T_TLAND - CUT_T)
    dy = -2400 * (1 - max(0.0, u) ** 2)
    for j in L.JOINTS: p[j] = (p[j][0], p[j][1] + dy)
    return p
S.hook(drop_t)
L.POSES["sit_ring"] = dict(L.POSES["sit_floor"]); L.POSES["sit_ring"].update(relb=(640, 1180), rhand=(700, 1090), rhand_t="grip")
S.set(T_TLAND, "sit_ring", "dead_stare", dur=0.06, ease="snap", stretch=-0.3, nowalk=1.0)
S.set(T_TLAND + 0.15, "sit_ring", "dead_stare", dur=0.3, ease="back", stretch=0.0, nowalk=1.0)
S.sfx(T_TLAND, "thud", 0.18); S.shake(T_TLAND, 0.4, 14)
def land_fx(cr, t, p, ly):
    if ly == "front" and T_TLAND <= t < T_TLAND + 0.7: L.draw_poof(cr, XL, FLOOR_Y - 40, (t - T_TLAND) / 0.7, r=200, sid=32)
S.prop(land_fx)
S.sfx(T_SWIVEL, "kaboom", 0.08, dur=2.0); S.shake(T_SWIVEL + 0.1, 0.5, 6)
S.set(T_SWIVEL + 0.35, "sit_ring", "dead_stare", dur=0.25, look=(0.8, -0.9), tilt=-0.1, nowalk=1.0)    # up at the eye
S.set(30.4, "sit_ring", "dead_stare", dur=0.25, look=(0.8, 0.1), tilt=0.05, nowalk=1.0)               # the ring
S.set(30.85, "sit_ring", "dead_stare", dur=0.25, look=(0.0, 0.0), tilt=0.0, nowalk=1.0)               # us
L.POSES["ring_on"] = dict(L.POSES["sit_floor"]); L.POSES["ring_on"].update(relb=(640, 1180), rhand=(690, 1100), rhand_t="mitt",
                                                                           lelb=(560, 1200), lhand=(640, 1110), lhand_t="grip")
S.set(T_ON, "ring_on", "dead_stare", dur=0.2, look=(0.7, 0.3), nowalk=1.0)
S.set(T_VANISH, "ring_on", "dead_stare", dur=0.0, show=0.0, nowalk=1.0)
S.sfx(T_VANISH, "twinkle", 0.08)
L.POSES["sneak_r"] = dict(relb=(640, 1000), rhand=(660, 1080), rhand_t="mitt")
S.set(32.2, "sneak_r", "dead_stare", dur=0.3, show=0.0)                         # (invisible) stands up...
S.xkeys.append((32.9, SXL - 120, 1.2, "smooth")); S.x = SXL - 120                # ...and tiptoes away
S.set(32.9, "sneak_r", "dead_stare", dur=0.2, show=0.0, tiptoe=1.0)
S.set(T_BACK, "hold_ring_r", "dead_stare", dur=0.0, show=1.0, look=(0.0, 0.0))  # takes it off: right there
S.sfx(T_BACK, "pop", 0.08)
S.set(T_BACK + 0.45, "hold_ring_r", "dead_stare", dur=0.2, look=(0.8, -0.9), tilt=-0.1)              # the eye. glaring.
S.set(T_BACK + 0.9, "hold_ring_r", "dead_stare", dur=0.25, look=(0.0, 0.0), tilt=0.0)                # us
S.set(T_PUTDOWN, "stand", "dead_stare", dur=0.15)
S.sfx(T_PUTDOWN + 0.35, "tok", 0.03)
S.blink(T_PUTDOWN + 0.4)
S.t = T_ASK
S.the_ask(T_ASK, hold=7.0, push=False)
S.camera(T_PUTDOWN, TX - 550, 840, 0.66, 0.8)

# ================================================================ the ring prop, start to finish
RING_END = (XL - 120 + 130, FLOOR_Y - 16)
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
        if t < T_GRAB: O.draw_ring(cr, hx - 6, hy - 50, t, r=40, spin=0.0)
        else: O.draw_ring(cr, hx - 8, hy + 52, t, r=36, spin=0.0)            # hanging off his wrist
        L.draw_grips(cr, p); return
    if t < T_DROP:
        if t < T_ILAND + 0.2: return
        hx, hy = p["rhand"]
        O.draw_ring(cr, hx + 6, hy - 50 if t < T_REACH + 0.15 else hy + 50, t, r=40, spin=0.0); L.draw_grips(cr, p); return
    if t < T_LAVA:
        s = t - T_DROP; O.draw_ring(cr, XI + 216, 955 + 0.5 * 2600 * s * s, t, r=40, spin=3.0); return
    if t < T_CATCH:                                               # floats on the lava, sinking, sizzling
        s = t - T_LAVA
        O.draw_ring(cr, XI + 216 + 260 * s, LAVA_Y - 30 + 22 * s, 0.0, r=40, flat=0.6)
        O.draw_splash(cr, XI + 216, LAVA_Y, s / 0.6, color=O.LAVA, n=8, r=120, sid=7700)
        O.draw_smoke_puff(cr, XI + 216, LAVA_Y - 80 - 160 * (s % 0.5), 30 + 40 * (s % 0.5), alpha=0.6, dark=0.4); return
    if t < CUT_T:
        hx, hy = p["rhand"]; O.draw_ring(cr, hx + 4, hy - 46, t, r=36, spin=0.0); return
    if t < T_ON:
        hx, hy = p["rhand"]; O.draw_ring(cr, hx + 6, hy - 50, t, r=40, spin=0.0); L.draw_grips(cr, p); return
    if t < T_BACK:                                                # slid onto his mitt (around it); then floats alone
        hx, hy = p["rhand"]; k = smooth(ramp(t, T_ON, T_VANISH - 0.1))
        O.draw_ring(cr, hx, hy - 50 * (1 - k), t, r=lerp(40, 30, k), spin=0.0)
        if t >= T_VANISH: O.draw_sparkle(cr, hx + 30, hy - 30, ((t - T_VANISH) % 0.9) / 0.5, r=35)
        return
    if t < T_PUTDOWN + 0.35:
        hx, hy = p["rhand"]
        if t < T_PUTDOWN: O.draw_ring(cr, hx + 6, hy - 50, t, r=40, spin=0.0); L.draw_grips(cr, p); return
        u = (t - T_PUTDOWN) / 0.35
        O.draw_ring(cr, lerp(hx, RING_END[0], u), lerp(hy, RING_END[1], u * u), t, r=40, spin=4.0); return
    O.draw_ring(cr, RING_END[0], RING_END[1], 0.0, r=44, flat=0.75 * (1 - math.exp(-(t - T_PUTDOWN - 0.35) * 5)))
S.prop(ring)
def vanish_fx(cr, t, p, ly):
    if ly == "front":
        if T_VANISH <= t < T_VANISH + 0.6: L.burst_lines(cr, p["hip"][0], p["hip"][1] - 200, (t - T_VANISH) / 0.6, r0=120, r1=300, n=10, sid=81)
        if T_BACK <= t < T_BACK + 0.5: L.burst_lines(cr, p["hip"][0], p["hip"][1] - 200, (t - T_BACK) / 0.5, r0=200, r1=360, n=10, sid=82)
S.prop(vanish_fx)

# ---------------------------------------------------------------- HUD: the RINGS counter (the running gag)
def hud(cr, t):
    if t < T_PICK or t > T_PUTDOWN + 0.8: return
    a = ramp(t, T_PICK, T_PICK + 0.2) * (1 - ramp(t, T_PUTDOWN + 0.3, T_PUTDOWN + 0.8))
    if T_DROP <= t < T_CATCH: n, warn = 0, (0.5 + 0.5 * math.cos((t - T_DROP) * 12))
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
    chime(buf, T_PICK); chime(buf, T_CATCH)
    whistle_s(buf, T_BLOW + 0.15)
    screech(buf, T_SWOOP - 0.1); screech(buf, CUT_B2 + 0.1, 0.5)
    scatter(buf, T_DROP + 0.05)
    return buf * 0.12
_orig_soften = L._soften
def _soften_plus(x): return _orig_soften(x) + extra(len(x))
L._soften = _soften_plus

if __name__ == "__main__":
    print(f"lava {T_LAVA:.2f} end {S.t:.2f}", file=sys.stderr)
    S.render("day010.mp4")
