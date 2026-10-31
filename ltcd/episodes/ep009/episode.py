"""Day 9 — COMMENT episode: @nicolascechettoschuller "Go to green hill" (Instagram, day 8 reel, 1 like).
A GENERIC green-hill speed-game world (checkered brown dirt, grass, palm trees, sunflowers, sparkling water, gold rings,
a giant loop): no hedgehog, no characters, no logo or game name on screen (same call as the day 4 block game).

SHOT 1  The airfield, next to the planted plane and the puke puddle (where day 8 left him). Reads the comment. Stares.
WALK    He walks right, past the plane, past a GREEN HILL arrow sign, into the green hill: checkered dirt, palm trees,
        sunflowers, water sparkling behind.
RING    A gold ring floats in front of him. He looks at it. At us. Takes it. RINGS 1. Walks to the next one. RINGS 2.
        He looks at us. There's a whole line of them.
RUN     He goes for them: walking, then jogging, then running, faster and faster, the counter climbing; legs go to a
        cartoon blur wheel; a GIANT loop - he runs all the way round it; out of it even faster; RINGS 999; he outruns
        the camera and is gone. Dust settles. Empty hill.
GOAL    RE-CUT on Justin's notes (2026-10-31): he blasts past the end-of-level sign and skids to a stop; the sign
        spins and lands on his face. Level done: he strikes the victory stance (hand on hip, peace sign up), dead
        stare. HE HAS PASSED. He holds it. The most harmless little ladybug robot putters up, very slowly. It pokes his
        shin. Every one of his 999 rings bursts out of him. RINGS 0. He holds the stance through all of it.
END     Lowers the peace sign. Looks at the bug. It leaves. The ask, there, past the goal (where he lives now).
MUSIC   Original chiptune in the 90s speed-game style (written for this episode, not a copy of any game's music):
        kicks in as he crosses into the green hill, cuts out at the goal; a short original victory jingle; game-style
        ring chimes and the ring-scatter jingle.
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y
from ink import smooth

# ---------------------------------------------------------------- places
XI, YI = 9000.0, FLOOR_Y - 425.0          # the planted plane (day 8)
PUKE_X = 7470.0
SIGN_X = 9480.0
GX = 9800.0                               # the airfield ends, the green hill starts
SX0 = 7210.0                              # his body offset at the start (x 7750)
SXA = 10060.0                             # after the walk (x 10600)
SXB = 10560.0                             # at ring 2 (x 11100); the run starts here
R = 900.0                                 # loop radius (running surface)
PALMS = [(10150, 760), (12350, 880), (14100, 720), (18900, 860), (20600, 760), (23500, 900), (26800, 780),
         (30000, 860), (33400, 820), (36900, 880), (40500, 780)]
FLOWERS = [10350, 11650, 12900, 13650, 14800, 15400, 18400, 19700, 21300, 22400, 24600, 25900, 27800, 29300,
           31500, 34800, 38200, 41700]

# ---------------------------------------------------------------- timeline
T_WALK, T_ARR = 4.0, 10.5
T_REACH, T_GET1 = 12.0, 12.3
T_W2, T_GET2 = 13.8, 14.75
T_R = 16.4                                # the run starts
def s_of(u): return 350 * u + 20 * u ** 3 if u > 0 else 0.0
def v_of(u): return 350 + 60 * u * u if u > 0 else 0.0
def u_of_s(s):
    a, b = 0.0, 20.0
    for _ in range(60):
        m = (a + b) / 2
        if s_of(m) < s: a = m
        else: b = m
    return (a + b) / 2
U_BLUR = math.sqrt((1600 - 350) / 60)      # legs go to a blur wheel above 1600 px/s
S_L = s_of(5.5)                            # loop entry
LX = 540 + SXB + S_L                       # loop bottom contact x
LCY = FLOOR_Y - R
CIRC = 2 * math.pi * R
U_L0, U_L1 = 5.5, u_of_s(S_L + CIRC)
T_L0, T_L1 = T_R + U_L0, T_R + U_L1
T_BLUR = T_R + U_BLUR
T_DEC = T_L1 + 1.4                        # brakes
D_DEC = 0.5
T_STOP = T_DEC + D_DEC

def contact(t):
    """(x, theta) of the point under his feet during the run; theta = loop angle (0 = on flat ground)."""
    u = t - T_R; s = s_of(u)
    if s < S_L: return 540 + SXB + s, 0.0
    if s < S_L + CIRC: return LX, (s - S_L) / R
    if t < T_DEC: return LX + (s - S_L - CIRC), 0.0
    xd = LX + s_of(T_DEC - T_R) - S_L - CIRC; vd = v_of(T_DEC - T_R); tau = min(t - T_DEC, D_DEC)
    return xd + vd * tau - vd * tau * tau / (2 * D_DEC), 0.0          # skids to a stop
def run_offset(t):
    x, th = contact(t); return x - 540
def loop_pt(th, d=0.0):
    """point at loop angle th, d px in from the running surface towards the centre."""
    return (LX + (R - d) * math.sin(th), LCY + (R - d) * math.cos(th))

S = M.Scene(x0=SX0)
S.auto_blinks = False
S.card("nicolascechettoschuller", "Go to green hill", "1", t0=0.35)
CAM0 = (540 + SX0 + 40, 930, 1.12)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0
S.sfx(0.35, "tick", 0.04)

# ================================================================ worlds
def world(cr, t):
    if True:
        O.draw_airfield_world(cr, t, x0=1300, x1=GX, sign_x=2230, sock_x=4300, hangar_x=1950)
        O.draw_green_hill_world(cr, t, x0=GX, x1=60000, loop=(LX, R), palms=PALMS, flowers=FLOWERS)
        O.draw_signpost(cr, SIGN_X, "GREEN HILL")
        # day 8 leftovers: the planted plane, its dirt mound, a little smoke; the puke puddle
        cr.save(); cr.rectangle(XI - 2000, -5000, 4000, 5000 + FLOOR_Y + 12); cr.clip()      # nose buried in the ground
        O.draw_plane(cr, XI, YI, math.pi / 2, t, part="back")
        O.draw_plane(cr, XI, YI, math.pi / 2, t, part="front", prop=0.0, wheel=False)
        cr.restore()
        L.sketch_ellipse(cr, XI, FLOOR_Y + 10, 260, 50, 6, sid=5320, fill=(0.50, 0.37, 0.24))
        for k in range(4):
            a = (t * 0.4 + k / 4) % 1.0
            O.draw_smoke_puff(cr, XI - 30 + 50 * a, FLOOR_Y - 140 - 520 * a, 45 + 80 * a, alpha=(1 - a) * 0.45, dark=0.5)
        O.draw_puke(cr, PUKE_X, FLOOR_Y - 18, 75, t, 0.0, squash=0.85)
S.background(world)

# ================================================================ SHOT 1: the airfield. reads it. stares.
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(0.6, react="dead_stare", lines=1, face="deadpan")
S.set(2.9, "stand", "dead_stare", dur=0.3, lid=1.0)                         # slow blink
S.set(3.35, "stand", "dead_stare", dur=0.4)

# ================================================================ WALK right, past the plane, into the green hill
S.xkeys.append((T_WALK, SXA, T_ARR - T_WALK, "smooth")); S.x = SXA
def walk_x(t): return 540 + lerp(SX0, SXA, smooth(ramp(t, T_WALK, T_ARR, "linear")))
S.set(T_WALK, "stand", "dead_stare", dur=0.3, look=(0.7, 0.0))
_ct = T_WALK
while _ct < T_ARR + 0.5:
    x = walk_x(_ct + 0.25)
    z = lerp(1.12, 0.8, smooth(ramp(_ct, T_WALK, T_WALK + 1.5))); z = lerp(z, 0.85, smooth(ramp(_ct, T_ARR - 1.5, T_ARR)))
    S.camera(_ct, x + 60, lerp(930, 900, ramp(_ct, T_WALK, T_WALK + 1.5)), z, dur=0.1, ease="linear")
    _ct += 0.1

# ================================================================ RING 1, RING 2
R1 = (540 + SXA + 210, 905.0)
R2 = (540 + SXB, 950.0)
L.POSES["reach_r"] = dict(relb=(665, 930), rhand=(752, 905), rhand_t="open")
S.set(T_ARR + 0.3, "stand", "dead_stare", dur=0.35, look=(0.8, 0.3))       # the ring
S.set(T_ARR + 1.0, "stand", "dead_stare", dur=0.35, look=(0.8, 0.3), tilt=0.05)
S.set(T_ARR + 1.5, "stand", "dead_stare", dur=0.35, look=(0.0, 0.0), tilt=0.0)   # us
S.blink(T_ARR + 1.2)
S.set(T_REACH, "reach_r", "dead_stare", dur=0.3, look=(0.8, 0.3))
S.set(T_GET1 + 0.35, "stand", "dead_stare", dur=0.4, look=(0.8, 0.3))
S.set(T_GET1 + 0.9, "stand", "dead_stare", dur=0.35, look=(0.0, 0.0))     # us. RINGS 1.
S.xkeys.append((T_W2, SXB, T_GET2 - T_W2 + 0.1, "smooth")); S.x = SXB
S.set(T_W2, "stand", "dead_stare", dur=0.3, look=(0.7, 0.2))
S.set(T_GET2 + 0.45, "stand", "dead_stare", dur=0.35, look=(0.0, 0.0))     # us. RINGS 2.
S.blink(T_GET2 + 1.0)
S.set(T_R - 0.7, "stand", "dead_stare", dur=0.4, look=(0.95, 0.1))       # the line of rings
S.camera(T_ARR, 540 + SXA + 160, 900, 0.85, 1.0)
S.camera(T_W2, 540 + SXB + 140, 900, 0.85, 1.2)

# ================================================================ THE RUN
X_STOP = contact(T_STOP)[0]
SX_STOP = X_STOP - 540
GOALX = X_STOP - 650
def _pass_time():
    a, b = T_L1, T_STOP
    for _ in range(50):
        m = (a + b) / 2
        if contact(m)[0] < GOALX: a = m
        else: b = m
    return (a + b) / 2
T_PASS = _pass_time()
PALMS[:] = [pp for pp in PALMS if abs(pp[0] - X_STOP) > 1100 and abs(pp[0] - GOALX) > 500]
T_SIGN = T_PASS + 2.6                     # the sign stops spinning
T_POSE = T_STOP + 3.3                     # victory stance
T_BUG0 = T_POSE + 2.4                     # the bug sets off
T_BUG1 = T_BUG0 + 4.0                     # ... arrives at his foot
T_POKE = T_BUG1 + 0.8
T_DOWN = T_POKE + 3.0
T_BUGOFF = T_DOWN + 1.0
T_US = T_DOWN + 1.8
T_ASK = T_US + 1.0

_t = T_R
while _t < T_STOP + 0.1:
    S.xkeys.append((_t, run_offset(_t), 1 / 30, "linear")); _t += 1 / 30
S.x = SX_STOP
S.set(T_R, "stand", "deadpan", dur=0.4, lag=0.3)
S.set(T_R + 1.5, "stand", "deadpan", dur=1.5, run=1.0, lag=0.1)
S.set(T_BLUR - 0.3, "stand", "deadpan", dur=0.3, run=1.0, lid=0.35, lag=0.0)
S.set(T_BLUR, "stand", "deadpan", dur=0.0, lid=0.45, curl=-0.8, lag=0.0, nowalk=1.0)
S.sfx(T_BLUR, "whoosh", 0.05)
S.sfx(T_BLUR + 0.1, "wind", 0.03, dur=T_DEC - T_BLUR)
S.sfx(T_L0, "whoosh", 0.05); S.sfx(T_L1, "whoosh", 0.05)

# skid: leaning back, heels dug in, arms out
L.POSES["skid"] = dict(hip=(500, 1130), neck=(470, 790), head=(455, 665), lelb=(380, 860), lhand=(300, 800), relb=(560, 880),
                       rhand=(640, 820), lhand_t="open", rhand_t="open", lknee=(560, 1290), lfoot=(650, FLOOR_Y),
                       rknee=(620, 1300), rfoot=(720, FLOOR_Y), lfoot_dir=0.9, rfoot_dir=0.9, nowalk=1.0)
S.set(T_DEC, "skid", "deadpan", dur=0.1, lag=0.0, lid=0.3, curl=-0.5)
S.sfx(T_DEC, "skid", 0.08, dur=D_DEC + 0.1)
S.set(T_STOP, "stand", "deadpan", dur=0.35, ease="back", lag=0.0, nowalk=1.0)
S.set(T_STOP + 0.6, "stand", "deadpan", dur=0.4, lag=1.0, nowalk=1.0)
S.set(T_STOP + 0.9, "stand", "dead_stare", dur=0.4, look=(-0.9, -0.2), tilt=-0.05)          # the spinning sign
S.set(T_SIGN + 0.4, "stand", "dead_stare", dur=0.4, look=(-0.9, -0.2), tilt=-0.08)          # ...his own face on it
S.set(T_SIGN + 1.0, "stand", "dead_stare", dur=0.4, look=(0.0, 0.0), tilt=0.0)              # us
S.blink(T_SIGN + 0.7)

def blur_hook(tt, p):
    if not (T_BLUR <= tt < T_DEC): return p
    h = p["hip"]
    p["lknee"] = (h[0] + 30, h[1] + 170); p["rknee"] = (h[0] + 70, h[1] + 160)
    p["lfoot"] = (h[0] + 10, h[1] + 330); p["rfoot"] = (h[0] + 110, h[1] + 310)
    n = p["neck"]                                                     # arms streaming straight back
    p["lelb"] = (n[0] - 150, n[1] + 120); p["lhand"] = (n[0] - 300, n[1] + 170)
    p["relb"] = (n[0] - 140, n[1] + 150); p["rhand"] = (n[0] - 290, n[1] + 220)
    p["lhand_t"] = p["rhand_t"] = "open"
    for k in ("head", "neck"): p[k] = (p[k][0] + 50, p[k][1] + 10)  # leaning into it
    return p
def loop_hook(tt, p):
    if not (T_L0 <= tt < T_L1): return p
    x, th = contact(tt)
    if th == 0.0: return p
    cx, cy = loop_pt(th)
    a = -th
    px, py = p["hip"][0], FLOOR_Y
    c, s_ = math.cos(a), math.sin(a)
    for j in L.JOINTS:
        dx, dy = p[j][0] - px, p[j][1] - py
        p[j] = (cx + dx * c - dy * s_, cy + dx * s_ + dy * c)
    p["tilt"] = p.get("tilt", 0.0) + a
    return p
S.hook(blur_hook); S.hook(loop_hook)

def run_fx(cr, t, p, ly):
    if not (T_BLUR <= t < T_DEC) or ly != "back": return
    x, th = contact(t)
    a = -th
    h = p["hip"]; c, s_ = math.cos(a), math.sin(a)
    def rot(dx, dy): return (h[0] + dx * c - dy * s_, h[1] + dx * s_ + dy * c)
    wc = rot(60, 230)                                                 # the blur wheel where his legs were
    for k in range(3):
        L.sketch_ellipse(cr, wc[0], wc[1], 150 - 25 * k, 120 - 18 * k, 6, rot=a + 0.5 * k + t * 9, sid=7100 + k, fill=None, alpha=0.9)
    for k, dy in enumerate((-430, -250, -60, 120)):                   # speed lines streaming behind him
        q = rot(-240, dy)
        L.motion_lines(cr, q[0], q[1], math.pi + a, n=1, length=420 + 120 * (k % 2), alpha=0.8, sid=7110 + k, width=6)
S.prop(run_fx)

# ---------------------------------------------------------------- the rings on his path
RINGS = []                                                            # (s on the path, (x, y))
for k in range(1, 40):
    x = R2[0] + 260 * k
    if x > LX - 200: break
    RINGS.append((x - 540 - SXB, (x, 950.0)))
for k in range(1, 8):
    th = k * 2 * math.pi / 8
    RINGS.append((S_L + th * R, loop_pt(th, 530)))
for k in range(1, 60):
    x = LX + 300 + 330 * k
    if x > GOALX - 900: break
    RINGS.append((S_L + CIRC + (x - LX), (x, 950.0)))
RING_T = [(T_R + u_of_s(s), xy) for s, xy in RINGS]
def ring_count(t):
    n = (t >= T_GET1) + (t >= T_GET2) + sum(1 for tc, _ in RING_T if t >= tc)
    n += int(999 * smooth(ramp(t, T_L1 - 0.2, T_L1 + 1.2)))
    return min(999, n)
def rings(cr, t, p, ly):
    if ly != "back" or t >= T_STOP + 1: return
    if t < T_GET1: O.draw_ring(cr, R1[0], R1[1] + 8 * math.sin(t * 2), t)
    else: O.draw_sparkle(cr, R1[0], R1[1], (t - T_GET1) / 0.4)
    if t < T_GET2: O.draw_ring(cr, R2[0], R2[1] + 8 * math.sin(t * 2 + 1), t + 0.3)
    else: O.draw_sparkle(cr, R2[0], R2[1], (t - T_GET2) / 0.4)
    for i, (tc, (x, y)) in enumerate(RING_T):
        if t < tc: O.draw_ring(cr, x, y + 8 * math.sin(t * 2 + i), t + i * 0.2)
        else: O.draw_sparkle(cr, x, y, (t - tc) / 0.4)
S.prop(rings)

DUST = []
_t = T_R + 2.0
while _t < T_STOP:
    x, th = contact(_t)
    if th == 0.0: DUST.append((_t, x, _t >= T_DEC))
    _t += 0.06 if _t < T_DEC else 0.03
def dust(cr, t, p, ly):
    if ly != "back": return
    for t0, x, sk in DUST:
        a = t - t0
        if 0 <= a < 1.4:
            k = 1.0 if sk else min(1.0, v_of(t0 - T_R) / 2500)
            O.draw_smoke_puff(cr, x + (120 if sk else -40 * a), FLOOR_Y - 40 - 60 * a, (30 + 90 * a) * (0.6 + 0.8 * k),
                              alpha=(1 - a / 1.4) * 0.8, dark=0.05)
S.prop(dust)

# ---------------------------------------------------------------- camera for the run
def follow(t):
    x, th = contact(t)
    z = lerp(0.85, 0.62, smooth(ramp(t, T_R + 1.0, T_R + 4.0)))
    cx, cy = x + lerp(140, 260, ramp(t, T_R, T_R + 4)), 900.0
    k = smooth(ramp(t, T_L0 - 1.2, T_L0 - 0.1)) * (1 - smooth(ramp(t, T_L1 + 0.05, T_L1 + 0.6)))
    cx, cy, z = lerp(cx, LX, k), lerp(cy, LCY + 150, k), lerp(z, 0.46, k)
    e = smooth(ramp(t, T_DEC - 0.3, T_STOP + 0.5))                   # settles on the goal: him + the sign
    return lerp(cx, X_STOP - 300, e), lerp(cy, 920, e), lerp(z, 0.78, e)
_ct = T_R + 0.6
while _ct < T_STOP + 0.6:
    S.camera(_ct, *follow(_ct), dur=1 / 30, ease="linear"); _ct += 1 / 30
CAM_POSE = (X_STOP + 80, 985, 1.0)
S.camera(T_POSE - 0.5, *CAM_POSE, dur=0.8)

# ================================================================ THE GOAL SIGN
PHI = 2 * math.pi * 7 + math.pi
def sign_phi(t):
    if t < T_PASS: return 0.0
    u = min(1.0, (t - T_PASS) / (T_SIGN - T_PASS))
    return PHI * (1 - (1 - u) ** 2)
def goal_sign(cr, t, p, ly):
    if ly != "back": return
    x, yb = GOALX, FLOOR_Y
    L.sketch_rect(cr, x - 12, yb - 520, x + 12, yb, 5, sid=7300, fill=(0.62, 0.64, 0.68))
    phi = sign_phi(t); c = math.cos(phi)
    w = 165 * max(0.06, abs(c)); cy = yb - 690
    L.sketch_ellipse(cr, x, cy, w, 165, 7, sid=7301, fill=(1.0, 0.82, 0.15) if c >= 0 else (0.45, 0.70, 1.0))
    if abs(c) > 0.25:
        cr.save(); cr.translate(x, cy); cr.scale(abs(c), 1.0)
        if c >= 0:
            O.draw_text(cr, "GOAL", 0, 0, 70, color=(200, 40, 34))
        else:                                                     # his own face
            L.sketch_circle(cr, 0, 8, 105, 6, sid=7302)
            for ex in (-38, 38):
                L.sketch_circle(cr, ex, -5, 22, 4, sid=7303 + (ex > 0))
                cr.arc(ex + 3, -2, 8, 0, 2 * math.pi); cr.set_source_rgb(0.07, 0.07, 0.08); cr.fill()
            L.sketch_line(cr, [(-30, 55), (30, 55)], 5, sid=7305)
            O.sketch_curve(cr, (0, -97), (-10, -150), (18, -140), 5, sid=7306)
        cr.restore()
    if t >= T_PASS and t < T_SIGN:                                 # spin lines
        L.motion_lines(cr, x - 200, cy - 60, math.pi, n=3, length=90, spread=60, alpha=0.6 * (1 - ramp(t, T_SIGN - 0.8, T_SIGN)), sid=7310)
S.prop(goal_sign)

# ================================================================ VICTORY STANCE. HE HAS PASSED.
L.POSES["victory"] = dict(lelb=(415, 965), lhand=(476, 1092), lhand_t="fist", relb=(705, 790), rhand=(740, 615),
                          rhand_t="peace", lfoot=(470, FLOOR_Y), rfoot=(625, FLOOR_Y), lknee=(495, 1300), rknee=(600, 1300),
                          lean=0.04, tilt=-0.07, lfoot_dir=-0.6, rfoot_dir=0.8)
S.set(T_POSE - 0.12, "stand", "dead_stare", dur=0.1, stretch=-0.15)
S.set(T_POSE, "victory", "dead_stare", dur=0.18, ease="back", look=(0.0, 0.0))
S.set(T_BUG0 + 1.8, "victory", "dead_stare", dur=0.5, look=(0.75, 0.85))        # eyes only: the bug
S.set(T_BUG1 + 0.6, "victory", "dead_stare", dur=0.3, look=(0.0, 0.0))          # back to us. holding.
S.blink(T_POSE + 1.6, T_BUG1 + 0.2)
def banner(cr, t):
    if not (T_POSE + 0.3 <= t < T_POSE + 3.2): return
    u = smooth(ramp(t, T_POSE + 0.3, T_POSE + 0.6)) - smooth(ramp(t, T_POSE + 2.8, T_POSE + 3.2))
    x = lerp(-900, 140, u)
    L.sketch_rect(cr, x, 1290, x + 800, 1400, 6, sid=7320, fill=(0.20, 0.42, 0.90))
    for k in range(4): L.sketch_rect(cr, x - 60 - k * 0 , 1300 + k * 25, x - 10, 1312 + k * 25, 0.1, sid=7321 + k, fill=(1.0, 0.82, 0.15))
    for dx, dy in ((-4, 0), (4, 0), (0, -4), (0, 4)):
        O.draw_text(cr, "HE HAS PASSED", x + 400 + dx, 1345 + dy, 66, color=(18, 18, 22))
    O.draw_text(cr, "HE HAS PASSED", x + 400, 1345, 66, color=(255, 255, 255))
S.overlay(banner)
def peace(cr, t, p, ly):
    """a big readable V: two chunky fingers up out of his raised mitt."""
    if ly != "front": return
    k = smooth(ramp(t, T_POSE + 0.05, T_POSE + 0.2)) * (1 - smooth(ramp(t, T_DOWN, T_DOWN + 0.25)))
    if k < 0.05: return
    hx, hy = p["rhand"]
    for ang in (-0.32, 0.18):
        cr.save(); cr.translate(hx, hy - 10); cr.rotate(ang)
        L.sketch_rect(cr, -13, -70 * k, 13, 0, 5, sid=7330 + (ang > 0), fill=(0.97, 0.96, 0.93))
        cr.restore()
    L.sketch_circle(cr, hx, hy, 24, 5, sid=7332, fill=(0.97, 0.96, 0.93))
S.prop(peace)

# ================================================================ the bug
BUG_STOP = X_STOP + 205
def bug_state(t):
    """(x, facing -1 left / +1 right, poke 0..1, eye look up 0..1, putter bob)"""
    if t < T_BUG0: return None
    if t < T_BUG1:
        u = (t - T_BUG0) / (T_BUG1 - T_BUG0)
        return (lerp(X_STOP + 1250, BUG_STOP, u), -1, 0.0, 0.0)
    poke = pulse(t, T_POKE, 0.12) if T_POKE - 0.2 < t < T_POKE + 0.3 else 0.0
    up = smooth(ramp(t, T_BUG1 + 0.1, T_BUG1 + 0.4)) * (1 - smooth(ramp(t, T_BUGOFF - 0.2, T_BUGOFF)))
    if t < T_BUGOFF: return (BUG_STOP, -1, poke, up)
    return (BUG_STOP + 260 * (t - T_BUGOFF - 0.3) if t > T_BUGOFF + 0.3 else BUG_STOP, 1, 0.0, 0.0)
def bug(cr, t, p, ly):
    if ly != "front": return
    st = bug_state(t)
    if st is None: return
    x, f, poke, up = st
    moving = (T_BUG0 <= t < T_BUG1) or t > T_BUGOFF + 0.3
    bob = 5 * abs(math.sin(t * 9)) if moving else 0.0
    O.draw_ladybot(cr, x, FLOOR_Y, t, face=f, poke=poke, look_up=up, bob=bob, wheel_ang=-x / 30.0)
    if moving and int(t * 4) % 2 == 0:
        a = (t * 4) % 1.0
        O.draw_smoke_puff(cr, x - f * 95 - f * 40 * a, FLOOR_Y - 60 - 30 * a, 14 + 16 * a, alpha=0.5 * (1 - a), dark=0.2)
S.prop(bug)
for k in range(int((T_BUG1 - T_BUG0) * 3)): S.sfx(T_BUG0 + 0.6 + k / 3, "tok", 0.012)

# ---------------------------------------------------------------- the poke: every ring comes out
S.set(T_POKE + 0.02, "victory", "dead_stare", dur=0.05, ease="snap", stretch=-0.12, look=(0.0, 0.0))
S.set(T_POKE + 0.12, "victory", "dead_stare", dur=0.35, ease="back", stretch=0.0, look=(0.0, 0.0))
S.shake(T_POKE, 0.4, 10)
S.sfx(T_POKE, "boop", 0.05)
_rr = random.Random(9)
BURST = []
for i in range(130):
    ang = _rr.uniform(-math.pi * 0.97, -math.pi * 0.03); sp = _rr.uniform(700, 2300)
    vx, vy = math.cos(ang) * sp, math.sin(ang) * sp
    x, y = X_STOP + _rr.uniform(-60, 60), 900 + _rr.uniform(-140, 140)
    life = _rr.uniform(2.6, 4.0); traj = []
    for fr in range(int(life * 30) + 1):
        traj.append((x, y)); dt = 1 / 30
        vy += 2600 * dt; x += vx * dt; y += vy * dt
        if y > FLOOR_Y - 50 and vy > 0: y = FLOOR_Y - 50; vy = -vy * 0.55; vx *= 0.8
    BURST.append((life, traj, _rr.uniform(0, 6)))
def burst(cr, t, p, ly):
    if ly != "front" or t < T_POKE: return
    s = t - T_POKE; fr = int(s * 30)
    for life, traj, ph in BURST:
        if s >= life: continue
        if s > life - 0.9 and int(s * 15) % 2: continue                 # flicker before they vanish
        x, y = traj[min(fr, len(traj) - 1)]
        O.draw_ring(cr, x, y, t + ph, r=44)
S.prop(burst)

S.set(T_DOWN, "stand", "dead_stare", dur=0.8, look=(0.7, 0.9), tilt=0.06)      # lowers it. looks at the bug.
S.set(T_BUGOFF + 0.4, "stand", "dead_stare", dur=0.5, look=(0.9, 0.6), tilt=0.04)  # watches it go
S.set(T_US, "stand", "dead_stare", dur=0.4, look=(0.0, 0.0), tilt=0.0)          # us
S.blink(T_US + 0.6)
S.camera(T_DOWN + 0.3, X_STOP + 60, 960, 1.05, 2.0)

# ================================================================ the ask, past the goal
S.t = T_ASK
S.the_ask(T_ASK, hold=8.0)

# ---------------------------------------------------------------- HUD: the ring counter
def hud(cr, t):
    if t < T_GET1: return
    a = ramp(t, T_GET1, T_GET1 + 0.3)
    if t < T_POKE: n, warn = ring_count(t), 0.0
    else:
        n = int(999 * (1 - ramp(t, T_POKE, T_POKE + 0.5, "linear")))
        s = t - T_POKE
        warn = (0.5 + 0.5 * math.cos(s * 8)) if s < 4.0 else 1.0
    O.draw_ring_hud(cr, n, alpha=a, warn=warn)
S.overlays.insert(0, hud)

# ================================================================ MUSIC + game sounds (original, bright: added after the soft filter)
import numpy as np
SR = L.SR
def _t(d): return np.arange(int(d * SR)) / SR
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def fm_note(m, d, idx=2.2, ratio=2.0, decay=0.25):
    tt = _t(d); f = mtof(m)
    env = np.minimum(1, tt / 0.006) * np.exp(-tt / decay) * np.minimum(1, (d - tt) / 0.02)
    mod = idx * np.exp(-tt / 0.12) * np.sin(2 * np.pi * f * ratio * tt)
    return (np.sin(2 * np.pi * f * tt + mod) * env).astype(np.float32)
def bass_note(m, d):
    tt = _t(d); f = mtof(m)
    sq = np.sign(np.sin(2 * np.pi * f * tt)) * 0.5 + np.sin(2 * np.pi * f * tt) * 0.5
    return (sq * np.minimum(1, tt / 0.004) * np.exp(-tt / 0.18) * np.minimum(1, (d - tt) / 0.01)).astype(np.float32)
_nr = np.random.default_rng(3)
def kick():
    tt = _t(0.18); return (np.sin(2 * np.pi * np.cumsum(55 + 140 * np.exp(-tt / 0.03)) / SR) * np.exp(-tt / 0.07)).astype(np.float32)
def snare():
    tt = _t(0.16); return (_nr.standard_normal(len(tt)) * np.exp(-tt / 0.045) * 0.6 + np.sin(2 * np.pi * 190 * tt) * np.exp(-tt / 0.04) * 0.4).astype(np.float32)
def hat():
    tt = _t(0.05); n = _nr.standard_normal(len(tt)); n = n - np.convolve(n, np.ones(4) / 4, "same")
    return (n * np.exp(-tt / 0.012) * 0.5).astype(np.float32)
E8 = 60 / 152 / 2                                           # eighth note at 152 bpm
# an original 8-bar tune over C | Am | Dm | G  (pairs: midi or None rest, length in eighths)
MEL = [(76, 1), (79, 1), (84, 2), (83, 1), (79, 1), (81, 2),
       (79, 1), (76, 1), (72, 2), (74, 1), (76, 2), (None, 1),
       (77, 1), (81, 1), (86, 2), (84, 1), (81, 1), (83, 2),
       (81, 1), (79, 1), (77, 1), (74, 1), (79, 3), (None, 1),
       (76, 1), (79, 1), (84, 2), (83, 1), (79, 1), (81, 2),
       (79, 1), (76, 1), (84, 2), (83, 1), (81, 1), (79, 2),
       (77, 1), (76, 1), (74, 1), (77, 1), (81, 2), (84, 2),
       (83, 2), (86, 2), (84, 3), (None, 1)]
ROOTS = [36, 33, 38, 31] * 2
CHORD = {36: (64, 67, 71), 33: (60, 64, 67), 38: (65, 69, 72), 31: (65, 67, 71)}
def place(buf, sig, t0, g):
    i = int(t0 * SR)
    if i < 0 or i >= len(buf): return
    m = min(len(sig), len(buf) - i); buf[i:i + m] += sig[:m] * g
def music(buf, t0, t1):
    bar = 8 * E8; loop = 8 * bar
    k = 0
    while t0 + k * loop < t1:
        b0 = t0 + k * loop
        tm = b0
        for m, d in MEL:
            if m is not None and tm < t1: place(buf, fm_note(m, d * E8 * 0.95, decay=0.18 + 0.08 * d), tm, 0.55)
            tm += d * E8
        for bi, r in enumerate(ROOTS):
            for e in range(8):
                te = b0 + bi * bar + e * E8
                if te >= t1: continue
                place(buf, bass_note(r + (12 if e % 2 else 0), E8 * 0.9), te, 0.45)
                if e in (0, 4): place(buf, kick(), te, 0.8)
                if e in (2, 6): place(buf, snare(), te, 0.35)
                place(buf, hat(), te + E8 / 2, 0.25)
                if e in (1, 3, 5, 7):                                      # off-beat chord stabs
                    for cm in CHORD[r]: place(buf, fm_note(cm, E8 * 0.5, idx=1.0, ratio=1.0, decay=0.06), te, 0.12)
        k += 1
def ring_chime():
    a = fm_note(100, 0.07, idx=1.2, ratio=3.0, decay=0.05); b = fm_note(105, 0.35, idx=1.2, ratio=3.0, decay=0.12)
    out = np.zeros(len(a) + len(b), np.float32); out[:len(a)] += a; out[int(0.055 * SR):int(0.055 * SR) + len(b)] += b
    return out
def scatter(buf, t0):
    rr = random.Random(4)
    for k in range(22):
        tk = t0 + 0.9 * (k / 22) ** 1.3
        place(buf, fm_note(rr.choice((96, 98, 100, 103, 105, 108)) - int(8 * k / 22), 0.2, idx=1.5, ratio=3.0, decay=0.07), tk, 0.55 - 0.015 * k)
def jingle(buf, t0):
    s = 60 / 152 / 4
    seq = [(72, 0), (76, 1), (79, 2), (84, 3), (83, 5), (84, 6), (88, 8)]
    for m, k in seq: place(buf, fm_note(m, 1.2 if k == 8 else 0.3, decay=0.5 if k == 8 else 0.12), t0 + k * s, 0.6)
    for cm in (60, 64, 67, 72): place(buf, fm_note(cm, 1.3, idx=0.8, ratio=1.0, decay=0.5), t0 + 8 * s, 0.22)
    place(buf, kick(), t0 + 8 * s, 0.8)
def sign_spin(buf, t0, t1):
    tk = t0
    while tk < t1:
        place(buf, hat(), tk, 0.5); place(buf, fm_note(91, 0.04, idx=0.5, decay=0.02), tk, 0.12)
        u = (tk - t0) / (t1 - t0); tk += 0.04 + 0.22 * u * u
def _border():
    a, b = T_WALK, T_ARR
    for _ in range(40):
        m = (a + b) / 2
        if walk_x(m) < GX: a = m
        else: b = m
    return a
T_MUSIC0 = _border()
def bright(n):
    buf = np.zeros(n, np.float32)
    mus = np.zeros(n, np.float32); music(mus, T_MUSIC0, T_PASS + 0.15)
    i0, i1 = int((T_PASS - 0.15) * SR), int((T_PASS + 0.15) * SR)
    mus[i0:i1] *= np.linspace(1, 0, i1 - i0); mus[i1:] = 0
    mus[int(T_MUSIC0 * SR):int(T_MUSIC0 * SR) + 400] *= np.linspace(0, 1, 400)
    buf += mus * 0.055
    ch = ring_chime()
    for tc in [T_GET1, T_GET2] + [tc for tc, _ in RING_T][:12]: place(buf, ch, tc, 0.05)
    sp = np.zeros(n, np.float32); sign_spin(sp, T_PASS, T_SIGN); buf += sp * 0.05
    jg = np.zeros(n, np.float32); jingle(jg, T_POSE); buf += jg * 0.07
    sc = np.zeros(n, np.float32); scatter(sc, T_POKE + 0.03); buf += sc * 0.09
    return buf
_orig_soften = L._soften
def _soften_plus(x):
    return _orig_soften(x) + bright(len(x))
L._soften = _soften_plus

if __name__ == "__main__":
    print(f"loop {T_L0:.2f}-{T_L1:.2f}  stop {T_STOP:.2f}  pass {T_PASS:.2f}  pose {T_POSE:.2f}  poke {T_POKE:.2f}  ask {T_ASK:.2f}  end {S.t:.2f}  music {T_MUSIC0:.2f}", file=sys.stderr)
    S.render("day009.mp4")
