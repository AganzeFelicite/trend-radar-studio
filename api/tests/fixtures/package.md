# Video package: daily_radar · 2026-11-04

| | |
|---|---|
| package_id | `2026-11-04-daily_radar-en-v5` |
| format | daily_radar |
| language | en |
| host | Wi-Fido (the Video Studio's character) |
| data brand | Trend Radar |
| target length | 40 s (hook, at most 3 segments, close) |
| status | **not approved (preview: don't publish)** |
| built from | Daily Brief v5, scores at 2026-11-04 09:00 UTC, last 24 hours |
| movement | some |
| data cards | `cards/title.png`, `cards/segment-1.png`, `cards/end.png` (not rendered yet: draw them from the facts in our style) |
| previous titles | none published yet |

You are the research and production assistant for **Wi-Fido**, a stylised AI host who tells GTA 6 creators which topics are rising, using data from **Trend Radar** (YouTube, Bluesky and gaming news, collected hourly through official APIs). Make one 40-second vertical video (1080×1920) in English.

Work in two phases:
1. **Research** (section 2). Then stop and report your findings.
2. **Production** (section 3), after the report is reviewed.

## 1. Facts

Two kinds of fact may be said or shown as numbers or dates:
- `verified`: our data, listed below.
- `official`: from Rockstar Newswire, PlayStation, Xbox or a store page, added by you during research with the primary-source URL (resolve short links like bit.ly; never cite a news site as the source of an official fact).

| ID | Type | Fact | Value | Source |
|---|---|---|---|---|
| F1 | verified | Pre-load: rank | #1 | Trend Radar topic_scores · preload · public_rank · 2026-11-04 09:00 UTC |
| F2 | verified | Pre-load: rank 6 hours ago | #1 | Trend Radar topic_scores · preload · public_rank_6h_ago · 2026-11-04 09:00 UTC |
| F3 | verified | Pre-load: score (0-100) | 68 | Trend Radar topic_scores · preload · score · 2026-11-04 09:00 UTC |
| F4 | verified | Pre-load: share of the GTA 6 conversation, 24h | 11.5% | Trend Radar topic_scores · preload · attention · 2026-11-04 09:00 UTC |
| F5 | verified | Pre-load: sources it's active on | 3 | Trend Radar topic_scores · preload · sources · 2026-11-04 09:00 UTC |
| F6 | verified | Pre-load: posts and videos, 24h | 62 | Trend Radar topic_scores · preload · items · 2026-11-04 09:00 UTC |
| F7 | official | Pre-load start date | November 10 | https://www.rockstargames.com/newswire/example |

**Movement: some.** Say each topic's rank change exactly as listed.

## 2. Research

Goal: find out **why** each topic is moving and **what viewers want to know**. Read comments and replies only through official APIs: YouTube Data API (`commentThreads.list`) and the Bluesky API (`app.bsky.feed.getPostThread`). Items about piracy, jailbreaks, leaks or cheats have been removed; don't research them.

### Segment 1: Pre-load
- Pre-load: #1, score 68, unchanged in 6 hours (still #1) (facts F1, F2, F3, F4, F5, F6, F7)
- What people call it: pre load, preload, november 10, pre loading, preloading, pre loads, 212 gb, file size, storage, 212gb, install size, download size, 210 gb

Find out:
1. What is actually happening with Pre-load & File size? For every official statement give the primary-source URL (Rockstar Newswire, PlayStation, Xbox or the store page; resolve short links; a news article is never the source of an official fact) and tag it `official`. Everything else is `unverified-context`.
2. The 3 questions, complaints or claims that come up most in the comments and replies of the items below (read through the YouTube Data API and the Bluesky API only; paraphrase; no usernames; rough share).
3. What do the top videos have in common (angle, title, hook in the first 5 seconds), and what do viewers say is missing? That gap is our angle.

### Official sources seen in our data
Check these first for `official` facts:
- none found in today's items

### Breakout videos: study why these work
Small channels getting far more views than they have subscribers. Note their title, hook and format; don't copy or show them.
- none today

**Report format:** for each segment, bullets of findings, each with a source link and a tag: `official` (primary source URL), `verified` (one of our facts) or `unverified-context`. End with one suggested angle per segment.

## 3. Production

**Script** (today's draft; keep its facts and framing, tighten to 40 s, add at most one cited finding per segment):
> HOOK: Wi-Fido here with your GTA 6 radar for November 4. Pre-load and File size hold the top spots.
>
> WHAT THE DATA SHOWS: Pre-load sits at #1 with a score of 68 out of 100, and File size is at #3 with 36. Both are unchanged over the past six hours, still holding their places. Xbox stays at #2 with 42. Map moved up a place over six hours, from #5 to #4, with a score of 28.
>
> WHY IT MATTERS: Creators, this shows where attention is building across YouTube, Bluesky and gaming news. Topics at the top give you a clear sense of what viewers are searching for and sharing right now.
>
> WHAT NEXT: Use these topics to plan your next video, and watch how Map moves in the next update.

**Owner's line:** [OWNER COMMENTARY: added on the approval page. Leave a 4-second slot.]

| Time | Voice | On screen (our own graphics only) |
|---|---|---|
| 0-4s | Hook | Title card "GTA 6 trends · Nov 4" and Wi-Fido |
| 4-13s | Pre-load & File size: the data, its movement, one cited finding | cards/segment-1.png |
| 32-40s | Why it matters, the owner's line (4 s), what to watch | Host close-up with the owner's line as a caption, then cards/end.png |

**Graphics:** our own style. Dark background, one green accent, bold monospaced numbers, simple bars and lines. No game art, logos, screenshots or thumbnails.

**Deliver:** the MP4 (1080×1920, 40 s or less, captions burned in); 3 title options (never "confirmed", "leaked", "insane" or all-caps words, different from the previous titles above); a caption that includes "AI host powered by real-time GTA 6 trend data from Trend Radar"; 3-5 hashtags.

## 4. Rules (non-negotiable)

- No third-party clips or thumbnails in the video. The videos, posts and headlines in the research list are for reading and citing only.
- No Rockstar/GTA logos, art, screenshots, characters or music.
- The host is a stylised, clearly-AI character, never a realistic human. Trend Radar is the data source, not the host.
- The platform AI label must be switched on when posting (YouTube altered/synthetic content; TikTok AI-generated).
- Only `verified` facts (listed in this package) and `official` facts (from Rockstar Newswire, PlayStation, Xbox or a store page, with the primary-source URL; short links resolved; never a news site as the source) may be said or shown as numbers or dates.
- Anything else from research is cited and marked `unverified-context`, and is never shown as a number.
- No sensational claims: no "leaked", "confirmed", "cancelled" or "delayed" framing unless an official source says so; no fake urgency.
- Titles never use "confirmed", "leaked", "insane" or all-caps words, and differ from the previous titles listed in this package.
- No finance, money-making, health or legal topics. Nothing about piracy, jailbreaks, leaks or cheats.
- Read comments and replies only through official APIs: YouTube Data API (commentThreads.list) and the Bluesky API (app.bsky.feed.getPostThread). No scraping.
- Never show or say commenters' names or handles; paraphrase what they say.
