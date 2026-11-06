"""Day 28 — "Used to it". A hairline crack runs across the screen, on OUR side of the glass, and it ticks. C: "Keep your
eyes on it." — he points at it. T: every tick is louder than the last, and the crack creeps a little each time. At first
he flinches, then he counts, then he turns his back on it and looks out of the window instead, and never looks back,
even as the last tick runs it to the edge of the screen. IDEA (you): you can get used to anything — the job that was only
for a year, the town you were leaving after the summer, the ache you stopped mentioning. Nobody decides to stay; you
just stop jumping. UNSETTLE: "I'm not looking at it anymore. You noticed that." (said with his back to it). LIFT
(implied): the evening light in the window he chose to look at. HOOK: "You can get used to anything. That's how you end
up staying."
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, ONE)

N.setup()
T, TE = N.T, N.TE

POINT = P(relb=(548, 1040), rhand=(612, 975), finger=1.0, look=(0.45, 0.3), tilt=0.06, swing=0.0)   # points at it
WATCH = P(look=(0.4, 0.3), tilt=0.05, swing=0.0, eyescale=1.05)
COUNT = P(ONE, look=(0.35, 0.25), tilt=0.04)
ROOM = P(WATCH, look=(0.2, 0.15), tilt=0.0, eyescale=1.0)
WLOOK = P(head=(468, 766), tilt=0.13, look=(0.85, -0.75), swing=0.0)                # looking out of the window
WLOOK2 = P(WLOOK, tilt=0.16, look=(0.8, -0.7), relb=(520, 1100), rhand=(500, 1180))
NOTLOOK = P(WLOOK, tilt=0.1, look=(0.9, -0.6))

t_keep, t_crack, t_right, t_ticks_e, t_listen_e = T("keep"), T("crack"), T("right"), TE("ticks"), TE("listen")
t_jumped_e, t_counted_e, t_room_e, t_thats, t_job = TE("jumped"), TE("counted"), TE("room"), T("that's"), T("job")
t_mention_e, t_stay_e, t_jumping_e, t_im, t_noticed_e = TE("mentioning"), TE("stay"), TE("jumping"), T("i'm"), TE("that", 2)
t_can, t_anything_e, t_staying_e = T("can"), TE("anything"), TE("staying")

# each tick louder than the last; the crack creeps a little with every one
TICKS = [TE("it") + 0.45, t_ticks_e + 0.55, t_listen_e + 0.7, t_jumped_e + 0.35, t_counted_e + 0.6,
         t_room_e + 1.0, t_mention_e + 0.9, t_stay_e + 0.4, t_jumping_e + 0.9, t_noticed_e + 1.1,
         t_anything_e + 0.6, t_staying_e + 0.2]
gains = [0.18 + 0.75 * (k / (len(TICKS) - 1)) ** 1.3 for k in range(len(TICKS))]
sfx = [(tk, "tick", g) for tk, g in zip(TICKS, gains)] + [(tk + 0.03, "crackle", 0.6 * g) for tk, g in zip(TICKS, gains)]
crack = Track([(0, 0.86, 0)] + [(tk, 0.86 + 0.14 * (k + 1) / len(TICKS), 0.25) for k, tk in enumerate(TICKS)])

FLINCH = TICKS[:3]            # he jumps at the first ones, then stops jumping
def flinch(t, p):
    for k, tk in enumerate(FLINCH):
        if t >= tk:
            e = math.exp(-(t - tk) / 0.18) * (1.0 - 0.3 * k)
            p = dict(p)
            p["tilt"] = p.get("tilt", 0) - 0.12 * e
            p["eyescale"] = p.get("eyescale", 1.0) + 0.14 * e
    return p

pose_track = Track([
    (0, KNOCK, 0),
    (t_keep - 0.35, POINT, 0.4),                 # "Keep your eyes on it."
    (t_right + 0.4, WATCH, 0.9),
    (T("second") - 0.2, COUNT, 0.5),             # counting the ticks
    (t_counted_e + 0.8, ROOM, 1.0),
    (t_thats - 0.6, WLOOK, 1.6),                 # turns away to the window
    (t_job, WLOOK2, 2.0),
    (t_im - 0.3, NOTLOOK, 1.4),
    (t_can - 0.3, WLOOK, 2.0),
])
x_track = Track([(0, 0.0, 0), (t_thats - 0.6, 230.0, 2.4)])     # walks over under the window, back to the crack

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_keep - 0.3, (480, 900, 1.42), 0.8),
    (t_crack, (482, 880, 1.6), t_room_e - t_crack),              # slow push while it ticks
    (t_thats - 0.6, (650, 820, 1.08), 2.4),                       # wide: he walks away from it, to the window
    (t_job + 1.0, (680, 760, 1.2), t_im - t_job - 1.0),
    (t_im - 0.2, (700, 760, 1.34), t_staying_e - t_im + 0.4),     # slow push on him, turned away
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_keep, mood_vec("unease"), 0.5),
    (T("second"), mood_vec("uncanny"), 1.2),
    (t_room_e, mood_vec("drifting"), 1.6),
    (t_job, mood_vec("melancholy"), 1.6),
    (t_im, mood_vec("lonely"), 1.4),
    (t_can, mood_vec("uncanny"), 1.6),
])

DAY = dict(top=(184, 196, 210), bot=(230, 233, 238), clouds=0.55, cloud_v=5.0, sun=0.15, sun_y=0.36, sun_r=30)
DUSK = dict(top=(122, 128, 170), bot=(236, 178, 140), clouds=0.4, cloud_v=3.0, sun=0.7, sun_y=0.72, sun_r=36)
sky = Track([
    (0, SKY(**DAY, drone=0.3), 0),
    (t_keep, SKY(**DAY, drone=0.2), 1.0),
    (t_thats, SKY(**DUSK, drone=0.22), t_staying_e - t_thats),   # the day goes while he gets used to it
])
class Env:
    def at(self, t):
        d = dict(sky.at(t))
        d.update(crack=crack.at(t))
        return d
env_track = Env()

CRACK = dict(origin=(752, 1002), heading=2.62, length=1000, seed=11, branches=6)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=27, sfx=sfx, crack=CRACK, pose_hook=flinch)
N.main("nigel_bane_ep028_used.mp4")
