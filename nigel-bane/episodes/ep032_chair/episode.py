"""Day 32 — "The chair" (posts as `… II fitting`). C: "Sit up. Look how you're holding your head." — then he shows
you: chin down, shoulders in, hands together, the way you hold your phone — and stays like that. T: he holds that
posture the whole episode; near the end he tries to come up and can't quite. A chair has appeared, tagged "for nigel",
exactly his height ("Somebody measured."). IDEA (you): everything made for you is shaped like you — your shoes, your
pillow, the screen in your hand — and then, slowly, you're shaped like it. UNSETTLE: "My neck has stopped asking."
HOOK: "Everything made for you is also making you."
Voice: reused the Nov 6 cloud recording (no re-voicing).
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, smooth, KNOCK)

N.setup()
T, TE = N.T, N.TE

TALL = P(head=(452, 762), neck=(452, 934), look=(0.0, 0.0), eyescale=1.12, tilt=0.0, swing=0.0)       # "Sit up."
CHIN = P(TALL, head=(468, 812), neck=(460, 975), look=(0.0, -0.2), tilt=0.06, eyescale=1.0)
SHOULD = P(CHIN, lelb=(425, 1095), lhand=(420, 1180), relb=(482, 1095), rhand=(486, 1180))
HUNCH = P(CHIN, head=(502, 862), neck=(480, 992), lelb=(446, 1112), lhand=(518, 1078), relb=(522, 1118),
          rhand=(530, 1080), look=(0.0, -0.36), tilt=0.2)                                         # hands together
HUNCH_CHAIR = P(HUNCH, look=(0.55, -0.15), tilt=0.12)
HUNCH_YOU = P(HUNCH, look=(0.0, -0.35), eyescale=1.06)
HUNCH_DEEP = P(HUNCH, head=(514, 886), neck=(488, 1006), look=(0.0, -0.48), tilt=0.24)

t_sit, t_look, t_like, t_chin, t_shoulders, t_hands = T("sit"), T("look"), T("like"), T("chin"), T("shoulders"), T("hands")
t_thats, t_theres, t_its, t_somebody, t_everything = T("that's"), T("there's"), T("it's"), T("somebody"), T("everything")
t_ive, t_my, t_its2, t_come_e, t_everything2, t_end = T("i've"), T("my"), T("it's", 2), TE("up", 2), T("everything", 2), TE("you", 5)

TRY0, TRY1 = t_its2, t_come_e + 0.9      # tries to come up; can't quite
def strain(t, p):
    if TRY0 <= t <= TRY1:
        u = (t - TRY0) / (TRY1 - TRY0)
        up = math.sin(math.pi * u) * 26                          # rises a little, sinks back
        sh = math.sin(t * 38) * 2.2 * math.sin(math.pi * u)      # and shakes with the effort
        p = dict(p)
        p["head"] = (p["head"][0] + sh, p["head"][1] - up)
        p["neck"] = (p["neck"][0], p["neck"][1] - up * 0.5)
        p["eyescale"] = p.get("eyescale", 1.0) + 0.06 * math.sin(math.pi * u)
    return p

pose_track = Track([
    (0, KNOCK, 0),
    (t_sit - 0.3, TALL, 0.35),                     # "Sit up." — snaps upright
    (t_chin - 0.1, CHIN, 0.6),                     # "Chin down."
    (t_shoulders - 0.1, SHOULD, 0.6),              # "Shoulders in."
    (t_hands - 0.1, HUNCH, 0.7),                   # "Hands together."
    (t_thats, HUNCH_YOU, 0.8),                     # "That's how you're watching me."
    (t_theres - 0.2, HUNCH_CHAIR, 0.8),            # glances at the chair, without coming up
    (t_everything - 0.3, HUNCH_YOU, 1.0),
    (t_ive - 0.2, HUNCH_DEEP, 2.0),
    (t_everything2 - 0.2, P(HUNCH_DEEP, eyescale=1.08), 1.0),
])
x_track = Track([(0, 0.0, 0)])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_sit, (465, 900, 1.5), 0.6),
    (t_like, (468, 920, 1.62), t_thats - t_like),            # in on the posture
    (t_theres - 0.2, (600, 1060, 1.05), 1.6),                # wide: the chair beside him
    (t_its, (640, 1080, 1.25), t_somebody - t_its + 1.5),    # creep toward it
    (t_everything - 0.3, (480, 930, 1.4), 1.6),              # back to him, still hunched
    (t_everything + 2.0, (475, 920, 1.62), t_ive - t_everything - 2.0),
    (t_ive - 0.2, (472, 915, 1.8), t_end - t_ive + 0.6),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_sit, mood_vec("unease"), 0.4),
    (t_thats, mood_vec("uncanny"), 1.0),
    (t_theres, mood_vec("curious"), 1.2),
    (t_somebody, mood_vec("uncanny"), 1.0),
    (t_everything, mood_vec("drifting"), 1.6),
    (t_ive, mood_vec("melancholy"), 1.4),
    (t_its2, mood_vec("unease"), 1.0),
    (t_everything2, mood_vec("uncanny"), 1.4),
])

AFTERNOON = dict(top=(176, 192, 222), bot=(246, 222, 190), clouds=0.35, cloud_v=3.0, sun=0.7, sun_y=0.62, sun_r=32)
DUSK = dict(top=(110, 118, 162), bot=(232, 168, 136), clouds=0.3, cloud_v=2.0, sun=0.6, sun_y=0.8, sun_r=34)
sky = Track([
    (0, SKY(**AFTERNOON, drone=0.3), 0),
    (t_everything, SKY(**DUSK, drone=0.24), t_end - t_everything),     # the light goes while he holds it
    (t_its2, SKY(**DUSK, drone=0.06), 1.0),
])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

def chair(cr, t, pose, env):
    N.draw_chair(cr, 735, scale=1.15, tag=True, tag_swing=t * 1.1)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=31, under_hook=chair, pose_hook=strain)
N.main("nigel_bane_ep032_chair.mp4")
