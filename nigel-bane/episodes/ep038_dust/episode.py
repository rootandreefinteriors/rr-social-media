"""Day 38 — "Dust" (posts as `… IIIII III shedding`). Mouse arc 2/4. IDEA: some of the dust in your room used to be you.
C: "Hold out your hand. Slowly. Into the light." — he's already going down on his knees, reaching into a sunbeam on
the floor; dust turns in it. T (a visible yes/no): a mouse sits in the far end of the sunbeam eating the dust; the
beam is sliding off his hand; will the mouse reach his fingertip before the light leaves it? It touches his fingertip
in the held silence after "Before it goes", just as the light slides off his hand. R (caught): "Your hand's out right
now. In your room. Some of it is landing on you, too." Unsettling line: "Some of it is skin. A little, every day,
without asking." Implied lift: the touch. ENDING (action): the light leaves his hand on "Some of that was you."
Featured sound: tiny claws. Whispered stretch: "Come on. Before it goes."
"""
import math
import os
import random
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import cairo
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, STAND)

N.setup()
T, TE = N.T, N.TE
F = N.FLOOR_Y

KNEEL = P(STAND, hip=(400, 1380), neck=(560, 1160), head=(660, 1050),
          lknee=(520, 1466), lfoot=(330, 1476), rknee=(540, 1460), rfoot=(350, F),
          lelb=(520, 1300), lhand=(560, 1450), relb=(640, 1250), rhand=(660, 1330),
          tilt=0.35, look=(0.6, 0.7), swing=0.0)
REACH = P(KNEEL, relb=(660, 1285), rhand=(706, 1398), finger=1.0, look=(0.55, 0.85))      # into the light
REACH_M = P(REACH, look=(0.9, 0.6))                                                       # at the mouse
REACH_CAM = P(REACH, look=(-0.2, 0.1), tilt=0.25, eyescale=1.06)                          # at us
REACH_HOLD = P(REACH, look=(0.75, 0.8), eyescale=1.12)
REACH_LAST = P(REACH, look=(0.5, 0.9), eyescale=1.08, tilt=0.38)
FX, FY = 724, 1424            # his fingertip (world)

t_hold, t_slowly, t_into, t_see, t_dont, t_mouse = T("hold"), T("slowly"), T("into"), T("see"), T("don't"), T("mouse")
t_eat1, t_dust1, t_dust2, t_your, t_light2, t_coming, t_come, t_goes_e, t_some3, t_end = (
    T("eating"), T("dust"), T("dust", 2), T("your", 2), T("light's"), T("coming"), T("come"), TE("goes"),
    T("some", 3), TE("you", 2))

TOUCH = t_goes_e + 1.0
pose_track = Track([
    (0, KNOCK, 0),
    (t_hold - 0.3, KNEEL, 1.4),
    (t_into - 0.2, REACH, 1.6),          # slowly, into the light
    (t_mouse - 0.3, REACH_M, 0.7),
    (t_dust2 + 0.6, REACH_CAM, 1.0),
    (t_light2 - 0.3, REACH_M, 0.7),
    (t_come - 0.2, REACH_HOLD, 0.6),
    (t_some3 - 0.4, REACH_LAST, 0.8),
])
x_track = Track([(0, 0.0, 0)])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_hold, (540, 1150, 1.3), 1.6),                    # follow him down to the floor
    (t_see - 0.1, (720, 1430, 2.3), 0),                 # CUT: his hand in the light, dust turning
    (t_see, (715, 1435, 2.45), t_dont - t_see),
    (t_mouse - 0.6, (820, 1380, 2.1), 1.6),             # pan along the beam to the mouse
    (t_eat1 - 0.1, (900, 1420, 2.7), 0),                # CUT: close on the mouse eating
    (t_eat1, (905, 1425, 2.9), t_dust2 + 0.5 - t_eat1),
    (t_dust2 + 0.5, (600, 1140, 1.8), 0),               # CUT: him, kneeling, close
    (t_your - 0.1, (620, 1120, 2.1), 0),                # CUT: closer as he looks at us
    (t_your, (625, 1110, 2.25), t_light2 - t_your),
    (t_light2 - 0.1, (700, 1200, 1.0), 0),             # CUT: wide on the floor: the beam, his hand, the mouse
    (t_light2, (720, 1230, 1.08), t_come - t_light2),
    (t_come - 0.1, (770, 1415, 2.6), 0),                # CUT: close on fingertip and mouse
    (t_come, (765, 1418, 2.85), t_end - t_come + 1.0),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_into, mood_vec("awe"), 1.2),
    (t_mouse, mood_vec("curious"), 0.8),
    (t_dust1 + 1.0, mood_vec("uncanny"), 1.5),
    (t_your, mood_vec("unease"), 1.0),
    (t_light2, mood_vec("unease"), 0.5),
    (TOUCH - 0.2, mood_vec("warm"), 0.8),
    (t_some3, mood_vec("uncanny"), 1.2),
])

SUN = dict(top=(150, 186, 226), bot=(242, 226, 196), clouds=0.3, cloud_v=3.0, sun=0.9, sun_y=0.62, sun_r=34)
sky = Track([(0, SKY(**SUN, drone=0.18), 0), (t_come, SKY(**SUN, drone=0.05), 1.0), (TOUCH, SKY(**SUN, drone=0.14), 2.0)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

# the sunbeam: from the window down to a patch on the floor that slides right, off his hand
L_track = Track([(0, 600.0, 0), (t_light2 - 0.9, 690.0, TOUCH - t_light2 + 0.9), (TOUCH + 0.4, 800.0, t_end - TOUCH)])
BW = 440
WX, WY, WW, WH = N.WIN
def beam_poly(t):
    L = L_track.at(t)
    return [(WX + 8, WY + WH), (WX + WW - 4, WY + WH), (L + BW, F + 6), (L, F + 6)]
def beam(cr, t, pose, env):
    pts = beam_poly(t)
    g = cairo.LinearGradient(0, WY + WH, 0, F)
    g.add_color_stop_rgba(0, 1.0, 0.88, 0.55, 0.10)
    g.add_color_stop_rgba(1, 1.0, 0.84, 0.50, 0.30)
    cr.move_to(*pts[0])
    for p in pts[1:]:
        cr.line_to(*p)
    cr.close_path(); cr.set_source(g); cr.fill()
    L = L_track.at(t)                                         # warm patch on the floor
    cr.save(); cr.translate(L + BW / 2, F + 4); cr.scale(1, 0.09)
    pg = cairo.RadialGradient(0, 0, 0, 0, 0, BW * 0.62)
    pg.add_color_stop_rgba(0, 1, 0.86, 0.5, 0.45); pg.add_color_stop_rgba(1, 1, 0.86, 0.5, 0)
    cr.set_source(pg); cr.arc(0, 0, BW * 0.62, 0, 2 * math.pi); cr.fill(); cr.restore()

MOTES = [(random.Random(i * 13).random(), random.Random(i * 7 + 3).random(), random.Random(i * 5 + 9).random())
         for i in range(90)]
def inside(pts, x, y):
    (x0, y0), (x1, _), (x2, y2), (x3, _) = pts
    if y < y0 or y > y2:
        return False
    u = (y - y0) / (y2 - y0)
    return x0 + (x3 - x0) * u <= x <= x1 + (x2 - x1) * u

# the mouse: in the far end of the light, eating; then, as the light slides, it edges toward his fingertip
MX0 = 960.0
MXT = FX + 46 * 2.2 - 48          # body x at which its nose meets his fingertip
mx = Track([(0, MX0, 0), (t_light2 + 0.6, MX0, 0), (t_light2 + 0.7, 930.0, 0.9), (t_coming + 0.4, 900.0, 0.6),
            (t_come + 0.5, 860.0, 0.8), (TOUCH - 0.7, MXT, 0.7)])
mrun = Track([(0, 0.0, 0), (t_light2 + 0.7, 1.0, 0.1), (t_light2 + 1.6, 0.0, 0.2), (t_coming + 0.4, 1.0, 0.1),
              (t_coming + 1.0, 0.0, 0.2), (t_come + 0.5, 0.8, 0.1), (t_come + 1.3, 0.0, 0.2),
              (TOUCH - 0.7, 0.6, 0.1), (TOUCH, 0.0, 0.2)])
mrear = Track([(0, 0.55, 0), (t_dust2 + 0.3, 0.55, 0), (t_light2 + 0.5, 0.0, 0.3), (t_come + 1.4, 0.3, 0.4),
               (TOUCH - 0.75, 0.0, 0.2), (TOUCH - 0.15, 0.62, 0.35), (t_end, 0.62, 0)])
def mouse(cr, t, pose, env):
    eating = t < t_light2 + 0.5
    sniff = 1.0 if (eating or t > TOUCH - 0.3) else 0.4
    N.draw_mouse(cr, mx.at(t), F + 1, t, face=-1, scale=2.2, run=mrun.at(t), rear=mrear.at(t), sniff=sniff)
    pts = beam_poly(t)                                     # dust turning in the light, in front of everything
    for i, (a, b, c) in enumerate(MOTES):
        y = WY + WH + 30 + ((b + t * (0.006 + 0.01 * c)) % 1.0) * (F - WY - WH - 40)
        u = (y - (WY + WH)) / (F - WY - WH)
        x0 = pts[0][0] + (pts[3][0] - pts[0][0]) * u; x1 = pts[1][0] + (pts[2][0] - pts[1][0]) * u
        x = x0 + (x1 - x0) * ((a + 0.04 * math.sin(t * 0.35 + i)) % 1.0)
        if not inside(pts, x, y):
            continue
        tw = 0.5 + 0.5 * math.sin(t * (1.2 + c) + i * 2.1)
        cr.set_source_rgba(0.93, 0.72, 0.32, 0.35 + 0.6 * tw)
        cr.arc(x, y, 2.0 + 3.0 * c, 0, 2 * math.pi); cr.fill()

pan = lambda x: max(-1, min(1, (x - 480) / 540)) * 0.5
sfx = [(t_light2 + 0.7, "scritch", 0.26, pan(950)), (t_coming + 0.4, "scritch", 0.24, pan(900)),
       (t_come + 0.5, "scritch", 0.24, pan(870)), (TOUCH - 0.7, "scritch", 0.3, pan(840))]
N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=37, draw_hook=mouse, under_hook=beam, sfx=sfx,
            caption_avoid=[(0, 99, lambda t: (mx.at(t) - 130, F - 140, mx.at(t) + 200, F + 30)),
                           (t_into, 99, lambda t: (FX - 120, FY - 120, FX + 60, F + 20))])
N.BLINKS = [b for b in N.BLINKS if not (t_come - 0.3 < b < t_end)]   # he doesn't blink while it comes
N.main("nigel_bane_ep038_dust.mp4")
