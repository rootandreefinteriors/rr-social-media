"""Day 14 - COMMENT episode: @thatboypiwko "Go to the racetrack" (TikTok, day 13 video, 0 likes).
Deadpan. The kitten rides on his head (in a tiny racing helmet), calm and bored, never harmed - it is the hero. See BEATS.md.

THEATER aisle -> runs out the EXIT door -> the megaplex's back door opens onto a racetrack PIT LANE (cars roar past; the
crew chief's board: YOU.) -> a tiny helmet for the kitten -> the GRID: five red lights... lights out, he stalls -> the
kitten presses DO NOT PRESS -> the race (passes everyone) -> PIT STOP (2.1 s, squeegee) -> WHITE FLAG -> stuck behind
#1 -> the kitten presses it again -> MEGA BOOST -> CHECKERED FLAG -> skids into VICTORY LANE -> trophy, the winner's milk
-> the kitten curls up in the trophy -> ASK.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import ramp, pulse, lerp, FLOOR_Y, Track
from ink import smooth, back_out, sketch_rect, sketch_line, sketch_circle, sketch_ellipse, sketch_poly, draw_text
import numpy as np

FR = 1 / 30
def trap(t, a, b, c): return smooth(ramp(t, a, b)) * (1 - smooth(ramp(t, b, c)))
KS = 0.62

# ================================================================ places
FX = 120000.0; ASKX = 121250.0; EXITX = ASKX + 760.0          # the theater (day 13's ending) + its EXIT door
RX = 200000.0                                                  # pit lane
WALLX = RX - 400.0                                             # the megaplex back wall ends here; door at WALLX - 260
CHX = RX + 380.0                                               # crew chief (pit lane)
CARX = RX + 1250.0                                             # car #0, parked
GX = 300000.0                                                  # the race (his car stays here; the world scrolls)
FLAGX = 400000.0                                               # the flag stand
VX = 500000.0                                                  # victory lane
TROPHY_X = VX - 450.0
YB_FAR = 1290.0                                                # the far lane

# ================================================================ timeline
T_READ = 0.3
T_TURN = 1.6; T_RUN = 1.8; T_DOOR = 2.4
CUT_PIT = 2.6; T_STOP = 3.5
FAR_PASS = (2.9, 3.9, 4.5)
T_LOOKCARS = 3.7; T_US = 4.9
T_BOARD = 5.6; T_LOOKB = 5.95; T_GLANCE = 6.6; T_POINTCAR = 7.0
T_UPCAT = 7.9; T_DIG = 8.2; T_POP = 8.8; T_HELMON = 9.3
T_CHIEF = 9.9; T_NOD = 10.3
CUT_GRID = 10.9
LIGHTS = (11.4, 11.95, 12.5, 13.05, 13.6)
T_OUT = 14.6
CUT_CLOSE1 = 15.2; T_KLOOK1 = 15.9; T_UPK1 = 16.2; T_PRESS1 = 16.5
CUT_GO = 16.7
PASSES = (17.5, 18.2, 18.8, 19.3, 19.7, 20.0, 20.25)
T_P2 = 20.55
T_PITIN = 21.0; T_PIT = 22.0; T_PITGO = 24.0
CUT_FLAG1 = 25.0; T_L1 = 25.45; T_HIM1 = 25.7
CUT_CHASE = 26.4
CUT_CLOSE2 = 29.0; T_UPK2 = 29.4; T_KBUT = 29.8; T_KBACK = 30.1; T_HNOD = 30.5; T_PRESS2 = 30.9
CUT_BOOST = 31.05
CUT_FLAG2 = 31.9; T_HIM2 = 32.05; T_SPIN = 32.15; T_L2 = 32.8
CUT_BRAKE = 33.3; T_STOPPED = 34.9
CUT_VIC = 36.2; T_TROPHY_DOWN = 37.4; T_LOOKUP_T = 37.6
T_MILK_GIVE = 38.3; T_MILK_TAKE = 38.6; T_DRINK = 38.9; T_DRINK1 = 40.7; T_MILK_DOWN = 40.9
T_HOP = 41.7; T_LAND = 42.3; T_SLEEP = 42.9
T_LOOKT = 42.5; T_LOOKUS = 43.3
T_ASK = 44.2
ASK_HOLD = 10.0


def scene(t):
    """which set we are on."""
    if t < CUT_PIT - FR: return "theater"
    if t < CUT_GRID - FR: return "pit"
    if t < CUT_FLAG1 - FR: return "race"
    if t < CUT_CHASE - FR: return "flag"
    if t < CUT_FLAG2 - FR: return "race"
    if t < CUT_BRAKE - FR: return "flag"
    if t < CUT_VIC - FR: return "race"
    return "victory"

def in_car(t): return CUT_GRID - FR <= t < CUT_VIC - FR

# ---------------------------------------------------------------- the treadmill (his speed along the track)
def speed(t):
    if t < CUT_GO: return 0.0
    if t < T_PITIN: return lerp(0.0, 5200.0, smooth(ramp(t, CUT_GO, CUT_GO + 0.5))) + 1400 * ramp(t, 17.2, T_PITIN)
    if t < T_PIT: return 6600.0 * (1 - ramp(t, T_PITIN, T_PIT)) ** 1.6
    if t < T_PITGO: return 0.0
    if t < CUT_BOOST: return 6000.0 * smooth(ramp(t, T_PITGO, T_PITGO + 0.6))
    if t < CUT_BRAKE: return 15000.0
    return 9000.0 * (1 - ramp(t, CUT_BRAKE, T_STOPPED)) ** 1.5
_TT = np.arange(0, 80, 1 / 240)
_POS = np.concatenate([[0.0], np.cumsum([speed(x) / 240 for x in _TT[:-1]])])
def P(t): return float(np.interp(t, _TT, _POS))
P_PIT = P(T_PIT); P_STOP = P(T_STOPPED)

def jit(t):
    """car bounce at speed."""
    v = speed(t)
    if not in_car(t) or scene(t) != "race": return 0.0
    return min(1.0, v / 4000) * 4 * math.sin(t * 53) + (3 * math.sin(t * 71) if T_OUT <= t < CUT_GO else 0)

def car_ang(t):
    """wheelie at the launches, nose dip under braking."""
    a = -0.07 * trap(t, CUT_GO - 0.05, CUT_GO + 0.1, CUT_GO + 0.7) if t >= CUT_GO - 0.05 else 0.0
    a += -0.09 * trap(t, CUT_BOOST - 0.05, CUT_BOOST + 0.05, CUT_BOOST + 0.6) if t >= CUT_BOOST - 0.05 else 0.0
    if CUT_BRAKE <= t: a += 0.035 * trap(t, CUT_BRAKE, CUT_BRAKE + 0.2, T_STOPPED + 0.3)
    return a

S = M.Scene(x0=ASKX - 540)
S.auto_blinks = False
S.floor = False
S.card("thatboypiwko", "Go to the racetrack", "0", t0=0.3)
CAM0 = (ASKX + 120, 930, 1.1)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0

# ================================================================ helpers
def npc_pose(x, face="deadpan", body="stand", **kw):
    p = L.pose(body, face, **kw)
    ox = x - 540
    for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1])
    p["breath_ph"] = 0.0
    return L.constrain(p)

def shift(p, dx, dy):
    for j in L.JOINTS: p[j] = (p[j][0] + dx, p[j][1] + dy)
    return p

# ================================================================ THEATER (day 13's ending)
def theater(cr, t):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    cr.rectangle(vx0, vy0, vx1 - vx0, vy1 - vy0); cr.set_source_rgb(0.42, 0.30, 0.33); cr.fill()
    for k in range(-2, 7):
        O.draw_seat_front(cr, FX - 900 + k * 300 + 150, 380, s=0.62, sid=14600 + k, part="all")
    cr.rectangle(vx0, 640, vx1 - vx0, 40); cr.set_source_rgb(0.36, 0.24, 0.27); cr.fill()
    for k in range(-3, 4):
        O.draw_seat_front(cr, FX + k * 300, 740, s=1.0, sid=14620 + k, part="all")
    cr.rectangle(vx0, FLOOR_Y, vx1 - vx0, vy1 - FLOOR_Y); cr.set_source_rgb(0.22, 0.10, 0.12); cr.fill()
    for k in range(5):
        cr.arc(ASKX - 300 + k * 300, FLOOR_Y + 40, 9, 0, 2 * math.pi); cr.set_source_rgb(*O.CINE_GOLD); cr.fill()
    # the EXIT door (right wall)
    dx0, dx1, dy0 = EXITX - 160, EXITX + 260, FLOOR_Y - 860
    op = smooth(ramp(t, T_DOOR - 0.05, T_DOOR + 0.12))
    sketch_rect(cr, dx0 - 30, dy0 - 30, dx1 + 30, FLOOR_Y, 7, sid=17500, fill=(0.30, 0.20, 0.22))
    sketch_rect(cr, dx0, dy0, dx1, FLOOR_Y, 6, sid=17501, fill=(1.0, 1.0, 0.96) if op > 0 else (0.55, 0.56, 0.6))
    if op > 0:
        sketch_rect(cr, dx1 - 30 - 330 * (1 - op), dy0, dx1, FLOOR_Y, 6, sid=17502, fill=(0.55, 0.56, 0.6))
    else:
        sketch_rect(cr, dx0 + 290, dy0 + 430, dx0 + 360, dy0 + 470, 4, sid=17503, fill=(0.85, 0.85, 0.88))
    sketch_rect(cr, dx0 + 40, dy0 - 200, dx1 - 40, dy0 - 70, 6, sid=17504, fill=(0.20, 0.70, 0.35))
    draw_text(cr, "EXIT", (dx0 + dx1) / 2, dy0 - 135, 76, color=(255, 255, 255))

# ================================================================ PIT LANE
def far_car_x(t, t0, x_from, x_to, dur=0.45):
    if not (t0 - 0.05 <= t <= t0 + dur + 0.05): return None
    return lerp(x_from, x_to, (t - t0) / dur)

def chief_pose(t):
    kw = dict(turn=-0.5, look=(-0.8, 0.0))
    p = npc_pose(CHX, "deadpan", "stand", **kw)
    up = smooth(ramp(t, T_BOARD, T_BOARD + 0.3)) * (1 - smooth(ramp(t, T_POINTCAR - 0.2, T_POINTCAR + 0.1)))
    if up > 0:                                                 # the board, held high
        p["lhand"] = lerp(p["lhand"], (CHX - 70, 430), up); p["lelb"] = lerp(p["lelb"], (CHX - 160, 620), up); p["lhand_t"] = "grip"
    pt = smooth(ramp(t, T_POINTCAR, T_POINTCAR + 0.25)) * (1 - smooth(ramp(t, T_UPCAT, T_UPCAT + 0.3)))
    if pt > 0:                                                 # points at the car
        p["rhand"] = lerp(p["rhand"], (CHX + 270, 860), pt); p["relb"] = lerp(p["relb"], (CHX + 150, 880), pt); p["rhand_t"] = "point"
        p["turn"] = lerp(-0.5, 0.5, pt)
    if T_NOD <= t < T_NOD + 0.5:
        d = 30 * math.sin(math.pi * (t - T_NOD) / 0.5)
        p["head"] = (p["head"][0], p["head"][1] + d)
    if t >= T_UPCAT: p["look"] = (-0.75, -0.5)
    return L.constrain(p)

def pit_lane(cr, t):
    O.draw_raceway(cr, t, ox=0.0, x0=WALLX)
    for k, t0 in enumerate(FAR_PASS):                          # cars roaring past on the track
        x = far_car_x(t, t0, RX + 2200, RX - 1800)
        if x is not None:
            cols = ((0.25, 0.45, 0.85), (0.98, 0.80, 0.20), (0.40, 0.75, 0.40))
            O.draw_racecar(cr, x, YB_FAR, s=0.6, col=cols[k], num=str(k + 3), driver=True, spin=t * 40, sid=17600 + 40 * k)
            for j in range(3):
                sketch_line(cr, [(x + 520 * 0.6 + 40, YB_FAR - 120 - 70 * j), (x + 520 * 0.6 + 340, YB_FAR - 120 - 70 * j)], 5,
                            sid=17700 + j, color=(1, 1, 1), alpha=0.8)
    vx0, vy0, vx1, vy1 = O._visible(cr)                        # the pit wall
    cr.rectangle(WALLX, 1250, vx1 - WALLX, 90); cr.set_source_rgb(0.86, 0.86, 0.84); cr.fill()
    sketch_line(cr, [(WALLX, 1250), (vx1, 1250)], 5, sid=17710); sketch_line(cr, [(WALLX, 1340), (vx1, 1340)], 5, sid=17711)
    for k in range(int((WALLX) // 220), int(vx1 // 220) + 1):
        cr.rectangle(k * 220, 1254, 110, 82); cr.set_source_rgb(0.86, 0.22, 0.2); cr.fill()
    O.draw_back_door(cr, WALLX, FLOOR_Y, open_=1.0 - smooth(ramp(t, CUT_PIT + 0.3, CUT_PIT + 0.7)))
    O.draw_racecar(cr, CARX, FLOOR_Y, s=1.0, button=True, sid=17000)
    cp = chief_pose(t)
    O.draw_staff(cr, t, cp, 0.0, s=1.0, kind="crew")
    up = smooth(ramp(t, T_BOARD, T_BOARD + 0.3)) * (1 - smooth(ramp(t, T_POINTCAR - 0.2, T_POINTCAR + 0.1)))
    if up > 0.02:
        hx, hy = cp["lhand"]
        O.draw_pit_board(cr, hx, hy - 10 + 200 * (1 - up), "YOU.", s=1.0)
        L.draw_grips(cr, cp)

# ================================================================ RACE (treadmill), FLAG STAND, VICTORY LANE
OPP = ((0.25, 0.45, 0.85), (0.98, 0.80, 0.20), (0.40, 0.75, 0.40), (0.68, 0.52, 0.86), (0.97, 0.62, 0.72), (0.42, 0.80, 0.78), (0.9, 0.5, 0.2))
LEADER = (0.14, 0.14, 0.16)

def leader_rel(t):
    """#1's position relative to him (far lane) during the chase."""
    if t < CUT_CHASE: return None
    if t < CUT_BOOST:
        r = 1100.0
        r = lerp(r, 520.0, smooth(ramp(t, CUT_CHASE, 27.4)))
        r = lerp(r, 1000.0, smooth(ramp(t, 27.6, 28.2)))
        r = lerp(r, 620.0, smooth(ramp(t, 28.3, 28.9)))
        return r
    return lerp(620.0, -3200.0, ramp(t, CUT_BOOST, CUT_BOOST + 0.35))

def race_world(cr, t):
    ox = P(t)
    marks = (("pit", GX + P_PIT),)
    if t >= CUT_BRAKE - FR: marks = ()
    blur = min(1.0, max(0.0, (speed(t) - 3000) / 4000))
    O.draw_raceway(cr, t, ox=ox, marks=marks, hats=1.0 if t >= CUT_BOOST else 0.0, hat_t0=CUT_BOOST, blur=0.0)
    # far lane: the start grid, then the cars he passes
    if t < CUT_GO + 0.6:
        for k, (rel, col, num) in enumerate(((900, LEADER, "1"), (-900, OPP[0], "3"), (1900, OPP[1], "4"), (-1900, OPP[2], "5"))):
            go = 0.0 if t < T_OUT else 5000 * (t - T_OUT) ** 1.2
            x = GX + rel + go - ox
            O.draw_racecar(cr, x, YB_FAR, s=0.62, col=col, num=num, driver=True, spin=t * 30 * (t > T_OUT), sid=17600 + 40 * k)
    for k, tp in enumerate(PASSES):
        if tp - 0.4 <= t <= tp + 0.4:
            x = GX + lerp(1700, -1700, (t - tp + 0.4) / 0.8)
            O.draw_racecar(cr, x, YB_FAR, s=0.62, col=OPP[k % len(OPP)], num=str(k + 2 if k < 6 else 9), driver=True, spin=t * 30,
                           sid=17600 + 40 * (k % 5))
    # P2 board (the chief behind the pit wall)
    if T_P2 - 0.6 <= t <= T_P2 + 0.6:
        x = GX + lerp(1500, -1300, (t - T_P2 + 0.6) / 1.2)
        cp = npc_pose(x, "deadpan", turn=0.3, look=(0.0, 0.0))
        cp["lhand"] = (x - 120, 640); cp["lelb"] = (x - 150, 820); cp["lhand_t"] = "grip"
        cp = L.constrain(cp)
        cr.save(); cr.translate(x, YB_FAR); cr.scale(0.62, 0.62); cr.translate(-x, -FLOOR_Y)
        O.draw_staff(cr, t, cp, 0.0, s=1.0, kind="crew")
        O.draw_pit_board(cr, cp["lhand"][0], cp["lhand"][1] - 10, "P2", s=1.2)
        L.draw_grips(cr, cp)
        cr.restore()
    # #1, during the chase
    r = leader_rel(t)
    if r is not None and t < CUT_BRAKE:
        x = GX + r
        look = 0.0
        if 27.4 <= t < 28.0: look = -2.6 * trap(t, 27.4, 27.55, 28.0)
        if CUT_BOOST <= t: look = (t - CUT_BOOST) * 30
        O.draw_racecar(cr, x, YB_FAR, s=0.62, col=LEADER, num="1", driver=True, spin=t * 40, look=look, sid=17880)
        if t < CUT_BOOST:
            for j in range(4):                                    # the draft: air wrapping around #1 back to him
                yy = YB_FAR - 150 - 60 * j
                sketch_line(cr, [(x - 420, yy), (x - 700 - 40 * j, yy + 30 * math.sin(t * 9 + j))], 5, sid=17890 + j, color=(1, 1, 1), alpha=0.7)
    # the crew in the pit box (stay with the box)
    if T_PITIN <= t < CUT_FLAG1:
        crew_layer(cr, t, ox)
    # victory lane arrives as he brakes
    if t >= CUT_BRAKE - FR:
        ax = GX + P_STOP + 150 - ox
        O.draw_victory_arch(cr, ax, FLOOR_Y, w=1300)

CREW_X = (-520, 560)                                            # rear + front wheel men, relative to the pit box
SQ_X = -330                                                     # the squeegee man
def crew_layer(cr, t, ox):
    base = GX + P_PIT - ox
    if t < T_PIT - 0.05: return
    for k, dx in enumerate(CREW_X):
        cp = npc_pose(base + dx, "deadpan", "crouch", turn=0.4 if dx < 0 else -0.4, look=(0.6 if dx < 0 else -0.6, 0.6))
        O.draw_staff(cr, t, cp, 0.0, s=1.0, kind="crew")
    # chief with the time board
    cx_ = base + 1050
    cp = npc_pose(cx_, "deadpan", turn=-0.4, look=(-0.8, 0.0))
    if t >= T_PIT + 1.2:
        cp["lhand"] = (cx_ - 120, 720); cp["lelb"] = (cx_ - 150, 880); cp["lhand_t"] = "grip"; cp = L.constrain(cp)
    O.draw_staff(cr, t, cp, 0.0, s=1.0, kind="crew")
    if t >= T_PIT + 1.2:
        O.draw_pit_board(cr, cp["lhand"][0], cp["lhand"][1] - 10, "2.1 s", s=1.0)
    # the squeegee man (behind him, reaching over)
    sx = base + SQ_X - 140
    cp = npc_pose(sx, "deadpan", turn=0.5, look=(0.8, -0.2))
    O.draw_staff(cr, t, cp, 0.0, s=1.0, kind="crew")

def squeegee_pos(t):
    """the squeegee blade sweeps across his face twice (T_PIT + 0.4 .. + 1.2)."""
    a, b = T_PIT + 0.4, T_PIT + 1.2
    if not (a <= t < b): return None
    u = (t - a) / (b - a)
    k = u * 2 % 1.0
    return lerp(-170, 170, smooth(k))

FLAG_CAM = (FLAGX + 100, 560, 0.62)
FLAGMAN_X = FLAGX - 350
def flagman_pose(t):
    p = npc_pose(FLAGMAN_X, "deadpan", turn=0.3, look=(0.6, 0.3))
    if t < CUT_FLAG2 - FR or t < T_SPIN:
        p["rhand"] = (FLAGMAN_X + 110, 520 + 25 * math.sin(t * 11)); p["relb"] = (FLAGMAN_X + 150, 700); p["rhand_t"] = "grip"
    else:                                                     # spun like a top by the wind
        u = t - T_SPIN
        p["turn"] = 1.5 * math.sin(u * 30) * max(0.0, 1 - u / 0.9)
        p["tilt"] = 0.1 * math.sin(u * 20) * max(0.0, 1 - u / 0.9)
        p["lhand"] = (FLAGMAN_X - 200, 820); p["rhand"] = (FLAGMAN_X + 200, 820); p["lhand_t"] = p["rhand_t"] = "open"
        p["face"] = "dead_stare"
    p = L.constrain(p)
    return shift(p, 0, 700 - FLOOR_Y)

def flag_world(cr, t):
    O.draw_raceway(cr, t, ox=7000.0, marks=(("finish", FLAGX + 7000.0 + 300),))
    # the stand
    sx = FLAGMAN_X
    for d in (-1, 1): sketch_rect(cr, sx + d * 230 - 18, 700, sx + d * 230 + 18, 1130, 5, sid=17910 + (d > 0), fill=(0.9, 0.9, 0.92))
    sketch_rect(cr, sx - 280, 700, sx + 280, 740, 6, sid=17912, fill=(0.95, 0.95, 0.95))
    fp = flagman_pose(t)
    O.draw_staff(cr, t, fp, 0.0, s=1.0, kind="flag", vest=(0.95, 0.95, 0.95))
    white = t < CUT_CHASE
    if white or t < T_SPIN:
        hx, hy = fp["rhand"]
        O.draw_flag(cr, hx, hy - 140, "white" if white else "checker", t=t, w=260, h=180)
        L.draw_grips(cr, fp)
    else:                                                     # ripped away, up into the sky
        u = t - T_SPIN
        O.draw_flag(cr, FLAGMAN_X + 110 - 1500 * u, 380 - 2400 * u + 500 * u * u, "checker", t=t * 2, w=260, h=180)
    # #1
    x = None
    if white and T_L1 - 0.2 <= t <= T_L1 + 0.4: x = lerp(FLAGX - 1700, FLAGX + 2000, (t - T_L1 + 0.2) / 0.6)
    if not white and T_L2 - 0.3 <= t <= T_L2 + 0.6: x = lerp(FLAGX - 1700, FLAGX + 2000, (t - T_L2 + 0.3) / 0.9)
    if x is not None:
        O.draw_racecar(cr, x, FLOOR_Y, s=1.0, col=LEADER, num="1", driver=True, spin=t * 40, sid=17880)
        for j in range(4): sketch_line(cr, [(x - 700, FLOOR_Y - 120 - 80 * j), (x - 1300, FLOOR_Y - 120 - 80 * j)], 6, sid=17700 + j, color=(1, 1, 1), alpha=0.8)

def victory_world(cr, t):
    O.draw_raceway(cr, t, ox=11000.0)
    O.draw_victory_arch(cr, VX, FLOOR_Y, w=1700)
    O.draw_racecar(cr, VX + 1000, FLOOR_Y, s=1.0, button=True, sid=17000)
    O.draw_confetti(cr, t, CUT_VIC + 0.1, VX - 1200, VX + 1300, -200, n=80)
    tc = trophy_state(t)
    if tc and tc[2] == "chief":
        pass

def world(cr, t):
    st = scene(t)
    if st == "theater": theater(cr, t)
    elif st == "pit": pit_lane(cr, t)
    elif st == "race": race_world(cr, t)
    elif st == "flag": flag_world(cr, t)
    else: victory_world(cr, t)
S.background(world)

# ================================================================ HIM
# --- theater: read, run to the EXIT
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(T_READ, react="deadpan", lines=1, dur=1.2, face="deadpan")
S.set(T_TURN, "stand", "deadpan", dur=0.2, look=(0.9, 0.0), turn=0.5)
S.set(T_RUN, "stand", "deadpan", dur=0.15, run=1.0, look=(0.9, 0.0), turn=0.5, lean=0.12)
S.xkeys.append((T_RUN, EXITX - 540 + 40, CUT_PIT - T_RUN + 0.05, "inn")); S.x = EXITX - 500
S.camera(T_RUN, EXITX - 120, 930, 1.0, 0.7)
S.sfx(T_RUN, "whoosh", 0.04); S.sfx(T_DOOR, "clack", 0.08)
S.flash(T_DOOR + 0.02, 0.55)
# --- pit lane: bursts out of the back door
PITCAM = (RX + 150, 800, 0.58)
S.cut(CUT_PIT - FR, cam=PITCAM, x=WALLX - 260 - 540)
S.set(CUT_PIT - FR, "stand", "deadpan", dur=0.0, run=1.0, look=(0.9, 0.0), turn=0.5, lean=0.12)
S.xkeys.append((CUT_PIT, RX - 200 - 540, T_STOP - CUT_PIT, "out")); S.x = RX - 200 - 540
S.set(T_STOP - 0.15, "stand", "deadpan", dur=0.15, run=0.0, look=(0.6, -0.2), turn=0.4, stretch=-0.2)
S.set(T_STOP + 0.05, "stand", "deadpan", dur=0.3, ease="back", look=(0.6, -0.2), turn=0.4)
S.sfx(T_STOP - 0.15, "skid", 0.05, dur=0.3)
for k, tp in enumerate(FAR_PASS):
    S.sfx(tp + 0.05, "whoosh", 0.09, dur=0.45)
S.set(T_LOOKCARS, "stand", "deadpan", dur=0.4, look=(0.5, -0.3), turn=0.3)
S.set(T_US, "stand", "dead_stare", dur=0.4, look=(0.0, 0.0), turn=0.0)
S.camera(CUT_PIT + 1.0, RX + 300, 860, 0.72, 2.0)
S.camera(T_BOARD - 0.2, (RX - 200 + CHX) / 2, 830, 0.85, 1.0)
S.set(T_LOOKB, "stand", "dead_stare", dur=0.3, look=(0.85, -0.6), turn=0.45)
S.set(T_GLANCE, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), turn=0.0)
S.set(T_POINTCAR + 0.25, "stand", "dead_stare", dur=0.35, look=(0.9, 0.0), turn=0.5)
S.camera(T_POINTCAR, RX + 450, 840, 0.62, 0.8)
S.sfx(T_BOARD + 0.05, "pat", 0.05); S.sfx(T_POINTCAR, "tok", 0.04)
# the helmet for the kitten
S.camera(T_UPCAT - 0.1, RX - 200 + 60, 780, 1.05, 0.7)
S.set(T_UPCAT, "stand", "deadpan", dur=0.3, look=(-0.1, -1.0), turn=0.0, brow=0.1)
S.set(T_DIG, "stand", "deadpan", dur=0.3, look=(0.3, 0.8), turn=0.1)
S.set(T_POP + 0.05, "stand", "deadpan", dur=0.3, look=(0.2, -0.9), turn=0.0)
S.set(T_CHIEF, "stand", "deadpan", dur=0.3, look=(0.85, -0.1), turn=0.45)
S.camera(T_CHIEF - 0.1, (RX - 200 + CHX) / 2, 820, 0.85, 0.5)
S.sfx(T_DIG + 0.1, "rummage", 0.05, dur=0.5); S.sfx(T_POP, "pop", 0.08); S.sfx(T_HELMON, "pat", 0.05)
S.blink(T_US + 0.6)
HELM_HAND_X = RX - 380
def helmet_hook(t, p):
    if T_DIG <= t < T_HELMON + 0.4:
        hip = (p["hip"][0] + 48, p["hip"][1] - 26)
        top = (p["head"][0] + 40, p["head"][1] - 170)
        if t < T_POP:
            u = smooth(ramp(t, T_DIG, T_DIG + 0.2)); dig = ramp(t, T_DIG + 0.2, T_DIG + 0.3)
            q = (hip[0] + 14 * math.sin(t * 24) * dig, hip[1] + 6 * math.sin(t * 31) * dig)
            p["rhand"] = lerp(p["rhand"], q, u)
        elif t < T_HELMON:
            q = lerp(hip, top, smooth(ramp(t, T_POP, T_HELMON - 0.05)))
            p["rhand"] = q; p["relb"] = (q[0] + 120, (q[1] + p["neck"][1]) / 2 + 120); p["rhand_t"] = "grip"
        else:
            p["rhand"] = lerp(top, p["rhand"], smooth(ramp(t, T_HELMON, T_HELMON + 0.4)))
    return p
S.hook(helmet_hook)

# --- in the car
L.POSES["drive"] = dict(lelb=(455, 1000), lhand=(440, 925), relb=(625, 1000), rhand=(640, 925), lhand_t="grip", rhand_t="grip",
                        lknee=(390, 1150), rknee=(690, 1150), lfoot=(470, 1250), rfoot=(610, 1250), nowalk=1.0)
DRV = dict(lag=0.0, nowalk=1.0)
WIDE = (GX + 80, 860, 0.56)
GRIDCAM = (GX + 120, 860, 0.68)
CLOSE = (GX - 40, 720, 1.12)
def car_cut(t, cam, x=GX, **kw):
    S.cut(t - FR, cam=cam, x=x - 540)
    S.set(t - FR, "drive", kw.pop("face", "deadpan"), dur=0.0, **DRV, **kw)
car_cut(CUT_GRID, GRIDCAM, look=(0.0, 0.0))
S.camera(CUT_GRID + 0.1, GX + 60, 820, 0.86, T_OUT - CUT_GRID - 0.2)     # slow creep in during the lights
for k, tl in enumerate(LIGHTS):
    S.sfx(tl, "boop", 0.07)
S.set(LIGHTS[0] + 0.2, "drive", "deadpan", dur=0.3, look=(-0.6, -0.9), turn=-0.2, **DRV)           # up at the lights
S.set(LIGHTS[2] + 0.1, "drive", "deadpan", dur=0.6, look=(-0.6, -0.9), turn=-0.2, sweat=0.3, **DRV)
S.set(LIGHTS[4] + 0.1, "drive", "holding_it", dur=0.6, look=(-0.6, -0.9), turn=-0.2, sweat=0.7, **DRV)
S.set(T_OUT + 0.05, "drive", "deadpan", dur=0.1, ease="snap", look=(0.6, 0.0), turn=0.3, sweat=0.4, stretch=0.06, **DRV)
S.sfx(T_OUT + 0.02, "whoosh", 0.1, dur=0.6); S.sfx(T_OUT + 0.15, "poof", 0.06)
S.set(T_OUT + 0.4, "drive", "deadpan", dur=0.3, look=(0.85, 0.0), turn=0.4, **DRV)
# close: the stare, the button
car_cut(CUT_CLOSE1, CLOSE, face="dead_stare", look=(0.0, 0.0))
S.camera(CUT_CLOSE1, GX - 40, 700, 1.2, 1.3)
S.set(T_UPK1, "drive", "dead_stare", dur=0.3, look=(-0.1, -1.0), **DRV)
S.set(T_PRESS1 + 0.12, "drive", "deadpan", dur=0.1, ease="snap", look=(0.0, 0.0), stretch=-0.1, **DRV)
S.sfx(T_PRESS1, "boop", 0.06)
# GO (the kitten pressed it)
car_cut(CUT_GO, WIDE, look=(0.0, 0.0), stretch=0.15)
S.set(CUT_GO + 0.3, "drive", "deadpan", dur=0.4, look=(0.0, 0.0), **DRV)
S.flash(T_PRESS1 + 0.1, 0.3, (1.0, 0.85, 0.5))
S.sfx(CUT_GO - 0.08, "kaboom", 0.3, dur=1.4); S.shake(CUT_GO, 0.6, 16)
for tp in PASSES: S.sfx(tp - 0.05, "whoosh", 0.05, dur=0.35)
S.camera(CUT_GO + 1.0, GX + 150, 860, 0.64, 3.0)
S.set(18.6, "drive", "deadpan", dur=0.4, look=(0.6, 0.3), turn=0.3, **DRV)                # watches one go by
S.set(19.4, "drive", "deadpan", dur=0.4, look=(0.0, 0.0), **DRV)
# pit stop
S.sfx(T_PITIN, "skid", 0.06, dur=0.9)
S.camera(T_PITIN + 0.2, GX + 220, 830, 0.62, 0.8)
S.poof(T_PIT - 0.02, at=(GX - 520, FLOOR_Y - 300), r=170, sound=False); S.poof(T_PIT - 0.02, at=(GX + 560, FLOOR_Y - 300), r=170, sound=False)
S.sfx(T_PIT, "poof", 0.05)
for k in range(12): S.sfx(T_PIT + 0.15 + 0.07 * k, "tick", 0.05)
S.camera(T_PIT + 0.35, GX - 40, 760, 1.0, 0.4)                                  # in on the squeegee
S.set(T_PIT + 0.4, "drive", "dead_stare", dur=0.15, look=(0.0, 0.0), lid=0.7, **DRV)
S.set(T_PIT + 1.25, "drive", "dead_stare", dur=0.2, look=(0.0, 0.0), **DRV)
S.sfx(T_PIT + 0.45, "squeak", 0.04); S.sfx(T_PIT + 0.85, "squeak", 0.04)
S.camera(T_PIT + 1.15, GX + 350, 830, 0.62, 0.4)
S.sfx(T_PITGO, "whoosh", 0.07, dur=0.5)
S.camera(T_PITGO + 0.1, GX + 150, 860, 0.66, 0.6)
S.blink(T_PIT + 1.6)
# flag stand 1: WHITE FLAG. #1 then him.
def flag_cut(t, t_him, dur):
    S.cut(t - FR, cam=FLAG_CAM, x=FLAGX - 1900 - 540)
    S.set(t - FR, "drive", "deadpan", dur=0.0, **DRV)
    S.xkeys.append((t_him - dur / 2, FLAGX - 1900 - 540, 0.001, "linear"))
    S.xkeys.append((t_him - dur / 2 + 0.002, FLAGX + 2100 - 540, dur, "linear")); S.x = FLAGX + 2100 - 540
flag_cut(CUT_FLAG1, T_HIM1, 0.45)
S.sfx(T_L1, "whoosh", 0.08, dur=0.4); S.sfx(T_HIM1, "whoosh", 0.08, dur=0.4)
# the chase
car_cut(CUT_CHASE, WIDE, look=(0.8, -0.1), turn=0.4)
S.camera(CUT_CHASE, GX + 300, 860, 0.64, 2.4)
S.set(27.55, "drive", "deadpan", dur=0.2, look=(0.8, -0.1), turn=0.4, lid=0.5, **DRV)          # #1 looks back at him
S.set(28.2, "drive", "deadpan", dur=0.3, look=(0.8, -0.1), turn=0.4, sweat=0.3, **DRV)
hb = 27.0; per = 0.6
while hb < T_PRESS2:
    S.sfx(hb, "thud", 0.05); S.sfx(hb + 0.16, "thud", 0.035); hb += per; per = max(0.32, per * 0.9)
# close 2: the look
car_cut(CUT_CLOSE2, CLOSE, look=(0.8, -0.1), turn=0.3, sweat=0.5)
S.camera(CUT_CLOSE2, GX - 50, 700, 1.25, 1.9)
S.set(CUT_CLOSE2 + 0.15, "drive", "holding_it", dur=0.4, look=(0.8, -0.1), turn=0.3, sweat=0.8, **DRV)
S.set(T_UPK2, "drive", "holding_it", dur=0.35, look=(-0.1, -1.0), turn=0.0, sweat=0.8, **DRV)
S.set(T_HNOD, "drive", "deadpan", dur=0.15, look=(-0.1, -1.0), sweat=0.6, **DRV)
S.set(T_HNOD + 0.2, "drive", "deadpan", dur=0.2, look=(-0.1, -1.0), sweat=0.6, **DRV)
def nod_hook(t, p):
    if T_HNOD <= t < T_HNOD + 0.35:
        d = 22 * math.sin(math.pi * (t - T_HNOD) / 0.35)
        p["head"] = (p["head"][0], p["head"][1] + d)
    return p
S.hook(nod_hook)
S.sfx(T_PRESS2, "boop", 0.07)
S.flash(T_PRESS2 + 0.08, 0.45)
S.sfx(T_PRESS2 + 0.1, "kaboom", 0.5, dur=2.2)
# BOOST
car_cut(CUT_BOOST, WIDE, look=(0.0, 0.0), stretch=0.2)
S.set(CUT_BOOST + 0.2, "drive", "dead_stare", dur=0.3, look=(0.0, 0.0), **DRV)
S.shake(CUT_BOOST, 0.8, 22)
S.sfx(CUT_BOOST + 0.1, "whoosh", 0.1, dur=0.5)
# flag stand 2: CHECKERED FLAG
flag_cut(CUT_FLAG2, T_HIM2, 0.15)
S.sfx(T_HIM2, "whoosh", 0.12, dur=0.6); S.shake(T_HIM2, 0.4, 14); S.sfx(T_L2, "whoosh", 0.05, dur=0.4)
S.camera(CUT_FLAG2 + 0.4, FLAGX - 150, 640, 0.75, 0.6)
# braking into victory lane
car_cut(CUT_BRAKE, (GX + 150, 830, 0.62), look=(0.0, 0.0))
S.sfx(CUT_BRAKE, "skid", 0.07, dur=1.5)
S.set(T_STOPPED + 0.05, "drive", "deadpan", dur=0.1, ease="snap", look=(0.0, 0.0), stretch=-0.08, **DRV)
S.set(T_STOPPED + 0.25, "drive", "dead_stare", dur=0.3, ease="back", look=(0.0, 0.0), **DRV)
S.camera(T_STOPPED + 0.1, GX + 60, 760, 0.82, 1.0)
S.blink(T_STOPPED + 0.9)

# --- victory lane
HIMV = VX - 60
VICCAM = (VX + 50, 840, 0.7)
S.cut(CUT_VIC - FR, cam=VICCAM, x=HIMV - 540)
S.set(CUT_VIC - FR, "stand", "deadpan", dur=0.0, look=(0.6, 0.0), turn=0.3)
S.sfx(CUT_VIC + 0.1, "pop", 0.08)
S.set(T_TROPHY_DOWN - 1.0, "stand", "deadpan", dur=0.3, look=(-0.9, 0.0), turn=-0.4)
S.set(T_LOOKUP_T, "stand", "deadpan", dur=0.7, look=(-0.6, -1.0), turn=-0.3, tilt=-0.05)
S.sfx(T_TROPHY_DOWN, "thud", 0.15); S.shake(T_TROPHY_DOWN, 0.3, 10)
S.set(T_MILK_GIVE - 0.1, "stand", "deadpan", dur=0.3, look=(0.85, 0.0), turn=0.45)
S.camera(T_MILK_GIVE - 0.4, HIMV + 150, 800, 1.0, 0.6)
L.POSES["drink"] = dict(relb=(640, 840), rhand=(600, 690), rhand_t="grip")
S.set(T_DRINK, "drink", "deadpan", dur=0.35, look=(0.0, -0.9), tilt=-0.25, lid=0.6)
S.set(T_DRINK1, "drink", "deadpan", dur=0.3, look=(0.0, -0.9), tilt=-0.25, lid=0.6)
S.set(T_MILK_DOWN, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), tilt=0.0)
for k in range(5): S.sfx(T_DRINK + 0.25 + 0.33 * k, "gulp", 0.05)
S.blink(T_MILK_DOWN + 0.5)
S.camera(T_HOP - 0.3, VX - 250, 820, 0.85, 0.7)
S.set(T_HOP, "stand", "dead_stare", dur=0.3, look=(-0.5, -0.9), turn=-0.2)
S.set(T_LOOKT, "stand", "dead_stare", dur=0.4, look=(-0.8, -0.2), turn=-0.4)
S.set(T_LOOKUS, "stand", "dead_stare", dur=0.4, look=(0.0, 0.0), turn=0.0)
S.sfx(T_HOP, "boing", 0.03); S.sfx(T_LAND, "pat", 0.05)
S.blink(T_LOOKUS + 0.6)
S.camera(T_LAND - 0.15, TROPHY_X + 140, 660, 1.35, 0.5)                         # in on the kitten in the cup
S.camera(T_LOOKUS + 0.3, HIMV - 120, 930, 0.9, 0.9)
S.t = T_ASK
S.the_ask(T_ASK, hold=ASK_HOLD, push=False)

def milk_state(t):
    """(x, y, ang, level) of the milk bottle, or None."""
    if t < T_MILK_GIVE - 0.6 or t >= T_ASK: return None
    return "chief" if t < T_MILK_TAKE else "him"
def drink_hook(t, p):
    if T_MILK_TAKE <= t < T_DRINK:
        q = lerp((HIMV + 300, 1010), (p["rhand"][0], p["rhand"][1]), 0.0)
        p["rhand"] = lerp(p["rhand"], (HIMV + 140, 960), smooth(ramp(t, T_MILK_TAKE - 0.2, T_MILK_TAKE)))
        p["rhand_t"] = "grip"
    return p
S.hook(drink_hook)

# ================================================================ the car he drives (follows his hips)
def car_x(t, p): return p["hip"][0]
def rot_about(pt, piv, a):
    dx, dy = pt[0] - piv[0], pt[1] - piv[1]; c, s_ = math.cos(a), math.sin(a)
    return (piv[0] + dx * c - dy * s_, piv[1] + dx * s_ + dy * c)
def car_hook(t, p):
    if not in_car(t): return p
    a = car_ang(t); j = jit(t)
    piv = (p["hip"][0] - 430, FLOOR_Y)
    for k in L.JOINTS:
        q = rot_about(p[k], piv, a) if a else p[k]
        p[k] = (q[0], q[1] + j)
    if a: p["tilt"] = p.get("tilt", 0.0) + a
    sq = squeegee_pos(t)
    return p
S.hook(car_hook)
def his_car(cr, t, p, ly):
    if not in_car(t): return
    x = car_x(t, p); a = car_ang(t); yb = FLOOR_Y + jit(t)
    spin = t * 45 * min(1.0, max(speed(t), 2000 if scene(t) == "flag" else 0) / 3000)
    pressed = 1.0 if (T_PRESS1 <= t < T_PRESS1 + 0.3 or T_PRESS2 <= t < T_PRESS2 + 0.3) else 0.0
    if ly == "back":
        flames(cr, t, x, yb, a)
        O.draw_racecar(cr, x, yb, part="back", button=True, pressed=pressed, ang=a, spin=spin, sid=17000)
        return
    O.draw_racecar(cr, x, yb, part="front", ang=a, spin=spin, sid=17000)
    hx = (p["lhand"][0] + p["rhand"][0]) / 2; hy = (p["lhand"][1] + p["rhand"][1]) / 2
    sketch_ellipse(cr, hx, hy + 8, 118, 30, 7, sid=17060, fill=None)                       # the steering wheel
    L.draw_grips(cr, p)
    if scene(t) == "flag":
        for j in range(5):
            sketch_line(cr, [(x - 700, yb - 120 - 120 * j), (x - 1600, yb - 120 - 120 * j)], 7, sid=17720 + j, color=(1, 1, 1), alpha=0.85)
    # pit stop: tyres fly off, dust at the wheels, the squeegee
    if T_PIT - 0.05 <= t < T_PIT + 1.3:
        for k, (wx, wr) in enumerate(((-430, 118), (460, 100))):
            u = t - T_PIT - 0.15
            if 0 <= u < 1.2:
                O.draw_tyre(cr, x + wx - 900 * u, yb - wr - 900 * u + 1600 * u * u, wr, ang=u * 10, sid=17090 + 10 * k)
            if t < T_PIT + 1.0:
                for i in range(6):
                    ang = t * 20 + i * 1.05
                    cr.arc(x + wx + 120 * math.cos(ang), yb - wr + 80 * math.sin(ang), 60, 0, 2 * math.pi)
                    cr.set_source_rgba(0.9, 0.9, 0.9, 0.85); cr.fill_preserve(); L.stroke_ink(cr, 4)
    sq = squeegee_pos(t)
    if sq is not None:
        hx_, hy_ = p["head"]
        O.draw_squeegee(cr, hx_ + sq, hy_ - 10, ang=-0.15)
    # braking: sparks + skid smoke
    if CUT_BRAKE <= t < T_STOPPED + 0.8:
        live = 1 - ramp(t, T_STOPPED - 0.3, T_STOPPED)
        for i in range(10):
            u = ((t * 3 + i * 0.37) % 1.0)
            sx, sy = x - 430 - 500 * u, yb - 10 - 220 * u + 260 * u * u
            if live > 0.05:
                sketch_line(cr, [(sx, sy), (sx + 40, sy + 8)], 6, sid=17730 + i, color=(1.0, 0.75, 0.2), alpha=live)
        sm = 1 - ramp(t, T_STOPPED + 0.1, T_STOPPED + 0.8)
        for i in range(5):
            O.draw_smoke_puff(cr, x - 300 - 260 * i + 40 * math.sin(t * 3 + i), yb - 120 - 30 * i, 170 + 30 * i, alpha=0.85 * sm)
S.prop(his_car)

def flames(cr, t, x, yb, a):
    """exhaust flames, streaming off screen to the left (the two boosts)."""
    big = 0.0
    if CUT_GO - 0.1 <= t < CUT_GO + 1.4: big = max(big, 0.7 * (1 - ramp(t, CUT_GO + 0.7, CUT_GO + 1.4)))
    if CUT_BOOST - FR <= t < CUT_BRAKE: big = max(big, 1.0)
    if scene(t) == "flag" and t >= CUT_FLAG2: big = 1.0 - ramp(t, T_HIM2 + 0.15, T_HIM2 + 0.55)
    if big <= 0: return
    ex, ey = O.rc_pt(x, yb, a, *O.RC_EXHAUST)
    for k, dy in enumerate((-40, 40, 0)):
        pts = [(ex - 260 * i, ey + dy + 26 * math.sin(t * 17 + i * 1.3 + k)) for i in range(12)]
        O.draw_flames(cr, pts, t + k, w=(150 - 35 * k) * big)

# ================================================================ the kitten (on his head; later in the trophy)
def kitten_spot(p, lift=0.0):
    hx, hy = p["head"]; a = p.get("tilt", 0.0)
    ox, oy = 5.0, -104.0 - lift
    return hx + ox * math.cos(a) - oy * math.sin(a), hy + ox * math.sin(a) + oy * math.cos(a), a
CUP = (TROPHY_X, FLOOR_Y - 1120 * 0.8 - 14)
def kitten(cr, t, p, ly):
    if ly != "front": return
    x, y, a = kitten_spot(p)
    st = scene(t)
    look = (0.0, 0.0); blink = 0.0
    if st == "theater": look = (0.6, -0.3) if t > T_TURN else (0.0, 0.0)
    if st == "pit":
        look = (0.8, 0.1)
        if T_POP <= t < T_HELMON: look = (0.4, -0.6)
        if T_HELMON + 0.2 <= t < T_HELMON + 0.8: blink = math.sin(math.pi * (t - T_HELMON - 0.2) / 0.6)
    if st == "race" and in_car(t):
        look = (0.4, 0.0)
        if T_KLOOK1 <= t < CUT_GO: look = (-0.9, -0.3)
        if T_KBUT <= t < T_KBACK: look = (-0.9, -0.3)
        if T_KBACK <= t < T_PRESS2: look = (0.2, 0.9); blink = math.sin(math.pi * min(1.0, (t - T_KBACK) / 0.6)) if t < T_KBACK + 0.6 else 0
        if T_PRESS2 <= t < CUT_BOOST: look = (-0.9, -0.3)
        if T_STOPPED <= t: look = (0.0, 0.0)
        if T_STOPPED + 0.6 <= t < T_STOPPED + 1.2: blink = math.sin(math.pi * (t - T_STOPPED - 0.6) / 0.6)
    if st == "victory":
        look = (-0.6, -0.4) if t < T_MILK_GIVE else (0.7, 0.4)
        if T_DRINK <= t < T_MILK_DOWN + 0.3: look = (0.5, -0.3)
        if t >= T_HOP - 0.4: look = (-0.9, -0.2)
    # the hop into the trophy
    if st == "victory" and t >= T_HOP:
        u = smooth(ramp(t, T_HOP, T_LAND))
        x = lerp(x, CUP[0], u); y = lerp(y, CUP[1], u) - 260 * math.sin(math.pi * u)
        a = 0.0
    helm = t >= T_HELMON
    if st == "victory" and t >= T_LAND:
        sl = ramp(t, T_SLEEP - 0.3, T_SLEEP)
        O.draw_cat(cr, x, y, s=KS, t=t, kind="loaf", col="black", look=(0.0, 0.3), blink=sl, sid=2000)
        if helm: O.draw_kitten_helmet(cr, x, y, KS, 0.0)
        return
    O.draw_cat(cr, x, y, s=KS, t=t, kind="loaf", col="black", look=look, blink=blink, sid=2000, tilt=a * 0.6)
    if helm: O.draw_kitten_helmet(cr, x, y, KS, a * 0.6)
    # the paw on the button
    for tp in (T_PRESS1, T_PRESS2):
        if tp - 0.25 <= t < tp + 0.35 and in_car(t):
            bx, by = O.rc_pt(car_x(t, p), FLOOR_Y + jit(t), car_ang(t), O.RC_BUTTON[0], O.RC_BUTTON[1] - 40)
            u = smooth(ramp(t, tp - 0.25, tp)) * (1 - smooth(ramp(t, tp + 0.15, tp + 0.35)))
            sx, sy = x - 30, y - 30
            ex_, ey_ = lerp((sx, sy), (bx + 10, by), u)
            fur = (0.13, 0.13, 0.15)
            sketch_line(cr, [(sx, sy), (ex_, ey_)], 16, sid=2050, color=fur)
            sketch_circle(cr, ex_, ey_, 15, 4, sid=2051, fill=fur)
S.prop(kitten)

def helmet_in_hand(cr, t, p, ly):
    if ly != "front" or not (T_POP <= t < T_HELMON): return
    hx, hy = p["rhand"]
    if t < T_POP + 0.25: L.burst_lines(cr, hx, hy - 40, (t - T_POP) / 0.4, r0=60, r1=130, n=8, sid=31)
    O.draw_kitten_helmet(cr, hx + 10, hy + 40, 0.75, 0.2)
    L.draw_grips(cr, p)
S.prop(helmet_in_hand)

# ================================================================ victory lane: the chief, the trophy, the milk
def trophy_state(t):
    if scene(t) != "victory": return None
    if t < T_TROPHY_DOWN:
        u = smooth(ramp(t, CUT_VIC + 0.1, T_TROPHY_DOWN - 0.15))
        return (lerp(VX + 1500, TROPHY_X, u), FLOOR_Y - 60 * (1 - ramp(t, T_TROPHY_DOWN - 0.15, T_TROPHY_DOWN)), "chief")
    return (TROPHY_X, FLOOR_Y, "down")
def vchief_pose(t):
    ts = trophy_state(t)
    if t < T_TROPHY_DOWN + 0.2:
        x = ts[0] + 380
    else:
        x = TROPHY_X + 380 + lerp(0, HIMV + 330 - TROPHY_X - 380, smooth(ramp(t, T_TROPHY_DOWN + 0.2, T_MILK_GIVE - 0.2)))
        x += 1400 * smooth(ramp(t, T_MILK_TAKE + 0.4, T_MILK_TAKE + 1.6))
    p = npc_pose(x, "deadpan", turn=-0.5, look=(-0.8, 0.0))
    if t < T_TROPHY_DOWN:
        p["lhand"] = (x - 330, 1000); p["lelb"] = (x - 200, 960); p["rhand"] = (x - 250, 1060); p["relb"] = (x - 90, 1050)
        p["lhand_t"] = p["rhand_t"] = "grip"
    elif T_MILK_GIVE - 0.5 <= t < T_MILK_TAKE:
        p["lhand"] = (x - 190, 960); p["lelb"] = (x - 120, 1010); p["lhand_t"] = "grip"
    return L.constrain(p)
def victory_props(cr, t, p, ly):
    if scene(t) != "victory": return
    ts = trophy_state(t)
    if ly == "back":
        if t < T_MILK_TAKE + 1.7:
            cp = vchief_pose(t)
            O.draw_staff(cr, t, cp, 0.0, s=1.0, kind="crew")
            if T_MILK_GIVE - 0.5 <= t < T_MILK_TAKE:
                O.draw_milk(cr, cp["lhand"][0] - 10, cp["lhand"][1] - 40, s=1.0)
                L.draw_grips(cr, cp)
        O.draw_trophy(cr, ts[0], ts[1], s=0.8, part="back")
        return
    O.draw_trophy(cr, ts[0], ts[1], s=0.8, part="front")
    if ts[2] == "chief":
        cp = vchief_pose(t); L.draw_grips(cr, cp)
    if T_MILK_TAKE <= t < T_ASK - 0.2:
        hx, hy = p["rhand"]
        lev = 1 - ramp(t, T_DRINK + 0.2, T_DRINK1)
        ang = 0.0
        if T_DRINK - 0.05 <= t < T_MILK_DOWN: ang = -2.5 * smooth(ramp(t, T_DRINK - 0.05, T_DRINK + 0.3)) * (1 - smooth(ramp(t, T_DRINK1, T_MILK_DOWN)))
        if t >= T_HOP - 0.6:                                    # sets the empty bottle down
            return
        O.draw_milk(cr, hx + 10 * math.cos(ang), hy - 40, s=1.0, ang=ang, level=lev)
        L.draw_grips(cr, p)
S.props.insert(0, victory_props)

def trophy_cover(cr, t, p, ly):
    """the trophy's front rim drawn over the sleeping kitten so it sits IN the cup."""
    if scene(t) != "victory" or ly != "front" or t < T_LAND - 0.1: return
    cx, cy = TROPHY_X, FLOOR_Y - 1120 * 0.8
    cr.save(); cr.rectangle(cx - 300, cy + 2, 600, 600); cr.clip()
    O.draw_trophy(cr, TROPHY_X, FLOOR_Y, s=0.8, part="front")
    cr.restore()
S.prop(trophy_cover)

# speed lines (screen space) while racing fast
def speed_ov(cr, t):
    if scene(t) != "race" or not in_car(t): return
    v = speed(t)
    if v < 2500: return
    a = min(1.0, (v - 2500) / 6000)
    for k in range(14):
        yy = 380 + (k * 397) % 1300
        xx = (1400 - ((t * 5200 + k * 523) % 2600))
        cr.move_to(xx, yy); cr.line_to(xx + 300 + 200 * a, yy)
        cr.set_source_rgba(1, 1, 1, 0.55 * a); cr.set_line_width(6); cr.stroke()
S.overlays.insert(0, speed_ov)

# start lights (world space, the grid): drawn as a background add-on
def lights_bg(cr, t):
    if not (CUT_GRID - FR <= t < CUT_CLOSE1 - FR): return
    n = sum(1 for tl in LIGHTS if t >= tl) if t < T_OUT else 0
    sketch_line(cr, [(GX - 900, 120), (GX + 2000, 120)], 14, sid=17950, color=(0.3, 0.3, 0.34))
    O.draw_start_lights(cr, GX - 230, 150, n_on=n, s=0.8)
S.background(lights_bg)

if __name__ == "__main__":
    print(f"end {S.t:.2f}", file=sys.stderr)
    S.render("day014.mp4")
