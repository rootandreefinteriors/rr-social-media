"""Day 6 — COMMENT episode: @nerdbpy "Rock a baby to sleep. (My mom said this)" (Instagram, day 5 reel, 4 likes).
RE-CUT on Justin's outline (2026-10-28). He lives outside the burger place (STATE world.location). No HUD.

SHOT 1  Outside the burger place, in the wrappers. Reads the comment. Stares. Slow blink.
MOM     A mom walks in from the left carrying her baby, stops in front of him, hands him the baby and scurries into
        the burger place.
CRY     Silence. The baby looks at him. Its face crumples: waah. He is frazzled (hair frizzes, sweat, eyes dart).
ROCK    He cradles it and rocks it, back and forth. The crying fades. It falls asleep (z z z). His hair settles. He
        keeps rocking... slower... his lids get heavy... he falls asleep standing up, holding it. Both: Zzz.
BURGER  The mom comes out holding a burger. Eats it in one bite. Sees them. Delighted. Takes her baby back, kisses him
        on the cheek. He wakes up. He blushes. She scurries off. He stands there, arms still cradling nothing.
END     The ask, still blushing.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y
from ink import smooth, draw_text

SX = 2000                       # where he lives (body centre 2540, in the wrappers)
X0 = 540 + SX
DOOR = 2760                     # the burger place's door
MS = 0.92                       # the mom is drawn a little smaller than him
CAM0 = (2600, 930, 1.15)
CAM_WIDE = (2560, 930, 1.0)
CAM_CLOSE = (2560, 860, 1.15)
CAM_RET = (2650, 930, 1.0)

# ---------------------------------------------------------------- timeline
M_IN0, M_IN1 = 3.6, 6.4         # she walks in
G0, G1 = 6.9, 7.6               # she hands him the baby
RUN0, RUN1 = 8.0, 9.0           # she scurries into the shop
T_CRY = 11.3
R0 = 15.6                       # he starts cradling + rocking
T_HUSH, T_SLEEP = 19.6, 20.8    # crying fades / baby asleep
T_NOD, T_OUT = 24.0, 27.2       # he gets drowsy / he's asleep
OUT0, OUT1 = 30.4, 31.2         # she comes out with a burger
T_BITE = 32.0
T_SEE = 32.9
W0, W1 = 33.8, 34.8             # she walks over
K0, K1 = 35.0, 35.8             # takes the baby
KISS = 36.2
T_WAKE = 36.9
BYE0, BYE1 = 37.8, 39.0         # scurries off to the right
T_ASK = 41.6

S = M.Scene(x0=SX)
S.auto_blinks = False
S.card("nerdbpy", "Rock a baby to sleep. (My mom said this)", "4", t0=0.35)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0
S.sfx(0.35, "tick", 0.04)
S.background(lambda cr, t: O.draw_burger_world(cr, t))

# ================================================================ the mom: her own track on his rig
MX = Track([(0.0, 1700.0, 0), (M_IN0, 1700.0, 0), (M_IN0, 2270.0, M_IN1 - M_IN0, "out"),
            (RUN0, float(DOOR), RUN1 - RUN0, "inn"),
            (OUT0, float(DOOR), 0), (W0, 2745.0, W1 - W0, "smooth"),
            (BYE0, 3500.0, BYE1 - BYE0, "inn")])
def mom_x(t): return MX.at(t)
def mom_shown(t):
    if t < M_IN0 or t >= BYE1: return 0.0
    if RUN1 - 0.1 <= t < OUT0: return 0.0                       # inside the shop
    return 1.0
MK = [(0.0, L.pose("stand", "happy", turn=1.0), 0)]
def mk(t, body, face, dur=0.3, ease="smooth", **kw): MK.append((t, L.pose(body, face, **kw), dur, ease))
mk(M_IN1 - 0.3, "stand", "happy", turn=0.9, look=(0.6, 0.0))
mk(G0 - 0.3, "stand", "eager", turn=0.8, look=(0.5, 0.2))
mk(G1 + 0.1, "stand", "happy", turn=0.8, look=(0.6, 0.0))
mk(RUN0 - 0.1, "stand", "eager", turn=1.1, look=(0.8, -0.2), run=1.0)
mk(OUT0, "stand", "happy", turn=0.0, look=(0.0, 0.0), run=0.0, dur=0.0)
mk(OUT1, "stand", "happy", turn=-0.3, look=(-0.2, -0.3))                     # admires her burger
mk(T_BITE - 0.25, "stand", "eager", turn=-0.2, look=(0.3, -0.5))
mk(T_BITE + 0.15, "stand", "happy", turn=-0.2, look=(0.0, 0.0), squash=0.25)
mk(T_SEE, "stand", "surprised", dur=0.15, ease="snap", turn=-0.9, look=(-0.8, 0.1))
mk(T_SEE + 0.5, "stand", "delighted", dur=0.25, turn=-0.9, look=(-0.8, 0.1))
mk(W1, "stand", "happy", turn=-1.0, look=(-0.8, 0.2))
mk(KISS - 0.25, "stand", "kiss", turn=-1.2, lean=-0.07, tilt=-0.12, fx_hearts=0.0)
mk(KISS + 0.45, "stand", "delighted", turn=-1.0, lean=0.0, tilt=0.0)
mk(BYE0 - 0.1, "stand", "delighted", turn=1.1, look=(0.8, 0.0), run=1.0)
MOMK = Track(MK)

def mom_pose(t):
    """unscaled pose (feet on the floor at her x), with a little walk/run cycle and her hands where they need to be."""
    p = dict(MOMK.at(t))
    x = mom_x(t); v = (mom_x(t + 0.02) - mom_x(t - 0.02)) / 0.04
    wk = min(1.0, abs(v) / 60.0); d = 1 if v >= 0 else -1
    run = p.get("run", 0.0)
    ox = x - 540
    for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1])
    if wk > 0.01:
        ph = x / 70.0 * math.pi
        stride, lift = 55 + 35 * run, 32 + 28 * run
        hipx, hipy = p["hip"]
        bob = (9 + 12 * run) * abs(math.sin(ph)) * wk
        for side, off in (("l", 0.0), ("r", math.pi)):
            s_ = math.sin(ph + off); lf = max(0.0, math.cos(ph + off)) * lift
            foot = (hipx + stride * s_, FLOOR_Y - lf)
            knee = ((hipx + foot[0]) / 2 + d * 24, (hipy + FLOOR_Y) / 2 - lf * 0.55)
            p[side + "foot"] = lerp(p[side + "foot"], foot, wk); p[side + "knee"] = lerp(p[side + "knee"], knee, wk)
        for k in ("head", "neck", "hip", "lelb", "relb", "lhand", "rhand"): p[k] = (p[k][0], p[k][1] + bob)
        p["lfoot_dir"] = p["rfoot_dir"] = 0.9 * d
        if run > 0.5: p["lean"] = p.get("lean", 0.0) + 0.1 * d
    ln = p.get("lean", 0.0)
    if abs(ln) > 1e-4:
        fx_ = (p["lfoot"][0] + p["rfoot"][0]) / 2; c, s_ = math.cos(ln), math.sin(ln)
        for j in L.JOINTS:
            if j in ("lfoot", "rfoot"): continue
            dx, dy = p[j][0] - fx_, p[j][1] - FLOOR_Y
            p[j] = (fx_ + dx * c - dy * s_, FLOOR_Y + dx * s_ + dy * c)
    # hands: on the baby while she has it; the burger in her right hand
    b = baby(t)
    e = mom_hold(t)
    if e > 0.01 and b:
        for side, (lx, ly) in (("l", (-85, 34)), ("r", (100, 30))):
            hx, hy = unscale(p, O.baby_pt(b[0], b[1], b[2], lx, ly))
            p[side + "hand"] = lerp(p[side + "hand"], (hx, hy), e); p[side + "hand_t"] = "grip"
    if OUT0 <= t < T_BITE + 0.4:
        bh = (p["neck"][0] + 95, p["neck"][1] + 120)
        if t > T_BITE - 0.35: bh = lerp(bh, (p["head"][0] + 20, p["head"][1] + 70), smooth(ramp(t, T_BITE - 0.35, T_BITE - 0.05)) * (1 - ramp(t, T_BITE + 0.1, T_BITE + 0.4)))
        p["rhand"] = bh; p["rhand_t"] = "grip"
    return L.constrain(p)
def scale_pt(p, pt):
    fx = (p["lfoot"][0] + p["rfoot"][0]) / 2
    return (fx + (pt[0] - fx) * MS, FLOOR_Y + (pt[1] - FLOOR_Y) * MS)
def unscale(p, pt):
    fx = (p["lfoot"][0] + p["rfoot"][0]) / 2
    return (fx + (pt[0] - fx) / MS, FLOOR_Y + (pt[1] - FLOOR_Y) / MS)
def mom_blink(t):
    for b in (5.2, 9.7, OUT1 + 0.4, T_SEE + 1.2, BYE0 - 0.4):
        if b <= t < b + 0.16: return math.sin(math.pi * (t - b) / 0.16)
    return 0.0

def mom(cr, t, p, ly):
    if ly != "back" or mom_shown(t) < 0.5: return
    q = mom_pose(t)
    O.draw_mom(cr, t, q, mom_blink(t), s=MS)
    if OUT0 <= t < T_BITE + 0.05:                                       # the burger, gone in one bite
        hx, hy = scale_pt(q, q["rhand"])
        O.draw_burger(cr, hx, hy - 40, 0.42, sid=3)
    if T_BITE <= t < T_BITE + 0.4:
        L.burst_lines(cr, *scale_pt(q, (q["head"][0] + 10, q["head"][1] + 60)), (t - T_BITE) / 0.4, r0=60, r1=110, n=8, sid=61)
S.sfx(T_BITE, "chomp", 0.06); S.sfx(T_BITE + 0.35, "gulp", 0.05)

# the door: open while she goes in / comes out
def door(cr, t, p, ly):
    if ly != "back": return
    if (RUN1 - 0.35 <= t < RUN1 + 0.25) or (OUT0 - 0.25 <= t < OUT0 + 0.45):
        L.sketch_rect(cr, DOOR - 45, FLOOR_Y - 250, DOOR + 45, FLOOR_Y, 5, sid=6310, fill=(0.22, 0.2, 0.24))
S.sfx(RUN1 + 0.2, "tok", 0.05); S.sfx(OUT0 - 0.2, "tok", 0.05)

# ================================================================ the baby: who holds it, where
def sway(t):
    if t < R0: return 0.0
    a = smooth(ramp(t, R0, R0 + 1.2)) * (1 - 0.55 * smooth(ramp(t, T_NOD, T_OUT + 1.0)))
    a *= 1 - smooth(ramp(t, K0, K0 + 0.3))
    f = 0.55 - 0.2 * smooth(ramp(t, T_NOD, T_OUT))
    return a * math.sin(2 * math.pi * f * (t - R0))
def his_spot(t):
    s_ = sway(t)
    frazzle = (T_CRY + 0.5 <= t < R0)
    y = 985 if t >= R0 - 0.4 else 1010
    x = X0 + 60 * s_ + (8 * math.sin(t * 17) if frazzle else 0.0)
    if T_CRY + 1.4 <= t < R0 - 0.5: x += 35; y -= 30            # holds it out a little, at arm's length
    return (x, y + 10 * abs(s_), 0.22 * s_)
def mom_spot(t):
    p = mom_pose_raw(t)
    return (*scale_pt(p, (p["hip"][0] + 20, p["neck"][1] + 185)), 0.0)
def mom_pose_raw(t):                                                  # body only (no hands) for placing the baby
    p = dict(MOMK.at(t)); ox = mom_x(t) - 540
    for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1])
    return p
def mom_hold(t):
    if t < G1 + 0.05: return 1.0
    if t < K0 - 0.2: return 0.0
    return smooth(ramp(t, K0 - 0.2, K0 + 0.2))
def baby(t):
    if t < M_IN0 or t >= BYE1: return None
    if t < G0: return mom_spot(t)
    if t < G1:
        u = smooth((t - G0) / (G1 - G0)); a, b = mom_spot(t), his_spot(t)
        return (lerp(a[0], b[0], u), lerp(a[1], b[1], u) - 40 * math.sin(math.pi * u), lerp(a[2], b[2], u))
    if t < K0: return his_spot(t)
    if t < K1:
        u = smooth((t - K0) / (K1 - K0)); a, b = his_spot(t), mom_spot(t)
        return (lerp(a[0], b[0], u), lerp(a[1], b[1], u) - 40 * math.sin(math.pi * u), lerp(a[2], b[2], u))
    return mom_spot(t)
def baby_st(t):
    if t < T_CRY - 0.6:
        lk = (-1.0, 0.2) if t >= G1 + 1.2 else (0.4, -0.3)
        return dict(eyes="open", look=lk)
    if t < T_CRY: return dict(eyes="open", look=(-1.0, 0.2) if t < T_CRY - 0.3 else (0.0, 0.0))
    if t < T_SLEEP:
        k = 1 - smooth(ramp(t, T_HUSH, T_SLEEP - 0.3))
        if t >= T_SLEEP - 0.5: return dict(eyes="open", look=(-0.5, 0.3)) if t < T_SLEEP - 0.25 else dict(eyes="sleep")
        return dict(eyes="cry", cry=smooth(ramp(t, T_CRY, T_CRY + 0.25)) * (0.4 + 0.6 * k))
    return dict(eyes="sleep")
def baby_draw(cr, t, p, ly):
    if ly != "front": return
    b = baby(t)
    if b: O.draw_baby(cr, b[0], b[1], b[2], baby_st(t), t)
    if T_CRY + 0.2 <= t < T_SLEEP - 0.5 and b:                       # waah
        k = 1 - smooth(ramp(t, T_HUSH, T_SLEEP - 0.6))
        for i in range(3):
            u = ((t - T_CRY) * 0.7 + i / 3) % 1.0
            hx, hy = O.baby_pt(b[0], b[1], b[2], *O.BABY_FACE)
            draw_text(cr, "waah", hx - 60 - 160 * u, hy - 90 - 170 * u, 46 + 22 * u, color=(30, 30, 34),
                      rot=-0.15 + 0.06 * math.sin(t * 20 + i), alpha=math.sin(math.pi * u) * k)
def zzz(cr, t, p, ly):
    if ly != "front": return
    b = baby(t)
    if b and T_SLEEP + 0.8 <= t < K0:
        for i in range(3):
            u = ((t - T_SLEEP) * 0.45 + i / 3) % 1.0
            hx, hy = O.baby_pt(b[0], b[1], b[2], *O.BABY_FACE)
            draw_text(cr, "z", hx - 70 - 40 * u + 10 * math.sin(u * 6), hy - 80 - 150 * u, 34 + 26 * u, color=(30, 30, 34),
                      alpha=math.sin(math.pi * u) * ramp(t, T_SLEEP + 0.8, T_SLEEP + 1.4))
    if T_OUT + 0.5 <= t < KISS + 0.1:                                 # his: bigger, up and to the left
        hx, hy = p["head"]
        for i in range(3):
            u = ((t - T_OUT) * 0.4 + i / 3) % 1.0
            draw_text(cr, "Z", hx - 130 - 80 * u + 12 * math.sin(u * 5), hy - 40 - 170 * u, 46 + 34 * u, color=(30, 30, 34),
                      alpha=math.sin(math.pi * u) * ramp(t, T_OUT + 0.5, T_OUT + 1.2))
for k in range(5): S.sfx(T_CRY + 0.1 + k * 0.95, "wah", 0.05 if k < 4 else 0.03)
S.sfx(T_HUSH + 0.3, "wah", 0.018)

# his hands on the baby (cradling) from the handover until he lowers his empty arms
def hold_e(t): return smooth(ramp(t, G0 + 0.1, G1 - 0.05)) * (1 - smooth(ramp(t, T_ASK - 1.7, T_ASK - 1.0)))
def cradle_hook(tt, p):
    e = hold_e(tt)
    if e < 0.001: return p
    b = baby(tt) if tt < K0 else None
    if b is None:                                                    # baby gone: the arms keep the shape
        b = his_spot(K0)
    lh = O.baby_pt(b[0], b[1], b[2], -78, 40); rh = O.baby_pt(b[0], b[1], b[2], 105, 28)
    p["lhand"] = lerp(p["lhand"], lh, e); p["rhand"] = lerp(p["rhand"], rh, e)
    p["lelb"] = lerp(p["lelb"], (p["lelb"][0] - 30, lh[1] + 30), e); p["relb"] = lerp(p["relb"], (p["relb"][0] + 20, rh[1] + 40), e)
    p["lhand_t"] = p["rhand_t"] = "grip"
    s_ = sway(tt)
    for k_, a in (("head", 22), ("neck", 14), ("hip", 6)): p[k_] = (p[k_][0] + a * s_, p[k_][1])
    p["tilt"] = p.get("tilt", 0.0) + 0.06 * s_
    return p

# ================================================================ HIM
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(0.6, react="dead_stare", lines=2, face="deadpan")
S.set(3.0, "stand", "dead_stare", dur=0.25, lid=1.0)
S.set(3.35, "stand", "dead_stare", dur=0.35)
S.camera(M_IN0 - 0.3, *CAM_WIDE, dur=1.5)
S.set(M_IN0 + 0.6, "stand", "dead_stare", dur=0.5, look=(-0.8, 0.0))                       # watches her come in
S.set(M_IN1, "stand", "dead_stare", dur=0.3, look=(-0.7, 0.1))
S.set(G0 - 0.2, "hold_front", "dead_stare", dur=0.4, look=(-0.4, 0.4))                      # takes it
S.set(RUN0 + 0.2, "hold_front", "dead_stare", dur=0.3, look=(0.7, -0.1))                    # watches her go
S.set(RUN1 + 0.4, "hold_front", "dead_stare", dur=0.3, look=(0.8, 0.0), tilt=-0.03)
S.set(RUN1 + 1.3, "hold_front", "dead_stare", dur=0.4, look=(0.0, 0.6), tilt=0.0)           # looks down at it
S.blink(10.0)
S.set(10.5, "hold_front", "dead_stare", dur=0.35, look=(0.0, 0.0))                           # at us
S.camera(10.2, *CAM_CLOSE, dur=1.4)
# frazzled
S.set(T_CRY + 0.3, "hold_front", "dead_stare", dur=0.12, ease="snap", eyescale=1.15, lid=0.0, look=(0.0, 0.6))
S.set(T_CRY + 0.9, "hold_front", "dead_stare", dur=0.15, eyescale=1.15, lid=0.0, frizz=1.0, sweat=0.5, look=(0.7, 0.0))   # the door
S.set(T_CRY + 1.5, "hold_front", "holding_it", dur=0.15, eyescale=1.1, frizz=1.0, sweat=0.8, twitch=0.6, look=(0.0, 0.6))
S.set(T_CRY + 2.1, "hold_front", "holding_it", dur=0.15, eyescale=1.1, frizz=1.0, sweat=1.0, twitch=0.8, look=(-0.8, 0.0))
S.set(T_CRY + 2.7, "hold_front", "holding_it", dur=0.25, eyescale=1.1, frizz=1.0, sweat=1.0, twitch=0.8, quiver=0.7, look=(0.0, 0.0))  # at us
S.set(T_CRY + 3.6, "hold_front", "holding_it", dur=0.3, frizz=1.0, sweat=1.0, quiver=0.7, breath=1.8, breath_rate=2.2, look=(0.0, 0.6))
# rocks it
S.set(R0, "hold_front", "resigned", dur=0.8, frizz=1.0, sweat=0.8, look=(0.0, 0.7))
S.set(T_HUSH, "hold_front", "resigned", dur=0.8, frizz=1.0, sweat=0.4, look=(0.0, 0.7))
S.set(T_SLEEP + 0.4, "hold_front", "deadpan", dur=0.6, frizz=0.0, sweat=0.2, look=(0.0, 0.7))   # it's out. the hair settles.
S.sfx(T_SLEEP + 0.4, "boing", 0.02)
S.set(T_SLEEP + 1.6, "hold_front", "deadpan", dur=0.5, look=(0.0, 0.0))                          # at us
S.camera(T_SLEEP + 1.0, 2540, 870, 1.22, 6.0)
S.set(T_NOD, "hold_front", "sleepy", dur=1.5, lid=0.6, look=(0.0, 0.3))
S.set(T_NOD + 1.6, "hold_front", "sleepy", dur=0.8, lid=0.85, tilt=0.1)
S.set(T_NOD + 2.4, "hold_front", "sleepy", dur=0.2, ease="snap", lid=0.3, tilt=0.0)            # catches himself
S.set(T_NOD + 2.7, "hold_front", "sleepy", dur=0.6, lid=0.8, tilt=0.06)
S.set(T_OUT, "hold_front", "asleep", dur=0.8, fx_zzz=0.0)
S.sfx(T_OUT + 0.6, "snore", 0.03, dur=1.6); S.sfx(T_OUT + 2.4, "snore", 0.03, dur=1.6)
S.camera(OUT0 - 0.6, *CAM_RET, dur=1.4)
S.sfx(T_OUT + 4.2, "snore", 0.025, dur=1.6)
# she takes it, kisses him; he wakes; blushes
S.set(KISS + 0.1, "hold_front", "asleep", dur=0.1, fx_zzz=0.0)
S.sfx(KISS + 0.05, "pop", 0.04)
S.set(T_WAKE, "hold_front", "dead_stare", dur=0.15, ease="snap", eyescale=1.12, lid=0.0, look=(0.0, 0.0))
S.set(T_WAKE + 0.5, "hold_front", "dead_stare", dur=0.3, look=(0.0, 0.6))                    # his arms: empty
S.set(T_WAKE + 1.1, "hold_front", "dead_stare", dur=0.3, look=(0.7, 0.0))                    # her
S.set(T_WAKE + 1.4, "hold_front", "dead_stare", dur=1.2, look=(0.7, 0.0), blush=1.0)         # blush builds
S.set(BYE1 + 0.2, "hold_front", "dead_stare", dur=0.4, look=(0.0, 0.0), blush=1.0)           # at us
S.blink(BYE1 + 1.4)
S.set(T_ASK - 1.7, "stand", "dead_stare", dur=0.7, blush=1.0)
S.t = T_ASK
S.camera(T_ASK - 1.0, 2560, 900, 1.12, 1.0)
S.camera(T_ASK + 6.9, 2560, 905, 1.16, 3.0)
S.the_ask(T_ASK, hold=8.0, push=False, keep=dict(blush=1.0))

def kiss_fx(cr, t, p, ly):
    if ly == "front" and KISS <= t < KISS + 0.5:
        hx, hy = p["head"]
        L.burst_lines(cr, hx + 105, hy + 25, (t - KISS) / 0.5, r0=30, r1=70, n=6, sid=71)

# ---------------------------------------------------------------- draw order + hooks
S.props.insert(0, lambda cr, t, p, ly: O.draw_wrapper_pile(cr, X0, 1350, 260) if ly == "back" else None)
for f in (door, mom): S.prop(f)
S.prop(lambda cr, t, p, ly: O.draw_wrapper_pile(cr, X0 + 40, 900, 95) if ly == "front" else None)
for f in (baby_draw, zzz, kiss_fx): S.prop(f)
S.hook(cradle_hook)

if __name__ == "__main__":
    S.render("day006.mp4")
