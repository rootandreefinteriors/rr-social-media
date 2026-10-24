import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
import cairo, ink, character as C
W, H = 2400, 1500
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cr = cairo.Context(surf)
cr.set_source_rgb(*ink.PAPER); cr.paint()
cells = [("deadpan", {}), ("dead_stare", {}), ("resigned", {}), ("holding_it", dict(heat_fill=0.45, sweat=0.8, twitch=1.0)),
         ("holding_it", dict(heat_fill=0.85, pupil=0.55, fx_steam=0.6, curl_up=1.0, tear1=1.0, tilt=0.12)),
         ("deadpan", dict(heat_fill=1.0, curl_up=1.0))]
for i, (face, kw) in enumerate(cells):
    p = C.constrain(C.pose("stand", face, **kw))
    cr.save(); cr.translate(-140 + i * 400, -400); C.draw_guy(cr, 1.3, p, 0.0); cr.restore()
for i, body in enumerate(["shrug", "cheer", "crouch", "think", "point_right", "sit_floor"]):
    p = C.constrain(C.pose(body, "deadpan"))
    cr.save(); cr.translate(-140 + i * 400, 800); cr.scale(0.45, 0.45); cr.translate(0, -0); C.draw_guy(cr, 1.3, p, 0.0); cr.restore()
surf.write_to_png("faces.png"); print("ok")
