"""Day 15 - COMMENT episode: @nicolascechettoschuller "Seja feliz" (Instagram, day 14 reel, 0 likes) - Portuguese for
"be happy". The black car drops him at a sunny beach (wavy mosaic sidewalk, a granite dome with a cable car in the bay)
and leaves for good. He can't smile; a finger smile flops; a seagull steals his ice cream; a little rain cloud appears
over his head and follows him; lightning takes the empty cone; he sits in the rain. The cloud's own gust gives him an
idea: a kite. The wind yanks him up through the cloud into the sun - he smiles, grins, laughs, loops. The abandoned
cloud rains itself out -> a rainbow, and the wind dies; he lands on the rainbow and slides down it, laughing, and lands
in the sand. Button: the seagull drops one scoop back on his head; he eats it. Real smile. Ask on the beach. See BEATS.md.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
import character as C
from ltcd import ramp, lerp, FLOOR_Y
from ink import smooth, back_out, sketch_rect, sketch_line, sketch_circle, draw_text
import numpy as np

FR = 1 / 30

# ================================================================ places
SEATX = 260000.0                                   # the back seat (day 14's ending)
BX = 700000.0                                      # the beach: where he stops
CARX = BX - 2300.0                                 # the black car drops him here (door centre = CARX - 140)
PROM_END = BX - 1300.0                              # the mosaic sidewalk ends, the sand starts
WX0, WX1 = BX - 6000.0, BX + 12000.0
SUGAR = BX + 2600.0
OX = BX - 540.0                                    # body offset on the beach
TX = BX - 300.0                                    # take-off point (his centre x)
RBX, RB = TX + 3600.0, 1500.0                      # the rainbow: centre on the ground, outer radius
TH_END = 0.49                                      # where he leaves the rainbow (angle)

# ================================================================ timeline
T_READ = 0.3; T_BRAKE = 1.7
CUT_OUT = 2.4; T_SHUT = 2.8; T_PEEL = 3.1; T_LOOKL = 3.25; T_LOOKUS = 3.7; T_RUN = 4.1; T_ARR = 5.1
T_TRY = 5.6; T_SAG = 7.2; T_FING = 7.9; T_LET = 9.0
T_PULL1 = 9.5; T_POP1 = T_PULL1 + 1.4
T_LOOKC = 11.3; T_SMALL = 11.7; T_LICK = 12.3; T_GULL = 11.9; T_GRAB = 12.6; T_GULLX = 13.5
T_STARE = 13.2; T_US = 14.1
T_CLOUD = 14.8; T_DRIP = 15.2; T_UP = 15.35; T_RAIN = 15.8
T_STEPR = 16.6; T_UP2 = 17.5; T_RUNL = 18.0; T_UP3 = 18.9
T_RUMBLE = 19.5; T_ZAP = 20.2; T_AFTER = 20.8; T_SIT = 21.4
T_GUST = 22.9; T_LOOKG = 23.2; T_IDEA = 23.9; T_STAND = 24.3
T_PULL2 = 24.7; T_POP2 = T_PULL2 + 1.4
T_CATCH = 26.5; T_LIFT = 27.1
A1 = 29.7; C1 = 31.8; LP1 = 33.4; DR1 = 34.1; SL1 = 37.4; T_LAND = 38.0 + 1 / 60
T_RAINOUT0 = 28.6; T_RAINOUT1 = 33.0; T_BOW0 = 32.6; T_BOW1 = 33.8
T_STAND2 = 39.9
T_GULL2 = 40.5; T_DROP = 41.3; T_PLOP = 41.75; T_LOOKUP = 42.05; T_REACH = 42.7; T_TAKE = 43.05; T_EAT = 43.6; T_SMILE = 44.0
T_ASK = 45.3
ASK_HOLD = 10.0

# ================================================================ the flight path (relative to the take-off point)
def fpath(t):
    """(dx, alt, rot) of his body while the kite has him. rot = body rotation (rad, + = clockwise on screen)."""
    if t < T_LIFT: return (0.0, 0.0, 0.0)
    if t < A1:                                                     # yanked up, through the cloud
        u = ramp(t, T_LIFT, A1)
        return (1100 * smooth(u), 1250 * (1 - (1 - u) ** 2), 0.15 * math.sin(math.pi * u))
    if t < C1:                                                     # over the beach and the bay
        v = ramp(t, A1, C1, "linear")
        return (1100 + 1000 * v, 1250 + 80 * math.sin(2 * math.pi * v), 0.06 * math.sin(2 * math.pi * v))
    if t < LP1:                                                    # the loop
        v = ramp(t, C1, LP1, "linear"); a = 2 * math.pi * smooth(v)
        return (2100 + 380 * math.sin(a) + 450 * v, 1250 + 380 * (1 - math.cos(a)), -a)
    top = (RBX - TX, RB)
    if t < DR1:                                                    # the wind dies: drops onto the top of the rainbow
        v = ramp(t, LP1, DR1)
        return (lerp(2550, top[0], smooth(v)), lerp(1250, top[1], smooth(v)) + 220 * math.sin(math.pi * v), 0.0)
    if t < SL1:                                                    # slides down the rainbow
        v = ramp(t, DR1, SL1, "linear")
        th = math.pi / 2 - (math.pi / 2 - TH_END) * v ** 1.7
        return (RBX - TX + RB * math.cos(th), RB * math.sin(th), 0.55 * (math.pi / 2 - th))
    if t < T_LAND:                                                 # off the end, into the sand
        v = ramp(t, SL1, T_LAND, "linear")
        x0, a0 = RBX - TX + RB * math.cos(TH_END), RB * math.sin(TH_END)
        return (x0 + 650 * v, a0 * (1 - v * v) + 120 * math.sin(math.pi * v), 0.55 * (math.pi / 2 - TH_END) * (1 - v))
    return None
DX_LAND = fpath(T_LAND - 1e-4)[0]
LANDX = TX + DX_LAND + 40                                          # his centre after landing
LOX = LANDX - 540.0

def flying(t): return T_LIFT <= t < T_LAND

# ================================================================ scene
S = M.Scene(x0=SEATX - 540)
S.auto_blinks = False
S.floor = False
S.card("nicolascechettoschuller", "Seja feliz", "0", t0=0.3)
SEATCAM = (SEATX, 900, 1.0)
S.camkeys[0] = (0.0, SEATCAM, 0); S.cam = SEATCAM

# ---------------------------------------------------------------- the back seat (morning: palms stream past)
def seat(cr, t):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    cr.rectangle(vx0, vy0, vx1 - vx0, vy1 - vy0); cr.set_source_rgb(0.10, 0.10, 0.13); cr.fill()
    wx0, wy0, wx1, wy1 = SEATX - 430, 330, SEATX + 430, 960
    cr.save(); cr.rectangle(wx0, wy0, wx1 - wx0, wy1 - wy0); cr.clip()
    cr.rectangle(wx0, wy0, wx1 - wx0, wy1 - wy0); cr.set_source_rgb(*O.BEACH_SKY[0]); cr.fill()
    cr.rectangle(wx0, wy1 - 220, wx1 - wx0, 120); cr.set_source_rgb(*O.SEA); cr.fill()
    cr.rectangle(wx0, wy1 - 100, wx1 - wx0, 100); cr.set_source_rgb(*O.SAND); cr.fill()
    sp = 1500 * (1 - smooth(ramp(t, T_BRAKE, T_BRAKE + 0.5)))
    pos = 1500 * min(t, T_BRAKE) + 1500 * 0.25 * max(0, min(t, T_BRAKE + 0.5) - T_BRAKE)
    for k in range(4):
        xx = wx1 + 300 - ((pos + k * 420) % 1700)
        cr.save(); cr.translate(xx, wy1); cr.scale(0.45, 0.45); cr.translate(-xx, -FLOOR_Y)
        O.draw_palm(cr, xx, t, h=900, yb=FLOOR_Y, sid=k)
        cr.restore()
    cr.restore()
    sketch_rect(cr, wx0, wy0, wx1, wy1, 7, sid=18610, fill=None)
    sketch_line(cr, [(wx0 + 60, wy0 + 40), (wx0 + 200, wy0 + 200)], 8, sid=18611, color=(1, 1, 1), alpha=0.25)
    sketch_rect(cr, SEATX - 760, 900, SEATX + 760, FLOOR_Y + 300, 7, sid=18612, fill=(0.18, 0.16, 0.16))
    for k in (-1, 0, 1): sketch_line(cr, [(SEATX + k * 500, 940), (SEATX + k * 500, 1300)], 4, sid=18613, color=(0.10, 0.09, 0.09))
    for k in range(4):
        cr.arc(SEATX - 600 + 400 * k, 230, 10, 0, 2 * math.pi); cr.set_source_rgb(0.75, 0.80, 1.0); cr.fill()

def seat_front(cr, t, p, ly):
    if ly != "front" or t >= CUT_OUT - FR: return
    sketch_rect(cr, SEATX - 900, 1370, SEATX + 900, FLOOR_Y + 600, 7, sid=18620, fill=(0.12, 0.11, 0.11))
    for d in (-1, 1):
        sketch_rect(cr, SEATX + d * 420 - 260, 1300, SEATX + d * 420 + 260, FLOOR_Y + 600, 7, sid=18621 + (d > 0), fill=(0.20, 0.18, 0.18))
S.prop(seat_front)

# ---------------------------------------------------------------- the rain cloud
_CX_T = np.array([0.0, T_STEPR, T_STEPR + 0.6, T_RUNL, T_RUNL + 0.55, 200.0])
_CX_X = np.array([BX, BX, BX + 300, BX + 300, TX, TX])
def cloud_x(t):
    return float(np.mean([np.interp(t - 0.4 + k * 0.06, _CX_T, _CX_X) for k in range(-4, 5)]))
def cloud_state(t):
    """(x, y, scale, dark, rain amount) or None."""
    if t < T_CLOUD: return None
    s = 0.55 * back_out(min(1.0, (t - T_CLOUD) / 0.3), 1.8) + 0.45 * smooth(ramp(t, T_CLOUD + 0.5, T_RUMBLE))
    dark = 0.35 + 0.5 * smooth(ramp(t, T_CLOUD + 0.5, T_RUMBLE))
    gust = trap(t, T_GUST - 0.1, T_GUST + 0.3, T_LIFT + 0.5)
    s *= 1 + 0.12 * gust * (0.5 + 0.5 * math.sin(t * 9))
    out = smooth(ramp(t, T_RAINOUT0, T_RAINOUT1))
    s *= 1 - out; dark = lerp(dark, 0.1, out)
    if s < 0.03: return None
    rain = smooth(ramp(t, T_RAIN - 0.1, T_RAIN + 0.3)) * (1 - out) ** 0.5
    return (cloud_x(t), 330 + 8 * math.sin(t * 2), s, dark, rain)

def trap(t, a, b, c): return smooth(ramp(t, a, b)) * (1 - smooth(ramp(t, b, c)))

def gust_amt(t): return trap(t, T_GUST - 0.1, T_GUST + 0.4, T_LIFT + 2.5) if t < 34 else 0.0

# ---------------------------------------------------------------- world
def beach(cr, t):
    O.draw_beach_world(cr, t, WX0, WX1, PROM_END, wind=gust_amt(t), sugar_x=SUGAR)
    if t < T_PEEL + 1.5:                                        # the black car: door shuts, it reverses away for good
        dr = 1.0 - smooth(ramp(t, T_SHUT, T_SHUT + 0.2))
        dx = 0.0 if t < T_PEEL else -2600 * (t - T_PEEL) ** 2
        O.draw_limo(cr, CARX + dx, FLOOR_Y, door=dr, spin=dx / 120)
        if t >= T_PEEL:
            for k in range(4):
                u = (t - T_PEEL) - k * 0.12
                if 0 < u < 1.0:
                    O.draw_smoke_puff(cr, CARX + 1000 + dx * 0.3 - 200 * u + 100 * k, FLOOR_Y - 100 - 140 * u, 100 + 160 * u, alpha=0.7 * (1 - u))
    # the rainbow (rain + sun, once the cloud has rained itself out)
    sw = smooth(ramp(t, T_BOW0, T_BOW1))
    O.draw_rainbow(cr, RBX, FLOOR_Y, RB + 30, band=60, sweep=sw)
    # the kite lying on the sand (end)
    ks = kite_state(t)
    if ks and ks[-1] == "sand": O.draw_kite(cr, ks[0], ks[1], s=0.8, ang=ks[2], t=0.0, tail=0.0)

def world(cr, t):
    if t < CUT_OUT - FR: seat(cr, t)
    else: beach(cr, t)
S.background(world)

def cloud_layer(cr, t, p, ly):
    cs = cloud_state(t)
    if cs is None: return
    x, y, s, dark, rain = cs
    through = T_LIFT + 0.15 <= t < T_LIFT + 0.55
    if ly == "back" and not through:
        O.draw_rain_cloud(cr, x, y, s, dark)
    if ly == "front":
        if rain > 0.02:
            cr.save(); cr.rectangle(x - 400, y, 800, FLOOR_Y - y); cr.clip()
            O.draw_cloud_rain(cr, t, x, y + 60 * s, FLOOR_Y, 230 * s, amt=rain)
            cr.restore()
        if through: O.draw_rain_cloud(cr, x, y, s, dark)
        fl = trap(t, T_RUMBLE, T_RUMBLE + 0.08, T_RUMBLE + 0.35) + trap(t, T_ZAP - 0.05, T_ZAP, T_ZAP + 0.3)
        if fl > 0.02: O.draw_rain_cloud(cr, x, y, s * 1.02, 0.0, alpha=0.8 * fl)
        if T_DRIP <= t < T_DRIP + 0.25:                          # the first drip lands on his head
            hx, hy = p["head"]; u = (t - T_DRIP) / 0.25
            O.draw_droplet(cr, hx + 10, lerp(y + 80, hy - 120, u), 14, color=(0.55, 0.75, 0.95))
        if T_ZAP <= t < T_ZAP + 0.22:                             # ZAP
            hx, hy = p["rhand"]
            O.draw_bolt(cr, x - 20, y + 70 * s, hx, hy - 110)
        if T_LIFT + 0.5 <= t < T_LIFT + 0.9:                      # punched out through the top of it
            L.burst_lines(cr, x, y - 80, (t - T_LIFT - 0.5) / 0.4, r0=160, r1=260, n=10, sid=77)
S.prop(cloud_layer)

# wind streaks during the gust (screen space would fight the card; draw in world space around him)
def wind_layer(cr, t, p, ly):
    g = gust_amt(t)
    if ly != "front" or g < 0.05: return
    hx = p["hip"][0]
    for k in range(7):
        u = ((t * 1.6) + k * 0.37) % 1.0
        xx = hx + 900 - 1900 * u; yy = 500 + 140 * k + 30 * math.sin(t * 3 + k)
        cr.move_to(xx, yy); cr.curve_to(xx - 80, yy - 20, xx - 160, yy + 20, xx - 260, yy)
        cr.set_source_rgba(1, 1, 1, 0.85 * g); cr.set_line_width(10); cr.stroke()
        cr.move_to(xx, yy); cr.curve_to(xx - 80, yy - 20, xx - 160, yy + 20, xx - 260, yy)
        cr.set_source_rgba(0.1, 0.1, 0.12, 0.35 * g); cr.set_line_width(3); cr.stroke()
S.prop(wind_layer)

# ================================================================ HIM
def dig_pull(t0, hold_pose, look=(0.4, -0.2)):
    """the signature gag, quick: eyes down, hand digs around at his hip (no pocket), POP - it's in his hand."""
    POCK = (588 + S.x, 1092)
    S.set(t0, "stand", "deadpan", dur=0.35, look=(0.35, 0.9), tilt=0.05)
    def hk(tt, p):
        if t0 + 0.25 <= tt < t0 + 1.35:
            u = ramp(tt, t0 + 0.25, t0 + 0.5)
            dig = ramp(tt, t0 + 0.5, t0 + 0.6) * (1 - ramp(tt, t0 + 1.2, t0 + 1.3))
            p["rhand"] = lerp(p["rhand"], (POCK[0] + 14 * math.sin(tt * 24) * dig, POCK[1] + 6 * math.sin(tt * 31) * dig), u)
        return p
    S.hook(hk)
    S.sfx(t0 + 0.55, "rummage", 0.04, dur=0.6)
    S.set(t0 + 1.35, hold_pose, "deadpan", dur=0.2, ease="back", look=look)
    S.sfx(t0 + 1.4, "pop", 0.1)
    def pr(cr, tt, p, ly):
        if ly == "front" and t0 + 1.4 <= tt < t0 + 1.7:
            L.burst_lines(cr, p["rhand"][0], p["rhand"][1] - 80, (tt - t0 - 1.4) / 0.4, r0=90, r1=160, n=10, sid=9)
    S.prop(pr)
    return t0 + 1.4

# ---- the back seat: reads it; the car brakes
S.set(0.0, "stand", "deadpan", dur=0.0, nowalk=1.0)
S.read_card(T_READ, react="deadpan", lines=1, dur=1.1, face="deadpan")
S.set(T_BRAKE, "stand", "deadpan", dur=0.08, ease="snap", lean=0.16, eyescale=1.2, look=(0.0, 0.0), curl_up=1.0, nowalk=1.0)
S.set(T_BRAKE + 0.35, "stand", "dead_stare", dur=0.3, lean=0.0, nowalk=1.0)
S.shake(T_BRAKE, 0.5, 18); S.sfx(T_BRAKE, "skid", 0.08, dur=0.6)
# ---- outside: out of the car; it leaves; he runs right onto the beach
S.cut(CUT_OUT - FR, cam=(CARX + 250, 1000, 0.55), x=CARX - 140 - 540)
S.set(CUT_OUT - FR, "stand", "deadpan", dur=0.0, look=(0.0, 0.0))
S.sfx(T_SHUT, "thud", 0.1)
S.set(T_LOOKL, "stand", "deadpan", dur=0.25, look=(-0.9, 0.0), turn=-0.5)
S.sfx(T_PEEL, "skid", 0.07, dur=0.7); S.sfx(T_PEEL + 0.1, "whoosh", 0.07, dur=0.6)
S.set(T_LOOKUS, "stand", "dead_stare", dur=0.25, look=(0.0, 0.0), turn=0.0)
S.set(T_RUN, "stand", "deadpan", dur=0.15, run=1.0, look=(0.9, 0.0), turn=0.5, lean=0.12)
S.xkeys.append((T_RUN, OX, T_ARR - T_RUN, "inn")); S.x = OX
S.camera(T_RUN, BX - 150, 880, 0.9, 1.1)
S.sfx(T_RUN, "whoosh", 0.04)
S.set(T_ARR - 0.1, "stand", "deadpan", dur=0.12, ease="snap", stretch=-0.25, look=(0.3, 0.0))
S.set(T_ARR + 0.1, "stand", "deadpan", dur=0.3, ease="back", look=(0.0, 0.0))
S.sfx(T_ARR - 0.1, "skid", 0.05, dur=0.35)
# ---- tries to smile. it doesn't stay.
S.camera(T_ARR, BX, 840, 1.05, 1.2)
S.set(T_TRY, "stand", "deadpan", dur=1.4, mouth="auto", smile=0.55, twitch=0.7, quiver=0.6, look=(0.0, 0.0))
S.set(T_SAG, "stand", "deadpan", dur=0.35, mouth="auto", smile=-0.25, look=(0.0, 0.1))
S.sfx(T_SAG, "slide_down", 0.025, dur=0.4)
L.POSES["finger_smile"] = dict(lelb=(415, 800), lhand=(492, 692), relb=(665, 800), rhand=(588, 692), lhand_t="point", rhand_t="point", lhand_front=1.0, rhand_front=1.0)
S.set(T_FING, "finger_smile", "deadpan", dur=0.3, mouth="grin", smile=1.0, open=0.15, look=(0.0, 0.0))
S.set(T_FING + 0.6, "finger_smile", "deadpan", dur=0.3, mouth="grin", smile=1.0, open=0.15, look=(0.0, 0.0), twitch=0.5)
S.set(T_LET, "stand", "deadpan", dur=0.15, ease="snap", mouth="auto", smile=-0.2)
S.sfx(T_LET + 0.05, "boing", 0.035)
S.camera(T_LET + 0.1, BX, 860, 0.92, 0.8)
# ---- an ice cream
L.POSES["hold_cone"] = dict(relb=(650, 960), rhand=(690, 860), rhand_t="grip")
dig_pull(T_PULL1, "hold_cone")
S.set(T_LOOKC, "hold_cone", "deadpan", dur=0.3, look=(0.7, -0.6), turn=0.2)
S.set(T_SMALL, "hold_cone", "deadpan", dur=0.6, mouth="auto", smile=0.35, lid=0.25, look=(0.7, -0.6), turn=0.2)
L.POSES["lick"] = dict(relb=(660, 880), rhand=(610, 780), rhand_t="grip")
S.set(T_LICK, "lick", "deadpan", dur=0.3, mouth="blep", lid=0.3, look=(0.4, -0.4), turn=0.1)
S.set(T_GRAB + 0.15, "lick", "deadpan", dur=0.08, ease="snap", mouth="blep", eyescale=1.25, curl_up=1.0, look=(0.4, -0.4))
S.sfx(T_GRAB, "whoosh", 0.07, dur=0.4); S.sfx(T_GRAB + 0.05, "squeak", 0.04)
S.set(T_STARE, "hold_cone", "dead_stare", dur=0.4, look=(0.6, -0.5), turn=0.2)
S.set(T_STARE + 0.5, "hold_cone", "dead_stare", dur=0.3, look=(-0.9, -0.6), turn=-0.3)       # the gull, gone
S.set(T_US, "hold_cone", "dead_stare", dur=0.3, look=(0.0, 0.0))
S.blink(T_US + 0.4)
# ---- the rain cloud
S.sfx(T_CLOUD, "pop", 0.06); S.sfx(T_DRIP + 0.25, "drip", 0.06)
S.set(T_UP, "hold_cone", "deadpan", dur=0.35, look=(0.0, -1.0), tilt=-0.05)
S.sfx(T_RAIN, "rain", 0.035, dur=T_LIFT - T_RAIN + 1.5)
S.set(T_UP + 1.0, "hold_cone", "resigned", dur=0.3, look=(0.0, 0.0))
S.camera(T_CLOUD, BX, 880, 0.85, 1.0)
S.walk_to(T_STEPR, OX + 300, 0.6)
S.set(T_UP2, "hold_cone", "deadpan", dur=0.3, look=(-0.3, -1.0))
S.set(T_RUNL, "hold_cone", "deadpan", dur=0.12, run=1.0, look=(-0.9, 0.0), turn=-0.5, lean=-0.12)
S.xkeys.append((T_RUNL, TX - 540, 0.55, "linear")); S.x = TX - 540
S.set(T_RUNL + 0.6, "hold_cone", "deadpan", dur=0.25, ease="back", look=(0.0, 0.0))
S.set(T_UP3, "hold_cone", "holding_it", dur=0.35, look=(0.2, -1.0))
S.camera(T_RUNL, BX - 150, 880, 0.85, 0.8)
S.sfx(T_RUMBLE, "kaboom", 0.09, dur=1.4); S.shake(T_RUMBLE, 0.4, 6)
S.set(T_RUMBLE + 0.3, "hold_cone", "holding_it", dur=0.2, look=(0.2, -1.0), sweat=0.4)
S.flash(T_ZAP, 0.3); S.shake(T_ZAP, 0.4, 12)
S.sfx(T_ZAP, "kaboom", 0.16, dur=0.9); S.sfx(T_ZAP + 0.05, "poof", 0.06)
S.set(T_ZAP + 0.05, "hold_cone", "deadpan", dur=0.06, ease="snap", eyescale=1.3, curl_up=1.0, pupil=0.6, look=(0.0, 0.0))
S.set(T_AFTER, "stand", "resigned", dur=0.4, look=(0.5, 0.4))
S.set(T_SIT - 0.1, "sit_floor", "resigned", dur=0.35, look=(0.0, 0.3), nowalk=1.0)
S.sfx(T_SIT + 0.2, "thud", 0.05)
S.camera(T_SIT, TX, 870, 0.88, 1.2)
S.set(T_SIT + 0.9, "sit_floor", "resigned", dur=0.5, look=(0.0, 0.0), lid=0.6, nowalk=1.0)
# ---- the gust; an idea; a kite
S.sfx(T_GUST, "wind", 0.08, dur=T_LIFT - T_GUST + 2.0)
S.set(T_LOOKG, "sit_floor", "deadpan", dur=0.35, look=(0.0, -1.0), nowalk=1.0)
S.set(T_IDEA, "sit_floor", "deadpan", dur=0.25, ease="back", look=(0.0, 0.0), brow=0.7, eyescale=1.12, lid=0.1, nowalk=1.0)
S.set(T_STAND, "stand", "deadpan", dur=0.35, look=(0.0, 0.0), lid=0.2)
S.camera(T_STAND, TX + 60, 800, 0.8, 1.0)
L.POSES["kite_up"] = dict(relb=(660, 720), rhand=(700, 580), rhand_t="grip")
dig_pull(T_PULL2, "kite_up", look=(0.5, -0.8))
S.set(T_CATCH, "kite_up", "deadpan", dur=0.2, look=(0.6, -1.0), turn=0.3, lean=0.05)
S.sfx(T_CATCH, "whoosh", 0.06, dur=0.5)
# ---- the kite has him
L.POSES["hang"] = dict(relb=(600, 520), rhand=(605, 395), rhand_t="grip", lelb=(445, 900), lhand=(380, 990), lhand_t="open",
                       lknee=(515, 1300), lfoot=(500, 1445), rknee=(572, 1290), rfoot=(600, 1430), lfoot_dir=-0.2, rfoot_dir=0.3)
S.set(T_LIFT, "hang", "deadpan", dur=0.08, ease="snap", eyescale=1.3, mouth="o", open=0.3, curl_up=1.0, look=(0.5, -0.8), nowalk=1.0, lag=0.25)
S.sfx(T_LIFT, "boing", 0.05); S.sfx(T_LIFT + 0.1, "whoosh", 0.08, dur=0.8)
S.set(T_LIFT + 0.3, "hang", "deadpan", dur=0.2, eyes="closed", mouth="flat", nowalk=1.0, lag=0.25)            # through the cloud
S.sfx(T_LIFT + 0.5, "poof", 0.05)
S.set(T_LIFT + 0.75, "hang", "deadpan", dur=0.3, eyescale=1.15, look=(0.0, 0.6), nowalk=1.0, lag=0.25)         # sun. no rain.
S.set(T_LIFT + 1.6, "hang", "deadpan", dur=0.6, mouth="auto", smile=0.45, lid=0.15, look=(0.5, 0.4), nowalk=1.0, lag=0.25)
S.set(A1 - 0.2, "hang", "happy", dur=0.5, mouth="grin", smile=0.9, open=0.4, look=(0.3, 0.2), nowalk=1.0, lag=0.25)
S.set(A1 + 0.9, "hang", "laughing", dur=0.4, nowalk=1.0, lag=0.25)
S.sfx(C1 + 0.2, "slide_up", 0.04, dur=0.7); S.sfx(C1 + 0.9, "slide_down", 0.04, dur=0.7)
L.POSES["slide"] = dict(L.POSES["sit_floor"], lelb=(442, 1000), lhand=(400, 860), relb=(638, 1000), rhand=(680, 860), lhand_t="open", rhand_t="open")
S.set(DR1 - 0.25, "slide", "laughing", dur=0.25, nowalk=1.0, lag=0.25)
S.sfx(DR1, "thud", 0.05); S.sfx(DR1 + 0.1, "slide_down", 0.05, dur=SL1 - DR1)
S.sfx(T_BOW0 + 0.2, "twinkle", 0.05)
S.set(SL1 - 0.1, "slide", "laughing", dur=0.2, nowalk=1.0, lag=0.25, curl_up=1.0)
# ---- lands in the sand
S.xkeys.append((T_LAND, LOX, 0.001, "linear")); S.x = LOX
S.set(T_LAND - 0.05, "sit_floor", "laughing", dur=0.1, ease="snap", nowalk=1.0, stretch=-0.2)
S.set(T_LAND + 0.15, "sit_floor", "laughing", dur=0.3, ease="back", nowalk=1.0)
S.sfx(T_LAND, "thud", 0.12); S.shake(T_LAND, 0.35, 10)
S.set(T_LAND + 1.0, "sit_floor", "happy", dur=0.5, mouth="grin", smile=0.9, open=0.3, breath_rate=2.2, nowalk=1.0)
S.set(T_STAND2, "stand", "happy", dur=0.4, smile=0.7, look=(0.0, 0.0))
# ---- the seagull pays him back
S.set(T_GULL2 + 0.3, "stand", "happy", dur=0.3, smile=0.7, look=(0.7, -0.9), turn=0.2)
S.sfx(T_GULL2 + 0.2, "whoosh", 0.04, dur=0.5)
S.set(T_PLOP + 0.05, "stand", "deadpan", dur=0.08, ease="snap", stretch=-0.15, mouth="auto", smile=0.5, look=(0.0, 0.0))
S.set(T_PLOP + 0.25, "stand", "deadpan", dur=0.25, ease="back", mouth="auto", smile=0.5, look=(0.0, 0.0))
S.sfx(T_PLOP, "splat", 0.05)
S.set(T_LOOKUP, "stand", "deadpan", dur=0.3, mouth="auto", smile=0.5, look=(0.0, -1.0))
L.POSES["reach_top"] = dict(relb=(690, 640), rhand=(590, 495), rhand_t="grab")
S.set(T_REACH, "reach_top", "deadpan", dur=0.3, mouth="auto", smile=0.5, look=(0.1, -1.0))
L.POSES["eat"] = dict(relb=(650, 900), rhand=(590, 730), rhand_t="fist")
S.set(T_TAKE + 0.1, "eat", "deadpan", dur=0.35, mouth="auto", smile=0.5, look=(0.2, 0.5))
for k in range(2): S.sfx(T_EAT + 0.05 + 0.25 * k, "chomp", 0.04)
S.set(T_EAT + 0.1, "stand", "deadpan", dur=0.3, mouth="auto", smile=0.3, look=(0.0, 0.0))
S.set(T_SMILE, "stand", "happy", dur=0.5, eyes="happy", smile=0.8, look=(0.0, 0.0))
S.set(T_SMILE + 0.9, "stand", "happy", dur=0.4, smile=0.55, look=(0.0, 0.0))
S.camera(T_STAND2, LANDX + 60, 860, 0.9, 1.0)
S.camera(T_LOOKUP, LANDX, 840, 1.0, 1.2)
S.t = T_ASK
S.the_ask(T_ASK, hold=ASK_HOLD, keep=dict(mouth="auto", smile=0.45))

# ================================================================ flight: hook + camera
def flight_hook(t, p):
    fp = fpath(t) if flying(t) else None
    if fp is None: return p
    dx, alt, rot = fp
    px, py = p["hip"]
    c, s_ = math.cos(rot), math.sin(rot)
    for j in C.JOINTS:
        x, y = p[j][0] - px, p[j][1] - py
        p[j] = (px + x * c - y * s_ + dx, py + x * s_ + y * c - alt)
    p["tilt"] = p.get("tilt", 0.0) + rot
    return p
S.hook(flight_hook)

def him_hip(t):
    fp = fpath(t) if flying(t) else (0.0, 0.0, 0.0)
    return (TX + fp[0], 1118 - fp[1])

def cam_target(t):
    hx, hy = him_hip(t)
    if t < A1:
        u = smooth(ramp(t, T_LIFT - 0.1, T_LIFT + 0.5))
        return (lerp(TX + 60, hx + 120, u), lerp(800, hy - 200, u), lerp(0.8, 0.55, smooth(ramp(t, T_LIFT, A1))))
    if t < C1: return (hx + 120, hy - 200, 0.55)
    if t < LP1: return (TX + 2350, 1118 - 1250 - 300, 0.5)
    if t < DR1:
        u = smooth(ramp(t, LP1, DR1)); return (lerp(TX + 2350, hx + 150, u), lerp(1118 - 1550, hy - 200, u), 0.52)
    return (hx + 150, hy - 200, 0.55)
_ct = np.arange(T_LIFT, T_LAND - 0.03, 0.1)
_cv = np.array([cam_target(x) for x in _ct])
for i, tt in enumerate(_ct):
    lo, hi = max(0, i - 1), min(len(_ct), i + 2)
    cx, cy, z = _cv[lo:hi].mean(axis=0)
    S.camkeys.append((float(tt), (float(cx), float(cy), float(z)), 0.1, "linear"))
S.camkeys.append((T_LAND + 0.05, (LANDX + 80, 880, 0.75), 0.6, "smooth"))
S.camkeys.sort(key=lambda k: k[0])

# ================================================================ props he holds
def cone_layer(cr, t, p, ly):
    if ly != "front" or not (T_POP1 <= t < T_ZAP): return
    hx, hy = p["rhand"]
    if t < T_GRAB: O.draw_cone(cr, hx, hy - 40, 0.85)
    else: O.draw_empty_cone(cr, hx, hy - 40, 0.85)
    L.draw_grips(cr, p)
S.prop(cone_layer)

def zap_puff(cr, t, p, ly):
    if ly == "front" and T_ZAP <= t < T_ZAP + 0.6:
        u = (t - T_ZAP) / 0.6
        O.draw_smoke_puff(cr, 690 + TX - 540 + 0, 820 - 120 * u, 70 + 90 * u, alpha=1 - u, dark=0.5)
S.prop(zap_puff)

def kite_state(t):
    """(x, y, ang, mode)"""
    if t < T_POP2: return None
    if t < T_CATCH: return None                                     # held: drawn in kite_layer from the hand
    if t < T_LIFT: return ("catch",)
    if t < DR1 + 0.05: return ("fly",)
    # released: drifts down to the sand next to where he lands
    p0 = kite_free_start()
    u = ramp(t, DR1 + 0.05, T_LAND + 1.6)
    if u >= 1.0: return (LANDX + 330, FLOOR_Y - 30, 1.35, "sand")
    x = lerp(p0[0], LANDX + 330, smooth(u)) + 120 * math.sin(u * 9)
    y = lerp(p0[1], FLOOR_Y - 30, u ** 1.3)
    return (x, y, 0.4 * math.sin(u * 9) + 1.35 * smooth(ramp(u, 0.8, 1.0)), "drift")

def kite_fly_pos(t, hand):
    fp = fpath(t) if flying(t) else (0, 0, 0)
    rot = fp[2]
    ox_, oy_ = 290, -160
    c, s_ = math.cos(rot), math.sin(rot)
    return (hand[0] + ox_ * c - oy_ * s_ + 30 * math.sin(t * 5), hand[1] + ox_ * s_ + oy_ * c + 25 * math.sin(t * 7)), rot + 0.35 + 0.12 * math.sin(t * 4)

_KFS = []
def kite_free_start():
    if not _KFS:
        hp = L.pose_with_follow(DR1 + 0.05)
        _KFS.append(kite_fly_pos(DR1 + 0.05, hp["rhand"])[0])
    return _KFS[0]

def kite_layer(cr, t, p, ly):
    if t < T_POP2: return
    if ly == "back":
        ks = kite_state(t)
        if ks and ks[-1] == "drift": O.draw_kite(cr, ks[0], ks[1], s=0.8, ang=ks[2], t=t, tail=0.5)
        return
    hx, hy = p["rhand"]
    if t < T_CATCH:
        O.draw_kite(cr, hx + 20, hy - 140, s=0.8, ang=0.15 + 0.05 * math.sin(t * 6), t=t, tail=0.4)
        L.draw_grips(cr, p); return
    ks = kite_state(t)
    if ks[0] == "catch":
        u = smooth(ramp(t, T_CATCH, T_LIFT - 0.1))
        (kx, ky), ka = kite_fly_pos(t, (hx, hy))
        kx, ky = lerp((hx + 20, hy - 140), (kx, ky), u)
        sketch_line(cr, [(hx, hy - 10), (kx, ky + 40)], 3, sid=15300, amp=0.2)
        O.draw_kite(cr, kx, ky, s=0.8, ang=lerp(0.15, ka, u), t=t, tail=1.0)
        L.draw_grips(cr, p); return
    if ks[0] == "fly":
        (kx, ky), ka = kite_fly_pos(t, (hx, hy))
        sketch_line(cr, [(hx, hy - 10), (kx, ky + 40)], 3, sid=15300, amp=0.2)
        O.draw_kite(cr, kx, ky, s=0.8, ang=ka, t=t, tail=1.0)
        L.draw_grips(cr, p); return
S.prop(kite_layer)

# ================================================================ the seagull
def gull_state(t):
    """(x, y, facing, carry) or None"""
    if T_GULL <= t < T_GULLX:                                       # the theft
        hx = BX + 70 + 150; hy = 790
        a, b, c = (BX + 1500, 250), (BX + 400, 900), (BX - 1700, 150)
        if t < T_GRAB:
            u = ramp(t, T_GULL, T_GRAB); q = lerp(a, (hx, hy - 150), smooth(u))
            return (q[0], q[1] - 120 * math.sin(math.pi * u) * 0, -1, 0)
        u = ramp(t, T_GRAB, T_GULLX)
        q = lerp((hx, hy - 150), c, u ** 1.3)
        return (q[0], q[1], -1, 3)
    if T_GULL2 <= t < T_DROP + 1.4:                                 # the payback
        if t < T_DROP:
            u = smooth(ramp(t, T_GULL2, T_DROP)); q = lerp((LANDX + 1500, 150), (LANDX + 60, 260), u)
            return (q[0], q[1], -1, 1)
        u = ramp(t, T_DROP, T_DROP + 1.4); q = lerp((LANDX + 60, 260), (LANDX - 1700, 0), u ** 1.4)
        return (q[0], q[1], -1, 0)
    return None

def gull_layer(cr, t, p, ly):
    if ly != "front": return
    g = gull_state(t)
    if g: O.draw_seagull(cr, g[0], g[1], s=0.9, flap=math.sin(t * 16), facing=g[2], carry=g[3])
    # the dropped scoop: falls, sits on his head, in his hand, eaten
    if T_DROP <= t < T_EAT:
        hx, hy = p["head"]
        if t < T_PLOP:
            u = ramp(t, T_DROP, T_PLOP)
            x = lerp(LANDX + 60 - 155, hx, u); y = lerp(260 - 10, hy - 150, u * u)
            O.draw_scoop(cr, x, y)
        elif t < T_TAKE:
            sq = 1 - 0.25 * trap(t, T_PLOP, T_PLOP + 0.06, T_PLOP + 0.3)
            cr.save(); cr.translate(hx, hy - 150 + 40 * (1 - sq)); cr.scale(1 / sq, sq); O.draw_scoop(cr, 0, 0); cr.restore()
        else:
            rx, ry = p["rhand"]; O.draw_scoop(cr, rx + 5, ry - 45)
            L.draw_grips(cr, p)
S.prop(gull_layer)

if __name__ == "__main__":
    print(f"end {S.t:.2f}", file=sys.stderr)
    S.render("day015.mp4")
