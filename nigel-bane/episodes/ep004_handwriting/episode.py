"""Day 4 — "Handwriting". Mark 3 is in his hand but not his memory.
Memory = notes from people who used to be you. Hook: tomorrow he'll try to remember something on purpose.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, THINK, ONE, OPEN, SHRUG, CHEST, PRESENT, STAND)

N.setup()
T, TE = N.T, N.TE

TALLYLOOK = P(look=(-0.85, 0.15), tilt=-0.12, lelb=(380, 1060), lhand=(330, 1010), swing=0.0)
LOOKHAND = P(relb=(560, 1040), rhand=(570, 905), look=(0.45, 0.15), tilt=0.1, swing=0.0)
TEMPLE = P(relb=(585, 965), rhand=(598, 845), finger=1.0, look=(-0.2, -0.25), tilt=-0.08, swing=0.0)
TOUCH3 = P(look=(-0.85, 0.1), tilt=-0.1, lelb=(335, 1085), lhand=(279, 1015), swing=0.0)   # hand on mark 3
SOFT = P(PRESENT, tilt=0.06, look=(0.0, 0.1))

t_four, t_drew, t_watched, t_but = T("four"), T("drew"), T("watched"), T("but")
t_third, t_hand_wr, t_myhand, t_just = T("third"), T("handwriting"), T("hand"), T("just")
t_and, t_learning, t_first, t_somebody = T("and"), T("learning"), T("first"), T("somebody")
t_itwas, t_supposedly, t_so, t_hes = T("it"), T("supposedly"), T("so"), T("he's")
t_left, t_you_were, t_maybe, t_notes = T("left"), T("were"), T("maybe"), T("notes")
t_kind, t_thorough, t_tomorrow, t_justsee = T("kind"), T("thorough"), T("tomorrow"), T("just", 3)

pose_track = Track([
    (0, KNOCK, 0),
    (TE("there") + 0.1, STAND, 0.6),
    (t_four - 0.4, TALLYLOOK, 0.6),
    (t_drew + 0.3, TALLYLOOK, 0.3),
    (t_watched - 0.1, PRESENT, 0.7),
    (t_but - 0.1, TALLYLOOK, 0.7),
    (t_hand_wr - 0.2, LOOKHAND, 0.6),
    (t_just - 0.1, SHRUG, 0.6),
    (t_and, THINK, 0.9),
    (t_learning - 0.2, TEMPLE, 0.5),
    (t_first - 0.2, OPEN, 0.6),
    (t_somebody - 0.1, PRESENT, 0.6),
    (t_itwas - 0.1, CHEST, 0.5),
    (t_supposedly - 0.1, SHRUG, 0.5),
    (t_so - 0.1, THINK, 0.7),
    (t_left - 0.3, TOUCH3, 0.9),
    (t_maybe - 0.2, STAND, 1.0),
    (t_kind - 0.1, SOFT, 0.8),
    (t_tomorrow - 0.1, ONE, 0.5),
    (t_justsee - 0.1, THINK, 0.7),
])

x_track = Track([
    (0, 0.0, 0),
    (TE("there") + 0.2, -195.0, 1.7),
    (t_and - 0.2, 20.0, 2.2),
    (t_so - 0.3, -150.0, 2.0),
    (t_maybe, 60.0, 4.5),          # slow walk away; his past selves trail behind
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (TE("there"), (360, 990, 1.12), 1.8),
    (t_third - 0.4, (220, 1010, 1.55), 1.6),       # in on the third mark
    (t_hand_wr, (330, 950, 1.15), 1.2),
    (t_and, (540, 960, 1.0), 2.0),
    (t_so, (420, 980, 1.08), 2.0),
    (t_maybe, (540, 960, 1.0), 3.0),
    (t_tomorrow, (520, 900, 1.12), 3.0),
])
follow_track = Track([(0, 0.0, 0), (t_and, 0.2, 1.5)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_third - 0.2, mood_vec("uncanny"), 0.8),
    (t_and, mood_vec("drifting"), 1.2),
    (t_first, mood_vec("awe"), 0.3),                 # "the first time I saw a colour"
    (t_first + 0.5, mood_vec("warm"), 0.3),
    (t_first + 1.0, mood_vec("curious"), 0.3),
    (t_first + 1.5, mood_vec("uncanny"), 0.3),
    (t_somebody, mood_vec("drifting"), 0.8),
    (t_so, mood_vec("melancholy"), 1.2),
    (t_you_were - 0.3, mood_vec("warm"), 1.2),
    (t_maybe, mood_vec("drifting"), 1.5),
    (t_kind, mood_vec("warm"), 1.0),
    (t_tomorrow, mood_vec("curious"), 1.0),
])

MORNING = dict(top=(205, 222, 240), bot=(250, 240, 214), clouds=0.6, cloud_v=9.0)
env_track = Track([
    (0, SKY(**MORNING), 0),
    (t_third - 0.2, SKY(**MORNING, drone=0.45), 1.0),
    (t_first - 0.1, SKY(top=(255, 120, 140), bot=(255, 220, 120), clouds=0.2, cloud_v=9, drone=0.6), 0.3),
    (t_first + 0.5, SKY(top=(120, 220, 160), bot=(240, 250, 160), clouds=0.2, cloud_v=9, drone=0.6), 0.3),
    (t_first + 1.0, SKY(top=(110, 140, 255), bot=(220, 170, 255), clouds=0.2, cloud_v=9, drone=0.6), 0.3),
    (t_first + 1.6, SKY(**MORNING, drone=0.4), 1.2),
    (t_so, SKY(top=(175, 185, 205), bot=(225, 222, 228), clouds=0.6, cloud_v=4, drone=0.4), 1.5),
    (t_maybe, SKY(top=(190, 185, 215), bot=(240, 225, 225), clouds=0.4, cloud_v=-6, echo=1.0, drone=0.55), 1.2),
    (t_kind, SKY(top=(205, 215, 238), bot=(252, 238, 210), clouds=0.5, cloud_v=6, echo=0.0, drone=0.45), 1.5),
    (t_tomorrow, SKY(top=(205, 215, 238), bot=(252, 238, 210), clouds=0.3, cloud_v=4, after=0.7, sun_y=0.35,
                     drone=0.4), 1.5),     # the dotted ghost of the old sun: what he'll try to remember
])

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=3, tally_new=[(t_four - 0.1, 0.6)])
N.main("nigel_bain_ep004_handwriting.mp4")
