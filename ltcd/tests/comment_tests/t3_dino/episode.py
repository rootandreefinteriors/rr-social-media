"""TEST 3 (not posted) — top comment: "tickling match with a dinosaur where the loser buys the winner ice cream".

Reads it, looks around: a dinosaur? THUD. THUD. A T. rex walks in. He's terrified -- it smiles and wiggles its tiny
arms hello. He points at the comment; it nods. DING. His turn: tickles its belly -- it pulls its head back and stares
down at him, deadpan. A feather (POP) under the chin -- it yawns. Its turn: it leans in and wiggles its tiny arms,
nowhere near him -- he instantly collapses laughing on the floor. It looks at its own arms, then gets very proud.
Loser buys: he POPs out a three-scoop cone. Its tiny arms can't reach. He feeds it: CHOMP, gone. He checks his hand.
Hearts. The ask, with his new friend standing beside him.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y

CAM = (540, 840, 0.9)                     # a little wider than usual so the dino's head stays clear of the card
DX0, DX = 1500, 840                       # dino walks in from DX0 to DX
STEP = (DX0 - DX) / 5                     # 5 steps

L.POSES["tickle_ready"] = dict(lelb=(415, 965), lhand=(445, 845), relb=(665, 965), rhand=(640, 840), lhand_t="open",
                               rhand_t="open")

S = M.Scene(x0=-260)
S.card("tinyarms.club", "tickling match with a dinosaur where the loser buys the winner ice cream", "5.8K", t0=0.3)
S.camkeys[0] = (0.0, CAM, 0); S.cam = CAM
S.sfx(0.3, "tick", 0.06)

# ---------------------------------------------------------------- the dino's own timeline
D = dict(O.DINO); D.update(x=DX0, s=1.0, look=(-1.0, 0.1), smile=0.2, lean=0.0)
dkeys = [(0.0, dict(D), 0)]
def dk(t, dur=0.3, ease="smooth", **kw):
    D.update(kw); dkeys.append((t, dict(D), dur, ease))
dblinks = []

# ---------------------------------------------------------------- reads it. a dinosaur?
S.read_card(0.6, react="confused", lines=3)
S.look(S.t, (-1.0, 0.0), 0.2); S.look(S.t + 0.55, (1.0, 0.0), 0.2)
S.t += 1.1
S.shrug(S.t, 0.6)

# ---------------------------------------------------------------- THUD. THUD. it walks in
T_WALK0, T_WALK1 = S.t + 0.2, S.t + 3.2
dk(T_WALK0, 0.0); dk(T_WALK0 + 0.001, T_WALK1 - T_WALK0, "linear", x=DX)
def dino_x(t):
    return DX0 if t < T_WALK0 else (DX if t >= T_WALK1 else lerp(DX0, DX, (t - T_WALK0) / (T_WALK1 - T_WALK0)))
for k in range(1, 6):                                    # a thud + a little shake on every footfall
    tk = T_WALK0 + (T_WALK1 - T_WALK0) * k / 5
    S.sfx(tk, "thud", 0.12); S.shake(tk, 0.25, 7)
S.set(T_WALK0, "stand", "surprised", dur=0.1, ease="snap", look=(1.0, 0.0)); S._hop(T_WALK0 + 0.05, 16)
S.set(T_WALK0 + 0.7, "stand", "scared", dur=0.3, look=(1.0, -0.1))
dk(T_WALK1 + 0.1, 0.4, look=(-1.0, 0.25), smile=0.0)    # stops. looks down at him.
T_HI = T_WALK1 + 1.0
dk(T_HI, 0.25, "back", smile=1.0, blush=0.8, brow=0.6, arms=1.0)   # big smile, tiny-arm wave
dk(T_HI + 1.3, 0.3, arms=0.0, blush=0.4)
S.set(T_HI + 0.4, "stand", "happy", dur=0.3, look=(1.0, 0.0))
S.wave(T_HI + 0.8, 1.0, face="happy")
dblinks += [T_HI + 2.0]

# ---------------------------------------------------------------- "tickle match?" (points at the comment) -> nod -> DING
t = S.t + 0.1
S.set(t, "point_up", "eager", dur=0.25, ease="back", look=(0.7, -0.8))
dk(t + 0.6, 0.15, bob=24.0); dk(t + 0.8, 0.15, bob=0.0); dk(t + 1.0, 0.15, bob=24.0); dk(t + 1.2, 0.2, bob=0.0)
T_DING = t + 1.6
S.sfx(T_DING, "ding", 0.07)
S.set(T_DING, "tickle_ready", "determined", dur=0.2, ease="back")
S.hook(lambda tt, p, a=T_DING, b=T_DING + 1.3: (p.update(lhand=(p["lhand"][0] + 7 * math.sin(tt * 34), p["lhand"][1] + 5 * math.sin(tt * 29)),
                                                         rhand=(p["rhand"][0] + 7 * math.sin(tt * 31), p["rhand"][1] + 5 * math.sin(tt * 37))) or p) if a <= tt < b else p)
dk(T_DING, 0.2, brow=-1.0, smile=0.5, blush=0.0, arms=1.0)
dk(T_DING + 1.3, 0.2, arms=0.0, brow=0.0, smile=0.3)
S.t = T_DING + 1.4

# ---------------------------------------------------------------- his turn: belly tickle (it pulls its head back, deadpan)
S.walk_to(S.t, 30, 0.9)
dk(S.t - 0.8, 0.5, lean=-0.9, look=(-0.4, 0.95), smile=0.0, lid=0.45)
T_TK = S.t
BELLY = [(DX - 112, 985), (DX - 98, 1062)]
def tickle_hook(tt, p, a=T_TK, b=T_TK + 2.0):
    if a <= tt < b:
        u = ramp(tt, a, a + 0.25) * (1 - ramp(tt, b - 0.2, b))
        for j, (bx, by), ph in (("lhand", BELLY[0], 0.0), ("rhand", BELLY[1], 1.7)):
            p[j] = lerp(p[j], (bx + 13 * math.sin(tt * 40 + ph), by + 9 * math.sin(tt * 33 + ph)), u)
            p[j + "_t"] = "open"
    return p
S.set(T_TK, "stand", "delighted", dur=0.2)
S.hook(tickle_hook)
S.sfx(T_TK + 0.2, "rummage", 0.04, dur=1.7)
S.prop(lambda cr, tt, p, ly: [L.motion_lines(cr, BELLY[0][0] - 50, BELLY[0][1] - 60, -2.3, n=3, length=40, spread=22, sid=k, width=3)
                              for k in (0,)] if ly == "front" and T_TK + 0.3 <= tt < T_TK + 1.9 and int(tt * 8) % 2 == 0 else None)
dblinks += [T_TK + 1.1]
S.set(T_TK + 2.05, "stand", "nervous", dur=0.3, look=(0.5, -0.9))
S.t = T_TK + 2.6
S.walk_to(S.t, -70, 0.6, face="nervous")

# ---------------------------------------------------------------- a feather (POP) under the chin -> it yawns
S.pocket_pull(S.t, "feather", lambda cr, x, y, s, tt, p: O.draw_feather(cr, x, y, s, 0.5, tt, wiggle=feather_wiggle(tt),
                                                                       droop=ramp(tt, T_DROOP, T_DROOP + 0.5)),
              (0, 0), layer="front", narrow_w=0, held=True, offset=(0, -6))
T_FT = S.t
CHIN = (620, 640)          # hand position; the feather angles up to its chin
def feather_wiggle(tt): return 1.0 if T_FT + 0.4 <= tt < T_FT + 2.4 else 0.0
def chin_hook(tt, p, a=T_FT, b=T_FT + 2.6):
    if a <= tt < b:
        u = ramp(tt, a, a + 0.4) * (1 - ramp(tt, b - 0.3, b))
        p["rhand"] = lerp(p["rhand"], (CHIN[0] + 10 * math.sin(tt * 20), CHIN[1] + 6 * math.sin(tt * 27)), u)
        p["relb"] = lerp(p["relb"], (CHIN[0] - 50, CHIN[1] + 170), u)
    return p
S.hook(chin_hook)
S.set(T_FT, "stand", "mischievous", dur=0.3, look=(0.6, -0.8))
T_YAWN = T_FT + 1.0
dk(T_YAWN, 0.4, mouth=1.0, eyes="happy", lid=0.0)
dk(T_YAWN + 1.0, 0.3, mouth=0.0, eyes="normal", lid=0.45)
S.set(T_YAWN + 0.3, "stand", "shocked", dur=0.12, ease="snap", look=(0.6, -0.8))
T_DROOP = T_FT + 2.6
S.set(T_DROOP, "stand", "sad", dur=0.4)
S.objects["feather"]["t_off"] = T_DROOP + 0.9
S.poof(T_DROOP + 0.8, (CHIN[0] - 40, 1060), r=70, sound=False)
S.t = T_DROOP + 1.0

# ---------------------------------------------------------------- its turn: tiny-arm tickle from way over there -> he collapses
S.walk_to(S.t, -260, 1.0, face="nervous")
T_IT = S.t + 0.1
dk(T_IT - 0.6, 0.4, lean=0.0, lid=0.0, look=(-1.0, 0.2), smile=0.3)
dk(T_IT, 0.35, lean=0.5, lid=0.3, smile=0.9, brow=-0.6, arms=1.0)
T_LOL = T_IT + 0.45
S.set(T_LOL, "stand", "laughing", dur=0.12, ease="snap")
S._hop(T_LOL + 0.1, 22)
S.set(T_LOL + 0.6, "crouch", "laughing", dur=0.25)
S.set(T_LOL + 0.9, "sit_floor", "laughing", dur=0.2, ease="back")
S.set(T_LOL + 1.25, "lie_back", "laughing", dur=0.3)
S.sfx(T_LOL + 1.4, "thud", 0.05)
def kick_hook(tt, p, a=T_LOL + 1.5, b=T_LOL + 3.6):
    if a <= tt < b:
        for j, ph in (("lfoot", 0.0), ("rfoot", 1.6)):
            p[j] = (p[j][0] + 10 * math.sin(tt * 15 + ph), p[j][1] - 45 * max(0.0, math.sin(tt * 15 + ph)))
    return p
S.hook(kick_hook)
T_ARMS = T_LOL + 2.2
dk(T_ARMS, 0.3, arms=0.0, lean=0.1, look=(-0.3, 1.0), brow=0.9, smile=0.0, lid=0.0)    # ...looks at its own arms
dk(T_ARMS + 1.0, 0.25, "back", eyes="happy", smile=1.0, blush=0.9, brow=0.5, look=(-1.0, 0.0), arms=0.6)  # WINNER
dk(T_ARMS + 2.0, 0.3, arms=0.0)
S.sfx(T_ARMS + 1.0, "ding", 0.05)

# ---------------------------------------------------------------- loser buys: up, sigh, POP a cone
S.t = T_LOL + 3.7
S.stand(S.t, "embarrassed")
t = S.t
S.set(t, "stand", "embarrassed", dur=0.3, rhand_front=1.0)
S.hook(lambda tt, p, a=t, b=t + 0.9: (p.update(rhand=lerp(p["rhand"], (p["head"][0] + 35, p["head"][1] + 10), ramp(tt, a, a + 0.3) * (1 - ramp(tt, b - 0.25, b))),
                                                rhand_front=1.0) or p) if a <= tt < b else p)
S.set(t + 1.1, "stand", "sad", dur=0.3, look=(0.7, -0.8))
S.t = t + 1.9
S.shrug(S.t, 0.6)
S.walk_to(S.t, -300, 0.45)
dk(S.t - 0.2, 0.4, eyes="normal", lean=-0.3, smile=0.4, blush=0.2, look=(-1.0, 0.3))
S.pocket_pull(S.t, "cone", lambda cr, x, y, s, tt, p: O.draw_cone(cr, x, y, 0.8 * s), (0, 0), layer="front", narrow_w=0,
              held=True, offset=(0, -4))
# offers it. its tiny arms can't reach.
T_OF = S.t
OFFER = (385, 705)
S.set(T_OF, "stand", "hopeful", dur=0.3)
dk(T_OF + 0.3, 0.3, lean=0.0, look=(-1.0, 0.5), arms=1.0, worry=1.0, brow=0.3, smile=-0.3, eyes="normal")
T_FEED = T_OF + 2.0
def offer_hook(tt, p, a=T_OF, b=T_FEED):
    if a <= tt < b + 1.6:
        u = ramp(tt, a, a + 0.4)
        tgt = OFFER if tt < b else lerp(OFFER, (452, 728), ramp(tt, b, b + 0.5))
        p["rhand"] = lerp(p["rhand"], tgt, u); p["relb"] = lerp(p["relb"], (p["neck"][0] + 120, p["neck"][1] + 170), u)
    return p
S.hook(offer_hook)
S.set(T_FEED - 0.3, "stand", "idea", dur=0.15, ease="back")
S.xkeys.append((T_FEED, -255, 0.4)); S.x = -255
dk(T_FEED + 0.15, 0.4, lean=0.45, arms=0.0, worry=0.0, smile=0.6, mouth=1.0, look=(-1.0, 0.6))
T_CH = T_FEED + 1.0
dk(T_CH, 0.08, "snap", mouth=0.0)
S.objects["cone"]["t_off"] = T_CH + 0.03
S.sfx(T_CH, "chomp", 0.1); S.sfx(T_CH + 0.8, "gulp", 0.07)
S.prop(lambda cr, tt, p, ly: O.draw_splash(cr, 470, 640, (tt - T_CH) / 0.6, color=(0.93, 0.76, 0.5), n=7, r=120, sid=30, spread=1.4)
       if ly == "front" else None)
S.set(T_CH + 0.05, "stand", "shocked", dur=0.1, ease="snap")
dk(T_CH + 0.8, 0.3, "back", eyes="happy", smile=1.0, blush=0.9, hearts=1.0, lean=0.0, brow=0.4)
# checks his hand -- all there. relief.
t = T_CH + 1.6
S.set(t, "stand", "worried", dur=0.3, look=(0.5, 0.2), rhand_front=1.0)
S.hook(lambda tt, p, a=t, b=t + 1.4: (p.update(rhand=lerp(p["rhand"], (p["head"][0] + 120 + 8 * math.sin(tt * 18), p["head"][1] + 40),
                                                               ramp(tt, a, a + 0.3) * (1 - ramp(tt, b - 0.3, b))),
                                                relb=lerp(p["relb"], (p["head"][0] + 160, p["head"][1] + 230), ramp(tt, a, a + 0.3) * (1 - ramp(tt, b - 0.3, b))),
                                                rhand_t="open", rhand_front=1.0) or p) if a <= tt < b else p)
S.set(t + 0.9, "stand", "happy", dur=0.25, ease="back", blush=0.7)
dk(t + 2.6, 0.4, hearts=0.0, eyes="normal", smile=0.7, blush=0.3, look=(-1.0, 0.2))
dblinks += [t + 3.2]
S.t = t + 1.9
S.walk_to(S.t, -270, 0.4)

# ---------------------------------------------------------------- the ask (his new friend stays)
T_ASK = S.t
dk(T_ASK, 0.4, lean=-0.3, look=(-1.0, 0.4))
S.the_ask(T_ASK, hold=8.0, push=False)
T_HOLD = T_ASK + 6.9
dk(T_HOLD + 1.0, 0.5, lean=0.2, look=(-1.0, 0.8), smile=0.8)                 # leans in to read his sign
dk(T_HOLD + 5.0, 0.3, arms=0.7, blush=0.6); dk(T_HOLD + 6.2, 0.3, arms=0.0)
dblinks += [T_HOLD + 0.4, T_HOLD + 3.1, T_HOLD + 6.8]

# ---------------------------------------------------------------- draw the dino (behind him)
DT = Track(dkeys)
def dino(cr, tt, p, ly):
    if ly != "back": return
    st = dict(DT.at(tt)); st["x"] = dino_x(tt)
    st["walk"] = math.pi / 2 + (DX0 - st["x"]) / STEP * math.pi
    if st["x"] > 1450: return
    bl = max([1 - abs(tt - b - 0.08) / 0.08 for b in dblinks if 0 <= tt - b < 0.16] + [0.0])
    O.draw_dino(cr, st, tt, blink=bl)
S.prop(dino)
S.props.remove(dino); S.props.insert(0, dino)          # dino first: held props + his hands draw over it

if __name__ == "__main__":
    S.render("ltcd_test3_dino_tickle.mp4")
