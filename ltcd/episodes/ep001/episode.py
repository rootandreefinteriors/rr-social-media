"""Let the comments decide — Episode 1: "the ask".

He walks in from off-screen left, turns to camera, pulls a giant clipboard out of where a pocket would be (cartoon:
it keeps coming), plucks the pen from the clip, scribbles (we only see the back of the board), flips it round:
TELL ME WHAT TO DO NEXT IN THE COMMENTS — and holds it there, blinking at us, until the hard cut.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import ltcd as L
from ltcd import P, Track, smooth, ramp, back_out, lerp

DUR = 22.5
SIGN = ["TELL ME", "WHAT TO DO", "NEXT IN THE", "COMMENTS"]
BW, BH = 540, 600                 # clipboard size (world px)
HOLD = (540, 1112)                # board centre while held up
POCKET = (612, 1150)              # 'where a pocket would be' (his right hip, screen right)

# ---------------------------------------------------------------- body ---
STAND = P()
SETTLE = P(squash=0.5)
REACH = P(relb=(604, 1020), rhand=(616, 1150), look=(0.45, 0.65), tilt=0.07, swing=0.0)
PULL_HI = P(relb=(690, 860), rhand=(650, 560), look=(0.35, -0.55), tilt=-0.05, swing=0.0, brow=0.2)
LOOK_DOWN = P(look=(0.1, 0.75), tilt=0.04, swing=0.0, mouth=-0.1)
FRONT = P(look=(0.0, 0.0), swing=0.0)

pose = Track([
    (0.0, STAND, 0),
    (2.62, SETTLE, 0.08), (2.75, STAND, 0.25),          # skid to a stop, little squash
    (3.55, REACH, 0.35),
    (4.0, PULL_HI, 0.85),                               # the board just keeps coming out
    (5.0, P(look=(0.2, 0.3), swing=0.0), 0.45),
    (5.55, LOOK_DOWN, 0.3),
    (8.85, FRONT, 0.4),
    (12.0, P(FRONT, tilt=0.11, brow=0.45), 0.6),        # expectant head tilt
    (16.6, P(FRONT, tilt=0.0, brow=0.15), 0.6),
    (18.0, P(FRONT, eyescale=1.16, brow=0.35), 0.5),    # leans in, eyes wide
    (19.6, P(FRONT, eyescale=1.0, brow=0.1, tilt=-0.07), 0.7),
])
xt = Track([(0.0, -900, 0), (0.05, 0, 2.55)])
cam = Track([(0.0, (540, 960, 1.0), 0), (9.6, (540, 1030, 1.08), 12.5)])

# ---------------------------------------------------------------- board ---
def board(t, p):
    """clipboard state: centre, rotation, x-scale, flip (0 back .. 1 front), clip line while emerging."""
    if t < 3.95: return None
    hx, hy = p["rhand"]
    if t < 4.9:                                          # emerging from the 'pocket', hanging from his hand
        return dict(c=(hx - 12, hy + BH / 2 - 18), rot=0.07, sx=0.82, flip=0.0, clip=POCKET[1] + 4)
    if t < 5.05:                                         # POP — springs to full size
        u = back_out((t - 4.9) / 0.15)
        return dict(c=(hx - 12, hy + BH / 2 - 18), rot=0.07 * (1 - u), sx=0.82 + 0.18 * u, flip=0.0, clip=None)
    u = ramp(t, 5.05, 5.55)                              # brought down to the chest, back towards camera
    top_pos = (PULL_HI["rhand"][0] - 12, PULL_HI["rhand"][1] + BH / 2 - 18)
    c = lerp(top_pos, (HOLD[0], HOLD[1] + 15), u)
    f = ramp(t, 8.95, 9.45)                              # the flip
    lift = -14 * math.sin(math.pi * ramp(t, 8.95, 9.45))
    y = c[1] + lift - 15 * f
    # presentation beats while holding it up
    bump = -16 * math.exp(-((t - 10.05) / 0.09) ** 2)
    shake = sum(math.exp(-((t - k) / 0.07) ** 2) for k in (14.6, 14.95))
    return dict(c=(c[0], y + bump), rot=0.0, sx=1.0 + 0.05 * shake, flip=f, clip=None)

_emerge_c = {}
def hook(t, p):
    b = board(t, p)
    if b is None: return p
    if t >= 5.05:   # both hands on the board edges
        u = ramp(t, 5.05, 5.45)
        cx, cy = b["c"]; hw = BW * b["sx"] * abs(math.cos(math.pi * b["flip"])) / 2
        hw = max(hw, 60)
        lh, rh = (cx - hw - 4, cy + 30), (cx + hw + 4, cy + 30)
        p["lhand"] = lerp(p["lhand"], lh, u); p["lelb"] = lerp(p["lelb"], (cx - hw * 0.55, cy - 40), u)
        p["rhand"] = lerp(p["rhand"], rh, u); p["relb"] = lerp(p["relb"], (cx + hw * 0.55, cy - 40), u)
        # pluck the pen from the clip, scribble behind the top edge, put it back
        pen_u = ramp(t, 5.6, 5.85) * (1 - ramp(t, 8.6, 8.85))
        if pen_u > 0:
            top = cy - BH / 2
            busy = sum(ramp(t, a, a + 0.05) * (1 - ramp(t, b_ - 0.05, b_)) for a, b_ in ((6.0, 6.9), (7.1, 7.8), (8.0, 8.45)))
            jx = (30 * math.sin(t * 21) + 14 * math.sin(t * 8.3)) * busy
            jy = (9 * math.sin(t * 33) + 5 * math.sin(t * 13)) * busy
            dot = -14 * math.exp(-((t - 8.52) / 0.04) ** 2)          # the full stop
            write = (cx + 125 + jx, top + 8 + jy + dot)
            p["rhand"] = lerp(p["rhand"], write, pen_u)
            p["relb"] = lerp(p["relb"], (cx + 150, top + 170), pen_u)
    return p

FRONT_TEXT = L.sign_front(" ".join(SIGN), lines=SIGN)

def props(cr, t, p, layer):
    b = board(t, p)
    if b is None: return
    behind = t < 5.42                                    # while it comes out it passes behind his head
    if (layer == "back") != behind:
        if layer == "front" and behind and 3.95 <= t < 5.05:   # fist on top of the board as he pulls
            hx, hy = p["rhand"]; L.sketch_circle(cr, hx, hy, 17, 6, sid=410)
        return
    pen_u = ramp(t, 5.6, 5.85) * (1 - ramp(t, 8.6, 8.85))
    if 5.6 <= t <= 8.85 and pen_u > 0.02:               # pen sticks up above the board while he writes
        hx, hy = p["rhand"]
        L.draw_pen(cr, hx, hy, ang=0.35, s=1.0)
        busy = sum(ramp(t, a, a + 0.05) * (1 - ramp(t, b_ - 0.05, b_)) for a, b_ in ((6.0, 6.9), (7.1, 7.8), (8.0, 8.45)))
        if busy > 0.3:                                   # cartoon scribble marks
            for k in range(3):
                ang = -math.pi / 2 + (k - 1) * 0.55
                L.motion_lines(cr, hx + 20, hy - 95, ang, n=1, length=34, alpha=busy, sid=400 + k + L.BOIL % 5)
    L.draw_clipboard(cr, b["c"][0], b["c"][1], BW * b["sx"], BH, rot=b["rot"], flip=b["flip"],
                     front=FRONT_TEXT, clip_y=b["clip"])
    if 3.95 <= t < 5.05:                                 # speed lines out of the 'pocket'
        if t < 4.9:
            L.motion_lines(cr, POCKET[0] - 10, POCKET[1] + 30, math.pi / 2, n=3, length=50, spread=40, sid=420)
    if t >= 5.4:                                         # thumbs over the edges (he's gripping it)
        for side in ("lhand", "rhand"):
            if side == "rhand" and 5.6 <= t <= 8.85: continue
            x, y = p[side]
            sgn = 1 if side == "lhand" else -1
            cr.move_to(x - sgn * 4, y - 14); cr.curve_to(x + sgn * 20, y - 16, x + sgn * 26, y + 4, x + sgn * 8, y + 10)
            L.stroke_ink(cr, 6)
    if 8.95 < t < 9.5:                                   # whip lines on the flip
        cx, cy = b["c"]
        a = math.sin(math.pi * ramp(t, 8.95, 9.5))
        for side in (-1, 1):
            L.motion_lines(cr, cx + side * (BW / 2 + 30), cy, math.pi / 2 if side > 0 else -math.pi / 2, n=3,
                           length=70, spread=60, alpha=a, sid=430 + side)

blinks = [1.6, 3.35, 6.6, 10.8, 13.4, 13.62, 16.2, 19.1, 21.2]
sfx = [
    (2.62, "thud", 0.25),                  # skids to a stop
    (3.97, "zip", 0.55),                   # zwiiip — it keeps coming
    (4.9, "pop", 0.6),                     # POP
    (5.48, "tap", 0.35),                   # board settles against his chest
    (5.68, "pop", 0.25),                   # pen plucked from the clip
    (6.0, "scribble", 0.5, dict(dur=0.9)),
    (7.1, "scribble", 0.5, dict(dur=0.7)),
    (8.0, "scribble", 0.5, dict(dur=0.45)),
    (8.5, "tap", 0.3),                     # full stop
    (8.72, "zip_down", 0.25),              # pen back in the clip
    (8.98, "flip", 0.6),                   # FWIP
    (10.0, "tap", 0.3),
    (14.6, "tap", 0.35), (14.95, "tap", 0.35),
] + [(b, "blink", 0.14) for b in blinks if b > 9.5]

L.configure(duration=DUR, pose_track=pose, x_track=xt, cam_track=cam, props=props, pose_hook=hook, sfx=sfx,
            blinks=blinks)

if __name__ == "__main__":
    L.main("ltcd_ep001_the_ask.mp4")
