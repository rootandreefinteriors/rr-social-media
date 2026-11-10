"""Day 36 — "Empty room" (posts as `… IIIII I vacating`). Mouse arc 1/4. C: "Stay here. Watch the room for me. Tell me if
anything moves." — he's pointing round the room as he says it. "Something lives in here. It only comes out when I'm
gone." He walks out of frame. T: the empty room — a mouse comes out from the corner by the wall, crosses the floor,
rears up to sniff; his voice from off-screen, "...Anything?" — it freezes; his footsteps come back and it darts away
a beat before he steps in. R (the turn): "It was out, wasn't it. I can tell by your face." — you saw what he never
has. ENDING (flat fact): "Every other room in your home is empty right now. Probably." Featured sound: tiny claws.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, smooth, KNOCK, OPEN)

N.setup()
T, TE = N.T, N.TE

ROOM = P(OPEN, look=(0.0, 0.0), swing=0.0)                         # "Watch the room for me."
POINT = P(relb=(548, 1040), rhand=(620, 1000), finger=1.0, look=(0.5, 0.2), tilt=0.06, swing=0.0)
HUSH = P(look=(-0.3, 0.3), tilt=-0.06, eyescale=1.08, swing=0.0)
GO = P(look=(0.8, 0.0), tilt=0.0)                                  # walking off to the right
BACK = P(look=(0.0, 0.05), tilt=0.0, eyescale=1.08)
FACE = P(BACK, eyescale=1.14, tilt=0.04)
NEVER = P(look=(-0.5, 0.45), tilt=-0.08)                           # looks over at the corner it comes from
LAST = P(look=(0.0, 0.02), tilt=0.02, eyescale=1.04)

t_stay, t_tell, t_something, t_im_going, t_minute_e, t_anything = (
    T("stay"), T("tell"), T("something"), T("going"), TE("minute"), T("anything", 2))
t_it_was, t_never, t_knows2, t_every, t_end = T("was"), T("never"), T("knows", 2), T("every"), TE("probably")

OUT0, OUT1 = t_im_going, t_minute_e + 0.6          # walks out of frame (right)
M0 = t_minute_e + 1.2                               # the mouse comes out
BACK0 = t_anything + 5.2                            # his footsteps come back
pose_track = Track([
    (0, KNOCK, 0),
    (t_stay - 0.3, ROOM, 0.5),
    (t_tell - 0.2, POINT, 0.5),
    (t_something - 0.3, HUSH, 0.8),
    (OUT0, GO, 0.6),
    (BACK0 + 0.9, BACK, 1.0),
    (t_it_was - 0.2, FACE, 0.6),
    (t_never - 0.2, NEVER, 1.0),
    (t_every - 0.3, LAST, 1.2),
])
x_track = Track([(0, 0.0, 0), (OUT0, 980.0, OUT1 - OUT0), (BACK0, 0.0, 1.6)])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_stay, (520, 940, 1.2), 1.2),
    (t_something, (500, 910, 1.4), 1.6),
    (OUT0, (470, 1150, 1.15), 1.4),                  # the empty room, low, its floor
    (M0 + 0.4, (360, 1270, 1.55), 4.0),              # creep in on the mouse, down on the floor
    (BACK0, (480, 1000, 1.1), 1.4),
    (t_it_was, (470, 880, 1.55), 1.2),
    (t_never, (470, 870, 1.62), t_every - t_never),
    (t_every - 0.2, (468, 850, 1.85), t_end - t_every + 0.8),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_stay, mood_vec("curious"), 0.5),
    (t_something, mood_vec("uncanny"), 0.8),
    (BACK0, mood_vec("unease"), 0.6),
    (t_it_was, mood_vec("uncanny"), 1.0),
    (t_never, mood_vec("lonely"), 1.4),
    (t_every, mood_vec("uncanny"), 1.4),
])

DAY = dict(top=(184, 200, 222), bot=(236, 236, 236), clouds=0.5, cloud_v=4.0, sun=0.3, sun_y=0.4, sun_r=30)
sky = Track([(0, SKY(**DAY, drone=0.28), 0), (OUT1, SKY(**DAY, drone=0.12), 1.0), (t_it_was, SKY(**DAY, drone=0.24), 1.5)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

# the mouse: out of the corner by the wall, across the floor, up on its hind legs; freezes at his voice; then the
# sound of him coming back — and it's gone a beat before he's in
mx = Track([(0, -150.0, 0), (M0, -150.0, 0), (M0 + 0.1, 300.0, 1.6), (M0 + 3.4, 470.0, 1.3), (BACK0 - 0.1, -250.0, 0.7)])
mrun = Track([(0, 0.0, 0), (M0, 1.0, 0.1), (M0 + 1.6, 0.0, 0.2), (M0 + 3.4, 1.0, 0.1), (M0 + 4.7, 0.0, 0.2),
              (BACK0 - 0.1, 1.0, 0.05), (BACK0 + 0.6, 0.0, 0.1)])
mrear = Track([(0, 0.0, 0), (M0 + 1.9, 1.0, 0.4), (t_anything - 0.05, 1.0, 0), (M0 + 3.2, 0.0, 0.3), (M0 + 5.0, 0.7, 0.4),
               (BACK0 - 0.3, 0.0, 0.15)])
FREEZE = (t_anything - 0.05, t_anything + 1.3)
def mouse(cr, t, pose, env):
    if t < M0 or t > BACK0 + 0.8:
        return
    x = mx.at(t)
    face = 1 if t < BACK0 - 0.1 else -1
    frozen = FREEZE[0] <= t <= FREEZE[1]
    sniff = 0.0 if frozen else (1.0 if mrear.at(t) > 0.3 else 0.3)
    N.draw_mouse(cr, x, N.FLOOR_Y + 1, t if not frozen else FREEZE[0], face=face, scale=2.4,
                 run=mrun.at(t), rear=mrear.at(t), sniff=sniff)

def chair(cr, t, pose, env):
    N.draw_chair(cr, 860, scale=1.1, tag=True, tag_swing=0.0)

pan = lambda x: max(-1, min(1, (x - 480) / 540)) * 0.5
sfx = [(M0 + 0.1, "scritch", 0.32, pan(0)), (M0 + 0.8, "scritch", 0.3, pan(200)), (M0 + 3.4, "scritch", 0.28, pan(420)),
       (BACK0 - 0.1, "scritch", 0.4, pan(300)), (BACK0 + 0.3, "scritch", 0.3, pan(60))]
N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=35, draw_hook=mouse, under_hook=chair, sfx=sfx,
            caption_avoid=[(M0, BACK0 + 0.8, lambda t: (mx.at(t) - 220, N.FLOOR_Y - 200, mx.at(t) + 220, N.FLOOR_Y + 30))])
N.main("nigel_bane_ep036_empty_room.mp4")
