"""Day 7 — "Waiting". Waiting for the thing at the window edge. Time gets thick; waiting is hope with nothing to do.
First ritual line: "Still here." (hand on the tally). Hook: the window looks smaller (it is: win_scale 0.86).
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, THINK, ONE, OPEN, SHRUG, CHEST, PRESENT, STAND)

N.setup()
T, TE = N.T, N.TE

EDGE = P(head=(470, 768), tilt=0.16, look=(0.95, -0.9), swing=0.0)
WLOOK = P(head=(468, 766), tilt=0.13, look=(0.85, -0.75))
PHONE = P(relb=(540, 1070), rhand=(520, 990), look=(0.35, 0.45), tilt=0.12, swing=0.0)   # staring at his hand
LEAN = P(head=(440, 772), tilt=-0.1, lelb=(410, 1110), lhand=(475, 1135), relb=(500, 1110), rhand=(430, 1140),
         look=(0.2, 0.25), swing=0.0)
TOUCH7 = P(lelb=(360, 1080), lhand=(324, 1018), look=(0.0, 0.0), tilt=0.0, swing=0.0)   # hand on mark 7
SIDEEYE = P(TOUCH7, look=(0.85, -0.7), tilt=0.1)

t_ive, t_waiting1, t_it, t_waiting2 = T("i've"), T("waiting"), T("it"), T("waiting", 2)
t_time, t_one, t_whole, t_ithink = T("time"), T("one"), T("whole"), T("think")
t_w_grow, t_w_week, t_w_text, t_w_feel = T("waiting", 4), T("waiting", 5), T("waiting", 6), T("waiting", 7)
t_and2, t_like2, t_but, t_so = T("and", 2), T("like", 2), T("but"), T("so")
t_idont, t_its, t_seven, t_still = T("mind"), T("it's"), T("seven"), T("still")
t_the_win, t_or, t_one_of = T("window", 2), T("or"), T("one", 2)

pose_track = Track([
    (0, KNOCK, 0),
    (t_ive - 0.2, EDGE, 0.8),
    (t_it - 0.1, P(EDGE, look=(0.6, -0.5)), 0.6),
    (t_waiting2 - 0.1, THINK, 0.7),
    (t_one - 0.1, ONE, 0.5),
    (t_whole - 0.1, SHRUG, 0.6),
    (t_ithink - 0.2, PRESENT, 0.6),
    (t_w_grow - 0.1, ONE, 0.4),
    (t_w_week - 0.1, OPEN, 0.4),
    (t_w_text - 0.1, PHONE, 0.4),
    (t_w_feel - 0.1, CHEST, 0.4),
    (t_and2 - 0.1, STAND, 0.6),
    (t_but - 0.1, WLOOK, 0.8),
    (t_so - 0.1, P(SHRUG, tilt=0.05, look=(0.0, 0.1)), 0.7),
    (t_idont - 0.4, LEAN, 0.9),
    (t_seven - 0.35, STAND, 0.3),
    (t_still - 0.4, TOUCH7, 0.5),
    (t_the_win - 0.3, SIDEEYE, 0.6),
    (t_one_of - 0.2, P(TOUCH7, look=(0.05, 0.05), eyescale=1.05), 0.8),
])

x_track = Track([
    (0, 0.0, 0),
    (t_ive - 0.2, 160.0, 1.6),
    (t_waiting2, 30.0, 2.6),                # slow, thick time
    (t_w_grow - 0.1, -60.0, 0.9),
    (t_w_week - 0.1, 40.0, 0.9),
    (t_w_text - 0.1, -30.0, 0.9),
    (t_w_feel - 0.1, 60.0, 0.9),
    (t_and2, -40.0, 2.4),                   # walking the "hallway"
    (t_but, 120.0, 1.8),
    (t_idont - 0.6, -120.0, 1.6),           # to the wall
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_ive - 0.3, (720, 700, 1.15), 2.0),
    (t_waiting2, (540, 960, 1.0), 2.4),
    (t_and2, (380, 1000, 0.9), 0.1),
    (t_and2 + 0.1, (700, 1000, 0.9), 3.0),   # sideways dolly, like a corridor
    (t_but, (560, 940, 1.02), 1.6),
    (t_idont - 0.4, (340, 990, 1.12), 1.8),
    (t_the_win - 0.4, (520, 760, 1.04), 1.6),   # bring the window into frame for the shrink
])
follow_track = Track([(0, 0.0, 0), (t_waiting2, 0.15, 1.5), (t_and2, 0.0, 0.5), (t_but, 0.15, 1.0),
                      (t_idont - 0.4, 0.0, 1.0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_waiting2, mood_vec("drifting"), 1.4),
    (t_ithink, mood_vec("melancholy"), 1.6),
    (t_but - 0.1, mood_vec("warm"), 1.4),
    (t_seven, mood_vec("curious"), 1.0),
    (t_still, mood_vec("drifting"), 0.8),
    (t_the_win - 0.2, mood_vec("unease"), 0.8),
])

GREY = dict(top=(200, 206, 216), bot=(232, 234, 238), clouds=0.6, cloud_v=4.0)
env_track = Track([
    (0, SKY(**GREY), 0),
    (t_time - 0.2, SKY(top=(196, 200, 214), bot=(230, 230, 236), clouds=0.6, cloud_v=0.4, echo=0.8, drone=0.5), 1.2),
    (t_ithink, SKY(**GREY, echo=0.0, drone=0.4), 1.5),
    (t_and2, SKY(top=(185, 190, 205), bot=(225, 226, 232), clouds=0.5, cloud_v=2, drone=0.45), 1.5),
    (t_but, SKY(top=(195, 210, 232), bot=(250, 236, 214), clouds=0.4, cloud_v=4, sun=0.45, sun_r=26, sun_y=0.4,
                drone=0.6), 1.6),
    (t_seven, SKY(top=(200, 206, 220), bot=(236, 234, 236), clouds=0.4, cloud_v=3, drone=0.4), 1.5),
    (t_the_win, SKY(top=(196, 198, 214), bot=(230, 228, 234), clouds=0.4, cloud_v=1, win_scale=0.86, drone=0.25), 1.4),
])

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=6, tally_new=[(t_seven - 0.1, 0.6)])
N.main("nigel_bain_ep007_waiting.mp4")
