"""Day 29 — "Taped". Night. A strip of clear tape has been laid over the crack across the screen — on OUR side of the
glass, where he can't reach. C: "Hold still. Let me see." — he leans right in to the glass. T: one corner of the tape keeps
lifting in a draught; will it hold? Twice it peels up while he holds his breath; it settles; "...It's holding." IDEA
(you): you've been fixed by people you'll never thank — someone salted the steps, checked the brakes on your bus, stayed
up at three in the morning so a stranger wouldn't be alone. UNSETTLE: "On your side. I can't reach your side." and "They
did it while I was asleep." LIFT (implied): the tape holding; dawn coming up in the window. HOOK: "Somebody fixed
something for you today. You'll never find out what."
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, OPEN, PRESENT, CHEST)

N.setup()
T, TE = N.T, N.TE

LEAN = P(head=(462, 800), neck=(458, 965), look=(-0.35, 0.5), tilt=-0.12, eyescale=1.08, swing=0.0,
         relb=(540, 1090), rhand=(560, 1170))
TAPE = P(LEAN, look=(-0.4, 0.45), tilt=-0.1)
REACH = P(relb=(600, 1060), rhand=(640, 960), palm=0.75, look=(-0.2, 0.3), tilt=-0.05, swing=0.0)   # hand flat on his side
FREEZE = P(LEAN, look=(-0.4, 0.5), eyescale=1.14, tilt=-0.08, lelb=(395, 1080), lhand=(420, 1015))    # holding his breath
ASLEEP = P(look=(0.0, 0.05), tilt=0.05, swing=0.0)
LEFT = P(OPEN, look=(0.0, 0.0))
YOU = P(PRESENT, look=(0.0, 0.05))
NAMES = P(CHEST, look=(0.0, 0.1))
WATCH2 = P(FREEZE, head=(458, 790))
HOLDS = P(look=(-0.2, 0.3), tilt=0.04, eyescale=1.02, swing=0.0)
LAST = P(look=(0.0, 0.03), tilt=0.02, swing=0.0)

t_hold, t_someone1, t_on, t_i_cant, t_dont = T("hold"), T("someone"), T("on"), T("can't"), T("don't")
t_they1, t_left_e, t_that, t_someone2, t_names_e = T("they"), TE("left"), T("that"), T("someone", 2), TE("names")
t_its, t_somebody = T("it's"), T("somebody")

# the corner of the tape: twice it lifts in a draught while he holds his breath; then it holds
lift = Track([
    (0, 0.12, 0),
    (t_dont - 0.9, 0.55, 0.9), (t_dont + 0.6, 0.8, 1.2), (t_dont + 2.4, 0.3, 1.2), (t_they1 - 0.2, 0.15, 0.8),
    (t_names_e + 0.2, 0.6, 0.9), (t_names_e + 1.4, 0.92, 1.0), (t_its - 0.2, 0.18, 0.6), (t_its + 0.6, 0.06, 1.0),
])
def tape_lift(t):
    base = lift.at(t)
    return max(0.0, base + 0.05 * base * math.sin(t * 13) + 0.03 * base * math.sin(t * 29))

pose_track = Track([
    (0, KNOCK, 0),
    (t_hold - 0.3, LEAN, 0.6),                   # "Hold still. Let me see."
    (t_someone1, TAPE, 1.0),
    (t_on + 0.4, REACH, 0.8),                    # "On your side. I can't reach your side."
    (t_dont - 0.9, FREEZE, 0.5),                 # the corner lifts — "Don't."
    (t_they1 - 0.3, ASLEEP, 1.0),
    (t_left_e - 0.6, LEFT, 0.6),
    (t_that - 0.3, YOU, 0.8),
    (t_someone2 + 1.0, NAMES, 1.2),
    (t_names_e + 0.2, WATCH2, 0.6),              # it lifts again
    (t_its, HOLDS, 1.0),
    (t_somebody - 0.4, LAST, 1.2),
])
x_track = Track([(0, 0.0, 0), (t_they1 - 0.3, -30.0, 1.2), (t_names_e + 0.2, 0.0, 0.8)])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_hold - 0.3, (468, 870, 1.72), 0.8),                       # right up to the glass
    (t_someone1, (470, 880, 1.78), t_dont - t_someone1),
    (t_dont - 0.9, (468, 850, 1.92), 4.0),                       # held breath
    (t_they1 - 0.3, (480, 930, 1.3), 1.6),                       # back a step
    (t_that, (485, 910, 1.48), t_names_e - t_that),             # slow push
    (t_names_e + 0.2, (470, 860, 1.75), 1.4),
    (t_somebody - 0.4, (468, 840, 1.95), 5.0),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_someone1, mood_vec("uncanny"), 1.0),
    (t_dont - 0.9, mood_vec("unease"), 0.6),
    (t_they1, mood_vec("drifting"), 1.2),
    (t_that, mood_vec("warm"), 1.6),
    (t_someone2 + 2, mood_vec("lonely"), 1.6),
    (t_its, mood_vec("warm"), 1.0),
    (t_somebody, mood_vec("uncanny"), 1.6),
])

NIGHT = dict(top=(18, 22, 58), bot=(48, 44, 96), clouds=0.0, cloud_v=0.0, stars=0.75, sun=0.95, sun_y=0.34, sun_r=26)
DAWN = dict(top=(96, 110, 168), bot=(238, 196, 170), clouds=0.25, cloud_v=2.0, stars=0.1, sun=0.6, sun_y=0.8, sun_r=30)
sky = Track([
    (0, SKY(**NIGHT, drone=0.3), 0),
    (t_dont - 0.9, SKY(**NIGHT, drone=0.05), 0.6),               # dead quiet while it lifts
    (t_they1, SKY(**NIGHT, drone=0.28), 1.5),
    (t_names_e, SKY(**NIGHT, drone=0.05), 0.6),
    (t_its, SKY(**DAWN, drone=0.25), t_somebody - t_its + 4),    # first light while it holds
])
class Env:
    def at(self, t):
        d = dict(sky.at(t))
        d.update(crack=1.0, tape=1.0, tape_lift=tape_lift(t))
        return d
env_track = Env()

CRACK = dict(origin=(752, 1002), heading=2.62, length=1000, seed=11, branches=6, tape_at=0.4, tape_len=380, tape_w=72)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=28, crack=CRACK)
N.main("nigel_bane_ep029_taped.mp4")
