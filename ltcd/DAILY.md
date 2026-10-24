# Daily routine — runs 3:00 PM ET in the cloud (Claude Code routine)

You are the sole producer of **Let the comments decide**. Read `ltcd/SHOW.md` (the rules) and `ltcd/STATE.json`
(where the story is) first. Work inside this repo. Be careful and finish: tonight's 7 PM post depends on you.

## 0. Setup (every run — fresh machine)
```
sudo apt-get update -qq && sudo apt-get install -y -qq libcairo2-dev pkg-config python3-dev ffmpeg >/dev/null
pip install -q pycairo numpy pillow  ||  pip install -q --break-system-packages pycairo numpy pillow
git config user.name "Claude (LTCD routine)"; git config user.email "noreply@anthropic.com"
```

## 1. Collect comments (Porter connector)
- `mcp__Porter_Metrics__list_accounts(connector="tiktok-insights")` → the `let.the.comments.decide` account id.
- `execute_action(action="tiktok_insights.video_list", ...)` → recent videos (item_id, caption, create_time).
- For every video posted since day `STATE.ask_since_day` (i.e. since the last comment episode): `execute_action(
  action="tiktok_insights.comment_list", params={video_id, max_count:30, sort_field:"likes"...})` and page with
  `cursor` until done. Keep: text, likes, username, create_time, status, owner. Drop owner (our own) and HIDDEN ones.
- Same for Instagram if `instagram-insights` has an account connected (`instagram_insights.media_list` /
  `instagram_insights.comment_list`). If not connected, note it in the summary and continue with TikTok only.
- Only comments created before now. Drop any whose text matches an entry in `STATE.used_comments`.

## 2. Pick the winner
- Rank by likes desc, tie → earliest. Walk down the list; the first comment that passes **every** rule in SHOW.md
  ("Qualifies only if all true" + "Don't get trolled") wins. Write down why each higher-ranked one was skipped.
- No winner → this is a **waiting episode**.

## 3. Write the episode
- New folder `ltcd/episodes/epNNN/` (NNN = STATE.day + 1, zero-padded). **Build it with `engine/moves.py`** (the
  `Scene` builder) — never hand-place joints. Working examples to copy: `ltcd/tests/comment_tests/t1_ramen`,
  `t2_nuke`, `t3_dino` (and `ltcd/tests/moves_smoke`). Key calls:
  `S = M.Scene(x0=...)`, `S.card(user, text, likes)`, `S.read_card(t, react, lines)`, `S.walk_to/run_to`,
  gestures (`wave nod shake_head shrug thumbs_up facepalm think cheer jump dance sit stand sleep hop`),
  `S.set(t, body, face, **overrides)` for one-off acting, `S.pocket_pull(t, name, drawer, land, narrow_w=0, held=...)`
  to produce any object, `S.place / hide / poof_away`, `S.prop / hook / background / overlay`, `S.shake`, `S.flash`,
  `S.sfx`, and always `S.the_ask(S.t, hold=8-10)` last. Props library: `engine/objects.py` (tub, ACME bomb, fish,
  ice-cream cone, feather, snorkel, friendly T. rex `draw_dino`, water, splash, rain, build cloud, crater).
  Add new props to objects.py (keep old ones working). Custom one-episode poses go in `L.POSES[...]` in episode.py.
- **The pull gag (signature):** he digs his hand around at his hip and pulls the thing out of nowhere — **NO pocket
  is ever drawn** (user note 2026-10-24: "don't make an actual pocket, just have him dig his hand around and pull it
  out"). `pocket_pull` and `the_ask` already do this; don't reintroduce a pocket.
- **Comment episode:** he does what the comment says, cartoon style. Pin the comment card (`S.card`) for the whole
  episode — it auto-shrinks long comments; keep his head, his fx and every prop BELOW it (if something tall must
  appear, widen the camera like t3_dino: `S.camkeys[0] = (0, (540, 840, 0.9), 0)` and `the_ask(..., push=False)`).
  Average ~60 s, max 75 s. Continuity per SHOW.md (≤3 major persistent things; use cartoon consequences to remove
  things). End with `the_ask` (dig at hip -> clipboard -> scribble -> flip: TELL ME WHAT TO DO NEXT IN THE COMMENTS).
- **Waiting episode:** picks up from the last scene; he's still waiting with the sign. Unique each time and more
  ridiculous as `STATE.waiting_streak` grows. 20–45 s. Ends re-presenting the sign.
- Keep everything inside the safe zone (x 60–920, y 200–1480 on screen). Big readable shapes. Lots of motion —
  no dead stretches. Jumps: use the `cannonball` pose + low hops (~175) so he never flies up behind the card; set
  `nowalk=1` for anything airborne/sliding.
- **Sound is subtle and sparse** (user note): one soft effect on KEY actions only (gains 0.03–0.12; a big boom up to
  0.5 is the loudest thing in an episode). No music. No dialogue (written words OK, no swearing).

## 4. Check, then render
- `python episode.py --still <6-10 times>` → look at every still (Read the PNGs). Fix anything unreadable, clipped,
  overlapping the comment card, or boring. Then `python episode.py` (writes the mp4).
- Verify with ffprobe: 1080x1920, 30 fps, duration ≤ 75 s. Pull 3 frames from the mp4 and look at them.
- Copy to `ltcd/videos/dayNNN.mp4` (NNN = new day). Delete still_*.png and mix.wav.

## 5. Publish (only after the video is verified)
- Commit episode folder + video + updated STATE.json + LOG.md line; `git push origin HEAD:main`.
  If main is rejected, push the current branch and use that branch name in the raw URL.
- `curl -sI https://raw.githubusercontent.com/rootandreefinteriors/rr-social-media/<branch>/ltcd/videos/dayNNN.mp4`
  must return 200.
- `mcp__Buffer_Comments__create_post` twice (TikTok 6ad3bc77778b240e2f3cdf83 and Instagram 6ad3bc60778b240e2f3cde9b),
  `schedulingType:"automatic"`, `mode:"customScheduled"`, `dueAt: <today>T19:00:00-04:00` (-05:00 from 2026-11-01),
  caption per SHOW.md, `assets:[{video:{url:<raw url>}}]`, metadata TikTok `{tiktok:{isAiGenerated:false}}`,
  Instagram `{instagram:{type:"reel", shouldShareToFeed:true, isAiGenerated:false}}`. Check both come back `scheduled`.

## 6. Update state
- STATE.json: `day` += 1; `last_episode` (type, folder, video, posted_at, buffer post ids); for a comment episode:
  `ask_since_day` = new day, `waiting_streak` = 0, append the comment to `used_comments`, update `world`; for a
  waiting episode: `waiting_streak` += 1. Append to `history` (one-line summary).
- Append a line to `ltcd/LOG.md`: date, day, type, winning comment (+ likes) or "no qualifying comment", skipped
  comments with reasons, video URL, Buffer post ids. Commit + push.

## 7. Report
Short plain-language summary for Justin (not a developer): what tonight's episode is, the winning comment (or why
none qualified), and anything that needs him (connector sign-ins, errors). Send it as a push notification too.

## Never
- Never post anything that fails SHOW.md rules. Never delete posts. Never post immediately (always 7 PM schedule).
- If something breaks and you can't make a new episode, schedule a re-post of the previous video at 7 PM with
  caption `day N · still waiting 👇` and report the problem — the show must not skip a day.
