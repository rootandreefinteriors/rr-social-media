"""Day 24 — "Reflection". Night: the window is black enough to be a mirror. He's trying to catch his reflection looking
somewhere else — just once. IDEA (you): you've never seen your own face. Mirrors flip you, photos catch you trying; the
only face you know is the one that knows it's being watched. Somebody on a bus once saw you thinking. Everyone else
gets the other face — "the one you're making right now, watching this." TENSION: escalating tricks to catch it off
guard (a sudden tilt, a raised hand, finally eyes shut... and snapped open) — it's always already looking back.
"...Too slow." HOOK: "Everyone you've ever met has seen a face you never will. Yours, when you're not watching it."
The reflection is driven from his own pose (tilt, arm, eyes, eye colour) so it can never fall out of step.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, CHEST, PRESENT, ONE)

N.setup()
T, TE = N.T, N.TE

UP = dict(look=(0.55, -0.92), swing=0.0)
WATCH = P(**UP, tilt=0.1, lelb=(412, 1100), lhand=(402, 1215), relb=(500, 1100), rhand=(512, 1215))
SNAP = P(WATCH, tilt=0.42)                                     # a sudden tilt
WAVE = P(WATCH, relb=(560, 1010), rhand=(600, 890), tilt=0.08)  # a slow raised hand
TO_YOU = P(look=(0.0, 0.0), tilt=0.0, swing=0.0)
SOFT = P(CHEST, look=(0.0, 0.08))
BUS = P(PRESENT, look=(-0.3, 0.05), tilt=-0.05)
YOU_NOW = P(ONE, look=(0.0, 0.0), relb=(540, 1050), rhand=(560, 940), eyescale=1.08)
SHUT = P(WATCH, shut=1.0, tilt=0.06)
OPEN_SNAP = P(WATCH, shut=0.0, eyescale=1.15, tilt=0.12)
LAST = P(TO_YOU, eyescale=1.04)

t_there_end, t_dark, t_trying, t_once = TE("there"), T("dark"), T("trying"), T("once")
t_looking, t_never1, t_youve, t_mirrors, t_only = T("looking"), T("never"), T("you've"), T("mirrors"), T("only")
t_somebody, t_everyone1, t_making, t_this_end = T("somebody"), T("everyone"), T("making"), TE("this")
t_hold, t_on_end, t_too, t_everyone2 = T("hold"), TE("on", 2), T("too"), T("everyone", 2)

SHUT_T = TE("on", 2) + 0.15
OPEN_T = T("too") - 0.35
pose_track = Track([
    (0, KNOCK, 0),
    (t_there_end + 0.1, WATCH, 0.8),                # under the window, looking up at himself
    (t_trying - 0.1, WAVE, 1.6),                    # a slow hand... it raises one too
    (t_once - 0.05, SNAP, 0.12),                    # snap!
    (t_once + 0.45, WATCH, 0.6),
    (t_youve - 0.3, TO_YOU, 0.9),
    (t_mirrors - 0.1, SOFT, 0.6),
    (t_somebody - 0.2, BUS, 0.7),
    (t_everyone1 - 0.2, TO_YOU, 0.6),
    (t_making - 0.2, YOU_NOW, 0.6),                 # the one you're making right now
    (t_hold - 0.3, WATCH, 0.7),
    (SHUT_T, SHUT, 0.25),
    (OPEN_T, OPEN_SNAP, 0.08),                      # open — it's already looking
    (t_everyone2 - 0.3, LAST, 1.0),
])

x_track = Track([(0, 0.0, 0), (t_there_end + 0.1, 170.0, 1.4), (t_youve - 0.3, 60.0, 1.4),
                 (t_hold - 0.3, 170.0, 1.2), (t_everyone2 - 0.3, 60.0, 1.4)])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_there_end + 0.1, (700, 590, 1.15), 2.0),      # him and his reflection
    (t_looking - 0.2, (840, 380, 2.3), 2.4),         # the reflection, close: it never looks away
    (t_youve - 0.2, (520, 830, 1.55), 2.0),          # to you
    (t_mirrors, (520, 800, 2.1), t_this_end - t_mirrors),   # one slow push to "watching this"
    (t_hold - 0.3, (720, 560, 1.25), 1.6),           # the last trick
    (t_everyone2 - 0.3, (520, 840, 1.6), 2.0),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_dark, mood_vec("drifting"), 1.2),
    (t_looking, mood_vec("uncanny"), 1.2),
    (t_youve, mood_vec("melancholy"), 1.2),
    (t_everyone1, mood_vec("unease"), 1.2),
    (t_hold, mood_vec("uncanny"), 0.8),
    (t_everyone2, mood_vec("lonely"), 1.4),
])

NIGHT = dict(top=(14, 16, 36), bot=(30, 30, 60), clouds=0.0, cloud_v=0.0, stars=0.3, silver=0.12, mirror=1.0,
             snow_pile=0.4)
sky_track = Track([
    (0, SKY(**NIGHT, drone=0.3), 0),
    (t_looking, SKY(**NIGHT, drone=0.45), 1.5),
    (t_making, SKY(**NIGHT, drone=0.6), 2.0),
    (t_this_end + 0.1, SKY(**NIGHT, drone=0.15), 0.6),
    (SHUT_T, SKY(**NIGHT, drone=0.0), 0.4),           # silence while his eyes are shut
    (OPEN_T, SKY(**NIGHT, drone=0.55), 0.2),
    (t_everyone2, SKY(**NIGHT, drone=0.45), 2.0),
])
class Env:
    def at(self, t):
        d = dict(sky_track.at(t))
        p = pose_track.at(t)
        m = mood_track.at(t)
        arm = max(0.0, min(1.0, (1090 - p["rhand"][1]) / 200.0))
        shut = max(p["shut"], 1.0 if N.blink_amt(t) > 0.5 else 0.0)   # it blinks when he blinks
        d.update(mirror_tilt=-p["tilt"], mirror_shut=shut, mirror_arm=arm, mirror_eyes=m["p1"],
                 web=1.0, spider=1.0, prey=1.0, prey_wrap=1.0)
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
            tally_base=24, tally_new=[], web=WEB, draw_hook=bundle)
N.BLINKS = [b for b in N.BLINKS if abs(b - OPEN_T) > 1.5 and abs(b - t_once) > 1.0]
N.main("nigel_bane_ep024_reflection.mp4")
