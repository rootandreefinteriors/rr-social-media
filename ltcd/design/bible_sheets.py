"""Character bible sheets for the LTCD guy. python bible_sheets.py -> sheet_*.png"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import cairo, ink
import ltcd as L

def new(w, h):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s)
    c.set_source_rgb(*L.PAPER); c.paint(); return s, c

def label(cr, txt, x, y, size=40):
    L.draw_text(cr, txt, x, y, size)

def head_at(cr, p, x, y, sc=1.0, t=0.7, fx=False):
    cr.save(); cr.translate(x, y); cr.scale(sc, sc); cr.rotate(p.get("tilt", 0.0))
    L.draw_head(cr, p, 0.0, t)
    cr.restore()
    if fx:
        cr.save(); cr.translate(x, y); cr.scale(sc, sc); L.draw_fx(cr, p, 0, 0, t); cr.restore()

def body_at(cr, p, cx, cy, sc=0.42, t=0.7):
    cr.save(); cr.translate(cx, cy); cr.scale(sc, sc); cr.translate(-540, -980)
    L.sketch_line(cr, [(240, L.FLOOR_Y), (840, L.FLOOR_Y)], 3.5, sid=90, alpha=0.6)
    L.draw_guy(cr, t, p, 0.0)
    cr.restore()

ink.BOIL = 0

# ---- 1. turnaround + hands
s, cr = new(2400, 1500)
label(cr, "TURNAROUND", 1200, 70, 64)
for i, (name, kw) in enumerate([("front", dict(turn=0.0)), ("3/4", dict(turn=0.9, look=(0.5, 0))),
                                 ("profile", dict(turn=1.5, look=(0.9, 0))), ("back", dict(back=1.0))]):
    head_at(cr, L.pose("stand", "happy", **kw), 330 + i * 580, 420, 1.3)
    label(cr, name, 330 + i * 580, 640)
label(cr, "HANDS", 1200, 800, 64)
for i, h in enumerate([k for k in L.HANDS if k not in ("grip", "none")]):
    x = 170 + i * 230
    L.draw_hand(cr, (x, 1060), (x - 120, 1110), h, 1, sid=10 + i, sc=2.2)
    label(cr, h, x + 10, 1250, 36)
s.write_to_png(os.path.join(HERE, "sheet_turnaround.png"))

# ---- 2. expressions
names = list(L.EXPR)
cols = 7; rows = math.ceil(len(names) / cols)
s, cr = new(cols * 340 + 40, rows * 400 + 140)
label(cr, "EXPRESSIONS", (cols * 340 + 40) / 2, 70, 64)
for i, n in enumerate(names):
    r, c = divmod(i, cols)
    x, y = 190 + c * 340, 300 + r * 400
    head_at(cr, L.pose("stand", n), x, y, 0.95, fx=True)
    label(cr, n, x, y + 165, 32)
s.write_to_png(os.path.join(HERE, "sheet_expressions.png"))

# ---- 3. body poses
names = list(L.POSES)
cols = 7; rows = math.ceil(len(names) / cols)
s, cr = new(cols * 340 + 40, rows * 560 + 140)
label(cr, "BODY POSES", (cols * 340 + 40) / 2, 70, 64)
faces = dict(shy="shy", wave="happy", cheer="delighted", facepalm="annoyed", scratch_head="confused", think="thinking",
             shrug="confused", cower="scared", hug_self="cold", sit_floor="bored", lie_back="dizzy", crouch="nervous",
             jump_tuck="eager", dance_a="singing", dance_b="singing", sneak="mischievous", fly="determined",
             thumbs_up="proud", arms_crossed="impatient", hands_hips="determined", point_up="idea", clap="eager",
             present="eager", bow="happy", point_cam="happy")
for i, n in enumerate(names):
    r, c = divmod(i, cols)
    x, y = 190 + c * 340, 380 + r * 560
    body_at(cr, L.pose(n, faces.get(n, "neutral")), x, y, 0.4)
    label(cr, n, x, y + 245, 32)
s.write_to_png(os.path.join(HERE, "sheet_poses.png"))

# ---- 4. eyes, mouths, symbols
s, cr = new(2400, 1700)
label(cr, "EYES", 1200, 70, 60)
for i, e in enumerate(L.EYES):
    x = 140 + i * 265
    head_at(cr, L.pose("stand", "neutral", eyes=e, smile=0.3), x, 260, 0.85)
    label(cr, e, x, 400, 32)
label(cr, "MOUTHS", 1200, 520, 60)
mouth_kw = dict(auto=dict(smile=0.6), grin=dict(open=0.8), o=dict(open=0.6), yawn=dict(open=1.0), scream=dict(open=1.0),
                wail=dict(open=0.7), smirk=dict(smile=0.6))
for i, m in enumerate(L.MOUTHS):
    x = 120 + (i % 13) * 180
    head_at(cr, L.pose("stand", "neutral", mouth=m, **mouth_kw.get(m, {})), x, 700, 0.62)
    label(cr, m, x, 810, 30)
label(cr, "SYMBOLS + EXTRAS", 1200, 930, 60)
extras = [("fx_q", {}), ("fx_ex", {}), ("fx_zzz", {}), ("fx_hearts", {}), ("fx_stars", {}), ("fx_bulb", {}), ("fx_steam", {}),
          ("fx_nervous", {}), ("fx_notes", {}), ("fx_sparkle", {}), ("tears", {}), ("sweat", {}), ("vein", {}), ("gloom", {}),
          ("blush", {}), ("teary", {})]
for i, (k, kw) in enumerate(extras):
    r, c = divmod(i, 8)
    x, y = 150 + c * 300, 1180 + r * 330
    p = L.pose("stand", "neutral"); p[k] = 1.0
    head_at(cr, p, x, y, 0.55, fx=True)
    label(cr, k.replace("fx_", ""), x, y + 105, 30)
s.write_to_png(os.path.join(HERE, "sheet_details.png"))
print("ok")
