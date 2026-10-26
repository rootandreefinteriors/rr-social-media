"""Day 4 — COMMENT episode: @neoblade75 "Beat Mc in hardcore mode:)" (Instagram, day 3 reel).

A generic blocky survival game (no logos, names or real characters), played dead straight, in the style of the
"100 days in hardcore" videos (full-screen DAY cards between scenes). He WINS.
SHOT 1  Reads the comment. Stares. Slow blink. Tiny nod.
CARD    DAY 1.  Block world, ten big hardcore hearts. He punches a log out of a tree. The top of the tree stays
        floating. He looks up at it for a long time. Looks back at us. The little log flies into him.
CARD    NIGHT 1.  A one-block-wide dirt pillar; only his eyes, through a one-block window. Two knocks from outside.
        His eyes slide over. Slide back. Slow blink.
CARD    DAY 41.  Three hearts left. A stone-brick room with the floor portal (a starry black pit in a ring of frame
        blocks). He looks down into it. Looks at us. Steps off the edge and drops through. Empty pit.
CARD    THE END.  A huge black blocky dragon flies in, lands, roars -- and swipes: HALF A HEART (the hearts swell up,
        the last half blinks; he slowly looks down at them). He pulls a pixel sword from his hip, walks up and hits it
        over and over in a blur; the boss bar drops in chunks. A pause. One last tap. The bar empties. The dragon
        dissolves into beams of light. He doesn't move.
SHOT    The victory text scrolls (YOU WON. ON HARDCORE. WITH HALF A HEART. ...). Dead stare.
END     The white void; the half heart is still in the corner, blinking. The ask, deadpan.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y
from ink import smooth, draw_text

BS = 110
SKY_DAY, SKY_NIGHT, SKY_END, SKY_GREY = (0.80, 0.89, 0.98), (0.10, 0.12, 0.25), (0.24, 0.19, 0.30), (0.30, 0.30, 0.33)
CARD_LEN = 1.5
C1 = 5.2;  T1 = C1 + CARD_LEN          # DAY 1
C2 = 16.7; T2 = C2 + CARD_LEN          # NIGHT 1
C3 = 25.2; T3 = C3 + CARD_LEN          # DAY 41
C4 = 33.2; T4 = C4 + CARD_LEN          # THE END
T_HIT = T4 + 5.9
T_PULL = T_HIT + 3.2
T_F0, T_F1 = T_PULL + 2.7, T_PULL + 5.7          # the flurry
T_LAST = T_F1 + 0.9                               # one last tap
T_DIE = T_LAST + 0.6
T5 = T_DIE + 3.2                                  # victory text
T6 = T5 + 6.5                                     # back to the void: the ask
TREE_X = 840
PIT0, PIT1 = 600, 930                             # floor portal (world x)
CARDS = ((C1, "DAY 1"), (C2, "NIGHT 1"), (C3, "DAY 41"), (C4, "THE END"))

L.POSES["punch"] = dict(relb=(660, 930), rhand=(690, 1010), rhand_t="fist", lhand_t="fist")
L.POSES["sword_up"] = dict(relb=(650, 960), rhand=(700, 900), rhand_t="grip")

S = M.Scene()
S.auto_blinks = False
S.card("neoblade75", "Beat Mc in hardcore mode:)", "0", t0=0.35)
S.sfx(0.35, "tick", 0.04)

def shot(t):
    if t < C1: return 0
    if t < T1: return -1
    if t < C2: return 1
    if t < T2: return -1
    if t < C3: return 2
    if t < T3: return -1
    if t < C4: return 3
    if t < T4: return -1
    if t < T5: return 4
    if t < T6: return 5
    return 6

# ================================================================ world backgrounds
def sky(cr, col):
    cr.rectangle(-3000, -3000, 8000, 8000); cr.set_source_rgb(*col); cr.fill()
def bg(cr, t):
    k = shot(t)
    if k == 1:
        sky(cr, SKY_DAY); O.draw_square_sun(cr, 230, 330)
        O.draw_block_cloud(cr, 120 + 6 * t, 520); O.draw_block_cloud(cr, -260 + 6 * t, 430, 200, 40)
        O.draw_ground(cr)
    elif k == 2:
        sky(cr, SKY_NIGHT); O.draw_square_sun(cr, 230, 360, 110, moon=True)
        for i in range(14): cr.rectangle(-100 + (i * 173) % 1300, 150 + (i * 97) % 700, 7, 7)
        cr.set_source_rgb(0.9, 0.9, 1.0); cr.fill()
        O.draw_ground(cr)
    elif k == 3:                                                    # stone-brick room around the floor portal
        sky(cr, (0.36, 0.36, 0.38))
        cr.set_source_rgb(0.27, 0.27, 0.29)
        for r in range(14):
            yy = FLOOR_Y - (r + 1) * BS / 2
            cr.rectangle(-700, yy, 2600, 5); cr.fill()
            for c in range(-6, 20): cr.rectangle(c * BS + (BS / 2 if r % 2 else 0), yy, 5, BS / 2); cr.fill()
        x = -660
        while x < 1800:
            if not (PIT0 <= x < PIT1):
                kind = "endframe" if (PIT0 - BS <= x < PIT0 or PIT1 <= x < PIT1 + BS) else "stonebrick"
                for r in range(3): O.draw_block(cr, x, FLOOR_Y + r * BS, BS, kind if r == 0 else "stonebrick", sid=1200 + int(x) + r)
            x += BS
    elif k == 4:
        sky(cr, SKY_END)
        for i in range(22): cr.rectangle(-500 + (i * 211) % 2200, -200 + (i * 131) % 1300, 8, 8)
        cr.set_source_rgba(0.95, 0.9, 1.0, 0.8); cr.fill()
        O.draw_ground(cr, "endstone", "endstone")
    elif k == 5:
        sky(cr, SKY_GREY)
S.background(bg)

# ================================================================ overlays: hearts HUD, DAY cards, boss bar, victory text
def health(t):
    if t < T3: return 10.0
    if t < T_HIT: return 3.0
    return 0.5
def hud(cr, t):
    if t < T1: return
    dark = shot(t) in (2, 3, 4, 5)
    blink = 0.5 + 0.5 * math.sin(t * 7) if t >= T_HIT else 0.0
    big = ramp(t, T_HIT + 0.5, T_HIT + 0.9) * (1 - ramp(t, T_HIT + 2.9, T_HIT + 3.3))   # the hearts swell after the hit
    s = 5.6 + 4.0 * big
    y = 1440 - 6 * s
    draw_text(cr, "HARDCORE", 72, y - 30, 34, color=(240, 240, 240) if dark else (18, 18, 22), anchor="left")
    O.draw_hearts_bar(cr, 78, y, health(t), s=s, gap=6 + 3 * big, blink=blink)
def title_cards(cr, t):
    for t0, txt in CARDS:
        if t0 <= t < t0 + CARD_LEN:
            cr.set_source_rgb(0.04, 0.04, 0.05); cr.paint()
            draw_text(cr, txt, 540, 900, 150, color=(245, 245, 245))
def boss_hp(t):
    if t < T_F0: return 1.0
    if t < T_F1: return 1.0 - 0.88 * min(8, int((t - T_F0) / 0.375) + 1) / 8
    return 0.12 if t < T_LAST else 0.0
def bossbar(cr, t):
    if not (T4 + 1.0 <= t < T_DIE + 1.6): return
    a = min(1.0, (t - T4 - 1.0) / 0.4) * (1 - ramp(t, T_DIE + 1.0, T_DIE + 1.6))
    draw_text(cr, "DRAGON", 540, 455, 34, color=(240, 240, 240), alpha=a)
    cr.rectangle(220, 485, 640, 20); cr.set_source_rgba(0.25, 0.08, 0.3, a); cr.fill()
    cr.rectangle(220, 485, 640 * boss_hp(t), 20); cr.set_source_rgba(0.88, 0.38, 0.92, a); cr.fill()
    cr.rectangle(220, 485, 640, 20); cr.set_source_rgba(1, 1, 1, a); cr.set_line_width(3); cr.stroke()
SCROLL = ["YOU WON.", "ON HARDCORE.", "WITH HALF A HEART.", "IT TOOK 41 DAYS.", "NOBODY SAW IT.", "THIS TEXT WILL NOW",
          "SCROLL FOR", "TWENTY MINUTES."]
def scroll(cr, t):
    if not (T5 <= t < T6): return
    cr.save(); cr.rectangle(0, 470, 1080, 830); cr.clip()
    for i, line in enumerate(SCROLL):
        y = 1200 + i * 92 - (t - T5) * 128
        if 440 < y < 1360:
            a = min(1.0, (y - 470) / 80, (1300 - y) / 80)
            if a > 0: draw_text(cr, line, 620, y, 56, color=(240, 240, 240), alpha=a)
    cr.restore()
for f in (scroll, bossbar, title_cards, hud): S.overlays.insert(0, f)     # all under the comment card

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

# ================================================================ DAY 1: punch a tree.
S.cut(C1, cam=(560, 930, 1.15), x=-120)
S.set(C1, "stand", "dead_stare", dur=0.0)
S.blink(T1 + 0.5)
S.walk_to(T1 + 0.7, 140, 1.4)
TP0, TP1 = T1 + 2.6, T1 + 5.2
S.set(TP0 - 0.2, "punch", "dead_stare", dur=0.25, look=(0.75, 0.25))
def punching(tt, p):
    if TP0 <= tt < TP1:
        v = max(0.0, math.sin(2 * math.pi * (tt - TP0) * 3.2)) ** 0.7
        p["rhand"] = lerp(p["rhand"], (788, 1090), v); p["relb"] = lerp(p["relb"], (740, 990), v)
    return p
S.hook(punching)
k = 0
while TP0 + (k + 0.25) / 3.2 < TP1:
    S.sfx(TP0 + (k + 0.25) / 3.2, "tap", 0.028); k += 1
TB = TP1
S.set(TB, "stand", "dead_stare", dur=0.35, look=(0.6, 0.7))
S.sfx(TB, "pop", 0.05)
def tree(cr, tt, p, ly):
    if ly != "back" or shot(tt) != 1: return
    for j in range(4):
        if j == 3 and tt >= TB: continue
        O.draw_block(cr, TREE_X - BS / 2, FLOOR_Y - BS * (j + 1), BS, "log", sid=700 + j,
                     crack=ramp(tt, TP0, TP1, "linear") if j == 3 else 0.0)
    for (i, j) in [(-1, 4), (0, 4), (1, 4), (-1, 5), (0, 5), (1, 5), (0, 6)]:
        O.draw_block(cr, TREE_X - BS / 2 + i * BS, FLOOR_Y - BS * (j + 1), BS, "leaves", sid=720 + i * 5 + j)
S.prop(tree)
T_GET = TB + 4.0
def item(cr, tt, p, ly):
    if ly != "front" or not (TB <= tt < T_GET + 0.3): return
    y0, y1 = FLOOR_Y - BS * 3.5, FLOOR_Y - 40
    x, y = TREE_X, (lerp(y0, y1, ramp(tt, TB, TB + 0.5, "inn")) if tt < TB + 0.5 else y1)
    if tt >= T_GET: x, y = lerp((x, y), p["hip"], ramp(tt, T_GET, T_GET + 0.3))
    O.draw_item_block(cr, x, y, "log", tt, 1.0)
S.prop(item)
S.sfx(T_GET + 0.3, "pop", 0.035)
S.set(TB + 1.1, "stand", "dead_stare", dur=0.5, look=(0.5, -0.9), tilt=-0.08)     # slowly looks up at the floating tree
S.set(TB + 3.1, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), tilt=0.0)       # back to us
S.blink(TB + 2.2)

# ================================================================ NIGHT 1: the dirt pillar.
S.cut(C2, cam=(540, 900, 1.15), x=0)
S.set(C2, "stand", "dead_stare", dur=0.0, breath=0.5)
def hut(cr, tt, p, ly):
    if ly != "front" or shot(tt) != 2: return
    for i in range(3):
        for k_ in range(9):
            if (i, k_) == (1, 7): continue
            O.draw_block(cr, 540 - 1.5 * BS + i * BS, FLOOR_Y - BS * (k_ + 1), BS, "dirt", sid=740 + i * 13 + k_)
S.prop(hut)
TK = T2 + 1.8
S.sfx(TK, "tok", 0.05); S.sfx(TK + 0.4, "tok", 0.05); S.shake(TK, 0.2, 4); S.shake(TK + 0.4, 0.2, 4)
S.set(TK + 0.8, "stand", "dead_stare", dur=0.25, look=(0.9, 0.0), breath=0.5)
S.set(TK + 2.9, "stand", "dead_stare", dur=0.25, look=(0.0, 0.0), breath=0.5)
S.set(TK + 3.8, "stand", "dead_stare", dur=0.3, lid=1.0, breath=0.5)
S.set(TK + 4.2, "stand", "dead_stare", dur=0.35, breath=0.5)

# ================================================================ DAY 41: the floor portal.
S.cut(C3, cam=(600, 930, 1.12), x=-260)
S.set(C3, "stand", "dead_stare", dur=0.0)
S.blink(T3 + 0.6)
S.walk_to(T3 + 0.9, -10, 1.0)                                         # to the edge (pit starts at x 600)
S.set(T3 + 2.3, "stand", "dead_stare", dur=0.3, look=(0.6, 0.95), tilt=0.06)          # looks down into it
S.set(T3 + 3.6, "stand", "dead_stare", dur=0.3, look=(0.0, 0.0), tilt=0.0)            # looks at us
T_STEP = T3 + 4.7
S.xkeys.append((T_STEP, 130, 0.35, "out")); S.x = 130
S.set(T_STEP, "stand", "dead_stare", dur=0.2, nowalk=1.0)
def fall(tt, p):
    if T_STEP + 0.25 <= tt < C4:
        d = 0.5 * 4200 * (tt - T_STEP - 0.25) ** 2
        for j in L.JOINTS: p[j] = (p[j][0], p[j][1] + d)
    return p
S.hook(fall)
S.sfx(T_STEP + 0.35, "whoosh", 0.05)
def pit(cr, tt, p, ly):
    if ly == "front" and shot(tt) == 3: O.draw_end_portal(cr, PIT0, PIT1, FLOOR_Y, 3 * BS, tt)
S.prop(pit)

# ================================================================ THE END: the dragon.
S.cut(C4, cam=(560, 840, 0.9), x=-250)
S.set(C4, "stand", "dead_stare", dur=0.0, look=(0.9, -0.4))
D = dict(O.DRAGON); D.update(x=1750.0, y=1100.0, legs=0.0, fl=1.0, look=(-1.0, 0.0))
dkeys = [(0.0, dict(D), 0)]
def dk(t, dur=0.3, ease="smooth", **kw):
    D.update(kw); dkeys.append((t, dict(D), dur, ease))
dk(T4 + 0.6, 2.4, "out", x=900.0, y=FLOOR_Y)
dk(T4 + 2.4, 0.6, legs=1.0)
dk(T4 + 2.8, 0.6, fl=0.0)
S.sfx(T4 + 0.8, "whoosh", 0.04); S.sfx(T4 + 1.8, "whoosh", 0.04)
S.sfx(T4 + 3.0, "thud", 0.1); S.shake(T4 + 3.0, 0.4, 10)
S.set(T4 + 3.2, "stand", "dead_stare", dur=0.3, look=(0.9, 0.1))
dk(T4 + 3.6, 0.6, hy=60.0, look=(-1.0, 0.3))                          # lowers its head at him
dk(T4 + 4.3, 0.25, "back", jaw=1.0)                                   # roars
S.sfx(T4 + 4.3, "wind", 0.09, dur=1.1); S.shake(T4 + 4.3, 1.0, 6)
dk(T4 + 5.3, 0.2, jaw=0.2)
dk(T_HIT - 0.25, 0.25, "inn", hx=-150.0)                              # SWIPE
dk(T_HIT + 0.05, 0.7, hx=0.0)
S.flash(T_HIT, 0.45, (0.9, 0.15, 0.15)); S.shake(T_HIT, 0.45, 18); S.sfx(T_HIT, "bonk", 0.09)
S.set(T_HIT, "stand", "dead_stare", dur=0.08, ease="snap", lean=-0.12, twitch=1.0)
S.set(T_HIT + 0.25, "stand", "dead_stare", dur=0.5, lean=0.0, twitch=1.0)
S.set(T_HIT + 0.9, "stand", "dead_stare", dur=0.6, look=(-0.6, 1.0), twitch=0.4)      # slowly looks down at the hearts
S.sfx(T_HIT + 1.0, "tick", 0.04); S.sfx(T_HIT + 1.9, "tick", 0.04)
S.set(T_HIT + 2.7, "stand", "dead_stare", dur=0.4, look=(0.9, 0.1))
# the pull: digs at his hip (no pocket), pulls out a sword
HIP = (588 - 250, 1092)
def dig(tt, p):
    if T_PULL <= tt < T_PULL + 1.2:
        u = ramp(tt, T_PULL, T_PULL + 0.25)
        d_ = ramp(tt, T_PULL + 0.25, T_PULL + 0.35) * (1 - ramp(tt, T_PULL + 1.0, T_PULL + 1.1))
        p["rhand"] = lerp(p["rhand"], (HIP[0] + 14 * math.sin(tt * 24) * d_, HIP[1] + 6 * math.sin(tt * 31) * d_), u)
    return p
S.hook(dig)
S.set(T_PULL, "stand", "dead_stare", dur=0.3, look=(0.35, 0.9), tilt=0.05)
S.set(T_PULL + 1.15, "sword_up", "dead_stare", dur=0.3, ease="back", look=(0.4, -0.3))
S.sfx(T_PULL + 1.2, "pop", 0.05)
def sword_draw(cr, x, y, s, t, p):
    if t >= T6: return
    O.draw_pixel_sword(cr, x, y, s * 0.95, ang=2.75 if t >= T5 else 0.55)   # lowered on the victory screen
S.place("sword", sword_draw, (0, 0), t_on=T_PULL + 1.2, layer="front", pop=True, follow="rhand")
S.set(T_PULL + 1.6, "sword_up", "dead_stare", dur=0.3, look=(0.9, 0.1))
S.xkeys.append((T_PULL + 1.7, -130, 0.9)); S.x = -130                    # walks up to it
S.sfx(T_PULL + 1.8, "step", 0.03); S.sfx(T_PULL + 2.25, "step", 0.03)
NOSE = (480, 1080)
def hits(tt, p):
    if T_F0 <= tt < T_F1:                                           # the flurry: a blur of hits
        v = 0.5 + 0.5 * math.sin(2 * math.pi * (tt - T_F0) * 8.0)
        p["rhand"] = lerp((p["neck"][0] + 110, 930), (NOSE[0] + 30, NOSE[1] - 20), v)
        p["relb"] = (p["neck"][0] + 95, 950)
    v = pulse(tt, T_LAST, 0.18)                                     # ...and one slow last tap
    if v > 0.01:
        p["rhand"] = lerp(p["rhand"], (NOSE[0] + 30, NOSE[1] - 20), v); p["relb"] = lerp(p["relb"], (p["neck"][0] + 100, 950), v)
    return p
S.hook(hits)
S.set(T_F0 - 0.1, "sword_up", "dead_stare", dur=0.2, look=(0.9, 0.2))
def flurry_fx(cr, tt, p, ly):
    if ly == "front" and T_F0 <= tt < T_F1:
        u = ((tt - T_F0) * 8.0) % 1.0
        L.draw_impact(cr, NOSE[0] - 10, NOSE[1] - 30, u, r=60, sid=int((tt - T_F0) * 8))
        L.motion_lines(cr, p["rhand"][0] - 40, p["rhand"][1], -2.4, n=3, length=70, spread=26, alpha=0.7)
    if ly == "front" and T_LAST - 0.02 <= tt < T_LAST + 0.4:
        L.draw_impact(cr, NOSE[0] - 10, NOSE[1] - 30, (tt - T_LAST) / 0.4, r=70, sid=99)
S.prop(flurry_fx)
for kk in range(4): S.sfx(T_F0 + 0.2 + kk * 0.75, "tok", 0.04)
S.sfx(T_LAST, "tok", 0.07)
dk(T_F0, 0.1, lid=0.6)
for kk in range(8):
    dk(T_F0 + kk * 0.375, 0.06, "snap", hx=-14.0 if kk % 2 else 10.0)
dk(T_F1, 0.3, hx=0.0, lid=0.0, look=(0.0, 0.0))                      # it looks at us
dk(T_LAST, 0.08, "snap", hx=-10.0, lid=1.0); dk(T_LAST + 0.15, 0.3, hx=0.0, lid=0.5)
dk(T_DIE, 2.2, "inn", fade=1.0, y=FLOOR_Y - 260.0, legs=0.4)
S.sfx(T_DIE + 0.2, "kaboom", 0.3); S.shake(T_DIE + 0.2, 1.6, 9); S.flash(T_DIE + 1.9, 0.7)
DT = Track(dkeys)
def dragon(cr, tt, p, ly):
    if ly != "back" or shot(tt) != 4: return
    st = DT.at(tt)
    wv = st["fl"] * math.sin(tt * 5.5) + (1 - st["fl"]) * 0.85
    st["flap"] = math.asin(max(-1.0, min(1.0, wv)))
    if st["fade"] < 0.999: O.draw_dragon(cr, st, tt)
    O.draw_death_beams(cr, st["x"], st["y"] - 280, (tt - T_DIE) / 2.6, tt)
S.prop(dragon)
S.set(T_F1 + 0.1, "sword_up", "dead_stare", dur=0.3, look=(0.9, 0.1))
S.set(T_DIE + 2.6, "sword_up", "dead_stare", dur=0.3, lid=1.0)
S.set(T5 - 0.05, "sword_up", "dead_stare", dur=0.3)

# ================================================================ the victory text. it keeps going.
S.cut(T5, cam=(540, 930, 1.15), x=-330)
S.set(T5, "stand", "dead_stare", dur=0.0, rhand_t="grip")
S.set(T5 + 4.2, "stand", "dead_stare", dur=0.25, look=(0.7, -0.5), rhand_t="grip")
S.set(T5 + 5.6, "stand", "dead_stare", dur=0.25, look=(0.0, 0.0), rhand_t="grip")

# ================================================================ the ask (deadpan). the half heart stays.
S.cut(T6, cam=M.CARD_CAM, x=0)
S.set(T6, "stand", "dead_stare", dur=0.0)
S.blink(T6 + 0.3)
S.the_ask(T6 + 0.4, hold=5.5)

if __name__ == "__main__":
    S.render("day004.mp4")
