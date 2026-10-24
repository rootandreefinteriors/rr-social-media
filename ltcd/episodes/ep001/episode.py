"""Let the comments decide — Episode 1: "the ask" (v2).

He peeks in from the left edge, notices us, startles, smiles shyly and walks in. A shy wave. "One sec" finger.
Pats his hips — a pocket pops into existence on his hip — he reaches in up to the elbow, rummages (tongue out),
and pulls out a clipboard that keeps coming... and coming... POP, full size. Plucks the pen, writes (tongue out),
full stop, admires it, flips it: TELL ME WHAT TO DO NEXT IN THE COMMENTS. Hopeful little hops, taps COMMENTS,
looks back at us pleading, blushes, leans in. Hard cut.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import ltcd as L
from ltcd import pose, Track, ramp, pulse, lerp, back_out, smooth

DUR = 26.0
SIGN = ["TELL ME", "WHAT TO DO", "NEXT IN THE", "COMMENTS"]
BW, BH = 520, 580
HOLD = (540, 1140)
POCKET = (588, 1092)
PULL_A, PULL_C, PULL_B = (588, 1092), (700, 830), (735, 470)

def hopv(t):                     # little hopeful hops while holding the sign
    return 16 * (pulse(t, 13.95, 0.09) + pulse(t, 14.35, 0.09)) + 9 * (pulse(t, 23.9, 0.1) + pulse(t, 24.3, 0.1))

# ------------------------------------------------------------------ body ---
F = lambda body, face, **kw: pose(body, face, **kw)
keys = [
    (0.0,  F("stand", "neutral", lean=0.25, look=(0.7, -0.1), smile=0.1), 0),
    (0.9,  F("stand", "neutral", lean=0.25, look=(0.25, 0.0), smile=0.1), 0.25, "out"),          # ...sees us
    (1.1,  F("stand", "surprised", lean=0.21, look=(0.25, 0.0)), 0.12, "snap"),                    # !
    (1.45, F("stand", "shy", lean=0.24, look=(0.3, 0.05)), 0.35),
    (1.75, F("stand", "shy", lean=0.0, look=(0.2, 0.0), blush=0.6), 0.6),                          # walks in
    (3.55, F("stand", "happy", stretch=-0.35, look=(0.0, 0.0)), 0.1, "snap"),                      # skid stop
    (3.7,  F("stand", "happy", stretch=0.0), 0.3, "back"),
    (3.9,  F("wave", "shy", blush=0.9, smile=0.75, tilt=-0.06), 0.25, "back"),                     # hi.
    (4.95, F("point_up", "eager", tilt=0.05, open=0.0, smile=0.6), 0.2, "snap"),                   # one sec
    (5.55, F("hands_hips", "thinking", look=(0.0, 0.7), tilt=0.06), 0.2),                         # pat pat
    (6.3,  F("hands_hips", "surprised", look=(0.35, 0.75), eyescale=1.08, open=0.3), 0.12, "snap"),  # a pocket!
    (6.5,  F("hands_hips", "concentrating", look=(0.35, 0.8), tilt=0.1, lhand_t="fist"), 0.25),     # rummage
    (7.6,  F("hands_hips", "eager", look=(0.4, 0.4), lhand_t="fist"), 0.12, "snap"),               # got it
    (7.75, F("hands_hips", "surprised", look=(0.55, -0.85), eyescale=1.1, open=0.5, lhand_t="fist"), 0.9),  # it keeps coming
    (8.92, F("stand", "delighted", look=(0.3, -0.4), eyescale=1.1), 0.1, "snap"),                  # POP
    (9.3,  F("hold_front", "happy", look=(0.0, 0.4)), 0.3),
    (10.0, F("hold_front", "concentrating", look=(0.45, 0.9), tilt=0.1), 0.25),                     # writing
    (12.55, F("hold_front", "proud", look=(0.0, 0.6), tilt=0.0), 0.2),                              # admire
    (12.95, F("hold_front", "eager", look=(0.0, 0.0)), 0.25),
    (13.5, F("hold_front", "hopeful", look=(0.0, 0.0)), 0.3),
    (15.05, F("hold_front", "hopeful", look=(-0.35, 0.85)), 0.25),                                  # taps COMMENTS
    (16.35, F("hold_front", "pleading", look=(0.0, 0.0)), 0.3),
    (17.5, F("hold_front", "shy", look=(0.0, 0.0), blush=1.0, smile=0.6), 0.35),
    (19.4, F("hold_front", "pleading", look=(0.0, -0.05), curl=0.2), 0.8),                           # leans in
    (22.3, F("hold_front", "hopeful", tilt=0.12), 0.5),
    (23.6, F("hold_front", "eager", tilt=0.04, smile=0.8, open=0.0), 0.3),
    (25.0, F("hold_front", "hopeful", tilt=0.0), 0.4),
]
body = Track(keys)
xt = Track([(0.0, -800, 0), (0.15, -605, 0.6, "out"), (1.75, 0, 1.85)])
cam = Track([(0.0, (540, 1000, 1.22), 0), (13.4, (540, 1010, 1.26), 4.0), (19.4, (540, 1020, 1.36), 2.0)])

# ---------------------------------------------------------------- board ---
def _bezpt(a, c, b, u):
    return ((1 - u) ** 2 * a[0] + 2 * (1 - u) * u * c[0] + u * u * b[0], (1 - u) ** 2 * a[1] + 2 * (1 - u) * u * c[1] + u * u * b[1])

def pull_hand(t):
    return _bezpt(PULL_A, PULL_C, PULL_B, ramp(t, 7.72, 8.9, "smooth"))

def board(t):
    if t < 7.72: return None
    if t < 8.9:
        return dict(mode="narrow", a=POCKET, b=pull_hand(t))
    top_c = (PULL_B[0] - 20, PULL_B[1] + BH / 2 - 10)
    if t < 9.2:
        s = back_out((t - 8.9) / 0.2, 2.0)
        return dict(mode="full", c=top_c, w=70 + (BW - 70) * s, flip=0.0, layer="back")
    u = ramp(t, 9.2, 9.62, "smooth")
    c = lerp(top_c, HOLD, u)
    f = ramp(t, 12.95, 13.45, "smooth")
    lift = -30 * math.sin(math.pi * f) - 20 * f
    bump = -10 * pulse(t, 13.5, 0.07)
    return dict(mode="full", c=(c[0], c[1] + lift + bump - hopv(t)), w=BW, flip=f, layer="back" if t < 9.62 else "front")

FRONT = L.sign_front(" ".join(SIGN), lines=SIGN)
BUSY = ((10.1, 11.0), (11.2, 11.8), (11.95, 12.35))
def busy(t): return sum(ramp(t, a, a + 0.05) * (1 - ramp(t, b - 0.05, b)) for a, b in BUSY)
def pen_on(t): return 9.85 <= t < 12.8

def hook(t, p):
    hv = hopv(t) + 14 * pulse(t, 1.12, 0.08)                       # hops (startle + hopeful hops with the sign)
    if hv > 0.05:
        for k in L.JOINTS: p[k] = (p[k][0], p[k][1] - hv)
    p["hop"] = hv
    if 3.9 <= t < 4.95:                                            # wave
        p["rhand"] = (p["rhand"][0] + 26 * math.sin((t - 3.9) * 15), p["rhand"][1])
    if 5.55 <= t < 6.3:                                            # pat pat
        p["lhand"] = (p["lhand"][0], p["lhand"][1] - 18 * (pulse(t, 5.75, 0.05) + pulse(t, 5.98, 0.05)))
        p["rhand"] = (p["rhand"][0], p["rhand"][1] - 18 * (pulse(t, 5.86, 0.05) + pulse(t, 6.1, 0.05)))
    if 6.45 <= t < 7.72:                                           # arm into the pocket, rummaging
        u = ramp(t, 6.45, 6.7, "out")
        jig = 10 * math.sin(t * 31) * ramp(t, 6.75, 6.85) * (1 - ramp(t, 7.5, 7.6))
        p["rhand"] = lerp(p["rhand"], (POCKET[0] + jig * 0.4, POCKET[1] + 4), u)
        p["relb"] = lerp(p["relb"], (POCKET[0] + 60 + jig, POCKET[1] - 120 + jig * 0.5), u)
        if u > 0.6: p["rhand_t"] = "none"
        p["neck"] = (p["neck"][0] + jig * 0.3, p["neck"][1])
    if 7.72 <= t < 8.9:                                            # pulling it out (the fist is drawn over the board)
        h = pull_hand(t); p["rhand"] = h; p["relb"] = ((h[0] + 640) / 2 + 40, (h[1] + 900) / 2); p["rhand_t"] = "none"
    if 8.9 <= t < 9.25:
        p["rhand"] = (PULL_B[0] - 5, PULL_B[1] + 10); p["relb"] = (690, 650); p["rhand_t"] = "fist"
    b = board(t)
    if b and b["mode"] == "full" and t >= 9.2:                     # hands on the board edges
        u = ramp(t, 9.2, 9.55)
        cx, cy = b["c"]; hw = max(60, b["w"] * abs(math.cos(math.pi * b["flip"])) / 2)
        p["lhand"] = lerp(p["lhand"], (cx - hw - 2, cy + 10), u); p["lelb"] = lerp(p["lelb"], (cx - hw * 0.6, cy - 70), u)
        p["rhand"] = lerp(p["rhand"], (cx + hw + 2, cy + 10), u); p["relb"] = lerp(p["relb"], (cx + hw * 0.6, cy - 70), u)
        if u > 0.5: p["lhand_t"] = p["rhand_t"] = "grip"
        if pen_on(t):                                              # pluck pen, scribble behind the top edge
            w = ramp(t, 9.75, 9.95) * (1 - ramp(t, 12.6, 12.8))
            top = cy - BH / 2
            jx = (34 * math.sin(t * 21) + 16 * math.sin(t * 8.3)) * busy(t)
            jy = (10 * math.sin(t * 33) + 6 * math.sin(t * 13)) * busy(t) - 16 * pulse(t, 12.45, 0.04)
            p["rhand"] = lerp(p["rhand"], (cx + 95 + jx, top + 30 + jy), w)
            p["relb"] = lerp(p["relb"], (cx + 200, top + 160), w)
            if w > 0.3: p["rhand_t"] = "none"
        if 15.05 <= t < 16.75:                                     # left hand lets go, taps COMMENTS
            w = ramp(t, 15.05, 15.3) * (1 - ramp(t, 16.45, 16.75))
            tap = -16 * (pulse(t, 15.6, 0.05) + pulse(t, 16.0, 0.05))
            p["lhand"] = lerp(p["lhand"], (cx - 120, cy + 205 + tap), w)
            p["lelb"] = lerp(p["lelb"], (cx - 230, cy + 120), w)
            if w > 0.4: p["lhand_t"] = "none"; p["_point"] = w
    return p

def props(cr, t, p, layer):
    b = board(t)
    if b and b["mode"] == "narrow" and layer == "front":         # it keeps coming out of the pocket
        (ax, ay), (bx, by) = b["a"], b["b"]
        ang = math.atan2(by - ay, bx - ax); L_ = math.hypot(bx - ax, by - ay)
        cr.save(); cr.translate(ax, ay); cr.rotate(ang)
        L.sketch_rect(cr, -10, -35, L_ + 6, 35, 7, sid=300)
        cr.restore()
        L.motion_lines(cr, ax + 10, ay - 40, -math.pi / 2 + 0.3, n=3, length=50, spread=24, sid=440, alpha=0.8)
    if 6.25 <= t < 9.45 and layer == "front":                     # the pocket (covers the arm going in / board coming out)
        u = ramp(t, 6.25, 6.42, "linear") * (1 - ramp(t, 9.25, 9.42, "linear"))
        L.draw_pocket(cr, POCKET[0], POCKET[1], u)
        if t < 6.6: L.burst_lines(cr, POCKET[0], POCKET[1] - 10, (t - 6.25) / 0.35, r0=60, r1=110, n=8, sid=5, width=4)
    if b and b["mode"] == "narrow" and layer == "front":         # his fist over the top of it
        h = pull_hand(t); L.sketch_circle(cr, h[0], h[1], 22, 6, sid=450)
    if b and b["mode"] == "full" and b["layer"] == layer:
        if layer == "front" and pen_on(t):
            w = ramp(t, 9.75, 9.95) * (1 - ramp(t, 12.6, 12.8))
            if w > 0.3:
                hx, hy = p["rhand"]; L.draw_pen(cr, hx, hy - 20, ang=0.3)
                if busy(t) > 0.3:
                    for k in range(3):
                        L.motion_lines(cr, hx + 26, hy - 120, -math.pi / 2 + (k - 1) * 0.55, n=1, length=30, alpha=busy(t), sid=460 + k + L.ink.BOIL % 5)
        L.draw_clipboard(cr, b["c"][0], b["c"][1], b["w"], BH, flip=b["flip"], front=FRONT)
        if layer == "back" and t < 9.1:
            L.burst_lines(cr, b["c"][0], b["c"][1], (t - 8.9) / 0.4, r0=BW * 0.45, r1=BW * 0.7, n=12, sid=7)
        if 12.95 < t < 13.5:                                      # whip lines on the flip
            a = math.sin(math.pi * ramp(t, 12.95, 13.5))
            for side in (-1, 1):
                L.motion_lines(cr, b["c"][0] + side * (BW / 2 + 30), b["c"][1], math.pi / 2 if side > 0 else -math.pi / 2,
                               n=3, length=70, spread=60, alpha=a, sid=470 + side)
    if layer == "front":
        L.draw_grips(cr, p)
        if p.get("_point", 0) > 0.4:                              # pointing hand in front of the sign
            x, y = p["lhand"]
            L.sketch_line(cr, [(x - 70, y + 40), (x, y)], 9, sid=480)
            L.draw_hand(cr, (x, y), (x - 70, y + 40), "point", -1, sid=481)

blinks = [2.6, 4.6, 9.4, 13.1, 17.0, 18.6, 18.82, 21.0, 22.5, 25.3]
sfx = [
    (1.1, "boop", 0.22),                                  # (startle)
    (3.55, "skid", 0.25), (3.62, "thud", 0.12),
    (5.75, "pat", 0.25), (5.86, "pat", 0.25), (5.98, "pat", 0.25), (6.1, "pat", 0.25),
    (6.27, "pop", 0.28),                                  # a pocket appears
    (6.6, "rummage", 0.35, dict(dur=0.95)),
    (7.6, "tick", 0.2),
    (7.74, "slide_up", 0.28, dict(dur=1.15)),             # it keeps coming
    (8.9, "pop", 0.35), (8.92, "boing", 0.22),            # POP
    (9.28, "zip_down", 0.14),                             # pocket closes
    (9.6, "tap", 0.2),
    (9.82, "tick", 0.2),                                  # pen
    (10.1, "scribble", 0.32, dict(dur=0.9)), (11.2, "scribble", 0.32, dict(dur=0.6)), (11.95, "scribble", 0.32, dict(dur=0.4)),
    (12.43, "tap", 0.18),                                 # full stop
    (12.7, "tick", 0.15),
    (12.97, "flip", 0.3),
    (13.95, "tap", 0.12), (14.35, "tap", 0.12),
    (15.58, "tap", 0.16), (15.98, "tap", 0.16),
    (17.5, "twinkle", 0.08),
    (23.9, "tap", 0.1), (24.3, "tap", 0.1),
] + [(b, "blink", 0.06) for b in blinks if b > 13]

L.configure(duration=DUR, pose_track=body, x_track=xt, cam_track=cam, props=props, pose_hook=hook, sfx=sfx, blinks=blinks)

if __name__ == "__main__":
    L.main("ltcd_ep001_the_ask.mp4")
