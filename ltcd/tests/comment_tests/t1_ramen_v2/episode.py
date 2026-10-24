"""TEST 1 v2 (not posted) — top comment: "bathe in a tub of spicy ramen". Adult-swim deadpan rewrite.

SHOT 1  He reads the comment. Looks back at us. Holds it way too long. Slow blink. Tiny nod.
SHOT 2  HARD CUT: just his head sticking out of a tub of red ramen, a noodle on his head, staring at us. An egg drifts
        over and bumps his chin; he looks at it, looks back. Then the spice arrives, slowly: red liquid rises inside his
        head like a glass filling up while he keeps a straight face -- sweat, a twitch, pupils shrinking, a faint
        ringing that swells... his hair snaps straight up and the ringing stops dead. One tear. He sinks, still staring,
        to eye level... then all the way under. Just the hair sticking out. Bubbles stop.
SHOT 3  HARD CUT wide: giant chopsticks come down from somewhere above, fish around, clamp, yank --
        HARD CUT: he's hanging folded over the chopsticks like a noodle, upside-down face still staring at us, dripping
        into a puddle. They give him a little shake. Hold him up toward whatever is up there. Pause. Let go. He drops
        into the puddle. Gets up. The ask, deadpan, dripping. The noodle slides off his head mid-ask. He doesn't react.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y
from ink import smooth

TS, TX = 0.95, 620
G = O.tub_geom(TX, FLOOR_Y, TS); RIM = G["rim_y"]
OX = TX - 540                                   # his body offset in the tub

L.POSES["tub_neck"] = dict(head=(540, 1100), neck=(540, 1215), hip=(540, 1420), lelb=(480, 1330), lhand=(470, 1405),
                           relb=(600, 1330), rhand=(610, 1405), lknee=(500, 1400), lfoot=(470, 1425), rknee=(580, 1400),
                           rfoot=(610, 1425), nowalk=1.0)
L.POSES["tub_peek"] = dict(L.POSES["tub_neck"], head=(540, 1222), neck=(540, 1300), hip=(540, 1400))
L.POSES["tub_under"] = dict(L.POSES["tub_neck"], head=(540, 1322), neck=(540, 1385), hip=(540, 1415))
L.POSES["heap"] = dict(head=(330, 1388), neck=(445, 1410), hip=(760, 1440), lelb=(560, 1455), lhand=(650, 1466),
                       relb=(600, 1400), rhand=(700, 1452), lknee=(860, 1400), rknee=(890, 1430), lfoot=(985, 1462),
                       rfoot=(1010, 1466), tilt=4.83, lfoot_dir=1.0, rfoot_dir=1.0, nowalk=1.0)

CAM1 = (620, 880, 1.08)          # standing: card stays clear of his hair
CAM2 = (TX, 1070, 1.55)          # close on the head in the soup
CAM3 = (TX, 1000, 1.0)           # wide: tub + what comes down
CAM4 = (580, 1010, 1.05)         # hanging (he's at the far left, clear of the card)
CAM5 = (420, 880, 1.05)          # standing again (straight hair is taller)

S = M.Scene(x0=OX)
S.auto_blinks = False                                              # a dead stare barely blinks
S.blink(8.3, 13.2, 17.8, 18.05, 41.7)
S.card("noodle.gremlin", "bathe in a tub of spicy ramen", "2.4K", t0=0.35)
S.camkeys[0] = (0.0, CAM1, 0); S.cam = CAM1
S.sfx(0.35, "tick", 0.04)

# ================================================================ SHOT 1: reads it. stares. accepts.
S.set(0.0, "stand", "deadpan", dur=0.0)
S.set(1.0, "stand", "deadpan", dur=0.14, look=(0.55, -0.9), tilt=-0.05)          # eyes go first; head follows (lag)
def read_eyes(tt, p, a=1.2, per=0.8, n=2):
    if a <= tt < a + per * n:
        k = (tt - a) / per; u = k % 1.0
        p["look"] = (0.35 + 0.5 * smooth(min(1.0, u * 1.25)), -0.92 + 0.12 * int(k)); p["saccade"] = 0.0
    return p
S.hook(read_eyes)
S.set(2.9, "stand", "deadpan", dur=0.13, look=(0.0, 0.0), tilt=0.0)               # back to us
S.set(3.1, "stand", "dead_stare", dur=0.6)
S.set(4.7, "stand", "dead_stare", dur=0.22, lid=1.0)                              # slow blink
S.set(5.05, "stand", "resigned", dur=0.35)
def nod(tt, p, a=5.45):
    v = 16 * math.sin(math.pi * min(1.0, max(0.0, (tt - a) / 0.7)))
    if v > 0.01: p["head"] = (p["head"][0], p["head"][1] + v)
    return p
S.hook(nod)

# ================================================================ SHOT 2: head in the soup
T2 = 6.4
S.cut(T2, cam=CAM2)
S.set(T2, "tub_neck", "dead_stare", dur=0.0)
S.camera(T2 + 1.0, TX, 1080, 1.75, 13.0)                                         # slow creep in
S.sfx(T2, "simmer", 0.05, dur=36.0)
def tub_back(cr, x, yb, s, t, p): O.draw_tub(cr, x, yb, TS, t, "back", steam=1.0)
def tub_front(cr, x, yb, s, t, p):
    rip = ramp(t, 31.3, 31.5) * (1 - ramp(t, 32.2, 32.6)) * ((t * 1.3) % 1.0)
    O.draw_tub(cr, x, yb, TS, t, "front", simmer=1.0, ripple=rip, ripple_x=-20)
S.place("tub_back", tub_back, (TX, FLOOR_Y), t_on=T2, layer="back")
S.place("tub_front", tub_front, (TX, FLOOR_Y), t_on=T2, layer="front")
S.place("noodle", lambda cr, x, y, s, tt, p: noodle(cr, tt, p), (0, 0), t_on=T2, layer="front")

# the egg drifts over and bumps his chin
T_BUMP = 10.0
def egg_x(t):
    if t < 8.8: return TX + 192 + 4 * math.sin(t * 1.3)
    if t < T_BUMP: return lerp(TX + 192, TX + 104, smooth((t - 8.8) / (T_BUMP - 8.8)))
    return TX + 104 + 9 * math.exp(-(t - T_BUMP) * 3) * math.sin((t - T_BUMP) * 12) + 6 * (1 - math.exp(-(t - T_BUMP) * 2))
def egg(cr, tt, p, ly):
    if ly == "front" and T2 <= tt < 28.9: O.draw_egg(cr, egg_x(tt), RIM + 15 + 2.5 * math.sin(tt * 2.1), 0.95)
S.prop(egg)
S.sfx(T_BUMP, "tok", 0.03)
S.hook(lambda tt, p: (p.update(head=(p["head"][0] - 6 * pulse(tt, T_BUMP + 0.06, 0.1), p["head"][1])) or p))
S.set(T_BUMP + 0.35, "tub_neck", "dead_stare", dur=0.12, look=(0.55, 0.85), tilt=0.07)
S.set(T_BUMP + 1.9, "tub_neck", "dead_stare", dur=0.12, look=(0.0, 0.0), tilt=0.0)

# the spice arrives. he does not look away.
H0, H1 = 12.0, 19.5
S.set(H0, "tub_neck", "dead_stare", dur=6.0, breath_rate=2.2, breath=1.6)          # breathing quickens
S.set(16.0, "tub_neck", "holding_it", dur=3.5, breath_rate=2.6, breath=1.8)        # eyes open up, brows lift a little
def heat(tt, p):
    if tt < H0: return p
    p["heat_fill"] = ramp(tt, H0, H1)
    p["sweat"] = max(p.get("sweat", 0.0), ramp(tt, 13.5, 14.6))
    p["twitch"] = max(p.get("twitch", 0.0), ramp(tt, 15.0, 15.4))
    p["pupil"] = min(p.get("pupil", 1.0), lerp(0.95, 0.58, ramp(tt, 16.0, 19.0)))
    p["fx_steam"] = max(p.get("fx_steam", 0.0), 0.8 * ramp(tt, 18.0, 19.5) - 0.4 * ramp(tt, 34.0, 40.0))
    if tt >= H1: p["curl_up"] = 1.0
    p["tear1"] = max(p.get("tear1", 0.0), ramp(tt, 20.0, 21.4) * (1 - ramp(tt, 40.0, 42.0)))
    return p
S.hook(heat)
S.sfx(16.5, "whine", 0.022, dur=H1 - 16.5)

# sinks. eye level. under.
T_SINK = 21.8
S.set(T_SINK, "tub_peek", "holding_it", dur=2.4, ease="smooth", quiver=0.0, breath_rate=1.0, breath=0.6)
S.set(T_SINK + 3.8, "tub_under", "dead_stare", dur=1.0, ease="inn")
for tb in (22.6, 23.3, 24.1, 26.4): S.sfx(tb, "blub", 0.035)
S.prop(lambda cr, tt, p, ly: O.draw_bubbles(cr, tt, TX + 8, RIM + 6, n=4, spread=26, rise=150, size=8, seed=3)
       if ly == "front" and 22.4 <= tt < 26.8 else None)

# ================================================================ SHOT 3: something comes down
T3 = 28.9
S.cut(T3, cam=CAM3)
def chop(t):
    """(tip, ang, gap, clip) of the giant chopsticks over time."""
    a = 1.02
    if t < 29.6: return None
    if t < 30.9:
        u = smooth((t - 29.6) / 1.3); tip = lerp((-300, -400), (TX - 15, RIM - 70), u); gap = 46
    elif t < 31.4:
        u = smooth((t - 30.9) / 0.5); tip = lerp((TX - 15, RIM - 70), (TX - 15, RIM + 40), u); gap = 46
    elif t < 32.1:
        u = (t - 31.4) / 0.7; tip = (TX - 15 + 26 * math.sin(u * 2 * math.pi * 1.5), RIM + 40 + 8 * math.cos(u * 6 * math.pi)); gap = 46
    elif t < 32.3:
        tip = (TX - 15, RIM + 40); gap = lerp(46, 10, (t - 32.1) / 0.1)
    else:
        tip = (TX - 15, RIM + 40 - 300 * ((t - 32.3) / 0.12)); gap = 10
    return tip, a, gap
def chop_draw(cr, tt, p, ly):
    if ly != "front" or not (T3 <= tt < T4): return
    c = chop(tt)
    if c: O.draw_chopsticks(cr, c[0], c[1], c[2], clip_y=RIM + 6 if c[0][1] > RIM - 30 else None, t=tt)
    if 32.3 <= tt < T4: O.draw_splash(cr, TX, RIM + 8, (tt - 32.3) / 0.5, n=16, r=300, sid=40, floor_y=RIM + 8)
S.prop(chop_draw)
S.sfx(30.95, "clack", 0.045); S.sfx(31.5, "blub", 0.03); S.sfx(32.12, "clack", 0.06); S.sfx(32.3, "sploosh", 0.07)

# ================================================================ SHOT 3b: hanging by the scruff from the chopsticks
T4 = 32.45
XH = -290                                                          # he hangs (and lands) at world x 250
S.cut(T4, cam=CAM4, x=XH)
S.set(T4, "stand", "dead_stare", dur=0.0, nowalk=1.0, feet_lag=1.0)
PIN0 = (250, 650)
T_SHAKE, T_UP, T_REL = 36.0, 37.0, 38.6
def pin(t):
    x, y = PIN0
    if T_SHAKE <= t < T_SHAKE + 0.6: y += 14 * math.sin((t - T_SHAKE) / 0.6 * 3 * 2 * math.pi)
    if t >= T_UP: u = smooth((t - T_UP) / 0.9); x, y = x - 30 * u, y - 60 * u
    return x, y
def sway(t):
    a = 0.12 * math.exp(-(t - T4) * 0.9) * math.sin((t - T4) * 2 * math.pi * 0.55)
    if t >= T_SHAKE: a += 0.05 * math.exp(-(t - T_SHAKE) * 1.5) * math.sin((t - T_SHAKE) * 2 * math.pi * 0.6)
    if t >= T_UP: a += 0.04 * math.exp(-(t - T_UP) * 1.2) * math.sin((t - T_UP) * 2 * math.pi * 0.55)
    return a
SCRUFF = dict(head=(4, -126), neck=(0, 0), hip=(-6, 340), lelb=(-46, 190), lhand=(-50, 348), relb=(42, 195), rhand=(46, 352),
              lknee=(-22, 524), lfoot=(-20, 692), rknee=(28, 522), rfoot=(26, 696))
def dangle(tt, p):
    if not (T4 <= tt < T_REL + 0.3): return p
    w = 1.0 - ramp(tt, T_REL, T_REL + 0.22, "inn")                  # let go: he drops onto his feet
    if w <= 0.0: return p
    (px_, py_), a = pin(tt), sway(tt)
    ca, sa = math.cos(a), math.sin(a)
    for j, (dx, dy) in SCRUFF.items():
        p[j] = lerp(p[j], (px_ + dx * ca - dy * sa, py_ + dx * sa + dy * ca), w)
    p["tilt"] = lerp(p["tilt"], 0.12 + a, w)
    p["lfoot_dir"] = lerp(p.get("lfoot_dir", 0), -0.25, w); p["rfoot_dir"] = lerp(p.get("rfoot_dir", 0), 0.25, w)
    return p
S.hook(dangle)
def chop_hold(cr, tt, p, ly):
    if ly != "back" or not (T4 <= tt < T_REL + 1.6): return       # behind him: they've got him by the back of the neck
    (px_, py_) = pin(tt)
    if tt < T_REL: O.draw_chopsticks(cr, (px_ + 6, py_ + 14), 1.02, 26, t=tt)
    else:                                                          # opens, then slides back up out of frame
        u = smooth((tt - T_REL - 0.05) / 1.4)
        O.draw_chopsticks(cr, (px_ + 6 - 600 * u, py_ + 14 - 900 * u), 1.02, lerp(26, 90, min(1.0, (tt - T_REL) / 0.12)), t=tt)
S.prop(chop_hold)
S.set(35.0, "stand", "dead_stare", dur=0.35, lid=1.0, nowalk=1.0, feet_lag=1.0)                  # slow blink, hanging
S.set(35.5, "stand", "dead_stare", dur=0.4, nowalk=1.0, feet_lag=1.0)
S.set(T_REL + 0.2, "stand", "dead_stare", dur=0.08, stretch=-0.35, nowalk=1.0)                    # lands: squash...
S.set(T_REL + 0.3, "stand", "dead_stare", dur=0.45, ease="back", stretch=0.0)                     # ...and up
S.sfx(T_REL, "clack", 0.05); S.sfx(T_REL + 0.21, "splat", 0.06); S.sfx(T_REL + 0.22, "thud", 0.035)
for td in (33.1, 33.9, 34.5, 35.4, 36.3, 37.2, 38.0, 39.6, 40.5): S.sfx(td, "drip", 0.016)
S.prop(lambda cr, tt, p, ly: O.draw_drips(cr, p, tt, T4, T_REL - T4 + 3.5) if ly == "front" else None)
def puddle(cr, tt, p, ly):
    if ly == "back" and tt >= T4: O.draw_puddle(cr, 250, 140 * smooth((tt - T4) / 6.0))
S.props.insert(1, puddle)                                          # under him, over the floor
S.camera(T_REL + 0.6, *CAM5, dur=1.6)                              # eases over so the sign has room
S.t = T_REL + 2.4

# ================================================================ the ask (deadpan) -- the noodle slides off mid-hold
T_ASK = S.t
HOLD = 8.0
T_SLIDE = T_ASK + 6.9 + 3.6
def noodle(cr, tt, p):
    if tt < T_SLIDE:
        O.draw_noodle_hat(cr, p, clip_y=RIM + 4 if T2 <= tt < T4 else None); return
    u = (tt - T_SLIDE) / 0.55
    if u < 1.0:
        q = dict(p); hx, hy = p["head"]
        q["head"] = (hx + 40 * u, hy + 30 * u + 220 * u * u); q["tilt"] = p["tilt"] + 1.2 * u
        O.draw_noodle_hat(cr, q)
    else:
        O.draw_floor_noodle(cr, p["head"][0] + 75)
S.sfx(T_SLIDE + 0.55, "pat", 0.03)
S.the_ask(T_ASK, hold=HOLD, push=False)
def glance(tt, p, a=T_SLIDE + 0.75):                                # eyes flick down at it. nothing else.
    if a <= tt < a + 0.7: p["look"] = (0.45, 0.95); p["saccade"] = 0.0
    return p
S.hook(glance)

if __name__ == "__main__":
    S.render("ltcd_test1_ramen_v2.mp4")
