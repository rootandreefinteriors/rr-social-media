"""Day 9 — "Leaving". Sleep: every night you leave and trust the one who wakes up will be you.
Prop: the bird crosses the window mid-thought (D6 glimpse -> D9 crossing -> D12 lands).
Hook: "I'll let you know who comes back."
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, THINK, ONE, OPEN, SHRUG, CHEST, PRESENT, STAND)

N.setup()
T, TE = N.T, N.TE

SNAP = P(head=(470, 766), tilt=0.18, look=(0.95, -0.85), eyescale=1.08, swing=0.0)
FLAP_UP = P(lelb=(360, 1040), lhand=(290, 990), relb=(540, 1040), rhand=(610, 990), look=(0.0, 0.0), eyescale=1.06, swing=0.0)
FLAP_DN = P(lelb=(370, 1090), lhand=(300, 1120), relb=(530, 1090), rhand=(600, 1120), look=(0.0, 0.0), eyescale=1.06, swing=0.0)
SOFT = P(PRESENT, tilt=0.06, look=(0.0, 0.1))
CLOSED = P(look=(0.0, 0.35), tilt=-0.12, swing=0.0)
LIE = P(head=(300, 1306), neck=(466, 1442), hip=(735, 1452),
        lelb=(560, 1456), lhand=(650, 1462), relb=(585, 1440), rhand=(680, 1432),
        lknee=(850, 1455), lfoot=(962, 1470), rknee=(845, 1446), rfoot=(958, 1462),
        tilt=-math.pi / 2, look=(1.0, 0.0), swing=0.0)

t_so, t_sleep, t_every, t_leave = T("so"), T("sleep"), T("every"), T("leave")
t_lie, t_and1, t_and2, t_nobody = T("lie"), T("and"), T("and", 2), T("nobody")
t_like, t_isnt, t_to, t_and3 = T("like"), T("isn't"), T("to"), T("and", 3)
t_oh, t_did, t_something, t_a = T("oh"), T("did"), T("something"), T("a")
t_with, t_anyway, t_maybe, t_you_s2 = T("with"), T("anyway"), T("maybe"), T("you", 11)
t_im, t_ill = T("i'm"), T("i'll")

BIRD_T = t_oh - 1.25

pose_track = Track([
    (0, KNOCK, 0),
    (t_so - 0.1, THINK, 0.7),
    (t_every - 0.1, STAND, 0.8),
    (t_lie - 0.1, CLOSED, 0.8),
    (t_and2 - 0.1, P(look=(0.4, -0.3), tilt=0.08), 1.0),
    (t_and2 + 1.0, CHEST, 0.7),
    (t_nobody - 0.1, ONE, 0.5),
    (t_like - 0.2, SHRUG, 0.6),
    (t_isnt - 0.1, OPEN, 0.7),
    (t_and3 - 0.1, PRESENT, 0.7),
    (BIRD_T + 0.35, SNAP, 0.18),            # head snaps to the window
    (t_did - 0.15, P(look=(0.0, 0.0), eyescale=1.1), 0.4),   # to us: did you see that?
    (t_with - 0.1, FLAP_UP, 0.25),
    (t_with + 0.3, FLAP_DN, 0.25),
    (t_with + 0.6, FLAP_UP, 0.25),
    (t_with + 0.9, FLAP_DN, 0.25),
    (t_anyway - 0.1, STAND, 0.8),
    (t_maybe - 0.1, SOFT, 0.8),
    (t_you_s2 - 0.1, CHEST, 0.6),
    (t_im - 0.2, LIE, 1.3),
    (t_ill, P(LIE, look=(1.0, 0.3)), 1.0),
])

x_track = Track([
    (0, 0.0, 0),
    (t_every - 0.2, 120.0, 2.6),
    (t_nobody - 0.2, -60.0, 2.4),
    (t_isnt, 80.0, 2.2),
    (BIRD_T + 0.2, 150.0, 0.8),             # a step toward the window
    (t_anyway, 40.0, 1.6),
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_so - 0.2, (540, 960, 1.0), 2.4),
    (t_and2, (540, 1000, 0.85), 3.0),        # "somewhere you can't remember": the room drifts away
    (t_nobody, (540, 960, 1.0), 2.0),
    (BIRD_T + 0.2, (720, 640, 1.18), 0.9),   # the window, quick
    (t_did, (600, 840, 1.08), 1.0),
    (t_anyway, (540, 960, 1.0), 1.6),
    (t_im - 0.2, (560, 1290, 1.22), 2.2),
])
follow_track = Track([(0, 0.0, 0), (t_so, 0.2, 1.5), (BIRD_T, 0.0, 0.5), (t_anyway, 0.2, 1.0), (t_im, 0.0, 1.0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_sleep, mood_vec("drifting"), 1.2),
    (t_and2, mood_vec("melancholy"), 1.6),
    (t_nobody, mood_vec("drifting"), 1.2),
    (t_isnt, mood_vec("lonely"), 1.4),
    (BIRD_T + 0.3, mood_vec("awe"), 0.3),
    (t_did, mood_vec("curious"), 0.5),
    (t_anyway, mood_vec("drifting"), 1.0),
    (t_maybe, mood_vec("warm"), 1.4),
    (t_im, mood_vec("drifting"), 1.6),
])

EVENING = dict(top=(240, 170, 140), bot=(250, 215, 180), clouds=0.4, cloud_v=5.0)
TWILIGHT = dict(top=(70, 80, 140), bot=(225, 160, 140), clouds=0.15, cloud_v=2.0)
env_track = Track([
    (0, SKY(**EVENING), 0),
    (t_and2, SKY(top=(160, 110, 150), bot=(240, 180, 150), clouds=0.3, cloud_v=3, echo=0.5, drone=0.5), 2.5),
    (t_nobody, SKY(top=(150, 115, 160), bot=(240, 185, 160), clouds=0.3, cloud_v=3, echo=0.0, drone=0.4), 1.5),
    (t_to - 0.2, SKY(**TWILIGHT, drone=0.55), 2.0),                        # "hand yourself to the dark"
    (BIRD_T - 0.3, SKY(**TWILIGHT, drone=0.15), 0.3),                       # hush for the bird
    (t_anyway, SKY(**TWILIGHT, drone=0.4), 1.0),
    (t_maybe, SKY(top=(60, 70, 130), bot=(200, 150, 150), clouds=0.1, cloud_v=1, stars=0.25, drone=0.55), 2.0),
    (t_im, SKY(top=(16, 18, 42), bot=(44, 40, 80), clouds=0.0, cloud_v=0, stars=0.6, drone=0.7), 2.5),
])

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=9, tally_new=[],
            birds=[dict(t=BIRD_T - 0.3, dur=2.1, x0=1.1, x1=-0.15, y=0.5, size=30)])
N.main("nigel_bane_ep009_leaving.mp4")
