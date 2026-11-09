"""Day 18 (re-cut, Justin's direction): @_taun_taun "Hit the lottery for 10 million and get your family back"
(Instagram, day 17 reel, 4 likes).
His empty house (no couch) -> the corner store: one $1 ticket, the draw on the store TV, every number matches,
JACKPOT, the clerk faints and comes back up with a giant check -> he thinks of the family photo -> her place: the check
held over his head under her window; she isn't impressed and shuts the curtain; the check droops -> he pulls out his
game controller and drops it in the trash -> a ring box, one knee -> she comes out with the baby: yes, a hug -> home:
they carry the couch back in together, sit down; the door creaks: the black kitten wanders in and curls up next to
them on the couch -> the ask on the TV. See BEATS.md.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
import character as C
from ltcd import Track, ramp, lerp, pulse, FLOOR_Y
from ink import smooth, sketch_line, draw_text

HERE = os.path.dirname(os.path.abspath(__file__))
FR = 1 / 30

# ================================================================ places
IX = 1300000.0                                      # his house, inside (day 17)
TVX = IX + 650.0; CLOCK = (IX - 150.0, 560.0); OUTLET = (IX + 1010.0, FLOOR_Y - 230.0)
SINKX = IX + 1240.0; FRIDGEX = IX + 1600.0; DOORX = IX - 900.0; COUCHX = IX - 150.0
SEAT_L, SEAT_R = COUCHX - 175.0, COUCHX + 175.0
SX = 2600000.0                                      # the corner store
CX = SX + 420.0                                     # the counter (clerk behind it)
TV = (SX - 480.0, 640.0)                            # the lotto TV on the wall
HX = 2900000.0                                      # her place (house front)
WIN, DOOR = O.her_house_geom(HX)
WINX = (WIN[0] + WIN[2]) / 2
TRASH = HX - 1380.0

# ================================================================ timeline
T_READ = 0.4; T_LOOKC = 1.75; T_US0 = 2.3; T_UP = 2.55; T_RUN = 2.85; CUT1 = 3.4
T_ARR = 4.1; T_DIG1 = 4.4; T_POP1 = T_DIG1 + 1.4; T_SLAP = 6.0; T_TIX0, T_TIX1 = 6.35, 6.75
T_TVON = 7.1
BALLS = [7.9, 9.0, 10.1, 11.2, 12.3, 14.55]
CUT_TIX = 13.25; CUT_TV = 14.15; T_JACK = 15.05
CUT_REACT = 16.2; T_CURL = 16.75; T_GRIN = 17.15; T_FAINT = 16.95
T_CHECKUP = 18.25; CK0, CK1 = 18.7, 19.1
T_THINK = 19.8; T_THINK1 = 21.3; T_RUN2 = 21.4; CUT2 = 22.0
T_ARR2 = 22.8; T_LIFT = 23.0
T_CUR_OPEN = 23.8; T_SHE_LOOK = 24.8; T_SHAKE = 25.6; T_CUR_SHUT = 26.3
T_LOWER = 26.9; T_DROOP0, T_DROOP1 = 27.2, 28.0; T_SETDOWN = 28.3
T_LOOKT = 28.9; T_US1 = 29.4
T_DIG2 = 29.8; T_POP2 = T_DIG2 + 1.4; T_LOOKPAD = 31.35
T_WALKT0, T_WALKT1 = 32.2, 32.9; T_LID0 = 32.95; T_DROP = 33.25; T_LID1 = 33.6
T_PEEK0, T_PEEK1 = 33.7, 35.8
T_BACK0, T_BACK1 = 34.1, 34.8
T_DIG3 = 35.0; T_POP3 = T_DIG3 + 1.4; T_KNEEL = 36.5; T_OPENBOX = 36.95
T_CUR_FLY = 37.6; T_DOOR = 38.0; SW0, SW1 = 38.2, 39.5
T_RING = 39.8; T_YES = 40.4; T_STANDUP = 40.75; T_HUG = 41.15
CUT3 = 43.3
T_DOORIN = 43.4; CA0, CA1 = 43.6, 45.5; T_SETC = 45.6; T_SIT = 46.15; T_BABY = 46.6; T_ARM = 47.2
T_CREAK = 48.0; KW0, KW1 = 48.3, 49.8; T_HOP = 49.85; T_CURL_C = 50.4
T_LOOKCAT = 50.6; T_LOOKHER = 51.2
T_PUSH = 51.8; T_TEXT = 52.4
T_END = 61.6

# ================================================================ poses
def P(name, **kw): L.POSES[name] = kw
P("floor_pad", **dict(L.POSES["sit_floor"], lelb=(470, 1210), lhand=(515, 1250), relb=(610, 1210), rhand=(570, 1250), lhand_t="grip", rhand_t="grip"))
P("offer_r", relb=(680, 900), rhand=(800, 880), rhand_t="grip")
P("ticket", lelb=(465, 990), lhand=(478, 930), relb=(615, 990), rhand=(602, 930), lhand_t="grip", rhand_t="grip")
P("check_up", lelb=(420, 720), lhand=(400, 560), relb=(660, 720), rhand=(680, 560), lhand_t="grip", rhand_t="grip")
P("check_chest", lelb=(450, 960), lhand=(400, 900), relb=(630, 960), rhand=(680, 900), lhand_t="grip", rhand_t="grip")
P("hold_r", relb=(630, 960), rhand=(660, 900), rhand_t="grip")
P("kneel", head=(560, 880), neck=(560, 1005), hip=(545, 1290), lknee=(470, FLOOR_Y - 20), lfoot=(330, FLOOR_Y), rknee=(660, 1300),
  rfoot=(680, FLOOR_Y), lelb=(500, 1150), lhand=(520, 1250), relb=(650, 1120), rhand=(740, 1060), rhand_t="grip",
  lfoot_dir=-0.9, rfoot_dir=0.6, nowalk=1.0)
P("hug_r", lelb=(600, 900), lhand=(720, 860), relb=(660, 960), rhand=(760, 940), lhand_t="open", rhand_t="open", lean=0.08)
P("carry", lelb=(455, 980), lhand=(470, 1050), relb=(625, 980), rhand=(610, 1050), lhand_t="grip", rhand_t="grip")
P("couch_sit", **dict(head=(540, 752), neck=(540, 878), hip=(540, 1228), lknee=(400, 1300), rknee=(680, 1300), lfoot=(430, FLOOR_Y),
  rfoot=(650, FLOOR_Y), lelb=(465, 1075), lhand=(462, 1200), relb=(615, 1075), rhand=(618, 1200), lfoot_dir=-0.5, rfoot_dir=0.5, nowalk=1.0))
P("couch_arm", **dict(L.POSES["couch_sit"], lelb=(430, 830), lhand=(290, 820), lhand_t="mitt"))
# hers
P("g_hold", lelb=(470, 1030), lhand=(480, 1100), relb=(610, 1030), rhand=(600, 1100), lhand_t="grip", rhand_t="grip")
P("g_hug", lelb=(470, 1030), lhand=(490, 1100), relb=(560, 920), rhand=(430, 880), lhand_t="grip", rhand_t="open", lean=-0.06)
P("g_sit_hold", **dict(L.POSES["couch_sit"], head=(540, 740), neck=(540, 862), hip=(540, 1205), lelb=(470, 1030), lhand=(480, 1100),
  relb=(610, 1030), rhand=(600, 1100), lhand_t="grip", rhand_t="grip"))

# ================================================================ scene
S = M.Scene(start_body="floor_pad", start_face="deadpan", x0=IX - 360)
S.auto_blinks = True
S.floor = False
S.card("_taun_taun", "Hit the lottery for 10 million and get your family back", "4", t0=0.3)
CAM0 = (IX + 120, 880, 0.9)
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

# ---------------------------------------------------------------- A: the empty house
for k in range(5): S.sfx(0.1 + k * 0.38, "tick", 0.018)
S.set(0.0, "floor_pad", "deadpan", dur=0.0, turn=1.0, look=(1.0, -0.3), lid=0.2)
S.set(T_READ, "floor_pad", "deadpan", dur=0.3, turn=0.3, look=(0.7, -0.9), tilt=-0.05)
def read_hk(tt, p):
    if T_READ + 0.3 <= tt < T_LOOKC - 0.1:
        k = (tt - T_READ - 0.3) / 0.5; u = k % 1.0
        p["look"] = (0.4 + 0.5 * smooth(u), -0.92 + 0.1 * int(k % 2))
    return p
S.hook(read_hk)
S.set(T_LOOKC, "floor_pad", "dead_stare", dur=0.35, turn=-0.7, look=(-1.0, 0.1))          # the empty spot where the couch was
S.set(T_US0, "floor_pad", "resigned", dur=0.3, turn=0.0, look=(0.0, 0.0))
S.set(T_UP, "stand", "deadpan", dur=0.3, look=(0.9, 0.0), turn=0.5)
S.set(T_RUN, "stand", "deadpan", dur=0.15, run=1.0, look=(1.0, 0.0), turn=1.0, lean=0.1)
S.xkeys.append((T_RUN, IX + 700, CUT1 - T_RUN, "inn")); S.x = IX + 700
S.sfx(T_RUN, "whoosh", 0.05)

# ---------------------------------------------------------------- B: the corner store
CAM_ST = (SX, 760, 0.7)
S.cut(CUT1 - FR, cam=CAM_ST, x=SX - 1150 - 540)
S.set(CUT1 - FR, "stand", "deadpan", dur=0.0, run=1.0, look=(1.0, 0.0), turn=1.0, lean=0.1)
S.xkeys.append((CUT1, SX - 80 - 540, T_ARR - CUT1, "out")); S.x = SX - 80 - 540
S.set(T_ARR - 0.1, "stand", "deadpan", dur=0.12, ease="snap", stretch=-0.25, run=0.0, turn=0.6, look=(0.9, 0.0))
S.set(T_ARR + 0.1, "stand", "deadpan", dur=0.25, ease="back", turn=0.6, look=(0.9, 0.0)); S.sfx(T_ARR - 0.1, "skid", 0.05, dur=0.3)
dig_pull(T_DIG1, "offer_r", look=(0.9, 0.2), turn=0.6)
S.set(T_SLAP, "offer_r", "deadpan", dur=0.12, ease="snap", turn=0.6, look=(0.9, 0.3), rhand=(840, 1000))
S.sfx(T_SLAP + 0.1, "pat", 0.08)
S.set(T_TIX0, "offer_r", "deadpan", dur=0.25, turn=0.6, look=(0.9, 0.0), rhand=(800, 900))
S.set(T_TIX1 + 0.05, "ticket", "deadpan", dur=0.35, turn=0.3, look=(0.0, 0.8))
# the draw
S.sfx(T_TVON, "boop", 0.06)
S.set(T_TVON + 0.15, "ticket", "deadpan", dur=0.35, turn=-0.4, look=(-0.9, -0.4))
S.camera(T_TVON + 0.1, SX - 280, 760, 0.95, 0.8)
for i, b in enumerate(BALLS[:5]):
    S.sfx(b, "pop", 0.06)
    S.set(b + 0.3, "ticket", "dead_stare", dur=0.2, turn=-0.1, look=(0.0, 0.9), sweat=0.2 * i, eyescale=1.0 + 0.04 * i)   # checks the ticket
    S.sfx(b + 0.45, "tick", 0.03)
    S.set(b + 0.7, "ticket", "dead_stare", dur=0.2, turn=-0.4, look=(-0.9, -0.4), sweat=0.2 * i, eyescale=1.0 + 0.05 * i,
          quiver=0.25 * i)
for k, tt in enumerate([12.9, 13.35, 13.75, 14.1, 14.35]): S.sfx(tt, "thud", 0.035 + 0.008 * k)
# insert: the ticket in his trembling hands (5 circled)
S.cut(CUT_TIX - FR, cam=(SX - 80, 905, 4.6))
S.cut(CUT_TV - FR, cam=(TV[0], TV[1] + 40, 1.7))
S.sfx(BALLS[5], "pop", 0.08)
S.sfx(T_JACK, "ding", 0.09); S.sfx(T_JACK + 0.05, "twinkle", 0.06); S.sfx(T_JACK + 0.3, "ding", 0.06)
S.flash(T_JACK, 0.35, (1.0, 0.95, 0.6))
# his reaction + the clerk
S.cut(CUT_REACT - FR, cam=(SX + 80, 800, 0.85))
S.set(CUT_REACT - FR, "ticket", "dead_stare", dur=0.0, turn=0.0, look=(0.0, 0.0), sweat=0.6, eyescale=1.2)
S.set(T_CURL, "ticket", "dead_stare", dur=0.08, ease="snap", turn=0.0, look=(0.0, 0.0), eyescale=1.35, curl_up=1.0, pupil=0.6)
S.sfx(T_CURL, "boing", 0.06)
S.set(T_GRIN, "ticket", "delighted", dur=0.6, turn=0.0, mouth="grin", smile=1.0, open=0.5, curl_up=0.0, eyes="normal", eyescale=1.1)
S.sfx(T_FAINT + 0.35, "thud", 0.08)
S.set(T_CHECKUP + 0.2, "ticket", "delighted", dur=0.3, turn=0.6, look=(0.9, -0.3), mouth="grin", smile=1.0, open=0.5)
S.sfx(T_CHECKUP, "pop", 0.08)
S.set(CK1, "check_up", "delighted", dur=0.3, ease="back", look=(0.0, -0.9), mouth="grin", smile=1.0, open=0.6)
S.camera(CK1, SX + 30, 760, 0.75, 0.6)
# he thinks of them
S.set(T_THINK, "check_chest", "resigned", dur=0.6, look=(0.6, -0.9), smile=0.1, tilt=0.06)
S.sfx(T_THINK, "twinkle", 0.03)
S.set(T_THINK1 - 0.4, "check_chest", "deadpan", dur=0.3, look=(1.0, 0.0), brow=-0.3, turn=0.6)
S.set(T_RUN2, "check_up", "deadpan", dur=0.15, run=1.0, look=(1.0, 0.0), turn=1.0, lean=0.1, brow=-0.3)
S.xkeys.append((T_RUN2, SX + 1000, CUT2 - T_RUN2, "inn")); S.x = SX + 1000
S.sfx(T_RUN2, "whoosh", 0.05)

# ---------------------------------------------------------------- C: her place
CAM_H = (HX - 700, 860, 0.72)
S.cut(CUT2 - FR, cam=CAM_H, x=HX - 2100 - 540)
S.set(CUT2 - FR, "check_up", "deadpan", dur=0.0, run=1.0, look=(1.0, 0.0), turn=1.0, lean=0.1, brow=-0.3)
S.xkeys.append((CUT2, HX - 1000 - 540, T_ARR2 - CUT2, "out")); S.x = HX - 1000 - 540
S.set(T_ARR2 - 0.1, "check_up", "deadpan", dur=0.12, ease="snap", run=0.0, stretch=-0.2, turn=0.6, look=(0.9, -0.4))
S.set(T_LIFT, "check_up", "deadpan", dur=0.3, ease="back", turn=0.5, look=(0.9, -0.5), hop=0)
S.sfx(T_CUR_OPEN, "whoosh", 0.04)
S.set(T_CUR_OPEN + 0.4, "check_up", "hopeful", dur=0.3, turn=0.5, look=(0.9, -0.5), smile=0.4, mouth="auto")
S.sfx(T_CUR_SHUT, "whoosh", 0.05)
S.set(T_CUR_SHUT + 0.2, "check_up", "dead_stare", dur=0.15, ease="snap", turn=0.5, look=(0.9, -0.5), eyescale=1.15)
S.set(T_LOWER, "check_chest", "resigned", dur=0.5, turn=0.2, look=(0.2, 0.6))
S.sfx(T_DROOP0, "slide_down", 0.03, dur=0.8)
S.set(T_SETDOWN, "stand", "resigned", dur=0.35, turn=0.0, look=(0.3, 0.7))
S.sfx(T_SETDOWN + 0.3, "thud", 0.03)
S.set(T_LOOKT, "stand", "resigned", dur=0.3, turn=-0.6, look=(-1.0, 0.2))
S.set(T_US1, "stand", "deadpan", dur=0.3, turn=0.0, look=(0.0, 0.0))
dig_pull(T_DIG2, "hold_r", look=(0.3, 0.6))
S.set(T_LOOKPAD, "hold_r", "sad", dur=0.4, look=(0.3, 0.6), smile=-0.2, lid=0.35)
S.set(T_WALKT0 - 0.1, "hold_r", "deadpan", dur=0.2, turn=-0.7, look=(-1.0, 0.3))
S.walk_to(T_WALKT0, TRASH + 230 - 540, T_WALKT1 - T_WALKT0)
S.set(T_LID0 - 0.15, "point_left", "deadpan", dur=0.2, turn=-0.7, look=(-0.8, 0.6), lhand=(330, 1010), lhand_t="grip",
      relb=(560, 960), rhand=(470, 880), rhand_t="grip")
S.sfx(T_LID0, "clack", 0.05)
S.set(T_DROP, "point_left", "deadpan", dur=0.12, turn=-0.7, look=(-0.8, 0.8), lhand=(330, 1010), lhand_t="grip",
      relb=(470, 880), rhand=(370, 860), rhand_t="open")
S.sfx(T_DROP + 0.25, "bonk", 0.06)
S.set(T_LID1, "stand", "deadpan", dur=0.25, turn=-0.5, look=(-0.6, 0.6))
S.sfx(T_LID1 + 0.05, "clack", 0.07)
S.set(T_BACK0 - 0.1, "stand", "deadpan", dur=0.2, turn=0.6, look=(0.9, -0.3))
S.walk_to(T_BACK0, HX - 920 - 540, T_BACK1 - T_BACK0)
dig_pull(T_DIG3, "hold_r", look=(0.3, 0.5))
S.set(T_KNEEL, "kneel", "deadpan", dur=0.35, turn=0.6, look=(0.9, -0.6))
S.sfx(T_KNEEL + 0.3, "thud", 0.03)
S.sfx(T_OPENBOX, "ding", 0.06)
S.set(T_OPENBOX + 0.2, "kneel", "hopeful", dur=0.4, turn=0.6, look=(0.9, -0.6), smile=0.3, mouth="auto")
S.sfx(T_CUR_FLY, "whoosh", 0.05)
S.set(T_CUR_FLY + 0.2, "kneel", "surprised", dur=0.15, turn=0.6, look=(0.9, -0.7))
S.sfx(T_DOOR, "squeak", 0.03)
S.camera(T_CUR_FLY, HX - 520, 860, 0.72, 1.2)
S.set(SW0 + 0.3, "kneel", "hopeful", dur=0.3, turn=0.7, look=(1.0, -0.2), smile=0.3, mouth="auto")
S.set(T_RING, "kneel", "hopeful", dur=0.3, turn=0.7, look=(0.9, -0.6), smile=0.4, mouth="auto")
S.set(T_YES + 0.15, "kneel", "happy", dur=0.3, turn=0.7, look=(0.9, -0.6), smile=0.8)
S.set(T_STANDUP, "stand", "happy", dur=0.35, turn=0.6, look=(0.9, -0.2), smile=0.8)
S.set(T_HUG, "hug_r", "happy", dur=0.35, turn=0.7, eyes="closed", smile=0.9, tilt=0.12)
S.camera(T_HUG - 0.2, HX - 760, 900, 0.85, 0.8)
S.sfx(T_HUG + 0.1, "pat", 0.04)

# ---------------------------------------------------------------- D: home, with the couch
def his_carry_x(t): return lerp(DOORX - 160, COUCHX + 480, smooth(ramp(t, CA0, CA1)))       # his body centre
S.cut(CUT3 - FR, cam=(IX - 700, 880, 0.75), x=DOORX - 160 - 540)
S.camera(CA0, IX - 330, 880, 0.75, CA1 - CA0)
S.set(CUT3 - FR, "carry", "happy", dur=0.0, turn=-0.6, look=(-0.9, 0.2), smile=0.6, show=0.0)
S.set(T_DOORIN + 0.05, "carry", "happy", dur=0.0, turn=-0.6, look=(-0.9, 0.2), smile=0.6, show=1.0)
S.xkeys.append((CA0, COUCHX + 480 - 540, CA1 - CA0, "smooth")); S.x = COUCHX + 480 - 540
S.sfx(T_DOORIN, "squeak", 0.03)
for k in range(5): S.sfx(CA0 + 0.2 + k * 0.38, "step", 0.03)
S.sfx(T_SETC, "thud", 0.07)
S.set(T_SETC, "stand", "happy", dur=0.3, turn=-0.4, look=(-0.6, 0.4), smile=0.6)
S.xkeys.append((T_SIT - 0.3, SEAT_R - 540, 0.4)); S.x = SEAT_R - 540
S.set(T_SIT, "couch_sit", "happy", dur=0.35, turn=-0.3, look=(-0.6, 0.2), smile=0.6)
S.sfx(T_SIT + 0.3, "thud", 0.03)
S.set(T_ARM, "couch_arm", "happy", dur=0.5, turn=-0.4, look=(-0.6, 0.2), smile=0.7, lid=0.2)
S.sfx(T_CREAK, "squeak", 0.03)
S.set(T_CREAK + 0.3, "couch_arm", "happy", dur=0.3, turn=-0.7, look=(-1.0, 0.0), smile=0.5)
S.set(T_LOOKCAT, "couch_arm", "happy", dur=0.3, turn=-0.4, look=(-0.6, 0.8), smile=0.8)
S.set(T_LOOKHER, "couch_arm", "happy", dur=0.3, turn=-0.3, look=(0.0, 0.0), smile=0.9, eyes="closed")
for k in range(3): S.sfx(KW0 + 0.1 + k * 0.45, "tiptoe", 0.02)
S.sfx(KW0 + 0.3, "squeak", 0.015)
S.sfx(T_HOP + 0.25, "pat", 0.03)
S.camera(T_CREAK, IX - 420, 900, 0.85, 0.6)
S.camera(T_PUSH, TVX, FLOOR_Y - 10 - 600, 1.9, 1.4)
S.flash(T_TEXT, 0.25)
S.sfx(T_TEXT, "boop", 0.05)
S.camera(T_TEXT + 1.0, TVX, FLOOR_Y - 10 - 600, 1.95, 7.0)
S.blink(1.2, 9.6, 21.0, 24.0, 30.2, 34.2, 39.0, 45.0, 49.0)
S.t = T_END

# ================================================================ HER (on his rig, scaled)
G_HAIR, G_DRESS = (0.62, 0.28, 0.16), (0.30, 0.66, 0.66)
GS = 0.92
GXK = [(0.0, WINX, 0), (SW0 - 0.01, (DOOR[0] + DOOR[2]) / 2, 0.001, "linear"), (SW0, HX - 640, SW1 - SW0, "smooth"),
       (CUT3 - FR, COUCHX - 480, 0.001, "linear"), (CA0, COUCHX - 480 + (COUCHX + 480 - (DOORX + 100)), 0.001, "linear")]
# while carrying she walks in step with the couch (set below by function)
GW = Track([(0.0, 0.0, 0), (SW0, 1.0, 0.1), (SW1 - 0.15, 0.0, 0.15), (CA0, 1.0, 0.1), (CA1 - 0.15, 0.0, 0.15)])
GK = [(0.0, L.pose("g_hold", "neutral", turn=-0.6, look=(-0.9, 0.3)), 0)]
def gk(t, body, face, dur=0.25, ease="smooth", **kw): GK.append((t, L.pose(body, face, **kw), dur, ease))
gk(T_CUR_OPEN + 0.3, "g_hold", "neutral", dur=0.3, turn=-0.7, look=(-1.0, 0.4))
gk(T_SHE_LOOK, "g_hold", "annoyed", dur=0.3, turn=-0.7, look=(-0.9, -0.2), lid=0.5)
gk(T_SHE_LOOK + 0.5, "g_hold", "annoyed", dur=0.3, turn=-0.7, look=(-1.0, 0.4), lid=0.5)
gk(T_SHAKE + 0.5, "g_hold", "annoyed", dur=0.3, turn=-0.3, look=(0.0, 0.0), lid=0.5)
gk(T_PEEK0, "g_hold", "sad", dur=0.3, turn=-0.8, look=(-1.0, 0.3))
gk(SW0, "g_hold", "surprised", dur=0.2, turn=-1.0, look=(-1.0, 0.4), open=0.2)
gk(SW1 - 0.1, "g_hold", "surprised", dur=0.2, turn=-0.8, look=(-0.6, 0.8), open=0.3)
gk(T_RING, "g_hold", "happy", dur=0.3, turn=-0.8, look=(-0.6, 0.6), smile=0.6)
gk(T_YES, "g_hold", "delighted", dur=0.2, turn=-0.8, look=(-0.6, 0.5))
gk(T_HUG, "g_hug", "happy", dur=0.35, turn=-0.8, eyes="closed", smile=0.9, tilt=-0.12)
gk(CUT3 - FR, "carry", "happy", dur=0.0, turn=0.6, look=(0.9, 0.2), smile=0.6)
gk(T_SETC, "stand", "happy", dur=0.3, turn=0.4, look=(0.6, 0.4), smile=0.6)
gk(T_SIT, "couch_sit", "happy", dur=0.35, turn=0.3, look=(0.6, 0.3), smile=0.6)
gk(T_BABY, "g_sit_hold", "happy", dur=0.35, turn=0.3, look=(0.3, 0.5), smile=0.7)
gk(T_ARM + 0.2, "g_sit_hold", "happy", dur=0.4, turn=0.4, look=(0.7, -0.2), smile=0.8, tilt=0.12, head=(570, 745), neck=(550, 862))
gk(T_CREAK + 0.3, "g_sit_hold", "happy", dur=0.3, turn=-0.6, look=(-1.0, 0.0), smile=0.6)
gk(T_LOOKCAT, "g_sit_hold", "happy", dur=0.3, turn=0.2, look=(0.6, 0.8), smile=0.9)
gk(T_LOOKHER, "g_sit_hold", "happy", dur=0.3, turn=0.4, look=(0.7, -0.2), smile=0.9, eyes="closed", tilt=0.12, head=(570, 745), neck=(550, 862))
GKT = Track(GK)

def g_x(t):
    if CUT3 - FR <= t < T_SETC:
        return his_carry_x(t) - 960.0
    if T_SETC <= t:
        return lerp(his_carry_x(T_SETC) - 960.0, SEAT_L, smooth(ramp(t, T_SIT - 0.3, T_SIT + 0.1)))
    if t < SW0: return WINX if t < T_CUR_FLY else WINX
    return lerp((DOOR[0] + DOOR[2]) / 2, HX - 640, smooth(ramp(t, SW0, SW1)))

def g_base(t):
    p = dict(GKT.at(t))
    x = g_x(t); ox = x - 540
    for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1])
    wk = GW.at(t)
    v = (g_x(t + 0.03) - g_x(t - 0.03)) / 0.06; d = 1 if v > 1 else (-1 if v < -1 else 0)
    if wk > 0.01 and abs(v) > 20:
        ph = t * 2 * math.pi * 1.6
        hipx, hipy = p["hip"]
        for side, off in (("l", 0.0), ("r", math.pi)):
            s_ = math.sin(ph + off); lf = max(0.0, math.cos(ph + off)) * 30
            foot = (hipx + 52 * s_, FLOOR_Y - lf); knee = ((hipx + foot[0]) / 2 + d * 22, (hipy + FLOOR_Y) / 2 - lf * 0.6)
            p[side + "foot"] = lerp(p[side + "foot"], foot, wk); p[side + "knee"] = lerp(p[side + "knee"], knee, wk)
        bob = 8 * abs(math.sin(ph)) * wk
        for k in ("head", "neck", "hip", "lelb", "relb", "lhand", "rhand"): p[k] = (p[k][0], p[k][1] + bob)
        if d: p["lfoot_dir"] = p["rfoot_dir"] = 0.9 * d
    return p
def g_pose(t):
    p = g_base(t); q = g_base(t - 0.08)
    hp, hq = p["hip"], q["hip"]
    for j in ("head", "lelb", "relb", "lhand", "rhand"):
        p[j] = (hp[0] + 0.65 * (p[j][0] - hp[0]) + 0.35 * (q[j][0] - hq[0]), hp[1] + 0.65 * (p[j][1] - hp[1]) + 0.35 * (q[j][1] - hq[1]))
    return L.constrain(p)
def foot_c(p): return (p["lfoot"][0] + p["rfoot"][0]) / 2
def scale_pt(p, pt):
    fx = foot_c(p); return (fx + (pt[0] - fx) * GS, FLOOR_Y + (pt[1] - FLOOR_Y) * GS)
def g_blink(t):
    for b in (25.2, 30.0, 36.0, 40.9, 47.6, 50.2):
        if b <= t < b + 0.16: return math.sin(math.pi * (t - b) / 0.16)
    return 0.0
def g_scene(t):
    """where she is: 'window' (inside, seen through the window), 'out' (outside), 'home', or None."""
    if CUT2 - FR <= t < CUT3 - FR:
        if t < T_CUR_FLY + 0.3: return "window"
        if t < SW0: return None
        return "out"
    if t >= CUT3 - FR: return "home"
    return None

def draw_her(cr, t):
    q = g_pose(t)
    O.draw_mom(cr, t, q, g_blink(t), s=GS, hair=G_HAIR, dress=G_DRESS, bun=False)
    if baby_with_her(t):
        hc = scale_pt(q, ((q["lhand"][0] + q["rhand"][0]) / 2, (q["lhand"][1] + q["rhand"][1]) / 2))
        if T_HUG <= t < CUT3:
            hc = scale_pt(q, q["lhand"])
        O.draw_baby(cr, hc[0] + 10, hc[1] - 15, 0.0, dict(eyes="open", look=(-0.8, -0.2)) if t < CUT3 else dict(eyes="sleep"), t, s=0.8)
        fx = foot_c(q); cr.save(); cr.translate(fx, FLOOR_Y); cr.scale(GS, GS); cr.translate(-fx, -FLOOR_Y); L.draw_grips(cr, q); cr.restore()
def baby_with_her(t):
    if g_scene(t) in ("window", "out"): return True
    return t >= T_BABY

# ================================================================ the clerk (behind the counter)
CLERK_HAIR, CLERK_VEST = (0.55, 0.55, 0.58), (0.90, 0.35, 0.30)
def clerk_pose(t):
    if t < T_TIX0 - 0.3: body, kw = "stand", dict(turn=-0.5, look=(-0.8, 0.0))
    elif t < T_TIX1 + 0.3: body, kw = "point_left", dict(turn=-0.6, look=(-0.9, 0.3), lhand=(330, 900), lhand_t="grip")
    elif t < T_TVON + 0.2: body, kw = "stand", dict(turn=-0.5, look=(-0.8, 0.0))
    elif t < CUT_REACT: body, kw = "stand", dict(turn=-0.7, look=(-1.0, -0.6))
    elif t < T_FAINT: body, kw = "stand", dict(turn=-0.5, look=(-0.8, 0.0), eyescale=1.2, mouth="o", open=0.6)
    elif t < T_CHECKUP: body, kw = "stand", dict(eyes="x", mouth="wavy")
    elif t < CK1 + 0.1: body, kw = "check_up", dict(turn=-0.5, look=(-0.8, 0.0), smile=0.6)
    else: body, kw = "stand", dict(turn=-0.5, look=(-0.8, 0.0), smile=0.7)
    p = L.pose(body, "neutral", **kw)
    ox = CX + 80 - 540
    drop = 0.0
    if t >= T_FAINT: drop = 900 * smooth(ramp(t, T_FAINT, T_FAINT + 0.35)) * (1 - smooth(ramp(t, T_CHECKUP - 0.25, T_CHECKUP)))
    for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1] + drop)
    return L.constrain(p), drop
def clerk_layer(cr, t, p, ly):
    if ly != "back" or not (CUT1 - FR <= t < CUT2 - FR): return
    q, drop = clerk_pose(t)
    cr.save(); cr.rectangle(CX - 600, -9000, 1200, 9000 + FLOOR_Y - 480); cr.clip()
    O.draw_mom(cr, t, q, 0.0, s=0.95, hair=CLERK_HAIR, dress=CLERK_VEST, bun=True)
    cr.restore()
    O.draw_store_counter(cr, CX)
    if T_SLAP + 0.1 <= t < T_TIX1:                                  # the dollar on the counter
        O.sketch_rect(cr, CX - 470, FLOOR_Y - 520, CX - 330, FLOOR_Y - 480, 4, sid=22400, fill=(0.70, 0.88, 0.62))
    if T_TIX0 <= t < T_TIX1:                                         # the ticket, from her hand to his
        u = smooth(ramp(t, T_TIX0, T_TIX1)); a = scale_pt(q, q["lhand"]) if False else (q["lhand"][0], q["lhand"][1])
        O.draw_ticket(cr, lerp(a[0], p["rhand"][0], u), lerp(a[1], p["rhand"][1], u) + 20, s=0.45)
    if CK0 - 0.6 <= t < CK0:                                         # she pops up with the check
        O.draw_big_check(cr, (q["lhand"][0] + q["rhand"][0]) / 2, min(q["lhand"][1], q["rhand"][1]) - 150, s=0.6)
S.prop(clerk_layer)

# ================================================================ backgrounds
def world(cr, t):
    if t < CUT1 - FR or t >= CUT3 - FR:
        home = t >= CUT3 - FR
        door = 0.0
        if home:
            door = max(smooth(ramp(t, T_DOORIN - 0.1, T_DOORIN + 0.15)) * (1 - smooth(ramp(t, CA1 - 0.2, CA1 + 0.3))),
                       smooth(ramp(t, T_CREAK, T_CREAK + 0.4)) * (1 - smooth(ramp(t, KW1 - 0.2, KW1 + 0.3))))
        O.draw_room(cr, t, IX - 3000, IX + 3000, door_x=DOORX, door_open=door, frame_x=IX - 450,
                    frame_fall=0.0 if home else 1.0, kitchen_x=IX + 1000)
        O.draw_wall_clock(cr, *CLOCK, hour=7.0, minute=20.0)
        O.draw_outlet(cr, *OUTLET)
        sketch_line(cr, [(TVX + 280, FLOOR_Y - 330), (OUTLET[0] - 10, FLOOR_Y - 250), (OUTLET[0], OUTLET[1])], 5, sid=20200, amp=0.4)
        O.draw_tv(cr, TVX, FLOOR_Y - 10, t, screen="text" if t >= T_TEXT else ("off" if home else "game"))
        O.draw_sink_counter(cr, SINKX, FLOOR_Y - 10, n=25, t=t)
        O.draw_fridge(cr, FRIDGEX, FLOOR_Y - 10, photo=1.0)
        if not home:                                                       # the controller he leaves on the floor
            pass
        return
    if t < CUT2 - FR:
        O.draw_store_inside(cr, t, SX - 4000, SX + 4000)
        if t < CUT_TIX - FR or t >= CUT_TV - FR:
            shown = 0.0 if t < BALLS[0] else sum(min(1.0, max(0.0, (t - b) / 0.3)) for b in BALLS)
            jack = 1.0 if t >= T_JACK else 0.0
            fl = (1.0 if int((t - T_JACK) * 6) % 2 == 0 else 0.0) if T_JACK <= t < CUT_REACT + 3 else 0.0
            if t >= T_TVON: O.draw_lotto_tv(cr, TV[0], TV[1], t, shown=shown, jackpot=jack, flash=fl)
            else: O.draw_lotto_tv(cr, TV[0], TV[1], t, shown=0, jackpot=0) if False else _tv_off(cr)
        return
    O.draw_street(cr, t, HX - 6000, HX + 6000)
    O.draw_her_house(cr, HX, part="inside")
def _tv_off(cr):
    w, h = 560, 380; x, y = TV
    sketch_line(cr, [(x, y - h / 2 - 140), (x, y - h / 2)], 8, sid=22160, amp=0.2)
    O.sketch_rect(cr, x - w / 2 - 22, y - h / 2 - 22, x + w / 2 + 22, y + h / 2 + 22, 7, sid=22161, fill=(0.14, 0.14, 0.18))
S.background(world)

def curtain(t):
    if t < T_CUR_OPEN: return 1.0
    if t < T_CUR_SHUT: return 1.0 - smooth(ramp(t, T_CUR_OPEN, T_CUR_OPEN + 0.45))
    if t < T_PEEK0: return smooth(ramp(t, T_CUR_SHUT, T_CUR_SHUT + 0.3))
    if t < T_CUR_FLY: return 1.0 - 0.18 * smooth(ramp(t, T_PEEK0, T_PEEK0 + 0.3)) * (1 - smooth(ramp(t, T_PEEK1, T_PEEK1 + 0.3)))
    return 1.0 - smooth(ramp(t, T_CUR_FLY, T_CUR_FLY + 0.25))
def her_door(t):
    return smooth(ramp(t, T_DOOR, T_DOOR + 0.25)) * (1 - smooth(ramp(t, SW0 + 0.8, SW0 + 1.2)))

def house_layer(cr, t, p, ly):
    """her house: the inside, her in the window (clipped), the wall, the curtains, the door; the trash can."""
    if ly != "back" or not (CUT2 - FR <= t < CUT3 - FR): return
    if g_scene(t) == "window":
        cr.save(); cr.rectangle(WIN[0], WIN[1], WIN[2] - WIN[0], WIN[3] - WIN[1]); cr.clip()
        draw_her(cr, t)
        cr.restore()
    if T_PEEK0 <= t < T_CUR_FLY:                                          # one eye in the gap of the curtain
        k = smooth(ramp(t, T_PEEK0 + 0.2, T_PEEK0 + 0.4)) * (1 - smooth(ramp(t, T_PEEK1, T_PEEK1 + 0.2)))
        if k > 0.05:
            ex, ey = WIN[0] + 55, WIN[1] + 190
            O.sketch_ellipse(cr, ex, ey, 22, 28, 5, sid=22410, fill=(1, 1, 1), alpha=k)
            cr.arc(ex - 8, ey + 4, 10, 0, 2 * math.pi); cr.set_source_rgba(0.05, 0.05, 0.08, k); cr.fill()
    O.draw_her_house(cr, HX, part="wall")
    O.draw_her_house(cr, HX, part="curtain", curtain=curtain(t))
    O.draw_her_house(cr, HX, part="door", door=her_door(t))
    O.draw_trash_can(cr, TRASH, FLOOR_Y - 20, lid=smooth(ramp(t, T_LID0, T_LID0 + 0.2)) * (1 - smooth(ramp(t, T_LID1, T_LID1 + 0.15))))
    if g_scene(t) == "out": draw_her(cr, t)
    # the check, set down leaning on the grass
    if T_SETDOWN + 0.3 <= t:
        O.draw_big_check(cr, HX - 1180 + 560 - 560, FLOOR_Y - 150, s=0.42, ang=-0.12, droop=1.0) if False else \
            O.draw_big_check(cr, HX - 1130, FLOOR_Y - 120, s=0.42, ang=0.05, droop=1.0)
S.prop(house_layer)

# ================================================================ home: the couch, her, the kitten
def couch_x(t):
    if t < CA0: return his_carry_x(CA0) - 480
    return his_carry_x(t) - 480
def home_layer(cr, t, p, ly):
    if t < CUT3 - FR: return
    if ly == "back":
        cx = couch_x(min(t, CA1))
        cr.save()
        if t < CA1: cr.rectangle(DOORX - 200, -9000, 99999, 99999); cr.clip()
        O.draw_couch(cr, cx, FLOOR_Y - 10)
        cr.restore()
        if t >= T_HOP + 0.5:                                                # the kitten, curled up between them
            O.draw_cat(cr, COUCHX, FLOOR_Y - 10 - O.BENCH_SEAT + 4, s=0.85, t=t, kind="loaf", col="black",
                       look=(0.3, 0.2), blink=0.6 if t > T_CURL_C + 0.6 else 0.0, sid=2000, swish=0.3)
        cr.save()
        if t < CA1 + 0.2: cr.rectangle(DOORX - 200, -9000, 99999, 99999); cr.clip()
        draw_her(cr, t)
        cr.restore()
        if t < T_BABY:                                                      # the baby rides on the couch seat, then she picks it up
            bx, by = cx + 30, FLOOR_Y - 10 - O.BENCH_SEAT - 40
            if t >= T_BABY - 0.35:
                q = g_pose(t); hc = scale_pt(q, ((q["lhand"][0] + q["rhand"][0]) / 2, (q["lhand"][1] + q["rhand"][1]) / 2))
                u = smooth(ramp(t, T_BABY - 0.35, T_BABY)); bx, by = lerp(bx, hc[0] + 10, u), lerp(by, hc[1] - 15, u)
            O.draw_baby(cr, bx, by, 0.0, dict(eyes="open", look=(0.0, -0.5)), t, s=0.8)
        if KW0 - 0.2 <= t < T_HOP + 0.5:                                    # the kitten wanders in
            if t < KW1:
                u = ramp(t, KW0, KW1, "linear")
                O.draw_cat(cr, lerp(DOORX - 80, COUCHX - 520, u), FLOOR_Y - 10, s=0.85, t=t, kind="walk", col="black", face=1,
                           phase=t * 9, sid=2000)
            else:
                u = ramp(t, T_HOP, T_HOP + 0.45)
                x = lerp(COUCHX - 520, COUCHX, u); y = lerp(FLOOR_Y - 10, FLOOR_Y - 10 - O.BENCH_SEAT + 4, u) - 160 * math.sin(math.pi * u)
                O.draw_cat(cr, x, y, s=0.85, t=t, kind="walk", col="black", face=1, phase=0.0, sid=2000)
S.prop(home_layer)

# ================================================================ his props
def props_front(cr, t, p, ly):
    if ly != "front": return
    hx, hy = p["rhand"]
    if CUT1 - FR <= t < CUT2 - FR:
        if T_POP1 <= t < T_SLAP + 0.1:                                       # the dollar
            O.sketch_rect(cr, hx - 70, hy - 20, hx + 70, hy + 20, 4, sid=22400, fill=(0.70, 0.88, 0.62)); L.draw_grips(cr, p)
        if T_TIX1 <= t < CK0 + 0.3:                                          # the ticket in both hands
            mx = (p["lhand"][0] + p["rhand"][0]) / 2; my = (p["lhand"][1] + p["rhand"][1]) / 2
            if CUT_TIX - FR <= t < CUT_TV - FR:
                mx += 3 * math.sin(t * 40); my += 2 * math.sin(t * 33)
            circ = sum(1 for b in BALLS if t >= b + 0.35)
            O.draw_ticket(cr, mx, my + 40, s=0.55, circled=circ)
            L.draw_grips(cr, p)
        if CK0 <= t < CK1 + 0.05:                                            # the check, from her to him
            q, _ = clerk_pose(t)
            u = smooth(ramp(t, CK0, CK1)); a = ((q["lhand"][0] + q["rhand"][0]) / 2, min(q["lhand"][1], q["rhand"][1]) - 150)
            b = ((p["lhand"][0] + p["rhand"][0]) / 2, min(p["lhand"][1], p["rhand"][1]) - 150)
            O.draw_big_check(cr, lerp(a[0], b[0], u), lerp(a[1], b[1], u), s=0.6)
    if (CK1 + 0.05 <= t < CUT2 - FR) or (CUT2 - FR <= t < T_SETDOWN + 0.3):    # the check in his hands
        mx = (p["lhand"][0] + p["rhand"][0]) / 2; my = min(p["lhand"][1], p["rhand"][1])
        dr = smooth(ramp(t, T_DROOP0, T_DROOP1)) if t >= CUT2 else 0.0
        up = my - 150 if my < 700 else my - 20
        if T_SETDOWN <= t:
            up = lerp(up, FLOOR_Y - 120, smooth(ramp(t, T_SETDOWN, T_SETDOWN + 0.3))); mx = lerp(mx, HX - 1130, smooth(ramp(t, T_SETDOWN, T_SETDOWN + 0.3)))
        O.draw_big_check(cr, mx, up, s=0.6 if t < CUT2 else 0.55, droop=dr)
        L.draw_grips(cr, p)
    if T_THINK <= t < T_THINK1:                                              # he thinks of them: the family photo
        k = smooth(ramp(t, T_THINK, T_THINK + 0.3)) * (1 - smooth(ramp(t, T_THINK1 - 0.3, T_THINK1)))
        bx, by = p["head"][0] + 300, p["head"][1] - 150
        cr.push_group()
        O.draw_cloud(cr, bx, by, s=2.2)
        for i, r in enumerate((14, 22, 32)):
            O.sketch_circle(cr, lerp(p["head"][0] + 90, bx - 150, i / 3), lerp(p["head"][1] - 50, by + 60, i / 3), r, 5, sid=22425 + i)
        O.sketch_rect(cr, bx - 120, by - 95, bx + 120, by + 95, 5, sid=22420, fill=(1, 1, 1)); O._photo_fam(cr, bx, by + 85, 0.65)
        cr.pop_group_to_source(); cr.paint_with_alpha(k)
    if T_POP2 <= t < T_DROP:                                                 # the game controller
        O.draw_controller(cr, hx, hy - 10, s=0.85); L.draw_grips(cr, p)
    if T_DROP <= t < T_DROP + 0.3:
        u = ramp(t, T_DROP, T_DROP + 0.3, "linear")
        O.draw_controller(cr, lerp(hx, TRASH, u), lerp(hy, FLOOR_Y - 380, u) - 60 * math.sin(math.pi * u) + 120 * u * u, s=0.85, ang=3 * u)
    if T_POP3 <= t < T_RING + 0.4:                                           # the ring box
        O.draw_ring_box(cr, hx + 5, hy - 5, s=0.9, open_=smooth(ramp(t, T_OPENBOX, T_OPENBOX + 0.25)), t=t); L.draw_grips(cr, p)
    if T_RING + 0.4 <= t < CUT3 - FR and g_scene(t) == "out":                # she has the ring box now
        q = g_pose(t); rx, ry = scale_pt(q, q["rhand"])
        if t < T_HUG: O.draw_ring_box(cr, rx, ry, s=0.8, open_=1.0, t=t)
    if T_OPENBOX + 0.25 <= t < T_OPENBOX + 0.6:
        L.burst_lines(cr, hx, hy - 90, (t - T_OPENBOX - 0.25) / 0.35, r0=60, r1=120, n=10, sid=22430)
    if CUT3 - FR <= t < CA1 + 0.2 and his_layer_clip(t):
        pass
    if T_PUSH > t >= T_CURL_C and False: pass
S.prop(props_front)
def his_layer_clip(t): return False

# his carry: hide him while behind the door frame
def hide_hook(tt, p):
    return p
S.hook(hide_hook)

if __name__ == "__main__":
    print(f"end {S.t:.2f}", file=sys.stderr)
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        S.build()
        import cairo
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, L.W, L.H)
        for a in sys.argv[2:]:
            tt = float(a); L.render_frame(tt, surf); surf.write_to_png(f"still_{tt:05.2f}.png")
    else:
        S.render("day018.mp4")
