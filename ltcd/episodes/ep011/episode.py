"""Day 11 - COMMENT episode: @angela.tgz "Build a cat shelter and be happy about it" (Instagram, day 10 reel, 2 likes).
He lives in Mordor now (ruins of the eye tower, the eagle at his left, the burnt-out eyeball at his right). See BEATS.md.

KITTEN   A tiny black kitten pads in through the ash and sits at his feet. He reads the comment.
GRIN     "Be happy": a huge dead-eyed toothy grin. The kitten puffs up, hisses, hops back. Grin off.
BUILD    Hammer from his hip. Build cloud with the tower chunk -> a little stone CAT SHELTER. The kitten moves in.
         Stiff thumbs-up, small stiff smile.
FLOOD    Rumble. Cut: the black gate (ONE DOES NOT SIMPLY WALK INTO MORDOR) opens and cats simply walk in; one sits
         on the sign. Cut: the wave rolls at him (heartbeat), forced smile, sweat.
BURIED   Buried to the neck in cats; cats loaf on the eagle; cats stack on his head, faster and faster, his smile
         wider and twitchier; the little shelter bulges with cats.
BURST    Creak. The shelter bursts; every cat lands on its feet. Rows of cats stare at him.
TOWER    He runs at the tower stump: a GIANT build cloud (the eyeball rolls in, cats get flung out, land on feet).
         POP: a giant CAT TOWER. Cats leap up and fill it. The kitten climbs to the top, between the horns.
EYE      Close: the kitten's glowing slit-pupil eyes where the Eye was. Slow blink. He slow-blinks back... a real smile.
BUTTON   The kitten nudges the eyeball off the ledge, staring at him. It falls. BONK. He gets up, smile stuck on.
ASK      The ask at the foot of the cat tower, smiling with dead eyes.
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import ramp, pulse, lerp, FLOOR_Y
from ink import smooth, back_out
import numpy as np

FR = 1 / 30
# ---------------------------------------------------------------- places (from day 10)
SX0 = 31160.0                              # body offset: he stands at x 31700
X0 = 540 + SX0
TX, TH = 32600.0, 1330.0                   # the (ruined) eye tower -> the cat tower
VX, VH, VW = 34200.0, 3600.0, 3400.0
GATE_X = 27600.0
EAGLE_X = 31180.0
CHUNK_X = 31960.0
EYEB = (32220.0, FLOOR_Y - 150)            # the burnt-out eyeball
EYE_R = 150
SH_X = 31990.0                             # the little shelter (built from the chunk)
SXR = 31420.0                              # he ends up here (x 31960), under the tower's high ledge
XR = 540 + SXR
LEDGE = (TX + O.CAT_TOWER_LEDGE[0], FLOOR_Y + O.CAT_TOWER_LEDGE[1])   # (32130, 388)
KS = 0.7                                   # kitten scale

# ---------------------------------------------------------------- timeline
T_KSIT = 1.4
T_READ = 2.0
T_GRIN, T_HISS, T_GRIN_OFF = 4.15, 4.55, 5.6
T_PULL = 6.3
T_CLOUD0, T_CLOUD1 = 9.35, 12.25
T_KIN0, T_KIN1 = 12.9, 13.7
T_THUMB = 14.2
T_RUMBLE = 15.3
CUT_GATE = 16.4
T_DOORS = 16.6
T_SIGNCAT = 17.5
CUT_WAVE = 19.0
T_HIT = 21.0
STACK_T = [22.0, 22.9, 23.7, 24.4, 25.0, 25.5, 25.9]
T_CREAK = 27.0
T_BURST = 28.0
T_STARE = 29.6
T_RUN, T_RUN1 = 30.9, 31.4
CUT_BIG = 31.75
T_BIG0, T_BIG1 = 31.9, 36.0
T_CLIMB = 36.4
T_KCLIMB0, T_KCLIMB1 = 39.0, 40.2
CUT_TOP = 40.35
T_KBLINK = 40.95
CUT_HIM = 42.0
T_HBLINK = 42.35
T_JOY = 43.1
CUT_PUSH = 45.2
CUT_UNAWARE = 46.4
CUT_PUSH2 = 47.0
T_TIP = 47.3
CUT_FALL = 47.55
T_FALL0 = 47.45
T_BONK = T_FALL0 + math.sqrt(2 * ((EYEB[1]) - (LEDGE[1] - EYE_R)) / 2600)
T_ROLL0, T_ROLL1 = 49.0, 49.6
T_UP = 49.75
T_ASK = 50.9
ASK_HOLD = 8.0

S = M.Scene(x0=SX0)
S.auto_blinks = False
S.card("angela.tgz", "Build a cat shelter and be happy about it", "2", t0=0.3)
CAM0 = (X0 + 110, 1060, 1.05)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0

# ================================================================ the world
def ruins(cr, t):
    """the tower after the eye blew (day 10): a jagged smoking stump, rubble round the base."""
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

def gate_doors(cr, t):
    """the black gate's doors swing open (dark gap in the middle)."""
    if not (CUT_GATE - 0.1 <= t < CUT_WAVE): return
    u = smooth(ramp(t, T_DOORS, T_DOORS + 0.8))
    if u <= 0: return
    gw, gh, x, yb = 520, 820, GATE_X, FLOOR_Y
    L.sketch_rect(cr, x - gw, yb - gh, x + gw, yb, 7, sid=9915, fill=(0.05, 0.04, 0.05))
    for sx in (-1, 1):
        w = gw * (1 - 0.82 * u)
        x0 = x + sx * gw; x1 = x0 - sx * w
        L.sketch_rect(cr, min(x0, x1), yb - gh, max(x0, x1), yb, 7, sid=9916 + (sx > 0), fill=(0.22, 0.19, 0.20))
    sw, sh = 760, 230; cy = yb - gh - 60
    L.sketch_rect(cr, x - sw / 2, cy - sh / 2, x + sw / 2, cy + sh / 2, 6, sid=9912, fill=(0.80, 0.60, 0.36))
    L.draw_text(cr, "ONE DOES NOT SIMPLY WALK INTO MORDOR", x, cy, 64, max_w=sw - 60)
    for sx in (-1, 1):
        cr.arc(x + sx * (sw / 2 - 26), cy, 9, 0, 2 * math.pi); L.fill_ink(cr); cr.new_path()

def world(cr, t):
    O.draw_dark_land_world(cr, t, x0=24900, x1=45000, volcano=(VX, VH, VW), gate=GATE_X, tower=None)
    gate_doors(cr, t)
    if t < T_BIG1: ruins(cr, t)
    else: O.draw_cat_tower(cr, TX, FLOOR_Y, t)
S.background(world)

# ================================================================ the eagle (stays at his left)
def eagle(cr, t, p, ly):
    if ly != "back": return
    look, alarm = 0.8, 0.0
    if T_RUMBLE + 0.2 <= t < T_HIT: look, alarm = -0.8, smooth(ramp(t, T_RUMBLE + 0.2, T_RUMBLE + 0.5)) * 0.7
    elif T_HIT <= t < T_BURST: look, alarm = (0.8 if (t * 0.7) % 2 < 1 else 0.3), 0.25
    O.draw_eagle(cr, EAGLE_X, FLOOR_Y, t, flap=0.06, s=0.8, look=look, alarm=alarm, face=1)
S.prop(eagle)

# ================================================================ cats: who's where, when
rng = random.Random(11)
V = 1000.0                                 # the flood runs at 1000 px/s
def cat_col(i): return O.CAT_KINDS[(i * 5 + 1) % len(O.CAT_KINDS)]

# pile slots around him (a mound up to his neck), the eagle's back, the shelter door
PILE = []
for row, (n, hw) in enumerate(((7, 380), (6, 330), (5, 270), (4, 210), (3, 150), (2, 90))):
    for k in range(n):
        x = X0 + (k - (n - 1) / 2) * (2 * hw / max(1, n - 1)) * 0.95 + rng.uniform(-15, 15)
        PILE.append(dict(x=x, y=FLOOR_Y - row * 118 + rng.uniform(-8, 8), kind="loaf" if (k + row) % 3 else "sit",
                         s=0.78 + rng.uniform(-0.05, 0.05), row=row))
EAGLE_SLOTS = [dict(x=EAGLE_X - 110, y=1130, kind="loaf", s=0.6), dict(x=EAGLE_X + 40, y=1125, kind="loaf", s=0.6),
               dict(x=EAGLE_X + 152, y=1050, kind="loaf", s=0.5)]
N_SHELTER = 7
CATS = []                                   # every flood cat: dict(ti, dest, kind of destination, slot)
order = [("eagle", s_) for s_ in EAGLE_SLOTS] + [("pile", s_) for s_ in PILE] + [("shelter", None) for _ in range(N_SHELTER)]
rng.shuffle(order)
order.sort(key=lambda o: (o[1]["x"] if o[1] else SH_X) + rng.uniform(-500, 500))   # nearer slots fill first, roughly
for i, (where, slot) in enumerate(order):
    ti = 16.9 + i * (2.0 / len(order)) + rng.uniform(-0.02, 0.02)
    dest = slot["x"] if slot else SH_X
    if where == "pile": dest = X0 - 420 + (slot["x"] - X0) * 0.15          # runners vanish into the edge of the mound
    if where == "eagle": dest = EAGLE_X - 200
    arr = ti + (dest - GATE_X) / V
    CATS.append(dict(i=i, ti=ti, dest=dest, arr=max(arr, T_HIT if where == "pile" else arr), where=where, slot=slot,
                     lane=rng.uniform(-20, 40), s=rng.uniform(0.62, 0.8), col=cat_col(i)))
for c in CATS:
    if c["where"] == "pile": c["arr"] = max(c["arr"], T_HIT + 0.05 * c["slot"]["row"] + rng.uniform(0, 0.25) + 0.35 * c["slot"]["row"])
SHELTER_ARR = sorted(c["arr"] for c in CATS if c["where"] == "shelter")

# where everything lands after the burst (on its feet), and who climbs the tower later
LAND = []
for r_, (y, x0_, x1_) in enumerate(((FLOOR_Y + 70, 30700, 31560), (FLOOR_Y + 20, 30760, 31520), (FLOOR_Y + 110, 30650, 31580),
                                    (FLOOR_Y + 60, 31820, 32020))):
    n = int((x1_ - x0_) // 105) + 1
    for k in range(n): LAND.append((x0_ + k * (x1_ - x0_) / max(1, n - 1) + rng.uniform(-20, 20), y))
rng.shuffle(LAND)
KITTEN_LAND = (31430.0, FLOOR_Y + 30)
STACK = [dict(col=cat_col(40 + k), s=0.62) for k in range(len(STACK_T))]
FLYERS = []                                 # (start fn, land xy, col, scale, t0, dur)
li = 0
def _add_flyer(start, col, s):
    global li
    land = LAND[li % len(LAND)] if li < len(LAND) else (30400 - 120 * (li - len(LAND)), FLOOR_Y + 60)
    li += 1
    FLYERS.append(dict(start=start, land=land, col=col, s=s, t0=T_BURST + rng.uniform(0.0, 0.12), dur=rng.uniform(0.7, 1.15)))
for c in CATS:
    if c["where"] == "shelter": _add_flyer((SH_X + rng.uniform(-120, 120), FLOOR_Y - 150), c["col"], 0.62)
    else: _add_flyer((c["slot"]["x"], c["slot"]["y"]), c["col"], c["slot"]["s"] * 0.85)
for k, st in enumerate(STACK): _add_flyer(("stack", k), st["col"], st["s"])
# the climbers: the flyers that land nearest the tower take the tower seats (seat 0, the top, is the kitten's)
SEATS = O.cat_tower_spots(TX, FLOOR_Y)
by_near = sorted(range(len(FLYERS)), key=lambda i: -FLYERS[i]["land"][0])
for n, i in enumerate(by_near[:len(SEATS) - 1]):
    FLYERS[i]["seat"] = SEATS[n + 1]; FLYERS[i]["climb"] = T_CLIMB + n * 0.14
FLUNG = [dict(t0=33.4, start=(32100, 700), land=(31560, FLOOR_Y + 40), col="white"),
         dict(t0=34.6, start=(32150, 500), land=(31380, FLOOR_Y + 100), col="orange")]

def arc(a, b, u, h=260):
    u = max(0.0, min(1.0, u))
    return (lerp(a[0], b[0], u), lerp(a[1], b[1], u) - h * 4 * u * (1 - u))

def stack_xy(k, t, p):
    hx, hy = p["head"]
    sway = sum(math.sin(t * 2.4 + j * 0.5) * 6 * j for j in range(k + 1)) * ramp(t, STACK_T[0], STACK_T[-1])
    return (hx + sway, hy - 112 - k * 82)

def kitten_state(t, p):
    """(x, yb, kind, look, blink, puff, hiss, glow, alpha, face) or None"""
    if t < T_KSIT:                                                # pads in from the right
        u = t / T_KSIT
        return (lerp(32480, 31880, u), FLOOR_Y + 10, "walk", (0, 0), 0, 0, 0, 0, 1, -1, u * 9)
    if t < T_HISS:
        lk = (-0.6, -1.0) if t < 3.8 else (-0.4, -1.0)
        return (31880, FLOOR_Y + 10, "sit", lk, pulse(t, 2.9, 0.08) * 0, 0, 0, 0, 1, 1, 0)
    if t < T_GRIN_OFF + 0.3:                                      # puffs up, hisses, hops back
        u = ramp(t, T_HISS + 0.15, T_HISS + 0.55, "linear")
        x, y = arc((31880, FLOOR_Y + 10), (32460, FLOOR_Y + 30), u, 120)
        pf = min(1.0, (t - T_HISS) / 0.12)
        return (x, y, "puff", (0, 0), 0, pf, pf, 0, 1, -1, 0)
    if t < T_KIN0:
        return (32460, FLOOR_Y + 30, "sit", (-0.8, -0.2), 0, 0, 0, 0, 1, 1, 0)
    if t < T_KIN1 + 0.25:                                         # trots into the shelter
        u = ramp(t, T_KIN0, T_KIN1, "linear")
        return (lerp(32460, SH_X, u), FLOOR_Y + 30 - 30 * u, "walk", (0, 0), 0, 0, 0, 0, 1 - ramp(t, T_KIN1 - 0.1, T_KIN1 + 0.2), -1, u * 8)
    if t < T_BURST: return None
    if t < T_BURST + 1.0:                                         # blown out with the rest; lands on its feet
        u = (t - T_BURST) / 0.95
        x, y = arc((SH_X, FLOOR_Y - 120), KITTEN_LAND, u, 700)
        return (x, y, "fall" if u < 0.85 else "sit", (0.3, 0), 0, 0, 0, 0, 1, 1, 0)
    if t < T_KCLIMB0:
        return (KITTEN_LAND[0], KITTEN_LAND[1], "sit", (0.8 if t < 36 else 0.6, -0.3 if t > 36 else 0), 0, 0, 0, 0, 1, 1, 0)
    path_ = [KITTEN_LAND, (TX - 250, FLOOR_Y - 120), (TX - 250, FLOOR_Y - 380), (TX - 240, FLOOR_Y - 790), (TX, FLOOR_Y - 1190)]
    if t < T_KCLIMB1:
        u = (t - T_KCLIMB0) / (T_KCLIMB1 - T_KCLIMB0) * (len(path_) - 1)
        k = min(int(u), len(path_) - 2)
        x, y = arc(path_[k], path_[k + 1], u - k, 160)
        return (x, y, "fall", (0, -0.5), 0, 0, 0, 0, 1, 1, 0)
    if t < 44.9:
        glow = smooth(ramp(t, CUT_TOP, CUT_TOP + 0.5))
        bl = 0.0
        if T_KBLINK <= t < T_KBLINK + 0.8: bl = math.sin(math.pi * (t - T_KBLINK) / 0.8)
        lk = (0.0, 0.0) if t < CUT_HIM else (-0.4, 0.9)
        return (TX, FLOOR_Y - 1190, "sit", lk, bl, 0, 0, glow if t < CUT_HIM + 0.5 else glow * (1 - ramp(t, CUT_HIM, CUT_HIM + 1.0)), 1, 1, 0)
    # on the ledge's arm, right of the eyeball: looks at it, at him, nudges, pushes
    x, y = LEDGE[0] + 200, LEDGE[1] + 34
    lk = (-1.0, 0.2)
    if CUT_PUSH + 0.6 <= t < CUT_PUSH + 1.0: lk = (-0.3, 1.0)        # down at him
    if t >= CUT_PUSH2: lk = (-0.3, 1.0) if t < T_TIP + 0.4 else (-0.2, 1.0)
    return (x, y, "sit", lk, 0, 0, 0, 0, 1, 1, 0)

NUDGES = [CUT_PUSH + 1.1, CUT_PUSH + 1.55, CUT_PUSH2 + 0.1]
def eyeball_x(t):
    """the eyeball's x on the ledge after the build: each nudge shoves it a little left."""
    x = LEDGE[0]
    for k, tn in enumerate(NUDGES):
        x -= (25 if k < 2 else 150) * smooth(ramp(t, tn, tn + 0.18))
    return x

def cats(cr, t, p, ly):
    if ly != "front": return
    # the kitten
    ks = kitten_state(t, p)
    if ks:
        x, y, kind, lk, bl, pf, hs, gl, al, face, ph = ks
        if gl > 0.02:                                             # the new Eye: a ring of fire round the kitten
            hx, hy = x, y - 146 * KS
            for k in range(10):
                a = 2 * math.pi * k / 10 + 0.3
                bx, by = hx + math.cos(a) * 70, hy + math.sin(a) * 62
                Lf = (60 + 25 * math.sin(t * 9 + k * 2.1)) * gl
                O.draw_flames(cr, [(bx + math.cos(a) * Lf * i / 5, by + math.sin(a) * Lf * i / 5) for i in range(6)], t + k, w=30 * gl)
        if al > 0.02:
            O.draw_cat(cr, x, y, s=KS, t=t, kind=kind, col="black", face=face, look=lk, blink=bl, puff=pf, hiss=hs, glow=gl,
                       sid=2000, alpha=al, phase=ph)
        if t >= CUT_PUSH and t < T_TIP + 0.3:                     # its paw reaching for the eyeball
            for tn in NUDGES:
                k = pulse(t, tn + 0.05, 0.12)
                if k > 0.05:
                    sx, sy = x - 30, y - 50
                    ex = lerp(sx, eyeball_x(t) + EYE_R - 5, k)
                    L.sketch_line(cr, [(sx, sy), (ex, sy - 10 * k)], 16, sid=2100)
                    L.sketch_ellipse(cr, ex, sy - 10 * k, 16, 12, 4, sid=2101, fill=O.CAT_COLS["black"][0])
    # the flood: runners
    if T_DOORS < t < 24.0:
        for c in CATS:
            if not (c["ti"] <= t < c["arr"]): continue
            x = GATE_X + V * (t - c["ti"])
            if x > c["dest"]: continue
            O.draw_cat(cr, x, FLOOR_Y + c["lane"], s=c["s"], t=t, kind="run", col=c["col"], face=1, phase=(t - c["ti"]) * 22 + c["i"],
                       sid=3000 + 40 * (c["i"] % 20), swish=0.3)
    # the cat on the sign
    if CUT_GATE <= t < CUT_WAVE and t >= T_SIGNCAT - 0.6:
        a, b = (GATE_X + 120, FLOOR_Y), (GATE_X + 250, FLOOR_Y - 820 - 60 - 115)
        u = ramp(t, T_SIGNCAT, T_SIGNCAT + 0.4, "linear")
        if t < T_SIGNCAT:
            x0_ = GATE_X + V * (t - T_SIGNCAT + 0.12)
            O.draw_cat(cr, min(a[0], x0_), FLOOR_Y, s=0.75, t=t, kind="run", col="grey", face=1, phase=t * 22, sid=2500)
        else:
            x, y = arc(a, b, u, 200)
            O.draw_cat(cr, x, y, s=0.75, t=t, kind="fall" if u < 1 else "sit", col="grey", look=(0.0, 0.4), sid=2500)
    # piled up: mound, eagle, head stack (before the burst)
    if T_HIT - 0.2 <= t < T_BURST:
        for c in sorted((c for c in CATS if c["where"] in ("pile", "eagle")), key=lambda c: (-c["slot"]["row"] if "row" in c["slot"] else 0)):
            if t < c["arr"]: continue
            sl = c["slot"]; pop = min(1.0, (t - c["arr"]) / 0.15)
            lk = (math.sin(t * 0.8 + c["i"]) * 0.6, 0.2 * math.sin(t * 0.5 + c["i"] * 2))
            O.draw_cat(cr, sl["x"], sl["y"] + 30 * (1 - pop), s=sl["s"] * (0.6 + 0.4 * pop), t=t, kind=sl["kind"], col=c["col"],
                       look=lk, sid=3000 + 40 * (c["i"] % 20), blink=1.0 if (t + c["i"] * 0.7) % 3.1 < 0.12 else 0.0)
        for k, tk in enumerate(STACK_T):
            if t < tk - 0.3: continue
            hx, hy = stack_xy(k, t, p)
            u = min(1.0, (t - tk + 0.3) / 0.3)
            y = lerp(hy - 700, hy, u * u)
            O.draw_cat(cr, hx, y, s=STACK[k]["s"], t=t, kind="loaf" if u >= 1 else "fall", col=STACK[k]["col"],
                       look=(0.0, 0.5 if k == 0 else 0.0), sid=4000 + 40 * k)
    # the burst: everyone flies out and lands on their feet; later the climbers take the tower
    if t >= T_BURST:
        for i, f in enumerate(FLYERS):
            st = f["start"]
            if st[0] == "stack":
                st = (X0 + 30 * st[1] * math.sin(st[1]), 640 - 112 - st[1] * 82)
            u = (t - f["t0"]) / f["dur"]
            look = ((1 if X0 > f["land"][0] else -1) * 0.7, -0.1)
            if t >= T_STARE + 1.0 and t < T_BIG1: look = (0.8, -0.2)                   # watching the cloud
            if t >= T_BIG1: look = (0.7, -0.5)
            if "climb" in f and t >= f["climb"]:
                v = (t - f["climb"]) / 0.9
                x, y = arc(f["land"], f["seat"], v, 300)
                kind = "fall" if v < 1 else ("loaf" if i % 3 == 0 else "sit")
                look = (0.0, 0.2) if v >= 1 else look
            elif u < 0:
                continue
            else:
                x, y = arc(st, f["land"], u, 600)
                kind = "fall" if u < 1 else ("sit" if i % 4 else "loaf")
                if T_BIG0 <= t < T_BIG1 and abs(x - TX) < 1000 and x > XR - 60: continue      # (inside the big cloud's footprint: hidden by it)
            sp = 0.03 if (kind != "fall" and t < 45) else 0.0
            O.draw_cat(cr, x, y, s=f["s"], t=t, kind=kind, col=f["col"], look=look, sid=5000 + 40 * (i % 25),
                       tilt=(t * 9 + i) if kind == "fall" and "climb" not in f else 0.0,
                       blink=1.0 if (t + i * 0.37) % 3.7 < 0.12 else (sp * 0))
    for f in FLUNG:
        if t < f["t0"]: continue
        u = (t - f["t0"]) / 0.9
        x, y = arc(f["start"], f["land"], u, 500)
        O.draw_cat(cr, x, y, s=0.7, t=t, kind="fall" if u < 1 else "sit", col=f["col"], look=(0.8, -0.3), sid=5900,
                   tilt=t * 10 if u < 1 else 0.0)
S.prop(cats)

# ================================================================ props: chunk, shelter, rubble, eyeball, clouds
def things(cr, t, p, ly):
    if ly == "back":
        if t < T_CLOUD0 + 0.2:                                    # the tower chunk (day 10)
            L.sketch_rect(cr, CHUNK_X - 80, FLOOR_Y - 140, CHUNK_X + 80, FLOOR_Y, 5, sid=7830, fill=(0.12, 0.10, 0.11))
        if T_BIG1 > t:                                            # the eyeball, until it rolls into the big cloud
            if t < T_BIG0 + 0.3: ex = EYEB[0]
            else: ex = lerp(EYEB[0], EYEB[0] + 500, smooth(ramp(t, T_BIG0 + 0.3, T_BIG0 + 1.0)))
            draw_eyeball(cr, ex, EYEB[1], ang=-(ex - EYEB[0]) / EYE_R, t=t)
        if T_CLOUD1 - 0.1 <= t < T_BURST:                         # the little shelter
            heads = sum(1 for a in SHELTER_ARR if t >= a)
            bulge = min(1.0, heads / N_SHELTER) * 0.7 + 0.3 * ramp(t, T_CREAK, T_BURST)
            s = back_out(min(1.0, (t - T_CLOUD1 + 0.1) / 0.3), 1.8)
            if heads == 0: bulge = 0.0
            O.draw_cat_shelter(cr, SH_X, FLOOR_Y, t, bulge=bulge, heads=heads, s=max(0.05, s))
        if t >= T_BURST:                                          # its rubble stays
            for i, (dx, r) in enumerate(((-120, 50), (-40, 34), (60, 46), (140, 30), (10, 26))):
                L.sketch_poly(cr, [(SH_X + dx - r, FLOOR_Y + 4), (SH_X + dx - r * 0.6, FLOOR_Y - r * 0.9), (SH_X + dx + r * 0.5, FLOOR_Y - r),
                                   (SH_X + dx + r, FLOOR_Y + 4)], 4, sid=8800 + i, fill=(0.24, 0.21, 0.22))
            L.sketch_rect(cr, SH_X - 100, FLOOR_Y - 34, SH_X + 60, FLOOR_Y - 4, 4, sid=8810, fill=(0.85, 0.66, 0.40))   # the plank sign
        if t >= T_BIG1 and t < T_TIP:                             # the eyeball on the tower's high ledge
            draw_eyeball(cr, eyeball_x(t), LEDGE[1] - EYE_R + 4, ang=-(eyeball_x(t) - LEDGE[0]) / EYE_R, t=t)
    else:
        if T_CLOUD0 <= t < T_CLOUD1:
            O.draw_build_cloud(cr, (X0 + SH_X) / 2 - 20, 1130, t, T_CLOUD0, T_CLOUD1 - T_CLOUD0, r=440)
        if T_BIG0 <= t < T_BIG1:
            O.draw_build_cloud(cr, TX - 60, 820, t, T_BIG0, T_BIG1 - T_BIG0, r=1080)
            if t < T_BIG0 + 0.6: pass
        if T_BURST <= t < T_BURST + 0.9:                          # the burst: flying stones
            u = (t - T_BURST) / 0.9
            L.draw_impact(cr, SH_X, FLOOR_Y - 200, min(1.0, u * 3), r=420, sid=88)
            for i in range(10):
                a = -math.pi * (0.1 + 0.8 * i / 9)
                x = SH_X + math.cos(a) * 1300 * u; y = FLOOR_Y - 200 + math.sin(a) * 1300 * u + 1800 * u * u
                L.sketch_rect(cr, x - 30, y - 22, x + 30, y + 22, 4, sid=8820 + i, fill=(0.24, 0.21, 0.22))
        if T_BIG1 <= t < T_BIG1 + 0.35:
            L.burst_lines(cr, TX, 700, (t - T_BIG1) / 0.35, r0=700, r1=1100, n=14, sid=89)
        if T_CLOUD1 <= t < T_CLOUD1 + 0.3:
            L.burst_lines(cr, SH_X, FLOOR_Y - 220, (t - T_CLOUD1) / 0.3, r0=220, r1=380, n=10, sid=90)
        if T_TIP <= t < T_ROLL1 + 3000:                           # the eyeball falls... onto him, then rolls off
            if t < T_BONK:
                s_ = max(0.0, t - T_FALL0)
                ex, ey = LEDGE[0] - 175, LEDGE[1] - EYE_R + 0.5 * 2600 * s_ * s_
                if t < T_FALL0: ex, ey = eyeball_x(t), LEDGE[1] - EYE_R + 4
                draw_eyeball(cr, ex, min(ey, EYEB[1]), ang=t * 3, t=t)
            else:
                u = smooth(ramp(t, T_ROLL0, T_ROLL1))
                ex = lerp(XR, XR - 330, u)
                draw_eyeball(cr, ex, EYEB[1], ang=-(ex - XR) / EYE_R + 1.0, t=t)
            if T_BONK <= t < T_BONK + 0.6:
                L.draw_impact(cr, XR, FLOOR_Y - 320, (t - T_BONK) / 0.6, r=170, sid=91)
            if T_FALL0 <= t < T_BONK:                             # its shadow on the ground, growing
                k = ramp(t, T_FALL0, T_BONK)
                cr.save(); cr.translate(XR, FLOOR_Y + 6); cr.scale(1.0, 0.18); cr.arc(0, 0, 40 + 120 * k, 0, 2 * math.pi); cr.restore()
                cr.set_source_rgba(0, 0, 0, 0.25 + 0.3 * k); cr.fill()
S.prop(things)

def draw_eyeball(cr, x, y, ang=0.0, t=0.0):
    L.sketch_circle(cr, x, y, EYE_R, 6, sid=7840, fill=(0.62, 0.48, 0.30))
    cr.save(); cr.translate(x, y); cr.rotate(ang)
    cr.save(); cr.scale(0.22, 1.0); cr.arc(0, 0, 110, 0, 2 * math.pi); cr.restore(); cr.set_source_rgb(0.2, 0.15, 0.12); cr.fill()
    for q in ([(-120, -40), (-60, -10), (-30, 40)], [(60, -110), (90, -50), (130, -30)]):
        L.sketch_line(cr, q, 4, sid=7841)
    cr.restore()

# ================================================================ HIM
S.set(0.0, "stand", "dead_stare", dur=0.0)
S.set(0.55, "stand", "dead_stare", dur=0.35, look=(0.5, 0.9), tilt=0.05)                 # the kitten
S.set(1.5, "stand", "dead_stare", dur=0.3, look=(0.3, 0.95), tilt=0.07)
S.read_card(T_READ, react="dead_stare", lines=2, dur=1.7, face="deadpan")
S.set(3.95, "stand", "dead_stare", dur=0.3, look=(0.35, 0.95), tilt=0.06)                 # the kitten again
# "be happy": the grin
S.set(T_GRIN, "stand", "dead_stare", dur=0.35, mouth="teeth", smile=1.0, open=0.35, mouth_w=1.5, look=(0.35, 0.95), eyescale=1.08, lid=0.22, tilt=0.06)
S.set(T_HISS + 0.3, "stand", "dead_stare", dur=0.2, mouth="teeth", smile=1.0, open=0.35, mouth_w=1.5, look=(0.6, 0.85), eyescale=1.08, lid=0.22, twitch=0.6)
S.set(T_GRIN_OFF, "stand", "dead_stare", dur=0.2, look=(0.6, 0.8))
S.set(T_GRIN_OFF + 0.35, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0))                 # us
S.blink(T_GRIN_OFF + 0.6)

def hammer(cr, x, y, s, t, p):
    if T_CLOUD0 + 0.15 <= t < T_CLOUD1 - 0.05: return
    O.draw_hammer(cr, x, y, s=0.9 * s, ang=0.15)
_k0 = len(S.keys)
S.pocket_pull(T_PULL, "hammer", hammer, (0, 0), held=True, offset=(0, 10), narrow_w=0)
for i in range(_k0, len(S.keys)):                                 # keep the pull deadpan
    k = S.keys[i]; d = dict(k[1]); d.update(L.EXPR["deadpan"]); d["open"] = 0.0; d["eyescale"] = 1.0
    S.keys[i] = (k[0], d) + tuple(k[2:])
S.set(S.t, "stand", "deadpan", dur=0.25, look=(0.7, 0.5))                                 # the chunk
# into the build cloud
S.set(T_CLOUD0 - 0.25, "crouch", "deadpan", dur=0.15, look=(0.7, 0.5))
S._hop(T_CLOUD0 - 0.05, 60, 0.1)
S.set(T_CLOUD0 + 0.15, "stand", "deadpan", dur=0.0, show=0.0)
for k in range(9):
    S.sfx(T_CLOUD0 + 0.3 + k * 0.29, ("clack", "tok", "bonk")[k % 3], (0.05, 0.04, 0.05)[k % 3])
S.sfx(T_CLOUD0, "poof", 0.12)
S.set(T_CLOUD1 - 0.05, "stand", "deadpan", dur=0.0, show=1.0, sweat=0.5, look=(0.7, 0.3))
S.sfx(T_CLOUD1, "pop", 0.12)
S.set(T_CLOUD1 + 0.6, "stand", "deadpan", dur=0.3, look=(0.0, 0.0), sweat=0.4)            # us
S.set(T_KIN0 + 0.1, "stand", "deadpan", dur=0.3, look=(0.8, 0.6), sweat=0.3)              # the kitten goes in
L.POSES["thumbs_l"] = dict(lelb=(425, 905), lhand=(392, 800), lhand_t="thumbs")
S.set(T_THUMB, "thumbs_l", "dead_stare", dur=0.25, ease="back", look=(0.0, 0.0), mouth="auto", smile=0.45, twitch=0.4)
S.set(T_THUMB + 1.0, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0))
# rumble: they're coming
S.set(T_RUMBLE + 0.4, "stand", "dead_stare", dur=0.25, look=(-0.9, 0.0))                  # eyes first
S.set(T_RUMBLE + 0.65, "stand", "dead_stare", dur=0.35, look=(-0.9, 0.0), turn=-0.5, tilt=-0.04)
for i in range(5): S.shake(T_RUMBLE + 0.2 * i, 0.3, 2 + i)
S.sfx(T_RUMBLE, "kaboom", 0.05, dur=2.6)

# ================================================================ cut: the gate
S.cut(CUT_GATE - FR, cam=(GATE_X + 180, 1000, 0.82))
S.camera(CUT_GATE, GATE_X + 200, 1005, 0.86, CUT_WAVE - CUT_GATE, ease="linear")
S.sfx(T_DOORS, "squeak", 0.05); S.sfx(T_DOORS + 0.1, "kaboom", 0.06, dur=1.5)
S.sfx(T_SIGNCAT + 0.4, "tok", 0.05)

# ================================================================ cut: the wave rolls in
S.cut(CUT_WAVE - FR, cam=(X0 - 520, 960, 0.55))
S.camera(CUT_WAVE, X0 - 300, 900, 0.6, T_HIT - CUT_WAVE, ease="inn")
S.set(CUT_WAVE - FR, "stand", "dead_stare", dur=0.0, look=(-0.9, 0.0), turn=-0.5, tilt=-0.04)
S.set(CUT_WAVE + 0.5, "stand", "dead_stare", dur=0.6, look=(-0.9, 0.0), turn=-0.5, mouth="auto", smile=0.7, sweat=0.6, quiver=0.4)
S.set(T_HIT - 0.4, "stand", "dead_stare", dur=0.3, look=(-0.6, 0.0), turn=-0.2, mouth="auto", smile=0.75, sweat=1.0, quiver=0.7, eyescale=1.1)
for k in range(9):                                                # heartbeat
    tk = CUT_WAVE + 0.1 + k * (0.3 - 0.012 * k)
    S.sfx(tk, "thud", 0.05 + 0.006 * k); S.sfx(tk + 0.14, "thud", 0.035 + 0.004 * k)
S.sfx(CUT_WAVE + 0.4, "rain", 0.05, dur=T_HIT - CUT_WAVE)          # a thousand little paws
S.sfx(T_HIT, "thud", 0.16); S.shake(T_HIT, 0.4, 12)

# ================================================================ buried: the stack, the smile
CAM_PILE = (X0 + 50, 800, 0.62)
S.camera(T_HIT + 0.3, *CAM_PILE, dur=0.5)
S.camera(T_HIT + 1.2, X0 + 60, 760, 0.57, dur=T_CREAK - T_HIT - 1.2, ease="linear")
S.set(T_HIT + 0.1, "stand", "dead_stare", dur=0.15, ease="snap", look=(0.0, 0.0), mouth="auto", smile=0.6, sweat=0.9, eyescale=1.12)
for k, tk in enumerate(STACK_T):
    sm = min(1.0, 0.65 + 0.06 * k)
    S.sfx(tk, "tok", 0.05 + 0.005 * k)
    S.set(tk + 0.05, "stand", "dead_stare", dur=0.08, ease="snap", stretch=-0.06, look=(0.0, -0.4), mouth="auto", smile=sm,
          mouth_w=1.0 + 0.11 * k, twitch=0.2 + 0.1 * k, sweat=0.9, lid=0.25)
    S.set(tk + 0.25, "stand", "dead_stare", dur=0.2, look=(0.0, 0.0), mouth="auto", smile=sm, mouth_w=1.0 + 0.11 * k,
          twitch=0.2 + 0.1 * k, sweat=0.9, lid=0.25)
S.set(T_CREAK, "stand", "dead_stare", dur=0.2, look=(0.9, 0.5), mouth="auto", smile=1.0, mouth_w=1.9, twitch=1.0, sweat=1.0)   # the shelter
S.set(T_CREAK + 0.35, "stand", "dead_stare", dur=0.3, look=(0.9, 0.5), turn=0.4, mouth="auto", smile=1.0, mouth_w=1.9, twitch=1.0, sweat=1.0)
S.sfx(T_CREAK, "squeak", 0.04); S.sfx(T_CREAK + 0.5, "squeak", 0.05)
for i in range(4): S.shake(T_CREAK + 0.25 * i, 0.25, 2 + 2 * i)
for k in range(N_SHELTER): S.sfx(SHELTER_ARR[k], "pop", 0.03)

# ================================================================ BURST
S.flash(T_BURST, 0.4)
S.sfx(T_BURST, "kaboom", 0.42, dur=2.6); S.shake(T_BURST, 0.8, 26)
S.camera(T_BURST, X0 - 150, 930, 0.5, 0.35, ease="out")
S.set(T_BURST, "stand", "dead_stare", dur=0.06, ease="snap", look=(0.9, 0.4), eyescale=1.2, mouth="auto", smile=1.0, mouth_w=1.9, lid=0.0)
for k in range(14): S.sfx(T_BURST + 0.75 + k * 0.045, "tok", 0.025)          # cats landing on their feet
S.set(T_BURST + 1.2, "stand", "dead_stare", dur=0.3, look=(-0.6, 0.2), mouth="auto", smile=0.9, mouth_w=1.6)       # rows of cats
S.camera(T_STARE - 0.3, X0 - 250, 1000, 0.62, 1.2)
S.set(T_STARE, "stand", "dead_stare", dur=0.35, look=(-0.6, 0.2))                       # smile drops
S.set(T_STARE + 0.4, "stand", "dead_stare", dur=0.25, look=(0.9, -0.3))                 # the stump (eyes first)
S.set(T_STARE + 0.75, "stand", "dead_stare", dur=0.35, look=(0.9, -0.4), turn=0.4, tilt=0.03)
# runs at the stump, leaps into the giant cloud
S.run_to(T_RUN, SXR, T_RUN1 - T_RUN)
S.camera(T_RUN, XR + 200, 950, 0.58, 0.5)
S.cut(CUT_BIG - FR, cam=(TX - 250, 720, 0.47))
S.set(CUT_BIG - FR, "crouch", "deadpan", dur=0.0, look=(0.8, -0.5))
S._hop(T_BIG0 - 0.1, 120, 0.12)
S.set(T_BIG0 + 0.15, "stand", "deadpan", dur=0.0, show=0.0)
S.hide("hammer", T_BIG0 + 0.15)
S.sfx(T_BIG0, "poof", 0.15)
for k in range(12):
    S.sfx(T_BIG0 + 0.25 + k * 0.31, ("clack", "bonk", "tok")[k % 3], 0.05)
for f in FLUNG: S.sfx(f["t0"], "whoosh", 0.04); S.sfx(f["t0"] + 0.9, "tok", 0.05)
S.sfx(T_BIG0 + 0.4, "rummage", 0.03, dur=0.6)

# ================================================================ the cat tower
S.set(T_BIG1 - 0.05, "stand", "dead_stare", dur=0.0, show=1.0, look=(0.7, -0.9), sweat=0.5, tilt=-0.05)
S.sfx(T_BIG1, "pop", 0.18); S.shake(T_BIG1, 0.3, 8)
S.camera(T_BIG1, TX - 200, 740, 0.48, 3.0, ease="linear")
for n in range(len(SEATS) - 1): S.sfx(T_CLIMB + n * 0.14 + 0.85, "tok", 0.025)
S.set(T_CLIMB + 1.5, "stand", "dead_stare", dur=0.4, look=(0.6, -1.0), tilt=-0.08, sweat=0.3)
S.set(T_KCLIMB0 + 0.2, "stand", "dead_stare", dur=0.4, look=(-0.6, 0.6), sweat=0.2)      # the kitten goes by
S.set(T_KCLIMB0 + 0.7, "stand", "dead_stare", dur=0.5, look=(0.6, -1.0), tilt=-0.1)       # ...up to the top
S.camera(T_KCLIMB0, TX - 150, 600, 0.52, T_KCLIMB1 - T_KCLIMB0)
for k in range(4): S.sfx(T_KCLIMB0 + 0.3 * k + 0.2, "tok", 0.03)

# ================================================================ the new Eye. slow blink. a real smile.
KHEAD = (TX, FLOOR_Y - 1190 - 146 * KS)
S.cut(CUT_TOP - FR, cam=(KHEAD[0], KHEAD[1] + 60, 2.3))
S.camera(CUT_TOP, KHEAD[0], KHEAD[1] + 40, 2.6, CUT_HIM - CUT_TOP, ease="linear")
S.sfx(CUT_TOP, "whine", 0.03, dur=1.6)
S.cut(CUT_HIM - FR, cam=(XR + 40, 690, 1.25))
S.camera(CUT_HIM, XR + 40, 700, 1.32, CUT_PUSH - CUT_HIM, ease="linear")
S.set(CUT_HIM - FR, "stand", "dead_stare", dur=0.0, look=(0.3, -1.0), tilt=-0.1)
S.set(T_HBLINK, "stand", "dead_stare", dur=0.3, look=(0.3, -1.0), tilt=-0.1, lid=1.0)             # slow blink back
S.set(T_HBLINK + 0.55, "stand", "dead_stare", dur=0.3, look=(0.3, -1.0), tilt=-0.1, lid=0.3)
S.set(T_JOY, "stand", "dead_stare", dur=0.6, look=(0.2, -0.9), tilt=-0.08, smile=0.5, mouth="auto", brow=0.3)
S.set(T_JOY + 0.6, "stand", "delighted", dur=0.5, ease="back", blush=0.0, tilt=-0.1, look=(0.2, -0.6))   # it cracks
S.sfx(T_JOY + 0.6, "twinkle", 0.04)
for i in range(6): S.shake(T_JOY + 0.3 * i, 0.4, 2)

# ================================================================ the push
S.cut(CUT_PUSH - FR, cam=(LEDGE[0] + 30, LEDGE[1] - 120, 1.35))
S.cut(CUT_UNAWARE - FR, cam=(XR + 40, 720, 1.3))
S.cut(CUT_PUSH2 - FR, cam=(LEDGE[0] + 30, LEDGE[1] - 120, 1.4))
for tn in NUDGES: S.sfx(tn + 0.12, "tok", 0.04)
S.cut(CUT_FALL - FR, cam=(XR + 60, 860, 0.72))
S.sfx(CUT_FALL, "slide_down", 0.07, dur=T_BONK - CUT_FALL)
S.set(CUT_FALL + 0.25, "stand", "delighted", dur=0.25, blush=0.0, look=(0.0, -1.0), tilt=-0.08)    # looks up. still smiling.
S.set(T_BONK - FR, "stand", "delighted", dur=0.04, ease="snap", blush=0.0, stretch=-0.8, nowalk=1.0)
S.sfx(T_BONK, "bonk", 0.3); S.sfx(T_BONK, "thud", 0.25); S.shake(T_BONK, 0.5, 22)
S.set(T_BONK + 0.02, "stand", "delighted", dur=0.0, blush=0.0, show=0.0, nowalk=1.0)
S.set(T_ROLL0 + 0.25, "sit_floor", "knocked_out", dur=0.0, stretch=-0.35, nowalk=1.0)
for k in range(4): S.sfx(T_ROLL0 + 0.15 * k, "tok", 0.02)
S.set(T_UP, "stand", "dead_stare", dur=0.25, ease="back", mouth="grin", smile=1.0, open=0.45, mouth_w=1.4, stretch=0.0)
S.sfx(T_UP, "boing", 0.05)
S.camera(T_UP, XR + 180, 880, 0.66, 0.8)
S.blink(T_UP + 0.6)
S.t = T_ASK
S.the_ask(T_ASK, hold=ASK_HOLD, push=False, keep=dict(mouth="grin", smile=1.0, open=0.45, mouth_w=1.4))

# ---------------------------------------------------------------- episode sounds (synth): meows, hiss, purr
SR = L.SR
def _t(d): return np.arange(int(d * SR)) / SR
def place(buf, sig, t0, g):
    i = int(t0 * SR)
    if 0 <= i < len(buf): m = min(len(sig), len(buf) - i); buf[i:i + m] += sig[:m] * g
def meow(f0=700, d=0.45, seed=0):
    tt = _t(d); u = tt / d
    f = f0 * (0.85 + 0.35 * np.sin(np.pi * u ** 0.8)) * (1 + 0.02 * np.sin(2 * np.pi * 7 * tt))
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)
    env = np.minimum(1, tt / 0.03) * np.minimum(1, (d - tt) / 0.12) * (0.6 + 0.4 * np.sin(np.pi * u))
    return (sig * env * 0.35).astype(np.float32)
def hiss(d=0.6):
    tt = _t(d); nz = np.random.default_rng(3).standard_normal(len(tt))
    nz = nz - np.convolve(nz, np.ones(6) / 6, mode="same")
    return (nz * np.minimum(1, tt / 0.02) * np.exp(-tt / 0.35) * 0.6).astype(np.float32)
def purr(d, rate=26):
    tt = _t(d); nz = np.random.default_rng(9).standard_normal(len(tt))
    lp = np.convolve(nz, np.ones(60) / 60, mode="same")
    am = 0.5 + 0.5 * np.sin(2 * np.pi * rate * tt) ** 2
    return (lp * am * np.minimum(1, tt / 0.8) * np.minimum(1, (d - tt) / 0.4) * 6.0).astype(np.float32)
def extra(n):
    buf = np.zeros(n, np.float32)
    place(buf, meow(1100, 0.32), 0.25, 0.5); place(buf, meow(1250, 0.38), T_KSIT + 0.2, 0.6)
    place(buf, hiss(), T_HISS, 0.6)
    place(buf, meow(1200, 0.3), T_KIN1 + 0.6, 0.35)                      # from inside the shelter
    rr = random.Random(5)
    for k in range(5): place(buf, meow(rr.uniform(500, 900), 0.5), T_RUMBLE + 0.3 + k * 0.17, 0.12)   # far away. many.
    for k in range(26): place(buf, meow(rr.uniform(550, 1300), rr.uniform(0.3, 0.5)), T_DOORS + 0.3 + k * 0.09, 0.22)
    for k in range(10): place(buf, meow(rr.uniform(600, 1200), 0.35), T_HIT + 0.1 + k * 0.25, 0.18)
    for k, tk in enumerate(STACK_T): place(buf, meow(900 + 60 * k, 0.25), tk - 0.2, 0.2)
    for k in range(8): place(buf, meow(rr.uniform(700, 1400), 0.3), T_BURST + 0.1 + k * 0.06, 0.25)
    place(buf, meow(1300, 0.3), FLUNG[0]["t0"], 0.3); place(buf, meow(1000, 0.3), FLUNG[1]["t0"], 0.3)
    place(buf, purr(CUT_PUSH - T_KBLINK + 0.6), T_KBLINK, 0.35)            # every cat purrs
    place(buf, meow(1250, 0.4), T_TIP + 0.3, 0.3)
    return buf * 0.5
_orig_soften = L._soften
def _soften_plus(x): return _orig_soften(x) + extra(len(x))
L._soften = _soften_plus

if __name__ == "__main__":
    print(f"bonk {T_BONK:.2f} end {S.t:.2f}", file=sys.stderr)
    S.render("day011.mp4")
