"""Day 22 -- WAITING episode (no qualifying comment on day 21: both new comments were sexual innuendo, see LOG.md).
The message is the star.

He is still where day 21 left him: inside GAME CAVE at the demo TV corner, the new console plugged in and still
updating (UPDATE 3 OF 47 now - a day has passed), the opened console box + the game box on the floor next to him.
He stands holding the sign up to us: TELL ME WHAT TO DO NEXT IN THE COMMENTS. Dead stare, breathing, the odd blink,
eyes flick down to the sign once. The only beat: he turns the sign to himself, writes "I HAVE TIME.", turns it back
and keeps staring. Slow blink. Hard cut. ~21 s. Copied from tests/waiting_ref; only the place + line changed.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import objects as O
from ink import FLOOR_Y, sketch_line, draw_text

sk_rect, sk_poly = O.sketch_rect, O.sketch_poly

# GAME CAVE exactly as day 21 left it (see ep021/episode.py)
IX = 8000000.0
TVX = IX - 1500.0
HIS_TV = TVX + 560.0                       # where he did the ask on day 21

S = M.Scene(x0=HIS_TV - 540)
S.floor = False

def draw_poster_mini(cr):
    w, h = 150, 210
    bands = ((0.98, 0.45, 0.62), (1.0, 0.68, 0.42), (1.0, 0.80, 0.40), (0.55, 0.30, 0.62))
    for i, c in enumerate(bands):
        cr.rectangle(-w / 2, -h / 2 + i * h / 4, w, h / 4 + 1); cr.set_source_rgb(*c); cr.fill()
    cr.arc(0, 30, 45, math.pi, 2 * math.pi); cr.set_source_rgb(1.0, 0.92, 0.45); cr.fill()
    draw_text(cr, "6", 0, -30, 110, color=(255, 255, 255))
    sk_rect(cr, -w / 2, -h / 2, w / 2, h / 2, 4, sid=21861, fill=None)

def draw_console_box(cr, x, yb, s=1.0, ang=0.0, sid=21850):
    cr.save(); cr.translate(x, yb); cr.rotate(ang); cr.scale(s, s)
    sk_rect(cr, -95, -250, 95, 0, 5, sid=sid, fill=(0.97, 0.97, 0.99))
    cr.rectangle(-93, -250, 186, 50); cr.set_source_rgb(0.12, 0.14, 0.30); cr.fill()
    sk_poly(cr, [(-30, -40), (-48, -185), (-8, -185), (0, -40)], 3, sid=sid + 1, fill=(1, 1, 1))
    sk_poly(cr, [(0, -40), (8, -185), (48, -185), (30, -40)], 3, sid=sid + 2, fill=(1, 1, 1))
    cr.rectangle(-6, -180, 12, 140); cr.set_source_rgb(0.12, 0.12, 0.14); cr.fill()
    draw_text(cr, "NEXT GEN", 0, -225, 26, color=(255, 255, 255))
    cr.restore()

def draw_game_box(cr, x, yb, s=1.0, ang=0.0):
    cr.save(); cr.translate(x, yb); cr.rotate(ang); cr.scale(s, s)
    cr.translate(0, -105); draw_poster_mini(cr); cr.restore()

def draw_tv_screen(cr, t):
    x, yb = TVX, FLOOR_Y
    sx0, sy0, sx1, sy1 = x - 230, yb - 750, x + 230, yb - 450
    cr.rectangle(sx0, sy0, sx1 - sx0, sy1 - sy0); cr.set_source_rgb(0.06, 0.08, 0.16); cr.fill()
    draw_text(cr, "UPDATE 3 OF 47", x, sy0 + 55, 48, color=(255, 255, 255))
    draw_text(cr, "150 GB", x, sy0 + 115, 40, color=(180, 200, 255))
    bx0, bx1, by = sx0 + 40, sx1 - 40, sy0 + 175
    cr.rectangle(bx0, by, bx1 - bx0, 34); cr.set_source_rgb(0.25, 0.25, 0.32); cr.fill()
    cr.rectangle(bx0, by, (bx1 - bx0) * 0.01, 34); cr.set_source_rgb(0.30, 0.85, 0.45); cr.fill()
    draw_text(cr, "1%", x, by + 80, 40, color=(255, 255, 255))
    draw_text(cr, "TIME LEFT: 11 HRS", x, by + 130, 34, color=(255, 200, 120))

def store(cr, t):
    O.draw_store_inside(cr, t, IX - 6000, IX + 6000)
    O.draw_tv(cr, TVX, FLOOR_Y, t, screen="off", sid=21950)
    draw_tv_screen(cr, t)
    draw_console_box(cr, HIS_TV + 330, FLOOR_Y + 10, s=0.8, sid=21960)
    draw_game_box(cr, HIS_TV + 470, FLOOR_Y + 10, s=0.7, ang=0.08)
    sketch_line(cr, [(TVX + 200, FLOOR_Y - 330), (TVX + 300, FLOOR_Y - 60), (HIS_TV - 20, FLOOR_Y - 230)], 5, sid=21970, amp=0.5)
S.background(store)

S.auto_blinks = False
S.blink(2.4, 9.9, 14.6)
S.hold_sign(0.0, 21.0, extra="I HAVE TIME.", write_at=6.6, push=False)
# camera: wide enough to show the demo TV still updating behind him, then a slow creep in on him + the sign
CAM0 = (HIS_TV - 210, 940, 0.94)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0
S.camera(0.5, HIS_TV - 190, 950, 1.00, 20.0)
S.set(4.0, "hold_front", "dead_stare", dur=0.12, look=(0.0, 0.85))       # eyes flick down to the sign...
S.set(4.7, "hold_front", "dead_stare", dur=0.12, look=(0.0, 0.0))        # ...and back to us
S.set(18.2, "hold_front", "dead_stare", dur=0.3, lid=1.0)                # one slow blink
S.set(18.65, "hold_front", "dead_stare", dur=0.35)

if __name__ == "__main__":
    S.render("day022.mp4")
