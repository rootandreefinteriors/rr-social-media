"""Day 21: @thatboypiwko "Go buy a ps5 and gta 6" (TikTok, day 20 video, 0 likes).
The curb outside LE FANCY (she nods: go) -> he runs out right -> a night strip mall: GAME CAVE, a neon-sunset "6" poster,
COMING NOV 19, TODAY NOV 12 -> he sits down at the door, first in line -> time-lapse: days flicker by, the line grows,
pizza boxes pile up -> NOV 19, 11:59: the clerk steps out with a sign: DELAYED (heartbeat, push-in) -> wrong side: OPEN,
12:00 -> the line stampedes over him -> inside: the LAST ONE console + game, $569.98 -> a sock of pennies buries the
counter and the clerk -> boxes overhead, light beam -> demo TV: UPDATE 1 OF 47 -> the ask. See BEATS.md.
Brands stay off screen (generic white console, a neon-sunset box with a "6"); nothing from the game's crime side.
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import numpy as np
import moves as M
import ltcd as L
import objects as O
import character as C
from ltcd import Track, ramp, lerp, pulse, FLOOR_Y
from ink import smooth, sketch_line, draw_text

FR = 1 / 30
sk_rect, sk_poly, sk_circ, sk_ell = O.sketch_rect, O.sketch_poly, O.sketch_circle, O.sketch_ellipse

# ================================================================ places
RX = 5000000.0                                      # outside LE FANCY (day 20)
CART = RX + 1640.0
CURB_HIM, CURB_HER = RX + 1420.0, RX + 1110.0
GX = 7000000.0                                      # the strip mall: GAME CAVE
DOOR0, DOOR1 = GX + 160.0, GX + 480.0
DOORX = (DOOR0 + DOOR1) / 2
HIS_Q = GX - 120.0                                  # where he sits, first in line (body centre)
LINE_X = [HIS_Q - 330 - 250 * k for k in range(7)]
IX = 8000000.0                                      # inside GAME CAVE
CTR_X = IX + 470.0                                  # counter centre
CTR_TOP = FLOOR_Y - 470.0
CLERK_X = IX + 620.0
HIS_I = IX - 170.0
BOX_A, BOX_B = IX + 90.0, IX + 250.0                # console box / game box on the counter
TVX = IX - 1500.0                                   # the demo TV (screen centre x)
HIS_TV = TVX + 560.0

# ================================================================ timeline
T_READ = 0.35; T_WIDE = 1.3; T_LOOKHER = 1.6; T_NOD = 1.85; CUT_UP = 2.25; T_RUN = 2.45; CUT1 = 3.05
T_ARR = 3.8; T_POSTER = 4.2; T_BOARD = 4.85; T_US = 5.45; T_SIT = 6.1; T_US1 = 6.6
T_TL0 = 7.1
DAYS = [1.9, 1.75, 1.55, 1.4, 1.25, 1.1, 0.95]
B = [T_TL0]
for d in DAYS: B.append(B[-1] + d)
T_TL1 = B[-1]                                       # ~17.0: NOV 19, night
T_CLK0 = T_TL1                                      # 11:59:56 -> 12:00:00 at T_OPEN
T_DOOR1 = T_TL1 + 0.6; T_SIGNFLIP = T_TL1 + 1.4; T_REACT = T_SIGNFLIP + 0.3
T_PUSH0, T_PUSH1 = T_REACT + 0.2, T_REACT + 2.4
T_CHECK = T_PUSH1 + 0.05; T_SHRUG = T_CHECK + 0.45; T_OPEN = T_SHRUG + 0.5
T_STAMP = T_OPEN + 0.6; T_FLAT = T_STAMP + 1.6; T_STAMP1 = T_STAMP + 1.8
T_HEAD = T_STAMP1 + 0.6; T_HEADUS = T_HEAD + 0.6
CUT_IN = T_HEADUS + 1.2
T_WALK0, T_WALK1 = CUT_IN + 0.1, CUT_IN + 1.3
T_SLAP = T_WALK1 + 0.25; T_STARE = T_SLAP + 0.4; T_SCAN = T_STARE + 0.6
CUT_REG = T_SCAN + 0.35; CUT_REG1 = CUT_REG + 1.5
T_DIG = CUT_REG1 + 0.15; T_POP = T_DIG + 1.4
T_TIP0 = T_POP + 0.45; T_POUR0 = T_TIP0 + 0.25; T_POUR1 = T_POUR0 + 2.3
T_KACHING = T_POUR1 + 0.35; T_RECEIPT = T_KACHING + 0.15
T_HOIST = T_RECEIPT + 0.7; T_BEAM0 = T_HOIST + 0.35; T_SMILE = T_BEAM0 + 0.6; T_BEAM1 = T_BEAM0 + 2.4
CUT_TV = T_BEAM1 + 0.1
T_START = CUT_TV + 0.6; T_UPD = T_START + 0.35; T_LOOKTV = T_UPD + 0.3; T_LEFT = T_UPD + 1.3
T_US2 = T_LEFT + 0.5; T_BAR100 = T_US2 + 1.5; T_UPD2 = T_BAR100 + 0.25; T_US3 = T_UPD2 + 0.55
T_STAND = T_US3 + 1.3; T_ASK = T_STAND + 0.8; HOLD = 9.0

# ================================================================ poses
def P(name, **kw): L.POSES[name] = kw
P("sit_curb", **dict(L.POSES["sit_floor"], nowalk=1.0))
SITF = L.POSES["sit_floor"]
P("q_sit", **dict(SITF, nowalk=1.0))
P("q_slump", **dict(SITF, head=(548, 1010), neck=(544, 1125), lelb=(480, 1250), lhand=(500, 1330), relb=(600, 1250), rhand=(590, 1330), nowalk=1.0))
P("flat", **dict(L.POSES["lie_back"], nowalk=1.0))
P("flat_up", **dict(L.POSES["lie_back"], head=(345, 1300), neck=(450, 1370), tilt=-1.1, nowalk=1.0))
P("slap", relb=(690, 900), rhand=(800, CTR_TOP - 40), rhand_t="flat")
P("tip", lelb=(560, 870), lhand=(700, 780), relb=(690, 820), rhand=(790, 700), lhand_t="grip", rhand_t="grip")
P("hoist", lelb=(440, 700), lhand=(470, 520), relb=(640, 700), rhand=(610, 520), lhand_t="grip", rhand_t="grip")
P("tv_sit", **dict(SITF, lelb=(480, 1210), lhand=(520, 1250), relb=(600, 1210), rhand=(560, 1250), lhand_t="grip", rhand_t="grip", nowalk=1.0))
# others
P("g_sitc", **dict(SITF, lelb=(470, 1240), lhand=(470, 1318), lhand_t="grip", nowalk=1.0))
P("violin", lelb=(470, 900), lhand=(470, 830), relb=(650, 810), rhand=(760, 760), lhand_t="grip", rhand_t="grip", tilt=0.18)
P("k_sign", lelb=(450, 900), lhand=(420, 800), relb=(630, 900), rhand=(660, 800), lhand_t="grip", rhand_t="grip")
P("k_scan", relb=(470, 960), rhand=(400, 940), rhand_t="grip", lelb=(610, 980), lhand=(560, 1060))

# ================================================================ scene (him)
CAM_A = (RX + 1230, 790, 0.76)
S = M.Scene(start_body="sit_curb", start_face="deadpan", x0=CURB_HIM - 540)
S.auto_blinks = True
S.floor = False
S.card("thatboypiwko", "Go buy a ps5 and gta 6", "0", t0=0.3)
S.camkeys[0] = (0.0, CAM_A, 0); S.cam = CAM_A

XT = None
def S_x(t): return XT.at(t) if XT else 0.0

def dig_pull(t0, hold_pose, look=(0.4, -0.2), pock=(595, 1092), **kw):
    """digs his hand around at his hip (no pocket), POP -> the thing is in his hand (drawn by the caller from t0+1.4)."""
    S.set(t0, "stand", "deadpan", dur=0.35, look=(0.35, 0.9), tilt=0.05, **kw)
    def hk(tt, p):
        if t0 + 0.25 <= tt < t0 + 1.35:
            POCK = (pock[0] + S_x(tt), pock[1])
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
            L.burst_lines(cr, p["rhand"][0], p["rhand"][1] - 50, (tt - t0 - 1.4) / 0.4, r0=60, r1=120, n=10, sid=9)
    S.prop(pr)

# ---------------------------------------------------------------- A: the curb outside LE FANCY
S.keys[0] = (0.0, L.pose("sit_curb", "deadpan", turn=0.0, look=(0.0, 0.0)), 0)
S.set(T_READ, "sit_curb", "deadpan", dur=0.25, turn=0.3, look=(0.8, -0.8))
def read_hk(tt, p):
    if T_READ + 0.3 <= tt < T_WIDE - 0.05:
        k = (tt - T_READ - 0.3) / 0.45; u = k % 1.0
        p["look"] = (0.3 + 0.6 * smooth(u), -0.85 + 0.12 * int(k % 2))
    return p
S.hook(read_hk)
S.set(T_WIDE, "sit_curb", "dead_stare", dur=0.08, ease="snap", turn=0.0, look=(0.0, 0.0), eyescale=1.4, pupil=0.55, curl_up=1.0)
S.sfx(T_WIDE, "boing", 0.05)
S.set(T_LOOKHER, "sit_curb", "deadpan", dur=0.25, turn=-0.8, look=(-1.0, 0.0), eyescale=1.15, curl_up=0.6)
S.cut(CUT_UP - FR, cam=(RX + 1330, 760, 0.76))
S.set(CUT_UP - FR, "stand", "deadpan", dur=0.0, turn=0.6, look=(1.0, 0.0))
S.set(T_RUN, "stand", "deadpan", dur=0.15, run=1.0, look=(1.0, 0.0), turn=1.0, lean=0.1)
S.xkeys.append((T_RUN, CURB_HIM + 900 - 540, CUT1 - T_RUN, "inn")); S.x = CURB_HIM + 900 - 540
S.sfx(T_RUN, "whoosh", 0.05)

# ---------------------------------------------------------------- B: GAME CAVE, outside
CAM_B = (GX + 120, 960, 0.62)
S.cut(CUT1 - FR, cam=CAM_B, x=GX - 1700 - 540)
S.set(CUT1 - FR, "stand", "deadpan", dur=0.0, run=1.0, look=(1.0, 0.0), turn=1.0, lean=0.1)
S.xkeys.append((CUT1, HIS_Q - 540, T_ARR - CUT1, "out")); S.x = HIS_Q - 540
S.set(T_ARR - 0.1, "stand", "deadpan", dur=0.12, ease="snap", stretch=-0.25, run=0.0, turn=0.6, look=(0.9, 0.0))
S.set(T_ARR + 0.1, "stand", "deadpan", dur=0.25, ease="back", turn=0.6, look=(0.9, -0.1)); S.sfx(T_ARR - 0.1, "skid", 0.05, dur=0.3)
S.set(T_POSTER, "stand", "deadpan", dur=0.3, turn=-0.6, look=(-0.9, -0.5))
S.set(T_BOARD, "stand", "deadpan", dur=0.3, turn=0.6, look=(0.9, -1.0), tilt=-0.05)
S.set(T_US, "stand", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0))
S.set(T_SIT - 0.2, "crouch", "deadpan", dur=0.25, turn=0.2, look=(0.2, 0.0), nowalk=1.0)
S.set(T_SIT + 0.1, "q_sit", "deadpan", dur=0.25, ease="back", turn=0.2, look=(0.2, 0.0))
S.sfx(T_SIT + 0.1, "thud", 0.04)
S.set(T_US1, "q_sit", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0))
# time-lapse: each day his lids droop a little more; he glances at the line once
for i in range(7):
    lid = 0.3 + 0.05 * (i + 1)
    body = "q_sit" if i < 4 else "q_slump"
    S.set(B[i] + 0.05, body, "dead_stare", dur=0.15, turn=(0.0 if i % 3 else -0.5), look=((0.0, 0.0) if i % 3 else (-1.0, 0.0)), lid=lid)
    S.set(B[i] + DAYS[i] * 0.55, body, "dead_stare", dur=0.15, turn=0.0, look=(0.0, 0.0), lid=lid)
# the sign
S.set(T_DOOR1 + 0.2, "q_slump", "deadpan", dur=0.3, turn=0.8, look=(1.0, -0.6), lid=0.25)
S.set(T_REACT, "q_slump", "dead_stare", dur=0.1, ease="snap", turn=0.8, look=(1.0, -0.6), lid=0.0, eyescale=1.35, pupil=0.5)
S.set(T_REACT + 0.7, "q_slump", "dead_stare", dur=0.6, turn=0.3, look=(0.0, 0.0), lid=0.0, eyescale=1.3, pupil=0.5, twitch=0.6, sweat=0.5, quiver=0.4)
S.set(T_REACT + 1.6, "q_slump", "dead_stare", dur=0.8, turn=0.1, look=(0.0, 0.0), lid=0.0, eyescale=1.3, pupil=0.45, twitch=1.0, sweat=1.0, quiver=0.9)
S.set(T_CHECK + 0.2, "q_slump", "deadpan", dur=0.3, turn=0.8, look=(1.0, -0.6), sweat=0.6)
S.set(T_OPEN + 0.15, "q_slump", "dead_stare", dur=0.1, ease="snap", turn=0.8, look=(1.0, -0.6), eyescale=1.2, curl_up=1.0)
S.camera(T_PUSH0, HIS_Q + 330, 900, 0.98, T_PUSH1 - T_PUSH0)
S.cut(T_CHECK - FR, cam=CAM_B)
# the stampede: he turns to the noise, then he's flattened
S.set(T_STAMP + 0.1, "q_slump", "dead_stare", dur=0.2, turn=-0.9, look=(-1.0, 0.0), eyescale=1.2)
S.set(T_FLAT - FR, "flat", "dead_stare", dur=0.0, look=(0.0, -0.3), lid=0.2)
S.sfx(T_STAMP, "rumble_feet", 0.12, dur=T_STAMP1 - T_STAMP + 0.2)
S.shake(T_FLAT, T_STAMP1 - T_FLAT, 10)
S.set(T_HEAD, "flat_up", "deadpan", dur=0.4, look=(0.4, 0.4))
S.set(T_HEADUS, "flat_up", "dead_stare", dur=0.3, look=(0.3, 0.6), lid=0.3)

# ---------------------------------------------------------------- C: inside GAME CAVE
CAM_I = (IX + 260, 900, 0.80)
S.cut(CUT_IN - FR, cam=CAM_I, x=IX - 1000 - 540)
S.set(CUT_IN - FR, "stand", "deadpan", dur=0.0, turn=0.7, look=(1.0, 0.0), lid=0.3)
S.walk_to(T_WALK0, HIS_I - 540, T_WALK1 - T_WALK0)
S.set(T_SLAP - 0.15, "slap", "deadpan", dur=0.15, ease="snap", turn=0.6, look=(0.8, 0.3), lid=0.3)
S.sfx(T_SLAP, "pat", 0.07)
S.set(T_STARE, "slap", "dead_stare", dur=0.3, turn=0.7, look=(1.0, -0.4), lid=0.3)
S.set(CUT_REG1 - FR, "stand", "dead_stare", dur=0.0, turn=0.0, look=(0.0, 0.0), sweat=0.6, eyescale=1.15)
dig_pull(T_DIG, "tip", look=(0.8, 0.3), turn=0.5)
S.set(T_TIP0, "tip", "deadpan", dur=0.25, turn=0.5, look=(0.8, 0.3), lelb=(600, 830), lhand=(720, 760), relb=(700, 780), rhand=(800, 640))
S.set(T_POUR1 - 0.4, "tip", "deadpan", dur=0.5, turn=0.5, look=(0.9, 0.0), lelb=(600, 830), lhand=(720, 760), relb=(700, 780), rhand=(800, 640))
S.set(T_POUR1 + 0.1, "stand", "deadpan", dur=0.35, turn=0.6, look=(1.0, -0.2))
S.set(T_KACHING + 0.15, "stand", "dead_stare", dur=0.25, turn=0.6, look=(1.0, -0.3))
S.set(T_HOIST, "hoist", "deadpan", dur=0.45, turn=0.0, look=(0.0, -0.9))
S.set(T_SMILE, "hoist", "happy", dur=0.6, turn=0.0, look=(0.0, -0.9), smile=0.45, lid=0.1)
S.set(T_BEAM1 - 0.5, "hoist", "happy", dur=0.4, turn=0.0, look=(0.0, 0.0), smile=0.4)
S.camera(T_HOIST, IX + 160, 860, 0.84, 0.8)

# ---------------------------------------------------------------- D: the demo TV
CAM_TV = (TVX + 330, 960, 0.80)
S.cut(CUT_TV - FR, cam=CAM_TV, x=HIS_TV - 540)
S.set(CUT_TV - FR, "tv_sit", "happy", dur=0.0, turn=-0.8, look=(-1.0, -0.6), smile=0.35)
S.set(T_START, "tv_sit", "happy", dur=0.1, ease="snap", turn=-0.8, look=(-1.0, -0.6), smile=0.4, lhand=(525, 1240), rhand=(565, 1240))
S.sfx(T_START, "tap", 0.06)
S.set(T_LOOKTV, "tv_sit", "deadpan", dur=0.3, turn=-0.8, look=(-1.0, -0.6))
S.set(T_LEFT + 0.2, "tv_sit", "deadpan", dur=0.3, turn=-0.8, look=(-1.0, -0.4), lid=0.4)
S.set(T_US2, "tv_sit", "dead_stare", dur=0.35, turn=0.0, look=(0.0, 0.0), lid=0.35)
S.set(T_BAR100 - 0.2, "tv_sit", "deadpan", dur=0.25, turn=-0.8, look=(-1.0, -0.5), eyescale=1.1)
S.set(T_UPD2 + 0.15, "tv_sit", "dead_stare", dur=0.1, turn=-0.8, look=(-1.0, -0.5), lid=0.5)
S.set(T_US3, "tv_sit", "dead_stare", dur=0.4, turn=0.0, look=(0.0, 0.0), lid=0.45, twitch=0.4)
S.set(T_STAND, "crouch", "deadpan", dur=0.3, nowalk=1.0)
S.set(T_STAND + 0.35, "stand", "deadpan", dur=0.3, ease="back")
S.camera(T_STAND, HIS_TV - 100, 900, 0.86, 0.7)
S.x = HIS_TV - 540
S.the_ask(T_ASK, hold=HOLD)
T_END = S.t
S.blink(2.0, 5.1, 9.0, 12.6, 22.0, 30.6, 37.0, 41.5)
XT = Track(S.xkeys)

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
        # breathing
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

# ---------------------------------------------------------------- HER (on the curb, day 20)
G_HAIR, G_DRESS = (0.62, 0.28, 0.16), (0.30, 0.66, 0.66)
GS = 0.92
G = Actor(CURB_HER, "g_sitc", "happy", turn=0.5, look=(0.6, -0.2), smile=0.6)
G.blinks = [0.9, 2.7]
G.k(T_LOOKHER + 0.2, "g_sitc", "happy", dur=0.3, turn=0.7, look=(1.0, 0.0), smile=0.8)
G.k(T_NOD, "g_sitc", "happy", dur=0.15, turn=0.7, look=(1.0, 0.3), smile=0.9, tilt=0.12)
G.k(T_NOD + 0.2, "g_sitc", "happy", dur=0.15, turn=0.7, look=(1.0, 0.0), smile=0.9, tilt=-0.02)
G.k(T_NOD + 0.4, "g_sitc", "happy", dur=0.15, turn=0.7, look=(1.0, 0.3), smile=0.9, tilt=0.1)
G.k(CUT_UP + 0.1, "g_sitc", "happy", dur=0.3, turn=0.8, look=(1.0, -0.1), smile=0.8)
G.done()

def draw_her(cr, t):
    q = G.pose(t)
    O.draw_mom(cr, t, q, G.blink(t), s=GS, hair=G_HAIR, dress=G_DRESS, bun=False)
    rx, ry = scale_pt(q, q["lhand"], GS)
    O.draw_rose(cr, rx, ry - 10, s=0.55, ang=-0.25)
    fx = foot_c(q)
    cr.save(); cr.translate(fx, FLOOR_Y); cr.scale(GS, GS); cr.translate(-fx, -FLOOR_Y); L.draw_grips(cr, q); cr.restore()

# ---------------------------------------------------------------- the violinists (still playing, day 20)
VIOS = []
for k, vx in enumerate((RX + 380, RX + 600, RX + 820)):
    a = Actor(vx, "violin", "concentrating", turn=0.7, look=(0.6, 0.3), lid=0.5, eyes="closed"); a.done(); VIOS.append(a)
def draw_violinist(cr, t, v, k):
    q = v.pose(t)
    ph = t * 2 * math.pi / 0.9 + 1.3 * k
    q["lhand"] = (q["lhand"][0] - 70 * math.sin(ph), q["lhand"][1] + 10 * math.cos(ph))
    q = L.constrain(q)
    O.draw_staff(cr, t, q, 0.0, s=1.0, kind="plain", vest=(0.10, 0.10, 0.12))
    nx, ny = q["neck"]
    sk_poly(cr, [(nx, ny + 22), (nx - 26, ny + 8), (nx - 26, ny + 36)], 3, sid=24210, fill=(0.1, 0.1, 0.1))
    sk_poly(cr, [(nx, ny + 22), (nx + 26, ny + 8), (nx + 26, ny + 36)], 3, sid=24211, fill=(0.1, 0.1, 0.1))
    O.draw_violin(cr, (q["neck"][0] + 30, q["neck"][1] + 10), q["rhand"], s=0.9)
    L.draw_grips(cr, q)
    a = q["lhand"]; O.draw_bow(cr, a, (a[0] + 330, a[1] - 70))

# ---------------------------------------------------------------- the line (7 people, one joins each day)
HOODIES = [(0.25, 0.45, 0.75), (0.80, 0.35, 0.30), (0.30, 0.62, 0.40), (0.55, 0.40, 0.70), (0.95, 0.65, 0.20),
           (0.35, 0.35, 0.40), (0.20, 0.65, 0.70)]
LINE = []
for i, lx in enumerate(LINE_X):
    sitting = i in (1, 4)
    a = Actor(lx, "q_sit" if sitting else "stand", "deadpan", turn=0.7, look=(0.9, 0.0), lid=0.3 + 0.05 * (i % 3))
    a.k(T_REACT + 0.05 * i, "q_sit" if sitting else "stand", "dead_stare", dur=0.12, ease="snap", turn=0.7, look=(1.0, -0.4), lid=0.0,
        eyescale=1.3, pupil=0.5)
    a.k(T_OPEN + 0.2, "stand", "dead_stare", dur=0.15, ease="snap", turn=0.9, look=(1.0, -0.4), eyescale=1.2, curl_up=1.0)
    a.blinks = [B[min(6, i)] + 0.7 + 0.37 * j for j in range(0, 12, 3)]
    a.done(); LINE.append(a)
def cloud_x(t):
    """the stampede cloud's centre: it rolls in from the back of the line, swallows everyone, runs over him, into the door."""
    u = ramp(t, T_STAMP, T_STAMP1 + 0.6, "linear")
    return lerp(LINE_X[-1] - 150, DOORX + 150, u)
def line_on(i, t): return B[i] <= t and (t < T_STAMP or cloud_x(t) < LINE_X[i] + 150)
def draw_line_person(cr, t, i):
    q = LINE[i].pose(t)
    O.draw_staff(cr, t, q, LINE[i].blink(t), s=0.93, kind="plain", vest=HOODIES[i])
    if i % 2 == 0:                                                              # a few backwards caps
        hx, hy = q["head"]; R = C.HEAD_R * 0.93
        fx = foot_c(q); hx = fx + (hx - fx) * 0.93; hy = FLOOR_Y + (hy - FLOOR_Y) * 0.93
        sk_poly(cr, [(hx - 104, hy - R + 46), (hx - 84, hy - R - 26), (hx, hy - R - 46), (hx + 84, hy - R - 26), (hx + 104, hy - R + 46)], 6,
                sid=21500 + i, fill=HOODIES[(i + 3) % 7])
        sk_poly(cr, [(hx - 100, hy - R + 40), (hx - 190, hy - R + 50), (hx - 190, hy - R + 70), (hx - 100, hy - R + 62)], 5,
                sid=21510 + i, fill=HOODIES[(i + 3) % 7])

# ---------------------------------------------------------------- the clerk
K = Actor(DOORX + 700, "stand", "neutral", turn=-0.6, look=(-0.9, 0.0), lid=0.45)
K.blinks = [18.5, 20.0, 31.0, 36.5]
K.at(T_DOOR1 - FR, DOORX + 40)
K.walk(T_DOOR1, T_DOOR1 + 0.45, DOORX + 260)
K.k(T_DOOR1 + 0.3, "k_sign", "neutral", dur=0.3, turn=-0.6, look=(-0.8, 0.1), lid=0.45, smile=0.0)
K.k(T_CHECK, "k_sign", "neutral", dur=0.3, turn=-0.3, look=(-0.2, -0.8), lid=0.3, smile=0.0)
K.k(T_SHRUG, "shrug", "neutral", dur=0.2, turn=-0.5, look=(-0.6, 0.0), lid=0.45, smile=0.0)
K.k(T_OPEN - 0.15, "k_sign", "neutral", dur=0.2, turn=-0.6, look=(-0.8, 0.1), lid=0.45, smile=0.1)
K.walk(T_OPEN + 0.25, T_OPEN + 0.6, DOORX + 700)
K.k(T_OPEN + 0.25, "stand", "surprised", dur=0.15, turn=0.8, look=(1.0, 0.0))
# inside: behind the counter
K.at(CUT_IN - FR, CLERK_X)
K.k(CUT_IN - FR, "stand", "neutral", dur=0.0, turn=-0.6, look=(-0.9, 0.0), lid=0.5, smile=0.0)
K.k(T_SCAN - 0.25, "k_scan", "neutral", dur=0.25, turn=-0.5, look=(-0.7, 0.5), lid=0.5, smile=0.0)
K.k(T_SCAN + 0.3, "stand", "neutral", dur=0.3, turn=-0.6, look=(-0.9, 0.0), lid=0.5, smile=0.0)
K.k(T_POUR0 + 0.2, "stand", "neutral", dur=0.3, turn=-0.6, look=(-0.9, -0.3), lid=0.2, smile=0.0, eyescale=1.15)
K.k(T_POUR1 - 0.6, "stand", "neutral", dur=0.4, turn=-0.4, look=(-0.6, -0.6), lid=0.1, smile=-0.2, eyescale=1.25)
K.k(T_KACHING + 0.3, "stand", "neutral", dur=0.3, turn=-0.6, look=(-1.0, 0.0), lid=0.55, smile=0.0)
K.done()
def draw_clerk(cr, t, sign=True):
    q = K.pose(t)
    O.draw_staff(cr, t, q, K.blink(t), s=0.95, kind="cashier", vest=(0.20, 0.55, 0.35))
    return q

def sign_side(t):
    """0 = blank back to us, 1 = DELAYED, 2 = OPEN."""
    if t < T_SIGNFLIP: return 0
    if t < T_OPEN - 0.05: return 1
    return 2
def draw_door_sign(cr, t, q):
    fx = foot_c(q)
    hx = fx + ((q["lhand"][0] + q["rhand"][0]) / 2 - fx) * 0.95
    hy = FLOOR_Y + ((q["lhand"][1] + q["rhand"][1]) / 2 - FLOOR_Y) * 0.95
    if K.KT.at(t) is None: return
    flip = 1.0
    for tf in (T_SIGNFLIP, T_OPEN - 0.05):
        if tf - 0.12 <= t < tf + 0.12: flip = abs((t - tf) / 0.12)
    w = 300 * max(0.05, flip); h = 180
    side = sign_side(t)
    if T_CHECK + 0.1 <= t < T_OPEN - 0.17:                                       # she turns it to herself: we see the back
        side = 0
    sk_rect(cr, hx - w / 2, hy - h - 20, hx + w / 2, hy - 20, 6, sid=21600, fill=(1, 1, 0.97) if side != 1 else (1.0, 0.93, 0.90))
    if flip > 0.5:
        if side == 1: draw_text(cr, "DELAYED", hx, hy - h / 2 - 20, 58, color=(200, 25, 30), max_w=w - 20)
        elif side == 2: draw_text(cr, "OPEN", hx, hy - h / 2 - 20, 80, color=(30, 140, 60), max_w=w - 20)

# ================================================================ the strip mall
NIGHT, DAYC = (0.10, 0.12, 0.26), (0.62, 0.80, 0.96)
def daylight(t):
    if t < T_TL0 or t >= T_TL1: return 0.0
    for i in range(7):
        if B[i] <= t < B[i + 1]:
            u = (t - B[i]) / DAYS[i]
            return math.sin(math.pi * u) ** 0.5
    return 0.0
def day_index(t):
    """which date the board shows: 12 before the time-lapse, 13.. 19 during it."""
    if t < T_TL0: return 12
    for i in range(7):
        if t < B[i + 1]: return 13 + i if t >= B[i] + DAYS[i] * 0.5 else 12 + i
    return 19

def draw_mall(cr, t):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    dl = daylight(t)
    sky = lerp(NIGHT, DAYC, dl)
    cr.rectangle(vx0 - 10, vy0 - 10, vx1 - vx0 + 20, FLOOR_Y - vy0 + 10); cr.set_source_rgb(*sky); cr.fill()
    if dl < 0.5:                                                                # stars
        for k in range(40):
            sx = GX - 4000 + (k * 7919) % 8000; sy = 120 + (k * 3571) % 520
            if vx0 - 20 < sx < vx1 + 20:
                cr.arc(sx, sy, 4 + (k % 3), 0, 2 * math.pi); cr.set_source_rgba(1, 1, 0.9, (1 - 2 * dl) * 0.8); cr.fill()
    # the mall: one long low building, shops left and right of GAME CAVE
    top = FLOOR_Y - 1180
    wall = lerp((0.30, 0.28, 0.34), (0.86, 0.80, 0.70), dl)
    sk_rect(cr, GX - 6000, top, GX + 6000, FLOOR_Y, 7, sid=21000, fill=wall)
    sk_rect(cr, GX - 6000, top - 50, GX + 6000, top + 30, 6, sid=21001, fill=lerp((0.20, 0.20, 0.24), (0.70, 0.62, 0.52), dl))
    for k in range(-5, 6):                                                      # other (closed) shops
        if k == 0: continue
        sx = GX + k * 1100
        if sx + 500 < vx0 or sx - 500 > vx1: continue
        sk_rect(cr, sx - 420, FLOOR_Y - 820, sx + 420, FLOOR_Y - 140, 6, sid=21010 + k, fill=lerp((0.16, 0.18, 0.24), (0.55, 0.68, 0.78), dl))
        sk_rect(cr, sx - 380, top + 70, sx + 380, top + 230, 5, sid=21030 + k, fill=lerp((0.38, 0.36, 0.40), (0.95, 0.93, 0.88), dl))
        draw_text(cr, ("NAILS", "TAXES", "VAPE-FREE ZONE", "PIZZA", "LAUNDRY", "PIZZA", "DENTIST", "PHONES", "SHOES", "INSURANCE")[(k + 5) % 10],
                  sx, top + 150, 64, color=(70, 70, 80))
    # GAME CAVE
    sk_rect(cr, GX - 900, top + 40, GX + 900, top + 260, 7, sid=21050, fill=(0.14, 0.12, 0.20))
    glow = 1.0 - 0.5 * dl
    draw_text(cr, "GAME CAVE", GX - 330, top + 150, 120, color=(int(120 + 135 * glow), int(220 * glow + 30), 255))
    # the big window with the poster
    wx0, wx1, wy0, wy1 = GX - 860, GX + 80, FLOOR_Y - 900, FLOOR_Y - 140
    sk_rect(cr, wx0, wy0, wx1, wy1, 7, sid=21060, fill=(0.95, 0.88, 0.62))
    draw_poster(cr, (wx0 + wx1) / 2, (wy0 + wy1) / 2 - 20, s=1.0)
    # the door
    sk_rect(cr, DOOR0, FLOOR_Y - 820, DOOR1, FLOOR_Y, 7, sid=21070, fill=(0.98, 0.90, 0.62) if door_open(t) > 0.5 else (0.25, 0.30, 0.36))
    if door_open(t) <= 0.5:
        sk_rect(cr, DOOR0 + 40, FLOOR_Y - 700, DOOR1 - 40, FLOOR_Y - 380, 4, sid=21071, fill=(0.40, 0.48, 0.58))
        sk_rect(cr, DOOR0 + 40, FLOOR_Y - 640, DOOR1 - 40, FLOOR_Y - 470, 4, sid=21072, fill=(1, 1, 0.97))
        draw_text(cr, "COMING", DOORX, FLOOR_Y - 600, 40, color=(40, 40, 50))
        draw_text(cr, "NOV 19", DOORX, FLOOR_Y - 520, 56, color=(200, 30, 40))
    # the date board over the door
    by = FLOOR_Y - 960
    sk_rect(cr, DOORX - 230, by - 80, DOORX + 230, by + 80, 6, sid=21080, fill=(0.08, 0.08, 0.10))
    if t < T_CLK0:
        di = day_index(t)
        draw_text(cr, "TODAY", DOORX, by - 35, 34, color=(255, 170, 60))
        draw_text(cr, f"NOV {di}", DOORX, by + 25, 66, color=(255, 120, 40))
    else:
        secs = 60 - (T_OPEN - t)
        if t < T_OPEN:
            s_ = int(secs); txt = f"11:59:{s_:02d}"
            col = (255, 80, 60)
        else:
            txt = "12:00:00"; col = (90, 255, 120)
        draw_text(cr, "NOV 19", DOORX, by - 38, 32, color=(255, 170, 60))
        draw_text(cr, txt, DOORX, by + 22, 66, color=col)
    # sidewalk
    cr.rectangle(vx0 - 10, FLOOR_Y, vx1 - vx0 + 20, vy1 - FLOOR_Y + 10); cr.set_source_rgb(*lerp((0.30, 0.30, 0.34), (0.78, 0.76, 0.72), dl)); cr.fill()
    sketch_line(cr, [(vx0 - 10, FLOOR_Y), (vx1 + 10, FLOOR_Y)], 6, sid=21090, amp=0.4)
    sketch_line(cr, [(vx0 - 10, FLOOR_Y + 150), (vx1 + 10, FLOOR_Y + 150)], 5, sid=21091, amp=0.4)
    if dl > 0.02:                                                               # daylight wash over the whole frame
        pass

def door_open(t):
    return 1.0 if (T_DOOR1 - 0.05 <= t < CUT_IN) else 0.0

def draw_poster(cr, x, y, s=1.0):
    """the window poster: a neon sunset, palm trees, a giant 6, OUT NOV 19. No title, no logo."""
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    w, h = 820, 680
    bands = ((0.98, 0.45, 0.62), (0.99, 0.55, 0.50), (1.0, 0.68, 0.42), (1.0, 0.80, 0.40), (0.55, 0.30, 0.62))
    for i, c in enumerate(bands):
        cr.rectangle(-w / 2, -h / 2 + i * h / 5, w, h / 5 + 1); cr.set_source_rgb(*c); cr.fill()
    cr.arc(0, 60, 190, math.pi, 2 * math.pi); cr.set_source_rgb(1.0, 0.92, 0.45); cr.fill()
    for k in range(4):
        cr.rectangle(-200, 60 - 40 * k - 10, 400, 10); cr.set_source_rgb(*bands[k]); cr.fill()
    cr.rectangle(-w / 2, 60, w, h / 2 - 60); cr.set_source_rgb(0.30, 0.18, 0.45); cr.fill()
    for xx, sc in ((-290, 1.0), (300, 0.8)):                                    # palm silhouettes
        cr.save(); cr.translate(xx, 60); cr.scale(sc, sc)
        cr.move_to(-8, 0); cr.curve_to(-10, -120, 10, -220, 30, -300); cr.line_to(42, -296); cr.curve_to(22, -210, 8, -120, 10, 0)
        cr.close_path(); cr.set_source_rgb(0.18, 0.08, 0.25); cr.fill()
        for a in (-2.6, -2.0, -1.2, -0.5, 0.2):
            cr.move_to(36, -298); cr.curve_to(36 + 70 * math.cos(a), -298 + 50 * math.sin(a) - 30, 36 + 140 * math.cos(a), -298 + 100 * math.sin(a),
                                            36 + 160 * math.cos(a), -298 + 140 * math.sin(a) + 40)
            cr.set_line_width(26); cr.set_source_rgb(0.18, 0.08, 0.25); cr.stroke()
        cr.restore()
    draw_text(cr, "6", 0, -110, 330, color=(255, 255, 255))
    draw_text(cr, "OUT NOV 19", 0, 230, 70, color=(255, 230, 120))
    cr.restore()
    sk_rect(cr, x - w / 2 * s, y - h / 2 * s, x + w / 2 * s, y + h / 2 * s, 6, sid=21065, fill=None)

def draw_pizza_box(cr, x, y, ang=0.0, sid=21700):
    cr.save(); cr.translate(x, y); cr.rotate(ang)
    sk_rect(cr, -130, -36, 130, 0, 4, sid=sid, fill=(0.88, 0.78, 0.58))
    draw_text(cr, "PIZZA", 0, -18, 26, color=(190, 50, 40))
    cr.restore()
def pizza_boxes(t):
    if t < T_TL0: return 0
    for i in range(7):
        if t < B[i + 1]: return i
    return 7

# ================================================================ inside GAME CAVE
def draw_store(cr, t):
    O.draw_store_inside(cr, t, IX - 6000, IX + 6000)
    vx0, vy0, vx1, vy1 = O._visible(cr)
    if t < CUT_TV - FR:                                                         # a SOLD OUT strip over the shelves
        sk_rect(cr, IX - 330, FLOOR_Y - 1180, IX + 30, FLOOR_Y - 1080, 5, sid=21790, fill=(1, 1, 0.97))
        draw_text(cr, "SOLD OUT", IX - 150, FLOOR_Y - 1130, 60, color=(200, 30, 40))

def draw_counter(cr, t):
    x = CTR_X
    sk_rect(cr, x - 450, CTR_TOP, x + 450, FLOOR_Y - 10, 7, sid=21800, fill=(0.30, 0.28, 0.42))
    sk_rect(cr, x - 480, CTR_TOP - 30, x + 480, CTR_TOP + 10, 6, sid=21801, fill=(0.45, 0.42, 0.60))
    # register
    sk_rect(cr, x + 220, CTR_TOP - 150, x + 420, CTR_TOP - 30, 5, sid=21802, fill=(0.18, 0.18, 0.22))
    sk_rect(cr, x + 240, CTR_TOP - 260, x + 400, CTR_TOP - 160, 5, sid=21803, fill=(0.10, 0.30, 0.20))
    if t >= T_SCAN:
        draw_text(cr, "$569.98", x + 320, CTR_TOP - 210, 34, color=(120, 255, 150))

def draw_console_box(cr, x, yb, s=1.0, ang=0.0, sid=21850):
    """a generic next-gen console box (white with a black band, a drawing of the console). No logo."""
    cr.save(); cr.translate(x, yb); cr.rotate(ang); cr.scale(s, s)
    sk_rect(cr, -95, -250, 95, 0, 5, sid=sid, fill=(0.97, 0.97, 0.99))
    cr.rectangle(-93, -250, 186, 50); cr.set_source_rgb(0.12, 0.14, 0.30); cr.fill()
    sk_poly(cr, [(-30, -40), (-48, -185), (-8, -185), (0, -40)], 3, sid=sid + 1, fill=(1, 1, 1))
    sk_poly(cr, [(0, -40), (8, -185), (48, -185), (30, -40)], 3, sid=sid + 2, fill=(1, 1, 1))
    cr.rectangle(-6, -180, 12, 140); cr.set_source_rgb(0.12, 0.12, 0.14); cr.fill()
    draw_text(cr, "NEXT GEN", 0, -225, 26, color=(255, 255, 255))
    cr.restore()
def draw_game_box(cr, x, yb, s=1.0, ang=0.0, sid=21860):
    cr.save(); cr.translate(x, yb); cr.rotate(ang); cr.scale(s, s)
    cr.translate(0, -105); draw_poster_mini(cr); cr.restore()
def draw_poster_mini(cr):
    w, h = 150, 210
    bands = ((0.98, 0.45, 0.62), (1.0, 0.68, 0.42), (1.0, 0.80, 0.40), (0.55, 0.30, 0.62))
    for i, c in enumerate(bands):
        cr.rectangle(-w / 2, -h / 2 + i * h / 4, w, h / 4 + 1); cr.set_source_rgb(*c); cr.fill()
    cr.arc(0, 30, 45, math.pi, 2 * math.pi); cr.set_source_rgb(1.0, 0.92, 0.45); cr.fill()
    draw_text(cr, "6", 0, -30, 110, color=(255, 255, 255))
    sk_rect(cr, -w / 2, -h / 2, w / 2, h / 2, 4, sid=21861, fill=None)

def draw_tag(cr, x, y):
    sk_poly(cr, [(x - 70, y - 30), (x + 60, y - 30), (x + 85, y), (x + 60, y + 30), (x - 70, y + 30)], 4, sid=21870, fill=(1.0, 0.85, 0.25))
    draw_text(cr, "LAST ONE", x, y, 26, color=(160, 30, 30))

def draw_sock(cr, x, y, ang=0.0, full=1.0):
    """a huge bulging sock of pennies, held at its top (x, y); ang tips it."""
    cr.save(); cr.translate(x, y); cr.rotate(ang)
    bul = 0.5 + 0.5 * full
    sk_poly(cr, [(-40, 0), (40, 0), (60 * bul + 10, 150), (80 * bul + 20, 260), (40, 330), (-60, 330), (-90 * bul, 250), (-70 * bul, 120)], 6,
            sid=21880, fill=(0.95, 0.95, 0.92))
    sk_rect(cr, -46, -10, 46, 40, 5, sid=21881, fill=(0.85, 0.30, 0.30))
    cr.restore()
def sock_mouth(t, p):
    return (p["rhand"][0] + 10, p["rhand"][1] - 10)

PENNY = (0.80, 0.48, 0.25)
def pile_h(t):
    """penny mound height above the counter top."""
    return 340 * smooth(ramp(t, T_POUR0 + 0.15, T_POUR1 + 0.1))
def draw_pile(cr, t):
    h = pile_h(t)
    if h < 2: return
    x = CTR_X + 120; w = 470 + 0.4 * h
    pts = [(x - w, CTR_TOP + 10)]
    for i in range(1, 20):
        u = i / 20; px = x - w + 2 * w * u
        py = CTR_TOP - h * math.sin(math.pi * u) ** 0.8 + 8 * math.sin(i * 2.3)
        pts.append((px, py))
    pts.append((x + w, CTR_TOP + 10))
    sk_poly(cr, pts, 6, sid=21900, fill=PENNY)
    rng = random.Random(21)
    for k in range(int(70 * min(1.0, h / 200))):                               # coin faces
        u = rng.random(); px = x - w + 2 * w * u
        top = CTR_TOP - h * math.sin(math.pi * u) ** 0.8
        py = rng.uniform(top + 15, CTR_TOP)
        cr.arc(px, py, 14, 0, 2 * math.pi); cr.set_source_rgb(0.92, 0.62, 0.35); cr.fill_preserve()
        cr.set_source_rgba(0.35, 0.18, 0.10, 0.7); cr.set_line_width(3); cr.stroke()
    # spill down the front of the counter + a heap on the floor
    sp = smooth(ramp(t, T_POUR0 + 0.8, T_POUR1 + 0.2))
    if sp > 0.01:
        for k in range(5):
            xx = CTR_X - 380 + 170 * k
            yy = CTR_TOP + (FLOOR_Y - CTR_TOP) * sp
            sk_poly(cr, [(xx - 30, CTR_TOP), (xx + 30, CTR_TOP), (xx + 26 + 6 * k % 3, yy), (xx - 26, yy)], 4, sid=21910 + k, fill=PENNY)
        sk_ell(cr, CTR_X - 40, FLOOR_Y + 10, 520 * sp, 50 * sp + 1, 5, sid=21920, fill=PENNY)

def draw_stream(cr, t, p):
    """the penny waterfall from the sock's mouth onto the counter (runs while pouring, tapers off)."""
    if not (T_POUR0 <= t < T_POUR1 + 0.3): return
    a = sock_mouth(t, p)
    a = (a[0] + 120, a[1] + 60)
    end = (CTR_X + 60, CTR_TOP - pile_h(t) * 0.8)
    taper = 1 - smooth(ramp(t, T_POUR1 - 0.3, T_POUR1 + 0.3))
    for k in range(60):
        u = ((k / 60) + t * 2.2) % 1.0
        x = lerp(a[0], end[0], u) + 18 * math.sin(k * 3.1)
        y = a[1] + (end[1] - a[1]) * u * u + 10 * math.cos(k * 1.7)
        r = 13 * taper * (0.7 + 0.3 * math.sin(k))
        if r < 2: continue
        cr.arc(x, y, r, 0, 2 * math.pi); cr.set_source_rgb(*PENNY); cr.fill_preserve()
        cr.set_source_rgba(0.3, 0.15, 0.08, 0.8); cr.set_line_width(3); cr.stroke()

def draw_beam(cr, t):
    if not (T_BEAM0 <= t < T_BEAM1 + 0.3): return
    a = smooth(ramp(t, T_BEAM0, T_BEAM0 + 0.3)) * (1 - smooth(ramp(t, T_BEAM1, T_BEAM1 + 0.3)))
    hx = HIS_I + 0
    cr.move_to(hx - 120, -400); cr.line_to(hx + 120, -400); cr.line_to(hx + 330, FLOOR_Y); cr.line_to(hx - 330, FLOOR_Y); cr.close_path()
    cr.set_source_rgba(1.0, 0.95, 0.65, 0.45 * a); cr.fill()
    for k in range(10):                                                          # dust motes
        u = (k * 0.137 + t * 0.15) % 1.0
        cr.arc(hx - 200 + 400 * ((k * 0.61) % 1), FLOOR_Y - 1500 * u, 5, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 0.8, 0.8 * a); cr.fill()

# ---------------------------------------------------------------- the TV corner
def draw_tv_screen(cr, t):
    x, yb = TVX, FLOOR_Y
    sx0, sy0, sx1, sy1 = x - 230, yb - 750, x + 230, yb - 450
    cr.rectangle(sx0, sy0, sx1 - sx0, sy1 - sy0); cr.set_source_rgb(0.06, 0.08, 0.16); cr.fill()
    if t < T_UPD:
        draw_text(cr, "PRESS START", x, (sy0 + sy1) / 2, 52, color=(255, 255, 255), alpha=0.5 + 0.5 * (int(t * 3) % 2))
        return
    n = 1 if t < T_UPD2 else 2
    draw_text(cr, f"UPDATE {n} OF 47", x, sy0 + 55, 48, color=(255, 255, 255))
    draw_text(cr, "150 GB", x, sy0 + 115, 40, color=(180, 200, 255))
    if n == 1:
        prog = 0.01 * ramp(t, T_UPD, T_BAR100 - 0.3)
        prog = prog + 0.99 * smooth(ramp(t, T_BAR100 - 0.3, T_BAR100))
    else:
        prog = 0.0
    bx0, bx1, by = sx0 + 40, sx1 - 40, sy0 + 175
    cr.rectangle(bx0, by, bx1 - bx0, 34); cr.set_source_rgb(0.25, 0.25, 0.32); cr.fill()
    cr.rectangle(bx0, by, (bx1 - bx0) * prog, 34); cr.set_source_rgb(0.30, 0.85, 0.45); cr.fill()
    draw_text(cr, f"{int(prog * 100)}%", x, by + 80, 40, color=(255, 255, 255))
    if t >= T_LEFT and n == 1 and prog < 0.5:
        draw_text(cr, "TIME LEFT: 11 HRS", x, by + 130, 34, color=(255, 200, 120))
    if n == 2 or t >= T_BAR100:
        if n == 2: draw_text(cr, "TIME LEFT: 11 HRS", x, by + 130, 34, color=(255, 200, 120))

def draw_tv_corner(cr, t):
    O.draw_tv(cr, TVX, FLOOR_Y, t, screen="off", sid=21950)
    draw_tv_screen(cr, t)
    # the open console box next to him + the cable
    draw_console_box(cr, HIS_TV + 330, FLOOR_Y + 10, s=0.8, sid=21960)
    draw_game_box(cr, HIS_TV + 470, FLOOR_Y + 10, s=0.7, ang=0.08)
    sketch_line(cr, [(TVX + 200, FLOOR_Y - 330), (TVX + 300, FLOOR_Y - 60), (HIS_TV - 20, FLOOR_Y - 230)], 5, sid=21970, amp=0.5)

# ================================================================ backgrounds
def world(cr, t):
    if t < CUT1 - FR:
        O.draw_city_night(cr, t, RX - 6000, RX + 6000)
        O.draw_lamp(cr, RX - 1700); O.draw_lamp(cr, RX + 2300, sid=18132)
        O.draw_restaurant(cr, RX, FLOOR_Y, t, door=0.0)
        O.draw_street_clock(cr, RX - 1150, FLOOR_Y, hour=10.0, minute=31.0)
        return
    if t < CUT_IN - FR:
        draw_mall(cr, t); return
    draw_store(cr, t)
    if t >= CUT_TV - FR:
        draw_tv_corner(cr, t)
S.background(world)

# ================================================================ props
_rng = random.Random(7)
DOGS = [(CURB_HIM + _rng.uniform(-900, 900), FLOOR_Y + _rng.uniform(20, 90), _rng.uniform(-0.4, 0.4)) for _ in range(14)]
PIZ_SCATTER = [(HIS_Q - 300 + 160 * k + 40 * math.sin(k * 2.0), FLOOR_Y + 60 + 25 * (k % 3), 0.5 * math.sin(k * 1.3)) for k in range(7)]

def props_back(cr, t, p, ly):
    if ly != "back": return
    if t < CUT1 - FR:
        O.draw_hotdog_cart(cr, CART, FLOOR_Y, t, wreck=1.0)
        for k in range(3):
            u = (t * 0.5 + k / 3) % 1.0
            O.draw_smoke_puff(cr, CART - 80 + 60 * k + 40 * u, FLOOR_Y - 600 - 500 * u, 60 + 70 * u, alpha=0.35 * (1 - u), dark=0.5)
        for k, v in enumerate(VIOS): draw_violinist(cr, t, v, k)
        for (x, y, a) in DOGS: O.draw_hotdog(cr, x, y, s=0.75, ang=a)
        draw_her(cr, t)
        return
    if t < CUT_IN - FR:
        for i in range(6, -1, -1):
            if line_on(i, t): draw_line_person(cr, t, i)
        if T_DOOR1 - FR <= t < T_OPEN + 0.6:
            q = draw_clerk(cr, t)
            draw_door_sign(cr, t, q)
            L.draw_grips(cr, q)
        if t < T_FLAT:                                                          # pizza boxes stacked beside him
            for k in range(pizza_boxes(t)):
                draw_pizza_box(cr, HIS_Q - 190, FLOOR_Y - 36 * k, ang=0.04 * math.sin(k * 2.0), sid=21700 + k)
        return
    if t < CUT_TV - FR:                                                         # inside: the clerk, the counter
        draw_clerk(cr, t)
        draw_counter(cr, t)
        draw_pile(cr, t)
        if t < T_HOIST + 0.2:
            draw_console_box(cr, BOX_A, CTR_TOP - 25)
            draw_game_box(cr, BOX_B, CTR_TOP - 25)
            if t < T_SLAP: draw_tag(cr, (BOX_A + BOX_B) / 2, CTR_TOP - 320)
        if t >= T_RECEIPT:                                                      # a receipt sticks up out of the pile
            u = smooth(ramp(t, T_RECEIPT, T_RECEIPT + 0.3))
            sk_rect(cr, CTR_X + 60, CTR_TOP - pile_h(t) - 150 * u, CTR_X + 130, CTR_TOP - pile_h(t) + 20, 4, sid=21990, fill=(1, 1, 0.97))
        draw_beam(cr, t)
        return

def props_front(cr, t, p, ly):
    if ly != "front": return
    if CUT1 - FR <= t < CUT_IN - FR:
        if T_FLAT <= t:                                                         # scattered pizza boxes
            for k, (x, y, a) in enumerate(PIZ_SCATTER[:7]): draw_pizza_box(cr, x, y, ang=a, sid=21720 + k)
        if T_STAMP <= t < T_STAMP1 + 0.6:                                        # the stampede cloud
            u = ramp(t, T_STAMP, T_STAMP1 + 0.6, "linear")
            cx = cloud_x(t)
            sc = 1.0 if u < 0.8 else 1 - (u - 0.8) / 0.2
            for k, (dx, dy, r) in enumerate(((-300, -200, 260), (-60, -380, 300), (220, -220, 260), (-150, 30, 240), (150, 0, 250), (380, -60, 200),
                                            (-420, -40, 200))):
                O.draw_smoke_puff(cr, cx + dx * sc + 30 * math.sin(t * 9 + k), FLOOR_Y - 330 + dy * sc + 25 * math.cos(t * 11 + k),
                                  r * sc * (0.9 + 0.1 * math.sin(t * 13 + k)), alpha=1.0, dark=0.15)
            if sc > 0.3:                                                         # flailing feet and fists
                for k in range(9):
                    ang = t * 14 + k * 2.1
                    ex = cx + 420 * sc * math.cos(k * 1.7 + t * 3); ey = FLOOR_Y - 330 + 300 * sc * math.sin(k * 2.3 + t * 4)
                    sketch_line(cr, [(ex, ey), (ex + 60 * math.cos(ang), ey + 60 * math.sin(ang))], 9, sid=21800 + k, amp=0.3)
                    if k % 2: C.draw_foot(cr, (ex + 70 * math.cos(ang), ey + 70 * math.sin(ang)), math.cos(ang), sid=21810 + k)
                    else:
                        cr.arc(ex + 70 * math.cos(ang), ey + 70 * math.sin(ang), 20, 0, 2 * math.pi); cr.set_source_rgb(1, 1, 1); cr.fill_preserve()
                        cr.set_source_rgb(0.1, 0.1, 0.1); cr.set_line_width(6); cr.stroke()
        return
    if CUT_IN - FR <= t < CUT_TV - FR:
        if T_POP <= t < T_POUR1 + 0.5:                                          # the sock
            hx, hy = p["rhand"]
            ang = -0.2 if t < T_TIP0 else -0.2 - 2.0 * smooth(ramp(t, T_TIP0, T_TIP0 + 0.3))
            draw_sock(cr, hx, hy, ang=ang, full=1 - ramp(t, T_POUR0, T_POUR1))
            L.draw_grips(cr, p)
        draw_stream(cr, t, p)
        if t >= T_HOIST + 0.2:                                                   # boxes overhead
            u = smooth(ramp(t, T_HOIST - 0.1, T_HOIST + 0.35))
            lx, ly_ = p["lhand"]; rx, ry = p["rhand"]
            draw_console_box(cr, lerp(BOX_A, lx - 30, u), lerp(CTR_TOP - 25, ly_ + 10, u))
            draw_game_box(cr, lerp(BOX_B, rx + 60, u), lerp(CTR_TOP - 25, ry + 10, u))
            L.draw_grips(cr, p)
        return
    if t >= CUT_TV - FR and t < T_STAND + 0.2:                                   # the controller
        hx = (p["lhand"][0] + p["rhand"][0]) / 2; hy = (p["lhand"][1] + p["rhand"][1]) / 2
        O.draw_controller(cr, hx, hy - 10, s=0.8)
        L.draw_grips(cr, p)
S.prop(props_back)
S.prop(props_front)

def lens(cr, t):
    """register insert (screen space, under the card)."""
    if CUT_REG <= t + FR < CUT_REG1:
        cr.set_source_rgb(0.12, 0.12, 0.16); cr.paint()
        sk_rect(cr, 140, 560, 940, 1500, 10, sid=22000, fill=(0.06, 0.20, 0.12))
        jit = 2 * math.sin(t * 40)
        rows = (("CONSOLE", "$499.99"), ("GAME", "$69.99"))
        for i, (a, b_) in enumerate(rows):
            draw_text(cr, a, 210 + jit, 700 + i * 120, 62, anchor="left", color=(120, 255, 150))
            draw_text(cr, b_, 800 + jit, 700 + i * 120, 62, color=(120, 255, 150))
        sketch_line(cr, [(200, 950), (880, 950)], 5, sid=22001, amp=0.3, color=(0.5, 1.0, 0.6))
        k = smooth(ramp(t, CUT_REG + 0.3, CUT_REG + 0.5))
        draw_text(cr, "TOTAL", 540 + jit, 1080, 80, color=(120, 255, 150))
        draw_text(cr, "$569.98", 540 + jit, 1260, 150 * (0.7 + 0.3 * k), color=(255, 255, 255), alpha=k)
    # daylight wash over the mall (the time-lapse)
    if T_TL0 <= t < T_TL1:
        dl = daylight(t)
        cr.set_source_rgba(1.0, 0.98, 0.85, 0.10 * dl); cr.paint()
S.overlays.insert(0, lens)

# ================================================================ sounds
def sfx_heart():
    tt = np.arange(int(0.5 * L.SR)) / L.SR
    s = np.sin(2 * np.pi * 55 * tt) * np.exp(-tt / 0.06) + 0.7 * np.sin(2 * np.pi * 50 * tt) * np.exp(-np.clip(tt - 0.18, 0, None) / 0.06) * (tt > 0.18)
    return (s * 0.9).astype(np.float32)
def sfx_rumble_feet(dur=2.2):
    n = int(dur * L.SR); out = np.zeros(n, np.float32); rng = np.random.default_rng(5)
    for k in range(int(dur * 22)):
        i = int(rng.uniform(0, dur - 0.2) * L.SR); tt = np.arange(int(0.12 * L.SR)) / L.SR
        out[i:i + len(tt)] += (np.sin(2 * np.pi * rng.uniform(60, 110) * tt) * np.exp(-tt / 0.03) * rng.uniform(0.4, 0.9)).astype(np.float32)
    env = np.minimum(1, np.arange(n) / (0.2 * L.SR)) * np.minimum(1, (n - np.arange(n)) / (0.4 * L.SR))
    return (out * env * 0.6).astype(np.float32)
def sfx_coins(dur=2.4):
    n = int(dur * L.SR); out = np.zeros(n, np.float32); rng = np.random.default_rng(9)
    for k in range(int(dur * 70)):
        i = int(rng.uniform(0, dur - 0.1) * L.SR); tt = np.arange(int(0.05 * L.SR)) / L.SR
        f = rng.uniform(2800, 5200)
        out[i:i + len(tt)] += (np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.01) * rng.uniform(0.1, 0.35)).astype(np.float32)
    env = np.minimum(1, (n - np.arange(n)) / (0.5 * L.SR))
    return (out * env).astype(np.float32)
def sfx_kaching():
    tt = np.arange(int(0.9 * L.SR)) / L.SR
    s = (np.sin(2 * np.pi * 1760 * tt) + 0.6 * np.sin(2 * np.pi * 2637 * tt)) * np.exp(-np.clip(tt - 0.08, 0, None) / 0.25) * (tt > 0.08)
    s += np.random.default_rng(3).standard_normal(len(tt)) * np.exp(-tt / 0.02) * 0.3
    return (s * 0.35).astype(np.float32)
def sfx_choir(dur=2.2):
    tt = np.arange(int(dur * L.SR)) / L.SR; out = np.zeros(len(tt))
    for m in (57, 61, 64, 69):
        f = 440 * 2 ** ((m - 69) / 12)
        for h, a in ((1, 1.0), (2, 0.35), (3, 0.15)):
            out += a * np.sin(2 * np.pi * f * h * tt * (1 + 0.004 * np.sin(2 * np.pi * 5 * tt)))
    env = np.minimum(1, tt / 0.4) * np.minimum(1, (dur - tt) / 0.6)
    return (out * env * 0.12).astype(np.float32)
def sfx_beep():
    tt = np.arange(int(0.25 * L.SR)) / L.SR
    return (np.sign(np.sin(2 * np.pi * 1000 * tt)) * 0.25 * (tt < 0.2)).astype(np.float32)
L.SYNTH.update(heart=sfx_heart, rumble_feet=sfx_rumble_feet, coins=sfx_coins, kaching=sfx_kaching, choir=sfx_choir, beep=sfx_beep)

for i in range(1, 7): S.sfx(B[i], "tick", 0.05)                                  # the date board flips
k = 0
tb = T_CLK0 + 0.1
while tb < T_OPEN - 0.2:
    S.sfx(tb, "heart", 0.07 + 0.01 * min(k, 6)); tb += 0.62 - 0.02 * min(k, 6); k += 1
for s_ in range(4): S.sfx(T_OPEN - 4 + s_ + 0.0, "tick", 0.04) if T_OPEN - 4 + s_ > T_CLK0 else None
S.sfx(T_DOOR1, "squeak", 0.03)
S.sfx(T_SIGNFLIP, "flip", 0.05)
S.sfx(T_OPEN - 0.05, "flip", 0.05)
S.sfx(T_OPEN, "beep", 0.05)
S.sfx(T_SCAN, "beep", 0.03)
S.sfx(CUT_REG + 0.35, "thud", 0.07)
S.sfx(T_POUR0, "coins", 0.10, dur=T_POUR1 - T_POUR0 + 0.3)
S.sfx(T_KACHING, "kaching", 0.08)
S.sfx(T_RECEIPT, "zip", 0.04)
S.sfx(T_BEAM0, "choir", 0.07, dur=T_BEAM1 - T_BEAM0 + 0.2)
S.sfx(T_UPD, "boop", 0.04)
S.sfx(T_UPD2, "ding", 0.05)
S.sfx(T_FLAT, "splat", 0.05)

if __name__ == "__main__":
    print(f"end {T_END:.2f}", file=sys.stderr)
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        S.build()
        import cairo
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, L.W, L.H)
        for a in sys.argv[2:]:
            tt = float(a); L.render_frame(tt, surf); surf.write_to_png(f"still_{tt:05.2f}.png")
    else:
        S.render("day021.mp4")
