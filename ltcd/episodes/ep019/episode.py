"""Day 19 (re-cut, Justin's call): @nevaehells "Raise your kid to be the next LeBron james" (Instagram, day 18 reel).
Home, on the couch -> he takes the baby and runs out right -> a neighbourhood court: the baby + a basketball; days and
nights whip by and the kid grows up a step each time (granny shot bonks Dad / crossover breaks Dad's ankles + swish /
THE CHOSEN ONE magazine + a dunk / the grown kid chases Dad down and pins his layup on the board) -> THE FINALS: chalk
toss swallows Dad, GAME 7 down one with 0:05, the kid takes off from the free-throw line and shatters the backboard,
102-101 FINAL, confetti; the kid hands Dad the trophy and it flattens him -> the ask at centre court. See BEATS.md.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
import character as C
from ltcd import Track, ramp, lerp, pulse, FLOOR_Y
from ink import smooth, sketch_line, draw_text

FR = 1 / 30

# ================================================================ places
IX = 1300000.0                                      # his house, inside (day 18)
TVX = IX + 650.0; CLOCK = (IX - 150.0, 560.0); OUTLET = (IX + 1010.0, FLOOR_Y - 230.0)
SINKX = IX + 1240.0; FRIDGEX = IX + 1600.0; DOORX = IX - 900.0; COUCHX = IX - 150.0
SEAT_L, SEAT_R = COUCHX - 175.0, COUCHX + 175.0
CX = 3000000.0                                      # the neighbourhood court
CBX = CX - 900.0                                    # its backboard
CRIM = O.hoop_rim(CBX)
AX = 4000000.0                                      # the arena
ABX = AX - 900.0
ARIM = O.hoop_rim(ABX)
FT_X = ARIM[0] + 840.0                              # the free-throw line
CHAIR = AX + 330.0                                  # his spot in the FRONT ROW of the stands
STAND_UP = 300.0                                    # the front row is raised: his feet are behind the courtside wall
WALL_TOP = FLOOR_Y - 600.0
SBX, SBY = AX + 3000.0, 900.0                       # the scoreboard (seen in inserts)
BALL_R = 46.0
BFLOOR = FLOOR_Y - BALL_R

# ================================================================ timeline
T_READ = 0.4; T_LOOKB = 1.6; T_US0 = 2.0; T_UP = 2.25; T_TAKE0, T_TAKE1 = 2.35, 2.65; T_RUN = 2.8; CUT1 = 3.3
T_SKID = 4.0; T_SET0, T_SET1 = 4.3, 4.75; T_DIG = 5.0; T_POP = T_DIG + 1.4; T_DROP = 6.65; T_REST = 7.4
T_POINT = 6.9; T_US1 = 7.6
NIGHTS = [(8.35, 0.17), (8.80, 0.17),
          (11.15, 0.10), (11.42, 0.10), (11.65, 0.10),
          (16.80, 0.09), (17.00, 0.09),
          (22.40, 0.07), (22.55, 0.07)]
SW1, SW2, SW3, SW4 = 8.80, 11.65, 17.00, 22.55     # the kid is older from here (at the darkest frame)
T_CROUCH1, T_TOSS = 9.2, 9.5; T_BONK = 10.15; T_BONK_END = 10.9
T_DRIB0 = 11.85; T_XOVER = 13.0; T_LUNGE = 13.05; T_FALL = 13.55; T_DRIVE1 = 14.1; T_SHOT = 14.5; T_REL = 14.62
T_SWISH = 15.35; T_SW_FLOOR = 15.6
T_WIND = 17.3; T_SLAP = 17.8; T_PEEL = 18.3; CUT_MAG = 18.7; CUT_MAG1 = 19.7; T_LOOKK = 19.9
T_TRUN = 20.1; T_TJUMP = 20.55; T_DUNK = 20.95; T_TDROP = 21.5; T_MAGDROP = 21.9
T_DRUN = 22.75; T_KCHASE = 22.95; T_LAY = 23.45; T_LREL = 23.62; T_BLOCK = 23.75; T_UNPIN = 24.1; T_FLAT = 24.35
T_KPOINT = 25.3; CUT_RUN = 25.85; CUT2 = 26.6
T_DIP = 27.0; T_CLAP = 27.45; T_CLEAR = 29.0
CUT_SB = 29.9; CUT_GO = 31.2; T_GO = 31.35; T_X2 = 31.95; T_TAKEOFF = 33.4; T_SLAM = 35.6; T_KLAND = 36.25
CUT_SB2 = 36.5; CUT_WIN = 37.5; T_SMILE = 38.1
CUT_TRO = 39.2; T_HAND0, T_HAND1 = 39.55, 40.0; T_TIP0, T_FALL0 = 40.3, 41.0; T_IMPACT = 41.45; T_TLAND = 41.85
T_ZOOM0 = 43.0; T_END = 60.3
PLAQUE = ("TELL ME WHAT", "TO DO NEXT IN", "THE COMMENTS")
DFX = AX + 150.0                                    # Dad's feet in the trophy scene
FLAT = 1.42                                         # how far he tips over (rad): flat on his back
TBASE = (DFX + 500 * math.sin(FLAT) - 10, FLOOR_Y - 500 * math.cos(FLAT) - 12)   # the trophy, upright on his belly

# ================================================================ poses
def P(name, **kw): L.POSES[name] = kw
P("couch_sit", head=(540, 752), neck=(540, 878), hip=(540, 1228), lknee=(400, 1300), rknee=(680, 1300), lfoot=(430, FLOOR_Y),
  rfoot=(650, FLOOR_Y), lelb=(465, 1075), lhand=(462, 1200), relb=(615, 1075), rhand=(618, 1200), lfoot_dir=-0.5, rfoot_dir=0.5, nowalk=1.0)
P("couch_arm", **dict(L.POSES["couch_sit"], lelb=(430, 830), lhand=(290, 820), lhand_t="mitt"))
P("g_sit_hold", **dict(L.POSES["couch_sit"], head=(540, 740), neck=(540, 862), hip=(540, 1205), lelb=(470, 1030), lhand=(480, 1100),
  relb=(610, 1030), rhand=(600, 1100), lhand_t="grip", rhand_t="grip"))
P("carry", lelb=(455, 980), lhand=(470, 1050), relb=(625, 980), rhand=(610, 1050), lhand_t="grip", rhand_t="grip", swing=0.0)
P("set_down", head=(470, 900), neck=(490, 1020), hip=(560, 1280), lknee=(450, 1330), rknee=(640, 1360), lfoot=(470, FLOOR_Y),
  rfoot=(640, FLOOR_Y), lelb=(420, 1180), lhand=(380, 1380), relb=(520, 1200), rhand=(470, 1390), lhand_t="grip", rhand_t="grip", nowalk=1.0)
P("hold_r", relb=(630, 960), rhand=(660, 900), rhand_t="grip")
P("defend", head=(540, 800), neck=(540, 925), hip=(540, 1240), lknee=(420, 1330), rknee=(660, 1330), lfoot=(400, FLOOR_Y),
  rfoot=(680, FLOOR_Y), lelb=(400, 980), lhand=(330, 900), relb=(680, 980), rhand=(750, 900), lfoot_dir=-0.8, rfoot_dir=0.8, nowalk=1.0)
P("lunge", head=(700, 820), neck=(680, 940), hip=(610, 1240), lknee=(480, 1360), rknee=(760, 1320), lfoot=(380, FLOOR_Y),
  rfoot=(820, FLOOR_Y), lelb=(560, 980), lhand=(470, 900), relb=(780, 980), rhand=(860, 880), nowalk=1.0)
P("face_mag", lelb=(440, 860), lhand=(480, 660), relb=(640, 860), rhand=(600, 660), lhand_t="grip", rhand_t="grip")
P("hold_mag", lelb=(455, 1000), lhand=(475, 930), relb=(625, 1000), rhand=(605, 930), lhand_t="grip", rhand_t="grip")
P("dribble_l", hip=(540, 1150), lknee=(480, 1310), rknee=(600, 1310), neck=(530, 790), head=(525, 665),
  lelb=(440, 990), lhand=(390, 1120), relb=(620, 990), rhand=(660, 1060), lfoot_dir=-0.9, rfoot_dir=-0.6)
P("layup", hip=(540, 1100), lknee=(450, 1150), lfoot=(470, 1330), rknee=(560, 1290), rfoot=(600, FLOOR_Y),
  lelb=(470, 650), lhand=(430, 500), lhand_t="grip", relb=(620, 960), rhand=(660, 1050), nowalk=1.0)
P("chair_sit", head=(560, 690), neck=(560, 815), hip=(565, 1150), lknee=(400, 1155), rknee=(420, 1170), lfoot=(410, FLOOR_Y),
  rfoot=(440, FLOOR_Y), lelb=(500, 1000), lhand=(430, 1140), relb=(560, 1010), rhand=(460, 1150), lfoot_dir=-0.8, rfoot_dir=-0.8, nowalk=1.0)
P("tro_hold", lelb=(450, 960), lhand=(460, 860), relb=(630, 960), rhand=(620, 860), lhand_t="grip", rhand_t="grip")
# the kid
P("k_up", lelb=(460, 600), lhand=(495, 450), relb=(620, 600), rhand=(585, 450), lhand_t="grip", rhand_t="grip")
P("k_crouch_up", hip=(540, 1180), lknee=(470, 1320), rknee=(610, 1320), neck=(540, 840), head=(540, 715),
  lelb=(460, 680), lhand=(495, 530), relb=(620, 680), rhand=(585, 530), lhand_t="grip", rhand_t="grip")
P("k_toss", lelb=(480, 640), lhand=(500, 480), relb=(600, 640), rhand=(580, 480))
P("k_shoot", lelb=(470, 680), lhand=(500, 540), relb=(590, 650), rhand=(560, 500), lhand_t="grip", rhand_t="grip")
P("k_hip", relb=(630, 980), rhand=(640, 1100), rhand_t="grip")
P("k_hipL", lelb=(450, 980), lhand=(440, 1100), lhand_t="grip")
P("k_dunk", lelb=(480, 640), lhand=(470, 470), lhand_t="grip", relb=(620, 950), rhand=(650, 1040),
  lknee=(500, 1290), lfoot=(470, 1420), rknee=(600, 1300), rfoot=(620, 1440), nowalk=1.0)
P("k_hang", lelb=(500, 610), lhand=(500, 450), lhand_t="grip", relb=(600, 610), rhand=(590, 450), rhand_t="grip",
  lknee=(520, 1300), lfoot=(510, 1470), rknee=(570, 1300), rfoot=(580, 1470), nowalk=1.0)
P("k_fly", lknee=(430, 1180), lfoot=(330, 1270), rknee=(630, 1300), rfoot=(730, 1430),
  lelb=(440, 820), lhand=(380, 760), relb=(650, 690), rhand=(690, 540), rhand_t="grip", nowalk=1.0)
P("k_block", lelb=(440, 640), lhand=(380, 480), relb=(610, 960), rhand=(650, 1040),
  lknee=(470, 1250), lfoot=(430, 1380), rknee=(600, 1300), rfoot=(640, 1440), nowalk=1.0)
P("k_dip", lelb=(470, 1050), lhand=(470, 1180), relb=(610, 1050), rhand=(610, 1180), hip=(540, 1150), lknee=(490, 1310), rknee=(590, 1310))
P("k_clap", lelb=(470, 680), lhand=(530, 520), relb=(610, 680), rhand=(550, 520))
P("k_tro", lelb=(455, 950), lhand=(470, 860), relb=(625, 950), rhand=(610, 860), lhand_t="grip", rhand_t="grip")

# ================================================================ the scene (Dad)
S = M.Scene(start_body="couch_sit", start_face="deadpan", x0=SEAT_R - 540)
S.auto_blinks = True
S.floor = False
S.card("nevaehells", "Raise your kid to be the next LeBron james", "0", t0=0.3)
CAM0 = (IX - 150, 880, 0.85)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0

def dig_pull(t0, hold_pose, look=(0.4, -0.2), **kw):
    """digs his hand around at his hip (no pocket), POP -> the thing is in his hand (drawn by the caller from t0+1.4)."""
    POCK = (595 + S.x, 1092)
    S.set(t0, "stand", "deadpan", dur=0.35, look=(0.35, 0.9), tilt=0.05, **kw)
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
            L.burst_lines(cr, p["rhand"][0], p["rhand"][1] - 60, (tt - t0 - 1.4) / 0.4, r0=70, r1=130, n=10, sid=9)
    S.prop(pr)

def at(t, x):            # instant re-position of Dad (inside a time-lapse flash or a cut)
    S.cut(t, x=x - 540)

# ---------------------------------------------------------------- A: home, on the couch
S.set(0.0, "couch_sit", "deadpan", dur=0.0, turn=-0.3, look=(-0.5, 0.2))
S.set(T_READ, "couch_sit", "deadpan", dur=0.3, turn=0.3, look=(0.7, -0.9), tilt=-0.05)
def read_hk(tt, p):
    if T_READ + 0.3 <= tt < T_LOOKB - 0.1:
        k = (tt - T_READ - 0.3) / 0.45; u = k % 1.0
        p["look"] = (0.4 + 0.5 * smooth(u), -0.92 + 0.1 * int(k % 2))
    return p
S.hook(read_hk)
S.set(T_LOOKB, "couch_sit", "deadpan", dur=0.3, turn=-0.6, look=(-1.0, 0.5))                 # the baby
S.set(T_US0, "couch_sit", "deadpan", dur=0.3, turn=0.0, look=(0.0, 0.0), brow=-0.35)           # to us: decided
S.set(T_UP, "stand", "deadpan", dur=0.25, turn=-0.5, look=(-0.9, 0.4), brow=-0.3)
S.set(T_TAKE0, "carry", "deadpan", dur=0.3, turn=-0.5, look=(-0.6, 0.6), brow=-0.3)
S.set(T_RUN, "carry", "deadpan", dur=0.15, run=1.0, look=(1.0, 0.0), turn=1.0, lean=0.1, brow=-0.3)
S.xkeys.append((T_RUN, IX + 900 - 540, CUT1 - T_RUN, "inn")); S.x = IX + 900 - 540
S.sfx(T_RUN, "whoosh", 0.05)

# ---------------------------------------------------------------- B: the court
CAM_C = (CX - 300, 870, 0.72)
S.cut(CUT1 - FR, cam=CAM_C, x=CX - 1250 - 540)
S.set(CUT1 - FR, "carry", "deadpan", dur=0.0, run=1.0, look=(1.0, 0.0), turn=1.0, lean=0.1, brow=-0.3)
S.xkeys.append((CUT1, CX + 80 - 540, T_SKID - CUT1, "out")); S.x = CX + 80 - 540
S.set(T_SKID - 0.1, "carry", "deadpan", dur=0.12, ease="snap", run=0.0, stretch=-0.25, turn=0.3, look=(0.5, 0.0))
S.sfx(T_SKID - 0.1, "skid", 0.05, dur=0.3)
S.set(T_SKID + 0.1, "carry", "deadpan", dur=0.25, ease="back", turn=-0.5, look=(-0.8, -0.3))           # looks at the hoop
S.set(T_SET0, "set_down", "deadpan", dur=0.35, turn=-0.6, look=(-0.7, 0.9))
S.set(T_SET1 + 0.1, "stand", "deadpan", dur=0.35, turn=-0.4, look=(-0.6, 0.8))
dig_pull(T_DIG, "hold_r", look=(0.3, 0.3), turn=-0.2)
S.set(T_DROP, "stand", "deadpan", dur=0.2, turn=-0.4, look=(-0.4, 0.9))
S.sfx(T_DROP + 0.25, "tok", 0.06); S.sfx(T_DROP + 0.5, "tok", 0.04); S.sfx(T_DROP + 0.65, "tok", 0.025)
S.set(T_POINT, "point_left", "deadpan", dur=0.25, ease="back", turn=-0.6, look=(-0.9, -0.5))
S.set(T_US1, "point_left", "dead_stare", dur=0.35, turn=0.0, look=(0.0, 0.0))
S.set(SW1 - FR, "arms_crossed", "deadpan", dur=0.0, turn=-0.4, look=(-0.6, 0.3))
# the toddler's granny shot
S.set(T_TOSS + 0.15, "arms_crossed", "deadpan", dur=0.3, turn=-0.3, look=(-0.3, -1.0))            # eyes up with the ball
S.set(T_BONK, "arms_crossed", "deadpan", dur=0.08, ease="snap", stretch=-0.2, lid=0.6, look=(0.0, -0.4))
S.sfx(T_BONK, "bonk", 0.08)
S.set(T_BONK + 0.15, "arms_crossed", "dead_stare", dur=0.3, ease="back", stretch=0.0, lid=0.55, twitch=0.6)
S.set(T_BONK + 0.55, "arms_crossed", "dead_stare", dur=0.3, look=(0.0, 0.0), lid=0.5)
S.sfx(T_BONK + 0.45, "tok", 0.03); S.sfx(T_BONK + 0.7, "tok", 0.02)
# the crossover
at(SW2 - FR, CX - 200)
S.set(SW2 - FR, "defend", "deadpan", dur=0.0, turn=0.6, look=(0.8, 0.4))
def defend_hk(tt, p):
    if SW2 <= tt < T_LUNGE:
        dx = 22 * math.sin((tt - SW2) * 7.0)
        for k in L.JOINTS: p[k] = (p[k][0] + dx, p[k][1])
    return p
S.hook(defend_hk)
S.set(T_LUNGE, "lunge", "deadpan", dur=0.15, ease="snap", turn=0.6, look=(1.0, 0.5))
S.set(T_LUNGE + 0.3, "lunge", "dead_stare", dur=0.15, turn=0.0, look=(-0.8, 0.4), eyescale=1.15)
S.set(T_FALL, "sit_floor", "dead_stare", dur=0.18, ease="snap", turn=-0.3, look=(-0.9, 0.0), eyescale=1.1)
S.sfx(T_FALL + 0.12, "thud", 0.09)
S.set(T_FALL + 0.6, "sit_floor", "deadpan", dur=0.4, turn=-0.6, look=(-1.0, -0.5))
S.set(T_SW_FLOOR + 0.2, "sit_floor", "dead_stare", dur=0.35, turn=0.0, look=(0.0, 0.0))
S.sfx(T_SWISH, "whoosh", 0.04, dur=0.25)
# the magazine + the dunk
at(SW3 - FR, CX + 150)
S.set(SW3 - FR, "stand", "deadpan", dur=0.0, turn=-0.4, look=(-0.7, 0.2))
S.sfx(T_WIND, "wind", 0.05, dur=0.8)
S.set(T_WIND + 0.2, "stand", "deadpan", dur=0.25, turn=0.5, look=(0.9, -0.3))
S.set(T_SLAP, "face_mag", "deadpan", dur=0.1, ease="snap", stretch=-0.15, show=1.0)
S.sfx(T_SLAP, "pat", 0.09)
S.set(T_SLAP + 0.2, "face_mag", "deadpan", dur=0.25, ease="back", stretch=0.0)
S.set(T_PEEL, "hold_mag", "deadpan", dur=0.3, turn=0.0, look=(0.0, 0.9))
S.sfx(T_PEEL, "flip", 0.05)
S.cut(CUT_MAG - FR, cam=(CX + 150, 1000, 2.1))
S.cut(CUT_MAG1 - FR, cam=CAM_C)
S.set(T_LOOKK, "hold_mag", "deadpan", dur=0.35, turn=-0.5, look=(-1.0, 0.0))
S.set(T_DUNK + 0.1, "hold_mag", "dead_stare", dur=0.15, turn=-0.5, look=(-1.0, -0.6), eyescale=1.12)
S.sfx(T_DUNK, "clack", 0.09); S.sfx(T_DUNK + 0.02, "thud", 0.06); S.shake(T_DUNK, 0.4, 10)
S.set(T_MAGDROP, "stand", "deadpan", dur=0.3, turn=0.0, look=(0.0, 0.0))
S.sfx(T_TDROP + 0.2, "thud", 0.04)
# the block
at(SW4 - FR, CX + 50)
S.set(SW4 - FR, "dribble_l", "deadpan", dur=0.0, turn=-0.7, look=(-1.0, -0.2), swing=0.0)
S.set(T_DRUN, "dribble_l", "deadpan", dur=0.1, run=1.0, swing=0.0, turn=-0.8, look=(-1.0, -0.3))
S.xkeys.append((T_DRUN, CX - 430 - 540, T_LAY - T_DRUN, "linear")); S.x = CX - 430 - 540
S.set(T_LAY, "layup", "deadpan", dur=0.15, ease="snap", run=0.0, hop=130, turn=-0.8, look=(-0.8, -0.8))
S.set(T_BLOCK, "layup", "dead_stare", dur=0.1, hop=130, turn=-0.8, look=(-0.5, -1.0), eyescale=1.15)
S.sfx(T_BLOCK, "pat", 0.12); S.sfx(T_BLOCK + 0.02, "clack", 0.07)
S.set(T_BLOCK + 0.25, "stand", "dead_stare", dur=0.2, hop=0, turn=-0.4, look=(0.6, -0.8))
S.set(T_FLAT, "lie_back", "dead_stare", dur=0.2, ease="snap", turn=0.0, look=(0.6, -0.6))
S.sfx(T_FLAT + 0.15, "thud", 0.09)
S.set(T_FLAT + 0.6, "lie_back", "dead_stare", dur=0.35, look=(0.0, -0.2))
S.sfx(T_UNPIN + 0.35, "tok", 0.04); S.sfx(T_UNPIN + 0.6, "tok", 0.025)
S.set(T_KPOINT + 0.2, "lie_back", "deadpan", dur=0.3, look=(0.9, -0.6))
at(CUT_RUN - FR, CX - 300)
S.set(CUT_RUN - FR, "stand", "deadpan", dur=0.0, run=1.0, turn=1.0, look=(1.0, 0.0), lean=0.1)
S.xkeys.append((CUT_RUN, CX + 900 - 540, CUT2 - CUT_RUN, "linear")); S.x = CX + 900 - 540
S.sfx(CUT_RUN, "whoosh", 0.04)
for (tn, hw) in NIGHTS: S.sfx(tn - hw, "whoosh", 0.02, dur=2 * hw)

# ---------------------------------------------------------------- C: the arena
CAM_A = (AX - 200, 860, 0.66)
S.cut(CUT2 - FR, cam=CAM_A, x=CHAIR - 540)
S.set(CUT2 - FR, "stand", "deadpan", dur=0.0, turn=-0.5, look=(-0.8, 0.3), hop=STAND_UP, nowalk=1.0)
S.set(T_DIP + 0.1, "stand", "deadpan", dur=0.3, turn=-0.6, look=(-1.0, 0.4), hop=STAND_UP, nowalk=1.0)
S.sfx(T_CLAP, "clap", 0.08); S.sfx(T_CLAP + 0.03, "poof", 0.10)
S.set(T_CLEAR, "stand", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), hop=STAND_UP, nowalk=1.0)
S.blink(T_CLEAR + 0.4, T_CLEAR + 0.75)
S.cut(CUT_SB - FR, cam=(SBX, SBY, 1.15))
for k in range(4): S.sfx(CUT_SB + 0.15 + k * 0.32, "thud", 0.05 + 0.01 * k)
S.sfx(CUT_SB + 1.0, "tick", 0.04)
S.cut(CUT_GO - FR, cam=(AX - 50, 860, 0.62))
S.camera(T_GO + 0.3, AX - 300, 860, 0.62, T_SLAM - T_GO - 0.3)
S.set(CUT_GO - FR, "stand", "deadpan", dur=0.0, turn=0.6, look=(0.9, 0.4), hop=STAND_UP, nowalk=1.0)
S.set(T_X2 + 0.2, "stand", "dead_stare", dur=0.3, turn=0.2, look=(0.5, 0.5), hop=STAND_UP, nowalk=1.0)
S.set(T_TAKEOFF - 0.1, "stand", "dead_stare", dur=0.3, turn=-0.6, look=(-1.0, 0.2), hop=STAND_UP, nowalk=1.0)
S.set(T_TAKEOFF + 0.5, "stand", "dead_stare", dur=0.5, turn=-0.7, look=(-1.0, -0.5), eyescale=1.1, hop=STAND_UP, nowalk=1.0)
for tk in (32.4, 33.6, 34.8): S.sfx(tk, "tick", 0.04)
S.sfx(T_X2 + 0.5, "thud", 0.05); S.sfx(T_SLAM + 0.3, "thud", 0.07)
S.sfx(T_SLAM, "kaboom", 0.45); S.sfx(T_SLAM + 0.05, "buzzer", 0.14); S.flash(T_SLAM, 0.45)
S.shake(T_SLAM, 0.7, 24)
S.cut(CUT_SB2 - FR, cam=(SBX, SBY, 1.15))
S.sfx(CUT_SB2 + 0.1, "ding", 0.06)
S.cut(CUT_WIN - FR, cam=(AX - 150, 880, 0.66))
S.set(CUT_WIN - FR, "stand", "deadpan", dur=0.0, turn=-0.6, look=(-1.0, 0.3), hop=STAND_UP, nowalk=1.0)
S.set(T_SMILE, "stand", "happy", dur=0.8, turn=-0.5, look=(-0.9, 0.3), smile=0.45, mouth="auto", hop=STAND_UP, nowalk=1.0)
S.sfx(CUT_WIN + 0.1, "twinkle", 0.04)
# the trophy
S.cut(CUT_TRO - FR, cam=(AX + 60, 900, 0.78), x=DFX - 540)
S.set(CUT_TRO - FR, "stand", "happy", dur=0.0, turn=-0.5, look=(-0.9, -0.3), smile=0.4)
S.set(T_HAND0, "tro_hold", "happy", dur=0.35, turn=-0.4, look=(-0.6, -0.6), smile=0.4)
S.set(T_HAND1 + 0.1, "tro_hold", "deadpan", dur=0.25, turn=0.0, look=(0.0, -0.9), stretch=-0.12)
S.set(T_TIP0, "tro_hold", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lean=0.14, nowalk=1.0)
S.set(T_TIP0 + 0.3, "tro_hold", "dead_stare", dur=0.25, turn=0.0, look=(0.0, 0.0), lean=0.04, nowalk=1.0)
S.set(T_TIP0 + 0.55, "tro_hold", "dead_stare", dur=0.15, turn=0.0, look=(0.0, 0.0), lean=0.26, nowalk=1.0)
S.sfx(T_TIP0 + 0.1, "squeak", 0.03)
S.set(T_FALL0, "tro_hold", "dead_stare", dur=T_IMPACT - T_FALL0, ease="inn", turn=0.0, look=(0.0, 0.0), lean=FLAT, nowalk=1.0)
S.set(T_IMPACT, "stand", "dead_stare", dur=0.25, ease="back", turn=0.0, look=(0.0, 0.0), lean=FLAT, nowalk=1.0)
S.sfx(T_IMPACT, "thud", 0.12); S.shake(T_IMPACT, 0.3, 10)
S.sfx(T_TLAND, "clack", 0.09); S.sfx(T_TLAND + 0.02, "thud", 0.06); S.shake(T_TLAND, 0.25, 8)
S.camera(T_FALL0 - 0.2, AX + 430, 1080, 0.8, 0.8)
S.camera(T_ZOOM0, TBASE[0] + 130, 1250, 1.7, 2.6)
S.camera(T_ZOOM0 + 2.7, TBASE[0] + 130, 1250, 1.84, T_END - T_ZOOM0 - 2.7)
S.blink(T_TLAND + 0.6, 46.5, 51.0, 55.8)
S.t = T_END

# ================================================================ the kid
STAGES = [(0.0, 0, 0.0), (SW1, 1, 0.45), (SW2, 2, 0.62), (SW3, 3, 0.88), (SW4, 4, 1.18), (CUT2 - FR, 5, 1.18)]
def stage(t):
    st = STAGES[0]
    for s_ in STAGES:
        if t >= s_[0]: st = s_
    return st[1], st[2]

KK = [(0.0, L.pose("stand", "neutral"), 0)]
def kk(t, body, face="neutral", dur=0.25, ease="smooth", **kw): KK.append((t, L.pose(body, face, **kw), dur, ease))
KXK = [(0.0, CX - 150, 0)]
def kx(t, x, dur=0.001, ease="linear"): KXK.append((t, x, dur, ease))
KUP = [(0.0, 0.0, 0)]
def kup(t, h, dur=0.2, ease="smooth"): KUP.append((t, h, dur, ease))
KRUN = [(0.0, 0.0, 0)]
def krun(t, v, dur=0.1): KRUN.append((t, v, dur))

# stage 1: the toddler
kx(SW1 - FR, CX - 150); kk(SW1 - FR, "k_up", "neutral", dur=0.0, turn=0.5, look=(0.7, 0.0))
kk(T_CROUCH1, "k_crouch_up", "concentrating", dur=0.25, turn=0.4, look=(0.5, -0.6))
kk(T_TOSS, "k_toss", "neutral", dur=0.12, ease="snap", turn=0.4, look=(0.5, -1.0))
kk(T_BONK + 0.1, "stand", "neutral", dur=0.4, turn=0.6, look=(0.9, -0.3))
# stage 2: the crossover kid
kx(SW2 - FR, CX + 150); kk(SW2 - FR, "dribble_l", "determined", dur=0.0, turn=-0.7, look=(-0.9, 0.0))
kk(T_XOVER, "dribble_l", "determined", dur=0.1, turn=-0.7, look=(-0.9, 0.0), lhand=(680, 1120), lelb=(560, 1000), relb=(640, 990), rhand=(700, 1060))
kx(T_XOVER, CX + 40, 0.25, "smooth")
kk(T_XOVER + 0.28, "dribble_l", "determined", dur=0.12, turn=-0.8, look=(-1.0, 0.0))
krun(T_XOVER + 0.3, 1.0)
kx(T_XOVER + 0.3, CX - 440, T_DRIVE1 - T_XOVER - 0.3, "linear")
krun(T_DRIVE1, 0.0)
kk(T_DRIVE1 + 0.1, "k_shoot", "concentrating", dur=0.2, turn=-0.6, look=(-0.8, -0.9))
kup(T_SHOT, 110, 0.18, "out"); kup(T_REL + 0.2, 0, 0.25, "inn")
kk(T_REL + 0.05, "k_toss", "concentrating", dur=0.1, turn=-0.6, look=(-0.8, -1.0))
kk(T_SWISH + 0.15, "stand", "smug", dur=0.35, turn=0.0, look=(0.0, 0.0))
# stage 3: the teen (headband) + the dunk
kx(SW3 - FR, CX - 280); kk(SW3 - FR, "k_hip", "neutral", dur=0.0, turn=0.5, look=(0.8, 0.0))
kk(T_LOOKK + 0.2, "k_hip", "smug", dur=0.3, turn=0.5, look=(0.9, 0.0))
kk(T_TRUN, "k_hip", "determined", dur=0.15, turn=-0.8, look=(-1.0, -0.5))
krun(T_TRUN, 1.0); kx(T_TRUN, CX - 560, T_TJUMP - T_TRUN, "linear"); krun(T_TJUMP, 0.0)
kk(T_TJUMP, "k_dunk", "determined", dur=0.15, ease="snap", turn=-0.7, look=(-0.8, -1.0), lhand_t="grip")
kup(T_TJUMP, 330, T_DUNK - T_TJUMP, "out")
kx(T_TJUMP, CRIM[0] + 70, T_DUNK - T_TJUMP, "smooth")
kk(T_DUNK, "k_hang", "determined", dur=0.1, ease="snap", turn=-0.3, look=(-0.3, -0.9))
kup(T_DUNK, 300, 0.1)
kup(T_TDROP, 0, 0.25, "inn")
kk(T_TDROP, "stand", "smug", dur=0.3, turn=0.6, look=(0.9, 0.0))
# stage 4: grown, the chase-down block
kx(SW4 - FR, CX + 380); kk(SW4 - FR, "stand", "smug", dur=0.0, turn=-0.6, look=(-0.9, 0.0))
kk(T_KCHASE, "stand", "determined", dur=0.12, turn=-0.9, look=(-1.0, -0.2), run=1.0)
krun(T_KCHASE, 1.0); kx(T_KCHASE, CX - 300, T_LAY + 0.1 - T_KCHASE, "inn"); krun(T_LAY + 0.1, 0.0)
kk(T_LAY + 0.1, "k_block", "determined", dur=0.12, ease="snap", turn=-0.8, look=(-0.8, -1.0), lhand_t="open")
kup(T_LAY + 0.1, 260, T_BLOCK - T_LAY - 0.1, "out"); kx(T_LAY + 0.1, CX - 690, T_BLOCK - T_LAY - 0.1, "out")
kup(T_UNPIN, 0, 0.3, "inn")
kk(T_UNPIN + 0.1, "stand", "smug", dur=0.3, turn=0.3, look=(0.6, 0.6))
kx(T_UNPIN + 0.3, CX - 300, 0.4, "smooth")
kk(T_KPOINT, "point_right", "smug", dur=0.25, ease="back", turn=0.6, look=(0.8, 0.5))
kx(CUT_RUN - FR, CX - 650); kk(CUT_RUN - FR, "stand", "determined", dur=0.0, turn=1.0, look=(1.0, 0.0), run=1.0)
krun(CUT_RUN - FR, 1.0, 0.001); kx(CUT_RUN, CX + 500, CUT2 - CUT_RUN, "linear")
# stage 5: the arena
krun(CUT2 - FR, 0.0, 0.001)
kx(CUT2 - FR, AX - 120); kk(CUT2 - FR, "stand", "determined", dur=0.0, turn=0.6, look=(0.9, 0.0))
kk(T_DIP, "k_dip", "determined", dur=0.3, turn=0.3, look=(0.3, 0.8))
kk(T_CLAP, "k_clap", "determined", dur=0.12, ease="snap", turn=0.0, look=(0.0, -1.0))
kk(T_CLAP + 0.9, "stand", "smug", dur=0.5, turn=0.5, look=(0.9, 0.2))
kx(CUT_GO - FR, AX + 940); kk(CUT_GO - FR, "dribble_l", "determined", dur=0.0, turn=-0.8, look=(-1.0, -0.2))
krun(T_GO, 1.0); kx(T_GO, AX + 760, T_X2 - T_GO, "linear")
kk(T_X2, "dribble_l", "determined", dur=0.1, turn=-0.7, look=(-0.9, 0.0), lhand=(680, 1120), lelb=(560, 1000), relb=(640, 990), rhand=(700, 1060))
kx(T_X2, AX + 660, 0.25, "smooth")
kk(T_X2 + 0.28, "dribble_l", "determined", dur=0.12, turn=-0.8, look=(-1.0, 0.0))
kx(T_X2 + 0.3, FT_X, T_TAKEOFF - T_X2 - 0.3, "linear"); krun(T_TAKEOFF, 0.0)
kk(T_TAKEOFF, "k_fly", "determined", dur=0.25, turn=-0.8, look=(-1.0, -0.4))
kx(T_TAKEOFF, ARIM[0] + 90, T_SLAM - T_TAKEOFF, "smooth")
def fly_h(t): return 380 * math.sin(math.pi * min(1.0, ramp(t, T_TAKEOFF, T_SLAM + 0.15, "linear"))) + 190 * ramp(t, T_TAKEOFF, T_SLAM, "linear")
kk(T_SLAM - 0.12, "k_dunk", "determined", dur=0.12, ease="snap", turn=-0.6, look=(-0.6, -0.8))
kk(T_SLAM + 0.05, "k_hang", "determined", dur=0.1, turn=-0.2, look=(-0.2, -0.6))
kk(T_KLAND, "stand", "smug", dur=0.3, turn=0.4, look=(0.6, -0.2))
kx(CUT_WIN - FR, AX - 520); kk(CUT_WIN - FR, "cheer", "delighted", dur=0.0, turn=0.0, look=(0.0, -0.6))
kk(CUT_WIN + 0.6, "cheer", "delighted", dur=0.3, turn=0.4, look=(0.6, -0.4))
kx(CUT_TRO - FR, AX - 300); kk(CUT_TRO - FR, "k_tro", "happy", dur=0.0, turn=0.6, look=(0.9, -0.2), smile=0.6)
kx(T_HAND0, AX - 190, T_HAND1 - T_HAND0, "smooth")
kk(T_HAND1, "stand", "happy", dur=0.3, turn=0.6, look=(0.9, -0.2), smile=0.6)
kk(T_TIP0 + 0.4, "stand", "surprised", dur=0.3, turn=0.6, look=(0.9, 0.4))
kk(T_IMPACT + 0.3, "stand", "surprised", dur=0.4, turn=0.7, look=(1.0, 0.9))
kk(T_TLAND + 0.6, "stand", "neutral", dur=0.5, turn=0.7, look=(1.0, 0.9), lid=0.5)
KKT, KXT, KUT, KRT = Track(KK), Track(KXK), Track(KUP), Track(KRUN)

def kid_up(t):
    if T_TAKEOFF <= t < T_SLAM + 0.05: return fly_h(t)
    if T_SLAM + 0.05 <= t < T_KLAND:
        return lerp(fly_h(T_SLAM + 0.05), 0.0, smooth(ramp(t, T_SLAM + 0.55, T_KLAND)))
    return KUT.at(t)

def kid_local(t):
    """the kid's pose in local (unscaled) coords, shifted to his x, with a walk/run cycle when moving."""
    p = dict(KKT.at(t))
    x = KXT.at(t); _, s = stage(t)
    ox = x - 540
    for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1])
    v = (KXT.at(t + 0.02) - KXT.at(t - 0.02)) / 0.04 / max(0.3, s)
    run = KRT.at(t)
    if abs(v) > 30 and p.get("nowalk", 0.0) < 0.5 and kid_up(t) < 5:
        d = 1 if v > 0 else -1
        ph = t * 2 * math.pi * (1.6 + 1.4 * run)
        hipx, hipy = p["hip"]
        stride = 58 + 40 * run; liftk = 34 + 30 * run
        for side, off in (("l", 0.0), ("r", math.pi)):
            s_ = math.sin(ph + off); lf = max(0.0, math.cos(ph + off)) * liftk
            foot = (hipx + stride * s_, FLOOR_Y - lf); knee = ((hipx + foot[0]) / 2 + d * (22 + 30 * run), (hipy + FLOOR_Y) / 2 - lf * 0.6)
            p[side + "foot"] = foot; p[side + "knee"] = knee
        bob = (8 + 12 * run) * abs(math.sin(ph))
        for k in ("head", "neck", "hip", "lelb", "relb", "lhand", "rhand"): p[k] = (p[k][0], p[k][1] + bob)
        p["lfoot_dir"] = p["rfoot_dir"] = 0.9 * d
        p["lean"] = 0.08 * d * run
    ln = p.get("lean", 0.0)
    if abs(ln) > 1e-3:
        fx = (p["lfoot"][0] + p["rfoot"][0]) / 2; c, s_ = math.cos(ln), math.sin(ln)
        for k in L.JOINTS:
            if k in ("lfoot", "rfoot"): continue
            dx, dy = p[k][0] - fx, p[k][1] - FLOOR_Y
            p[k] = (fx + dx * c - dy * s_, FLOOR_Y + dx * s_ + dy * c)
    p["breath_ph"] = t * 1.9
    p["hair"] = "hightop"
    return C.constrain(p)

def kid_xf(t):
    """(fx, up, s): the kid is drawn scaled by s around (fx, FLOOR_Y), lifted by up."""
    _, s = stage(t)
    return KXT.at(t), kid_up(t), s
def kid_pt(t, pt):
    fx, up, s = kid_xf(t)
    return (fx + (pt[0] - fx) * s, FLOOR_Y + (pt[1] - FLOOR_Y) * s - up)
def kid_joint(t, j): return kid_pt(t, kid_local(t)[j])
def kid_hands(t):
    p = kid_local(t); a, b = kid_pt(t, p["lhand"]), kid_pt(t, p["rhand"])
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)

KBLINKS = [3.0, 9.9, 12.6, 16.2, 19.0, 22.0, 25.0, 28.5, 30.5, 36.4, 39.8, 44.0, 47.5, 51.0, 55.0, 58.0]
def kid_blink(t):
    for b in KBLINKS:
        if b <= t < b + 0.14: return math.sin(math.pi * (t - b) / 0.14)
    return 0.0

def draw_kid(cr, t):
    st, s = stage(t)
    if st == 0: return
    p = kid_local(t)
    fx, up, s = kid_xf(t)
    cr.save(); cr.translate(fx, FLOOR_Y - up); cr.scale(s, s); cr.translate(-fx, -FLOOR_Y)
    if up < 5 and not (CUT2 - FR <= t < CUT_GO - FR and False):
        L.draw_shadow(cr, fx, scale=0.9)
    if st >= 5:
        p["larm_over"] = p["rarm_over"] = 1.0
    C.draw_guy(cr, t, p, kid_blink(t))
    if st >= 5:
        O.draw_jersey(cr, p, "23")
        C.draw_arm_over(cr, p, "l"); C.draw_arm_over(cr, p, "r")
    if st >= 3:
        O.draw_headband(cr, p)
    L.draw_grips(cr, p)
    cr.restore()

# ================================================================ the other team (the last play): smaller, green
DS = 0.86
DEF = []          # each: dict(x=Track, k=Track of poses, up=Track, num)
def _mk(num, x0):
    d = dict(K=[(0.0, L.pose("defend", "determined", turn=0.6, look=(0.9, 0.0)), 0)], X=[(0.0, x0, 0)], U=[(0.0, 0.0, 0)], num=num)
    DEF.append(d); return d
def dk(d, t, body, face="determined", dur=0.2, ease="smooth", **kw): d["K"].append((t, L.pose(body, face, **kw), dur, ease))
D1, D2, D3 = _mk("7", AX + 640), _mk("11", AX - 130), _mk("4", AX - 470)
# D1: guards the kid at the top, bites on the crossover and sits down (ankles)
dk(D1, T_X2 + 0.05, "lunge", "determined", dur=0.15, ease="snap", turn=0.6, look=(1.0, 0.4))
dk(D1, T_X2 + 0.45, "sit_floor", "shocked", dur=0.18, ease="snap", turn=-0.5, look=(-0.9, -0.2))
dk(D1, T_X2 + 1.0, "sit_floor", "dead_stare", dur=0.4, turn=-0.7, look=(-1.0, -0.6))
# D2: reaches for the steal as he goes by, spins round, watches him fly
dk(D2, T_TAKEOFF + 0.15, "cheer", "determined", dur=0.15, ease="snap", turn=0.6, look=(0.8, -1.0), nowalk=1.0)
D2["U"] += [(T_TAKEOFF + 0.15, 110.0, 0.3, "out"), (T_TAKEOFF + 0.5, 0.0, 0.3, "inn")]
dk(D2, T_TAKEOFF + 0.85, "stand", "shocked", dur=0.3, turn=-0.8, look=(-0.9, -1.0))
# D3: under the rim, jumps to contest - gets dunked on, flat on his back under the glass
dk(D3, T_TAKEOFF, "defend", "determined", dur=0.3, turn=0.6, look=(0.9, -0.8))
dk(D3, T_SLAM - 0.55, "cheer", "determined", dur=0.15, ease="snap", turn=0.6, look=(0.8, -1.0), nowalk=1.0)
D3["U"] += [(T_SLAM - 0.55, 150.0, 0.3, "out"), (T_SLAM - 0.1, 0.0, 0.25, "inn")]
dk(D3, T_SLAM + 0.15, "lie_back", "dizzy", dur=0.15, ease="snap", look=(0.0, -0.4))
dk(D3, T_SLAM + 1.2, "lie_back", "dead_stare", dur=0.4, look=(0.0, -0.6))
for d in DEF: d["KT"], d["XT"], d["UT"] = Track(d["K"]), Track(d["X"]), Track(d["U"])

def def_draw(cr, t, d):
    p = dict(d["KT"].at(t)); x = d["XT"].at(t); ox = x - 540
    for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1])
    if d is D2 or d is D1:                  # a little defensive shuffle while he's guarding
        sh = 14 * math.sin(t * 8.0 + (0 if d is D1 else 2)) * (1 - ramp(t, T_TAKEOFF, T_TAKEOFF + 0.15) if d is D2 else (1.0 if t < T_X2 else 0.0))
        for j in L.JOINTS: p[j] = (p[j][0] + sh, p[j][1])
    p["breath_ph"] = t * 2.1; p["hair"] = "bald"
    p = C.constrain(p)
    fx = x; up = d["UT"].at(t)
    cr.save(); cr.translate(fx, FLOOR_Y - up); cr.scale(DS, DS); cr.translate(-fx, -FLOOR_Y)
    L.draw_shadow(cr, fx, scale=0.8)
    p["larm_over"] = p["rarm_over"] = 1.0
    C.draw_guy(cr, t, p, 0.0)
    O.draw_jersey(cr, p, d["num"], col=(0.12, 0.50, 0.32), trim=(0.97, 0.97, 0.97), sid=23250)
    C.draw_arm_over(cr, p, "l"); C.draw_arm_over(cr, p, "r")
    cr.restore()

def draw_defenders(cr, t):
    if not (CUT_GO - FR <= t) or (CUT_SB2 - FR <= t < CUT_WIN - FR): return
    for d in DEF:
        if t >= CUT_WIN - FR and d is not D3: continue      # the other two have left the floor
        def_draw(cr, t, d)

# ================================================================ the baby (before he grows)
def baby_pos(t, p):
    """(x, y, look) of the swaddled baby, or None."""
    if t < T_TAKE0:
        q = her_pose(t); hc = scale_pt(q, ((q["lhand"][0] + q["rhand"][0]) / 2, (q["lhand"][1] + q["rhand"][1]) / 2))
        return (hc[0] + 10, hc[1] - 15, (0.6, -0.4) if t > T_US0 else (0.0, -0.5))
    hc = ((p["lhand"][0] + p["rhand"][0]) / 2, (p["lhand"][1] + p["rhand"][1]) / 2 - 15)
    if t < T_TAKE1:
        q = her_pose(t); a = scale_pt(q, ((q["lhand"][0] + q["rhand"][0]) / 2, (q["lhand"][1] + q["rhand"][1]) / 2))
        u = smooth(ramp(t, T_TAKE0, T_TAKE1)); return (lerp(a[0] + 10, hc[0], u), lerp(a[1] - 15, hc[1], u), (0.8, -0.5))
    if t < CUT1 - FR: return (hc[0], hc[1], (0.8, -0.5))
    if t < T_SET0 + 0.15: return (hc[0], hc[1], (0.6, -0.6))
    if t < T_SET1:
        u = smooth(ramp(t, T_SET0 + 0.15, T_SET1)); return (lerp(hc[0], CX - 170, u), lerp(hc[1], FLOOR_Y - 62, u), (0.6, -0.6))
    if t < SW1:
        lk = (0.8, -0.7)
        if T_POINT + 0.2 <= t < T_US1 + 0.1: lk = (-1.0, -0.8)
        elif T_US1 + 0.1 <= t: lk = (0.0, 0.0)
        return (CX - 170, FLOOR_Y - 62, lk)
    return None

# ================================================================ her (home only)
G_HAIR, G_DRESS = (0.62, 0.28, 0.16), (0.30, 0.66, 0.66)
GS = 0.92
def her_pose(t):
    if t < T_US0: kw = dict(turn=0.3, look=(0.5, 0.5), smile=0.5); face = "happy"
    elif t < T_TAKE1 + 0.2: kw = dict(turn=0.5, look=(0.8, -0.4), smile=0.2); face = "surprised"
    else: kw = dict(turn=0.6, look=(1.0, -0.2), smile=0.0, eyescale=1.1); face = "surprised"
    p = L.pose("g_sit_hold", face, **kw)
    ox = SEAT_L - 540
    for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1])
    if t >= T_TAKE0:
        u = smooth(ramp(t, T_TAKE0, T_TAKE1 + 0.2))
        p["lhand"] = lerp(p["lhand"], (p["lhand"][0] + 10, p["lhand"][1] + 90), u)
        p["rhand"] = lerp(p["rhand"], (p["rhand"][0] + 10, p["rhand"][1] + 90), u)
        p["lhand_t"] = p["rhand_t"] = "mitt"
    return L.constrain(p)
def scale_pt(p, pt):
    fx = (p["lfoot"][0] + p["rfoot"][0]) / 2
    return (fx + (pt[0] - fx) * GS, FLOOR_Y + (pt[1] - FLOOR_Y) * GS)
def her_blink(t):
    for b in (1.1, 2.9):
        if b <= t < b + 0.16: return math.sin(math.pi * (t - b) / 0.16)
    return 0.0

# ================================================================ the ball
def bounce(t, t0, t1, a, b, n=2, h0=None):
    """from point a, bouncing n times along the floor to rest at x=b[0] (on the floor)."""
    u = ramp(t, t0, t1, "linear")
    x = lerp(a[0], b[0], 1 - (1 - u) ** 2)
    segs = [1.0 / (2 ** i) for i in range(n + 1)]; tot = sum(segs); acc = 0.0
    h0 = h0 if h0 is not None else BFLOOR - a[1]
    for i, sg in enumerate(segs):
        w = sg / tot
        if u <= acc + w or i == n:
            v = min(1.0, (u - acc) / w)
            if i == 0:          # first fall from a
                return (x, lerp(a[1], BFLOOR, v * v))
            h = h0 * 0.35 ** i
            return (x, BFLOOR - h * 4 * v * (1 - v))
        acc += w
    return (x, BFLOOR)
def arc(t, t0, t1, a, b, h):
    u = ramp(t, t0, t1, "linear")
    return (lerp(a[0], b[0], u), lerp(a[1], b[1], u) - h * 4 * u * (1 - u))
def dribble(t, t0, hand, period=0.42):
    k = ((t - t0) / period) % 1.0
    d = 1 - abs(1 - 2 * k)
    return (hand[0], lerp(hand[1] + 40, BFLOOR, d * d * (3 - 2 * d)))

C_REST1 = (CX - 10, BFLOOR)
def ball_pos(t, p):
    """the ball's centre, or None. p = Dad's live pose."""
    if t < T_POP: return None
    if t < T_DROP: return (p["rhand"][0], p["rhand"][1] - 50)
    if t < T_REST: return bounce(t, T_DROP, T_REST, (CX + 230, 840), C_REST1, n=3)
    if t < SW1: return C_REST1
    if t < T_TOSS:
        h = kid_hands(t); return (h[0], h[1] - 40)
    if t < T_BONK:
        h0 = kid_hands(T_TOSS); hd = p["head"]
        return arc(t, T_TOSS, T_BONK, (h0[0], h0[1] - 20), (hd[0] - 10, hd[1] - 160), 380)
    if t < T_BONK_END: return bounce(t, T_BONK, T_BONK_END, (CX + 70, FLOOR_Y - 990), (CX + 520, BFLOOR), n=2, h0=300)
    if t < SW2: return (CX + 520, BFLOOR)
    if t < T_DRIVE1 + 0.1:
        lh = kid_joint(t, "lhand")
        if T_XOVER <= t < T_XOVER + 0.28:
            a = kid_joint(T_XOVER, "lhand"); b = kid_joint(T_XOVER + 0.28, "lhand")
            u = ramp(t, T_XOVER, T_XOVER + 0.28, "linear")
            return (lerp(a[0], b[0], u), lerp(a[1], BFLOOR, 1 - abs(1 - 2 * u)))
        return dribble(t, T_DRIB0, lh, 0.4 if t < T_XOVER else 0.3)
    if t < T_REL:
        h = kid_hands(t); return (h[0], h[1] - 30)
    if t < T_SWISH:
        h0 = kid_hands(T_REL); return arc(t, T_REL, T_SWISH, (h0[0], h0[1] - 30), (CRIM[0] + 2, CRIM[1] - 30), 420)
    if t < T_SW_FLOOR: return (CRIM[0] + 2, lerp(CRIM[1] - 30, BFLOOR, ramp(t, T_SWISH, T_SW_FLOOR, "inn")))
    if t < T_SW_FLOOR + 0.8: return bounce(t, T_SW_FLOOR, T_SW_FLOOR + 0.8, (CRIM[0], BFLOOR - 1), (CRIM[0] + 260, BFLOOR), n=2, h0=220)
    if t < SW3: return (CRIM[0] + 260, BFLOOR)
    if t < T_TJUMP:
        h = kid_joint(t, "rhand"); return (h[0] + 10, h[1] - 0.88 * 40)
    if t < T_DUNK:
        h = kid_joint(t, "lhand"); return (h[0], h[1] - 40)
    if t < T_DUNK + 0.3: return (CRIM[0] + 2, lerp(CRIM[1], BFLOOR, ramp(t, T_DUNK, T_DUNK + 0.3, "inn")))
    if t < T_DUNK + 1.0: return bounce(t, T_DUNK + 0.3, T_DUNK + 1.0, (CRIM[0], BFLOOR - 1), (CRIM[0] + 330, BFLOOR), n=2, h0=250)
    if t < SW4: return (CRIM[0] + 330, BFLOOR)
    if t < T_LAY:
        return dribble(t, SW4, p["lhand"], 0.36)
    if t < T_LREL: return (p["lhand"][0], p["lhand"][1] - 46)
    PIN = (CBX + 110, FLOOR_Y - 1270)
    if t < T_BLOCK:
        a = (p["lhand"][0], p["lhand"][1] - 46)
        u = ramp(t, T_LREL, T_BLOCK, "linear"); return (lerp(a[0], PIN[0], u), lerp(a[1], PIN[1], u))
    if t < T_UNPIN: return PIN
    if t < T_UNPIN + 0.9: return bounce(t, T_UNPIN, T_UNPIN + 0.9, PIN, (CX - 120, BFLOOR), n=2, h0=200)
    if t < CUT2 - FR: return (CX - 120, BFLOOR)
    # arena
    if t < CUT_GO - FR: return None
    if t < T_TAKEOFF:
        return dribble(t, T_GO, kid_joint(t, "lhand"), 0.3)
    if t < T_SLAM - 0.12:
        h = kid_joint(t, "rhand"); return (h[0] + 15, h[1] - 50)
    if t < T_SLAM:
        h = kid_joint(t, "lhand"); return (h[0], h[1] - 50)
    if t < T_SLAM + 0.3: return (ARIM[0], lerp(ARIM[1], BFLOOR, ramp(t, T_SLAM, T_SLAM + 0.3, "inn")))
    if t < T_SLAM + 1.2: return bounce(t, T_SLAM + 0.3, T_SLAM + 1.2, (ARIM[0], BFLOOR - 1), (ARIM[0] + 420, BFLOOR), n=3, h0=260)
    return (ARIM[0] + 420, BFLOOR) if t < CUT_WIN - FR else None

# ================================================================ night (the days whipping by)
def night(t):
    v = 0.0
    for c, hw in NIGHTS:
        if abs(t - c) < hw: v = max(v, math.cos(0.5 * math.pi * (t - c) / hw) ** 2)
    return v
def sun_u(t):
    cs = [c for c, _ in NIGHTS]
    if t < cs[0]: return 0.35 + 0.02 * t
    for a, b in zip(cs, cs[1:]):
        if a <= t < b: return ramp(t, a, b, "linear")
    return 0.25 + 0.03 * (t - cs[-1])
def moon_u(t):
    for c, hw in NIGHTS:
        if abs(t - c) < hw: return 0.5 + 0.5 * (t - c) / hw
    return None
def night_ov(cr, t):
    if not (CUT1 - FR <= t < CUT2 - FR): return
    n = night(t)
    if n > 0.01:
        cr.set_source_rgba(0.04, 0.05, 0.14, 0.72 * n); cr.paint()
S.overlays.insert(0, night_ov)

def clock_ov(cr, t):
    """the game clock during the last play (bottom left, it IS a game)."""
    if not (CUT_GO - FR <= t < T_SLAM): return
    secs = 4 if t < 32.4 else (3 if t < 33.6 else (2 if t < 34.8 else 1))
    L.sketch_rect(cr, 70, 1450, 330, 1580, 6, sid=23300, fill=(0.08, 0.08, 0.1))
    draw_text(cr, f"0:0{secs}", 200, 1515, 90, color=(255, 90, 60))
S.overlay(clock_ov)

# ================================================================ backgrounds
def world(cr, t):
    if t < CUT1 - FR:
        O.draw_room(cr, t, IX - 3000, IX + 3000, door_x=DOORX, door_open=0.0, frame_x=IX - 450, frame_fall=0.0, kitchen_x=IX + 1000)
        O.draw_wall_clock(cr, *CLOCK, hour=7.0, minute=22.0)
        O.draw_outlet(cr, *OUTLET)
        O.draw_tv(cr, TVX, FLOOR_Y - 10, t, screen="off")
        O.draw_sink_counter(cr, SINKX, FLOOR_Y - 10, n=25, t=t)
        O.draw_fridge(cr, FRIDGEX, FLOOR_Y - 10, photo=1.0)
        return
    if t < CUT2 - FR:
        if CUT_MAG - FR <= t < CUT_MAG1 - FR:
            cr.set_source_rgb(0.62, 0.82, 0.97); cr.paint(); return
        O.draw_court_world(cr, t, CX - 6000, CX + 6000, night=night(t), sun_u=sun_u(t), moon_u=moon_u(t))
        return
    if (CUT_SB - FR <= t < CUT_GO - FR) or (CUT_SB2 - FR <= t < CUT_WIN - FR):
        cr.set_source_rgb(0.12, 0.12, 0.17); cr.paint()
        fin = t >= CUT_SB2 - FR
        clock = "0:05" if t < CUT_SB + 1.0 else "0:04"
        fl = 1.0 if (fin and int((t - CUT_SB2) * 5) % 2 == 0) else 0.0
        O.draw_scoreboard(cr, SBX, SBY, home="102" if fin else "100", away="101", clock=clock, top="GAME 7", flash=fl, final=fin)
        return
    roar = 1.0 if t >= T_SLAM else 0.2
    O.draw_arena(cr, t, AX - 6000, AX + 6000, roar=roar, banner_x=AX - 330, flashes=1.0 + 2.0 * (t >= T_SLAM))
    O.draw_paint(cr, ARIM[0], ft_x=FT_X)
S.background(world)

# ================================================================ props
def hoop_state(t):
    """(x, bend, shake, swish, shatter, glass) of the hoop in the current place, or None."""
    if CUT1 - FR <= t < CUT2 - FR and not (CUT_MAG - FR <= t < CUT_MAG1 - FR):
        bend = 0.0; shake = 0.0; sw = 0.0
        if T_DUNK <= t < T_TDROP + 0.6:
            bend = 1.0 if t < T_TDROP else 1.0 - smooth(ramp(t, T_TDROP, T_TDROP + 0.4)) * 1.0 + 0.25 * math.sin((t - T_TDROP) * 30) * (1 - ramp(t, T_TDROP, T_TDROP + 0.6))
            shake = 14 * (1 - ramp(t, T_DUNK, T_TDROP + 0.6))
        if T_BLOCK <= t < T_BLOCK + 0.6: shake = 10 * (1 - ramp(t, T_BLOCK, T_BLOCK + 0.6))
        for ts in (T_SWISH, T_DUNK):
            if ts <= t < ts + 0.8: sw = max(sw, 1 - (t - ts) / 0.8)
        return (CBX, bend, shake, sw, 0.0, False)
    if t >= CUT2 - FR and not ((CUT_SB - FR <= t < CUT_GO - FR) or (CUT_SB2 - FR <= t < CUT_WIN - FR)):
        bend = 0.0; shake = 0.0; sw = 0.0; sh = 0.0
        if t >= T_SLAM:
            sh = 1.0; bend = 1.0 if t < T_KLAND else 0.85
            shake = 16 * (1 - ramp(t, T_SLAM, T_SLAM + 0.8))
            sw = max(0.0, 1 - (t - T_SLAM) / 0.8)
        return (ABX, bend, shake, sw, sh, True)
    return None

def props_back(cr, t, p, ly):
    if ly != "back": return
    if t < CUT1 - FR:                                      # home: couch, kitten, her
        O.draw_couch(cr, COUCHX, FLOOR_Y - 10)
        O.draw_cat(cr, COUCHX, FLOOR_Y - 10 - O.BENCH_SEAT + 4, s=0.85, t=t, kind="loaf", col="black", look=(0.3, 0.2),
                   blink=0.6 if t < T_TAKE0 else 0.0, sid=2000, swish=0.3)
        q = her_pose(t)
        O.draw_mom(cr, t, q, her_blink(t), s=GS, hair=G_HAIR, dress=G_DRESS, bun=False)
    if in_stands(t):
        draw_fans(cr, t)                                   # the front row around him (behind the wall)
        return
    if t >= CUT2 - FR and not insert(t):
        draw_fans(cr, t); draw_wall(cr, t)
    hs = hoop_state(t)
    if hs:
        O.draw_hoop(cr, hs[0], part="back", t=t, bend=hs[1], shake=hs[2], swish=hs[3], shatter=hs[4], glass=hs[5])
    if t >= CUT2 - FR: draw_defenders(cr, t)
    draw_kid(cr, t)
S.prop(props_back)

def insert(t): return (CUT_SB - FR <= t < CUT_GO - FR) or (CUT_SB2 - FR <= t < CUT_WIN - FR)
def in_stands(t): return CUT2 - FR <= t < CUT_TRO - FR and not insert(t)
FAN_COLS = ((0.90, 0.30, 0.28), (0.98, 0.84, 0.32), (0.45, 0.65, 0.95), (0.97, 0.62, 0.72), (0.55, 0.80, 0.45), (0.80, 0.55, 0.95))
def draw_fans(cr, t):
    """the front row of fans, standing behind the courtside wall (their heads level with his)."""
    for k in range(-14, 16):
        x = AX + k * 230 + 60
        if x < AX - 700 or abs(x - CHAIR) < 190: continue
        h = (k * 2654435761) % 997
        col = FAN_COLS[h % len(FAN_COLS)]
        roar = 1.0 if t >= T_SLAM else 0.0
        bob = (6 + 22 * roar) * abs(math.sin(t * (3 + 6 * roar) + h))
        hx, hy = x, FLOOR_Y - 760 - STAND_UP + 40 * (h % 3 == 0) - bob
        L.sketch_poly(cr, [(x - 70, WALL_TOP + 40), (x - 62, hy + 120), (x - 30, hy + 95), (x + 30, hy + 95), (x + 62, hy + 120),
                           (x + 70, WALL_TOP + 40)], 6, sid=23400 + k % 7, fill=col)
        if roar:                                            # arms up after the dunk
            for d in (-1, 1): sketch_line(cr, [(x + d * 60, hy + 130), (x + d * 110, hy - 70)], 9, sid=23410 + k % 5 + d)
        L.sketch_circle(cr, hx, hy, 80, 7, sid=23420 + k % 9, fill=(0.99, 0.99, 0.98))
        cap = FAN_COLS[(h + 2) % len(FAN_COLS)]
        cr.new_path(); cr.arc(hx, hy, 78, math.pi, 2 * math.pi); cr.close_path(); cr.set_source_rgb(*cap); cr.fill_preserve(); L.stroke_ink(cr, 6)
        L.sketch_rect(cr, hx - 10, hy - 18, hx + 110, hy + 2, 5, sid=23425, fill=cap)
        for d in (-1, 1):
            cr.new_path(); cr.arc(hx + d * 26, hy + 18 + 3 * math.sin(t + h), 8, 0, 2 * math.pi); L.fill_ink(cr); cr.new_path()
        if roar: L.sketch_ellipse(cr, hx, hy + 52, 18, 15, 4, sid=23430, fill=(0.3, 0.1, 0.12))
        else: sketch_line(cr, [(hx - 16, hy + 52), (hx + 16, hy + 52)], 4, sid=23431, amp=0.3)
def draw_wall(cr, t):
    """the courtside wall in front of the front row (from just right of the basket support)."""
    x0, x1 = AX - 760, AX + 6000
    L.sketch_rect(cr, x0, WALL_TOP, x1, FLOOR_Y - 190, 6, sid=23440, fill=(0.14, 0.17, 0.34))
    sketch_line(cr, [(x0, WALL_TOP + 8), (x1, WALL_TOP + 8)], 10, sid=23441, amp=0.3, color=(0.75, 0.62, 0.25))
    for k in range(-1, 8):
        draw_text(cr, "THE FINALS", AX - 420 + k * 760, WALL_TOP + 170, 64, color=(250, 200, 70))

def props_front(cr, t, p, ly):
    if ly != "front": return
    if in_stands(t):
        draw_wall(cr, t)
        hs = hoop_state(t)
        if hs: O.draw_hoop(cr, hs[0], part="back", t=t, bend=hs[1], shake=hs[2], swish=hs[3], shatter=hs[4], glass=hs[5])
        draw_defenders(cr, t); draw_kid(cr, t)
    # the baby
    bp = baby_pos(t, p)
    if bp:
        O.draw_baby(cr, bp[0], bp[1], 0.0, dict(eyes="open", look=bp[2]), t, s=0.8)
        if t < T_SET1 and t >= T_TAKE0: L.draw_grips(cr, p)
        if t < T_TAKE0:
            q = her_pose(t); fx = (q["lfoot"][0] + q["rfoot"][0]) / 2
            cr.save(); cr.translate(fx, FLOOR_Y); cr.scale(GS, GS); cr.translate(-fx, -FLOOR_Y); L.draw_grips(cr, q); cr.restore()
    # the ball, then the front of the rim + net over it
    b = ball_pos(t, p)
    if b and not (CUT_MAG - FR <= t < CUT_MAG1 - FR):
        _, s = stage(t)
        O.draw_basketball(cr, b[0], b[1], r=BALL_R, ang=t * 3.0)
        if T_POP <= t < T_DROP or (SW4 <= t < T_LREL): L.draw_grips(cr, p)
    hs = hoop_state(t)
    if hs:
        O.draw_hoop(cr, hs[0], part="front", t=t, bend=hs[1], shake=hs[2], swish=hs[3], shatter=hs[4], glass=hs[5])
        if hs[4] > 0: O.draw_shards(cr, hs[0] + 5, FLOOR_Y - 1330, t - T_SLAM, n=30)
    # the magazine
    if T_WIND <= t < T_SLAP:
        u = ramp(t, T_WIND, T_SLAP, "linear")
        hd = p["head"]
        x = lerp(CX + 1100, hd[0], u); y = lerp(560, hd[1], u) - 120 * math.sin(math.pi * u)
        O.draw_magazine(cr, x, y, s=0.75, ang=6 * u)
    elif T_SLAP <= t < T_PEEL + 0.05:
        hd = p["head"]; O.draw_magazine(cr, hd[0], hd[1] + 10, s=0.75, ang=0.05); L.draw_grips(cr, p)
    elif T_PEEL + 0.05 <= t < T_MAGDROP:
        mx = (p["lhand"][0] + p["rhand"][0]) / 2; my = (p["lhand"][1] + p["rhand"][1]) / 2
        if CUT_MAG - FR <= t < CUT_MAG1 - FR: mx, my = CX + 150, 930
        O.draw_magazine(cr, mx, my + 40, s=0.75, ang=0.0); L.draw_grips(cr, p)
    elif T_MAGDROP <= t < SW4:
        u = ramp(t, T_MAGDROP, T_MAGDROP + 0.35, "inn")
        O.draw_magazine(cr, lerp(CX + 160, CX + 260, u), lerp(1010, FLOOR_Y - 20, u), s=0.75, ang=lerp(0.0, 1.45, u))
    # the chalk cloud
    if T_CLAP <= t < CUT_SB - FR:
        hp = kid_hands(T_CLAP + 0.05)
        O.draw_chalk_cloud(cr, AX + 170, 760, ramp(t, T_CLAP, T_CLAP + 1.9, "linear"), r=560)
    # confetti
    if CUT_WIN - FR <= t:
        for k in range(8):
            t0 = CUT_WIN - 0.6 + 3.0 * k
            if 0 <= t - t0 < 7: O.draw_confetti(cr, t, t0, AX - 1400, AX + 1800, -300, n=60, seed=3 + k)
    # the trophy
    if CUT_TRO - FR <= t:
        if t < T_FALL0:
            if t < T_HAND0:
                h = kid_hands(t); tx, ty = h[0], h[1]
            elif t < T_HAND1:
                a = kid_hands(T_HAND0); b = ((p["lhand"][0] + p["rhand"][0]) / 2, (p["lhand"][1] + p["rhand"][1]) / 2)
                u = smooth(ramp(t, T_HAND0, T_HAND1)); tx, ty = lerp(a[0], b[0], u), lerp(a[1], b[1], u)
            else:
                tx, ty = ((p["lhand"][0] + p["rhand"][0]) / 2, (p["lhand"][1] + p["rhand"][1]) / 2)
            ang = p.get("lean", 0.0) if t >= T_TIP0 else 0.0
            cr.save(); cr.translate(tx, ty); cr.rotate(ang)
            O.draw_trophy(cr, 0, 600, s=0.55, plaque=PLAQUE)
            cr.restore()
            L.draw_grips(cr, p)
            if t < T_HAND0:
                q = kid_local(t); fx, up, s_ = kid_xf(t)
                cr.save(); cr.translate(fx, FLOOR_Y - up); cr.scale(s_, s_); cr.translate(-fx, -FLOOR_Y); L.draw_grips(cr, q); cr.restore()
        else:
            q = L.pose_with_follow(T_FALL0 - FR)
            hx, hy = (q["lhand"][0] + q["rhand"][0]) / 2, (q["lhand"][1] + q["rhand"][1]) / 2
            a0 = q.get("lean", 0.0)
            sx, sy = hx - 600 * math.sin(a0), hy + 600 * math.cos(a0)
            u = ramp(t, T_FALL0 + 0.1, T_TLAND, "linear")
            bx = lerp(sx, TBASE[0], smooth(u)); by = lerp(sy, TBASE[1], u * u) - 260 * math.sin(math.pi * u) * (1 - u * 0.3)
            ang = lerp(a0, 0.0, smooth(u)) + (0.6 * math.sin(math.pi * u) if u < 1 else 0.0)
            if t > T_TLAND: ang = 0.07 * math.sin((t - T_TLAND) * 18) * math.exp(-(t - T_TLAND) * 4)
            cr.save(); cr.translate(bx, by); cr.rotate(ang)
            O.draw_trophy(cr, 0, 0, s=0.55, plaque=PLAQUE)
            cr.restore()
S.prop(props_front)

if __name__ == "__main__":
    print(f"end {T_END:.2f}", file=sys.stderr)
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        S.build()
        import cairo
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, L.W, L.H)
        for a in sys.argv[2:]:
            tt = float(a); L.render_frame(tt, surf); surf.write_to_png(f"still_{tt:05.2f}.png")
    else:
        S.render("day019.mp4")
