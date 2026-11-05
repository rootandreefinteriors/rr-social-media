"""Day 14 - COMMENT episode: @sohomnilesh "Go to diddy party" (Instagram, day 13 reel, 0 likes). Justin's pick + outline
(2026-11-05): a black car takes him to a lavish mansion with an extravagant driveway; he knocks, the door opens by
itself; a rich-people cocktail party; the host (white suit, dark sunglasses) taps him on the shoulder; staredown; the host
pulls out a bottle of baby oil and chases him around the house; he narrowly escapes back into the black car, which
speeds away; he writes the ask in the back of the car. The kitten is gone (Justin). PG-13: all implied. See BEATS.md.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import ramp, lerp, FLOOR_Y
from ink import smooth, sketch_rect, sketch_line, sketch_circle, sketch_ellipse, sketch_poly, draw_text
import numpy as np

FR = 1 / 30
def trap(t, a, b, c): return smooth(ramp(t, a, b)) * (1 - smooth(ramp(t, b, c)))

# ================================================================ places
FX = 120000.0; ASKX = 121250.0; EXITX = ASKX + 760.0          # the theater (day 13's ending)
SX = 200000.0; MX = SX - 600.0; CARX = SX + 1700.0             # the street outside MEGAPLEX 30, the black car
SEATX = 260000.0                                               # the back seat
DX = 300000.0                                                  # the driveway (the car stays here; the world scrolls)
DOORX = 400000.0                                               # the mansion's front door
HX = 500000.0                                                  # the ballroom
HDOOR = HX - 1800.0; EASEL = HX - 1350.0; BOUNCER = HX - 1100.0; HIMH = HX - 800.0; TOWER = HX + 200.0
GUESTS = ((HX + 700, "smug", 0.0), (HX + 1050, "neutral", 1.3), (HX + 1450, "smug", 2.1), (HX + 1850, "neutral", 0.7))
HW = 600000.0                                                  # the west wing hallway (doors)
HWD = (HW - 900.0, HW - 300.0, HW + 300.0, HW + 900.0)
EXCAR = DOORX + 1500.0                                         # the car waiting at the steps

# ================================================================ timeline
T_READ = 0.3; T_TURN = 1.6; T_RUN = 1.8; T_DOOR = 2.4
CUT_ST = 2.6; T_CDOOR = 3.0; T_LOOKD = 3.35; T_US1 = 3.9; T_WALK = 4.4
CUT_SEAT1 = 5.4
CUT_DRIVE = 7.2; T_ARRIVE = 12.0
CUT_DOOR = 12.6; KNOCKS = (13.0, 13.3, 13.6); T_OPEN = 14.1; T_US2 = 14.7
CUT_HALL = 15.4; T_NOD = 16.6; T_SELF = 17.0; T_US3 = 17.6
T_WAITER = 17.6; T_TAKE = 18.6; T_EAT = 19.0
T_HOSTWALK = 19.4; T_TAP = 20.8; T_TURNH = 21.15; T_STARTLE = 21.35
CUT_C1 = 22.2; CUT_C2 = 23.0; CUT_C3 = 23.8
T_REACH = 24.2; T_BOTTLE = 24.8; SQUEEZES = (25.3, 25.65)
T_LOOKB = 26.1; T_US4 = 26.6; T_RUNA = 27.2
CUT_HALLWAY = 28.4
CUT_HALL2 = 32.9; T_SQUIRT = 33.5; T_SLIP = 34.15; T_SLIDE1 = 35.2
T_HSLIP = 34.85; T_CRASH = 35.55
T_WATCH = 35.6; T_US5 = 36.2; T_RUNB = 36.6; T_GONE = 37.35
CUT_OUT = 37.6; T_INCAR = 38.6; T_PEEL = 38.9; T_HOSTDOOR = 39.1
CUT_SEAT2 = 40.7; T_BACK = 41.2; T_US6 = 42.1; T_BAG = 42.6; T_BAGTAKE = 43.2; T_PEEK = 43.6; T_MINI = 44.1
T_STARE = 44.5; T_US7 = 45.1; T_TOSS = 45.7
T_ASK = 46.8
ASK_HOLD = 9.5

def scene(t):
    for a, nm in ((CUT_ASKSEAT := CUT_SEAT2, "seat"), (CUT_OUT, "out"), (CUT_HALL2, "hall"), (CUT_HALLWAY, "hallway"),
                  (CUT_HALL, "hall"), (CUT_DOOR, "door"), (CUT_DRIVE, "drive"), (CUT_SEAT1, "seat"), (CUT_ST, "street")):
        if t >= a - FR: return nm
    return "theater"

# ---------------------------------------------------------------- the driveway treadmill
def speed(t):
    if t < CUT_DRIVE or t >= T_ARRIVE: return 0.0
    return 2900.0 * (1 - smooth(ramp(t, T_ARRIVE - 0.9, T_ARRIVE)))
_TT = np.arange(0, 70, 1 / 240)
_POS = np.concatenate([[0.0], np.cumsum([speed(x) / 240 for x in _TT[:-1]])])
def P(t): return float(np.interp(t, _TT, _POS))
P_END = P(T_ARRIVE)

S = M.Scene(x0=ASKX - 540)
S.auto_blinks = False
S.floor = False
S.card("sohomnilesh", "Go to diddy party", "0", t0=0.3)
CAM0 = (ASKX + 120, 930, 1.1)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0

# ================================================================ helpers
def npc_pose(x, face="deadpan", body="stand", **kw):
    p = L.pose(body, face, **kw)
    ox = x - 540
    for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1])
    p["breath_ph"] = 0.0
    return L.constrain(p)

def walk_legs(p, ph, amp=70):
    s_ = math.sin(ph)
    p["lfoot"] = (p["lfoot"][0] + amp * s_, p["lfoot"][1] - 30 * max(0.0, math.cos(ph)))
    p["rfoot"] = (p["rfoot"][0] - amp * s_, p["rfoot"][1] - 30 * max(0.0, -math.cos(ph)))
    return p

# ================================================================ sets
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
    dx0, dx1, dy0 = EXITX - 160, EXITX + 260, FLOOR_Y - 860
    op = smooth(ramp(t, T_DOOR - 0.05, T_DOOR + 0.12))
    sketch_rect(cr, dx0 - 30, dy0 - 30, dx1 + 30, FLOOR_Y, 7, sid=17500, fill=(0.30, 0.20, 0.22))
    sketch_rect(cr, dx0, dy0, dx1, FLOOR_Y, 6, sid=17501, fill=(0.10, 0.12, 0.24) if op > 0 else (0.55, 0.56, 0.6))
    if op > 0: sketch_rect(cr, dx1 - 30 - 330 * (1 - op), dy0, dx1, FLOOR_Y, 6, sid=17502, fill=(0.55, 0.56, 0.6))
    else: sketch_rect(cr, dx0 + 290, dy0 + 430, dx0 + 360, dy0 + 470, 4, sid=17503, fill=(0.85, 0.85, 0.88))
    sketch_rect(cr, dx0 + 40, dy0 - 200, dx1 - 40, dy0 - 70, 6, sid=17504, fill=(0.20, 0.70, 0.35))
    draw_text(cr, "EXIT", (dx0 + dx1) / 2, dy0 - 135, 76, color=(255, 255, 255))

def street(cr, t):
    O.draw_city_night(cr, t, SX - 5000, SX + 6000)
    O.draw_megaplex(cr, MX, FLOOR_Y, t)
    O.draw_limo(cr, CARX, FLOOR_Y, door=smooth(ramp(t, T_CDOOR, T_CDOOR + 0.6)))

def seat(cr, t):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    cr.rectangle(vx0, vy0, vx1 - vx0, vy1 - vy0); cr.set_source_rgb(0.10, 0.10, 0.13); cr.fill()
    wx0, wy0, wx1, wy1 = SEATX - 430, 330, SEATX + 430, 960                 # the rear window
    cr.save(); cr.rectangle(wx0, wy0, wx1 - wx0, wy1 - wy0); cr.clip()
    cr.rectangle(wx0, wy0, wx1 - wx0, wy1 - wy0); cr.set_source_rgb(*O.NIGHT_SKY[1]); cr.fill()
    if t < CUT_DRIVE:                                                        # city lights streaming past
        for k in range(8):
            xx = wx1 + 200 - ((t * 1500 + k * 260) % 1300)
            sketch_rect(cr, xx, wy0 + 260 + 60 * (k % 3), xx + 160, wy1, 3, sid=18600 + k, fill=(0.20, 0.20, 0.32))
            cr.arc(xx + 60, wy0 + 120 + 40 * (k % 2), 22, 0, 2 * math.pi); cr.set_source_rgb(1, 0.9, 0.5); cr.fill()
    else:                                                                    # the mansion, getting smaller
        u = ramp(t, CUT_SEAT2, CUT_SEAT2 + 6.0, "linear")
        sc = lerp(0.16, 0.05, u ** 0.6)
        cr.save(); cr.translate(SEATX, wy1 - 40); cr.scale(sc, sc); cr.translate(-DOORX, -FLOOR_Y)
        O.draw_mansion(cr, DOORX, FLOOR_Y, t)
        cr.restore()
        cr.rectangle(wx0, wy1 - 40, wx1 - wx0, 40); cr.set_source_rgb(0.25, 0.25, 0.28); cr.fill()
    cr.restore()
    sketch_rect(cr, wx0, wy0, wx1, wy1, 7, sid=18610, fill=None)
    sketch_line(cr, [(wx0 + 60, wy0 + 40), (wx0 + 200, wy0 + 200)], 8, sid=18611, color=(1, 1, 1), alpha=0.25)
    sketch_rect(cr, SEATX - 760, 900, SEATX + 760, FLOOR_Y + 300, 7, sid=18612, fill=(0.18, 0.16, 0.16))   # the seat back
    for k in (-1, 0, 1): sketch_line(cr, [(SEATX + k * 500, 940), (SEATX + k * 500, 1300)], 4, sid=18613, color=(0.10, 0.09, 0.09))
    for k in range(4):                                                        # little ceiling lights
        cr.arc(SEATX - 600 + 400 * k, 230, 10, 0, 2 * math.pi); cr.set_source_rgb(0.75, 0.80, 1.0); cr.fill()

def seat_front(cr, t, p, ly):
    if ly != "front" or scene(t) != "seat": return
    sketch_rect(cr, SEATX - 900, 1370, SEATX + 900, FLOOR_Y + 600, 7, sid=18620, fill=(0.12, 0.11, 0.11))
    for d in (-1, 1):
        sketch_rect(cr, SEATX + d * 420 - 260, 1300, SEATX + d * 420 + 260, FLOOR_Y + 600, 7, sid=18621 + (d > 0), fill=(0.20, 0.18, 0.18))
S.prop(seat_front)

# driveway: gate, fountains, signs, lamps, hedges; the mansion at the end
DRIVE_ITEMS = (("gate", 900), ("fountain", 2600), ("sign", 3700, "DRIVEWAY|CONTINUES"), ("fountain", 5400),
               ("sign", 6500, "STILL|DRIVEWAY"), ("fountain", 8200), ("sign", 9600, "ALMOST"))
def drive(cr, t):
    ox = P(t)
    O.draw_night_sky(cr, FLOOR_Y, t, ox)
    vx0, vy0, vx1, vy1 = O._visible(cr)
    mx = DX + P_END + 1200 - ox
    O.draw_mansion(cr, mx, FLOOR_Y - 380, t)
    cr.rectangle(vx0, FLOOR_Y - 420, vx1 - vx0, 60); cr.set_source_rgb(0.16, 0.34, 0.20); cr.fill()
    for k in range(int((vx0 + ox) // 500) - 1, int((vx1 + ox) // 500) + 2):
        xx = k * 500 - ox
        if xx > mx - 2700: continue
        O.draw_hedge(cr, xx, FLOOR_Y - 360, s=0.8, sid=18120 + k % 3)
    cr.rectangle(vx0, FLOOR_Y - 360, vx1 - vx0, vy1 - FLOOR_Y + 360); cr.set_source_rgb(0.84, 0.80, 0.72); cr.fill()
    for k in range(int((vx0 + ox) // 300) - 1, int((vx1 + ox) // 300) + 2):
        xx = k * 300 - ox
        cr.move_to(xx, FLOOR_Y - 360); cr.line_to(xx - 120, vy1); cr.set_source_rgba(0.6, 0.55, 0.48, 0.6); cr.set_line_width(4); cr.stroke()
    sketch_line(cr, [(vx0, FLOOR_Y - 360), (vx1, FLOOR_Y - 360)], 5, sid=18630)
    for k in range(int((vx0 + ox) // 1400) - 1, int((vx1 + ox) // 1400) + 2):
        xx = k * 1400 + 700 - ox
        if xx > mx - 2700: continue
        O.draw_lamp(cr, xx, FLOOR_Y - 340, sid=18130)
    for it in DRIVE_ITEMS:
        xx = DX + it[1] - ox
        if not (vx0 - 1600 < xx < vx1 + 1600): continue
        if it[0] == "gate": O.draw_gate(cr, xx, FLOOR_Y - 330)
        elif it[0] == "fountain": O.draw_fountain(cr, xx, FLOOR_Y - 340, t, s=1.1)
        else: O.draw_sign(cr, xx, FLOOR_Y - 340, it[2], size=60)

def door_set(cr, t, door=None):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    O.draw_night_sky(cr, FLOOR_Y, t)
    op = smooth(ramp(t, T_OPEN, T_OPEN + 1.0)) if door is None else door
    O.draw_mansion(cr, DOORX, FLOOR_Y, t, door=op)
    cr.rectangle(vx0, FLOOR_Y, vx1 - vx0, vy1 - FLOOR_Y); cr.set_source_rgb(0.84, 0.80, 0.72); cr.fill()
    sketch_line(cr, [(vx0, FLOOR_Y), (vx1, FLOOR_Y)], 5, sid=18640)

def outside(cr, t):
    door_set(cr, t, door=1.0)
    if t < T_INCAR + 0.15: dr = 1.0
    else: dr = 1 - smooth(ramp(t, T_INCAR + 0.05, T_INCAR + 0.25))
    dx = 0.0 if t < T_PEEL else 2600 * (t - T_PEEL) ** 2
    O.draw_limo(cr, EXCAR + dx, FLOOR_Y, door=dr, spin=-dx / 120)
    if t >= T_PEEL:
        for k in range(5):
            u = (t - T_PEEL) - k * 0.12
            if 0 < u < 1.2:
                O.draw_smoke_puff(cr, EXCAR - 1000 + 300 * u - 120 * k, FLOOR_Y - 100 - 160 * u, 120 + 200 * u, alpha=0.8 * (1 - u / 1.2))

def hall(cr, t):
    O.draw_hall(cr, t, yb=FLOOR_Y)
    O.draw_double_door(cr, HDOOR, FLOOR_Y, open_=1.0 if (CUT_HALL - FR <= t < CUT_HALL + 0.6 or T_RUNB + 0.4 <= t) else 0.0, sid=18700)
    for cx in (HX - 1300, HX + 300, HX + 1700): O.draw_chandelier(cr, cx, 180, t)
    O.draw_easel(cr, EASEL, FLOOR_Y)
    crashed = t >= T_CRASH and scene(t) == "hall" and t >= CUT_HALL2
    if not crashed:
        O.draw_champagne_tower(cr, TOWER, FLOOR_Y, t)
    else:
        O.draw_champagne_tower(cr, TOWER, FLOOR_Y, t, fall=min(1.2, t - T_CRASH))
    # the bouncer at the easel
    look = (0.8, 0.2) if t < T_NOD + 0.6 else (0.3, 0.0)
    bp = npc_pose(BOUNCER, "deadpan", turn=0.4, look=look)
    if T_NOD <= t < T_NOD + 0.4: bp["head"] = (bp["head"][0], bp["head"][1] + 28 * math.sin(math.pi * (t - T_NOD) / 0.4))
    O.draw_staff(cr, t, bp, 0.0, s=1.1, kind="plain", vest=(0.98, 0.98, 0.96))
    # guests in white, holding coupes (unbothered by everything)
    for k, (gx, face, ph) in enumerate(GUESTS):
        gp = npc_pose(gx, face, turn=-0.4 if k % 2 else 0.4, look=(-0.7 if k % 2 else 0.7, 0.0), lid=0.4)
        gp["head"] = (gp["head"][0] + 6 * math.sin(t * 2 + ph), gp["head"][1] + 8 * math.sin(t * 3 + ph))
        sip = k == 1 and T_CRASH + 0.4 <= t < T_CRASH + 1.4 and t >= CUT_HALL2
        hand = (gx + 40, 700) if sip else (gx + 120, 960)
        gp["rhand"] = hand; gp["relb"] = (gx + 130, 1040); gp["rhand_t"] = "grip"
        gp = L.constrain(gp)
        O.draw_staff(cr, t, gp, 0.0, s=1.0, kind="plain", vest=(0.99, 0.99, 0.97))
        O.draw_coupe(cr, gp["rhand"][0], gp["rhand"][1] + 30, 0.9)
        L.draw_grips(cr, gp)
    # the waiter
    if T_WAITER - 0.8 <= t < T_EAT + 1.6 and t < CUT_HALLWAY:
        wx = lerp(HX + 600, HIMH + 330, smooth(ramp(t, T_WAITER - 0.8, T_WAITER))) + 1600 * smooth(ramp(t, T_EAT + 0.4, T_EAT + 1.6))
        wp = npc_pose(wx, "deadpan", turn=-0.4, look=(-0.8, 0.0))
        wp["lhand"] = (wx - 150, 900); wp["lelb"] = (wx - 100, 1000); wp["lhand_t"] = "flat"; wp = L.constrain(wp)
        O.draw_staff(cr, t, wp, 0.0, s=1.05, kind="plain", vest=(0.12, 0.12, 0.14))
        tx, ty = wp["lhand"]
        sketch_ellipse(cr, tx, ty - 10, 130, 18, 5, sid=18710, fill=(0.85, 0.86, 0.9))
        for i in range(3 if t < T_TAKE else 2):
            sketch_circle(cr, tx - 60 + 60 * i, ty - 34, 14, 4, sid=18711 + i, fill=(0.95, 0.75, 0.45))
    # the oil puddle (second hall scene)
    if t >= T_SQUIRT + 0.45 and t >= CUT_HALL2:
        O.draw_oil_puddle(cr, HX + 820, FLOOR_Y, 340 * smooth(ramp(t, T_SQUIRT + 0.45, T_SQUIRT + 0.7)))

def hallway(cr, t):
    O.draw_hall(cr, t, yb=FLOOR_Y, windows=False)
    sketch_rect(cr, HW - 300, 120, HW + 300, 260, 6, sid=18750, fill=(0.12, 0.12, 0.14))
    draw_text(cr, "WEST WING", HW, 190, 70, color=(255, 214, 80))
    for k, dx_ in enumerate(HWD):
        O.draw_double_door(cr, dx_, FLOOR_Y, open_=door_open(t, k), w=420, h=1000, sid=18760 + 10 * k)

# who goes in/out of which door in the hallway: (t_appear, door_from, t_vanish, door_to)
HIM_HW = ((CUT_HALLWAY + 0.15, 0, 29.4, 2), (30.8, 3, 32.1, 0))
HOST_HW = ((29.6, 1, 30.7, 3), (31.4, 2, 32.75, 0))
def door_open(t, k):
    v = 0.0
    for sched in (HIM_HW, HOST_HW):
        for (ta, da, tv, dv) in sched:
            for tt, d in ((ta, da), (tv, dv)):
                if d == k: v = max(v, trap(t, tt - 0.25, tt, tt + 0.35))
    return v

def world(cr, t):
    st = scene(t)
    {"theater": theater, "street": street, "seat": seat, "drive": drive, "door": door_set, "hall": hall,
     "hallway": hallway, "out": outside}[st](cr, t)
S.background(world)

# ================================================================ HIM
HIDE = dict(show=0.0, nowalk=1.0)
# theater -> EXIT
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(T_READ, react="deadpan", lines=1, dur=1.2, face="deadpan")
S.set(T_TURN, "stand", "deadpan", dur=0.2, look=(0.9, 0.0), turn=0.5)
S.set(T_RUN, "stand", "deadpan", dur=0.15, run=1.0, look=(0.9, 0.0), turn=0.5, lean=0.12)
S.xkeys.append((T_RUN, EXITX - 500, CUT_ST - T_RUN + 0.05, "inn")); S.x = EXITX - 500
S.camera(T_RUN, EXITX - 120, 930, 1.0, 0.7)
S.sfx(T_RUN, "whoosh", 0.04); S.sfx(T_DOOR, "clack", 0.08)
# the street: the black car's back door opens by itself
S.cut(CUT_ST - FR, cam=(SX + 900, 860, 0.6), x=SX + 250 - 540)
S.set(CUT_ST - FR, "stand", "deadpan", dur=0.0, look=(0.8, 0.0), turn=0.4)
S.set(T_LOOKD, "stand", "deadpan", dur=0.3, look=(0.9, 0.1), turn=0.5)
S.set(T_US1, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), turn=0.0)
S.sfx(T_CDOOR, "slide_down", 0.04, dur=0.6)
S.camera(CUT_ST + 0.2, SX + 800, 880, 0.72, 1.6)
S.walk_to(T_WALK, CARX - 260 - 540, 0.8)
# back seat 1
SEATCAM = (SEATX, 900, 0.95)
S.cut(CUT_SEAT1 - FR, cam=SEATCAM, x=SEATX - 540)
S.set(CUT_SEAT1 - FR, "stand", "deadpan", dur=0.0, look=(0.0, 0.0), nowalk=1.0)
S.set(CUT_SEAT1 + 0.8, "stand", "deadpan", dur=0.3, look=(-0.6, -0.5), turn=-0.4, nowalk=1.0)
S.set(CUT_SEAT1 + 1.4, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), nowalk=1.0)
S.camera(CUT_SEAT1, SEATX, 880, 1.05, 1.8)
# the driveway (he's inside the car: hidden)
S.cut(CUT_DRIVE - FR, cam=(DX + 300, 760, 0.42), x=DX - 540)
S.set(CUT_DRIVE - FR, "stand", "deadpan", dur=0.0, **HIDE)
S.camera(T_ARRIVE - 1.5, DX + 900, 400, 0.3, 1.6)
def drive_car(cr, t, p, ly):
    if ly != "back" or scene(t) != "drive": return
    O.draw_limo(cr, DX, FLOOR_Y, spin=-P(t) / 120)
S.prop(drive_car)
# the door: knock knock. it opens by itself.
S.cut(CUT_DOOR - FR, cam=(DOORX, 880, 0.7), x=DOORX - 540)
S.set(CUT_DOOR - FR, "stand", "deadpan", dur=0.0, look=(0.0, -0.5), back=0.0)
L.POSES["knock"] = dict(relb=(650, 870), rhand=(640, 760), rhand_t="fist")
for k, tk in enumerate(KNOCKS):
    S.set(tk - 0.1, "knock", "deadpan", dur=0.08, look=(0.2, -0.6), lean=-0.02)
    S.set(tk + 0.02, "knock", "deadpan", dur=0.08, look=(0.2, -0.6), lean=0.02)
    S.sfx(tk, "tok", 0.1)
S.set(KNOCKS[-1] + 0.25, "stand", "deadpan", dur=0.3, look=(0.0, -0.5))
S.sfx(T_OPEN, "slide_down", 0.05, dur=1.0)
S.set(T_OPEN + 0.5, "stand", "deadpan", dur=0.4, look=(0.0, -0.4), lid=0.2)
S.set(T_US2, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0))
S.camera(CUT_DOOR + 0.1, DOORX, 900, 0.82, 2.5)
# the ballroom
S.cut(CUT_HALL - FR, cam=(HX - 900, 880, 0.62), x=HIMH - 540)
S.set(CUT_HALL - FR, "stand", "deadpan", dur=0.0, look=(-0.6, 0.0), turn=-0.3)
S.set(CUT_HALL + 0.5, "stand", "deadpan", dur=0.3, look=(-0.8, 0.0), turn=-0.4)          # the bouncer is looking at him
S.set(T_SELF, "stand", "deadpan", dur=0.3, look=(0.0, 0.9), turn=0.0, tilt=0.06)          # looks down at himself (white)
S.set(T_US3, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0))
S.sfx(T_NOD, "tok", 0.03)
S.camera(CUT_HALL + 0.2, HX - 800, 860, 0.72, 2.0)
S.set(T_WAITER + 0.1, "stand", "deadpan", dur=0.3, look=(0.9, 0.2), turn=0.5)
L.POSES["take"] = dict(relb=(650, 980), rhand=(720, 930), rhand_t="grab")
S.set(T_TAKE - 0.25, "take", "deadpan", dur=0.25, look=(0.9, 0.4), turn=0.4)
L.POSES["eat"] = dict(relb=(640, 900), rhand=(580, 720), rhand_t="fist")
S.set(T_EAT - 0.1, "eat", "deadpan", dur=0.3, look=(0.0, 0.0))
S.set(T_EAT + 0.5, "stand", "deadpan", dur=0.3, look=(0.0, 0.0))
for k in range(3): S.sfx(T_EAT + 0.1 + 0.3 * k, "chomp", 0.035)
def canape(cr, t, p, ly):
    if ly == "front" and T_TAKE <= t < T_EAT + 0.1:
        hx, hy = p["rhand"]; sketch_circle(cr, hx + 6, hy - 22, 14, 4, sid=18712, fill=(0.95, 0.75, 0.45))
S.prop(canape)
S.camera(T_HOSTWALK, HIMH + 130, 820, 0.85, 1.2)
# the tap. startle.
S.sfx(T_TAP, "tap", 0.08); S.sfx(T_TAP + 0.18, "tap", 0.08)
S.set(T_TURNH, "stand", "deadpan", dur=0.2, look=(0.9, -0.5), turn=0.5)
S.set(T_STARTLE, "stand", "deadpan", dur=0.08, ease="snap", look=(0.8, -0.6), turn=0.5, eyescale=1.3, pupil=0.55, brow=0.9,
      curl_up=1.0, hop=60, mouth="o", open=0.25, lean=-0.06)
S.set(T_STARTLE + 0.35, "stand", "deadpan", dur=0.3, look=(0.85, -0.6), turn=0.5, eyescale=1.15, pupil=0.7, brow=0.4, curl_up=0.6)
S.sfx(T_STARTLE, "boing", 0.04)
S.set(CUT_C1 - FR, "stand", "dead_stare", dur=0.0, look=(0.85, -0.55), turn=0.5, sweat=0.4, curl_up=0.4)
S.cut(CUT_C1 - FR, cam=(HIMH + 40, 640, 1.45))
S.set(CUT_C1 + 0.4, "stand", "dead_stare", dur=0.1, look=(0.85, -0.55), turn=0.5, sweat=0.5, twitch=0.7, curl_up=0.4)
S.set(CUT_C1 + 0.6, "stand", "dead_stare", dur=0.2, look=(0.85, -0.55), turn=0.5, sweat=0.6, curl_up=0.4)
S.cut(CUT_C2 - FR, cam=(HIMH + 250, 560, 1.5))
S.cut(CUT_C3 - FR, cam=(HIMH + 130, 820, 0.95))
S.set(T_BOTTLE + 0.25, "stand", "dead_stare", dur=0.3, look=(0.9, -0.2), turn=0.5, sweat=0.7)
S.sfx(T_BOTTLE, "pop", 0.08)
for sq in SQUEEZES: S.sfx(sq, "squeak", 0.05)
S.set(T_LOOKB, "stand", "dead_stare", dur=0.3, look=(0.9, -0.1), turn=0.5, sweat=0.8, eyescale=1.1)
S.set(T_US4, "stand", "dead_stare", dur=0.25, look=(0.0, 0.0), turn=0.0, sweat=0.8)
S.camera(T_LOOKB, HIMH + 100, 760, 1.1, 0.8)
# RUN (left, out of shot)
S.set(T_RUNA, "stand", "deadpan", dur=0.12, run=1.0, look=(-0.9, 0.0), turn=-0.5, lean=-0.12, sweat=0.6)
S.xkeys.append((T_RUNA, HIMH - 1700 - 540, CUT_HALLWAY - T_RUNA, "inn")); S.x = HIMH - 1700 - 540
S.camera(T_RUNA, HIMH - 300, 860, 0.62, 0.6)
S.sfx(T_RUNA, "whoosh", 0.06)
# the west wing: doors
HWCAM = (HW, 860, 0.55)
S.cut(CUT_HALLWAY - FR, cam=HWCAM, x=HWD[0] - 540)
S.set(CUT_HALLWAY - FR, "stand", "deadpan", dur=0.0, run=1.0, look=(0.9, 0.0), turn=0.5, lean=0.1, nowalk=0.0, sweat=0.6)
(ta, da, tv, dv), (tb, db, tw, dw) = HIM_HW
S.xkeys.append((ta, HWD[da] - 540, 0.001, "linear")); S.xkeys.append((ta + 0.01, HWD[dv] - 540, tv - ta - 0.01, "linear"))
S.set(tv, "stand", "deadpan", dur=0.05, run=1.0, look=(0.9, 0.0), turn=0.5, sweat=0.6, show=0.0)
S.xkeys.append((tb - 0.02, HWD[db] - 540, 0.001, "linear"))
S.set(tb, "stand", "deadpan", dur=0.05, run=1.0, look=(0.9, 0.2), turn=0.6, lean=-0.1, sweat=0.7, show=1.0)       # looks back while running left
S.xkeys.append((tb + 0.01, HWD[dw] - 540, tw - tb - 0.01, "linear"))
S.set(tw, "stand", "deadpan", dur=0.05, run=1.0, sweat=0.7, show=0.0)
for tt in (ta, tv, tb, tw): S.sfx(tt, "clack", 0.05)
for (t1, d1, t2, d2) in HOST_HW: S.sfx(t1, "clack", 0.04); S.sfx(t2, "clack", 0.04)
# back in the ballroom: he runs in from the right; the oil; the slide under the table; the host wipes out
HALL2CAM = (HX + 250, 860, 0.5)
S.cut(CUT_HALL2 - FR, cam=HALL2CAM, x=HX + 1900 - 540)
S.set(CUT_HALL2 - FR, "stand", "deadpan", dur=0.0, run=1.0, look=(-0.9, 0.0), turn=-0.5, lean=-0.12, sweat=0.7, show=1.0)
S.xkeys.append((CUT_HALL2, HX + 820 - 540, T_SLIP - CUT_HALL2, "linear"))
S.set(T_SLIP, "lie_back", "deadpan", dur=0.15, ease="snap", look=(0.0, -0.4), sweat=0.7, nowalk=1.0, eyescale=1.15)
S.xkeys.append((T_SLIP + 0.01, HX - 700 - 540, T_SLIDE1 - T_SLIP, "out"))
S.sfx(T_SQUIRT, "splat", 0.05); S.sfx(T_SLIP, "skid", 0.07, dur=0.9)
S.set(T_SLIDE1 + 0.05, "stand", "deadpan", dur=0.25, ease="back", look=(0.9, 0.0), turn=0.5, sweat=0.7)
S.set(T_WATCH, "stand", "dead_stare", dur=0.2, look=(0.9, 0.0), turn=0.5, sweat=0.6)
S.sfx(T_HSLIP, "skid", 0.06, dur=0.6); S.sfx(T_CRASH, "kaboom", 0.25, dur=1.2); S.shake(T_CRASH, 0.5, 16)
for k in range(6): S.sfx(T_CRASH + 0.25 + 0.11 * k, "clack", 0.04)
S.set(T_US5, "stand", "dead_stare", dur=0.25, look=(0.0, 0.0), turn=0.0, sweat=0.6)
S.camera(T_CRASH - 0.2, HX - 200, 860, 0.58, 0.6)
S.set(T_RUNB, "stand", "deadpan", dur=0.12, run=1.0, look=(-0.9, 0.0), turn=-0.5, lean=-0.12, sweat=0.6)
S.xkeys.append((T_RUNB, HDOOR - 540, T_GONE - T_RUNB, "linear"))
S.set(T_GONE, "stand", "deadpan", dur=0.05, show=0.0, run=1.0)
S.camera(T_RUNB, HX - 1100, 860, 0.58, 0.8)
S.sfx(T_RUNB, "whoosh", 0.05)
# outside: into the car, the car peels out. the host in the doorway.
S.cut(CUT_OUT - FR, cam=(DOORX + 800, 760, 0.4), x=DOORX - 540)
S.set(CUT_OUT - FR, "stand", "deadpan", dur=0.0, run=1.0, look=(0.9, 0.0), turn=0.5, lean=0.12, sweat=0.6, show=1.0)
S.xkeys.append((CUT_OUT, EXCAR - 140 - 540, T_INCAR - CUT_OUT, "linear"))
S.set(T_INCAR, "stand", "deadpan", dur=0.05, show=0.0, nowalk=1.0)
S.sfx(T_INCAR + 0.15, "thud", 0.12); S.sfx(T_PEEL, "skid", 0.07, dur=0.8); S.sfx(T_PEEL + 0.1, "whoosh", 0.08, dur=0.6)
S.camera(T_PEEL, DOORX + 500, 760, 0.4, 2.0)
# back seat 2: the escape. the party favor.
S.cut(CUT_SEAT2 - FR, cam=(SEATX, 900, 1.0), x=SEATX - 540)
S.set(CUT_SEAT2 - FR, "stand", "holding_it", dur=0.0, look=(0.0, 0.0), sweat=0.9, breath_rate=3.0, show=1.0, nowalk=1.0)
S.set(T_BACK, "stand", "holding_it", dur=0.3, look=(-0.3, -1.0), turn=-0.6, tilt=-0.08, sweat=0.8, breath_rate=2.5, nowalk=1.0)
S.set(T_US6, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), sweat=0.5, breath_rate=1.6, nowalk=1.0)
S.set(T_BAG, "stand", "dead_stare", dur=0.3, look=(-0.7, 0.6), turn=-0.3, sweat=0.4, nowalk=1.0)
L.POSES["hold_bag"] = dict(relb=(650, 1000), rhand=(700, 1050), rhand_t="grip")
S.set(T_BAGTAKE, "hold_bag", "dead_stare", dur=0.3, look=(0.7, 0.6), turn=0.3, sweat=0.3, nowalk=1.0)
L.POSES["hold_mini"] = dict(relb=(650, 1000), rhand=(700, 1050), rhand_t="grip", lelb=(440, 960), lhand=(470, 860), lhand_t="grip")
S.set(T_MINI, "hold_mini", "dead_stare", dur=0.3, look=(-0.4, 0.3), sweat=0.2, nowalk=1.0)
S.set(T_US7, "hold_mini", "dead_stare", dur=0.3, look=(0.0, 0.0), nowalk=1.0)
L.POSES["toss"] = dict(relb=(650, 1000), rhand=(700, 1050), rhand_t="grip", lelb=(420, 760), lhand=(380, 600), lhand_t="open")
S.set(T_TOSS, "toss", "dead_stare", dur=0.15, look=(0.0, 0.0), nowalk=1.0)
S.set(T_TOSS + 0.4, "hold_bag", "dead_stare", dur=0.3, look=(0.0, 0.0), nowalk=1.0)
S.set(T_ASK - 0.45, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), nowalk=1.0)
S.sfx(T_BAGTAKE, "flip", 0.05); S.sfx(T_MINI, "pop", 0.06); S.sfx(T_TOSS + 0.05, "whoosh", 0.05)
S.blink(T_US6 + 0.5, T_US7 + 0.4)
S.camera(T_STARE, SEATX, 870, 1.1, 1.0)
S.camera(T_ASK - 0.6, SEATX, 930, 1.0, 0.6)
S.t = T_ASK
S.the_ask(T_ASK, hold=ASK_HOLD, push=False)

def favor(cr, t, p, ly):
    if ly != "front" or scene(t) != "seat" or t < T_BAG - 0.4 or t >= T_ASK - 0.4: return
    if t < T_BAGTAKE:                                                     # the driver's arm passes it back
        u = smooth(ramp(t, T_BAG - 0.4, T_BAG + 0.3))
        hx, hy = lerp((SEATX - 1000, 1300), (SEATX + 60, 1150), u)
        sketch_line(cr, [(SEATX - 1200, 1450), (hx, hy)], 34, sid=18800, color=(0.1, 0.1, 0.12))
        O.draw_gift_bag(cr, hx, hy - 40, 0.9)
        return
    hx, hy = p["rhand"]
    O.draw_gift_bag(cr, hx, hy + 90, 0.9)
    L.draw_grips(cr, p)
    if T_MINI <= t < T_TOSS + 0.6:
        lx, ly_ = p["lhand"]
        if t < T_TOSS:
            if t < T_MINI + 0.25: L.burst_lines(cr, lx, ly_ - 40, (t - T_MINI) / 0.4, r0=50, r1=110, n=8, sid=31)
            O.draw_baby_oil(cr, lx, ly_ - 40, s=0.35)
        else:
            u = (t - T_TOSS) / 0.6
            O.draw_baby_oil(cr, lx - 500 * u, ly_ - 300 * u + 400 * u * u, s=0.35, ang=-8 * u)
        L.draw_grips(cr, p)
S.prop(favor)

# ================================================================ THE HOST
HS = 1.15
def host_state(t):
    """(pose, bottle, squeeze, visible)"""
    st = scene(t)
    if st == "hall" and t < CUT_HALLWAY:
        if t < T_HOSTWALK: return None
        u = smooth(ramp(t, T_HOSTWALK, T_TAP - 0.15))
        x = lerp(HX + 1300, HIMH + 260, u)
        if t >= T_RUNA + 0.3: x = HIMH + 260 - 600 * ramp(t, T_RUNA + 0.3, CUT_HALLWAY, "linear")
        p = npc_pose(x, "deadpan", turn=-0.5, look=(-0.8, 0.0))
        if T_HOSTWALK <= t < T_TAP - 0.15 or t >= T_RUNA + 0.3: p = walk_legs(p, t * 9, 60)
        if T_TAP - 0.25 <= t < T_TURNH + 0.4:                                   # the tap
            g = trap(t, T_TAP - 0.25, T_TAP - 0.05, T_TURNH + 0.4)
            p["lhand"] = lerp(p["lhand"], (HIMH + 95, 790 + 15 * math.sin(t * 40) * (t < T_TAP + 0.3)), g)
            p["lelb"] = lerp(p["lelb"], (x - 110, 840), g); p["lhand_t"] = "flat"
        bottle = None; sq = 0.0
        if T_REACH <= t < T_BOTTLE:
            g = smooth(ramp(t, T_REACH, T_REACH + 0.3)); p["rhand"] = lerp(p["rhand"], (x - 10, 860), g); p["relb"] = (x + 90, 960)
        if t >= T_BOTTLE:
            g = smooth(ramp(t, T_BOTTLE, T_BOTTLE + 0.25))
            p["rhand"] = lerp((x - 10, 860), (x + 200, 900), g); p["relb"] = (x + 130, 1000); p["rhand_t"] = "grip"; bottle = "r"
            sq = max(trap(t, s0 - 0.08, s0, s0 + 0.15) for s0 in SQUEEZES)
        return L.constrain(p), bottle, sq
    if st == "hallway":
        for (ta, da, tv, dv) in HOST_HW:
            if ta <= t < tv:
                x = lerp(HWD[da], HWD[dv], (t - ta) / (tv - ta))
                d = -1 if HWD[dv] < HWD[da] else 1
                p = walk_legs(npc_pose(x, "deadpan", turn=0.5 * d, look=(0.8 * d, 0.0)), t * 9, 60)
                p["rhand"] = (x + 120 * d, 820); p["relb"] = (x + 60 * d, 930); p["rhand_t"] = "grip"
                return L.constrain(p), "r", 0.0
        return None
    if st == "hall":                                                         # second ballroom scene
        if t < T_HSLIP:
            x = lerp(HX + 2200, HX + 900, ramp(t, CUT_HALL2, T_HSLIP, "linear"))
            p = walk_legs(npc_pose(x, "deadpan", turn=-0.5, look=(-0.8, 0.0)), t * 9, 60)
            sq = trap(t, T_SQUIRT - 0.1, T_SQUIRT, T_SQUIRT + 0.4)
            p["rhand"] = (x - 140, 780 - 40 * sq); p["relb"] = (x - 30, 900); p["rhand_t"] = "grip"
            return L.constrain(p), "r", sq
        if t < T_CRASH:                                                      # slips: slides feet-first into the tower
            u = ramp(t, T_HSLIP, T_CRASH, "linear")
            x = lerp(HX + 900, TOWER + 300, u)
            p = npc_pose(x, "deadpan", body="lie_back", look=(-0.5, -0.5))
            p = L.constrain(p)
            return p, "r", 0.0
        x = TOWER + 330
        p = npc_pose(x, "deadpan", body="sit_floor", look=(-0.6, 0.0))
        up = smooth(ramp(t, T_CRASH + 0.9, T_CRASH + 1.3))
        p["rhand"] = (x - 120, lerp(1300, 950, up)); p["relb"] = (x - 40, lerp(1260, 1080, up)); p["rhand_t"] = "grip"
        return L.constrain(p), "r", 0.0
    if st == "out" and t >= T_HOSTDOOR:
        x = DOORX
        p = npc_pose(x, "deadpan", look=(0.8, 0.0), turn=0.3)
        w = smooth(ramp(t, T_HOSTDOOR + 0.5, T_HOSTDOOR + 0.8))
        p["lhand"] = (x - 150, lerp(1100, 650 + 30 * math.sin(t * 7), w)); p["lelb"] = (x - 140, lerp(1000, 820, w)); p["lhand_t"] = "open"
        p["rhand"] = (x + 120, 900); p["relb"] = (x + 80, 1000); p["rhand_t"] = "grip"
        p = L.constrain(p)
        for j in L.JOINTS: p[j] = (p[j][0], p[j][1] - 120)                   # standing on the top step
        return p, "r", 0.0
    return None

def host(cr, t, p, ly):
    hs = host_state(t)
    if hs is None: return
    hp, bottle, sq = hs
    st = scene(t)
    front_now = (st == "hall" and t < CUT_HALLWAY and T_TAP - 0.3 <= t)
    if (ly == "front") != front_now and st != "hallway": return
    if st == "hallway" and ly != "front": return
    if st == "out":
        cr.save(); cr.translate(0, -120 * 0)
    O.draw_host(cr, hp, t, s=HS, bottle=bottle, squeeze=sq, smirk=0.5)
    if st == "out": cr.restore()
    # the squirt: a stream of oil arcing ahead onto the floor
    if st == "hall" and t >= CUT_HALL2 and T_SQUIRT - 0.05 <= t < T_SQUIRT + 0.5:
        fx = (hp["lfoot"][0] + hp["rfoot"][0]) / 2
        bx = fx + (hp["rhand"][0] - fx) * HS; by = FLOOR_Y + (hp["rhand"][1] - 70 - 140 - FLOOR_Y) * HS
        u = ramp(t, T_SQUIRT - 0.05, T_SQUIRT + 0.3)
        pts = [(bx - 520 * v * u * 2, by - 200 * v * u * 2 + 900 * (v * u * 2) ** 2) for v in [i / 12 for i in range(13)]]
        pts = [q for q in pts if q[1] < FLOOR_Y + 20]
        O.draw_oil_stream(cr, pts, 20)
S.prop(host)

def glint(cr, t):
    """close-up on the host: his shades catch the chandelier light."""
    if not (CUT_C2 - FR <= t < CUT_C3 - FR): return
    u = (t - CUT_C2 - 0.3) / 0.35
    if 0 <= u <= 1:
        x, y = 560 + 100, 860
        r = 70 * math.sin(math.pi * u)
        cr.set_source_rgba(1, 1, 1, 0.95); cr.set_line_width(8)
        for a in (0, math.pi / 2):
            cr.move_to(x - r * math.cos(a), y - r * math.sin(a)); cr.line_to(x + r * math.cos(a), y + r * math.sin(a)); cr.stroke()
S.overlay(glint)
S.sfx(CUT_C2 + 0.35, "twinkle", 0.04)

if __name__ == "__main__":
    print(f"end {S.t:.2f}", file=sys.stderr)
    S.render("day014.mp4")
