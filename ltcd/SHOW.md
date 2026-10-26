# LET THE COMMENTS DECIDE — show bible

TikTok + Instagram: **@let.the.comments.decide**. Owner: Justin. Claude makes every episode.
Daily loop: **post 7:00 PM ET → comments come in → 3:00 PM ET next day: comment sweep + make the next episode → 7:00 PM post.**

## The character & world
- A basic, nameless stick figure with a LOT of face (see `design/sheet_*.png`, built from `engine/character.py`):
  big cartoon eyes (white, black pupils, shine, eyelids), thick expressive brows, a mouth with many shapes, ONE bouncy
  hair curl on top (his signature silhouette), rubber-hose limbs, mitten hands with gestures, bean-shaped feet.
  No clothes, no pockets — he digs his hand around at his hip and pulls things out of nowhere (never draw a pocket). He never speaks. NOT Nigel.
- **Tone (user note 2026-10-24 — overrides older "cute" wording): Adult Swim, for teens and adults** (expect an
  edgelord audience). NOT childish: no hearts, sparkles, blushing, star eyes, happy hops, thumbs-up "yay" beats.
  Deadpan, dry, absurd, a little dark. He is a dead-eyed hostage of the comments: he does EXACTLY what they say with
  total, joyless commitment, and the humour comes from his flat reactions to insane situations, uncomfortable holds,
  hard cuts, and a slightly dark absurd escalation (something bigger than him shows up; the joke turns on him).
  Still PG-13 (rules below). Reference: `tests/comment_tests/t1_ramen_v2` — APPROVED direction (user, 2026-10-24: "this is the right direction for now").
- **Acting (user note: emotions felt canned, fired at the wrong time, disconnected):** reactions come AFTER the thing
  that causes them (~0.3 s), eyes move first, then the head, then the body. Emotions BUILD out of the situation
  (ramp parameters over seconds: heat_fill, sweat, twitch, pupil, quiver, tear1, breath_rate) instead of switching
  presets. Default faces: `deadpan`, `dead_stare`, `resigned`, `holding_it`. Few blinks during a stare. Long holds
  are fine if something small keeps changing (a drip, a twitch, steam, a slow camera creep).
- **Animation (user note: too rigid/stiff/disconnected/amateur):** the engine now gives every joint follow-through
  (drag + overshoot), soft curved limbs, breathing and eye micro-movements — let them work: prefer fewer, longer,
  well-timed moves over many snappy ones. Physical contact must be real (if he touches, tickles, grabs or is grabbed,
  the parts actually meet). Use HARD CUTS (`S.cut`) instead of animating awkward in-betweens (climbing in/out, lifts).
- **Acting toolkit:** `pose(body, face, **overrides)` with POSES, EXPR (incl. the deadpan set), eye styles, mouth
  styles, extras (heat_fill, tear1, twitch, quiver, curl_up, sweat, tears, soot, frizz), procedural cycles, lean,
  squash/stretch, and Track easings. The old cute vocabulary (blush, hearts, starstruck, pleading) is retired unless a
  comment explicitly calls for it, and even then play it straight.
- Same hand-drawn line style as Nigel: black ink on white paper, line boil, paper grain, a floor line. The default
  world is an empty white void. Frame him big (camera zoom ~1.2+) so faces read on a phone.
## Episode types
1. **Episode 1 — "the ask"** (`episodes/ep001`, already posted in the older cuter style). The ending of every
   episode is now the deadpan ask (`S.the_ask(..., mood="deadpan")`, the default): dig at hip, clipboard, scribble,
   flip, dead stare, one slow blink, cut.
2. **Comment episode** — he does what the winning comment says, in this style, then ends with the clipboard beat.
   - **Length: average ~60 s, never more than 75 s.** Simple requests can be drawn out for comedy; complicated ones
     get a simplified, funny take. Both are part of the humour.
   - The winning comment is pinned **top-right** as a recreated comment card (`draw_comment_card`): @username, the
     comment text, the like count. Visible for the whole episode (it may shrink a little after the first seconds).
3. **Waiting episode** — when there is no qualifying comment. (User note 2026-10-24, overrides the older "Mario 64
   idle / rain / cobwebs / tumbleweed" ideas: "the focus needs to be on the message when no one has commented yet, not
   gimmicky animations that don't make sense".)
   - **The message is the star.** He stands centre holding the sign up to us — TELL ME WHAT TO DO NEXT IN THE COMMENTS
     — readable the whole time. Dead stare, breathing, the odd blink, a slow camera creep. That's the episode.
   - **At most ONE small beat, and it must add to the message:** he turns the sign to himself, writes one short line
     under the message, turns it back (`S.hold_sign(..., extra="I'LL WAIT.", write_at=...)`). Some days: no beat at all.
   - **Escalation over a drought = only what's on the sign and his posture.** Each waiting day the sign keeps
     yesterday's line (`extra_shown=`) and he writes a new one: e.g. `I'LL WAIT.` → `STILL HERE.` → `DAY 4.` →
     `ANY TIME NOW.` → `I DON'T BLINK MUCH.` Short (≤ 20 characters), deadpan, plain words. Posture can slump a little
     (small `lean`, lower `lid`) as the streak grows. That's all.
   - **Never:** props, symbols or effects that need explaining (no chalk outlines, lying under the sign, rain, cobwebs,
     tumbleweeds, beards, seasons, moons…), sitting/lying/hiding the sign, or anything that covers the message.
   - 18–25 s. Hard cut at the end. Reference: `tests/waiting_ref/episode.py` (copy it, change the line).

## Choosing the comment (the 3 PM sweep)
- Pool: comments on every post published since the last comment episode (TikTok + Instagram), posted before the sweep,
  not already used, not written by our own account.
- Rank by likes (most first); tie → earliest. Take the **highest-ranked comment that qualifies**. If none qualify →
  waiting episode.
- **Qualifies only if all true:**
  - PG-13 / ESRB T. No nudity or sexual content (cartoon kiss / hearts OK). No graphic violence or gore
    (Looney Tunes slapstick OK: anvils, pies, bonks, ACME-style cartoon bombs and comically huge cartoon explosions
    with soot faces — even a cartoon "nuke" as a big round ACME bomb. NOT OK: realistic weapons, any how-to detail,
    real places/people/groups as targets, or anything referencing a real attack, war or disaster).
  - No real people (celebrities, politicians, creators, the commenter's friends) — no likenesses, no names on screen.
  - No swearing or slurs, even written, even misspelled/disguised.
  - Nothing racist, sexist, homophobic, transphobic, ableist, or otherwise demeaning to any group.
  - No politics, religion, current tragedies, drugs/alcohol/vaping, weapons glorification, self-harm, suicide, or
    dangerous challenges (even as a joke).
  - No copyrighted characters, brands or logos — make a generic version instead only if the request still works
    without the IP (e.g. "be Spider-Man" → a generic superhero), otherwise skip it. **User note 2026-10-26: make the
    generic version as close as you can without violating copyright** — the recognisable look and feel (block
    textures, pixel hearts, a purple portal, a black dragon for a block game) but no logos, game/brand names on
    screen, or the actual named characters (reference: `episodes/ep004` "Beat Mc in hardcore mode").
  - Do what the comment actually asks: "beat X" means he wins (deadpan), not a fail gag.
  - No links, ads, "follow me", spam, or personal info. No requests aimed at harassing someone.
  - Must be doable as a 75-second silent cartoon.
- **Don't get trolled.** Skip bait designed to make the account look bad, inside jokes/code words, coordinated spam,
  "do something that secretly means X", requests that only work as a slur/innuendo, and anything you'd be
  uncomfortable seeing pinned on screen. When in doubt, skip it. Reward legitimate, fun, creative contributions.
- The pinned comment card shows the comment **as written** (only if it qualifies — the card itself must pass the rules).
  Long comments may be trimmed with "…".

## Continuity (the comments stick — with limits)
- The world persists between episodes: things he gets/learns/becomes can stay. That is part of the draw.
- **Keep it readable: at most ~3 persistent "companions/major props" at once** (pets, vehicles, a house…). When a new
  one would exceed that — or when two clearly clash — use a **cartoon consequence**: e.g. "get a dog" then "get a cat"
  → the dog vanishes in a POOF as the cat appears ("getting the cat meant giving up the dog"). Other tools: things
  wander off, get eaten, shrink, fly away, get traded, turn out to be cardboard cut-outs. Make removals funny.
- Small things (a hat, a scar from the anvil, a plant) can come and go freely. Not every element needs to appear in
  every episode — bring back old things as callbacks when it's funny.
- Track everything in `STATE.json` (`world`) so the next episode knows what exists.

## Posting
- Both platforms, same video, **7:00 PM America/New_York** (offset -04:00 until 2026-11-01, then -05:00).
- Caption: `day N · tell me what to do next 👇` (+ `#letthecommentsdecide #stickfigure #animation`). For comment
  episodes: `day N · @username said: "<comment, trimmed>" · what next? 👇`.
- Buffer account = `Buffer_Comments` connector (org 6ad3b32d59096eb0b75abe28; TikTok 6ad3bc77778b240e2f3cdf83,
  Instagram 6ad3bc60778b240e2f3cde9b — Instagram metadata `{type:"reel", shouldShareToFeed:true}`). AI label OFF
  (`isAiGenerated:false` on both).
- Videos are hosted in this repo under `ltcd/videos/` and passed to Buffer as raw.githubusercontent.com URLs.
