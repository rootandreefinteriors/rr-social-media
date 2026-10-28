"""Day 6 — COMMENT episode: @nerdbpy "Rock a baby to sleep. (My mom said this)" (Instagram, day 5 reel, 4 likes).
Format reference: episodes/ep005. He lives outside the burger place now (STATE world.location).

SHOT 1  Outside the burger place, in the wrappers. Reads the comment. Stares. Slow blink. Tiny nod. Shuffles right.
TRUCK   The yellow dump truck again (1 BABY). Backs in, beeping, tips its bed: a GIANT wooden cradle slides out the back
        and lands with a thud, rocking. A giant baby in it, asleep, snot bubble. The truck leaves. Silence.
WAKE    The bubble pops. The baby opens its eyes. Looks at him. Its face crumples: WAAAH. Tear jets, a gale that
        blows the wrappers away and his hair into a frizz. BABY: 118 dB.
ROCK    He puts a hand on the rim and rocks it. Gently. Nothing. Faster and bigger, the cradle swinging him back and
        forth with it, sweat building, dB climbing to 9,998... then mid-swing the baby is OUT. Dead silence. He stops
        the cradle dead. Exhausted hold.
SNORE   The snot bubble grows... and grows... SNORE: a blast that takes him clean off screen. Empty frame. The baby
        sleeps. He falls back in from the sky onto his butt in the wrappers. Stands. Deadpan. The ask, next to the
        sleeping giant baby (it stays).
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y
from ink import smooth, draw_text

SX = 2000                       # where day 5 left him (body centre 2540, in the wrappers)
SX2 = 2100                      # by the cradle's head end
SX_LAND = 2050
X0 = 540 + SX
CX = 3170                       # cradle centre (rockers touch the floor here)
RIM0 = O.cradle_pt(CX, FLOOR_Y, 0.0, *O.CRADLE_RIM)
CAM0 = (2600, 930, 1.15)
CAM_WIDE = (3350, 700, 0.6)
CAM_MAIN = (3093, 790, 0.68)
CAM_LAND = (2790, 930, 0.95)

# ---------------------------------------------------------------- timeline
T_SHUF = 4.4
TT0, TT1 = 5.4, 7.8             # truck backs in / bed tips
CS0, CS1 = 8.5, 9.3             # cradle slides out / lands
T_WAKE, T_CRY = 13.4, 14.5
R0, R1 = 17.6, 33.6             # rocking / OUT
T_INH = R1 + 4.4                # the big inhale
T_SN = T_INH + 1.4              # SNORE
T_F0 = T_SN + 2.5               # falls back in
T_LAND = T_F0 + 0.55

S = M.Scene(x0=SX)
S.auto_blinks = False
S.card("nerdbpy", "Rock a baby to sleep. (My mom said this)", "4", t0=0.35)
S.camkeys[0] = (0.0, CAM0, 0); S.cam = CAM0
S.sfx(0.35, "tick", 0.04)
S.background(lambda cr, t: O.draw_burger_world(cr, t))

# ================================================================ the rock: amplitude + frequency build, then OUT
DT = 1 / 120.0
_PH = [0.0]
for k in range(int(70 / DT)):
    t_ = k * DT
    f = lerp(0.5, 1.55, smooth(ramp(t_, R0 + 3.0, R1 - 0.8)) ** 1.2)
    _PH.append(_PH[-1] + 2 * math.pi * f * DT)
def phase(t): return _PH[min(len(_PH) - 1, max(0, int((t - R0) / DT)))] if t >= R0 else 0.0
def amp(t):
    if t < R0: return 0.0
    a = 0.04 * ramp(t, R0, R0 + 0.6) + 0.16 * smooth(ramp(t, R0 + 2.5, R1)) ** 1.4
    return a * (1 - smooth(ramp(t, R1 + 0.15, R1 + 0.75)))
def land_rock(t):               # it rocks a little after it lands, settles
    if t < CS1: return 0.0
    u = t - CS1
    return 0.12 * math.exp(-u * 1.6) * math.sin(u * 5.5)
def ang(t): return amp(t) * math.sin(phase(t)) + land_rock(t)

def cradle_pos(t):
    """(cx, yb, ang, scale) — slides out of the truck bed, lands, rocks."""
    if t < CS0: return None
    if t < CS1:
        u = (t - CS0) / (CS1 - CS0)
        mx, my = RX_END - 160, FLOOR_Y - 340
        x = lerp(mx, CX, u); y = lerp(my, FLOOR_Y, u * u) - 260 * math.sin(math.pi * u) * (1 - u)
        return (x, y, lerp(-0.6, 0.0, smooth(u)), lerp(0.45, 1.0, smooth(u)))
    sq = 1 - 0.08 * pulse(t, CS1 + 0.05, 0.12)
    return (CX, FLOOR_Y, ang(t), sq)

# baby face over time
def bubble_r(t):
    if t < CS1: return 0.0
    if t < T_WAKE: return 16 + 8 * math.sin(t * 2.3)
    if t < R1 + 0.3: return 0.0
    if t < T_INH: return 14 * ramp(t, R1 + 0.3, R1 + 1.0) + 7 * math.sin(t * 2.1)
    if t < T_SN: return 20 + 110 * smooth(ramp(t, T_INH, T_SN - 0.1)) ** 1.5 + 3 * math.sin(t * 30) * ramp(t, T_SN - 0.5, T_SN)
    if t < T_SN + 1.0: return 0.0
    return 12 * ramp(t, T_SN + 1.0, T_SN + 1.8) + 6 * math.sin(t * 2.1)
def cry_k(t): return smooth(ramp(t, T_CRY, T_CRY + 0.25)) * (1 if t < R1 else 0)
def baby_st(t):
    st = dict(bubble=bubble_r(t))
    if T_WAKE <= t < R1:
        if t < T_CRY:
            st.update(eyes="open", open=ramp(t, T_WAKE + 0.05, T_WAKE + 0.4) * (1 - pulse(t, T_WAKE + 0.85, 0.1)),
                      look=(-1.0 * ramp(t, T_WAKE + 0.4, T_WAKE + 0.6), 0.25))
            if t > T_CRY - 0.25: st.update(eyes="cry")
        else:
            st.update(eyes="cry", cry=cry_k(t) * (0.85 + 0.15 * math.sin(t * 9)))
    return st
def cradle(cr, t, p, ly):
    if ly != "back": return
    c = cradle_pos(t)
    if c: O.draw_cradle(cr, c[0], c[1], c[2], baby_st(t), t, s=c[3])
S.sfx(CS1, "thud", 0.14); S.shake(CS1, 0.4, 10)
S.sfx(T_WAKE, "pop", 0.04)

# tears: two jets from the eyes, running off screen (taper in and out, never break up)
def tears_k(t): return smooth(ramp(t, T_CRY + 0.15, T_CRY + 0.6)) * (1 - smooth(ramp(t, R1, R1 + 0.25)))
def tears(cr, t, p, ly):
    if ly != "front" or not (T_CRY <= t < R1 + 0.3): return
    k = tears_k(t)
    if k < 0.02: return
    a = ang(t)
    for i, (ex, ey) in enumerate(O.BABY_EYES):
        sd = -1 if i == 0 else 1
        src = O.cradle_pt(CX, FLOOR_Y, a, ex + 30 * sd, ey)
        v = (sd * (700 + 260 * k) + 300 * math.sin(t * 3 + i), -(760 + 120 * math.sin(t * 4.1 + i)))
        cr.save(); cr.rectangle(-9000, -9000, 20000, 9000 + FLOOR_Y + 4); cr.clip()
        O.draw_tear_jet(cr, src, v, t, life=1.5, w0=22 * k + 2, w1=70 * k + 4)
        cr.restore()
def waaah(cr, t, p, ly):
    if ly != "front" or not (T_CRY <= t < R1): return
    k = cry_k(t); a = ang(t)
    hx, hy = O.cradle_pt(CX, FLOOR_Y, a, O.BABY_HEAD[0], O.BABY_HEAD[1] - 270)
    sz = 110 + 30 * smooth(ramp(t, R0 + 4, R1))
    draw_text(cr, "WAAAH", hx + 250 + 5 * math.sin(t * 47), hy + 4 * math.cos(t * 53), sz, color=(30, 30, 34),
              rot=0.05 * math.sin(t * 13), alpha=k)
# the gale off the crying: wind streaks blowing left across him
def gale(cr, t, p, ly):
    if ly != "front": return
    k = cry_k(t) * (0.6 + 0.4 * smooth(ramp(t, R0, R1)))
    s2 = ramp(t, T_SN, T_SN + 0.05) * (1 - ramp(t, T_SN + 0.6, T_SN + 1.0))       # the snore: bigger, faster
    for k_, spd, y0, n in ((k, 1500, 700, 7), (s2, 4200, 520, 14)):
        if k_ < 0.02: continue
        for j in range(n):
            x = 2950 - ((t * spd + j * 397) % 1500)
            y = y0 + j * (95 if n < 10 else 65) + 10 * math.sin(t * 7 + j)
            L.sketch_line(cr, [(x, y), (x + 160 + 40 * (j % 3), y)], 5, sid=8000 + j, alpha=0.8 * k_)

# ================================================================ wrappers: the low front pile gets blown away
_rw = random.Random(5)
FLY = [(X0 + _rw.uniform(-380, 420), FLOOR_Y - _rw.uniform(10, 80), _rw.uniform(0, 1.1), _rw.uniform(-300, 100)) for _ in range(18)]
def wrappers_back(cr, t, p, ly):
    if ly == "back": O.draw_wrapper_pile(cr, X0, 1350, 260)
def wrappers_front(cr, t, p, ly):
    if ly != "front": return
    h = 95 * (1 - smooth(ramp(t, T_CRY + 0.3, T_CRY + 1.6)))
    O.draw_wrapper_pile(cr, X0 + 40, 900, h)
    for i, (x0, y0, d, vy) in enumerate(FLY):
        u = t - (T_CRY + 0.3 + d)
        if 0 <= u < 1.4:
            O.draw_wrapper(cr, x0 - 1300 * u - 500 * u * u, y0 + vy * u - 400 * math.sin(min(1.0, u) * math.pi) * 0.5, 1.1, sid=7300 + i)

# ================================================================ TRUCK: the callback. 1 BABY.
RX_END = CX + 630
TRK = Track([(0.0, dict(rx=4800.0, tilt=0.0), 0), (TT0, dict(rx=4800.0, tilt=0.0), 0),
             (TT0, dict(rx=float(RX_END), tilt=0.0), TT1 - 0.4 - TT0, "out"),
             (TT1, dict(rx=float(RX_END), tilt=0.85), 0.8),
             (CS1 + 0.4, dict(rx=float(RX_END), tilt=0.0), 0.8),
             (CS1 + 1.4, dict(rx=5200.0, tilt=0.0), 1.6, "inn")])
def truck(cr, t, p, ly):
    if ly != "back" or not (TT0 <= t < CS1 + 3.2): return
    st = TRK.at(t)
    O.draw_dump_truck(cr, st["rx"], FLOOR_Y, st["tilt"], t, 0.0, label="1 BABY")
for k in range(4): S.sfx(TT0 + 0.3 + k * 0.6, "boop", 0.04)
S.sfx(TT1, "whine", 0.012, dur=0.9); S.sfx(CS0, "whoosh", 0.03); S.sfx(CS1 + 1.4, "whoosh", 0.035)

# ================================================================ HUD: the baby meter
def db(t):
    base = 118 + 3 * math.sin(t * 11)
    if t < R0 + 3: return base
    return base + 9880 * smooth(ramp(t, R0 + 3, R1 - 0.1)) ** 3.2
def hud(cr, t):
    a = ramp(t, CS1 + 0.6, CS1 + 1.0) * (1 - ramp(t, T_LAND + 2.5, T_LAND + 2.8))
    if a < 0.01: return
    cr.rectangle(60, 212, 286, 140); cr.set_source_rgba(0.08, 0.06, 0.11, 0.62 * a); cr.fill()
    draw_text(cr, "BABY", 78, 248, 30, color=(240, 240, 240), anchor="left", alpha=a)
    if T_CRY + 0.1 <= t < R1: txt, col = f"{int(db(t)):,} dB", (255, 120, 100)
    elif T_SN <= t < T_SN + 1.4: txt, col = "SNORING", (255, 214, 92)
    else: txt, col = "ASLEEP", (170, 220, 255)
    draw_text(cr, txt, 78, 306, 52 if len(txt) < 8 else 46, color=col, anchor="left", alpha=a)
S.overlays.insert(0, hud)

# ================================================================ SHOT 1: reads it. stares. accepts. shuffles over.
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(0.6, react="dead_stare", lines=2, face="deadpan")
S.set(3.0, "stand", "dead_stare", dur=0.25, lid=1.0)
S.set(3.4, "stand", "resigned", dur=0.35)
def nod(tt, p, a=3.8):
    v = 14 * math.sin(math.pi * min(1.0, max(0.0, (tt - a) / 0.7)))
    if v > 0.01: p["head"] = (p["head"][0], p["head"][1] + v)
    return p
S.hook(nod)
S.set(T_SHUF - 0.2, "stand", "dead_stare", dur=0.3, look=(0.6, 0.0))
S.xkeys.append((T_SHUF, SX2, 0.9, "smooth")); S.x = SX2
S.set(T_SHUF + 1.0, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0))

# ================================================================ TRUCK arrives; he watches; the cradle lands
S.camera(TT0 - 0.4, *CAM_WIDE, dur=1.4)
S.set(TT0 + 0.5, "stand", "dead_stare", dur=0.4, look=(0.9, 0.0))
S.set(TT1 + 0.3, "stand", "dead_stare", dur=0.4, look=(0.9, -0.5), tilt=-0.04)
S.set(CS0 + 0.3, "stand", "dead_stare", dur=0.3, look=(0.8, 0.2), tilt=0.0)
S.set(CS1 + 0.35, "stand", "dead_stare", dur=0.12, ease="snap", eyescale=1.08)            # the thud
S.set(CS1 + 0.6, "stand", "dead_stare", dur=0.4, look=(0.8, 0.2))
S.camera(CS1 + 1.6, *CAM_MAIN, dur=1.4)
S.set(12.0, "stand", "dead_stare", dur=0.5, look=(0.7, 0.35))
S.set(12.8, "stand", "dead_stare", dur=0.35, look=(0.0, 0.0))                          # at us
S.blink(13.1)
S.set(T_WAKE + 0.4, "stand", "dead_stare", dur=0.25, look=(0.8, 0.3))                    # it's looking at him
S.set(T_CRY + 0.3, "stand", "dead_stare", dur=0.35, lid=0.62, frizz=0.9, lean=-0.05, look=(0.6, 0.2))   # the gale hits
S.sfx(T_CRY, "wind", 0.06, dur=R1 - T_CRY + 0.4)
S.set(T_CRY + 1.6, "stand", "dead_stare", dur=0.6, lid=0.62, frizz=1.0, lean=-0.04, look=(0.0, 0.0))  # at us. in the gale.
S.set(T_CRY + 2.4, "stand", "dead_stare", dur=0.3, lid=1.0, frizz=1.0, lean=-0.04)         # slow blink
S.set(T_CRY + 2.8, "stand", "dead_stare", dur=0.35, lid=0.62, frizz=1.0, lean=-0.04, look=(0.6, 0.2))

# ================================================================ ROCK: hands on the rim; the cradle drags him with it
def engage(t): return smooth(ramp(t, R0 - 0.7, R0)) * (1 - smooth(ramp(t, R1 + 2.2, R1 + 3.0)))
def rocking(tt, p):
    e = engage(tt)
    if e < 0.001: return p
    a = ang(tt)
    rim = O.cradle_pt(CX, FLOOR_Y, a, *O.CRADLE_RIM)
    full = (rim[0] - RIM0[0]) * min(1.0, e * 1.2)
    dx = full if full < 0 else 0.6 * full                  # pulled along when it swings to him; leans in when it swings away
    for j in L.JOINTS: p[j] = (p[j][0] + dx, p[j][1])
    ln = (full - dx) / 450.0
    if ln > 1e-4:
        fx_ = (p["lfoot"][0] + p["rfoot"][0]) / 2; c, s_ = math.cos(ln), math.sin(ln)
        for j in L.JOINTS:
            if j in ("lfoot", "rfoot"): continue
            ddx, ddy = p[j][0] - fx_, p[j][1] - FLOOR_Y
            p[j] = (fx_ + ddx * c - ddy * s_, FLOOR_Y + ddx * s_ + ddy * c)
    p["rhand"] = lerp(p["rhand"], (rim[0] - 8, rim[1] + 18), e); p["rhand_t"] = "open"
    p["lhand"] = lerp(p["lhand"], (rim[0] - 22, rim[1] + 90), e); p["lhand_t"] = "open"
    return p
def sq(t):                       # creak at each end of a swing (thinned out when it's fast)
    out, last = [], -9
    for k in range(1, 200):
        ph = math.pi / 2 + (k - 1) * math.pi
        for i in range(len(_PH) - 1):
            if _PH[i] <= ph < _PH[i + 1]:
                tt = R0 + i * DT
                if tt < R1 and tt - last > 0.5: out.append(tt); last = tt
                break
        else: break
    return out
for tt in sq(0): S.sfx(tt, "squeak", 0.025)
S.set(R0 - 0.7, "stand", "dead_stare", dur=0.6, lid=0.6, frizz=1.0, lean=0.05, look=(0.6, 0.3))
S.set(R0 + 2.0, "stand", "deadpan", dur=0.8, lid=0.6, frizz=1.0, lean=0.07, look=(0.0, 0.0))              # at us
S.set(R0 + 5.0, "stand", "resigned", dur=1.5, lid=0.6, frizz=1.0, lean=0.09, sweat=0.3, look=(0.6, 0.3))
S.set(R0 + 8.5, "stand", "holding_it", dur=2.0, lid=0.5, frizz=1.0, lean=0.12, sweat=0.6, quiver=0.5, breath=1.6, breath_rate=1.8)
S.set(R0 + 12.0, "stand", "holding_it", dur=2.0, lid=0.4, frizz=1.0, lean=0.14, sweat=1.0, quiver=1.0, twitch=0.8, breath=2.2, breath_rate=2.6, look=(0.0, 0.0))
# OUT. silence. stops it dead. exhausted.
S.set(R1 + 0.35, "stand", "dead_stare", dur=0.15, ease="snap", eyescale=1.12, lid=0.2, frizz=1.0, lean=0.12, sweat=1.0, look=(0.6, 0.3))
S.set(R1 + 1.3, "stand", "resigned", dur=0.8, lid=0.62, frizz=1.0, lean=0.04, sweat=1.0, breath=2.4, breath_rate=2.6, look=(0.0, 0.0))
S.blink(R1 + 2.6)
S.set(R1 + 3.2, "stand", "resigned", dur=0.8, lid=0.62, frizz=1.0, sweat=0.7, breath=1.6, breath_rate=1.6)

# ================================================================ SNORE
S.set(T_INH + 0.3, "stand", "dead_stare", dur=0.6, lid=0.3, frizz=1.0, sweat=0.5, look=(0.75, 0.3), lean=0.06)   # watches it grow
S.set(T_SN - 0.4, "stand", "dead_stare", dur=0.3, lid=0.3, frizz=1.0, sweat=0.5, look=(0.0, 0.0), lean=0.08)     # at us
S.sfx(T_INH, "snore", 0.05, dur=1.3)
S.sfx(T_SN, "pop", 0.06); S.sfx(T_SN + 0.02, "kaboom", 0.3, dur=1.4); S.sfx(T_SN + 0.12, "whoosh", 0.06)
S.shake(T_SN, 0.7, 16)
S.set(T_SN + 0.05, "cheer", "dead_stare", dur=0.12, ease="snap", eyescale=1.25, lid=0.0, frizz=1.0, nowalk=1.0, lag=0.5,
      rhand_t="open", lhand_t="open")
BL = 0.75
def blast(tt, p):
    if not (T_SN + 0.05 <= tt < T_F0): return p
    u = tt - T_SN - 0.05
    if u >= BL: p["show"] = 0.0; return p
    h = p["hip"]; th = -9.0 * u * u - 2.0 * u
    q = (h[0] - 900 * u - 2600 * u * u, h[1] - 520 * u + 260 * u * u)
    c, s_ = math.cos(th), math.sin(th)
    for j in L.JOINTS:
        dx, dy = p[j][0] - h[0], p[j][1] - h[1]
        p[j] = (q[0] + dx * c - dy * s_, q[1] + dx * s_ + dy * c)
    p["tilt"] = p.get("tilt", 0.0) + th
    return p
S.cut(T_SN + 1.2, x=SX_LAND)
S.camera(T_SN + 1.0, *CAM_LAND, dur=1.2)
S.sfx(T_SN + 1.6, "snore", 0.025, dur=1.2)
def zzz(cr, t, p, ly):
    if ly != "front" or t < T_SN + 1.4: return
    for k in range(3):
        u = ((t - T_SN - 1.4) * 0.45 + k / 3) % 1.0
        hx, hy = O.cradle_pt(CX, FLOOR_Y, ang(t), -120, -640)
        draw_text(cr, "z", hx + 60 * u + 15 * math.sin(u * 6), hy - 220 * u, 50 + 40 * u, color=(30, 30, 34),
                  alpha=math.sin(math.pi * u) * ramp(t, T_SN + 1.4, T_SN + 2.0))

# ================================================================ FALLS BACK IN. on his butt. stands. the ask.
S.set(T_F0 - 0.3, "sit_floor", "dead_stare", dur=0.05, frizz=1.0, nowalk=1.0, lag=0.6, eyescale=1.1)
def fall(tt, p):
    if not (T_F0 - 0.3 <= tt < T_LAND): return p
    u = max(0.0, (tt - T_F0) / (T_LAND - T_F0))
    dy = -1700 * (1 - u * u)
    for j in L.JOINTS: p[j] = (p[j][0], p[j][1] + dy)
    return p
S.sfx(T_F0, "whoosh", 0.03)
S.set(T_LAND, "sit_floor", "dead_stare", dur=0.06, ease="snap", stretch=-0.3, frizz=1.0, lag=1.0)
S.set(T_LAND + 0.15, "sit_floor", "dead_stare", dur=0.4, ease="back", stretch=0.0, frizz=1.0)
S.sfx(T_LAND, "thud", 0.2); S.sfx(T_LAND + 0.02, "bonk", 0.04); S.shake(T_LAND, 0.5, 16)
def land_poof(cr, t, p, ly):
    if ly == "front" and T_LAND <= t < T_LAND + 0.8: L.draw_poof(cr, 540 + SX_LAND, FLOOR_Y - 40, (t - T_LAND) / 0.8, r=200, sid=32)
S.blink(T_LAND + 1.0)
S.set(T_LAND + 1.4, "sit_floor", "dead_stare", dur=0.4, frizz=1.0, look=(0.8, 0.1))        # at the baby
S.set(T_LAND + 2.2, "sit_floor", "dead_stare", dur=0.3, frizz=1.0, look=(0.0, 0.0))        # at us
S.set(T_LAND + 2.8, "crouch", "dead_stare", dur=0.3, frizz=1.0)
S.set(T_LAND + 3.15, "stand", "dead_stare", dur=0.3, ease="back", frizz=1.0)
S.x = SX_LAND
S.t = T_LAND + 3.8
T_ASK = S.t
S.camera(T_ASK + 6.9, 2770, 930, 1.0, 3.0)
S.camera(T_ASK + 11.0, 2760, 935, 1.05, 2.5)
S.the_ask(T_ASK, hold=8.0, push=False, keep=dict(frizz=1.0))

# ---------------------------------------------------------------- draw order + hooks
S.props.insert(0, wrappers_back)
for f in (truck, cradle): S.prop(f)
for f in (wrappers_front, tears, waaah, gale, zzz, land_poof): S.prop(f)
for h in (rocking, blast, fall): S.hook(h)

if __name__ == "__main__":
    S.render("day006.mp4")
