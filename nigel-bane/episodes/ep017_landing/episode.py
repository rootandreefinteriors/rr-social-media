"""Day 17 — "Landing". A spider got in last night; she spins her web on camera in the corner by the window.
Idea (about YOU): she makes it out of herself and feels anything that touches any part of it — that's what this glass
is: every time you touch your screen, he feels it ("I felt you get here"). You make one too, out of what's inside you
(the people you follow, what you watch at 3am), then sit in the middle and wait for something to land.
Lift (implied): the web is invisible until the light hits it. Hook: "Everything that lands in a web thinks it found
something." Unsettling: his palm on the glass + the print it leaves; the web trembles by itself when he says he felt
you arrive (he notices). Signature device: the web being spun on camera.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, OPEN, SHRUG, CHEST, PRESENT, ONE, STAND)

N.setup()
T, TE = N.T, N.TE

# ---- poses
UPWEB = dict(look=(0.45, -0.95), tilt=0.12, swing=0.0)
HUSH = P(**UPWEB, relb=(560, 1050), rhand=(545, 960), finger=1.0)
POINT_WEB = P(**UPWEB, relb=(548, 1000), rhand=(612, 885), finger=1.0)
STILL = P(**UPWEB, lelb=(412, 1100), lhand=(402, 1215), relb=(500, 1100), rhand=(512, 1215))
AROUND = P(STILL, look=(-0.85, -0.2), tilt=-0.1)
OPEN_UP = P(OPEN, **UPWEB)
FROM_CHEST = P(CHEST, look=(0.45, -0.9), tilt=0.08)
PULL_OUT = P(**UPWEB, lelb=(400, 1100), lhand=(386, 1200), relb=(545, 1060), rhand=(628, 1012))
NOTHING = P(SHRUG, look=(-0.4, -0.9), tilt=-0.05)
REACH = P(look=(0.55, 0.25), tilt=0.05, relb=(565, 1040), rhand=(636, 1000), finger=1.0, swing=0.0)
REACH_PULL = P(REACH, rhand=(660, 1007))
REACH_REL = P(REACH, rhand=(628, 995))
WATCHUP = P(STILL, eyescale=1.06)
TOUCH_SOFT = P(REACH, look=(0.45, -0.9), tilt=0.1)
TO_CAM = P(look=(0.0, 0.02), tilt=0.0, swing=0.0)
PALM = P(TO_CAM, relb=(600, 1110), rhand=(668, 985), palm=2.4, eyescale=1.04)
PALM_GLANCE = P(PALM, look=(0.6, -0.9), tilt=0.1)
CHEST_ME = P(CHEST, look=(0.0, 0.05))
OPEN_YOU = P(PRESENT, look=(0.0, 0.0))
ONE_YOU = P(ONE, look=(0.1, -0.05))
NIGHTLOOK = P(look=(0.85, -0.75), tilt=0.13, swing=0.0)
SEEK = P(STILL, look=(-0.5, -0.6), tilt=-0.06)
SUNUP = P(STILL, look=(0.8, -0.8), tilt=0.12, eyescale=1.06)
LAST = P(TO_CAM, tilt=0.05, eyescale=1.05)

t_shh, t_look, t_night, t_how = T("shh"), T("look"), T("night"), T("how")
t_shes, t_thread, t_comes, t_hangs, t_nothing = T("she's"), T("thread"), T("comes"), T("hangs"), T("nothing")
t_watch, t_felt, t_touches, t_part = T("watch"), T("felt"), T("touches"), T("part")
t_think, t_every2, t_touch, t_feel = T("think"), T("every", 2), T("touch"), T("feel")
t_felt2, t_here2_end = T("felt", 2), TE("here", 2)
t_make, t_inside, t_people, t_things, t_three = T("make"), T("inside"), T("people"), T("things"), T("three")
t_andthen, t_wait, t_land_end = T("and", 2), T("wait"), TE("land")
t_most, t_see, t_only, t_light = T("most"), T("see"), T("only"), T("light")
t_every_last, t_thinks, t_found = T("everything"), T("thinks"), T("found")

W0 = TE("watch")                 # ~1.9 s of silence follows "Watch." — the pluck lives here
PLUCK = W0 + 0.62
TREMBLE = t_here2_end + 0.25     # nobody touches it: the web shivers by itself

pose_track = Track([
    (0, KNOCK, 0),
    (t_shh - 0.35, HUSH, 0.5),
    (t_look - 0.1, POINT_WEB, 0.6),
    (t_night - 0.3, STILL, 0.7),
    (t_how - 0.15, AROUND, 0.5),                  # where did she get in?
    (t_shes - 0.3, OPEN_UP, 0.6),
    (t_thread - 0.25, FROM_CHEST, 0.5),           # it comes out of you...
    (t_comes + 0.1, PULL_OUT, 0.9),               # ...and out
    (t_hangs - 0.2, NOTHING, 0.6),
    (W0 - 0.5, REACH, 0.7),
    (PLUCK - 0.32, REACH_PULL, 0.28),
    (PLUCK, REACH_REL, 0.06),                     # twang
    (PLUCK + 0.35, WATCHUP, 0.9),
    (t_touches - 0.45, TOUCH_SOFT, 0.4),          # a fingertip, barely
    (t_part + 0.1, WATCHUP, 0.8),
    (t_think - 0.2, TO_CAM, 0.9),
    (t_touch - 0.55, PALM, 0.55),                 # his palm flat on the glass
    (TREMBLE + 0.22, PALM_GLANCE, 0.3),           # the web moved. he looks.
    (t_make - 0.3, P(OPEN_YOU, look=(0.0, 0.1)), 0.8),
    (t_inside - 0.2, CHEST_ME, 0.5),
    (t_people - 0.2, OPEN_YOU, 0.6),
    (t_things - 0.2, ONE_YOU, 0.6),
    (t_three - 0.2, NIGHTLOOK, 0.8),
    (t_andthen - 0.1, STILL, 1.2),                # goes still, like her
    (t_most - 0.2, P(STILL, eyescale=1.0), 0.8),
    (t_see - 0.2, SEEK, 0.8),
    (t_only - 0.2, SUNUP, 0.9),
    (t_every_last - 0.2, LAST, 1.0),
    (t_thinks, P(LAST, eyescale=1.1, tilt=0.02), 1.0),
])

x_track = Track([
    (0, 0.0, 0),
    (t_shh - 0.3, 40.0, 1.2),
    (W0 - 0.9, 0.0, 0.9),
    (t_make, 30.0, 1.6),
    (t_most - 0.2, 60.0, 1.6),
    (t_every_last - 0.3, 0.0, 1.6),
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_shh - 0.2, (560, 640, 1.12), 1.6),         # reveal: the web above him
    (t_night - 0.2, (640, 400, 2.15), 2.2),       # up close: she's spinning
    (t_hangs - 0.1, (560, 300, 1.7), 2.4),        # along a thread that ends in nothing
    (W0 - 0.6, (600, 760, 1.0), 1.4),             # him, the dragline, the web
    (t_felt + 0.1, (650, 430, 1.55), 1.8),
    (t_think - 0.1, (470, 880, 1.6), 1.8),        # back to the glass
    (t_touch - 0.4, (480, 860, 1.85), 2.0),
    (t_make, (520, 820, 1.2), 2.0),
    (t_andthen, (655, 335, 2.7), 4.2),            # the one in the middle, waiting
    (t_most - 0.1, (600, 520, 1.15), 2.2),
    (t_light - 0.2, (630, 470, 1.3), 3.0),
    (t_every_last - 0.1, (470, 840, 1.85), 3.5),  # to you
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_look, mood_vec("awe"), 0.8),
    (t_how - 0.1, mood_vec("uncanny"), 0.6),
    (t_shes, mood_vec("drifting"), 1.0),
    (W0, mood_vec("curious"), 0.8),
    (t_felt, mood_vec("awe"), 1.0),
    (t_think, mood_vec("unease"), 1.0),
    (t_make, mood_vec("drifting"), 1.2),
    (t_three, mood_vec("melancholy"), 1.0),
    (t_andthen, mood_vec("lonely"), 1.4),
    (t_land_end, mood_vec("uncanny"), 1.0),
    (t_most, mood_vec("drifting"), 1.2),
    (t_light, mood_vec("awe"), 1.2),
    (t_light + 1.6, mood_vec("warm"), 1.4),
    (t_thinks, mood_vec("unease"), 1.4),
])

MORN = dict(top=(196, 206, 228), bot=(246, 232, 214), clouds=0.4, cloud_v=4.0, spider=1.0)
NIGHT = dict(top=(16, 18, 44), bot=(40, 36, 80), clouds=0.0, cloud_v=0.0, stars=0.6, spider=1.0)
PRE = dict(top=(150, 160, 190), bot=(200, 196, 206), clouds=0.15, cloud_v=2.0, spider=1.0)
SUN = dict(top=(255, 190, 140), bot=(255, 226, 180), clouds=0.2, cloud_v=2.0, sun=1.0, sun_y=0.72, sun_r=40,
           beam=0.7, sparkle=0.35, shimmer=0.5, spider=1.0)
sky_track = Track([
    (0, SKY(**MORN, drone=0.25), 0),
    (t_how - 0.1, SKY(**MORN, drone=0.45), 0.8),
    (t_shes, SKY(**MORN, drone=0.3), 1.2),
    (t_think, SKY(top=(186, 192, 208), bot=(232, 226, 220), clouds=0.3, cloud_v=3.0, spider=1.0, drone=0.5), 1.4),
    (t_here2_end, SKY(top=(176, 182, 200), bot=(226, 220, 216), clouds=0.3, cloud_v=2.0, spider=1.0, drone=0.8), 0.6),
    (t_make, SKY(**MORN, drone=0.35), 1.6),
    (t_three - 0.2, SKY(**NIGHT, drone=0.4), 1.2),
    (t_andthen, SKY(**NIGHT, drone=0.55), 1.5),
    (t_land_end + 0.2, SKY(**NIGHT, drone=0.8), 0.8),
    (t_most, SKY(**PRE, drone=0.35), 2.0),
    (t_only - 0.2, SKY(**SUN, drone=0.5), 2.0),
    (t_every_last, SKY(**dict(SUN, beam=0.5, shimmer=0.3), drone=0.55), 2.0),
    (t_thinks, SKY(**dict(SUN, beam=0.5, shimmer=0.3), drone=0.75), 1.5),
])
web_track = Track([(0, 0.42, 0), (0.01, 0.62, 6.0), (6.02, 0.82, 6.5), (12.6, 1.0, 6.4)])
vis_track = Track([(0, 1.0, 0), (t_see - 0.1, 0.12, 1.2), (t_light - 0.15, 1.0, 1.2)])
glow_track = Track([(0, 0.0, 0), (t_light - 0.15, 1.0, 1.5), (t_every_last + 0.5, 0.75, 3.0)])
dy_track = Track([(0, 0.0, 0), (PLUCK + 0.08, 24.0, 0.18), (PLUCK + 2.0, 0.0, 0.9),
                  (t_touches + 0.08, 12.0, 0.15), (t_part + 0.3, 0.0, 0.6),
                  (TREMBLE + 0.05, 10.0, 0.2), (TREMBLE + 1.2, 0.0, 0.8)])
turn_track = Track([(0, math.pi / 2, 0), (PLUCK + 0.08, math.pi / 2 + 0.3, 0.2), (PLUCK + 2.0, math.pi / 2, 0.8),
                    (TREMBLE + 0.05, math.pi / 2 - 0.9, 0.35), (t_make + 1.0, math.pi / 2, 1.2)])

class Env:
    """sky track + separate web tracks merged into one env state"""
    def at(self, t):
        d = dict(sky_track.at(t))
        d.update(web=web_track.at(t), web_vis=vis_track.at(t), web_glow=glow_track.at(t),
                 spider_dy=dy_track.at(t), spider_turn=turn_track.at(t))
        return d
env_track = Env()

WEB = dict(hub=(655, 328),
           frame=[(570, 235), (742, 214), (748, 420), (585, 440)],
           anchors=[(500, 168), (800, 205), (840, 354), (470, 520)],   # two moorings end in nothing
           fade=[0, 3],
           dragline=((632, 438), (650, 1478)),
           spokes=11, turns=8, spider_size=1.25)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=17, tally_new=[], web=WEB,
            plucks=[(PLUCK, 1.0), (t_touches + 0.02, 0.45), (TREMBLE, 0.6)],
            extra_blinks=[TREMBLE + 0.9])
N.main("nigel_bane_ep017_landing.mp4")
