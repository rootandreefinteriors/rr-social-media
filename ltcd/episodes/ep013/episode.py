"""Day 13 - WAITING episode (no new comments on the day 12 posts, TikTok or Instagram). The message is the star.

FUN PARK, at the EXIT station of THE BIG ONE where day 12 left him; the kitten loafed on his head, the ride photo in
its mouth. He holds the sign up to us: TELL ME WHAT TO DO NEXT IN THE COMMENTS. Dead stare, breathing, one eye flick
down to the sign. The only beat: he turns the sign to himself and writes today's line -- "WE'LL WAIT." (him and the
cat) -- turns it back and keeps staring. The kitten slow-blinks once. Slow blink from him. Hard cut. ~21 s.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import FLOOR_Y
import numpy as np

KS = 0.62
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
HANG_X = 45700.0
Y0 = FLOOR_Y - 40
raw = catmull([(42500, Y0), (43350, Y0), (43750, Y0 - 220), (45300, Y0 - 1700), (45650, Y0 - 1890), (EDGE_X, Y0 - 1870),
               (46280, Y0 - 900), (46480, Y0 - 150), (46900, Y0), (L1X - 1, Y0)])
raw += loop_pts(L1X, L1R, L1D)
raw += catmull([(L1X + 2 * math.pi * L1D + 1, Y0), (49000, Y0), (49600, Y0 - 650), (50200, Y0), (L2X - 1, Y0)])[1:]
raw += loop_pts(L2X, L2R, L2D)
raw += catmull([(L2X + 2 * math.pi * L2D + 1, Y0), (52500, Y0), (55000, Y0)])[1:]
# resample to even spacing
TRK = [raw[0]]; SL = [0.0]
acc = 0.0
for a, b in zip(raw[:-1], raw[1:]):
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    if d < 1e-6: continue
    acc += d; TRK.append(b); SL.append(acc)
SL = np.array(SL); TX_ = np.array([p[0] for p in TRK]); TY_ = np.array([p[1] for p in TRK])
def track_at(s):
    s = max(0.0, min(SL[-1] - 1, s)); i = int(np.searchsorted(SL, s)) - 1; i = max(0, min(len(SL) - 2, i))
    u = (s - SL[i]) / max(1e-6, SL[i + 1] - SL[i])
    x = TX_[i] + (TX_[i + 1] - TX_[i]) * u; y = TY_[i] + (TY_[i + 1] - TY_[i]) * u
    j0, j1 = max(0, i - 3), min(len(SL) - 1, i + 4)
    ang = math.atan2(TY_[j1] - TY_[j0], TX_[j1] - TX_[j0])
    return x, y, ang
def s_of_x(x, after=0.0):
    for i in range(len(SL)):
        if SL[i] >= after and TX_[i] >= x: return SL[i]
    return SL[-1]
DRAW_TRK = TRK[::3]
S_START = s_of_x(43000)
S_EDGE = s_of_x(HANG_X)
S_BRAKE = s_of_x(52400, after=s_of_x(L2X + 600))
S_STOPX = 53400.0; S_STOP = s_of_x(S_STOPX, after=S_BRAKE)

XE = S_STOPX + 880; SXE = XE - 540            # exit station spot (day 12's ask)
SCREEN = (XE + 560, 830)

def park(cr, t):
    O.draw_park_world(cr, t, x0=38550, x1=70000)
    O.draw_track(cr, DRAW_TRK, FLOOR_Y)
    sx = S_STOPX
    L.sketch_rect(cr, sx - 700, FLOOR_Y - 30, sx + 700, FLOOR_Y + 40, 5, sid=13200 + int(sx) % 7, fill=(0.75, 0.66, 0.58))
    for px in (sx - 650, sx + 650):
        L.sketch_rect(cr, px - 18, FLOOR_Y - 1000, px + 18, FLOOR_Y - 30, 5, sid=13210 + int(px) % 9, fill=(0.98, 0.95, 0.9))
    L.sketch_poly(cr, [(sx - 760, FLOOR_Y - 1000), (sx, FLOOR_Y - 1160), (sx + 760, FLOOR_Y - 1000)], 6, sid=13220 + int(sx) % 5, fill=O.PARK_TEAL)
    L.sketch_rect(cr, sx - 330, FLOOR_Y - 1080, sx + 330, FLOOR_Y - 940, 5, sid=13230 + int(sx) % 5, fill=(1, 1, 0.97))
    L.draw_text(cr, "EXIT", sx, FLOOR_Y - 1010, 84, color=(200, 50, 60), max_w=620)
    O.draw_photo_screen(cr, SCREEN[0], SCREEN[1], w=640, h=480, inner=photo_inner)
    L.sketch_rect(cr, SCREEN[0] - 40, SCREEN[1] + 255, SCREEN[0] + 40, FLOOR_Y, 5, sid=13250, fill=(0.3, 0.3, 0.34))

def photo_inner(cr, x0, y0, w, h):
    """the ride photo, simplified: sky, a strip of blue track, the car."""
    cr.rectangle(x0, y0, w, h); cr.set_source_rgb(0.62, 0.82, 0.98); cr.fill()
    cr.rectangle(x0, y0 + h * 0.72, w, h * 0.06); cr.set_source_rgb(0.36, 0.58, 0.92); cr.fill()
    cr.rectangle(x0 + w * 0.3, y0 + h * 0.5, w * 0.4, h * 0.22); cr.set_source_rgb(0.85, 0.25, 0.3); cr.fill()
    cr.arc(x0 + w * 0.5, y0 + h * 0.36, h * 0.11, 0, 2 * math.pi); cr.set_source_rgb(1, 1, 1); cr.fill_preserve()
    cr.set_source_rgb(0.1, 0.1, 0.12); cr.set_line_width(3); cr.stroke()
    cr.arc(x0 + w * 0.5, y0 + h * 0.18, h * 0.07, 0, 2 * math.pi); cr.set_source_rgb(0.1, 0.1, 0.12); cr.fill()

S = M.Scene(x0=SXE)
S.auto_blinks = False
S.floor = False
S.background(park)
S.blink(2.4, 9.9, 14.6)
S.hold_sign(0.0, 21.0, extra="WE'LL WAIT.", write_at=6.6)
S.set(4.0, "hold_front", "dead_stare", dur=0.12, look=(0.0, 0.85))       # eyes flick down to the sign...
S.set(4.7, "hold_front", "dead_stare", dur=0.12, look=(0.0, 0.0))        # ...and back to us
S.set(18.2, "hold_front", "dead_stare", dur=0.3, lid=1.0)                # one slow blink
S.set(18.65, "hold_front", "dead_stare", dur=0.35)

def mini_photo(cr, x, y, s, ang=0.0):
    cr.save(); cr.translate(x, y); cr.rotate(ang + 0.12); cr.scale(s, s)
    L.sketch_rect(cr, -90, -70, 90, 70, 5, sid=13300, fill=(1, 1, 1))
    cr.save(); cr.rectangle(-78, -58, 156, 100); cr.clip(); cr.translate(-78, -58)
    photo_inner(cr, 0, 0, 156, 100); cr.restore()
    cr.restore()

def kitten(cr, t, p, ly):
    if ly != "front": return
    hx, hy = p["head"]; a = p.get("tilt", 0.0)
    ox, oy = 5.0, -104.0
    x = hx + ox * math.cos(a) - oy * math.sin(a); y = hy + ox * math.sin(a) + oy * math.cos(a)
    look = (0.0, 0.0); blink = 0.0
    if 7.0 <= t < 9.2: look = (0.0, 0.9)                                  # watches him write
    if 12.0 <= t < 13.0: blink = math.sin(math.pi * (t - 12.0))           # one slow blink at us
    O.draw_cat(cr, x, y, s=KS, t=t, kind="loaf", col="black", look=look, blink=blink, sid=2000, tilt=a * 0.6)
    mini_photo(cr, x - 85, y - 30, 0.38, a * 0.6 - 0.35)
S.prop(kitten)

if __name__ == "__main__":
    S.render("day013.mp4")
