r"""Nigel Bane render engine (shared by every episode).

World = flat black-and-white hand-drawn line art. Colour lives only in Nigel's eyes (HD galaxies, mood driven)
and in the window (whose sky mirrors his eyes).

An episode script does:
    import sys; sys.path.insert(0, r"C:
igelbain\engine")
    import nigel as N
    N.setup()                      # loads words.json + voice_edit.wav from the episode folder
    T, TE = N.T, N.TE
    ... build Tracks with N.P / N.SKY / N.mood_vec ...
    N.configure(mood_track=..., pose_track=..., x_track=..., cam_track=..., follow_track=..., env_track=...,
                window_knocks=[...], tally_base=0, tally_new=[(t, dur), ...], sfx=[...])
    N.main()
"""
import cairo, numpy as np, json, wave, math, os, subprocess, sys, random
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
VO = 2.0          # voice starts here (after the cold-open knocks)
SR = 44100
INK = (0.07, 0.07, 0.08)
PAPER = (0.985, 0.984, 0.978)
FLOOR_Y = 1478
INTRO_KNOCKS = [0.55, 0.9, 1.25]
KNOCK_GAIN = {}   # optional {knock_time: gain multiplier}; episodes may extend INTRO_KNOCKS for on-lens knocks later on

# ---------------------------------------------------------------- timing ---
words = []
voice = None
def setup(words_path="words.json", voice_path="voice_edit.wav", vo=2.0):
    global words, voice, VO
    VO = vo
    words = json.load(open(words_path))
    for w in words:
        w["start"] += VO; w["end"] += VO
    with wave.open(voice_path) as wv:
        voice = np.frombuffer(wv.readframes(wv.getnframes()), dtype=np.int16).astype(np.float32) / 32768

def _find(text, n):
    c = 0
    for w in words:
        if w["text"].lower().strip(".,?!") == text.lower():
            c += 1
            if c == n:
                return w
    raise KeyError(text)

def T(text, n=1): return _find(text, n)["start"]
def TE(text, n=1): return _find(text, n)["end"]

# ------------------------------------------------------------- utilities ---
def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)

def lerp(a, b, u):
    if isinstance(a, dict):
        return {k: lerp(a[k], b[k], u) for k in a}
    if isinstance(a, (tuple, list)):
        return tuple(lerp(x, y, u) for x, y in zip(a, b))
    return a + (b - a) * u

class Track:
    """keys: (time, value, transition_seconds). Value eases from the previous state starting at time."""
    def __init__(self, keys):
        self.keys = sorted(keys, key=lambda k: k[0])
    def at(self, t):
        cur = self.keys[0][1]
        for kt, kv, kd in self.keys[1:]:
            if t < kt:
                break
            cur = lerp(cur, kv, smooth((t - kt) / max(kd, 1e-3)))
        return cur

def rgb(c): return tuple(v / 255 for v in c)

# ---------------------------------------------------------------- moods ----
MOODS = {
    "curious":    dict(pal=[(4, 26, 40), (20, 150, 170), (170, 255, 240)], acc=(255, 200, 120), brow=0.25, frown=0.0, spin=0.6),
    "uncanny":    dict(pal=[(16, 6, 40), (80, 46, 180), (100, 240, 215)], acc=(255, 100, 210), brow=0.4, frown=0.1, spin=1.1),
    "drifting":   dict(pal=[(10, 8, 44), (72, 50, 170), (190, 150, 255)], acc=(90, 225, 255), brow=0.3, frown=0.05, spin=0.8),
    "awe":        dict(pal=[(46, 14, 0), (220, 110, 25), (255, 235, 140)], acc=(255, 120, 190), brow=-0.1, frown=-0.15, spin=1.0),
    "melancholy": dict(pal=[(2, 4, 20), (24, 56, 130), (100, 150, 235)], acc=(160, 100, 240), brow=0.6, frown=0.3, spin=0.45),
    "lonely":     dict(pal=[(2, 3, 12), (16, 30, 84), (80, 105, 180)], acc=(110, 90, 200), brow=0.8, frown=0.4, spin=0.3),
    "warm":       dict(pal=[(46, 10, 30), (215, 85, 120), (255, 220, 150)], acc=(255, 245, 180), brow=0.35, frown=-0.12, spin=0.7),
    "unease":     dict(pal=[(24, 0, 34), (205, 30, 170), (90, 255, 175)], acc=(255, 255, 255), brow=0.6, frown=0.15, spin=1.9),
    "void":       dict(pal=[(0, 0, 0), (6, 6, 12), (40, 40, 60)], acc=(30, 30, 50), brow=0.7, frown=0.1, spin=0.15),   # eyes gone black (dread)
}
def mood_vec(name):
    m = MOODS[name]
    return {"p0": m["pal"][0], "p1": m["pal"][1], "p2": m["pal"][2], "acc": m["acc"],
            "brow": m["brow"], "frown": m["frown"], "spin": m["spin"]}


# ----------------------------------------------------------------- poses ---
# simple stick figure: single ink lines. Coordinates are world space at body offset 0.
BASE = dict(head=(450, 775), neck=(452, 945), hip=(450, 1240),
            lelb=(408, 1098), lhand=(394, 1205), relb=(496, 1098), rhand=(508, 1205),
            lknee=(428, 1360), lfoot=(405, FLOOR_Y), rknee=(474, 1360), rfoot=(497, FLOOR_Y),
            tilt=0.0, look=(0.0, 0.0), eyescale=1.0, swing=1.0, fist=0.0, roll=0.0, finger=0.0, letter=0.0,
            reveal=1.0, palm=0.0, shut=0.0)
def P(base=BASE, **kw):
    d = dict(base); d.update(kw); return d

STAND = P()
KNOCK = P(relb=(628, 1040), rhand=(612, 905), fist=1.0, swing=0.0, look=(0.0, 0.05), tilt=0.03)
TAPGLASS = P(relb=(560, 1085), rhand=(548, 1000), fist=0.6, swing=0.0, look=(0.15, 0.2), tilt=0.05)
THINK = P(lelb=(424, 1092), lhand=(492, 1080), relb=(530, 1062), rhand=(478, 962), tilt=-0.1, look=(-0.45, -0.5), swing=0.0)
OPEN = P(lelb=(382, 1048), lhand=(304, 1004), relb=(522, 1048), rhand=(600, 1004), swing=0.0)
CHEST = P(relb=(522, 1102), rhand=(462, 1030), lelb=(400, 1100), lhand=(386, 1200), tilt=-0.06, look=(0.0, 0.15), swing=0.0)
EXIST = P(lelb=(372, 1000), lhand=(300, 905), relb=(530, 1000), rhand=(602, 905), look=(0.0, -0.45), swing=0.0)
ROLL = P(relb=(532, 1080), rhand=(575, 1018), roll=1.0, swing=0.4)
SHRUG = P(lelb=(392, 1078), lhand=(338, 1050), relb=(512, 1078), rhand=(566, 1050), tilt=0.07, look=(0.1, 0.1), swing=0.0)
POINT_UP = P(relb=(542, 1002), rhand=(612, 880), look=(0.75, -0.8), tilt=0.12, swing=0.0, finger=1.0)
PRESENT = P(lelb=(386, 1082), lhand=(330, 1062), relb=(516, 1082), rhand=(572, 1062), look=(0.0, 0.1), swing=0.0)
ONE = P(relb=(546, 1062), rhand=(558, 935), finger=1.0, look=(0.0, 0.0), swing=0.0)
READ = P(lelb=(398, 1112), lhand=(428, 1078), relb=(504, 1112), rhand=(478, 1078), look=(0.0, 0.7), tilt=-0.12,
         swing=0.0, letter=1.0)
SIT = P(head=(430, 1010), neck=(455, 1185), hip=(398, 1452),
        lelb=(505, 1305), lhand=(548, 1292), relb=(525, 1322), rhand=(566, 1286),
        lknee=(545, 1270), lfoot=(612, 1476), rknee=(570, 1284), rfoot=(642, FLOOR_Y),
        tilt=-0.16, look=(0.1, 0.55), swing=0.0)
SIT_UP = P(SIT, head=(442, 1004), tilt=0.16, look=(0.8, -0.8))
SIT_REACH = P(SIT_UP, relb=(600, 1205), rhand=(690, 1125))
SIT_CAM = P(SIT, head=(440, 1004), tilt=0.03, look=(0.0, 0.0))
SIT_WIDE = P(SIT_CAM, eyescale=1.12, tilt=0.0)


# window / world params (window sky is in colour and follows his eyes)
WIN = (690, 205, 300, 325)   # x, y, w, h (world)
def SKY(**kw):
    d = dict(top=(200, 206, 214), bot=(232, 235, 239), clouds=0.75, cloud_v=12.0, sun=0.0, sun_y=0.30,
             after=0.0, beam=0.0, stars=0.0, ripple=0.0, sparkle=0.0, echo=0.0, drone=0.35, shimmer=0.0,
             lift=0.0, roll=0.0, silver=0.0, mirror=0.0, mirror_eyes=(20, 150, 170),
             mirror_arm=0.0, mirror_tilt=0.0, rain=0.0, sun_r=34.0, win_scale=1.0,
             perch=0.0, perch_x=0.62, perch_tilt=0.0, perch_hop=0.0, perch_size=2.0,
             web=0.0, web_vis=1.0, web_glow=0.0, spider=0.0, spider_turn=math.pi / 2, spider_dy=0.0,
             prey=0.0, prey_struggle=0.0, prey_wrap=0.0, spider_to_prey=0.0, buzz=0.0,
             dark=0.0, snow=0.0, snow_pile=0.0, icicle=0.0, mirror_shut=0.0, web_torn=0.0, web_fall=0.0,
             crack=0.0, crack_vis=1.0, tape=0.0, tape_lift=0.0, tape_drop=0.0)
    d.update(kw); return d


# ------------------------------------------------------ episode configuration ---
mood_track = pose_track = x_track = cam_track = follow_track = env_track = None
WINDOW_KNOCKS = []
DURATION = 0.0
NFRAMES = 0
TALLY_BASE = 0          # marks already on the wall when the episode starts
TALLY_NEW = []          # [(start_time, seconds)] marks drawn on camera this episode
SFX = []                # [(time, kind, gain)] kind in {"scratch", "knock", "knock_far"}
POSE_HOOK = None
BLINKS = []
BIRDS = []   # [dict(t, dur, x0, x1, y)] in window-fraction coords; a little ink 'v' flapping across
WEB = None   # spider web geometry (see build_web); drawn when env "web" > 0
PLUCKS = []  # [(time, gain)] the web/dragline trembles (and thrums faintly) from these moments
DRAW_HOOK = None
DRIPS = []        # [time] icicle drips (env "icicle" > 0): a bead swells, falls, and plinks
GLASS_TAPS = []   # [(time, gain)] a knock from OUR side of the glass: dull tap + a tiny shake of the whole frame

def configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
              window_knocks=(), tally_base=0, tally_new=(), sfx=(), extra_blinks=(), pose_hook=None, tail=0.55,
              birds=(), web=None, plucks=(), draw_hook=None, lens_bugs=(), glass_taps=(), drips=(), crack=None):
    """Install an episode's timelines and precompute everything derived from them.
    draw_hook(cr, t, pose, env): episode-specific drawing in world space, right after Nigel is drawn."""
    g = globals()
    g["DRAW_HOOK"] = draw_hook
    g["LENS_BUGS"] = list(lens_bugs)
    g["GLASS_TAPS"] = list(glass_taps)
    g["DRIPS"] = list(drips)
    g["CRACK"] = build_crack(crack) if crack else None
    sfx = list(sfx) + [(k, "knock_far", 0.16) for b in lens_bugs for k in b.get("taps", [])]
    g.update(mood_track=mood_track, pose_track=pose_track, x_track=x_track, cam_track=cam_track,
             follow_track=follow_track, env_track=env_track, WINDOW_KNOCKS=list(window_knocks),
             TALLY_BASE=tally_base, TALLY_NEW=list(tally_new), SFX=list(sfx), POSE_HOOK=pose_hook, BIRDS=list(birds),
             WEB=build_web(web) if web else None, PLUCKS=list(plucks))
    g["DURATION"] = words[-1]["end"] + tail          # hard cut right after the last word
    g["NFRAMES"] = int(g["DURATION"] * FPS)
    # voice envelope (mouth + talking hands)
    global venv, venv_slow, nv
    hopn = SR // FPS
    nv = len(voice) // hopn
    venv = np.sqrt((voice[: nv * hopn].reshape(nv, hopn) ** 2).mean(1))
    venv = venv / (np.percentile(venv, 95) + 1e-9)
    venv = np.convolve(venv, [0.25, 0.5, 0.25], mode="same")
    venv_slow = np.convolve(venv, np.ones(9) / 9, mode="same")
    # blinks
    rng = random.Random(7)
    b, bt = [], 1.6
    while bt < g["DURATION"]:
        b.append(bt); bt += rng.uniform(2.4, 5.0)
    g["BLINKS"] = b + list(extra_blinks)
    # locomotion
    global _lx, _lv, _lph
    _lx = np.array([x_track.at((f - PRE) / FPS) for f in range(g["NFRAMES"] + PRE + 4)])
    _lv = np.gradient(_lx) * FPS
    _lph = np.cumsum(np.abs(_lv) / FPS / 92.0 * math.pi)
    # captions
    global CHUNKS
    CHUNKS = build_chunks()
    layout_chunks(CHUNKS)

venv = venv_slow = None
nv = 0
def mouth_open(t):
    i = int((t - VO) * FPS)
    if i < 0 or i >= nv:
        return 0.0
    return float(np.clip((venv[i] - 0.12) * 1.15, 0, 1))
def speech_energy(t):
    i = int((t - VO) * FPS)
    if i < 0 or i >= nv:
        return 0.0
    return float(np.clip(venv_slow[i], 0, 1.2))

def blink_amt(t):
    b = 0.0
    for t0 in BLINKS:
        d = t - t0
        if 0 <= d < 0.18:
            b = max(b, 1 - abs(d - 0.09) / 0.09)
    return b

# ------------------------------------------------- locomotion (precomputed) ---
PRE = 90   # frames of history before t=0 (for echo ghosts)
_lx = _lv = _lph = None

def loco(t):
    i = int(round(t * FPS)) + PRE
    i = min(max(i, 0), len(_lx) - 1)
    return _lx[i], _lv[i], _lph[i]

def live_pose(t):
    """pose + walking + speech beats, in world coordinates."""
    p = dict(pose_track.at(t))
    x, v, ph = loco(t)
    wk = min(1.0, abs(v) / 55.0)
    d = 1 if v >= 0 else -1
    sitting = p["hip"][1] > 1350
    if sitting:
        wk = 0.0
    if wk > 0.001:
        bob = 7 * abs(math.sin(ph)) * wk
        hipx, hipy = p["hip"]
        for side, off in (("l", 0.0), ("r", math.pi)):
            s = math.sin(ph + off)
            lift = max(0.0, math.cos(ph + off)) * 26
            foot = (hipx + 52 * s, FLOOR_Y - lift)
            knee = ((hipx + foot[0]) / 2 + d * 16, (hipy + FLOOR_Y) / 2 - lift * 0.4)
            p[side + "foot"] = lerp(p[side + "foot"], foot, wk)
            p[side + "knee"] = lerp(p[side + "knee"], knee, wk)
        sw = wk * p["swing"]
        if sw > 0.001:
            for side, off in (("l", math.pi), ("r", 0.0)):
                s = math.sin(ph + off)
                p[side + "hand"] = lerp(p[side + "hand"], (p[side + "hand"][0] + 34 * s, p[side + "hand"][1] - 6 * abs(s)), sw)
                p[side + "elb"] = lerp(p[side + "elb"], (p[side + "elb"][0] + 14 * s, p[side + "elb"][1]), sw)
        for k in ("head", "neck", "hip", "lelb", "relb", "lhand", "rhand"):
            p[k] = (p[k][0], p[k][1] + bob)
        p["look"] = (p["look"][0] + 0.45 * d * wk, p["look"][1])
        p["tilt"] += 0.05 * d * wk
    # talking: hands move a little with the voice (beat gestures)
    e = speech_energy(t)
    if not sitting:
        p["rhand"] = (p["rhand"][0] + e * 10 * math.sin(t * 2.3), p["rhand"][1] - e * 18)
        p["lhand"] = (p["lhand"][0] - e * 8 * math.sin(t * 1.9 + 1), p["lhand"][1] - e * 10)
    if p["roll"] > 0.01:
        p["rhand"] = (p["rhand"][0] + math.cos(t * 6.5) * 26 * p["roll"], p["rhand"][1] + math.sin(t * 6.5) * 20 * p["roll"])
    # the knock: fist swings in toward the glass
    push = sum(math.exp(-((t - k) / 0.085) ** 2) * KNOCK_GAIN.get(k, 1.0) for k in INTRO_KNOCKS) * p["fist"]
    p["push"] = push
    if push > 0.001:
        p["rhand"] = (p["rhand"][0] - 22 * push, p["rhand"][1] + 48 * push)
        p["relb"] = (p["relb"][0] - 10 * push, p["relb"][1] + 6 * push)
        p["head"] = (p["head"][0] + 4 * push, p["head"][1] + 6 * push)
    lift = env_track.at(t)["lift"]
    for k in ("head", "neck", "hip", "lelb", "lhand", "relb", "rhand", "lknee", "lfoot", "rknee", "rfoot"):
        p[k] = (p[k][0] + x, p[k][1] - lift)
    # drawing a tally mark: left hand follows the line as it's scratched in
    for i, (ts, dur) in enumerate(TALLY_NEW):
        w = smooth((t - ts + 0.35) / 0.35) * (1 - smooth((t - ts - dur) / 0.4))
        if w > 0.001:
            (ax, ay), (bx, by) = tally_mark(TALLY_BASE + i)
            u = smooth((t - ts) / dur)
            tip = (ax + (bx - ax) * u, ay + (by - ay) * u)
            sh = lerp(p["neck"], p["hip"], 0.14)
            elb = (tip[0] + 78, max(tip[1] + 62, sh[1] + 40))   # forearm comes in diagonally from his body
            p["lhand"] = lerp(p["lhand"], tip, w)
            p["lelb"] = lerp(p["lelb"], elb, w)
            p["look"] = lerp(p["look"], (-0.85, 0.15), w)
            p["tilt"] = lerp(p["tilt"], -0.12, w)
            p["scratch"] = max(p.get("scratch", 0.0), w)
    if POSE_HOOK:
        p = POSE_HOOK(t, p)
    return p

# --------------------------------------------------------------- tally ------
TALLY_XY = (95, 965)   # world: top-left of the tally block on the left wall
def tally_mark(i):
    """endpoints of mark i (0-based). Groups of five: four strokes + a diagonal."""
    g, k = divmod(i, 5)
    row, col = divmod(g, 4)
    gx, gy = TALLY_XY[0] + col * 92, TALLY_XY[1] + row * 150
    rr = random.Random(i * 31)
    if k < 4:
        x = gx + k * 17 + rr.uniform(-2, 2)
        return (x + rr.uniform(-3, 3), gy + rr.uniform(-4, 4)), (x + rr.uniform(-3, 3), gy + 104 + rr.uniform(-5, 5))
    return (gx - 10, gy + 82 + rr.uniform(-4, 4)), (gx + 66, gy + 18 + rr.uniform(-4, 4))

def draw_tally(cr, t):
    total = TALLY_BASE + len(TALLY_NEW)
    for i in range(total):
        (ax, ay), (bx, by) = tally_mark(i)
        u = 1.0
        if i >= TALLY_BASE:
            ts, dur = TALLY_NEW[i - TALLY_BASE]
            u = smooth((t - ts) / dur)
            if u <= 0:
                continue
        tip = (ax + (bx - ax) * u, ay + (by - ay) * u)
        path(cr, sketch_pts([(ax, ay), tip], amp=1.2, sid=200 + i, step=14)); stroke_ink(cr, 6.5)

# --------------------------------------------------------- sketch drawing ---
BOIL = 0
def wob(seed, k):
    return math.sin(k * 1.7 + seed * 12.9898 + BOIL * 3.1) * 0.5 + 0.5 * math.sin(k * 3.3 + seed * 4.1 + BOIL * 5.7)

def sketch_pts(pts, amp=2.0, sid=0, step=20):
    out = []
    for a in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[a], pts[a + 1]
        L = math.hypot(x1 - x0, y1 - y0) + 1e-6
        n = max(2, int(L / step))
        nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        for k in range(n + (1 if a == len(pts) - 2 else 0)):
            u = k / n
            o = amp * math.sin(u * math.pi + wob(sid + a, 1)) * wob(sid + a * 7, 2)
            o += amp * 0.5 * math.sin(u * math.pi * 3 + wob(sid, 3) * 3)
            out.append((x0 + (x1 - x0) * u + nx * o, y0 + (y1 - y0) * u + ny * o))
    return out

def path(cr, pts):
    cr.move_to(*pts[0])
    for p in pts[1:]:
        cr.line_to(*p)

def circle_pts(cx, cy, r, sid=0, n=72, amp=0.008):
    p1, p2 = wob(sid, 1) * 6, wob(sid, 2) * 6
    return [(cx + r * (1 + amp * math.sin(3 * a + p1) + amp * 0.6 * math.sin(5 * a + p2)) * math.cos(a),
             cy + r * (1 + amp * math.sin(3 * a + p1) + amp * 0.6 * math.sin(5 * a + p2)) * math.sin(a))
            for a in [2 * math.pi * i / n for i in range(n + 1)]]

def stroke_ink(cr, width, color=INK, alpha=1.0):
    cr.set_source_rgba(*color, alpha)
    cr.set_line_width(width)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.stroke()

# ------------------------------------------------------------ HD eyes ------
TEX = 512
def make_noise(seed, slope):
    n = np.random.default_rng(seed).standard_normal((TEX, TEX))
    k = np.sqrt(np.fft.fftfreq(TEX)[:, None] ** 2 + np.fft.fftfreq(TEX)[None, :] ** 2)
    filt = 1 / (k + 1.5 / TEX) ** slope
    filt[0, 0] = 0
    m = np.real(np.fft.ifft2(np.fft.fft2(n) * filt))
    m = (m - m.min()) / (m.max() - m.min())
    return m.astype(np.float32)
NEB1 = make_noise(11, 1.55)
NEB2 = make_noise(12, 1.35)
WARP = make_noise(13, 2.1)
_star_tab = np.random.default_rng(3).random((64, 512)).astype(np.float32)
_star_ph = np.random.default_rng(4).random((64, 512)).astype(np.float32) * 6.28

def samp(tex, u, v):
    x0 = np.floor(u); y0 = np.floor(v)
    fx = (u - x0).astype(np.float32); fy = (v - y0).astype(np.float32)
    x0 = x0.astype(np.int64) % TEX; y0 = y0.astype(np.int64) % TEX
    x1 = (x0 + 1) % TEX; y1 = (y0 + 1) % TEX
    a = tex[y0, x0] * (1 - fx) + tex[y0, x1] * fx
    b = tex[y1, x0] * (1 - fx) + tex[y1, x1] * fx
    return a * (1 - fy) + b * fy

_grid_cache = {}
def grid(px):
    if px not in _grid_cache:
        c = (np.arange(px) + 0.5) / px * 2 - 1
        X, Y = np.meshgrid(c, c)
        R = np.sqrt(X * X + Y * Y).astype(np.float32)
        TH = np.arctan2(Y, X).astype(np.float32)
        mask = np.clip((1 - R) * px / 2, 0, 1).astype(np.float32)
        ri = np.clip((R * 63).astype(int), 0, 63)
        ti = ((TH + math.pi) / (2 * math.pi) * 511).astype(int)
        logr = np.log(R + 0.035).astype(np.float32)
        _grid_cache[px] = (R, TH, mask, ri, ti, logr)
    return _grid_cache[px]

IRID = np.array([0.0, 0.33, 0.67], np.float32)
def eye_surface(px, t, rot, m, seed):
    """shimmering, morphing galaxy / kaleidoscope iris."""
    R, TH, mask, ri, ti, logr = grid(px)
    th = TH + rot + seed
    morph = 0.5 + 0.5 * math.sin(t * 0.23 + seed * 1.7)            # spiral <-> kaleidoscope
    twist = 2.2 + 0.9 * math.sin(t * 0.31 + seed)
    seg = 2 * math.pi / 6
    kal = np.abs(np.mod(th, seg) - seg / 2) / seg                     # mirrored wedge coordinate
    us = th / (2 * math.pi) * TEX * 2 + logr * TEX * 0.12 * twist
    vs = R * TEX * 0.55 - t * 22
    uk = kal * TEX * 0.9 + t * 6
    vk = logr * TEX * 0.22 - t * 40                                   # endless inward tunnel
    wv = samp(WARP, us * 0.4 + t * 9, vs * 0.4) * 70
    n1 = samp(NEB1, us + wv, vs + wv)
    n2 = samp(NEB2, uk + wv * 0.6, vk + wv * 0.6)
    neb = n1 * (1 - morph) + n2 * morph
    arms = (0.5 + 0.5 * np.cos(2 * th + 6.5 * logr)) ** 2
    core = np.exp(-(R / 0.15) ** 2) * (0.85 + 0.15 * math.sin(t * 3.1 + seed))
    inten = np.clip((neb - 0.25) * 1.5 + arms * 0.3 * (1 - R) + core * 0.9, 0, 1)
    p0, p1, p2 = (np.array(rgb(m[k]), np.float32) for k in ("p0", "p1", "p2"))
    i3 = inten[..., None]
    col = np.where(i3 < 0.5, p0 + (p1 - p0) * (i3 * 2), p1 + (p2 - p1) * ((i3 - 0.5) * 2))
    irid = 0.5 + 0.5 * np.cos(2 * math.pi * ((neb * 1.4 + R * 1.3 - t * 0.22)[..., None] + IRID))
    col = col * 0.74 + irid * (0.30 * inten)[..., None]
    col = col + np.array(rgb(m["acc"]), np.float32) * ((n2 ** 4) * 0.7 * R)[..., None]
    shift = int(rot / (2 * math.pi) * 512 * 0.6)
    st = (_star_tab[ri, (ti + shift) % 512] > 0.985)
    tw = 0.55 + 0.45 * np.sin(t * 9 + _star_ph[ri, (ti + shift) % 512])
    col = col + (st * tw * (1 - R) * 1.4)[..., None]
    limbal = np.clip((R - 0.8) / 0.2, 0, 1) ** 1.4                  # dark ring like a real iris
    col = col * (1 - 0.9 * limbal)[..., None]
    col = np.clip(col, 0, 1) * mask[..., None]
    arr = np.empty((px, px, 4), np.uint8)
    arr[..., 0] = col[..., 2] * 255
    arr[..., 1] = col[..., 1] * 255
    arr[..., 2] = col[..., 0] * 255
    arr[..., 3] = mask * 255
    arr = np.ascontiguousarray(arr)
    return cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_ARGB32, px, px, px * 4), arr

def catchlight(cr, er):
    """glossy highlights: a tiny reflection of the window + a soft dot. Makes him feel alive."""
    cr.set_source_rgba(1, 1, 1, 0.92)
    x0, y0, s = er * 0.18, -er * 0.62, er * 0.17
    for dx in (0, 1):
        for dy in (0, 1):
            cr.rectangle(x0 + dx * (s + er * 0.035), y0 + dy * (s * 1.1 + er * 0.035), s, s * 1.1)
    cr.fill()
    cr.set_source_rgba(1, 1, 1, 0.55)
    cr.arc(-er * 0.45, er * 0.45, er * 0.08, 0, 2 * math.pi); cr.fill()

# --------------------------------------------------------------- Nigel -----
HEAD_R = 170
EYE_R = 70
EYES = [(-68, -6, 0.0), (68, -6, 2.1)]   # x, y, galaxy seed (head frame)

def draw_nigel(cr, t, p, mood, zoom, rot, mouth, blink, ghost=False):
    g = lambda k: p[k]
    blink = max(blink, p.get("shut", 0.0))   # eyes held shut
    hx, hy = g("head")
    breath = math.sin(t * 1.6) * 3.0
    hy += breath
    nk = (g("neck")[0], g("neck")[1] + breath * 0.5)
    hip = g("hip")
    sh = lerp(nk, hip, 0.14)
    limbs = [[hip, g("lknee"), g("lfoot")], [hip, g("rknee"), g("rfoot")], [nk, hip],
             [sh, g("lelb"), g("lhand")], [sh, g("relb"), g("rhand")]]
    rv = p.get("reveal", 1.0)
    def part(a, b): return min(1.0, max(0.0, (rv - a) / (b - a)))
    body_u = part(0.5, 1.0)          # being drawn: head (0-.3) -> eyes (.3-.45) -> body (.5-1)
    cr.save()
    if rv < 1.0:
        cr.rectangle(-5000, -5000, 10000, 5000 + nk[1] - 8 + body_u * (FLOOR_Y + 30 - nk[1]))
        cr.clip()
    for i, l in enumerate(limbs):
        path(cr, sketch_pts(l, amp=1.8, sid=11 + i * 5)); stroke_ink(cr, 9)
    path(cr, sketch_pts([nk, (hx + 2, hy + HEAD_R - 6)], amp=1, sid=9)); stroke_ink(cr, 9)
    if p.get("scratch", 0) > 0.05:   # little fist pressed to the wall while he scratches a mark
        x, y = g("lhand")
        cr.arc(x + 4, y + 2, 11 * p["scratch"], 0, 2 * math.pi)
        cr.set_source_rgb(*PAPER); cr.fill_preserve(); stroke_ink(cr, 5.5)
    if p["finger"] > 0.05:
        x, y = g("rhand")
        ex, ey = g("relb")
        dx, dy = x - ex, y - ey
        L = math.hypot(dx, dy) + 1e-6
        cr.move_to(x, y); cr.line_to(x + dx / L * 34 * p["finger"], y + dy / L * 34 * p["finger"]); stroke_ink(cr, 7)
    if p["letter"] > 0.05:
        lx_, ly_ = lerp(g("lhand"), g("rhand"), 0.5)
        cr.save(); cr.translate(lx_, ly_ - 18); cr.rotate(-0.08)
        a = p["letter"]
        cr.rectangle(-46, -30, 92, 60); cr.set_source_rgba(*PAPER, a); cr.fill_preserve(); stroke_ink(cr, 5, alpha=a)
        cr.move_to(-46, -30); cr.line_to(0, 4); cr.line_to(46, -30); stroke_ink(cr, 4, alpha=a)
        cr.restore()
    cr.restore()   # end body clip
    # ---- head (flat white, ink outline)
    head_u, eye_u = part(0.0, 0.3), part(0.3, 0.45)
    cr.save()
    cr.translate(hx, hy)
    cr.rotate(g("tilt"))
    hp = circle_pts(0, 0, HEAD_R, sid=3, amp=0.007)
    if head_u < 1.0:   # the outline being drawn round, like a pen
        if head_u > 0.0:
            path(cr, hp[:max(2, int(len(hp) * head_u))]); stroke_ink(cr, 8)
    else:
        path(cr, hp)
        cr.set_source_rgb(*PAPER); cr.fill_preserve(); stroke_ink(cr, 8)
    if eye_u < 1.0:
        cr.push_group()
    sway = math.sin(t * 1.1) * 0.04 + (p["look"][0] * -0.05)
    for i, (a0, ln, bend) in enumerate([(3.55, 115, 0.45), (3.75, 145, 0.55), (3.95, 100, 0.35)]):
        a = a0 + sway
        x0, y0 = HEAD_R * math.cos(a) * 0.98, HEAD_R * math.sin(a) * 0.98
        cr.move_to(x0, y0)
        cr.curve_to(x0 - 38, y0 - 10 - i * 6, x0 - 66 - bend * 30, y0 + ln * 0.4, x0 - 56 - bend * 40 + wob(i, 4) * 3, y0 + ln)
        stroke_ink(cr, 4)
    lx, ly = p["look"]
    fx, fy = lx * 14, ly * 16
    er = EYE_R * p["eyescale"]
    for i, (ex, ey, seed) in enumerate(EYES):
        ex += fx; ey += fy
        cr.save()
        cr.translate(ex, ey)
        cr.save()
        cr.scale(1, max(0.04, 1 - blink))
        if ghost:
            cr.arc(0, 0, er, 0, 2 * math.pi); cr.set_source_rgb(0.75, 0.75, 0.78); cr.fill()
        else:
            px = max(16, int(2 * er * zoom) // 4 * 4)
            surf, _keep = eye_surface(px, t, rot * (1 if i else -1.12), mood, seed)
            cr.save()
            cr.translate(-er, -er); cr.scale(2 * er / px, 2 * er / px)
            cr.set_source_surface(surf, 0, 0); cr.paint()
            cr.restore()
            catchlight(cr, er)
        path(cr, circle_pts(0, 0, er, sid=50 + i, n=48, amp=0.01))
        cr.restore()
        stroke_ink(cr, 5.5)
        if blink > 0.35:
            cr.move_to(-er, 0); cr.curve_to(-er * 0.4, er * 0.2, er * 0.4, er * 0.2, er, 0); stroke_ink(cr, 5)
        cr.restore()
    # brows: soft, inner ends lift (sympathetic)
    b = mood["brow"]
    for i, (ex, ey, _) in enumerate(EYES):
        ex += fx; ey += fy
        side = 1 if i else -1
        inner = (ex - side * er * 0.55, ey - er - 20 - b * 16)
        outer = (ex + side * er * 0.6, ey - er - 14 + b * 6)
        mid = ((inner[0] + outer[0]) / 2, min(inner[1], outer[1]) - 7)
        cr.move_to(*inner); cr.curve_to(mid[0], mid[1], mid[0], mid[1], *outer)
        stroke_ink(cr, 5.5)
    # mouth: small and soft
    mx, my = fx * 0.6, 108 + fy * 0.5
    fr = mood["frown"]
    w = 40 - mouth * 6
    bot = my + fr * 8 + mouth * 22
    cr.move_to(mx - w / 2, my + fr * 6)
    cr.curve_to(mx - w / 4, my - fr * 10, mx + w / 4, my - fr * 10, mx + w / 2, my + fr * 6)
    if mouth > 0.06:
        cr.curve_to(mx + w / 4, bot, mx - w / 4, bot, mx - w / 2, my + fr * 6)
        cr.close_path()
        cr.set_source_rgb(*INK); cr.fill_preserve()
    stroke_ink(cr, 5)
    if eye_u < 1.0:   # hair, eyes and face fade in after the outline
        cr.pop_group_to_source(); cr.paint_with_alpha(eye_u)
    cr.restore()
    if p["fist"] > 0.02:
        x, y = g("rhand")
        path(cr, sketch_pts([g("relb"), (x, y)], amp=1.5, sid=27)); stroke_ink(cr, 9 + 3 * p["push"])
        fr = (26 + 40 * p["push"]) * p["fist"]
        lw = 6.5 + 4 * p["push"]
        cr.save(); cr.translate(x, y); cr.rotate(-0.15)
        # palm block + four knuckle bumps along the top, facing the viewer
        cr.move_to(-fr, -fr * 0.35)
        for k in range(4):
            x0 = -fr + k * fr * 0.5
            cr.curve_to(x0, -fr * 0.68, x0 + fr * 0.5, -fr * 0.68, x0 + fr * 0.5, -fr * 0.35)
        cr.curve_to(fr * 1.1, fr * 0.2, fr * 0.9, fr * 0.85, fr * 0.3, fr * 0.85)
        cr.line_to(-fr * 0.6, fr * 0.85)
        cr.curve_to(-fr * 1.1, fr * 0.8, -fr * 1.15, fr * 0.1, -fr, -fr * 0.35)
        cr.close_path()
        cr.set_source_rgb(*PAPER); cr.fill_preserve(); stroke_ink(cr, lw)
        for k in range(1, 4):   # finger creases
            xx = -fr + k * fr * 0.5
            cr.move_to(xx, -fr * 0.3); cr.line_to(xx - fr * 0.05, fr * 0.15); stroke_ink(cr, lw * 0.55)
        cr.move_to(-fr * 0.9, fr * 0.25); cr.curve_to(-fr * 0.3, fr * 0.1, fr * 0.2, fr * 0.2, fr * 0.5, fr * 0.45)
        stroke_ink(cr, lw * 0.6)   # thumb
        cr.restore()
    if p.get("palm", 0) > 0.02:   # open hand flat against the glass, facing the viewer (drawn over the head)
        x, y = g("rhand")
        path(cr, sketch_pts([g("relb"), (x, y)], amp=1.5, sid=29)); stroke_ink(cr, 9)
        fr = 40 * p["palm"]
        cr.save(); cr.translate(x, y); cr.rotate(-0.12)
        def capsule(x0, y0, ang, ln, wd):
            cr.save(); cr.translate(x0, y0); cr.rotate(ang)
            cr.move_to(-wd / 2, 0); cr.line_to(-wd / 2, -ln + wd / 2)
            cr.arc(0, -ln + wd / 2, wd / 2, math.pi, 2 * math.pi)
            cr.line_to(wd / 2, 0); cr.close_path(); cr.restore()
            cr.set_source_rgb(*PAPER); cr.fill_preserve(); stroke_ink(cr, 5.5)
        for fx_, ln, ang in [(-0.6, 0.95, -0.2), (-0.2, 1.18, -0.07), (0.2, 1.12, 0.06), (0.6, 0.9, 0.2)]:
            capsule(fx_ * fr, -0.55 * fr, ang, ln * fr, 0.36 * fr)
        capsule(-0.75 * fr, 0.25 * fr, -1.05, 0.8 * fr, 0.38 * fr)          # thumb
        cr.save(); cr.scale(1.0, 1.05); cr.arc(0, 0, fr * 0.92, 0, 2 * math.pi); cr.restore()
        cr.set_source_rgb(*PAPER); cr.fill_preserve(); stroke_ink(cr, 6)
        cr.restore()

# ------------------------------------------------------------- window ------
CLOUDS = [(0.15, 0.25, 1.0), (0.65, 0.18, 0.8), (0.95, 0.45, 1.2), (0.40, 0.55, 0.7)]
STARS = [(random.Random(i).random(), random.Random(i + 999).random() * 0.85, random.Random(i + 77).random())
         for i in range(150)]
STARS[0] = (0.62, 0.30, 0.5)

def window_interior(t, env, zoom, cloud_off, mood=None):
    _, _, ww, wh = WIN
    pw, ph = max(8, int(ww * zoom)), max(8, int(wh * zoom))
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, pw, ph)
    c = cairo.Context(s)
    c.scale(pw / ww, ph / wh)
    gr = cairo.LinearGradient(0, 0, 0, wh)
    gr.add_color_stop_rgb(0, *rgb(env["top"])); gr.add_color_stop_rgb(1, *rgb(env["bot"]))
    c.set_source(gr); c.paint()
    if env["stars"] > 0.001:
        n = max(1, int(env["stars"] * len(STARS)))
        for i, (sx, sy, ph_) in enumerate(STARS[:n]):
            tw = 0.6 + 0.4 * math.sin(t * (2 + ph_ * 3) + ph_ * 10)
            rad = (3.2 if i == 0 else 1.1 + ph_ * 1.4) * (1 + 0.3 * env["shimmer"])
            if i == 0:
                gl = cairo.RadialGradient(sx * ww, sy * wh, 0, sx * ww, sy * wh, 22)
                gl.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.5 * tw); gl.add_color_stop_rgba(1, 1, 1, 1, 0)
                c.set_source(gl); c.arc(sx * ww, sy * wh, 22, 0, 2 * math.pi); c.fill()
            c.set_source_rgba(1, 0.97, 0.88, tw)
            c.arc(sx * ww, sy * wh, rad, 0, 2 * math.pi); c.fill()
    sx, sy = ww * 0.58, wh * env["sun_y"]
    if env["sun"] > 0.01:
        sr = env["sun_r"]
        gl = cairo.RadialGradient(sx, sy, sr * 0.3, sx, sy, sr * 3.5)
        gl.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.9 * env["sun"]); gl.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
        c.set_source(gl); c.arc(sx, sy, sr * 3.5, 0, 2 * math.pi); c.fill()
        c.set_source_rgba(1, 0.98, 0.86, env["sun"]); c.arc(sx, sy, sr, 0, 2 * math.pi); c.fill()
    if env["after"] > 0.01:   # the sun is gone; its ghost stays (you only ever see old light)
        c.set_source_rgba(0.4, 0.9, 0.95, 0.55 * env["after"])
        c.set_line_width(3); c.arc(sx + 6, sy + 4, 34, 0, 2 * math.pi); c.stroke()
        c.set_source_rgba(0.6, 0.4, 0.95, 0.35 * env["after"])
        c.arc(sx - 5, sy - 3, 36, 0, 2 * math.pi); c.stroke()
    if env["clouds"] > 0.01:
        for i, (cx0, cy0, sc) in enumerate(CLOUDS):
            span = ww + 260
            cx = ((cx0 * span + cloud_off * (0.7 + 0.3 * sc)) % span) - 130
            cy = cy0 * wh
            c.set_source_rgba(1, 1, 1, 0.85 * env["clouds"])
            for dx, dy, rr in [(-40, 8, 30), (-10, -10, 38), (28, 0, 32), (55, 12, 22), (5, 14, 30)]:
                c.arc(cx + dx * sc, cy + dy * sc, rr * sc, 0, 2 * math.pi); c.fill()
    for b in BIRDS:
        u = (t - b["t"]) / b["dur"]
        if 0 <= u <= 1:
            bx = ww * (b["x0"] + (b["x1"] - b["x0"]) * u)
            by = wh * b["y"] + 6 * math.sin(u * 9)
            flap = math.sin(t * 22) * 0.6
            sz = b.get("size", 9)
            c.move_to(bx - sz, by - sz * (0.3 + flap)); c.line_to(bx, by); c.line_to(bx + sz, by - sz * (0.3 + flap))
            c.set_source_rgba(0.12, 0.12, 0.14, 0.95); c.set_line_width(2.6); c.stroke()
    if env["perch"] > 0.01:   # the bird, sitting on the outside ledge at the bottom of the window
        a = env["perch"]
        bx, by = ww * env["perch_x"], wh - 6 - 14 * env["perch_hop"]
        c.save(); c.translate(bx, by); c.scale(env['perch_size'], env['perch_size'])
        c.set_source_rgba(0.1, 0.1, 0.12, a); c.set_line_width(2.4)
        c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.save(); c.translate(0, -16); c.scale(1.35, 1.0)                     # body
        c.arc(0, 0, 11, 0, 2 * math.pi); c.restore()
        c.set_source_rgba(*PAPER, a); c.fill_preserve(); c.set_source_rgba(0.1, 0.1, 0.12, a); c.stroke()
        c.move_to(-13, -18); c.line_to(-26, -24); c.line_to(-24, -14); c.close_path()   # tail
        c.set_source_rgba(*PAPER, a); c.fill_preserve(); c.set_source_rgba(0.1, 0.1, 0.12, a); c.stroke()
        c.move_to(-3, -5); c.line_to(-4, 2); c.move_to(4, -5); c.line_to(5, 2); c.stroke()   # legs
        c.save(); c.translate(10, -30); c.rotate(env["perch_tilt"])          # head tilts (copies him later)
        c.arc(0, 0, 7.5, 0, 2 * math.pi)
        c.set_source_rgba(*PAPER, a); c.fill_preserve(); c.set_source_rgba(0.1, 0.1, 0.12, a); c.stroke()
        c.move_to(7, -1); c.line_to(14, 1); c.line_to(7, 3); c.stroke()          # beak
        c.arc(2.5, -1.5, 1.6, 0, 2 * math.pi); c.fill()                          # eye
        c.restore()
        c.move_to(-8, -15); c.curve_to(-2, -10, 5, -10, 9, -14); c.stroke()       # wing line
        c.restore()
    if env["rain"] > 0.01:   # slanted rain streaks
        rr = random.Random(5)
        c.set_line_width(1.6)
        for k in range(int(70 * env["rain"])):
            x0 = rr.uniform(-40, ww + 20); sp = rr.uniform(260, 380); ph = rr.uniform(0, wh + 60)
            y0 = (ph + t * sp) % (wh + 60) - 30
            c.move_to(x0 + y0 * 0.25, y0); c.line_to(x0 + y0 * 0.25 + 5, y0 + 20)
            c.set_source_rgba(0.92, 0.95, 1.0, 0.55 * env["rain"]); c.stroke()
    if env["snow"] > 0.01:   # snow falling outside: soft flakes drifting down, swaying
        rr = random.Random(11)
        for k in range(int(90 * env["snow"])):
            x0 = rr.uniform(-20, ww + 20); sp = rr.uniform(28, 55); ph = rr.uniform(0, wh + 40); r0 = rr.uniform(1.6, 3.6)
            y0 = (ph + t * sp) % (wh + 40) - 20
            x = x0 + 9 * math.sin(t * rr.uniform(0.6, 1.4) + k)
            c.set_source_rgba(1, 1, 1, 0.85 * env["snow"]); c.arc(x, y0, r0, 0, 2 * math.pi); c.fill()
    if env["snow_pile"] > 0.01:   # snow piled on the outside ledge, along the bottom of the glass
        hgt = 66 * env["snow_pile"]
        c.move_to(-5, wh + 2)
        for k in range(13):
            u = k / 12
            c.line_to(u * ww, wh - hgt * (0.75 + 0.25 * math.sin(u * 7.3 + 1.1)))
        c.line_to(ww + 5, wh + 2); c.close_path()
        c.set_source_rgba(0.97, 0.98, 1.0, 0.97); c.fill_preserve()
        c.set_source_rgba(0.72, 0.78, 0.88, 0.8); c.set_line_width(1.6); c.stroke()
    if env["icicle"] > 0.01:   # an icicle hanging from the top of the frame, dripping
        ix, L = ww * 0.66, 135 * env["icicle"]
        c.move_to(ix - 15, -2); c.curve_to(ix - 11, L * 0.4, ix - 4, L * 0.8, ix, L)
        c.curve_to(ix + 4, L * 0.8, ix + 11, L * 0.4, ix + 15, -2); c.close_path()
        c.set_source_rgba(0.80, 0.89, 1.0, 0.97); c.fill_preserve()
        c.set_source_rgba(0.30, 0.42, 0.62, 0.95); c.set_line_width(2.4); c.stroke()
        c.move_to(ix - 6, 6); c.line_to(ix - 1.5, L * 0.72); c.set_source_rgba(1, 1, 1, 0.95); c.set_line_width(2.2); c.stroke()
        for d in DRIPS:
            grow = smooth((t - (d - 0.7)) / 0.7) if t < d else 0.0     # a bead swells at the tip...
            if grow > 0.02:
                c.arc(ix, L + 4 * grow, 4.6 * grow, 0, 2 * math.pi); c.set_source_rgba(0.7, 0.84, 1.0, 0.97); c.fill_preserve(); c.set_source_rgba(0.3, 0.42, 0.62, 0.8); c.set_line_width(1.2); c.stroke()
            u = (t - d) / 0.5                                            # ...and falls
            if 0 <= u < 1:
                c.save(); c.translate(ix, L + 3 + (wh - L) * u * u); c.scale(1, 1.5)
                c.arc(0, 0, 4.6, 0, 2 * math.pi); c.restore(); c.set_source_rgba(0.7, 0.84, 1.0, 0.97 * (1 - u * 0.3)); c.fill()
    if env["silver"] > 0.01:   # the glass going mirror-like
        sg = cairo.LinearGradient(0, 0, ww, wh)
        sg.add_color_stop_rgba(0, 0.93, 0.94, 0.96, 0.85 * env["silver"])
        sg.add_color_stop_rgba(0.5, 0.78, 0.80, 0.84, 0.85 * env["silver"])
        sg.add_color_stop_rgba(1, 0.95, 0.95, 0.97, 0.85 * env["silver"])
        c.set_source(sg); c.paint()
    if env["mirror"] > 0.01:   # a small reflected Nigel looking back out at him
        a = env["mirror"]
        mx, my, hr = ww * 0.5, wh * 0.42, 46
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_source_rgba(*INK, a); c.set_line_width(4)
        c.move_to(mx, my + hr); c.line_to(mx, wh + 5); c.stroke()
        c.move_to(mx, my + hr + 30); c.line_to(mx - 34, my + hr + 85); c.stroke()
        ma = env["mirror_arm"]
        c.move_to(mx, my + hr + 30); c.line_to(mx + 34 + 18 * ma, my + hr + 85 - 150 * ma); c.stroke()
        c.save(); c.translate(mx, my); c.rotate(env["mirror_tilt"]); c.translate(-mx, -my)
        c.arc(mx, my, hr, 0, 2 * math.pi); c.set_source_rgba(*PAPER, a); c.fill_preserve()
        c.set_source_rgba(*INK, a); c.stroke()
        ec = rgb(env["mirror_eyes"])
        for ex in (-19, 19):
            if env["mirror_shut"] > 0.5:   # the reflection's eyes close when his do
                c.move_to(mx + ex - 17, my - 2); c.curve_to(mx + ex - 7, my + 3, mx + ex + 7, my + 3, mx + ex + 17, my - 2)
                c.set_source_rgba(*INK, a); c.set_line_width(2.5); c.stroke()
                continue
            gr = cairo.RadialGradient(mx + ex, my - 2, 1, mx + ex, my - 2, 18)
            gr.add_color_stop_rgba(0, min(1, ec[0] + 0.4), min(1, ec[1] + 0.4), min(1, ec[2] + 0.4), a)
            gr.add_color_stop_rgba(1, ec[0] * 0.4, ec[1] * 0.4, ec[2] * 0.4, a)
            c.set_source(gr); c.arc(mx + ex, my - 2, 17, 0, 2 * math.pi); c.fill()
            c.set_source_rgba(*INK, a); c.set_line_width(2.5); c.arc(mx + ex, my - 2, 17, 0, 2 * math.pi); c.stroke()
        c.set_source_rgba(1, 1, 1, 0.8 * a); c.rectangle(mx + 22, my - 13, 5, 5); c.fill()
        c.rectangle(mx - 16, my - 13, 5, 5); c.fill()
        for k in range(3):   # hair
            c.move_to(mx - hr * 0.9, my - hr * 0.35 + k * 4)
            c.curve_to(mx - hr * 1.2, my - hr * 0.4, mx - hr * 1.35, my, mx - hr * 1.3 + k * 3, my + hr * 0.5)
            c.set_source_rgba(*INK, a); c.set_line_width(1.6); c.stroke()
        c.restore()
    s.flush()
    if env["ripple"] > 0.01:   # glass going thin: the sky wobbles like water
        a = np.ndarray((ph, s.get_stride() // 4, 4), np.uint8, s.get_data())[:, :pw].copy()
        yy, xx = np.mgrid[0:ph, 0:pw]
        amp = env["ripple"] * 10 * zoom
        dx = (amp * np.sin(yy / (13 * zoom) + t * 7) + amp * 0.6 * np.sin((xx + yy) / (23 * zoom) - t * 5)).astype(int)
        dy = (amp * 0.7 * np.sin(xx / (17 * zoom) - t * 6)).astype(int)
        a = np.ascontiguousarray(a[np.clip(yy + dy, 0, ph - 1), np.clip(xx + dx, 0, pw - 1)])
        return cairo.ImageSurface.create_for_data(memoryview(a), cairo.FORMAT_ARGB32, pw, ph, pw * 4), a
    return s, None

def draw_window(cr, t, env, zoom, cloud_off, shake):
    x, y, ww, wh = WIN
    sc = env["win_scale"]
    x, y, ww, wh = x + ww * (1 - sc) / 2, y + wh * (1 - sc) / 2, ww * sc, wh * sc
    x += shake[0]; y += shake[1]
    s, _keep = window_interior(t, env, zoom, cloud_off)
    cr.save()
    cr.rectangle(x, y, ww, wh); cr.clip()
    cr.translate(x, y); cr.scale(ww / s.get_width(), wh / s.get_height())
    cr.set_source_surface(s, 0, 0); cr.paint()
    cr.restore()
    cr.set_source_rgba(1, 1, 1, 0.35)
    cr.set_line_width(6)
    cr.move_to(x + 30, y + 120); cr.line_to(x + 95, y + 40); cr.stroke()
    cr.set_line_width(3)
    cr.move_to(x + 48, y + 140); cr.line_to(x + 108, y + 66); cr.stroke()
    o = 10
    for k, seg in enumerate([[(x - o, y), (x + ww + o, y)], [(x - o, y + wh), (x + ww + o, y + wh)],
                             [(x, y - o), (x, y + wh + o)], [(x + ww, y - o), (x + ww, y + wh + o)]]):
        path(cr, sketch_pts(seg, amp=1.6, sid=70 + k)); stroke_ink(cr, 8)
    path(cr, sketch_pts([(x + ww / 2, y), (x + ww / 2, y + wh)], amp=1.4, sid=80)); stroke_ink(cr, 6)
    path(cr, sketch_pts([(x, y + wh * 0.46), (x + ww, y + wh * 0.46)], amp=1.4, sid=81)); stroke_ink(cr, 6)
    path(cr, sketch_pts([(x - 28, y + wh + 18), (x + ww + 28, y + wh + 18)], amp=1.5, sid=82)); stroke_ink(cr, 7)
    path(cr, sketch_pts([(x - 20, y + wh + 30), (x + ww + 20, y + wh + 30)], amp=1.5, sid=83)); stroke_ink(cr, 3, alpha=0.5)

def draw_beam(cr, env):
    if env["beam"] < 0.01:
        return
    x, y, ww, wh = WIN
    g = cairo.LinearGradient(x + ww, y + wh, 300, FLOOR_Y)
    g.add_color_stop_rgba(0, 1.0, 0.86, 0.45, 0.30 * env["beam"])
    g.add_color_stop_rgba(1, 1.0, 0.80, 0.45, 0.06 * env["beam"])
    cr.move_to(x + 6, y + wh); cr.line_to(x + ww, y + wh)
    cr.line_to(720, FLOOR_Y + 4); cr.line_to(150, FLOOR_Y + 4); cr.close_path()
    cr.set_source(g); cr.fill()
    cr.save(); cr.translate(430, FLOOR_Y + 12); cr.scale(1, 0.12)
    pg = cairo.RadialGradient(0, 0, 0, 0, 0, 300)
    pg.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.35 * env["beam"]); pg.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
    cr.set_source(pg); cr.arc(0, 0, 300, 0, 2 * math.pi); cr.fill(); cr.restore()

SPARKS = [(random.Random(i * 3).random(), random.Random(i * 5 + 1).random(), random.Random(i * 7 + 2).random())
          for i in range(46)]
def draw_sparkles(cr, t, amt):
    if amt < 0.01:
        return
    for i, (a, b, c) in enumerate(SPARKS):
        life = (t * (0.025 + 0.02 * c) + a) % 1.0
        x = 980 - life * (700 + 300 * b) + math.sin(t * 0.7 + i) * 20
        y = 330 + life * (900 + 300 * c) + math.cos(t * 0.5 + i) * 15
        al = amt * math.sin(life * math.pi) * (0.55 + 0.45 * math.sin(t * 3 + i))
        s = 5 + 7 * c
        cr.set_source_rgba(1, 0.82, 0.45, max(0, al))
        cr.move_to(x, y - s); cr.line_to(x + s * 0.22, y - s * 0.22); cr.line_to(x + s, y)
        cr.line_to(x + s * 0.22, y + s * 0.22); cr.line_to(x, y + s); cr.line_to(x - s * 0.22, y + s * 0.22)
        cr.line_to(x - s, y); cr.line_to(x - s * 0.22, y - s * 0.22); cr.close_path(); cr.fill()

# ------------------------------------------------------------ spider web ---
# Episode passes web=dict(hub=(x,y), frame=[(x,y)...] (polygon around the hub, in order), anchors=[(x,y)|None...]
# (one per frame vertex: where its mooring thread goes; a point marked by "fade" ends in nothing), fade=[i...],
# dragline=((x,y),(x,y)) or None, spokes=11, turns=8, spider_size=1.2).
# env: web 0..1 build progress (0-.3 spokes, .3-1 sticky spiral, spider walks the drawing end), web_vis (alpha),
# web_glow (light hitting it: gold lines + dew), spider (alpha), spider_turn (head angle at the hub; pi/2 = head
# down), spider_dy (small step off the hub). PLUCKS make the whole thing tremble.
def _ray_poly(o, d, poly):
    best = None
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % len(poly)]
        ex, ey = bx - ax, by - ay
        den = d[0] * ey - d[1] * ex
        if abs(den) < 1e-9:
            continue
        s = ((ax - o[0]) * ey - (ay - o[1]) * ex) / den
        u = ((ax - o[0]) * d[1] - (ay - o[1]) * d[0]) / den
        if s > 0 and -1e-6 <= u <= 1 + 1e-6 and (best is None or s < best):
            best = s
    return best or 50.0

def build_web(spec):
    w = dict(spokes=11, turns=8, spider_size=1.2, fade=[], anchors=None, dragline=None)
    w.update(spec)
    hx, hy = w["hub"]
    rr = random.Random(17)
    dirs, lens = [], []
    for i in range(w["spokes"]):
        a = 2 * math.pi * i / w["spokes"] + rr.uniform(-0.12, 0.12)
        d = (math.cos(a), math.sin(a))
        dirs.append(d); lens.append(_ray_poly((hx, hy), d, w["frame"]))
    w["dirs"], w["lens"] = dirs, lens
    K = w["turns"] * w["spokes"]
    w["spiral"] = []
    for k in range(K + 1):
        i = k % w["spokes"]
        f = 0.9 - 0.72 * k / K
        w["spiral"].append((i, f))
    return w

def web_tremble(t):
    a = 0.0
    for tp, gain in PLUCKS:
        if t >= tp:
            a += gain * math.exp(-(t - tp) / 0.45)
    return a

def draw_spider(cr, x, y, ang, size, alpha, t, busy):
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(size, size)
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.set_source_rgba(*INK, alpha); cr.set_line_width(3.0)
    for side in (-1, 1):
        for k, (a0, l1, l2) in enumerate([(0.55, 20, 24), (1.05, 19, 22), (1.9, 18, 21), (2.5, 21, 25)]):
            tw = 0.08 * math.sin(t * 9 + k * 1.7 + side) * busy
            a = side * (a0 + tw)
            rx, ry = 3 + 2.5 * k - 6, side * 4
            kx, ky = rx + l1 * math.cos(a), ry + l1 * math.sin(a)
            bend = a + side * (0.9 if k < 2 else -0.9) * (1 if k < 2 else 1)
            fx, fy = kx + l2 * math.cos(bend - side * 0.5), ky + l2 * math.sin(bend - side * 0.5)
            cr.move_to(rx, ry); cr.line_to(kx, ky); cr.line_to(fx, fy); cr.stroke()
    cr.save(); cr.translate(-15, 0); cr.scale(1.25, 1.0); cr.arc(0, 0, 12, 0, 2 * math.pi); cr.restore()
    cr.fill()
    cr.save(); cr.translate(6, 0); cr.scale(1.15, 1.0); cr.arc(0, 0, 7, 0, 2 * math.pi); cr.restore()
    cr.fill()
    cr.set_source_rgba(*PAPER, 0.55 * alpha)   # a faint mark on her back so she reads as a body, not a blot
    cr.move_to(-22, 0); cr.line_to(-9, 0); cr.set_line_width(1.6); cr.stroke()
    cr.restore()

def draw_prey(cr, t, env, pos, kind, size):
    """something caught in the web: a fly / moth (struggling) cross-fading into a silk-wrapped bundle"""
    a, st, wr = env["prey"], env["prey_struggle"], env["prey_wrap"]
    x, y = pos
    x += st * 2.5 * math.sin(t * 37) + st * 1.5 * math.sin(t * 23 + 1)
    y += st * 2.0 * math.cos(t * 31)
    cr.save(); cr.translate(x, y); cr.scale(size, size)
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    fa = a * (1 - wr)
    if fa > 0.01:
        cr.save(); cr.rotate(-0.5 + 0.25 * st * math.sin(t * 9))
        moth = kind == "moth"
        flap = st * math.sin(t * 58)
        for side in (-1, 1):   # wings (a ghost wing when they buzz)
            for gk, ga in ((0, 1.0), (1, 0.35 * st)):
                if ga < 0.02:
                    continue
                ang = side * (0.9 + 0.55 * flap + gk * 0.5 * side)
                cr.save(); cr.rotate(-ang if side < 0 else ang)
                if moth:
                    cr.move_to(0, 0); cr.curve_to(-6, -14, -22, -22, -20, -4); cr.curve_to(-18, 4, -8, 4, 0, 0)
                else:
                    cr.save(); cr.translate(-9, 0); cr.scale(1.0, 0.45); cr.arc(0, 0, 10, 0, 2 * math.pi); cr.restore()
                cr.set_source_rgba(0.78, 0.8, 0.84, 0.55 * fa * ga); cr.fill_preserve()
                cr.set_source_rgba(*INK, 0.8 * fa * ga); cr.set_line_width(1.2); cr.stroke()
                cr.restore()
        cr.set_source_rgba(*INK, fa); cr.set_line_width(1.4)
        for k in range(3):   # legs
            for side in (-1, 1):
                cr.move_to(-2 + k * 4, 0); cr.line_to(-5 + k * 5 + st * 2 * math.sin(t * 20 + k), side * (9 + k)); cr.stroke()
        cr.save(); cr.scale(1.5 if moth else 1.3, 0.75 if moth else 0.85)
        cr.arc(0, 0, 6.5, 0, 2 * math.pi); cr.restore(); cr.fill()                    # body
        cr.arc(8.5 if moth else 8, 0, 4.2, 0, 2 * math.pi); cr.fill()               # head
        cr.restore()
    if a * wr > 0.01:   # the bundle: white silk, ink outline, wrap lines
        ca = a * wr
        cr.save(); cr.rotate(0.35)
        L = 15 if kind != "moth" else 20
        cr.save(); cr.scale(0.68, 1.0); cr.arc(0, 0, L, 0, 2 * math.pi); cr.restore()
        cr.set_source_rgba(*PAPER, ca); cr.fill_preserve(); cr.set_source_rgba(*INK, ca); cr.set_line_width(1.8); cr.stroke()
        cr.set_line_width(1.0)
        for k in range(5):
            yy = -L * 0.7 + k * L * 0.35
            cr.move_to(-L * 0.62, yy + 3); cr.curve_to(-L * 0.2, yy - 4, L * 0.2, yy + 6, L * 0.62, yy - 2)
            cr.set_source_rgba(*INK, 0.55 * ca); cr.stroke()
        cr.move_to(0, -L); cr.line_to(0, -L - 9); cr.set_source_rgba(*INK, 0.6 * ca); cr.stroke()   # the thread it hangs from
        cr.restore()
    cr.restore()

def draw_moth(cr, x, y, s, flap, alpha, ang=0.0, dusty=False):
    """a moth seen from above, wings beating (flap = phase in radians). dusty=True: just its soft print"""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    fold = 0.25 + 0.75 * abs(math.cos(flap))
    for side in (-1, 1):
        cr.save(); cr.scale(side * fold, 1.0)
        for wing in ((0, -4, 22, -22, 32, -6, 20, 5, 0, 2), (0, 2, 17, 5, 21, 17, 8, 19, 0, 8)):
            x0, y0, c1x, c1y, c2x, c2y, ex_, ey_, bx, by = wing
            cr.move_to(x0, y0); cr.curve_to(c1x, c1y, c2x, c2y, ex_, ey_); cr.curve_to(ex_ - 6, ey_ + 1, bx + 4, by, bx, by)
            cr.close_path()
            if dusty:
                cr.set_source_rgba(0.5, 0.45, 0.4, 0.22 * alpha); cr.fill()
            else:
                cr.set_source_rgba(0.72, 0.69, 0.64, 0.9 * alpha); cr.fill_preserve()
                cr.set_source_rgba(*INK, alpha); cr.set_line_width(1.3 / max(fold, 0.4)); cr.stroke()
        cr.arc(16, -8, 2.6, 0, 2 * math.pi)
        cr.set_source_rgba(*INK, (0.25 if dusty else 0.6) * alpha); cr.fill()
        cr.restore()
    if not dusty:
        cr.set_source_rgba(*INK, alpha)
        cr.save(); cr.translate(0, 2); cr.scale(0.32, 1.0); cr.arc(0, 0, 11, 0, 2 * math.pi); cr.restore(); cr.fill()
        cr.arc(0, -10, 3.2, 0, 2 * math.pi); cr.fill()
        cr.set_line_width(1.1)
        for side in (-1, 1):
            cr.move_to(side, -12); cr.curve_to(side * 4, -20, side * 7, -22, side * 9, -25); cr.stroke()
    cr.restore()

LENS_BUGS = []   # [dict(t0, t1, x, y, size, taps=[...])] a moth fluttering against OUR glass (screen space)
def draw_lens_bugs(cr, t):
    for b in LENS_BUGS:
        t0, t1, x, y, s = b["t0"], b["t1"], b["x"], b["y"], b.get("size", 4.5)
        if t > t1:   # its dust stays on the glass, like a little drawing
            a = math.exp(-(t - t1) / 25.0)
            draw_moth(cr, x, y, s * 0.95, 0.0, a, 0.15, dusty=True)
            rr = random.Random(9)
            for k in range(40):   # powder specks
                px, py = x + rr.gauss(0, 18 * s), y + rr.gauss(0, 10 * s)
                cr.set_source_rgba(0.45, 0.4, 0.35, 0.25 * a * rr.random()); cr.arc(px, py, rr.uniform(0.8, 2.2), 0, 2 * math.pi); cr.fill()
        u = (t - (t0 - 0.7)) / 0.7
        if 0 <= u < 1:    # flying in at the lens
            draw_moth(cr, x - 220 * (1 - u), y + 300 * (1 - u), s * (0.25 + 0.75 * u * u), t * 46, 1.0, 0.3 * (1 - u))
        elif t0 <= t <= t1:   # fluttering against the glass
            jx = 14 * math.sin(t * 9) + 6 * math.sin(t * 23); jy = 10 * math.cos(t * 7) + 5 * math.sin(t * 19)
            tap = max([math.exp(-((t - k) / 0.05) ** 2) for k in b.get("taps", [])] + [0.0])
            draw_moth(cr, x + jx, y + jy, s * (1 + 0.05 * tap), t * 46, 1.0, 0.15 + 0.1 * math.sin(t * 3))
        elif t1 < t < t1 + 0.6:   # and away again
            u = (t - t1) / 0.6
            draw_moth(cr, x + 260 * u, y - 380 * u, s * (1 - 0.8 * u), t * 46, 1.0 - u, -0.4)

def web_damage(w, segs, moor, torn, fall, t):
    """torn (0..1): holes ripped in the spiral, one spoke snapped, loose ends hanging. fall (0..1): the web lets go,
    piece by piece (spiral first, then spokes, then the frame), and each piece drifts down, turning, and fades."""
    out = []
    nf = len(w["frame"])
    sp = w["spiral"]
    for n, (p0, p1, kind) in enumerate(segs):
        fa = 1.0
        if kind == "spoke":
            j = n - nf
            if j == 3:   # snapped halfway
                p1 = lerp(p0, p1, 1 - 0.5 * torn)
        elif kind == "spiral":
            k = n - nf - w["spokes"]
            i, f = sp[min(k, len(sp) - 1)]
            if (i in (2, 3) and f > 0.4) or (i == 7 and 0.3 < f < 0.65) or (i == 3 and f > 0.2):
                fa = 1 - torn
        out.append([p0, p1, kind, fa, n])
    if torn > 0:   # loose ends, swaying
        hx, hy = w["hub"]
        d3, L3 = w["dirs"][3], w["lens"][3]
        for m, (sx, sy, ln) in enumerate([(hx + d3[0] * L3 * 0.5, hy + d3[1] * L3 * 0.5, 46),
                                          (w["frame"][3][0] + 30, w["frame"][3][1] - 4, 64),
                                          (hx + w["dirs"][7][0] * w["lens"][7] * 0.66, hy + w["dirs"][7][1] * w["lens"][7] * 0.66, 38)]):
            prev = (sx, sy)
            for q in range(1, 6):
                u = q / 5
                sway = 7 * u * u * math.sin(t * 1.3 + m * 2.0)
                pt = (sx + sway + 6 * u * (m - 1), sy + ln * u)
                out.append([prev, pt, "spiral", torn * 0.9, 900 + m * 10 + q])
                prev = pt
    if fall > 0:   # it comes away in pieces: neighbouring threads fall together as one torn patch
        def chunk(sg):
            p0, p1, kind, fa, n = sg
            if n >= 900:
                return 300 + (n - 900) // 10
            if kind == "frame":
                return 200 + n
            if kind == "spoke":
                return 100 + (n - nf)
            k = n - nf - w["spokes"]
            i, f = sp[min(k, len(sp) - 1)]
            return (i // 2) * 4 + int(f * 3.4)
        groups = {}
        for sg in out:
            groups.setdefault(chunk(sg), []).append(sg)
        for cid, gs in groups.items():
            mx = sum((g[0][0] + g[1][0]) / 2 for g in gs) / len(gs)
            my = sum((g[0][1] + g[1][1]) / 2 for g in gs) / len(gs)
            h = 0.5 + 0.5 * math.sin(cid * 12.9898) * math.cos(cid * 4.13)
            r = 0.4 * h if cid < 100 else (0.18 + 0.2 * h if cid >= 300 else (0.3 + 0.22 * h if cid < 200 else 0.5 + 0.1 * h))
            u = max(0.0, min(1.0, (fall - r) / 0.5))
            if u <= 0:
                continue
            rot = (h - 0.5) * 1.4 * u
            ca, sa = math.cos(rot), math.sin(rot)
            dx = 46 * u * math.sin(2.2 * u + cid) + 12 * u * math.sin(t * 1.2 + cid)
            dy = 430 * u ** 1.35
            sq = 1 - 0.35 * u   # silk crumples as it falls
            def mv(p):
                x, y = (p[0] - mx) * sq, (p[1] - my) * sq
                return (mx + dx + x * ca - y * sa, my + dy + x * sa + y * ca)
            for sg in gs:
                sg[0], sg[1] = mv(sg[0]), mv(sg[1])
                sg[3] = sg[3] * (1 - smooth((u - 0.45) / 0.55))
        moor = [(p0, p1, fade, 1 - smooth((fall - 0.5) / 0.2)) for p0, p1, fade in moor]
    return [tuple(sg[:4]) for sg in out], moor

def draw_web(cr, t, env):
    w = WEB
    if w is None or env["web"] <= 0.001:
        return
    b, vis, glow = env["web"], env["web_vis"], env["web_glow"]
    hx, hy = w["hub"]
    A = web_tremble(t) + env["prey_struggle"] * 0.32 * (0.6 + 0.4 * math.sin(t * 11))
    def jig(x, y, wt, sid):
        j = 0.6 * (wob(sid, 1) - 0.5)
        return (x + A * 5 * wt * math.sin(t * 48 + sid) + j, y + A * 4 * wt * math.cos(t * 41 + sid * 0.7) + j)
    segs = []   # (p0, p1, kind) kind: frame/spoke/spiral
    F = w["frame"]
    for i in range(len(F)):
        segs.append((jig(*F[i], 1, i), jig(*F[(i + 1) % len(F)], 1, i + 1), "frame"))
    ns = w["spokes"]
    tip = None
    for i, (d, L) in enumerate(zip(w["dirs"], w["lens"])):
        u = smooth((b - i * 0.3 / ns) / (0.3 / ns))
        if u <= 0:
            continue
        e = (hx + d[0] * L * u, hy + d[1] * L * u)
        segs.append((jig(hx, hy, 0, 99), jig(*e, u, 30 + i), "spoke"))
        if u < 1:
            tip = (e, math.atan2(d[1], d[0]))
    sp = w["spiral"]
    s = (b - 0.3) / 0.7
    head = None
    if s > 0:
        n = s * (len(sp) - 1)
        pts = []
        for k in range(int(n) + 2):
            if k >= len(sp):
                break
            i, f = sp[k]
            d, L = w["dirs"][i], w["lens"][i]
            pts.append(jig(hx + d[0] * L * f, hy + d[1] * L * f, f, 60 + k))
        last = min(int(n), len(pts) - 1)
        for k in range(last):
            segs.append((pts[k], pts[k + 1], "spiral"))
        if last + 1 < len(pts) and n < len(sp) - 1:
            fr_ = n - int(n)
            p0, p1 = pts[last], pts[last + 1]
            pe = (p0[0] + (p1[0] - p0[0]) * fr_, p0[1] + (p1[1] - p0[1]) * fr_)
            segs.append((p0, pe, "spiral"))
            head = (pe, math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
        w["_dew"] = pts[: last + 1]
    else:
        w["_dew"] = []
    # mooring threads: to the window frame, or out into nothing
    moor = []
    if w["anchors"]:
        for i, a in enumerate(w["anchors"]):
            if a is not None:
                moor.append((jig(*F[i], 1, i), a, i in w["fade"]))
    if env["web_torn"] > 0 or env["web_fall"] > 0:
        segs, moor = web_damage(w, segs, moor, env["web_torn"], env["web_fall"], t)
    def ink_pass(col, alpha, widths):
        for sg in segs:
            p0, p1, kind = sg[:3]; fa = sg[3] if len(sg) > 3 else 1.0
            if fa < 0.01:
                continue
            cr.move_to(*p0); cr.line_to(*p1)
            cr.set_source_rgba(*col, fa * alpha * (0.8 if kind == "spiral" else 1.0)); cr.set_line_width(widths[kind]); cr.stroke()
        for mg in moor:
            p0, p1, fade = mg[:3]; fa = mg[3] if len(mg) > 3 else 1.0
            if fa < 0.01:
                continue
            if fade:
                g = cairo.LinearGradient(p0[0], p0[1], p1[0], p1[1])
                g.add_color_stop_rgba(0, *col, alpha * fa); g.add_color_stop_rgba(1, *col, 0)
                cr.set_source(g)
            else:
                cr.set_source_rgba(*col, alpha * fa)
            cr.move_to(*p0); cr.line_to(*p1); cr.set_line_width(widths["frame"]); cr.stroke()
    cr.save(); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    if w["dragline"]:
        (ax, ay), (bx, by) = w["dragline"]
        drop = smooth(min(1.0, env["web_fall"] * 2.4))
        ay = ay + (by - 40 - ay) * drop                      # its top lets go and it falls in a heap
        ax = ax + (bx - ax) * drop
        vis_d = vis * (1 - smooth((env["web_fall"] - 0.45) / 0.3))
        L = math.hypot(bx - ax, by - ay); nx, ny = -(by - ay) / L, (bx - ax) / L
        pts = []
        for k in range(41):
            u = k / 40
            o = A * 16 * math.sin(math.pi * u) * math.sin(t * 52)
            pts.append((ax + (bx - ax) * u + nx * o, ay + (by - ay) * u + ny * o))
        for col, al, wd in ([(INK, 0.7 * vis_d * (1 - 0.4 * glow), 2.4)] +
                            ([((1.0, 0.72, 0.25), 0.3 * glow, 7), ((1.0, 0.8, 0.38), 0.95 * glow, 2.6)] if glow > 0.01 else [])):
            path(cr, pts); cr.set_source_rgba(*col, al); cr.set_line_width(wd); cr.stroke()
    if glow > 0.01:   # warm light pooled behind the web so the lit threads read against it
        R = max(w["lens"]) * 1.5
        g = cairo.RadialGradient(hx, hy, 0, hx, hy, R)
        g.add_color_stop_rgba(0, 1.0, 0.78, 0.42, 0.32 * glow); g.add_color_stop_rgba(1, 1.0, 0.78, 0.42, 0)
        cr.set_source(g); cr.arc(hx, hy, R, 0, 2 * math.pi); cr.fill()
    ink_pass(INK, 0.72 * vis * (1 - 0.45 * glow), dict(frame=2.2, spoke=2.0, spiral=1.6))
    if glow > 0.01:   # the light finds it: every thread lights up gold, dew beads glint
        ink_pass((1.0, 0.68, 0.2), 0.35 * glow, dict(frame=8, spoke=7.5, spiral=6.5))
        ink_pass((1.0, 0.78, 0.34), 0.95 * glow, dict(frame=3.0, spoke=2.8, spiral=2.4))
        ink_pass((1.0, 0.97, 0.86), 0.9 * glow, dict(frame=1.2, spoke=1.1, spiral=1.0))
        for k, (x, y) in enumerate(w["_dew"][::2]):
            tw = 0.55 + 0.45 * math.sin(t * 3.3 + k * 2.1)
            gg = cairo.RadialGradient(x, y, 0, x, y, 9)
            gg.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.6 * glow * tw); gg.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
            cr.set_source(gg); cr.arc(x, y, 9, 0, 2 * math.pi); cr.fill()
            cr.set_source_rgba(1, 0.99, 0.94, glow * tw); cr.arc(x, y, 3.0, 0, 2 * math.pi); cr.fill()
            if k % 4 == 0:
                sz = 12 * tw * glow
                cr.move_to(x - sz, y); cr.line_to(x + sz, y); cr.move_to(x, y - sz); cr.line_to(x, y + sz)
                cr.set_source_rgba(1, 0.95, 0.75, 0.85 * glow * tw); cr.set_line_width(1.6); cr.stroke()
    cr.restore()
    prey = w.get("prey")
    if prey and env["prey"] > 0.01:
        draw_prey(cr, t, env, prey["pos"], prey.get("kind", "fly"), prey.get("size", 1.3))
    if env["spider"] > 0.01:
        busy = 1.0 if b < 1 else 0.15
        if head is not None:
            (px, py), ang = head
        elif tip is not None:
            (px, py), ang = tip
        else:
            px, py, ang = hx, hy, env["spider_turn"]
        hub_u = smooth((b - 0.96) / 0.04)
        px, py = lerp((px, py), (hx, hy + env["spider_dy"]), hub_u)
        ang = ang + (env["spider_turn"] - ang) * hub_u
        sp_u = env["spider_to_prey"]
        if prey and sp_u > 0.001:   # she walks out to what she caught, and turns it while she wraps it
            qx, qy = prey["pos"]
            wrap_busy = env["prey_wrap"] * (1 - env["prey_wrap"]) * 4
            tx = qx - 16 + wrap_busy * 9 * math.cos(t * 5); ty = qy - 12 + wrap_busy * 7 * math.sin(t * 5)
            face = math.atan2(qy - py, qx - px) if sp_u < 0.98 else math.atan2(qy - ty, qx - tx)
            px, py = lerp((px, py), (tx, ty), sp_u)
            ang = ang + (face - ang) * smooth(sp_u * 3)
            busy = max(busy, wrap_busy, 1.0 if 0.02 < sp_u < 0.98 else 0.0)
        px += A * 3 * math.sin(t * 47); py += A * 3 * math.cos(t * 39)
        draw_spider(cr, px, py, ang, w["spider_size"], env["spider"] * max(vis, 0.35), t, busy + min(1, A))

def web_box():
    """world bbox of the web (for keeping captions off it)"""
    xs = [p[0] for p in WEB["frame"]]; ys = [p[1] for p in WEB["frame"]]
    return min(xs) - 30, min(ys) - 30, max(xs) + 30, max(ys) + 30

def draw_room(cr):
    cr.set_source_rgb(*PAPER); cr.paint()
    path(cr, sketch_pts([(-6000, FLOOR_Y), (14000, FLOOR_Y)], amp=1.3, sid=90, step=40)); stroke_ink(cr, 3.5, alpha=0.8)

def draw_shadow(cr, p):
    x = (p["lfoot"][0] + p["rfoot"][0]) / 2
    for k in range(3):   # a few pencil scratches under his feet
        w = 70 - k * 18
        cr.move_to(x - w + k * 6, FLOOR_Y + 9 + k * 7); cr.line_to(x + w - k * 4, FLOOR_Y + 9 + k * 7)
        stroke_ink(cr, 2, alpha=0.35)

# --------------------------------------------------------- glass overlay ---
_knock_screen = {}
def knuckle_marks(cr, t):
    for k in INTRO_KNOCKS:
        if t < k or k not in _knock_screen:
            continue
        a = math.exp(-(t - k) / 5.0)
        x, y = _knock_screen[k]
        for i in range(4):
            kx, ky = x - 36 + i * 24, y - 10 + abs(i - 1.5) * 5
            g = cairo.RadialGradient(kx, ky, 0, kx, ky, 20)
            g.add_color_stop_rgba(0, 0.6, 0.6, 0.62, 0.22 * a); g.add_color_stop_rgba(1, 0.6, 0.6, 0.62, 0)
            cr.set_source(g); cr.arc(kx, ky, 20, 0, 2 * math.pi); cr.fill()

# ------------------------------------------- a crack in OUR side of the glass (D27–30) ---
# configure(crack=dict(origin=(x, y) screen px, heading=rad, length=px, seed, branches, tape_at=0..1, tape_len=px)).
# env: crack 0..1 (how far it has crept), crack_vis (alpha), tape 0..1 (a strip of clear tape laid along it),
# tape_lift 0..1 (one corner of the tape peeling up), tape_drop 0..1 (it lets go and falls off the glass). Hairline, phone-screen thin: a dark core with a bright edge.
CRACK = None
def build_crack(spec):
    c = dict(heading=-0.32, length=640, seed=3, branches=5, tape_at=0.42, tape_len=300, tape_w=64)
    c.update(spec)
    rr = random.Random(c["seed"])
    def walk(x, y, ang, L, kink=0.16, lo=16, hi=42):
        h0 = ang
        pts, cum, d = [(x, y)], [0.0], 0.0
        while d < L:
            st = rr.uniform(lo, hi)
            ang = h0 + max(-0.45, min(0.45, ang - h0 + rr.gauss(0, kink)))
            x, y = x + math.cos(ang) * st, y + math.sin(ang) * st
            d += st
            pts.append((x, y)); cum.append(d)
        return pts, cum, ang
    ox, oy = c["origin"]
    main, mcum, _ = walk(ox, oy, c["heading"], c["length"])
    c["main"], c["mcum"] = main, mcum
    br = []
    for k in range(c["branches"]):
        f = rr.uniform(0.1, 0.85)
        d0 = f * c["length"]
        i = max(1, next(j for j, v in enumerate(mcum) if v >= d0))
        (ax, ay), (bx, by) = main[i - 1], main[i]
        a = math.atan2(by - ay, bx - ax) + rr.choice((-1, 1)) * rr.uniform(0.45, 1.1)
        pts, cum, _ = walk(bx, by, a, rr.uniform(50, 170), kink=0.2, lo=10, hi=28)
        br.append((mcum[i], pts, cum))
    for k in range(7):   # the impact point: short rays out of a tiny chip
        a = rr.uniform(0, 2 * math.pi)
        pts, cum, _ = walk(ox, oy, a, rr.uniform(10, 38), kink=0.25, lo=5, hi=12)
        br.append((0.0, pts, cum))
    c["branch"] = br
    xs = [p[0] for p in main] + [p[0] for _, pts, _ in br for p in pts]
    ys = [p[1] for p in main] + [p[1] for _, pts, _ in br for p in pts]
    c["box"] = (min(xs) - 50, min(ys) - 60, max(xs) + 50, max(ys) + 60)
    # the tape is laid along the middle of the crack
    d_mid = c["tape_at"] * c["length"]
    i = max(1, next(j for j, v in enumerate(mcum) if v >= d_mid))
    c["tape_c"] = main[i]
    (ax, ay), (bx, by) = main[0], main[-1]
    c["tape_ang"] = math.atan2(by - ay, bx - ax)
    return c

def _partial(pts, cum, L):
    out = [pts[0]]
    for k in range(1, len(pts)):
        if cum[k] <= L:
            out.append(pts[k])
        else:
            u = (L - cum[k - 1]) / max(1e-6, cum[k] - cum[k - 1])
            (ax, ay), (bx, by) = pts[k - 1], pts[k]
            out.append((ax + (bx - ax) * u, ay + (by - ay) * u))
            break
    return out

def draw_crack(cr, t, env):
    c = CRACK
    if c is None:
        return
    g, vis = env["crack"], env["crack_vis"]
    if g > 0.001 and vis > 0.01:
        Lg = g * c["length"]
        lines = [_partial(c["main"], c["mcum"], Lg)]
        for d0, pts, cum in c["branch"]:
            if Lg > d0 + 2:
                bl = (Lg - d0) * (0.8 if d0 > 0 else 3.0)
                if bl > 2:
                    lines.append(_partial(pts, cum, bl))
        cr.save(); cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
        for col, al, wd, off in (((0.2, 0.21, 0.24), 0.28, 5.0, (0, 0)),     # soft shadow in the glass
                                 ((1.0, 1.0, 1.0), 0.9, 2.2, (1.6, 1.4)),      # the bright broken edge
                                 ((0.06, 0.06, 0.08), 0.9, 1.7, (0, 0))):      # hairline core
            for ln in lines:
                if len(ln) < 2:
                    continue
                cr.move_to(ln[0][0] + off[0], ln[0][1] + off[1])
                for x, y in ln[1:]:
                    cr.line_to(x + off[0], y + off[1])
                cr.set_source_rgba(*col, al * vis); cr.set_line_width(wd); cr.stroke()
        ox, oy = c["origin"]   # the chip where it started
        gg = cairo.RadialGradient(ox, oy, 0, ox, oy, 9)
        gg.add_color_stop_rgba(0, 1, 1, 1, 0.9 * vis); gg.add_color_stop_rgba(1, 1, 1, 1, 0)
        cr.set_source(gg); cr.arc(ox, oy, 9, 0, 2 * math.pi); cr.fill()
        cr.set_source_rgba(0.1, 0.1, 0.12, 0.6 * vis); cr.set_line_width(1.0); cr.arc(ox, oy, 4.5, 0.4, 4.6); cr.stroke()
        cr.restore()
    ta = env["tape"]
    if ta > 0.01:
        (tx, ty), ang = c["tape_c"], c["tape_ang"]
        L2, W2 = c["tape_len"] / 2, c["tape_w"] / 2
        lift = env["tape_lift"]
        dr = env["tape_drop"]   # it lets go and falls away down the glass, turning
        cr.save(); cr.translate(tx - 120 * dr, ty + 1500 * dr * dr); cr.rotate(ang + 0.9 * dr)
        rr = random.Random(5)
        def edge(x, sgn):   # torn ends: a fine zigzag
            return [(x + sgn * rr.uniform(0, 5), -W2 + k * (2 * W2) / 8) for k in range(9)]
        fold = 78 * lift   # one corner folds back along a diagonal
        left = edge(-L2, -1)
        right = list(reversed(edge(L2, 1)))
        body = left + [(L2, W2)] + [p for p in right if p[1] > -W2 + fold * 0.9] + [(L2, -W2 + fold), (L2 - fold, -W2)]
        if fold < 1:
            body = left + right
        cr.move_to(*body[0])
        for p in body[1:]:
            cr.line_to(*p)
        cr.close_path()
        cr.set_source_rgba(0.93, 0.90, 0.74, 0.55 * ta); cr.fill_preserve()     # yellowed clear tape
        cr.set_source_rgba(0.35, 0.34, 0.3, 0.75 * ta); cr.set_line_width(2.0); cr.stroke()
        sh = cairo.LinearGradient(0, -W2, 0, W2)   # a soft sheen across it
        sh.add_color_stop_rgba(0, 1, 1, 1, 0.0); sh.add_color_stop_rgba(0.35, 1, 1, 1, 0.55 * ta)
        sh.add_color_stop_rgba(0.5, 1, 1, 1, 0.0)
        cr.set_source(sh); cr.rectangle(-L2 + 4, -W2 + 3, 2 * L2 - 8 - fold, 2 * W2 - 6); cr.fill()
        if fold >= 1:   # the lifted flap curls up off the glass, its shadow falling where it used to lie
            a0, b0, c0 = (L2 - fold, -W2), (L2, -W2 + fold), (L2, -W2)
            tip = (L2 - fold * 0.62, -W2 + fold * 0.62)
            cr.move_to(*a0); cr.line_to(*b0); cr.line_to(*c0); cr.close_path()
            cr.set_source_rgba(0, 0, 0, 0.28 * ta * lift); cr.fill()
            cr.move_to(*a0); cr.curve_to(a0[0] + 4, a0[1] + fold * 0.3, tip[0] - 6, tip[1] - 4, *tip)
            cr.curve_to(tip[0] + 4, tip[1] + 6, b0[0] - fold * 0.3, b0[1] - 4, *b0); cr.close_path()
            cr.set_source_rgba(0.98, 0.96, 0.86, 0.95 * ta); cr.fill_preserve()
            cr.set_source_rgba(0.25, 0.24, 0.22, 0.9 * ta); cr.set_line_width(2.0); cr.stroke()
        cr.restore()

_palm = dict(pos=None, size=0.0, last=None)
def palm_print(cr, t):
    """the print his hand leaves on the glass (our side of the screen), fading slowly"""
    if _palm["pos"] is None or t <= _palm["last"] + 0.05:
        return
    a = 0.42 * math.exp(-(t - _palm["last"]) / 7.0)
    if a < 0.01:
        return
    x, y = _palm["pos"]; fr = _palm["size"]
    cr.save(); cr.translate(x, y); cr.rotate(-0.12)
    def capsule(x0, y0, ang, ln, wd):
        cr.save(); cr.translate(x0, y0); cr.rotate(ang)
        cr.move_to(-wd / 2, 0); cr.line_to(-wd / 2, -ln + wd / 2)
        cr.arc(0, -ln + wd / 2, wd / 2, math.pi, 2 * math.pi); cr.line_to(wd / 2, 0); cr.close_path(); cr.restore()
    cr.push_group()
    for fx_, ln, ang in [(-0.6, 0.95, -0.2), (-0.2, 1.18, -0.07), (0.2, 1.12, 0.06), (0.6, 0.9, 0.2)]:
        capsule(fx_ * fr, -0.55 * fr, ang, ln * fr, 0.34 * fr)
    capsule(-0.75 * fr, 0.25 * fr, -1.05, 0.8 * fr, 0.36 * fr)
    cr.new_sub_path(); cr.save(); cr.scale(1.0, 1.05); cr.arc(0, 0, fr * 0.9, 0, 2 * math.pi); cr.restore()
    cr.set_source_rgba(0.6, 0.62, 0.66, 1.0); cr.set_fill_rule(cairo.FILL_RULE_WINDING); cr.fill_preserve()
    cr.set_line_width(fr * 0.12); cr.stroke()          # soft rim, like a greasy print on glass
    cr.pop_group_to_source(); cr.paint_with_alpha(a * 0.45)
    cr.restore()

def shake_at(t, knocks, amp):
    sx = sy = 0.0
    for k in knocks:
        if t >= k:
            e = math.exp(-(t - k) * 22) * amp * KNOCK_GAIN.get(k, 1.0)
            sx += e * math.sin((t - k) * 95); sy += e * math.cos((t - k) * 77)
    return sx, sy

# --------------------------------------------------------------- captions ---
# Waking-Life-ish: each phrase lands somewhere new in the open space, words pop in one at a time
# with a little tilt / size / drift. Kept inside TikTok's safe zone and away from his face + window.
# captions: Indie Flower (OFL, engine/fonts); NIGEL_FONT overrides it
FONT_PATH = os.environ.get("NIGEL_FONT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "IndieFlower-Regular.ttf")
SAFE = (70, 230, 900, 1440)   # x0, y0, x1, y1 on screen (clear of TikTok's UI)
_word_cache = {}
def word_surface(text, size):
    key = (text, size)
    if key not in _word_cache:
        f = ImageFont.truetype(FONT_PATH, size)
        pad = 16
        tw = int(ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(text, font=f)) + pad * 2
        th = int(size * 1.45) + pad
        img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((pad, pad // 2), text, font=f, fill=(18, 18, 22, 255), stroke_width=10, stroke_fill=(252, 252, 250, 255))
        d.text((pad, pad // 2), text, font=f, fill=(18, 18, 22, 255), stroke_width=2, stroke_fill=(18, 18, 22, 255))
        a = np.array(img).astype(np.float32)
        al = a[..., 3:4] / 255
        bgra = np.ascontiguousarray(np.concatenate([a[..., 2:3] * al, a[..., 1:2] * al, a[..., 0:1] * al, a[..., 3:4]], 2).astype(np.uint8))
        adv = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(text, font=f)
        _word_cache[key] = (cairo.ImageSurface.create_for_data(memoryview(bgra), cairo.FORMAT_ARGB32, tw, th, tw * 4), bgra, tw, th, adv, pad)
    return _word_cache[key]

def build_chunks():
    chunks, cur = [], []
    for w in words:
        if cur and len(" ".join(x["text"] for x in cur + [w])) > 20:
            chunks.append(cur); cur = []
        cur.append(w)
        if w["text"][-1] in ".,?!":
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    out = []
    for i, ch in enumerate(chunks):
        s = ch[0]["start"] - 0.05
        e = ch[-1]["end"] + 0.45
        if i + 1 < len(chunks):
            e = min(e if chunks[i + 1][0]["start"] - ch[-1]["end"] >= 0.9 else chunks[i + 1][0]["start"] - 0.02,
                    chunks[i + 1][0]["start"] - 0.02)
        out.append(dict(start=s, end=max(e, s + 0.4), words=ch))
    return out

def world_to_screen(t, pt):
    cx, cy, z = cam_track.at(t)
    cx += follow_track.at(t) * loco(t)[0]
    return ((pt[0] - cx) * z + W / 2, (pt[1] - cy) * z + H / 2)

def layout_chunks(chunks):
    prev = None
    for idx, ch in enumerate(chunks):
        r = random.Random(1000 + idx)
        for shrink in (1.0, 0.8, 0.66):   # crowded frame? try smaller text before covering him
            size = r.choice([78, 84, 92, 100]) * shrink
            ws = [(w, w["text"].lower(), r.uniform(-0.09, 0.09), r.uniform(0.9, 1.12), r.uniform(-8, 8)) for w in ch["words"]]
            widths = [word_surface(txt, int(size * sc))[4] + size * 0.3 for _, txt, _, sc, _ in ws]
            total = sum(widths) - size * 0.3
            # where are his head and the window on screen during this phrase?
            samples = [ch["start"] + (ch["end"] - ch["start"]) * u for u in (0.1, 0.5, 0.9)]
            heads = [(world_to_screen(tm, live_pose(tm)["head"]), HEAD_R * cam_track.at(tm)[2] + 70) for tm in samples]
            bodies = []
            for tm in samples:
                lp = live_pose(tm)
                xs = [world_to_screen(tm, lp[k])[0] for k in ("hip", "lhand", "rhand", "lfoot", "rfoot", "lknee", "rknee")]
                ys = [world_to_screen(tm, lp[k])[1] for k in ("neck", "lfoot", "rfoot", "lhand", "rhand")]
                bodies.append((min(xs) - 40, min(ys), max(xs) + 40, max(ys) + 20))
            wins = []
            for tm in samples:
                wx0, wy0 = world_to_screen(tm, (WIN[0] - 40, WIN[1] - 30))
                wx1, wy1 = world_to_screen(tm, (WIN[0] + WIN[2] + 40, WIN[1] + WIN[3] + 60))
                wins.append((wx0, wy0, wx1, wy1))
            half_h = size * 0.55   # text is a box, not a line
            best, bscore = None, -1e9
            for _ in range(250):
                cx = r.uniform(SAFE[0] + total / 2, max(SAFE[0] + total / 2 + 1, SAFE[2] - total / 2))
                cy = r.uniform(SAFE[1] + 60, SAFE[3] - 60)
                x0, x1 = cx - total / 2, cx + total / 2
                score = 1e9
                for (hx, hy), hr in heads:
                    dxh = max(x0 - hx, 0, hx - x1)
                    dyh = max(abs(cy - hy) - half_h, 0)
                    dd = math.hypot(dxh, dyh) - hr
                    score = min(score, dd)
                    if dd < 0:
                        score -= 2000        # never over his face
                score = min(score, 260)
                if TALLY_BASE + len(TALLY_NEW) > 0:   # never cover the tally marks
                    for tm in samples:
                        tx0, ty0 = world_to_screen(tm, (TALLY_XY[0] - 30, TALLY_XY[1] - 20))
                        n = TALLY_BASE + len(TALLY_NEW)
                        tx1, ty1 = world_to_screen(tm, (TALLY_XY[0] + min(4, (n + 4) // 5) * 92 + 10,
                                                        TALLY_XY[1] + ((n - 1) // 20 + 1) * 150))
                        if x1 > tx0 and x0 < tx1 and ty0 - half_h < cy < ty1 + half_h:
                            score -= 1200
                for bx0, by0, bx1, by1 in bodies:
                    if x1 > bx0 and x0 < bx1 and by0 - half_h < cy < by1 + half_h:
                        score -= 400
                for wx0, wy0, wx1, wy1 in wins:
                    if x1 > wx0 and x0 < wx1 and wy0 - half_h < cy < wy1 + half_h:
                        score -= 1000
                if WEB is not None:   # keep captions off the spider web
                    bx0_, by0_, bx1_, by1_ = web_box()
                    for tm in samples:
                        if env_track.at(tm)["web"] <= 0.001:
                            continue
                        sx0, sy0 = world_to_screen(tm, (bx0_, by0_)); sx1, sy1 = world_to_screen(tm, (bx1_, by1_))
                        if x1 > sx0 and x0 < sx1 and sy0 - half_h < cy < sy1 + half_h:
                            score -= 900
                if CRACK is not None:   # keep captions off the crack (and its tape)
                    cx0_, cy0_, cx1_, cy1_ = CRACK["box"]
                    if any(env_track.at(tm)["crack"] > 0.01 or env_track.at(tm)["tape"] > 0.01 for tm in samples):
                        if x1 > cx0_ and x0 < cx1_ and cy0_ - half_h < cy < cy1_ + half_h:
                            score -= 900
                if prev:
                    score += min(math.hypot(cx - prev[0], cy - prev[1]), 400) * 0.35   # keep it moving around
                if score > bscore:
                    bscore, best = score, (cx, cy)
            if bscore > -300:
                break
        prev = best
        x = best[0] - total / 2
        placed = []
        for (w, txt, rotw, sc, dy), wd in zip(ws, widths):
            placed.append(dict(t=w["start"], txt=txt, x=x, y=best[1] + dy, rot=rotw, size=int(size * sc),
                               cxw=x + (wd - size * 0.3) / 2))
            x += wd
        ch["placed"] = placed
        ch["tilt"] = r.uniform(-0.07, 0.07)
        ch["drift"] = (r.uniform(-14, 14), r.uniform(-10, 10))
        ch["center"] = best

def draw_caption(cr, t):
    for ch in CHUNKS:
        if not (ch["start"] <= t < ch["end"]):
            continue
        out = min(1.0, (ch["end"] - t) / 0.15)
        age = t - ch["start"]
        cx, cy = ch["center"]
        cr.save()
        cr.translate(cx + ch["drift"][0] * age, cy + ch["drift"][1] * age)
        cr.rotate(ch["tilt"] + 0.012 * math.sin(t * 1.3))
        cr.translate(-cx, -cy)
        for i, pw in enumerate(ch["placed"]):
            wa = t - (pw["t"] - 0.04)
            if wa < 0:
                continue
            a = min(1.0, wa / 0.1) * out
            pop = 1 + 0.25 * (1 - smooth(wa / 0.16))
            surf, _, tw, th, adv, pad = word_surface(pw["txt"], pw["size"])
            jx = wob(i + 40, 7) * 1.2; jy = wob(i + 60, 8) * 1.2   # boil with the drawing
            cr.save()
            cr.translate(pw["cxw"] + jx, pw["y"] + jy)
            cr.rotate(pw["rot"]); cr.scale(pop, pop)
            cr.translate(-tw / 2, -th / 2)
            cr.set_source_surface(surf, 0, 0); cr.paint_with_alpha(max(0.0, a))
            cr.restore()
        cr.restore()


CHUNKS = []


# ------------------------------------------------------------ paper grain ---
GRAIN = []
for i in range(3):
    gsurf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 540, 960)
    ga = np.ndarray((960, 540, 4), np.uint8, gsurf.get_data())
    n = np.random.default_rng(i).random((960, 540))
    ga[..., 0] = ga[..., 1] = ga[..., 2] = 0
    ga[..., 3] = ((n > 0.93) * (n - 0.93) / 0.07 * 50).astype(np.uint8)
    gsurf.mark_dirty()
    GRAIN.append(gsurf)

# ------------------------------------------------------------- frame -------
class State:
    rot = 0.0
    cloud_off = 0.0

def render_frame(t, st, surf):
    global BOIL
    BOIL = int(t * 10)            # line boil ~10 fps, like redrawn pencil
    cr = cairo.Context(surf)
    env = env_track.at(t)
    mood = mood_track.at(t)
    pose = live_pose(t)
    cx, cy, z = cam_track.at(t)
    cx += follow_track.at(t) * loco(t)[0]
    cx += math.sin(t * 0.37) * 4; cy += math.cos(t * 0.29) * 4
    z *= 1 + 0.025 * pose["push"]   # tiny lurch toward the lens on each knock
    sx1, sy1 = shake_at(t, INTRO_KNOCKS, 8)
    for k, gn in GLASS_TAPS:
        if t >= k:
            e = math.exp(-(t - k) * 26) * 5 * gn
            sx1 += e * math.sin((t - k) * 90); sy1 += e * math.cos((t - k) * 71)
    for k in INTRO_KNOCKS:   # remember where the knuckles hit the glass
        if k not in _knock_screen and t >= k:
            hx, hy = pose["rhand"]
            _knock_screen[k] = ((hx - cx) * z + W / 2, (hy - cy) * z + H / 2)
    cr.save()
    cr.translate(W / 2 + sx1, H / 2 + sy1)
    cr.rotate(env["roll"])
    cr.scale(z, z)
    cr.translate(-cx, -cy)
    draw_room(cr)
    draw_window(cr, t, env, z, st.cloud_off, shake_at(t, WINDOW_KNOCKS, 7))
    draw_beam(cr, env)
    draw_web(cr, t, env)
    draw_tally(cr, t)
    draw_shadow(cr, pose)
    echo = env["echo"]
    if echo > 0.02:   # you only ever see old light: his recent past lingers behind him
        for k in (3, 2, 1):
            tk = t - k * 0.4
            cr.push_group()
            draw_nigel(cr, tk, live_pose(tk), mood, z, st.rot, 0.0, 0.0, ghost=True)
            cr.pop_group_to_source()
            cr.paint_with_alpha(echo * 0.13 * (4 - k))
    draw_nigel(cr, t, pose, mood, z, st.rot, mouth_open(t), blink_amt(t))
    if DRAW_HOOK:
        DRAW_HOOK(cr, t, pose, env)
    draw_sparkles(cr, t, env["sparkle"])
    if env["dark"] > 0.01:   # lights out: his eyes are the only light in the room (every blink dims it)
        L = 1 - max(pose.get("shut", 0.0), blink_amt(t) * 0.8)
        hx, hy = pose["head"]
        lx_, ly_ = pose["look"][0] * 110, pose["look"][1] * 100   # the light goes where he looks (head frame)
        ca, sa = math.cos(pose["tilt"]), math.sin(pose["tilt"])
        ex, ey = hx + lx_ * ca - ly_ * sa, hy - 6 + lx_ * sa + ly_ * ca
        R = 300 + 300 * L
        D = env["dark"] * 0.93
        g = cairo.RadialGradient(ex, ey, 0, ex, ey, R)
        g.add_color_stop_rgba(0, 0.02, 0.02, 0.06, D * (1 - 0.95 * L))
        g.add_color_stop_rgba(0.42, 0.02, 0.02, 0.06, D * (1 - 0.8 * L))
        g.add_color_stop_rgba(1, 0.02, 0.02, 0.06, D)
        cr.set_source(g); cr.paint()
        c1 = rgb(mood["p2"])   # a faint wash of whatever colour his eyes are
        g2 = cairo.RadialGradient(ex, ey, 0, ex, ey, R * 0.8)
        g2.add_color_stop_rgba(0, *c1, 0.10 * L * env["dark"]); g2.add_color_stop_rgba(1, *c1, 0)
        cr.set_source(g2); cr.paint()
        cr.push_group()   # the window still lets a little night in
        draw_window(cr, t, env, z, st.cloud_off, (0, 0))
        cr.pop_group_to_source(); cr.paint_with_alpha(0.55 * env["dark"])
    cr.restore()
    if pose.get("palm", 0) > 0.8:   # remember where his palm is pressed to the glass
        hx, hy = pose["rhand"]
        _palm.update(pos=((hx - cx) * z + W / 2, (hy - cy) * z + H / 2), size=40 * pose["palm"] * z, last=t)
    knuckle_marks(cr, t)
    palm_print(cr, t)
    draw_lens_bugs(cr, t)
    draw_crack(cr, t, env)
    cr.save(); cr.scale(2, 2); cr.set_source_surface(GRAIN[BOIL % 3], 0, 0); cr.paint_with_alpha(0.5); cr.restore()
    draw_caption(cr, t)
    st.rot += mood["spin"] / FPS
    st.cloud_off += env["cloud_v"] / FPS

# ---------------------------------------------------------------- audio ----
def synth_audio():
    n = int(DURATION * SR) + SR
    mix = np.zeros(n, np.float32)
    rngn = np.random.default_rng(1)
    def place(sig, t0, gain=1.0):
        i = int(t0 * SR)
        if i >= n:
            return
        m = min(len(sig), n - i)
        mix[i:i + m] += sig[:m] * gain
    def onepole(s, a):
        y = np.zeros_like(s)
        for i in range(1, len(s)):
            y[i] = y[i - 1] + a * (s[i] - y[i - 1])
        return y
    def knock(bright=1.0, dull=0.0):
        L = int(0.35 * SR); tt = np.arange(L) / SR
        s = (np.sin(2 * np.pi * 140 * tt) * np.exp(-tt / 0.045) * 0.9
             + np.sin(2 * np.pi * 330 * tt) * np.exp(-tt / 0.03) * 0.5
             + np.sin(2 * np.pi * 1850 * tt) * np.exp(-tt / 0.010) * 0.35 * bright
             + np.sin(2 * np.pi * 3100 * tt) * np.exp(-tt / 0.005) * 0.2 * bright)
        s = s + rngn.standard_normal(L) * np.exp(-tt / 0.006) * 0.45 * bright
        if dull > 0:
            s = onepole(s, 0.08 + 0.5 * (1 - dull)) * 2.2
            for d, gg in [(0.031, 0.4), (0.067, 0.25), (0.11, 0.15)]:
                k = int(d * SR); s[k:] += s[:-k] * gg
        return s.astype(np.float32)
    def step():
        L = int(0.12 * SR); tt = np.arange(L) / SR
        s = rngn.standard_normal(L) * np.exp(-tt / 0.012) * 0.6 + np.sin(2 * np.pi * 85 * tt) * np.exp(-tt / 0.03)
        return onepole(s.astype(np.float32), 0.12) * 1.6
    for k in INTRO_KNOCKS:
        place(knock(1.0), k, 0.55 * KNOCK_GAIN.get(k, 1.0))
    for k in WINDOW_KNOCKS:
        place(knock(0.6, dull=0.85), k, 0.35)
    for k, gn in GLASS_TAPS:
        place(knock(0.75, dull=0.35), k, 0.32 * gn)
    def drip():   # a single water drop landing: a bright plink
        L = int(0.25 * SR); tt = np.arange(L) / SR
        f = 1500 + 700 * np.exp(-tt / 0.012)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.045) + rngn.standard_normal(L) * np.exp(-tt / 0.003) * 0.3
        return s.astype(np.float32)
    for d in DRIPS:
        place(drip(), d + 0.5, 0.11)      # it lands as the falling bead reaches the sill
    def scratch(dur):
        L = int((dur + 0.08) * SR); tt = np.arange(L) / SR
        nz = rngn.standard_normal(L).astype(np.float32)
        hp = nz - onepole(nz, 0.25)                      # thin, papery
        rasp = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 38 * tt + 3 * np.sin(2 * np.pi * 3 * tt)))
        env = np.clip(tt / 0.03, 0, 1) * np.clip((dur + 0.08 - tt) / 0.08, 0, 1)
        return (hp * rasp * env * 0.9).astype(np.float32)
    for ts, dur in TALLY_NEW:
        place(scratch(dur), ts, 0.22)
    def thrum():   # a low, felt-more-than-heard string note: silk being plucked
        L = int(1.4 * SR); tt = np.arange(L) / SR
        f = 98 * (1 + 0.04 * np.exp(-tt / 0.08))
        s = (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.35 * np.sin(2 * np.pi * np.cumsum(f * 2.01) / SR)) * np.exp(-tt / 0.38)
        return (s * np.clip(tt / 0.004, 0, 1)).astype(np.float32)
    for tp, gain in PLUCKS:
        place(thrum(), tp, 0.16 * gain)
    def heart():   # one heartbeat, lub-dub: felt more than heard
        L = int(0.6 * SR); tt = np.arange(L) / SR
        s = np.sin(2 * np.pi * 52 * tt) * np.exp(-tt / 0.07)
        t2 = np.clip(tt - 0.27, 0, None)
        s += 0.65 * np.sin(2 * np.pi * 46 * t2) * np.exp(-t2 / 0.06) * (tt >= 0.27)
        return (s * np.clip(tt / 0.005, 0, 1)).astype(np.float32)
    def tick():   # glass under strain: one tiny, bright click
        L = int(0.09 * SR); tt = np.arange(L) / SR
        s = (np.sin(2 * np.pi * 5200 * tt) * np.exp(-tt / 0.004) * 0.6 + np.sin(2 * np.pi * 2650 * tt) * np.exp(-tt / 0.008) * 0.5
             + rngn.standard_normal(L) * np.exp(-tt / 0.0015) * 0.7)
        return s.astype(np.float32)
    def crackle(dur):   # the crack creeping: a dry run of ticks
        L = int((dur + 0.1) * SR); out = np.zeros(L, np.float32)
        rr = random.Random(int(dur * 1000))
        x = 0.0
        while x < dur:
            i = int(x * SR); tk = tick() * rr.uniform(0.35, 1.0)
            m = min(len(tk), L - i); out[i:i + m] += tk[:m]
            x += rr.uniform(0.012, 0.06)
        return out
    for ts, kind, gain in SFX:
        if kind == "tick":
            place(tick(), ts, gain)
        if kind == "crackle":
            place(crackle(0.35), ts, gain)
        if kind == "heart":
            place(heart(), ts, gain)
        if kind == "thrum":
            place(thrum(), ts, gain)
        if kind == "scratch":
            place(scratch(0.5), ts, gain)
        elif kind == "knock":
            place(knock(1.0), ts, gain)
        elif kind == "knock_far":
            place(knock(0.6, dull=0.85), ts, gain)
    # footsteps whenever a foot plants while he's walking
    stp = step()
    last = None
    for f in range(NFRAMES):
        x, v, ph = loco(f / FPS)
        cur = int(ph / math.pi)
        if abs(v) >= 30 and pose_track.at(f / FPS)["hip"][1] <= 1350 and last is not None and cur != last:
            place(stp, f / FPS, 0.10 * min(1, abs(v) / 90) * random.Random(f).uniform(0.7, 1.1))
        last = cur
    place(voice, VO, 0.92)
    br = np.cumsum(rngn.standard_normal(n)).astype(np.float32)
    br -= np.convolve(br, np.ones(2048) / 2048, mode="same")
    br /= np.abs(br).max() + 1e-9
    tt = np.arange(n) / SR
    fr = np.clip((tt * FPS).astype(int), 0, NFRAMES + FPS)
    envs = [env_track.at(i / FPS) for i in range(NFRAMES + FPS + 2)]
    drone_amt = np.array([e["drone"] for e in envs], np.float32)[fr]
    shim_amt = np.array([e["shimmer"] for e in envs], np.float32)[fr]
    mix += br * 0.012
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * tt)
    drone = (np.sin(2 * np.pi * 55 * tt) + 0.7 * np.sin(2 * np.pi * 55.4 * tt + 1)
             + 0.45 * np.sin(2 * np.pi * 82.4 * tt) + 0.25 * np.sin(2 * np.pi * 164.8 * tt + 2) * lfo)
    mix += drone * 0.03 * drone_amt * lfo
    sh = (np.sin(2 * np.pi * 880 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 5.1 * tt))
          + 0.6 * np.sin(2 * np.pi * 1318.5 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 3.7 * tt + 1))
          + 0.4 * np.sin(2 * np.pi * 1760 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 6.3 * tt + 2)))
    mix += sh * 0.006 * shim_amt
    buzz_amt = np.array([e["buzz"] for e in envs], np.float32)[fr]
    if buzz_amt.max() > 0.001:   # a fly in a web: nasal, wavering buzz
        f0 = 205 + 22 * np.sin(2 * np.pi * 6.7 * tt) + 9 * np.sin(2 * np.pi * 13.1 * tt + 1)
        ph = np.cumsum(f0) / SR
        bz = sum(np.sin(2 * np.pi * k * ph) / k for k in range(1, 8))
        bz *= 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 2.3 * tt + 2 * np.sin(2 * np.pi * 0.7 * tt)))
        mix += bz.astype(np.float32) * 0.02 * buzz_amt
    mix = mix[: int(DURATION * SR)]
    mix[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))   # click-free hard cut
    mix *= 0.95 / max(1e-6, np.abs(mix).max())
    with wave.open("mix.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())


# ----------------------------------------------------------------- main ----
def main(out="episode.mp4"):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    st = State()
    if "--still" in sys.argv:
        times = sorted(float(a) for a in sys.argv[sys.argv.index("--still") + 1:])
        f = 0
        for target in times:
            while f / FPS < target:
                t = f / FPS
                if any(k <= t and k not in _knock_screen for k in INTRO_KNOCKS):
                    render_frame(t, st, surf)   # records knuckle positions
                else:
                    st.rot += mood_track.at(t)["spin"] / FPS
                    st.cloud_off += env_track.at(t)["cloud_v"] / FPS
                f += 1
            render_frame(target, st, surf)
            surf.write_to_png(f"still_{target:05.1f}.png")
            print("wrote", f"still_{target:05.1f}.png")
        return
    print(f"duration {DURATION:.2f}s, {NFRAMES} frames")
    synth_audio()
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error",
                           "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", "mix.wav",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000",
                           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out],
                          stdin=subprocess.PIPE)
    for f in range(NFRAMES):
        render_frame(f / FPS, st, surf)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
        if f % 150 == 0:
            print(f"frame {f}/{NFRAMES}", flush=True)
    ff.stdin.close(); ff.wait()
    print("done ->", out)
