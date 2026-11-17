"""Day 42 — "Arms out" (posts as `… IIIII IIIII II bracing`). Room arc 3/4, the tightest point. IDEA: a small room
feels safe, and that's how it keeps you. The room is as narrow as the window: he stands in the middle with his arms
out and his palms flat on both walls, the low ceiling resting on the window frame. C (the test): "Stand up. Arms out.
Go on, try it. ...Can you touch both walls?" — real silence while you try. T: "I'm going to push them back." He braces
and pushes, trembling, the camera creeping in; will they give? They don't. R (the test, then one scene): you could
walk most of your morning with your eyes shut. He stops pushing and just leans into the wall, comfortable: "It's cosy,
actually." Unsettling line: "I stopped pushing because it was nice." ENDING (instruction for after): "Tonight, stand
in the middle of your room with your arms out, and your eyes shut. Notice how sure you are where the walls are."
One continuous shot (user, 2026-11-17).
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

OFF = 390.0                       # he stands under the window (body centre x 840)
LW, RW = 650.0, 1030.0            # the two walls: just wider than the window
CEIL = 203.0

t_stand, t_arms, t_walls, t_can, t_push, t_mm, t_moving = T("stand"), T("arms"), T("walls"), T("can", 2), T("push"), T("mm"), T("moving")
t_could, t_bed, t_corner, t_small, t_cosy, t_stopped, t_nice = T("could"), T("bed"), T("corner"), T("small"), T("cosy"), T("stopped"), T("nice")
t_tonight, t_notice, t_end = T("tonight"), T("notice"), TE("are", 2)

ARMS = P(STAND, lelb=(355, 1000), lhand=(LW - OFF + 4, 990), relb=(545, 1000), rhand=(RW - OFF - 4, 990),
         look=(0.0, 0.05), swing=0.0, finger=0.0)
ARMS_CAM = P(ARMS, look=(0.0, 0.0), eyescale=1.06)
ARMS_DOWN = P(ARMS, look=(0.0, 0.5))
PUSH = P(ARMS, hip=(450, 1265), neck=(452, 965), head=(450, 798), lknee=(405, 1370), rknee=(495, 1370),
         lelb=(362, 1008), relb=(538, 1008), look=(0.0, -0.1), eyescale=1.14, tilt=0.0)
PANT = P(ARMS, look=(0.1, 0.15), tilt=-0.05)
UP = P(ARMS, look=(0.35, -0.6), tilt=0.06)
LEAN = P(ARMS, head=(418, 790), neck=(440, 950), hip=(452, 1240), tilt=-0.28, look=(-0.2, 0.2), shut=0.45,
         lelb=(362, 998), relb=(545, 1010))
LEAN_CAM = P(LEAN, look=(0.15, 0.05), shut=0.0, tilt=-0.18)
LAST = P(ARMS, look=(0.0, 0.0), eyescale=1.06, tilt=0.0)

pose_track = Track([
    (0, KNOCK, 0),
    (t_arms - 0.3, ARMS, 1.2),                   # arms out: palms land flat on both walls
    (t_walls - 0.6, ARMS_CAM, 0.6),
    (t_can - 0.4, ARMS_DOWN, 0.5),
    (t_push - 0.3, ARMS, 0.5),
    (t_mm - 0.4, PUSH, 1.0),                     # braces and pushes
    (t_moving - 0.4, PANT, 1.0),
    (t_could - 0.3, ARMS_CAM, 1.0),
    (t_bed, UP, 1.2),
    (t_small - 0.3, ARMS_CAM, 1.0),
    (t_cosy - 1.2, LEAN, 1.6),                   # stops pushing and leans into it
    (t_stopped - 0.3, LEAN_CAM, 1.0),
    (t_tonight - 0.4, LAST, 1.4),
])
def strain(t, p):
    """the push: the whole body trembles while the hands stay flat on the walls"""
    if t_mm - 0.2 < t < t_moving:
        a = min(1.0, (t - t_mm + 0.2) / 0.6) * min(1.0, (t_moving - t) / 0.4)
        dx = a * (4.0 * math.sin(t * 37) + 2.5 * math.sin(t * 23))
        for k in ("head", "neck", "hip", "lelb", "relb", "lknee", "rknee"):
            p[k] = (p[k][0] + dx, p[k][1] + a * 1.5 * math.sin(t * 41))
        p["eyescale"] = p.get("eyescale", 1.0) + 0.02 * a * math.sin(t * 29)
    return p
x_track = Track([(0, OFF, 0)])

cam_track = Track([                                        # ONE continuous shot
    (0, (OFF + 470, 880, 1.6), 0),
    (t_arms - 0.2, (840, 1000, 1.05), 2.4),                # ease out: both walls at his fingertips
    (t_push, (840, 1010, 1.3), t_moving - t_push + 0.5),   # creep in through the push
    (t_could - 0.3, (840, 990, 1.05), 3.0),                # back out
    (t_cosy - 1.4, (820, 900, 1.6), 3.2),                  # in on his face, leaning
    (t_tonight - 0.6, (800, 980, 0.86), 4.0),              # pull out: the whole narrow room, the tally on the side wall
    (t_notice, (800, 985, 0.84), t_end - t_notice + 0.6),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_arms, mood_vec("drifting"), 1.0),
    (t_push, mood_vec("unease"), 1.0),
    (t_moving, mood_vec("lonely"), 1.2),
    (t_could, mood_vec("melancholy"), 1.5),
    (t_cosy - 1.0, mood_vec("warm"), 2.0),
    (t_stopped, mood_vec("uncanny"), 1.5),
    (t_tonight, mood_vec("drifting"), 1.5),
])

EVE = dict(top=(60, 70, 120), bot=(150, 120, 150), clouds=0.3, cloud_v=1.0, stars=0.15, sun=0.0, sun_y=0.3, sun_r=24)
sky = Track([(0, SKY(**EVE, drone=0.18), 0), (t_walls + 0.4, SKY(**EVE, drone=0.0), 0.6),
             (t_can, SKY(**EVE, drone=0.16), 1.0), (t_mm, SKY(**EVE, drone=0.3), 2.0),
             (t_moving, SKY(**EVE, drone=0.12), 1.5), (t_cosy, SKY(**EVE, drone=0.06), 2.0)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

CRACKS = [(720, 1.4, 11), (860, 1.6, 12), (940, 1.3, 13)]
def room(cr, t, pose, env):
    """the low ceiling and the two side walls at his fingertips (shaded planes, seen edge-on); the tally stays on the
    left side wall"""
    cr.rectangle(-2000, -2000, 5000, CEIL + 2000)
    cr.set_source_rgba(0.93, 0.93, 0.925, 1.0); cr.fill()
    for k in range(3):
        yy = CEIL - 14 - k * 13
        N.path(cr, N.sketch_pts([(-2000, yy), (3000, yy)], amp=1.2, sid=200 + k, step=40)); N.stroke_ink(cr, 1.2, alpha=0.18)
    N.path(cr, N.sketch_pts([(-2000, CEIL), (3000, CEIL)], amp=1.4, sid=210, step=40)); N.stroke_ink(cr, 4.0, alpha=0.85)
    for x0, s, sid in CRACKS:
        pts, px, py = [], x0, CEIL
        for j in range(7):
            pts.append((px, py)); px += (14 if j % 2 == 0 else -9) * s; py -= 9 * s
        N.path(cr, pts); N.stroke_ink(cr, 2.4, alpha=0.8)
    for x0, x1, sid in ((-2000, LW, 300), (RW, 3000, 320)):
        cr.rectangle(x0, CEIL, x1 - x0, F - CEIL); cr.set_source_rgba(0.9, 0.9, 0.895, 1.0); cr.fill()
        for k in range(26):
            xx = (LW - 40 - k * 34) if x1 == LW else (RW + 40 + k * 34)
            N.path(cr, N.sketch_pts([(xx, CEIL + 30), (xx + (-50 if x1 == LW else 50), F - 20)], amp=0.9, sid=sid + k, step=30))
            N.stroke_ink(cr, 1.3, alpha=0.14)
    for x, sid in ((LW, 340), (RW, 341)):
        N.path(cr, N.sketch_pts([(x, CEIL), (x, F)], amp=1.3, sid=sid, step=30)); N.stroke_ink(cr, 4.2, alpha=0.9)
    N.draw_tally(cr, t)                                    # the marks, on the left side wall

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=41, under_hook=room, pose_hook=strain)
N.BLINKS = [b for b in N.BLINKS if not (t_mm - 0.3 < b < t_moving)]
N.main("nigel_bane_ep042_arms_out.mp4")
