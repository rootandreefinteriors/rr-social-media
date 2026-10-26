"""Day 4 — COMMENT episode: @neoblade75 "Beat Mc in hardcore mode:)" (Instagram, day 3 reel).

A generic blocky survival game (no logos, names or real characters), played dead straight. He WINS.
SHOT 1  Reads the comment. Stares. Slow blink. Tiny nod.
SHOT 2  HARD CUT: block world, "DAY 1", ten hardcore hearts in the corner. He walks to a tree and punches one log
        out of it, very slowly. The log pops out; the top of the tree stays floating in the air. He looks up at it.
        Looks back at us. The little log flies into him.
SHOT 3  HARD CUT: "NIGHT 1". A one-block-wide dirt pillar. Only his eyes, through a one-block window. Something
        knocks twice outside. His eyes slide over. Slide back.
SHOT 4  HARD CUT: "DAY 41". Three hearts left. A purple portal. He walks in. Looks at us from inside.
SHOT 5  HARD CUT: "THE END". A huge black blocky dragon flies in, lands, lowers its head, roars -- and swipes: down to
        HALF A HEART. He checks the hearts. Digs at his hip, pulls out a pixel sword. Walks up. Taps it once on the
        nose. Pause. The boss bar drains anyway, slowly. The dragon dissolves into beams of light. He doesn't move.
SHOT 6  HARD CUT: black. The victory text scrolls up (YOU WON. ON HARDCORE. WITH HALF A HEART. ...). Dead stare.
END     HARD CUT to the white void; the half heart is still in the corner, blinking. The ask, deadpan.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y
from ink import smooth, draw_text

BS = 110
SKY_DAY, SKY_NIGHT, SKY_END, SKY_BLACK = (0.80, 0.89, 0.98), (0.10, 0.12, 0.25), (0.24, 0.19, 0.30), (0.30, 0.30, 0.33)
T1, T2, T3, T4 = 6.4, 15.0, 21.0, 28.6          # shot starts: day 1 / night 1 / day 41 / the end
T_HIT = T4 + 5.6
T_PULL = T_HIT + 2.6
T_BONK = 39.9
T_DIE = T_BONK + 2.9
T5 = T_DIE + 3.0                                # victory text
T6 = T5 + 7.5                                   # back to the void: the ask
TREE_X = 840

L.POSES["punch"] = dict(relb=(660, 930), rhand=(690, 1010), rhand_t="fist", lhand_t="fist")
L.POSES["sword_up"] = dict(relb=(650, 960), rhand=(700, 900), rhand_t="grip")

S = M.Scene()
S.auto_blinks = False
S.card("neoblade75", "Beat Mc in hardcore mode:)", "0", t0=0.35)
S.sfx(0.35, "tick", 0.04)

def shot(t): return 0 if t < T1 else 1 if t < T2 else 2 if t < T3 else 3 if t < T4 else 4 if t < T5 else 5 if t < T6 else 6

# ================================================================ world backgrounds
def sky(cr, col):
    cr.rectangle(-3000, -3000, 8000, 8000); cr.set_source_rgb(*col); cr.fill()
def bg(cr, t):
    k = shot(t)
    if k in (1, 3):
        sky(cr, SKY_DAY); O.draw_square_sun(cr, 230, 330)
        O.draw_block_cloud(cr, 120 + 6 * t, 520); O.draw_block_cloud(cr, -260 + 6 * t, 430, 200, 40)
        O.draw_ground(cr)
    elif k == 2:
        sky(cr, SKY_NIGHT); O.draw_square_sun(cr, 230, 360, 110, moon=True)
        for i in range(14): cr.rectangle(-100 + (i * 173) % 1300, 150 + (i * 97) % 700, 7, 7)
        cr.set_source_rgb(0.9, 0.9, 1.0); cr.fill()
        O.draw_ground(cr)
    elif k == 4:
        sky(cr, SKY_END)
        for i in range(22): cr.rectangle(-500 + (i * 211) % 2200, -200 + (i * 131) % 1300, 8, 8)
        cr.set_source_rgba(0.95, 0.9, 1.0, 0.8); cr.fill()
        O.draw_ground(cr, "endstone", "endstone")
    elif k == 5:
        sky(cr, SKY_BLACK)
S.background(bg)

# ================================================================ HUD: hardcore hearts (stay to the very end)
def health(t):
    if t < T3: return 10.0
    if t < T_HIT: return 3.0
    return 0.5
def hud(cr, t):
    if t < T1: return
    dark = shot(t) in (2, 4, 5)
    blink = 0.5 + 0.5 * math.sin(t * 7) if t >= T_HIT else 0.0
    draw_text(cr, "HARDCORE", 92, 1372, 30, color=(240, 240, 240) if dark else (18, 18, 22), anchor="left")
    O.draw_hearts_bar(cr, 100, 1402, health(t), s=4.4, gap=6, blink=blink)
    if T_HIT <= t < T_HIT + 0.5:                                    # the hit: hearts shake
        pass
def labels(cr, t):
    for t0, txt, col in ((T1, "DAY 1", (18, 18, 22)), (T2, "NIGHT 1", (240, 240, 240)), (T3, "DAY 41", (18, 18, 22)),
                         (T4, "THE END", (240, 240, 240))):
        if t0 + 0.15 <= t < t0 + 2.4:
            draw_text(cr, txt, 92, 300, 72, color=col, anchor="left", alpha=min(1.0, (t0 + 2.4 - t) / 0.3))
def bossbar(cr, t):
    if not (T4 + 1.0 <= t < T_DIE + 1.6): return
    a = min(1.0, (t - T4 - 1.0) / 0.4) * (1 - ramp(t, T_DIE + 1.0, T_DIE + 1.6))
    hp = 1.0 - ramp(t, T_BONK + 0.9, T_BONK + 2.6, "linear")
    draw_text(cr, "DRAGON", 540, 455, 34, color=(240, 240, 240), alpha=a)
    cr.rectangle(220, 485, 640, 20); cr.set_source_rgba(0.25, 0.08, 0.3, a); cr.fill()
    cr.rectangle(220, 485, 640 * hp, 20); cr.set_source_rgba(0.88, 0.38, 0.92, a); cr.fill()
    cr.rectangle(220, 485, 640, 20); cr.set_source_rgba(1, 1, 1, a); cr.set_line_width(3); cr.stroke()
SCROLL = ["YOU WON.", "ON HARDCORE.", "WITH HALF A HEART.", "IT TOOK 41 DAYS.", "NOBODY SAW IT.", "THIS TEXT WILL NOW",
          "SCROLL FOR", "TWENTY MINUTES."]
def scroll(cr, t):
    if not (T5 <= t < T6): return
    cr.save(); cr.rectangle(0, 470, 1080, 830); cr.clip()
    for i, line in enumerate(SCROLL):
        y = 1300 + i * 95 - (t - T5) * 128
        if 440 < y < 1360:
            a = min(1.0, (y - 470) / 80, (1300 - y) / 80)
            if a > 0: draw_text(cr, line, 620, y, 56, color=(240, 240, 240), alpha=a)
    cr.restore()
for f in (scroll, bossbar, labels, hud): S.overlays.insert(0, f)     # all under the comment card

# ================================================================ SHOT 1: reads it. stares. accepts.
S.set(0.0, "stand", "deadpan", dur=0.0)
S.read_card(0.8, react="dead_stare", lines=1, face="deadpan")
S.set(4.0, "stand", "dead_stare", dur=0.25, lid=1.0)
S.set(4.4, "stand", "resigned", dur=0.35)
def nod(tt, p, a=5.0):
    v = 16 * math.sin(math.pi * min(1.0, max(0.0, (tt - a) / 0.7)))
    if v > 0.01: p["head"] = (p["head"][0], p["head"][1] + v)
    return p
S.hook(nod)

# ================================================================ SHOT 2: day 1. punch a tree.
S.cut(T1, cam=(560, 930, 1.15), x=-120)
S.set(T1, "stand", "dead_stare", dur=0.0)
S.blink(T1 + 0.6)
S.walk_to(T1 + 1.0, 140, 1.4)                                      # -> 8.65
TP0, TP1 = 9.0, 11.6
S.set(TP0 - 0.2, "punch", "dead_stare", dur=0.25, look=(0.75, 0.25))
def punch_v(tt):
    if not (TP0 <= tt < TP1): return 0.0
    return max(0.0, math.sin(2 * math.pi * (tt - TP0) * 3.2)) ** 0.7
def punching(tt, p):
    v = punch_v(tt)
    if v > 0:
        p["rhand"] = lerp(p["rhand"], (788, 1090), v); p["relb"] = lerp(p["relb"], (740, 990), v)
    return p
S.hook(punching)
k = 0
while TP0 + (k + 0.25) / 3.2 < TP1:
    S.sfx(TP0 + (k + 0.25) / 3.2, "tap", 0.028); k += 1
TB = TP1
S.set(TB, "stand", "dead_stare", dur=0.35, look=(0.6, 0.6))
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
T_GET = TB + 2.7
def item(cr, tt, p, ly):
    if ly != "front" or not (TB <= tt < T_GET + 0.3): return
    y0, y1 = FLOOR_Y - BS * 3.5, FLOOR_Y - 40
    if tt < TB + 0.5: x, y = TREE_X, lerp(y0, y1, ramp(tt, TB, TB + 0.5, "inn"))
    else: x, y = TREE_X, y1
    if tt >= T_GET:                                                 # flies into him
        u = ramp(tt, T_GET, T_GET + 0.3); x, y = lerp((x, y), p["hip"], u)
    O.draw_item_block(cr, x, y, "log", tt, 1.0)
S.prop(item)
S.sfx(T_GET + 0.3, "pop", 0.035)
S.set(TB + 0.9, "stand", "dead_stare", dur=0.3, look=(0.5, -0.9), tilt=-0.06)     # looks up at the floating tree
S.set(TB + 2.2, "stand", "dead_stare", dur=0.25, look=(0.0, 0.0), tilt=0.0)       # back to us
S.blink(TB + 1.6)

# ================================================================ SHOT 3: night 1. the dirt pillar.
S.cut(T2, cam=(540, 900, 1.15), x=0)
S.set(T2, "stand", "dead_stare", dur=0.0, breath=0.5)
def hut(cr, tt, p, ly):
    if ly != "front" or shot(tt) != 2: return
    for i in range(3):
        for k_ in range(9):
            if (i, k_) == (1, 7): continue
            O.draw_block(cr, 540 - 1.5 * BS + i * BS, FLOOR_Y - BS * (k_ + 1), BS, "dirt", sid=740 + i * 13 + k_)
S.prop(hut)
S.sfx(T2 + 2.0, "tok", 0.05); S.sfx(T2 + 2.35, "tok", 0.05); S.shake(T2 + 2.0, 0.2, 4); S.shake(T2 + 2.35, 0.2, 4)
S.set(T2 + 2.7, "stand", "dead_stare", dur=0.15, look=(0.9, 0.0), breath=0.5)
S.set(T2 + 4.1, "stand", "dead_stare", dur=0.15, look=(0.0, 0.0), breath=0.5)
S.set(T2 + 4.9, "stand", "dead_stare", dur=0.3, lid=1.0, breath=0.5)
S.set(T2 + 5.3, "stand", "dead_stare", dur=0.35, breath=0.5)

# ================================================================ SHOT 4: day 41. the portal.
PORTAL_X = 800
S.cut(T3, cam=(680, 930, 1.05), x=-260)
KP = dict()
S.set(T3, "stand", "dead_stare", dur=0.0, **KP)
S.set(T3 + 1.6, "stand", "dead_stare", dur=0.3, lid=1.0, **KP)
S.set(T3 + 2.0, "stand", "dead_stare", dur=0.35, **KP)
S.set(T3 + 2.6, "stand", "dead_stare", dur=0.2, look=(0.9, 0.0), **KP)
S.walk_to(T3 + 3.4, 260, 1.8)                                         # -> into the portal
def portal(cr, tt, p, ly):
    if shot(tt) != 3: return
    if ly == "back": O.draw_portal(cr, PORTAL_X, FLOOR_Y, tt, "frame")
    else: O.draw_portal(cr, PORTAL_X, FLOOR_Y, tt, "swirl", alpha=0.8)
S.prop(portal)
S.sfx(T3 + 5.2, "whoosh", 0.05)
S.set(T3 + 6.0, "stand", "dead_stare", dur=0.25, look=(0.0, 0.0), **KP)

# ================================================================ SHOT 5: the end. the dragon.
S.cut(T4, cam=(560, 840, 0.9), x=-250)
S.set(T4, "stand", "dead_stare", dur=0.0, look=(0.9, -0.4), **KP)
D = dict(O.DRAGON); D.update(x=1750.0, y=1100.0, legs=0.0, fl=1.0, look=(-1.0, 0.0))
dkeys = [(0.0, dict(D), 0)]
def dk(t, dur=0.3, ease="smooth", **kw):
    D.update(kw); dkeys.append((t, dict(D), dur, ease))
dk(T4 + 0.6, 2.4, "out", x=900.0, y=FLOOR_Y)
dk(T4 + 2.4, 0.6, legs=1.0)
dk(T4 + 2.8, 0.6, fl=0.0)
S.sfx(T4 + 0.8, "whoosh", 0.04); S.sfx(T4 + 1.8, "whoosh", 0.04)
S.sfx(T4 + 3.0, "thud", 0.1); S.shake(T4 + 3.0, 0.4, 10)
S.set(T4 + 3.2, "stand", "dead_stare", dur=0.3, look=(0.9, 0.1), **KP)
dk(T4 + 3.6, 0.6, hy=60.0, look=(-1.0, 0.3))                          # lowers its head at him
dk(T4 + 4.3, 0.25, "back", jaw=1.0)                                   # roars
S.sfx(T4 + 4.3, "wind", 0.09, dur=1.1); S.shake(T4 + 4.3, 1.0, 6)
dk(T4 + 5.3, 0.2, jaw=0.2)
dk(T_HIT - 0.25, 0.25, "inn", hx=-150.0)                              # SWIPE
dk(T_HIT + 0.05, 0.7, hx=0.0)
S.flash(T_HIT, 0.45, (0.9, 0.15, 0.15)); S.shake(T_HIT, 0.45, 18); S.sfx(T_HIT, "bonk", 0.09)
S.set(T_HIT, "stand", "dead_stare", dur=0.08, ease="snap", lean=-0.12, twitch=1.0, **KP)
S.set(T_HIT + 0.25, "stand", "dead_stare", dur=0.5, lean=0.0, twitch=1.0, **KP)
S.set(T_HIT + 1.0, "stand", "dead_stare", dur=0.3, look=(-0.6, 1.0), twitch=0.4, **KP)   # checks the hearts
S.set(T_HIT + 2.1, "stand", "dead_stare", dur=0.25, look=(0.9, 0.1), **KP)
# the pull: digs at his hip (no pocket), pulls out a sword
HIP = (588 - 250, 1092)
def dig(tt, p):
    if T_PULL <= tt < T_PULL + 1.2:
        u = ramp(tt, T_PULL, T_PULL + 0.25)
        d_ = ramp(tt, T_PULL + 0.25, T_PULL + 0.35) * (1 - ramp(tt, T_PULL + 1.0, T_PULL + 1.1))
        p["rhand"] = lerp(p["rhand"], (HIP[0] + 14 * math.sin(tt * 24) * d_, HIP[1] + 6 * math.sin(tt * 31) * d_), u)
    return p
S.hook(dig)
S.set(T_PULL, "stand", "dead_stare", dur=0.3, look=(0.35, 0.9), tilt=0.05, **KP)
S.set(T_PULL + 1.15, "sword_up", "dead_stare", dur=0.3, ease="back", look=(0.4, -0.3), **KP)
S.sfx(T_PULL + 1.2, "pop", 0.05)
def sword_draw(cr, x, y, s, t, p):
    if t >= T6: return
    O.draw_pixel_sword(cr, x, y, s * 0.95, ang=2.75 if t >= T5 else 0.55)   # lowered on the victory screen
S.place("sword", sword_draw, (0, 0), t_on=T_PULL + 1.2, layer="front", pop=True, follow="rhand")
S.set(T_PULL + 1.7, "sword_up", "dead_stare", dur=0.3, look=(0.9, 0.1), **KP)
S.xkeys.append((T_PULL + 1.9, -130, 0.9)); S.x = -130                    # walks up to it
S.sfx(T_PULL + 2.0, "step", 0.03); S.sfx(T_PULL + 2.45, "step", 0.03)
def bonk(tt, p):
    v = pulse(tt, T_BONK, 0.12)
    if v > 0.01:
        p["rhand"] = lerp(p["rhand"], (p["neck"][0] + 175, 1060), v); p["relb"] = lerp(p["relb"], (p["neck"][0] + 110, 930), v)
    return p
S.hook(bonk)
S.sfx(T_BONK, "tok", 0.07)
dk(T_BONK, 0.08, "snap", hx=-12.0, lid=1.0); dk(T_BONK + 0.15, 0.3, hx=0.0, lid=0.0)
dk(T_BONK + 0.9, 0.5, look=(0.0, 0.0))                                 # it looks at us. the bar drains.
dk(T_BONK + 1.6, 1.0, lid=0.5)
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
S.set(T_DIE + 2.6, "sword_up", "dead_stare", dur=0.3, lid=1.0, **KP)
S.set(T_DIE + 3.0 - 0.05, "sword_up", "dead_stare", dur=0.3, **KP)

# ================================================================ SHOT 6: the victory text. it keeps going.
S.cut(T5, cam=(540, 930, 1.15), x=-330)
S.set(T5, "stand", "dead_stare", dur=0.0, rhand_t="grip", **KP)
S.set(T5 + 5.0, "stand", "dead_stare", dur=0.25, look=(0.7, -0.5), rhand_t="grip", **KP)
S.set(T5 + 6.4, "stand", "dead_stare", dur=0.25, look=(0.0, 0.0), rhand_t="grip", **KP)

# ================================================================ the ask (deadpan). the half heart stays.
S.cut(T6, cam=M.CARD_CAM, x=0)
S.set(T6, "stand", "dead_stare", dur=0.0, **KP)
S.blink(T6 + 0.3)
S.the_ask(T6 + 0.5, hold=6.5, keep=KP)

if __name__ == "__main__":
    S.render("day004.mp4")
