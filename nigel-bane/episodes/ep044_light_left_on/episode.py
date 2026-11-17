"""Day 44 — "Light left on" (posts as `… IIIII IIIII IIII dimming`). Keeper arc 1/4. IDEA: you leave a light on so the
room isn't empty when you come back, as if you were two people. Dusk. A small lamp on the floor, lit, with a paper tag
"for nigel"; there's no cord. C: "Don't turn your light off. Not yet. Stay with this one." — he's kneeling by it. T
(said early, a visible yes/no): "...And it's getting dimmer." Will it last? It dims all episode, flickers twice, and
goes out on the last word. R (one scene): coming home late, seeing your light from the street, and for half a second
it looks like somebody's in. Implied lift / unsettling at once: "You left it on for yourself. Like you were two
people." ENDING (question): "Who are you leaving yours on for?" — the lamp dies on "for". One continuous shot.
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

t_dont, t_notyet, t_somebody, t_lamp, t_tag, t_nigel, t_isnt, t_dimmer = (
    T("don't"), T("not"), T("somebody"), T("lamp"), T("tag"), T("nigel"), T("isn't"), T("dimmer"))
t_youve, t_late, t_street, t_half, t_in, t_then, t_yourself, t_two = (
    T("you've"), T("late"), T("street"), T("half"), T("in"), T("then"), T("yourself"), T("two"))
t_ny1, t_ny2, t_who, t_for_last, t_end = T("not", 2), T("not", 3), T("who"), T("for", 4), TE("for", 4)

KNEEL = P(STAND, head=(430, 1120), neck=(445, 1240), hip=(470, 1390), lknee=(420, 1470), lfoot=(560, 1476),
          rknee=(450, 1468), rfoot=(590, F), lelb=(400, 1330), lhand=(380, 1440),
          relb=(520, 1330), rhand=(560, 1420), tilt=0.1, look=(0.2, 0.6), swing=0.0)
AT_LAMP = P(KNEEL, look=(0.85, 0.35), tilt=0.14, relb=(540, 1340), rhand=(600, 1400))      # watching it, a hand near it
TO_US = P(KNEEL, look=(0.0, 0.0), tilt=0.04)
CUP = P(KNEEL, look=(0.8, 0.45), tilt=0.18, relb=(545, 1330), rhand=(612, 1352), lelb=(470, 1350), lhand=(560, 1380))
TO_US_LOW = P(KNEEL, look=(0.05, 0.05), eyescale=1.06, tilt=0.06)
LAST = P(KNEEL, look=(0.1, 0.0), eyescale=1.1, tilt=0.06)

pose_track = Track([
    (0, KNOCK, 0),
    (t_dont - 0.4, AT_LAMP, 1.2),                  # already kneeling beside it
    (t_somebody - 0.3, TO_US, 0.9),
    (t_tag - 0.3, AT_LAMP, 0.8),
    (t_dimmer - 0.5, AT_LAMP, 0.4),
    (t_youve - 0.3, TO_US, 1.0),
    (t_late, TO_US_LOW, 1.5),
    (t_then - 0.3, AT_LAMP, 1.2),
    (t_ny1 - 0.5, CUP, 0.9),                       # "Not yet... not yet..." — hands cupped round it
    (t_who - 0.6, LAST, 0.8),
])
x_track = Track([(0, 0.0, 0)])

# the lamp's brightness: dims slowly all episode, two flickers, and goes out on the last word
bright = Track([(0, 1.0, 0), (t_dimmer - 0.6, 0.82, 1.6), (t_youve, 0.55, t_ny1 - t_youve - 1.0),
                (t_ny1 + 1.6, 0.34, 2.0), (t_who, 0.26, 1.2), (t_for_last, 0.0, 0.22)])
FLICKERS = [(t_late + 0.9, 0.35), (t_in + 0.8, 0.5), (t_ny1 + 0.6, 0.85), (t_ny2 + 0.5, 0.6)]
def lamp_level(t):
    b = bright.at(t)
    for ft, depth in FLICKERS:
        u = t - ft
        if 0 <= u < 0.55:
            b *= 1 - depth * (0.5 + 0.5 * math.sin(u * 46)) * (1 - u / 0.55)
    return max(0.0, b)

cam_track = Track([                                        # ONE continuous shot
    (0, (470, 880, 1.6), 0),
    (t_dont - 0.2, (580, 1200, 1.25), 2.2),                # down with him by the lamp
    (t_lamp - 0.5, (650, 1290, 1.55), 2.2),                # in on the lamp
    (t_tag - 0.2, (720, 1260, 1.9), 1.8),                  # the tag
    (t_isnt - 0.2, (630, 1320, 1.3), 2.0),                 # out: no cord anywhere
    (t_youve - 0.3, (560, 1160, 1.12), 4.0),               # ease out: him and the lamp, dusk in the window
    (t_late, (520, 1090, 1.45), t_then - t_late),          # slow push on him through the story
    (t_ny1 - 0.6, (600, 1210, 1.6), 2.2),                  # the two of them, close
    (t_who - 0.4, (520, 1120, 1.85), t_end - t_who + 0.5), # in on his face, lit from below, as it goes
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_dont, mood_vec("warm"), 1.2),
    (t_dimmer - 0.4, mood_vec("unease"), 0.8),
    (t_youve, mood_vec("melancholy"), 1.5),
    (t_then, mood_vec("lonely"), 1.5),
    (t_ny1, mood_vec("unease"), 1.0),
    (t_who, mood_vec("uncanny"), 1.0),
])

DUSK = dict(top=(52, 54, 104), bot=(214, 140, 120), clouds=0.35, cloud_v=1.4, stars=0.1, sun=0.0, sun_y=0.3, sun_r=24)
sky = Track([(0, SKY(**DUSK, drone=0.14), 0), (t_dimmer + 0.4, SKY(**DUSK, drone=0.0), 0.6),
             (t_youve, SKY(**DUSK, drone=0.1), 1.5), (t_ny1, SKY(**DUSK, drone=0.0), 1.0)])
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
            caption_avoid=[(0, 99, lambda t: (LAMP_X - 100, F - 320, LAMP_X + 160, F + 20))])
N.main("nigel_bane_ep044_light_left_on.mp4")
