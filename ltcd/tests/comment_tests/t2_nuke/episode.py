"""TEST 2 (not posted) — top comment: "build a nuclear bomb and set it off underwater". Looney Tunes rules.

Reads it, rubs his hands. Dives into a cartoon construction cloud (tools + stars flying out) -> ta-da: a big round
ACME bomb with a red button. Thumbs up. Reads "underwater" -> POPs a snorkel onto his face. The world floods; the water
goes right over the top of his snorkel. "...oh." Shrug. Slow-motion underwater walk to the bomb, presses the button, it
starts blinking. He runs. Empty frame, ticking speeds up. He peeks back in, covering his ears. FLASH / KABOOM / the
whole ocean is blown away. Silence. He's standing there sooty, hair standing up. A fish falls out of the sky onto his
head, flops, hops away. He coughs a puff of smoke. Weak thumbs up. The ask (still sooty).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y, ellipse, stroke_ink, fill_paper, sketch_circle
from ink import ease_out, smooth

BX, BS = 770, 0.9                                  # the bomb
BOMB_TOP = FLOOR_Y - 2 * 165 * BS
BUTTON = (BX, FLOOR_Y - 165 * BS - 165 * BS - 42 * BS)

S = M.Scene()
S.card("acme.intern", "build a nuclear bomb and set it off underwater", "3.1K", t0=0.3)
S.sfx(0.3, "tick", 0.06)

# --- reads it. rubs his hands.
S.read_card(0.6, react="mischievous", lines=3)
t = S.t
S.set(t, "clap", "mischievous", dur=0.25)
S.hook(lambda tt, p, a=t + 0.1, b=t + 1.1: (p.update(lhand=(p["lhand"][0] + 10 * math.sin(tt * 30), p["lhand"][1]),
                                                     rhand=(p["rhand"][0] - 10 * math.sin(tt * 30), p["rhand"][1])) or p) if a <= tt < b else p)
S.set(t + 1.2, "stand", "determined", dur=0.25, ease="back")
S.t = t + 1.5
S.walk_to(S.t, -170, 0.9)

# --- dives into the construction cloud
t = S.t
S.set(t, "crouch", "determined", dur=0.18)
S.set(t + 0.2, "cannonball", "determined", dur=0.1, ease="snap")
S.xkeys.append((t + 0.22, 60, 0.25))
S._hop(t + 0.32, 120, 0.1)
T_C0, T_C1 = t + 0.3, t + 3.3
S.set(T_C0 + 0.12, "stand", "neutral", dur=0.05, show=0.0, nowalk=1.0)
S.xkeys.append((T_C1 - 0.5, -170, 0.05))
S.prop(lambda cr, tt, p, ly: O.draw_build_cloud(cr, BX - 90, 1250, tt, T_C0, T_C1 - T_C0, r=300) if ly == "front" else None)
S.sfx(T_C0, "rummage", 0.06, dur=2.9)
for dt in (0.5, 1.2, 1.9, 2.5): S.sfx(T_C0 + dt, "bonk", 0.04)
S.sfx(T_C0 + 0.9, "clap", 0.04)
bomb_state = dict(light=0.0, pressed=0.0)
def bomb(cr, x, yb, s, t, p):
    O.draw_bomb(cr, x, yb, BS * s, t, light=bomb_light(t), pressed=ramp(t, T_PRESS, T_PRESS + 0.12))
S.place("bomb", bomb, (BX, FLOOR_Y), t_on=T_C1 - 0.1, layer="back", pop=True)
S.poof(T_C1 - 0.25, (BX - 90, 1250), r=240, sound=False); S.sfx(T_C1 - 0.1, "poof", 0.05)
S.set(T_C1 - 0.08, "present", "proud", dur=0.15, ease="back", show=1.0)
S.sfx(T_C1 + 0.1, "ding", 0.06)
S.t = T_C1 + 1.3
S.thumbs_up(S.t, 0.9)

# --- "...underwater." -> POP, snorkel
t = S.t
S.set(t, "stand", "thinking", dur=0.3, look=(0.75, -0.75))
S.set(t + 1.0, "stand", "idea", dur=0.2, ease="back")
S.hop(t + 1.05, 1, 18)
S.pocket_pull(t + 1.6, "snorkel", lambda cr, x, y, s, tt, p: O.draw_snorkel(cr, p, s), (370, 820), layer="front", narrow_w=0)
T_SNORK = t + 1.6 + 2.1
S.set(T_SNORK + 0.6, "stand", "proud", dur=0.25, mouth="flat")

# --- the world floods (right over the top of his snorkel)
T_W0, T_W1 = T_SNORK + 1.4, T_SNORK + 3.6
T_BOOM = 0.0                                          # set below
def level(t):
    if t < T_BOOM: return lerp(FLOOR_Y + 30, -260, smooth((t - T_W0) / (T_W1 - T_W0))) if t >= T_W0 else FLOOR_Y + 500
    return lerp(-260, -3200, ease_out((t - T_BOOM) / 0.45))
S.set(T_W0 + 0.2, "stand", "surprised", dur=0.25, look=(0.0, 0.9), mouth="flat")
S.set(T_W0 + 1.0, "stand", "surprised", dur=0.4, look=(0.0, -0.9), mouth="flat")
for k in range(5): S.sfx(T_W0 + 0.3 + k * 0.45, "bubble", 0.045)
T_OH = T_W1 + 0.3
S.set(T_OH, "stand", "bored", dur=0.3, look=(-0.4, -0.9), mouth="flat")       # looks at the snorkel top. ...oh.
S.sfx(T_OH + 0.4, "bubble", 0.06)
S.set(T_OH + 1.3, "stand", "annoyed", dur=0.25, look=(0.0, 0.0), mouth="flat")
S.blink(T_OH + 1.7)
S.t = T_OH + 2.3
S.shrug(S.t, 0.7)

# --- slow-motion walk to the bomb, press the button
S.walk_to(S.t, 20, 1.5)
t = S.t
T_PRESS = t + 0.75
def press_hook(tt, p, a=t, b=T_PRESS + 0.55):
    if a <= tt < b:
        u = ramp(tt, a, a + 0.45)
        tgt = (BUTTON[0] - 6, BUTTON[1] - 22 + 14 * ramp(tt, T_PRESS, T_PRESS + 0.12))
        p["rhand"] = lerp(p["rhand"], tgt, u); p["relb"] = lerp(p["relb"], (BUTTON[0] - 110, BUTTON[1] - 160), u)
        p["rhand_t"] = "point"
    return p
S.set(t, "stand", "concentrating", dur=0.35, lean=0.15, look=(0.9, 0.5), mouth="flat")
S.hook(press_hook)
S.sfx(T_PRESS, "boop", 0.07)
T_L0 = T_PRESS + 0.2
def bomb_light(t):
    if t < T_L0 or t >= T_BOOM: return 0.0
    u = t - T_L0
    ph = 2 * math.pi * (1.6 * u + 0.55 * u * u)          # blinking speeds up
    return 1.0 if math.sin(ph) > 0 else 0.15
S.set(T_PRESS + 0.6, "stand", "worried", dur=0.25, lean=0.0, look=(0.9, -0.3), mouth="flat")
S.set(T_PRESS + 1.3, "stand", "scared", dur=0.12, ease="snap", eyescale=1.25, mouth="flat")
S.t = T_PRESS + 1.9

# --- RUN
S.run_to(S.t, -950, 1.0)
t_run = S.t
S.camera(t_run - 0.4, 580, 1010, 1.22, 1.8)
# peeks back in from the left edge, covering his ears
S.xkeys.append((t_run + 0.9, -400, 0.45)); S.x = -400
S.set(t_run + 0.9, "cower", "scared", dur=0.3, lean=0.18, mouth="flat")
T_BOOM = t_run + 2.4

# blinking ticks (sound follows the light)
tt, last = T_L0, 0.0
while tt < T_BOOM - 0.02:
    if bomb_light(tt) > 0.5 and last < 0.5: S.sfx(tt, "tick", 0.05)
    last = bomb_light(tt); tt += 1 / 120

# --- KABOOM
S.flash(T_BOOM, 0.8)
S.shake(T_BOOM, 1.5, 34)
S.sfx(T_BOOM, "kaboom", 0.5)
S.camera(T_BOOM, 540, 930, 1.15, 0.05)
S.objects["bomb"]["t_off"] = T_BOOM; S.objects["snorkel"]["t_off"] = T_BOOM
S.xkeys.append((T_BOOM + 0.02, -250, 0.02)); S.x = -250
S.set(T_BOOM + 0.02, "stand", "neutral", dur=0.02, nowalk=1.0, eyescale=1.15, mouth="flat", smile=0.0, brow=0.4)
S.set(T_BOOM + 0.4, "stand", "neutral", dur=0.3, eyescale=1.1, mouth="flat", smile=0.0, brow=0.3)
def big_bubble(cr, tt, p, ly):
    if ly != "front" or not (T_BOOM <= tt < T_BOOM + 0.7): return
    u = (tt - T_BOOM) / 0.7
    sketch_circle(cr, BX, 1250, 60 + 1900 * ease_out(u), 16 * (1 - u) + 2, sid=990, fill=None, alpha=1 - u)
def water(cr, tt, p, ly):
    if ly != "front": return
    lv = level(tt)
    if lv < FLOOR_Y + 100 and lv > -3000:
        O.draw_water(cr, lv, tt)
        if T_W1 <= tt < T_BOOM: O.draw_bubbles(cr, tt, *O.snorkel_top(p), n=3, spread=10, rise=200, size=9, seed=1)
S.prop(water); S.prop(big_bubble)
S.prop(lambda cr, tt, p, ly: O.draw_crater(cr, BX, 1.0, tt, smoke=1 - ramp(tt, T_BOOM + 4, T_BOOM + 12)) if ly == "back" and tt >= T_BOOM else None)
S.prop(lambda cr, tt, p, ly: O.draw_rain(cr, tt, T_BOOM + 0.6, 2.4, n=22, x0=60, x1=1040, y_top=120) if ly == "front" else None)
# a fish swims by while it's underwater
S.prop(lambda cr, tt, p, ly: O.draw_fish(cr, lerp(1150, -150, (tt - T_W1 - 1.0) / 5.0), 930 + 20 * math.sin(tt * 2), 0.9, 0.0, tt)
       if ly == "back" and T_W1 + 1.0 <= tt < min(T_W1 + 6.0, T_BOOM) else None)
# underwater float: everything but the feet sways a little
def floaty(tt, p):
    if T_W1 - 0.5 <= tt < T_BOOM:
        k = ramp(tt, T_W1 - 0.5, T_W1 + 0.5)
        dy = -9 * math.sin(tt * 1.7) * k
        for j in ("head", "neck", "hip", "lelb", "lhand", "relb", "rhand"): p[j] = (p[j][0], p[j][1] + dy)
        p["curl"] = p.get("curl", 0.0) + 0.35 * math.sin(tt * 1.3) * k
    return p
S.hook(floaty)
# soot + frizz + a wisp of smoke from then on
S.hook(lambda tt, p: (p.update(soot=1.0, frizz=1.0, fx_steam=max(p.get("fx_steam", 0), 0.5 - 0.3 * ramp(tt, T_BOOM + 3, T_BOOM + 10)))
                       or p) if tt >= T_BOOM else p)
S.blink(T_BOOM + 1.6, T_BOOM + 2.5)

# --- a fish falls out of the sky onto his head, flops, hops off
T_F0 = T_BOOM + 3.0; T_F1 = T_F0 + 0.5; T_F2 = T_F1 + 1.3; T_F3 = T_F2 + 0.5
def fish(cr, tt, p, ly):
    if ly != "front" or not (T_F0 <= tt < T_F3 + 1.6): return
    hx, hy = p["head"]
    top = (hx + 5, hy - L.HEAD_R - 22)
    if tt < T_F1:
        u = smooth((tt - T_F0) / (T_F1 - T_F0)) ** 1.6
        O.draw_fish(cr, top[0], lerp(-150, top[1], u), 1.0, 0.0, tt)
    elif tt < T_F2:
        O.draw_fish(cr, top[0], top[1] - 10 * abs(math.sin(tt * 11)), 1.0, 0.0, tt, flop=1.0)
    elif tt < T_F3:
        u = (tt - T_F2) / (T_F3 - T_F2)
        O.draw_fish(cr, lerp(top[0], top[0] + 260, u), lerp(top[1], FLOOR_Y - 30, u) - 220 * math.sin(math.pi * u), 1.0, 2.5 * u, tt)
    else:
        u = (tt - T_F3) / 1.6
        hop = abs(math.sin(u * 3 * math.pi))
        O.draw_fish(cr, top[0] + 260 + 520 * u, FLOOR_Y - 30 - 90 * hop, 1.0, 0.4 * math.sin(tt * 12), tt)
S.prop(fish)
S.sfx(T_F1, "pat", 0.06)
for k in range(3): S.sfx(T_F3 + k * 0.53, "pat", 0.035)
S.set(T_F1 + 0.15, "stand", "neutral", dur=0.25, look=(0.0, -1.0), eyescale=1.1, mouth="flat", smile=0.0)
S.set(T_F2 + 0.2, "stand", "neutral", dur=0.3, look=(1.0, 0.4), mouth="flat", smile=0.0)
# coughs a puff of smoke
T_CO = T_F3 + 1.4
S.set(T_CO, "stand", "neutral", dur=0.1, ease="snap", eyes="closed", mouth="o", open=0.5, tilt=0.06)
S._hop(T_CO + 0.05, 8, 0.06)
S.prop(lambda cr, tt, p, ly: L.draw_poof(cr, p["head"][0] + 30, p["head"][1] + 90, (tt - T_CO) / 0.7, r=55, sid=5) if ly == "front" else None)
S.sfx(T_CO, "poof", 0.04)
S.set(T_CO + 0.5, "stand", "neutral", dur=0.25, mouth="flat", smile=0.1)
S.t = T_CO + 0.9
S.thumbs_up(S.t, 1.1)
S.walk_to(S.t, -170, 0.6)

S.the_ask(S.t, hold=9.0)

if __name__ == "__main__":
    S.render("ltcd_test2_acme_bomb.mp4")
