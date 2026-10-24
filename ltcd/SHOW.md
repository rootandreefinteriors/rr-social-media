# LET THE COMMENTS DECIDE — show bible

TikTok + Instagram: **@let.the.comments.decide**. Owner: Justin. Claude makes every episode.
Daily loop: **post 7:00 PM ET → comments come in → 3:00 PM ET next day: comment sweep + make the next episode → 7:00 PM post.**

## The character & world
- A basic, nameless stick figure with a LOT of face (see `design/sheet_*.png`, built from `engine/character.py`):
  big cartoon eyes (white, black pupils, shine, eyelids), thick expressive brows, a mouth with many shapes, ONE bouncy
  hair curl on top (his signature silhouette), rubber-hose limbs, mitten hands with gestures, bean-shaped feet.
  No clothes, no pockets (he pulls things out of where a pocket would be). He never speaks. NOT Nigel.
- **Personality:** eager, earnest, hopeful, a little shy. He genuinely wants to do what you tell him and wants you
  to like it. He commits 100% to every instruction, however silly — that sincerity is the joke and the heart.
  Small acting beats sell him: shy wave, blush, hopeful pupils, tongue out when concentrating, proud little nod.
- **Acting toolkit:** `pose(body, face, **overrides)` with POSES (31 body poses), EXPR (47 expressions), eyes
  styles (happy, closed, x, spiral, heart, star, dot, wide), 13 mouth styles, extras (tears, sweat drop, anger vein,
  gloom, blush, teary), symbols (? ! Zzz hearts dizzy-stars idea-bulb steam nervous-lines notes sparkles swirl),
  hand gestures (mitt fist open point poke thumbs peace grab flat grip), head turn (front, 3/4, profile, back),
  procedural cycles (walk, run, sneak/tiptoe, shiver, laugh, sob, dance, sleep, fidget), lean, squash/stretch, hop,
  and Track easings (snap, back = overshoot, elastic, bounce) for cartoon timing. Use anticipation → action →
  overshoot/settle on every big move. Keep him moving — never a dead stretch.
- Same hand-drawn line style as Nigel: black ink on white paper, line boil, paper grain, a floor line. The default
  world is an empty white void. Frame him big (camera zoom ~1.2+) so faces read on a phone.
## Episode types
1. **Episode 1 — "the ask"** (`episodes/ep001`). Walk in from left, turn, pull clipboard, scribble, flip, hold sign,
   blink and stare until the hard cut.
2. **Comment episode** — he does what the winning comment says, in this style, then ends with the clipboard beat.
   - **Length: average ~60 s, never more than 75 s.** Simple requests can be drawn out for comedy; complicated ones
     get a simplified, funny take. Both are part of the humour.
   - The winning comment is pinned **top-right** as a recreated comment card (`draw_comment_card`): @username, the
     comment text, the like count. Visible for the whole episode (it may shrink a little after the first seconds).
3. **Waiting episode** — when there is no qualifying comment. It picks up where the last episode left off: he is still
   standing there with his sign, waiting. Every waiting episode must be **unique**, and they get **more ridiculous the
   longer the drought lasts** (Mario 64 idle energy): foot tapping → pacing with the sign → yawning → falling asleep
   standing up → it starts raining on just him → cobwebs → a tumbleweed rolls through → he writes "DAY 4" on the
   sign → he grows a long beard → vines grow up the sign → seasons change around him → a tiny moon orbits his head…
   Always ends with him re-presenting the sign (TELL ME WHAT TO DO NEXT IN THE COMMENTS). 20–45 s is fine.

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
    without the IP (e.g. "be Spider-Man" → a generic superhero), otherwise skip it.
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
