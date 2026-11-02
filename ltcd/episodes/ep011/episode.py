"""Day 11 (RE-CUT on Justin's notes, 2026-11-02) - COMMENT episode: @angela.tgz "Build a cat shelter and be happy about it"
(Instagram, day 10 reel, 2 likes). Warm, cute, animal-friendly: a real CAT RESCUE SHELTER for stray cats. Mordor is over:
he walks out of it to the right into a new sunny town. Ends with a donation message for a real cat sanctuary.

LEAVE     Mordor ruins. He reads the comment. A tiny mew from the right. He runs right, out of Mordor, into a sunny town.
KITTEN    A cardboard box: FREE KITTEN. A black kitten pops up. He crouches; it sniffs his mitten; slow blink (cat for
          "I love you"); he slow-blinks back; picks it up. Tries to smile (stiff). It purrs. The smile goes soft.
STRAYS    Mews everywhere: a cat up a tree, kittens peeking out of a box pile. The kitten climbs onto his head (if it
          fits, it sits) and stays there.
BUILD     Hammer from his hip. Build cloud -> a cosy CAT RESCUE SHELTER.
RESCUE    He catches the tree cat in his arms and brings it in; a line of kittens follows him in like ducklings.
INSIDE    One can goes pssht - every head turns. Fancy bed: every cat squeezes into the box it came in instead.
          A cat slowly pushes his mug off the shelf, staring at him; he catches it.
ADOPTION  ADOPTION DAY: the mom (day 6) adopts the orange cat. He stamps ADOPTED on photo after photo. The last photo is
          the kitten's. He stamps it himself. Hug, real smile, purr.
ASK       In front of the shelter, kitten on his head: TO HELP SAVE REAL CATS, PLEASE DONATE TO THE CAT HOUSE ON THE
          KINGS AT CATHOUSEONTHEKINGS.COM - then he flips the page: TELL ME WHAT TO DO NEXT IN THE COMMENTS.
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import ramp, pulse, lerp, FLOOR_Y, Track
from ink import smooth, back_out
import numpy as np

FR = 1 / 30
NOW = [0.0]
# ---------------------------------------------------------------- places
SX0 = 31160.0; X0 = 540 + SX0                 # Mordor: where day 10 left him (x 31700)
TX, TH = 32600.0, 1330.0                      # the ruined eye tower
EAGLE_X = 31180.0
EYEB = (32220.0, FLOOR_Y - 150)
BORDER = 33400.0                              # Mordor ends, the town begins
XA = 34480.0; SXA = XA - 540                  # where he stops in town
KBOX = 34800.0                                # the FREE KITTEN box
PILE_X = 33950.0                              # the box pile with three kittens
SH = 35700.0                                  # the CAT RESCUE SHELTER (35200 - 36200), door at SH
TREE = 36950.0; TREE_H = 1900
BR = O.tree_branch_tip(TREE, FLOOR_Y, TREE_H)  # (37220, 563)
XB = 34960.0; SXB = XB - 540                  # after the build, left of the shelter (and for the ask)
# inside
IX = 60540.0; SXI = IX - 540
SHELF_X = 60150.0; SHELF_Y = (1100.0, 850.0)
BOWLS = [60820 + 130 * i for i in range(6)]
FBOX = 61950.0                                # the box the fancy bed came in
BED_X = 61600.0
BOARD = (61250.0, 1000.0)
PHOTOS = [(60990 + 175 * (i % 4), 910 + 205 * (i // 4)) for i in range(8)]
PHOTO_COLS = ["orange", "grey", "white", "cream", "brown", "grey", "white", "black"]   # the last one is the kitten
KS = 0.62

# ---------------------------------------------------------------- timeline
T_READ = 0.35
T_MEW = 2.05
T_RUN, T_RUN1 = 2.6, 4.4
T_POPUP = 5.0
T_CROUCH = 5.6
T_SNIFF = 6.3
T_KBLINK, T_HBLINK = 7.0, 7.6
T_PICK = 8.4
T_SMILE0, T_SMILE1 = 9.0, 10.1
T_LOOK = 11.0
T_HEAD = 13.3
T_PULL = 13.9
T_CLOUD0, T_CLOUD1 = 16.9, 19.7
CUT_TREE = 21.2
T_REACH = 21.8
T_CJUMP = 22.5
CUT_DOOR = 24.0
CUT_DUCK = 25.6
T_DWALK0, T_DWALK1 = 25.8, 28.4
T_DCLOSE = 29.3
CUT_IN = 30.0
T_CAN = 30.8
T_FEED0, T_FEED1 = 31.3, 33.4
T_BED = 33.7
T_BOX0 = 34.8
CUT_MUG = 37.4
MUG_N = [37.9, 38.4, 39.0]
T_CATCH = 39.35
CUT_ADOPT = 40.4
CUT_MOM = 41.6
T_MCAT = 42.8
T_MOUT = 43.9
CUT_STAMP = 44.8
STAMP_T = [45.0, 45.6, 46.1, 46.5, 46.85, 47.15, 47.4]
T_LAST = 48.9
CUT_HUG = 49.3
CUT_ASK = 51.6
T_ASK = 51.9
ASK_HOLD = 6.6
T_PAGE = T_ASK + 6.9 + ASK_HOLD
END = T_PAGE + 2.9

S = M.Scene(x0=SX0)
S.auto_blinks = False
S.card("angela.tgz", "Build a cat shelter and be happy about it", "2", t0=0.3)
CAM0 = (X0 + 230, 1010, 1.0)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0

# ================================================================ worlds
def ruins(cr, t):
    x, yb = TX, FLOOR_Y; tw = 150
    top = yb - TH * 0.5
    pts = [(x - tw * 1.9, yb), (x - tw * 1.3, top + 90), (x - tw * 0.9, top - 40), (x - tw * 0.4, top + 60), (x, top - 90),
           (x + tw * 0.5, top + 40), (x + tw * 1.0, top - 20), (x + tw * 1.35, top + 110), (x + tw * 1.9, yb)]
    L.sketch_poly(cr, pts, 7, sid=7800, fill=(0.12, 0.10, 0.11), amp=0.4)
    for k in range(4):
        a = (t * 0.25 + k / 4) % 1.0
        O.draw_smoke_puff(cr, x - 60 + 40 * k - 200 * a, top - 120 - 900 * a, 80 + 260 * a, alpha=(1 - a) * 0.85, dark=0.8)
    O.draw_flames(cr, [(x + 60, top + 10 - 30 * i) for i in range(6)], t, w=60)

def eyeball(cr, x, y):
    L.sketch_circle(cr, x, y, 150, 6, sid=7840, fill=(0.62, 0.48, 0.30))
    cr.save(); cr.translate(x, y)
    cr.save(); cr.scale(0.22, 1.0); cr.arc(0, 0, 110, 0, 2 * math.pi); cr.restore(); cr.set_source_rgb(0.2, 0.15, 0.12); cr.fill()
    cr.restore()

def window_cats(t):
    n = 0
    if t >= CUT_DOOR + 1.0: n = 1
    if t >= T_DCLOSE: n = 4
    return n

def door_open(t):
    a = smooth(ramp(t, CUT_DOOR + 0.2, CUT_DOOR + 0.5)) * (1 - smooth(ramp(t, CUT_DOOR + 1.2, CUT_DOOR + 1.5)))
    b = smooth(ramp(t, 27.4, 27.7)) * (1 - smooth(ramp(t, T_DCLOSE - 0.3, T_DCLOSE)))
    c = smooth(ramp(t, CUT_ADOPT + 0.7, CUT_ADOPT + 1.0)) * (1 - smooth(ramp(t, CUT_MOM - 0.05, CUT_MOM)))
    return max(a, b, c)

def world(cr, t):
    NOW[0] = t
    if CUT_IN - FR <= t < CUT_ADOPT - FR or CUT_MOM - FR <= t < CUT_ASK - FR:
        inside(cr, t); return
    if t < T_RUN1 + 1.0:
        O.draw_dark_land_world(cr, t, x0=24900, x1=BORDER, volcano=None, gate=None, tower=None)
        ruins(cr, t)
        eyeball(cr, *EYEB)
        O.draw_eagle(cr, EAGLE_X, FLOOR_Y, t, flap=0.06, s=0.8, look=0.8 if t < T_RUN + 0.5 else 0.9, face=1)
    O.draw_town_world(cr, t, x0=BORDER if t < T_RUN1 + 1.0 else 20000, x1=40000)
    O.draw_tree(cr, TREE, FLOOR_Y, t, h=TREE_H)
    if t >= T_CLOUD1 - 0.05:
        sc = back_out(min(1.0, (t - T_CLOUD1 + 0.05) / 0.35), 1.6)
        cr.save(); cr.translate(SH, FLOOR_Y); cr.scale(max(0.05, sc), max(0.05, sc)); cr.translate(-SH, -FLOOR_Y)
        O.draw_rescue_shelter(cr, SH, FLOOR_Y, t, door=door_open(t), window_cats=window_cats(t),
                              banner="ADOPTION DAY" if t >= CUT_ADOPT - FR else None)
        cr.restore()
    O.draw_box(cr, KBOX, FLOOR_Y + 20, s=1.0, label="FREE KITTEN", sid=10300)
    if t < T_DWALK0 + 1.4:                                           # the box pile the three kittens live in
        O.draw_box(cr, PILE_X - 120, FLOOR_Y + 10, s=0.85, sid=10330)
        O.draw_box(cr, PILE_X + 110, FLOOR_Y + 30, s=0.9, sid=10340)
S.background(world)

def inside(cr, t):
    O.draw_shelter_inside(cr, t, 59000, 63500)
    for k, y in enumerate(SHELF_Y):                                   # cat condo shelves
        L.sketch_rect(cr, SHELF_X - 230, y, SHELF_X + 230, y + 34, 5, sid=10700 + k, fill=(0.78, 0.58, 0.40))
    L.sketch_rect(cr, SHELF_X - 20, SHELF_Y[1] + 34, SHELF_X + 20, FLOOR_Y, 5, sid=10703, fill=(0.88, 0.76, 0.56))
    wx, wy = 62300, 520                                               # sunny window
    L.sketch_rect(cr, wx - 220, wy - 200, wx + 220, wy + 200, 6, sid=10704, fill=(0.82, 0.93, 1.0))
    L.sketch_circle(cr, wx + 110, wy - 90, 50, 5, sid=10705, fill=(1.0, 0.86, 0.35))
    L.sketch_line(cr, [(wx, wy - 200), (wx, wy + 200)], 5, sid=10706); L.sketch_line(cr, [(wx - 220, wy), (wx + 220, wy)], 5, sid=10707)
    bx, by = BOARD                                                    # the ADOPT ME board
    L.sketch_rect(cr, bx - 380, by - 260, bx + 380, by + 260, 7, sid=10710, fill=(0.80, 0.64, 0.44))
    L.draw_text(cr, "ADOPT ME", bx, by - 205, 56, color=(170, 50, 40))
    for i, (px, py) in enumerate(PHOTOS):
        O.draw_cat_photo(cr, px, py, PHOTO_COLS[i], stamp=stamp_k(t, i), s=0.95, sid=10720 + 12 * i)
    dx = 62950                                                        # the door (right)
    L.sketch_rect(cr, dx - 130, FLOOR_Y - 360, dx + 130, FLOOR_Y, 6, sid=10790, fill=O.SHELTER_DOOR)
    for i, bxx in enumerate(BOWLS):                                   # food bowls
        L.sketch_ellipse(cr, bxx, FLOOR_Y + 40, 52, 20, 5, sid=10800 + i, fill=(0.92, 0.45, 0.45))
    O.draw_box(cr, FBOX, FLOOR_Y + 30, s=1.2, label="FANCY BED", flaps=1.0, sid=10820)
    if t >= T_BED:
        s_ = back_out(min(1.0, (t - T_BED) / 0.3), 1.7)
        O.draw_cat_bed(cr, BED_X, FLOOR_Y + 40, s=max(0.05, s_) * 1.1)
    if t < CUT_MUG + 1.5 or t >= CUT_ADOPT:
        pass

STAMP_ALL = STAMP_T + [T_LAST]
def stamp_k(t, i):
    if t < CUT_STAMP - 1: return 0.0
    return min(1.0, max(0.0, (t - STAMP_ALL[i]) / 0.12)) if t >= STAMP_ALL[i] else 0.0

# ================================================================ HIM: Mordor -> town
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(T_READ, react="deadpan", lines=2, dur=1.6, face="deadpan")
S.set(T_MEW + 0.25, "stand", "deadpan", dur=0.25, look=(0.9, 0.1))                  # a mew, off to the right
S.set(T_MEW + 0.45, "stand", "deadpan", dur=0.3, look=(0.9, 0.1), turn=0.5, brow=0.3)
S.set(T_RUN - 0.12, "stand", "deadpan", dur=0.1, look=(0.9, 0.0), turn=0.5, stretch=-0.15)
S.set(T_RUN, "stand", "deadpan", dur=0.15, run=1.0, look=(0.9, 0.0), turn=0.5, lean=0.12)
S.xkeys.append((T_RUN, SXA, T_RUN1 - T_RUN, "smooth")); S.x = SXA
S.set(T_RUN1 - 0.1, "stand", "deadpan", dur=0.15, run=0.0, look=(0.6, 0.6), stretch=-0.2)
S.set(T_RUN1 + 0.1, "stand", "deadpan", dur=0.3, ease="back", look=(0.7, 0.7))
S.sfx(T_RUN, "whoosh", 0.05); S.sfx(T_RUN1 - 0.1, "skid", 0.05, dur=0.3)
def run_x(t): return 540 + lerp(SX0, SXA, smooth(ramp(t, T_RUN, T_RUN1)))
_ct = T_RUN - 0.05
while _ct < T_RUN1 + 0.6:
    S.camera(_ct, run_x(_ct + 0.05) + 230, 1010, lerp(1.0, 0.85, smooth(ramp(_ct, T_RUN, T_RUN + 0.4)) * (1 - smooth(ramp(_ct, T_RUN1 - 0.4, T_RUN1 + 0.5)))),
             dur=1 / 15, ease="linear")
    _ct += 1 / 15
S.camera(T_RUN1 + 0.7, XA + 330, 1120, 1.15, 0.6)
def smoke_wall(cr, t, p, ly):
    """a wall of Mordor smoke at the border (hides where one world meets the other); he runs through it."""
    if ly != "front" or t >= T_RUN1 + 1.0: return
    for i in range(-4, 16):
        for j in range(2):
            y = FLOOR_Y + 200 - i * 260 + 40 * math.sin(t * 1.3 + i)
            x = BORDER - 120 + 240 * j + 60 * math.sin(t * 0.9 + i * 1.7 + j)
            dark = lerp(0.8, 0.25, j)
            O.draw_smoke_puff(cr, x, y, 260 + 40 * math.sin(i * 2.3 + j), alpha=1.0, dark=dark)
S.prop(smoke_wall)
def run_fx(cr, t, p, ly):
    if ly != "back" or not (T_RUN + 0.2 <= t < T_RUN1 - 0.2): return
    h = p["hip"]
    for k, dy in enumerate((-400, -200, 0)):
        L.motion_lines(cr, h[0] - 200, h[1] + dy, math.pi, n=1, length=360, alpha=0.7, sid=7110 + k, width=6)
S.prop(run_fx)

# ---------------------------------------------------------------- the kitten in the box
L.POSES["crouch_reach"] = dict(L.POSES["crouch"]); L.POSES["crouch_reach"].update(relb=(640, 1150), rhand=(730, 1240), rhand_t="open")
L.POSES["cradle"] = dict(lelb=(470, 985), lhand=(515, 925), relb=(612, 985), rhand=(566, 925), lhand_t="grip", rhand_t="grip")
L.POSES["to_head"] = dict(lelb=(440, 720), lhand=(505, 540), relb=(642, 720), rhand=(577, 540), lhand_t="grip", rhand_t="grip")
L.POSES["reach_up"] = dict(lelb=(470, 690), lhand=(500, 540), relb=(612, 690), rhand=(585, 540), lhand_t="open", rhand_t="open")
S.set(T_POPUP + 0.3, "stand", "deadpan", dur=0.25, look=(0.8, 0.9), tilt=0.05)
S.set(T_CROUCH, "crouch", "deadpan", dur=0.35, look=(0.8, 0.5), tilt=0.05)
S.set(T_SNIFF - 0.2, "crouch_reach", "deadpan", dur=0.4, look=(0.8, 0.5), tilt=0.05)
S.set(T_SNIFF + 0.5, "crouch_reach", "deadpan", dur=0.3, look=(0.0, 0.0))                 # us
S.set(T_KBLINK, "crouch_reach", "deadpan", dur=0.25, look=(0.8, 0.5))                      # it slow-blinks...
S.set(T_HBLINK, "crouch_reach", "deadpan", dur=0.3, look=(0.8, 0.5), lid=1.0)              # ...he slow-blinks back
S.set(T_HBLINK + 0.55, "crouch_reach", "deadpan", dur=0.3, look=(0.8, 0.5), lid=0.3, brow=0.2)
S.cut(T_PICK - FR)
S.set(T_PICK - FR, "cradle", "deadpan", dur=0.0, look=(0.3, 0.8), tilt=0.06)              # holding it
S.set(T_SMILE0, "cradle", "neutral", dur=0.5, look=(0.0, 0.0), smile=0.45, lid=0.2)   # "be happy": a small try
S.set(T_SMILE0 + 0.6, "cradle", "neutral", dur=0.4, look=(0.3, 0.8), smile=0.5, lid=0.2, tilt=0.06)
S.set(T_SMILE1, "cradle", "neutral", dur=0.7, look=(0.3, 0.85), smile=0.75, lid=0.2, tilt=0.08)                 # it purrs: soft
S.set(T_SMILE1 + 0.6, "cradle", "neutral", dur=0.3, look=(0.0, 0.0), smile=0.75, lid=0.15)
S.camera(T_PICK, XA + 300, 1060, 1.15, 1.5)
# strays everywhere
S.camera(T_LOOK, BR[0] - 150, 640, 0.62, 0.55)
S.camera(T_LOOK + 1.15, PILE_X + 200, 1000, 0.72, 0.5)
S.camera(T_LOOK + 1.95, XA + 300, 1060, 1.05, 0.4)
S.set(T_LOOK + 0.1, "cradle", "neutral", dur=0.25, look=(0.9, -0.6), smile=0.5)          # the tree
S.set(T_LOOK + 1.15, "cradle", "neutral", dur=0.3, look=(-0.9, 0.3), smile=0.5, turn=-0.3)   # the boxes
S.set(T_LOOK + 1.95, "cradle", "neutral", dur=0.3, look=(0.0, 0.0), smile=0.5)
S.set(T_HEAD, "to_head", "neutral", dur=0.35, look=(0.0, -0.8), smile=0.5)                  # onto his head it goes
S.set(T_HEAD + 0.5, "stand", "neutral", dur=0.3, look=(0.0, 0.0), smile=0.4)
S.camera(T_HEAD - 0.2, XA + 300, 980, 0.95, 0.6)

# ---------------------------------------------------------------- the hammer + the build
def hammer(cr, x, y, s, t, p):
    if T_CLOUD1 + 0.6 <= t: return
    O.draw_hammer(cr, x, y, s=0.9 * s, ang=0.15)
_k0 = len(S.keys)
S.pocket_pull(T_PULL, "hammer", hammer, (0, 0), held=True, offset=(0, 10), narrow_w=0)
for i in range(_k0, len(S.keys)):
    k = S.keys[i]; d = dict(k[1]); d.update(dict(L.EXPR["neutral"])); d.update(eyes="normal", mouth="auto", tongue=0.0, blush=0.0, open=0.0, eyescale=1.0, smile=0.4, lid=0.15, brow=0.1, worry=0.0, skeptic=0.0, fx_sparkle=0.0)
    S.keys[i] = (k[0], d) + tuple(k[2:])
S.walk_to(T_CLOUD0 - 0.5, SXB, 0.45)
S.set(T_CLOUD0 - 0.1, "stand", "neutral", dur=0.2, look=(0.8, 0.1), turn=0.5, smile=0.4)
S.camera(T_CLOUD0 - 0.5, SH - 300, 940, 0.66, 0.5)
L.POSES["ham_up"] = dict(relb=(670, 820), rhand=(700, 690), rhand_t="grip")
L.POSES["ham_dn"] = dict(relb=(690, 960), rhand=(800, 1010), rhand_t="grip")
HITS = [T_CLOUD0 + 0.35 + k * 0.32 for k in range(8)]
for k, th in enumerate(HITS):                                     # one swing = one tap, in sync
    S.set(th - 0.2, "ham_up", "neutral", dur=0.14, look=(0.8, 0.2), turn=0.5, smile=0.4, brow=0.15)
    S.set(th, "ham_dn", "neutral", dur=0.07, ease="snap", look=(0.8, 0.3), turn=0.5, smile=0.4, brow=0.15)
    S.sfx(th, ("tap", "tok")[k % 2], 0.05)
S.set(HITS[-1] + 0.3, "stand", "neutral", dur=0.3, look=(0.8, 0.0), turn=0.5, smile=0.4)
S.sfx(T_CLOUD0, "poof", 0.06)
S.set(T_CLOUD1 + 0.05, "stand", "neutral", dur=0.3, look=(0.8, -0.5), turn=0.3, smile=0.4, brow=0.3)
S.sfx(T_CLOUD1, "pop", 0.12); S.sfx(T_CLOUD1 + 0.1, "ding", 0.05)
S.set(T_CLOUD1 + 0.8, "stand", "neutral", dur=0.3, look=(0.0, 0.0), smile=0.5)

# ---------------------------------------------------------------- rescue 1: the cat up the tree
XT = BR[0] - 60
S.cut(CUT_TREE - FR, cam=(XT - 60, 700, 0.62), x=XT - 540)
S.set(CUT_TREE - FR, "stand", "neutral", dur=0.0, look=(0.5, -1.0), tilt=-0.1, smile=0.3)
S.set(T_REACH, "reach_up", "neutral", dur=0.35, look=(0.4, -1.0), tilt=-0.12, smile=0.3)
S.set(T_CJUMP + 0.35, "cradle", "neutral", dur=0.15, ease="snap", look=(0.2, 0.8), smile=0.5)
S.set(T_CJUMP + 0.9, "cradle", "neutral", dur=0.3, look=(0.0, 0.0), smile=0.6)
S.sfx(T_CJUMP, "whoosh", 0.03); S.sfx(T_CJUMP + 0.4, "pat", 0.06)
# ---------------------------------------------------------------- in through the door
S.cut(CUT_DOOR - FR, cam=(SH - 150, 950, 0.72), x=SH - 300 - 540)
S.set(CUT_DOOR - FR, "cradle", "neutral", dur=0.0, look=(0.8, 0.3), smile=0.6, turn=0.3)
S.set(CUT_DOOR + 0.55, "present", "neutral", dur=0.2, look=(0.8, 0.4), smile=0.6, turn=0.3)
S.set(CUT_DOOR + 1.1, "stand", "neutral", dur=0.3, look=(0.0, 0.0), smile=0.6)
S.sfx(CUT_DOOR + 0.2, "squeak", 0.02); S.sfx(CUT_DOOR + 1.5, "tok", 0.04)
# ---------------------------------------------------------------- rescue 2: the ducklings
S.cut(CUT_DUCK - FR, cam=(PILE_X + 500, 980, 0.72), x=PILE_X + 150 - 540)
S.set(CUT_DUCK - FR, "stand", "neutral", dur=0.0, look=(-0.8, 0.5), smile=0.5, turn=-0.3)
S.walk_to(T_DWALK0, SH + 300 - 540, T_DWALK1 - T_DWALK0)
S.set(T_DWALK0 + 0.3, "stand", "neutral", dur=0.3, look=(0.8, 0.0), smile=0.5, turn=0.4)
S.set(T_DWALK1 + 0.3, "stand", "neutral", dur=0.3, look=(-0.8, 0.4), smile=0.6, turn=-0.4)   # watches them go in
S.set(T_DCLOSE + 0.2, "stand", "neutral", dur=0.3, look=(0.0, 0.0), smile=0.6)
S.nod(T_DCLOSE + 0.35, 1)
_ct = T_DWALK0
while _ct < T_DWALK1 + 0.5:
    S.camera(_ct, lerp(PILE_X + 150, SH + 300, smooth(ramp(_ct, T_DWALK0, T_DWALK1))) - 150, 980, 0.72, dur=1 / 15, ease="linear")
    _ct += 1 / 15
S.sfx(27.4, "squeak", 0.02); S.sfx(T_DCLOSE, "tok", 0.04)

# ================================================================ INSIDE
L.POSES["hold_can"] = dict(relb=(650, 900), rhand=(690, 830), rhand_t="grip")
S.cut(CUT_IN - FR, cam=(60850, 1060, 0.8), x=SXI)
S.set(CUT_IN - FR, "hold_can", "neutral", dur=0.0, look=(0.6, 0.0), smile=0.4)
S.set(T_CAN, "hold_can", "neutral", dur=0.15, look=(0.3, -0.2), smile=0.4)
S.set(T_CAN + 0.4, "hold_can", "neutral", dur=0.3, look=(0.8, 0.4), smile=0.4, brow=0.3)     # every head turns
S.set(T_FEED0 + 0.6, "stand", "neutral", dur=0.4, look=(0.8, 0.8), smile=0.65)
S.sfx(T_CAN, "poof", 0.04); S.sfx(T_CAN, "tick", 0.06)
for i in range(6): S.sfx(T_FEED0 + 0.4 + i * 0.08, "tok", 0.02)
for i in range(10): S.sfx(T_FEED0 + 1.0 + i * 0.2, "chomp", 0.015)
# the fancy bed
S.camera(T_BED - 0.3, 61450, 1080, 0.8, 0.6)
S.set(T_BED - 0.2, "present", "neutral", dur=0.3, look=(0.8, 0.5), smile=0.6)
S.sfx(T_BED, "pop", 0.08)
S.set(T_BOX0 + 0.3, "stand", "neutral", dur=0.3, look=(0.9, 0.4), smile=0.3)                 # they walk past it...
S.set(T_BOX0 + 1.5, "stand", "deadpan", dur=0.3, look=(0.9, 0.4))                            # ...into the box
S.set(T_BOX0 + 2.1, "stand", "deadpan", dur=0.3, look=(0.0, 0.0), smile=0.25)                # us
for i in range(5): S.sfx(T_BOX0 + 0.2 + i * 0.25, "tok", 0.03)
# the mug
S.cut(CUT_MUG - FR, cam=(60420, 950, 1.0))
S.set(CUT_MUG - FR, "stand", "neutral", dur=0.0, look=(-0.6, -0.4), smile=0.2, turn=-0.3)
S.set(MUG_N[1] + 0.25, "stand", "deadpan", dur=0.25, look=(-0.6, -0.4), turn=-0.3)
L.POSES["catch"] = dict(lelb=(420, 980), lhand=(345, 1060), lhand_t="open")
S.set(T_CATCH - 0.12, "catch", "deadpan", dur=0.1, ease="snap", look=(-0.7, 0.4), turn=-0.3, lhand_t="grip")
S.set(T_CATCH + 0.5, "catch", "deadpan", dur=0.3, look=(0.0, 0.0), lhand_t="grip")           # us
for tn in MUG_N[:2]: S.sfx(tn + 0.1, "tok", 0.03)
S.sfx(T_CATCH, "pat", 0.08)

# ================================================================ ADOPTION DAY
S.cut(CUT_ADOPT - FR, cam=(SH - 300, 900, 0.62), x=SXB)
S.set(CUT_ADOPT - FR, "stand", "neutral", dur=0.0, look=(-0.6, 0.0), smile=0.5, show=0.0)
S.sfx(CUT_ADOPT + 0.75, "squeak", 0.02)
S.cut(CUT_MOM - FR, cam=(61350, 1000, 0.72), x=SXI)
S.set(CUT_MOM - FR, "stand", "neutral", dur=0.0, look=(0.9, 0.0), smile=0.5, show=1.0)
S.set(T_MCAT + 0.4, "stand", "neutral", dur=0.4, look=(0.9, 0.0), smile=0.8, brow=0.2)
# stamping
L.POSES["stamp_up"] = dict(relb=(660, 820), rhand=(720, 660), rhand_t="grip")
S.cut(CUT_STAMP - FR, cam=(61150, 980, 0.95))
S.set(CUT_STAMP - FR, "stand", "neutral", dur=0.0, look=(0.9, -0.4), smile=0.5)
def stamp_x(t):
    for i, ts in enumerate(STAMP_ALL):
        if t < ts - 0.15: return PHOTOS[i][0] - 230
    return PHOTOS[7][0] - 230
_xk = []
for i, ts in enumerate(STAMP_ALL):
    S.xkeys.append((ts - 0.35 if i else CUT_STAMP - FR, PHOTOS[i][0] - 230 - 540, 0.2 if i else 0.0, "smooth"))
    S.sfx(ts, "thud", 0.12); S.sfx(ts + 0.02, "tap", 0.05)
S.x = PHOTOS[7][0] - 230 - 540
def stamp_hand(tt, p):
    if not (CUT_STAMP - FR <= tt < CUT_HUG - FR): return p
    k = len([s for s in STAMP_ALL if s <= tt])
    i = min(k, 7) if tt < STAMP_ALL[min(k, 7)] - 0.0 else min(k, 7)
    nxt = next((j for j, s in enumerate(STAMP_ALL) if s > tt - 0.12), 7)
    px, py = PHOTOS[nxt]
    ts = STAMP_ALL[nxt]
    lift = 0.0 if tt >= ts else min(1.0, (ts - tt) / 0.18)
    if nxt == 7 and tt < T_LAST - 0.2: lift = 1.0                  # hesitates over the last one
    p["rhand"] = (px - 10, py - 40 - 90 * lift); p["rhand_t"] = "grip"
    p["relb"] = ((p["neck"][0] + px) / 2 + 30, (p["neck"][1] + py) / 2 + 90)
    return p
S.hook(stamp_hand)
S.set(STAMP_ALL[6] + 0.4, "stand", "neutral", dur=0.3, look=(0.7, -0.3), smile=0.4)
S.set(48.0, "stand", "neutral", dur=0.3, look=(0.7, -0.2), smile=0.2)                        # the last photo
S.set(48.35, "stand", "neutral", dur=0.3, look=(0.0, -1.0), smile=0.2, brow=0.4)             # up at the kitten on his head
S.set(T_LAST - 0.15, "stand", "neutral", dur=0.2, look=(0.7, -0.2), smile=0.6)
S.sfx(T_LAST + 0.1, "ding", 0.08)
# the hug: a real smile
S.cut(CUT_HUG - FR, cam=(PHOTOS[7][0] - 230, 900, 1.2))
S.set(CUT_HUG - FR, "cradle", "delighted", dur=0.0, blush=0.0, look=(0.2, 0.6), tilt=0.1)
S.set(CUT_HUG + 0.6, "cradle", "delighted", dur=0.4, blush=0.0, eyes="happy", tilt=0.14)
S.set(CUT_HUG + 1.8, "cradle", "happy", dur=0.4, look=(0.0, 0.0), smile=0.9, tilt=0.06)
S.sfx(CUT_HUG + 0.4, "twinkle", 0.04)

# ================================================================ THE ASK (outside, kitten on his head)
ASKX = XB + 140
S.cut(CUT_ASK - FR, cam=(ASKX + 250, 1000, 0.98), x=ASKX - 540)
S.set(CUT_ASK - FR, "stand", "neutral", dur=0.0, look=(0.0, 0.0), smile=0.6)
DONATE = ["TO HELP SAVE", "REAL CATS,", "PLEASE DONATE", "TO THE CAT HOUSE", "ON THE KINGS AT", "CATHOUSEON", "THEKINGS.COM"]
ASKL = ["TELL ME", "WHAT TO DO", "NEXT IN THE", "COMMENTS"]
_orig_front = L.sign_front
F_DON = _orig_front(" ".join(DONATE), lines=DONATE)
F_ASK = _orig_front(" ".join(ASKL), lines=ASKL)
def _front(cr, w, h): (F_ASK if NOW[0] >= T_PAGE + 0.18 else F_DON)(cr, w, h)
L.sign_front = lambda *a, **k: _front
S.t = T_ASK
S.the_ask(T_ASK, hold=ASK_HOLD + 2.9, push=False, keep=dict(mouth="auto", smile=0.6))
L.sign_front = _orig_front
S.sfx(T_PAGE, "flip", 0.07)
S.camera(T_ASK + 6.9, ASKX, 1180, 1.75, 0.7)
S.camera(T_PAGE + 0.35, ASKX + 200, 1060, 1.12, 0.5)
def page_flip(cr, t, p, ly):
    if ly != "front" or not (T_PAGE <= t < T_PAGE + 0.36): return
    u = (t - T_PAGE) / 0.36
    cx, cy = 540 + ASKX - 540, 1120 - 16
    top = cy - 280 + 26
    hgt = (560 - 60) * (1 - u) if u < 0.5 else 0
    if u < 0.5:
        L.sketch_rect(cr, cx - 205, top, cx + 205, top + (560 - 60) * (1 - 2 * u), 4, sid=10900, fill=(1, 1, 1))
    else:
        L.sketch_rect(cr, cx - 205, top - 160 * (u - 0.5) * 2, cx + 205, top, 4, sid=10901, fill=(0.95, 0.95, 0.93))
S.prop(page_flip)

# ================================================================ cats
def head_kitten(t):
    return T_HEAD + 0.3 <= t and not (CUT_ADOPT - FR <= t < CUT_MOM - FR) \
        and not (CUT_HUG - FR <= t < CUT_ASK - FR)

def kitten(cr, t, p):
    bl = 0.0
    if T_KBLINK <= t < T_KBLINK + 0.8: bl = math.sin(math.pi * (t - T_KBLINK) / 0.8)
    if CUT_HUG + 0.9 <= t < CUT_HUG + 1.7: bl = math.sin(math.pi * (t - CUT_HUG - 0.9) / 0.8)
    if t < T_POPUP - 0.3: return
    if t < T_PICK - FR:                                       # in the box: pops up, sniffs, slow blink
        u = smooth(ramp(t, T_POPUP, T_POPUP + 0.3))
        y = FLOOR_Y + 20 - 150 + 120 * (1 - u)
        cr.save(); cr.rectangle(KBOX - 400, -5000, 800, 5000 + FLOOR_Y + 20 - 150 + 4); cr.clip()
        lk = (-0.7, -0.3) if t > T_POPUP + 0.5 else (0.0, 0.0)
        if T_SNIFF <= t < T_SNIFF + 0.8: lk = (-1.0, 0.2)
        O.draw_cat(cr, KBOX, y + 40, s=KS, t=t, kind="sit", col="black", look=lk, blink=bl, sid=2000)
        cr.restore()
        if T_SNIFF <= t < T_SNIFF + 0.8:
            L.burst_lines(cr, KBOX - 80, y - 100, ((t - T_SNIFF) % 0.4) / 0.4, r0=20, r1=40, n=3, sid=2010)
        return
    if T_PICK - FR <= t < T_HEAD + 0.3 or CUT_HUG - FR <= t < CUT_ASK - FR:   # in his arms
        k = smooth(ramp(t, T_HEAD, T_HEAD + 0.3)) if t < CUT_HUG else 0.0
        hx = (p["lhand"][0] + p["rhand"][0]) / 2; hy = (p["lhand"][1] + p["rhand"][1]) / 2 + 35
        tx, ty = p["head"][0], p["head"][1] - 110
        x, y = lerp((hx, hy), (tx, ty), k)
        O.draw_cat(cr, x, y, s=KS, t=t, kind="loaf", col="black", look=(0.4, -0.6) if t < CUT_HUG else (0.3, -0.8), blink=bl, sid=2000)
        if t >= T_SMILE1 - 0.6 and t < T_LOOK or t >= CUT_HUG:                      # purr lines
            for side in (-1, 1):
                L.motion_lines(cr, x + side * 90, y - 60, math.pi * (1 if side < 0 else 0), n=2, length=30, alpha=0.6, sid=2020 + side, width=4)
        return
    if head_kitten(t):
        hx, hy = p["head"]
        lk = (0.0, 0.0)
        if 47.9 <= t < 48.6: lk = (0.6, 1.0)
        O.draw_cat(cr, hx + 5, hy - 104, s=KS, t=t, kind="loaf", col="black", look=lk, sid=2000, tilt=p.get("tilt", 0.0) * 0.6)

# outside strays
def tree_cat(cr, t, p):
    if t < CUT_TREE - FR + 0.0 and t >= T_LOOK - 0.5 or CUT_TREE - FR <= t < T_CJUMP:
        O.draw_cat(cr, BR[0] - 20, BR[1] + 4, s=0.62, t=t, kind="sit", col="orange", look=(-0.3, 0.8), sid=2100)
    elif T_CJUMP <= t < CUT_DOOR + 0.6:
        u = ramp(t, T_CJUMP, T_CJUMP + 0.4, "linear")
        hx = (p["lhand"][0] + p["rhand"][0]) / 2; hy = (p["lhand"][1] + p["rhand"][1]) / 2 + 35
        if t < CUT_DOOR - FR:
            a = (BR[0] - 20, BR[1] + 4)
            x = lerp(a[0], hx, u); y = lerp(a[1], hy, u) - 120 * 4 * u * (1 - u)
            O.draw_cat(cr, x, y, s=0.62, t=t, kind="fall" if u < 1 else "loaf", col="orange", look=(0.0, 0.5), sid=2100)
        else:
            u2 = ramp(t, CUT_DOOR + 0.5, CUT_DOOR + 0.6)
            O.draw_cat(cr, lerp(hx, SH, u2), hy, s=0.62, t=t, kind="loaf", col="orange", look=(0.6, 0.0), sid=2100)

DUCKS = ["grey", "white", "cream"]
def ducklings(cr, t, p):
    if t < T_LOOK - 0.5: return
    for i, col in enumerate(DUCKS):
        bx = PILE_X - 120 + 230 * i
        if t < T_DWALK0 + 0.3 + 0.25 * i:                     # peeking out of the boxes
            if CUT_TREE - FR <= t < CUT_DUCK - FR: continue
            cr.save(); cr.rectangle(bx - 300, -5000, 600, 5000 + FLOOR_Y - 110); cr.clip()
            O.draw_cat(cr, bx, FLOOR_Y - 30, s=0.55, t=t, kind="sit", col=col, look=(0.6, -0.2), sid=2200 + 40 * i)
            cr.restore()
            continue
        hipx = p["hip"][0]
        x = hipx - 220 - 170 * i
        arrive = t >= 27.6 and x >= SH - 40
        if t >= T_DCLOSE - 0.3 or (x >= SH - 40 and t >= 27.6): continue
        x = min(x, SH + 300)
        O.draw_cat(cr, x, FLOOR_Y + 30, s=0.55, t=t, kind="walk", col=col, face=1, phase=t * 9 + i, sid=2200 + 40 * i)

# inside: the rescued cats
IN_CATS = [dict(col="orange", home=(SHELF_X - 100, SHELF_Y[0]), kind="sit"), dict(col="grey", home=(SHELF_X + 110, SHELF_Y[0]), kind="loaf"),
           dict(col="white", home=(SHELF_X, SHELF_Y[1]), kind="sit"), dict(col="cream", home=(60700 - 380, FLOOR_Y + 30), kind="loaf"),
           dict(col="brown", home=(61250, FLOOR_Y + 40), kind="sit"), dict(col="grey", home=(61480, FLOOR_Y + 30), kind="loaf")]
BOXSPOTS = [(FBOX - 60, FLOOR_Y - 120), (FBOX + 60, FLOOR_Y - 125), (FBOX, FLOOR_Y - 190), (FBOX - 70, FLOOR_Y - 250),
            (FBOX + 70, FLOOR_Y - 255), (FBOX, FLOOR_Y - 320)]
def arc(a, b, u, h=200):
    u = max(0.0, min(1.0, u)); return (lerp(a[0], b[0], u), lerp(a[1], b[1], u) - h * 4 * u * (1 - u))
def inside_cats(cr, t, p):
    for i, c in enumerate(IN_CATS):
        if i == 0 and t >= T_MCAT: continue                   # the orange cat goes home with the mom
        home, bowl = c["home"], (BOWLS[i], FLOOR_Y + 30)
        box = BOXSPOTS[i]
        lk = (math.sin(t * 0.7 + i) * 0.5, 0.0); kind = c["kind"]; xy = home; bob = 0.0
        if t >= T_CAN + 0.05: lk = ((1 if IX > home[0] else -1) * 0.9, -0.3)
        if t >= T_FEED0:
            u = (t - T_FEED0 - 0.08 * i) / 0.6
            xy = arc(home, bowl, u, 160); kind = "fall" if u < 1 else "loaf"
            if u >= 1: lk = (0.0, 1.0); bob = 8 * abs(math.sin(t * 9 + i))
        if t >= T_BOX0:
            u = (t - T_BOX0 - 0.25 * i) / 0.45
            if u > 0: xy = arc(bowl, box, u, 180); kind = "fall" if u < 1 else "loaf"; lk = (-0.4, 0.0) if u >= 1 else (0.6, 0.0); bob = 0
            if u > 0 and u < 1: pass
        if t >= CUT_MUG - FR and i == 2:                       # the white cat is the mug-pusher (on the top shelf)
            xy = (SHELF_X + 120, SHELF_Y[1]); kind = "sit"; lk = (0.9, 0.2)
            if MUG_N[1] + 0.2 <= t < MUG_N[2]: lk = (0.9, 0.6)
        if t >= CUT_STAMP - FR: break
        O.draw_cat(cr, xy[0], xy[1] + bob * 0, s=0.6, t=t, kind=kind, col=c["col"], look=lk, sid=2300 + 40 * i,
                   tilt=0.0, blink=1.0 if (t + i * 0.9) % 3.6 < 0.12 else 0.0)
        if kind == "loaf" and t >= T_FEED0 and t < T_BOX0 and bob: pass
    # the mug
    if CUT_MUG - FR <= t < CUT_ADOPT - FR:
        mx = SHELF_X + 200
        for k, tn in enumerate(MUG_N): mx += (14 if k < 2 else 60) * smooth(ramp(t, tn, tn + 0.15))
        if t < MUG_N[2] + 0.12:
            O.draw_mug(cr, mx, SHELF_Y[1])
        elif t < T_CATCH:
            s_ = t - MUG_N[2] - 0.12
            O.draw_mug(cr, mx + 40 * s_, SHELF_Y[1] + 0.5 * 2600 * s_ * s_, ang=4 * s_)
        else:
            hx, hy = p["lhand"]; O.draw_mug(cr, hx, hy + 40)
        for tn in MUG_N:                                       # the paw
            k = pulse(t, tn + 0.06, 0.1)
            if k > 0.05:
                sx_, sy_ = SHELF_X + 160, SHELF_Y[1] - 50
                L.sketch_line(cr, [(sx_, sy_), (sx_ + 50 * k, sy_ - 5)], 14, sid=2390)
                L.sketch_ellipse(cr, sx_ + 50 * k, sy_ - 5, 14, 11, 4, sid=2391, fill=(1, 1, 1))
    # can in his hand
    if CUT_IN - FR <= t < T_FEED0 + 0.6:
        hx, hy = p["rhand"]
        L.sketch_rect(cr, hx - 34, hy - 70, hx + 34, hy + 10, 5, sid=2395, fill=(0.82, 0.84, 0.88))
        L.sketch_rect(cr, hx - 34, hy - 50, hx + 34, hy - 10, 3, sid=2396, fill=(0.95, 0.55, 0.45))
        if T_CAN <= t < T_CAN + 0.4: L.burst_lines(cr, hx, hy - 80, (t - T_CAN) / 0.4, r0=30, r1=80, n=6, sid=2397)
    # the stamp in his hand
    if CUT_STAMP - FR <= t < CUT_HUG - FR:
        hx, hy = p["rhand"]; O.draw_stamp(cr, hx + 10, hy + 40, s=0.9)

# ---------------------------------------------------------------- the mom (day 6 callback) adopts the orange cat
MXK = Track([(0.0, 34500.0, 0), (CUT_ADOPT, 34500.0, 0), (CUT_ADOPT, 34500.0, 0), (CUT_ADOPT + 0.05, SH - 60, 1.0, "smooth"),
             (CUT_MOM, 62900.0, 0), (CUT_MOM + 0.05, 61700.0, 0.7, "out"), (T_MOUT, 61700.0, 0), (T_MOUT + 0.05, 63300.0, 1.0, "inn")])
def mom_pose(t):
    x = MXK.at(t)
    v = (MXK.at(t + 0.03) - MXK.at(t - 0.03)) / 0.06
    face = "happy"; kw = dict(look=(0.0, 0.0))
    if CUT_ADOPT <= t < CUT_MOM: kw.update(turn=0.8, look=(0.8, 0.0))
    if CUT_MOM <= t: kw.update(turn=-0.8, look=(-0.8, 0.3))
    if CUT_MOM + 0.7 <= t < T_MOUT: face = "delighted"; kw.update(blush=0.0, look=(-0.8, 0.5))
    if t >= T_MOUT: kw.update(turn=0.8, look=(0.8, 0.2))
    p = L.pose("stand", face, **kw)
    ox = x - 540
    for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1])
    if abs(v) > 30:
        ph = t * 2 * math.pi * 1.6; hipx, hipy = p["hip"]
        for side, off in (("l", 0.0), ("r", math.pi)):
            s_ = math.sin(ph + off); lf = max(0.0, math.cos(ph + off)) * 30
            p[side + "foot"] = (hipx + 50 * s_, FLOOR_Y - lf)
            p[side + "knee"] = (hipx + 25 * s_ + (14 if v > 0 else -14), (hipy + FLOOR_Y) / 2 - lf * 0.6)
        bob = 8 * abs(math.sin(ph))
        for k in ("head", "neck", "hip", "lelb", "relb", "lhand", "rhand"): p[k] = (p[k][0], p[k][1] + bob)
    cl = smooth(ramp(t, CUT_MOM + 0.7, CUT_MOM + 1.0)) if t >= CUT_MOM else 0.0
    if cl > 0:                                                         # hands together / holding the cat
        cc = (p["neck"][0], p["neck"][1] + 150 if t >= T_MCAT + 0.3 else p["neck"][1] + 60)
        p["lhand"] = lerp(p["lhand"], (cc[0] - 22, cc[1]), cl); p["rhand"] = lerp(p["rhand"], (cc[0] + 22, cc[1]), cl)
        p["lhand_t"] = p["rhand_t"] = "grip"
    return L.constrain(p)
def mom(cr, t, p, ly):
    if ly != "back": return
    if CUT_ADOPT - FR <= t < CUT_MOM - FR:
        q = mom_pose(t); O.draw_mom(cr, t, q, 0.0, s=0.92, alpha=1.0 - ramp(t, CUT_MOM - 0.4, CUT_MOM - 0.1))
    elif CUT_MOM - FR <= t < T_MOUT + 1.2:
        q = mom_pose(t); O.draw_mom(cr, t, q, 0.0, s=0.92)
        fx = (q["lfoot"][0] + q["rfoot"][0]) / 2
        def sc(pt): return (fx + (pt[0] - fx) * 0.92, FLOOR_Y + (pt[1] - FLOOR_Y) * 0.92)
        if t >= T_MCAT - 0.4:
            hx, hy = sc(((q["lhand"][0] + q["rhand"][0]) / 2, (q["lhand"][1] + q["rhand"][1]) / 2))
            u = ramp(t, T_MCAT - 0.4, T_MCAT, "linear")
            a = BOXSPOTS[0]
            x, y = arc(a, (hx, hy + 40), u, 220)
            O.draw_cat(cr, x, y, s=0.6, t=t, kind="fall" if u < 1 else "loaf", col="orange", look=(0.3, -0.5), sid=2300,
                       blink=0.8 if T_MCAT + 0.4 <= t < T_MCAT + 0.9 else 0.0)
            if t >= T_MCAT + 0.2:
                for k in range(3):
                    v_ = ((t - T_MCAT) * 0.8 + k / 3) % 1.0
                    heart(cr, hx - 40 + 40 * k, hy - 160 - 160 * v_, 16, alpha=1 - v_)
S.prop(mom)

def heart(cr, x, y, hs, alpha=1.0):
    cr.move_to(x, y + hs * 0.9); cr.curve_to(x - hs * 1.6, y - hs * 0.2, x - hs * 0.5, y - hs * 1.3, x, y - hs * 0.35)
    cr.curve_to(x + hs * 0.5, y - hs * 1.3, x + hs * 1.6, y - hs * 0.2, x, y + hs * 0.9)
    cr.set_source_rgba(0.92, 0.30, 0.38, alpha); cr.fill_preserve(); cr.set_source_rgba(0.07, 0.07, 0.08, alpha); cr.set_line_width(3); cr.stroke()

def cats(cr, t, p, ly):
    if ly == "back":
        if t < CUT_IN - FR or CUT_ADOPT - FR <= t < CUT_MOM - FR or t >= CUT_ASK - FR:
            tree_cat(cr, t, p); ducklings(cr, t, p)
        else:
            inside_cats(cr, t, p)
        return
    kitten(cr, t, p)
    if T_CLOUD0 <= t < T_CLOUD1:
        O.draw_build_cloud(cr, SH, 1100, t, T_CLOUD0, T_CLOUD1 - T_CLOUD0, r=620)
    if T_CLOUD1 <= t < T_CLOUD1 + 0.35:
        L.burst_lines(cr, SH, 900, (t - T_CLOUD1) / 0.35, r0=560, r1=820, n=12, sid=89)
    if CUT_HUG - FR <= t < CUT_ASK - FR:
        hx = (p["lhand"][0] + p["rhand"][0]) / 2; hy = (p["lhand"][1] + p["rhand"][1]) / 2
        for k in range(3):
            v_ = ((t - CUT_HUG) * 0.6 + k / 3) % 1.0
            heart(cr, hx - 70 + 70 * k, hy - 220 - 260 * v_, 20, alpha=1 - v_)
S.prop(cats)

# ---------------------------------------------------------------- sounds: mews, purrs, a can
SR = L.SR
def _t(d): return np.arange(int(d * SR)) / SR
def place(buf, sig, t0, g):
    i = int(t0 * SR)
    if 0 <= i < len(buf): m = min(len(sig), len(buf) - i); buf[i:i + m] += sig[:m] * g
def meow(f0=700, d=0.45):
    tt = _t(d); u = tt / d
    f = f0 * (0.85 + 0.35 * np.sin(np.pi * u ** 0.8)) * (1 + 0.02 * np.sin(2 * np.pi * 7 * tt))
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)
    env = np.minimum(1, tt / 0.03) * np.minimum(1, (d - tt) / 0.12) * (0.6 + 0.4 * np.sin(np.pi * u))
    return (sig * env * 0.35).astype(np.float32)
def purr(d, rate=26):
    tt = _t(d); nz = np.random.default_rng(9).standard_normal(len(tt))
    lp = np.convolve(nz, np.ones(60) / 60, mode="same")
    am = 0.5 + 0.5 * np.sin(2 * np.pi * rate * tt) ** 2
    return (lp * am * np.minimum(1, tt / 0.5) * np.minimum(1, (d - tt) / 0.4) * 6.0).astype(np.float32)
def extra(n):
    buf = np.zeros(n, np.float32)
    place(buf, meow(1300, 0.3), T_MEW, 0.35)
    place(buf, meow(1250, 0.35), T_POPUP + 0.1, 0.5)
    place(buf, meow(1350, 0.28), T_SMILE1 - 0.3, 0.25)
    rr = random.Random(5)
    for k in range(4): place(buf, meow(rr.uniform(800, 1200), 0.35), T_LOOK + 0.1 + k * 0.4, 0.25)
    place(buf, meow(900, 0.4), CUT_TREE + 0.3, 0.35)
    for k in range(3): place(buf, meow(1200 + 80 * k, 0.25), T_DWALK0 + 0.4 + k * 0.5, 0.25)
    for k in range(6): place(buf, meow(rr.uniform(800, 1300), 0.3), T_CAN + 0.1 + k * 0.07, 0.25)
    place(buf, meow(1000, 0.35), MUG_N[1] + 0.3, 0.25)
    place(buf, meow(1200, 0.35), T_MCAT + 0.3, 0.3)
    place(buf, meow(1300, 0.3), CUT_HUG + 0.5, 0.25)
    place(buf, meow(1300, 0.3), T_ASK + 7.5, 0.2)
    return buf * 0.5
_orig_soften = L._soften
def _soften_plus(x): return _orig_soften(x) + extra(len(x))
L._soften = _soften_plus

if __name__ == "__main__":
    print(f"page {T_PAGE:.2f} end {S.t:.2f}", file=sys.stderr)
    S.render("day011.mp4")
