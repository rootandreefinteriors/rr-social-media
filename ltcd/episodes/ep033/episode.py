"""Day 33: IG @nicolascechettoschuller: "Go to mars". See BEATS.md.
He reads it on the night street outside the museum, sees a red dot by the moon, and rides his T. rex out through a fog
bank to a LAUNCH SITE: a giant rocket, a countdown board running. Two helmets out of nowhere (one giant, for the rex).
The cramped capsule, 3-2-1, the big red button, liftoff, space. An asteroid: the rex knows what that is. He swerves,
pulls the shade, pats its helmet. Mars: out of fuel, crash landing, a red dust cloud. One small step. The rex floats in
Mars gravity. A lonely rover rolls over, beeps happy birthday to itself, takes a selfie. The ask on Mars.
"""
import sys, os, math, random, wave
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
import numpy as np
import moves as M
import ltcd as L
import objects as O
import character as C
from ltcd import Track, ramp, lerp, pulse, FLOOR_Y
from ink import smooth, sketch_line, draw_text

# the museum district (day 32) is drawn with day 32's own code
_spec = importlib.util.spec_from_file_location("ep032_episode", os.path.join(HERE, "..", "ep032", "episode.py"))
E32 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(E32)
E31 = E32.E31

FR = 1 / 30
sk_rect, sk_poly, sk_circ, sk_ell = O.sketch_rect, O.sketch_poly, O.sketch_circle, O.sketch_ellipse
INKC = (0.07, 0.07, 0.09)
RS = E32.RS

def cam(x, z, fs=1530):
    return (x, FLOOR_Y - (fs - 960) / z, z)

# ================================================================ places
X_STOP = E32.X_STOP                   # the T. rex on the street (day 32 ask)
AX = E32.AX                           # him on the sidewalk
FOG_S = X_STOP + 3300.0               # the fog bank at the end of the street
LS = 12000000.0                       # the launch site
FOG_L = LS - 2400.0
RKX = LS + 950.0                      # the rocket on its pad
PAD_H = 150.0
BOARD_X = LS + 150.0
REX_LS = LS - 1250.0                  # the T. rex standing at the launch site
HIM_LS = LS - 380.0
CAPX = 12100000.0                     # the capsule interior set
SPX = 12200000.0                      # space (over the Earth)
SPY = -20000.0
SPX2 = 12300000.0                     # space (the asteroid)
SPX3 = 12400000.0                     # space (arriving at Mars)
MRS = 12500000.0                      # Mars
RKM = MRS + 2750.0                    # the rocket on Mars
HIM_M = MRS + 410.0
HF = HIM_M + 150.0                    # where he ends up (after the first step)
REX_M = MRS + 1250.0
ROV_X0, ROV_X1 = MRS + 3000.0, MRS + 1180.0

# ================================================================ timeline
T_READ = 0.3
T_SKY = 1.9
CUT_RIDE = 2.8; T_REINS = 2.95; T_BOLT = 3.1
CUT_LS = 4.5; T_SKID1 = 5.3; T_UP = 5.5
CUT_STAND = 6.3
T_BOARD1 = 6.35
T_HELM = 6.7; POP_HELM = T_HELM + 2.1
T_HUP = 9.4; T_HON = 10.2
T_REXLOOK = 10.45
T_HELM2 = 10.7; POP_HELM2 = T_HELM2 + 2.1
CUT_RH = 13.3; T_FOG = 13.45; T_BOARD2 = 13.85
CUT_CAP = 14.4
T_N = (14.6, 15.4, 16.2)               # 3, 2, 1
T_PRESS = 17.0
CUT_LAUNCH = 17.4; T_LIFT = 18.2
CUT_SPACE = 21.2; T_COAST = 21.6
CUT_IN2 = 22.6; T_AST0 = 23.5; T_PANIC = 23.9
T_LOOKREX = 24.8; T_LOOKAST = 25.3; T_STICK = 26.1
CUT_MISS = 26.3; T_PASS0, T_PASS1 = 26.5, 27.3
CUT_IN3 = 27.9; T_SHADE0, T_SHADE1 = 28.3, 28.6; T_PAT = (29.0, 29.35); T_CALM = 29.6
CUT_APP = 30.3; T_FLIP0, T_FLIP1 = 30.5, 31.3
CUT_LAND = 31.9; T_SPUT = (32.3, 32.6, 32.9); T_SLAM = 33.1; T_CLEAR = 34.4
CUT_STEP = 34.8; T_FOOT0, T_FOOT1 = 35.0, 35.7; T_PULLBACK = 36.55
T_REXJUMP = 36.6; T_REXLAND = 37.2
T_HOP0, T_HOP1 = 38.0, 40.6
T_ROV0, T_ROV1 = 40.9, 42.0
T_ROVLOOK = 42.1; T_SNIFF = 42.5
T_SING0 = 43.0; T_SING1 = 44.4
T_ARM0, T_SELFIE = 44.5, 45.2
T_ASK = 46.0; HOLD = 9.5

# ================================================================ the T. rex (outdoors)
def rex(t):
    """(X near foot, lift, pitch, face, st) for the outdoor T. rex."""
    st = dict(O.DINO); st.update(s=RS, look=(-0.5, 0.6), smile=0.7, lid=0.0, mouth=0.0, arms=0.0, walk=0.0)
    X, lift, pitch, face = X_STOP, 0.0, 0.05, 1
    if t < CUT_RIDE:
        if t >= T_SKY + 0.3: st["look"] = (-0.6, -1.0); pitch = -0.06 * smooth(ramp(t, T_SKY + 0.3, T_SKY + 0.8))
    elif t < CUT_LS:
        st["look"] = (-1.0, 0.0); pitch = 0.0
        if t >= T_BOLT:
            u = t - T_BOLT
            X = X_STOP + 900 * u + 700 * u * u
            st["walk"] = u * 16.0
            pitch = 0.10 + 0.05 * math.sin(u * 16)
            lift = 40 * abs(math.sin(u * 8))
            st["mouth"] = 0.2
    elif t < CUT_CAP:
        if t < T_SKID1:
            u = ramp(t, CUT_LS, T_SKID1)
            X = lerp(FOG_L - 200, REX_LS, 1 - (1 - u) ** 2)
            st["walk"] = 0.0 if u > 0.5 else (t - CUT_LS) * 16
            pitch = 0.22 * math.sin(math.pi * u); st["look"] = (-1.0, 0.0)
        else:
            X = REX_LS; pitch = 0.0
            st["look"] = (-1.0, -0.4)
            if t >= T_UP: st["look"] = (-0.6, -1.0); pitch = -0.10 * smooth(ramp(t, T_UP, T_UP + 0.6))
            if t >= CUT_STAND - FR: st["look"] = (-0.8, 0.5); pitch = 0.05; st["smile"] = 0.5
            if t >= T_REXLOOK: st["look"] = (-1.0, 0.8); pitch = 0.08
            if t >= POP_HELM2 + 0.2: st["look"] = (-0.9, 0.0); st["lid"] = 0.0; st["smile"] = 0.2
            if t >= CUT_RH - FR: st["look"] = (-0.6, 0.3); st["smile"] = 0.7; pitch = 0.04
    elif t < CUT_LAND:
        X = REX_LS                                         # (not drawn outdoors in these shots)
    else:
        face = -1; X = REX_M; st["look"] = (-0.6, 0.6); st["smile"] = 0.6
        if t < T_REXLAND:
            u = ramp(t, T_REXJUMP, T_REXLAND)
            X = lerp(RKM - 150, REX_M, u); lift = 900 * (1 - u) + 260 * math.sin(math.pi * u)
            pitch = 0.08
        elif t < T_HOP0:
            st["look"] = (-0.2, 1.0); pitch = 0.18 * smooth(ramp(t, T_REXLAND + 0.2, T_REXLAND + 0.6))
            if t >= T_REXLAND + 1.2: st["look"] = (-0.8, -0.2); pitch = 0.0; st["smile"] = 0.9
        elif t < T_HOP1:
            u = ramp(t, T_HOP0, T_HOP1, "linear")
            lift = 1750 * 4 * u * (1 - u)
            pitch = -0.25 * math.sin(math.pi * u)
            st["eyes"] = "happy" if 0.15 < u < 0.85 else "normal"; st["smile"] = 1.0
            st["arms"] = 0.6
        else:
            st["smile"] = 0.8; st["look"] = (-0.8, 0.2)
            if t >= T_ROVLOOK: st["look"] = (1.0, 0.3)
            if T_SNIFF <= t < T_SING0: pitch = 0.1 + 0.03 * math.sin(t * 30)
            if t >= T_SELFIE - 0.6: st["look"] = (0.9, -0.2); st["eyes"] = "normal"; st["smile"] = 1.0
            if T_SELFIE <= t < T_SELFIE + 0.5: st["eyes"] = "happy"
            if t >= T_ASK: st["look"] = (-0.6, 0.6); st["smile"] = 0.7; st["eyes"] = "normal"
    return X, lift, pitch, face, st

def rex_world(X, lift, pitch, face, lx, h):
    """a point in the T. rex's own (draw_dino, left-facing, x=0) coords -> world."""
    s = RS
    px, py = 40 * s, FLOOR_Y - 400 * s
    x, y = lx * s, FLOOR_Y - h * s
    c, s_ = math.cos(-pitch), math.sin(-pitch)
    dx, dy = x - px, y - py
    x, y = px + dx * c - dy * s_, py + dx * s_ + dy * c
    return (X - face * x, y - lift)

def seat(t):
    X, lift, pitch, face, st = rex(t)
    x, y = rex_world(X, lift, pitch, face, 215, 615)
    return (x, y - O._walkbob(st))

def rex_drawn(t):
    if t < CUT_LS: return True
    if t < CUT_CAP - FR: return True
    if t >= CUT_LAND - FR and t >= T_REXJUMP: return True
    return False

def helmet(cr, x, y, r, fog=0.0, sid=33000, collar=True):
    """a fishbowl space helmet centred (x, y), radius r."""
    cr.arc(x, y, r, 0, 2 * math.pi); cr.set_source_rgba(0.80, 0.92, 1.0, 0.16); cr.fill()
    if fog > 0.01:
        cr.arc(x + 0.15 * r, y + 0.3 * r, r * 0.55, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.55 * fog); cr.fill()
    sk_circ(cr, x, y, r, max(5, r * 0.03), sid=sid, fill=None)
    cr.arc(x, y, r * 0.78, math.pi * 1.1, math.pi * 1.45); cr.set_source_rgba(1, 1, 1, 0.85); cr.set_line_width(max(6, r * 0.07)); cr.stroke()
    cr.arc(x, y, r * 0.78, math.pi * 1.55, math.pi * 1.6); cr.stroke()
    if collar:
        sk_ell(cr, x, y + r * 0.92, r * 0.62, r * 0.16, 5, sid=sid + 1, fill=(0.80, 0.80, 0.84))

def rex_helmet_on(t):
    return t >= CUT_RH - FR

def rex_head_c(t):
    X, lift, pitch, face, st = rex(t)
    x, y = rex_world(X, lift, pitch, face, -235, 930)
    return x, y - O._walkbob(st)

def draw_rex(cr, t):
    if not rex_drawn(t): return
    X, lift, pitch, face, st = rex(t)
    blink = 0.0
    for b in (1.2, 6.9, 11.6, 13.5, 39.0, 41.4, 48.0, 53.0):
        if b <= t < b + 0.16: blink = math.sin(math.pi * (t - b) / 0.16)
    cr.save(); cr.translate(0, -lift)
    O.draw_trex(cr, X, st, t, face=face, pitch=pitch, blink=blink)
    cr.restore()
    # the saddle stays on it
    x, y = rex_world(X, lift, pitch, face, 215, 600)
    y -= O._walkbob(st)
    E32.draw_saddle(cr, x, y + 10, pitch * face + 0.08 * face, 1.0, sid=33510, stirrups=False)
    if rex_helmet_on(t):
        hx, hy = rex_head_c(t)
        fog = 0.0
        if t < CUT_CAP: fog = pulse(t, T_FOG + 0.4, 0.5)
        helmet(cr, hx, hy, 300, fog=fog, sid=33020)

def draw_reins(cr, t, p):
    if not (CUT_RIDE - FR <= t < CUT_STAND - FR): return
    hand = ((p["lhand"][0] + p["rhand"][0]) / 2, (p["lhand"][1] + p["rhand"][1]) / 2)
    X, lift, pitch, face, st = rex(t)
    m = O.trex_pt(X, st, face, pitch, "mouth"); m = (m[0], m[1] - lift)
    mid = ((hand[0] + m[0]) / 2, max(hand[1], m[1]) + 60)
    cr.move_to(*hand); cr.curve_to(mid[0], mid[1], mid[0], mid[1], m[0] - 40, m[1] - 20)
    cr.set_source_rgb(0.35, 0.20, 0.10); cr.set_line_width(7); cr.stroke()

# ================================================================ the rocket
WHITE_R = (0.95, 0.95, 0.93)
def draw_rocket(cr, x, yb, ang=0.0, flame=0.0, t=0.0, s=1.0, sid=34000, porthole=True, flame_len=1.0):
    """the rocket standing with its base (nozzle top) at (x, yb), rotated ang around its middle. ~2500 tall."""
    cr.save(); cr.translate(x, yb - 1200 * s); cr.rotate(ang); cr.scale(s, s); cr.translate(0, 1200)
    if flame > 0.01:
        n = 7
        Lf = (650 + 80 * math.sin(t * 23)) * flame_len
        pts = [(0, 150 + k * Lf / (n - 1)) for k in range(n)]
        cr.save(); cr.arc(0, 200, 260 * flame, 0, 2 * math.pi); cr.set_source_rgba(1.0, 0.85, 0.4, 0.35 * flame); cr.fill(); cr.restore()
        O.draw_flames(cr, pts, t, w=150 * flame)
    sk_poly(cr, [(-110, 0), (110, 0), (150, 150), (-150, 150)], 6, sid=sid, fill=(0.45, 0.45, 0.50))        # nozzle
    for d in (-1, 1):                                                                                     # fins
        sk_poly(cr, [(d * 200, -620), (d * 420, -120), (d * 430, 60), (d * 200, -60)], 6, sid=sid + 1 + (d > 0), fill=(0.80, 0.16, 0.14))
    sk_rect(cr, -210, -1900, 210, 0, 7, sid=sid + 3, fill=WHITE_R)                                        # body
    cr.rectangle(-206, -420, 412, 120); cr.set_source_rgb(0.12, 0.12, 0.14); cr.fill()
    cr.rectangle(-206, -1150, 206, 260); cr.set_source_rgb(0.12, 0.12, 0.14); cr.fill()
    cr.rectangle(0, -890, 206, 260); cr.set_source_rgb(0.12, 0.12, 0.14); cr.fill()
    sk_rect(cr, -210, -1900, 210, 0, 7, sid=sid + 3, fill=None)
    sk_poly(cr, [(-210, -1900), (-170, -2150), (-80, -2380), (0, -2480), (80, -2380), (170, -2150), (210, -1900)], 7,
            sid=sid + 4, fill=(0.80, 0.16, 0.14))                                                        # nose cone
    if porthole:
        sk_circ(cr, 0, -1680, 80, 6, sid=sid + 5, fill=(0.55, 0.75, 0.95))
        cr.arc(-20, -1700, 40, math.pi * 1.1, math.pi * 1.5); cr.set_source_rgba(1, 1, 1, 0.8); cr.set_line_width(8); cr.stroke()
    sk_poly(cr, [(-30, -620), (30, -620), (30, 60), (-30, 60)], 5, sid=sid + 6, fill=(0.80, 0.16, 0.14))     # centre fin (edge-on)
    cr.restore()

def rocket_pt(x, yb, ang, lx, ly, s=1.0):
    """rocket-local (lx, ly) (base = 0, up = -y) -> world, matching draw_rocket."""
    cx, cy = x, yb - 1200 * s
    dx, dy = lx * s, (ly + 1200) * s
    c, s_ = math.cos(ang), math.sin(ang)
    return (cx + dx * c - dy * s_, cy + dx * s_ + dy * c)

# ================================================================ worlds
NSKY = E32.NSKY
WALK_TOP = E32.WALK_TOP

def mars_dot(cr, t):
    """a small red dot next to the moon (rides with the camera, like the moon)."""
    cx, cy, z = L.cam_track.at(t)
    x, y = cx + (330 - 540) / z, cy + (700 - 960) / z
    r = 15 / z
    cr.arc(x, y, r * 3.0, 0, 2 * math.pi); cr.set_source_rgba(1.0, 0.45, 0.3, 0.25 + 0.1 * math.sin(t * 5)); cr.fill()
    cr.arc(x, y, r, 0, 2 * math.pi); cr.set_source_rgb(0.95, 0.38, 0.22); cr.fill()

def floodlight(cr, x, t, sid, beam=1.0, flip=1):
    sk_rect(cr, x - 22, FLOOR_Y - 1700, x + 22, FLOOR_Y, 5, sid=sid, fill=(0.35, 0.35, 0.40))
    for k in range(6):
        sketch_line(cr, [(x - 22, FLOOR_Y - 250 * k), (x + 22, FLOOR_Y - 250 * k - 125)], 3, sid=sid + 1, alpha=0.6)
    sk_rect(cr, x - 160, FLOOR_Y - 1880, x + 160, FLOOR_Y - 1700, 5, sid=sid + 2, fill=(0.25, 0.25, 0.30))
    for k in range(4):
        sk_circ(cr, x - 110 + 73 * k, FLOOR_Y - 1790, 30, 3, sid=sid + 3 + k, fill=(1.0, 0.97, 0.80))
    if beam > 0:
        cr.move_to(x - 150, FLOOR_Y - 1760); cr.line_to(x + 150, FLOOR_Y - 1760)
        cr.line_to(x + flip * 1500 + 600, FLOOR_Y); cr.line_to(x + flip * 1500 - 600, FLOOR_Y); cr.close_path()
        cr.set_source_rgba(1.0, 0.96, 0.75, 0.10 * beam); cr.fill()

def draw_gantry(cr, x, t):
    """the red launch tower next to the rocket."""
    top = FLOOR_Y - PAD_H - 2350
    for d in (0, 260):
        sketch_line(cr, [(x + d, FLOOR_Y - PAD_H), (x + d, top)], 12, sid=34100 + d % 7, amp=0.2, color=(0.70, 0.18, 0.14))
    k = 0
    y = FLOOR_Y - PAD_H
    while y > top + 100:
        sketch_line(cr, [(x, y), (x + 260, y - 220)], 6, sid=34110 + k % 5, amp=0.2, color=(0.70, 0.18, 0.14))
        sketch_line(cr, [(x, y - 220), (x + 260, y - 220)], 6, sid=34120 + k % 5, amp=0.2, color=(0.70, 0.18, 0.14))
        y -= 220; k += 1
    sk_rect(cr, x - 300, FLOOR_Y - PAD_H - 1830, x, FLOOR_Y - PAD_H - 1790, 4, sid=34130, fill=(0.70, 0.18, 0.14))  # walkway arm

def count_val(t):
    return max(0, int(math.ceil(T_PRESS - t - 1e-6)))

def draw_board(cr, t):
    x = BOARD_X
    for d in (-150, 150):
        sketch_line(cr, [(x + d, FLOOR_Y), (x + d, FLOOR_Y - 760)], 10, sid=34200 + (d > 0), amp=0.2)
    sk_rect(cr, x - 210, FLOOR_Y - 1060, x + 210, FLOOR_Y - 740, 6, sid=34202, fill=(0.08, 0.08, 0.10))
    v = count_val(t)
    col = (255, 150, 40) if v > 3 else (255, 60, 50)
    draw_text(cr, "T-00:%02d" % v, x, FLOOR_Y - 900, 108, color=col)

def draw_launch_site(cr, t, lift_dark=0.0):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    a, b = vx0 - 50, vx1 + 50
    for i, (y, c) in enumerate(NSKY):
        y1 = NSKY[i + 1][0] if i + 1 < len(NSKY) else FLOOR_Y - 200
        top = y if i > 0 else min(y, vy0 - 100)
        cr.rectangle(a, top, b - a, y1 - top + 1); cr.set_source_rgb(*c); cr.fill()
    cx, cy, z = L.cam_track.at(t)
    for k in range(30):
        sx = cx - 1500 + (k * 397) % 3000; sy = cy - 2300 + (k * 211) % 1500
        if sy < FLOOR_Y - 800:
            cr.arc(sx, sy, 5 + (k % 3) * 2, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.5 + 0.4 * math.sin(t * 2 + k)); cr.fill()
    # far shoreline + low hills
    cr.rectangle(a, FLOOR_Y - 200, b - a, 201); cr.set_source_rgb(0.16, 0.20, 0.30); cr.fill()
    sk_poly(cr, [(LS - 4000, FLOOR_Y - 200), (LS - 2600, FLOOR_Y - 420), (LS - 1500, FLOOR_Y - 260), (LS - 400, FLOOR_Y - 380),
                 (LS + 900, FLOOR_Y - 230), (LS + 2400, FLOOR_Y - 450), (LS + 4200, FLOOR_Y - 200)], 5, sid=34300, fill=(0.14, 0.15, 0.22))
    # the ground (concrete apron)
    cr.rectangle(a, FLOOR_Y - 60, b - a, 1600); cr.set_source_rgb(0.38, 0.38, 0.40); cr.fill()
    for k in range(int((a - LS) // 400) - 1, int((b - LS) // 400) + 2):
        sketch_line(cr, [(LS + 400 * k, FLOOR_Y - 55), (LS + 400 * k - 120, FLOOR_Y + 400)], 3, sid=34310 + k % 7, color=(0.30, 0.30, 0.32), amp=0.3)
    sketch_line(cr, [(a, FLOOR_Y), (b, FLOOR_Y)], 6, sid=34320, amp=0.3)
    # warning stripes on the pad
    sk_rect(cr, RKX - 700, FLOOR_Y - PAD_H, RKX + 700, FLOOR_Y, 6, sid=34330, fill=(0.55, 0.55, 0.58))
    for k in range(10):
        xx = RKX - 680 + 140 * k
        cr.move_to(xx, FLOOR_Y - PAD_H + 10); cr.line_to(xx + 60, FLOOR_Y - PAD_H + 10); cr.line_to(xx + 20, FLOOR_Y - PAD_H + 50); cr.line_to(xx - 40, FLOOR_Y - PAD_H + 50)
        cr.close_path(); cr.set_source_rgb(0.95, 0.80, 0.15); cr.fill()
    floodlight(cr, LS - 1700, t, 34400, flip=1)
    floodlight(cr, RKX + 1500, t, 34410, flip=-1)
    draw_gantry(cr, RKX + 420, t)

def rocket_rise(t):
    if t < T_LIFT: return 0.0
    u = t - T_LIFT
    return 180 * u + 520 * u * u

def draw_launch(cr, t):
    """the rocket on the pad (before and during liftoff)."""
    rise = rocket_rise(t) if t >= CUT_LAUNCH - FR else 0.0
    flame = 0.0
    if t >= CUT_LAUNCH - FR:
        flame = min(1.0, 0.5 + (t - CUT_LAUNCH) * 1.2)
    sh = 0.0
    if CUT_LAUNCH <= t < T_LIFT: sh = 6 * math.sin(t * 60)
    draw_rocket(cr, RKX + sh, FLOOR_Y - PAD_H - rise, 0.0, flame=flame, t=t, flame_len=1.0 + min(2.0, rise / 800))

def draw_launch_smoke(cr, t):
    if t < CUT_LAUNCH - FR or t >= CUT_SPACE: return
    u = t - CUT_LAUNCH
    for k in range(16):
        side = -1 if k % 2 else 1
        spread = min(1.0, u / 1.6)
        x = RKX + side * (200 + 140 * (k // 2) * spread * 2.2)
        y = FLOOR_Y - PAD_H - 60 - 90 * ((k * 37) % 5) * spread
        r = (160 + 70 * ((k * 13) % 4)) * (0.4 + 0.9 * spread)
        O.draw_smoke_puff(cr, x + 30 * math.sin(t * 2 + k), y, r, alpha=0.95)

def sky_dark(cr, t):
    """the sky goes black as the rocket climbs (drawn over the launch-site sky, behind the rocket)."""
    if not (CUT_LAUNCH - FR <= t < CUT_SPACE): return
    cx, cy, z = L.cam_track.at(t)
    d = smooth(ramp(-(cy - (FLOOR_Y - 1000)), 600, 3200))
    if d <= 0.01: return
    vx0, vy0, vx1, vy1 = O._visible(cr)
    cr.rectangle(vx0 - 50, vy0 - 50, vx1 - vx0 + 100, vy1 - vy0 + 100); cr.set_source_rgba(0.02, 0.02, 0.06, d); cr.fill()
    for k in range(60):
        sx = vx0 + (k * 7919) % max(1, int(vx1 - vx0)); sy = vy0 + (k * 3571) % max(1, int(vy1 - vy0))
        cr.rectangle(sx, sy, 9, 9); cr.set_source_rgba(1, 1, 0.92, d * (0.55 + 0.45 * math.sin(t * 2 + k))); cr.fill()

def stars(cr, t, vx=0.0, vy=0.0, n=120, seed=0):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    cr.rectangle(vx0 - 50, vy0 - 50, vx1 - vx0 + 100, vy1 - vy0 + 100); cr.set_source_rgb(0.02, 0.02, 0.06); cr.fill()
    W_, H_ = vx1 - vx0, vy1 - vy0
    for k in range(n):
        bx = ((k * 7919 + seed * 131) % 10000) / 10000; by = ((k * 3571 + seed * 71) % 10000) / 10000
        x = vx0 + ((bx * W_ + vx * t) % W_); y = vy0 + ((by * H_ + vy * t) % H_)
        if abs(vx) > 900:
            cr.move_to(x, y); cr.line_to(x - vx * 0.05, y); cr.set_source_rgba(1, 1, 0.92, 0.7); cr.set_line_width(7); cr.stroke()
        else:
            cr.rectangle(x, y, 9, 9); cr.set_source_rgba(1, 1, 0.92, 0.55 + 0.45 * math.sin(t * 2 + k)); cr.fill()

def draw_mars_planet(cr, cx, cy, R, sid=34600):
    for i, (dr, a) in enumerate(((240, 0.12), (140, 0.2))):
        cr.arc(cx, cy, R + dr, 0, 2 * math.pi); cr.set_source_rgba(1.0, 0.6, 0.4, a); cr.fill()
    cr.arc(cx, cy, R, 0, 2 * math.pi); cr.set_source_rgb(0.80, 0.38, 0.22); cr.fill()
    cr.save(); cr.arc(cx, cy, R, 0, 2 * math.pi); cr.clip()
    rr = random.Random(sid)
    for k in range(26):
        a = rr.uniform(-0.5, 0.5) - math.pi / 2; d = rr.uniform(0.82, 1.0) * R
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
        sk_ell(cr, x, y, rr.uniform(60, 260), rr.uniform(30, 120), 4, sid=sid + k, fill=(0.66, 0.30, 0.18))
    sk_ell(cr, cx - 900, cy - R + 220, 1500, 110, 4, sid=sid + 40, fill=(0.62, 0.27, 0.16))   # the big canyon
    sk_ell(cr, cx + 400, cy - R + 60, 700, 70, 0.1, sid=sid + 41, fill=(1, 1, 1), alpha=0.6)
    cr.restore()
    cr.arc(cx, cy, R, 0, 2 * math.pi); cr.set_source_rgb(*INKC); cr.set_line_width(8); cr.stroke()

# ---- Mars
MSKY = [(-6000, (0.76, 0.55, 0.42)), (-1500, (0.84, 0.63, 0.47)), (200, (0.90, 0.71, 0.53)), (800, (0.94, 0.78, 0.60))]
HOR = FLOOR_Y - 280
def draw_mars(cr, t):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    a, b = vx0 - 50, vx1 + 50
    for i, (y, c) in enumerate(MSKY):
        y1 = MSKY[i + 1][0] if i + 1 < len(MSKY) else HOR
        top = y if i > 0 else min(y, vy0 - 100)
        cr.rectangle(a, top, b - a, y1 - top + 1); cr.set_source_rgb(*c); cr.fill()
    cx, cy, z = L.cam_track.at(t)
    # two little moons (ride with the camera)
    sk_circ(cr, cx - 250 / z, cy - 640 / z, 26 / z, 3, sid=34700, fill=(0.72, 0.66, 0.60))
    sk_ell(cr, cx - 120 / z, cy - 560 / z, 15 / z, 11 / z, 3, sid=34701, fill=(0.72, 0.66, 0.60))
    # the giant flat volcano on the horizon
    sk_poly(cr, [(MRS + 300, HOR), (MRS + 1500, HOR - 520), (MRS + 2300, HOR - 600), (MRS + 3200, HOR - 500), (MRS + 4600, HOR)], 6,
            sid=34710, fill=(0.80, 0.52, 0.38))
    sk_ell(cr, MRS + 2250, HOR - 590, 420, 40, 4, sid=34711, fill=(0.70, 0.42, 0.30))
    # the mesa with a face
    sk_poly(cr, [(MRS - 1600, HOR), (MRS - 1450, HOR - 330), (MRS - 900, HOR - 360), (MRS - 700, HOR)], 5, sid=34720, fill=(0.74, 0.46, 0.33))
    for dx in (-1270, -1040):
        sk_ell(cr, MRS + dx, HOR - 255, 40, 20, 3, sid=34721, fill=(0.55, 0.32, 0.22))
    sketch_line(cr, [(MRS - 1250, HOR - 150), (MRS - 1060, HOR - 150)], 6, sid=34722, color=(0.55, 0.32, 0.22))
    sk_poly(cr, [(MRS - 3600, HOR), (MRS - 3000, HOR - 180), (MRS - 2300, HOR - 120), (MRS - 1900, HOR)], 5, sid=34723, fill=(0.78, 0.50, 0.36))
    # far ground + near ground
    cr.rectangle(a, HOR, b - a, FLOOR_Y - HOR + 1); cr.set_source_rgb(0.80, 0.46, 0.30); cr.fill()
    cr.rectangle(a, FLOOR_Y, b - a, 1600); cr.set_source_rgb(0.72, 0.38, 0.24); cr.fill()
    rr = random.Random(33)
    for k in range(60):
        x = MRS - 3000 + k * 140 + rr.uniform(-50, 50); y = HOR + 30 + rr.uniform(0, FLOOR_Y - HOR - 40)
        if a < x < b:
            sk_ell(cr, x, y, rr.uniform(10, 30), rr.uniform(5, 12), 2, sid=34730 + k % 9, fill=(0.62, 0.32, 0.20))
    for k in range(18):
        x = MRS - 2600 + k * 420 + rr.uniform(-80, 80); y = FLOOR_Y + rr.uniform(80, 500)
        if a < x < b:
            sk_poly(cr, [(x - 70, y), (x - 40, y - 50), (x + 30, y - 60), (x + 80, y)], 4, sid=34740 + k % 9, fill=(0.56, 0.30, 0.20))
    for k, (x, y, w) in enumerate(((MRS - 700, FLOOR_Y + 260, 260), (MRS + 2900, FLOOR_Y + 380, 340), (MRS + 1100, FLOOR_Y + 620, 200))):
        sk_ell(cr, x, y, w, w * 0.22, 4, sid=34760 + k, fill=(0.62, 0.32, 0.20))
        sk_ell(cr, x, y + 6, w * 0.75, w * 0.14, 0.1, sid=34765 + k, fill=(0.55, 0.28, 0.18))
    sketch_line(cr, [(a, FLOOR_Y), (b, FLOOR_Y)], 6, sid=34770, amp=0.3)

def landed(t): return t >= T_SLAM
def rocket_mars(t):
    """(yb, ang, flame) of the rocket coming down on Mars."""
    if t < T_SLAM:
        u = ramp(t, CUT_LAND, T_SPUT[0])
        yb = lerp(FLOOR_Y - 4200, FLOOR_Y - 800, 1 - (1 - u) ** 2)
        if t >= T_SPUT[0]:
            yb = FLOOR_Y - 800 + 120 * ramp(t, T_SPUT[0], T_SPUT[2])
        if t >= T_SPUT[2] + 0.05:
            v = ramp(t, T_SPUT[2] + 0.05, T_SLAM, "linear"); yb = lerp(FLOOR_Y - 680, FLOOR_Y + 150, v * v)
        fl = 1.0
        for ts in T_SPUT:
            if ts <= t < ts + 0.12: fl = 0.0
        if t >= T_SPUT[2] + 0.05: fl = 0.0
        return yb, 0.03 * math.sin(t * 5), fl
    k = smooth(ramp(t, T_SLAM, T_SLAM + 0.25))
    return FLOOR_Y + 150 + 30 * math.sin(math.pi * k), 0.14 * k, 0.0

def draw_mars_rocket(cr, t):
    if t < CUT_LAND - FR: return
    yb, ang, fl = rocket_mars(t)
    if t < T_SLAM:
        draw_rocket(cr, RKM, yb, ang, flame=fl, t=t, flame_len=0.8)
        for ts in T_SPUT:
            u = (t - ts) / 0.5
            if 0 <= u < 1:
                O.draw_smoke_puff(cr, RKM + 40 * math.sin(ts * 9), yb + 200 + 300 * u, 120 + 140 * u, alpha=0.8 * (1 - u), dark=0.5)
    else:
        cr.save(); cr.rectangle(RKM - 3000, -9000, 6000, 9000 + FLOOR_Y + 30); cr.clip()
        draw_rocket(cr, RKM, yb, ang, flame=0.0, t=t)
        cr.restore()
        sk_poly(cr, [(RKM - 520, FLOOR_Y + 20), (RKM - 380, FLOOR_Y - 60), (RKM + 420, FLOOR_Y - 50), (RKM + 560, FLOOR_Y + 20)], 5,
                sid=34800, fill=(0.66, 0.34, 0.22))

def draw_dust(cr, t):
    if not (T_SLAM - 0.02 <= t < T_CLEAR + 0.4): return
    u = ramp(t, T_SLAM, T_CLEAR + 0.4)
    cover = 1.0 - smooth(ramp(t, T_SLAM + 0.6, T_CLEAR + 0.4))
    rr = random.Random(7)
    for k in range(34):
        a = rr.uniform(math.pi, 2 * math.pi); d = rr.uniform(0.3, 1.0)
        r = 300 + 3500 * d * min(1, (t - T_SLAM) * 2.5)
        x = RKM + math.cos(a) * r * 1.2; y = FLOOR_Y - 100 + math.sin(a) * r * 0.55
        O.draw_smoke_puff(cr, x, y, (400 + 300 * rr.random()) * (0.6 + 0.8 * u), alpha=0.95 * cover)
    if cover > 0.02:
        vx0, vy0, vx1, vy1 = O._visible(cr)
        cr.rectangle(vx0 - 50, vy0 - 50, vx1 - vx0 + 100, vy1 - vy0 + 100)
        cr.set_source_rgba(0.82, 0.50, 0.34, 0.85 * cover * smooth(ramp(t, T_SLAM, T_SLAM + 0.25))); cr.fill()

def draw_dust_haze(cr, t):
    """red dust settling after the dust clears (tints, thins)."""
    if not (T_CLEAR + 0.4 <= t < T_CLEAR + 2.5): return
    a = 0.25 * (1 - ramp(t, T_CLEAR + 0.4, T_CLEAR + 2.5))
    vx0, vy0, vx1, vy1 = O._visible(cr)
    cr.rectangle(vx0 - 50, vy0 - 50, vx1 - vx0 + 100, vy1 - vy0 + 100); cr.set_source_rgba(0.85, 0.55, 0.38, a); cr.fill()

# ---- footprints
STAND = C.pose("stand", "deadpan")
FOOT_X = HIM_M - 540 + STAND["lfoot"][0] - 10
def draw_prints(cr, t):
    if t >= T_FOOT1:
        k = ramp(t, T_FOOT1, T_FOOT1 + 0.1)
        sk_ell(cr, FOOT_X - 20, FLOOR_Y + 8, 46, 14, 3, sid=34900, fill=(0.55, 0.28, 0.18), alpha=k)
        for j in range(4):
            sketch_line(cr, [(FOOT_X - 55 + 24 * j, FLOOR_Y + 4), (FOOT_X - 45 + 24 * j, FLOOR_Y + 14)], 3, sid=34901 + j, color=(0.45, 0.22, 0.14), alpha=k)
    if t >= T_REXLAND:
        x = REX_M - 40
        sk_ell(cr, x, FLOOR_Y + 22, 120, 28, 4, sid=34910, fill=(0.55, 0.28, 0.18))
        for j in (-1, 0, 1):
            sk_poly(cr, [(x - 60, FLOOR_Y + 22), (x - 130 - 10 * abs(j), FLOOR_Y + 22 + 26 * j), (x - 60, FLOOR_Y + 30 + 6 * j)], 3,
                    sid=34912 + j, fill=(0.55, 0.28, 0.18))

# ---- the rover
def rover_x(t):
    u = ramp(t, T_ROV0, T_ROV1)
    return lerp(ROV_X0, ROV_X1, 1 - (1 - u) ** 2)

def draw_rover(cr, t):
    if t < T_ROV0: return
    x = rover_x(t); yb = FLOOR_Y
    s = 1.6
    moving = T_ROV0 <= t < T_ROV1
    roll = (x - ROV_X0) / 40.0
    head = -1.0                                          # camera head looks left
    if t >= T_ROVLOOK: head = -1.0
    if T_ARM0 <= t < T_ASK: head = -0.4
    bob = 3 * math.sin(t * 20) if moving else 0.0
    cr.save(); cr.translate(x, yb); cr.scale(s, s)
    # wheels + rocker bars
    for k, wx in enumerate((-160, 0, 160)):
        sketch_line(cr, [(wx, -48), (0, -120 + bob)], 9, sid=35000 + k, amp=0.2, color=(0.30, 0.30, 0.34))
    for k, wx in enumerate((-160, 0, 160)):
        sk_circ(cr, wx, -45, 45, 5, sid=35010 + k, fill=(0.30, 0.30, 0.34))
        for j in range(3):
            a = roll + j * 2.09
            sketch_line(cr, [(wx, -45), (wx + 34 * math.cos(a), -45 + 34 * math.sin(a))], 4, sid=35020 + j, color=(0.6, 0.6, 0.65))
    # body
    sk_rect(cr, -190, -230 + bob, 190, -120 + bob, 6, sid=35030, fill=(0.93, 0.92, 0.88))
    sk_rect(cr, -150, -260 + bob, 120, -230 + bob, 5, sid=35031, fill=(0.85, 0.66, 0.25))
    sk_rect(cr, 120, -320 + bob, 200, -230 + bob, 5, sid=35032, fill=(0.80, 0.80, 0.84))     # the power box at the back
    for k in range(3):
        sketch_line(cr, [(130, -300 + 25 * k + bob), (190, -300 + 25 * k + bob)], 3, sid=35033 + k, alpha=0.6)
    # mast + camera head
    sketch_line(cr, [(-110, -230 + bob), (-110, -520 + bob)], 12, sid=35040, amp=0.2, color=(0.85, 0.85, 0.88))
    sketch_line(cr, [(-110, -230 + bob), (-110, -520 + bob)], 12, sid=35040, amp=0.2)
    hx, hy = -110, -560 + bob
    sk_rect(cr, hx - 75, hy - 45, hx + 75, hy + 45, 5, sid=35041, fill=(0.93, 0.92, 0.88))
    for k, dy in enumerate((-14, 18)):
        ex = hx + 75 * head
        sk_circ(cr, ex - 8 * (1 if head < 0 else -1), hy + dy, 17, 4, sid=35042 + k, fill=(0.15, 0.15, 0.20))
        cr.arc(ex - 12 * (1 if head < 0 else -1), hy + dy - 5, 5, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.8); cr.fill()
    # the arm (stowed at the front; up for the selfie)
    ar = smooth(ramp(t, T_ARM0, T_SELFIE - 0.1)) * (1 - smooth(ramp(t, T_ASK - 0.6, T_ASK)))
    sh = (-190, -175 + bob)
    el = (lerp(-260, -230, ar), lerp(-150, -520, ar) + bob)
    hd = (lerp(-300, -330, ar), lerp(-110, -760, ar) + bob)
    sketch_line(cr, [sh, el, hd], 9, sid=35050, amp=0.2, color=(0.30, 0.30, 0.34))
    sk_rect(cr, hd[0] - 34, hd[1] - 26, hd[0] + 34, hd[1] + 26, 4, sid=35051, fill=(0.93, 0.92, 0.88))
    sk_circ(cr, hd[0] - 34, hd[1], 13, 3, sid=35052, fill=(0.15, 0.15, 0.20))
    cr.restore()
    # notes while it beeps to itself
    if T_SING0 <= t < T_SING1:
        for k in range(4):
            u = ((t - T_SING0) * 0.9 + k / 4) % 1.0
            nx, ny = x + s * (hx + 40) - 160 * u + 40 * math.sin(u * 7 + k), yb + s * hy - 120 - 300 * u
            cr.arc(nx, ny, 16, 0, 2 * math.pi); cr.set_source_rgba(*INKC, 1 - u); cr.fill()
            sketch_line(cr, [(nx + 14, ny), (nx + 14, ny - 60)], 5, sid=35060 + k, alpha=1 - u)

# ================================================================ the capsule (interior set)
CAP_L, CAP_R, CAP_T, CAP_B = CAPX - 720, CAPX + 720, 330, FLOOR_Y
WIN = (CAPX + 430, 640, 150)
PANEL = (CAPX + 250, 940, CAPX + 700, 1300)
BUTTON = (CAPX + 360, 1225, 46)
HIM_CAP = CAPX - 430                   # his body offset in the capsule
def cap_outside(t):
    return "space" if t >= CUT_IN2 - FR else "pad"

def draw_window_view(cr, t):
    wx, wy, wr = WIN
    cr.save(); cr.arc(wx, wy, wr, 0, 2 * math.pi); cr.clip()
    if cap_outside(t) == "pad":
        cr.rectangle(wx - wr, wy - wr, 2 * wr, 2 * wr); cr.set_source_rgb(0.14, 0.14, 0.28); cr.fill()
        for k in range(5):
            cr.rectangle(wx - 120 + 55 * k, wy - 110 + 37 * (k % 3), 7, 7); cr.set_source_rgb(1, 1, 0.9); cr.fill()
        sketch_line(cr, [(wx + 60, wy - wr), (wx + 60, wy + wr)], 10, sid=35100, color=(0.70, 0.18, 0.14))   # the tower
    else:
        cr.rectangle(wx - wr, wy - wr, 2 * wr, 2 * wr); cr.set_source_rgb(0.02, 0.02, 0.06); cr.fill()
        for k in range(14):
            sx = wx - wr + ((k * 97 + t * 30) % (2 * wr)); sy = wy - wr + (k * 61) % (2 * wr)
            cr.rectangle(sx, sy, 6, 6); cr.set_source_rgb(1, 1, 0.9); cr.fill()
        if T_AST0 <= t < CUT_MISS + 1:
            u = ramp(t, T_AST0, T_STICK + 0.2)
            ax, ay = wx + lerp(170, 10, u), wy + lerp(-150, -10, u)
            r = lerp(22, 175, u ** 1.6)
            draw_asteroid(cr, ax, ay, r, t)
    cr.restore()
    # the shade
    if t >= T_SHADE0 and t >= CUT_IN3 - FR:
        k = smooth(ramp(t, T_SHADE0, T_SHADE1))
        cr.save(); cr.arc(wx, wy, wr, 0, 2 * math.pi); cr.clip()
        h = 2 * wr * k
        cr.rectangle(wx - wr, wy - wr, 2 * wr, h); cr.set_source_rgb(0.85, 0.80, 0.62); cr.fill()
        for j in range(int(h // 40)):
            sketch_line(cr, [(wx - wr, wy - wr + 40 * j + 20), (wx + wr, wy - wr + 40 * j + 20)], 2, sid=35110 + j % 5, alpha=0.3)
        cr.restore()
        sk_circ(cr, wx, wy - wr + h, 10, 3, sid=35120, fill=(0.6, 0.5, 0.3))
    sk_circ(cr, wx, wy, wr, 9, sid=35130, fill=None)
    sk_circ(cr, wx, wy, wr + 26, 7, sid=35131, fill=None)

def draw_asteroid(cr, x, y, r, t, sid=35200):
    rr = random.Random(sid)
    rot = t * 0.9
    pts = []
    for k in range(12):
        a = rot + k / 12 * 2 * math.pi
        d = r * (0.82 + 0.25 * rr.random())
        pts.append((x + math.cos(a) * d, y + math.sin(a) * d))
    sk_poly(cr, pts, max(3, r * 0.04), sid=sid, fill=(0.50, 0.44, 0.40))
    for k in range(4):
        a = rot + k * 1.7 + 0.3
        sk_circ(cr, x + math.cos(a) * r * 0.45, y + math.sin(a) * r * 0.45, r * 0.16, max(2, r * 0.025), sid=sid + 1 + k, fill=(0.40, 0.35, 0.32))

def draw_capsule(cr, t):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    cr.rectangle(vx0 - 50, vy0 - 50, vx1 - vx0 + 100, vy1 - vy0 + 100); cr.set_source_rgb(0.22, 0.23, 0.27); cr.fill()
    # the cabin (rounded cone shape)
    pts = [(CAP_L, CAP_B + 700), (CAP_L, CAP_B), (CAP_L + 60, CAP_T + 300), (CAPX - 300, CAP_T), (CAPX + 300, CAP_T), (CAP_R - 60, CAP_T + 300), (CAP_R, CAP_B), (CAP_R, CAP_B + 700)]
    sk_poly(cr, pts, 8, sid=35300, fill=(0.80, 0.81, 0.84))
    for k in range(6):
        x = CAP_L + 120 + 240 * k
        sketch_line(cr, [(x, CAP_T + 60), (x, CAP_B)], 3, sid=35301 + k, alpha=0.25)
    for k in range(int((CAP_R - CAP_L) // 60)):
        cr.arc(CAP_L + 40 + 60 * k, CAP_T + 330, 6, 0, 2 * math.pi); cr.set_source_rgba(0.4, 0.4, 0.45, 0.6); cr.fill()
    # the round hatch on the left (where the rex's head comes in)
    sk_circ(cr, CAPX - 470, 820, 330, 8, sid=35310, fill=(0.30, 0.31, 0.36))
    sk_circ(cr, CAPX - 470, 820, 290, 4, sid=35311, fill=None)
    # the floor
    cr.rectangle(CAP_L + 30, CAP_B - 60, CAP_R - CAP_L - 60, 760); cr.set_source_rgb(0.50, 0.51, 0.56); cr.fill()
    for k in range(12):
        sketch_line(cr, [(CAP_L + 60 + 120 * k, CAP_B - 50), (CAP_L + 20 + 120 * k, CAP_B + 650)], 3, sid=35305 + k % 5, alpha=0.3)
    sketch_line(cr, [(CAP_L + 30, CAP_B - 60), (CAP_R - 30, CAP_B - 60)], 6, sid=35306)
    # the control panel
    x0, y0, x1, y1 = PANEL
    sk_poly(cr, [(x0, y0), (x1, y0 - 60), (x1, y1), (x0 + 60, y1)], 6, sid=35320, fill=(0.38, 0.40, 0.46))
    sk_rect(cr, x0 + 110, y0 + 20, x0 + 380, y0 + 190, 5, sid=35321, fill=(0.06, 0.10, 0.08))
    v = None
    if t < CUT_LAUNCH:
        v = count_val(t)
        txt = str(v) if v <= 3 else "T-%02d" % v
        if t >= T_PRESS: txt = "GO"
        draw_text(cr, txt, x0 + 245, y0 + 105, 120 if len(txt) <= 2 else 80, color=(90, 255, 120))
    else:
        txt = {True: "MARS", False: "..."}[t >= CUT_IN3 - FR]
        if T_AST0 <= t < CUT_MISS: txt = "!!"
        draw_text(cr, txt, x0 + 245, y0 + 105, 90, color=(255, 80, 60) if txt == "!!" else (90, 255, 120))
    for k in range(6):
        cr.arc(x0 + 150 + 45 * k, y0 + 240, 12, 0, 2 * math.pi)
        on = (int(t * 4) + k) % 3 == 0
        cr.set_source_rgb(*((0.3, 1.0, 0.4) if on else (0.25, 0.25, 0.28))); cr.fill()
    bx, by, br = BUTTON
    pr = 6 if (T_PRESS <= t < T_PRESS + 0.3) else 0
    sk_ell(cr, bx, by + 20, br + 18, 20, 4, sid=35330, fill=(0.25, 0.25, 0.28))
    sk_ell(cr, bx, by + pr, br, br * 0.55, 5, sid=35331, fill=(0.88, 0.12, 0.12))
    # the stick
    sx, sy = CAPX + 230, CAP_B - 70
    tilt = 0.0
    if T_STICK <= t < CUT_IN3: tilt = 0.5 * smooth(ramp(t, T_STICK, T_STICK + 0.15))
    tx, ty = sx + 220 * math.sin(tilt), sy - 220 * math.cos(tilt)
    sketch_line(cr, [(sx, sy), (tx, ty)], 12, sid=35340, color=(0.15, 0.15, 0.18))
    sk_circ(cr, tx, ty, 26, 4, sid=35341, fill=(0.15, 0.15, 0.18))
    draw_window_view(cr, t)

def cap_rex_st(t):
    st = dict(O.DINO); st.update(s=RS, look=(-0.8, 0.3), smile=0.5, lid=0.0, mouth=0.0, arms=0.0, walk=0.0)
    jit = 0.0
    if t >= CUT_IN2 - FR:
        st["look"] = (-1.0, -0.4); st["smile"] = 0.4
    if T_PANIC <= t < T_CALM:
        st["pupil"] = 0.22; st["lid"] = 0.0; st["smile"] = -0.4; st["worry"] = 1.0; st["brow"] = 1.0; st["mouth"] = 0.12
        st["look"] = (-1.0, -0.5); jit = 1.0
        if t >= CUT_IN3 - FR: st["look"] = (-0.5, 0.0)
    if t >= T_CALM:
        st["eyes"] = "happy"; st["smile"] = 0.9; st["look"] = (-0.6, 0.2)
    if t >= T_CALM + 0.6 and t < CUT_APP: st["eyes"] = "normal"
    if t < CUT_IN2 - FR and t >= T_PRESS: st["look"] = (-1.0, -0.2); st["smile"] = 0.3; st["lid"] = 0.0
    return st, jit

CAP_HEAD = (CAPX - 300, 720)
def cap_rex_draw(cr, t):
    st, jit = cap_rex_st(t)
    pitch = 0.32
    hx0, hy0 = rex_world(0.0, 0.0, pitch, 1, -235, 930)
    jx = jit * 6 * math.sin(t * 55); jy = jit * 4 * math.sin(t * 43)
    X = CAP_HEAD[0] - hx0 + jx
    dy = CAP_HEAD[1] - hy0 + jy
    cr.save()
    cr.arc(CAPX - 470, 820, 290, 0, 2 * math.pi); cr.new_sub_path(); cr.rectangle(CAPX - 470, CAP_T, 450, 600); cr.clip()
    cr.translate(0, dy)
    O.draw_trex(cr, X, st, t, face=1, pitch=pitch)
    cr.restore()
    if jit > 0:
        for k in range(3):
            u = ((t - T_PANIC) * 1.6 + k / 3) % 1.0
            dx_, dy_ = CAP_HEAD[0] - 120 + 110 * k, CAP_HEAD[1] - 150 + 140 * u
            cr.move_to(dx_, dy_ - 26); cr.curve_to(dx_ + 16, dy_, dx_ + 14, dy_ + 16, dx_, dy_ + 16); cr.curve_to(dx_ - 14, dy_ + 16, dx_ - 16, dy_, dx_, dy_ - 26)
            cr.set_source_rgba(0.6, 0.85, 1.0, 1 - u); cr.fill_preserve(); cr.set_source_rgba(*INKC, 1 - u); cr.set_line_width(3); cr.stroke()
    fog = pulse(t, T_PANIC + 0.6, 0.4) + pulse(t, T_PANIC + 1.6, 0.4)
    helmet(cr, CAP_HEAD[0] + jx, CAP_HEAD[1] + jy, 300, fog=min(1.0, fog), sid=33020)

def draw_seat(cr, t, p):
    hx, hy = p["hip"]
    sk_poly(cr, [(hx - 150, hy + 40), (hx - 190, hy - 330), (hx - 120, hy - 340), (hx - 80, hy + 20)], 6, sid=35400, fill=(0.30, 0.32, 0.40))
    sk_rect(cr, hx - 150, hy + 15, hx + 140, hy + 75, 6, sid=35401, fill=(0.30, 0.32, 0.40))
    sketch_line(cr, [(hx, hy + 75), (hx, CAP_B - 60)], 16, sid=35402, color=(0.25, 0.25, 0.30))

def draw_belts(cr, t, p):
    n, h = p["neck"], p["hip"]
    sketch_line(cr, [(n[0] - 30, n[1] - 10), (h[0] + 40, h[1] - 20)], 9, sid=35410, color=(0.85, 0.55, 0.15))

# ================================================================ space shots
def draw_space_earth(cr, t):
    cx, cy, z = L.cam_track.at(t)
    stars(cr, t, 0, 60, n=110, seed=1)
    O.draw_space(cr, t, SPX, SPY + 9000 + 1300 + 400 * ramp(t, CUT_SPACE, CUT_IN2), R=9000.0)

def space_rocket(t):
    u = t - CUT_SPACE
    return SPX + 60 * u, SPY - 200 * u
def draw_space_rocket(cr, t):
    x, yb = space_rocket(t)
    fl = 1.0 - smooth(ramp(t, T_COAST, T_COAST + 0.4))
    draw_rocket(cr, x, yb + 1200, 0.15, flame=fl, t=t, flame_len=0.7)

def miss_rocket(t):
    u = ramp(t, CUT_MISS, CUT_IN3, "linear")
    dy = 380 * smooth(ramp(t, CUT_MISS, T_PASS0 + 0.2)) - 120 * smooth(ramp(t, T_PASS1, CUT_IN3))
    ang = math.pi / 2 + 0.35 * math.sin(math.pi * ramp(t, CUT_MISS, T_PASS1))
    return SPX2, SPY + dy, ang
def draw_miss(cr, t):
    stars(cr, t, -2600, 0, n=70, seed=2)
    x, y, ang = miss_rocket(t)
    draw_rocket(cr, x, y + 1200, ang, flame=0.8, t=t, flame_len=0.6)
    u = ramp(t, CUT_MISS, CUT_IN3, "linear")
    ax = lerp(SPX2 + 3000, SPX2 - 3400, smooth(ramp(t, CUT_MISS, CUT_IN3)) * 0.4 + 0.6 * ramp(t, T_PASS0 - 0.1, T_PASS1 + 0.2))
    ay = SPY - 380
    draw_asteroid(cr, ax, ay, 520, t, sid=35210)
    for k in range(5):
        sketch_line(cr, [(ax + 560 + 70 * k, ay - 300 + 140 * k), (ax + 1200 + 140 * k, ay - 300 + 140 * k)], 7, sid=35230 + k, color=(1, 1, 1), alpha=0.5)

def app_rocket(t):
    k = smooth(ramp(t, T_FLIP0, T_FLIP1))
    ang = math.pi * (1 - k)
    y = SPY - 300 + 500 * ramp(t, CUT_APP, CUT_LAND, "linear")
    return SPX3, y, ang
def draw_approach(cr, t):
    stars(cr, t, 0, -40, n=110, seed=3)
    draw_mars_planet(cr, SPX3 - 400, SPY + 8800 + 900 - 600 * ramp(t, CUT_APP, CUT_LAND), 8000)
    x, y, ang = app_rocket(t)
    fl = 0.0 if t < T_FLIP1 else 0.8
    draw_rocket(cr, x, y + 1200, ang, flame=fl, t=t, flame_len=0.7)

# ================================================================ world dispatcher
def world(cr, t):
    if t < CUT_LS - FR:
        E32.draw_outside(cr, t)
        mars_dot(cr, t)
        return
    if t < CUT_CAP - FR:
        draw_launch_site(cr, t)
        return
    if t < CUT_LAUNCH - FR:
        draw_capsule(cr, t); return
    if t < CUT_SPACE - FR:
        draw_launch_site(cr, t); sky_dark(cr, t); return
    if t < CUT_IN2 - FR:
        draw_space_earth(cr, t); return
    if t < CUT_MISS - FR:
        draw_capsule(cr, t); return
    if t < CUT_IN3 - FR:
        draw_miss(cr, t); return
    if t < CUT_APP - FR:
        draw_capsule(cr, t); return
    if t < CUT_LAND - FR:
        draw_approach(cr, t); return
    draw_mars(cr, t)

# ================================================================ poses
def P_(name, **kw): L.POSES[name] = kw
P_("helm_up", lelb=(450, 720), lhand=(470, 560), relb=(630, 720), rhand=(610, 560), lhand_t="open", rhand_t="open")
P_("helm_on", lelb=(440, 860), lhand=(445, 760), relb=(640, 860), rhand=(635, 760), lhand_t="open", rhand_t="open")
P_("big_up", lelb=(440, 700), lhand=(450, 520), relb=(640, 700), rhand=(630, 520), lhand_t="open", rhand_t="open")
P_("press", lknee=(620, 1235), lfoot=(600, 1360), rknee=(630, 1225), rfoot=(612, 1350),
   lelb=(590, 1010), lhand=(640, 1080), relb=(700, 1000), rhand=(800, 1060), lhand_t="fist", rhand_t="point", nowalk=1.0)
P_("stick", lknee=(620, 1235), lfoot=(600, 1360), rknee=(630, 1225), rfoot=(612, 1350),
   lelb=(590, 1010), lhand=(640, 1080), relb=(680, 1090), rhand=(760, 1200), lhand_t="fist", rhand_t="fist", nowalk=1.0)
P_("shade", lknee=(620, 1235), lfoot=(600, 1360), rknee=(630, 1225), rfoot=(612, 1350),
   lelb=(590, 1010), lhand=(640, 1080), relb=(720, 760), rhand=(860, 540), lhand_t="fist", rhand_t="fist", nowalk=1.0)
P_("pat", lknee=(620, 1235), lfoot=(600, 1360), rknee=(630, 1225), rfoot=(612, 1350),
   lelb=(430, 820), lhand=(330, 760), relb=(600, 1000), rhand=(660, 1060), lhand_t="flat", rhand_t="fist", nowalk=1.0)
P_("step_up", lknee=(610, 1280), lfoot=(590, 1310), lfoot_dir=0.3, nowalk=1.0)

# ================================================================ scene (him)
S = M.Scene(start_body="stand", start_face="deadpan", x0=AX - 540)
S.auto_blinks = True
S.floor = False
S.card("nicolascechettoschuller", "Go to mars", "0", t0=0.3)
CAM_A = cam(AX - 120, 0.62, fs=1640)
S.camkeys[0] = (0.0, CAM_A, 0); S.cam = CAM_A

# ---------------------------------------------------------------- A: the street
S.read_card(T_READ, react="deadpan", lines=1)
S.set(T_SKY, "stand", "deadpan", dur=0.3, look=(-0.6, -1.0), tilt=-0.08)
S.set(T_SKY + 0.4, "stand", "dead_stare", dur=0.3, look=(-0.6, -1.0), tilt=-0.10, lid=0.2)
S.sfx(T_SKY + 0.2, "twinkle", 0.03)
S.cut(CUT_RIDE - FR, cam=cam(X_STOP + 200, 0.50, fs=1660), x=AX - 540)
S.set(CUT_RIDE - FR, "ride", "deadpan", dur=0.0, turn=0.9, look=(1.0, 0.0))
S.set(T_REINS, "ride", "deadpan", dur=0.1, ease="snap", turn=0.9, look=(1.0, 0.0), lhand=(660, 1000), rhand=(665, 990))
S.sfx(T_REINS, "tap", 0.05)
S.sfx(T_BOLT, E32.ROAR_WAV, 0.12); S.sfx(T_BOLT + 0.1, "whoosh", 0.08)
S.set(T_BOLT + 0.05, "ride", "deadpan", dur=0.12, ease="snap", turn=0.9, look=(1.0, 0.0), lean=-0.2, curl_up=1.0)
S.set(T_BOLT + 0.5, "ride", "deadpan", dur=0.3, turn=0.9, look=(1.0, 0.0), lean=-0.05)
for k in range(4): S.sfx(T_BOLT + 0.2 + 0.3 * k, "thud", 0.07)

# ---------------------------------------------------------------- B: the launch site
CAM_LS = cam(LS - 150, 0.36, fs=1720)
S.cut(CUT_LS - FR, cam=CAM_LS, x=AX - 540)
S.set(CUT_LS - FR, "ride", "deadpan", dur=0.0, turn=0.9, look=(1.0, 0.0), lean=-0.05)
S.sfx(CUT_LS + 0.1, "skid", 0.12, dur=0.7)
S.set(CUT_LS + 0.15, "ride", "dead_stare", dur=0.15, turn=0.9, look=(1.0, 0.0), lean=0.25)
S.set(T_SKID1, "ride", "dead_stare", dur=0.3, turn=0.9, look=(1.0, 0.0), lid=0.3)
S.set(T_UP, "ride", "dead_stare", dur=0.5, turn=0.6, look=(0.6, -1.0), tilt=-0.12, lid=0.15)
S.camera(T_UP, *cam(LS + 200, 0.33, fs=1780), 0.8)
for k in range(int(T_PRESS - CUT_LS)):
    tt = T_PRESS - 1 - k
    if CUT_LS < tt < CUT_CAP and not (CUT_CAP - FR <= tt): S.sfx(tt, "tick", 0.025)
# standing next to it
CAM_ST = cam(LS - 420, 0.50, fs=1650)
S.cut(CUT_STAND - FR, cam=CAM_ST, x=HIM_LS - 540)
S.set(CUT_STAND - FR, "stand", "deadpan", dur=0.0, turn=0.4, look=(0.8, -0.3))
S.set(T_BOARD1, "stand", "dead_stare", dur=0.25, turn=0.4, look=(1.0, -0.2), lid=0.25)
S.pocket_pull(T_HELM, "helm", lambda cr, x, y, s, t, p: my_helmet_held(cr, x, y, s, t, p), (0, 0), held=True)
S.set(POP_HELM + 0.1, "stand", "deadpan", dur=0.3, look=(0.3, -0.6))
S.set(T_HUP, "helm_up", "deadpan", dur=0.35, look=(0.0, -1.0))
S.set(T_HON - 0.2, "helm_on", "deadpan", dur=0.2, look=(0.0, 0.0))
S.sfx(T_HON, "tok", 0.07)
S.set(T_HON + 0.25, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), lid=0.3)
S.set(T_REXLOOK, "stand", "dead_stare", dur=0.35, turn=-0.5, look=(-1.0, -0.5), lid=0.3)
S.pocket_pull(T_HELM2, "helm2", lambda cr, x, y, s, t, p: big_helmet_held(cr, x, y, s, t, p), (0, 0), held=True, narrow_w=150)
S.set(POP_HELM2 + 0.05, "big_up", "deadpan", dur=0.3, turn=-0.3, look=(-0.6, -0.8))
S.sfx(POP_HELM2 + 0.1, "rummage", 0.03, dur=0.3)
# the rex in its helmet
S.cut(CUT_RH - FR, cam=cam(LS - 470, 0.48, fs=1650), x=HIM_LS - 540)
S.set(CUT_RH - FR, "stand", "dead_stare", dur=0.0, turn=-0.5, look=(-1.0, -0.6), lid=0.3)
S.sfx(T_FOG + 0.4, "whoosh", 0.03, dur=0.4)
S.set(T_BOARD2, "stand", "dead_stare", dur=0.2, ease="snap", turn=0.6, look=(1.0, 0.0), lid=0.0, eyescale=1.2)
S.sfx(T_BOARD2, "boop", 0.04)

# ---------------------------------------------------------------- C: the capsule
CAM_CAP = (CAPX + 150, 1020, 0.90)
S.cut(CUT_CAP - FR, cam=CAM_CAP, x=HIM_CAP)
S.set(CUT_CAP - FR, "ride", "deadpan", dur=0.0, turn=0.9, look=(1.0, -0.2))
for k, tn in enumerate(T_N):
    S.sfx(tn, "boop", 0.05)
S.set(T_N[0] + 0.2, "ride", "dead_stare", dur=0.3, turn=0.9, look=(1.0, -0.1), lid=0.3)
S.set(T_N[1] + 0.2, "press", "dead_stare", dur=0.5, turn=0.9, look=(1.0, 0.4), lid=0.3)
S.set(T_PRESS - 0.1, "press", "dead_stare", dur=0.1, ease="snap", turn=0.9, look=(1.0, 0.5), lid=0.3, rhand=(820, 1110))
S.sfx(T_PRESS, "tap", 0.07)
S.camera(T_N[0], CAPX + 200, 1030, 0.98, 2.4)

# ---------------------------------------------------------------- D: liftoff
CAM_L = cam(RKX, 0.30, fs=1780)
S.cut(CUT_LAUNCH - FR, cam=CAM_L, x=HIM_CAP)
S.set(CUT_LAUNCH - FR, "stand", "deadpan", dur=0.0, show=0.0, nowalk=1.0)
S.sfx(CUT_LAUNCH, "kaboom", 0.5); S.shake(CUT_LAUNCH, 3.6, 14)
S.sfx(CUT_LAUNCH + 0.3, "wind", 0.08, dur=3.2)
_ck = []
t_ = T_LIFT + 0.4
while t_ < CUT_SPACE:
    rise = rocket_rise(t_)
    _ck.append((t_, (RKX, min(FLOOR_Y - (1780 - 960) / 0.30, FLOOR_Y - PAD_H - rise - 900), 0.30), 0.1, "linear"))
    t_ += 0.1
S.camkeys += _ck

# ---------------------------------------------------------------- space (Earth)
S.cut(CUT_SPACE - FR, cam=(SPX, SPY - 300, 0.40), x=HIM_CAP)
S.camera(CUT_SPACE, SPX + 60, SPY - 500, 0.38, 1.4)

# ---------------------------------------------------------------- inside again: the asteroid
S.cut(CUT_IN2 - FR, cam=(CAPX + 150, 1020, 0.90), x=HIM_CAP)
S.set(CUT_IN2 - FR, "ride", "deadpan", dur=0.0, turn=0.9, look=(0.9, -0.7), lid=0.3)
S.set(T_AST0 + 0.4, "ride", "dead_stare", dur=0.3, turn=0.9, look=(0.9, -0.8), lid=0.2)
for k in range(8): S.sfx(T_PANIC + 0.2 + 0.32 * k, "thud", 0.08); S.sfx(T_PANIC + 0.34 + 0.32 * k, "thud", 0.045)
S.set(T_LOOKREX, "ride", "dead_stare", dur=0.25, turn=0.9, look=(-1.0, -0.5), lid=0.2)
S.set(T_LOOKREX + 0.25, "ride", "dead_stare", dur=0.3, turn=-0.4, look=(-1.0, -0.5), lid=0.25)
S.set(T_LOOKAST, "ride", "dead_stare", dur=0.15, turn=0.9, look=(0.9, -0.8), lid=0.0, eyescale=1.2)
S.camera(T_AST0, CAPX + 10, 980, 0.95, 2.8)
S.set(T_STICK - 0.1, "stick", "dead_stare", dur=0.1, ease="snap", turn=0.9, look=(0.9, -0.8), lid=0.0, eyescale=1.2)
S.sfx(T_STICK, "clack", 0.06)
# the near miss outside
S.cut(CUT_MISS - FR, cam=(SPX2, SPY - 100, 0.36), x=HIM_CAP)
S.sfx(T_PASS0 + 0.2, "whoosh", 0.12, dur=0.8)
# inside: the shade, the pat
S.cut(CUT_IN3 - FR, cam=(CAPX + 150, 1020, 0.90), x=HIM_CAP)
S.set(CUT_IN3 - FR, "stick", "dead_stare", dur=0.0, turn=0.9, look=(0.9, -0.8), lid=0.2)
S.set(T_SHADE0 - 0.2, "shade", "dead_stare", dur=0.2, turn=0.9, look=(0.9, -0.8), lid=0.3)
S.sfx(T_SHADE0 + 0.05, "flip", 0.06)
S.set(T_SHADE1 + 0.1, "ride", "dead_stare", dur=0.25, turn=-0.5, look=(-1.0, -0.4), lid=0.3)
S.set(T_PAT[0] - 0.2, "pat", "dead_stare", dur=0.2, turn=-0.7, look=(-1.0, -0.5), lid=0.3)
for tp in T_PAT: S.sfx(tp, "tok", 0.05)
S.set(T_CALM, "pat", "deadpan", dur=0.3, turn=-0.7, look=(-1.0, -0.5), lid=0.3, smile=0.15)
S.set(T_CALM + 0.4, "ride", "deadpan", dur=0.3, turn=0.9, look=(1.0, 0.0), lid=0.3)

# ---------------------------------------------------------------- arriving at Mars
S.cut(CUT_APP - FR, cam=(SPX3, SPY - 200, 0.36), x=HIM_CAP)
S.set(CUT_APP - FR, "stand", "deadpan", dur=0.0, show=0.0, nowalk=1.0)
S.sfx(T_FLIP1, "whine", 0.03, dur=0.6)

# ---------------------------------------------------------------- landing
S.cut(CUT_LAND - FR, cam=cam(RKM - 150, 0.33, fs=1750), x=HIM_M - 540)
for ts in T_SPUT: S.sfx(ts, "poof", 0.06)
S.sfx(T_SLAM, "kaboom", 0.5); S.shake(T_SLAM, 1.0, 30)

# ---------------------------------------------------------------- one small step
S.cut(CUT_STEP - FR, cam=(HIM_M + 60, FLOOR_Y - 50, 1.7), x=HIM_M - 540)
S.set(CUT_STEP - FR, "step_up", "deadpan", dur=0.0, nowalk=1.0)
S.set(T_FOOT0, "stand", "deadpan", dur=T_FOOT1 - T_FOOT0, ease="smooth", nowalk=1.0)
S.sfx(T_FOOT1, "tap", 0.05)
S.cut(T_PULLBACK - FR, cam=cam(MRS + 1450, 0.37, fs=1720))
S.set(T_PULLBACK, "stand", "deadpan", dur=0.3, turn=0.0, look=(0.0, 0.0))
S.walk_to(T_PULLBACK - 0.45, HF - 540, dur=0.55)
S.set(T_PULLBACK + 0.4, "stand", "dead_stare", dur=0.3, turn=0.3, look=(0.0, 0.8), lid=0.3)
S.set(T_REXJUMP, "stand", "dead_stare", dur=0.25, turn=0.5, look=(1.0, -0.4), lid=0.2)
S.sfx(T_REXLAND, "thud", 0.22); S.shake(T_REXLAND, 0.4, 14)
S.set(T_REXLAND + 0.3, "stand", "dead_stare", dur=0.3, turn=0.5, look=(0.7, 0.9), lid=0.3)
S.set(T_REXLAND + 0.9, "stand", "dead_stare", dur=0.3, turn=0.3, look=(-0.4, 0.9), lid=0.35)
S.set(T_HOP0 - 0.2, "stand", "dead_stare", dur=0.3, turn=0.4, look=(1.0, 0.0), lid=0.3)
S.sfx(T_HOP0, "boing", 0.05)
S.set(T_HOP0 + 0.4, "stand", "dead_stare", dur=0.8, turn=0.4, look=(0.8, -1.0), tilt=-0.1, lid=0.2)
S.camera(T_HOP0 + 0.2, *cam(MRS + 1250, 0.35, fs=1760), 1.0)
S.set(T_HOP0 + 1.4, "stand", "dead_stare", dur=1.0, turn=0.4, look=(0.8, -1.0), tilt=-0.14, lid=0.15)
S.set(T_HOP1 - 0.9, "stand", "dead_stare", dur=0.8, turn=0.4, look=(0.8, -0.2), tilt=-0.04, lid=0.2)
S.sfx(T_HOP1, "thud", 0.08)
S.camera(T_HOP1 + 0.1, *cam(MRS + 1100, 0.45, fs=1690), 1.0)
S.set(T_HOP1 + 0.3, "stand", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lid=0.35)
S.sfx(T_ROV0, "whine", 0.02, dur=1.1)
S.set(T_ROV1 - 0.3, "stand", "dead_stare", dur=0.35, turn=0.5, look=(1.0, 0.1), lid=0.3)
S.sfx(T_SNIFF, "whoosh", 0.04, dur=0.25); S.sfx(T_SNIFF + 0.3, "whoosh", 0.04, dur=0.25)

def _write_wav(path, sig, sr=48000):
    sig = np.clip(sig, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((sig * 32767).astype(np.int16).tobytes())
TUNE_WAV = os.path.join(HERE, "rover_tune.wav")
def make_tune():
    sr = 48000
    notes = [(392, 0.16), (392, 0.10), (440, 0.28), (392, 0.28), (523, 0.28), (494, 0.5)]     # public-domain birthday tune
    out = []
    for f, d in notes:
        tt = np.arange(int(d * sr)) / sr
        sq = np.sign(np.sin(2 * np.pi * f * tt)) * 0.5 + 0.5 * np.sin(2 * np.pi * f * tt)
        env = np.clip(tt / 0.01, 0, 1) * np.clip((d - tt) / 0.04, 0, 1)
        out.append(sq * env * 0.6); out.append(np.zeros(int(0.04 * sr)))
    _write_wav(TUNE_WAV, np.concatenate(out))
if not os.path.exists(TUNE_WAV): make_tune()
S.sfx(T_SING0, TUNE_WAV, 0.05)
S.set(T_SING0 + 0.3, "stand", "dead_stare", dur=0.4, turn=0.5, look=(1.0, -0.2), lid=0.4)
S.sfx(T_ARM0, "whine", 0.02, dur=0.5)
S.set(T_SELFIE - 0.5, "stand", "dead_stare", dur=0.3, turn=0.6, look=(1.0, -0.6), lid=0.3)
S.flash(T_SELFIE, 0.35); S.sfx(T_SELFIE, "tick", 0.08)
S.set(T_SELFIE + 0.4, "stand", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lid=0.35)

# ---------------------------------------------------------------- the ask (on Mars)
S.x = HF - 540
S.camera(T_ASK - 0.6, *cam(S.x + 540 + 300, 0.58, fs=1650), 1.0)
S.the_ask(T_ASK, hold=HOLD, push=False)
S.camera(T_ASK + 6.9, *cam(S.x + 540 + 260, 0.62, fs=1650), 5.0)
T_END = S.t
S.blink(3.6, 8.4, 11.9, 19.0, 24.0, 31.5, 37.5, 41.5)

# camera follow during the gallops
_ck = []
t_ = T_BOLT
while t_ < CUT_LS - FR:
    X, lift, pitch, face, st = rex(t_)
    _ck.append((t_, cam(X + 250, 0.50, fs=1660), 0.1, "linear")); t_ += 0.1
t_ = CUT_LS
while t_ < T_SKID1 + 0.05:
    X, lift, pitch, face, st = rex(t_)
    _ck.append((t_, cam(max(X + 900, LS - 150), 0.36, fs=1720), 0.1, "linear")); t_ += 0.1
S.camkeys += _ck
S.camkeys.sort(key=lambda k: k[0])

# ---------------------------------------------------------------- hooks
def ride_hook(t, p):
    if CUT_RIDE - FR <= t < CUT_STAND - FR:
        sx, sy = seat(t)
        hx, hy = p["hip"]
        dx, dy = sx - hx, sy - 30 - hy
        for k in L.JOINTS:
            p[k] = (p[k][0] + dx, p[k][1] + dy)
    if (CUT_IN3 - FR <= t < CUT_APP) and t >= T_PAT[0] - 0.2:
        # the pats land on the rex's helmet
        hx, hy = CAP_HEAD
        tx, ty = hx + 290, hy - 60
        k = ramp(t, T_PAT[0] - 0.2, T_PAT[0])
        bob = 0.0
        for tp in T_PAT: bob += 30 * pulse(t, tp - 0.1, 0.1)
        p["lhand"] = lerp(p["lhand"], (tx, ty - bob), k)
        p["lelb"] = lerp(p["lelb"], ((p["neck"][0] + tx) / 2, (p["neck"][1] + ty) / 2 + 40), k)
    if CUT_IN2 - FR <= t < CUT_MISS and t >= T_STICK - 0.1:
        sx, sy = CAPX + 230, CAP_B - 70
        tx, ty = sx + 220 * math.sin(0.5), sy - 220 * math.cos(0.5)
        p["rhand"] = (tx, ty); p["relb"] = ((p["neck"][0] + tx) / 2 + 20, (p["neck"][1] + ty) / 2 + 60)
    if CUT_IN3 - FR <= t < T_SHADE0 - 0.2:
        sx, sy = CAPX + 230, CAP_B - 70
        tx, ty = sx + 220 * math.sin(0.5), sy - 220 * math.cos(0.5)
        p["rhand"] = (tx, ty); p["relb"] = ((p["neck"][0] + tx) / 2 + 20, (p["neck"][1] + ty) / 2 + 60)
    if CUT_IN3 - FR <= t < CUT_APP and T_SHADE0 <= t < T_SHADE1 + 0.1:
        wx, wy, wr = WIN
        k = smooth(ramp(t, T_SHADE0, T_SHADE1))
        tx, ty = wx, wy - wr + 2 * wr * k
        p["rhand"] = (tx, ty); p["relb"] = ((p["neck"][0] + tx) / 2 + 30, (p["neck"][1] + ty) / 2 + 80)
    if CUT_CAP - FR <= t < CUT_LAUNCH and t >= T_N[1] + 0.2:
        bx, by, br = BUTTON
        k = smooth(ramp(t, T_N[1] + 0.2, T_N[1] + 0.7))
        hover = (bx, by - 80) if t < T_PRESS - 0.1 else (bx, by - 22)
        p["rhand"] = lerp(p["rhand"], hover, k); p["rhand_t"] = "point"
        p["relb"] = lerp(p["relb"], ((p["neck"][0] + hover[0]) / 2 + 10, (p["neck"][1] + hover[1]) / 2 + 70), k)
    return p
S.hook(ride_hook)

# ---------------------------------------------------------------- helmets
def my_helmet_on(t): return t >= T_HON
def my_helmet_held(cr, x, y, s, t, p):
    if my_helmet_on(t): return
    if t >= T_HUP:
        mx = (p["lhand"][0] + p["rhand"][0]) / 2; my = (p["lhand"][1] + p["rhand"][1]) / 2
        helmet(cr, mx, my - 110, 175, sid=33000)
    else:
        helmet(cr, x, y - 150, 175, sid=33000)
def draw_my_helmet(cr, t, p):
    if not my_helmet_on(t): return
    if CUT_LAUNCH - FR <= t < CUT_IN2 - FR or CUT_MISS - FR <= t < CUT_IN3 - FR or CUT_APP - FR <= t < CUT_STEP - FR: return
    if p.get("show", 1.0) < 0.5: return
    hx, hy = p["head"]
    helmet(cr, hx + 6, hy - 10, 175, sid=33000)

def big_helmet_held(cr, x, y, s, t, p):
    if t >= CUT_RH - FR: return
    if t >= POP_HELM2 + 0.1:
        mx = (p["lhand"][0] + p["rhand"][0]) / 2; my = (p["lhand"][1] + p["rhand"][1]) / 2
        helmet(cr, mx, my - 250, 300, sid=33020)
    else:
        helmet(cr, x, y - 300, 300, sid=33020)

# ---------------------------------------------------------------- draw order
def props_back(cr, t, p, ly):
    if ly != "back": return
    if t < CUT_LS - FR:
        E32.draw_light(cr, 60.0)
        draw_rex(cr, t)
        return
    if t < CUT_CAP - FR:
        draw_board(cr, t)
        draw_launch(cr, t)
        draw_rex(cr, t)
        return
    if t < CUT_LAUNCH - FR or (CUT_IN2 - FR <= t < CUT_MISS - FR) or (CUT_IN3 - FR <= t < CUT_APP - FR):
        cap_rex_draw(cr, t)
        draw_seat(cr, t, p)
        return
    if t < CUT_SPACE - FR:
        draw_launch(cr, t)
        draw_launch_smoke(cr, t)
        return
    if t < CUT_IN2 - FR:
        draw_space_rocket(cr, t); return
    if t < CUT_LAND - FR:
        return
    draw_prints(cr, t)
    draw_mars_rocket(cr, t)
    draw_rex(cr, t)
    draw_rover(cr, t)
S.prop(props_back)
S.background(world)

def props_front(cr, t, p, ly):
    if ly != "front": return
    if t < CUT_LS - FR:
        E32.draw_pters(cr, 60.0 + t)
        E31.draw_fog(cr, FOG_S, t, sid=33990)
    if CUT_LS - FR <= t < CUT_STAND:
        E31.draw_fog(cr, FOG_L, t, sid=33995)
    draw_reins(cr, t, p)
    draw_my_helmet(cr, t, p)
    if CUT_CAP - FR <= t < CUT_LAUNCH - FR or (CUT_IN2 - FR <= t < CUT_MISS - FR) or (CUT_IN3 - FR <= t < CUT_APP - FR):
        draw_belts(cr, t, p)
    if t >= CUT_LAND - FR:
        draw_dust(cr, t)
        draw_dust_haze(cr, t)
S.prop(props_front)

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        import cairo
        S.build()
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, L.W, L.H)
        for a in sys.argv[2:]:
            tt = float(a); L.render_frame(tt, surf); surf.write_to_png(os.path.join(HERE, "still_%05.2f.png" % tt))
        print("dur", T_END)
    else:
        S.render("day033.mp4")
