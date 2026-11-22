"""Day 43 — remade 2026-11-22 after the owner's hard reset (posts as `… IIIII IIIII III unwatching`). Room arc 4/4, the
room comes back to its size. THE LINE: "Most things get better while you aren't looking. ...That's why it never feels
like they are." The room is still as narrow as the window, the ceiling low on the window frame. C (plain): "I'm going to
shut my eyes. You keep yours open. Watch the walls for me." T (visible yes/no): the walls and ceiling drift outward
only while his eyes are shut; he peeks with ONE eye and everything stops dead ("It stops when I look."). Eyes shut
again, he feels his way to the right wall and lays his palm on it as it slides away under his hand ("I like it when it
moves. It feels like breathing."). Bridge: the room only grows when he isn't looking -> a cut, grief, the person you
couldn't stop thinking about all get better on the days you don't check. He opens his eyes in the full-size room for
the last two lines. One continuous shot; one whispered stretch; the featured close sound is the wall sliding under his
palm (a soft scrape).
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, STAND, OPEN)

N.setup()
T, TE = N.T, N.TE
F = N.FLOOR_Y

OFF = 390.0                         # under the window: body centre x 840
OFF2 = 470.0                        # a small shuffle toward the right wall, eyes shut

t_shut, t_eyes, t_you, t_watch, t_me = T("shut"), T("eyes"), T("you"), T("watch"), T("me")
t_are, t_moving, t_stops, t_always, t_like = T("are"), T("moving"), T("stops"), T("always"), T("like")
t_feels, t_breath, t_cut, t_grief, t_person = T("feels"), T("breathing"), T("cut"), T("grief"), T("person")
t_morning2, t_most, t_thats, t_end = T("morning", 2), T("most"), T("that's"), TE("are", 2)

SHUT0 = t_eyes + 0.1                # "...shut my eyes." — they close on the word
PEEK0 = t_stops - 0.9               # one eye opens: the walls stop dead
SHUT1 = TE("look", 2) + 0.35        # after "It always stops when I look." — shut again
OPEN_END = t_most - 1.4             # in the full-size room, eyes open for the last two lines

# ---------------------------------------------------------------- the room: it only grows while his eyes are shut
GROW1 = t_me + 0.6
GROW2 = SHUT1 + 0.5
GROW_END = OPEN_END - 0.6
lw = Track([(0, 650.0, 0), (GROW1, 600.0, PEEK0 - GROW1 - 0.1), (GROW2, -520.0, GROW_END - GROW2)])
rw = Track([(0, 1030.0, 0), (GROW1, 1075.0, PEEK0 - GROW1 - 0.1), (GROW2, 2240.0, GROW_END - GROW2)])
ceil = Track([(0, 203.0, 0), (GROW1, 168.0, PEEK0 - GROW1 - 0.1), (GROW2, -760.0, GROW_END - GROW2)])

# ---------------------------------------------------------------- poses
CLOSED = P(STAND, shut=1.0, look=(0.0, 0.1), tilt=0.02, swing=0.0)
CLOSED_L = P(CLOSED, shut_l=1.0)        # around the peek the left eye never moves (no dip open mid-blend)
TO_US = P(STAND, look=(0.0, 0.0), eyescale=1.05, swing=0.0)
OFFER = P(OPEN, shut=1.0, look=(0.0, 0.1), swing=0.0)                          # "Watch the walls for me." — palms out
WHISPER = P(STAND, shut=1.0, shut_l=1.0, look=(0.0, 0.15), tilt=-0.06, relb=(520, 1090), rhand=(500, 1010), swing=0.0)
PEEK = P(STAND, shut=0.0, shut_l=1.0, look=(0.8, 0.0), eyescale=1.08, tilt=0.1, swing=0.0)       # one eye, at the wall
PEEK_US = P(STAND, shut=0.0, shut_l=1.0, look=(0.05, 0.0), eyescale=1.08, tilt=0.08, swing=0.0)  # one eye, at us
FEEL = P(STAND, shut=1.0, look=(0.3, 0.05), tilt=0.08, relb=(560, 1060), rhand=(640, 1000), swing=0.4)
PALM = P(STAND, shut=1.0, look=(0.35, 0.05), tilt=0.12, relb=(575, 1040), rhand=(680, 985), swing=0.0)
LETGO = P(STAND, shut=1.0, look=(0.1, 0.15), tilt=0.05, swing=0.0)
CLOSED_US = P(STAND, shut=1.0, look=(0.0, 0.05), tilt=-0.03, swing=0.0)
AROUND_L = P(STAND, look=(-0.85, -0.25), eyescale=1.12, swing=0.0)
AROUND_R = P(STAND, look=(0.85, -0.3), eyescale=1.12, swing=0.0)
LAST = P(STAND, look=(0.0, 0.0), eyescale=1.1, tilt=0.03, swing=0.0)

pose_track = Track([
    (0, KNOCK, 0),
    (t_shut - 0.5, TO_US, 0.7),
    (SHUT0, CLOSED, 0.5),
    (t_watch - 0.3, OFFER, 0.9),
    (t_are - 0.6, WHISPER, 0.8),
    (PEEK0, PEEK, 0.35),                       # one eye opens, on the wall: it stops dead
    (t_stops + 0.5, PEEK_US, 0.6),             # "It stops when I look." — to us, still one eye
    (SHUT1, CLOSED_L, 0.45),
    (GROW2 + 0.2, FEEL, 1.0),                  # feeling his way toward the right wall, eyes shut
    (t_like - 0.5, PALM, 0.8),                 # palm on the wall as it slides
    (t_breath + 0.9, LETGO, 1.2),              # it slides out of reach; his hand drops
    (t_cut - 0.2, CLOSED_US, 1.2),
    (OPEN_END, AROUND_L, 0.6),                 # eyes open: the room, back to its size
    (OPEN_END + 1.0, AROUND_R, 0.7),
    (t_most - 0.3, LAST, 0.8),
])

def palm_hook(t, p):
    """while his palm is on the right wall it rides the wall (world coords here), until the wall slides out of reach"""
    a0, a1 = t_like - 0.3, t_breath + 0.9
    if a0 < t < a1 + 1.2:
        want = rw.at(t) - 8                              # the wall's face
        reach = p["neck"][0] + 235                       # his arm, fully out
        k = min(1.0, (t - a0) / 0.5) * (1.0 if t < a1 else max(0.0, 1 - (t - a1) / 1.2))
        hx = p["rhand"][0] + k * (min(want, reach) - p["rhand"][0])
        p["rhand"] = (hx, p["rhand"][1])
        p["relb"] = ((p["neck"][0] + hx) / 2 + 12, (p["neck"][1] + p["rhand"][1]) / 2 + 40)
    return p

x_track = Track([(0, OFF, 0), (GROW2 + 0.3, OFF2, 2.2)])       # a slow shuffle right, eyes shut

cam_track = Track([                                            # ONE continuous shot
    (0, (OFF + 470, 880, 1.6), 0),
    (t_watch - 0.2, (840, 1000, 1.05), 2.4),                   # ease out: the narrow room
    (t_are, (840, 1000, 0.94), PEEK0 - t_are - 0.3),           # drift wider as the walls go
    (PEEK0 - 0.1, (850, 900, 1.35), 1.4),                      # in on the one open eye
    (SHUT1, (900, 970, 1.05), 2.6),                            # out, following him to the wall
    (t_breath + 1.0, (840, 1000, 0.66), OPEN_END - t_breath - 1.0),   # the long pull-out while the room grows
    (t_most - 0.6, (900, 880, 1.3), t_end - t_most + 1.6),     # slow push in for the last line
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (SHUT0, mood_vec("drifting"), 1.0),
    (PEEK0, mood_vec("uncanny"), 0.4),
    (SHUT1, mood_vec("drifting"), 1.5),
    (t_like, mood_vec("warm"), 1.5),
    (t_cut, mood_vec("melancholy"), 2.0),
    (OPEN_END, mood_vec("awe"), 1.0),
    (t_thats, mood_vec("uncanny"), 1.0),
])

NIGHT = dict(top=(18, 24, 60), bot=(52, 50, 96), clouds=0.1, cloud_v=0.6, stars=0.6, sun=0.0, sun_y=0.3, sun_r=24)
sky = Track([(0, SKY(**NIGHT, drone=0.16), 0), (t_are, SKY(**NIGHT, drone=0.0), 0.8),
             (PEEK0, SKY(**NIGHT, drone=0.1), 0.4), (SHUT1, SKY(**NIGHT, drone=0.05), 2.0),
             (OPEN_END, SKY(**NIGHT, drone=0.0), 1.5)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

CRACKS = [(720, 1.4, 11), (860, 1.6, 12), (940, 1.3, 13)]
def room(cr, t, pose, env):
    """the ceiling and both side walls, wherever they've drifted to; the tally redrawn on top. Both walls are drawn the
    same way at all times (owner, 2026-11-22: whatever he walks to must be on screen)."""
    L, R, C = lw.at(t), rw.at(t), ceil.at(t)
    cr.rectangle(-4000, -4000, 9000, C + 4000)
    cr.set_source_rgba(0.93, 0.93, 0.925, 1.0); cr.fill()
    for k in range(3):
        yy = C - 14 - k * 13
        N.path(cr, N.sketch_pts([(-4000, yy), (5000, yy)], amp=1.2, sid=200 + k, step=40)); N.stroke_ink(cr, 1.2, alpha=0.18)
    N.path(cr, N.sketch_pts([(-4000, C), (5000, C)], amp=1.4, sid=210, step=40)); N.stroke_ink(cr, 4.0, alpha=0.85)
    for x0, s, sid in CRACKS:
        pts, px, py = [], x0, C
        for j in range(7):
            pts.append((px, py)); px += (14 if j % 2 == 0 else -9) * s; py -= 9 * s
        N.path(cr, pts); N.stroke_ink(cr, 2.4, alpha=0.8)
    for x0, x1, left, sid in ((-4000, L, True, 300), (R, 5000, False, 320)):
        cr.rectangle(x0, C, x1 - x0, F - C); cr.set_source_rgba(0.9, 0.9, 0.895, 1.0); cr.fill()
        for k in range(40):
            xx = (L - 40 - k * 34) if left else (R + 40 + k * 34)
            N.path(cr, N.sketch_pts([(xx, max(C, -1200) + 30), (xx + (-50 if left else 50), F - 20)], amp=0.9, sid=sid + k, step=30))
            N.stroke_ink(cr, 1.3, alpha=0.14)
    for x, sid in ((L, 340), (R, 341)):
        N.path(cr, N.sketch_pts([(x, C), (x, F)], amp=1.3, sid=sid, step=30)); N.stroke_ink(cr, 4.2, alpha=0.9)
    N.draw_tally(cr, t)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track, tally_base=42, under_hook=room,
            pose_hook=palm_hook, sfx=[(t_like - 0.1, "scratch", 0.18)])
N.BLINKS = [b for b in N.BLINKS if not (PEEK0 - 0.3 < b < SHUT1 + 0.3) and not (OPEN_END - 0.3 < b < OPEN_END + 1.8)]
N.main("nigel_bane_ep043_unwatching.mp4")
