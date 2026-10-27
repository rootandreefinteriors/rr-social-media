"""Day 5 — COMMENT episode: @nerdbpy "Eat a billion big Mac's" (Instagram, day 4 reel, 8 likes).

Still in the block-game End (dark purple sky, end-stone floor, half a hardcore heart, his sword lying on the floor).
A generic triple-decker burger (no box, no logo, no name on screen). He does it. All of it. Deadpan.
SHOT 1  Reads the comment. Stares. Slow blink. Tiny nod.
CARD    BURGER 1.  He digs at his hip and pulls out a burger. Looks at it. Looks at us. Eats it in four slow bites,
        chewing, staring at us. Gulp. The counter ticks 0 -> 1. His eyes slide down to the counter. Back to us.
CARD    BURGER 2.  Same stare, mid-chew. One bite. Counter: 2. (That's the whole shot.)
CARD    BURGER 40,000.  Burger towers on both sides, a round belly now. Autopilot: hip -> mouth -> hip -> mouth, the
        counter rolling. He never stops looking at us.
CARD    BURGER 999,999,999.  Sitting in front of a mountain of wrappers, enormous belly. The last burger. Three slow
        bites. 1,000,000,000. Soft ding. A toast slides in: ADVANCEMENT MADE — WHY. Nothing. Then the belly slowly
        deflates with a long hiss, back to a stick. He stands up.
END     The ask, right there, in front of the wrapper mountain.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y
from ink import smooth, draw_text, sketch_rect, WHITE

OX = 80                                           # body offset: leaves room for the counter bottom-left
CAM = (560, 930, 1.15)
CARD_LEN = 1.5
C1 = 5.2;  T1 = C1 + CARD_LEN                     # BURGER 1
C2 = 19.9; T2 = C2 + CARD_LEN                     # BURGER 2
C3 = 24.9; T3 = C3 + CARD_LEN                     # BURGER 40,000
C4 = 34.3; T4 = C4 + CARD_LEN                     # BURGER 999,999,999
CARDS = ((C1, "BURGER 1"), (C2, "BURGER 2"), (C3, "BURGER 40,000"), (C4, "BURGER 999,999,999"))
MOUTH = (540 + OX + 62, 695)                      # where the burger's centre sits when he bites
HIP = (588 + OX, 1092)

L.POSES["eat"] = dict(relb=(660, 900), rhand=(MOUTH[0] - OX + 20, MOUTH[1] + 40), rhand_t="grip")   # body-local
L.POSES["hold_burger"] = dict(relb=(668, 960), rhand=(720, 880), rhand_t="grip")

S = M.Scene(x0=OX)
S.auto_blinks = False
S.camkeys[0] = (0.0, CAM, 0); S.cam = CAM
S.card("nerdbpy", "Eat a billion big Mac’s", "8", t0=0.35)
S.camkeys[0] = (0.0, CAM, 0); S.cam = CAM
S.sfx(0.35, "tick", 0.04)
S.background(O.draw_end_world)

def shot(t):
    for i, (c, _) in enumerate(CARDS):
        if c <= t < c + CARD_LEN: return -1
    if t < C1: return 0
    if t < C2: return 1
    if t < C3: return 2
    if t < C4: return 3
    return 4

# ================================================================ state tracks: burger in hand, bites, belly, count
burger_keys = []          # (t_on, t_off) a burger is in his hand
bite_keys = []            # (t, amount 0..1 eaten after this bite)
def in_hand(t):
    for a, b in burger_keys:
        if a <= t < b: return True
    return False
def bites(t):
    v = 0.0
    for a, b in burger_keys:
        if a <= t < b:
            for tb, amt in bite_keys:
                if a <= tb <= t: v = amt
    return v
belly = Track([(0.0, dict(b=0.0), 0), (C3, dict(b=0.0), 0), (T3, dict(b=0.42), 0.001),
               (T3 + 1.0, dict(b=0.55), C4 - T3 - 1.5), (C4, dict(b=1.0), 0.001)])
count_keys = [(0.0, 0)]
def count(t):
    v = 0
    for tc, n in sorted(count_keys):
        if t >= tc: v = n
    return v

# ================================================================ overlays: HUD (hearts + counter), cards, toast
def hud(cr, t):
    if shot(t) == -1: return
    s, y = 5.6, 1440 - 6 * 5.6
    top = 1196 if T1 <= t < T_ASK else 1352
    cr.rectangle(52, top, 470, 1452 - top); cr.set_source_rgba(0.08, 0.06, 0.11, 0.62); cr.fill()
    draw_text(cr, "HARDCORE", 72, y - 30, 34, color=(240, 240, 240), anchor="left")
    O.draw_hearts_bar(cr, 78, y, 0.5, s=s, gap=6, blink=0.5 + 0.5 * math.sin(t * 7))
    if T1 <= t < T_ASK:
        draw_text(cr, "BURGERS EATEN", 72, 1236, 30, color=(240, 240, 240), anchor="left")
        draw_text(cr, f"{count(t):,}", 72, 1292, 54, color=(255, 214, 92), anchor="left")
def title_cards(cr, t):
    for t0, txt in CARDS:
        if t0 <= t < t0 + CARD_LEN:
            cr.set_source_rgb(0.04, 0.04, 0.05); cr.paint()
            draw_text(cr, txt, 540, 900, 150 if len(txt) < 12 else 104, color=(245, 245, 245))
T_DONE = T4 + 8.6                                  # the billionth bite lands
def toast(cr, t):
    if not (T_DONE + 1.2 <= t < T_DONE + 6.2): return
    u = min(ramp(t, T_DONE + 1.2, T_DONE + 1.6), 1 - ramp(t, T_DONE + 5.7, T_DONE + 6.2))
    x0 = -560 + 652 * smooth(u)                      # slides in from the left
    cr.rectangle(x0, 540, 560, 130); cr.set_source_rgb(0.13, 0.12, 0.15); cr.fill()
    cr.rectangle(x0, 540, 560, 130); cr.set_source_rgb(0.55, 0.55, 0.58); cr.set_line_width(6); cr.stroke()
    O.draw_burger(cr, x0 + 70, 605, 0.42)
    draw_text(cr, "ADVANCEMENT MADE", x0 + 135, 580, 32, color=(255, 214, 92), anchor="left")
    draw_text(cr, "WHY.", x0 + 135, 630, 44, color=(245, 245, 245), anchor="left")
for f in (toast, title_cards, hud): S.overlays.insert(0, f)                # all under the comment card

# ================================================================ world props
SWORD_REST = (OX + 760, FLOOR_Y - 12)
def floor_props(cr, t, p, ly):
    if ly != "back" or shot(t) in (-1,): return
    if shot(t) != 4: O.draw_pixel_sword(cr, *SWORD_REST, 0.95, ang=1.5708)
    if shot(t) == 3:                                                       # burger towers both sides
        for bx, n in ((OX + 170, 6), (OX + 960, 5)):
            for k in range(n):
                O.draw_burger(cr, bx + 6 * math.sin(k * 2.3), FLOOR_Y - 68 - k * 118, 0.8, sid=10 * k)
    if shot(t) == 4: O.draw_wrapper_pile(cr, OX + 520, 1150, 520)
S.prop(floor_props)
def held(cr, t, p, ly):
    if ly != "front": return
    b = belly.at(t)["b"]
    if t >= T_DEFL: b = b * (1 - ramp(t, T_DEFL, T_DEFL + 2.6, "inn"))
    O.draw_belly(cr, p, b, wob_=math.sin(t * 30) * (ramp(t, T_DEFL, T_DEFL + 0.3) - ramp(t, T_DEFL + 2.3, T_DEFL + 2.6)) if t >= T_DEFL else 0.0)
    if in_hand(t):
        hx, hy = p["rhand"]
        O.draw_burger(cr, hx - 20, hy - 40, 0.82, bites(t))
S.prop(held)

# eating helpers ------------------------------------------------------------------------------
chew_spans = []
def chew_hook(tt, p):
    for a, b in chew_spans:
        if a <= tt < b:
            p["mouth"] = "o"; p["open"] = 0.12 + 0.18 * (0.5 + 0.5 * math.sin((tt - a) * 15))
    return p
S.hook(chew_hook)
def bite(t, amt, face="dead_stare", body="eat", **kw):
    """hand pushes the burger into his mouth, CHOMP, then chews for ~0.6 s."""
    def hk(tt, p, t0=t):
        v = pulse(tt, t0, 0.12)
        if v > 0.01: p["rhand"] = (p["rhand"][0] - 26 * v, p["rhand"][1] - 6 * v); p["head"] = (p["head"][0] + 4 * v, p["head"][1])
        return p
    S.hook(hk)
    bite_keys.append((t + 0.06, amt)); chew_spans.append((t + 0.12, t + 0.75))
    S.sfx(t + 0.06, "chomp", 0.05)

def pull_burger(t, face="dead_stare"):
    """dig at the hip (no pocket), the burger comes up in his hand. ~1.6 s."""
    def dig(tt, p, t0=t):
        if t0 <= tt < t0 + 1.2:
            u = ramp(tt, t0, t0 + 0.25)
            d_ = ramp(tt, t0 + 0.25, t0 + 0.35) * (1 - ramp(tt, t0 + 1.0, t0 + 1.1))
            p["rhand"] = lerp(p["rhand"], (HIP[0] + 14 * math.sin(tt * 24) * d_, HIP[1] + 6 * math.sin(tt * 31) * d_), u)
        return p
    S.hook(dig)
    S.set(t, "stand", face, dur=0.3, look=(0.35, 0.9), tilt=0.05)
    S.set(t + 1.15, "hold_burger", face, dur=0.3, ease="back", look=(0.4, -0.1))
    S.sfx(t + 1.2, "pop", 0.05)
    def pop_fx(cr, tt, p, ly, t0=t + 1.2):
        if ly == "front" and t0 <= tt < t0 + 0.3: L.burst_lines(cr, p["rhand"][0] - 20, p["rhand"][1] - 40, (tt - t0) / 0.4, r0=90, r1=150, n=10, sid=9)
    S.prop(pop_fx)
    return t + 1.2

# ================================================================ SHOT 1: reads it. stares. accepts.
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(0.6, react="dead_stare", lines=1, face="deadpan")
S.set(3.2, "stand", "dead_stare", dur=0.25, lid=1.0)
S.set(3.6, "stand", "resigned", dur=0.35)
def nod(tt, p, a=4.1):
    v = 16 * math.sin(math.pi * min(1.0, max(0.0, (tt - a) / 0.7)))
    if v > 0.01: p["head"] = (p["head"][0], p["head"][1] + v)
    return p
S.hook(nod)

# ================================================================ BURGER 1
S.cut(C1, cam=CAM, x=OX)
S.set(C1, "stand", "dead_stare", dur=0.0)
S.blink(T1 + 0.4)
tb = pull_burger(T1 + 0.8)
burger_keys.append((tb, C2))
S.set(tb + 0.5, "hold_burger", "dead_stare", dur=0.5, look=(0.75, 0.15), tilt=0.04)       # looks at it
S.set(tb + 1.6, "hold_burger", "dead_stare", dur=0.3, look=(0.0, 0.0), tilt=0.0)          # looks at us
S.set(tb + 2.4, "eat", "dead_stare", dur=0.45)                                            # up to the mouth
for k, amt in enumerate((0.25, 0.5, 0.75, 1.0)):
    bite(tb + 3.0 + k * 0.85, amt)
TG = tb + 3.0 + 4 * 0.85
S.set(TG - 0.2, "stand", "dead_stare", dur=0.4)
S.sfx(TG + 0.1, "gulp", 0.06)
def gulp(tt, p, a=TG + 0.1):
    v = pulse(tt, a, 0.12)
    if v > 0.01: p["head"] = (p["head"][0], p["head"][1] + 10 * v)
    return p
S.hook(gulp)
count_keys.append((TG + 0.5, 1)); S.sfx(TG + 0.5, "tick", 0.04)
S.set(TG + 1.3, "stand", "dead_stare", dur=0.35, look=(-0.85, 0.9), tilt=-0.04)           # eyes slide down to the counter
S.set(TG + 3.1, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), tilt=0.0)                # back to us
S.set(TG + 3.9, "stand", "dead_stare", dur=0.3, lid=1.0)
S.set(TG + 4.3, "stand", "dead_stare", dur=0.35)

# ================================================================ BURGER 2 (that's the whole shot)
S.cut(C2, cam=(OX + 560, 760, 1.5), x=OX)
S.set(C2, "eat", "dead_stare", dur=0.0)
burger_keys.append((C2, C3)); bite_keys.append((C2, 0.25))
count_keys.append((C2, 1))
chew_spans.append((T2, T2 + 1.3))
bite(T2 + 1.5, 0.5)
chew_spans.append((T2 + 2.25, C3))
count_keys.append((T2 + 2.0, 2)); S.sfx(T2 + 2.0, "tick", 0.04)

# ================================================================ BURGER 40,000: autopilot
S.cut(C3, cam=(OX + 540, 940, 1.02), x=OX)
S.set(C3, "eat", "dead_stare", dur=0.0, lid=0.5)
CYC = 0.9
NC = int((C4 - T3 - 0.3) / CYC)
def autopilot(tt, p):
    if T3 <= tt < T3 + NC * CYC:
        u = ((tt - T3) / CYC) % 1.0
        down = (MOUTH[0] + 40, 1080)
        up = (MOUTH[0] + 20, MOUTH[1] + 40)
        w = smooth(min(1.0, u / 0.4)) if u < 0.5 else 1 - smooth(min(1.0, (u - 0.6) / 0.4))
        p["rhand"] = lerp(down, up, w)
        p["relb"] = (690 + OX, 960)
    return p
S.hook(autopilot)
for k in range(NC):
    a = T3 + k * CYC
    burger_keys.append((a + 0.05, a + CYC * 0.75))
    bite_keys.append((a + 0.05, 0.0)); bite_keys.append((a + 0.45, 0.55)); bite_keys.append((a + 0.6, 1.0))
    chew_spans.append((a + 0.45, a + CYC))
    if k % 2 == 0: S.sfx(a + 0.45, "chomp", 0.03)
for k in range(int((C4 - T3) / 0.1)):
    count_keys.append((T3 + k * 0.1, 40000 + k * 137))
count_keys.insert(1, (C3, 40000))
S.set(T3 + 3.0, "eat", "dead_stare", dur=1.0, lid=0.62, sweat=0.4)
S.set(C4 - 1.5, "eat", "dead_stare", dur=0.8, lid=0.7, sweat=0.6, look=(0.0, 0.1))

# ================================================================ BURGER 999,999,999: the last one
S.cut(C4, cam=(OX + 560, 1010, 1.05), x=OX)
S.set(C4, "sit_floor", "dead_stare", dur=0.0, lid=0.55, sweat=0.5,
      relb=(700, 1150), rhand=(720, 1050), rhand_t="grip", lelb=(330, 1230), lhand=(320, 1330))
count_keys.append((C4, 999999999))
burger_keys.append((T4, T4 + 9.0))
S.blink(T4 + 0.9)
SITM = (MOUTH[0], MOUTH[1] + 345)                  # mouth while sitting (head is 345 lower)
def raise_last(tt, p):
    if T4 + 2.0 <= tt < T4 + 8.9:
        u = ramp(tt, T4 + 2.0, T4 + 2.6)
        p["rhand"] = lerp(p["rhand"], (SITM[0] + 20, SITM[1] + 40), u); p["relb"] = lerp(p["relb"], (720 + OX, 1180), u)
    return p
S.hook(raise_last)
S.set(T4 + 0.9, "sit_floor", "dead_stare", dur=0.5, look=(0.7, 0.2), lid=0.55, sweat=0.5,
      relb=(700, 1150), rhand=(720, 1050), rhand_t="grip", lelb=(330, 1230), lhand=(320, 1330))
S.set(T4 + 2.0, "sit_floor", "dead_stare", dur=0.5, look=(0.0, 0.0), lid=0.55, sweat=0.5,
      relb=(700, 1150), rhand=(720, 1050), rhand_t="grip", lelb=(330, 1230), lhand=(320, 1330))
for k, (tb_, amt) in enumerate(((T4 + 3.4, 0.33), (T4 + 5.4, 0.66), (T4 + 7.8, 1.0))):
    bite(tb_, amt)
S.set(T4 + 6.3, "sit_floor", "holding_it", dur=0.8, lid=0.45, sweat=0.8, twitch=0.6,
      relb=(700, 1150), rhand=(720, 1050), rhand_t="grip", lelb=(330, 1230), lhand=(320, 1330))
S.set(T4 + 8.9, "sit_floor", "dead_stare", dur=0.4, lid=0.5, sweat=0.6,
      relb=(640, 1210), rhand=(700, 1310), lelb=(330, 1230), lhand=(320, 1330))
S.sfx(T_DONE + 0.2, "gulp", 0.06)
count_keys.append((T_DONE + 0.6, 1000000000)); S.sfx(T_DONE + 0.6, "ding", 0.05)
S.sfx(T_DONE + 1.25, "whoosh", 0.03)
S.set(T_DONE + 2.4, "sit_floor", "dead_stare", dur=0.35, look=(-0.8, -0.7), lid=0.5, sweat=0.4,
      relb=(640, 1210), rhand=(700, 1310), lelb=(330, 1230), lhand=(320, 1330))  # eyes to the toast
S.set(T_DONE + 4.0, "sit_floor", "dead_stare", dur=0.3, look=(0.0, 0.0), lid=0.5, sweat=0.4,
      relb=(640, 1210), rhand=(700, 1310), lelb=(330, 1230), lhand=(320, 1330))
T_DEFL = T_DONE + 6.6                              # the belly lets go, slowly
S.sfx(T_DEFL, "wind", 0.06, dur=2.6)
S.set(T_DEFL + 0.3, "sit_floor", "dead_stare", dur=2.0, lid=0.42, sweat=0.0,
      relb=(610, 1240), rhand=(610, 1318), lelb=(470, 1240), lhand=(470, 1318))
S.set(T_DEFL + 3.2, "sit_floor", "dead_stare", dur=0.3, lid=1.0)
S.set(T_DEFL + 3.6, "sit_floor", "dead_stare", dur=0.3)
S.stand(T_DEFL + 4.3, face="dead_stare")
S.camera(T_DEFL + 4.3, OX + 560, 940, 1.12, 0.8)
S.t = T_DEFL + 5.3

# ================================================================ the ask, right here, in front of the wrappers
T_ASK = S.t
S.blink(S.t - 0.2)
S.the_ask(S.t, hold=8.0)

if __name__ == "__main__":
    S.render("day005.mp4")
