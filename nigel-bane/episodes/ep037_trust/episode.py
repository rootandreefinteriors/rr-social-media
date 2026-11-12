"""Day 37 — "Trust" (posts as `… IIIII II inching`). Mouse arc 2/4. IDEA: before anything comes near you, it has to
decide you're safe. C: "Hold out your hand. Flat. Don't move it." — he's already kneeling, hand going down flat on the
floor. T (said early, so the viewer knows what to watch): "If I move, it goes. If I don't... it might come." The mouse,
by the tagged chair, edges toward his hand in short dashes; when his hand shakes it backs off; it comes again; on the
last line it puts a paw on his finger. R (someone else): "Someone you love did it once. The first time they leaned on
you, they'd already decided. You didn't see them decide." Unsettling: whispered "Don't. Don't go." Implied lift: the
paw on his finger. ENDING (action): the touch, with "Someone decided you were safe, once. You never found out which
day." said over it. Featured sound: tiny claws.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, STAND)

N.setup()
T, TE = N.T, N.TE
F = N.FLOOR_Y

KNEEL = P(STAND, hip=(400, 1380), neck=(540, 1170), head=(640, 1060),
          lknee=(520, 1466), lfoot=(330, 1476), rknee=(540, 1460), rfoot=(350, F),
          lelb=(500, 1310), lhand=(540, 1452), relb=(620, 1300), rhand=(650, 1400),
          tilt=0.3, look=(0.6, 0.7), swing=0.0)
FLAT = P(KNEEL, relb=(650, 1330), rhand=(700, 1466), look=(0.7, 0.8))            # hand flat on the floor
FLAT_M = P(FLAT, look=(0.95, 0.75))                                              # at the mouse
FLAT_CAM = P(FLAT, look=(-0.15, 0.15), tilt=0.22, eyescale=1.05)                 # at us
FLAT_HOLD = P(FLAT_M, eyescale=1.14)
HX = 754                      # where his fingertips end on the floor (world)
SC = 2.4                      # mouse scale; its nose is 36*SC in front of its body x
CHAIR_X = 900

t_hold, t_mouse, t_if, t_come_e, t_its, t_most = T("hold"), T("mouse"), T("if"), TE("come", 1), T("deciding"), T("most")
t_someone, t_my, t_dont2, t_go_e, t_coming, t_someone2, t_once2, t_end = (
    T("someone"), T("my"), T("don't", 3), TE("go"), T("coming"), T("someone", 2), T("once", 2), TE("day"))

pose_track = Track([
    (0, KNOCK, 0),
    (t_hold - 0.3, KNEEL, 1.2),
    (t_hold + 1.0, FLAT, 1.0),
    (t_mouse - 0.2, FLAT_M, 0.6),
    (t_someone - 0.3, FLAT_CAM, 0.9),
    (t_my - 0.4, FLAT_M, 0.6),
    (t_coming - 0.3, FLAT_HOLD, 0.6),
])
def tremble(t, p):
    if t_my - 0.1 < t < t_dont2 + 0.6:        # his hand shakes
        a = 3.2 * math.sin(t * 47) + 2.0 * math.sin(t * 29)
        x, y = p["rhand"]; p["rhand"] = (x + a, y - abs(a) * 0.4)
    return p
x_track = Track([(0, 0.0, 0)])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_hold, (560, 1180, 1.25), 1.4),                   # down to the floor with him
    (t_mouse - 0.1, (760, 1300, 1.25), 0),              # CUT: his hand, the gap, the mouse by the chair
    (t_mouse, (770, 1320, 1.35), t_its - t_mouse),
    (t_its - 0.1, (900, 1400, 2.4), 0),                 # CUT: close on the mouse, deciding
    (t_its, (895, 1405, 2.55), t_someone - t_its),
    (t_someone - 0.1, (600, 1120, 1.9), 0),             # CUT: him, whispering to us
    (t_someone, (605, 1110, 2.05), t_my - t_someone),
    (t_my - 0.1, (770, 1330, 1.4), 0),                  # CUT: hand and mouse; the hand shakes, it backs off
    (t_my, (775, 1340, 1.5), t_coming - t_my),
    (t_coming - 0.1, (760, 1405, 2.5), 0),              # CUT: close on fingers and mouse
    (t_coming, (755, 1410, 2.8), t_end - t_coming + 1.5),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_hold, mood_vec("drifting"), 1.0),
    (t_mouse, mood_vec("curious"), 0.8),
    (t_someone, mood_vec("lonely"), 1.4),
    (t_my, mood_vec("unease"), 0.6),
    (t_coming, mood_vec("awe"), 1.0),
    (t_once2, mood_vec("warm"), 1.2),
])

DAY = dict(top=(176, 196, 222), bot=(236, 234, 228), clouds=0.4, cloud_v=3.0, sun=0.4, sun_y=0.45, sun_r=28)
sky = Track([(0, SKY(**DAY, drone=0.2), 0), (t_hold + 1.0, SKY(**DAY, drone=0.1), 1.5),
             (t_coming, SKY(**DAY, drone=0.04), 1.5)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

# the mouse: by the chair; edges toward his hand in short dashes; backs off when the hand shakes; comes again; touches
TOUCH_X = HX + 36 * SC - 4
D1, D2, BACK, D3, D4, D5 = t_come_e + 0.8, t_someone - 0.4, t_my + 0.9, t_go_e + 0.8, t_coming + 0.2, t_once2 - 0.4
mx = Track([(0, 1010.0, 0), (D1, 950.0, 0.7), (D2, 905.0, 0.6), (BACK, 975.0, 0.35), (D3, 925.0, 0.9),
            (D4, 880.0, 0.7), (D5, TOUCH_X, 0.9)])
mrun = Track([(0, 0.0, 0), (D1, 1.0, 0.08), (D1 + 0.7, 0.0, 0.15), (D2, 1.0, 0.08), (D2 + 0.6, 0.0, 0.15),
              (BACK, 1.0, 0.05), (BACK + 0.4, 0.0, 0.1), (D3, 0.8, 0.1), (D3 + 0.9, 0.0, 0.2),
              (D4, 0.8, 0.1), (D4 + 0.7, 0.0, 0.2), (D5, 0.5, 0.1), (D5 + 0.9, 0.0, 0.3)])
mrear = Track([(0, 0.0, 0), (t_mouse + 0.5, 0.55, 0.4), (D1 - 0.2, 0.0, 0.2), (D1 + 1.2, 0.5, 0.4), (D2 - 0.2, 0.0, 0.2),
               (D2 + 1.0, 0.45, 0.4), (BACK - 0.1, 0.0, 0.1), (BACK + 1.0, 0.6, 0.3), (D3 - 0.2, 0.0, 0.2),
               (D4 - 0.1, 0.0, 0.1), (D5 + 1.0, 0.22, 0.5)])
def hand(cr, pose):
    """his hand laid flat on the floor: a palm and four fingers pointing toward the mouse, and a thumb"""
    if t_hold > 0 and pose["rhand"][1] < F - 30:
        return
    x, y = pose["rhand"]
    for k, (dx, dy) in enumerate([(54, -1), (57, -9), (52, -18), (43, -26)]):
        N.path(cr, N.sketch_pts([(x + 4, y - 2 - k * 5), (x + dx, y + dy + 6)], amp=0.4, sid=300 + k, step=6))
        N.stroke_ink(cr, 4.0)
    N.path(cr, N.sketch_pts([(x + 2, y - 14), (x + 16, y - 40)], amp=0.4, sid=310, step=6)); N.stroke_ink(cr, 4.0)

def mouse(cr, t, pose, env):
    hand(cr, pose)
    face = 1 if BACK - 0.05 < t < BACK + 0.45 else -1     # turns tail for a second when it backs off
    N.draw_mouse(cr, mx.at(t), F + 1, t, face=face, scale=SC, run=mrun.at(t), rear=mrear.at(t),
                 sniff=1.0 if mrun.at(t) < 0.2 else 0.3)

def chair(cr, t, pose, env):
    N.draw_chair(cr, CHAIR_X, scale=1.1, tag=True, tag_swing=0.0)

pan = lambda x: max(-1, min(1, (x - 480) / 540)) * 0.5
sfx = [(D1, "scritch", 0.28, pan(980)), (D2, "scritch", 0.26, pan(930)), (BACK, "scritch", 0.34, pan(950)),
       (D3, "scritch", 0.26, pan(950)), (D4, "scritch", 0.24, pan(900)), (D5, "scritch", 0.22, pan(820))]
N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=36, draw_hook=mouse, under_hook=chair, pose_hook=tremble, sfx=sfx,
            caption_avoid=[(0, 99, lambda t: (min(HX - 40, mx.at(t) - 120), F - 160, mx.at(t) + 200, F + 30))])
N.BLINKS = [b for b in N.BLINKS if not (t_coming - 0.3 < b < t_end)]
N.main("nigel_bane_ep037_trust.mp4")
