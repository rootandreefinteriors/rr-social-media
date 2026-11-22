"""Day 44 — remade 2026-11-22 after the owner's hard reset (posts as `… IIIII IIIII IIII dimming`). Keeper arc 1/4: a
lamp arrives and dies. THE LINE: "You keep it lit so you won't be the one who let it go out." Dusk. A small lamp on the
floor, lit, tag "for nigel", no cord; he is kneeling with his hands cupped round it. C (plain, to one listener, about
what we can see): "Shh. Keep still. It's going out." T (visible yes/no): it dims and flickers all episode; will it last
while he holds it? Salad-Fingers tenderness: "There, there." as one finger strokes the shade. Bridge: he doesn't even
like the lamp; he just doesn't want it to go out while he's holding it -> the friendship where you always text first,
the dead group chat: you keep it lit so you won't be the one who let it go out. ENDING (action + flat line): on the
second "not yet" he slowly lifts his hands off it; it goes out a beat later; "...It wasn't me." One continuous shot.
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
LAMP_X = 690.0

t_shh, t_going, t_somebody, t_isnt, t_been, t_there, t_dont, t_just = (
    T("shh"), T("going"), T("somebody"), T("isn't"), T("been"), T("there", 2), T("don't", 1), T("just"))
t_youve, t_friend, t_group, t_something, t_keep2, t_ny1, t_ny2, t_it_last, t_end = (
    T("you've"), T("friendship"), T("group"), T("something"), T("keep", 2), T("not", 1), T("not", 2), T("wasn't"), TE("me", 2))
t_holding = T("holding")
DIE = TE("yet", 2) + 0.75                       # it goes out in the held beat after the second "not yet"

KNEEL = P(STAND, head=(430, 1120), neck=(445, 1240), hip=(470, 1390), lknee=(420, 1470), lfoot=(560, 1476),
          rknee=(450, 1468), rfoot=(590, F), lelb=(400, 1330), lhand=(380, 1440),
          relb=(520, 1330), rhand=(560, 1420), tilt=0.1, look=(0.2, 0.6), swing=0.0)
CUP = P(KNEEL, look=(0.8, 0.4), tilt=0.16, relb=(538, 1248), rhand=(608, 1182), lelb=(522, 1338), lhand=(598, 1292))   # both hands shielding it, like a candle
CUP_US = P(CUP, look=(0.1, 0.05), tilt=0.1)
AT_LAMP = P(KNEEL, look=(0.85, 0.35), tilt=0.14, relb=(540, 1340), rhand=(600, 1400))
STROKE = P(KNEEL, look=(0.85, 0.4), tilt=0.2, relb=(560, 1290), rhand=(640, 1250), finger=1.0)
TO_US = P(KNEEL, look=(0.0, 0.0), tilt=0.04)
TO_US_LOW = P(KNEEL, look=(0.05, 0.05), eyescale=1.06, tilt=0.06)
LIFT = P(KNEEL, look=(0.75, 0.4), tilt=0.1, relb=(505, 1338), rhand=(548, 1292), lelb=(398, 1342), lhand=(352, 1296))   # hands pulled back off it, held open
LAST = P(KNEEL, look=(0.05, 0.0), eyescale=1.1, tilt=0.06)

pose_track = Track([
    (0, KNOCK, 0),
    (t_shh - 0.5, CUP, 1.0),                       # already kneeling, hands cupped round it
    (t_somebody - 0.3, CUP_US, 0.8),
    (t_isnt - 0.2, AT_LAMP, 0.8),
    (t_there - 0.4, STROKE, 0.8),                  # "There, there." — one finger strokes the shade
    (t_dont - 0.3, TO_US, 0.9),                    # "I don't even like it very much." — flat, to us
    (t_just - 0.3, CUP, 1.0),
    (t_youve - 0.3, TO_US, 1.0),
    (t_friend, TO_US_LOW, 1.5),
    (t_ny1 - 0.6, CUP, 0.9),                       # "Not yet..."
    (t_ny2 + 0.3, LIFT, 1.4),                      # "...not yet..." — he lifts his hands off it, slowly
    (DIE + 0.5, LAST, 1.2),                        # "...It wasn't me."
])
def stroke(t, p):
    """the finger strokes back and forth along the shade during "There, there." """
    a0, a1 = t_there - 0.1, t_dont - 0.4
    if a0 < t < a1:
        k = min(1.0, (t - a0) / 0.4) * min(1.0, (a1 - t) / 0.4)
        p["rhand"] = (p["rhand"][0] + k * 26 * math.sin((t - a0) * 3.4), p["rhand"][1] + k * 6 * math.sin((t - a0) * 3.4))
    return p
x_track = Track([(0, 0.0, 0), (t_shh - 0.6, 40.0, 1.0)])   # shuffles in close to it

bright = Track([(0, 1.0, 0), (t_going + 0.6, 0.86, 1.2), (t_been, 0.74, 4.0), (t_youve, 0.52, t_ny1 - t_youve - 1.0),
                (t_ny1, 0.34, 2.4), (t_ny2 + 0.6, 0.22, DIE - t_ny2 - 0.9), (DIE, 0.0, 0.28)])
FLICKERS = [(t_going + 0.3, 0.55), (t_holding + 0.5, 0.3), (t_group + 0.4, 0.4), (t_ny1 + 0.7, 0.85),
            (t_ny2 + 0.6, 0.7), (DIE - 0.45, 0.8)]
def lamp_level(t):
    b = bright.at(t)
    for ft, depth in FLICKERS:
        u = t - ft
        if 0 <= u < 0.55:
            b *= 1 - depth * (0.5 + 0.5 * math.sin(u * 46)) * (1 - u / 0.55)
    return max(0.0, b)

cam_track = Track([                                        # ONE continuous shot
    (0, (470, 880, 1.6), 0),
    (t_shh - 0.3, (600, 1230, 1.4), 2.2),                  # down with him: hands round the lamp
    (t_somebody, (660, 1240, 1.65), 2.0),                  # in on the lamp and its tag, his face at the edge
    (t_isnt - 0.2, (640, 1320, 1.25), 2.0),                # out: no cord anywhere
    (t_there - 0.6, (640, 1240, 1.6), 1.8),                # in on the finger stroking the shade
    (t_dont - 0.4, (540, 1150, 1.4), 1.6),                 # his face: "I don't even like it"
    (t_youve - 0.3, (560, 1160, 1.12), 3.0),               # ease out: him and the lamp, dusk in the window
    (t_friend, (500, 1110, 1.55), t_keep2 - t_friend),     # slow push on him through the list
    (t_keep2 + 0.4, (510, 1120, 1.75), 3.0),               # the line, close
    (t_ny1 - 0.4, (600, 1220, 1.5), 2.2),                  # the two of them as he lifts his hands
    (DIE + 0.3, (520, 1130, 1.8), t_end - DIE + 0.3),      # in on his face in the dark
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_shh, mood_vec("unease"), 1.0),
    (t_there, mood_vec("warm"), 1.2),
    (t_dont, mood_vec("drifting"), 1.0),
    (t_youve, mood_vec("melancholy"), 1.5),
    (t_keep2, mood_vec("lonely"), 1.2),
    (t_ny1, mood_vec("unease"), 1.0),
    (DIE, mood_vec("uncanny"), 0.6),
])

DUSK = dict(top=(52, 54, 104), bot=(214, 140, 120), clouds=0.35, cloud_v=1.4, stars=0.1, sun=0.0, sun_y=0.3, sun_r=24)
DARK = dict(top=(30, 32, 70), bot=(110, 80, 100), clouds=0.3, cloud_v=1.4, stars=0.3, sun=0.0, sun_y=0.3, sun_r=24)
sky = Track([(0, SKY(**DUSK, drone=0.12), 0), (t_shh, SKY(**DUSK, drone=0.0), 0.6),
             (t_youve, SKY(**DUSK, drone=0.08), 1.5), (t_ny1, SKY(**DARK, drone=0.0), 6.0)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

def lamp(cr, t, pose, env):
    """a small lamp on the floor with a paper shade; no cord. Its warm glow scales with lamp_level(t)."""
    b = lamp_level(t)
    x = LAMP_X
    sh_top, sh_bot = F - 300, F - 200
    if b > 0.01:                                           # the glow: on the floor and the wall behind
        g = cairo.RadialGradient(x, sh_bot + 10, 0, x, sh_bot + 10, 420)
        g.add_color_stop_rgba(0, 1.0, 0.84, 0.5, 0.6 * b); g.add_color_stop_rgba(0.45, 1.0, 0.85, 0.58, 0.24 * b)
        g.add_color_stop_rgba(1, 1.0, 0.9, 0.7, 0.0)
        cr.set_source(g); cr.arc(x, sh_bot + 10, 420, 0, 2 * math.pi); cr.fill()
        pool = cairo.RadialGradient(x, F, 0, x, F, 260)
        pool.add_color_stop_rgba(0, 1.0, 0.85, 0.5, 0.3 * b); pool.add_color_stop_rgba(1, 1.0, 0.85, 0.5, 0.0)
        cr.save(); cr.translate(0, F); cr.scale(1, 0.25); cr.translate(0, -F)
        cr.set_source(pool); cr.arc(x, F, 260, 0, 2 * math.pi); cr.fill(); cr.restore()
    # the shade, lit from inside
    shade = [(x - 52, sh_top), (x + 52, sh_top), (x + 84, sh_bot), (x - 84, sh_bot)]
    cr.move_to(*shade[0]); [cr.line_to(*p) for p in shade[1:]]; cr.close_path()
    cr.set_source_rgba(1.0, 0.84, 0.42, 0.06 + 0.85 * b); cr.fill()
    for a, c_ in ((shade[0], shade[1]), (shade[1], shade[2]), (shade[2], shade[3]), (shade[3], shade[0])):
        N.path(cr, N.sketch_pts([a, c_], amp=1.0, sid=500 + int(a[0]) % 7, step=14)); N.stroke_ink(cr, 3.4, alpha=0.9)
    if b > 0.01:                                           # the bulb's hot spot under the shade
        hb = cairo.RadialGradient(x, sh_bot - 6, 0, x, sh_bot - 6, 60)
        hb.add_color_stop_rgba(0, 1, 0.97, 0.85, 0.9 * b); hb.add_color_stop_rgba(1, 1, 0.9, 0.6, 0.0)
        cr.set_source(hb); cr.arc(x, sh_bot - 6, 60, 0, 2 * math.pi); cr.fill()
    N.path(cr, N.sketch_pts([(x, sh_bot), (x, F - 22)], amp=0.8, sid=510, step=12)); N.stroke_ink(cr, 4.0, alpha=0.9)
    cr.save(); cr.translate(x, F - 10); cr.scale(1, 0.32)
    N.path(cr, N.circle_pts(0, 0, 58, sid=511)); cr.restore(); N.stroke_ink(cr, 3.6, alpha=0.9)
    # the tag, hanging off the shade's lower edge on a string
    px, py = x + 70, sh_bot - 4
    sw = 0.08 * math.sin(t * 1.3)
    tx, ty = px + 10 + 30 * math.sin(sw), py + 52
    N.path(cr, N.sketch_pts([(px, py), (tx - 2, ty - 16)], amp=0.6, sid=512, step=6)); N.stroke_ink(cr, 1.5, alpha=0.75)
    N.draw_tag(cr, tx + 12, ty, ang=1.45 + sw, scale=0.75, flip=1.0, string=False, sid=513)

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track, tally_base=43, under_hook=lamp,
            pose_hook=stroke, sfx=[(DIE, "tick", 0.35)],
            caption_avoid=[(0, 99, lambda t: (LAMP_X - 100, F - 320, LAMP_X + 160, F + 20))])
N.BLINKS = [b for b in N.BLINKS if not (DIE - 0.5 < b < DIE + 1.5)]
N.main("nigel_bane_ep044_dimming.mp4")
