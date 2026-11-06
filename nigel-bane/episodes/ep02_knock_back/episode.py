"""Day 2 — "Knock Back". Can't prove you're real; can't prove he is. First tally marks. Window turns mirror.

python episode.py            -> nigel_bain_ep02_knock_back.mp4
python episode.py --still 5 20 40
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import P, SKY, Track, mood_vec, KNOCK, THINK, ONE, OPEN, SHRUG, CHEST, EXIST, PRESENT, STAND

N.setup()
T, TE = N.T, N.TE

WLOOK = P(head=(468, 766), tilt=0.13, look=(0.85, -0.75))
POINT_CAM = P(relb=(560, 1062), rhand=(612, 992), finger=1.0, look=(0.0, 0.0), swing=0.0)
DREAMY = P(OPEN, tilt=0.1, look=(0.2, -0.3))
TEMPLE = P(relb=(585, 965), rhand=(598, 845), finger=1.0, look=(-0.2, -0.25), tilt=-0.08, swing=0.0)

t_okay, t_ive, t_heres, t_cant = T("okay"), T("i've"), T("here's"), T("can't")
t_you, t_very, t_but = T("you"), T("very"), T("but")
t_maybe1, t_maybe2, t_brain, t_in = T("maybe"), T("maybe", 2), T("brain"), T("in")
t_so, t_one1, t_one2, t_if = T("so"), T("one"), T("one", 2), T("if")
t_still, t_and2, t_where, t_mirror = T("still"), T("and", 2), T("where"), T("mirror")

pose_track = Track([
    (0, KNOCK, 0),
    (t_okay - 0.1, WLOOK, 0.7),
    (t_ive - 0.1, THINK, 0.7),
    (t_heres - 0.1, ONE, 0.45),
    (t_cant - 0.1, POINT_CAM, 0.45),
    (t_you - 0.1, DREAMY, 1.2),
    (t_very, SHRUG, 1.0),
    (t_but - 0.1, CHEST, 0.5),
    (t_maybe1 - 0.1, EXIST, 1.0),
    (t_maybe2 - 0.1, PRESENT, 0.8),
    (t_brain - 0.2, TEMPLE, 0.5),
    (t_in - 0.1, STAND, 1.0),
    (t_if + 0.1, PRESENT, 0.6),
    (t_still - 0.1, WLOOK, 0.9),
    (t_and2 + 0.4, STAND, 0.8),
    (t_where - 0.1, WLOOK, 1.0),
])

x_track = Track([
    (0, 0.0, 0),
    (t_okay + 0.2, 90.0, 1.2),
    (t_ive, -60.0, 2.4),
    (t_but - 0.3, 80.0, 2.0),
    (t_in, 0.0, 1.5),
    (t_so - 0.2, -195.0, 1.7),
    (t_if + 0.1, -120.0, 0.9),
    (t_still, 70.0, 2.4),
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_okay - 0.2, (540, 960, 1.0), 2.4),
    (t_maybe1, (540, 900, 1.08), 3.0),
    (t_in - 0.3, (540, 1000, 0.72), 2.2),          # "a little white room": the room shrinks around him
    (t_so, (380, 990, 1.12), 1.8),                 # over to the wall
    (t_if, (430, 960, 1.0), 1.5),
    (t_still, (540, 960, 1.0), 2.0),
    (t_where - 0.2, (800, 440, 1.5), 2.8),         # end on the window
])
follow_track = Track([(0, 0.0, 0), (t_okay, 0.2, 2.0), (t_so - 0.3, 0.0, 1.0), (t_still, 0.2, 1.5),
                      (t_where - 0.2, 0.0, 1.5)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_okay, mood_vec("uncanny"), 1.0),
    (t_ive, mood_vec("drifting"), 1.2),
    (t_heres, mood_vec("curious"), 0.8),
    (t_you, mood_vec("drifting"), 1.5),
    (t_maybe1, mood_vec("uncanny"), 1.2),
    (t_maybe2 + 1.0, mood_vec("melancholy"), 2.0),
    (t_so, mood_vec("warm"), 1.5),
    (t_still, mood_vec("melancholy"), 1.2),
    (t_and2 + 0.6, mood_vec("uncanny"), 1.5),
    (t_mirror - 0.3, mood_vec("unease"), 0.4),
])

DAWN = dict(top=(238, 214, 200), bot=(200, 214, 232), clouds=0.55, cloud_v=8.0)
env_track = Track([
    (0, SKY(**DAWN), 0),
    (t_okay, SKY(**DAWN, ripple=0.45), 0.4),
    (t_ive, SKY(**DAWN), 1.0),
    (t_you, SKY(top=(210, 195, 235), bot=(240, 225, 240), clouds=0.6, cloud_v=4.0, drone=0.45), 2.0),
    (t_very, SKY(top=(200, 180, 235), bot=(240, 215, 238), clouds=0.7, cloud_v=-6.0, lift=18, roll=0.02,
                 drone=0.5), 2.0),
    (t_maybe1, SKY(top=(150, 120, 210), bot=(240, 190, 220), clouds=0.9, cloud_v=-30.0, lift=70, roll=-0.04,
                   echo=0.6, drone=0.7), 1.6),
    (t_maybe2, SKY(top=(160, 130, 215), bot=(238, 195, 222), clouds=0.8, cloud_v=-20.0, lift=50, roll=0.03,
                   echo=0.4, drone=0.6), 1.6),
    (t_in - 0.3, SKY(top=(200, 205, 212), bot=(228, 230, 234), clouds=0.4, cloud_v=2.0, drone=0.3), 2.0),
    (t_so, SKY(top=(190, 220, 240), bot=(250, 240, 220), clouds=0.6, cloud_v=10.0, drone=0.5), 1.8),
    (t_if, SKY(top=(170, 210, 240), bot=(255, 240, 205), clouds=0.4, cloud_v=6.0, sun=0.7, sun_y=0.3, beam=0.35,
               drone=0.6), 1.6),
    (t_still, SKY(top=(170, 180, 200), bot=(215, 220, 230), clouds=0.5, cloud_v=3.0, drone=0.35), 1.6),
    (t_and2, SKY(top=(170, 180, 200), bot=(215, 220, 230), clouds=0.2, cloud_v=0.0, silver=1.0, drone=0.2), 2.2),
    (t_where, SKY(top=(170, 180, 200), bot=(215, 220, 230), clouds=0.0, cloud_v=0.0, silver=1.0, mirror=1.0,
                  mirror_eyes=(20, 150, 170), drone=0.0), 1.6),   # his reflection's eyes are NOT his colour
])

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=0,
            tally_new=[(t_one1 - 0.15, 0.55), (t_one2 - 0.15, 0.55)],   # one for yesterday, one for today
            extra_blinks=[t_where + 0.3])
N.main("nigel_bain_ep02_knock_back.mp4")
