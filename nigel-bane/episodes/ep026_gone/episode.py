"""Day 26 — "Gone". CHAPTER 2 OPENS. The spider is gone; the web hangs empty and torn in the window corner, the bundles
gone with her. C: "Look in the corner. Tell me she's there." — he spins round, pointing up at it. T: the search, corner by
corner (web, wall, floor), then the web letting go piece by piece when he tugs the dragline. IDEA (you): you never see
anything leave — a friend you talked to every day, a song you knew every word to; there was a last time for all of them.
UNSETTLE: "Everything you have right now is already leaving. Slowly enough that it looks like staying." LIFT (implied):
one wisp of silk settles on his open hand and he closes his fingers round it. HOOK: "You never see anything leave. You
just notice, one morning, that it's been gone for a while."
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, OPEN, STAND)

N.setup()
T, TE = N.T, N.TE

CORNER = P(relb=(540, 1000), rhand=(608, 900), finger=1.0, look=(0.8, -0.85), tilt=0.12, swing=0.0)   # points up at the web
UPLOOK = P(look=(0.7, -0.85), tilt=0.1, swing=0.0)
WALLUP = P(look=(-0.8, -0.6), tilt=-0.1, swing=0.0)
WALLDN = P(look=(-0.7, 0.5), tilt=-0.06, swing=0.0)
FLOOR = P(look=(0.3, 0.95), tilt=0.14, swing=0.0, lelb=(400, 1120), lhand=(372, 1190), relb=(500, 1120), rhand=(530, 1190))
GOTIN = P(UPLOOK, lelb=(392, 1090), lhand=(340, 1060), relb=(512, 1090), rhand=(560, 1060), look=(0.6, -0.8))
EVERYDAY = P(UPLOOK, look=(0.55, -0.75), tilt=0.06, eyescale=1.04)
TO_YOU = P(look=(0.0, 0.03), tilt=0.0, swing=0.0)
SOMEONE = P(OPEN, look=(0.0, 0.0))
SONG = P(TO_YOU, relb=(530, 1100), rhand=(478, 1028), lelb=(400, 1100), lhand=(386, 1200), tilt=-0.08)    # hand to chest
LEAVING = P(TO_YOU, eyescale=1.08, tilt=0.02)
REACH = P(relb=(535, 1060), rhand=(588, 985), look=(0.55, -0.7), tilt=0.08, swing=0.0)                       # hand on the dragline
TUG = P(REACH, relb=(530, 1090), rhand=(586, 1030))
WATCH = P(REACH, relb=(530, 1100), rhand=(575, 1060), look=(0.45, -0.55), eyescale=1.06)
PALM = P(relb=(520, 1130), rhand=(565, 1085), look=(0.35, 0.55), tilt=0.1, swing=0.0)                       # open hand, looking at it
HOLD = P(PALM, rhand=(548, 1078), look=(0.1, 0.25), tilt=0.05)
LAST = P(HOLD, look=(0.0, 0.03), tilt=0.02, eyescale=1.04)

t_look, t_tell, t_shes, t_web_e = T("look"), T("tell"), T("she's", 2), TE("web")
t_not2, t_wall_e, t_not3, t_floor_e = T("not", 2), TE("wall"), T("not", 3), TE("floor")
t_she1, t_she2, t_i_looked, t_every1 = T("she"), T("she", 2), T("looked"), T("every")
t_cant, t_you_have, t_someone, t_song = T("can't"), T("have"), T("someone"), T("song")
t_there2, t_nobody, t_everything, t_staying_e = T("there", 3), T("nobody"), T("everything"), TE("staying")
t_oh, t_never, t_just, t_gone = T("oh"), T("never"), T("just"), T("gone")

TUG_T = t_staying_e + 1.2          # he takes the dragline in the silence...
FALL0 = TUG_T + 0.35               # ...and the web lets go
FALL1 = t_oh + 1.0

pose_track = Track([
    (0, KNOCK, 0),
    (t_look - 0.35, CORNER, 0.45),                  # "Look in the corner" — spins round, pointing up at it
    (t_tell, UPLOOK, 0.9),
    (t_web_e + 0.1, WALLUP, 0.6),                   # not on the web... the wall...
    (t_wall_e + 0.4, WALLDN, 0.9),
    (t_not3 - 0.3, FLOOR, 0.7),                     # ...the floor
    (t_she1 - 0.4, GOTIN, 0.9),
    (t_i_looked - 0.3, EVERYDAY, 1.0),
    (t_you_have - 0.4, TO_YOU, 0.8),
    (t_someone - 0.2, SOMEONE, 0.6),
    (t_song - 0.2, SONG, 0.7),
    (t_nobody - 0.2, TO_YOU, 0.8),
    (t_everything - 0.1, LEAVING, 1.0),
    (t_staying_e + 0.1, REACH, 1.0),
    (TUG_T, TUG, 0.25),
    (TUG_T + 0.3, WATCH, 0.8),
    (FALL1 - 0.7, PALM, 0.9),                       # a wisp settles on his hand
    (t_never - 0.2, HOLD, 1.2),                     # fingers close round it
    (t_just, LAST, 1.6),
])

x_track = Track([
    (0, 0.0, 0),
    (t_web_e + 0.1, -175.0, 1.4),                   # to the wall
    (t_not3 - 0.5, -40.0, 1.2),                     # floor, on the way back
    (t_she1 - 0.4, 50.0, 1.4),                      # under the corner
    (t_you_have - 0.4, 20.0, 1.2),
    (t_everything, 50.0, 2.0),
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_look - 0.3, (600, 700, 1.12), 1.1),          # him and the corner
    (t_shes - 0.2, (640, 560, 1.45), 1.2),          # the empty web, him looking up at it
    (t_web_e + 0.1, (420, 960, 1.0), 1.4),          # the search, wide
    (t_she1 - 0.4, (590, 760, 1.2), 1.5),
    (t_i_looked, (600, 700, 1.32), t_you_have - t_i_looked),          # slow push while he stares at it
    (t_you_have - 0.3, (500, 860, 1.42), 1.6),      # to you
    (t_someone, (500, 840, 1.7), t_everything - t_someone),          # slow push
    (t_everything, (495, 830, 1.82), t_staying_e - t_everything + 0.4),
    (t_staying_e + 0.2, (640, 610, 1.38), 1.2),     # the web comes down, around him
    (FALL0 + 1.0, (620, 760, 1.25), FALL1 - FALL0 - 1.0),
    (FALL1 - 0.6, (560, 900, 1.45), 1.4),           # his hand
    (t_never - 0.3, (580, 760, 1.5), 1.6),          # him and the bare corner
    (t_just, (575, 770, 1.68), t_gone - t_just + 1.0),
])
follow_track = Track([(0, 0.0, 0), (t_web_e, 0.12, 0.8), (t_she1, 0.0, 1.2)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_look, mood_vec("unease"), 0.6),
    (t_she1, mood_vec("lonely"), 1.2),
    (t_i_looked, mood_vec("melancholy"), 1.4),
    (t_someone, mood_vec("warm"), 1.4),
    (t_there2, mood_vec("melancholy"), 1.2),
    (t_everything, mood_vec("uncanny"), 1.0),
    (TUG_T, mood_vec("drifting"), 1.0),
    (t_oh, mood_vec("lonely"), 1.2),
    (t_just, mood_vec("uncanny"), 1.6),
])

DAY = dict(top=(176, 190, 206), bot=(226, 230, 236), clouds=0.65, cloud_v=6.0, sun=0.15, sun_y=0.35, sun_r=30)
sky_track = Track([
    (0, SKY(**DAY, drone=0.3), 0),
    (t_everything, SKY(**DAY, drone=0.12), 1.5),               # the room goes quiet under it
    (TUG_T, SKY(**dict(DAY, clouds=0.5), drone=0.0, shimmer=0.2), 1.5),
    (t_never, SKY(**DAY, drone=0.25), 2.5),
])
fall = Track([(0, 0.0, 0), (FALL0, 1.0, FALL1 - FALL0)])
class Env:
    def at(self, t):
        d = dict(sky_track.at(t))
        d.update(web=1.0, spider=0.0, prey=0.0, web_torn=1.0, web_fall=fall.at(t))
        return d
env_track = Env()

WEB = dict(hub=(655, 328), frame=[(570, 235), (742, 214), (748, 420), (585, 440)],
           anchors=[(500, 168), (800, 205), (840, 354), (470, 520)], fade=[0, 3],
           dragline=((632, 438), (650, 1478)), spokes=11, turns=8, spider_size=1.25)

def wisp(cr, t, pose, env):
    """one bit of silk drifts down onto his open hand and stays there"""
    t0, t1 = FALL1 - 1.9, FALL1 - 0.3
    if t < t0:
        return
    hx, hy = pose["rhand"]
    tx, ty = hx + 4, hy - 16
    u = min(1.0, (t - t0) / (t1 - t0))
    e = 1 - (1 - u) ** 2
    x = tx + (1 - e) * 60 + 14 * (1 - u) * math.sin(t * 2.4)
    y = ty - (1 - e) * 300
    cr.save()
    cr.set_line_cap(1)
    cr.move_to(x - 16, y + 2)
    cr.curve_to(x - 6, y - 8 - 3 * math.sin(t * 1.7), x + 4, y + 8, x + 17, y - 1 + 2 * math.sin(t * 2.1))
    cr.set_source_rgba(0.12, 0.12, 0.14, 0.75); cr.set_line_width(1.8); cr.stroke()
    cr.restore()

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=25, web=WEB, plucks=[(TUG_T, 0.9)], draw_hook=wisp)
N.main("nigel_bane_ep026_gone.mp4")
