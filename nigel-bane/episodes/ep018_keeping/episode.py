"""Day 18 — "Keeping". A fly is caught in yesterday's web, buzzing. Right after the open he freezes mid-step:
"Don't move. That's what it did wrong." It isn't stuck until it tries to leave; every pull finds another thread.
YOU: you don't feel yours either until you try to go (phone down at 1am, stop checking if they saw it, leave the town
you grew up in) — and faint threads appear running from his own body out into the room (signature device; he looks
down at them). The spider walks out and wraps the fly: "She isn't even hungry. She's just... keeping it. For later."
The dare: "Try it. Right now. Try to stop watching me." 3 s of real silence, him frozen, staring. "...You're still
here." (eyes soften: the implied lift) — he finally puts his foot down. Hook: "Eighteen days. I've never tried to
leave. I just assumed I could." (sets up D23, the edge of the room)
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, ONE, OPEN, READ, STAND)

N.setup()
T, TE = N.T, N.TE

# ---- poses: legs frozen mid-step (right foot lifted), upper body still talks
FZ = dict(lknee=(430, 1362), lfoot=(410, 1478), rknee=(514, 1318), rfoot=(546, 1392), swing=0.0)
FZ_START = P(**FZ, lelb=(398, 1084), lhand=(352, 1148), relb=(504, 1084), rhand=(552, 1146), look=(0.3, -0.5), tilt=0.06)
FZ_UP = P(FZ_START, look=(0.5, -0.95), tilt=0.1)
FZ_CAM = P(FZ_START, look=(0.0, 0.0), tilt=0.02)
FZ_ONE = P(ONE, **FZ, look=(0.05, -0.05))
FZ_PHONE = P(READ, **FZ, letter=0.0, look=(0.0, 0.75), tilt=-0.1)
FZ_PHONE_UP = P(FZ_PHONE, look=(0.1, 0.0), tilt=0.0)
FZ_AWAY = P(OPEN, **FZ, look=(-0.6, -0.1), tilt=-0.05)
FZ_DOWN = P(**FZ, lelb=(400, 1090), lhand=(368, 1182), relb=(502, 1090), rhand=(534, 1182), look=(0.05, 0.9), tilt=-0.1)
FZ_STARE = P(FZ_CAM, eyescale=1.08)
SOFT = P(look=(0.0, 0.05), tilt=0.04, swing=0.0, eyescale=1.02)
TALLY_LOOK = P(look=(-0.88, 0.1), tilt=-0.08, swing=0.0)
EDGE_LOOK = P(look=(0.95, 0.05), tilt=0.05, swing=0.0)
LAST = P(look=(0.0, 0.0), tilt=0.0, swing=0.0, eyescale=1.04)

t_there_end, t_move, t_wrong = TE("there"), T("move"), T("wrong")
t_tries, t_pulls, t_you1 = T("tries"), T("pulls"), T("you")
t_not, t_put, t_stop1, t_leave2 = T("not"), T("put"), T("stop"), T("leave", 2)
t_thats2, t_threads, t_were_end = T("that's", 2), T("threads"), TE("were")
t_she, t_shes, t_keeping, t_later_end = T("she"), T("she's"), T("keeping"), TE("later")
t_try1, t_me_end = T("try", 2), TE("me")
t_youre, t_here_end = T("you're"), TE("here")
t_eighteen, t_ive, t_just, t_could = T("eighteen"), T("i've"), T("just", 2), T("could")

pose_track = Track([
    (0, KNOCK, 0),
    (t_there_end + 0.05, FZ_START, 0.35),         # one step... and he freezes
    (t_move + 0.6, FZ_UP, 0.9),
    (t_you1 - 0.25, FZ_CAM, 0.6),
    (t_not - 0.1, FZ_ONE, 0.5),
    (t_put - 0.2, FZ_PHONE, 0.6),
    (t_stop1 + 0.6, FZ_PHONE_UP, 0.6),
    (t_leave2 - 0.15, FZ_AWAY, 0.6),
    (t_threads - 0.5, FZ_DOWN, 0.8),              # ...and sees his own threads
    (t_she - 0.2, FZ_UP, 0.8),
    (t_try1 - 0.25, FZ_CAM, 0.5),
    (t_me_end + 0.1, FZ_STARE, 0.8),
    (t_youre - 0.1, P(FZ_STARE, eyescale=1.0), 0.6),
    (t_here_end + 0.3, SOFT, 1.0),                # finally, the foot comes down
    (t_eighteen - 0.25, TALLY_LOOK, 0.7),
    (t_ive - 0.1, EDGE_LOOK, 0.9),                # toward the edge of the room
    (t_just - 0.2, LAST, 0.9),
])

x_track = Track([(0, 0.0, 0)])

FLY = (712, 262)
cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_there_end + 0.1, (600, 640, 1.1), 1.3),     # him frozen; the web; something in it
    (t_move + 0.5, (690, 320, 2.4), 1.8),          # the fly
    (t_pulls, (590, 700, 1.05), 2.0),
    (t_you1 - 0.2, (480, 870, 1.45), 1.8),
    (t_leave2, (500, 900, 1.3), 2.0),
    (t_thats2 - 0.1, (540, 880, 0.95), 2.2),       # wide: the threads
    (t_she - 0.2, (680, 315, 2.3), 1.8),           # she walks out to it
    (t_try1 - 0.25, (470, 860, 1.7), 1.2),         # the dare
    (t_me_end + 0.1, (470, 835, 1.98), 3.6),       # the silence, creeping in
    (t_here_end + 0.2, (480, 900, 1.3), 1.6),
    (t_eighteen - 0.2, (330, 960, 1.1), 1.6),
    (t_ive - 0.1, (560, 900, 1.2), 1.8),
    (t_just - 0.3, (470, 850, 1.7), 2.0),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_move - 0.2, mood_vec("unease"), 0.6),
    (t_wrong + 0.6, mood_vec("uncanny"), 1.0),
    (t_you1, mood_vec("drifting"), 1.2),
    (t_put, mood_vec("melancholy"), 1.2),
    (t_thats2, mood_vec("uncanny"), 1.0),
    (t_she, mood_vec("unease"), 1.0),
    (t_keeping, mood_vec("lonely"), 1.2),
    (t_try1, mood_vec("unease"), 0.8),
    (t_youre, mood_vec("warm"), 1.2),
    (t_eighteen, mood_vec("lonely"), 1.2),
    (t_just, mood_vec("uncanny"), 1.2),
])

GREY = dict(top=(190, 196, 210), bot=(228, 226, 222), clouds=0.6, cloud_v=3.0)
sky_track = Track([
    (0, SKY(**GREY, drone=0.3), 0),
    (t_move + 0.5, SKY(**GREY, drone=0.45), 1.0),
    (t_you1, SKY(**GREY, drone=0.35), 1.5),
    (t_thats2, SKY(top=(180, 184, 200), bot=(220, 218, 216), clouds=0.5, cloud_v=2.0, drone=0.6, shimmer=0.4), 1.2),
    (t_she - 0.3, SKY(**GREY, drone=0.45), 1.5),
    (t_me_end, SKY(**GREY, drone=0.0), 0.5),       # real silence
    (t_youre, SKY(top=(214, 206, 214), bot=(246, 232, 214), clouds=0.4, cloud_v=2.0, sun=0.45, sun_y=0.62, sun_r=30,
                  drone=0.2), 1.6),               # a little warmth comes through
    (t_eighteen, SKY(**GREY, drone=0.3), 2.0),
    (t_just, SKY(top=(178, 184, 198), bot=(218, 216, 214), clouds=0.5, cloud_v=2.0, drone=0.5), 1.5),
])

# the fly: twitching, with bursts when it pulls; the spider walks out and wraps it
bursts = [(0.15, 1.1, 0.8), (t_move + 0.55, 1.8, 1.0), (t_tries, 1.0, 1.0), (t_pulls, 1.1, 1.0),
          (t_not + 0.6, 0.8, 0.6), (t_she - 0.1, 1.3, 1.0)]
skeys = [(0, 0.25, 0)]
for t0, dur, amp in bursts:
    skeys += [(t0, amp, 0.12), (t0 + dur, 0.25, 0.35)]
skeys += [(t_shes + 0.5, 0.0, 1.2)]          # wrapped: it stops
struggle_track = Track(skeys)
buzz_track = Track([(k[0], k[1] * 0.9, k[2]) for k in skeys])
to_prey = Track([(0, 0.0, 0), (t_she - 0.1, 1.0, 2.2), (t_try1 - 0.3, 0.0, 2.5)])
wrap_track = Track([(0, 0.0, 0), (t_shes - 0.3, 1.0, 3.0)])
threads_track = Track([(0, 0.0, 0), (t_thats2 + 0.6, 1.0, 1.4), (t_were_end + 0.2, 1.0, 0.1), (t_she - 0.4, 0.0, 1.4)])
glint_track = Track([(0, 0.0, 0), (t_were_end - 0.3, 1.0, 0.5), (t_were_end + 0.6, 0.0, 1.2)])

class Env:
    def at(self, t):
        d = dict(sky_track.at(t))
        st = struggle_track.at(t)
        d.update(web=1.0, spider=1.0, prey=1.0, prey_struggle=st, buzz=buzz_track.at(t),
                 spider_to_prey=to_prey.at(t), prey_wrap=wrap_track.at(t),
                 threads=threads_track.at(t), glint=glint_track.at(t))
        return d
env_track = Env()

WEB = dict(hub=(655, 328),
           frame=[(570, 235), (742, 214), (748, 420), (585, 440)],
           anchors=[(500, 168), (800, 205), (840, 354), (470, 520)], fade=[0, 3],
           dragline=((632, 438), (650, 1478)),
           spokes=11, turns=8, spider_size=1.25,
           prey=dict(pos=FLY, kind="fly", size=1.9))

# threads from his own body out into the room (and one to the web)
ROOM_ANCHORS = [("rhand", (1500, 760)), ("lhand", (-420, 860)), ("top", (560, -620)), ("left", (-360, 260)),
                ("hip", (1450, 1350)), ("lfoot", (60, 1478)), ("rfoot", (930, 1478)), ("rhand", (655, 328)),
                ("right", (990, 530)), ("top", (180, -500))]
def threads(cr, t, p, env):
    a = env["threads"]
    if a < 0.01:
        return
    hx, hy = p["head"]
    pts = dict(top=(hx + 10, hy - 168), left=(hx - 166, hy - 20), right=(hx + 160, hy + 40))
    g = env["glint"]
    for k, (j, (ax, ay)) in enumerate(ROOM_ANCHORS):
        sx, sy = pts[j] if j in pts else p[j]
        mx, my = (sx + ax) / 2, (sy + ay) / 2 + 40 + 20 * math.sin(k * 1.7)     # silk sags a little
        sway = 3 * math.sin(t * 1.3 + k)
        reach = min(1.0, max(0.0, a * 1.6 - k * 0.06))                          # they appear one after another
        if reach <= 0:
            continue
        ex, ey = sx + (ax - sx) * reach, sy + (ay - sy) * reach
        cx_, cy_ = sx + (mx - sx) * reach, sy + (my + sway - sy) * reach
        for col, al, wd in [(N.INK, 0.7 * a, 2.1)] + ([((1.0, 0.72, 0.25), 0.45 * g, 8), ((1.0, 0.95, 0.8), 0.95 * g, 2.2)]
                                                       if g > 0.01 else []):
            cr.move_to(sx, sy); cr.curve_to(cx_, cy_, cx_, cy_, ex, ey)
            cr.set_source_rgba(*col, al); cr.set_line_width(wd); cr.stroke()

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=18, tally_new=[], web=WEB, draw_hook=threads,
            extra_blinks=[t_me_end + 1.7])
N.main("nigel_bane_ep018_keeping.mp4")
