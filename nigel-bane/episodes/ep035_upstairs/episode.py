"""Day 35 — "Upstairs" (DREAD; posts as `… IIIII creaking`). Night. C (whispered): "Quiet. Look up." — he freezes with
his eyes on the ceiling as heavy footsteps cross the floor above, left to right, and stop right over him. "There's no
upstairs. I've checked." A little dust sifts down. T: the steps stop, hold, and later cross back the other way; he
never moves. R (one scene): late in bed, one creak out in the hall; you lay very still, decided it was the house, and
went back to sleep. "I'm not going to look either." ENDING (instruction for after): "Tonight, when you hear it,
don't decide what it is." Featured sound: the footsteps overhead (stereo, crossing).
"""
import math
import os
import random
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, smooth, KNOCK)

N.setup()
T, TE = N.T, N.TE

UP = P(look=(0.0, -0.95), tilt=0.0, eyescale=1.14, swing=0.0, lelb=(415, 1110), lhand=(420, 1200), relb=(488, 1110), rhand=(482, 1200))
UP_R = P(UP, look=(0.45, -0.9), tilt=0.05)
UP_L = P(UP, look=(-0.45, -0.9), tilt=-0.05)
STILL = P(UP, eyescale=1.18)
TO_YOU = P(look=(0.0, 0.02), tilt=0.0, eyescale=1.06, swing=0.0, lelb=(415, 1110), lhand=(420, 1200), relb=(488, 1110), rhand=(482, 1200))
SCENE = P(TO_YOU, look=(0.0, 0.0), tilt=0.04)

t_quiet, t_up_e, t_theres, t_room_e, t_stopped_e = T("quiet"), TE("up"), T("there's"), TE("room"), TE("stopped")
t_youve, t_im, t_either_e, t_tonight, t_end = T("you've"), T("i'm"), TE("either"), T("tonight"), TE("is")

# the steps: across (left → right) and stop overhead; later back the other way, fading
STEPS1 = [t_up_e + 0.3 + 0.62 * k for k in range(7)]
STEPS2 = [t_either_e + 0.4 + 0.66 * k for k in range(7)]
sfx = [(ts, "step_above", 0.55, -0.5 + k * 0.5 / 6) for k, ts in enumerate(STEPS1)]
sfx += [(ts, "step_above", 0.5 * (1 - 0.1 * k), -k * 0.5 / 6) for k, ts in enumerate(STEPS2)]
STOP = STEPS1[-1]

def jolt(t, p):   # a tiny flinch at each step overhead
    for ts in STEPS1 + STEPS2:
        if 0 <= t - ts < 0.25:
            p = dict(p); e = math.exp(-(t - ts) / 0.06)
            p["eyescale"] = p.get("eyescale", 1.0) + 0.05 * e
    return p

pose_track = Track([
    (0, KNOCK, 0),
    (t_quiet - 0.3, UP, 0.5),                       # "Quiet. Look up." — freezes, eyes to the ceiling
    (STEPS1[2], UP_R, 1.4),                         # his eyes follow the steps
    (STOP, STILL, 0.8),
    (t_youve - 0.3, TO_YOU, 1.4),                   # to you, very quietly
    (t_im - 0.3, STILL, 1.0),                       # back up at the ceiling
    (STEPS2[1], UP_L, 2.5),
    (t_tonight - 0.3, TO_YOU, 1.2),
])
x_track = Track([(0, 0.0, 0)])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_quiet, (480, 760, 1.35), 1.6),                           # tilt up with him
    (STEPS1[0], (500, 600, 1.15), STOP - STEPS1[0]),            # the empty ceiling above him
    (STOP + 0.5, (470, 800, 1.55), 3.0),                        # slowly down onto his face
    (t_youve, (470, 860, 1.62), t_im - t_youve),                # slow push while he tells you
    (t_im, (480, 720, 1.3), 2.0),
    (t_tonight - 0.3, (468, 850, 1.85), t_end - t_tonight + 1.0),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_quiet, mood_vec("unease"), 0.4),
    (STOP, mood_vec("void"), 1.2),
    (t_youve, mood_vec("lonely"), 1.6),
    (t_im, mood_vec("unease"), 1.0),
    (t_tonight, mood_vec("uncanny"), 1.4),
])

NIGHT = dict(top=(14, 18, 44), bot=(36, 34, 74), clouds=0.0, cloud_v=0.0, stars=0.6, sun=0.0, sun_y=0.3, sun_r=24)
sky = Track([
    (0, SKY(**NIGHT, drone=0.25), 0),
    (t_quiet, SKY(**NIGHT, drone=0.0), 0.4),                    # dead quiet but for the steps
    (t_youve, SKY(**NIGHT, drone=0.12), 2.0),
    (t_im, SKY(**NIGHT, drone=0.0), 0.8),
    (t_tonight, SKY(**NIGHT, drone=0.1), 1.0),
])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

# when the steps stop over him, a little dust sifts down from the ceiling (he sees it)
rr = random.Random(35)
MOTES = [(rr.uniform(400, 520), rr.uniform(0, 1.8), rr.uniform(0.6, 1.3)) for _ in range(14)]
def dust(cr, t, pose, env):
    for x0, dly, sp in MOTES:
        u = t - STOP - 0.2 - dly
        if 0 < u < 6:
            y = 120 + u * 110 * sp
            x = x0 + 8 * math.sin(u * 1.7 + x0)
            a = min(1, u * 2) * (1 - smooth((u - 4) / 2)) * 0.6
            cr.arc(x, y, 1.6, 0, 2 * math.pi); cr.set_source_rgba(*N.INK, a); cr.fill()

def chair(cr, t, pose, env):
    N.draw_chair(cr, 600 + 260, scale=1.1, tag=True, tag_swing=0.0)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=34, sfx=sfx, pose_hook=jolt, draw_hook=dust, under_hook=chair)
N.BLINKS = [b for b in N.BLINKS if not (STEPS1[0] - 0.5 < b < t_youve)]    # he doesn't blink while it's overhead
N.main("nigel_bane_ep035_upstairs.mp4")
