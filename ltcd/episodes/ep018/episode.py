"""Day 18: @gaiawhitelily "Wake up in the dinosaurs age" (Instagram, day 17 reel, 1 like).
His house: reads it, yawns, runs out to the right into a meadow, falls asleep under a tree. Time runs backwards around
him (sun and moon whip past, the tree un-grows, giant ferns sprout, a volcano rises). Footsteps ripple the puddle by
his head. He wakes, stands: a T. rex. It sniffs him; he freezes; his curl springs up; ROAR; chase (log hurdle, a near
miss); he hides in a little cave - its tiny arms can't reach. A meteor. He pulls out a tiny umbrella; the T. rex
squeezes its head under it. IMPACT. They're fine; the umbrella isn't. A tiny-arm high five; it stomps off. The ask.
See BEATS.md.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import ramp, lerp, pulse, FLOOR_Y
from ink import smooth, sketch_line, draw_text

HERE = os.path.dirname(os.path.abspath(__file__))
FR = 1 / 30

# ================================================================ places
IX = 1300000.0                                      # his house, inside (day 17)
TVX = IX + 650.0; LAMPX = IX + 230.0; CLOCK = (IX - 150.0, 560.0); OUTLET = (IX + 1010.0, FLOOR_Y - 230.0)
SINKX = IX + 1240.0; FRIDGEX = IX + 1600.0; DOORX = IX - 900.0
DX = 2000000.0                                      # the meadow -> the dinosaur age
TREE = DX - 470.0
PUDDLE = (DX - 600.0, FLOOR_Y - 40.0)
VOLC = DX + 900.0
LOG = DX + 1700.0
CAVE = DX + 3600.0
FERNS = [(DX - 1500, 700), (DX - 1150, 560), (DX - 820, 760), (DX - 120, 520), (DX + 260, 700), (DX + 620, 620),
         (DX + 1100, 760), (DX + 1450, 560), (DX + 1950, 700), (DX + 2350, 600), (DX + 2600, 760),
         (DX + 4300, 700), (DX + 4700, 600), (DX + 1000 - 2600, 650)]
CYCADS = [(DX - 1350, 500), (DX + 450, 560), (DX + 1250, 480), (DX + 2150, 520), (DX + 4500, 520)]

# ================================================================ timeline
T_READ = 0.45; T_YAWN = 2.0; T_UP = 2.55; T_RUN = 2.95; CUT1 = 3.6
T_IN1 = 4.4; T_FLOP = 4.5; T_SLEEP = 4.95
TL0, TL1 = 5.6, 10.2
HITS = [10.9, 11.9, 14.3]
T_EYE = 12.2; T_SIT = 12.6; T_LOOKL = 13.1; T_LOOKR = 13.6; T_STAND = 14.0
PT0, PT1 = 12.8, 14.8                               # pterodactyl flyby
T_STOMP = 15.0
T_TILT = 15.7
T_LOWER = 16.9
T_SNIFF = 17.9; T_PUFF = 18.4
T_FREEZE = 18.7
T_BOING = 20.4; T_SNAP = 20.7; T_ROAR = 21.1; T_ROAR1 = 22.0
CH0, CH1 = 22.3, 27.4                               # the chase
T_CHOMP = 26.2
T_CAVE = 27.4; T_BONK = 27.95; ARMS0, ARMS1 = 28.6, 30.4; T_ARMLOOK = 30.6
T_RUMB = 31.6; MET0, T_IMP = 32.2, 40.6
T_LOOKUP = 32.0; T_EACH = 33.3; T_US1 = 34.0
T_OUT = 34.6
T_PULL = 35.6
T_RAISE = 38.35; T_OPEN = 38.6
T_RXLOOK = 38.8; T_SCOOT = 39.3
T_WHITE = T_IMP + 1.4
T_CRUMB = 43.4
T_EACH2 = 44.2; T_HF = 44.7; T_REACH = 45.5; T_GAP = 46.0; T_JUMP = 46.4; T_PAT = 46.62
T_TURN = 47.7; WALK0, WALK1 = 48.0, 49.8
T_US2 = 49.8
T_ASK = 50.4

UMB_C = CAVE - 850.0                                # where he stands for the umbrella + the ask (his centre)

# ================================================================ scene
def P(name, **kw): L.POSES[name] = kw
P("floor_pad", **dict(L.POSES["sit_floor"], lelb=(470, 1210), lhand=(515, 1250), relb=(610, 1210), rhand=(570, 1250), lhand_t="grip", rhand_t="grip"))
P("umb_up", relb=(650, 790), rhand=(615, 600), rhand_t="grip")
P("reach_up", relb=(660, 720), rhand=(690, 540), rhand_t="open", tiptoe=1.0)
P("freeze", lelb=(470, 975), lhand=(455, 1130), relb=(610, 975), rhand=(625, 1130), lhand_t="open", rhand_t="open")
P("huddle", **dict(L.POSES["sit_floor"], lelb=(470, 1210), lhand=(500, 1290), relb=(610, 1210), rhand=(580, 1290)))

S = M.Scene(start_body="floor_pad", start_face="deadpan", x0=IX - 360)
S.auto_blinks = True
S.floor = False
S.card("gaiawhitelily", "Wake up in the dinosaurs age", "1", t0=0.3)
CAM0 = (IX + 180, 880, 1.0)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0

# ---------------------------------------------------------------- tiny keyframe helper for the T. rex
class K:
    def __init__(self, **v): self.keys = [(0.0, 0.0, dict(v))]; self.cur = dict(v)
    def to(self, t, dur=0.3, **v):
        self.cur = dict(self.cur); self.cur.update(v); self.keys.append((t, dur, dict(self.cur))); return self
    def at(self, t):
        prev = self.keys[0][2]; out = dict(prev)
        for t0, d, vals in self.keys[1:]:
            if t < t0: break
            u = 1.0 if d <= 0 else smooth((t - t0) / d)
            out = {k: (lerp(prev[k], vals[k], u) if isinstance(vals[k], (int, float)) else (vals[k] if u > 0.5 else prev[k])) for k in vals}
            if u >= 1.0: prev = vals
            else: prev = out
        return out

# precompute nose offsets for aiming
RS = 2.1
def nose_off(lean, pitch, s=RS):
    st = dict(O.DINO); st.update(s=s, lean=lean); return O.trex_pt(0.0, st, 1, pitch, "nose")
NO_SNIFF = nose_off(1.5, 0.45)          # (dx, y)
NO_CAVE = nose_off(2.0, 0.5)
NO_CHASE = nose_off(0.8, 0.2)
ARM0 = (lambda st: O.trex_pt(0.0, st, 1, 0.2, "arm"))(dict(O.DINO, s=RS, lean=0.0))

HEAD_STAND = (540.0, 640.0)
SNIFF_X = DX - 30 - NO_SNIFF[0] - 60      # his head at DX (standing centre)
CAVE_X = (CAVE - 470) - NO_CAVE[0]
UMB_X = (UMB_C - 120) - NO_SNIFF[0]
HF_X = (UMB_C + 150) - ARM0[0]
HOP_HF = max(100.0, 540.0 - ARM0[1] - 30.0)              # its tiny arm right above his reaching hand

R = K(X=DX - 2600.0, lean=0.0, pitch=0.0, mouth=0.0, lx=-0.6, ly=0.2, arms=0.0, lid=0.0, brow=0.0, worry=0.0,
      smile=0.0, face=1, gait=0.0, happy=0.0, show=1.0)
R.to(13.6, 0.0, gait=1.0)
R.to(13.6, T_STOMP - 13.6 - 0.05, X=DX - 560.0)
R.to(T_STOMP, 0.05, gait=0.0)
R.to(T_TILT + 0.4, 0.5, lx=-0.3, ly=0.9)                          # looks down at him
R.to(T_LOWER, 0.9, X=SNIFF_X, lean=1.5, pitch=0.45, lx=-0.2, ly=0.5)
R.to(T_FREEZE, 0.6, lid=0.35, brow=-0.3)
R.to(T_SNAP, 0.1, lx=-0.1, ly=-0.9, lid=0.0, brow=-0.8)
R.to(T_ROAR, 0.15, mouth=1.0)
R.to(T_ROAR1, 0.2, mouth=0.0, lean=0.8, pitch=0.2, lx=-0.9, ly=0.3)
R.to(CH0, 0.01, gait=1.0)
R.to(T_CHOMP - 0.5, 0.25, mouth=1.0)
R.to(T_CHOMP, 0.08, mouth=0.0)
R.to(T_CAVE + 0.1, 0.01, gait=1.0)
R.to(T_BONK - 0.4, 0.4, lean=2.0, pitch=0.5, mouth=0.0)
R.to(T_BONK, 0.01, gait=0.0)
R.to(T_BONK + 0.1, 0.2, brow=0.6, worry=0.8, lid=0.2)
R.to(ARMS0, 0.3, arms=1.0, brow=-0.5, worry=0.0, lid=0.0)
R.to(ARMS1, 0.3, arms=0.0)
R.to(T_ARMLOOK, 0.35, lx=0.6, ly=1.0, brow=0.9, worry=1.0)
R.to(T_LOOKUP + 0.2, 0.5, lean=0.6, pitch=0.1, lx=-0.7, ly=-1.0, brow=0.8, worry=0.6)
R.to(T_EACH, 0.3, lx=-0.2, ly=0.6, brow=0.4)
R.to(T_OUT - 0.4, 0.01, gait=1.0)
R.to(T_OUT - 0.4, 1.0, X=UMB_X - 900.0, lean=0.3, pitch=0.0, lx=-0.7, ly=-0.9)
R.to(T_OUT + 0.65, 0.01, gait=0.0)
R.to(T_RXLOOK, 0.25, lx=-0.1, ly=-1.0, brow=0.6)                  # the umbrella
R.to(T_RXLOOK + 0.35, 0.25, lx=-0.9, ly=-0.8)                     # the meteor
R.to(T_SCOOT, 0.01, gait=1.0)
R.to(T_SCOOT, 0.7, X=UMB_X, lean=1.5, pitch=0.45, lx=0.5, ly=-0.6, worry=0.8, brow=0.6)
R.to(T_SCOOT + 0.72, 0.01, gait=0.0)
R.to(T_EACH2, 0.3, lx=1.0, ly=0.0, worry=0.0, brow=0.3)
R.to(T_HF, 0.6, X=HF_X, lean=0.0, pitch=0.2, lx=-0.3, ly=0.9, smile=0.6, arms=0.15)
R.to(T_PAT + 0.2, 0.2, happy=1.0, smile=1.0, arms=0.0)
R.to(T_TURN, 0.0, face=-1, pitch=0.0, happy=0.0, smile=0.4, lx=-0.6, ly=0.1)
R.to(WALK0, 0.01, gait=1.0)
R.to(WALK0, WALK1 - WALK0, X=HF_X - 2600.0)

def rex_x(t):
    """during the chase it follows him (keyframes only hold its look/mouth)."""
    if CH0 <= t < T_CAVE + 0.1:
        hx = his_cx(t)
        gap = lerp(1250, 980, smooth(ramp(t, CH0, T_CHOMP))) + 260 * smooth(ramp(t, T_CHOMP, T_CAVE))
        return hx - NO_CHASE[0] - (gap - 900)
    if T_CAVE + 0.1 <= t < T_BONK:
        a = his_cx(T_CAVE + 0.1) - NO_CHASE[0] - (lerp(1250, 980, 1.0) + 260 - 900)
        return lerp(a, CAVE_X, smooth(ramp(t, T_CAVE + 0.1, T_BONK)))
    if T_BONK <= t < T_OUT - 0.4: return CAVE_X
    return R.at(t)["X"]

def rex_state(t):
    v = R.at(t)
    st = dict(O.DINO)
    st.update(s=RS, lean=v["lean"], mouth=v["mouth"], look=(v["lx"], v["ly"]), arms=v["arms"], lid=v["lid"], brow=v["brow"],
              worry=v["worry"], smile=v["smile"], eyes="happy" if v["happy"] > 0.5 else "normal")
    if v["gait"] > 0.5: st["walk"] = (t * 9.0) % (2 * math.pi) + 0.001
    return rex_x(t), st, int(v["face"]), v["pitch"]

def rex_visible(t): return CUT1 <= t and t >= 13.0

# ---------------------------------------------------------------- his x during the chase
def his_cx(t):
    return lerp(DX, CAVE - 250.0, (min(max(t, CH0), CH1) - CH0) / (CH1 - CH0))

# ================================================================ world
def day_phase(t):
    u = ramp(t, TL0, TL1, "linear")
    return 2 * math.pi * 5.0 * u * u
def night_amt(t):
    if not (TL0 <= t < TL1): return 0.0
    return 0.5 - 0.5 * math.cos(day_phase(t))
def pre_amt(t): return smooth(ramp(t, TL0 + 0.5, TL1 - 0.8))
def after_amt(t): return 1.0 if t >= T_IMP else 0.0
def glow_amt(t):
    if t >= T_IMP: return 0.0
    return smooth(ramp(t, T_RUMB, T_IMP)) * 0.8
def meteor_pos(t):
    u = ramp(t, MET0, T_IMP, "linear"); e = u ** 1.6
    a = (CAVE - 1900.0, -400.0); b = (UMB_C - 820.0, FLOOR_Y - 330.0)
    return lerp(a[0], b[0], e), lerp(a[1], b[1], e), 40 + 300 * e

def sky_fx(cr, t):
    if PT0 <= t < PT1:
        u = (t - PT0) / (PT1 - PT0)
        O.draw_pterodactyl(cr, lerp(DX + 900, DX - 900, u), 740 - 80 * math.sin(math.pi * u), s=0.8, flap=math.sin(t * 9), facing=-1)
    if MET0 <= t < T_IMP:
        mx, my, mr = meteor_pos(t)
        O.draw_meteor(cr, mx, my, mr, t)

def world(cr, t):
    O._T_GLOB[0] = t
    if t < CUT1 - FR:
        O.draw_room(cr, t, IX - 3000, IX + 3000, door_x=DOORX, frame_x=IX - 450, frame_fall=1.0, kitchen_x=IX + 1000)
        O.draw_wall_clock(cr, *CLOCK, hour=7.0, minute=20.0)
        O.draw_outlet(cr, *OUTLET)
        sketch_line(cr, [(TVX + 280, FLOOR_Y - 330), (OUTLET[0] - 10, FLOOR_Y - 250), (OUTLET[0], OUTLET[1])], 5, sid=20200, amp=0.4)
        O.draw_tv(cr, TVX, FLOOR_Y - 10, t, screen="game")
        O.draw_sink_counter(cr, SINKX, FLOOR_Y - 10, n=25, t=t)
        O.draw_fridge(cr, FRIDGEX, FLOOR_Y - 10, photo=1.0)
        return
    ph = day_phase(t) if TL0 <= t < TL1 else 0.0
    cx = L.cam_track.at(t)[0]
    sun = moon = None
    if TL0 <= t < TL1:
        R_ = 1700.0; c0 = (cx, FLOOR_Y - 300)
        sun = (c0[0] - 750 * math.sin(ph), c0[1] - 1450 * math.cos(ph))
        moon = (c0[0] + 750 * math.sin(ph), c0[1] + 1450 * math.cos(ph))
    elif t < TL0:
        sun = (cx + 700, FLOOR_Y - 1150)
    O.draw_dino_world(cr, t, DX - 6000, DX + 9000, pre=pre_amt(t), night=night_amt(t), after=after_amt(t), sun=sun, moon=moon,
                      volcano=(VOLC, 1100 * smooth(ramp(t, TL0 + 2.2, TL1 - 0.3)), 0.0), tree=TREE,
                      tree_g=1.0 - smooth(ramp(t, TL0 + 0.8, TL0 + 3.0)), ferns=FERNS, cycads=CYCADS,
                      fern_g=smooth(ramp(t, TL0 + 2.0, TL1 - 0.4)), glow=glow_amt(t), cave=CAVE, sky_fx=lambda c: sky_fx(c, t))
    if t < T_IMP:
        O.draw_puddle_rings(cr, *PUDDLE, 130, t, HITS + [T_STOMP])
        O.draw_log(cr, LOG, FLOOR_Y - 20, smash=1.0 if t >= log_smash_t() else 0.0)
    else:
        O.draw_log(cr, LOG, FLOOR_Y - 20, smash=1.0)
S.background(world)

_LOG_T = [None]
def log_smash_t():
    if _LOG_T[0] is None:
        tt = CH0
        while tt < T_CAVE and rex_x(tt) < LOG - 60: tt += 0.02
        _LOG_T[0] = tt
    return _LOG_T[0]

# ================================================================ his acting
# A: the house - reads, yawns, runs out right
S.set(0.0, "floor_pad", "deadpan", dur=0.0, turn=1.0, look=(1.0, -0.3), lid=0.2)
for k in range(5): S.sfx(0.1 + k * 0.38, "tick", 0.018)
S.set(T_READ, "floor_pad", "deadpan", dur=0.35, turn=0.3, look=(0.7, -0.9), tilt=-0.05)
def read_hk(tt, p):
    if T_READ + 0.35 <= tt < T_YAWN - 0.1:
        k = (tt - T_READ - 0.35) / 0.8; u = k % 1.0
        p["look"] = (0.4 + 0.5 * smooth(u), -0.92)
    return p
S.hook(read_hk)
S.set(T_YAWN, "sit_floor", "yawning", dur=0.3, lelb=(430, 900), lhand=(420, 800), relb=(650, 900), rhand=(660, 800), lhand_t="fist", rhand_t="fist")
S.set(T_UP, "stand", "sleepy", dur=0.3)
S.set(T_RUN, "stand", "sleepy", dur=0.15, turn=1.2, look=(1.0, 0.0))
S.run_to(T_RUN, IX + 650, CUT1 - T_RUN)
S.sfx(T_RUN, "whoosh", 0.04)

# B: meadow - runs in, flops down under the tree, asleep
S.cut(CUT1 - FR, cam=(DX - 100, 1050, 1.0), x=DX - 540 - 560)
S.set(CUT1 - FR, "stand", "sleepy", dur=0.0, turn=1.2, look=(1.0, 0.0), run=1.0)
S.xkeys.append((CUT1, DX - 540 - 150, T_IN1 - CUT1, "linear")); S.x = DX - 540 - 150
S.set(T_IN1, "crouch", "sleepy", dur=0.12, run=0.0, nowalk=1.0)
S.xkeys.append((T_FLOP, DX - 650, 0.35)); S.x = DX - 650
S.set(T_FLOP, "lie_back", "sleepy", dur=0.35, nowalk=1.0)
S.sfx(T_FLOP + 0.3, "thud", 0.05)
S.set(T_SLEEP, "lie_back", "asleep", dur=0.4, nowalk=1.0, tilt=-1.45)
for k in range(4): S.sfx(T_SLEEP + 0.3 + k * 1.6, "snore", 0.03)

# C: the time-lapse (camera pulls out, then back in)
S.camera(TL0, DX + 250, 720, 0.6, 1.0)
S.camera(TL1 - 0.3, DX - 250, 1050, 1.0, 0.7)
S.sfx(TL0, "slide_down", 0.05, dur=TL1 - TL0)
for k in range(9):
    u = math.sqrt((k + 0.5) / 10)                     # a soft whoosh per day, faster and faster
    S.sfx(TL0 + u * (TL1 - TL0), "whoosh", 0.025)

# D: the footsteps ripple the puddle; he wakes, sits up, stands
for i, h in enumerate(HITS):
    S.sfx(h, "thud", 0.09 + 0.03 * i); S.shake(h, 0.3, 6 + 4 * i)
S.set(T_EYE, "lie_back", "dead_stare", dur=0.2, nowalk=1.0, tilt=-1.45, look=(-0.6, 0.3), lid=0.5)
S.xkeys.append((T_SIT, DX - 540, 0.45)); S.x = DX - 540
S.set(T_SIT, "sit_floor", "deadpan", dur=0.45, nowalk=1.0, look=(0.0, 0.0))
S.set(T_LOOKL, "sit_floor", "deadpan", dur=0.3, nowalk=1.0, look=(-1.0, -0.2), turn=-0.5)
S.set(T_LOOKR, "sit_floor", "deadpan", dur=0.3, nowalk=1.0, look=(0.8, -0.8), turn=0.4)       # the pterodactyl
S.set(T_STAND - 0.05, "crouch", "deadpan", dur=0.25, look=(0.0, 0.0), turn=0.0)
S.set(T_STAND + 0.25, "stand", "deadpan", dur=0.3, look=(-0.3, 0.6))
S.set(HITS[2] + 0.2, "stand", "deadpan", dur=0.3, look=(-0.5, 0.9), lid=0.25)                 # looks at the puddle
S.sfx(T_STOMP, "thud", 0.2); S.shake(T_STOMP, 0.45, 24)
S.set(T_STOMP + 0.15, "stand", "dead_stare", dur=0.1, ease="snap", look=(-0.5, 0.9), eyescale=1.2, curl_up=0.0)
S.set(T_STOMP + 0.5, "stand", "dead_stare", dur=0.6, look=(-1.0, 0.2), turn=-0.6, eyescale=1.1)

# E: the T. rex. tilt up; it lowers its head; sniff; he freezes
S.cut(T_TILT - FR, cam=(DX - 450, 700, 0.42))
S.set(T_TILT + 0.3, "stand", "dead_stare", dur=0.8, look=(-0.8, -1.0), turn=-0.6, tilt=0.12, eyescale=1.1)
S.camera(T_LOWER + 0.1, DX - 260, 860, 0.86, 1.0)
S.set(T_LOWER + 0.5, "freeze", "holding_it", dur=0.5, look=(-1.0, 0.0), turn=-0.5, sweat=0.0)
S.sfx(T_SNIFF, "whoosh", 0.06); S.sfx(T_PUFF, "whoosh", 0.07)
S.set(T_SNIFF, "freeze", "holding_it", dur=0.3, look=(-1.0, 0.0), turn=-0.5, lean=-0.06, tilt=-0.1)
S.set(T_PUFF, "freeze", "holding_it", dur=0.12, ease="snap", look=(-1.0, 0.0), turn=-0.5, lean=0.06, tilt=0.18, lid=0.6)
S.set(T_FREEZE, "freeze", "holding_it", dur=0.4, look=(-1.0, 0.0), turn=-0.5)
S.set(T_FREEZE + 0.4, "freeze", "holding_it", dur=1.2, look=(-1.0, 0.0), turn=-0.5, sweat=1.0, quiver=1.0)
for k, tt in enumerate([18.9, 19.4, 19.8, 20.1, 20.35]): S.sfx(tt, "thud", 0.035 + 0.006 * k)
S.camera(T_FREEZE + 0.2, DX - 200, 830, 0.98, 1.6)
S.set(T_BOING, "freeze", "holding_it", dur=0.05, ease="snap", look=(-1.0, 0.0), turn=-0.5, sweat=1.0, quiver=1.0, curl_up=1.0)
S.sfx(T_BOING, "boing", 0.08)
S.set(T_BOING + 0.25, "freeze", "dead_stare", dur=0.2, look=(-0.2, -1.0), turn=-0.3, sweat=1.0, curl_up=1.0)   # eyes up at his curl
S.set(T_SNAP + 0.15, "freeze", "dead_stare", dur=0.2, look=(-1.0, 0.0), turn=-0.5, sweat=1.0, curl_up=1.0)
S.sfx(T_ROAR, "wind", 0.3, dur=0.9); S.sfx(T_ROAR, "thud", 0.12); S.shake(T_ROAR, 0.9, 16)
S.set(T_ROAR + 0.05, "freeze", "shocked", dur=0.1, ease="snap", look=(-1.0, 0.0), turn=-0.5, lean=0.12, tilt=0.3, curl_up=1.0, fx_ex=0.0)

# F: the chase
S.camera(T_ROAR1, DX + 100, 740, 0.56, 0.5)
S.camera(CH0 + 0.5, CAVE - 550, 740, 0.56, CH1 - CH0 - 0.5, ease="linear")
S.set(T_ROAR1, "stand", "scared", dur=0.15, turn=1.2, look=(1.0, 0.0), run=1.0, fx_nervous=0.0, shiver=0.0)
S.xkeys.append((CH0, CAVE - 250.0 - 540, CH1 - CH0, "linear")); S.x = CAVE - 250.0 - 540
S._hop(24.88, 210, 0.3)                                      # hurdles the log
S.sfx(24.65, "whoosh", 0.04)
def chase_sfx():
    tt = CH0 + 0.2
    while tt < T_CAVE:
        S.sfx(tt, "thud", 0.06); tt += 0.35
chase_sfx()
S.sfx(T_CHOMP, "chomp", 0.12)
S.set(T_CHOMP + 0.05, "stand", "shocked", dur=0.08, ease="snap", turn=1.2, look=(-1.0, 0.0), run=1.0, fx_ex=0.0)
S.set(T_CHOMP + 0.5, "stand", "scared", dur=0.2, turn=1.2, look=(1.0, 0.0), run=1.0)

# G: the cave - huddles inside; the snout jams; tiny arms
S.set(T_CAVE, "huddle", "scared", dur=0.2, run=0.0, nowalk=1.0, turn=-0.8, look=(-1.0, 0.0))
S.camera(T_CAVE, CAVE - 750, 960, 0.72, 0.6)
S.sfx(T_BONK, "bonk", 0.1); S.shake(T_BONK, 0.35, 12)
S.set(T_BONK + 0.3, "huddle", "deadpan", dur=0.4, nowalk=1.0, turn=-0.8, look=(-1.0, -0.2))
ARM_C = O.trex_pt(CAVE_X, dict(O.DINO, s=RS, lean=2.0), 1, 0.5, "arm")
S.camera(ARMS0 - 0.1, ARM_C[0] + 180, ARM_C[1] + 160, 1.0, 0.5)
S.camera(ARMS1 + 0.2, CAVE - 750, 960, 0.72, 0.5)
S.set(ARMS0 + 0.4, "huddle", "deadpan", dur=0.4, nowalk=1.0, turn=-0.8, look=(-1.0, 0.2), lid=0.45)
S.set(T_ARMLOOK + 0.3, "huddle", "deadpan", dur=0.3, nowalk=1.0, turn=-0.4, look=(-0.2, 0.0), lid=0.4)   # to us

# H: the meteor
S.sfx(T_RUMB, "wind", 0.12, dur=T_IMP - T_RUMB)
S.camera(T_LOOKUP, CAVE - 1050, 520, 0.5, 1.2)
S.set(T_LOOKUP + 0.2, "huddle", "dead_stare", dur=0.5, nowalk=1.0, turn=-0.6, look=(-0.8, -1.0), tilt=0.15)
S.set(T_EACH + 0.3, "huddle", "dead_stare", dur=0.3, nowalk=1.0, turn=-0.8, look=(-1.0, 0.0))
S.set(T_US1, "huddle", "dead_stare", dur=0.3, nowalk=1.0, turn=0.0, look=(0.0, 0.0))

# I: out, the umbrella
S.set(T_OUT, "crouch", "deadpan", dur=0.3, turn=-0.8, look=(-1.0, -0.5), nowalk=1.0)
S.set(T_OUT + 0.35, "stand", "deadpan", dur=0.3, turn=-0.8, look=(-1.0, -0.6))
S.walk_to(T_OUT + 0.4, UMB_C - 540, 0.6)
S.camera(T_OUT, UMB_C - 250, 760, 0.66, 1.0)
S.set(T_PULL - 0.05, "stand", "deadpan", dur=0.2, turn=0.0, look=(0.0, 0.0))
def umb_draw(cr, x, y, s, tt, p):
    O.draw_umbrella(cr, x, y + 20, s=0.8 * s, open_=smooth(ramp(tt, T_OPEN, T_OPEN + 0.25)), burnt=1.0 if tt >= T_IMP else 0.0,
                    crumble=ramp(tt, T_CRUMB, T_CRUMB + 0.7))
S.pocket_pull(T_PULL, "umbrella", umb_draw, (0, 0), layer="front", narrow_w=0, held=True, offset=(0, 0))
import character as C
for i, k in enumerate(S.keys):
    if T_PULL - 0.01 <= k[0] < T_RAISE and len(k) > 2:
        d = dict(k[1]); lk = d.get("look"); d.update(C.EXPR["deadpan"]); d["look"] = lk; d.update(blush=0.0, eyes="normal", eyescale=1.0, open=0.0, fx_sparkle=0.0)
        S.keys[i] = (k[0], d) + tuple(k[2:])
S.set(T_RAISE, "umb_up", "deadpan", dur=0.3, look=(0.2, -0.9))
S.sfx(T_OPEN, "flip", 0.08)
S.set(T_OPEN + 0.4, "umb_up", "deadpan", dur=0.3, look=(0.0, 0.0))
S.set(T_SCOOT + 0.5, "umb_up", "deadpan", dur=0.3, look=(-1.0, 0.0), turn=-0.4)
S.set(T_SCOOT + 1.0, "umb_up", "dead_stare", dur=0.3, look=(0.0, 0.0), turn=0.0)
S.camera(T_SCOOT, UMB_C - 330, 820, 0.78, 1.2)
S.shake(T_SCOOT + 0.4, T_IMP - T_SCOOT - 0.4, 6)

# impact
S.sfx(T_IMP, "kaboom", 0.5); S.shake(T_IMP, 1.6, 44)
S.sfx(T_IMP + 1.2, "whine", 0.025, dur=2.4)
S.set(T_IMP, "umb_up", "dead_stare", dur=0.0, look=(0.0, 0.0), turn=0.0)
S.set(T_CRUMB, "umb_up", "dead_stare", dur=0.3, look=(0.0, -1.0))            # looks up at what's left
S.sfx(T_CRUMB, "poof", 0.05)
S.set(T_CRUMB + 0.6, "stand", "dead_stare", dur=0.35, look=(0.3, 0.6))
S.objects["umbrella"]["t_off"] = T_CRUMB + 0.75
S.set(T_EACH2, "stand", "deadpan", dur=0.3, look=(-1.0, -0.2), turn=-0.5)

# J: the high five
S.camera(T_HF, UMB_C - 350, 640, 0.45, 0.8)
S.set(T_HF + 0.6, "stand", "deadpan", dur=0.3, look=(-0.3, -1.0), turn=-0.2)
S.camera(T_REACH - 0.1, UMB_C - 200, 760, 0.8, 0.5)
S.camera(T_PAT + 0.45, UMB_C - 350, 640, 0.45, 0.6)
S.set(T_REACH, "reach_up", "deadpan", dur=0.35, look=(0.2, -1.0), turn=0.0)
S.set(T_GAP, "reach_up", "dead_stare", dur=0.25, look=(0.5, -1.0), turn=0.2, lid=0.35)
S.set(T_JUMP - 0.15, "crouch", "deadpan", dur=0.12, look=(0.3, -1.0), nowalk=1.0)
S.set(T_JUMP, "reach_up", "deadpan", dur=0.1, ease="snap", look=(0.3, -1.0), nowalk=1.0)
S._hop(T_JUMP + 0.22, HOP_HF, 0.2)
S.sfx(T_PAT, "pat", 0.1); S.sfx(T_PAT + 0.3, "ding", 0.05)
S.set(T_PAT + 0.4, "stand", "deadpan", dur=0.3, look=(-0.4, -0.8), smile=0.15)
for k in range(5): S.sfx(WALK0 + 0.15 + k * 0.35, "thud", 0.07 - 0.01 * k)
S.set(T_TURN + 0.4, "stand", "deadpan", dur=0.4, look=(-1.0, -0.3), turn=-0.6)
S.camera(T_TURN + 0.4, UMB_C, 940, 1.18, 1.4)
S.set(T_US2, "stand", "deadpan", dur=0.35, look=(0.0, 0.0), turn=0.0)

# K: the ask
S.t = T_ASK
S.x = UMB_C - 540
S.the_ask(T_ASK, hold=8.0)
S.blink(1.0, 6.2, 13.0, 27.0, 33.6, 45.0, 49.0)

# ================================================================ the T. rex + fx props
def rex_layer(cr, t, p, ly):
    if ly != "back" or not rex_visible(t) or t >= WALK1 + 0.2: return
    X, st, face, pitch = rex_state(t)
    O.draw_trex(cr, X, st, t, face=face, pitch=pitch, blink=1.0 if any(0 <= t - b < 0.12 for b in (24.0, 31.2, 36.4, 45.0)) else 0.0)
    if CH0 <= t < T_CAVE and False: pass
S.prop(rex_layer)

def fx_front(cr, t, p, ly):
    if ly == "back":
        if CUT1 <= t and t >= T_CAVE - 0.2 and t < T_OUT + 0.6:
            pass
        return
    # the cave lip over him
    if T_CAVE - 2.0 <= t:
        O.draw_cave_rock(cr, CAVE, FLOOR_Y, "rim")
    X, st, face, pitch = rex_state(t) if rex_visible(t) else (0, None, 1, 0)
    if st is not None and T_SNIFF <= t < T_SNIFF + 0.45:                     # sniff: lines into the nostril
        nx, ny = O.trex_pt(X, st, face, pitch, "nose")
        u = (t - T_SNIFF) / 0.45
        for k in range(3):
            a = (p["head"][0] - 20, p["head"][1] - 40 + 40 * k); b = (nx + 10, ny)
            m = lerp(a, b, 0.3 + 0.5 * u)
            sketch_line(cr, [m, lerp(m, b, 0.4)], 4, sid=22000 + k, alpha=0.7)
        draw_text(cr, "sniff", nx - 140, ny - 230, 46, color=(30, 30, 34), alpha=math.sin(math.pi * u))
    if st is not None and T_PUFF <= t < T_PUFF + 0.4:
        nx, ny = O.trex_pt(X, st, face, pitch, "nose")
        u = (t - T_PUFF) / 0.4
        for k in range(3):
            O.draw_smoke_puff(cr, lerp(nx + 30, p["head"][0] + 40, u), ny - 20 + 40 * k - 30, 30 + 30 * u, alpha=(1 - u) * 0.8)
    if st is not None and T_ROAR <= t < T_ROAR1:
        mx, my = O.trex_pt(X, st, face, pitch, "mouth")
        u = ((t - T_ROAR) * 3.0) % 1.0
        for k in range(4):
            yy = my - 160 + 100 * k
            sketch_line(cr, [(mx + 60 + 300 * u, yy), (mx + 260 + 300 * u, yy + 10 * (k - 1.5))], 6, sid=22010 + k, alpha=0.8 * (1 - u))
    if st is not None and T_CHOMP <= t < T_CHOMP + 0.3:
        mx, my = O.trex_pt(X, st, face, pitch, "mouth")
        L.burst_lines(cr, mx + 40, my, (t - T_CHOMP) / 0.3, r0=90, r1=170, n=8, sid=22020)
    if st is not None and ARMS0 + 0.2 <= t < ARMS1 and int(t * 8) % 2 == 0:
        ax, ay = O.trex_pt(X, st, face, pitch, "arm")
        L.motion_lines(cr, ax + 60, ay - 40, -0.6, n=3, length=50, spread=26, sid=22030, width=4)
        L.motion_lines(cr, ax + 60, ay + 60, 0.6, n=3, length=50, spread=26, sid=22031, width=4)
    if T_BONK <= t < T_BONK + 0.35:
        L.burst_lines(cr, CAVE - 470, NO_CAVE[1], (t - T_BONK) / 0.35, r0=80, r1=170, n=8, sid=22021)
    if st is not None and T_PAT <= t < T_PAT + 0.3:
        L.burst_lines(cr, p["rhand"][0], p["rhand"][1] - 20, (t - T_PAT) / 0.3, r0=50, r1=110, n=8, sid=22022)
    if st is not None and log_smash_t() <= t < log_smash_t() + 0.35:
        L.burst_lines(cr, LOG, FLOOR_Y - 80, (t - log_smash_t()) / 0.35, r0=120, r1=230, n=10, sid=22023)
S.prop(fx_front)
S.sfx(log_smash_t(), "thud", 0.12); S.sfx(log_smash_t(), "clack", 0.06)

def screen_fx(cr, t):
    n = night_amt(t)
    if n > 0.01: cr.set_source_rgba(0.04, 0.05, 0.14, 0.45 * n); cr.paint()
    g = glow_amt(t)
    if g > 0.01: cr.set_source_rgba(1.0, 0.55, 0.2, 0.22 * g); cr.paint()
    if T_IMP <= t < T_WHITE:
        a = 1.0 if t < T_IMP + 0.5 else 1.0 - smooth(ramp(t, T_IMP + 0.5, T_WHITE))
        cr.set_source_rgba(1.0, 0.98, 0.92, a); cr.paint()
    if t >= T_IMP + 0.3:
        O.draw_ash(cr, t, amt=smooth(ramp(t, T_IMP + 0.3, T_IMP + 2.0)))
S.overlays.insert(0, screen_fx)

if __name__ == "__main__":
    print(f"end {S.t:.2f}", file=sys.stderr)
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        S.build()
        import cairo
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, L.W, L.H)
        for a in sys.argv[2:]:
            tt = float(a); L.render_frame(tt, surf); surf.write_to_png(f"still_{tt:05.2f}.png")
    else:
        S.render("day018.mp4")
