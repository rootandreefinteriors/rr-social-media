"""Day 14 — "Performing". The bird watches → idea: we're different when watched; which one is real?
Signature visuals: a stage spotlight on "I'm performing. For a bird." (he bows); he walks out of frame on
"the one nobody sees" and keeps talking off-screen. Ends implicating the viewer: "Not since you showed up."
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, ONE, OPEN, CHEST, PRESENT, STAND, THINK)

N.setup()
T, TE = N.T, N.TE

WLOOK = P(head=(468, 766), tilt=0.13, look=(0.85, -0.75), swing=0.0)
STRAIGHT = P(head=(450, 755), neck=(452, 928), look=(0.0, -0.1), tilt=0.0, swing=0.0)
BOW = P(head=(470, 800), tilt=0.35, look=(0.2, 0.6), lelb=(392, 1110), lhand=(380, 1210),
        relb=(560, 1040), rhand=(612, 1000), swing=0.0)
POINT_CAM = P(relb=(560, 1062), rhand=(612, 992), finger=1.0, look=(0.0, 0.0), swing=0.0)
STARE = P(look=(0.0, 0.0), tilt=0.0, eyescale=1.1, swing=0.0)

t_second, t_it_watches, t_and1, t_im_diff = T("second"), T("watches"), T("and"), T("different")
t_stand, t_think, t_performing, t_bird = T("stand"), T("think"), T("performing"), T("bird")
t_everybody, t_shower, t_bus, t_third = T("everybody"), T("shower"), T("bus"), T("third")
t_watching, t_so, t_or, t_heres = T("watching", 2), T("so"), T("or"), T("here's")
t_dont, t_ive, t_not_since = T("don't"), T("i've", 2), T("since")

pose_track = Track([
    (0, KNOCK, 0),
    (t_second - 0.1, WLOOK, 0.7),
    (t_and1 - 0.1, THINK, 0.6),
    (t_stand - 0.2, STRAIGHT, 0.6),
    (t_think - 0.1, CHEST, 0.5),
    (t_performing - 0.2, OPEN, 0.5),
    (t_bird - 0.3, BOW, 0.6),                    # a little bow, for a bird
    (t_everybody, STAND, 0.6),
    (t_third - 0.1, PRESENT, 0.6),
    (t_watching - 0.2, POINT_CAM, 0.4),          # watching this
    (t_so, THINK, 0.6),
    (t_heres - 0.1, STAND, 0.6),
    (t_ive - 0.2, STARE, 1.0),
])

x_track = Track([
    (0, 0.0, 0),
    (t_second, 150.0, 1.5),
    (t_everybody - 0.2, -150.0, 2.0),            # the shower person...
    (t_bus - 0.6, 120.0, 2.0),                   # ...the bus person...
    (t_third - 0.4, 0.0, 1.4),                   # ...and the one watching this
    (t_or - 0.6, -760.0, 2.6),                   # walks right out of frame: the one nobody sees
    (t_heres + 0.2, -20.0, 2.6),                 # comes back
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_second - 0.2, (720, 650, 1.15), 2.0),
    (t_and1, (540, 960, 1.0), 1.6),
    (t_performing - 0.3, (560, 900, 1.15), 1.0),
    (t_everybody, (540, 960, 1.0), 1.4),
    (t_watching - 0.2, (452, 800, 1.6), 1.2),    # into his eyes: watching this
    (t_so, (600, 900, 0.95), 2.0),               # camera stays put while he walks out
    (t_ive - 0.2, (450, 790, 1.7), 3.0),         # close on him at the end
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_and1, mood_vec("drifting"), 1.0),
    (t_performing, mood_vec("awe"), 0.6),
    (t_everybody, mood_vec("curious"), 1.0),
    (t_watching, mood_vec("uncanny"), 0.8),
    (t_heres, mood_vec("melancholy"), 1.2),
    (t_ive, mood_vec("unease"), 1.2),
])

DAY = dict(top=(200, 214, 236), bot=(248, 242, 228), clouds=0.4, cloud_v=4.0, perch=1.0, perch_x=0.62)
def sky(tilt=0.0, **kw):
    d = dict(DAY); d.update(kw)
    return SKY(perch_tilt=tilt, **d)
env_track = Track([
    (0, sky(drone=0.3), 0),
    (t_stand, sky(tilt=0.2, drone=0.35), 0.5),
    (t_performing - 0.2, sky(top=(255, 200, 140), bot=(255, 230, 190), sun=0.9, sun_y=0.4, beam=1.0, tilt=0.3,
                             drone=0.5, shimmer=0.6), 0.5),     # spotlight
    (t_everybody, sky(drone=0.35), 1.2),
    (t_so, sky(top=(185, 195, 222), bot=(236, 234, 236), drone=0.2), 1.5),
    (t_or, sky(top=(170, 178, 205), bot=(226, 226, 232), tilt=-0.25, drone=0.1), 1.0),   # the bird looks where he went
    (t_heres, sky(top=(185, 195, 222), bot=(236, 234, 236), drone=0.25), 1.2),
    (t_ive, sky(top=(160, 165, 195), bot=(220, 218, 228), tilt=0.35, drone=0.15), 1.5),  # the bird turns to you too
])

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=14, tally_new=[])
N.main("nigel_bane_ep014_performing.mp4")
