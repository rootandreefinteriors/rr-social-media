"""Day 2 (TEST MODE cloud run 2026-10-24) — WAITING episode #1: nobody has commented yet.

SHOT 1  Exactly where Day 1 left him: centre stage, holding up the sign, staring at us. His foot taps. His eyes slide
        down to the sign (is it still there?), back up. One slow blink. The foot keeps tapping. The camera creeps.
SHOT 2  HARD CUT: sitting on the floor, still holding the sign up over his head. His arms sag, slowly, until the
        sign covers him completely -- only the hair curl sticks out. Hold. His head slides out sideways to check on us.
        Still nothing. Slow blink. Slides back.
SHOT 3  HARD CUT: flat on his back, the sign lying on top of him like a blanket. A clock ticks somewhere. His eyes
        slide over to us. A twitch builds. Slow blink.
SHOT 4  HARD CUT: a chalk outline of him on the floor, the sign lying across it. Nobody there. Hold.
        HARD CUT wider: he's standing right next to the outline, staring at us. Glances at it. Back to us.
        Then the ask, deadpan: digs at his hip, a fresh clipboard, scribble, flip. The old one stays on the floor.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
import moves as M
import ltcd as L
from ltcd import ramp, pulse, lerp, FLOOR_Y
from ink import smooth, sketch_rect, sketch_line, stroke_ink, INK

SIGN = ("TELL ME", "WHAT TO DO", "NEXT IN THE", "COMMENTS")
FRONT = L.sign_front(" ".join(SIGN), lines=list(SIGN))
BW, BH = 470, 560

L.POSES["flat"] = dict(L.POSES["lie_back"], lelb=(645, 1392), lhand=(815, 1402), relb=(645, 1430),
                       rhand=(815, 1446), lhand_t="mitt", rhand_t="mitt", nowalk=1.0)

CAM1 = (540, 1000, 1.22)          # Day 1's last framing
CAM2 = (440, 1010, 1.0)           # sitting, sign held high: wide enough that the board stays in the safe zone
CAM3 = (640, 1250, 1.06)          # on the floor
OUT_DX = -150                     # the chalk outline sits 150 px left of where he lay
CAM4A = (560, 1260, 1.15)          # the outline, nobody there
XS = 350                          # he stands here, right of the outline
CAM4B = (560, 1080, 0.85)         # wide: outline + him
CAM5 = (850, 1010, 1.1)           # the ask

S = M.Scene()
S.auto_blinks = False
S.camkeys[0] = (0.0, CAM1, 0); S.cam = CAM1

def held_sign(cx, cy):
    """hands on both sides of a front-facing sign centred at (cx, cy)."""
    def hk(p):
        hw = BW / 2
        p["lhand"] = (cx - hw - 2, cy - 80); p["lelb"] = (cx - hw + 30, cy - 200)
        p["rhand"] = (cx + hw + 2, cy - 80); p["relb"] = (cx + hw - 30, cy - 200)
        p["lhand_t"] = p["rhand_t"] = "grip"
        return p
    return hk

# ================================================================ SHOT 1: still here. still holding it.
T2 = 7.6
S.set(0.0, "hold_front", "dead_stare", dur=0.0)
S.blink(5.4)
S.set(2.4, "hold_front", "dead_stare", dur=0.45, look=(0.0, 0.85))              # eyes slide down to the sign
S.set(3.5, "hold_front", "dead_stare", dur=0.5, look=(0.0, 0.0))                # ...back to us
S.set(5.2, "hold_front", "dead_stare", dur=0.4, lid=1.0)                        # slow blink
S.set(5.75, "hold_front", "resigned", dur=0.6)
S.camera(0.6, 540, 1010, 1.34, 6.8)                                             # slow creep
TAPS = [1.0 + 0.62 * k for k in range(10)]
def tap(tt, p):
    if tt < T2:
        v = sum(16 * pulse(tt, a, 0.11) for a in TAPS)
        if v > 0.01: x, y = p["rfoot"]; p["rfoot"] = (x + 4, y - v); p["rfoot_dir"] = p.get("rfoot_dir", 0) - 0.4 * v / 16
    return p
S.hook(tap)
for a in TAPS[::2]: S.sfx(a + 0.11, "tap", 0.025)

def sign1(cr, tt, p, ly):
    if ly == "front" and tt < T2:
        L.draw_clipboard(cr, 540, 1120, BW, BH, flip=1.0, front=FRONT); L.draw_grips(cr, p)
S.prop(sign1)
S.hook(lambda tt, p: held_sign(540, 1120)(p) if tt < T2 else p)

# ================================================================ SHOT 2: sitting. the sign wins.
T3 = 16.2
XSIT = -100
S.cut(T2, cam=CAM2, x=XSIT)
S.set(T2, "sit_floor", "dead_stare", dur=0.0, nowalk=1.0)
SX = 540 + XSIT
def sign2_y(tt):                                                   # held high -> sags until it hides him
    return lerp(545, 1150, ramp(tt, T2 + 0.9, T2 + 5.0, "smooth"))
def sit_hold(tt, p):
    if T2 <= tt < T3: p = held_sign(SX, sign2_y(tt))(p)
    return p
S.hook(sit_hold)
S.set(T2 + 0.9, "sit_floor", "resigned", dur=2.5, nowalk=1.0)
S.set(T2 + 4.6, "sit_floor", "dead_stare", dur=0.4, nowalk=1.0)
# the peek: head slides out to the left of the sign, checks on us, slides back
TP0, TP1 = T2 + 6.0, T2 + 7.9
def peek(tt, p):
    u = ramp(tt, TP0, TP0 + 0.7) * (1 - ramp(tt, TP1, TP1 + 0.6))
    if u > 0.0:
        hx, hy = p["head"]; p["head"] = (hx - 265 * u, hy + 40 * u); p["tilt"] = p.get("tilt", 0.0) - 0.55 * u
        nx, ny = p["neck"]; p["neck"] = (nx - 60 * u, ny)
    return p
S.hook(peek)
S.set(TP0 + 0.9, "sit_floor", "dead_stare", dur=0.35, lid=1.0, nowalk=1.0)    # slow blink, half out
S.set(TP0 + 1.35, "sit_floor", "dead_stare", dur=0.4, nowalk=1.0)
S.sfx(T2 + 5.0, "pat", 0.03)                                       # the board settles on his knees
def sign2(cr, tt, p, ly):
    if ly == "front" and T2 <= tt < T3:
        L.draw_clipboard(cr, SX, sign2_y(tt), BW, BH, flip=1.0, front=FRONT); L.draw_grips(cr, p)
S.prop(sign2)

# ================================================================ SHOT 3: horizontal. a clock ticks.
T4 = 22.6
S.cut(T3, cam=CAM3, x=0)
S.set(T3, "flat", "dead_stare", dur=0.0, nowalk=1.0, look=(0.0, -0.6))     # staring at the ceiling
S.set(T3 + 2.2, "flat", "dead_stare", dur=0.6, nowalk=1.0, look=(0.0, 0.0))   # ...eyes slide over to us
S.set(T3 + 4.3, "flat", "dead_stare", dur=0.35, nowalk=1.0, lid=1.0)
S.set(T3 + 4.8, "flat", "resigned", dur=0.5, nowalk=1.0)
S.camera(T3 + 0.3, 630, 1275, 1.12, 6.0)
def lie_fx(tt, p):
    if T3 <= tt < T4: p["twitch"] = max(p.get("twitch", 0.0), ramp(tt, T3 + 3.0, T3 + 3.6) * (1 - ramp(tt, T3 + 5.2, T3 + 5.6)))
    return p
S.hook(lie_fx)
for k in range(6): S.sfx(T3 + 0.5 + k * 1.0, "tick", 0.03)
def blanket(cr, cx, cy, ang=0.03):
    """the clipboard, seen edge-on, lying flat (on him, or on the floor)."""
    cr.save(); cr.translate(cx, cy); cr.rotate(ang)
    sketch_rect(cr, -200, -16, 200, 12, 7, sid=300)
    sketch_rect(cr, 160, -30, 200, -16, 5, sid=301)                  # the clip, sticking up at one end
    cr.restore()
def sign3(cr, tt, p, ly):
    if ly == "front" and T3 <= tt < T4:
        nx, ny = p["neck"]; hx, hy = p["hip"]
        blanket(cr, (nx + hx) / 2 + 50, (ny + hy) / 2 - 30, math.atan2(hy - ny, hx - nx))
S.prop(sign3)

# ================================================================ SHOT 4: the outline.
LIE = L.POSES["flat"]
def chalk_outline(cr, dx):
    """a dashed outline of him lying there, traced on the floor."""
    J = {k: (LIE[k][0] + dx, LIE[k][1]) for k in ("head", "neck", "hip")}
    cr.save(); cr.set_dash([22, 16]); cr.set_line_cap(1)
    hx, hy = J["head"]
    cr.arc(hx, hy - 6, 118, 0.5, 2 * math.pi - 0.5); stroke_ink(cr, 6)     # open where it meets the body
    body = [(440, 1335), (600, 1350), (770, 1368), (960, 1390), (985, 1362), (1012, 1368), (1018, 1400),
            (1030, 1474), (440, 1474)]                              # torso, arms tucked in, feet sticking up
    cr.move_to(body[0][0] + dx, body[0][1])
    for x, y in body[1:]: cr.line_to(x + dx, y)
    stroke_ink(cr, 6)
    cr.restore()
    nx, ny = J["neck"]; px, py = J["hip"]
    blanket(cr, (nx + px) / 2 + 50, (ny + py) / 2 - 30, math.atan2(py - ny, px - nx))

T5 = T4 + 1.8                                                      # cut wider: he's right there
S.cut(T4, cam=CAM4A, x=2400)                                       # he is not in this shot
S.set(T4, "stand", "dead_stare", dur=0.0)
S.camera(T4 + 0.2, 540, 1270, 1.22, 1.6)
S.cut(T5, cam=CAM4B, x=XS)
S.set(T5, "stand", "dead_stare", dur=0.0)
S.set(T5 + 1.2, "stand", "dead_stare", dur=0.35, look=(-0.85, 0.75), tilt=0.05)    # eyes go to the outline
S.set(T5 + 2.3, "stand", "dead_stare", dur=0.45, look=(0.0, 0.0), tilt=0.0)        # ...back to us
S.blink(T5 + 3.1)
def outline(cr, tt, p, ly):
    if ly == "back" and tt >= T4: chalk_outline(cr, OUT_DX)
S.prop(outline)

# ================================================================ the ask (deadpan)
T_ASK = T5 + 3.6
S.x = XS
S.camera(T_ASK - 0.3, *CAM5, dur=1.4)
S.the_ask(T_ASK, hold=8.0, push=True)
S.t = T_ASK + 6.9 + 8.0

if __name__ == "__main__":
    S.render("day002.mp4")
