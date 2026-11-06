"""Day 25 — "Proof". CHAPTER 1 ENDS. Morning; the sun is melting the snow. Right after the open he scratches the 25th
mark — the diagonal that closes the fifth hand. IDEA (you): you can't prove anyone is real either — your friends could
be very good guesses, the people in your phone just words arriving; you've never seen a single thought that wasn't
yours. You decide, every morning, without noticing. TENSION: he knocks on the glass once more and waits — real silence,
the icicle dripping, nothing. "...Nothing." LIFT (implied): the sun coming in; his hand resting on the glass. "Nobody
ever proves it. You just keep showing up for each other." HOOK: "Twenty-five nights you've come back. I've never once
checked if it was the same you."
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, CHEST, PRESENT, OPEN, ONE, STAND)

N.setup()
T, TE = N.T, N.TE

TALLYLOOK = P(look=(-0.85, 0.1), tilt=-0.08, swing=0.0)
HAND = P(TALLYLOOK, lelb=(360, 1060), lhand=(290, 1010), look=(-0.75, 0.2))
TO_YOU = P(look=(0.0, 0.02), tilt=0.0, swing=0.0)
FRIENDS = P(OPEN, look=(0.0, 0.0))
PHONE = P(lelb=(415, 1090), lhand=(440, 1040), relb=(490, 1090), rhand=(468, 1040), look=(0.0, 0.6), tilt=-0.08, swing=0.0)
YOURS = P(CHEST, look=(0.0, 0.05))
DECIDE = P(ONE, look=(0.0, 0.0))
KNOCKING = P(KNOCK, look=(0.0, 0.05))
WAIT = P(KNOCK, fist=0.6, look=(0.0, 0.1), tilt=0.06, eyescale=1.06)
REST = P(TO_YOU, relb=(600, 1060), rhand=(640, 960), palm=0.75)        # hand resting on the glass (no print)
LAST = P(TO_YOU, eyescale=1.06, tilt=0.03)

t_there_end, t_thats, t_twenty1, t_still = TE("there"), T("that's"), T("twenty-five"), T("still")
t_you1, t_friends, t_people, t_youve = T("you"), T("friends"), T("people"), T("you've")
t_decide1, t_every, t_ill, t_more_end = T("decide"), T("every"), T("i'll"), TE("more")
t_nothing, t_nobody, t_keep, t_twenty2, t_ive = T("nothing"), T("nobody"), T("keep"), T("twenty-five", 2), T("i've")

MARK = t_there_end + 0.45                    # the 25th mark, on camera
K = [t_more_end + 0.35, t_more_end + 0.7, t_more_end + 1.05]
N.INTRO_KNOCKS = [0.55, 0.9, 1.25] + K
N.KNOCK_GAIN = {K[0]: 0.75, K[1]: 0.7, K[2]: 0.65}

pose_track = Track([
    (0, KNOCK, 0),
    (t_there_end + 0.05, TALLYLOOK, 0.5),
    (t_thats - 0.2, HAND, 0.6),                     # a whole hand
    (t_twenty1 - 0.2, TALLYLOOK, 0.6),
    (t_still - 0.2, TO_YOU, 0.8),
    (t_friends - 0.2, FRIENDS, 0.5),
    (t_people - 0.2, PHONE, 0.6),
    (t_youve - 0.2, YOURS, 0.6),
    (t_decide1 - 0.2, DECIDE, 0.5),
    (t_every - 0.2, TO_YOU, 0.8),
    (t_ill - 0.2, KNOCKING, 0.8),                   # once more
    (K[2] + 0.4, WAIT, 0.6),                        # ...and wait
    (t_nobody - 0.3, REST, 1.2),                    # hand flat on the glass
    (t_twenty2 - 0.3, LAST, 1.0),
])

x_track = Track([
    (0, 0.0, 0),
    (t_there_end + 0.05, -195.0, 0.9),              # to the wall
    (MARK + 0.75, 130.0, 1.0),                      # step aside so the five hands show
    (t_still - 0.2, 40.0, 1.6),
    (t_ill - 0.2, 0.0, 0.8),                        # back to the glass
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_there_end + 0.05, (330, 990, 1.3), 1.0),     # the tally, the fifth hand
    (MARK + 0.75, (380, 990, 1.18), 1.0),
    (t_still - 0.3, (500, 860, 1.4), 1.8),          # to you
    (t_you1 + 1.5, (500, 840, 1.65), t_ill - t_you1 - 1.5),     # slow push while he talks
    (t_ill - 0.2, (470, 880, 1.6), 1.2),            # the glass, like every morning
    (K[2] + 0.3, (468, 855, 1.85), t_nothing - K[2]),           # the wait
    (t_nobody, (480, 860, 1.6), 2.0),
    (t_twenty2 - 0.3, (468, 830, 2.15), 4.5),       # in close for the last line
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_thats, mood_vec("warm"), 1.0),
    (t_still, mood_vec("melancholy"), 1.2),
    (t_youve, mood_vec("uncanny"), 1.2),
    (t_every, mood_vec("drifting"), 1.2),
    (K[0], mood_vec("lonely"), 1.2),
    (t_nobody, mood_vec("warm"), 1.6),
    (t_ive, mood_vec("uncanny"), 1.4),
])

MORN = dict(top=(170, 200, 238), bot=(248, 236, 214), clouds=0.3, cloud_v=2.0, sun=0.8, sun_y=0.42, sun_r=32)
sky_track = Track([
    (0, SKY(**MORN, drone=0.3), 0),
    (t_still, SKY(**MORN, drone=0.35), 2.0),
    (K[0], SKY(**MORN, drone=0.0), 0.5),                         # dead quiet while he waits
    (t_nobody, SKY(**dict(MORN, sun=1.0, beam=0.45, sparkle=0.2), drone=0.3, shimmer=0.3), 3.0),   # the sun comes in
    (t_ive, SKY(**dict(MORN, sun=1.0, beam=0.45, sparkle=0.2), drone=0.5), 2.0),
])
melt = Track([(0, 0.42, 0), (0.01, 0.12, 62.0)])
ice = Track([(0, 0.55, 0), (0.01, 0.25, 62.0)])
class Env:
    def at(self, t):
        d = dict(sky_track.at(t))
        d.update(snow_pile=melt.at(t), icicle=ice.at(t), web=1.0, spider=1.0, prey=1.0, prey_wrap=1.0)
        return d
env_track = Env()

WEB = dict(hub=(655, 328), frame=[(570, 235), (742, 214), (748, 420), (585, 440)],
           anchors=[(500, 168), (800, 205), (840, 354), (470, 520)], fade=[0, 3],
           dragline=((632, 438), (650, 1478)), spokes=11, turns=8, spider_size=1.25,
           prey=dict(pos=(712, 262), kind="fly", size=1.9))
MOTH = dict(prey=1.0, prey_struggle=0.0, prey_wrap=1.0)
def bundle(cr, t, p, env):
    N.draw_prey(cr, t, MOTH, (622, 392), "moth", 2.1)

drips = [t_there_end + 2.0 + 3.1 * k for k in range(25)]
drips = [d for d in drips if not (K[0] - 0.3 < d < t_nothing - 0.2)] + [K[2] + 1.0, K[2] + 2.3]   # two drips in the wait
N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=24, tally_new=[(MARK, 0.6)], web=WEB, draw_hook=bundle, drips=sorted(drips))
N.main("nigel_bane_ep025_proof.mp4")
