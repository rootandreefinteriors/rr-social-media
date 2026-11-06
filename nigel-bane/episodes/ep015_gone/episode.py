"""Day 15 — "Gone". He never named the bird — "if you don't name something, you can't call it back."
It leaves on camera mid-thought. Signature visual: a faint ghost outline of the bird lingers on the empty ledge
on "it was a shape", then fades. Ends sitting under the window: "In case looking was what kept it here."
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, ONE, CHEST, PRESENT, STAND, THINK, SIT_UP)

N.setup()
T, TE = N.T, N.TE

WLOOK = P(head=(468, 766), tilt=0.13, look=(0.85, -0.75), swing=0.0)
CAMLOOK = P(look=(0.0, 0.0), tilt=0.0, swing=0.0)
REACH = P(WLOOK, relb=(570, 960), rhand=(650, 860), tilt=0.18, look=(0.95, -0.9))
STILL = P(WLOOK, lelb=(412, 1100), lhand=(402, 1215), relb=(500, 1100), rhand=(512, 1215))

t_still, t_keep, t_like, t_never = T("still"), T("keep"), T("like"), T("never")
t_proud, t_names, t_but, t_if = T("proud"), T("names"), T("but"), T("if")
t_oh1, t_oh2, t_going, t_gone = T("oh"), T("oh", 2), T("going"), T("gone")
t_dont, t_shape1, t_shape2, t_im = T("don't", 2), T("shape"), T("shape", 2), T("i'm")

LEAVE = t_going - 0.15

pose_track = Track([
    (0, KNOCK, 0),
    (t_still - 0.1, WLOOK, 0.5),
    (t_keep - 0.1, CAMLOOK, 0.3),                # keeps checking: window, you, window...
    (t_keep + 0.6, WLOOK, 0.3),
    (t_like - 0.1, CAMLOOK, 0.3),
    (t_like + 1.2, WLOOK, 0.3),
    (t_never - 0.1, CHEST, 0.6),
    (t_names - 0.2, ONE, 0.5),
    (t_but - 0.1, THINK, 0.6),
    (t_if - 0.1, PRESENT, 0.6),
    (t_oh1 - 0.2, WLOOK, 0.3),
    (t_oh2 - 0.1, REACH, 0.6),                   # reaching for it
    (t_gone - 0.2, STILL, 1.6),
    (t_dont, P(STILL, look=(0.2, 0.2), tilt=-0.1), 1.0),
    (t_im - 0.3, SIT_UP, 1.4),                   # sits down under the window to keep looking
])

x_track = Track([(0, 0.0, 0), (t_still - 0.2, 150.0, 1.6), (t_never, 40.0, 2.0), (t_oh1 - 0.4, 160.0, 1.0)])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_still - 0.2, (720, 650, 1.15), 2.0),
    (t_never, (540, 960, 1.0), 1.6),
    (t_oh1 - 0.3, (760, 600, 1.3), 1.0),
    (t_gone + 0.5, (840, 470, 1.8), 2.5),        # the empty ledge
    (t_im - 0.3, (700, 900, 0.95), 4.0),         # slow pull back: him sitting, the empty window
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_never, mood_vec("warm"), 1.2),
    (t_but, mood_vec("drifting"), 1.0),
    (t_oh1, mood_vec("awe"), 0.4),
    (t_oh2, mood_vec("unease"), 0.6),
    (t_gone, mood_vec("lonely"), 1.6),
    (t_im, mood_vec("melancholy"), 2.0),
])

DAY = dict(top=(200, 210, 232), bot=(244, 238, 228), clouds=0.4, cloud_v=4.0, perch_x=0.62)
def sky(perch=1.0, tilt=0.0, hop=0.0, **kw):
    d = dict(DAY); d.update(kw)
    return SKY(perch=perch, perch_tilt=tilt, perch_hop=hop, **d)
env_track = Track([
    (0, sky(drone=0.3), 0),
    (t_keep, sky(tilt=0.2, drone=0.35), 0.6),
    (t_but, sky(tilt=-0.15, drone=0.4), 0.8),
    (t_oh1 - 0.15, sky(hop=1.0, tilt=0.3, drone=0.3), 0.15),          # it hops
    (t_oh1 + 0.2, sky(hop=0.0, tilt=0.3, drone=0.3), 0.2),
    (LEAVE, sky(perch=0.0, drone=0.2), 0.12),                          # ...and it's off
    (t_gone, sky(perch=0.0, top=(180, 188, 210), bot=(232, 230, 230), drone=0.0), 1.5),
    (t_shape1 - 0.3, sky(perch=0.22, top=(180, 188, 210), bot=(232, 230, 230), drone=0.0), 1.0),  # its ghost on the ledge
    (t_shape2 + 0.6, sky(perch=0.0, top=(160, 150, 185), bot=(225, 200, 200), drone=0.2), 2.0),
    (t_im, sky(perch=0.0, top=(110, 100, 150), bot=(215, 170, 160), drone=0.3), 3.0),   # dusk
])

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=15, tally_new=[],
            birds=[dict(t=LEAVE, dur=1.8, x0=0.62, x1=-0.25, y=0.62, size=40)])    # takes off and is gone
N.main("nigel_bane_ep015_gone.mp4")
