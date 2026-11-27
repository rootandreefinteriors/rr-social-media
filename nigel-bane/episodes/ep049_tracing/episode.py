"""Day 49 — "tracing" (posts as `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIII tracing`).
Body arc 1/4 (prop: an outline of his hand, traced on OUR side of the glass). Owner-approved script, 2026-11-27.
THE LINE: "You've never once been anywhere it wasn't." (your body)
C: "Hold your hand up. Up to mine." — he raises his palm and lays it flat on the glass, beside his face.
T (love): a line draws itself round his hand on our side of the glass, finger by finger; he asks you to stay with your
hand against his until it's done ("Stay there till it's done. Please." ... "Nearly... don't go..."). It closes on
"...There." Bridge: the outline is the only shape he's ever been -> yours has been everywhere you've been.
Unsettling: the line drawing itself on our side; "You stayed." (he seems to know). Lift (implied): "It's still yours."
His palm is pinned to the glass (engine/hand_outline.py): it keeps its place and size on screen while the camera
moves, because it's ON the glass. One continuous shot.
"""
import math
import os
import random
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
import hand_outline as HO
from nigel import (P, SKY, Track, mood_vec, KNOCK, STAND, smooth)

N.setup()
T, TE = N.T, N.TE

t_hold, t_up2, t_mine, t_there1 = T("hold"), T("up", 2), TE("mine"), T("there", 2)
t_something, t_glass, t_stay, t_please = T("something's"), TE("glass"), T("stay"), TE("please")
t_goes, t_finger, t_slowly, t_like, t_never1, t_outline = T("goes"), TE("finger"), T("slowly"), T("like"), T("never"), T("outline")
t_thats, t_every, t_yours1, t_against, t_born, t_worst = T("that's"), T("every", 2), T("yours"), T("against"), TE("born"), T("worst")
t_youve, t_nearly, t_dont, t_go, t_there_end = T("you've"), T("nearly"), T("don't"), TE("go"), T("there", 8)
t_you_stayed, t_put, t_its, t_end = T("you", 3), T("put"), T("it's", 2), TE("yours", 3)

TRACE0 = t_something + 0.4          # the line starts drawing
TRACE1 = t_there_end + 0.15         # ...and closes on "There."
LIFT = t_put - 0.2                  # he takes his hand off the glass

# how far round the hand the line has got: steady and slow, a held breath round "Nearly... don't go...", closed on "There."
trace = Track([(0, 0.0, 0), (TRACE0, 0.0, 0), (TRACE0 + 0.01, 0.30, t_finger - TRACE0),        # round the thumb and first fingers
               (t_finger + 0.6, 0.55, t_never1 - t_finger),                                     # every finger, slowly
               (t_never1 + 0.6, 0.80, t_youve - t_never1),
               (t_youve + 0.6, 0.93, t_nearly - t_youve),
               (t_nearly + 0.2, 0.985, t_go - t_nearly),                                         # nearly...
               (t_go + 0.3, 1.0, TRACE1 - t_go - 0.3)])

pin_w = Track([(0, 0.0, 0), (t_up2 - 0.2, 1.0, t_there1 - t_up2 + 0.2), (LIFT, 0.0, 0.9)])

# ------------------------------------------------------------------ poses
CAM_X, CAM_Y = HO.CENTER
RAISE = P(STAND, relb=HO.HAND["relb"], rhand=HO.HAND["rhand"], palm=HO.HAND["palm"], spread=1.0, look=(0.25, 0.1), eyescale=1.04, swing=0.0)
WATCH = P(RAISE, look=(0.55, 0.45), tilt=0.06, eyescale=1.08)                  # watching the line go round
TO_US = P(RAISE, look=(0.0, 0.0), tilt=0.02)
SOFT = P(RAISE, look=(0.05, 0.08), tilt=-0.04, eyescale=1.02)
CHEEK = P(RAISE, head=(470, 785), look=(0.35, 0.2), tilt=0.12, eyescale=1.0, shut=0.22)  # leans toward his hand, fond
HOLD = P(RAISE, look=(0.5, 0.35), eyescale=1.16, tilt=0.03)                     # nearly... don't move
GLAD = P(RAISE, look=(0.0, 0.0), eyescale=1.06, tilt=-0.03)
DOWN = P(STAND, look=(0.0, 0.0), eyescale=1.04, tilt=0.02, swing=0.0)
LAST = P(STAND, look=(0.12, 0.1), eyescale=1.02, tilt=0.05, swing=0.0)

pose_track = Track([
    (0, KNOCK, 0),
    (t_hold - 0.2, P(STAND, look=(0.0, 0.0), swing=0.0), 0.6),
    (t_up2 - 0.3, RAISE, 1.2),                     # "Up to mine." — the palm comes up flat onto the glass
    (t_something - 0.2, WATCH, 0.8),               # "Something's drawing round my hand."
    (t_glass - 0.2, TO_US, 0.8),                   # "On your side of the glass."
    (t_please + 0.2, WATCH, 1.0),
    (t_like - 0.2, SOFT, 1.0),
    (t_thats - 0.2, CHEEK, 1.4),                   # "That's the only shape I've ever been."
    (t_yours1 - 0.3, TO_US, 1.0),                  # "Yours is right there, against mine."
    (t_born + 0.2, SOFT, 1.2),
    (t_youve - 0.3, TO_US, 1.0),
    (t_nearly - 0.4, HOLD, 0.8),                   # nearly... don't go...
    (t_there_end - 0.1, WATCH, 0.4),
    (t_you_stayed - 0.3, GLAD, 0.8),               # "...You stayed."
    (LIFT, DOWN, 0.9),                             # "You can put yours down now." — he takes his hand off
    (t_its - 0.2, LAST, 1.0),                      # "It's still yours." — a glance at the outline
])

def hook(t, p):
    p = HO.pin(p, t, cam_track, pin_w.at(t))
    w = smooth((t - TRACE0) / 0.6) * (1 - smooth((t - TRACE1 - 0.2) / 0.5))
    lw = (1 - smooth((t - t_glass) / 0.4)) + smooth((t - t_please - 0.2) / 0.8) * (1 - smooth((t - t_like + 0.2) / 0.8))
    lw += smooth((t - t_nearly + 0.4) / 0.6) * (1 - smooth((t - TRACE1) / 0.4))
    lw = min(1.0, lw) * w
    if lw > 0.001:                                  # his eyes follow the pen tip round his hand
        cx, cy, z = cam_track.at(t)
        tx, ty = HO.tip(max(0.001, trace.at(t)))
        hx, hy = (p["head"][0] - cx) * z + 540, (p["head"][1] - cy) * z + 960
        lx = max(-1, min(1, (tx - hx) / 320)); ly = max(-1, min(1, (ty - hy) / 320))
        p["look"] = (p["look"][0] + (lx - p["look"][0]) * lw, p["look"][1] + (ly - p["look"][1]) * lw)
    return p

x_track = Track([(0, 0.0, 0)])

CAM = HO.CAM
cam_track = Track([                                          # ONE continuous shot
    (0, (470, 880, 1.6), 0),
    (t_hold - 0.2, CAM, 2.4),                                # settle on his face and the raised hand
    (t_please + 0.3, (505, 930, 1.7), 6.0),                  # slow push in while it goes round the fingers
    (t_thats - 0.4, (535, 975, 1.35), 5.0),                  # ease back: the whole outline, him leaning to it
    (t_yours1 - 0.2, (515, 945, 1.55), 4.0),                 # "Yours is right there, against mine."
    (t_worst - 0.6, (525, 990, 1.3), 4.5),                   # out a little
    (t_nearly - 0.6, (508, 935, 1.72), t_there_end - t_nearly + 0.4),   # creeps in through "Nearly... don't go..."
    (LIFT + 0.4, (530, 960, 1.4), 3.0),                      # a little out: the empty outline on the glass
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_something, mood_vec("awe"), 1.0),
    (t_stay, mood_vec("unease"), 0.8),
    (t_goes, mood_vec("drifting"), 1.5),
    (t_thats, mood_vec("warm"), 1.5),
    (t_yours1, mood_vec("awe"), 1.5),
    (t_worst, mood_vec("melancholy"), 1.5),
    (t_nearly, mood_vec("unease"), 1.0),
    (t_you_stayed, mood_vec("warm"), 1.2),
    (t_its, mood_vec("drifting"), 1.0),
])

DAY = dict(top=(168, 196, 228), bot=(226, 232, 238), clouds=0.55, cloud_v=6.0, sun=0.35, sun_y=0.35, sun_r=26)
sky = Track([(0, SKY(**DAY, drone=0.16), 0), (TRACE0, SKY(**DAY, drone=0.06), 2.0),
             (t_nearly, SKY(**DAY, drone=0.0), 1.0), (t_you_stayed, SKY(**DAY, drone=0.08), 2.0)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

def glass(cr, t, pose, env, to_screen):
    N._palm["pos"] = None                        # no greasy palm print: the traced line is the mark he leaves
    HO.draw(cr, progress=trace.at(t), t=t)

# the featured close sound: the soft drag of the line on the glass, in the quiet beats
sfx = [(TRACE0 + 0.2, "scratch", 0.07), (t_please + 0.5, "scratch", 0.09), (t_finger + 0.3, "scratch", 0.07),
       (t_nearly + 1.1, "scratch", 0.06), (t_go + 0.5, "scratch", 0.08), (t_there_end - 0.35, "scratch", 0.07)]

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track, tally_base=49, pose_hook=hook,
            glass_hook=glass, sfx=sfx, caption_avoid=[(TRACE0, 99, HO.caption_box(cam_track))])
N.BLINKS = [b for b in N.BLINKS if not (t_nearly - 0.3 < b < t_there_end + 0.3)]
N.main("nigel_bane_ep049_tracing.mp4")
