"""Day 4 — WAITING episode #3 (still no comments on days 1-3). The message is the star.

He stands centre, holding the sign up to us: TELL ME WHAT TO DO NEXT IN THE COMMENTS, with yesterday's line
"STILL HERE." still under it. Dead stare, a touch more slumped than yesterday (small lean, heavier lids). Breathing,
the odd blink, his eyes flick down to the sign once. The only beat: he turns the sign to himself and writes today's
line -- "DAY 4." -- turns it back and keeps staring. Slow blink. Hard cut. ~21 s.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M

SLUMP = dict(lean=0.025, lid=0.3)

S = M.Scene()
S.auto_blinks = False
S.blink(2.4, 9.9, 14.6)
S.hold_sign(0.0, 21.0, extra="DAY 4.", extra_shown="STILL HERE.", write_at=6.6)
S.set(0.0, "hold_front", "dead_stare", dur=0.0, **SLUMP)
S.set(4.0, "hold_front", "dead_stare", dur=0.12, look=(0.0, 0.85), **SLUMP)      # eyes flick down to the sign...
S.set(4.7, "hold_front", "dead_stare", dur=0.12, look=(0.0, 0.0), **SLUMP)       # ...and back to us
S.set(9.6, "hold_front", "dead_stare", dur=0.6, **SLUMP)                         # settles back into the slump
S.set(18.2, "hold_front", "dead_stare", dur=0.3, lean=0.025, lid=1.0)            # one slow blink
S.set(18.65, "hold_front", "dead_stare", dur=0.35, **SLUMP)

if __name__ == "__main__":
    S.render("day004.mp4")
