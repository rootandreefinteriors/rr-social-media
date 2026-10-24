"""Let the comments decide — Episode 1: "the ask" (v3, simplified).

Peeks in from the left, notices us, smiles shyly, walks in, shy wave. Looks down at his hip — a pocket appears where
a pocket would be — reaches in, pulls out a clipboard that keeps coming, POP, full size. Writes (tongue out), flips
it: TELL ME WHAT TO DO NEXT IN THE COMMENTS. Hopeful hops, blush, leans in. Hard cut.
Sound: soft footsteps, one pop, a scribble, a flip. That's all.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import ltcd as L
from ltcd import pose, Track, ramp, pulse, lerp, back_out

DUR = 23.0
SIGN = ["TELL ME", "WHAT TO DO", "NEXT IN THE", "COMMENTS"]
BW, BH = 470, 560
HOLD = (540, 1120)
POCKET = (588, 1092)
PULL_A, PULL_C, PULL_B = (588, 1092), (690, 860), (720, 520)
T_POCKET, T_REACH, T_PULL, T_POP = 5.2, 5.35, 6.35, 7.45
T_DOWN, T_PEN, T_WRITE0, T_WRITE1, T_FLIP = 7.75, 8.2, 8.45, 10.7, 11.35

def hopv(t):
    return 14 * (pulse(t, 12.4, 0.09) + pulse(t, 12.8, 0.09)) + 8 * (pulse(t, 20.9, 0.1) + pulse(t, 21.3, 0.1)) + 12 * pulse(t, 1.12, 0.08)

F = lambda body, face, **kw: pose(body, face, **kw)
body = Track([
    (0.0,  F("stand", "neutral", lean=0.25, look=(0.7, -0.1), smile=0.1), 0),
    (0.9,  F("stand", "neutral", lean=0.25, look=(0.25, 0.0), smile=0.1), 0.25, "out"),       # ...sees us
    (1.1,  F("stand", "surprised", lean=0.21, look=(0.25, 0.0)), 0.12, "snap"),
    (1.45, F("stand", "shy", lean=0.24, look=(0.3, 0.05)), 0.35),
    (1.75, F("stand", "shy", lean=0.0, look=(0.2, 0.0), blush=0.5), 0.6),                      # walks in
    (3.55, F("stand", "happy", stretch=-0.3, look=(0.0, 0.0)), 0.1, "snap"),
    (3.7,  F("stand", "happy", stretch=0.0), 0.3, "back"),
    (3.9,  F("wave", "shy", blush=0.9, smile=0.75, tilt=-0.06), 0.25, "back"),                 # hi.
    (5.0,  F("stand", "thinking", look=(0.4, 0.8), tilt=0.08), 0.25),                           # looks at his hip
    (5.25, F("stand", "surprised", look=(0.4, 0.8), eyescale=1.06, open=0.3), 0.1, "snap"),     # a pocket!
    (5.45, F("stand", "concentrating", look=(0.4, 0.8), tilt=0.1), 0.2),                        # reaches in
    (6.25, F("stand", "eager", look=(0.45, 0.3)), 0.1, "snap"),                                 # got it
    (6.4,  F("stand", "surprised", look=(0.5, -0.8), eyescale=1.08, open=0.4), 0.8),           # it keeps coming
    (7.47, F("stand", "delighted", look=(0.3, -0.4)), 0.1, "snap"),                             # POP
    (7.85, F("hold_front", "happy", look=(0.0, 0.4)), 0.3),
    (8.45, F("hold_front", "concentrating", look=(0.4, 0.9), tilt=0.08), 0.25),                # writing
    (10.8, F("hold_front", "proud", look=(0.0, 0.6), tilt=0.0), 0.2),                           # admires it
    (11.35, F("hold_front", "eager", look=(0.0, 0.0)), 0.25),
    (11.9, F("hold_front", "hopeful", look=(0.0, 0.0)), 0.3),
    (14.5, F("hold_front", "pleading", look=(0.0, -0.05)), 0.5),
    (16.0, F("hold_front", "shy", blush=1.0, smile=0.6), 0.35),                                 # blush
    (17.6, F("hold_front", "pleading", look=(0.0, -0.05)), 0.8),                                 # leans in
    (19.6, F("hold_front", "hopeful", tilt=0.1), 0.5),
    (20.7, F("hold_front", "eager", tilt=0.03, smile=0.8), 0.3),
    (22.0, F("hold_front", "hopeful", tilt=0.0), 0.4),
])
xt = Track([(0.0, -800, 0), (0.15, -605, 0.6, "out"), (1.75, 0, 1.85)])
cam = Track([(0.0, (540, 1000, 1.22), 0), (11.9, (540, 1010, 1.26), 3.0), (17.6, (540, 1020, 1.36), 2.0)])

def _bezpt(a, c, b, u):
    return ((1 - u) ** 2 * a[0] + 2 * (1 - u) * u * c[0] + u * u * b[0], (1 - u) ** 2 * a[1] + 2 * (1 - u) * u * c[1] + u * u * b[1])
def pull_hand(t):
    return _bezpt(PULL_A, PULL_C, PULL_B, ramp(t, T_PULL, T_POP))

def board(t):
    if t < T_PULL: return None
    if t < T_POP: return dict(mode="narrow", a=POCKET, b=pull_hand(t))
    top_c = (PULL_B[0] - 30, PULL_B[1] + BH / 2 - 10)
    if t < T_POP + 0.25:
        s = back_out((t - T_POP) / 0.22, 1.8)
        return dict(mode="full", c=top_c, w=70 + (BW - 70) * s, flip=0.0, layer="back")
    u = ramp(t, T_POP + 0.25, T_DOWN + 0.1)
    c = lerp(top_c, HOLD, u)
    f = ramp(t, T_FLIP, T_FLIP + 0.5)
    lift = -26 * math.sin(math.pi * f) - 16 * f
    return dict(mode="full", c=(c[0], c[1] + lift - hopv(t)), w=BW, flip=f, layer="back" if t < T_DOWN + 0.08 else "front")

FRONT = L.sign_front(" ".join(SIGN), lines=SIGN)
def writing(t): return ramp(t, T_WRITE0, T_WRITE0 + 0.1) * (1 - ramp(t, T_WRITE1 - 0.1, T_WRITE1))
def pen_w(t): return ramp(t, T_PEN, T_PEN + 0.2) * (1 - ramp(t, T_WRITE1 + 0.05, T_WRITE1 + 0.25))

def hook(t, p):
    hv = hopv(t)
    if hv > 0.05:
        for k in L.JOINTS: p[k] = (p[k][0], p[k][1] - hv)
    if 3.9 <= t < 5.0:                                             # shy wave
        p["rhand"] = (p["rhand"][0] + 24 * math.sin((t - 3.9) * 14), p["rhand"][1])
    if T_REACH <= t < T_PULL:                                      # hand into the pocket, rummage a little
        u = ramp(t, T_REACH, T_REACH + 0.25)
        jig = 8 * math.sin(t * 28) * ramp(t, T_REACH + 0.3, T_REACH + 0.4) * (1 - ramp(t, T_PULL - 0.2, T_PULL - 0.1))
        p["rhand"] = lerp(p["rhand"], (POCKET[0] + jig, POCKET[1] + 4), u)
        if u > 0.7: p["rhand_t"] = "none"
    if T_PULL <= t < T_POP:
        p["rhand"] = pull_hand(t); p["rhand_t"] = "none"
    if T_POP <= t < T_POP + 0.3:
        p["rhand"] = (PULL_B[0] - 5, PULL_B[1] + 8)
    b = board(t)
    if b and b["mode"] == "full" and t >= T_POP + 0.25:            # both hands on the board edges
        u = ramp(t, T_POP + 0.25, T_DOWN)
        cx, cy = b["c"]; hw = max(60, b["w"] * abs(math.cos(math.pi * b["flip"])) / 2)
        p["lhand"] = lerp(p["lhand"], (cx - hw - 2, cy - 80), u); p["lelb"] = (cx - hw + 30, cy - 200)
        p["rhand"] = lerp(p["rhand"], (cx + hw + 2, cy - 80), u); p["relb"] = (cx + hw - 30, cy - 200)
        if u > 0.5: p["lhand_t"] = p["rhand_t"] = "grip"
        w = pen_w(t)
        if w > 0:                                                  # right hand takes the pen and writes behind the top edge
            top = cy - BH / 2
            k = writing(t)
            jx = (30 * math.sin(t * 19) + 14 * math.sin(t * 7.3)) * k
            jy = (8 * math.sin(t * 29) + 5 * math.sin(t * 11)) * k
            p["rhand"] = lerp(p["rhand"], (cx + 90 + jx, top + 28 + jy), w)
            p["relb"] = (cx + 170, top + 120)
            if w > 0.3: p["rhand_t"] = "none"
    return p

def props(cr, t, p, layer):
    b = board(t)
    if layer == "front" and T_POCKET <= t < T_DOWN + 0.2:         # the pocket appears where a pocket would be
        u = ramp(t, T_POCKET, T_POCKET + 0.15, "linear") * (1 - ramp(t, T_DOWN, T_DOWN + 0.15, "linear"))
        if b and b["mode"] == "narrow":                          # the board coming out of it (drawn first)
            (ax, ay), (bx, by) = b["a"], b["b"]
            ang = math.atan2(by - ay, bx - ax); L_ = math.hypot(bx - ax, by - ay)
            cr.save(); cr.translate(ax, ay); cr.rotate(ang); L.sketch_rect(cr, -10, -32, L_ + 6, 32, 7, sid=300); cr.restore()
        L.draw_pocket(cr, POCKET[0], POCKET[1], u)
        if b and b["mode"] == "narrow":
            h = pull_hand(t); L.draw_hand(cr, h, (h[0] - 30, h[1] + 60), "mitt", 1, sid=450)
    if b and b["mode"] == "full" and b["layer"] == layer:
        if layer == "front" and pen_w(t) > 0.3:
            hx, hy = p["rhand"]; L.draw_pen(cr, hx, hy - 18, ang=0.3)
        L.draw_clipboard(cr, b["c"][0], b["c"][1], b["w"], BH, flip=b["flip"], front=FRONT)
        if layer == "back" and t < T_POP + 0.3:
            L.burst_lines(cr, b["c"][0], b["c"][1], (t - T_POP) / 0.4, r0=BW * 0.45, r1=BW * 0.68, n=10, sid=7)
    if layer == "front":
        L.draw_grips(cr, p)

blinks = [2.6, 4.7, 8.0, 11.6, 14.0, 16.9, 17.1, 19.3, 21.9]
sfx = [
    (T_POP, "pop", 0.22),
    (T_WRITE0, "scribble", 0.16, dict(dur=T_WRITE1 - T_WRITE0)),
    (T_FLIP, "flip", 0.18),
]
L.configure(duration=DUR, pose_track=body, x_track=xt, cam_track=cam, props=props, pose_hook=hook, sfx=sfx, blinks=blinks)

if __name__ == "__main__":
    L.main("ltcd_ep001_the_ask.mp4")
