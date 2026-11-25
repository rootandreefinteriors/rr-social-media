"""Day 34: IG @cr1ms0n_h0rnet: "Name the dinosaur Jerry". See BEATS.md.
On Mars a dust storm rolls in; he rides his T. rex out to the right, out of the dust wall into MARS BASE 1. A HELLO MY
NAME IS sticker: JERRY. It ignores the name (JERRY!, JERRY!!!, its tail nearly takes his head off). A potato from the
greenhouse works - only with a potato. A potato on a stick: the chase stomps JERRY across Mars, visible from space. It
catches the potato. JERRY? - it nuzzles him. The rover catches up with its own blank name tag. The ask at the base.
"""
import sys, os, math, random
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
import character as C
from ltcd import ramp, lerp, pulse, FLOOR_Y
from ink import smooth, sketch_line, draw_text

# Mars (day 33) is drawn with day 33's own code
_spec = importlib.util.spec_from_file_location("ep033_episode", os.path.join(HERE, "..", "ep033", "episode.py"))
E33 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(E33)
E32 = E33.E32

FR = 1 / 30
sk_rect, sk_poly, sk_circ, sk_ell = O.sketch_rect, O.sketch_poly, O.sketch_circle, O.sketch_ellipse
INKC = (0.07, 0.07, 0.09)
RS = E33.RS
cam = E33.cam
rex_world = E33.rex_world
helmet = E33.helmet

# ================================================================ places
MRS = E33.MRS
HF = E33.HF                            # him at the landing site (day 33 ask)
REX_M = E33.REX_M
RKM = E33.RKM
BASE = 12600000.0                      # MARS BASE 1
DW = BASE - 2300.0                     # the dust wall (the border)
GH = BASE - 1150.0                     # the greenhouse dome
HAB = BASE + 2100.0                    # the habitat dome
SIGN_X = BASE + 1250.0
HB = BASE + 60.0                       # him at the base
REX_B = HB + 690.0                     # the rex (near foot) at the base
OV = 12700000.0                        # the overhead (satellite) view
PL = 12800000.0                        # the planet from space

# ================================================================ timeline
T_READ = 0.3
T_LOOKREX = 1.6; T_TILT = 1.9
T_RUMBLE = 2.3; T_LOOKL = 2.55
CUT_RIDE = 3.3; T_BOLT = 3.45
CUT_BASE = 5.2; T_SKID = 6.0
CUT_STAND = 6.6
T_TAG = 6.75; POP_TAG = T_TAG + 2.1
T_W0, T_W1 = 9.35, 10.35
T_SHOW = 10.5
T_STEP = 11.25; T_SLAP = 12.0
T_DOWN = 12.45; T_ARMS0, T_ARMS1 = 12.9, 14.1
CUT_SIGN = 14.3; T_SHAKE = 15.2; T_YAWN = 15.8
CUT_SIGN2 = 16.8; T_TAIL = 17.35; T_DUCK = 17.25
T_UP2 = 18.4; T_STARE = 18.75
T_SLIDE = 19.75; T_IDEA = 20.35
CUT_GH = 20.9; T_GRAB = 21.15; T_YANK = 21.55
CUT_FEED = 22.4; T_WHIP = 22.65; T_STOMP0, T_STOMP1 = 22.95, 23.45; T_CHOMP = 23.8
T_EMPTY = 24.15
T_SIGN3 = 25.0; T_AWAY = 25.35; T_US = 25.7
CUT_ROD = 26.5; T_LUNGE = 27.15
CUT_OV = 27.9; LET_DUR = 1.15
CUT_PLANET = CUT_OV + 5 * LET_DUR + 0.45          # 34.1
CUT_END = CUT_PLANET + 2.05                        # 36.15
T_SKID2 = CUT_END + 0.55; T_CHOMP2 = CUT_END + 0.85
CUT_LAST = CUT_END + 1.75                          # 37.9
T_HEART0 = CUT_LAST + 0.3
T_TURN = CUT_LAST + 1.25; T_NUZ = CUT_LAST + 1.95; T_SMILE = CUT_LAST + 2.3
T_ROV0, T_ROV1 = 41.4, 42.3
T_BEEP = 42.45; T_TAGUP0, T_TAGUP1 = 42.7, 43.2
T_LOOKROV = 43.3; T_LOOKUS = 43.95
T_ASK = 44.6; HOLD = 9.5

# ================================================================ the rex (Jerry)
def rex(t):
    """(X near foot, lift, pitch, face, st)."""
    st = dict(O.DINO); st.update(s=RS, look=(-0.6, 0.6), smile=0.6, lid=0.0, mouth=0.0, arms=0.0, walk=0.0)
    X, lift, pitch, face = REX_M, 0.0, 0.0, -1
    if t < CUT_RIDE:
        if t >= T_TILT: pitch = 0.07 * smooth(ramp(t, T_TILT, T_TILT + 0.3)); st["look"] = (-0.8, 0.3); st["smile"] = 0.3
        if t >= T_LOOKL + 0.15:
            st["look"] = (-1.0, -0.1); pitch = 0.0; st["pupil"] = 0.6; st["smile"] = 0.0; st["worry"] = 0.6
    elif t < CUT_STAND - FR:
        face = 1; st["look"] = (-1.0, 0.0)
        if t < CUT_BASE - FR:
            u = max(0.0, t - T_BOLT)
            X = REX_M - 250 + 700 * u + 900 * u * u
            if t >= T_BOLT:
                st["walk"] = u * 16.0; pitch = 0.10 + 0.05 * math.sin(u * 16); lift = 40 * abs(math.sin(u * 8)); st["mouth"] = 0.2
        else:
            u = ramp(t, CUT_BASE, T_SKID)
            X = lerp(DW - 200, REX_B - 300, 1 - (1 - u) ** 2)
            st["walk"] = 0.0 if u > 0.55 else (t - CUT_BASE) * 16
            pitch = 0.22 * math.sin(math.pi * u)
    elif t < CUT_GH - FR:
        X = REX_B; face = -1; st["look"] = (-0.8, 0.4); st["smile"] = 0.6
        if t >= POP_TAG: st["look"] = (-0.9, 0.7)
        if t >= T_SLAP - 0.1:
            st["look"] = (-0.3, 1.0); pitch = 0.0
        if t >= T_DOWN:
            pitch = 0.16 * smooth(ramp(t, T_DOWN, T_DOWN + 0.4)); st["look"] = (0.4, 1.0)
        if T_ARMS0 <= t < T_ARMS1:
            st["arms"] = 0.5 + 0.5 * math.sin((t - T_ARMS0) * 22); st["worry"] = 0.5; st["brow"] = 0.4
        if t >= T_ARMS1: st["arms"] = 0.0; st["worry"] = 0.0; st["brow"] = 0.0; pitch = 0.0; st["look"] = (-0.8, 0.4)
        if t >= CUT_SIGN - FR:
            st["look"] = (0.2, -1.0); pitch = -0.05; st["smile"] = 0.4; st["lid"] = 0.2
            if T_YAWN <= t < T_YAWN + 0.9:
                k = math.sin(math.pi * ramp(t, T_YAWN, T_YAWN + 0.9)); st["mouth"] = 1.0 * k; st["lid"] = 0.2 + 0.6 * k; pitch = -0.05 - 0.10 * k
        if t >= CUT_SIGN2 - FR:
            face = 1; X = REX_B - 380; st["look"] = (-1.0, -0.4); st["lid"] = 0.35; st["mouth"] = 0.0
            # the tail swings low past his head, then back
            pitch = -0.30 * math.sin(math.pi * ramp(t, T_TAIL - 0.3, T_TAIL + 0.5))
    elif t < CUT_FEED - FR:
        X = REX_B; face = -1
    elif t < CUT_ROD - FR:
        X = REX_B; face = -1; st["look"] = (0.3, -0.6); st["smile"] = 0.4
        if t >= T_WHIP:
            st["look"] = (-1.0, 0.5); st["pupil"] = 1.5; st["smile"] = 1.0
        if t >= T_STOMP0:
            u = smooth(ramp(t, T_STOMP0, T_STOMP1))
            X = REX_B - 220 * u
            st["walk"] = 0.0 if t >= T_STOMP1 else (t - T_STOMP0) * 14
        if t >= T_STOMP1:
            pitch = 0.42 * smooth(ramp(t, T_STOMP1, T_CHOMP - 0.05))
            st["mouth"] = 0.9 * ramp(t, T_STOMP1, T_CHOMP - 0.1)
        if t >= T_CHOMP:
            pitch = 0.42 * (1 - smooth(ramp(t, T_CHOMP, T_CHOMP + 0.45))); st["mouth"] = 0.15 + 0.15 * math.sin((t - T_CHOMP) * 18)
            st["eyes"] = "happy"; st["pupil"] = 1.0
        if t >= T_SIGN3:
            st["mouth"] = 0.0; st["eyes"] = "normal"; st["look"] = (-0.9, 0.4)
        if t >= T_AWAY:
            st["look"] = (1.0, -0.6); st["lid"] = 0.3; st["smile"] = 0.4
    elif t < CUT_OV - FR:
        face = 1; st["look"] = (1.0, 0.0); st["pupil"] = 0.7
        X = REX_B - 300
        st["look"] = (1.0, -0.2); st["eyes"] = "normal"
        if t >= T_LUNGE:
            u = t - T_LUNGE
            X = REX_B - 300 + 500 * u + 900 * u * u
            st["walk"] = u * 16; pitch = 0.12 + 0.05 * math.sin(u * 16); lift = 40 * abs(math.sin(u * 8)); st["mouth"] = 0.5
    elif t < CUT_END - FR:
        X = REX_B
    elif t < CUT_LAST - FR:
        face = 1
        u = ramp(t, CUT_END, T_SKID2)
        X = lerp(REX_B - 1500, REX_B - 300, 1 - (1 - u) ** 2)
        st["walk"] = 0.0 if u > 0.6 else (t - CUT_END) * 16
        pitch = 0.18 * math.sin(math.pi * u); st["look"] = (1.0, -0.1); st["mouth"] = 0.5
        if t >= T_SKID2:
            st["mouth"] = 0.5 + 0.2 * math.sin(t * 25); pitch = 0.05
        if t >= T_CHOMP2 - 0.15:
            k = pulse(t, T_CHOMP2, 0.18)
            pitch = 0.05 + 0.18 * k; st["mouth"] = 0.8 * k if t < T_CHOMP2 else 0.2 + 0.1 * math.sin(t * 18)
            if t >= T_CHOMP2 + 0.2: st["eyes"] = "happy"; st["smile"] = 1.0
    else:
        X = REX_B; face = -1; st["look"] = (0.6, -0.5); st["smile"] = 0.5; st["lid"] = 0.25
        if t >= T_TURN:
            k = smooth(ramp(t, T_TURN, T_NUZ))
            st["look"] = (-1.0, 0.8); st["lid"] = 0.0; st["smile"] = 0.9
            pitch = 0.40 * k
            X = REX_B - 120 * k
        if t >= T_NUZ:
            st["eyes"] = "happy"; st["smile"] = 1.0
            pitch = 0.40 + 0.03 * math.sin((t - T_NUZ) * 9)
        if t >= T_SMILE + 0.9:
            k = smooth(ramp(t, T_SMILE + 0.9, T_SMILE + 1.5))
            pitch = lerp(pitch, 0.06, k); X = lerp(REX_B - 120, REX_B, k)
            if k > 0.5: st["eyes"] = "normal"; st["look"] = (-0.6, 0.6)
        if t >= T_ROV0 + 0.3: st["look"] = (-1.0, 0.5)
        if t >= T_ASK: st["look"] = (-0.6, 0.6); st["smile"] = 0.8
    return X, lift, pitch, face, st

def seat(t):
    X, lift, pitch, face, st = rex(t)
    x, y = rex_world(X, lift, pitch, face, 215, 615)
    return (x, y - O._walkbob(st))

def rex_head_c(t):
    X, lift, pitch, face, st = rex(t)
    x, y = rex_world(X, lift, pitch, face, -235, 930)
    return x, y - O._walkbob(st)

TAG_LH = (-60, 560)                     # the tag on its belly (rex-local)
def tag_on_rex(t): return t >= T_SLAP

def rex_drawn(t):
    if CUT_GH - FR <= t < CUT_FEED - FR: return False
    if CUT_OV - FR <= t < CUT_END - FR: return False
    return True

def draw_rex(cr, t):
    if not rex_drawn(t): return
    X, lift, pitch, face, st = rex(t)
    blink = 0.0
    for b in (1.0, 5.8, 9.9, 13.5, 21.0, 30.0, 39.2, 47.0, 52.5):
        if b <= t < b + 0.16: blink = math.sin(math.pi * (t - b) / 0.16)
    cr.save(); cr.translate(0, -lift)
    O.draw_trex(cr, X, st, t, face=face, pitch=pitch, blink=blink)
    cr.restore()
    x, y = rex_world(X, lift, pitch, face, 215, 600)
    E32.draw_saddle(cr, x, y + 10 - O._walkbob(st), pitch * face + 0.08 * face, 1.0, sid=33510, stirrups=False)
    if tag_on_rex(t) and face == -1:
        tx, ty = rex_world(X, lift, pitch, face, *TAG_LH)
        name_tag(cr, tx, ty - O._walkbob(st), 1.1, ang=-0.12 + pitch * face, sid=36010)
    hx, hy = rex_head_c(t)
    helmet(cr, hx, hy, 300, sid=33020)

# ================================================================ props
def name_tag(cr, x, y, s=1.0, ang=0.0, text="JERRY", reveal=1.0, sid=36000):
    """a HELLO MY NAME IS sticker centred (x, y), 200 x 140 at s=1."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sk_rect(cr, -100, -70, 100, 70, 4, sid=sid, fill=(0.98, 0.98, 0.97))
    cr.rectangle(-98, -68, 196, 52); cr.set_source_rgb(0.86, 0.14, 0.14); cr.fill()
    cr.rectangle(-98, 54, 196, 14); cr.set_source_rgb(0.86, 0.14, 0.14); cr.fill()
    sk_rect(cr, -100, -70, 100, 70, 4, sid=sid, fill=None)
    draw_text(cr, "HELLO", 0, -52, 26, color=(255, 255, 255))
    draw_text(cr, "MY NAME IS", 0, -28, 16, color=(255, 255, 255))
    if text and reveal > 0.01:
        n = max(0, min(len(text), int(math.ceil(len(text) * reveal))))
        if n: draw_text(cr, text[:n], -78, 18, 46, anchor="left")
    cr.restore()

def potato(cr, x, y, r=60, ang=0.0, sid=36100, roots=False):
    cr.save(); cr.translate(x, y); cr.rotate(ang)
    if roots:
        for k in range(4):
            sketch_line(cr, [(-r * 0.3 + k * r * 0.2, r * 0.6), (-r * 0.5 + k * r * 0.35, r * 1.3)], 3, sid=sid + 10 + k, color=(0.45, 0.32, 0.18))
        for k in range(3):
            sketch_line(cr, [(-r * 0.2 + k * r * 0.2, -r * 0.6), (-r * 0.6 + k * r * 0.6, -r * 1.6)], 6, sid=sid + 20 + k, color=(0.25, 0.55, 0.22))
            sk_ell(cr, -r * 0.6 + k * r * 0.6, -r * 1.7, r * 0.28, r * 0.15, 3, sid=sid + 25 + k, fill=(0.45, 0.75, 0.35))
    sk_ell(cr, 0, 0, r * 1.25, r * 0.9, 5, sid=sid, fill=(0.78, 0.60, 0.36))
    for k, (dx, dy) in enumerate(((-0.5, -0.2), (0.3, -0.35), (0.55, 0.25), (-0.15, 0.35))):
        cr.arc(dx * r, dy * r, r * 0.07, 0, 2 * math.pi); cr.set_source_rgb(0.50, 0.36, 0.20); cr.fill()
    cr.restore()

def placard(cr, x, y, text, s=1.0, sid=36200):
    """a hand-held sign centred (x, y): 360 x 180."""
    sk_rect(cr, x - 180 * s, y - 90 * s, x + 180 * s, y + 90 * s, 5, sid=sid, fill=(0.97, 0.95, 0.88))
    draw_text(cr, text, x, y + 4, int((92 if len(text) <= 6 else 74) * s), max_w=330 * s)

def stick_tip(t, p):
    X, lift, pitch, face, st = rex(t)
    n = O.trex_pt(X, st, face, pitch, "nose")
    return (n[0] + 120, n[1] - lift - 330)

def draw_stick(cr, t, p):
    if not (CUT_ROD - FR <= t < CUT_OV - FR or CUT_END - FR <= t < CUT_LAST - FR): return
    h = p["rhand"]; tip = stick_tip(t, p)
    sketch_line(cr, [h, tip], 9, sid=36300, amp=0.2, color=(0.50, 0.33, 0.16))
    if t >= CUT_END - FR and t >= T_CHOMP2: return
    sw = 0.2 * math.sin(t * 5)
    px, py = tip[0] + 220 * math.sin(sw), tip[1] + 220 * math.cos(sw)
    sketch_line(cr, [tip, (px, py)], 3, sid=36301, amp=0.1)
    potato(cr, px, py + 55, 65, ang=0.2, sid=36120)

# ================================================================ worlds
MSKY = E33.MSKY
HOR = E33.HOR

def mars_sky_ground(cr, x0, seed=34):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    a, b = vx0 - 50, vx1 + 50
    for i, (y, c) in enumerate(MSKY):
        y1 = MSKY[i + 1][0] if i + 1 < len(MSKY) else HOR
        top = y if i > 0 else min(y, vy0 - 100)
        cr.rectangle(a, top, b - a, y1 - top + 1); cr.set_source_rgb(*c); cr.fill()
    return a, b

def draw_storm(cr, x, t, sid=36400):
    """the red dust storm wall, its front edge at x, everything left of it is dust."""
    for k in range(30):
        yy = FLOOR_Y + 120 - 150 * (k // 2)
        xx = x + (100 if k % 2 else -120) + 60 * math.sin(t * 2.3 + k)
        sk_circ(cr, xx, yy, 260 + 40 * math.sin(k * 1.9), 5, sid=sid + 20 + k % 7, fill=(0.80, 0.48, 0.32))
    cr.rectangle(x - 6000, -9000, 6000 - 60, FLOOR_Y + 11000); cr.set_source_rgba(0.72, 0.40, 0.26, 0.97); cr.fill()
    rr = random.Random(sid)
    for k in range(14):
        sx = x - 200 - rr.uniform(0, 1400) + ((t * 900 + k * 130) % 600)
        sy = FLOOR_Y - rr.uniform(0, 2200)
        sketch_line(cr, [(sx, sy), (sx + 200, sy + 20)], 5, sid=sid + k % 5, color=(0.55, 0.28, 0.18), alpha=0.7)

def storm_x(t):
    if t < CUT_RIDE - FR:
        return MRS - 1000 + 900 * smooth(ramp(t, T_RUMBLE, CUT_RIDE))
    X, lift, pitch, face, st = rex(t)
    return X - 1150 + 60 * math.sin(t * 3)

def draw_greenhouse(cr, t, inside=False):
    x, r = GH, 900
    yb = FLOOR_Y
    sk_rect(cr, x - r - 40, yb - 60, x + r + 40, yb + 10, 5, sid=36500, fill=(0.85, 0.85, 0.88))
    # planter rows of potato plants
    for row in range(2):
        py = yb - 60 - 110 * row
        sk_rect(cr, x - r + 80 + 40 * row, py - 50, x + r - 80 - 40 * row, py, 4, sid=36501 + row, fill=(0.45, 0.30, 0.20))
        for k in range(8 - row):
            px = x - r + 150 + 40 * row + k * (2 * r - 300 - 80 * row) / (7 - row)
            for j in range(3):
                a = -math.pi / 2 + (j - 1) * 0.6
                sketch_line(cr, [(px, py - 50), (px + 60 * math.cos(a), py - 50 + 70 * math.sin(a))], 5, sid=36510 + j, color=(0.25, 0.55, 0.22))
                sk_ell(cr, px + 70 * math.cos(a), py - 50 + 80 * math.sin(a), 22, 13, 2, sid=36520 + j, fill=(0.45, 0.75, 0.35))
    # the dome
    cr.arc(x, yb - 60, r, math.pi, 2 * math.pi); cr.close_path(); cr.set_source_rgba(0.85, 0.95, 1.0, 0.22); cr.fill()
    cr.arc(x, yb - 60, r, math.pi, 2 * math.pi); cr.set_source_rgb(*INKC); cr.set_line_width(7); cr.stroke()
    for k in range(1, 5):
        a = math.pi + k * math.pi / 5
        sketch_line(cr, [(x, yb - 60 - r), (x + r * math.cos(a), yb - 60 + r * math.sin(a))], 3, sid=36530 + k, alpha=0.35)
    cr.arc(x, yb - 60, r * 0.6, math.pi, 2 * math.pi); cr.set_source_rgba(*INKC, 0.35); cr.set_line_width(3); cr.stroke()
    cr.arc(x, yb - 60, r * 0.85, math.pi * 1.15, math.pi * 1.4); cr.set_source_rgba(1, 1, 1, 0.8); cr.set_line_width(12); cr.stroke()

def draw_hab(cr, t):
    x, r = HAB, 820
    cr.arc(x, FLOOR_Y - 40, r, math.pi, 2 * math.pi); cr.close_path(); cr.set_source_rgb(0.95, 0.95, 0.93); cr.fill()
    cr.arc(x, FLOOR_Y - 40, r, math.pi, 2 * math.pi); cr.set_source_rgb(*INKC); cr.set_line_width(7); cr.stroke()
    for k in range(1, 4):
        cr.arc(x, FLOOR_Y - 40, r, math.pi + k * 0.25 * math.pi - 0.02, math.pi + k * 0.25 * math.pi + 0.02)
    for k in range(3):
        sketch_line(cr, [(x - r + 60, FLOOR_Y - 40 - 200 * (k + 1)), (x + r - 60, FLOOR_Y - 40 - 200 * (k + 1))], 3, sid=36610 + k, alpha=0.25)
    sk_rect(cr, x - 160, FLOOR_Y - 420, x + 160, FLOOR_Y, 6, sid=36620, fill=(0.80, 0.80, 0.84))      # airlock
    sk_circ(cr, x, FLOOR_Y - 280, 70, 5, sid=36621, fill=(0.55, 0.75, 0.95))
    sk_rect(cr, x - 40, FLOOR_Y - 820, x + 40, FLOOR_Y - 760, 3, sid=36622, fill=(0.86, 0.14, 0.14))
    # antenna dish
    ax = HAB + 1150
    sketch_line(cr, [(ax, FLOOR_Y), (ax, FLOOR_Y - 700)], 10, sid=36630, amp=0.2, color=(0.6, 0.6, 0.65))
    cr.save(); cr.translate(ax, FLOOR_Y - 760); cr.rotate(-0.5)
    sk_ell(cr, 0, 0, 260, 90, 5, sid=36631, fill=(0.92, 0.92, 0.94)); cr.restore()
    sk_circ(cr, ax - 40, FLOOR_Y - 840, 14, 3, sid=36632, fill=(0.86, 0.14, 0.14))

def draw_sign(cr, t):
    x = SIGN_X
    for d in (-170, 170):
        sketch_line(cr, [(x + d, FLOOR_Y), (x + d, FLOOR_Y - 560)], 9, sid=36700 + (d > 0), amp=0.2, color=(0.5, 0.5, 0.55))
    sk_rect(cr, x - 260, FLOOR_Y - 840, x + 260, FLOOR_Y - 520, 6, sid=36702, fill=(0.95, 0.95, 0.93))
    draw_text(cr, "MARS BASE 1", x, FLOOR_Y - 750, 66)
    draw_text(cr, "POP. 0", x, FLOOR_Y - 620, 66, color=(200, 40, 40))

def draw_base(cr, t):
    a, b = mars_sky_ground(cr, BASE)
    cx, cy, z = L.cam_track.at(t)
    sk_circ(cr, cx - 250 / z, cy - 640 / z, 26 / z, 3, sid=34700, fill=(0.72, 0.66, 0.60))
    sk_ell(cr, cx - 120 / z, cy - 560 / z, 15 / z, 11 / z, 3, sid=34701, fill=(0.72, 0.66, 0.60))
    # far ridges
    sk_poly(cr, [(BASE - 5000, HOR), (BASE - 3400, HOR - 260), (BASE - 1800, HOR - 160), (BASE + 200, HOR - 330), (BASE + 2300, HOR - 200),
                 (BASE + 4300, HOR - 380), (BASE + 6500, HOR)], 5, sid=36800, fill=(0.80, 0.52, 0.38))
    cr.rectangle(a, HOR, b - a, FLOOR_Y - HOR + 1); cr.set_source_rgb(0.80, 0.46, 0.30); cr.fill()
    cr.rectangle(a, FLOOR_Y, b - a, 1600); cr.set_source_rgb(0.72, 0.38, 0.24); cr.fill()
    rr = random.Random(34)
    for k in range(70):
        x = BASE - 3500 + k * 140 + rr.uniform(-50, 50); y = HOR + 30 + rr.uniform(0, FLOOR_Y - HOR - 40)
        if a < x < b:
            sk_ell(cr, x, y, rr.uniform(10, 30), rr.uniform(5, 12), 2, sid=34730 + k % 9, fill=(0.62, 0.32, 0.20))
    for k in range(22):
        x = BASE - 3200 + k * 420 + rr.uniform(-80, 80); y = FLOOR_Y + rr.uniform(80, 500)
        if a < x < b:
            sk_poly(cr, [(x - 70, y), (x - 40, y - 50), (x + 30, y - 60), (x + 80, y)], 4, sid=34740 + k % 9, fill=(0.56, 0.30, 0.20))
    sketch_line(cr, [(a, FLOOR_Y), (b, FLOOR_Y)], 6, sid=34770, amp=0.3)
    draw_hab(cr, t)
    draw_sign(cr, t)
    draw_greenhouse(cr, t)
    # the giant three-toed tracks after the run (the end of the Y)
    if t >= CUT_END - FR:
        for k in range(6):
            x = REX_B - 1600 + 230 * k
            if x < REX_B - 300:
                sk_ell(cr, x, FLOOR_Y + 40 + 25 * (k % 2), 70, 16, 3, sid=36900 + k, fill=(0.55, 0.28, 0.18))

# ---- overhead (satellite) view: the rex stomps JERRY
U = 420.0
STROKES = [
    [(0.15, 0.0), (0.8, 0.0), (0.8, 1.05), (0.7, 1.3), (0.42, 1.4), (0.15, 1.3), (0.02, 1.08)],                          # J
    [(0.9, 0.0), (0.0, 0.0), (0.0, 0.7), (0.7, 0.7), (0.0, 0.7), (0.0, 1.4), (0.9, 1.4)],                                # E
    [(0.0, 1.4), (0.0, 0.0), (0.6, 0.0), (0.85, 0.2), (0.85, 0.5), (0.6, 0.7), (0.0, 0.7), (0.9, 1.4)],                 # R
    [(0.0, 1.4), (0.0, 0.0), (0.6, 0.0), (0.85, 0.2), (0.85, 0.5), (0.6, 0.7), (0.0, 0.7), (0.9, 1.4)],                 # R
    [(0.0, 0.0), (0.45, 0.7), (0.9, 0.0), (0.45, 0.7), (0.45, 1.4)],                                                     # Y
]
def letter_pts(i):
    ox = OV - 2.6 * U + i * 1.15 * U
    oy = FLOOR_Y - 0.7 * U
    return [(ox + x * U, oy + y * U) for x, y in STROKES[i]]

def path_at(pts, u):
    seg = [math.hypot(pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1]) for k in range(len(pts) - 1)]
    tot = sum(seg); d = u * tot
    for k, s in enumerate(seg):
        if d <= s or k == len(seg) - 1:
            f = min(1.0, d / s if s else 0)
            a, b = pts[k], pts[k + 1]
            return (lerp(a[0], b[0], f), lerp(a[1], b[1], f)), math.atan2(b[1] - a[1], b[0] - a[0]), k, f
        d -= s

def partial(pts, u):
    (x, y), ang, k, f = path_at(pts, u)
    return pts[:k + 1] + [(x, y)]

def letter_u(i, t):
    t0 = CUT_OV + i * LET_DUR
    return ramp(t, t0 + 0.12, t0 + LET_DUR - 0.08, "linear")

def draw_overhead(cr, t):
    vx0, vy0, vx1, vy1 = O._visible(cr)
    cr.rectangle(vx0 - 50, vy0 - 50, vx1 - vx0 + 100, vy1 - vy0 + 100); cr.set_source_rgb(0.78, 0.44, 0.28); cr.fill()
    rr = random.Random(77)
    for k in range(60):
        x = OV - 4000 + rr.uniform(0, 8000); y = FLOOR_Y - 3000 + rr.uniform(0, 6000)
        r = rr.uniform(30, 140)
        sk_circ(cr, x, y, r, 3, sid=37000 + k % 9, fill=(0.70, 0.38, 0.24))
        cr.arc(x + r * 0.15, y + r * 0.15, r * 0.7, 0, 2 * math.pi); cr.set_source_rgba(0.55, 0.28, 0.18, 0.5); cr.fill()
    # the base from above (two domes)
    for (x, y, r) in ((OV - 2300, FLOOR_Y + 1150, 260), (OV - 1750, FLOOR_Y + 1250, 190)):
        sk_circ(cr, x, y, r, 5, sid=37020, fill=(0.95, 0.95, 0.93))
        cr.arc(x - r * 0.3, y - r * 0.3, r * 0.4, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.6); cr.fill()
    # the trenches
    for i in range(5):
        u = letter_u(i, t)
        if u <= 0: continue
        pts = partial(letter_pts(i), u)
        for w, c in ((70, (0.50, 0.25, 0.15)), (40, (0.40, 0.19, 0.11))):
            cr.move_to(*pts[0])
            for q in pts[1:]: cr.line_to(*q)
            cr.set_source_rgb(*c); cr.set_line_width(w); cr.set_line_cap(1); cr.set_line_join(1); cr.stroke()
    # the rex from above, chasing the potato
    i = min(4, int((t - CUT_OV) / LET_DUR))
    u = letter_u(i, t)
    t0 = CUT_OV + i * LET_DUR
    if t < t0 + 0.12 and i > 0:                         # hop to the next letter
        a = letter_pts(i - 1)[-1]; b = letter_pts(i)[0]
        f = ramp(t, t0 - 0.08, t0 + 0.12)
        (x, y), ang, hop = (lerp(a[0], b[0], f), lerp(a[1], b[1], f)), math.atan2(b[1] - a[1], b[0] - a[0]), math.sin(math.pi * f)
    else:
        (x, y), ang, k, f = path_at(letter_pts(i), u); hop = 0.0
    top_rex(cr, x, y, ang, t, 1.7 + 0.6 * hop)
    # dust kicked up
    for k in range(4):
        q = ((t * 3 + k / 4) % 1.0)
        O.draw_smoke_puff(cr, x - math.cos(ang) * (90 + 120 * q), y - math.sin(ang) * (90 + 120 * q), 40 + 50 * q, alpha=0.6 * (1 - q), dark=0.3)

def top_rex(cr, x, y, ang, t, s=1.0):
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    g = O.DINO_GREEN
    sk_poly(cr, [(-60, -18), (-230, -4 + 20 * math.sin(t * 20)), (-60, 18)], 3, sid=37100, fill=g)                # tail
    for d in (-1, 1):
        ph = math.sin(t * 22 + (d > 0) * math.pi)
        sk_ell(cr, -10 + 30 * ph * d, d * 42, 34, 16, 3, sid=37101 + (d > 0), fill=g)                              # legs
    sk_ell(cr, 0, 0, 85, 44, 4, sid=37103, fill=g)                                                                  # body
    sk_ell(cr, 100, 0, 52, 34, 4, sid=37104, fill=g)                                                                # head
    cr.arc(100, 0, 64, 0, 2 * math.pi); cr.set_source_rgba(0.85, 0.95, 1.0, 0.3); cr.fill_preserve()
    cr.set_source_rgb(*INKC); cr.set_line_width(3); cr.stroke()
    sk_circ(cr, -10, 0, 22, 3, sid=37105, fill=(0.98, 0.98, 1.0))                                                    # him (from above)
    sk_circ(cr, -10, 0, 30, 2, sid=37106, fill=None)
    sketch_line(cr, [(10, 10), (250, 40)], 4, sid=37107, color=(0.50, 0.33, 0.16))                                 # the stick
    potato(cr, 262, 42, 18, sid=37110)
    cr.restore()

# ---- the planet with JERRY on it
def draw_planet(cr, t):
    E33.stars(cr, t, 0, 0, n=120, seed=4)
    R = 2600
    cx, cy = PL, FLOOR_Y + 300
    cr.arc(cx, cy, R + 120, 0, 2 * math.pi); cr.set_source_rgba(1.0, 0.6, 0.4, 0.15); cr.fill()
    cr.arc(cx, cy, R, 0, 2 * math.pi); cr.set_source_rgb(0.80, 0.38, 0.22); cr.fill()
    cr.save(); cr.arc(cx, cy, R, 0, 2 * math.pi); cr.clip()
    rr = random.Random(8)
    for k in range(30):
        a = rr.uniform(0, 2 * math.pi); d = rr.uniform(0, 0.95) * R
        sk_ell(cr, cx + math.cos(a) * d, cy + math.sin(a) * d, rr.uniform(80, 300), rr.uniform(40, 140), 4, sid=37200 + k % 9, fill=(0.68, 0.31, 0.18))
    sk_ell(cr, cx, cy - R + 160, 900, 150, 0.1, sid=37230, fill=(1, 1, 1), alpha=0.75)        # the ice cap
    draw_text(cr, "JERRY", cx + 60, cy - 120, 980, color=(95, 40, 22), rot=-0.06)
    # night side shading
    cr.arc(cx + R * 0.55, cy + R * 0.2, R * 1.1, 0, 2 * math.pi); cr.set_source_rgba(0, 0, 0.05, 0.25); cr.fill()
    cr.restore()
    cr.arc(cx, cy, R, 0, 2 * math.pi); cr.set_source_rgb(*INKC); cr.set_line_width(14); cr.stroke()
    # a little moon passes in front
    u = ramp(t, CUT_PLANET, CUT_END, "linear")
    mx = lerp(cx - 3400, cx + 1200, u); my = cy - R - 250 + 900 * u
    sk_ell(cr, mx, my, 150, 110, 5, sid=37240, fill=(0.62, 0.56, 0.50))
    for (dx, dy, r) in ((-40, -20, 30), (50, 30, 22)):
        cr.arc(mx + dx, my + dy, r, 0, 2 * math.pi); cr.set_source_rgb(0.50, 0.45, 0.40); cr.fill()

# ---- world dispatcher
def world(cr, t):
    if t < CUT_BASE - FR:
        E33.draw_mars(cr, t); return
    if t < CUT_OV - FR:
        draw_base(cr, t); return
    if t < CUT_PLANET - FR:
        draw_overhead(cr, t); return
    if t < CUT_END - FR:
        draw_planet(cr, t); return
    draw_base(cr, t)

# ================================================================ the rover
ROV_X = HB - 720
def rover_x(t):
    u = ramp(t, T_ROV0, T_ROV1)
    return lerp(HB - 1900, ROV_X, 1 - (1 - u) ** 2)

def draw_rover(cr, x, t, moving=False, arm=0.0, tag=False, dusty=0.0):
    yb = FLOOR_Y; s = 1.6
    roll = x / 40.0
    bob = 3 * math.sin(t * 20) if moving else 0.0
    cr.save(); cr.translate(x, yb); cr.scale(-s, s)                 # mirrored: it faces right (towards him)
    for k, wx in enumerate((-160, 0, 160)):
        sketch_line(cr, [(wx, -48), (0, -120 + bob)], 9, sid=35000 + k, amp=0.2, color=(0.30, 0.30, 0.34))
    for k, wx in enumerate((-160, 0, 160)):
        sk_circ(cr, wx, -45, 45, 5, sid=35010 + k, fill=(0.30, 0.30, 0.34))
        for j in range(3):
            a = roll + j * 2.09
            sketch_line(cr, [(wx, -45), (wx + 34 * math.cos(a), -45 + 34 * math.sin(a))], 4, sid=35020 + j, color=(0.6, 0.6, 0.65))
    body = (lerp(0.93, 0.80, dusty), lerp(0.92, 0.58, dusty), lerp(0.88, 0.45, dusty))
    sk_rect(cr, -190, -230 + bob, 190, -120 + bob, 6, sid=35030, fill=body)
    sk_rect(cr, -150, -260 + bob, 120, -230 + bob, 5, sid=35031, fill=(0.85, 0.66, 0.25))
    sk_rect(cr, 120, -320 + bob, 200, -230 + bob, 5, sid=35032, fill=(0.80, 0.80, 0.84))
    sketch_line(cr, [(-110, -230 + bob), (-110, -520 + bob)], 12, sid=35040, amp=0.2)
    hx, hy = -110, -560 + bob
    sk_rect(cr, hx - 75, hy - 45, hx + 75, hy + 45, 5, sid=35041, fill=body)
    for k, dy in enumerate((-14, 18)):
        ex = hx - 75
        sk_circ(cr, ex + 8, hy + dy, 17, 4, sid=35042 + k, fill=(0.15, 0.15, 0.20))
        cr.arc(ex + 4, hy + dy - 5, 5, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.8); cr.fill()
    sh = (-190, -175 + bob)
    el = (lerp(-260, -250, arm), lerp(-150, -420, arm) + bob)
    hd = (lerp(-300, -200, arm), lerp(-110, -560, arm) + bob)
    sketch_line(cr, [sh, el, hd], 9, sid=35050, amp=0.2, color=(0.30, 0.30, 0.34))
    sk_rect(cr, hd[0] - 34, hd[1] - 26, hd[0] + 34, hd[1] + 26, 4, sid=35051, fill=(0.93, 0.92, 0.88))
    cr.restore()
    if tag and arm > 0.05:
        wx, wy = x - s * hd[0], yb + s * (hd[1] - 70)
        name_tag(cr, wx, wy, 0.8 * min(1.0, arm * 1.5), ang=0.08, text="", sid=36050)

def draw_rovers(cr, t):
    if t < CUT_BASE - FR:
        E33.draw_rover(cr, 60.0)                   # still parked at the landing site
        return
    if t >= T_ROV0 and t >= CUT_LAST - FR:
        x = rover_x(t)
        arm = smooth(ramp(t, T_TAGUP0, T_TAGUP1)) * (1 - smooth(ramp(t, T_ASK + 1.0, T_ASK + 1.6)))
        draw_rover(cr, x, t, moving=t < T_ROV1, arm=arm, tag=True, dusty=0.7)
        if T_BEEP <= t < T_BEEP + 0.6:
            for k in range(3):
                q = ramp(t, T_BEEP + 0.1 * k, T_BEEP + 0.1 * k + 0.4)
                if 0 < q < 1:
                    cr.arc(x - 1.6 * -110 + 60 * k, FLOOR_Y - 1.6 * 560 - 60 - 80 * q, 12, 0, 2 * math.pi)
                    cr.set_source_rgba(*INKC, 1 - q); cr.fill()

def draw_dust_trail(cr, t):
    if T_ROV0 <= t < T_ROV1 + 0.6:
        x = rover_x(t)
        for k in range(4):
            q = ((t * 2 + k / 4) % 1.0)
            O.draw_smoke_puff(cr, x - 300 - 200 * q, FLOOR_Y - 40 - 60 * q, 60 + 60 * q, alpha=0.5 * (1 - q), dark=0.3)

# ================================================================ poses
def P_(name, **kw): L.POSES[name] = kw
P_("tag_write", lelb=(470, 900), lhand=(560, 860), relb=(650, 930), rhand=(600, 880), lhand_t="grip", rhand_t="grip")
P_("tag_show", lelb=(450, 880), lhand=(510, 800), relb=(630, 880), rhand=(570, 800), lhand_t="grip", rhand_t="grip")
P_("reach_up", relb=(700, 780), rhand=(800, 640), rhand_t="flat", lelb=(460, 920), lhand=(440, 1020))
P_("sign_up", lelb=(420, 600), lhand=(450, 430), relb=(660, 600), rhand=(630, 430), lhand_t="grip", rhand_t="grip")
P_("sign_low", lelb=(440, 940), lhand=(470, 1040), relb=(640, 940), rhand=(610, 1040), lhand_t="grip", rhand_t="grip")
P_("duck", lknee=(470, 1240), lfoot=(470, 1360), rknee=(620, 1240), rfoot=(610, 1360), hip=(540, 1180), neck=(540, 980),
   head=(540, 860), lelb=(420, 900), lhand=(470, 770), relb=(660, 900), rhand=(610, 770), lhand_t="grip", rhand_t="grip", nowalk=1.0)
P_("pull_plant", lelb=(500, 1040), lhand=(560, 1120), relb=(600, 1040), rhand=(580, 1120), lhand_t="fist", rhand_t="fist", lean=0.15)
P_("potato_up", lelb=(440, 900), lhand=(410, 820), relb=(680, 760), rhand=(720, 620), lhand_t="grip", rhand_t="grip")
P_("hand_look", lelb=(440, 900), lhand=(410, 820), relb=(680, 860), rhand=(740, 800), lhand_t="grip", rhand_t="open")
P_("rod", lknee=(620, 1235), lfoot=(600, 1360), rknee=(630, 1225), rfoot=(612, 1350),
   lelb=(600, 1000), lhand=(640, 1060), relb=(660, 980), rhand=(700, 1000), lhand_t="fist", rhand_t="fist", nowalk=1.0)
P_("hold_sign_l", lelb=(440, 880), lhand=(430, 760), relb=(640, 940), rhand=(610, 1040), lhand_t="grip", rhand_t="flat")

# ================================================================ scene (him)
S = M.Scene(start_body="stand", start_face="deadpan", x0=HF - 540)
S.auto_blinks = True
S.floor = False
S.card("cr1ms0n_h0rnet", "Name the dinosaur Jerry", "0", t0=0.3)
CAM_A = cam(MRS + 1000, 0.48, fs=1660)
S.camkeys[0] = (0.0, CAM_A, 0); S.cam = CAM_A

# ---------------------------------------------------------------- A: the landing site
S.read_card(T_READ, react="deadpan", lines=1)
S.set(T_LOOKREX, "stand", "deadpan", dur=0.35, turn=0.5, look=(1.0, -0.5))
S.set(T_TILT + 0.3, "stand", "dead_stare", dur=0.3, turn=0.5, look=(1.0, -0.6), lid=0.3)
S.sfx(T_RUMBLE, "wind", 0.10, dur=3.0); S.shake(T_RUMBLE, 1.0, 6)
S.set(T_LOOKL, "stand", "dead_stare", dur=0.25, turn=-0.6, look=(-1.0, -0.2), lid=0.0)
S.set(T_LOOKL + 0.35, "stand", "dead_stare", dur=0.12, ease="snap", turn=-0.6, look=(-1.0, -0.2), eyescale=1.25, lid=0.0)
S.camera(T_RUMBLE, *cam(MRS + 700, 0.42, fs=1680), 1.0)

# the ride
S.cut(CUT_RIDE - FR, cam=cam(REX_M, 0.42, fs=1680), x=HF - 540)
S.set(CUT_RIDE - FR, "ride", "deadpan", dur=0.0, turn=0.9, look=(1.0, 0.0), eyescale=1.1)
S.sfx(T_BOLT, E32.ROAR_WAV, 0.10); S.sfx(T_BOLT + 0.1, "whoosh", 0.08)
S.set(T_BOLT + 0.05, "ride", "deadpan", dur=0.12, ease="snap", turn=0.9, look=(1.0, 0.0), lean=-0.2, curl_up=1.0)
S.set(T_BOLT + 0.5, "ride", "dead_stare", dur=0.3, turn=0.9, look=(1.0, 0.0), lean=-0.05)
S.set(T_BOLT + 1.1, "ride", "dead_stare", dur=0.2, turn=0.2, look=(-1.0, 0.0), lean=-0.05)
for k in range(5): S.sfx(T_BOLT + 0.2 + 0.3 * k, "thud", 0.07)

# ---------------------------------------------------------------- B: Mars Base 1
S.cut(CUT_BASE - FR, cam=cam(DW + 900, 0.40, fs=1700), x=HF - 540)
S.set(CUT_BASE - FR, "ride", "deadpan", dur=0.0, turn=0.9, look=(1.0, 0.0), lean=-0.05)
S.sfx(CUT_BASE + 0.1, "skid", 0.12, dur=0.7)
S.set(CUT_BASE + 0.4, "ride", "dead_stare", dur=0.15, turn=0.9, look=(1.0, 0.0), lean=0.25)
S.set(T_SKID, "ride", "dead_stare", dur=0.3, turn=0.6, look=(0.9, -0.3), lid=0.3)

# standing next to it: the name tag
CAM_ST = cam(HB + 330, 0.56, fs=1650)
S.cut(CUT_STAND - FR, cam=CAM_ST, x=HB - 540)
S.set(CUT_STAND - FR, "stand", "deadpan", dur=0.0, turn=0.5, look=(1.0, -0.5))
S.pocket_pull(T_TAG, "tag", lambda cr, x, y, s, t, p: tag_held(cr, t, p), (0, 0), held=True)
S.set(POP_TAG + 0.1, "stand", "deadpan", dur=0.3, look=(0.3, 0.6))
S.set(T_W0 - 0.25, "tag_write", "deadpan", dur=0.25, look=(0.2, 1.0), lid=0.45, tilt=0.06)
S.sfx(T_W0, "scribble", 0.07, dur=T_W1 - T_W0)
S.set(T_SHOW, "tag_show", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lid=0.3)
S.walk_to(T_STEP, HB + 120 - 540, dur=0.45)
S.set(T_STEP + 0.4, "reach_up", "deadpan", dur=0.3, turn=0.6, look=(1.0, -0.4))
S.sfx(T_SLAP, "tok", 0.08)
S.set(T_SLAP + 0.3, "stand", "dead_stare", dur=0.35, turn=0.5, look=(1.0, -0.6), lid=0.3)
for k in range(5): S.sfx(T_ARMS0 + 0.22 * k, "squeak", 0.025)
S.set(T_ARMS0 + 0.5, "stand", "dead_stare", dur=0.3, turn=0.5, look=(1.0, -0.3), lid=0.35)

# JERRY! sign
S.cut(CUT_SIGN - FR, cam=cam(HB + 330, 0.54, fs=1650), x=HB - 540)
S.set(CUT_SIGN - FR, "sign_up", "dead_stare", dur=0.0, turn=0.4, look=(1.0, -0.7), lid=0.3)
S.set(T_SHAKE - 0.1, "sign_up", "dead_stare", dur=0.1, turn=0.4, look=(1.0, -0.7), lid=0.3)
S.sfx(T_SHAKE, "rummage", 0.06, dur=0.4)
S.sfx(T_YAWN, "wah", 0.03)
S.set(T_YAWN + 0.4, "sign_up", "dead_stare", dur=0.3, turn=0.2, look=(0.2, 0.0), lid=0.4)
# JERRY!!! - it turns away, the tail
S.cut(CUT_SIGN2 - FR, cam=cam(HB + 150, 0.50, fs=1650), x=HB - 540)
S.set(CUT_SIGN2 - FR, "sign_up", "dead_stare", dur=0.0, turn=0.5, look=(1.0, -0.6), lid=0.2)
S.sfx(CUT_SIGN2, "flip", 0.06)
S.set(T_DUCK, "duck", "dead_stare", dur=0.12, ease="snap", turn=0.5, look=(1.0, -0.8), eyescale=1.2, lid=0.0)
S.sfx(T_TAIL, "whoosh", 0.12, dur=0.5)
S.set(T_UP2, "sign_low", "dead_stare", dur=0.35, turn=0.0, look=(0.0, 0.0), lid=0.35)
S.set(T_SLIDE, "sign_low", "dead_stare", dur=0.35, turn=0.0, look=(-1.0, 0.1), lid=0.3)
S.set(T_IDEA, "sign_low", "dead_stare", dur=0.1, ease="snap", turn=-0.3, look=(-1.0, 0.1), lid=0.0, curl_up=1.0, eyescale=1.1)
S.sfx(T_IDEA, "ding", 0.04)

# the greenhouse
S.cut(CUT_GH - FR, cam=cam(GH, 0.62, fs=1640), x=GH + 120 - 540)
S.set(CUT_GH - FR, "stand", "deadpan", dur=0.0, turn=-0.3, look=(-0.4, 0.8))
S.set(T_GRAB - 0.1, "pull_plant", "deadpan", dur=0.2, turn=-0.2, look=(0.0, 1.0), lid=0.3)
S.set(T_YANK, "potato_up", "deadpan", dur=0.12, ease="snap", turn=0.0, look=(0.6, -0.8), lean=-0.15)
S.sfx(T_YANK, "pop", 0.12); S.sfx(T_YANK + 0.05, "spring", 0.03)
S.set(T_YANK + 0.4, "potato_up", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lid=0.3)

# the feeding
CAM_F = cam(HB + 320, 0.54, fs=1650)
S.cut(CUT_FEED - FR, cam=CAM_F, x=HB - 540)
S.set(CUT_FEED - FR, "potato_up", "dead_stare", dur=0.0, turn=0.5, look=(1.0, -0.5), lid=0.3)
S.sfx(T_WHIP, "whoosh", 0.06, dur=0.2)
S.set(T_WHIP + 0.25, "potato_up", "dead_stare", dur=0.12, ease="snap", turn=0.5, look=(1.0, -0.6), lid=0.0, eyescale=1.15)
S.sfx(T_STOMP0 + 0.05, "thud", 0.15); S.sfx(T_STOMP0 + 0.35, "thud", 0.15); S.shake(T_STOMP0 + 0.05, 0.6, 8)
S.camera(T_STOMP0, *cam(HB + 260, 0.58, fs=1650), 0.8)
S.sfx(T_CHOMP, "chomp", 0.14)
S.set(T_CHOMP + 0.02, "hand_look", "dead_stare", dur=0.1, ease="snap", turn=0.5, look=(1.0, -0.5), lid=0.0, eyescale=1.2)
S.set(T_EMPTY, "hand_look", "dead_stare", dur=0.35, turn=0.6, look=(1.0, -0.3), lid=0.4)
for k in range(4): S.sfx(T_CHOMP + 0.3 + 0.18 * k, "chomp", 0.03)
S.set(T_SIGN3 - 0.2, "hold_sign_l", "dead_stare", dur=0.25, turn=0.5, look=(1.0, -0.6), lid=0.35)
S.sfx(T_AWAY, "whoosh", 0.03, dur=0.2)
S.set(T_US, "hold_sign_l", "dead_stare", dur=0.35, turn=0.0, look=(0.0, 0.0), lid=0.4)

# potato on a stick
S.cut(CUT_ROD - FR, cam=cam(REX_B - 80, 0.42, fs=1690), x=HB - 540)
S.set(CUT_ROD - FR, "rod", "deadpan", dur=0.0, turn=0.9, look=(1.0, 0.0), lid=0.35)
S.sfx(T_LUNGE, E32.ROAR_WAV, 0.07); S.sfx(T_LUNGE + 0.05, "whoosh", 0.08)
S.set(T_LUNGE + 0.05, "rod", "deadpan", dur=0.12, ease="snap", turn=0.9, look=(1.0, 0.0), lean=-0.2, curl_up=1.0)
for k in range(3): S.sfx(T_LUNGE + 0.15 + 0.25 * k, "thud", 0.07)

# overhead + planet (he is drawn tiny on the rex's back)
S.cut(CUT_OV - FR, cam=(OV + 40, FLOOR_Y - 60, 0.34), x=HB - 540)
S.set(CUT_OV - FR, "stand", "deadpan", dur=0.0, show=0.0, nowalk=1.0)
S.camera(CUT_OV + 0.2, OV + 40, FLOOR_Y - 60, 0.30, 5 * LET_DUR)
for i in range(5):
    for k in range(int(LET_DUR / 0.16)):
        S.sfx(CUT_OV + i * LET_DUR + 0.15 + 0.16 * k, "thud", 0.035 + 0.01 * i)
S.cut(CUT_PLANET - FR, cam=(PL, FLOOR_Y + 200, 0.17), x=HB - 540)
S.camera(CUT_PLANET, PL, FLOOR_Y + 200, 0.14, 2.0)
S.sfx(CUT_PLANET + 0.05, "twinkle", 0.05)

# back on the ground
S.cut(CUT_END - FR, cam=cam(REX_B - 400, 0.44, fs=1680), x=HB - 540)
S.set(CUT_END - FR, "rod", "dead_stare", dur=0.0, turn=0.9, look=(1.0, 0.0), lid=0.5, lean=-0.05)
S.sfx(CUT_END + 0.05, "skid", 0.10, dur=0.6)
S.set(CUT_END + 0.15, "rod", "dead_stare", dur=0.15, turn=0.9, look=(1.0, 0.0), lean=0.25, lid=0.5)
S.set(T_SKID2, "rod", "dead_stare", dur=0.3, turn=0.9, look=(1.0, 0.2), lid=0.55)
S.sfx(T_CHOMP2, "chomp", 0.12)
S.set(T_CHOMP2 + 0.3, "rod", "dead_stare", dur=0.3, turn=0.9, look=(1.0, -0.2), lid=0.4)

# JERRY? - it answers
CAM_L = cam(HB + 280, 0.56, fs=1650)
S.cut(CUT_LAST - FR, cam=CAM_L, x=HB - 540)
S.set(CUT_LAST - FR, "sign_up", "dead_stare", dur=0.0, turn=0.5, look=(1.0, -0.6), lid=0.3)
for k in range(3): S.sfx(T_HEART0 + 0.3 * k, "thud", 0.07); S.sfx(T_HEART0 + 0.3 * k + 0.12, "thud", 0.04)
S.camera(T_HEART0, *cam(HB + 260, 0.62, fs=1640), 0.9)
S.set(T_TURN + 0.2, "sign_low", "dead_stare", dur=0.4, turn=0.5, look=(1.0, -0.7), lid=0.1, eyescale=1.1)
S.sfx(T_NUZ, "pat", 0.08)
S.set(T_NUZ + 0.05, "sign_low", "dead_stare", dur=0.12, ease="snap", turn=0.5, look=(1.0, -0.8), lean=-0.12, lid=0.2)
S.set(T_SMILE, "sign_low", "deadpan", dur=0.6, turn=0.4, look=(0.6, -0.6), lid=0.25, smile=0.45, lean=0.0)
S.camera(T_SMILE + 0.8, *cam(HB - 60, 0.54, fs=1650), 1.2)
# the rover
S.sfx(T_ROV0, "whine", 0.02, dur=0.9)
S.set(T_ROV0 + 0.4, "sign_low", "deadpan", dur=0.3, turn=-0.4, look=(-1.0, 0.2), lid=0.3, smile=0.2)
S.sfx(T_BEEP, "boop", 0.04); S.sfx(T_BEEP + 0.15, "boop", 0.04)
S.sfx(T_TAGUP0, "whine", 0.02, dur=0.4)
S.set(T_LOOKROV, "sign_low", "dead_stare", dur=0.3, turn=-0.5, look=(-1.0, -0.3), lid=0.35)
S.set(T_LOOKUS, "sign_low", "dead_stare", dur=0.35, turn=0.0, look=(0.0, 0.0), lid=0.4)

# ---------------------------------------------------------------- the ask (Mars Base 1)
S.x = HB - 540
S.set(T_ASK - 0.35, "stand", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lid=0.4)
S.camera(T_ASK - 0.4, *cam(HB + 80, 0.56, fs=1650), 1.0)
S.the_ask(T_ASK, hold=HOLD, push=False)
S.camera(T_ASK + 6.9, *cam(HB + 80, 0.60, fs=1650), 5.0)
T_END = S.t
S.blink(5.0, 9.0, 13.9, 21.9, 33.0, 37.0, 42.0)

# camera follow during the rides
_ck = []
t_ = T_BOLT
while t_ < CUT_BASE - FR:
    X, lift, pitch, face, st = rex(t_)
    _ck.append((t_, cam(X + 350, 0.42, fs=1680), 0.1, "linear")); t_ += 0.1
t_ = CUT_BASE
while t_ < T_SKID + 0.05:
    X, lift, pitch, face, st = rex(t_)
    _ck.append((t_, cam(max(X + 700, DW + 900), 0.40, fs=1700), 0.1, "linear")); t_ += 0.1
t_ = T_LUNGE
while t_ < CUT_OV - FR:
    X, lift, pitch, face, st = rex(t_)
    _ck.append((t_, cam(X + 200, 0.42, fs=1690), 0.1, "linear")); t_ += 0.1
S.camkeys += _ck
S.camkeys.sort(key=lambda k: k[0])

# ---------------------------------------------------------------- hooks
RIDING = ((CUT_RIDE - FR, CUT_STAND - FR), (CUT_ROD - FR, CUT_OV - FR), (CUT_END - FR, CUT_LAST - FR))
def riding(t): return any(a <= t < b for a, b in RIDING)

def ride_hook(t, p):
    if riding(t):
        sx, sy = seat(t)
        hx, hy = p["hip"]
        dx, dy = sx - hx, sy - 30 - hy
        for k in L.JOINTS:
            p[k] = (p[k][0] + dx, p[k][1] + dy)
    # writing on the tag (the pen jitters)
    if CUT_STAND - FR <= t < T_SHOW and T_W0 <= t < T_W1:
        k = 1.0
        p["rhand"] = (p["rhand"][0] + 26 * math.sin(t * 19) + 12 * math.sin(t * 7.3), p["rhand"][1] + 6 * math.sin(t * 29))
        p["rhand_t"] = "fist"
    # the slap lands on its belly
    if T_STEP + 0.4 <= t < T_SLAP + 0.25:
        X, lift, pitch, face, st = rex(t)
        tx, ty = rex_world(X, lift, pitch, face, *TAG_LH)
        k = smooth(ramp(t, T_STEP + 0.4, T_SLAP))
        p["rhand"] = lerp(p["rhand"], (tx, ty), k)
        p["relb"] = lerp(p["relb"], ((p["neck"][0] + tx) / 2 + 20, (p["neck"][1] + ty) / 2 + 60), k)
    # the nuzzle pushes him back a little
    if CUT_LAST - FR <= t < T_ASK and t >= T_NUZ:
        bump = 18 * pulse(t, T_NUZ + 0.08, 0.15)
        for k in L.JOINTS:
            if k in ("head", "neck", "lelb", "relb", "lhand", "rhand"):
                p[k] = (p[k][0] - bump, p[k][1])
    return p
S.hook(ride_hook)

# ---------------------------------------------------------------- held things
def tag_held(cr, t, p):
    if t >= T_SLAP: return
    if t < T_SHOW and t >= T_W0 - 0.25:
        x, y = p["lhand"][0] + 40, p["lhand"][1] - 30
        rev = ramp(t, T_W0, T_W1, "linear")
        name_tag(cr, x, y, 0.85, ang=0.05, reveal=rev, sid=36000)
        if T_W0 - 0.1 <= t < T_W1 + 0.1:
            hx, hy = p["rhand"]; L.draw_pen(cr, hx, hy - 18, ang=0.3)
        return
    if t >= T_SHOW and t < T_STEP + 0.4:
        x, y = (p["lhand"][0] + p["rhand"][0]) / 2, (p["lhand"][1] + p["rhand"][1]) / 2 - 60
        name_tag(cr, x, y, 0.95, sid=36000)
        return
    if t >= T_STEP + 0.4:
        x, y = p["rhand"]
        name_tag(cr, x, y, 0.85, ang=-0.12, sid=36000)
        return
    x, y = p["rhand"]
    name_tag(cr, x, y - 70, 0.85, text="", sid=36000)

def sign_text(t):
    if CUT_SIGN - FR <= t < CUT_SIGN2 - FR: return "JERRY!"
    if CUT_SIGN2 - FR <= t < CUT_GH - FR: return "JERRY!!!"
    if CUT_FEED - FR <= t < CUT_ROD - FR: return "JERRY"
    if CUT_LAST - FR <= t < T_ASK - 0.3: return "JERRY?"
    return None

def draw_sign_held(cr, t, p):
    txt = sign_text(t)
    if not txt: return
    if CUT_FEED - FR <= t < CUT_ROD - FR:
        if t < T_SIGN3 - 0.2:
            x, y = p["lhand"][0] - 20, p["lhand"][1] - 60
            placard(cr, x, y, txt, s=0.7)
        else:
            x, y = p["lhand"][0] + 20, p["lhand"][1] - 70
            placard(cr, x, y, txt, s=0.8)
        return
    sh = 0.0
    if CUT_SIGN - FR <= t < CUT_SIGN2 and T_SHAKE <= t < T_SHAKE + 0.4: sh = 18 * math.sin(t * 60)
    x = (p["lhand"][0] + p["rhand"][0]) / 2 + sh
    y = (p["lhand"][1] + p["rhand"][1]) / 2 - 75
    placard(cr, x, y, txt, s=1.0 if txt != "JERRY!!!" else 1.15)
    L.draw_grips(cr, p)

def draw_potato_held(cr, t, p):
    if CUT_GH - FR <= t < CUT_FEED - FR and t >= T_YANK:
        x, y = p["rhand"]
        potato(cr, x + 10, y - 90, 95, ang=0.15, roots=True, sid=36100)
        if t < T_YANK + 0.35:
            L.burst_lines(cr, x, y - 70, (t - T_YANK) / 0.4, r0=90, r1=170, n=10, sid=9)
            for k in range(6):
                q = ramp(t, T_YANK, T_YANK + 0.35)
                cr.arc(x - 80 + 32 * k, y + 60 - 140 * q + 200 * q * q, 12, 0, 2 * math.pi); cr.set_source_rgb(0.45, 0.30, 0.20); cr.fill()
    if CUT_FEED - FR <= t < T_CHOMP:
        x, y = p["rhand"]
        potato(cr, x + 10, y - 90, 95, ang=0.15, roots=False, sid=36100)

def draw_my_helmet(cr, t, p):
    if CUT_OV - FR <= t < CUT_END - FR: return
    if p.get("show", 1.0) < 0.5: return
    hx, hy = p["head"]
    helmet(cr, hx + 6, hy - 10, 175, sid=33000)

def draw_chomp_fx(cr, t):
    for tc, at in ((T_CHOMP, "feed"), (T_CHOMP2, "end")):
        if tc <= t < tc + 0.3:
            if at == "feed" and not (CUT_FEED - FR <= t < CUT_ROD): continue
            if at == "end" and not (CUT_END - FR <= t < CUT_LAST): continue
            X, lift, pitch, face, st = rex(t)
            m = O.trex_pt(X, st, face, pitch, "mouth")
            L.burst_lines(cr, m[0], m[1] - lift, (t - tc) / 0.3, r0=80, r1=170, n=8, sid=12)

# ---------------------------------------------------------------- draw order
def props_back(cr, t, p, ly):
    if ly != "back": return
    if t < CUT_BASE - FR:
        E33.draw_prints(cr, 60.0)
        E33.draw_mars_rocket(cr, 60.0)
        draw_rex(cr, t)
        draw_rovers(cr, t)
        return
    if CUT_OV - FR <= t < CUT_END - FR: return
    if CUT_GH - FR <= t < CUT_FEED - FR: return
    draw_rex(cr, t)
    draw_dust_trail(cr, t)
    draw_rovers(cr, t)
S.prop(props_back)
S.background(world)

def props_front(cr, t, p, ly):
    if ly != "front": return
    if t < CUT_BASE - FR and t >= T_RUMBLE:
        draw_storm(cr, storm_x(t), t)
    if CUT_BASE - FR <= t < CUT_STAND:
        draw_storm(cr, DW, t, sid=36420)
    draw_my_helmet(cr, t, p)
    draw_stick(cr, t, p)
    draw_sign_held(cr, t, p)
    draw_potato_held(cr, t, p)
    draw_chomp_fx(cr, t)
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
        S.render("day034.mp4")
