"""Day 11 — "Deciding". The bird flies past twice, slower the second time ("like it's deciding something").
Idea: decisions show up after you've already acted, like a receipt; you find out what you wanted by watching what you did.
The props ARE the idea: two passes illustrate "slower"; he's already walking before he says so; ghosts = "what you did".
Hook: "If it lands, I won't move. I'll just let it decide." (bird swoops low toward the ledge; lands D12)
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, THINK, OPEN, SHRUG, CHEST, PRESENT, STAND, READ)

N.setup()
T, TE = N.T, N.TE

WLOOK = P(head=(468, 766), tilt=0.13, look=(0.85, -0.75))
FEET = P(look=(0.1, 0.9), tilt=-0.15)                       # looking down at his own walking feet
RECEIPT = P(READ, look=(0.0, 0.55), tilt=-0.08)             # a little slip of paper in his hands
LOOKBACK = P(look=(-0.85, 0.1), tilt=-0.08, swing=0.0)
SOFT = P(PRESENT, tilt=0.06, look=(0.0, 0.1))
FROZEN = P(WLOOK, lelb=(412, 1100), lhand=(402, 1215), relb=(500, 1100), rhand=(512, 1215), swing=0.0)

t_came, t_flew, t_slower, t_like1 = T("came"), T("flew"), T("slower"), T("like")
t_and, t_whether1, t_whether2, t_then = T("and"), T("whether"), T("whether", 2), T("then")
t_how, t_dont, t_notice, t_walking = T("how"), T("don't"), T("notice"), T("walking")
t_decision, t_like2, t_maybe, t_you = T("decision"), T("like", 2), T("maybe"), T("you")
t_which, t_but, t_it_means, t_if = T("which"), T("but"), T("means"), T("if")

pose_track = Track([
    (0, KNOCK, 0),
    (t_came - 0.1, WLOOK, 0.8),
    (t_like1 - 0.1, THINK, 0.7),
    (t_and - 0.1, PRESENT, 0.6),
    (t_whether2 - 0.1, CHEST, 0.5),
    (t_then - 0.1, P(STAND, look=(0.3, -0.2)), 0.6),
    (t_how - 0.1, THINK, 0.6),
    (t_dont - 0.1, SHRUG, 0.5),
    (t_notice - 0.1, FEET, 0.6),                # ...and notices he's already walking
    (t_decision - 0.1, STAND, 0.5),
    (t_like2 - 0.2, RECEIPT, 0.5),
    (t_maybe - 0.1, STAND, 0.6),
    (t_you - 0.1, LOOKBACK, 0.8),               # watching what you did: the trail behind him
    (t_which - 0.1, SOFT, 0.8),
    (t_but - 0.1, P(SOFT, look=(0.0, 0.0)), 0.6),
    (t_if - 0.2, FROZEN, 1.0),
])

x_track = Track([
    (0, 0.0, 0),
    (t_came, 140.0, 1.6),
    (t_and, 40.0, 1.8),
    (t_then - 0.3, -160.0, 6.5),                # starts walking BEFORE he says he's walking
    (t_maybe + 0.4, 60.0, 4.0),                 # walks on; the ghosts trail behind
    (t_if - 0.4, 170.0, 1.8),                   # to the window, then freezes
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_came - 0.2, (700, 690, 1.12), 2.0),      # Nigel + window for the two passes
    (t_like1, (540, 960, 1.0), 2.0),
    (t_notice - 0.2, (420, 1180, 1.25), 1.6),   # down toward his feet
    (t_decision, (540, 960, 1.0), 1.6),
    (t_if - 0.4, (760, 640, 1.2), 2.4),
])
follow_track = Track([(0, 0.0, 0), (t_like1, 0.25, 1.5), (t_if - 0.4, 0.0, 1.0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_like1, mood_vec("drifting"), 1.0),
    (t_whether2, mood_vec("melancholy"), 1.0),
    (t_then, mood_vec("curious"), 1.0),
    (t_notice, mood_vec("uncanny"), 0.8),
    (t_maybe, mood_vec("drifting"), 1.2),
    (t_which, mood_vec("warm"), 1.4),
    (t_if, mood_vec("awe"), 1.2),
])

MORNING = dict(top=(170, 205, 240), bot=(248, 240, 222), clouds=0.5, cloud_v=7.0)
env_track = Track([
    (0, SKY(**MORNING), 0),
    (t_then, SKY(**MORNING, echo=0.0, drone=0.45), 1.0),
    (t_maybe, SKY(top=(185, 200, 230), bot=(245, 236, 226), clouds=0.4, cloud_v=4, echo=0.9, drone=0.5), 1.2),
    (t_which, SKY(**MORNING, echo=0.0, drone=0.4), 1.5),
    (t_if - 0.3, SKY(top=(175, 210, 240), bot=(250, 242, 222), clouds=0.3, cloud_v=2, drone=0.15), 1.2),   # hush
])

END = N.words[-1]["end"]
N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=11, tally_new=[],
            birds=[dict(t=t_flew - 0.2, dur=1.1, x0=1.1, x1=-0.15, y=0.32, size=30),         # first pass: quick
                   dict(t=t_slower + 0.1, dur=2.8, x0=1.1, x1=-0.15, y=0.45, size=34),        # second: slower
                   dict(t=END - 1.9, dur=2.6, x0=1.15, x1=0.55, y=0.86, size=36)])          # swooping low toward the ledge
N.main("nigel_bane_ep011_deciding.mp4")
