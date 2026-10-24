"""objects — reusable cartoon props for comment episodes. Line-drawn like him; colour used sparingly (one or two
accents per prop). Every drawer takes world coords; most anchor at bottom-centre (x, yb) with a scale s so they work
with moves.Scene.place(..., pop=True).

    draw_tub(cr, x, yb, s, t, part)        clawfoot tub of spicy ramen. part "back" (rim, broth, steam) / "front" (wall)
    draw_noodle_hat(cr, p)                 a noodle draped on his head (follows head + tilt)
    draw_drips(cr, p, t, t0, dur)          drips falling off him (after a bath)
    draw_bomb(cr, x, yb, s, t, ...)        round black ACME cartoon bomb with a big red button
    draw_fish(cr, x, y, s, ang, t)         little orange fish
    draw_cone(cr, x, y, s)                 three-scoop ice cream cone; (x, y) = where the hand holds it
    draw_dino(cr, st, t)                   friendly T. rex facing left; st = dict (see DINO)
    draw_water(cr, level_y, t)             underwater tint + surface line (front layer); draw_bubbles(...)
    draw_build_cloud(cr, x, y, t, t0, dur) Looney Tunes "fight cloud" that builds something
    draw_crater(cr, x, s, t)               scorch mark + smoke on the floor
"""
import math
from ink import (INK, PAPER, WHITE, FLOOR_Y, wob, sketch_pts, path, stroke_ink, fill_paper, fill_ink, sketch_line,
                 sketch_circle, sketch_rect, ellipse, sketch_ellipse, sketch_poly, draw_text, smooth, back_out, clamp01, lerp)
from props import draw_impact
import character as C

BROTH = (0.88, 0.38, 0.24)
NOODLE = (0.98, 0.9, 0.62)
WATER = (0.70, 0.84, 0.94)
SOOT = (0.30, 0.29, 0.28)

def _noodle(cr, pts, sid=0, w=1.0):
    """an outlined noodle strand along pts."""
    q = sketch_pts(pts, amp=1.0, sid=sid, step=10)
    path(cr, q); stroke_ink(cr, 10 * w)
    path(cr, q); stroke_ink(cr, 5.5 * w, NOODLE)

def _wavy(x0, y0, x1, y1, amp, n=4, ph=0.0, k=24):
    return [(x0 + (x1 - x0) * u + amp * math.sin(u * n * math.pi + ph) * (-(y1 - y0)) / (math.hypot(x1 - x0, y1 - y0) + 1e-6),
             y0 + (y1 - y0) * u + amp * math.sin(u * n * math.pi + ph) * (x1 - x0) / (math.hypot(x1 - x0, y1 - y0) + 1e-6))
            for u in [i / k for i in range(k + 1)]]

# ------------------------------------------------------------------ ramen tub ---
def tub_geom(x, yb, s=1.0):
    return dict(rim_y=yb - 290 * s, rw=245 * s, ry=36 * s, foot=yb - 22 * s, bottom=yb - 44 * s)

def draw_tub(cr, x, yb, s, t, part="back", steam=1.0, ripple=0.0, ripple_x=0.0):
    g = tub_geom(x, yb, s); ry_, rw, ry = g["rim_y"], g["rw"], g["ry"]
    if part == "back":
        if steam > 0.02:                                   # steam curls rising behind him
            for k in range(4):
                u = (t * 0.45 + k * 0.27) % 1.0
                bx = x + (-170 + k * 110) * s + 18 * math.sin(t * 2 + k)
                pts = _wavy(bx, ry_ - 10 * s, bx + 20 * s, ry_ - (90 + 170 * u) * s, 12 * s, 3, t * 3 + k, 16)
                path(cr, pts); stroke_ink(cr, 4, alpha=0.45 * steam * math.sin(math.pi * u))
        ellipse(cr, x, ry_, rw, ry, sid=700, amp=0.01); fill_paper(cr, PAPER); stroke_ink(cr, 7)
        ellipse(cr, x, ry_ + 2 * s, rw - 16 * s, ry - 9 * s, sid=701, amp=0.01); fill_paper(cr, BROTH); cr.new_path()
        for k in range(3):                                 # noodles on the far half of the surface
            y0 = ry_ - 12 * s + k * 5 * s
            _noodle(cr, _wavy(x - 170 * s + k * 40 * s, y0, x + 150 * s - k * 30 * s, y0 - 4 * s, 7 * s, 6, k + t * 0.6, 20), sid=710 + k)
        return
    # front: the near half of the rim band + broth (covers him below the surface), toppings, then the tub wall
    cr.save(); cr.rectangle(x - rw - 40 * s, ry_, 2 * rw + 80 * s, ry * 2); cr.clip()
    ellipse(cr, x, ry_, rw, ry, sid=700, amp=0.01); fill_paper(cr, PAPER); stroke_ink(cr, 7)
    ellipse(cr, x, ry_ + 2 * s, rw - 16 * s, ry - 9 * s, sid=701, amp=0.01); fill_paper(cr, BROTH); cr.new_path()
    cr.restore()
    for k in range(3):
        y0 = ry_ + 8 * s + k * 7 * s
        _noodle(cr, _wavy(x - 190 * s + k * 50 * s, y0, x + 180 * s - k * 40 * s, y0 + 3 * s, 6 * s, 7, k * 2 + t * 0.7, 22), sid=720 + k)
    # half egg + fish-cake swirl + chili flakes
    ex, ey = x + 120 * s, ry_ + 12 * s
    ellipse(cr, ex, ey, 34 * s, 20 * s, rot=0.1, sid=730); fill_paper(cr, WHITE); stroke_ink(cr, 5)
    ellipse(cr, ex, ey, 15 * s, 9 * s, sid=731); fill_paper(cr, (0.99, 0.78, 0.3)); stroke_ink(cr, 3)
    nx, ny = x - 120 * s, ry_ + 14 * s
    ellipse(cr, nx, ny, 30 * s, 17 * s, sid=732); fill_paper(cr, WHITE); stroke_ink(cr, 5)
    cr.move_to(nx, ny)
    for i in range(30):
        a = i * 0.42; r = i * 0.85 * s
        cr.line_to(nx + r * math.cos(a), ny + r * math.sin(a) * 0.55)
    stroke_ink(cr, 3, (0.92, 0.45, 0.55))
    for k in range(9):
        cx_ = x + (-200 + 47 * k) * s + 9 * math.sin(k * 3.1); cy_ = ry_ + (6 + 14 * ((k * 7) % 3)) * s
        cr.arc(cx_, cy_, 3.5 * s, 0, 6.3); fill_ink(cr, (0.62, 0.12, 0.08)); cr.new_path()
    if ripple > 0.02:                                       # rings on the surface (splash / dip)
        for k in range(2):
            u = (ripple + k * 0.35) % 1.0
            rr = min((40 + 180 * u) * s, rw - 20 * s - abs(ripple_x))
            ellipse(cr, x + ripple_x, ry_ + 12 * s, rr, (8 + 18 * u) * s * rr / ((40 + 180 * u) * s), sid=740 + k); stroke_ink(cr, 3, alpha=(1 - u) * 0.8)
    # rim near half + wall
    n = 40
    arc = [(x + rw * math.cos(math.pi - math.pi * i / n), ry_ + ry * math.sin(math.pi - math.pi * i / n)) for i in range(n + 1)]
    wall = arc + [(x + rw * 0.96, ry_ + 120 * s), (x + rw * 0.8, g["bottom"]), (x + rw * 0.4, g["bottom"] + 10 * s),
                  (x - rw * 0.4, g["bottom"] + 10 * s), (x - rw * 0.8, g["bottom"]), (x - rw * 0.96, ry_ + 120 * s)]
    path(cr, sketch_pts(wall + [wall[0]], amp=1.0, sid=750, step=18)); cr.close_path(); fill_paper(cr, PAPER); stroke_ink(cr, 7)
    path(cr, sketch_pts(arc, amp=0.8, sid=751, step=18)); stroke_ink(cr, 4)
    path(cr, sketch_pts([(x - rw * 0.97, ry_ + 18 * s), (x - rw * 0.4, ry_ + ry + 14 * s), (x + rw * 0.4, ry_ + ry + 14 * s),
                         (x + rw * 0.97, ry_ + 18 * s)], amp=0.8, sid=752, step=18)); stroke_ink(cr, 3, alpha=0.6)
    for k in range(4):                                     # a little hatching on the right of the wall
        xx = x + rw * (0.55 + 0.1 * k)
        sketch_line(cr, [(xx, ry_ + 90 * s), (xx - 14 * s, ry_ + 200 * s)], 3, sid=760 + k, alpha=0.35)
    for sx in (-1, 1):                                     # claw feet
        fx = x + sx * rw * 0.66
        ellipse(cr, fx, g["foot"], 30 * s, 22 * s, sid=770 + sx); fill_paper(cr, PAPER); stroke_ink(cr, 6)
        for j in range(3):
            cr.arc(fx + (j - 1) * 17 * s, yb - 4 * s, 7 * s, 0, 6.3); fill_paper(cr, PAPER); stroke_ink(cr, 4)

def draw_noodle_hat(cr, p, alpha=1.0):
    """a noodle draped over his head (continuity gag). Drawn in the front layer."""
    hx, hy = p["head"]; R = C.HEAD_R
    cr.save(); cr.translate(hx, hy); cr.rotate(p.get("tilt", 0.0))
    pts = []
    for i in range(23):
        a = -1.25 + i * 0.1
        r = R + 7 + 7 * math.sin(i * 1.3)
        pts.append((math.sin(a) * r, -math.cos(a) * r))
    pts = [(-R * 0.62, -R * 0.05), (-R * 0.8, -R * 0.2)] + pts[1:] + [(R * 1.02, R * 0.05), (R * 1.08, R * 0.32), (R * 0.98, R * 0.55)]
    _noodle(cr, pts, sid=780, w=1.15)
    cr.restore()

def draw_drips(cr, p, t, t0, dur, color=BROTH):
    """drips falling off him for dur seconds after t0."""
    if not (t0 <= t < t0 + dur): return
    fade = 1 - clamp01((t - t0 - dur + 0.6) / 0.6)
    for k, j in enumerate(("lhand", "rhand", "hip", "lhand", "rhand", "head")):
        u = ((t - t0) * 1.4 + k * 0.37) % 1.0
        x, y = p[j]; y += u * 260 + (40 if j == "head" else 0); x += (k % 3 - 1) * 14
        ellipse(cr, x, y, 7, 10, sid=790 + k); fill_paper(cr, color, fade * (1 - u)); stroke_ink(cr, 2.5, alpha=fade * (1 - u))

# ------------------------------------------------------------------ ACME bomb ---
def draw_bomb(cr, x, yb, s, t, light=0.0, pressed=0.0, label="ACME"):
    r = 165 * s; cy = yb - r
    # cap + button
    sketch_rect(cr, x - 40 * s, cy - r - 30 * s, x + 40 * s, cy - r + 14 * s, 6, sid=800, fill=(0.2, 0.2, 0.21))
    by = cy - r - 42 * s + 12 * s * pressed
    ellipse(cr, x, by, 34 * s, 15 * s, sid=801); fill_paper(cr, (0.86, 0.22, 0.2)); stroke_ink(cr, 5)
    cr.rectangle(x - 34 * s, by, 68 * s, (cy - r - 30 * s) - by); fill_paper(cr, (0.86, 0.22, 0.2)); cr.new_path()
    cr.move_to(x - 34 * s, by); cr.line_to(x - 34 * s, cy - r - 30 * s); cr.move_to(x + 34 * s, by); cr.line_to(x + 34 * s, cy - r - 30 * s); stroke_ink(cr, 5)
    sketch_circle(cr, x, cy, r, 7, sid=802, fill=(0.17, 0.17, 0.18))
    cr.arc(x - r * 0.35, cy - r * 0.38, r * 0.42, math.pi * 1.05, math.pi * 1.45); stroke_ink(cr, 9, WHITE, 0.55)
    draw_text(cr, label, x, cy - 30 * s, 84 * s, color=(245, 245, 240), rot=-0.04)
    tx, ty = x, cy + 62 * s                                  # cartoon trefoil
    for k in range(3):
        a0 = -math.pi / 2 + k * 2 * math.pi / 3 - 0.5
        cr.new_path(); cr.arc(tx, ty, 38 * s, a0, a0 + 1.0); cr.arc_negative(tx, ty, 11 * s, a0 + 1.0, a0); cr.close_path()
        fill_ink(cr, (0.98, 0.84, 0.25))
    cr.arc(tx, ty, 7 * s, 0, 6.3); fill_ink(cr, (0.98, 0.84, 0.25)); cr.new_path()
    if light > 0.01:                                         # blinking warning light
        lx, ly = x + r * 0.62, cy - r * 0.55
        cr.arc(lx, ly, 15 * s, 0, 6.3); fill_ink(cr, lerp((0.4, 0.1, 0.1), (1.0, 0.25, 0.2), light)); cr.new_path()
        for k in range(8):
            a = k * math.pi / 4
            cr.move_to(lx + math.cos(a) * 24 * s, ly + math.sin(a) * 24 * s); cr.line_to(lx + math.cos(a) * 40 * s, ly + math.sin(a) * 40 * s)
        stroke_ink(cr, 4, (1.0, 0.3, 0.25), light)

def draw_crater(cr, x, s, t, smoke=1.0):
    ellipse(cr, x, FLOOR_Y + 6, 230 * s, 26 * s, sid=810); fill_ink(cr, SOOT, 0.85); cr.new_path()
    for k in range(5):
        u = (t * 0.4 + k * 0.2) % 1.0
        bx = x + (-160 + 80 * k) * s + 20 * math.sin(t + k)
        sketch_circle(cr, bx, FLOOR_Y - 20 - u * 300, (20 + 40 * u) * s, 4, sid=811 + k, alpha=smoke * 0.6 * math.sin(math.pi * u))

# ------------------------------------------------------------------ fish ---
def draw_fish(cr, x, y, s=1.0, ang=0.0, t=0.0, flop=0.0):
    cr.save(); cr.translate(x, y); cr.rotate(ang + 0.35 * flop * math.sin(t * 22))
    cr.move_to(42 * s, 0); cr.line_to(78 * s, -26 * s); cr.line_to(74 * s, 26 * s); cr.close_path()
    fill_paper(cr, (0.98, 0.6, 0.3)); stroke_ink(cr, 5)
    ellipse(cr, 0, 0, 52 * s, 29 * s, sid=820); fill_paper(cr, (0.98, 0.64, 0.32)); stroke_ink(cr, 6)
    cr.arc(-28 * s, -6 * s, 8 * s, 0, 6.3); fill_paper(cr, WHITE); stroke_ink(cr, 3)
    cr.arc(-29 * s, -6 * s, 3.5 * s, 0, 6.3); fill_ink(cr); cr.new_path()
    cr.move_to(-50 * s, 8 * s); cr.line_to(-40 * s, 6 * s); stroke_ink(cr, 3)
    cr.restore()

# ------------------------------------------------------------------ ice cream ---
def draw_cone(cr, x, y, s=1.0):
    """three scoops; (x, y) = where the hand holds the cone."""
    top = y - 60 * s
    path(cr, [(x - 46 * s, top), (x, y + 95 * s), (x + 46 * s, top)]); cr.close_path(); fill_paper(cr, (0.93, 0.76, 0.5)); stroke_ink(cr, 6)
    cr.save(); path(cr, [(x - 46 * s, top), (x, y + 95 * s), (x + 46 * s, top)]); cr.close_path(); cr.clip()
    for k in range(-4, 5):
        cr.move_to(x + k * 24 * s - 60 * s, top); cr.line_to(x + k * 24 * s + 60 * s, y + 100 * s)
        cr.move_to(x + k * 24 * s + 60 * s, top); cr.line_to(x + k * 24 * s - 60 * s, y + 100 * s)
    stroke_ink(cr, 2.5, alpha=0.5); cr.restore()
    for k, col in enumerate(((0.97, 0.72, 0.78), (0.74, 0.92, 0.8), (0.99, 0.95, 0.84))):
        sketch_circle(cr, x + (6 if k == 1 else -4) * s, top - (28 + 62 * k) * s, (54 - 5 * k) * s, 6, sid=830 + k, fill=col)
    cr.arc(x + 4 * s, top - 190 * s, 13 * s, 0, 6.3); fill_paper(cr, (0.86, 0.15, 0.2)); stroke_ink(cr, 4)
    cr.move_to(x + 6 * s, top - 202 * s); cr.curve_to(x + 10 * s, top - 225 * s, x + 20 * s, top - 232 * s, x + 28 * s, top - 236 * s); stroke_ink(cr, 3)

# ------------------------------------------------------------------ dinosaur ---
DINO_GREEN = (0.80, 0.91, 0.74)
DINO = dict(x=780.0, s=1.0, walk=0.0, mouth=0.0, arms=0.0, lean=0.0, look=(-0.6, 0.1), smile=0.4, lid=0.0, blush=0.0,
            hearts=0.0, brow=0.0, worry=0.0, eyes="normal", bob=0.0, show=1.0)

def _walkbob(st):
    ph = st.get("walk", 0.0)
    return st.get("bob", 0.0) + (10 * st["s"] * abs(math.sin(ph)) if ph else 0.0)

def dino_head(st):
    """centre of the dino's head (for aiming hands / props at its mouth)."""
    x, s, ln = st["x"], st["s"], st["lean"]
    return (x - 200 * s - 80 * s * ln, FLOOR_Y - 900 * s + 170 * s * ln - _walkbob(st))

def dino_mouth(st):
    hx, hy = dino_head(st); s = st["s"]
    return (hx - 110 * s, hy + 30 * s)

def _leg(cr, st, hipx, hipy, footx, lift, G, sid, near=True):
    s = st["s"]; yb = FLOOR_Y
    if near:
        ellipse(cr, hipx, hipy, 100 * s, 130 * s, rot=-0.2, sid=sid); fill_paper(cr, G); stroke_ink(cr, 7)
    knee = (hipx + (footx - hipx) * 0.4 + 18 * s, (hipy + yb) / 2 + 30 * s - lift * 0.5)
    for wdt, col in ((42 * s, INK), (29 * s, G)):
        cr.move_to(hipx, hipy + 60 * s); cr.curve_to(knee[0], knee[1], knee[0], knee[1], footx + 10 * s, yb - 36 * s - lift)
        cr.set_line_cap(1); cr.set_source_rgb(*col); cr.set_line_width(wdt); cr.stroke()
    ellipse(cr, footx - 22 * s, yb - 22 * s - lift, 78 * s, 24 * s, sid=sid + 1); fill_paper(cr, G); stroke_ink(cr, 6)
    for j in range(3):
        cx_ = footx - 90 * s + j * 22 * s
        cr.move_to(cx_, yb - 30 * s - lift); cr.line_to(cx_ - 14 * s, yb - 8 * s - lift); stroke_ink(cr, 5)

def draw_dino(cr, st, t, blink=0.0):
    """friendly T. rex facing left. One smooth silhouette (body + neck + tail) so the head can never come loose."""
    if st.get("show", 1.0) < 0.01: return
    x, s = st["x"], st["s"]; yb = FLOOR_Y
    ph = st.get("walk", 0.0); wb = _walkbob(st)
    G = DINO_GREEN
    P = lambda dx, h: (x + dx * s, yb - h * s - wb)
    hx, hy = dino_head(st)
    # far leg (behind everything)
    fl = 34 * s * math.sin(ph + math.pi) if ph else 0.0; flift = max(0.0, math.cos(ph + math.pi)) * 26 * s if ph else 0.0
    _leg(cr, st, *P(110, 400), x + 120 * s + fl, flift, G, 840, near=False)
    # silhouette: front of the neck -> head -> back of the neck -> back -> tail -> belly
    cr.move_to(*P(-170, 560))
    cr.curve_to(*P(-215, 690), hx + 0 * s, hy + 150 * s, hx + 30 * s, hy + 40 * s)
    cr.line_to(hx + 95 * s, hy - 45 * s)
    cr.curve_to(hx + 175 * s, hy + 30 * s, *P(70, 770), *P(150, 640))
    cr.curve_to(*P(330, 520), *P(520, 300), *P(660, 140))
    cr.curve_to(*P(470, 230), *P(300, 330), *P(170, 380))
    cr.curve_to(*P(90, 300), *P(-60, 290), *P(-130, 380))
    cr.curve_to(*P(-190, 440), *P(-200, 500), *P(-170, 560))
    cr.close_path(); fill_paper(cr, G); stroke_ink(cr, 8)
    cr.save(); ellipse(cr, *P(-85, 480), 88 * s, 150 * s, rot=-0.35, sid=843); fill_paper(cr, (0.95, 0.97, 0.88))
    stroke_ink(cr, 4, alpha=0.6); ellipse(cr, *P(-85, 480), 88 * s, 150 * s, rot=-0.35); cr.clip()
    for k in range(6):
        yy = P(0, 360 + 55 * k)[1]
        cr.move_to(x - 220 * s, yy + 40 * s); cr.line_to(x + 60 * s, yy - 50 * s)
    stroke_ink(cr, 3, alpha=0.3); cr.restore()
    # near leg
    nl = 34 * s * math.sin(ph) if ph else 0.0; nlift = max(0.0, math.cos(ph)) * 26 * s if ph else 0.0
    _leg(cr, st, *P(40, 400), x + 0 * s + nl, nlift, G, 844, near=True)
    # tiny arms (the whole joke)
    ar = st.get("arms", 0.0)
    for k, (sx_, sy_) in enumerate((P(-150, 640), P(-118, 612))):
        wig = ar * 0.7 * math.sin(t * 26 + k * 2.1)
        a1 = math.pi * 0.82 + wig; a2 = a1 + 0.9 + wig * 0.6
        ex_, ey_ = sx_ + math.cos(a1) * 46 * s, sy_ + math.sin(a1) * 46 * s
        hx_, hy_ = ex_ + math.cos(a2) * 40 * s, ey_ + math.sin(a2) * 40 * s
        sketch_line(cr, [(sx_, sy_), (ex_, ey_), (hx_, hy_)], 7, sid=851 + k, amp=0.5)
        ellipse(cr, hx_, hy_, 11 * s, 8 * s, rot=a2, sid=853 + k); fill_paper(cr, G); stroke_ink(cr, 4.5)
    # head: mouth interior -> lower jaw -> upper head
    mo = st.get("mouth", 0.0); ang = 0.55 * mo
    HX, HY = hx + 70 * s, hy + 22 * s                      # jaw hinge
    if mo > 0.05:
        cr.move_to(HX, HY); cr.line_to(HX - 225 * s, HY)
        cr.line_to(HX - 215 * s * math.cos(ang), HY + 215 * s * math.sin(ang)); cr.close_path(); fill_ink(cr, (0.42, 0.14, 0.16)); cr.new_path()
    cr.save(); cr.translate(HX, HY); cr.rotate(-ang)
    cr.move_to(0, 0); cr.line_to(-212 * s, 0)
    cr.curve_to(-218 * s, 30 * s, -190 * s, 52 * s, -150 * s, 54 * s); cr.curve_to(-80 * s, 58 * s, -20 * s, 48 * s, 0, 0)
    cr.close_path(); fill_paper(cr, G); stroke_ink(cr, 7)
    if mo > 0.15:
        for k in range(5):
            tx_ = -195 * s + k * 36 * s
            path(cr, [(tx_, 2 * s), (tx_ + 11 * s, -15 * s), (tx_ + 22 * s, 2 * s)]); cr.close_path(); fill_paper(cr, WHITE); stroke_ink(cr, 3)
    cr.restore()
    cr.move_to(hx + 95 * s, hy - 45 * s)
    cr.curve_to(hx + 80 * s, hy - 118 * s, hx - 20 * s, hy - 122 * s, hx - 90 * s, hy - 96 * s)
    cr.curve_to(hx - 150 * s, hy - 80 * s, hx - 185 * s, hy - 50 * s, hx - 185 * s, hy - 10 * s)
    cr.curve_to(hx - 185 * s, hy + 14 * s, hx - 172 * s, hy + 22 * s, hx - 150 * s, hy + 22 * s)
    cr.line_to(HX, HY)
    cr.curve_to(hx + 110 * s, hy + 18 * s, hx + 118 * s, hy - 12 * s, hx + 95 * s, hy - 45 * s)
    cr.close_path(); fill_paper(cr, G); stroke_ink(cr, 7)
    for k in range(4):                                     # little teeth peeking down
        tx_ = hx - 140 * s + k * 40 * s
        path(cr, [(tx_, hy + 21 * s), (tx_ + 10 * s, hy + 38 * s), (tx_ + 20 * s, hy + 21 * s)]); cr.close_path(); fill_paper(cr, WHITE); stroke_ink(cr, 3)
    sm = st.get("smile", 0.4)
    if mo <= 0.15:                                          # smile curl at the back of the mouth
        cr.move_to(HX - 40 * s, HY); cr.curve_to(HX - 10 * s, HY, HX + 8 * s, HY - 14 * sm * s, HX + 14 * s, HY - 26 * sm * s); stroke_ink(cr, 5)
    cr.arc(hx - 160 * s, hy - 42 * s, 6 * s, 0, 6.3); fill_ink(cr); cr.new_path()        # nostril
    ex, ey = hx + 20 * s, hy - 58 * s                       # the eye (same style as his)
    lid = max(st.get("lid", 0.0), blink)
    if st.get("eyes") == "happy" or lid > 0.95:
        cr.move_to(ex - 24 * s, ey + 4 * s); cr.curve_to(ex - 10 * s, ey - 20 * s, ex + 10 * s, ey - 20 * s, ex + 24 * s, ey + 4 * s); stroke_ink(cr, 6)
    else:
        ellipse(cr, ex, ey, 24 * s, 30 * s, sid=850); fill_paper(cr, WHITE)
        cr.save(); cr.clip_preserve(); cr.new_path()
        lx, ly = st.get("look", (-0.6, 0.1))
        cr.arc(ex + lx * 10 * s, ey + ly * 12 * s, 12 * s, 0, 6.3); fill_ink(cr); cr.new_path()
        cr.arc(ex + lx * 10 * s - 4 * s, ey + ly * 12 * s - 5 * s, 4 * s, 0, 6.3); fill_paper(cr, WHITE); cr.new_path()
        if lid > 0.02:
            cr.rectangle(ex - 30 * s, ey - 34 * s, 60 * s, 64 * s * lid); fill_paper(cr, G); cr.new_path()
            cr.move_to(ex - 26 * s, ey - 30 * s + 60 * s * lid); cr.line_to(ex + 26 * s, ey - 30 * s + 60 * s * lid); stroke_ink(cr, 5)
        cr.restore()
        ellipse(cr, ex, ey, 24 * s, 30 * s); stroke_ink(cr, 6)
    b, w = st.get("brow", 0.0), st.get("worry", 0.0)
    cr.move_to(ex - 28 * s, ey - 44 * s - b * 10 * s - w * 8 * s); cr.line_to(ex + 26 * s, ey - 44 * s - b * 10 * s + w * 6 * s); stroke_ink(cr, 6)
    bl = st.get("blush", 0.0)
    if bl > 0.05:
        for k in range(3):
            x0 = hx + (30 + k * 12) * s
            cr.move_to(x0 - 5 * s, hy + 2 * s); cr.line_to(x0 + 5 * s, hy - 12 * s); stroke_ink(cr, 3.5, alpha=bl)
    hz = st.get("hearts", 0.0)
    if hz > 0.02:
        for k in range(3):
            u = (t * 0.4 + k / 3) % 1.0
            px, py, sz = hx - 100 * s + k * 100 * s + 20 * math.sin(t * 3 + k), hy - 150 * s - u * 140, 18 + 10 * u
            cr.move_to(px, py + sz * 0.9); cr.curve_to(px - sz * 1.6, py - sz * 0.2, px - sz * 0.5, py - sz * 1.3, px, py - sz * 0.35)
            cr.curve_to(px + sz * 0.5, py - sz * 1.3, px + sz * 1.6, py - sz * 0.2, px, py + sz * 0.9)
            fill_paper(cr, (0.97, 0.72, 0.78), hz * math.sin(math.pi * u)); stroke_ink(cr, 4, alpha=hz * math.sin(math.pi * u))

# ------------------------------------------------------------------ underwater ---
def draw_water(cr, level_y, t, alpha=0.42):
    """front layer: everything below level_y is under water (tinted), with a wavy surface line."""
    if level_y > FLOOR_Y + 400: return
    pts = [(x, level_y + 9 * math.sin(x * 0.012 + t * 2.2) + 4 * math.sin(x * 0.031 - t * 3)) for x in range(-1600, 2700, 40)]
    path(cr, pts); cr.line_to(2700, 4000); cr.line_to(-1600, 4000); cr.close_path(); fill_paper(cr, WATER, alpha); cr.new_path()
    path(cr, pts); stroke_ink(cr, 5, alpha=0.8)

def draw_bubbles(cr, t, x0, y0, n=6, spread=60, rise=300, size=10, seed=0, alpha=1.0):
    for k in range(n):
        u = (t * 0.6 + k / n + seed * 0.13) % 1.0
        x = x0 + spread * math.sin(k * 2.7 + seed) + 12 * math.sin(t * 3 + k)
        y = y0 - u * rise
        cr.arc(x, y, size * (0.6 + 0.6 * ((k * 7) % 3) / 2), 0, 6.3); stroke_ink(cr, 3, alpha=alpha * (1 - u))

def draw_build_cloud(cr, x, y, t, t0, dur, r=260):
    """the cartoon 'fight cloud': churning puffs, stars and tools flicking out. Returns nothing."""
    u = (t - t0) / dur
    if not (0 <= u < 1): return
    grow = back_out(min(1.0, u * 5)) * (1 - smooth((u - 0.88) / 0.12))
    for k in range(9):
        a = k / 9 * 2 * math.pi + t * 3
        bx, by = x + math.cos(a) * r * 0.55 * grow, y + math.sin(a) * r * 0.42 * grow
        sketch_circle(cr, bx + 12 * math.sin(t * 17 + k), by + 10 * math.cos(t * 13 + k), r * (0.38 + 0.07 * math.sin(k * 2.3 + t * 9)) * grow,
                      6, sid=860 + k)
    sketch_circle(cr, x, y, r * 0.55 * grow, 6, sid=870)
    for k in range(3):                                          # stars + tools popping out of the cloud
        ph = (t * 2.5 + k * 0.33) % 1.0
        a = k * 2.1 + int(t * 2.5 + k * 0.33) * 1.7
        px, py = x + math.cos(a) * r * (0.7 + 0.25 * ph), y + math.sin(a) * r * (0.55 + 0.2 * ph)
        if k == 0: draw_impact(cr, px, py, ph, r=46, sid=k)
        elif k == 1 and ph < 0.7:                               # wrench
            cr.save(); cr.translate(px, py); cr.rotate(a + t * 8)
            sketch_rect(cr, -10, -60, 10, 40, 5, sid=880); sketch_circle(cr, 0, -70, 22, 5, sid=881); cr.restore()
        elif k == 2 and ph < 0.7:                               # hammer
            cr.save(); cr.translate(px, py); cr.rotate(-a - t * 7)
            sketch_rect(cr, -8, -50, 8, 50, 5, sid=882); sketch_rect(cr, -36, -70, 36, -44, 5, sid=883, fill=(0.3, 0.3, 0.32)); cr.restore()

def draw_splash(cr, x, y, u, color=BROTH, n=12, r=230, sid=0, spread=0.8, floor_y=None):
    """droplets thrown up in a fan from (x, y) and falling back. u: 0..1 life."""
    if not (0 < u < 1): return
    a = 1 - smooth((u - 0.6) / 0.4)
    for k in range(n):
        ang = -math.pi * (0.5 - spread / 2 + spread * k / max(1, n - 1))
        sp = r * (0.7 + 0.5 * ((k * 7) % 5) / 4)
        px = x + math.cos(ang) * sp * u
        py = y + math.sin(ang) * sp * u + 420 * u * u
        if floor_y is not None and py > floor_y: continue          # fell back in / hit the floor
        ellipse(cr, px, py, 9, 12, rot=ang, sid=sid + k); fill_paper(cr, color, a); stroke_ink(cr, 3, alpha=a)

def draw_snorkel(cr, p, s=1.0):
    """snorkel in his mouth, tube up the LEFT side of his head (keeps clear of the pinned card). Follows head + tilt."""
    hx, hy = p["head"]
    cr.save(); cr.translate(hx, hy); cr.rotate(p.get("tilt", 0.0)); cr.scale(s, s)
    pts = [(-20, 60), (-95, 56), (-132, 24), (-140, -60), (-140, -178)]
    cr.set_line_cap(1); cr.set_line_join(1)
    for wdt, col in ((26, INK), (15, (0.98, 0.78, 0.25))):
        path(cr, pts); cr.set_source_rgb(*col); cr.set_line_width(wdt); cr.stroke()
    ellipse(cr, -140, -180, 16, 7, sid=905); fill_paper(cr, (0.98, 0.78, 0.25)); stroke_ink(cr, 5)
    ellipse(cr, 4, 60, 32, 17, sid=900); fill_paper(cr, (0.98, 0.78, 0.25)); stroke_ink(cr, 5)
    cr.restore()

def snorkel_top(p):
    hx, hy = p["head"]; a = p.get("tilt", 0.0)
    return (hx - 140 * math.cos(a) + 180 * math.sin(a), hy - 140 * math.sin(a) - 180 * math.cos(a))

def draw_rain(cr, t, t0, dur, n=18, color=WATER, seed=0, x0=0, x1=1080, y_top=0):
    """drops falling everywhere for dur seconds (water coming back down after a big splash)."""
    if not (t0 <= t < t0 + dur): return
    fade = 1 - clamp01((t - t0 - dur + 0.5) / 0.5)
    for k in range(n):
        u = ((t - t0) * 0.9 + (k * 0.618 + seed) % 1.0) % 1.0
        x = x0 + (x1 - x0) * ((k * 0.381 + seed * 0.17) % 1.0)
        y = y_top + u * (FLOOR_Y - y_top)
        ellipse(cr, x, y, 8, 12, sid=910 + k); fill_paper(cr, color, fade); stroke_ink(cr, 2.5, alpha=fade)

def draw_feather(cr, x, y, s=1.0, ang=-0.25, t=0.0, wiggle=0.0, droop=0.0):
    """a tickling feather held at its quill (x, y), pointing up (ang tilts; droop 0..1 wilts it)."""
    cr.save(); cr.translate(x, y); cr.rotate(ang + wiggle * 0.3 * math.sin(t * 30) + droop * 1.9); cr.scale(s, s)
    cr.move_to(0, -12); cr.curve_to(-34, -50, -30, -110, 0, -150); cr.curve_to(28, -112, 32, -50, 0, -12); cr.close_path()
    fill_paper(cr, (0.88, 0.82, 0.97)); stroke_ink(cr, 5)
    for k in range(5):
        yy = -35 - k * 22
        cr.move_to(0, yy); cr.line_to(-20 + k * 2, yy - 16); cr.move_to(0, yy); cr.line_to(19 - k * 2, yy - 16)
    stroke_ink(cr, 2.5, alpha=0.6)
    cr.move_to(0, 22); cr.line_to(0, -146); stroke_ink(cr, 4)
    cr.restore()
