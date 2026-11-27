"""Day 53 — "overlooking" (posts as `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII III overlooking`).
Seeing arc 1/3 (theme: what you can't see, or stop seeing; prop: the window). Owner-approved script, 2026-11-27.
THE LINE: "There's probably someone in your life like that... You stopped really seeing them a long time ago."
C: "Watch the cloud with me. That one. In the middle." (he points up at the window)
T (love, like the mouse): one cloud, shaped like a sleeping dog, has stayed in the middle of his window all day while
the others go past; he's fond of it and keeps checking it's still there. Will it stay? He looks at us "just for a
second" (the camera comes in close on his face; the window is out of frame) and when the camera drifts back up to the
window it's gone. Bridge: the one thing that never moves becomes part of the window and you stop seeing it -> the person
who is always there. Ending (question): "When did you last really look at them?" One continuous shot.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, STAND, POINT_UP, smooth)

N.setup()
T, TE = N.T, N.TE

t_watch, t_that1, t_middle, t_dog, t_others, t_stayed = T("watch"), T("that"), TE("middle"), TE("dog"), T("others"), T("stayed")
t_keep, t_still1, t_like1, t_everything, t_stopped1, t_theres = T("keep"), T("still"), T("like", 2), T("everything"), T("stopped"), T("there's")
t_same1, t_you_stopped, t_youd, t_still2, t_im, t_just2, t_second = T("same"), T("you"), T("you'd"), T("still", 2), T("i'm"), T("just", 2), TE("second")
t_gone, t_when, t_end = T("gone"), T("when"), TE("them", 2)

GONE0, GONE1 = t_just2 + 0.6, t_second + 0.9          # the cloud goes while the window is out of frame
cloud_a = Track([(0, 1.0, 0), (GONE0, 0.0, GONE1 - GONE0)])

def dog_cloud(c, t, env, ww, wh):
    """one cloud that doesn't move: a sleeping dog, curled, in the middle of the window"""
    a = cloud_a.at(t)
    if a <= 0.005:
        return
    br = 1 + 0.015 * math.sin(t * 1.3)                  # it breathes, very slightly
    cx, cy = ww * 0.46, wh * 0.60
    body = [(-40, 0, 40), (0, -9, 46), (40, 0, 40), (-12, 18, 37), (26, 20, 35)]
    head = [(84, 16, 26), (108, 24, 14)]                                         # head down on its paws, snout
    paws = [(102, 42, 10), (82, 44, 10)]
    tail = [(-84, -4, 15), (-97, -19, 11), (-88, -33, 9)]                      # tail curled up behind
    lumps = body + head + paws + tail
    c.save(); c.translate(cx, cy); c.scale(1.18, 1.18 * br)
    c.set_source_rgba(0.72, 0.78, 0.88, 0.6 * a)        # a soft grey underside
    for dx, dy, r in lumps:
        c.arc(dx + 2, dy + 7, r, 0, 2 * math.pi); c.fill()
    c.set_source_rgba(1, 1, 1, 0.97 * a)
    for dx, dy, r in lumps:
        c.arc(dx, dy, r, 0, 2 * math.pi); c.fill()
    c.save(); c.translate(74, 6); c.rotate(0.9); c.scale(1.0, 0.55)            # one floppy ear
    c.set_source_rgba(0.82, 0.86, 0.93, 0.9 * a); c.arc(0, 0, 15, 0, 2 * math.pi); c.fill()
    c.restore()
    c.restore()

# ------------------------------------------------------------------ poses
WLOOK = P(STAND, look=(0.85, -0.8), tilt=0.12, eyescale=1.06, swing=0.0)
POINT = P(POINT_UP, eyescale=1.08)
FOND = P(WLOOK, tilt=0.2, eyescale=1.02, lelb=(400, 1090), lhand=(410, 1040))       # head on one side, fond of it
TO_US = P(STAND, look=(0.0, 0.0), swing=0.0)
SOFT = P(STAND, look=(0.05, 0.08), tilt=-0.04, swing=0.0)
TO_US_CLOSE = P(STAND, look=(0.0, 0.0), eyescale=1.08, tilt=0.02, swing=0.0)
UNEASE = P(WLOOK, eyescale=1.2, tilt=0.06)

pose_track = Track([
    (0, KNOCK, 0),
    (t_watch - 0.3, WLOOK, 0.7),                  # "Watch the cloud with me."
    (t_that1 - 0.2, POINT, 0.6),                  # "That one. In the middle."
    (t_dog + 0.3, WLOOK, 0.8),
    (t_keep - 0.2, TO_US, 0.6),                   # "I keep checking."
    (t_still1 - 0.4, WLOOK, 0.5),                 # "Still there."
    (t_like1 - 0.2, FOND, 1.2),                   # "I like that it stays."
    (t_stopped1 - 0.2, TO_US, 1.0),               # "I stopped really looking at it about lunchtime."
    (t_theres, SOFT, 1.2),
    (t_you_stopped - 0.2, TO_US, 1.0),
    (t_still2 - 0.4, WLOOK, 0.6),                 # "...Still there."
    (t_im - 0.2, TO_US_CLOSE, 0.7),               # "I'm going to look at you. Just for a second."
    (GONE1 + 0.1, UNEASE, 0.6),                   # looks back up: "It's gone."
    (t_when - 0.3, TO_US, 0.9),                   # "When did you last really look at them?"
])
x_track = Track([(0, 0.0, 0)])

WIN_SHOT = (620, 720, 1.05)
cam_track = Track([                                          # ONE continuous shot
    (0, (470, 880, 1.6), 0),
    (t_watch - 0.1, WIN_SHOT, 2.4),                          # up to the window: him, and the cloud
    (t_that1 + 0.3, (815, 440, 1.85), 3.0),                  # in on the window: the cloud like a sleeping dog
    (t_others + 0.4, (790, 470, 1.7), 3.5),                  # the others drift past it
    (t_keep - 0.3, (640, 690, 1.15), 2.4),                   # back out to him checking
    (t_like1 - 0.4, (610, 730, 1.08), 3.0),
    (t_stopped1 - 0.4, (480, 860, 1.4), 3.5),                # down to him (the window still at the top right)
    (t_you_stopped, (470, 850, 1.5), 4.0),
    (t_still2 - 0.6, WIN_SHOT, 2.4),                         # back up: "...Still there."
    (t_im - 0.2, (450, 800, 2.05), 2.0),                     # in on his face; the window is out of frame
    (GONE1 + 0.05, WIN_SHOT, 1.6),                           # back up to the window: it's gone
    (t_when - 0.2, (520, 820, 1.35), 2.4),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_watch, mood_vec("awe"), 1.0),
    (t_stayed, mood_vec("warm"), 1.5),
    (t_stopped1, mood_vec("drifting"), 1.5),
    (t_theres, mood_vec("melancholy"), 1.5),
    (t_youd, mood_vec("lonely"), 1.5),
    (t_still2, mood_vec("warm"), 0.8),
    (GONE1, mood_vec("unease"), 0.6),
    (t_when, mood_vec("uncanny"), 1.0),
])

DAY = dict(top=(150, 186, 232), bot=(214, 228, 242), clouds=0.5, cloud_v=11.0, sun=0.0, sun_y=0.3, sun_r=26)
sky = Track([(0, SKY(**DAY, drone=0.14), 0), (t_watch, SKY(**DAY, drone=0.06), 1.5),
             (t_im, SKY(**DAY, drone=0.0), 1.0), (GONE1, SKY(**DAY, drone=0.18), 1.5)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track, tally_base=53, window_hook=dog_cloud)
N.BLINKS = [b for b in N.BLINKS if not (GONE1 - 0.2 < b < t_gone + 0.6)]
N.main("nigel_bane_ep053_overlooking.mp4")
