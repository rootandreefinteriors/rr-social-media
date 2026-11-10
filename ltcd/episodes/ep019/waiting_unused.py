"""Day 19 -- WAITING episode (no qualifying comment on day 18: the only new comment names a real celebrity, so it
can't be pinned on screen -- see LOG.md). The message is the star.

He is still where day 18 left him: at home, inside. The couch is back; she sits on it holding the sleeping baby, the
black kitten curled up next to her. He stands in front of the couch holding the sign up to us: TELL ME WHAT TO DO NEXT
IN THE COMMENTS. Dead stare, breathing, the odd blink, eyes flick down to the sign once. The only beat: he turns the
sign to himself, writes "WE'LL WAIT.", turns it back and keeps staring. Slow blink. Hard cut. ~21 s.
Copied from tests/waiting_ref; only the place + line changed.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import moves as M
import ltcd as L
import objects as O
from ltcd import FLOOR_Y
from ink import sketch_line

# his house, inside, exactly as day 18 left it (see ep018/episode.py)
IX = 1300000.0
TVX = IX + 650.0; CLOCK = (IX - 150.0, 560.0); OUTLET = (IX + 1010.0, FLOOR_Y - 230.0)
SINKX = IX + 1240.0; FRIDGEX = IX + 1600.0; DOORX = IX - 900.0; COUCHX = IX - 150.0
SEAT_L = COUCHX - 175.0
HE = IX + 230.0                                     # where he stands (his centre)
G_HAIR, G_DRESS = (0.62, 0.28, 0.16), (0.30, 0.66, 0.66)
GS = 0.92

L.POSES["couch_sit"] = dict(head=(540, 752), neck=(540, 878), hip=(540, 1228), lknee=(400, 1300), rknee=(680, 1300),
    lfoot=(430, FLOOR_Y), rfoot=(650, FLOOR_Y), lelb=(465, 1075), lhand=(462, 1200), relb=(615, 1075), rhand=(618, 1200),
    lfoot_dir=-0.5, rfoot_dir=0.5, nowalk=1.0)
L.POSES["g_sit_hold"] = dict(L.POSES["couch_sit"], head=(540, 740), neck=(540, 862), hip=(540, 1205), lelb=(470, 1030),
    lhand=(480, 1100), relb=(610, 1030), rhand=(600, 1100), lhand_t="grip", rhand_t="grip")

S = M.Scene(x0=HE - 540)
S.floor = False

def room(cr, t):
    O.draw_room(cr, t, IX - 3000, IX + 3000, door_x=DOORX, door_open=0.0, frame_x=IX - 450, frame_fall=0.0,
                kitchen_x=IX + 1000)
    O.draw_wall_clock(cr, *CLOCK, hour=7.0, minute=20.0 + t / 60.0)
    O.draw_outlet(cr, *OUTLET)
    sketch_line(cr, [(TVX + 280, FLOOR_Y - 330), (OUTLET[0] - 10, FLOOR_Y - 250), (OUTLET[0], OUTLET[1])], 5, sid=20200, amp=0.4)
    O.draw_tv(cr, TVX, FLOOR_Y - 10, t, screen="off")
    O.draw_sink_counter(cr, SINKX, FLOOR_Y - 10, n=25, t=t)
    O.draw_fridge(cr, FRIDGEX, FLOOR_Y - 10, photo=1.0)
S.background(room)

def her_blink(t):
    import math
    for b in (3.1, 8.4, 13.2, 17.0):
        if b <= t < b + 0.16: return math.sin(math.pi * (t - b) / 0.16)
    return 0.0
def her_pose(t):
    p = L.pose("g_sit_hold", "happy", turn=0.3, look=(0.5, 0.5), smile=0.5)
    ox = SEAT_L - 540
    for j in L.JOINTS: p[j] = (p[j][0] + ox, p[j][1])
    return L.constrain(p)
def scale_pt(p, pt):
    fx = (p["lfoot"][0] + p["rfoot"][0]) / 2
    return (fx + (pt[0] - fx) * GS, FLOOR_Y + (pt[1] - FLOOR_Y) * GS)

def family(cr, t, p, ly):
    """the couch, her with the sleeping baby, the kitten curled up next to her (background only, nothing happens)."""
    if ly != "back": return
    O.draw_couch(cr, COUCHX, FLOOR_Y - 10)
    O.draw_cat(cr, COUCHX + 60, FLOOR_Y - 10 - O.BENCH_SEAT + 4, s=0.85, t=t, kind="loaf", col="black",
               look=(0.3, 0.2), blink=0.6, sid=2000, swish=0.3)
    q = her_pose(t)
    O.draw_mom(cr, t, q, her_blink(t), s=GS, hair=G_HAIR, dress=G_DRESS, bun=False)
    hc = scale_pt(q, ((q["lhand"][0] + q["rhand"][0]) / 2, (q["lhand"][1] + q["rhand"][1]) / 2))
    O.draw_baby(cr, hc[0] + 10, hc[1] - 15, 0.0, dict(eyes="sleep"), t, s=0.8)
    fx = (q["lfoot"][0] + q["rfoot"][0]) / 2
    cr.save(); cr.translate(fx, FLOOR_Y); cr.scale(GS, GS); cr.translate(-fx, -FLOOR_Y); L.draw_grips(cr, q); cr.restore()
S.prop(family)

S.auto_blinks = False
S.blink(2.4, 9.9, 14.6)
S.hold_sign(0.0, 21.0, extra="WE'LL WAIT.", write_at=6.6, push=False)
S.camera(0.0, IX - 20, 1000, 0.98, 0.0)                                   # wide enough for the family on the couch
S.camera(0.5, IX - 5, 1010, 1.05, 20.0)                                 # slow creep in
S.set(4.0, "hold_front", "dead_stare", dur=0.12, look=(0.0, 0.85))       # eyes flick down to the sign...
S.set(4.7, "hold_front", "dead_stare", dur=0.12, look=(0.0, 0.0))        # ...and back to us
S.set(18.2, "hold_front", "dead_stare", dur=0.3, lid=1.0)                # one slow blink
S.set(18.65, "hold_front", "dead_stare", dur=0.35)

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        S.build()
        import cairo
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, L.W, L.H)
        for a in sys.argv[2:]:
            tt = float(a); L.render_frame(tt, surf); surf.write_to_png(f"still_{tt:05.2f}.png")
    else:
        S.render("day019.mp4")
