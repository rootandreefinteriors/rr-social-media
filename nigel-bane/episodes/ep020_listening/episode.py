"""Day 20 — "Listening". (Bible beat: a faint tap at night, he isn't sure he heard it.) Night (window), normal room. Right after the
open: "Shh. Get down. Listen." — he drops flat on the floor. It's not the moth: she got the moth (wrapped in the web,
next to the fly). YOU: the phone that buzzes in your pocket when nothing's there, your name in the shower, a hand on
your shoulder in an empty room — "Your body wants to be reached so badly, it makes it up." "You've done this too. Lain
very still in the dark. Listening for proof." Real silence... then two faint taps from OUR side of the glass (the frame
shivers). He sits bolt upright, staring at us: "...There. That came from your side." Hook: "If I made that up, I'm
lonelier than I thought. If I didn't... it was you." (eyes go warm on "you": the implied lift.) D22: a clear knock.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, SIT_CAM, STAND)

N.setup()
T, TE = N.T, N.TE

LIE = P(head=(300, 1306), neck=(466, 1442), hip=(735, 1452),
        lelb=(560, 1456), lhand=(650, 1462), relb=(585, 1440), rhand=(680, 1432),
        lknee=(850, 1455), lfoot=(962, 1470), rknee=(845, 1446), rfoot=(958, 1462),
        tilt=-math.pi / 2, look=(1.0, 0.0), swing=0.0)
LIE_WEB = P(LIE, look=(0.9, 0.45))          # head frame: up and toward the window
LIE_CAM = P(LIE, look=(0.0, 0.0))
LIE_SHOULDER = P(LIE, look=(-0.5, 0.8))      # a glance down at his own shoulder
LIE_WIDE = P(LIE_CAM, eyescale=1.1)
DUCK = P(STAND, head=(440, 820), tilt=-0.1, look=(0.0, 0.3), swing=0.0)
SIT_SNAP = P(SIT_CAM, eyescale=1.14)
SIT_LEAN = P(SIT_CAM, head=(452, 992), eyescale=1.12, tilt=0.0)
SIT_LAST = P(SIT_LEAN, head=(456, 984), eyescale=1.16)

t_there_end, t_shh, t_listen = TE("there"), T("shh"), T("listen")
t_its, t_you1, t_shoulder = T("it's"), T("you"), T("shoulder")
t_your5, t_youve, t_so2, t_diff_end = T("your", 5), T("you've"), T("so", 2), TE("difference")
t_there3, t_that, t_if1, t_if2, t_you_last = T("there", 3), T("that"), T("if"), T("if", 2), T("you", 5)

TAP1 = t_diff_end + 1.35
TAP2 = TAP1 + 0.4

pose_track = Track([
    (0, KNOCK, 0),
    (t_shh - 0.15, DUCK, 0.4),
    (t_shh + 0.35, LIE, 1.0),                      # flat on the floor
    (t_its - 0.2, LIE_WEB, 0.8),
    (t_you1 - 0.1, LIE_CAM, 0.8),
    (t_shoulder - 0.3, LIE_SHOULDER, 0.5),         # ...a hand on your shoulder
    (t_shoulder + 0.9, LIE_CAM, 0.8),
    (t_youve - 0.1, LIE, 1.0),                     # staring up, listening
    (TAP1 + 0.05, LIE_WIDE, 0.15),
    (TAP2 + 0.25, SIT_SNAP, 0.45),                 # bolt upright, facing us
    (t_that - 0.1, SIT_LEAN, 1.2),
    (t_if2 - 0.1, SIT_LAST, 1.6),
])

x_track = Track([(0, 0.0, 0)])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_shh - 0.1, (430, 1260, 1.3), 2.4),          # down on the floor with him
    (t_its - 0.2, (650, 330, 2.0), 2.0),           # the moth, wrapped in the web
    (t_you1 - 0.2, (390, 1288, 1.4), 2.0),         # back to him, and stay
    (t_you1 + 2.0, (415, 1290, 1.78), t_diff_end - t_you1 - 2.0),   # one slow creep in while he talks and listens
    (TAP2 + 0.2, (450, 1000, 1.5), 0.8),           # he sits bolt upright
    (t_that, (448, 985, 2.3), 9.0),                # one long push into his eyes to the end
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_shh, mood_vec("unease"), 0.6),
    (t_its, mood_vec("melancholy"), 1.0),
    (t_you1, mood_vec("drifting"), 1.0),
    (t_shoulder - 0.2, mood_vec("uncanny"), 0.8),
    (t_your5, mood_vec("lonely"), 1.2),
    (t_youve, mood_vec("drifting"), 1.2),
    (t_so2, mood_vec("lonely"), 1.2),
    (TAP1, mood_vec("unease"), 0.2),
    (t_that, mood_vec("uncanny"), 1.0),
    (t_if1, mood_vec("lonely"), 1.2),
    (t_you_last - 0.3, mood_vec("warm"), 1.0),
])

NIGHT = dict(top=(18, 22, 58), bot=(48, 44, 96), clouds=0.0, cloud_v=0.0, stars=0.75, sun=0.95, sun_y=0.34, sun_r=26)
sky_track = Track([
    (0, SKY(**NIGHT, drone=0.35), 0),
    (t_listen, SKY(**NIGHT, drone=0.2), 0.8),
    (t_you1, SKY(**NIGHT, drone=0.35), 1.5),
    (t_shoulder - 0.2, SKY(**NIGHT, drone=0.5, shimmer=0.3), 1.0),
    (t_youve, SKY(**NIGHT, drone=0.3), 1.5),
    (t_diff_end, SKY(**NIGHT, drone=0.0), 0.6),    # dead quiet
    (TAP2 + 0.3, SKY(**NIGHT, drone=0.45), 1.5),
    (t_if2, SKY(**NIGHT, drone=0.55), 2.0),
])
class Env:
    def at(self, t):
        d = dict(sky_track.at(t))
        d.update(web=1.0, spider=1.0, prey=1.0, prey_wrap=1.0, spider_turn=2.0)
        return d
env_track = Env()

WEB = dict(hub=(655, 328), frame=[(570, 235), (742, 214), (748, 420), (585, 440)],
           anchors=[(500, 168), (800, 205), (840, 354), (470, 520)], fade=[0, 3],
           dragline=((632, 438), (650, 1478)), spokes=11, turns=8, spider_size=1.25,
           prey=dict(pos=(712, 262), kind="fly", size=1.9))
MOTH_BUNDLE = dict(prey=1.0, prey_struggle=0.0, prey_wrap=1.0)
def bundle(cr, t, p, env):   # last night's moth (caught on camera in D19), now wrapped
    N.draw_prey(cr, t, MOTH_BUNDLE, (622, 392), "moth", 2.1)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=20, tally_new=[], web=WEB, draw_hook=bundle,
            glass_taps=[(TAP1, 0.7), (TAP2, 0.55)], extra_blinks=[TAP1 + 0.9])
N.main("nigel_bane_ep020_listening.mp4")
