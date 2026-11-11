"""Day 37 — "Ceiling" (posts as `… IIIII II nearing`). IDEA: you lie under your ceiling every night and couldn't describe
it. C: "Lie down with me. ...On your back. Go on." — he's already lowering himself to the floor. T (a visible yes/no,
review 2026-11-11): the ceiling is shown at the top of the room for the first time, and every time we cut back to the
wide shot it is lower; will it come down onto the window? It comes to rest on the window's top frame on the last line.
Nigel notices ("Mine's lower than it was. ...No. It isn't. [whispers] It is."). R (the question): "Now think of yours.
Don't look. What colour is it, exactly?" — then ~5 s of real silence; he never answers it. Unsettling line: the
whispered "It is." Implied lift: his hand raised toward it, "Not past it. At it." — he is looking at it, properly.
ENDING (admission): "I count the cracks up there every night. ...Five. I don't remember the number going up." (four
cracks in the earlier wide shots, five in the last).
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, STAND)

N.setup()
T, TE = N.T, N.TE

LIE = P(head=(300, 1306), neck=(466, 1442), hip=(735, 1452),
        lelb=(560, 1456), lhand=(650, 1462), relb=(585, 1440), rhand=(680, 1432),
        lknee=(850, 1455), lfoot=(962, 1470), rknee=(845, 1446), rfoot=(958, 1462),
        tilt=-math.pi / 2, look=(1.0, 0.0), swing=0.0)
KNEEL = P(STAND, head=(430, 1120), neck=(445, 1240), hip=(470, 1390), lknee=(420, 1470), lfoot=(560, 1476),
          rknee=(450, 1468), rfoot=(590, N.FLOOR_Y), lelb=(400, 1330), lhand=(380, 1440),
          relb=(520, 1330), rhand=(560, 1420), tilt=0.1, look=(0.2, 0.6), swing=0.0)
LIE_UP = P(LIE, look=(1.0, 0.0))                                   # straight up at the ceiling
LIE_REACH = P(LIE, relb=(620, 1360), rhand=(700, 1250), finger=1.0, look=(0.95, 0.25))   # "Not past it. At it."
LIE_CAM = P(LIE, look=(0.1, 0.9), eyescale=1.06)                   # eyes slide over to us
LIE_WIDE = P(LIE_UP, eyescale=1.16)                                # "Mine's lower than it was."
LIE_SHUT = P(LIE_UP, shut=1.0)
LIE_LAST = P(LIE_UP, eyescale=1.1, look=(1.0, -0.15))

t_lie, t_back, t_thats, t_not, t_at = T("lie"), T("back"), T("that's"), T("not"), T("at", 2)
t_now, t_what, t_match_e, t_youve = T("now"), T("what"), TE("match"), T("you've")
t_and, t_mines, t_no, t_isnt, t_is, t_i_count, t_five, t_end = (
    T("and"), T("mine's"), T("no"), T("isn't"), T("is", 4), T("count"), T("five"), TE("up", 2))

pose_track = Track([
    (0, KNOCK, 0),
    (t_lie - 0.3, KNEEL, 0.8),
    (t_lie + 0.6, LIE, 1.1),
    (t_thats - 0.2, LIE_UP, 0.6),
    (t_not - 0.3, LIE_REACH, 0.9),
    (t_now - 0.2, LIE_UP, 0.9),
    (t_what - 0.4, LIE_CAM, 0.8),
    (t_youve - 0.4, LIE_UP, 1.0),
    (t_mines - 0.3, LIE_WIDE, 0.5),
    (t_no + 0.4, LIE_SHUT, 0.25),
    (t_is - 0.5, LIE_WIDE, 0.2),
    (t_i_count - 0.3, LIE_LAST, 1.0),
])
x_track = Track([(0, 0.0, 0)])

WIDE = (540, 960, 1.0)
cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_lie, (520, 1180, 1.25), 1.4),                  # follow him down to the floor
    (t_thats - 0.1, WIDE, 0),                         # CUT: the whole room, the ceiling at the top (4 cracks)
    (t_thats + 0.1, (540, 930, 1.04), t_now - t_thats),
    (t_now - 0.15, (360, 1250, 2.0), 0),              # CUT: close on him lying, face up
    (t_now, (350, 1265, 2.3), t_youve - t_now - 0.3), # slow push through the question and the silence
    (t_youve - 0.15, WIDE, 0),                        # CUT: wide — it's lower
    (t_youve, (540, 940, 1.03), t_and - t_youve),
    (t_and - 0.1, (330, 1280, 2.5), 0),               # CUT: close on his eyes
    (t_mines - 0.15, WIDE, 0),                        # CUT: wide — lower again; he sees it
    (t_mines, (540, 950, 1.02), 2.0),
    (t_isnt + 0.5, (320, 1285, 3.0), 0),              # CUT: extreme close on his eyes ("It is.")
    (t_isnt + 0.6, (316, 1290, 3.3), 2.6),
    (t_i_count - 0.2, WIDE, 0),                       # CUT: wide — resting on the window; five cracks
    (t_i_count, (540, 955, 1.04), t_end - t_i_count + 2.5),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_lie, mood_vec("drifting"), 1.0),
    (t_now, mood_vec("lonely"), 1.2),
    (t_youve, mood_vec("melancholy"), 1.5),
    (t_mines, mood_vec("unease"), 0.6),
    (t_is - 0.5, mood_vec("uncanny"), 0.5),
    (t_i_count, mood_vec("lonely"), 1.6),
])

EVE = dict(top=(34, 44, 92), bot=(104, 92, 138), clouds=0.15, cloud_v=2.0, stars=0.35, sun=0.0, sun_y=0.3, sun_r=24)
sky = Track([(0, SKY(**EVE, drone=0.22), 0),
             (t_match_e, SKY(**EVE, drone=0.0), 0.6),          # the question: real silence
             (t_youve - 0.2, SKY(**EVE, drone=0.18), 0.8),
             (t_mines, SKY(**EVE, drone=0.3), 2.0),
             (t_i_count, SKY(**EVE, drone=0.16), 2.0)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

# the ceiling: its underside steps lower at every cut back to the wide shot (it never moves on screen)
STEPS = [(0, 62.0, 4), (t_youve - 0.2, 112.0, 4), (t_mines - 0.2, 158.0, 4), (t_i_count - 0.25, 194.0, 5)]
CRACKS = [(60, 1.9, 11), (300, 2.2, 12), (520, 1.7, 13), (640, 2.0, 14), (1010, 1.9, 15)]
_order = [0, 2, 3, 4, 1]   # the fifth crack is the one in the middle-left
def ceiling(cr, t, pose, env):
    y, n = STEPS[0][1], STEPS[0][2]
    for ts, yy, nn in STEPS:
        if t >= ts:
            y, n = yy, nn
    cr.rectangle(-600, -1200, 2400, y + 1200)
    cr.set_source_rgba(0.93, 0.93, 0.925, 1.0); cr.fill()
    for k in range(3):                                   # faint pencil shading on its face
        yy = y - 14 - k * 13
        N.path(cr, N.sketch_pts([(-600, yy), (1800, yy)], amp=1.2, sid=200 + k, step=40))
        N.stroke_ink(cr, 1.2, alpha=0.18)
    N.path(cr, N.sketch_pts([(-600, y), (1800, y)], amp=1.4, sid=210, step=40)); N.stroke_ink(cr, 4.0, alpha=0.85)
    for i in _order[:n]:                                 # hairline cracks running up from the underside
        x0, s, sid = CRACKS[i]
        pts, px, py = [], x0, y
        for j in range(7):
            pts.append((px, py))
            px += (14 if j % 2 == 0 else -9) * s
            py -= 9 * s
        N.path(cr, pts); N.stroke_ink(cr, 2.6, alpha=0.8)
        N.path(cr, [pts[3], (pts[3][0] + 16 * s, pts[3][1] - 6 * s)]); N.stroke_ink(cr, 1.2, alpha=0.6)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=36, under_hook=ceiling)
N.BLINKS = [b for b in N.BLINKS if not (t_match_e < b < t_youve) and not (t_no - 0.3 < b < t_is + 0.3)]
N.main("nigel_bane_ep037_ceiling.mp4")
