"""Day 52 — "slowing" (posts as `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII II slowing`).
Body arc 4/4, the exit: the hand outline on OUR side of the glass fades and is gone. Owner-approved script, 2026-11-27.
THE LINE: "Your heart has never once asked you for anything."
C: "Shh. Put your hand on your chest." (personal-attention moment; Bible rule 11 lists D52)
T (fear): he lays his ear on the glass where his hand was and we hear his heart through it, fast, then slowing, the
gaps getting longer ("...Don't stop. ...Don't stop."); will it stop? It settles into a calm beat. Bridge: something
has kept him going the whole time without being asked -> yours, under your hand, right now. The outline pulses faintly
with each beat. Revised 2026-11-27 (owner): the spoken ending "...The outline's going. Let it." is cut; the message
stays on the heart. The outline fades in the calm silence after "It's just calm."; he notices with a gesture only (his
palm touches the glass where it was, then goes flat to his own chest) and says the last line with his hand there.
Heartbeat = `heart_phone` (mid-range thump that reads on phone speakers). One continuous shot.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
import hand_outline as HO
from nigel import (P, SKY, Track, mood_vec, KNOCK, STAND, CHEST, smooth)

N.setup()
T, TE = N.T, N.TE

t_shh, t_put, t_chest, t_ive, t_ear, t_hear, t_listen = T("shh"), T("put"), TE("chest"), T("i've"), T("ear"), T("hear"), T("listen")
t_slowing, t_dont1, t_dont2, t_been, t_through, t_kept = T("slowing"), T("don't"), T("don't", 2), T("been"), T("through"), T("kept")
t_doing2, t_quieter, t_isnt, t_calm, t_your_heart, t_end = (
    T("doing", 2), T("quieter"), T("isn't"), TE("calm"), T("your", 4), TE("anything"))

# the heartbeat, heard through the glass: quick, then slowing, long gaps, then calm and steady
beats, b = [], t_hear + 0.1
while b < t_slowing:
    beats.append((b, 0.55)); b += 0.62
for gap in (0.8, 1.0, 1.25, 1.55, 1.85, 2.2, 2.5):          # "...Don't stop. ...Don't stop."
    beats.append((b, 0.55)); b += gap
while b < t_end - 1.2:                                       # calm, steady, a little quieter from "It's quieter."
    g = 0.5 if b < t_quieter else 0.32
    beats.append((b, g * (1 - 0.5 * smooth((b - t_your_heart) / 6.0)))); b += 1.05
BEAT_T = [x for x, _ in beats]

def pulse(t):
    """the outline swells a hair on each beat"""
    p = 0.0
    for bt in BEAT_T:
        if bt - 0.05 <= t <= bt + 0.6:
            d = t - bt
            p = max(p, math.exp(-((d - 0.06) / 0.07) ** 2) + 0.6 * math.exp(-((d - 0.33) / 0.07) ** 2))
    return p

fade = Track([(0, 1.0, 0), (t_calm - 1.5, 0.75, 1.5), (t_calm + 0.2, 0.0, 2.4)])   # it goes, in the calm silence

# ------------------------------------------------------------------ poses
TO_US = P(STAND, look=(0.0, 0.0), swing=0.0)
HUSH = P(STAND, look=(0.0, 0.05), eyescale=1.08, tilt=-0.02, swing=0.0)
HAND_CHEST = P(CHEST, look=(0.0, 0.1), swing=0.0)
EAR = P(CHEST, head=(478, 790), neck=(460, 950), tilt=0.3, look=(0.3, 0.2), shut=1.0, swing=0.0)     # ear to the glass
EAR_OPEN = P(EAR, shut=0.0, look=(0.15, 0.1), eyescale=1.18)                                       # fear: eyes open
EAR_SOFT = P(EAR, shut=1.0, tilt=0.26)
EAR_US = P(EAR, shut=0.0, look=(-0.15, 0.0), eyescale=1.04, tilt=0.24)
UP = P(CHEST, look=(0.55, 0.45), tilt=0.06, eyescale=1.06, swing=0.0)                              # straightens, watches it go
TOUCH = P(STAND, relb=HO.HAND["relb"], rhand=HO.HAND["rhand"], palm=HO.HAND["palm"] * 0.82, look=(0.55, 0.45),
          tilt=0.07, eyescale=1.08, swing=0.0)                                                       # palm where it was
LAST = P(CHEST, look=(0.0, 0.0), tilt=0.02, eyescale=1.02, swing=0.0)                               # hand on his chest

pose_track = Track([
    (0, KNOCK, 0),
    (t_shh - 0.3, HUSH, 0.6),                      # "Shh."
    (t_put - 0.2, HAND_CHEST, 1.0),                # "Put your hand on your chest."
    (t_ive - 0.2, EAR, 1.6),                       # leans his ear onto the glass where his hand was
    (t_slowing - 0.2, EAR_OPEN, 0.7),              # "...It's slowing down." — eyes open
    (t_been, EAR_SOFT, 1.4),                       # calmer: eyes shut again
    (t_doing2 - 0.3, EAR_US, 1.0),                 # "It's doing it now, under your hand."
    (t_quieter - 0.3, EAR_SOFT, 1.0),
    (t_calm - 0.1, UP, 1.3),                       # calm: he lifts his head off the glass; the outline is going
    (t_calm + 2.0, TOUCH, 0.9),                    # his palm touches the glass where it was
    (t_your_heart - 1.1, LAST, 1.0),               # then flat to his own chest
])                                                 # "Your heart has never once asked you for anything." (hand there)
x_track = Track([(0, 0.0, 0)])

def lean_cam(z, dx=0.0, dy=0.0):
    """a camera that puts his tilted head right up against the outline on the glass: his ear at its edge"""
    hx, hy = EAR["head"]
    return (hx - (395 + dx - 540) / z, hy - (1010 + dy - 960) / z, z)

cam_track = Track([                                          # ONE continuous shot
    (0, (470, 880, 1.6), 0),
    (t_put - 0.3, (480, 940, 1.4), 2.0),                     # his hand going to his chest; the outline on the glass
    (t_ive - 0.2, lean_cam(1.5), 2.6),                       # he leans in; his head comes over the outline
    (t_hear + 0.4, lean_cam(1.68), 6.0),                     # creeping in while the heart is fast
    (t_been, lean_cam(1.55), 6.0),                           # easing back as it calms
    (t_doing2 - 0.4, lean_cam(1.62, 10, 10), 5.0),
    (t_calm - 0.4, HO.CAM, 2.2),                             # he straightens; the outline goes; his palm finds the spot
    (t_your_heart - 0.6, (480, 905, 1.62), 3.0),             # easing in on him, hand on his chest, for the last line
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_shh, mood_vec("drifting"), 1.0),
    (t_hear, mood_vec("awe"), 1.2),
    (t_slowing, mood_vec("unease"), 0.8),
    (t_been, mood_vec("melancholy"), 2.0),
    (t_kept, mood_vec("warm"), 2.0),
    (t_quieter, mood_vec("drifting"), 1.5),
    (t_calm + 0.5, mood_vec("lonely"), 1.5),
    (t_your_heart - 0.8, mood_vec("warm"), 1.5),
])

NIGHT = dict(top=(14, 18, 48), bot=(40, 40, 82), clouds=0.1, cloud_v=0.5, stars=0.7, sun=0.0, sun_y=0.3, sun_r=24)
sky = Track([(0, SKY(**NIGHT, drone=0.12), 0), (t_shh, SKY(**NIGHT, drone=0.0), 1.0),
             (t_calm, SKY(**NIGHT, drone=0.06), 2.0)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

def glass(cr, t, pose, env, to_screen):
    N._palm["pos"] = None
    a = fade.at(t)
    HO.draw(cr, progress=1.0, scale=0.82 * (1 + 0.012 * pulse(t) * a), alpha=a, t=t)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track, tally_base=52, glass_hook=glass,
            sfx=[(bt, "heart_phone", g) for bt, g in beats], caption_avoid=[(0, 99, HO.caption_box(cam_track, 0.82))])
N.BLINKS = [b for b in N.BLINKS if not (t_ive < b < t_slowing or t_been < b < t_doing2 or t_quieter < b < t_your_heart)]
N.main("nigel_bane_ep052_slowing.mp4")
