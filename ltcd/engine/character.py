"""character — the LTCD guy.

A basic stick figure with a LOT of face: big cartoon eyes (pupils, shine, lids), thick brows, a mouth with many
shapes, one bouncy hair curl, rubber-hose limbs, mitten hands with gestures, bean feet, cartoon symbols.
Personality: eager, earnest, hopeful, a little shy — he really wants you to tell him what to do.

A pose is a plain dict (see BASE). Build one with:
    pose("wave", "shy", look=(0.2, 0))          # body pose + expression + overrides
    P(**overrides)                               # from BASE
Libraries: POSES (body), EXPR (face), HANDS (gesture names), EYES (eye styles), MOUTHS (mouth styles), FX (symbols).
"""
import math, random
import ink
from ink import (INK, PAPER, WHITE, FLOOR_Y, wob, path, circle_pts, bez, sketch_pts, stroke_ink, fill_paper,
                 fill_ink, sketch_line, sketch_circle, ellipse, sketch_ellipse, draw_text, lerp, smooth, clamp01)

HEAD_R = 118

BASE = dict(
    # skeleton, world coords, standing front-on at x=540. "l" = screen-left side.
    head=(540, 640), neck=(540, 768), hip=(540, 1118),
    lelb=(468, 960), lhand=(452, 1105), relb=(612, 960), rhand=(628, 1105),
    lknee=(512, 1300), lfoot=(498, FLOOR_Y), rknee=(568, 1300), rfoot=(582, FLOOR_Y),
    # body
    tilt=0.0,          # head roll (rad)
    lean=0.0,          # whole body rotates around the feet (rad)
    stretch=0.0,       # -1 squash .. +1 stretch (around the feet)
    hop=0.0,           # px off the ground
    turn=0.0,          # head turn: 0 front, +-1 three-quarter, +-1.5 profile (+ = facing screen right)
    back=0.0,          # 1 = we see the back of his head (no face)
    show=1.0, curl=0.0, swing=1.0,
    lhand_t="mitt", rhand_t="mitt",           # HANDS
    lhand_front=0.0, rhand_front=0.0,         # 1 = that arm is drawn over his head (facepalm, scratch head...)
    lfoot_dir=-0.5, rfoot_dir=0.5, tiptoe=0.0,
    # face
    look=(0.0, 0.0),   # pupils -1..1
    eyes="normal",     # EYES
    lid=0.0, lid_slant=0.0, lower_lid=0.0,    # upper lid 0..1, slant + angry / - sad, lower lid 0..1
    pupil=1.0, eyescale=1.0, shine=0.0, teary=0.0, skeptic=0.0,
    brow=0.0, worry=0.0,                      # brow + raised; worry + inner ends up (hopeful/sad) - down (cross)
    mouth="auto", smile=0.3, open=0.0, mouth_w=1.0, tongue=0.0,
    blush=0.0, tears=0.0, sweat=0.0, vein=0.0, gloom=0.0, squash=0.0,
    # cartoon symbols around the head, 0..1
    fx_q=0.0, fx_ex=0.0, fx_zzz=0.0, fx_hearts=0.0, fx_stars=0.0, fx_bulb=0.0, fx_steam=0.0, fx_nervous=0.0,
    fx_notes=0.0, fx_sparkle=0.0, fx_swirl=0.0,
    # procedural cycles, 0..1 (animated by the engine)
    shiver=0.0, laugh=0.0, sob=0.0, dance=0.0, sleep=0.0, sneak=0.0, fidget=0.0, run=0.0,
)
def P(base=BASE, **kw):
    d = dict(base); d.update(kw); return d

HANDS = ["mitt", "fist", "open", "point", "poke", "thumbs", "peace", "grab", "flat", "grip", "none"]
EYES = ["normal", "happy", "closed", "x", "spiral", "heart", "star", "dot", "wide"]
MOUTHS = ["auto", "grin", "teeth", "o", "wavy", "blep", "yawn", "scream", "kiss", "smirk", "wail", "cat", "flat"]
FX = ["fx_q", "fx_ex", "fx_zzz", "fx_hearts", "fx_stars", "fx_bulb", "fx_steam", "fx_nervous", "fx_notes", "fx_sparkle", "fx_swirl"]

# ------------------------------------------------------------ expressions ---
EXPR = {
    "neutral":      dict(smile=0.2),
    "happy":        dict(smile=0.7, brow=0.2),
    "eager":        dict(smile=0.9, open=0.5, brow=0.5, pupil=1.15),
    "delighted":    dict(eyes="happy", mouth="grin", smile=1.0, open=0.8, brow=0.6, blush=0.4),
    "laughing":     dict(eyes="happy", mouth="grin", smile=1.0, open=1.0, brow=0.5, laugh=1.0, tears=0.25),
    "hopeful":      dict(smile=0.35, brow=0.6, worry=0.8, pupil=1.4, shine=0.6, look=(0, -0.1)),
    "pleading":     dict(smile=-0.1, brow=0.7, worry=1.0, pupil=1.6, shine=1.0, teary=0.6, look=(0, -0.15)),
    "shy":          dict(smile=0.5, brow=0.3, worry=0.6, blush=1.0, look=(-0.6, 0.4)),
    "embarrassed":  dict(mouth="wavy", smile=0.2, brow=0.4, worry=0.8, blush=1.0, sweat=0.7, look=(-0.6, 0.3)),
    "surprised":    dict(mouth="o", open=0.6, brow=1.0, pupil=0.75, eyescale=1.12),
    "shocked":      dict(eyes="dot", mouth="scream", open=1.0, brow=1.2, eyescale=1.2, fx_ex=1.0),
    "scared":       dict(mouth="teeth", brow=1.0, worry=1.0, pupil=0.6, eyescale=1.15, sweat=1.0, shiver=1.0, fx_nervous=1.0),
    "nervous":      dict(mouth="wavy", smile=0.0, brow=0.5, worry=0.9, sweat=0.8, look=(0.4, 0.1), fx_nervous=0.8),
    "worried":      dict(smile=-0.35, brow=0.4, worry=1.0, look=(0, 0.2)),
    "sad":          dict(smile=-0.6, brow=0.2, worry=1.0, pupil=1.2, teary=0.5, look=(0, 0.45), lid=0.2, lid_slant=-0.5),
    "crying":       dict(mouth="wail", open=0.7, smile=-0.8, brow=0.3, worry=1.0, eyes="closed", tears=1.0, sob=1.0),
    "angry":        dict(smile=-0.5, brow=-0.7, worry=-1.0, lid=0.25, lid_slant=1.0, vein=0.8),
    "furious":      dict(mouth="teeth", brow=-1.0, worry=-1.2, lid=0.3, lid_slant=1.0, vein=1.0, fx_steam=1.0, pupil=0.7),
    "impatient":    dict(smile=-0.45, brow=-0.5, worry=-0.8, lid=0.45, lid_slant=0.4, look=(0.6, 0.0)),
    "annoyed":      dict(mouth="flat", brow=-0.3, worry=-0.4, lid=0.5, look=(0.7, 0.0)),
    "skeptical":    dict(mouth="smirk", smile=-0.2, skeptic=1.0, lid=0.3, look=(0.3, 0)),
    "smug":         dict(mouth="smirk", smile=0.6, lid=0.45, lid_slant=0.3, brow=0.2, skeptic=0.4),
    "confused":     dict(mouth="wavy", smile=0.0, skeptic=0.8, brow=0.3, look=(0.5, -0.4), fx_q=1.0, tilt=0.15),
    "thinking":     dict(mouth="flat", smile=0.0, brow=0.2, worry=-0.2, look=(0.6, -0.7), lid=0.15, skeptic=0.3),
    "concentrating": dict(smile=-0.1, tongue=1.0, brow=-0.4, worry=-0.2, look=(0.4, 0.75), lid=0.25),
    "idea":         dict(smile=0.8, open=0.4, brow=1.0, pupil=0.9, eyescale=1.1, fx_bulb=1.0),
    "determined":   dict(mouth="teeth", smile=0.2, brow=-0.6, worry=-0.6, lid=0.2, lid_slant=0.5, fx_sparkle=0.4),
    "proud":        dict(eyes="happy", smile=0.8, brow=0.4, fx_sparkle=0.8, tilt=-0.08),
    "sleepy":       dict(smile=0.0, brow=-0.2, worry=0.3, lid=0.75),
    "asleep":       dict(eyes="closed", mouth="o", open=0.25, sleep=1.0, fx_zzz=1.0, tilt=0.18),
    "yawning":      dict(eyes="closed", mouth="yawn", open=1.0, brow=0.5),
    "bored":        dict(mouth="flat", lid=0.6, brow=-0.1, look=(0.5, 0.3)),
    "disgusted":    dict(mouth="blep", brow=-0.4, worry=0.4, lid=0.4, lower_lid=0.3, look=(-0.4, 0.2), skeptic=0.3),
    "dizzy":        dict(eyes="spiral", mouth="wavy", fx_stars=1.0, tilt=0.12),
    "knocked_out":  dict(eyes="x", mouth="wavy", open=0.0, fx_stars=1.0, tilt=0.25),
    "in_love":      dict(eyes="heart", smile=0.8, blush=1.0, fx_hearts=1.0),
    "starstruck":   dict(eyes="star", mouth="grin", smile=1.0, open=0.7, brow=0.8, fx_sparkle=1.0),
    "mischievous":  dict(mouth="smirk", smile=0.8, lid=0.4, lid_slant=0.6, brow=-0.2, skeptic=0.5, look=(0.5, 0)),
    "cold":         dict(mouth="teeth", brow=0.3, worry=0.8, shiver=1.0, blush=0.5),
    "hot":          dict(mouth="blep", lid=0.4, brow=0.2, worry=0.6, sweat=1.0, fx_steam=0.4),
    "gloomy":       dict(smile=-0.4, lid=0.5, lid_slant=-0.4, gloom=1.0, look=(0, 0.5)),
    "cheeky":       dict(mouth="cat", smile=0.6, lid=0.2, blush=0.4),
    "kiss":         dict(mouth="kiss", eyes="closed", blush=0.8, fx_hearts=0.6),
    "singing":      dict(eyes="closed", mouth="o", open=0.7, brow=0.6, fx_notes=1.0, tilt=-0.1),
}

# -------------------------------------------------------------- body poses ---
POSES = {
    "stand":        dict(),
    "shy":          dict(lelb=(498, 980), lhand=(528, 1090), relb=(582, 980), rhand=(552, 1090), lhand_t="fist", rhand_t="fist",
                         lfoot_dir=0.35, rfoot_dir=-0.35, tilt=0.07),
    "wave":         dict(relb=(668, 760), rhand=(700, 620), rhand_t="open"),
    "wave_left":    dict(lelb=(412, 760), lhand=(380, 620), lhand_t="open"),
    "point_up":     dict(relb=(648, 720), rhand=(660, 535), rhand_t="point"),
    "point_right":  dict(relb=(700, 860), rhand=(830, 840), rhand_t="point"),
    "point_left":   dict(lelb=(380, 860), lhand=(250, 840), lhand_t="point"),
    "point_cam":    dict(relb=(650, 900), rhand=(610, 880), rhand_t="poke"),
    "shrug":        dict(neck=(540, 758), lelb=(430, 905), lhand=(372, 830), relb=(650, 905), rhand=(708, 830),
                         lhand_t="open", rhand_t="open", tilt=0.12),
    "hands_hips":   dict(lelb=(402, 955), lhand=(482, 1096), relb=(678, 955), rhand=(598, 1096), lhand_t="fist", rhand_t="fist"),
    "arms_crossed": dict(lelb=(470, 1000), lhand=(605, 935), relb=(610, 1000), rhand=(475, 935)),
    "think":        dict(relb=(650, 905), rhand=(566, 772), rhand_t="fist", lelb=(475, 1005), lhand=(608, 968), tilt=0.08),
    "facepalm":     dict(relb=(650, 860), rhand=(552, 640), rhand_t="open", rhand_front=1.0, tilt=0.12, lean=0.02),
    "scratch_head": dict(relb=(690, 650), rhand=(615, 535), rhand_t="open", rhand_front=1.0, tilt=0.12),
    "thumbs_up":    dict(relb=(655, 905), rhand=(690, 800), rhand_t="thumbs"),
    "cheer":        dict(lelb=(430, 660), lhand=(395, 480), relb=(650, 660), rhand=(685, 480), lhand_t="open", rhand_t="open", hop=10),
    "clap":         dict(lelb=(470, 925), lhand=(533, 880), relb=(610, 925), rhand=(547, 880), lhand_t="flat", rhand_t="flat"),
    "cower":        dict(head=(540, 690), neck=(540, 810), hip=(540, 1160), lelb=(430, 770), lhand=(498, 650), relb=(650, 770),
                         rhand=(582, 650), lhand_t="open", rhand_t="open", lhand_front=1.0, rhand_front=1.0,
                         lknee=(482, 1330), rknee=(598, 1330), lfoot_dir=0.3, rfoot_dir=-0.3),
    "hug_self":     dict(lelb=(452, 905), lhand=(602, 858), relb=(628, 905), rhand=(478, 858)),
    "present":      dict(lelb=(420, 960), lhand=(330, 905), relb=(660, 960), rhand=(750, 905), lhand_t="open", rhand_t="open"),
    "bow":          dict(head=(540, 780), neck=(540, 880), lelb=(470, 1010), lhand=(470, 1140), relb=(610, 1010), rhand=(610, 1140)),
    "crouch":       dict(head=(540, 790), neck=(540, 915), hip=(540, 1255), lelb=(462, 1080), lhand=(472, 1240),
                         relb=(618, 1080), rhand=(608, 1240), lknee=(462, 1335), rknee=(618, 1335), lfoot_dir=-0.6, rfoot_dir=0.6),
    "sit_floor":    dict(head=(540, 985), neck=(540, 1108), hip=(540, 1450), lknee=(468, 1325), rknee=(612, 1325),
                         lfoot=(432, FLOOR_Y), rfoot=(648, FLOOR_Y), lelb=(470, 1240), lhand=(470, 1318),
                         relb=(610, 1240), rhand=(610, 1318), lfoot_dir=-0.5, rfoot_dir=0.5),
    "lie_back":     dict(head=(330, 1365), neck=(445, 1395), hip=(760, 1420), lelb=(560, 1350), lhand=(640, 1370),
                         relb=(560, 1440), rhand=(650, 1455), lknee=(860, 1360), rknee=(880, 1400),
                         lfoot=(965, 1430), rfoot=(985, 1460), tilt=-1.45, lfoot_dir=1.0, rfoot_dir=1.0, look=(0.6, 0.0)),
    "jump_tuck":    dict(lknee=(498, 1235), rknee=(582, 1235), lfoot=(505, 1355), rfoot=(575, 1355),
                         lelb=(430, 700), lhand=(400, 560), relb=(650, 700), rhand=(680, 560), lhand_t="open", rhand_t="open"),
    "dance_a":      dict(lelb=(430, 700), lhand=(400, 560), lhand_t="point", relb=(650, 980), rhand=(575, 1090), rhand_t="fist",
                         hip=(560, 1118), lknee=(505, 1300), rknee=(600, 1290), tilt=-0.12),
    "dance_b":      dict(relb=(650, 700), rhand=(680, 560), rhand_t="point", lelb=(430, 980), lhand=(505, 1090), lhand_t="fist",
                         hip=(520, 1118), lknee=(480, 1290), rknee=(575, 1300), tilt=0.12),
    "hold_front":   dict(lelb=(470, 980), lhand=(480, 1010), relb=(610, 980), rhand=(600, 1010), lhand_t="grip", rhand_t="grip"),
    "sneak":        dict(head=(560, 690), neck=(552, 815), hip=(530, 1160), lelb=(560, 900), lhand=(610, 860), relb=(640, 920),
                         rhand=(680, 880), lhand_t="mitt", rhand_t="mitt", lknee=(470, 1290), rknee=(610, 1250),
                         lfoot=(450, FLOOR_Y), rfoot=(640, 1430), tiptoe=1.0, lfoot_dir=0.8, rfoot_dir=0.8, sneak=1.0),
    "fly":          dict(lelb=(450, 650), lhand=(470, 500), relb=(640, 650), rhand=(620, 500), lhand_t="fist", rhand_t="fist",
                         lknee=(520, 1310), rknee=(560, 1310), lfoot=(530, 1460), rfoot=(552, 1455), tiptoe=1.0),
}

def pose(body="stand", face="neutral", **kw):
    d = dict(BASE); d.update(POSES[body]); d.update(EXPR[face]); d.update(kw); return d

# ------------------------------------------------------------- hands/feet ---
def draw_hand(cr, pos, frm, kind, side, sid=0, sc=1.0):
    """cartoon mitten hand at pos; frm = the point the forearm comes from (sets the angle).
    side: -1 screen-left hand, +1 screen-right hand (thumb goes towards the body)."""
    if kind in ("none", "grip"): return
    x, y = pos
    ang = math.atan2(y - frm[1], x - frm[0])
    cr.save(); cr.translate(x, y); cr.rotate(ang); cr.scale(sc, sc)
    th = -side if math.cos(ang) >= 0 else side
    def blob(cx, cy, rx, ry, rot=0.0, s_=0, w=6):
        ellipse(cr, cx, cy, rx, ry, rot, sid=sid + s_); fill_paper(cr); stroke_ink(cr, w)
    if kind == "mitt":
        blob(14, 0, 25, 20); blob(6, th * 19, 11, 8, th * 0.6, 1, 5.5)
    elif kind == "fist":
        blob(12, 0, 21, 19)
        for k in (-1, 0, 1):
            cr.move_to(24, k * 8); cr.line_to(31, k * 8); stroke_ink(cr, 3.5)
    elif kind == "point":
        blob(38, -6, 18, 7, 0, 2, 5.5); blob(10, 0, 19, 17)
    elif kind == "poke":       # pointing straight at the camera: fingertip towards us
        blob(10, 0, 20, 18); sketch_circle(cr, 18, -4, 13, 5.5, sid=sid + 7); cr.arc(18, -4, 4, 0, 6.3); fill_ink(cr)
    elif kind == "thumbs":
        blob(10, 0, 20, 18)
        cr.save(); cr.rotate(-ang); blob(4, -26, 8, 15, 0, 3, 5.5); cr.restore()
    elif kind == "peace":
        blob(34, -12, 17, 6.5, -0.35, 2, 5); blob(34, 10, 17, 6.5, 0.35, 3, 5); blob(8, 0, 19, 17)
    elif kind == "grab":       # open C-shaped grabbing hand
        cr.arc(14, 0, 22, -2.2, 2.2); stroke_ink(cr, 7); blob(-2, th * 18, 9, 7, 0, 1, 5)
    elif kind == "flat":       # flat palm (clapping, chopping, stop!)
        blob(18, 0, 28, 13, 0, 0, 6); blob(4, th * 15, 10, 6, th * 0.8, 1, 5)
    elif kind == "open":
        for k, a in enumerate((-0.8, -0.27, 0.27, 0.8)):
            blob(22 + 20 * math.cos(a), 22 * math.sin(a), 14, 7, a, 3 + k, 5)
        blob(8, 0, 20, 18); blob(2, th * 22, 12, 7, th * 1.1, 1, 5)
    cr.restore()

def draw_foot(cr, pos, d, tiptoe=0.0, sid=0):
    """bean-shaped cartoon foot; d = direction it points (-1 left .. 1 right, 0 at camera)."""
    x, y = pos
    rot = tiptoe * 0.9 * (1 if d >= 0 else -1)
    ellipse(cr, x + 22 * d, y - 13 - tiptoe * 6, 26 + 14 * abs(d), 15, rot=rot, sid=sid, amp=0.02)
    fill_paper(cr); stroke_ink(cr, 6.5)

# ------------------------------------------------------------------- face ---
def thru(a, e, b):
    """bezier control so the limb curve passes THROUGH the elbow/knee e."""
    return (2 * e[0] - (a[0] + b[0]) / 2, 2 * e[1] - (a[1] + b[1]) / 2)

def _proj(x0, turn, rate=0.38):
    """front-view x on the face -> (screen x, foreshortening, visible) for a head turned by `turn`
    (+-1 = three-quarter, +-1.5 = profile). Cartoon rule: in profile the far eye is hidden."""
    Rf = HEAD_R * 0.92
    th = math.asin(max(-0.99, min(0.99, x0 / Rf))) + turn * rate
    vis = math.cos(th) > 0.08 and not (abs(turn) > 1.25 and x0 * turn < 0 and abs(x0) > 20)
    return Rf * math.sin(th), max(0.3, math.cos(th)), vis

def _eye(cr, p, ex, ey, rx, ry, side, blink, t):
    style = p.get("eyes", "normal")
    lid = max(p.get("lid", 0.0), blink)
    if style == "happy":       # ^ ^
        cr.move_to(ex - rx, ey + ry * 0.25); cr.curve_to(ex - rx * 0.5, ey - ry * 0.75, ex + rx * 0.5, ey - ry * 0.75, ex + rx, ey + ry * 0.25)
        stroke_ink(cr, 7); return
    if style == "closed" or lid > 0.97:
        cr.move_to(ex - rx, ey); cr.curve_to(ex - rx * 0.5, ey + ry * 0.55, ex + rx * 0.5, ey + ry * 0.55, ex + rx, ey)
        stroke_ink(cr, 6.5); return
    if style == "x":
        for a in (-1, 1):
            cr.move_to(ex - rx * 0.7, ey - a * ry * 0.6); cr.line_to(ex + rx * 0.7, ey + a * ry * 0.6)
        stroke_ink(cr, 7); return
    if style == "dot":         # tiny shocked dots, no whites
        cr.arc(ex, ey, 7, 0, 6.3); fill_ink(cr); cr.new_path(); return
    # white of the eye
    ellipse(cr, ex, ey, rx, ry, sid=40 + side); fill_paper(cr, WHITE)
    cr.save(); cr.clip_preserve(); cr.new_path()
    lx, ly = p["look"]
    px, py = ex + lx * rx * 0.42, ey + ly * ry * 0.38
    if style == "spiral":
        cr.move_to(ex, ey)
        for k in range(60):
            a = k * 0.35 + t * 6 * side; r = k * rx * 0.016
            cr.line_to(ex + r * math.cos(a), ey + r * math.sin(a) * ry / rx)
        stroke_ink(cr, 4)
    elif style == "heart":
        s = rx * 0.75
        cr.move_to(ex, ey + s * 0.9); cr.curve_to(ex - s * 1.6, ey - s * 0.2, ex - s * 0.5, ey - s * 1.3, ex, ey - s * 0.35)
        cr.curve_to(ex + s * 0.5, ey - s * 1.3, ex + s * 1.6, ey - s * 0.2, ex, ey + s * 0.9); fill_ink(cr); cr.new_path()
    elif style == "star":
        s = rx * 0.85; cr.move_to(ex, ey - s)
        for k in range(1, 10):
            a = -math.pi / 2 + k * math.pi / 5; r = s if k % 2 == 0 else s * 0.42
            cr.line_to(ex + r * math.cos(a), ey + r * math.sin(a))
        cr.close_path(); fill_ink(cr); cr.new_path()
    else:
        pr = 12.5 * p.get("pupil", 1.0) * p.get("eyescale", 1.0)
        if style == "wide": pr *= 0.6
        cr.arc(px, py, pr, 0, 2 * math.pi); fill_ink(cr); cr.new_path()
        sh = p.get("shine", 0.0)
        cr.arc(px - pr * 0.35, py - pr * 0.4, pr * (0.32 + 0.18 * sh), 0, 2 * math.pi); fill_paper(cr, WHITE); cr.new_path()
        if sh > 0.05:
            cr.arc(px + pr * 0.4, py + pr * 0.38, pr * 0.15 * sh + 1, 0, 2 * math.pi); fill_paper(cr, WHITE); cr.new_path()
    tr = p.get("teary", 0.0)
    if tr > 0.05:              # welling water line
        yw = ey + ry * (0.75 - 0.35 * tr)
        cr.move_to(ex - rx, yw)
        for k in range(9):
            cr.line_to(ex - rx + k * rx / 4, yw + 3 * math.sin(k * 1.4 + t * 8))
        cr.line_to(ex + rx, ey + ry); cr.line_to(ex - rx, ey + ry); cr.close_path()
        fill_paper(cr, (0.92, 0.95, 1.0), 0.9 * tr); stroke_ink(cr, 2.5, alpha=tr); cr.new_path()
    # lids
    sl = p.get("lid_slant", 0.0) * side * -1   # + angry: inner end lower
    if lid > 0.01:
        yl = ey - ry + 2 * ry * min(lid, 0.98)
        yi, yo = yl + sl * ry * 0.35, yl - sl * ry * 0.35   # inner (towards nose) / outer
        xi, xo = ex - side * (rx + 6), ex + side * (rx + 6)
        cr.move_to(xi, ey - ry - 6); cr.line_to(xi, yi); cr.line_to(xo, yo); cr.line_to(xo, ey - ry - 6); cr.close_path()
        fill_paper(cr); cr.new_path()
        cr.move_to(xi, yi); cr.line_to(xo, yo); stroke_ink(cr, 5.5)
    ll = p.get("lower_lid", 0.0)
    if ll > 0.01:
        yb = ey + ry - 2 * ry * ll * 0.6
        cr.move_to(ex - rx - 6, ey + ry + 6); cr.line_to(ex - rx - 6, yb); cr.curve_to(ex - rx * 0.3, yb - 6, ex + rx * 0.3, yb - 6, ex + rx + 6, yb)
        cr.line_to(ex + rx + 6, ey + ry + 6); cr.close_path(); fill_paper(cr); cr.new_path()
        cr.move_to(ex - rx, yb); cr.curve_to(ex - rx * 0.3, yb - 6, ex + rx * 0.3, yb - 6, ex + rx, yb); stroke_ink(cr, 4.5)
    cr.restore()
    ellipse(cr, ex, ey, rx, ry, sid=40 + side); stroke_ink(cr, 5.5)

def _mouth(cr, p, mx, my, sx, t):
    style = p.get("mouth", "auto")
    sm, op = p.get("smile", 0.0), p.get("open", 0.0)
    wdt = (52 + 12 * abs(sm)) * p.get("mouth_w", 1.0) * sx
    def open_shape(top, depth, curve):
        cr.move_to(mx - wdt / 2, top)
        cr.curve_to(mx - wdt / 4, top + curve, mx + wdt / 4, top + curve, mx + wdt / 2, top)
        cr.curve_to(mx + wdt / 2, top + depth, mx - wdt / 2, top + depth, mx - wdt / 2, top); cr.close_path()
    def tongue_in(top, depth):
        cr.save(); open_shape(top, depth, sm * 8); cr.clip()
        ellipse(cr, mx + 4 * sx, top + depth * 0.82, wdt * 0.32, depth * 0.3 + 3, sid=60); fill_paper(cr, (0.92, 0.92, 0.92)); stroke_ink(cr, 3)
        cr.restore()
    if style == "auto":
        if op > 0.05:
            top = my - 4 - sm * 6; d = 50 * op
            open_shape(top, d, sm * 8); fill_ink(cr); cr.new_path()
            if op > 0.35: tongue_in(top, d)
            open_shape(top, d, sm * 8); stroke_ink(cr, 5)
        else:
            cr.move_to(mx - wdt / 2, my - sm * 3)
            cr.curve_to(mx - wdt / 5, my + sm * 22, mx + wdt / 5, my + sm * 22, mx + wdt / 2, my - sm * 3); stroke_ink(cr, 6.5)
    elif style == "grin":      # big open smile with a row of top teeth
        wdt *= 1.35; top = my - 10; d = 46 * max(0.4, op)
        open_shape(top, d, 6); fill_ink(cr); cr.new_path()
        cr.save(); open_shape(top, d, 6); cr.clip()
        cr.rectangle(mx - wdt / 2, top - 4, wdt, 14); fill_paper(cr, WHITE); cr.new_path()
        tongue_in(top, d); cr.restore()
        open_shape(top, d, 6); stroke_ink(cr, 5.5)
    elif style == "teeth":     # gritted teeth
        w2, h2 = wdt * 1.2, 26
        cr.rectangle(mx - w2 / 2, my - h2 / 2, w2, h2); fill_paper(cr, WHITE); stroke_ink(cr, 5)
        cr.move_to(mx - w2 / 2, my); cr.line_to(mx + w2 / 2, my); stroke_ink(cr, 3)
        for k in range(1, 4):
            xx = mx - w2 / 2 + k * w2 / 4; cr.move_to(xx, my - h2 / 2); cr.line_to(xx, my + h2 / 2); stroke_ink(cr, 3)
    elif style == "o":
        r = 9 + 14 * op
        ellipse(cr, mx, my + 4, r * 0.85 * sx, r, sid=62); fill_ink(cr); stroke_ink(cr, 5)
    elif style == "wavy":
        cr.move_to(mx - wdt / 2, my)
        for k in range(1, 9):
            cr.line_to(mx - wdt / 2 + k * wdt / 8, my + (5 if k % 2 else -5) + sm * (k - 4) ** 2 * -0.4)
        stroke_ink(cr, 5)
    elif style == "blep":      # little tongue sticking out the middle
        cr.move_to(mx - wdt / 2, my); cr.line_to(mx + wdt / 2, my); stroke_ink(cr, 5.5)
        cr.move_to(mx - 11, my); cr.curve_to(mx - 12, my + 24, mx + 12, my + 24, mx + 11, my)
        fill_paper(cr, (0.94, 0.94, 0.94)); stroke_ink(cr, 4.5)
        cr.move_to(mx, my + 3); cr.line_to(mx, my + 12); stroke_ink(cr, 3)
    elif style == "yawn":
        ellipse(cr, mx, my + 10, 22 * sx, 34 * max(0.4, op), sid=63); fill_ink(cr); stroke_ink(cr, 5)
        cr.save(); ellipse(cr, mx, my + 10, 22 * sx, 34 * max(0.4, op), sid=63); cr.clip()
        ellipse(cr, mx, my + 34, 14 * sx, 12, sid=64); fill_paper(cr, (0.92, 0.92, 0.92)); stroke_ink(cr, 3); cr.restore()
    elif style == "scream":
        w2 = wdt * 1.3
        cr.move_to(mx - w2 * 0.35, my - 12); cr.line_to(mx + w2 * 0.35, my - 12)
        cr.curve_to(mx + w2 * 0.6, my + 30, mx + w2 * 0.4, my + 48, mx, my + 48)
        cr.curve_to(mx - w2 * 0.4, my + 48, mx - w2 * 0.6, my + 30, mx - w2 * 0.35, my - 12); cr.close_path()
        fill_ink(cr); stroke_ink(cr, 5)
    elif style == "kiss":
        ellipse(cr, mx + 4, my + 2, 9 * sx, 8, sid=65); fill_paper(cr); stroke_ink(cr, 5)
        cr.move_to(mx - 2, my + 2); cr.line_to(mx + 10, my + 2); stroke_ink(cr, 3)
    elif style == "smirk":
        cr.move_to(mx - wdt / 2, my + 4); cr.curve_to(mx, my + 8, mx + wdt / 4, my + 2, mx + wdt / 2 + 6, my - 10 - sm * 6)
        stroke_ink(cr, 5.5)
    elif style == "wail":      # crying wide open frown
        top = my + 6
        cr.move_to(mx - wdt * 0.7, top + 20); cr.curve_to(mx - wdt * 0.4, top - 16, mx + wdt * 0.4, top - 16, mx + wdt * 0.7, top + 20)
        cr.curve_to(mx + wdt * 0.3, top + 30, mx - wdt * 0.3, top + 30, mx - wdt * 0.7, top + 20); cr.close_path()
        fill_ink(cr); stroke_ink(cr, 5)
    elif style == "cat":       # :3
        for a in (-1, 1):
            cr.move_to(mx, my); cr.curve_to(mx + a * 6, my + 12, mx + a * 16, my + 12, mx + a * 20, my - 2)
        stroke_ink(cr, 5)
    elif style == "flat":
        cr.move_to(mx - wdt / 2, my); cr.line_to(mx + wdt / 2, my); stroke_ink(cr, 5.5)
    tg = p.get("tongue", 0.0)
    if tg > 0.05:
        tx, ty = mx + wdt * 0.22, my + sm * 6 + 1
        cr.move_to(tx - 11, ty); cr.curve_to(tx - 12, ty + 24 * tg, tx + 14, ty + 26 * tg, tx + 12, ty - 1)
        fill_paper(cr, (0.95, 0.95, 0.95)); stroke_ink(cr, 4.5)
        cr.move_to(tx + 1, ty + 3); cr.line_to(tx + 1, ty + 12 * tg); stroke_ink(cr, 3)

def draw_head(cr, p, blink, t=0.0):
    """head at the current origin (already translated + rotated)."""
    sq = p.get("squash", 0.0)
    cr.scale(1 + 0.1 * sq, 1 - 0.1 * sq)
    turn = p.get("turn", 0.0)
    back = p.get("back", 0.0) > 0.5
    cx_curl = _proj(-4, turn)[0] if not back else 4
    cr.save(); cr.translate(cx_curl, -HEAD_R + 6); cr.rotate(p.get("curl", 0.0) + turn * 0.15)
    cr.move_to(0, 0); cr.curve_to(-14, -50, 44, -70, 40, -38)
    cr.curve_to(37, -18, 12, -22, 16, -40); cr.curve_to(19, -52, 30, -48, 28, -40)
    stroke_ink(cr, 6.5); cr.restore()
    sketch_circle(cr, 0, 0, HEAD_R, 8, sid=3)
    if back: return
    lx, ly = p["look"]
    fy = ly * 12
    es = p.get("eyescale", 1.0)
    sk = p.get("skeptic", 0.0)
    gl = p.get("gloom", 0.0)
    if gl > 0.05:              # dread lines over the top of the face
        cr.save(); ellipse(cr, 0, 0, HEAD_R - 4, HEAD_R - 4); cr.clip()
        for k in range(9):
            xx = -80 + k * 20; cr.move_to(xx, -HEAD_R); cr.line_to(xx, -HEAD_R + 70 * gl); stroke_ink(cr, 3, alpha=0.8 * gl)
        cr.restore()
    for side in (-1, 1):
        x0 = side * 40 + lx * 14
        sx_, fs, vis = _proj(x0, turn)
        if not vis: continue
        if abs(turn) > 1.25:        # profile: one full-ish eye set back from the edge
            sx_ = math.copysign(min(abs(sx_), 74), sx_); fs = max(fs, 0.75)
        ey = -14 + fy
        rx = 25 * es * max(0.25, fs) * (1 + (0.08 if side > 0 else -0.08) * sk)
        ry = 33 * es * (1 - (0.0 if side > 0 else 0.18) * sk)
        _eye(cr, p, sx_, ey, rx, ry, side, blink, t)
        b, w = p.get("brow", 0.0) + (0.5 if side > 0 else -0.3) * sk, p.get("worry", 0.0)
        by = ey - 33 * es - 18 - b * 14
        bw = 26 * max(0.3, fs)
        inner = (sx_ - side * 6 * fs, by - w * 10)
        outer = (sx_ + side * bw, by + w * 6 + 4)
        mid = ((inner[0] + outer[0]) / 2, (inner[1] + outer[1]) / 2 - 5)
        cr.move_to(*inner); cr.curve_to(mid[0], mid[1], mid[0], mid[1], *outer); stroke_ink(cr, 8)
    mxs, mfs, mvis = _proj(lx * 11, turn, rate=0.75)
    if abs(turn) > 1.25: mxs = math.copysign(min(abs(mxs), 86), mxs)
    _mouth(cr, p, mxs, 56 + fy * 0.7, max(0.35, mfs), t)
    bl = p.get("blush", 0.0)
    if bl > 0.05:
        for side in (-1, 1):
            bxs, bfs, bvis = _proj(side * 70, turn)
            if not bvis: continue
            for k in range(3):
                x0 = bxs + (k - 1) * 10 * bfs
                cr.move_to(x0 - 5, 36 + fy); cr.line_to(x0 + 5, 24 + fy); stroke_ink(cr, 3.5, alpha=bl)
    tr = p.get("tears", 0.0)
    if tr > 0.05:              # streams + falling drops
        for side in (-1, 1):
            txs, tfs, tvis = _proj(side * 40, turn)
            if not tvis: continue
            x0, y0 = txs + side * 10, 18 + fy
            cr.move_to(x0, y0); cr.curve_to(x0 + side * 4, y0 + 40, x0 - side * 2, y0 + 70, x0 + side * 6, y0 + 92 * tr)
            stroke_ink(cr, 7, (0.6, 0.7, 0.85), 0.9 * tr)
            for k in range(2):
                u = (t * 1.6 + k * 0.5 + (0.25 if side > 0 else 0)) % 1.0
                dy = y0 + 92 * tr + u * 70
                ellipse(cr, x0 + side * (6 + u * 10), dy, 5, 7, sid=66 + k); fill_paper(cr, (0.85, 0.9, 1.0), tr * (1 - u)); stroke_ink(cr, 2.5, alpha=tr * (1 - u))
    sw = p.get("sweat", 0.0)
    if sw > 0.05:              # the classic big sweat drop at the temple
        sxs, sfs, svis = _proj(-78 if turn >= 0 else 78, turn)
        x0, y0 = sxs, -70 + 6 * math.sin(t * 3)
        cr.move_to(x0, y0 - 22 * sw); cr.curve_to(x0 - 14 * sw, y0, x0 - 14 * sw, y0 + 18 * sw, x0, y0 + 18 * sw)
        cr.curve_to(x0 + 14 * sw, y0 + 18 * sw, x0 + 14 * sw, y0, x0, y0 - 22 * sw); fill_paper(cr, (0.9, 0.95, 1.0)); stroke_ink(cr, 4)
    vn = p.get("vein", 0.0)
    if vn > 0.05:              # anger vein
        x0, y0 = _proj(52, turn)[0], -78
        s = 14 * vn * (1 + 0.15 * math.sin(t * 12))
        for a in (0, 1, 2, 3):
            ang = a * math.pi / 2 + math.pi / 4
            cr.move_to(x0 + math.cos(ang) * s * 0.35, y0 + math.sin(ang) * s * 0.35)
            cr.curve_to(x0 + math.cos(ang + 0.5) * s, y0 + math.sin(ang + 0.5) * s, x0 + math.cos(ang - 0.5) * s, y0 + math.sin(ang - 0.5) * s,
                        x0 + math.cos(ang) * s * 1.2, y0 + math.sin(ang) * s * 1.2)
        stroke_ink(cr, 4.5)

def draw_fx(cr, p, hx, hy, t):
    """cartoon symbols around his head (world coords; hx,hy = head centre)."""
    R = HEAD_R
    v = lambda k: p.get(k, 0.0)
    if v("fx_q") > 0.02:
        draw_text(cr, "?", hx + 150, hy - 150 + 6 * math.sin(t * 3), 120 * (0.6 + 0.4 * v("fx_q")), rot=0.15, alpha=v("fx_q"))
    if v("fx_ex") > 0.02:
        draw_text(cr, "!", hx + 140, hy - 170 - 10 * abs(math.sin(t * 9)), 140 * v("fx_ex"), rot=0.1, alpha=v("fx_ex"))
    if v("fx_zzz") > 0.02:
        for k in range(3):
            u = (t * 0.35 + k / 3) % 1.0
            draw_text(cr, "z", hx + 120 + u * 120, hy - 120 - u * 200, 40 + 50 * u, rot=0.2, alpha=v("fx_zzz") * math.sin(math.pi * u))
    if v("fx_hearts") > 0.02:
        for k in range(3):
            u = (t * 0.4 + k / 3) % 1.0
            x, y, s = hx - 120 + k * 120 + 20 * math.sin(t * 3 + k), hy - 160 - u * 160, 18 + 10 * u
            cr.move_to(x, y + s * 0.9); cr.curve_to(x - s * 1.6, y - s * 0.2, x - s * 0.5, y - s * 1.3, x, y - s * 0.35)
            cr.curve_to(x + s * 0.5, y - s * 1.3, x + s * 1.6, y - s * 0.2, x, y + s * 0.9)
            fill_paper(cr, PAPER, v("fx_hearts") * math.sin(math.pi * u)); stroke_ink(cr, 4, alpha=v("fx_hearts") * math.sin(math.pi * u))
    if v("fx_stars") > 0.02:   # dizzy stars orbiting
        for k in range(4):
            a = t * 4 + k * math.pi / 2
            x, y, s = hx + math.cos(a) * 150, hy - R - 20 + math.sin(a) * 34, 18
            cr.move_to(x, y - s)
            for j in range(1, 10):
                aa = -math.pi / 2 + j * math.pi / 5; r = s if j % 2 == 0 else s * 0.45
                cr.line_to(x + r * math.cos(aa), y + r * math.sin(aa))
            cr.close_path(); fill_paper(cr, PAPER, v("fx_stars")); stroke_ink(cr, 4, alpha=v("fx_stars"))
    if v("fx_bulb") > 0.02:    # idea!
        x, y, a = hx + 10, hy - R - 150, v("fx_bulb")
        sketch_circle(cr, x, y, 46 * a, 6, sid=600, alpha=a)
        cr.rectangle(x - 20 * a, y + 40 * a, 40 * a, 28 * a); fill_paper(cr, PAPER, a); stroke_ink(cr, 5, alpha=a)
        cr.move_to(x - 12 * a, y + 10 * a); cr.line_to(x - 4 * a, y - 14 * a); cr.line_to(x + 4 * a, y + 10 * a); cr.line_to(x + 12 * a, y - 14 * a); stroke_ink(cr, 3, alpha=a)
        for k in range(7):
            ang = math.pi + k * math.pi / 6
            r0, r1 = 62 * a, (86 + 8 * math.sin(t * 10 + k)) * a
            cr.move_to(x + math.cos(ang) * r0, y + math.sin(ang) * r0); cr.line_to(x + math.cos(ang) * r1, y + math.sin(ang) * r1)
            stroke_ink(cr, 5, alpha=a)
    if v("fx_steam") > 0.02:
        for side in (-1, 1):
            for k in range(2):
                u = (t * 1.2 + k * 0.5) % 1.0
                x, y = hx + side * (R * 0.75 + u * 40), hy - R * 0.6 - u * 90
                sketch_circle(cr, x, y, (14 + 26 * u) * v("fx_steam"), 4, sid=610 + k, alpha=v("fx_steam") * (1 - u))
    if v("fx_nervous") > 0.02:  # little wobble lines beside his head
        for side in (-1, 1):
            for k in range(3):
                x = hx + side * (R + 26 + k * 4); y = hy - 40 + k * 34
                cr.move_to(x, y); cr.curve_to(x + side * 14, y + 6, x + side * 14, y + 16, x + side * 2 * math.sin(t * 20), y + 22)
                stroke_ink(cr, 4, alpha=v("fx_nervous"))
    if v("fx_notes") > 0.02:
        for k in range(3):
            u = (t * 0.45 + k / 3) % 1.0
            x, y = hx + 140 + 30 * math.sin(t * 2 + k), hy - 80 - u * 220
            a = v("fx_notes") * math.sin(math.pi * u)
            ellipse(cr, x, y, 13, 10, rot=-0.4, sid=620 + k); fill_ink(cr, INK, a); cr.new_path()
            cr.move_to(x + 11, y - 2); cr.line_to(x + 11, y - 48); cr.line_to(x + 30, y - 38); stroke_ink(cr, 4.5, alpha=a)
    if v("fx_sparkle") > 0.02:
        for k in range(4):
            ph = (t * 1.5 + k * 0.37) % 1.0
            x, y = hx + math.cos(k * 1.9) * 170, hy + math.sin(k * 2.7) * 110 - 40
            s = 22 * math.sin(math.pi * ph) * v("fx_sparkle")
            if s < 1: continue
            cr.move_to(x, y - s); cr.curve_to(x, y, x, y, x + s, y); cr.curve_to(x, y, x, y, x, y + s)
            cr.curve_to(x, y, x, y, x - s, y); cr.curve_to(x, y, x, y, x, y - s); stroke_ink(cr, 3.5)
    if v("fx_swirl") > 0.02:   # angry/confused scribble cloud
        x, y = hx + 20, hy - R - 70
        cr.move_to(x - 60, y)
        for k in range(40):
            a = k * 0.9 + t * 5
            cr.line_to(x - 60 + k * 3 + 18 * math.cos(a), y + 14 * math.sin(a * 1.3))
        stroke_ink(cr, 4, alpha=v("fx_swirl"))

# ------------------------------------------------------------------- body ---
def draw_guy(cr, t, p, blink):
    """the hero. p = live pose (world coords)."""
    if p.get("show", 1.0) < 0.01: return
    g = lambda k: p[k]
    hx, hy = g("head")
    breath = math.sin(t * 1.7) * 2.5 * (1 + 2.5 * p.get("sleep", 0.0))
    hy += breath
    nk = (g("neck")[0], g("neck")[1] + breath * 0.5)
    hip = g("hip")
    sh = lerp(nk, hip, 0.1)
    for i, kn, ft in ((0, "lknee", "lfoot"), (1, "rknee", "rfoot")):
        path(cr, sketch_pts(bez(hip, thru(hip, g(kn), g(ft)), g(ft)), amp=1.2, sid=11 + i * 5, step=14)); stroke_ink(cr, 9)
    tip = p.get("tiptoe", 0.0)
    draw_foot(cr, g("lfoot"), p.get("lfoot_dir", 0.0), tip, sid=70)
    draw_foot(cr, g("rfoot"), p.get("rfoot_dir", 0.0), tip, sid=71)
    mid = ((nk[0] + hip[0]) / 2 + (nk[0] - hip[0]) * 0.1, (nk[1] + hip[1]) / 2)
    path(cr, sketch_pts(bez(nk, mid, hip), amp=1.2, sid=21, step=14)); stroke_ink(cr, 9)
    sketch_line(cr, [nk, (hx, hy + HEAD_R - 4)], 9, sid=9, amp=0.8)
    arms = [(0, "lelb", "lhand", "lhand_t", -1, "lhand_front"), (1, "relb", "rhand", "rhand_t", 1, "rhand_front")]
    def arm(i, el, hd, ht, side):
        c_ = thru(sh, g(el), g(hd))
        path(cr, sketch_pts(bez(sh, c_, g(hd)), amp=1.2, sid=31 + i * 5, step=14)); stroke_ink(cr, 9)
        draw_hand(cr, g(hd), lerp(c_, g(hd), 0.6), p.get(ht, "mitt"), side, sid=80 + i * 10)
    for i, el, hd, ht, side, fr in arms:
        if p.get(fr, 0.0) < 0.5: arm(i, el, hd, ht, side)
    cr.save(); cr.translate(hx, hy); cr.rotate(g("tilt"))
    draw_head(cr, p, blink, t)
    cr.restore()
    for i, el, hd, ht, side, fr in arms:
        if p.get(fr, 0.0) >= 0.5: arm(i, el, hd, ht, side)
    draw_fx(cr, p, hx, hy, t)

def draw_grips(cr, p):
    """hands set to "grip" are drawn after the prop they hold (so the mitten sits over its edge)."""
    for hd, ht, el, side in (("lhand", "lhand_t", "lelb", -1), ("rhand", "rhand_t", "relb", 1)):
        if p.get(ht) == "grip":
            draw_hand(cr, p[hd], p[el], "mitt", side, sid=95 if side < 0 else 105)

JOINTS = ("head", "neck", "hip", "lelb", "lhand", "relb", "rhand", "lknee", "lfoot", "rknee", "rfoot")
