"""Day 22: @alex03330_ (IG, 2 likes): "Use dark magic to transform the world into gta 6 except your the main character..."
(card trimmed before its last clause). Justin's outline: he flirts with the game's leading lady, his wife catches him,
takes the baby and leaves again; as many in-jokes as possible, nothing sexual; he loses both. See BEATS.md.
The leading lady is an ORIGINAL character (red bob, yellow sundress, round shades) and is never named on screen.
"""
import sys, os, math, random, wave
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import numpy as np
import cairo
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, lerp, FLOOR_Y
from ink import smooth, sketch_line, draw_text

HERE = os.path.dirname(os.path.abspath(__file__))
FR = 1 / 30
sk_rect, sk_poly, sk_circ, sk_ell = O.sketch_rect, O.sketch_poly, O.sketch_circle, O.sketch_ellipse

# ================================================================ places
IX = 8000000.0                       # inside GAME CAVE (day 21/22)
TVX = IX - 1500.0
HIS_TV = TVX + 560.0
NX = 9000000.0                       # the neon city
DOOR_X = NX - 1150.0
PALM_X = NX - 160.0
HER_X = NX + 470.0
CAR_X = NX + 720.0
WIFE_X = NX - 450.0
BOOM_X = NX - 200.0

# ================================================================ timeline
T_READ = 0.3
T_TV = 2.6; T_TVBACK = 3.2
T_BOOK = 3.6                    # pocket_pull -> POP at +2.1
T_OPEN = 6.1; T_BAR0, T_BAR1 = 6.4, 6.9; T_47 = 6.95; T_START = 7.25
T_BLAST = 7.0; CUT1 = 7.6
T_RUN = 7.7; T_HUD = (9.0, 9.25, 9.5)
T_SEEHER = 10.2; T_SHADES = 10.5; T_METER = 10.6
T_WALK1 = 11.0; T_LEAN = 11.8; T_BEND0, T_BEND1 = 12.1, 12.6; T_FALL = 12.6
T_UP0 = 14.0; T_UP1 = 14.4
T_GUNS = 14.8; T_GUNS1 = 16.0
T_BOX = 16.4                    # POP at 18.5
T_SETDOWN = 19.0; T_PLAY = 19.5
T_CHEAT0 = 21.7; CHEAT = ["R1", "R2", "L1", "R2", "LEFT", "DOWN", "RIGHT", "UP", "LEFT", "DOWN", "RIGHT", "UP"]
T_CHEAT1 = T_CHEAT0 + 0.15 * len(CHEAT); T_ACT = T_CHEAT1 + 0.15
T_RAIN0, T_RAIN1 = T_ACT + 0.2, T_ACT + 3.8
T_SHUP = T_ACT + 0.8
T_PAT = 27.0; T_WALK2 = 27.4
T_CRY = 28.4; T_STARS = [28.5, 28.8, 29.1, 29.4, 29.7]
T_TURN = 29.9; T_PAN = 30.2
T_GUNS2 = 32.0; T_GUNS2_1 = 33.3
T_SHRUG = 33.6; T_INCAR = 34.4; T_DRIVE0, T_DRIVE1 = 34.8, 35.5
T_LEAVE0, T_LEAVE1 = 35.8, 37.0; T_REACH = 36.0
T_BACK0, T_BACK1 = 37.6, 38.4; T_GRAB = 38.6; T_OUT0, T_OUT1 = 39.0, 39.9
T_BILL0, T_BILL1 = 40.1, 40.8
T_TIP = 41.0; T_GREY0, T_GREY1 = 41.6, 42.0; T_WASTED = 42.0; T_COLOR = 44.4
T_GETUP = 44.8
T_RING = 45.8; T_PHONE = 46.0; T_DECLINE = 47.6
T_ASK = 48.4; HOLD = 8.0

STAGES = [(0.0, 0), (T_METER, 0), (T_GUNS1 - 0.2, 5), (T_PLAY + 0.6, 40), (T_SHUP + 0.3, 90), (T_PAT + 0.3, 99), (T_DRIVE0 + 0.4, 0)]
def meter(t):
    v = 0
    for t0, val in STAGES:
        if t >= t0: v = val
    return v
def stars_lit(t): return sum(1 for s in T_STARS if t >= s)
def money(t):
    if t < T_RAIN0: return 0
    u = smooth(ramp(t, T_RAIN0, T_RAIN0 + 1.8))
    return int(999999999 * u)

# ================================================================ poses
def P(name, **kw): L.POSES[name] = kw
P("flat", **dict(L.POSES["lie_back"], nowalk=1.0))
P("lean_palm", relb=(650, 820), rhand=(700, 760), lelb=(470, 1000), lhand=(500, 1080), rhand_t="flat")
P("fguns", lelb=(600, 930), lhand=(720, 900), relb=(640, 960), rhand=(770, 950))
P("fguns_l", relb=(480, 930), rhand=(360, 900), lelb=(440, 960), lhand=(310, 950))
P("poke", relb=(640, 900), rhand=(720, 820), lelb=(470, 1000), lhand=(500, 1080))
P("reach_l", lelb=(400, 900), lhand=(300, 880), relb=(610, 1000), rhand=(590, 1080))
P("book_open", lelb=(460, 990), lhand=(480, 900), relb=(620, 990), rhand=(600, 900), lhand_t="grip", rhand_t="grip")
# others
P("w_cradle", lelb=(460, 1000), lhand=(520, 960), relb=(620, 1000), rhand=(570, 960), lhand_t="grip", rhand_t="grip")
P("w_carry2", lelb=(460, 1000), lhand=(530, 960), relb=(640, 1010), rhand=(660, 1100), lhand_t="grip", rhand_t="grip")
P("w_grab", **dict(L.POSES["crouch"], lelb=(460, 1050), lhand=(520, 1020), relb=(650, 1150), rhand=(700, 1260), lhand_t="grip", rhand_t="grip"))
P("h_lean", **dict(L.POSES["arms_crossed"], lean=0.10))
P("h_pat", relb=(650, 1000), rhand=(760, 1080), rhand_t="flat")
P("h_shades", relb=(620, 930), rhand=(560, 800))

# ================================================================ scene (him)
S = M.Scene(start_body="stand", start_face="deadpan", x0=HIS_TV - 540)
S.auto_blinks = True
S.floor = False
S.card("alex03330_", "Use dark magic to transform the world into gta 6 except your the main character…", "2", t0=0.3)
CAM_S = (HIS_TV - 200, 930, 0.95)
S.camkeys[0] = (0.0, CAM_S, 0); S.cam = CAM_S

S.read_card(T_READ, react="deadpan", lines=2)
S.set(T_TV, "stand", "deadpan", dur=0.3, turn=-0.8, look=(-1.0, -0.4))
S.set(T_TVBACK, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), lid=0.4)
def draw_book_held(cr, x, y, s, t, p):
    if t >= T_BLAST + 0.1: return                       # used up in the blast
    if t >= T_OPEN:                                     # open: two pages + a purple glow
        g = ramp(t, T_OPEN, T_OPEN + 0.4) * (0.7 + 0.3 * math.sin(t * 12))
        cr.arc(x - 60, y - 40, 170 * s, 0, 2 * math.pi); cr.set_source_rgba(0.62, 0.25, 0.95, 0.35 * g); cr.fill()
        sk_poly(cr, [(x - 60, y - 10), (x - 170, y - 30), (x - 170, y - 150), (x - 60, y - 130)], 4, sid=22201, fill=(0.95, 0.93, 0.98))
        sk_poly(cr, [(x - 60, y - 10), (x + 50, y - 30), (x + 50, y - 150), (x - 60, y - 130)], 4, sid=22202, fill=(0.95, 0.93, 0.98))
        for k in range(4):
            sketch_line(cr, [(x - 150, y - 120 + 22 * k), (x - 80, y - 105 + 22 * k)], 3, sid=22210 + k, color=(0.45, 0.15, 0.6))
            sketch_line(cr, [(x - 40, y - 105 + 22 * k), (x + 30, y - 120 + 22 * k)], 3, sid=22220 + k, color=(0.45, 0.15, 0.6))
        return
    cr.save(); cr.translate(x, y - 90); cr.scale(s, s)
    sk_rect(cr, -95, -120, 95, 120, 6, sid=22200, fill=(0.10, 0.08, 0.14))
    draw_text(cr, "DARK", 0, -45, 42, color=(190, 120, 255))
    draw_text(cr, "MAGIC", 0, 5, 42, color=(190, 120, 255))
    cr.arc(0, 70, 26, 0, 2 * math.pi); cr.set_source_rgb(0.62, 0.25, 0.95); cr.set_line_width(5); cr.stroke()
    cr.restore()
S.pocket_pull(T_BOOK, "book", draw_book_held, (0, 0), held=True)
S.set(T_BOOK + 2.15, "stand", "deadpan", dur=0.2, look=(0.3, 0.6))
S.set(T_OPEN - 0.2, "book_open", "concentrating", dur=0.3, look=(0.0, 0.7), tilt=0.06)
S.sfx(T_OPEN, "twinkle", 0.06)
def bookhook(t, p):
    if T_OPEN - 0.2 <= t < T_BLAST + 0.1:
        S.objects["book"]["follow"] = "rhand"
    return p
S.hook(bookhook)
S.set(T_BAR0 + 0.2, "book_open", "surprised", dur=0.15, ease="snap", turn=-0.8, look=(-1.0, -0.4), eyescale=1.2)
S.set(T_BLAST, "cower", "shocked", dur=0.12, ease="snap", eyescale=1.3, curl_up=1.0)
S.sfx(T_BAR0, "zip", 0.06); S.sfx(T_47, "ding", 0.08)
S.sfx(T_BLAST, "kaboom", 0.35); S.shake(T_BLAST, 0.6, 22)
S.flash(CUT1, 0.6, color=(0.92, 0.82, 1.0))

# ---------------------------------------------------------------- B: out of the store, into the neon city
CAM_N = (NX + 200, 900, 0.85)
S.cut(CUT1 - FR, cam=(DOOR_X + 450, 900, 0.85), x=DOOR_X - 540)
S.set(CUT1 - FR, "stand", "dead_stare", dur=0.0)
S.run_to(T_RUN, NX - 280 - 540, dur=1.0)
S.camera(T_RUN, CAM_N[0], CAM_N[1], CAM_N[2], 1.3)
S.set(8.9, "stand", "deadpan", dur=0.3)
for k, th in enumerate(T_HUD): S.sfx(th, "tick", 0.07)
S.set(T_HUD[0] + 0.1, "stand", "deadpan", dur=0.3, look=(-0.9, -1.0))
S.set(T_SEEHER, "stand", "deadpan", dur=0.3, turn=0.7, look=(1.0, 0.0))
S.set(T_SEEHER + 0.4, "stand", "dead_stare", dur=0.2, turn=0.7, look=(1.0, 0.0), eyescale=1.15)
S.sfx(T_METER, "boop", 0.05)
# attempt 1: lean on the palm
S.set(T_WALK1, "stand", "smug", dur=0.4, turn=0.5, look=(1.0, 0.0))
S.set(T_LEAN, "lean_palm", "smug", dur=0.4, turn=0.4, look=(1.0, 0.0), lean=0.12)
S.set(T_BEND0, "lean_palm", "smug", dur=0.5, turn=0.4, look=(1.0, 0.0), lean=0.35)
S.set(T_FALL, "flat", "dead_stare", dur=0.25, ease="inn")
S.sfx(T_BEND0, "squeak", 0.05); S.sfx(T_FALL + 0.2, "thud", 0.15); S.shake(T_FALL + 0.2, 0.3, 8)
S.set(T_FALL + 0.6, "flat", "dead_stare", dur=0.3, look=(0.0, -0.8))
S.set(T_UP0, "crouch", "deadpan", dur=0.3, nowalk=1.0)
S.set(T_UP1, "stand", "deadpan", dur=0.3, ease="back", turn=0.6, look=(1.0, 0.0))
# attempt 2: finger guns
S.set(T_GUNS, "fguns", "cheeky", dur=0.2, ease="snap", turn=0.6, look=(1.0, 0.0), tilt=0.1)
S.sfx(T_GUNS + 0.2, "tok", 0.07); S.sfx(T_GUNS + 0.55, "tok", 0.07)
S.set(T_GUNS + 0.5, "fguns", "cheeky", dur=0.1, ease="snap", turn=0.6, look=(1.0, 0.0), tilt=0.14, lid=0.6)
S.set(T_GUNS1 - 0.3, "stand", "deadpan", dur=0.3, turn=0.6, look=(1.0, 0.0))
# attempt 3: the boombox
def draw_boom_held(cr, x, y, s, t, p):
    O.draw_boombox(cr, x, y - 80, s=0.55 * s, t=t, play=0.0)
S.pocket_pull(T_BOX, "boomh", draw_boom_held, (0, 0), held=True)
S.set(T_SETDOWN, "crouch", "deadpan", dur=0.3, nowalk=1.0, turn=0.5, look=(0.6, 0.6))
S.hide("boomh", T_SETDOWN + 0.3)
S.set(T_SETDOWN + 0.6, "stand", "deadpan", dur=0.3, turn=0.6, look=(1.0, 0.0))
S.sfx(T_SETDOWN + 0.3, "tap", 0.06)
# attempt 4: the cheat code (pokes the air for each button)
for i in range(len(CHEAT)):
    tt = T_CHEAT0 + 0.15 * i
    S.set(tt, "poke", "concentrating", dur=0.06, ease="snap", look=(0.6, -0.4), rhand=(720 + 20 * (i % 3), 820 + 15 * (i % 2)))
    S.set(tt + 0.08, "poke", "concentrating", dur=0.06, look=(0.6, -0.4), rhand=(690, 860))
    S.sfx(tt, "tap", 0.05)
S.set(T_ACT, "stand", "deadpan", dur=0.3, look=(-0.9, -1.0))
S.sfx(T_ACT, "ding", 0.09)
S.set(T_RAIN0 + 0.4, "stand", "deadpan", dur=0.4, look=(0.0, -1.0))
S.set(T_SHUP + 0.6, "stand", "smug", dur=0.4, turn=0.6, look=(1.0, 0.0), smile=0.25)
# the walk to the car -> the wanted stars -> the wife
S.walk_to(T_WALK2, NX + 140 - 540, dur=0.9)
S.set(T_CRY + 0.15, "stand", "dead_stare", dur=0.15, ease="snap", turn=0.6, look=(1.0, 0.0), eyescale=1.0)
S.set(T_STARS[2], "stand", "dead_stare", dur=1.0, turn=0.6, look=(0.6, -0.2), eyescale=1.35, pupil=0.6)
S.set(T_TURN, "stand", "dead_stare", dur=0.7, turn=-0.8, look=(-1.0, 0.0), eyescale=1.35, pupil=0.6, sweat=0.6)
for k in range(5): S.sfx(T_STARS[k], "ding", 0.05 + 0.01 * k)
S.sfx(T_CRY, "wah", 0.07)
for k in range(5): S.sfx(29.2 + 0.6 * k, "thud", 0.06)
S.camera(T_PAN, NX - 60, 900, 0.85, 0.6)
S.set(T_GUNS2, "fguns_l", "cheeky", dur=0.2, ease="snap", turn=-0.6, look=(-1.0, 0.0), tilt=-0.1, sweat=0.6)
S.sfx(T_GUNS2 + 0.2, "tok", 0.06)
S.set(T_GUNS2_1, "stand", "dead_stare", dur=0.6, turn=-0.6, look=(-1.0, 0.0), sweat=0.4)
S.set(T_DRIVE0 + 0.1, "stand", "dead_stare", dur=0.3, turn=0.8, look=(1.0, 0.0))
S.sfx(T_DRIVE0, "skid", 0.12); S.sfx(T_DRIVE0 + 0.1, "whoosh", 0.08)
S.camera(T_SHRUG, NX + 300, 900, 0.85, 0.5)
S.camera(T_LEAVE0, NX - 120, 900, 0.85, 0.6)
S.camera(T_OUT1 + 0.1, NX + 110, 900, 0.9, 0.8)
S.set(T_LEAVE0, "stand", "dead_stare", dur=0.3, turn=-0.8, look=(-1.0, 0.0))
S.set(T_REACH, "reach_l", "sad", dur=0.5, turn=-0.8, look=(-1.0, 0.0))
S.set(T_LEAVE1 + 0.2, "stand", "resigned", dur=0.6, turn=-0.6, look=(-1.0, 0.2))
S.set(T_GRAB, "stand", "dead_stare", dur=0.3, turn=-0.6, look=(-0.8, 0.6))
S.sfx(T_GRAB, "tap", 0.06)
S.set(T_OUT1 + 0.1, "stand", "dead_stare", dur=0.4, turn=0.0, look=(0.0, 0.0), lid=0.4)
S.set(T_BILL1, "stand", "dead_stare", dur=0.2, look=(0.0, -0.6), lid=0.5)
S.sfx(T_BILL1, "pat", 0.04)
S.set(T_TIP, "flat", "dead_stare", dur=0.6, ease="inn")
S.sfx(T_TIP + 0.55, "thud", 0.12)
S.sfx(T_WASTED, "thud", 0.25)
S.set(T_GETUP, "crouch", "deadpan", dur=0.3, nowalk=1.0)
S.set(T_GETUP + 0.4, "stand", "deadpan", dur=0.3, ease="back")
# the phone
for k in range(3): S.sfx(T_RING + 0.5 * k, "ding", 0.07)
S.set(T_PHONE + 0.2, "stand", "deadpan", dur=0.3, turn=-0.5, look=(-0.9, -0.5))
S.set(T_PHONE + 1.0, "stand", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lid=0.45)
S.set(T_DECLINE - 0.3, "reach_l", "dead_stare", dur=0.25, turn=-0.3, look=(-0.8, -0.4), lhand=(330, 900))
S.set(T_DECLINE + 0.3, "stand", "deadpan", dur=0.3)
S.sfx(T_DECLINE, "boop", 0.07)
S.x = NX + 140 - 540             # where he ends up (he walked toward the car)
S.the_ask(T_ASK, hold=HOLD)
T_END = S.t
S.blink(2.0, 9.8, 13.2, 17.5, 23.0, 27.0, 33.0, 38.0, 45.6)

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

# ---------------------------------------------------------------- the leading lady (original character)
H_HAIR, H_DRESS, HS = (0.85, 0.22, 0.16), (0.98, 0.80, 0.22), 0.92
H = Actor(HER_X, "h_lean", "bored", turn=-0.5, look=(-0.4, 0.0), lid=0.4)
H.blinks = [9.4, 13.9, 18.0, 22.2, 26.1, 31.3]
H.k(T_SHADES, "h_shades", "skeptical", dur=0.3, turn=-0.6, look=(-1.0, 0.1))
H.k(T_SHADES + 0.6, "h_lean", "skeptical", dur=0.3, turn=-0.6, look=(-1.0, 0.1))
H.k(T_FALL + 0.4, "h_lean", "skeptical", dur=0.3, turn=-0.6, look=(-1.0, 0.5), tilt=-0.08)
H.k(T_GUNS + 0.5, "h_lean", "skeptical", dur=0.3, turn=-0.6, look=(-1.0, 0.0), tilt=0.06)
for k in range(8):                                    # nods along to the music
    tt = T_PLAY + 0.3 + 0.5 * k
    H.k(tt, "h_lean", "happy", dur=0.2, turn=-0.5, look=(-0.8, 0.0), smile=0.5, tilt=0.09 * (1 if k % 2 else -1))
H.k(T_CHEAT0, "h_lean", "skeptical", dur=0.3, turn=-0.6, look=(-1.0, -0.2))
H.k(T_SHUP, "h_shades", "surprised", dur=0.25, turn=-0.6, look=(-0.4, -1.0), eyescale=1.2)
H.k(T_SHUP + 0.6, "h_lean", "laughing", dur=0.3, turn=-0.5, look=(-0.6, -0.6))
H.k(T_PAT, "h_pat", "happy", dur=0.3, turn=-0.6, look=(-1.0, 0.0), smile=0.7)
H.k(T_STARS[1], "h_pat", "surprised", dur=0.3, turn=-0.6, look=(-1.0, 0.0))
H.k(T_TURN + 0.2, "stand", "surprised", dur=0.4, turn=-0.9, look=(-1.0, 0.0))
H.k(T_GUNS2 + 0.4, "stand", "skeptical", dur=0.3, turn=-0.6, look=(-0.7, 0.0))
H.k(T_SHRUG, "shrug", "bored", dur=0.3, turn=-0.3, look=(0.0, 0.0))
H.k(T_SHRUG + 0.5, "stand", "bored", dur=0.3, turn=0.8, look=(1.0, 0.0))
H.walk(T_SHRUG + 0.5, T_INCAR, CAR_X - 30)
H.X.append((T_DRIVE0, CAR_X + 2400, T_DRIVE1 - T_DRIVE0, "inn"))
H.done()
def shades_state(t):
    """1 = on her eyes, 0 = pushed up on her head"""
    if t < T_SHADES: return 1.0
    if t < T_SHUP: return 1.0 - 0.6 * ramp(t, T_SHADES, T_SHADES + 0.3)     # lowered: peeking over them
    if t < T_SHRUG: return 0.0
    return ramp(t, T_SHRUG + 0.2, T_SHRUG + 0.5)
def car_x(t):
    if t < T_DRIVE0: return CAR_X
    return CAR_X + 2400 * ramp(t, T_DRIVE0, T_DRIVE1, "inn")

def draw_her(cr, t):
    q = H.pose(t)
    if t >= T_INCAR: q["lfoot"] = (q["lfoot"][0], q["lfoot"][1]); dy = -60
    else: dy = 0
    cr.save(); cr.translate(0, dy)
    O.draw_mom(cr, t, q, H.blink(t), s=HS, hair=H_HAIR, dress=H_DRESS, bun=False)
    hx, hy = scale_pt(q, q["head"], HS); tn = q.get("turn", 0.0)
    st = shades_state(t)
    gy = hy - 8 - 20 * (1 - st) * 0 - (1 - st) * 95
    gy = hy - 6 + (0 if st >= 0.99 else (22 if st > 0.3 else -95))
    if st >= 0.99: gy = hy - 6
    elif st > 0.3: gy = hy + 18
    else: gy = hy - 100
    gx = hx + 28 * tn
    for dx in (-36, 36):
        sk_circ(cr, gx + dx * (1 - 0.25 * abs(tn)), gy, 27, 5, sid=22300 + int(dx > 0), fill=(0.10, 0.10, 0.14))
    sketch_line(cr, [(gx - 12, gy - 4), (gx + 12, gy - 4)], 5, sid=22303)
    cr.restore()

# ---------------------------------------------------------------- his wife (+ the baby)
W_HAIR, W_DRESS = (0.62, 0.28, 0.16), (0.30, 0.66, 0.66)
W = Actor(WIFE_X - 900, "w_cradle", "annoyed", turn=0.8, look=(1.0, 0.0))
W.blinks = [32.9]
W.walk(28.0, 29.6, WIFE_X)
W.k(29.7, "w_cradle", "annoyed", dur=0.3, turn=0.7, look=(1.0, 0.0), lid=0.35)
W.k(31.0, "w_cradle", "angry", dur=0.6, turn=0.7, look=(1.0, 0.0), lid=0.2)
W.k(T_LEAVE0 - 0.2, "w_cradle", "angry", dur=0.3, turn=-0.8, look=(-1.0, 0.0), back=1.0)
W.walk(T_LEAVE0, T_LEAVE1, WIFE_X - 1100)
W.k(T_BACK0, "w_cradle", "annoyed", dur=0.1, turn=0.8, look=(1.0, 0.3), back=0.0)
W.walk(T_BACK0, T_BACK1, BOOM_X - 120)
W.k(T_BACK1 + 0.05, "w_grab", "annoyed", dur=0.25, turn=0.6, look=(0.8, 0.8))
W.k(T_GRAB + 0.2, "w_carry2", "annoyed", dur=0.3, turn=0.5, look=(1.0, 0.0))
W.k(T_OUT0 - 0.1, "w_carry2", "annoyed", dur=0.2, turn=-0.8, look=(-1.0, 0.0), back=1.0)
W.walk(T_OUT0, T_OUT1, WIFE_X - 1100)
W.done()
def draw_wife(cr, t):
    if t < 27.9 or (T_LEAVE1 <= t < T_BACK0) or t >= T_OUT1: return
    q = W.pose(t)
    WS = 0.92
    O.draw_mom(cr, t, q, W.blink(t), s=WS, hair=W_HAIR, dress=W_DRESS, bun=False)
    lh = scale_pt(q, q["lhand"], WS); rh = scale_pt(q, q["rhand"], WS)
    cry = 0.6 + 0.4 * math.sin(t * 9) if t < T_PAN + 1.0 else 0.25
    if q.get("back", 0.0) < 0.5:
        if t >= T_GRAB + 0.2:
            O.draw_baby(cr, lh[0] - 10, lh[1] - 10, ang=0.0, st={"eyes": "open", "cry": 0.0}, t=t, s=0.65)
        else:
            O.draw_baby(cr, (lh[0] + rh[0]) / 2 - 20, (lh[1] + rh[1]) / 2 - 10, ang=0.0, st={"eyes": "cry", "cry": cry}, t=t, s=0.65)
    if t >= T_GRAB + 0.2:
        O.draw_boombox(cr, rh[0] + (0 if q.get("back", 0.0) < 0.5 else -40), rh[1] + 50, s=0.45, t=t, play=0.0)
    cr.save(); fx = foot_c(q); cr.translate(fx, FLOOR_Y); cr.scale(WS, WS); cr.translate(-fx, -FLOOR_Y); L.draw_grips(cr, q); cr.restore()

# ================================================================ the money (rains down and stays)
_r = random.Random(22)
BILLS = []
for i in range(46):
    x = NX - 500 + _r.uniform(0, 1500); t0 = T_RAIN0 + _r.uniform(0, T_RAIN1 - T_RAIN0 - 1.0)
    BILLS.append((x, t0, _r.uniform(1.1, 1.6), _r.uniform(0, 6.28), FLOOR_Y + _r.uniform(-10, 60), _r.uniform(-0.5, 0.5)))
def draw_bills(cr, t):
    for i, (x, t0, d, ph, yl, al) in enumerate(BILLS):
        if t < t0: continue
        u = min(1.0, (t - t0) / d)
        y = lerp(-300, yl, u); xx = x + (40 * math.sin(ph + t * 4) if u < 1 else 0)
        a = al if u >= 1 else 0.5 * math.sin(ph + t * 5)
        O.draw_dollar(cr, xx, y, s=0.55, ang=a, sid=24150 + (i % 5) * 3)
def draw_last_bill(cr, t):
    if t < T_BILL0 or t >= T_TIP: return
    u = ramp(t, T_BILL0, T_BILL1)
    hx = NX + 140; y = lerp(-200, 780, smooth(u))
    O.draw_dollar(cr, hx + 50 * math.sin(t * 5) * (1 - u), y, s=0.55, ang=0.35 * math.sin(t * 6) * (1 - u))

# ================================================================ backgrounds
def draw_tv_screen(cr, t):
    x, yb = TVX, FLOOR_Y
    sx0, sy0, sx1, sy1 = x - 230, yb - 750, x + 230, yb - 450
    cr.rectangle(sx0, sy0, sx1 - sx0, sy1 - sy0); cr.set_source_rgb(0.06, 0.08, 0.16); cr.fill()
    if t >= T_START:
        draw_text(cr, "PRESS START", x, (sy0 + sy1) / 2, 52, color=(255, 255, 255), alpha=0.5 + 0.5 * (int(t * 3) % 2)); return
    n = 3 if t < T_47 else 47
    prog = 0.01 + 0.99 * smooth(ramp(t, T_BAR0, T_BAR1))
    draw_text(cr, f"UPDATE {n} OF 47", x, sy0 + 55, 48, color=(255, 255, 255))
    draw_text(cr, "150 GB", x, sy0 + 115, 40, color=(180, 200, 255))
    bx0, bx1, by = sx0 + 40, sx1 - 40, sy0 + 175
    cr.rectangle(bx0, by, bx1 - bx0, 34); cr.set_source_rgb(0.25, 0.25, 0.32); cr.fill()
    cr.rectangle(bx0, by, (bx1 - bx0) * prog, 34); cr.set_source_rgb(0.30, 0.85, 0.45); cr.fill()
    draw_text(cr, f"{int(prog * 100)}%", x, by + 80, 40, color=(255, 255, 255))

def draw_poster_mini(cr):
    w, h = 150, 210
    bands = ((0.98, 0.45, 0.62), (1.0, 0.68, 0.42), (1.0, 0.80, 0.40), (0.55, 0.30, 0.62))
    for i, c in enumerate(bands):
        cr.rectangle(-w / 2, -h / 2 + i * h / 4, w, h / 4 + 1); cr.set_source_rgb(*c); cr.fill()
    cr.arc(0, 30, 45, math.pi, 2 * math.pi); cr.set_source_rgb(1.0, 0.92, 0.45); cr.fill()
    draw_text(cr, "6", 0, -30, 110, color=(255, 255, 255))
    sk_rect(cr, -w / 2, -h / 2, w / 2, h / 2, 4, sid=21861, fill=None)
def draw_console_box(cr, x, yb, s=1.0, sid=21960):
    cr.save(); cr.translate(x, yb); cr.scale(s, s)
    sk_rect(cr, -95, -250, 95, 0, 5, sid=sid, fill=(0.97, 0.97, 0.99))
    cr.rectangle(-93, -250, 186, 50); cr.set_source_rgb(0.12, 0.14, 0.30); cr.fill()
    draw_text(cr, "NEXT GEN", 0, -225, 26, color=(255, 255, 255))
    cr.restore()

def store(cr, t):
    O.draw_store_inside(cr, t, IX - 6000, IX + 6000)
    O.draw_tv(cr, TVX, FLOOR_Y, t, screen="off", sid=21950)
    draw_tv_screen(cr, t)
    draw_console_box(cr, HIS_TV + 330, FLOOR_Y + 10, s=0.8)
    cr.save(); cr.translate(HIS_TV + 470, FLOOR_Y + 10 - 105 * 0.7); cr.scale(0.7, 0.7); cr.rotate(0.08); draw_poster_mini(cr); cr.restore()
    sketch_line(cr, [(TVX + 200, FLOOR_Y - 330), (TVX + 300, FLOOR_Y - 60), (HIS_TV - 20, FLOOR_Y - 230)], 5, sid=21970, amp=0.5)

SKY = [(-3000, (0.30, 0.16, 0.45)), (-200, (0.55, 0.22, 0.58)), (300, (0.88, 0.36, 0.55)), (650, (0.98, 0.55, 0.45)), (850, (1.0, 0.72, 0.42))]
HORIZON = FLOOR_Y - 430
def neon(cr, t):
    x0, x1 = NX - 4000, NX + 4000
    for i, (y, c) in enumerate(SKY):
        y1 = SKY[i + 1][0] if i + 1 < len(SKY) else HORIZON
        cr.rectangle(x0, y, x1 - x0, y1 - y + 1); cr.set_source_rgb(*c); cr.fill()
    # the striped sun
    sx, sy, r = NX + 520, HORIZON, 330
    cr.save(); cr.arc(sx, sy, r, math.pi, 2 * math.pi); cr.close_path(); cr.clip()
    cr.rectangle(sx - r, sy - r, 2 * r, r); cr.set_source_rgb(1.0, 0.86, 0.35); cr.fill()
    for k in range(5):
        yy = sy - 40 - 52 * k; hgt = 16 - 3 * k
        cr.rectangle(sx - r, yy, 2 * r, hgt); cr.set_source_rgb(0.98, 0.55, 0.45); cr.fill()
    cr.restore()
    # ocean + beach
    cr.rectangle(x0, HORIZON, x1 - x0, 160); cr.set_source_rgb(0.20, 0.62, 0.72); cr.fill()
    for k in range(6):
        yy = HORIZON + 20 + 24 * k
        sketch_line(cr, [(sx - 260 + 30 * k, yy), (sx + 260 - 30 * k, yy)], 4, sid=22400 + k, color=(1.0, 0.85, 0.5))
    cr.rectangle(x0, HORIZON + 160, x1 - x0, 110); cr.set_source_rgb(0.98, 0.88, 0.66); cr.fill()
    # the sidewalk + road
    cr.rectangle(x0, HORIZON + 270, x1 - x0, FLOOR_Y - HORIZON - 270 + 1); cr.set_source_rgb(0.86, 0.82, 0.86); cr.fill()
    cr.rectangle(x0, FLOOR_Y, x1 - x0, 900); cr.set_source_rgb(0.24, 0.22, 0.30); cr.fill()
    for k in range(-12, 12):
        cr.rectangle(NX + 360 * k, FLOOR_Y + 160, 180, 18); cr.set_source_rgb(1.0, 0.85, 0.3); cr.fill()
    cr.rectangle(x0, FLOOR_Y - 6, x1 - x0, 14); cr.set_source_rgb(0.98, 0.45, 0.70); cr.fill()
    sketch_line(cr, [(x0, FLOOR_Y), (x1, FLOOR_Y)], 6, sid=22410, amp=0.3)
    # background palms + the art-deco hotel
    for k, px in enumerate((NX - 900, NX - 380, NX + 1150, NX + 1600, NX - 1800)):
        O.draw_palm(cr, px, t, h=560, s=0.7, yb=HORIZON + 270, sid=22420 + 7 * k)
    hx0, hx1, hy = NX - 2100, NX - 1250, HORIZON - 420
    sk_rect(cr, hx0, hy, hx1, HORIZON + 270, 6, sid=22440, fill=(0.98, 0.78, 0.85))
    sk_rect(cr, (hx0 + hx1) / 2 - 90, hy - 160, (hx0 + hx1) / 2 + 90, hy, 6, sid=22441, fill=(0.98, 0.78, 0.85))
    for r_ in range(4):
        for c_ in range(5):
            sk_rect(cr, hx0 + 50 + 160 * c_, hy + 60 + 150 * r_, hx0 + 140 + 160 * c_, hy + 140 + 150 * r_, 4, sid=22450 + r_ * 5 + c_,
                    fill=(0.35, 0.80, 0.85))
    draw_text(cr, "OCEAN VIEW", (hx0 + hx1) / 2, hy - 80, 50, color=(60, 230, 230))
    # the store he came out of (left edge of the new world - its facade hides the border)
    sk_rect(cr, DOOR_X - 2400, FLOOR_Y - 1500, DOOR_X - 200, FLOOR_Y, 7, sid=22460, fill=(0.28, 0.20, 0.40))
    sk_rect(cr, DOOR_X - 520, FLOOR_Y - 640, DOOR_X - 220, FLOOR_Y, 6, sid=22461, fill=(0.55, 0.30, 0.85))
    draw_text(cr, "GAME CAVE", DOOR_X - 900, FLOOR_Y - 1050, 90, color=(255, 120, 220))
    # the hero palm (bends when he leans on it, stays bent)
    bend = 0.0 if t < T_BEND0 else 0.5 * smooth(ramp(t, T_BEND0, T_BEND1))
    O.draw_palm(cr, PALM_X, t, h=900, bend=bend, sid=22480)
    # the boombox on the ground
    if T_SETDOWN + 0.3 <= t < T_GRAB:
        play = 1.0 if t >= T_PLAY else 0.0
        O.draw_boombox(cr, BOOM_X, FLOOR_Y - 70, s=0.55, t=t, play=play)
        if play:
            for k in range(3):
                u = ((t - T_PLAY) * 0.6 + k / 3) % 1.0
                O.draw_note(cr, BOOM_X - 60 + 70 * k + 30 * math.sin(t * 3 + k), FLOOR_Y - 180 - 260 * u, s=0.6, alpha=1 - u, double=k % 2 == 1)

def draw_car_big(cr, t):
    cx = car_x(t)
    if t >= T_DRIVE0:
        for k in range(5):
            u = ((t - T_DRIVE0) * 1.5 + k * 0.2)
            if u < 1.5: O.draw_smoke_puff(cr, CAR_X - 150 + 120 * k, FLOOR_Y - 60 - 40 * u, 60 + 60 * u, alpha=max(0.0, 0.8 - 0.5 * u))
    O.draw_car(cr, cx, FLOOR_Y - 10, s=1.7, col=(0.98, 0.42, 0.66), sid=22500)

def world(cr, t):
    if t < CUT1 - FR:
        store(cr, t); return
    neon(cr, t)
    draw_car_big(cr, t) if t < T_INCAR else None
S.background(world)

# ================================================================ props (layers)
def props_back(cr, t, p, ly):
    if ly != "back" or t < CUT1 - FR: return
    draw_her(cr, t) if t < T_DRIVE1 else None
    if t >= T_INCAR: draw_car_big(cr, t)
    draw_wife(cr, t)
S.prop(props_back)
def props_front(cr, t, p, ly):
    if ly != "front": return
    if t < CUT1 - FR:
        if t >= T_BLAST:
            O.draw_magic_burst(cr, p["rhand"][0], p["rhand"][1] - 60, t - T_BLAST, t=t, r=1500)
        return
    draw_bills(cr, t); draw_last_bill(cr, t)
    if T_PHONE <= t < T_DECLINE + 0.25:                                  # the phone pops up next to him
        s = max(0.05, min(1.0, (t - T_PHONE) / 0.2))
        px, py = p["neck"][0] - 260, p["neck"][1] + 90
        cr.save(); cr.translate(px, py); cr.scale(s, s)
        sk_rect(cr, -95, -170, 95, 170, 7, sid=22600, fill=(0.12, 0.12, 0.16))
        cr.rectangle(-80, -150, 160, 300); cr.set_source_rgb(0.25, 0.55, 0.85); cr.fill()
        draw_text(cr, "COUSIN", 0, -110, 40, color=(255, 255, 255))
        sk_circ(cr, -45, 115, 26, 4, sid=22601, fill=(0.95, 0.25, 0.25)); sk_circ(cr, 45, 115, 26, 4, sid=22602, fill=(0.3, 0.85, 0.4))
        cr.restore()
        if t >= T_PHONE + 0.4:
            O.draw_bubble(cr, px - 10, py - 310, 330, 150, (px + 10, py - 175), text="LET'S GO BOWLING!", t=t)
S.prop(props_front)

# ================================================================ HUD (screen space, top-left, clear of the card)
def hud(cr, t):
    if t < T_HUD[0] or t >= T_ASK: return
    a1 = ramp(t, T_HUD[0], T_HUD[0] + 0.15)
    # minimap
    cx, cy, r = 150, 480, 80
    cr.save(); cr.arc(cx, cy, r, 0, 2 * math.pi); cr.set_source_rgba(0.15, 0.20, 0.25, 0.8 * a1); cr.fill_preserve()
    cr.set_source_rgba(1, 1, 1, a1); cr.set_line_width(6); cr.stroke()
    cr.arc(cx, cy, r - 3, 0, 2 * math.pi); cr.clip()
    for k in range(-3, 4):
        cr.rectangle(cx - r, cy + 40 * k - 5, 2 * r, 10); cr.set_source_rgba(0.6, 0.6, 0.65, a1); cr.fill()
    cr.rectangle(cx + 20, cy - r, 12, 2 * r); cr.set_source_rgba(0.6, 0.6, 0.65, a1); cr.fill()
    cr.move_to(cx, cy - 16); cr.line_to(cx + 12, cy + 12); cr.line_to(cx - 12, cy + 12); cr.close_path()
    cr.set_source_rgba(1, 1, 1, a1); cr.fill()
    if H_ON(t):
        cr.arc(cx + 55, cy - 20, 9, 0, 2 * math.pi); cr.set_source_rgba(0.98, 0.42, 0.66, a1); cr.fill()
    cr.restore()
    if t >= T_HUD[1]:
        a2 = ramp(t, T_HUD[1], T_HUD[1] + 0.15)
        draw_text(cr, "${:,}".format(money(t)), 70, 150, 38, color=(90, 220, 110), alpha=a2, anchor="left")
    if t >= T_HUD[2]:
        a3 = ramp(t, T_HUD[2], T_HUD[2] + 0.15); n = stars_lit(t)
        flash_on = n == 5 and int(t * 4) % 2 == 0
        for k in range(5):
            lit = k < n
            col = ((0.35, 0.55, 1.0) if flash_on else (1.0, 0.85, 0.2)) if lit else (1, 1, 1)
            O.draw_star(cr, 92 + 56 * k, 215, 24, color=col, alpha=a3 if lit else 0.5 * a3)
    if t >= T_METER:
        m = meter(t); a4 = ramp(t, T_METER, T_METER + 0.2)
        draw_text(cr, "DATE", 70, 285, 32, color=(255, 255, 255), alpha=a4, anchor="left")
        cr.rectangle(175, 270, 160, 30); cr.set_source_rgba(0.2, 0.2, 0.25, 0.8 * a4); cr.fill()
        cr.rectangle(175, 270, 160 * m / 100, 30); cr.set_source_rgba(0.98, 0.42, 0.66, a4); cr.fill()
        cr.rectangle(175, 270, 160, 30); cr.set_source_rgba(1, 1, 1, a4); cr.set_line_width(3); cr.stroke()
        draw_text(cr, f"{m}%", 255, 330, 28, color=(255, 255, 255), alpha=a4)
    if T_ACT <= t < T_ACT + 2.5:
        draw_text(cr, "CHEAT ACTIVATED", 70, 375, 30, color=(255, 255, 255), alpha=1 - ramp(t, T_ACT + 2.0, T_ACT + 2.5), anchor="left")
def H_ON(t): return T_SEEHER - 0.5 <= t < T_DRIVE1
def cheat_overlay(cr, t):
    if not (T_CHEAT0 <= t < T_ACT + 0.4): return
    n = min(len(CHEAT), int((t - T_CHEAT0) / 0.15) + 1)
    a = 1 - ramp(t, T_ACT, T_ACT + 0.4)
    line1 = " ".join(CHEAT[:min(n, 6)]); line2 = " ".join(CHEAT[6:n])
    cr.rectangle(60, 1280, 960, 170); cr.set_source_rgba(0, 0, 0, 0.55 * a); cr.fill()
    draw_text(cr, line1, 540, 1330, 46, color=(255, 255, 255), alpha=a)
    if line2: draw_text(cr, line2, 540, 1400, 46, color=(255, 255, 255), alpha=a)
def wasted(cr, t):
    if not (T_GREY0 <= t < T_COLOR + 0.3): return
    g = ramp(t, T_GREY0, T_GREY1) * (1 - ramp(t, T_COLOR, T_COLOR + 0.3))
    cr.save(); cr.set_operator(cairo.OPERATOR_HSL_SATURATION); cr.set_source_rgba(0.5, 0.5, 0.5, g); cr.paint(); cr.restore()
    cr.set_source_rgba(0, 0, 0, 0.25 * g); cr.paint()
    if t >= T_WASTED:
        u = ramp(t, T_WASTED, T_WASTED + 0.25)
        cr.rectangle(0, 700, 1080, 200); cr.set_source_rgba(0, 0, 0, 0.45 * g * u); cr.fill()
        draw_text(cr, "WASTED", 540, 800, 170 * (1.15 - 0.15 * u), color=(200, 30, 30), alpha=g * u)
S.overlay(wasted); S.overlay(hud); S.overlay(cheat_overlay)

# ================================================================ music: an original synthwave groove for the boombox
MUSIC = os.path.join(HERE, "groove.wav")
def make_groove(path, dur=20.0, sr=48000, bpm=104):
    n = int(dur * sr); tt = np.arange(n) / sr; out = np.zeros(n, np.float32)
    beat = 60 / bpm
    prog = [(45, 52, 57), (41, 48, 53), (43, 50, 55), (40, 47, 52)]          # Am F G Em (MIDI roots + fifths)
    def f(m): return 440.0 * 2 ** ((m - 69) / 12)
    for b in range(int(dur / beat)):
        t0 = b * beat; ch = prog[(b // 4) % 4]
        for e in range(2):                                                   # 8th-note bass
            s0 = int((t0 + e * beat / 2) * sr); ln = int(beat / 2 * sr * 0.9)
            if s0 + ln >= n: continue
            x = np.arange(ln) / sr; fr = f(ch[0] - 12)
            w = (2 * ((x * fr) % 1.0) - 1) * np.exp(-x * 6)
            out[s0:s0 + ln] += 0.30 * w
        s0 = int(t0 * sr); ln = int(beat * sr)                               # pad
        if s0 + ln < n:
            x = np.arange(ln) / sr
            pad = sum(np.sin(2 * np.pi * f(m + 12) * x + 0.3 * np.sin(2 * np.pi * 5 * x)) for m in ch) / 3
            out[s0:s0 + ln] += 0.12 * pad
            if b % 2 == 0:                                                   # kick
                k = np.sin(2 * np.pi * (50 + 80 * np.exp(-x * 30)) * x) * np.exp(-x * 9)
                out[s0:s0 + ln] += 0.5 * k
            else:                                                            # snare
                sn = np.random.RandomState(b).standard_normal(ln) * np.exp(-x * 14)
                out[s0:s0 + ln] += 0.22 * sn
    out /= np.abs(out).max() + 1e-9
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((out * 32000).astype(np.int16).tobytes())
make_groove(MUSIC, dur=T_GRAB - T_PLAY)
S.sfx(T_PLAY, MUSIC, 0.10)

def _cut_music():
    """trim the groove where she takes the boombox"""
    pass

if __name__ == "__main__":
    S.render("day022.mp4")
