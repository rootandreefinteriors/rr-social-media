"""Day 36: IG @nicolascechettoschuller: "Try find extraterrestrial life". See BEATS.md.
At Cydonia there's nothing alive. The rover points right; he rides Jerry through a dust devil into JEZERO CRATER (the old lake bed).
A magnifying glass (a rock: nothing), the rover's drill (dust) - while little green heads peek over the ridge behind him and duck every
time he turns. Jerry can't warn him (tiny arms). A giant radio dish prints 6EQUJ5 - Wow! - the aliens tiptoe up and tap his shoulder.
TAKE ME TO YOUR LEADER: he points at Jerry. The alien calls the mothership: a beam takes him up, a giant eye studies him through a giant
magnifying glass, BZZT, he's dropped. The ship leaves. A sign lands next to him: NO INTELLIGENT LIFE FOUND. The ask at Jezero.
"""
import sys, os, math, random
import importlib.util
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
import character as C
import cairo
from ltcd import ramp, lerp, pulse, FLOOR_Y
from ink import smooth, sketch_line, draw_text

_RF = L.render_frame
_spec = importlib.util.spec_from_file_location("ep035_episode", os.path.join(HERE, "..", "ep035", "episode.py"))
E35 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(E35)
L.render_frame = _RF                       # day 35 patched it for its photo; not ours
E34, E33, E32 = E35.E34, E35.E33, E35.E32

FR = 1 / 30
sk_rect, sk_poly, sk_circ, sk_ell = O.sketch_rect, O.sketch_poly, O.sketch_circle, O.sketch_ellipse
INKC = (0.07, 0.07, 0.09)
RS = E33.RS
cam = E33.cam
rex_world = E33.rex_world
helmet = E33.helmet

# ================================================================ places
CY = E35.CY
HC = CY - 220.0                   # him at Cydonia (day 35 ask)
REX_C = E35.REX_C
ROV_C = HC + 650.0                 # the rover at Cydonia (moved right of him, faces right)
DD2 = CY + 2900.0                 # the dust devil (border)
JZ = 14600000.0                   # JEZERO CRATER: him
REX_J = JZ - 1000.0               # Jerry (near foot), facing right
ROV_J = JZ + 1250.0               # the rover (faces left)
ROCK_X = JZ + 330.0
DISH_X = JZ - 560.0
PRX = DISH_X + 250.0              # the dish's printer
SIGN_X = JZ + 600.0               # NO INTELLIGENT LIFE FOUND
JSIGN = JZ - 2000.0               # the JEZERO CRATER sign
GLASS_REST = (JZ + 170.0, FLOOR_Y - 18)
STRIP_REST = (JZ - 150.0, FLOOR_Y - 10)
SHIP_X = JZ + 300.0
SHIP_R = 2200.0
SHIP_Y1 = FLOOR_Y - 4700.0
LIFT = 3200.0

# ================================================================ timeline
T_READ = 0.3
T_LOOKL, T_LOOKR = 1.8, 2.2
T_ROV = 2.6; T_LOOKROV = 2.75; T_LOOKR2 = 3.1
CUT_RIDE = 3.5; T_BOLT = 3.65
CUT_JZ = 5.5; T_STOPJ = 6.3
CUT_STAND = 7.0
T_GLASS = 7.2; POP_GLASS = T_GLASS + 2.1
CUT_ROCK = 9.8; T_FLIP0, T_FLIP1 = 10.7, 11.05; T_EBLINK = 11.4
CUT_PEEK = 11.8; T_P1UP0, T_P1UP1 = 12.0, 12.6; T_TURN1 = 13.0; T_DUCK1 = 12.95; T_BACK1 = 13.75
T_ROVIN0, T_ROVIN1 = 13.9, 14.5; T_DRILL0, T_DRILL1 = 14.6, 15.6; T_CUP0, T_CUP1 = 15.6, 16.0; T_SAD = 16.6; T_CUPDN = 17.0
T_P2UP0, T_P2UP1 = 15.0, 15.8
T_JSEE = 16.4
CUT_JERRY = 17.0; T_TAP0, T_TAP1 = 17.15, 18.1; T_TURNJ = 18.0; T_DUCK2 = 17.85
T_CHIN = 18.4; T_LOOKRIDGE = 18.65; T_BACK2 = 19.1
T_GDROP = 19.35; T_GLAND = 19.65
T_DISH = 19.8; POP_DISH = T_DISH + 2.1
CUT_WOW = 22.5; T_PRINT0, T_PRINT1 = 22.65, 23.45; T_CIRC0, T_CIRC1 = 23.55, 23.95; T_WOW0, T_WOW1 = 24.0, 24.4
CUT_BEHIND = 24.6; T_SNEAK0, T_SNEAK1 = 24.75, 26.35; T_TAP = 26.55
CUT_FACE2 = 26.9; T_TURNF = 26.95; T_TWITCH = 27.7; T_SDROP = 27.45; T_SLAND = 27.8
T_SIGN0, T_SIGN1 = 28.15, 28.45; T_POINT = 28.95
CUT_LEADER = 29.6; T_RISE = 29.7
CUT_ALIEN = 30.6; T_ALOOK = 30.65; T_ABACK = 30.95; T_REMOTE = 31.1; T_PRESS = 31.25
T_HUM = 31.4
CUT_SHIP = 31.9; T_SHIP1 = 34.0
T_BEAM = 34.2; T_AUP0, T_AUP1 = 34.3, 35.3; T_HUP0, T_HUP1 = 34.55, 36.3
CUT_RISE = 35.0
CUT_EXAM = 36.4; T_LENS0, T_LENS1 = 36.5, 36.9; T_SCAN0, T_SCAN1 = 37.0, 37.85; T_SQUINT = 37.95; T_BZZT = 38.25; T_LENSOUT = 38.45
CUT_FALL = 38.8; T_LAND = 39.5
T_LEAVE = 40.05
CUT_SIGNC = 40.9; T_SF0, T_SF1 = 41.0, 41.5
T_LOOKSIGN = 41.95; T_LOOKUS = 42.7
CUT_STAND2 = 43.3
T_ASK = 43.6; HOLD = 10.5

# ================================================================ sounds made for this episode
SR = 44100
HUM_WAV = os.path.join(HERE, "ufo_hum.wav")
SCAN_WAV = os.path.join(HERE, "scan.wav")
def make_hum():
    """the mothership: a deep wobbling drone that swells."""
    dur = 3.2; tt = np.arange(int(dur * SR)) / SR
    f = 52 + 3 * np.sin(2 * np.pi * 0.7 * tt)
    ph = np.cumsum(f) / SR * 2 * np.pi
    s = np.sin(ph) + 0.5 * np.sin(2 * ph + 0.3) + 0.25 * np.sin(3 * ph) + 0.18 * np.sin(2 * np.pi * 330 * tt + 2 * np.sin(2 * np.pi * 5 * tt))
    s *= (1 + 0.3 * np.sin(2 * np.pi * 6 * tt))
    env = np.clip(tt / 1.2, 0, 1) * np.clip((dur - tt) / 0.5, 0, 1)
    s = s * env; s /= np.abs(s).max() + 1e-9
    E35._write_wav(HUM_WAV, s * 0.9)
def make_scan():
    """the scanner: a soft rising sci-fi warble."""
    dur = T_SCAN1 - T_SCAN0; tt = np.arange(int(dur * SR)) / SR
    f = 600 + 500 * tt / dur + 120 * np.sin(2 * np.pi * 14 * tt)
    s = np.sin(np.cumsum(f) / SR * 2 * np.pi) * np.clip(tt / 0.05, 0, 1) * np.clip((dur - tt) / 0.08, 0, 1)
    E35._write_wav(SCAN_WAV, s * 0.5)
if not os.path.exists(HUM_WAV): make_hum()
if not os.path.exists(SCAN_WAV): make_scan()

# ================================================================ things
GREEN = (0.58, 0.84, 0.44)
GREEN_D = (0.40, 0.66, 0.30)

def alien(cr, x, yf, s=1.0, look=(0.0, 0.0), arm=0.0, reach=None, blink=0.0, sid=37000, bob=0.0, squint=0.0, both_up=0.0):
    """a little green man, feet at (x, yf). arm: right arm raised 0..1 (or reach=(x, y) world target); both_up: holds a sign up."""
    yf = yf - bob
    for d in (-1, 1):                                                     # legs + feet
        sketch_line(cr, [(x + d * 24 * s, yf - 100 * s), (x + d * 30 * s, yf - 14 * s)], 9 * s, sid=sid + (d > 0), amp=0.2)
        sk_ell(cr, x + d * 40 * s, yf - 10 * s, 28 * s, 13 * s, 4 * s, sid=sid + 2 + (d > 0), fill=GREEN)
    sh_l, sh_r = (x - 46 * s, yf - 215 * s), (x + 46 * s, yf - 215 * s)
    # arms
    if both_up > 0.01:
        hl = (lerp(x - 80 * s, x - 70 * s, both_up), lerp(yf - 110 * s, yf - 420 * s, both_up))
        hr = (lerp(x + 80 * s, x + 70 * s, both_up), lerp(yf - 110 * s, yf - 420 * s, both_up))
    else:
        hl = (x - 80 * s, yf - 110 * s)
        hr = reach if reach is not None else (lerp(x + 80 * s, x + 120 * s, arm), lerp(yf - 110 * s, yf - 360 * s, arm))
    for k, (a, b) in enumerate(((sh_l, hl), (sh_r, hr))):
        m = ((a[0] + b[0]) / 2 + (-1 if k == 0 else 1) * 18 * s, (a[1] + b[1]) / 2 + 10 * s)
        sketch_line(cr, [a, m, b], 8 * s, sid=sid + 4 + k, amp=0.2)
        sk_circ(cr, b[0], b[1], 15 * s, 3 * s, sid=sid + 6 + k, fill=GREEN)
    sk_ell(cr, x, yf - 165 * s, 58 * s, 80 * s, 5 * s, sid=sid + 8, fill=GREEN)        # body
    sketch_line(cr, [(x, yf - 240 * s), (x, yf - 262 * s)], 10 * s, sid=sid + 9, amp=0.1)
    hx, hy = x, yf - 345 * s
    for d in (-1, 1):                                                     # antennae
        tip = (hx + d * 62 * s, hy - 150 * s)
        sketch_line(cr, [(hx + d * 28 * s, hy - 82 * s), (hx + d * 48 * s, hy - 120 * s), tip], 5 * s, sid=sid + 10 + (d > 0), amp=0.2)
        sk_circ(cr, tip[0], tip[1], 14 * s, 3 * s, sid=sid + 12 + (d > 0), fill=GREEN)
    # head: big at the top, narrow chin
    pts = []
    for i in range(37):
        a = 2 * math.pi * i / 36
        rx = 95 * s * (1.0 if math.sin(a) < 0 else 1.0 - 0.38 * math.sin(a))
        pts.append((hx + rx * math.cos(a), hy + (98 if math.sin(a) > 0 else 92) * s * math.sin(a)))
    sk_poly(cr, pts, 5 * s, sid=sid + 14, fill=GREEN)
    # eyes: big black almonds
    for d in (-1, 1):
        ex, ey = hx + d * 42 * s + look[0] * 6 * s, hy - 4 * s + look[1] * 5 * s
        ry = 22 * s * max(0.06, 1 - blink) * (1 - 0.6 * squint)
        cr.save(); cr.translate(ex, ey); cr.rotate(d * 0.5); cr.scale(36 * s, ry); cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore()
        cr.set_source_rgb(0.04, 0.05, 0.06); cr.fill()
        if blink < 0.5:
            cr.arc(ex - 10 * s + look[0] * 6 * s, ey - 7 * s, 7 * s, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.9); cr.fill()
    sketch_line(cr, [(hx - 12 * s, hy + 56 * s), (hx + 12 * s, hy + 56 * s)], 3 * s, sid=sid + 16, amp=0.1)

def mothership(cr, x, y, R=SHIP_R, t=0.0, sid=37100):
    """the giant saucer, centre (x, y)."""
    # under-glow
    cr.save(); cr.translate(x, y + 0.17 * R); cr.scale(0.34 * R, 0.07 * R); cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore()
    cr.set_source_rgba(0.75, 1.0, 0.70, 0.85); cr.fill()
    sk_ell(cr, x, y + 0.05 * R, R, 0.17 * R, 12, sid=sid, fill=(0.45, 0.47, 0.53))           # lower hull
    sk_ell(cr, x, y - 0.03 * R, 0.96 * R, 0.13 * R, 9, sid=sid + 1, fill=(0.70, 0.72, 0.78))  # upper hull
    # dome
    cr.save(); cr.rectangle(x - R, y - 0.6 * R, 2 * R, 0.55 * R); cr.clip()
    sk_ell(cr, x, y - 0.06 * R, 0.42 * R, 0.30 * R, 9, sid=sid + 2, fill=(0.72, 0.93, 0.78))
    cr.arc(x - 0.2 * R, y - 0.2 * R, 0.08 * R, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.6); cr.fill()
    cr.restore()
    sk_ell(cr, x, y - 0.06 * R, 0.44 * R, 0.06 * R, 7, sid=sid + 3, fill=(0.55, 0.57, 0.63))
    # rim lights, chasing
    n = 14
    for k in range(n):
        a = math.pi * (0.06 + 0.88 * k / (n - 1))
        lx, ly = x - math.cos(a) * 0.9 * R, y + 0.07 * R + math.sin(a) * 0.08 * R
        on = (int(t * 8) - k) % 4 == 0
        col = (1.0, 0.92, 0.35) if on else (0.85, 0.35, 0.30)
        sk_circ(cr, lx, ly, 0.035 * R, 4, sid=sid + 10 + k % 5, fill=col)

def beam(cr, xt, yt, xb, yb, wt, wb, a=1.0, t=0.0):
    if wt < 2 or wb < 2: return
    cr.move_to(xt - wt / 2, yt); cr.line_to(xt + wt / 2, yt); cr.line_to(xb + wb / 2, yb); cr.line_to(xb - wb / 2, yb); cr.close_path()
    cr.set_source_rgba(0.78, 1.0, 0.72, 0.38 * a); cr.fill()
    for k in range(9):
        u = ((k / 9) + t * 0.9) % 1.0
        y = lerp(yt, yb, u); w = lerp(wt, wb, u)
        x = lerp(xt, xb, u)
        cr.save(); cr.translate(x, y); cr.scale(w / 2, w * 0.06); cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore()
        cr.set_source_rgba(0.55, 0.95, 0.5, 0.5 * a * math.sin(math.pi * u)); cr.set_line_width(6); cr.stroke()

def magnifier(cr, x, y, r, ang=0.8, sid=37200, inside=None):
    """lens centre (x, y), handle pointing at angle ang (rad, 0 = right, pi/2 = down)."""
    hx0, hy0 = x + math.cos(ang) * r * 1.08, y + math.sin(ang) * r * 1.08
    hx1, hy1 = x + math.cos(ang) * r * 2.1, y + math.sin(ang) * r * 2.1
    sketch_line(cr, [(hx0, hy0), (hx1, hy1)], max(6, r * 0.22), sid=sid, amp=0.2, color=(0.35, 0.2, 0.1))
    cr.arc(x, y, r, 0, 2 * math.pi); cr.set_source_rgba(0.82, 0.93, 1.0, 0.35); cr.fill()
    if inside:
        cr.save(); cr.arc(x, y, r, 0, 2 * math.pi); cr.clip(); inside(cr); cr.restore()
    cr.arc(x - r * 0.3, y - r * 0.3, r * 0.45, math.pi * 1.0, math.pi * 1.45); cr.set_source_rgba(1, 1, 1, 0.8)
    cr.set_line_width(max(3, r * 0.08)); cr.stroke()
    sk_circ(cr, x, y, r, max(5, r * 0.13), sid=sid + 1, fill=None)

def rock(cr, x, flip=0.0, sid=37300):
    """a lumpy rock sitting on the ground centred at x; flip 0..1 rolls it over to the right (underside shows)."""
    px, py = x + 95, FLOOR_Y
    cr.save(); cr.translate(px, py); cr.rotate(math.pi * 0.95 * smooth(flip)); cr.translate(-px, -py)
    sk_poly(cr, [(x - 100, FLOOR_Y), (x - 85, FLOOR_Y - 70), (x - 20, FLOOR_Y - 105), (x + 60, FLOOR_Y - 90), (x + 95, FLOOR_Y - 30),
                 (x + 95, FLOOR_Y)], 6, sid=sid, fill=(0.62, 0.36, 0.25))
    sk_poly(cr, [(x - 95, FLOOR_Y - 4), (x + 92, FLOOR_Y - 4), (x + 80, FLOOR_Y - 22), (x - 80, FLOOR_Y - 20)], 3, sid=sid + 1,
            fill=(0.45, 0.25, 0.17))
    cr.restore()

def dish(cr, x, s=1.0, sid=37400):
    """the giant radio dish on a tripod, aimed at the sky; a little printer box at its foot (right)."""
    top = (x, FLOOR_Y - 620 * s)
    for d in (-1, 0, 1):
        sketch_line(cr, [top, (x + d * 230 * s, FLOOR_Y)], 10 * s, sid=sid + 2 + d, amp=0.2, color=(0.35, 0.35, 0.40))
    sk_rect(cr, x - 40 * s, FLOOR_Y - 700 * s, x + 40 * s, FLOOR_Y - 600 * s, 5, sid=sid + 4, fill=(0.6, 0.6, 0.65))
    cx, cy = x - 10 * s, FLOOR_Y - 860 * s
    cr.save(); cr.translate(cx, cy); cr.rotate(-0.35)
    cr.move_to(-360 * s, -40 * s); cr.curve_to(-250 * s, 150 * s, 250 * s, 150 * s, 360 * s, -40 * s); cr.close_path()
    cr.set_source_rgb(0.92, 0.92, 0.94); cr.fill_preserve(); cr.set_source_rgb(*INKC); cr.set_line_width(7); cr.stroke()
    sk_ell(cr, 0, -40 * s, 360 * s, 60 * s, 7, sid=sid + 5, fill=(0.82, 0.83, 0.87))
    for k in (-1, 1):
        sketch_line(cr, [(k * 300 * s, -45 * s), (0, -330 * s)], 5, sid=sid + 6 + (k > 0), amp=0.2, color=(0.35, 0.35, 0.40))
    sk_rect(cr, -26 * s, -380 * s, 26 * s, -320 * s, 4, sid=sid + 8, fill=(0.85, 0.66, 0.25))
    cr.restore()
    sketch_line(cr, [(x + 30 * s, FLOOR_Y - 640 * s), (PRX - 60, FLOOR_Y - 150)], 4, sid=sid + 9, amp=0.4)       # cable
    sk_rect(cr, PRX - 95, FLOOR_Y - 190, PRX + 95, FLOOR_Y, 6, sid=sid + 10, fill=(0.85, 0.85, 0.88))       # printer
    sk_rect(cr, PRX - 65, FLOOR_Y - 196, PRX + 65, FLOOR_Y - 180, 3, sid=sid + 11, fill=(0.2, 0.2, 0.25))
    cr.arc(PRX + 60, FLOOR_Y - 60, 12, 0, 2 * math.pi); cr.set_source_rgb(0.3, 0.85, 0.35); cr.fill()

WOW_CHARS = "6EQUJ5"
def strip(cr, x, yb, length, chars=1.0, circ=0.0, wow=0.0, ang=0.0, s=1.0, sid=37500):
    """the printout strip standing up from (x, yb) (its bottom), `length` long."""
    cr.save(); cr.translate(x, yb); cr.rotate(ang); cr.scale(s, s)
    sk_rect(cr, -55, -length, 55, 0, 4, sid=sid, fill=(0.98, 0.98, 0.95))
    for k in range(1, 9):
        y = -length + k * 70
        if y < -10: cr.arc(-42, y, 5, 0, 2 * math.pi); cr.arc(42, y, 5, 0, 2 * math.pi); cr.set_source_rgba(0, 0, 0, 0.25); cr.fill()
    n = int(len(WOW_CHARS) * chars + 1e-6)
    for i in range(n):
        y = -length + 90 + i * 95
        if y < -20: draw_text(cr, WOW_CHARS[i], 0, y, 74)
    if circ > 0.01:
        cr.save(); cr.translate(0, -length + 90 + 2.5 * 95); cr.scale(78, 320)
        cr.arc(0, 0, 1, -math.pi / 2, -math.pi / 2 + 2 * math.pi * min(1.0, circ)); cr.restore()
        cr.set_source_rgb(0.85, 0.12, 0.12); cr.set_line_width(9); cr.set_line_cap(1); cr.stroke()
    if wow > 0.01:
        cr.save(); cr.rectangle(80, -length - 50, 260 * wow, 300); cr.clip()
        draw_text(cr, "Wow!", 200, -length + 140, 92, color=(215, 30, 30), rot=-0.12)
        cr.restore()
    cr.restore()

def nil_sign(cr, x, y, ang=0.0, sid=37600):
    """NO INTELLIGENT LIFE FOUND on a stake; (x, y) is the stake's tip."""
    cr.save(); cr.translate(x, y); cr.rotate(ang)
    sketch_line(cr, [(0, 0), (0, -560)], 12, sid=sid, amp=0.2, color=(0.45, 0.45, 0.5))
    sk_rect(cr, -250, -820, 250, -520, 7, sid=sid + 1, fill=(0.97, 0.97, 0.95))
    sk_rect(cr, -232, -802, 232, -538, 3, sid=sid + 2, fill=None)
    draw_text(cr, "NO", 0, -770, 50, color=(200, 30, 30))
    draw_text(cr, "INTELLIGENT LIFE", 0, -690, 50)
    draw_text(cr, "FOUND", 0, -605, 66, color=(200, 30, 30))
    cr.restore()

def leader_sign(cr, x, y, s=1.0, sid=37650):
    sk_rect(cr, x - 230 * s, y - 120 * s, x + 230 * s, y + 120 * s, 6, sid=sid, fill=(0.97, 0.97, 0.92))
    draw_text(cr, "TAKE ME TO", x, y - 50 * s, int(60 * s))
    draw_text(cr, "YOUR LEADER", x, y + 45 * s, int(60 * s))

def remote(cr, x, y, pressed=False, sid=37700):
    sk_rect(cr, x - 22, y - 50, x + 22, y + 30, 4, sid=sid, fill=(0.3, 0.3, 0.35))
    cr.arc(x, y - 22, 11, 0, 2 * math.pi); cr.set_source_rgb(1.0, 0.25, 0.2) if not pressed else cr.set_source_rgb(1.0, 0.85, 0.3); cr.fill()

# ================================================================ Jezero crater
def draw_jezero(cr, t):
    a, b = E34.mars_sky_ground(cr, JZ, seed=36)
    cxx, cyy, z = L.cam_track.at(t)
    sk_circ(cr, cxx + 280 / z, cyy - 700 / z, 22 / z, 3, sid=34700, fill=(0.72, 0.66, 0.60))       # little moon
    # the mothership rises behind the far rim
    sy = ship_y(t)
    if sy is not None and sy < FLOOR_Y + 100: mothership(cr, ship_x(t), sy, t=t)
    # far crater rim (a long wall all round)
    HOR = E34.HOR
    rim = [(JZ - 9000, HOR + 10)]
    rr = random.Random(361)
    for k in range(37):
        rim.append((JZ - 9000 + k * 500, HOR - 420 - 120 * math.sin(k * 0.9) - rr.uniform(0, 90)))
    rim.append((JZ + 9500, HOR + 10))
    sk_poly(cr, rim, 6, sid=36100, fill=(0.78, 0.48, 0.34))
    cr.rectangle(a, HOR, b - a, FLOOR_Y - HOR + 1); cr.set_source_rgb(0.82, 0.52, 0.36); cr.fill()
    # the old river delta: a pale layered fan in the distance
    for k, c in enumerate(((0.88, 0.66, 0.50), (0.86, 0.60, 0.44), (0.90, 0.70, 0.55))):
        w = 2300 - 500 * k
        sk_poly(cr, [(JZ - 4200 - w, HOR + 20), (JZ - 4200 - w * 0.3, HOR - 140 + 40 * k), (JZ - 4200 + w * 0.3, HOR - 140 + 40 * k),
                     (JZ - 4200 + w, HOR + 20)], 4, sid=36110 + k, fill=c)
    cr.rectangle(a, FLOOR_Y, b - a, 1600); cr.set_source_rgb(0.74, 0.42, 0.27); cr.fill()
    # dried mud cracks (an old lake bed)
    for k in range(40):
        x = JZ - 6000 + k * 330 + rr.uniform(-60, 60); y = FLOOR_Y + rr.uniform(60, 520)
        if a - 200 < x < b + 200:
            sketch_line(cr, [(x - 90, y), (x - 20, y + 18), (x + 40, y - 10), (x + 100, y + 12)], 3, sid=36130 + k % 9, alpha=0.45)
    # the low ridge behind him (aliens hide behind it)
    ridge_aliens(cr, t)
    sk_poly(cr, [(JZ + 150, FLOOR_Y - 230), (JZ + 330, FLOOR_Y - 420), (JZ + 620, FLOOR_Y - 460), (JZ + 900, FLOOR_Y - 430),
                 (JZ + 1200, FLOOR_Y - 470), (JZ + 1500, FLOOR_Y - 440), (JZ + 1800, FLOOR_Y - 455), (JZ + 2100, FLOOR_Y - 380),
                 (JZ + 2350, FLOOR_Y - 230)], 6, sid=36150, fill=(0.70, 0.40, 0.27))
    for k in range(6):
        x = JZ + 400 + k * 320
        sketch_line(cr, [(x, FLOOR_Y - 400), (x + 60, FLOOR_Y - 320)], 3, sid=36160 + k, alpha=0.4)
    sketch_line(cr, [(a, FLOOR_Y), (b, FLOOR_Y)], 6, sid=34770, amp=0.3)
    # rocks
    for k in range(18):
        x = JZ - 4800 + k * 560 + rr.uniform(-80, 80)
        if abs(x - JZ) < 900 or not (a - 200 < x < b + 200): continue
        y = FLOOR_Y + rr.uniform(30, 400)
        sk_poly(cr, [(x - 70, y), (x - 40, y - 50), (x + 30, y - 60), (x + 80, y)], 4, sid=34740 + k % 9, fill=(0.56, 0.30, 0.20))
    # the sign
    x = JSIGN
    for d in (-210, 210):
        sketch_line(cr, [(x + d, FLOOR_Y), (x + d, FLOOR_Y - 560)], 9, sid=36170 + (d > 0), amp=0.2, color=(0.5, 0.5, 0.55))
    sk_rect(cr, x - 330, FLOOR_Y - 900, x + 330, FLOOR_Y - 520, 6, sid=36172, fill=(0.95, 0.95, 0.93))
    draw_text(cr, "JEZERO CRATER", x, FLOOR_Y - 815, 64)
    draw_text(cr, "ANCIENT LAKE BED", x, FLOOR_Y - 715, 44, color=(40, 90, 170))
    draw_text(cr, "LOOK FOR LIFE HERE", x, FLOOR_Y - 625, 40, color=(200, 40, 40))
    rock(cr, ROCK_X, flip=ramp(t, T_FLIP0, T_FLIP1, "linear"))

def draw_cydonia(cr, t):
    a, b = E34.mars_sky_ground(cr, CY)
    cxx, cyy, z = L.cam_track.at(t)
    sk_circ(cr, cxx - 250 / z, cyy - 640 / z, 26 / z, 3, sid=34700, fill=(0.72, 0.66, 0.60))
    sk_poly(cr, [(CY - 6000, E34.HOR), (CY - 4200, E34.HOR - 300), (CY - 2600, E34.HOR - 180), (CY + 2600, E34.HOR - 260),
                 (CY + 4400, E34.HOR - 120), (CY + 6500, E34.HOR)], 5, sid=35610, fill=(0.80, 0.52, 0.38))
    cr.rectangle(a, E34.HOR, b - a, FLOOR_Y - E34.HOR + 1); cr.set_source_rgb(0.80, 0.46, 0.30); cr.fill()
    cr.rectangle(a, FLOOR_Y, b - a, 1600); cr.set_source_rgb(0.72, 0.38, 0.24); cr.fill()
    rr = random.Random(351)
    for k in range(26):
        x = CY - 5200 + k * 420 + rr.uniform(-80, 80); y = FLOOR_Y + rr.uniform(80, 500)
        if a < x < b:
            sk_poly(cr, [(x - 70, y), (x - 40, y - 50), (x + 30, y - 60), (x + 80, y)], 4, sid=34740 + k % 9, fill=(0.56, 0.30, 0.20))
    E35.draw_face(cr, 1000.0)                    # grinning, eyes shut (stone)
    sketch_line(cr, [(a, FLOOR_Y), (b, FLOOR_Y)], 6, sid=34770, amp=0.3)
    E35.draw_cy_sign(cr, t)
    E35.shards(cr, E35.HFX + 180)
    E35.jackhammer(cr, E35.JH_REST[0] - 160, E35.JH_REST[1], E35.JH_REST[0] + 160, E35.JH_REST[1] + 10)
    O.draw_feather(cr, E35.HFX - 250, FLOOR_Y - 12, s=1.5, ang=1.62, t=t, droop=0.0)
    # a little dust skitters past (nothing alive)
    if T_LOOKL - 0.2 <= t < T_LOOKR2:
        u = ramp(t, T_LOOKL - 0.2, T_LOOKR2, "linear")
        O.draw_smoke_puff(cr, lerp(HC - 1600, HC + 1400, u), FLOOR_Y - 40 - 40 * abs(math.sin(u * 12)), 45, alpha=0.6, dark=0.2)

# ================================================================ the ship
def ship_x(t):
    if t >= T_LEAVE: return SHIP_X + 900 * ramp(t, T_LEAVE, T_LEAVE + 0.5, "linear") ** 2
    return SHIP_X
def ship_y(t):
    if t < CUT_SHIP - FR: return None
    if t < T_SHIP1:
        u = ramp(t, CUT_SHIP, T_SHIP1)
        return lerp(FLOOR_Y + 300, SHIP_Y1, 1 - (1 - u) ** 2.2) + 18 * math.sin(t * 9) * (1 - u)
    if t < T_LEAVE: return SHIP_Y1 + 25 * math.sin(t * 2.2)
    u = ramp(t, T_LEAVE, T_LEAVE + 0.5, "linear")
    if u >= 1: return None
    return SHIP_Y1 - 14000 * u * u
def beam_on(t): return T_BEAM <= t < CUT_FALL - FR
def beam_k(t): return smooth(ramp(t, T_BEAM, T_BEAM + 0.2))

# ================================================================ the aliens
# peekers behind the ridge: (x, up-intervals)
PEEK = [(JZ + 760, ((T_P1UP0, T_P1UP1, T_DUCK1, T_DUCK1 + 0.22), (T_P2UP0 + 0.25, T_P2UP1 + 0.25, T_DUCK2, T_DUCK2 + 0.2))),
        (JZ + 470, ((T_P2UP0, T_P2UP1, T_DUCK2 + 0.05, T_DUCK2 + 0.25),)),
        (JZ + 1700, ((T_P2UP0 + 0.5, T_P2UP1 + 0.5, T_DUCK2 + 0.1, T_DUCK2 + 0.3),))]
def ridge_aliens(cr, t):
    if not (CUT_PEEK - FR <= t < CUT_WOW - FR): return
    cr.save(); cr.rectangle(JZ - 5000, FLOOR_Y - 20000, 10000, 20000 - 300); cr.clip()
    _ridge_aliens(cr, t)
    cr.restore()

def _ridge_aliens(cr, t):
    for i, (x, ivs) in enumerate(PEEK):
        up = 0.0
        for a, b, c, d in ivs:
            if a <= t < d:
                up = smooth(ramp(t, a, b)) * (1 - ramp(t, c, d, "linear"))
        if up < 0.01: continue
        look = (-0.8, 0.3)
        alien(cr, x, FLOOR_Y - 250 + 400 * (1 - up), s=1.15, look=look, sid=37000 + 30 * i,
              blink=1.0 if (13.6 + i * 0.4) <= t < (13.75 + i * 0.4) else 0.0)

# the sneakers: (start x, end x)
SNEAK = [(JZ + 1350, JZ + 270), (JZ + 1600, JZ + 520), (JZ + 1850, JZ + 760), (JZ + 2100, JZ + 990)]
def sneak_x(i, t):
    x0, x1 = SNEAK[i]
    u = ramp(t, T_SNEAK0 + 0.12 * i, T_SNEAK1 + 0.08 * i, "linear")
    return lerp(x0, x1, u)
def sneak_bob(i, t):
    if not (T_SNEAK0 <= t < T_SNEAK1 + 0.4): return 0.0
    return 22 * abs(math.sin((t - T_SNEAK0) * 6.5 + i))
def alien_lift(i, t):
    if t < T_AUP0 + 0.1 * i: return 0.0
    u = ramp(t, T_AUP0 + 0.1 * i, T_AUP1 + 0.1 * i)
    return 4300 * u * u
def draw_ground_aliens(cr, t):
    if t < CUT_BEHIND - FR or t >= CUT_FALL - FR: return
    if CUT_LEADER - FR <= t < CUT_ALIEN - FR: return
    for i in reversed(range(len(SNEAK))):
        x = sneak_x(i, t)
        lift = alien_lift(i, t)
        if lift > 4000: continue
        yf = FLOOR_Y - lift
        look = (-0.9, -0.5)
        kw = {}
        if i == 0:
            if T_TAP - 0.25 <= t < T_TAP + 0.4:
                k = smooth(ramp(t, T_TAP - 0.25, T_TAP)) * (1 - smooth(ramp(t, T_TAP + 0.25, T_TAP + 0.4)))
                tap = 10 * math.sin((t - T_TAP) * 40) if t >= T_TAP else 0
                kw["reach"] = (lerp(x + 80, JZ + 85, k), lerp(FLOOR_Y - 110, FLOOR_Y - 520 + tap, k))
            if t >= CUT_FACE2 - FR: look = (-1.0, -1.0)
            if T_SIGN0 <= t < CUT_LEADER - FR:
                kw["both_up"] = smooth(ramp(t, T_SIGN0, T_SIGN1))
            if CUT_ALIEN - FR <= t:
                look = (-1.0, -0.2) if t < T_ABACK else (-1.0, -1.0)
                kw["reach"] = (x + 90, FLOOR_Y - 300 - 40 * smooth(ramp(t, T_REMOTE, T_REMOTE + 0.15)))
            if lift > 0: look = (0.0, 0.5)
        else:
            if t >= CUT_FACE2 - FR: look = (-1.0, -0.8)
        alien(cr, x, yf, s=1.15, look=look, sid=37000 + 30 * i, bob=sneak_bob(i, t),
              blink=1.0 if (27.25 + i * 0.3) <= t < (27.4 + i * 0.3) else 0.0, **kw)
        if i == 0 and "both_up" in kw and kw["both_up"] > 0.01:
            leader_sign(cr, x + 150, FLOOR_Y - lerp(200, 640, kw["both_up"]) * 1.15, s=1.0)
        if i == 0 and CUT_ALIEN - FR <= t and lift < 10 and t >= T_REMOTE:
            rx_, ry_ = kw["reach"]
            remote(cr, rx_ + 5, ry_ - 30, pressed=t >= T_PRESS)
            if T_PRESS <= t < T_PRESS + 0.3:
                L.burst_lines(cr, rx_ + 5, ry_ - 60, (t - T_PRESS) / 0.3, r0=40, r1=90, n=7, sid=21)

# ================================================================ the rex (Jerry)
def rex(t):
    st = dict(O.DINO); st.update(s=RS, look=(0.6, 0.6), smile=0.5, lid=0.0, mouth=0.0, arms=0.0, walk=0.0)
    X, lift, pitch, face = REX_C, 0.0, 0.0, 1
    if t < CUT_RIDE - FR:
        st["look"] = (0.9, 0.5)
        if t >= T_ROV + 0.1: st["look"] = (-0.3, 0.9)
        if t >= T_LOOKR2: st["look"] = (1.0, 0.0); st["smile"] = 0.6
        return X, lift, pitch, face, st
    if t < CUT_JZ - FR:
        st["look"] = (1.0, 0.0)
        u = max(0.0, t - T_BOLT)
        X = REX_C - 200 + 700 * u + 900 * u * u
        if t >= T_BOLT:
            st["walk"] = u * 16.0; pitch = 0.10 + 0.05 * math.sin(u * 16); lift = 40 * abs(math.sin(u * 8)); st["mouth"] = 0.2
        return X, lift, pitch, face, st
    if t < CUT_STAND - FR:
        u = ramp(t, CUT_JZ, T_STOPJ)
        X = lerp(REX_J - 1400, REX_J + 200, 1 - (1 - u) ** 2)
        st["walk"] = 0.0 if u > 0.55 else (t - CUT_JZ) * 16
        pitch = 0.22 * math.sin(math.pi * u); st["look"] = (1.0, -0.2)
        return X, lift, pitch, face, st
    X = REX_J; st["look"] = (0.8, 0.5)
    if t >= T_JSEE and t < T_BACK2 + 0.3:
        st["look"] = (1.0, -0.2); st["pupil"] = 0.55; st["worry"] = 0.7; st["smile"] = 0.0; st["sweat"] = 1.0
    if CUT_JERRY - FR <= t < T_BACK2 + 0.3:
        k = smooth(ramp(t, CUT_JERRY, T_TAP0 + 0.2)) * (1 - smooth(ramp(t, T_TAP1, T_TAP1 + 0.3)))
        X = REX_J + 180 * k; pitch = 0.18 * k
        st["arms"] = 0.5 + 0.5 * math.sin((t - T_TAP0) * 30) if T_TAP0 <= t < T_TAP1 else 0.0
        st["mouth"] = 0.25 * k
        if t >= T_TURNJ: st["look"] = (0.4, 0.3)
        if t >= T_CHIN: st["look"] = (1.0, -0.3); pitch = -0.08 * smooth(ramp(t, T_CHIN, T_CHIN + 0.15)) * (1 - ramp(t, T_CHIN + 0.4, T_CHIN + 0.6))
    if T_BACK2 + 0.3 <= t < CUT_BEHIND - FR:
        st["look"] = (0.9, 0.2); st["worry"] = 0.4
    if CUT_BEHIND - FR <= t < CUT_LEADER - FR:                 # hiding behind the dish
        k = smooth(ramp(t, CUT_BEHIND, CUT_BEHIND + 0.5))
        pitch = 0.42 * k; X = REX_J - 60 * k
        st["look"] = (1.0, -0.2); st["pupil"] = 0.5; st["worry"] = 0.8; st["smile"] = 0.0; st["sweat"] = 1.0
        if t >= CUT_FACE2: st["look"] = (1.0, 0.2)
    if CUT_LEADER - FR <= t < CUT_SHIP - FR:                   # "the leader"
        k = smooth(ramp(t, T_RISE, T_RISE + 0.45))
        pitch = 0.42 * (1 - k); X = REX_J - 60 - 390 * k
        st["walk"] = (t - T_RISE) * 12 if T_RISE <= t < T_RISE + 0.45 else 0.0
        st["look"] = (-0.2, 0.5); st["smile"] = 0.9; st["worry"] = 0.0; st["pupil"] = 1.0
        if t >= T_RISE + 0.35: st["eyes"] = "happy"; st["arms"] = 0.5 + 0.5 * math.sin((t - T_RISE) * 14)
        if t >= CUT_ALIEN - FR: st["eyes"] = "normal"; st["arms"] = 0.0; st["look"] = (1.0, 0.3)
        if t >= T_HUM + 0.2: st["look"] = (0.7, -1.0); st["pupil"] = 0.5; st["worry"] = 0.6; st["smile"] = 0.0
    if t >= CUT_SHIP - FR: X = REX_J - 450
    if CUT_SHIP - FR <= t < CUT_SIGNC - FR:
        st["look"] = (0.6, -1.0); st["pupil"] = 0.45; st["worry"] = 0.8; st["smile"] = 0.0; st["mouth"] = 0.4
    if t >= CUT_SIGNC - FR:
        st["look"] = (1.0, 0.4); st["smile"] = 0.3; st["worry"] = 0.2
    return X, lift, pitch, face, st

def seat(t):
    X, lift, pitch, face, st = rex(t)
    x, y = rex_world(X, lift, pitch, face, 215, 615)
    return (x, y - O._walkbob(st))

def rex_head_c(t):
    X, lift, pitch, face, st = rex(t)
    x, y = rex_world(X, lift, pitch, face, -235, 930)
    return x, y - O._walkbob(st)

def rex_drawn(t):
    if CUT_ROCK - FR <= t < CUT_PEEK - FR: return False
    if CUT_PEEK - FR <= t < CUT_JERRY - FR: return False
    if CUT_FACE2 - FR <= t < CUT_LEADER - FR: return False
    if CUT_ALIEN - FR <= t < CUT_SHIP - FR: return False
    if CUT_RISE - FR <= t < CUT_FALL - FR: return False
    return True

def draw_rex(cr, t):
    if not rex_drawn(t): return
    X, lift, pitch, face, st = rex(t)
    blink = 0.0
    for b in (1.2, 6.9, 12.0, 19.9, 23.0, 30.2, 42.4, 50.0, 56.0):
        if b <= t < b + 0.16: blink = math.sin(math.pi * (t - b) / 0.16)
    sw = st.pop("sweat", 0.0)
    cr.save(); cr.translate(0, -lift)
    O.draw_trex(cr, X, st, t, face=face, pitch=pitch, blink=blink)
    cr.restore()
    x, y = rex_world(X, lift, pitch, face, 215, 600)
    E32.draw_saddle(cr, x, y + 10 - O._walkbob(st), pitch * face + 0.08 * face, 1.0, sid=33510, stirrups=False)
    tx, ty = rex_world(X, lift, pitch, face, *E34.TAG_LH)
    E34.name_tag(cr, tx, ty - O._walkbob(st), 1.1, ang=(-0.12 + pitch * face) * (1 if face == -1 else -1), sid=36010)
    hx, hy = rex_head_c(t)
    helmet(cr, hx, hy, 300, sid=33020)
    if sw > 0.5:                                                  # sweat drops
        for k in range(2):
            q = ((t * 1.6 + k * 0.5) % 1.0)
            cr.save(); cr.translate(hx - 120 + 240 * k, hy - 120 + 120 * q); cr.scale(14, 22)
            cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore(); cr.set_source_rgba(0.55, 0.8, 1.0, 1 - q); cr.fill()

# ================================================================ the rover
def rover_state(t):
    """x, face(1 right/-1 left), moving, arm"""
    if t < CUT_RIDE - FR:
        return ROV_C, 1, False, smooth(ramp(t, T_ROV, T_ROV + 0.3))
    if t < T_ROVIN0: return None
    if t < T_ROVIN1:
        u = ramp(t, T_ROVIN0, T_ROVIN1)
        return lerp(ROV_J + 1500, ROV_J, 1 - (1 - u) ** 2), -1, True, 0.0
    arm = smooth(ramp(t, T_CUP0, T_CUP1)) * (1 - smooth(ramp(t, T_CUPDN, T_CUPDN + 0.3)))
    return ROV_J, -1, False, arm

def rover_hand(x, face, arm):
    s = 1.6
    hdx, hdy = lerp(-300, -200, arm), lerp(-110, -560, arm)
    return (x - face * s * hdx, FLOOR_Y + s * hdy)

def rover_drawn(t):
    if CUT_ROCK - FR <= t < CUT_PEEK - FR: return False
    if CUT_WOW - FR <= t < CUT_BEHIND - FR: return False
    if CUT_LEADER - FR <= t < CUT_ALIEN - FR: return False
    if CUT_RISE - FR <= t < CUT_FALL - FR: return False
    return True

def draw_rover_j(cr, t):
    s_ = rover_state(t)
    if not s_ or not rover_drawn(t): return
    x, face, moving, arm = s_
    cr.save()
    if face == -1: cr.translate(x, 0); cr.scale(-1, 1); cr.translate(-x, 0)
    E34.draw_rover(cr, x, t, moving=moving, arm=arm, tag=False, dusty=0.7)
    cr.restore()
    hx, hy = rover_hand(x, face, arm)
    if T_DRILL0 <= t < T_DRILL1:                                  # the drill
        jx = 4 * math.sin(t * 80)
        sketch_line(cr, [(hx + jx, hy + 20), (hx + jx, FLOOR_Y + 10)], 10, sid=37800, amp=0.1, color=(0.4, 0.4, 0.45))
        for k in range(4):
            q = ((t * 3 + k / 4) % 1.0)
            O.draw_smoke_puff(cr, hx + (-1) ** k * (40 + 100 * q), FLOOR_Y - 30 - 70 * q, 30 + 40 * q, alpha=0.6 * (1 - q), dark=0.25)
    if arm > 0.3 and t >= T_CUP0:                                 # the sample cup
        sk_rect(cr, hx - 34, hy - 90, hx + 34, hy - 26, 4, sid=37810, fill=(0.85, 0.88, 0.95))
        sk_ell(cr, hx, hy - 88, 34, 9, 3, sid=37811, fill=(0.68, 0.40, 0.26))
    if T_SAD <= t < T_SAD + 0.6:
        q = ramp(t, T_SAD, T_SAD + 0.6)
        cr.arc(x - face * 180, FLOOR_Y - 960 - 60 * q, 12, 0, 2 * math.pi); cr.set_source_rgba(*INKC, 1 - q); cr.fill()
    if T_ROV <= t < T_ROV + 0.6:
        for k in range(2):
            q = ramp(t, T_ROV + 0.15 * k, T_ROV + 0.15 * k + 0.4)
            if 0 < q < 1:
                cr.arc(x + 180 + 60 * k, FLOOR_Y - 960 - 80 * q, 12, 0, 2 * math.pi); cr.set_source_rgba(*INKC, 1 - q); cr.fill()

# ================================================================ held things / ground things
def glass_drawer(cr, x, y, s, t, p):
    if t >= T_GDROP: return
    hx, hy = p["rhand"]
    if CUT_ROCK - FR <= t < CUT_PEEK - FR: return
    if t < POP_GLASS + 0.1:
        magnifier(cr, hx + 10, hy - 110, 80, ang=1.5); return
    if T_CUP0 + 0.2 <= t < T_CUPDN + 0.2:                          # held out at the sample cup
        def eye(cr2):
            cr2.arc(hx + 30, hy - 120, 40, 0, 2 * math.pi); cr2.set_source_rgb(1, 1, 1); cr2.fill()
            cr2.arc(hx + 46, hy - 118, 18, 0, 2 * math.pi); cr2.set_source_rgb(*INKC); cr2.fill()
        magnifier(cr, hx + 30, hy - 120, 80, ang=1.75, inside=None)
        return
    magnifier(cr, hx + 10, hy - 110, 80, ang=1.5)

def glass_on_ground(cr, t):
    if t < T_GDROP: return
    if CUT_WOW - FR <= t < CUT_BEHIND - FR: return
    if t < T_GLAND:
        u = ramp(t, T_GDROP, T_GLAND)
        return magnifier(cr, lerp(JZ + 230, GLASS_REST[0], u), lerp(FLOOR_Y - 500, GLASS_REST[1] - 50, u * u), 80, ang=lerp(1.5, 3.3, u))
    magnifier(cr, GLASS_REST[0] + 60, GLASS_REST[1] - 50, 80, ang=3.1)

def strip_draw(cr, t, p):
    """the printout: in the printer (insert), then in his hands, then on the ground."""
    if t < T_PRINT0: return
    if t < CUT_BEHIND - FR:
        u = ramp(t, T_PRINT0, T_PRINT1, "linear")
        strip(cr, PRX, FLOOR_Y - 190, 140 + 560 * u, chars=u, circ=ramp(t, T_CIRC0, T_CIRC1, "linear"), wow=ramp(t, T_WOW0, T_WOW1, "linear"))
        return
    if t < T_SDROP:
        lh, rh = p["lhand"], p["rhand"]
        mx, my = (lh[0] + rh[0]) / 2, (lh[1] + rh[1]) / 2
        strip(cr, mx, my + 250 * 0.42, 700, circ=1.0, wow=1.0, s=0.42, ang=0.05)
        return
    if t < T_SLAND:
        u = ramp(t, T_SDROP, T_SLAND)
        strip(cr, lerp(JZ + 30, STRIP_REST[0], u), lerp(FLOOR_Y - 600, STRIP_REST[1], u * u), 700, circ=1.0, wow=1.0, s=0.42,
              ang=lerp(0.05, 1.45, u))
        return
    strip(cr, STRIP_REST[0], STRIP_REST[1], 700, circ=1.0, wow=1.0, s=0.42, ang=1.5)

def dish_drawer(cr, x, y, s, t, p):
    if CUT_RISE - FR <= t < CUT_FALL - FR: return
    dish(cr, DISH_X, 1.25)

# ================================================================ poses
def P_(name, **kw): L.POSES[name] = kw
P_("glass_hold", lelb=(460, 960), lhand=(450, 1060), relb=(640, 950), rhand=(660, 900), rhand_t="grip")
P_("glass_out", lelb=(460, 960), lhand=(450, 1060), relb=(680, 860), rhand=(800, 820), rhand_t="grip")
P_("strip_read", lelb=(460, 950), lhand=(500, 880), relb=(620, 950), rhand=(580, 880), lhand_t="grip", rhand_t="grip")
P_("point_l", lelb=(420, 860), lhand=(300, 800), lhand_t="point", relb=(620, 960), rhand=(630, 1060))
P_("float", lelb=(450, 930), lhand=(400, 1010), relb=(630, 930), rhand=(680, 1010), nowalk=1.0)
P_("look_up", lelb=(460, 960), lhand=(450, 1060), relb=(620, 960), rhand=(630, 1060))

# ================================================================ scene (him)
deadpan_pull = E35.deadpan_pull

S = M.Scene(start_body="stand", start_face="deadpan", x0=HC - 540)
S.auto_blinks = True
S.floor = False
S.card("nicolascechettoschuller", "Try find extraterrestrial life", "0", t0=0.3)
CAM_A = cam(HC - 150, 0.46, fs=1660)
S.camkeys[0] = (0.0, CAM_A, 0); S.cam = CAM_A

# ---------------------------------------------------------------- A: Cydonia
S.read_card(T_READ, react="deadpan", lines=1)
S.set(T_LOOKL, "stand", "dead_stare", dur=0.25, turn=-0.3, look=(-1.0, 0.1), lid=0.3)
S.set(T_LOOKR, "stand", "dead_stare", dur=0.25, turn=0.3, look=(1.0, 0.1), lid=0.3)
S.sfx(T_LOOKL, "wind", 0.04, dur=1.0)
S.sfx(T_ROV, "boop", 0.04); S.sfx(T_ROV + 0.15, "boop", 0.04); S.sfx(T_ROV, "whine", 0.015, dur=0.4)
S.set(T_LOOKROV, "stand", "deadpan", dur=0.25, turn=-0.5, look=(-1.0, 0.3))
S.set(T_LOOKR2, "stand", "deadpan", dur=0.3, turn=0.6, look=(1.0, -0.2))
S.camera(T_LOOKL, *cam(HC - 180, 0.44, fs=1665), 1.6)

# the ride
S.cut(CUT_RIDE - FR, cam=cam(REX_C, 0.42, fs=1680), x=HC - 540)
S.set(CUT_RIDE - FR, "ride", "deadpan", dur=0.0, turn=0.9, look=(1.0, 0.0))
S.sfx(T_BOLT, E32.ROAR_WAV, 0.08); S.sfx(T_BOLT + 0.1, "whoosh", 0.08)
S.set(T_BOLT + 0.05, "ride", "deadpan", dur=0.12, ease="snap", turn=0.9, look=(1.0, 0.0), lean=-0.2, curl_up=1.0)
S.set(T_BOLT + 0.5, "ride", "dead_stare", dur=0.3, turn=0.9, look=(1.0, 0.0), lean=-0.05)
for k in range(5): S.sfx(T_BOLT + 0.2 + 0.3 * k, "thud", 0.07)
S.sfx(CUT_JZ - 0.7, "wind", 0.08, dur=1.2)

# ---------------------------------------------------------------- B: Jezero
CAM_W = cam(JZ - 900, 0.30, fs=1700)
S.cut(CUT_JZ - FR, cam=CAM_W, x=HC - 540)
S.set(CUT_JZ - FR, "ride", "deadpan", dur=0.0, turn=0.9, look=(1.0, 0.0), lean=-0.05)
S.sfx(CUT_JZ + 0.1, "skid", 0.12, dur=0.7)
S.set(CUT_JZ + 0.4, "ride", "dead_stare", dur=0.15, turn=0.9, look=(1.0, 0.0), lean=0.25)
S.set(T_STOPJ, "ride", "dead_stare", dur=0.4, turn=-0.4, look=(-1.0, -0.2), lid=0.2)
S.camera(T_STOPJ - 0.3, *cam(JZ - 950, 0.29, fs=1710), 1.0)

S.cut(CUT_STAND - FR, cam=cam(JZ - 150, 0.50, fs=1665), x=JZ - 540)
S.set(CUT_STAND - FR, "stand", "deadpan", dur=0.0, look=(0.0, 0.0))
deadpan_pull(S, T_GLASS, "glass", glass_drawer, (0, 0), held=True)
S.set(POP_GLASS + 0.1, "glass_hold", "deadpan", dur=0.3, look=(0.3, -0.3), lid=0.35)

# insert: the rock
S.cut(CUT_ROCK - FR, cam=cam(ROCK_X - 60, 1.05, fs=1420))
S.sfx(T_FLIP0 + 0.2, "clack", 0.06); S.sfx(T_FLIP1, "thud", 0.05)
S.sfx(T_EBLINK, "blink", 0.03)

# the first peek
CAM_P = cam(JZ + 560, 0.45, fs=1680)
S.cut(CUT_PEEK - FR, cam=CAM_P)
S.set(CUT_PEEK - FR, "glass_hold", "dead_stare", dur=0.0, look=(0.0, 0.0), lid=0.35)
S.set(T_TURN1, "glass_hold", "dead_stare", dur=0.3, turn=0.9, look=(1.0, -0.2), lid=0.3)
S.set(T_BACK1, "glass_hold", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lid=0.4)
S.sfx(T_DUCK1, "whoosh", 0.03, dur=0.2)
S.camera(CUT_PEEK, *cam(JZ + 600, 0.47, fs=1675), 1.2)

# the rover drills
S.sfx(T_ROVIN0, "whine", 0.02, dur=0.6)
S.sfx(T_DRILL0, "whine", 0.05, dur=T_DRILL1 - T_DRILL0); S.sfx(T_DRILL0, "rummage", 0.06, dur=T_DRILL1 - T_DRILL0)
S.set(T_DRILL0 + 0.2, "glass_hold", "dead_stare", dur=0.3, turn=0.7, look=(1.0, 0.6), lid=0.35)
S.set(T_CUP1 + 0.1, "glass_out", "dead_stare", dur=0.35, turn=0.8, look=(1.0, -0.2), lid=0.2)
S.set(T_SAD - 0.1, "glass_out", "dead_stare", dur=0.2, turn=0.8, look=(1.0, -0.2), lid=0.45)
S.sfx(T_SAD, "boop", 0.03); S.sfx(T_SAD + 0.18, "slide_down", 0.02, dur=0.3)
S.set(T_CUPDN, "glass_hold", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lid=0.4)
S.camera(T_ROVIN0, *cam(JZ + 650, 0.43, fs=1680), 1.0)

# Jerry can't warn him
S.cut(CUT_JERRY - FR, cam=cam(JZ - 350, 0.42, fs=1680))
S.set(CUT_JERRY - FR, "glass_hold", "dead_stare", dur=0.0, look=(0.0, 0.0), lid=0.4)
for k in range(5): S.sfx(T_TAP0 + 0.18 * k, "squeak", 0.012)
S.set(T_TURNJ, "glass_hold", "dead_stare", dur=0.3, turn=-0.8, look=(-1.0, -0.3), lid=0.35)
S.set(T_LOOKRIDGE, "glass_hold", "dead_stare", dur=0.3, turn=0.9, look=(1.0, -0.1), lid=0.35)
S.set(T_BACK2, "glass_hold", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lid=0.45)
S.sfx(T_DUCK2, "whoosh", 0.03, dur=0.2)
S.set(T_GDROP - 0.05, "stand", "dead_stare", dur=0.2, look=(0.2, 0.7), lid=0.4)
S.sfx(T_GLAND, "clack", 0.06)
S.x = JZ - 540
deadpan_pull(S, T_DISH, "dish", dish_drawer, (DISH_X, FLOOR_Y), held=False)
S.sfx(POP_DISH + 0.05, "thud", 0.08)
S.set(POP_DISH + 0.15, "stand", "dead_stare", dur=0.3, turn=-0.5, look=(-0.8, -0.8), lid=0.3)
S.camera(T_DISH, *cam(JZ - 300, 0.40, fs=1685), 2.0)

# insert: the printout
S.cut(CUT_WOW - FR, cam=(PRX + 60, FLOOR_Y - 560, 1.05))
for k in range(8): S.sfx(T_PRINT0 + 0.1 * k, "tick", 0.05)
S.sfx(T_CIRC0, "scribble", 0.05, dur=T_CIRC1 - T_CIRC0); S.sfx(T_WOW0, "scribble", 0.05, dur=T_WOW1 - T_WOW0)

# they sneak up
CAM_B = cam(JZ + 300, 0.42, fs=1680)
S.cut(CUT_BEHIND - FR, cam=CAM_B)
S.set(CUT_BEHIND - FR, "strip_read", "dead_stare", dur=0.0, look=(0.0, 0.7), lid=0.4)
S.camera(CUT_BEHIND, *cam(JZ + 280, 0.52, fs=1670), T_TAP - CUT_BEHIND, "linear")
for k in range(9): S.sfx(T_SNEAK0 + 0.16 * k + 0.05, "tiptoe", 0.04)
hb = T_SNEAK0 + 0.1; gap = 0.62
while hb < T_TAP - 0.1:
    S.sfx(hb, "thud", 0.07); S.sfx(hb + 0.13, "thud", 0.045); hb += gap; gap = max(0.32, gap * 0.85)
S.set(T_SNEAK1 - 0.3, "strip_read", "dead_stare", dur=0.4, look=(0.3, -0.6), lid=0.3)       # the dish: where is it from?
S.sfx(T_TAP, "tap", 0.10); S.sfx(T_TAP + 0.17, "tap", 0.08)
S.set(T_TAP + 0.08, "strip_read", "dead_stare", dur=0.1, ease="snap", look=(0.3, -0.6), lid=0.1, eyescale=1.08)

# face to face
S.cut(CUT_FACE2 - FR, cam=cam(JZ + 160, 0.78, fs=1580))
S.set(CUT_FACE2 - FR, "strip_read", "dead_stare", dur=0.0, look=(0.3, 0.0), lid=0.2)
S.set(T_TURNF, "strip_read", "dead_stare", dur=0.45, turn=0.9, look=(1.0, 0.85), tilt=0.06, lid=0.2)
S.set(T_SDROP, "stand", "dead_stare", dur=0.2, turn=0.9, look=(1.0, 0.85), tilt=0.06, lid=0.15, eyescale=1.08)
S.sfx(T_SLAND, "flip", 0.03)
S.set(T_TWITCH, "stand", "dead_stare", dur=0.06, ease="snap", turn=0.9, look=(1.0, 0.85), tilt=0.06, lid=0.15, eyescale=1.08, twitch=1.0)
S.set(T_TWITCH + 0.2, "stand", "dead_stare", dur=0.15, turn=0.9, look=(1.0, 0.85), tilt=0.06, lid=0.2, twitch=0.0)
S.sfx(T_SIGN0, "flip", 0.05)
S.set(T_SIGN1 + 0.1, "stand", "dead_stare", dur=0.35, turn=0.7, look=(0.8, -0.4), tilt=0.0, lid=0.3)
S.set(T_POINT, "point_l", "dead_stare", dur=0.5, turn=-0.7, look=(-1.0, 0.0), lid=0.4)

# the leader
S.cut(CUT_LEADER - FR, cam=cam(REX_J - 200, 0.47, fs=1665))
S.sfx(T_RISE + 0.35, "squeak", 0.03); S.sfx(T_RISE + 0.6, "squeak", 0.03)

# the alien calls it in
S.cut(CUT_ALIEN - FR, cam=cam(JZ + 230, 0.74, fs=1590))
S.set(CUT_ALIEN - FR, "point_l", "dead_stare", dur=0.0, turn=-0.7, look=(-1.0, 0.0), lid=0.4)
S.set(T_ABACK, "stand", "dead_stare", dur=0.35, turn=0.6, look=(1.0, 0.8), lid=0.35)
S.sfx(T_PRESS, "boop", 0.06); S.sfx(T_PRESS + 0.12, "boop", 0.05)
S.sfx(T_HUM, HUM_WAV, 0.30); S.shake(T_HUM, 3.0, 7)
S.set(T_HUM + 0.15, "stand", "dead_stare", dur=0.35, turn=0.2, look=(0.2, -1.0), tilt=-0.08, lid=0.1, eyescale=1.1)

# ---------------------------------------------------------------- C: the mothership
CAM_S = cam(JZ + 300, 0.2, fs=1760)
S.cut(CUT_SHIP - FR, cam=CAM_S)
S.set(CUT_SHIP - FR, "look_up", "dead_stare", dur=0.0, turn=0.2, look=(0.2, -1.0), tilt=-0.08, lid=0.1, eyescale=1.1)
S.camera(CUT_SHIP, *cam(JZ + 300, 0.19, fs=1770), T_SHIP1 - CUT_SHIP)
S.sfx(T_BEAM, "whoosh", 0.10, dur=0.5); S.sfx(T_BEAM, "whine", 0.04, dur=2.0)
for i in range(4): S.sfx(T_AUP0 + 0.1 * i, "slide_up", 0.025, dur=0.6)
S.set(T_HUP0, "float", "dead_stare", dur=0.5, look=(0.0, 0.0), lid=0.35)
S.sfx(T_HUP0, "slide_up", 0.05, dur=1.6)
def his_lift(t):
    if T_HUP0 <= t < CUT_FALL - FR: return LIFT * smooth(ramp(t, T_HUP0, T_HUP1))
    if CUT_FALL - FR <= t < T_LAND:
        u = ramp(t, CUT_FALL, T_LAND, "linear"); return LIFT * 0.85 * (1 - u * u)
    return 0.0
S.cut(CUT_RISE - FR, cam=(JZ, FLOOR_Y - his_lift(CUT_RISE) - 380, 0.42))
_ck = []; t_ = CUT_RISE
while t_ < CUT_EXAM:
    _ck.append((t_, (JZ + 60, FLOOR_Y - his_lift(t_) - 360 - 40 * ramp(t_, CUT_RISE, T_HUP1), lerp(0.42, 0.52, ramp(t_, CUT_RISE, CUT_EXAM))), 0.1, "linear"))
    t_ += 0.1
S.camkeys += _ck
S.blink(35.6)

# under the ship: the exam
CAM_X = (JZ + 260, FLOOR_Y - LIFT - 360 - 120, 0.60)
S.cut(CUT_EXAM - FR, cam=CAM_X)
S.set(CUT_EXAM - FR, "float", "dead_stare", dur=0.0, look=(0.0, 0.0), lid=0.4)
S.set(T_LENS1 + 0.1, "float", "dead_stare", dur=0.3, turn=0.6, look=(1.0, 0.0), lid=0.3)
S.sfx(T_LENS0, "whoosh", 0.05, dur=0.4)
S.sfx(T_SCAN0, SCAN_WAV, 0.06)
S.set(T_SCAN1, "float", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lid=0.45)
S.sfx(T_BZZT, "buzzer", 0.08, dur=0.6)
S.camera(CUT_EXAM, *(JZ + 300, FLOOR_Y - LIFT - 480, 0.64), CUT_FALL - CUT_EXAM)

# the drop
CAM_G = cam(JZ + 250, 0.25, fs=1730)
S.cut(CUT_FALL - FR, cam=CAM_G)
S.set(CUT_FALL - FR, "cannonball", "dead_stare", dur=0.0, look=(0.0, 0.0), lid=0.3)
S.sfx(CUT_FALL, "slide_down", 0.05, dur=0.6)
S.set(T_LAND - 0.1, "sit_floor", "dead_stare", dur=0.1, ease="snap", look=(0.0, 0.0), lid=0.3)
S.sfx(T_LAND, "thud", 0.20); S.shake(T_LAND, 0.4, 9)
S.sfx(T_LEAVE, "whoosh", 0.10, dur=0.5); S.sfx(T_LEAVE + 0.45, "twinkle", 0.04)
S.set(T_LEAVE + 0.1, "sit_floor", "dead_stare", dur=0.3, look=(0.2, -1.0), lid=0.2)

# the sign
S.cut(CUT_SIGNC - FR, cam=cam(JZ + 280, 0.47, fs=1665))
S.set(CUT_SIGNC - FR, "sit_floor", "dead_stare", dur=0.0, look=(0.0, -0.3), lid=0.35)
S.sfx(T_SF0, "whoosh", 0.03, dur=0.4)
S.sfx(T_SF1, "thud", 0.12); S.sfx(T_SF1, "clack", 0.05); S.shake(T_SF1, 0.3, 6)
S.set(T_SF1 + 0.05, "sit_floor", "dead_stare", dur=0.08, ease="snap", look=(0.0, -0.3), lid=0.1, eyescale=1.08)
S.set(T_LOOKSIGN, "sit_floor", "dead_stare", dur=0.4, turn=0.7, look=(1.0, -0.6), tilt=-0.05, lid=0.3)
S.set(T_LOOKUS, "sit_floor", "dead_stare", dur=0.4, turn=0.0, look=(0.0, 0.0), tilt=0.0, lid=0.45)
S.camera(T_LOOKSIGN, *cam(JZ + 260, 0.52, fs=1655), 1.3)
S.cut(CUT_STAND2 - FR, cam=cam(JZ + 200, 0.50, fs=1660), x=JZ - 540)
S.set(CUT_STAND2 - FR, "stand", "dead_stare", dur=0.0, look=(0.0, 0.0), lid=0.4)

# ---------------------------------------------------------------- the ask (Jezero)
S.x = JZ - 540
S.the_ask(T_ASK, hold=HOLD, push=False)
S.camera(T_ASK + 6.9, *cam(JZ + 160, 0.55, fs=1650), 5.0)
T_END = S.t
S.blink(5.0, 12.3, 20.0, 29.2, 33.0, 46.0)

# camera follow during the ride
_ck = []
t_ = T_BOLT
while t_ < CUT_JZ - FR:
    X, lift, pitch, face, st = rex(t_)
    _ck.append((t_, cam(X + 350, 0.42, fs=1680), 0.1, "linear")); t_ += 0.1
S.camkeys += _ck
S.camkeys.sort(key=lambda k: k[0])

# ---------------------------------------------------------------- hooks
RIDING = ((CUT_RIDE - FR, CUT_STAND - FR),)
def riding(t): return any(a <= t < b for a, b in RIDING)

def hook_main(t, p):
    if riding(t):
        sx, sy = seat(t)
        hx, hy = p["hip"]
        dx, dy = sx - hx, sy - 30 - hy
        for k in L.JOINTS: p[k] = (p[k][0] + dx, p[k][1] + dy)
    if CUT_ROCK - FR <= t < CUT_PEEK - FR or CUT_WOW - FR <= t < CUT_BEHIND - FR:
        p["show"] = 0.0
    h = his_lift(t)
    if h > 0:
        bob = 14 * math.sin((t - T_HUP0) * 3.0) if t < CUT_FALL - FR else 0.0
        for k in L.JOINTS: p[k] = (p[k][0], p[k][1] - h + bob)
        p["nowalk"] = 1.0
    return p
S.hook(hook_main)

# ---------------------------------------------------------------- draw order
def insert_rock(cr, t):
    """his giant eye in the lens over the rock; a mitten flips it."""
    lx, ly = ROCK_X - 20, FLOOR_Y - 290
    def eye(cr2):
        cr2.rectangle(lx - 300, ly - 300, 600, 600); cr2.set_source_rgb(0.97, 0.97, 0.95); cr2.fill()
        lid = 0.0
        if T_EBLINK <= t < T_EBLINK + 0.2: lid = math.sin(math.pi * (t - T_EBLINK) / 0.2)
        look_dx = 0 if t < T_FLIP0 else 30 * smooth(ramp(t, T_FLIP0, T_FLIP1))
        cr2.arc(lx + look_dx, ly + 60, 95, 0, 2 * math.pi); cr2.set_source_rgb(*INKC); cr2.fill()
        cr2.arc(lx + look_dx - 30, ly + 25, 26, 0, 2 * math.pi); cr2.set_source_rgb(1, 1, 1); cr2.fill()
        cr2.rectangle(lx - 300, ly - 300, 600, 160 + 300 * (0.2 + 0.8 * lid)); cr2.set_source_rgb(0.97, 0.97, 0.95); cr2.fill()
        sketch_line(cr2, [(lx - 260, ly - 140 + 300 * (0.2 + 0.8 * lid) + 20), (lx + 260, ly - 140 + 300 * (0.2 + 0.8 * lid) + 20)], 10, sid=37900, amp=0.3)
    magnifier(cr, lx, ly, 200, ang=-2.3, inside=eye)
    hx, hy = lx + math.cos(-2.3) * 200 * 2.1, ly + math.sin(-2.3) * 200 * 2.1
    C.draw_hand(cr, (hx, hy), (hx - 60, hy - 60), "mitt", 1, sid=452)
    if T_FLIP0 - 0.35 <= t < T_FLIP1 + 0.3:                        # the other mitten flips the rock
        k = smooth(ramp(t, T_FLIP0 - 0.35, T_FLIP0)) * (1 - smooth(ramp(t, T_FLIP1, T_FLIP1 + 0.3)))
        u = ramp(t, T_FLIP0, T_FLIP1)
        mx, my = lerp(ROCK_X - 500, ROCK_X - 110 + 160 * u, k), lerp(FLOOR_Y - 60, FLOOR_Y - 60 - 120 * math.sin(math.pi * u), k)
        C.draw_hand(cr, (mx, my), (mx - 80, my + 10), "mitt", -1, sid=453)
    if T_FLIP1 <= t < T_FLIP1 + 0.5:
        q = ramp(t, T_FLIP1, T_FLIP1 + 0.5)
        O.draw_smoke_puff(cr, ROCK_X - 30, FLOOR_Y - 30 - 20 * q, 40 + 40 * q, alpha=0.6 * (1 - q), dark=0.25)

def insert_wow(cr, t):
    """a mitten with a red marker circles the signal and writes Wow!"""
    if not (T_CIRC0 - 0.3 <= t < T_WOW1 + 0.3): return
    yb = FLOOR_Y - 190; length = 700
    if t < T_CIRC1:
        a = -math.pi / 2 + 2 * math.pi * ramp(t, T_CIRC0, T_CIRC1, "linear")
        px, py = PRX + 78 * math.cos(a), yb - length + 90 + 2.5 * 95 + 320 * math.sin(a)
    else:
        u = ramp(t, T_WOW0, T_WOW1, "linear")
        px, py = PRX + 90 + 230 * u, yb - length + 140 + 20 * math.sin(u * 20)
    k = smooth(ramp(t, T_CIRC0 - 0.3, T_CIRC0)) * (1 - smooth(ramp(t, T_WOW1, T_WOW1 + 0.3)))
    px, py = lerp(PRX + 600, px, k), lerp(FLOOR_Y - 400, py, k)
    cr.save(); cr.translate(px, py); cr.rotate(-0.6)
    sk_rect(cr, -10, -150, 10, 0, 3, sid=37910, fill=(0.85, 0.12, 0.12))
    cr.restore()
    C.draw_hand(cr, (px + 70, py - 90), (px + 150, py - 40), "mitt", 1, sid=454)

def draw_exam(cr, t, layer):
    """under the ship: the giant eye behind a giant magnifying glass, the scan line."""
    if not (CUT_EXAM - FR <= t < CUT_FALL - FR): return
    k = smooth(ramp(t, T_LENS0, T_LENS1)) * (1 - smooth(ramp(t, T_LENSOUT, T_LENSOUT + 0.3)))
    lx = lerp(JZ + 1900, JZ + 760, k); ly = FLOOR_Y - LIFT - 420
    if layer == "back":
        # the giant head behind the lens
        sk_ell(cr, lx + 900, ly - 60, 820, 1050, 10, sid=37920, fill=GREEN)
        def eye(cr2):
            cr2.rectangle(lx - 500, ly - 500, 1000, 1000); cr2.set_source_rgb(*GREEN); cr2.fill()
            sq = smooth(ramp(t, T_SQUINT, T_SQUINT + 0.15))
            cr2.save(); cr2.translate(lx + 40, ly); cr2.rotate(-0.45); cr2.scale(330, 190 * (1 - 0.65 * sq)); cr2.arc(0, 0, 1, 0, 2 * math.pi); cr2.restore()
            cr2.set_source_rgb(0.04, 0.05, 0.06); cr2.fill()
            cr2.arc(lx - 80, ly - 70 * (1 - 0.6 * sq), 50, 0, 2 * math.pi); cr2.set_source_rgba(1, 1, 1, 0.9); cr2.fill()
            if sq > 0.05:
                sketch_line(cr2, [(lx - 340, ly - 250 + 120 * sq), (lx + 380, ly - 330 + 120 * sq)], 14, sid=37925, amp=0.3)
        magnifier(cr, lx, ly, 380, ang=0.55, inside=eye, sid=37930)
        return
    if T_SCAN0 <= t < T_SCAN1:
        u = ramp(t, T_SCAN0, T_SCAN1, "linear")
        y = lerp(FLOOR_Y - LIFT - 960, FLOOR_Y - LIFT + 20, u)
        cr.rectangle(JZ - 330, y - 8, 660, 16); cr.set_source_rgba(0.4, 1.0, 0.4, 0.75); cr.fill()
        cr.move_to(lx - 300, ly); cr.line_to(JZ - 330, y); cr.line_to(JZ + 330, y); cr.close_path()
        cr.set_source_rgba(0.6, 1.0, 0.55, 0.18); cr.fill()
    if T_BZZT <= t < T_BZZT + 0.5:
        cr.arc(lx - 360, ly - 400, 46, 0, 2 * math.pi); cr.set_source_rgb(0.95, 0.15, 0.12); cr.fill()
        L.burst_lines(cr, lx - 360, ly - 400, ramp(t, T_BZZT, T_BZZT + 0.5), r0=60, r1=120, n=8, sid=22)

def props_back(cr, t, p, ly):
    if ly != "back": return
    if t < CUT_JZ - FR:
        draw_rover_j(cr, t); draw_rex(cr, t); return
    if CUT_ROCK - FR <= t < CUT_PEEK - FR:
        return
    if CUT_EXAM - FR <= t < CUT_FALL - FR:
        draw_exam(cr, t, "back"); return
    draw_rover_j(cr, t)
    draw_rex(cr, t)
    glass_on_ground(cr, t)
    if t >= T_SLAND or CUT_WOW - FR <= t < CUT_BEHIND - FR: strip_draw(cr, t, p)
    draw_ground_aliens(cr, t)
S.prop(props_back)

def world(cr, t):
    if t < CUT_JZ - FR: draw_cydonia(cr, t); return
    draw_jezero(cr, t)
    if CUT_EXAM - FR <= t < CUT_FALL - FR:
        mothership(cr, SHIP_X, SHIP_Y1 + 25 * math.sin(t * 2.2), t=t)
S.background(world)

def draw_my_helmet(cr, t, p):
    if p.get("show", 1.0) < 0.5: return
    hx, hy = p["head"]
    helmet(cr, hx + 6, hy - 10, 175, sid=33000)

def props_front(cr, t, p, ly):
    if ly != "front": return
    draw_my_helmet(cr, t, p)
    if CUT_BEHIND - FR <= t < T_SDROP: strip_draw(cr, t, p)
    if T_SDROP <= t < T_SLAND: strip_draw(cr, t, p)
    if CUT_ROCK - FR <= t < CUT_PEEK - FR: insert_rock(cr, t)
    if CUT_WOW - FR <= t < CUT_BEHIND - FR: insert_wow(cr, t)
    draw_exam(cr, t, "front")
    # the beam
    if beam_on(t) and not (CUT_EXAM - FR <= t < CUT_FALL - FR):
        k = beam_k(t)
        sy = ship_y(t) or SHIP_Y1
        beam(cr, SHIP_X, sy + 0.2 * SHIP_R, JZ + 420, FLOOR_Y + 20, 700 * k, 1500 * k, a=k, t=t)
    if CUT_EXAM - FR <= t < CUT_FALL - FR:
        beam(cr, SHIP_X, SHIP_Y1 + 0.2 * SHIP_R, JZ + 420, FLOOR_Y + 20, 700, 1500, a=0.8, t=t)
    # the ride: dust devil + wipe
    if CUT_RIDE - FR <= t < CUT_JZ - FR:
        if t >= CUT_JZ - 1.1: E35.draw_dust_devil(cr, t, DD2)
        if t >= CUT_JZ - 0.35:
            vx0, vy0, vx1, vy1 = O._visible(cr)
            cr.rectangle(vx0 - 100, vy0 - 100, vx1 - vx0 + 200, vy1 - vy0 + 200)
            cr.set_source_rgba(0.80, 0.55, 0.40, ramp(t, CUT_JZ - 0.35, CUT_JZ - 0.05)); cr.fill()
    if CUT_JZ - FR <= t < CUT_JZ + 0.5:
        k = 1 - ramp(t, CUT_JZ, CUT_JZ + 0.5)
        for j in range(6):
            O.draw_smoke_puff(cr, REX_J - 1500 + 200 * math.sin(j), FLOOR_Y - 300 - 300 * j, 400, alpha=0.9 * k, dark=0.15)
    if T_LAND <= t < T_LAND + 0.45:
        q = ramp(t, T_LAND, T_LAND + 0.45)
        for d in (-1, 1):
            O.draw_smoke_puff(cr, JZ + d * 150, FLOOR_Y - 40, 110 * (1 + q), alpha=0.7 * (1 - q), dark=0.25)
    # the NO INTELLIGENT LIFE FOUND sign
    if t >= T_SF0 and t >= CUT_SIGNC - FR:
        u = ramp(t, T_SF0, T_SF1)
        if u < 1:
            y = lerp(FLOOR_Y - 2600, FLOOR_Y + 30, u * u); ang = 0.5 * math.sin(u * 9) * (1 - u)
            nil_sign(cr, SIGN_X + 120 * math.sin(u * 5) * (1 - u), y, ang)
        else:
            wob = 0.06 * math.sin((t - T_SF1) * 28) * math.exp(-(t - T_SF1) * 5)
            nil_sign(cr, SIGN_X, FLOOR_Y + 30, wob)
            if t < T_SF1 + 0.35:
                L.burst_lines(cr, SIGN_X, FLOOR_Y - 20, (t - T_SF1) / 0.35, r0=60, r1=150, n=8, sid=23)
S.prop(props_front)

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        S.build()
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, L.W, L.H)
        for a in sys.argv[2:]:
            tt = float(a); L.render_frame(tt, surf); surf.write_to_png(os.path.join(HERE, "still_%05.2f.png" % tt))
        print("dur", T_END)
    else:
        S.render("day036.mp4")
