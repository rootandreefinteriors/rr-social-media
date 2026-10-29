"""Day 7 — COMMENT episode: @nerdbpy "Join Hogwarts." (Instagram, day 6 reel, 0 likes; the only comment).
RE-CUT on Justin's outline (2026-10-29). Generic wizard school: no names, crests or characters on screen (only the
pinned card shows the comment). Platform 9 3/4 is a long brick station wall; the door is set into it further along.

SHOT 1  Beside the wrapper pile outside the burger place. Reads the comment. Stares. Slow blink.
OWL     An owl flaps in and drops an envelope on his head (bonk). He catches it, opens it and READS it (we see the
        back). Then turns it to us: YOU'RE IN. / WIZARD SCHOOL. Lets it fall. The owl points off screen right.
WALL    He walks right, the owl hovering over him. A brick wall comes into view, platform signs 9 and 10 on it. The
        owl points at the wall. He backs up. Winds up: legs spin in place, dust. Full sprint at the wall. SMACK. Stuck
        to it for a beat. Peels off, falls on his back. Stars.
DOOR    The owl points again. The camera pulls out: right next to the wall stands a door: DOOR TO WIZARD SCHOOL.
        He looks at it. At us. Gets up, walks over, through the door. CUT: the castle at night, the same door standing
        in the courtyard; he steps out of it.
HAT     A giant old patched hat drops over him to his knees. HMM. It rummages. ... A patch flips open: his eye. HELLO?
        (hello... echoes around inside his head) THERE'S NO BRAIN IN THIS HEAD. Its brows slam down: EXPELLED. FOREVER. It overloads and blasts him into the sky.
OUT     CUT: the empty white room. He falls out of the sky onto his butt, sooty. Looks around. His letter flutters
        down after him; he reads it, turns it to us: EXPELLED stamped across YOU'RE IN. Lets it drop.
END     He stands. The ask, in the white room.
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y
from ink import smooth, draw_text, sketch_line

SX = 2020                       # start + end: body centre 2560, just right of the wrapper pile (where day 6 left him)
X0 = 540 + SX
PILE = (2210, 640, 230)
WALL_L, WALL_R, WALL_H = 3750, 5800, 1150   # the brick platform wall; 9 3/4 near its left end
XW, WALL_W = (WALL_L + WALL_R) / 2, WALL_R - WALL_L
XD = 4660                       # the door, set into the same wall further along (more wall after it)
DOOR_H = 1000
SXA = 2910                      # where he stops in front of the wall (x 3450)
SXB = 2650                      # backs up to here
SXH = 3140                      # flat against the wall
SXL = 3050                      # lying on his back
SXD = XD - 540                  # in the doorway
X3 = 9140                       # the castle (another place entirely: reached through the door)
SX3 = X3 - 540
XDC = X3 - 1080                 # the same door, standing in the courtyard, clear of the castle
CAM0 = (2640, 945, 1.1)
CAM_WALL = (3780, 930, 0.8)
CAM_OUT = (3880, 830, 0.5)
CAM_HAT = (X3, 900, 0.88)

# ---------------------------------------------------------------- timeline
OWL0, DROP, HOV = 4.0, 5.2, 6.2
BONK, CATCH = 5.55, 6.15
OPEN, TURN = 6.9, 9.3           # opens it (reads the side facing him) / turns it round to us
LETGO = 11.8
PT1 = 12.4                      # owl points right
T_WALK, T_ARR = 14.0, 17.3
PT2 = 17.7                      # owl points at the wall
BACK0, BACK1 = 19.4, 20.3       # backs up
WH0, WH1 = 20.6, 21.7           # legs spin in place
HIT = 22.15                     # SMACK
PEEL, SLID, FLOOR = 22.55, 23.0, 23.75
PT3 = 25.2                      # owl points again; camera pulls out
UP0 = 27.6                      # gets up
DW0, DW1 = 28.6, 31.4           # walks to the door
DOOR_OPEN = 30.8
CUT2 = 32.2                     # through the door -> the castle
OUT1 = 34.6
HF0, HLAND = 36.4, 37.15
EYES = 37.8
B1 = (38.2, 39.6, "HMM.")
RUM0, RUM1 = 39.8, 41.4
B2 = (40.0, 41.3, "...")
FLAP0, FLAP1 = 41.5, 42.9
B3 = (43.1, 44.6, "HELLO?")
ECHO = 43.6                     # "hello..." echoes around inside his empty head
B4 = (44.9, 47.2, "THERE'S NO BRAIN IN THIS HEAD.")
B5 = (47.5, 48.9, "EXPELLED.")
B6 = (49.0, 50.4, "FOREVER.")
OV0, BOOM = 49.0, 50.9
UP1 = BOOM + 0.9
CUT3 = 52.2                     # the empty white room
LAND = 52.9
L2_0, L2_1 = 54.0, 55.1         # the letter flutters down after him; he catches it
TURN2 = 56.1                    # reads it, then turns it to us: EXPELLED stamped across it
LETGO2 = 58.3
STAND = 58.8
T_ASK = 59.7

S = M.Scene(x0=SX)
S.auto_blinks = False
S.card("nerdbpy", "Join Hogwarts.", "0", t0=0.35)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0
S.sfx(0.35, "tick", 0.04)

# ================================================================ worlds
LOOSE = [(2600, 0.9, 1), (2660, 0.8, 2), (2370, 1.0, 3), (3050, 0.8, 4), (2950, 0.7, 5)]
def door_open(t):
    a = smooth(ramp(t, DOOR_OPEN, DOOR_OPEN + 0.4))
    if CUT2 <= t < CUT3: a = 1 - smooth(ramp(t, OUT1 + 0.3, OUT1 + 0.7))
    return a
def world(cr, t):
    if CUT2 <= t < CUT3:
        O.draw_castle_world(cr, t, cx=X3)
        O.draw_free_door(cr, XDC, door_open(t), "inside", sign=None, h=DOOR_H)
        return
    if t >= CUT3: return                                                   # the empty white room
    O.draw_burger_world(cr, t)
    sketch_line(cr, [(2500, FLOOR_Y), (6000, FLOOR_Y)], 3.5, sid=91, amp=1.3, alpha=0.8)
    O.draw_wrapper_pile(cr, *PILE)
    for x, sc, k in LOOSE: O.draw_wrapper(cr, x, FLOOR_Y - 14 * sc, sc, sid=7700 + k)
    O.draw_brick_wall(cr, XW, WALL_W, WALL_H, signs=(("9 3/4", (4100 - WALL_L) / WALL_W),))
    O.draw_free_door(cr, XD, door_open(t), "inside", h=DOOR_H)
    O.draw_free_door(cr, XD, door_open(t), "panel", h=DOOR_H, sign_w=560)
S.background(world)

# ================================================================ SHOT 1: reads it. stares.
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(0.6, react="dead_stare", lines=1, face="deadpan")
S.set(2.9, "stand", "dead_stare", dur=0.3, lid=1.0)                         # slow blink
S.set(3.35, "stand", "dead_stare", dur=0.4)

# ================================================================ THE OWL
XA = 540 + SXA
OWLK = [(0.0, (X0 - 1000.0, 330.0), 0), (OWL0, (X0 - 1000.0, 330.0), 0),
        (OWL0, (X0 + 30.0, 420.0), DROP - OWL0, "out"),
        (DROP + 0.15, (X0 - 240.0, 440.0), HOV - DROP - 0.15),                    # hovers to his left
        (T_WALK + 0.2, (XA - 170.0, 420.0), T_ARR - T_WALK + 0.2),                  # follows him over
        (FLOOR + 0.3, (3250.0, 1060.0), 0.9),                                      # over him, looking down
        (UP0 - 0.4, (3320.0, 420.0), 0.7),                                          # up out of his way
        (DW0 + 0.3, (XD - 280.0, 400.0), 1.5),                                      # to the door
        (CUT2 - 0.9, (XD, 900.0), 0.5, "inn"),                                      # in through it
        (CUT2, (XDC, 700.0), 0.0),                                                  # out the other side, after him
        (CUT2 + 0.9, (X3 - 470.0, 880.0), 1.8)]
OWLP = Track(OWLK)
def owl_pos(t):
    x, y = OWLP.at(t)
    return x, y + 14 * math.sin(t * 11)
def owl_point(t):
    for t0, dur, ang in ((PT1, 1.5, 0.0), (PT2, 1.4, 0.25), (PT3, 1.8, -0.1)):
        if t0 <= t < t0 + dur + 0.3: return smooth(ramp(t, t0, t0 + 0.25)) * (1 - smooth(ramp(t, t0 + dur, t0 + dur + 0.3))), ang
    return 0.0, 0.0
def owl_look(t):
    if FLOOR + 0.6 <= t < PT3: return (-0.6, 0.8)                         # at him, on the ground
    pk, ang = owl_point(t)
    if pk > 0.3: return (0.9, 0.3 * ang)
    return (0.0, 0.0)
def owl_blink(t):
    for b in (HOV + 1.5, 15.4, 24.3, 24.5, 34.6, 40.0, 46.0):
        if b <= t < b + (0.4 if b in (24.3,) else 0.15): return 1.0
    return 0.0
def owl(cr, t, p, ly):
    if ly != "front" or t < OWL0 or t >= BOOM + 0.6 and t < CUT3 or t >= CUT3: return
    if CUT2 - 0.45 <= t < CUT2 + 0.9: return                                # it's through the door (comes out after him)
    x, y = owl_pos(t)
    pk, ang = owl_point(t)
    O.draw_owl(cr, x, y, 1.0, 1.0, t, blink=owl_blink(t), point=pk, point_ang=ang, look=owl_look(t))
    if t < DROP: O.draw_envelope(cr, x, y + 110, 0.75, 0.1)                # in its feet
S.sfx(OWL0 + 0.2, "whoosh", 0.04); S.sfx(DROP + 0.3, "whoosh", 0.03)
for t_ in (PT1, PT2, PT3): S.sfx(t_ + 0.05, "tok", 0.03)

# ================================================================ THE LETTER: he reads it, THEN shows us
def env_pos(t):
    ox, oy = OWLP.at(DROP); a = (ox, oy + 14 * math.sin(DROP * 11) + 110)
    head_top = (X0 + 10, 500); hands = (X0, 1000)
    if t < BONK:
        u = ramp(t, DROP, BONK, "inn"); return (lerp(a[0], head_top[0], u), lerp(a[1], head_top[1], u), 0.1 + 0.5 * u)
    if t < CATCH:
        u = (t - BONK) / (CATCH - BONK)
        return (lerp(head_top[0], hands[0] + 20, u) + 60 * math.sin(math.pi * u), lerp(head_top[1], hands[1], u) - 160 * math.sin(math.pi * u),
                0.6 - 2.2 * u)
    return (*hands, 0.0)
def letter_k(t): return smooth(ramp(t, OPEN, OPEN + 0.35))
def letter_flip(t): return smooth(ramp(t, TURN, TURN + 0.45))               # 0 = facing him, 1 = facing us
def letter_c(t):
    if t < LETGO: return (X0, lerp(1000, lerp(930, 880, letter_flip(t)), smooth(ramp(t, OPEN, OPEN + 0.5))))
    u = ramp(t, LETGO, LETGO + 1.0, "linear")
    return (X0 + 170 * u + 60 * math.sin(u * 9), lerp(880, FLOOR_Y - 14, u * u))
def letter_w(t):
    f = letter_flip(t)
    return lerp(120, 400, letter_k(t)) * max(0.06, abs(math.cos(math.pi * f))) if t < LETGO else 400
def letter(cr, t, p, ly):
    if t < DROP or t >= CUT2: return
    if t < OPEN:
        if ly == "front":
            x, y, a = env_pos(t); O.draw_envelope(cr, x, y, 0.75, a)
        return
    cx, cy = letter_c(t)
    if t < LETGO + 1.0:
        if ly != "front": return
        k = letter_k(t); w = letter_w(t); h = lerp(80, 300, k)
        u = ramp(t, LETGO, LETGO + 1.0)
        h *= 1 - 0.9 * u; rot = 0.25 * math.sin(u * 8) * u
        cr.save(); cr.translate(cx, cy); cr.rotate(rot); cr.translate(-cx, -cy)
        O.draw_letter(cr, cx, cy, w, max(20, h), ("YOU'RE IN.",), sub="WIZARD SCHOOL", back=letter_flip(t) < 0.5)
        cr.restore()
        if OPEN <= t < OPEN + 0.35: L.burst_lines(cr, cx, cy, (t - OPEN) / 0.35, r0=150, r1=230, n=10, sid=21)
    elif ly == "back":
        O.draw_letter(cr, cx, cy, 380, 30, ())
S.sfx(BONK, "bonk", 0.06); S.sfx(CATCH, "pat", 0.04); S.sfx(OPEN, "flip", 0.05); S.sfx(TURN, "flip", 0.06)
S.sfx(LETGO + 0.95, "flip", 0.025)
def letter_hands(tt, p):
    e = smooth(ramp(tt, CATCH - 0.2, CATCH)) * (1 - smooth(ramp(tt, LETGO - 0.05, LETGO + 0.3)))
    if e < 0.001: return p
    if tt < OPEN: l, r = (X0 - 55, 1010), (X0 + 55, 1010)
    else:
        cx, cy = letter_c(tt); w = max(110, letter_w(tt))
        l, r = (cx - w / 2 - 6, cy + 40), (cx + w / 2 + 6, cy + 40)
    p["lhand"] = lerp(p["lhand"], l, e); p["rhand"] = lerp(p["rhand"], r, e)
    p["lelb"] = lerp(p["lelb"], (l[0] + 10, l[1] + 110), e); p["relb"] = lerp(p["relb"], (r[0] - 10, r[1] + 110), e)
    if e > 0.5: p["lhand_t"] = p["rhand_t"] = "grip"
    return p
S.hook(letter_hands)
def reading(tt, p):                                                        # eyes scan the lines, top to bottom
    if OPEN + 0.5 <= tt < TURN - 0.3:
        k = (tt - OPEN - 0.5) / 0.6; u = k % 1.0
        p["look"] = (-0.45 + 0.9 * smooth(u), 0.6 + 0.08 * min(3, int(k)))
    return p
S.hook(reading)

S.set(OWL0 + 0.3, "stand", "dead_stare", dur=0.4, look=(-0.8, -0.5))
S.set(OWL0 + 0.7, "stand", "dead_stare", dur=0.6, look=(-0.3, -0.85), tilt=0.04)
S.set(DROP + 0.1, "stand", "dead_stare", dur=0.3, look=(0.2, -0.9), tilt=0.0)
S.set(BONK, "stand", "dead_stare", dur=0.06, ease="snap", lid=0.85, squash=0.25)               # bonk
S.set(BONK + 0.2, "stand", "dead_stare", dur=0.3, ease="back", look=(0.1, 0.3))
S.set(CATCH + 0.1, "stand", "dead_stare", dur=0.3, look=(0.0, 0.85))
S.set(OPEN + 0.3, "stand", "deadpan", dur=0.4, look=(0.0, 0.7), lid=0.45, tilt=0.05)            # reads it
S.set(TURN - 0.3, "stand", "deadpan", dur=0.3, look=(0.0, 0.7), lid=0.45, tilt=0.0)
S.set(TURN + 0.6, "stand", "dead_stare", dur=0.4, look=(0.0, 0.0))                             # shows us. stares.
S.blink(TURN + 1.6)
S.set(LETGO + 0.3, "stand", "dead_stare", dur=0.4, look=(0.3, 0.7))                            # lets it go
S.set(PT1 + 0.35, "stand", "dead_stare", dur=0.3, look=(-0.7, -0.6))                           # the owl...
S.set(PT1 + 0.7, "stand", "dead_stare", dur=0.5, look=(-0.7, -0.6), tilt=0.04)
S.set(PT1 + 1.2, "stand", "dead_stare", dur=0.35, look=(0.9, 0.0), tilt=-0.03)                 # ...where it points

# ================================================================ WALK right. the wall.
S.xkeys.append((T_WALK, SXA, T_ARR - T_WALK, "smooth")); S.x = SXA
S.camera(T_WALK, *CAM_WALL, dur=T_ARR - T_WALK + 0.4)
S.set(T_ARR, "stand", "dead_stare", dur=0.3, look=(0.4, 0.0))
S.set(PT2 + 0.3, "stand", "dead_stare", dur=0.3, look=(-0.6, -0.7))                            # owl
S.set(PT2 + 0.8, "stand", "dead_stare", dur=0.4, look=(0.9, -0.2))                             # the wall
S.blink(PT2 + 1.4)
S.set(PT2 + 1.6, "stand", "dead_stare", dur=0.4, look=(0.0, 0.0))                              # us
# backs up... winds up... GO
S.xkeys.append((BACK0, SXB, BACK1 - BACK0, "smooth")); S.x = SXB
S.set(BACK0, "stand", "dead_stare", dur=0.3, look=(0.9, 0.0))
S.set(WH0 - 0.3, "crouch", "dead_stare", dur=0.3, look=(1.0, 0.0), lid=0.45, lean=0.12)
S.set(WH0, "stand", "dead_stare", dur=0.15, look=(1.0, 0.0), lid=0.5, lean=0.28, nowalk=1.0,
      lelb=(450, 900), lhand=(410, 840), relb=(640, 900), rhand=(690, 830), lhand_t="fist", rhand_t="fist")
S.sfx(WH0, "skid", 0.05, dur=WH1 - WH0)
def wheel(tt, p):                                                          # legs spin in place, a blur
    if not (WH0 <= tt < WH1): return p
    hx, hy = p["hip"]
    for side, off in (("l", 0.0), ("r", math.pi)):
        a = tt * 42 + off
        foot = (hx + 85 * math.cos(a), FLOOR_Y - 70 - 70 * math.sin(a))
        p[side + "foot"] = foot; p[side + "knee"] = ((hx + foot[0]) / 2 + 30, (hy + foot[1]) / 2 - 20)
    return p
S.hook(wheel)
def wheel_fx(cr, t, p, ly):
    if ly != "front" or not (WH0 <= t < WH1 + 0.45): return
    hx = p["hip"][0]
    cr.save(); cr.translate(hx, FLOOR_Y - 70); cr.scale(110, 90); cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore()
    L.stroke_ink(cr, 3, alpha=0.4)
    for k in range(3):
        u = ((t - WH0) * 2.6 + k / 3) % 1.0
        L.draw_dust(cr, hx - 90 - 60 * u, FLOOR_Y, u, side=-1, sid=60 + k * 7)
    if t >= WH1:                                                           # speed lines behind him
        for k in range(4):
            yk = 760 + k * 150
            sketch_line(cr, [(hx - 160 - 260 * (t - WH1) / 0.45, yk), (hx - 120, yk)], 5, sid=70 + k, amp=0.4)
S.set(WH1, "stand", "dead_stare", dur=0.08, ease="snap", run=1.0, lean=0.3, nowalk=0.0, look=(1.0, 0.0))
S.xkeys.append((WH1, SXH, HIT - WH1, "inn")); S.x = SXH
S.sfx(WH1, "whoosh", 0.06)
# SMACK
S.set(HIT, "stand", "dead_stare", dur=0.05, ease="snap", run=0.0, lean=-0.06, stretch=0.18, squash=-0.4,
      eyescale=1.2, lid=0.0, look=(0.0, 0.0), nowalk=1.0, tilt=-0.08,
      lelb=(580, 870), lhand=(620, 760), relb=(625, 960), rhand=(620, 1060), lhand_t="flat", rhand_t="flat")
S.sfx(HIT, "bonk", 0.14); S.sfx(HIT, "thud", 0.2); S.shake(HIT, 0.4, 16)
def smack(cr, t, p, ly):
    if ly == "front" and HIT <= t < HIT + 0.45:
        L.draw_impact(cr, WALL_L, 760, (t - HIT) / 0.45, r=120, sid=81)
# slides down the wall onto his butt... then tips over onto his back. KO.
L.POSES["ko"] = dict(head=(-95, 1392), neck=(30, 1428), hip=(380, 1440), lknee=(470, 1292), rknee=(500, 1300),
                     lfoot=(520, FLOOR_Y), rfoot=(570, FLOOR_Y), lelb=(-10, 1300), lhand=(-70, 1165), relb=(220, 1452),
                     rhand=(385, 1462), tilt=-1.35, lfoot_dir=0.6, rfoot_dir=0.8, lhand_t="open", rhand_t="open",
                     lhand_front=0.0, rhand_front=0.0)
S.set(PEEL, "sit_floor", "dizzy", dur=SLID - PEEL, ease="inn", nowalk=1.0, look=(0.0, 0.0), tilt=0.12)
S.set(SLID, "sit_floor", "dizzy", dur=0.06, ease="snap", nowalk=1.0, stretch=-0.25, tilt=0.12)
S.sfx(SLID, "thud", 0.1)
S.set(SLID + 0.35, "ko", "dizzy", dur=FLOOR - SLID - 0.35, ease="inn", nowalk=1.0)
S.sfx(FLOOR, "thud", 0.15); S.shake(FLOOR, 0.3, 8)
S.camera(HIT + 0.2, 3560, 960, 0.8, 1.2)
S.set(FLOOR + 0.05, "ko", "dizzy", dur=0.2, nowalk=1.0)
S.sfx(FLOOR + 0.3, "twinkle", 0.04)
# the owl points again, the camera pulls out: a door, in the same wall
S.set(PT3 - 0.2, "ko", "dead_stare", dur=0.4, nowalk=1.0, look=(0.6, -0.6))             # stars gone. the owl.
S.camera(PT3 + 0.3, *CAM_OUT, dur=1.4)
S.set(PT3 + 1.0, "ko", "dead_stare", dur=0.4, nowalk=1.0, look=(1.0, -0.2))             # the door
S.set(PT3 + 1.9, "ko", "dead_stare", dur=0.4, nowalk=1.0, look=(0.6, 0.6))               # at us
S.blink(PT3 + 2.4)
S.cut(UP0)                                                                  # jump cut: up. no in-between.
S.set(UP0, "stand", "dead_stare", dur=0.0, nowalk=0.0, look=(0.8, 0.0), lhand_front=0.0, rhand_front=0.0)
S.xkeys.append((DW0, SXD, DW1 - DW0, "smooth")); S.x = SXD
S.camera(DW0, XD - 300, 900, 0.8, DW1 - DW0)
S.set(DW1, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0))
S.sfx(DOOR_OPEN, "squeak", 0.03)
S.set(CUT2 - 0.5, "stand", "dead_stare", dur=0.3, look=(0.0, -0.3))

# ================================================================ CUT: through the door, the castle
S.cut(CUT2, cam=(X3 - 620, 930, 0.72), x=XDC - 540)
S.camera(CUT2 + 0.6, X3 - 120, 930, 0.88, OUT1 - CUT2 - 0.4)
S.set(CUT2, "stand", "dead_stare", dur=0.0, look=(0.6, 0.0))
S.xkeys.append((CUT2 + 0.3, SX3, OUT1 - CUT2 - 0.3, "smooth")); S.x = SX3
S.sfx(OUT1 + 0.7, "tok", 0.05)
def court_door(cr, t, p, ly):                                              # its panel, in front of the courtyard
    if ly == "back" and CUT2 <= t < CUT3: O.draw_free_door(cr, XDC, door_open(t), "panel", sign=None, h=DOOR_H)
S.set(OUT1, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0))
S.set(OUT1 + 0.5, "stand", "dead_stare", dur=0.5, look=(0.0, -0.9))                           # the castle
S.set(OUT1 + 0.9, "stand", "dead_stare", dur=0.6, look=(0.0, -0.9), tilt=-0.05)
S.set(OUT1 + 1.6, "stand", "dead_stare", dur=0.4, look=(0.0, 0.0), tilt=0.0)

# ================================================================ THE HAT
HW, HH = 820.0, 1050.0
BRIM_Y = 1290.0
S.camera(HF0 - 0.6, *CAM_HAT, dur=1.0)
S.set(HF0 + 0.15, "stand", "dead_stare", dur=0.25, look=(0.0, -1.0))
S.sfx(HF0 - 0.1, "slide_down", 0.04, dur=0.8); S.sfx(HLAND, "thud", 0.15); S.shake(HLAND, 0.35, 9)
S.sfx(RUM0, "rummage", 0.05, dur=1.7)
S.sfx(FLAP0, "pop", 0.03); S.sfx(FLAP1 - 0.2, "tok", 0.03)
S.sfx(B5[0], "bonk", 0.03); S.sfx(B6[0], "bonk", 0.04)
S.sfx(OV0, "whine", 0.035, dur=BOOM - OV0)
for k, tk in enumerate((49.6, 50.1, 50.45, 50.7)): S.sfx(tk, "pop", 0.015 + 0.004 * k)
def ov(t): return ramp(t, OV0, BOOM, "inn")
def hat_state(t):
    st = dict(bx=X3, by=BRIM_Y, swell=1.0, bend=0.25, droop=0.55, eyes=0.0, look=(0.0, 0.0), mouth=0.0, glow=0.0, angry=0.0)
    if t < HLAND:
        u = ramp(t, HF0, HLAND, "inn"); st["by"] = lerp(-900, BRIM_Y, u); st["droop"] = 0.55 - 0.35 * u
        return st
    s_ = math.exp(-(t - HLAND) * 5) * math.sin((t - HLAND) * 26)
    st["swell"] = 1.0 + 0.08 * s_; st["bend"] = 0.25 + 0.15 * s_
    st["eyes"] = smooth(ramp(t, EYES, EYES + 0.3))
    if t < B1[1]: st["look"] = (-0.5, -0.6) if t > B1[0] - 0.2 else (0.0, 0.0)
    if RUM0 <= t < RUM1:
        r = math.sin(math.pi * (t - RUM0) / (RUM1 - RUM0))
        st["bend"] += 0.25 * r * math.sin(t * 9); st["swell"] += 0.05 * r * math.sin(t * 13)
        st["look"] = (0.7 * math.sin(t * 5), 0.6)
    if FLAP0 <= t < FLAP1: st["look"] = (0.6, 0.4)
    if B3[0] - 0.2 <= t < B3[1]: st["look"] = (0.0, 0.9)
    if B4[0] - 0.2 <= t: st["look"] = (0.0, 0.0); st["eyes"] = 1.0 + 0.3 * ramp(t, B4[0], B4[0] + 0.3)
    if t >= B5[0] - 0.15:                                                  # brows SLAM down
        st["angry"] = smooth(ramp(t, B5[0] - 0.15, B5[0])); st["eyes"] = 0.7
        st["swell"] += 0.06 * pulse(t, B5[0], 0.08) + 0.06 * pulse(t, B6[0], 0.08)
    for b in (B1, B3, B4, B5, B6):
        if b[0] <= t < b[1] - 0.3:
            st["mouth"] = 0.25 + 0.25 * abs(math.sin((t - b[0]) * 9))
    o = ov(t)
    if o > 0:
        st["bx"] += (6 + 24 * o) * math.sin(t * (30 + 40 * o)); st["swell"] += 0.25 * o
        st["glow"] = o; st["mouth"] = max(st["mouth"], 0.6 * o)
        st["bend"] += 0.1 * math.sin(t * 23) * o
    return st
def hat(cr, t, p, ly):
    if ly != "front" or not (HF0 <= t < BOOM): return
    st = hat_state(t)
    O.draw_wizard_hat(cr, st["bx"], st["by"], HW, HH, t, bend=st["bend"], droop=st["droop"], swell=st["swell"],
                      eyes=st["eyes"], look=st["look"], mouth=st["mouth"], glow=st["glow"], angry=st["angry"])
    ex, ey = X3 + 42, 636                                                  # the flap over his eye
    k = smooth(ramp(t, FLAP0, FLAP0 + 0.2)) * (1 - smooth(ramp(t, FLAP1 - 0.25, FLAP1)))
    if t >= HLAND:
        if k > 0.02:
            cr.arc(ex, ey, 62, 0, 2 * math.pi); cr.set_source_rgb(0.08, 0.06, 0.05); cr.fill()
            if k > 0.6:
                bl = 1.0 if FLAP0 + 0.95 <= t < FLAP0 + 1.12 else 0.0
                L.sketch_circle(cr, ex, ey, 44, 6, sid=7950, fill=(1, 1, 1))
                if bl < 0.5:
                    cr.arc(ex, ey + 6, 19, 0, 2 * math.pi); L.fill_ink(cr)
                    cr.arc(ex - 6, ey, 6, 0, 2 * math.pi); cr.set_source_rgb(1, 1, 1); cr.fill()
                    L.sketch_line(cr, [(ex - 44, ey - 16), (ex + 44, ey - 16)], 7, sid=7951, amp=0.2)
                else:
                    L.sketch_line(cr, [(ex - 44, ey), (ex + 44, ey)], 7, sid=7952, amp=0.2)
        h = 136 * (1 - 2 * k)
        y0 = ey - 68
        L.sketch_poly(cr, [(ex - 68, y0), (ex + 68, y0), (ex + 68, y0 + h), (ex - 68, y0 + h)], 4, sid=7953, fill=O.HAT_P, amp=0.6)
        for j in range(5):
            xj = ex - 68 + 136 * (j + 0.5) / 5
            L.sketch_line(cr, [(xj, y0 - 7), (xj, y0 + 7)], 3, sid=7960 + j, amp=0.2, color=lerp(L.INK, O.GOLD, ov(t)))
    if HLAND <= t < HLAND + 0.4:
        L.draw_poof(cr, X3 - 380, FLOOR_Y - 40, (t - HLAND) / 0.6, r=150, sid=41)
        L.draw_poof(cr, X3 + 380, FLOOR_Y - 40, (t - HLAND) / 0.6, r=150, sid=42)
    o = ov(t)
    if o > 0.15:
        tx, ty = O.hat_pt(st["bx"], st["by"], HW, HH, 0.99, 0, st["bend"], st["droop"], st["swell"])
        for i in range(8):
            u = ((t - OV0) * (1.2 + 2.0 * o) + i / 8) % 1.0
            a = i * 2.4
            O.draw_star(cr, tx + math.cos(a) * 160 * u, ty + math.sin(a) * 120 * u - 60 * u, 10 + 14 * o * (1 - u),
                        (O.GOLD, O.VIOLET, O.CYAN)[i % 3], ang=t * 3 + i, alpha=(1 - u) * min(1.0, o * 2))
def bubbles(cr, t, p, ly):
    if ly != "front": return
    for k in range(3):                                                     # hello... hello... bouncing around in there
        u = (t - ECHO - 0.45 * k) / 1.3
        if 0 <= u < 1:
            draw_text(cr, "hello...", X3 + 20 + 90 * math.sin(u * 5 + k * 2), 600 - 40 * k + 50 * u, 62 - 10 * k,
                      color=(255, 240, 200), alpha=math.sin(math.pi * u) * (1 - 0.2 * k))
    for b in (B1, B2, B3, B4, B5, B6):
        if b[0] <= t < b[1]:
            a = min(1.0, (t - b[0]) / 0.15, (b[1] - t) / 0.15)
            sz = 72 if b in (B5, B6) else 56
            O.draw_thought(cr, X3 - 205, 410, b[2], tail=(X3 - 140, 560), size=sz, max_w=360, alpha=a)
S.set(HLAND, "stand", "dead_stare", dur=0.08, ease="snap", squash=0.15)
S.set(HLAND + 0.2, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), squash=0.0)
def shuffle(tt, p):
    if B2[0] <= tt < B2[1]:
        v = 22 * max(0.0, math.sin((tt - B2[0]) * 7))
        p["rfoot"] = (p["rfoot"][0], p["rfoot"][1] - v)
    return p
S.hook(shuffle)

# ================================================================ BOOM: expelled, into the sky
S.flash(BOOM, 0.45)
S.sfx(BOOM, "kaboom", 0.45, dur=2.6); S.sfx(BOOM + 0.6, "twinkle", 0.05); S.shake(BOOM, 0.9, 26)
S.set(BOOM, "cannonball", "dead_stare", dur=0.1, ease="snap", eyescale=1.25, lid=0.0, lag=0.5)
S.set(CUT3 - 0.3, "sit_floor", "dead_stare", dur=0.2, lag=0.5, nowalk=1.0)
def flight_y(t):
    if BOOM <= t < CUT3: return -2600 * ramp(t, BOOM + 0.08, UP1, "inn")
    if CUT3 <= t < LAND: u = (t - CUT3) / (LAND - CUT3); return -1750 * (1 - u * u)
    return 0.0
def flight_x(t):
    if BOOM <= t < CUT3: return -420 * ramp(t, BOOM + 0.08, UP1, "smooth")
    if CUT3 <= t < LAND: u = (t - CUT3) / (LAND - CUT3); return -740 * (1 - u * u)
    return 0.0
def flight(tt, p):
    y = flight_y(tt)
    if y < -0.5:
        x = flight_x(tt)
        for j in L.JOINTS: p[j] = (p[j][0] + x, p[j][1] + y)
    return p
S.hook(flight)
def boom(cr, t, p, ly):
    if ly != "front" or not (BOOM <= t < CUT3): return
    O.draw_magic_burst(cr, X3, 900, t - BOOM, part="stars")
    rnd = random.Random(3)
    for i in range(10):
        a = rnd.uniform(-math.pi, 0); sp = rnd.uniform(500, 1100); u = t - BOOM
        x = X3 + math.cos(a) * sp * u; y = 800 + math.sin(a) * sp * u + 700 * u * u
        cr.save(); cr.translate(x, y); cr.rotate(u * rnd.uniform(-8, 8))
        L.sketch_poly(cr, [(-30, -16), (26, -22), (34, 14), (-22, 20)], 4, sid=7970 + i, fill=O.HAT_D, amp=0.6)
        cr.restore()
def boom_back(cr, t, p, ly):
    if ly != "back" or not (BOOM <= t < CUT3): return
    O.draw_brim_ring(cr, X3, t, w=400)
    O.draw_magic_burst(cr, X3, 900, t - BOOM, part="cloud")

# ================================================================ CUT: the empty white room. lands. the letter, again.
S.cut(CUT3, cam=(540, 900, 0.95), x=0)
S.set(LAND, "sit_floor", "dead_stare", dur=0.06, ease="snap", stretch=-0.3, lag=1.0)
S.set(LAND + 0.15, "sit_floor", "dead_stare", dur=0.4, ease="back", stretch=0.0, fx_steam=0.4)
S.sfx(LAND, "thud", 0.2); S.sfx(LAND + 0.02, "bonk", 0.04); S.shake(LAND, 0.5, 16)
def land_fx(cr, t, p, ly):
    if ly == "front" and LAND <= t < LAND + 0.8: L.draw_poof(cr, 540, FLOOR_Y - 40, (t - LAND) / 0.8, r=200, sid=32)
S.blink(LAND + 1.0)
S.set(LAND + 0.8, "sit_floor", "dead_stare", dur=0.3, look=(0.0, 0.0), fx_steam=0.3)          # where is this
S.set(LAND + 1.3, "sit_floor", "dead_stare", dur=0.4, look=(-0.8, 0.0), fx_steam=0.2)
S.set(LAND + 1.9, "sit_floor", "dead_stare", dur=0.4, look=(0.8, 0.0), fx_steam=0.1)
S.set(L2_0 + 0.2, "sit_floor", "dead_stare", dur=0.4, look=(0.0, -0.9))                        # something's coming down
# the letter flutters down after him, into his hands; he reads it; turns it round: EXPELLED stamped across it
L2_HOLD = (540, 1262)
def l2_flip(t): return smooth(ramp(t, TURN2, TURN2 + 0.45))
def l2_c(t):
    if t < L2_1:
        u = ramp(t, L2_0, L2_1, "linear")
        return (540 + 160 * math.sin(u * 7) * (1 - u), lerp(-250, L2_HOLD[1], u ** 1.4), 0.4 * math.sin(u * 7) * (1 - u))
    if t < LETGO2: return (L2_HOLD[0], L2_HOLD[1] - 20 * smooth(ramp(t, TURN2, TURN2 + 0.4)), 0.0)
    u = ramp(t, LETGO2, LETGO2 + 0.8, "linear")
    return (540 + 150 * u + 50 * math.sin(u * 9), lerp(L2_HOLD[1], FLOOR_Y - 14, u * u), 0.3 * math.sin(u * 8) * u)
def l2_w(t):
    if L2_1 <= t < LETGO2: return 400 * max(0.06, abs(math.cos(math.pi * l2_flip(t))))
    return 400
def letter2(cr, t, p, ly):
    if t < L2_0: return
    cx, cy, rot = l2_c(t)
    if t >= LETGO2 + 0.8:
        if ly == "back": O.draw_letter(cr, cx, cy, 380, 30, ())
        return
    if ly != "front": return
    u = ramp(t, LETGO2, LETGO2 + 0.8)
    h = 300 * (1 - 0.9 * u)
    cr.save(); cr.translate(cx, cy); cr.rotate(rot); cr.translate(-cx, -cy)
    O.draw_letter(cr, cx, cy, l2_w(t), max(20, h), ("YOU'RE IN.",), sub="WIZARD SCHOOL",
                  back=(t < LETGO2 and l2_flip(t) < 0.5), stamp="EXPELLED")
    cr.restore()
S.sfx(L2_1, "pat", 0.04); S.sfx(TURN2, "flip", 0.06); S.sfx(LETGO2 + 0.75, "flip", 0.025)
def l2_hands(tt, p):
    e = smooth(ramp(tt, L2_1 - 0.2, L2_1)) * (1 - smooth(ramp(tt, LETGO2 - 0.05, LETGO2 + 0.3)))
    if e < 0.001: return p
    cx, cy, _ = l2_c(tt); w = max(110, l2_w(tt))
    l, r = (cx - w / 2 - 6, cy + 40), (cx + w / 2 + 6, cy + 40)
    p["lhand"] = lerp(p["lhand"], l, e); p["rhand"] = lerp(p["rhand"], r, e)
    p["lelb"] = lerp(p["lelb"], (l[0] + 20, l[1] + 70), e); p["relb"] = lerp(p["relb"], (r[0] - 20, r[1] + 70), e)
    if e > 0.5: p["lhand_t"] = p["rhand_t"] = "grip"
    return p
S.hook(l2_hands)
def reading2(tt, p):
    if L2_1 + 0.25 <= tt < TURN2 - 0.2:
        k = (tt - L2_1 - 0.25) / 0.45; u = k % 1.0
        p["look"] = (-0.45 + 0.9 * smooth(u), 0.65)
    return p
S.hook(reading2)
S.set(L2_1, "sit_floor", "deadpan", dur=0.3, look=(0.0, 0.7), lid=0.45, tilt=0.05)
S.set(TURN2 + 0.5, "sit_floor", "dead_stare", dur=0.4, look=(0.0, 0.0), tilt=0.0)               # at us
S.blink(TURN2 + 1.3)
S.set(LETGO2 + 0.2, "sit_floor", "dead_stare", dur=0.4, look=(0.3, 0.7))

# ================================================================ stands. the ask, in the empty white room.
S.stand(STAND, face="dead_stare")
S.t = T_ASK
S.camera(T_ASK - 1.0, 540, 930, 1.12, 1.0)
S.the_ask(T_ASK, hold=6.0, keep=dict(soot=0.65, frizz=0.5))
S.hook(lambda tt, p: (p.update(soot=0.65, frizz=max(p.get("frizz", 0.0), 0.5)) if tt >= BOOM else None) or p)

# ---------------------------------------------------------------- draw order + hooks
S.props.insert(0, boom_back); S.props.insert(1, court_door)
for f in (letter, owl, wheel_fx, smack, hat, boom, land_fx, letter2, bubbles): S.prop(f)

if __name__ == "__main__":
    S.render("day007.mp4")
