"""Day 13 - COMMENT episode: @second_degree_burn "Go to the movies!" (Instagram, day 12 reel, 0 likes).
Deadpan, Family Guy timing. The kitten rides on his head the whole time, never harmed. See BEATS.md.

PARK EXIT -> run right through the park's back gate -> MEGAPLEX 30 (NO PETS: he pulls out a tiny cowboy hat and puts
it on the kitten; the usher stares him down, lets it slide) -> LOBBY (SMALL popcorn $47.50, the TIP SCREEN) ->
THEATER (hat tossed; empty theater; a giant in a top hat sits right in front; 47 previews; the popcorn is gone before
the movie; the movie starts and he can't see it -> he pulls out a periscope, raises it over the hat, and watches
EXPLOSION 7 through it) -> THE END: the tall guy finally gets up and leaves -> ASK in the aisle.
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
T_SIGN = 6.55; T_UPCAT = 7.0; T_DIG = 7.35; T_HATPOP = 7.95; T_HATON = 8.45
T_STARE = 8.9; T_TWITCH = 10.2; T_NARROW = 10.8; T_STEP = 11.25; T_IN = 11.9
CUT_LOBBY = 12.4
T_POINT = 12.7; T_DROP = 13.3; T_LOOKB = 13.7; T_TAP = 14.4; T_SWIVEL = 14.75
CUT_TIP1 = 15.2
CUT_TWO = 16.7
CUT_TIP2 = 18.6; T_SLIDE = 18.95; T_PRESS = 19.4; T_TOTAL = 19.65
CUT_TAKE = 20.3
CUT_THEATER = 21.3; T_HATOFF = 21.75; T_TOSS = 22.35          # front: the hat comes off, tossed
CUT_BACK1 = 23.3
T_GIANT_IN = 23.7; T_GIANT_SIT = 25.3
T_LEAN1 = 25.8; T_LEAN2 = 26.6
CUT_STARE = 27.5
CUT_PREV1 = 28.9
CUT_EAT = 30.3
CUT_PREV47 = 33.5
CUT_EMPTY = 34.5; T_RATTLE = 35.0; T_KERNEL = 35.9; T_EATK = 36.4
CUT_MOVIE = 37.3; T_LEAN3 = 37.8                               # back: the movie starts. he can't see it.
CUT_PULL = 39.0; T_DIG2 = 39.35; T_SCOPE_POP = 39.95; T_SCOPE_UP = 40.15; T_SCOPE_EXT = 40.45
CUT_SCOPE_BACK = 41.2                                          # back: the periscope rises over the hat
CUT_POV = 42.5                                                 # the periscope view: the movie
CUT_WATCH = 46.7                                               # front: watching through it
CUT_END = 48.2; T_GSTAND = 48.7; T_GLEAVE = 49.1; T_LIGHTS = 49.5; T_LOWER = 50.7
CUT_FINAL = 51.6; T_STOW = 52.0
CUT_ASK = 53.4
T_ASK = 53.6
ASK_HOLD = 7.5
MOVIE_BOOM = CUT_POV + 0.9                                    # the building blows up (in the movie)


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
    for a, b in ((CUT_THEATER, CUT_BACK1), (CUT_STARE, CUT_PREV1), (CUT_EAT, CUT_PREV47), (CUT_EMPTY, CUT_MOVIE),
                 (CUT_PULL, CUT_SCOPE_BACK), (CUT_WATCH, CUT_END), (CUT_FINAL, CUT_ASK)):
        if a - FR <= t < b - FR: return "front"
    return "back"

def hat_state(t):
    """where the tiny cowboy hat is: None / 'hand' / 'cat' / 'fly'."""
    if t < T_HATPOP or t >= T_TOSS + 0.8: return None
    if t < T_HATON: return "hand"
    if t < T_HATOFF: return "cat"
    if t < T_TOSS: return "hand"
    return "fly"

def scope_ext(t):
    """periscope extension 0..1 (front shot goes to 0.35, the back shot to 1, then it comes down at T_LOWER)."""
    if t < T_SCOPE_EXT: return 0.0
    e = 0.35 * smooth(ramp(t, T_SCOPE_EXT, T_SCOPE_EXT + 0.5)) + 0.65 * smooth(ramp(t, CUT_SCOPE_BACK + 0.2, CUT_SCOPE_BACK + 1.0))
    return e * (1 - smooth(ramp(t, T_LOWER, T_LOWER + 0.7)))
def scope_on(t): return T_SCOPE_POP <= t < T_STOW + 0.35
def scope_up(t): return smooth(ramp(t, T_SCOPE_UP, T_SCOPE_UP + 0.3)) * (1 - smooth(ramp(t, T_LOWER + 0.5, T_LOWER + 0.9)))

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
SCR = (TX - 440, 100, TX + 440, 640)          # the movie screen
G_ROW_Y, H_ROW_Y, N_ROW_Y = 790.0, 905.0, 1190.0
GIANT_SHOULDER_Y = 880.0
GS = 1.15
def lights(t): return smooth(ramp(t, T_LIGHTS, T_LIGHTS + 1.0))
def wall_col(t, base): return lerp(base, (0.62, 0.46, 0.48), 0.6 * lights(t))

def giant_state(t):
    """(x, y) of the tall guy's shoulders in the back view, or None."""
    if t < T_GIANT_IN: return None
    if t < T_GIANT_SIT:
        u = smooth(ramp(t, T_GIANT_IN, T_GIANT_SIT - 0.25))
        x = lerp(TX + 1000, TX, u); y = GIANT_SHOULDER_Y - 200 + 12 * abs(math.sin(t * 7)) * (1 - u)
        if t > T_GIANT_SIT - 0.25: y = lerp(GIANT_SHOULDER_Y - 200, GIANT_SHOULDER_Y, smooth(ramp(t, T_GIANT_SIT - 0.25, T_GIANT_SIT)))
        return (x, y)
    if t < T_GSTAND: return (TX + lean_giant(t), GIANT_SHOULDER_Y)
    y = lerp(GIANT_SHOULDER_Y, GIANT_SHOULDER_Y - 200, smooth(ramp(t, T_GSTAND, T_GSTAND + 0.35)))
    u = ramp(t, T_GLEAVE, T_GLEAVE + 1.3, "linear")
    if u >= 1: return None
    return (TX + 1300 * u, y + 12 * abs(math.sin(t * 7)) * (u > 0))

def lean_amt(t):
    """his head lean in the back view (-1 left .. +1 right)."""
    a = -1.0 * smooth(ramp(t, T_LEAN1, T_LEAN1 + 0.3)) + 2.0 * smooth(ramp(t, T_LEAN2, T_LEAN2 + 0.35)) - 1.0 * smooth(ramp(t, CUT_STARE - 0.3, CUT_STARE))
    a += -1.0 * smooth(ramp(t, T_LEAN3, T_LEAN3 + 0.25)) + 1.0 * smooth(ramp(t, T_LEAN3 + 0.75, T_LEAN3 + 1.0))
    return a
def lean_giant(t): return 150 * lean_amt(t - 0.35)

def draw_movie(cr, x0, y0, w, h, t):
    """EXPLOSION 7, as it plays: title card, then a desert road; a getaway car races in, the building blows up, the
    car jumps through the fireball, title slam."""
    cr.save(); cr.rectangle(x0, y0, w, h); cr.clip()
    mt = t - CUT_MOVIE
    if mt < 1.6:
        cr.rectangle(x0, y0, w, h); cr.set_source_rgb(0.06, 0.06, 0.08); cr.fill()
        draw_text(cr, "EXPLOSION 7", x0 + w / 2, y0 + h / 2, w * 0.13, color=(255, 214, 80), max_w=w * 0.9)
        cr.restore(); return
    for k, col in enumerate(((0.98, 0.62, 0.30), (0.99, 0.74, 0.42), (1.0, 0.85, 0.58))):
        cr.rectangle(x0, y0 + h * 0.2 * k, w, h * 0.2 + 1); cr.set_source_rgb(*col); cr.fill()
    gy = y0 + h * 0.62
    sketch_circle(cr, x0 + w * 0.2, y0 + h * 0.2, h * 0.08, 4, sid=15000, fill=(1.0, 0.95, 0.7))
    sketch_poly(cr, [(x0 - 10, gy), (x0 + w * 0.1, gy - h * 0.16), (x0 + w * 0.3, gy - h * 0.16), (x0 + w * 0.36, gy)], 4, sid=15001, fill=(0.80, 0.42, 0.26))
    cr.rectangle(x0, gy, w, h - (gy - y0)); cr.set_source_rgb(0.88, 0.70, 0.44); cr.fill()
    sketch_line(cr, [(x0, gy), (x0 + w, gy)], 4, sid=15002)
    cr.rectangle(x0, gy + h * 0.1, w, h * 0.06); cr.set_source_rgb(0.30, 0.30, 0.34); cr.fill()
    for k in range(6):
        cr.rectangle(x0 + ((k * 0.2 - mt * 0.6) % 1.2) * w - 0.1 * w, gy + h * 0.125, w * 0.06, h * 0.012); cr.set_source_rgb(1, 1, 0.8); cr.fill()
    road_y = gy + h * 0.16
    bx = x0 + w * 0.6; bw = w * 0.14
    e = t - MOVIE_BOOM
    if e < 0.08:                                                           # the building
        sketch_rect(cr, bx - bw / 2, gy - h * 0.34, bx + bw / 2, gy + h * 0.02, 5, sid=15003, fill=(0.62, 0.62, 0.66))
        for i in range(2):
            for j in range(4):
                cr.rectangle(bx - bw * 0.32 + i * bw * 0.4, gy - h * 0.3 + j * h * 0.075, bw * 0.24, h * 0.045); cr.set_source_rgb(0.3, 0.4, 0.6); cr.fill()
    else:
        sketch_poly(cr, [(bx - bw * 0.7, gy + h * 0.02), (bx - bw * 0.3, gy - h * 0.06), (bx + bw * 0.1, gy - h * 0.03), (bx + bw * 0.6, gy + h * 0.02)], 4, sid=15004, fill=(0.45, 0.42, 0.44))
    if 0 <= e < 2.6:                                                      # the fireball
        r = h * 0.42 * back_out(min(1.0, e / 0.35), 1.6) * (1 - 0.35 * smooth(ramp(e, 1.6, 2.6)))
        O.draw_boom(cr, bx, gy - h * 0.12, r, t=t, sid=15010)
    # the car
    if e < 0.3:
        u = ramp(t, MOVIE_BOOM - 1.4, MOVIE_BOOM + 0.3, "linear") if t >= MOVIE_BOOM - 1.4 else ((mt - 1.6) * 0.35) % 1.0
        cx = x0 + lerp(0.0, 0.36, u) * w; cy = road_y; ang = 0.0
    elif e < 1.3:
        u = (e - 0.3) / 1.0
        cx = x0 + lerp(0.36, 1.05, u) * w; cy = road_y - h * 0.5 * 4 * u * (1 - u); ang = -0.35 + 0.6 * u
    else:
        cx = None
    if cx is not None:
        for k in range(3):
            sketch_line(cr, [(cx - w * 0.14, cy - h * (0.03 + 0.03 * k)), (cx - w * 0.3, cy - h * (0.03 + 0.03 * k))], 4, sid=15020 + k, color=(1, 1, 1))
        O.draw_car(cr, cx, cy, s=w / 1100, ang=ang)
    if e >= 1.6:                                                          # title slam
        sc = back_out(min(1.0, (e - 1.6) / 0.3), 1.8)
        draw_text(cr, "EXPLOSION 7", x0 + w / 2, y0 + h * 0.3, w * 0.075 * max(0.05, sc), color=(140, 20, 20), rot=-0.05)
    cr.restore()

def screen_content(cr, t):
    x0, y0, x1, y1 = SCR; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    def big(txt, size=84, y=cy, col=(240, 240, 240)): draw_text(cr, txt, cx, y, size, color=col, max_w=x1 - x0 - 60)
    def strip(txt):
        for i, part in enumerate(txt.split("|")): draw_text(cr, part, x0 + 24, y0 + 40 + 44 * i, 40, color=(255, 214, 80), anchor="left")
    if t < CUT_PREV1 - FR:
        big("PLEASE SILENCE", 76, cy - 60); big("YOUR PHONES", 76, cy + 40)
    elif t < CUT_PREV47 - FR:
        strip("PREVIEW|1 OF 47"); big("IN A WORLD...", 90)
    elif t < CUT_MOVIE - FR:
        strip("PREVIEW|47 OF 47"); big("COMING SOON", 90)
    elif t < CUT_END - FR:
        draw_movie(cr, x0, y0, x1 - x0, y1 - y0, t)
    else:
        big("THE END", 120)

def theater_back(cr, t):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    cr.rectangle(vx0, vy0, vx1 - vx0, vy1 - vy0); cr.set_source_rgb(*wall_col(t, (0.14, 0.09, 0.12))); cr.fill()
    ceil = -40.0
    cr.rectangle(vx0, vy0, vx1 - vx0, ceil - vy0); cr.set_source_rgb(*wall_col(t, (0.08, 0.06, 0.09))); cr.fill()
    for k in range(-6, 7): sketch_line(cr, [(TX + k * 260, vy0), (TX + k * 260, ceil)], 3, sid=14500 + k % 4, color=(0.20, 0.16, 0.20))
    sketch_line(cr, [(vx0, ceil), (vx1, ceil)], 5, sid=14510)
    for d in (-1, 1):
        x_ = TX + d * 470
        sketch_rect(cr, x_ - 70, ceil, x_ + 70, 760, 5, sid=14512 + (d > 0), fill=O.CINE_RED_D)
    x0, y0, x1, y1 = SCR
    sketch_rect(cr, x0, y0, x1, y1, 6, sid=14514, fill=(0.10, 0.10, 0.13))
    cr.save(); cr.rectangle(x0, y0, x1 - x0, y1 - y0); cr.clip(); screen_content(cr, t); cr.restore()
    sketch_rect(cr, x0, y0, x1, y1, 6, sid=14515, fill=None)
    O.draw_seat_row(cr, TX, 680, n=11, w=150, h=120, gap=12, s=0.75, sid=14520)
    g = giant_state(t)
    if g: O.draw_giant_back(cr, g[0], g[1], s=GS, tilt=0.03 * math.sin(t * 2))
    O.draw_seat_row(cr, TX, G_ROW_Y, n=11, w=170, h=150, gap=14, s=0.85, sid=14540)

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
def theater_front(cr, t):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    cr.rectangle(vx0, vy0, vx1 - vx0, vy1 - vy0); cr.set_source_rgb(*wall_col(t, (0.12, 0.08, 0.11))); cr.fill()
    for k in range(-2, 7):                                                  # empty rows behind him
        O.draw_seat_front(cr, FX - 900 + k * 300 + 150, 380, s=0.62, sid=14600 + k, part="all")
    cr.rectangle(vx0, 640, vx1 - vx0, 40); cr.set_source_rgb(*wall_col(t, (0.20, 0.12, 0.15))); cr.fill()
    for k in range(-3, 8):
        if k == 0: continue
        O.draw_seat_front(cr, FX + k * 300, SEAT_Y, s=1.0, sid=14620 + k, part="all")
    O.draw_seat_front(cr, FX, SEAT_Y, s=1.0, sid=14620, part="back")
    cr.rectangle(vx0, FLOOR_Y, vx1 - vx0, vy1 - FLOOR_Y); cr.set_source_rgb(0.22, 0.10, 0.12); cr.fill()
    if t >= CUT_ASK - FR:
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
# --- the door: NO PETS -> a tiny cowboy hat over the kitten. the usher stares.
DOORCAM = (MX + 20, 880, 0.92)
S.walk_to(T_WALK, XDOOR - 540, T_WALK1 - T_WALK)
S.camera(T_WALK, *DOORCAM, dur=1.0)
S.set(T_SIGN, "stand", "deadpan", dur=0.35, look=(-0.9, 0.2), turn=-0.3)                 # the NO PETS sign
S.set(T_UPCAT, "stand", "deadpan", dur=0.3, look=(-0.1, -1.0), turn=0.0, brow=0.1)         # ...up at the kitten
S.set(T_DIG, "stand", "deadpan", dur=0.3, look=(0.3, 0.8), turn=0.1)                       # digs at his hip
S.set(T_HATPOP + 0.05, "stand", "deadpan", dur=0.3, look=(0.2, -0.9), turn=0.0)            # puts it on the cat
S.set(T_STARE - 0.3, "stand", "deadpan", dur=0.35, look=(0.85, -0.1), turn=0.45)           # at the usher
S.set(T_TWITCH + 0.15, "stand", "deadpan", dur=0.1, look=(0.85, -0.1), turn=0.45, twitch=0.6)
S.set(T_TWITCH + 0.5, "stand", "deadpan", dur=0.3, look=(0.85, -0.1), turn=0.45)
S.set(T_STEP + 0.4, "stand", "deadpan", dur=0.3, look=(0.9, 0.0), turn=0.5)
S.camera(T_STARE - 0.2, (XDOOR + XUSH) / 2, 620, 1.3, 0.5)          # in on the stare
S.camera(T_STARE + 0.4, (XDOOR + XUSH) / 2, 610, 1.4, 1.9)
S.walk_to(T_IN, XDOOR - 540 + 330, CUT_LOBBY - T_IN - 0.25)
S.sfx(T_DIG + 0.1, "rummage", 0.05, dur=0.5); S.sfx(T_HATPOP, "pop", 0.08); S.sfx(T_HATON, "pat", 0.05)
S.sfx(T_TWITCH, "tick", 0.04); S.sfx(T_STEP + 0.25, "pat", 0.05)
S.blink(9.6)
def hat_hook(t, p):
    """the hand: digs at the hip, pops the hat out, sets it on the kitten (door); later takes it off and tosses it."""
    if T_DIG <= t < T_HATON + 0.4:
        hip = (p["hip"][0] + 48, p["hip"][1] - 26)
        top = (p["head"][0] + 30, p["head"][1] - 190)
        if t < T_HATPOP:
            u = smooth(ramp(t, T_DIG, T_DIG + 0.2)); dig = ramp(t, T_DIG + 0.2, T_DIG + 0.3)
            q = (hip[0] + 14 * math.sin(t * 24) * dig, hip[1] + 6 * math.sin(t * 31) * dig)
            p["rhand"] = lerp(p["rhand"], q, u)
        elif t < T_HATON:
            q = lerp(hip, top, smooth(ramp(t, T_HATPOP, T_HATON - 0.05)))
            p["rhand"] = q; p["relb"] = (q[0] + 120, (q[1] + p["neck"][1]) / 2 + 120); p["rhand_t"] = "grip"
        else:
            p["rhand"] = lerp(top, p["rhand"], smooth(ramp(t, T_HATON, T_HATON + 0.4)))
    if T_HATOFF - 0.4 <= t < T_TOSS + 0.45:
        top = (p["head"][0] + 30, p["head"][1] - 190)
        if t < T_HATOFF: q = lerp(p["rhand"], top, smooth(ramp(t, T_HATOFF - 0.4, T_HATOFF)))
        elif t < T_TOSS: q = lerp(top, (p["head"][0] + 120, p["head"][1] - 260), smooth(ramp(t, T_HATOFF + 0.1, T_TOSS)))
        else: q = lerp((p["head"][0] + 120, p["head"][1] - 260), p["rhand"], smooth(ramp(t, T_TOSS + 0.05, T_TOSS + 0.45)))
        p["rhand"] = q; p["relb"] = (q[0] + 110, (q[1] + p["neck"][1]) / 2 + 130); p["rhand_t"] = "grip" if t < T_TOSS else "open"
    return p
S.hook(hat_hook)
def cowboy_hat(cr, t, p, ly):
    if ly != "front": return
    st = hat_state(t)
    if st is None: return
    if st == "hand":
        hx, hy = p["rhand"]
        if t < T_HATON and t < T_HATPOP + 0.25: L.burst_lines(cr, hx, hy - 40, (t - T_HATPOP) / 0.4, r0=60, r1=130, n=8, sid=31)
        O.draw_cowboy_hat(cr, hx - 10, hy - 6, s=0.82, ang=0.1)
        L.draw_grips(cr, p)
    elif st == "cat":
        x, y, a = kitten_spot(p)
        O.draw_cowboy_hat(cr, x - 8, y - 70, s=0.82, ang=a * 0.6 - 0.08)
    else:                                                                  # tossed over his shoulder, off frame left
        u = (t - T_TOSS) / 0.8
        x0, y0 = p["head"][0] + 120, p["head"][1] - 260
        O.draw_cowboy_hat(cr, x0 - 1100 * u, y0 - 380 * math.sin(math.pi * min(1, u * 0.9)) + 500 * u * u, s=0.82, ang=-9 * u)


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

# --- THEATER
L.POSES["cine_sit"] = dict(head=(540, 790), neck=(540, 915), hip=(540, 1250), lelb=(450, 1030), lhand=(395, 1062),
                           relb=(630, 1030), rhand=(685, 1062), lhand_t="grip", rhand_t="grip",
                           lknee=(470, 1270), rknee=(610, 1270), lfoot=(470, FLOOR_Y), rfoot=(610, FLOOR_Y), nowalk=1.0)
SIT = dict(lag=0.4, nowalk=1.0)
def back_cut(t, cam=BACKCAM):
    S.cut(t - FR, cam=cam, x=TX - 540)
    S.set(t - FR, "cine_sit", "deadpan", dur=0.0, back=1.0, **SIT)
def front_cut(t, cam=FRONTCAM, **kw):
    S.cut(t - FR, cam=cam, x=FX - 540)
    S.set(t - FR, "cine_sit", "deadpan", dur=0.0, **SIT, **kw)
BUCK = (FX + 300, SEAT_Y + 400)              # the bucket in the seat next to him (bottom-centre)
# he sits down, takes the hat off the cat and tosses it
front_cut(CUT_THEATER, cam=(FX + 60, 840, 1.25), look=(0.0, 0.0))
S.set(T_HATOFF - 0.4, "cine_sit", "deadpan", dur=0.3, look=(0.2, -1.0), **SIT)
S.set(T_TOSS + 0.2, "cine_sit", "deadpan", dur=0.3, look=(0.0, 0.0), **SIT)
S.sfx(T_TOSS, "whoosh", 0.05)
# back: the empty theater. the tall guy.
back_cut(CUT_BACK1)
S.camera(CUT_BACK1, TX, 780, 1.0, 1.6)
for k in range(3): S.sfx(T_GIANT_IN + 0.5 * k, "step", 0.04)
S.sfx(T_GIANT_SIT, "thud", 0.14); S.shake(T_GIANT_SIT, 0.25, 6)
for tl in (T_LEAN1, T_LEAN2): S.sfx(tl, "squeak", 0.025); S.sfx(tl + 0.35, "squeak", 0.02)
front_cut(CUT_STARE, cam=(FX + 30, 820, 1.32))
S.set(CUT_STARE + 0.5, "cine_sit", "dead_stare", dur=0.4, look=(0.0, 0.0), **SIT)
S.camera(CUT_STARE, FX + 30, 800, 1.42, 1.4)
back_cut(CUT_PREV1)
# eating faster and faster (front)
front_cut(CUT_EAT, cam=(FX + 120, 880, 1.15), look=(0.0, -0.2))
EAT_TS = []
_tt = CUT_EAT + 0.2; per = 0.85
while _tt < CUT_PREV47 - 0.25:
    EAT_TS.append((_tt, per)); _tt += per; per = max(0.2, per * 0.8)
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
            q = lerp(dip, mouth, smooth(u / 0.45)) if u < 0.45 else lerp(mouth, dip, smooth((u - 0.45) / 0.55))
            p["rhand"] = q; p["relb"] = (q[0] + 90, q[1] + 170); p["rhand_t"] = "fist"
            break
    return p
S.hook(eat_hook)
for t0, d in EAT_TS: S.sfx(t0 + d * 0.45, "chomp", 0.035)
S.set(CUT_EAT + 1.6, "cine_sit", "deadpan", dur=0.5, look=(0.0, 0.0), lid=0.45, **SIT)
back_cut(CUT_PREV47)
# the empty bucket + the last kernel
front_cut(CUT_EMPTY, cam=(FX + 120, 880, 1.15), look=(0.8, 0.7), turn=0.3)
def kernel_hook(t, p):
    if not (CUT_EMPTY - FR <= t < CUT_MOVIE - FR): return p
    dip = (BUCK[0] - 40, BUCK[1] - 400); mouth = (p["head"][0] + 25, p["head"][1] + 70)
    if T_RATTLE - 0.3 <= t < T_KERNEL:
        g = smooth(ramp(t, T_RATTLE - 0.3, T_RATTLE))
        q = lerp(p["rhand"], (dip[0] + 18 * math.sin(t * 40) * (t > T_RATTLE), dip[1] + 8 * math.sin(t * 31) * (t > T_RATTLE)), g)
        p["rhand"] = q; p["relb"] = (q[0] + 80, q[1] + 170); p["rhand_t"] = "fist"
    elif T_KERNEL <= t < T_EATK + 0.4:
        q = lerp(dip, mouth, smooth(ramp(t, T_KERNEL, T_EATK))); p["rhand"] = q; p["relb"] = (q[0] + 90, q[1] + 170); p["rhand_t"] = "fist"
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
# the movie starts (back): he can't see it. one more lean.
back_cut(CUT_MOVIE)
S.sfx(CUT_MOVIE + 1.7, "kaboom", 0.12, dur=1.0)
S.sfx(T_LEAN3, "squeak", 0.025); S.sfx(T_LEAN3 + 0.75, "squeak", 0.02)
# front: the periscope
front_cut(CUT_PULL, cam=(FX + 80, 800, 1.18), look=(0.0, 0.0))
S.set(T_DIG2, "cine_sit", "deadpan", dur=0.3, look=(0.5, 0.8), **SIT)
S.set(T_SCOPE_POP + 0.1, "cine_sit", "deadpan", dur=0.3, look=(0.3, -0.2), **SIT)
S.set(T_SCOPE_UP + 0.3, "cine_sit", "deadpan", dur=0.3, look=(0.0, -0.1), **SIT)
S.sfx(T_DIG2 + 0.1, "rummage", 0.05, dur=0.5); S.sfx(T_SCOPE_POP, "pop", 0.09); S.sfx(T_SCOPE_EXT, "slide_up", 0.05)
# back: it rises over the hat
back_cut(CUT_SCOPE_BACK, cam=(TX, 700, 0.9))
S.sfx(CUT_SCOPE_BACK + 0.2, "slide_up", 0.06)
# the periscope view (insert)
S.sfx(CUT_POV, "tick", 0.05)
S.sfx(MOVIE_BOOM, "kaboom", 0.4, dur=1.8); S.sfx(MOVIE_BOOM + 0.3, "whoosh", 0.07); S.sfx(MOVIE_BOOM + 1.6, "thud", 0.12)
# front: watching. lit by the explosions.
front_cut(CUT_WATCH, cam=(FX + 60, 820, 1.3), look=(0.0, 0.0))
S.set(CUT_WATCH + 0.6, "cine_sit", "deadpan", dur=0.8, look=(0.0, 0.0), smile=0.45, **SIT)
S.sfx(CUT_WATCH + 0.3, "kaboom", 0.08, dur=1.0)
# back: THE END. the tall guy gets up and leaves. now he can see the screen.
back_cut(CUT_END)
S.sfx(T_GSTAND, "squeak", 0.04); 
for k in range(3): S.sfx(T_GLEAVE + 0.4 * k, "step", 0.04)
S.sfx(T_LOWER, "slide_down", 0.05)
S.camera(T_GLEAVE + 0.6, TX, 780, 1.08, 1.6)
# front: dead stare. the periscope goes back where it came from.
front_cut(CUT_FINAL, cam=(FX + 30, 820, 1.32), look=(0.0, 0.0))
S.set(T_STOW, "cine_sit", "dead_stare", dur=0.3, look=(0.0, 0.0), **SIT)
S.sfx(T_STOW + 0.15, "zip_down", 0.05)
S.blink(CUT_FINAL + 1.1)
# --- THE ASK (in the aisle)
S.cut(CUT_ASK - FR, cam=(ASKX, 930, 1.15), x=ASKX - 540)
S.set(CUT_ASK - FR, "stand", "deadpan", dur=0.0)
S.t = T_ASK
S.the_ask(T_ASK, hold=ASK_HOLD)

def scope_hook(t, p):
    if not scope_on(t) or setting(t) != "front": return p
    hx, hy = p["head"]
    if t < T_SCOPE_POP:
        return p
    if T_STOW <= t:
        q = lerp((hx + 70, hy + 230), (p["hip"][0] + 60, p["hip"][1] - 40), smooth(ramp(t, T_STOW, T_STOW + 0.3)))
        p["rhand"] = q; p["relb"] = (q[0] + 90, q[1] + 120); p["rhand_t"] = "grip"; return p
    u = scope_up(t)
    by = lerp(hy + 230, hy - 14, u); bx = hx + 78
    p["lhand"] = (bx - 62, by + 30); p["lelb"] = (bx - 140, by + 170)
    p["rhand"] = (bx + 62, by + 30); p["relb"] = (bx + 140, by + 170)
    p["lhand_t"] = p["rhand_t"] = "grip"
    return p
S.hook(scope_hook)
def dig_hook(t, p):
    if T_DIG2 <= t < T_SCOPE_POP:
        hip = (p["hip"][0] + 90, p["hip"][1] - 30)
        u = smooth(ramp(t, T_DIG2, T_DIG2 + 0.2)); dig = ramp(t, T_DIG2 + 0.2, T_DIG2 + 0.3)
        p["rhand"] = lerp(p["rhand"], (hip[0] + 14 * math.sin(t * 24) * dig, hip[1] + 6 * math.sin(t * 31) * dig), u)
    return p
S.hook(dig_hook)
def periscope(cr, t, p, ly):
    if ly != "front" or not scope_on(t): return
    st = setting(t); hx, hy = p["head"]; e = scope_ext(t)
    if st == "front":
        if t >= T_STOW + 0.3: return
        if t >= T_STOW:
            x, y = p["rhand"]; O.draw_periscope(cr, x, y, y - 120, "front"); return
        u = scope_up(t); by = lerp(hy + 230, hy - 14, u); bx = hx + 78
        O.draw_periscope(cr, bx, by, by - 160 - e * 1400, "front")
        if t < T_SCOPE_POP + 0.3: L.burst_lines(cr, bx, by, (t - T_SCOPE_POP) / 0.4, r0=80, r1=170, n=9, sid=33)
        L.draw_grips(cr, p)
    elif st == "back" and CUT_SCOPE_BACK - FR <= t < CUT_FINAL - FR:
        bx = hx + 60
        O.draw_periscope(cr, bx, hy - 60, hy - 160 - e * 560, "back")
S.prop(periscope)

# his row (back view), his seat + armrests + bucket (front view)
def seats_front_layer(cr, t, p, ly):
    st = setting(t)
    if st == "back" and ly == "back" and CUT_THEATER - FR <= t:
        O.draw_popcorn(cr, TX + 205, H_ROW_Y + 240, s=0.6, level=level(t), t=t, label="")
    if st == "back" and ly == "front":
        O.draw_seat_row(cr, TX, H_ROW_Y, n=9, w=190, h=260, gap=16, s=1.0, sid=14800)
        O.draw_seat_row(cr, TX, N_ROW_Y, n=7, w=240, h=320, gap=20, s=1.0, sid=14820)
    if st == "front" and CUT_THEATER - FR <= t < CUT_ASK - FR and ly == "front":
        O.draw_seat_front(cr, FX, SEAT_Y, s=1.0, sid=14620, part="arms")
        L.draw_grips(cr, p)
        O.draw_popcorn(cr, BUCK[0], BUCK[1], s=0.75, level=level(t), t=t)
        for k in range(-3, 4):
            O.draw_seat_row(cr, FX + k * 330, 1215, n=1, w=290, h=300, s=1.0, sid=14840 + k)
S.prop(seats_front_layer)
def lean_hook(t, p):
    if setting(t) == "back" and CUT_BACK1 - FR <= t < CUT_ASK - FR:
        lx = 130 * lean_amt(t)
        for j in ("head", "neck"): p[j] = (p[j][0] + lx, p[j][1])
        p["tilt"] = p.get("tilt", 0.0) + 0.12 * lean_amt(t)
    return p
S.hook(lean_hook)

# the periscope view: an insert (screen space, under the card)
def pov(cr, t):
    if not (CUT_POV - FR <= t < CUT_WATCH - FR): return
    W_, H_ = L.W, L.H
    cr.set_source_rgb(0.03, 0.03, 0.04); cr.paint()
    cx, cy, R = W_ / 2, 1010, 470
    cr.save(); cr.arc(cx, cy, R, 0, 2 * math.pi); cr.clip()
    draw_movie(cr, cx - R * 1.25, cy - R, 2.5 * R, 2 * R, t)
    a = 1 - ramp(t, CUT_POV, CUT_POV + 0.25)
    if a > 0: cr.set_source_rgba(0, 0, 0, a); cr.paint()
    cr.restore()
    cr.arc(cx, cy, R, 0, 2 * math.pi); cr.set_source_rgb(0.03, 0.03, 0.04); cr.set_line_width(26); cr.stroke()
    for (x1, y1, x2, y2) in ((cx - R, cy, cx - 60, cy), (cx + 60, cy, cx + R, cy), (cx, cy - R, cx, cy - 60), (cx, cy + 60, cx, cy + R)):
        cr.move_to(x1, y1); cr.line_to(x2, y2); cr.set_source_rgba(0, 0, 0, 0.35); cr.set_line_width(4); cr.stroke()
S.overlays.insert(0, pov)


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
    look = (0.0, 0.0); blink = 0.0
    if st == "street":
        if T_TURN <= t < T_RUN1 + 0.6: look = (0.9, -0.2)
        if T_LOOKUP <= t < T_WALK1: look = (0.6, -0.9)
        if T_HATPOP <= t < T_HATON: look = (0.4, -0.6)                          # watches the hat come
        if T_HATON <= t: look = (0.8, 0.1)                                     # ...then stares at the usher too
        if T_TWITCH <= t < T_TWITCH + 0.3: a += 0.06 * math.sin((t - T_TWITCH) * 60)
    if st == "lobby":
        look = (0.7, -0.6) if t < T_TAP else (0.6, 0.3)
        if CUT_TWO - FR <= t < CUT_TIP2: look = (0.8, 0.0); blink = 0.3
    if st == "front":
        look = (0.0, -0.3)
        if T_HATOFF - 0.3 <= t < T_TOSS + 0.6: look = (-0.8, -0.3) if t >= T_TOSS else (0.3, -0.6)
        if CUT_EAT - FR <= t < CUT_PREV47: look = (0.6, 0.8)
        if CUT_PULL - FR <= t < CUT_SCOPE_BACK: look = (0.5, 0.5) if t < T_SCOPE_POP else (0.5, -0.9)
        if CUT_WATCH - FR <= t < CUT_END:
            look = (0.4, -0.9)
            if CUT_WATCH + 0.6 <= t < CUT_WATCH + 1.4: blink = math.sin(math.pi * (t - CUT_WATCH - 0.6) / 0.8)
        if t >= CUT_ASK - FR: look = (0.0, 0.0)
    O.draw_cat(cr, x, y, s=KS, t=t, kind="loaf", col="black", look=look, blink=blink, sid=2000, tilt=a * 0.6)
S.prop(kitten)
S.prop(cowboy_hat)

# light from the screen washing over the front shots (orange flashes while he watches the movie)
def wash(cr, t):
    if setting(t) != "front" or t >= CUT_ASK - FR or t < CUT_THEATER - FR: return
    if CUT_WATCH - FR <= t < CUT_END:
        a = 0.10 + 0.06 * max(0.0, math.sin(t * 13)) ; col = (0.98, 0.62, 0.28)
    else:
        a = 0.08 + 0.03 * math.sin(t * 5.3) * math.sin(t * 2.1); col = (0.55, 0.65, 0.95)
    cr.set_source_rgba(col[0], col[1], col[2], a * (1 - 0.6 * lights(t))); cr.paint()
S.overlays.insert(0, wash)

if __name__ == "__main__":
    print(f"end {S.t:.2f}", file=sys.stderr)
    S.render("day013.mp4")
