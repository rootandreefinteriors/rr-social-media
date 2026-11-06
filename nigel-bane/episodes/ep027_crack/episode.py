"""Day 27 — "Crack". On the last knock of the open, a tick: a hairline crack appears in the glass where his knuckles hit
— on OUR side. C: "Don't touch the glass." — he snaps his hand back and freezes. T: the crack creeps a little every time
he speaks; will it reach the edge? It stops just short at the cut. IDEA (you): you stop seeing damage after about a week
— a drawer that sticks, a light that flickers, something someone said that you never brought up again. You didn't fix
it; you just stopped seeing it. UNSETTLE: "That's not on my side... It's on yours." + it grows when he talks. LIFT
(implied): he sits down in front of it to keep watching it for you. HOOK: "Whatever's been cracked in your life the
longest... you stopped seeing it about a week in."
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, OPEN, ONE, PRESENT, SIT_CAM)

N.setup()
T, TE = N.T, N.TE

BACK = P(KNOCK, relb=(560, 1075), rhand=(590, 1015), fist=0.7, look=(0.45, 0.3), tilt=-0.08, eyescale=1.1)  # hand snatched back
FROZEN = P(BACK, look=(0.5, 0.35), tilt=-0.05)
LEAN = P(head=(468, 785), neck=(462, 950), relb=(548, 1080), rhand=(575, 1030), look=(0.55, 0.35), tilt=0.1, swing=0.0)
YOURS = P(LEAN, look=(0.1, 0.05), tilt=0.02, eyescale=1.06)
CAREFUL = P(LEAN, lelb=(410, 1080), lhand=(440, 1020), relb=(500, 1080), rhand=(468, 1020), look=(0.45, 0.3))  # hands together, very still
TO_YOU = P(look=(0.0, 0.03), tilt=0.0, swing=0.0)
HOME = P(PRESENT, look=(0.0, 0.05))
DRAWER = P(ONE, look=(0.1, 0.0))
SAID = P(TO_YOU, relb=(522, 1102), rhand=(462, 1030), lelb=(400, 1100), lhand=(386, 1200), tilt=-0.07)
WEEK = P(OPEN, look=(0.0, 0.0), tilt=0.04)
FLAT = P(TO_YOU, eyescale=1.06)
SITLOOK = P(SIT_CAM, look=(0.45, 0.1), tilt=0.06)
SITYOU = P(SIT_CAM, look=(0.05, 0.02), eyescale=1.05)

t_there_e, t_dont, t_thats, t_its1, t_every1 = TE("there"), T("don't"), T("that's"), T("it's"), T("every")
t_it_goes, t_so, t_careful_e = T("goes"), T("so"), TE("careful")
t_you_have, t_something1, t_drawer, t_light, t_something2 = T("have"), T("something"), T("drawer"), T("light"), T("something", 2)
t_for1, t_then, t_didnt2, t_just, t_alright, t_ill2, t_for_you, t_you_e = (
    T("for"), T("then"), T("didn't", 2), T("just"), T("alright"), T("i'll", 2), T("for", 2), TE("you", 7))
t_whatever, t_longest, t_week2 = T("whatever's"), T("longest"), T("week", 2)

TICK = t_there_e + 0.15                     # the glass gives
steps = [(TICK, 0.07), (t_thats, 0.15), (t_its1, 0.23), (t_every1 + 0.3, 0.32), (t_it_goes, 0.41),
         (t_you_have, 0.49), (t_something1 + 0.3, 0.56), (t_drawer, 0.62), (t_light, 0.68), (t_something2 + 0.3, 0.75),
         (t_for1, 0.8), (t_then, 0.84), (T("didn't", 2), 0.88), (t_just, 0.91), (t_alright, 0.93), (t_for_you, 0.95),
         (t_whatever, 0.97), (t_longest, 0.985), (t_week2, 1.0)]
crack = Track([(0, 0.0, 0)] + [(ts, g, 0.35 if k else 0.12) for k, (ts, g) in enumerate(steps)])
sfx = [(TICK, "tick", 0.5), (TICK + 0.04, "crackle", 0.3)] + [(ts, "crackle", 0.18 + 0.1 * (k % 2)) for k, (ts, g) in enumerate(steps[1:])]

pose_track = Track([
    (0, KNOCK, 0),
    (TICK + 0.05, BACK, 0.18),                    # snatches his hand back
    (t_dont + 0.3, FROZEN, 0.8),
    (t_thats - 0.3, LEAN, 1.0),                   # leans in to look at it
    (t_its1 - 0.2, YOURS, 0.6),
    (t_so - 0.3, CAREFUL, 0.8),
    (t_you_have - 0.5, TO_YOU, 1.0),
    (t_something1 - 0.2, HOME, 0.6),
    (t_drawer - 0.2, DRAWER, 0.5),
    (t_something2 - 0.2, SAID, 0.6),
    (t_for1 - 0.2, WEEK, 0.6),
    (T("you", 5) - 0.2, FLAT, 0.8),               # "You didn't fix it."
    (t_alright - 0.4, SITLOOK, 1.4),              # sits down in front of it
    (t_for_you - 0.2, SITYOU, 0.8),
    (t_you_e + 0.3, SITLOOK, 1.4),
    (t_whatever + 0.2, SITYOU, 2.0),
])
x_track = Track([(0, 0.0, 0), (t_you_have - 0.5, -20.0, 1.2), (t_alright - 0.4, 0.0, 1.0)])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (TICK + 0.05, (468, 890, 1.52), 0.5),                     # a small jolt back
    (t_thats - 0.3, (480, 860, 1.5), 1.0),
    (t_thats + 0.8, (485, 850, 1.62), t_careful_e - t_thats),   # slow push while he looks at it
    (t_you_have - 0.5, (490, 930, 1.22), 1.6),                # mid: he talks to you
    (t_something1, (490, 910, 1.36), t_then - t_something1),
    (T("you", 5) - 0.3, (475, 860, 1.55), 1.2),               # "You didn't fix it."
    (t_alright - 0.4, (480, 1120, 1.3), 1.6),                 # down with him, sitting
    (t_for_you + 0.6, (470, 1080, 1.48), t_week2 - t_for_you),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (TICK, mood_vec("unease"), 0.3),
    (t_its1, mood_vec("uncanny"), 1.0),
    (t_you_have, mood_vec("drifting"), 1.4),
    (t_something2, mood_vec("melancholy"), 1.4),
    (T("you", 5), mood_vec("unease"), 1.0),
    (t_alright, mood_vec("warm"), 1.6),
    (t_whatever, mood_vec("uncanny"), 1.4),
])

DAY = dict(top=(184, 196, 210), bot=(230, 233, 238), clouds=0.6, cloud_v=5.0, sun=0.1, sun_y=0.36, sun_r=30)
sky = Track([
    (0, SKY(**DAY, drone=0.3), 0),
    (TICK, SKY(**DAY, drone=0.12), 0.3),                      # the room goes quiet when the glass gives
    (t_you_have, SKY(**DAY, drone=0.28), 2.0),
    (t_alright, SKY(**DAY, drone=0.18), 2.0),
    (t_whatever, SKY(**DAY, drone=0.08), 2.0),
])
class Env:
    def at(self, t):
        d = dict(sky.at(t))
        d.update(crack=crack.at(t))
        return d
env_track = Env()

CRACK = dict(origin=(752, 1002), heading=2.62, length=880, seed=11, branches=6)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=26, sfx=sfx, crack=CRACK)
N.main("nigel_bane_ep027_crack.mp4")
