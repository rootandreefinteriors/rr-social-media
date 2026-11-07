"""Day 16 -- WAITING episode (no qualifying comment on day 15: the only new comment was "cool", a remark, not a request).
The message is the star.

He is still where day 15 left him: on the sunny beach, the rainbow behind him, the kite lying on the sand next to him.
He stands centre holding the sign up to us: TELL ME WHAT TO DO NEXT IN THE COMMENTS. Dead stare, breathing, the odd
blink, eyes flick down to the sign once. The only beat: he turns the sign to himself, writes "I'LL WAIT HERE.", turns
it back and keeps staring. Slow blink. Hard cut. ~21 s. Copied from tests/waiting_ref; only the place + line changed.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import objects as O
from ink import FLOOR_Y

# the beach exactly as day 15 left it (see ep015/episode.py)
BX = 700000.0
WX0, WX1 = BX - 6000.0, BX + 12000.0
PROM_END = BX - 1300.0
SUGAR = BX + 2600.0
RBX, RB = BX - 300.0 + 3600.0, 1500.0
LANDX = 705313.3938825098                    # his centre at the end of day 15
OX = LANDX - 540.0

S = M.Scene(x0=OX)
S.floor = False

def beach(cr, t):
    O.draw_beach_world(cr, t, WX0, WX1, PROM_END, sugar_x=SUGAR)
    O.draw_rainbow(cr, RBX, FLOOR_Y, RB + 30, band=60, sweep=1.0)
    O.draw_kite(cr, LANDX + 330, FLOOR_Y - 30, s=0.8, ang=1.35, t=0.0, tail=0.0)
S.background(beach)

S.auto_blinks = False
S.blink(2.4, 9.9, 14.6)
S.hold_sign(0.0, 21.0, extra="I'LL WAIT HERE.", write_at=6.6)
S.set(4.0, "hold_front", "dead_stare", dur=0.12, look=(0.0, 0.85))       # eyes flick down to the sign...
S.set(4.7, "hold_front", "dead_stare", dur=0.12, look=(0.0, 0.0))        # ...and back to us
S.set(18.2, "hold_front", "dead_stare", dur=0.3, lid=1.0)                # one slow blink
S.set(18.65, "hold_front", "dead_stare", dur=0.35)

if __name__ == "__main__":
    S.render("day016.mp4")
