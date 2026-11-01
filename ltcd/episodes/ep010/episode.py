"""Day 10 — COMMENT episode: @second_degree_burn "Pick up a ring and take it to mordor" (Instagram, day 9 reel, 0 likes).
Parody of the ring-quest story (SHOW.md: parody is fine): a generic dark land - ash plain, a giant volcano, a black
tower with a giant flaming eye. The ring is one of HIS rings from green hill (the gold speed-game ring left over from
day 9). Everything drawn by us; no characters from the books/films.

SHOT 1  Green hill, past the GOAL sign (where day 9 left him). Reads the comment. One gold ring is still lying in the
        grass by his feet. He looks at it. At us. Crouches, picks it up, holds it up. Stares at it. At us.
WALK    He walks right holding the ring out. A MORDOR arrow sign. The grass ends: ash, a blood-orange sky, glowing
        cracks, ash drifting down; a volcano so big it runs out of the frame; a black tower with a giant flaming eye.
        The eye notices him and follows him. He gets hotter (sweat) and keeps walking. Stops at the foot of the tower.
STARE   He looks up at the eye. Hard cuts: the EYE (staring) / HIM (dead stare) / the EYE: it trembles, waters...
        blinks / HIM: hasn't moved. Looks at us.
CHAMBER CUT: inside the volcano, on the ledge over the lava. He holds the ring out over the drop. Long hold. Looks at
        it. At us. Lets go. It falls a long way. Plink. Silence. He looks at us. A bubble. A rumble. The lava rises.
        His eyes slowly go wide.
BOOM    FLASH. Outside: the volcano erupts, a giant lava column, and he is fired out of the top, spinning, up out of
        the sky. The eye watches him go.
HOME    CUT: green hill, quiet, the GOAL sign. Whistle. He falls into frame and lands on his butt. Beat. The ring
        falls out of the sky, bonks him on the head and lands in the grass exactly where it was at the start.
        He looks at it. At us. Stands. The ask, past the goal (where he lives).
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y
from ink import smooth

# ---------------------------------------------------------------- places
SX0 = 22871.36                             # body offset where day 9 left him (x 23411)
X0 = 540 + SX0
GOALX = 23061.36                           # the GOAL sign (showing his face) just behind him
PALMS = [(10150, 760), (12350, 880), (14100, 720), (18900, 860), (20600, 760)]
FLOWERS = [f for f in (10350, 11650, 12900, 13650, 14800, 15400, 18400, 19700, 21300, 22400) if f < 24300]
BORDER = 24900.0                           # green hill ends, the dark land starts
SIGN_X = 24560.0
SXW = SX0 + 5000.0                         # where the walk ends (x 28411)
XW = 540 + SXW
TX, TH = 29500.0, 1330.0                   # the eye tower
EYE = (TX, FLOOR_Y - TH + 40)
VX, VH = 31500.0, 3600.0                   # the volcano
VRIM = O.volcano_rim(VX, VH)
SXI = 49460.0                              # inside the volcano (x 50000)
XI = 540 + SXI
EDGE = XI + 150
LAVA_Y = FLOOR_Y + 900
RING0 = (X0 + 150, FLOOR_Y - 16)           # the leftover ring, lying in the grass

# ---------------------------------------------------------------- timeline
T_LOOKDOWN = 3.9
T_CROUCH, T_GRAB, T_UP = 5.0, 5.7, 6.2
T_WALK, T_ARR = 8.4, 20.4
T_LOOKUP = 20.9
CUT_E1, CUT_H1, CUT_E2, CUT_H2, CUT_IN = 21.7, 23.1, 24.7, 26.5, 28.2
T_TEAR, T_EBLINK = 25.0, 25.95
T_REACH = 29.9
T_DROP = 33.6
FALL = math.sqrt(2 * (LAVA_Y - 960) / 2600)
T_PLINK = T_DROP + FALL
T_RUMBLE = 37.0
T_ERUPT = 39.4
CUT_GH = 42.0
T_LAND = 43.3
T_RING = 45.4                              # the ring bonks his head
T_RLAND = 46.1
T_STAND = 49.0
T_ASK = 50.2

S = M.Scene(x0=SX0)
S.auto_blinks = False
S.card("second_degree_burn", "Pick up a ring and take it to mordor", "0", t0=0.35)
CAM0 = (X0 + 60, 930, 1.12)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0
S.sfx(0.35, "tick", 0.04)

def walk_x(t): return 540 + lerp(SX0, SXW, smooth(ramp(t, T_WALK, T_ARR, "linear")))
def _cross():
    a, b = T_WALK, T_ARR
    for _ in range(40):
        m = (a + b) / 2
        if walk_x(m) < BORDER: a = m
        else: b = m
    return a
T_CROSS = _cross()
T_NOTICE = T_CROSS + 2.2                   # the eye swings round to him

# ================================================================ worlds
def eye_state(t):
    """(look, lid, water) of the giant eye."""
    if t < T_NOTICE: look = 0.55
    elif t < CUT_IN: look = lerp(0.55, max(-1.0, min(1.0, (walk_x(t) - TX) / 1300)), smooth(ramp(t, T_NOTICE, T_NOTICE + 0.5)))
    else: look = -0.75
    if t >= T_ERUPT:                                       # watches him go: up and over to the left
        look = lerp(-0.2, -1.0, smooth(ramp(t, T_ERUPT + 0.2, T_ERUPT + 1.4)))
    lid = 0.0; water = 0.0
    if CUT_E2 <= t < CUT_H2:
        water = smooth(ramp(t, T_TEAR, T_TEAR + 0.8))
        lid = 0.12 * smooth(ramp(t, T_TEAR + 0.3, T_EBLINK - 0.05))
        if t >= T_EBLINK: lid = 1.0 - smooth(ramp(t, T_EBLINK + 0.18, T_EBLINK + 0.45)); water *= 1 - ramp(t, T_EBLINK, T_EBLINK + 0.1)
    return look, lid, water

def goal_sign(cr):
    """the GOAL sign from day 9, landed showing his face."""
    x, yb = GOALX, FLOOR_Y
    L.sketch_rect(cr, x - 12, yb - 520, x + 12, yb, 5, sid=7300, fill=(0.62, 0.64, 0.68))
    cy = yb - 690
    L.sketch_ellipse(cr, x, cy, 165, 165, 7, sid=7301, fill=(0.45, 0.70, 1.0))
    cr.save(); cr.translate(x, cy)
    L.sketch_circle(cr, 0, 8, 105, 6, sid=7302)
    for ex in (-38, 38):
        L.sketch_circle(cr, ex, -5, 22, 4, sid=7303 + (ex > 0))
        cr.arc(ex + 3, -2, 8, 0, 2 * math.pi); cr.set_source_rgb(0.07, 0.07, 0.08); cr.fill()
    L.sketch_line(cr, [(-30, 55), (30, 55)], 5, sid=7305)
    O.sketch_curve(cr, (0, -97), (-10, -150), (18, -140), 5, sid=7306)
    cr.restore()

def world(cr, t):
    if CUT_IN <= t < T_ERUPT:                              # inside the volcano
        rise = 520 * smooth(ramp(t, T_RUMBLE + 0.3, T_ERUPT))
        O.draw_lava_chamber(cr, t, EDGE, LAVA_Y, rise=rise, glow=1.0 + 0.0 * rise)
        return
    O.draw_green_hill_world(cr, t, x0=9800, x1=BORDER, palms=PALMS, flowers=FLOWERS)
    goal_sign(cr)
    O.draw_signpost(cr, SIGN_X, "MORDOR")
    look, lid, water = eye_state(t)
    O.draw_dark_land_world(cr, t, x0=BORDER, x1=45000, volcano=(VX, VH, 3400),
                           tower=dict(x=TX, h=TH, look=look, lid=lid, water=water))
S.background(world)

# ================================================================ SHOT 1: green hill. reads it. the ring.
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(0.6, react="dead_stare", lines=2, face="deadpan")
S.set(3.3, "stand", "dead_stare", dur=0.3, lid=1.0)                        # slow blink
S.set(3.65, "stand", "dead_stare", dur=0.35)
S.set(T_LOOKDOWN, "stand", "dead_stare", dur=0.4, look=(0.55, 0.95), tilt=0.06)   # the ring in the grass
S.set(T_LOOKDOWN + 0.6, "stand", "dead_stare", dur=0.4, look=(0.55, 0.95), tilt=0.12)
S.set(T_LOOKDOWN + 1.0, "stand", "dead_stare", dur=0.35, look=(0.0, 0.0), tilt=0.0)   # us
L.POSES["pick"] = dict(L.POSES["crouch"]); L.POSES["pick"].update(head=(640, 930), neck=(600, 1050), hip=(530, 1260), relb=(660, 1260), rhand=(688, 1432), lelb=(500, 1150), lhand=(560, 1250), rhand_t="open")
L.POSES["hold_ring"] = dict(relb=(650, 930), rhand=(690, 830), rhand_t="grip", swing=0.25)
S.set(T_CROUCH, "pick", "dead_stare", dur=0.45, look=(0.6, 0.9))
S.set(T_GRAB - 0.05, "pick", "dead_stare", dur=0.1, look=(0.6, 0.9), rhand_t="grip")
S.set(T_UP, "hold_ring", "dead_stare", dur=0.45, look=(0.7, -0.2))
S.sfx(T_GRAB, "ding", 0.04)
S.set(T_UP + 0.9, "hold_ring", "dead_stare", dur=0.3, look=(0.75, -0.3), tilt=0.05)
S.blink(T_UP + 1.2)
S.set(T_UP + 1.6, "hold_ring", "dead_stare", dur=0.35, look=(0.0, 0.0), tilt=0.0)   # us
S.camera(T_CROUCH, X0 + 120, 980, 1.12, 0.6)
S.camera(T_UP, X0 + 60, 930, 1.12, 0.6)

# ================================================================ WALK right into the dark land
S.xkeys.append((T_WALK, SXW, T_ARR - T_WALK, "smooth")); S.x = SXW
S.set(T_WALK, "hold_ring", "dead_stare", dur=0.3, look=(0.6, 0.0))
S.set(T_CROSS + 0.4, "hold_ring", "dead_stare", dur=0.6, look=(0.7, -0.35))      # the volcano
S.set(T_NOTICE + 0.5, "hold_ring", "dead_stare", dur=0.5, look=(0.7, -0.5))      # the eye
S.set(T_NOTICE + 2.0, "hold_ring", "deadpan", dur=1.5, look=(0.6, 0.0), sweat=0.35)
S.set(T_ARR - 2.0, "hold_ring", "deadpan", dur=1.5, look=(0.6, -0.1), sweat=0.6)
S.blink(T_WALK + 2.5, T_NOTICE + 1.4)
S.sfx(T_CROSS, "wind", 0.035, dur=CUT_IN - T_CROSS)
_ct = T_WALK
while _ct < T_ARR + 0.6:
    x = walk_x(_ct + 0.25)
    k = smooth(ramp(_ct, T_WALK, T_WALK + 2.0))
    e = smooth(ramp(_ct, T_ARR - 2.5, T_ARR + 0.5))
    z = lerp(1.12, 0.66, k); z = lerp(z, 0.6, e)
    S.camera(_ct, x + lerp(60, 300, k) + 250 * e, lerp(930, 860, k) - 60 * e, z, dur=0.1, ease="linear")
    _ct += 0.1
CAM_END = (XW + 550, 800, 0.6)
S.set(T_ARR + 0.2, "hold_ring", "dead_stare", dur=0.4, look=(0.0, 0.0), sweat=0.6)
S.set(T_LOOKUP, "hold_ring", "dead_stare", dur=0.5, look=(0.75, -0.85), tilt=-0.08, sweat=0.6)   # up at the eye
S.camera(T_ARR + 0.6, XW + 560, 790, 0.62, 1.2)

# ================================================================ STARE: hard cuts eye / him / eye / him
CAM_EYE = (EYE[0], EYE[1] + 60, 1.5)
CAM_HIM = (XW + 40, 700, 1.6)
S.cut(CUT_E1 - 1 / 30, cam=CAM_EYE)
S.camera(CUT_E1, EYE[0], EYE[1] + 60, 1.58, CUT_H1 - CUT_E1, ease="linear")
S.cut(CUT_H1 - 1 / 30, cam=CAM_HIM)
S.camera(CUT_H1, XW + 40, 700, 1.7, CUT_E2 - CUT_H1, ease="linear")
S.set(CUT_H1 - 1 / 30, "hold_ring", "dead_stare", dur=0.0, look=(0.75, -0.85), tilt=-0.08, sweat=0.7)
S.cut(CUT_E2 - 1 / 30, cam=(EYE[0], EYE[1] + 60, 1.62))
S.camera(CUT_E2, EYE[0], EYE[1] + 60, 1.75, CUT_H2 - CUT_E2, ease="linear")
S.shake(T_TEAR + 0.3, 0.6, 5)
S.sfx(T_EBLINK, "clack", 0.05)
S.cut(CUT_H2 - 1 / 30, cam=(XW + 40, 700, 1.75))
S.set(CUT_H2 + 0.7, "hold_ring", "dead_stare", dur=0.6, look=(0.0, 0.0), tilt=0.0, sweat=0.7)   # slowly back to us
S.camera(CUT_H2, XW + 40, 700, 1.82, CUT_IN - CUT_H2, ease="linear")

# ================================================================ CHAMBER: inside the volcano, over the lava
CAM_IN = (EDGE + 100, 1350, 0.6)
S.cut(CUT_IN - 1 / 30, cam=CAM_IN, x=SXI)
S.set(CUT_IN - 1 / 30, "hold_ring", "dead_stare", dur=0.0, sweat=0.8, look=(0.0, 0.0))
S.camera(CUT_IN, EDGE + 60, 1300, 0.68, T_DROP - CUT_IN, ease="linear")      # slow creep
S.set(CUT_IN + 0.5, "hold_ring", "dead_stare", dur=0.5, look=(0.7, 0.9), tilt=0.07, sweat=0.8)   # down: the lava
S.set(CUT_IN + 1.5, "hold_ring", "dead_stare", dur=0.4, look=(0.0, 0.0), tilt=0.0, sweat=0.8)
L.POSES["reach_r"] = dict(relb=(668, 935), rhand=(752, 905), rhand_t="grip")
S.set(T_REACH, "reach_r", "dead_stare", dur=0.5, look=(0.8, 0.4), sweat=0.8)
S.set(T_REACH + 1.2, "reach_r", "dead_stare", dur=0.4, look=(0.8, 0.3), tilt=0.06, sweat=0.85)    # the ring
S.set(T_REACH + 2.3, "reach_r", "dead_stare", dur=0.5, look=(0.0, 0.0), tilt=0.0, sweat=0.9)      # us. holds.
S.blink(T_REACH + 0.8)
S.set(T_DROP, "reach_r", "dead_stare", dur=0.08, ease="snap", rhand_t="open", sweat=0.9)       # lets go
S.set(T_DROP + 0.3, "reach_r", "dead_stare", dur=0.5, look=(0.8, 0.95), tilt=0.08, rhand_t="open", sweat=0.9)  # watches it fall
S.set(T_PLINK + 1.0, "stand", "dead_stare", dur=0.8, look=(0.8, 0.95), tilt=0.06, sweat=0.9)
S.set(T_PLINK + 1.8, "stand", "dead_stare", dur=0.5, look=(0.0, 0.0), tilt=0.0, sweat=0.9)       # us. nothing.
S.sfx(T_PLINK, "drip", 0.06)
S.blink(T_PLINK + 2.4)
# the slow tell
S.set(T_RUMBLE + 0.5, "stand", "dead_stare", dur=0.5, look=(0.75, 0.9), tilt=0.05, sweat=1.0)
S.set(T_RUMBLE + 1.2, "stand", "dead_stare", dur=1.6, look=(0.75, 0.9), tilt=0.05, sweat=1.0, eyescale=1.22, pupil=0.5, lid=0.0)
S.set(T_ERUPT - 0.5, "stand", "dead_stare", dur=0.4, look=(0.0, 0.0), sweat=1.0, eyescale=1.25, pupil=0.45, lid=0.0)   # us
S.sfx(T_RUMBLE, "kaboom", 0.07, dur=2.6)
S.sfx(T_RUMBLE - 0.6, "bubble", 0.05); S.sfx(T_RUMBLE + 0.7, "blub", 0.05)
for i in range(8): S.shake(T_RUMBLE + 0.3 * i, 0.35, 3 + 2.2 * i)

# ================================================================ BOOM: outside, the volcano blows, he is fired out
CAM_OUT = (31300, -2600, 0.4)
S.flash(T_ERUPT, 0.6)
S.sfx(T_ERUPT, "kaboom", 0.5, dur=2.6); S.shake(T_ERUPT, 1.2, 30)
S.cut(T_ERUPT - 1 / 30, cam=CAM_OUT, x=VX - 540)
S.set(T_ERUPT - 1 / 30, "cannonball", "dead_stare", dur=0.0, lag=0.0, nowalk=1.0, eyescale=1.2, lid=0.0)
S.sfx(T_ERUPT + 0.3, "whoosh", 0.06)
T_FLY0, T_FLY1 = T_ERUPT + 0.25, T_ERUPT + 2.1
def fired(tt, p):
    if not (T_ERUPT - 1 / 30 <= tt < CUT_GH - 1 / 30): return p
    u = max(0.0, (tt - T_FLY0) / (T_FLY1 - T_FLY0))
    if tt < T_FLY0: tx, ty, a = VX, VRIM[2] - 150, 0.0
    else:
        tx = VX - 2000 * u ** 0.8
        ty = VRIM[2] - 150 - 5600 * u ** 1.5
        a = -3 * 2 * math.pi * u
    h = p["hip"]; c, s_ = math.cos(a), math.sin(a)
    for j in L.JOINTS:
        dx, dy = p[j][0] - h[0], p[j][1] - h[1]
        p[j] = (tx + dx * c - dy * s_, ty + dx * s_ + dy * c)
    p["tilt"] = p.get("tilt", 0.0) + a
    return p
S.hook(fired)
_re = random.Random(10)
ROCKS = [(_re.uniform(-0.6, 0.6), _re.uniform(2600, 5200), _re.uniform(60, 130), _re.uniform(0, 0.5)) for _ in range(16)]
def eruption(cr, t, p, ly):
    if not (T_ERUPT <= t < CUT_GH): return
    s = t - T_ERUPT
    cx, cy = VX, VRIM[2]
    if ly == "back":
        h = 9000 * smooth(min(1.0, s / 0.5))                       # the lava column runs off the top of the frame
        w = 640 + 70 * math.sin(t * 13)
        pts = [(cx + 40 * math.sin(i * 0.9 + t * 8), cy + 40 - h * i / 24) for i in range(25)]
        O.draw_stream(cr, pts, w=w, color=O.LAVA, lumps=True)
        O.draw_stream(cr, pts, w=w * 0.45, color=O.LAVA_B, lumps=False)
        for i in range(10):                                         # smoke boiling out round the base
            a = (s * 0.5 + i / 10) % 1.0
            O.draw_smoke_puff(cr, cx + (i - 4.5) * 300 * (0.6 + a), cy + 150 - 900 * a, 260 + 420 * a, alpha=(1 - a) * 0.9, dark=0.7)
    else:
        for i, (dxk, sp, r, d) in enumerate(ROCKS):               # burning rocks thrown out
            v = s - d
            if v <= 0: continue
            x = cx + dxk * sp * v * 1.2; y = cy - sp * v * math.cos(dxk) + 2600 * v * v
            if y > FLOOR_Y: continue
            O.draw_flames(cr, [(x - dxk * 40 * k, y + 60 * k) for k in range(6)], t + i, w=r * 0.9)
            L.sketch_circle(cr, x, y, r, 5, sid=7600 + i, fill=O.DL_ROCK)
        if s < 0.8: L.draw_impact(cr, cx, cy, min(1.0, s * 3), r=900, sid=76)
S.prop(eruption)

# ================================================================ HOME: green hill. lands on his butt. the ring.
CAM_GH = (X0 + 60, 960, 1.05)
S.cut(CUT_GH - 1 / 30, cam=CAM_GH, x=SX0)
S.set(CUT_GH - 1 / 30, "cannonball", "dead_stare", dur=0.0, lag=0.0, nowalk=1.0)
S.set(T_LAND - 0.15, "sit_floor", "dead_stare", dur=0.15, lag=0.0, nowalk=1.0)
S.sfx(T_LAND - 0.7, "slide_down", 0.06, dur=0.7)
def drop_in(tt, p):
    if not (CUT_GH - 1 / 30 <= tt < T_LAND): return p
    T0 = T_LAND - 0.55
    dy = -2200 if tt < T0 else -2200 * (1 - ((tt - T0) / 0.55) ** 2)
    for j in L.JOINTS: p[j] = (p[j][0], p[j][1] + dy)
    return p
S.hook(drop_in)
S.set(T_LAND, "sit_floor", "dead_stare", dur=0.06, ease="snap", stretch=-0.3, nowalk=1.0)
S.set(T_LAND + 0.15, "sit_floor", "dead_stare", dur=0.4, ease="back", stretch=0.0, nowalk=1.0)
S.sfx(T_LAND, "thud", 0.18); S.shake(T_LAND, 0.4, 14)
def land_fx(cr, t, p, ly):
    if ly == "front" and T_LAND <= t < T_LAND + 0.8: L.draw_poof(cr, X0, FLOOR_Y - 40, (t - T_LAND) / 0.8, r=200, sid=32)
S.prop(land_fx)
S.set(T_LAND + 0.9, "sit_floor", "dead_stare", dur=0.5, look=(0.0, 0.0), nowalk=1.0)
S.blink(T_LAND + 1.3)
S.set(T_RING + 0.03, "sit_floor", "dead_stare", dur=0.08, ease="snap", nowalk=1.0, squash=0.15, lid=0.5)   # bonk
S.set(T_RING + 0.35, "sit_floor", "dead_stare", dur=0.3, nowalk=1.0)
S.sfx(T_RING, "bonk", 0.06); S.sfx(T_RLAND, "tok", 0.03); S.sfx(T_RLAND + 0.25, "tok", 0.015)
S.set(T_RLAND + 0.6, "sit_floor", "dead_stare", dur=0.45, look=(0.75, 0.6), tilt=0.06, nowalk=1.0)    # it
S.set(T_RLAND + 1.7, "sit_floor", "dead_stare", dur=0.45, look=(0.0, 0.0), tilt=0.0, nowalk=1.0)       # us
S.blink(T_RLAND + 2.3)
S.t = T_STAND
S.stand(T_STAND, face="dead_stare")
S.x = SX0
S.camera(T_STAND, X0 + 60, 930, 1.12, 1.0)

# ================================================================ the ring prop, start to finish
HEAD_TOP = 985 - 120
def ring(cr, t, p, ly):
    if t < T_GRAB:
        if ly == "back":
            O.draw_ring(cr, RING0[0], RING0[1], t, r=44, flat=0.75)
            u = (t % 2.2) / 0.5
            O.draw_sparkle(cr, RING0[0] + 30, RING0[1] - 20, u, r=40)
        return
    if t < T_DROP:
        if ly != "front": return
        if CUT_E1 - 1 / 30 <= t < CUT_IN - 1 / 30 and (t < CUT_H1 - 1 / 30 or CUT_E2 - 1 / 30 <= t < CUT_H2 - 1 / 30): return
        hx, hy = p["rhand"]
        if t < T_REACH + 0.25: O.draw_ring(cr, hx + 6, hy - 50, t, r=40, spin=0.0)    # held up, showing it
        else: O.draw_ring(cr, hx + 4, hy + 50, t, r=40, spin=0.0)                    # dangling over the drop
        L.draw_grips(cr, p)
        return
    if t < T_PLINK:                                               # falls a long way into the lava
        if ly != "front": return
        s = t - T_DROP
        y0 = 905 + 50
        O.draw_ring(cr, XI + 752 - 540 + 4, y0 + 0.5 * 2600 * s * s, t, r=40, spin=3.0)
        return
    if t < T_ERUPT:
        if ly == "front":
            O.draw_splash(cr, XI + 216, LAVA_Y, (t - T_PLINK) / 0.7, color=O.LAVA, n=8, r=120, sid=7700)
        return
    if t < CUT_GH: return
    if t < T_RING - 0.5: return
    if t < T_RING:                                                # falls out of the sky onto his head
        if ly != "front": return
        u = (t - T_RING + 0.5) / 0.5
        O.draw_ring(cr, X0 + 10, lerp(-300, HEAD_TOP - 40, u * u), t, r=44, spin=5.0); return
    if t < T_RLAND:                                               # bounces off, arcs over to the old spot
        if ly != "front": return
        u = (t - T_RING) / (T_RLAND - T_RING)
        x = lerp(X0 + 10, RING0[0], u); y = lerp(HEAD_TOP - 40, RING0[1], u) - 420 * 4 * u * (1 - u)
        O.draw_ring(cr, x, y, t, r=44, spin=6.0); return
    if ly != "back": return
    s = t - T_RLAND                                               # wobbles flat, settles
    fl = 0.75 * (1 - math.exp(-s * 5) * abs(math.cos(s * 14)))
    O.draw_ring(cr, RING0[0], RING0[1], 0.0, r=44, flat=max(0.02, fl))
S.prop(ring)
def bonk_fx(cr, t, p, ly):
    if ly == "front" and T_RING <= t < T_RING + 0.5: L.burst_lines(cr, X0 + 10, HEAD_TOP - 30, (t - T_RING) / 0.5, r0=60, r1=140, n=8, sid=78)
S.prop(bonk_fx)

# ================================================================ the ask, past the goal (where he lives)
S.t = T_ASK
S.the_ask(T_ASK, hold=8.0)

if __name__ == "__main__":
    print(f"cross {T_CROSS:.2f} notice {T_NOTICE:.2f} plink {T_PLINK:.2f} end {S.t:.2f}", file=sys.stderr)
    S.render("day010.mp4")
