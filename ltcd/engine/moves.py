"""moves — tested building blocks for LTCD episodes. Episodes should be built from these, not hand-placed joints.

    import moves as M
    S = M.Scene()
    S.enter_peek(0.0)                       # peeks in from the left, notices us, walks to centre   (-> ~3.7 s)
    S.wave(S.t)                             # shy wave                                              (+1.1 s)
    S.face(S.t, "eager"); S.wait(0.5)
    S.walk_to(S.t, 200, 1.5)                # walk to an x offset (body offset, 0 = centre)
    S.jump(S.t); S.dance(S.t, 3.0); S.cheer(S.t); S.nod(S.t); S.shake_head(S.t); S.shrug(S.t)
    S.thumbs_up(S.t); S.facepalm(S.t); S.sit(S.t); S.stand(S.t); S.sleep(S.t, 3); S.look(S.t, (1, 0))
    S.poof(S.t, (x, y)); S.sfx(S.t, "pop", 0.2); S.card("username", "comment text", likes)
    S.the_ask(S.t)                          # the standard ending: dig at hip -> clipboard -> write -> flip -> hopeful hold
    S.render("out.mp4")                     # or --still times

Every move starts at time t, advances S.t to its end, and leaves him in a known resting pose. Arms/legs are
length-constrained by the engine, so nothing can detach. Sound is sparse on purpose: moves add at most one soft
effect on their key action.
"""
import math, sys
import ltcd as L
from ltcd import pose, Track, ramp, pulse, lerp, back_out
from ink import smooth as smooth_

CARD_CAM = (540, 930, 1.15)      # framing when a comment card is pinned
CARD_FX_OFF = ("fx_q", "fx_ex", "fx_bulb")   # symbols that would sit under the pinned card: off while it is shown

class _Cam:
    """camera track + shakes (shakes: (t0, dur, amp))."""
    def __init__(self, track, shakes): self.track, self.shakes = track, list(shakes)
    def at(self, t):
        cx, cy, z = self.track.at(t)
        for t0, d, a in self.shakes:
            if t0 <= t < t0 + d:
                k = a * (1 - (t - t0) / d) ** 1.5
                cx += k * math.sin(t * 71.0); cy += k * math.cos(t * 57.0)
        return (cx, cy, z)

class _SignFront:
    """the sign's face: the main message, plus an optional handwritten addition under it that writes on (reveal 0..1)."""
    def __init__(self, lines, extra=None):
        self.lines, self.extra, self.reveal = lines, extra, 0.0
        self.main = L.sign_front(" ".join(lines), lines=lines)
    def __call__(self, cr, w, h):
        if not self.extra:
            self.main(cr, w, h); return
        mh = h * 0.74
        s, tw, th = L.fit_text(" ".join(self.lines), w - 30, mh - 30, lines=self.lines)
        cr.save(); cr.translate(-tw / 2, -h / 2 + (mh - th) / 2 + 6); cr.set_source_surface(s, 0, 0); cr.paint(); cr.restore()
        if self.reveal > 0.01:
            s2, tw2, th2 = L.fit_text(self.extra, w - 90, h * 0.17, lines=[self.extra])
            x0, y0 = -tw2 / 2, h / 2 - h * 0.235
            cr.save(); cr.rectangle(x0 - 4, y0 - 6, (tw2 + 8) * self.reveal, th2 + 12); cr.clip()
            cr.translate(x0, y0); cr.rotate(-0.025); cr.set_source_surface(s2, 0, 0); cr.paint(); cr.restore()

class Scene:
    def __init__(self, start_body="stand", start_face="neutral", x0=0.0, zoom=1.22):
        self.body, self.face_name, self.extra = start_body, start_face, {}
        self.keys = [(0.0, pose(start_body, start_face), 0)]
        self.xkeys = [(0.0, x0, 0)]
        self.camkeys = [(0.0, (540, 1000, zoom), 0)]
        self.hooks, self.props, self.overlays, self.sfxs, self.blinks = [], [], [], [], []
        self.t = 0.0
        self.x = x0
        self.card_on = False
        self.objects = {}
        self.props.append(self._draw_objects)
        self.cam = (540, 1000, zoom)
        self.bgs, self.shakes, self.floor, self.cuts = [], [], True, []

    # ------------------------------------------------------------- basics
    def _key(self, t, dur=0.3, ease="smooth", **kw):
        self.extra.update({k: v for k, v in kw.items() if k not in ("body", "face")})
        if "body" in kw: self.body = kw["body"]
        if "face" in kw: self.face_name = kw["face"]
        d = pose(self.body, self.face_name, **self.extra)
        self.keys.append((t, d, dur, ease))

    def set(self, t, body=None, face=None, dur=0.3, ease="smooth", clear=True, **kw):
        """change body pose and/or expression at t (clear=True drops previous one-off overrides)."""
        if clear: self.extra = {}
        args = dict(kw)
        if body: args["body"] = body
        if face: args["face"] = face
        self._key(t, dur, ease, **args)
        return self

    def face(self, t, face, dur=0.25, **kw):
        return self.set(t, face=face, dur=dur, clear=False, **kw)

    def wait(self, s): self.t += s; return self

    def sfx(self, t, kind, gain=0.2, **kw): self.sfxs.append((t, kind, gain, kw) if kw else (t, kind, gain)); return self

    def camera(self, t, cx=540, cy=1000, zoom=1.22, dur=1.0, ease="smooth"):
        self.camkeys.append((t, (cx, cy, zoom), dur, ease)); self.cam = (cx, cy, zoom); return self

    def blink(self, *ts): self.blinks += list(ts); return self

    def card(self, username, text, likes=None, t0=0.0, t1=None):
        """pin the winning comment top-right. Frames him a little smaller/lower so the card never covers his head."""
        self.card_on = True
        self.camkeys[0] = (0.0, CARD_CAM, 0); self.cam = CARD_CAM
        def ov(cr, t):
            if t >= t0 and (t1 is None or t < t1):
                L.draw_comment_card(cr, username, text, likes, alpha=min(1.0, (t - t0) / 0.3 + 0.01))
        self.overlays.append(ov); return self

    def _hook(self, fn): self.hooks.append(fn)
    def _prop(self, fn): self.props.append(fn)

    # ------------------------------------------------------------- world / camera extras
    def hook(self, fn): self.hooks.append(fn); return self            # fn(t, pose) -> pose
    def prop(self, fn): self.props.append(fn); return self            # fn(cr, t, pose, layer)  layer "back"/"front"
    def overlay(self, fn): self.overlays.append(fn); return self      # fn(cr, t)  screen space
    def background(self, fn): self.bgs.append(fn); return self        # fn(cr, t)  world space, before everything
    def shake(self, t, dur=0.5, amp=14): self.shakes.append((t, dur, amp)); return self
    def cut(self, t, cam=None, x=None):
        """HARD CUT at t: optional new camera (cx, cy, zoom) and body offset, both instant; follow-through restarts."""
        self.cuts.append(t)
        if cam: self.camkeys.append((t, cam, 0.001, "linear")); self.cam = cam
        if x is not None: self.xkeys.append((t, x, 0.001, "linear")); self.x = x
        return self
    def flash(self, t, dur=0.6, color=(1.0, 1.0, 1.0)):
        """full-screen flash that fades out (drawn under the comment card)."""
        def ov(cr, tt):
            if t <= tt < t + dur:
                cr.set_source_rgba(color[0], color[1], color[2], (1 - (tt - t) / dur) ** 0.7); cr.paint()
        self.overlays.insert(0, ov); return self

    def read_card(self, t, react="eager", lines=2, dur=None, face="thinking"):
        """looks up at the pinned comment and reads it (eyes scan each line), then back to us with a reaction."""
        per = 0.85; dur = dur or 0.5 + per * lines
        self.set(t, "stand", face, dur=0.3, look=(0.7, -0.85), tilt=-0.06)
        def hk(tt, p):
            if t + 0.35 <= tt < t + 0.35 + per * lines:
                k = (tt - t - 0.35) / per; u = k % 1.0
                p["look"] = (0.4 + 0.5 * smooth_(u), -0.9 + 0.12 * int(k))
            return p
        self.hook(hk)
        self.set(t + dur, "stand", react, dur=0.25, ease="back")
        self.t = t + dur + 0.35
        return self

    # ------------------------------------------------------------- locomotion
    def walk_to(self, t, x, dur=None, face=None):
        dur = dur or max(0.6, abs(x - self.x) / 380)
        self.xkeys.append((t, x, dur)); self.x = x
        if face: self.face(t, face)
        self.t = t + dur
        self.set(self.t - 0.12, stretch=-0.25, dur=0.1, ease="snap", clear=False)
        self.set(self.t, stretch=0.0, dur=0.3, ease="back", clear=False)
        self.t += 0.25
        return self

    def run_to(self, t, x, dur=None):
        dur = dur or max(0.4, abs(x - self.x) / 900)
        self.set(t, run=1.0, dur=0.15, clear=False)
        self.xkeys.append((t, x, dur, "linear")); self.x = x
        self.set(t + dur, run=0.0, stretch=-0.3, dur=0.08, ease="snap", clear=False)
        self.set(t + dur + 0.1, stretch=0.0, dur=0.3, ease="back", clear=False)
        self.t = t + dur + 0.4
        return self

    def enter_peek(self, t=0.0):
        """peek in from the left edge, notice us (little hop), smile shyly, walk to centre."""
        self.xkeys = [(0.0, -800, 0), (t + 0.15, -605, 0.6, "out")]
        self.set(t, "stand", "neutral", dur=0, lean=0.25, look=(0.7, -0.1), smile=0.1)
        self.set(t + 0.9, "stand", "neutral", dur=0.25, ease="out", lean=0.25, look=(0.25, 0.0), smile=0.1)
        self.set(t + 1.1, "stand", "surprised", dur=0.12, ease="snap", lean=0.21, look=(0.25, 0.0))
        self.set(t + 1.45, "stand", "shy", dur=0.35, lean=0.24, look=(0.3, 0.05))
        self.set(t + 1.75, "stand", "shy", dur=0.6, lean=0.0, look=(0.2, 0.0), blush=0.5)
        self._hop(t + 1.12, 12)
        self.xkeys.append((t + 1.75, 0, 1.85)); self.x = 0
        self.set(t + 3.55, "stand", "happy", dur=0.1, ease="snap", stretch=-0.3)
        self.set(t + 3.7, "stand", "happy", dur=0.3, ease="back")
        self.t = t + 3.9
        return self

    # ------------------------------------------------------------- gestures
    def _hop(self, t0, h=14, w=0.09):
        def hk(t, p):
            v = h * pulse(t, t0, w)
            if v > 0.05:
                for k in L.JOINTS: p[k] = (p[k][0], p[k][1] - v)
            return p
        self._hook(hk)

    def hop(self, t, n=1, h=14, gap=0.4):
        for i in range(n): self._hop(t + i * gap + 0.1, h)
        self.t = t + n * gap + 0.1; return self

    def wave(self, t, dur=1.1, face="shy"):
        self.set(t, "wave", face, dur=0.25, ease="back", blush=0.8 if face == "shy" else 0.0)
        def hk(tt, p):
            if t <= tt < t + dur: p["rhand"] = (p["rhand"][0] + 24 * math.sin((tt - t) * 14), p["rhand"][1])
            return p
        self._hook(hk)
        self.set(t + dur, "stand", self.face_name, dur=0.3)
        self.t = t + dur + 0.3; return self

    def nod(self, t, n=2):
        for i in range(n):
            self.set(t + i * 0.32, tilt=0.0, dur=0.08, clear=False)
            def hk(tt, p, t0=t + i * 0.32):
                v = 22 * pulse(tt, t0 + 0.1, 0.07); p["head"] = (p["head"][0], p["head"][1] + v); return p
            self._hook(hk)
        self.t = t + n * 0.32 + 0.1; return self

    def shake_head(self, t, n=3):
        def hk(tt, p):
            if t <= tt < t + n * 0.22:
                p["look"] = (p["look"][0] + 0.6 * math.sin((tt - t) * 28), p["look"][1])
                p["head"] = (p["head"][0] + 10 * math.sin((tt - t) * 28), p["head"][1])
            return p
        self._hook(hk); self.t = t + n * 0.22 + 0.1; return self

    def look(self, t, where=(0, 0), dur=0.25):
        return self.set(t, look=where, dur=dur, clear=False)

    def _pose_beat(self, t, body, face, hold, back="stand", **kw):
        self.set(t, body, face, dur=0.25, ease="back", **kw)
        self.set(t + hold, back, self.face_name if back == "stand" else face, dur=0.3)
        self.t = t + hold + 0.3; return self

    def shrug(self, t, hold=1.0): return self._pose_beat(t, "shrug", "confused", hold)
    def thumbs_up(self, t, hold=1.0): return self._pose_beat(t, "thumbs_up", "proud", hold)
    def facepalm(self, t, hold=1.2): return self._pose_beat(t, "facepalm", "annoyed", hold)
    def think(self, t, hold=1.5): return self._pose_beat(t, "think", "thinking", hold)
    def scratch_head(self, t, hold=1.2): return self._pose_beat(t, "scratch_head", "confused", hold)
    def arms_crossed(self, t, hold=1.5, face="impatient"): return self._pose_beat(t, "arms_crossed", face, hold)
    def hands_hips(self, t, hold=1.5, face="determined"): return self._pose_beat(t, "hands_hips", face, hold)
    def point(self, t, side="right", hold=1.0, face="eager"):
        return self._pose_beat(t, "point_right" if side == "right" else "point_left", face, hold)

    def cheer(self, t, hold=1.0):
        self.set(t, "crouch", "eager", dur=0.18)                         # anticipation
        self.set(t + 0.2, "cheer", "delighted", dur=0.15, ease="back")
        self._hop(t + 0.32, 40, 0.13)
        self.set(t + 0.2 + hold, "stand", "happy", dur=0.35)
        self.t = t + hold + 0.6; return self

    def jump(self, t, height=90):
        self.set(t, "crouch", "determined", dur=0.2)                     # anticipation squash
        self.set(t + 0.22, "jump_tuck", "delighted", dur=0.12, ease="snap")
        self._hop(t + 0.5, height, 0.2)
        self.set(t + 0.75, "crouch", "happy", dur=0.1, ease="snap")      # land
        self.set(t + 0.9, "stand", "happy", dur=0.3, ease="back")
        self.sfx(t + 0.78, "thud", 0.12)
        self.t = t + 1.25; return self

    def dance(self, t, dur=3.0, face="singing"):
        self.set(t, "stand", face, dur=0.3, dance=1.0)
        self.set(t + dur, "stand", "happy", dur=0.4, dance=0.0)
        self.t = t + dur + 0.4; return self

    def sit(self, t, face="bored"):
        self.set(t, "crouch", face, dur=0.25); self.set(t + 0.3, "sit_floor", face, dur=0.25, ease="back")
        self.sfx(t + 0.5, "thud", 0.1); self.t = t + 0.8; return self

    def stand(self, t, face="neutral"):
        self.set(t, "crouch", face, dur=0.3); self.set(t + 0.35, "stand", face, dur=0.3, ease="back")
        self.t = t + 0.7; return self

    def sleep(self, t, dur=3.0):
        self.set(t, "stand", "sleepy", dur=0.6); self.set(t + 0.8, "stand", "asleep", dur=0.6)
        self.set(t + dur, "stand", "surprised", dur=0.12, ease="snap"); self._hop(t + dur + 0.05, 16)
        self.set(t + dur + 0.4, "stand", "embarrassed", dur=0.3)
        self.t = t + dur + 0.9; return self

    def poof(self, t, at=(540, 1100), r=140, sound=True):
        def pr(cr, tt, p, layer):
            if layer == "front": L.draw_poof(cr, at[0], at[1], (tt - t) / 0.7, r=r, sid=3)
        self._prop(pr)
        if sound: self.sfx(t, "poof", 0.18)
        return self

    # ------------------------------------------------------------- objects (props that persist)
    def _draw_objects(self, cr, t, p, layer):
        for name, o in self.objects.items():
            if o["layer"] != layer or t < o["t_on"] or (o["t_off"] is not None and t >= o["t_off"]): continue
            s = back_out(min(1.0, (t - o["t_on"]) / 0.25), 1.8) if o["pop"] else 1.0
            s = max(0.05, s)
            if o.get("follow"):
                jx, jy = p[o["follow"]]; ox_, oy_ = o.get("offset", (0, 0))
                o["drawer"](cr, jx + ox_, jy + oy_, s, t, p)
            else:
                o["drawer"](cr, o["land"][0], o["land"][1], s, t, p)

    def place(self, name, drawer, land, t_on=0.0, layer="front", pop=False, follow=None, offset=(0, 0)):
        """put a prop in the world. drawer(cr, x, y, scale, t, pose) draws it with bottom-centre at (x, y).
        follow="rhand" keeps it in his hand (x, y = that joint + offset)."""
        self.objects[name] = dict(drawer=drawer, land=land, t_on=t_on, t_off=None, layer=layer, pop=pop, follow=follow,
                                  offset=offset); return self

    def hide(self, name, t): self.objects[name]["t_off"] = t; return self

    def poof_away(self, name, t, at=None, r=170):
        o = self.objects[name]; o["t_off"] = t + 0.12
        self.poof(t, at or (o["land"][0], o["land"][1] - 150), r=r)
        self.t = t + 0.7; return self

    def pocket_pull(self, t, name, drawer, land, layer="front", narrow_w=64, held=False, offset=(0, 0)):
        """his signature gag: digs his hand around at his hip (NO pocket is drawn), pulls - it keeps coming out - POP,
        the prop lands at `land`."""
        ox = self.x
        POCKET = (588 + ox, 1092)
        A, C_, B = POCKET, (690 + ox, 860), (720 + ox, 560)
        T_P, T_REACH, T_PULL, T_POP = t + 0.2, t + 0.35, t + 1.2, t + 2.1
        S = self
        S.set(t, "stand", "thinking", dur=0.25, look=(0.4, 0.8), tilt=0.08)
        S.set(T_P + 0.05, "stand", "surprised", dur=0.1, ease="snap", look=(0.4, 0.8), eyescale=1.06, open=0.3)
        S.set(T_P + 0.25, "stand", "concentrating", dur=0.2, look=(0.4, 0.8), tilt=0.1)
        S.set(T_PULL - 0.1, "stand", "eager", dur=0.1, ease="snap", look=(0.45, 0.3))
        S.set(T_PULL + 0.05, "stand", "surprised", dur=0.7, look=(0.5, -0.8), eyescale=1.08, open=0.4)
        S.set(T_POP + 0.02, "stand", "delighted", dur=0.1, ease="snap", look=(0.3, 0.0))
        S.set(T_POP + 0.5, "stand", "happy", dur=0.3)
        S.sfx(T_POP, "pop", 0.2)
        def bez(u): return ((1 - u) ** 2 * A[0] + 2 * (1 - u) * u * C_[0] + u * u * B[0], (1 - u) ** 2 * A[1] + 2 * (1 - u) * u * C_[1] + u * u * B[1])
        def ph(tt): return bez(ramp(tt, T_PULL, T_POP))
        def hk(tt, p):
            if T_REACH <= tt < T_PULL:
                u = ramp(tt, T_REACH, T_REACH + 0.25)          # hand to the hip, digs around (visible, no pocket)
                dig = ramp(tt, T_REACH + 0.25, T_REACH + 0.35) * (1 - ramp(tt, T_PULL - 0.15, T_PULL - 0.05))
                p["rhand"] = lerp(p["rhand"], (POCKET[0] + 14 * math.sin(tt * 24) * dig, POCKET[1] + 6 * math.sin(tt * 31) * dig), u)
            if T_PULL <= tt < T_POP: p["rhand"] = ph(tt); p["rhand_t"] = "none"
            return p
        def pr(cr, tt, p, ly):
            if ly != "front" or not (T_P <= tt < T_POP + 0.3): return
            u = ramp(tt, T_P, T_P + 0.15, "linear") * (1 - ramp(tt, T_POP + 0.1, T_POP + 0.25, "linear"))
            if T_PULL <= tt < T_POP and narrow_w > 0:
                (ax, ay), (bx, by) = POCKET, ph(tt)
                ang = math.atan2(by - ay, bx - ax); L_ = math.hypot(bx - ax, by - ay)
                cr.save(); cr.translate(ax, ay); cr.rotate(ang); L.sketch_rect(cr, -10, -narrow_w / 2, L_ + 6, narrow_w / 2, 7, sid=301); cr.restore()
            if T_PULL <= tt < T_POP:
                h = ph(tt); L.draw_hand(cr, h, (h[0] - 30, h[1] + 60), "mitt", 1, sid=451)
            if T_POP <= tt < T_POP + 0.3:
                bx_, by_ = (p["rhand"][0], p["rhand"][1] - 60) if held else (land[0], land[1] - 160)
                L.burst_lines(cr, bx_, by_, (tt - T_POP) / 0.4, r0=140 if not held else 90, r1=230 if not held else 160, n=10, sid=9)
        self._hook(hk); self._prop(pr)
        if held:
            def hk2(tt, p):
                if T_POP <= tt < T_POP + 0.35: p["rhand"] = (B[0] - 5, B[1] + 8)
                return p
            self._hook(hk2)
        self.place(name, drawer, land, t_on=T_POP, layer=layer, pop=True, follow="rhand" if held else None, offset=offset)
        self.t = T_POP + 0.6
        return self

    # ------------------------------------------------------------- WAITING: just him and the sign
    def hold_sign(self, t, dur, lines=("TELL ME", "WHAT TO DO", "NEXT IN THE", "COMMENTS"), extra=None, write_at=None,
                  write_dur=1.6, push=True, extra_shown=None, hold_y=1120):
        """He stands holding the sign up, facing us, the whole time (the message is the star). Optional single beat at
        write_at: he turns the sign to himself, writes `extra` (pen bobbing over the top edge), turns it back and the
        new line is there under the message. `extra_shown` = a line that is already on the sign from an earlier day.
        Deadpan throughout. Use for waiting episodes; no other gags needed."""
        ox = self.x
        BW, BH = 470, 560
        HOLD = (540 + ox, hold_y)
        S = self
        front = _SignFront(list(lines), extra or extra_shown)
        T_F0 = write_at if write_at is not None else 1e9          # flip to him
        T_W0, T_W1 = T_F0 + 0.55, T_F0 + 0.55 + write_dur         # writing
        T_F1 = T_W1 + 0.2                                         # flip back to us
        S.set(t, "hold_front", "dead_stare", dur=0.0)
        if write_at is not None:
            S.set(T_F0, "hold_front", "dead_stare", dur=0.3, look=(0.3, 0.9), tilt=0.06, lid=0.42)
            S.set(T_F1 + 0.3, "hold_front", "dead_stare", dur=0.3, look=(0.0, 0.0), tilt=0.0)
            S.sfx(T_F0, "flip", 0.06); S.sfx(T_W0, "scribble", 0.07, dur=write_dur); S.sfx(T_F1, "flip", 0.06)
        def flip(tt):        # 1 = message to us, 0 = turned to him
            return 1.0 - ramp(tt, T_F0, T_F0 + 0.45) + ramp(tt, T_F1, T_F1 + 0.45)
        def board_c(tt):
            f = flip(tt); lift = -22 * math.sin(math.pi * f) if 0.02 < f < 0.98 else 0.0
            return (HOLD[0], HOLD[1] + 4 * math.sin(tt * 0.9) + lift)
        def writing(tt): return ramp(tt, T_W0, T_W0 + 0.1) * (1 - ramp(tt, T_W1 - 0.1, T_W1))
        def pen_w(tt): return ramp(tt, T_W0 - 0.15, T_W0) * (1 - ramp(tt, T_W1, T_W1 + 0.15))
        def hk(tt, p):
            if not (t <= tt < t + dur): return p
            cx, cy = board_c(tt); hw = max(60, BW * abs(math.cos(math.pi * flip(tt))) / 2)
            p["lhand"] = (cx - hw - 2, cy - 80); p["lelb"] = (cx - hw + 30, cy - 200)
            p["rhand"] = (cx + hw + 2, cy - 80); p["relb"] = (cx + hw - 30, cy - 200)
            p["lhand_t"] = p["rhand_t"] = "grip"
            w = pen_w(tt)
            if w > 0:                       # writes on the face turned to him, behind the top edge (only the pen shows)
                top = cy - BH / 2; k = writing(tt)
                jx = (30 * math.sin(tt * 19) + 14 * math.sin(tt * 7.3)) * k
                jy = (8 * math.sin(tt * 29) + 5 * math.sin(tt * 11)) * k
                p["rhand"] = lerp(p["rhand"], (cx + 90 + jx, top + 28 + jy), w); p["relb"] = (cx + 170, top + 120)
                if w > 0.3: p["rhand_t"] = "none"
            return p
        S._hook(hk)
        def pr(cr, tt, p, layer):
            if layer != "front" or not (t <= tt < t + dur): return
            cx, cy = board_c(tt)
            front.extra = extra if (extra and tt >= T_F1) else extra_shown     # yesterday's line until the flip back
            front.reveal = 1.0 if front.extra else 0.0
            if pen_w(tt) > 0.3:
                hx, hy = p["rhand"]; L.draw_pen(cr, hx, hy - 18, ang=0.3)
            L.draw_clipboard(cr, cx, cy, BW, BH, flip=flip(tt), front=front)
            L.draw_grips(cr, p)
        S._prop(pr)
        if push:
            S.camera(t, 540 + ox, 1000, 1.22, 0.0)
            S.camera(t + 0.5, 540 + ox, 1015, 1.34, max(1.0, dur - 1.0))
        S.t = t + dur
        return self

    # ------------------------------------------------------------- THE ASK (standard ending)
    def the_ask(self, t, text_lines=("TELL ME", "WHAT TO DO", "NEXT IN THE", "COMMENTS"), hold=10.0, push=True,
                mood="deadpan", keep=None):
        """digs at his hip (no pocket drawn) -> clipboard keeps coming -> POP -> write -> flip -> hopeful hold.
        Starts from a standing rest at body offset self.x. ~9.5 s + hold."""
        ox = self.x
        BW, BH = 470, 560
        HOLD = (540 + ox, 1120)
        POCKET = (588 + ox, 1092)
        A, C_, B = POCKET, (690 + ox, 860), (720 + ox, 520)
        T_POCKET, T_REACH, T_PULL, T_POP = t + 0.2, t + 0.35, t + 1.35, t + 2.45
        T_DOWN, T_PEN, T_W0, T_W1, T_FLIP = t + 2.75, t + 3.2, t + 3.45, t + 5.7, t + 6.35
        T_HOLD = t + 6.9
        S = self
        kp = dict(keep or {})            # persistent look (soaked, sooty...) carried through the ask
        if mood == "cute":
            S.set(t, "stand", "thinking", dur=0.25, look=(0.4, 0.8), tilt=0.08)
            S.set(T_POCKET + 0.05, "stand", "surprised", dur=0.1, ease="snap", look=(0.4, 0.8), eyescale=1.06, open=0.3)
            S.set(T_POCKET + 0.25, "stand", "concentrating", dur=0.2, look=(0.4, 0.8), tilt=0.1)
            S.set(T_PULL - 0.1, "stand", "eager", dur=0.1, ease="snap", look=(0.45, 0.3))
            S.set(T_PULL + 0.05, "stand", "surprised", dur=0.8, look=(0.5, -0.8), eyescale=1.08, open=0.4)
            S.set(T_POP + 0.02, "stand", "delighted", dur=0.1, ease="snap", look=(0.3, -0.4))
            S.set(T_DOWN + 0.1, "hold_front", "happy", dur=0.3, look=(0.0, 0.4))
            S.set(T_W0, "hold_front", "concentrating", dur=0.25, look=(0.4, 0.9), tilt=0.08)
            S.set(T_W1 + 0.1, "hold_front", "proud", dur=0.2, look=(0.0, 0.6))
            S.set(T_FLIP, "hold_front", "eager", dur=0.25)
            S.set(T_HOLD, "hold_front", "hopeful", dur=0.3)
            S.set(T_HOLD + hold * 0.25, "hold_front", "pleading", dur=0.5)
            S.set(T_HOLD + hold * 0.4, "hold_front", "shy", dur=0.35, blush=1.0, smile=0.6)
            S.set(T_HOLD + hold * 0.55, "hold_front", "pleading", dur=0.8)
            S.set(T_HOLD + hold * 0.75, "hold_front", "hopeful", dur=0.5, tilt=0.1)
            S.set(T_HOLD + hold * 0.88, "hold_front", "eager", dur=0.3, tilt=0.03, smile=0.8)
            hops = [(T_HOLD + 0.5, 14), (T_HOLD + 0.9, 14), (T_HOLD + hold * 0.88 + 0.2, 8), (T_HOLD + hold * 0.88 + 0.6, 8)]
            S.blink(T_DOWN + 0.25, T_HOLD - 0.3, T_HOLD + hold * 0.2, T_HOLD + hold * 0.5, T_HOLD + hold * 0.52, T_HOLD + hold * 0.7, T_HOLD + hold * 0.98)
            g_pop, g_scr, g_flip = 0.22, 0.16, 0.18
        else:                            # deadpan: no hops, no blush, no pleading. eyes lead, the head follows.
            S.set(t, "stand", "deadpan", dur=0.45, look=(0.35, 0.9), tilt=0.05, **kp)
            S.set(T_PULL - 0.05, "stand", "deadpan", dur=0.5, look=(0.45, -0.5), tilt=-0.02, **kp)
            S.set(T_POP + 0.1, "stand", "deadpan", dur=0.4, look=(0.25, -0.2), brow=0.15, **kp)
            S.set(T_DOWN + 0.1, "hold_front", "deadpan", dur=0.45, look=(0.0, 0.3), **kp)
            S.set(T_W0, "hold_front", "deadpan", dur=0.35, look=(0.35, 0.95), lid=0.45, tilt=0.06, **kp)
            S.set(T_W1 + 0.15, "hold_front", "deadpan", dur=0.4, look=(0.0, 0.0), **kp)
            S.set(T_HOLD, "hold_front", "dead_stare", dur=0.6, **kp)
            S.set(T_HOLD + hold * 0.45, "hold_front", "dead_stare", dur=0.5, look=(0.0, 0.85), **kp)   # glances at his sign
            S.set(T_HOLD + hold * 0.45 + 1.1, "hold_front", "dead_stare", dur=0.4, look=(0.0, 0.0), **kp)
            S.set(T_HOLD + hold * 0.86, "hold_front", "dead_stare", dur=0.35, lid=1.0, **kp)        # one slow blink
            S.set(T_HOLD + hold * 0.86 + 0.45, "hold_front", "dead_stare", dur=0.4, **kp)
            hops = []
            S.blink(T_DOWN + 0.5, T_HOLD + hold * 0.2)
            g_pop, g_scr, g_flip = 0.1, 0.07, 0.07
        if push and not self.card_on:
            S.camera(T_HOLD, 540 + ox, 1010, 1.26, 3.0)
            S.camera(T_HOLD + hold * 0.55, 540 + ox, 1020, 1.36, 2.0)
        elif push:
            S.camera(T_HOLD, 540 + ox, 940, 1.18, 3.0)
            S.camera(T_HOLD + hold * 0.55, 540 + ox, 950, 1.23, 2.0)
        S.sfx(T_POP, "pop", g_pop); S.sfx(T_W0, "scribble", g_scr, dur=T_W1 - T_W0); S.sfx(T_FLIP, "flip", g_flip)

        def hopv(tt): return sum(h * pulse(tt, t0, 0.09) for t0, h in hops)
        def bez(u): return ((1 - u) ** 2 * A[0] + 2 * (1 - u) * u * C_[0] + u * u * B[0], (1 - u) ** 2 * A[1] + 2 * (1 - u) * u * C_[1] + u * u * B[1])
        def pull_hand(tt): return bez(ramp(tt, T_PULL, T_POP))
        def board(tt):
            if tt < T_PULL: return None
            if tt < T_POP: return dict(mode="narrow", a=POCKET, b=pull_hand(tt))
            top_c = (B[0] - 30, B[1] + BH / 2 - 10)
            if tt < T_POP + 0.25:
                s = back_out((tt - T_POP) / 0.22, 1.8)
                return dict(mode="full", c=top_c, w=70 + (BW - 70) * s, flip=0.0, layer="back")
            c = lerp(top_c, HOLD, ramp(tt, T_POP + 0.25, T_DOWN + 0.1))
            f = ramp(tt, T_FLIP, T_FLIP + 0.5)
            lift = -26 * math.sin(math.pi * f) - 16 * f
            return dict(mode="full", c=(c[0], c[1] + lift - hopv(tt)), w=BW, flip=f, layer="back" if tt < T_DOWN + 0.08 else "front")
        def writing(tt): return ramp(tt, T_W0, T_W0 + 0.1) * (1 - ramp(tt, T_W1 - 0.1, T_W1))
        def pen_w(tt): return ramp(tt, T_PEN, T_PEN + 0.2) * (1 - ramp(tt, T_W1 + 0.05, T_W1 + 0.25))
        FRONT = L.sign_front(" ".join(text_lines), lines=list(text_lines))

        def hk(tt, p):
            if tt < t: return p
            hv = hopv(tt)
            if hv > 0.05:
                for k in L.JOINTS: p[k] = (p[k][0], p[k][1] - hv)
            if T_REACH <= tt < T_PULL:
                u = ramp(tt, T_REACH, T_REACH + 0.25)          # hand to the hip, digs around (visible, no pocket)
                dig = ramp(tt, T_REACH + 0.25, T_REACH + 0.35) * (1 - ramp(tt, T_PULL - 0.15, T_PULL - 0.05))
                p["rhand"] = lerp(p["rhand"], (POCKET[0] + 14 * math.sin(tt * 24) * dig, POCKET[1] + 6 * math.sin(tt * 31) * dig), u)
            if T_PULL <= tt < T_POP: p["rhand"] = pull_hand(tt); p["rhand_t"] = "none"
            if T_POP <= tt < T_POP + 0.3: p["rhand"] = (B[0] - 5, B[1] + 8)
            b = board(tt)
            if b and b["mode"] == "full" and tt >= T_POP + 0.25:
                u = ramp(tt, T_POP + 0.25, T_DOWN)
                cx, cy = b["c"]; hw = max(60, b["w"] * abs(math.cos(math.pi * b["flip"])) / 2)
                p["lhand"] = lerp(p["lhand"], (cx - hw - 2, cy - 80), u); p["lelb"] = (cx - hw + 30, cy - 200)
                p["rhand"] = lerp(p["rhand"], (cx + hw + 2, cy - 80), u); p["relb"] = (cx + hw - 30, cy - 200)
                if u > 0.5: p["lhand_t"] = p["rhand_t"] = "grip"
                w = pen_w(tt)
                if w > 0:
                    top = cy - BH / 2; k = writing(tt)
                    jx = (30 * math.sin(tt * 19) + 14 * math.sin(tt * 7.3)) * k
                    jy = (8 * math.sin(tt * 29) + 5 * math.sin(tt * 11)) * k
                    p["rhand"] = lerp(p["rhand"], (cx + 90 + jx, top + 28 + jy), w); p["relb"] = (cx + 170, top + 120)
                    if w > 0.3: p["rhand_t"] = "none"
            return p
        def pr(cr, tt, p, layer):
            if tt < t: return
            b = board(tt)
            if layer == "front" and T_POCKET <= tt < T_DOWN + 0.2:
                u = ramp(tt, T_POCKET, T_POCKET + 0.15, "linear") * (1 - ramp(tt, T_DOWN, T_DOWN + 0.15, "linear"))
                if b and b["mode"] == "narrow":
                    (ax, ay), (bx, by) = b["a"], b["b"]
                    ang = math.atan2(by - ay, bx - ax); L_ = math.hypot(bx - ax, by - ay)
                    cr.save(); cr.translate(ax, ay); cr.rotate(ang); L.sketch_rect(cr, -10, -32, L_ + 6, 32, 7, sid=300); cr.restore()
                if b and b["mode"] == "narrow":
                    h = pull_hand(tt); L.draw_hand(cr, h, (h[0] - 30, h[1] + 60), "mitt", 1, sid=450)
            if b and b["mode"] == "full" and b["layer"] == layer:
                if layer == "front" and pen_w(tt) > 0.3:
                    hx, hy = p["rhand"]; L.draw_pen(cr, hx, hy - 18, ang=0.3)
                L.draw_clipboard(cr, b["c"][0], b["c"][1], b["w"], BH, flip=b["flip"], front=FRONT)
                if layer == "back" and tt < T_POP + 0.3:
                    L.burst_lines(cr, b["c"][0], b["c"][1], (tt - T_POP) / 0.4, r0=BW * 0.45, r1=BW * 0.68, n=10, sid=7)
            if layer == "front": L.draw_grips(cr, p)
        self._hook(hk); self._prop(pr)
        self.t = T_HOLD + hold
        return self

    # ------------------------------------------------------------- render
    def build(self, duration=None):
        dur = duration or self.t
        hooks, props, ovs, bgs = list(self.hooks), list(self.props), list(self.overlays), list(self.bgs)
        card = self.card_on
        def hook(t, p):
            for h in hooks: p = h(t, p)
            if card:
                for k in CARD_FX_OFF: p[k] = 0.0
            return p
        def bg(cr, t):
            for f in bgs: f(cr, t)
        def prop(cr, t, p, layer):
            for f in props: f(cr, t, p, layer)
        def overlay(cr, t):
            for f in ovs: f(cr, t)
        bl = sorted(self.blinks) if self.blinks else None
        if bl is not None and getattr(self, "auto_blinks", True):   # add natural blinks in long gaps
            extra, last = [], 0.0
            for b in bl + [dur]:
                while b - last > 4.0: last += 3.2; extra.append(last)
                last = b
            bl = sorted(bl + extra)
        L.configure(duration=dur, pose_track=Track(self.keys), x_track=Track(self.xkeys),
                    cam_track=_Cam(Track(self.camkeys), self.shakes), props=prop, pose_hook=hook,
                    overlay=overlay if ovs else None, sfx=self.sfxs, blinks=bl, floor=self.floor,
                    background=bg if bgs else None, cuts=self.cuts)
        return dur

    def render(self, out, duration=None):
        self.build(duration); L.main(out)
