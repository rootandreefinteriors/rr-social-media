"""Day 47 — "carrying" (posts as `… IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII II carrying`). Keeper arc
4/4, the lamp's exit; written in the owner's hard reset (2026-11-22). THE LINE: "And one night... they carried you for
the last time. ... Nobody knew it was the last one. Not even them." Night. He sits on the floor against the wall beside
the dead lamp (its two tags: "for nigel", "thank you."), pinching his own cheek to stay awake. C (plain): "Stay up with
me. I want to see who comes in." T (visible yes/no): will he stay awake? His eyelids sink and he jerks up ("...I'm not
sleepy."), then sink further all through the story. Bridge: whoever keeps this room only comes while he's asleep ->
somebody carried you in from the car while you slept, and one night was the last. His eyes close on "Not even them.";
the camera eases out; the lamp rises slowly, up and out of the top of the frame, as if carried; dawn comes up in the
window. He wakes to the empty floor: "...They came. I didn't feel a thing." One continuous shot.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import cairo
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, SIT)

N.setup()
T, TE = N.T, N.TE
F = N.FLOOR_Y
LAMP_X = 770.0
OFFX = -60.0

t_stay, t_want, t_they, t_not, t_sleepy, t_when = T("stay"), T("want"), T("they"), T("not"), TE("sleepy"), T("when", 2)
t_somebody, t_up, t_shoes, t_sometimes, t_and2, t_last, t_youd = T("somebody"), T("up", 2), T("shoes"), T("sometimes"), T("and", 2), T("last"), T("you'd")
t_nobody2, t_noteven, t_them_end, t_came, t_i_last, t_end = T("nobody", 2), T("not", 2), TE("them"), T("they", 3), T("didn't"), TE("thing")

SINK0 = t_sleepy + 0.25          # eyelids sink after "I'm not sleepy."
JERK = t_when - 0.75             # ...and he jerks upright
SLEEP = t_them_end + 0.25        # asleep on "Not even them."
LIFT0, LIFT1 = SLEEP + 1.4, t_came - 1.4     # the lamp rises out of the frame while he sleeps
WAKE = t_came - 0.9

# ------------------------------------------------------------------ poses (sitting on the floor, back to the wall)
SITP = P(SIT, head=(440, 1004), tilt=0.03, look=(0.0, 0.0))
PINCH = P(SITP, relb=(586, 1178), rhand=(606, 1082), shut=0.15, look=(0.05, 0.05))     # pinching his own cheek
AT_LAMP = P(SITP, look=(0.85, 0.2), tilt=0.08, shut=0.15)
DROWSY1 = P(SITP, shut=0.35, look=(0.0, 0.1))
SINKING = P(SITP, head=(446, 1022), tilt=0.12, shut=0.92, look=(0.0, 0.3))
JERKED = P(SITP, head=(440, 996), tilt=-0.02, shut=0.0, eyescale=1.14, look=(0.0, -0.05))
DROWSY2 = P(SITP, shut=0.45, look=(0.0, 0.15), tilt=0.05)
DROWSY3 = P(SITP, head=(444, 1012), shut=0.62, look=(0.0, 0.2), tilt=0.1)
DROWSY4 = P(SITP, head=(448, 1020), shut=0.78, look=(0.0, 0.25), tilt=0.16)
ASLEEP = P(SITP, head=(458, 1048), neck=(458, 1190), tilt=0.38, shut=1.0, look=(0.0, 0.4))
WOKEN = P(SITP, shut=0.0, eyescale=1.1, look=(0.85, 0.45), tilt=0.1)                   # the empty floor where it was
TO_US = P(SITP, shut=0.0, look=(0.0, 0.0), eyescale=1.04, tilt=0.03)

pose_track = Track([
    (0, KNOCK, 0),
    (t_stay - 0.8, PINCH, 1.0),                   # sitting against the wall, pinching his cheek
    (t_want, AT_LAMP, 0.8),                       # "I want to see who comes in."
    (t_they - 0.2, DROWSY1, 0.9),
    (SINK0, SINKING, 1.1),                        # the lids sink...
    (JERK, JERKED, 0.25),                         # ...he jerks upright
    (t_when + 0.6, DROWSY2, 3.0),
    (t_shoes, PINCH, 0.8),                        # another pinch, mid-story
    (t_sometimes - 0.3, DROWSY3, 2.0),
    (t_and2 - 0.3, DROWSY4, 2.5),                 # "And one night..."
    (t_noteven - 0.2, ASLEEP, 1.4),               # "Not even them." — asleep
    (WAKE, WOKEN, 0.55),                          # wakes: the floor is empty
    (t_i_last - 0.6, TO_US, 0.8),
])
x_track = Track([(0, 0.0, 0), (t_stay - 0.9, OFFX, 1.0)])

# ------------------------------------------------------------------ the lamp, and its lift
lift = Track([(0, 0.0, 0), (LIFT0, 1.0, LIFT1 - LIFT0)])
def draw_lamp(cr, t, pose, env):
    u = lift.at(t)
    if u > 0.999:
        return
    dy = -u * 1900                                     # up and out of the top of the frame
    rot = 0.05 * math.sin(u * math.pi * 2.0) * u        # a slight sway as it goes, like something carried
    x = LAMP_X
    cr.save(); cr.translate(x, F - 10 + dy); cr.rotate(rot); cr.translate(-x, -(F - 10))
    sh_top, sh_bot = F - 300, F - 200
    shade = [(x - 52, sh_top), (x + 52, sh_top), (x + 84, sh_bot), (x - 84, sh_bot)]
    cr.move_to(*shade[0]); [cr.line_to(*q) for q in shade[1:]]; cr.close_path()
    cr.set_source_rgba(0.95, 0.94, 0.9, 1.0); cr.fill()
    for a, b in ((shade[0], shade[1]), (shade[1], shade[2]), (shade[2], shade[3]), (shade[3], shade[0])):
        N.path(cr, N.sketch_pts([a, b], amp=1.0, sid=500 + int(a[0]) % 7, step=14)); N.stroke_ink(cr, 3.4, alpha=0.9)
    N.path(cr, N.sketch_pts([(x, sh_bot), (x, F - 22)], amp=0.8, sid=510, step=12)); N.stroke_ink(cr, 4.0, alpha=0.9)
    cr.save(); cr.translate(x, F - 10); cr.scale(1, 0.32)
    N.path(cr, N.circle_pts(0, 0, 58, sid=511)); cr.restore()
    cr.set_source_rgba(0.95, 0.94, 0.9, 1.0); cr.fill_preserve(); N.stroke_ink(cr, 3.6, alpha=0.9)
    sw = 0.08 * math.sin(t * 1.3) + 0.25 * u                      # tags swing more as it rises
    px, py = x + 70, sh_bot - 4                                    # "for nigel", on the right
    tx, ty = px + 10 + 30 * math.sin(sw), py + 52
    N.path(cr, N.sketch_pts([(px, py), (tx - 2, ty - 16)], amp=0.6, sid=512, step=6)); N.stroke_ink(cr, 1.5, alpha=0.75)
    N.draw_tag(cr, tx + 12, ty, ang=1.45 + sw, scale=0.75, flip=1.0, string=False, sid=513)
    ax, ay = x - 80, F - 210                                       # "thank you.", on the left
    hx, hy = ax - 4 - 20 * math.sin(sw), ay + 70
    N.path(cr, N.sketch_pts([(ax, ay), (hx, hy - 30)], amp=0.6, sid=540, step=8)); N.stroke_ink(cr, 1.5, alpha=0.75)
    N.draw_tag(cr, hx, hy, ang=1.45 - sw, scale=0.95, flip=1.0, text="thank you.", string=False, sid=541)
    cr.restore()

cam_track = Track([                                        # ONE continuous shot
    (0, (470, 880, 1.6), 0),
    (t_stay - 0.6, (560, 1150, 1.35), 2.0),                # down to him on the floor, the lamp beside him
    (t_want + 0.3, (600, 1160, 1.15), 1.8),                # the lamp, the empty room he's watching
    (t_they, (430, 1060, 1.7), 2.4),                       # his face, drowsy
    (t_when, (450, 1080, 1.45), 2.0),                      # the story: a slow push in over it
    (t_somebody, (430, 1050, 1.95), t_nobody2 - t_somebody),
    (SLEEP - 0.3, (600, 900, 0.8), 3.4),                   # asleep: ease right out — the lamp, the window
    (WAKE - 0.6, (520, 1090, 1.5), 2.4),                   # back in as he wakes
    (t_i_last - 0.2, (430, 1050, 1.8), t_end - t_i_last + 0.3),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_stay, mood_vec("unease"), 1.0),
    (t_they, mood_vec("drifting"), 1.5),
    (JERK, mood_vec("unease"), 0.3),
    (t_when, mood_vec("warm"), 2.0),
    (t_and2, mood_vec("melancholy"), 2.0),
    (t_noteven, mood_vec("lonely"), 1.0),
    (WAKE, mood_vec("awe"), 0.6),
    (t_i_last, mood_vec("uncanny"), 1.0),
])

NIGHT = dict(top=(14, 18, 48), bot=(40, 40, 82), clouds=0.1, cloud_v=0.5, stars=0.7, sun=0.0, sun_y=0.3, sun_r=24)
DAWN = dict(top=(120, 140, 190), bot=(240, 190, 160), clouds=0.4, cloud_v=0.8, stars=0.0, sun=0.6, sun_y=0.82, sun_r=28)
sky = Track([(0, SKY(**NIGHT, drone=0.14), 0), (t_stay, SKY(**NIGHT, drone=0.06), 1.0),
             (SLEEP, SKY(**NIGHT, drone=0.0), 1.0), (SLEEP + 1.0, SKY(**DAWN, drone=0.0), WAKE - SLEEP - 0.8),
             (WAKE, SKY(**DAWN, drone=0.05), 1.0)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track, tally_base=46, under_hook=draw_lamp,
            caption_avoid=[(0, 99, lambda t: (LAMP_X - 130, F - 330 - lift.at(t) * 1900, LAMP_X + 160, F + 20 - lift.at(t) * 1900))])
N.BLINKS = [b for b in N.BLINKS if not (SINK0 - 0.3 < b < JERK + 0.5) and not (SLEEP - 1.5 < b < WAKE + 0.8)]
N.main("nigel_bane_ep047_carrying.mp4")
