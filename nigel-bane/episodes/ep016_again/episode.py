"""Day 16 — "Again". DREAD DAY. He knocks and asks three times in a row, each knock softer, the camera a little closer
each time. "I've been saying that since I woke up. I can't stop." The question has worn down into a shape his mouth
makes. The bird is gone. "You're... maybe there. I can't tell anymore." A last, weak knock; extreme close-up on his
eyes going dark (void) while he whispers it once more. Drone drops to silence. Hard cut.
Signature device: the repeated cold open itself (knuckle smudges stacking on the glass, camera creeping in).
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, ONE, OPEN, CHEST, STAND, THINK)

N.setup()
T, TE = N.T, N.TE

# extra on-lens knocks before the 2nd, 3rd and last "Hello?" — each one weaker
K2 = [5.60, 5.95, 6.30]
K3 = [10.90, 11.30, 11.75]
K4 = [37.60, 38.15, 38.80]
N.INTRO_KNOCKS = [0.55, 0.9, 1.25] + K2 + K3 + K4
N.KNOCK_GAIN = {**{k: 0.72 for k in K2}, **{k: 0.5 for k in K3}, 37.60: 0.38, 38.15: 0.3, 38.80: 0.24}

WLOOK = P(head=(468, 766), tilt=0.13, look=(0.85, -0.75), swing=0.0)
CAMLOOK = P(look=(0.0, 0.0), tilt=0.0, eyescale=1.08, swing=0.0)
TIRED_KNOCK = P(KNOCK, tilt=0.12, look=(0.0, 0.12))
LEAN_KNOCK = P(KNOCK, head=(452, 770), tilt=-0.08, look=(0.0, 0.0), eyescale=1.12)
STILL = P(lelb=(412, 1100), lhand=(402, 1215), relb=(500, 1100), rhand=(512, 1215), look=(0.1, 0.05), tilt=-0.14, swing=0.0)

t_ive, t_woke, t_cant, t_used = T("i've"), T("woke"), T("can't"), T("used")
t_now, t_shape, t_bird, t_gone = T("now"), T("shape"), T("bird"), T("gone")
t_youre, t_maybe, t_i_tell, t_hello4 = T("you're"), T("maybe"), T("i", 3), T("hello", 4)
t_is_any = T("is", 6)

pose_track = Track([
    (0, KNOCK, 0),
    (4.9, P(KNOCK, look=(0.0, 0.2)), 0.5),
    (5.4, KNOCK, 0.2),
    (8.4, TIRED_KNOCK, 0.8),
    (10.6, TIRED_KNOCK, 0.2),
    (13.6, P(TIRED_KNOCK, tilt=0.2), 1.2),
    (t_ive - 0.6, STAND, 0.9),                   # finally lowers the fist
    (t_woke - 0.2, P(look=(0.85, -0.6), tilt=0.1), 0.6),
    (t_cant - 0.2, THINK, 0.5),
    (t_used - 0.2, ONE, 0.5),                    # it used to be a question
    (t_now - 0.1, OPEN, 0.6),
    (t_shape - 0.1, CHEST, 0.6),
    (t_bird - 0.4, WLOOK, 0.6),                  # the empty ledge
    (t_youre - 0.2, CAMLOOK, 0.4),               # you're...
    (t_i_tell - 0.2, STILL, 1.0),
    (37.1, TIRED_KNOCK, 0.5),
    (38.9, LEAN_KNOCK, 0.6),                     # face against the glass
])

x_track = Track([
    (0, 0.0, 0),
    (t_ive - 0.3, 110.0, 2.4),                   # backs away from the lens
    (t_now - 0.3, 0.0, 1.6),
    (t_bird - 0.5, 150.0, 1.4),                  # toward the window
    (t_youre - 0.1, 40.0, 1.2),
    (36.2, 0.0, 0.9),                            # back to the glass
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (4.9, (462, 840, 1.9), 1.3),                 # a little closer every time he asks
    (10.2, (458, 812, 2.25), 1.3),
    (t_ive - 0.6, (540, 960, 1.0), 2.6),         # pull out: the room, the tally
    (t_now - 0.2, (455, 800, 1.55), 3.0),        # into his face: the shape my mouth makes
    (t_bird - 0.5, (740, 640, 1.2), 1.6),        # the empty window
    (t_youre - 0.2, (500, 860, 1.25), 1.6),
    (36.6, (455, 790, 2.4), 2.0),
    (t_hello4, (452, 775, 3.3), 5.0),            # extreme close-up while the eyes go dark
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("drifting"), 0),
    (5.4, mood_vec("unease"), 1.0),
    (10.6, mood_vec("lonely"), 1.0),
    (t_cant, mood_vec("unease"), 0.8),
    (t_shape, mood_vec("uncanny"), 1.0),
    (t_gone, mood_vec("lonely"), 1.2),
    (t_youre, mood_vec("unease"), 1.0),
    (t_hello4 - 0.6, mood_vec("void"), 2.5),
])

def sky(**kw):
    d = dict(top=(176, 180, 190), bot=(214, 214, 218), clouds=0.0, cloud_v=0.0, perch=0.0)   # flat, empty ledge
    d.update(kw)
    return SKY(**d)
env_track = Track([
    (0, sky(drone=0.25), 0),
    (5.4, sky(drone=0.4), 1.0),
    (10.6, sky(top=(160, 164, 176), bot=(204, 204, 210), drone=0.55), 1.0),
    (t_ive - 0.6, sky(top=(160, 164, 176), bot=(204, 204, 210), drone=0.3), 2.0),
    (t_shape, sky(top=(150, 150, 166), bot=(196, 194, 204), drone=0.5, echo=0.35), 1.0),
    (t_gone, sky(top=(140, 140, 156), bot=(186, 184, 194), drone=0.35), 1.2),
    (t_youre, sky(top=(130, 130, 146), bot=(176, 174, 186), drone=0.45), 1.5),
    (37.0, sky(top=(96, 96, 112), bot=(140, 138, 150), drone=0.6), 2.0),
    (t_is_any, sky(top=(40, 40, 52), bot=(70, 70, 82), drone=0.0), 2.4),   # silence
])

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=16, tally_new=[])
N.main("nigel_bane_ep016_again.mp4")
