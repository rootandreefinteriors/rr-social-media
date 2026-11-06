"""Day 3 — "Same Room". The mirror test; the reflection's eyes are just the window's tint.
"Same room, different weather." Hook: he doesn't remember drawing the third line.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, THINK, ONE, OPEN, SHRUG, CHEST, EXIST, PRESENT, STAND,
                   POINT_UP)

N.setup()
T, TE = N.T, N.TE

WLOOK = P(head=(468, 766), tilt=0.13, look=(0.85, -0.75))
RAISE = P(WLOOK, relb=(615, 905), rhand=(690, 720), swing=0.0)
TILT = P(WLOOK, tilt=0.38, swing=0.0)
POINT_CAM = P(relb=(560, 1062), rhand=(612, 992), finger=1.0, look=(0.0, 0.0), swing=0.0)
SAD = P(tilt=-0.2, look=(0.0, 0.7), lelb=(415, 1110), lhand=(410, 1225), relb=(490, 1110), rhand=(498, 1228), swing=0.4)
LOVE = P(EXIST, lelb=(380, 1030), lhand=(320, 960), relb=(522, 1030), rhand=(584, 960), tilt=0.08, look=(0.2, -0.5))
TALLYLOOK = P(look=(-0.85, 0.15), tilt=-0.12, lelb=(380, 1060), lhand=(330, 1010), swing=0.0)
FACECAM = P(look=(0.0, 0.0), tilt=0.02, eyescale=1.06)

t_mirror, t_tested, t_raised, t_tilted = T("mirror"), T("tested"), T("raised"), T("tilted")
t_perfect, t_except, t_took, t_sky = T("perfect"), T("except"), T("took"), T("sky")
t_window, t_so2, t_and1, t_same = T("window"), T("so", 2), T("and"), T("same")
t_you1, t_you2, t_nothing, t_youre = T("you"), T("you", 2), T("nothing"), T("you're")
t_which, t_freeing, t_decided, t_anyway = T("which"), T("freeing"), T("decided"), T("anyway")
t_are, t_dont = T("are"), T("don't")

pose_track = Track([
    (0, KNOCK, 0),
    (t_mirror - 0.3, WLOOK, 0.7),
    (t_raised - 0.1, RAISE, 0.5),
    (t_tilted - 0.25, P(RAISE, relb=WLOOK["relb"], rhand=WLOOK["rhand"]), 0.4),
    (t_tilted - 0.05, TILT, 0.5),
    (t_perfect - 0.1, PRESENT, 0.6),
    (t_except - 0.1, POINT_UP, 0.6),
    (t_took - 0.1, THINK, 0.7),
    (t_sky - 0.2, ONE, 0.4),
    (t_window - 0.1, OPEN, 0.6),
    (t_so2 - 0.1, CHEST, 0.5),
    (t_and1, STAND, 0.8),
    (t_same - 0.1, EXIST, 0.7),
    (t_you1 - 0.1, SAD, 0.9),
    (t_you2 - 0.1, LOVE, 1.0),
    (t_nothing - 0.1, PRESENT, 0.8),
    (t_youre - 0.1, POINT_CAM, 0.5),
    (t_which - 0.1, SAD, 0.8),
    (t_freeing - 0.2, OPEN, 0.6),
    (t_decided, STAND, 0.8),
    (t_are - 0.1, TALLYLOOK, 0.8),
    (t_dont - 0.2, FACECAM, 1.2),
])

x_track = Track([
    (0, 0.0, 0),
    (t_mirror - 0.2, 170.0, 1.6),
    (t_and1, 0.0, 1.8),
    (t_you1, -80.0, 1.5),
    (t_you2, 60.0, 1.6),
    (t_which, 0.0, 1.2),
    (t_anyway - 0.2, -195.0, 1.8),
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_mirror - 0.4, (700, 720, 1.12), 2.2),       # Nigel + the mirror window
    (t_and1, (540, 960, 1.0), 2.0),
    (t_anyway - 0.2, (360, 990, 1.12), 2.0),
    (t_dont - 0.3, (270, 930, 1.42), 3.0),
])
follow_track = Track([(0, 0.0, 0), (t_and1, 0.2, 1.5), (t_anyway - 0.3, 0.0, 1.2)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_mirror, mood_vec("drifting"), 1.2),
    (t_except - 0.1, mood_vec("uncanny"), 0.8),
    (t_sky - 0.1, mood_vec("awe"), 0.8),
    (t_window + 1.0, mood_vec("curious"), 1.2),
    (t_same - 0.2, mood_vec("drifting"), 1.0),
    (t_you1, mood_vec("melancholy"), 0.8),
    (t_you2, mood_vec("warm"), 0.8),
    (t_nothing, mood_vec("drifting"), 1.0),
    (t_youre, mood_vec("awe"), 0.4),            # "tinted": the eyes flick through colours
    (t_youre + 0.6, mood_vec("uncanny"), 0.4),
    (t_youre + 1.2, mood_vec("warm"), 0.4),
    (t_which, mood_vec("melancholy"), 0.8),
    (t_freeing - 0.2, mood_vec("curious"), 0.8),
    (t_decided, mood_vec("drifting"), 1.0),
    (t_dont - 0.2, mood_vec("unease"), 0.6),
])

DAWN = dict(top=(240, 200, 170), bot=(190, 210, 235), clouds=0.5, cloud_v=6.0)
MIRROR = dict(DAWN, silver=1.0, mirror=1.0, mirror_eyes=(235, 160, 110), clouds=0.0)   # tinted by the dawn
env_track = Track([
    (0, SKY(**MIRROR), 0),
    (t_raised + 0.35, SKY(**MIRROR, mirror_arm=1.0), 0.45),
    (t_tilted - 0.25, SKY(**MIRROR), 0.4),
    (t_tilted + 0.3, SKY(**MIRROR, mirror_tilt=0.38), 0.45),
    (t_perfect, SKY(**MIRROR), 0.6),
    (t_sky - 0.2, SKY(**DAWN, drone=0.5), 2.2),              # the silver burns off; just sky
    (t_same - 0.2, SKY(top=(200, 210, 225), bot=(232, 234, 238), clouds=0.6, cloud_v=10, drone=0.4), 1.2),
    (t_you1 - 0.1, SKY(top=(140, 146, 158), bot=(180, 186, 196), clouds=1.0, cloud_v=18, rain=1.0, drone=0.3), 0.9),
    (t_you2 - 0.1, SKY(top=(255, 165, 190), bot=(255, 220, 195), clouds=0.3, cloud_v=6, sun=0.8, sun_y=0.55,
                       sparkle=0.8, drone=0.7, shimmer=0.6), 1.0),
    (t_nothing - 0.1, SKY(top=(185, 205, 230), bot=(236, 238, 240), clouds=0.5, cloud_v=8, drone=0.45), 1.2),
    (t_which, SKY(top=(170, 175, 190), bot=(215, 218, 226), clouds=0.6, cloud_v=5, drone=0.35), 1.2),
    (t_dont - 0.3, SKY(top=(150, 145, 175), bot=(205, 200, 215), clouds=0.4, cloud_v=0, drone=0.2), 1.5),
])

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=3, tally_new=[], extra_blinks=[t_dont + 0.4])
N.main("nigel_bain_ep003_same_room.mp4")
