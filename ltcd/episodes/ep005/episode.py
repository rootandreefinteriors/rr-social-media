"""Day 5 — COMMENT episode: @nerdbpy "Eat a billion big Mac's" (Instagram, day 4 reel, 8 likes).
Re-cut on Justin's outline (2026-10-27). Generic burgers and a generic red/yellow burger place: no logo, no arches,
no brand name on screen (only the pinned comment card shows the comment as written).

SHOT 1  The End (block world, half a hardcore heart). Reads the comment. Stares. Slow blink. Tiny nod.
WALK    He walks off to the right; the camera goes with him; the end-stone stops and he's in a new world: pale sky,
        paper ground, a red-and-yellow burger place with a tall BURGERS sign. The hardcore hearts fade away.
TRUCK   He looks at the place. Looks at us. A yellow dump truck (1 BILLION BURGERS) backs in, beeping, tips its bed and
        dumps them all on him. A burger mountain. Silence. His head and neck pop out of the top.
EAT     He pulls out the first wrapped burger, unwraps it, eats it in ONE bite. Then the next. Faster and faster
        (BURGERS LEFT counter falling), his belly swelling as the pile sinks and wrappers pile up around him. The last
        two are a struggle. Done: huge belly, wrappers everywhere, exhausted.
LAUNCH  His eyes go wide. A gurgle. A cartoon jet of poop blasts out of his butt and launches him into the sky: loops,
        flips, a twirl past clouds and up into the stars, the belly slowly deflating. It sputters out. He falls and
        lands on his butt in the wrappers.
END     Stands up. Deadpan. The ask, in front of the burger place (where he lives now).
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y
from ink import smooth, draw_text
import cairo

SX = 2000                       # his body offset in the new world
X0 = 540 + SX                   # his body centre there
BORDER = 1250                   # where the block world ends
STORE_X = 2760
CAM0 = (540, 930, 1.15)
CAM_STORE = (2700, 900, 0.8)
CAM_WIDE = (2800, 1000, 0.62)
CAM_EAT = (2620, 880, 0.95)

# ---------------------------------------------------------------- timeline
T_WALK, T_ARR = 4.6, 8.8
TT0 = 11.0                      # truck starts backing in
TT1 = 13.6                      # bed tips
P0, P1 = 14.2, 16.4             # pour
T_CUT = 19.2; TP = 19.6         # cut close, head pops out
E0 = 21.2                       # eating starts
DURS = [3.4, 1.9, 1.15, 0.8, 0.6, 0.45, 0.36, 0.3, 0.28, 0.26] + [0.25] * 8 + [2.3, 2.6]
N = len(DURS)
SCHED = []
_a = E0
for d in DURS: SCHED.append((_a, d)); _a += d
E_END = _a                       # 37.6
T_WIDE_EYES = E_END + 2.4
TL = T_WIDE_EYES + 1.8           # launch
FL = 9.8                         # flight length; lands on his butt at TL + FL
TLAND = TL + FL

S = M.Scene()
S.auto_blinks = False
S.card("nerdbpy", "Eat a billion big Mac’s", "8", t0=0.35)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0
S.sfx(0.35, "tick", 0.04)

# ================================================================ world: the End -> the new world, sky up to the stars
CLOUDS = [(X0 - 420, 120, 0.9), (X0 + 520, -380, 1.1), (X0 - 150, -820, 1.0), (X0 + 640, -1250, 0.9),
          (X0 - 560, -1500, 1.2), (X0 + 200, -1700, 0.8), (X0 + 900, 400, 0.8)]
_r = random.Random(4)
STARS = [(_r.uniform(1300, 4200), _r.uniform(-3400, -900), _r.uniform(5, 10)) for _ in range(120)]
def world(cr, t):
    g = cairo.LinearGradient(0, 700, 0, -2600)
    g.add_color_stop_rgb(0.0, 0.80, 0.89, 0.98); g.add_color_stop_rgb(0.45, 0.55, 0.62, 0.86)
    g.add_color_stop_rgb(1.0, 0.07, 0.07, 0.20)
    cr.rectangle(BORDER, -6000, 9000, 12000); cr.set_source(g); cr.fill()
    for x, y, s in STARS:
        a = ramp(-y, 900, 1900) * (0.55 + 0.45 * math.sin(t * 2 + x))
        if a > 0.02: cr.rectangle(x, y, s, s); cr.set_source_rgba(1, 1, 0.92, a); cr.fill()
    for x, y, s in CLOUDS: O.draw_cloud(cr, x + 10 * math.sin(t * 0.3 + x), y, s)
    cr.rectangle(BORDER, FLOOR_Y, 9000, 3000); cr.set_source_rgb(0.95, 0.94, 0.90); cr.fill()
    O.draw_burger_store(cr, STORE_X)
    cr.save(); cr.rectangle(-4000, -6000, 4000 + BORDER, 12000); cr.clip()          # the block world, left of the border
    O.draw_end_world(cr, t)
    cr.restore()
S.background(world)

# ================================================================ HUD: hardcore hearts fade as he leaves; BURGERS LEFT
LEFT_KEYS = [(0.0, 1e9)]
for i, (a, d) in enumerate(SCHED):
    done = a + 0.86 * d
    if i < 2: v = 1e9 - (i + 1)
    elif i >= N - 2: v = N - 1 - i                         # 1 -> 0 on the last two
    else: v = 2.0 * (1e9 / 2.0) ** (1 - (i - 1) / (N - 4))  # geometric slide down to 2
    LEFT_KEYS.append((done, max(0.0, v)))
def burgers_left(t):
    prev = LEFT_KEYS[0]
    for k in LEFT_KEYS[1:]:
        if t < k[0]:
            if prev[1] > 3 and k[1] > 1 and k[0] - prev[0] < 0.6:     # rolls between fast steps (log space)
                u = (t - prev[0]) / (k[0] - prev[0])
                return math.exp(lerp(math.log(prev[1]), math.log(k[1]), u))
            return prev[1]
        prev = k
    return prev[1]
def hud(cr, t):
    a = 1 - ramp(t, T_WALK + 1.2, T_WALK + 2.4)
    if a > 0.01:
        s, y = 5.6, 1440 - 6 * 5.6
        cr.rectangle(52, 1352, 470, 100); cr.set_source_rgba(0.08, 0.06, 0.11, 0.62 * a); cr.fill()
        draw_text(cr, "HARDCORE", 72, y - 30, 34, color=(240, 240, 240), anchor="left", alpha=a)
        O.draw_hearts_bar(cr, 78, y, 0.5, s=s, gap=6, blink=0.5 + 0.5 * math.sin(t * 7), alpha=a)
    b = ramp(t, P0, P0 + 0.4) * (1 - ramp(t, E_END + 1.5, E_END + 2.0))
    if b > 0.01:
        cr.rectangle(52, 1290, 520, 150); cr.set_source_rgba(0.08, 0.06, 0.11, 0.62 * b); cr.fill()
        draw_text(cr, "BURGERS LEFT", 72, 1330, 32, color=(240, 240, 240), anchor="left", alpha=b)
        draw_text(cr, f"{int(round(burgers_left(t))):,}", 72, 1392, 58, color=(255, 214, 92), anchor="left", alpha=b)
S.overlays.insert(0, hud)

# ================================================================ SHOT 1: reads it. stares. accepts.
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(0.6, react="dead_stare", lines=1, face="deadpan")
S.set(3.0, "stand", "dead_stare", dur=0.25, lid=1.0)
S.set(3.4, "stand", "resigned", dur=0.35)
def nod(tt, p, a=3.8):
    v = 16 * math.sin(math.pi * min(1.0, max(0.0, (tt - a) / 0.7)))
    if v > 0.01: p["head"] = (p["head"][0], p["head"][1] + v)
    return p
S.hook(nod)

# ================================================================ WALK right, into the new world
S.set(T_WALK - 0.3, "stand", "dead_stare", dur=0.3, look=(0.8, 0.0))
S.xkeys.append((T_WALK, SX, T_ARR - T_WALK, "smooth")); S.x = SX
S.camera(T_WALK, *CAM_STORE, dur=T_ARR - T_WALK + 0.3)
S.set(T_ARR, "stand", "dead_stare", dur=0.3, look=(0.3, 0.0))
S.blink(T_ARR + 0.3)
S.set(T_ARR + 0.6, "stand", "dead_stare", dur=0.4, look=(0.75, -0.45), tilt=-0.04)        # looks at the burger place
S.set(T_ARR + 1.7, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), tilt=0.0)            # at us

# ================================================================ TRUCK: backs in, tips, dumps a billion burgers on him
S.camera(TT0, *CAM_WIDE, dur=1.4)
RX_END = X0 + 430
TRK = Track([(0.0, dict(rx=4100.0, tilt=0.0, load=1.0), 0), (TT0, dict(rx=4100.0, tilt=0.0, load=1.0), 0),
             (TT0, dict(rx=float(RX_END), tilt=0.0, load=1.0), TT1 - 0.4 - TT0, "out"),
             (TT1, dict(rx=float(RX_END), tilt=0.85, load=1.0), 1.2),
             (P0 + 0.4, dict(rx=float(RX_END), tilt=0.85, load=0.0), P1 - P0 - 0.4),
             (P1 + 0.4, dict(rx=float(RX_END), tilt=0.0, load=0.0), 0.8),
             (P1 + 1.4, dict(rx=4400.0, tilt=0.0, load=0.0), 1.6, "inn")])
for k in range(4): S.sfx(TT0 + 0.3 + k * 0.6, "boop", 0.04)
S.sfx(TT1, "whine", 0.015, dur=1.1); S.sfx(P1 + 1.4, "whoosh", 0.04)
def truck(cr, t, p, ly):
    if ly != "back" or not (TT0 <= t < P1 + 3.2): return
    st = TRK.at(t)
    O.draw_dump_truck(cr, st["rx"], FLOOR_Y, st["tilt"], t, st["load"])
S.prop(truck)
def mouth_of_bed(t):
    st = TRK.at(t); a = st["tilt"]
    return (st["rx"] - 250 * math.sin(a) + 30, FLOOR_Y - 175 - 250 * math.cos(a))
_r2 = random.Random(9)
FALLERS = [(P0 + 0.1 + k * (P1 - P0 - 0.3) / 40, _r2.uniform(-320, -40), _r2.uniform(-200, 120)) for k in range(40)]
def falling(cr, t, p, ly):
    if ly != "front" or not (P0 <= t < P1 + 1.2): return
    for t0, vx, vy in FALLERS:
        u = t - t0
        if 0 <= u < 1.2:
            mx, my = mouth_of_bed(t0)
            x, y = mx + vx * u, my + vy * u + 0.5 * 2600 * u * u
            k_ = max(0.0, 1 - ((x - X0) / max(1.0, pile_w(t) / 2)) ** 2)
            if y < FLOOR_Y - pile_h(t) * k_ ** 0.8 + 40 or y < 900:
                O.draw_burger(cr, x, y, 0.55, sid=int(t0 * 10))
for k in range(9): S.sfx(P0 + 0.2 + k * 0.24, "thud", 0.03)
S.shake(P0 + 0.3, P1 - P0, 5)
S.set(TT0 + 0.6, "stand", "dead_stare", dur=0.4, look=(0.9, 0.0))                          # looks at the truck
S.set(TT1 + 0.4, "stand", "dead_stare", dur=0.4, look=(0.8, -0.8), tilt=-0.05)             # ...up at the bed
S.set(P0 + 0.3, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), tilt=0.0)                 # at us, as it lands on him

# the pile: rises over him during the pour, slumps when he pops out, sinks as he eats
def eaten(t):
    n = 0
    for a, d in SCHED:
        if t >= a + 0.72 * d: n += 1
    return n / N
def pile_h(t):
    if t < P0: return 0.0
    if t < TP: return 1060 * smooth(ramp(t, P0 + 0.2, P1))
    h = lerp(1060, 600, ramp(t, TP, TP + 0.22, "out"))
    f = eaten(t)
    return h * (1 - f) if f < 1 else 0.0
def pile_w(t): return 1150 * (0.3 + 0.7 * (1 - eaten(t))) if t >= E0 else 1150 * min(1.0, 0.5 + ramp(t, P0, P1))
def pile(cr, t, p, ly):
    if ly == "front" and t >= P0: O.draw_burger_pile(cr, X0, pile_w(t), pile_h(t))

# ================================================================ HEAD POPS OUT
S.cut(T_CUT, cam=CAM_EAT)
S.set(TP - 0.05, "stand", "dead_stare", dur=0.08, ease="snap", stretch=0.25)
S.set(TP + 0.12, "stand", "dead_stare", dur=0.35, ease="back", stretch=0.0)
S.sfx(TP, "pop", 0.08)
def pop_fx(cr, t, p, ly):
    if ly == "front" and TP <= t < TP + 0.4: L.burst_lines(cr, p["head"][0], p["head"][1] - 40, (t - TP) / 0.4, r0=150, r1=230, n=10, sid=12)
S.blink(TP + 1.0)

# ================================================================ EAT: one bite each, faster and faster
def belly_b(t):
    if t < TL + 0.6: return 1.25 * eaten(t) ** 0.9
    return 1.25 * (1 - smooth(ramp(t, TL + 0.6, TL + 7.6)))
def dip_pt(t): return (X0 + 175, FLOOR_Y - pile_h(t) + 70 if pile_h(t) > 150 else FLOOR_Y - 120)
NEAR = (X0 + 150, 790)
MOUTH = (X0 + 30, 745)          # hand here -> burger centre at his mouth
def cyc(t):
    for i, (a, d) in enumerate(SCHED):
        if a <= t < a + d: return i, (t - a) / d
    return None, None
def eat_hook(tt, p):
    i, u = cyc(tt)
    if i is None: return p
    if u < 0.28: h = lerp(p["rhand"], dip_pt(tt), smooth(u / 0.28))
    elif u < 0.5: h = lerp(dip_pt(tt), NEAR, smooth((u - 0.28) / 0.22))
    elif u < 0.6: h = NEAR
    elif u < 0.72: h = lerp(NEAR, MOUTH, smooth((u - 0.6) / 0.12))
    elif u < 0.86: h = MOUTH
    else: h = lerp(MOUTH, dip_pt(tt), smooth((u - 0.86) / 0.14) * 0.5)
    p["rhand"] = h; p["rhand_t"] = "grip"
    (bx, by), r = O.belly_geom(p, belly_b(tt))
    p["relb"] = (max(X0 + 120, bx + r * 0.85 if belly_b(tt) > 0.3 else 0), 900 if belly_b(tt) < 0.6 else by - r * 0.5)
    if 0.6 <= u < 0.86:                                     # mouth opens wide, then shut
        p["mouth"] = "o"; p["open"] = 1.0 if u < 0.8 else 0.2; p["eyescale"] = 1.0
    if SCHED[i][1] > 1.0: p["look"] = (0.55, 0.15) if u < 0.6 else p["look"]   # watches the slow ones
    return p
def gulps(tt, p):
    for a, d in SCHED:
        v = pulse(tt, a + 0.86 * d, 0.1)
        if v > 0.01: p["head"] = (p["head"][0], p["head"][1] + 12 * v)
    return p
for i, (a, d) in enumerate(SCHED):
    if d > 0.5 or i % 2 == 0: S.sfx(a + 0.72 * d, "chomp", 0.05 if d > 0.5 else 0.03)
    if d > 0.5: S.sfx(a + 0.86 * d, "gulp", 0.05); S.sfx(a + 0.5 * d, "flip", 0.03)
def held(cr, t, p, ly):
    if ly != "front": return
    i, u = cyc(t)
    if i is None or u < 0.3: return
    hx, hy = p["rhand"]; cx, cy = hx, hy - 45
    if u < 0.5: O.draw_wrapped_burger(cr, cx, cy, 0.7)
    elif u < 0.72: O.draw_burger(cr, cx, cy, 0.62, sid=i)
    elif u < 0.84:
        k = (u - 0.72) / 0.12
        O.draw_burger(cr, lerp(cx, X0, k), lerp(cy, 700, k), 0.62 * (1 - k), sid=i)
    if 0.5 <= u < 0.58 and SCHED[i][1] > 0.5: L.burst_lines(cr, cx, cy, (u - 0.5) / 0.1, r0=70, r1=120, n=8, sid=i)
_r3 = random.Random(21)
WR_LAND = [(_r3.choice((-1, 1)) * _r3.uniform(260, 600), _r3.uniform(-1, 1)) for _ in range(N)]
def flying_wrappers(cr, t, p, ly):
    if ly != "front": return
    for i, (a, d) in enumerate(SCHED):
        t0 = a + 0.5 * d; dur = max(0.35, 0.5 * d)
        u = (t - t0) / dur
        if 0 <= u < 1:
            sx_, sy_ = NEAR[0], NEAR[1] - 45
            ex, ey = X0 + WR_LAND[i][0], FLOOR_Y - 30
            O.draw_wrapper(cr, lerp(sx_, ex, u), lerp(sy_, ey, u) - 380 * math.sin(math.pi * u), 1.1, sid=7000 + i)
def wrappers_back(cr, t, p, ly):
    if ly == "back" and t >= E0: O.draw_wrapper_pile(cr, X0, 1350, 30 + 230 * eaten(t))
def wrappers_front(cr, t, p, ly):
    if ly == "front" and t >= E0 + 2: O.draw_wrapper_pile(cr, X0 + 40, 900, 15 + 80 * eaten(t))
def belly(cr, t, p, ly):
    if ly != "front": return
    b = belly_b(t)
    w = (math.sin(t * 26) * ramp(t, TL + 0.6, TL + 1.0) * (1 - ramp(t, TL + 7.2, TL + 7.6))) if t >= TL else 0.0
    O.draw_belly(cr, p, b, wob_=w)
# arms rest on the belly when it is big (and he isn't eating)
def belly_arms(tt, p):
    b = belly_b(tt)
    if b < 0.3 or (TL <= tt < TLAND): return p
    (bx, by), r = O.belly_geom(p, b)
    p["lelb"] = (bx - r - 8, by - r * 0.35); p["lhand"] = (bx - r - 20, by + r * 0.3)
    if cyc(tt)[0] is None:
        p["relb"] = (bx + r + 8, by - r * 0.35); p["rhand"] = (bx + r + 20, by + r * 0.3)
    return p
S.set(E0, "stand", "dead_stare", dur=0.3)
S.set(SCHED[-2][0], "stand", "holding_it", dur=0.8, sweat=0.8, quiver=0.6, twitch=0.5)    # the last two are a fight
S.set(SCHED[-1][0] + 1.4, "stand", "holding_it", dur=0.6, sweat=1.0, quiver=1.0, twitch=1.0, lid=0.35)
S.set(E_END, "stand", "resigned", dur=0.6, lid=0.62, sweat=0.9, breath=2.2, breath_rate=2.4)  # done. exhausted.
S.camera(E_END, X0 + 60, 860, 1.08, 2.6)
S.blink(E_END + 1.2)

# ================================================================ LAUNCH: eyes wide, gurgle, the jet
S.set(T_WIDE_EYES, "stand", "dead_stare", dur=0.12, ease="snap", eyescale=1.35, pupil=0.45, brow=0.5, lid=0.0, twitch=0.8, sweat=0.6)
S.sfx(T_WIDE_EYES + 0.4, "blub", 0.05); S.sfx(T_WIDE_EYES + 1.0, "blub", 0.06); S.shake(T_WIDE_EYES + 1.0, 0.4, 5)
WP = [(0.0, X0, 1118), (0.8, X0, 520), (1.6, X0 + 150, -300), (2.4, X0 + 600, -700), (3.0, X0 + 520, -1250),
      (3.5, X0 + 150, -1060), (4.0, X0 + 260, -700), (4.5, X0 + 560, -900), (5.2, X0 + 300, -1700),
      (5.9, X0 - 200, -2200), (6.6, X0 - 520, -1900), (7.2, X0 - 300, -1500), (7.8, X0 + 50, -1800), (8.3, X0 + 100, -1950)]
def _cr(p0, p1, p2, p3, u):
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)
def Q(u):
    """his hip position u seconds after launch."""
    if u <= 0: return (X0, 1118.0)
    if u < WP[-1][0]:
        k = max(i for i in range(len(WP)) if WP[i][0] <= u)
        a, b = WP[k], WP[k + 1]; s = (u - a[0]) / (b[0] - a[0])
        p0 = WP[max(0, k - 1)]; p3 = WP[min(len(WP) - 1, k + 2)]
        return (_cr(p0[1], a[1], b[1], p3[1], s), _cr(p0[2], a[2], b[2], p3[2], s))
    v = u - WP[-1][0]; d = FL - WP[-1][0]
    y = WP[-1][2] + 0.5 * 3400 / d / d * 2 * (v * v / 2) if v < d else 1450.0     # free fall onto his butt
    y = min(1450.0, WP[-1][2] + (1450.0 - WP[-1][2]) * (v / d) ** 2)
    return (lerp(WP[-1][1], X0, v / d), y)
# head points along the flight direction while the jet is on (precomputed, unwrapped) + one extra twirl
_TH = []; _prev = 0.0
for k in range(int(FL * 120) + 2):
    u = k / 120.0
    if u < 7.8:
        a_, b_ = Q(u - 0.01), Q(u + 0.01)
        vx, vy = b_[0] - a_[0], b_[1] - a_[1]
        th = math.atan2(vx, -vy) if math.hypot(vx, vy) > 1e-3 else _prev
        while th - _prev > math.pi: th -= 2 * math.pi
        while th - _prev < -math.pi: th += 2 * math.pi
        th = lerp(0.0, th, ramp(u, 0.0, 0.5))
    else:
        th = _prev
    _TH.append(th); _prev = th
TH_END = _TH[int(7.8 * 120)]
TH_UP = round(TH_END / (2 * math.pi)) * 2 * math.pi
def theta(u):
    i = min(len(_TH) - 1, max(0, int(u * 120)))
    th = _TH[i] + 2 * math.pi * smooth(ramp(u, 4.1, 4.7))            # the twirl
    if u >= 7.8: th = lerp(TH_END + 2 * math.pi, TH_UP + 2 * math.pi, smooth(ramp(u, 7.8, 8.6)))
    return th
def flight(tt, p):
    if not (TL <= tt < TLAND): return p
    u = tt - TL
    q, th = Q(u), theta(u)
    h = p["hip"]; c, s_ = math.cos(th), math.sin(th)
    for j in L.JOINTS:
        dx, dy = p[j][0] - h[0], p[j][1] - h[1]
        p[j] = (q[0] + dx * c - dy * s_, q[1] + dx * s_ + dy * c)
    p["tilt"] = p.get("tilt", 0.0) + th
    return p
def jet_on(te):
    u = te - TL
    return 0.0 <= u <= 8.0
def jet_k(te):                                                     # pressure: full, then tapers off (no dangling end)
    return 1.0 - smooth(ramp(te - TL, 7.3, 8.0))
def nozzle(te):
    u = te - TL; q, th = Q(u), theta(u)
    return q, (-math.sin(th), math.cos(th))                        # out of his butt, along his body
JET_V, JET_LIFE = 1700.0, 1.6                                   # long enough that it always runs off screen
_rj = random.Random(77)
DROPS = [(TL + k / 90.0, _rj.uniform(-1, 1), _rj.uniform(0.5, 1.0), _rj.uniform(7, 17)) for k in range(int(8.0 * 90))]
def jet(cr, t, p, ly):
    if ly != "back" or not (TL <= t < TL + 9.8): return
    cr.save(); cr.rectangle(-9000, -9000, 20000, 9000 + FLOOR_Y + 6); cr.clip()      # it doesn't go through the ground
    segs, cur = [], []
    te = t
    while te >= max(TL, t - JET_LIFE):                             # nozzle first, outwards
        if jet_on(te):
            (nx, ny), (dx, dy) = nozzle(te); a = t - te
            cur.append((nx + dx * JET_V * a, ny + dy * JET_V * a + 0.5 * 900 * a * a, (50 + 85 * a) * jet_k(te) + 2))
        elif cur: segs.append(cur); cur = []
        te -= 1 / 60
    if cur: segs.append(cur)
    for sg in segs: O.draw_spray(cr, sg, t=t)
    for te0, side, sp, r in DROPS:                                 # spatter flying off the sides
        a = t - te0
        if not (0 <= a < 0.9) or not jet_on(te0): continue
        (nx, ny), (dx, dy) = nozzle(te0)
        vx, vy = dx * JET_V * sp - dy * side * 520, dy * JET_V * sp + dx * side * 520
        O.draw_droplet(cr, nx + vx * a, ny + vy * a + 0.5 * 1500 * a * a, r * (1 - 0.5 * a) * jet_k(te0) + 1)
    cr.restore()
S.sfx(TL, "sploosh", 0.12); S.sfx(TL + 0.05, "kaboom", 0.25, dur=1.6); S.sfx(TL + 0.3, "wind", 0.07, dur=7.6)
S.shake(TL, 0.6, 16)
for k in range(5): S.sfx(TL + 7.5 + k * 0.15, "blub", 0.04)
def launch_poof(cr, t, p, ly):
    if ly == "front" and TL <= t < TL + 0.8: L.draw_poof(cr, X0, FLOOR_Y - 60, (t - TL) / 0.8, r=220, sid=31)
S.set(TL, "cheer", "dead_stare", dur=0.2, eyescale=1.3, pupil=0.5, brow=0.4, lid=0.0, lag=0.45, nowalk=1.0, rhand_t="open", lhand_t="open")
S.set(TL + 3.0, "cheer", "dead_stare", dur=1.0, eyescale=1.25, pupil=0.55, lid=0.1, lag=0.45, nowalk=1.0, rhand_t="open", lhand_t="open")
S.set(TL + 8.0, "sit_floor", "dead_stare", dur=0.5, eyescale=1.0, lag=0.45, nowalk=1.0)             # falling, already sitting
# camera follows him (a little behind, so the loops read)
_ct = TL + 0.2
while _ct < TLAND:
    qa = Q(_ct - TL - 0.25); qb = Q(_ct - TL)
    cx, cy = lerp(qa, qb, 0.5)
    S.camera(_ct, cx + 40, cy - 120, 0.68, dur=0.2, ease="linear")
    _ct += 0.2
S.camera(TLAND - 0.1, X0 + 60, 930, 0.95, dur=0.35, ease="out")

# ================================================================ LANDS ON HIS BUTT. stands. the ask.
S.set(TLAND, "sit_floor", "dead_stare", dur=0.06, ease="snap", stretch=-0.3, lag=1.0)
S.set(TLAND + 0.15, "sit_floor", "dead_stare", dur=0.4, ease="back", stretch=0.0)
S.sfx(TLAND, "thud", 0.2); S.sfx(TLAND + 0.02, "bonk", 0.04); S.shake(TLAND, 0.5, 18)
def land_poof(cr, t, p, ly):
    if ly == "front" and TLAND <= t < TLAND + 0.8: L.draw_poof(cr, X0, FLOOR_Y - 40, (t - TLAND) / 0.8, r=200, sid=32)
S.blink(TLAND + 1.0)
S.set(TLAND + 0.9, "sit_floor", "dead_stare", dur=0.3, look=(0.0, 0.0))
S.stand(TLAND + 1.8, face="dead_stare")
S.t = TLAND + 2.7
S.camera(S.t - 0.6, X0, 930, 1.15, 0.6)

T_ASK = S.t
S.the_ask(T_ASK, hold=8.0)

# ---------------------------------------------------------------- draw order + hooks
S.props.insert(1, wrappers_back)
for f in (belly, pile, wrappers_front, falling, held, flying_wrappers, pop_fx, launch_poof, land_poof): S.prop(f)
S.prop(jet)
for h in (eat_hook, gulps, belly_arms, flight): S.hook(h)

if __name__ == "__main__":
    S.render("day005.mp4")
