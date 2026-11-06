"""Day 22 — "Silence". The sun is out after the snow; an icicle hangs outside the window, dripping. Right after the
open: "Wait. Listen to that." IDEA (you): when did you last hear nothing? Something is always playing. TENSION: he asks
for ten seconds of quiet and actually takes all ten — the icicle drips once a second, counting; the room's hum keeps
rising; under it, faintly, a heartbeat. "Did you hear it? Under the hum? It's always there. It was there before you
could talk." HOOK: "There's something under all your noise. You keep it playing so you don't have to meet it."
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, ONE, OPEN, SHRUG, CHEST, PRESENT)

N.setup()
T, TE = N.T, N.TE

LISTEN = P(look=(0.65, -0.8), tilt=0.22, relb=(560, 1050), rhand=(545, 960), finger=1.0, swing=0.0)
ICICLE = P(LISTEN, finger=0.0, relb=(500, 1100), rhand=(512, 1215), tilt=0.12, eyescale=1.05)
TO_YOU = P(look=(0.0, 0.02), tilt=0.0, swing=0.0)
NOT1 = P(ONE, look=(0.0, 0.0))
NOT2 = P(OPEN, look=(-0.2, 0.0))
NOT3 = P(SHRUG, look=(0.2, 0.0))
SOFT = P(CHEST, look=(0.0, 0.1), tilt=-0.04)
QUIET = P(TO_YOU, lelb=(412, 1100), lhand=(402, 1215), relb=(500, 1100), rhand=(512, 1215), shut=1.0, tilt=0.06)
OPENED = P(QUIET, shut=0.0, eyescale=1.12, tilt=0.0)
LAST = P(TO_YOU, eyescale=1.04)

t_there_end, t_wait, t_icicle, t_whens = TE("there"), T("wait"), T("icicle"), T("when's")
t_not1, t_not2, t_not3, t_most = T("not"), T("not", 2), T("not", 3), T("most")
t_lets, t_first_end, t_did, t_its2, t_theres = T("let's"), TE("first"), T("did"), T("it's", 2), T("there's")

QUIET_START = t_first_end + 0.35
pose_track = Track([
    (0, KNOCK, 0),
    (t_there_end + 0.1, LISTEN, 0.6),              # wait — listen
    (t_icicle - 0.2, ICICLE, 0.8),
    (t_whens - 0.3, TO_YOU, 0.9),
    (t_not1 - 0.1, NOT1, 0.4),
    (t_not2 - 0.1, NOT2, 0.4),
    (t_not3 - 0.1, NOT3, 0.4),
    (t_most - 0.2, SOFT, 0.7),
    (t_lets - 0.2, TO_YOU, 0.6),
    (QUIET_START, QUIET, 0.8),                     # eyes shut. ten seconds.
    (t_did - 0.5, OPENED, 0.35),
    (t_theres - 0.2, LAST, 1.0),
])

x_track = Track([(0, 0.0, 0), (t_there_end + 0.1, 130.0, 1.3), (t_whens - 0.3, 40.0, 1.4)])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_there_end + 0.1, (800, 420, 1.5), 2.0),     # the window, the icicle
    (t_icicle, (880, 330, 2.3), 2.5),              # close on the drip
    (t_whens - 0.3, (490, 860, 1.42), 2.0),        # to you
    (QUIET_START - 0.4, (490, 830, 1.5), 1.0),
    (QUIET_START + 0.6, (492, 790, 2.15), 10.0),   # one slow push through the whole silence
    (t_theres - 0.2, (490, 830, 1.6), 2.5),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_icicle, mood_vec("drifting"), 1.2),
    (t_whens, mood_vec("uncanny"), 1.0),
    (t_most, mood_vec("melancholy"), 1.0),
    (t_did, mood_vec("unease"), 0.6),
    (t_its2, mood_vec("uncanny"), 1.2),
])

SUN = dict(top=(140, 182, 232), bot=(232, 238, 246), clouds=0.3, cloud_v=2.0, sun=0.7, sun_y=0.3, sun_r=30, icicle=1.0)
sky_track = Track([
    (0, SKY(**SUN, drone=0.3), 0),
    (t_whens, SKY(**SUN, drone=0.3), 1.0),
    (QUIET_START, SKY(**SUN, drone=0.35), 0.5),
    (QUIET_START + 0.5, SKY(**SUN, drone=1.25), 9.5),   # the hum swells through the silence
    (t_did + 0.2, SKY(**SUN, drone=0.5), 2.0),
    (t_theres, SKY(**SUN, drone=0.75), 3.0),
])
pile = Track([(0, 0.95, 0), (0.01, 0.78, 60.0)])         # yesterday's snow, slowly melting
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

# the icicle: a drip every ~2 s... then exactly one a second through the ten seconds of quiet
drips = [d for d in [t_wait + 0.6 + 2.1 * k for k in range(40)] if d < QUIET_START - 0.6]
drips += [QUIET_START + 0.2 + k for k in range(10)]
drips += [t_did + 1.4 + 2.2 * k for k in range(8)]
beats = [(QUIET_START + 2.5 + 1.02 * k, 0.12 + 0.05 * k) for k in range(8)]      # a heartbeat fades up under it
beats += [(t_did + 0.2 + 1.02 * k, max(0.0, 0.5 - 0.06 * k)) for k in range(9)]
N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=22, tally_new=[], web=WEB, draw_hook=bundle, drips=drips,
            sfx=[(b, "heart", g) for b, g in beats if g > 0.01])
N.main("nigel_bane_ep022_silence.mp4")
