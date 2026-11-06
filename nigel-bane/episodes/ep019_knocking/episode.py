"""Day 19 (v2) — "Knocking". Night; a moth is beating against the inside of the window, trying to reach the moon, right
next to the spider's web. ONE idea: things that love the light. Right after the open he's under the window waving it
away from the web ("Go on. Not that way."). It wants the moon — moths steer by it — but a window isn't the sky, so it
keeps hitting the glass (soft taps all episode). YOU: "Your face is lit up right now. Pointed at the brightest thing in
the room. It isn't the sky either. But you keep coming back to it." The spider has been watching the whole time: "She
knows where it ends up." — and the moth flies into the web on camera. "Oh." Hook: "Things that love the light don't
know when to stop knocking." Five shots, slow moves. (v1 rejected 2026-10-23: lights-out gimmick, glass print, too busy.)
"""
import math
import random
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, ONE, OPEN, CHEST, POINT_UP, PRESENT)

N.setup()
T, TE = N.T, N.TE

UP = dict(look=(0.6, -0.92), tilt=0.12, swing=0.0)
SHOO = P(**UP, relb=(575, 1000), rhand=(640, 872), roll=0.85)
MOON = P(POINT_UP, look=(0.75, -0.9), tilt=0.12)
STRAIGHT_A = P(ONE, rhand=(500, 990), relb=(520, 1070), look=(0.4, -0.5), tilt=0.06)
STRAIGHT_B = P(ONE, rhand=(660, 985), relb=(580, 1060), look=(0.6, -0.6), tilt=0.08)
GLASS = P(OPEN, **UP)
WATCH = P(**UP, lelb=(412, 1100), lhand=(402, 1215), relb=(500, 1100), rhand=(512, 1215))
TO_YOU = P(look=(0.0, 0.02), tilt=0.0, swing=0.0)
YOU_POINT = P(ONE, look=(0.0, 0.0), relb=(540, 1050), rhand=(560, 940))
BRIGHT = P(PRESENT, look=(0.0, 0.05))
SOFT = P(CHEST, look=(0.0, 0.1), tilt=-0.04)
WEBLOOK = P(WATCH, look=(0.45, -0.95), tilt=0.1)
REACH = P(WEBLOOK, relb=(560, 1010), rhand=(620, 905), eyescale=1.06)
LAST = P(TO_YOU, eyescale=1.04, tilt=0.03)

t_there_end, t_go, t_wants, t_moths, t_they = TE("there"), T("go"), T("wants"), T("moths"), T("they")
t_but1, t_its, t_night_end = T("but"), T("it's"), TE("night")
t_you1, t_face, t_pointed, t_isnt2, t_keep2 = T("you"), T("face"), T("pointed"), T("isn't", 2), T("keep", 2)
t_shes, t_knows, t_up_end, t_oh = T("she's"), T("knows"), TE("up", 2), T("oh")
t_things, t_knocking = T("things"), T("knocking")

CATCH = t_up_end + 0.55                  # the moth flies into the web
CATCH_POS = (622, 392)

pose_track = Track([
    (0, KNOCK, 0),
    (t_there_end + 0.1, SHOO, 0.7),                # under the window: go on, not that way
    (t_wants - 0.2, MOON, 0.7),
    (t_they - 0.1, STRAIGHT_A, 0.5),
    (t_they + 1.3, STRAIGHT_B, 1.5),               # ...and fly straight
    (t_but1 - 0.1, GLASS, 0.7),
    (t_its - 0.2, WATCH, 0.9),                     # just watching it hit the glass
    (t_you1 - 0.3, TO_YOU, 0.9),
    (t_face - 0.1, YOU_POINT, 0.5),
    (t_pointed + 0.1, BRIGHT, 0.7),
    (t_keep2 - 0.4, SOFT, 0.8),
    (t_shes - 0.3, WEBLOOK, 0.9),
    (CATCH - 0.1, REACH, 0.35),                    # half a reach — too late
    (t_oh + 0.4, WEBLOOK, 1.2),
    (t_things - 0.3, LAST, 1.0),
])

x_track = Track([
    (0, 0.0, 0),
    (t_there_end + 0.1, 165.0, 1.6),               # straight over under the window
    (t_you1 - 0.3, 60.0, 1.6),
    (CATCH - 0.15, 105.0, 0.6),                    # a step toward it
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_there_end + 0.1, (650, 600, 1.12), 2.2),    # him, the window, the moth, the web
    (t_you1 - 0.3, (520, 840, 1.45), 2.0),         # to you
    (t_you1 + 1.8, (515, 845, 1.6), 6.0),          # slow push while he talks
    (t_shes - 0.2, (640, 540, 1.22), 2.2),         # the web, the moth, him
    (t_knows - 0.2, (640, 390, 1.95), 3.5),         # in close on the web for the catch
    (t_things - 0.4, (580, 620, 1.15), 2.0),       # to us, with the web behind him
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_wants, mood_vec("drifting"), 1.2),
    (t_but1, mood_vec("melancholy"), 1.2),
    (t_you1, mood_vec("uncanny"), 1.2),
    (t_keep2, mood_vec("lonely"), 1.2),
    (t_shes, mood_vec("unease"), 1.2),
    (t_oh, mood_vec("lonely"), 1.0),
    (t_things, mood_vec("uncanny"), 1.2),
])

NIGHT = dict(top=(18, 22, 58), bot=(48, 44, 96), clouds=0.0, cloud_v=0.0, stars=0.75, sun=0.95, sun_y=0.34, sun_r=26)
sky_track = Track([
    (0, SKY(**NIGHT, drone=0.3), 0),
    (t_you1, SKY(**NIGHT, drone=0.4), 2.0),
    (t_shes, SKY(**NIGHT, drone=0.5), 2.0),
    (CATCH, SKY(**NIGHT, drone=0.7, shimmer=0.2), 1.0),
    (t_things, SKY(**NIGHT, drone=0.5), 1.5),
])
struggle = Track([(0, 0.0, 0), (CATCH, 1.0, 0.1), (CATCH + 3.0, 0.7, 2.0), (t_things + 1.0, 0.45, 2.0)])
to_prey = Track([(0, 0.0, 0), (CATCH + 0.8, 1.0, 3.2)])
turn = Track([(0, math.pi / 2, 0), (t_shes, 0.25, 1.5)])     # she has been facing the window the whole time
class Env:
    def at(self, t):
        d = dict(sky_track.at(t))
        d.update(web=1.0, spider=1.0, prey=0.0, prey_struggle=struggle.at(t), spider_to_prey=to_prey.at(t),
                 spider_turn=turn.at(t))
        return d
env_track = Env()

WEB = dict(hub=(655, 328), frame=[(570, 235), (742, 214), (748, 420), (585, 440)],
           anchors=[(500, 168), (800, 205), (840, 354), (470, 520)], fade=[0, 3],
           dragline=((632, 438), (650, 1478)), spokes=11, turns=8, spider_size=1.25,
           prey=dict(pos=CATCH_POS, kind="moth"))  # drawn by the hook below; the spider walks to it

# ---- the moth: beating against the inside of the window, then into the web
rr = random.Random(19)
BUMPS = []
bt = 0.6
while bt < CATCH - 1.4:
    BUMPS.append(bt); bt += rr.uniform(1.6, 2.8)
BUMPS += [t_night_end + 0.5, t_night_end + 1.15]          # the two we listen to
BUMPS = sorted(b for b in BUMPS if b < CATCH - 1.3)
FLY_BUNDLE = dict(prey=1.0, prey_struggle=0.0, prey_wrap=1.0)

def flutter(t):
    drift = 30 * N.smooth((t - t_shes) / 4.0)              # edges a little toward the web corner near the end
    bx = 865 - drift + 40 * math.sin(t * 0.41)             # but stays on the window side until the dive
    by = 365 + 60 * math.sin(t * 0.57 + 1)
    jx = 15 * math.sin(t * 8.3) + 7 * math.sin(t * 13.1)
    jy = 11 * math.cos(t * 6.7) + 6 * math.sin(t * 11.3)
    return bx + jx, by + jy

def moth(cr, t, p, env):
    N.draw_prey(cr, t, FLY_BUNDLE, (712, 262), "fly", 1.9)             # the fly from D18, still wrapped
    if t < CATCH:
        x, y = flutter(t)
        u = (t - (CATCH - 1.1)) / 1.1
        if u > 0:                                                       # the last dive, into the web
            x, y = N.lerp((x, y), CATCH_POS, N.smooth(u))
            y -= 40 * math.sin(math.pi * u)
        bump = sum(math.exp(-((t - b) / 0.07) ** 2) for b in BUMPS)
        N.draw_moth(cr, x + 6 * bump, y - 4 * bump, 2.1 * (1 + 0.1 * bump), t * 40, 1.0, 0.25 * math.sin(t * 2.1))
    else:                                                               # stuck: wings beating in place
        st = env["prey_struggle"]
        x = CATCH_POS[0] + st * 2.5 * math.sin(t * 31); y = CATCH_POS[1] + st * 2.0 * math.cos(t * 27)
        flap = (t * 34) if st > 0.5 else 0.6 + 0.4 * math.sin(t * 9)
        N.draw_moth(cr, x, y, 2.0, flap, 1.0, -0.35)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=19, tally_new=[], web=WEB, draw_hook=moth,
            sfx=[(b, "knock_far", 0.075) for b in BUMPS] + [(CATCH, "thrum", 0.16)])
N.main("nigel_bane_ep019_knocking.mp4")
