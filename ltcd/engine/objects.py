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
    draw_ring(cr, x, y, t, r)              a spinning gold ring (the generic speed-game collectible); flat=0..1 lies down
    draw_palm(cr, x, t, h, bend)           cartoon palm tree (banded trunk, big fronds) standing at x on the floor
    draw_sunflower(cr, x, t, h)            a big sunflower whose petals turn slowly
    draw_loop(cr, cx, R, t)                giant checkered loop-de-loop: running surface radius R, bottom at (cx, FLOOR_Y)
    draw_green_hill_world(cr, t, x0, ...)  generic green-hill speed-game world right of x0: blue sky bands, clouds,
                                           far hills, sparkling water, palms, sunflowers, grass on checkered brown
                                           dirt; optional loop; nothing drawn left of x0 (no names, no characters)
    draw_signpost(cr, x, text)             a wooden arrow signpost pointing right
    draw_ring_hud(cr, n, ...)              screen-space RINGS counter (top-left, inside the safe zone)
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

def draw_mom(cr, t, p, blink=0.0, s=0.92, alpha=1.0, hair=None, dress=None, bun=True, phones=0.0):
    """draw a mom on his rig. p = a constrained pose (world coords, feet at FLOOR_Y). Long dark hair with a bun on top
    (covers his signature curl), a pink dress, otherwise the same line style. Drawn scaled s around her feet.
    p["back"] = 1 shows her from behind (all hair)."""
    if alpha < 0.01: return
    HAIR_ = hair or HAIR; DRESS_ = dress or DRESS
    fx = (p["lfoot"][0] + p["rfoot"][0]) / 2
    cr.push_group()
    cr.save(); cr.translate(fx, FLOOR_Y); cr.scale(s, s); cr.translate(-fx, -FLOOR_Y)
    hx, hy = p["head"]; tl = p.get("tilt", 0.0); tn = p.get("turn", 0.0); bk = p.get("back", 0.0) > 0.5
    cr.save(); cr.translate(hx, hy); cr.rotate(tl)                          # hair behind the head
    sketch_poly(cr, [(-135 - 10 * tn, -20), (-120, -110), (-60, -150), (60, -150), (120, -110), (135 - 10 * tn, -20),
                     (140, 120), (95, 170), (-95, 170), (-140, 120)], 6, sid=7601, fill=HAIR_, amp=1.0)
    cr.restore()
    q = dict(p); q["larm_over"] = q["rarm_over"] = 1.0
    C.draw_guy(cr, t, q, blink)
    nx, ny = p["neck"]; hpx, hpy = p["hip"]
    sketch_poly(cr, [(nx - 26, ny + 22), (nx + 26, ny + 22), (hpx + 50, hpy - 40), (hpx + 105, hpy + 150), (hpx - 105, hpy + 150),
                     (hpx - 50, hpy - 40)], 6, sid=7602, fill=DRESS_, amp=1.0)
    C.draw_arm_over(cr, q, "l"); C.draw_arm_over(cr, q, "r")
    cr.save(); cr.translate(hx, hy); cr.rotate(tl)                          # bangs (or the whole back of the head) + bun
    cr.save(); cr.arc(0, 0, C.HEAD_R + 2, 0, 2 * math.pi); cr.clip()
    if bk:
        cr.rectangle(-200, -200, 400, 400); cr.set_source_rgb(*HAIR_); cr.fill()
    else:
        sketch_poly(cr, [(-140, -160), (140, -160), (140, -40), (60 + 30 * tn, -62), (10 * tn, -80), (-60 + 30 * tn, -60), (-140, -40)],
                    6, sid=7603, fill=HAIR_, amp=0.8)
    cr.restore()
    if bk: cr.arc(0, 0, C.HEAD_R, 0, 2 * math.pi); stroke_ink(cr, 7)
    if bun: sketch_circle(cr, 8 * tn, -C.HEAD_R - 30, 52, 6, sid=7604, fill=HAIR_)
    if phones > 0.01 and not bk:                                         # headphones: 0 = round her neck, 1 = on her ears
        ph = smooth(phones)
        for sd in (-1, 1):
            ex, ey = sd * (C.HEAD_R + 6) * (1 - 0.35 * (1 - ph)), lerp(C.HEAD_R + 70, 10, ph)
            sketch_ellipse(cr, ex, ey, 26, 40, 5, sid=7606 + (sd > 0), fill=(0.20, 0.22, 0.28))
        if ph > 0.5:
            cr.arc(0, 10, C.HEAD_R + 12, math.pi * 1.02, math.pi * 1.98); stroke_ink(cr, 14); cr.new_path()
            cr.arc(0, 10, C.HEAD_R + 12, math.pi * 1.02, math.pi * 1.98); cr.set_source_rgb(0.20, 0.22, 0.28); cr.set_line_width(7); cr.stroke()
        else:
            cr.arc(0, C.HEAD_R + 70, C.HEAD_R * 0.75, 0.15 * math.pi, 0.85 * math.pi); stroke_ink(cr, 14); cr.new_path()
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


# ---------------------------------------------------------------- green hill (generic speed-game world, day 9)
GOLD_R = (1.0, 0.80, 0.12)
GH_GRASS = (0.36, 0.74, 0.25)
GH_GRASS_D = (0.24, 0.55, 0.16)
GH_DIRT = ((0.80, 0.50, 0.20), (0.58, 0.33, 0.12))
GH_SKY = ((0.62, 0.84, 1.0), (0.22, 0.48, 0.92))
GH_WATER = (0.24, 0.55, 0.92)

def draw_ring(cr, x, y, t=0.0, r=52.0, flat=0.0, alpha=1.0, spin=4.0):
    """spinning gold ring centre (x, y). flat 0..1 = tipped over lying on the floor (thin horizontal ellipse)."""
    w = max(0.18, abs(math.cos(t * spin))) if flat <= 0 else 1.0
    rx, ry = r * w, r * (1 - 0.82 * flat)
    cr.push_group()
    cr.save(); cr.translate(x, y); cr.scale(max(rx, 1) / r, max(ry, 1) / r)
    cr.arc(0, 0, r, 0, 2 * math.pi); cr.restore()
    cr.set_source_rgb(*INK); cr.set_line_width(26); cr.stroke_preserve()
    cr.set_source_rgb(*GOLD_R); cr.set_line_width(14); cr.stroke()
    cr.save(); cr.translate(x, y); cr.scale(max(rx, 1) / r, max(ry, 1) / r)
    cr.arc(0, 0, r, math.pi * 1.1, math.pi * 1.45); cr.restore()
    cr.set_source_rgba(1, 1, 0.85, 0.9); cr.set_line_width(5); cr.stroke()
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha)

def draw_sparkle(cr, x, y, u, r=70, color=GOLD_R):
    """a little 4-point collect sparkle, u 0..1 life."""
    if not (0 <= u < 1): return
    a = 1 - u; s = r * (0.4 + 0.8 * u)
    for k in range(4):
        ang = k * math.pi / 2 + 0.4
        cr.move_to(x + math.cos(ang) * s * 0.3, y + math.sin(ang) * s * 0.3)
        cr.line_to(x + math.cos(ang) * s, y + math.sin(ang) * s)
    cr.set_source_rgba(*INK, a); cr.set_line_width(9); cr.stroke_preserve()
    cr.set_source_rgba(*color, a); cr.set_line_width(5); cr.stroke()

def palm_pt(x, h, bend, u, yb=FLOOR_Y):
    """point at height fraction u (0 foot .. 1 top) of a palm trunk of height h, leaning right by bend."""
    return (x + 60 * math.sin(u * 2.2) + bend * 260 * u * u, yb - h * u)

def draw_palm(cr, x, t=0.0, h=820.0, bend=0.0, yb=FLOOR_Y, s=1.0, sid=0):
    """cartoon palm tree: banded trunk curving a little, six big fronds and coconuts on top."""
    n = 9
    for k in range(n):                                                   # trunk segments, alternating tan / brown
        u0, u1 = k / n, (k + 1) / n
        (ax, ay), (bx, by) = palm_pt(x, h, bend, u0, yb), palm_pt(x, h, bend, u1, yb)
        w0, w1 = 52 * s * (1 - 0.35 * u0), 52 * s * (1 - 0.35 * u1)
        pts = [(ax - w0, ay), (bx - w1, by + 4), (bx + w1, by + 4), (ax + w0, ay)]
        sketch_poly(cr, pts, 5, sid=sid + 9600 + k, fill=((0.80, 0.58, 0.32) if k % 2 == 0 else (0.62, 0.42, 0.20)), amp=0.4)
    tx, ty = palm_pt(x, h, bend, 1.0, yb)
    sw = math.sin(t * 1.3 + x * 0.01) * 0.06 + bend * 0.6
    for k, (ang, L_) in enumerate(((-2.9, 380), (-2.3, 420), (-1.75, 330), (-1.25, 400), (-0.7, 430), (-0.15, 370))):
        a = ang + sw
        tip = (tx + math.cos(a) * L_ * s, ty + math.sin(a) * L_ * s + 140 * s * abs(math.cos(a)))
        mid = (tx + math.cos(a) * L_ * 0.55 * s, ty + math.sin(a) * L_ * 0.55 * s - 40 * s)
        nx, ny = -math.sin(a), math.cos(a)
        pts = [(tx, ty), (mid[0] + nx * 55 * s, mid[1] + ny * 55 * s), tip, (mid[0] - nx * 40 * s, mid[1] - ny * 40 * s)]
        sketch_poly(cr, pts, 5, sid=sid + 9620 + k, fill=GH_GRASS if k % 2 else GH_GRASS_D, amp=0.5)
    for k, (dx, dy) in enumerate(((-30, 30), (25, 35), (0, 55))):
        sketch_circle(cr, tx + dx * s, ty + dy * s, 26 * s, 4, sid=sid + 9640 + k, fill=(0.45, 0.30, 0.15))

def draw_sunflower(cr, x, t=0.0, h=300.0, yb=FLOOR_Y, sid=0):
    sketch_line(cr, [(x, yb), (x + 6, yb - h)], 9, sid=sid + 9650, amp=0.4, color=GH_GRASS_D)
    sketch_ellipse(cr, x - 40, yb - h * 0.4, 40, 16, 4, rot=-0.5, sid=sid + 9651, fill=GH_GRASS)
    cx, cy = x + 6, yb - h
    sp = t * 0.8 + x
    for k in range(10):
        a = sp + k * 2 * math.pi / 10
        sketch_ellipse(cr, cx + math.cos(a) * 62, cy + math.sin(a) * 62, 36, 18, 3.5, rot=a, sid=sid + 9652 + k, fill=(1.0, 0.82, 0.15))
    sketch_circle(cr, cx, cy, 42, 4.5, sid=sid + 9665, fill=(0.50, 0.30, 0.12))

def draw_signpost(cr, x, text="GREEN HILL", yb=FLOOR_Y):
    sketch_rect(cr, x - 14, yb - 430, x + 14, yb, 5, sid=9670, fill=(0.62, 0.42, 0.24))
    pts = [(x - 250, yb - 560), (x + 200, yb - 560), (x + 280, yb - 485), (x + 200, yb - 410), (x - 250, yb - 410)]
    sketch_poly(cr, pts, 6, sid=9671, fill=(0.80, 0.60, 0.36))
    draw_text(cr, text, x - 15, yb - 485, 60, max_w=420)

def _visible(cr, pad=600):
    x0, y0, x1, y1 = cr.clip_extents()
    return x0 - pad, y0 - pad, x1 + pad, y1 + pad

def draw_loop(cr, cx, R, t=0.0, yb=FLOOR_Y, part="back"):
    """giant checkered loop. Running surface = circle radius R around (cx, yb - R); the band goes outward 110 px."""
    cy = yb - R; n = 40; W_ = 110
    if part == "back":
        for k in range(n):
            a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
            cr.move_to(cx + R * math.cos(a0), cy + R * math.sin(a0))
            cr.arc(cx, cy, R, a0, a1); cr.arc_negative(cx, cy, R + W_, a1, a0); cr.close_path()
            cr.set_source_rgb(*GH_DIRT[k % 2]); cr.fill()
        cr.arc(cx, cy, R + W_, 0, 2 * math.pi); cr.set_source_rgb(*INK); cr.set_line_width(9); cr.stroke()
        cr.arc(cx, cy, R + 14, 0, 2 * math.pi); cr.set_source_rgb(*GH_GRASS); cr.set_line_width(28); cr.stroke()
        cr.arc(cx, cy, R, 0, 2 * math.pi); cr.set_source_rgb(*INK); cr.set_line_width(8); cr.stroke()
        for sx in (-1, 1):                                                  # little ramps where it meets the ground
            pts = [(cx + sx * (R * 0.55), yb), (cx + sx * (R * 0.98), yb - R * 0.35), (cx + sx * (R + W_ + 120), yb)]
            sketch_poly(cr, pts, 6, sid=9680 + (sx > 0), fill=GH_DIRT[1], amp=0.4)

def draw_green_hill_world(cr, t, x0=9700, x1=80000, loop=None, palms=(), flowers=(), yb=FLOOR_Y):
    """generic green-hill world right of x0 (nothing left of it). loop = (cx, R) or None."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    a, b = max(x0, vx0), min(x1, vx1)
    if b <= a: return
    cr.save(); cr.rectangle(x0, vy0 - 10, x1 - x0, vy1 - vy0 + 20); cr.clip()
    _gh_draw(cr, t, x0, x1, a, b, vy0, vy1, loop, palms, flowers, yb)
    cr.restore()

def _gh_draw(cr, t, x0, x1, a, b, vy0, vy1, loop, palms, flowers, yb):
    top = min(vy0, yb - 200)
    nb = 30                                                                  # sky: solid bands (no far-off gradients)
    for k in range(nb):
        y_hi = yb - 260 - (k + 1) * 110
        y_lo = yb - 260 - k * 110 if k else yb + 10
        if k == nb - 1: y_hi = min(y_hi, top - 10)
        cr.rectangle(a, y_hi, b - a, y_lo - y_hi + 1); cr.set_source_rgb(*lerp(GH_SKY[0], GH_SKY[1], min(1.0, k / 18))); cr.fill()
    for k in range(int((a - x0) // 900) - 1, int((b - x0) // 900) + 2):    # clouds
        cx = x0 + k * 900 + 200 * math.sin(k * 2.1)
        draw_cloud(cr, cx + 12 * math.sin(t * 0.3 + k), yb - 1230 - 260 * ((k * 37) % 5) / 5, 0.75 + 0.3 * ((k * 13) % 4) / 4)
    for k in range(int((a - x0) // 700) - 1, int((b - x0) // 700) + 2):    # far rounded hills
        hx = x0 + k * 700 + 150 * math.sin(k * 1.7); hr = 300 + 90 * ((k * 7) % 3)
        cr.arc(hx, yb - 300 + hr * 0.25, hr, math.pi, 2 * math.pi); cr.close_path()
        cr.set_source_rgb(0.56, 0.80, 0.50); cr.fill_preserve(); cr.set_source_rgba(*INK, 0.5); cr.set_line_width(5); cr.stroke()
    cr.rectangle(a, yb - 300, b - a, 300); cr.set_source_rgb(*GH_WATER); cr.fill()      # sparkling water
    for k in range(int((a - x0) // 160), int((b - x0) // 160) + 1):
        wx = x0 + k * 160 + 40 * math.sin(t * 1.5 + k); wy = yb - 260 + (k * 53) % 200
        cr.rectangle(wx, wy, 70, 7); cr.set_source_rgba(1, 1, 1, 0.55 + 0.45 * math.sin(t * 3 + k)); cr.fill()
    sketch_line(cr, [(a, yb - 300), (b, yb - 300)], 4, sid=9690, amp=0.6, alpha=0.6)
    for px, ph in palms:
        if a - 700 < px < b + 700: draw_palm(cr, px, t, ph, sid=int(px) % 97)
    if loop: draw_loop(cr, loop[0], loop[1], t, yb)
    sq = 90                                                                   # checkered dirt below the grass
    i0, i1 = int((a - x0) // sq), int((b - x0) // sq) + 1
    for row in range(int(max(0, (min(vy1, yb + 3000) - yb - 60)) // sq) + 2):
        y = yb + 60 + row * sq
        for i in range(i0, i1):
            cr.rectangle(x0 + i * sq, y, sq + 0.5, sq + 0.5); cr.set_source_rgb(*GH_DIRT[(i + row) % 2]); cr.fill()
    cr.rectangle(a, yb, b - a, 60); cr.set_source_rgb(*GH_GRASS); cr.fill()             # grass strip, scalloped
    cr.move_to(a, yb + 60)
    for i in range(int((a - x0) // 60), int((b - x0) // 60) + 2):
        xx = x0 + i * 60; cr.line_to(xx + 30, yb + 92); cr.line_to(xx + 60, yb + 60)
    cr.line_to(b, yb + 60); cr.close_path(); cr.set_source_rgb(*GH_GRASS); cr.fill()
    sketch_line(cr, [(a, yb), (b, yb)], 4, sid=9691, amp=1.0, alpha=0.85)
    for fx in flowers:
        if a - 200 < fx < b + 200: draw_sunflower(cr, fx, t, 280 + 60 * (int(fx) % 3), sid=int(fx) % 53)

def draw_ring_hud(cr, n, x=70, y=330, alpha=1.0, warn=0.0):
    """screen-space RINGS counter, left-anchored. warn 0..1 turns the number red (flashing is up to the caller)."""
    if alpha <= 0.01: return
    col = lerp((255, 205, 30), (230, 40, 30), warn)
    cr.push_group()
    for txt, xx, size in (("RINGS", x, 70), (str(int(n)), x + 245, 76)):
        for dx, dy in ((-4, 0), (4, 0), (0, -4), (0, 4), (-3, -3), (3, 3), (-3, 3), (3, -3)):
            draw_text(cr, txt, xx + dx, y + dy, size, color=(18, 18, 22), anchor="left")
        draw_text(cr, txt, xx, y, size, color=tuple(int(c) for c in (col if txt != "RINGS" else (255, 205, 30))), anchor="left")
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha)

def draw_ladybot(cr, x, yb=FLOOR_Y, t=0.0, face=-1, poke=0.0, look_up=0.0, bob=0.0, wheel_ang=0.0, s=1.0):
    """the most harmless little speed-game enemy: a red ladybug robot on one wheel. (x, yb) = wheel contact.
    face -1 = facing left. poke 0..1 shoots its little nose out; look_up 0..1 tilts the eye up."""
    cr.save(); cr.translate(x, yb - bob); cr.scale(face * -1 * s, s)          # local: facing LEFT = -x
    sketch_circle(cr, 0, -30, 30, 5, sid=9700, fill=(0.55, 0.60, 0.68))       # the wheel
    cr.move_to(0, -30); cr.line_to(22 * math.cos(wheel_ang), -30 + 22 * math.sin(wheel_ang)); stroke_ink(cr, 4)
    sketch_line(cr, [(0, -30), (10, -62)], 6, sid=9701)
    nose = 30 + 45 * poke                                                       # the poker
    sketch_poly(cr, [(-70, -108), (-70 - nose, -98), (-70, -88)], 4, sid=9702, fill=(0.75, 0.76, 0.80))
    pts = [(-80 + 160 * k / 16, -60 - 75 * math.sin(math.pi * k / 16)) for k in range(17)]
    sketch_poly(cr, pts, 6, sid=9703, fill=(0.88, 0.18, 0.16))                  # red dome
    for k, (dx, dy, r) in enumerate(((10, -112, 11), (40, -92, 9), (-15, -80, 8), (52, -70, 7))):
        cr.arc(dx, dy, r, 0, 2 * math.pi); fill_ink(cr); cr.new_path()
    sketch_line(cr, [(15, -133), (15, -60)], 3, sid=9704, alpha=0.6)
    sketch_circle(cr, -48, -100, 19, 4, sid=9705, fill=WHITE)                   # one big eye
    cr.arc(-54 + 2 * look_up, -100 - 9 * look_up, 7.5, 0, 2 * math.pi); fill_ink(cr); cr.new_path()
    sketch_line(cr, [(-30, -132), (-38, -158)], 3.5, sid=9706)                  # antenna
    sketch_circle(cr, -39, -162, 6, 3, sid=9707, fill=(1.0, 0.82, 0.15))
    cr.restore()


# ---------------------------------------------------------------- the dark land (day 10): ash plain, volcano, the eye
DL_SKY = ((0.92, 0.42, 0.16), (0.46, 0.17, 0.12))
DL_ASH = (0.30, 0.27, 0.26)
DL_ROCK = (0.22, 0.18, 0.18)
LAVA = (1.0, 0.45, 0.10)
LAVA_B = (1.0, 0.84, 0.28)
EYE_FIRE = (1.0, 0.62, 0.12)

def volcano_rim(vx, h, yb=FLOOR_Y):
    """(left rim x, right rim x, rim y) of the volcano drawn by draw_volcano."""
    return vx - 280, vx + 280, yb - h

def draw_volcano(cr, vx, h, t=0.0, yb=FLOOR_Y, w=1800, glow=1.0, smoke=1.0):
    """a big dark cartoon volcano: concave cone, glowing crater, lava streaks, a lazy smoke plume."""
    lx, rx, ry = volcano_rim(vx, h, yb)
    pts = [(vx - w, yb)]
    for k in range(1, 12):
        u = k / 12; pts.append((lerp(vx - w, lx, u), yb - h * (u ** 1.3)))
    pts += [(lx, ry), (rx, ry)]
    for k in range(11, 0, -1):
        u = k / 12; pts.append((lerp(vx + w, rx, u), yb - h * (u ** 1.3)))
    pts.append((vx + w, yb))
    sketch_poly(cr, pts, 7, sid=9800, fill=(0.27, 0.21, 0.20), amp=0.5)
    sketch_ellipse(cr, vx, ry, 280, 46, 6, sid=9801, fill=lerp((0.5, 0.2, 0.1), LAVA, glow))
    for k, (sx, ln) in enumerate(((-0.55, 0.55), (0.25, 0.7), (0.7, 0.4), (-0.15, 0.35))):    # lava streaks
        x0 = vx + sx * 240; q = []
        for i in range(10):
            u = ln * i / 9; yy = ry + h * u
            spread = (w - 280) * (u ** (1 / 1.3)) * (1 if sx > 0 else -1) * abs(sx) * 0.9
            q.append((x0 + spread + 22 * math.sin(i * 1.3 + k), yy))
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        path(cr, q); stroke_ink(cr, 30); path(cr, q); stroke_ink(cr, 18, LAVA)
    for k in range(5):                                                         # smoke plume, drifting left
        a = (t * 0.12 + k / 5) % 1.0
        draw_smoke_puff(cr, vx - 600 * a, ry - 120 - 1500 * a, 120 + 380 * a, alpha=smoke * (1 - a) * 0.85, dark=0.75)

def draw_eye_tower(cr, x, h, t=0.0, yb=FLOOR_Y, look=0.0, lid=0.0, s=1.0, water=0.0, look_y=0.0, flare=1.0):
    """a tall black spiked tower with a giant flaming slit eye cradled between two horns at the top.
    look -1..1 moves the pupil left/right, lid 0..1 closes the eye (it blinks), water 0..1 a big tear forming."""
    top = yb - h
    tw = 150 * s
    body = [(x - tw * 1.9, yb), (x - tw * 0.9, top + 260 * s), (x - tw * 1.25, top + 120 * s), (x - tw * 0.6, top + 200 * s),
            (x + tw * 0.6, top + 200 * s), (x + tw * 1.25, top + 120 * s), (x + tw * 0.9, top + 260 * s), (x + tw * 1.9, yb)]
    sketch_poly(cr, body, 7, sid=9810, fill=(0.12, 0.10, 0.11), amp=0.4)
    for sx in (-1, 1):                                                         # the two horns
        horn = [(x + sx * tw * 0.75, top + 210 * s), (x + sx * tw * 1.25, top + 60 * s), (x + sx * tw * 0.95, top - 220 * s),
                (x + sx * tw * 1.55, top + 40 * s), (x + sx * tw * 1.25, top + 230 * s)]
        sketch_poly(cr, horn, 6, sid=9811 + (sx > 0), fill=(0.12, 0.10, 0.11), amp=0.3)
    for k in range(4):                                                         # little windows
        sketch_rect(cr, x - 18 * s, top + (420 + 230 * k) * s, x + 18 * s, top + (470 + 230 * k) * s, 3, sid=9813 + k, fill=EYE_FIRE)
    ex, ey = x, top + 40 * s
    ew, eh = 210 * s, 105 * s
    for k in range(10):                                                        # flames round the eye
        a = 2 * math.pi * k / 10 + 0.3
        bx, by = ex + math.cos(a) * ew * 0.9, ey + math.sin(a) * eh * 0.9
        L = (90 + 40 * math.sin(t * 9 + k * 2.1)) * s * flare
        draw_flames(cr, [(bx + math.cos(a) * L * i / 5, by + math.sin(a) * L * i / 5 - 18 * s * i / 5) for i in range(6)], t + k, w=46 * s)
    def almond():
        cr.move_to(ex - ew, ey); cr.curve_to(ex - ew * 0.5, ey - eh * 1.35, ex + ew * 0.5, ey - eh * 1.35, ex + ew, ey)
        cr.curve_to(ex + ew * 0.5, ey + eh * 1.35, ex - ew * 0.5, ey + eh * 1.35, ex - ew, ey); cr.close_path()
    almond(); cr.set_source_rgb(*EYE_FIRE); cr.fill()
    cr.save(); almond(); cr.clip()
    cr.arc(ex, ey, ew * 0.6, 0, 2 * math.pi); cr.set_source_rgb(*LAVA_B); cr.fill()
    px = ex + look * ew * 0.45
    cr.save(); cr.translate(px, ey + look_y * eh * 0.35); cr.scale(0.22, 1.0); cr.arc(0, 0, eh * 0.95, 0, 2 * math.pi); cr.restore()
    cr.set_source_rgb(0.05, 0.03, 0.03); cr.fill()
    if lid > 0.01:                                                             # lids meet in the middle
        lc = (0.12, 0.10, 0.11)
        cr.rectangle(ex - ew, ey - eh * 1.2, ew * 2, eh * 1.2 * lid); cr.set_source_rgb(*lc); cr.fill()
        cr.rectangle(ex - ew, ey + eh * 1.2 * (1 - lid), ew * 2, eh * 1.2 * lid); cr.set_source_rgb(*lc); cr.fill()
    cr.restore()
    almond(); stroke_ink(cr, 7 * s)
    if water > 0.02:                                                           # a fat tear welling at the corner
        r = 26 * s * water
        cr.arc(ex + ew * 0.8, ey + eh * 0.55 + 30 * s * water, r, 0, 2 * math.pi)
        cr.set_source_rgb(0.70, 0.84, 0.94); cr.fill_preserve(); stroke_ink(cr, 4 * s)

def draw_dark_land_world(cr, t, x0=24900, x1=45000, volcano=None, tower=None, yb=FLOOR_Y, ash=1.0, gate=None):
    """generic dark land right of x0: blood-orange sky in solid bands, jagged far mountains, an ash plain with
    glowing cracks. volcano = (vx, h[, w]) or None; tower = dict(x, h, look, lid, water) or None."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    a, b = max(x0, vx0), min(x1, vx1)
    if b <= a: return
    cr.save(); cr.rectangle(x0, vy0 - 10, x1 - x0, vy1 - vy0 + 20); cr.clip()
    top = min(vy0, yb - 200)
    for k in range(30):
        y_hi = yb - 200 - (k + 1) * 120
        y_lo = yb - 200 - k * 120 if k else yb + 10
        if k == 29: y_hi = min(y_hi, top - 10)
        cr.rectangle(a, y_hi, b - a, y_lo - y_hi + 1); cr.set_source_rgb(*lerp(DL_SKY[0], DL_SKY[1], min(1.0, k / 12))); cr.fill()
    for layer, (base, amp_, col, step) in enumerate(((yb - 380, 420, (0.36, 0.20, 0.17), 520), (yb - 180, 300, DL_ROCK, 380))):
        k0, k1 = int((a - x0) // step) - 1, int((b - x0) // step) + 2
        pts = [(x0 + k0 * step, yb + 10)]
        for k in range(k0, k1 + 1):
            hh = amp_ * (0.45 + 0.55 * (((k * 7 + layer * 3) % 5) / 4))
            pts.append((x0 + k * step, base - hh)); pts.append((x0 + (k + 0.5) * step, base - hh * 0.35))
        pts.append((x0 + (k1 + 1) * step, yb + 10))
        sketch_poly(cr, pts, 5, sid=9830 + layer, fill=col, amp=0.3)
    if volcano: draw_volcano(cr, volcano[0], volcano[1], t, yb, w=volcano[2] if len(volcano) > 2 else 1800)
    if tower: draw_eye_tower(cr, tower["x"], tower["h"], t, yb, look=tower.get("look", 0.0), lid=tower.get("lid", 0.0),
                             water=tower.get("water", 0.0), look_y=tower.get("look_y", 0.0), flare=tower.get("flare", 1.0))
    if gate: draw_black_gate(cr, gate, t, yb)
    cr.rectangle(a, yb, b - a, max(200, vy1 - yb + 20)); cr.set_source_rgb(*DL_ASH); cr.fill()
    sketch_line(cr, [(a, yb), (b, yb)], 4, sid=9840, amp=1.0, alpha=0.9)
    for k in range(int((a - x0) // 430), int((b - x0) // 430) + 2):          # glowing cracks + rocks
        cx = x0 + k * 430 + 120 * math.sin(k * 2.3)
        cy = yb + 70 + (k * 37) % 140
        q = [(cx - 110, cy), (cx - 50, cy + 18), (cx, cy - 6), (cx + 60, cy + 14), (cx + 120, cy - 2)]
        path(cr, q); stroke_ink(cr, 14); path(cr, q); stroke_ink(cr, 7, lerp(LAVA, LAVA_B, 0.5 + 0.5 * math.sin(t * 2 + k)))
        if k % 3 == 0:
            rx = cx + 200
            sketch_poly(cr, [(rx - 60, yb + 2), (rx - 35, yb - 50), (rx + 20, yb - 62), (rx + 60, yb + 2)], 5, sid=9850 + k % 7, fill=DL_ROCK)
    if ash > 0.01:                                                             # ash drifting down
        for k in range(int((a - x0) // 140), int((b - x0) // 140) + 1):
            for j in range(3):
                fx = x0 + k * 140 + 60 * math.sin(t * 0.7 + k * 1.3 + j)
                fy = vy0 + ((t * 90 + k * 211 + j * 577) % max(1.0, (yb - vy0)))
                cr.rectangle(fx, fy, 10, 10); cr.set_source_rgba(0.55, 0.52, 0.50, 0.75 * ash); cr.fill()
    cr.restore()

def draw_lava_chamber(cr, t, edge, lava_y, yb=FLOOR_Y, x0=None, rise=0.0, glow=1.0):
    """inside the volcano: rock walls lit orange from below, a rock ledge (the floor) ending at x = edge, a sheer drop
    to a bubbling lava pool at lava_y (rise px lifts the lava). Fills everything visible."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    if x0 is not None: vx0 = max(vx0, x0)
    for k in range(int((vy1 - vy0) // 140) + 2):                              # wall: solid bands, hotter lower down
        y = vy0 + k * 140
        u = min(1.0, max(0.0, (y - (yb - 1600)) / (lava_y - (yb - 1600))))
        cr.rectangle(vx0, y, vx1 - vx0, 141); cr.set_source_rgb(*lerp((0.16, 0.08, 0.07), (0.62, 0.22, 0.08), u * glow)); cr.fill()
    for k in range(int((vx1 - vx0) // 380) + 2):                               # cracks in the far wall
        x = vx0 - (vx0 % 380) + k * 380
        q = [(x, yb - 1300 + 90 * (k % 3)), (x + 60, yb - 1100), (x + 10, yb - 900 + 40 * (k % 2)), (x + 80, yb - 700)]
        path(cr, q); stroke_ink(cr, 5, alpha=0.6)
    ly = lava_y - rise
    cr.rectangle(vx0, ly, vx1 - vx0, vy1 - ly + 10); cr.set_source_rgb(*LAVA); cr.fill()
    q = [(x, ly + 14 * math.sin(x / 120 + t * 2.2)) for x in range(int(vx0) - 60, int(vx1) + 80, 40)]
    path(cr, q + [(vx1 + 80, ly + 60), (vx0 - 60, ly + 60)]); cr.close_path(); cr.set_source_rgb(*LAVA); cr.fill()
    path(cr, q); stroke_ink(cr, 7)
    for k in range(int((vx1 - vx0) // 170) + 1):                               # bright swirls + bubbles
        x = vx0 + k * 170 + 50 * math.sin(t + k)
        y = ly + 70 + (k * 47) % 160
        sketch_ellipse(cr, x, y, 50, 12, 0.1, sid=9860 + k % 9, fill=LAVA_B, alpha=0.8)
        u = (t * 0.8 + k * 0.37) % 1.0
        if u < 0.5:
            r = 14 + 40 * u
            cr.arc(x + 40, ly + 6 - r * 0.4, r, math.pi, 2 * math.pi); cr.set_source_rgb(*LAVA_B); cr.fill_preserve(); stroke_ink(cr, 4)
    for k in range(6):                                                         # heat shimmer rising off the pool
        u = (t * 0.5 + k / 6) % 1.0
        x = edge + 150 + k * 140
        q = [(x + 18 * math.sin(i * 1.4 + t * 4), ly - 60 - u * 700 - i * 40) for i in range(6)]
        path(cr, q); cr.set_source_rgba(1.0, 0.85, 0.5, 0.35 * (1 - u)); cr.set_line_width(5); cr.stroke()
    ledge = [(vx0 - 50, yb), (edge, yb), (edge + 30, yb + 90), (edge - 15, yb + 230), (edge + 20, yb + 420),
             (edge - 40, yb + 640), (edge - 10, vy1 + 50), (vx0 - 50, vy1 + 50)]
    sketch_poly(cr, ledge, 7, sid=9870, fill=(0.20, 0.15, 0.14), amp=0.4)
    path(cr, [(edge + 30, yb + 90), (edge - 15, yb + 230), (edge + 20, yb + 420)]); stroke_ink(cr, 14, (0.85, 0.40, 0.12))
    sketch_line(cr, [(vx0 - 50, yb), (edge, yb)], 5, sid=9871, amp=1.0)


def draw_black_gate(cr, x, t=0.0, yb=FLOOR_Y, w=1500, h=1150, sign="ONE DOES NOT SIMPLY WALK INTO MORDOR"):
    """a huge black iron gate in a spiked wall between two jagged cliffs, a plank sign nailed on it. x = centre."""
    for sx in (-1, 1):                                                         # cliffs either side
        c0 = x + sx * w / 2
        pts = [(c0, yb), (c0, yb - h - 150), (c0 + sx * 260, yb - h - 600), (c0 + sx * 520, yb - h - 300),
               (c0 + sx * 800, yb - h - 750), (c0 + sx * 1300, yb - h - 200), (c0 + sx * 1500, yb)]
        sketch_poly(cr, pts, 7, sid=9900 + (sx > 0), fill=(0.20, 0.16, 0.16), amp=0.4)
    sketch_rect(cr, x - w / 2, yb - h, x + w / 2, yb, 7, sid=9902, fill=(0.13, 0.11, 0.12))
    for k in range(13):                                                        # spikes along the top
        sx0 = x - w / 2 + k * w / 12
        sketch_poly(cr, [(sx0 - 40, yb - h), (sx0, yb - h - 140), (sx0 + 40, yb - h)], 5, sid=9903 + k % 5, fill=(0.13, 0.11, 0.12))
    gw, gh = 520, 820                                                          # the gate doors
    sketch_rect(cr, x - gw, yb - gh, x + gw, yb, 7, sid=9910, fill=(0.22, 0.19, 0.20))
    sketch_line(cr, [(x, yb - gh), (x, yb)], 7, sid=9911)
    for row in range(5):
        for col in range(8):
            cr.arc(x - gw + 65 + col * (2 * gw - 130) / 7, yb - gh + 90 + row * 160, 14, 0, 2 * math.pi)
            cr.set_source_rgb(0.45, 0.42, 0.42); cr.fill_preserve(); stroke_ink(cr, 3)
    sw, sh = 760, 230                                                          # the plank sign
    cy = yb - gh - 60
    sketch_rect(cr, x - sw / 2, cy - sh / 2, x + sw / 2, cy + sh / 2, 6, sid=9912, fill=(0.80, 0.60, 0.36))
    draw_text(cr, sign, x, cy, 64, max_w=sw - 60)
    for sx in (-1, 1):
        cr.arc(x + sx * (sw / 2 - 26), cy, 9, 0, 2 * math.pi); fill_ink(cr)

EAGLE = (0.48, 0.32, 0.18)
EAGLE_D = (0.36, 0.23, 0.12)
def draw_eagle(cr, x, y, t=0.0, flap=1.0, s=1.0, face=1, look=0.0, alarm=0.0, grip=True):
    """a giant brown eagle seen from the side-ish, wings beating. (x, y) = where the talons grip (bottom).
    face 1 = facing right. alarm 0..1 = eyes wide + feathers puffed."""
    cr.save(); cr.translate(x, y); cr.scale(s * face, s)
    by = -330                                                                  # body centre above the talons
    ph = math.sin(t * 9.0) * flap
    for k, (dx, dy) in enumerate(((-30, 0), (30, 0))):                         # legs + talons
        sketch_line(cr, [(dx, by + 80), (dx * 1.4, -40), (dx * 1.2, 0)], 14, sid=9920 + k, color=(0.95, 0.75, 0.20))
        for c in (-1, 0, 1):
            sketch_line(cr, [(dx * 1.2, 0), (dx * 1.2 + c * 26, 30)], 9, sid=9922 + k * 3 + c)
    for side, shade in ((-1, EAGLE_D), (1, EAGLE)):                            # wings: far one darker
        tip_y = by - 360 * ph * side * 0.0 - 330 * ph
        pts = [(-60, by - 40), (-260, by - 120 - 200 * ph), (-560, tip_y - 60), (-760, tip_y + 40), (-560, tip_y + 90),
               (-620, tip_y + 150), (-420, by - 10 + 60 * ph), (-60, by + 60)]
        if side < 0: pts = [(px_ * 0.85 + 40, py_ - 40) for px_, py_ in pts]
        sketch_poly(cr, pts, 6, sid=9930 + (side > 0), fill=shade, amp=0.3)
    sketch_poly(cr, [(-140, by + 40), (-380, by + 140), (-360, by + 40), (-400, by - 20), (-140, by - 30)], 6, sid=9932, fill=EAGLE_D)
    sketch_ellipse(cr, 0, by, 210, 120 + 20 * alarm, 6, sid=9933, fill=EAGLE)
    sketch_circle(cr, 190, by - 120, 92 + 10 * alarm, 6, sid=9934, fill=(0.97, 0.96, 0.93))     # white head
    sketch_poly(cr, [(260, by - 150), (360, by - 120), (340, by - 70), (300, by - 90), (262, by - 95)], 5, sid=9935,
                fill=(0.98, 0.78, 0.18), amp=0.3)                              # hooked beak
    er = 22 + 14 * alarm
    cr.arc(215, by - 140, er, 0, 2 * math.pi); cr.set_source_rgb(1, 1, 1); cr.fill_preserve(); stroke_ink(cr, 4)
    cr.arc(215 + 8 * look, by - 140, er * 0.45, 0, 2 * math.pi); fill_ink(cr)
    sketch_line(cr, [(185, by - 175 + 10 * alarm), (250, by - 160 - 6 * alarm)], 7, sid=9936)  # stern brow
    cr.restore()

def draw_eagle_feather(cr_, x, y, ang, sid=0):
    cr_.save(); cr_.translate(x, y); cr_.rotate(ang)
    sketch_ellipse(cr_, 0, 0, 46, 14, 4, sid=sid, fill=EAGLE)
    cr_.restore()

def draw_beam(cr, src, tgt, width=320, alpha=1.0, locked=0.0):
    """the eye's searchlight: a cone from src to tgt (width at the target end). locked 0..1 = brighter, redder."""
    dx, dy = tgt[0] - src[0], tgt[1] - src[1]
    L_ = math.hypot(dx, dy) or 1.0; nx, ny = -dy / L_, dx / L_
    w = width / 2
    pts = [(src[0] + nx * 30, src[1] + ny * 30), (tgt[0] + nx * w, tgt[1] + ny * w), (tgt[0] - nx * w, tgt[1] - ny * w),
           (src[0] - nx * 30, src[1] - ny * 30)]
    col = lerp((1.0, 0.85, 0.35), (1.0, 0.45, 0.15), locked)
    cr.move_to(*pts[0])
    for p_ in pts[1:]: cr.line_to(*p_)
    cr.close_path(); cr.set_source_rgba(*col, (0.28 + 0.2 * locked) * alpha); cr.fill()
    for a, b in ((pts[0], pts[1]), (pts[3], pts[2])):
        cr.move_to(*a); cr.line_to(*b); cr.set_source_rgba(*col, 0.7 * alpha); cr.set_line_width(6); cr.stroke()
    sketch_ellipse(cr, tgt[0], tgt[1], w, w * 0.45, 0.1, sid=9940, fill=col, alpha=(0.25 + 0.25 * locked) * alpha)


# ---------------------------------------------------------------- cats (day 11): cats, a little cat shelter, a giant cat tower
CAT_COLS = dict(
    black=((0.17, 0.16, 0.18), (1.0, 0.82, 0.18)),          # (fur, eyes)
    orange=((0.96, 0.62, 0.26), (0.55, 0.80, 0.30)),
    grey=((0.64, 0.64, 0.68), (0.95, 0.80, 0.25)),
    white=((0.98, 0.97, 0.95), (0.40, 0.70, 0.95)),
    cream=((0.95, 0.86, 0.66), (0.55, 0.78, 0.35)),
    brown=((0.60, 0.44, 0.30), (0.95, 0.78, 0.22)),
)
CAT_KINDS = ("orange", "grey", "black", "white", "cream", "brown")
PINK = (0.96, 0.62, 0.66)

def _cat_ear(cr, a, b, c, fur, sid):
    sketch_poly(cr, [a, b, c], 4, sid=sid, fill=fur, amp=0.4)
    mx, my = (a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3
    q = [lerp(p_, (mx, my), 0.45) for p_ in (a, b, c)]
    cr.move_to(*q[0]); cr.line_to(*q[1]); cr.line_to(*q[2]); cr.close_path(); cr.set_source_rgb(*PINK); cr.fill()

def cat_face(cr, hx, hy, r, col="orange", look=(0.0, 0.0), blink=0.0, hiss=0.0, glow=0.0, sid=0, ears=True, stripes=None,
             eye_open=1.0):
    """a front-facing cat head centred (hx, hy), radius r: ears, slit-pupil eyes, pink nose, whiskers.
    blink 0..1 closes the eyes (slow blink), hiss 0..1 opens the mouth, glow 0..1 makes the eyes burn."""
    fur, eye = CAT_COLS.get(col, CAT_COLS["orange"])
    if ears:
        _cat_ear(cr, (hx - r * 0.95, hy - r * 0.35), (hx - r * 0.78, hy - r * 1.35), (hx - r * 0.2, hy - r * 0.85), fur, sid + 1)
        _cat_ear(cr, (hx + r * 0.2, hy - r * 0.85), (hx + r * 0.78, hy - r * 1.35), (hx + r * 0.95, hy - r * 0.35), fur, sid + 2)
    sketch_ellipse(cr, hx, hy, r * 1.08, r * 0.92, 4, sid=sid + 3, fill=fur)
    if stripes or col in ("orange", "brown", "grey"):
        for k in (-1, 0, 1):
            sketch_line(cr, [(hx + k * r * 0.22, hy - r * 0.9), (hx + k * r * 0.18, hy - r * 0.6)], max(2.0, r * 0.07), sid=sid + 4 + k,
                        color=lerp(fur, INK, 0.45))
    ink = (0.95, 0.93, 0.9) if col == "black" else INK
    ey = hy - r * 0.08
    for side in (-1, 1):
        ex = hx + side * r * 0.42
        cr.new_path(); rx, ry = r * 0.27, r * 0.31 * eye_open
        cr.save(); cr.translate(ex, ey); cr.scale(1.0, max(0.02, 1 - blink)); cr.arc(0, 0, rx, 0, 2 * math.pi); cr.restore()
        cr.set_source_rgb(*lerp(eye, (1.0, 0.95, 0.4), glow)); cr.fill_preserve(); stroke_ink(cr, max(2.0, r * 0.06))
        if blink < 0.85:
            px, py = ex + look[0] * rx * 0.35, ey + look[1] * ry * 0.3
            cr.save(); cr.translate(px, py); cr.scale(0.22 + 0.5 * hiss, (1 - blink) * 0.85); cr.arc(0, 0, ry, 0, 2 * math.pi); cr.restore()
            fill_ink(cr); cr.new_path()
            if glow > 0.05:
                cr.arc(ex, ey, rx * (1.5 + 0.3 * glow), 0, 2 * math.pi); cr.set_source_rgba(1.0, 0.7, 0.2, 0.25 * glow); cr.fill()
        else:
            sketch_line(cr, [(ex - rx, ey), (ex, ey + rx * 0.35), (ex + rx, ey)], max(2.0, r * 0.07), sid=sid + 8 + side, color=ink)
    nx, ny = hx, hy + r * 0.28
    cr.move_to(nx - r * 0.12, ny - r * 0.06); cr.line_to(nx + r * 0.12, ny - r * 0.06); cr.line_to(nx, ny + r * 0.08); cr.close_path()
    cr.set_source_rgb(*PINK); cr.fill()
    if hiss > 0.05:
        cr.save(); cr.translate(nx, ny + r * 0.32); cr.scale(1.0, 0.4 + 0.9 * hiss); cr.arc(0, 0, r * 0.26, 0, 2 * math.pi); cr.restore()
        cr.set_source_rgb(0.45, 0.08, 0.1); cr.fill_preserve(); stroke_ink(cr, max(2.0, r * 0.05))
        for side in (-1, 1):                                             # fangs
            cr.move_to(nx + side * r * 0.15, ny + r * 0.2); cr.line_to(nx + side * r * 0.09, ny + r * 0.36); cr.line_to(nx + side * r * 0.03, ny + r * 0.2)
            cr.close_path(); cr.set_source_rgb(1, 1, 1); cr.fill()
    else:
        sketch_line(cr, [(nx - r * 0.22, ny + r * 0.2), (nx - r * 0.1, ny + r * 0.26), (nx, ny + r * 0.1), (nx + r * 0.1, ny + r * 0.26),
                         (nx + r * 0.22, ny + r * 0.2)], max(2.0, r * 0.05), sid=sid + 12, color=ink, amp=0.4)
    for side in (-1, 1):
        for k in (-1, 0, 1):
            sketch_line(cr, [(hx + side * r * 0.45, ny + r * 0.05 + k * r * 0.1), (hx + side * r * 1.35, ny - r * 0.05 + k * r * 0.22)],
                        max(1.5, r * 0.035), sid=sid + 14 + k + 3 * (side > 0), color=ink, amp=0.4)

def _cat_tail(cr, pts, fur, w, sid, puff=0.0):
    w = w * (1 + 1.4 * puff)
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    path(cr, pts); stroke_ink(cr, w + 8); path(cr, pts); stroke_ink(cr, w, fur)

def draw_cat(cr, x, yb, s=1.0, t=0.0, kind="sit", col="orange", face=1, look=(0.0, 0.0), blink=0.0, phase=0.0, puff=0.0,
             hiss=0.0, glow=0.0, sid=0, swish=1.0, alpha=1.0, tilt=0.0):
    """a cartoon cat standing on (x, yb). kind: "sit" (front, tail curled), "loaf" (tucked in), "walk"/"run" (side view,
    facing `face` = +1 right / -1 left, legs cycling with `phase`), "puff" (side view, arched back, fur up, hissing),
    "fall" (spread out, mid-air). ~200 px tall sitting at s=1."""
    fur, _ = CAT_COLS.get(col, CAT_COLS["orange"])
    cr.save(); cr.translate(x, yb); cr.rotate(tilt); cr.scale(s, s)
    if alpha < 0.999: cr.push_group()
    sw = math.sin(t * 2.6 + sid) * swish
    if kind in ("sit", "loaf"):
        if kind == "sit":
            _cat_tail(cr, [(-30, -14), (-80, -18), (-102, -50), (-96 + 10 * sw, -100), (-80 + 22 * sw, -128)], fur, 16, sid)
            sketch_ellipse(cr, 0, -62, 54, 64, 4, sid=sid + 20, fill=fur)
            sketch_ellipse(cr, 0, -48, 26, 34, 0.1, sid=sid + 21, fill=lerp(fur, (1, 1, 1), 0.35))
            for side in (-1, 1): sketch_ellipse(cr, side * 20, -8, 18, 10, 4, sid=sid + 22 + (side > 0), fill=fur)
            cat_face(cr, 3, -146, 48, col, look, blink, hiss, glow, sid + 30)
        else:
            _cat_tail(cr, [(40, -10), (75, -6), (90, -20)], fur, 14, sid)
            sketch_ellipse(cr, 0, -40, 72, 42, 4, sid=sid + 20, fill=fur)
            cat_face(cr, -18, -88, 42, col, look, blink, hiss, glow, sid + 30)
    elif kind == "fall":
        for k, (ax, ay) in enumerate(((-60, -40), (60, -40), (-50, -110), (50, -110))):
            sketch_line(cr, [(0, -80), (ax * 1.2, ay - 10)], 14, sid=sid + 40 + k)
        _cat_tail(cr, [(0, -60), (-20, 10), (10, 40 + 10 * sw)], fur, 14, sid)
        sketch_ellipse(cr, 0, -80, 50, 56, 4, sid=sid + 20, fill=fur)
        cat_face(cr, 0, -150, 44, col, look, blink, hiss, glow, sid + 30)
    else:                                                                       # side view: walk / run / puff
        cr.scale(face, 1)
        run = 1.0 if kind == "run" else 0.0
        arch = puff
        by = -86 - 30 * arch - 8 * run * abs(math.sin(phase))
        amp = 26 + 30 * run
        for k, (lx, ph) in enumerate(((-52, 0.0), (48, math.pi), (-40, math.pi), (60, 0.0))):
            fx = lx + amp * math.sin(phase + ph) * (1 - arch); fy = -6 * max(0.0, math.cos(phase + ph)) * (1 + run)
            col_l = lerp(fur, INK, 0.25) if k < 2 else fur
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            path(cr, [(lx * 0.8, by + 10), (fx, fy - 6)]); stroke_ink(cr, 22); path(cr, [(lx * 0.8, by + 10), (fx, fy - 6)]); stroke_ink(cr, 14, col_l)
        tail_up = 1.0 - 0.6 * run
        _cat_tail(cr, [(-70, by - 4), (-112, by - 40 * tail_up - 10), (-120 + 10 * sw, by - 100 * tail_up), (-104 + 18 * sw, by - 140 * tail_up)],
                  fur, 16, sid, puff=puff)
        body = []
        for i in range(25):
            a = 2 * math.pi * i / 24
            rx, ry = 82, 42
            bx, byy = rx * math.cos(a), ry * math.sin(a) - (36 * arch * math.cos(a / 2) ** 8 if math.sin(a) < 0 else 0)
            if arch > 0.02 and math.sin(a) < 0:                                 # fur standing up on the back
                spike = 14 * arch * (1 if i % 2 else -0.3)
                bx, byy = bx * (1 + spike / 90), byy - spike
            body.append((bx, by + byy))
        sketch_poly(cr, body, 4, sid=sid + 20, fill=fur, amp=0.3)
        hx_, hy_ = 86, by - 34 - 10 * arch
        cr.save(); cr.translate(hx_, hy_); cr.scale(face, 1)            # face stays readable (un-mirror the face)
        cat_face(cr, 0, 0, 40, col, look=(0.5 * face + look[0], look[1]), blink=blink, hiss=hiss, glow=glow, sid=sid + 30)
        cr.restore()
    if alpha < 0.999: cr.pop_group_to_source(); cr.paint_with_alpha(alpha)
    cr.restore()

def draw_cat_shelter(cr, x, yb=FLOOR_Y, t=0.0, bulge=0.0, heads=0, s=1.0, sign="CAT SHELTER"):
    """a little stone cat shelter (built from a tower chunk): dark stone-block walls, a pitched roof, a round cat door,
    a plank sign on the roof. bulge 0..1 = over capacity (walls swell + wobble, cracks); heads = cat heads poking out."""
    w, hw, rh = 330 * s, 230 * s, 170 * s
    sx = 1 + bulge * (0.20 + 0.06 * math.sin(t * 31))
    sy = 1 + bulge * (0.10 + 0.04 * math.sin(t * 27 + 1))
    cr.save(); cr.translate(x, yb); cr.scale(sx, sy)
    stone = (0.24, 0.21, 0.22)
    sketch_rect(cr, -w / 2, -hw, w / 2, 0, 6, sid=9960, fill=stone)
    for row in range(4):                                                       # stone blocks
        yy = -hw + row * hw / 4
        sketch_line(cr, [(-w / 2, yy), (w / 2, yy)], 3, sid=9961 + row, color=(0.45, 0.42, 0.42))
        off = (row % 2) * w / 6
        for k in range(4):
            xx = -w / 2 + off + k * w / 3
            if -w / 2 < xx < w / 2: sketch_line(cr, [(xx, yy), (xx, yy + hw / 4)], 3, sid=9965 + k, color=(0.45, 0.42, 0.42))
    roof = [(-w / 2 - 40 * s, -hw + 4), (0, -hw - rh), (w / 2 + 40 * s, -hw + 4)]
    sketch_poly(cr, roof, 6, sid=9970, fill=(0.16, 0.13, 0.14))
    cr.move_to(-62 * s, 0); cr.line_to(-62 * s, -70 * s); cr.arc(0, -70 * s, 62 * s, math.pi, 2 * math.pi); cr.line_to(62 * s, 0); cr.close_path()
    cr.set_source_rgb(0.05, 0.04, 0.05); cr.fill_preserve(); stroke_ink(cr, 5)
    wx, wy = 105 * s, -150 * s                                                 # window
    sketch_rect(cr, wx - 38 * s, wy - 34 * s, wx + 38 * s, wy + 34 * s, 5, sid=9971, fill=(0.05, 0.04, 0.05))
    pw, ph = 290 * s, 60 * s                                                   # the plank sign on the roof
    py = -hw - rh * 0.42
    sketch_rect(cr, -pw / 2, py - ph / 2, pw / 2, py + ph / 2, 5, sid=9972, fill=(0.85, 0.66, 0.40))
    draw_text(cr, sign, 0, py, 30 * s, max_w=pw - 16)
    if bulge > 0.45:                                                           # cracks
        k = (bulge - 0.45) / 0.55
        for q in ([(-w / 2, -hw * 0.7), (-w / 2 + 60 * k, -hw * 0.6), (-w / 2 + 40 * k, -hw * 0.4), (-w / 2 + 110 * k, -hw * 0.3)],
                  [(w / 2, -hw * 0.3), (w / 2 - 70 * k, -hw * 0.45), (w / 2 - 50 * k, -hw * 0.65)],
                  [(-20, -hw - rh * 0.9), (10, -hw - rh * 0.7), (-15, -hw - rh * 0.55)]):
            sketch_line(cr, q, 4, sid=9975)
    spots = [(0, -40 * s, 34), (wx, wy, 26), (-90 * s, -hw - 40 * s, 30), (60 * s, -hw - 100 * s, 28), (-150 * s, -60 * s, 26),
             (150 * s, -40 * s, 26), (-40 * s, -hw - 140 * s, 26), (0, -150 * s, 0)]
    for i in range(min(heads, len(spots) - 1)):
        hx, hy, r = spots[i]
        bob = 6 * math.sin(t * 7 + i * 2.1)
        cat_face(cr, hx, hy + bob, r * s, CAT_KINDS[i % len(CAT_KINDS)], look=(0.3 * math.sin(t + i), 0.0), sid=9980 + i * 20)
    cr.restore()

def draw_hammer(cr, x, y, s=1.0, ang=0.0):
    """a cartoon claw hammer; (x, y) = where the hand grips the handle."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_rect(cr, -11, -150, 11, 40, 5, sid=9990, fill=(0.80, 0.60, 0.36))
    sketch_poly(cr, [(-70, -190), (52, -190), (52, -138), (-30, -138), (-70, -150)], 5, sid=9991, fill=(0.55, 0.57, 0.62))
    sketch_poly(cr, [(52, -186), (96, -210), (82, -168), (52, -150)], 4, sid=9992, fill=(0.55, 0.57, 0.62))
    cr.restore()

# the giant cat tower: platform tops (dx, dy from the base, half width) - cats sit on these
CAT_TOWER_PLATFORMS = [(-250, -380, 150), (240, -560, 150), (-240, -790, 140), (230, -990, 130), (0, -1190, 120),
                       (-470, -1090, 110), (0, -120, 300)]
CAT_TOWER_LEDGE = (-470, -1090)            # the small high ledge on the left where the burnt-out eyeball sits

def cat_tower_spots(x, yb=FLOOR_Y):
    """(world x, world y) seats for cats, filled in order (the top seat between the horns is index 0 ... kept for the kitten)."""
    out = [(x, yb - 1190)]
    for dx, dy, hw in CAT_TOWER_PLATFORMS[:4]:
        n = 3 if hw >= 140 else 2
        for k in range(n):
            out.append((x + dx + (k - (n - 1) / 2) * hw * 0.62, yb + dy))
    for k in range(6): out.append((x - 250 + k * 100, yb - 120))
    return out

def draw_cat_tower(cr, x, yb=FLOOR_Y, t=0.0, sign="CAT SHELTER", hammer=True):
    """the old eye tower rebuilt as a giant cat tree: rope-wrapped scratching trunk, carpeted platforms on posts, cubby
    boxes with round holes, dangling toy mice, the two black horns on top with a cushion between them, a sign at the base."""
    rope, rope_d = (0.88, 0.76, 0.56), (0.66, 0.52, 0.34)
    carpet, carpet_d = (0.56, 0.50, 0.64), (0.42, 0.37, 0.50)
    top = yb - 1190
    for sx in (-1, 1):                                                         # the old horns, now holding the top cushion
        horn = [(x + sx * 90, top + 20), (x + sx * 150, top - 60), (x + sx * 120, top - 260), (x + sx * 200, top - 70), (x + sx * 170, top + 30)]
        sketch_poly(cr, horn, 6, sid=9811 + (sx > 0), fill=(0.12, 0.10, 0.11), amp=0.3)
    tw = 70
    sketch_rect(cr, x - tw, top + 20, x + tw, yb - 120, 6, sid=10000, fill=rope)  # rope-wrapped trunk
    yy = top + 40
    while yy < yb - 130:
        sketch_line(cr, [(x - tw + 4, yy + 16), (x + tw - 4, yy)], 4, sid=10001 + int(yy) % 7, color=rope_d, amp=0.6)
        yy += 30
    for i, (dx, dy, hw) in enumerate(CAT_TOWER_PLATFORMS[:4] + [CAT_TOWER_PLATFORMS[5]]):
        px, py = x + dx, yb + dy
        if abs(dx) > tw:                                                       # arm from the trunk to the platform
            sx = 1 if dx > 0 else -1
            sketch_rect(cr, min(x, px), py + 34, max(x, px), py + 62, 5, sid=10010 + i, fill=rope_d)
        sketch_rect(cr, px - 26, py + 40, px + 26, py + 220 if i < 4 else py + 120, 5, sid=10020 + i, fill=rope)   # post
        sketch_rect(cr, px - hw, py, px + hw, py + 40, 6, sid=10030 + i, fill=carpet)
        sketch_line(cr, [(px - hw + 8, py + 8), (px + hw - 8, py + 8)], 3, sid=10040 + i, color=carpet_d)
        if i in (0, 3):                                                        # dangling toy mouse
            mx = px + (hw - 20) * (1 if dx > 0 else -1); sw = 0.35 * math.sin(t * 2.2 + i)
            ex, ey = mx + 120 * math.sin(sw), py + 40 + 120 * math.cos(sw)
            sketch_line(cr, [(mx, py + 40), (ex, ey)], 3, sid=10050 + i)
            sketch_ellipse(cr, ex, ey + 18, 16, 22, 3, sid=10055 + i, fill=(0.72, 0.72, 0.76))
    for i, (bx, by, bw, bh) in enumerate(((x + 170, yb - 120, 200, 170), (x - 330, yb - 560, 180, 150))):   # cubby boxes
        sketch_rect(cr, bx - bw / 2, by - bh, bx + bw / 2, by, 6, sid=10060 + i, fill=carpet)
        sketch_circle(cr, bx, by - bh / 2, bh * 0.3, 5, sid=10062 + i, fill=(0.08, 0.06, 0.08))
    sketch_ellipse(cr, x, top + 6, 140, 34, 6, sid=10070, fill=(0.85, 0.30, 0.30))   # top cushion
    if hammer:                                                                 # the hammer, stuck in the trunk
        draw_hammer(cr, x + 60, yb - 330, s=0.9, ang=1.9)
    bw, bh = 600, 120                                                          # carpeted base + the sign
    sketch_rect(cr, x - bw / 2, yb - bh, x + bw / 2, yb, 6, sid=10080, fill=carpet_d)
    sketch_rect(cr, x - 230, yb - 112, x + 230, yb - 16, 5, sid=10081, fill=(0.85, 0.66, 0.40))
    draw_text(cr, sign, x, yb - 64, 62, max_w=430)


# ---------------------------------------------------------------- the sunny town + the CAT RESCUE SHELTER (day 11 re-cut)
TOWN_SKY = ((0.80, 0.91, 0.99), (0.52, 0.76, 0.96))
TOWN_GRASS = (0.62, 0.82, 0.45)
WALK = (0.86, 0.85, 0.82)
SHELTER_WALL = (0.99, 0.93, 0.80)
SHELTER_ROOF = (0.80, 0.36, 0.30)
SHELTER_DOOR = (0.38, 0.62, 0.46)

def _house(cr, x, yb, w, h, col, sid):
    sketch_rect(cr, x - w / 2, yb - h, x + w / 2, yb, 5, sid=sid, fill=col)
    sketch_poly(cr, [(x - w / 2 - 30, yb - h + 4), (x, yb - h - w * 0.45), (x + w / 2 + 30, yb - h + 4)], 5, sid=sid + 1, fill=(0.72, 0.42, 0.36))
    for k in (-1, 1):
        sketch_rect(cr, x + k * w * 0.22 - 34, yb - h * 0.7, x + k * w * 0.22 + 34, yb - h * 0.7 + 64, 4, sid=sid + 2 + k, fill=(0.90, 0.96, 1.0))
    sketch_rect(cr, x - 36, yb - 130, x + 36, yb, 4, sid=sid + 5, fill=(0.60, 0.44, 0.32))

def draw_town_world(cr, t, x0=33400, x1=60000, yb=FLOOR_Y):
    """a sunny little town right of x0: soft blue sky (solid bands), sun, clouds, green hills, pastel houses, grass and a
    pale sidewalk as the floor. Nothing drawn left of x0."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    a, b = max(x0, vx0), min(x1, vx1)
    if b <= a: return
    cr.save(); cr.rectangle(x0, vy0 - 10, x1 - x0, vy1 - vy0 + 20); cr.clip()
    top = min(vy0, yb - 200)
    for k in range(30):
        y_hi = yb - 300 - (k + 1) * 120; y_lo = yb - 300 - k * 120 if k else yb + 10
        if k == 29: y_hi = min(y_hi, top - 10)
        cr.rectangle(a, y_hi, b - a, y_lo - y_hi + 1); cr.set_source_rgb(*lerp(TOWN_SKY[0], TOWN_SKY[1], min(1.0, k / 12))); cr.fill()
    sx = x0 + 2600
    if a - 400 < sx < b + 400:
        sketch_circle(cr, sx, yb - 1500, 120, 6, sid=10100, fill=(1.0, 0.86, 0.35))
    for k in range(int((a - x0) // 900) - 1, int((b - x0) // 900) + 2):
        draw_cloud(cr, x0 + k * 900 + 200 + 30 * math.sin(t * 0.2 + k), yb - 1250 - 160 * (k % 3), s=0.9 + 0.2 * (k % 2))
    step = 520
    k0, k1 = int((a - x0) // step) - 1, int((b - x0) // step) + 2
    pts = [(x0 + k0 * step, yb + 10)]
    for k in range(k0, k1 + 1):
        pts.append((x0 + k * step, yb - 330 - 90 * ((k * 3) % 4) / 3)); pts.append((x0 + (k + 0.5) * step, yb - 300))
    pts.append((x0 + (k1 + 1) * step, yb + 10))
    sketch_poly(cr, pts, 5, sid=10101, fill=(0.70, 0.86, 0.55), amp=0.3)
    cols = ((0.98, 0.84, 0.80), (0.82, 0.90, 0.98), (0.99, 0.95, 0.76), (0.86, 0.94, 0.84))
    for k in range(int((a - x0) // 1300) - 1, int((b - x0) // 1300) + 2):
        hx = x0 + 650 + k * 1300
        if k % 3 == 1: continue                                           # gaps between houses
        _house(cr, hx, yb - 120, 420, 360, cols[k % 4], 10110 + (k % 5) * 6)
    cr.rectangle(a, yb - 120, b - a, 120); cr.set_source_rgb(*TOWN_GRASS); cr.fill()
    sketch_line(cr, [(a, yb - 120), (b, yb - 120)], 4, sid=10140, amp=1.0)
    cr.rectangle(a, yb, b - a, max(200, vy1 - yb + 20)); cr.set_source_rgb(*WALK); cr.fill()
    sketch_line(cr, [(a, yb), (b, yb)], 4, sid=10141, amp=1.0)
    for k in range(int((a - x0) // 260), int((b - x0) // 260) + 2):          # paving joints
        xx = x0 + k * 260
        sketch_line(cr, [(xx, yb + 4), (xx - 60, yb + 300)], 3, sid=10142, color=(0.70, 0.69, 0.66))
    cr.restore()

def draw_tree(cr, x, yb=FLOOR_Y, t=0.0, h=900, sid=10200):
    """a big round leafy cartoon tree with one long branch to the right (a cat can sit on it at branch_tip)."""
    sketch_poly(cr, [(x - 60, yb), (x - 40, yb - h * 0.6), (x + 40, yb - h * 0.6), (x + 60, yb)], 6, sid=sid, fill=(0.62, 0.44, 0.30))
    sketch_poly(cr, [(x + 20, yb - h * 0.45), (x + 300, yb - h * 0.62), (x + 300, yb - h * 0.58), (x + 30, yb - h * 0.37)], 5,
                sid=sid + 1, fill=(0.62, 0.44, 0.30))
    for k, (dx, dy, r) in enumerate(((-150, -0.78, 200), (130, -0.82, 210), (0, -0.98, 230), (-60, -0.70, 170), (90, -0.68, 160))):
        sketch_circle(cr, x + dx + 6 * math.sin(t * 1.3 + k), yb + h * dy, r, 6, sid=sid + 2 + k, fill=(0.46, 0.72, 0.36))

def tree_branch_tip(x, yb=FLOOR_Y, h=900): return (x + 270, yb - h * 0.61)

def draw_box(cr, x, yb=FLOOR_Y, s=1.0, label=None, flaps=1.0, sid=10300):
    """an open cardboard box (bottom centre (x, yb)); label = marker text on the front."""
    w, h = 230 * s, 150 * s
    for sx in (-1, 1):                                                         # open flaps
        sketch_poly(cr, [(x + sx * w / 2, yb - h), (x + sx * (w / 2 + 60 * s * flaps), yb - h - 50 * s * flaps), (x + sx * (w / 2 - 20 * s), yb - h - 60 * s * flaps),
                         (x + sx * (w / 2 - 60 * s), yb - h)], 4, sid=sid + (sx > 0), fill=(0.80, 0.62, 0.40))
    sketch_rect(cr, x - w / 2, yb - h, x + w / 2, yb, 5, sid=sid + 2, fill=(0.86, 0.68, 0.45))
    if label: draw_text(cr, label, x, yb - h / 2, 34 * s, max_w=w - 16)

def draw_mug(cr, x, y, s=1.0, ang=0.0):
    """a coffee mug, bottom centre (x, y)."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_circle(cr, 40, -45, 22, 6, sid=10310, fill=None)
    sketch_rect(cr, -40, -90, 40, 0, 5, sid=10311, fill=(0.40, 0.66, 0.85))
    cr.restore()

def draw_cat_bed(cr, x, yb=FLOOR_Y, s=1.0):
    """a fancy round cushion cat bed (purple velvet, gold trim) - the one no cat will use."""
    sketch_ellipse(cr, x, yb - 50 * s, 170 * s, 60 * s, 6, sid=10320, fill=(0.62, 0.42, 0.72))
    sketch_ellipse(cr, x, yb - 64 * s, 120 * s, 32 * s, 5, sid=10321, fill=(0.74, 0.56, 0.82))
    sketch_line(cr, [(x - 160 * s, yb - 40 * s), (x + 160 * s, yb - 40 * s)], 4, sid=10322, color=(0.92, 0.74, 0.25))

def draw_rescue_shelter(cr, x, yb=FLOOR_Y, t=0.0, door=0.0, window_cats=3, banner=None, s=1.0):
    """the CAT RESCUE SHELTER: a cosy two-storey building, cream walls, red roof, a big sign, flower boxes, two
    windows with cats in them, a green door with a paw print. door 0..1 opens it. banner = a hanging banner text."""
    w, h = 1000 * s, 780 * s
    sketch_rect(cr, x - w / 2, yb - h, x + w / 2, yb, 7, sid=10400, fill=SHELTER_WALL)
    sketch_poly(cr, [(x - w / 2 - 60, yb - h + 6), (x - w / 2 + 40, yb - h - 170 * s), (x + w / 2 - 40, yb - h - 170 * s),
                     (x + w / 2 + 60, yb - h + 6)], 7, sid=10401, fill=SHELTER_ROOF)
    sw, sh = 820 * s, 140 * s                                                    # the sign
    sy = yb - h + 20 * s
    sketch_rect(cr, x - sw / 2, sy, x + sw / 2, sy + sh, 6, sid=10402, fill=(1.0, 1.0, 0.98))
    draw_text(cr, "CAT RESCUE SHELTER", x, sy + sh / 2, 60 * s, max_w=sw - 20, color=(170, 50, 40))
    for k, wx in enumerate((x - 300 * s, x + 300 * s)):                       # windows with cats in them
        wy0, wy1 = yb - h + 230 * s, yb - h + 470 * s
        sketch_rect(cr, wx - 130 * s, wy0, wx + 130 * s, wy1, 6, sid=10403 + k, fill=(0.86, 0.94, 1.0))
        sketch_line(cr, [(wx, wy0), (wx, wy1)], 4, sid=10405 + k)
        n = max(0, min(2, window_cats - 2 * k))
        for j in range(n):
            cat_face(cr, wx - 60 * s + j * 120 * s, wy1 - 50 * s + 6 * math.sin(t * 2 + j + k), 42 * s, CAT_KINDS[(k * 2 + j) % 6], sid=10410 + 20 * (k * 2 + j))
        sketch_rect(cr, wx - 150 * s, wy1, wx + 150 * s, wy1 + 50 * s, 5, sid=10407 + k, fill=(0.66, 0.46, 0.32))  # flower box
        for f in range(5):
            fx = wx - 120 * s + f * 60 * s
            sketch_circle(cr, fx, wy1 - 6, 18 * s, 4, sid=10450 + f, fill=((0.96, 0.45, 0.55), (1.0, 0.82, 0.3), (0.75, 0.55, 0.9))[f % 3])
    dw, dh = 220 * s, 330 * s                                                    # the door
    cr.rectangle(x - dw / 2, yb - dh, dw, dh); cr.set_source_rgb(0.98, 0.86, 0.60); cr.fill()
    if door < 0.98:
        ow = dw * (1 - door)
        sketch_rect(cr, x - dw / 2, yb - dh, x - dw / 2 + ow, yb, 6, sid=10460, fill=SHELTER_DOOR)
        if ow > 60:
            px, py = x - dw / 2 + ow / 2, yb - dh * 0.55                       # paw print
            sketch_circle(cr, px, py, 26 * s * ow / dw, 3, sid=10461, fill=(1, 1, 1))
            for j, (ax, ay) in enumerate(((-30, -36), (-10, -50), (12, -50), (32, -36))):
                sketch_circle(cr, px + ax * s * ow / dw, py + ay * s, 9 * s * ow / dw, 3, sid=10462 + j, fill=(1, 1, 1))
    sketch_rect(cr, x - dw / 2, yb - dh, x + dw / 2, yb, 6, sid=10466, fill=None)
    if banner:
        bw = 700 * s; by = yb - h - 240 * s
        sketch_line(cr, [(x - bw / 2 - 40, by - 30), (x + bw / 2 + 40, by - 30)], 4, sid=10470)
        sketch_poly(cr, [(x - bw / 2, by - 30), (x + bw / 2, by - 30), (x + bw / 2 - 30, by + 90), (x - bw / 2 + 30, by + 90)], 5,
                    sid=10471, fill=(1.0, 0.85, 0.40))
        draw_text(cr, banner, x, by + 30, 62 * s, max_w=bw - 80, color=(170, 50, 40))

INTERIOR_WALL = (0.99, 0.94, 0.86)
def draw_shelter_inside(cr, t, x0, x1, yb=FLOOR_Y):
    """inside the shelter: cream walls with a wainscot, a sunny window, a warm wood floor. (Furniture drawn by the episode.)"""
    vx0, vy0, vx1, vy1 = _visible(cr)
    a, b = max(x0, vx0), min(x1, vx1)
    cr.rectangle(a, vy0 - 10, b - a, yb - vy0 + 10); cr.set_source_rgb(*INTERIOR_WALL); cr.fill()
    cr.rectangle(a, yb - 300, b - a, 300); cr.set_source_rgb(0.92, 0.80, 0.66); cr.fill()
    sketch_line(cr, [(a, yb - 300), (b, yb - 300)], 4, sid=10500)
    for k in range(int((a - x0) // 120), int((b - x0) // 120) + 2):
        sketch_line(cr, [(x0 + k * 120, yb - 296), (x0 + k * 120, yb)], 2, sid=10501, color=(0.80, 0.66, 0.52))
    cr.rectangle(a, yb, b - a, max(200, vy1 - yb + 20)); cr.set_source_rgb(0.80, 0.62, 0.42); cr.fill()
    sketch_line(cr, [(a, yb), (b, yb)], 5, sid=10502)
    for k in range(int((a - x0) // 340), int((b - x0) // 340) + 2):
        sketch_line(cr, [(x0 + k * 340, yb + 4), (x0 + k * 340 - 50, yb + 400)], 3, sid=10503, color=(0.66, 0.48, 0.32))

def draw_cat_photo(cr, x, y, col, stamp=0.0, s=1.0, sid=10600):
    """a polaroid of a cat pinned to the board; stamp 0..1 slams a red ADOPTED stamp across it."""
    w, h = 150 * s, 170 * s
    sketch_rect(cr, x - w / 2, y - h / 2, x + w / 2, y + h / 2, 4, sid=sid, fill=(1, 1, 1))
    cr.rectangle(x - w / 2 + 12, y - h / 2 + 12, w - 24, h - 50); cr.set_source_rgb(0.86, 0.94, 1.0); cr.fill()
    cr.save(); cr.rectangle(x - w / 2 + 12, y - h / 2 + 12, w - 24, h - 50); cr.clip()
    cat_face(cr, x, y - 14 * s, 40 * s, col, sid=sid + 2)
    cr.restore()
    cr.arc(x, y - h / 2 + 4, 8, 0, 2 * math.pi); cr.set_source_rgb(0.9, 0.25, 0.25); cr.fill()
    if stamp > 0.01:
        k = 1.0 + 0.6 * (1 - min(1.0, stamp))
        cr.save(); cr.translate(x, y + 10); cr.rotate(-0.25); cr.scale(k, k)
        cr.rectangle(-82 * s, -24 * s, 164 * s, 48 * s); cr.set_source_rgba(0.85, 0.15, 0.15, 0.9 * min(1.0, stamp * 2)); cr.set_line_width(5); cr.stroke()
        draw_text(cr, "ADOPTED", 0, 0, 34 * s, color=(215, 40, 40), alpha=min(1.0, stamp * 2))
        cr.restore()

def draw_stamp(cr, x, y, s=1.0):
    """a rubber stamp; (x, y) = bottom of the stamp face."""
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    sketch_rect(cr, -42, -34, 42, 0, 4, sid=10620, fill=(0.85, 0.20, 0.20))
    sketch_rect(cr, -14, -90, 14, -34, 4, sid=10621, fill=(0.62, 0.44, 0.30))
    sketch_circle(cr, 0, -108, 26, 4, sid=10622, fill=(0.62, 0.44, 0.30))
    cr.restore()

# ============================================================ FUN PARK (day 12: theme park right of the town)
PARK_PINK = (0.97, 0.62, 0.72)
PARK_TEAL = (0.42, 0.80, 0.78)
PARK_YEL = (1.0, 0.84, 0.32)
PARK_RED = (0.90, 0.30, 0.28)
PARK_PURP = (0.68, 0.52, 0.86)
PARK_PLAZA = (0.93, 0.88, 0.80)
BALLOON_COLS = (PARK_RED, PARK_YEL, PARK_TEAL, PARK_PINK, PARK_PURP, (0.45, 0.65, 0.95))

def draw_park_world(cr, t, x0=38550, x1=70000, yb=FLOOR_Y, grid_x0=33400):
    """the FUN PARK, right of x0: the same sky + clouds + paving grid as the town (so the seam can be hidden behind the
    gate), soft purple hills, a hedge strip, bunting, and a warm plaza floor. Rides are drawn by the episode."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    a, b = max(x0, vx0), min(x1, vx1)
    if b <= a: return
    cr.save(); cr.rectangle(x0, vy0 - 10, x1 - x0, vy1 - vy0 + 20); cr.clip()
    top = min(vy0, yb - 200)
    for k in range(40):
        y_hi = yb - 300 - (k + 1) * 120; y_lo = yb - 300 - k * 120 if k else yb + 10
        if k == 39: y_hi = min(y_hi, top - 10)
        cr.rectangle(a, y_hi, b - a, y_lo - y_hi + 1); cr.set_source_rgb(*lerp(TOWN_SKY[0], TOWN_SKY[1], min(1.0, k / 12))); cr.fill()
    for k in range(int((a - grid_x0) // 900) - 1, int((b - grid_x0) // 900) + 2):
        draw_cloud(cr, grid_x0 + k * 900 + 200 + 30 * math.sin(t * 0.2 + k), yb - 1250 - 160 * (k % 3), s=0.9 + 0.2 * (k % 2))
    step = 520                                                                  # the town's hills, continued (same grid)
    k0, k1 = int((a - grid_x0) // step) - 1, int((b - grid_x0) // step) + 2
    pts = [(grid_x0 + k0 * step, yb + 10)]
    for k in range(k0, k1 + 1):
        pts.append((grid_x0 + k * step, yb - 330 - 90 * ((k * 3) % 4) / 3)); pts.append((grid_x0 + (k + 0.5) * step, yb - 300))
    pts.append((grid_x0 + (k1 + 1) * step, yb + 10))
    sketch_poly(cr, pts, 5, sid=10101, fill=(0.70, 0.86, 0.55), amp=0.3)
    cr.rectangle(a, yb - 120, b - a, 120); cr.set_source_rgb(*TOWN_GRASS); cr.fill()
    for k in range(int((a - x0) // 150) - 1, int((b - x0) // 150) + 2):       # hedge bumps
        sketch_circle(cr, x0 + k * 150 + 75, yb - 120, 80, 4, sid=12110 + (k % 4), fill=(0.46, 0.70, 0.36))
    cr.rectangle(a, yb, b - a, max(200, vy1 - yb + 20)); cr.set_source_rgb(*WALK); cr.fill()
    sketch_line(cr, [(a, yb), (b, yb)], 4, sid=10141, amp=1.0)
    for k in range(int((a - grid_x0) // 260), int((b - grid_x0) // 260) + 2):   # same paving joints as the town
        xx = grid_x0 + k * 260
        sketch_line(cr, [(xx, yb + 4), (xx - 60, yb + 300)], 3, sid=10142, color=(0.70, 0.69, 0.66))
    cr.restore()

def draw_balloon(cr, x, y, r=46, col=PARK_RED, string=160, t=0.0, sid=12200):
    bx = x + 6 * math.sin(t * 1.7 + sid)
    sketch_line(cr, [(bx, y + r * 1.15), (x + 10 * math.sin(t * 1.3 + sid), y + r + string)], 2.5, sid=sid + 1)
    sketch_ellipse(cr, bx, y, r * 0.86, r, 4, sid=sid, fill=col)
    cr.arc(bx - r * 0.3, y - r * 0.35, r * 0.16, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.8); cr.fill()

def draw_balloon_bunch(cr, x, y, t=0.0, n=7, sid=12300):
    for i in range(n):
        a = i * 2.4
        draw_balloon(cr, x + 70 * math.cos(a) * (i / n + 0.3), y - 80 * math.sin(a) * (i / n + 0.3) - 40 * (i % 3),
                     r=48 + 6 * (i % 2), col=BALLOON_COLS[i % 6], string=200 + 30 * (i % 3), t=t, sid=sid + 7 * i)

def draw_park_gate(cr, x, yb=FLOOR_Y, t=0.0, sign="FUN PARK"):
    """the entrance: two striped towers, an arch with the sign, balloon bunches, and tall hedges both sides (they hide
    the town/park seam behind them)."""
    for k, dx in enumerate((-1, 1)):                                            # tall hedges
        for j in range(6):
            hx = x + dx * (520 + 120 * j)
            sketch_circle(cr, hx, yb - 260 - 40 * (j % 2), 190, 5, sid=12400 + 10 * k + j, fill=(0.40, 0.64, 0.32))
        sketch_rect(cr, x + dx * 470 - (0 if dx > 0 else 760), yb - 320, x + dx * 470 + (760 if dx > 0 else 0), yb, 5, sid=12420 + k,
                    fill=(0.40, 0.64, 0.32))
    for k, dx in enumerate((-1, 1)):                                            # towers
        tx = x + dx * 380
        sketch_rect(cr, tx - 90, yb - 1250, tx + 90, yb, 6, sid=12430 + k, fill=(1.0, 0.97, 0.92))
        for j in range(8):
            y0 = yb - 1250 + j * 156
            if j % 2 == 0:
                cr.rectangle(tx - 87, y0 + 3, 174, 78); cr.set_source_rgb(*PARK_RED); cr.fill()
        sketch_rect(cr, tx - 90, yb - 1250, tx + 90, yb, 6, sid=12432 + k, fill=None)
        sketch_poly(cr, [(tx - 130, yb - 1250), (tx, yb - 1480), (tx + 130, yb - 1250)], 6, sid=12434 + k, fill=PARK_TEAL)
        sketch_line(cr, [(tx, yb - 1480), (tx, yb - 1580)], 4, sid=12436 + k)
        sketch_poly(cr, [(tx, yb - 1580), (tx + 70 * (1 + 0.2 * math.sin(t * 4 + k)), yb - 1555), (tx, yb - 1530)], 3, sid=12438 + k, fill=PARK_YEL)
        draw_balloon_bunch(cr, tx + dx * 200, yb - 900, t, sid=12500 + 60 * k)
    ay = yb - 1080                                                              # the arch + sign
    sketch_poly(cr, [(x - 300, ay + 60), (x - 280, ay - 90), (x, ay - 200), (x + 280, ay - 90), (x + 300, ay + 60), (x, ay - 50)], 6,
                sid=12440, fill=PARK_YEL)
    sketch_rect(cr, x - 330, ay - 120, x + 330, ay + 70, 6, sid=12441, fill=(1.0, 1.0, 0.98))
    draw_text(cr, sign, x, ay - 25, 104, color=(200, 50, 60), max_w=620)
    for i in range(9):                                                          # light bulbs
        bx = x - 300 + i * 75
        on = (int(t * 6) + i) % 2
        cr.arc(bx, ay + 52, 11, 0, 2 * math.pi); cr.set_source_rgb(*(PARK_YEL if on else (1, 1, 0.9))); cr.fill_preserve(); stroke_ink(cr, 3)

def draw_bunting(cr, xa, xb, y, sag=80, n=None, sid=12600):
    n = n or max(3, int((xb - xa) // 90))
    pts = [(lerp(xa, xb, i / 20), y + sag * 4 * (i / 20) * (1 - i / 20)) for i in range(21)]
    sketch_line(cr, pts, 3, sid=sid)
    for i in range(n):
        u = (i + 0.5) / n; px, py = lerp(xa, xb, u), y + sag * 4 * u * (1 - u)
        sketch_poly(cr, [(px - 30, py), (px + 30, py), (px, py + 60)], 3, sid=sid + 1 + i % 5, fill=BALLOON_COLS[i % 6], amp=0.5)

def draw_ferris_wheel(cr, x, yb=FLOOR_Y, R=700, t=0.0, spin=0.12):
    """a big ferris wheel behind everything; it turns slowly."""
    hy = yb - R - 220
    for dx in (-1, 1):
        sketch_line(cr, [(x, hy), (x + dx * R * 0.55, yb)], 14, sid=12700 + (dx > 0))
    sketch_circle(cr, x, hy, R, 9, sid=12702, fill=None)
    sketch_circle(cr, x, hy, R * 0.92, 4, sid=12703, fill=None)
    n = 10
    for i in range(n):
        a = t * spin + i * 2 * math.pi / n
        sketch_line(cr, [(x, hy), (x + R * math.cos(a), hy + R * math.sin(a))], 4, sid=12704 + i)
    for i in range(n):
        a = t * spin + i * 2 * math.pi / n
        gx, gy = x + R * math.cos(a), hy + R * math.sin(a)
        sketch_line(cr, [(gx, gy), (gx, gy + 40)], 4, sid=12720 + i)
        sketch_rect(cr, gx - 60, gy + 40, gx + 60, gy + 130, 5, sid=12730 + i, fill=BALLOON_COLS[i % 6])
    sketch_circle(cr, x, hy, 60, 6, sid=12750, fill=PARK_YEL)

def draw_teacup(cr, x, yb, s=1.0, col=PARK_PINK, part="whole", ph=0.0, sid=12800):
    """a giant spinning teacup ride car, bottom centre (x, yb). part 'back' = the inside rim, 'front' = the bowl (covers
    a rider from the chest down). ph = spin phase (the dots slide round)."""
    w, h = 520 * s, 330 * s
    if part in ("back", "whole"):
        sketch_ellipse(cr, x, yb - h, w / 2, 70 * s, 6, sid=sid, fill=lerp(col, (0.3, 0.2, 0.25), 0.35))
    if part in ("front", "whole"):
        pts = [(x - w / 2, yb - h)]
        for i in range(21):
            a = math.pi * i / 20
            pts.append((x - w / 2 * math.cos(a), yb - h + 10 * s + (h - 40 * s) * math.sin(a) ** 0.6))
        pts.append((x + w / 2, yb - h))
        for i in range(21):
            a = math.pi * i / 20
            pts.append((x + w / 2 * math.cos(a), yb - h + 70 * s * math.sin(a)))
        sketch_poly(cr, pts, 6, sid=sid + 1, fill=col, amp=0.5)
        cr.save()
        cr.new_path(); [cr.line_to(*p_) for p_ in pts]; cr.close_path(); cr.clip()
        for i in range(6):                                                    # polka dots sliding round
            a = ph + i * math.pi / 3
            c = math.cos(a)
            if math.sin(a) < 0: continue
            sketch_circle(cr, x + w * 0.42 * c, yb - h * 0.45 + 20 * s * (1 - abs(c)), 34 * s * (0.4 + 0.6 * math.sin(a)), 3, sid=sid + 3 + i,
                          fill=(1.0, 0.97, 0.9))
        cr.restore()
        sketch_rect(cr, x - 70 * s, yb - 30 * s, x + 70 * s, yb, 4, sid=sid + 10, fill=lerp(col, (0.3, 0.2, 0.25), 0.3))
        sketch_ellipse(cr, x + w / 2 + 40 * s, yb - h * 0.55, 60 * s, 80 * s, 10 * s, sid=sid + 11, fill=None)   # handle

def draw_cup_wheel(cr, x, y, s=1.0, ang=0.0, sid=12850):
    """the spin wheel in the middle of a teacup (seen a little from above), on a post."""
    sketch_rect(cr, x - 12 * s, y, x + 12 * s, y + 200 * s, 4, sid=sid, fill=(0.75, 0.75, 0.78))
    sketch_ellipse(cr, x, y, 120 * s, 38 * s, 6, sid=sid + 1, fill=(0.95, 0.95, 0.97))
    for i in range(4):
        a = ang + i * math.pi / 4
        sketch_line(cr, [(x - 110 * s * math.cos(a), y - 34 * s * math.sin(a)), (x + 110 * s * math.cos(a), y + 34 * s * math.sin(a))], 4, sid=sid + 2 + i)
    sketch_ellipse(cr, x, y, 26 * s, 10 * s, 4, sid=sid + 7, fill=PARK_RED)

def draw_cup_platform(cr, x, yb=FLOOR_Y, w=1500):
    sketch_ellipse(cr, x, yb + 30, w / 2, 110, 6, sid=12870, fill=(0.82, 0.78, 0.92))
    sketch_ellipse(cr, x, yb + 30, w / 2 - 60, 80, 3, sid=12871, fill=None)

def draw_height_sign(cr, x, yb=FLOOR_Y, line_y=415, light=0.0, arm=330, text=("YOU MUST BE", "THIS TALL", "TO RIDE")):
    """YOU MUST BE THIS TALL TO RIDE: a post with a big board and a cartoon arm sticking out LEFT at height line_y,
    plus a light on top (light 0 red .. 1 green)."""
    sketch_rect(cr, x - 22, line_y - 40, x + 22, yb, 5, sid=12900, fill=(0.98, 0.90, 0.40))
    for j in range(int((yb - line_y) // 70)):
        yy = yb - 70 * (j + 1)
        sketch_line(cr, [(x - 22, yy), (x - 2, yy)], 3, sid=12901)
    sketch_rect(cr, x - 30, line_y - 6, x - arm, line_y + 18, 5, sid=12902, fill=PARK_RED)       # the arm
    sketch_ellipse(cr, x - arm - 20, line_y + 6, 34, 26, 5, sid=12903, fill=(1, 1, 1))
    bw, bh = 420, 300
    by = line_y + 110; bx = x + 20 + bw / 2
    sketch_rect(cr, bx - bw / 2, by, bx + bw / 2, by + bh, 6, sid=12904, fill=(1.0, 1.0, 0.98))
    for i, ln in enumerate(text):
        draw_text(cr, ln, bx, by + 60 + i * 88, 58, color=(200, 50, 60), max_w=bw - 40)
    col = lerp((0.85, 0.2, 0.2), (0.25, 0.85, 0.35), light)
    if light > 0.5:
        cr.arc(x, line_y - 100, 90, 0, 2 * math.pi); cr.set_source_rgba(0.4, 1.0, 0.5, 0.3 * light); cr.fill()
    sketch_rect(cr, x - 8, line_y - 60, x + 8, line_y - 30, 4, sid=12906, fill=(0.6, 0.6, 0.6))
    sketch_circle(cr, x, line_y - 100, 46, 6, sid=12905, fill=col)

def draw_ride_gate(cr, x, yb=FLOOR_Y, open_=0.0):
    """a little swing gate (post + bar) that swings open."""
    sketch_rect(cr, x - 20, yb - 420, x + 20, yb, 5, sid=12920, fill=(0.75, 0.75, 0.78))
    L_ = 380 * math.cos(open_ * math.pi / 2 * 0.95)
    sketch_rect(cr, x + 10, yb - 360, x + 10 + max(30, L_), yb - 320, 4, sid=12921, fill=PARK_RED)

def track_normal(ang): return (math.sin(ang), -math.cos(ang))

def draw_track(cr, pts, yb=FLOOR_Y, supports=True, sid=12950, col=(0.36, 0.58, 0.92)):
    """roller coaster track along pts (list of (x, y)): two rails + ties, white support legs down to the ground."""
    if supports:
        for i in range(0, len(pts), 14):
            x, y = pts[i]
            if y < yb - 60:
                sketch_line(cr, [(x, y + 20), (x, yb)], 7, sid=sid + 1 + (i // 14) % 7, color=(0.55, 0.55, 0.6))
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    path(cr, pts); stroke_ink(cr, 30); path(cr, pts); stroke_ink(cr, 20, col)
    for i in range(0, len(pts) - 1, 4):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        a = math.atan2(y1 - y0, x1 - x0); nx, ny = track_normal(a)
        sketch_line(cr, [(x0 - nx * 26, y0 - ny * 26), (x0 + nx * 6, y0 + ny * 6)], 4, sid=sid + 9)

def draw_coaster_car(cr, x, y, ang=0.0, part="front", bar=1.0, s=1.0, col=PARK_RED, sign=None):
    """the front coaster car, car-local origin = on the track under the car centre; 'up' is the track normal.
    part 'back' = seat back behind the rider, 'front' = the body that covers him from the hips down + the lap bar."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    if part == "back":
        sketch_rect(cr, -230, -470, -150, -120, 6, sid=13000, fill=lerp(col, (0, 0, 0), 0.25))
    else:
        for wx in (-150, 150):
            sketch_circle(cr, wx, -18, 30, 5, sid=13001 + (wx > 0), fill=(0.3, 0.3, 0.33))
        pts = [(-250, -40), (-250, -250), (-120, -260), (180, -250), (300, -170), (300, -40)]
        sketch_poly(cr, pts, 7, sid=13003, fill=col, amp=0.5)
        sketch_line(cr, [(-240, -120), (290, -120)], 4, sid=13004, color=(1.0, 0.85, 0.35))
        if sign: draw_text(cr, sign, 20, -175, 40, color=(255, 250, 235), max_w=480)
        if bar > 0.01:                                                       # lap bar (swings down)
            a0 = 1.4 * (1 - bar)
            cr.save(); cr.translate(150, -250); cr.rotate(a0)
            sketch_line(cr, [(0, 0), (-110, -50), (-170, -50)], 18, sid=13005, color=(0.25, 0.25, 0.28))
            cr.restore()
    cr.restore()

def draw_photo_screen(cr, x, y, w=620, h=470, title="RIDE PHOTO", inner=None):
    """the on-ride photo monitor at the exit: a dark frame, a title, inner(cr, x0, y0, w, h) draws the photo."""
    sketch_rect(cr, x - w / 2 - 30, y - h / 2 - 110, x + w / 2 + 30, y + h / 2 + 30, 7, sid=13100, fill=(0.22, 0.22, 0.26))
    draw_text(cr, title, x, y - h / 2 - 55, 66, color=(255, 220, 90), max_w=w)
    sketch_rect(cr, x - w / 2, y - h / 2, x + w / 2, y + h / 2, 5, sid=13101, fill=(0.80, 0.91, 0.99))
    if inner:
        cr.save(); cr.rectangle(x - w / 2, y - h / 2, w, h); cr.clip()
        inner(cr, x - w / 2, y - h / 2, w, h)
        cr.restore()
        sketch_rect(cr, x - w / 2, y - h / 2, x + w / 2, y + h / 2, 5, sid=13102, fill=None)


# ------------------------------------------------------------------ the movies (day 14) ---
NIGHT_SKY = ((0.10, 0.12, 0.26), (0.16, 0.18, 0.36), (0.24, 0.24, 0.44))
CINE_RED, CINE_RED_D = (0.72, 0.14, 0.18), (0.50, 0.08, 0.12)
CINE_WALL = (0.16, 0.10, 0.14)
CINE_GOLD = (1.0, 0.82, 0.30)
STAFF_RED = (0.84, 0.16, 0.20)
COAT = (0.22, 0.22, 0.28)

def draw_city_night(cr, t, x0, x1, yb=FLOOR_Y, fade=0.0):
    """a night street right of x0: solid sky bands (no far-from-origin gradients), stars, dark buildings with lit windows,
    a sidewalk. Hide the seam at x0 behind something (the park's back gate)."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    a, b = max(x0, vx0), min(x1, vx1)
    if b <= a: return
    cr.save(); cr.rectangle(x0, vy0 - 10, x1 - x0, vy1 - vy0 + 20); cr.clip()
    top = min(vy0, yb - 3000)
    bands = [(top, yb - 1500, NIGHT_SKY[0]), (yb - 1500, yb - 900, NIGHT_SKY[1]), (yb - 900, yb + 10, NIGHT_SKY[2])]
    day = [TOWN_SKY[1], lerp(TOWN_SKY[0], TOWN_SKY[1], 0.5), TOWN_SKY[0]]
    def dusk(x): return clamp01((x - x0) / fade) if fade > 0 else 1.0
    step = 40
    for k in range(int((a - x0) // step), int((b - x0) // step) + 1):        # evening falls over `fade` px (solid strips)
        xs = x0 + k * step; u = dusk(xs + step / 2)
        for (y0, y1, col), dc in zip(bands, day):
            cr.rectangle(xs, y0, step + 1, y1 - y0 + 1); cr.set_source_rgb(*lerp(dc, col, smooth(u))); cr.fill()
    for k in range(int((a - x0) // 110) - 1, int((b - x0) // 110) + 2):            # stars
        sx = x0 + k * 110 + 47 * math.sin(k * 12.9898); sy = yb - 1100 - 900 * abs(math.sin(k * 78.233))
        tw = (0.6 + 0.4 * math.sin(t * 3 + k)) * smooth(clamp01(dusk(sx) * 1.5 - 0.5))
        cr.arc(sx, sy, 4 + 2 * (k % 3), 0, 2 * math.pi); cr.set_source_rgba(1, 1, 0.85, tw); cr.fill()
    for k in range(int((a - x0 - fade * 0.4) // 420) - 1, int((b - x0) // 420) + 2):            # buildings
        bx = x0 + fade * 0.4 + k * 420; h = 700 + 380 * abs(math.sin(k * 3.7)); w = 380
        sketch_rect(cr, bx, yb - h, bx + w, yb, 5, sid=14000 + (k % 7), fill=(0.20, 0.20, 0.32))
        for i in range(3):
            for j in range(int(h // 160) - 1):
                if math.sin(k * 7 + i * 3 + j * 5) > -0.2:
                    wx, wy = bx + 50 + i * 115, yb - h + 60 + j * 160
                    cr.rectangle(wx, wy, 60, 80); cr.set_source_rgb(1.0, 0.86, 0.45); cr.fill()
    for k in range(int((a - x0) // step), int((b - x0) // step) + 1):
        xs = x0 + k * step
        cr.rectangle(xs, yb, step + 1, max(200, vy1 - yb + 20)); cr.set_source_rgb(*lerp(WALK, (0.42, 0.42, 0.48), smooth(dusk(xs + step / 2)))); cr.fill()
    sketch_line(cr, [(a, yb), (b, yb)], 4, sid=14010, amp=1.0)
    for k in range(int((a - x0) // 260), int((b - x0) // 260) + 2):
        xx = x0 + k * 260
        sketch_line(cr, [(xx, yb + 4), (xx - 60, yb + 300)], 3, sid=14011, color=(0.32, 0.32, 0.38))
    cr.restore()

def _bulbs(cr, x0, y0, x1, y1, t, step=60, r=10, sid=0):
    """chasing marquee bulbs around a rectangle."""
    pts = []
    n_x, n_y = max(2, int((x1 - x0) / step)), max(2, int((y1 - y0) / step))
    for i in range(n_x + 1): pts.append((x0 + (x1 - x0) * i / n_x, y0))
    for i in range(1, n_y + 1): pts.append((x1, y0 + (y1 - y0) * i / n_y))
    for i in range(1, n_x + 1): pts.append((x1 - (x1 - x0) * i / n_x, y1))
    for i in range(1, n_y): pts.append((x0, y1 - (y1 - y0) * i / n_y))
    for i, (bx, by) in enumerate(pts):
        on = (i + int(t * 8)) % 3 == 0
        cr.arc(bx, by, r, 0, 2 * math.pi); cr.set_source_rgb(*((1.0, 0.95, 0.55) if on else (0.85, 0.62, 0.22)))
        cr.fill_preserve(); stroke_ink(cr, 3)

def draw_megaplex(cr, x, yb=FLOOR_Y, t=0.0):
    """MEGAPLEX 30: a red movie palace. Big bulb sign on top, a marquee (EXPLOSION 7 / NOW IN 4D), lit glass doors in the
    middle (x-160..x+160), poster cases either side."""
    w = 1000
    sketch_rect(cr, x - w, yb - 1500, x + w, yb, 7, sid=14100, fill=CINE_RED)
    for k in range(-4, 5):                                                     # pilasters
        cr.rectangle(x + k * 220 - 14, yb - 1500, 28, 1500); cr.set_source_rgb(*CINE_RED_D); cr.fill()
    sketch_rect(cr, x - w, yb - 1500, x + w, yb, 7, sid=14101, fill=None)
    # top sign
    sketch_rect(cr, x - 560, yb - 1890, x + 560, yb - 1540, 7, sid=14102, fill=(0.14, 0.12, 0.20))
    _bulbs(cr, x - 530, yb - 1860, x + 530, yb - 1570, t, step=70, r=12, sid=14103)
    draw_text(cr, "MEGAPLEX 30", x, yb - 1715, 150, color=(255, 214, 80), max_w=980)
    for dx in (-420, 420): sketch_line(cr, [(x + dx, yb - 1540), (x + dx, yb - 1500)], 10, sid=14104)
    # marquee
    sketch_poly(cr, [(x - 820, yb - 1300), (x + 820, yb - 1300), (x + 900, yb - 1140), (x - 900, yb - 1140)], 7, sid=14105, fill=(0.98, 0.95, 0.85))
    _bulbs(cr, x - 800, yb - 1280, x + 800, yb - 1160, t, step=80, r=9, sid=14106)
    draw_text(cr, "EXPLOSION 7", x, yb - 1245, 70, color=(30, 30, 34), max_w=1400)
    draw_text(cr, "TONIGHT ONLY", x, yb - 1185, 52, color=(200, 40, 50), max_w=1400)
    # doors
    sketch_rect(cr, x - 200, yb - 640, x + 200, yb, 7, sid=14107, fill=(1.0, 0.86, 0.50))
    sketch_line(cr, [(x, yb - 640), (x, yb)], 6, sid=14108)
    for dx in (-30, 30): sketch_line(cr, [(x + dx, yb - 360), (x + dx, yb - 260)], 8, sid=14109 + (dx > 0))
    # poster cases: the EXPLOSION 7 poster (a giant starburst)
    for k, px in enumerate((x - 650, x + 650)):
        sketch_rect(cr, px - 190, yb - 820, px + 190, yb - 220, 7, sid=14112 + k, fill=(0.12, 0.10, 0.16))
        draw_boom(cr, px, yb - 560, 150, t=t, sid=14120 + 10 * k)
        draw_text(cr, "EXPLOSION 7", px, yb - 300, 46, color=(255, 214, 80), max_w=340)
        _bulbs(cr, px - 190, yb - 820, px + 190, yb - 220, t, step=75, r=7, sid=14114 + k)

def draw_boom(cr, x, y, r, t=0.0, sid=14130, alpha=1.0):
    """a cartoon explosion starburst (orange + yellow), for posters and the movie screen."""
    for k, (rr, col) in enumerate(((1.0, (0.96, 0.42, 0.16)), (0.66, (1.0, 0.80, 0.25)), (0.34, (1.0, 0.97, 0.75)))):
        pts = []
        n = 14
        for i in range(2 * n):
            ang = i * math.pi / n + 0.15 * k + 0.05 * math.sin(t * 9 + i)
            q = r * rr * (1.0 if i % 2 == 0 else 0.62)
            pts.append((x + math.cos(ang) * q, y + math.sin(ang) * q))
        sketch_poly(cr, pts, 5, sid=sid + k, fill=col, alpha=alpha, amp=0.8)

def draw_no_pets(cr, x, yb=FLOOR_Y):
    """a sign on a post by the door: a cat in a red circle with a slash, NO PETS."""
    sketch_rect(cr, x - 14, yb - 640, x + 14, yb, 5, sid=14140, fill=(0.75, 0.70, 0.62))
    sketch_ellipse(cr, x, yb + 4, 90, 18, 4, sid=14141, fill=(0.75, 0.70, 0.62))
    sketch_rect(cr, x - 170, yb - 920, x + 170, yb - 560, 6, sid=14142, fill=(1, 1, 1))
    cy = yb - 775
    sketch_ellipse(cr, x, cy + 30, 52, 40, 4, sid=14143, fill=(0.15, 0.15, 0.18))        # cat silhouette
    sketch_circle(cr, x, cy - 30, 36, 4, sid=14144, fill=(0.15, 0.15, 0.18))
    for d in (-1, 1):
        sketch_poly(cr, [(x + d * 14, cy - 58), (x + d * 34, cy - 84), (x + d * 36, cy - 44)], 3, sid=14145 + (d > 0), fill=(0.15, 0.15, 0.18))
    cr.arc(x, cy, 110, 0, 2 * math.pi); stroke_ink(cr, 20, (0.88, 0.16, 0.18))
    cr.move_to(x - 78, cy - 78); cr.line_to(x + 78, cy + 78); stroke_ink(cr, 20, (0.88, 0.16, 0.18))
    draw_text(cr, "NO PETS", x, yb - 610, 56, color=(200, 30, 40), max_w=320)

def draw_staff(cr, t, p, blink=0.0, s=1.0, kind="usher", alpha=1.0, vest=None):
    """a cinema worker on his rig (p = constrained pose, world coords): red vest, and a red cap that hides the curl.
    kind "usher" (pillbox cap) or "cashier" (visor). Drawn scaled s around the feet."""
    if alpha < 0.01: return
    fx = (p["lfoot"][0] + p["rfoot"][0]) / 2
    cr.push_group()
    cr.save(); cr.translate(fx, FLOOR_Y); cr.scale(s, s); cr.translate(-fx, -FLOOR_Y)
    q = dict(p); q["larm_over"] = q["rarm_over"] = 1.0
    C.draw_guy(cr, t, q, blink)
    nx, ny = p["neck"]; hpx, hpy = p["hip"]
    sketch_poly(cr, [(nx - 40, ny + 18), (nx + 40, ny + 18), (hpx + 62, hpy - 10), (hpx + 60, hpy + 40), (hpx - 60, hpy + 40),
                     (hpx - 62, hpy - 10)], 6, sid=14150, fill=vest or (CREW_ORANGE if kind in ("crew", "flag") else STAFF_RED), amp=1.0)
    if kind in ("crew", "flag"):
        cr.rectangle(nx - 50, ny + 150, 100, 22); cr.set_source_rgb(0.95, 0.95, 0.92); cr.fill()
    elif kind == "plain":
        pass
    else:
        for k in range(3): cr.arc(nx, ny + 90 + 90 * k, 8, 0, 2 * math.pi); cr.set_source_rgb(*CINE_GOLD); cr.fill_preserve(); stroke_ink(cr, 3)
    C.draw_arm_over(cr, q, "l"); C.draw_arm_over(cr, q, "r")
    hx, hy = p["head"]; tl = p.get("tilt", 0.0); tn = p.get("turn", 0.0)
    cr.save(); cr.translate(hx, hy); cr.rotate(tl)
    R = C.HEAD_R
    if kind in ("crew", "flag"):                                                 # racing cap (+ headset for the crew)
        cap = CREW_BLUE if kind == "crew" else (0.15, 0.15, 0.18)
        sketch_poly(cr, [(-108, -R + 46), (-88, -R - 30), (0, -R - 52), (88, -R - 30), (108, -R + 46)], 6, sid=14154, fill=cap)
        sketch_poly(cr, [(60 * tn - 60, -R + 40), (60 * tn + 150, -R + 40), (60 * tn + 150, -R + 62), (60 * tn - 60, -R + 62)], 5,
                    sid=14155, fill=cap)
        if kind == "crew":
            cr.arc(0, 0, R + 14, math.pi * 1.05, math.pi * 1.95); stroke_ink(cr, 9)
            for d in (-1, 1): sketch_ellipse(cr, d * (R + 6), 0, 22, 40, 5, sid=14156 + (d > 0), fill=(0.2, 0.2, 0.24))
            sketch_line(cr, [(-(R + 6), 30), (-R + 20, 90), (-50, 100)], 5, sid=14158)
    elif kind == "plain":
        pass
    elif kind == "usher":
        sketch_rect(cr, -80 + 20 * tn, -R - 70, 80 + 20 * tn, -R + 22, 6, sid=14151, fill=STAFF_RED)
        cr.rectangle(-78 + 20 * tn, -R - 10, 156, 16); cr.set_source_rgb(*CINE_GOLD); cr.fill()
    else:
        sketch_poly(cr, [(-112, -R + 50), (-80, -R - 20), (80, -R - 20), (112, -R + 50)], 6, sid=14152, fill=STAFF_RED)
        sketch_poly(cr, [(40 * tn - 70, -R + 40), (40 * tn + 70, -R + 40), (40 * tn + 120 + 40 * tn, -R + 66), (40 * tn - 120 + 40 * tn, -R + 66)],
                    5, sid=14153, fill=STAFF_RED)
    cr.restore()
    cr.restore()
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha)

def draw_giant_back(cr, x, y, s=1.0, tilt=0.0, sid=14160):
    """the tall guy, seen from behind (in the theater): a dark coat's shoulders, the back of a big round head and a
    very tall top hat. (x, y) = the middle of his shoulders. ~1.7x our guy."""
    cr.save(); cr.translate(x, y); cr.rotate(tilt); cr.scale(s, s)
    sketch_poly(cr, [(-230, 260), (-215, 40), (-120, -10), (120, -10), (215, 40), (230, 260)], 7, sid=sid, fill=COAT)
    sketch_rect(cr, -26, -60, 26, 0, 6, sid=sid + 1, fill=PAPER)
    sketch_circle(cr, 0, -190, 150, 8, sid=sid + 2, fill=PAPER)
    sketch_ellipse(cr, 0, -318, 190, 34, 6, sid=sid + 3, fill=(0.12, 0.12, 0.14))
    sketch_rect(cr, -118, -660, 118, -322, 7, sid=sid + 4, fill=(0.12, 0.12, 0.14))
    cr.rectangle(-116, -400, 232, 40); cr.set_source_rgb(0.62, 0.14, 0.18); cr.fill()
    cr.restore()

def draw_popcorn(cr, x, yb, s=1.0, level=1.0, t=0.0, ang=0.0, label="SMALL", sid=14170):
    """a red/white striped popcorn bucket, bottom-centre at (x, yb). At s=1: 520 tall, 400 wide at the top.
    level 1 = heaped, 0 = empty (dark inside shows)."""
    cr.save(); cr.translate(x, yb); cr.rotate(ang); cr.scale(s, s)
    H, TW, BW = 520, 200, 150
    if level > 0.02:                                                       # the heap
        hh = 40 + 200 * level
        for i in range(11):
            u = i / 10; px = -TW + 2 * TW * u; py = -H - hh * math.sin(math.pi * u) * 0.9 + 18
            sketch_circle(cr, px * 0.92, py + 30, 42 + 8 * math.sin(i * 2.1), 4, sid=sid + i, fill=(1.0, 0.96, 0.78))
        for i in range(7):
            u = (i + 0.5) / 7; px = -TW * 0.75 + 1.5 * TW * u; py = -H - hh * math.sin(math.pi * u) * 0.65
            sketch_circle(cr, px, py + 50, 40, 4, sid=sid + 20 + i, fill=(1.0, 0.92, 0.62))
    pts = [(-TW, -H), (TW, -H), (BW, 0), (-BW, 0)]
    sketch_poly(cr, pts, 7, sid=sid + 41, fill=(1, 1, 1))
    cr.save(); path(cr, pts); cr.close_path(); cr.clip()
    for k in range(-3, 4):
        if k % 2 == 0: continue
        cr.move_to(k * 62 - 31, -H); cr.line_to(k * 62 + 31, -H); cr.line_to(k * 47 + 23, 0); cr.line_to(k * 47 - 23, 0); cr.close_path()
        cr.set_source_rgb(0.86, 0.18, 0.20); cr.fill()
    cr.restore()
    sketch_poly(cr, pts, 7, sid=sid + 42, fill=None)
    if level <= 0.02:
        sketch_ellipse(cr, 0, -H, TW, 34, 6, sid=sid + 40, fill=(0.24, 0.12, 0.12))
    if label:
        sketch_circle(cr, 0, -H * 0.5, 92, 5, sid=sid + 43, fill=(1, 1, 1))
        draw_text(cr, label, 0, -H * 0.5, 50, color=(200, 30, 40), max_w=160)
    cr.restore()

def draw_kernel(cr, x, y, r=26, sid=14190):
    sketch_circle(cr, x, y, r, 4, sid=sid, fill=(1.0, 0.95, 0.75))
    sketch_circle(cr, x + r * 0.5, y - r * 0.4, r * 0.6, 3, sid=sid + 1, fill=(1.0, 0.92, 0.62))

def draw_card_reader(cr, x, yb, ang=0.0, s=1.0, sid=14200):
    """the little card terminal on the counter (bottom-centre at x, yb). ang = how far it has swivelled to face him."""
    cr.save(); cr.translate(x, yb); cr.scale(s, s)
    sketch_rect(cr, -30, -70, 30, 0, 5, sid=sid, fill=(0.3, 0.3, 0.34))
    cr.translate(0, -70); sx = max(0.25, abs(math.cos(ang)))
    cr.scale(sx, 1)
    sketch_rect(cr, -95, -200, 95, 0, 6, sid=sid + 1, fill=(0.22, 0.22, 0.26))
    sketch_rect(cr, -75, -180, 75, -60, 4, sid=sid + 2, fill=(0.80, 0.93, 0.98))
    for i in range(3): sketch_rect(cr, -70 + i * 50, -45, -30 + i * 50, -15, 3, sid=sid + 3 + i, fill=(0.55, 0.55, 0.6))
    cr.restore()

def draw_tip_screen(cr, W, H, t=0.0, press=None, total=None, sid=14220):
    """INSERT SHOT (screen space, fills the frame): the card reader's screen asking for a tip on popcorn.
    press = None / "30" (that button lit). total = text shown after paying."""
    cr.set_source_rgb(0.18, 0.12, 0.10); cr.paint()                            # the counter, out of focus
    sketch_rect(cr, 60, 360, W - 60, 1720, 9, sid=sid, fill=(0.22, 0.22, 0.26))
    sketch_rect(cr, 110, 420, W - 110, 1560, 6, sid=sid + 1, fill=(0.85, 0.95, 0.99))
    for i in range(3): sketch_rect(cr, 160 + i * 270, 1600, 380 + i * 270, 1680, 4, sid=sid + 2 + i, fill=(0.55, 0.55, 0.6))
    if total:
        draw_text(cr, "THANK YOU!", W / 2, 760, 110, color=(30, 30, 34))
        draw_text(cr, total, W / 2, 1000, 150, color=(30, 30, 34))
        draw_text(cr, "POPCORN (SMALL)", W / 2, 1200, 60, color=(90, 90, 100))
        return
    draw_text(cr, "ADD A TIP?", W / 2, 580, 120, color=(30, 30, 34))
    for i, pct in enumerate(("20%", "25%", "30%")):
        y = 790 + i * 210
        lit = press == pct
        sketch_rect(cr, 200, y - 80, W - 200, y + 80, 6, sid=sid + 10 + i, fill=(0.30, 0.62, 0.95) if lit else (1, 1, 1))
        draw_text(cr, pct, W / 2, y, 100, color=(255, 255, 255) if lit else (30, 30, 34))
    draw_text(cr, "no tip", W - 240, 1490, 42, color=(130, 130, 140))

def draw_seat_row(cr, cx, y, n=9, w=200, h=220, gap=16, s=1.0, sid=14260, skip=()):
    """a row of cinema seat BACKS seen from behind; tops at y. skip = seat indices left out (someone's seat flew off)."""
    total = n * w + (n - 1) * gap
    for i in range(n):
        if i in skip: continue
        x0 = cx - total * s / 2 + i * (w + gap) * s
        sketch_rect(cr, x0, y, x0 + w * s, y + h * s, 6, sid=sid + i, fill=CINE_RED)
        cr.rectangle(x0 + 14 * s, y + 14 * s, w * s - 28 * s, 26 * s); cr.set_source_rgb(*CINE_RED_D); cr.fill()

def draw_seat_front(cr, x, y, s=1.0, sid=14290, part="all"):
    """one cinema seat seen from the front (the seat he sits in / empty seats behind him). (x, y) = top of the back."""
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    if part in ("all", "back"):
        sketch_rect(cr, -130, 0, 130, 420, 7, sid=sid, fill=CINE_RED)
        sketch_rect(cr, -100, 30, 100, 330, 5, sid=sid + 1, fill=CINE_RED_D)
    if part in ("all", "arms"):
        for d in (-1, 1):
            sketch_rect(cr, d * 150 - 30, 330, d * 150 + 30, 560, 6, sid=sid + 2 + (d > 0), fill=(0.30, 0.20, 0.22))
            sketch_rect(cr, d * 150 - 44, 310, d * 150 + 44, 350, 5, sid=sid + 4 + (d > 0), fill=(0.38, 0.26, 0.28))
    cr.restore()

HAT_BROWN, HAT_BAND = (0.66, 0.44, 0.24), (0.36, 0.22, 0.12)
def draw_cowboy_hat(cr, x, y, s=1.0, ang=0.0, sid=14950):
    """a tiny cowboy hat; (x, y) = the middle of the brim."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_poly(cr, [(-46, 0), (-40, -52), (-16, -66), (0, -56), (16, -66), (40, -52), (46, 0)], 5, sid=sid, fill=HAT_BROWN)
    cr.rectangle(-44, -16, 88, 13); cr.set_source_rgb(*HAT_BAND); cr.fill()
    path(cr, [(-100, -14), (-80, 4), (-40, 14), (40, 14), (80, 4), (100, -14), (84, 10), (40, 26), (-40, 26), (-84, 10)]); cr.close_path()
    cr.set_source_rgb(*HAT_BROWN); cr.fill_preserve(); stroke_ink(cr, 5)
    cr.restore()

def draw_periscope(cr, bx, by, top, view="front", sid=14960):
    """a grey periscope. front view: eyepiece box centred at (bx, by), the tube goes straight up to y=top, where the
    top box shows its mirror (facing the camera). back view: just the tube + the back of the top box."""
    G, GD = (0.62, 0.64, 0.68), (0.40, 0.42, 0.46)
    w = 44
    if top < by - 40:
        sketch_rect(cr, bx - w / 2, top + 40, bx + w / 2, by - 30, 5, sid=sid, fill=G)
        for k in range(1, 4):                                                   # telescoping joints
            yy = by - 30 - (by - 30 - top - 40) * k / 4
            sketch_rect(cr, bx - w / 2 - 5, yy - 8, bx + w / 2 + 5, yy + 8, 4, sid=sid + 1 + k, fill=GD)
    sketch_rect(cr, bx - 60, top - 40, bx + 60, top + 45, 6, sid=sid + 6, fill=G)
    if view == "front":
        sketch_rect(cr, bx - 42, top - 26, bx + 42, top + 30, 4, sid=sid + 7, fill=(0.70, 0.86, 0.98))
        sketch_rect(cr, bx - 58, by - 34, bx + 58, by + 34, 6, sid=sid + 8, fill=G)
        sketch_line(cr, [(bx - 40, by + 12), (bx + 40, by + 12)], 4, sid=sid + 9, color=GD)

def draw_car(cr, x, y, s=1.0, ang=0.0, col=(0.88, 0.18, 0.18), sid=14980):
    """a little cartoon getaway car (side view, facing right), (x, y) = between the wheels on the ground."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_rect(cr, -120, -70, 120, -20, 5, sid=sid, fill=col)
    sketch_poly(cr, [(-70, -70), (-45, -115), (40, -115), (70, -70)], 5, sid=sid + 1, fill=col)
    sketch_poly(cr, [(-52, -74), (-36, -104), (-4, -104), (-4, -74)], 3, sid=sid + 2, fill=(0.75, 0.90, 1.0))
    sketch_poly(cr, [(6, -74), (6, -104), (34, -104), (54, -74)], 3, sid=sid + 3, fill=(0.75, 0.90, 1.0))
    for wx in (-70, 70): sketch_circle(cr, wx, -18, 26, 5, sid=sid + 4 + (wx > 0), fill=(0.15, 0.15, 0.18))
    cr.restore()

# ============================================================ RACETRACK (day 14) ===
CREW_ORANGE = (0.98, 0.55, 0.16)
CREW_BLUE = (0.22, 0.40, 0.80)
CAR0 = (0.92, 0.20, 0.18)                  # his car (#0)
CAR0_D = (0.70, 0.12, 0.12)
ASPHALT = (0.38, 0.38, 0.42)
TRACK_SKY = ((0.66, 0.84, 0.98), (0.52, 0.76, 0.96))
CROWD_COLS = ((0.90, 0.30, 0.28), (0.98, 0.84, 0.32), (0.42, 0.80, 0.78), (0.45, 0.65, 0.95), (0.97, 0.62, 0.72),
              (0.68, 0.52, 0.86), (1.0, 1.0, 1.0), (0.30, 0.30, 0.34))
RC_SEAT = (0.0, -360.0)                    # car-local: his hip (cockpit centre)
RC_BUTTON = (-135.0, -1000.0)             # car-local: the DO NOT PRESS button (base centre), on an arm off the roll hoop
RC_EXHAUST = (-660.0, -250.0)

def rc_pt(x, yb, ang, lx, ly, s=1.0):
    """car-local -> world (car origin = ground point under the cockpit; ang rotates about the REAR wheel contact)."""
    px, py = -430.0 * s, 0.0
    qx, qy = lx * s - px, ly * s - py
    ca, sa = math.cos(ang), math.sin(ang)
    return (x + px + qx * ca - qy * sa, yb + py + qx * sa + qy * ca)

def _tyre(cr, x, y, r, spin=0.0, sid=0):
    sketch_circle(cr, x, y, r, 6, sid=sid, fill=(0.14, 0.14, 0.16))
    sketch_circle(cr, x, y, r * 0.45, 4, sid=sid + 1, fill=(0.70, 0.72, 0.76))
    for k in range(3):
        a = spin + k * 2 * math.pi / 3
        sketch_line(cr, [(x, y), (x + r * 0.42 * math.cos(a), y + r * 0.42 * math.sin(a))], 4, sid=sid + 2 + k, amp=0.2)

def draw_tyre(cr, x, y, r=110, ang=0.0, sid=17090):
    _tyre(cr, x, y, r, ang, sid)

def draw_racecar(cr, x, yb=FLOOR_Y, s=1.0, ang=0.0, part="all", col=CAR0, num="0", t=0.0, spin=0.0, driver=False,
                 button=False, pressed=0.0, hoop_h=None, sid=17000, wheels=True, look=0.0):
    """an open-wheel race car, side view facing right. (x, yb) = the ground under the cockpit. part "back" = engine
    cover, roll hoop (+ the DO NOT PRESS button), rear wing - drawn behind the driver; "front" = side pod, nose, wheels
    - drawn over his legs; "all" = both (+ a helmeted driver if driver=True). ang tilts it about the rear wheel."""
    dk = lerp(col, (0, 0, 0), 0.3)
    cr.save()
    px = -430.0 * s
    cr.translate(x + px, yb); cr.rotate(ang); cr.translate(-px, 0); cr.scale(s, s)
    if part in ("back", "all"):
        sketch_rect(cr, -680, -560, -540, -500, 5, sid=sid, fill=dk)                       # rear wing
        sketch_line(cr, [(-640, -500), (-600, -330)], 8, sid=sid + 1, amp=0.3)
        sketch_line(cr, [(-570, -500), (-540, -330)], 8, sid=sid + 2, amp=0.3)
        sketch_poly(cr, [(-650, -170), (-650, -320), (-420, -360), (-200, -470), (-120, -470), (-120, -200)], 6, sid=sid + 3, fill=col)
        hh = hoop_h if hoop_h is not None else (1000 if button else 560)
        px_ = -235
        sketch_rect(cr, px_ - 22, -hh, px_ + 22, -440, 5, sid=sid + 4, fill=(0.85, 0.86, 0.90))   # roll hoop post
        for k in range(int((hh - 470) // 90)):
            cr.rectangle(px_ - 20, -hh + 30 + 90 * k, 40, 30); cr.set_source_rgb(*col); cr.fill()
        if button:
            bx, by_ = RC_BUTTON
            sketch_rect(cr, px_ - 22, by_ - 22, bx + 30, by_ + 10, 5, sid=sid + 15, fill=(0.85, 0.86, 0.90))   # the arm
            sketch_rect(cr, bx - 56, by_ - 30, bx + 56, by_, 5, sid=sid + 5, fill=(0.3, 0.3, 0.34))
            py_ = by_ - 30 + 14 * pressed
            sketch_poly(cr, [(bx - 44, py_), (bx - 40, py_ - 26), (bx - 18, py_ - 42), (bx + 18, py_ - 42), (bx + 40, py_ - 26), (bx + 44, py_)],
                        5, sid=sid + 6, fill=(0.95, 0.12, 0.12))
            sketch_rect(cr, px_ - 100, -900, px_ + 100, -770, 5, sid=sid + 7, fill=(1.0, 0.86, 0.20))
            draw_text(cr, "DO NOT", px_, -862, 44, color=(20, 20, 24), max_w=185)
            draw_text(cr, "PRESS", px_, -805, 44, color=(20, 20, 24), max_w=185)
        if driver:
            sketch_circle(cr, 0, -510, 92, 6, sid=sid + 8, fill=lerp(col, (1, 1, 1), 0.5))
            cr.save(); cr.translate(0, -510); cr.rotate(look)
            sketch_rect(cr, 10, -40, 92, 10, 4, sid=sid + 9, fill=(0.12, 0.14, 0.2))
            cr.restore()
    if part in ("front", "all"):
        sketch_poly(cr, [(-640, -140), (-640, -300), (-170, -330), (-170, -400), (160, -400), (250, -320), (780, -250), (830, -200),
                         (790, -150), (160, -130)], 7, sid=sid + 10, fill=col)
        sketch_line(cr, [(-600, -230), (760, -205)], 10, sid=sid + 11, amp=0.3, color=(1, 1, 1))
        sketch_rect(cr, 620, -150, 880, -112, 5, sid=sid + 12, fill=dk)                        # front wing
        sketch_circle(cr, -300, -235, 62, 5, sid=sid + 13, fill=(1, 1, 1))
        draw_text(cr, num, -300, -235, 76, color=(20, 20, 24))
        sketch_poly(cr, [(-170, -400), (160, -400), (120, -430), (-150, -430)], 5, sid=sid + 14, fill=dk)  # cockpit rim
        if wheels:
            _tyre(cr, -430, -118, 118, spin, sid + 20)
            _tyre(cr, 460, -100, 100, spin * 1.2, sid + 30)
    cr.restore()

def draw_kitten_helmet(cr, x, y, s=0.62, ang=0.0, sid=17100):
    """a tiny racing helmet for the loafed kitten; (x, y) = the kitten's loaf spot (as kitten_spot returns)."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    hx, hy = -18, -88
    pts = [(hx - 50 + 100 * k / 16 - 0, hy - 8 - 54 * math.sin(math.pi * k / 16)) for k in range(17)]
    sketch_poly(cr, pts + [(hx + 52, hy - 2), (hx - 52, hy - 2)], 5, sid=sid, fill=CAR0)
    cr.rectangle(hx - 6, hy - 62, 12, 54); cr.set_source_rgb(1, 1, 1); cr.fill()
    sketch_line(cr, [(hx - 54, hy - 4), (hx + 56, hy - 4)], 7, sid=sid + 1, amp=0.3)
    cr.restore()

def draw_start_lights(cr, x, y, n_on=0, s=1.0, sid=17120):
    """the start gantry's light bar: five pods, two red lamps each. n_on lamps-pods lit (0..5)."""
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    sketch_rect(cr, -360, -26, 360, 26, 6, sid=sid, fill=(0.18, 0.18, 0.2))
    for i in range(5):
        cx = -280 + 140 * i
        sketch_rect(cr, cx - 52, -10, cx + 52, 230, 6, sid=sid + 1 + i, fill=(0.12, 0.12, 0.14))
        for j in range(2):
            on = i < n_on
            sketch_circle(cr, cx, 60 + 100 * j, 36, 4, sid=sid + 10 + 2 * i + j, fill=(1.0, 0.16, 0.12) if on else (0.30, 0.10, 0.10))
            if on:
                cr.arc(cx - 10, 50 + 100 * j, 10, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.7); cr.fill()
    cr.restore()

def draw_pit_board(cr, x, y, text, s=1.0, ang=0.0, sid=17140):
    """a pit board on a pole: (x, y) = the bottom of the board (the pole hangs below it)."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_line(cr, [(0, 0), (0, 160)], 12, sid=sid, amp=0.3)
    sketch_rect(cr, -190, -230, 190, 0, 7, sid=sid + 1, fill=(0.10, 0.10, 0.12))
    draw_text(cr, text, 0, -115, 120, color=(255, 214, 80), max_w=340)
    cr.restore()

def draw_flag(cr, x, y, kind="white", t=0.0, w=300, h=200, wave=1.0, sid=17160):
    """a waving flag on a short stick; (x, y) = the top of the stick (flag flies to the right)."""
    sketch_line(cr, [(x, y), (x, y + h + 140)], 9, sid=sid, amp=0.3)
    n = 10
    def pt(u, v):
        return (x + w * u, y + h * v + wave * 26 * math.sin(t * 11 - u * 5) * u)
    top = [pt(k / n, 0) for k in range(n + 1)]; bot = [pt(k / n, 1) for k in range(n, -1, -1)]
    sketch_poly(cr, top + bot, 5, sid=sid + 1, fill=(1, 1, 1))
    if kind == "checker":
        for i in range(6):
            for j in range(4):
                if (i + j) % 2: continue
                q = [pt(i / 6, j / 4), pt((i + 1) / 6, j / 4), pt((i + 1) / 6, (j + 1) / 4), pt(i / 6, (j + 1) / 4)]
                path(cr, q); cr.close_path(); cr.set_source_rgb(0.1, 0.1, 0.12); cr.fill()
        sketch_poly(cr, top + bot, 5, sid=sid + 2, fill=None)

def draw_checker_strip(cr, x, y0, y1, w=90, sq=45):
    for j in range(int((y1 - y0) // sq) + 1):
        for i in range(int(w // sq)):
            cr.rectangle(x + i * sq, y0 + j * sq, sq, sq)
            cr.set_source_rgb(*((0.1, 0.1, 0.12) if (i + j) % 2 else (1, 1, 1))); cr.fill()

def draw_raceway(cr, t, ox=0.0, x0=-1e9, yb=FLOOR_Y, marks=(), hats=0.0, hat_t0=0.0, blur=0.0):
    """the racetrack seen from the infield, side-scrolling: sky, grandstand + crowd, catch fence, the outer wall with
    ads, the asphalt. ox = how far the scenery has scrolled LEFT (treadmill), x0 = left edge (a wall hides it).
    marks = (kind, world_x) extras on the track: "pit" (a painted box with a 0), "finish" (checker strip)."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    lx = max(vx0, x0)
    cr.rectangle(lx, vy0, vx1 - lx, 420 - vy0); cr.set_source_rgb(*TRACK_SKY[0]); cr.fill()
    # grandstand roof + seats + crowd
    cr.rectangle(lx, 240, vx1 - lx, 60); cr.set_source_rgb(0.30, 0.32, 0.38); cr.fill()
    cr.rectangle(lx, 300, vx1 - lx, 690); cr.set_source_rgb(0.72, 0.72, 0.76); cr.fill()
    sketch_line(cr, [(lx, 300), (vx1, 300)], 5, sid=17200)
    step = 52.0
    k0 = int((lx + ox) // step) - 1; k1 = int((vx1 + ox) // step) + 1
    for row in range(10):
        yy = 340 + row * 62
        for k in range(k0, k1):
            xx = k * step - ox + (row % 2) * step / 2
            if xx < lx - 30: continue
            hsh = (k * 7919 + row * 104729) % 97
            if hsh < 12: continue
            col = CROWD_COLS[hsh % len(CROWD_COLS)]
            bob = 6 * math.sin(t * 9 + hsh) if hsh % 3 == 0 else 0
            cr.arc(xx, yy + bob, 17, 0, 2 * math.pi); cr.set_source_rgb(*col); cr.fill_preserve()
            cr.set_source_rgb(*INK); cr.set_line_width(3); cr.stroke()
            if hats > 0 and hsh % 4 == 0:                                             # hats blown off by the pass
                u = max(0.0, t - hat_t0 - (hsh % 7) * 0.03)
                if u > 0:
                    hx_, hy_ = xx - 900 * u, yy - 18 - 1300 * u + 900 * u * u
                    cr.save(); cr.translate(hx_, hy_); cr.rotate(-6 * u)
                    cr.rectangle(-18, -14, 36, 14); cr.set_source_rgb(*CROWD_COLS[(hsh + 3) % 8]); cr.fill_preserve(); stroke_ink(cr, 3)
                    cr.restore()
    for k in range(int((lx + ox) // 600) - 1, int((vx1 + ox) // 600) + 2):           # roof posts
        xx = k * 600 - ox
        sketch_line(cr, [(xx, 300), (xx, 990)], 6, sid=17210 + k % 5, amp=0.3, color=(0.45, 0.46, 0.5))
    # catch fence
    cr.set_source_rgba(0.35, 0.36, 0.4, 0.55); cr.set_line_width(3)
    for k in range(int((lx + ox) // 70) - 1, int((vx1 + ox) // 70) + 2):
        xx = k * 70 - ox
        cr.move_to(xx, 780); cr.line_to(xx, 990); cr.stroke()
    cr.move_to(lx, 780); cr.line_to(vx1, 780); cr.stroke()
    # the wall + ads
    cr.rectangle(lx, 990, vx1 - lx, 140); cr.set_source_rgb(0.97, 0.97, 0.95); cr.fill()
    cr.rectangle(lx, 1100, vx1 - lx, 30); cr.set_source_rgb(0.86, 0.20, 0.20); cr.fill()
    ads = ("GO FAST", "TIRES", "SPEEDWAY", "TURN LEFT", "OIL")
    for k in range(int((lx + ox) // 900) - 1, int((vx1 + ox) // 900) + 2):
        xx = k * 900 - ox
        if xx < lx - 400: continue
        draw_text(cr, ads[k % len(ads)], xx + 300, 1045, 58, color=(40, 60, 140) if k % 2 else (200, 50, 40), max_w=520)
    sketch_line(cr, [(lx, 990), (vx1, 990)], 5, sid=17220)
    sketch_line(cr, [(lx, 1130), (vx1, 1130)], 5, sid=17221)
    # asphalt
    cr.rectangle(lx, 1130, vx1 - lx, vy1 - 1130); cr.set_source_rgb(*ASPHALT); cr.fill()
    for k in range(int((lx + ox) // 400) - 1, int((vx1 + ox) // 400) + 2):            # dashes (show the speed)
        xx = k * 400 - ox
        cr.rectangle(xx, yb + 70, 200, 16); cr.set_source_rgb(0.95, 0.95, 0.92); cr.fill()
    cr.rectangle(lx, 1300, vx1 - lx, 10); cr.set_source_rgb(0.95, 0.95, 0.92); cr.fill()
    for kind, wx in marks:
        xx = wx - ox
        if xx < vx0 - 1200 or xx > vx1 + 1200: continue
        if kind == "pit":
            cr.set_source_rgb(1.0, 0.86, 0.2); cr.set_line_width(14)
            cr.rectangle(xx - 800, 1330, 1600, yb + 150 - 1330); cr.stroke()
            draw_text(cr, "0", xx + 650, yb + 120, 70, color=(255, 214, 50))
        elif kind == "finish":
            draw_checker_strip(cr, xx - 45, 1130, vy1, 90)
    if blur > 0:
        for k in range(16):
            yy = 330 + k * 92
            cr.move_to(vx0, yy); cr.line_to(vx1, yy); cr.set_source_rgba(1, 1, 1, 0.25 * blur); cr.set_line_width(10); cr.stroke()

def draw_back_door(cr, x, yb=FLOOR_Y, open_=0.0, x_left=-1e9):
    """the megaplex's back wall (everything left of x), with the EXIT door at x - 260 swinging open toward us."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    cr.rectangle(vx0, vy0, x - vx0, vy1 - vy0); cr.set_source_rgb(0.52, 0.22, 0.20); cr.fill()
    for j in range(int((vy0) // 70) - 1, int(vy1 // 70) + 1):                     # bricks
        yy = j * 70
        cr.move_to(vx0, yy); cr.line_to(x, yy); cr.set_source_rgba(0.3, 0.1, 0.1, 0.6); cr.set_line_width(4); cr.stroke()
        for i in range(int((vx0) // 150) - 1, int(x // 150) + 1):
            xx = i * 150 + (75 if j % 2 else 0)
            if xx < x: cr.move_to(xx, yy); cr.line_to(xx, yy + 70); cr.stroke()
    sketch_line(cr, [(x, vy0), (x, yb)], 7, sid=17300)
    dx0, dx1, dy0 = x - 460, x - 60, yb - 820
    sketch_rect(cr, dx0, dy0, dx1, yb, 7, sid=17301, fill=(0.95, 0.98, 1.0))       # daylight... (inside is bright)
    sketch_rect(cr, dx0 + 40, dy0 - 170, dx1 - 40, dy0 - 50, 6, sid=17302, fill=(0.20, 0.70, 0.35))
    draw_text(cr, "EXIT", (dx0 + dx1) / 2, dy0 - 110, 72, color=(255, 255, 255))
    w = (dx1 - dx0) * (1 - 0.85 * open_)
    sketch_rect(cr, dx1 - w if open_ < 0.5 else dx1, dy0, dx1 if open_ < 0.5 else dx1 + (dx1 - dx0) * 0.85 * open_, yb, 7, sid=17303,
                fill=(0.62, 0.64, 0.68))

def draw_trophy(cr, x, yb=FLOOR_Y, s=1.0, part="all", sid=17400):
    """a giant gold trophy (~1150 tall at s=1). part "back" = the cup's inside rim, "front" = everything else."""
    G, GD = (1.0, 0.80, 0.22), (0.86, 0.62, 0.12)
    cr.save(); cr.translate(x, yb); cr.scale(s, s)
    if part in ("back", "all"):
        sketch_ellipse(cr, 0, -1120, 300, 50, 6, sid=sid, fill=(0.62, 0.44, 0.08))
    if part in ("front", "all"):
        sketch_rect(cr, -240, -140, 240, 0, 7, sid=sid + 1, fill=(0.28, 0.20, 0.14))
        sketch_rect(cr, -190, -230, 190, -140, 6, sid=sid + 2, fill=(0.28, 0.20, 0.14))
        cr.rectangle(-120, -110, 240, 60); cr.set_source_rgb(*GD); cr.fill()
        draw_text(cr, "1ST", 0, -80, 50, color=(60, 40, 10))
        sketch_poly(cr, [(-60, -230), (-40, -560), (40, -560), (60, -230)], 6, sid=sid + 3, fill=G)
        sketch_ellipse(cr, 0, -580, 120, 40, 5, sid=sid + 4, fill=GD)
        for d in (-1, 1):                                                           # handles
            sketch_curve(cr, (d * 260, -1050), (d * 470, -900), (d * 180, -760), 22, sid=sid + 5 + (d > 0), color=INK)
            sketch_curve(cr, (d * 260, -1050), (d * 470, -900), (d * 180, -760), 12, sid=sid + 5 + (d > 0), amp=0.0, color=GD)
        cup = [(-300 + 0, -1120)] + [(300 * math.cos(math.pi - a), -1120 + 500 * math.sin(a) ** 0.8) for a in [math.pi * k / 24 for k in range(1, 24)]] + [(300, -1120)]
        sketch_poly(cr, cup, 7, sid=sid + 8, fill=G)
        cr.arc(-120, -1000, 30, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.6); cr.fill()
        sketch_line(cr, [(-300, -1120), (300, -1120)], 7, sid=sid + 9)
    cr.restore()

def draw_milk(cr, x, y, s=1.0, ang=0.0, level=1.0, sid=17420):
    """a glass milk bottle; (x, y) = its middle."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    body = [(-55, 110), (-55, -20), (-30, -70), (-28, -120), (28, -120), (30, -70), (55, -20), (55, 110)]
    sketch_poly(cr, body, 5, sid=sid, fill=(0.88, 0.94, 0.98))
    if level > 0.01:
        top = 110 - 200 * level
        cr.save(); path(cr, body); cr.close_path(); cr.clip()
        cr.rectangle(-60, top, 120, 240); cr.set_source_rgb(1, 1, 1); cr.fill(); cr.restore()
        sketch_line(cr, [(-50, top), (50, top)], 3, sid=sid + 1, amp=0.2, alpha=0.5)
    sketch_poly(cr, body, 5, sid=sid + 2, fill=None)
    sketch_rect(cr, -40, -10, 40, 60, 3, sid=sid + 3, fill=(0.45, 0.65, 0.95))
    draw_text(cr, "MILK", 0, 25, 30, color=(255, 255, 255))
    cr.restore()

def draw_squeegee(cr, x, y, ang=0.0, s=1.0, sid=17440):
    """(x, y) = the middle of the rubber blade; the handle goes off to the right/down."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_line(cr, [(0, 0), (40, 300)], 12, sid=sid, amp=0.3, color=(0.45, 0.45, 0.5))
    sketch_rect(cr, -14, -110, 14, 110, 5, sid=sid + 1, fill=(0.2, 0.2, 0.22))
    cr.restore()

def draw_confetti(cr, t, t0, x0, x1, y_top, n=60, seed=3):
    u = t - t0
    if u < 0: return
    for k in range(n):
        h = (k * 2654435761 + seed) % 1000 / 1000.0
        h2 = (k * 40503 + seed * 7) % 1000 / 1000.0
        x = x0 + (x1 - x0) * h + 60 * math.sin(u * 3 + k)
        y = y_top - 300 * h2 + u * (350 + 200 * h)
        cr.save(); cr.translate(x, y); cr.rotate(u * 5 + k)
        cr.rectangle(-14, -8, 28, 16); cr.set_source_rgb(*CROWD_COLS[k % 6]); cr.fill()
        cr.restore()

def draw_victory_arch(cr, x, yb=FLOOR_Y, w=1500, h=1250, sid=17460):
    for d in (-1, 1):
        sketch_rect(cr, x + d * w / 2 - 40, yb - h, x + d * w / 2 + 40, yb, 6, sid=sid + (d > 0), fill=(0.95, 0.95, 0.92))
    sketch_rect(cr, x - w / 2 - 80, yb - h - 170, x + w / 2 + 80, yb - h + 10, 7, sid=sid + 2, fill=(0.12, 0.12, 0.14))
    draw_checker_strip(cr, x - w / 2 - 70, yb - h - 160, yb - h - 115, w + 140, 45)
    draw_text(cr, "VICTORY LANE", x, yb - h - 50, 96, color=(255, 214, 80), max_w=w)

# ============================================================ THE WHITE PARTY (day 14) ===
LIMO = (0.10, 0.10, 0.12)
TINT = (0.20, 0.22, 0.30)
SKIN_HOST = (0.45, 0.30, 0.21)
SUIT = (0.98, 0.98, 0.96)
CREAM = (0.97, 0.92, 0.82)
GOLD = (0.96, 0.78, 0.25)
OIL = (0.99, 0.86, 0.52)

def draw_limo(cr, x, yb=FLOOR_Y, s=1.0, door=0.0, t=0.0, spin=0.0, sid=18000):
    """a long black car, side view facing right; (x, yb) = ground under the middle. door = rear door swing 0..1
    (the door is at x-330..x-40)."""
    cr.save(); cr.translate(x, yb); cr.scale(s, s)
    sketch_poly(cr, [(-980, -150), (-980, -420), (-700, -460), (-560, -720), (420, -720), (620, -470), (960, -430), (990, -300),
                     (990, -150)], 7, sid=sid, fill=LIMO)
    for (a, b) in ((-660, -360), (-300, 20), (60, 380)):                       # tinted windows
        pts = [(a, -480), (a + 30 if a == -660 else a, -690), (b, -690), (b if b < 380 else 560, -480)] if a != -660 else [(-660, -480), (-540, -690), (-360, -690), (-360, -480)]
        sketch_poly(cr, pts, 5, sid=sid + 1 + (a > 0), fill=TINT)
        sketch_line(cr, [(pts[0][0] + 40, -520), (pts[0][0] + 120, -650)], 6, sid=sid + 5, color=(1, 1, 1), alpha=0.35)
    sketch_line(cr, [(-960, -300), (970, -300)], 6, sid=sid + 6, color=(0.75, 0.76, 0.8))
    sketch_rect(cr, 940, -400, 990, -350, 4, sid=sid + 7, fill=(1.0, 0.95, 0.7))
    sketch_rect(cr, -985, -400, -955, -350, 4, sid=sid + 8, fill=(0.9, 0.15, 0.15))
    for wx in (-640, 640):
        sketch_circle(cr, wx, -120, 120, 6, sid=sid + 9 + (wx > 0), fill=(0.08, 0.08, 0.09))
        sketch_circle(cr, wx, -120, 55, 4, sid=sid + 11 + (wx > 0), fill=(0.75, 0.76, 0.8))
        for k in range(3):
            a = spin + k * 2.094
            sketch_line(cr, [(wx, -120), (wx + 50 * math.cos(a), -120 + 50 * math.sin(a))], 4, sid=sid + 13 + k, amp=0.2)
    # the rear door (x -300..20): opens toward us (it swings out to the left)
    if door > 0.01:
        sketch_rect(cr, -300, -690, 20, -160, 5, sid=sid + 20, fill=(0.03, 0.03, 0.05))      # the dark doorway
        w = 320 * (1 - 0.75 * door)
        sketch_poly(cr, [(-300, -690), (-300 - w * 0.9, -700 - 40 * door), (-300 - w * 0.9, -150 + 30 * door), (-300, -160)], 6, sid=sid + 21, fill=LIMO)
    else:
        sketch_line(cr, [(-300, -700), (-300, -160)], 4, sid=sid + 22, color=(0.3, 0.3, 0.34))
        sketch_line(cr, [(20, -700), (20, -160)], 4, sid=sid + 23, color=(0.3, 0.3, 0.34))
        sketch_rect(cr, -60, -400, -10, -380, 3, sid=sid + 24, fill=(0.75, 0.76, 0.8))
    cr.restore()

def draw_night_sky(cr, yb=FLOOR_Y, t=0.0, ox=0.0):
    vx0, vy0, vx1, vy1 = _visible(cr)
    for (y0, y1, col) in ((vy0, yb - 1500, NIGHT_SKY[0]), (yb - 1500, yb - 900, NIGHT_SKY[1]), (yb - 900, vy1, NIGHT_SKY[2])):
        cr.rectangle(vx0, y0, vx1 - vx0, y1 - y0 + 1); cr.set_source_rgb(*col); cr.fill()
    for k in range(int((vx0 + ox * 0.2) // 130) - 1, int((vx1 + ox * 0.2) // 130) + 2):
        sx = k * 130 - ox * 0.2 + 47 * math.sin(k * 12.9898); sy = yb - 1000 - 1100 * abs(math.sin(k * 78.233))
        cr.arc(sx, sy, 4 + 2 * (k % 3), 0, 2 * math.pi); cr.set_source_rgba(1, 1, 0.85, 0.6 + 0.4 * math.sin(t * 3 + k)); cr.fill()

def draw_fountain(cr, x, yb=FLOOR_Y, t=0.0, s=1.0, sid=18100):
    cr.save(); cr.translate(x, yb); cr.scale(s, s)
    sketch_ellipse(cr, 0, -60, 420, 70, 6, sid=sid, fill=(0.85, 0.85, 0.88))
    sketch_rect(cr, -420, -60, 420, 0, 6, sid=sid + 1, fill=(0.85, 0.85, 0.88))
    sketch_rect(cr, -40, -420, 40, -60, 5, sid=sid + 2, fill=(0.88, 0.88, 0.9))
    sketch_ellipse(cr, 0, -420, 200, 40, 5, sid=sid + 3, fill=(0.88, 0.88, 0.9))
    for k in range(-3, 4):                                                       # water arcs
        pts = [(k * 10 + 280 * k / 3 * u, -430 - 300 * u * (1 - u) * 2.2 + 360 * u * u) for u in [i / 10 for i in range(11)]]
        sketch_line(cr, pts, 6, sid=sid + 10 + k, color=(0.55, 0.78, 0.98), alpha=0.85)
    sketch_line(cr, [(0, -440), (0, -720 - 20 * math.sin(t * 9))], 10, sid=sid + 20, color=(0.55, 0.78, 0.98))
    cr.restore()

def draw_hedge(cr, x, yb=FLOOR_Y, s=1.0, sid=18120):
    cr.save(); cr.translate(x, yb); cr.scale(s, s)
    sketch_rect(cr, -30, -120, 30, 0, 4, sid=sid, fill=(0.40, 0.26, 0.16))
    sketch_circle(cr, 0, -260, 150, 5, sid=sid + 1, fill=(0.20, 0.42, 0.24))
    cr.restore()

def draw_lamp(cr, x, yb=FLOOR_Y, sid=18130):
    sketch_line(cr, [(x, yb), (x, yb - 900)], 10, sid=sid, amp=0.3, color=(0.12, 0.12, 0.14))
    cr.arc(x, yb - 930, 110, 0, 2 * math.pi); cr.set_source_rgba(1, 0.9, 0.5, 0.25); cr.fill()
    sketch_circle(cr, x, yb - 930, 44, 5, sid=sid + 1, fill=(1.0, 0.92, 0.55))

def draw_sign(cr, x, yb, text, sid=18140, w=520, size=58):
    sketch_line(cr, [(x, yb), (x, yb - 520)], 10, sid=sid, amp=0.3, color=(0.4, 0.3, 0.2))
    sketch_rect(cr, x - w / 2, yb - 720, x + w / 2, yb - 500, 6, sid=sid + 1, fill=(1, 1, 0.97))
    lines = text.split("|")
    for i, ln in enumerate(lines):
        draw_text(cr, ln, x, yb - 610 + (i - (len(lines) - 1) / 2) * size * 1.05, size, color=(30, 30, 34), max_w=w - 30)

def draw_gate(cr, x, yb=FLOOR_Y, sid=18160, text="WHITE PARTY"):
    for d in (-1, 1):
        sketch_rect(cr, x + d * 700 - 60, yb - 1250, x + d * 700 + 60, yb, 7, sid=sid + (d > 0), fill=(0.92, 0.92, 0.9))
        sketch_circle(cr, x + d * 700, yb - 1290, 60, 5, sid=sid + 2 + (d > 0), fill=GOLD)
    sketch_rect(cr, x - 640, yb - 1250, x + 640, yb - 1080, 6, sid=sid + 4, fill=(0.12, 0.12, 0.14))
    draw_text(cr, text, x, yb - 1165, 96, color=(255, 214, 80), max_w=1200)
    for k in range(-8, 9):
        sketch_line(cr, [(x + k * 75, yb - 1080), (x + k * 75, yb - 820)], 5, sid=sid + 10 + k % 4, amp=0.3, color=(0.75, 0.6, 0.2))

def draw_mansion(cr, x, yb=FLOOR_Y, t=0.0, door=0.0, sid=18200):
    """a huge white mansion; the front doors (x-300..x+300, 900 tall) at the top of three steps."""
    W = 2600
    sketch_poly(cr, [(x - W - 100, yb - 2050), (x, yb - 2700), (x + W + 100, yb - 2050)], 8, sid=sid, fill=(0.30, 0.30, 0.36))
    sketch_rect(cr, x - W, yb - 2050, x + W, yb - 120, 8, sid=sid + 1, fill=(0.97, 0.95, 0.90))
    for i in range(-5, 6):
        if abs(i) <= 1: continue
        for j in range(2):
            wx, wy = x + i * 430, yb - 1850 + j * 820
            sketch_rect(cr, wx - 120, wy, wx + 120, wy + 520, 5, sid=sid + 10 + (i + j) % 7, fill=(1.0, 0.88, 0.50))
            sketch_line(cr, [(wx, wy), (wx, wy + 520)], 4, sid=sid + 20, amp=0.2)
    for k in (-3, -1.4, 1.4, 3):                                                  # columns
        cx = x + k * 260
        sketch_rect(cr, cx - 60, yb - 1900, cx + 60, yb - 120, 6, sid=sid + 30 + int(k * 2) % 9, fill=(1, 1, 0.98))
    sketch_rect(cr, x - 1000, yb - 2000, x + 1000, yb - 1880, 6, sid=sid + 40, fill=(1, 1, 0.98))
    draw_text(cr, "WHITE PARTY", x, yb - 1940, 90, color=(200, 160, 40), max_w=1800)
    for k in range(3):
        sketch_rect(cr, x - 900 + 80 * k, yb - 120 + 40 * k, x + 900 - 80 * k, yb - 80 + 40 * k, 5, sid=sid + 50 + k, fill=(0.92, 0.92, 0.94))
    draw_double_door(cr, x, yb - 120, door, sid=sid + 60)
    cr.arc(x, yb - 1300, 120, 0, 2 * math.pi); cr.set_source_rgba(1, 0.9, 0.5, 0.2); cr.fill()

def draw_double_door(cr, x, yb, open_=0.0, w=600, h=900, sid=18260):
    sketch_rect(cr, x - w / 2 - 40, yb - h - 40, x + w / 2 + 40, yb, 7, sid=sid, fill=(0.85, 0.80, 0.70))
    sketch_rect(cr, x - w / 2, yb - h, x + w / 2, yb, 6, sid=sid + 1, fill=(1.0, 0.88, 0.55))        # warm light inside
    if open_ > 0.01:
        for k in range(5):
            cr.arc(x - 200 + 100 * k, yb - h + 220, 18, 0, 2 * math.pi); cr.set_source_rgba(0.6, 0.45, 0.2, 0.5); cr.fill()
    lw = w / 2 * (1 - 0.8 * open_)
    for d in (-1, 1):
        x0 = x + d * w / 2
        pts = [(x0, yb - h), (x0 - d * lw, yb - h + 30 * open_), (x0 - d * lw, yb - 30 * open_), (x0, yb)]
        sketch_poly(cr, pts, 6, sid=sid + 2 + (d > 0), fill=(0.36, 0.20, 0.12))
        hx = x0 - d * lw * 0.85
        sketch_circle(cr, hx, yb - h / 2, 18, 4, sid=sid + 4 + (d > 0), fill=GOLD)

def draw_hall(cr, t, x0=-1e9, x1=1e9, yb=FLOOR_Y, sid=18300, windows=True):
    """a grand ballroom: cream walls, red curtains, gold trim, a black-and-white marble floor."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    a, b = max(vx0, x0), min(vx1, x1)
    cr.rectangle(a, vy0, b - a, yb - vy0); cr.set_source_rgb(*CREAM); cr.fill()
    cr.rectangle(a, yb - 360, b - a, 18); cr.set_source_rgb(*GOLD); cr.fill()
    cr.rectangle(a, vy0, b - a, 60 - vy0); cr.set_source_rgb(0.92, 0.86, 0.74); cr.fill()
    if windows:
        for k in range(int(a // 900) - 1, int(b // 900) + 2):
            wx = k * 900 + 450
            sketch_rect(cr, wx - 160, 220, wx + 160, yb - 420, 6, sid=sid + k % 5, fill=(0.16, 0.18, 0.34))
            for d in (-1, 1):
                sketch_poly(cr, [(wx + d * 160, 180), (wx + d * 260, 180), (wx + d * 230, yb - 400), (wx + d * 150, yb - 400)], 5,
                            sid=sid + 10 + (d > 0), fill=(0.72, 0.12, 0.16))
    cr.rectangle(a, yb, b - a, vy1 - yb); cr.set_source_rgb(0.96, 0.96, 0.94); cr.fill()
    for k in range(int(a // 160) - 1, int(b // 160) + 2):
        for j in range(6):
            if (k + j) % 2:
                cr.rectangle(k * 160, yb + j * 100, 160, 100); cr.set_source_rgb(0.16, 0.16, 0.18); cr.fill()
    sketch_line(cr, [(a, yb), (b, yb)], 5, sid=sid + 20)

def draw_chandelier(cr, x, y, t=0.0, sid=18330):
    sketch_line(cr, [(x, -600), (x, y - 120)], 6, sid=sid, amp=0.2)
    sketch_ellipse(cr, x, y, 260, 50, 6, sid=sid + 1, fill=GOLD)
    for k in range(-3, 4):
        cx = x + k * 80
        sketch_line(cr, [(cx, y), (cx, y + 70 + 10 * (k % 2))], 4, sid=sid + 2, amp=0.2)
        cr.arc(cx, y + 80, 14, 0, 2 * math.pi); cr.set_source_rgb(0.75, 0.9, 1.0); cr.fill_preserve(); stroke_ink(cr, 3)
        cr.arc(cx, y - 30, 26, 0, 2 * math.pi); cr.set_source_rgba(1, 0.9, 0.5, 0.35 + 0.1 * math.sin(t * 5 + k)); cr.fill()
        sketch_line(cr, [(cx, y), (cx, y - 30)], 8, sid=sid + 3, amp=0.2, color=(1, 1, 1))

def draw_coupe(cr, x, y, s=1.0, ang=0.0, full=True, sid=18350):
    """a champagne coupe; (x, y) = the base."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_line(cr, [(-26, 0), (26, 0)], 5, sid=sid, amp=0.2)
    sketch_line(cr, [(0, 0), (0, -60)], 5, sid=sid + 1, amp=0.2)
    pts = [(-46, -60 - 30 * math.sin(math.pi * u)) for u in []]
    sketch_poly(cr, [(-50, -90), (50, -90), (24, -62), (-24, -62)], 4, sid=sid + 2, fill=(1.0, 0.92, 0.60) if full else (0.92, 0.96, 1.0))
    cr.restore()

def draw_champagne_tower(cr, x, yb=FLOOR_Y, t=0.0, fall=0.0, t0=0.0, sid=18360):
    """a table with a pyramid of coupes. fall > 0: the glasses fly everywhere (u = seconds since the crash)."""
    sketch_rect(cr, x - 260, yb - 420, x + 260, yb - 380, 5, sid=sid, fill=(1, 1, 1))
    sketch_poly(cr, [(x - 260, yb - 380), (x + 260, yb - 380), (x + 220, yb), (x - 220, yb)], 5, sid=sid + 1, fill=(1, 1, 1))
    rows = 4
    for r in range(rows):
        n = rows - r
        for i in range(n):
            gx = x + (i - (n - 1) / 2) * 104; gy = yb - 420 - r * 92
            if fall > 0:
                h = (i * 13 + r * 7) % 11 / 11.0
                vx = (h - 0.5) * 2400; vy = -900 - 900 * h
                gx += vx * fall; gy += vy * fall + 2600 * fall * fall
                draw_coupe(cr, gx, gy, 1.0, ang=fall * (8 * h - 4), full=False, sid=sid + 10 + (i + r) % 6)
            else:
                draw_coupe(cr, gx, gy, 1.0, sid=sid + 10 + (i + r) % 6)

def draw_easel(cr, x, yb=FLOOR_Y, text="DRESS CODE:|ALL WHITE", sid=18400):
    for d in (-1, 1): sketch_line(cr, [(x + d * 30, yb - 900), (x + d * 170, yb)], 8, sid=sid + (d > 0), amp=0.3, color=(0.45, 0.3, 0.18))
    sketch_rect(cr, x - 220, yb - 920, x + 220, yb - 480, 6, sid=sid + 2, fill=(0.12, 0.12, 0.14))
    cr.rectangle(x - 205, yb - 905, 410, 410); cr.set_source_rgb(*GOLD); cr.set_line_width(4); cr.stroke()
    for i, ln in enumerate(text.split("|")):
        draw_text(cr, ln, x, yb - 760 + i * 90, 62, color=(255, 255, 255), max_w=380)

def draw_baby_oil(cr, x, y, s=1.0, ang=0.0, squeeze=0.0, sid=18420):
    """a big bottle of baby oil; (x, y) = its middle (cap points up at ang=0)."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s * (1 + 0.08 * squeeze), s * (1 - 0.05 * squeeze))
    body = [(-70, 150), (-70, -60), (-50, -120), (-28, -140), (28, -140), (50, -120), (70, -60), (70, 150)]
    sketch_poly(cr, body, 6, sid=sid, fill=(0.99, 0.80, 0.70))
    cr.save(); path(cr, body); cr.close_path(); cr.clip()
    cr.rectangle(-70, -40, 140, 190); cr.set_source_rgba(*OIL, 0.8); cr.fill(); cr.restore()
    sketch_poly(cr, body, 6, sid=sid + 1, fill=None)
    sketch_rect(cr, -30, -200, 30, -140, 5, sid=sid + 2, fill=(1.0, 0.55, 0.70))
    sketch_rect(cr, -58, -30, 58, 110, 4, sid=sid + 3, fill=(1, 1, 1))
    draw_text(cr, "BABY", 0, 10, 40, color=(230, 80, 130))
    draw_text(cr, "OIL", 0, 62, 44, color=(230, 80, 130))
    sketch_line(cr, [(-48, -90), (-48, 120)], 6, sid=sid + 4, color=(1, 1, 1), alpha=0.6, amp=0.2)
    cr.restore()

def draw_oil_stream(cr, pts, w=20, sid=18440):
    if len(pts) < 2: return
    path(cr, pts); cr.set_source_rgba(*OIL, 0.9); cr.set_line_width(w); cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.stroke()
    path(cr, pts); cr.set_source_rgba(1, 1, 1, 0.6); cr.set_line_width(w * 0.3); cr.stroke()

def draw_oil_puddle(cr, x, yb, r, sid=18450):
    sketch_ellipse(cr, x, yb + 20, r, r * 0.16, 4, sid=sid, fill=OIL, alpha=0.95)
    sketch_ellipse(cr, x - r * 0.3, yb + 14, r * 0.25, r * 0.04, 0.1, sid=sid + 1, fill=(1, 1, 1), alpha=0.7)

def draw_gift_bag(cr, x, y, s=1.0, sid=18460):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    for d in (-1, 1): sketch_curve(cr, (d * 60, -130), (d * 30, -230), (d * 10 - 0, -130), 6, sid=sid + (d > 0))
    sketch_poly(cr, [(-110, -130), (110, -130), (100, 120), (-100, 120)], 6, sid=sid + 2, fill=(1, 1, 1))
    draw_text(cr, "PARTY", 0, -40, 44, color=(200, 160, 40))
    draw_text(cr, "FAVOR", 0, 10, 44, color=(200, 160, 40))
    cr.restore()

def draw_host(cr, p, t=0.0, s=1.15, smirk=0.3, bottle=None, squeeze=0.0, glance=0.0):
    """the party host: brown skin, short black hair, a trimmed beard, dark sunglasses, an all-white suit and a gold chain.
    p = a constrained rig pose (world coords, feet on FLOOR_Y); drawn scaled s around the feet. bottle = 'r'/'l' hand
    holding the baby oil."""
    fx = (p["lfoot"][0] + p["rfoot"][0]) / 2
    cr.save(); cr.translate(fx, FLOOR_Y); cr.scale(s, s); cr.translate(-fx, -FLOOR_Y)
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    def limb(a, b, c, w=44):
        path(cr, [a, b, c]); cr.set_source_rgb(*INK); cr.set_line_width(w + 10); cr.stroke()
        path(cr, [a, b, c]); cr.set_source_rgb(*SUIT); cr.set_line_width(w); cr.stroke()
    hip, neck = p["hip"], p["neck"]
    for sd in ("l", "r"):                                                       # legs + shoes
        limb((hip[0] + (-24 if sd == "l" else 24), hip[1]), p[sd + "knee"], p[sd + "foot"])
        fx_, fy_ = p[sd + "foot"]
        sketch_ellipse(cr, fx_ + (-14 if sd == "l" else 14), fy_ - 10, 46, 22, 5, sid=18500 + (sd == "r"), fill=(0.08, 0.08, 0.1))
    nx, ny = neck; hx_, hy_ = hip
    jacket = [(nx - 70, ny + 10), (nx + 70, ny + 10), (hx_ + 82, hy_ + 30), (hx_ - 82, hy_ + 30)]
    sketch_poly(cr, jacket, 6, sid=18502, fill=SUIT)
    sketch_poly(cr, [(nx - 30, ny + 10), (nx + 30, ny + 10), (nx, ny + 150)], 4, sid=18503, fill=(0.95, 0.95, 0.93))
    sketch_line(cr, [(nx - 40, ny + 10), (nx - 10, ny + 200)], 4, sid=18504, amp=0.3)
    sketch_line(cr, [(nx + 40, ny + 10), (nx + 10, ny + 200)], 4, sid=18505, amp=0.3)
    pts = [(nx - 42 + 84 * u, ny + 20 + 110 * math.sin(math.pi * u)) for u in [i / 12 for i in range(13)]]   # gold chain
    path(cr, pts); cr.set_source_rgb(*GOLD); cr.set_line_width(9); cr.stroke()
    for sd in ("l", "r"):                                                       # arms + hands
        sh = (nx + (-62 if sd == "l" else 62), ny + 30)
        limb(sh, p[sd + "elb"], p[sd + "hand"], 38)
        hx2, hy2 = p[sd + "hand"]
        sketch_circle(cr, hx2, hy2, 26, 5, sid=18510 + (sd == "r"), fill=SKIN_HOST)
    if bottle:                                                                  # held by the neck, label clear
        bx, by = p[bottle + "hand"]
        sketch_circle(cr, bx, by, 26, 5, sid=18512, fill=SKIN_HOST)
        draw_baby_oil(cr, bx, by + 120, s=1.0, ang=0.12 if bottle == "r" else -0.12, squeeze=squeeze)
        sketch_circle(cr, bx + 6, by - 4, 22, 4, sid=18512, fill=SKIN_HOST)
    hx, hy = p["head"]; tl = p.get("tilt", 0.0); tn = p.get("turn", 0.0)
    cr.save(); cr.translate(hx, hy); cr.rotate(tl)
    R = 112
    sketch_rect(cr, -30, R - 30, 30, R + 40, 5, sid=18513, fill=SKIN_HOST)
    sketch_circle(cr, 0, 0, R, 7, sid=18514, fill=SKIN_HOST)
    cr.save(); cr.arc(0, 0, R - 4, 0, 2 * math.pi); cr.clip()
    cr.rectangle(-R, -R, 2 * R, 52); cr.set_source_rgb(0.08, 0.06, 0.06); cr.fill()            # short hair
    cr.arc(0, 30, R - 6, 0.12 * math.pi, 0.88 * math.pi); cr.set_line_width(36); cr.set_source_rgb(0.12, 0.08, 0.07); cr.stroke()   # beard
    cr.restore()
    ox = 26 * tn
    sketch_rect(cr, ox - 26, 18, ox + 26, 30, 3, sid=18515, fill=(0.12, 0.08, 0.07))           # moustache
    sketch_line(cr, [(ox - 28 + 0, 62), (ox + 0, 66 + 10 * smirk), (ox + 30, 56 - 14 * smirk)], 5, sid=18516, amp=0.2)
    for d in (-1, 1):                                                           # the sunglasses
        sketch_rect(cr, ox + d * 50 - 40, -40, ox + d * 50 + 40, 8, 5, sid=18517 + (d > 0), fill=(0.04, 0.04, 0.06))
        sketch_line(cr, [(ox + d * 50 - 24, -30), (ox + d * 50 - 6, -6)], 5, sid=18519, color=(1, 1, 1), alpha=0.5, amp=0.1)
    sketch_line(cr, [(ox - 10, -24), (ox + 10, -24)], 6, sid=18520, amp=0.1)
    cr.restore()
    cr.restore()


# ------------------------------------------------------------------ day 15: the beach ("seja feliz") ---
BEACH_SKY = ((0.78, 0.92, 1.0), (0.42, 0.70, 0.97))
SEA = (0.30, 0.72, 0.80)
SEA_D = (0.20, 0.55, 0.68)
SAND = (0.97, 0.88, 0.66)
SAND_WET = (0.88, 0.76, 0.52)
ROCK = (0.42, 0.52, 0.40)
RAINBOW = ((0.93, 0.25, 0.25), (0.98, 0.58, 0.20), (0.99, 0.88, 0.30), (0.40, 0.80, 0.40), (0.30, 0.55, 0.92), (0.58, 0.38, 0.85))

def draw_sugarloaf(cr, x, yb, h=1300, w=900, sid=15000):
    """a big rounded granite dome rising out of the sea (bottom-centre x, yb), a smaller hump to its left and a cable
    car line between their tops."""
    hx, hh, hw = x - 1100, h * 0.5, w * 0.8
    for (cx, hh_, ww, s_) in ((hx, hh, hw, sid), (x, h, w, sid + 1)):
        pts = []
        for k in range(25):
            u = k / 24
            a = math.pi * u
            pts.append((cx - ww / 2 * math.cos(a) * (1 + 0.15 * math.sin(a * 2)), yb - hh_ * math.sin(a) ** 0.55))
        sketch_poly(cr, pts, 6, sid=s_, fill=ROCK, amp=0.4)
        for k in range(3):                                            # a few rock lines
            sketch_line(cr, [(cx - ww * 0.2 + k * ww * 0.18, yb - hh_ * 0.85), (cx - ww * 0.28 + k * ww * 0.2, yb - hh_ * 0.35)], 3,
                        sid=s_ + 10 + k, color=(0.30, 0.38, 0.30))
        sketch_poly(cr, [(cx - ww * 0.3, yb - hh_ * 0.98 + 30), (cx, yb - hh_ - 20), (cx + ww * 0.3, yb - hh_ * 0.98 + 30)], 4,
                    sid=s_ + 20, fill=(0.35, 0.60, 0.35), amp=0.4)      # green cap
    a, b = (hx, yb - hh - 10), (x, yb - h - 10)
    sketch_line(cr, [a, b], 3, sid=sid + 30, amp=0.2)
    return a, b

def draw_cable_car(cr, a, b, u, s=1.0, sid=15040):
    """a little cable car cabin hanging from the line a->b at fraction u."""
    px, py = lerp(a, b, u)
    sketch_line(cr, [(px, py), (px, py + 60 * s)], 4, sid=sid, amp=0.2)
    sketch_rect(cr, px - 55 * s, py + 60 * s, px + 55 * s, py + 150 * s, 4, sid=sid + 1, fill=(0.95, 0.85, 0.30))
    sketch_rect(cr, px - 40 * s, py + 75 * s, px + 40 * s, py + 110 * s, 3, sid=sid + 2, fill=(0.75, 0.90, 0.98))

def draw_promenade(cr, x0, x1, yb, depth=260, sid=15060):
    """the famous black-and-white wavy mosaic sidewalk, as a floor strip from yb down."""
    cr.rectangle(x0, yb, x1 - x0, depth); cr.set_source_rgb(0.98, 0.97, 0.94); cr.fill()
    for row in range(5):
        y = yb + 30 + row * 52
        pts = [(x, y + 18 * math.sin((x - x0) / 70.0)) for x in range(int(x0), int(x1) + 20, 20)]
        if row % 2 == 0:
            cr.move_to(*pts[0])
            for p in pts[1:]: cr.line_to(*p)
            cr.set_source_rgb(0.12, 0.12, 0.14); cr.set_line_width(26); cr.stroke()

def draw_beach_umbrella(cr, x, yb, col=(0.95, 0.35, 0.30), sid=15080):
    sketch_line(cr, [(x, yb), (x + 30, yb - 520)], 8, sid=sid, amp=0.3)
    pts = [(x + 30 + 300 * math.cos(math.pi + k * math.pi / 8), yb - 520 - 120 * math.sin(k * math.pi / 8)) for k in range(9)]
    sketch_poly(cr, pts, 5, sid=sid + 1, fill=col, amp=0.4)
    for k in (2, 4, 6):
        a = math.pi + k * math.pi / 8
        sketch_line(cr, [(x + 30, yb - 640), (x + 30 + 300 * math.cos(a), yb - 520 - 120 * math.sin(k * math.pi / 8))], 3, sid=sid + 2 + k)

def draw_beach_world(cr, t, x0, x1, prom_end, yb=FLOOR_Y, wind=0.0, sugar_x=None):
    """sunny beach right of x0: deep-blue sky bands, the sun, puffy clouds, the sea with waves, a big granite dome with a
    cable car out in the bay, sand as the floor; left of prom_end the floor is the wavy mosaic sidewalk."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    a, b = max(x0, vx0), min(x1, vx1)
    if b <= a: return
    cr.save(); cr.rectangle(x0, vy0 - 10, x1 - x0, vy1 - vy0 + 20); cr.clip()
    top = min(vy0, yb - 200)
    nb = int((yb - 400 - top) // 150) + 2
    for k in range(nb):
        y_lo = yb - 400 - k * 150 if k else yb + 10; y_hi = yb - 400 - (k + 1) * 150
        cr.rectangle(a, y_hi, b - a, y_lo - y_hi + 1); cr.set_source_rgb(*lerp(BEACH_SKY[0], BEACH_SKY[1], min(1.0, k / 14))); cr.fill()
    sx = x0 + 5400
    if a - 600 < sx < b + 600:
        for k in range(12):
            an = k * math.pi / 6 + t * 0.2
            sketch_line(cr, [(sx + 170 * math.cos(an), yb - 1750 + 170 * math.sin(an)), (sx + 240 * math.cos(an), yb - 1750 + 240 * math.sin(an))], 8, sid=15100 + k, color=(0.98, 0.70, 0.20))
        sketch_circle(cr, sx, yb - 1750, 130, 6, sid=15099, fill=(1.0, 0.86, 0.35))
    for k in range(int((a - x0) // 1100) - 1, int((b - x0) // 1100) + 2):
        draw_cloud(cr, x0 + k * 1100 + 300 + 30 * math.sin(t * 0.2 + k), yb - 1500 - 260 * (k % 3) - 900 * (k % 2), s=0.9 + 0.25 * (k % 2))
    # the sea
    cr.rectangle(a, yb - 420, b - a, 260); cr.set_source_rgb(*SEA); cr.fill()
    if sugar_x is not None and a - 1800 < sugar_x < b + 1800:
        ca, cb = draw_sugarloaf(cr, sugar_x, yb - 380)
        draw_cable_car(cr, ca, cb, 0.35 + 0.25 * math.sin(t * 0.25))
    cr.rectangle(a, yb - 400, b - a, 240); cr.set_source_rgb(*SEA); cr.fill()
    sketch_line(cr, [(a, yb - 420), (b, yb - 420)], 4, sid=15120, amp=0.6)
    for k in range(int(a // 300) - 1, int(b // 300) + 2):
        wx = k * 300 + 60 * math.sin(t * 0.8 + k)
        yy = yb - 360 + 60 * (k % 3)
        cr.move_to(wx - 60, yy); cr.curve_to(wx - 30, yy - 18, wx + 30, yy - 18, wx + 60, yy)
        cr.set_source_rgb(*SEA_D); cr.set_line_width(5); cr.stroke()
    # sand
    cr.rectangle(a, yb - 160, b - a, max(400, vy1 - yb + 200)); cr.set_source_rgb(*SAND); cr.fill()
    cr.rectangle(a, yb - 160, b - a, 50); cr.set_source_rgb(*SAND_WET); cr.fill()
    foam = [(x, yb - 160 + 10 * math.sin(x / 90.0 + t * 1.5)) for x in range(int(a), int(b) + 40, 40)]
    sketch_line(cr, foam, 7, sid=15121, color=(1, 1, 1), amp=0.4)
    for k in range(int(a // 230) - 1, int(b // 230) + 2):                 # sand speckles
        xx = k * 230 + 70 * math.sin(k * 3.7)
        cr.arc(xx, yb - 60 + 40 * math.sin(k * 1.9), 5, 0, 2 * math.pi); cr.set_source_rgb(0.85, 0.72, 0.48); cr.fill()
    for k in range(int((a - x0) // 1900) - 1, int((b - x0) // 1900) + 2):  # palms + umbrellas on the back of the beach
        bx = x0 + 1200 + k * 1900
        if bx > prom_end + 300 and k % 2 == 0:
            draw_beach_umbrella(cr, bx + 300, yb - 100, col=((0.95, 0.35, 0.30), (0.30, 0.60, 0.95), (0.99, 0.80, 0.25))[k % 3], sid=15080 + k % 3 * 10)
        else:
            draw_palm(cr, bx, t, h=950, bend=-0.1 - 0.7 * wind, yb=yb - 110, s=0.9, sid=k % 4)
    if a < prom_end:
        draw_promenade(cr, a, min(b, prom_end), yb - 30, depth=max(400, vy1 - yb + 200))
        cr.rectangle(a, yb - 160, min(b, prom_end) - a, 130); cr.set_source_rgb(0.62, 0.62, 0.64); cr.fill()   # the road edge
    sketch_line(cr, [(a, yb), (b, yb)], 4, sid=15122, amp=1.0, alpha=0.4)
    cr.restore()

def draw_seagull(cr, x, y, s=1.0, flap=0.0, facing=-1, carry=0, sid=15200, cone=False):
    """a white seagull, centre (x, y); flap -1..1 wing angle; facing 1 = flying right, -1 = left; carry = scoops in its beak."""
    cr.save(); cr.translate(x, y); cr.scale(s * facing, s)             # drawn facing right (facing=1), mirrored for left
    for side in (-1, 1):                                                # wings
        ang = flap * 0.9
        tip = (-40 + 30 * side, -150 * math.cos(ang) * (1 if side > 0 else 0.85) + 20)
        tip = (-30 + 40 * side, -40 - 140 * math.sin(0.6 + ang))
        sketch_poly(cr, [(-50, -10), (tip[0] - 60, tip[1] - 10), (tip[0] + 40, tip[1]), (40, -10)], 5, sid=sid + (side > 0),
                    fill=(0.78, 0.80, 0.84) if side < 0 else (0.88, 0.89, 0.92), amp=0.4)
    sketch_ellipse(cr, 0, 0, 95, 42, 5, sid=sid + 3, fill=(1, 1, 1))
    sketch_circle(cr, 80, -30, 40, 5, sid=sid + 4, fill=(1, 1, 1))
    sketch_poly(cr, [(112, -34), (165, -24), (112, -14)], 4, sid=sid + 5, fill=(0.98, 0.65, 0.15), amp=0.2)
    cr.arc(90, -40, 7, 0, 2 * math.pi); fill_ink(cr); cr.new_path()
    sketch_poly(cr, [(-90, -5), (-150, -25), (-150, 20)], 4, sid=sid + 6, fill=(0.78, 0.80, 0.84), amp=0.2)
    for k in range(carry):
        sketch_circle(cr, 175 + 20 * k, -10 + 46 * k, 34, 4, sid=sid + 10 + k, fill=SCOOPS[k % 3])
    if cone:                                                            # a whole ice-cream cone clutched in its feet
        sketch_line(cr, [(-10, 30), (0, 60)], 4, sid=sid + 30, amp=0.2, color=(0.98, 0.65, 0.15))
        sketch_line(cr, [(25, 30), (28, 60)], 4, sid=sid + 31, amp=0.2, color=(0.98, 0.65, 0.15))
        draw_cone(cr, 15, 280, 0.94)
    cr.restore()

SCOOPS = ((0.97, 0.72, 0.78), (0.74, 0.92, 0.8), (0.99, 0.95, 0.84))

def draw_scoop(cr, x, y, r=48, col=SCOOPS[0], sid=15220):
    sketch_circle(cr, x, y, r, 5, sid=sid, fill=col)
    cr.arc(x - r * 0.3, y - r * 0.3, r * 0.18, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.8); cr.fill()

def draw_empty_cone(cr, x, y, s=1.0):
    """just the cone, held at (x, y)."""
    top = y - 60 * s
    path(cr, [(x - 46 * s, top), (x, y + 95 * s), (x + 46 * s, top)]); cr.close_path(); fill_paper(cr, (0.93, 0.76, 0.5)); stroke_ink(cr, 6)
    cr.save(); path(cr, [(x - 46 * s, top), (x, y + 95 * s), (x + 46 * s, top)]); cr.close_path(); cr.clip()
    for k in range(-4, 5):
        cr.move_to(x + k * 24 * s - 60 * s, top); cr.line_to(x + k * 24 * s + 60 * s, y + 100 * s)
        cr.move_to(x + k * 24 * s + 60 * s, top); cr.line_to(x + k * 24 * s - 60 * s, y + 100 * s)
    stroke_ink(cr, 2.5, alpha=0.5); cr.restore()

def draw_rain_cloud(cr, x, y, s=1.0, dark=0.5, alpha=1.0):
    """a grey rain cloud, centre (x, y). dark 0 (light grey) .. 1 (storm)."""
    if s <= 0.02 or alpha <= 0.01: return
    puffs = [(-110, 20, 70), (-45, -25, 85), (40, -35, 90), (110, 10, 72), (0, 30, 80)]
    col = lerp((0.82, 0.83, 0.86), (0.34, 0.35, 0.40), dark)
    cr.push_group()
    for dx, dy, r in puffs:
        cr.arc(x + dx * s, y + dy * s, r * s, 0, 2 * math.pi); cr.new_sub_path()
    cr.set_source_rgb(*INK); cr.set_line_width(14 * s); cr.stroke_preserve(); cr.set_source_rgb(*col); cr.fill()
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha)

def draw_cloud_rain(cr, t, x, y_top, y_bot, w, amt=1.0, seed=0):
    """streaks of rain falling from a cloud: x centre, width w, between y_top and y_bot; amt 0..1 density."""
    n = int(30 * amt)
    for k in range(n):
        h1 = (math.sin(k * 12.9898 + seed) * 43758.5453) % 1.0
        h2 = (math.sin(k * 78.233 + seed) * 12345.678) % 1.0
        u = ((t * 2.6) + h1) % 1.0
        xx = x - w / 2 + w * h2
        yy = y_top + u * (y_bot - y_top)
        cr.move_to(xx, yy); cr.line_to(xx - 6, yy + 46)
        cr.set_source_rgb(*INK); cr.set_line_width(9); cr.stroke()
        cr.move_to(xx, yy); cr.line_to(xx - 6, yy + 46)
        cr.set_source_rgb(0.55, 0.75, 0.95); cr.set_line_width(5); cr.stroke()

def draw_bolt(cr, x0, y0, x1, y1, sid=15240, alpha=1.0):
    """a fat zig-zag lightning bolt from (x0, y0) to (x1, y1)."""
    n = 6
    pts = []
    for k in range(n + 1):
        u = k / n
        off = (0 if k in (0, n) else (60 if k % 2 else -60))
        pts.append((x0 + (x1 - x0) * u + off, y0 + (y1 - y0) * u))
    left = [(px - 22, py) for px, py in pts]; right = [(px + 22, py) for px, py in pts[::-1]]
    right[0] = (pts[-1][0], pts[-1][1]); left[-1] = (pts[-1][0], pts[-1][1])
    sketch_poly(cr, left + right, 6, sid=sid, fill=(1.0, 0.92, 0.30), alpha=alpha, amp=0.3)

def draw_kite(cr, x, y, s=1.0, ang=0.0, t=0.0, tail=1.0, sid=15260):
    """a yellow diamond kite with a smiley face, centre (x, y), and a bow tail that waves."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    pts = [(0, -150), (100, -20), (0, 150), (-100, -20)]
    # tail first (behind)
    tp = [(0, 150)]
    for k in range(1, 8):
        tp.append((40 * math.sin(t * 7 + k * 0.9) * tail, 150 + k * 50))
    sketch_line(cr, tp, 4, sid=sid + 1, amp=0.3)
    for k in (2, 4, 6):
        bx, by = tp[k]
        sketch_poly(cr, [(bx, by), (bx - 26, by - 16), (bx - 26, by + 16)], 3, sid=sid + 2 + k, fill=(0.95, 0.35, 0.30), amp=0.2)
        sketch_poly(cr, [(bx, by), (bx + 26, by - 16), (bx + 26, by + 16)], 3, sid=sid + 3 + k, fill=(0.95, 0.35, 0.30), amp=0.2)
    sketch_poly(cr, pts, 6, sid=sid, fill=(1.0, 0.86, 0.25), amp=0.4)
    sketch_line(cr, [(0, -150), (0, 150)], 3, sid=sid + 20, alpha=0.5)
    sketch_line(cr, [(-100, -20), (100, -20)], 3, sid=sid + 21, alpha=0.5)
    cr.arc(-32, -45, 11, 0, 2 * math.pi); fill_ink(cr); cr.new_path()
    cr.arc(32, -45, 11, 0, 2 * math.pi); fill_ink(cr); cr.new_path()
    cr.arc(0, -10, 45, 0.25 * math.pi, 0.75 * math.pi); stroke_ink(cr, 7); cr.new_path()
    cr.restore()

def draw_rainbow(cr, cx, yb, r, band=55, alpha=1.0, sweep=1.0):
    """a rainbow arc standing on the ground at yb, centre cx, outer radius r. sweep 0..1 grows it from the left leg."""
    if alpha <= 0.01 or sweep <= 0.01: return
    cr.push_group()
    a0 = math.pi; a1 = math.pi + math.pi * sweep
    for k, col in enumerate(RAINBOW):
        ro = r - k * band
        cr.new_path(); cr.arc(cx, yb, ro, a0, a1); cr.arc_negative(cx, yb, ro - band, a1, a0); cr.close_path()
        cr.set_source_rgb(*col); cr.fill()
    cr.new_path(); cr.arc(cx, yb, r, a0, a1); cr.set_source_rgb(*INK); cr.set_line_width(7); cr.stroke()
    cr.new_path(); cr.arc(cx, yb, r - 6 * band, a0, a1); cr.set_line_width(6); cr.stroke()
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha)

# ============================================================ day 17: a park at golden hour (girlfriend + baby)
PARK_SKY = ((1.00, 0.86, 0.62), (0.99, 0.76, 0.58), (0.93, 0.66, 0.62), (0.78, 0.62, 0.72), (0.58, 0.60, 0.80))
PAVING = (0.86, 0.80, 0.72)
LAWN = (0.60, 0.78, 0.42)
SKYLINE = (0.74, 0.58, 0.62)
ROSE_RED = (0.88, 0.16, 0.24)
BOOM = (0.26, 0.27, 0.32)
SAUCE = (0.86, 0.26, 0.16)
PASTA = (0.99, 0.88, 0.52)
STORK_ORANGE = (0.98, 0.55, 0.18)
CAP_BLUE = (0.30, 0.50, 0.86)

def draw_park_world(cr, t, x0, x1, yb=FLOOR_Y, trees=(), lamps=()):
    """a city park at golden hour, between x0 and x1: warm sky bands (solid, no far gradients), a low sun, a soft
    skyline, a hedge, a lawn strip, round trees and lamp posts at the given x, and a paved path as the floor."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    a, b = max(x0, vx0), min(x1, vx1)
    if b <= a: return
    cr.save(); cr.rectangle(x0, vy0 - 10, x1 - x0, vy1 - vy0 + 20); cr.clip()
    top = min(vy0, yb - 300)
    nb = int((yb - 300 - top) // 170) + 2
    for k in range(nb):
        y_lo = yb - 300 - k * 170 if k else yb + 10; y_hi = yb - 300 - (k + 1) * 170
        cr.rectangle(a, y_hi, b - a, y_lo - y_hi + 1); cr.set_source_rgb(*PARK_SKY[min(len(PARK_SKY) - 1, k // 2)]); cr.fill()
    sx = x0 + (x1 - x0) * 0.55                                          # the low sun
    cr.arc(sx, yb - 760, 330, 0, 2 * math.pi); cr.set_source_rgba(1.0, 0.95, 0.70, 0.35); cr.fill()
    sketch_circle(cr, sx, yb - 760, 200, 6, sid=19000, fill=(1.0, 0.90, 0.55))
    for k in range(int((a - x0) // 1300) - 1, int((b - x0) // 1300) + 2):
        draw_cloud(cr, x0 + k * 1300 + 400 + 30 * math.sin(t * 0.15 + k), yb - 1650 - 240 * (k % 3), s=0.8 + 0.2 * (k % 2))
    for k in range(int((a - x0) // 260) - 1, int((b - x0) // 260) + 2):  # the skyline, far away
        bx = x0 + k * 260
        h = 360 + 260 * abs(math.sin(k * 1.7)) + 160 * (k % 3 == 0)
        cr.rectangle(bx, yb - 300 - h, 230, h); cr.set_source_rgb(*SKYLINE); cr.fill()
        for j in range(int(h // 90)):
            for i in range(2):
                cr.rectangle(bx + 40 + i * 100, yb - 300 - h + 40 + j * 90, 40, 40)
        cr.set_source_rgba(1.0, 0.92, 0.70, 0.45); cr.fill()
    cr.rectangle(a, yb - 420, b - a, 140); cr.set_source_rgb(0.42, 0.62, 0.34); cr.fill()      # hedge band
    for k in range(int(a // 120) - 1, int(b // 120) + 2):
        cr.arc(k * 120 + 60, yb - 420, 70, math.pi, 2 * math.pi); cr.set_source_rgb(0.42, 0.62, 0.34); cr.fill()
    sketch_line(cr, [(x, yb - 420 - 40 * abs(math.sin(x / 120.0 * math.pi))) for x in range(int(a), int(b) + 60, 60)], 4, sid=19001, amp=0.6, alpha=0.5)
    cr.rectangle(a, yb - 280, b - a, 120); cr.set_source_rgb(*LAWN); cr.fill()
    for x in trees:
        if a - 700 < x < b + 700: draw_tree(cr, x, yb - 190, t, h=1100, sid=19010 + int(x) % 7 * 10)
    cr.rectangle(a, yb - 160, b - a, max(400, vy1 - yb + 200)); cr.set_source_rgb(*PAVING); cr.fill()    # the path
    sketch_line(cr, [(a, yb - 160), (b, yb - 160)], 5, sid=19002, amp=0.8)
    for k in range(int(a // 240) - 1, int(b // 240) + 2):
        cr.move_to(k * 240, yb - 160); cr.line_to(k * 240 - 120, yb + 400)
    cr.set_source_rgba(0.55, 0.48, 0.40, 0.35); cr.set_line_width(4); cr.stroke()
    for x in lamps:
        if a - 300 < x < b + 300: draw_lamp(cr, x, yb - 150, sid=19050 + int(x) % 5 * 3)
    sketch_line(cr, [(a, yb), (b, yb)], 4, sid=19003, amp=1.0, alpha=0.3)
    cr.restore()

BENCH_SEAT = 230.0                     # the seat's top, above the floor
def draw_bench(cr, x, yb=FLOOR_Y, w=820, sid=19100):
    """a front-on park bench (behind whoever sits on it): backrest slats, seat, iron legs."""
    wood = (0.70, 0.46, 0.28)
    for sd in (-1, 1):
        sketch_line(cr, [(x + sd * (w / 2 - 40), yb), (x + sd * (w / 2 - 40), yb - 560)], 14, sid=sid + (sd > 0), amp=0.3, color=(0.15, 0.15, 0.17))
    for k in range(3):
        y0 = yb - 560 + k * 88
        sketch_rect(cr, x - w / 2, y0, x + w / 2, y0 + 62, 6, sid=sid + 3 + k, fill=wood)
    sketch_rect(cr, x - w / 2 - 20, yb - BENCH_SEAT, x + w / 2 + 20, yb - BENCH_SEAT + 50, 6, sid=sid + 8, fill=lerp(wood, (0, 0, 0), 0.12))

def draw_rose(cr, x, y, s=1.0, ang=0.0, petals=1.0, sid=19200):
    """a single red rose held at its stem's middle (x, y); the bloom up and to the side by ang."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_line(cr, [(0, 110), (4, 0), (-2, -150)], 7, sid=sid, amp=0.3, color=(0.20, 0.50, 0.22))
    sketch_poly(cr, [(2, -40), (50, -70), (70, -40), (30, -30)], 4, sid=sid + 1, fill=(0.35, 0.65, 0.30), amp=0.3)
    r = 46
    if petals > 0.5:
        sketch_circle(cr, -2, -185, r, 6, sid=sid + 2, fill=ROSE_RED)
        sketch_line(cr, [(-26, -190), (-6, -205), (16, -185), (-2, -170), (-12, -186)], 4, sid=sid + 3, amp=0.3)
    else:                                                                   # one petal left, drooping
        sketch_poly(cr, [(-2, -150), (-38, -170), (-30, -205), (-4, -175)], 5, sid=sid + 4, fill=ROSE_RED, amp=0.3)
    cr.restore()

def draw_petal(cr, x, y, ang=0.0, s=1.0, sid=19210):
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_poly(cr, [(-30, 0), (0, -20), (30, 0), (0, 22)], 4, sid=sid, fill=ROSE_RED, amp=0.3)
    cr.restore()

def draw_boombox(cr, x, y, s=1.0, t=0.0, play=0.0, sid=19300):
    """a chunky boombox, centre (x, y): handle, two speakers that thump while it plays."""
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    sketch_line(cr, [(-190, -95), (-170, -150), (170, -150), (190, -95)], 10, sid=sid, amp=0.3)
    sketch_rect(cr, -260, -100, 260, 110, 7, sid=sid + 1, fill=BOOM)
    sketch_rect(cr, -70, -70, 70, 10, 5, sid=sid + 2, fill=(0.55, 0.75, 0.85))
    for k in range(5): sketch_rect(cr, -60 + k * 26, 30, -44 + k * 26, 50, 3, sid=sid + 3 + k, fill=(0.85, 0.85, 0.88))
    th = play * (0.5 + 0.5 * math.sin(t * 2 * math.pi * 2.2)) ** 2
    for sd in (-1, 1):
        sketch_circle(cr, sd * 165, 5, 75 + 7 * th, 6, sid=sid + 10 + (sd > 0), fill=(0.16, 0.16, 0.20))
        sketch_circle(cr, sd * 165, 5, 30 + 4 * th, 4, sid=sid + 12 + (sd > 0), fill=(0.45, 0.46, 0.52))
    cr.restore()

def draw_note(cr, x, y, s=1.0, alpha=1.0, double=False, sid=19320):
    """a music note."""
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    sketch_ellipse(cr, 0, 0, 22, 16, 4, rot=-0.4, sid=sid, fill=INK, alpha=alpha)
    sketch_line(cr, [(18, -4), (18, -80)], 6, sid=sid + 1, amp=0.2, alpha=alpha)
    if double:
        sketch_ellipse(cr, 60, -10, 22, 16, 4, rot=-0.4, sid=sid + 2, fill=INK, alpha=alpha)
        sketch_line(cr, [(78, -14), (78, -90)], 6, sid=sid + 3, amp=0.2, alpha=alpha)
        sketch_line(cr, [(18, -80), (78, -90)], 12, sid=sid + 4, amp=0.2, alpha=alpha)
    else:
        sketch_line(cr, [(18, -80), (44, -56)], 6, sid=sid + 4, amp=0.2, alpha=alpha)
    cr.restore()

def draw_spaghetti(cr, x, y, s=1.0, t=0.0, steam=1.0, sid=19400):
    """a plate of spaghetti and meatballs, plate centre (x, y)."""
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    sketch_ellipse(cr, 0, 0, 190, 48, 6, sid=sid, fill=(1, 1, 1))
    sketch_ellipse(cr, 0, -4, 140, 32, 3, sid=sid + 1, fill=None, alpha=0.4)
    sketch_ellipse(cr, 0, -40, 125, 55, 5, sid=sid + 2, fill=PASTA)
    for k in range(7):
        a0 = k * 0.9
        cr.move_to(-100 + 30 * k, -40 + 20 * math.sin(a0)); cr.curve_to(-60 + 30 * k, -90, -20 + 20 * k, 0, 40 + 10 * k, -50)
    stroke_ink(cr, 3, alpha=0.6); cr.new_path()
    sketch_ellipse(cr, 0, -70, 70, 26, 4, sid=sid + 3, fill=SAUCE)
    for k, (mx, my) in enumerate(((-45, -82), (5, -96), (50, -78))):
        sketch_circle(cr, mx, my, 26, 4, sid=sid + 5 + k, fill=(0.55, 0.30, 0.20))
    cr.restore()
    if steam > 0.01:
        for k in range(3):
            u = (t * 0.6 + k / 3) % 1.0
            xx = x + (-50 + 50 * k) * s + 20 * math.sin(u * 6 + k)
            pts = [(xx + 18 * math.sin(u * 5 + j * 0.9), y - (110 + 60 * j + 160 * u) * s) for j in range(4)]
            sketch_line(cr, pts, 6, sid=sid + 20 + k, amp=0.3, color=(1, 1, 1), alpha=steam * math.sin(math.pi * u) * 0.9)

def draw_noodle(cr, a, b, sag=60.0, sid=19450):
    """one long noodle between two points (two mouths), sagging in the middle."""
    mx, my = (a[0] + b[0]) / 2, max(a[1], b[1]) + sag
    for w, col in ((13, INK), (7, PASTA)):
        cr.move_to(*a); cr.curve_to(a[0] + (mx - a[0]) * 0.5, my, b[0] + (mx - b[0]) * 0.5, my, *b)
        cr.set_source_rgb(*col); cr.set_line_width(w); cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.stroke()

def draw_book(cr, x, y, s=1.0, ang=0.0, sid=19470):
    """an open book seen from the front (its cover toward us), centre (x, y)."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_poly(cr, [(-90, -60), (0, -48), (90, -60), (90, 60), (0, 70), (-90, 60)], 5, sid=sid, fill=(0.36, 0.52, 0.72), amp=0.3)
    sketch_line(cr, [(0, -48), (0, 70)], 4, sid=sid + 1, amp=0.2)
    cr.restore()

def draw_stork(cr, x, y, s=1.0, t=0.0, flap=0.0, facing=-1, mode="fly", beak=0.0, bundle=True, clip=0.0, look=0.0,
               nod=0.0, cap_tip=0.0, sid=19500):
    """a big delivery stork, body centre (x, y), drawn facing left (facing=-1) or right. mode "fly" (legs trailing,
    wings flapping by flap -1..1) or "stand" (long legs down to y + 560*s, wings folded). It wears a blue delivery cap.
    bundle: a swaddled baby hanging from its beak in a knotted cloth. clip 0..1 holds out a clipboard (SIGN HERE) with
    its wing. look -1..1 (head lowered to read the clipboard), nod: a head bob."""
    cr.save(); cr.translate(x, y); cr.scale(s * facing, s)             # drawn facing RIGHT locally
    W = (1, 1, 1); BLK = (0.12, 0.12, 0.14)
    # legs
    if mode == "stand":
        for k, dx in enumerate((-20, 40)):
            sketch_line(cr, [(dx, 60), (dx + 10, 300), (dx, 560)], 8, sid=sid + k, amp=0.3, color=STORK_ORANGE)
            sketch_line(cr, [(dx - 40, 560), (dx + 60, 560)], 8, sid=sid + 2 + k, amp=0.2, color=STORK_ORANGE)
    else:
        for k, dy in enumerate((20, 50)):
            sketch_line(cr, [(-120, dy), (-380, dy + 40), (-470, dy + 30)], 8, sid=sid + k, amp=0.3, color=STORK_ORANGE)
    # far wing
    if mode == "fly":
        _stork_wing(cr, -60 - 330 * math.sin(0.5 + flap * 0.9), (0.88, 0.89, 0.92), sid + 5, x0=-40)
    # tail + body
    sketch_poly(cr, [(-150, -10), (-260, -40), (-250, 30), (-150, 30)], 5, sid=sid + 7, fill=BLK, amp=0.3)
    sketch_ellipse(cr, 0, 0, 175, 95, 6, sid=sid + 8, fill=W)
    if mode == "stand":                                                    # folded wing
        sketch_poly(cr, [(-120, -40), (60, -60), (110, 0), (-40, 60), (-200, 40)], 5, sid=sid + 9, fill=(0.92, 0.93, 0.95), amp=0.3)
        sketch_poly(cr, [(-120, -10), (-200, 40), (-60, 50)], 5, sid=sid + 10, fill=BLK, amp=0.3)
    # neck + head
    hx, hy = 150 + 30 * look, -250 + 70 * look + 18 * nod
    cr.move_to(110, -40); cr.curve_to(170, -120, 120, -180, hx, hy)
    cr.set_source_rgb(*INK); cr.set_line_width(58); cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.stroke()
    cr.move_to(110, -40); cr.curve_to(170, -120, 120, -180, hx, hy)
    cr.set_source_rgb(*W); cr.set_line_width(44); cr.stroke()
    sketch_circle(cr, hx, hy, 58, 6, sid=sid + 11, fill=W)
    ba = 0.25 + 0.5 * look                                                 # beak angle (down when reading)
    bx, by = hx + 50 * math.cos(ba), hy + 50 * math.sin(ba)
    tipx, tipy = bx + 210 * math.cos(ba), by + 210 * math.sin(ba)
    nx, ny = -math.sin(ba), math.cos(ba)
    sketch_poly(cr, [(bx - 12 * nx, by - 12 * ny), (tipx, tipy), (bx + 14 * nx, by + 14 * ny)], 5, sid=sid + 12, fill=STORK_ORANGE, amp=0.2)
    if beak > 0.05:
        sketch_line(cr, [(bx, by), (tipx + 20 * nx * beak, tipy + 60 * ny * beak)], 5, sid=sid + 13, amp=0.2)
    cr.arc(hx + 18, hy - 16, 10, 0, 2 * math.pi); fill_ink(cr); cr.new_path()
    sketch_line(cr, [(hx + 2, hy - 36), (hx + 36, hy - 32)], 5, sid=sid + 14, amp=0.2)
    # the delivery cap
    cr.save(); cr.translate(hx, hy - 40); cr.rotate(-0.15 - 0.6 * cap_tip)
    sketch_poly(cr, [(-58, 0), (-50, -60), (40, -62), (56, 0)], 5, sid=sid + 15, fill=CAP_BLUE, amp=0.3)
    sketch_poly(cr, [(40, 0), (110, 8), (104, 22), (40, 16)], 5, sid=sid + 16, fill=lerp(CAP_BLUE, (0, 0, 0), 0.2), amp=0.2)
    cr.restore()
    # the bundle in the beak (a cloth sling knotted at the tip)
    if bundle:
        kx, ky = bx + 150 * math.cos(ba), by + 150 * math.sin(ba)
        sketch_line(cr, [(kx, ky), (kx - 60, ky + 100)], 6, sid=sid + 17, amp=0.3)
        sketch_line(cr, [(kx, ky), (kx + 60, ky + 100)], 6, sid=sid + 18, amp=0.3)
        sketch_circle(cr, kx, ky, 16, 4, sid=sid + 19, fill=(1, 1, 1))
    # near wing (fly) / clipboard wing (stand)
    if mode == "fly":
        _stork_wing(cr, -40 - 360 * math.sin(0.4 + flap * 0.9), W, sid + 20, x0=0)
    cr.restore()

def _stork_wing(cr, tipy, col, sid, x0=0.0):
    """one flapping wing seen from the side: a long rounded blade from the shoulder to tipy (up < 0 < down),
    white with black flight feathers on the outer third."""
    k = tipy
    root = [(x0 - 90, -10), (x0 + 90, -10)]
    pts = [root[0], (x0 - 150, k * 0.45), (x0 - 130, k * 0.85), (x0 - 40, k), (x0 + 50, k * 0.95), (x0 + 70, k * 0.5), root[1]]
    sketch_poly(cr, pts, 6, sid=sid, fill=col, amp=0.4)
    tipp = [(x0 - 142, k * 0.66), (x0 - 130, k * 0.85), (x0 - 40, k), (x0 + 50, k * 0.95), (x0 + 62, k * 0.66)]
    sketch_poly(cr, tipp, 5, sid=sid + 1, fill=(0.12, 0.12, 0.14), amp=0.3)

def stork_bundle_pt(x, y, s=1.0, facing=-1, look=0.0, nod=0.0):
    """world position of the baby bundle that hangs from the stork's beak (centre of the swaddle)."""
    hx, hy = 150 + 30 * look, -250 + 70 * look + 18 * nod
    ba = 0.25 + 0.5 * look
    bx, by = hx + 50 * math.cos(ba), hy + 50 * math.sin(ba)
    kx, ky = bx + 150 * math.cos(ba), by + 150 * math.sin(ba)
    return (x + facing * kx * s, y + (ky + 165) * s)

def draw_delivery_board(cr, x, y, s=1.0, ang=0.0, signed=0.0, sid=19600):
    """the stork's clipboard: SIGN HERE + an X line; signed 0..1 draws his scribble."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_rect(cr, -150, -190, 150, 190, 6, sid=sid, fill=(0.80, 0.62, 0.42))
    sketch_rect(cr, -125, -160, 125, 170, 4, sid=sid + 1, fill=(1, 1, 1))
    sketch_rect(cr, -50, -205, 50, -170, 4, sid=sid + 2, fill=(0.7, 0.7, 0.74))
    draw_text(cr, "SIGN", 0, -95, 64, color=(30, 30, 34))
    draw_text(cr, "HERE", 0, -25, 64, color=(30, 30, 34))
    draw_text(cr, "X", -95, 85, 50, color=(30, 30, 34))
    sketch_line(cr, [(-70, 105), (100, 105)], 4, sid=sid + 3, amp=0.2)
    if signed > 0.01:
        pts = [(-60 + 160 * u, 85 + 18 * math.sin(u * 30) - 10 * u) for u in [i / 30 * signed for i in range(31)]]
        sketch_line(cr, pts, 4, sid=sid + 4, amp=0.2, color=(0.15, 0.25, 0.65))
    cr.restore()

# ============================================================ day 17 ALT: the house (rom-com montage + breakup)
WALL = (0.97, 0.91, 0.80)
WOODF = (0.80, 0.62, 0.42)
COUCH = (0.42, 0.55, 0.75)
TAPE = (0.98, 0.80, 0.30)

def draw_house_front(cr, x, yb=FLOOR_Y, t=0.0, sid=19700):
    """a little suburban house front (~1300 wide): siding, a red roof, two windows, a front door, a picket fence."""
    w, h = 1300, 900
    sketch_rect(cr, x - w / 2, yb - h, x + w / 2, yb - 100, 6, sid=sid, fill=(0.80, 0.88, 0.95))
    for k in range(1, 9): sketch_line(cr, [(x - w / 2, yb - 100 - k * 95), (x + w / 2, yb - 100 - k * 95)], 2, sid=sid + 1 + k, alpha=0.3)
    sketch_poly(cr, [(x - w / 2 - 80, yb - h + 6), (x, yb - h - 520), (x + w / 2 + 80, yb - h + 6)], 6, sid=sid + 12, fill=(0.80, 0.34, 0.30))
    for k in (-1, 1):
        sketch_rect(cr, x + k * 380 - 130, yb - 700, x + k * 380 + 130, yb - 430, 5, sid=sid + 14 + k, fill=(0.95, 0.92, 0.70))
        sketch_line(cr, [(x + k * 380, yb - 700), (x + k * 380, yb - 430)], 4, sid=sid + 17 + k)
    sketch_rect(cr, x - 110, yb - 520, x + 110, yb - 100, 6, sid=sid + 20, fill=(0.85, 0.30, 0.28))
    cr.arc(x + 70, yb - 300, 12, 0, 2 * math.pi); fill_ink(cr); cr.new_path()

def draw_picket_fence(cr, x0, x1, yb=FLOOR_Y, sid=19740):
    sketch_line(cr, [(x0, yb - 160), (x1, yb - 160)], 8, sid=sid, color=INK)
    for k in range(int((x1 - x0) // 90) + 1):
        xx = x0 + k * 90
        sketch_poly(cr, [(xx - 28, yb), (xx - 28, yb - 230), (xx, yb - 270), (xx + 28, yb - 230), (xx + 28, yb)], 4, sid=sid + 1 + k % 9, fill=(1, 1, 1), amp=0.3)

def draw_sold_sign(cr, x, yb=FLOOR_Y, drop=1.0, sid=19760):
    """a real-estate sign on a post: drop 0..1 slams it down from above."""
    yo = -900 * (1 - drop) ** 2
    cr.save(); cr.translate(0, yo)
    sketch_line(cr, [(x - 150, yb), (x - 150, yb - 620)], 10, sid=sid, color=(0.35, 0.25, 0.18))
    sketch_line(cr, [(x - 150, yb - 600), (x + 170, yb - 600)], 10, sid=sid + 1, color=(0.35, 0.25, 0.18))
    sketch_rect(cr, x - 110, yb - 580, x + 160, yb - 400, 6, sid=sid + 2, fill=(1, 1, 1))
    draw_text(cr, "FOR SALE", x + 25, yb - 530, 40, color=(30, 30, 34))
    cr.save(); cr.translate(x + 25, yb - 455); cr.rotate(-0.12)
    sketch_rect(cr, -150, -45, 150, 45, 5, sid=sid + 3, fill=(0.88, 0.18, 0.20))
    draw_text(cr, "SOLD!", 0, 0, 70, color=(255, 255, 255))
    cr.restore()
    cr.restore()

def draw_room(cr, t, x0, x1, yb=FLOOR_Y, door_x=None, door_open=0.0, frame_x=None, frame_fall=0.0, win_x=None, kitchen_x=None):
    """the inside of his house: a cream wall, a wooden floor, a baseboard, a window, a door (open_ 0..1), a picture
    frame (frame_fall 0..1 drops it to the floor), and from kitchen_x on: tiles + counter."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    a, b = max(x0, vx0), min(x1, vx1)
    if b <= a: return
    cr.rectangle(a, vy0 - 10, b - a, yb - 140 - vy0 + 10); cr.set_source_rgb(*WALL); cr.fill()
    cr.rectangle(a, yb - 140, b - a, max(400, vy1 - yb + 200)); cr.set_source_rgb(*WOODF); cr.fill()
    for k in range(int(a // 200) - 1, int(b // 200) + 2):
        cr.move_to(k * 200, yb - 140); cr.line_to(k * 200 - 160, yb + 500)
    cr.set_source_rgba(0.45, 0.32, 0.20, 0.35); cr.set_line_width(4); cr.stroke()
    sketch_rect(cr, a - 10, yb - 180, b + 10, yb - 140, 5, sid=19800, fill=(1, 1, 1))
    if kitchen_x is not None and kitchen_x < b:
        ka = max(a, kitchen_x)
        cr.rectangle(ka, vy0 - 10, b - ka, yb - 180 - vy0 + 10); cr.set_source_rgb(0.86, 0.93, 0.92); cr.fill()
        for k in range(int(ka // 90), int(b // 90) + 1):
            for j in range(int((yb - 1000) // 90), int((yb - 180) // 90)):
                cr.rectangle(k * 90, j * 90, 90, 90)
        cr.set_source_rgba(0.5, 0.6, 0.6, 0.25); cr.set_line_width(2); cr.stroke()
    if win_x is not None and a - 500 < win_x < b + 500:
        sketch_rect(cr, win_x - 260, yb - 1150, win_x + 260, yb - 650, 7, sid=19801, fill=(0.98, 0.78, 0.60))
        sketch_line(cr, [(win_x, yb - 1150), (win_x, yb - 650)], 6, sid=19802)
        sketch_line(cr, [(win_x - 260, yb - 900), (win_x + 260, yb - 900)], 6, sid=19803)
        for sd in (-1, 1):
            sketch_poly(cr, [(win_x + sd * 250, yb - 1190), (win_x + sd * 340, yb - 1190), (win_x + sd * 360, yb - 600), (win_x + sd * 270, yb - 640)],
                        5, sid=19804 + (sd > 0), fill=(0.90, 0.45, 0.42))
    if door_x is not None and a - 400 < door_x < b + 400:
        sketch_rect(cr, door_x - 200, yb - 1060, door_x + 200, yb - 140, 7, sid=19810, fill=(0.98, 0.86, 0.62) if door_open > 0.05 else (0.62, 0.42, 0.28))
        if door_open > 0.05:                                              # the door swung in, toward the wall on the left
            w_ = 400 * (1 - door_open) + 50 * door_open
            sketch_rect(cr, door_x - 200, yb - 1060, door_x - 200 + w_, yb - 140, 6, sid=19811, fill=(0.62, 0.42, 0.28))
        else:
            cr.arc(door_x + 140, yb - 600, 16, 0, 2 * math.pi); fill_ink(cr); cr.new_path()
    if frame_x is not None and a - 400 < frame_x < b + 400:
        y = lerp(yb - 1000, yb - 200, frame_fall ** 2)
        cr.save(); cr.translate(frame_x, y); cr.rotate(0.6 * frame_fall)
        sketch_rect(cr, -150, -110, 150, 110, 7, sid=19812, fill=(0.70, 0.52, 0.35))
        sketch_rect(cr, -115, -80, 115, 80, 4, sid=19813, fill=(0.98, 0.95, 0.90))
        _photo_fam(cr, 0, 40, 0.5)
        if frame_fall >= 1.0:
            for k in range(4): sketch_line(cr, [(-60 + 40 * k, -80), (-20 + 30 * k, 80)], 3, sid=19814 + k, alpha=0.7)
        cr.restore()

def _photo_fam(cr, x, y, s=1.0):
    """three tiny stick figures (him, her with long hair, the baby) for photos."""
    for k, (dx, hair) in enumerate(((-60, False), (60, True))):
        hx = x + dx * s
        if hair: sketch_circle(cr, hx, y - 120 * s, 34 * s, 3, sid=19830, fill=(0.62, 0.28, 0.16))
        sketch_circle(cr, hx, y - 120 * s, 26 * s, 3, sid=19831 + k, fill=(1, 1, 1))
        sketch_line(cr, [(hx, y - 94 * s), (hx, y - 30 * s)], 3, sid=19833 + k, amp=0.2)
        sketch_line(cr, [(hx - 20 * s, y), (hx, y - 30 * s), (hx + 20 * s, y)], 3, sid=19835 + k, amp=0.2)
    sketch_ellipse(cr, x, y - 60 * s, 26 * s, 16 * s, 3, sid=19837, fill=(0.70, 0.84, 0.96))

def draw_couch(cr, x, yb=FLOOR_Y, w=820, tape=0.0, sid=19840):
    """a front-on couch whose seat top is BENCH_SEAT above the floor (people sit 'on' it). tape 0..1 runs a strip of
    masking tape down the middle."""
    sketch_rect(cr, x - w / 2, yb - 640, x + w / 2, yb - BENCH_SEAT, 7, sid=sid, fill=COUCH)
    for sd in (-1, 1): sketch_rect(cr, x + sd * (w / 2) - 70, yb - 420, x + sd * (w / 2) + 70, yb - 60, 7, sid=sid + 1 + (sd > 0), fill=lerp(COUCH, (0, 0, 0), 0.12))
    sketch_rect(cr, x - w / 2 + 60, yb - BENCH_SEAT, x + w / 2 - 60, yb - 60, 7, sid=sid + 3, fill=lerp(COUCH, (1, 1, 1), 0.12))
    sketch_line(cr, [(x, yb - 600), (x, yb - BENCH_SEAT)], 3, sid=sid + 4, alpha=0.4)
    for sd in (-1, 1): sketch_line(cr, [(x + sd * 300, yb - 60), (x + sd * 300, yb)], 10, sid=sid + 5 + (sd > 0), amp=0.2)
    if tape > 0.01:
        y0 = yb - 650; y1 = lerp(y0, yb - 40, tape)
        sketch_rect(cr, x - 22, y0, x + 22, y1, 3, sid=sid + 8, fill=TAPE, amp=0.4)

def draw_couch_front(cr, x, yb=FLOOR_Y, w=820, tape=0.0, sid=19860):
    """the couch's seat front (drawn OVER sitters' legs is not needed - kept empty for draw-order symmetry)."""
    return

def draw_tv(cr, x, yb=FLOOR_Y, t=0.0, screen="game", text_lines=None, glow=1.0, sid=19870):
    """a TV on a low stand with a console. screen: "game" (a little platformer that blinks), "off", or "text"
    (text_lines on a dark screen, with a blinking cursor). Screen centre = (x, yb - 600), 460 x 300."""
    sketch_rect(cr, x - 330, yb - 300, x + 330, yb - 60, 6, sid=sid, fill=(0.55, 0.40, 0.28))
    for sd in (-1, 1): sketch_line(cr, [(x + sd * 300, yb - 60), (x + sd * 300, yb)], 10, sid=sid + 1 + (sd > 0), amp=0.2)
    sketch_rect(cr, x + 60, yb - 360, x + 260, yb - 300, 5, sid=sid + 3, fill=(0.18, 0.18, 0.22))
    cr.arc(x + 230, yb - 330, 8, 0, 2 * math.pi); cr.set_source_rgb(0.3, 0.9, 0.4); cr.fill()
    sketch_line(cr, [(x, yb - 300), (x, yb - 420)], 14, sid=sid + 4, amp=0.2)
    sketch_rect(cr, x - 260, yb - 780, x + 260, yb - 420, 8, sid=sid + 5, fill=(0.14, 0.14, 0.18))
    sx0, sy0, sx1, sy1 = x - 230, yb - 750, x + 230, yb - 450
    if screen == "game":
        cr.rectangle(sx0, sy0, sx1 - sx0, sy1 - sy0); cr.set_source_rgb(0.35, 0.65, 0.98); cr.fill()
        cr.rectangle(sx0, sy1 - 60, sx1 - sx0, 60); cr.set_source_rgb(0.35, 0.75, 0.30); cr.fill()
        px = sx0 + 60 + ((t * 120) % 300); py = sy1 - 100 - 60 * abs(math.sin(t * 5))
        cr.rectangle(px, py, 36, 40); cr.set_source_rgb(0.95, 0.30, 0.25); cr.fill()
        for k in range(3):
            cx = sx0 + ((k * 160 - t * 90) % (sx1 - sx0))
            cr.rectangle(cx, sy1 - 170, 40, 40); cr.set_source_rgb(1.0, 0.80, 0.25); cr.fill()
        if int(t * 4) % 2 == 0:
            cr.arc(px + 150, py - 20, 10, 0, 2 * math.pi); cr.set_source_rgb(1, 1, 1); cr.fill()
    elif screen == "text":
        cr.rectangle(sx0, sy0, sx1 - sx0, sy1 - sy0); cr.set_source_rgb(0.08, 0.10, 0.18); cr.fill()
        lines = text_lines or ("TELL ME", "WHAT TO DO", "NEXT IN THE", "COMMENTS")
        n = len(lines)
        for i, ln in enumerate(lines):
            draw_text(cr, ln, x, sy0 + 50 + i * 58, 52, color=(255, 255, 255))
        if int(t * 2.5) % 2 == 0:
            cr.rectangle(x + 150, sy0 + 30 + (n - 1) * 58, 18, 44); cr.set_source_rgb(1, 1, 1); cr.fill()
    cr.rectangle(sx0, sy0, sx1 - sx0, sy1 - sy0); cr.set_source_rgba(1, 1, 1, 0.06); cr.fill()

def draw_controller(cr, x, y, s=1.0, ang=0.0, sid=19890):
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_poly(cr, [(-80, -20), (80, -20), (95, 35), (55, 40), (35, 15), (-35, 15), (-55, 40), (-95, 35)], 5, sid=sid, fill=(0.22, 0.22, 0.27), amp=0.3)
    for k, c in enumerate(((0.95, 0.3, 0.3), (0.3, 0.8, 0.4))):
        cr.arc(45 + 18 * k, -2 - 8 * k, 8, 0, 2 * math.pi); cr.set_source_rgb(*c); cr.fill()
    cr.restore()

def draw_thermostat(cr, x, y, val=70, off=0.0, t=0.0, sid=19900):
    """a round wall thermostat showing val; off 0..1 = the dial has popped off and flies down-right."""
    sketch_rect(cr, x - 110, y - 140, x + 110, y + 140, 6, sid=sid, fill=(0.96, 0.96, 0.96))
    hot = max(0.0, min(1.0, (val - 60) / 20))
    if off < 0.01:
        sketch_circle(cr, x, y, 85, 6, sid=sid + 1, fill=lerp((0.55, 0.75, 1.0), (1.0, 0.45, 0.35), hot))
        draw_text(cr, f"{int(round(val))}", x, y, 66, color=(30, 30, 34))
    else:
        cr.arc(x, y, 30, 0, 2 * math.pi); fill_ink(cr); cr.new_path()
        for k in range(3): sketch_line(cr, [(x - 20 + 20 * k, y + 30), (x - 30 + 25 * k, y + 70)], 4, sid=sid + 5 + k)
        u = off
        dx, dy = x + 250 * u, y - 200 * math.sin(math.pi * min(1, u)) + 500 * u * u
        cr.save(); cr.translate(dx, dy); cr.rotate(8 * u)
        sketch_circle(cr, 0, 0, 85, 6, sid=sid + 1, fill=lerp((0.55, 0.75, 1.0), (1.0, 0.45, 0.35), hot))
        cr.restore()

def draw_suitcase(cr, x, y, s=1.0, sid=19920):
    """hanging from a hand at (x, y)."""
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    sketch_line(cr, [(-40, 10), (-40, -20), (40, -20), (40, 10)], 7, sid=sid, amp=0.2)
    sketch_rect(cr, -150, 10, 150, 230, 7, sid=sid + 1, fill=(0.82, 0.32, 0.36))
    sketch_line(cr, [(-150, 60), (150, 60)], 4, sid=sid + 2, alpha=0.5)
    cr.restore()

def draw_tape_roll(cr, x, y, s=1.0, sid=19930):
    sketch_circle(cr, x, y, 46 * s, 6, sid=sid, fill=TAPE)
    sketch_circle(cr, x, y, 20 * s, 4, sid=sid + 1, fill=WALL)

def draw_bubble(cr, x, y, w, h, tail, text=None, scribble=0.0, t=0.0, angry=False, sid=19940):
    """a speech bubble centred (x, y), w x h, tail pointing at `tail`. text, or angry scribble (0..1 density)."""
    fillc = (1.0, 0.92, 0.90) if angry else (1, 1, 1)
    sketch_poly(cr, [(x - 50, y + h / 2 - 10), tail, (x + 30, y + h / 2 - 10)], 6, sid=sid, fill=fillc, amp=0.4)
    sketch_ellipse(cr, x, y, w / 2, h / 2, 7, sid=sid + 1, fill=fillc)
    if text:
        draw_text(cr, text, x, y, min(90, h * 0.32), color=(30, 30, 34), max_w=w * 0.82)
    if scribble > 0.01:
        n = int(10 + 30 * scribble)
        pts = []
        for k in range(n):
            u = k / n
            pts.append((x - w * 0.32 + w * 0.64 * ((k * 0.37 + 0.13 * math.sin(k + t * 9)) % 1.0),
                        y - h * 0.28 + h * 0.56 * ((k * 0.61 + 0.1 * math.cos(k * 1.7 + t * 11)) % 1.0)))
        sketch_line(cr, pts, 6, sid=sid + 2, amp=0.6, color=(0.80, 0.12, 0.12))
        for k in range(3):                                                 # grawlix symbols, drawn (no words)
            gx = x - w * 0.25 + k * w * 0.25; gy = y + h * 0.05 * math.sin(t * 13 + k)
            if k == 0: cr.arc(gx, gy, h * 0.08, 0, 2 * math.pi); stroke_ink(cr, 5); cr.new_path()
            if k == 1: draw_star(cr, gx, gy, h * 0.1, color=(0.95, 0.75, 0.2))
            if k == 2: sketch_line(cr, [(gx, gy - h * 0.12), (gx + h * 0.05, gy), (gx - h * 0.05, gy + 4), (gx, gy + h * 0.12)], 6, sid=sid + 9, color=(0.95, 0.6, 0.1))

def draw_fridge(cr, x, yb=FLOOR_Y, photo=0.0, sid=19960):
    """a fridge; photo 0..1 = the family photo stuck on it (0 = not there, 1 = on)."""
    sketch_rect(cr, x - 220, yb - 1150, x + 220, yb - 60, 7, sid=sid, fill=(0.94, 0.96, 0.98))
    sketch_line(cr, [(x - 220, yb - 760), (x + 220, yb - 760)], 5, sid=sid + 1)
    for yy in ((yb - 1000, yb - 880), (yb - 700, yb - 450)):
        sketch_line(cr, [(x - 170, yy[0]), (x - 170, yy[1])], 9, sid=sid + 2, amp=0.2)
    for k, (mx, my, c) in enumerate(((x + 60, yb - 1050, (0.95, 0.35, 0.30)), (x + 140, yb - 940, (0.30, 0.60, 0.95)))):
        sketch_circle(cr, mx, my, 18, 3, sid=sid + 3 + k, fill=c)
    if photo > 0.01:
        cr.save(); cr.translate(x + 40, yb - 560); cr.rotate(-0.06)
        sketch_rect(cr, -110, -90, 110, 90, 5, sid=sid + 6, fill=(1, 1, 1))
        _photo_fam(cr, 0, 70, 0.55)
        sketch_circle(cr, 0, -88, 16, 3, sid=sid + 7, fill=(0.95, 0.80, 0.25))
        cr.restore()

def draw_sink_counter(cr, x, yb=FLOOR_Y, n=26, extra=0, wobble=0.0, t=0.0, sid=20000):
    """a kitchen counter with a sink and a leaning tower of dirty plates (n plates + `extra` freshly added ones on top);
    wobble 0..1 makes the tower sway."""
    sketch_rect(cr, x - 260, yb - 430, x + 260, yb - 40, 7, sid=sid, fill=(0.80, 0.66, 0.50))
    for k in (-1, 1): sketch_rect(cr, x + k * 130 - 110, yb - 380, x + k * 130 + 110, yb - 80, 4, sid=sid + 1 + (k > 0), fill=(0.86, 0.72, 0.56))
    sketch_rect(cr, x - 290, yb - 460, x + 290, yb - 420, 6, sid=sid + 3, fill=(0.92, 0.92, 0.94))
    sketch_line(cr, [(x + 150, yb - 460), (x + 150, yb - 560), (x + 60, yb - 570)], 10, sid=sid + 4, amp=0.2, color=(0.6, 0.62, 0.66))
    y = yb - 470; px = x - 40
    for k in range(n + extra):
        sway = wobble * 4.0 * k * math.sin(t * 9) + 1.6 * k * math.sin(k * 0.7)
        cx = px + sway + (6 * math.sin(k * 2.1))
        col = (1, 1, 1) if k % 3 else (0.92, 0.95, 1.0)
        sketch_ellipse(cr, cx, y, 120, 20, 4, sid=sid + 10 + k % 30, fill=col)
        if k % 4 == 1:
            cr.arc(cx - 40, y - 4, 7, 0, 2 * math.pi); cr.set_source_rgb(0.86, 0.26, 0.16); cr.fill()
        y -= 24
    for k in range(3):
        sketch_rect(cr, x + 150 + k * 40, yb - 520 - (k % 2) * 30, x + 180 + k * 40, yb - 460, 3, sid=sid + 50 + k, fill=(0.95, 0.80, 0.45))
    for k in range(3):                                                      # flies (stink)
        u = t * 2 + k
        cr.arc(px + 80 * math.sin(u * 1.7), y - 30 + 25 * math.cos(u * 2.3), 6, 0, 2 * math.pi); fill_ink(cr); cr.new_path()

def draw_plate(cr, x, y, s=1.0, sid=20060):
    sketch_ellipse(cr, x, y, 120 * s, 20 * s, 4, sid=sid, fill=(1, 1, 1))
    cr.arc(x - 30 * s, y - 4 * s, 7 * s, 0, 2 * math.pi); cr.set_source_rgb(0.86, 0.26, 0.16); cr.fill()

def draw_vacuum(cr, hx, hy, bx, yb=FLOOR_Y, on=0.0, t=0.0, sid=20070):
    """an upright vacuum: handle in the hand at (hx, hy), the head on the floor at bx."""
    sketch_line(cr, [(hx, hy), (bx, yb - 120)], 12, sid=sid, amp=0.2, color=(0.30, 0.30, 0.34))
    sketch_rect(cr, bx - 60, yb - 330 + 4 * on * math.sin(t * 60), bx + 50, yb - 110, 6, sid=sid + 1, fill=(0.88, 0.30, 0.40))
    sketch_rect(cr, bx - 110, yb - 120, bx + 110, yb - 40, 6, sid=sid + 2, fill=(0.35, 0.35, 0.40))
    for k in (-1, 1): sketch_circle(cr, bx + k * 80, yb - 30, 22, 4, sid=sid + 3 + (k > 0), fill=(0.15, 0.15, 0.18))
    if on > 0.01:
        for k in range(3):
            u = (t * 3 + k / 3) % 1.0
            sketch_line(cr, [(bx - 120 - 60 * u, yb - 60 - 30 * k), (bx - 160 - 60 * u, yb - 70 - 30 * k)], 4, sid=sid + 6 + k, alpha=1 - u)

def draw_outlet(cr, x, y, sid=20090):
    sketch_rect(cr, x - 40, y - 60, x + 40, y + 60, 4, sid=sid, fill=(1, 1, 1))
    for k in (-1, 1): sketch_line(cr, [(x - 12, y + k * 25 - 8), (x - 12, y + k * 25 + 8)], 4, sid=sid + 1); sketch_line(cr, [(x + 12, y + k * 25 - 8), (x + 12, y + k * 25 + 8)], 4, sid=sid + 2)

def draw_wall_clock(cr, x, y, hour=3.0, minute=0.0, sid=20100):
    sketch_circle(cr, x, y, 110, 7, sid=sid, fill=(1, 1, 1))
    for k in range(12):
        a = k * math.pi / 6
        sketch_line(cr, [(x + 85 * math.sin(a), y - 85 * math.cos(a)), (x + 98 * math.sin(a), y - 98 * math.cos(a))], 4, sid=sid + 1 + k, amp=0.1)
    ah = (hour % 12 + minute / 60) * math.pi / 6; am = minute * math.pi / 30
    sketch_line(cr, [(x, y), (x + 55 * math.sin(ah), y - 55 * math.cos(ah))], 9, sid=sid + 20, amp=0.1)
    sketch_line(cr, [(x, y), (x + 85 * math.sin(am), y - 85 * math.cos(am))], 6, sid=sid + 21, amp=0.1)

def draw_side_lamp(cr, x, yb=FLOOR_Y, on=0.0, glow=None, sid=20130):
    sketch_rect(cr, x - 110, yb - 380, x + 110, yb - 340, 5, sid=sid, fill=(0.55, 0.40, 0.28))
    for k in (-1, 1): sketch_line(cr, [(x + k * 90, yb - 340), (x + k * 90, yb)], 8, sid=sid + 1 + (k > 0), amp=0.2)
    sketch_line(cr, [(x, yb - 380), (x, yb - 600)], 8, sid=sid + 3, amp=0.2)
    g = on if glow is None else glow
    if g > 0.01:
        cr.arc(x, yb - 640, 420, 0, 2 * math.pi); cr.set_source_rgba(1.0, 0.85, 0.45, 0.25 * g); cr.fill()
    sketch_poly(cr, [(x - 70, yb - 720), (x + 70, yb - 720), (x + 120, yb - 590), (x - 120, yb - 590)], 6, sid=sid + 4,
                fill=lerp((0.78, 0.74, 0.62), (1.0, 0.93, 0.62), on))

# ------------------------------------------------------------------ day 18: the dinosaur age ---
PRE_DAY = (0.99, 0.86, 0.62)          # warm prehistoric sky
PRE_DAY_HI = (0.96, 0.72, 0.50)
MOD_DAY = (0.74, 0.87, 0.98)
MOD_DAY_HI = (0.58, 0.77, 0.96)
NIGHT = (0.10, 0.12, 0.26)
FERN = (0.36, 0.62, 0.30)
FERN_D = (0.26, 0.48, 0.24)
ASH_SKY = (0.62, 0.46, 0.38)

def draw_fern(cr, x, yb=FLOOR_Y, h=600.0, g=1.0, t=0.0, lean=0.0, flat=0.0, col=FERN, sid=21000):
    """a giant prehistoric fern: 5 arching fronds out of one clump. g 0..1 = grown; flat 0..1 = blown flat (to the left)."""
    if g < 0.02: return
    h = h * g
    for k in range(5):
        a = -math.pi / 2 + (k - 2) * 0.42 + lean + 0.04 * math.sin(t * 1.1 + k + x * 0.01)
        a = lerp(a, -math.pi + 0.15 + 0.05 * k, flat)
        L_ = h * (0.75 + 0.25 * (k % 2)) * (1 - 0.45 * flat)
        pts = []
        for i in range(9):
            u = i / 8
            bend = a + 0.9 * u * u * (1 if math.cos(a) >= 0 else -1) * (1 - flat)
            px = x + math.cos(a) * L_ * u + math.cos(bend) * 0.0
            py = yb + math.sin(a) * L_ * u + (L_ * 0.35 * u * u) * (1 - flat)
            pts.append((px, py))
        sketch_line(cr, pts, 7, sid=sid + k, amp=0.5, color=lerp(col, (0.30, 0.25, 0.20), flat * 0.6))
        for i in range(1, 8):
            u = i / 8; px, py = pts[i]; qx, qy = pts[i + 1]
            ang = math.atan2(qy - py, qx - px); ll = 90 * g * (1 - u * 0.6)
            for sd in (-1, 1):
                ex_, ey_ = px + math.cos(ang + sd * 1.1) * ll, py + math.sin(ang + sd * 1.1) * ll
                cr.move_to(px, py); cr.line_to(ex_, ey_)
        cr.set_source_rgb(*lerp(col, (0.30, 0.25, 0.20), flat * 0.6)); cr.set_line_width(10); cr.set_line_cap(1); cr.stroke()

def draw_cycad(cr, x, yb=FLOOR_Y, h=520.0, g=1.0, t=0.0, sid=21020):
    """a stubby pineapple-trunk cycad with a crown of stiff leaves."""
    if g < 0.02: return
    h *= g; w = 70 * g
    sketch_poly(cr, [(x - w, yb), (x - w * 0.8, yb - h), (x + w * 0.8, yb - h), (x + w, yb)], 6, sid=sid, fill=(0.62, 0.46, 0.30))
    for j in range(1, 6):
        yy = yb - h * j / 6
        cr.move_to(x - w * 0.9, yy); cr.line_to(x + w * 0.9, yy - 18)
    stroke_ink(cr, 3, alpha=0.5)
    for k in range(7):
        a = -math.pi / 2 + (k - 3) * 0.38 + 0.03 * math.sin(t + k)
        L_ = 330 * g
        tip = (x + math.cos(a) * L_, yb - h + math.sin(a) * L_ * 0.8 + 60 * g * abs(k - 3) / 3)
        sketch_poly(cr, [(x - 12, yb - h), ((x + tip[0]) / 2 + 20 * math.sin(a), (yb - h + tip[1]) / 2 - 22), tip,
                         ((x + tip[0]) / 2 - 20 * math.sin(a), (yb - h + tip[1]) / 2 + 22), (x + 12, yb - h)], 5, sid=sid + 1 + k, fill=FERN, amp=0.5)

def draw_pterodactyl(cr, x, y, s=1.0, flap=0.0, facing=1, sid=21040):
    """a flying pterodactyl seen from the side, centre (x, y), facing right (facing=1)."""
    cr.save(); cr.translate(x, y); cr.scale(s * facing, s)
    wy = -130 * math.sin(flap)
    for sd, col in ((-1, (0.66, 0.50, 0.44)), (1, (0.78, 0.60, 0.52))):
        sketch_poly(cr, [(-40, 0), (-60 + 30 * sd, wy - 20), (-200, wy * 0.7 + 40), (40, 10)], 5, sid=sid + (sd > 0), fill=col, amp=0.4)
    sketch_ellipse(cr, 0, 0, 80, 30, 5, sid=sid + 2, fill=(0.78, 0.60, 0.52))
    sketch_poly(cr, [(60, -30), (110, -40), (230, -10), (110, 0), (70, 10)], 5, sid=sid + 3, fill=(0.78, 0.60, 0.52), amp=0.3)
    sketch_poly(cr, [(80, -32), (20, -80), (70, -38)], 4, sid=sid + 4, fill=(0.78, 0.60, 0.52), amp=0.3)
    cr.arc(100, -24, 6, 0, 2 * math.pi); fill_ink(cr); cr.new_path()
    cr.restore()

def draw_meteor(cr, x, y, r, t=0.0, trail=1.0, sid=21050):
    """a giant flaming meteor at (x, y) radius r, coming down from the upper left; trail runs off up-left."""
    for k in range(7, 0, -1):                                           # fire trail (tapers, runs off-screen)
        u = k / 7
        cx, cy = x - 3.0 * r * u * trail, y - 2.2 * r * u * trail
        rr = r * (1.25 - 0.55 * u) * (1 + 0.06 * math.sin(t * 20 + k))
        col = lerp((1.0, 0.92, 0.45), (0.95, 0.35, 0.15), u)
        cr.arc(cx, cy, rr, 0, 2 * math.pi); cr.set_source_rgba(col[0], col[1], col[2], 0.85 - 0.5 * u); cr.fill()
    cr.arc(x, y, r * 1.35, 0, 2 * math.pi); cr.set_source_rgba(1.0, 0.85, 0.40, 0.55); cr.fill()
    sketch_circle(cr, x, y, r, max(4, r * 0.05), sid=sid, fill=(0.42, 0.30, 0.26))
    for k in range(5):
        a = k * 1.3 + 0.4
        cr.arc(x + math.cos(a) * r * 0.5, y + math.sin(a) * r * 0.5, r * 0.14, 0, 2 * math.pi)
    cr.set_source_rgba(0.25, 0.17, 0.14, 0.8); cr.fill()
    cr.arc(x + r * 0.3, y + r * 0.3, r * 0.6, -0.4, 1.9); cr.set_source_rgba(1.0, 0.55, 0.2, 0.6); cr.set_line_width(r * 0.14); cr.stroke()

def draw_umbrella(cr, x, y, s=1.0, open_=1.0, burnt=0.0, crumble=0.0, ang=0.0, sid=21060):
    """a small black umbrella held at the handle (x, y); open_ 0..1; burnt 1 = only the bare smoking ribs + shaft;
    crumble 0..1 = the skeleton falls apart into ash."""
    if crumble >= 1.0: return
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    al = 1.0 - crumble
    sketch_line(cr, [(0, 0), (0, -360)], 7, sid=sid, amp=0.2, alpha=al)
    cr.arc(-22, 0, 22, 0, math.pi); stroke_ink(cr, 7, alpha=al)
    w = 60 + 260 * open_; top = -470 + 40 * (1 - open_)
    if burnt < 0.5:
        pts = [(0, top - 20)]
        for k in range(9):
            u = k / 8; xx = -w + 2 * w * u
            pts.append((xx, top + 110 * open_ + (0 if k % 2 == 0 else -18) + 90 * (1 - open_) * (1 - abs(2 * u - 1))))
        sketch_poly(cr, [(0, top - 20)] + pts[1:], 6, sid=sid + 1, fill=(0.14, 0.14, 0.18))
        sketch_line(cr, [(0, top - 20), (0, top - 70)], 7, sid=sid + 2, amp=0.2)
    else:
        for k in range(5):                                             # bare ribs
            u = k / 4; xx = -w + 2 * w * u
            dy = 40 * crumble * (k % 2 + 1)
            sketch_line(cr, [(0, top - 10), ((xx) * 0.5, top + 20 + dy), (xx, top + 120 + dy * 2)], 5, sid=sid + 10 + k, amp=0.5, alpha=al)
        for k in range(3):
            u = (t_glob(sid) * 0.6 + k / 3) % 1.0
            draw_smoke_puff(cr, -40 + 50 * k, top - 60 - 220 * u, 30 + 40 * u, alpha=(1 - u) * 0.7 * al, dark=0.6)
    cr.restore()

_T_GLOB = [0.0]
def t_glob(_sid=0): return _T_GLOB[0]

def draw_cave_rock(cr, x, yb=FLOOR_Y, part="back", sid=21080):
    """a big boulder hill with a small cave opening at the bottom-left; part "back" = the rock + the dark opening,
    "rim" = the opening's top lip (drawn over things inside). Opening: x-430..x-80, up to yb-620."""
    if part == "back":
        sketch_poly(cr, [(x - 700, yb), (x - 620, yb - 700), (x - 300, yb - 1150), (x + 200, yb - 1300), (x + 700, yb - 1100),
                         (x + 1000, yb - 600), (x + 1100, yb)], 8, sid=sid, fill=(0.66, 0.60, 0.54))
        for k, (a, b) in enumerate((((x - 100, yb - 1000), (x + 300, yb - 900)), ((x + 400, yb - 700), (x + 700, yb - 500)),
                                    ((x - 500, yb - 860), (x - 320, yb - 940)))):
            sketch_line(cr, [a, b], 4, sid=sid + 1 + k, alpha=0.5)
        cr.move_to(x - 450, yb); cr.curve_to(x - 450, yb - 640, x - 60, yb - 640, x - 60, yb); cr.close_path()
        cr.set_source_rgb(0.16, 0.14, 0.14); cr.fill()
    else:
        cr.move_to(x - 470, yb); cr.curve_to(x - 470, yb - 670, x - 40, yb - 670, x - 40, yb)
        stroke_ink(cr, 9)

def draw_log(cr, x, yb=FLOOR_Y, smash=0.0, sid=21090):
    """a fallen tree trunk lying across the path (~420 wide, 150 tall); smash 0..1 flattens it into splinters."""
    if smash < 0.5:
        sketch_rect(cr, x - 210, yb - 150, x + 210, yb, 7, sid=sid, fill=(0.58, 0.40, 0.26))
        sketch_ellipse(cr, x + 210, yb - 75, 40, 75, 6, sid=sid + 1, fill=(0.86, 0.70, 0.48))
        sketch_ellipse(cr, x + 210, yb - 75, 16, 34, 3, sid=sid + 2, fill=(0.86, 0.70, 0.48))
        for k in range(3): sketch_line(cr, [(x - 160 + 120 * k, yb - 110), (x - 80 + 120 * k, yb - 100)], 3, sid=sid + 3 + k, alpha=0.5)
    else:
        for k in range(7):
            xx = x - 260 + 85 * k
            sketch_poly(cr, [(xx, yb), (xx + 30, yb - 40 - 25 * (k % 3)), (xx + 70, yb)], 5, sid=sid + 10 + k, fill=(0.58, 0.40, 0.26), amp=0.4)

def draw_puddle_rings(cr, x, y, rx, t, hits, sid=21100):
    """a little puddle on the ground with ripple rings that spread from every footfall time in hits."""
    sketch_ellipse(cr, x, y, rx, rx * 0.22, 5, sid=sid, fill=(0.62, 0.78, 0.90))
    cr.save(); cr.translate(x, y); cr.scale(1.0, 0.22)
    cr.arc(0, 0, rx - 4, 0, 2 * math.pi); cr.restore(); cr.save(); cr.clip()
    for th in hits:
        u = (t - th) / 1.1
        if 0 <= u < 1:
            for j in range(3):
                r_ = rx * (0.15 + 0.9 * u) - j * 30
                if r_ > 4:
                    cr.save(); cr.translate(x, y); cr.scale(1.0, 0.22); cr.arc(0, 0, r_, 0, 2 * math.pi); cr.restore()
                    cr.set_source_rgba(1, 1, 1, 0.9 * (1 - u)); cr.set_line_width(5); cr.stroke()
    cr.restore()

def draw_trex(cr, X, st, t, face=1, pitch=0.0, blink=0.0):
    """the friendly T. rex (draw_dino) placed with its near foot at world x X, facing right (face=1) or left (-1),
    pitched forward around the hip by `pitch` rad (head goes down). st as DINO (x is ignored)."""
    s = st["s"]; d = dict(st); d["x"] = 0.0
    cr.save(); cr.translate(X, 0); cr.scale(-face, 1)
    if abs(pitch) > 1e-4:
        hx, hy = 40 * s, FLOOR_Y - 400 * s
        cr.translate(hx, hy); cr.rotate(-pitch); cr.translate(-hx, -hy)
    draw_dino(cr, d, t, blink=blink)
    cr.restore()

def trex_pt(X, st, face=1, pitch=0.0, which="eye"):
    """world position of the T. rex's eye / nostril / mouth / arm (for aiming), matching draw_trex."""
    s = st["s"]; d = dict(st); d["x"] = 0.0
    hx, hy = dino_head(d)
    lx, ly = {"eye": (hx + 20 * s, hy - 58 * s), "nose": (hx - 160 * s, hy - 42 * s), "mouth": (hx - 110 * s, hy + 30 * s),
              "arm": (-150 * s - 40 * s, FLOOR_Y - 640 * s + 60 * s - _walkbob(d)), "head": (hx, hy)}[which]
    if abs(pitch) > 1e-4:
        px, py = 40 * s, FLOOR_Y - 400 * s
        c, s_ = math.cos(-pitch), math.sin(-pitch)
        dx, dy = lx - px, ly - py
        lx, ly = px + dx * c - dy * s_, py + dx * s_ + dy * c
    return (X - face * lx, ly)

def draw_ash(cr, t, amt=1.0, n=40, sid=21120):
    """screen-space falling ash flakes (overlay)."""
    if amt < 0.01: return
    for k in range(n):
        u = (t * (0.08 + 0.03 * (k % 5)) + k * 0.137) % 1.0
        x = (k * 263.7 + 60 * math.sin(t * 0.7 + k)) % 1080
        y = -40 + u * 2000
        cr.arc(x, y, 5 + (k % 3) * 3, 0, 2 * math.pi)
        cr.set_source_rgba(0.35, 0.33, 0.32, 0.55 * amt); cr.fill()

def draw_dino_world(cr, t, x0, x1, pre=1.0, night=0.0, after=0.0, sun=None, moon=None, volcano=None, yb=FLOOR_Y,
                    tree=None, ferns=(), cycads=(), fern_g=1.0, tree_g=1.0, glow=0.0, cave=None, sky_fx=None):
    """the meadow that becomes the dinosaur age. pre 0..1 = modern meadow -> prehistoric jungle colours; night 0..1
    darkens the sky; after 0..1 = after the meteor (ash sky, flattened plants, smoke); sun/moon = world (x, y);
    volcano = (x, h, top_blown 0..1); tree = x (a modern tree, scaled by tree_g); ferns/cycads = lists of (x, h);
    glow 0..1 = orange meteor light."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    a, b = max(x0, vx0), min(x1, vx1)
    if b <= a: return
    lo = lerp(MOD_DAY, PRE_DAY, pre); hi = lerp(MOD_DAY_HI, PRE_DAY_HI, pre)
    lo = lerp(lo, NIGHT, night); hi = lerp(hi, NIGHT, night)
    lo = lerp(lo, ASH_SKY, after); hi = lerp(hi, lerp(ASH_SKY, (0.3, 0.22, 0.2), 0.5), after)
    lo = lerp(lo, (1.0, 0.62, 0.30), glow); hi = lerp(hi, (0.95, 0.45, 0.22), glow)
    top = min(vy0, yb - 200)
    nb = int((yb - 300 - top) // 160) + 2
    for k in range(nb):
        y_lo = yb - 300 - k * 160 if k else yb + 10; y_hi = yb - 300 - (k + 1) * 160
        cr.rectangle(a, y_hi, b - a, y_lo - y_hi + 1); cr.set_source_rgb(*lerp(lo, hi, min(1.0, k / 12))); cr.fill()
    if night > 0.3:
        for k in range(int(a // 230), int(b // 230) + 1):
            yy = yb - 900 - (k * 137) % 1600
            cr.arc(k * 230 + 40 * math.sin(k), yy, 5, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 0.9, (night - 0.3) * 1.4); cr.fill()
    if sun is not None and night < 0.9:
        sketch_circle(cr, sun[0], sun[1], 150, 6, sid=21130, fill=(1.0, 0.86, 0.35), alpha=1 - night)
    if moon is not None and night > 0.1:
        sketch_circle(cr, moon[0], moon[1], 110, 6, sid=21131, fill=(0.96, 0.96, 0.88), alpha=min(1, night * 1.5))
    if sky_fx is not None: sky_fx(cr)
    # far hills
    for k in range(int(a // 1400) - 1, int(b // 1400) + 2):
        hx = k * 1400
        col = lerp(lerp((0.62, 0.80, 0.52), (0.52, 0.70, 0.40), pre), (0.45, 0.38, 0.34), after)
        col = lerp(col, (0.15, 0.2, 0.25), night * 0.8)
        cr.move_to(hx - 900, yb - 280); cr.curve_to(hx - 500, yb - 700 - 120 * (k % 3), hx + 500, yb - 700 - 120 * (k % 3), hx + 900, yb - 280)
        cr.close_path(); cr.set_source_rgb(*col); cr.fill()
    if volcano is not None:
        vx, vh, blown = volcano
        if vh > 20:
            draw_volcano(cr, vx, vh * (1 - 0.35 * blown), t, yb=yb - 280, w=1500 * max(0.3, vh / 1200), glow=1.0, smoke=min(1.0, vh / 900) * (1 + blown))
    # ground
    gcol = lerp(lerp((0.56, 0.80, 0.42), (0.44, 0.66, 0.32), pre), (0.50, 0.42, 0.36), after)
    gcol = lerp(gcol, (0.12, 0.18, 0.18), night * 0.8)
    cr.rectangle(a, yb - 300, b - a, max(600, vy1 - yb + 400)); cr.set_source_rgb(*gcol); cr.fill()
    sketch_line(cr, [(a, yb - 300), (b, yb - 300)], 5, sid=21132, amp=0.8, alpha=0.6)
    for k in range(int(a // 170) - 1, int(b // 170) + 2):                   # grass tufts / pebbles
        xx = k * 170 + 50 * math.sin(k * 2.3); yy = yb - 220 + (k * 53) % 260
        if after < 0.5:
            cr.move_to(xx - 14, yy); cr.line_to(xx - 6, yy - 30); cr.move_to(xx, yy); cr.line_to(xx + 2, yy - 38)
            cr.move_to(xx + 14, yy); cr.line_to(xx + 10, yy - 28)
            cr.set_source_rgba(0.2, 0.35, 0.15, 0.6); cr.set_line_width(4); cr.stroke()
        else:
            cr.arc(xx, yy, 8, 0, 2 * math.pi); cr.set_source_rgba(0.3, 0.27, 0.25, 0.6); cr.fill()
    if cave is not None and a - 1300 < cave < b + 800:
        draw_cave_rock(cr, cave, yb, "back")
    if tree is not None and tree_g > 0.02 and a - 600 < tree < b + 600:
        cr.save(); cr.translate(tree, yb - 120); cr.scale(tree_g, tree_g); cr.translate(-tree, -(yb - 120))
        draw_tree(cr, tree, yb - 120, t, h=1000)
        cr.restore()
    for k, (fx, fh) in enumerate(cycads):
        if a - 500 < fx < b + 500: draw_cycad(cr, fx, yb - 200 + 40 * (k % 2), fh, fern_g, t, sid=21020 + 10 * (k % 4))
    for k, (fx, fh) in enumerate(ferns):
        if a - 700 < fx < b + 700: draw_fern(cr, fx, yb - 150 + 60 * (k % 3), fh, fern_g, t, flat=after, sid=21000 + 7 * (k % 5))
    if after > 0.01:
        for k in range(int(a // 900) - 1, int(b // 900) + 2):               # smoking craters
            cx = k * 900 + 200 * math.sin(k * 1.7)
            ellipse(cr, cx, yb - 120 + 40 * (k % 2), 160, 26, sid=21140 + k % 5); fill_ink(cr, SOOT, 0.7 * after); cr.new_path()
            for j in range(3):
                u = (t * 0.25 + j / 3 + k * 0.17) % 1.0
                draw_smoke_puff(cr, cx + 40 * math.sin(t + j + k), yb - 160 - 700 * u, 60 + 120 * u, alpha=after * (1 - u) * 0.55, dark=0.7)

# ------------------------------------------------------------------ day 18 (re-cut): the lottery ---
STORE_WALL = (0.93, 0.95, 0.88)
STORE_FLOOR = (0.80, 0.82, 0.84)

def draw_store_inside(cr, t, x0, x1, yb=FLOOR_Y, sid=22100):
    """a corner store inside: pale wall, checker floor, shelves of colourful boxes, a fridge of drinks."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    a, b = max(x0, vx0), min(x1, vx1)
    if b <= a: return
    cr.rectangle(a, vy0 - 10, b - a, yb - 140 - vy0 + 10); cr.set_source_rgb(*STORE_WALL); cr.fill()
    cr.rectangle(a, yb - 140, b - a, max(400, vy1 - yb + 300)); cr.set_source_rgb(*STORE_FLOOR); cr.fill()
    for k in range(int(a // 160) - 1, int(b // 160) + 2):
        for j in range(4):
            if (k + j) % 2 == 0:
                cr.rectangle(k * 160, yb - 140 + j * 120, 160, 120); cr.set_source_rgba(0.6, 0.62, 0.66, 0.35); cr.fill()
    sketch_line(cr, [(a, yb - 140), (b, yb - 140)], 5, sid=sid, amp=0.6)
    cols = ((0.95, 0.35, 0.30), (0.30, 0.60, 0.95), (0.99, 0.80, 0.25), (0.45, 0.78, 0.40), (0.85, 0.50, 0.85))
    for k in range(int((a - x0) // 1100) - 1, int((b - x0) // 1100) + 2):     # shelves
        sx = x0 + k * 1100
        if sx < x0 or sx + 700 > x1: continue
        sketch_rect(cr, sx, yb - 1050, sx + 700, yb - 160, 6, sid=sid + 1 + k % 3, fill=(0.82, 0.74, 0.62))
        for r in range(4):
            yy = yb - 1050 + 60 + r * 220
            sketch_line(cr, [(sx, yy + 150), (sx + 700, yy + 150)], 5, sid=sid + 5 + r)
            for i in range(6):
                bx = sx + 20 + i * 113
                sketch_rect(cr, bx, yy + 20, bx + 90, yy + 148, 3, sid=sid + 10 + (i + r) % 7, fill=cols[(i + r + k) % 5], amp=0.6)

def draw_store_counter(cr, x, yb=FLOOR_Y, sid=22140):
    """the shop counter (front-on), ~900 wide, top at yb - 470; a little LOTTO stand on it."""
    sketch_rect(cr, x - 450, yb - 470, x + 450, yb - 10, 7, sid=sid, fill=(0.62, 0.42, 0.28))
    sketch_rect(cr, x - 480, yb - 500, x + 480, yb - 460, 6, sid=sid + 1, fill=(0.80, 0.62, 0.44))
    for k in range(3): sketch_line(cr, [(x - 400 + 300 * k, yb - 440), (x - 400 + 300 * k, yb - 40)], 3, sid=sid + 2 + k, alpha=0.4)
    sketch_rect(cr, x - 130, yb - 700, x + 70, yb - 500, 5, sid=sid + 6, fill=(0.98, 0.84, 0.25))
    draw_text(cr, "LOTTO", x - 30, yb - 640, 44, color=(200, 40, 40))
    draw_text(cr, "$1", x - 30, yb - 560, 52, color=(30, 30, 34))

LOTTO_NUMS = (4, 8, 15, 16, 23, 42)

def draw_lotto_tv(cr, x, y, t, shown=0, jackpot=0.0, flash=0.0, sid=22160):
    """a TV hanging on the store wall, centre (x, y), 560 x 380: TONIGHT'S DRAW + up to 6 balls (shown = how many,
    fractional = the last one popping in); jackpot 0..1 swaps to JACKPOT $10,000,000."""
    w, h = 560, 380
    sketch_line(cr, [(x, y - h / 2 - 140), (x, y - h / 2)], 8, sid=sid, amp=0.2)
    sketch_rect(cr, x - w / 2 - 22, y - h / 2 - 22, x + w / 2 + 22, y + h / 2 + 22, 7, sid=sid + 1, fill=(0.14, 0.14, 0.18))
    bg = lerp((0.10, 0.16, 0.42), (0.98, 0.82, 0.20), flash)
    cr.rectangle(x - w / 2, y - h / 2, w, h); cr.set_source_rgb(*bg); cr.fill()
    if jackpot < 0.5:
        draw_text(cr, "TONIGHT'S DRAW", x, y - 125, 46, color=(255, 255, 255))
        for i in range(6):
            u = clamp01(shown - i)
            if u <= 0: continue
            bx = x - 225 + i * 90; by = y + 20
            r = 38 * back_out(u, 2.0)
            sketch_circle(cr, bx, by, r, 4, sid=sid + 10 + i, fill=(1, 1, 1))
            if u > 0.6: draw_text(cr, str(LOTTO_NUMS[i]), bx, by, 40, color=(30, 30, 34))
        draw_text(cr, "$10,000,000 JACKPOT", x, y + 125, 36, color=(255, 220, 80))
    else:
        c = (30, 30, 34) if flash > 0.5 else (255, 220, 80)
        draw_text(cr, "JACKPOT!", x, y - 70, 96, color=c)
        draw_text(cr, "$10,000,000", x, y + 70, 80, color=c)

def draw_ticket(cr, x, y, s=1.0, circled=0, ang=0.0, sid=22180):
    """a lottery ticket held at (x, y) (bottom-centre), the six numbers; `circled` of them ringed in red."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_rect(cr, -130, -170, 130, 0, 4, sid=sid, fill=(1.0, 0.97, 0.80), amp=0.5)
    draw_text(cr, "LOTTO", 0, -140, 34, color=(200, 40, 40))
    for i, n in enumerate(LOTTO_NUMS):
        cx, cy = -80 + (i % 3) * 80, -90 + (i // 3) * 55
        draw_text(cr, str(n), cx, cy, 36, color=(30, 30, 34))
        if i < circled:
            cr.save(); cr.translate(cx, cy); cr.scale(1.0, 0.7); cr.arc(0, 0, 34, 0, 2 * math.pi); cr.restore()
            cr.set_source_rgb(0.85, 0.15, 0.15); cr.set_line_width(5); cr.stroke()
    cr.restore()

def draw_big_check(cr, x, y, s=1.0, ang=0.0, droop=0.0, sid=22200):
    """a giant novelty cheque, centre (x, y), ~760 x 360 at s=1. droop 0..1 = it sags (folds down) in the middle."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    w, h = 380, 180
    d = 120 * droop
    pts = [(-w, -h + d * 0.2), (0, -h + d), (w, -h + d * 0.2), (w, h + d * 0.2), (0, h + d), (-w, h + d * 0.2)]
    sketch_poly(cr, pts, 7, sid=sid, fill=(0.88, 0.96, 0.86), amp=0.6)
    draw_text(cr, "PAY TO: YOU", -150 , -110 + d * 0.6, 40, color=(30, 30, 34))
    draw_text(cr, "$10,000,000", 0, 0 + d * 0.8, 92, color=(30, 120, 50))
    draw_text(cr, "TEN MILLION DOLLARS", 0, 100 + d * 0.9, 34, color=(30, 30, 34))
    sketch_line(cr, [(140, 145 + d * 0.5), (340, 145 + d * 0.3)], 3, sid=sid + 1)
    cr.restore()

def draw_trash_can(cr, x, yb=FLOOR_Y, lid=0.0, sid=22220):
    """a metal curb-side trash can; lid 0..1 lifts the lid off (up and to the right)."""
    sketch_poly(cr, [(x - 130, yb - 420), (x + 130, yb - 420), (x + 110, yb), (x - 110, yb)], 7, sid=sid, fill=(0.66, 0.70, 0.72))
    for k in range(4): sketch_line(cr, [(x - 85 + 57 * k, yb - 390), (x - 75 + 50 * k, yb - 30)], 3, sid=sid + 1 + k, alpha=0.5)
    lx, ly = x + 170 * lid, yb - 430 - 140 * math.sin(math.pi * min(1.0, lid) * 0.5)
    cr.save(); cr.translate(lx, ly); cr.rotate(0.5 * lid)
    sketch_ellipse(cr, 0, 0, 150, 26, 6, sid=sid + 6, fill=(0.58, 0.62, 0.64))
    sketch_rect(cr, -30, -50, 30, -24, 5, sid=sid + 7, fill=(0.58, 0.62, 0.64))
    cr.restore()

def draw_ring_box(cr, x, y, s=1.0, open_=0.0, t=0.0, sid=22240):
    """a little red ring box held at (x, y) (bottom-centre); open_ 0..1 flips the lid up to show a sparkling ring."""
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    sketch_rect(cr, -46, -60, 46, 0, 5, sid=sid, fill=(0.80, 0.16, 0.22), amp=0.4)
    if open_ > 0.05:
        cr.save(); cr.translate(0, -60); cr.scale(1.0, 1.0 - 2.0 * min(1.0, open_)); sketch_rect(cr, -46, -40, 46, 0, 5, sid=sid + 1, fill=(0.70, 0.12, 0.18), amp=0.4); cr.restore()
        if open_ > 0.6:
            sketch_ellipse(cr, 0, -64, 24, 18, 6, sid=sid + 2, fill=None, color=(0.95, 0.75, 0.20))
            draw_star(cr, 0, -92, 18 + 6 * math.sin(t * 9), color=(0.75, 0.92, 1.0))
            for k in range(4):
                a = k * math.pi / 2 + t * 2
                sketch_line(cr, [(math.cos(a) * 50, -92 + math.sin(a) * 50), (math.cos(a) * 80, -92 + math.sin(a) * 80)], 4, sid=sid + 3 + k,
                            color=(0.95, 0.80, 0.30), alpha=open_)
    else:
        sketch_rect(cr, -46, -100, 46, -60, 5, sid=sid + 1, fill=(0.70, 0.12, 0.18), amp=0.4)
    cr.restore()

HER_WALL = (0.98, 0.90, 0.78)
def her_house_geom(x, yb=FLOOR_Y):
    """(window rect x0, y0, x1, y1), (door rect x0, y0, x1, y1) of draw_her_house."""
    return (x - 560, yb - 1040, x - 60, yb - 560), (x + 180, yb - 860, x + 480, yb - 100)

def draw_her_house(cr, x, yb=FLOOR_Y, part="wall", curtain=1.0, door=0.0, sid=22260):
    """a small cream house front (~1500 wide) with a big front window (left) and a front door (right).
    part "wall": the wall with the window + door holes cut out (draw her INSIDE before this, clipped to the window);
    part "inside": the dim room seen through the window/door; part "curtain": the two curtains (curtain 1 = closed);
    "door": the door leaf (door 0..1 open = swings out to the right)."""
    (wx0, wy0, wx1, wy1), (dx0, dy0, dx1, dy1) = her_house_geom(x, yb)
    if part == "inside":
        cr.rectangle(wx0, wy0, wx1 - wx0, wy1 - wy0); cr.rectangle(dx0, dy0, dx1 - dx0, dy1 - dy0)
        cr.set_source_rgb(0.96, 0.86, 0.70); cr.fill()
        return
    if part == "wall":
        cr.save()
        cr.rectangle(x - 760, yb - 1240, 1520, 1150); cr.rectangle(wx1, wy0, wx0 - wx1, wy1 - wy0); cr.rectangle(dx1, dy0, dx0 - dx1, dy1 - dy0)
        cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); cr.set_source_rgb(*HER_WALL); cr.fill()
        cr.restore()
        sketch_rect(cr, x - 760, yb - 1240, x + 760, yb - 90, 7, sid=sid, fill=None)
        sketch_poly(cr, [(x - 860, yb - 1230), (x, yb - 1720), (x + 860, yb - 1230)], 7, sid=sid + 1, fill=(0.45, 0.55, 0.78))
        sketch_rect(cr, wx0 - 20, wy0 - 20, wx1 + 20, wy1 + 20, 7, sid=sid + 2, fill=None)
        sketch_rect(cr, wx0 - 50, wy1 + 20, wx1 + 50, wy1 + 60, 6, sid=sid + 3, fill=(1, 1, 1))
        sketch_rect(cr, dx0 - 15, dy0 - 15, dx1 + 15, dy1, 7, sid=sid + 4, fill=None)
        sketch_rect(cr, dx0 - 60, yb - 100, dx1 + 60, yb - 40, 6, sid=sid + 5, fill=(0.75, 0.72, 0.70))
        for k in range(3):
            fx = x - 520 + 160 * k
            sketch_circle(cr, fx, yb - 120, 70, 5, sid=sid + 6 + k, fill=(0.46, 0.72, 0.36))
            sketch_circle(cr, fx + 20, yb - 160, 16, 3, sid=sid + 9 + k, fill=(0.98, 0.55, 0.65))
        return
    if part == "curtain":
        hw = (wx1 - wx0) / 2
        for sd in (-1, 1):
            cw = 40 + (hw - 40) * curtain
            ex = wx0 if sd < 0 else wx1
            ix = ex - sd * cw
            pts = [(ex, wy0), (ix, wy0)] + [(ix + 10 * math.sin(k * 1.3), wy0 + k * (wy1 - wy0) / 8) for k in range(1, 8)] + [(ix, wy1), (ex, wy1)]
            sketch_poly(cr, pts, 5, sid=sid + 20 + (sd > 0), fill=(0.85, 0.35, 0.40), amp=0.5)
            for k in range(1, 4):
                fx = lerp(ex, ix, k / 4)
                sketch_line(cr, [(fx, wy0 + 10), (fx, wy1 - 10)], 2, sid=sid + 23 + k, alpha=0.4)
        sketch_line(cr, [(wx0 - 30, wy0 - 6), (wx1 + 30, wy0 - 6)], 8, sid=sid + 30, amp=0.2)
        return
    if part == "door":
        w = (dx1 - dx0) * (1 - 0.85 * door)
        sketch_rect(cr, dx0, dy0, dx0 + w, dy1, 6, sid=sid + 40, fill=(0.40, 0.55, 0.80))
        if door < 0.3: cr.arc(dx0 + w - 40, (dy0 + dy1) / 2, 14, 0, 2 * math.pi); fill_ink(cr); cr.new_path()

def draw_street(cr, t, x0, x1, yb=FLOOR_Y, sid=22300):
    """a quiet street at golden hour: sky bands, a few far houses, grass strip + sidewalk as the floor."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    a, b = max(x0, vx0), min(x1, vx1)
    if b <= a: return
    top = min(vy0, yb - 200)
    nb = int((yb - 300 - top) // 160) + 2
    for k in range(nb):
        y_lo = yb - 300 - k * 160 if k else yb + 10; y_hi = yb - 300 - (k + 1) * 160
        cr.rectangle(a, y_hi, b - a, y_lo - y_hi + 1); cr.set_source_rgb(*lerp((0.99, 0.84, 0.62), (0.62, 0.74, 0.95), min(1.0, k / 10))); cr.fill()
    for k in range(int(a // 1200) - 1, int(b // 1200) + 2):
        hx = k * 1200 + 300
        sketch_rect(cr, hx - 260, yb - 900, hx + 260, yb - 300, 5, sid=sid + k % 4, fill=lerp((0.85, 0.80, 0.90), (0.80, 0.90, 0.85), (k % 3) / 2))
        sketch_poly(cr, [(hx - 300, yb - 895), (hx, yb - 1120), (hx + 300, yb - 895)], 5, sid=sid + 5 + k % 4, fill=(0.70, 0.40, 0.38))
    cr.rectangle(a, yb - 300, b - a, 220); cr.set_source_rgb(0.56, 0.78, 0.44); cr.fill()
    cr.rectangle(a, yb - 80, b - a, max(400, vy1 - yb + 300)); cr.set_source_rgb(0.84, 0.84, 0.82); cr.fill()
    sketch_line(cr, [(a, yb - 80), (b, yb - 80)], 4, sid=sid + 10, amp=0.5, alpha=0.6)
    for k in range(int(a // 300) - 1, int(b // 300) + 2):
        cr.move_to(k * 300, yb - 80); cr.line_to(k * 300 - 60, yb + 300)
    cr.set_source_rgba(0.5, 0.5, 0.5, 0.4); cr.set_line_width(3); cr.stroke()


# ================================================================ day 19: basketball (court, arena, the kid's kit)
BBALL = (0.93, 0.50, 0.18)
COURT_SKY_DAY, COURT_SKY_NIGHT = (0.62, 0.82, 0.97), (0.10, 0.12, 0.26)
ASPHALT = (0.46, 0.47, 0.50)
HARDWOOD = (0.86, 0.66, 0.42)
HOOP_RIM_DX, HOOP_RIM_DY = 120.0, 1180.0          # rim centre relative to the backboard foot (bx, yb)

def draw_basketball(cr, x, y, r=46, ang=0.0, sid=23000):
    """an orange basketball with seams; (x, y) = centre."""
    cr.save(); cr.translate(x, y); cr.rotate(ang)
    sketch_circle(cr, 0, 0, r, 5, sid=sid, fill=BBALL)
    sketch_line(cr, [(-r, 0), (r, 0)], 3, sid=sid + 1, amp=0.3)
    sketch_line(cr, [(0, -r), (0, r)], 3, sid=sid + 2, amp=0.3)
    sketch_curve(cr, (-r * 0.62, -r * 0.78), (-r * 0.25, 0), (-r * 0.62, r * 0.78), 3, sid=sid + 3, amp=0.3)
    sketch_curve(cr, (r * 0.62, -r * 0.78), (r * 0.25, 0), (r * 0.62, r * 0.78), 3, sid=sid + 4, amp=0.3)
    cr.restore()

def hoop_rim(bx, yb=FLOOR_Y): return (bx + HOOP_RIM_DX, yb - HOOP_RIM_DY)

def draw_hoop(cr, bx, yb=FLOOR_Y, part="back", t=0.0, bend=0.0, shake=0.0, swish=0.0, shatter=0.0, pole=True,
              sid=23010, glass=False):
    """a hoop facing RIGHT (the shooter stands to its right). bx = the backboard's x. part "back" = pole, backboard,
    back of the rim; "front" = the front of the rim + the net. bend 0..1 = the rim pulled down by a dunk, shake = board
    wobble px, swish 0..1 = net flick, shatter 0..1 = the board is gone (draw_shards does the flying glass)."""
    rx, ry = hoop_rim(bx, yb)
    wob = shake * math.sin(t * 40.0)
    by = yb - 1330 + wob
    if part == "back":
        if pole:
            px = bx - 230
            sketch_rect(cr, px - 22, by + 40, px + 22, yb, 6, sid=sid, fill=(0.35, 0.37, 0.42))
            sketch_line(cr, [(px, by + 60), (bx - 20, by + 110)], 16, sid=sid + 1, amp=0.3)
            sketch_line(cr, [(px, by + 60), (bx - 20, by + 110)], 8, sid=sid + 1, amp=0.0, color=(0.35, 0.37, 0.42))
        if shatter < 0.5:
            fill = (0.82, 0.92, 0.98) if glass else WHITE
            sketch_rect(cr, bx - 30, by - 200, bx + 40, by + 170, 6, sid=sid + 2, fill=fill)
            sketch_rect(cr, bx - 10, by - 50, bx + 24, by + 110, 4, sid=sid + 3, fill=None, color=(0.85, 0.15, 0.12))
        else:
            sketch_rect(cr, bx - 30, by - 200, bx + 40, by + 170, 5, sid=sid + 2, fill=None, alpha=0.5)
        # back half of the rim
        ang = 0.35 * bend
        cr.save(); cr.translate(bx + 30, ry + wob); cr.rotate(ang)
        cr.arc(HOOP_RIM_DX - 30, 0, 1, 0, 0)
        cr.save(); cr.scale(1.0, 0.24); cr.arc(HOOP_RIM_DX - 30, 0, 90, math.pi, 2 * math.pi); cr.restore()
        stroke_ink(cr, 9, color=(0.9, 0.25, 0.12)); cr.restore()
    else:
        ang = 0.35 * bend
        cr.save(); cr.translate(bx + 30, ry + wob); cr.rotate(ang)
        cx = HOOP_RIM_DX - 30
        # the net: a tapered mesh hanging from the rim
        fl = 18 * swish * math.sin(t * 30.0)
        top = [(cx - 90 + 180 * k / 6, 0) for k in range(7)]
        bot = [(cx - 50 + 100 * k / 6 + fl, 150 + 20 * swish) for k in range(7)]
        for a, b in zip(top, bot): sketch_line(cr, [a, b], 3, sid=sid + 10, amp=0.2)
        for a, b in zip(top, bot[::-1]): sketch_line(cr, [a, b], 3, sid=sid + 11, amp=0.2, alpha=0.7)
        sketch_line(cr, [bot[0], bot[-1]], 3, sid=sid + 12, amp=0.2)
        cr.save(); cr.scale(1.0, 0.24); cr.arc(cx, 0, 90, 0, math.pi); cr.restore()
        stroke_ink(cr, 9, color=(0.9, 0.25, 0.12))
        cr.save(); cr.scale(1.0, 0.24); cr.arc(cx, 0, 90, 0, 2 * math.pi); cr.restore()
        stroke_ink(cr, 3)
        cr.restore()

def draw_shards(cr, x, y, u, n=26, sid=23040, spread=1.0):
    """glass from a shattered backboard flying out and falling (u = seconds since the break)."""
    if u <= 0: return
    for k in range(n):
        h = ((k * 2654435761) % 1000) / 1000.0; h2 = ((k * 40503 + 17) % 1000) / 1000.0
        vx = (h - 0.35) * 1500 * spread; vy = -300 - 900 * h2
        px = x + vx * u; py = y + vy * u + 1800 * u * u
        if py > FLOOR_Y + 20: py = FLOOR_Y - 6; px = x + vx * (u * 0.6)
        r = 18 + 26 * h
        cr.save(); cr.translate(px, py); cr.rotate(u * (4 + 6 * h) + k)
        sketch_poly(cr, [(-r, -r * 0.4), (r * 0.7, -r * 0.8), (r * 0.4, r * 0.7)], 3, sid=sid + k % 7, fill=(0.80, 0.92, 0.99))
        cr.restore()

def draw_court_world(cr, t, x0, x1, yb=FLOOR_Y, night=0.0, sun_u=0.5, moon_u=None, sid=23060):
    """an outdoor neighbourhood court: sky (day->night), sun or moon arcing over, trees, a chain-link fence, asphalt."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    a, b = max(x0, vx0), min(x1, vx1)
    if b <= a: return
    sky = lerp(COURT_SKY_DAY, COURT_SKY_NIGHT, night)
    cr.rectangle(a, vy0 - 10, b - a, yb - 200 - vy0 + 10); cr.set_source_rgb(*sky); cr.fill()
    cx = (vx0 + vx1) / 2
    if night > 0.3:
        for k in range(30):
            h = ((k * 2654435761) % 1000) / 1000.0; h2 = ((k * 40503) % 1000) / 1000.0
            cr.arc(vx0 + (vx1 - vx0) * h, vy0 + 700 + (yb - 1300 - vy0 - 700) * h2, 5, 0, 2 * math.pi)
            cr.set_source_rgba(1, 1, 0.9, (night - 0.3) / 0.7); cr.fill()
    if sun_u is not None and night < 0.95:                  # the sun arcs left -> right over the court
        sx = cx - 1500 + 3000 * sun_u; sy = yb - 900 - 900 * math.sin(math.pi * min(1, max(0, sun_u)))
        sketch_circle(cr, sx, sy, 110, 5, sid=sid, fill=(1.0, 0.86, 0.30), alpha=1 - night)
    if moon_u is not None and night > 0.05:
        mx = cx - 1500 + 3000 * moon_u; my = yb - 900 - 900 * math.sin(math.pi * min(1, max(0, moon_u)))
        sketch_circle(cr, mx, my, 90, 5, sid=sid + 1, fill=(0.95, 0.95, 0.88), alpha=night)
    dk = 1 - 0.55 * night
    for k in range(int(a // 700) - 1, int(b // 700) + 2):  # trees behind the fence
        tx = k * 700 + 200 + 120 * math.sin(k * 1.7)
        sketch_rect(cr, tx - 25, yb - 700, tx + 25, yb - 200, 5, sid=sid + 2 + k % 3, fill=(0.55 * dk, 0.38 * dk, 0.25 * dk))
        sketch_circle(cr, tx, yb - 820, 230 + 30 * math.sin(k), 5, sid=sid + 5 + k % 3, fill=(0.42 * dk, 0.70 * dk, 0.38 * dk))
    # the chain-link fence (diamond mesh) along the back of the court
    ft = yb - 860
    cr.save(); cr.rectangle(a, ft, b - a, 660); cr.clip()
    cr.set_source_rgba(0.55, 0.57, 0.60, 0.8); cr.set_line_width(3)
    for k in range(int(a // 60) - 12, int(b // 60) + 14):
        cr.move_to(k * 60, ft); cr.line_to(k * 60 + 660, ft + 660)
        cr.move_to(k * 60, ft); cr.line_to(k * 60 - 660, ft + 660)
    cr.stroke(); cr.restore()
    sketch_line(cr, [(a, ft), (b, ft)], 7, sid=sid + 9, amp=0.4, color=(0.45, 0.47, 0.5))
    for k in range(int(a // 900) - 1, int(b // 900) + 2):
        sketch_line(cr, [(k * 900, ft - 20), (k * 900, yb - 200)], 9, sid=sid + 10 + k % 3, amp=0.3, color=(0.45, 0.47, 0.5))
    # asphalt + court paint
    cr.rectangle(a, yb - 200, b - a, max(400, vy1 - yb + 300)); cr.set_source_rgb(*lerp(ASPHALT, (0.25, 0.26, 0.30), night)); cr.fill()
    sketch_line(cr, [(a, yb - 200), (b, yb - 200)], 5, sid=sid + 14, amp=0.4)
    paint = (0.97, 0.97, 0.95)
    sketch_line(cr, [(a, yb - 150), (b, yb - 150)], 6, sid=sid + 15, amp=0.3, color=paint, alpha=0.8)
    sketch_line(cr, [(a, yb + 120), (b, yb + 120)], 6, sid=sid + 16, amp=0.3, color=paint, alpha=0.8)
    for k in range(int(a // 140) - 1, int(b // 140) + 2):     # cracks
        if k % 5 == 0: sketch_line(cr, [(k * 140, yb - 120), (k * 140 + 40, yb - 60), (k * 140 + 10, yb + 10)], 3, sid=sid + 17, alpha=0.35)

def draw_arena(cr, t, x0, x1, yb=FLOOR_Y, flashes=1.0, roar=0.0, banner_x=None, sid=23100):
    """THE FINALS: dark stands packed with fans (camera flashes), a WITNESS banner, the hardwood floor."""
    vx0, vy0, vx1, vy1 = _visible(cr)
    a, b = max(x0, vx0), min(x1, vx1)
    if b <= a: return
    cr.rectangle(a, vy0 - 10, b - a, yb - 260 - vy0 + 10); cr.set_source_rgb(0.12, 0.12, 0.17); cr.fill()
    step = 54.0
    for row in range(16):
        yy = yb - 330 - row * 58
        for k in range(int(a // step) - 1, int(b // step) + 2):
            xx = k * step + (row % 2) * step / 2
            hsh = (k * 7919 + row * 104729) % 97
            if hsh < 8: continue
            col = CROWD_COLS[hsh % len(CROWD_COLS)]
            bob = (4 + 10 * roar) * math.sin(t * (6 + 6 * roar) + hsh) if hsh % 3 == 0 else 0
            cr.arc(xx, yy + bob, 18, 0, 2 * math.pi); cr.set_source_rgb(*[c * 0.75 for c in col]); cr.fill()
            if flashes > 0 and (hsh * 13 + k * 7 + row * 31 + int(t * 7)) % 263 == 0:
                cr.arc(xx, yy, 34, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.85 * flashes); cr.fill()
    # an ad-board strip on the courtside wall
    cr.rectangle(a, yb - 260, b - a, 70); cr.set_source_rgb(0.16, 0.20, 0.40); cr.fill()
    for k in range(int(a // 900) - 1, int(b // 900) + 2):
        draw_text(cr, "THE FINALS", k * 900 + 450, yb - 225, 44, color=(250, 200, 70))
    sketch_line(cr, [(a, yb - 190), (b, yb - 190)], 5, sid=sid, amp=0.3)
    # hardwood
    cr.rectangle(a, yb - 190, b - a, max(400, vy1 - yb + 300)); cr.set_source_rgb(*HARDWOOD); cr.fill()
    cr.set_source_rgba(0.6, 0.42, 0.24, 0.35); cr.set_line_width(3)
    for j in range(6):
        cr.move_to(a, yb - 160 + j * 70); cr.line_to(b, yb - 160 + j * 70)
    cr.stroke()
    if banner_x is not None:                                      # the WITNESS banner hanging from the rafters
        bx = banner_x
        sketch_line(cr, [(bx - 230, vy0 - 50), (bx - 230, 120)], 4, sid=sid + 2, color=(0.5, 0.5, 0.55))
        sketch_line(cr, [(bx + 230, vy0 - 50), (bx + 230, 120)], 4, sid=sid + 3, color=(0.5, 0.5, 0.55))
        sketch_rect(cr, bx - 260, 120, bx + 260, 330, 6, sid=sid + 4, fill=(0.10, 0.10, 0.12))
        draw_text(cr, "WITNESS", bx, 225, 96, color=(250, 250, 250))

def draw_paint(cr, rim_x, yb=FLOOR_Y, ft_x=None, sid=23130):
    """the painted key on the hardwood under the hoop + the free-throw line (seen from the side: a long band)."""
    ft_x = ft_x if ft_x is not None else rim_x + 900
    cr.rectangle(rim_x - 150, yb - 170, ft_x - rim_x + 150, 260); cr.set_source_rgba(0.80, 0.22, 0.20, 0.55); cr.fill()
    sketch_line(cr, [(ft_x, yb - 170), (ft_x - 40, yb + 90)], 7, sid=sid, amp=0.3, color=(0.98, 0.98, 0.96))

def draw_scoreboard(cr, x, y, home="100", away="101", clock="0:05", top="GAME 7", flash=0.0, final=False, sid=23140):
    """a hanging scoreboard (~760 x 460), (x, y) = centre."""
    sketch_line(cr, [(x - 250, y - 230), (x - 250, y - 900)], 5, sid=sid, color=(0.5, 0.5, 0.55))
    sketch_line(cr, [(x + 250, y - 230), (x + 250, y - 900)], 5, sid=sid + 1, color=(0.5, 0.5, 0.55))
    sketch_rect(cr, x - 380, y - 230, x + 380, y + 230, 7, sid=sid + 2, fill=(0.08, 0.08, 0.10))
    draw_text(cr, top, x, y - 170, 52, color=(250, 200, 70))
    draw_text(cr, "HOME", x - 220, y - 95, 44, color=(220, 220, 220))
    draw_text(cr, "AWAY", x + 220, y - 95, 44, color=(220, 220, 220))
    hc = (255, 235, 80) if flash > 0.5 else (255, 90, 60)
    draw_text(cr, home, x - 220, y + 5, 110, color=hc)
    draw_text(cr, away, x + 220, y + 5, 110, color=(255, 90, 60))
    sketch_rect(cr, x - 120, y + 95, x + 120, y + 205, 4, sid=sid + 3, fill=(0.16, 0.16, 0.2))
    draw_text(cr, "FINAL" if final else clock, x, y + 150, 72 if not final else 60, color=(255, 255, 255))

def draw_magazine(cr, x, y, s=1.0, ang=0.0, sid=23160):
    """a sports magazine cover: THE CHOSEN ONE, the kid (headband) on it. ~330 x 440 at s=1, (x, y) = centre."""
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(s, s)
    sketch_rect(cr, -165, -220, 165, 220, 5, sid=sid, fill=(0.97, 0.95, 0.90))
    cr.rectangle(-150, -205, 300, 70); cr.set_source_rgb(0.85, 0.15, 0.15); cr.fill()
    draw_text(cr, "SPORTS", 0, -170, 50, color=(255, 255, 255))
    sketch_circle(cr, 0, -10, 78, 5, sid=sid + 1, fill=WHITE)                     # the kid's face
    sketch_line(cr, [(-2, -88), (-6, -112), (10, -122), (20, -110), (8, -102)], 4, sid=sid + 2)
    cr.save(); cr.arc(0, -10, 76, 0, 2 * math.pi); cr.clip()
    cr.rectangle(-90, -62, 180, 22); cr.set_source_rgb(0.98, 0.98, 0.98); cr.fill()
    sketch_line(cr, [(-90, -62), (90, -62)], 3, sid=sid + 3); sketch_line(cr, [(-90, -40), (90, -40)], 3, sid=sid + 4)
    cr.restore()
    for ex in (-26, 26):
        cr.new_path(); cr.arc(ex, -12, 13, 0, 2 * math.pi); fill_paper(cr, WHITE); stroke_ink(cr, 3)
        cr.new_path(); cr.arc(ex, -10, 6, 0, 2 * math.pi); fill_ink(cr); cr.new_path()
    sketch_line(cr, [(-20, 32), (20, 32)], 4, sid=sid + 5, amp=0.3)
    sketch_rect(cr, -70, 70, 70, 140, 4, sid=sid + 6, fill=(0.98, 0.98, 0.98))
    draw_text(cr, "23", 0, 105, 50, color=(200, 30, 30))
    draw_text(cr, "THE CHOSEN ONE", 0, 185, 40, color=(20, 20, 24))
    cr.restore()

def draw_chalk_cloud(cr, x, y, u, r=520, sid=23180):
    """the pre-game chalk toss: a white powder cloud bursting up and out (u = 0..1 life, fades out at the end)."""
    if u <= 0 or u >= 1: return
    g = 1 - (1 - min(1.0, u * 2.2)) ** 3
    al = 1.0 if u < 0.6 else 1 - (u - 0.6) / 0.4
    for k in range(14):
        h = ((k * 2654435761) % 1000) / 1000.0; h2 = ((k * 40503) % 1000) / 1000.0
        ang = -math.pi / 2 + (h - 0.5) * 2.6
        d = r * g * (0.4 + 0.6 * h2)
        px, py = x + math.cos(ang) * d * 1.3, y + math.sin(ang) * d * 0.8 + 120 * u
        rr = (110 + 140 * h) * (0.4 + 0.8 * g)
        sketch_circle(cr, px, py, rr, 4, sid=sid + k % 9, fill=(0.99, 0.99, 0.98), color=(0.75, 0.75, 0.78), alpha=al)

def draw_folding_chair(cr, x, yb=FLOOR_Y, sid=23200):
    """a courtside folding chair seen from the side (seat at yb - 330, facing LEFT)."""
    col = (0.30, 0.30, 0.36)
    sketch_line(cr, [(x - 120, yb), (x + 90, yb - 330)], 9, sid=sid, amp=0.3, color=col)
    sketch_line(cr, [(x + 120, yb), (x - 90, yb - 330)], 9, sid=sid + 1, amp=0.3, color=col)
    sketch_rect(cr, x - 140, yb - 350, x + 140, yb - 320, 5, sid=sid + 2, fill=(0.75, 0.15, 0.15))
    sketch_line(cr, [(x + 110, yb - 330), (x + 130, yb - 700)], 9, sid=sid + 3, amp=0.3, color=col)
    sketch_rect(cr, x + 100, yb - 720, x + 150, yb - 540, 5, sid=sid + 4, fill=(0.75, 0.15, 0.15))

def draw_jersey(cr, p, num="23", col=(0.42, 0.18, 0.55), trim=(0.98, 0.80, 0.22), sid=23220):
    """a basketball tank top on a stick body (p = the pose, world coords). Draw it after the body, then the arms."""
    nk, hp = p["neck"], p["hip"]
    dx, dy = hp[0] - nk[0], hp[1] - nk[1]
    L_ = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L_, dy / L_; nx, ny = -uy, ux
    def P(along, side): return (nk[0] + ux * along + nx * side, nk[1] + uy * along + ny * side)
    top, bot = 20, L_ + 40
    pts = [P(top, -62), P(top + 10, -30), P(top + 40, 0), P(top + 10, 30), P(top, 62), P(top + 90, 80), P(bot, 88),
           P(bot, -88), P(top + 90, -80)]
    sketch_poly(cr, pts, 6, sid=sid, fill=col)
    sketch_line(cr, [P(top, -62), P(top + 10, -30), P(top + 40, 0), P(top + 10, 30), P(top, 62)], 6, sid=sid + 1, amp=0.3, color=trim)
    mx, my = P(top + (bot - top) * 0.45, 0)
    draw_text(cr, num, mx, my, 92, color=(int(trim[0] * 255), int(trim[1] * 255), int(trim[2] * 255)))
    sketch_rect(cr, *P(bot - 30, -88), *P(bot, 88), 0, sid=sid + 2, fill=None, alpha=0.0)

def draw_headband(cr, p, col=(0.98, 0.98, 0.98), sid=23240):
    """a sweatband round his forehead (p = the pose, world coords)."""
    import character as _C
    hx, hy = p["head"]; R = _C.HEAD_R
    cr.save(); cr.translate(hx, hy); cr.rotate(p.get("tilt", 0.0))
    cr.arc(0, 0, R - 4, 0, 2 * math.pi); cr.clip()
    cr.rectangle(-R - 10, -R * 0.80, 2 * R + 20, R * 0.26); cr.set_source_rgb(*col); cr.fill()
    cr.restore()
    cr.save(); cr.translate(hx, hy); cr.rotate(p.get("tilt", 0.0))
    for yy in (-R * 0.80, -R * 0.54):
        w = math.sqrt(max(0.0, R * R - yy * yy))
        sketch_line(cr, [(-w, yy), (w, yy)], 4.5, sid=sid + (yy > -R * 0.6), amp=0.3)
    cr.restore()
