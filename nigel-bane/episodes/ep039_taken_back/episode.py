"""Day 39 — DREAD "Taken back" (posts as `… IIIII IIII outlasting`). Mouse arc 4/4: the mouse leaves, and takes the tagged
chair with it. IDEA: almost everything you own will outlast you and go to someone you'll never meet. Flat grey light,
no hum. C: "Hold on to something near you." He turns to the window; behind him, in the same shot, the chair slides a
little across the floor. He turns back: "It moved. The chair. While I wasn't looking." From then on the viewer watches
the chair whenever he looks away (T): it only moves when he isn't looking at it. "Again." The mouse comes out from
under it and keeps pace beside it. R (caught): "Whatever you're holding right now will probably belong to someone else
one day." He looks at it — it stops — "I could stop it. ...I'm not going to." He looks back at us and the chair and
the mouse slide out past the edge of the room. "It was never mine. I just sat in it." ENDING (flat fact, whispered):
"Some of what's in your room right now will belong to someone you'll never meet." The room is empty again.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, CHEST, STAND)

N.setup()
T, TE = N.T, N.TE
F = N.FLOOR_Y

HOLD = P(CHEST, look=(0.0, 0.05))                                   # holding on to himself
WIN_LOOK = P(HOLD, look=(0.75, -0.75), tilt=0.14)                   # turned to the window
AT_CHAIR = P(HOLD, look=(0.95, 0.35), tilt=0.06, eyescale=1.1)      # looking at the chair
TO_US = P(STAND, look=(0.0, 0.0), swing=0.0, eyescale=1.04)
TO_US2 = P(TO_US, lelb=(400, 1080), lhand=(370, 1180), tilt=-0.04)
EMPTY = P(STAND, look=(0.85, 0.5), tilt=0.05, swing=0.0)            # at the empty floor
LAST = P(STAND, look=(0.0, 0.02), swing=0.0, eyescale=1.08)

t_hold, t_you_e, t_it, t_while, t_somebody, t_exactly_e, t_again, t_mouse, t_going, t_whatever = (
    T("hold"), TE("you", 1), T("it", 1), T("while"), T("somebody"), TE("exactly"), T("again"), T("mouse"),
    T("going", 1), T("whatever"))
t_i_could, t_im, t_to_e, t_never2, t_some, t_end = (T("could"), T("i'm"), TE("to", 3), T("was", 2), T("some"),
                                                     TE("meet"))
print("to#3 end", t_to_e, "was#2", t_never2)

pose_track = Track([
    (0, KNOCK, 0),
    (t_hold - 0.3, HOLD, 0.6),
    (t_you_e + 0.3, WIN_LOOK, 0.6),          # turns to the window...
    (t_it - 0.6, AT_CHAIR, 0.35),            # ...and back: it moved
    (t_somebody - 0.2, HOLD, 0.8),
    (t_exactly_e + 0.4, WIN_LOOK, 0.6),      # to the window again
    (t_again - 0.5, AT_CHAIR, 0.35),
    (t_whatever - 0.3, TO_US, 0.8),          # to us: it moves while he talks
    (t_whatever + 4.0, TO_US2, 1.2),
    (t_i_could - 0.3, AT_CHAIR, 0.6),        # he looks: it stops
    (t_im + 0.8, TO_US, 0.6),                # looks away again: it goes
    (t_never2 - 0.4, EMPTY, 0.8),
    (t_some - 0.4, LAST, 0.9),
])
x_track = Track([(0, 0.0, 0)])

# the chair only moves while he isn't looking at it
C0, C1, C2, C3 = 690.0, 750.0, 815.0, 880.0
M_EXIT0 = t_im + 1.0
cx = Track([(0, C0, 0), (t_you_e + 0.8, C1, 1.6), (t_exactly_e + 0.9, C2, 1.8), (t_whatever + 0.6, C3, 8.5),
            (M_EXIT0, 1520.0, t_never2 - 0.4 - M_EXIT0)])
WIDE = (640, 1090, 1.15)
cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_hold, WIDE, 1.2),                                 # the whole room: him, the chair
    (t_while - 0.1, (520, 920, 1.6), 0),                 # CUT: him
    (t_while, (520, 915, 1.7), t_exactly_e - t_while),
    (t_exactly_e + 0.2, WIDE, 0),                        # CUT: wide; he turns away, it moves
    (t_mouse - 0.1, (820, 1350, 1.9), 0),                # CUT: the mouse coming out from under it
    (t_whatever - 0.1, WIDE, 0),                         # CUT: wide; he talks to us, it creeps behind
    (t_whatever, (650, 1095, 1.18), t_i_could - t_whatever),
    (t_i_could - 0.1, (650, 1050, 1.35), 0),               # CUT: medium, he looks at it
    (t_im + 0.7, WIDE, 0),                               # CUT: wide; it goes
    (t_never2 - 0.2, (520, 930, 1.55), 0),               # CUT: him and the empty floor
    (t_some - 0.2, (470, 880, 1.75), 0),                 # CUT: close, to us
    (t_some, (468, 870, 1.85), t_end - t_some + 2),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_hold, mood_vec("unease"), 0.8),
    (t_it, mood_vec("uncanny"), 0.4),
    (t_mouse, mood_vec("lonely"), 1.2),
    (t_whatever, mood_vec("unease"), 1.2),
    (t_im, mood_vec("melancholy"), 1.0),
    (t_never2, mood_vec("void"), 1.2),
    (t_some, mood_vec("uncanny"), 1.2),
])

GREY = dict(top=(176, 178, 184), bot=(208, 208, 210), clouds=0.85, cloud_v=1.0, sun=0.0, sun_y=0.3, sun_r=24)
sky = Track([(0, SKY(**GREY, drone=0.12), 0), (t_hold, SKY(**GREY, drone=0.0), 1.0)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

# the mouse: comes out from under the seat on "The mouse lives under it" and keeps pace beside the chair, on the far side
M_OUT = t_mouse - 0.4
def mouse_x(t):
    return cx.at(t) + 150
mrun = lambda t: 1.0 if (abs(cx.at(t + 0.05) - cx.at(t)) > 0.4 or M_OUT < t < M_OUT + 0.7) else 0.0
def chair(cr, t, pose, env):
    N.draw_chair(cr, cx.at(t), scale=1.1, tag=True, tag_swing=0.6 * math.sin(t * 2.0) * min(1, abs(cx.at(t + 0.05) - cx.at(t))))
def mouse(cr, t, pose, env):
    if t < M_OUT:
        return
    x = cx.at(t) + min(1.0, (t - M_OUT) / 0.7) * 150
    N.draw_mouse(cr, x, F + 1, t, face=1, scale=2.2, run=mrun(t), rear=0.0 if mrun(t) else 0.4,
                 sniff=0.4 if mrun(t) else 1.0)

pan = lambda x: max(-1, min(1, (x - 480) / 540)) * 0.5
sfx = [(M_OUT, "scritch", 0.3, pan(950))] + [(t_whatever + 0.6 + k * 2.1, "scritch", 0.16, pan(1100)) for k in range(4)] + \
      [(M_EXIT0 + k * 0.9, "scritch", 0.22, pan(1150)) for k in range(4)]
N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=38, under_hook=chair, draw_hook=mouse, sfx=sfx,
            caption_avoid=[(0, 99, lambda t: (cx.at(t) - 110, F - 430, cx.at(t) + 260, F + 30))])
N.main("nigel_bane_ep039_taken_back.mp4")
