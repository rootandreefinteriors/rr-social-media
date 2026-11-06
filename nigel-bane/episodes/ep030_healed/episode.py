"""Day 30 — "Healed". A strip of tape is stuck to OUR side of the glass. C: "Point to the crack. Under the tape. Go on." —
he points at it. Then the tape lets go and falls away down the screen: there's nothing under it. T: his fingertip
searches the clean glass for the crack the whole episode, slower and slower, and never finds it. IDEA (you): healing is
mostly forgetting exactly where it hurt — a scar you'd have to look for now, a name that used to hurt to hear, a song
you can listen to again. You didn't decide to get better; one day you went to touch the sore part and couldn't find it.
UNSETTLE: "Glass doesn't heal. I know that much. Glass doesn't heal." LIFT (implied): morning sun, the song line, his
hand finally resting flat. HOOK: "You heal by forgetting where it was. Then you can't find it again."
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, OPEN, CHEST, ONE)

N.setup()
T, TE = N.T, N.TE

POINT = P(relb=(560, 1050), rhand=(600, 990), finger=1.0, look=(-0.35, 0.45), tilt=-0.08, swing=0.0)
FALLS = P(POINT, look=(-0.45, 0.8), tilt=-0.12, eyescale=1.12)
SEARCH = P(relb=(590, 1100), rhand=(672, 1045), finger=1.0, look=(0.4, 0.35), tilt=0.05, swing=0.0, eyescale=1.04)
FLAT = P(SEARCH, look=(0.0, 0.05), eyescale=1.08, tilt=0.0)
TO_YOU = P(look=(0.0, 0.03), tilt=0.0, swing=0.0)
SCAR = P(ONE, look=(0.0, 0.0))
NAME = P(CHEST, look=(0.0, 0.08))
SONG = P(OPEN, look=(0.0, 0.0), tilt=0.06)
SEARCH2 = P(SEARCH, look=(0.3, 0.25), tilt=0.08)
REST = P(relb=(600, 1060), rhand=(640, 960), palm=0.75, look=(0.0, 0.03), tilt=0.02, swing=0.0)   # hand flat on the glass

t_point, t_go, t_gone, t_theres, t_was1, t_or = T("point"), T("go"), T("gone"), T("there's"), T("was"), T("or")
t_glass1, t_glass2, t_heal2_e, t_youve = T("glass"), T("glass", 2), TE("heal", 2), T("you've")
t_scar, t_name, t_song, t_didnt, t_one, t_find_e = T("scar"), T("name"), T("song"), T("didn't"), T("one"), TE("it", 2)
t_had, t_ago_e, t_heal3, t_then = T("had"), TE("ago"), T("heal", 3), T("then")

LIFT0, DROP0, DROP1 = TE("on") - 0.1, TE("on") + 0.5, TE("on") + 1.5     # the tape peels, lets go, falls away
lift = Track([(0, 0.15, 0), (LIFT0, 1.0, 0.7)])
drop = Track([(0, 0.0, 0), (DROP0, 1.0, DROP1 - DROP0)])

# his fingertip hunts across the glass: wide and quick at first, slower and smaller until it stops
def hunt(t, p):
    if p.get("finger", 0) < 0.5 or t < t_gone:
        return p
    u = min(1.0, (t - t_gone) / (t_heal3 + 1.5 - t_gone))
    amp = 70 * (1 - u) ** 0.7
    ph = 2.2 * (t - t_gone) - 0.9 * (t - t_gone) ** 2 / (t_heal3 - t_gone + 4)   # it slows down
    p = dict(p)
    x, y = p["rhand"]
    p["rhand"] = (x + amp * math.sin(ph * 1.3), y + 0.6 * amp * math.sin(ph * 0.9 + 1.0))
    return p

pose_track = Track([
    (0, KNOCK, 0),
    (t_point - 0.35, POINT, 0.45),               # "Point to the crack. Under the tape."
    (LIFT0, FALLS, 0.6),                          # watches it fall
    (t_gone + 0.2, SEARCH, 0.8),                  # fingertip on the glass, hunting
    (t_glass1 - 0.2, FLAT, 1.0),
    (t_youve - 0.3, TO_YOU, 1.0),                 # steps back to talk to you
    (t_scar - 0.2, SCAR, 0.6),
    (t_name - 0.2, NAME, 0.6),
    (t_song - 0.2, SONG, 0.7),
    (t_didnt - 0.2, TO_YOU, 0.8),
    (t_had - 0.4, SEARCH2, 1.0),                  # back to the glass, slower
    (t_heal3 + 1.0, REST, 1.6),                   # gives up; hand flat
])
x_track = Track([(0, 0.0, 0), (t_youve - 0.3, -25.0, 1.2), (t_had - 0.4, 0.0, 1.0)])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_point - 0.3, (470, 900, 1.48), 0.8),
    (LIFT0, (470, 905, 1.42), 1.5),                              # let the tape fall through frame
    (t_gone, (475, 875, 1.55), 1.2),
    (t_theres, (478, 860, 1.75), t_youve - t_theres),           # slow push while he hunts
    (t_youve - 0.3, (485, 930, 1.25), 1.6),                      # back a step
    (t_scar, (485, 905, 1.42), t_had - t_scar),
    (t_had - 0.4, (470, 870, 1.65), 1.4),
    (t_heal3 - 0.3, (468, 850, 1.9), t_then - t_heal3 + 3.0),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_point, mood_vec("unease"), 0.5),
    (t_gone, mood_vec("uncanny"), 0.8),
    (t_youve, mood_vec("melancholy"), 1.4),
    (t_song, mood_vec("warm"), 1.4),
    (t_had, mood_vec("drifting"), 1.4),
    (t_heal3, mood_vec("uncanny"), 1.6),
])

MORN = dict(top=(150, 190, 236), bot=(250, 238, 214), clouds=0.3, cloud_v=2.5, sun=0.85, sun_y=0.4, sun_r=32)
sky = Track([
    (0, SKY(**MORN, drone=0.3), 0),
    (LIFT0, SKY(**MORN, drone=0.12), 0.5),
    (t_youve, SKY(**MORN, drone=0.28), 2.0),
    (t_song, SKY(**dict(MORN, beam=0.35, sparkle=0.15), drone=0.3), 2.0),     # the sun comes in on the song
    (t_had, SKY(**MORN, drone=0.15), 2.0),
])
class Env:
    def at(self, t):
        d = dict(sky.at(t))
        d.update(crack=1.0, crack_vis=0.0, tape=1.0 if t < DROP1 else 0.0, tape_lift=lift.at(t), tape_drop=drop.at(t))
        return d
env_track = Env()

CRACK = dict(origin=(752, 1002), heading=2.62, length=1000, seed=11, branches=6, tape_at=0.4, tape_len=380, tape_w=72)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=29, crack=CRACK, pose_hook=hunt, sfx=[(LIFT0 + 0.5, "tick", 0.18)])
N.main("nigel_bane_ep030_healed.mp4")
