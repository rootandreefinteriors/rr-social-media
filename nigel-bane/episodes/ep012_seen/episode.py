"""Day 12 — "Seen". The bird has landed on the ledge (payoff of D6 glimpse → D9 → D11).
Idea: being seen by something with no word for you — no opinion, no story, just the shape — and it stayed.
"I'm not going to name it. Names are how you stop looking." (↺ D6). Shot/reverse-shot Nigel ↔ bird; bird stays D12–15.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, CHEST, PRESENT, STAND, OPEN)

N.setup()
T, TE = N.T, N.TE

WLOOK = P(head=(468, 766), tilt=0.13, look=(0.85, -0.75), swing=0.0)
STILL = P(WLOOK, lelb=(412, 1100), lhand=(402, 1215), relb=(500, 1100), rhand=(512, 1215))
HUSH = P(WLOOK, relb=(560, 1050), rhand=(545, 960), finger=1.0)          # finger raised: don't move
POINT_WALL = P(WLOOK, lelb=(370, 1060), lhand=(300, 1020), look=(-0.6, -0.1), tilt=-0.05)
OPEN_SOFT = P(OPEN, look=(0.7, -0.6), tilt=0.1)
TO_YOU = P(PRESENT, look=(0.0, 0.0), tilt=0.0)
TILT_L = P(STILL, tilt=0.32)

t_dont, t_look, t_landed, t_its1 = T("don't"), T("look"), T("landed"), T("it's")
t_doesnt1, t_room, t_wall, t_day = T("doesn't"), T("room"), T("wall"), T("day")
t_has, t_and1, t_thats, t_no1 = T("has"), T("and"), T("that's"), T("no", 2)
t_just2, t_most, t_your, t_this = T("just", 2), T("most"), T("your"), T("this")
t_and2, t_stayed, t_im, t_names = T("and", 2), T("stayed"), T("i'm"), T("names")
t_its_still, t_im2, t_until = T("it's", 3), T("i'm", 2), T("until")

pose_track = Track([
    (0, KNOCK, 0),
    (t_dont - 0.2, HUSH, 0.4),
    (t_look - 0.1, STILL, 0.6),
    (t_doesnt1 - 0.1, P(STILL, tilt=0.06), 0.6),
    (t_room - 0.2, OPEN_SOFT, 0.6),
    (t_wall - 0.2, POINT_WALL, 0.5),
    (t_day - 0.2, P(OPEN_SOFT, look=(0.8, -0.85)), 0.5),
    (t_has - 0.1, STILL, 0.6),
    (t_thats - 0.1, CHEST, 0.6),
    (t_just2 - 0.1, OPEN_SOFT, 0.8),
    (t_most - 0.1, TO_YOU, 0.8),                 # to you: most people only see the word for you
    (t_this - 0.2, STILL, 0.8),
    (t_im - 0.1, TILT_L, 0.8),
    (t_names, STILL, 1.0),
    (t_im2 - 0.1, P(STILL, eyescale=1.05), 1.2),
])

x_track = Track([(0, 0.0, 0), (t_dont - 0.4, 150.0, 1.6)])   # a slow, careful step closer, then stays put

BIRD = (840, 515, 1.9)        # the ledge, close
TWO = (720, 640, 1.18)        # Nigel + window
NIGEL = (600, 820, 1.35)
cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_look - 0.2, BIRD, 1.6),
    (t_its1, TWO, 1.8),
    (t_doesnt1 + 0.5, NIGEL, 2.0),
    (t_has, BIRD, 1.8),
    (t_thats, TWO, 1.6),
    (t_most - 0.2, (560, 900, 1.25), 1.4),       # toward the viewer
    (t_this - 0.2, BIRD, 1.6),
    (t_im - 0.1, NIGEL, 1.6),
    (t_its_still - 0.2, (740, 650, 1.1), 3.0),   # slow pull to the two of them
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_look, mood_vec("awe"), 1.0),
    (t_doesnt1, mood_vec("drifting"), 1.4),
    (t_thats, mood_vec("warm"), 1.4),
    (t_most, mood_vec("melancholy"), 1.0),
    (t_this, mood_vec("warm"), 1.2),
    (t_im, mood_vec("awe"), 1.4),
])

MORNING = dict(top=(185, 212, 240), bot=(250, 240, 218), clouds=0.35, cloud_v=4.0, perch=1.0, perch_x=0.62)
def bird(tilt=0.0, hop=0.0, **kw):
    return SKY(**MORNING, perch_tilt=tilt, perch_hop=hop, **kw)
env_track = Track([
    (0, bird(drone=0.2), 0),
    (t_landed + 0.3, bird(tilt=0.25, drone=0.25), 0.4),       # it looks
    (t_room, bird(tilt=-0.15, drone=0.3), 0.4),
    (t_and1, bird(tilt=0.3, drone=0.35), 0.5),                # still looking
    (t_thats, bird(tilt=0.0, drone=0.45, shimmer=0.3), 0.8),
    (t_this, bird(tilt=0.2, drone=0.4), 0.5),
    (t_stayed - 0.1, bird(tilt=0.2, hop=1.0, drone=0.4), 0.15),   # a little hop: it stayed
    (t_stayed + 0.25, bird(tilt=0.05, hop=0.0, drone=0.4), 0.25),
    (t_names, bird(tilt=-0.2, drone=0.3), 0.6),
    (t_until, bird(tilt=0.15, drone=0.15), 0.6),
])

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=12, tally_new=[], extra_blinks=[t_stayed + 0.6])
N.main("nigel_bane_ep012_seen.mp4")
