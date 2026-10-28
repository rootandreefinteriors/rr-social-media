r"""LET THE COMMENTS DECIDE — render engine.

Modules:
    ink.py        line primitives (boil, sketchy shapes), easing, Track, lettering
    character.py  the guy: BASE pose, POSES (body), EXPR (face), pose(body, face, **kw), draw_guy, FX symbols
    props.py      clipboard, pen, pocket, poof, dust, impact, speed lines, comment card
    ltcd.py       (this) episode config, procedural motion (walk/run/sneak/shiver/laugh/sob/dance/sleep/fidget),
                  secondary motion (the curl), renderer, sound effects, main()

Episode script:
    import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
    import ltcd as L
    body = L.Track([(0, L.pose("stand", "neutral"), 0), (2.0, L.pose("wave", "shy"), 0.3, "back"), ...])
    L.configure(duration=24, pose_track=body, x_track=L.Track([...]), cam_track=L.Track([...]),
                props=fn(cr, t, pose, layer), pose_hook=fn(t, pose) -> pose, overlay=fn(cr, t), sfx=[(t, kind, gain, {kw})])
    L.main("out.mp4")        # python episode.py --still 3 6 10  -> still_*.png
Track keys: (time, value, seconds, ease) — ease: smooth out inn back elastic bounce snap linear hold.
Sounds (SFX kinds): see SYNTH below, or any WAV in ../sfx/ ("name.wav").
"""
import cairo, numpy as np, wave, math, subprocess, sys, random, os
import ink
from ink import *            # noqa: F401,F403  (re-export the drawing API as L.*)
from character import *      # noqa: F401,F403
from props import *          # noqa: F401,F403
import character as C

# ------------------------------------------------------------ episode config ---
pose_track = x_track = cam_track = None
PROPS = POSE_HOOK = OVERLAY = None
SFX = []; BLINKS = []; DURATION = 0.0; NFRAMES = 0
FLOOR = True; STEP_GAIN = 0.04; BG = None

def configure(duration, pose_track, x_track, cam_track, props=None, pose_hook=None, overlay=None,
              sfx=(), blinks=None, floor=True, step_gain=0.04, background=None, cuts=(), follow=True):
    """props(cr, t, pose, layer) is called with layer 'back' (behind him) and 'front' (over him).
    overlay(cr, t) draws in screen space (e.g. the pinned comment card). background(cr, t) draws the world first."""
    g = globals()
    g.update(pose_track=pose_track, x_track=x_track, cam_track=cam_track, PROPS=props, POSE_HOOK=pose_hook,
             OVERLAY=overlay, SFX=list(sfx), DURATION=duration, NFRAMES=int(duration * FPS), FLOOR=floor,
             STEP_GAIN=step_gain, BG=background)
    if blinks is None:
        rng = random.Random(7); b, bt = [], 1.4
        while bt < duration: b.append(bt); bt += rng.uniform(2.2, 4.5)
        blinks = b
    g["BLINKS"] = list(blinks)
    global _lx, _lv, _lph, _bph, CUT_F, FOLLOW, _SAC
    _lx = np.array([x_track.at((f - PRE) / FPS) for f in range(NFRAMES + PRE + 4)])
    _lv = np.gradient(_lx) * FPS
    for c in cuts:                       # no walk "velocity" across a hard cut
        i = int(round(c * FPS)) + PRE
        _lv[max(0, i - 2):i + 3] = 0.0
    _lph = np.cumsum(np.abs(_lv) / FPS / 80.0 * math.pi)
    rate = np.array([pose_track.at((f - PRE) / FPS).get("breath_rate", 1.0) for f in range(NFRAMES + PRE + 4)])
    _bph = np.cumsum(rate * 1.7 / FPS)
    CUT_F = sorted(int(math.floor(c * FPS + 1e-6)) + 1 for c in cuts); FOLLOW = follow   # first frame of the new shot
    _PC.clear()
    rs = random.Random(11); _SAC = []; tt = 0.0           # eye micro-movements: hold 0.5-1.4 s, then a quick dart
    while tt < duration + 2:
        _SAC.append((tt, rs.uniform(-0.13, 0.13), rs.uniform(-0.08, 0.08))); tt += rs.uniform(0.5, 1.4)

def blink_amt(t):
    b = 0.0
    for t0 in BLINKS:
        d = t - t0
        if 0 <= d < 0.16: b = max(b, 1 - abs(d - 0.08) / 0.08)
    return b

PRE = 60
_lx = _lv = _lph = _bph = None
CUT_F, FOLLOW, _SAC, _PC = [], True, [], {}

def _saccade(t):
    i = 0
    while i + 1 < len(_SAC) and _SAC[i + 1][0] <= t: i += 1
    t0, x1, y1 = _SAC[i]
    _, x0, y0 = _SAC[i - 1] if i > 0 else (0, 0.0, 0.0)
    u = min(1.0, (t - t0) / 0.06)
    return (x0 + (x1 - x0) * u, y0 + (y1 - y0) * u)
def loco(t):
    i = min(max(int(round(t * FPS)) + PRE, 0), len(_lx) - 1)
    return _lx[i], _lv[i], _lph[i]

def _add(p, k, dx, dy):
    p[k] = (p[k][0] + dx, p[k][1] + dy)

def live_pose(t):
    """pose at time t: track + procedural walk/run/sneak + cycles + lean/stretch + body offset + hook."""
    p = dict(pose_track.at(t))
    x, v, ph = loco(t)
    wk = min(1.0, abs(v) / 50.0) * (1.0 - min(1.0, p.get("nowalk", 0.0)))   # nowalk: airborne / sliding, no steps
    d = 1 if v >= 0 else -1
    run, sneak = p.get("run", 0.0), p.get("sneak", 0.0)
    if wk > 0.001:   # walk cycle driven by horizontal speed (bouncy, cartoony); run/sneak change the style
        stride = 58 + 40 * run - 10 * sneak
        liftk = 34 + 30 * run + 40 * sneak
        bob = (10 + 14 * run) * abs(math.sin(ph)) * wk
        hipx, hipy = p["hip"]
        for side, off in (("l", 0.0), ("r", math.pi)):
            s = math.sin(ph + off)
            lift = max(0.0, math.cos(ph + off)) * liftk
            foot = (hipx + stride * s, FLOOR_Y - lift)
            knee = ((hipx + foot[0]) / 2 + d * (20 + 30 * run + 20 * sneak), (hipy + FLOOR_Y) / 2 - lift * 0.55)
            p[side + "foot"] = lerp(p[side + "foot"], foot, wk)
            p[side + "knee"] = lerp(p[side + "knee"], knee, wk)
        sw = wk * p["swing"]
        if sw > 0.001:
            for side, off in (("l", math.pi), ("r", 0.0)):
                s = math.sin(ph + off)
                if run > 0.3:    # pumping bent arms
                    ex, ey = p["neck"][0] + (-1 if side == "l" else 1) * 40 + 30 * s * d, p["neck"][1] + 150
                    hx, hy = ex + 50 * d, ey - 60 - 30 * s
                    p[side + "elb"] = lerp(p[side + "elb"], (ex, ey), sw * run); p[side + "hand"] = lerp(p[side + "hand"], (hx, hy), sw * run)
                    if run > 0.5: p[side + "hand_t"] = "fist"
                p[side + "hand"] = lerp(p[side + "hand"], (p[side + "hand"][0] + 40 * s, p[side + "hand"][1] - 8 * abs(s)), sw * (1 - run))
                p[side + "elb"] = lerp(p[side + "elb"], (p[side + "elb"][0] + 16 * s, p[side + "elb"][1]), sw * (1 - run))
        for k in ("head", "neck", "hip", "lelb", "relb", "lhand", "rhand"):
            p[k] = (p[k][0], p[k][1] + bob)
        p["look"] = (p["look"][0] + 0.55 * d * wk, p["look"][1])
        p["tilt"] += 0.06 * d * wk
        p["lean"] = p.get("lean", 0.0) + d * wk * (0.06 * run + 0.03 * sneak)
        p["lfoot_dir"] = lerp(p.get("lfoot_dir", -0.5), 0.9 * d, wk)
        p["rfoot_dir"] = lerp(p.get("rfoot_dir", 0.5), 0.9 * d, wk)
    # --- cycles
    sv = p.get("shiver", 0.0)
    if sv > 0.01:
        for i, k in enumerate(C.JOINTS):
            if k in ("lfoot", "rfoot"): continue
            _add(p, k, sv * 3.5 * math.sin(t * 61 + i * 1.3), sv * 2 * math.sin(t * 53 + i))
    la = p.get("laugh", 0.0)
    if la > 0.01:
        p["hop"] = p.get("hop", 0.0) + la * 9 * abs(math.sin(t * 13))
        p["tilt"] += la * (-0.08 + 0.05 * math.sin(t * 13))
    sb = p.get("sob", 0.0)
    if sb > 0.01:
        for k in ("head", "neck", "lelb", "relb", "lhand", "rhand"):
            _add(p, k, 0, sb * 6 * math.sin(t * 15))
    dn = p.get("dance", 0.0)
    if dn > 0.01:
        sway = math.sin(t * 6.3)
        _add(p, "hip", dn * 26 * sway, -dn * 6 * abs(sway))
        for k in ("neck", "head"): _add(p, k, -dn * 14 * sway, 0)
        _add(p, "lhand", 0, -dn * 120 * max(0, sway)); _add(p, "rhand", 0, -dn * 120 * max(0, -sway))
        _add(p, "lelb", 0, -dn * 60 * max(0, sway)); _add(p, "relb", 0, -dn * 60 * max(0, -sway))
        _add(p, "lknee", dn * 14 * sway, -dn * 18 * max(0, sway)); _add(p, "rknee", dn * 14 * sway, -dn * 18 * max(0, -sway))
        p["tilt"] += dn * 0.08 * sway
    sl = p.get("sleep", 0.0)
    if sl > 0.01:
        sway = math.sin(t * 0.9)
        for k in ("head", "neck"): _add(p, k, sl * 12 * sway, sl * 10)
        p["tilt"] += sl * 0.05 * sway
    fd = p.get("fidget", 0.0)
    if fd > 0.01:
        w_ = math.sin(t * 0.8) * fd
        _add(p, "hip", w_ * 10, 0); _add(p, "neck", w_ * 6, 0); _add(p, "head", w_ * 8, 0)
        p["look"] = (p["look"][0] + 0.25 * math.sin(t * 0.37) * fd, p["look"][1])
    # --- breathing (chest/arms rise; rate-aware phase) + eye micro-movements
    bi = min(max(int(round(t * FPS)) + PRE, 0), len(_bph) - 1)
    p["breath_ph"] = _bph[bi]
    br = p.get("breath", 1.0) * math.sin(_bph[bi])
    if abs(br) > 1e-3:
        for k, a in (("lelb", 1.8), ("relb", 1.8), ("lhand", 1.1), ("rhand", 1.1)): _add(p, k, 0, -a * br)
    sc = p.get("saccade", 0.0)
    if sc > 0.01:
        sx_, sy_ = _saccade(t); p["look"] = (p["look"][0] + sx_ * sc, p["look"][1] + sy_ * sc)
    # --- lean (rotate around the feet) and squash/stretch
    fx_ = (p["lfoot"][0] + p["rfoot"][0]) / 2
    ln, st = p.get("lean", 0.0), p.get("stretch", 0.0)
    if abs(ln) > 1e-4 or abs(st) > 1e-4:
        c, s_ = math.cos(ln), math.sin(ln)
        for k in C.JOINTS:
            if k in ("lfoot", "rfoot"): continue
            dx, dy = p[k][0] - fx_, p[k][1] - FLOOR_Y
            dx, dy = dx * (1 - 0.12 * st), dy * (1 + 0.2 * st)
            p[k] = (fx_ + dx * c - dy * s_, FLOOR_Y + dx * s_ + dy * c)
        p["squash"] = p.get("squash", 0.0) - 0.6 * st
    hop = p.get("hop", 0.0)
    for k in C.JOINTS:
        p[k] = (p[k][0] + x, p[k][1] - hop)
    if POSE_HOOK: p = POSE_HOOK(t, p)
    return C.constrain(p)

# follow-through / overlapping action: every joint is a damped spring chasing its pose target, so parts drag,
# overshoot and settle a beat after the body instead of all stopping at once. (joint: Hz, damping, amount)
LAGS = {"hip": (4.0, 0.7, 0.2), "neck": (3.2, 0.55, 0.4), "head": (2.5, 0.42, 0.7), "tilt": (2.5, 0.42, 0.7),
        "lelb": (2.7, 0.5, 0.5), "relb": (2.7, 0.5, 0.5), "lhand": (2.2, 0.4, 0.75), "rhand": (2.2, 0.4, 0.75),
        "lknee": (3.0, 0.6, 0.25), "rknee": (3.0, 0.6, 0.25), "lfoot": (2.4, 0.45, 0.8), "rfoot": (2.4, 0.45, 0.8)}
LAG_WIN = 16

def _lp(f):
    r = _PC.get(f)
    if r is None: r = _PC[f] = live_pose(f / FPS)
    return r

def _last_cut(f):
    c0 = -10 ** 9
    for c in CUT_F:
        if c <= f: c0 = c
    return c0

def filtered_pose(f):
    p0 = _lp(f)
    out = dict(p0)
    start = max(f - LAG_WIN, _last_cut(f))
    lm = p0.get("lag", 1.0)
    if not FOLLOW or lm < 0.01 or start >= f: return out
    dt = 1.0 / FPS / 2
    for j, (hz, z, amt) in LAGS.items():
        a = amt * lm
        side = j[0] if j[0] in "lr" and j[1:] in ("hand", "elb", "foot", "knee") else ""
        if j[1:] in ("hand", "elb"):
            a *= p0.get(side + "hand_lag", 1.0)
            if p0.get(side + "hand_t") in ("grip", "none"): a = 0.0     # holding something: no drag
        if j[1:] in ("foot", "knee") and j[1:] == "foot": a *= p0.get("feet_lag", 0.0)  # planted unless dangling
        if a < 0.01: continue
        w = 2 * math.pi * hz
        x = _lp(start)[j]
        if isinstance(x, tuple):
            x0, x1, v0, v1 = x[0], x[1], 0.0, 0.0
            for g in range(start + 1, f + 1):
                tx, ty = _lp(g)[j]
                for _ in range(2):
                    v0 += (w * w * (tx - x0) - 2 * z * w * v0) * dt; x0 += v0 * dt
                    v1 += (w * w * (ty - x1) - 2 * z * w * v1) * dt; x1 += v1 * dt
            tx, ty = p0[j]; out[j] = (tx + a * (x0 - tx), ty + a * (x1 - ty))
        else:
            xs, vs = x, 0.0
            for g in range(start + 1, f + 1):
                tg = _lp(g)[j]
                for _ in range(2):
                    vs += (w * w * (tg - xs) - 2 * z * w * vs) * dt; xs += vs * dt
            out[j] = p0[j] + a * (xs - p0[j])
    return C.constrain(out)

def pose_with_follow(t):
    """filtered pose + the curl lagging behind head movement and springing back."""
    f = int(round(t * FPS))
    p = filtered_pose(f)
    acc, c0 = 0.0, _last_cut(f)
    for k, w_ in ((2, 1.0), (3, 0.6), (5, 0.35)):
        if f - k - 1 < c0: continue
        q = _lp(f - k); r = _lp(f - k - 1)
        vx = (q["head"][0] - r["head"][0]) * FPS; vy = (q["head"][1] - r["head"][1]) * FPS
        acc += w_ * (-vx * 0.0011 + vy * 0.0009) * math.cos(k / FPS * 40)
    p["curl"] = p.get("curl", 0.0) + max(-0.55, min(0.55, acc))
    return p

# ------------------------------------------------------------ frame ---------
GRAIN = []
for _i in range(3):
    _gs = cairo.ImageSurface(cairo.FORMAT_ARGB32, 540, 960)
    _ga = np.ndarray((960, 540, 4), np.uint8, _gs.get_data())
    _n = np.random.default_rng(_i).random((960, 540))
    _ga[..., 0] = _ga[..., 1] = _ga[..., 2] = 0
    _ga[..., 3] = ((_n > 0.93) * (_n - 0.93) / 0.07 * 50).astype(np.uint8)
    _gs.mark_dirty(); GRAIN.append(_gs)

def world_to_screen(t, pt):
    cx, cy, z = cam_track.at(t)
    return ((pt[0] - cx) * z + W / 2, (pt[1] - cy) * z + H / 2)

def render_frame(t, surf):
    ink.BOIL = int(t * 10)        # line boil ~10 fps, like redrawn pencil
    cr = cairo.Context(surf)
    cr.set_source_rgb(*PAPER); cr.paint()
    pose = pose_with_follow(t)
    cx, cy, z = cam_track.at(t)
    cr.save()
    cr.translate(W / 2, H / 2); cr.scale(z, z); cr.translate(-cx, -cy)
    if BG: BG(cr, t)
    if FLOOR:
        sketch_line(cr, [(-1500, FLOOR_Y), (2600, FLOOR_Y)], 3.5, sid=90, amp=1.3, alpha=0.8)
        if pose.get("show", 1) > 0.01 and pose["lfoot"][1] > FLOOR_Y - 200:
            draw_shadow(cr, (pose["lfoot"][0] + pose["rfoot"][0]) / 2, scale=1 - min(0.6, pose.get("hop", 0) / 300))
    if PROPS: PROPS(cr, t, pose, "back")
    draw_guy(cr, t, pose, blink_amt(t))
    if PROPS: PROPS(cr, t, pose, "front")
    cr.restore()
    if OVERLAY: OVERLAY(cr, t)
    cr.save(); cr.scale(2, 2); cr.set_source_surface(GRAIN[ink.BOIL % 3], 0, 0); cr.paint_with_alpha(0.5); cr.restore()

# ------------------------------------------------------------ audio ---------
# Cartoon sound effects, synthesised. Everything is soft and short; the master is kept quiet (no loudnorm) so
# effects sit UNDER the picture. Episode gains of 0.2-0.6 are typical.
_rng = np.random.default_rng(1)
def _tt(dur): return np.arange(int(dur * SR)) / SR
def _onepole(s, a):
    y = np.zeros_like(s); acc = 0.0
    for i in range(len(s)):
        acc += a * (s[i] - acc); y[i] = acc
    return y
def _sweep(f0, f1, dur, shape=1.0):
    tt = _tt(dur); u = (tt / dur) ** shape
    return np.sin(2 * np.pi * np.cumsum(f0 + (f1 - f0) * u) / SR)
def _noise(dur, a=0.2):
    nz = _rng.standard_normal(len(_tt(dur))).astype(np.float32); return _onepole(nz, a)
def _env(dur, att=0.01, rel=0.05):
    tt = _tt(dur); return np.clip(tt / att, 0, 1) * np.clip((dur - tt) / rel, 0, 1)

def sfx_step():
    tt = _tt(0.11)
    return _onepole((_rng.standard_normal(len(tt)) * np.exp(-tt / 0.01) * 0.4 + np.sin(2 * np.pi * 95 * tt) * np.exp(-tt / 0.03)).astype(np.float32), 0.12) * 1.5
def sfx_tiptoe():
    tt = _tt(0.06); return (np.sin(2 * np.pi * 700 * tt) * np.exp(-tt / 0.008) * 0.4).astype(np.float32)
def sfx_zip(dur=0.32, up=True):   # cartoon 'zwip' — pulling something out of nowhere
    tt = _tt(dur); f0, f1 = (350, 1300) if up else (1200, 300)
    tone = _sweep(f0, f1, dur, 0.8) * np.exp(-((tt - dur * 0.6) / (dur * 0.45)) ** 2)
    return (tone * 0.5 + _noise(dur, 0.25) * 0.4 * np.sin(np.pi * tt / dur)).astype(np.float32)
def sfx_slide_up(dur=0.6): tt = _tt(dur); return (_sweep(300, 1400, dur, 1.3) * _env(dur, 0.03, 0.1) * (1 + 0.15 * np.sin(2 * np.pi * 7 * tt)) * 0.45).astype(np.float32)
def sfx_slide_down(dur=0.6): tt = _tt(dur); return (_sweep(1300, 260, dur, 0.8) * _env(dur, 0.03, 0.1) * (1 + 0.15 * np.sin(2 * np.pi * 7 * tt)) * 0.45).astype(np.float32)
def sfx_pop():
    tt = _tt(0.12); return (_sweep(800, 260, 0.12, 0.5) * np.exp(-tt / 0.03) + _rng.standard_normal(len(tt)) * np.exp(-tt / 0.003) * 0.3).astype(np.float32)
def sfx_boop(): tt = _tt(0.14); return (_sweep(520, 760, 0.14, 0.6) * np.exp(-tt / 0.05) * 0.6).astype(np.float32)
def sfx_tick(): tt = _tt(0.05); return (np.sin(2 * np.pi * 1600 * tt) * np.exp(-tt / 0.006) * 0.4).astype(np.float32)
def sfx_scribble(dur=0.8):
    tt = _tt(dur); nz = _rng.standard_normal(len(tt)).astype(np.float32); hp = nz - _onepole(nz, 0.3)
    strokes = 0.45 + 0.55 * np.clip(np.sin(2 * np.pi * 6.5 * tt + 2 * np.sin(2 * np.pi * 1.3 * tt)), 0, 1)
    return (_onepole(hp, 0.5) * strokes * _env(dur, 0.04, 0.08) * 0.6).astype(np.float32)
def sfx_flip(): tt = _tt(0.2); s = _noise(0.2, 0.3); return (s * np.sin(np.pi * tt / 0.2) ** 2 * 0.8 + _sweep(500, 180, 0.2) * np.exp(-tt / 0.06) * 0.2).astype(np.float32)
def sfx_blink(): tt = _tt(0.06); return (np.sin(2 * np.pi * 1900 * tt) * np.exp(-tt / 0.01) * 0.35).astype(np.float32)
def sfx_tap():
    tt = _tt(0.14); return _onepole((np.sin(2 * np.pi * 170 * tt) * np.exp(-tt / 0.035) + _rng.standard_normal(len(tt)) * np.exp(-tt / 0.005) * 0.3).astype(np.float32), 0.25) * 1.3
def sfx_pat():
    tt = _tt(0.09); return _onepole((_rng.standard_normal(len(tt)) * np.exp(-tt / 0.012)).astype(np.float32), 0.15) * 1.2
def sfx_boing(dur=0.5):
    tt = _tt(dur); f = 180 + 60 * np.sin(2 * np.pi * 9 * tt) * np.exp(-tt / 0.25) + 120 * np.exp(-tt / 0.08)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.18) * 0.7).astype(np.float32)
def sfx_whoosh(dur=0.4): tt = _tt(dur); return (_noise(dur, 0.07) * np.sin(np.pi * tt / dur) ** 2 * 2.2).astype(np.float32)
def sfx_poof(): tt = _tt(0.45); return (_noise(0.45, 0.09) * np.exp(-tt / 0.12) * 2.0 + _sweep(300, 120, 0.45) * np.exp(-tt / 0.08) * 0.3).astype(np.float32)
def sfx_thud(): tt = _tt(0.3); return (np.sin(2 * np.pi * 60 * tt) * np.exp(-tt / 0.07) + _rng.standard_normal(len(tt)) * np.exp(-tt / 0.008) * 0.2).astype(np.float32)
def sfx_skid(dur=0.35): tt = _tt(dur); nz = _rng.standard_normal(len(tt)).astype(np.float32); return ((nz - _onepole(nz, 0.2)) * _env(dur, 0.01, 0.15) * 0.35).astype(np.float32)
def sfx_rummage(dur=0.9):
    tt = _tt(dur); bursts = np.clip(np.sin(2 * np.pi * 9 * tt + 3 * np.sin(2 * np.pi * 2.1 * tt)), 0, 1) ** 2
    return (_noise(dur, 0.15) * bursts * _env(dur, 0.05, 0.1) * 1.4).astype(np.float32)
def sfx_ding(): tt = _tt(0.9); return ((np.sin(2 * np.pi * 1320 * tt) + 0.5 * np.sin(2 * np.pi * 2640 * tt)) * np.exp(-tt / 0.3) * 0.3).astype(np.float32)
def sfx_bonk(): tt = _tt(0.35); return (np.sin(2 * np.pi * np.cumsum(420 * np.exp(-tt / 0.12) + 140) / SR) * np.exp(-tt / 0.09) * 0.8).astype(np.float32)
def sfx_splat(): tt = _tt(0.3); return (_noise(0.3, 0.12) * np.exp(-tt / 0.06) * 2.2 + np.sin(2 * np.pi * 90 * tt) * np.exp(-tt / 0.05) * 0.5).astype(np.float32)
def sfx_clap(): tt = _tt(0.12); nz = _rng.standard_normal(len(tt)).astype(np.float32); return ((nz - _onepole(nz, 0.3)) * np.exp(-tt / 0.018) * 0.9).astype(np.float32)
def sfx_squeak(): tt = _tt(0.18); return (_sweep(1400, 1900, 0.18) * _env(0.18, 0.02, 0.06) * 0.25).astype(np.float32)
def sfx_gulp(): tt = _tt(0.25); return (_sweep(260, 120, 0.25, 0.6) * np.exp(-tt / 0.08) * 0.7).astype(np.float32)
def sfx_snore(dur=1.6):
    tt = _tt(dur); env = np.clip(np.sin(np.pi * tt / dur), 0, 1) ** 1.5
    buzz = np.sign(np.sin(2 * np.pi * (60 + 20 * np.sin(np.pi * tt / dur)) * tt)) * 0.5 + _noise(dur, 0.05) * 1.5
    return (_onepole(buzz.astype(np.float32), 0.06) * env * 0.9).astype(np.float32)
def sfx_twinkle(): tt = _tt(0.5); return (sum(np.sin(2 * np.pi * f * tt) * np.exp(-((tt - d) / 0.05) ** 2) for f, d in ((1760, 0.05), (2093, 0.15), (2637, 0.25))) * 0.18).astype(np.float32)
def sfx_rain(dur=3.0): return (_noise(dur, 0.4) * _env(dur, 0.5, 0.5) * 0.25).astype(np.float32)
def sfx_wind(dur=3.0): tt = _tt(dur); return (_noise(dur, 0.02) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.4 * tt)) * _env(dur, 0.6, 0.6) * 3.0).astype(np.float32)
def sfx_bubble(): tt = _tt(0.12); return (_sweep(300, 900, 0.12, 0.4) * np.exp(-tt / 0.04) * 0.5).astype(np.float32)
def sfx_spring(): return sfx_boing(0.7)
def sfx_slurp(dur=0.9):    # noodle slurp: bubbly rising suck
    tt = _tt(dur); f = 300 + 500 * (tt / dur) + 90 * np.sin(2 * np.pi * 23 * tt)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(dur, 0.05, 0.15) * (0.5 + 0.5 * np.sin(2 * np.pi * 17 * tt) ** 2) * 0.35
            + _noise(dur, 0.3) * _env(dur, 0.05, 0.2) * 0.25).astype(np.float32)
def sfx_kaboom(dur=2.6):   # big cartoon boom: low thump + rolling rumble (still rounded off, never harsh)
    tt = _tt(dur)
    thump = np.sin(2 * np.pi * np.cumsum(90 * np.exp(-tt / 0.25) + 38) / SR) * np.exp(-tt / 0.45)
    rumble = _noise(dur, 0.02) * np.exp(-tt / 0.9) * 9.0
    return ((thump + rumble) * _env(dur, 0.004, 0.6) * 0.8).astype(np.float32)
def sfx_simmer(dur=10.0):  # pot on low heat: soft bubbling bed + scattered little pops
    tt = _tt(dur); out = (_noise(dur, 0.03) * 1.3 * (0.75 + 0.25 * np.sin(2 * np.pi * 0.27 * tt))).astype(np.float32)
    r = np.random.default_rng(5); t0 = 0.0
    while True:
        t0 += r.uniform(0.04, 0.3)
        if t0 >= dur - 0.08: break
        i, m = int(t0 * SR), int(0.05 * SR); f0 = r.uniform(140, 420)
        seg = np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f0 * 1.8, m)) / SR) * np.exp(-np.arange(m) / SR / 0.012) * r.uniform(0.15, 0.5)
        out[i:i + m] += seg.astype(np.float32)
    return (out * _env(dur, 0.25, 0.4)).astype(np.float32)
def sfx_tok(): tt = _tt(0.07); return (np.sin(2 * np.pi * 820 * tt) * np.exp(-tt / 0.012) * 0.5).astype(np.float32)
def sfx_whine(dur=3.0):    # faint ear-ring that swells, then stops dead
    tt = _tt(dur); return (np.sin(2 * np.pi * (3050 + 40 * tt / dur) * tt) * (tt / dur) ** 1.6 * _env(dur, 0.3, 0.004) * 0.3).astype(np.float32)
def sfx_blub(): tt = _tt(0.18); return (_sweep(150, 480, 0.18, 0.5) * np.exp(-tt / 0.05) * 0.7).astype(np.float32)
def sfx_clack():
    tt = _tt(0.12); nz = _rng.standard_normal(len(tt)).astype(np.float32); hp = nz - _onepole(nz, 0.35)
    env = np.exp(-tt / 0.005) + 0.8 * np.exp(-np.clip(tt - 0.055, 0, None) / 0.005) * (tt > 0.055)
    return (hp * env * 0.9 + np.sin(2 * np.pi * 1250 * tt) * env * 0.3).astype(np.float32)
def sfx_drip(): tt = _tt(0.06); return (_sweep(1900, 850, 0.06) * np.exp(-tt / 0.012) * 0.4).astype(np.float32)
def sfx_sploosh():
    tt = _tt(0.7); return (_noise(0.7, 0.14) * np.exp(-tt / 0.16) * 1.8 + np.sin(2 * np.pi * 85 * tt) * np.exp(-tt / 0.07) * 0.6).astype(np.float32)
def sfx_chomp():
    tt = _tt(0.22); return (_onepole((_rng.standard_normal(len(tt)) * np.exp(-tt / 0.02)).astype(np.float32), 0.35) * 1.4
                            + np.sin(2 * np.pi * 140 * tt) * np.exp(-tt / 0.04) * 0.6).astype(np.float32)

def sfx_wah(dur=0.75):    # small baby "waah": a soft wobbling glide up then down
    tt = _tt(dur); f = 430 + 220 * np.sin(np.pi * tt / dur) ** 0.7 + 18 * np.sin(2 * np.pi * 7 * tt)
    ph = np.cumsum(f) / SR * 2 * np.pi
    return ((np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)) * _env(dur, 0.06, 0.2) * 0.35).astype(np.float32)

SYNTH = dict(step=sfx_step, tiptoe=sfx_tiptoe, zip=sfx_zip, zip_down=lambda: sfx_zip(0.26, up=False),
             slide_up=sfx_slide_up, slide_down=sfx_slide_down, pop=sfx_pop, boop=sfx_boop, tick=sfx_tick,
             scribble=sfx_scribble, flip=sfx_flip, blink=sfx_blink, tap=sfx_tap, pat=sfx_pat, boing=sfx_boing,
             whoosh=sfx_whoosh, poof=sfx_poof, thud=sfx_thud, skid=sfx_skid, rummage=sfx_rummage, ding=sfx_ding,
             bonk=sfx_bonk, splat=sfx_splat, clap=sfx_clap, squeak=sfx_squeak, gulp=sfx_gulp, snore=sfx_snore,
             twinkle=sfx_twinkle, rain=sfx_rain, wind=sfx_wind, bubble=sfx_bubble, spring=sfx_spring,
             slurp=sfx_slurp, kaboom=sfx_kaboom, chomp=sfx_chomp, simmer=sfx_simmer, tok=sfx_tok, whine=sfx_whine,
             blub=sfx_blub, clack=sfx_clack, drip=sfx_drip, sploosh=sfx_sploosh, wah=sfx_wah)
SFX_DIR = os.path.join(HERE, "..", "sfx")

def load_wav(name):
    path_ = name if os.path.isabs(name) else os.path.join(SFX_DIR, name)
    with wave.open(path_) as w:
        ch, sr = w.getnchannels(), w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    if ch > 1: a = a.reshape(-1, ch).mean(1)
    if sr != SR: a = np.interp(np.linspace(0, len(a) - 1, int(len(a) * SR / sr)), np.arange(len(a)), a).astype(np.float32)
    return a

MASTER_PEAK = 0.32      # ~ -10 dBFS peak: sound effects stay subtle
def _soften(x):
    """gentle low-pass + a little room so synthetic clicks don't bite."""
    y = np.empty_like(x); a = 0.33; acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc); y[i] = acc
    rv = np.zeros_like(y)
    for d, g in ((0.023, 0.2), (0.041, 0.14), (0.067, 0.09), (0.097, 0.05)):
        k = int(d * SR); rv[k:] += y[:-k] * g
    return y + rv

def synth_audio(out="mix.wav"):
    n = int(DURATION * SR) + SR
    mix = np.zeros(n, np.float32)
    def place(sig, t0, gain=1.0):
        i = int(t0 * SR)
        if i >= n or i < 0: return
        m = min(len(sig), n - i); mix[i:i + m] += sig[:m] * gain
    for item in SFX:
        t0, kind, gain = item[:3]
        kw = item[3] if len(item) > 3 else {}
        place(load_wav(kind) if kind.endswith(".wav") else SYNTH[kind](**kw), t0, gain)
    stp, last = sfx_step(), None
    for f in range(NFRAMES):
        x, v, ph = loco(f / FPS)
        cur = int(ph / math.pi)
        if abs(v) >= 25 and last is not None and cur != last and pose_track.at(f / FPS).get("nowalk", 0.0) < 0.5:
            place(stp, f / FPS, STEP_GAIN * min(1, abs(v) / 80) * random.Random(f).uniform(0.75, 1.1))
        last = cur
    br = np.cumsum(_rng.standard_normal(n)).astype(np.float32)   # barely-there room tone
    br -= np.convolve(br, np.ones(2048) / 2048, mode="same"); br /= np.abs(br).max() + 1e-9
    mix = _soften(mix) + br * 0.006
    mix = mix[: int(DURATION * SR)]
    mix[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    mix *= MASTER_PEAK / max(1e-6, np.abs(mix).max())
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())

# ------------------------------------------------------------ main ----------
def main(out="episode.mp4"):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    if "--still" in sys.argv:
        for a in sys.argv[sys.argv.index("--still") + 1:]:
            t = float(a); render_frame(t, surf); surf.write_to_png(f"still_{t:05.1f}.png"); print("wrote", f"still_{t:05.1f}.png")
        return
    print(f"duration {DURATION:.2f}s, {NFRAMES} frames", flush=True)
    synth_audio("mix.wav")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", "mix.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                           "-pix_fmt", "yuv420p", "-ar", "48000", "-c:a", "aac", "-b:a", "160k",
                           "-movflags", "+faststart", "-shortest", out], stdin=subprocess.PIPE)
    for f in range(NFRAMES):
        render_frame(f / FPS, surf); surf.flush(); ff.stdin.write(bytes(surf.get_data()))
        if f % 150 == 0: print(f"frame {f}/{NFRAMES}", flush=True)
    ff.stdin.close(); ff.wait()
    print("done ->", out)
