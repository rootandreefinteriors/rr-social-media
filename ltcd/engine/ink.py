"""ink — hand-drawn line primitives + timing/easing shared by every part of the LTCD engine.

Everything boils (re-wobbles) ~10x a second via the module global BOIL, set by the renderer each frame.
"""
import cairo, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, SR = 1080, 1920, 30, 44100
INK = (0.07, 0.07, 0.08)
PAPER = (0.985, 0.984, 0.978)
WHITE = (1.0, 1.0, 1.0)
FLOOR_Y = 1478
FONT_MARKER = os.path.join(HERE, "fonts", "PermanentMarker-Regular.ttf")
SAFE = (60, 200, 920, 1480)   # screen box clear of TikTok / Reels UI (right rail, caption block)
BOIL = 0

# ---------------------------------------------------------------- easing ---
def clamp01(x): return min(1.0, max(0.0, x))
def smooth(x): x = clamp01(x); return x * x * (3 - 2 * x)
def ease_out(x): x = clamp01(x); return 1 - (1 - x) ** 3
def ease_in(x): x = clamp01(x); return x ** 3
def back_out(u, s=1.7):
    u = clamp01(u) - 1; return u * u * ((s + 1) * u + s) + 1
def elastic_out(u):
    u = clamp01(u)
    if u in (0.0, 1.0): return u
    return 2 ** (-10 * u) * math.sin((u * 10 - 0.75) * (2 * math.pi) / 3) + 1
def bounce_out(u):
    u = clamp01(u); n, d = 7.5625, 2.75
    if u < 1 / d: return n * u * u
    if u < 2 / d: u -= 1.5 / d; return n * u * u + 0.75
    if u < 2.5 / d: u -= 2.25 / d; return n * u * u + 0.9375
    u -= 2.625 / d; return n * u * u + 0.984375
def snap(u): u = clamp01(u); return 1 - (1 - u) ** 5          # cartoon "snap" into a pose
EASE = dict(smooth=smooth, out=ease_out, inn=ease_in, back=back_out, elastic=elastic_out, bounce=bounce_out,
            snap=snap, linear=clamp01, hold=lambda u: 1.0 if u >= 1 else 0.0)

def ramp(t, t0, t1, ease="smooth"):
    """0 before t0, 1 after t1, eased between."""
    return EASE[ease]((t - t0) / max(1e-6, t1 - t0))

def pulse(t, t0, width=0.08):
    """gaussian bump centred on t0 (for quick hits: taps, bumps, nods)."""
    return math.exp(-((t - t0) / width) ** 2)

def lerp(a, b, u):
    if isinstance(a, str) or isinstance(b, str): return b if u >= 0.5 else a
    if isinstance(a, dict):
        return {k: lerp(a.get(k, b.get(k)), b.get(k, a.get(k)), u) for k in set(a) | set(b)}
    if isinstance(a, (tuple, list)): return tuple(lerp(x, y, u) for x, y in zip(a, b))
    return a + (b - a) * u

class Track:
    """keys: (time, value, transition_seconds[, ease]). Value eases from the previous state starting at time.
    ease: smooth (default) | out | inn | back (overshoot) | elastic | bounce | snap | linear | hold."""
    def __init__(self, keys):
        self.keys = sorted([k if len(k) == 4 else (k[0], k[1], k[2], "smooth") for k in keys], key=lambda k: k[0])
    def at(self, t):
        cur = self.keys[0][1]
        for kt, kv, kd, ke in self.keys[1:]:
            if t < kt: break
            cur = lerp(cur, kv, EASE[ke]((t - kt) / max(kd, 1e-3)))
        return cur

# --------------------------------------------------------------- sketching ---
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

def bez(p0, c, p1, n=14):
    """quadratic bezier sampled to a polyline (rubber-hose limbs)."""
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * c[0] + u * u * p1[0],
             (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * c[1] + u * u * p1[1]) for u in [i / n for i in range(n + 1)]]

def stroke_ink(cr, width, color=INK, alpha=1.0):
    cr.set_source_rgba(*color, alpha); cr.set_line_width(width)
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND); cr.stroke()

def fill_paper(cr, color=PAPER, alpha=1.0):
    cr.set_source_rgba(*color, alpha); cr.fill_preserve()

def fill_ink(cr, color=INK, alpha=1.0):
    cr.set_source_rgba(*color, alpha); cr.fill_preserve()

def sketch_line(cr, pts, width=8, sid=0, amp=1.6, color=INK, alpha=1.0):
    path(cr, sketch_pts(pts, amp=amp, sid=sid)); stroke_ink(cr, width, color, alpha)

def sketch_curve(cr, p0, c, p1, width=8, sid=0, amp=1.2, color=INK, alpha=1.0):
    path(cr, sketch_pts(bez(p0, c, p1), amp=amp, sid=sid, step=14)); stroke_ink(cr, width, color, alpha)

def sketch_circle(cr, cx, cy, r, width=8, sid=0, fill=PAPER, color=INK, alpha=1.0):
    path(cr, circle_pts(cx, cy, r, sid=sid)); cr.close_path()
    if fill is not None: fill_paper(cr, fill, alpha)
    stroke_ink(cr, width, color, alpha)

def ellipse(cr, cx, cy, rx, ry, rot=0.0, sid=0, amp=0.012):
    """sketchy ellipse PATH (caller fills/strokes)."""
    pts = circle_pts(0, 0, 1, sid=sid, n=48, amp=amp)
    c, s_ = math.cos(rot), math.sin(rot)
    path(cr, [(cx + (x * rx) * c - (y * ry) * s_, cy + (x * rx) * s_ + (y * ry) * c) for x, y in pts]); cr.close_path()

def sketch_ellipse(cr, cx, cy, rx, ry, width=6, rot=0.0, sid=0, fill=PAPER, color=INK, alpha=1.0):
    ellipse(cr, cx, cy, rx, ry, rot, sid)
    if fill is not None: fill_paper(cr, fill, alpha)
    stroke_ink(cr, width, color, alpha)

def sketch_rect(cr, x0, y0, x1, y1, width=7, sid=0, fill=PAPER, color=INK, alpha=1.0, amp=1.4):
    pts = sketch_pts([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], amp=amp, sid=sid, step=24)
    path(cr, pts); cr.close_path()
    if fill is not None: fill_paper(cr, fill, alpha)
    stroke_ink(cr, width, color, alpha)

def sketch_poly(cr, pts, width=6, sid=0, fill=PAPER, color=INK, alpha=1.0, amp=1.2, closed=True):
    pp = sketch_pts(list(pts) + ([pts[0]] if closed else []), amp=amp, sid=sid, step=18)
    path(cr, pp)
    if closed: cr.close_path()
    if fill is not None and closed: fill_paper(cr, fill, alpha)
    stroke_ink(cr, width, color, alpha)

# ------------------------------------------------------------ lettering ---
_surf_cache = {}
def text_surface(text, size, font=FONT_MARKER, color=(18, 18, 22), max_w=None, lines=None, line_gap=0.98, align="center"):
    """multi-line marker lettering as a cairo surface (premultiplied BGRA). returns (surf, w, h)."""
    key = (text, size, font, color, max_w, tuple(lines) if lines else None, line_gap, align)
    if key in _surf_cache: return _surf_cache[key][0], _surf_cache[key][2], _surf_cache[key][3]
    f = ImageFont.truetype(font, int(size))
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
        d.text((x, 10 + i * lh), l, font=f, fill=tuple(color) + (255,))
    a = np.array(img).astype(np.float32); al = a[..., 3:4] / 255
    bgra = np.ascontiguousarray(np.concatenate([a[..., 2:3] * al, a[..., 1:2] * al, a[..., 0:1] * al, a[..., 3:4]], 2).astype(np.uint8))
    s = cairo.ImageSurface.create_for_data(memoryview(bgra), cairo.FORMAT_ARGB32, tw, th, tw * 4)
    _surf_cache[key] = (s, bgra, tw, th)
    return s, tw, th

def fit_text(text, box_w, box_h, lines=None, start=150):
    for size in range(start, 30, -4):
        s, tw, th = text_surface(text, size, max_w=box_w, lines=lines)
        if tw - 40 <= box_w and th - size * 0.4 <= box_h: return s, tw, th
    return text_surface(text, 30, max_w=box_w, lines=lines)

def draw_text(cr, text, x, y, size=60, color=(18, 18, 22), rot=0.0, alpha=1.0, max_w=None, anchor="center"):
    """marker text centred (or left-anchored) at x,y."""
    s, tw, th = text_surface(text, size, color=color, max_w=max_w)
    cr.save(); cr.translate(x, y); cr.rotate(rot)
    ox = -tw / 2 if anchor == "center" else 0
    cr.set_source_surface(s, ox, -th / 2); cr.paint_with_alpha(alpha); cr.restore()
