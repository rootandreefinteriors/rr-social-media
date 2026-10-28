"""props — the clipboard, the pocket, cartoon effects (speed lines, poofs, dust, impact stars) and the comment card."""
import math
import ink
from ink import (INK, PAPER, WHITE, FLOOR_Y, SAFE, wob, sketch_pts, path, stroke_ink, fill_paper, fill_ink, sketch_line,
                 sketch_circle, sketch_rect, ellipse, text_surface, fit_text, back_out, smooth, clamp01)

# ------------------------------------------------------------ clipboard ---
def draw_clip(cr, x, top, s=0.72):
    sketch_rect(cr, x - 70 * s, top - 22 * s, x + 70 * s, top + 26 * s, 6, sid=301)
    cr.arc(x, top - 22 * s, 24 * s, math.pi, 2 * math.pi); stroke_ink(cr, 6)
    cr.arc(x, top - 22 * s, 11 * s, math.pi, 2 * math.pi); stroke_ink(cr, 4)

def draw_clipboard(cr, cx, cy, w, h, rot=0.0, flip=0.0, front=None, alpha=1.0):
    """clipboard centred at (cx,cy). flip 0 = back towards camera .. 1 = front (the sign) towards camera."""
    sx = math.cos(math.pi * flip)
    if abs(sx) < 0.02: sx = 0.02 if sx >= 0 else -0.02
    cr.save(); cr.translate(cx, cy); cr.rotate(rot); cr.scale(abs(sx), 1)
    cr.push_group()
    sketch_rect(cr, -w / 2, -h / 2, w / 2, h / 2, 7, sid=300)
    if sx < 0:
        sketch_rect(cr, -w / 2 + 24, -h / 2 + 44, w / 2 - 24, h / 2 - 20, 4, sid=310, amp=1.0)
        if front: front(cr, w - 48, h - 64)
    else:
        for k in range(3):
            yy = -h / 2 + h * (0.3 + 0.2 * k)
            sketch_line(cr, [(-w / 2 + 40, yy), (-w / 2 + 120, yy - 40)], 3, sid=320 + k, alpha=0.3)
    draw_clip(cr, 0, -h / 2 + 10)
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha)
    cr.restore()

def sign_front(text, lines=None):
    """front() callable for draw_clipboard that writes TEXT in big marker letters."""
    def f(cr, w, h):
        s, tw, th = fit_text(text, w - 30, h - 40, lines=lines)
        jx, jy = wob(77, 4) * 1.5, wob(78, 5) * 1.5
        cr.save(); cr.translate(-tw / 2 + jx, -th / 2 + 18 + jy); cr.set_source_surface(s, 0, 0); cr.paint(); cr.restore()
    return f

def draw_pen(cr, x, y, ang=0.35, s=1.0, alpha=1.0):
    """a marker pen; (x,y) = where his hand holds it, tip pointing along ang+pi/2."""
    cr.save(); cr.translate(x, y); cr.rotate(ang)
    sketch_rect(cr, -9 * s, -78 * s, 9 * s, 14 * s, 5, sid=330, alpha=alpha)
    cr.move_to(-9 * s, 14 * s); cr.line_to(0, 34 * s); cr.line_to(9 * s, 14 * s); stroke_ink(cr, 5, alpha=alpha)
    cr.rectangle(-9 * s, -78 * s, 18 * s, 16 * s); fill_ink(cr, INK, alpha); cr.new_path()
    cr.restore()

def draw_pocket(cr, x, y, u, w=58):
    """a cartoon pocket opening (dark slit with a lip) that appears where a pocket would be. u 0..1."""
    if u <= 0.01: return
    s = back_out(min(1.0, u), 2.2)
    ellipse(cr, x, y, w * s, 15 * s, sid=500, amp=0.03); fill_ink(cr); cr.new_path()
    cr.move_to(x - w * s * 1.05, y - 3); cr.curve_to(x - w * s * 0.4, y - 13 * s, x + w * s * 0.4, y - 13 * s, x + w * s * 1.05, y - 3)
    stroke_ink(cr, 5)

# -------------------------------------------------------------- effects ---
def motion_lines(cr, x, y, ang, n=3, length=60, spread=26, alpha=1.0, sid=0, width=4):
    """cartoon speed lines trailing at angle ang (radians) from (x,y)."""
    for k in range(n):
        off = (k - (n - 1) / 2) * spread
        ox, oy = -math.sin(ang) * off, math.cos(ang) * off
        L = length * (0.7 + 0.3 * wob(sid + k, 2))
        sketch_line(cr, [(x + ox, y + oy), (x + ox + math.cos(ang) * L, y + oy + math.sin(ang) * L)], width, sid=sid + k,
                    amp=0.8, alpha=alpha)

def burst_lines(cr, x, y, u, r0=40, r1=110, n=8, sid=0, width=5):
    """radial 'pop!' lines around a point. u: 0..1 life."""
    if not (0 < u < 1): return
    a = 1 - smooth(u)
    for k in range(n):
        ang = k * 2 * math.pi / n + sid
        ra, rb = r0 + (r1 - r0) * u * 0.6, r0 + (r1 - r0) * min(1.0, u * 1.6)
        sketch_line(cr, [(x + math.cos(ang) * ra, y + math.sin(ang) * ra), (x + math.cos(ang) * rb, y + math.sin(ang) * rb)],
                    width, sid=sid + k, amp=0.6, alpha=a)

def draw_poof(cr, x, y, u, r=120, sid=0):
    """cartoon poof cloud. u: 0..1 life."""
    if not (0 < u < 1): return
    a = 1 - smooth((u - 0.55) / 0.45)
    rr = r * (0.4 + 0.8 * back_out(min(1, u * 2.2)))
    for k in range(7):
        ang = k / 7 * 2 * math.pi + sid
        bx, by = x + math.cos(ang) * rr * 0.55, y + math.sin(ang) * rr * 0.45
        sketch_circle(cr, bx, by, rr * (0.38 + 0.08 * math.sin(k * 2.3)), 5, sid=sid + k, alpha=a)
    sketch_circle(cr, x, y, rr * 0.5, 5, sid=sid + 9, alpha=a)

def draw_dust(cr, x, y, u, side=0, sid=0):
    """little dust puffs at the feet (skids, landings). side: -1 / 1 puff direction, 0 both."""
    if not (0 < u < 1): return
    a = 1 - smooth(u)
    for k in range(4):
        d = (k % 2 * 2 - 1) if side == 0 else side
        bx = x + d * (20 + 70 * u * (0.6 + 0.2 * k)); by = y - 8 - 30 * u * (k % 3) * 0.5
        sketch_circle(cr, bx, by, 10 + 16 * u, 4, sid=sid + k, alpha=a)

def draw_impact(cr, x, y, u, r=70, sid=0):
    """cartoon impact star (bonk!)."""
    if not (0 < u < 1): return
    a = 1 - smooth((u - 0.4) / 0.6); s = r * back_out(min(1.0, u * 3))
    pts = []
    for k in range(16):
        ang = k * math.pi / 8 + sid; rr = s if k % 2 == 0 else s * 0.5
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    path(cr, pts); cr.close_path(); fill_paper(cr, WHITE, a); stroke_ink(cr, 5, alpha=a)

def draw_shadow(cr, x, scale=1.0, alpha=0.35):
    for k in range(3):
        w_ = (62 - k * 16) * scale
        cr.move_to(x - w_ + k * 6, FLOOR_Y + 9 + k * 7); cr.line_to(x + w_ - k * 4, FLOOR_Y + 9 + k * 7)
        stroke_ink(cr, 2, alpha=alpha)

# --------------------------------------------------------- comment card ---
def draw_comment_card(cr, username, text, likes=None, x=None, y=None, w=560, alpha=1.0, scale=1.0):
    """the winning comment, pinned top-right (screen space, inside the safe zone)."""
    x = SAFE[2] - w * scale if x is None else x
    y = 100 if y is None else y                  # high up, clear of his head (user note 2026-10-28: "always be higher")
    s_user, uw, uh = text_surface("@" + username, 36, max_w=w - 120, align="left")
    for size in (46, 42, 38, 34, 30, 27):        # long comments shrink so the card never grows down onto his head
        s_txt, tw, th = text_surface(text, size, max_w=w - 50, align="left")
        if th <= 140: break
    hgt = 30 + uh + th + (40 if likes is not None else 10)
    cr.save(); cr.translate(x, y); cr.scale(scale, scale)
    cr.push_group()
    sketch_rect(cr, 0, 0, w, hgt, 5, sid=900, fill=WHITE)
    sketch_circle(cr, 42, 42, 22, 4, sid=901)
    cr.set_source_surface(s_user, 70, 14); cr.paint()
    cr.set_source_surface(s_txt, 10, 18 + uh); cr.paint()
    if likes is not None:
        s_l, lw, lh = text_surface(str(likes), 32, align="left")
        lx0 = w - lw - 6; cr.set_source_surface(s_l, lx0, hgt - 50); cr.paint()
        hx, hy, hs = lx0 + 4, hgt - 26, 11          # little drawn heart
        cr.move_to(hx, hy + hs * 0.9); cr.curve_to(hx - hs * 1.6, hy - hs * 0.2, hx - hs * 0.5, hy - hs * 1.3, hx, hy - hs * 0.35)
        cr.curve_to(hx + hs * 0.5, hy - hs * 1.3, hx + hs * 1.6, hy - hs * 0.2, hx, hy + hs * 0.9); fill_ink(cr); cr.new_path()
    cr.pop_group_to_source(); cr.paint_with_alpha(alpha)
    cr.restore()
