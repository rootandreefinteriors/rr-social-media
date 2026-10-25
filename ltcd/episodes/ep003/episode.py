"""Day 3 — WAITING episode #2 (still no comments on day 1 or day 2). The message is the star.

He stands centre, holding the sign up to us: TELL ME WHAT TO DO NEXT IN THE COMMENTS, with yesterday's line
"I'LL WAIT." still under it. Dead stare. Breathing, the odd blink, his eyes flick down to the sign once. The only beat:
he turns the sign to himself and writes today's line -- "STILL HERE." -- turns it back and keeps staring. Slow blink.
Hard cut. ~21 s.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M

S = M.Scene()
S.auto_blinks = False
S.blink(2.4, 9.9, 14.6)
S.hold_sign(0.0, 21.0, extra="STILL HERE.", extra_shown="I'LL WAIT.", write_at=6.6)
S.set(4.0, "hold_front", "dead_stare", dur=0.12, look=(0.0, 0.85))       # eyes flick down to the sign...
S.set(4.7, "hold_front", "dead_stare", dur=0.12, look=(0.0, 0.0))        # ...and back to us
S.set(18.2, "hold_front", "dead_stare", dur=0.3, lid=1.0)                # one slow blink
S.set(18.65, "hold_front", "dead_stare", dur=0.35)

if __name__ == "__main__":
    S.render("day003.mp4")
