"""Day 5 — "On Purpose". He remembers the sun on purpose; it's different every time.
Memories are rebuilt, not replayed. First full hand of tally marks. Hook: tomorrow he'll just look out the window.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, THINK, ONE, OPEN, SHRUG, CHEST, EXIST, PRESENT, STAND,
                   POINT_UP, ROLL)

N.setup()
T, TE = N.T, N.TE

WLOOK = P(head=(468, 766), tilt=0.13, look=(0.85, -0.75))
LOOKHAND = P(relb=(560, 1040), rhand=(570, 905), look=(0.45, 0.15), tilt=0.1, swing=0.0)
BUILD = P(lelb=(392, 1085), lhand=(420, 1015), relb=(512, 1085), rhand=(486, 965), look=(0.0, 0.3), swing=0.0)
LOOKBACK = P(look=(-0.8, 0.0), tilt=-0.06, swing=1.0)
SOFT = P(PRESENT, tilt=0.06, look=(0.0, 0.1))

t_okay, t_picked, t_the, t_before = T("okay"), T("picked"), T("the"), T("before")
t_every, t_warmer, t_bigger, t_repaint = T("every"), T("warmer"), T("bigger"), T("repainting")
t_they, t_dont, t_rebuild, t_which = T("they"), T("don't"), T("rebuild"), T("which")
t_past, t_its, t_so, t_but = T("past"), T("it's", 2), T("so"), T("but")
t_five, t_whole, t_think, t_see = T("five"), T("whole"), T("think", 2), T("see")

pose_track = Track([
    (0, KNOCK, 0),
    (t_okay - 0.1, STAND, 0.6),
    (t_picked - 0.1, THINK, 0.7),
    (t_the - 0.2, POINT_UP, 0.8),
    (t_every - 0.1, OPEN, 0.7),
    (t_warmer - 0.1, WLOOK, 0.5),
    (t_bigger - 0.1, EXIST, 0.5),
    (t_repaint - 0.3, ROLL, 0.6),
    (t_they - 0.1, THINK, 0.7),
    (t_dont - 0.1, ONE, 0.4),
    (t_rebuild - 0.2, BUILD, 0.6),
    (t_which - 0.1, LOOKBACK, 0.8),
    (t_its - 0.1, CHEST, 0.6),
    (t_so - 0.1, P(look=(0.0, 0.5), tilt=-0.15, swing=0.5), 0.9),
    (t_but - 0.1, SOFT, 0.8),
    (t_whole - 0.3, LOOKHAND, 0.5),
    (t_think - 0.1, STAND, 0.8),
    (t_see - 0.6, WLOOK, 1.0),
])

x_track = Track([
    (0, 0.0, 0),
    (t_okay, 60.0, 1.2),
    (t_the - 0.3, 170.0, 1.6),            # over toward the window
    (t_they - 0.2, -40.0, 2.4),
    (t_which - 0.1, 140.0, 3.5),          # walks on; his past trails him
    (t_but + 0.2, -195.0, 2.2),           # to the wall
    (t_think + 0.4, 160.0, 2.6),          # back to the window
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_okay - 0.2, (540, 960, 1.0), 2.4),
    (t_the - 0.3, (720, 760, 1.1), 2.0),          # Nigel + the remembered sun
    (t_they - 0.2, (540, 960, 1.0), 2.0),
    (t_but + 0.2, (360, 990, 1.12), 2.0),
    (t_think + 0.3, (700, 760, 1.12), 3.0),
])
follow_track = Track([(0, 0.0, 0), (t_okay, 0.2, 1.5), (t_the - 0.3, 0.0, 1.0), (t_they, 0.2, 1.5),
                      (t_but + 0.2, 0.0, 1.0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_picked, mood_vec("drifting"), 1.0),
    (t_the, mood_vec("awe"), 1.2),
    (t_warmer - 0.1, mood_vec("warm"), 0.5),
    (t_bigger - 0.1, mood_vec("awe"), 0.5),
    (t_repaint - 0.2, mood_vec("uncanny"), 0.4),
    (t_repaint + 0.4, mood_vec("warm"), 0.4),
    (t_repaint + 0.9, mood_vec("drifting"), 0.4),
    (t_they, mood_vec("drifting"), 1.0),
    (t_rebuild, mood_vec("curious"), 1.0),
    (t_which, mood_vec("drifting"), 1.2),
    (t_so, mood_vec("melancholy"), 1.0),
    (t_but, mood_vec("warm"), 1.2),
    (t_five, mood_vec("curious"), 1.0),
    (t_see - 0.3, mood_vec("drifting"), 1.5),
])

PALE = dict(top=(208, 214, 226), bot=(238, 236, 232), clouds=0.4, cloud_v=5.0)
env_track = Track([
    (0, SKY(**PALE, after=0.8, sun_y=0.35), 0),                         # the dotted ghost of the old sun
    (t_the - 0.1, SKY(top=(190, 214, 236), bot=(250, 238, 214), clouds=0.3, cloud_v=4, after=0.3,
                      sun=0.6, sun_r=28, sun_y=0.35, drone=0.5), 1.4),
    (t_warmer - 0.1, SKY(top=(240, 190, 140), bot=(255, 228, 180), clouds=0.2, cloud_v=4, sun=0.9, sun_r=42,
                         sun_y=0.38, beam=0.4, drone=0.6), 0.7),
    (t_bigger - 0.1, SKY(top=(255, 160, 100), bot=(255, 214, 150), clouds=0.1, cloud_v=4, sun=1.0, sun_r=62,
                         sun_y=0.42, beam=0.8, drone=0.8), 0.7),
    # "repainting": the remembered sky changes paint
    (t_repaint, SKY(top=(150, 120, 230), bot=(255, 180, 200), clouds=0.1, sun=1.0, sun_r=55, sun_y=0.42, beam=0.6,
                    drone=0.7), 0.4),
    (t_repaint + 0.5, SKY(top=(90, 200, 190), bot=(250, 240, 170), clouds=0.1, sun=1.0, sun_r=48, sun_y=0.4,
                          beam=0.5, drone=0.7), 0.4),
    (t_repaint + 1.0, SKY(top=(255, 140, 120), bot=(255, 220, 180), clouds=0.1, sun=1.0, sun_r=58, sun_y=0.42,
                          beam=0.6, drone=0.7), 0.4),
    (t_they, SKY(top=(200, 205, 225), bot=(245, 232, 215), clouds=0.4, cloud_v=6, sun=0.5, sun_r=34, sun_y=0.35,
                 beam=0.0, drone=0.5), 1.8),
    (t_which, SKY(top=(195, 190, 220), bot=(240, 225, 220), clouds=0.4, cloud_v=-8, sun=0.4, sun_r=34, sun_y=0.35,
                  echo=1.0, drone=0.55), 1.2),
    (t_so, SKY(top=(170, 175, 195), bot=(215, 215, 222), clouds=0.5, cloud_v=-3, sun=0.0, after=0.8, sun_y=0.35,
               drone=0.35), 1.2),
    (t_but, SKY(top=(195, 210, 232), bot=(250, 236, 214), clouds=0.4, cloud_v=4, sun=0.55, sun_r=32, sun_y=0.35,
                after=0.0, sparkle=0.35, drone=0.55), 1.4),
    (t_think, SKY(top=(150, 195, 235), bot=(235, 240, 245), clouds=0.7, cloud_v=10, sparkle=0.0, drone=0.4), 2.0),
])

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=4, tally_new=[(t_five - 0.05, 0.7)])
N.main("nigel_bain_ep005_on_purpose.mp4")
