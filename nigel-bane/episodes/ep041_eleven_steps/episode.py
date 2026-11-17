"""Day 41 — "Eleven steps" (posts as `… IIIII IIIII I shortening`). Room arc 2/4. IDEA: lives shrink so slowly you
never notice: the friend you stopped calling. The low ceiling (it came down in D40) still rests on the window frame.
C: "Count with me. Out loud." — he's at the tally wall, already turned toward the far wall. T (said early, a visible
yes/no): "It's twelve steps to that wall. It's always been twelve." Will he make twelve? He walks and counts, one step
per number, and the wall arrives at eleven. Again, back the other way, slower: eleven. R (someone else, one scene):
"There's probably someone you used to talk to every day..." — nobody decided; one week you didn't call. Implied lift:
"You'd know their laugh from another room." ENDING (caught): "You counted with me. I saw your lips move."
One continuous shot (user, 2026-11-17): the camera follows him and pulls out; no cuts.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import cairo
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, STAND, THINK, CHEST)

N.setup()
T, TE = N.T, N.TE
F = N.FLOOR_Y
W = N.words

def nth(text, n):
    """start time of the n-th word whose text (lowercased, stripped) is `text`"""
    c = 0
    for w in W:
        if w["text"].lower().strip(".,?!") == text:
            c += 1
            if c == n:
                return w["start"]
    raise KeyError(text)

NUMS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven"]
C1 = [nth(n, 1) for n in NUMS]                     # first count (walking right)
C2 = [nth(n, 2) for n in NUMS[:10]] + [nth("eleven", 3)]   # second count (walking back); "...Eleven." is #2
t_count, t_twelve2, t_eleven_b = T("count"), T("twelve", 2), nth("eleven", 2)
t_again, t_slower, t_theres, t_youd, t_nobody, t_it_didnt = T("again"), T("slower"), T("there's"), T("you'd"), T("nobody"), T("it", 2)
t_you_counted, t_saw, t_end = T("counted"), T("saw"), TE("move")

STEP = 92.0                                         # the engine's stride: one foot plant per 92 px
X0 = -130.0                                         # starts at the tally wall (hip at x 320)
X11 = X0 + 11 * STEP                                # hip x at the far wall = 1332
WALL_X = 1482.0                                     # the far wall
CEIL = 203.0                                        # the low ceiling, resting on the window frame (window top 205)

LOOK_WALL = P(STAND, look=(0.85, 0.0), tilt=0.04)
WALKP = P(STAND, look=(0.8, 0.05), swing=0.7)
HAND_WALL = P(STAND, relb=(545, 1010), rhand=(612, 985), look=(0.9, -0.1), tilt=0.06, swing=0.0)
STARE_WALL = P(HAND_WALL, eyescale=1.12)
TURN = P(STAND, look=(-0.6, 0.0), swing=0.0)
WALKBACK = P(STAND, look=(-0.8, 0.05), swing=0.7)
BACK_AT = P(STAND, look=(-0.3, 0.0), lelb=(380, 1060), lhand=(320, 1110), swing=0.0)
TO_US = P(STAND, look=(0.0, 0.05), swing=0.0)
SOFT = P(CHEST, look=(0.05, 0.1))
LAST = P(STAND, look=(0.0, 0.0), eyescale=1.08, swing=0.0)

pose_track = Track([
    (0, KNOCK, 0),
    (t_count - 0.3, LOOK_WALL, 0.8),
    (C1[0] - 0.6, WALKP, 0.4),
    (C1[10] + 0.1, HAND_WALL, 0.6),                 # the wall arrives: hand flat on it
    (t_eleven_b - 0.2, STARE_WALL, 0.5),
    (t_again - 0.3, TURN, 0.7),
    (C2[0] - 0.6, WALKBACK, 0.4),
    (C2[10] + 0.2, BACK_AT, 0.6),                   # back at the tally wall
    (t_theres - 0.3, TO_US, 0.8),
    (t_youd - 0.2, SOFT, 1.0),
    (t_nobody - 0.2, TO_US, 1.0),
    (t_it_didnt - 0.3, THINK, 1.0),
    (t_you_counted - 0.4, LAST, 0.9),
])

# one 92-px step per spoken number, landing on the word
xk = [(0, X0, 0)]
for k, tc in enumerate(C1):
    xk.append((tc - 0.5, X0 + (k + 1) * STEP, 0.55))
for k, tc in enumerate(C2):
    xk.append((tc - 0.6, X11 - (k + 1) * STEP, 0.7))      # slower
x_track = Track(xk)

cam_track = Track([                                        # ONE continuous shot
    (0, (470, 880, 1.6), 0),
    (t_count, (520, 1000, 1.1), 1.6),                      # ease back: him, the low ceiling, the far wall waiting
    (C1[10] + 0.4, (560, 960, 1.35), 1.6),                 # in a little on him at the wall
    (t_again - 0.2, (520, 1000, 1.1), 1.6),                # back out for the walk back
    (C2[10] + 0.4, (760, 1000, 0.74), 2.6),                # pull right out: the whole low room, wall to wall
    (t_nobody, (430, 910, 1.3), t_you_counted - t_nobody - 0.5),   # slow push in on him through the story
    (t_you_counted - 0.4, (340, 850, 1.8), 2.4),           # in close for the last line
    (t_saw + 0.6, (335, 840, 1.9), t_end - t_saw + 0.5),
])
follow_track = Track([(0, 0.0, 0), (C1[0] - 1.2, 1.0, 1.6), (C2[10] + 0.4, 0.0, 2.6)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (C1[6], mood_vec("unease"), 2.5),
    (t_eleven_b, mood_vec("uncanny"), 0.6),
    (t_again, mood_vec("unease"), 1.0),
    (t_theres, mood_vec("melancholy"), 1.5),
    (t_you_counted, mood_vec("lonely"), 1.2),
    (t_saw, mood_vec("uncanny"), 0.8),
])

DAY = dict(top=(150, 190, 225), bot=(220, 225, 232), clouds=0.6, cloud_v=1.2, sun=0.0, sun_y=0.3, sun_r=24)
sky = Track([(0, SKY(**DAY, drone=0.14), 0), (C1[8], SKY(**DAY, drone=0.24), 3.0),
             (t_eleven_b, SKY(**DAY, drone=0.0), 0.4), (t_theres, SKY(**DAY, drone=0.12), 2.0)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

CRACKS = [(60, 1.9, 11), (300, 2.2, 12), (520, 1.7, 13), (640, 2.0, 14), (1010, 1.9, 15)]
def room(cr, t, pose, env):
    """the low ceiling (resting on the window frame) and the far wall on the right"""
    cr.rectangle(-1600, -1600, 4200, CEIL + 1600)
    cr.set_source_rgba(0.93, 0.93, 0.925, 1.0); cr.fill()
    for k in range(3):
        yy = CEIL - 14 - k * 13
        N.path(cr, N.sketch_pts([(-1600, yy), (2600, yy)], amp=1.2, sid=200 + k, step=40))
        N.stroke_ink(cr, 1.2, alpha=0.18)
    N.path(cr, N.sketch_pts([(-1600, CEIL), (2600, CEIL)], amp=1.4, sid=210, step=40)); N.stroke_ink(cr, 4.0, alpha=0.85)
    for x0, s, sid in CRACKS:
        pts, px, py = [], x0, CEIL
        for j in range(7):
            pts.append((px, py)); px += (14 if j % 2 == 0 else -9) * s; py -= 9 * s
        N.path(cr, pts); N.stroke_ink(cr, 2.6, alpha=0.8)
    # the far wall: the side wall seen edge-on, a shaded plane beyond the corner line
    cr.rectangle(WALL_X, CEIL, 2200, F - CEIL)
    cr.set_source_rgba(0.9, 0.9, 0.895, 1.0); cr.fill()
    for k in range(9):
        xx = WALL_X + 30 + k * 34
        N.path(cr, N.sketch_pts([(xx, CEIL + 30), (xx + 60, F - 20)], amp=0.9, sid=230 + k, step=30))
        N.stroke_ink(cr, 1.3, alpha=0.16)
    N.path(cr, N.sketch_pts([(WALL_X, CEIL), (WALL_X, F)], amp=1.3, sid=220, step=30)); N.stroke_ink(cr, 4.2, alpha=0.9)

sfx = []
N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=40, under_hook=room, sfx=sfx,
            caption_avoid=[(0, 99, lambda t: (WALL_X - 20, CEIL, WALL_X + 900, F + 40))])
N.main("nigel_bane_ep041_eleven_steps.mp4")
