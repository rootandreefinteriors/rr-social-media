"""Day 48 — "borrowing" (posts as `… IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII III borrowing`). Thanksgiving.
The glass arc 1/4 (his breath on our side); written in the owner's hard reset (2026-11-22). THE LINE: "So if you've lost
someone... a little of what they breathed is in you right now." Afternoon; the room is empty again. C (plain, something
the viewer can do): "Breathe on your screen. Go on. ...Hhhaa. Like that." — he leans right in and breathes on the glass,
and a patch of fog blooms on OUR side of the screen. T (visible yes/no): "I'm going to hold my breath until it's gone."
Real silence while the fog shrinks from the edges in; he holds, trembling; it vanishes and he lets the breath go. Bridge:
his breath is on your side now; a second ago it was in him -> breath doesn't stay where you leave it; it goes round the
room, out the window (the camera drifts to the window), round the world -> a little of what someone you lost breathed is
in you right now. ENDING: "Breathe in." (eyes shut, he breathes in) "...That was some of theirs." One continuous shot.
Truth: true at the level of molecules (a breath's molecules disperse round the atmosphere within a few years).
"""
import math
import os
import random
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import cairo
import nigel as N
from nigel import (P, SKY, Track, mood_vec, KNOCK, STAND)

N.setup()
T, TE = N.T, N.TE
F = N.FLOOR_Y

t_breathe, t_go, t_hh, t_like, t_mines, t_second, t_hold = T("breathe"), T("go"), T("hhhaa"), T("like"), T("mine's"), T("second"), T("hold")
t_gone, t_breath2, t_round1, t_out, t_window, t_round2, t_most = TE("gone"), T("breath", 2), T("round"), T("out", 2), T("window"), T("round", 2), T("most")
t_so, t_lost, t_not, t_every, t_breathe_in, t_that, t_end = T("so"), T("lost"), T("not"), T("every"), T("breathe", 2), T("that", 2), TE("theirs")

FOG0 = t_hh + 0.05                 # the breath hits the glass
HOLD0 = t_gone + 0.25              # holding
FOG_GONE = T("breath", 2) - 1.7    # it's gone ...
EXHALE = FOG_GONE + 0.25           # ... and he lets go

# ------------------------------------------------------------------ the fog, on OUR side of the glass (screen space)
rnd = random.Random(48)
DROPS = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(1.6, 4.6), rnd.uniform(0.3, 1.0)) for _ in range(520)]
DROPS = [d for d in DROPS if d[0] ** 2 + d[1] ** 2 <= 1]
LOBES = [(rnd.uniform(-0.35, 0.35), rnd.uniform(-0.25, 0.25), rnd.uniform(0.55, 0.85)) for _ in range(6)]
fog_r = Track([(0, 0.0, 0), (FOG0, 250.0, 0.45), (FOG0 + 0.6, 236.0, HOLD0 - FOG0 - 0.6), (HOLD0, 0.0, FOG_GONE - HOLD0)])
_fog_at = {}

def fog(cr, t, pose, env, to_screen):
    r = fog_r.at(t)
    if r < 1.0 or t < FOG0:
        return
    if "xy" not in _fog_at:                     # it stays where his mouth was when he breathed, on the glass
        hx, hy = pose_track.at(FOG0)["head"]
        cx, cy, z = cam_track.at(FOG0)
        _fog_at["xy"] = ((hx + 4 - cx) * z + 540, (hy + 112 - cy) * z + 960)
    x, y = _fog_at["xy"]
    sy = 0.78                                   # a breath patch is a little wider than tall
    cr.save(); cr.translate(x, y); cr.scale(1, sy)
    for lx, ly, lr in LOBES:                    # soft, slightly lumpy body: cool grey, so it reads on the white room
        R = r * lr
        g = cairo.RadialGradient(lx * r, ly * r, 0, lx * r, ly * r, R)
        g.add_color_stop_rgba(0, 0.72, 0.76, 0.83, 0.38)
        g.add_color_stop_rgba(0.65, 0.76, 0.8, 0.86, 0.28)
        g.add_color_stop_rgba(1, 0.85, 0.88, 0.92, 0.0)
        cr.set_source(g); cr.arc(lx * r, ly * r, R, 0, 2 * math.pi); cr.fill()
    g = cairo.RadialGradient(0, 0, 0, 0, 0, r)  # a milky veil over the middle, softening what's behind it
    g.add_color_stop_rgba(0, 0.97, 0.98, 0.99, 0.42); g.add_color_stop_rgba(0.75, 0.96, 0.97, 0.98, 0.25)
    g.add_color_stop_rgba(1, 0.96, 0.97, 0.98, 0.0)
    cr.set_source(g); cr.arc(0, 0, r, 0, 2 * math.pi); cr.fill()
    for dx, dy, s, a in DROPS:                  # beads of condensation: a bright side and a shadow side
        d = math.hypot(dx, dy)
        edge = max(0.0, 1 - d) ** 0.5
        px, py = dx * r * 0.92, dy * r * 0.92
        cr.arc(px + 0.8, py + 1.0, s, 0, 2 * math.pi); cr.set_source_rgba(0.55, 0.6, 0.68, 0.35 * a * edge); cr.fill()
        cr.arc(px, py, s, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.85 * a * edge); cr.fill()
    cr.restore()

# ------------------------------------------------------------------ poses
LEAN = P(STAND, head=(450, 760), look=(0.0, 0.05), eyescale=1.05, swing=0.0)
LOOK_FOG = P(STAND, head=(450, 768), look=(0.0, 0.55), eyescale=1.1, tilt=0.04, swing=0.0)
TO_US = P(STAND, look=(0.0, 0.0), eyescale=1.04, swing=0.0)
HOLD = P(STAND, head=(450, 768), look=(0.0, 0.45), eyescale=1.18, swing=0.0)
LETGO = P(STAND, head=(452, 792), neck=(452, 955), tilt=-0.06, shut=0.4, look=(0.0, 0.25), swing=0.0)
WINDOW = P(STAND, look=(0.85, -0.8), tilt=0.12, eyescale=1.05, swing=0.0)
SOFT = P(STAND, look=(0.0, 0.05), tilt=0.03, swing=0.0)
INHALE = P(STAND, head=(450, 762), neck=(452, 938), shut=1.0, tilt=-0.04, look=(0.0, -0.1), swing=0.0)
LAST = P(STAND, look=(0.0, 0.0), eyescale=1.08, tilt=0.02, swing=0.0)

pose_track = Track([
    (0, KNOCK, 0),
    (t_breathe - 0.5, LEAN, 0.9),                  # leans right in to the glass
    (FOG0 + 0.9, LOOK_FOG, 0.8),                   # looks down at the fog he left
    (t_mines + 0.6, TO_US, 0.8),
    (t_second, LOOK_FOG, 0.8),
    (t_hold - 0.4, TO_US, 0.6),
    (HOLD0, HOLD, 0.6),                            # holding his breath, eyes on the fog
    (EXHALE, LETGO, 0.5),                          # it's gone: he lets it go
    (t_breath2 - 0.4, TO_US, 0.8),
    (t_out - 0.4, WINDOW, 1.0),                    # "Out the window." — he looks up at it
    (t_most - 0.3, TO_US, 1.2),
    (t_so - 0.2, SOFT, 1.0),
    (t_breathe_in - 0.1, INHALE, 0.7),             # "Breathe in." — eyes shut, he breathes in
    (t_that + 0.2, LAST, 0.9),                     # "...That was some of theirs."
])
def tremble(t, p):
    """while he holds his breath he trembles, a little more every second"""
    if HOLD0 < t < EXHALE:
        a = min(1.0, (t - HOLD0) / (EXHALE - HOLD0)) * min(1.0, (EXHALE - t) / 0.2)
        dx = a * (2.2 * math.sin(t * 41) + 1.4 * math.sin(t * 27))
        for k in ("head", "neck"):
            p[k] = (p[k][0] + dx, p[k][1])
        p["eyescale"] = p.get("eyescale", 1.0) + 0.02 * a * math.sin(t * 33)
    return p
x_track = Track([(0, 0.0, 0)])

cam_track = Track([                                        # ONE continuous shot
    (0, (470, 880, 1.6), 0),
    (t_breathe - 0.4, (452, 830, 2.25), 1.6),              # in very close: he's right at the glass
    (t_mines + 0.4, (452, 840, 2.1), 1.6),
    (HOLD0 - 0.2, (452, 832, 2.3), EXHALE - HOLD0),        # holds close through the held breath
    (t_breath2 - 0.2, (520, 940, 1.2), 3.0),               # ease out as he talks about the air
    (t_out - 0.6, (760, 640, 1.25), 2.4),                  # drift up to the window
    (t_most - 0.4, (540, 960, 1.05), 3.2),                 # back down to him, the whole room
    (t_so, (470, 870, 1.75), t_every - t_so + 1.0),        # slow push in
    (t_breathe_in - 0.4, (460, 840, 2.0), t_end - t_breathe_in + 0.6),
])
follow_track = Track([(0, 0.0, 0)])

mood_track = Track([
    (0, mood_vec("curious"), 0),
    (t_breathe, mood_vec("drifting"), 1.0),
    (FOG0 + 0.6, mood_vec("awe"), 1.0),
    (t_hold, mood_vec("unease"), 0.8),
    (EXHALE, mood_vec("drifting"), 1.0),
    (t_out, mood_vec("awe"), 1.5),
    (t_so, mood_vec("melancholy"), 1.5),
    (t_not, mood_vec("warm"), 2.0),
    (t_that, mood_vec("uncanny"), 1.0),
])

AFT = dict(top=(150, 170, 200), bot=(222, 214, 206), clouds=0.6, cloud_v=1.0, sun=0.3, sun_y=0.55, sun_r=24)
sky = Track([(0, SKY(**AFT, drone=0.12), 0), (t_breathe, SKY(**AFT, drone=0.0), 0.8),
             (t_round1, SKY(**dict(AFT, cloud_v=3.2), drone=0.05), 2.5), (t_most, SKY(**AFT, drone=0.06), 3.0),
             (t_breathe_in, SKY(**AFT, drone=0.0), 1.0)])
class Env:
    def at(self, t):
        return sky.at(t)
env_track = Env()

N.configure(mood_track, pose_track, x_track, cam_track, follow_track, env_track, tally_base=47, pose_hook=tremble,
            glass_hook=fog)
N.BLINKS = [b for b in N.BLINKS if not (HOLD0 - 0.3 < b < EXHALE + 0.2)]
N.main("nigel_bane_ep048_borrowing.mp4")
