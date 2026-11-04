"""Day 13 - COMMENT episode: @second_degree_burn "Go to the movies!" (Instagram, day 12 reel, 0 likes).
Deadpan, Family Guy timing. The kitten rides on his head the whole time (the bored straight man), never harmed.
See BEATS.md for the beat sheet + gate.

PARK EXIT -> run right through the park's back gate -> MEGAPLEX 30 (NO PETS: the kitten becomes a hat; the usher
stares) -> LOBBY (SMALL popcorn, $47.50, the TIP SCREEN) -> THEATER (empty; the tall guy in a top hat sits right in
front; 47 previews; the popcorn is gone before the movie; 4D: water, fans, rodeo -> the tall guy is launched through
the roof, he loops the theater, finally sees the movie) -> credits -> post-credits: the tall guy drops back in -> ASK.
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
KS = 0.62

# ================================================================ places
# park (day 12/13): the coaster track is rebuilt here exactly as in ep012 so the exit station matches
HANG_X = 45700.0
Y0 = FLOOR_Y - 40
def catmull(knots, n=24):
    out = []
    P = [knots[0]] + list(knots) + [knots[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            u = k / n; u2, u3 = u * u, u * u * u
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u3) for j in (0, 1)))
    out.append(knots[-1]); return out
def loop_pts(cx, R, d, n=160):
    return [(cx + R * math.sin(th) + d * th, Y0 - R + R * math.cos(th)) for th in [2 * math.pi * k / n for k in range(n + 1)]]
L1X, L1R, L1D = 48000.0, 700.0, 80.0
L2X, L2R, L2D = 51200.0, 520.0, 70.0
EDGE_X = 45950.0
raw = catmull([(42500, Y0), (43350, Y0), (43750, Y0 - 220), (45300, Y0 - 1700), (45650, Y0 - 1890), (EDGE_X, Y0 - 1870),
               (46280, Y0 - 900), (46480, Y0 - 150), (46900, Y0), (L1X - 1, Y0)])
raw += loop_pts(L1X, L1R, L1D)
raw += catmull([(L1X + 2 * math.pi * L1D + 1, Y0), (49000, Y0), (49600, Y0 - 650), (50200, Y0), (L2X - 1, Y0)])[1:]
raw += loop_pts(L2X, L2R, L2D)
raw += catmull([(L2X + 2 * math.pi * L2D + 1, Y0), (52500, Y0), (55000, Y0)])[1:]
DRAW_TRK = raw[::3]
S_STOPX = 53400.0
XE = S_STOPX + 880; SXE = XE - 540            # the exit station spot (day 12's ask, day 13)
SCREEN = (XE + 560, 830)
GATE2 = 56000.0                               # the park's back gate: hides the park / night-street seam
MX = 58400.0                                  # MEGAPLEX 30 (doors MX-200..MX+200)
SIGN_X = MX - 520.0                           # NO PETS
XSTOP = 57300.0                               # where his run ends
XDOOR = MX - 130.0                            # where he stands at the door
XUSH = MX + 330.0                             # the usher
LX = 80000.0                                  # the lobby set
XCOUNT = LX - 350.0                           # him at the counter
CASH_X = LX + 230.0
READER_X = LX - 40.0
BUCKET_X = LX + 500.0
COUNTER_Y = 1130.0
TX = 100000.0                                 # the theater, from behind
FX = 120000.0                                 # the theater, from the front (his seat)
ASKX = 121250.0                               # the aisle (the ask)

# ================================================================ timeline
T_READ = 0.3
T_TURN = 1.75
T_RUN, T_RUN1 = 2.0, 4.1
T_LOOKUP = 4.5
T_WALK, T_WALK1 = 5.5, 6.4
T_SIGN = 6.55; T_UPCAT = 7.0; T_FLAT = 7.25
T_STARE = 7.9; T_TWITCH = 9.6; T_NARROW = 10.3; T_STEP = 10.75; T_IN = 11.4
CUT_LOBBY = 12.0
T_POINT = 12.3; T_DROP = 12.9; T_LOOKB = 13.3; T_TAP = 14.0; T_SWIVEL = 14.35
CUT_TIP1 = 14.8
CUT_TWO = 16.3
CUT_TIP2 = 18.2; T_SLIDE = 18.55; T_PRESS = 19.0; T_TOTAL = 19.25
CUT_TAKE = 19.9
CUT_THEATER = 20.9
T_GIANT_IN = 21.6; T_GIANT_SIT = 23.2
T_LEAN1 = 23.7; T_LEAN2 = 24.5
CUT_STARE = 25.4
CUT_PREV1 = 26.8
CUT_EAT = 28.2
CUT_PREV47 = 31.4
CUT_EMPTY = 32.4; T_RATTLE = 32.9; T_KERNEL = 33.8; T_EATK = 34.3
CUT_4D = 35.2
CUT_SEAT = 36.4; T_TILT = 36.6; T_WATER = 37.2; T_WATER1 = 37.9
T_FANS = 38.9; T_FANS1 = 40.4
T_RODEO = 40.4
CUT_LAUNCH = 42.2; T_GLAUNCH = 42.7; T_CRASH = 42.88
T_LOOP0 = 43.7; T_LOOP1 = 45.9
T_BOOM = 46.2
CUT_LIT = 47.8; T_BOING = 48.2
CUT_CREDITS = 49.6; T_END = 49.6; T_LIGHTS = 50.2; T_ROLL0 = 50.6; T_ROLL1 = 52.4
T_POST = 52.4; T_GFALL = 52.9; T_GLAND = 53.25
CUT_ASK = 55.3
T_ASK = 55.5
ASK_HOLD = 7.0

S = M.Scene(x0=SXE)
S.auto_blinks = False
S.floor = False
S.card("second_degree_burn", "Go to the movies!", "0", t0=0.3)
CAM0 = (XE + 60, 930, 1.12)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0
TK = []                                       # (t, kind, a) world-set switches, for the background

def setting(t):
    if t < CUT_LOBBY - FR: return "street"
    if t < CUT_THEATER - FR: return "lobby"
    if CUT_ASK - FR <= t: return "front"
    for a, b in ((CUT_STARE, CUT_PREV1), (CUT_EAT, CUT_PREV47), (CUT_EMPTY, CUT_4D), (CUT_SEAT, CUT_LAUNCH), (CUT_LIT, CUT_CREDITS)):
        if a - FR <= t < b - FR: return "front"
    return "back"

# ================================================================ helpers
def npc_pose(x, face="deadpan", body="stand", **kw):
    p = L.pose(body, face, **kw)
    ox = x - 540
    for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1])
    p["breath_ph"] = 0.0
    return L.constrain(p)

def mini_photo(cr, x, y, s, ang=0.0):
    cr.save(); cr.translate(x, y); cr.rotate(ang + 0.12); cr.scale(s, s)
    sketch_rect(cr, -90, -70, 90, 70, 5, sid=13300, fill=(1, 1, 1))
    cr.save(); cr.rectangle(-78, -58, 156, 100); cr.clip(); cr.translate(-78, -58)
    photo_inner(cr, 0, 0, 156, 100); cr.restore()
    cr.restore()
def photo_inner(cr, x0, y0, w, h):
    cr.rectangle(x0, y0, w, h); cr.set_source_rgb(0.62, 0.82, 0.98); cr.fill()
    cr.rectangle(x0, y0 + h * 0.72, w, h * 0.06); cr.set_source_rgb(0.36, 0.58, 0.92); cr.fill()
    cr.rectangle(x0 + w * 0.3, y0 + h * 0.5, w * 0.4, h * 0.22); cr.set_source_rgb(0.85, 0.25, 0.3); cr.fill()
    cr.arc(x0 + w * 0.5, y0 + h * 0.36, h * 0.11, 0, 2 * math.pi); cr.set_source_rgb(1, 1, 1); cr.fill_preserve()
    cr.set_source_rgb(0.1, 0.1, 0.12); cr.set_line_width(3); cr.stroke()
    cr.arc(x0 + w * 0.5, y0 + h * 0.18, h * 0.07, 0, 2 * math.pi); cr.set_source_rgb(0.1, 0.1, 0.12); cr.fill()

# ================================================================ STREET (park exit -> megaplex)
def usher_pose(t):
    face, kw = "deadpan", dict(turn=-0.5, look=(-0.8, 0.0))
    if t >= T_STARE: kw.update(look=(-0.75, -0.75))                        # up at the "hat"
    if t >= T_NARROW: kw.update(lid=0.62)
    if t >= T_STEP + 0.3: kw.update(lid=0.36, look=(-0.8, 0.0))
    body = "stand"
    p = npc_pose(XUSH + 90 * smooth(ramp(t, T_STEP, T_STEP + 0.5)), face, body, **kw)
    g = smooth(ramp(t, T_STEP + 0.2, T_STEP + 0.55)) * (1 - smooth(ramp(t, T_IN + 0.4, T_IN + 0.8)))
    if g > 0:                                                              # waves him in (palm open, toward the door)
        p["lhand"] = lerp(p["lhand"], (p["neck"][0] - 210, p["neck"][1] + 170), g); p["lelb"] = lerp(p["lelb"], (p["neck"][0] - 120, p["neck"][1] + 220), g)
        p["lhand_t"] = "open"
    return L.constrain(p)

def street(cr, t):
    O.draw_park_world(cr, t, x0=38550, x1=GATE2)
    O.draw_track(cr, DRAW_TRK, FLOOR_Y)
    sx = S_STOPX
    sketch_rect(cr, sx - 700, FLOOR_Y - 30, sx + 700, FLOOR_Y + 40, 5, sid=13200 + int(sx) % 7, fill=(0.75, 0.66, 0.58))
    for px in (sx - 650, sx + 650):
        sketch_rect(cr, px - 18, FLOOR_Y - 1000, px + 18, FLOOR_Y - 30, 5, sid=13210 + int(px) % 9, fill=(0.98, 0.95, 0.9))
    sketch_poly(cr, [(sx - 760, FLOOR_Y - 1000), (sx, FLOOR_Y - 1160), (sx + 760, FLOOR_Y - 1000)], 6, sid=13220 + int(sx) % 5, fill=O.PARK_TEAL)
    sketch_rect(cr, sx - 330, FLOOR_Y - 1080, sx + 330, FLOOR_Y - 940, 5, sid=13230 + int(sx) % 5, fill=(1, 1, 0.97))
    draw_text(cr, "EXIT", sx, FLOOR_Y - 1010, 84, color=(200, 50, 60), max_w=620)
    O.draw_photo_screen(cr, SCREEN[0], SCREEN[1], w=640, h=480, inner=photo_inner)
    sketch_rect(cr, SCREEN[0] - 40, SCREEN[1] + 255, SCREEN[0] + 40, FLOOR_Y, 5, sid=13250, fill=(0.3, 0.3, 0.34))
    O.draw_city_night(cr, t, GATE2, 66000, fade=1800)
    O.draw_park_gate(cr, GATE2, FLOOR_Y, t, sign="BYE NOW!")
    O.draw_megaplex(cr, MX, FLOOR_Y, t)
    O.draw_no_pets(cr, SIGN_X, FLOOR_Y)
    O.draw_staff(cr, t, usher_pose(t), 0.0, s=1.05, kind="usher")

# ================================================================ LOBBY
def cashier_pose(t):
    kw = dict(turn=-0.55, look=(-0.8, 0.0))
    if t >= CUT_TWO - FR: kw.update(look=(-0.85, -0.05), lid=0.45)
    p = npc_pose(CASH_X, "deadpan", "stand", **kw)
    if T_POINT + 0.3 <= t < T_DROP + 0.25:                                # lifts the bucket onto the counter
        g = smooth(ramp(t, T_POINT + 0.3, T_DROP - 0.2))
        for s_, dx in (("l", -60), ("r", 60)):
            p[s_ + "hand"] = lerp(p[s_ + "hand"], (BUCKET_X + dx, COUNTER_Y - 380 - 60 * g), 1.0)
            p[s_ + "elb"] = (p[s_ + "hand"][0] + (60 if s_ == "r" else 20), p[s_ + "hand"][1] + 140)
    return L.constrain(p)

def bucket_on_counter(t): return T_DROP - 0.05 <= t < CUT_TAKE - FR

def lobby(cr, t):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    cr.rectangle(vx0, vy0, vx1 - vx0, FLOOR_Y - vy0); cr.set_source_rgb(0.40, 0.10, 0.14); cr.fill()
    for k in range(int((vx0 - LX) // 300) - 1, int((vx1 - LX) // 300) + 2):       # wall panels
        sketch_line(cr, [(LX + k * 300, vy0), (LX + k * 300, FLOOR_Y)], 4, sid=14300 + k % 5, color=(0.30, 0.06, 0.10))
    cr.rectangle(vx0, FLOOR_Y, vx1 - vx0, vy1 - FLOOR_Y); cr.set_source_rgb(0.30, 0.08, 0.12); cr.fill()
    for k in range(int((vx0 - LX) // 120), int((vx1 - LX) // 120) + 2):           # carpet dots
        for j in range(3):
            cr.arc(LX + k * 120 + 60 * (j % 2), FLOOR_Y + 60 + j * 110, 8, 0, 2 * math.pi); cr.set_source_rgb(*O.CINE_GOLD); cr.fill()
    sketch_line(cr, [(vx0, FLOOR_Y), (vx1, FLOOR_Y)], 4, sid=14310)
    # menu board
    bx, by = LX + 120, 300
    sketch_rect(cr, bx - 420, by - 140, bx + 420, by + 330, 7, sid=14311, fill=(0.10, 0.10, 0.12))
    draw_text(cr, "POPCORN", bx, by - 70, 74, color=(255, 214, 80))
    for i, (sz, pr) in enumerate((("SMALL", "$47.50"), ("MEDIUM", "$62.00"), ("LARGE", "ASK"))):
        draw_text(cr, sz, bx - 160, by + 40 + i * 90, 56, color=(255, 255, 255))
        draw_text(cr, pr, bx + 190, by + 40 + i * 90, 56, color=(255, 255, 255))
    # a poster on the left wall
    sketch_rect(cr, LX - 1000, 380, LX - 640, 900, 7, sid=14312, fill=(0.12, 0.10, 0.16))
    O.draw_boom(cr, LX - 820, 620, 130, t=t, sid=14313)
    draw_text(cr, "EXPLOSION 7", LX - 820, 840, 42, color=(255, 214, 80), max_w=330)
    # popcorn machine behind the counter
    sketch_rect(cr, LX + 620, 520, LX + 900, COUNTER_Y, 6, sid=14314, fill=(0.85, 0.20, 0.22))
    sketch_rect(cr, LX + 645, 560, LX + 875, 900, 5, sid=14315, fill=(1.0, 0.95, 0.75))
    # the cashier, behind the counter
    if CUT_LOBBY - FR <= t:
        O.draw_staff(cr, t, cashier_pose(t), 0.0, s=0.88, kind="cashier")
    if bucket_on_counter(t):
        u = ramp(t, T_DROP - 0.05, T_DROP + 0.05, "linear")
        O.draw_popcorn(cr, BUCKET_X, COUNTER_Y + 10 - 60 * (1 - u), s=0.98, level=1.0, t=t)
    sketch_rect(cr, LX - 160, COUNTER_Y, LX + 1100, FLOOR_Y, 7, sid=14316, fill=(0.55, 0.30, 0.18))
    sketch_rect(cr, LX - 190, COUNTER_Y - 30, LX + 1130, COUNTER_Y + 10, 6, sid=14317, fill=(0.68, 0.42, 0.26))
    sketch_rect(cr, LX - 100, COUNTER_Y + 80, LX + 1040, COUNTER_Y + 220, 5, sid=14318, fill=(1.0, 0.92, 0.62))
    draw_text(cr, "CONCESSIONS", LX + 470, COUNTER_Y + 150, 64, color=(140, 40, 40))
    ang = 0.0 if t < T_SWIVEL else lerp(0.0, math.pi, smooth(ramp(t, T_SWIVEL, T_SWIVEL + 0.4)))
    O.draw_card_reader(cr, READER_X, COUNTER_Y - 25, ang=ang)

# ================================================================ THEATER (from behind)
BACKCAM = (TX, 800, 0.95)
WIDECAM = (TX, 560, 0.8)
SCR = (TX - 440, 100, TX + 440, 640)          # the movie screen
G_ROW_Y, H_ROW_Y, N_ROW_Y = 790.0, 905.0, 1190.0
GIANT_SHOULDER_Y = 880.0
GS = 1.15
def lights(t): return smooth(ramp(t, T_LIGHTS, T_LIGHTS + 1.0))
def wall_col(t, base): return lerp(base, (0.62, 0.46, 0.48), 0.6 * lights(t))

def giant_state(t):
    """(x, y, visible) of the tall guy's shoulders in the back view."""
    if t < T_GIANT_IN: return None
    x_in = TX + 1000
    if t < T_GIANT_SIT:
        u = smooth(ramp(t, T_GIANT_IN, T_GIANT_SIT - 0.25))
        x = lerp(x_in, TX, u); y = GIANT_SHOULDER_Y - 200 + 12 * abs(math.sin(t * 7)) * (1 - u)
        if t > T_GIANT_SIT - 0.25: y = lerp(GIANT_SHOULDER_Y - 200, GIANT_SHOULDER_Y, smooth(ramp(t, T_GIANT_SIT - 0.25, T_GIANT_SIT)))
        return (x, y)
    if t < T_GLAUNCH:
        return (TX + lean_giant(t), GIANT_SHOULDER_Y + rodeo_dy(t, 0.7))
    if t < T_GFALL:
        u = t - T_GLAUNCH
        return (TX, GIANT_SHOULDER_Y - 6000 * u * u - 400 * u) if u < 0.5 else None
    u = smooth(ramp(t, T_GFALL, T_GLAND, "linear")) if t < T_GLAND else 1.0
    yy = lerp(-900, GIANT_SHOULDER_Y, ramp(t, T_GFALL, T_GLAND, "linear") ** 2)
    return (TX, yy + 18 * pulse(t, T_GLAND + 0.05, 0.08))

def lean_amt(t):
    """his head lean in the back view (-1 left .. +1 right)."""
    return -1.0 * smooth(ramp(t, T_LEAN1, T_LEAN1 + 0.3)) + 2.0 * smooth(ramp(t, T_LEAN2, T_LEAN2 + 0.35)) - 1.0 * smooth(ramp(t, CUT_STARE - 0.3, CUT_STARE))
def lean_giant(t): return 150 * lean_amt(t - 0.35)

def rodeo_k(t): return smooth(ramp(t, T_RODEO, T_RODEO + 1.2)) * (1 - smooth(ramp(t, T_LOOP0 - 0.3, T_LOOP0)))
def rodeo_dy(t, a=1.0):
    k = rodeo_k(t)
    if k <= 0: return 0.0
    f = 3.0 + 4.0 * ramp(t, T_RODEO, T_RODEO + 2.5)
    return -a * k * 55 * abs(math.sin(t * f * math.pi))
def tilt_4d(t): return 22 * smooth(ramp(t, T_TILT, T_TILT + 0.5)) * (1 - smooth(ramp(t, T_FANS1, T_FANS1 + 0.3)))

def loop_u(t): return smooth(ramp(t, T_LOOP0, T_LOOP1)) if T_LOOP0 <= t < T_LOOP1 + 0.4 else 0.0
LOOP_R = 340.0
def loop_xform(t):
    """(dx, dy, ang) of his seat during the loop around the theater (back view)."""
    u = loop_u(t)
    if u <= 0 or u >= 1: return (0.0, 0.0, 0.0)
    th = 2 * math.pi * u
    return (LOOP_R * 0.9 * math.sin(th), -LOOP_R * (1 - math.cos(th)), th)

def screen_content(cr, t):
    x0, y0, x1, y1 = SCR; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    def big(txt, size=84, y=cy, col=(240, 240, 240)): draw_text(cr, txt, cx, y, size, color=col, max_w=x1 - x0 - 60)
    def strip(txt):
        for i, part in enumerate(txt.split("|")): draw_text(cr, part, x0 + 24, y0 + 40 + 44 * i, 40, color=(255, 214, 80), anchor="left")
    if t < CUT_PREV1 - FR:
        big("PLEASE SILENCE", 76, cy - 60); big("YOUR PHONES", 76, cy + 40)
    elif t < CUT_PREV47 - FR:
        strip("PREVIEW|1 OF 47"); big("IN A WORLD...", 90)
    elif t < CUT_4D - FR:
        strip("PREVIEW|47 OF 47"); big("COMING SOON", 90)
    elif t < T_BOOM:
        strip("FEATURE|PRESENTATION"); big("4D", 200, cy, col=(255, 214, 80))
    elif t < T_END:
        u = ramp(t, T_BOOM, T_BOOM + 0.5)
        cr.rectangle(x0, y0, x1 - x0, y1 - y0); cr.set_source_rgb(0.98, 0.70, 0.30); cr.fill()
        O.draw_boom(cr, cx, cy + 20, 120 + 330 * back_out(u, 1.4), t=t, sid=14400)
        draw_text(cr, "KA-BOOM", cx, cy + 20, 120, color=(140, 30, 20), rot=-0.06, alpha=min(1.0, u * 3))
    elif t < T_ROLL0:
        big("THE END", 110)
    elif t < T_POST:
        u = (t - T_ROLL0) / (T_ROLL1 - T_ROLL0)
        lines = ["EXPLOSION 7", "", "DIRECTED BY", "SOMEBODY", "", "4D EFFECTS", "A GUY WITH A HOSE", "", "NO PETS WERE", "ALLOWED"]
        for i, ln in enumerate(lines):
            if not ln: continue
            yy = y1 + 40 + i * 70 - u * (len(lines) * 70 + 600)
            if y0 + 20 < yy < y1 - 10: draw_text(cr, ln, cx, yy, 50, color=(230, 230, 230), max_w=x1 - x0 - 60)
    else:
        big("POST-CREDITS", 92, cy - 50); big("SCENE", 92, cy + 50)

def theater_back(cr, t):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    cr.rectangle(vx0, vy0, vx1 - vx0, vy1 - vy0); cr.set_source_rgb(*wall_col(t, (0.14, 0.09, 0.12))); cr.fill()
    ceil = -40.0
    cr.rectangle(vx0, vy0, vx1 - vx0, ceil - vy0); cr.set_source_rgb(*wall_col(t, (0.08, 0.06, 0.09))); cr.fill()
    for k in range(-6, 7): sketch_line(cr, [(TX + k * 260, vy0), (TX + k * 260, ceil)], 3, sid=14500 + k % 4, color=(0.20, 0.16, 0.20))
    sketch_line(cr, [(vx0, ceil), (vx1, ceil)], 5, sid=14510)
    if t >= T_CRASH:                                                          # the hole the tall guy went through
        pts = [(TX - 190, ceil), (TX - 150, ceil - 70), (TX - 60, ceil - 40), (TX, ceil - 110), (TX + 80, ceil - 50), (TX + 170, ceil - 80), (TX + 200, ceil)]
        sketch_poly(cr, pts + [(TX + 200, vy0), (TX - 190, vy0)], 5, sid=14511, fill=(0.10, 0.12, 0.26))
        for k in range(5):
            cr.arc(TX - 120 + 60 * k, ceil - 300 - 90 * (k % 2), 4, 0, 2 * math.pi); cr.set_source_rgb(1, 1, 0.85); cr.fill()
        cr.move_to(TX - 170, ceil); cr.line_to(TX + 180, ceil); cr.line_to(TX + 420, FLOOR_Y); cr.line_to(TX - 420, FLOOR_Y); cr.close_path()
        cr.set_source_rgba(0.85, 0.88, 1.0, 0.10); cr.fill()
    # curtains + screen
    for d in (-1, 1):
        x_ = TX + d * 470
        sketch_rect(cr, x_ - 70, ceil, x_ + 70, 760, 5, sid=14512 + (d > 0), fill=O.CINE_RED_D)
    x0, y0, x1, y1 = SCR
    sketch_rect(cr, x0, y0, x1, y1, 6, sid=14514, fill=(0.10, 0.10, 0.13))
    cr.save(); cr.rectangle(x0, y0, x1 - x0, y1 - y0); cr.clip(); screen_content(cr, t); cr.restore()
    sketch_rect(cr, x0, y0, x1, y1, 6, sid=14515, fill=None)
    # the 4D sign on the left wall
    on = T_4D_ON <= t
    sketch_rect(cr, TX - 660, 470, TX - 540, 610, 5, sid=14516, fill=(1.0, 0.85, 0.3) if on else (0.25, 0.22, 0.24))
    draw_text(cr, "4D", TX - 600, 540, 60, color=(160, 30, 30) if on else (90, 80, 85))
    # far rows, then the tall guy's row
    O.draw_seat_row(cr, TX, 680, n=11, w=150, h=120, gap=12, s=0.75, sid=14520)
    g = giant_state(t)
    clip_hole = t >= T_CRASH and (t < T_GFALL)
    if g:
        cr.save()
        if T_GLAUNCH <= t < T_GFALL or (T_GFALL <= t < T_GLAND):
            cr.rectangle(vx0, ceil - 120, vx1 - vx0, vy1); cr.clip()
        O.draw_giant_back(cr, g[0], g[1] + rodeo_dy(t, 0.7) * (t < T_GLAUNCH), s=GS, tilt=0.03 * math.sin(t * 2))
        if T_GLAUNCH <= t < T_GLAUNCH + 0.4:
            for k in range(5): L.motion_lines(cr, g[0] - 160 + 80 * k, g[1] + 330, math.pi / 2, n=1, length=420, alpha=0.9, sid=14570 + k, width=7)
        cr.restore()
    skip = ()
    O.draw_seat_row(cr, TX, G_ROW_Y + rodeo_dy(t, 0.5), n=11, w=170, h=150, gap=14, s=0.85, sid=14540, skip=skip)
    if CUT_4D - FR <= t < T_RODEO:                                           # rumble
        pass
    if t < T_CRASH + 0.6 and t >= T_CRASH:                                 # debris
        for k in range(8):
            u = (t - T_CRASH) / 0.6
            dx = (k - 3.5) * 70 * (1 + u); dy = ceil + 1600 * u * u * (0.6 + 0.1 * k) - 200 * u
            sketch_rect(cr, TX + dx - 20, dy - 20, TX + dx + 20, dy + 20, 4, sid=14560 + k, fill=(0.35, 0.30, 0.34))
def T_PREV_DARK(t): return False
T_4D_ON = CUT_4D + 0.3

def world(cr, t):
    st = setting(t)
    if st == "street": street(cr, t)
    elif st == "lobby": lobby(cr, t)
    elif st == "back": theater_back(cr, t)
    else: theater_front(cr, t)
S.background(world)

# ================================================================ THEATER (from the front: his seat)
FRONTCAM = (FX + 60, 860, 1.2)
SEAT_Y = 740.0
def screen_light(t):
    """colour of the light from the screen on the front set."""
    if T_BOOM <= t < T_END: return (0.98, 0.62, 0.28), 0.10 + 0.03 * math.sin(t * 20)
    return (0.55, 0.65, 0.95), 0.10 + 0.03 * math.sin(t * 5.3) * math.sin(t * 2.1)
def seat_dy(t): return rodeo_dy(t) + (-tilt_4d(t) * 0.3)
def theater_front(cr, t):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    cr.rectangle(vx0, vy0, vx1 - vx0, vy1 - vy0); cr.set_source_rgb(*wall_col(t, (0.12, 0.08, 0.11))); cr.fill()
    for k in range(-2, 7):                                                  # empty rows behind him
        O.draw_seat_front(cr, FX - 900 + k * 300 + 150, 380, s=0.62, sid=14600 + k, part="all")
    cr.rectangle(vx0, 640, vx1 - vx0, 40); cr.set_source_rgb(*wall_col(t, (0.20, 0.12, 0.15))); cr.fill()
    for k in range(-3, 8):
        if k == 0: continue
        O.draw_seat_front(cr, FX + k * 300, SEAT_Y, s=1.0, sid=14620 + k, part="all")
    O.draw_seat_front(cr, FX, SEAT_Y + seat_dy(t), s=1.0, sid=14620, part="back")
    cr.rectangle(vx0, FLOOR_Y, vx1 - vx0, vy1 - FLOOR_Y); cr.set_source_rgb(0.22, 0.10, 0.12); cr.fill()
    if t >= CUT_ASK - FR:                                                   # the aisle (the ask): steps with little lights
        for k in range(3):
            cr.arc(ASKX - 300 + k * 300, FLOOR_Y + 40, 9, 0, 2 * math.pi); cr.set_source_rgb(*O.CINE_GOLD); cr.fill()

# ================================================================ HIM
# --- park exit, read, run
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(T_READ, react="deadpan", lines=1, dur=1.3, face="deadpan")
S.set(T_TURN, "stand", "deadpan", dur=0.25, look=(0.9, 0.0), turn=0.5)
S.set(T_RUN, "stand", "deadpan", dur=0.15, run=1.0, look=(0.9, 0.0), turn=0.5, lean=0.12)
S.xkeys.append((T_RUN, XSTOP - 540, T_RUN1 - T_RUN, "smooth")); S.x = XSTOP - 540
S.set(T_RUN1 - 0.1, "stand", "deadpan", dur=0.15, run=0.0, look=(0.6, -0.5), stretch=-0.2, turn=0.4)
S.set(T_RUN1 + 0.1, "stand", "deadpan", dur=0.3, ease="back", look=(0.5, -0.8), turn=0.3)
S.set(T_LOOKUP, "stand", "deadpan", dur=0.5, look=(0.4, -1.0), brow=0.25, turn=0.2)
S.sfx(T_RUN, "whoosh", 0.05); S.sfx(T_RUN1 - 0.1, "skid", 0.05, dur=0.3)
def run_x(t): return 540 + lerp(SXE, XSTOP - 540, smooth(ramp(t, T_RUN, T_RUN1)))
_ct = T_RUN - 0.05
while _ct < T_RUN1 + 0.2:
    S.camera(_ct, run_x(_ct + 0.05) + 200, 930, lerp(1.12, 0.8, smooth(ramp(_ct, T_RUN, T_RUN + 0.4)) * (1 - smooth(ramp(_ct, T_RUN1 - 0.4, T_RUN1 + 0.2)))),
             dur=1 / 15, ease="linear")
    _ct += 1 / 15
S.camera(T_RUN1 + 0.25, MX - 100, 640, 0.52, 0.9)                 # the reveal: MEGAPLEX 30
def run_fx(cr, t, p, ly):
    if ly != "back" or not (T_RUN + 0.2 <= t < T_RUN1 - 0.2): return
    h = p["hip"]
    for k, dy in enumerate((-400, -200, 0)):
        L.motion_lines(cr, h[0] - 200, h[1] + dy, math.pi, n=1, length=360, alpha=0.7, sid=7110 + k, width=6)
S.prop(run_fx)
# --- the door
DOORCAM = (MX + 20, 880, 0.92)
S.walk_to(T_WALK, XDOOR - 540, T_WALK1 - T_WALK)
S.camera(T_WALK, *DOORCAM, dur=1.0)
S.set(T_SIGN, "stand", "deadpan", dur=0.35, look=(-0.9, 0.2), turn=-0.3)                 # the NO PETS sign
S.set(T_UPCAT, "stand", "deadpan", dur=0.3, look=(-0.1, -1.0), turn=0.0, brow=0.1)         # ...up at the kitten
S.set(T_FLAT + 0.35, "stand", "deadpan", dur=0.35, look=(0.85, -0.1), turn=0.45)           # at the usher
S.set(T_TWITCH + 0.15, "stand", "deadpan", dur=0.1, look=(0.85, -0.1), turn=0.45, twitch=0.6)
S.set(T_TWITCH + 0.5, "stand", "deadpan", dur=0.3, look=(0.85, -0.1), turn=0.45)
S.set(T_STEP + 0.4, "stand", "deadpan", dur=0.3, look=(0.9, 0.0), turn=0.5)
S.camera(T_STARE, MX + 40, 860, 1.02, 2.4)                         # slow push on the stare
S.walk_to(T_IN, XDOOR - 540 + 330, CUT_LOBBY - T_IN - 0.25)
S.sfx(T_FLAT, "squeak", 0.03); S.sfx(T_TWITCH, "tick", 0.04); S.sfx(T_STEP + 0.25, "pat", 0.05)
S.blink(8.6)

# --- LOBBY
LOBBYCAM = (LX + 90, 880, 0.95)
S.cut(CUT_LOBBY - FR, cam=LOBBYCAM, x=XCOUNT - 540)
S.set(CUT_LOBBY - FR, "stand", "deadpan", dur=0.0, look=(0.8, -0.6), turn=0.45)
S.set(T_POINT, "point_up", "deadpan", dur=0.25, ease="back", look=(0.8, -0.8), turn=0.45)
S.set(T_POINT + 0.6, "stand", "deadpan", dur=0.3, look=(0.8, -0.3), turn=0.45)
S.set(T_LOOKB, "stand", "deadpan", dur=0.6, look=(0.6, -1.0), turn=0.4, brow=0.15)        # up the bucket
S.set(T_LOOKB + 0.6, "stand", "deadpan", dur=0.3, look=(0.0, 0.0), turn=0.1)               # at us
L.POSES["tap_card"] = dict(relb=(650, 980), rhand=(790, 1020), rhand_t="flat")
S.set(T_TAP - 0.3, "tap_card", "deadpan", dur=0.3, look=(0.7, 0.6), turn=0.4)
S.set(T_TAP + 0.35, "stand", "deadpan", dur=0.3, look=(0.7, 0.5), turn=0.4)
S.sfx(T_DROP, "thud", 0.18); S.shake(T_DROP, 0.3, 10); S.sfx(T_TAP, "boop", 0.08)
S.sfx(T_POINT + 0.1, "tok", 0.04)
# tip screen inserts (screen space, under the card)
def tip_insert(cr, t):
    a = CUT_TIP1 - FR <= t < CUT_TWO - FR
    b = CUT_TIP2 - FR <= t < CUT_TAKE - FR
    if not (a or b): return
    W_, H_ = L.W, L.H
    NOTIP = (W_ - 430, 1420); B30 = (W_ / 2 + 120, 1250)
    if a:
        u = smooth(ramp(t, CUT_TIP1, CUT_TIP1 + 0.9))
        hx, hy = lerp((W_ / 2 + 60, 2150), NOTIP, u)
        hx += 6 * math.sin(t * 9) * ramp(t, CUT_TIP1 + 0.9, CUT_TIP1 + 1.0); hy += 30
        O.draw_tip_screen(cr, W_, H_, t)
    else:
        u = smooth(ramp(t, T_SLIDE, T_PRESS - 0.1))
        hx, hy = lerp(NOTIP, B30, u); hy += 30
        pressed = t >= T_PRESS
        if pressed: hy += 14 * (1 - ramp(t, T_PRESS, T_PRESS + 0.15))
        O.draw_tip_screen(cr, W_, H_, t, press="30%" if pressed else None, total="$61.75" if t >= T_TOTAL else None)
    if not (b and t >= T_TOTAL):
        insert_finger(cr, hx, hy)
def insert_finger(cr, x, y):
    """a big mitten with the index finger out, coming up from the bottom of the frame (tip at x, y)."""
    sketch_line(cr, [(x + 150, L.H + 60), (x + 110, y + 330)], 30, sid=470)
    sketch_ellipse(cr, x + 70, y + 250, 105, 120, 8, rot=-0.25, sid=471, fill=(1, 1, 1))
    sketch_rect(cr, x - 32, y - 10, x + 32, y + 200, 8, sid=472, fill=(1, 1, 1))
    sketch_ellipse(cr, x, y - 4, 32, 30, 8, sid=473, fill=(1, 1, 1))
    sketch_line(cr, [(x - 24, y + 170), (x + 24, y + 170)], 6, sid=474)
S.overlays.insert(0, tip_insert)
S.sfx(T_PRESS, "boop", 0.08); S.sfx(T_TOTAL + 0.05, "ding", 0.05)
# the two-shot: the cashier stares. he stares. clock ticks.
TWOCAM = ((XCOUNT + CASH_X) / 2, 760, 1.18)
S.cut(CUT_TWO - FR, cam=TWOCAM)
S.set(CUT_TWO - FR, "stand", "dead_stare", dur=0.0, look=(0.85, -0.1), turn=0.55)
S.camera(CUT_TWO, (XCOUNT + CASH_X) / 2, 740, 1.3, CUT_TIP2 - CUT_TWO)
S.set(CUT_TWO + 0.9, "stand", "dead_stare", dur=0.4, look=(0.75, 0.7), turn=0.4)           # glances down at the reader
S.set(CUT_TWO + 1.4, "stand", "dead_stare", dur=0.3, look=(0.85, -0.1), turn=0.55, sweat=0.4)
k_ = CUT_TWO + 0.2
while k_ < CUT_TIP2 - 0.1:
    S.sfx(k_, "tick", 0.05); k_ += 0.5
# takes the bucket and shuffles off (to the left: the theater doors)
L.POSES["hug_bucket"] = dict(lelb=(430, 1010), lhand=(468, 960), relb=(650, 1010), rhand=(612, 960), lhand_t="grip", rhand_t="grip")
S.cut(CUT_TAKE - FR, cam=LOBBYCAM)
S.set(CUT_TAKE - FR, "hug_bucket", "deadpan", dur=0.0, look=(-0.6, 0.0), turn=-0.4)
S.walk_to(CUT_TAKE + 0.1, XCOUNT - 540 - 650, CUT_THEATER - CUT_TAKE - 0.4)
def held_bucket(cr, t, p, ly):
    if ly != "front" or not (CUT_TAKE - FR <= t < CUT_THEATER - FR): return
    hx = (p["lhand"][0] + p["rhand"][0]) / 2; hy = (p["lhand"][1] + p["rhand"][1]) / 2
    O.draw_popcorn(cr, hx, hy + 210, s=0.5, level=1.0, t=t)
    L.draw_grips(cr, p)
S.prop(held_bucket)

# --- THEATER: back view
L.POSES["cine_sit"] = dict(head=(540, 790), neck=(540, 915), hip=(540, 1250), lelb=(450, 1030), lhand=(395, 1062),
                           relb=(630, 1030), rhand=(685, 1062), lhand_t="grip", rhand_t="grip",
                           lknee=(470, 1270), rknee=(610, 1270), lfoot=(470, FLOOR_Y), rfoot=(610, FLOOR_Y), nowalk=1.0)
SIT = dict(lag=0.4, nowalk=1.0)
def back_cut(t):
    S.cut(t - FR, cam=BACKCAM, x=TX - 540)
    S.set(t - FR, "cine_sit", "deadpan", dur=0.0, back=1.0, **SIT)
def front_cut(t, cam=FRONTCAM, **kw):
    S.cut(t - FR, cam=cam, x=FX - 540)
    S.set(t - FR, "cine_sit", "deadpan", dur=0.0, **SIT, **kw)
back_cut(CUT_THEATER)
S.camera(CUT_THEATER, TX, 780, 1.0, 2.0)
S.sfx(T_GIANT_IN, "step", 0.04); S.sfx(T_GIANT_IN + 0.5, "step", 0.04); S.sfx(T_GIANT_IN + 1.0, "step", 0.04)
S.sfx(T_GIANT_SIT, "thud", 0.14); S.shake(T_GIANT_SIT, 0.25, 6)
S.sfx(T_LEAN1, "squeak", 0.025); S.sfx(T_LEAN1 + 0.35, "squeak", 0.02); S.sfx(T_LEAN2, "squeak", 0.025); S.sfx(T_LEAN2 + 0.35, "squeak", 0.02)
# reaction: front, dead stare at us
front_cut(CUT_STARE, cam=(FX + 30, 820, 1.32))
S.set(CUT_STARE + 0.5, "cine_sit", "dead_stare", dur=0.4, look=(0.0, 0.0), **SIT)
S.camera(CUT_STARE, FX + 30, 800, 1.42, 1.4)
back_cut(CUT_PREV1)
S.camera(CUT_PREV1, *BACKCAM, dur=0.01)
# eating faster and faster (front)
front_cut(CUT_EAT, look=(0.0, -0.2))
EAT_TS = []
_tt = CUT_EAT + 0.2; per = 0.85
while _tt < CUT_PREV47 - 0.25:
    EAT_TS.append((_tt, per)); _tt += per; per = max(0.2, per * 0.8)
BUCK = (FX + 300, SEAT_Y + 400)              # the bucket in the seat next to him (bottom-centre)
def level(t):
    if t < CUT_EAT: return 1.0
    if t < CUT_PREV47: return lerp(1.0, 0.12, ramp(t, CUT_EAT, CUT_PREV47 - 0.2, "linear") ** 0.8)
    return 0.12 if t < CUT_EMPTY - FR else 0.0
def eat_hook(t, p):
    if not (CUT_EAT - FR <= t < CUT_PREV47 - FR): return p
    for t0, d in EAT_TS:
        if t0 <= t < t0 + d:
            u = (t - t0) / d
            dip = (BUCK[0] - 30, BUCK[1] - 520 * 0.75 - 30); mouth = (p["head"][0] + 30, p["head"][1] + 60)
            if u < 0.45: q = lerp(dip, mouth, smooth(u / 0.45))
            else: q = lerp(mouth, dip, smooth((u - 0.45) / 0.55))
            p["rhand"] = q; p["relb"] = (q[0] + 90, q[1] + 170); p["rhand_t"] = "fist"
            p["open"] = 0.5 * pulse(u, 0.4, 0.08); p["mouth"] = "auto"
            break
    return p
S.hook(eat_hook)
for t0, d in EAT_TS: S.sfx(t0 + d * 0.45, "chomp", 0.035)
S.camera(CUT_EAT, FX + 120, 880, 1.15, 0.01)
S.set(CUT_EAT + 1.6, "cine_sit", "deadpan", dur=0.5, look=(0.0, 0.0), lid=0.45, **SIT)
back_cut(CUT_PREV47)
S.camera(CUT_PREV47, *BACKCAM, dur=0.01)
# the empty bucket + the last kernel
front_cut(CUT_EMPTY, cam=(FX + 120, 880, 1.15), look=(0.8, 0.7), turn=0.3)
def kernel_hook(t, p):
    if not (CUT_EMPTY - FR <= t < CUT_4D - FR): return p
    dip = (BUCK[0] - 40, BUCK[1] - 400); mouth = (p["head"][0] + 25, p["head"][1] + 70)
    if T_RATTLE - 0.3 <= t < T_KERNEL:
        g = smooth(ramp(t, T_RATTLE - 0.3, T_RATTLE))
        q = lerp(p["rhand"], (dip[0] + 18 * math.sin(t * 40) * (t > T_RATTLE), dip[1] + 8 * math.sin(t * 31) * (t > T_RATTLE)), g)
        p["rhand"] = q; p["relb"] = (q[0] + 80, q[1] + 170); p["rhand_t"] = "fist"
    elif T_KERNEL <= t < T_EATK + 0.4:
        u = smooth(ramp(t, T_KERNEL, T_EATK))
        q = lerp(dip, mouth, u); p["rhand"] = q; p["relb"] = (q[0] + 90, q[1] + 170); p["rhand_t"] = "fist"
    return p
S.hook(kernel_hook)
S.set(T_KERNEL, "cine_sit", "deadpan", dur=0.4, look=(0.3, 0.5), turn=0.1, **SIT)
S.set(T_EATK, "cine_sit", "deadpan", dur=0.15, look=(0.0, 0.0), turn=0.0, open=0.3, **SIT)
S.set(T_EATK + 0.2, "cine_sit", "dead_stare", dur=0.2, look=(0.0, 0.0), **SIT)
for k in range(4): S.sfx(T_RATTLE + 0.12 * k, "tok", 0.05)
S.sfx(T_EATK + 0.15, "chomp", 0.06)
S.camera(CUT_EMPTY + 1.0, FX + 60, 830, 1.32, 1.6)
def kernel_prop(cr, t, p, ly):
    if ly == "front" and T_KERNEL <= t < T_EATK + 0.12:
        hx, hy = p["rhand"]; O.draw_kernel(cr, hx + 6, hy - 34, r=18)
S.prop(kernel_prop)
# 4D on (back)
back_cut(CUT_4D)
S.camera(CUT_4D, *BACKCAM, dur=0.01)
S.sfx(T_4D_ON, "ding", 0.06); S.shake(CUT_4D + 0.6, 0.6, 4)
# the seat: tilt, water, fans, rodeo (front)
front_cut(CUT_SEAT, look=(0.0, 0.0))
S.set(T_TILT + 0.3, "cine_sit", "deadpan", dur=0.25, look=(0.0, 0.0), eyescale=1.06, brow=0.15, **SIT)
S.set(T_WATER + 0.25, "cine_sit", "dead_stare", dur=0.12, ease="snap", look=(0.0, 0.0), lid=0.75, **SIT)
S.set(T_WATER1 + 0.2, "cine_sit", "dead_stare", dur=0.3, look=(0.0, 0.0), lid=0.38, **SIT)                       # dripping. stare.
S.set(T_FANS + 0.1, "cine_sit", "deadpan", dur=0.25, look=(0.0, 0.0), lid=0.6, **SIT)
S.set(T_FANS1 - 0.1, "cine_sit", "deadpan", dur=0.3, look=(0.0, 0.0), lid=0.4, **SIT)
S.set(T_RODEO + 0.6, "cine_sit", "deadpan", dur=0.3, look=(0.0, 0.0), eyescale=1.1, brow=0.3, **SIT)
S.sfx(T_TILT, "slide_down", 0.03); S.sfx(T_WATER, "sploosh", 0.12); S.sfx(T_WATER1 + 0.3, "drip", 0.06); S.sfx(T_WATER1 + 0.7, "drip", 0.05)
S.sfx(T_FANS, "wind", 0.10, dur=T_FANS1 - T_FANS + 0.2)
for k in range(10): S.sfx(T_RODEO + 0.2 + 0.18 * k, "thud", 0.03 + 0.004 * k)
S.camera(CUT_SEAT, FX + 60, 850, 1.25, 2.0)
S.shake(T_RODEO, CUT_LAUNCH - T_RODEO, 16)
def seat_hook(t, p):
    st = setting(t)
    if not (CUT_THEATER - FR <= t < CUT_ASK - FR): return p
    dy = rodeo_dy(t) - tilt_4d(t) * 0.3 if st == "front" else rodeo_dy(t)
    if st == "back":
        lx = 130 * lean_amt(t)
        for j in ("head", "neck"): p[j] = (p[j][0] + lx, p[j][1])
        p["tilt"] = p.get("tilt", 0.0) + 0.12 * lean_amt(t)
    if abs(dy) > 0.01:
        for j in L.JOINTS: p[j] = (p[j][0], p[j][1] + dy)
    if st == "front" and tilt_4d(t) > 0:
        p["head"] = (p["head"][0], p["head"][1] + 0.6 * tilt_4d(t)); p["tilt"] = p.get("tilt", 0.0) - 0.004 * tilt_4d(t)
    if st == "back":
        dx_, dy_, ang = loop_xform(t)
        if ang:
            cx_, cy_ = TX, H_ROW_Y + 100
            c, s_ = math.cos(ang), math.sin(ang)
            for j in L.JOINTS:
                x_, y_ = p[j][0] - cx_, p[j][1] - cy_
                p[j] = (cx_ + dx_ + x_ * c - y_ * s_, cy_ + dy_ + x_ * s_ + y_ * c)
            p["tilt"] = p.get("tilt", 0.0) + ang
    return p
S.hook(seat_hook)
def water(cr, t, p, ly):
    if ly != "front" or setting(t) != "front": return
    hx, hy = p["head"]
    if T_WATER <= t < T_WATER1:
        u = ramp(t, T_WATER, T_WATER + 0.12, "linear")
        n = 18; pts = []
        for i in range(n):
            k = i / (n - 1)
            pts.append((lerp(FX + 620, hx + 40, k * u + (1 - u)), lerp(hy - 140, hy + 10, k) - 60 * math.sin(math.pi * k), 26 + 34 * k))
        O.draw_spray(cr, pts, color=(0.62, 0.82, 0.98), dark=(0.40, 0.64, 0.90), t=t)
        for k in range(6):
            a = k * 1.1 + t * 7; r = 90 + 40 * ((t * 5 + k) % 1)
            O.draw_droplet(cr, hx + 40 + math.cos(a) * r, hy + math.sin(a) * r * 0.7, 9, color=(0.62, 0.82, 0.98))
    if T_WATER1 <= t < T_FANS + 0.4:                                     # dripping (the fans blow it off)
        for k in range(5):
            ph = ((t - T_WATER1) * (1.3 + 0.2 * k) + k * 0.37) % 1.0
            x_ = hx - 90 + 45 * k + (300 * ramp(t, T_FANS, T_FANS + 0.4) * -1)
            y_ = hy + 40 + 260 * ph * ph
            O.draw_droplet(cr, x_, y_, 9 + 2 * (k % 2), color=(0.62, 0.82, 0.98))
        cr.save(); cr.translate(hx, hy)
        sketch_ellipse(cr, -30, 120, 70, 14, 3, sid=14700, fill=(0.62, 0.82, 0.98), alpha=1 - ramp(t, T_FANS, T_FANS + 0.4))
        cr.restore()
    if T_FANS <= t < T_FANS1:                                            # wind lines blasting from the right
        for k in range(7):
            ph = ((t * 3.5 + k * 0.29) % 1.0)
            y_ = hy - 260 + k * 85
            x_ = FX + 700 - ph * 1300
            sketch_line(cr, [(x_, y_), (x_ + 300, y_ + 6 * math.sin(k + t * 9))], 9, sid=14710 + k, color=(0.92, 0.95, 1.0), alpha=0.9 * math.sin(math.pi * ph))
S.prop(water)
# the launch (back, wide)
S.cut(CUT_LAUNCH - FR, cam=WIDECAM, x=TX - 540)
S.set(CUT_LAUNCH - FR, "cine_sit", "deadpan", dur=0.0, back=1.0, **SIT)
S.shake(CUT_LAUNCH, T_LOOP0 - CUT_LAUNCH, 10)
S.sfx(T_GLAUNCH, "spring", 0.10); S.sfx(T_GLAUNCH + 0.05, "whoosh", 0.08); S.sfx(T_CRASH, "kaboom", 0.25, dur=1.2); S.shake(T_CRASH, 0.5, 22)
S.sfx(T_LOOP0, "spring", 0.10); S.sfx(T_LOOP0 + 0.1, "whoosh", 0.08, dur=1.8)
T_FLASH = T_LOOP0 + (T_LOOP1 - T_LOOP0) * 0.5
S.flash(T_FLASH, 0.35); S.sfx(T_FLASH, "tick", 0.1); S.sfx(T_FLASH + 0.02, "pop", 0.05)
S.sfx(T_LOOP1, "thud", 0.2); S.shake(T_LOOP1, 0.4, 18)
S.set(T_LOOP1 + 0.2, "cine_sit", "deadpan", dur=0.3, back=1.0, **SIT)
S.camera(T_LOOP1 + 0.1, TX, 760, 0.9, 0.8)                         # in on the screen: KA-BOOM
S.sfx(T_BOOM + 0.05, "kaboom", 0.4, dur=1.6)
S.shake(T_BOOM + 0.05, 0.6, 8)
# lit by the movie (front): the curl springs back
front_cut(CUT_LIT, cam=(FX + 40, 830, 1.32), look=(0.0, -0.1))
S.set(T_BOING + 0.6, "cine_sit", "deadpan", dur=0.4, look=(0.0, -0.4), smile=0.15, **SIT)
# credits + the post-credits scene (back)
back_cut(CUT_CREDITS)
S.camera(CUT_CREDITS, *BACKCAM, dur=0.01)
S.camera(T_ROLL0, TX, 790, 1.02, 3.0)
S.sfx(T_GFALL, "slide_down", 0.05); S.sfx(T_GLAND, "thud", 0.2); S.shake(T_GLAND, 0.35, 14)
S.camera(T_GLAND + 0.3, TX, 760, 1.12, 1.6)
S.blink(54.4)
# --- THE ASK (in the aisle)
S.cut(CUT_ASK - FR, cam=(ASKX, 930, 1.15), x=ASKX - 540)
S.set(CUT_ASK - FR, "stand", "deadpan", dur=0.0)
S.t = T_ASK
S.the_ask(T_ASK, hold=ASK_HOLD)

# his seat-row backs + the near rows (back view), his seat + armrests (front view), the bucket
def seats_front_layer(cr, t, p, ly):
    st = setting(t)
    if st == "back" and ly == "back" and CUT_THEATER - FR <= t:
        # the bucket in the seat beside him (top shows over the seat back)
        if t >= CUT_THEATER - FR:
            O.draw_popcorn(cr, TX + 205, H_ROW_Y + 240 + rodeo_dy(t), s=0.6, level=level(t), t=t, label="")
    if st == "back" and ly == "front":
        dx_, dy_, ang = loop_xform(t)
        skip = (4,) if ang else ()
        O.draw_seat_row(cr, TX, H_ROW_Y + rodeo_dy(t), n=9, w=190, h=260, gap=16, s=1.0, sid=14800, skip=skip)
        if ang:
            cx_, cy_ = TX, H_ROW_Y + 100
            u = loop_u(t); n = 14                                          # white speed trail along the loop
            for i in range(n):
                th = 2 * math.pi * max(0.0, u - 0.03 * (i + 1))
                if th <= 0: break
                x_ = cx_ + LOOP_R * 0.9 * math.sin(th); y_ = cy_ - 200 - LOOP_R * (1 - math.cos(th))
                th2 = 2 * math.pi * max(0.0, u - 0.03 * (i + 2))
                x2 = cx_ + LOOP_R * 0.9 * math.sin(th2); y2 = cy_ - 200 - LOOP_R * (1 - math.cos(th2))
                sketch_line(cr, [(x_, y_), (x2, y2)], 10, sid=14900 + i, color=(0.95, 0.95, 1.0), alpha=1 - i / n)
            cr.save(); cr.translate(cx_ + dx_, cy_ + dy_); cr.rotate(ang); cr.translate(-cx_, -cy_)
            O.draw_seat_row(cr, TX, H_ROW_Y, n=1, w=190, h=260, s=1.0, sid=14804)
            cr.restore()
        O.draw_seat_row(cr, TX, N_ROW_Y + rodeo_dy(t, 0.6), n=7, w=240, h=320, gap=20, s=1.0, sid=14820)
    if st == "front" and t < CUT_ASK - FR:
        dy = seat_dy(t)
        if ly == "front":
            O.draw_seat_front(cr, FX, SEAT_Y + dy, s=1.0, sid=14620, part="arms")
            L.draw_grips(cr, p)
            O.draw_popcorn(cr, BUCK[0], BUCK[1] + dy, s=0.75, level=level(t), t=t)
            for k in range(-3, 4):                                       # the row in front (backs to us) hides his legs
                O.draw_seat_row(cr, FX + k * 330, 1215 + rodeo_dy(t, 0.4), n=1, w=290, h=300, s=1.0, sid=14840 + k)
S.prop(seats_front_layer)

# ================================================================ the kitten (always on his head)
def kitten_spot(p, lift=0.0):
    hx, hy = p["head"]; a = p.get("tilt", 0.0)
    ox, oy = 5.0, -104.0 - lift
    return hx + ox * math.cos(a) - oy * math.sin(a), hy + ox * math.sin(a) + oy * math.cos(a), a
def kitten_back(cr, x, y, s, a):
    cr.save(); cr.translate(x, y); cr.rotate(a * 0.6); cr.scale(s, s)
    fur = (0.13, 0.13, 0.15)
    sketch_ellipse(cr, 0, -40, 72, 42, 4, sid=2020, fill=fur)
    sketch_circle(cr, 10, -88, 40, 4, sid=2021, fill=fur)
    for d in (-1, 1): sketch_poly(cr, [(10 + d * 12, -118), (10 + d * 34, -150), (10 + d * 38, -104)], 4, sid=2022 + (d > 0), fill=fur)
    sketch_line(cr, [(-60, -20), (-95, -10), (-105, -35)], 12, sid=2024, color=fur)
    cr.restore()
def kitten(cr, t, p, ly):
    if ly != "front": return
    if CUT_TIP1 - FR <= t < CUT_TWO - FR or CUT_TIP2 - FR <= t < CUT_TAKE - FR: return
    x, y, a = kitten_spot(p)
    st = setting(t)
    if st == "back":
        kitten_back(cr, x, y, KS, a); return
    look = (0.0, 0.0); blink = 0.0; flat = 0.0
    if st == "street":
        if T_TURN <= t < T_RUN1 + 0.6: look = (0.9, -0.2)
        if T_LOOKUP <= t < T_WALK1: look = (0.6, -0.9)
        flat = smooth(ramp(t, T_FLAT, T_FLAT + 0.3)) * (1 - smooth(ramp(t, T_STEP + 0.8, T_STEP + 1.1)))
        if flat > 0: blink = flat
        if T_STEP + 0.3 <= t < T_STEP + 0.8: blink = 0.5                       # opens one eye... (both, a crack)
        if T_TWITCH <= t < T_TWITCH + 0.25: a += 0.05 * math.sin((t - T_TWITCH) * 60)
    if st == "lobby":
        look = (0.7, -0.6) if t < T_TAP else (0.6, 0.3)
        if CUT_TWO - FR <= t < CUT_TIP2: look = (0.8, 0.0); blink = 0.3
    if st == "front":
        look = (0.0, -0.3)
        if CUT_EAT - FR <= t < CUT_PREV47: look = (0.6, 0.8)
        if T_WATER <= t < T_FANS1: blink = 0.85
        if CUT_LIT - FR <= t < CUT_CREDITS:
            look = (0.0, 0.0)
            if T_BOING + 0.6 <= t < T_BOING + 1.4: blink = math.sin(math.pi * (t - T_BOING - 0.6) / 0.8)
        if t >= CUT_ASK - FR: look = (0.0, 0.0)
    cr.save()
    if flat > 0:
        cr.translate(x, y); cr.scale(1 + 0.18 * flat, 1 - 0.28 * flat); cr.translate(-x, -y)
    wob_ = 0.0
    if T_FANS <= t < T_FANS1: wob_ = 0.06 * math.sin(t * 40)
    O.draw_cat(cr, x, y, s=KS, t=t, kind="loaf", col="black", look=look, blink=blink, sid=2000, tilt=a * 0.6 + wob_, swish=0.0 if flat else 1.0)
    cr.restore()
    mini_photo(cr, x - 85, y - 30 + 10 * flat, 0.38, a * 0.6 - 0.35)
S.prop(kitten)

# light from the screen washing over the front shots
def wash(cr, t):
    if setting(t) != "front" or t >= CUT_ASK - FR: return
    if CUT_TIP1 - FR <= t < CUT_TAKE - FR: return
    col, a = screen_light(t)
    cr.set_source_rgba(col[0], col[1], col[2], a * (1 - 0.6 * lights(t))); cr.paint()
S.overlays.insert(0, wash)

if __name__ == "__main__":
    print(f"end {S.t:.2f}", file=sys.stderr)
    S.render("day013.mp4")
