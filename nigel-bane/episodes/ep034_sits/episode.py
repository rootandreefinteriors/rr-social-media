"""Day 34 — "Sits" (posts as `… IIII anchoring`). C: "Try to stand up. Right now. Without your hands." — he
drops into the chair as he says it, then waits for you to try (real silence). R (the test): "Did you use your hands?
…Most people do." The chair has a dip in it now, his shape; your favourite spot has one too ("That dip is every
evening you spent there"). T: his turn — no hands — he strains, rises a little, sinks back; tries again; "It's
further up than it was." ENDING (flip): "Okay. You can sit back down. You were going to anyway." Featured sound: the
none (a synthesized chair creak was cut: it sounded like a fart).
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK)

N.setup()
T, TE = N.T, N.TE

CX = 600                    # the chair, same spot as Days 32–36
OFF = CX - 450              # Nigel's offset when he's in it
SEAT = P(head=(450, 845), neck=(451, 1012), hip=(450, 1290), lelb=(408, 1150), lhand=(398, 1262), relb=(494, 1150),
         rhand=(504, 1262), lknee=(384, 1302), lfoot=(380, 1478), rknee=(516, 1302), rfoot=(520, 1478),
         look=(0.0, 0.02), tilt=0.0, swing=0.0)
WAIT = P(SEAT, eyescale=1.08, look=(0.0, 0.0))
MOST = P(SEAT, tilt=0.07, look=(0.05, 0.05))
DIP = P(SEAT, look=(0.3, 0.75), tilt=0.12, relb=(505, 1170), rhand=(548, 1268))           # looks down at the seat
YOU = P(SEAT, look=(0.0, 0.02))
WARM = P(SEAT, look=(0.0, 0.05), tilt=-0.04, eyescale=1.04)
NOHANDS = P(SEAT, lelb=(402, 1095), lhand=(470, 1085), relb=(500, 1095), rhand=(432, 1085), look=(0.0, -0.1))  # arms folded
LIFT = P(NOHANDS, head=(452, 806), neck=(452, 972), hip=(450, 1246), lknee=(388, 1290), rknee=(512, 1290), eyescale=1.12)
SINK = P(NOHANDS, tilt=0.05, look=(0.1, 0.2))
RUEFUL = P(SEAT, look=(0.0, 0.05), tilt=0.08)
FLIP = P(SEAT, look=(0.0, 0.0), tilt=0.02, eyescale=1.02)

t_try, t_hands_e, t_did, t_ive, t_dip, t_nobody, t_your = T("try"), TE("hands"), T("did"), T("i've"), T("dip"), T("nobody"), T("favourite")
t_okay1, t_no, t_give, t_further, t_okay2, t_end = T("okay"), T("no"), T("give"), T("further"), T("okay", 2), TE("anyway")

TRY1, TRY2 = TE("hands", 3) + 0.3, TE("second") + 0.2         # his two attempts
pose_track = Track([
    (0, KNOCK, 0),
    (t_try - 0.35, SEAT, 0.55),                    # drops into the chair as he says it
    (t_hands_e + 0.1, WAIT, 1.0),                  # waits for you to try
    (t_did, MOST, 0.8),
    (t_ive - 0.2, YOU, 0.8),
    (t_dip - 0.2, DIP, 0.8),                       # the dip in the seat
    (t_nobody - 0.2, YOU, 0.8),
    (t_your - 0.2, WARM, 1.0),
    (t_okay1 - 0.2, YOU, 0.6),
    (t_no - 0.2, NOHANDS, 0.6),
    (TRY1, LIFT, 1.6), (TRY1 + 2.4, SINK, 0.9),    # rises a little… sinks back
    (TRY2, LIFT, 1.2), (TRY2 + 1.5, SINK, 0.8),
    (t_further - 0.2, RUEFUL, 0.8),
    (t_okay2 - 0.2, FLIP, 1.0),
])
def strain(t, p):
    for a, b in ((TRY1, TRY1 + 2.4), (TRY2, TRY2 + 1.5)):
        if a <= t <= b:
            u = (t - a) / (b - a)
            p = dict(p); sh = math.sin(t * 41) * 2.6 * math.sin(math.pi * u)
            p["head"] = (p["head"][0] + sh, p["head"][1]); p["neck"] = (p["neck"][0] + sh * 0.5, p["neck"][1])
    return p

x_track = Track([(0, 0.0, 0), (t_try - 0.4, float(OFF), 0.5)])
cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_try - 0.3, (600, 1010, 1.3), 0.8),                       # him in the chair
    (t_hands_e, (600, 1000, 1.5), t_did - t_hands_e),           # holds on him while you try
    (t_dip - 0.3, (610, 1120, 1.55), 1.2),                      # the seat
    (t_nobody, (600, 1000, 1.45), 1.2),
    (t_your, (598, 980, 1.62), t_okay1 - t_your),               # slow push
    (t_no, (600, 1060, 1.25), 1.0),                             # wide enough to see him try
    (t_further, (600, 1000, 1.45), 1.4),
    (t_okay2, (598, 975, 1.72), t_end - t_okay2 + 0.6),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_try, mood_vec("unease"), 0.5),
    (t_did, mood_vec("warm"), 1.0),
    (t_ive, mood_vec("drifting"), 1.2),
    (t_your, mood_vec("melancholy"), 1.4),
    (t_no, mood_vec("unease"), 0.8),
    (t_further, mood_vec("lonely"), 1.0),
    (t_okay2, mood_vec("uncanny"), 1.2),
])

MORN = dict(top=(168, 196, 232), bot=(246, 236, 214), clouds=0.4, cloud_v=3.0, sun=0.7, sun_y=0.45, sun_r=30)
sky = Track([(0, SKY(**MORN, drone=0.28), 0), (t_hands_e, SKY(**MORN, drone=0.08), 0.6), (t_did, SKY(**MORN, drone=0.26), 1.0),
             (t_no, SKY(**MORN, drone=0.1), 0.8), (t_okay2, SKY(**MORN, drone=0.24), 1.0)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

def chair(cr, t, pose, env):
    N.draw_chair(cr, CX, scale=1.1, tag=True, tag_swing=t * 0.8)

sfx = []
N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=33, under_hook=chair, pose_hook=strain, sfx=sfx)
N.main("nigel_bane_ep034_sits.mp4")
