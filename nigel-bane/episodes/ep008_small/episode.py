"""Day 8 — "Small". He measures the window: four hands, same as yesterday, so it's him.
The whole sky fits through a tiny hole; so does the world through your eyes. Small is where big comes in.
Hook: he doesn't know how to sleep; the room hums. (-> Day 9: sleep / dreams)
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, THINK, ONE, CHEST, PRESENT, STAND, POINT_UP)

N.setup()
T, TE = N.T, N.TE

MEASURE = P(relb=(560, 975), rhand=(625, 880), look=(0.75, -0.75), tilt=0.12, swing=0.0)
def MEAS(dx): return P(MEASURE, rhand=(625 + dx, 880 - dx * 0.15), relb=(560 + dx * 0.4, 975))
TINY = P(lelb=(415, 1090), lhand=(440, 1040), relb=(490, 1090), rhand=(468, 1040), look=(0.5, -0.4), swing=0.0)
WLOOK = P(head=(468, 766), tilt=0.13, look=(0.85, -0.75))
SOFT = P(PRESENT, tilt=0.06, look=(0.0, 0.1))
LIE = P(head=(300, 1306), neck=(466, 1442), hip=(735, 1452),
        lelb=(560, 1456), lhand=(650, 1462), relb=(585, 1440), rhand=(680, 1432),
        lknee=(850, 1455), lfoot=(962, 1470), rknee=(845, 1446), rfoot=(958, 1462),
        tilt=-math.pi / 2, look=(1.0, 0.0), swing=0.0)

t_okay, t_with, t_four, t_it1 = T("okay"), T("with"), T("four"), T("it")
t_so1, t_its_me, t_heres, t_this = T("so"), T("it's", 2), T("here's"), T("this")
t_and1, t_every1, t_every2, t_entire = T("and"), T("every"), T("every", 2), T("entire")
t_squeezed, t_your, t_two, t_and2 = T("squeezed"), T("your"), T("two"), T("and", 2)
t_so2, t_maybe2, t_ilike, t_im = T("so", 2), T("maybe", 2), T("like", 2), T("i'm")
t_tried, t_dont, t_lay, t_humming = T("tried"), T("don't"), T("lay"), T("humming")

pose_track = Track([
    (0, KNOCK, 0),
    (t_okay - 0.1, STAND, 0.5),
    (t_with - 0.3, MEAS(0), 0.6),
    (t_four - 0.05, MEAS(0), 0.1),          # four little hand-steps across the window
    (t_four + 0.25, MEAS(22), 0.14),
    (t_four + 0.5, MEAS(44), 0.14),
    (t_four + 0.75, MEAS(66), 0.14),
    (t_it1 - 0.1, ONE, 0.5),
    (t_so1 - 0.1, POINT_UP, 0.5),
    (t_its_me - 0.1, CHEST, 0.4),
    (t_heres - 0.1, THINK, 0.6),
    (t_this - 0.1, TINY, 0.5),
    (t_and1 - 0.1, WLOOK, 0.7),
    (t_squeezed - 0.1, MEAS(30), 0.6),       # covers the window with his hand
    (t_your - 0.2, P(look=(0.0, 0.0), tilt=0.0, eyescale=1.05), 0.6),
    (t_so2 - 0.1, P(STAND, look=(0.0, -0.2)), 0.8),
    (t_ilike - 0.2, SOFT, 0.8),
    (t_tried - 0.3, LIE, 1.2),               # lies down on the floor
    (t_lay, P(LIE, look=(1.0, 0.25)), 1.0),
])

x_track = Track([
    (0, 0.0, 0),
    (t_okay, 110.0, 1.4),
    (t_heres, 30.0, 2.0),
    (t_ilike - 0.3, 0.0, 1.0),
])

EYE_Y = 769   # world y of his eyes (standing)
cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_okay - 0.2, (650, 760, 1.08), 2.0),
    (t_heres, (540, 960, 1.0), 2.0),
    (t_and1 - 0.2, (700, 680, 1.12), 1.6),
    (t_your - 0.3, (480, EYE_Y, 3.0), 1.8),         # into his eyes
    (t_two, (548, EYE_Y - 6, 4.6), 2.5),            # one HD eye fills the frame
    (t_so2 - 0.9, (540, 1000, 0.6), 2.3),           # pull way out: he is tiny
    (t_ilike - 0.2, (520, 960, 1.0), 2.0),
    (t_tried - 0.2, (560, 1290, 1.22), 2.2),        # down on the floor with him
])
follow_track = Track([(0, 0.0, 0), (t_okay, 0.0, 0.1)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_its_me, mood_vec("drifting"), 1.0),
    (t_this, mood_vec("curious"), 0.8),
    (t_and1, mood_vec("awe"), 1.2),
    (t_your, mood_vec("drifting"), 1.0),
    (t_two, mood_vec("awe"), 2.0),
    (t_so2, mood_vec("warm"), 1.6),
    (t_tried, mood_vec("lonely"), 1.6),
    (t_humming - 0.4, mood_vec("uncanny"), 1.2),
])

PALE = dict(top=(206, 210, 222), bot=(236, 236, 236), clouds=0.5, cloud_v=4.0)
env_track = Track([
    (0, SKY(**PALE, win_scale=0.86), 0),                           # still "smaller" from yesterday...
    (t_heres, SKY(**PALE, win_scale=1.0), 6.0),                    # ...quietly back to normal
    # the whole sky squeezes through: a time-lapse in the window
    (t_and1, SKY(top=(240, 190, 170), bot=(200, 215, 235), clouds=0.9, cloud_v=140, drone=0.55), 0.6),
    (t_every1, SKY(top=(110, 180, 245), bot=(220, 235, 250), clouds=0.8, cloud_v=160, sun=0.8, sun_y=0.3,
                   drone=0.6), 0.6),
    (t_every2, SKY(top=(255, 140, 90), bot=(255, 210, 150), clouds=0.5, cloud_v=160, sun=0.9, sun_y=0.55,
                   drone=0.65), 0.6),
    (t_entire, SKY(top=(255, 170, 90), bot=(255, 225, 160), clouds=0.2, cloud_v=60, sun=1.0, sun_r=62, sun_y=0.45,
                   beam=0.6, drone=0.75), 0.7),
    (t_squeezed, SKY(top=(10, 12, 32), bot=(32, 30, 64), clouds=0.0, cloud_v=0, stars=1.0, drone=0.6), 0.8),
    (t_your, SKY(**PALE, drone=0.5), 1.5),
    (t_so2, SKY(top=(250, 225, 180), bot=(255, 240, 215), clouds=0.3, cloud_v=3, sun=0.5, sun_r=30, sun_y=0.35,
                beam=0.35, sparkle=0.5, drone=0.65, shimmer=0.5), 2.0),
    (t_tried, SKY(top=(26, 28, 54), bot=(54, 48, 88), clouds=0.0, cloud_v=0, stars=0.45, drone=0.8), 2.4),
    (t_lay, SKY(top=(20, 22, 46), bot=(46, 40, 80), clouds=0.0, cloud_v=0, stars=0.5, drone=1.6), 3.0),  # the hum
])

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=8, tally_new=[])
N.main("nigel_bain_ep008_small.mp4")
