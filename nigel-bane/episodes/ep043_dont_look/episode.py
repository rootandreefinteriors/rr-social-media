"""Day 43 — "Don't look" (posts as `… IIIII IIIII III unwatching`). Room arc 4/4, the resolution (re-varied in the lost
2026-11-16 review so D41 and D43 aren't both step counts). IDEA: measuring a life makes it smaller. The room is still
as narrow as the window, the ceiling low. C: "Close your eyes with me. ...No. Not you. You keep yours open. Watch the
walls for me." R (the swap): he asks you to watch for him, because he can't. T (a visible yes/no): the walls drift
outward and the ceiling lifts, slowly, ON CAMERA, but only while his eyes are shut. Will it come back? "If I look, it
stops." He peeks: it stops ("It moved. Didn't it."). He shuts them again and it keeps going until the room is its old
size. "I used to count everything in here... every time I counted, the room was exactly that big." Unsettling line:
"Somewhere in your head, you know how much of this video is left." ENDING (flip of the command): "You can stop
watching the walls now. ...You won't, though." — his eyes open on the last line, on us. One continuous shot.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, STAND, OPEN, THINK)

N.setup()
T, TE = N.T, N.TE
F = N.FLOOR_Y
OFF = 390.0

t_close, t_no, t_watch, t_moving, t_dont, t_have, t_moved, t_okay, t_shutting = (
    T("close"), T("no"), T("watch"), T("moving"), T("don't"), T("have"), T("moved"), T("okay"), T("shutting"))
t_used, t_counted, t_somewhere, t_isit, t_keeping, t_youcan, t_wont, t_end = (
    T("used"), T("counted"), T("somewhere"), T("back"), T("keeping", 2), T("can"), T("won't"), TE("though"))

SHUT0 = t_close + 0.6                 # his eyes close
PEEK0 = t_have + 0.5                  # "...I have to look." — they open
SHUT1 = t_shutting + 0.4              # "Shutting them again."
OPEN_END = t_wont - 0.2               # the last line: eyes open, on us

CLOSED = P(STAND, shut=1.0, look=(0.0, 0.1), tilt=0.02, swing=0.0)
PRESENT_SHUT = P(OPEN, shut=1.0, look=(0.0, 0.1), swing=0.0)
WHISPER = P(STAND, shut=1.0, look=(0.0, 0.15), tilt=-0.06, relb=(520, 1090), rhand=(500, 1010), swing=0.0)
PEEK_L = P(STAND, shut=0.0, look=(-0.85, 0.05), eyescale=1.12, swing=0.0)
PEEK_R = P(STAND, shut=0.0, look=(0.85, 0.05), eyescale=1.12, swing=0.0)
PEEK_US = P(STAND, shut=0.0, look=(0.0, 0.0), eyescale=1.08, swing=0.0)
CLOSED_THINK = P(THINK, shut=1.0, look=(-0.2, -0.3))
CLOSED_US = P(STAND, shut=1.0, look=(0.0, 0.0), tilt=0.04, swing=0.0)
LAST = P(STAND, shut=0.0, look=(0.0, 0.0), eyescale=1.1, swing=0.0)

pose_track = Track([
    (0, KNOCK, 0),
    (t_close - 0.2, CLOSED, 0.8),
    (t_watch - 0.3, PRESENT_SHUT, 0.9),           # "Watch the walls for me." — hands open toward them
    (t_moving - 0.4, WHISPER, 0.8),
    (PEEK0, PEEK_L, 0.35),                         # eyes open: left wall...
    (PEEK0 + 0.9, PEEK_R, 0.5),                    # ...right wall
    (t_moved + 0.6, PEEK_US, 0.5),                 # "Didn't it." — to us
    (SHUT1, CLOSED, 0.6),
    (t_used - 0.3, CLOSED_THINK, 1.2),
    (t_somewhere - 0.4, CLOSED_US, 1.2),
    (OPEN_END, LAST, 0.5),
])
x_track = Track([(0, OFF, 0)])

# the room only grows while his eyes are shut: it drifts outward in two runs and stops dead while he looks
GROW1, GROW2 = SHUT0 + 1.0, SHUT1 + 0.8
lw = Track([(0, 650.0, 0), (GROW1, 540.0, PEEK0 - GROW1 - 0.2), (GROW2, -520.0, 26.0)])
rw = Track([(0, 1030.0, 0), (GROW1, 1140.0, PEEK0 - GROW1 - 0.2), (GROW2, 2200.0, 26.0)])
ceil = Track([(0, 203.0, 0), (GROW1, 150.0, PEEK0 - GROW1 - 0.2), (GROW2, -700.0, 26.0)])

cam_track = Track([                                        # ONE continuous shot
    (0, (OFF + 470, 880, 1.6), 0),
    (t_no - 0.2, (840, 1000, 1.05), 2.4),                  # ease out: the narrow room, his eyes shut
    (t_moving, (840, 1000, 0.92), PEEK0 - t_moving - 0.4), # a slow drift wider as the walls go
    (PEEK0 - 0.2, (830, 920, 1.25), 1.6),                  # in on him as he looks
    (SHUT1, (820, 1000, 0.85), 6.0),                       # out again while it grows
    (t_somewhere - 2.0, (800, 1000, 0.68), 9.0),           # the whole room, back to its size
    (t_youcan - 0.5, (840, 900, 1.35), t_end - t_youcan + 0.2),   # slow push in for the last line
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_close, mood_vec("drifting"), 1.0),
    (PEEK0, mood_vec("unease"), 0.5),
    (SHUT1, mood_vec("drifting"), 1.5),
    (t_used, mood_vec("melancholy"), 2.0),
    (t_somewhere, mood_vec("uncanny"), 1.5),
    (t_isit, mood_vec("awe"), 3.0),
    (OPEN_END, mood_vec("uncanny"), 0.5),
])

NIGHT = dict(top=(18, 24, 60), bot=(52, 50, 96), clouds=0.1, cloud_v=0.6, stars=0.6, sun=0.0, sun_y=0.3, sun_r=24)
sky = Track([(0, SKY(**NIGHT, drone=0.16), 0), (t_moving + 0.6, SKY(**NIGHT, drone=0.0), 0.8),
             (PEEK0, SKY(**NIGHT, drone=0.1), 0.5), (SHUT1, SKY(**NIGHT, drone=0.06), 2.0)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

CRACKS = [(720, 1.4, 11), (860, 1.6, 12), (940, 1.3, 13)]
def room(cr, t, pose, env):
    """the ceiling and the two side walls, wherever they've drifted to; the tally redrawn on top"""
    L, R, C = lw.at(t), rw.at(t), ceil.at(t)
    cr.rectangle(-4000, -4000, 9000, C + 4000)
    cr.set_source_rgba(0.93, 0.93, 0.925, 1.0); cr.fill()
    for k in range(3):
        yy = C - 14 - k * 13
        N.path(cr, N.sketch_pts([(-4000, yy), (5000, yy)], amp=1.2, sid=200 + k, step=40)); N.stroke_ink(cr, 1.2, alpha=0.18)
    N.path(cr, N.sketch_pts([(-4000, C), (5000, C)], amp=1.4, sid=210, step=40)); N.stroke_ink(cr, 4.0, alpha=0.85)
    for x0, s, sid in CRACKS:
        pts, px, py = [], x0, C
        for j in range(7):
            pts.append((px, py)); px += (14 if j % 2 == 0 else -9) * s; py -= 9 * s
        N.path(cr, pts); N.stroke_ink(cr, 2.4, alpha=0.8)
    for x0, x1, left, sid in ((-4000, L, True, 300), (R, 5000, False, 320)):
        cr.rectangle(x0, C, x1 - x0, F - C); cr.set_source_rgba(0.9, 0.9, 0.895, 1.0); cr.fill()
        for k in range(40):
            xx = (L - 40 - k * 34) if left else (R + 40 + k * 34)
            N.path(cr, N.sketch_pts([(xx, max(C, -1200) + 30), (xx + (-50 if left else 50), F - 20)], amp=0.9, sid=sid + k, step=30))
            N.stroke_ink(cr, 1.3, alpha=0.14)
    for x, sid in ((L, 340), (R, 341)):
        N.path(cr, N.sketch_pts([(x, C), (x, F)], amp=1.3, sid=sid, step=30)); N.stroke_ink(cr, 4.2, alpha=0.9)
    N.draw_tally(cr, t)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track, tally_base=42, under_hook=room)
N.BLINKS = [b for b in N.BLINKS if not (PEEK0 - 0.3 < b < SHUT1 + 0.3)]   # wide-eyed while he looks
N.main("nigel_bane_ep043_dont_look.mp4")
