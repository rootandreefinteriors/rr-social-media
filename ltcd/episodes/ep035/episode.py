"""Day 35: TikTok @irdlubuhsmmp: "Smile". See BEATS.md.
At Mars Base 1 he can't smile. The rover points right; he rides Jerry through a dust devil into CYDONIA: the Face on Mars, a giant
stone face as flat as his. Fingers (tok - the helmet), a mirror (it cracks), Jerry's feather, the rover's dance (it tips over): nothing.
He jackhammers a giant grin into the face. It opens its eyes and LAUGHS: the ground bounces, he's launched, lands, and smiles for real.
The orbiter's flash: the photo (frame 35A72) caught him flat. The ask at Cydonia.
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

_spec = importlib.util.spec_from_file_location("ep034_episode", os.path.join(HERE, "..", "ep034", "episode.py"))
E34 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(E34)
E33 = E34.E33
E32 = E34.E32

FR = 1 / 30
sk_rect, sk_poly, sk_circ, sk_ell = O.sketch_rect, O.sketch_poly, O.sketch_circle, O.sketch_ellipse
INKC = (0.07, 0.07, 0.09)
RS = E33.RS
cam = E33.cam
rex_world = E33.rex_world
helmet = E33.helmet

# ================================================================ places
BASE = E34.BASE
HB = E34.HB                       # him at Mars Base 1 (day 34 ask)
REX_B = E34.REX_B
ROV_B = E34.ROV_X
DD = BASE + 4700.0                # the dust devil (border)
CY = 13600000.0                   # CYDONIA: the face's centre line
HFX = CY - 650.0                  # him at the face
REX_C = CY - 1450.0               # Jerry at the face (near foot), facing right
DXR = HFX - 560.0                 # the rover's dance spot

# ================================================================ timeline
T_READ = 0.3
T_TRY0, T_TRY1 = 1.85, 2.6
T_ROV = 2.75; T_LOOKR = 3.15
CUT_RIDE = 3.6; T_BOLT = 3.75
CUT_CY = 5.6; T_STOPC = 6.4
CUT_FACE = 7.4
CUT_TOK = 8.9; T_TOK = 9.35
T_MIR = 10.6; POP_MIR = T_MIR + 2.1
T_MLOOK = 12.95; T_CRACK = 14.0; T_MDROP = 14.8; T_MLAND = 15.05
CUT_FEATH = 15.3; T_TK0, T_TK1 = 15.85, 17.4; T_FDROP = 17.95
CUT_ROVER = 18.4; T_DANCE = 18.9; T_WHEELIE = 20.2; T_TIP = 20.6; T_TIPPED = 20.9
T_UP = 21.6; T_IDEA = 21.95
T_JH = 22.2; POP_JH = T_JH + 2.1
CUT_CARVE = 24.9; T_C0 = 25.1
CUT_WIDE = 26.7; T_C1 = 29.0
T_CLEAR = 29.9; T_DROP = 30.1
CUT_COPY = 31.3; T_STRAIN0, T_STRAIN1 = 31.4, 33.6
T_RUMBLE = 33.6
CUT_EYES = 34.1; T_EYES0, T_EYES1 = 34.3, 34.8
T_LAUGH = 35.5; HA = 0.36
T_LAUNCH = T_LAUGH + 0.05; T_LAND = T_LAUNCH + 1.4
CUT_SMILE = 37.4; T_TWITCH = 38.0; T_SMILE = 38.3; T_HISLAUGH = 39.0
CUT_SNAPW = 40.45; T_SNAP = 40.75
CUT_PHOTO = 40.8
CUT_AFTER = 42.9; T_LOOKUS = 43.2
CUT_STANDUP = 43.6
T_ASK = 44.0; HOLD = 10.2
T_LAUGH_END = T_SNAP

def laughing(t): return T_LAUGH <= t < T_LAUGH_END
def ha_phase(t): return ((t - T_LAUGH) % HA) / HA
def ha_hop(t, amp=1.0):
    if not laughing(t): return 0.0
    return amp * math.sin(math.pi * min(1.0, ha_phase(t) / 0.55)) if ha_phase(t) < 0.55 else 0.0

# ================================================================ sounds made for this episode
SR = 44100
def _write_wav(path, a):
    import wave
    a = np.clip(a, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((a * 32767).astype(np.int16).tobytes())

LAUGH_WAV = os.path.join(HERE, "face_laugh.wav")
JACK_WAV = os.path.join(HERE, "jackhammer.wav")
def make_laugh():
    """a deep, booming stone 'HA HA HA' (voiced low buzz through a vowel-ish resonance, one per HA)."""
    n = int((T_LAUGH_END - T_LAUGH) / HA) + 1
    out = np.zeros(int((T_LAUGH_END - T_LAUGH + 0.6) * SR), np.float32)
    rng = np.random.default_rng(5)
    for k in range(n):
        d = 0.24; tt = np.arange(int(d * SR)) / SR
        f0 = 92 - 14 * tt / d + (3 if k % 2 else 0)
        ph = np.cumsum(f0) / SR * 2 * np.pi
        v = sum(np.sin(h * ph) * (1.0 / h) * (1.6 if 5 <= h <= 9 else 1.0) for h in range(1, 16))
        br = rng.standard_normal(len(tt)) * 0.15
        env = np.clip(tt / 0.02, 0, 1) * np.exp(-tt / 0.11)
        s = (v * 0.5 + br) * env
        i = int(k * HA * SR); m = min(len(s), len(out) - i)
        out[i:i + m] += s[:m]
    out /= np.abs(out).max() + 1e-9
    _write_wav(LAUGH_WAV, out * 0.9)

def make_jack():
    """jackhammer: a rattle of hits that speeds up (18 -> 34 hits/s) over the carve."""
    dur = T_C1 - T_C0 + 0.2
    out = np.zeros(int(dur * SR), np.float32)
    rng = np.random.default_rng(7)
    t = 0.0
    while t < dur - 0.05:
        u = t / dur
        rate = 18 if t < CUT_WIDE - T_C0 else 18 + 16 * ((t - (CUT_WIDE - T_C0)) / (T_C1 - CUT_WIDE)) ** 1.5
        hl = int(0.03 * SR); tt = np.arange(hl) / SR
        hit = (rng.standard_normal(hl) * 0.6 + np.sin(2 * np.pi * 140 * tt)) * np.exp(-tt / 0.008)
        i = int(t * SR); m = min(hl, len(out) - i); out[i:i + m] += hit[:m]
        t += 1.0 / rate
    out /= np.abs(out).max() + 1e-9
    _write_wav(JACK_WAV, out * 0.8)
if not os.path.exists(LAUGH_WAV): make_laugh()
if not os.path.exists(JACK_WAV): make_jack()

# ================================================================ the giant face (Cydonia)
FACE_C = (CY, FLOOR_Y - 950.0)
FRX, FRY = 1250.0, 1650.0
EYE_Y = FLOOR_Y - 1600.0
EYE_DX = 500.0
STONE = (0.72, 0.45, 0.32)
STONE_D = (0.55, 0.31, 0.21)
GL, GC1, GC2, GR = (CY - 640, FLOOR_Y - 720), (CY - 380, FLOOR_Y - 290), (CY + 380, FLOOR_Y - 290), (CY + 640, FLOOR_Y - 720)

def bez(u, a=GL, b=GC1, c=GC2, d=GR):
    v = 1 - u
    return (v ** 3 * a[0] + 3 * v * v * u * b[0] + 3 * v * u * u * c[0] + u ** 3 * d[0],
            v ** 3 * a[1] + 3 * v * v * u * b[1] + 3 * v * u * u * c[1] + u ** 3 * d[1])

def carve_u(t):
    if t < T_C0: return 0.0
    if t < CUT_WIDE: return 0.22 * ramp(t, T_C0, CUT_WIDE, "linear")
    return min(1.0, 0.22 + 0.78 * ramp(t, CUT_WIDE, T_C1, "linear") ** 1.7)

def face_eyes(t):
    """0 = stone sockets, 1 = open eyes."""
    if t < T_EYES0 or t >= CUT_AFTER - FR: return 0.0
    return smooth(ramp(t, T_EYES0, T_EYES1))

def face_jaw(t):
    if not laughing(t): return 0.0
    k = ramp(t, T_LAUGH, T_LAUGH + 0.15)
    return k * (0.55 + 0.45 * math.sin(math.pi * ha_phase(t)))

def draw_face(cr, t):
    cx, cy = FACE_C
    cr.save()
    cr.rectangle(cx - FRX - 900, cy - FRY - 900, 2 * FRX + 1800, FLOOR_Y + 25 - (cy - FRY - 900)); cr.clip()
    _draw_face(cr, t, cx, cy)
    cr.restore()
    rr = random.Random(36)
    for k in range(16):
        x = cx - FRX + k * (2 * FRX / 15) + rr.uniform(-40, 40)
        sk_poly(cr, [(x - 90, FLOOR_Y + 30), (x - 50, FLOOR_Y - 40), (x + 40, FLOOR_Y - 50), (x + 100, FLOOR_Y + 30)], 4,
                sid=35580 + k % 7, fill=(0.62, 0.36, 0.24))

def _draw_face(cr, t, cx, cy):
    # the head, buried to the chin
    cr.save()
    cr.rectangle(cx - FRX - 400, cy - FRY - 400, 2 * FRX + 800, FLOOR_Y + 40 - (cy - FRY - 400)); cr.clip()
    sk_ell(cr, cx, cy, FRX, FRY, 9, sid=35500, fill=STONE)
    # side shading (solid bands, no gradients)
    cr.save(); cr.translate(cx, cy); cr.scale(FRX, FRY); cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore(); cr.clip()
    cr.save(); cr.translate(cx + FRX * 0.55, cy); cr.scale(FRX * 0.7, FRY * 1.1); cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore()
    cr.set_source_rgba(*STONE_D, 0.0); cr.fill()
    cr.save(); cr.translate(cx + FRX * 1.25, cy); cr.scale(FRX * 0.75, FRY * 1.2); cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore()
    cr.set_source_rgba(*STONE_D, 0.40); cr.fill()
    rr = random.Random(35)
    for k in range(18):                                   # pocks
        a = rr.uniform(0, 2 * math.pi); d = rr.uniform(0.15, 0.92)
        x, y = cx + math.cos(a) * d * FRX, cy + math.sin(a) * d * FRY
        if abs(x - cx) < 700 and EYE_Y - 250 < y < FLOOR_Y - 250: continue
        r = rr.uniform(25, 70)
        sk_ell(cr, x, y, r, r * 0.7, 3, sid=35510 + k % 7, fill=STONE_D)
    for k in range(5):                                    # cracks
        x0, y0 = cx + rr.uniform(-1000, 1000), cy - FRY + rr.uniform(150, 600)
        pts = [(x0, y0)]
        for j in range(4): pts.append((pts[-1][0] + rr.uniform(-60, 60), pts[-1][1] + rr.uniform(50, 110)))
        sketch_line(cr, pts, 3, sid=35520 + k, alpha=0.5)
    cr.restore()
    sk_ell(cr, cx, cy, FRX, FRY, 9, sid=35500, fill=None)
    # brow ridge
    for d in (-1, 1):
        sketch_line(cr, [(cx + d * 160, EYE_Y - 230), (cx + d * 500, EYE_Y - 280), (cx + d * 820, EYE_Y - 200)], 12, sid=35530 + (d > 0), amp=0.4)
    # eyes
    ey = face_eyes(t)
    for d in (-1, 1):
        ex = cx + d * EYE_DX
        sk_ell(cr, ex, EYE_Y, 270, 150, 7, sid=35540 + (d > 0), fill=STONE_D)
        if ey > 0.01:
            cr.save(); cr.translate(ex, EYE_Y); cr.scale(250, 135); cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore()
            cr.set_source_rgb(0.97, 0.95, 0.90); cr.fill()
            look = eye_look(t)
            happy = laughing(t) and t >= T_LAUGH + 0.1
            if not happy:
                cr.arc(ex + 110 * look[0], EYE_Y + 60 * look[1], 70, 0, 2 * math.pi); cr.set_source_rgb(*INKC); cr.fill()
                cr.arc(ex + 110 * look[0] - 22, EYE_Y + 60 * look[1] - 22, 18, 0, 2 * math.pi); cr.set_source_rgb(1, 1, 1); cr.fill()
            # the stone lid rolls up
            lid = 1.0 - ey
            if happy: lid = 0.55
            cr.save(); cr.translate(ex, EYE_Y); cr.scale(250, 135); cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore(); cr.clip()
            cr.rectangle(ex - 300, EYE_Y - 160, 600, 300 * lid + 10); cr.set_source_rgb(*STONE_D); cr.fill()
            cr.reset_clip()
            if happy:                                             # laughing eyes: squeezed shut, happy arcs
                sk_ell(cr, ex, EYE_Y, 250, 135, 6, sid=35545 + (d > 0), fill=STONE_D)
                cr.move_to(ex - 170, EYE_Y + 50); cr.curve_to(ex - 90, EYE_Y - 80, ex + 90, EYE_Y - 80, ex + 170, EYE_Y + 50)
                cr.set_source_rgb(*INKC); cr.set_line_width(22); cr.set_line_cap(1); cr.stroke()
            sk_ell(cr, ex, EYE_Y, 250, 135, 6, sid=35545 + (d > 0), fill=None)
        else:
            sketch_line(cr, [(ex - 200, EYE_Y + 10), (ex, EYE_Y + 30), (ex + 200, EYE_Y + 10)], 7, sid=35548 + (d > 0), amp=0.3)
    # nose ridge
    sk_poly(cr, [(cx - 60, EYE_Y - 120), (cx - 150, FLOOR_Y - 930), (cx - 70, FLOOR_Y - 880), (cx + 70, FLOOR_Y - 880),
                 (cx + 150, FLOOR_Y - 930), (cx + 60, EYE_Y - 120)], 7, sid=35550, fill=STONE)
    cr.move_to(cx + 60, EYE_Y - 120); cr.line_to(cx + 150, FLOOR_Y - 930); cr.line_to(cx + 70, FLOOR_Y - 880)
    cr.close_path(); cr.set_source_rgba(*STONE_D, 0.5); cr.fill()
    for d in (-1, 1):
        sk_ell(cr, cx + d * 70, FLOOR_Y - 905, 30, 16, 3, sid=35555 + (d > 0), fill=STONE_D)
    # mouth: the flat slit, then the carved grin
    u = 1.0 if t >= T_C1 else carve_u(t)
    slit_a = 1.0 - ramp(u, 0.35, 0.9, "linear")
    if slit_a > 0.01:
        sketch_line(cr, [(cx - 560, FLOOR_Y - 560), (cx, FLOOR_Y - 552), (cx + 560, FLOOR_Y - 560)], 10, sid=35560, amp=0.3, alpha=slit_a)
    jaw = face_jaw(t)
    if jaw > 0.01:
        n = 24
        top = [bez(i / n) for i in range(n + 1)]
        lo = [(x, y + jaw * 380 * math.sin(math.pi * i / n) ** 0.8) for i, (x, y) in enumerate(top)]
        cr.move_to(*top[0])
        for q in top[1:]: cr.line_to(*q)
        for q in reversed(lo): cr.line_to(*q)
        cr.close_path(); cr.set_source_rgb(0.22, 0.09, 0.07); cr.fill_preserve()
        cr.set_source_rgb(*INKC); cr.set_line_width(9); cr.stroke()
        # stone teeth row
        cr.save(); cr.move_to(*top[0])
        for q in top[1:]: cr.line_to(*q)
        for q in reversed(lo): cr.line_to(*q)
        cr.close_path(); cr.clip()
        for i in range(1, n):
            x, y = top[i]
            cr.rectangle(x - 22, y - 4, 44, 56); cr.set_source_rgb(0.92, 0.88, 0.80); cr.fill()
        cr.restore()
    elif u > 0.0:
        n = max(2, int(40 * u))
        pts = [bez(u * i / n) for i in range(n + 1)]
        for w, c in ((64, (0.30, 0.13, 0.09)), (34, (0.18, 0.07, 0.05))):
            cr.move_to(*pts[0])
            for q in pts[1:]: cr.line_to(*q)
            cr.set_source_rgb(*c); cr.set_line_width(w); cr.set_line_cap(1); cr.set_line_join(1); cr.stroke()
        if u >= 0.999:                                    # cheek dimples at the corners
            for (x, y), d in ((GL, -1), (GR, 1)):
                sketch_line(cr, [(x + d * 10, y + 60), (x + d * 50, y - 30), (x + d * 20, y - 100)], 8, sid=35570 + (d > 0), amp=0.3)

def eye_look(t):
    """where the giant face's pupils look: down at him."""
    if t < T_EYES1: return (0.0, 0.2 + 0.6 * smooth(ramp(t, T_EYES0 + 0.2, T_EYES1)))
    hx = his_x(t)
    return (max(-1.0, min(1.0, (hx - CY) / 900.0)), 0.8)

def his_x(t):
    return L.loco(t)[0] + 540 if hasattr(L, "loco") else HFX

def draw_cy_sign(cr, t):
    x = CY + 1700
    for d in (-190, 190):
        sketch_line(cr, [(x + d, FLOOR_Y), (x + d, FLOOR_Y - 560)], 9, sid=35600 + (d > 0), amp=0.2, color=(0.5, 0.5, 0.55))
    sk_rect(cr, x - 290, FLOOR_Y - 860, x + 290, FLOOR_Y - 520, 6, sid=35602, fill=(0.95, 0.95, 0.93))
    draw_text(cr, "CYDONIA", x, FLOOR_Y - 760, 74)
    draw_text(cr, "THE FACE ON MARS", x, FLOOR_Y - 625, 44, color=(200, 40, 40))

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
    orbiter_sky(cr, t)
    draw_face(cr, t)
    sketch_line(cr, [(a, FLOOR_Y), (b, FLOOR_Y)], 6, sid=34770, amp=0.3)
    draw_cy_sign(cr, t)
    # bouncing pebbles while it laughs
    if t >= T_RUMBLE and t < T_LAUGH_END:
        amp = 30 if t < T_LAUGH else 110
        for k in range(14):
            x = CY - 2400 + k * 330
            if not (a < x < b): continue
            ph = ((t * (3.2 if t >= T_LAUGH else 9) + k * 0.37) % 1.0)
            y = FLOOR_Y + 20 - amp * math.sin(math.pi * ph)
            sk_poly(cr, [(x - 28, y), (x - 14, y - 26), (x + 16, y - 30), (x + 30, y)], 3, sid=35620 + k % 5, fill=(0.56, 0.30, 0.20))

# ---- the orbiter (a tiny satellite)
def orbiter(cr, x, y, s=1.0, sid=35650):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    for d in (-1, 1):
        sk_rect(cr, d * 70 - 55, -22, d * 70 + 55, 22, 3, sid=sid + (d > 0), fill=(0.25, 0.35, 0.65))
        for k in range(1, 4):
            sketch_line(cr, [(d * 70 - 55 + 27 * k, -22), (d * 70 - 55 + 27 * k, 22)], 2, sid=sid + 3 + k, color=(0.7, 0.8, 1.0))
    sk_rect(cr, -24, -30, 24, 30, 3, sid=sid + 8, fill=(0.85, 0.75, 0.45))
    sk_circ(cr, 0, 34, 12, 2, sid=sid + 9, fill=(0.2, 0.2, 0.25))
    cr.restore()

def orbiter_pos(t):
    cxx, cyy, z = L.cam_track.at(t)
    if CUT_CY - FR <= t < CUT_FACE - FR:
        u = ramp(t, CUT_CY, CUT_FACE + 0.6, "linear")
        return (cxx + (-640 + 1280 * u) / z, cyy - 480 / z), 0.9 / z
    if CUT_SNAPW - FR <= t < CUT_AFTER - FR:
        tt = min(t, T_SNAP)
        u = ramp(tt, CUT_SNAPW - 0.3, T_SNAP + 0.6, "linear")
        return (cxx + (-300 + 600 * u) / z, cyy - 470 / z), 0.9 / z
    return None, 0

def orbiter_sky(cr, t):
    pos, s = orbiter_pos(t)
    if pos: orbiter(cr, pos[0], pos[1], s)

# ---- the dust devil
def draw_dust_devil(cr, t, x):
    for k in range(16):
        y = FLOOR_Y - 140 * k
        r = 120 + 40 * k
        for j in (-1, 1):
            xx = x + j * r * 0.5 + 90 * math.sin(t * 5 + k * 1.3 + j) + 8 * k * math.sin(t * 1.3)
            O.draw_smoke_puff(cr, xx, y - 40 * j, r * 0.8, alpha=0.8, dark=0.15)
    for k in range(6):
        a = t * 9 + k
        sketch_line(cr, [(x - 300 + 120 * math.cos(a), FLOOR_Y - 400 - 250 * k), (x + 300 + 120 * math.cos(a + 1), FLOOR_Y - 360 - 250 * k)],
                    5, sid=35700 + k, color=(0.55, 0.30, 0.20), alpha=0.6)

# ================================================================ the rex (Jerry)
def rex(t):
    st = dict(O.DINO); st.update(s=RS, look=(-0.6, 0.6), smile=0.6, lid=0.0, mouth=0.0, arms=0.0, walk=0.0)
    X, lift, pitch, face = REX_B, 0.0, 0.0, -1
    if t < CUT_RIDE - FR:
        if t >= T_TRY0 + 0.3: st["look"] = (-0.9, 0.7); st["smile"] = 0.3; pitch = 0.05
        if t >= T_ROV + 0.2: st["look"] = (-1.0, 0.5); pitch = 0.0
        if t >= T_LOOKR + 0.1: st["look"] = (1.0, -0.1); st["smile"] = 0.5
        return X, lift, pitch, face, st
    if t < CUT_CY - FR:
        face = 1; st["look"] = (1.0, 0.0)
        u = max(0.0, t - T_BOLT)
        X = REX_B - 200 + 700 * u + 900 * u * u
        if t >= T_BOLT:
            st["walk"] = u * 16.0; pitch = 0.10 + 0.05 * math.sin(u * 16); lift = 40 * abs(math.sin(u * 8)); st["mouth"] = 0.2
        return X, lift, pitch, face, st
    face = 1
    if t < CUT_FACE - FR:
        u = ramp(t, CUT_CY, T_STOPC)
        X = lerp(REX_C - 1400, REX_C + 200, 1 - (1 - u) ** 2)
        st["walk"] = 0.0 if u > 0.55 else (t - CUT_CY) * 16
        pitch = 0.22 * math.sin(math.pi * u); st["look"] = (1.0, -0.2)
        if t >= T_STOPC: st["look"] = (0.8, -1.0); pitch = -0.08; st["pupil"] = 0.8
        return X, lift, pitch, face, st
    X = REX_C; st["look"] = (0.8, 0.5); st["smile"] = 0.5
    if CUT_FEATH - FR <= t < CUT_ROVER - FR:
        k = smooth(ramp(t, CUT_FEATH, T_TK0 - 0.1)) * (1 - smooth(ramp(t, T_TK1 + 0.1, T_TK1 + 0.5)))
        X = REX_C + 250 * k
        pitch = 0.25 * k
        st["look"] = (0.6, 0.9); st["smile"] = 0.8
        if T_TK0 <= t < T_TK1:
            pitch += 0.02 * math.sin((t - T_TK0) * 26); X += 14 * math.sin((t - T_TK0) * 13)
            st["arms"] = 0.5 + 0.5 * math.sin((t - T_TK0) * 24)
            st["eyes"] = "happy"
        if t >= T_TK1 + 0.1:
            st["look"] = (-0.2, 0.0); st["smile"] = 0.1; st["worry"] = 0.6; st["brow"] = 0.3
    elif CUT_ROVER - FR <= t < CUT_CARVE - FR:
        st["look"] = (-0.3, 1.0); st["smile"] = 0.7
        if t >= T_TIP: st["pupil"] = 0.6; st["worry"] = 0.5; st["smile"] = 0.0
        if t >= T_UP: st["look"] = (0.8, 0.4); st["worry"] = 0.0; st["smile"] = 0.4; st["pupil"] = 1.0
    elif t < CUT_COPY - FR:
        st["look"] = (1.0, 0.2); st["smile"] = 0.4
    elif t < CUT_AFTER - FR:
        st["look"] = (1.0, 0.4)
        if t >= T_RUMBLE + 0.2: st["look"] = (1.0, -0.8); st["pupil"] = 0.55; st["worry"] = 0.7; st["smile"] = 0.0
        if laughing(t):
            lift = 70 * ha_hop(t)
            if t >= T_LAUGH + 0.8:
                st["eyes"] = "happy"; st["mouth"] = 0.55 + 0.3 * math.sin(math.pi * ha_phase(t)); st["smile"] = 1.0
                st["worry"] = 0.0; st["pupil"] = 1.0; pitch = -0.06
    else:
        st["look"] = (0.9, 0.6); st["smile"] = 0.6; st["lid"] = 0.2
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
    if CUT_TOK - FR <= t < CUT_FEATH - FR: return False          # close on him
    if CUT_CARVE - FR <= t < CUT_WIDE - FR: return False
    if CUT_COPY - FR <= t < CUT_EYES - FR: return False
    if CUT_SMILE - FR <= t < CUT_SNAPW - FR: return False
    return True

def draw_rex(cr, t):
    if not rex_drawn(t): return
    X, lift, pitch, face, st = rex(t)
    blink = 0.0
    for b in (1.2, 6.9, 12.0, 19.5, 23.0, 31.0, 43.4, 50.0, 56.0):
        if b <= t < b + 0.16: blink = math.sin(math.pi * (t - b) / 0.16)
    cr.save(); cr.translate(0, -lift)
    O.draw_trex(cr, X, st, t, face=face, pitch=pitch, blink=blink)
    cr.restore()
    x, y = rex_world(X, lift, pitch, face, 215, 600)
    E32.draw_saddle(cr, x, y + 10 - O._walkbob(st), pitch * face + 0.08 * face, 1.0, sid=33510, stirrups=False)
    tx, ty = rex_world(X, lift, pitch, face, *E34.TAG_LH)
    E34.name_tag(cr, tx, ty - O._walkbob(st), 1.1, ang=(-0.12 + pitch * face) * (1 if face == -1 else -1), sid=36010)
    hx, hy = rex_head_c(t)
    helmet(cr, hx, hy, 300, sid=33020)
    # the feather in its tiny hand
    if CUT_FEATH - FR <= t < T_FDROP:
        m = O.trex_pt(X, st, face, pitch, "arm")
        droop = smooth(ramp(t, T_TK1 + 0.1, T_TK1 + 0.6))
        O.draw_feather(cr, m[0] + 10, m[1] - lift + 10, s=2.1, ang=2.3 + 0.4 * (1 - min(1, pitch / 0.25)), t=t,
                       wiggle=1.0 if T_TK0 <= t < T_TK1 else 0.0, droop=0.25 * droop)

def feather_on_ground(cr, t):
    if t < T_FDROP or not (CUT_FEATH - FR <= t < CUT_CARVE - FR or t >= CUT_WIDE - FR): return
    X, lift, pitch, face, st = rex(min(t, T_FDROP))
    m = O.trex_pt(X, st, face, pitch, "arm")
    u = ramp(t, T_FDROP, T_FDROP + 0.45)
    x = lerp(m[0] + 10, HFX - 250, u) + 40 * math.sin(u * 9) * (1 - u)
    y = lerp(m[1], FLOOR_Y - 12, u)
    O.draw_feather(cr, x, y, s=1.5, ang=lerp(1.6, 1.62, u), t=t, droop=0.0)

# ================================================================ the rover
TIPPED_ANG = math.pi / 2
def rover_state(t):
    """x, ang, lift, moving, arm, present"""
    if t < CUT_RIDE - FR:
        arm = smooth(ramp(t, T_ROV, T_ROV + 0.3))
        return ROV_B, 0.0, 0.0, False, arm, True
    if t < CUT_ROVER - FR: return None
    if t < T_DANCE:
        u = ramp(t, CUT_ROVER, T_DANCE)
        return lerp(DXR - 1300, DXR, 1 - (1 - u) ** 2), 0.0, 0.0, True, 0.0, True
    if t < T_WHEELIE:
        k = t - T_DANCE
        return DXR + 110 * math.sin(k * 7.5), 0.05 * math.sin(k * 15), 18 * abs(math.sin(k * 7.5)), True, 0.5 + 0.5 * math.sin(k * 10), True
    if t < T_TIPPED:
        u = ramp(t, T_WHEELIE, T_TIP)
        ang = -0.45 * smooth(u)
        if t >= T_TIP:
            v = ramp(t, T_TIP, T_TIPPED)
            ang = -0.45 - (TIPPED_ANG - 0.45) * v * v
        return DXR + 80 * u, ang, 0.0, True, 1.0, True
    if t < T_LAUNCH:
        return DXR + 80, -TIPPED_ANG, 0.0, True, 0.3, True
    if t < T_LAUNCH + 0.55:
        v = ramp(t, T_LAUNCH, T_LAUNCH + 0.55)
        return DXR + 80, -TIPPED_ANG * (1 - v), 330 * math.sin(math.pi * v), True, 0.3, True
    lift = 40 * ha_hop(t) if laughing(t) else 0.0
    return DXR + 80, 0.0, lift, laughing(t), 0.2, True

def draw_rover_c(cr, t):
    s_ = rover_state(t)
    if not s_: return
    x, ang, lift, moving, arm, _ = s_
    if CUT_TOK - FR <= t < CUT_ROVER - FR: return
    if CUT_CARVE - FR <= t < CUT_WIDE - FR: return
    if CUT_COPY - FR <= t < CUT_EYES - FR: return
    if CUT_SMILE - FR <= t < CUT_SNAPW - FR: return
    cr.save()
    px, py = x - 250, FLOOR_Y - 60                    # pivot near the back wheel (it faces right)
    cr.translate(0, -lift)
    cr.translate(px, py); cr.rotate(ang); cr.translate(-px, -py)
    roll_t = t * (3 if moving else 0)
    E34.draw_rover(cr, x + (math.sin(t * 6) * 3 if abs(ang) > 1.2 else 0), t, moving=moving, arm=arm, tag=False, dusty=0.7)
    cr.restore()
    if T_TIP + 0.25 <= t < T_TIPPED + 0.35:
        L.burst_lines(cr, x, FLOOR_Y - 120, ramp(t, T_TIPPED - 0.05, T_TIPPED + 0.35), r0=150, r1=260, n=9, sid=11)
    if CUT_ROVER - FR <= t < T_WHEELIE and t >= T_DANCE:            # music notes from its speaker
        for k in range(3):
            q = ((t - T_DANCE) * 1.3 + k / 3) % 1.0
            nx, ny = x + 60 + 70 * k, FLOOR_Y - 900 - 260 * q
            cr.arc(nx, ny, 16, 0, 2 * math.pi); cr.set_source_rgba(*INKC, 1 - q); cr.fill()
            sketch_line(cr, [(nx + 14, ny), (nx + 14, ny - 60)], 4, sid=35800 + k, alpha=1 - q)
    if T_ROV <= t < T_ROV + 0.6:
        for k in range(2):
            q = ramp(t, T_ROV + 0.15 * k, T_ROV + 0.15 * k + 0.4)
            if 0 < q < 1:
                cr.arc(ROV_B + 180 + 60 * k, FLOOR_Y - 960 - 80 * q, 12, 0, 2 * math.pi); cr.set_source_rgba(*INKC, 1 - q); cr.fill()

# ================================================================ held things
def mirror(cr, x, y, ang=0.0, s=1.0, crack=0.0, sid=35900):
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sk_rect(cr, -14, 0, 14, 130, 3, sid=sid, fill=(0.85, 0.55, 0.65))
    sk_ell(cr, 0, -70, 80, 95, 5, sid=sid + 1, fill=(0.85, 0.55, 0.65))
    sk_ell(cr, 0, -70, 64, 78, 3, sid=sid + 2, fill=(0.80, 0.92, 1.0))
    cr.move_to(-30, -120); cr.line_to(10, -40); cr.set_source_rgba(1, 1, 1, 0.8); cr.set_line_width(10); cr.stroke()
    if crack > 0.01:
        for k, a in enumerate((0.3, 1.4, 2.5, 3.6, 4.6, 5.6)):
            L_ = 75 * min(1.0, crack * 1.3)
            sketch_line(cr, [(6, -64), (6 + L_ * 0.5 * math.cos(a + 0.2), -64 + L_ * 0.5 * math.sin(a + 0.2)),
                             (6 + L_ * math.cos(a), -64 + L_ * math.sin(a))], 3, sid=sid + 10 + k)
    cr.restore()

def mirror_drawer(cr, x, y, s, t, p):
    if t >= CUT_FEATH - FR and t < CUT_CARVE - FR:            # shards on the ground
        if t >= T_MLAND: shards(cr, HFX + 180)
        return
    if t >= CUT_WIDE - FR: return
    if t < T_MDROP:
        hx, hy = p["rhand"]
        mirror(cr, hx + 6, hy - 30, ang=-0.25, s=s * 1.0, crack=ramp(t, T_CRACK, T_CRACK + 0.12))
        if T_CRACK <= t < T_CRACK + 0.3:
            L.burst_lines(cr, hx, hy - 100, (t - T_CRACK) / 0.3, r0=90, r1=160, n=8, sid=13)
        return
    if t < T_MLAND:
        u = ramp(t, T_MDROP, T_MLAND)
        hx, hy = p["rhand"]
        mirror(cr, lerp(hx + 6, HFX + 180, u), lerp(hy - 30, FLOOR_Y - 140, u * u), ang=-0.25 + 1.5 * u, crack=1.0)
        return
    shards(cr, HFX + 180)
    if t < T_MLAND + 0.3:
        L.burst_lines(cr, HFX + 180, FLOOR_Y - 40, (t - T_MLAND) / 0.3, r0=60, r1=130, n=8, sid=14)

def shards(cr, x):
    sk_rect(cr, x - 70, FLOOR_Y - 26, x + 50, FLOOR_Y - 8, 3, sid=35950, fill=(0.85, 0.55, 0.65))
    for k, (dx, dy, r) in enumerate(((-60, -18, 0.3), (40, -12, 1.2), (100, -20, 2.0), (-120, -10, 2.7), (10, -30, 0.9))):
        sk_poly(cr, [(x + dx, FLOOR_Y + dy), (x + dx + 26 * math.cos(r), FLOOR_Y + dy - 14), (x + dx + 30, FLOOR_Y + dy + 6)], 2,
                sid=35951 + k, fill=(0.80, 0.92, 1.0))

def jackhammer(cr, hx, hy, tx, ty, sid=36050):
    """handle bar at (hx, hy), bit tip at (tx, ty)."""
    ang = math.atan2(ty - hy, tx - hx); Ln = math.hypot(tx - hx, ty - hy)
    cr.save(); cr.translate(hx, hy); cr.rotate(ang)
    sk_rect(cr, -10, -60, 14, 60, 4, sid=sid, fill=(0.25, 0.25, 0.28))                 # T-handle
    sk_rect(cr, 10, -34, Ln * 0.58, 34, 5, sid=sid + 1, fill=(0.92, 0.72, 0.18))      # body
    for k in range(3):
        sketch_line(cr, [(30 + k * 26, -34), (30 + k * 26, 34)], 3, sid=sid + 2 + k, alpha=0.6)
    sk_rect(cr, Ln * 0.58, -16, Ln * 0.66, 16, 3, sid=sid + 6, fill=(0.4, 0.4, 0.45))
    sk_poly(cr, [(Ln * 0.66, -7), (Ln - 16, -6), (Ln, 0), (Ln - 16, 6), (Ln * 0.66, 7)], 3, sid=sid + 7, fill=(0.75, 0.75, 0.8))
    cr.restore()

JH_LEN = 300.0
def jh_tip(t):
    p = bez(carve_u(t))
    if T_C0 <= t < T_C1:
        p = (p[0] + 7 * math.sin(t * 90), p[1] + 6 * math.sin(t * 77))
    return p

def carve_x(t):
    """his body x (centre) while carving: just left of the bit."""
    p = bez(carve_u(t))
    return p[0] - 300

JH_REST = (CY + 520.0, FLOOR_Y - 34)
def jh_drawer(cr, x, y, s, t, p):
    if t < CUT_CARVE - FR:
        hx, hy = p["rhand"]
        if t < POP_JH + 0.1:
            jackhammer(cr, hx, hy - 20, hx + 20, hy + 260 * s)
        else:
            mx = (p["lhand"][0] + p["rhand"][0]) / 2; my = (p["lhand"][1] + p["rhand"][1]) / 2
            jackhammer(cr, mx, my, mx + 40, FLOOR_Y - 30)
        return
    if t < T_DROP:
        if CUT_CARVE - FR <= t:
            h = jh_handle(t, p); tip = jh_tip(t) if t < T_C1 else bez(1.0)
            jackhammer(cr, h[0], h[1], tip[0], tip[1])
            if T_C0 <= t < T_C1:
                L.burst_lines(cr, tip[0], tip[1], (t * 6) % 1.0, r0=30, r1=90, n=6, sid=15)
        return
    u = ramp(t, T_DROP, T_DROP + 0.3)
    if u < 1:
        h = jh_handle(T_DROP, p); tip = bez(1.0)
        jackhammer(cr, lerp(h[0], JH_REST[0] - 160, u), lerp(h[1], JH_REST[1], u * u), lerp(tip[0], JH_REST[0] + 160, u), lerp(tip[1], JH_REST[1] + 10, u * u))
    else:
        jackhammer(cr, JH_REST[0] - 160, JH_REST[1], JH_REST[0] + 160, JH_REST[1] + 10)

def jh_handle(t, p):
    nx, ny = p["neck"]
    tip = jh_tip(t) if t < T_C1 else bez(1.0)
    d = math.hypot(tip[0] - nx, tip[1] - ny - 260) + 1e-6
    hx, hy = nx + 80, ny + 260
    ux, uy = (tip[0] - hx), (tip[1] - hy); n = math.hypot(ux, uy) + 1e-6
    if n > JH_LEN: hx, hy = tip[0] - ux / n * JH_LEN, tip[1] - uy / n * JH_LEN
    return (hx, hy)

# dust while carving
def carve_dust(cr, t, layer):
    if not (CUT_CARVE - FR <= t < T_CLEAR + 0.6): return
    u = min(carve_u(t), 1.0)
    fade = 1.0 - ramp(t, T_C1 + 0.1, T_CLEAR + 0.5)
    if layer == "back":
        for k in range(6):
            q = max(0.0, u - 0.04 * k)
            x, y = bez(q)
            r = 70 + 25 * k + 20 * math.sin(k * 1.7 + t * 3)
            O.draw_smoke_puff(cr, x + 20 * math.sin(t * 3 + k), y - 150 - 60 * k, r, alpha=0.45 * fade * (1 - k / 7), dark=0.25)
    else:
        if t < T_C1:
            tip = jh_tip(t)
            for k in range(4):
                q = ((t * 3 + k / 4) % 1.0)
                O.draw_smoke_puff(cr, tip[0] + 40 + 120 * q, tip[1] - 60 * q, 40 + 60 * q, alpha=0.6 * (1 - q), dark=0.25)
                cr.arc(tip[0] + 60 * math.cos(k * 1.6 + t * 20) * q * 2, tip[1] - 40 * q * 2 + 80 * q * q * 4, 8, 0, 2 * math.pi)
                cr.set_source_rgb(*STONE_D); cr.fill()

# ================================================================ poses
def P_(name, **kw): L.POSES[name] = kw
P_("tok", lelb=(430, 860), lhand=(385, 712), relb=(650, 860), rhand=(700, 712), lhand_t="point", rhand_t="point")
P_("mirror_look", lelb=(450, 940), lhand=(440, 1040), relb=(700, 820), rhand=(735, 700), lhand_t="mitt", rhand_t="grip")
P_("jh_hold", lelb=(470, 960), lhand=(520, 1030), relb=(620, 960), rhand=(580, 1030), lhand_t="grip", rhand_t="grip")
P_("jh_carve", lelb=(560, 950), lhand=(600, 960), relb=(640, 920), rhand=(640, 960), lhand_t="grip", rhand_t="grip", nowalk=1.0)
P_("strain", lelb=(455, 960), lhand=(470, 1060), relb=(625, 960), rhand=(610, 1060), lhand_t="fist", rhand_t="fist")
P_("look_up", lelb=(460, 960), lhand=(450, 1060), relb=(620, 960), rhand=(630, 1060))

# ================================================================ scene (him)
def deadpan_pull(S, *a, **kw):
    """pocket_pull, but he stays flat the whole time (he can't smile - that's the episode)."""
    orig = S.set
    def flat_set(t, body=None, face=None, dur=0.3, ease="smooth", clear=True, **k2):
        for bad in ("eyescale", "open", "tilt"): k2.pop(bad, None)
        return orig(t, body, "deadpan", dur=dur, ease=ease, clear=clear, lid=0.4, **k2)
    S.set = flat_set
    try: M.Scene.pocket_pull(S, *a, **kw)
    finally: S.set = orig

S = M.Scene(start_body="stand", start_face="deadpan", x0=HB - 540)
S.auto_blinks = True
S.floor = False
S.card("irdlubuhsmmp", "Smile", "0", t0=0.3)
NOCARD = [False]
_card_ov = S.overlays[-1]
S.overlays[-1] = lambda cr, t: None if NOCARD[0] else _card_ov(cr, t)
CAM_A = cam(HB + 60, 0.56, fs=1650)
S.camkeys[0] = (0.0, CAM_A, 0); S.cam = CAM_A

# ---------------------------------------------------------------- A: Mars Base 1
S.read_card(T_READ, react="deadpan", lines=1)
S.set(T_TRY0, "strain", "holding_it", dur=0.4, look=(0.0, 0.0), quiver=0.4)
S.set(T_TRY0 + 0.45, "strain", "holding_it", dur=0.25, mouth="auto", smile=0.14, quiver=0.9, twitch=0.7, sweat=0.3, look=(0.0, 0.0))
S.sfx(T_TRY0 + 0.5, "squeak", 0.03); S.sfx(T_TRY0 + 0.62, "squeak", 0.02)
S.set(T_TRY1, "stand", "deadpan", dur=0.12, ease="snap", look=(0.0, 0.0))
S.camera(T_TRY0, *cam(HB + 40, 0.62, fs=1640), 0.7)
S.sfx(T_ROV, "boop", 0.04); S.sfx(T_ROV + 0.15, "boop", 0.04); S.sfx(T_ROV, "whine", 0.015, dur=0.4)
S.set(T_ROV + 0.2, "stand", "deadpan", dur=0.3, turn=-0.4, look=(-1.0, 0.3))
S.set(T_LOOKR, "stand", "deadpan", dur=0.3, turn=0.6, look=(1.0, -0.2))
S.camera(T_ROV, *cam(HB - 60, 0.52, fs=1660), 0.8)

# the ride
S.cut(CUT_RIDE - FR, cam=cam(REX_B, 0.42, fs=1680), x=HB - 540)
S.set(CUT_RIDE - FR, "ride", "deadpan", dur=0.0, turn=0.9, look=(1.0, 0.0))
S.sfx(T_BOLT, E32.ROAR_WAV, 0.08); S.sfx(T_BOLT + 0.1, "whoosh", 0.08)
S.set(T_BOLT + 0.05, "ride", "deadpan", dur=0.12, ease="snap", turn=0.9, look=(1.0, 0.0), lean=-0.2, curl_up=1.0)
S.set(T_BOLT + 0.5, "ride", "dead_stare", dur=0.3, turn=0.9, look=(1.0, 0.0), lean=-0.05)
for k in range(5): S.sfx(T_BOLT + 0.2 + 0.3 * k, "thud", 0.07)
S.sfx(CUT_CY - 0.7, "wind", 0.08, dur=1.2)

# ---------------------------------------------------------------- B: Cydonia
CAM_W = cam(CY - 400, 0.30, fs=1700)
S.cut(CUT_CY - FR, cam=CAM_W, x=HB - 540)
S.set(CUT_CY - FR, "ride", "deadpan", dur=0.0, turn=0.9, look=(1.0, 0.0), lean=-0.05)
S.sfx(CUT_CY + 0.1, "skid", 0.12, dur=0.7)
S.set(CUT_CY + 0.4, "ride", "dead_stare", dur=0.15, turn=0.9, look=(1.0, 0.0), lean=0.25)
S.set(T_STOPC, "ride", "dead_stare", dur=0.4, turn=0.6, look=(0.6, -1.0), lid=0.2)
S.camera(T_STOPC - 0.2, *cam(CY - 350, 0.29, fs=1720), 1.0)
S.sfx(CUT_CY + 0.3, "boop", 0.015)

# the two flat faces
S.cut(CUT_FACE - FR, cam=cam(HFX + 300, 0.40, fs=1690), x=HFX - 540)
S.set(CUT_FACE - FR, "stand", "dead_stare", dur=0.0, look=(0.0, 0.0), lid=0.3)
S.set(CUT_FACE + 0.45, "stand", "dead_stare", dur=0.3, look=(0.7, -1.0), tilt=-0.08, lid=0.2)
S.set(CUT_FACE + 1.05, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), tilt=0.0, lid=0.35)
S.camera(CUT_FACE, *cam(HFX + 300, 0.43, fs=1680), 1.5)

# attempt 1: fingers vs the helmet
S.cut(CUT_TOK - FR, cam=cam(HFX + 40, 0.66, fs=1640), x=HFX - 540)
S.set(CUT_TOK - FR, "stand", "deadpan", dur=0.0, look=(0.0, 0.0))
S.set(CUT_TOK + 0.1, "tok", "deadpan", dur=0.35, look=(0.0, 0.0))
S.sfx(T_TOK, "tok", 0.07); S.sfx(T_TOK + 0.22, "tok", 0.06)
S.set(T_TOK + 0.5, "tok", "dead_stare", dur=0.3, look=(0.0, 0.0), lid=0.4)
S.set(T_TOK + 1.0, "stand", "dead_stare", dur=0.4, look=(0.0, 0.0), lid=0.4)

# attempt 2: the mirror
deadpan_pull(S, T_MIR, "mirror", mirror_drawer, (0, 0), held=True)
S.set(T_MLOOK - 0.2, "mirror_look", "deadpan", dur=0.3, turn=0.4, look=(1.0, -0.3))
S.set(T_MLOOK + 0.3, "mirror_look", "holding_it", dur=0.4, turn=0.4, look=(1.0, -0.3), quiver=0.6)
S.set(T_CRACK - 0.3, "mirror_look", "holding_it", dur=0.3, turn=0.4, look=(1.0, -0.3), mouth="auto", smile=0.12, quiver=1.0, twitch=0.8, sweat=0.5)
S.sfx(T_MLOOK + 0.5, "squeak", 0.02); S.sfx(T_CRACK - 0.2, "squeak", 0.025)
S.sfx(T_CRACK, "clack", 0.10)
S.set(T_CRACK + 0.05, "mirror_look", "dead_stare", dur=0.1, ease="snap", turn=0.4, look=(1.0, -0.3), eyescale=1.15)
S.set(T_CRACK + 0.35, "mirror_look", "dead_stare", dur=0.35, turn=0.1, look=(0.0, 0.0), lid=0.4)
S.set(T_MDROP, "stand", "dead_stare", dur=0.25, turn=0.0, look=(0.3, 0.6), lid=0.4)
S.sfx(T_MLAND, "clack", 0.07); S.sfx(T_MLAND + 0.05, "tick", 0.05)

# attempt 3: Jerry's feather
S.cut(CUT_FEATH - FR, cam=cam(HFX - 300, 0.50, fs=1660), x=HFX - 540)
S.set(CUT_FEATH - FR, "stand", "dead_stare", dur=0.0, turn=-0.3, look=(-0.8, -0.6), lid=0.3)
S.set(T_TK0, "stand", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lid=0.35)
for k in range(7): S.sfx(T_TK0 + 0.22 * k, "squeak", 0.015)
S.set(T_TK0 + 0.75, "stand", "dead_stare", dur=0.08, ease="snap", look=(0.0, 0.0), lid=0.35, twitch=0.9, brow=0.25)
S.set(T_TK0 + 1.0, "stand", "dead_stare", dur=0.2, look=(0.0, 0.0), lid=0.4, twitch=0.0, brow=0.0)
S.set(T_TK1 + 0.3, "stand", "dead_stare", dur=0.3, turn=-0.3, look=(-0.8, -0.6), lid=0.4)
S.sfx(T_FDROP + 0.4, "whoosh", 0.015, dur=0.3)

# attempt 4: the rover's dance
S.cut(CUT_ROVER - FR, cam=cam(HFX - 320, 0.50, fs=1660), x=HFX - 540)
S.set(CUT_ROVER - FR, "stand", "dead_stare", dur=0.0, turn=-0.3, look=(-0.8, -0.3), lid=0.4)
S.sfx(CUT_ROVER, "whine", 0.02, dur=0.6)
S.sfx(T_DANCE, E33.TUNE_WAV, 0.05)
S.sfx(T_WHEELIE, "whine", 0.03, dur=0.4)
S.sfx(T_TIPPED - 0.05, "clack", 0.10); S.sfx(T_TIPPED, "thud", 0.10)
S.set(T_TIPPED + 0.1, "stand", "dead_stare", dur=0.3, turn=-0.4, look=(-1.0, 0.5), lid=0.4)
S.set(T_TIPPED + 0.45, "stand", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), lid=0.45)
S.set(T_UP, "stand", "dead_stare", dur=0.35, turn=0.2, look=(0.8, -1.0), tilt=-0.08, lid=0.3)
S.set(T_IDEA, "stand", "dead_stare", dur=0.1, ease="snap", turn=0.2, look=(0.8, -1.0), tilt=-0.08, lid=0.0, curl_up=1.0, eyescale=1.1)
S.sfx(T_IDEA, "ding", 0.04)
S.camera(T_UP, *cam(HFX - 100, 0.52, fs=1650), 0.6)

# the jackhammer
S.x = HFX - 540
deadpan_pull(S, T_JH, "jh", jh_drawer, (0, 0), held=True)
S.set(POP_JH + 0.1, "jh_hold", "deadpan", dur=0.3, look=(0.0, 0.0), lid=0.4)

# carving
S.cut(CUT_CARVE - FR, cam=cam(GL[0] - 120, 0.62, fs=1640), x=carve_x(CUT_CARVE) - 540)
S.set(CUT_CARVE - FR, "jh_carve", "deadpan", dur=0.0, turn=0.7, look=(1.0, -0.4), lid=0.35)
S.sfx(T_C0, JACK_WAV, 0.10)
S.set(T_C0 + 0.3, "jh_carve", "dead_stare", dur=0.3, turn=0.7, look=(1.0, -0.2), lid=0.4)
S.camera(T_C0, *cam(bez(0.22)[0] - 160, 0.62, fs=1640), CUT_WIDE - T_C0, "linear")
S.cut(CUT_WIDE - FR, cam=cam(CY, 0.34, fs=1700))
S.set(CUT_WIDE - FR, "jh_carve", "dead_stare", dur=0.0, turn=0.7, look=(1.0, 0.0), lid=0.4)
S.shake(CUT_WIDE, T_C1 - CUT_WIDE, 5)
S.set(T_C1 + 0.1, "jh_carve", "dead_stare", dur=0.3, turn=0.5, look=(0.8, -0.4), lid=0.4)
S.set(T_DROP, "stand", "dead_stare", dur=0.25, turn=0.0, look=(0.4, 0.6), lid=0.4)
S.sfx(T_DROP + 0.3, "clack", 0.10); S.sfx(T_DROP + 0.3, "thud", 0.08)
S.set(T_DROP + 0.4, "look_up", "dead_stare", dur=0.35, turn=-0.2, look=(-0.6, -1.0), tilt=-0.1, lid=0.25)
S.set(T_DROP + 0.95, "look_up", "dead_stare", dur=0.3, turn=0.0, look=(0.0, 0.0), tilt=0.0, lid=0.4)
S.camera(T_CLEAR - 0.3, *cam(CY + 150, 0.36, fs=1700), 1.2)
_xk = []
t_ = CUT_CARVE
while t_ <= T_C1 + 0.05:
    _xk.append((t_, carve_x(t_) - 540, 0.1, "linear")); t_ += 0.1
S.xkeys += _xk
X_END = carve_x(T_C1) - 540
S.xkeys.append((T_C1 + 0.1, X_END, 0.001, "linear")); S.x = X_END

# copying it: the strain
S.cut(CUT_COPY - FR, cam=cam(X_END + 540 - 60, 0.66, fs=1640), x=X_END)
S.set(CUT_COPY - FR, "strain", "holding_it", dur=0.0, look=(0.0, 0.0), quiver=0.2)
S.set(T_STRAIN0 + 0.6, "strain", "holding_it", dur=0.8, mouth="auto", smile=0.06, quiver=0.6, twitch=0.3, sweat=0.3, look=(0.0, 0.0))
S.set(T_STRAIN0 + 1.5, "strain", "holding_it", dur=0.6, mouth="auto", smile=0.16, quiver=1.0, twitch=0.9, sweat=0.8, brow=0.4, look=(0.0, 0.0))
for k in range(5): S.sfx(T_STRAIN0 + 0.7 + 0.32 * k, "squeak", 0.012 + 0.004 * k)
S.camera(T_STRAIN0, *cam(X_END + 540 - 60, 0.74, fs=1630), T_STRAIN1 - T_STRAIN0)
S.sfx(T_RUMBLE, "kaboom", 0.12, dur=2.0); S.shake(T_RUMBLE, 0.5, 10)
S.set(T_RUMBLE + 0.05, "stand", "dead_stare", dur=0.12, ease="snap", look=(0.0, 0.0), lid=0.2, eyescale=1.1)
S.set(T_RUMBLE + 0.25, "stand", "dead_stare", dur=0.3, look=(-0.3, -1.0), tilt=-0.08, lid=0.1, eyescale=1.15)

# the eyes open
CAM_E = cam(CY - 200, 0.33, fs=1700)
S.cut(CUT_EYES - FR, cam=CAM_E)
S.set(CUT_EYES - FR, "look_up", "dead_stare", dur=0.0, look=(-0.3, -1.0), tilt=-0.08, lid=0.1, eyescale=1.15)
S.sfx(T_EYES0, "rummage", 0.10, dur=0.5); S.sfx(T_EYES0, "thud", 0.06)
for k in range(3): S.sfx(T_EYES1 + 0.15 + 0.3 * k, "thud", 0.07); S.sfx(T_EYES1 + 0.15 + 0.3 * k + 0.12, "thud", 0.04)
S.camera(T_EYES1, *cam(CY - 200, 0.35, fs=1700), 0.7)

# THE LAUGH: launch, flip, land
CAM_L = cam(CY - 350, 0.31, fs=1700)
S.camera(T_LAUGH - 0.05, *CAM_L, 0.3)
S.sfx(T_LAUGH, LAUGH_WAV, 0.42)
S.shake(T_LAUGH, T_LAUGH_END - T_LAUGH, 9)
S.sfx(T_LAUNCH, "boing", 0.06); S.sfx(T_LAUNCH, "whoosh", 0.06)
S.set(T_LAUNCH, "cannonball", "dead_stare", dur=0.12, ease="snap", look=(0.0, 0.0), lid=0.2, eyescale=1.1)
S.set(T_LAND - 0.12, "sit_floor", "dead_stare", dur=0.12, ease="snap", look=(0.0, 0.0), lid=0.3)
S.sfx(T_LAND, "thud", 0.18)
X_SIT = CY - 220 - 540
S.xkeys.append((T_LAUNCH, X_END, 0.001, "linear"))
S.xkeys.append((T_LAUNCH + 0.02, X_SIT, T_LAND - T_LAUNCH - 0.02, "linear")); S.x = X_SIT

def flip_hook(t, p):
    if T_LAUNCH <= t < T_LAND:
        u = (t - T_LAUNCH) / (T_LAND - T_LAUNCH)
        h = 760 * 4 * u * (1 - u)
        ang = 2 * math.pi * smooth(u) * -1
        cx_, cy_ = p["hip"]
        c, s_ = math.cos(ang), math.sin(ang)
        for k in L.JOINTS:
            dx, dy = p[k][0] - cx_, p[k][1] - cy_ - 120
            p[k] = (cx_ + dx * c - dy * s_, cy_ + 120 + dx * s_ + dy * c - h)
        p["nowalk"] = 1.0
    if laughing(t) and t >= T_LAND:
        b = 26 * ha_hop(t)
        for k in L.JOINTS: p[k] = (p[k][0], p[k][1] - b)
    return p
S.hook(flip_hook)

# close: the smile
S.cut(CUT_SMILE - FR, cam=cam(X_SIT + 540 + 30, 0.72, fs=1600))
S.set(CUT_SMILE - FR, "sit_floor", "dead_stare", dur=0.0, look=(0.0, 0.0), lid=0.35)
S.set(CUT_SMILE + 0.25, "sit_floor", "dead_stare", dur=0.35, look=(0.6, -0.9), tilt=-0.06, lid=0.3)
S.set(T_TWITCH, "sit_floor", "dead_stare", dur=0.1, ease="snap", look=(0.6, -0.9), tilt=-0.06, lid=0.3, mouth="auto", smile=0.12, twitch=0.8)
S.set(T_TWITCH + 0.15, "sit_floor", "dead_stare", dur=0.1, look=(0.6, -0.9), tilt=-0.06, lid=0.3, mouth="auto", smile=0.02)
S.set(T_SMILE, "sit_floor", "neutral", dur=0.6, mouth="auto", smile=1.0, lid=0.1, look=(0.2, -0.3), brow=0.15, tilt=-0.04)
S.set(T_HISLAUGH, "sit_floor", "laughing", dur=0.25, tears=0.0, blush=0.0)
S.camera(T_SMILE, *cam(X_SIT + 540 + 20, 0.86, fs=1580), 1.8)

# hard cut wide: flat again. FLASH.
CAM_P = cam(CY - 700, 0.31, fs=1700)
S.cut(CUT_SNAPW - FR, cam=CAM_P)
S.set(CUT_SNAPW - FR, "sit_floor", "dead_stare", dur=0.0, look=(0.0, 0.0), lid=0.35)
S.set(T_SNAP - 0.1, "sit_floor", "dead_stare", dur=0.08, look=(0.0, 0.0), lid=1.0)
S.sfx(T_SNAP, "clap", 0.05); S.sfx(T_SNAP, "tick", 0.06); S.sfx(T_SNAP + 0.05, "twinkle", 0.02)
S.flash(T_SNAP, 0.25)

# after the photo: quiet
S.cut(CUT_AFTER - FR, cam=cam(X_SIT + 540 - 250, 0.52, fs=1660))
S.set(CUT_AFTER - FR, "sit_floor", "dead_stare", dur=0.0, look=(0.0, 0.0), lid=0.4)
S.set(CUT_AFTER + 0.1, "sit_floor", "dead_stare", dur=0.3, look=(-0.6, -0.2), lid=0.4)
S.set(T_LOOKUS, "sit_floor", "dead_stare", dur=0.3, look=(0.0, 0.0), lid=0.45)
S.cut(CUT_STANDUP - FR, cam=cam(X_SIT + 540 - 150, 0.54, fs=1655))
S.set(CUT_STANDUP - FR, "stand", "dead_stare", dur=0.0, look=(0.0, 0.0), lid=0.4)

# ---------------------------------------------------------------- the ask (Cydonia)
S.the_ask(T_ASK, hold=HOLD, push=False)
S.camera(T_ASK + 6.9, *cam(X_SIT + 540 - 120, 0.58, fs=1650), 5.0)
T_END = S.t
S.blink(5.0, 12.3, 19.4, 27.5, 32.0, 46.0)

# camera follow during the rides
_ck = []
t_ = T_BOLT
while t_ < CUT_CY - FR:
    X, lift, pitch, face, st = rex(t_)
    _ck.append((t_, cam(X + 350, 0.42, fs=1680), 0.1, "linear")); t_ += 0.1
S.camkeys += _ck
S.camkeys.sort(key=lambda k: k[0])

# ---------------------------------------------------------------- hooks
RIDING = ((CUT_RIDE - FR, CUT_FACE - FR),)
def riding(t): return any(a <= t < b for a, b in RIDING)

def ride_hook(t, p):
    if riding(t):
        sx, sy = seat(t)
        hx, hy = p["hip"]
        dx, dy = sx - hx, sy - 30 - hy
        for k in L.JOINTS:
            p[k] = (p[k][0] + dx, p[k][1] + dy)
    # carving: hands on the jackhammer, the whole body rattles
    if CUT_CARVE - FR <= t < T_DROP:
        h = jh_handle(t, p)
        tip = jh_tip(t) if t < T_C1 else bez(1.0)
        ux, uy = tip[0] - h[0], tip[1] - h[1]; n = math.hypot(ux, uy) + 1e-6
        ux, uy = ux / n, uy / n
        p["lhand"] = (h[0] - uy * 40, h[1] + ux * 40); p["rhand"] = (h[0] + uy * 40, h[1] - ux * 40)
        for side in ("l", "r"):
            sh = p["neck"]; hd = p[side + "hand"]
            p[side + "elb"] = ((sh[0] + hd[0]) / 2 - 20, (sh[1] + hd[1]) / 2 + 70)
        if T_C0 <= t < T_C1:
            jx, jy = 5 * math.sin(t * 83), 4 * math.sin(t * 71)
            for k in L.JOINTS:
                if k not in ("lfoot", "rfoot"): p[k] = (p[k][0] + jx, p[k][1] + jy)
    return p
S.hook(ride_hook)

# ---------------------------------------------------------------- draw order
def props_back(cr, t, p, ly):
    if ly != "back": return
    if t < CUT_CY - FR:
        E34.draw_rex.__globals__  # (day 34's base props are drawn by its world)
        draw_rover_c(cr, t)
        draw_rex(cr, t)
        return
    carve_dust(cr, t, "back")
    draw_rex(cr, t)
    feather_on_ground(cr, t)
    draw_rover_c(cr, t)
S.prop(props_back)

def world(cr, t):
    if t < CUT_CY - FR:
        E34.draw_base(cr, t if t < 1e9 else 0); return
    draw_cydonia(cr, t)
S.background(world)

def draw_my_helmet(cr, t, p):
    if p.get("show", 1.0) < 0.5: return
    hx, hy = p["head"]
    helmet(cr, hx + 6, hy - 10, 175, sid=33000)
    if CUT_TOK - FR <= t < CUT_TOK + 2.0 and T_TOK <= t < T_TOK + 0.5:
        for k, tk in enumerate((T_TOK, T_TOK + 0.22)):
            if tk <= t < tk + 0.25:
                for side in ("lhand", "rhand"):
                    x, y = p[side]; L.burst_lines(cr, x, y, (t - tk) / 0.25, r0=30, r1=70, n=6, sid=16 + k)

def props_front(cr, t, p, ly):
    if ly != "front": return
    draw_my_helmet(cr, t, p)
    carve_dust(cr, t, "front")
    if CUT_RIDE - FR <= t < CUT_CY - FR:
        if t >= CUT_CY - 1.1: draw_dust_devil(cr, t, DD)
        if t >= CUT_CY - 0.35:
            vx0, vy0, vx1, vy1 = O._visible(cr)
            cr.rectangle(vx0 - 100, vy0 - 100, vx1 - vx0 + 200, vy1 - vy0 + 200)
            cr.set_source_rgba(0.80, 0.55, 0.40, ramp(t, CUT_CY - 0.35, CUT_CY - 0.05)); cr.fill()
    if CUT_CY - FR <= t < CUT_CY + 0.5:
        k = 1 - ramp(t, CUT_CY, CUT_CY + 0.5)
        for j in range(6):
            O.draw_smoke_puff(cr, REX_C - 1500 + 200 * math.sin(j), FLOOR_Y - 300 - 300 * j, 400, alpha=0.9 * k, dark=0.15)
    if T_LAND <= t < T_LAND + 0.4:
        O.draw_smoke_puff(cr, X_SIT + 540 - 120, FLOOR_Y - 40, 90 * (1 + ramp(t, T_LAND, T_LAND + 0.4)), alpha=0.7 * (1 - ramp(t, T_LAND, T_LAND + 0.4)), dark=0.25)
        O.draw_smoke_puff(cr, X_SIT + 540 + 120, FLOOR_Y - 40, 90 * (1 + ramp(t, T_LAND, T_LAND + 0.4)), alpha=0.7 * (1 - ramp(t, T_LAND, T_LAND + 0.4)), dark=0.25)
S.prop(props_front)

# ---------------------------------------------------------------- the photo (frame 35A72)
_ORIG_RENDER = L.render_frame
def _render(t, surf):
    if not (CUT_PHOTO <= t < CUT_AFTER - FR):
        return _ORIG_RENDER(t, surf)
    tmp = cairo.ImageSurface(cairo.FORMAT_ARGB32, L.W, L.H)
    NOCARD[0] = True
    try: _ORIG_RENDER(T_SNAP - FR, tmp)
    finally: NOCARD[0] = False
    cr = cairo.Context(surf)
    cr.set_source_rgb(0.20, 0.12, 0.09); cr.paint()
    k = smooth(ramp(t, CUT_PHOTO, CUT_PHOTO + 0.3))
    pz = smooth(ramp(t, CUT_PHOTO + 0.75, CUT_AFTER - 0.25))
    s = lerp(1.05, 0.80, k) * (1 - pz) + 2.3 * pz
    fx, fy = L.world_to_screen(T_SNAP, (X_SIT + 540, FLOOR_Y - 360))
    cr.save(); cr.translate(L.W / 2, L.H / 2 + 40 * (1 - pz) + 260 * pz); cr.rotate(-0.035 * k); cr.scale(s, s)
    cr.translate(-(fx - L.W / 2) * pz, -(fy - L.H / 2) * pz)
    W2, H2 = L.W / 2, L.H / 2
    cr.rectangle(-W2 - 50, -H2 - 50, L.W + 100, L.H + 230); cr.set_source_rgb(0.97, 0.96, 0.93); cr.fill()
    cr.set_source_surface(tmp, -W2, -H2); cr.paint()
    cr.rectangle(-W2, -H2, L.W, L.H); cr.set_operator(cairo.OPERATOR_HSL_SATURATION); cr.set_source_rgb(0.5, 0.5, 0.5); cr.fill()
    cr.set_operator(cairo.OPERATOR_OVER)
    cr.rectangle(-W2, -H2, L.W, L.H); cr.set_source_rgba(0.1, 0.1, 0.1, 0.12); cr.fill()
    for y in range(int(-H2), int(H2), 6):                                  # scan lines
        cr.rectangle(-W2, y, L.W, 2); cr.set_source_rgba(0, 0, 0, 0.07); cr.fill()
    for i in range(1, 5):                                                    # reseau crosses
        for j in range(1, 8):
            x, y = -W2 + i * L.W / 5, -H2 + j * L.H / 8
            cr.move_to(x - 16, y); cr.line_to(x + 16, y); cr.move_to(x, y - 16); cr.line_to(x, y + 16)
            cr.set_source_rgba(0, 0, 0, 0.75); cr.set_line_width(3); cr.stroke()
    cr.rectangle(-W2, -H2, L.W, L.H); cr.set_source_rgb(*INKC); cr.set_line_width(4); cr.stroke()
    draw_text(cr, "35A72", -W2 + 160, H2 + 95, 80, rot=-0.02)
    cr.restore()
    _card_ov(cr, t)
    cr.save(); cr.scale(2, 2); cr.set_source_surface(L.GRAIN[int(t * 10) % 3], 0, 0); cr.paint_with_alpha(0.5); cr.restore()
L.render_frame = _render

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        S.build()
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, L.W, L.H)
        for a in sys.argv[2:]:
            tt = float(a); L.render_frame(tt, surf); surf.write_to_png(os.path.join(HERE, "still_%05.2f.png" % tt))
        print("dur", T_END)
    else:
        S.render("day035.mp4")
