"""Day 10 — "Drawn". He dreamed someone was drawing him: head, then eyes, then they stopped.
Maybe morning is someone redrawing you from memory. "I'd rather be redrawn than erased."
Prop: the bird passes slowly, close ("it looked right at me") -> lands D12.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, THINK, OPEN, CHEST, PRESENT, STAND)

N.setup()
T, TE = N.T, N.TE

WLOOK = P(head=(468, 766), tilt=0.13, look=(0.85, -0.75))
FACECAM = P(look=(0.0, 0.0), tilt=0.0, swing=0.0)
UNSURE = P(look=(0.0, 0.15), tilt=-0.06, lelb=(400, 1080), lhand=(420, 1150), relb=(500, 1080), rhand=(480, 1150), swing=0.0)
EYESPOINT = P(relb=(585, 965), rhand=(598, 845), finger=1.0, look=(0.0, 0.0), swing=0.0)
LOOKDOWN = P(OPEN, look=(0.0, 0.8), tilt=-0.12)
SOFT = P(PRESENT, tilt=0.06, look=(0.0, 0.1))

t_its, t_i_think, t_dreamed, t_line = T("it's"), T("think"), T("dreamed"), T("line")
t_my, t_then1, t_and1, t_like = T("my"), T("then"), T("and"), T("like")
t_woke, t_im, t_two, t_all = T("woke"), T("i'm"), T("two"), T("all", 2)
t_but, t_somebody, t_and2, t_maybe = T("but"), T("somebody"), T("and", 3), T("maybe")
t_thats, t_id, t_thing, t_it2, t_i3 = T("that's", 2), T("i'd"), T("thing"), T("it"), T("think", 2)

pose_track = Track([
    (0, KNOCK, 0),
    (t_its - 0.1, UNSURE, 0.7),
    (t_dreamed - 0.1, FACECAM, 0.8),
    (t_woke - 0.1, UNSURE, 0.6),
    (t_im - 0.1, CHEST, 0.5),
    (t_two - 0.1, EYESPOINT, 0.5),
    (t_all - 0.1, LOOKDOWN, 0.6),
    (t_but - 0.1, THINK, 0.7),
    (t_somebody - 0.1, PRESENT, 0.7),
    (t_and2 - 0.1, STAND, 0.8),
    (t_thats - 0.1, SOFT, 0.7),
    (t_id - 0.1, CHEST, 0.6),
    (t_thing - 0.3, WLOOK, 0.9),
    (t_i3 - 0.2, P(WLOOK, look=(0.3, -0.25), tilt=0.06), 1.0),
])

# being drawn: 1 = whole, 0 = nothing. head 0-.3, eyes .3-.45, body .5-1
reveal = Track([
    (0, 1.0, 0),
    (t_dreamed + 0.1, 0.0, 1.0),          # he un-draws
    (t_my, 0.3, 1.3),                     # "my head first"
    (t_then1, 0.47, 1.1),                 # "then my eyes" ... and then they stopped
    (t_woke, 1.0, 1.5),                   # "I woke up and checked": the body draws down
])
def hook(t, p):
    p["reveal"] = reveal.at(t)
    return p

x_track = Track([
    (0, 0.0, 0),
    (t_but - 0.2, 100.0, 2.0),
    (t_and2 - 0.2, -90.0, 4.5),           # slow walk; yesterday's versions of him trail behind
    (t_thing - 0.4, 150.0, 1.6),
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_its - 0.2, (540, 960, 1.0), 2.0),
    (t_dreamed, (470, 830, 1.5), 2.0),       # close on where his head is drawn
    (t_woke + 0.2, (470, 1000, 0.92), 1.6),  # back out as the body draws down
    (t_but, (540, 960, 1.0), 1.6),
    (t_thing - 0.3, (720, 650, 1.18), 2.0),  # the window, for the bird
])
follow_track = Track([(0, 0.0, 0), (t_but, 0.2, 1.5), (t_thing - 0.3, 0.0, 1.0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_dreamed, mood_vec("drifting"), 1.2),
    (t_and1, mood_vec("uncanny"), 1.0),
    (t_woke, mood_vec("curious"), 1.0),
    (t_im, mood_vec("warm"), 1.0),
    (t_but, mood_vec("drifting"), 1.2),
    (t_and2, mood_vec("melancholy"), 1.4),
    (t_thats, mood_vec("warm"), 1.2),
    (t_thing, mood_vec("unease"), 1.0),
])

DREAM = dict(top=(14, 16, 40), bot=(44, 38, 86), clouds=0.0, cloud_v=0.0, stars=0.7)
env_track = Track([
    (0, SKY(top=(120, 130, 175), bot=(225, 185, 175), clouds=0.3, cloud_v=3), 0),
    (t_dreamed, SKY(**DREAM, drone=0.75, shimmer=0.4), 1.2),
    (t_woke, SKY(top=(240, 196, 160), bot=(205, 216, 236), clouds=0.4, cloud_v=6, drone=0.45), 2.0),   # morning
    (t_but, SKY(top=(225, 205, 215), bot=(250, 238, 222), clouds=0.5, cloud_v=6, sun=0.5, sun_r=26, sun_y=0.6,
                drone=0.5), 2.5),
    (t_and2, SKY(top=(200, 205, 222), bot=(238, 236, 232), clouds=0.5, cloud_v=4, echo=0.85, drone=0.45), 1.5),
    (t_thats, SKY(top=(205, 215, 235), bot=(250, 238, 214), clouds=0.4, cloud_v=5, echo=0.0, drone=0.5), 1.5),
    (t_thing - 0.3, SKY(top=(200, 210, 230), bot=(240, 238, 232), clouds=0.3, cloud_v=2, drone=0.2), 1.2),
])

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=10, tally_new=[], pose_hook=hook,
            birds=[dict(t=T("looked") - 1.0, dur=3.6, x0=1.15, x1=-0.2, y=0.4, size=38)])   # slow, close: "it looked right at me"
N.main("nigel_bane_ep010_drawn.mp4")
