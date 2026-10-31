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
TREE    CUT: a quiet palm tree. Nothing happens. Nothing keeps happening. Then WHAM: he hits it flat at full speed. Every
        ring explodes out of him and rains down everywhere. RINGS 0 (flashing red). He stays stuck to the tree, deadpan.
        Slides down onto his butt. One last ring rolls up, wobbles and falls flat next to him. He looks at it. At us.
END     Stands. The ask, under the palm tree in the green hill (where he lives now).
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
TREEX = 60000.0                           # the palm tree he hits
PALMS = [(10150, 760), (12350, 880), (14100, 720), (18900, 860), (20600, 760), (23500, 900), (26800, 780),
         (30000, 860), (TREEX - 1500, 760), (TREEX + 1300, 840)]
FLOWERS = [10350, 11650, 12900, 13650, 14800, 15400, 18400, 19700, 21300, 22400, 24600, 25900, 27800,
           TREEX - 900, TREEX + 700]

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
CUT_TREE = T_L1 + 3.3
T_HIT = CUT_TREE + 2.6
T_SLIDE = T_HIT + 2.3
T_SIT = T_SLIDE + 1.1
T_ROLL0 = T_SIT + 1.2
T_FALL = T_ROLL0 + 2.3
T_STAND = T_FALL + 2.6
T_STEP = T_STAND + 0.9
XASK = TREEX - 540 - 680
T_ASK = T_STEP + 2.2

def contact(t):
    """(x, theta) of the point under his feet during the run; theta = loop angle (0 = on flat ground)."""
    u = t - T_R; s = s_of(u)
    if s < S_L: return 540 + SXB + s, 0.0
    if s < S_L + CIRC: return LX, (s - S_L) / R
    return LX + (s - S_L - CIRC), 0.0
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
    if t < CUT_TREE:
        O.draw_airfield_world(cr, t, x0=1300, x1=GX, sign_x=2230, sock_x=4300, hangar_x=1950)
        O.draw_green_hill_world(cr, t, x0=GX, x1=TREEX + 8000, loop=(LX, R), palms=PALMS, flowers=FLOWERS)
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
    else:
        O.draw_green_hill_world(cr, t, x0=GX, x1=TREEX + 8000, palms=PALMS, flowers=FLOWERS)
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
S.sfx(T_WALK + 4.6, "twinkle", 0.04)                                       # into the green hill

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
S.sfx(T_GET1, "ding", 0.06)
S.xkeys.append((T_W2, SXB, T_GET2 - T_W2 + 0.1, "smooth")); S.x = SXB
S.set(T_W2, "stand", "dead_stare", dur=0.3, look=(0.7, 0.2))
S.sfx(T_GET2, "ding", 0.06)
S.set(T_GET2 + 0.45, "stand", "dead_stare", dur=0.35, look=(0.0, 0.0))     # us. RINGS 2.
S.blink(T_GET2 + 1.0)
S.set(T_R - 0.7, "stand", "dead_stare", dur=0.4, look=(0.95, 0.1))       # the line of rings
S.camera(T_ARR, 540 + SXA + 160, 900, 0.85, 1.0)
S.camera(T_W2, 540 + SXB + 140, 900, 0.85, 1.2)

# ================================================================ THE RUN
_t = T_R
while _t < CUT_TREE - 1 / 30:
    S.xkeys.append((_t, run_offset(_t), 1 / 30, "linear")); _t += 1 / 30
S.set(T_R, "stand", "deadpan", dur=0.4, lag=0.3)
S.set(T_R + 1.5, "stand", "deadpan", dur=1.5, run=1.0, lag=0.1)
S.set(T_BLUR - 0.3, "stand", "deadpan", dur=0.3, run=1.0, lid=0.35, lag=0.0)
S.set(T_BLUR, "stand", "deadpan", dur=0.0, lid=0.45, curl=-0.8, lag=0.0, nowalk=1.0)
S.sfx(T_BLUR, "whoosh", 0.07)
S.sfx(T_R + 2.5, "wind", 0.03, dur=T_BLUR - T_R - 2.5)
S.sfx(T_BLUR + 0.1, "wind", 0.06, dur=CUT_TREE - T_BLUR - 1.3)
S.sfx(T_L0, "whoosh", 0.06); S.sfx(T_L1, "whoosh", 0.06)

def blur_hook(tt, p):
    if not (T_BLUR <= tt < CUT_TREE): return p
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
    if not (T_R <= tt < CUT_TREE): return p
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
    if not (T_BLUR <= t < CUT_TREE) or ly != "back": return
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
for k in range(1, 40):
    x = LX + 300 + 330 * k
    RINGS.append((S_L + CIRC + (x - LX), (x, 950.0)))
RING_T = [(T_R + u_of_s(s), xy) for s, xy in RINGS]
for tc, _ in RING_T[:3]: S.sfx(tc, "ding", 0.04)
def ring_count(t):
    n = (t >= T_GET1) + (t >= T_GET2) + sum(1 for tc, _ in RING_T if t >= tc)
    n += int(999 * smooth(ramp(t, T_L1 - 0.2, T_L1 + 1.6)))
    return min(999, n)
def rings(cr, t, p, ly):
    if ly != "back" or t >= CUT_TREE: return
    if t < T_GET1: O.draw_ring(cr, R1[0], R1[1] + 8 * math.sin(t * 2), t)
    else: O.draw_sparkle(cr, R1[0], R1[1], (t - T_GET1) / 0.4)
    if t < T_GET2: O.draw_ring(cr, R2[0], R2[1] + 8 * math.sin(t * 2 + 1), t + 0.3)
    else: O.draw_sparkle(cr, R2[0], R2[1], (t - T_GET2) / 0.4)
    for i, (tc, (x, y)) in enumerate(RING_T):
        if t < tc: O.draw_ring(cr, x, y + 8 * math.sin(t * 2 + i), t + i * 0.2)
        else: O.draw_sparkle(cr, x, y, (t - tc) / 0.4)
S.prop(rings)

# dust kicked up behind him on the flat
DUST = []
_t = T_R + 2.0
while _t < CUT_TREE - 0.8:
    x, th = contact(_t)
    if th == 0.0: DUST.append((_t, x))
    _t += 0.06
def dust(cr, t, p, ly):
    if ly != "back" or t >= CUT_TREE: return
    for t0, x in DUST:
        a = t - t0
        if 0 <= a < 1.4:
            k = min(1.0, v_of(t0 - T_R) / 2500)
            O.draw_smoke_puff(cr, x - 40 * a, FLOOR_Y - 40 - 60 * a, (30 + 90 * a) * (0.6 + 0.8 * k), alpha=(1 - a / 1.4) * 0.8, dark=0.05)
S.prop(dust)

# ---------------------------------------------------------------- camera for the run (he finally outruns it)
def follow(t):
    x, th = contact(t)
    z = lerp(0.85, 0.62, smooth(ramp(t, T_R + 1.0, T_R + 4.0)))
    cx, cy = x + lerp(140, 260, ramp(t, T_R, T_R + 4)), 900.0
    k = smooth(ramp(t, T_L0 - 1.2, T_L0 - 0.1)) * (1 - smooth(ramp(t, T_L1 + 0.05, T_L1 + 0.6)))
    return lerp(cx, LX, k), lerp(cy, LCY + 150, k), lerp(z, 0.46, k)
T_LET = T_L1 + 0.6                                                    # the camera stops keeping up
_lx, _ly, _lz = follow(T_LET)
_vl = v_of(T_LET - T_R) * 0.8
def cam_run(t):
    if t < T_LET: return follow(t)
    s = t - T_LET; D = 1.4                                           # decelerates to a stop
    dx = _vl * (s - s * s / (2 * D)) if s < D else _vl * D / 2
    return _lx + dx, _ly, _lz
_ct = T_R + 0.6
while _ct < CUT_TREE - 0.05:
    S.camera(_ct, *cam_run(_ct), dur=1 / 30, ease="linear"); _ct += 1 / 30

# ================================================================ THE TREE. nothing happens. then WHAM.
CAM_TREE = (TREEX + 40, 880, 0.78)
S.cut(CUT_TREE - 1 / 30, cam=CAM_TREE, x=TREEX - 540 - 6000)
S.xkeys.append((T_HIT - 0.12, TREEX - 540 - 6000, 0.001, "linear"))
S.xkeys.append((T_HIT - 0.1, TREEX - 540, 0.1, "linear")); S.x = TREEX - 540
S.camera(CUT_TREE + 0.2, TREEX + 40, 890, 0.82, T_HIT - CUT_TREE - 0.3)     # slow creep in on the empty tree
S.sfx(T_HIT - 1.0, "whine", 0.03, dur=1.0)
L.POSES["splat"] = dict(lelb=(440, 800), lhand=(375, 690), relb=(640, 800), rhand=(705, 690), lhand_t="open", rhand_t="open",
                        lknee=(470, 1290), lfoot=(425, 1440), rknee=(610, 1290), rfoot=(655, 1440),
                        lfoot_dir=-0.9, rfoot_dir=0.9, nowalk=1.0)
S.set(CUT_TREE - 1 / 30, "stand", "deadpan", dur=0.0, nowalk=1.0, lag=0.0, lid=0.45)
S.set(T_HIT, "splat", "dead_stare", dur=0.0, hop=210, stretch=-0.25, lag=0.6, mouth="flat", eyescale=1.05)
S.set(T_HIT + 0.12, "splat", "dead_stare", dur=0.3, ease="back", hop=210, stretch=0.0, lag=0.6, mouth="flat")
S.flash(T_HIT, 0.25); S.shake(T_HIT, 0.7, 26)
S.sfx(T_HIT, "kaboom", 0.32, dur=1.4); S.sfx(T_HIT, "thud", 0.2); S.sfx(T_HIT + 0.05, "twinkle", 0.1)
S.set(T_HIT + 1.2, "splat", "dead_stare", dur=0.3, hop=210, mouth="flat", lag=0.6, look=(0.0, 0.0))
S.blink(T_HIT + 1.5)
S.set(T_SLIDE, "splat", "dead_stare", dur=0.5, hop=200, mouth="flat", lag=0.6, look=(0.0, 0.0), lid=0.3)
S.set(T_SLIDE + 0.5, "sit_floor", "dead_stare", dur=T_SIT - T_SLIDE - 0.5, ease="inn", mouth="flat", lag=0.6, nowalk=1.0)
S.sfx(T_SLIDE + 0.4, "slide_down", 0.04, dur=T_SIT - T_SLIDE - 0.4)
S.set(T_SIT, "sit_floor", "dead_stare", dur=0.06, ease="snap", stretch=-0.3, nowalk=1.0)
S.set(T_SIT + 0.12, "sit_floor", "dead_stare", dur=0.4, ease="back", stretch=0.0, nowalk=1.0)
S.sfx(T_SIT, "thud", 0.12); S.shake(T_SIT, 0.3, 10)
S.camera(T_SIT + 0.2, TREEX - 60, 940, 0.9, 1.4)

def bend(t):
    if t < T_HIT: return 0.03 * math.sin(t * 1.1)
    s = t - T_HIT
    return 0.55 * math.exp(-2.0 * s) * math.sin(15 * s) + 0.03 * math.sin(t * 1.1)
H_TREE = 980.0
def stuck(tt, p):
    if not (T_HIT <= tt < T_SIT + 0.3): return p
    for j in L.JOINTS:
        hgt = max(0.0, FLOOR_Y - p[j][1]) / H_TREE
        p[j] = (p[j][0] + bend(tt) * 260 * hgt * hgt, p[j][1])
    return p
S.hook(stuck)
def tree(cr, t, p, ly):
    if ly == "back" and t >= CUT_TREE - 1 / 30:
        O.draw_palm(cr, TREEX - 50, t, H_TREE, bend=bend(t), s=1.25, sid=40)
def streak(cr, t, p, ly):
    if ly != "front" or not (T_HIT - 0.12 <= t < T_HIT + 0.35): return
    a = 1 - ramp(t, T_HIT, T_HIT + 0.35, "linear")
    for k, y in enumerate((700, 860, 1020, 1200, 1360)):
        L.sketch_line(cr, [(TREEX - 1300, y), (TREEX - 180, y)], 7, sid=7200 + k, amp=0.6, alpha=a)
    if t >= T_HIT: L.draw_impact(cr, TREEX, 820, (t - T_HIT) / 0.6, r=420, sid=61)

# every ring he had comes out of him at once
_rr = random.Random(9)
BURST = []
for i in range(130):
    ang = _rr.uniform(-math.pi * 0.97, -math.pi * 0.03); sp = _rr.uniform(700, 2300)
    vx, vy = math.cos(ang) * sp, math.sin(ang) * sp
    x, y = TREEX + _rr.uniform(-60, 60), 830 + _rr.uniform(-140, 140)
    life = _rr.uniform(2.6, 4.0); traj = []
    for f in range(int(life * 30) + 1):
        traj.append((x, y)); dt = 1 / 30
        vy += 2600 * dt; x += vx * dt; y += vy * dt
        if y > FLOOR_Y - 50 and vy > 0: y = FLOOR_Y - 50; vy = -vy * 0.55; vx *= 0.8
    BURST.append((life, traj, _rr.uniform(0, 6)))
def burst(cr, t, p, ly):
    if ly != "front" or t < T_HIT: return
    s = t - T_HIT; f = int(s * 30)
    for life, traj, ph in BURST:
        if s >= life: continue
        if s > life - 0.9 and int(s * 15) % 2: continue                 # flicker before they vanish
        x, y = traj[min(f, len(traj) - 1)]
        O.draw_ring(cr, x, y, t + ph, r=44)
S.sfx(T_HIT + 0.9, "ding", 0.04); S.sfx(T_HIT + 1.3, "ding", 0.03); S.sfx(T_HIT + 1.9, "ding", 0.02)

# ---------------------------------------------------------------- one last ring rolls up, wobbles, falls flat
RX1 = TREEX + 330
def last_ring(cr, t, p, ly):
    if ly != "back" or t < T_ROLL0: return
    u = ramp(t, T_ROLL0, T_FALL, "out")
    x = lerp(TREEX + 1100, RX1, u)
    if t < T_FALL:
        O.draw_ring(cr, x, FLOOR_Y - 52, 0.0, r=52, spin=0.0)
        return
    s = t - T_FALL
    fl = smooth(ramp(s, 0.0, 0.5)) - 0.18 * math.exp(-s * 3) * abs(math.sin(s * 14)) * ramp(s, 0.4, 0.5)
    fl = max(0.0, min(1.0, fl))
    O.draw_ring(cr, RX1, FLOOR_Y - 52 * (1 - 0.82 * fl), 0.0, r=52, flat=max(0.001, fl), spin=0.0)
for k, dt in enumerate((0.5, 0.75, 0.92, 1.03)): S.sfx(T_FALL + dt, "tok", 0.05 - 0.008 * k)
S.set(T_ROLL0 + 0.5, "sit_floor", "dead_stare", dur=0.4, look=(0.85, 0.3), tilt=-0.03, nowalk=1.0)
S.set(T_FALL + 0.4, "sit_floor", "dead_stare", dur=0.3, look=(0.85, 0.6), tilt=-0.05, nowalk=1.0)
S.set(T_FALL + 1.5, "sit_floor", "dead_stare", dur=0.4, look=(0.0, 0.0), tilt=0.0, nowalk=1.0)     # us
S.blink(T_FALL + 2.1)

# ================================================================ stands. the ask, under the palm tree.
S.stand(T_STAND, face="dead_stare")
S.xkeys.append((T_STEP, XASK, 1.8, "smooth")); S.x = XASK                   # steps out from under the tree
S.set(T_STEP, "stand", "dead_stare", dur=0.3, look=(-0.6, 0.0))
S.set(T_STEP + 1.6, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0))
S.camera(T_STEP + 0.1, XASK + 540 + 60, 930, 1.12, 1.9)
S.t = T_ASK
S.the_ask(T_ASK, hold=8.0)

# ---------------------------------------------------------------- HUD: the ring counter
def hud(cr, t):
    if t < T_GET1: return
    a = ramp(t, T_GET1, T_GET1 + 0.3)
    if t < T_HIT: n, warn = ring_count(t), 0.0
    else:
        n = int(999 * (1 - ramp(t, T_HIT, T_HIT + 0.5, "linear")))
        s = t - T_HIT
        warn = (0.5 + 0.5 * math.cos(s * 8)) if s < 4.0 else 1.0
    O.draw_ring_hud(cr, n, alpha=a, warn=warn)
S.overlays.insert(0, hud)

# ---------------------------------------------------------------- draw order
S.props.insert(0, tree)
for f in (streak, burst, last_ring): S.prop(f)

if __name__ == "__main__":
    print(f"loop {T_L0:.2f}-{T_L1:.2f}  cut {CUT_TREE:.2f}  hit {T_HIT:.2f}  ask {T_ASK:.2f}  end {S.t:.2f}", file=sys.stderr)
    S.render("day009.mp4")
