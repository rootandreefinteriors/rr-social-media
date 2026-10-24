"""TEST 1 (not posted) — top comment: "bathe in a tub of spicy ramen".

Reads the comment, digs at his hip and POPs out a clawfoot tub of spicy ramen. Toe-dip: way too spicy (face flushes,
steam, hops). Looks at the comment again... determined. Cannonball. Shock -> melts into it. Slurps a noodle. Sinks to
eye level, then all the way under (just his hair curl sticking out, bubbles), pops back up wearing a noodle. Thumbs up.
Climbs out dripping, shakes off like a dog, notices the noodle, shrugs, keeps it. The ask (noodle still on).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import Track, ramp, pulse, lerp, FLOOR_Y

TS = 0.95                               # tub scale
TX = 740                                # tub centre (world x)
G = O.tub_geom(TX, FLOOR_Y, TS); RIM = G["rim_y"]
IN = TX - 540                           # his body offset when he is in the tub

# --- tub poses (around x=540; the tub wall hides everything below the rim)
L.POSES["tub_sit"] = dict(head=(540, 885), neck=(540, 1010), hip=(540, 1350), lelb=(425, 1088), lhand=(338, 1196),
                          relb=(655, 1088), rhand=(742, 1196), lknee=(470, 1300), lfoot=(440, 1420), rknee=(610, 1300),
                          rfoot=(640, 1420), lfoot_dir=-0.5, rfoot_dir=0.5)
L.POSES["tub_relax"] = dict(L.POSES["tub_sit"], head=(518, 900), neck=(534, 1022), tilt=-0.13, lelb=(420, 1095),
                            lhand=(330, 1192), relb=(660, 1092), rhand=(748, 1192))
L.POSES["tub_thumb"] = dict(L.POSES["tub_sit"], relb=(690, 1060), rhand=(735, 930), rhand_t="thumbs")
L.POSES["tub_peek"] = dict(head=(540, 1222), neck=(540, 1300), hip=(540, 1400), lelb=(480, 1330), lhand=(470, 1380),
                           relb=(600, 1330), rhand=(610, 1380), lknee=(500, 1400), lfoot=(470, 1425), rknee=(580, 1400),
                           rfoot=(610, 1425))
L.POSES["tub_under"] = dict(L.POSES["tub_peek"], head=(540, 1322), neck=(540, 1385), hip=(540, 1415))
L.POSES["toe_dip"] = dict(hip=(545, 1118), lknee=(525, 1300), lfoot=(520, FLOOR_Y), rknee=(625, 1060), rfoot=(650, 1212),
                          lelb=(440, 900), lhand=(360, 860), relb=(650, 905), rhand=(740, 850), lhand_t="open",
                          rhand_t="open", tilt=-0.08, rfoot_dir=0.8, lfoot_dir=-0.3)
L.POSES["toe_yank"] = dict(L.POSES["toe_dip"], rknee=(610, 1010), rfoot=(600, 1150), relb=(660, 820), rhand=(720, 700),
                           lelb=(430, 820), lhand=(360, 720))

S = M.Scene()
S.card("noodle.gremlin", "bathe in a tub of spicy ramen", "2.4K", t0=0.3)
S.sfx(0.3, "tick", 0.06)

# --- reads it, delighted
S.read_card(0.6, react="delighted", lines=2)
S.hop(S.t, n=2, h=16, gap=0.32)
S.walk_to(S.t + 0.1, -230, 0.95)

# --- digs at his hip: POP, the tub
t_pull = S.t + 0.05
def tub_ripple(t):
    if T_DIP <= t < T_DIP + 0.9: return (t - T_DIP) / 0.9
    if T_LAND <= t < T_LAND + 1.1: return (t - T_LAND) / 1.1
    return 0.0
def tub_back(cr, x, yb, s, t, p): O.draw_tub(cr, x, yb, TS * s, t, "back", steam=1.0)
def tub_front(cr, x, yb, s, t, p):
    rx = -185 if t < T_LAND else 0.0
    O.draw_tub(cr, x, yb, TS * s, t, "front", ripple=tub_ripple(t), ripple_x=rx)
S.pocket_pull(t_pull, "tub_front", tub_front, (TX, FLOOR_Y), layer="front", narrow_w=0)
T_POP = t_pull + 2.1
S.place("tub_back", tub_back, (TX, FLOOR_Y), t_on=T_POP, layer="back", pop=True)

# --- ooh. rubs his hands.
t = S.t
S.set(t, "stand", "starstruck", dur=0.25, ease="back", look=(1.0, 0.35))
S.set(t + 1.0, "clap", "mischievous", dur=0.25, look=(0.9, 0.3))
S.hook(lambda tt, p, a=t + 1.1, b=t + 2.0: (p.update(lhand=(p["lhand"][0] + 10 * math.sin(tt * 30), p["lhand"][1]),
                                                     rhand=(p["rhand"][0] - 10 * math.sin(tt * 30), p["rhand"][1])) or p) if a <= tt < b else p)
S.set(t + 2.1, "stand", "eager", dur=0.25)
S.t = t + 2.3
S.walk_to(S.t, -100, 0.7)

# --- toe dip -> SPICY
t = S.t
S.set(t, "toe_dip", "concentrating", dur=0.45, look=(0.8, 0.85))
T_DIP = t + 0.5
S.sfx(T_DIP + 0.05, "bubble", 0.06)
S.set(T_DIP + 0.45, "toe_yank", "shocked", dur=0.1, ease="snap", eyescale=1.2)
S.set(T_DIP + 0.55, "toe_yank", "shocked", dur=0.1, face_tint=1.0, fx_steam=1.0, eyescale=1.2, clear=False)
for k in range(3): S._hop(T_DIP + 0.75 + k * 0.3, 26, 0.09)
S.set(T_DIP + 1.65, "stand", "hot", dur=0.3, face_tint=1.0, fx_steam=1.0, sweat=1.0)
S.hook(lambda tt, p, a=T_DIP + 1.9, b=T_DIP + 3.0: (p.update(rhand=(p["head"][0] + 70 + 22 * math.sin(tt * 26), p["head"][1] + 130),
                                                             relb=(p["head"][0] + 140, p["head"][1] + 300), rhand_t="open", rhand_front=1.0) or p) if a <= tt < b else p)
S.t = T_DIP + 3.1

# --- looks at the comment again. ...the comments decide. Determined.
t = S.t
S.set(t, "stand", "worried", dur=0.3, look=(0.7, -0.85), face_tint=0.6)
S.set(t + 1.0, "stand", "determined", dur=0.25, ease="back", face_tint=0.4)
S.nod(t + 1.3, 1)
S.t = t + 1.9

# --- cannonball
t = S.t
S.set(t, "crouch", "determined", dur=0.2)
S.set(t + 0.22, "cannonball", "delighted", dur=0.12, ease="snap")
S.xkeys.append((t + 0.25, IN, 0.55)); S.x = IN
S._hop(t + 0.52, 175, 0.2)
T_LAND = t + 0.82
S.set(T_LAND, "tub_sit", "shocked", dur=0.12, ease="snap", eyescale=1.2, face_tint=1.0, fx_steam=1.0, nowalk=1.0)
S.sfx(T_LAND, "splat", 0.14)
S.prop(lambda cr, tt, p, ly: O.draw_splash(cr, TX, RIM + 10, (tt - T_LAND) / 0.8, n=14, r=260, sid=40, floor_y=RIM + 5) if ly == "front" else None)
S.set(T_LAND + 0.35, "tub_sit", "shocked", dur=0.2, eyescale=1.2, face_tint=1.0, fx_steam=1.0, shiver=0.8)

# --- ...melts into it
t = T_LAND + 1.5
S.set(t, "tub_relax", "happy", dur=0.8, eyes="happy", smile=0.9, face_tint=0.85, fx_steam=0.7, blush=0.6)

# --- slurp
T_SL = t + 2.2
S.set(T_SL, "tub_sit", "neutral", dur=0.3, mouth="o", open=0.25, look=(0.5, 0.85), face_tint=0.85, fx_steam=0.7)
S.sfx(T_SL + 0.3, "slurp", 0.12, dur=1.1)
S.sfx(T_SL + 1.5, "gulp", 0.08)
def slurp(cr, tt, p, ly):
    if ly != "front" or not (T_SL + 0.25 <= tt < T_SL + 1.45): return
    u = ramp(tt, T_SL + 0.3, T_SL + 1.4)
    hx, hy = p["head"]; mth = (hx + 8, hy + 62)
    base = (TX + 70, RIM + 14)
    a = lerp(base, mth, u)
    pts = []
    for i in range(16):
        v = i / 15
        q = lerp(a, mth, v)
        pts.append((q[0] + 16 * math.sin(v * 9 + tt * 14) * (1 - v), q[1]))
    O._noodle(cr, pts, sid=700)
S.prop(slurp)
S.set(T_SL + 1.6, "tub_sit", "delighted", dur=0.2, ease="back", face_tint=1.0, fx_steam=1.0, teary=0.8, sweat=0.8)

# --- sinks to eye level... looks around... all the way under (just the curl)... POPS up wearing a noodle
t = T_SL + 2.9
S.set(t, "tub_peek", "neutral", dur=0.55, ease="inn", look=(-0.8, 0.0), face_tint=0.8, smile=0.0)
S.look(t + 0.9, (0.8, 0.0), 0.25); S.look(t + 1.4, (0.0, 0.0), 0.2)
S.set(t + 1.9, "tub_under", "neutral", dur=0.35, ease="inn", face_tint=0.8)
for k in range(3): S.sfx(t + 2.4 + k * 0.33, "bubble", 0.05)
S.prop(lambda cr, tt, p, ly, a=t + 2.2, b=t + 3.5: O.draw_bubbles(cr, tt, TX, RIM + 4, n=5, spread=40, rise=170, size=9, seed=2)
       if ly == "back" and a <= tt < b else None)
T_UP = t + 3.6
S.set(T_UP, "tub_sit", "surprised", dur=0.18, ease="back", face_tint=0.9, fx_steam=0.6)
S.sfx(T_UP, "splat", 0.07)
S.prop(lambda cr, tt, p, ly: O.draw_splash(cr, TX, RIM + 10, (tt - T_UP) / 0.7, n=8, r=170, sid=60, floor_y=RIM + 5) if ly == "front" else None)
S.place("noodle", lambda cr, x, y, s, tt, p: O.draw_noodle_hat(cr, p), (0, 0), t_on=T_UP + 0.04, layer="front")
S.set(T_UP + 0.7, "tub_thumb", "proud", dur=0.3, ease="back", face_tint=0.9, fx_steam=0.6)

# --- climbs out, drips, shakes off like a dog
t = T_UP + 2.3
S.set(t, "crouch", "eager", dur=0.18)
S.set(t + 0.2, "cannonball", "happy", dur=0.12, ease="snap")
S.xkeys.append((t + 0.22, -170, 0.6)); S.x = -170
S._hop(t + 0.5, 175, 0.2)
S.set(t + 0.82, "crouch", "happy", dur=0.1, ease="snap", nowalk=1.0); S.sfx(t + 0.84, "thud", 0.06)
S.set(t + 1.0, "stand", "happy", dur=0.3, ease="back")
T_OUT = t + 0.85
S.prop(lambda cr, tt, p, ly: O.draw_drips(cr, p, tt, T_OUT, 3.2) if ly == "front" else None)
T_SH = t + 1.5
S.set(T_SH, "stand", "laughing", dur=0.15, shiver=3.0, laugh=0.0, tears=0.0)
S.sfx(T_SH, "rummage", 0.05, dur=0.7)
S.prop(lambda cr, tt, p, ly: O.draw_splash(cr, p["hip"][0], p["neck"][1] + 80, (tt - T_SH - 0.1) / 0.8, n=16, r=300, sid=80, spread=1.9, floor_y=FLOOR_Y)
       if ly == "front" else None)
S.set(T_SH + 0.8, "stand", "happy", dur=0.25)

# --- notices the noodle. shrugs. keeps it.
t = T_SH + 1.4
S.set(t, "stand", "surprised", dur=0.25, look=(0.0, -1.0), eyescale=1.08)
S.blink(t + 0.55)
S.shrug(t + 0.9, 0.8)
S.t += 0.1

# lingering spice: a faint flush + wisp of steam for the rest of the episode
S.hook(lambda tt, p: (p.update(face_tint=max(p.get("face_tint", 0), 0.45 - 0.2 * ramp(tt, T_OUT + 3, T_OUT + 15)),
                               fx_steam=max(p.get("fx_steam", 0), 0.25 * (1 - ramp(tt, T_OUT + 6, T_OUT + 10)))) or p) if tt >= T_UP + 2.3 else p)

S.the_ask(S.t, hold=9.0)

if __name__ == "__main__":
    S.render("ltcd_test1_ramen.mp4")
