"""Day 23 -- WAITING episode (no comments yet on the day 22 posts, TikTok or Instagram).
The message is the star.

He is still where day 22 left him: on the sidewalk of the neon crime-game city, sunset sky, the striped sun, the
bent palm behind him, $999,999,999 lying all over the ground, his phone face-down at his feet, the HUD still up with
the five wanted stars flashing (the money counter, the minimap - the leading lady's dot is gone).
He stands holding the sign up to us: TELL ME WHAT TO DO NEXT IN THE COMMENTS. Dead stare, breathing, the odd blink,
eyes flick down to the sign once. The only beat: he turns the sign to himself, writes "STILL WANTED.", turns it back
and keeps staring. Slow blink. Hard cut. ~21 s. Copied from tests/waiting_ref; only the place + line changed.
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import objects as O
from ink import FLOOR_Y, sketch_line, draw_text

sk_rect = O.sketch_rect

# THE NEON GAME CITY exactly as day 22 left it (see ep022/episode.py neon())
NX = 9000000.0
DOOR_X = NX - 1150.0
PALM_X = NX - 160.0
HX = NX + 360.0                       # a step right of where he did the ask on day 22 (NX+140), clear of the bent palm

S = M.Scene(x0=HX - 540)
S.floor = False

SKY = [(-3000, (0.30, 0.16, 0.45)), (-200, (0.55, 0.22, 0.58)), (300, (0.88, 0.36, 0.55)), (650, (0.98, 0.55, 0.45)), (850, (1.0, 0.72, 0.42))]
HORIZON = FLOOR_Y - 430

_r = random.Random(22)                # same money as day 22, lying where it landed
BILLS = []
for i in range(46):
    x = NX - 500 + _r.uniform(0, 1500); _r.uniform(0, 1)
    _r.uniform(1.1, 1.6); _r.uniform(0, 6.28)
    BILLS.append((x, FLOOR_Y + _r.uniform(-10, 60), _r.uniform(-0.5, 0.5)))

def neon(cr, t):
    x0, x1 = NX - 4000, NX + 4000
    for i, (y, c) in enumerate(SKY):
        y1 = SKY[i + 1][0] if i + 1 < len(SKY) else HORIZON
        cr.rectangle(x0, y, x1 - x0, y1 - y + 1); cr.set_source_rgb(*c); cr.fill()
    sx, sy, r = NX + 520, HORIZON, 330
    cr.save(); cr.arc(sx, sy, r, math.pi, 2 * math.pi); cr.close_path(); cr.clip()
    cr.rectangle(sx - r, sy - r, 2 * r, r); cr.set_source_rgb(1.0, 0.86, 0.35); cr.fill()
    for k in range(5):
        yy = sy - 40 - 52 * k; hgt = 16 - 3 * k
        cr.rectangle(sx - r, yy, 2 * r, hgt); cr.set_source_rgb(0.98, 0.55, 0.45); cr.fill()
    cr.restore()
    cr.rectangle(x0, HORIZON, x1 - x0, 160); cr.set_source_rgb(0.20, 0.62, 0.72); cr.fill()
    for k in range(6):
        yy = HORIZON + 20 + 24 * k
        sketch_line(cr, [(sx - 260 + 30 * k, yy), (sx + 260 - 30 * k, yy)], 4, sid=22400 + k, color=(1.0, 0.85, 0.5))
    cr.rectangle(x0, HORIZON + 160, x1 - x0, 110); cr.set_source_rgb(0.98, 0.88, 0.66); cr.fill()
    cr.rectangle(x0, HORIZON + 270, x1 - x0, FLOOR_Y - HORIZON - 270 + 1); cr.set_source_rgb(0.86, 0.82, 0.86); cr.fill()
    cr.rectangle(x0, FLOOR_Y, x1 - x0, 900); cr.set_source_rgb(0.24, 0.22, 0.30); cr.fill()
    for k in range(-12, 12):
        cr.rectangle(NX + 360 * k, FLOOR_Y + 160, 180, 18); cr.set_source_rgb(1.0, 0.85, 0.3); cr.fill()
    cr.rectangle(x0, FLOOR_Y - 6, x1 - x0, 14); cr.set_source_rgb(0.98, 0.45, 0.70); cr.fill()
    sketch_line(cr, [(x0, FLOOR_Y), (x1, FLOOR_Y)], 6, sid=22410, amp=0.3)
    for k, px in enumerate((NX - 900, NX - 380, NX + 1150, NX + 1600, NX - 1800)):
        O.draw_palm(cr, px, t, h=560, s=0.7, yb=HORIZON + 270, sid=22420 + 7 * k)
    hx0, hx1, hy = NX - 2100, NX - 1250, HORIZON - 420
    sk_rect(cr, hx0, hy, hx1, HORIZON + 270, 6, sid=22440, fill=(0.98, 0.78, 0.85))
    sk_rect(cr, (hx0 + hx1) / 2 - 90, hy - 160, (hx0 + hx1) / 2 + 90, hy, 6, sid=22441, fill=(0.98, 0.78, 0.85))
    for r_ in range(4):
        for c_ in range(5):
            sk_rect(cr, hx0 + 50 + 160 * c_, hy + 60 + 150 * r_, hx0 + 140 + 160 * c_, hy + 140 + 150 * r_, 4,
                    sid=22450 + r_ * 5 + c_, fill=(0.35, 0.80, 0.85))
    draw_text(cr, "OCEAN VIEW", (hx0 + hx1) / 2, hy - 80, 50, color=(60, 230, 230))
    sk_rect(cr, DOOR_X - 2400, FLOOR_Y - 1500, DOOR_X - 200, FLOOR_Y, 7, sid=22460, fill=(0.28, 0.20, 0.40))
    sk_rect(cr, DOOR_X - 520, FLOOR_Y - 640, DOOR_X - 220, FLOOR_Y, 6, sid=22461, fill=(0.55, 0.30, 0.85))
    draw_text(cr, "GAME CAVE", DOOR_X - 900, FLOOR_Y - 1050, 90, color=(255, 120, 220))
    O.draw_palm(cr, PALM_X, t, h=900, bend=0.5, sid=22480)          # the palm he bent on day 22
S.background(neon)

def draw_phone_floor(cr, x, y, s, t, p):
    cr.save(); cr.translate(x, y); cr.scale(1.0, 0.35); cr.rotate(0.3)
    sk_rect(cr, -58, -100, 58, 100, 5, sid=22610, fill=(0.12, 0.12, 0.16)); cr.restore()
S.place("phone_floor", draw_phone_floor, (NX + 290, FLOOR_Y - 12), t_on=0.0, layer="front")

def money_floor(cr, t, p, ly):
    if ly != "front": return
    for i, (x, yl, al) in enumerate(BILLS):
        O.draw_dollar(cr, x, yl, s=0.55, ang=al, sid=24150 + (i % 5) * 3)
S.prop(money_floor)

def hud(cr, t):                      # the HUD never went away: minimap, the money, five flashing stars
    cx, cy, r = 150, 480, 80
    cr.save(); cr.arc(cx, cy, r, 0, 2 * math.pi); cr.set_source_rgba(0.15, 0.20, 0.25, 0.8); cr.fill_preserve()
    cr.set_source_rgba(1, 1, 1, 1); cr.set_line_width(6); cr.stroke()
    cr.arc(cx, cy, r - 3, 0, 2 * math.pi); cr.clip()
    for k in range(-3, 4):
        cr.rectangle(cx - r, cy + 40 * k - 5, 2 * r, 10); cr.set_source_rgb(0.6, 0.6, 0.65); cr.fill()
    cr.rectangle(cx + 20, cy - r, 12, 2 * r); cr.set_source_rgb(0.6, 0.6, 0.65); cr.fill()
    cr.move_to(cx, cy - 16); cr.line_to(cx + 12, cy + 12); cr.line_to(cx - 12, cy + 12); cr.close_path()
    cr.set_source_rgb(1, 1, 1); cr.fill()
    cr.restore()
    draw_text(cr, "$999,999,999", 70, 150, 38, color=(90, 220, 110), anchor="left")
    flash_on = int(t * 4) % 2 == 0
    for k in range(5):
        O.draw_star(cr, 92 + 56 * k, 215, 24, color=(0.35, 0.55, 1.0) if flash_on else (1.0, 0.85, 0.2))
S.overlay(hud)

S.auto_blinks = False
S.blink(2.4, 9.9, 14.6)
S.hold_sign(0.0, 21.0, extra="STILL WANTED.", write_at=6.6, push=False)
CAM0 = (HX - 210, 940, 0.94)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0
S.camera(0.5, HX - 190, 950, 1.00, 20.0)
S.set(4.0, "hold_front", "dead_stare", dur=0.12, look=(0.0, 0.85))       # eyes flick down to the sign...
S.set(4.7, "hold_front", "dead_stare", dur=0.12, look=(0.0, 0.0))        # ...and back to us
S.set(18.2, "hold_front", "dead_stare", dur=0.3, lid=1.0)                # one slow blink
S.set(18.65, "hold_front", "dead_stare", dur=0.35)

if __name__ == "__main__":
    S.render("day023.mp4")
