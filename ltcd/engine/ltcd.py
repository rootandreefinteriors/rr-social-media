r"""LET THE COMMENTS DECIDE — render engine.

Same hand-drawn world as Nigel Bane (ink line boil, paper grain, white void, floor line) but the hero is a plain,
nameless stick figure: round head, dot eyes, simple mouth, optional brows. No voice — the show is silent apart from
cartoon sound effects (synthesised here, or WAV files dropped in ../sfx/).

Pure python: pycairo + numpy + Pillow + ffmpeg (runs on the laptop and in the cloud routine).

An episode script:
    import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "engine"))
    import ltcd as L
    pose = L.Track([...]); xt = L.Track([...]); cam = L.Track([...])
    L.configure(duration=22.0, pose_track=pose, x_track=xt, cam_track=cam,
                props=my_props, pose_hook=my_hook, sfx=[(t, "pop", 0.5), ...], blinks=[...], comment=None)
    L.main("ep001.mp4")          # or:  python episode.py --still 3 6 10   -> still_*.png

Building blocks for episode scripts: Track, P (poses), draw_clipboard, sign_surface, draw_poof, motion_lines,
draw_comment_card, sketch_line, sketch_circle, stroke_ink, fill_paper. Colour is allowed (pass rgb tuples) but the
default world is black ink on white paper.
"""
import cairo, numpy as np, wave, math, subprocess, sys, random, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, SR = 1080, 1920, 30, 44100
INK = (0.07, 0.07, 0.08)
PAPER = (0.985, 0.984, 0.978)
FLOOR_Y = 1478
FONT_MARKER = os.path.join(HERE, "fonts", "PermanentMarker-Regular.ttf")
SAFE = (60, 200, 920, 1480)   # screen box clear of TikTok / Reels UI (right rail, caption block)

# ------------------------------------------------------------------ utils ---
def smooth(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)

def ramp(t, t0, t1):
    """0 before t0, 1 after t1, smoothstep between."""
    return smooth((t - t0) / max(1e-6, t1 - t0))

def back_out(u, s=1.7):
    """overshoot ease (cartoon spring)."""
    u = min(1.0, max(0.0, u)); u -= 1; return u * u * ((s + 1) * u + s) + 1

def lerp(a, b, u):
    if isinstance(a, dict): return {k: lerp(a[k], b[k], u) for k in a}
    if isinstance(a, (tuple, list)): return tuple(lerp(x, y, u) for x, y in zip(a, b))
    return a + (b - a) * u

class Track:
    """keys: (time, value, transition_seconds). Value eases from the previous state starting at time."""
    def __init__(self, keys): self.keys = sorted(keys, key=lambda k: k[0])
    def at(self, t):
        cur = self.keys[0][1]
        for kt, kv, kd in self.keys[1:]:
            if t < kt: break
            cur = lerp(cur, kv, smooth((t - kt) / max(kd, 1e-3)))
        return cur

# ------------------------------------------------------------------ poses ---
# Front-facing stick figure standing at x=540 (body offset 0). World units == screen pixels at zoom 1.
HEAD_R = 88
BASE = dict(head=(540, 690), neck=(540, 782), hip=(540, 1135),
            lelb=(492, 975), lhand=(470, 1110), relb=(588, 975), rhand=(610, 1110),
            lknee=(516, 1305), lfoot=(494, FLOOR_Y), rknee=(564, 1305), rfoot=(586, FLOOR_Y),
            tilt=0.0, look=(0.0, 0.0), brow=0.0, mouth=0.0, eyescale=1.0, swing=1.0, squash=0.0, show=1.0)
def P(base=BASE, **kw):
    d = dict(base); d.update(kw); return d
STAND = P()

# --------------------------------------------------------------- sketching ---
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
    for p in pts[1:]: cr.line_to(*p)

def circle_pts(cx, cy, r, sid=0, n=72, amp=0.008):
    p1, p2 = wob(sid, 1) * 6, wob(sid, 2) * 6
    return [(cx + r * (1 + amp * math.sin(3 * a + p1) + amp * 0.6 * math.sin(5 * a + p2)) * math.cos(a),
             cy + r * (1 + amp * math.sin(3 * a + p1) + amp * 0.6 * math.sin(5 * a + p2)) * math.sin(a))
            for a in [2 * math.pi * i / n for i in range(n + 1)]]

def stroke_ink(cr, width, color=INK, alpha=1.0):
    cr.set_source_rgba(*color, alpha); cr.set_line_width(width)
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND); cr.stroke()

def fill_paper(cr, color=PAPER, alpha=1.0):
    cr.set_source_rgba(*color, alpha); cr.fill_preserve()

def sketch_line(cr, pts, width=8, sid=0, amp=1.6, color=INK, alpha=1.0):
    path(cr, sketch_pts(pts, amp=amp, sid=sid)); stroke_ink(cr, width, color, alpha)

def sketch_circle(cr, cx, cy, r, width=8, sid=0, fill=PAPER, color=INK, alpha=1.0):
    path(cr, circle_pts(cx, cy, r, sid=sid))
    if fill is not None: fill_paper(cr, fill, alpha)
    stroke_ink(cr, width, color, alpha)

def sketch_rect(cr, x0, y0, x1, y1, width=7, sid=0, fill=PAPER, color=INK, alpha=1.0, amp=1.4):
    pts = sketch_pts([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], amp=amp, sid=sid, step=24)
    path(cr, pts); cr.close_path()
    if fill is not None: fill_paper(cr, fill, alpha)
    stroke_ink(cr, width, color, alpha)

# ------------------------------------------------------------- the guy -----
def draw_guy(cr, t, p, blink):
    """plain stick figure. p = live pose in world coords."""
    if p.get("show", 1.0) < 0.01: return
    g = lambda k: p[k]
    hx, hy = g("head")
    breath = math.sin(t * 1.7) * 2.5
    hy += breath
    nk = (g("neck")[0], g("neck")[1] + breath * 0.5)
    hip = g("hip")
    sh = lerp(nk, hip, 0.13)
    for i, l in enumerate([[hip, g("lknee"), g("lfoot")], [hip, g("rknee"), g("rfoot")], [nk, hip],
                           [sh, g("lelb"), g("lhand")], [sh, g("relb"), g("rhand")]]):
        path(cr, sketch_pts(l, amp=1.7, sid=11 + i * 5)); stroke_ink(cr, 8)
    sketch_line(cr, [nk, (hx, hy + HEAD_R - 4)], 8, sid=9, amp=1)
    cr.save(); cr.translate(hx, hy); cr.rotate(g("tilt"))
    sq = p.get("squash", 0.0)
    cr.scale(1 + 0.12 * sq, 1 - 0.12 * sq)
    sketch_circle(cr, 0, 0, HEAD_R, 8, sid=3)
    lx, ly = p["look"]
    fx, fy = lx * 26, ly * 22
    es = p["eyescale"]
    for side in (-1, 1):
        ex, ey = side * 30 + fx, -8 + fy
        cr.save(); cr.translate(ex, ey); cr.scale(es, es * max(0.08, 1 - blink))
        cr.arc(0, 0, 9.5, 0, 2 * math.pi); cr.set_source_rgb(*INK); cr.fill()
        cr.restore()
        if blink > 0.6:
            cr.move_to(ex - 10, ey); cr.line_to(ex + 10, ey); stroke_ink(cr, 4.5)
        b = p["brow"]          # >0 raised/expectant, <0 cross/impatient
        if abs(b) > 0.04:
            if b > 0:   # raised, evenly, a little arched (expectant / surprised)
                inner = (ex - side * 12, ey - 24 - b * 14); outer = (ex + side * 13, ey - 23 - b * 11)
                mid = ((inner[0] + outer[0]) / 2, min(inner[1], outer[1]) - 4)
                cr.move_to(*inner); cr.curve_to(mid[0], mid[1], mid[0], mid[1], *outer)
            else:       # cross / impatient: inner ends pulled down
                inner = (ex - side * 12, ey - 20 + abs(b) * 6); outer = (ex + side * 14, ey - 27 - abs(b) * 5)
                cr.move_to(*inner); cr.line_to(*outer)
            stroke_ink(cr, 4.5, alpha=min(1.0, abs(b) * 3))
    m = p["mouth"]             # >0 smile, <0 frown, around 0 a flat little line
    mx, my = fx * 0.7, 36 + fy * 0.6
    cr.move_to(mx - 16, my); cr.curve_to(mx - 6, my + 12 * m, mx + 6, my + 12 * m, mx + 16, my)
    stroke_ink(cr, 4.5)
    cr.restore()

# ------------------------------------------------------------ props -------
_surf_cache = {}
def text_surface(text, size, font=FONT_MARKER, color=(18, 18, 22), max_w=None, lines=None, line_gap=0.98, align="center"):
    """multi-line marker lettering as a cairo surface (premultiplied BGRA). returns (surf, w, h)."""
    key = (text, size, font, color, max_w, tuple(lines) if lines else None, line_gap, align)
    if key in _surf_cache: return _surf_cache[key][0], _surf_cache[key][2], _surf_cache[key][3]
    f = ImageFont.truetype(font, size)
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    if lines is None:
        lines, cur = [], ""
        for w_ in text.split():
            nxt = (cur + " " + w_).strip()
            if max_w and probe.textlength(nxt, font=f) > max_w and cur:
                lines.append(cur); cur = w_
            else:
                cur = nxt
        if cur: lines.append(cur)
    lh = int(size * 1.25 * line_gap)
    tw = int(max(probe.textlength(l, font=f) for l in lines)) + 40
    th = lh * len(lines) + int(size * 0.5)
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        lw = probe.textlength(l, font=f)
        x = (tw - lw) / 2 if align == "center" else 20
        d.text((x, 10 + i * lh), l, font=f, fill=color + (255,))
    a = np.array(img).astype(np.float32); al = a[..., 3:4] / 255
    bgra = np.ascontiguousarray(np.concatenate([a[..., 2:3] * al, a[..., 1:2] * al, a[..., 0:1] * al, a[..., 3:4]], 2).astype(np.uint8))
    s = cairo.ImageSurface.create_for_data(memoryview(bgra), cairo.FORMAT_ARGB32, tw, th, tw * 4)
    _surf_cache[key] = (s, bgra, tw, th)
    return s, tw, th

def fit_text(text, box_w, box_h, lines=None, start=140):
    for size in range(start, 30, -4):
        s, tw, th = text_surface(text, size, max_w=box_w, lines=lines)
        if tw - 40 <= box_w and th - size * 0.4 <= box_h: return s, tw, th
    return text_surface(text, 30, max_w=box_w - 40, lines=lines)

def draw_clip(cr, x, top, s=1.0):
    """the metal clip at the top of a clipboard (ink drawing)."""
    sketch_rect(cr, x - 70 * s, top - 22 * s, x + 70 * s, top + 26 * s, 6, sid=301)
    cr.arc(x, top - 22 * s, 24 * s, math.pi, 2 * math.pi); stroke_ink(cr, 6)
    cr.arc(x, top - 22 * s, 11 * s, math.pi, 2 * math.pi); stroke_ink(cr, 4)

def draw_clipboard(cr, cx, cy, w, h, rot=0.0, flip=0.0, front=None, clip_y=None, alpha=1.0):
    """clipboard centred at (cx,cy). flip: 0 = back towards camera ... 1 = front (sign) towards camera.
    front: callable(cr, w, h) drawing the sign content centred at 0,0 (paper coords).
    clip_y: only draw above this world y (used while it's being pulled out of the 'pocket')."""
    sx = math.cos(math.pi * flip)
    if abs(sx) < 0.02: sx = 0.02 if sx >= 0 else -0.02
    cr.save()
    if clip_y is not None:
        cr.rectangle(-5000, -5000, 10000, clip_y + 5000); cr.clip()
    cr.translate(cx, cy); cr.rotate(rot); cr.scale(abs(sx), 1)
    cr.push_group()
    sketch_rect(cr, -w / 2, -h / 2, w / 2, h / 2, 7, sid=300)
    if sx < 0:   # front: a sheet of paper on the board + whatever is written on it
        sketch_rect(cr, -w / 2 + 26, -h / 2 + 46, w / 2 - 26, h / 2 - 22, 4, sid=310, amp=1.0)
        if front: front(cr, w - 52, h - 68)
    else:        # back: a couple of board hatch lines so it reads as a back
        for k in range(3):
            yy = -h / 2 + h * (0.3 + 0.2 * k)
            sketch_line(cr, [(-w / 2 + 40, yy), (-w / 2 + 120, yy - 40)], 3, sid=320 + k, alpha=0.35)
    draw_clip(cr, 0, -h / 2 + 10, 0.72)
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha)
    cr.restore()

def sign_front(text, lines=None):
    """returns a front() callable for draw_clipboard that writes TEXT in big marker letters."""
    def f(cr, w, h):
        s, tw, th = fit_text(text, w - 30, h - 40, lines=lines)
        jx, jy = wob(77, 4) * 1.5, wob(78, 5) * 1.5
        cr.save(); cr.translate(-tw / 2 + jx, -th / 2 + 18 + jy)
        cr.set_source_surface(s, 0, 0); cr.paint(); cr.restore()
    return f

def draw_pen(cr, x, y, ang=-0.6, s=1.0, alpha=1.0):
    cr.save(); cr.translate(x, y); cr.rotate(ang)
    sketch_rect(cr, -8 * s, -70 * s, 8 * s, 10 * s, 5, sid=330, alpha=alpha)
    cr.move_to(-8 * s, 10 * s); cr.line_to(0, 30 * s); cr.line_to(8 * s, 10 * s); stroke_ink(cr, 5, alpha=alpha)
    cr.restore()

def motion_lines(cr, x, y, ang, n=3, length=60, spread=26, alpha=1.0, sid=0):
    """cartoon speed lines trailing at angle ang (radians) from (x,y)."""
    for k in range(n):
        off = (k - (n - 1) / 2) * spread
        ox, oy = -math.sin(ang) * off, math.cos(ang) * off
        L = length * (0.7 + 0.3 * wob(sid + k, 2))
        sketch_line(cr, [(x + ox, y + oy), (x + ox + math.cos(ang) * L, y + oy + math.sin(ang) * L)], 4, sid=sid + k,
                    amp=0.8, alpha=alpha)

def draw_poof(cr, x, y, u, r=120, sid=0):
    """cartoon poof cloud. u: 0..1 life."""
    if not (0 < u < 1): return
    a = 1 - smooth((u - 0.55) / 0.45)
    rr = r * (0.4 + 0.8 * back_out(min(1, u * 2.2)))
    for k in range(7):
        ang = k / 7 * 2 * math.pi + sid
        bx, by = x + math.cos(ang) * rr * 0.55, y + math.sin(ang) * rr * 0.45
        sketch_circle(cr, bx, by, rr * (0.38 + 0.08 * math.sin(k * 2.3)), 5, sid=sid + k, alpha=a)
    sketch_circle(cr, x, y, rr * 0.5, 5, sid=sid + 9, alpha=a)

def draw_comment_card(cr, username, text, likes=None, platform=None, x=None, y=None, w=430, alpha=1.0):
    """the winning comment, pinned top-right (screen space, inside the safe zone)."""
    x = SAFE[2] - w if x is None else x
    y = SAFE[1] + 10 if y is None else y
    s_user, uw, uh = text_surface("@" + username, 34, max_w=w - 120, align="left")
    s_txt, tw, th = text_surface(text, 34, max_w=w - 50, align="left", font=FONT_MARKER)
    hgt = 30 + uh + th + (40 if likes is not None else 10)
    cr.save()
    cr.push_group()
    sketch_rect(cr, x, y, x + w, y + hgt, 5, sid=900, fill=(1, 1, 1))
    sketch_circle(cr, x + 42, y + 42, 22, 4, sid=901)
    cr.set_source_surface(s_user, x + 70, y + 14); cr.paint()
    cr.set_source_surface(s_txt, x + 10, y + 18 + uh); cr.paint()
    if likes is not None:
        s_l, lw, lh = text_surface("♥ " + str(likes), 30, align="left")
        cr.set_source_surface(s_l, x + w - lw - 10, y + hgt - 46); cr.paint()
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha)
    cr.restore()

# ------------------------------------------------------------ episode config ---
pose_track = x_track = cam_track = None
PROPS = POSE_HOOK = OVERLAY = None
SFX = []; BLINKS = []; DURATION = 0.0; NFRAMES = 0
FLOOR = True

def configure(duration, pose_track, x_track, cam_track, props=None, pose_hook=None, overlay=None,
              sfx=(), blinks=None, floor=True, step_gain=0.16):
    """props(cr, t, pose, layer) is called with layer 'back' (behind him), 'front' (over him).
    overlay(cr, t) draws in screen space (e.g. the pinned comment card)."""
    g = globals()
    g.update(pose_track=pose_track, x_track=x_track, cam_track=cam_track, PROPS=props, POSE_HOOK=pose_hook,
             OVERLAY=overlay, SFX=list(sfx), DURATION=duration, NFRAMES=int(duration * FPS), FLOOR=floor,
             STEP_GAIN=step_gain)
    if blinks is None:
        rng = random.Random(7); b, bt = [], 1.4
        while bt < duration: b.append(bt); bt += rng.uniform(2.2, 4.5)
        blinks = b
    g["BLINKS"] = list(blinks)
    global _lx, _lv, _lph
    _lx = np.array([x_track.at((f - PRE) / FPS) for f in range(NFRAMES + PRE + 4)])
    _lv = np.gradient(_lx) * FPS
    _lph = np.cumsum(np.abs(_lv) / FPS / 80.0 * math.pi)

def blink_amt(t):
    b = 0.0
    for t0 in BLINKS:
        d = t - t0
        if 0 <= d < 0.16: b = max(b, 1 - abs(d - 0.08) / 0.08)
    return b

PRE = 60
_lx = _lv = _lph = None
def loco(t):
    i = min(max(int(round(t * FPS)) + PRE, 0), len(_lx) - 1)
    return _lx[i], _lv[i], _lph[i]

def live_pose(t):
    p = dict(pose_track.at(t))
    x, v, ph = loco(t)
    wk = min(1.0, abs(v) / 50.0)
    d = 1 if v >= 0 else -1
    if wk > 0.001:   # walk cycle driven by horizontal speed (bouncy, cartoony)
        bob = 10 * abs(math.sin(ph)) * wk
        hipx, hipy = p["hip"]
        for side, off in (("l", 0.0), ("r", math.pi)):
            s = math.sin(ph + off)
            lift = max(0.0, math.cos(ph + off)) * 34
            foot = (hipx + 58 * s, FLOOR_Y - lift)
            knee = ((hipx + foot[0]) / 2 + d * 20, (hipy + FLOOR_Y) / 2 - lift * 0.45)
            p[side + "foot"] = lerp(p[side + "foot"], foot, wk)
            p[side + "knee"] = lerp(p[side + "knee"], knee, wk)
        sw = wk * p["swing"]
        if sw > 0.001:
            for side, off in (("l", math.pi), ("r", 0.0)):
                s = math.sin(ph + off)
                p[side + "hand"] = lerp(p[side + "hand"], (p[side + "hand"][0] + 40 * s, p[side + "hand"][1] - 8 * abs(s)), sw)
                p[side + "elb"] = lerp(p[side + "elb"], (p[side + "elb"][0] + 16 * s, p[side + "elb"][1]), sw)
        for k in ("head", "neck", "hip", "lelb", "relb", "lhand", "rhand"):
            p[k] = (p[k][0], p[k][1] + bob)
        p["look"] = (p["look"][0] + 0.55 * d * wk, p["look"][1])
        p["tilt"] += 0.06 * d * wk
    for k in ("head", "neck", "hip", "lelb", "lhand", "relb", "rhand", "lknee", "lfoot", "rknee", "rfoot"):
        p[k] = (p[k][0] + x, p[k][1])
    if POSE_HOOK: p = POSE_HOOK(t, p)
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
    global BOIL
    BOIL = int(t * 10)            # line boil ~10 fps, like redrawn pencil
    cr = cairo.Context(surf)
    cr.set_source_rgb(*PAPER); cr.paint()
    pose = live_pose(t)
    cx, cy, z = cam_track.at(t)
    cr.save()
    cr.translate(W / 2, H / 2); cr.scale(z, z); cr.translate(-cx, -cy)
    if FLOOR:
        sketch_line(cr, [(-1500, FLOOR_Y), (2600, FLOOR_Y)], 3.5, sid=90, amp=1.3, alpha=0.8)
        if pose.get("show", 1) > 0.01:
            x = (pose["lfoot"][0] + pose["rfoot"][0]) / 2
            for k in range(3):
                w_ = 62 - k * 16
                cr.move_to(x - w_ + k * 6, FLOOR_Y + 9 + k * 7); cr.line_to(x + w_ - k * 4, FLOOR_Y + 9 + k * 7)
                stroke_ink(cr, 2, alpha=0.35)
    if PROPS: PROPS(cr, t, pose, "back")
    draw_guy(cr, t, pose, blink_amt(t))
    if PROPS: PROPS(cr, t, pose, "front")
    cr.restore()
    if OVERLAY: OVERLAY(cr, t)
    cr.save(); cr.scale(2, 2); cr.set_source_surface(GRAIN[BOIL % 3], 0, 0); cr.paint_with_alpha(0.5); cr.restore()

# ------------------------------------------------------------ audio ---------
_rng = np.random.default_rng(1)
def _tt(dur): return np.arange(int(dur * SR)) / SR
def _onepole(s, a):
    y = np.zeros_like(s); acc = 0.0
    for i in range(len(s)):
        acc += a * (s[i] - acc); y[i] = acc
    return y
def _sweep(f0, f1, dur, shape=1.0):
    tt = _tt(dur); u = (tt / dur) ** shape
    f = f0 + (f1 - f0) * u
    return np.sin(2 * np.pi * np.cumsum(f) / SR)

def sfx_step():
    tt = _tt(0.11)
    s = _rng.standard_normal(len(tt)) * np.exp(-tt / 0.01) * 0.5 + np.sin(2 * np.pi * 95 * tt) * np.exp(-tt / 0.03)
    return _onepole(s.astype(np.float32), 0.14) * 1.7
def sfx_zip(dur=0.32, up=True):      # cartoon 'zwip' — pulling something out of nowhere
    tt = _tt(dur)
    f0, f1 = (350, 1500) if up else (1400, 300)
    tone = _sweep(f0, f1, dur, 0.8) * np.exp(-((tt - dur * 0.6) / (dur * 0.45)) ** 2)
    nz = _rng.standard_normal(len(tt)); nz = nz - _onepole(nz, 0.3)
    return (tone * 0.6 + nz * 0.25 * np.sin(np.pi * tt / dur)).astype(np.float32)
def sfx_pop():
    tt = _tt(0.12)
    return (_sweep(900, 260, 0.12, 0.5) * np.exp(-tt / 0.03) + _rng.standard_normal(len(tt)) * np.exp(-tt / 0.004) * 0.6).astype(np.float32)
def sfx_scribble(dur=0.8):
    tt = _tt(dur)
    nz = _rng.standard_normal(len(tt)).astype(np.float32); hp = nz - _onepole(nz, 0.35)
    strokes = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 7.5 * tt + 2 * np.sin(2 * np.pi * 1.3 * tt)))
    env = np.clip(tt / 0.03, 0, 1) * np.clip((dur - tt) / 0.05, 0, 1)
    return (hp * strokes * env * 0.8).astype(np.float32)
def sfx_flip():
    tt = _tt(0.2)
    nz = _rng.standard_normal(len(tt)).astype(np.float32)
    s = nz - _onepole(nz, 0.15)
    return (s * np.sin(np.pi * tt / 0.2) ** 2 * 0.7 + _sweep(500, 180, 0.2) * np.exp(-tt / 0.06) * 0.3).astype(np.float32)
def sfx_blink():
    tt = _tt(0.07)
    return (np.sin(2 * np.pi * 2300 * tt) * np.exp(-tt / 0.012) * 0.5 + np.sin(2 * np.pi * 3450 * tt) * np.exp(-tt / 0.008) * 0.25).astype(np.float32)
def sfx_tap():                       # cardboard tap / sign bump
    tt = _tt(0.14)
    s = np.sin(2 * np.pi * 170 * tt) * np.exp(-tt / 0.035) + _rng.standard_normal(len(tt)) * np.exp(-tt / 0.006) * 0.4
    return _onepole(s.astype(np.float32), 0.25) * 1.4
def sfx_boing(dur=0.5):
    tt = _tt(dur)
    f = 180 + 60 * np.sin(2 * np.pi * 9 * tt) * np.exp(-tt / 0.25) + 120 * np.exp(-tt / 0.08)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.18)).astype(np.float32)
def sfx_whoosh(dur=0.4):
    tt = _tt(dur)
    nz = _rng.standard_normal(len(tt)).astype(np.float32); s = _onepole(nz, 0.08)
    return (s * np.sin(np.pi * tt / dur) ** 2 * 2.5).astype(np.float32)
def sfx_poof():
    tt = _tt(0.45)
    nz = _rng.standard_normal(len(tt)).astype(np.float32); s = _onepole(nz, 0.1)
    return (s * np.exp(-tt / 0.12) * 2.2 + _sweep(300, 120, 0.45) * np.exp(-tt / 0.08) * 0.4).astype(np.float32)
def sfx_thud():
    tt = _tt(0.3)
    return (np.sin(2 * np.pi * 60 * tt) * np.exp(-tt / 0.07) + _rng.standard_normal(len(tt)) * np.exp(-tt / 0.01) * 0.3).astype(np.float32)
SYNTH = dict(step=sfx_step, zip=sfx_zip, zip_down=lambda: sfx_zip(0.26, up=False), pop=sfx_pop, scribble=sfx_scribble,
             flip=sfx_flip, blink=sfx_blink, tap=sfx_tap, boing=sfx_boing, whoosh=sfx_whoosh, poof=sfx_poof, thud=sfx_thud)
SFX_DIR = os.path.join(HERE, "..", "sfx")

def load_wav(name):
    path_ = name if os.path.isabs(name) else os.path.join(SFX_DIR, name)
    with wave.open(path_) as w:
        ch, sw, sr = w.getnchannels(), w.getsampwidth(), w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    if ch > 1: a = a.reshape(-1, ch).mean(1)
    if sr != SR: a = np.interp(np.linspace(0, len(a) - 1, int(len(a) * SR / sr)), np.arange(len(a)), a).astype(np.float32)
    return a

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
        if kind.endswith(".wav"): sig = load_wav(kind)
        else: sig = SYNTH[kind](**kw)
        place(sig, t0, gain)
    stp, last = sfx_step(), None
    for f in range(NFRAMES):
        x, v, ph = loco(f / FPS)
        cur = int(ph / math.pi)
        if abs(v) >= 25 and last is not None and cur != last:
            place(stp, f / FPS, STEP_GAIN * min(1, abs(v) / 80) * random.Random(f).uniform(0.75, 1.1))
        last = cur
    br = np.cumsum(_rng.standard_normal(n)).astype(np.float32)   # barely-there room tone
    br -= np.convolve(br, np.ones(2048) / 2048, mode="same"); br /= np.abs(br).max() + 1e-9
    mix += br * 0.01
    mix = mix[: int(DURATION * SR)]
    mix[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    mix *= 0.95 / max(1e-6, np.abs(mix).max())
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
                           "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac",
                           "-b:a", "192k", "-movflags", "+faststart", "-shortest", out], stdin=subprocess.PIPE)
    for f in range(NFRAMES):
        render_frame(f / FPS, surf); surf.flush(); ff.stdin.write(bytes(surf.get_data()))
        if f % 150 == 0: print(f"frame {f}/{NFRAMES}", flush=True)
    ff.stdin.close(); ff.wait()
    print("done ->", out)
