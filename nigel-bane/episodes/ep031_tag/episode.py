"""Day 31 — "A tag" (posts as `… I inheriting`). A paper tag on a string lies face down on the floor; it wasn't there
last night. C: "Look down. What's on your floor?" — he snaps his gaze down to it. T: he won't turn it over; he sits
beside it, dead still, through the whole middle, then on "Okay." picks it up and turns it: "for nigel" — not his
handwriting. IDEA (you): almost nothing around you did you choose — the bed, the lamp, the cup, your name; somebody
handed it to you and you kept it. UNSETTLE: "Even the room you're watching this in." (whispered) + the tag in someone
else's hand. LIFT (implied): somebody thought to leave him something. HOOK: "Look around. Count what you actually chose."
Voice: reused the Nov 6 cloud recording (no re-voicing).
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, lerp, smooth, KNOCK, SIT, SIT_CAM, SIT_WIDE, SIT_REACH)

N.setup()
T, TE = N.T, N.TE

LOOKDOWN = P(head=(476, 800), neck=(462, 966), look=(0.45, 0.9), tilt=0.16, eyescale=1.1, swing=0.0)
STARE = P(LOOKDOWN, look=(0.5, 0.85), tilt=0.2)
SITTAG = P(SIT, head=(436, 1006), look=(0.75, 0.75), tilt=0.12, eyescale=1.04)                 # sits by it, staring
STILL = P(SITTAG, look=(0.8, 0.8), tilt=0.16)
SITYOU = P(SIT_CAM, look=(0.0, 0.02))
SITOPEN = P(SIT_WIDE, look=(0.0, 0.0), eyescale=1.12)
REACH = P(SIT_REACH, look=(0.85, 0.7), tilt=0.15)
HOLD = P(SIT_CAM, relb=(560, 1120), rhand=(590, 1030), look=(0.55, 0.15), tilt=0.06)              # holds it up
HOLDYOU = P(HOLD, look=(0.0, 0.02), tilt=0.0, eyescale=1.06)

t_look, t_theres, t_face, t_it_wasnt, t_i_havent = T("look"), T("there's"), T("face"), T("wasn't"), T("haven't")
t_look2, t_bed, t_almost, t_somebody, t_even = T("look", 2), T("bed"), T("almost"), T("somebody"), T("even")
t_okay, t_okay_e, t_says, t_for, t_thats, t_look3, t_chose_e = (
    T("okay"), TE("okay"), T("says"), T("for"), T("that's"), T("look", 3), TE("chose"))

PICK0, PICK1 = t_okay_e + 0.25, t_okay_e + 1.05        # lifts it off the floor
FLIP0, FLIP1 = PICK1, t_says - 0.15                     # turns it over

pose_track = Track([
    (0, KNOCK, 0),
    (t_look - 0.3, LOOKDOWN, 0.35),                     # "Look down." — snaps down to it
    (t_theres, STARE, 1.0),
    (t_it_wasnt - 0.5, SITTAG, 1.4),                    # sits down beside it
    (t_i_havent, STILL, 2.0),
    (t_look2 - 0.3, SITYOU, 1.0),                       # to you
    (t_almost, SITOPEN, 1.2),
    (t_somebody, SITYOU, 1.2),
    (t_even - 0.2, P(SITOPEN, eyescale=1.18), 0.8),
    (t_okay - 0.5, P(SITTAG, look=(0.85, 0.75)), 1.0),
    (PICK0 - 0.2, REACH, 0.5),                          # picks it up
    (PICK1, HOLD, 0.6),
    (t_thats - 0.2, HOLDYOU, 0.8),
])
x_track = Track([(0, 0.0, 0), (t_it_wasnt - 0.5, -40.0, 1.2)])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_look - 0.2, (540, 1180, 1.3), 1.0),              # down to the floor with him
    (t_theres, (690, 1410, 2.7), 1.6),                  # the tag, face down, on its string
    (t_it_wasnt, (560, 1230, 1.32), 1.6),               # he sits beside it
    (t_i_havent, (590, 1290, 1.55), t_look2 - t_i_havent),
    (t_look2 - 0.2, (470, 1080, 1.45), 1.4),            # to you
    (t_bed, (460, 1060, 1.62), t_even - t_bed),         # slow push
    (t_even - 0.2, (450, 1030, 1.85), 2.5),
    (t_okay - 0.6, (580, 1230, 1.4), 1.2),              # back to the tag
    (FLIP1 - 0.3, (520, 1045, 2.0), 1.0),              # what it says
    (t_thats, (500, 1070, 1.6), 1.2),
    (t_look3, (470, 1050, 1.8), t_chose_e - t_look3 + 0.6),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_look, mood_vec("unease"), 0.4),
    (t_theres, mood_vec("uncanny"), 1.2),
    (t_it_wasnt, mood_vec("lonely"), 1.2),
    (t_i_havent, mood_vec("unease"), 1.2),
    (t_look2, mood_vec("drifting"), 1.6),
    (t_even, mood_vec("uncanny"), 1.0),
    (t_for, mood_vec("unease"), 0.6),
    (t_look3, mood_vec("uncanny"), 1.4),
])

DAY = dict(top=(190, 198, 210), bot=(234, 236, 240), clouds=0.6, cloud_v=4.0, sun=0.12, sun_y=0.4, sun_r=30)
sky = Track([
    (0, SKY(**DAY, drone=0.3), 0),
    (t_i_havent, SKY(**DAY, drone=0.12), 1.5),                  # quiet while he won't touch it
    (t_look2, SKY(**DAY, drone=0.28), 2.0),
    (t_okay - 0.5, SKY(**DAY, drone=0.06), 1.0),                # dead quiet as he turns it over
    (t_thats, SKY(**DAY, drone=0.3), 1.5),
])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

FLOOR_TAG = (726, 1468)
def tag(cr, t, pose, env):
    lift = smooth((t - PICK0) / (PICK1 - PICK0))
    flip = smooth((t - FLIP0) / (FLIP1 - FLIP0))
    hx, hy = pose["rhand"]
    x, y = lerp(FLOOR_TAG, (hx + 52, hy - 8), lift)
    N.draw_tag(cr, x, y, ang=lerp(-0.12, 0.05, lift) + 0.03 * math.sin(t * 1.3) * lift, scale=lerp(1.0, 1.35, lift),
               flip=flip, squash=lerp(0.5, 1.0, lift), string=True)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=30, draw_hook=tag)
N.main("nigel_bane_ep031_tag.mp4")
