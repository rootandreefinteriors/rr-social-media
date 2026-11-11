"""Day 20: @second_degree_burn "Take your wife out on a date" (Instagram, day 19 reel, 0 likes).
The Finals arena (flat under the trophy) -> he reads it, he's late, runs out right -> a night street outside LE FANCY:
she's waiting, arms crossed, the street clock says 9:47; a rose (she takes it this time) -> inside: a menu of insane
prices, a violinist who gets closer, then three; one pea each under giant silver domes; the receipt unrolls across the
floor; he pays with $1 -> thrown out the door, cannonball into a hot dog cart: KABOOM, hot dogs rain down -> she
walks out and laughs for real, sits with him on the curb, hot dogs, her head on his shoulder; the violinists follow
them out -> the ask on the curb. See BEATS.md.
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

# ================================================================ places
AX = 4000000.0                                      # the Finals arena (day 19)
DFX = AX + 150.0                                    # his feet (flat on his back)
FLAT = 1.42
TBASE = (DFX + 500 * math.sin(FLAT) - 10, FLOOR_Y - 500 * math.cos(FLAT) - 12)
PLAQUE = ("TELL ME WHAT", "TO DO NEXT IN", "THE COMMENTS")
RX = 5000000.0                                      # the street outside LE FANCY (restaurant middle)
DOORX = RX + 300.0
CLOCKX = RX - 1150.0
HIS_B, HER_B = RX - 640.0, RX - 170.0
DX = 6000000.0                                      # inside: the table
HIS_C, HER_C = DX - 330.0, DX + 330.0
PLATE_L, PLATE_R = DX - 150.0, DX + 150.0
TTOP = FLOOR_Y - 360.0
CART = RX + 1640.0
CURB_HIM, CURB_HER = RX + 1420.0, RX + 1110.0

# ================================================================ timeline
T_READ = 0.35; T_WIDE = 1.3; CUT_UP = 1.95; T_LOOKUS = 2.1; T_RUN = 2.45; CUT1 = 3.05
T_ARR = 3.85; T_LOOKCLK = 4.25; T_LOOKHER = 4.85; T_US = 5.3; T_DIG = 5.6; T_POP = T_DIG + 1.4
T_OFFER = 7.15; T_TAKE = 8.35; T_SMILE = 8.6; T_WALK0, T_WALK1 = 9.0, 9.7; CUT2 = 9.8
T_WIN0, T_WIN1 = 9.85, 10.45; T_MENU0, T_MENU1 = 10.55, 10.85
CUT_MENU = 11.4; CUT_MENU1 = 13.5
T_ORDER = 13.9; T_WNOD = 14.2; T_WOUT0, T_WOUT1 = 14.5, 15.1
T_V1IN0, T_V1IN1 = 14.95, 15.55; T_PLAY1 = 15.6; T_CLOSE0, T_CLOSE1 = 16.3, 17.1; T_US2 = 16.7
CUT3 = 18.0
T_DOM0, T_DOM1 = 19.8, 20.45; T_SETDOM = 20.6; T_LIFT = 21.2
CUT_PEA = 21.75; CUT_PEA1 = 22.85
T_PINCH = 23.1; T_EAT = 23.5; T_GULP = 23.85; T_US3 = 24.1
T_FOLDER = 24.5; T_OPEN = 25.0; T_ROLL0, T_ROLL1 = 25.2, 26.6
CUT_TOT = 26.9; CUT_TOT1 = 28.2
T_DIG2 = 28.3; T_POP2 = T_DIG2 + 1.4; T_LAY = 30.0; T_WLOOK = 30.25; T_TWITCH = 30.6; T_WPOINT = 31.0
CUT4 = 31.6
T_DOOR = 31.65; T_FLY0 = 31.7; T_HIT = 32.6; T_SMOKE1 = 33.6
T_BONK = 34.4
T_HER0 = 35.2; T_HW0, T_HW1 = 35.4, 36.2; T_LAUGH0, T_LAUGH1 = 36.4, 37.8; T_HW2, T_HW3 = 37.9, 38.6; T_HSIT = 38.75
T_HAND0, T_HAND1 = 39.2, 39.7; T_BITE = 40.1; T_LEAN = 40.7; T_HSMILE = 41.2
T_VOUT0, T_VOUT1 = 41.7, 42.8; T_PLAY2 = 42.9; T_TURN = 43.2; T_BACK = 43.9
T_GULP2 = 44.3; T_STAND = 44.6; T_ASK = 45.4; HOLD = 8.6

# ================================================================ poses
def P(name, **kw): L.POSES[name] = kw
P("lie_tro", lelb=(450, 960), lhand=(460, 860), relb=(630, 960), rhand=(620, 860), lhand_t="grip", rhand_t="grip")
P("offer_r", relb=(680, 900), rhand=(800, 880), rhand_t="grip")
P("c_sit", head=(540, 752), neck=(540, 878), hip=(540, 1228), lknee=(400, 1300), rknee=(680, 1300), lfoot=(430, FLOOR_Y),
  rfoot=(650, FLOOR_Y), lelb=(465, 1075), lhand=(462, 1200), relb=(615, 1075), rhand=(618, 1200), lfoot_dir=-0.5, rfoot_dir=0.5, nowalk=1.0)
C_SIT = L.POSES["c_sit"]
P("c_menu", **dict(C_SIT, lelb=(500, 1010), lhand=(560, 930), relb=(660, 1010), rhand=(700, 930), lhand_t="grip", rhand_t="grip"))
P("c_point", **dict(C_SIT, relb=(660, 1000), rhand=(770, 990), rhand_t="point"))
P("c_hands", **dict(C_SIT, lelb=(500, 1050), lhand=(560, 990), relb=(640, 1050), rhand=(690, 990), lhand_t="grip", rhand_t="grip"))
P("sit_curb", **dict(L.POSES["sit_floor"], nowalk=1.0))
# hers
P("g_cross", lelb=(470, 1000), lhand=(605, 935), relb=(610, 1000), rhand=(475, 935))
P("g_take", lelb=(440, 950), lhand=(360, 900), lhand_t="grip")
P("g_rose", lelb=(470, 1000), lhand=(500, 930), lhand_t="grip")
P("g_csit", **dict(C_SIT, lelb=(470, 1050), lhand=(500, 1130), lhand_t="mitt"))
P("g_sitc", **dict(L.POSES["sit_floor"], lelb=(470, 1240), lhand=(470, 1318), lhand_t="grip", nowalk=1.0))
P("g_sitc_eat", **dict(L.POSES["sit_floor"], relb=(600, 1180), rhand=(580, 1060), rhand_t="grip", lelb=(470, 1240), lhand=(470, 1318),
  lhand_t="grip", nowalk=1.0))
# waiter / violinists
P("w_tray", lelb=(450, 960), lhand=(380, 900), relb=(630, 960), rhand=(700, 900), lhand_t="open", rhand_t="open")
P("w_hand", lelb=(420, 920), lhand=(320, 900), lhand_t="grip")
P("w_point", lelb=(400, 860), lhand=(270, 820), lhand_t="point")
P("violin", lelb=(470, 900), lhand=(470, 830), relb=(650, 810), rhand=(760, 760), lhand_t="grip", rhand_t="grip", tilt=0.18)

# ================================================================ scene (him)
S = M.Scene(start_body="lie_tro", start_face="dead_stare", x0=DFX - 540)
S.auto_blinks = True
S.floor = False
S.card("second_degree_burn", "Take your wife out on a date", "0", t0=0.3)
CAM0 = (AX + 560, 1060, 0.86)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0

def dig_pull(t0, hold_pose, look=(0.4, -0.2), pock=(595, 1092), **kw):
    """digs his hand around at his hip (no pocket), POP -> the thing is in his hand (drawn by the caller from t0+1.4)."""
    S.set(t0, hold_pose if hold_pose.startswith("c_") else "stand", "deadpan", dur=0.35, look=(0.35, 0.9), tilt=0.05, **kw)
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

def S_x(t):
    """his body offset at t (from the x keys - only used for the dig position)."""
    return XT.at(t) if XT else 0.0
XT = None

# ---------------------------------------------------------------- A: the arena, under the trophy
S.keys[0] = (0.0, L.pose("lie_tro", "dead_stare", turn=0.0, look=(0.0, 0.0), lean=FLAT, nowalk=1.0), 0)
S.set(T_READ, "lie_tro", "deadpan", dur=0.25, turn=0.3, look=(0.8, -0.6), lean=FLAT, nowalk=1.0)
def read_hk(tt, p):
    if T_READ + 0.3 <= tt < T_WIDE - 0.05:
        k = (tt - T_READ - 0.3) / 0.45; u = k % 1.0
        p["look"] = (0.3 + 0.6 * smooth(u), -0.7 + 0.15 * int(k % 2))
    return p
S.hook(read_hk)
S.set(T_WIDE, "lie_tro", "dead_stare", dur=0.08, ease="snap", turn=0.0, look=(0.0, 0.0), lean=FLAT, nowalk=1.0, eyescale=1.4,
      pupil=0.55, curl_up=1.0)
S.sfx(T_WIDE, "boing", 0.05)
S.cut(CUT_UP - FR, cam=(AX + 420, 880, 0.86))
S.set(CUT_UP - FR, "stand", "dead_stare", dur=0.0, turn=0.0, look=(0.0, 0.0), eyescale=1.25, curl_up=0.6)
S.set(T_LOOKUS, "stand", "deadpan", dur=0.25, turn=0.0, look=(0.0, 0.0), sweat=0.5)
S.set(T_RUN, "stand", "deadpan", dur=0.15, run=1.0, look=(1.0, 0.0), turn=1.0, lean=0.1)
S.xkeys.append((T_RUN, DFX + 900 - 540, CUT1 - T_RUN, "inn")); S.x = DFX + 900 - 540
S.sfx(T_RUN, "whoosh", 0.05)

# ---------------------------------------------------------------- B: the street outside LE FANCY
CAM_B = (RX - 470, 720, 0.70)
S.cut(CUT1 - FR, cam=CAM_B, x=RX - 1900 - 540)
S.set(CUT1 - FR, "stand", "deadpan", dur=0.0, run=1.0, look=(1.0, 0.0), turn=1.0, lean=0.1)
S.xkeys.append((CUT1, HIS_B - 540, T_ARR - CUT1, "out")); S.x = HIS_B - 540
S.set(T_ARR - 0.1, "stand", "deadpan", dur=0.12, ease="snap", stretch=-0.25, run=0.0, turn=0.6, look=(0.9, 0.0))
S.set(T_ARR + 0.1, "stand", "deadpan", dur=0.25, ease="back", turn=0.6, look=(0.9, -0.1)); S.sfx(T_ARR - 0.1, "skid", 0.05, dur=0.3)
S.set(T_LOOKCLK, "stand", "deadpan", dur=0.3, turn=-0.7, look=(-1.0, -0.9), tilt=-0.05)
S.set(T_LOOKHER, "stand", "dead_stare", dur=0.25, turn=0.7, look=(1.0, -0.2), sweat=0.4)
S.set(T_US, "stand", "deadpan", dur=0.25, turn=0.0, look=(0.0, 0.0), sweat=0.4)
dig_pull(T_DIG, "offer_r", look=(0.9, -0.1), turn=0.6)
S.set(T_OFFER, "offer_r", "deadpan", dur=0.35, turn=0.7, look=(1.0, -0.2), rhand=(810, 870))
S.set(T_TAKE + 0.15, "stand", "deadpan", dur=0.35, turn=0.7, look=(1.0, -0.2))
S.set(T_SMILE + 0.25, "stand", "happy", dur=0.4, turn=0.7, look=(1.0, -0.2), smile=0.35)
S.set(T_WALK0 - 0.1, "stand", "happy", dur=0.2, turn=0.9, look=(1.0, 0.0), smile=0.3)
S.walk_to(T_WALK0, DOORX - 300 - 540, T_WALK1 - T_WALK0)

# ---------------------------------------------------------------- C: inside, the table
CAM_C = (DX - 60, 843, 0.85)
S.cut(CUT2 - FR, cam=CAM_C, x=HIS_C - 540)
S.set(CUT2 - FR, "c_sit", "happy", dur=0.0, turn=0.7, look=(1.0, -0.1), smile=0.3)
S.set(T_WIN1 - 0.2, "c_sit", "deadpan", dur=0.3, turn=0.6, look=(0.8, -0.6))
S.set(T_MENU0 + 0.1, "c_hands", "deadpan", dur=0.3, turn=0.6, look=(0.8, -0.3))
S.set(T_MENU1 + 0.2, "c_menu", "deadpan", dur=0.3, turn=0.4, look=(0.5, 0.4))
S.sfx(T_MENU1, "flip", 0.05)
# the menu insert (overlay) - he is reading it
S.set(CUT_MENU1 - FR, "c_menu", "dead_stare", dur=0.0, turn=0.4, look=(0.5, 0.4), sweat=0.8, eyescale=1.15, quiver=0.4)
S.set(CUT_MENU1 + 0.25, "c_menu", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), sweat=0.8, eyescale=1.15, quiver=0.4)
S.set(T_ORDER, "c_point", "deadpan", dur=0.25, turn=0.6, look=(0.9, -0.5), sweat=0.6)
S.sfx(T_ORDER + 0.1, "tap", 0.04)
S.set(T_ORDER + 0.7, "c_sit", "deadpan", dur=0.35, turn=0.6, look=(0.9, 0.0), sweat=0.4)
# the violinist
S.set(T_PLAY1 + 0.3, "c_sit", "deadpan", dur=0.3, turn=-0.5, look=(-0.9, -0.3), sweat=0.3)
S.set(T_US2, "c_sit", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), sweat=0.3)
def bow_hk(tt, p):
    """the bow brushes his head on every stroke once the violinist is close (a little head bob + the curl flicks)."""
    if False:
        k = max(0.0, math.sin(tt * 2 * math.pi / 0.9)) ** 6
        for j in ("head",):
            p[j] = (p[j][0] + 6 * k, p[j][1] + 4 * k)
        p["tilt"] = p.get("tilt", 0.0) + 0.05 * k
    return p
S.hook(bow_hk)
S.set(CUT3 - FR, "c_sit", "dead_stare", dur=0.0, turn=0.0, look=(0.0, 0.0), quiver=0.5, lid=0.15)
S.set(CUT3 + 1.2, "c_sit", "dead_stare", dur=0.4, turn=0.0, look=(0.0, 0.0), quiver=0.5, lid=0.3, twitch=0.5)
# the domes
S.set(T_DOM1, "c_sit", "deadpan", dur=0.3, turn=0.5, look=(0.7, 0.5))
S.sfx(T_SETDOM, "clack", 0.05); S.sfx(T_SETDOM + 0.08, "clack", 0.04)
S.sfx(T_LIFT + 0.1, "ding", 0.07)
S.set(T_LIFT + 0.4, "c_sit", "deadpan", dur=0.25, turn=0.5, look=(0.7, 0.8), eyescale=1.1)
S.cut(CUT_PEA - FR, cam=(PLATE_L, TTOP - 60, 2.7))
S.cut(CUT_PEA1 - FR, cam=CAM_C)
S.set(CUT_PEA1 - FR, "c_sit", "deadpan", dur=0.0, turn=0.5, look=(0.7, 0.8))
S.set(T_PINCH - 0.2, "c_sit", "deadpan", dur=0.25, turn=0.5, look=(0.7, 0.8), relb=(660, 1050), rhand=(PLATE_L - HIS_C + 540 + 10, TTOP - 30),
      rhand_t="grip")
S.set(T_EAT, "c_sit", "deadpan", dur=0.25, turn=0.3, look=(0.3, 0.3), relb=(650, 980), rhand=(585, 815), rhand_t="grip")
S.set(T_GULP, "c_sit", "deadpan", dur=0.25, turn=0.3, look=(0.3, 0.3), mouth="flat")
S.sfx(T_GULP, "gulp", 0.08)
S.set(T_US3, "c_sit", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0))
# the bill
S.sfx(T_FOLDER, "pat", 0.05)
S.set(T_OPEN - 0.25, "c_hands", "deadpan", dur=0.3, turn=0.5, look=(0.7, 0.6))
S.sfx(T_OPEN + 0.1, "flip", 0.05)
S.sfx(T_ROLL0, "slide_down", 0.03, dur=1.3)
S.set(T_ROLL0 + 0.3, "c_hands", "dead_stare", dur=0.4, turn=0.0, look=(-0.6, 0.9), eyescale=1.1)
S.set(T_ROLL1 - 0.3, "c_hands", "dead_stare", dur=0.4, turn=0.0, look=(0.0, 0.5), eyescale=1.25, sweat=0.7, quiver=0.6)
for k in range(5): S.sfx(25.5 + k * 0.55, "thud", 0.05 + 0.01 * k)
S.set(CUT_TOT1 - FR, "c_hands", "dead_stare", dur=0.0, turn=0.0, look=(0.0, 0.0), eyescale=1.3, sweat=1.0, quiver=0.8, pupil=0.6)
dig_pull(T_DIG2, "c_hands", look=(0.6, 0.6), pock=(600, 1180), turn=0.4)
S.set(T_LAY, "c_hands", "deadpan", dur=0.3, turn=0.5, look=(0.7, 0.7), relb=(650, 1060), rhand=(720, TTOP - 10), rhand_t="open")
S.sfx(T_LAY + 0.2, "pat", 0.03)
S.set(T_WLOOK + 0.3, "c_sit", "deadpan", dur=0.3, turn=0.6, look=(0.9, -0.6))
S.set(T_WPOINT + 0.3, "c_sit", "dead_stare", dur=0.25, turn=0.6, look=(0.9, -0.6))

# ---------------------------------------------------------------- D: thrown out -> the hot dog cart
CAM_D = (RX + 1060, 640, 0.62)
S.cut(CUT4 - FR, cam=CAM_D, x=DOORX - 540)
S.set(CUT4 - FR, "cannonball", "dead_stare", dur=0.0, turn=0.0, look=(0.0, 0.0), show=0.0, nowalk=1.0)
S.set(T_FLY0, "cannonball", "dead_stare", dur=0.0, turn=0.0, look=(0.0, 0.0), show=1.0, nowalk=1.0)
S.sfx(T_DOOR, "clack", 0.08); S.sfx(T_FLY0, "whoosh", 0.07)
def fly_hk(tt, p):
    if T_FLY0 <= tt < T_HIT:
        u = ramp(tt, T_FLY0, T_HIT, "linear")
        c0 = ((p["lfoot"][0] + p["rfoot"][0]) / 2, 1080.0)
        cx = lerp(DOORX, CART - 60, u); cy = lerp(1040, 960, u) - 520 * math.sin(math.pi * u)
        a = 2 * math.pi * 1.5 * u
        ca, sa = math.cos(a), math.sin(a)
        for j in C.JOINTS:
            dx, dy = p[j][0] - c0[0], p[j][1] - c0[1]
            p[j] = (cx + dx * ca - dy * sa, cy + dx * sa + dy * ca)
        p["tilt"] = p.get("tilt", 0.0) + a
    return p
S.hook(fly_hk)
S.set(T_HIT, "cannonball", "dead_stare", dur=0.0, show=0.0, nowalk=1.0)
S.cut(T_HIT + 0.3, x=CURB_HIM - 540)
S.set(T_HIT + 0.3, "sit_curb", "dead_stare", dur=0.0, turn=0.0, look=(0.0, 0.0), show=1.0, nowalk=1.0)
S.sfx(T_HIT, "kaboom", 0.45, dur=2.2); S.shake(T_HIT, 0.6, 22); S.flash(T_HIT, 0.25, (1.0, 0.9, 0.6))
S.set(T_BONK + 0.05, "sit_curb", "dead_stare", dur=0.08, ease="snap", turn=0.0, look=(0.0, 0.0), stretch=-0.12, nowalk=1.0)
S.set(T_BONK + 0.3, "sit_curb", "deadpan", dur=0.3, turn=0.0, look=(0.0, 0.0), nowalk=1.0)
S.sfx(T_BONK, "bonk", 0.06)
S.set(T_HER0 + 0.2, "sit_curb", "deadpan", dur=0.35, turn=-0.7, look=(-1.0, -0.1), nowalk=1.0)
S.set(T_LAUGH0 + 0.4, "sit_curb", "deadpan", dur=0.3, turn=-0.6, look=(-1.0, -0.1), eyescale=1.1, nowalk=1.0)
S.set(T_LAUGH1 - 0.4, "sit_curb", "happy", dur=0.5, turn=-0.5, look=(-1.0, -0.1), smile=0.2, nowalk=1.0)
S.set(T_HAND0, "sit_curb", "happy", dur=0.35, turn=-0.6, look=(-1.0, 0.1), smile=0.3, lelb=(420, 1180), lhand=(330, 1160),
      lhand_t="grip", nowalk=1.0)
S.set(T_HAND1 + 0.1, "sit_curb", "happy", dur=0.35, turn=-0.5, look=(-0.9, 0.0), smile=0.3, nowalk=1.0)
S.set(T_LEAN + 0.25, "sit_curb", "happy", dur=0.5, turn=-0.5, look=(-0.8, 0.4), smile=0.3, nowalk=1.0)
S.set(T_HSMILE, "sit_curb", "happy", dur=0.6, turn=-0.3, look=(-0.6, 0.5), smile=0.75, lid=0.15, nowalk=1.0)
S.set(T_TURN, "sit_curb", "deadpan", dur=0.35, turn=-0.9, look=(-1.0, -0.4), nowalk=1.0)
S.set(T_BACK, "sit_curb", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), nowalk=1.0)
S.sfx(T_GULP2, "gulp", 0.07)
S.set(T_STAND, "crouch", "deadpan", dur=0.3, nowalk=1.0)
S.set(T_STAND + 0.35, "stand", "deadpan", dur=0.3, ease="back")
S.camera(T_HAND0, RX + 1250, 760, 0.76, 1.2)
S.camera(T_VOUT0, RX + 1000, 680, 0.64, 1.0)
S.camera(T_STAND, RX + 1200, 780, 0.76, 0.8)
S.x = CURB_HIM - 540
S.the_ask(T_ASK, hold=HOLD)
T_END = S.t
S.blink(2.6, 6.2, 9.2, 12.0, 19.0, 22.6, 27.5, 33.9, 36.0, 39.9, 42.4)
XT = Track(S.xkeys)

# ================================================================ other people (keyed on his rig)
class Actor:
    def __init__(self, x0, body="stand", face="neutral", **kw):
        self.K = [(0.0, L.pose(body, face, **kw), 0)]
        self.X = [(0.0, x0, 0)]; self.W = [(0.0, 0.0, 0)]
        self.blinks = []; self._t = None
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
        la = p.get("laugh", 0.0)
        if la > 0.01:
            b = la * 10 * abs(math.sin(t * 13))
            for k in ("head", "neck", "lelb", "relb", "lhand", "rhand"): p[k] = (p[k][0], p[k][1] - b)
            p["tilt"] = p.get("tilt", 0.0) + la * (-0.1 + 0.06 * math.sin(t * 13))
        ln = p.get("lean", 0.0)
        if abs(ln) > 1e-4:
            fx_ = (p["lfoot"][0] + p["rfoot"][0]) / 2; c, s_ = math.cos(ln), math.sin(ln)
            for k in L.JOINTS:
                if k in ("lfoot", "rfoot"): continue
                dx, dy = p[k][0] - fx_, p[k][1] - FLOOR_Y
                p[k] = (fx_ + dx * c - dy * s_, FLOOR_Y + dx * s_ + dy * c)
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

# ---------------------------------------------------------------- HER
G_HAIR, G_DRESS = (0.62, 0.28, 0.16), (0.30, 0.66, 0.66)
GS = 0.92
G = Actor(HER_B, "g_cross", "annoyed", turn=-0.6, look=(-0.9, 0.0), lid=0.45)
G.blinks = [4.4, 7.9, 12.6, 16.0, 19.4, 24.3, 37.0, 41.0, 44.5, 49.0, 53.0, 57.5]
G.k(T_ARR + 0.2, "g_cross", "annoyed", dur=0.3, turn=-0.7, look=(-1.0, 0.1), lid=0.5)
G.k(T_LOOKCLK + 0.1, "g_cross", "annoyed", dur=0.3, turn=-0.7, look=(-1.0, -0.6), lid=0.5)            # points him at the clock with her eyes
G.k(T_LOOKHER, "g_cross", "annoyed", dur=0.3, turn=-0.7, look=(-1.0, 0.1), lid=0.55)
G.k(T_POP + 0.2, "g_cross", "neutral", dur=0.3, turn=-0.7, look=(-1.0, 0.3), lid=0.3)
G.k(T_OFFER + 0.6, "g_cross", "neutral", dur=0.4, turn=-0.7, look=(-1.0, 0.2), lid=0.2)
G.k(T_TAKE - 0.2, "g_take", "neutral", dur=0.3, turn=-0.7, look=(-1.0, 0.2))
G.k(T_TAKE + 0.2, "g_rose", "happy", dur=0.35, turn=-0.5, look=(-0.4, 0.0), smile=0.5, eyes="closed")
G.k(T_SMILE + 0.3, "g_rose", "happy", dur=0.3, turn=-0.7, look=(-1.0, 0.0), smile=0.7)
G.k(T_WALK0 - 0.1, "g_rose", "happy", dur=0.2, turn=0.7, look=(1.0, 0.0), smile=0.6)
G.walk(T_WALK0 + 0.05, T_WALK1, DOORX - 20)
# inside
G.at(CUT2 - FR, HER_C)
G.k(CUT2 - FR, "g_csit", "happy", dur=0.0, turn=-0.7, look=(-1.0, 0.0), smile=0.6)
G.k(CUT_MENU1, "g_csit", "happy", dur=0.3, turn=-0.4, look=(-0.4, 0.6), smile=0.6)
G.k(T_PLAY1 + 0.2, "g_csit", "delighted", dur=0.4, turn=-0.6, look=(-1.0, -0.4), smile=0.9, blush=0.0)
G.k(CUT3 - FR, "g_csit", "happy", dur=0.0, turn=-0.5, look=(-0.8, -0.3), smile=0.9, eyes="closed", tilt=0.1)
G.k(T_DOM1, "g_csit", "happy", dur=0.3, turn=-0.3, look=(0.0, 0.5), smile=0.6)
G.k(T_LIFT + 0.4, "g_csit", "surprised", dur=0.25, turn=-0.3, look=(-0.2, 0.8), open=0.2)
G.k(CUT_PEA1, "g_csit", "neutral", dur=0.3, turn=-0.6, look=(-1.0, 0.0), smile=0.3)
G.k(T_ROLL0 + 0.2, "g_csit", "surprised", dur=0.3, turn=-0.5, look=(-0.8, 0.8), open=0.2)
G.k(CUT_TOT1, "g_csit", "neutral", dur=0.3, turn=-0.7, look=(-1.0, 0.0), smile=0.2)
G.k(T_WPOINT + 0.2, "g_csit", "surprised", dur=0.2, turn=-0.4, look=(0.6, -0.5), open=0.3)
# outside
G.at(CUT4 - FR, DOORX)
G.k(CUT4 - FR, "g_rose", "neutral", dur=0.0, turn=0.7, look=(1.0, 0.0))
G.walk(T_HW0, T_HW1, RX + 760)
G.k(T_HW1 - 0.1, "g_rose", "surprised", dur=0.25, turn=0.7, look=(1.0, 0.3), open=0.2)
G.k(T_LAUGH0, "g_rose", "laughing", dur=0.25, turn=0.4, look=(0.6, 0.2), laugh=1.0, tears=0.0)
G.k(T_LAUGH1 - 0.3, "g_rose", "happy", dur=0.4, turn=0.7, look=(1.0, 0.3), smile=0.9)
G.walk(T_HW2, T_HW3, CURB_HER)
G.k(T_HW3 - 0.05, "crouch", "happy", dur=0.2, turn=0.6, look=(1.0, 0.2), smile=0.8, nowalk=1.0)
G.k(T_HSIT, "g_sitc", "happy", dur=0.25, ease="back", turn=0.6, look=(1.0, 0.0), smile=0.8, nowalk=1.0)
G.k(T_HAND1 - 0.15, "g_sitc_eat", "happy", dur=0.3, turn=0.6, look=(1.0, 0.2), smile=0.8, rhand=(700, 1170), relb=(640, 1200), nowalk=1.0)
G.k(T_BITE - 0.2, "g_sitc_eat", "happy", dur=0.3, turn=0.4, look=(0.5, 0.2), smile=0.6, nowalk=1.0)
G.k(T_BITE + 0.4, "g_sitc_eat", "happy", dur=0.3, turn=0.5, look=(0.8, -0.2), smile=0.8, rhand=(610, 1150), nowalk=1.0)
G.k(T_LEAN, "g_sitc", "happy", dur=0.6, turn=0.5, look=(0.6, 0.0), smile=0.8, eyes="closed", lean=0.22, tilt=0.32, nowalk=1.0)
G.k(T_VOUT1, "g_sitc", "happy", dur=0.4, turn=0.3, look=(-0.6, -0.4), smile=0.9, lean=0.22, tilt=0.32, nowalk=1.0)
G.k(T_ASK, "g_sitc", "happy", dur=0.5, turn=0.5, look=(0.8, -0.6), smile=0.8, lean=0.08, tilt=0.12, nowalk=1.0)
G.done()

def her_tapping(t, p):
    """her foot taps while she waits (arms crossed), until she's handed the rose."""
    if t < T_OFFER and t < CUT2:
        k = max(0.0, math.sin(t * 2 * math.pi * 2.2))
        p["lfoot"] = (p["lfoot"][0], p["lfoot"][1] - 22 * k)
    return p

def draw_her(cr, t, rose=True):
    q = her_tapping(t, G.pose(t))
    O.draw_mom(cr, t, q, G.blink(t), s=GS, hair=G_HAIR, dress=G_DRESS, bun=False)
    fx = foot_c(q)
    if rose and ((T_TAKE <= t < CUT2) or t >= CUT4):
        rx, ry = scale_pt(q, q["lhand"], GS)
        O.draw_rose(cr, rx, ry - 10, s=0.55, ang=-0.25)
        cr.save(); cr.translate(fx, FLOOR_Y); cr.scale(GS, GS); cr.translate(-fx, -FLOOR_Y); L.draw_grips(cr, q); cr.restore()
    return q

# ---------------------------------------------------------------- the waiter
WT = Actor(DX + 1100, "stand", "neutral", turn=-0.6, look=(-0.9, 0.0), lid=0.4)
WT.blinks = [12.2, 19.0, 22.5, 26.0, 29.4]
WT.walk(T_WIN0, T_WIN1, DX + 210)
WT.k(T_WIN1, "w_hand", "neutral", dur=0.3, turn=-0.7, look=(-1.0, 0.2), lid=0.4, smile=0.0)
WT.k(T_MENU1 + 0.1, "stand", "neutral", dur=0.3, turn=-0.7, look=(-1.0, 0.2), lid=0.4, smile=0.0)
WT.k(T_WNOD, "bow", "neutral", dur=0.2, turn=-0.7, look=(-1.0, 0.4), lid=0.5, smile=0.0)
WT.k(T_WNOD + 0.25, "stand", "neutral", dur=0.2, turn=0.7, look=(1.0, 0.0), lid=0.4, smile=0.0)
WT.walk(T_WOUT0, T_WOUT1, DX + 1100)
WT.walk(T_DOM0, T_DOM1, DX + 210)
WT.k(T_DOM0 - 0.1, "w_tray", "neutral", dur=0.2, turn=-0.6, look=(-0.9, 0.0), lid=0.4, smile=0.1)
WT.k(T_SETDOM - 0.1, "w_tray", "neutral", dur=0.25, turn=-0.6, look=(-0.6, 0.6), lid=0.4, smile=0.1, lhand=(390, 1060), rhand=(690, 1060))
WT.k(T_LIFT - 0.2, "w_tray", "smug", dur=0.2, turn=-0.4, look=(-0.4, 0.6), lid=0.4, lhand=(380, 1010), rhand=(700, 1010))
WT.k(T_LIFT + 0.05, "w_tray", "smug", dur=0.25, ease="back", turn=-0.4, look=(-0.6, 0.0), lid=0.4, lhand=(330, 760), rhand=(750, 760))
WT.k(T_LIFT + 0.75, "w_tray", "smug", dur=0.3, turn=0.7, look=(1.0, 0.0), lid=0.4, lhand=(380, 940), rhand=(700, 940))
WT.walk(T_LIFT + 0.95, T_LIFT + 1.6, DX + 1150)
WT.k(T_FOLDER - 0.8, "stand", "smug", dur=0.01, turn=-0.7, look=(-1.0, 0.0), lid=0.45, lelb=(450, 960), lhand=(400, 1000), lhand_t="grip")
WT.walk(T_FOLDER - 0.75, T_FOLDER - 0.3, DX + 210)
WT.k(T_FOLDER - 0.3, "w_hand", "neutral", dur=0.25, turn=-0.7, look=(-1.0, 0.4), lid=0.45, lhand=(330, 1020))
WT.k(T_FOLDER + 0.2, "stand", "smug", dur=0.3, turn=-0.7, look=(-1.0, 0.2), lid=0.45)
WT.k(T_WLOOK, "stand", "neutral", dur=0.3, turn=-0.6, look=(-0.8, 0.9), lid=0.2, smile=0.0, eyescale=1.15)
WT.k(T_TWITCH, "stand", "neutral", dur=0.15, turn=-0.6, look=(-0.8, 0.9), lid=0.2, smile=-0.2, eyescale=1.15, twitch=1.0)
WT.k(T_WPOINT, "w_point", "angry", dur=0.2, ease="back", turn=-0.6, look=(-1.0, -0.2), twitch=1.0)
WT.done()

def draw_waiter(cr, t):
    q = WT.pose(t)
    O.draw_staff(cr, t, q, WT.blink(t), s=1.0, kind="plain", vest=(0.12, 0.12, 0.14))
    hx, hy = q["head"]; tn = q.get("turn", 0.0)
    sketch_line(cr, [(hx + 34 * tn - 46, hy + 58), (hx + 34 * tn - 10, hy + 46), (hx + 34 * tn + 10, hy + 46), (hx + 34 * tn + 46, hy + 58)],
                6, sid=24201, amp=0.2)                                          # thin moustache
    nx, ny = q["neck"]
    O.sketch_poly(cr, [(nx, ny + 22), (nx - 30, ny + 6), (nx - 30, ny + 40)], 3, sid=24202, fill=(0.75, 0.1, 0.15))
    O.sketch_poly(cr, [(nx, ny + 22), (nx + 30, ny + 6), (nx + 30, ny + 40)], 3, sid=24203, fill=(0.75, 0.1, 0.15))
    ex, ey = q["relb"]                                                          # the towel over his arm
    O.sketch_rect(cr, ex - 20, ey - 10, ex + 24, ey + 110, 3, sid=24204, fill=(1, 1, 1))
    return q

# ---------------------------------------------------------------- the violinists
def make_v(x0, xs):
    v = Actor(x0, "violin", "concentrating", turn=0.7, look=(0.6, 0.3), lid=0.5, eyes="closed")
    for (t, x, kind) in xs:
        if kind == "at": v.at(t, x)
        else: v.walk(t, t + kind, x)
    return v
V1 = make_v(DX - 1300, [(T_V1IN0, DX - 690, T_V1IN1 - T_V1IN0), (T_CLOSE0, DX - 620, T_CLOSE1 - T_CLOSE0),
                        (CUT4 - FR, DOORX, "at"), (T_VOUT0, RX + 380, 0.9)])
V1.k(T_CLOSE0, "violin", "concentrating", dur=0.8, turn=0.7, look=(0.6, 0.3), lid=0.5, eyes="closed", lean=0.14)
V1.k(CUT4 - FR, "violin", "concentrating", dur=0.0, turn=0.7, look=(0.6, 0.3), eyes="closed", lean=0.0)
V1.done()
V2 = make_v(DX - 900, [(CUT4 - FR, DOORX, "at"), (T_VOUT0 + 0.3, RX + 600, 0.9)])
V2.k(0, "violin", "concentrating", dur=0, turn=0.7, look=(0.6, 0.3), eyes="closed", lean=0.1); V2.done()
V3 = make_v(DX - 40, [(CUT4 - FR, DOORX, "at"), (T_VOUT0 + 0.6, RX + 820, 0.9)])
V3.k(0, "violin", "concentrating", dur=0, turn=-0.4, look=(-0.6, 0.3), eyes="closed", tilt=-0.1)
V3.k(CUT4 - FR, "violin", "concentrating", dur=0, turn=0.7, look=(0.6, 0.3), eyes="closed"); V3.done()

def v_on(v, t):
    if CUT2 - FR <= t < CUT4 - FR:
        if v is V1: return t >= T_V1IN0
        return CUT3 - FR <= t
    if t >= CUT4 - FR: return t >= T_VOUT0 + (0.3 if v is V2 else 0.6 if v is V3 else 0.0) - 0.05
    return False
def v_playing(v, t):
    if CUT2 - FR <= t < CUT4 - FR: return t >= (T_PLAY1 if v is V1 else CUT3 - FR)
    return t >= T_PLAY2
def v_pose(v, t):
    q = v.pose(t)
    if v_playing(v, t):                                                         # the bow saws back and forth
        ph = t * 2 * math.pi / 0.9 + (0.0 if v is V1 else 1.3 if v is V2 else 2.6)
        q["lhand"] = (q["lhand"][0] - 70 * math.sin(ph), q["lhand"][1] + 10 * math.cos(ph))
        q["head"] = (q["head"][0] + 6 * math.sin(ph * 0.5), q["head"][1])
    return L.constrain(q)
def chin(q): return (q["neck"][0] + 30 * (1 if q.get("turn", 0) > 0 else -1), q["neck"][1] + 10)
def draw_violinist(cr, t, v, part="body"):
    q = v_pose(v, t)
    flip = q.get("turn", 0) < 0
    if part == "body":
        O.draw_staff(cr, t, q, 0.0, s=1.0, kind="plain", vest=(0.10, 0.10, 0.12))
        nx, ny = q["neck"]
        O.sketch_poly(cr, [(nx, ny + 22), (nx - 26, ny + 8), (nx - 26, ny + 36)], 3, sid=24210, fill=(0.1, 0.1, 0.1))
        O.sketch_poly(cr, [(nx, ny + 22), (nx + 26, ny + 8), (nx + 26, ny + 36)], 3, sid=24211, fill=(0.1, 0.1, 0.1))
        neck_hand = q["rhand"]
        if flip:
            neck_hand = (2 * q["neck"][0] - q["rhand"][0], q["rhand"][1])
        O.draw_violin(cr, chin(q), neck_hand, s=0.9)
        L.draw_grips(cr, q)
    else:                                                                       # the bow (drawn over everything near it)
        a = q["lhand"]; d = -1 if flip else 1
        b = (a[0] + d * 330, a[1] - 70)
        O.draw_bow(cr, a, b)
        cr.save(); L.draw_grips(cr, dict(q, rhand_t="none", rhand=(-9999, -9999))) if False else None; cr.restore()
    return q

# ================================================================ hot dogs
_rng = random.Random(20)
DOGS = []
for k in range(34):
    a = _rng.uniform(-1.25, 1.25); sp = _rng.uniform(1300, 2400)
    DOGS.append(dict(vx=sp * math.sin(a) * 0.75, vy=-sp * math.cos(a), spin=_rng.uniform(-9, 9), rest_x=None))
G_ACC = 2600.0
BOOM = (CART, FLOOR_Y - 600)
def dog_state(d, t):
    u = t - T_HIT
    if u < 0: return None
    x = BOOM[0] + d["vx"] * u; y = BOOM[1] + d["vy"] * u + 0.5 * G_ACC * u * u
    ang = d["spin"] * u
    rest = FLOOR_Y + 60 - 10 * (abs(d["vx"]) % 7)
    if y > rest:                                                                # landed: stays where it fell
        # time of landing
        A_, B_, C_ = 0.5 * G_ACC, d["vy"], BOOM[1] - rest
        ul = (-B_ + math.sqrt(max(0.0, B_ * B_ - 4 * A_ * C_))) / (2 * A_)
        x = BOOM[0] + d["vx"] * ul; y = rest; ang = round(d["spin"] * ul / math.pi) * math.pi + 0.1 * (d["vx"] % 3)
    return x, y, ang

# ================================================================ backgrounds
def in_insert(t): return (CUT_MENU <= t + FR < CUT_MENU1) or (CUT_TOT <= t + FR < CUT_TOT1)
def world(cr, t):
    if t < CUT1 - FR:
        O.draw_arena(cr, t, AX - 6000, AX + 6000, roar=0.1, banner_x=AX - 330, flashes=0.6)
        return
    if t < CUT2 - FR or t >= CUT4 - FR:
        O.draw_city_night(cr, t, RX - 6000, RX + 6000)
        O.draw_lamp(cr, RX - 1700); O.draw_lamp(cr, RX + 2300, sid=18132)
        O.draw_restaurant(cr, RX, FLOOR_Y, t, door=door(t))
        O.draw_street_clock(cr, CLOCKX, FLOOR_Y, hour=9.0, minute=47.0)
        return
    O.draw_dining_room(cr, t, DX - 6000, DX + 6000)
    O.draw_chandelier(cr, DX, 330, t)
S.background(world)

def door(t):
    if t < CUT2 - FR:
        return smooth(ramp(t, T_WALK0 + 0.3, T_WALK0 + 0.6))
    o = smooth(ramp(t, T_DOOR - 0.05, T_DOOR + 0.05)) * (1 - smooth(ramp(t, T_FLY0 + 0.8, T_FLY0 + 1.2)))
    o = max(o, smooth(ramp(t, T_HER0 - 0.1, T_HER0 + 0.2)) * (1 - smooth(ramp(t, T_HW0 + 0.5, T_HW0 + 0.9))))
    o = max(o, smooth(ramp(t, T_VOUT0 - 0.2, T_VOUT0 + 0.1)) * (1 - smooth(ramp(t, T_VOUT1 - 0.2, T_VOUT1 + 0.2))))
    return o

# ================================================================ props
def receipt_pts(t):
    """from his hands down to the floor and along it to the right, under the table, off screen."""
    q = L.pose_with_follow(t)
    hx = (q["lhand"][0] + q["rhand"][0]) / 2; hy = (q["lhand"][1] + q["rhand"][1]) / 2
    grow = smooth(ramp(t, T_ROLL0, T_ROLL1))
    fx0 = hx + 40
    run = 4200 * grow
    pts = [(hx, hy), (hx + 30, hy + 80), (fx0 + 10, FLOOR_Y - 60), (fx0 + 60, FLOOR_Y + 40)]
    n = 30
    for i in range(1, n + 1):
        xx = fx0 + 60 + run * i / n
        pts.append((xx, FLOOR_Y + 40 + 6 * math.sin(i * 1.7 + t * 2)))
    return pts

def props_back(cr, t, p, ly):
    if ly != "back": return
    if t < CUT1 - FR:                                                           # the trophy
        if t < CUT_UP - FR:
            cr.save(); cr.translate(*TBASE); O.draw_trophy(cr, 0, 0, s=0.55, plaque=PLAQUE); cr.restore()
        else:
            cr.save(); cr.translate(DFX + 330, FLOOR_Y - 150); cr.rotate(math.pi / 2)
            O.draw_trophy(cr, 0, 0, s=0.55, plaque=PLAQUE); cr.restore()
        return
    if t < CUT2 - FR:                                                           # the street: her
        draw_her(cr, t)
        return
    if t < CUT4 - FR:                                                           # inside
        for v in (V2, V1):
            if v_on(v, t):
                draw_violinist(cr, t, v, "body")
                if v_playing(v, t): draw_violinist(cr, t, v, "bow")
        O.draw_chair(cr, HIS_C, FLOOR_Y, back_side=-1, sid=24080)
        O.draw_chair(cr, HER_C, FLOOR_Y, back_side=1, sid=24085)
        if T_WIN0 <= t < T_WOUT1 or T_DOM0 <= t:
            wq = draw_waiter(cr, t)
            if T_DOM0 <= t < T_SETDOM or T_LIFT + 0.3 <= t < T_LIFT + 1.7:          # the domes, in his hands
                up = T_LIFT <= t
                for k, h in enumerate((wq["lhand"], wq["rhand"])):
                    if up:
                        O.draw_cloche(cr, h[0], h[1] + 140, s=0.55, lift=0.0, food=None, sid=24150 + 10 * k, plate=False)
                    else:
                        O.draw_cloche(cr, h[0], h[1] - 4, s=0.55, lift=0.0, food=None, sid=24120 + 10 * k)
                L.draw_grips(cr, wq)
            if T_FOLDER - 0.8 <= t < T_FOLDER - 0.1:
                O.draw_bill_folder(cr, wq["lhand"][0], wq["lhand"][1] + 10, s=0.7)
        if v_on(V3, t):
            draw_violinist(cr, t, V3, "body")
            if v_playing(V3, t): draw_violinist(cr, t, V3, "bow")
        draw_her(cr, t, rose=False)
        O.draw_table(cr, DX, FLOOR_Y, t, part="front")
        O.draw_table(cr, DX, FLOOR_Y, t, part="top")
        O.draw_rose(cr, HER_C - 120, TTOP - 8, s=0.5, ang=-1.45)                # her rose, lying on the table
        if T_SETDOM <= t:                                                       # the plates / domes
            lift = smooth(ramp(t, T_LIFT, T_LIFT + 0.35))
            for k, px in enumerate((PLATE_L, PLATE_R)):
                eaten = k == 0 and t >= T_PINCH
                O.draw_cloche(cr, px, TTOP - 10, s=0.55, lift=min(0.95, ramp(t, T_LIFT, T_LIFT + 0.3)) if t < T_LIFT + 0.3 else 1.0, food=None if eaten else "pea", sid=24120 + 10 * k)
                if 0.0 < lift < 1.0: pass
        if T_FOLDER - 0.1 <= t:                                                 # the bill folder
            fy = TTOP - 10
            O.draw_bill_folder(cr, PLATE_L - 40, fy, s=0.7, open_=smooth(ramp(t, T_OPEN, T_OPEN + 0.2)))
        if t >= T_LAY + 0.2:                                                    # the $1 on the table
            O.draw_dollar(cr, PLATE_L + 40, TTOP - 8, s=0.6, ang=0.05)
        return
    # outside again
    O.draw_hotdog_cart(cr, CART, FLOOR_Y, t, wreck=1.0 if t >= T_HIT else 0.0)
    if t >= T_HIT:
        for k in range(3):                                                      # a little smoke keeps rising from the wreck
            u = ((t - T_HIT) * 0.5 + k / 3) % 1.0
            O.draw_smoke_puff(cr, CART - 80 + 60 * k + 40 * u, FLOOR_Y - 600 - 500 * u, 60 + 70 * u, alpha=0.35 * (1 - u), dark=0.5)
    for v in (V1, V2, V3):
        if v_on(v, t):
            draw_violinist(cr, t, v, "body")
            if v_playing(v, t): draw_violinist(cr, t, v, "bow")
    if t >= CUT4 - FR and (T_HER0 <= t):
        draw_her(cr, t)
S.prop(props_back)

def props_front(cr, t, p, ly):
    if ly != "front": return
    hx, hy = p["rhand"]
    if CUT1 - FR <= t < CUT2 - FR:                                              # the rose
        if T_POP <= t < T_TAKE:
            O.draw_rose(cr, hx, hy - 10, s=0.55, ang=0.25); L.draw_grips(cr, p)
        return
    if CUT2 - FR <= t < CUT4 - FR:
        if T_MENU0 <= t < T_WNOD + 0.3:                                         # the menu
            if t < T_MENU1:
                q = WT.pose(t); a = q["lhand"]
                u = smooth(ramp(t, T_MENU0, T_MENU1))
                b = ((p["lhand"][0] + p["rhand"][0]) / 2, (p["lhand"][1] + p["rhand"][1]) / 2 - 60)
                O.draw_menu(cr, lerp(a[0], b[0], u), lerp(a[1], b[1], u), s=0.7)
            elif t < T_ORDER + 0.3:
                mx = (p["lhand"][0] + p["rhand"][0]) / 2; my = (p["lhand"][1] + p["rhand"][1]) / 2
                O.draw_menu(cr, mx, my - 60, s=0.7); L.draw_grips(cr, p)
            else:                                                               # the waiter takes it away
                q = WT.pose(t); u = smooth(ramp(t, T_ORDER + 0.3, T_WNOD))
                O.draw_menu(cr, lerp(HIS_C + 150, q["lhand"][0], u), lerp(1000, q["lhand"][1], u), s=0.6, ang=0.2)
        if T_PINCH <= t < T_GULP:                                               # the pea, to his mouth
            sk = O.sketch_circle; sk(cr, hx, hy - 8, 10, 3, sid=24125, fill=(0.40, 0.72, 0.30))
        if T_OPEN <= t:                                                         # the receipt
            O.draw_receipt(cr, receipt_pts(t), w=90)
            if T_DIG2 + 0.2 > t: L.draw_grips(cr, p)
        if T_POP2 <= t < T_LAY + 0.2:
            O.draw_dollar(cr, hx, hy - 20, s=0.6, ang=-0.2); L.draw_grips(cr, p)
        return
    if t >= CUT4 - FR:
        if T_HIT <= t < T_SMOKE1 + 0.6:                                          # the boom cloud
            u = (t - T_HIT) / (T_SMOKE1 + 0.6 - T_HIT)
            O.draw_boom(cr, CART, FLOOR_Y - 520, 520 * (0.6 + 0.6 * u), t, alpha=max(0.0, 1 - u * 3))
            for k, (dx, dy) in enumerate(((-260, -100), (200, -180), (0, -420), (-120, 60), (300, 80), (-380, -320))):
                O.draw_smoke_puff(cr, CART + dx * (1 + u), FLOOR_Y - 500 + dy * (1 + u) - 120 * u, 230 + 140 * u, alpha=1 - smooth(ramp(u, 0.55, 1.0)), dark=0.25)
        for d in DOGS:                                                          # the hot dogs
            s_ = dog_state(d, t)
            if s_: O.draw_hotdog(cr, s_[0], s_[1], s=0.75, ang=s_[2])
        if T_BONK - 0.5 <= t < T_BONK + 0.9:                                     # the one that bonks him
            hd = p["head"]
            if t < T_BONK:
                u = ramp(t, T_BONK - 0.5, T_BONK, "linear"); y = lerp(hd[1] - 1300, hd[1] - 120, u * u)
                O.draw_hotdog(cr, hd[0] + 10, y, s=0.75, ang=0.3 + 6 * u)
            else:
                u = ramp(t, T_BONK, T_BONK + 0.9, "linear")
                O.draw_hotdog(cr, hd[0] + 10 + 260 * u, hd[1] - 120 - 300 * math.sin(math.pi * min(1, u * 1.2)) + 500 * u * u,
                              s=0.75, ang=0.3 + 8 * u)
        if T_BONK + 0.9 <= t:
            O.draw_hotdog(cr, CURB_HIM + 270, FLOOR_Y + 50, s=0.75, ang=0.1)
        if T_SMOKE1 - 0.4 <= t < T_GULP2:                                         # his hot dog, in his mouth
            hd = p["head"]; tn = p.get("turn", 0.0)
            O.draw_hotdog(cr, hd[0] + 40 * tn + 10, hd[1] + 62, s=0.62, ang=0.12)
        if T_HAND0 <= t:                                                        # the one he hands her
            q = G.pose(t)
            if t < T_HAND1:
                a = p["lhand"]; O.draw_hotdog(cr, a[0], a[1] - 15, s=0.62, ang=-0.2); L.draw_grips(cr, p)
            elif t < T_LEAN:
                rx, ry = scale_pt(q, q["rhand"], GS)
                O.draw_hotdog(cr, rx, ry - 12, s=0.62, ang=-0.4, bite=0.45 if t >= T_BITE else 0.0)
S.prop(props_front)

# ================================================================ inserts (under the comment card)
def inserts(cr, t):
    if CUT_MENU <= t + FR < CUT_MENU1:
        cr.set_source_rgb(0.30, 0.10, 0.12); cr.paint()
        O.draw_menu_page(cr, 540, 1060 + 6 * math.sin(t * 2), s=1.05, t=t)
    if CUT_TOT <= t + FR < CUT_TOT1:
        cr.set_source_rgb(0.30, 0.10, 0.12); cr.paint()
        jit = 3 * math.sin(t * 37)
        O.sketch_rect(cr, 170 + jit, 420, 910 + jit, 2000, 8, sid=24300, fill=(1, 1, 0.97))
        rows = (("WATER x2", "$80"), ("BREAD", "$55"), ("AIR (FRENCH)", "$95"), ("PEA x2", "$620"), ("VIOLIN x3", "$2,400"),
                ("CANDLE", "$65"), ("TIP (30%)", "$1,002"))
        for i, (a, b) in enumerate(rows):
            yy = 560 + i * 110
            draw_text(cr, a, 220 + jit, yy, 52, anchor="left", color=(60, 60, 70))
            draw_text(cr, b, 790 + jit, yy, 52, color=(60, 60, 70))
        sketch_line(cr, [(220, 1370), (860, 1370)], 5, sid=24301, amp=0.3)
        draw_text(cr, "TOTAL", 540 + jit, 1480, 90)
        k = smooth(ramp(t, CUT_TOT + 0.35, CUT_TOT + 0.55))
        draw_text(cr, "$4,817.00", 540 + jit, 1640, 140 * (0.7 + 0.3 * k), color=(190, 20, 30), alpha=k)
S.overlays.insert(0, inserts)
S.sfx(CUT_TOT + 0.4, "thud", 0.09)

# ================================================================ the violins (a soft bowed melody; gain kept low)
def sfx_violin(dur=4.0, notes=(69, 72, 76, 74, 72, 71, 69, 64), step=0.5, voices=1):
    SR = L.SR; n = int(dur * SR); tt = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    for vi in range(voices):
        tr = (0, -5, 7)[vi]
        for i in range(int(dur / step) + 1):
            m = notes[i % len(notes)] + tr
            f = 440 * 2 ** ((m - 69) / 12)
            t0 = i * step + 0.03 * vi
            seg = (tt >= t0) & (tt < t0 + step * 1.05)
            u = tt[seg] - t0
            vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * u) * np.clip(u / 0.15, 0, 1)
            ph = 2 * np.pi * f * np.cumsum(vib) / SR
            sig = sum(np.sin(ph * h) / h ** 1.3 for h in range(1, 7))
            env = np.clip(u / 0.08, 0, 1) * np.clip((step * 1.05 - u) / 0.1, 0, 1)
            out[seg] += (sig * env * 0.18).astype(np.float32)
    return out
L.SYNTH["violin"] = sfx_violin
S.sfx(T_PLAY1, "violin", 0.05, dur=CUT3 - T_PLAY1)
S.sfx(CUT3, "violin", 0.06, dur=CUT4 - CUT3, voices=3, step=0.25)
S.sfx(T_PLAY2, "violin", 0.035, dur=T_END - T_PLAY2 + 0.5, voices=3, step=0.6, notes=(69, 72, 76, 81, 79, 76, 72, 74))
S.sfx(T_HER0, "squeak", 0.03); S.sfx(T_VOUT0, "squeak", 0.03)
S.sfx(T_LAUGH0, "boop", 0.0)
S.sfx(T_HSIT + 0.1, "pat", 0.03); S.sfx(T_LEAN + 0.4, "twinkle", 0.03)
S.sfx(T_WPOINT, "tap", 0.05)
S.sfx(T_TAKE, "twinkle", 0.04)

if __name__ == "__main__":
    print(f"end {T_END:.2f}", file=sys.stderr)
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        S.build()
        import cairo
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, L.W, L.H)
        for a in sys.argv[2:]:
            tt = float(a); L.render_frame(tt, surf); surf.write_to_png(f"still_{tt:05.2f}.png")
    else:
        S.render("day020.mp4")
