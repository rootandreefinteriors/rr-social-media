"""The hand outline on OUR side of the glass (body arc, D49-52).

Something traces round Nigel's palm, flat on the glass, on the viewer's side of the screen. It is drawn in SCREEN
space (like the crack, the tape and D48's fog), so it stays where it was drawn when the camera moves.

Shared geometry, so the outline is the same shape in the same place on every day of the arc:
  CAM   the camera (cx, cy, zoom) that frames his palm exactly in the outline
  HAND  the palm pose keys (rhand, relb, palm) that fit it exactly
Use it from an episode's glass_hook:
  import hand_outline as HO
  HO.draw(cr, progress=1.0, scale=1.0, alpha=1.0, t=t)
progress 0..1 traces it (starting at the heel of the hand, round the thumb, every finger, back to the heel);
scale shrinks it about its centre (D51); alpha fades it (D52)."""
import math
import cairo
import numpy as np

W, H = 1080, 1920
CAM = (530.0, 975.0, 1.5)
HAND = dict(rhand=(703, 1052), relb=(637, 1174), palm=2.2, spread=1.0)
SPREAD = 1.0
ANG = -0.12                                   # the engine draws the open palm rotated by this
CENTER = ((HAND["rhand"][0] - CAM[0]) * CAM[2] + W / 2, (HAND["rhand"][1] - CAM[1]) * CAM[2] + H / 2)
FR = 40 * HAND["palm"] * CAM[2]               # the palm's size on screen
MARGIN = 0.10                                 # how far outside the hand the line runs (x FR)

def _silhouette(cr, fr, pad):
    """the engine's open-palm shape (fingers, thumb, palm), grown by pad px"""
    def capsule(x0, y0, ang, ln, wd):
        cr.save(); cr.translate(x0, y0); cr.rotate(ang)
        cr.move_to(-wd / 2, 0); cr.line_to(-wd / 2, -ln + wd / 2)
        cr.arc(0, -ln + wd / 2, wd / 2, math.pi, 2 * math.pi)
        cr.line_to(wd / 2, 0); cr.close_path(); cr.restore()
        cr.fill_preserve(); cr.set_line_width(2 * pad); cr.stroke()
    for fx_, ln, ang in [(fx * (1 + 0.22 * SPREAD), ln, ang * (1 + 1.5 * SPREAD))
                         for fx, ln, ang in [(-0.6, 0.95, -0.2), (-0.2, 1.18, -0.07), (0.2, 1.12, 0.06), (0.6, 0.9, 0.2)]]:
        capsule(fx_ * fr, -0.55 * fr, ang, ln * fr, 0.36 * fr)
    capsule(-0.75 * fr, 0.25 * fr, -1.05 - SPREAD * 0.25, 0.8 * fr, 0.38 * fr)
    cr.save(); cr.scale(1.0, 1.05); cr.arc(0, 0, fr * 0.92, 0, 2 * math.pi); cr.restore()
    cr.fill_preserve(); cr.set_line_width(2 * pad); cr.stroke()

def _contour():
    """ordered outline points (relative to CENTER, unrotated px), starting at the heel of the hand, going round the
    thumb first. Moore-neighbour trace of a rasterised, grown silhouette, then smoothed."""
    S = int(FR * 4.2)
    surf = cairo.ImageSurface(cairo.FORMAT_A8, S, S)
    cr = cairo.Context(surf)
    cr.translate(S / 2, S * 0.62); cr.rotate(ANG)
    cr.set_source_rgba(0, 0, 0, 1)
    _silhouette(cr, FR, FR * MARGIN)
    surf.flush()
    st = surf.get_stride()
    m = np.frombuffer(surf.get_data(), np.uint8).reshape(S, st)[:, :S] > 127
    ys, xs = np.nonzero(m)
    i = np.argmin(ys * S + xs); start = (ys[i], xs[i])
    nb = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
    pts = [start]; cur = start; d = 6
    for _ in range(S * 40):
        for k in range(8):
            dd = (d + k) % 8
            y, x = cur[0] + nb[dd][0], cur[1] + nb[dd][1]
            if 0 <= y < S and 0 <= x < S and m[y, x]:
                cur = (y, x); d = (dd + 5) % 8
                break
        if cur == start:
            break
        pts.append(cur)
    p = np.array([(x - S / 2, y - S * 0.62) for y, x in pts], np.float64)
    k = 4                                         # smooth (circular moving average), then resample evenly
    pad = np.concatenate([p[-k:], p, p[:k]])
    ker = np.ones(2 * k + 1) / (2 * k + 1)
    p = np.stack([np.convolve(pad[:, 0], ker, "valid"), np.convolve(pad[:, 1], ker, "valid")], 1)
    seg = np.hypot(*np.diff(np.vstack([p, p[:1]]), axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    L = cum[-1]; n = int(L / 4)
    u = np.linspace(0, L, n, endpoint=False)
    q = np.stack([np.interp(u, cum, np.append(p[:, 0], p[0, 0])), np.interp(u, cum, np.append(p[:, 1], p[0, 1]))], 1)
    # start at the heel of the hand (lowest point), and go round the thumb (screen left) first
    s = int(np.argmax(q[:, 1]))
    q = np.roll(q, -s, axis=0)
    if q[len(q) // 8, 0] > q[0, 0]:
        q = q[::-1]; q = np.roll(q, 1, axis=0)
    return q

PTS = _contour()

def bbox(scale=1.0, pad=30):
    x0, y0 = PTS.min(0) * scale; x1, y1 = PTS.max(0) * scale
    return (CENTER[0] + x0 - pad, CENTER[1] + y0 - pad, CENTER[0] + x1 + pad, CENTER[1] + y1 + pad)

def draw(cr, progress=1.0, scale=1.0, alpha=1.0, t=0.0, offset=(0.0, 0.0)):
    """the traced line on our side of the glass; a small pen-tip glint at its end while it's still being drawn"""
    if progress <= 0.002 or alpha <= 0.004:
        return
    n = len(PTS)
    m = max(2, int(n * min(1.0, progress)))
    boil = int(t * 10)
    rnd = np.random.default_rng(boil % 3 + 49)
    jit = rnd.normal(0, 0.55, (n, 2))
    jit = (jit + np.roll(jit, 1, 0) + np.roll(jit, -1, 0)) / 3   # a soft line boil, like the rest of the drawing
    P = PTS[:m] * scale + jit[:m] + np.array([CENTER[0] + offset[0], CENTER[1] + offset[1]])
    closed = progress >= 0.999
    def path():
        cr.move_to(*P[0])
        for x, y in P[1:]:
            cr.line_to(x, y)
        if closed:
            cr.close_path()
    cr.save()
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    path(); cr.set_source_rgba(1, 1, 1, 0.6 * alpha); cr.set_line_width(12.0); cr.stroke()   # a halo: it's on the glass
    path(); cr.set_source_rgba(0.09, 0.09, 0.12, 0.95 * alpha); cr.set_line_width(6.2); cr.stroke()
    cr.translate(-1.4, -1.6)
    path(); cr.set_source_rgba(1, 1, 1, 0.35 * alpha); cr.set_line_width(1.2); cr.stroke()  # glassy highlight
    cr.restore()
    if not closed:                                # the pen tip: a small dark bead with a glint
        x, y = P[-1]
        g = cairo.RadialGradient(x, y, 0, x, y, 16)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.55 * alpha); g.add_color_stop_rgba(1, 1, 1, 1, 0)
        cr.set_source(g); cr.arc(x, y, 16, 0, 2 * math.pi); cr.fill()
        cr.set_source_rgba(0.1, 0.1, 0.13, 0.95 * alpha); cr.arc(x, y, 4.2, 0, 2 * math.pi); cr.fill()

def screen_to_world(pt, cam):
    cx, cy, z = cam
    return ((pt[0] - W / 2) / z + cx, (pt[1] - H / 2) / z + cy)

def caption_box(cam_track, scale=1.0):
    """for configure(caption_avoid=[(t0, t1, HO.caption_box(cam_track))]): the outline, in world coords at time t"""
    def f(t):
        x0, y0, x1, y1 = bbox(scale)
        c = cam_track.at(t)
        a = screen_to_world((x0, y0), c); b = screen_to_world((x1, y1), c)
        return (a[0], a[1], b[0], b[1])
    return f

def pin(p, t, cam_track, w, offset=(0.0, 0.0), scale=1.0):
    """Pin his palm to the glass (weight w 0..1): the hand is ON the glass, so it stays put on screen and keeps its
    screen size while the camera moves; only his arm follows the room. offset (screen px) and scale move/grow the
    palm against the outline (D50: it doesn't fit)."""
    if w <= 0.001:
        return p
    cx, cy, z = cam_track.at(t)
    cx += math.sin(t * 0.37) * 4; cy += math.cos(t * 0.29) * 4     # the engine's camera drift
    sx, sy = CENTER[0] + offset[0], CENTER[1] + offset[1]
    rh = ((sx - W / 2) / z + cx, (sy - H / 2) / z + cy)
    palm = HAND["palm"] * CAM[2] / z * scale
    re = (rh[0] - 66, rh[1] + 122)
    def mix(a, b):
        return (a[0] + (b[0] - a[0]) * w, a[1] + (b[1] - a[1]) * w)
    p["rhand"] = mix(p["rhand"], rh); p["relb"] = mix(p["relb"], re)
    p["palm"] = p.get("palm", 0.0) + (palm - p.get("palm", 0.0)) * w
    p["spread"] = SPREAD
    return p

def tip(progress, scale=1.0):
    """screen position of the pen tip"""
    i = max(0, min(len(PTS) - 1, int(len(PTS) * progress) - 1))
    return (CENTER[0] + PTS[i][0] * scale, CENTER[1] + PTS[i][1] * scale)
