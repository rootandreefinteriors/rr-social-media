"""Day 23 — "Edge". DREAD DAY (done live). He takes the spider's long thread — so he can find his way back — and walks
off to find the wall. It never comes: white, and the floor line, forever. The room's hum fades behind him; the thread
trailing back to the web gets thinner and fainter the further he goes. IDEA (you): you know your street, the road to
work, a few rooms — everything past that you've only been told about. Maps. Pictures. Someone said it's there.
TENSION: the walk that should end and doesn't (+ the thread thinning). The camera pulls back: the window is a speck far
behind him. HOOK: "Everything past where you stopped walking... you're just trusting it's there."
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, ONE, OPEN, STAND)

N.setup()
T, TE = N.T, N.TE

LPICK = P(lelb=(420, 1060), lhand=(392, 1000), look=(-0.3, 0.15), tilt=-0.05, swing=0.0)
HOLD = P(lelb=(398, 1088), lhand=(350, 1134), relb=(500, 1100), rhand=(512, 1215), look=(0.65, 0.0), tilt=0.03, swing=0.0)
HOLD_YOU = P(HOLD, look=(0.0, 0.0), tilt=0.0)
HOLD_TALK = P(HOLD, relb=(540, 1060), rhand=(585, 1010), look=(0.2, 0.0))
AHEAD = P(HOLD, look=(0.95, -0.05), eyescale=1.08)
BACK = P(HOLD, look=(-0.95, 0.05), tilt=-0.06, eyescale=1.05)
THREAD_LOOK = P(HOLD, look=(-0.7, 0.45), tilt=-0.1)
LAST = P(HOLD_YOU, eyescale=1.05)

t_there_end, t_wall, t_touched, t_you1 = TE("there"), T("wall"), T("touched"), T("you")
t_maps, t_someone, t_there2_end = T("maps"), T("someone"), TE("there", 2)
t_should, t_now_end, t_keeps, t_going_end = T("should"), TE("now"), T("keeps"), TE("going", 2)
t_cant, t_threads, t_thin_end, t_every2 = T("can't"), T("thread's"), TE("thin"), T("everything", 2)

PICK = t_wall + 0.15
pose_track = Track([
    (0, KNOCK, 0),
    (t_there_end + 0.2, LPICK, 0.8),               # takes hold of the thread
    (t_touched + 0.2, HOLD, 0.6),                  # and goes
    (t_you1 - 0.2, HOLD_YOU, 0.7),
    (t_you1 + 2.2, HOLD_TALK, 0.8),
    (t_maps, HOLD, 0.8),
    (t_should - 0.3, AHEAD, 0.6),                  # it should be here
    (t_keeps - 0.2, HOLD, 0.6),
    (t_cant - 0.3, BACK, 0.9),                     # nothing behind him either
    (t_threads - 0.2, THREAD_LOOK, 0.7),
    (t_every2 - 0.4, LAST, 1.0),
])

x_track = Track([
    (0, 0.0, 0),
    (t_there_end + 0.2, 250.0, 1.0),
    (t_touched + 0.4, 2000.0, t_should - 0.3 - t_touched - 0.4),   # one long walk...
    (t_keeps - 0.2, 2400.0, t_going_end + 2.4 - t_keeps),           # ...it should be here by now. on.
])

cam_track = Track([
    (0, (470, 880, 1.6), 0),
    (t_there_end + 0.2, (620, 760, 1.2), 1.5),               # him at the web, the thread
    (t_touched + 0.4, (470, 860, 1.25), 2.0),                # walking with him (follow on)
    (t_going_end + 0.2, (1845, 1000, 0.36), 3.6),            # pull way back: the window is a speck
    (t_threads - 0.4, (470, 880, 1.15), 2.6),                # back in with him
    (t_every2 - 0.3, (470, 850, 1.45), 3.0),
])
follow_track = Track([
    (0, 0.0, 0),
    (t_touched + 0.4, 1.0, 2.0),
    (t_going_end + 0.2, 0.0, 3.6),
    (t_threads - 0.4, 1.0, 2.6),
])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_you1, mood_vec("drifting"), 1.2),
    (t_maps, mood_vec("uncanny"), 1.2),
    (t_should, mood_vec("unease"), 0.8),
    (t_cant, mood_vec("lonely"), 1.2),
    (t_every2, mood_vec("unease"), 1.2),
])

DAY = dict(top=(168, 186, 214), bot=(226, 230, 236), clouds=0.5, cloud_v=3.0, snow_pile=0.6)
sky_track = Track([
    (0, SKY(**DAY, drone=0.4), 0),
    (t_touched + 0.4, SKY(**DAY, drone=0.12), t_someone - t_touched),   # the room's hum fades behind him
    (t_should, SKY(**DAY, drone=0.0), 2.0),                             # nothing out here at all
    (t_every2, SKY(**DAY, drone=0.25), 2.5),
])
class Env:
    def at(self, t):
        d = dict(sky_track.at(t))
        d.update(web=1.0, spider=1.0, prey=1.0, prey_wrap=1.0)
        return d
env_track = Env()

WEB = dict(hub=(655, 328), frame=[(570, 235), (742, 214), (748, 420), (585, 440)],
           anchors=[(500, 168), (800, 205), (840, 354), (470, 520)], fade=[0, 3],
           dragline=None, spokes=11, turns=8, spider_size=1.25,           # the dragline is drawn below, in his hand
           prey=dict(pos=(712, 262), kind="fly", size=1.9))
MOTH = dict(prey=1.0, prey_struggle=0.0, prey_wrap=1.0)
TOP, FLOOR_END = (632, 438), (650, N.FLOOR_Y)

def scene(cr, t, p, env):
    N.draw_prey(cr, t, MOTH, (622, 392), "moth", 2.1)
    hand = p["lhand"]
    u = N.smooth((t - PICK) / 0.45)
    end = N.lerp(FLOOR_END, hand, u)
    L = math.hypot(end[0] - TOP[0], end[1] - TOP[1])
    wd = max(0.6, 2.3 - L / 1500.0)                     # thinner...
    al = max(0.22, 0.8 - L / 5500.0)                    # ...and fainter the further he goes
    sag = min(160.0, L * 0.05)
    mx, my = (TOP[0] + end[0]) / 2, (TOP[1] + end[1]) / 2 + sag
    cr.move_to(*TOP); cr.curve_to(mx, my, mx, my, *end)
    cr.set_source_rgba(*N.INK, al); cr.set_line_width(wd); cr.stroke()
    if L > 600:                                          # a glint running along it now and then
        g = (t * 0.35) % 1.0
        gx = TOP[0] + (end[0] - TOP[0]) * g; gy = TOP[1] + (end[1] - TOP[1]) * g + sag * 4 * g * (1 - g) * 0.5
        cr.arc(gx, gy, 3.0, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.8 * al); cr.fill()

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track,
            tally_base=23, tally_new=[], web=WEB, draw_hook=scene)
N.main("nigel_bane_ep023_edge.mp4")
