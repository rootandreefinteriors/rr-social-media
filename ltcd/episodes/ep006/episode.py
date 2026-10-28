"""Day 6 — COMMENT episode: @nerdbpy "Rock a baby to sleep. (My mom said this)" (Instagram, day 5 reel, 4 likes).
RE-CUT 2 on Justin's notes (2026-10-28): it all happens NEXT TO the wrapper pile (the pile is on his left now, the
burger place's door clear on his right), the mom walks off into the distance and in through a real door, and
everything is animated with more care (follow-through on her too, anticipation, settles). No HUD.

SHOT 1  Beside the wrapper pile outside the burger place. Reads the comment. Stares. Slow blink.
MOM     A mom walks in from the right carrying her baby, stops in front of him, hands it over (his arms come up to
        meet it), turns, and scurries off into the distance to the burger place: the door swings open, she's in, it
        swings shut.
CRY     Silence. The baby looks at him. Its face crumples: waah. He's frazzled (hair frizzes, sweat, eyes dart).
ROCK    He cradles it and sways, weight shifting side to side. The crying fades. It's asleep. His hair settles. He keeps
        swaying, slower... his head droops... a nod, he catches it... asleep standing up, holding it. Both: Zzz.
BURGER  The door opens; she comes back out toward us with a burger. Mouth wide, ONE bite, chew, gulp. Sees them.
        Delighted (hands clasped, up on her toes). Takes the baby back gently. Up on tiptoe, kisses his cheek. He
        wakes. Blushes. She scurries off. He stands there, arms still cradling nothing, then lowers them.
END     The ask, still blushing.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y
from ink import smooth, draw_text

SX = 2020                       # him: body centre 2560, just right of the wrapper pile
X0 = 540 + SX
PILE = (2210, 640, 230)         # wrapper pile centre / width / height (ends at ~2475, left of him)
DOORX = 2759
CAM0 = (2660, 960, 1.1)
CAM_A = (2770, 950, 1.0)

# ---------------------------------------------------------------- timeline
M_IN0, M_IN1 = 3.6, 6.5         # she walks in from the right
G0, G1 = 6.9, 7.7               # hands him the baby
RUN0, RUN1 = 8.3, 9.9           # scurries off into the distance to the door
T_CRY = 11.8
R0 = 16.0                       # he cradles + sways
T_HUSH, T_SLEEP = 20.0, 21.2
T_NOD, T_OUT = 24.4, 27.6
OUT0, OUT1 = 30.4, 32.0         # door opens; she walks back out toward us
T_BITE = 32.7
T_SEE = 33.9
W0, W1 = 34.8, 35.4             # steps over
K0, K1 = 35.6, 36.4             # takes the baby
KISS = 36.9
T_WAKE = 37.4
BYE0, BYE1 = 38.4, 39.6
T_ASK = 42.4

S = M.Scene(x0=SX)
S.auto_blinks = False
S.card("nerdbpy", "Rock a baby to sleep. (My mom said this)", "4", t0=0.35)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0
S.sfx(0.35, "tick", 0.04)
S.background(lambda cr, t: O.draw_burger_world(cr, t))

# ================================================================ the mom
MX = Track([(0.0, 3500.0, 0), (M_IN0, 3500.0, 0), (M_IN0, 2830.0, M_IN1 - M_IN0, "out"),
            (RUN0, float(DOORX), RUN1 - RUN0, "smooth"),
            (OUT0, float(DOORX), 0), (OUT0 + 0.2, 2880.0, OUT1 - OUT0 - 0.2, "out"),
            (W0, 2815.0, W1 - W0, "smooth"),
            (BYE0 + 0.15, 3600.0, BYE1 - BYE0 - 0.15, "inn")])
MSC = Track([(0.0, 0.92, 0), (RUN0, 0.92, 0), (RUN0, 0.27, RUN1 - RUN0, "inn"), (RUN1, 0.22, 0.4, "linear"),
             (OUT0, 0.25, 0), (OUT0 + 0.2, 0.92, OUT1 - OUT0 - 0.2, "out")])
# walking: 1 = stepping; stride 1 = sideways, ~0.2 = away from / toward us
MW = Track([(0.0, 0.0, 0), (M_IN0, 1.0, 0.25), (M_IN1 - 0.35, 0.0, 0.4), (RUN0 + 0.05, 1.0, 0.15), (RUN1, 0.0, 0.25),
            (OUT0 + 0.2, 1.0, 0.2), (OUT1 - 0.3, 0.0, 0.35), (W0, 1.0, 0.15), (W1 - 0.15, 0.0, 0.2),
            (BYE0 + 0.15, 1.0, 0.15)])
MSTR = Track([(0.0, 1.0, 0), (RUN0, 0.15, 0.2), (RUN1 + 1, 1.0, 0), (OUT0, 0.2, 0), (OUT1, 1.0, 0.3)])
def mom_x(t): return MX.at(t)
def ms(t): return MSC.at(t)
def mom_alpha(t):
    if t < M_IN0 or t >= BYE1 + 0.3: return 0.0
    if t >= RUN1 - 0.05 and t < OUT0: return 1 - ramp(t, RUN1 - 0.05, RUN1 + 0.35)
    if OUT0 <= t < OUT0 + 0.3: return ramp(t, OUT0, OUT0 + 0.3)
    return 1.0
MK = [(0.0, L.pose("stand", "happy", turn=-1.0), 0)]
def mk(t, body, face, dur=0.3, ease="smooth", **kw): MK.append((t, L.pose(body, face, **kw), dur, ease))
mk(M_IN1 - 0.4, "stand", "happy", dur=0.5, turn=-0.8, look=(-0.6, 0.0))
mk(G0 - 0.4, "stand", "eager", turn=-0.8, look=(-0.4, 0.3), lean=-0.05)
mk(G1 + 0.1, "stand", "happy", turn=-0.8, look=(-0.6, 0.0), lean=0.0)
mk(RUN0 - 0.45, "stand", "eager", dur=0.25, turn=-0.3, look=(0.0, 0.0), squash=0.25, stretch=-0.2)    # wind-up
mk(RUN0 - 0.1, "stand", "eager", dur=0.15, ease="snap", back=1.0, run=1.0, stretch=0.1)              # off she goes
mk(OUT0, "stand", "happy", dur=0.0, back=0.0, run=0.0, turn=0.0, look=(0.0, 0.0), stretch=0.0)
mk(OUT0 + 0.6, "stand", "happy", dur=0.4, turn=0.2, look=(0.3, 0.5))                                 # admiring her burger
mk(T_BITE - 0.45, "stand", "eager", dur=0.25, turn=0.1, mouth="o", open=1.0, look=(0.2, 0.6), tilt=-0.08)  # mouth WIDE
mk(T_BITE, "stand", "happy", dur=0.08, ease="snap", eyes="happy", smile=0.4, squash=0.35, tilt=0.0)  # CHOMP
mk(T_BITE + 0.15, "stand", "happy", dur=0.12, eyes="happy", squash=-0.1)
mk(T_BITE + 0.3, "stand", "happy", dur=0.12, eyes="happy", squash=0.25)
mk(T_BITE + 0.45, "stand", "happy", dur=0.12, eyes="happy", squash=-0.05)
mk(T_BITE + 0.7, "stand", "happy", dur=0.2, eyes="happy", smile=0.8)                                 # gulp. satisfied.
mk(T_SEE, "stand", "surprised", dur=0.12, ease="snap", turn=-0.9, look=(-0.8, 0.1))
mk(T_SEE + 0.45, "stand", "delighted", dur=0.25, turn=-0.9, look=(-0.8, 0.1), tiptoe=1.0, hop=14, blush=0.0)
mk(T_SEE + 0.75, "stand", "delighted", dur=0.25, turn=-0.9, look=(-0.8, 0.1), tiptoe=1.0, hop=0, blush=0.0)
mk(W1, "stand", "happy", dur=0.3, turn=-1.0, look=(-0.8, 0.3))
mk(KISS - 0.4, "stand", "kiss", dur=0.35, turn=-1.25, lean=-0.11, tilt=-0.14, tiptoe=1.0, hop=20, fx_hearts=0.0, blush=0.3)
mk(KISS + 0.45, "stand", "delighted", dur=0.35, turn=-1.0, lean=0.0, tilt=0.0, hop=0, tiptoe=0.0, blush=0.0)
mk(BYE0 - 0.25, "stand", "delighted", dur=0.2, turn=-0.4, squash=0.2, stretch=-0.15)                 # wind-up
mk(BYE0 + 0.05, "stand", "happy", dur=0.15, ease="snap", turn=1.1, look=(0.8, 0.0), run=1.0, stretch=0.0)
MOMK = Track(MK)

def mom_base(t):
    """her body: track + walk/run cycle + lean, unscaled (feet at the floor at her x)."""
    p = dict(MOMK.at(t))
    x = mom_x(t); ox = x - 540
    for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1])
    wk = MW.at(t); run = p.get("run", 0.0)
    v = (mom_x(t + 0.03) - mom_x(t - 0.03)) / 0.06; d = 1 if v > 1 else (-1 if v < -1 else 0)
    if wk > 0.01:
        ph = t * 2 * math.pi * (1.45 + 1.1 * run)
        stride, lift = (52 + 18 * run) * MSTR.at(t), 30 + 22 * run
        hipx, hipy = p["hip"]
        for side, off in (("l", 0.0), ("r", math.pi)):
            s_ = math.sin(ph + off); lf = max(0.0, math.cos(ph + off)) * lift
            foot = (hipx + stride * s_ + (-28 if side == "l" else 28) * (1 - MSTR.at(t)), FLOOR_Y - lf)
            knee = ((hipx + foot[0]) / 2 + d * 22 + (-14 if side == "l" else 14) * (1 - MSTR.at(t)), (hipy + FLOOR_Y) / 2 - lf * 0.6)
            p[side + "foot"] = lerp(p[side + "foot"], foot, wk); p[side + "knee"] = lerp(p[side + "knee"], knee, wk)
            hs = -s_ * (26 + 30 * run) * wk                                   # arms swing opposite the legs
            p[side + "hand"] = (p[side + "hand"][0] + hs, p[side + "hand"][1] - abs(s_) * 10 * run * wk)
            p[side + "elb"] = (p[side + "elb"][0] + hs * 0.4, p[side + "elb"][1])
        bob = (8 + 10 * run) * abs(math.sin(ph)) * wk
        for k in ("head", "neck", "hip", "lelb", "relb", "lhand", "rhand"): p[k] = (p[k][0], p[k][1] + bob)
        if d: p["lfoot_dir"] = p["rfoot_dir"] = 0.9 * d * MSTR.at(t)
        p["tilt"] = p.get("tilt", 0.0) + 0.04 * math.sin(ph) * wk
        if run > 0.5 and d: p["lean"] = p.get("lean", 0.0) + 0.09 * d
    hop = p.get("hop", 0.0)
    if hop:
        for j in L.JOINTS:
            if j not in ("lfoot", "rfoot") or p.get("tiptoe", 0) < 0.5: p[j] = (p[j][0], p[j][1] - hop)
    ln = p.get("lean", 0.0); st = p.get("stretch", 0.0)
    if abs(ln) > 1e-4 or abs(st) > 1e-4:
        fx_ = (p["lfoot"][0] + p["rfoot"][0]) / 2; c, s_ = math.cos(ln), math.sin(ln)
        for j in L.JOINTS:
            if j in ("lfoot", "rfoot"): continue
            dx, dy = p[j][0] - fx_, p[j][1] - FLOOR_Y
            dx, dy = dx * (1 - 0.12 * st), dy * (1 + 0.2 * st)
            p[j] = (fx_ + dx * c - dy * s_, FLOOR_Y + dx * s_ + dy * c)
    return p
LAGJ = ("head", "lelb", "relb", "lhand", "rhand")
def mom_pose(t):
    """+ follow-through (head and arms drag a beat behind the body) + hands on the baby / burger / clasped."""
    p = mom_base(t); q = mom_base(t - 0.08)
    hp, hq = p["hip"], q["hip"]
    for j in LAGJ:
        p[j] = (hp[0] + 0.65 * (p[j][0] - hp[0]) + 0.35 * (q[j][0] - hq[0]), hp[1] + 0.65 * (p[j][1] - hp[1]) + 0.35 * (q[j][1] - hq[1]))
    b = baby(t); e = mom_hold(t)
    if e > 0.01 and b:
        for side, (lx, ly) in (("l", (-85, 34)), ("r", (100, 30))):
            p[side + "hand"] = lerp(p[side + "hand"], unscale(t, p, O.baby_pt(b[0], b[1], b[2], lx, ly)), e); p[side + "hand_t"] = "grip"
    if OUT0 <= t < T_BITE + 0.5:                                        # the burger: held up, then into her mouth
        hold = (p["neck"][0] + 85, p["neck"][1] + 140)
        mouth = (p["head"][0] + 15, p["head"][1] + 75)
        u = smooth(ramp(t, T_BITE - 0.4, T_BITE - 0.02)) * (1 - smooth(ramp(t, T_BITE + 0.15, T_BITE + 0.5)))
        p["rhand"] = lerp(hold, mouth, u); p["rhand_t"] = "grip"
    c = smooth(ramp(t, T_SEE + 0.3, T_SEE + 0.55)) * (1 - smooth(ramp(t, W0 - 0.1, W0 + 0.2)))
    if c > 0.01:                                                        # hands clasped under her chin
        cc = (p["neck"][0] - 5, p["neck"][1] + 40)
        p["lhand"] = lerp(p["lhand"], (cc[0] - 14, cc[1]), c); p["rhand"] = lerp(p["rhand"], (cc[0] + 14, cc[1]), c)
    return L.constrain(p)
def foot_c(p): return (p["lfoot"][0] + p["rfoot"][0]) / 2
def scale_pt(t, p, pt):
    fx = foot_c(p); s_ = ms(t)
    return (fx + (pt[0] - fx) * s_, FLOOR_Y + (pt[1] - FLOOR_Y) * s_)
def unscale(t, p, pt):
    fx = foot_c(p); s_ = ms(t)
    return (fx + (pt[0] - fx) / s_, FLOOR_Y + (pt[1] - FLOOR_Y) / s_)
def mom_blink(t):
    for b in (5.4, RUN0 - 0.6, OUT1 + 0.2, T_SEE - 0.4, T_SEE + 1.4, BYE0 - 0.6):
        if b <= t < b + 0.16: return math.sin(math.pi * (t - b) / 0.16)
    return 0.0

def door_open(t):
    a = smooth(ramp(t, RUN1 - 0.7, RUN1 - 0.3)) * (1 - smooth(ramp(t, RUN1 + 0.4, RUN1 + 0.8)))
    b = smooth(ramp(t, OUT0 - 0.4, OUT0)) * (1 - smooth(ramp(t, OUT0 + 0.7, OUT0 + 1.1)))
    return max(a, b)
S.sfx(RUN1 - 0.6, "squeak", 0.02); S.sfx(RUN1 + 0.8, "tok", 0.05)
S.sfx(OUT0 - 0.35, "squeak", 0.02); S.sfx(OUT0 + 1.1, "tok", 0.05)
def mom(cr, t, p, ly):
    if ly != "back": return
    O.draw_store_door(cr, door_open(t), "inside")
    a = mom_alpha(t)
    if a > 0.01:
        q = mom_pose(t)
        near_door = (RUN1 - 0.8 <= t < OUT0 + 0.6)
        if near_door:
            x0, y0, x1, y1 = O.STORE_DOOR
            cr.save(); cr.rectangle(x0 - 400, -9000, 800 + x1 - x0, 9000 + y1); cr.clip()
        O.draw_mom(cr, t, q, mom_blink(t), s=ms(t), alpha=a)
        if OUT0 <= t < T_BITE + 0.05:
            hx, hy = scale_pt(t, q, q["rhand"])
            O.draw_burger(cr, hx, hy - 38 * ms(t), 0.4 * ms(t), sid=3)
        if T_BITE <= t < T_BITE + 0.35:
            L.burst_lines(cr, *scale_pt(t, q, (q["head"][0] + 15, q["head"][1] + 70)), (t - T_BITE) / 0.35, r0=55, r1=100, n=8, sid=61)
        if T_BITE + 0.6 <= t < T_BITE + 1.0:                                # the gulp, down her neck
            u = (t - T_BITE - 0.6) / 0.4
            hb = (q["head"][0], q["head"][1] + L.HEAD_R)
            gx, gy = scale_pt(t, q, lerp(hb, q["neck"], u))
            L.sketch_circle(cr, gx, gy, 13, 5, sid=62)
        if near_door: cr.restore()
        if BYE0 + 0.2 <= t < BYE1:                                          # dust off her heels
            for k in range(3):
                u = ((t - BYE0) * 2.4 + k / 3) % 1.0
                L.draw_dust(cr, mom_x(t - 0.25 * u) - 30, FLOOR_Y, u, side=-1, sid=90 + k * 7)
    O.draw_store_door(cr, door_open(t), "panel")
S.sfx(T_BITE, "chomp", 0.06); S.sfx(T_BITE + 0.62, "gulp", 0.05)
for k in range(5): S.sfx(BYE0 + 0.25 + k * 0.2, "step", 0.03)

# ================================================================ the baby
def sway(t):
    if t < R0: return 0.0
    a = smooth(ramp(t, R0, R0 + 1.4)) * (1 - 0.5 * smooth(ramp(t, T_NOD, T_OUT + 1.0)))
    a *= 1 - smooth(ramp(t, K0 - 0.3, K0 + 0.2))
    f = 0.5 - 0.16 * smooth(ramp(t, T_NOD, T_OUT))
    return a * math.sin(2 * math.pi * f * (t - R0))
def his_spot(t):
    s_ = sway(t - 0.12)                                                   # the baby trails his body a touch
    frazzle = smooth(ramp(t, T_CRY + 0.5, T_CRY + 0.8)) * (1 - smooth(ramp(t, R0 - 0.8, R0)))
    x = X0 + 55 * s_ + 7 * math.sin(t * 15) * frazzle + 30 * frazzle
    y = 990 - 28 * frazzle - 16 * s_ * s_
    if t >= T_NOD: y += 10 * smooth(ramp(t, T_NOD, T_OUT))
    return (x, y, 0.2 * s_ + 0.05 * math.sin(t * 15) * frazzle)
def mom_spot(t):
    p = mom_base(t)
    return (*scale_pt(t, p, (p["hip"][0] + 15, p["neck"][1] + 180)), 0.0)
def mom_hold(t):
    if t < G0: return 1.0
    if t < G1: return 1 - smooth(ramp(t, G1 - 0.25, G1))
    if t < K0 - 0.2: return 0.0
    return smooth(ramp(t, K0 - 0.2, K0 + 0.15))
def arc(a, b, u, h=45):
    return (lerp(a[0], b[0], u), lerp(a[1], b[1], u) - h * math.sin(math.pi * u), lerp(a[2], b[2], u))
def baby(t):
    if t < M_IN0 or t >= BYE1 + 0.3: return None
    if t < G0: return mom_spot(t)
    if t < G1: return arc(mom_spot(t), his_spot(t), smooth((t - G0) / (G1 - G0)))
    if t < K0: return his_spot(t)
    if t < K1: return arc(his_spot(t), mom_spot(t), smooth((t - K0) / (K1 - K0)), 30)
    return mom_spot(t)
def baby_st(t):
    if t < G1 + 0.8: return dict(eyes="open", look=(-0.8, -0.2) if t >= M_IN1 else (-0.3, 0.2))
    if t < T_CRY - 0.5: return dict(eyes="open", look=(-0.2, -1.0))                       # stares up at him
    if t < T_CRY - 0.15: return dict(eyes="open", look=(0.0, -1.0), cry=0.12)            # lip wobble
    if t < T_SLEEP:
        k = 1 - smooth(ramp(t, T_HUSH, T_SLEEP - 0.6))
        if t >= T_SLEEP - 0.6: return dict(eyes="open", look=(0.0, -0.6)) if t < T_SLEEP - 0.3 else dict(eyes="sleep")
        return dict(eyes="cry", cry=smooth(ramp(t, T_CRY - 0.15, T_CRY + 0.15)) * (0.35 + 0.65 * k))
    if K0 <= t < K1 + 0.4: return dict(eyes="sleep")
    return dict(eyes="sleep")
def baby_draw(cr, t, p, ly):
    b = baby(t)
    if not b: return
    with_mom = (t < G0 + 0.3) or (t >= K1 - 0.3)
    if (ly == "back") != with_mom: return                            # with her: drawn with her (behind him)
    O.draw_baby(cr, b[0], b[1], b[2], baby_st(t), t)
    if ly == "front" and T_CRY <= t < T_SLEEP - 0.7:
        k = 1 - smooth(ramp(t, T_HUSH, T_SLEEP - 0.8))
        for i in range(3):
            u = ((t - T_CRY) * 0.65 + i / 3) % 1.0
            hx, hy = O.baby_pt(b[0], b[1], b[2], *O.BABY_FACE)
            draw_text(cr, "waah", hx - 70 - 140 * u, hy - 80 - 160 * u, 44 + 22 * u, color=(30, 30, 34),
                      rot=-0.15 + 0.06 * math.sin(t * 20 + i), alpha=math.sin(math.pi * u) * k)
def zzz(cr, t, p, ly):
    if ly != "front": return
    b = baby(t)
    if b and T_SLEEP + 0.8 <= t < K0:
        for i in range(3):
            u = ((t - T_SLEEP) * 0.45 + i / 3) % 1.0
            hx, hy = O.baby_pt(b[0], b[1], b[2], *O.BABY_FACE)
            draw_text(cr, "z", hx - 75 - 40 * u + 10 * math.sin(u * 6), hy - 75 - 140 * u, 32 + 24 * u, color=(30, 30, 34),
                      alpha=math.sin(math.pi * u) * ramp(t, T_SLEEP + 0.8, T_SLEEP + 1.4))
    if T_OUT + 0.5 <= t < KISS + 0.3:                                 # his: bigger, up and to the left
        hx, hy = p["head"]
        fade = 1 - ramp(t, KISS, KISS + 0.3)
        for i in range(3):
            u = ((t - T_OUT) * 0.38 + i / 3) % 1.0
            draw_text(cr, "Z", hx - 135 - 80 * u + 12 * math.sin(u * 5), hy - 40 - 170 * u, 44 + 34 * u, color=(30, 30, 34),
                      alpha=math.sin(math.pi * u) * ramp(t, T_OUT + 0.5, T_OUT + 1.2) * fade)
for k in range(4): S.sfx(T_CRY + 0.05 + k * 1.0, "wah", 0.045)
S.sfx(T_HUSH + 0.2, "wah", 0.02, dur=0.5)

# his arms: up to meet the baby, cradling it, then cradling nothing until he lowers them
def hold_e(t): return smooth(ramp(t, G0 - 0.15, G0 + 0.45)) * (1 - smooth(ramp(t, T_ASK - 1.9, T_ASK - 1.1)))
def cradle_hook(tt, p):
    e = hold_e(tt)
    if e < 0.001: return p
    if tt < G0 + 0.45: b = arc(mom_spot(tt), his_spot(tt), smooth(ramp(tt, G0, G1)))
    elif tt < K0 + 0.25: b = baby(tt)
    else: b = his_spot(K0 - 0.3)                                     # she took it: the arms keep its shape
    lh = O.baby_pt(b[0], b[1], b[2], -78, 40); rh = O.baby_pt(b[0], b[1], b[2], 105, 28)
    p["lhand"] = lerp(p["lhand"], lh, e); p["rhand"] = lerp(p["rhand"], rh, e)
    p["lelb"] = lerp(p["lelb"], (p["lelb"][0] - 30, lh[1] + 30), e); p["relb"] = lerp(p["relb"], (p["relb"][0] + 20, rh[1] + 40), e)
    if e > 0.5: p["lhand_t"] = p["rhand_t"] = "grip"
    s_ = sway(tt)                                                    # weight shift: hips lead, head follows
    for k_, a in (("hip", 14), ("neck", 22), ("head", 28), ("lknee", 8), ("rknee", 8)): p[k_] = (p[k_][0] + a * s_, p[k_][1])
    p["tilt"] = p.get("tilt", 0.0) + 0.07 * sway(tt - 0.15)
    return p

# ================================================================ HIM
HEADS = dict(droop=dict(head=(548, 668), neck=(542, 784)), nod=dict(head=(552, 700), neck=(544, 800)),
             out=dict(head=(552, 690), neck=(543, 796), hip=(540, 1132), lknee=(506, 1308), rknee=(574, 1308)))
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(0.6, react="dead_stare", lines=2, face="deadpan")
S.set(3.0, "stand", "dead_stare", dur=0.3, lid=1.0)
S.set(3.4, "stand", "dead_stare", dur=0.4)
S.camera(M_IN0 - 0.4, *CAM_A, dur=1.8)
S.set(M_IN0 + 0.3, "stand", "dead_stare", dur=0.4, look=(0.8, 0.0))                          # eyes first...
S.set(M_IN0 + 0.7, "stand", "dead_stare", dur=0.6, look=(0.8, 0.0), tilt=-0.04)                # ...then the head
S.set(M_IN1 - 0.2, "stand", "dead_stare", dur=0.4, look=(0.6, 0.1), tilt=0.0)
S.set(G0 - 0.2, "hold_front", "dead_stare", dur=0.5, look=(0.4, 0.4))                         # arms come up to take it
S.set(G1 + 0.2, "hold_front", "dead_stare", dur=0.4, look=(0.2, 0.8))                         # looks down at it
S.set(RUN0 + 0.15, "hold_front", "dead_stare", dur=0.35, look=(0.6, 0.0))                      # watches her go
S.set(RUN1 + 0.9, "hold_front", "dead_stare", dur=0.3, look=(0.0, 0.0))                        # at us
S.blink(RUN1 + 1.4)
S.set(RUN1 + 2.0, "hold_front", "dead_stare", dur=0.5, look=(0.0, 0.8))                        # at it. it's looking at him.
# it cries. frazzled.
S.set(T_CRY + 0.3, "hold_front", "dead_stare", dur=0.12, ease="snap", eyescale=1.15, lid=0.0, look=(0.0, 0.8))
S.set(T_CRY + 0.8, "hold_front", "dead_stare", dur=0.15, eyescale=1.15, lid=0.0, frizz=1.0, sweat=0.5, look=(0.75, 0.0))   # the door
S.sfx(T_CRY + 0.8, "boing", 0.02)
S.set(T_CRY + 1.5, "hold_front", "holding_it", dur=0.15, eyescale=1.1, frizz=1.0, sweat=0.8, twitch=0.6, look=(0.0, 0.8))
S.set(T_CRY + 2.1, "hold_front", "holding_it", dur=0.15, eyescale=1.1, frizz=1.0, sweat=1.0, twitch=0.8, look=(-0.8, 0.0))
S.set(T_CRY + 2.7, "hold_front", "holding_it", dur=0.3, eyescale=1.1, frizz=1.0, sweat=1.0, twitch=0.8, quiver=0.7, look=(0.0, 0.0))  # at us
S.set(R0 - 0.6, "hold_front", "holding_it", dur=0.5, frizz=1.0, sweat=1.0, quiver=0.5, breath=1.8, breath_rate=2.0, look=(0.0, 0.8))
# rocks it
S.set(R0 + 0.4, "hold_front", "resigned", dur=1.0, frizz=1.0, sweat=0.8, look=(0.0, 0.75))
S.set(T_HUSH, "hold_front", "resigned", dur=0.8, frizz=1.0, sweat=0.4, look=(0.0, 0.75))
S.set(T_SLEEP + 0.4, "hold_front", "deadpan", dur=0.7, frizz=0.0, sweat=0.2, look=(0.0, 0.75))  # it's out. the hair settles.
S.set(T_SLEEP + 1.8, "hold_front", "deadpan", dur=0.6, look=(0.0, 0.0))                          # at us
S.camera(T_SLEEP + 1.0, 2730, 950, 1.06, 6.0)
S.set(T_NOD, "hold_front", "sleepy", dur=1.6, lid=0.6, look=(0.0, 0.3), **HEADS["droop"])
S.set(T_NOD + 1.5, "hold_front", "sleepy", dur=0.8, lid=0.9, tilt=0.12, **HEADS["nod"])          # head sinks...
S.set(T_NOD + 2.35, "hold_front", "sleepy", dur=0.15, ease="snap", lid=0.25, eyescale=1.08, tilt=0.0)   # catches it
S.set(T_NOD + 2.7, "hold_front", "sleepy", dur=0.9, lid=0.8, tilt=0.06, **HEADS["droop"])
S.set(T_OUT, "hold_front", "asleep", dur=1.0, fx_zzz=0.0, tilt=0.2, **HEADS["out"])
S.sfx(T_OUT + 0.8, "snore", 0.03, dur=1.6); S.sfx(T_OUT + 2.8, "snore", 0.028, dur=1.6)
S.camera(OUT0 - 0.8, *CAM_A, dur=1.4)
S.sfx(T_OUT + 4.8, "snore", 0.025, dur=1.6)
S.set(K0, "hold_front", "asleep", dur=0.3, fx_zzz=0.0, tilt=0.16, **HEADS["out"])
# kissed. wakes. blushes.
S.sfx(KISS, "pop", 0.04)
S.set(T_WAKE, "hold_front", "dead_stare", dur=0.14, ease="snap", eyescale=1.14, lid=0.0, look=(0.0, 0.0))
S.sfx(T_WAKE, "boing", 0.02)
S.set(T_WAKE + 0.5, "hold_front", "dead_stare", dur=0.35, look=(0.0, 0.85))                      # his arms: empty
S.set(T_WAKE + 1.1, "hold_front", "dead_stare", dur=0.3, look=(0.75, 0.0))                       # her
S.set(T_WAKE + 1.4, "hold_front", "dead_stare", dur=1.4, look=(0.75, 0.0), blush=1.0)            # blush builds
S.set(BYE1 + 0.3, "hold_front", "dead_stare", dur=0.5, look=(0.0, 0.0), blush=1.0)               # at us
S.blink(BYE1 + 1.5)
S.set(T_ASK - 1.9, "stand", "dead_stare", dur=0.9, blush=1.0)
S.t = T_ASK
S.camera(T_ASK - 1.2, 2690, 950, 1.05, 1.2)
S.camera(T_ASK + 6.9, 2680, 955, 1.1, 3.0)
S.the_ask(T_ASK, hold=8.0, push=False, keep=dict(blush=1.0))

def kiss_fx(cr, t, p, ly):
    if ly == "front" and KISS <= t < KISS + 0.45:
        hx, hy = p["head"]
        L.burst_lines(cr, hx + 100, hy + 20, (t - KISS) / 0.45, r0=26, r1=62, n=6, sid=71)

# the wrapper pile, beside him (not in front of anyone), and a few loose wrappers on the ground
LOOSE = [(2600, 0.9, 1), (2660, 0.8, 2), (2370, 1.0, 3), (3050, 0.8, 4), (2950, 0.7, 5)]
def pile(cr, t, p, ly):
    if ly != "back": return
    O.draw_wrapper_pile(cr, *PILE)
    for x, sc, k in LOOSE: O.draw_wrapper(cr, x, FLOOR_Y - 14 * sc, sc, sid=7700 + k)

# ---------------------------------------------------------------- draw order + hooks
S.props.insert(0, pile)
for f in (mom, baby_draw, zzz, kiss_fx): S.prop(f)
S.hook(cradle_hook)

if __name__ == "__main__":
    S.render("day006.mp4")
