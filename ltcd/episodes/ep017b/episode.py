"""Day 17 ALT (Justin's direction): @elijah_paradise "Get a girlfriend and have a baby" (Instagram, day 16 reel, 1 like).
Rom-com speedrun: rose fails, the spaghetti kiss, the delivery stork, a montage (SOLD sign, slow dance, fridge photo,
couch cuddle), record scratch, the breakup tropes (he games while she bounces the crying baby; the sink full of dishes;
she vacuums in front of his game; 3 AM, she waits up with the baby; the argument; WE NEED TO TALK), she leaves with the baby - and comes back for the couch. He shrugs, sits down,
plays video games again; the camera pushes into the TV: TELL ME WHAT TO DO NEXT IN THE COMMENTS. See BEATS.md.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
import character as C
from ltcd import Track, ramp, lerp, FLOOR_Y
from ink import smooth, sketch_line, draw_text
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FR = 1 / 30

# ================================================================ places
BX = 700000.0
WX0, WX1 = BX - 6000.0, BX + 12000.0
PROM_END = BX - 1300.0; SUGAR = BX + 2600.0
RBX, RB = BX - 300.0 + 3600.0, 1500.0
LANDX = 705313.3938825098; BOX = LANDX - 540.0
PX = 900000.0                                       # the park bench
HX0 = PX - 200.0; GXS = PX + 200.0
SKX, SKS = PX - 820.0, 1.2                          # the stork lands LEFT of him, facing right
EX = 1100000.0                                      # the house, outside
IX = 1300000.0                                      # the house, inside
COUCHX = IX - 150.0; TVX = IX + 650.0; DOORX = IX - 900.0; FRIDGEX = IX + 1600.0; SINKX = IX + 1240.0; LAMPX = IX + 230.0; CLOCK = (IX - 150.0, 560.0); OUTLET = (IX + 1010.0, FLOOR_Y - 230.0)
SEAT_L, SEAT_R = COUCHX - 190.0, COUCHX + 190.0

# ================================================================ timeline
T_READ = 0.3; T_WIDE = 1.45; T_US0 = 1.7; T_RUN = 2.0; CUT1 = 3.0; T_ARR = 3.6
T_P1 = 3.8; T_POP1 = T_P1 + 1.4
G1A, G1B = 5.0, 7.4
T_PETAL = 7.6; T_US1 = 7.9; T_TOSS = 8.15; T_SIT = 8.45
T_P3 = 8.95; T_POP3 = T_P3 + 1.4
G3A, G3B = 9.7, 10.7; T_SNIFF = 10.85; G3C, G3D = 11.2, 11.75
T_PLATE = 12.0; T_NOOD = 12.6; T_SLURP0 = 13.0; T_KISS = 14.8; T_RIGID = 15.15
ST_IN0, ST_IN1 = 15.9, 16.9; T_CLIP = 17.0; T_SIGN0, T_SIGN1 = 17.3, 17.9; T_DROP = 18.15; T_GOT = 18.45
T_TIP = 18.6; ST_UP0, ST_UP1 = 18.9, 19.9; T_AWW = 19.2; T_SMILE0 = 19.6
T_MUS = 20.2
M1 = 20.4; T_SOLD = 20.65
M2 = 22.2
M3 = 24.2; T_STICK = 24.75
M4 = 26.0
T_SCRATCH = 27.6
D1 = 27.8; G_IN0, G_IN1 = 27.9, 28.9; T_STARE = 29.1; T_BLOCK0, T_BLOCK1 = 30.1, 30.5; T_LEANA = 30.65; T_STORM0, T_STORM1 = 31.0, 31.55
D2 = 31.6; HW0, HW1 = 31.7, 32.5; T_LOOKP = 32.6; T_LOOKG = 33.0; T_ADD = 33.4; T_LEAVE = 33.95; T_STEAM = 34.1
D3 = 34.8; VAC0 = 34.95; T_YANK = 36.6; T_MAD = 36.85
D3B = 38.0; T_DOOR0 = 38.5; SN0, SN1 = 38.65, 40.0; T_LAMP = 40.2; T_GRIN = 41.4
SH = 5.0
D4 = 37.6 + SH; ARG = [(37.85 + SH, 0.35), (38.5 + SH, 0.6), (39.15 + SH, 1.0)]; T_DOTS = 39.9 + SH
D5 = 41.0 + SH; T_GULP = 41.7 + SH
L1 = 42.8 + SH; GL0, GL1 = 43.0 + SH, 44.05 + SH; T_DOOR1 = 43.7 + SH; T_SLAM1 = 44.35 + SH; T_FRAME = 44.6 + SH
L2 = 45.6 + SH; T_DOOR2 = 45.6 + SH; GR0, GR1 = 45.75 + SH, 46.3 + SH; T_GRAB = 46.4 + SH; GD0, GD1 = 46.55 + SH, 47.45 + SH; T_SLAM2 = 47.75 + SH
T_LOOKTV = 48.1 + SH; T_US3 = 48.6 + SH; T_SHRUG = 48.9 + SH; T_WALK = 49.65 + SH; T_FLOOR = 50.35 + SH; T_PAD = 50.7 + SH
T_PUSH = 51.3 + SH; T_TEXT = 51.9 + SH
T_END = 61.0 + SH

# ================================================================ scene
S = M.Scene(x0=BOX)
S.auto_blinks = False
S.floor = False
S.card("elijah_paradise", "Get a girlfriend and have a baby", "1", t0=0.3)
CAM_B = (LANDX, 880, 1.0)
S.camkeys[0] = (0.0, CAM_B, 0); S.cam = CAM_B

def couch_tape(t): return 0.0
def door_open3(t): return smooth(ramp(t, T_DOOR0 - 0.2, T_DOOR0 + 0.1)) * (1 - smooth(ramp(t, SN1, SN1 + 0.3))) if D3B <= t < D4 else 0.0
def tv_mode(t):
    if t >= T_TEXT: return "text"
    if T_YANK + 0.05 <= t < D4: return "off"
    return "game"
def couch_x(t):
    if t >= T_SLAM2 - 0.05: return None
    if t >= GD0: return COUCHX + (GX.at(t) - (COUCHX - 610))
    return COUCHX
def door_open(t):
    a = smooth(ramp(t, T_DOOR1 - 0.3, T_DOOR1)) * (1 - smooth(ramp(t, T_SLAM1 - 0.1, T_SLAM1)))
    b = smooth(ramp(t, T_DOOR2 - 0.05, T_DOOR2 + 0.15)) * (1 - smooth(ramp(t, T_SLAM2 - 0.1, T_SLAM2)))
    return max(a, b)

def world(cr, t):
    if t < CUT1 - FR:
        O.draw_beach_world(cr, t, WX0, WX1, PROM_END, sugar_x=SUGAR)
        O.draw_rainbow(cr, RBX, FLOOR_Y, RB + 30, band=60, sweep=1.0)
        O.draw_kite(cr, LANDX + 330, FLOOR_Y - 30, s=0.8, ang=1.35, t=0.0, tail=0.0)
        return
    if t < M1 - FR:
        O.draw_park_world(cr, t, PX - 6000, PX + 8000, trees=(PX - 1700, PX - 650, PX + 900, PX + 2300), lamps=(PX - 1150, PX + 650, PX + 2600))
        O.draw_bench(cr, PX, FLOOR_Y - 10)
        return
    if t < M2 - FR:
        O.draw_park_world(cr, t, EX - 6000, EX + 6000, trees=(EX - 1300, EX + 1400), lamps=())
        O.draw_house_front(cr, EX, FLOOR_Y - 150)
        O.draw_picket_fence(cr, EX - 1500, EX - 300, FLOOR_Y - 140); O.draw_picket_fence(cr, EX + 300, EX + 1500, FLOOR_Y - 140)
        O.draw_sold_sign(cr, EX + 620, FLOOR_Y - 30, drop=smooth(ramp(t, T_SOLD - 0.25, T_SOLD)) if t < T_SOLD else 1.0)
        return
    O.draw_room(cr, t, IX - 3000, IX + 3000, door_x=DOORX, door_open=max(door_open(t), door_open3(t)), frame_x=IX - 450,
                frame_fall=smooth(ramp(t, T_FRAME, T_FRAME + 0.3)) if t >= T_FRAME else 0.0, win_x=IX + 250 if False else None,
                kitchen_x=IX + 1000)
    if t < D2 - FR or t >= D3 - FR:
        cx = couch_x(t)
        if D3B - FR <= t < D4 - FR or (t >= D4 - FR and couch_x(t) is not None and t < L2): pass
        if cx is not None:
            if L2 <= t < T_SLAM2 + 0.1:
                cr.save(); cr.rectangle(DOORX - 200, -9000, 99999, 99999); cr.clip()
            O.draw_couch(cr, cx, FLOOR_Y - 10, tape=couch_tape(t))
            if L2 <= t < T_SLAM2 + 0.1: cr.restore()
    O.draw_wall_clock(cr, *CLOCK, hour=3.0 if D3B - FR <= t < D4 - FR else 7.0, minute=0.0 if D3B - FR <= t < D4 - FR else 20.0)
    O.draw_side_lamp(cr, LAMPX, FLOOR_Y - 10, on=1.0 if (t >= T_LAMP or t < D3B - FR) else 0.0, glow=1.0 if T_LAMP <= t < D4 - FR else 0.0)
    O.draw_outlet(cr, *OUTLET)
    plugged = not (T_YANK <= t < D4)
    if plugged: sketch_line(cr, [(TVX + 280, FLOOR_Y - 330), (OUTLET[0] - 10, FLOOR_Y - 250), (OUTLET[0], OUTLET[1])], 5, sid=20200, amp=0.4)
    else:
        u = min(1.0, (t - T_YANK) / 0.3)
        sketch_line(cr, [(TVX + 280, FLOOR_Y - 330), (OUTLET[0] - 60 * u, FLOOR_Y - 150 + 80 * u)], 5, sid=20200, amp=0.4)
    if D3 - FR <= t < D3B - FR:                                    # the vacuum cord, from the outlet
        q = g_pose(t); vb = vac_base(q)
        sketch_line(cr, [(OUTLET[0], OUTLET[1] + 20), (OUTLET[0] - 40, FLOOR_Y - 40), (vb + 60, FLOOR_Y - 60)], 4, sid=20201, amp=0.4, color=(0.2, 0.2, 0.25))
    O.draw_tv(cr, TVX, FLOOR_Y - 10, t, screen=tv_mode(t))
    O.draw_sink_counter(cr, SINKX, FLOOR_Y - 10, n=24, extra=1 if t >= T_ADD + 0.1 else 0,
                        wobble=(1 - ramp(t, T_ADD + 0.1, T_ADD + 1.1)) if T_ADD + 0.1 <= t < T_ADD + 1.1 else 0.0, t=t)
    O.draw_fridge(cr, FRIDGEX, FLOOR_Y - 10, photo=1.0 if t >= T_STICK + 0.05 else 0.0)
S.background(world)

# ================================================================ poses
def P(name, **kw): L.POSES[name] = kw
P("sit_bench", head=(540, 752), neck=(540, 878), hip=(540, 1228), lknee=(400, 1300), rknee=(680, 1300), lfoot=(430, FLOOR_Y), rfoot=(650, FLOOR_Y),
  lelb=(465, 1075), lhand=(462, 1200), relb=(615, 1075), rhand=(618, 1200), lfoot_dir=-0.5, rfoot_dir=0.5, nowalk=1.0)
L.POSES["offer"] = dict(relb=(690, 880), rhand=(830, 830), rhand_t="grip")
L.POSES["toss"] = dict(relb=(650, 700), rhand=(560, 560), rhand_t="open")
L.POSES["hold_plate"] = dict(L.POSES["sit_bench"], lelb=(455, 1060), lhand=(495, 1145), relb=(625, 1060), rhand=(590, 1145), lhand_t="grip", rhand_t="grip")
L.POSES["sit_hold"] = dict(L.POSES["sit_bench"], lelb=(470, 1040), lhand=(480, 1110), relb=(610, 1040), rhand=(600, 1110), lhand_t="grip", rhand_t="grip")
L.POSES["sit_pad"] = dict(L.POSES["sit_bench"], lelb=(470, 1060), lhand=(515, 1105), relb=(610, 1060), rhand=(570, 1105), lhand_t="grip", rhand_t="grip")
L.POSES["sit_cross"] = dict(L.POSES["sit_bench"], lelb=(470, 1060), lhand=(605, 1000), relb=(610, 1060), rhand=(475, 1000))
L.POSES["sit_sign"] = dict(L.POSES["sit_bench"], lelb=(410, 1000), lhand=(330, 1060), lhand_t="none")
L.POSES["floor_pad"] = dict(L.POSES["sit_floor"], lelb=(470, 1210), lhand=(515, 1250), relb=(610, 1210), rhand=(570, 1250), lhand_t="grip", rhand_t="grip")
L.POSES["dance"] = dict(lelb=(470, 980), lhand=(560, 960), relb=(640, 960), rhand=(700, 980))
L.POSES["plate_carry"] = dict(relb=(640, 980), rhand=(700, 950), rhand_t="grip")
L.POSES["plate_up"] = dict(relb=(700, 760), rhand=(760, 560), rhand_t="grip")
L.POSES["g_vac"] = dict(lelb=(600, 960), lhand=(680, 960), lhand_t="grip", relb=(630, 980), rhand=(700, 990), rhand_t="grip")
L.POSES["cross_stand"] = dict(L.POSES["arms_crossed"])
L.POSES["shrug2"] = dict(L.POSES["shrug"])
L.POSES["g_read"] = dict(lelb=(470, 960), lhand=(510, 885), relb=(610, 960), rhand=(570, 885), lhand_t="grip", rhand_t="grip")
L.POSES["g_sit"] = dict(L.POSES["sit_bench"], head=(540, 740), neck=(540, 862), hip=(540, 1205), lelb=(468, 1060), lhand=(480, 1180), relb=(612, 1060), rhand=(600, 1180))
L.POSES["g_sit_hold"] = dict(L.POSES["g_sit"], lelb=(470, 1030), lhand=(480, 1100), relb=(610, 1030), rhand=(600, 1100), lhand_t="grip", rhand_t="grip")
L.POSES["g_sit_cross"] = dict(L.POSES["g_sit"], lelb=(470, 1050), lhand=(605, 990), relb=(610, 1050), rhand=(475, 990))
L.POSES["g_sit_tape"] = dict(L.POSES["g_sit"], lelb=(440, 900), lhand=(345, 760), lhand_t="grip")
L.POSES["g_point"] = dict(lelb=(420, 860), lhand=(310, 820), lhand_t="point")
L.POSES["g_dance"] = dict(lelb=(450, 820), lhand=(390, 760), relb=(630, 820), rhand=(690, 760))
L.POSES["g_stick"] = dict(relb=(670, 820), rhand=(790, 820), rhand_t="flat")
L.POSES["g_up"] = dict(lelb=(420, 820), lhand=(330, 730), lhand_t="point")
L.POSES["g_suit"] = dict(lelb=(470, 1000), lhand=(500, 1010), lhand_t="grip", relb=(640, 1000), rhand=(660, 1150), rhand_t="grip")
L.POSES["g_drag"] = dict(lelb=(600, 1000), lhand=(740, 1120), lhand_t="grip", relb=(640, 980), rhand=(770, 1110), rhand_t="grip", lean=-0.12)

# ================================================================ HIM
def dig_pull(t0, hold_pose, look=(0.4, -0.2), sitting=False, **kw):
    POCK = (595 + S.x, 1200 if sitting else 1092)
    S.set(t0, "sit_bench" if sitting else "stand", "deadpan", dur=0.35, look=(0.35, 0.9), tilt=0.05, **kw)
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

# ---- beach -> park
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(T_READ, react="deadpan", lines=1, dur=1.05, face="deadpan")
S.set(T_WIDE, "stand", "deadpan", dur=0.12, ease="snap", eyescale=1.18, curl_up=0.8, look=(0.7, -0.8))
S.set(T_US0, "stand", "dead_stare", dur=0.2, look=(0.0, 0.0))
S.set(T_RUN, "stand", "deadpan", dur=0.15, run=1.0, look=(0.9, 0.0), turn=0.5, lean=0.12)
S.xkeys.append((T_RUN, BOX + 1300, CUT1 - T_RUN, "inn")); S.x = BOX + 1300
S.camera(T_RUN, LANDX + 250, 880, 1.0, 1.0); S.sfx(T_RUN, "whoosh", 0.05)
S.cut(CUT1 - FR, cam=(PX - 250, 900, 0.95), x=PX - 1350 - 540)
S.set(CUT1 - FR, "stand", "deadpan", dur=0.0, run=1.0, look=(0.9, 0.0), turn=0.5, lean=0.12)
S.xkeys.append((CUT1, HX0 - 540, T_ARR - CUT1, "out")); S.x = HX0 - 540
S.camera(CUT1, PX + 60, 900, 0.95, 0.8)
S.set(T_ARR - 0.1, "stand", "deadpan", dur=0.12, ease="snap", stretch=-0.25, look=(0.3, 0.0))
S.set(T_ARR + 0.1, "stand", "deadpan", dur=0.25, ease="back", look=(0.0, 0.0)); S.sfx(T_ARR - 0.1, "skid", 0.05, dur=0.35)
# rose
dig_pull(T_P1, "offer", look=(0.0, 0.0))
S.set(G1A + 0.3, "offer", "dead_stare", dur=0.3, look=(0.8, 0.0), turn=0.4, smile=0.25, twitch=0.4)
S.set(G1A + 1.2, "offer", "dead_stare", dur=0.4, look=(-0.2, 0.0), turn=0.0, smile=0.25)
S.set(G1A + 1.8, "offer", "dead_stare", dur=0.4, look=(-0.9, 0.0), turn=-0.5, smile=0.0)
S.set(T_PETAL - 0.1, "offer", "dead_stare", dur=0.25, look=(0.7, -0.3), turn=0.2)
S.set(T_US1, "offer", "dead_stare", dur=0.2, look=(0.0, 0.0), turn=0.0)
S.set(T_TOSS, "toss", "deadpan", dur=0.12, ease="snap"); S.sfx(T_TOSS, "whoosh", 0.04)
S.set(T_SIT, "sit_bench", "resigned", dur=0.35, look=(0.0, 0.2)); S.sfx(T_SIT + 0.3, "thud", 0.04)
# spaghetti
dig_pull(T_P3, "hold_plate", look=(0.0, 0.7), sitting=True)
S.set(T_SNIFF + 0.15, "hold_plate", "deadpan", dur=0.3, look=(0.8, 0.0), turn=0.2)
S.set(T_PLATE, "sit_bench", "dead_stare", dur=0.35, look=(0.6, 0.5), turn=0.4,
      lelb=(510, 1060), lhand=(640, 1205), relb=(660, 1060), rhand=(740, 1210), lhand_t="grip", rhand_t="grip")
KISS_H = dict(head=(642, 768), neck=(588, 882)); NOOD_H = dict(head=(585, 792), neck=(556, 890))
S.set(T_NOOD - 0.2, "sit_bench", "deadpan", dur=0.35, turn=0.9, look=(0.6, 0.6), mouth="o", open=0.25, **NOOD_H)
S.set(T_SLURP0, "sit_bench", "deadpan", dur=0.35, turn=1.0, look=(0.8, 0.0), mouth="o", open=0.2, **NOOD_H)
S.set(T_KISS - 0.05, "sit_bench", "deadpan", dur=T_KISS - T_SLURP0 - 0.4, turn=1.1, look=(0.9, -0.1), mouth="o", open=0.12, tilt=0.12, **KISS_H)
S.set(T_KISS, "sit_bench", "deadpan", dur=0.06, ease="snap", turn=1.1, mouth="kiss", eyes="closed", tilt=0.12, **KISS_H)
S.sfx(T_KISS, "pop", 0.08)
S.set(T_RIGID, "sit_bench", "dead_stare", dur=0.12, ease="snap", turn=0.4, eyescale=1.3, curl_up=1.0, pupil=0.6, look=(0.6, 0.0),
      head=(560, 752), neck=(545, 878), stretch=0.06); S.sfx(T_RIGID, "boing", 0.04)
S.set(T_RIGID + 0.4, "sit_bench", "dead_stare", dur=0.5, turn=0.2, eyescale=1.2, curl_up=0.8, look=(0.0, 0.0), blush=1.0)
# the stork
S.camera(ST_IN0, PX - 330, 880, 0.75, 0.9)
S.set(ST_IN0 + 0.2, "sit_bench", "dead_stare", dur=0.3, look=(-0.8, -0.6), turn=-0.4, blush=0.6); S.sfx(ST_IN0, "whoosh", 0.07, dur=0.8)
S.sfx(ST_IN1, "thud", 0.05)
S.set(T_SIGN0 - 0.25, "sit_sign", "deadpan", dur=0.25, look=(-0.8, 0.4), turn=-0.4, blush=0.3)
def sign_hook(tt, p):
    if T_SIGN0 <= tt < T_SIGN1:
        u = ramp(tt, T_SIGN0, T_SIGN1, "linear"); bx, by = BOARD
        p["lhand"] = (bx - 48 + 130 * u + 10 * math.sin(tt * 40), by + 38 + 12 * math.sin(tt * 30)); p["lhand_t"] = "none"
    return p
S.hook(sign_hook); S.sfx(T_SIGN0, "scribble", 0.06, dur=T_SIGN1 - T_SIGN0)
S.set(T_SIGN1 + 0.05, "sit_hold", "deadpan", dur=0.25, look=(-0.6, -0.6), turn=-0.3)
S.set(T_GOT, "sit_hold", "deadpan", dur=0.08, ease="snap", eyescale=1.2, squash=0.2, look=(0.0, 0.8)); S.sfx(T_GOT, "pat", 0.06)
S.set(T_GOT + 0.2, "sit_hold", "deadpan", dur=0.25, squash=0.0, look=(0.0, 0.8))
S.set(T_SMILE0, "sit_hold", "happy", dur=0.5, mouth="auto", smile=0.7, lid=0.1, look=(0.0, 0.7))
S.camera(ST_UP0 + 0.2, PX, 900, 0.95, 0.8)
# ---- MONTAGE
def montage_music():
    import wave
    SR = 44100; dur = T_SCRATCH - T_MUS; n = int(dur * SR); tt = np.arange(n) / SR
    beat = 60 / 88.0
    chords = [(60, 64, 67), (57, 60, 64), (53, 57, 60), (55, 59, 62)]
    mel = [(0, 76, 1), (1, 79, 1), (2, 77, 0.5), (2.5, 76, 0.5), (3, 74, 1), (4, 72, 1), (5, 76, 1), (6, 74, 2),
           (8, 76, 1), (9, 79, 1), (10, 81, 1), (11, 79, 1), (12, 77, 2)]
    f = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    out = np.zeros(n)
    for ci in range(6):
        ch = chords[ci % 4]; t0 = ci * 2 * beat
        for m in ch:
            a = (tt >= t0) * np.exp(-np.maximum(0, tt - t0) / 1.3)
            ph = 2 * np.pi * f(m) * np.maximum(0, tt - t0); out += 0.16 * a * (np.sin(ph) + 0.25 * np.sin(2 * ph))
    for b0, m, d in mel:
        t0 = b0 * beat
        a = ((tt >= t0) & (tt < t0 + d * beat + 0.25)) * np.exp(-np.maximum(0, tt - t0) / 0.7)
        out += 0.22 * a * np.sin(2 * np.pi * f(m) * np.maximum(0, tt - t0) + 0.004 * np.sin(2 * np.pi * 5 * tt))
    out *= np.minimum(1, tt / 0.3)
    out /= np.abs(out).max() + 1e-9
    with wave.open(os.path.join(HERE, "montage.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 0.9 * 32767).astype(np.int16).tobytes())
montage_music()
S.sfx(T_MUS, os.path.join(HERE, "montage.wav"), 0.07)
S.sfx(T_SCRATCH, "skid", 0.12, dur=0.35); S.sfx(T_SCRATCH + 0.05, "slide_down", 0.04, dur=0.3)
# M1 the house: SOLD
S.cut(M1 - FR, cam=(EX + 150, 880, 0.78), x=EX - 300 - 540)
S.set(M1 - FR, "stand", "happy", dur=0.0, smile=0.6, look=(0.0, 0.0))
S.set(T_SOLD + 0.15, "stand", "happy", dur=0.08, ease="snap", eyescale=1.15, curl_up=0.6, look=(0.9, 0.0), turn=0.4)
S.set(T_SOLD + 0.6, "stand", "happy", dur=0.3, smile=0.8, look=(0.8, 0.1), turn=0.4)
S.sfx(T_SOLD, "thud", 0.1); S.shake(T_SOLD, 0.3, 10)
# M2 slow dance in the kitchen
S.cut(M2 - FR, cam=(IX + 1300, 880, 1.0), x=IX + 1190 - 540)
S.set(M2 - FR, "dance", "happy", dur=0.0, turn=0.8, look=(0.8, 0.0), smile=0.7, lid=0.2, nowalk=1.0)
S.set(M2 + 0.8, "dance", "happy", dur=0.5, turn=0.8, eyes="closed", smile=0.8, nowalk=1.0)
def sway_hook(tt, p):
    if M2 - FR <= tt < M3 - FR:
        s_ = math.sin((tt - M2) * 2 * math.pi * 0.6)
        for k in ("head", "neck", "hip", "lelb", "relb", "lhand", "rhand"): p[k] = (p[k][0] + 22 * s_, p[k][1])
        p["tilt"] = p.get("tilt", 0) + 0.06 * s_
    return p
S.hook(sway_hook)
# M3 the fridge photo (he holds the baby)
S.cut(M3 - FR, cam=(IX + 1380, 880, 0.95), x=IX + 1080 - 540)
S.set(M3 - FR, "hold_front", "happy", dur=0.0, smile=0.6, turn=0.6, look=(0.8, 0.0))
S.set(T_STICK + 0.2, "hold_front", "happy", dur=0.35, smile=0.9, mouth="grin", open=0.2, turn=0.6, look=(0.9, -0.1))
# M4 the couch cuddle
S.cut(M4 - FR, cam=(COUCHX, 900, 1.0), x=SEAT_L - 540)
S.set(M4 - FR, "sit_bench", "happy", dur=0.0, smile=0.75, lid=0.2, look=(0.4, 0.3), turn=0.3)
S.set(M4 + 0.6, "sit_bench", "happy", dur=0.5, smile=0.9, eyes="closed", turn=0.3, tilt=0.1)
S.set(T_SCRATCH, "sit_bench", "dead_stare", dur=0.08, ease="snap", eyescale=1.15, look=(0.0, 0.0))
# ---- D1 video games
S.cut(D1 - FR, cam=(IX + 180, 880, 0.8), x=SEAT_L - 540)
S.set(D1 - FR, "sit_pad", "deadpan", dur=0.0, turn=1.0, look=(1.0, 0.0), lid=0.2, smile=0.15)
def mash(tt, p):
    for a, b in ((D1, D2 - FR), (D3, T_YANK), (T_PAD, T_END)):
        if a <= tt < b:
            k = 1 if not (T_BLOCK1 <= tt < T_STORM0) else 0.3
            for h in ("lhand", "rhand"): p[h] = (p[h][0] + 5 * math.sin(tt * 47 + (h == "lhand")), p[h][1] + 7 * math.sin(tt * 38) * k)
    return p
S.hook(mash)
for k in range(10): S.sfx(D1 + 0.2 + k * 0.33, "tick", 0.02)
S.set(T_STARE + 0.4, "sit_pad", "deadpan", dur=0.3, turn=1.0, look=(1.0, 0.0), lid=0.3)
S.set(T_BLOCK1, "sit_pad", "deadpan", dur=0.25, turn=0.9, look=(0.9, 0.0), lean=0.0, head=(650, 760), neck=(590, 878), tilt=0.25)   # leans around her
S.set(T_STORM1 + 0.1, "sit_pad", "deadpan", dur=0.3, turn=1.0, look=(1.0, 0.0), lid=0.2)
# ---- D2 the sink full of dishes (he adds one more)
S.cut(D2 - FR, cam=(SINKX - 50, 860, 0.85), x=IX + 450 - 540)
S.set(D2 - FR, "plate_carry", "deadpan", dur=0.0, turn=0.5, look=(0.9, 0.0))
S.walk_to(HW0, IX + 1000 - 540, HW1 - HW0)
S.set(T_LOOKP, "plate_carry", "deadpan", dur=0.3, turn=0.4, look=(0.6, -0.9))
S.set(T_LOOKG, "plate_carry", "dead_stare", dur=0.25, turn=0.5, look=(0.9, 0.0))
S.set(T_ADD - 0.25, "plate_up", "deadpan", dur=0.25, turn=0.4, look=(0.6, -0.9))
S.sfx(T_ADD, "clack", 0.05); S.sfx(T_ADD + 0.2, "squeak", 0.02)
S.set(T_ADD + 0.25, "stand", "deadpan", dur=0.25, turn=0.3, look=(0.6, -0.9))
S.set(T_LEAVE - 0.2, "stand", "deadpan", dur=0.2, turn=-0.5, look=(-0.9, 0.0))
S.walk_to(T_LEAVE, IX + 300 - 540, 0.8)
# ---- D3 she vacuums in front of his game
S.cut(D3 - FR, cam=(IX + 180, 880, 0.8), x=SEAT_L - 540)
S.set(D3 - FR, "sit_pad", "deadpan", dur=0.0, turn=1.0, look=(1.0, 0.0), lid=0.2)
for i in range(4):
    tt = VAC0 + 0.3 + i * 0.4
    S.set(tt, "sit_pad", "deadpan", dur=0.15, turn=1.0, look=(1.0, 0.0), lid=0.3 if i < 2 else 0.1, brow=-0.3 * (i > 1),
          head=(560 + 70 * (1 if i % 2 else -1), 760), neck=(545 + 30 * (1 if i % 2 else -1), 878), tilt=0.2 * (1 if i % 2 else -1))
S.sfx(VAC0, "wind", 0.08, dur=T_YANK - VAC0 + 0.1)
S.sfx(T_YANK, "pop", 0.08); S.sfx(T_YANK + 0.05, "slide_down", 0.03, dur=0.3)
S.set(T_YANK + 0.1, "sit_pad", "dead_stare", dur=0.08, ease="snap", turn=1.0, look=(1.0, 0.0), eyescale=1.2, curl_up=0.6)
S.set(T_MAD, "sit_pad", "angry", dur=0.25, turn=0.6, look=(0.9, 0.0), vein=1.0, curl_up=0.0)
# ---- D3B 3 AM: she waits up with the baby; he sneaks in; CLICK
S.cut(D3B - FR, cam=(IX - 340, 900, 0.7), x=DOORX - 540)
S.set(D3B - FR, "sneak", "deadpan", dur=0.0, turn=0.5, look=(0.6, 0.0), show=0.0, nowalk=1.0)
S.set(T_DOOR0 + 0.05, "sneak", "deadpan", dur=0.0, turn=0.5, look=(0.6, 0.0), show=1.0)
S.xkeys.append((SN0, IX - 600 - 540, SN1 - SN0, "linear")); S.x = IX - 600 - 540
for k in range(4): S.sfx(SN0 + 0.15 + k * 0.33, "tiptoe", 0.03)
S.sfx(T_DOOR0, "squeak", 0.03)
S.set(SN1, "sneak", "deadpan", dur=0.2, turn=0.6, look=(0.8, 0.0))
S.sfx(T_LAMP, "tick", 0.08)
S.set(T_LAMP + 0.1, "sneak", "dead_stare", dur=0.08, ease="snap", turn=0.6, look=(0.9, 0.1), eyescale=1.35, curl_up=1.0, pupil=0.55, sneak=0.0)
S.set(T_GRIN, "sneak", "dead_stare", dur=0.3, turn=0.6, look=(0.9, 0.1), mouth="teeth", smile=0.6, eyescale=1.2, sweat=0.8, sneak=0.0)
S.set(D4 - 0.3, "sneak", "dead_stare", dur=0.2, turn=0.6, look=(0.9, 0.1), mouth="teeth", smile=0.6, sweat=1.0, sneak=0.0)
# ---- D4 the argument / D5 we need to talk
S.cut(D4 - FR, cam=(IX + 20, 860, 1.0), x=IX - 230 - 540)
S.set(D4 - FR, "stand", "deadpan", dur=0.0, turn=0.5, look=(0.8, 0.0))
for i, (tt, sz) in enumerate(ARG):
    S.set(tt + 0.1, "stand", "deadpan", dur=0.1, ease="snap", turn=0.5, look=(0.8, -0.1), stretch=-0.06 * (i + 1), lean=-0.03 * (i + 1),
          eyescale=1.0 + 0.05 * i, sweat=0.3 * i)
    S.sfx(tt, "wah", 0.03 + 0.015 * i, dur=0.5)
S.set(T_DOTS - 0.2, "stand", "deadpan", dur=0.3, turn=0.5, look=(0.8, -0.1), sweat=0.6)
S.set(D5 + 0.2, "stand", "deadpan", dur=0.2, turn=0.5, look=(0.8, -0.3), eyescale=1.15, sweat=0.6)
S.set(T_GULP, "stand", "holding_it", dur=0.15, turn=0.3, look=(0.0, 0.0), sweat=1.0, squash=0.15); S.sfx(T_GULP, "gulp", 0.06)
S.set(T_GULP + 0.25, "stand", "holding_it", dur=0.2, look=(0.0, 0.0), sweat=1.0)
# ---- L1 she leaves; L2 she takes the couch
S.cut(L1 - FR, cam=(IX - 520, 900, 0.82), x=IX - 260 - 540)
S.set(L1 - FR, "stand", "dead_stare", dur=0.0, turn=-0.5, look=(-0.8, 0.0))
S.sfx(T_DOOR1 - 0.2, "squeak", 0.02); S.sfx(T_SLAM1, "thud", 0.14); S.shake(T_SLAM1, 0.4, 14)
S.set(T_SLAM1 + 0.05, "stand", "dead_stare", dur=0.08, ease="snap", eyescale=1.15, curl_up=0.6, look=(-0.8, 0.0), turn=-0.5)
S.sfx(T_FRAME + 0.3, "splat", 0.05); S.sfx(T_FRAME + 0.3, "clack", 0.05)
S.set(T_FRAME + 0.5, "stand", "dead_stare", dur=0.3, look=(-0.4, 0.5), turn=-0.3)
S.set(T_FRAME + 1.0, "stand", "dead_stare", dur=0.25, look=(0.0, 0.0), turn=0.0)
S.blink(T_FRAME + 1.4)
S.sfx(T_DOOR2, "squeak", 0.02)
S.set(T_DOOR2 + 0.2, "stand", "dead_stare", dur=0.3, look=(-0.8, 0.0), turn=-0.5)
S.set(T_GRAB + 0.3, "stand", "dead_stare", dur=0.3, look=(-0.9, 0.2), turn=-0.6)
S.sfx(GD0, "skid", 0.05, dur=GD1 - GD0)
S.sfx(T_SLAM2, "thud", 0.12); S.shake(T_SLAM2, 0.35, 10)
# ---- he shrugs and goes back to his game
S.camera(T_SLAM2 + 0.2, IX + 180, 880, 0.8, 0.9)
S.set(T_LOOKTV, "stand", "dead_stare", dur=0.3, look=(1.0, 0.0), turn=0.6)
S.set(T_US3, "stand", "dead_stare", dur=0.25, look=(0.0, 0.0), turn=0.0)
S.set(T_SHRUG, "shrug", "dead_stare", dur=0.25, look=(0.0, 0.0)); S.sfx(T_SHRUG, "boop", 0.03)
S.set(T_SHRUG + 0.55, "stand", "deadpan", dur=0.25, look=(0.9, 0.0), turn=0.5)
S.walk_to(T_WALK, IX + 180 - 540, 0.6)
S.set(T_FLOOR, "sit_floor", "deadpan", dur=0.3, turn=0.9, look=(1.0, -0.2)); S.sfx(T_FLOOR + 0.25, "thud", 0.04)
S.set(T_PAD, "floor_pad", "deadpan", dur=0.25, turn=1.0, look=(1.0, -0.3), smile=0.2, lid=0.2)
for k in range(24): S.sfx(T_PAD + 0.25 + k * 0.38, "tick", 0.018)
S.camera(T_PUSH, TVX, FLOOR_Y - 10 - 600, 1.9, 1.4)
S.flash(T_TEXT, 0.25)
S.sfx(T_TEXT, "boop", 0.05)
S.camera(T_TEXT + 1.0, TVX, FLOOR_Y - 10 - 600, 1.95, 7.0)
S.t = T_END

# ================================================================ HER
G_HAIR, G_DRESS = (0.62, 0.28, 0.16), (0.30, 0.66, 0.66)
GS = 0.92
GXK = [(0.0, PX + 900, 0), (G1A, PX + 900, 0), (G1A, PX - 1150, G1B - G1A, "linear"),
       (G3A, PX + 1250, 0), (G3A, PX + 520, G3B - G3A, "out"), (G3C, GXS, G3D - G3C, "smooth"),
       (M1 - FR, EX + 140, 0.001, "linear"), (M2 - FR, IX + 1410, 0.001, "linear"), (M3 - FR, IX + 1330, 0.001, "linear"),
       (M4 - FR, SEAT_R, 0.001, "linear"),
       (D1 - FR, IX - 1500, 0.001, "linear"), (G_IN0, IX + 120, G_IN1 - G_IN0, "out"), (T_BLOCK0, IX + 520, T_BLOCK1 - T_BLOCK0, "smooth"),
       (T_STORM0, IX - 1500, T_STORM1 - T_STORM0 + 0.6, "inn"),
       (D2 - FR, SINKX + 380, 0.001, "linear"), (D3 - FR, IX + 520, 0.001, "linear"), (VAC0, IX + 820, 0.4, "smooth"), (VAC0 + 0.4, IX + 380, 0.4, "smooth"), (VAC0 + 0.8, IX + 820, 0.4, "smooth"), (VAC0 + 1.2, IX + 380, 0.4, "smooth"), (T_YANK - 0.05, IX + 120, 0.3, "smooth"), (D3B - FR, SEAT_R, 0.001, "linear"), (D4 - FR, IX + 260, 0.001, "linear"),
       (L1 - FR, IX + 60, 0.001, "linear"), (GL0, DOORX, GL1 - GL0, "linear"),
       (GR0 - 0.05, DOORX, 0.001, "linear"), (GR0, COUCHX - 610, GR1 - GR0, "out"), (GD0, DOORX - 1100, GD1 - GD0 + 0.3, "inn")]
GX = Track(GXK)
GW = Track([(0.0, 0.0, 0), (G1A, 1.0, 0.1), (G1B, 0.0, 0.1), (G3A, 1.0, 0.1), (G3B - 0.3, 0.0, 0.3), (G3C, 1.0, 0.1), (G3D - 0.2, 0.0, 0.2),
            (G_IN0, 1.0, 0.1), (G_IN1 - 0.2, 0.0, 0.25), (T_BLOCK0, 1.0, 0.1), (T_BLOCK1 - 0.1, 0.0, 0.1), (T_STORM0, 1.0, 0.1),
            (D2 - FR, 0.0, 0.001), (D3B - FR, 0.0, 0.001), (GL0, 1.0, 0.1), (GL1, 0.0, 0.1), (GR0, 1.0, 0.1), (GR1 - 0.1, 0.0, 0.15), (GD0, 1.0, 0.1), (GD1 + 0.3, 0.0, 0.1)])
GK = [(0.0, L.pose("g_read", "neutral", turn=-0.9, look=(-0.2, 0.85), smile=0.25), 0)]
def gk(t, body, face, dur=0.25, ease="smooth", **kw): GK.append((t, L.pose(body, face, **kw), dur, ease))
gk(G3A, "g_read", "neutral", dur=0.0, turn=-0.9, look=(-0.2, 0.85), smile=0.2)
gk(T_SNIFF - 0.15, "g_read", "neutral", dur=0.2, turn=-0.5, look=(-0.4, 0.3), tilt=-0.08, brow=0.4)
gk(T_SNIFF + 0.25, "stand", "happy", dur=0.2, turn=-0.7, look=(-0.8, 0.5))
gk(G3D - 0.25, "crouch", "happy", dur=0.2, turn=-0.7, look=(-0.8, 0.4))
gk(G3D + 0.05, "g_sit", "happy", dur=0.2, ease="back", turn=-0.7, look=(-0.8, 0.4))
gk(T_NOOD - 0.2, "g_sit", "happy", dur=0.35, turn=-0.9, look=(-0.6, 0.6), mouth="o", open=0.25, smile=0.3, head=(495, 770), neck=(525, 875))
gk(T_SLURP0, "g_sit", "happy", dur=0.35, turn=-1.0, look=(-0.8, 0.0), mouth="o", open=0.2, smile=0.3, head=(495, 770), neck=(525, 875))
gk(T_KISS - 0.05, "g_sit", "happy", dur=T_KISS - T_SLURP0 - 0.4, turn=-1.1, look=(-0.9, -0.1), mouth="o", open=0.12, tilt=-0.12, head=(432, 708), neck=(492, 822))
gk(T_KISS, "g_sit", "happy", dur=0.06, ease="snap", turn=-1.1, mouth="kiss", eyes="closed", tilt=-0.12, head=(432, 708), neck=(492, 822))
gk(T_RIGID + 0.15, "g_sit", "delighted", dur=0.3, turn=-0.7, tilt=0.0, blush=0.5, head=(530, 745), neck=(536, 866))
gk(ST_IN0 + 0.3, "g_sit", "surprised", dur=0.3, turn=-0.6, look=(-0.9, -0.6), open=0.3)
gk(T_GOT + 0.1, "g_sit", "delighted", dur=0.3, turn=-0.8, look=(-0.7, 0.4), smile=0.9)
gk(M1 - FR, "hold_front", "happy", dur=0.0, turn=0.4, look=(0.8, 0.0), smile=0.7)
gk(T_SOLD + 0.2, "hold_front", "delighted", dur=0.15, turn=0.6, look=(0.9, 0.0))
gk(T_SOLD + 0.9, "hold_front", "happy", dur=0.3, turn=-0.7, look=(-0.8, 0.0), smile=0.9)
gk(M2 - FR, "g_dance", "happy", dur=0.0, turn=-0.8, look=(-0.8, 0.0), smile=0.7, lid=0.2)
gk(M2 + 0.6, "g_dance", "happy", dur=0.5, turn=-0.8, eyes="closed", smile=0.8, tilt=-0.1)
gk(M3 - FR, "g_stick", "happy", dur=0.0, turn=0.6, look=(0.8, 0.0), smile=0.7)
gk(T_STICK + 0.25, "stand", "delighted", dur=0.3, turn=-0.6, look=(-0.8, 0.1))
gk(M4 - FR, "g_sit_hold", "happy", dur=0.0, turn=-0.5, eyes="closed", smile=0.7, tilt=-0.26, head=(470, 760), neck=(505, 870))
gk(T_SCRATCH, "g_sit_hold", "surprised", dur=0.08, ease="snap", turn=0.0, look=(0.0, 0.0), tilt=0.0, open=0.2)
gk(D1 - FR, "hold_front", "worried", dur=0.0, turn=0.8, look=(0.8, 0.3))
gk(T_STARE, "hold_front", "annoyed", dur=0.3, turn=-0.8, look=(-0.9, 0.2))
gk(T_STARE + 0.5, "hold_front", "impatient", dur=0.3, turn=-0.8, look=(-0.9, 0.2), tiptoe=1.0, hop=8)
gk(T_STARE + 0.65, "hold_front", "impatient", dur=0.1, turn=-0.8, look=(-0.9, 0.2), hop=0)
gk(T_STARE + 0.8, "hold_front", "impatient", dur=0.1, turn=-0.8, look=(-0.9, 0.2), hop=8)
gk(T_STARE + 0.95, "hold_front", "impatient", dur=0.1, turn=-0.8, look=(-0.9, 0.2), hop=0)
gk(T_BLOCK1 + 0.15, "hold_front", "angry", dur=0.2, turn=-0.8, look=(-0.9, 0.2))
gk(T_LEANA + 0.1, "hold_front", "furious", dur=0.15, turn=-0.9, look=(-0.9, 0.3))
gk(T_STORM0, "hold_front", "furious", dur=0.15, turn=-1.0, look=(-1.0, 0.0))
gk(D2 - FR, "g_point", "annoyed", dur=0.0, turn=-0.7, look=(-0.8, -0.6))
gk(T_LOOKG - 0.1, "g_point", "angry", dur=0.2, turn=-0.8, look=(-0.9, 0.0))
gk(T_ADD + 0.2, "stand", "angry", dur=0.15, ease="snap", turn=-0.6, look=(-0.6, -0.8), eyescale=1.2)
gk(T_STEAM, "arms_crossed", "furious", dur=0.2, turn=-0.7, look=(-0.9, 0.0))
gk(D3 - FR, "g_vac", "annoyed", dur=0.0, turn=0.0, look=(0.6, 0.6), lid=0.4)
gk(T_YANK, "g_vac", "surprised", dur=0.1, turn=0.0, look=(0.6, 0.4), open=0.3)
gk(T_MAD + 0.25, "g_vac", "annoyed", dur=0.2, turn=-0.8, look=(-0.9, 0.0), lid=0.5)
gk(D3B - FR, "g_sit_hold", "angry", dur=0.0, turn=-0.6, look=(-0.9, 0.0))
gk(T_LAMP + 0.3, "g_sit_hold", "angry", dur=0.2, turn=-0.8, look=(-0.9, 0.0), lid=0.4)
gk(T_GRIN + 0.3, "g_sit_hold", "furious", dur=0.3, turn=-0.8, look=(-0.9, 0.0))
gk(D4 - FR, "g_point", "angry", dur=0.0, turn=-0.6, look=(-0.8, 0.0))
for i, (tt, sz) in enumerate(ARG): gk(tt, "g_point", "furious" if i == 2 else "angry", dur=0.1, ease="snap", turn=-0.7, look=(-0.9, 0.0), hop=10 * i)
gk(T_DOTS - 0.3, "stand", "angry", dur=0.3, turn=-0.6, look=(-0.8, 0.0), hop=0)
gk(D5, "arms_crossed", "annoyed", dur=0.3, turn=-0.6, look=(-0.8, 0.0), lid=0.4)
gk(L1 - FR, "g_suit", "annoyed", dur=0.0, turn=-1.0, look=(-1.0, 0.0))
gk(GR0 - 0.05, "stand", "annoyed", dur=0.0, turn=1.0, look=(1.0, 0.0))
gk(GR1, "g_drag", "annoyed", dur=0.25, turn=0.9, look=(0.9, 0.3))
gk(GD0, "g_drag", "annoyed", dur=0.2, turn=-1.0, look=(-1.0, 0.0))
GKT = Track(GK)

def g_base(t):
    p = dict(GKT.at(t))
    x = GX.at(t); ox = x - 540
    for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1])
    wk = GW.at(t)
    v = (GX.at(t + 0.03) - GX.at(t - 0.03)) / 0.06; d = 1 if v > 1 else (-1 if v < -1 else 0)
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
    hop = p.get("hop", 0.0)
    if hop:
        for j in L.JOINTS:
            if j not in ("lfoot", "rfoot"): p[j] = (p[j][0], p[j][1] - hop)
    if M2 - FR <= t < M3 - FR:                                       # the slow dance sway
        s_ = math.sin((t - M2) * 2 * math.pi * 0.6)
        for k in ("head", "neck", "hip", "lelb", "relb", "lhand", "rhand"): p[k] = (p[k][0] + 22 * s_, p[k][1])
    if T_STARE + 0.4 <= t < T_BLOCK0 or L1 <= t < GL0 + 0.3 or G_IN0 <= t < T_STARE:   # bouncing the baby
        b = 10 * abs(math.sin(t * 9))
        for k in ("lhand", "rhand", "lelb", "relb"): p[k] = (p[k][0], p[k][1] - b)
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
    for b in (6.2, 13.6, 21.4, 25.4, 29.8, 36.8, 42.0, 45.9):
        if b <= t < b + 0.16: return math.sin(math.pi * (t - b) / 0.16)
    return 0.0
def g_visible(t):
    if t < G1A: return False
    if G1B <= t < G3A: return False
    if T_STORM1 + 0.6 <= t < D2 - FR: return False
    if GL1 <= t < GR0 - 0.05: return False
    if t >= GD1 + 0.35: return False
    return True
def g_has_baby(t):
    return (M1 - FR <= t < M2 - FR) or (M4 - FR <= t < D2 - FR) or (D3B - FR <= t < D4 - FR) or (L1 - FR <= t < GL1 + 0.1)

def her(cr, t, p, ly):
    if ly != "back" or not g_visible(t): return
    q = g_pose(t)
    clip = (L1 <= t < T_SLAM2 + 0.1)
    if clip: cr.save(); cr.rectangle(DOORX - 200, -9000, 99999, 99999); cr.clip()
    O.draw_mom(cr, t, q, g_blink(t), s=GS, hair=G_HAIR, dress=G_DRESS, bun=False)
    hc = scale_pt(q, ((q["lhand"][0] + q["rhand"][0]) / 2, (q["lhand"][1] + q["rhand"][1]) / 2))
    def grips():
        fx = foot_c(q); cr.save(); cr.translate(fx, FLOOR_Y); cr.scale(GS, GS); cr.translate(-fx, -FLOOR_Y); L.draw_grips(cr, q); cr.restore()
    if t < G3D and q["lhand_t"] == "grip":
        O.draw_book(cr, hc[0], hc[1] - 10, s=0.95); grips()
    if g_has_baby(t):
        if L1 - FR <= t:
            bx, by = scale_pt(q, q["lhand"]); O.draw_baby(cr, bx + 20, by - 20, 0.0, dict(eyes="open", look=(0.8, 0.0)), t, s=0.8)
            sx, sy = scale_pt(q, q["rhand"]); O.draw_suitcase(cr, sx, sy, s=0.85 * GS)
        else:
            cry = D1 - FR <= t < D2 - FR
            O.draw_baby(cr, hc[0] + 10, hc[1] - 15, 0.0, dict(eyes="cry", cry=0.8) if cry else dict(eyes="sleep"), t, s=0.8)
            if cry:
                for i in range(2):
                    u = ((t - D1) * 0.8 + i / 2) % 1.0
                    draw_text(cr, "waah", hc[0] - 40 - 60 * u, hc[1] - 120 - 180 * u, 42 + 18 * u, color=(30, 30, 34), alpha=math.sin(math.pi * u))
        grips()
    if M3 - FR <= t < T_STICK + 0.05:                                    # the photo in her hand
        hx, hy = scale_pt(q, q["rhand"])
        cr.save(); cr.translate(hx + 50, hy); cr.rotate(-0.06)
        O.sketch_rect(cr, -110, -90, 110, 90, 5, sid=19966, fill=(1, 1, 1)); O._photo_fam(cr, 0, 70, 0.55); cr.restore()
    if D3 - FR <= t < D3B - FR:                                          # the vacuum
        hx, hy = scale_pt(q, ((q["lhand"][0] + q["rhand"][0]) / 2, (q["lhand"][1] + q["rhand"][1]) / 2))
        O.draw_vacuum(cr, hx, hy, vac_base(q), FLOOR_Y - 10, on=1.0 if VAC0 <= t < T_YANK + 0.3 else 0.0, t=t)
        grips()
    if clip: cr.restore()
S.prop(her)
for t0, t1 in ((G1A, G1B), (G3A, G3B - 0.3), (G_IN0, G_IN1), (GL0, GL1), (GR0, GR1), (GD0, GD1)):
    for k in range(int((t1 - t0) / 0.31)): S.sfx(t0 + 0.12 + k * 0.31, "step", 0.02)

def vac_base(q):
    return foot_c(q) + 260
def g_head(t):
    q = g_pose(t); return scale_pt(q, q["head"])
def g_mouth(t):
    q = g_pose(t); hx, hy = q["head"]; tn = q.get("turn", 0.0); return scale_pt(q, (hx + 28 * tn, hy + 62))

# ================================================================ props
PLATE_BENCH = (PX, FLOOR_Y - 10 - O.BENCH_SEAT - 2)
BOARD = (SKX + 330 * 1.0, 1000.0)
def props_back(cr, t, p, ly):
    if ly != "back": return
    if T_PLATE + 0.35 <= t < M1 - FR:
        O.draw_spaghetti(cr, PLATE_BENCH[0], PLATE_BENCH[1], s=0.75, t=t, steam=1 - ramp(t, T_KISS, T_KISS + 1.0))
    st = stork_state(t)
    if st:
        O.draw_stork(cr, st["x"], st["y"], s=SKS, t=t, flap=st["flap"], facing=st["facing"], mode=st["mode"], beak=st["beak"],
                     bundle=st["bundle"], cap_tip=st["tip"])
        if st["bundle"]:
            bx, by = O.stork_bundle_pt(st["x"], st["y"], SKS, st["facing"])
            O.draw_baby(cr, bx, by, 0.0, dict(eyes="sleep"), t, s=0.8)
        if st["clip"] > 0.01:
            O.draw_delivery_board(cr, BOARD[0], BOARD[1], s=0.8 * (0.3 + 0.7 * st["clip"]), ang=-0.05, signed=ramp(t, T_SIGN0, T_SIGN1, "linear"))
S.props.insert(0, props_back)
def stork_state(t):
    fl = math.sin(t * 2 * math.pi * 2.6)
    if ST_IN0 <= t < ST_IN1:
        u = ramp(t, ST_IN0, ST_IN1)
        return dict(x=lerp(PX - 2400, SKX, smooth(u)), y=lerp(-200, FLOOR_Y - 560 * SKS, 1 - (1 - u) ** 2), mode="fly" if u < 0.9 else "stand",
                    flap=fl, facing=1, beak=0.0, bundle=True, clip=0.0, tip=0.0)
    if ST_IN1 <= t < ST_UP0:
        clip = smooth(ramp(t, T_CLIP, T_CLIP + 0.25)) * (1 - smooth(ramp(t, T_SIGN1, T_SIGN1 + 0.2)))
        tip = math.sin(math.pi * ramp(t, T_TIP, T_TIP + 0.3)) if t >= T_TIP else 0.0
        return dict(x=SKX, y=FLOOR_Y - 560 * SKS, mode="stand", flap=0.0, facing=1, beak=1.0 if T_DROP <= t < T_DROP + 0.3 else 0.0,
                    bundle=t < T_DROP, clip=clip, tip=tip)
    if ST_UP0 <= t < ST_UP1:
        u = ramp(t, ST_UP0, ST_UP1)
        return dict(x=lerp(SKX, PX - 2200, u ** 1.4), y=lerp(FLOOR_Y - 560 * SKS, -400, smooth(u)), mode="fly", flap=fl, facing=-1, beak=0.0,
                    bundle=False, clip=0.0, tip=0.0)
    return None

def props_front(cr, t, p, ly):
    if ly != "front": return
    hx, hy = p["rhand"]
    if T_POP1 <= t < T_TOSS + 0.05:
        O.draw_rose(cr, hx + 5, hy - 10, s=0.95, ang=0.35, petals=1.0 if t < T_PETAL else 0.0); L.draw_grips(cr, p)
    if T_TOSS + 0.05 <= t < T_TOSS + 0.9:
        u = ramp(t, T_TOSS + 0.05, T_TOSS + 0.9, "linear")
        O.draw_rose(cr, HX0 - 900 * u, 560 - 700 * u + 1100 * u * u, s=0.95, ang=0.35 - 9 * u, petals=0.0)
    if T_PETAL <= t < M1 - FR:
        u = ramp(t, T_PETAL, T_PETAL + 0.9, "linear")
        O.draw_petal(cr, HX0 + 330 + 40 * math.sin(u * 9) * (u < 1), lerp(640, FLOOR_Y - 20, u), ang=1.2 * math.sin(u * 9) * (u < 1))
    if T_POP3 <= t < T_PLATE + 0.35:
        hand = ((p["lhand"][0] + p["rhand"][0]) / 2 + 5, (p["lhand"][1] + p["rhand"][1]) / 2 - 5)
        pp = lerp(hand, PLATE_BENCH, smooth(ramp(t, T_PLATE, T_PLATE + 0.3))) if t >= T_PLATE else hand
        O.draw_spaghetti(cr, pp[0], pp[1], s=0.75, t=t); L.draw_grips(cr, p)
    if T_POP3 + 0.5 <= t < T_SNIFF + 0.2:
        for k in range(3):
            u = ((t - T_POP3) * 0.5 + k / 3) % 1.0
            x0 = PX - 150 + 1000 * u; y0 = 1000 - 120 * u
            sketch_line(cr, [(x0 + 60 * j, y0 + 30 * math.sin(u * 8 + j * 1.3)) for j in range(5)], 6, sid=19390 + k, amp=0.3,
                        color=(1, 1, 1), alpha=0.85 * math.sin(math.pi * u))
    if T_SNIFF - 0.1 <= t < T_SNIFF + 0.4:
        hx2, hy2 = g_head(t)
        draw_text(cr, "sniff", hx2 - 200, hy2 - 30, 42, color=(30, 30, 34), alpha=math.sin(math.pi * ramp(t, T_SNIFF - 0.1, T_SNIFF + 0.4)))
    if T_NOOD <= t < T_KISS:
        a = (p["head"][0] + 28 * p.get("turn", 0), p["head"][1] + 62); b = g_mouth(t)
        u = smooth(ramp(t, T_SLURP0, T_KISS))
        O.draw_noodle(cr, a, b, sag=lerp(PLATE_BENCH[1] - 70 - max(a[1], b[1]), 10, u))
        S_ = None
    if T_KISS <= t < T_KISS + 0.5:
        L.burst_lines(cr, p["head"][0] + 70, p["head"][1] + 40, (t - T_KISS) / 0.5, r0=50, r1=110, n=8, sid=71)
    if T_SIGN0 - 0.1 <= t < T_SIGN1 + 0.05:
        lx, ly_ = p["lhand"]; L.draw_pen(cr, lx, ly_ - 18, ang=-0.3)
    # the baby: falls from the stork into his lap, then with him through M3
    if T_DROP <= t < T_GOT:
        u = ramp(t, T_DROP, T_GOT); a = O.stork_bundle_pt(SKX, FLOOR_Y - 560 * SKS, SKS, 1); b = his_baby(p)
        O.draw_baby(cr, lerp(a[0], b[0], u), lerp(a[1], b[1], u * u) - 120 * math.sin(math.pi * u), 0.3 * u, dict(eyes="sleep"), t, s=0.8)
    if (T_GOT <= t < M1 - FR) or (M3 - FR <= t < M4 - FR):
        b = his_baby(p)
        O.draw_baby(cr, b[0], b[1], 0.0, dict(eyes="open", look=(0.0, -1.0)) if t < M1 else dict(eyes="sleep"), t, s=0.8); L.draw_grips(cr, p)
    # the controller
    if (D1 - FR <= t < D2 - FR) or (D3 - FR <= t < D3B - FR) or t >= T_PAD:
        cx_ = (p["lhand"][0] + p["rhand"][0]) / 2; cy_ = (p["lhand"][1] + p["rhand"][1]) / 2
        O.draw_controller(cr, cx_, cy_ - 5, s=0.8); L.draw_grips(cr, p)
    # the argument bubbles
    if D4 - FR <= t < L1 - FR:
        hx2, hy2 = g_head(t)
        tail = (hx2 - 40, hy2 - 90)
        if t < D5:
            sz = 0.0
            for tt, s_ in ARG:
                if t >= tt: sz = lerp(sz, s_, smooth(ramp(t, tt, tt + 0.15)))
            if sz > 0.01:
                w, h = 240 + 460 * sz, 160 + 240 * sz
                O.draw_bubble(cr, hx2 - 120 - 170 * sz, hy2 - 200 - 100 * sz, w, h, tail, scribble=sz, t=t, angry=True)
            if t >= T_DOTS:
                O.draw_bubble(cr, p["head"][0] - 40, p["head"][1] - 240, 150, 100, (p["head"][0] - 10, p["head"][1] - 130), text="...")
        else:
            O.draw_bubble(cr, hx2 - 260, hy2 - 300, 560, 230, tail, text="WE NEED TO TALK.")
    if T_GULP <= t < T_GULP + 0.4:
        u = (t - T_GULP) / 0.4; hb = (p["head"][0], p["head"][1] + L.HEAD_R)
        L.sketch_circle(cr, *lerp(hb, p["neck"], u), 13, 5, sid=62)
S.prop(props_front)
def his_baby(p):
    return ((p["lhand"][0] + p["rhand"][0]) / 2 + 10, (p["lhand"][1] + p["rhand"][1]) / 2 - 15)

# the slow dance: her hands on his shoulders (drawn by pose); music notes in the montage
def notes(cr, t, p, ly):
    if ly == "front" and T_MUS <= t < T_SCRATCH:
        for k in range(2):
            u = ((t - T_MUS) * 0.6 + k / 2) % 1.0
            O.draw_note(cr, p["head"][0] + 220 + 60 * k, p["head"][1] - 60 - 140 * u, s=0.7, alpha=0.8 * math.sin(math.pi * u), double=k == 1, sid=19340 + k)
    if ly == "front" and T_YANK <= t < T_YANK + 0.3:
        L.burst_lines(cr, OUTLET[0], OUTLET[1], (t - T_YANK) / 0.3, r0=60, r1=120, n=8, sid=81)
    if ly == "front" and D2 - FR <= t < T_ADD + 0.12:                    # his dirty plate
        hx, hy = p["rhand"]; O.draw_plate(cr, hx, hy - 10, s=0.8); L.draw_grips(cr, p)
    if ly == "front" and T_STEAM <= t < D3 - FR:
        hx2, hy2 = g_head(t)
        for k in range(2):
            u = ((t - T_STEAM) * 1.5 + k / 2) % 1.0
            O.draw_smoke_puff(cr, hx2 + (-90 if k else 90) * (1 + u), hy2 - 100 - 120 * u, 30 + 30 * u, alpha=1 - u)
    if ly == "front" and T_SLAM1 <= t < T_SLAM1 + 0.35:
        L.burst_lines(cr, DOORX, FLOOR_Y - 600, (t - T_SLAM1) / 0.35, r0=480, r1=600, n=12, sid=82)
    if ly == "front" and T_SLAM2 <= t < T_SLAM2 + 0.35:
        L.burst_lines(cr, DOORX, FLOOR_Y - 600, (t - T_SLAM2) / 0.35, r0=480, r1=600, n=12, sid=83)
S.prop(notes)

def night(cr, t):
    """3 AM: the room is dark; only her two open eyes show. CLICK - the lamp."""
    if not (D3B - FR <= t < T_LAMP): return
    cr.set_source_rgba(0.04, 0.05, 0.12, 0.86); cr.paint()
    door = door_open3(t)
    q = g_pose(t); hx, hy = scale_pt(q, q["head"])
    z = L.cam_track.at(t)[2]
    for sd in (-1, 1):
        ex, ey = L.world_to_screen(t, (hx + sd * 36 * GS - 20, hy - 10))
        cr.save(); cr.translate(ex, ey); cr.scale(z, z)
        cr.save(); cr.scale(1.0, 1.15); cr.arc(0, 0, 22, 0, 2 * math.pi); cr.restore()
        cr.set_source_rgb(1, 1, 1); cr.fill()
        lk = -1.0 if t > SN0 + 0.3 else -0.3
        cr.arc(11 * lk, 2, 9, 0, 2 * math.pi); cr.set_source_rgb(0.05, 0.05, 0.08); cr.fill()
        cr.move_to(-26, -26 - 6 * sd); cr.line_to(22, -18 + 6 * sd)                 # angry lids
        cr.set_source_rgb(0.04, 0.05, 0.12); cr.set_line_width(14); cr.stroke()
        cr.restore()
S.overlays.insert(0, night)

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
