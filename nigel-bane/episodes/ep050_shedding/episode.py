"""Day 50 — "shedding" (posts as `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII shedding`).
Body arc 2/4 (the hand outline on OUR side of the glass, drawn on D49). Owner-approved script, 2026-11-27.
THE LINE: "The hand you just put down isn't quite the one you had last month. There was no day it happened."
C: "Put your hand down flat. On your leg. The table. Anything. Leave it there." — he pats his own hand flat on his leg.
T (fear): yesterday's outline "fit me exactly"; he lays his palm back in it and it doesn't fit (the thumb's out); again:
worse (the fingers are out); once more: further out. His own hand is changing under him and he can't stop it.
Bridge: he never felt it change, he's been in it the whole time -> your skin, bit by bit, while you watch this.
Ending (question): "Is that the same hand? ...How would you know?"
The outline is shown and named in this video ("Yesterday something drew round my hand. Right here."). One continuous shot.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
import hand_outline as HO
from nigel import (P, SKY, Track, mood_vec, KNOCK, STAND, smooth)

N.setup()
T, TE = N.T, N.TE

t_put, t_flat, t_leg, t_anything, t_leave = T("put"), TE("flat"), T("leg"), T("anything"), T("leave")
t_yesterday, t_right, t_glass, t_exactly = T("yesterday"), T("right"), TE("glass"), TE("exactly")
t_doesnt, t_thumbs, t_again, t_worse, t_fingers = T("doesn't"), T("thumb's"), TE("again"), T("worse"), T("fingers")
t_i, t_whole, t_once, t_more, t_further = T("i"), T("whole"), T("once"), TE("more"), T("further")
t_skin, t_bit, t_watching, t_the_hand, t_month = T("skin"), T("bit"), T("watching"), T("hand", 3), TE("month")
t_there, t_lift, t_look, t_is, t_how, t_end = T("there", 3), T("lift"), T("look"), T("is", 2), T("how"), TE("know")

# three tries: (palm lands, palm lifts, how wrong it is: scale, screen offset)
TRIES = [(t_exactly + 0.35, t_again - 0.35, 1.07, (-16, 12)),
         (t_again + 0.35, t_once - 0.2, 1.13, (10, -8)),
         (t_more + 0.35, t_skin + 0.6, 1.2, (-6, -18))]

def try_at(t):
    """pin weight, scale, offset of his palm on the outline at time t (eases between tries)"""
    for i, (a, b, sc, off) in enumerate(TRIES):
        if a - 0.6 <= t <= b + 0.6:
            w = smooth((t - a + 0.6) / 0.6) * (1 - smooth((t - b) / 0.6))
            return w, sc, off
    return 0.0, 1.0, (0, 0)

# ------------------------------------------------------------------ poses
PAT = P(STAND, relb=(520, 1150), rhand=(512, 1268), look=(0.15, 0.55), tilt=0.06, swing=0.0)        # hand flat on his leg
TO_US = P(STAND, look=(0.0, 0.0), swing=0.0)
SHOWS = P(STAND, relb=(600, 1120), rhand=(690, 1040), finger=1.0, look=(0.6, 0.4), tilt=0.08, swing=0.0)   # "Right here"
ON = P(STAND, relb=HO.HAND["relb"], rhand=HO.HAND["rhand"], palm=HO.HAND["palm"], spread=1.0,
       look=(0.55, 0.45), tilt=0.06, eyescale=1.06, swing=0.0)                                       # palm on the glass
ON_US = P(ON, look=(0.0, 0.0), tilt=0.0, eyescale=1.1)
OFF = P(STAND, relb=(560, 1130), rhand=(612, 1080), look=(0.5, 0.35), tilt=0.05, swing=0.0)          # hand just off the glass
AFRAID = P(STAND, relb=(540, 1130), rhand=(560, 1090), look=(0.0, 0.05), eyescale=1.12, tilt=-0.03, swing=0.0)
SOFT = P(STAND, look=(0.05, 0.1), tilt=0.04, swing=0.0)
OWN = P(STAND, relb=(540, 1120), rhand=(432, 1030), palm=0.95, look=(-0.15, 0.6), tilt=-0.08, eyescale=1.08, swing=0.0)  # looks at his own hand
LAST = P(STAND, relb=(540, 1120), rhand=(440, 1040), palm=0.9, look=(0.0, 0.0), eyescale=1.1, tilt=0.0, swing=0.0)

pose_track = Track([
    (0, KNOCK, 0),
    (t_put - 0.3, TO_US, 0.6),
    (t_flat - 0.6, PAT, 0.8),                       # "Put your hand down flat." — pats it onto his leg
    (t_leave + 0.4, TO_US, 0.8),
    (t_right - 0.4, SHOWS, 0.9),                    # "Right here, on your side of the glass."
    (t_exactly - 0.25, OFF, 0.6),
    (TRIES[0][0] - 0.5, ON, 0.5),                   # try 1
    (t_doesnt + 0.6, P(ON, eyescale=1.12), 0.4),
    (TRIES[0][1], OFF, 0.5),
    (TRIES[1][0] - 0.5, ON, 0.5),                   # try 2
    (t_fingers, P(ON, eyescale=1.16, tilt=0.1), 0.5),
    (t_i - 0.2, ON_US, 0.8),                        # "I didn't feel anything change."
    (TRIES[1][1], OFF, 0.5),
    (TRIES[2][0] - 0.5, ON, 0.5),                   # try 3
    (t_further, P(ON, eyescale=1.2, tilt=0.12, shut=0.0), 0.5),
    (t_skin + 0.6, AFRAID, 0.8),                    # takes it off; to us
    (t_bit, SOFT, 1.2),
    (t_the_hand - 0.4, TO_US, 1.0),
    (t_lift - 0.2, OWN, 1.0),                       # "Lift it up. Look at it."
    (t_is - 0.3, LAST, 1.0),                        # "Is that the same hand?"
])

def hook(t, p):
    w, sc, off = try_at(t)
    return HO.pin(p, t, cam_track, w, offset=off, scale=sc)

x_track = Track([(0, 0.0, 0)])

cam_track = Track([                                          # ONE continuous shot
    (0, (470, 880, 1.6), 0),
    (t_put - 0.2, (525, 1010, 1.3), 2.5),                    # out: his hand going flat on his leg
    (t_yesterday, HO.CAM, 3.0),                              # the outline on the glass, him beside it
    (TRIES[0][0], (515, 955, 1.6), 6.0),                     # slow push in through the first two tries
    (t_i, (500, 925, 1.72), 5.0),
    (TRIES[2][0] - 0.2, (515, 950, 1.62), 2.5),
    (t_skin + 0.3, (480, 880, 1.66), 6.0),                   # onto his face for the turn
    (t_the_hand, (505, 930, 1.5), 4.0),
    (t_lift - 0.3, (520, 905, 1.62), 3.0),                   # his own hand, held up in front of him
    (t_how - 0.6, (485, 870, 1.8), 2.5),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_yesterday, mood_vec("drifting"), 1.2),
    (t_doesnt, mood_vec("uncanny"), 0.8),
    (t_worse, mood_vec("unease"), 0.8),
    (t_i, mood_vec("lonely"), 1.2),
    (t_further, mood_vec("unease"), 0.8),
    (t_skin, mood_vec("drifting"), 1.5),
    (t_the_hand, mood_vec("melancholy"), 1.5),
    (t_lift, mood_vec("awe"), 1.2),
    (t_how, mood_vec("uncanny"), 1.0),
])

MORNING = dict(top=(176, 196, 222), bot=(238, 226, 214), clouds=0.5, cloud_v=5.0, sun=0.45, sun_y=0.62, sun_r=30)
sky = Track([(0, SKY(**MORNING, drone=0.14), 0), (t_doesnt, SKY(**MORNING, drone=0.22), 3.0),
             (t_further, SKY(**MORNING, drone=0.32), 2.0), (t_skin + 0.6, SKY(**MORNING, drone=0.08), 2.5)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

def glass(cr, t, pose, env, to_screen):
    N._palm["pos"] = None                           # no greasy print: the traced line is the only mark
    HO.draw(cr, progress=1.0, t=t)

sfx = [(a, "knock_far", 0.10) for a, _, _, _ in TRIES]   # the soft pat of his palm landing on the glass

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track, tally_base=50, pose_hook=hook,
            glass_hook=glass, sfx=sfx, caption_avoid=[(0, 99, HO.caption_box(cam_track))])
N.main("nigel_bane_ep050_shedding.mp4")
