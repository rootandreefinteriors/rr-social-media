"""Day 38 — "Under the chair" (posts as `… IIIII III unblinking`). Mouse arc 3/4. IDEA: something in your home has
probably watched you sleep. Night. C: "Don't blink. Watch it with me." — he's already down low on the floor, facing
the tagged chair. Two small eyes shine in the shadow under the seat. T (said early): "It stares until you look away.
Then it's gone. I'm not looking away." A staring match: close-ups cut between his eyes and the two dots; no blinks;
the silences get longer; "My eyes are stinging. ...I can't..." — he blinks, and the dots are gone. R (the turn): he
only talks about the mouse watching him sleep, then "Something in your home has probably watched you sleep. With your
mouth open." Unsettling line: that one. ENDING (question): "How many things in your home have watched you sleep?
...You don't know either."
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import cairo
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, STAND)

N.setup()
T, TE = N.T, N.TE
F = N.FLOOR_Y
CHAIR_X = 900

LOW = P(STAND, hip=(380, 1400), neck=(500, 1330), head=(610, 1290),
        lknee=(450, 1470), lfoot=(290, 1476), rknee=(470, 1466), rfoot=(310, F),
        lelb=(520, 1440), lhand=(590, 1470), relb=(540, 1430), rhand=(610, 1466),
        tilt=0.12, look=(1.0, 0.25), swing=0.0)
LOW_HARD = P(LOW, eyescale=1.14)                       # eyes wide, straining
LOW_CAM = P(LOW, look=(0.3, -0.1), eyescale=1.06)      # a glance toward us, eyes still open
LOW_LAST = P(LOW, look=(0.25, -0.05), eyescale=1.0)

t_dont, t_under, t_stares, t_im, t_away2_e, t_it_does, t_something, t_my, t_cant_e, t_gone2, t_how, t_end = (
    T("don't"), T("under"), T("stares"), T("i'm"), TE("away", 2), T("does"), T("something"), T("my"),
    TE("can't"), T("gone", 2), T("how"), TE("either"))
BLINK = t_cant_e + 1.1                               # the one blink he loses on

pose_track = Track([
    (0, KNOCK, 0),
    (t_dont - 0.3, LOW, 1.2),
    (t_im - 0.2, LOW_HARD, 0.6),
    (t_something - 0.3, LOW_CAM, 0.8),
    (t_my - 0.3, LOW_HARD, 0.5),
    (t_how - 0.4, LOW_LAST, 1.0),
])
def strain(t, p):
    if t_my < t < BLINK:                               # eyes trembling, fighting the blink
        p["eyescale"] = p.get("eyescale", 1.0) + 0.02 * math.sin(t * 31)
    if BLINK <= t < BLINK + 0.35:
        p["shut"] = 1.0
    return p
x_track = Track([(0, 0.0, 0)])

EYES = (880, 1428)
cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_dont, (620, 1250, 1.2), 1.4),                    # down low with him; the chair beyond
    (t_under - 0.1, (880, 1400, 2.6), 0),               # CUT: under the chair, two eyes
    (t_under, (880, 1405, 2.8), t_stares - t_under),
    (t_stares - 0.1, (560, 1300, 2.2), 0),              # CUT: his eyes
    (t_im - 0.1, (700, 1340, 1.45), 0),                 # CUT: two-shot, the long stare
    (t_im, (710, 1345, 1.55), t_it_does - t_im),
    (t_it_does - 0.1, (880, 1410, 3.2), 0),             # CUT: the dots, closer
    (t_it_does, (880, 1412, 3.4), t_something - t_it_does),
    (t_something - 0.1, (575, 1290, 2.6), 0),           # CUT: his face, to us
    (t_my - 0.1, (560, 1295, 3.4), 0),                  # CUT: extreme close on his straining eyes
    (t_my, (556, 1296, 3.7), BLINK - t_my),
    (BLINK + 0.15, (880, 1405, 2.8), 0),                # CUT: under the chair: empty
    (t_how - 0.1, (650, 1250, 1.3), 0),                 # CUT: wide, him and the empty dark under the chair
    (t_how, (660, 1260, 1.38), t_end - t_how + 2),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_under, mood_vec("uncanny"), 1.0),
    (t_im, mood_vec("unease"), 1.0),
    (t_it_does, mood_vec("lonely"), 1.5),
    (t_something, mood_vec("uncanny"), 1.2),
    (t_my, mood_vec("unease"), 0.6),
    (BLINK + 0.2, mood_vec("void"), 0.4),
    (t_how, mood_vec("uncanny"), 1.2),
])

NIGHT = dict(top=(16, 20, 48), bot=(40, 38, 80), clouds=0.0, cloud_v=0.0, stars=0.55, sun=0.0, sun_y=0.3, sun_r=24)
sky = Track([(0, SKY(**NIGHT, drone=0.22), 0), (t_im, SKY(**NIGHT, drone=0.06), 1.5), (t_my, SKY(**NIGHT, drone=0.0), 1.0),
             (t_how, SKY(**NIGHT, drone=0.16), 1.5)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

def under(cr, t, pose, env):
    """the chair, a soft pencil shadow under its seat, and two small eyes in it until he blinks"""
    s = 1.1
    seat_y = F - 170 * s
    x0, x1 = CHAIR_X - 64 * s, CHAIR_X + 64 * s + 34 * s
    cr.save(); cr.rectangle(x0, seat_y + 14, x1 - x0, F - seat_y - 14); cr.clip()
    cx, cy = EYES[0] + 10, EYES[1] - 10
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, 150)
    g.add_color_stop_rgba(0, 0.18, 0.18, 0.22, 0.62); g.add_color_stop_rgba(0.55, 0.2, 0.2, 0.24, 0.3)
    g.add_color_stop_rgba(1, 0.2, 0.2, 0.24, 0.0)
    cr.set_source(g); cr.paint()
    for k in range(7):                                  # a little pencil hatching in the darkest part
        xx = cx - 70 + k * 22
        N.path(cr, N.sketch_pts([(xx + 20, cy - 50), (xx - 14, F - 10)], amp=0.8, sid=400 + k, step=12))
        N.stroke_ink(cr, 1.2, alpha=0.2)
    cr.restore()
    N.draw_chair(cr, CHAIR_X, scale=s, tag=True, tag_swing=0.0)
    if t_under - 0.6 < t < BLINK:
        a = min(1.0, (t - t_under + 0.6) / 0.6)
        blink = 1.0
        for bt in (t_it_does + 2.2, t_something + 1.0):  # the mouse blinks, once or twice
            if bt < t < bt + 0.14:
                blink = 0.15
        for dx in (-14, 14):
            ex, ey = EYES[0] + dx, EYES[1]
            gl = cairo.RadialGradient(ex, ey, 0, ex, ey, 20)
            gl.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.55 * a); gl.add_color_stop_rgba(1, 1, 0.95, 0.8, 0)
            cr.set_source(gl); cr.arc(ex, ey, 20, 0, 2 * math.pi); cr.fill()
            cr.save(); cr.translate(ex, ey); cr.scale(1, blink)
            cr.set_source_rgba(1, 0.97, 0.88, a); cr.arc(0, 0, 5.6, 0, 2 * math.pi); cr.fill(); cr.restore()

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=37, under_hook=under, pose_hook=strain,
            caption_avoid=[(0, 99, lambda t: (CHAIR_X - 110, F - 430, CHAIR_X + 140, F + 30))])
N.BLINKS = [b for b in N.BLINKS if not (t_dont < b < BLINK + 1.0)]   # no blinks during the staring match
N.main("nigel_bane_ep038_under_chair.mp4")
