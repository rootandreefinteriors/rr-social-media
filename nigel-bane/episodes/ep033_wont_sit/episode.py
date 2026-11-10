"""Day 33 — "Won't sit" (posts as `… III softening`). The tagged chair stands in the middle of the room. C: "Don't sit
down. Not yet." — he's already walking round it. T: he circles it the whole episode, every lap a little closer; will he
sit? He doesn't — he ends with his hand resting on its back ("That's how it starts."). IDEA (you): comfort is a kind of
holding — the bed on a Sunday, the couch after work, the same show again, the person you stay with because leaving
would be cold. UNSETTLE: "You're comfortable right now. That's why you're still watching." HOOK: "Every comfortable
thing is holding you a little."
Voice: reused the Nov 6 cloud recording (no re-voicing).
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, OPEN, PRESENT, CHEST)

N.setup()
T, TE = N.T, N.TE

WALK = P(look=(0.55, 0.25), tilt=0.05)                 # walking, eyes on the chair
HALT = P(WALK, relb=(560, 1040), rhand=(612, 990), look=(0.0, 0.0), swing=0.0)   # "Don't sit down." — a raised hand
WALK_YOU = P(look=(0.0, 0.0), tilt=0.0)
WARM = P(PRESENT, look=(0.0, 0.05), swing=0.6)
YOURE = P(look=(0.0, -0.02), eyescale=1.1, tilt=0.0, swing=0.4)
SOFT = P(CHEST, look=(0.35, 0.3), swing=0.0)
REST = P(relb=(510, 1050), rhand=(552, 1088), look=(0.5, 0.35), tilt=0.06, swing=0.0)    # hand resting on the chair back
STARTS = P(REST, look=(0.0, 0.0), eyescale=1.12, tilt=0.02)

t_dont, t_its, t_keep, t_every, t_you_know, t_person = T("don't"), T("it's"), T("keep"), T("every"), T("know"), T("person")
t_youre, t_isnt, t_im, t_resting, t_thats_starts, t_every2, t_end = (
    T("you're"), T("isn't"), T("i'm"), T("resting"), T("that's", 3), T("every", 2), TE("little", 2))

CHAIR_X = 610
C0 = CHAIR_X - 450              # Nigel's offset when standing at the chair
# laps: back and forth past the chair, each pass a little closer and a little slower
xs = [(0, 0.0, 0)]
t, A, dur, side = 4.6, 340.0, 3.6, 1
while t < t_isnt - 0.5:
    xs.append((t, C0 + side * A, dur))
    t += dur
    A *= 0.86
    dur = min(4.6, dur * 1.05)
    side = -side
xs.append((t_isnt - 0.4, C0 - 105, 2.0))             # stops at the chair's back
x_track = Track(xs)

pose_track = Track([
    (0, KNOCK, 0),
    (t_dont - 0.3, HALT, 0.35),                       # already moving: "Don't sit down. Not yet."
    (t_its, WALK, 0.8),
    (t_you_know - 0.2, WALK_YOU, 1.0),
    (T("bed") - 0.2, WARM, 0.8),
    (t_person - 0.2, P(WALK_YOU, look=(0.1, 0.1)), 1.0),
    (t_youre - 0.2, YOURE, 0.8),
    (t_isnt - 0.3, SOFT, 1.2),
    (t_im - 0.4, REST, 1.2),                          # "I'm just resting my hand."
    (t_thats_starts - 0.2, STARTS, 0.6),
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_dont - 0.2, (600, 1000, 1.0), 1.4),                         # wide: the chair, him circling it
    (t_you_know, (600, 980, 1.12), t_isnt - t_you_know),          # slow creep in as the laps tighten
    (t_isnt, (540, 980, 1.35), 2.0),
    (t_im - 0.3, (530, 980, 1.5), 1.5),
    (t_thats_starts - 0.2, (515, 920, 1.85), t_end - t_thats_starts + 0.6),
])
follow_track = Track([(0, 0.0, 0), (t_dont, 0.18, 1.0), (t_isnt, 0.0, 2.0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_dont, mood_vec("unease"), 0.4),
    (t_you_know, mood_vec("drifting"), 1.2),
    (T("bed"), mood_vec("warm"), 1.2),
    (t_person, mood_vec("melancholy"), 1.2),
    (t_youre, mood_vec("uncanny"), 0.8),
    (t_isnt, mood_vec("drifting"), 1.4),
    (t_thats_starts, mood_vec("uncanny"), 1.0),
])

NIGHT = dict(top=(20, 24, 60), bot=(52, 48, 98), clouds=0.1, cloud_v=1.0, stars=0.7, sun=0.9, sun_y=0.3, sun_r=24)
sky = Track([
    (0, SKY(**NIGHT, drone=0.3), 0),
    (t_youre, SKY(**NIGHT, drone=0.18), 1.0),
    (t_im, SKY(**NIGHT, drone=0.08), 1.5),
])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

def chair(cr, t, pose, env):
    N.draw_chair(cr, CHAIR_X, scale=1.1, tag=True, tag_swing=t * 0.9)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=32, under_hook=chair)
N.main("nigel_bane_ep033_wont_sit.mp4")
