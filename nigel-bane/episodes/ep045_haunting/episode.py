"""Day 45 — "haunting" (posts as `… IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII haunting`). Keeper arc 2/4;
written in the owner's hard reset (2026-11-22). THE LINE: "Somewhere, a stranger has made up a face for you. ...It
probably isn't yours." Grey morning. The lamp from yesterday stands dark on the floor, tag "for nigel". C (plain):
"Come closer. Closer." — he leans toward us, and the camera comes closer. "...Look under here." — he lifts the lamp and
turns it upside down: a name is scratched into the underside of the base, worn almost flat. T: the name — can it be
read? His thumb rubs it slowly (the close sound); it never resolves. Salad-Fingers tenderness: "I like touching it.
It's worn so smooth." Poppy flatness: "I've decided they had a kind one." Bridge: he'll never see the face of whoever
owned this lamp -> if you've ever left a home, someone lives there now and once wondered about you. ENDING: he holds
the lamp against his cheek, eyes half-lidded, and whispers the last line to us. One continuous shot.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import cairo
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, STAND)

N.setup()
T, TE = N.T, N.TE
F = N.FLOOR_Y
OFFX = 40.0                                   # kneeling a little to the right, beside the lamp

t_come, t_closer2, t_look, t_lamp, t_name, t_not, t_mine = T("come"), T("closer", 2), T("look"), T("lamp"), T("name"), T("not"), T("mine")
t_like, t_worn, t_smooth, t_they, t_ill, t_decided, t_kind = T("like"), T("worn"), T("smooth"), T("they"), T("i'll"), T("decided"), T("kind")
t_youre, t_if, t_found, t_pencil, t_and, t_wondered, t_you5 = T("you're"), T("if"), T("found"), T("pencil"), T("and"), T("wondered"), TE("you", 2)
t_somewhere, t_it_last, t_end = T("somewhere"), T("probably"), TE("yours")

LIFT0 = t_look - 0.1                          # he lifts the lamp and turns it over
CHEEK0 = t_you5 + 0.25                        # ...and holds it against his cheek

# ------------------------------------------------------------------ the lamp: (pivot x, pivot y, rotation)
# pivot = the middle of the stem. Upright on the floor the base sits on the floor line.
FLOOR_PIV = (700.0, F - 10 - 145.0, 0.0)
HELD = (768.0, 1326.0, 2.25)                 # tipped over on a diagonal: base up toward him and us, shade down by the floor
CHEEK = (703.0, 1340.0, 2.25)                 # lifted a touch, so his cheek can rest on the base
lamp_tr = Track([(0, FLOOR_PIV, 0), (LIFT0, HELD, 1.5), (CHEEK0, CHEEK, 1.4)])

def R(rot, x, y):
    c, s = math.cos(rot), math.sin(rot)
    return (x * c - y * s, x * s + y * c)
def lamp_pt(t, lx, ly):
    """a point given in the lamp's own frame (pivot origin, upright), in world space"""
    px, py, rot = lamp_tr.at(t)
    dx, dy = R(rot, lx, ly)
    return (px + dx, py + dy)

NAME = [[(-34, 1), (-31, -5), (-28, 3), (-25, -6), (-21, 2), (-18, -4), (-14, 3)],      # a scrawl, worn almost flat
        [(-8, -6), (-6, 3), (-2, -3), (2, 4), (5, -5)],
        [(11, 2), (14, -6), (18, 3), (22, -4), (26, 2), (31, -3)]]

def draw_lamp(cr, t, pose, env):
    px, py, rot = lamp_tr.at(t)
    flip = abs(math.sin(rot / 2.0))               # 0 upright .. 1 upside down: how much of the base's underside we see
    cr.save()
    cr.translate(px, py); cr.rotate(rot)
    # stem
    N.path(cr, N.sketch_pts([(0, 145), (0, -45)], amp=0.8, sid=510, step=12)); N.stroke_ink(cr, 4.0, alpha=0.95)
    # shade (dark, unlit)
    shade = [(-52, -145), (52, -145), (84, -45), (-84, -45)]
    cr.move_to(*shade[0]); [cr.line_to(*q) for q in shade[1:]]; cr.close_path()
    cr.set_source_rgba(0.95, 0.94, 0.9, 1.0); cr.fill()
    for a, b in ((shade[0], shade[1]), (shade[1], shade[2]), (shade[2], shade[3]), (shade[3], shade[0])):
        N.path(cr, N.sketch_pts([a, b], amp=1.0, sid=500 + int(a[0]) % 7, step=14)); N.stroke_ink(cr, 3.4, alpha=0.9)
    # base: a disc; turned over, more of its underside faces us
    ry = 18 + 22 * flip
    cr.save(); cr.translate(0, 145); cr.scale(1, ry / 58.0)
    N.path(cr, N.circle_pts(0, 0, 58, sid=511)); cr.restore()
    cr.set_source_rgba(0.95, 0.94, 0.9, 1.0); cr.fill_preserve(); N.stroke_ink(cr, 3.6, alpha=0.95)
    cr.restore()
    if flip > 0.6:                                # the scratched name on the underside, worn faint
        a = min(1.0, (flip - 0.6) / 0.3) * 0.75
        cr.save(); cr.translate(px, py); cr.rotate(rot); cr.translate(0, 145)
        cr.rotate(math.pi)                         # the scrawl runs the right way for us when the lamp is tipped over
        cr.scale(1.0, (ry / 58.0) * 1.3)
        for k, stroke in enumerate(NAME):
            N.path(cr, N.sketch_pts(stroke, amp=0.5, sid=530 + k, step=4)); N.stroke_ink(cr, 1.4, alpha=a * 0.7)
        cr.restore()
    # the tag hangs from the shade's rim on its string, always straight down
    rim = lamp_pt(t, 80, -50) if math.cos(rot) > 0 else lamp_pt(t, 82, -142)
    rim = (rim[0], min(rim[1], F - 8))
    sw = 0.08 * math.sin(t * 1.3)
    tx, ty = rim[0] + 6 + 20 * math.sin(sw), min(rim[1] + 50, F - 30)   # it rests on the floor rather than hang through it
    N.path(cr, N.sketch_pts([rim, (tx - 2, ty - 16)], amp=0.6, sid=512, step=6)); N.stroke_ink(cr, 1.5, alpha=0.75)
    N.draw_tag(cr, tx + 10, ty, ang=1.45 + sw, scale=0.75, flip=1.0, string=False, sid=513)

# ------------------------------------------------------------------ poses
KNEEL = P(STAND, head=(430, 1120), neck=(445, 1240), hip=(470, 1390), lknee=(420, 1470), lfoot=(560, 1476),
          rknee=(450, 1468), rfoot=(590, F), lelb=(400, 1330), lhand=(380, 1440),
          relb=(520, 1330), rhand=(560, 1420), tilt=0.1, look=(0.2, 0.6), swing=0.0)
LEAN_US = P(KNEEL, head=(450, 1100), look=(0.0, 0.0), eyescale=1.12, tilt=0.02)     # "Come closer." — leaning toward us
AT_LAMP = P(KNEEL, look=(0.8, 0.4), tilt=0.14)
HOLD = P(KNEEL, look=(0.75, 0.15), tilt=0.12)                                       # hands are pinned to the lamp below
HOLD_US = P(KNEEL, look=(0.05, 0.0), tilt=0.06)
HOLD_FLAT = P(KNEEL, look=(0.0, 0.05), tilt=0.0, eyescale=0.98)
CHEEK_P = P(KNEEL, head=(440, 1140), neck=(447, 1252), tilt=0.2, look=(0.15, 0.1), shut=0.45)   # cheek down on the lamp's base, heavy-lidded
CHEEK_US = P(CHEEK_P, shut=0.0, look=(-0.05, -0.3), eyescale=0.98)    # eyes up and clear of the base

pose_track = Track([
    (0, KNOCK, 0),
    (t_come - 0.6, LEAN_US, 1.0),                 # already kneeling, leaning in to us
    (t_look - 0.5, AT_LAMP, 0.6),
    (LIFT0 + 0.3, HOLD, 1.2),
    (t_not - 0.3, HOLD_US, 0.6),                  # "Not mine." — to us
    (t_like - 0.4, HOLD, 0.8),                    # thumb on the name
    (t_ill - 0.3, HOLD_FLAT, 0.9),                # "I'll never see their face." — flat, to us
    (t_youre - 0.4, HOLD_US, 0.8),
    (CHEEK0, CHEEK_P, 1.4),                       # the lamp to his cheek
    (t_it_last - 0.6, CHEEK_US, 0.8),             # eyes open on us for the whisper
])

def hands(t, p):
    """once he has the lamp, his hands stay on it: left hand on the stem by the shade, right hand by the base; while he
    talks about the name his right thumb rubs slowly across it"""
    w = min(1.0, max(0.0, (t - LIFT0) / 0.45))
    if w <= 0:
        return p
    lh = lamp_pt(t, -10, 105)                     # near the base
    rh = lamp_pt(t, 12, 30)                       # on the stem, toward the shade
    if t_like - 0.3 < t < t_they + 0.2:            # thumb on the name: rubs back and forth, slowly
        k = min(1.0, (t - t_like + 0.3) / 0.5) * min(1.0, (t_they + 0.2 - t) / 0.5)
        target = lamp_pt(t, 14 * math.sin((t - t_like) * 2.6), 150)
        lh = (lh[0] + k * (target[0] - lh[0]), lh[1] + k * (target[1] - lh[1]))
    for hand, elb, h in (("lhand", "lelb", lh), ("rhand", "relb", rh)):
        x = p[hand][0] + w * (h[0] - p[hand][0]); y = p[hand][1] + w * (h[1] - p[hand][1])
        p[hand] = (x, y)
        side = -1 if hand == "lhand" else 1
        p[elb] = ((p["neck"][0] + x) / 2 + side * 18, max(p["neck"][1] + 40, (p["neck"][1] + y) / 2 + 55))
    return p

x_track = Track([(0, 0.0, 0), (t_come - 0.7, OFFX, 1.0)])

cam_track = Track([                                        # ONE continuous shot
    (0, (470, 880, 1.6), 0),
    (t_come - 0.3, (620, 1200, 1.25), 1.4),                # down to him, kneeling by the lamp
    (t_closer2 - 0.2, (600, 1180, 1.6), 1.2),              # "Closer." — we come closer
    (LIFT0 + 0.2, (640, 1160, 1.5), 1.6),                  # the lamp comes up into his hands
    (t_name - 0.4, (660, 1235, 2.5), 1.8),                 # in on the scratched name
    (t_not - 0.2, (600, 1140, 1.75), 1.0),                 # "Not mine." — his face and the lamp
    (t_like - 0.3, (650, 1235, 2.4), 1.6),                 # the thumb on the name
    (t_ill - 0.4, (560, 1150, 1.6), 1.6),                  # his face: "I'll never see their face."
    (t_youre - 0.5, (540, 1130, 1.95), 2.0),               # the turn, close
    (t_if - 0.2, (590, 1190, 1.3), t_and - t_if),          # slow drift back through the scene
    (t_and, (570, 1140, 1.7), CHEEK0 - t_and + 0.8),       # push in again
    (CHEEK0 + 0.8, (560, 1200, 1.9), t_end - CHEEK0),      # his cheek on the lamp, close, to the end
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_come, mood_vec("drifting"), 1.0),
    (t_name, mood_vec("uncanny"), 1.0),
    (t_like, mood_vec("warm"), 1.5),
    (t_ill, mood_vec("drifting"), 1.2),
    (t_youre, mood_vec("melancholy"), 1.5),
    (t_and, mood_vec("lonely"), 1.5),
    (t_somewhere, mood_vec("uncanny"), 1.2),
])

GREY = dict(top=(150, 158, 170), bot=(198, 200, 205), clouds=0.8, cloud_v=0.8, sun=0.0, sun_y=0.3, sun_r=24)
sky = Track([(0, SKY(**GREY, drone=0.12), 0), (t_come, SKY(**GREY, drone=0.0), 0.8),
             (t_youre, SKY(**GREY, drone=0.08), 2.0), (t_somewhere, SKY(**GREY, drone=0.0), 1.5)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

RUBS = []
_t = t_like + 0.1
while _t < t_they - 0.2:
    RUBS.append((_t, "scratch", 0.08)); _t += 1.2       # the thumb over the scratches: soft, every pass

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track, tally_base=44, draw_hook=draw_lamp,
            pose_hook=hands, sfx=RUBS,
            caption_avoid=[(0, 99, lambda t: (lamp_tr.at(t)[0] - 110, lamp_tr.at(t)[1] - 190, lamp_tr.at(t)[0] + 150, lamp_tr.at(t)[1] + 190))])
N.main("nigel_bane_ep045_haunting.mp4")
