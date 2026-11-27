"""Day 51 — "shaping" (posts as `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII I shaping`).
Body arc 3/4 (the hand outline on OUR side of the glass). Owner-approved script, 2026-11-27.
THE LINE: "There's probably a photo of you like that... Every year, it's a little harder to fit." / "It was only ever
where I stood once."
C: "Don't fix anything. Stay how you're sitting."
T (fear, closing in, like the walls): the outline is smaller every time he looks away. We see it happen, smoothly,
while his eyes are on the window; he looks back and says so. He squeezes his hand in (fingers together, thumb folded,
trembling); will he force himself in? He stops, lets his hand spread out again, half in, half out, and leans his cheek
on the glass beside it. Bridge: he's trying to fit a tracing of himself that keeps getting smaller -> the old photo of
you that's a little harder to fit every year. One continuous shot.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
import hand_outline as HO
from nigel import (P, SKY, Track, mood_vec, KNOCK, STAND, smooth)

N.setup()
T, TE = N.T, N.TE

t_dont, t_stay, t_sitting, t_outline, t_every, t_away1 = T("don't"), T("stay"), TE("sitting"), T("outline's"), T("every"), TE("away")
t_smaller2, t_trying, t_fold, t_thumb, t_nearly = T("smaller", 2), T("trying"), T("fold"), TE("thumb"), T("nearly")
t_looked, t_away2, t_again, t_something, t_isnt = T("looked"), TE("away", 2), T("again"), T("something"), T("isn't")
t_theres, t_summer, t_every2, t_harder, t_stop = T("there's"), T("summer"), T("every", 2), T("harder"), T("stop")
t_half1, t_half2, t_only, t_doesnt, t_end = T("half"), T("half", 2), T("only"), T("doesn't"), TE("this")

# he looks away at the window; while he does, the outline shrinks (we see it; he doesn't, until he looks back)
AWAY1 = (t_every + 0.2, t_smaller2 - 0.35)
AWAY2 = (TE("nearly") + 0.25, t_looked - 0.15)
scale = Track([(0, 0.94, 0), (AWAY1[0] + 0.5, 0.86, AWAY1[1] - AWAY1[0] - 0.7),
               (AWAY2[0] + 0.3, 0.77, AWAY2[1] - AWAY2[0] - 0.4)])

pin_w = Track([(0, 0.0, 0), (t_trying - 0.3, 1.0, 1.0)])
squeeze = Track([(0, 0.0, 0), (t_fold - 0.2, 0.75, 1.3), (t_again, 0.85, 1.0), (t_harder - 1.2, 1.0, 1.6),
                 (t_stop + 0.2, 0.0, 1.4)])                                   # fingers together, thumb folded in
slide = Track([(0, (0.0, 0.0), 0), (t_half1 - 0.4, (55.0, -8.0), 1.0), (t_half2 - 0.3, (125.0, -16.0), 1.0)])  # half in, half out

# ------------------------------------------------------------------ poses
TO_US = P(STAND, look=(0.0, 0.0), swing=0.0)
STILL = P(STAND, look=(0.0, 0.05), eyescale=1.06, tilt=-0.02, swing=0.0)
SEE = P(STAND, relb=(570, 1140), rhand=(560, 1180), look=(0.55, 0.45), tilt=0.08, eyescale=1.1, swing=0.0)
AWAY = P(STAND, look=(0.85, -0.8), tilt=0.14, eyescale=1.02, swing=0.0)                 # looks up at the window
ON = P(STAND, relb=HO.HAND["relb"], rhand=HO.HAND["rhand"], palm=HO.HAND["palm"], look=(0.55, 0.45), tilt=0.07,
       eyescale=1.08, swing=0.0)
ON_AWAY = P(ON, look=(0.85, -0.8), tilt=0.14)
ON_US = P(ON, look=(0.0, 0.0), tilt=0.02)
ON_SOFT = P(ON, look=(0.08, 0.1), tilt=-0.03, eyescale=1.02)
STRAIN = P(ON, look=(0.6, 0.5), eyescale=1.18, tilt=0.1)
CHEEK = P(ON, head=(478, 790), neck=(458, 950), look=(0.4, 0.25), tilt=0.16, shut=0.08, eyescale=0.98)

pose_track = Track([
    (0, KNOCK, 0),
    (t_dont - 0.3, STILL, 0.7),                    # "Don't fix anything. Stay how you're sitting."
    (t_outline - 0.4, SEE, 0.8),                   # "...The outline's smaller."
    (AWAY1[0], AWAY, 0.6),                         # "Every time I look away," — he looks at the window...
    (AWAY1[1], SEE, 0.4),                          # "...it's smaller."
    (t_trying - 0.4, ON, 1.0),                     # "I'm trying to get back in."
    (t_fold, STRAIN, 0.8),                         # "Fold the thumb."
    (AWAY2[0], ON_AWAY, 0.5),                      # a glance away...
    (AWAY2[1], STRAIN, 0.4),                       # "...I looked away. It's smaller again."
    (t_something - 0.2, ON_US, 1.0),
    (t_isnt, ON_SOFT, 1.0),
    (t_theres - 0.3, ON_US, 1.0),
    (t_every2 - 0.3, STRAIN, 1.0),                 # "Every year, it's a little harder to fit."
    (t_stop - 0.3, ON_US, 1.2),                    # "I'm going to stop now."
    (t_half1, P(ON, look=(0.55, 0.45)), 0.8),      # "Half in. Half out."
    (t_only - 0.3, CHEEK, 1.6),                    # leans his cheek on the glass beside it
    (t_doesnt - 0.2, P(CHEEK, look=(0.0, 0.0), shut=0.0), 1.2),
])

def hook(t, p):
    p = HO.pin(p, t, cam_track, pin_w.at(t), offset=slide.at(t))
    q = squeeze.at(t) * pin_w.at(t)
    p["spread"] = 1.0 - 0.75 * q                    # fingers pressed together
    p["thumb_fold"] = q
    p["palm"] *= 1.0 - 0.05 * q
    if q > 0.6:                                     # the strain shows in a fine tremble
        a = (q - 0.6) / 0.4
        p["rhand"] = (p["rhand"][0] + a * 1.6 * math.sin(t * 43), p["rhand"][1] + a * 1.2 * math.sin(t * 37))
        p["head"] = (p["head"][0] + a * 1.2 * math.sin(t * 29), p["head"][1])
    return p

x_track = Track([(0, 0.0, 0)])

cam_track = Track([                                          # ONE continuous shot
    (0, (470, 880, 1.6), 0),
    (t_dont, (485, 900, 1.66), 2.5),
    (t_outline - 0.6, HO.CAM, 2.4),                          # the outline, and him
    (t_trying, (515, 955, 1.62), 4.0),
    (t_something, (500, 925, 1.72), 5.0),                    # in on him
    (t_theres - 0.4, (478, 885, 1.78), 6.0),                 # onto his face for the photo
    (t_stop - 0.6, (525, 965, 1.48), 3.0),                   # back: half in, half out
    (t_only - 0.4, (505, 935, 1.66), 4.0),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_outline, mood_vec("uncanny"), 1.0),
    (t_trying, mood_vec("unease"), 1.0),
    (t_something, mood_vec("lonely"), 1.5),
    (t_theres, mood_vec("drifting"), 1.5),
    (t_summer, mood_vec("warm"), 1.5),
    (t_every2, mood_vec("melancholy"), 1.2),
    (t_stop, mood_vec("drifting"), 1.5),
    (t_only, mood_vec("warm"), 1.5),
])

AFT = dict(top=(170, 188, 214), bot=(234, 224, 212), clouds=0.6, cloud_v=5.0, sun=0.35, sun_y=0.5, sun_r=26)
sky = Track([(0, SKY(**AFT, drone=0.14), 0), (t_trying, SKY(**AFT, drone=0.24), 3.0),
             (t_harder, SKY(**AFT, drone=0.3), 2.0), (t_stop, SKY(**AFT, drone=0.08), 2.5)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

def glass(cr, t, pose, env, to_screen):
    N._palm["pos"] = None
    HO.draw(cr, progress=1.0, scale=scale.at(t), t=t)

sfx = [(t_trying + 0.65, "knock_far", 0.1)]          # his palm landing on the glass

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track, tally_base=50, pose_hook=hook,
            glass_hook=glass, sfx=sfx, caption_avoid=[(0, 99, HO.caption_box(cam_track))])
N.BLINKS = [b for b in N.BLINKS if not (AWAY1[0] - 0.2 < b < AWAY1[1] + 0.3 or AWAY2[0] - 0.2 < b < AWAY2[1] + 0.3)]
N.main("nigel_bane_ep051_shaping.mp4")
