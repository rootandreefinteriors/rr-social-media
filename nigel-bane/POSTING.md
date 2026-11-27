# Posting schedule — TikTok @nigel.bane (via Buffer)

- **Time:** 9:00 PM America/New_York, one per day, every day. (Late-night winding-down scroll; TikTok's evening
  peak is ~7–11 PM ET, and 9 PM ET is still prime time on the West Coast.)
- **Caption:** tally + one lowercase -ing word, nothing else (see BIBLE "Post captions").
- **Cover (from 2026-10-23):** every post gets a chosen cover frame (`thumbnailOffset`, ms): distinctive pose, eyes open,
  no caption words on screen. Helper: `engine/cover_gaps.py`. Same cover on TikTok and IG.
- **AI disclosure:** OFF (`isAiGenerated: false`) — user decision 2026-10-10.
- **Platforms:** TikTok + Instagram Reel, same video and caption, same time. (IG Days 1–7 posted manually by the user.)
- **Buffer account (since 2026-10-17):** Nigel's own — MCP server `buffer-nigel`, org `6ad3b3027648d77341057da5`.
  TikTok channel `6ad3bd1a778b240e2f3ce589` · Instagram channel `6ad3bb3d778b240e2f3cd282`.
  (Days 1–7 went out from the old Root & Reef account, channel `6aca790f6a5c39ccb6744297`, now removed.)
- **Buffer free plan:** max 10 scheduled posts per account → 5 days ahead (TikTok + IG). Drafts don't count, so
  **every finished episode goes into Buffer immediately as two dated drafts** (TikTok + IG, `saveToDraft:true`,
  dueAt = its 9 PM slot). The daily 3 PM refill promotes them to scheduled as slots free (see automation/ACCOUNTS.md).
- **Video hosting:** public GitHub repo `rootandreefinteriors/rr-social-media`, folder `nigel-bane/` (local clone `C:/tmp/rr-social-media`).
  Upload copy: `ffmpeg -i <episode>.mp4 -c:v libx264 -preset slow -crf 21 -pix_fmt yuv420p -c:a copy -movflags +faststart nigel-bane/dayNNN.mp4`
  (~20 MB each), then git add/commit/push and pass
  `https://raw.githubusercontent.com/rootandreefinteriors/rr-social-media/main/nigel-bane/dayNNN.mp4` to Buffer.
  Note: this repo is public, so the link between @nigel.bane and Root & Reef is visible (user accepted this).
- **Scheduling calls** (`mcp__buffer-nigel__create_post`, schedulingType=automatic, mode=customScheduled,
  dueAt=YYYY-MM-DDT21:00:00-04:00 — use -05:00 after DST ends Nov 1, text=caption, assets=[{video:{url}}]):
  TikTok: metadata `{tiktok:{isAiGenerated:false}}` · IG: metadata `{instagram:{type:"reel",shouldShareToFeed:true,isAiGenerated:false}}`.

> **2026-10-23:** Day 13 missed its Oct 22 slot (laptop refill didn't run Oct 18–22). User chose to shift: Day 13 → Oct 23
> and every later day +1. **From Day 13 on: Day N posts on 2026-10-11 + (N−1) days.**

| Day | Post date (9 PM ET) | Upload | Caption | TikTok post | IG post | Status |
|---|---|---|---|---|---|---|
| 1 | 2026-10-10 | nigel-bane/day001.mp4 | `I arriving` | (old acct) | manual | sent |
| 2 | 2026-10-11 | nigel-bane/day002.mp4 | `II answering` | (old acct) | manual | sent |
| 3 | 2026-10-12 | nigel-bane/day003.mp4 | `III copying` | (old acct) | manual | sent |
| 4 | 2026-10-13 | nigel-bane/day004.mp4 | `IIII forgetting` | (old acct) | manual | sent |
| 5 | 2026-10-14 | nigel-bane/day005.mp4 | `IIIII rebuilding` | (old acct) | manual | sent |
| 6 | 2026-10-15 | nigel-bane/day006.mp4 | `IIIII I watching` | (old acct) | manual | sent |
| 7 | 2026-10-16 | nigel-bane/day007.mp4 | `IIIII II closing` | (old acct) | manual | sent |
| 8 | 2026-10-17 | nigel-bane/day008.mp4 | `IIIII III humming` | `6ad3bd96938409f1d09a8e1d` | `6ad3bd960a208cb3233274d7` | scheduled |
| 9 | 2026-10-18 | nigel-bane/day009.mp4 | `IIIII IIII returning` | `6ad3bedd938409f1d09ae073` | `6ad3bede769b4579348d974d` | scheduled |
| 10 | 2026-10-19 | nigel-bane/day010.mp4 | `IIIII IIIII deciding` | `6ad3bede938409f1d09ae0bd` | `6ad3bedf769b4579348d9789` | scheduled |
| 11 | 2026-10-20 | nigel-bane/day011.mp4 | `IIIII IIIII I hovering` | `6ad3bedf769b4579348d97cb` | `6ad3bee00a208cb32332bef8` | scheduled |
| 12 | 2026-10-21 | nigel-bane/day012.mp4 | `IIIII IIIII II staying` | `6ad3bee1938409f1d09ae180` | `6ad3bee10a208cb32332bf86` | scheduled |
| 13 | 2026-10-23 | nigel-bane/day013.mp4 | `IIIII IIIII III mirroring` | – | – | sent |
| 14 | 2026-10-24 | nigel-bane/day014.mp4 | `IIIII IIIII IIII posing` | `6ad3c0f9938409f1d09b2aa0` | `6ad3c0f90a208cb323330a60` | scheduled (shifted +1 day) · cover 49.8 s (empty room, bird watching where he went) |
| 15 | 2026-10-25 | nigel-bane/day015.mp4 | `IIIII IIIII IIIII leaving` | `6ad3c0faae173d6e00cc587c` | `6ad3c0fa0b0d72757aedb21d` | scheduled (shifted +1 day) · cover 40.0 s (hand to head, empty window) |
| 16 | 2026-10-26 | nigel-bane/day016.mp4 | `IIIII IIIII IIIII I repeating` | `6ad3c0fb0b0d72757aedb23e` | `6ad3c0fc769b4579348dea1e` | scheduled (shifted +1 day) · cover 16.4 s (tired fist, eyes going dark) |
| 17 | 2026-10-27 | nigel-bane/day017.mp4 | `IIIII IIIII IIIII II landing` | `6adc0c136887a2efc192880a` | `6adc0c146887a2efc1928836` | scheduled · cover 37.95 s (palm on the glass) |
| 18 | 2026-10-28 | nigel-bane/day018.mp4 | `IIIII IIIII IIIII III keeping` | `6adc1007e4be8a4d86365234` | `6adc10073d5b27036b60372a` | scheduled · cover 4.75 s (frozen mid-step, fly + spider in the web) |
| 19 | 2026-10-29 | nigel-bane/day019.mp4 (v2; Buffer uses `?v=2`) | `IIIII IIIII IIIII IIII knocking` | `6adc12e20b5343d0705ec1e3` | `6adc12e38b3d437ddc97d8b9` | dated draft · cover 8.4 s (shooing the moth from the web) |
| 20 | 2026-10-30 | nigel-bane/day020.mp4 | `IIIII IIIII IIIII IIIII listening` | `6adc198f0b5343d0706077d0` | `6adc198fbd33ce99c300c488` | dated draft · cover 50.3 s (bolt upright on the floor, staring at us) |
| 21 | 2026-10-31 | nigel-bane/day021.mp4 | `IIIII IIIII IIIII IIIII I stitching` | `6adc26810b5343d070635c69` | `6adc2681e4be8a4d863c0433` | dated draft · cover 50.2 s (extreme close-up of straining eyes) |
| 22 | 2026-11-01 | nigel-bane/day022.mp4 | `IIIII IIIII IIIII IIIII II drowning` | `6adc27de6887a2efc1995667` | `6adc27de0b5343d070639224` | dated draft (-05:00) · cover 45.0 s (eyes shut in the silence) |
| 23 | 2026-11-02 | nigel-bane/day023.mp4 | `IIIII IIIII IIIII IIIII III unraveling` | `6adc27dee4be8a4d863c2cf9` | `6adc27df3d5b27036b65f35a` | dated draft · cover 41.5 s (tiny in the white, window far behind) |
| 24 | 2026-11-03 | nigel-bane/day024.mp4 | `IIIII IIIII IIIII IIIII IIII flipping` | `6adc29018b3d437ddc9d3bc2` | `6adc2901bd33ce99c30434db` | dated draft · cover 53.0 s (eyes shut, reflection's shut too) |
| 25 | 2026-11-04 | nigel-bane/day025.mp4 | `IIIII IIIII IIIII IIIII IIIII guessing` | `6adc2a388b3d437ddc9d7331` | `6adc2a38bd33ce99c3046911` | dated draft · cover 47.4 s (waiting at the glass, fist raised) |
| 26 | 2026-11-05 | nigel-bane/day026.mp4 | `IIIII IIIII IIIII IIIII IIIII I loosening` | `6aed16d47b7e47e8f4f67b54` | `6aed16d4f3498efda759def2` | scheduled · cover 51.6 s (hand on the thread under the torn web) |
| 27 | 2026-11-06 | nigel-bane/day027.mp4 | `IIIII IIIII IIIII IIIII IIIII II spreading` | `6aed19f486fe9b83795f6b43` | `6aed19f407f945cca92d4175` | scheduled · cover 55.0 s (sitting beside the crack) |
| 28 | 2026-11-07 | nigel-bane/day028.mp4 | `IIIII IIIII IIIII IIIII IIIII III settling` | `6aed1afe86fe9b83795ffcb5` | `6aed1afec1e74b84e5b6380b` | scheduled · cover 55.2 s (turned to the dusk window) |
| 29 | 2026-11-08 | nigel-bane/day029.mp4 | `IIIII IIIII IIIII IIIII IIIII IIII mending` | `6aed1cc87b7e47e8f4f90264` | `6aed1cc986fe9b837960a890` | scheduled · cover 19.5 s (holding his breath as the tape corner lifts) |
| 30 | 2026-11-09 | nigel-bane/day030.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII searching` | `6aed1cd1c1e74b84e5b6e5c7` | `6aed1cd1dbada656bee1a1f4` | scheduled · cover 56.0 s (fingertip searching the clean glass) |
| 31 | 2026-11-10 | nigel-bane/day031.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII I inheriting` | `6af2a52bb59b34913a586042` | `6af2a52cd35dff5701dd3d20` | scheduled · cover 50.4 s (lifting the blank tag) · voice reused from the Nov 6 run |
| 32 | 2026-11-11 | nigel-bane/day032.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII II fitting` | `6af2a52cd35dff5701dd3d52` | `6af2a52dd35dff5701dd3d94` | scheduled · cover 31.0 s (hunched beside the chair) · voice reused · re-cut twice 2026-11-10 (pauses had cut into words, then split the "p" off "up"); Buffer uses `?v=3` |
| 33 | 2026-11-12 | nigel-bane/day033.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII III softening` | `6af2a52ee261c09acc9ec791` | `6af2a52e223aa16048ed2737` | scheduled · cover 55.3 s (hand on the chair back) · voice reused |
| 34 | 2026-11-13 | nigel-bane/day034.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIII anchoring` | `6af34caba80c88d576499ebd` | `6af34cab2d2fdb3b7dec41b3` | scheduled · cover 48.5 s (straining to rise from the chair) · re-cut without the chair creak |
| 35 | 2026-11-14 | nigel-bane/day035.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII creaking` | `6af34cac825741bba847b336` | `6af34cadeca53e2861f22218` | scheduled · cover 26.0 s (dark eyes after the steps stop) · DREAD |
| 36 | 2026-11-15 | nigel-bane/day036.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII I vacating` | `6af34cae94964d984f038ee4` | `6af34cafeca53e2861f222a4` | dated DRAFT (promoted by the daily refill as slots free) · cover 41.2 s (looking toward the mouse corner) |
| 37 | 2026-11-16 | nigel-bane/day037.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII II inching` | `6af47a437b2522ad6c452571` | `6af47a46c6fc3e4d41b49755` | scheduled · cover 54.2 s (his hand, the mouse a whisker away) · replaced 2026-11-12 (the first cut, "nearing"/Ceiling, moves to D40); Buffer uses `?v=2` |
| 38 | 2026-11-17 | nigel-bane/day038.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII III unblinking` | `6af47b9700263add00a7c1f6` | `6af47b997b2522ad6c4590bd` | scheduled · replaced 2026-11-12 (the first cut, "shedding"/Dust, was dropped); re-cut 2026-11-17 as one continuous shot, Buffer uses `?v=3` · cover 23.4 s (staring at the eyes under the chair) |
| 39 | 2026-11-18 | nigel-bane/day039.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIII outlasting` | `6af518bacb4c7286fd074e54` | `6af518bccb4c7286fd074ea8` | scheduled · re-cut 2026-11-17 as one continuous shot, Buffer uses `?v=2` · cover 48.0 s (the chair sliding out of frame behind him) · DREAD |
| 40 | 2026-11-19 | nigel-bane/day040.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII nearing` | `6afcb263ca5f4f8df9cef955` | `6afcb264b0028e70d9d2b381` | scheduled · cover 33.5 s (lying on his back, eyes open) · voice from the Nov 11 `nearing` take, one continuous shot |
| 41 | 2026-11-20 | nigel-bane/day041.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII I shortening` | `6afcb3b3dfbe5d51e1ea518f` | `6afcb3b457c8fecbcd198e7b` | scheduled · cover 25.8 s (hand flat on the far wall) |
| 42 | 2026-11-21 | nigel-bane/day042.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII II bracing` | `6afcb3b57847359f57adabb5` | `6afcb3b6700b9ade62f16910` | scheduled · cover 13.0 s (arms out, palms on both walls) |
| 43 | 2026-11-22 | nigel-bane/day043.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII III unwatching` | `6afcb61e7338fb226f83069a` | `6afcb61f7847359f57ae93b2` | scheduled · REMADE 2026-11-22 (owner's hard reset; new script and voice, real eyelids), Buffer uses `?v=3` · cover 22.1 s (the one-eyed peek) |
| 44 | 2026-11-23 | nigel-bane/day044.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIII dimming` | `6afcb61f57c8fecbcd1a974d` | `6afcb6207847359f57ae9403` | scheduled · REMADE 2026-11-22 (owner's hard reset), Buffer uses `?v=2` · cover 10.2 s (his hand at the glowing lamp) |
| 45 | 2026-11-24 | nigel-bane/day045.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII haunting` | `6b032d8ec72676f5e94b5a76` | `6b032d90d864a01105e3585b` | scheduled · cover 62.6 s (cheek on the lamp's base) · owner-approved script (hard reset) |
| 46 | 2026-11-25 | nigel-bane/day046.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII I lingering` | `6b032e9bcc364169c174216a` | `6b032e9d846b0ee907a8281d` | scheduled · cover 16.9 s (the tag turned: "thank you.") · owner-approved script (hard reset) |
| 47 | 2026-11-26 | nigel-bane/day047.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII II carrying` | `6b032ea0d864a01105e424a4` | `6b032ea3bf5d5a73b6ae9cf3` | scheduled · cover 56.5 s (asleep, the lamp floating up, dawn) · owner-approved script (hard reset) |
| 48 | 2026-11-27 | nigel-bane/day048.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII III borrowing` | `6b03306dd5eabfb8cccb827f` | `6b033071c72676f5e94d3242` | scheduled · cover 12.5 s (the fog on the glass) · owner-approved script (hard reset) |
| 49 | 2026-11-28 | nigel-bane/day049.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIII tracing` | `6b09f01d585cafb820e014f8` | `6b09f01f585cafb820e0158e` | scheduled · cover 57.8 s (palm on the glass, the outline almost closed) · owner-approved script 2026-11-27 |
| 50 | 2026-11-29 | nigel-bane/day050.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII shedding` | `6b09f0acb5cd052fe28f9d86` | `6b09f0af585cafb820e058c4` | scheduled · cover 42.1 s (third try: his hand spilling out of the outline) · owner-approved script 2026-11-27 |
| 51 | 2026-11-30 | nigel-bane/day051.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII I shaping` | `6b09f203b5cd052fe2902f52` | `6b09f2062ea34800c29591e2` | scheduled · cover 56.5 s (half in, half out of the shrunken outline) · owner-approved script 2026-11-27 |
| 52 | 2026-12-01 | nigel-bane/day052.mp4 | `IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII IIIII II slowing` | `6b09f2abc02ca0988ab6fcb5` | `6b09f2adc02ca0988ab6fd74` | scheduled · cover 23.6 s (ear against the outline, eyes wide: "Don't stop.") · owner-approved script 2026-11-27 |
