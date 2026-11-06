"""Day 21 — "Blinking". Snow has been falling all night; he's at the window and refuses to blink, trying to see a single
flake land. IDEA (you): you blink ~15,000 times a day — over an hour of darkness — and your brain cuts it out and
stitches the day back together so it looks smooth. TENSION: the stare, held almost the whole episode (no automatic
blinks; the camera creeps into an extreme close-up of his straining eyes). PAYOFF: one heavy blink — and the snow on the
ledge has piled higher. "See? More." HOOK: "Your brain's been cutting the dark out of your life since you were born. You
never asked what else it cuts."
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, ONE, OPEN, STAND)

N.setup()
T, TE = N.T, N.TE

UP = dict(look=(0.62, -0.88), tilt=0.1, swing=0.0)
STARE = P(**UP, lelb=(412, 1100), lhand=(402, 1215), relb=(500, 1100), rhand=(512, 1215), eyescale=1.1)
HUSH = P(**UP, relb=(560, 1050), rhand=(545, 960), finger=1.0, eyescale=1.1)
STARE_CAM = P(STARE, look=(0.0, 0.0), tilt=0.02, eyescale=1.14)
STRAIN = P(STARE_CAM, eyescale=1.2, tilt=-0.03)
BLINK = P(STRAIN, shut=1.0, eyescale=1.0, tilt=-0.06)
AFTER = P(STARE, eyescale=1.0, look=(0.62, -0.75))
LAST = P(look=(0.0, 0.0), tilt=0.0, swing=0.0, eyescale=1.02)

t_there_end, t_shh, t_snowing = TE("there"), T("shh"), T("snowing")
t_you1, t_dark1, t_hour, t_noticed = T("you"), T("dark"), T("hour"), T("noticed")
t_brain, t_smooth_end, t_burning, t_cant_end = T("brain"), TE("smooth"), T("burning"), TE("can't")
t_see, t_more3, t_brains, t_born_end = T("see"), T("more", 3), T("brain's"), TE("born")

BLINK_T = t_cant_end + 0.35           # the one blink of the whole episode
pose_track = Track([
    (0, KNOCK, 0),
    (t_there_end + 0.1, HUSH, 0.6),
    (t_snowing - 0.3, STARE, 0.8),                # staring up at the ledge
    (t_you1 - 0.3, STARE_CAM, 1.0),               # eyes on you, still not blinking
    (t_burning - 0.3, STRAIN, 1.2),
    (BLINK_T, BLINK, 0.12),                       # ...gone
    (BLINK_T + 0.45, P(STRAIN, eyescale=1.0), 0.18),
    (t_see - 0.3, AFTER, 0.6),                    # back to the ledge
    (t_brains - 0.3, LAST, 0.9),
])
def tremble(t, p):    # the strain shows: eyes trembling more and more as the stare goes on
    s = N.smooth((t - t_noticed) / (BLINK_T - t_noticed)) if t < BLINK_T else 0.0
    if s > 0:
        p["eyescale"] += 0.025 * s * math.sin(t * 43) + 0.012 * s * math.sin(t * 71)
        p["tilt"] += 0.01 * s * math.sin(t * 29)
    return p

x_track = Track([(0, 0.0, 0), (t_there_end + 0.1, 120.0, 1.4), (t_brains - 0.3, 60.0, 1.4)])

EYES = (572, 768)
cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_there_end + 0.1, (640, 640, 1.12), 2.0),          # him under the window; the snow
    (t_you1 - 0.3, (575, 800, 1.5), 2.2),                # to you
    (t_you1 + 2.0, (575, 772, 2.6), t_burning - t_you1 - 2.0),   # one long creep into the stare
    (t_burning, (EYES[0], EYES[1], 3.3), 2.4),           # both eyes fill the frame
    (BLINK_T + 0.5, (820, 455, 1.85), 0.9),              # after the blink: the ledge, close
    (t_see + 1.6, (660, 620, 1.15), 1.6),
    (t_brains - 0.3, (520, 840, 1.55), 2.0),             # to you
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_snowing, mood_vec("drifting"), 1.2),
    (t_you1, mood_vec("curious"), 1.0),
    (t_dark1, mood_vec("uncanny"), 1.2),
    (t_brain, mood_vec("drifting"), 1.2),
    (t_burning, mood_vec("unease"), 1.4),
    (t_see, mood_vec("melancholy"), 1.0),
    (t_brains, mood_vec("uncanny"), 1.2),
])

WINTER = dict(top=(140, 150, 172), bot=(190, 196, 210), clouds=0.6, cloud_v=2.0, snow=0.95)
sky_track = Track([
    (0, SKY(**WINTER, drone=0.25), 0),
    (t_you1, SKY(**WINTER, drone=0.35), 2.0),
    (t_burning, SKY(**WINTER, drone=0.65, shimmer=0.3), 2.0),
    (BLINK_T + 0.3, SKY(**WINTER, drone=0.3), 0.6),
    (t_brains, SKY(**WINTER, drone=0.5), 2.0),
])
pile = Track([(0, 0.3, 0), (0.01, 0.52, BLINK_T - 0.3),        # creeps up so slowly you never see it move...
              (BLINK_T + 0.05, 0.98, 0.25)])                  # ...and jumps while his eyes are shut
class Env:
    def at(self, t):
        d = dict(sky_track.at(t))
        d.update(snow_pile=pile.at(t), web=1.0, spider=1.0, prey=1.0, prey_wrap=1.0)
        return d
env_track = Env()

WEB = dict(hub=(655, 328), frame=[(570, 235), (742, 214), (748, 420), (585, 440)],
           anchors=[(500, 168), (800, 205), (840, 354), (470, 520)], fade=[0, 3],
           dragline=((632, 438), (650, 1478)), spokes=11, turns=8, spider_size=1.25,
           prey=dict(pos=(712, 262), kind="fly", size=1.9))
MOTH = dict(prey=1.0, prey_struggle=0.0, prey_wrap=1.0)
def bundle(cr, t, p, env):
    N.draw_prey(cr, t, MOTH, (622, 392), "moth", 2.1)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=21, tally_new=[], web=WEB, draw_hook=bundle, pose_hook=tremble)
N.BLINKS = []          # he doesn't blink. at all. (the one blink is the pose's "shut")
N.main("nigel_bane_ep021_blinking.mp4")
