"""Day 31: IG @panque.4 (2 likes): "Buy a luxury car then go for the goth girls". See BEATS.md.
He scoops up the $999,999,999 off the neon sidewalk, runs out right through a purple fog wall into THE DARK SIDE OF
TOWN, buries a snobby salesman in money for a gold hypercar, drives it to THE CRYPT where three goth girls (ORIGINAL
adult characters, never named) ignore him; car alarm, exhaust flames, the DRESS CODE: ALL BLACK easel, matte black
paint... not enough. He floors it through the cemetery gate into an open grave: KABOOM, a thousand bats. They come
over, the black rose, the group shot, a bat on his curl. The ask in the cemetery.
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
import character as C
from ltcd import Track, ramp, lerp, FLOOR_Y
from ink import smooth, sketch_line, draw_text

FR = 1 / 30
sk_rect, sk_poly, sk_circ, sk_ell = O.sketch_rect, O.sketch_poly, O.sketch_circle, O.sketch_ellipse
INKC = (0.07, 0.07, 0.09)

# ================================================================ places
NX = 9000000.0                       # the neon game city (day 22/23)
DOOR_X = NX - 1150.0; PALM_X = NX - 160.0
HX0 = NX + 360.0                     # where he held the sign on day 23
FOG_N = NX + 1500.0                  # the fog wall at the neon city's right edge
GX = 10000000.0                      # THE DARK SIDE OF TOWN
FOG_G = GX - 1250.0
SPOT1 = GX - 600.0                   # where he stops at the car lot
SAL_X = GX - 280.0                   # the salesman
C0 = GX + 560.0                      # the car on its turntable
C1 = GX + 2700.0                     # parked in front of THE CRYPT
HIM2 = GX + 3480.0                   # him next to the parked car
EASEL_X = GX + 3700.0
G_X = (GX + 3990.0, GX + 4180.0, GX + 4370.0)
CLUB_X0, CLUB_X1 = GX + 3880.0, GX + 4760.0
CDOOR = GX + 4180.0
GATE_X = GX + 4850.0
RAMP_X = GX + 5350.0
GRAVE_X = GX + 6600.0
CAR_END = GRAVE_X - 200.0
MAUS_X = GX + 7150.0
HIM3 = GX + 5930.0                   # him by the wreck
G3_X = (GX + 5710.0, GX + 5500.0, GX + 5290.0)

def cam(x, z, fs=1530):
    """camera centred on world x at zoom z with the floor line at screen y fs."""
    return (x, FLOOR_Y - (fs - 960) / z, z)

# ================================================================ timeline
T_READ = 0.3
T_LOOKDOWN = 2.6
T_SACK = 3.0                                   # POP 5.1
T_CROUCH = 5.4; CUT_FULL = 5.8
T_RUN1 = 6.2; T_HUDOFF = (6.2, 6.8)
CUT_G = 7.6
T_RUN2 = 7.65; T_STOP = 8.6
T_SAL_LOOK = 8.9; T_SAL_TURN = 9.9
T_WALK_P = 10.2; T_POUR0, T_POUR1 = 10.7, 11.7
T_TOSS = 11.9
T_KEYS = 12.3; T_WALK_K = 12.5; T_TAKE = 13.0
T_CLICK = 13.4; T_DOOR0, T_DOOR1 = 13.5, 14.0
CUT_IN = 14.4; T_REV = (14.7, 15.0, 15.3)
T_GO1, T_ARRIVE = 15.6, 17.2
T_DOORUP = 17.4; CUT_OUT = 18.2
T_LEAN = 18.5; T_ALARM0, T_ALARM1 = 19.0, 20.8
T_FOB2 = 21.3; T_FLAMES = (21.6, 22.0, 22.4); T_YAWN = 22.6
T_EASEL = 23.6; T_SELF = 24.3; T_GOLD = 24.9
T_BUCKET = 25.4                                # POP 27.5
T_THROW = 27.9; T_SPLASH0, T_SPLASH1 = 28.1, 28.5
T_GLANCE = 28.9; T_UNGLANCE = 29.6
T_STARE = 29.9
T_LOOKR = 30.3; T_PANR = 30.5
CUT_IN2 = 31.6; T_HEART = (31.7, 32.1, 32.5); T_REV2 = 32.6
T_GO2 = 32.9; T_GATE = 33.25; T_RAMP = 33.6; T_LAND = 34.8
T_BATS0, T_BATS1 = 35.0, 37.0
CUT_WRECK = 37.2
T_GIRLS0, T_GIRLS1 = 37.5, 38.8
T_SEE = 39.0; T_TURNHIM = 39.6
T_ROSE0, T_ROSE1 = 40.0, 40.5; T_TAKE_R = 40.8
T_ALBUM = 41.4; T_LIGHT = 42.0
T_BAT0, T_BAT1 = 42.6, 43.4
T_TEETH = 44.2
T_ASK = 44.8; HOLD = 9.5

# ================================================================ poses
def P(name, **kw): L.POSES[name] = kw
P("drag_sack", relb=(630, 1020), rhand=(660, 1150), lelb=(470, 1000), lhand=(500, 1080))
P("pour", lelb=(560, 880), lhand=(660, 760), relb=(660, 900), rhand=(760, 800), lhand_t="grip", rhand_t="grip")
P("reach_r", relb=(630, 890), rhand=(665, 790), lelb=(470, 1000), lhand=(500, 1080))
P("fob_up", relb=(640, 900), rhand=(700, 820), lelb=(470, 1000), lhand=(500, 1080))
P("lean_car", lelb=(420, 980), lhand=(330, 1060), relb=(620, 1000), rhand=(600, 1080), lhand_t="flat")
P("hold_bucket", relb=(630, 1000), rhand=(650, 1080), lelb=(470, 1000), lhand=(500, 1080))
P("throw_l", relb=(560, 860), rhand=(440, 780), lelb=(450, 900), lhand=(380, 820))
P("take_rose", lelb=(440, 950), lhand=(380, 900), relb=(620, 1000), rhand=(600, 1080))
P("rose_hold", lelb=(450, 1000), lhand=(470, 940), relb=(620, 1000), rhand=(600, 1080))
P("rose_mouth", lelb=(450, 930), lhand=(520, 780), relb=(620, 1000), rhand=(600, 1080))
P("arms_x", **dict(L.POSES["arms_crossed"]))
# others
P("s_snob", relb=(610, 1000), rhand=(600, 1090), lelb=(470, 1000), lhand=(480, 1090))
P("s_keys", lelb=(440, 830), lhand=(400, 700), relb=(610, 1000), rhand=(600, 1090))
P("g_lean", lelb=(470, 1000), lhand=(510, 1080), relb=(610, 1000), rhand=(575, 1080), lean=0.04)
P("g_nails", lelb=(470, 1000), lhand=(510, 1080), relb=(640, 960), rhand=(600, 880))
P("g_parasol", lelb=(470, 1000), lhand=(510, 1080), relb=(650, 950), rhand=(640, 860))
P("g_rose", relb=(470, 950), rhand=(380, 900), lelb=(470, 1000), lhand=(510, 1080))
P("g_cross", **dict(L.POSES["arms_crossed"]))

# ================================================================ scene (him)
S = M.Scene(start_body="stand", start_face="deadpan", x0=HX0 - 540)
S.auto_blinks = True
S.floor = False
S.card("panque.4", "Buy a luxury car then go for the goth girls", "2", t0=0.3)
CAM_A = cam(HX0 - 150, 0.92)
S.camkeys[0] = (0.0, CAM_A, 0); S.cam = CAM_A

# ---------------------------------------------------------------- A: the neon street, the money, the sack
S.read_card(T_READ, react="deadpan", lines=2)
S.set(T_LOOKDOWN, "stand", "deadpan", dur=0.3, look=(0.3, 1.0), tilt=0.06)
S.set(T_LOOKDOWN + 0.35, "stand", "dead_stare", dur=0.2, look=(0.0, 0.0), lid=0.3)

def draw_sack(cr, x, y, s, t, p):
    """neck in his fist at (x, y); the bag hangs below. Empty when pulled, fat after the cut, tilted when pouring."""
    if t >= T_TOSS: return
    full = 0.25 if t < CUT_FULL else (1.0 if t < T_POUR0 else 1.0 - 0.8 * ramp(t, T_POUR0, T_POUR1))
    pouring = T_POUR0 - 0.4 <= t < T_TOSS
    cr.save(); cr.translate(x, y)
    if pouring:
        cr.rotate(-2.3 * ramp(t, T_POUR0 - 0.4, T_POUR0))       # mouth down toward the salesman
    cr.scale(s, s)
    bw, bh = 90 + 90 * full, 160 + 120 * full
    if not pouring and t >= CUT_FULL: bh = min(bh, FLOOR_Y - y - 20)  # rests just above the ground when he drags it
    sk_poly(cr, [(-25, 0), (25, 0), (bw * 0.8, bh * 0.35), (bw, bh * 0.75), (bw * 0.6, bh + 10), (-bw * 0.6, bh + 10),
                 (-bw, bh * 0.75), (-bw * 0.8, bh * 0.35)], 6, sid=31000, fill=(0.80, 0.66, 0.42))
    sketch_line(cr, [(-30, 18), (30, 18)], 7, sid=31001, color=(0.45, 0.30, 0.15))
    draw_text(cr, "$", 0, bh * 0.62, 70 + 50 * full, color=(40, 110, 50))
    cr.restore()
S.pocket_pull(T_SACK, "sack", draw_sack, (0, 0), held=True)
S.set(T_SACK + 2.2, "stand", "deadpan", dur=0.3, look=(0.3, 0.8))
S.set(T_CROUCH, "crouch", "deadpan", dur=0.3, nowalk=1.0, look=(0.3, 0.9))
S.sfx(T_CROUCH + 0.1, "rummage", 0.07)
S.cut(CUT_FULL - FR)
S.set(CUT_FULL - FR, "drag_sack", "dead_stare", dur=0.0, lid=0.35)
S.sfx(CUT_FULL, "thud", 0.12)
S.set(CUT_FULL + 0.15, "drag_sack", "deadpan", dur=0.25, turn=0.6, look=(1.0, 0.0))
S.run_to(T_RUN1, FOG_N + 200 - 540, dur=1.3)
S.camera(T_RUN1 + 0.2, *cam(FOG_N - 200, 0.92), 1.1)
S.sfx(T_RUN1 + 1.0, "whoosh", 0.08)

# ---------------------------------------------------------------- B: the dark side of town - the car lot
CAM_B = cam(GX + 150, 0.62)
S.cut(CUT_G - FR, cam=cam(GX - 700, 0.62), x=FOG_G - 540)
S.set(CUT_G - FR, "drag_sack", "deadpan", dur=0.0, turn=0.6, look=(1.0, 0.0), run=1.0)
S.run_to(T_RUN2, SPOT1 - 540, dur=0.9)
S.camera(T_RUN2 + 0.1, CAM_B[0], CAM_B[1], CAM_B[2], 1.0)
S.set(T_STOP, "drag_sack", "deadpan", dur=0.3, turn=0.5, look=(1.0, -0.2))
S.set(T_SAL_LOOK + 0.3, "drag_sack", "dead_stare", dur=0.3, turn=0.5, look=(1.0, -0.1))
S.set(T_SAL_TURN + 0.3, "drag_sack", "dead_stare", dur=0.2, turn=0.5, look=(1.0, 0.0), lid=0.45)
S.walk_to(T_WALK_P, SPOT1 + 40 - 540, dur=0.3)
S.set(T_POUR0 - 0.4, "pour", "deadpan", dur=0.35, turn=0.5, look=(1.0, 0.4), lid=0.35)
S.sfx(T_POUR0, "rain", 0.10)
S.sfx(T_POUR0 + 0.3, "whoosh", 0.05)
S.set(T_TOSS, "stand", "deadpan", dur=0.25, turn=0.5, look=(1.0, 0.0))
S.sfx(T_TOSS + 0.4, "tap", 0.05)
S.set(T_TAKE - 0.2, "reach_r", "deadpan", dur=0.25, turn=0.5, look=(1.0, -0.3))
S.set(T_TAKE + 0.2, "fob_up", "deadpan", dur=0.25, turn=0.4, look=(0.8, -0.2))
S.set(T_CLICK, "fob_up", "deadpan", dur=0.08, ease="snap", turn=0.5, look=(1.0, 0.0), rhand=(720, 800))
S.sfx(T_CLICK, "boop", 0.06); S.sfx(T_CLICK + 0.15, "boop", 0.06)
S.sfx(T_DOOR0, "whoosh", 0.05)
S.set(T_DOOR1, "stand", "deadpan", dur=0.3, turn=0.4, look=(0.0, 0.0), lid=0.3)
S.cut(CUT_IN - FR, cam=cam(C0 + 150, 0.62), x=C0 - 540)
S.set(CUT_IN - FR, "stand", "deadpan", dur=0.0, show=0.0, nowalk=1.0)
for k, tt in enumerate(T_REV):
    S.sfx(tt, "kaboom", 0.08); S.shake(tt, 0.25, 6 + 3 * k)
S.sfx(T_GO1, "skid", 0.06); S.sfx(T_GO1 + 0.1, "whoosh", 0.12)
S.camera(T_GO1 + 0.15, *cam(C1 + 600, 0.58), T_ARRIVE - T_GO1)
S.sfx(T_ARRIVE - 0.5, "skid", 0.12)

# ---------------------------------------------------------------- C: THE CRYPT
CAM_C = cam(GX + 3640, 0.66, fs=1640)
S.camera(T_ARRIVE + 0.1, CAM_C[0], CAM_C[1], CAM_C[2], 0.8)
S.sfx(T_DOORUP, "slide_up", 0.05)
S.cut(CUT_OUT - FR, x=HIM2 - 540)
S.set(CUT_OUT - FR, "stand", "deadpan", dur=0.0, show=1.0, nowalk=1.0, turn=0.5, look=(1.0, 0.0))
S.set(CUT_OUT + 0.1, "stand", "smug", dur=0.3, turn=0.5, look=(1.0, 0.0))
# attempt 1: leans on the car -> the alarm
S.set(T_LEAN, "lean_car", "smug", dur=0.4, turn=0.4, look=(1.0, 0.0), lean=-0.10)
S.set(T_ALARM0 + 0.1, "lean_car", "shocked", dur=0.1, ease="snap", turn=0.0, look=(-0.6, 0.0), eyescale=1.3, curl_up=1.0, lean=-0.05)
S.set(T_ALARM0 + 0.5, "stand", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lid=0.2)
for k in range(int((T_ALARM1 - T_ALARM0) / 0.3)):
    S.sfx(T_ALARM0 + 0.3 * k, "whine", 0.035)
S.set(T_ALARM1 - 0.35, "fob_up", "dead_stare", dur=0.2, look=(0.0, 0.0), lid=0.4)
S.sfx(T_ALARM1, "boop", 0.06)
S.set(T_ALARM1 + 0.25, "stand", "deadpan", dur=0.3, turn=0.5, look=(1.0, 0.0))
# attempt 2: the engine revs itself, exhaust fireballs
S.set(T_FOB2, "fob_up", "smug", dur=0.2, turn=0.5, look=(1.0, 0.0), rhand=(720, 800))
S.sfx(T_FOB2, "boop", 0.06)
for k, tt in enumerate(T_FLAMES):
    S.sfx(tt, "kaboom", 0.10); S.shake(tt, 0.2, 7)
S.set(T_FLAMES[2] + 0.3, "stand", "smug", dur=0.3, turn=0.6, look=(1.0, 0.0))
S.set(T_YAWN + 0.4, "stand", "dead_stare", dur=0.3, turn=0.6, look=(1.0, 0.0), lid=0.45)
# the easel: DRESS CODE: ALL BLACK -> himself (white) -> the gold car
S.set(T_EASEL, "stand", "deadpan", dur=0.4, turn=0.4, look=(0.7, -0.6))
S.set(T_SELF, "stand", "deadpan", dur=0.35, turn=0.0, look=(0.0, 1.0), tilt=0.1)
S.set(T_GOLD, "stand", "dead_stare", dur=0.35, turn=-0.7, look=(-1.0, 0.3))
S.sfx(T_GOLD + 0.2, "twinkle", 0.05)
S.set(T_GOLD + 0.4, "stand", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lid=0.3)
# the paint
def draw_bucket(cr, x, y, s, t, p):
    if t >= T_SPLASH0 + 0.3: return
    tilt = -1.6 * ramp(t, T_THROW, T_SPLASH0)
    cr.save(); cr.translate(x, y); cr.rotate(tilt); cr.scale(0.8 * s, 0.8 * s)
    sk_poly(cr, [(-80, -160), (80, -160), (65, 30), (-65, 30)], 6, sid=31100, fill=(0.78, 0.78, 0.82))
    sk_ell(cr, 0, -160, 80, 20, 5, sid=31101, fill=(0.06, 0.06, 0.08))
    sk_rect(cr, -62, -110, 62, -30, 4, sid=31102, fill=(0.12, 0.12, 0.14))
    draw_text(cr, "MATTE", 0, -88, 30, color=(255, 255, 255)); draw_text(cr, "BLACK", 0, -52, 30, color=(255, 255, 255))
    cr.arc(0, -170, 95, math.pi * 1.1, math.pi * 1.9); cr.set_source_rgb(*INKC); cr.set_line_width(5); cr.stroke()
    cr.restore()
S.pocket_pull(T_BUCKET, "bucket", draw_bucket, (0, 0), held=True, offset=(0, 40))
S.set(T_BUCKET + 2.2, "hold_bucket", "deadpan", dur=0.3, turn=-0.4, look=(-1.0, 0.2))
S.set(T_THROW - 0.25, "hold_bucket", "concentrating", dur=0.2, turn=-0.6, look=(-1.0, 0.0))
S.set(T_THROW, "throw_l", "concentrating", dur=0.18, ease="snap", turn=-0.6, look=(-1.0, 0.0))
S.sfx(T_SPLASH0, "splat", 0.16); S.sfx(T_SPLASH0 + 0.4, "tap", 0.05)
S.set(T_SPLASH1 + 0.1, "stand", "deadpan", dur=0.3, turn=-0.5, look=(-1.0, 0.0))
S.set(T_GLANCE + 0.2, "stand", "deadpan", dur=0.3, turn=0.6, look=(1.0, 0.0), brow=0.2)
S.set(T_UNGLANCE + 0.3, "stand", "dead_stare", dur=0.3, turn=0.6, look=(1.0, 0.0), lid=0.45)
S.set(T_STARE, "stand", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lid=0.45)
# the cemetery
S.set(T_LOOKR, "stand", "dead_stare", dur=0.6, turn=0.9, look=(1.0, -0.1), lid=0.2)
S.camera(T_PANR, *cam(GX + 6150, 0.45), 0.9)
S.sfx(T_PANR + 0.3, "wind", 0.05)
S.camera(T_PANR + 1.0, *cam(GX + 6150, 0.45), 0.1)
# launch 2
S.cut(CUT_IN2 - FR, cam=cam(C1 + 500, 0.58), x=C1 - 540)
S.set(CUT_IN2 - FR, "stand", "deadpan", dur=0.0, show=0.0, nowalk=1.0)
for tt in T_HEART: S.sfx(tt, "thud", 0.10); S.sfx(tt + 0.14, "thud", 0.06)
S.sfx(T_REV2, "kaboom", 0.10); S.shake(T_REV2, 0.25, 9)
S.sfx(T_GO2, "skid", 0.08)
S.camera(T_GO2 + 0.05, *cam(RAMP_X - 100, 0.55), T_RAMP - T_GO2)
S.sfx(T_GATE, "clack", 0.14); S.sfx(T_GATE + 0.05, "bonk", 0.10); S.shake(T_GATE, 0.3, 12)
S.sfx(T_RAMP, "boing", 0.06)
S.camera(T_RAMP + 0.02, *cam(GRAVE_X - 150, 0.50, fs=1600), T_LAND - T_RAMP)
S.sfx(T_LAND, "kaboom", 0.5); S.shake(T_LAND, 0.9, 30)
for k in range(10): S.sfx(T_BATS0 + 0.18 * k, "flip", 0.04)
S.sfx(T_BATS0 + 0.1, "wind", 0.08)
S.flash(T_BATS0 + 0.5, 0.35, color=(0.85, 0.82, 1.0)); S.sfx(T_BATS0 + 0.5, "thud", 0.12)
# the wreck
CAM_W = cam(HIM3 - 250, 0.62, fs=1640)
S.cut(CUT_WRECK - FR, cam=CAM_W, x=HIM3 - 540)
S.set(CUT_WRECK - FR, "stand", "dead_stare", dur=0.0, show=1.0, nowalk=1.0, turn=0.0, look=(0.0, 0.0), lid=0.35)
S.set(T_GIRLS0 + 0.4, "stand", "dead_stare", dur=0.3, turn=-0.6, look=(-1.0, 0.0), lid=0.3)
S.set(T_TURNHIM + 0.3, "stand", "deadpan", dur=0.25, turn=-0.6, look=(-1.0, 0.0), eyescale=1.1)
S.set(T_TAKE_R - 0.2, "take_rose", "deadpan", dur=0.25, turn=-0.6, look=(-1.0, 0.0))
S.sfx(T_TAKE_R, "tap", 0.05)
S.set(T_TAKE_R + 0.35, "rose_hold", "deadpan", dur=0.3, turn=-0.3, look=(-0.4, 0.5), curl_up=0.6)
S.set(T_ALBUM, "rose_hold", "dead_stare", dur=0.35, turn=0.0, look=(0.0, 0.0), lid=0.35)
S.flash(T_LIGHT, 0.3, color=(0.95, 0.95, 1.0)); S.sfx(T_LIGHT, "kaboom", 0.08)
S.set(T_BAT1 + 0.25, "rose_hold", "dead_stare", dur=0.25, look=(0.0, -1.0), lid=0.2)
S.sfx(T_BAT1, "tap", 0.04)
S.set(T_BAT1 + 0.9, "rose_hold", "dead_stare", dur=0.25, look=(0.0, 0.0), lid=0.35)
S.set(T_TEETH, "rose_mouth", "dead_stare", dur=0.3, look=(0.0, 0.0), lid=0.35)
S.set(T_TEETH + 0.4, "stand", "dead_stare", dur=0.25, look=(0.0, 0.0), lid=0.35)
S.x = HIM3 - 540
S.the_ask(T_ASK, hold=HOLD)
T_END = S.t
S.blink(2.2, 9.3, 16.0, 20.3, 26.0, 33.0, 38.4)

def rose_in_teeth(t): return t >= T_TEETH + 0.3

# ================================================================ other people
class Actor:
    def __init__(self, x0, body="stand", face="neutral", **kw):
        self.K = [(0.0, L.pose(body, face, **kw), 0)]
        self.X = [(0.0, x0, 0)]; self.W = [(0.0, 0.0, 0)]
        self.blinks = []
    def k(self, t, body, face="neutral", dur=0.25, ease="smooth", **kw):
        self.K.append((t, L.pose(body, face, **kw), dur, ease)); return self
    def at(self, t, x):
        self.X.append((t, x, 0.001, "linear")); return self
    def walk(self, t0, t1, x1):
        self.X.append((t0, x1, t1 - t0, "linear"))
        self.W += [(t0, 1.0, 0.08), (t1 - 0.1, 0.0, 0.1)]; return self
    def done(self):
        self.KT, self.XT, self.WT = Track(self.K), Track(self.X), Track(self.W); return self
    def base(self, t):
        p = dict(self.KT.at(t))
        x = self.XT.at(t); ox = x - 540
        for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1])
        wk = self.WT.at(t)
        v = (self.XT.at(t + 0.03) - self.XT.at(t - 0.03)) / 0.06; d = 1 if v > 1 else (-1 if v < -1 else 0)
        if wk > 0.01 and abs(v) > 20:
            ph = t * 2 * math.pi * 1.7
            hipx, hipy = p["hip"]
            for side, off in (("l", 0.0), ("r", math.pi)):
                s_ = math.sin(ph + off); lf = max(0.0, math.cos(ph + off)) * 30
                foot = (hipx + 52 * s_, FLOOR_Y - lf); knee = ((hipx + foot[0]) / 2 + d * 22, (hipy + FLOOR_Y) / 2 - lf * 0.6)
                p[side + "foot"] = lerp(p[side + "foot"], foot, wk); p[side + "knee"] = lerp(p[side + "knee"], knee, wk)
            bob = 8 * abs(math.sin(ph)) * wk
            for k in ("head", "neck", "hip", "lelb", "relb", "lhand", "rhand"): p[k] = (p[k][0], p[k][1] + bob)
            if d: p["lfoot_dir"] = p["rfoot_dir"] = 0.9 * d
        ln = p.get("lean", 0.0)
        if abs(ln) > 1e-4:
            fx_ = (p["lfoot"][0] + p["rfoot"][0]) / 2; c, s_ = math.cos(ln), math.sin(ln)
            for k in L.JOINTS:
                if k in ("lfoot", "rfoot"): continue
                dx, dy = p[k][0] - fx_, p[k][1] - FLOOR_Y
                p[k] = (fx_ + dx * c - dy * s_, FLOOR_Y + dx * s_ + dy * c)
        b = 4 * math.sin(t * 2.2 + x * 0.001)
        for k in ("head", "neck", "lelb", "relb", "lhand", "rhand"): p[k] = (p[k][0], p[k][1] + b)
        return p
    def pose(self, t):
        p = self.base(t); q = self.base(t - 0.08)
        hp, hq = p["hip"], q["hip"]
        for j in ("head", "lelb", "relb", "lhand", "rhand"):
            p[j] = (hp[0] + 0.65 * (p[j][0] - hp[0]) + 0.35 * (q[j][0] - hq[0]), hp[1] + 0.65 * (p[j][1] - hp[1]) + 0.35 * (q[j][1] - hq[1]))
        return L.constrain(p)
    def blink(self, t):
        for b in self.blinks:
            if b <= t < b + 0.16: return math.sin(math.pi * (t - b) / 0.16)
        return 0.0

def foot_c(p): return (p["lfoot"][0] + p["rfoot"][0]) / 2
def scale_pt(p, pt, s):
    fx = foot_c(p); return (fx + (pt[0] - fx) * s, FLOOR_Y + (pt[1] - FLOOR_Y) * s)

# ---------------------------------------------------------------- the salesman (black suit, red tie)
SA = Actor(SAL_X, "s_snob", "bored", turn=-0.3, look=(-0.3, 0.0), lid=0.4)
SA.blinks = [8.2]
SA.k(T_SAL_LOOK, "s_snob", "skeptical", dur=0.3, turn=-0.6, look=(-1.0, 0.9), lid=0.3)       # looks him up...
SA.k(T_SAL_LOOK + 0.5, "s_snob", "skeptical", dur=0.3, turn=-0.6, look=(-1.0, -0.6), lid=0.3)  # ...and down
SA.k(T_SAL_TURN, "s_snob", "smug", dur=0.4, turn=0.9, look=(1.0, -0.3), tilt=-0.12, lid=0.5)  # nose up, turns away
SA.k(T_POUR0 + 0.1, "s_snob", "shocked", dur=0.12, ease="snap", turn=-0.5, look=(-0.8, -1.0), eyescale=1.3)
SA.k(T_POUR1, "s_snob", "dead_stare", dur=0.3, turn=-0.3, look=(-0.5, 0.0), lid=0.3)
SA.k(T_KEYS, "s_keys", "dead_stare", dur=0.25, turn=-0.4, look=(-0.6, 0.0), lid=0.3)
SA.k(T_TAKE + 0.3, "s_keys", "resigned", dur=0.3, turn=-0.4, look=(-0.6, 0.0), lid=0.4)
SA.done()
def pile_h(t): return 760 * smooth(ramp(t, T_POUR0 + 0.1, T_POUR1 + 0.1))
def draw_salesman(cr, t):
    if t < CUT_G - FR or t >= CUT_OUT: return
    q = SA.pose(t)
    h = pile_h(t)
    O.draw_staff(cr, t, q, SA.blink(t), s=1.0, kind="plain", vest=(0.14, 0.14, 0.17))
    if h < 420:                                              # red tie
        nx, ny = q["neck"]
        sk_poly(cr, [(nx - 12, ny + 24), (nx + 12, ny + 24), (nx + 16, ny + 160), (nx, ny + 190), (nx - 16, ny + 160)], 4, sid=31200, fill=(0.85, 0.12, 0.15))
    if h > 5: draw_pile(cr, SAL_X, h, t)
    if t >= T_KEYS:                                          # the fob in his raised hand
        if t < T_TAKE:
            rx, ry = q["lhand"]; draw_fob(cr, rx, ry - 50)
_pr = random.Random(31)
PILE_BILLS = [(_pr.uniform(-1, 1), _pr.uniform(0.05, 0.95), _pr.uniform(-0.6, 0.6)) for _ in range(40)]
def draw_pile(cr, x, h, t):
    w = 220 + 0.12 * h
    pts = [(x - w, FLOOR_Y), (x - w * 0.7, FLOOR_Y - h * 0.55), (x - w * 0.35, FLOOR_Y - h * 0.92), (x, FLOOR_Y - h),
           (x + w * 0.35, FLOOR_Y - h * 0.92), (x + w * 0.7, FLOOR_Y - h * 0.55), (x + w, FLOOR_Y)]
    sk_poly(cr, pts, 6, sid=31210, fill=(0.62, 0.80, 0.55))
    for i, (u, v, a) in enumerate(PILE_BILLS):
        yy = FLOOR_Y - h * v; half = w * (1 - (v ** 1.6)) * 0.85
        O.draw_dollar(cr, x + u * half, yy + 30, s=0.42, ang=a, sid=24150 + (i % 5) * 3)
def draw_fob(cr, x, y, s=1.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    sk_ell(cr, 0, 0, 34, 50, 5, sid=31220, fill=(0.10, 0.10, 0.12))
    sk_circ(cr, 0, -12, 11, 3, sid=31221, fill=(0.9, 0.2, 0.2)); sk_circ(cr, 0, 18, 9, 3, sid=31222, fill=(0.75, 0.75, 0.8))
    cr.arc(0, -62, 16, 0, 2 * math.pi); cr.set_source_rgb(0.8, 0.8, 0.85); cr.set_line_width(5); cr.stroke()
    cr.restore()
def draw_fob_held(cr, x, y, s, t, p):
    if (CUT_IN - FR <= t < CUT_OUT) or t >= T_BUCKET: return
    draw_fob(cr, x, y - 45, 0.9)
S.place("fob", draw_fob_held, (0, 0), t_on=T_TAKE, layer="front", follow="rhand")

# ---------------------------------------------------------------- the goth girls (original characters)
G_HAIR = (0.07, 0.06, 0.09)
G_DRESS = ((0.10, 0.09, 0.12), (0.30, 0.10, 0.34), (0.36, 0.06, 0.12))
G_BUN = (False, True, False)
GS = 0.92
G = []
for i in range(3):
    body = ("g_nails", "g_lean", "g_parasol")[i]
    a = Actor(G_X[i], body, "bored", turn=-0.2 * (i - 1), look=(-0.2, 0.3 if i == 0 else 0.0), lid=0.55)
    G.append(a)
G[0].blinks = [19.6, 25.5, 31.0]; G[1].blinks = [18.9, 24.0, 30.2]; G[2].blinks = [20.4, 27.0, 33.2]
# attempts: nothing. one checks her nails, one yawns, one twirls the parasol.
G[0].k(T_ALARM0 + 0.6, "g_nails", "bored", dur=0.3, look=(0.0, 0.6), lid=0.6)
G[1].k(T_YAWN, "g_lean", "yawning", dur=0.3, lid=0.4)
G[1].k(T_YAWN + 1.0, "g_lean", "bored", dur=0.4, lid=0.55)
G[0].k(T_GLANCE, "g_nails", "bored", dur=0.25, turn=-0.5, look=(-1.0, 0.1), lid=0.45)     # the glance at the black car...
G[0].k(T_UNGLANCE, "g_nails", "bored", dur=0.3, turn=0.0, look=(0.0, 0.6), lid=0.6)       # ...back to her nails
# after the crash: they come over (cut), stare at the wreck, then at him
for i in range(3):
    a = G[i]
    a.at(CUT_WRECK - FR, G3_X[i] - 420)
    a.k(CUT_WRECK - FR, "g_parasol" if i == 2 else "stand", "bored", dur=0.0, turn=0.8, look=(1.0, 0.0), lid=0.5)
    a.walk(T_GIRLS0 + 0.12 * i, T_GIRLS1 + 0.12 * i, G3_X[i])
    a.k(T_SEE + 0.1 * i, "g_parasol" if i == 2 else "stand", "dead_stare", dur=0.3, turn=0.7, look=(1.0, -0.6), lid=0.1, eyescale=1.15)
    a.k(T_TURNHIM + 0.1 * i, "g_parasol" if i == 2 else "stand", "dead_stare", dur=0.35, turn=0.7, look=(1.0, 0.0), lid=0.2, eyescale=1.1)
G[0].k(T_ROSE0, "g_rose", "dead_stare", dur=0.35, turn=0.6, look=(1.0, 0.0), lid=0.25)
G[0].k(T_TAKE_R + 0.3, "stand", "dead_stare", dur=0.3, turn=0.5, look=(1.0, 0.0), lid=0.3)
for i in range(3):
    G[i].k(T_ALBUM + 0.1 * i, "g_parasol" if i == 2 else "g_cross", "dead_stare", dur=0.35, turn=0.0, look=(0.0, 0.0), lid=0.35)
for a in G: a.done()

def draw_black_rose(cr, x, y, s=1.0, ang=0.0, sid=31300):
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_line(cr, [(0, 110), (4, 0), (-2, -150)], 7, sid=sid, amp=0.3, color=(0.18, 0.32, 0.20))
    sk_poly(cr, [(2, -40), (50, -70), (70, -40), (30, -30)], 4, sid=sid + 1, fill=(0.22, 0.40, 0.24), amp=0.3)
    sk_circ(cr, -2, -185, 46, 6, sid=sid + 2, fill=(0.10, 0.08, 0.12))
    sketch_line(cr, [(-26, -190), (-6, -205), (16, -185), (-2, -170), (-12, -186)], 4, sid=sid + 3, amp=0.3, color=(0.45, 0.40, 0.50))
    cr.restore()

def draw_parasol(cr, x, y):
    """a black lace parasol held at (x, y), canopy above her head."""
    sketch_line(cr, [(x, y + 40), (x - 10, y - 330)], 7, sid=31310)
    cx, cy = x - 10, y - 330
    pts = [(cx - 230, cy + 60)]
    for k in range(7):
        a0 = math.pi + k * math.pi / 6
        pts.append((cx + 230 * math.cos(a0 + math.pi / 12), cy + 140 * math.sin(a0 + math.pi / 12) * 0.9))
    pts.append((cx + 230, cy + 60))
    sk_poly(cr, pts, 6, sid=31311, fill=(0.08, 0.07, 0.10))
    for k in range(6):                                         # the lace scallops
        sx = cx - 230 + 460 * (k + 0.5) / 6
        cr.arc(sx, cy + 60, 38, 0, math.pi); cr.set_source_rgb(0.08, 0.07, 0.10); cr.fill_preserve()
        cr.set_source_rgb(*INKC); cr.set_line_width(4); cr.stroke()

def draw_girl(cr, t, i):
    a = G[i]; q = a.pose(t)
    O.draw_mom(cr, t, q, a.blink(t), s=GS, hair=G_HAIR, dress=G_DRESS[i], bun=G_BUN[i])
    nx, ny = scale_pt(q, q["neck"], GS)
    sketch_line(cr, [(nx - 40, ny - 4), (nx + 40, ny - 4)], 9, sid=31320 + i, color=(0.05, 0.05, 0.07))     # choker
    if i == 2:
        rh = scale_pt(q, q["rhand"], GS); draw_parasol(cr, rh[0], rh[1])
    if i == 0 and T_ROSE0 <= t < T_TAKE_R:
        rh = scale_pt(q, q["rhand"], GS); draw_black_rose(cr, rh[0], rh[1] + 10, s=1.0, ang=-0.4)
    cr.save(); fx = foot_c(q); cr.translate(fx, FLOOR_Y); cr.scale(GS, GS); cr.translate(-fx, -FLOOR_Y); L.draw_grips(cr, q); cr.restore()
def girls_on(t): return CUT_IN - FR <= t < T_PANR + 1.2 or t >= CUT_WRECK - FR or (CUT_IN2 - FR <= t < T_RAMP + 0.3)

# ================================================================ the car
GOLD = (0.96, 0.76, 0.22); MATTE = (0.13, 0.12, 0.15)
def car_color(t, lx):
    """the paint: a black wave sweeps the car right->left (from his throw) during the splash."""
    if t < T_SPLASH0: return GOLD
    if t >= T_SPLASH1: return MATTE
    edge = 600 - 1200 * ramp(t, T_SPLASH0, T_SPLASH1)
    return MATTE if lx > edge else GOLD

CS = 1.15
def draw_hyper(cr, x, yb, ang=0.0, t=0.0, door=0.0, spin=0.0, lights=0.0, sid=31400):
    """a low wedge hypercar facing right. (x, yb) = ground under its middle. Rotates about (x, yb-200)."""
    cr.save(); cr.translate(x, yb - 200 * CS); cr.rotate(ang); cr.translate(0, 200 * CS); cr.scale(CS, CS)
    painted = T_SPLASH0 <= t < T_SPLASH1
    body = [(-560, -100), (-575, -250), (-470, -300), (-250, -330), (-90, -370), (150, -300), (420, -215), (570, -150),
            (580, -95), (520, -70), (-500, -70)]
    if painted:
        edge = 600 - 1200 * ramp(t, T_SPLASH0, T_SPLASH1)
        sk_poly(cr, body, 7, sid=sid, fill=GOLD)
        cr.save(); cr.rectangle(edge, -600, 1200, 800); cr.clip(); sk_poly(cr, body, 7, sid=sid, fill=MATTE); cr.restore()
    else:
        sk_poly(cr, body, 7, sid=sid, fill=car_color(t, 0))
    dark = car_color(t, 0) == MATTE and not painted
    if t < T_GO1:                                                    # the price sticker in the window
        sk_rect(cr, -230, -330, -40, -268, 3, sid=sid + 30, fill=(1, 1, 1))
        draw_text(cr, "$3,000,000", -135, -299, 30, color=(20, 20, 20))
    # spoiler
    sk_poly(cr, [(-560, -270), (-610, -360), (-430, -360), (-470, -300)], 5, sid=sid + 1, fill=car_color(t, -500))
    # the side window (tinted) + side intake
    sk_poly(cr, [(-280, -300), (-110, -345), (120, -290), (-280, -265)], 5, sid=sid + 2, fill=(0.10, 0.10, 0.16))
    sketch_line(cr, [(-200, -300), (-120, -330)], 5, sid=sid + 3, color=(1, 1, 1), alpha=0.35)
    sk_poly(cr, [(-430, -220), (-300, -215), (-320, -150), (-440, -160)], 4, sid=sid + 4, fill=(0.08, 0.08, 0.10))
    # the scissor door (hinged at the front, swings up)
    door_pts = [(-260, -262), (120, -285), (180, -220), (160, -110), (-240, -110)]
    if door > 0.01:
        sk_poly(cr, [(-260, -262), (120, -285), (160, -110), (-240, -110)], 5, sid=sid + 5, fill=(0.05, 0.05, 0.07))
        cr.save(); cr.translate(170, -200); cr.rotate(1.45 * door); cr.translate(-170, 200)
        sk_poly(cr, door_pts, 6, sid=sid + 6, fill=car_color(t, 0))
        sk_poly(cr, [(-240, -255), (100, -278), (130, -230), (-240, -225)], 4, sid=sid + 7, fill=(0.10, 0.10, 0.16))
        cr.restore()
    else:
        sketch_line(cr, [(-250, -260), (-240, -110), (160, -110), (175, -230)], 4, sid=sid + 8, color=(0.25, 0.20, 0.10) if not dark else (0.35, 0.35, 0.38))
    # lights
    hl = (1.0, 0.97, 0.75) if lights < 0.5 else (1.0, 1.0, 1.0)
    sk_poly(cr, [(470, -190), (560, -150), (545, -135), (460, -170)], 4, sid=sid + 9, fill=hl)
    sk_rect(cr, -585, -240, -560, -200, 3, sid=sid + 10, fill=(0.95, 0.15, 0.15) if lights < 0.5 else (1.0, 0.6, 0.6))
    if lights > 0.5:
        for (lx, ly) in ((540, -160), (-575, -220)):
            cr.arc(lx, ly, 120, 0, 2 * math.pi); cr.set_source_rgba(1.0, 0.9, 0.5, 0.35); cr.fill()
    if not dark and not painted:                                  # shine
        sketch_line(cr, [(-420, -270), (-300, -295)], 6, sid=sid + 11, color=(1, 1, 1), alpha=0.7)
        sketch_line(cr, [(200, -265), (380, -205)], 6, sid=sid + 12, color=(1, 1, 1), alpha=0.7)
    for k, wx in enumerate((-350, 345)):
        sk_circ(cr, wx, -85, 88, 6, sid=sid + 13 + k, fill=(0.08, 0.08, 0.09))
        sk_circ(cr, wx, -85, 50, 4, sid=sid + 15 + k, fill=GOLD if not dark else (0.25, 0.25, 0.28))
        for j in range(5):
            a = spin + j * 1.2566
            sketch_line(cr, [(wx, -85), (wx + 44 * math.cos(a), -85 + 44 * math.sin(a))], 4, sid=sid + 17 + j, amp=0.2)
    cr.restore()

def car_state(t):
    """(x, pivot lift, angle, spin) of the car."""
    if t < T_GO1: return C0, 0.0, 0.0, 0.0
    if t < T_ARRIVE:
        u = ramp(t, T_GO1, T_ARRIVE)
        uu = smooth(u)
        return lerp(C0, C1, uu), 0.0, -0.05 * math.sin(math.pi * min(1, u * 2)) + 0.06 * math.sin(math.pi * max(0, u * 2 - 1)), -40 * u
    if t < T_GO2: return C1, 0.0, 0.0, 0.0
    if t < T_RAMP:
        u = ramp(t, T_GO2, T_RAMP, "linear")
        return lerp(C1, RAMP_X, u * u), 0.0, -0.06 * u, -30 * u * u
    if t < T_LAND:
        u = ramp(t, T_RAMP, T_LAND, "linear")
        x = lerp(RAMP_X, CAR_END, u)
        lift = -520 * 4 * u * (1 - u) - 236 * u
        ang = lerp(-0.35, 1.15 + 2 * math.pi, u ** 1.15)
        return x, lift, ang, -30 - 20 * u
    return CAR_END, -236.0, 1.15, -50 - 12 * (t - T_LAND)

def door_amt(t):
    if t < T_DOOR0: return 0.0
    if t < CUT_IN - FR: return smooth(ramp(t, T_DOOR0, T_DOOR1))
    if t < T_DOORUP: return 0.0
    if t < CUT_OUT - FR: return smooth(ramp(t, T_DOORUP, CUT_OUT - 0.1))
    return 0.0
def lights_on(t):
    if T_CLICK <= t < T_CLICK + 0.45: return 1.0 if int((t - T_CLICK) / 0.12) % 2 == 0 else 0.0
    if T_ALARM0 <= t < T_ALARM1: return 1.0 if int((t - T_ALARM0) / 0.15) % 2 == 0 else 0.0
    return 0.0

def draw_flame(cr, x, y, u, s=1.0, sid=31500):
    """an exhaust fireball shooting left from (x, y); u 0..1 life."""
    if u <= 0 or u >= 1: return
    L_ = 420 * s * math.sin(math.pi * min(1, u * 1.6)) ** 0.6
    r = 90 * s * (1 - 0.5 * u)
    for k, (col, f) in enumerate((((0.98, 0.45, 0.12), 1.0), ((1.0, 0.80, 0.25), 0.7), ((1.0, 0.97, 0.75), 0.4))):
        pts = [(x, y - r * f * 0.6)]
        for j in range(9):
            a = math.pi / 2 + j * math.pi / 8
            pts.append((x - L_ * f + r * f * math.cos(a) - (25 * math.sin(j * 2.3 + u * 20) if j % 2 else 0), y + r * f * math.sin(a)))
        pts.append((x, y + r * f * 0.6))
        sk_poly(cr, pts, 4, sid=sid + k, fill=col, amp=0.8)

def draw_car_all(cr, t):
    if t < CUT_G - FR: return
    x, lift, ang, spin = car_state(t)
    yb = FLOOR_Y + lift
    landed = t >= T_LAND
    if landed:
        cr.save(); cr.rectangle(x - 3000, -6000, 6000, 6000 + FLOOR_Y + 4); cr.clip()
    draw_hyper(cr, x, yb, ang, t, door=door_amt(t), spin=spin * 3, lights=lights_on(t))
    if landed:
        cr.restore()
        sk_poly(cr, [(GRAVE_X - 230, FLOOR_Y + 6), (GRAVE_X - 160, FLOOR_Y - 40), (GRAVE_X + 170, FLOOR_Y - 45), (GRAVE_X + 260, FLOOR_Y + 6)],
                5, sid=31520, fill=(0.33, 0.24, 0.18))
    # exhaust fireballs (rear of the car, x-575)
    rx, ry = x - 590 * CS, yb - 120 * CS
    for tt in T_REV + T_FLAMES + (T_REV2,):
        if tt <= t < tt + 0.45 and not landed and t < T_RAMP:
            draw_flame(cr, rx, ry, (t - tt) / 0.45, s=1.0 + (0.4 if tt in T_FLAMES else 0.0))
    # skid smoke
    for t0, x0 in ((T_GO1, C0 - 350), (T_ARRIVE - 0.4, C1 - 250), (T_GO2, C1 - 350)):
        if t0 <= t < t0 + 1.6:
            for k in range(5):
                u = (t - t0) * 1.2 + k * 0.12
                if u < 1.5: O.draw_smoke_puff(cr, x0 + 110 * k, FLOOR_Y - 60 - 40 * u, 60 + 70 * u, alpha=max(0.0, 0.8 - 0.55 * u))
    # speed lines on the drives
    for (a, b) in ((T_GO1 + 0.1, T_ARRIVE - 0.3), (T_GO2 + 0.15, T_RAMP)):
        if a <= t < b:
            for k in range(7):
                yy = yb - 60 - 45 * k
                sketch_line(cr, [(x - 650 - 200 * (k % 3), yy), (x - 1300 - 150 * (k % 2), yy)], 5, sid=31530 + k, amp=0.3, alpha=0.6)
    # the crash: boom + smoke + flames out of the grave
    if t >= T_LAND:
        u = t - T_LAND
        if u < 0.9:
            O.draw_boom(cr, GRAVE_X, FLOOR_Y - 250, 300 + 900 * min(1, u / 0.25), t=t, sid=31540, alpha=max(0.0, 1 - max(0, u - 0.5) / 0.4))
        for k in range(6):
            uu = ((t - T_LAND) * 0.35 + k / 6) % 1.0
            O.draw_smoke_puff(cr, GRAVE_X - 120 + 60 * math.sin(k * 1.7), FLOOR_Y - 150 - 900 * uu, 70 + 160 * uu, alpha=0.55 * (1 - uu), dark=0.6)

# ---- the paint splash flying from his bucket to the car
def draw_splash(cr, t, p):
    if not (T_THROW + 0.1 <= t < T_SPLASH1 + 0.25): return
    u = ramp(t, T_THROW + 0.1, T_SPLASH1)
    hx, hy = p["rhand"]
    tx = C1 + 500 - 1100 * u
    for k in range(8):
        f = k / 7
        x = lerp(hx - 40, tx, f); y = lerp(hy - 80, FLOOR_Y - 330 + 60 * math.sin(k), f) - 220 * math.sin(math.pi * f) * (1 - u)
        r = 55 + 50 * math.sin(math.pi * f)
        sk_circ(cr, x, y, r * (1 - 0.6 * ramp(t, T_SPLASH1, T_SPLASH1 + 0.25)), 4, sid=31560 + k, fill=MATTE)
def draw_bucket_floor(cr, x, y, s, t, p):
    cr.save(); cr.translate(x, y); cr.rotate(1.57); cr.scale(0.8, 0.8)
    sk_poly(cr, [(-80, -160), (80, -160), (65, 30), (-65, 30)], 6, sid=31100, fill=(0.78, 0.78, 0.82))
    sk_ell(cr, 0, -160, 80, 20, 5, sid=31101, fill=(0.06, 0.06, 0.08))
    cr.restore()
    sk_ell(cr, x - 210, FLOOR_Y - 4, 120, 18, 3, sid=31570, fill=MATTE)
S.place("bucket_floor", draw_bucket_floor, (HIM2 - 160, FLOOR_Y - 70), t_on=T_SPLASH0 + 0.3, layer="back")
S.hide("bucket_floor", CUT_IN2)

# ---- the empty sack, tossed
def draw_sack_floor(cr, x, y, s, t, p):
    if t < T_TOSS + 0.4:
        u = ramp(t, T_TOSS, T_TOSS + 0.4)
        x = lerp(p["rhand"][0], x, u); y = lerp(p["rhand"][1], y, u) - 160 * math.sin(math.pi * u)
    sk_poly(cr, [(x - 90, y), (x + 90, y), (x + 70, y - 50), (x - 60, y - 60)], 5, sid=31010, fill=(0.80, 0.66, 0.42))
S.place("sack_floor", draw_sack_floor, (SPOT1 - 120, FLOOR_Y - 6), t_on=T_TOSS, layer="back")
S.hide("sack_floor", CUT_IN)

# ---- the money stream while pouring
def draw_stream_money(cr, t, p):
    if not (T_POUR0 <= t < T_POUR1 + 0.3): return
    hx, hy = p["rhand"]
    for k in range(16):
        u = ((t - T_POUR0) * 2.2 + k / 16) % 1.0
        if t - T_POUR0 < u / 2.2: continue
        x = lerp(hx + 60, SAL_X + 40 * math.sin(k * 2.1), u); y = lerp(hy + 40, FLOOR_Y - pile_h(t) - 40, u * u)
        O.draw_dollar(cr, x, y, s=0.45, ang=3 * u + k, sid=24150 + (k % 5) * 3)

# ================================================================ bats
_br = random.Random(77)
BATS = [(_br.uniform(0, 0.8), _br.uniform(-2.6, -0.5), _br.uniform(500, 1300), _br.uniform(0, 6.28), _br.uniform(0.5, 1.0)) for _ in range(70)]
def draw_bat(cr, x, y, s=1.0, flap=0.0, sid=31600, hang=False):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    if hang: cr.rotate(math.pi)
    w = 0.35 + 0.65 * abs(math.sin(flap))
    up = -40 * math.sin(flap)
    for d in (-1, 1):
        pts = [(0, -6), (d * 50, up - 20), (d * 110 * w, up - 30), (d * 150 * w, up + 5), (d * 115 * w, up - 2), (d * 95 * w, up + 18),
               (d * 65 * w, up + 4), (d * 45, up + 22), (d * 18, 14)]
        sk_poly(cr, pts, 4, sid=sid + (d > 0), fill=(0.08, 0.07, 0.10), amp=0.6)
    sk_ell(cr, 0, 4, 24, 32, 4, sid=sid + 2, fill=(0.08, 0.07, 0.10))
    sk_poly(cr, [(-18, -18), (-14, -44), (-4, -24)], 3, sid=sid + 3, fill=(0.08, 0.07, 0.10))
    sk_poly(cr, [(18, -18), (14, -44), (4, -24)], 3, sid=sid + 4, fill=(0.08, 0.07, 0.10))
    for d in (-1, 1):
        cr.arc(d * 9, -6, 4.5, 0, 2 * math.pi); cr.set_source_rgb(1.0, 0.95, 0.6); cr.fill()
    cr.restore()
def draw_bats(cr, t):
    if not (T_BATS0 <= t < T_BATS1 + 0.5): return
    ox, oy = MAUS_X, FLOOR_Y - 300
    for i, (d0, a, sp, ph, sc) in enumerate(BATS):
        tt = t - T_BATS0 - d0
        if tt < 0: continue
        x = ox + math.cos(a) * sp * tt * 1.4 - 900 * tt * tt * 0.4
        y = oy + math.sin(a) * sp * tt * 0.9 + 60 * math.sin(tt * 7 + ph)
        s = sc * (0.5 + 2.2 * tt)
        if s > 6: continue
        draw_bat(cr, x, y, s, flap=t * 22 + ph, sid=31600 + (i % 4) * 5)

def draw_curl_bat(cr, t, p):
    if t < T_BAT0: return
    hx, hy = p["head"]; tl = p.get("tilt", 0.0)
    tipx, tipy = hx + 8 + math.sin(tl) * 200, hy - C.HEAD_R - 92
    if t < T_BAT1:
        u = ramp(t, T_BAT0, T_BAT1)
        x = lerp(tipx + 500, tipx, smooth(u)) + 60 * math.sin(u * 9); y = lerp(tipy - 600, tipy, smooth(u))
        draw_bat(cr, x, y + 60, 0.85, flap=t * 20, sid=31650)
    else:
        sw = 0.12 * math.sin((t - T_BAT1) * 3) * math.exp(-(t - T_BAT1) * 0.6)
        cr.save(); cr.translate(tipx, tipy); cr.rotate(sw)
        sketch_line(cr, [(-6, 0), (6, 0)], 4, sid=31660)
        draw_bat(cr, 0, 60, 0.85, flap=math.pi / 2 * 0.0 + 0.15, sid=31650, hang=True)
        cr.restore()

def draw_rose_his(cr, t, p):
    if t < T_TAKE_R: return
    if rose_in_teeth(t):
        hx, hy = p["head"]; tn = p.get("turn", 0.0)
        mx, my = hx + 20 * tn, hy + 62
        cr.save(); cr.translate(mx, my); cr.rotate(-1.45)
        draw_black_rose(cr, 0, 0, s=0.55, ang=0.0)
        cr.restore()
        return
    lx, ly = p["lhand"]
    draw_black_rose(cr, lx, ly + 20, s=1.0, ang=-0.25)

# ================================================================ the neon city (day 22/23, unchanged) + its money
SKY = [(-3000, (0.30, 0.16, 0.45)), (-200, (0.55, 0.22, 0.58)), (300, (0.88, 0.36, 0.55)), (650, (0.98, 0.55, 0.45)), (850, (1.0, 0.72, 0.42))]
HORIZON = FLOOR_Y - 430
_r = random.Random(22)
BILLS = []
for i in range(46):
    x = NX - 500 + _r.uniform(0, 1500); _r.uniform(0, 1)
    _r.uniform(1.1, 1.6); _r.uniform(0, 6.28)
    BILLS.append((x, FLOOR_Y + _r.uniform(-10, 60), _r.uniform(-0.5, 0.5)))
def neon(cr, t):
    x0, x1 = NX - 4000, NX + 4000
    for i, (y, c) in enumerate(SKY):
        y1 = SKY[i + 1][0] if i + 1 < len(SKY) else HORIZON
        cr.rectangle(x0, y, x1 - x0, y1 - y + 1); cr.set_source_rgb(*c); cr.fill()
    sx, sy, r = NX + 520, HORIZON, 330
    cr.save(); cr.arc(sx, sy, r, math.pi, 2 * math.pi); cr.close_path(); cr.clip()
    cr.rectangle(sx - r, sy - r, 2 * r, r); cr.set_source_rgb(1.0, 0.86, 0.35); cr.fill()
    for k in range(5):
        yy = sy - 40 - 52 * k; hgt = 16 - 3 * k
        cr.rectangle(sx - r, yy, 2 * r, hgt); cr.set_source_rgb(0.98, 0.55, 0.45); cr.fill()
    cr.restore()
    cr.rectangle(x0, HORIZON, x1 - x0, 160); cr.set_source_rgb(0.20, 0.62, 0.72); cr.fill()
    for k in range(6):
        yy = HORIZON + 20 + 24 * k
        sketch_line(cr, [(sx - 260 + 30 * k, yy), (sx + 260 - 30 * k, yy)], 4, sid=22400 + k, color=(1.0, 0.85, 0.5))
    cr.rectangle(x0, HORIZON + 160, x1 - x0, 110); cr.set_source_rgb(0.98, 0.88, 0.66); cr.fill()
    cr.rectangle(x0, HORIZON + 270, x1 - x0, FLOOR_Y - HORIZON - 270 + 1); cr.set_source_rgb(0.86, 0.82, 0.86); cr.fill()
    cr.rectangle(x0, FLOOR_Y, x1 - x0, 900); cr.set_source_rgb(0.24, 0.22, 0.30); cr.fill()
    for k in range(-12, 12):
        cr.rectangle(NX + 360 * k, FLOOR_Y + 160, 180, 18); cr.set_source_rgb(1.0, 0.85, 0.3); cr.fill()
    cr.rectangle(x0, FLOOR_Y - 6, x1 - x0, 14); cr.set_source_rgb(0.98, 0.45, 0.70); cr.fill()
    sketch_line(cr, [(x0, FLOOR_Y), (x1, FLOOR_Y)], 6, sid=22410, amp=0.3)
    for k, px in enumerate((NX - 900, NX - 380, NX + 1150, NX + 1600, NX - 1800)):
        O.draw_palm(cr, px, t, h=560, s=0.7, yb=HORIZON + 270, sid=22420 + 7 * k)
    hx0, hx1, hy = NX - 2100, NX - 1250, HORIZON - 420
    sk_rect(cr, hx0, hy, hx1, HORIZON + 270, 6, sid=22440, fill=(0.98, 0.78, 0.85))
    sk_rect(cr, (hx0 + hx1) / 2 - 90, hy - 160, (hx0 + hx1) / 2 + 90, hy, 6, sid=22441, fill=(0.98, 0.78, 0.85))
    for r_ in range(4):
        for c_ in range(5):
            sk_rect(cr, hx0 + 50 + 160 * c_, hy + 60 + 150 * r_, hx0 + 140 + 160 * c_, hy + 140 + 150 * r_, 4,
                    sid=22450 + r_ * 5 + c_, fill=(0.35, 0.80, 0.85))
    draw_text(cr, "OCEAN VIEW", (hx0 + hx1) / 2, hy - 80, 50, color=(60, 230, 230))
    sk_rect(cr, DOOR_X - 2400, FLOOR_Y - 1500, DOOR_X - 200, FLOOR_Y, 7, sid=22460, fill=(0.28, 0.20, 0.40))
    sk_rect(cr, DOOR_X - 520, FLOOR_Y - 640, DOOR_X - 220, FLOOR_Y, 6, sid=22461, fill=(0.55, 0.30, 0.85))
    draw_text(cr, "GAME CAVE", DOOR_X - 900, FLOOR_Y - 1050, 90, color=(255, 120, 220))
    O.draw_palm(cr, PALM_X, t, h=900, bend=0.5, sid=22480)
    # the phone he dropped on day 22
    cr.save(); cr.translate(NX + 290, FLOOR_Y - 12); cr.scale(1.0, 0.35); cr.rotate(0.3)
    sk_rect(cr, -58, -100, 58, 100, 5, sid=22610, fill=(0.12, 0.12, 0.16)); cr.restore()
def neon_money(cr, t):
    if t >= CUT_FULL - FR: return
    for i, (x, yl, al) in enumerate(BILLS):
        O.draw_dollar(cr, x, yl, s=0.55, ang=al, sid=24150 + (i % 5) * 3)

def draw_fog(cr, x, t, sid=31700):
    """a tall wall of purple fog hiding the border between the worlds."""
    for k in range(26):
        yy = FLOOR_Y + 80 - 130 * (k // 2)
        xx = x + (90 if k % 2 else -110) + 50 * math.sin(t * 1.3 + k)
        O.draw_smoke_puff(cr, xx, yy, 230 + 30 * math.sin(k * 1.9), alpha=0.97)
    cr.rectangle(x - 160, -3000, 320, FLOOR_Y + 3200); cr.set_source_rgba(0.62, 0.55, 0.72, 0.96); cr.fill()

# ================================================================ THE DARK SIDE OF TOWN
NSKY = [(-3000, (0.10, 0.08, 0.18)), (0, (0.15, 0.11, 0.25)), (500, (0.22, 0.16, 0.33)), (850, (0.30, 0.22, 0.40))]
WALK_TOP = FLOOR_Y - 230
def dark(cr, t):
    x0, x1 = GX - 3000, GX + 11000
    for i, (y, c) in enumerate(NSKY):
        y1 = NSKY[i + 1][0] if i + 1 < len(NSKY) else WALK_TOP
        cr.rectangle(x0, y, x1 - x0, y1 - y + 1); cr.set_source_rgb(*c); cr.fill()
    cx, cy, z = L.cam_track.at(t)
    # stars + the moon ride with the camera (far away)
    for k in range(22):
        sx = cx - 900 + (k * 397) % 1800; sy = cy - 1300 + (k * 211) % 700
        cr.arc(sx, sy, 4 + (k % 3) * 2, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.5 + 0.4 * math.sin(t * 2 + k)); cr.fill()
    mx, my = cx - 300, cy - 760
    cr.arc(mx, my, 260, 0, 2 * math.pi); cr.set_source_rgba(0.95, 0.93, 0.85, 0.12); cr.fill()
    sk_circ(cr, mx, my, 190, 5, sid=31800, fill=(0.96, 0.95, 0.88))
    for (dx, dy, r) in ((-60, -40, 34), (50, 30, 24), (-20, 70, 18)):
        cr.arc(mx + dx, my + dy, r, 0, 2 * math.pi); cr.set_source_rgb(0.86, 0.85, 0.78); cr.fill()
    # skyline silhouettes
    _s = random.Random(5)
    bx = GX - 2600
    while bx < GX + 4800:
        w = _s.uniform(260, 520); h = _s.uniform(500, 1100)
        cr.rectangle(bx, WALK_TOP - h, w, h); cr.set_source_rgb(0.19, 0.15, 0.27); cr.fill()
        for r_ in range(int(h // 160)):
            for c_ in range(int(w // 130)):
                if _s.random() < 0.35:
                    cr.rectangle(bx + 40 + 130 * c_, WALK_TOP - h + 60 + 160 * r_, 50, 70)
                    cr.set_source_rgb(0.75, 0.55, 0.95) if _s.random() < 0.5 else cr.set_source_rgb(0.95, 0.82, 0.45); cr.fill()
        bx += w + _s.uniform(10, 80)
    # the cemetery hill (behind everything right of the club)
    cr.move_to(GX + 4600, WALK_TOP)
    for k in range(41):
        xx = GX + 4600 + k * 100; yy = WALK_TOP - 220 - 160 * math.sin(min(math.pi, k / 40 * math.pi))
        cr.line_to(xx, yy)
    cr.line_to(GX + 11000, WALK_TOP - 200); cr.line_to(GX + 11000, WALK_TOP); cr.close_path()
    cr.set_source_rgb(0.20, 0.18, 0.27); cr.fill()
    # sidewalk + street
    cr.rectangle(x0, WALK_TOP, x1 - x0, FLOOR_Y - WALK_TOP + 1); cr.set_source_rgb(0.40, 0.36, 0.47); cr.fill()
    for k in range(-14, 34):
        sketch_line(cr, [(GX + 300 * k, WALK_TOP + 10), (GX + 300 * k - 60, FLOOR_Y - 5)], 3, sid=31810 + (k % 7), color=(0.30, 0.27, 0.36), amp=0.4)
    cr.rectangle(x0, FLOOR_Y, x1 - x0, 900); cr.set_source_rgb(0.17, 0.15, 0.21); cr.fill()
    for k in range(-10, 40):
        cr.rectangle(GX + 360 * k, FLOOR_Y + 170, 170, 16); cr.set_source_rgb(0.55, 0.50, 0.62); cr.fill()
    sketch_line(cr, [(x0, FLOOR_Y), (x1, FLOOR_Y)], 6, sid=31820, amp=0.3)
    # PRESTIGE MOTORS (the lot)
    sk_rect(cr, GX - 900, FLOOR_Y - 1050, GX + 1000, WALK_TOP + 20, 7, sid=31830, fill=(0.80, 0.80, 0.86))
    for k in range(5):
        sk_rect(cr, GX - 840 + 370 * k, FLOOR_Y - 920, GX - 540 + 370 * k, WALK_TOP - 30, 4, sid=31831 + k, fill=(0.60, 0.68, 0.80))
    sk_rect(cr, GX - 700, FLOOR_Y - 1230, GX + 800, FLOOR_Y - 1080, 6, sid=31840, fill=(0.10, 0.10, 0.13))
    draw_text(cr, "PRESTIGE MOTORS", GX + 50, FLOOR_Y - 1155, 86, color=(240, 205, 90))
    for k, lx in enumerate((GX - 250, GX + 850)):                  # spotlights on the car
        cr.move_to(lx, FLOOR_Y - 1040); cr.line_to(C0 - 420 + 300 * k, FLOOR_Y); cr.line_to(C0 + 80 + 300 * k, FLOOR_Y); cr.close_path()
        cr.set_source_rgba(1.0, 0.97, 0.80, 0.22); cr.fill()
    sk_ell(cr, C0, FLOOR_Y - 10, 640, 38, 5, sid=31845, fill=(0.85, 0.85, 0.90))      # the turntable
    if t < T_GO1:                                                   # the price sticker on its stand
        pass
    # street lamps between the lot and the club
    for k, lx in enumerate((GX + 1500, GX + 2300, GX + 3350, GX + 5000, GX + 6900)):
        sketch_line(cr, [(lx, FLOOR_Y), (lx, FLOOR_Y - 900), (lx + 90, FLOOR_Y - 940)], 9, sid=31850 + k, amp=0.3)
        cr.arc(lx + 100, FLOOR_Y - 900, 140, 0, 2 * math.pi); cr.set_source_rgba(0.85, 0.65, 1.0, 0.18); cr.fill()
        sk_circ(cr, lx + 100, FLOOR_Y - 905, 32, 4, sid=31860 + k, fill=(0.92, 0.82, 1.0))
    # THE CRYPT
    sk_rect(cr, CLUB_X0, FLOOR_Y - 1350, CLUB_X1, WALK_TOP + 10, 7, sid=31870, fill=(0.46, 0.40, 0.53))
    for r_ in range(9):
        for c_ in range(6):
            bxx = CLUB_X0 + 30 + 135 * c_ + (60 if r_ % 2 else 0)
            if bxx + 90 < CLUB_X1:
                sketch_line(cr, [(bxx, FLOOR_Y - 1300 + 120 * r_), (bxx + 90, FLOOR_Y - 1300 + 120 * r_)], 3, sid=31871 + (r_ * 6 + c_) % 9,
                            color=(0.36, 0.31, 0.42), amp=0.4)
    sk_poly(cr, [(CDOOR - 130, WALK_TOP + 10), (CDOOR - 130, FLOOR_Y - 820), (CDOOR, FLOOR_Y - 930), (CDOOR + 130, FLOOR_Y - 820),
                 (CDOOR + 130, WALK_TOP + 10)], 6, sid=31880, fill=(0.10, 0.07, 0.12))
    glow = 0.85 + 0.15 * math.sin(t * 9) * (1 if int(t * 1.3) % 5 == 0 else 0)
    cr.rectangle(CLUB_X0 + 60, FLOOR_Y - 1300, CLUB_X1 - CLUB_X0 - 120, 160); cr.set_source_rgba(0.10, 0.06, 0.14, 0.9); cr.fill()
    draw_text(cr, "THE CRYPT", (CLUB_X0 + CLUB_X1) / 2, FLOOR_Y - 1220, 100, color=(205, 120, 255), alpha=glow)
    sk_rect(cr, CLUB_X0 + 40, FLOOR_Y - 1110, CLUB_X0 + 300, FLOOR_Y - 950, 5, sid=31885, fill=(0.12, 0.08, 0.14))
    draw_text(cr, "IT'S NOT", CLUB_X0 + 170, FLOOR_Y - 1065, 40, color=(255, 120, 200))
    draw_text(cr, "A PHASE", CLUB_X0 + 170, FLOOR_Y - 1005, 40, color=(255, 120, 200))
    O.draw_easel(cr, EASEL_X, FLOOR_Y, text="DRESS CODE:|ALL BLACK", sid=31890)
    # the cemetery: tombstones, crooked tree, the mausoleum, the open grave, the fence + gate
    for k, (tx, h) in enumerate(((GX + 5150, 230), (GX + 5700, 200), (GX + 5950, 260), (GX + 6250, 210), (GX + 7600, 240), (GX + 7950, 200), (GX + 8300, 230))):
        yb = WALK_TOP + 40
        sk_poly(cr, [(tx - 80, yb), (tx - 80, yb - h + 60), (tx - 50, yb - h + 10), (tx, yb - h), (tx + 50, yb - h + 10), (tx + 80, yb - h + 60),
                     (tx + 80, yb)], 5, sid=31900 + k, fill=(0.62, 0.62, 0.68))
        draw_text(cr, "RIP", tx, yb - h + 85, 34, color=(70, 70, 80))
    tx_ = GX + 7600
    sketch_line(cr, [(tx_ - 300, WALK_TOP - 120), (tx_ - 320, WALK_TOP - 700), (tx_ - 230, WALK_TOP - 900), (tx_ - 100, WALK_TOP - 960)], 22, sid=31910, amp=0.6)
    sketch_line(cr, [(tx_ - 320, WALK_TOP - 650), (tx_ - 480, WALK_TOP - 820), (tx_ - 560, WALK_TOP - 800)], 14, sid=31911, amp=0.6)
    sketch_line(cr, [(tx_ - 260, WALK_TOP - 860), (tx_ - 330, WALK_TOP - 1050)], 12, sid=31912, amp=0.6)
    # the mausoleum
    mx0, mx1, my0 = MAUS_X - 330, MAUS_X + 330, FLOOR_Y - 820
    sk_rect(cr, mx0, my0, mx1, WALK_TOP + 20, 7, sid=31920, fill=(0.66, 0.65, 0.72))
    sk_poly(cr, [(mx0 - 40, my0), (MAUS_X, my0 - 230), (mx1 + 40, my0)], 7, sid=31921, fill=(0.58, 0.57, 0.64))
    for k in range(4): sk_rect(cr, mx0 + 30 + 170 * k, my0 + 20, mx0 + 80 + 170 * k, WALK_TOP + 10, 4, sid=31922 + k, fill=(0.74, 0.73, 0.80))
    sk_rect(cr, MAUS_X - 120, FLOOR_Y - 560, MAUS_X + 120, WALK_TOP + 15, 6, sid=31926, fill=(0.06, 0.05, 0.08))
    draw_text(cr, "EST. 1666", MAUS_X, my0 - 70, 38, color=(60, 60, 70))
    # the open grave (a hole in the ground + a dirt mound + its headstone)
    sk_poly(cr, [(GRAVE_X - 200, FLOOR_Y), (GRAVE_X + 220, FLOOR_Y), (GRAVE_X + 190, FLOOR_Y + 70), (GRAVE_X - 170, FLOOR_Y + 70)], 5, sid=31930, fill=(0.06, 0.05, 0.06))
    sk_poly(cr, [(GRAVE_X + 260, FLOOR_Y), (GRAVE_X + 330, FLOOR_Y - 110), (GRAVE_X + 470, FLOOR_Y - 120), (GRAVE_X + 560, FLOOR_Y)], 5, sid=31931, fill=(0.36, 0.26, 0.20))
    # the iron fence (behind the path) + the ramp slab
    for k in range(int((MAUS_X + 1500 - GATE_X) // 70)):
        fx = GATE_X + 160 + 70 * k
        if abs(fx - GRAVE_X) < 300: continue
        sketch_line(cr, [(fx, WALK_TOP + 20), (fx, WALK_TOP - 330)], 6, sid=31940 + k % 9, amp=0.3)
        sk_poly(cr, [(fx - 12, WALK_TOP - 330), (fx, WALK_TOP - 365), (fx + 12, WALK_TOP - 330)], 3, sid=31950 + k % 9, fill=INKC)
    sketch_line(cr, [(GATE_X + 160, WALK_TOP - 280), (MAUS_X + 1500, WALK_TOP - 280)], 6, sid=31960, amp=0.4)
    sk_poly(cr, [(RAMP_X - 380, FLOOR_Y), (RAMP_X + 40, FLOOR_Y - 190), (RAMP_X + 60, FLOOR_Y - 150), (RAMP_X + 20, FLOOR_Y)], 6, sid=31965, fill=(0.62, 0.62, 0.68))
    # the gate (stone pillars + iron leaves until the car goes through)
    for d in (-1, 1):
        sk_rect(cr, GATE_X + d * 170 - 50, FLOOR_Y - 820, GATE_X + d * 170 + 50, FLOOR_Y, 6, sid=31970 + (d > 0), fill=(0.58, 0.57, 0.64))
        sk_circ(cr, GATE_X + d * 170, FLOOR_Y - 850, 45, 5, sid=31972 + (d > 0), fill=(0.58, 0.57, 0.64))
    if t < T_GATE:
        for k in range(6):
            fx = GATE_X - 110 + 44 * k
            sketch_line(cr, [(fx, FLOOR_Y - 10), (fx, FLOOR_Y - 640)], 7, sid=31975 + k, amp=0.3)
        for yy in (FLOOR_Y - 600, FLOOR_Y - 200): sketch_line(cr, [(GATE_X - 120, yy), (GATE_X + 120, yy)], 7, sid=31982 + (yy > 1000), amp=0.3)
        draw_text(cr, "R.I.P.", GATE_X, FLOOR_Y - 700, 46, color=(220, 220, 230))
    # the fog wall at the left edge of this world
    draw_fog(cr, FOG_G - 200, t, sid=31990)

def flying_bars(cr, t):
    if not (T_GATE <= t < T_GATE + 1.4): return
    u = t - T_GATE
    for k in range(6):
        vx, vy, w = 900 + 260 * k, -1500 + 160 * k, 9 + 3 * k
        x = GATE_X - 110 + 44 * k + vx * u; y = FLOOR_Y - 320 + vy * u + 2600 * u * u
        cr.save(); cr.translate(x, y); cr.rotate(w * u)
        sketch_line(cr, [(0, -320), (0, 320)], 7, sid=31975 + k, amp=0.3); cr.restore()

def world(cr, t):
    if t < CUT_G - FR:
        neon(cr, t); neon_money(cr, t)
        return
    dark(cr, t)
S.background(world)

def props_back(cr, t, p, ly):
    if ly != "back": return
    if t < CUT_G - FR: return
    if girls_on(t):
        for i in range(3): draw_girl(cr, t, i)
    draw_salesman(cr, t)
    draw_car_all(cr, t)
S.prop(props_back)

def props_front(cr, t, p, ly):
    if ly != "front": return
    if t < CUT_G - FR:
        if t >= T_RUN1: draw_fog(cr, FOG_N, t)
        return
    draw_stream_money(cr, t, p)
    draw_splash(cr, t, p)
    if p.get("show", 1.0) > 0.5:
        draw_rose_his(cr, t, p)
        draw_curl_bat(cr, t, p)
    flying_bars(cr, t)
    draw_bats(cr, t)
S.prop(props_front)

# ================================================================ HUD (the neon city's) fades as he leaves
def hud(cr, t):
    if t >= T_HUDOFF[1]: return
    a = 1 - ramp(t, T_HUDOFF[0], T_HUDOFF[1])
    cx, cy, r = 150, 480, 80
    cr.save(); cr.arc(cx, cy, r, 0, 2 * math.pi); cr.set_source_rgba(0.15, 0.20, 0.25, 0.8 * a); cr.fill_preserve()
    cr.set_source_rgba(1, 1, 1, a); cr.set_line_width(6); cr.stroke()
    cr.arc(cx, cy, r - 3, 0, 2 * math.pi); cr.clip()
    for k in range(-3, 4):
        cr.rectangle(cx - r, cy + 40 * k - 5, 2 * r, 10); cr.set_source_rgba(0.6, 0.6, 0.65, a); cr.fill()
    cr.rectangle(cx + 20, cy - r, 12, 2 * r); cr.set_source_rgba(0.6, 0.6, 0.65, a); cr.fill()
    cr.move_to(cx, cy - 16); cr.line_to(cx + 12, cy + 12); cr.line_to(cx - 12, cy + 12); cr.close_path()
    cr.set_source_rgba(1, 1, 1, a); cr.fill()
    cr.restore()
    m = "$999,999,999" if t < CUT_FULL - FR else "$999,999,999"
    draw_text(cr, m, 70, 150, 38, color=(90, 220, 110), alpha=a, anchor="left")
    flash_on = int(t * 4) % 2 == 0
    for k in range(5):
        O.draw_star(cr, 92 + 56 * k, 215, 24, color=(0.35, 0.55, 1.0) if flash_on else (1.0, 0.85, 0.2), alpha=a)
S.overlay(hud)

if __name__ == "__main__":
    S.render("day031.mp4")
