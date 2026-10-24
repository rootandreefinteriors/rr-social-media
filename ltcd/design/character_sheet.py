"""Character sheet for the LTCD guy: full body + expression range. Run: python character_sheet.py -> sheet.png"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine"))
import cairo
import ltcd as L
from ltcd import P

W, H = 2400, 1920
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
cr = cairo.Context(surf)
cr.set_source_rgb(*L.PAPER); cr.paint()
L.BOIL = 0

def label(txt, x, y, size=46):
    s, tw, th = L.text_surface(txt, size)
    cr.set_source_surface(s, x - tw / 2, y); cr.paint()

# --- full body: says hi (shy wave)
wave = P(relb=(668, 760), rhand=(700, 640), rhand_t="open", smile=0.75, brow=0.35, worry=0.3, blush=0.6,
         look=(0.0, 0.0), tilt=-0.06, lfoot_dir=-0.45, rfoot_dir=0.45, curl=0.1)
cr.save(); cr.translate(-40, 120); cr.scale(0.92, 0.92)
L.sketch_line(cr, [(200, L.FLOOR_Y), (900, L.FLOOR_Y)], 3.5, sid=90, alpha=0.8)
L.draw_guy(cr, 0, wave, 0.0)
cr.restore()
label("hi.", 490, 260, 60)

# --- full body: hopeful, holding hands together, on his toes
hope = P(lelb=(500, 930), lhand=(530, 1010), relb=(580, 930), rhand=(550, 1010), lhand_t="fist", rhand_t="fist",
         smile=0.4, brow=0.6, worry=0.75, pupil=1.35, look=(0.0, -0.1), tilt=0.08, curl=-0.15)
cr.save(); cr.translate(560, 120); cr.scale(0.92, 0.92)
L.sketch_line(cr, [(200, L.FLOOR_Y), (900, L.FLOOR_Y)], 3.5, sid=91, alpha=0.8)
L.draw_guy(cr, 0, hope, 0.0)
cr.restore()
label("(please?)", 1095, 260, 60)

# --- expression grid
faces = [
    ("eager", dict(smile=0.9, open=0.55, brow=0.5, worry=0.1, pupil=1.15)),
    ("hopeful", dict(smile=0.35, brow=0.6, worry=0.8, pupil=1.4, look=(0, -0.15))),
    ("surprised", dict(smile=0.0, open=0.75, brow=1.0, worry=0.0, pupil=0.75, eyescale=1.12)),
    ("concentrating", dict(smile=-0.1, tongue=1.0, brow=-0.4, worry=-0.2, look=(0.4, 0.75), lid=0.25)),
    ("impatient", dict(smile=-0.45, brow=-0.6, worry=-0.9, lid=0.45, look=(0.6, 0.0))),
    ("sleepy", dict(smile=0.0, open=0.0, brow=-0.2, worry=0.3, lid=0.8)),
    ("embarrassed", dict(smile=0.5, brow=0.3, worry=0.6, blush=1.0, look=(-0.6, 0.4))),
    ("sad", dict(smile=-0.6, brow=0.2, worry=1.0, look=(0, 0.5), pupil=1.2)),
    ("delighted", dict(smile=1.0, open=0.8, brow=0.8, lid=0.0, blush=0.5, pupil=1.25)),
]
gx0, gy0, cell = 1440, 160, 320
for i, (name, kw) in enumerate(faces):
    r, c = divmod(i, 3)
    x, y = gx0 + c * cell + cell / 2, gy0 + r * (cell + 230) + 210
    pp = P(**kw)
    cr.save(); cr.translate(x, y); cr.scale(1.05, 1.05)
    L.draw_head(cr, pp, 0.0)
    cr.restore()
    label(name, x, y + 150, 40)

surf.write_to_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sheet.png"))
print("sheet.png")
