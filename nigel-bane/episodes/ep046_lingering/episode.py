"""Day 46 — "lingering" (posts as `… IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII I lingering`). Keeper arc
3/4; written in the owner's hard reset (2026-11-22). THE LINE: "You've been the best part of somebody's day. They never
told you. ...That's how it usually goes." Morning. The dead lamp stands on the floor (its old tag "for nigel" on the
right); a NEW paper tag hangs from the left of its shade, face down, and he is crouched with one fingertip under its
corner. C (plain): "Don't look away. I'm going to turn it over. ...Not yet." T: what does it say? He sniffs it first
("It smells like someone else's hands." — the Salad-Fingers beat), then turns it: "thank you." Poppy repetition:
"Thank you. ...Thank you." He doesn't know what for. Bridge: he's been thanked for something he can't remember ->
somebody kept a thing you said on your way out of a room. ENDING: he holds the tag flat against his cheek, eyes
heavy, and whispers it; eyes open on us for the last line. One continuous shot.
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
LAMP_X = 700.0
OFFX = 40.0

t_dont, t_turn, t_notyet, t_smells, t_hands, t_thank1, t_thank2 = T("don't"), T("turn"), T("not"), T("smells"), TE("hands"), T("thank"), T("thank", 2)
t_idk, t_ive, t_still, t_somebody, t_years, t_they, t_bad, t_youd = T("know"), T("i've"), T("still"), T("somebody"), T("years"), T("they"), T("bad"), T("you'd")
t_best, t_told, t_thats, t_end = T("best"), T("told"), T("that's"), TE("goes")
t_youve = t_best - 0.6

TURN0 = t_hands + 0.55                      # he turns it over in the held beat after "hands."
CHEEK0 = t_youve - 0.9                      # the tag comes up to his cheek

# ------------------------------------------------------------------ the new tag
ANCHOR = (LAMP_X - 80, F - 210)             # tied to the shade's lower-left rim
HANG = (ANCHOR[0] - 4, ANCHOR[1] + 74)
UNDER = (ANCHOR[0] - 12, ANCHOR[1] + 66)    # lifted a touch on his fingertip
SNIFF = (ANCHOR[0] - 40, ANCHOR[1] + 22)    # up toward his face for the sniff
READ = (ANCHOR[0] - 30, ANCHOR[1] + 18)     # held up flat to read
tag_xy = Track([(0, HANG, 0), (t_dont - 0.4, UNDER, 0.8), (t_smells - 0.5, SNIFF, 0.9), (TURN0 - 0.1, READ, 0.6),
                (t_ive - 0.2, UNDER, 1.2)])
tag_ang = Track([(0, 1.45, 0), (t_smells - 0.5, 0.6, 0.9), (TURN0 - 0.1, 0.08, 0.6), (t_ive - 0.2, 1.2, 1.2)])
tag_flip = Track([(0, 0.0, 0), (TURN0, 1.0, 0.9)])
cheek_w = Track([(0, 0.0, 0), (CHEEK0, 1.0, 1.3)])

def tag_pos(t, pose):
    """where the tag is: on its string by the lamp, or (at the end) pressed flat to his right cheek"""
    x, y = tag_xy.at(t)
    w = cheek_w.at(t)
    if w > 0 and pose is not None:
        hx, hy = pose["head"]
        cx, cy = hx + 98, hy + 120                    # on the jaw, below the eye
        x, y = x + w * (cx - x), y + w * (cy - y)
    return x, y, tag_ang.at(t) * (1 - w) + 0.18 * w

_last_pose = {}
def draw_lamp_and_tags(cr, t, pose, env):
    """the dead lamp (shade, stem, base) and its old tag, under Nigel"""
    x = LAMP_X
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
    px, py = x + 70, sh_bot - 4                                # the old tag, "for nigel", on the right
    sw = 0.08 * math.sin(t * 1.3)
    tx, ty = px + 10 + 30 * math.sin(sw), py + 52
    N.path(cr, N.sketch_pts([(px, py), (tx - 2, ty - 16)], amp=0.6, sid=512, step=6)); N.stroke_ink(cr, 1.5, alpha=0.75)
    N.draw_tag(cr, tx + 12, ty, ang=1.45 + sw, scale=0.75, flip=1.0, string=False, sid=513)

def draw_new_tag(cr, t, pose, env):
    """the new tag and its string, over Nigel (it's in his fingers)"""
    x, y, ang = tag_pos(t, pose)
    sway = 0.05 * math.sin(t * 1.1) * (1 - cheek_w.at(t))
    hole = (x - 34 * math.cos(ang + sway) * 1.15, y - 34 * math.sin(ang + sway) * 1.15)
    mid = ((ANCHOR[0] + hole[0]) / 2 - 6, max(ANCHOR[1], hole[1]) + 10)
    N.path(cr, N.sketch_pts([ANCHOR, mid, hole], amp=0.6, sid=540, step=8)); N.stroke_ink(cr, 1.5, alpha=0.75)
    N.draw_tag(cr, x, y, ang=ang + sway, scale=1.3, flip=tag_flip.at(t), text="thank you.", string=False, sid=541)

# ------------------------------------------------------------------ poses
KNEEL = P(STAND, head=(430, 1120), neck=(445, 1240), hip=(470, 1390), lknee=(420, 1470), lfoot=(560, 1476),
          rknee=(450, 1468), rfoot=(590, F), lelb=(400, 1330), lhand=(380, 1440),
          relb=(520, 1330), rhand=(560, 1420), tilt=0.1, look=(0.2, 0.6), swing=0.0)
TO_US = P(KNEEL, look=(0.0, 0.0), tilt=0.04, eyescale=1.04)
AT_TAG = P(KNEEL, look=(0.8, 0.5), tilt=0.16)
SNIFFP = P(KNEEL, head=(468, 1132), neck=(452, 1246), look=(0.7, 0.35), tilt=0.22, shut=0.6)   # eyes half shut, sniffing
READP = P(KNEEL, look=(0.75, 0.25), tilt=0.12, eyescale=1.1)
FLAT = P(KNEEL, look=(0.0, 0.05), tilt=0.0, eyescale=0.98)
CHEEKP = P(KNEEL, head=(440, 1124), tilt=0.24, look=(0.1, 0.05), shut=0.5)
CHEEK_US = P(CHEEKP, shut=0.0, look=(0.0, -0.1), eyescale=1.02)

pose_track = Track([
    (0, KNOCK, 0),
    (t_dont - 0.6, TO_US, 1.0),                  # crouched, fingertip under the tag's corner, eyes on us
    (t_notyet - 0.2, AT_TAG, 0.7),
    (t_smells - 0.5, SNIFFP, 0.9),                # sniffs it
    (TURN0, READP, 0.6),                          # turns it: "thank you."
    (t_idk - 0.3, FLAT, 0.7),                     # "I don't know what I did." — flat, to us
    (t_somebody - 0.4, TO_US, 1.0),
    (CHEEK0, CHEEKP, 1.3),                        # tag flat to his cheek
    (t_thats - 0.5, CHEEK_US, 0.8),               # eyes open on us
])

def fingers(t, p):
    """his right hand holds the tag wherever it goes (fingertip under its corner, up to sniff and read, to his cheek)"""
    x, y, ang = tag_pos(t, p)
    w = min(1.0, max(0.0, (t - (t_dont - 0.6)) / 0.6))
    hx, hy = x + 38 * math.cos(ang) + 6, y + 38 * math.sin(ang) + 12
    p["rhand"] = (p["rhand"][0] + w * (hx - p["rhand"][0]), p["rhand"][1] + w * (hy - p["rhand"][1]))
    p["relb"] = ((p["neck"][0] + p["rhand"][0]) / 2 + 20, max(p["neck"][1] + 50, (p["neck"][1] + p["rhand"][1]) / 2 + 60))
    return p

x_track = Track([(0, 0.0, 0), (t_dont - 0.7, OFFX, 1.0)])

cam_track = Track([                                        # ONE continuous shot
    (0, (470, 880, 1.6), 0),
    (t_dont - 0.4, (600, 1220, 1.4), 1.6),                 # down to him: the lamp, the face-down tag on his fingertip
    (t_smells - 0.5, (580, 1160, 1.9), 1.4),               # the sniff, close
    (TURN0 - 0.1, (610, 1125, 3.0), 1.0),                  # in on the tag as it turns: "thank you."
    (t_idk - 0.3, (540, 1150, 1.7), 1.2),                  # his face
    (t_somebody - 0.5, (560, 1180, 1.3), 2.0),             # ease out for the story
    (t_years, (540, 1150, 1.55), t_youd - t_years),        # slow push on him
    (CHEEK0, (530, 1130, 2.0), t_end - CHEEK0 + 0.3),      # close: the tag at his cheek
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_dont, mood_vec("unease"), 1.0),
    (t_smells, mood_vec("drifting"), 1.0),
    (TURN0 + 0.4, mood_vec("awe"), 0.8),
    (t_idk, mood_vec("uncanny"), 1.0),
    (t_somebody, mood_vec("warm"), 1.5),
    (t_they, mood_vec("melancholy"), 1.5),
    (t_best, mood_vec("warm"), 1.5),
    (t_thats, mood_vec("lonely"), 1.0),
])

MORN = dict(top=(176, 198, 222), bot=(236, 222, 206), clouds=0.5, cloud_v=1.0, sun=0.5, sun_y=0.62, sun_r=26)
sky = Track([(0, SKY(**MORN, drone=0.12), 0), (t_dont, SKY(**MORN, drone=0.0), 0.8),
             (t_somebody, SKY(**MORN, drone=0.07), 2.0), (t_best, SKY(**MORN, drone=0.0), 1.5)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track, tally_base=45,
            under_hook=draw_lamp_and_tags, draw_hook=draw_new_tag, pose_hook=fingers,
            sfx=[(TURN0 + 0.2, "scratch", 0.12)],
            caption_avoid=[(0, 99, lambda t: (LAMP_X - 160, F - 320, LAMP_X + 160, F + 20))])
N.main("nigel_bane_ep046_lingering.mp4")
