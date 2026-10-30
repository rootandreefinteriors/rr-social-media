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
    draw_burger(cr, x, y, s, bites)        generic triple-decker burger (no brand); bites 0..1 eaten from the left
    draw_belly(cr, p, b)                   round cartoon belly over his torso (b 0..1), front layer
    draw_wrapper(cr, x, y, s, sid)         one crumpled burger wrapper; draw_wrapper_pile(cr, cx, w, h) a mound of them
    draw_wrapped_burger(cr, x, y, s)       a burger still in its paper; draw_burger_pile(cr, cx, w, h) a mound of burgers
    draw_burger_store(cr, cx, yb)          generic red/yellow fast-food burger place (no logo, no arches, no name)
    draw_dump_truck(cr, rx, yb, tilt, t)   yellow dump truck facing right; rx = rear end; tilt = bed angle (rad)
    draw_cloud(cr, x, y, s)                puffy outlined cartoon cloud
    draw_stream(cr, pts, w, color)         thick outlined cartoon stream through pts (e.g. a jet of brown "fuel")
    draw_cradle(cr, cx, yb, ang, st, t)    giant wooden rocking cradle with a giant baby in it (head at the LEFT end);
                                           cradle_pt(...) maps a cradle-local point to the world (eyes, rim, nose)
    draw_baby(cr, x, y, ang, st, t)        a normal-size swaddled baby (head to the left), centre (x, y)
    draw_mom(cr, t, p, blink)              a mom built on his rig: long hair + bun (hides the curl), a dress
    draw_owl(cr, x, y, s, flap, t)         brown delivery owl, wings flapping (flap 0..1 amount), centre (x, y)
    draw_envelope(cr, x, y, s, ang)        a parchment envelope with a red wax seal, centre (x, y)
    draw_letter(cr, cx, cy, w, h, lines)   an open parchment letter (big marker lines + a red seal), centre (cx, cy)
    draw_castle_world(cr, t, cx)           generic wizard-school castle at night: purple sky, stars, moon, towers with
                                           cone roofs, lit windows, a big arched gate; stone courtyard + floor line
    draw_wizard_hat(cr, bx, by, w, h, ...) giant old patched pointy hat with a crease face (eyes/mouth), floppy tip;
                                           (bx, by) = brim centre. glow/swell/shake for the overload, scorch for after
    draw_thought(cr, x, y, text, tail)     thought bubble with marker text, centre (x, y), dots trailing to `tail`
    draw_star(cr, x, y, r, color)          a chunky 5-point star (magic sparks); draw_magic_burst(...) a big spark boom
    draw_brim_ring(cr, x, t)               the scorched, smoking brim of a blown-up hat lying on the floor
    draw_brick_wall(cr, cx, w, h, signs)   a tall train-station brick wall with hanging platform signs (default 9 3/4)
    draw_free_door(cr, x, open_, part, sign) a tall wooden door standing on its own in its frame, with a plank sign on top
    draw_plane(cr, x, y, ang, t, part, prop) little red propeller plane, side view, nose to the right; (x, y) = the pilot
                                           seat (his hip goes here), ang = pitch (rad, + = nose down). part "back" =
                                           tail fin; "front" = fuselage/wing/wheels/prop (covers him below the chest)
    draw_space(cr, t, cx, cy)              black space, stars, the curve of the Earth below (centre-bottom at cx, cy)
    draw_puke(cr, x, y, r, t, ang)         a wobbly floating zero-g blob of green cartoon puke; draw_flames(...) re-entry fire
    draw_airfield_world(cr, t, x0, x1)     pale sky + clouds + grass airfield (right of x0): windsock, hangar, a
                                           FLIGHT SCHOOL sign; plane_wheel(...) one loose landing-gear wheel
"""
import math
import cairo
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

def draw_tub(cr, x, yb, s, t, part="back", steam=1.0, ripple=0.0, ripple_x=0.0, simmer=0.0):
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
    if simmer > 0.02:                                       # little bubbles rising and popping on the surface
        for k in range(7):
            u = (t * (0.7 + 0.13 * k) + k * 0.37) % 1.0
            bx = x + (-170 + 57 * k + 13 * math.sin(k * 5.1 + int(t * (0.7 + 0.13 * k) + k * 0.37))) * s
            by = ry_ + (8 + 10 * ((k * 3) % 3)) * s
            if u < 0.8:
                cr.arc(bx, by, (3 + 7 * u) * s, math.pi, 2 * math.pi); stroke_ink(cr, 2.5, alpha=simmer * 0.8)
            else:
                for j in range(4):
                    a = j * math.pi / 2 + 0.6
                    cr.move_to(bx + math.cos(a) * 8 * s, by + math.sin(a) * 6 * s); cr.line_to(bx + math.cos(a) * 14 * s, by + math.sin(a) * 10 * s)
                stroke_ink(cr, 2, alpha=simmer * 0.6)
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

def draw_noodle_hat(cr, p, alpha=1.0, clip_y=None):
    """one noodle draped over his crown: an end flopped over the forehead, the other hanging down the right side."""
    hx, hy = p["head"]; R = C.HEAD_R
    cr.save()
    if clip_y is not None: cr.rectangle(-5000, -5000, 10000, clip_y + 5000); cr.clip()
    cr.translate(hx, hy); cr.rotate(p.get("tilt", 0.0))
    pts = [(-34, -52), (-50, -78), (-58, -100)]
    pts += [(math.sin(a) * (R + 5 + 3 * math.sin(i * 1.7)), -math.cos(a) * (R + 5 + 3 * math.sin(i * 1.7)))
            for i, a in enumerate([-0.5 + k * 0.1 for k in range(12)])]
    pts += [(R * 0.98, -R * 0.12), (R * 1.04, R * 0.22), (R * 0.97, R * 0.5)]
    _noodle(cr, pts, sid=780, w=1.1)
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


# ------------------------------------------------------------------ giant chopsticks etc. ---
WOOD = (0.87, 0.73, 0.53)
def draw_chopsticks(cr, tip, ang, gap=30.0, length=1500, clip_y=None, t=0.0):
    """a giant pair of chopsticks coming in from off-screen. tip = midpoint between the two tips, ang = direction the
    sticks point (radians, base -> tip), gap = distance between tips. clip_y: hide anything below (dipped in broth)."""
    dx, dy = math.cos(ang), math.sin(ang); px, py = -dy, dx
    cr.save()
    if clip_y is not None:
        cr.rectangle(-5000, -5000, 10000, clip_y + 5000); cr.clip()
    for k, sg in enumerate((-1, 1)):
        tx, ty = tip[0] + px * sg * gap / 2, tip[1] + py * sg * gap / 2
        bx, by = tx - dx * length + px * sg * (gap / 2 + 40), ty - dy * length + py * sg * (gap / 2 + 40)
        a_, b_ = math.atan2(ty - by, tx - bx), None
        qx, qy = -math.sin(a_), math.cos(a_)
        pts = [(bx + qx * 17, by + qy * 17), (tx + qx * 6, ty + qy * 6), (tx - qx * 6, ty - qy * 6), (bx - qx * 17, by - qy * 17)]
        path(cr, pts); cr.close_path(); fill_paper(cr, WOOD); stroke_ink(cr, 6)
        for j in range(2):                                   # grain + the darker band near the top
            u0 = 0.08 + 0.05 * j
            cr.move_to(bx + (tx - bx) * u0 + qx * 15, by + (ty - by) * u0 + qy * 15); cr.line_to(bx + (tx - bx) * u0 - qx * 15, by + (ty - by) * u0 - qy * 15)
        stroke_ink(cr, 4, alpha=0.7)
    cr.restore()

def draw_egg(cr, x, y, s=1.0):
    """half a boiled egg floating yolk-up."""
    ellipse(cr, x, y, 34 * s, 20 * s, rot=0.08, sid=730); fill_paper(cr, WHITE); stroke_ink(cr, 5)
    ellipse(cr, x + 2 * s, y - 1 * s, 15 * s, 9 * s, sid=731); fill_paper(cr, (0.99, 0.78, 0.3)); stroke_ink(cr, 3)

def draw_puddle(cr, x, r, color=BROTH):
    if r < 2: return
    ellipse(cr, x, FLOOR_Y + 4, r, r * 0.16, sid=960, amp=0.03); fill_paper(cr, color, 0.95); stroke_ink(cr, 3.5, alpha=0.8)

def draw_floor_noodle(cr, x, y=FLOOR_Y - 5):
    pts = [(x - 60 + i * 10, y + 4 * math.sin(i * 1.3)) for i in range(13)]
    _noodle(cr, pts, sid=970)

# ------------------------------------------------------------------ blocky survival game (day 4) ---
# A generic "block world" look -- grass/dirt/log/leaves/obsidian/end-stone cubes with 8x8 pixel texture, pixel hearts,
# a pixel sword, a purple portal and a big black blocky dragon. No logos, names or real game characters.
BLK = dict(
    grass=((0.55, 0.38, 0.24), (0.45, 0.30, 0.19)), dirt=((0.55, 0.38, 0.24), (0.45, 0.30, 0.19)),
    log=((0.47, 0.35, 0.21), (0.36, 0.26, 0.15)), leaves=((0.33, 0.58, 0.22), (0.23, 0.44, 0.15)),
    obsidian=((0.10, 0.07, 0.15), (0.30, 0.18, 0.42)), endstone=((0.91, 0.90, 0.66), (0.80, 0.78, 0.52)),
    stone=((0.55, 0.55, 0.56), (0.45, 0.45, 0.47)), plank=((0.74, 0.58, 0.36), (0.62, 0.47, 0.28)),
    stonebrick=((0.52, 0.52, 0.53), (0.46, 0.46, 0.48)), endframe=((0.80, 0.84, 0.68), (0.68, 0.73, 0.56)))
GRASS_TOP = ((0.43, 0.70, 0.27), (0.35, 0.60, 0.21))

def _h(*a):
    v = 0
    for x in a: v = (v * 1103515245 + int(x) * 2654435761 + 12345) & 0x7fffffff
    return (v >> 8) % 1000 / 1000.0

def draw_block(cr, x0, y0, sz, kind="dirt", sid=0, alpha=1.0, outline=3.5, crack=0.0):
    """one textured cube face, top-left at (x0, y0). crack 0..1 draws breaking cracks."""
    base, spot = BLK[kind]; n = 8; px = sz / n
    cr.push_group()
    cr.rectangle(x0, y0, sz, sz); cr.set_source_rgb(*base); cr.fill()
    for i in range(n):
        for j in range(n):
            r = _h(sid, i, j); col = None
            if kind == "grass" and (j < 2 or (j == 2 and r < 0.5)): col = GRASS_TOP[1] if r < 0.3 else GRASS_TOP[0]
            elif kind == "log": col = spot if (i % 3 == 1 or r < 0.12) else None
            elif r < 0.32: col = spot
            if col: cr.rectangle(x0 + i * px, y0 + j * px, px + 0.5, px + 0.5); cr.set_source_rgb(*col); cr.fill()
    if kind == "stonebrick":                                # mortar lines
        cr.set_source_rgb(0.30, 0.30, 0.32)
        for yy in (0.0, 0.5): cr.rectangle(x0, y0 + yy * sz, sz, px * 0.6); cr.fill()
        for (xx, yy) in ((0.5, 0.0), (0.0, 0.5), (1.0, 0.5)): cr.rectangle(x0 + xx * sz - px * 0.3, y0 + yy * sz, px * 0.6, sz * 0.5); cr.fill()
    if kind == "endframe":                                  # green eye set in the top
        cr.rectangle(x0 + 2.5 * px, y0, 3 * px, 1.6 * px); cr.set_source_rgb(0.12, 0.35, 0.30); cr.fill()
        cr.rectangle(x0 + 3.5 * px, y0 + 0.2 * px, px, 1.0 * px); cr.set_source_rgb(0.45, 0.85, 0.65); cr.fill()
    if crack > 0.01:
        cx, cy = x0 + sz / 2, y0 + sz / 2
        for k in range(int(2 + 6 * crack)):
            a = k * 2.4 + sid
            pts = [(cx, cy)]
            for m in range(1, 4):
                pts.append((cx + math.cos(a + 0.4 * math.sin(m * 3 + k)) * sz * 0.16 * m * crack,
                            cy + math.sin(a + 0.4 * math.sin(m * 3 + k)) * sz * 0.16 * m * crack))
            path(cr, pts); stroke_ink(cr, 4, (0.08, 0.08, 0.08), 0.85)
    sketch_rect(cr, x0, y0, x0 + sz, y0 + sz, outline, sid=sid, fill=None, amp=0.8)
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha)

def draw_ground(cr, kind="grass", sub="dirt", bs=110, x0=-700, x1=1800, rows=3, yb=None):
    """a floor of blocks whose top is the floor line."""
    yb = FLOOR_Y if yb is None else yb
    k = 0
    x = x0
    while x < x1:
        for r in range(rows): draw_block(cr, x, yb + r * bs, bs, kind if r == 0 else sub, sid=900 + k * 7 + r)
        x += bs; k += 1

PIX_HEART = [".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]
def draw_pixel_heart(cr, x, y, s=6.0, fill=1.0, alpha=1.0):
    """pixel heart, top-left (x, y), cell size s. fill 1 full / 0.5 half / 0 empty."""
    cells = [(i, j) for j, row in enumerate(PIX_HEART) for i, c in enumerate(row) if c == "X"]
    for i, j in cells:                                      # black outline: each cell grown by one cell
        cr.rectangle(x + (i - 1) * s, y + (j - 1) * s, 3 * s, 3 * s)
    cr.set_source_rgba(0.06, 0.06, 0.07, alpha); cr.fill()
    for i, j in cells:
        red = fill >= 1.0 or (fill > 0 and i <= 3)
        col = (0.86, 0.12, 0.12) if red else (0.32, 0.30, 0.31)
        if red and j >= 3: col = (0.68, 0.06, 0.07)
        cr.rectangle(x + i * s, y + j * s, s + 0.4, s + 0.4); cr.set_source_rgba(*col, alpha); cr.fill()
    if fill > 0:
        cr.rectangle(x + 1 * s, y + 1 * s, s, s); cr.set_source_rgba(1, 1, 1, alpha * 0.9); cr.fill()

def draw_hearts_bar(cr, x, y, health, s=5.0, n=10, gap=6, alpha=1.0, blink=0.0):
    """row of n pixel hearts; health in hearts (0..n, halves allowed). blink makes the last one flash."""
    for k in range(n):
        f = 1.0 if health >= k + 1 else (0.5 if health >= k + 0.5 else 0.0)
        a = alpha
        if blink > 0 and f > 0 and health < k + 1.01: a *= 1 - 0.6 * blink
        draw_pixel_heart(cr, x + k * (7 * s + gap), y, s, f, a)

def draw_pixel_sword(cr, x, y, s=1.0, ang=-0.8, alpha=1.0):
    """chunky pixel sword; (x, y) = the grip. ang 0 = blade straight up."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    cr.push_group()
    BL, ED, GD, HD = (0.56, 0.93, 0.92), (0.22, 0.62, 0.66), (0.20, 0.20, 0.24), (0.45, 0.30, 0.16)
    cr.rectangle(-9, 16, 18, 34); cr.set_source_rgb(*HD); cr.fill()                 # handle
    cr.rectangle(-13, 48, 26, 14); cr.set_source_rgb(*GD); cr.fill()                # pommel
    cr.rectangle(-38, 2, 76, 16); cr.set_source_rgb(*GD); cr.fill()                 # guard
    cr.move_to(-14, 2); cr.line_to(-14, -150); cr.line_to(0, -172); cr.line_to(14, -150); cr.line_to(14, 2); cr.close_path()
    cr.set_source_rgb(*BL); cr.fill()
    cr.rectangle(2, -150, 6, 150); cr.set_source_rgb(*ED); cr.fill()               # edge shading
    cr.rectangle(-8, -140, 5, 40); cr.set_source_rgb(1, 1, 1); cr.fill()            # glint
    for (a0, b0, a1, b1) in ((-9, 16, 9, 50), (-13, 48, 13, 62), (-38, 2, 38, 18)):
        cr.rectangle(a0, b0, a1 - a0, b1 - b0); stroke_ink(cr, 4)
    cr.move_to(-14, 2); cr.line_to(-14, -150); cr.line_to(0, -172); cr.line_to(14, -150); cr.line_to(14, 2); stroke_ink(cr, 4.5)
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha); cr.restore()

def draw_portal(cr, cx, yb, t, part="frame", bs=110, w=4, h=5, alpha=1.0):
    """obsidian frame (part "frame") w x h blocks, bottom-centre (cx, yb); part "swirl" = the purple inside (draw it in
    front of whoever walks in, with alpha < 1)."""
    x0 = cx - w * bs / 2; y0 = yb - h * bs
    if part == "frame":
        for i in range(w):
            for j in range(h):
                if 0 < i < w - 1 and 0 < j < h - 1: continue
                draw_block(cr, x0 + i * bs, y0 + j * bs, bs, "obsidian", sid=950 + i * 11 + j)
        return
    ix0, iy0, iw, ih = x0 + bs, y0 + bs, (w - 2) * bs, (h - 2) * bs
    cr.save(); cr.rectangle(ix0, iy0, iw, ih); cr.clip()
    cr.set_source_rgba(0.50, 0.20, 0.82, 0.78 * alpha); cr.paint()
    for k in range(9):                                       # drifting swirl streaks
        yy = iy0 + ((k * 61 + t * 70) % ih)
        pts = [(ix0 + u * iw, yy + 14 * math.sin(u * 7 + t * 3 + k)) for u in [i / 12 for i in range(13)]]
        path(cr, pts); stroke_ink(cr, 7, (0.80, 0.55, 1.0), 0.55 * alpha)
    cr.restore()

def draw_square_sun(cr, x, y, sz=130, moon=False):
    if moon:
        cr.rectangle(x - sz / 2, y - sz / 2, sz, sz); cr.set_source_rgb(0.86, 0.88, 0.95); cr.fill()
        for (a, b, c) in ((-0.25, -0.15, 0.22), (0.15, 0.2, 0.16), (0.2, -0.25, 0.12)):
            cr.rectangle(x + a * sz, y + b * sz, c * sz, c * sz); cr.set_source_rgb(0.68, 0.70, 0.8); cr.fill()
    else:
        cr.rectangle(x - sz / 2, y - sz / 2, sz, sz); cr.set_source_rgb(1.0, 0.93, 0.45); cr.fill()
        cr.rectangle(x - sz * 0.3, y - sz * 0.3, sz * 0.6, sz * 0.6); cr.set_source_rgb(1.0, 0.99, 0.75); cr.fill()
    sketch_rect(cr, x - sz / 2, y - sz / 2, x + sz / 2, y + sz / 2, 4, sid=970, fill=None)

def draw_block_cloud(cr, x, y, w=260, h=50):
    cr.rectangle(x, y, w, h); cr.rectangle(x + w * 0.2, y - h * 0.6, w * 0.45, h * 0.6)
    cr.set_source_rgba(1, 1, 1, 0.92); cr.fill()

def draw_item_block(cr, x, y, kind, t, s=1.0):
    """a small dropped block spinning in place; (x, y) = its centre."""
    sz = 42 * s; sx = max(0.15, abs(math.cos(t * 2.2)))
    cr.save(); cr.translate(x, y + 6 * math.sin(t * 3)); cr.scale(sx, 1)
    draw_block(cr, -sz / 2, -sz / 2, sz, kind, sid=990, outline=2.5)
    cr.restore()

DRAGON = dict(x=820.0, y=FLOOR_Y, s=1.0, flap=0.0, hx=0.0, hy=0.0, jaw=0.0, look=(-1.0, 0.2), lid=0.0, fade=0.0, legs=1.0)
D_BLACK, D_WING, D_EYE = (0.08, 0.07, 0.09), (0.22, 0.20, 0.25), (0.78, 0.35, 1.0)

def _dbox(cr, x0, y0, x1, y1, sid, col=D_BLACK, w=5):
    cr.rectangle(min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0)); cr.set_source_rgb(*col); cr.fill()
    sketch_rect(cr, min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), w, sid=sid, fill=None, color=(0.0, 0.0, 0.0), amp=0.8)

def dragon_head(st):
    s = st["s"]; return (st["x"] - 330 * s + st["hx"], st["y"] - 420 * s + st["hy"])

def draw_dragon(cr, st, t):
    """big black blocky dragon facing left. st: x (body centre), y (where its feet stand), s, flap (wing phase, radians),
    hx/hy (head offset), jaw 0..1, look, lid, fade 0..1 (dissolving), legs 0..1 (tucked in flight)."""
    x, y, s = st["x"], st["y"], st["s"]
    cr.push_group()
    by0, by1 = y - 345 * s, y - 175 * s
    wv = math.sin(st["flap"])
    def wing(off, sid, shade):
        rx, ry = x + off * s, by0 + 10 * s
        tip = (rx + 330 * s, ry - 290 * s * wv - 40 * s)
        elbow = (rx + 90 * s, ry - 230 * s * wv - 60 * s)
        trail = (rx + 220 * s, ry - 70 * s * wv + 20 * s)
        pts = [(rx - 60 * s, ry), elbow, tip, trail, (rx + 120 * s, ry)]
        cr.move_to(*pts[0])
        for p_ in pts[1:]: cr.line_to(*p_)
        cr.close_path(); cr.set_source_rgb(*shade); cr.fill()
        sketch_poly(cr, pts, 5, sid=sid, fill=None, color=(0, 0, 0))
        for f in (0.45, 0.75):                                          # wing bones
            cr.move_to(*elbow); cr.line_to(lerp(trail, tip, f)[0], lerp(trail, tip, f)[1]); stroke_ink(cr, 4, (0, 0, 0))
    wing(40, 1001, (0.16, 0.14, 0.18))                                    # far wing
    for k in range(6):                                                    # tail
        tx = x + (180 + 62 * k) * s; ty = by0 + (40 - 22 * k + 10 * math.sin(t * 2 + k * 0.7)) * s
        sz = (70 - 8 * k) * s
        _dbox(cr, tx, ty, tx + 64 * s, ty + sz, 1010 + k)
        _dbox(cr, tx + 20 * s, ty - 18 * s, tx + 38 * s, ty, 1020 + k, w=3)
    lg = st["legs"]
    for k, lx in enumerate((-130, -60, 90, 150)):                          # legs
        ly1 = by1 + (175 * lg + 40 * (1 - lg)) * s
        _dbox(cr, x + lx * s, by1 - 10 * s, x + (lx + 42) * s, ly1, 1030 + k)
        _dbox(cr, x + (lx - 14) * s, ly1 - 22 * s, x + (lx + 46) * s, ly1, 1035 + k, w=3)
    _dbox(cr, x - 180 * s, by0, x + 180 * s, by1, 1040)                   # body
    for k in range(5): _dbox(cr, x + (-140 + 70 * k) * s, by0 - 22 * s, x + (-118 + 70 * k) * s, by0, 1045 + k, w=3)
    hx, hy = dragon_head(st)
    nx0, ny0 = x - 170 * s, by0 + 40 * s                                  # neck: blocks from body to head
    for k in range(4):
        u = (k + 0.5) / 4
        cx_, cy_ = lerp((nx0, ny0), (hx + 70 * s, hy + 40 * s), u)
        cy_ -= 40 * s * math.sin(math.pi * u)
        _dbox(cr, cx_ - 38 * s, cy_ - 34 * s, cx_ + 38 * s, cy_ + 34 * s, 1050 + k)
        _dbox(cr, cx_ - 9 * s, cy_ - 52 * s, cx_ + 9 * s, cy_ - 34 * s, 1055 + k, w=3)
    j = st["jaw"]                                                         # head: skull + snout + jaw
    jaw_drop = 70 * s * j
    _dbox(cr, hx - 80 * s, hy + 30 * s, hx + 20 * s, hy + 62 * s + jaw_drop, 1062)      # lower jaw
    if j > 0.05:
        cr.rectangle(hx - 80 * s, hy + 30 * s, 100 * s, jaw_drop); cr.set_source_rgb(0.45, 0.10, 0.25); cr.fill()
        for k in range(4): cr.rectangle(hx + (-74 + 24 * k) * s, hy + 30 * s, 10 * s, 12 * s); cr.set_source_rgb(0.95, 0.95, 0.9); cr.fill()
    _dbox(cr, hx - 20 * s, hy - 70 * s, hx + 120 * s, hy + 40 * s, 1060)    # skull
    _dbox(cr, hx - 100 * s, hy - 20 * s, hx - 20 * s, hy + 32 * s, 1061)    # snout
    cr.rectangle(hx - 92 * s, hy - 12 * s, 14 * s, 8 * s); cr.set_source_rgb(0.3, 0.28, 0.32); cr.fill()   # nostril
    for k in (0, 1): _dbox(cr, hx + (40 + 44 * k) * s, hy - 98 * s, hx + (58 + 44 * k) * s, hy - 70 * s, 1065 + k, w=3)
    ex, ey = hx + 28 * s, hy - 40 * s                                     # eye: purple slit with glow
    lid = st["lid"]
    cr.rectangle(ex - 6 * s, ey - 10 * s, 54 * s, 24 * s); cr.set_source_rgba(*D_EYE, 0.25); cr.fill()
    eh = 14 * s * (1 - lid)
    if eh > 0.5:
        cr.rectangle(ex, ey - eh / 2 + 2 * s, 42 * s, eh); cr.set_source_rgb(*D_EYE); cr.fill()
        lx = ex + 21 * s + 12 * s * st["look"][0]
        cr.rectangle(lx - 4 * s, ey - eh / 2 + 2 * s, 8 * s, eh); cr.set_source_rgb(0.98, 0.9, 1.0); cr.fill()
    wing(-30, 1002, D_WING)                                               # near wing
    cr.pop_group_to_source(); cr.paint_with_alpha(1.0 - st["fade"])

def draw_death_beams(cr, x, y, u, t, n=9, r=900):
    """purple/white beams of light bursting out of (x, y); u 0..1 life."""
    if not (0 < u < 1): return
    a = math.sin(math.pi * u)
    for k in range(n):
        ang = k * 2 * math.pi / n + t * 0.6 + 0.3 * math.sin(k * 3.1)
        w = 0.07 + 0.05 * math.sin(k * 1.7 + t * 4)
        cr.move_to(x, y)
        cr.line_to(x + math.cos(ang - w) * r * (0.4 + 0.6 * u), y + math.sin(ang - w) * r * (0.4 + 0.6 * u))
        cr.line_to(x + math.cos(ang + w) * r * (0.4 + 0.6 * u), y + math.sin(ang + w) * r * (0.4 + 0.6 * u))
        cr.close_path()
        col = (0.95, 0.85, 1.0) if k % 2 else (0.78, 0.45, 1.0)
        cr.set_source_rgba(*col, 0.55 * a); cr.fill()

def draw_end_portal(cr, x0, x1, top, depth, t):
    """the floor portal seen from the side: a starry black pit between x0..x1 from `top` down (draw in front)."""
    cr.rectangle(x0, top, x1 - x0, depth); cr.set_source_rgb(0.03, 0.05, 0.07); cr.fill()
    for k in range(26):
        sx = x0 + (k * 97.3) % (x1 - x0); sy = top + 8 + (k * 53.7 + t * 18) % (depth - 16)
        a = 0.5 + 0.5 * math.sin(t * 3 + k * 1.9)
        col = (0.55, 0.95, 0.85) if k % 3 else (0.95, 0.95, 1.0)
        cr.rectangle(sx, sy, 7, 7); cr.set_source_rgba(*col, a); cr.fill()
    cr.rectangle(x0, top, x1 - x0, 6); cr.set_source_rgba(0.45, 0.85, 0.75, 0.6); cr.fill()

# ------------------------------------------------------------------ where he lives now (from day 4) ---
def draw_end_world(cr, t):
    """S.background(O.draw_end_world): the dark purple sky, pixel stars and pale end-stone floor where he beat the
    dragon (day 4). He stays here until the comments send him somewhere else."""
    cr.rectangle(-3000, -3000, 8000, 8000); cr.set_source_rgb(0.24, 0.19, 0.30); cr.fill()
    for i in range(22): cr.rectangle(-500 + (i * 211) % 2200, -200 + (i * 131) % 1300, 8, 8)
    cr.set_source_rgba(0.95, 0.9, 1.0, 0.8); cr.fill()
    draw_ground(cr, "endstone", "endstone")

def hardcore_hud(health=0.5):
    """S.overlays.insert(0, O.hardcore_hud(0.5)): the HARDCORE label + heart row bottom-left (screen space), last
    heart blinking when low. Keep it on screen while he is in the block world."""
    def ov(cr, t):
        s, y = 5.6, 1440 - 6 * 5.6
        draw_text(cr, "HARDCORE", 72, y - 30, 34, color=(240, 240, 240), anchor="left")
        draw_hearts_bar(cr, 78, y, health, s=s, gap=6, blink=(0.5 + 0.5 * math.sin(t * 7)) if health <= 1 else 0.0)
    return ov


# ------------------------------------------------------------------ burgers (day 5) ---
# A generic triple-decker burger: three sesame bun pieces, two patties, cheese, lettuce. No box, no logo, no name.
BUN, BUN_D, PATTY, CHEESE, LETTUCE = (0.93, 0.68, 0.36), (0.83, 0.55, 0.26), (0.42, 0.26, 0.17), (1.0, 0.80, 0.25), (0.45, 0.74, 0.30)

def draw_burger(cr, x, y, s=1.0, bites=0.0, sid=0):
    """(x, y) = centre; ~170 x 150 at s=1. bites 0..1: eaten from the LEFT side (the side at his mouth), scalloped."""
    if bites >= 0.999: return
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.push_group()
    def layer(y0, y1, col, sid_, inset=0, r=10):
        sketch_rect(cr, -85 + inset, y0, 85 - inset, y1, 4.5, sid=sid + sid_, fill=col, amp=1.0)
    def lettuce(y0):
        pts = [(-92 + i * 9.2, y0 + 5 * math.sin(i * 1.7)) for i in range(21)] + [(92, y0 + 10), (-92, y0 + 10)]
        sketch_poly(cr, pts, 4, sid=sid + 7, fill=LETTUCE, amp=0.8)
    def cheese(y0):
        sketch_poly(cr, [(-88, y0), (88, y0), (70, y0 + 9), (20, y0 + 9), (6, y0 + 22), (-8, y0 + 9), (-88, y0 + 9)], 4,
                    sid=sid + 8, fill=CHEESE, amp=0.6)
    layer(52, 75, BUN, 1, inset=4)                                     # bottom bun
    layer(28, 52, PATTY, 2)                                            # patty
    cheese(22); lettuce(16)
    layer(-4, 18, BUN_D, 3, inset=2)                                   # middle bun
    layer(-28, -4, PATTY, 4)
    cheese(-34); lettuce(-40)
    cr.save(); cr.rectangle(-120, -100, 240, 60); cr.clip()            # top bun dome
    ellipse(cr, 0, -40, 86, 38, sid=sid + 5, amp=0.01); fill_paper(cr, BUN); stroke_ink(cr, 4.5); cr.restore()
    sketch_line(cr, [(-86, -40), (86, -40)], 4.5, sid=sid + 6, amp=0.6)
    for k, (sx, sy) in enumerate(((-45, -60), (-12, -68), (22, -63), (52, -54), (-62, -48), (5, -52), (-28, -52), (35, -48))):
        ellipse(cr, sx, sy, 6, 3.2, rot=0.4 * math.sin(k * 2.1), sid=sid + 20 + k); fill_paper(cr, (1.0, 0.98, 0.9)); stroke_ink(cr, 1.8)
    if bites > 0.001:                                                  # bitten away from the left: scalloped edge
        cx_ = -95 + 190 * bites
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.move_to(-130, -110); cr.line_to(cx_, -110)
        for k in range(4):
            yy = -80 + k * 46
            cr.arc(cx_, yy + 23, 24, -math.pi / 2, math.pi / 2)
        cr.line_to(cx_, 110); cr.line_to(-130, 110); cr.close_path(); cr.fill()
        cr.set_operator(cairo.OPERATOR_OVER)
    cr.pop_group_to_source(); cr.paint()
    cr.restore()

def belly_geom(p, b):
    nx, ny = p["neck"]; hx, hy = p["hip"]
    r = 34 + 150 * b
    return lerp((nx, ny), (hx, hy), 0.6 + 0.08 * b), r

def draw_belly(cr, p, b, wob_=0.0):
    """a round belly over his torso (front layer); b 0..1. wob_ adds a deflating wobble."""
    if b < 0.02: return
    (cx, cy), r = belly_geom(p, b)
    ellipse(cr, cx, cy, r * (1 + 0.06 * wob_), r * (0.96 - 0.06 * wob_), sid=4001, amp=0.012)
    fill_paper(cr); stroke_ink(cr, 7)
    cr.new_path()
    sketch_line(cr, [(cx - 8, cy + r * 0.25), (cx, cy + r * 0.3), (cx + 6, cy + r * 0.24)], 4, sid=4002, amp=0.4)  # button

def draw_wrapper(cr, x, y, s=1.0, sid=0):
    """one crumpled paper wrapper ball, centre (x, y)."""
    n = 9; pts = []
    for k in range(n):
        a = k * 2 * math.pi / n; rr = 26 * s * (0.75 + 0.45 * _h(sid, k))
        pts.append((x + rr * math.cos(a), y + rr * 0.8 * math.sin(a)))
    col = (0.98, 0.96, 0.9) if _h(sid, 99) < 0.6 else (0.96, 0.86, 0.62)
    sketch_poly(cr, pts, 3.5, sid=sid, fill=col, amp=0.8)
    a0 = _h(sid, 5) * 6
    sketch_line(cr, [(x - 10 * s * math.cos(a0), y - 8 * s * math.sin(a0)), (x + 8 * s, y + 4 * s)], 2.5, sid=sid + 1, amp=0.5)

def draw_wrapper_pile(cr, cx, w, h, yb=FLOOR_Y, n=None):
    """a mound of crumpled wrappers, bottom-centre (cx, yb), w wide, h tall. Stable (same balls every frame)."""
    if h < 4: return
    import random
    rnd = random.Random(77)
    pts = [(cx + (k / 24 - 0.5) * w, yb - h * (1 - (2 * k / 24 - 1) ** 2) ** 0.8) for k in range(25)]
    sketch_poly(cr, pts, 4, sid=5999, fill=(0.93, 0.89, 0.78), amp=1.0)
    n = n or int(10 + w * h / 1800)
    balls = []
    for k in range(n):
        u = rnd.uniform(-0.97, 0.97); top = h * (1 - u * u) ** 0.8
        yy = yb - top * (1 - rnd.random() ** 2.5) + 10
        balls.append((yy, cx + u * w / 2, k, rnd.uniform(0.9, 1.5)))
    for yy, xx, k, sc in sorted(balls):
        draw_wrapper(cr, xx, yy, sc, sid=5000 + k)


# ------------------------------------------------------------------ burger place / dump truck / sky (day 5 re-cut) ---
STORE_RED, STORE_YEL = (0.80, 0.17, 0.14), (1.0, 0.78, 0.16)

def draw_wrapped_burger(cr, x, y, s=1.0):
    """a burger still in its paper wrapper, centre (x, y)."""
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    pts = [(-78, 40), (-84, -10), (-60, -52), (0, -66), (60, -52), (84, -10), (78, 40), (0, 50)]
    sketch_poly(cr, pts, 4.5, sid=6100, fill=(0.98, 0.95, 0.86), amp=0.8)
    sketch_line(cr, [(-70, -12), (-10, -30), (40, -8)], 3, sid=6101, amp=0.5)
    sketch_line(cr, [(-30, 30), (20, 10), (70, 22)], 3, sid=6102, amp=0.5)
    sketch_rect(cr, -26, -16, 26, 6, 3, sid=6103, fill=STORE_RED, amp=0.4)
    cr.restore()

def draw_burger_pile(cr, cx, w, h, yb=FLOOR_Y, n=70, s=0.62):
    """a mound of burgers, bottom-centre (cx, yb). Positions are stable; the mound scales with w and h."""
    if h < 12: return
    import random
    rnd = random.Random(55)
    pts = [(cx + (k / 24 - 0.5) * w, yb - max(0.0, h - 35) * (1 - (2 * k / 24 - 1) ** 2) ** 0.8) for k in range(25)]
    sketch_poly(cr, pts, 4, sid=6200, fill=(0.62, 0.40, 0.22), amp=1.0)
    bs = s * min(1.0, 0.45 + h / 500)
    items = []
    for k in range(n):
        u = rnd.uniform(-0.93, 0.93); v = rnd.random() ** 0.55
        surf = h * (1 - u * u) ** 0.8
        y = yb - max(0.0, surf - 48 * bs / 0.62) * v - 20
        items.append((y, cx + u * w / 2, k))
    for y, x, k in sorted(items):
        draw_burger(cr, x, y, bs, sid=k * 3)

def draw_burger_store(cr, cx, yb=FLOOR_Y):
    """generic red/yellow burger place: brick-red box, yellow mansard band, striped awning, big windows, a door and a
    tall yellow sign on the LEFT with a drawn burger and the word BURGERS. No logo, no arches, no brand."""
    w, h = 820, 430
    x0, x1, y0 = cx - w / 2, cx + w / 2, yb - h
    sketch_rect(cr, x0, y0, x1, yb, 6, sid=6300, fill=STORE_RED)
    sketch_poly(cr, [(x0 - 40, y0 + 10), (x0 + 10, y0 - 90), (x1 - 10, y0 - 90), (x1 + 40, y0 + 10)], 6, sid=6301, fill=STORE_YEL)
    for k in range(7):                                                      # windows + door
        wx = x0 + 40 + k * 108
        if k == 3: sketch_rect(cr, wx, yb - 250, wx + 90, yb, 5, sid=6310, fill=(0.75, 0.88, 0.95)); continue
        sketch_rect(cr, wx, yb - 260, wx + 90, yb - 90, 5, sid=6320 + k, fill=(0.75, 0.88, 0.95))
    for k in range(14):                                                     # striped awning
        ax = x0 + 20 + k * 56
        sketch_poly(cr, [(ax, yb - 300), (ax + 56, yb - 300), (ax + 62, yb - 250), (ax + 6, yb - 250)], 3.5, sid=6340 + k,
                    fill=STORE_RED if k % 2 else (1, 1, 1), amp=0.4)
    draw_text(cr, "BURGERS", cx, y0 - 42, 62, color=(200, 30, 26))
    px = x0 - 230                                                           # the tall sign
    sketch_rect(cr, px - 16, yb - 700, px + 16, yb, 5, sid=6360, fill=(0.6, 0.6, 0.62))
    sketch_rect(cr, px - 150, yb - 900, px + 150, yb - 680, 6, sid=6361, fill=STORE_YEL)
    draw_burger(cr, px, yb - 830, 0.7, sid=40)
    draw_text(cr, "BURGERS", px, yb - 718, 44, color=(200, 30, 26))

def draw_dump_truck(cr, rx, yb, tilt=0.0, t=0.0, load=1.0, label="1 BILLION BURGERS"):
    """yellow dump truck facing RIGHT; rx = the rear end (where the load comes out), yb = ground. tilt = bed angle
    (rad, front end up). load 0..1 = burgers heaped in the bed."""
    YEL, DARK = (1.0, 0.80, 0.18), (0.25, 0.25, 0.28)
    sketch_rect(cr, rx + 10, yb - 175, rx + 880, yb - 120, 5, sid=6400, fill=DARK)          # chassis
    sketch_poly(cr, [(rx + 620, yb - 130), (rx + 620, yb - 420), (rx + 790, yb - 420), (rx + 880, yb - 290), (rx + 890, yb - 130)],
                6, sid=6401, fill=YEL)                                                         # cab
    sketch_poly(cr, [(rx + 650, yb - 390), (rx + 775, yb - 390), (rx + 840, yb - 295), (rx + 650, yb - 295)], 4, sid=6402,
                fill=(0.75, 0.88, 0.95))
    for k, wx in enumerate((rx + 130, rx + 270, rx + 760)):                                   # wheels
        sketch_circle(cr, wx, yb - 68, 68, 6, sid=6410 + k, fill=(0.15, 0.15, 0.17))
        sketch_circle(cr, wx, yb - 68, 28, 4, sid=6415 + k, fill=(0.7, 0.7, 0.72))
        a = -rx / 68.0
        cr.move_to(wx + 26 * math.cos(a), yb - 68 + 26 * math.sin(a)); cr.line_to(wx - 26 * math.cos(a), yb - 68 - 26 * math.sin(a))
        stroke_ink(cr, 4)
    cr.save(); cr.translate(rx, yb - 175); cr.rotate(-tilt)                                     # the bed, hinged at the rear
    if load > 0.02:
        for k in range(9):
            bx = 50 + k * 60; by = -235 - 40 * load * math.sin(math.pi * (k + 0.5) / 9)
            draw_burger(cr, bx, by, 0.45, sid=k * 5)
    sketch_poly(cr, [(0, 0), (0, -250), (600, -250), (600, 0)], 6, sid=6420, fill=YEL)
    for k in range(4): sketch_line(cr, [(30 + k * 150, -230), (30 + k * 150, -20)], 3, sid=6421 + k, amp=0.5)
    draw_text(cr, label, 300, -125, 46, color=(30, 30, 34))
    cr.restore()

def draw_cloud(cr, x, y, s=1.0, alpha=1.0):
    """puffy cartoon cloud, centre (x, y): one ink outline around white puffs."""
    puffs = [(-110, 20, 70), (-45, -25, 85), (40, -35, 90), (110, 10, 72), (0, 30, 80)]
    cr.push_group()
    for dx, dy, r in puffs:
        cr.arc(x + dx * s, y + dy * s, r * s, 0, 2 * math.pi); cr.new_sub_path()
    cr.set_source_rgb(*INK); cr.set_line_width(14 * s); cr.stroke_preserve(); cr.set_source_rgb(1, 1, 1); cr.fill()
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha)

def draw_stream(cr, pts, w=30, color=(0.46, 0.29, 0.14), lumps=True):
    """thick outlined cartoon stream through pts (list of (x, y)); round lumps along it."""
    if len(pts) < 2: return
    path(cr, pts); stroke_ink(cr, w + 10)
    if lumps:
        for k in range(0, len(pts), 3):
            cr.arc(pts[k][0], pts[k][1], w * 0.62 + 5, 0, 2 * math.pi); cr.set_source_rgb(*INK); cr.fill()
    path(cr, pts); stroke_ink(cr, w, color)
    if lumps:
        for k in range(0, len(pts), 3):
            cr.arc(pts[k][0], pts[k][1], w * 0.62, 0, 2 * math.pi); cr.set_source_rgb(*color); cr.fill()
            cr.arc(pts[k][0] - w * 0.2, pts[k][1] - w * 0.25, w * 0.14, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.35); cr.fill()

# ------------------------------------------------------------------ where he lives now (from day 5) ---
def draw_burger_world(cr, t, store_x=2760, x0=-4000):
    """S.background(lambda cr, t: O.draw_burger_world(cr, t, store_x=...)): pale sky with a few clouds, paper ground and
    the red/yellow burger place (sign on its left) where he landed on day 5. Body offset 2000 puts him at x 2540, just
    left of the store's centre (camera e.g. (2620, 930, 1.0)). Add O.draw_wrapper_pile(cr, 2540, 1350, 260) behind him
    for the leftover wrappers."""
    cr.rectangle(x0, -6000, 12000, 12000); cr.set_source_rgb(0.80, 0.89, 0.98); cr.fill()
    for (x, y, s) in ((store_x - 640, 120, 0.9), (store_x + 660, 400, 0.8), (store_x + 300, -380, 1.1)):
        draw_cloud(cr, x + 10 * math.sin(t * 0.3 + x), y, s)
    cr.rectangle(x0, FLOOR_Y, 12000, 3000); cr.set_source_rgb(0.95, 0.94, 0.90); cr.fill()
    draw_burger_store(cr, store_x)

def draw_spray(cr, pts, color=(0.52, 0.33, 0.14), dark=(0.36, 0.22, 0.09), t=0.0):
    """a runny cartoon jet: pts = [(x, y, w), ...] from the nozzle outwards (w = width there, growing as it spreads).
    Wobbly outlined ribbon with a darker core streak; make it long enough to leave the frame so it never 'ends'."""
    if len(pts) < 3: return
    L_, R_ = [], []
    for i, (x, y, w) in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) + 1e-6
        nx, ny = -dy / n, dx / n
        wl = w * (0.5 + 0.12 * math.sin(i * 0.9 + t * 23)); wr = w * (0.5 + 0.12 * math.sin(i * 1.3 - t * 19 + 2))
        L_.append((x + nx * wl, y + ny * wl)); R_.append((x - nx * wr, y - ny * wr))
    poly = L_ + R_[::-1]
    path(cr, poly); cr.close_path()
    cr.set_source_rgb(*color); cr.fill_preserve(); stroke_ink(cr, 7)
    core = [(x + 0.12 * w * math.sin(i * 0.7 + t * 17), y) for i, (x, y, w) in enumerate(pts)]
    path(cr, core); stroke_ink(cr, 10, dark, 0.8)
    for i in range(2, len(pts), 4):                                       # wet highlights
        x, y, w = pts[i]
        cr.arc(x - 0.18 * w, y - 0.1 * w, max(3.0, 0.07 * w), 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.35); cr.fill()

def draw_droplet(cr, x, y, r, color=(0.52, 0.33, 0.14)):
    cr.arc(x, y, r, 0, 2 * math.pi); cr.set_source_rgb(*color); cr.fill_preserve(); stroke_ink(cr, 4)


# ------------------------------------------------------------------ giant baby in a rocking cradle (day 6) ---
WOOD, WOOD_D, BLANKET, HOOD, SNOT, TEAR = (0.80, 0.60, 0.38), (0.62, 0.42, 0.24), (0.66, 0.80, 0.94), (0.96, 0.86, 0.70), (0.80, 0.95, 0.80), (0.55, 0.78, 0.97)
CRADLE_R = 1100.0                       # rocker radius: it swings around a point this far above the floor contact
BABY_HEAD = (-230.0, -545.0)            # cradle-local (origin = floor contact, y up is negative)
BABY_EYES = ((-290.0, -565.0), (-170.0, -565.0))
BABY_NOSE = (-215.0, -515.0)
BABY_MOUTH = (-230.0, -470.0)
CRADLE_RIM = (-400.0, -420.0)           # top of the head-end wall: where he pushes

def cradle_pt(cx, yb, ang, lx, ly, s=1.0):
    """cradle-local point -> world (same transform as draw_cradle)."""
    lx, ly = lx * s, ly * s
    X, Y = lx, ly + CRADLE_R
    c, sn = math.cos(ang), math.sin(ang)
    return (cx + X * c - Y * sn, yb - CRADLE_R + X * sn + Y * c)

def draw_cradle(cr, cx, yb, ang=0.0, st=None, t=0.0, s=1.0):
    """giant wooden rocking cradle, ~880 wide, rockers touching the floor at (cx, yb); ang = rock angle (rad, + tips
    the head end down-left). st: eyes ("sleep" | "open" | "cry"), cry 0..1 (mouth), open 0..1 (lids), look (x, y),
    bubble = snot bubble radius (px). The baby is big, round-headed, one hair curl, under a blue blanket."""
    st = st or {}
    cr.save(); cr.translate(cx, yb - CRADLE_R); cr.rotate(ang); cr.translate(0, CRADLE_R); cr.scale(s, s)
    # the head
    hx, hy = BABY_HEAD
    sketch_circle(cr, hx, hy, 165, 7, sid=7010, fill=WHITE)
    sketch_line(cr, [(hx - 10, hy - 163), (hx - 18, hy - 205), (hx + 10, hy - 225), (hx + 30, hy - 205), (hx + 12, hy - 190)], 6, sid=7011)
    eyes, cry, opn = st.get("eyes", "sleep"), st.get("cry", 0.0), st.get("open", 1.0)
    lx_, ly_ = st.get("look", (0.0, 0.0))
    for i, (ex, ey) in enumerate(BABY_EYES):
        sd = -1 if i == 0 else 1
        if eyes == "open" and opn > 0.15:
            ry = 34 * opn
            ellipse(cr, ex, ey, 30, ry, sid=7020 + i); fill_paper(cr, WHITE); stroke_ink(cr, 5)
            cr.arc(ex + 12 * lx_, ey + 10 * ly_ + 4, 15 * min(1.0, opn + 0.2), 0, 2 * math.pi); fill_ink(cr)
            cr.arc(ex + 12 * lx_ - 5, ey + 10 * ly_ - 2, 4.5, 0, 2 * math.pi); cr.set_source_rgb(1, 1, 1); cr.fill()
        elif eyes == "cry":                                                 # squeezed shut: > <
            sketch_line(cr, [(ex - 30 * sd, ey - 22), (ex + 22 * sd, ey), (ex - 30 * sd, ey + 20)], 7, sid=7024 + i)
        else:                                                               # asleep: a curve
            sketch_line(cr, [(ex - 28, ey - 2), (ex - 10, ey + 12), (ex + 10, ey + 12), (ex + 28, ey - 2)], 6, sid=7026 + i)
    nx, ny = BABY_NOSE
    sketch_line(cr, [(nx - 14, ny - 10), (nx - 4, ny + 4), (nx + 10, ny + 2)], 4, sid=7030)
    mx, my = BABY_MOUTH
    if cry > 0.02:                                                          # wailing: a huge open mouth
        w_, h_ = 26 + 52 * cry, 12 + 44 * cry
        wb = 1 + 0.06 * math.sin(t * 40) * cry
        ellipse(cr, mx, my + 8, w_ * wb, h_ / wb, sid=7031, amp=0.02); fill_ink(cr, (0.25, 0.08, 0.1)); cr.new_path()
        cr.save(); ellipse(cr, mx, my + 8, w_ * wb, h_ / wb, sid=7031, amp=0.02); cr.clip()
        ellipse(cr, mx, my + 8 + h_ * 0.75, w_ * 0.6, h_ * 0.45, sid=7032); fill_paper(cr, (0.95, 0.5, 0.55)); cr.restore()
        ellipse(cr, mx, my + 8, w_ * wb, h_ / wb, sid=7031, amp=0.02); stroke_ink(cr, 6)
    else:
        cr.arc(mx, my + 6, 9, 0, 2 * math.pi); stroke_ink(cr, 5)
    rb = st.get("bubble", 0.0)
    if rb > 2:                                                              # snot bubble from the nostril
        bx, by = nx + 6 + rb * 0.75, ny + 4 + rb * 0.25
        cr.arc(bx, by, rb, 0, 2 * math.pi); cr.set_source_rgba(*SNOT, 0.55); cr.fill_preserve(); stroke_ink(cr, 4)
        cr.arc(bx - rb * 0.35, by - rb * 0.35, max(2.0, rb * 0.15), 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.8); cr.fill()
    # rockers + legs
    def ry(x): return -CRADLE_R + math.sqrt(CRADLE_R ** 2 - x * x)
    rk = [(x, ry(x) - 14) for x in range(-470, 471, 20)]
    path(cr, rk); stroke_ink(cr, 40); path(cr, rk); stroke_ink(cr, 26, WOOD_D)
    for x in (-330, 330):
        sketch_rect(cr, x - 18, -130, x + 18, ry(x) - 20, 5, sid=7040 + (x > 0), fill=WOOD_D)
    # the box (front wall covers his neck), then the blanket over his body
    sketch_rect(cr, -400, -420, 400, -110, 7, sid=7050, fill=WOOD)
    for k in range(1, 8): sketch_line(cr, [(-400 + k * 100, -405), (-400 + k * 100, -125)], 3.5, sid=7051 + k, color=(0.55, 0.38, 0.22))
    sketch_rect(cr, -420, -440, -380, -100, 6, sid=7060, fill=WOOD_D)
    sketch_rect(cr, 380, -440, 420, -100, 6, sid=7061, fill=WOOD_D)
    bl = [(-90, -405), (-40, -470), (60, -505), (180, -510), (290, -485), (370, -440), (372, -330), (-88, -330)]
    sketch_poly(cr, bl, 6, sid=7070, fill=BLANKET, amp=1.0)
    for k in range(3): sketch_line(cr, [(-40 + k * 130, -470 + abs(k - 1) * 10), (0 + k * 130, -345)], 3, sid=7071 + k, color=(0.45, 0.6, 0.8))
    cr.restore()

def draw_tear_jet(cr, src, vel, t, life=1.2, g=2600.0, w0=26.0, w1=80.0, color=TEAR, n=34):
    """a cartoon tear stream from src with launch velocity vel; long enough to run off screen; wobbles."""
    pts = []
    for k in range(n):
        u = life * k / (n - 1)
        pts.append((src[0] + vel[0] * u, src[1] + vel[1] * u + 0.5 * g * u * u, w0 + (w1 - w0) * (k / (n - 1))))
    draw_spray(cr, pts, color=color, dark=(0.38, 0.6, 0.85), t=t)


# ------------------------------------------------------------------ a normal baby + a mom (day 6 re-cut) ---
SWADDLE, DRESS, HAIR = (0.70, 0.84, 0.96), (0.86, 0.38, 0.46), (0.36, 0.22, 0.14)
BABY_FACE = (-78.0, -16.0)

def baby_pt(x, y, ang, lx, ly, s=1.0):
    c, sn = math.cos(ang), math.sin(ang)
    return (x + (lx * c - ly * sn) * s, y + (lx * sn + ly * c) * s)

def draw_baby(cr, x, y, ang=0.0, st=None, t=0.0, s=1.0):
    """swaddled baby, ~230 x 130, centre (x, y), head at the LEFT end. st: eyes "open" | "sleep" | "cry",
    cry 0..1 (mouth), look (x, y), alpha."""
    st = st or {}
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_ellipse(cr, 30, 8, 108, 60, 6, sid=7501, fill=SWADDLE)
    for k in range(3): sketch_line(cr, [(-10 + k * 40, -45 + k * 4), (20 + k * 40, 55)], 3, sid=7502 + k, color=(0.45, 0.6, 0.8))
    hx, hy = BABY_FACE
    sketch_circle(cr, hx, hy, 58, 6, sid=7510, fill=WHITE)
    sketch_line(cr, [(hx - 2, hy - 57), (hx - 6, hy - 78), (hx + 8, hy - 88), (hx + 18, hy - 77), (hx + 8, hy - 70)], 4.5, sid=7511)
    eyes, cry = st.get("eyes", "open"), st.get("cry", 0.0)
    lx_, ly_ = st.get("look", (0.0, 0.0))
    for i, ex in enumerate((hx - 21, hx + 21)):
        ey = hy - 8; sd = -1 if i == 0 else 1
        if eyes == "open":
            ellipse(cr, ex, ey, 10, 12, sid=7520 + i); fill_paper(cr, WHITE); stroke_ink(cr, 3.5)
            cr.arc(ex + 4 * lx_, ey + 3 * ly_ + 1, 5.5, 0, 2 * math.pi); fill_ink(cr)
        elif eyes == "cry":
            sketch_line(cr, [(ex - 10 * sd, ey - 8), (ex + 8 * sd, ey), (ex - 10 * sd, ey + 7)], 4.5, sid=7524 + i, amp=0.4)
        else:
            sketch_line(cr, [(ex - 10, ey), (ex - 3, ey + 5), (ex + 3, ey + 5), (ex + 10, ey)], 4, sid=7526 + i, amp=0.4)
    mx, my = hx, hy + 24
    if cry > 0.05:
        w_, h_ = 8 + 14 * cry, 5 + 13 * cry * (0.85 + 0.15 * math.sin(t * 30))
        ellipse(cr, mx, my, w_, h_, sid=7530, amp=0.02); fill_ink(cr, (0.3, 0.1, 0.12)); cr.new_path()
        ellipse(cr, mx, my, w_, h_, sid=7530, amp=0.02); stroke_ink(cr, 3.5)
        for i, sd in enumerate((-1, 1)):                                   # little tears flicking off
            u = (t * 1.6 + i * 0.5) % 1.0
            cr.arc(hx + sd * (34 + 50 * u), hy - 10 - 30 * u + 60 * u * u, 6 * (1 - 0.4 * u), 0, 2 * math.pi)
            cr.set_source_rgb(0.55, 0.78, 0.97); cr.fill_preserve(); stroke_ink(cr, 2.5)
    elif eyes == "sleep":
        cr.arc(mx, my, 4, 0, 2 * math.pi); stroke_ink(cr, 3)
    else:
        sketch_line(cr, [(mx - 7, my - 1), (mx, my + 3), (mx + 7, my - 1)], 3.5, sid=7531, amp=0.3)
    cr.restore()

def draw_mom(cr, t, p, blink=0.0, s=0.92, alpha=1.0):
    """draw a mom on his rig. p = a constrained pose (world coords, feet at FLOOR_Y). Long dark hair with a bun on top
    (covers his signature curl), a pink dress, otherwise the same line style. Drawn scaled s around her feet.
    p["back"] = 1 shows her from behind (all hair)."""
    if alpha < 0.01: return
    fx = (p["lfoot"][0] + p["rfoot"][0]) / 2
    cr.push_group()
    cr.save(); cr.translate(fx, FLOOR_Y); cr.scale(s, s); cr.translate(-fx, -FLOOR_Y)
    hx, hy = p["head"]; tl = p.get("tilt", 0.0); tn = p.get("turn", 0.0); bk = p.get("back", 0.0) > 0.5
    cr.save(); cr.translate(hx, hy); cr.rotate(tl)                          # hair behind the head
    sketch_poly(cr, [(-135 - 10 * tn, -20), (-120, -110), (-60, -150), (60, -150), (120, -110), (135 - 10 * tn, -20),
                     (140, 120), (95, 170), (-95, 170), (-140, 120)], 6, sid=7601, fill=HAIR, amp=1.0)
    cr.restore()
    q = dict(p); q["larm_over"] = q["rarm_over"] = 1.0
    C.draw_guy(cr, t, q, blink)
    nx, ny = p["neck"]; hpx, hpy = p["hip"]
    sketch_poly(cr, [(nx - 26, ny + 22), (nx + 26, ny + 22), (hpx + 50, hpy - 40), (hpx + 105, hpy + 150), (hpx - 105, hpy + 150),
                     (hpx - 50, hpy - 40)], 6, sid=7602, fill=DRESS, amp=1.0)
    C.draw_arm_over(cr, q, "l"); C.draw_arm_over(cr, q, "r")
    cr.save(); cr.translate(hx, hy); cr.rotate(tl)                          # bangs (or the whole back of the head) + bun
    cr.save(); cr.arc(0, 0, C.HEAD_R + 2, 0, 2 * math.pi); cr.clip()
    if bk:
        cr.rectangle(-200, -200, 400, 400); cr.set_source_rgb(*HAIR); cr.fill()
    else:
        sketch_poly(cr, [(-140, -160), (140, -160), (140, -40), (60 + 30 * tn, -62), (10 * tn, -80), (-60 + 30 * tn, -60), (-140, -40)],
                    6, sid=7603, fill=HAIR, amp=0.8)
    cr.restore()
    if bk: cr.arc(0, 0, C.HEAD_R, 0, 2 * math.pi); stroke_ink(cr, 7)
    sketch_circle(cr, 8 * tn, -C.HEAD_R - 30, 52, 6, sid=7604, fill=HAIR)
    cr.restore()
    cr.restore()
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha)

# the burger place's door (draw_burger_store: centre 2760, 90 x 250): lit inside when open, a glass panel that swings
STORE_DOOR = (2714, FLOOR_Y - 250, 2804, FLOOR_Y)
def draw_store_door(cr, open_=0.0, part="inside"):
    """part "inside": the lit doorway (draw before whoever walks through it); part "panel": the door itself, swung
    open by open_ 0..1 on its left hinge (draw after them)."""
    x0, y0, x1, y1 = STORE_DOOR
    if part == "inside":
        if open_ > 0.01: sketch_rect(cr, x0, y0, x1, y1, 5, sid=6311, fill=(1.0, 0.88, 0.6))
        return
    w = (x1 - x0) * math.cos(open_ * 1.35)
    if w < 4: return
    sketch_poly(cr, [(x0, y0), (x0 + w, y0 + 10 * open_), (x0 + w, y1 - 6 * open_), (x0, y1)], 5, sid=6312, fill=(0.75, 0.88, 0.95), amp=0.5)
    sketch_line(cr, [(x0 + w * 0.78, y0 + 120), (x0 + w * 0.78, y0 + 150)], 5, sid=6313, amp=0.3)


# ------------------------------------------------------------------ wizard school (day 7) ---
OWL, OWL_L, BEAK = (0.58, 0.42, 0.28), (0.86, 0.76, 0.60), (0.96, 0.66, 0.20)
PARCH, SEAL = (0.97, 0.92, 0.78), (0.78, 0.12, 0.12)
HAT, HAT_D, HAT_P = (0.52, 0.38, 0.25), (0.38, 0.27, 0.17), (0.64, 0.50, 0.33)
GOLD, VIOLET, CYAN = (1.0, 0.82, 0.25), (0.70, 0.45, 0.98), (0.45, 0.88, 0.98)

def draw_owl(cr, x, y, s=1.0, flap=1.0, t=0.0, blink=0.0, point=0.0, point_ang=0.0, look=(0.0, 0.0)):
    """brown delivery owl seen from the front, wings beating (flap = how much), centre (x, y).
    point 0..1: its screen-right wing stops flapping and sticks out stiff along point_ang (rad, 0 = right, + = down)."""
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    a = flap * math.sin(t * 22)
    for sd in (-1, 1):                                                      # wings behind the body
        cr.save(); cr.translate(sd * 45, -10)
        r = sd * (-0.9 + 0.8 * a)
        if sd == 1 and point > 0: r = lerp(r, point_ang, point)
        cr.rotate(r)
        if sd == 1 and point > 0: cr.scale(1 + 0.35 * point, 1)
        sketch_ellipse(cr, sd * 70, 0, 80, 30, 6, sid=7700 + sd, fill=OWL)
        for k in range(3): sketch_line(cr, [(sd * (40 + k * 30), -10), (sd * (52 + k * 30), 14)], 3, sid=7703 + k, amp=0.3)
        cr.restore()
    sketch_ellipse(cr, 0, 0, 68, 82, 7, sid=7710, fill=OWL)
    sketch_ellipse(cr, 0, 22, 42, 50, 4, sid=7711, fill=OWL_L)
    for sd in (-1, 1):
        sketch_poly(cr, [(sd * 30, -62), (sd * 56, -100), (sd * 60, -55)], 5, sid=7712 + sd, fill=OWL, amp=0.4)   # ear tufts
        sketch_circle(cr, sd * 26, -30, 25, 5, sid=7715 + sd, fill=WHITE)
        if blink < 0.5:
            cr.arc(sd * 26 + 9 * look[0], -28 + 9 * look[1], 11, 0, 2 * math.pi); fill_ink(cr)
            cr.arc(sd * 22 + 9 * look[0], -33 + 9 * look[1], 4, 0, 2 * math.pi); cr.set_source_rgb(1, 1, 1); cr.fill()
        else:
            sketch_line(cr, [(sd * 26 - 16, -30), (sd * 26 + 16, -30)], 5, sid=7718 + sd, amp=0.3)
    sketch_poly(cr, [(-10, -16), (10, -16), (0, 6)], 4, sid=7720, fill=BEAK, amp=0.3)
    for sd in (-1, 1): sketch_line(cr, [(sd * 18, 78), (sd * 18, 96)], 5, sid=7721 + sd, amp=0.3, color=BEAK)
    cr.restore()

def draw_envelope(cr, x, y, s=1.0, ang=0.0):
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_rect(cr, -80, -52, 80, 52, 5, sid=7730, fill=PARCH)
    sketch_line(cr, [(-80, -52), (0, 8), (80, -52)], 4, sid=7731, amp=0.5)
    sketch_circle(cr, 0, 8, 17, 4, sid=7732, fill=SEAL)
    cr.restore()

def draw_letter(cr, cx, cy, w, h, lines=("YOU'RE IN.",), sub=None, alpha=1.0, back=False, stamp=None, stamp_k=1.0):
    """an open parchment letter facing us: big marker lines, an optional small line under them, a red wax seal.
    back=True: the blank back of it (he's reading the other side)."""
    cr.push_group()
    sketch_rect(cr, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 6, sid=7740, fill=PARCH)
    if back:
        for k in range(2):
            yk = cy - h / 2 + h * (k + 1) / 3
            sketch_line(cr, [(cx - w / 2 + 10, yk), (cx + w / 2 - 10, yk)], 2.5, sid=7741 + k, amp=0.6, alpha=0.35)
        cr.pop_group_to_source(); cr.paint_with_alpha(alpha); return
    for k in range(2):                                                      # fold creases
        yk = cy - h / 2 + h * (k + 1) / 3
        sketch_line(cr, [(cx - w / 2 + 10, yk), (cx + w / 2 - 10, yk)], 2.5, sid=7741 + k, amp=0.6, alpha=0.35)
    n = len(lines); size = min(90, w / 6)
    for i, l in enumerate(lines):
        draw_text(cr, l, cx, cy - h * 0.18 + (i - (n - 1) / 2) * size * 1.15, size, color=(30, 22, 18))
    if sub: draw_text(cr, sub, cx, cy + h * 0.14, size * 0.55, color=(70, 50, 40))
    sketch_circle(cr, cx, cy + h / 2 - 48, 26, 4, sid=7745, fill=SEAL)
    if stamp and stamp_k > 0.01:                                           # a big red rubber stamp across it
        from ink import text_surface
        surf, tw, th = text_surface(stamp, int(w / 5.2), color=(200, 24, 24))
        sc = 1.0 + 0.6 * (1 - stamp_k)
        cr.save(); cr.translate(cx, cy); cr.rotate(-0.22); cr.scale(sc, sc)
        cr.rectangle(-tw / 2 - 4, -th / 2 + 2, tw + 8, th - 4); cr.set_source_rgba(0.78, 0.09, 0.09, stamp_k); cr.set_line_width(9); cr.stroke()
        cr.set_source_surface(surf, -tw / 2, -th / 2); cr.paint_with_alpha(stamp_k)
        cr.restore()
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha)

def _cone_roof(cr, x, y, w, h, sid):
    sketch_poly(cr, [(x - w / 2 - 14, y), (x, y - h), (x + w / 2 + 14, y)], 6, sid=sid, fill=(0.24, 0.22, 0.42), amp=0.8)

def _window(cr, x, y, w, h, sid, lit=True):
    cr.move_to(x - w / 2, y + h / 2); cr.line_to(x - w / 2, y - h / 2 + w / 2)
    cr.arc(x, y - h / 2 + w / 2, w / 2, math.pi, 0); cr.line_to(x + w / 2, y + h / 2); cr.close_path()
    cr.set_source_rgb(*((1.0, 0.86, 0.45) if lit else (0.18, 0.16, 0.28))); cr.fill_preserve(); stroke_ink(cr, 4)

STONE, STONE_D, NIGHT_TOP, NIGHT_LOW = (0.80, 0.78, 0.84), (0.64, 0.62, 0.70), (0.10, 0.08, 0.24), (0.42, 0.30, 0.56)
def draw_castle_world(cr, t, cx=4140.0, x0=-4000, x1=12000):
    """night sky + a generic wizard-school castle centred on cx (gate behind whoever stands at cx), stone courtyard.
    No crest, no name, no house colours."""
    g = cairo.LinearGradient(0, -400, 0, FLOOR_Y)
    g.add_color_stop_rgb(0.0, *NIGHT_TOP); g.add_color_stop_rgb(1.0, *NIGHT_LOW)
    cr.rectangle(x0, -6000, x1 - x0, 6000 + FLOOR_Y); cr.set_source(g); cr.fill()
    for k in range(70):                                                     # stars (twinkle)
        sx = cx - 1500 + (k * 397) % 3000; sy = -350 + (k * 233) % 900
        a = 0.55 + 0.45 * math.sin(t * 2.3 + k)
        cr.rectangle(sx, sy, 6, 6); cr.set_source_rgba(1, 1, 0.9, a); cr.fill()
    cr.arc(cx + 620, -120, 95, 0, 2 * math.pi); cr.set_source_rgb(0.99, 0.97, 0.86); cr.fill_preserve(); stroke_ink(cr, 6)
    cr.arc(cx + 655, -140, 80, 0, 2 * math.pi); cr.set_source_rgb(*NIGHT_TOP); cr.fill()            # crescent
    yb = FLOOR_Y - 60
    # far towers
    for dx, w, h, rh in ((-760, 150, 900, 300), (720, 170, 1000, 330), (-420, 120, 1250, 280), (380, 130, 1180, 290)):
        sketch_rect(cr, cx + dx - w / 2, yb - h, cx + dx + w / 2, yb, 6, sid=7800 + dx % 97, fill=STONE_D)
        _cone_roof(cr, cx + dx, yb - h, w, rh, sid=7810 + dx % 89)
        _window(cr, cx + dx, yb - h + 130, 40, 80, sid=0, lit=(dx % 3 != 0))
    # main hall
    sketch_rect(cr, cx - 560, yb - 640, cx + 560, yb, 7, sid=7820, fill=STONE)
    for k in range(12):                                                     # battlements
        bx = cx - 560 + k * 102
        sketch_rect(cr, bx, yb - 700, bx + 56, yb - 638, 5, sid=7821 + k, fill=STONE)
    for k in range(6):                                                      # stone courses
        sketch_line(cr, [(cx - 556, yb - 100 * (k + 1)), (cx + 556, yb - 100 * (k + 1))], 2.5, sid=7835 + k, amp=0.8, alpha=0.35)
    for dx in (-430, -300, 300, 430):
        _window(cr, cx + dx, yb - 440, 64, 130, sid=0)
    # the gate (arched, open, warm light inside)
    gw, gh = 330, 520
    cr.move_to(cx - gw / 2, yb); cr.line_to(cx - gw / 2, yb - gh + gw / 2)
    cr.arc(cx, yb - gh + gw / 2, gw / 2, math.pi, 0); cr.line_to(cx + gw / 2, yb); cr.close_path()
    cr.set_source_rgb(1.0, 0.84, 0.50); cr.fill_preserve(); stroke_ink(cr, 7)
    # front towers flanking the gate
    for sd in (-1, 1):
        tx = cx + sd * 330
        sketch_rect(cr, tx - 80, yb - 860, tx + 80, yb, 6, sid=7850 + sd, fill=STONE)
        _cone_roof(cr, tx, yb - 860, 160, 300, sid=7853 + sd)
        _window(cr, tx, yb - 700, 46, 96, sid=0)
        cr.move_to(tx, yb - 1160); cr.line_to(tx + sd * 0 + 70, yb - 1135); cr.line_to(tx, yb - 1110)   # pennant
        cr.set_source_rgb(0.62, 0.30, 0.78); cr.fill_preserve(); stroke_ink(cr, 3)
    # courtyard: stone flags
    cr.rectangle(x0, yb, x1 - x0, 3000); cr.set_source_rgb(0.62, 0.60, 0.66); cr.fill()
    cr.rectangle(x0, FLOOR_Y, x1 - x0, 3000); cr.set_source_rgb(0.70, 0.68, 0.74); cr.fill()
    sketch_line(cr, [(x0, yb), (x1, yb)], 4, sid=7860, amp=1.0, alpha=0.7)
    sketch_line(cr, [(x0, FLOOR_Y), (x1, FLOOR_Y)], 3.5, sid=7861, amp=1.3, alpha=0.8)
    for k in range(-14, 15):
        sketch_line(cr, [(cx + k * 190, FLOOR_Y + 8), (cx + k * 230, FLOOR_Y + 400)], 2.5, sid=7870 + k, amp=0.8, alpha=0.3)

def hat_spine(bx, by, w, h, bend=0.0, droop=0.0, swell=1.0):
    """points along the hat's centre line, brim -> tip: list of (x, y, half_width)."""
    out = []
    for i in range(41):
        u = i / 40
        x = bx + bend * (u ** 2.2) * w * 0.55 + droop * (max(0.0, u - 0.62) / 0.38) ** 2 * w * 0.45
        y = by - h * u + droop * (max(0.0, u - 0.62) / 0.38) ** 2 * h * 0.22
        hw = (w / 2) * swell * (1 - u) ** 0.9 * (1 + 0.06 * math.sin(u * 9)) + 4
        out.append((x, y, hw))
    return out

def hat_pt(bx, by, w, h, u, side=0.0, bend=0.0, droop=0.0, swell=1.0):
    """a point on the hat: u up the spine (0 brim .. 1 tip), side -1..1 across it."""
    sp = hat_spine(bx, by, w, h, bend, droop, swell)
    i = min(39, int(u * 40)); k = u * 40 - i
    (xa, ya, wa), (xb, yb, wb) = sp[i], sp[i + 1]
    return (lerp(xa, xb, k) + side * lerp(wa, wb, k), lerp(ya, yb, k))

def draw_wizard_hat(cr, bx, by, w, h, t=0.0, bend=0.0, droop=0.0, swell=1.0, eyes=0.0, look=(0.0, 0.0), mouth=0.0,
                    glow=0.0, scorch=0.0, brim=True, sid=7900, angry=0.0):
    """giant, old, patched pointy hat. (bx, by) = brim centre. eyes 0..1 (closed crease .. open), look -1..1,
    mouth 0..1 (the brim crease opens), glow 0..1 (seams + stitches glow gold: overload), scorch 0..1 (burnt)."""
    col = lerp(HAT, (0.24, 0.21, 0.20), scorch)
    sp = hat_spine(bx, by, w, h, bend, droop, swell)
    left = [(x - hw, y) for x, y, hw in sp]; right = [(x + hw, y) for x, y, hw in sp]
    if brim:                                                                # back half of the brim
        cr.new_path(); cr.save(); cr.translate(bx, by); cr.scale(w * 0.78 * swell, w * 0.13); cr.arc(0, 0, 1, math.pi, 2 * math.pi); cr.restore()
        cr.set_source_rgb(*lerp(HAT_D, (0.18, 0.16, 0.15), scorch)); cr.fill_preserve(); stroke_ink(cr, 7)
    path(cr, sketch_pts(left + right[::-1], amp=1.4, sid=sid, step=24)); cr.close_path()
    cr.set_source_rgb(*col); cr.fill_preserve(); stroke_ink(cr, 8)
    # patches (stitched) + a band
    for k, (u, sd, pw, ph) in enumerate(((0.30, -0.45, 0.20, 0.10), (0.55, 0.30, 0.16, 0.09), (0.78, -0.1, 0.10, 0.06))):
        cxp, cyp = hat_pt(bx, by, w, h, u, sd, bend, droop, swell)
        pw_, ph_ = w * pw * swell, h * ph
        sketch_rect(cr, cxp - pw_ / 2, cyp - ph_ / 2, cxp + pw_ / 2, cyp + ph_ / 2, 4, sid=sid + 10 + k,
                    fill=lerp(HAT_P, (0.30, 0.26, 0.24), scorch), amp=1.0)
        for j in range(5):
            xj = cxp - pw_ / 2 + pw_ * (j + 0.5) / 5
            sketch_line(cr, [(xj, cyp - ph_ / 2 - 7), (xj, cyp - ph_ / 2 + 7)], 3, sid=sid + 20 + j, amp=0.2,
                        color=lerp(INK, GOLD, glow))
        if glow > 0.02:
            cr.rectangle(cxp - pw_ / 2, cyp - ph_ / 2, pw_, ph_); cr.set_source_rgba(*GOLD, min(1.0, 1.2 * glow)); cr.set_line_width(10 + 14 * glow); cr.stroke()
    bl, br = hat_pt(bx, by, w, h, 0.07, -1, bend, droop, swell), hat_pt(bx, by, w, h, 0.07, 1, bend, droop, swell)
    sketch_line(cr, [(bl[0] + 4, bl[1]), (br[0] - 4, br[1])], 6, sid=sid + 30, amp=0.8)
    if glow > 0.02:                                                         # the seams glow
        for edge in (left[:-3], right[:-3]):
            path(cr, edge); cr.set_source_rgba(*GOLD, 0.35 * glow); cr.set_line_width(60 * glow + 2); cr.stroke()
            path(cr, edge); cr.set_source_rgba(1.0, 0.95, 0.6, min(1.0, 1.3 * glow)); cr.set_line_width(20 * glow + 2); cr.stroke()
    # the face: two crease eyes + a crease mouth
    for sd in (-1, 1):
        ex, ey = hat_pt(bx, by, w, h, 0.42, sd * 0.36, bend, droop, swell)
        ew, eh = w * 0.075 * swell, w * 0.05 * max(0.05, eyes)
        ang = angry * w * 0.06                                            # angry: brows slam down toward the middle
        sketch_line(cr, [(ex - ew * 1.5, ey - eh - 16 - sd * ang), (ex + ew * 1.5, ey - eh - 24 + sd * 6 + sd * ang)],
                    6 + 4 * angry, sid=sid + 40 + sd, amp=0.6)
        if eyes > 0.08:
            ellipse(cr, ex, ey, ew, eh, sid=sid + 43 + sd); fill_ink(cr, HAT_D); cr.new_path()
            ellipse(cr, ex, ey, ew, eh, sid=sid + 43 + sd); stroke_ink(cr, 5)
            cr.arc(ex + look[0] * ew * 0.45, ey + look[1] * eh * 0.4, min(ew, eh) * 0.55, 0, 2 * math.pi)
            cr.set_source_rgb(1.0, 0.92, 0.55); cr.fill()
        else:
            sketch_line(cr, [(ex - ew, ey), (ex, ey + 6), (ex + ew, ey)], 6, sid=sid + 46, amp=0.4)
    mx, my = hat_pt(bx, by, w, h, 0.2, 0.0, bend, droop, swell)
    mw = w * 0.2 * swell
    if mouth > 0.05:
        ellipse(cr, mx, my, mw, 10 + 34 * mouth, sid=sid + 50); fill_ink(cr, (0.16, 0.10, 0.08)); cr.new_path()
        ellipse(cr, mx, my, mw, 10 + 34 * mouth, sid=sid + 50); stroke_ink(cr, 6)
    else:
        sketch_curve(cr, (mx - mw, my - 8), (mx, my + 12), (mx + mw, my - 8), 7, sid=sid + 51)
    if brim:                                                                # front half of the brim
        cr.new_path(); cr.save(); cr.translate(bx, by); cr.scale(w * 0.78 * swell, w * 0.13); cr.arc(0, 0, 1, 0, math.pi); cr.restore()
        cr.set_source_rgb(*lerp(HAT_D, (0.18, 0.16, 0.15), scorch)); cr.fill_preserve(); stroke_ink(cr, 7)
        sketch_line(cr, [(bx - w * 0.78 * swell, by), (bx + w * 0.78 * swell, by)], 4, sid=sid + 60, amp=0.6, alpha=0.5)

def sketch_curve(cr, p0, c, p1, width=8, sid=0, amp=1.2, color=INK):
    from ink import bez
    path(cr, sketch_pts(bez(p0, c, p1), amp=amp, sid=sid, step=14)); stroke_ink(cr, width, color)

def draw_thought(cr, x, y, text, tail=None, size=58, alpha=1.0, max_w=430):
    """a cloud-edged thought bubble with marker text centred at (x, y); little circles trail off toward `tail`."""
    from ink import text_surface
    s, tw, th = text_surface(text, size, max_w=max_w)
    w, h = tw + 40, th + 30
    cr.push_group()
    puffs = []
    n = max(4, int(w / 70))
    for i in range(n + 1):
        u = i / n
        puffs += [(x - w / 2 + w * u, y - h / 2, 46), (x - w / 2 + w * u, y + h / 2, 46)]
    for i in range(1, 3):
        v = i / 3
        puffs += [(x - w / 2, y - h / 2 + h * v, 46), (x + w / 2, y - h / 2 + h * v, 46)]
    if tail:
        for k, r in enumerate((28, 19, 12)):
            u = 0.45 + 0.2 * k
            puffs.append((lerp(x, tail[0], u), lerp(y + h / 2, tail[1], u), -r))
    for px, py, r in puffs:
        cr.arc(px, py, abs(r), 0, 2 * math.pi); cr.new_sub_path()
    cr.rectangle(x - w / 2, y - h / 2, w, h)
    cr.set_source_rgb(*INK); cr.set_line_width(12); cr.stroke_preserve(); cr.set_source_rgb(1, 1, 1); cr.fill()
    cr.set_source_surface(s, x - tw / 2, y - th / 2); cr.paint()
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha)

def draw_star(cr, x, y, r, color=GOLD, ang=0.0, alpha=1.0):
    pts = []
    for k in range(10):
        a = ang - math.pi / 2 + k * math.pi / 5; rr = r if k % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    path(cr, pts); cr.close_path(); cr.set_source_rgba(*color, alpha); cr.fill_preserve()
    cr.set_source_rgba(*INK, alpha); cr.set_line_width(max(2.0, r * 0.14)); cr.stroke()

import random as _random
_BURST = None
def draw_magic_burst(cr, x, y, u, t=0.0, r=1400, n=90, part="both"):
    """a huge cartoon magic explosion u seconds after it goes off: a fat cloud that blooms and fades + a storm of gold,
    violet and cyan stars flying out (gravity pulls them down, then they fade). part "cloud" / "stars" / "both"
    (draw the cloud in the back layer and the stars in front to see someone blasted out through it)."""
    global _BURST
    if _BURST is None:
        rnd = _random.Random(7)
        _BURST = [(rnd.uniform(0, 2 * math.pi), rnd.uniform(0.35, 1.0), rnd.uniform(18, 48), rnd.choice((GOLD, VIOLET, CYAN, GOLD)),
                   rnd.uniform(-3, 3)) for _ in range(n)]
    if u < 0: return
    k = min(1.0, u / 0.35)                                                  # the cloud
    ca = 1.0 - smooth((u - 0.5) / 1.4)
    if ca > 0.01 and part != "stars":
        cr.push_group()
        for i in range(9):
            a = i * 2 * math.pi / 9 + 0.3
            rr = (220 + 260 * back_out(k, 1.4)) * (0.8 + 0.2 * math.sin(i * 2.1))
            cr.arc(x + math.cos(a) * rr * 0.75, y + math.sin(a) * rr * 0.55 - 60, rr * 0.62, 0, 2 * math.pi); cr.new_sub_path()
        cr.set_source_rgb(*INK); cr.set_line_width(14); cr.stroke_preserve(); cr.set_source_rgb(0.86, 0.78, 0.98); cr.fill()
        for i in range(6):
            a = i * 2 * math.pi / 6
            rr = (120 + 170 * back_out(k, 1.4))
            cr.arc(x + math.cos(a) * rr * 0.6, y + math.sin(a) * rr * 0.45 - 60, rr * 0.55, 0, 2 * math.pi); cr.new_sub_path()
        cr.set_source_rgb(1.0, 0.95, 0.70); cr.fill()
        cr.pop_group_to_source(); cr.paint_with_alpha(ca)
    if part == "cloud": return
    for a, sp, sz, col, spin in _BURST:                                    # the stars
        d = r * sp * (1 - math.exp(-u * 2.4))
        sx = x + math.cos(a) * d; sy = y + math.sin(a) * d * 0.8 + 260 * u * u
        al = 1.0 - smooth((u - 1.6) / 1.4)
        if al > 0.01: draw_star(cr, sx, sy, sz * (1 - 0.3 * min(1, u / 3)), col, ang=spin * u, alpha=al)

def draw_brim_ring(cr, x, t=0.0, smoke=1.0, w=620):
    """the scorched brim of a blown-up hat, lying flat on the floor around x, smoking."""
    cr.save(); cr.translate(x, FLOOR_Y - 6); cr.scale(w, w * 0.11)
    cr.arc(0, 0, 1, 0, 2 * math.pi); cr.new_sub_path(); cr.arc_negative(0, 0, 0.62, 2 * math.pi, 0)
    cr.restore()
    cr.set_source_rgb(0.22, 0.19, 0.18); cr.fill_preserve(); stroke_ink(cr, 6)
    for k in range(4):                                                      # wisps
        u = ((t * 0.5) + k / 4) % 1.0
        sx = x + (-0.7 + 0.47 * k) * w * 0.8 + 30 * math.sin(t * 2 + k)
        cr.arc(sx + 20 * math.sin(u * 6 + k), FLOOR_Y - 30 - 260 * u, 18 + 40 * u, 0, 2 * math.pi)
        cr.set_source_rgba(0.55, 0.55, 0.58, 0.45 * smoke * math.sin(math.pi * u)); cr.fill()


BRICK, BRICK_D, MORTAR = (0.74, 0.36, 0.26), (0.62, 0.28, 0.20), (0.90, 0.86, 0.80)
def draw_brick_wall(cr, cx, w=700, h=1150, signs=(("9 3/4", 0.2),), yb=FLOOR_Y):
    """a tall station brick wall, bottom-centre (cx, yb), with platform signs hanging on it: signs = ((text, where
    across 0..1), ...)."""
    x0, x1, y0 = cx - w / 2, cx + w / 2, yb - h
    sketch_rect(cr, x0, y0, x1, yb, 7, sid=8000, fill=MORTAR)
    bh, bw = 56, 120
    row = 0; y = yb
    while y > y0 + 1:
        yt = max(y0, y - bh)
        off = (bw / 2) if row % 2 else 0
        x = x0 - off
        k = 0
        while x < x1:
            a, b = max(x0, x + 5), min(x1, x + bw - 5)
            if b - a > 8:
                cr.rectangle(a, yt + 5, b - a, (y - yt) - 10)
                cr.set_source_rgb(*(BRICK if (row * 7 + k * 3) % 5 else BRICK_D)); cr.fill()
            x += bw; k += 1
        y -= bh; row += 1
    cr.rectangle(x0, y0, w, h); stroke_ink(cr, 7)
    sketch_rect(cr, x0 - 20, y0 - 40, x1 + 20, y0, 6, sid=8001, fill=(0.55, 0.52, 0.50))     # coping
    from ink import text_surface
    for i, (txt, fr) in enumerate(signs):                                    # hanging signs
        sx = x0 + w * fr; sy = y0 + 250
        surf, tw, th = text_surface(txt, 88)
        hw = max(95, tw / 2 + 6)
        sketch_line(cr, [(sx - hw + 40, y0 + 10), (sx - hw + 40, sy - 60)], 4, sid=8010 + i, amp=0.3)
        sketch_line(cr, [(sx + hw - 40, y0 + 10), (sx + hw - 40, sy - 60)], 4, sid=8012 + i, amp=0.3)
        sketch_rect(cr, sx - hw, sy - 60, sx + hw, sy + 60, 6, sid=8014 + i, fill=(0.98, 0.98, 0.96))
        cr.set_source_surface(surf, sx - tw / 2, sy - th / 2 + 4); cr.paint()

WOODR = (0.66, 0.42, 0.24)
def draw_free_door(cr, x, open_=0.0, part="inside", sign="DOOR TO WIZARD SCHOOL", w=380, h=1150, yb=FLOOR_Y,
                   inside=(1.0, 0.86, 0.50), sign_w=None):
    """a big wooden door standing on its own in a frame (nothing behind it). part "inside" = frame + the glowing
    doorway (draw before whoever walks through); part "panel" = the door swinging open on its left hinge (draw after
    them) + the sign on top."""
    x0, x1, y0 = x - w / 2, x + w / 2, yb - h
    if part == "inside":
        sketch_rect(cr, x0 - 34, y0 - 34, x1 + 34, yb, 7, sid=8100, fill=(0.50, 0.32, 0.18))   # frame
        sketch_rect(cr, x0, y0, x1, yb, 5, sid=8101, fill=inside if open_ > 0.01 else (0.18, 0.14, 0.12))
        return
    dw = w * math.cos(open_ * 1.35)
    if dw > 4:
        sketch_poly(cr, [(x0, y0), (x0 + dw, y0 + 20 * open_), (x0 + dw, yb - 12 * open_), (x0, yb)], 6, sid=8102, fill=WOODR, amp=0.5)
        for k in range(1, 4):                                               # planks
            sketch_line(cr, [(x0 + dw * k / 4, y0 + 10 + 20 * open_ * k / 4), (x0 + dw * k / 4, yb - 10)], 3, sid=8103 + k, amp=0.4, alpha=0.6)
        cr.arc(x0 + dw * 0.85, y0 + h * 0.55, 16 * max(0.3, dw / w), 0, 2 * math.pi); cr.set_source_rgb(*GOLD); cr.fill_preserve(); stroke_ink(cr, 4)
    if sign:
        sw_ = sign_w or (w + 260)
        sketch_rect(cr, x - sw_ / 2, y0 - 230, x + sw_ / 2, y0 - 60, 6, sid=8110, fill=(0.92, 0.82, 0.60))
        sketch_line(cr, [(x - 120, y0 - 60), (x - 120, y0 - 34)], 5, sid=8111, amp=0.2)
        sketch_line(cr, [(x + 120, y0 - 60), (x + 120, y0 - 34)], 5, sid=8112, amp=0.2)
        from ink import text_surface
        surf, tw, th = text_surface(sign, 60, max_w=sw_ - 40)
        cr.set_source_surface(surf, x - tw / 2, y0 - 145 - th / 2); cr.paint()


# ------------------------------------------------------------------ day 8: the plane + the airfield
PLANE_RED = (0.86, 0.25, 0.21)
PLANE_RED_D = (0.66, 0.16, 0.14)
STEEL = (0.62, 0.64, 0.68)
GRASS = (0.62, 0.80, 0.45)
PLANE_SEAT_H = 400.0                    # seat (his hip) is this far above the ground when the plane sits on its wheels
WHEEL = (120.0, 330.0, 70.0)           # landing-gear wheel, plane-local (x, y, r)
def plane_pt(x, y, ang, lx, ly, s=1.0):
    """plane-local point (x right = nose, y down) -> world, for a plane whose seat is at (x, y) pitched by ang."""
    c, s_ = math.cos(ang), math.sin(ang)
    return (x + (lx * c - ly * s_) * s, y + (lx * s_ + ly * c) * s)

def plane_wheel(cr, x, y, r=70.0, spin=0.0):
    sketch_circle(cr, x, y, r, 7, sid=9301, fill=(0.2, 0.2, 0.22))
    sketch_circle(cr, x, y, r * 0.42, 5, sid=9302, fill=STEEL)
    for k in range(3):
        a = spin + k * 2.094
        sketch_line(cr, [(x + math.cos(a) * r * 0.42, y + math.sin(a) * r * 0.42), (x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.8)],
                    3, sid=9303 + k, amp=0.2, color=(0.5, 0.5, 0.52))

def draw_plane(cr, x, y, ang=0.0, t=0.0, part="front", prop=1.0, prop_ang=0.0, s=1.0, wheel=True, smoke=0.0, shake=0.0):
    """prop: 0 = stopped (one blade, at prop_ang), 1 = full-speed blur. shake: engine judder."""
    cr.save()
    if shake > 0: x += shake * 5 * math.sin(t * 61); y += shake * 5 * math.cos(t * 47)
    cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    if part == "back":                                                      # tail fin (behind the fuselage)
        sketch_poly(cr, [(-930, -150), (-990, -470), (-880, -470), (-700, -150)], 7, sid=9310, fill=PLANE_RED)
        sketch_line(cr, [(-960, -400), (-860, -400)], 5, sid=9311, amp=0.3, color=(1, 1, 1))
        cr.restore(); return
    if wheel:                                                               # landing gear
        wx, wy, wr = WHEEL
        sketch_line(cr, [(40, 140), (wx, wy)], 12, sid=9320, amp=0.3)
        sketch_line(cr, [(220, 130), (wx, wy)], 12, sid=9321, amp=0.3)
        plane_wheel(cr, wx, wy, wr, spin=t * 3)
    sketch_line(cr, [(-880, -20), (-900, 30)], 8, sid=9322, amp=0.2)       # tail skid
    sketch_circle(cr, -902, 42, 20, 5, sid=9323, fill=(0.2, 0.2, 0.22))
    body = [(-1000, -175), (-160, -150), (-150, -150), (150, -150), (360, -158), (520, -130), (560, -60), (560, 70),
            (520, 140), (300, 175), (0, 185), (-400, 120), (-800, 30), (-1000, -40)]
    sketch_poly(cr, body, 8, sid=9330, fill=PLANE_RED, amp=0.8)
    sketch_line(cr, [(-980, -60), (-300, 40), (300, 70), (540, 40)], 10, sid=9331, amp=0.4, color=(1, 1, 1))   # stripe
    sketch_poly(cr, [(430, -140), (560, -60), (560, 70), (520, 140), (430, 165)], 7, sid=9332, fill=STEEL, amp=0.5)  # cowling
    for k in range(3): sketch_line(cr, [(460 + 25 * k, -90), (460 + 25 * k, 120)], 3, sid=9333 + k, amp=0.3, alpha=0.6)
    sketch_poly(cr, [(-150, -150), (150, -150), (130, -175), (-130, -175)], 5, sid=9336, fill=PLANE_RED_D, amp=0.4)  # cockpit rim
    sketch_poly(cr, [(165, -150), (300, -150), (220, -300)], 5, sid=9337, fill=(0.80, 0.92, 1.0), alpha=0.75, amp=0.4)  # windshield
    sketch_poly(cr, [(-330, 30), (300, 30), (330, 70), (300, 115), (-330, 115), (-360, 70)], 7, sid=9338, fill=(1, 1, 1), amp=0.6)  # wing
    sketch_line(cr, [(-300, 72), (290, 72)], 9, sid=9339, amp=0.3, color=PLANE_RED)
    sketch_ellipse(cr, -900, -130, 150, 28, 6, sid=9340, fill=PLANE_RED)  # tailplane
    for k in range(6): sketch_line(cr, [(-250 + 110 * k, -40), (-250 + 110 * k, -38)], 6, sid=9341 + k, amp=0.1, alpha=0.5)  # rivets
    # propeller
    px = 590
    sketch_poly(cr, [(560, -45), (625, 0), (560, 45)], 6, sid=9350, fill=(0.95, 0.95, 0.95), amp=0.3)          # spinner
    if prop > 0.55:
        a = min(1.0, (prop - 0.55) / 0.3)
        cr.save(); cr.translate(px, 0); cr.scale(28, 300); cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore()
        cr.set_source_rgba(0.3, 0.3, 0.32, 0.18 * a); cr.fill()
        for k in range(3):
            yy = 300 * math.sin(t * 40 + k * 2.1)
            sketch_line(cr, [(px - 8, yy - 70), (px + 8, yy + 70)], 9, sid=9351 + k, amp=0.2, alpha=0.35 * a)
        for sgn in (-1, 1):
            cr.save(); cr.translate(px + 10, 0); cr.scale(45, 300)
            cr.arc(0, 0, 1, (0.25 if sgn > 0 else 0.9) * math.pi + 0.15, (0.75 if sgn > 0 else 1.1) * math.pi - 0.15)
            cr.restore(); stroke_ink(cr, 4, alpha=0.5 * a)
    if prop < 0.85:                                                         # the blade itself (seen edge-on, spinning)
        a = 1.0 - max(0.0, (prop - 0.55) / 0.3)
        L_ = 290 * math.cos(prop_ang)
        cr.push_group()
        sketch_poly(cr, [(px - 12, 0), (px - 16, -L_), (px + 16, -L_), (px + 12, 0), (px + 16, L_), (px - 16, L_)], 6, sid=9355,
                    fill=(0.45, 0.30, 0.18), amp=0.3)
        cr.pop_group_to_source(); cr.paint_with_alpha(a)
    cr.restore()

def draw_smoke_puff(cr, x, y, r, alpha=1.0, dark=0.0):
    col = lerp((0.85, 0.85, 0.85), (0.18, 0.18, 0.2), dark)
    cr.push_group()
    for dx, dy, k in ((-0.45, 0.1, 0.65), (0.35, 0.05, 0.7), (0.0, -0.35, 0.75), (0.0, 0.25, 0.7)):
        cr.arc(x + dx * r, y + dy * r, k * r, 0, 2 * math.pi); cr.new_sub_path()
    cr.set_source_rgb(*INK); cr.set_line_width(max(3, r * 0.09)); cr.stroke_preserve(); cr.set_source_rgb(*col); cr.fill()
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha)

def draw_windsock(cr, x, yb=FLOOR_Y, t=0.0, h=620):
    sketch_line(cr, [(x, yb), (x, yb - h)], 10, sid=9400, amp=0.3)
    pts_t, pts_b = [], []
    for k in range(6):
        u = k / 5; xx = x + 20 + 260 * u
        sag = 40 * u * u + 10 * math.sin(t * 5 - k * 0.9) * u
        rr = 50 * (1 - 0.45 * u)
        pts_t.append((xx, yb - h + 10 - rr + sag)); pts_b.append((xx, yb - h + 10 + rr + sag))
    for k in range(5):
        q = [pts_t[k], pts_t[k + 1], pts_b[k + 1], pts_b[k]]
        sketch_poly(cr, q, 5, sid=9401 + k, fill=((1.0, 0.55, 0.18) if k % 2 == 0 else (1, 1, 1)), amp=0.3)

def draw_hangar(cr, cx, yb=FLOOR_Y, w=1200, h=720):
    x0, x1 = cx - w / 2, cx + w / 2
    pts = [(x0, yb)] + [(cx + w / 2 * math.cos(math.pi - math.pi * k / 16), yb - 260 - (h - 260) * math.sin(math.pi * k / 16)) for k in range(17)] + [(x1, yb)]
    sketch_poly(cr, pts, 7, sid=9410, fill=(0.80, 0.82, 0.84), amp=0.6)
    for k in range(1, 8):
        xx = x0 + w * k / 8
        sketch_line(cr, [(xx, yb), (xx, yb - 260 - (h - 260) * math.sqrt(max(0.0, 1 - ((xx - cx) / (w / 2)) ** 2)))], 3, sid=9411 + k, amp=0.3, alpha=0.4)
    sketch_rect(cr, cx - 330, yb - 430, cx + 330, yb, 6, sid=9420, fill=(0.32, 0.33, 0.36))

def draw_airfield_world(cr, t, x0=1300, x1=40000, sign_x=2350, sock_x=3700, hangar_x=1950):
    """pale sky up to deep blue high above, clouds, a grass airfield right of x0 with a long runway strip, a hangar,
    a windsock and a FLIGHT SCHOOL sign. Left of x0 nothing is drawn (the empty white room)."""
    g = cairo.LinearGradient(0, 900, 0, -9000)                             # pale sky -> blue -> the black of space
    g.add_color_stop_rgb(0.0, 0.80, 0.89, 0.98); g.add_color_stop_rgb(0.42, 0.45, 0.62, 0.92)
    g.add_color_stop_rgb(0.75, 0.10, 0.14, 0.35); g.add_color_stop_rgb(1.0, 0.02, 0.02, 0.06)
    cr.rectangle(x0, -16000, x1 - x0, 16000 + FLOOR_Y); cr.set_source(g); cr.fill()
    for k in range(400):                                                    # stars, high up
        sx = x0 + (k * 7919) % int(x1 - x0); sy = -4800 - (k * 3571) % 11000
        a = clamp01((-sy - 4800) / 2500) * (0.6 + 0.4 * math.sin(t * 2 + k))
        cr.rectangle(sx, sy, 9, 9); cr.set_source_rgba(1, 1, 0.92, a); cr.fill()
    for k in range(60):                                                     # clouds, all the way along
        cx = x0 + 600 + k * 640 + 230 * math.sin(k * 2.3)
        cy = -2800 + ((k * 977) % 3300)
        if cy > 700: cy -= 1400
        draw_cloud(cr, cx + 10 * math.sin(t * 0.3 + k), cy, 0.8 + 0.35 * ((k * 37) % 10) / 10)
    cr.rectangle(x0, FLOOR_Y, x1 - x0, 3000); cr.set_source_rgb(*GRASS); cr.fill()
    cr.rectangle(x0, FLOOR_Y, x1 - x0, 60); cr.set_source_rgb(0.72, 0.72, 0.70); cr.fill()      # runway
    for k in range(int((x1 - x0) / 300)):
        cr.rectangle(x0 + 80 + k * 300, FLOOR_Y + 24, 150, 12); cr.set_source_rgb(1, 1, 1); cr.fill()
    sketch_line(cr, [(x0, FLOOR_Y), (min(x1, x0 + 20000), FLOOR_Y)], 3.5, sid=9430, amp=1.3, alpha=0.8)
    sketch_line(cr, [(x0, FLOOR_Y), (x0, FLOOR_Y + 3000)], 3.5, sid=9431, amp=1.0, alpha=0.5)
    draw_hangar(cr, hangar_x)
    draw_windsock(cr, sock_x, t=t)
    sketch_rect(cr, sign_x - 14, FLOOR_Y - 420, sign_x + 14, FLOOR_Y, 5, sid=9440, fill=(0.6, 0.6, 0.62))
    sketch_rect(cr, sign_x - 230, FLOOR_Y - 560, sign_x + 230, FLOOR_Y - 380, 6, sid=9441, fill=(1, 1, 1))
    draw_text(cr, "FLIGHT SCHOOL", sign_x, FLOOR_Y - 470, 62, color=(200, 40, 34), max_w=420)

PUKE = (0.62, 0.80, 0.30)
PUKE_D = (0.45, 0.62, 0.18)
def draw_puke(cr, x, y, r, t=0.0, ang=0.0, squash=0.0):
    """wobbly cartoon blob of green puke, centre (x, y), radius r (squash 0..1 flattens it into a splat)."""
    pts = []
    for k in range(24):
        a = 2 * math.pi * k / 24
        rr = r * (1 + 0.12 * math.sin(3 * a + t * 5) + 0.07 * math.sin(5 * a - t * 7))
        pts.append((x + math.cos(a + ang) * rr * (1 + 0.8 * squash), y + math.sin(a + ang) * rr * (1 - 0.75 * squash)))
    sketch_poly(cr, pts, max(4, r * 0.08), sid=9500, fill=PUKE, amp=0.3)
    for k, (dx, dy, kr) in enumerate(((-0.35, 0.2, 0.18), (0.3, -0.1, 0.14), (0.05, 0.4, 0.12), (0.4, 0.35, 0.1))):
        cr.arc(x + (dx * math.cos(ang) - dy * math.sin(ang)) * r * (1 + 0.8 * squash),
               y + (dx * math.sin(ang) + dy * math.cos(ang)) * r * (1 - 0.75 * squash), kr * r, 0, 2 * math.pi)
        cr.set_source_rgb(*PUKE_D); cr.fill()
    cr.arc(x - 0.3 * r, y - 0.35 * r * (1 - 0.75 * squash), 0.14 * r, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.7); cr.fill()

def draw_flames(cr, pts, t=0.0, w=1.0):
    """a flickering cartoon fire tongue along pts (from the hot end outwards), outer orange + inner yellow."""
    for col, k in (((1.0, 0.45, 0.10), 1.0), ((1.0, 0.85, 0.25), 0.55)):
        left, right = [], []
        n = len(pts)
        for i, (x, y) in enumerate(pts):
            u = i / max(1, n - 1)
            hw = w * k * (1 - u) ** 0.8 * (1 + 0.25 * math.sin(t * 31 + i * 1.7))
            if i < n - 1: dx, dy = pts[i + 1][0] - x, pts[i + 1][1] - y
            else: dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
            L_ = math.hypot(dx, dy) or 1.0; nx, ny = -dy / L_, dx / L_
            left.append((x + nx * hw, y + ny * hw)); right.append((x - nx * hw, y - ny * hw))
        sketch_poly(cr, left + right[::-1], 5 if k == 1.0 else 0.1, sid=9510, fill=col, amp=0.4)

def draw_space(cr, t, cx, cy, R=9000.0):
    cr.rectangle(cx - 20000, cy - 30000, 40000, 40000); cr.set_source_rgb(0.02, 0.02, 0.06); cr.fill()
    for k in range(260):
        sx = cx - 3000 + (k * 7919) % 6000; sy = cy - R - 4200 + (k * 3571) % 4800
        cr.rectangle(sx, sy, 8, 8); cr.set_source_rgba(1, 1, 0.92, 0.55 + 0.45 * math.sin(t * 2 + k)); cr.fill()
    ex, ey = cx, cy                                                         # the Earth, its top at cy - R
    for i, (dr, a) in enumerate(((260, 0.12), (170, 0.2), (90, 0.35))):    # atmosphere glow
        cr.arc(ex, ey, R + dr, 0, 2 * math.pi); cr.set_source_rgba(0.55, 0.78, 1.0, a); cr.fill()
    cr.arc(ex, ey, R, 0, 2 * math.pi); cr.set_source_rgb(0.24, 0.50, 0.86); cr.fill()
    cr.save(); cr.arc(ex, ey, R, 0, 2 * math.pi); cr.clip()
    for k, (dx, w_, h_) in enumerate(((-1500, 900, 260), (300, 1300, 380), (1900, 700, 220), (-3200, 1100, 300))):
        sketch_ellipse(cr, ex + dx, ey - R + 260 + 60 * k, w_, h_, 5, sid=9520 + k, fill=(0.42, 0.70, 0.36))
    for k in range(6):
        sketch_ellipse(cr, ex - 2600 + k * 1050, ey - R + 120 + 90 * (k % 3), 380, 50, 0.1, sid=9530 + k, fill=(1, 1, 1), alpha=0.8)
    cr.restore()
    cr.arc(ex, ey, R, 0, 2 * math.pi); stroke_ink(cr, 8)
