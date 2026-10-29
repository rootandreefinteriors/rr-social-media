"""Day 7 — COMMENT episode: @nerdbpy "Join Hogwarts." (Instagram, day 6 reel, 0 likes; the only comment).
Generic wizard school: an owl, a parchment letter, a castle with cone-roofed towers, a giant talking patched hat.
No names, crests, house colours or characters from the books on screen (only the pinned card shows the comment).

SHOT 1  Beside the wrapper pile outside the burger place. Reads the comment. Stares. Slow blink.
OWL     An owl flaps in and drops an envelope on his head (bonk). He catches it. It unfolds: YOU'RE IN. / WIZARD
        SCHOOL. He looks at it. At us. Lets it fall.
WALK    He walks right; the camera goes with him; day turns to night and a castle rises behind him. He stops at its
        gate. Looks up at it. At us.
HAT     A giant old patched hat drops out of the sky over him, down to his knees. Only his feet stick out. Its crease
        face wakes up. HMM. It rummages around in there. ... One of its patches flips open: his eye, looking at us.
        Blink. Shut. HELLO? THERE'S NOTHING IN HERE. It starts to overload: shaking, swelling, seams glowing gold...
BOOM    A huge magic explosion of stars. He's blasted straight up out of the frame. The scorched brim lies smoking.
        A beat. He falls back down onto his butt, sooty. The burnt little leftover hat flutters down onto his head.
        It opens its eyes: FINE. YOU'RE IN.
END     He stands. The ask, at the castle gate (where he lives now), sooty, the little hat on his head.
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y
from ink import smooth, draw_text, sketch_line
import cairo

SX = 2020                       # start: body centre 2560, just right of the wrapper pile (where day 6 left him)
X0 = 540 + SX
SX2 = 3600                      # the castle gate
X2 = 540 + SX2
BORDER = 3550                   # day turns to night around here
PILE = (2210, 640, 230)
CAM0 = (2640, 945, 1.1)
CAM_ARR = (X2, 930, 0.95)
CAM_HAT = (X2, 900, 0.88)
CAM_END = (X2, 880, 1.0)

# ---------------------------------------------------------------- timeline
OWL0, DROP, OWL1 = 4.0, 5.2, 6.8
BONK, CATCH = 5.55, 6.15
OPEN = 6.9
LETGO = 9.9
T_WALK, T_ARR = 10.4, 15.0
HF0, HLAND = 17.0, 17.75        # the hat falls / lands over him
EYES = 18.6
B1 = (19.3, 21.0, "HMM.")
RUM0, RUM1 = 21.2, 23.0
B2 = (21.4, 22.9, "...")
FLAP0, FLAP1 = 23.3, 25.0       # a patch flips open: his eye
B3 = (25.2, 26.7, "HELLO?")
B4 = (27.0, 29.5, "THERE'S NOTHING IN HERE.")
OV0, BOOM = 29.5, 32.4          # overload -> boom
UP1 = BOOM + 1.0                # he's gone (up out of frame)
FALL0, LAND = 34.9, 35.45
HAT2_0, HAT2_1 = 36.2, 37.4     # the leftover hat flutters down onto his head
B5 = (38.0, 40.4, "FINE. YOU'RE IN.")
STAND = 40.7
T_ASK = 41.7

S = M.Scene(x0=SX)
S.auto_blinks = False
S.card("nerdbpy", "Join Hogwarts.", "0", t0=0.35)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0
S.sfx(0.35, "tick", 0.04)

# ================================================================ world: burger place -> (dusk) -> castle at night
LOOSE = [(2600, 0.9, 1), (2660, 0.8, 2), (2370, 1.0, 3), (3050, 0.8, 4), (2950, 0.7, 5)]
def world(cr, t):
    O.draw_burger_world(cr, t)
    sketch_line(cr, [(2500, FLOOR_Y), (BORDER + 400, FLOOR_Y)], 3.5, sid=91, amp=1.3, alpha=0.8)
    O.draw_wrapper_pile(cr, *PILE)
    for x, sc, k in LOOSE: O.draw_wrapper(cr, x, FLOOR_Y - 14 * sc, sc, sid=7700 + k)
    cr.push_group()
    O.draw_castle_world(cr, t, cx=X2)
    cr.pop_group_to_source()
    m = cairo.LinearGradient(BORDER - 350, 0, BORDER + 350, 0)
    m.add_color_stop_rgba(0, 0, 0, 0, 0); m.add_color_stop_rgba(1, 0, 0, 0, 1)
    cr.mask(m)
S.background(world)

# ================================================================ SHOT 1: reads it. stares.
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(0.6, react="dead_stare", lines=1, face="deadpan")
S.set(2.9, "stand", "dead_stare", dur=0.3, lid=1.0)                         # slow blink
S.set(3.35, "stand", "dead_stare", dur=0.4)

# ================================================================ OWL + LETTER
OWLP = Track([(0.0, (X0 - 1000.0, 330.0), 0), (OWL0, (X0 - 1000.0, 330.0), 0),
              (OWL0, (X0 + 30.0, 420.0), DROP - OWL0, "out"),
              (DROP + 0.15, (X0 + 1100.0, 120.0), OWL1 - DROP - 0.15, "inn")])
S.sfx(OWL0 + 0.2, "whoosh", 0.04); S.sfx(DROP + 0.3, "whoosh", 0.03)
def owl(cr, t, p, ly):
    if ly != "front" or not (OWL0 <= t < OWL1): return
    x, y = OWLP.at(t)
    y += 14 * math.sin(t * 11)
    O.draw_owl(cr, x, y, 1.0, 1.0, t, blink=1.0 if DROP - 0.5 <= t < DROP - 0.35 else 0.0)
    if t < DROP: O.draw_envelope(cr, x, y + 110, 0.75, 0.1)                # in its feet
def env_pos(t):
    """the envelope: dropped -> bonks his head -> bounces -> into his hands."""
    ox, oy = OWLP.at(DROP); a = (ox, oy + 14 * math.sin(DROP * 11) + 110)
    head_top = (X0 + 10, 500)
    hands = (X0, 1000)
    if t < BONK:
        u = ramp(t, DROP, BONK, "inn"); return (lerp(a[0], head_top[0], u), lerp(a[1], head_top[1], u), 0.1 + 0.5 * u)
    if t < CATCH:
        u = (t - BONK) / (CATCH - BONK)
        return (lerp(head_top[0], hands[0] + 20, u) + 60 * math.sin(math.pi * u), lerp(head_top[1], hands[1], u) - 160 * math.sin(math.pi * u),
                0.6 - 2.2 * u)
    return (*hands, 0.0)
def letter_k(t): return smooth(ramp(t, OPEN, OPEN + 0.35))                  # envelope -> open letter
def letter_c(t):
    if t < LETGO: return (X0, lerp(1000, 880, smooth(ramp(t, OPEN, OPEN + 0.5))))
    u = ramp(t, LETGO, LETGO + 1.0, "linear")
    return (X0 + 170 * u + 60 * math.sin(u * 9), lerp(880, FLOOR_Y - 14, u * u))
def letter(cr, t, p, ly):
    if t < DROP: return
    if t < OPEN:
        if ly == "front":
            x, y, a = env_pos(t); O.draw_envelope(cr, x, y, 0.75, a)
        return
    cx, cy = letter_c(t)
    if t < LETGO + 1.0:
        if ly != "front": return
        k = letter_k(t); w = lerp(120, 400, k); h = lerp(80, 300, k)
        u = ramp(t, LETGO, LETGO + 1.0)
        h *= 1 - 0.9 * u; rot = 0.25 * math.sin(u * 8) * u
        cr.save(); cr.translate(cx, cy); cr.rotate(rot); cr.translate(-cx, -cy)
        O.draw_letter(cr, cx, cy, w, max(20, h), ("YOU'RE IN.",), sub="WIZARD SCHOOL")
        cr.restore()
        if OPEN <= t < OPEN + 0.35: L.burst_lines(cr, cx, cy, (t - OPEN) / 0.35, r0=180, r1=260, n=10, sid=21)
    elif ly == "back":                                                      # lying on the ground
        O.draw_letter(cr, cx, cy, 380, 30, ())
S.sfx(BONK, "bonk", 0.06); S.sfx(CATCH, "pat", 0.04); S.sfx(OPEN, "flip", 0.06); S.sfx(LETGO + 0.95, "flip", 0.025)
def letter_hands(tt, p):
    e = smooth(ramp(tt, CATCH - 0.2, CATCH)) * (1 - smooth(ramp(tt, LETGO - 0.05, LETGO + 0.3)))
    if e < 0.001: return p
    if tt < OPEN: l, r = (X0 - 55, 1010), (X0 + 55, 1010)
    else:
        k = letter_k(tt); cx, cy = letter_c(tt); w = lerp(120, 400, k)
        l, r = (cx - w / 2 - 6, cy + 40), (cx + w / 2 + 6, cy + 40)
    p["lhand"] = lerp(p["lhand"], l, e); p["rhand"] = lerp(p["rhand"], r, e)
    p["lelb"] = lerp(p["lelb"], (l[0] + 10, l[1] + 110), e); p["relb"] = lerp(p["relb"], (r[0] - 10, r[1] + 110), e)
    if e > 0.5: p["lhand_t"] = p["rhand_t"] = "grip"
    return p
S.hook(letter_hands)

S.set(OWL0 + 0.3, "stand", "dead_stare", dur=0.4, look=(-0.8, -0.5))                          # eyes find it
S.set(OWL0 + 0.7, "stand", "dead_stare", dur=0.6, look=(-0.3, -0.85), tilt=0.04)               # ...the head follows
S.set(DROP + 0.1, "stand", "dead_stare", dur=0.3, look=(0.2, -0.9), tilt=0.0)
S.set(BONK, "stand", "dead_stare", dur=0.06, ease="snap", lid=0.85, squash=0.25)              # bonk
S.set(BONK + 0.2, "stand", "dead_stare", dur=0.3, ease="back", look=(0.1, 0.3))
S.set(CATCH + 0.1, "stand", "dead_stare", dur=0.3, look=(0.0, 0.85))                           # looks at it
S.set(OPEN + 0.5, "stand", "dead_stare", dur=0.4, look=(0.0, 0.9), lid=0.4)                    # reads it
S.set(OPEN + 1.9, "stand", "dead_stare", dur=0.4, look=(0.0, 0.0))                             # at us
S.blink(OPEN + 2.6)
S.set(LETGO + 0.3, "stand", "dead_stare", dur=0.4, look=(0.3, 0.7))                            # watches it fall

# ================================================================ WALK right, into the night
S.set(T_WALK - 0.3, "stand", "dead_stare", dur=0.3, look=(0.8, 0.0))
S.xkeys.append((T_WALK, SX2, T_ARR - T_WALK, "smooth")); S.x = SX2
S.camera(T_WALK, *CAM_ARR, dur=T_ARR - T_WALK + 0.4)
S.set(T_ARR, "stand", "dead_stare", dur=0.3, look=(0.2, 0.0))
S.blink(T_ARR + 0.3)
S.set(T_ARR + 0.5, "stand", "dead_stare", dur=0.5, look=(0.0, -0.9))                          # up at the castle
S.set(T_ARR + 0.9, "stand", "dead_stare", dur=0.6, look=(0.0, -0.9), tilt=-0.05)
S.set(T_ARR + 1.9, "stand", "dead_stare", dur=0.4, look=(0.0, 0.0), tilt=0.0)                 # at us

# ================================================================ THE HAT
HW, HH = 820.0, 1050.0
BRIM_Y = 1290.0
S.camera(HF0 - 0.6, *CAM_HAT, dur=1.0)
S.set(HF0 + 0.15, "stand", "dead_stare", dur=0.25, look=(0.0, -1.0))                          # eyes up. too late.
S.sfx(HF0 - 0.1, "slide_down", 0.04, dur=0.8); S.sfx(HLAND, "thud", 0.15); S.shake(HLAND, 0.35, 9)
S.sfx(RUM0, "rummage", 0.05, dur=1.7)
S.sfx(FLAP0, "pop", 0.03); S.sfx(FLAP1 - 0.2, "tok", 0.03)
S.sfx(OV0, "whine", 0.035, dur=BOOM - OV0)
for k, tk in enumerate((30.4, 31.0, 31.5, 31.85, 32.1)): S.sfx(tk, "pop", 0.015 + 0.004 * k)
def ov(t): return ramp(t, OV0, BOOM, "inn")                               # overload 0..1
def hat_state(t):
    st = dict(bx=X2, by=BRIM_Y, swell=1.0, bend=0.25, droop=0.55, eyes=0.0, look=(0.0, 0.0), mouth=0.0, glow=0.0)
    if t < HLAND:
        u = ramp(t, HF0, HLAND, "inn"); st["by"] = lerp(-900, BRIM_Y, u); st["droop"] = 0.55 - 0.35 * u
        return st
    s_ = math.exp(-(t - HLAND) * 5) * math.sin((t - HLAND) * 26)          # the landing wobble
    st["swell"] = 1.0 + 0.08 * s_; st["bend"] = 0.25 + 0.15 * s_
    st["eyes"] = smooth(ramp(t, EYES, EYES + 0.3))
    if t < B1[1]: st["look"] = (-0.5, -0.6) if t > B1[0] - 0.2 else (0.0, 0.0)
    if RUM0 <= t < RUM1:                                                   # rummaging around in there
        r = math.sin(math.pi * (t - RUM0) / (RUM1 - RUM0))
        st["bend"] += 0.25 * r * math.sin(t * 9); st["swell"] += 0.05 * r * math.sin(t * 13)
        st["look"] = (0.7 * math.sin(t * 5), 0.6)
    if FLAP0 <= t < FLAP1: st["look"] = (0.6, 0.4)                         # side-eyes the flap
    if B3[0] - 0.2 <= t < B3[1]: st["look"] = (0.0, 0.9)                   # looks down into itself
    if B4[0] - 0.2 <= t: st["look"] = (0.0, 0.0); st["eyes"] = 1.0 + 0.3 * ramp(t, B4[0], B4[0] + 0.3)
    for b in (B1, B3, B4, B5):
        if b[0] <= t < b[1] - 0.3 and b is not B5:
            st["mouth"] = 0.25 + 0.25 * abs(math.sin((t - b[0]) * 9))
    o = ov(t)
    if o > 0:
        st["bx"] += (6 + 24 * o) * math.sin(t * (30 + 40 * o)); st["swell"] += 0.25 * o
        st["glow"] = o; st["mouth"] = max(st["mouth"], 0.6 * o); st["eyes"] = 1.3 + 0.3 * o
        st["bend"] += 0.1 * math.sin(t * 23) * o
    return st
def hat(cr, t, p, ly):
    if ly != "front" or not (HF0 <= t < BOOM): return
    st = hat_state(t)
    O.draw_wizard_hat(cr, st["bx"], st["by"], HW, HH, t, bend=st["bend"], droop=st["droop"], swell=st["swell"],
                      eyes=st["eyes"], look=st["look"], mouth=st["mouth"], glow=st["glow"])
    # the flap: a patch over his eye that flips open (hinged at the top)
    ex, ey = X2 + 42, 636
    k = smooth(ramp(t, FLAP0, FLAP0 + 0.2)) * (1 - smooth(ramp(t, FLAP1 - 0.25, FLAP1)))
    if t >= HLAND:
        if k > 0.02:
            cr.arc(ex, ey, 62, 0, 2 * math.pi); cr.set_source_rgb(0.08, 0.06, 0.05); cr.fill()
            if k > 0.6:                                                    # his eye in there. dead stare.
                bl = 1.0 if FLAP0 + 0.95 <= t < FLAP0 + 1.12 else 0.0
                L.sketch_circle(cr, ex, ey, 44, 6, sid=7950, fill=(1, 1, 1))
                if bl < 0.5:
                    cr.arc(ex, ey + 6, 19, 0, 2 * math.pi); L.fill_ink(cr)
                    cr.arc(ex - 6, ey, 6, 0, 2 * math.pi); cr.set_source_rgb(1, 1, 1); cr.fill()
                    L.sketch_line(cr, [(ex - 44, ey - 16), (ex + 44, ey - 16)], 7, sid=7951, amp=0.2)   # heavy lid
                else:
                    L.sketch_line(cr, [(ex - 44, ey), (ex + 44, ey)], 7, sid=7952, amp=0.2)
        h = 136 * (1 - 2 * k)                                              # the patch itself
        y0 = ey - 68
        col = O.HAT_P
        L.sketch_poly(cr, [(ex - 68, y0), (ex + 68, y0), (ex + 68, y0 + h), (ex - 68, y0 + h)], 4, sid=7953, fill=col, amp=0.6)
        for j in range(5):
            xj = ex - 68 + 136 * (j + 0.5) / 5
            L.sketch_line(cr, [(xj, y0 - 7), (xj, y0 + 7)], 3, sid=7960 + j, amp=0.2,
                          color=lerp(L.INK, O.GOLD, ov(t)))
    if HLAND <= t < HLAND + 0.4: L.draw_poof(cr, X2 - 380, FLOOR_Y - 40, (t - HLAND) / 0.6, r=150, sid=41)
    if HLAND <= t < HLAND + 0.4: L.draw_poof(cr, X2 + 380, FLOOR_Y - 40, (t - HLAND) / 0.6, r=150, sid=42)
    o = ov(t)
    if o > 0.15:                                                           # sparks fizzing off the tip
        tx, ty = O.hat_pt(st["bx"], st["by"], HW, HH, 0.99, 0, st["bend"], st["droop"], st["swell"])
        for i in range(8):
            u = ((t - OV0) * (1.2 + 2.0 * o) + i / 8) % 1.0
            a = i * 2.4
            O.draw_star(cr, tx + math.cos(a) * 160 * u, ty + math.sin(a) * 120 * u - 60 * u, 10 + 14 * o * (1 - u),
                        (O.GOLD, O.VIOLET, O.CYAN)[i % 3], ang=t * 3 + i, alpha=(1 - u) * min(1.0, o * 2))
def bubbles(cr, t, p, ly):
    if ly != "front": return
    for b in (B1, B2, B3, B4):
        if b[0] <= t < b[1]:
            a = min(1.0, (t - b[0]) / 0.15, (b[1] - t) / 0.15)
            O.draw_thought(cr, X2 - 250, 410, b[2], tail=(X2 - 160, 560), size=56, max_w=360, alpha=a)
    if B5[0] <= t < B5[1]:
        a = min(1.0, (t - B5[0]) / 0.15, (B5[1] - t) / 0.15)
        hx, hy = p["head"]
        O.draw_thought(cr, X2 - 250, 520, B5[2], tail=(hx - 80, hy - 200), size=56, max_w=330, alpha=a)

# under the hat he just stands there (we only see his shins + feet)
S.set(HLAND, "stand", "dead_stare", dur=0.08, ease="snap", squash=0.15)
S.set(HLAND + 0.2, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), squash=0.0)
def shuffle(tt, p):                                                        # one foot taps, slowly, while it thinks
    if B2[0] <= tt < B2[1]:
        v = 22 * max(0.0, math.sin((tt - B2[0]) * 7))
        p["rfoot"] = (p["rfoot"][0], p["rfoot"][1] - v)
    return p
S.hook(shuffle)

# ================================================================ BOOM: blasted up, out of the frame
S.flash(BOOM, 0.45)
S.sfx(BOOM, "kaboom", 0.45, dur=2.6); S.sfx(BOOM + 0.6, "twinkle", 0.05); S.shake(BOOM, 0.9, 26)
S.set(BOOM, "cannonball", "dead_stare", dur=0.1, ease="snap", eyescale=1.25, lid=0.0, soot=0.65, frizz=1.0, lag=0.5)
S.set(FALL0 - 0.4, "sit_floor", "dead_stare", dur=0.2, soot=0.65, frizz=1.0, lag=0.5, nowalk=1.0)
def flight_y(t):
    if t < BOOM: return 0.0
    if t < FALL0: return -2600 * ramp(t, BOOM + 0.08, UP1, "inn")             # we see him go, then he's gone
    if t < LAND: u = (t - FALL0) / (LAND - FALL0); return -1750 * (1 - u * u)     # drops back in, picking up speed
    return 0.0
def flight_x(t):                                                          # up and off to the LEFT, clear of the card
    if t < FALL0: return -420 * ramp(t, BOOM + 0.08, UP1, "smooth")
    if t < LAND: u = (t - FALL0) / (LAND - FALL0); return -740 * (1 - u * u)     # drops back in from the upper left
    return 0.0
def flight(tt, p):
    y = flight_y(tt)
    if y < -0.5:
        x = flight_x(tt)
        for j in L.JOINTS: p[j] = (p[j][0] + x, p[j][1] + y)
    return p
S.hook(flight)
def boom(cr, t, p, ly):
    if ly != "front" or t < BOOM: return
    O.draw_magic_burst(cr, X2, 900, t - BOOM, part="stars")
    rnd = random.Random(3)
    for i in range(10):                                                   # shreds of hat
        a = rnd.uniform(-math.pi, 0); sp = rnd.uniform(500, 1100); u = t - BOOM
        if u > 2.6: break
        x = X2 + math.cos(a) * sp * u; y = 800 + math.sin(a) * sp * u + 700 * u * u
        cr.save(); cr.translate(x, y); cr.rotate(u * rnd.uniform(-8, 8))
        L.sketch_poly(cr, [(-30, -16), (26, -22), (34, 14), (-22, 20)], 4, sid=7970 + i, fill=O.HAT_D, amp=0.6)
        cr.restore()
def brim(cr, t, p, ly):
    if ly == "back" and t >= BOOM: O.draw_brim_ring(cr, X2, t, smoke=1 - 0.6 * ramp(t, BOOM + 6, BOOM + 14), w=400)
def boom_cloud(cr, t, p, ly):                                              # behind him, so we see him shoot up through it
    if ly == "back" and t >= BOOM: O.draw_magic_burst(cr, X2, 900, t - BOOM, part="cloud")

# ================================================================ LANDS ON HIS BUTT. the leftovers.
S.set(LAND, "sit_floor", "dead_stare", dur=0.06, ease="snap", stretch=-0.3, soot=0.65, frizz=1.0, lag=1.0)
S.set(LAND + 0.15, "sit_floor", "dead_stare", dur=0.4, ease="back", stretch=0.0, soot=0.65, frizz=1.0, fx_steam=0.4)
S.sfx(LAND, "thud", 0.2); S.sfx(LAND + 0.02, "bonk", 0.04); S.shake(LAND, 0.5, 16)
def land_poof(cr, t, p, ly):
    if ly == "front" and LAND <= t < LAND + 0.8: L.draw_poof(cr, X2, FLOOR_Y - 40, (t - LAND) / 0.8, r=200, sid=32)
S.blink(LAND + 1.0)
S.set(HAT2_0 + 0.3, "sit_floor", "dead_stare", dur=0.5, look=(0.0, -0.9), soot=0.65, frizz=1.0, fx_steam=0.3)   # it's coming down
S.set(HAT2_1 + 0.05, "sit_floor", "dead_stare", dur=0.08, ease="snap", squash=0.15, soot=0.65, frizz=0.5, look=(0.0, -0.9))
S.set(HAT2_1 + 0.25, "sit_floor", "dead_stare", dur=0.4, squash=0.0, soot=0.65, frizz=0.5, look=(0.0, 0.0))
S.set(B5[0] + 0.4, "sit_floor", "dead_stare", dur=0.4, look=(0.0, -0.95), soot=0.65, frizz=0.5)   # up at it
S.set(B5[1] - 0.1, "sit_floor", "dead_stare", dur=0.4, look=(0.0, 0.0), soot=0.65, frizz=0.5)     # at us
S.sfx(HAT2_1, "pop", 0.04)
SW, SH = 190.0, 240.0
def small_hat_on(t, p):
    """(brim x, brim y, rotation) of the little hat while it sits on his head."""
    hx, hy = p["head"]; tl = p.get("tilt", 0.0)
    return (hx + (L.HEAD_R - 22) * math.sin(tl), hy - (L.HEAD_R - 22) * math.cos(tl), tl)
def small_hat(cr, t, p, ly):
    if ly != "front" or t < HAT2_0: return
    if t < HAT2_1:
        u = ramp(t, HAT2_0, HAT2_1, "linear")
        tx, ty, _ = small_hat_on(t, p)
        x = tx + 90 * math.sin(u * 7) * (1 - u); y = lerp(-250, ty, u ** 1.3); rot = 0.35 * math.sin(u * 7) * (1 - u)
    else:
        x, y, rot = small_hat_on(t, p)
    eyes = smooth(ramp(t, B5[0] - 0.5, B5[0] - 0.2))
    mouth = 0.2 + 0.25 * abs(math.sin((t - B5[0]) * 9)) if B5[0] <= t < B5[1] - 0.6 else 0.0
    cr.save(); cr.translate(x, y); cr.rotate(rot)
    O.draw_wizard_hat(cr, 0, 0, SW, SH, t, bend=0.3, droop=0.7, eyes=eyes, look=(-0.3, 0.4), mouth=mouth, scorch=1.0, sid=7990)
    cr.restore()
    for k in range(2):                                                    # a wisp off its tip
        u = ((t * 0.6) + k / 2) % 1.0
        tx, ty = O.hat_pt(x, y, SW, SH, 0.95, 0, 0.3, 0.7)
        cr.arc(tx + 15 * math.sin(u * 6), ty - 140 * u, 10 + 22 * u, 0, 2 * math.pi)
        cr.set_source_rgba(0.55, 0.55, 0.58, 0.4 * math.sin(math.pi * u)); cr.fill()

# ================================================================ stands. the ask, at the gate.
S.camera(LAND - 0.2, X2, 900, 0.95, 1.2)
S.stand(STAND, face="dead_stare")
S.set(STAND + 0.7, "stand", "dead_stare", dur=0.3, soot=0.65, frizz=0.5)
S.t = T_ASK
S.camera(T_ASK - 1.0, *CAM_END, dur=1.0)
S.camera(T_ASK + 6.9, X2, 885, 1.04, 3.0)
S.the_ask(T_ASK, hold=8.0, push=False, keep=dict(soot=0.65, frizz=0.5))
S.hook(lambda tt, p: (p.update(soot=0.65, frizz=max(p.get("frizz", 0.0), 0.5)) if tt >= BOOM else None) or p)

# ---------------------------------------------------------------- draw order + hooks
S.props.insert(0, brim); S.props.insert(1, boom_cloud)
for f in (letter, owl, hat, boom, land_poof, small_hat, bubbles): S.prop(f)

if __name__ == "__main__":
    S.render("day007.mp4")
