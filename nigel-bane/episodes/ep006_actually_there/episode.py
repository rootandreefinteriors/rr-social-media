"""Day 6 — "Actually There". No counting today, just looking. Naming things stops you seeing them.
Hook: something moved at the edge of the window (bird glimpse -> pays off Day 15).
Tally: while saying "No counting today" he absent-mindedly scratches mark 6, then stares at his hand.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, THINK, ONE, OPEN, SHRUG, PRESENT, STAND, POINT_UP, ROLL)

N.setup()
T, TE = N.T, N.TE

WLOOK = P(head=(468, 766), tilt=0.13, look=(0.85, -0.75))
GLANCE_TALLY = P(look=(-0.75, 0.1), tilt=-0.08, lelb=(395, 1085), lhand=(345, 1050), swing=0.0)
TINY = P(lelb=(415, 1090), lhand=(440, 1040), relb=(490, 1090), rhand=(468, 1040), look=(0.1, 0.35), swing=0.0)
UPWARD = P(WLOOK, lelb=(400, 1090), lhand=(372, 1180), relb=(505, 1095), rhand=(520, 1185), tilt=0.16)
FACECAM = P(look=(0.0, 0.0), tilt=0.04)
OWNHAND = P(lelb=(338, 1060), lhand=(262, 985), look=(-0.7, 0.4), tilt=-0.14, swing=0.0)   # looks at the hand that just counted
SNAP = P(WLOOK, tilt=0.18, look=(0.95, -0.85), eyescale=1.08)

t_okay, t_no, t_looking, t_white = T("okay"), T("no"), T("looking"), T("white")
t_about, t_but1, t_small, t_thing = T("about"), T("but"), T("small"), T("thing")
t_slowly, t_think, t_you, t_word3 = T("slowly"), T("think"), T("you"), T("word", 3)
t_so2, t_hard, t_sky, t_but2 = T("so", 2), T("hard"), T("sky"), T("but", 2)
t_andso, t_huh, t_something, t_probably = T("and", 3), T("huh"), T("something"), T("probably")

FLICK = t_huh + 0.45

pose_track = Track([
    (0, KNOCK, 0),
    (t_okay - 0.1, STAND, 0.5),
    (T("today") - 0.05, OWNHAND, 0.45),
    (t_looking - 0.2, WLOOK, 0.8),
    (t_white - 0.1, POINT_UP, 0.6),
    (t_about - 0.1, THINK, 0.6),
    (t_but1 - 0.1, SHRUG, 0.5),
    (t_small - 0.2, TINY, 0.5),
    (t_thing - 0.1, OPEN, 0.6),
    (t_slowly - 0.1, P(ROLL, look=(0.7, -0.6), tilt=0.1), 0.6),
    (t_think - 0.1, PRESENT, 0.8),
    (t_you - 0.1, ONE, 0.5),
    (t_word3 - 0.2, SHRUG, 0.6),
    (t_so2 - 0.1, THINK, 0.7),
    (t_sky - 0.2, WLOOK, 0.8),
    (t_but2 - 0.1, UPWARD, 1.5),
    (t_andso - 0.1, FACECAM, 1.2),
    (FLICK + 0.05, SNAP, 0.15),            # head snaps to the window
    (t_probably - 0.1, P(WLOOK, look=(0.3, -0.2), tilt=0.06), 1.4),
])

x_track = Track([
    (0, 0.0, 0),
    (TE("there") + 0.05, -195.0, 1.1),         # straight to the wall, out of habit
    (t_looking - 0.3, 180.0, 2.0),
    (t_think - 0.2, 0.0, 1.8),
    (t_so2 - 0.1, 170.0, 1.8),
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (TE("there") + 0.05, (360, 990, 1.12), 1.1),
    (t_looking - 0.2, (700, 720, 1.12), 2.0),
    (t_think - 0.2, (540, 960, 1.0), 2.0),
    (t_so2, (700, 720, 1.12), 2.0),
    (t_but2, (690, 680, 1.32), 5.0),             # slow push while the sky is "nothing"
    (FLICK, (760, 580, 1.4), 1.6),
])
follow_track = Track([(0, 0.0, 0), (t_think - 0.2, 0.2, 1.0), (t_so2, 0.0, 1.0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_white, mood_vec("drifting"), 1.2),
    (t_slowly - 0.2, mood_vec("uncanny"), 0.8),
    (t_think, mood_vec("curious"), 1.0),
    (t_you, mood_vec("drifting"), 1.0),
    (t_so2, mood_vec("curious"), 1.0),
    (t_but2 - 0.2, mood_vec("awe"), 1.4),
    (t_andso, mood_vec("warm"), 1.2),
    (FLICK, mood_vec("unease"), 0.3),
    (t_probably, mood_vec("drifting"), 1.6),
])

MORNING = dict(top=(196, 214, 236), bot=(246, 240, 226), clouds=0.6, cloud_v=6.0)
env_track = Track([
    (0, SKY(**MORNING), 0),
    (t_white - 0.2, SKY(top=(196, 214, 236), bot=(246, 240, 226), clouds=1.0, cloud_v=3.0, drone=0.45), 1.2),
    (t_slowly - 0.1, SKY(top=(190, 205, 232), bot=(244, 236, 230), clouds=1.0, cloud_v=-14.0, ripple=0.75,
                         drone=0.55), 0.8),
    (t_think, SKY(**MORNING), 1.4),
    (t_sky - 0.1, SKY(top=(45, 120, 255), bot=(130, 195, 255), clouds=0.4, cloud_v=6, drone=0.5), 0.9),  # trying to be blue
    (t_but2 - 0.1, SKY(top=(246, 242, 250), bot=(240, 248, 246), clouds=0.0, cloud_v=0, sparkle=0.35,
                       drone=0.7, shimmer=0.7), 2.0),                                                  # nothing. just there
    (t_huh, SKY(top=(225, 228, 240), bot=(242, 244, 244), clouds=0.2, cloud_v=2, drone=0.25), 1.0),
    (t_probably, SKY(top=(205, 214, 232), bot=(240, 238, 232), clouds=0.4, cloud_v=4, drone=0.2), 2.0),
])

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=5, tally_new=[(t_no - 0.05, 0.6)],
            birds=[dict(t=FLICK, dur=0.22, x0=1.06, x1=0.86, y=0.12, size=13),       # in at the corner...
                   dict(t=FLICK + 0.22, dur=0.26, x0=0.86, x1=1.08, y=0.10, size=13)])  # ...and gone
N.main("nigel_bain_ep006_actually_there.mp4")
