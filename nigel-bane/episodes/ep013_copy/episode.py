"""Day 13 — "Copy". The bird copies his head tilts → idea: everything we do is copied; what's left without the copies?
"There wasn't much there." → signature visual: his body erases from the feet up (reveal), then redraws.
Ends: "I'm not sure anymore which of us tilted first." — the bird tilts BEFORE him.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, ONE, OPEN, CHEST, PRESENT, STAND)

N.setup()
T, TE = N.T, N.TE

WLOOK = P(head=(468, 766), tilt=0.13, look=(0.85, -0.75), swing=0.0)
TILTED = P(WLOOK, tilt=0.42)
HIPS = P(lelb=(360, 1150), lhand=(410, 1225), relb=(545, 1150), rhand=(495, 1225), tilt=-0.05, look=(0.1, 0.0), swing=0.0)
WAVE = P(relb=(560, 1000), rhand=(600, 880), look=(0.0, 0.0), tilt=0.05, swing=0.0)
POINT_CAM = P(relb=(560, 1062), rhand=(612, 992), finger=1.0, look=(0.0, 0.0), swing=0.0)
RIGID = P(lelb=(420, 1105), lhand=(418, 1222), relb=(484, 1105), rhand=(486, 1222), look=(0.0, 0.0), tilt=0.0, swing=0.0)

t_watch, t_tilt, t_its_tilts, t_copied = T("watch"), T("tilt"), T("tilts"), T("copied")
t_every, t_stand, t_hello, t_somebody = T("everything"), T("stand"), T("hello"), T("somebody")
t_you, t_walk, t_so, t_tried = T("you"), T("walk"), T("so"), T("tried")
t_standing, t_there2, t_and_end, t_tilted = T("standing"), T("there", 3), T("and", 3), T("tilted")

pose_track = Track([
    (0, KNOCK, 0),
    (t_watch - 0.2, WLOOK, 0.7),
    (t_tilt, TILTED, 0.6),                       # he tilts...
    (t_copied - 0.3, WLOOK, 0.6),
    (t_every - 0.1, ONE, 0.5),
    (t_stand - 0.3, HIPS, 0.5),                  # "the way I stand"
    (t_hello - 0.3, WAVE, 0.4),                  # "the way I say hello"
    (t_somebody, PRESENT, 0.6),
    (t_you - 0.1, POINT_CAM, 0.5),
    (t_walk - 0.2, STAND, 0.6),
    (t_so - 0.1, OPEN, 0.6),
    (t_tried - 0.1, RIGID, 1.2),                 # standing still. copying nothing.
    (t_and_end - 0.2, WLOOK, 0.8),
    (t_tilted + 0.5, TILTED, 0.5),               # ...he tilts AFTER the bird
])

reveal = Track([(0, 1.0, 0), (t_there2 - 0.6, 0.6, 2.2), (t_and_end - 0.3, 1.0, 1.4)])   # not much there
def hook(t, p):
    p["reveal"] = reveal.at(t)
    return p

x_track = Track([
    (0, 0.0, 0),
    (t_watch - 0.3, 150.0, 1.6),
    (t_every, 0.0, 2.0),
    (t_walk - 0.3, -170.0, 2.6),                 # "a walk you saw once": he walks; copies trail him
    (t_so, 0.0, 1.6),
    (t_and_end - 0.4, 150.0, 1.5),
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_watch - 0.2, (720, 640, 1.18), 2.0),
    (t_every, (540, 960, 1.0), 2.0),
    (t_tried, (450, 900, 1.2), 5.0),             # slow push while he stands still
    (t_there2 - 0.6, (450, 980, 1.05), 2.0),
    (t_and_end - 0.4, (720, 640, 1.18), 1.8),
])
follow_track = Track([(0, 0.0, 0), (t_every, 0.2, 1.0), (t_tried, 0.0, 1.0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_tilt, mood_vec("uncanny"), 1.0),
    (t_copied, mood_vec("drifting"), 1.2),
    (t_you, mood_vec("curious"), 1.0),
    (t_so, mood_vec("drifting"), 1.0),
    (t_tried, mood_vec("lonely"), 1.6),
    (t_there2 - 0.4, mood_vec("void"), 1.6),
    (t_and_end - 0.2, mood_vec("unease"), 1.0),
])

DAY = dict(top=(190, 210, 236), bot=(246, 240, 226), clouds=0.4, cloud_v=4.0, perch=1.0, perch_x=0.62)
def sky(tilt=0.0, **kw):
    d = dict(DAY); d.update(kw)
    return SKY(perch_tilt=tilt, **d)
env_track = Track([
    (0, sky(drone=0.3), 0),
    (t_its_tilts - 0.1, sky(tilt=0.42, drone=0.35), 0.5),        # it tilts its head (after him)
    (t_copied, sky(tilt=0.0, drone=0.4), 0.8),
    (t_every, sky(echo=0.9, drone=0.45), 1.0),                   # copies everywhere
    (t_so, sky(echo=0.0, drone=0.35), 0.4),
    (t_tried, sky(top=(170, 180, 205), bot=(225, 225, 232), drone=0.2), 2.0),
    (t_there2 - 0.4, sky(top=(150, 155, 180), bot=(210, 210, 222), drone=0.0), 1.5),   # silence
    (t_and_end - 0.3, sky(drone=0.3), 1.5),
    (t_tilted - 0.25, sky(tilt=0.42, drone=0.3), 0.4),             # the bird tilts FIRST
])

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=13, tally_new=[], pose_hook=hook)
N.main("nigel_bane_ep013_copy.mp4")
