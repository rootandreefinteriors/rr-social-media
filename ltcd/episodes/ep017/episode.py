"""Day 17 - COMMENT episode: @elijah_paradise "Get a girlfriend and have a baby" (Instagram, day 16 reel, 1 like).

He reads it on the beach and runs off to the right; hard cut on the run into a park at golden hour. A rose: she walks
right past, nose in her book. A boombox over his head: she puts her headphones on. He sits on the bench and eats
spaghetti - the smell brings her over; one noodle, two ends, a cartoon kiss. Girlfriend. Then a delivery stork: SIGN
HERE; it flies off still holding the bundle, notices, lets go - he dives and catches it an inch above the fountain.
The baby cries; he rocks it to sleep (he's done this before, day 6). She leans on his shoulder. Button: the stork comes
back with a second bundle, checks the clipboard, shakes its head, leaves. Ask in the park. See BEATS.md.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
import character as C
from ltcd import Track, ramp, lerp, FLOOR_Y
from ink import smooth, back_out, sketch_line, draw_text
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FR = 1 / 30

# ================================================================ places
BX = 700000.0                                       # the beach (as day 16 left it)
WX0, WX1 = BX - 6000.0, BX + 12000.0
PROM_END = BX - 1300.0
SUGAR = BX + 2600.0
RBX, RB = BX - 300.0 + 3600.0, 1500.0
LANDX = 705313.3938825098
BOX = LANDX - 540.0

PX = 900000.0                                       # the park: the bench centre
PW0, PW1 = PX - 6000.0, PX + 8000.0
TREES = (PX - 1700, PX - 650, PX + 900, PX + 2300)
LAMPS = (PX - 1150, PX + 650, PX + 2600)
FX, FS = PX + 1150.0, 0.75                          # the fountain
HX0 = PX - 200.0                                    # him: standing / sitting centre
GXS = PX + 200.0                                    # her: sitting centre
SIGNX = PX + 470.0                                  # him: signing
SKX, SKS = PX + 960.0, 1.3                          # the stork, standing
SKY = FLOOR_Y - 560 * SKS
CP = (FX - 60.0, FLOOR_Y - 200.0)                   # where he catches the bundle (his hands)
AFTX = PX - 150.0                                   # him after the cut (holding the baby)
GXA = PX + 240.0                                    # her after the cut (standing)

# ================================================================ timeline
T_READ = 0.3; T_WIDE = 1.6; T_US0 = 1.95; T_RUN = 2.3; CUT_IN = 3.3; T_ARR = 4.15
T_P1 = 4.6; T_POP1 = T_P1 + 1.4                     # the rose
G1A, G1B = 6.5, 9.5                                 # she walks right -> left past him
T_PETAL = 9.9; T_LOOKR = 10.2; T_US1 = 10.8
T_TOSS = 11.2
T_P2 = 11.7; T_POP2 = T_P2 + 1.4; T_UP = T_POP2 + 0.15   # the boombox
T_MUS = 13.4
G2A, G2B = 13.3, 14.8                               # she walks back in from the left, stops
T_SEE2 = 15.1; T_PHONES = 16.1; G2C, G2D = 16.7, 18.4
T_DIE = 16.5                                        # the song winds down
T_LOWER = 17.0; T_SETDN = 17.6; T_SIT = 18.0
T_P3 = 19.4; T_POP3 = T_P3 + 1.4                    # the spaghetti
G3A, G3B = 21.3, 22.6                               # she walks in again, stops, sniffs
T_SNIFF = 22.7; T_OFF = 23.1; G3C, G3D = 23.5, 24.1  # headphones off, steps to the bench, sits
T_LOOKH = 24.4; T_PLATE = 24.8                      # plate down between them
T_NOOD = 25.5; T_SLURP0 = 26.0; T_KISS = 28.2
T_RIGID = 28.6; T_HAND = 29.4; T_US2 = 30.3
T_CARD = 31.0; T_LOOKG = 31.9
T_SHADOW = 32.3; ST_IN0, ST_IN1 = 32.4, 33.9         # the stork swoops in, lands
T_CLIP = 34.2; T_STANDUP = 34.4; T_WALK = 34.8; T_SIGN0, T_SIGN1 = 35.8, 36.7
T_TIP = 37.0; ST_UP0, ST_UP1 = 37.4, 38.4           # takes off with the bundle
T_POINT = 38.0; T_NOTICE = 38.5; T_DROP = 38.9
T_DIVE = 39.05; T_CATCH = 39.75; T_SLIDE = 40.05
CUT2 = 41.0                                         # standing, holding the baby
T_CRY = 41.6; R0 = 42.6; T_ASLEEP = 44.6
T_IMPRESS = 45.0; T_LEAN = 45.7; T_SMILE = 46.3
ST2_IN0, ST2_IN1 = 47.4, 48.6                      # the stork again, a second bundle
T_TURN = 48.8; T_CLIP2 = 49.0; T_READC = 49.6; T_SHAKE = 50.2; ST2_UP0, ST2_UP1 = 51.0, 52.0
T_EXHALE = 52.1; T_GIVE0, T_GIVE1 = 52.6, 53.3
T_ASK = 53.7
ASK_HOLD = 8.0

# ================================================================ scene
S = M.Scene(x0=BOX)
S.auto_blinks = False
S.floor = False
S.card("elijah_paradise", "Get a girlfriend and have a baby", "1", t0=0.3)
CAM_B = (LANDX, 880, 1.0)
S.camkeys[0] = (0.0, CAM_B, 0); S.cam = CAM_B

def world(cr, t):
    if t < CUT_IN - FR:
        O.draw_beach_world(cr, t, WX0, WX1, PROM_END, sugar_x=SUGAR)
        O.draw_rainbow(cr, RBX, FLOOR_Y, RB + 30, band=60, sweep=1.0)
        O.draw_kite(cr, LANDX + 330, FLOOR_Y - 30, s=0.8, ang=1.35, t=0.0, tail=0.0)
        return
    O.draw_park_world(cr, t, PW0, PW1, trees=TREES, lamps=LAMPS)
    O.draw_sign(cr, PX - 2000, FLOOR_Y - 150, "PARK|OPEN TILL DUSK", w=560, size=54)
    O.draw_fountain(cr, FX, FLOOR_Y - 20, t, s=FS)
    O.draw_bench(cr, PX, FLOOR_Y - 10)
S.background(world)

# ================================================================ HIM: helpers
def dig_pull(t0, hold_pose, look=(0.4, -0.2), sitting=False, **kw):
    """the signature gag: eyes down, hand digs around at his hip (no pocket), POP - it's in his hand."""
    POCK = (595 + S.x, 1200 if sitting else 1092)
    body0 = "sit_bench" if sitting else "stand"
    S.set(t0, body0, "deadpan", dur=0.35, look=(0.35, 0.9), tilt=0.05, **kw)
    def hk(tt, p):
        if t0 + 0.25 <= tt < t0 + 1.35:
            u = ramp(tt, t0 + 0.25, t0 + 0.5)
            dig = ramp(tt, t0 + 0.5, t0 + 0.6) * (1 - ramp(tt, t0 + 1.2, t0 + 1.3))
            p["rhand"] = lerp(p["rhand"], (POCK[0] + 14 * math.sin(tt * 24) * dig, POCK[1] + 6 * math.sin(tt * 31) * dig), u)
        return p
    S.hook(hk)
    S.sfx(t0 + 0.55, "rummage", 0.04, dur=0.6)
    S.set(t0 + 1.35, hold_pose, "deadpan", dur=0.2, ease="back", look=look, **kw)
    S.sfx(t0 + 1.4, "pop", 0.08)
    def pr(cr, tt, p, ly):
        if ly == "front" and t0 + 1.4 <= tt < t0 + 1.7:
            L.burst_lines(cr, p["rhand"][0], p["rhand"][1] - 80, (tt - t0 - 1.4) / 0.4, r0=90, r1=160, n=10, sid=9)
    S.prop(pr)
    return t0 + 1.4

L.POSES["sit_bench"] = dict(head=(540, 752), neck=(540, 878), hip=(540, 1228), lknee=(400, 1300), rknee=(680, 1300),
                            lfoot=(430, FLOOR_Y), rfoot=(650, FLOOR_Y), lelb=(465, 1075), lhand=(462, 1200),
                            relb=(615, 1075), rhand=(618, 1200), lfoot_dir=-0.5, rfoot_dir=0.5, nowalk=1.0)
L.POSES["offer"] = dict(relb=(690, 880), rhand=(830, 830), rhand_t="grip")
L.POSES["boom_up"] = dict(lelb=(410, 620), lhand=(445, 460), relb=(670, 620), rhand=(635, 460), lhand_t="grip", rhand_t="grip")
L.POSES["hold_plate"] = dict(L.POSES["sit_bench"], lelb=(455, 1060), lhand=(495, 1145), relb=(625, 1060), rhand=(590, 1145),
                             lhand_t="grip", rhand_t="grip")
L.POSES["sign"] = dict(relb=(690, 960), rhand=(748, 1068), rhand_t="none")
L.POSES["point_stork"] = dict(relb=(660, 700), rhand=(760, 560), rhand_t="point")

# ================================================================ HIM: the beach -> the park
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(T_READ, react="deadpan", lines=1, dur=1.2, face="deadpan")
S.set(T_WIDE, "stand", "deadpan", dur=0.12, ease="snap", eyescale=1.18, curl_up=0.8, look=(0.7, -0.8))
S.set(T_US0, "stand", "dead_stare", dur=0.25, look=(0.0, 0.0))
S.set(T_RUN, "stand", "deadpan", dur=0.15, run=1.0, look=(0.9, 0.0), turn=0.5, lean=0.12)
S.xkeys.append((T_RUN, BOX + 1300, CUT_IN - T_RUN, "inn")); S.x = BOX + 1300
S.camera(T_RUN, LANDX + 250, 880, 1.0, 1.0)
S.sfx(T_RUN, "whoosh", 0.05)
CAM_P = (PX + 60, 900, 0.95)
S.cut(CUT_IN - FR, cam=(PX - 250, 900, 0.95), x=PX - 1350 - 540)
S.set(CUT_IN - FR, "stand", "deadpan", dur=0.0, run=1.0, look=(0.9, 0.0), turn=0.5, lean=0.12)
S.xkeys.append((CUT_IN, HX0 - 540, T_ARR - CUT_IN, "out")); S.x = HX0 - 540
S.camera(CUT_IN, *CAM_P, dur=1.2)
S.set(T_ARR - 0.1, "stand", "deadpan", dur=0.12, ease="snap", stretch=-0.25, look=(0.3, 0.0))
S.set(T_ARR + 0.1, "stand", "deadpan", dur=0.3, ease="back", look=(0.0, 0.0))
S.sfx(T_ARR - 0.1, "skid", 0.05, dur=0.35)
S.set(T_ARR + 0.3, "stand", "deadpan", dur=0.3, look=(-0.6, 0.0))           # looks around: a park
# ---- the rose
dig_pull(T_P1, "offer", look=(0.0, 0.0))
S.set(T_POP1 + 0.4, "offer", "dead_stare", dur=0.3, look=(0.0, 0.0))
S.set(G1A + 0.5, "offer", "dead_stare", dur=0.3, look=(0.8, 0.0))           # she's coming
S.set(G1A + 1.1, "offer", "dead_stare", dur=0.4, look=(0.8, 0.0), turn=0.4, smile=0.25, twitch=0.4)   # a stiff smile
S.set(G1A + 1.9, "offer", "dead_stare", dur=0.5, look=(-0.2, 0.0), turn=0.0, smile=0.25)               # she passes
S.set(G1A + 2.5, "offer", "dead_stare", dur=0.5, look=(-0.9, 0.0), turn=-0.5, smile=0.0)               # gone
S.set(T_PETAL - 0.2, "offer", "dead_stare", dur=0.4, look=(0.0, 0.0), turn=0.0)
S.set(T_LOOKR, "offer", "dead_stare", dur=0.3, look=(0.8, -0.3), turn=0.2)
S.set(T_US1, "offer", "dead_stare", dur=0.3, look=(0.0, 0.0), turn=0.0)
S.blink(T_US1 + 0.35)
L.POSES["toss"] = dict(relb=(650, 700), rhand=(560, 560), rhand_t="open")
S.set(T_TOSS, "toss", "deadpan", dur=0.15, ease="snap", look=(0.0, 0.0))
S.set(T_TOSS + 0.25, "stand", "deadpan", dur=0.25, look=(0.0, 0.0))
S.sfx(T_TOSS, "whoosh", 0.04)
# ---- the boombox
dig_pull(T_P2, "offer", look=(0.3, 0.0))
S.set(T_UP, "boom_up", "deadpan", dur=0.35, ease="back", look=(0.0, 0.0), tilt=0.0)
S.sfx(T_UP + 0.1, "clack", 0.05)
S.set(G2A + 0.6, "boom_up", "dead_stare", dur=0.4, look=(-0.7, 0.0))        # eyes: she's back
S.set(G2B, "boom_up", "dead_stare", dur=0.5, look=(0.7, 0.05), turn=0.2)     # she stops right there
S.set(T_SEE2 + 0.3, "boom_up", "dead_stare", dur=0.6, look=(0.7, 0.05), turn=0.2, brow=0.25, smile=0.15)   # hope
S.set(T_PHONES + 0.3, "boom_up", "dead_stare", dur=0.15, look=(0.7, 0.05), turn=0.2, brow=0.0, smile=0.0)
S.set(G2C + 0.4, "boom_up", "dead_stare", dur=0.6, look=(0.9, 0.05), turn=0.3)
S.set(T_LOWER, "hold_front", "dead_stare", dur=0.5, look=(0.0, 0.0))
S.set(T_SETDN, "crouch", "dead_stare", dur=0.3, look=(-0.4, 0.4))
S.sfx(T_SETDN + 0.25, "thud", 0.04)
# ---- sits. spaghetti.
S.set(T_SIT, "sit_bench", "resigned", dur=0.4, look=(0.0, 0.2))
S.sfx(T_SIT + 0.35, "thud", 0.04)
S.set(T_SIT + 0.9, "sit_bench", "resigned", dur=0.3, look=(0.0, 0.0), squash=0.15)
S.set(T_SIT + 1.2, "sit_bench", "resigned", dur=0.3, look=(0.0, 0.0), squash=0.0)
dig_pull(T_P3, "hold_plate", look=(0.0, 0.7), sitting=True)
S.set(T_POP3 + 0.4, "hold_plate", "deadpan", dur=0.3, look=(0.0, 0.8))
S.set(G3B - 0.2, "hold_plate", "deadpan", dur=0.3, look=(0.0, 0.8), lid=0.4)
S.set(T_SNIFF + 0.2, "hold_plate", "deadpan", dur=0.3, look=(0.8, 0.0), turn=0.2)    # notices her
S.set(G3D + 0.1, "hold_plate", "dead_stare", dur=0.3, look=(0.8, 0.1), turn=0.4)
S.set(T_PLATE, "sit_bench", "dead_stare", dur=0.4, look=(0.6, 0.5), turn=0.4,        # the plate onto the bench between them
      lelb=(510, 1060), lhand=(640, 1205), relb=(660, 1060), rhand=(740, 1210), lhand_t="grip", rhand_t="grip")
S.set(T_PLATE + 0.5, "sit_bench", "dead_stare", dur=0.35, look=(0.8, 0.0), turn=0.6)
# the noodle: both lean in, slurping
KISS_H = dict(head=(642, 768), neck=(588, 882))
NOOD_H = dict(head=(585, 792), neck=(556, 890))
S.set(T_NOOD - 0.2, "sit_bench", "deadpan", dur=0.4, turn=0.9, look=(0.6, 0.6), mouth="o", open=0.25, **NOOD_H)
S.set(T_SLURP0, "sit_bench", "deadpan", dur=0.4, turn=1.0, look=(0.8, 0.0), mouth="o", open=0.2, **NOOD_H)
S.set(T_KISS - 0.05, "sit_bench", "deadpan", dur=T_KISS - T_SLURP0 - 0.45, ease="smooth", turn=1.1, look=(0.9, -0.1), mouth="o",
      open=0.12, tilt=0.12, **KISS_H)
S.set(T_KISS, "sit_bench", "deadpan", dur=0.06, ease="snap", turn=1.1, mouth="kiss", eyes="closed", tilt=0.12, **KISS_H)
S.sfx(T_KISS, "pop", 0.08)
S.set(T_RIGID, "sit_bench", "dead_stare", dur=0.12, ease="snap", turn=0.4, eyescale=1.3, curl_up=1.0, pupil=0.6, look=(0.6, 0.0),
      head=(560, 752), neck=(545, 878), stretch=0.06)
S.sfx(T_RIGID, "boing", 0.04)
S.set(T_RIGID + 0.5, "sit_bench", "dead_stare", dur=1.2, turn=0.3, eyescale=1.2, curl_up=0.8, pupil=0.7, look=(0.6, 0.0), blush=1.0)
S.set(T_HAND + 0.2, "sit_bench", "dead_stare", dur=0.3, turn=0.3, eyescale=1.2, curl_up=0.8, pupil=0.7, look=(0.3, 0.9), blush=1.0)
S.set(T_US2, "sit_bench", "deadpan", dur=0.6, turn=0.0, look=(0.0, 0.0), blush=1.0, mouth="auto", smile=0.35, lid=0.2)
S.set(T_CARD, "sit_bench", "deadpan", dur=0.3, look=(0.7, -0.85), tilt=-0.06, blush=0.7)
def card_scan(tt, p):
    if T_CARD + 0.3 <= tt < T_LOOKG - 0.1:
        u = ((tt - T_CARD - 0.3) / 0.6) % 1.0
        p["look"] = (0.4 + 0.5 * smooth(u), -0.85)
    return p
S.hook(card_scan)
S.set(T_LOOKG, "sit_bench", "dead_stare", dur=0.3, look=(0.9, 0.1), turn=0.5, blush=0.6)
S.set(T_SHADOW + 0.15, "sit_bench", "dead_stare", dur=0.3, look=(0.8, -0.9), turn=0.4, eyescale=1.12, blush=0.4)
S.sfx(T_SHADOW, "whoosh", 0.08, dur=0.9)
S.set(ST_IN1 + 0.2, "sit_bench", "dead_stare", dur=0.4, look=(0.8, -0.3), turn=0.4, blush=0.2)
S.sfx(ST_IN1, "thud", 0.06)
CAM_W = (PX + 600, 860, 0.58)
S.camera(T_SHADOW, *CAM_W, dur=1.4)
# ---- SIGN HERE
S.set(T_STANDUP, "crouch", "dead_stare", dur=0.25, look=(0.8, 0.0))
S.set(T_STANDUP + 0.3, "stand", "dead_stare", dur=0.3, ease="back", look=(0.8, 0.0))
S.walk_to(T_WALK, SIGNX - 540, 0.85)
S.camera(T_WALK, PX + 600, 900, 0.76, 1.0)
S.camera(ST_UP0, PX + 1000, 860, 0.62, 1.2)
S.set(T_SIGN0 - 0.3, "sign", "deadpan", dur=0.3, look=(0.7, 0.4), turn=0.3)
def sign_hook(tt, p):
    if T_SIGN0 <= tt < T_SIGN1:
        u = ramp(tt, T_SIGN0, T_SIGN1, "linear")
        bx, by = board_pos(tt)
        p["rhand"] = (bx - 48 + 130 * u + 10 * math.sin(tt * 40), by + 85 * 0.8 - 30 + 12 * math.sin(tt * 30))
        p["rhand_t"] = "none"
    return p
S.hook(sign_hook)
S.sfx(T_SIGN0, "scribble", 0.06, dur=T_SIGN1 - T_SIGN0)
S.set(T_SIGN1 + 0.1, "stand", "deadpan", dur=0.3, look=(0.7, -0.4), turn=0.3)
S.set(ST_UP0 + 0.1, "stand", "deadpan", dur=0.3, look=(0.7, -0.8), turn=0.3)
S.set(T_POINT, "point_stork", "deadpan", dur=0.2, ease="back", look=(0.7, -0.9), turn=0.3)
S.sfx(T_DROP, "slide_down", 0.04, dur=0.7)
S.set(T_DROP + 0.05, "stand", "deadpan", dur=0.08, ease="snap", eyescale=1.3, curl_up=1.0, look=(0.7, -0.6), turn=0.3)
# the dive: "fly" pose, rotated flat (see dive_hook)
S.set(T_DIVE, "fly", "deadpan", dur=0.15, ease="snap", eyescale=1.25, look=(0.8, 0.4), nowalk=1.0, lag=0.3, turn=0.6)
S.sfx(T_DIVE, "whoosh", 0.08, dur=0.5)
S.set(T_CATCH, "fly", "deadpan", dur=0.08, ease="snap", eyescale=1.2, look=(0.4, 0.6), nowalk=1.0, lag=0.3, turn=0.6, lhand_t="grip", rhand_t="grip")
S.sfx(T_CATCH, "thud", 0.1); S.sfx(T_CATCH + 0.05, "sploosh", 0.08); S.shake(T_CATCH, 0.35, 10)
S.set(T_SLIDE + 0.3, "fly", "dead_stare", dur=0.3, look=(0.0, 0.0), nowalk=1.0, lag=0.3, turn=0.0, lhand_t="grip", rhand_t="grip")
S.blink(T_SLIDE + 0.6)
# ---- CUT: on his feet, holding it
S.cut(CUT2 - FR, cam=(PX + 60, 900, 0.98), x=AFTX - 540)
S.set(CUT2 - FR, "hold_front", "dead_stare", dur=0.0, look=(0.0, 0.8))
S.set(T_CRY + 0.25, "hold_front", "dead_stare", dur=0.12, ease="snap", eyescale=1.15, look=(0.0, 0.8))
S.set(T_CRY + 0.7, "hold_front", "holding_it", dur=0.3, frizz=0.8, sweat=0.5, look=(0.0, 0.0))
S.set(R0, "hold_front", "resigned", dur=0.8, frizz=0.5, sweat=0.3, look=(0.0, 0.75))
S.set(T_ASLEEP + 0.2, "hold_front", "deadpan", dur=0.6, frizz=0.0, look=(0.0, 0.75))
S.set(T_ASLEEP + 0.9, "hold_front", "deadpan", dur=0.4, look=(0.8, 0.0), turn=0.3)          # her: impressed
S.set(T_LEAN + 0.3, "hold_front", "deadpan", dur=0.4, look=(0.6, -0.2), turn=0.3, eyescale=1.1)
S.set(T_SMILE, "hold_front", "happy", dur=0.8, mouth="auto", smile=0.6, lid=0.1, look=(0.0, 0.0), turn=0.0)
S.camera(T_LEAN, PX + 40, 880, 1.08, 1.4)
# ---- the stork again
S.camera(ST2_IN0, PX + 470, 860, 0.72, 1.0)
S.sfx(ST2_IN0, "whoosh", 0.07, dur=0.9); S.sfx(ST2_IN1, "thud", 0.05)
S.set(T_TURN, "hold_front", "deadpan", dur=0.9, smile=0.0, mouth="flat", look=(0.9, -0.2), turn=0.4, eyescale=1.15)
S.set(T_TURN + 1.2, "hold_front", "dead_stare", dur=0.5, look=(0.8, 0.0), turn=0.4, eyescale=1.25, curl_up=0.6)
S.set(T_SHAKE + 0.9, "hold_front", "dead_stare", dur=0.3, look=(0.8, -0.6), turn=0.4, eyescale=1.15)
S.set(T_EXHALE, "hold_front", "deadpan", dur=0.25, squash=0.25, lid=0.5, look=(0.0, 0.0))
S.set(T_EXHALE + 0.35, "hold_front", "deadpan", dur=0.35, squash=0.0, lid=0.3, look=(0.6, 0.2), turn=0.3)
S.sfx(T_EXHALE, "whoosh", 0.03, dur=0.6)
S.set(T_GIVE1, "stand", "deadpan", dur=0.4, look=(0.0, 0.0), turn=0.0, smile=0.25)
S.camera(T_GIVE0, PX + 40, 900, 0.98, 0.8)
S.t = T_ASK
S.the_ask(T_ASK, hold=ASK_HOLD, push=False, keep=dict(mouth="auto", smile=0.25))
S.camera(T_ASK + 6.9, PX + 10, 905, 1.06, 4.0)

# ================================================================ the dive (rotates his whole pose flat, arms forward)
DIVE_ROT = 1.42
def _hands_rel():
    hx = (470 + 620) / 2 - 540; hy = 500 - 1118
    c, s_ = math.cos(DIVE_ROT), math.sin(DIVE_ROT)
    return (hx * c - hy * s_, hx * s_ + hy * c)
HR = _hands_rel()
DIVE_END_HIP = (CP[0] - HR[0], CP[1] - HR[1])
def dive(t):
    """(dx, dy, rot) of his hip relative to standing at SIGNX, or None."""
    if not (T_DIVE <= t < CUT2 - FR): return None
    hip0 = (SIGNX, 1118.0)
    if t < T_CATCH:
        u = ramp(t, T_DIVE, T_CATCH, "linear")
        x = lerp(hip0[0], DIVE_END_HIP[0] - 60, u)
        y = lerp(hip0[1], DIVE_END_HIP[1], u) - 260 * math.sin(math.pi * u)
        rot = DIVE_ROT * smooth(min(1.0, u * 1.6))
        return (x - hip0[0], y - hip0[1], rot)
    u = smooth(ramp(t, T_CATCH, T_SLIDE))
    return (DIVE_END_HIP[0] - 60 + 60 * u - hip0[0], DIVE_END_HIP[1] - hip0[1], DIVE_ROT)
def dive_hook(t, p):
    d = dive(t)
    if d is None: return p
    dx, dy, rot = d
    px, py = p["hip"]
    c, s_ = math.cos(rot), math.sin(rot)
    for j in C.JOINTS:
        x, y = p[j][0] - px, p[j][1] - py
        p[j] = (px + x * c - y * s_ + dx, py + x * s_ + y * c + dy)
    p["tilt"] = p.get("tilt", 0.0) + rot
    return p
S.hook(dive_hook)

# ================================================================ HER (a stick figure like him: long auburn hair, teal dress)
G_HAIR, G_DRESS = (0.62, 0.28, 0.16), (0.30, 0.66, 0.66)
GS = 0.92
L.POSES["g_read"] = dict(lelb=(470, 960), lhand=(510, 885), relb=(610, 960), rhand=(570, 885), lhand_t="grip", rhand_t="grip")
L.POSES["g_sit"] = dict(L.POSES["sit_bench"], head=(540, 740), neck=(540, 862), hip=(540, 1205), lelb=(468, 1060), lhand=(480, 1180), relb=(612, 1060), rhand=(600, 1180))
L.POSES["g_phones"] = dict(lelb=(420, 800), lhand=(430, 660), relb=(660, 800), rhand=(650, 660), lhand_t="open", rhand_t="open")
L.POSES["g_clasp"] = dict(lelb=(470, 930), lhand=(528, 860), relb=(610, 930), rhand=(552, 860))
GX = Track([(0.0, PX + 900, 0),
            (G1A, PX + 900, 0), (G1A, PX - 1150, G1B - G1A, "linear"),
            (G2A, PX - 1150, 0), (G2A, PX + 250, G2B - G2A, "out"),
            (G2C, PX + 1250, G2D - G2C, "inn"),
            (G3A, PX + 1250, 0), (G3A, PX + 520, G3B - G3A, "out"),
            (G3C, GXS, G3D - G3C, "smooth"),
            (CUT2 - FR, GXA, 0.001, "linear"),
            (T_LEAN - 0.1, PX + 150, 0.6, "smooth"), (T_TURN + 0.1, GXA, 0.6, "smooth")])
GW = Track([(0.0, 0.0, 0), (G1A, 1.0, 0.1), (G1B, 0.0, 0.1), (G2A, 1.0, 0.1), (G2B - 0.3, 0.0, 0.35), (G2C, 1.0, 0.2),
            (G2D, 0.0, 0.1), (G3A, 1.0, 0.1), (G3B - 0.3, 0.0, 0.35), (G3C, 1.0, 0.1), (G3D - 0.2, 0.0, 0.2)])
GK = [(0.0, L.pose("g_read", "neutral", turn=-0.8, look=(-0.2, 0.8)), 0)]
def gk(t, body, face, dur=0.3, ease="smooth", **kw): GK.append((t, L.pose(body, face, **kw), dur, ease))
gk(G1A, "g_read", "neutral", dur=0.0, turn=-0.9, look=(-0.2, 0.85), smile=0.25)
gk(G2A, "g_read", "neutral", dur=0.0, turn=0.9, look=(0.2, 0.85), smile=0.25)
gk(G2B - 0.2, "g_read", "neutral", dur=0.4, turn=0.3, look=(0.0, 0.85), smile=0.2)
gk(T_SEE2, "g_read", "neutral", dur=0.5, turn=-0.6, look=(-0.7, -0.5), smile=0.1, brow=0.3)     # over the book, up at him
gk(T_SEE2 + 0.7, "g_read", "neutral", dur=0.3, turn=-0.6, look=(-0.7, -0.5), smile=0.0, brow=0.3, lid=0.25)
gk(T_PHONES, "g_phones", "neutral", dur=0.25, turn=-0.4, look=(-0.6, -0.4), lid=0.3, smile=0.1)
gk(T_PHONES + 0.4, "g_read", "neutral", dur=0.3, turn=0.0, look=(0.0, 0.85), lid=0.2, smile=0.2)
gk(G2C - 0.15, "g_read", "neutral", dur=0.2, turn=0.9, look=(0.2, 0.85), smile=0.25, fx_notes=0.0)
gk(G3A, "g_read", "neutral", dur=0.0, turn=-0.9, look=(-0.2, 0.85), smile=0.2)
gk(T_SNIFF - 0.2, "g_read", "neutral", dur=0.3, turn=-0.5, look=(-0.4, 0.3), tilt=-0.08, brow=0.4, lid=0.3)   # sniff
gk(T_SNIFF + 0.3, "g_read", "surprised", dur=0.2, turn=-0.7, look=(-0.8, 0.5), open=0.2, tilt=0.0)
gk(T_OFF, "g_phones", "happy", dur=0.25, turn=-0.7, look=(-0.8, 0.5))
gk(T_OFF + 0.35, "stand", "happy", dur=0.25, turn=-0.7, look=(-0.8, 0.5))
gk(G3D - 0.25, "crouch", "happy", dur=0.25, turn=-0.7, look=(-0.8, 0.4))
gk(G3D + 0.05, "g_sit", "happy", dur=0.25, ease="back", turn=-0.7, look=(-0.8, 0.4))
gk(T_LOOKH, "g_sit", "happy", dur=0.3, turn=-0.8, look=(-0.6, 0.6), smile=0.5)
gk(T_NOOD - 0.2, "g_sit", "happy", dur=0.4, turn=-0.9, look=(-0.6, 0.6), mouth="o", open=0.25, smile=0.3,
   head=(495, 770), neck=(525, 875))
gk(T_SLURP0, "g_sit", "happy", dur=0.4, turn=-1.0, look=(-0.8, 0.0), mouth="o", open=0.2, smile=0.3, head=(495, 770), neck=(525, 875))
gk(T_KISS - 0.05, "g_sit", "happy", dur=T_KISS - T_SLURP0 - 0.45, turn=-1.1, look=(-0.9, -0.1), mouth="o", open=0.12, tilt=-0.12,
   head=(432, 708), neck=(492, 822))
gk(T_KISS, "g_sit", "happy", dur=0.06, ease="snap", turn=-1.1, mouth="kiss", eyes="closed", tilt=-0.12, head=(432, 708), neck=(492, 822))
gk(T_RIGID + 0.15, "g_sit", "delighted", dur=0.3, turn=-0.7, tilt=0.0, blush=0.5, head=(530, 745), neck=(536, 866))
gk(T_HAND, "g_sit", "happy", dur=0.4, turn=-0.8, look=(-0.7, 0.2), smile=0.7, blush=0.4)
gk(T_LOOKG + 0.2, "g_sit", "happy", dur=0.3, turn=-0.8, look=(-0.8, 0.1), smile=0.5)
gk(T_SHADOW + 0.25, "g_sit", "surprised", dur=0.3, turn=0.4, look=(0.8, -0.9), open=0.3)
gk(ST_IN1 + 0.3, "g_sit", "neutral", dur=0.3, turn=0.6, look=(0.8, -0.3), smile=0.2)
gk(T_SIGN1, "g_sit", "neutral", dur=0.3, turn=0.6, look=(0.8, -0.5), smile=0.2)
gk(T_DROP, "g_sit", "surprised", dur=0.15, ease="snap", turn=0.6, look=(0.8, -0.6), open=0.5, eyescale=1.2)
gk(T_CATCH, "g_sit", "surprised", dur=0.2, turn=0.6, look=(0.9, 0.2), open=0.6, eyescale=1.2)
gk(T_SLIDE + 0.4, "g_sit", "happy", dur=0.3, turn=0.6, look=(0.9, 0.2), smile=0.6, eyes="happy")
gk(CUT2 - FR, "g_clasp", "worried", dur=0.0, turn=-0.7, look=(-0.6, 0.4))
gk(T_ASLEEP + 0.3, "g_clasp", "delighted", dur=0.3, turn=-0.8, look=(-0.6, 0.3), blush=0.0, eyes="happy", smile=0.9, open=0.3)
gk(T_LEAN, "stand", "happy", dur=0.6, turn=-0.8, look=(-0.4, 0.3), eyes="closed", smile=0.6, tilt=-0.28,
   head=(470, 670), neck=(510, 780))
gk(T_TURN + 0.2, "stand", "neutral", dur=0.9, turn=0.5, look=(0.9, -0.2), smile=0.0, eyescale=1.15, tilt=0.0)
gk(T_TURN + 1.25, "stand", "neutral", dur=0.4, turn=-0.3, look=(-0.9, 0.0), smile=0.0, eyescale=1.2)     # at him
gk(T_TURN + 1.75, "stand", "neutral", dur=0.4, turn=0.5, look=(0.9, -0.1), smile=0.0, eyescale=1.15)
gk(T_EXHALE + 0.1, "stand", "happy", dur=0.4, turn=-0.5, look=(-0.7, 0.2), smile=0.5)
gk(T_GIVE0, "hold_front", "happy", dur=0.4, turn=-0.5, look=(-0.6, 0.6), smile=0.6)
gk(T_GIVE1 + 0.3, "hold_front", "happy", dur=0.4, turn=-0.3, look=(0.0, 0.8), smile=0.6)
gk(T_ASK + 3.0, "hold_front", "happy", dur=0.5, turn=-0.4, look=(-0.6, -0.2), smile=0.5)
GKT = Track(GK)

def g_base(t):
    p = dict(GKT.at(t))
    x = GX.at(t); ox = x - 540
    for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1])
    wk = GW.at(t)
    v = (GX.at(t + 0.03) - GX.at(t - 0.03)) / 0.06; d = 1 if v > 1 else (-1 if v < -1 else 0)
    if wk > 0.01:
        ph = t * 2 * math.pi * 1.5
        stride, lift = 52, 30
        hipx, hipy = p["hip"]
        for side, off in (("l", 0.0), ("r", math.pi)):
            s_ = math.sin(ph + off); lf = max(0.0, math.cos(ph + off)) * lift
            foot = (hipx + stride * s_, FLOOR_Y - lf)
            knee = ((hipx + foot[0]) / 2 + d * 22, (hipy + FLOOR_Y) / 2 - lf * 0.6)
            p[side + "foot"] = lerp(p[side + "foot"], foot, wk); p[side + "knee"] = lerp(p[side + "knee"], knee, wk)
        bob = 8 * abs(math.sin(ph)) * wk
        for k in ("head", "neck", "hip", "lelb", "relb", "lhand", "rhand"): p[k] = (p[k][0], p[k][1] + bob)
        if d: p["lfoot_dir"] = p["rfoot_dir"] = 0.9 * d
        p["tilt"] = p.get("tilt", 0.0) + 0.03 * math.sin(ph) * wk
    return p
LAGJ = ("head", "lelb", "relb", "lhand", "rhand")
def g_pose(t):
    p = g_base(t); q = g_base(t - 0.08)
    hp, hq = p["hip"], q["hip"]
    for j in LAGJ:
        p[j] = (hp[0] + 0.65 * (p[j][0] - hp[0]) + 0.35 * (q[j][0] - hq[0]), hp[1] + 0.65 * (p[j][1] - hp[1]) + 0.35 * (q[j][1] - hq[1]))
    # the baby: from him into her arms
    b = baby(t)
    if b and T_GIVE0 <= t:
        e = smooth(ramp(t, T_GIVE0, T_GIVE1))
        for side, (lx, ly) in (("l", (-85, 34)), ("r", (100, 30))):
            p[side + "hand"] = lerp(p[side + "hand"], unscale(p, O.baby_pt(b[0], b[1], b[2], lx, ly)), e); p[side + "hand_t"] = "grip"
    return L.constrain(p)
def foot_c(p): return (p["lfoot"][0] + p["rfoot"][0]) / 2
def scale_pt(p, pt):
    fx = foot_c(p); return (fx + (pt[0] - fx) * GS, FLOOR_Y + (pt[1] - FLOOR_Y) * GS)
def unscale(p, pt):
    fx = foot_c(p); return (fx + (pt[0] - fx) / GS, FLOOR_Y + (pt[1] - FLOOR_Y) / GS)
def g_blink(t):
    for b in (7.6, 14.3, 17.2, 22.0, 24.6, 30.2, 34.9, 42.2, 50.6, 55.4, 59.0):
        if b <= t < b + 0.16: return math.sin(math.pi * (t - b) / 0.16)
    return 0.0
def phones(t):
    if t < T_PHONES: return 0.0
    if t < T_OFF: return smooth(ramp(t, T_PHONES, T_PHONES + 0.3))
    return 1 - smooth(ramp(t, T_OFF, T_OFF + 0.3))
def g_visible(t):
    return (G1A <= t < G1B) or (G2A <= t < G2D) or (t >= G3A)

def her(cr, t, p, ly):
    if ly != "back" or not g_visible(t): return
    q = g_pose(t)
    O.draw_mom(cr, t, q, g_blink(t), s=GS, hair=G_HAIR, dress=G_DRESS, bun=False, phones=phones(t))
    if t < T_OFF + 0.2:                                              # her book
        hx, hy = scale_pt(q, ((q["lhand"][0] + q["rhand"][0]) / 2, (q["lhand"][1] + q["rhand"][1]) / 2))
        if q["lhand_t"] == "grip":
            O.draw_book(cr, hx, hy - 10, s=0.95)
            fq = dict(q)
            cr.save(); fx = foot_c(q); cr.translate(fx, FLOOR_Y); cr.scale(GS, GS); cr.translate(-fx, -FLOOR_Y)
            L.draw_grips(cr, fq); cr.restore()
    if T_PHONES + 0.4 <= t < T_OFF:                                 # her own music, very small
        hx, hy = scale_pt(q, q["head"])
        for k in range(2):
            u = ((t - T_PHONES) * 0.7 + k * 0.5) % 1.0
            O.draw_note(cr, hx + 150 + 40 * u, hy - 60 - 120 * u, s=0.6, alpha=math.sin(math.pi * u) * 0.8, sid=19330 + k)
    if T_SNIFF - 0.2 <= t < T_SNIFF + 0.4:                           # sniff sniff
        hx, hy = scale_pt(q, q["head"])
        for k in range(2):
            u = ramp(t, T_SNIFF - 0.2 + k * 0.25, T_SNIFF + 0.15 + k * 0.25)
            if 0 < u < 1: draw_text(cr, "sniff", hx - 220, hy - 20 - 70 * k, 40, color=(30, 30, 34), alpha=math.sin(math.pi * u))
S.sfx(T_SNIFF - 0.15, "squeak", 0.015); S.sfx(T_SNIFF + 0.1, "squeak", 0.015)
for t0, t1 in ((G1A, G1B), (G2A, G2B - 0.3), (G2C, G2D), (G3A, G3B - 0.3)):
    n = int((t1 - t0) / 0.333)
    for k in range(n): S.sfx(t0 + 0.15 + k * 0.333, "step", 0.02)

# her head + mouth (world) for the noodle and the kiss
def g_mouth(t):
    q = g_pose(t)
    hx, hy = q["head"]; tn = q.get("turn", 0.0)
    return scale_pt(q, (hx + 28 * tn, hy + 62))
def his_mouth_p(p):
    hx, hy = p["head"]; tn = p.get("turn", 0.0)
    return (hx + 28 * tn, hy + 62)

# ================================================================ props
PLATE_BENCH = (PX, FLOOR_Y - 10 - O.BENCH_SEAT - 2)
def plate_pos(t, p):
    """(x, y) of the plate or None."""
    if t < T_POP3: return None
    if t < T_PLATE:
        return ((p["lhand"][0] + p["rhand"][0]) / 2 + 5, (p["lhand"][1] + p["rhand"][1]) / 2 - 5)
    if t < T_PLATE + 0.4:
        hand = ((p["lhand"][0] + p["rhand"][0]) / 2 + 5, (p["lhand"][1] + p["rhand"][1]) / 2 - 5)
        return lerp(hand, PLATE_BENCH, smooth(ramp(t, T_PLATE, T_PLATE + 0.35)))
    return PLATE_BENCH
def props_front(cr, t, p, ly):
    if ly != "front": return
    hx, hy = p["rhand"]
    # the rose (in his hand, then tossed)
    if T_POP1 <= t < T_TOSS + 0.1:
        O.draw_rose(cr, hx + 5, hy - 10, s=0.95, ang=0.35, petals=1.0 if t < T_PETAL else 0.0)
        L.draw_grips(cr, p)
    if T_TOSS + 0.1 <= t < T_TOSS + 1.0:
        u = ramp(t, T_TOSS + 0.1, T_TOSS + 1.0, "linear")
        x0, y0 = S_TOSS0
        O.draw_rose(cr, x0 - 900 * u, y0 - 700 * u + 1100 * u * u, s=0.95, ang=0.35 - 9 * u, petals=0.0)
    if T_PETAL <= t < T_PETAL + 1.2:                                 # the petal falls
        u = ramp(t, T_PETAL, T_PETAL + 1.2, "linear")
        O.draw_petal(cr, PETAL0[0] + 50 * math.sin(u * 9), PETAL0[1] + (FLOOR_Y - 20 - PETAL0[1]) * u, ang=1.2 * math.sin(u * 9))
    if T_PETAL + 1.2 <= t < CUT2:
        O.draw_petal(cr, PETAL0[0], FLOOR_Y - 20, ang=0.0)
    # the boombox
    if T_POP2 <= t < T_SETDN + 0.25:
        if t < T_UP:
            O.draw_boombox(cr, hx + 10, hy - 30, s=0.6)
            L.draw_grips(cr, p)
        else:
            cx = (p["lhand"][0] + p["rhand"][0]) / 2; cy = (p["lhand"][1] + p["rhand"][1]) / 2
            O.draw_boombox(cr, cx, cy - 20, s=0.75, t=t, play=boom_play(t))
            L.draw_grips(cr, p)
    if T_MUS + 0.2 <= t < T_DIE + 0.6:                                 # notes out of it
        cx = (p["lhand"][0] + p["rhand"][0]) / 2; cy = (p["lhand"][1] + p["rhand"][1]) / 2
        for k in range(3):
            u = ((t - T_MUS) * 0.8 + k / 3) % 1.0
            a = math.sin(math.pi * u) * (1 - ramp(t, T_DIE, T_DIE + 0.6))
            O.draw_note(cr, cx - 280 + 560 * (k % 2) + (-1 if k % 2 == 0 else 1) * 60 * u, cy + 30 - 120 * u, s=0.8, alpha=a,
                        double=(k == 1), sid=19340 + k)
    # the plate
    pp = plate_pos(t, p)
    if pp and t < T_PLATE + 0.4:
        steam = 1.0 if t < T_KISS else 1 - ramp(t, T_KISS, T_KISS + 1.0)
        O.draw_spaghetti(cr, pp[0], pp[1], s=0.75, t=t, steam=steam)
        if T_POP3 <= t < T_PLATE + 0.4: L.draw_grips(cr, p)
    if T_POP3 + 0.6 <= t < T_SNIFF + 0.3:                              # the smell drifts right, toward her
        for k in range(3):
            u = ((t - T_POP3) * 0.35 + k / 3) % 1.0
            x0 = PX - 150 + 1100 * u; y0 = 980 - 120 * u
            pts = [(x0 + 60 * j, y0 + 30 * math.sin(u * 8 + j * 1.3)) for j in range(5)]
            sketch_line(cr, pts, 6, sid=19390 + k, amp=0.3, color=(1, 1, 1), alpha=0.85 * math.sin(math.pi * u))
    # the noodle
    if T_NOOD <= t < T_KISS:
        a = his_mouth_p(p); b = g_mouth(t)
        u = smooth(ramp(t, T_SLURP0, T_KISS))
        sag = lerp(PLATE_BENCH[1] - 70 - max(a[1], b[1]), 10, u)
        O.draw_noodle(cr, a, b, sag=sag)
    if T_KISS <= t < T_KISS + 0.5:
        a = his_mouth_p(p)
        L.burst_lines(cr, a[0] + 40, a[1] - 20, (t - T_KISS) / 0.5, r0=50, r1=110, n=8, sid=71)
    # holding hands: their hands on the bench
    # the pen while he signs
    if T_SIGN0 - 0.1 <= t < T_SIGN1 + 0.05:
        L.draw_pen(cr, hx, hy - 18, ang=0.3)
S.prop(props_front)
def _bloom(t):
    p = L.pose_with_follow(t); hx, hy = p["rhand"]
    a = 0.35; bx, by = -2 * 0.95, -185 * 0.95
    return (hx + 5 + bx * math.cos(a) - by * math.sin(a), hy - 10 + bx * math.sin(a) + by * math.cos(a))
class _LazyPt:
    def __init__(self, f): self.f, self.v = f, None
    def __getitem__(self, i):
        if self.v is None: self.v = self.f()
        return self.v[i]
    def __iter__(self): return iter((self[0], self[1]))
S_TOSS0 = _LazyPt(lambda: _bloom(T_TOSS + 0.1))
PETAL0 = _LazyPt(lambda: _bloom(T_PETAL))

def boom_play(t):
    if t < T_MUS: return 0.0
    return 1 - smooth(ramp(t, T_DIE, T_DIE + 0.6))
def boombox_ground(cr, t, p, ly):
    if ly == "back" and T_SETDN + 0.25 <= t:
        O.draw_boombox(cr, PX - 560, FLOOR_Y - 85, s=0.6)
    if ly == "back" and t >= T_PLATE + 0.4:                          # the plate stays on the bench
        O.draw_spaghetti(cr, PLATE_BENCH[0], PLATE_BENCH[1], s=0.75, t=t, steam=1 - ramp(t, T_KISS, T_KISS + 1.0))
S.props.insert(0, boombox_ground)

# ================================================================ the stork
def stork_state(t):
    """dict(x, y, mode, flap, facing, look, nod, bundle, clip, cap_tip, beak) or None."""
    fl = math.sin(t * 2 * math.pi * 2.6)
    if ST_IN0 <= t < ST_IN1:                                          # swoops in from the top right, lands
        u = ramp(t, ST_IN0, ST_IN1)
        x = lerp(PX + 2400, SKX, smooth(u)); y = lerp(-200, SKY, 1 - (1 - u) ** 2)
        mode = "fly" if u < 0.92 else "stand"
        return dict(x=x, y=y, mode=mode, flap=fl * (1 - 0.6 * u), facing=-1, look=0.0, nod=0.0, bundle=True, clip=0.0, cap_tip=0.0, beak=0.0)
    if ST_IN1 <= t < ST_UP0:
        look = 0.6 * smooth(ramp(t, T_SIGN0 - 0.2, T_SIGN0 + 0.2)) * (1 - smooth(ramp(t, T_SIGN1, T_SIGN1 + 0.3)))
        tip = math.sin(math.pi * ramp(t, T_TIP, T_TIP + 0.4)) if T_TIP <= t < T_TIP + 0.4 else 0.0
        clip = smooth(ramp(t, T_CLIP, T_CLIP + 0.3)) * (1 - smooth(ramp(t, T_SIGN1 + 0.2, T_SIGN1 + 0.4)))
        sq = 0.04 * math.sin(math.pi * ramp(t, ST_IN1, ST_IN1 + 0.3)) if t < ST_IN1 + 0.3 else 0.0
        return dict(x=SKX, y=SKY + 600 * sq, mode="stand", flap=0.0, facing=-1, look=look, nod=0.0,
                    bundle=True, clip=clip, cap_tip=tip, beak=0.0)
    if ST_UP0 <= t < ST_UP1 + 1.2:                                    # up, over the fountain; notices; lets go; leaves
        if t < ST_UP1:
            u = ramp(t, ST_UP0, ST_UP1)
            x = lerp(SKX, HOVER[0], smooth(u)); y = lerp(SKY, HOVER[1], smooth(u))
        else:
            u = ramp(t, ST_UP1, ST_UP1 + 1.2)
            x = HOVER[0] + 250 * smooth(ramp(t, T_DROP + 0.2, ST_UP1 + 1.2)) * 3
            y = HOVER[1] - 600 * smooth(ramp(t, T_DROP + 0.2, ST_UP1 + 1.2)) ** 1.5
        look = 0.0
        if T_NOTICE <= t < T_DROP + 0.3: look = 0.5 * smooth(ramp(t, T_NOTICE, T_NOTICE + 0.2))
        return dict(x=x, y=y, mode="fly", flap=fl, facing=-1 if t < T_DROP + 0.25 else 1, look=look, nod=0.0,
                    bundle=t < T_DROP, clip=0.0, cap_tip=0.0, beak=1.0 if T_DROP <= t < T_DROP + 0.3 else 0.0)
    if ST2_IN0 <= t < ST2_UP1:                                        # the second visit
        if t < ST2_IN1:
            u = ramp(t, ST2_IN0, ST2_IN1)
            x = lerp(PX + 2400, SK2X, smooth(u)); y = lerp(-200, SKY, 1 - (1 - u) ** 2)
            return dict(x=x, y=y, mode="fly" if u < 0.92 else "stand", flap=fl * (1 - 0.6 * u), facing=-1, look=0.0, nod=0.0,
                        bundle=True, clip=0.0, cap_tip=0.0, beak=0.0)
        if t < ST2_UP0:
            clip = smooth(ramp(t, T_CLIP2, T_CLIP2 + 0.3))
            look = 1.0 * smooth(ramp(t, T_READC, T_READC + 0.25)) * (1 - smooth(ramp(t, T_SHAKE - 0.2, T_SHAKE)))
            nod = 0.0
            shake = 0.0
            if T_SHAKE <= t < T_SHAKE + 0.7: shake = math.sin((t - T_SHAKE) * 2 * math.pi * 3) * (1 - ramp(t, T_SHAKE, T_SHAKE + 0.7))
            st = dict(x=SK2X, y=SKY, mode="stand", flap=0.0, facing=-1, look=look, nod=nod, bundle=True, clip=clip, cap_tip=0.0, beak=0.0)
            st["shake"] = shake
            return st
        u = ramp(t, ST2_UP0, ST2_UP1)
        x = lerp(SK2X, PX + 2600, u ** 1.5); y = lerp(SKY, -500, smooth(u))
        return dict(x=x, y=y, mode="fly", flap=fl, facing=1, look=0.0, nod=0.0, bundle=True, clip=0.0, cap_tip=0.0, beak=0.0)
    return None
SK2X = PX + 1060.0
HOVER = (CP[0] + 343 * SKS, 330.0)        # so the bundle hangs right over the catch point (see stork_bundle_pt)

def stork_layer(cr, t, p, ly):
    st = stork_state(t)
    if ly == "back" and st:
        sh = st.get("shake", 0.0)
        cr.save()
        if sh:                                                        # head shake: wobble the whole bird a touch
            cr.translate(st["x"], st["y"]); cr.rotate(0.05 * sh); cr.translate(-st["x"], -st["y"])
        O.draw_stork(cr, st["x"], st["y"], s=SKS, t=t, flap=st["flap"], facing=st["facing"], mode=st["mode"], beak=st["beak"],
                     bundle=st["bundle"], look=st["look"], nod=st["nod"], cap_tip=st["cap_tip"])
        cr.restore()
        if st["bundle"]:
            bx, by = O.stork_bundle_pt(st["x"], st["y"], SKS, st["facing"], st["look"], st["nod"])
            O.draw_baby(cr, bx, by, 0.0, dict(eyes="sleep"), t, s=0.85)
        if st["clip"] > 0.01:
            bx, by = board_pos(t)
            O.draw_delivery_board(cr, bx, by, s=0.8 * (0.3 + 0.7 * st["clip"]), ang=0.05,
                                  signed=ramp(t, T_SIGN0, T_SIGN1, "linear") if t < ST2_IN0 else 0.0)
            # the wing tip that holds it
            O.sketch_poly(cr, [(bx + 100, by - 40), (bx + 175, by - 70), (bx + 230, by + 20), (bx + 120, by + 30)], 5, sid=19690,
                          fill=(0.93, 0.94, 0.96), amp=0.3)
    if ly == "back" and T_SHADOW <= t < ST_IN1:                       # its shadow sweeps across the path
        u = ramp(t, T_SHADOW, ST_IN1)
        cr.save(); cr.translate(lerp(PX + 1600, SKX, smooth(u)), FLOOR_Y - 40); cr.scale(1, 0.18)
        cr.arc(0, 0, 260 + 160 * (1 - u), 0, 2 * math.pi); cr.restore(); cr.set_source_rgba(0.2, 0.15, 0.2, 0.25 * math.sin(math.pi * min(1, u * 1.2)))
        cr.fill()
S.prop(her)
S.prop(stork_layer)
def board_pos(t):
    if t < ST2_IN0: return (SKX - 330, 1000.0)
    return (SK2X - 300, 1000.0)

# ================================================================ the baby
def his_spot(t, p=None):
    """cradled in his arms (after the cut), with the rocking sway."""
    s_ = sway(t - 0.12)
    frazzle = smooth(ramp(t, T_CRY + 0.6, T_CRY + 0.8)) * (1 - smooth(ramp(t, R0 - 0.3, R0 + 0.2)))
    x = AFTX + 55 * s_ + 7 * math.sin(t * 15) * frazzle + 10
    y = 990 - 16 * s_ * s_
    return (x, y, 0.2 * s_ + 0.05 * math.sin(t * 15) * frazzle)
def sway(t):
    if t < R0: return 0.0
    a = smooth(ramp(t, R0, R0 + 1.0)) * (1 - smooth(ramp(t, T_LEAN - 0.4, T_LEAN + 0.6)))
    return a * math.sin(2 * math.pi * 0.55 * (t - R0))
def her_spot(t):
    q = g_base(t)
    return (*scale_pt(q, (q["hip"][0] + 10, q["neck"][1] + 190)), 0.0)
def baby(t):
    """(x, y, ang) of the baby when it's NOT on the stork, else None."""
    if t < T_DROP: return None
    if t < T_CATCH:
        r = DROP_FROM[0]
        u = ramp(t, T_DROP, T_CATCH, "linear")
        return (lerp(DROP_FROM[0], CP[0], u), lerp(DROP_FROM[1], CP[1], u * u), 0.3 * u)
    if t < CUT2 - FR:
        d = dive(t)
        hx = SIGNX + d[0] + HR[0]; hy = 1118 + d[1] + HR[1]
        return (hx, hy, 0.3)
    if t < T_GIVE0: return his_spot(t)
    if t < T_GIVE1:
        u = smooth(ramp(t, T_GIVE0, T_GIVE1)); a = his_spot(t); b = her_spot(t)
        return (lerp(a[0], b[0], u), lerp(a[1], b[1], u) - 40 * math.sin(math.pi * u), 0.0)
    return her_spot(t)
_DF = []
def _drop_from():
    if not _DF:
        st = stork_state(T_DROP - 1e-3)
        _DF.append(O.stork_bundle_pt(st["x"], st["y"], SKS, st["facing"], st["look"], st["nod"]))
    return _DF[0]
class _Lazy:
    def __getitem__(self, i): return _drop_from()[i]
DROP_FROM = _Lazy()
def baby_st(t):
    if t < CUT2: return dict(eyes="sleep") if t < T_CATCH + 0.6 else dict(eyes="open", look=(-0.6, -0.4))
    if t < T_CRY - 0.2: return dict(eyes="open", look=(0.0, -1.0))
    if t < T_CRY + 0.1: return dict(eyes="open", look=(0.0, -1.0), cry=0.12)
    if t < T_ASLEEP:
        k = 1 - smooth(ramp(t, R0 + 0.6, T_ASLEEP - 0.5))
        if t >= T_ASLEEP - 0.5: return dict(eyes="open", look=(0.0, -0.6)) if t < T_ASLEEP - 0.25 else dict(eyes="sleep")
        return dict(eyes="cry", cry=smooth(ramp(t, T_CRY + 0.1, T_CRY + 0.3)) * (0.35 + 0.65 * k))
    return dict(eyes="sleep")
def baby_draw(cr, t, p, ly):
    b = baby(t)
    if not b: return
    with_her = t >= T_GIVE1 - 0.3
    if (ly == "back") != with_her: return
    O.draw_baby(cr, b[0], b[1], b[2], baby_st(t), t, s=0.85)
    if ly == "front" and T_CRY <= t < T_ASLEEP - 0.6:
        k = 1 - smooth(ramp(t, R0 + 0.6, T_ASLEEP - 0.7))
        for i in range(3):
            u = ((t - T_CRY) * 0.7 + i / 3) % 1.0
            hx, hy = O.baby_pt(b[0], b[1], b[2], *O.BABY_FACE, s=0.85)
            draw_text(cr, "waah", hx - 30 - 50 * u, hy - 90 - 190 * u, 44 + 22 * u, color=(30, 30, 34),
                      rot=-0.15 + 0.06 * math.sin(t * 20 + i), alpha=math.sin(math.pi * u) * k)
    if ly == "front" and T_ASLEEP + 0.4 <= t < T_TURN:
        for i in range(3):
            u = ((t - T_ASLEEP) * 0.45 + i / 3) % 1.0
            hx, hy = O.baby_pt(b[0], b[1], b[2], *O.BABY_FACE, s=0.85)
            draw_text(cr, "z", hx - 75 - 40 * u, hy - 75 - 130 * u, 32 + 24 * u, color=(30, 30, 34),
                      alpha=math.sin(math.pi * u) * ramp(t, T_ASLEEP + 0.4, T_ASLEEP + 1.0))
    if ly == "front" and T_GIVE1 - 0.3 > t >= CUT2: L.draw_grips(cr, p)
S.prop(baby_draw)
for k in range(3): S.sfx(T_CRY + 0.1 + k * 0.95, "wah", 0.04)
S.sfx(T_ASLEEP - 0.3, "wah", 0.015, dur=0.5)

def splash_layer(cr, t, p, ly):
    if ly != "front": return
    if T_CATCH <= t < T_CATCH + 0.9:                                   # the fountain spray rains on him
        u = ramp(t, T_CATCH, T_CATCH + 0.9, "linear")
        O.draw_splash(cr, FX - 120, FLOOR_Y - 120, u, color=(0.55, 0.78, 0.98), n=12, r=320, sid=17, spread=1.0)
    if T_CATCH <= t < CUT2 - FR:
        for k in range(10):
            u = ((t - T_CATCH) * 1.3 + k / 10) % 1.0
            xx = FX - 600 + 70 * k + 10 * math.sin(k * 3)
            O.draw_droplet(cr, xx, lerp(700, FLOOR_Y - 200, u), 11, color=(0.55, 0.78, 0.98))
S.prop(splash_layer)

# his arms cradling the baby after the cut, + the rocking sway
def cradle_hook(tt, p):
    if not (CUT2 - FR <= tt < T_GIVE1): return p
    e = 1 - smooth(ramp(tt, T_GIVE0 + 0.2, T_GIVE1))
    b = his_spot(tt)
    lh = O.baby_pt(b[0], b[1], b[2], -78 * 0.85, 40 * 0.85); rh = O.baby_pt(b[0], b[1], b[2], 105 * 0.85, 28 * 0.85)
    p["lhand"] = lerp(p["lhand"], lh, e); p["rhand"] = lerp(p["rhand"], rh, e)
    if e > 0.5: p["lhand_t"] = p["rhand_t"] = "grip"
    s_ = sway(tt)
    for k_, a in (("hip", 14), ("neck", 22), ("head", 28), ("lknee", 8), ("rknee", 8)): p[k_] = (p[k_][0] + a * s_, p[k_][1])
    p["tilt"] = p.get("tilt", 0.0) + 0.07 * sway(tt - 0.15)
    return p
S.hook(cradle_hook)

# holding hands on the bench (her hand on his)
def hands_layer(cr, t, p, ly):
    pass

# ================================================================ the song (original: soft e-piano, slows to a stop)
def make_song(path):
    import wave
    SR = 44100
    dur = (T_DIE + 0.7) - T_MUS
    n = int(dur * SR); tt = np.arange(n) / SR
    # tape slowdown at the end: time warps, pitch falls
    td = T_DIE - T_MUS
    warp = np.where(tt < td, tt, td + (tt - td) - 0.5 * ((tt - td) ** 2) / 0.7)
    warp = np.minimum(warp, td + 0.35)
    bpm = 84.0; beat = 60 / bpm
    chords = [(57, 60, 64), (53, 57, 60), (55, 59, 62), (52, 55, 59)]      # Am F G Em  (slow-jam)
    mel = [(0.0, 76, 0.9), (1.0, 74, 0.5), (1.5, 72, 0.5), (2.0, 74, 1.4), (4.0, 72, 0.9), (5.0, 71, 0.5), (5.5, 69, 0.5), (6.0, 71, 1.5)]
    def f(m): return 440.0 * 2 ** ((m - 69) / 12)
    out = np.zeros(n)
    for ci, ch in enumerate(chords):
        t0 = ci * 2 * beat
        for m in ch:
            a = (warp >= t0) * np.exp(-np.maximum(0, warp - t0) / 1.2)
            ph = 2 * np.pi * f(m) * np.maximum(0, warp - t0)
            out += 0.18 * a * (np.sin(ph) + 0.25 * np.sin(2 * ph))
    for b0, m, d in mel:
        t0 = b0 * beat
        a = ((warp >= t0) & (warp < t0 + d * beat + 0.3)) * np.exp(-np.maximum(0, warp - t0) / 0.6)
        ph = 2 * np.pi * f(m) * np.maximum(0, warp - t0) + 0.004 * np.sin(2 * np.pi * 5 * warp)
        out += 0.22 * a * np.sin(ph)
    out *= np.minimum(1, tt / 0.05) * np.clip((dur - tt) / 0.2, 0, 1)
    out /= np.abs(out).max() + 1e-9
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((out * 0.9 * 32767).astype(np.int16).tobytes())
SONG = os.path.join(HERE, "song.wav")
if not os.path.exists(SONG): make_song(SONG)
S.sfx(T_MUS, SONG, 0.06)
S.sfx(T_DIE, "slide_down", 0.015, dur=0.6)

if __name__ == "__main__":
    print(f"end {S.t:.2f}", file=sys.stderr)
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        S.build()
        import cairo
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, L.W, L.H)
        for a in sys.argv[2:]:
            tt = float(a); L.render_frame(tt, surf); surf.write_to_png(f"still_{tt:05.2f}.png")
    else:
        S.render("day017.mp4")
