# Video Studio — Plan

The full spec is in [BRIEF.md](BRIEF.md). One task at a time, with a report at the end of each phase.
**Ask before anything that costs money, deletes data, or publishes anything.**

Every task uses the same Definition of Done (DoD), plus its own checks:

```
- [ ] Implemented
- [ ] Tests written and passing (or manual test documented)
- [ ] README / docs updated
- [ ] Committed and pushed (message references the task, e.g. "V3.2: voice generation")
- [ ] Verified working — write HOW it was verified
```

## Open decisions (owner: you)

| # | Decision | Blocks | Status |
|---|---|---|---|
| D1 | Repo name (`video-studio` is already taken by the FilmCraft project) | V1.1 | **`trend-radar-studio`** |
| D2 | Character name: "Wi-Fido" is already a robot dog in Hasbro's *Rescue Bots* | V2.1 | **Big Dog** |
| D3 | Signature opening line + sign-off | V2.1 | **"Ping check — {NAME}'s online!"** / **"{NAME}, logging off. Stay pawsome."** |
| D4 | Remotion licence: free for individuals and companies of up to 3 people. Do we qualify? | V4.1 | **Yes**: you alone, or a team of 3 or fewer |
| D5 | Image model for the character sheet (paid) | V2.2 | Via fal.ai. Exact model and price confirmed with you before generating. |
| D6 | TTS provider for the designed voice (paid) | V2.3 | **ElevenLabs Starter ($6/mo), Voice Design**, male-leaning |
| D7 | Avatar provider: Kling Avatar v2 Std / Pro vs Hedra Character-3 (paid test) | V2.4 | **Test only Kling Std + Pro on fal.ai** (about $1.70). Hedra is skipped for budget unless Kling fails on a dog. |
| D8 | Monthly cost caps per service (LLM, TTS, avatar, image/video gen) | V1.4 | **$20/mo total**: TTS $6 · fal.ai (avatar + images) $10 · Claude API $4 |
| D9 | Rockstar policy check before using your own gameplay | V6.4 | open |
| D10 | Show style | V3.3, V4.1 | **News format.** The dog is on screen (lip-synced) only in a few short desk spots, about 10 s per video. Voice-over runs over B-roll and data cards the rest of the time. About $0.80 per video, about 17 videos a month. |
| D11 | Platforms | V4.3 | **YouTube Shorts, TikTok, Instagram Reels, Facebook Reels**: the posting checklist covers each platform's AI label |
| D12 | Accounts | V2.2+ | You create **fal.ai** (pay-as-you-go), **Pexels** (free) and **ElevenLabs Starter**, then paste the keys into `.env`. You already have an Anthropic key. |

### Pivot, 2026-11-04 (replaces D2, D5–D8 and D10 where they conflict)

| # | Decision | Status |
|---|---|---|
| D13 | Character: a **cartoon human news reporter with a headset** (no longer a dog), drawn once in code and reused | **GameReporter**; look approved; sign-off "Stay locked in." |
| D14 | Voice: **free local TTS (Kokoro)**, a male-leaning original voice mix ($0). Replaces ElevenLabs. | decided |
| D15 | Research and scripts run through **your own Claude Code, headless (`claude -p`)**, the same way as the `video-studio` Studio worker. $0 beyond your subscription. Replaces the paid Claude API. | decided |
| D16 | Editing follows **your existing FilmCraft pipeline**: the `filmcraft-commentary-short` format (splits, punch-ins, cards, pop captions, end card, beds and SFX from the licensed sound library), rendered with `filmcraft-cli`. The cartoon reporter clip takes the place of your phone footage. | **Both**: Remotion renders the reporter clip and our own graphics (data cards); FilmCraft assembles the final edit in your format |
| D17 | Hard rules still apply: no YouTube/yt-dlp clips and no license-uncertain memes. B-roll comes from our own graphics and Trend Radar cards (see D18). | decided |
| D18 | **Pexels paused new API keys** (Nov 2026), so B-roll is **drawn by us in Remotion**: animated data cards, charts, kinetic headlines, radar graphics and GameReporter reaction cutaways. $0, no account, no licence risk, and it all counts as our own content for YouTube originality. Pixabay (free key) can be added later if you want real-world footage. | default; Pixabay optional |

Expected per-video cost after the pivot is $0.

Prices checked 2026-11-04: fal.ai lists Kling Avatar v2 at $0.0562/s (Std) and $0.115/s (Pro). ElevenLabs Starter is $6/mo. Hedra's cheapest commercial plan is about $15/mo for about 4 min of video.

---

## Phase V1 — Foundation

### V1.1 Private repo via `gh`
- [x] `gh auth status` OK (account `AganzeFelicite`)
- [x] Name confirmed by you (D1): `trend-radar-studio`
- [x] `.gitignore` excludes `.env` / `.env.*` (keeps `.env.example`)
- [x] `gh repo view --json visibility` returns `PRIVATE`
- DoD: [x] Implemented [x] Tests/manual test [x] Docs [x] Committed & pushed [x] Verified — how: ran `gh repo view AganzeFelicite/trend-radar-studio --json visibility` and got `{"visibility":"PRIVATE"}`; `main` pushed and tracking `origin/main`.

### V1.2 Docker Compose: api, worker, postgres, redis, admin (Next.js), renderer (Remotion)
- [x] All services start
- [x] Health endpoint OK
- DoD: [x] Implemented [x] Tests/manual test [x] Docs [x] Committed & pushed [x] Verified — how: ran `docker compose up -d --build`, then `./scripts/smoke.sh`, which printed `ALL OK`. That covered api `/health` returning `{"status":"ok","db":"ok","redis":"ok","workers":1}`, the renderer `/health`, and the admin page showing the api status (admin → api → db/redis). Inside the renderer container, `npx remotion still src/index.ts Placeholder` produced a 1080×1920 PNG, which proves Chrome headless shell works. Failure path: with postgres stopped, `/health` returned HTTP 503 `{"status":"degraded","db":"OperationalError"}`, and it recovered to 200 after a restart.

### V1.3 Database: jobs, scripts, assets (with provenance), costs, outputs
- [x] Migrations up/down clean
- DoD: [x] Implemented [x] Tests/manual test [x] Docs [x] Committed & pushed [x] Verified — how: `uv run pytest` gives 9 passed. Those tests cover: migrations down to base with 0 tables, then back up to head with all 6 tables; assets rejected with no or empty licence and with source `youtube` or `gameplay`; unverified facts rejected without a source URL; outputs rejected without the AI disclosure or with anything other than 3 titles; negative costs rejected. `alembic check` reports no drift between the models and the migrations. In Docker, the api ran `alembic upgrade head` on startup and `./scripts/smoke.sh` printed `ALL OK`.

### V1.4 Config: character name, cost caps, blocklist, provider choices
- [x] `CHARACTER_NAME` used everywhere (no hard-coded name)
- [x] `.env.example` complete; no secrets committed
- [x] Cost caps enforced: `ensure_budget` runs before every paid call, `record_cost` logs every spend
- DoD: [x] Implemented [x] Tests/manual test [x] Docs [x] Committed & pushed [x] Verified — how: `uv run pytest` gives 13 passed. The new tests check that the caps total $20; that `.env.example` covers every env var the code and compose read (I deleted one line on purpose, the test failed naming it, then I restored it); that "Big Dog" is hard-coded only in `config.py`; and that the budget guard allows exactly $4.00 but raises at $4.01, ignoring last month's spend. `git ls-files` shows only `.env.example`, and a `git grep` for key patterns found none. In Docker, the api loaded the config (`Big Dog | claude-opus-5-5 | caps llm 4, tts 6, avatar 8, image 2, video 0`) and the smoke test printed `ALL OK`.

## Phase V2 — Character

### V2.1 Character bible (`docs/CHARACTER.md`)
- [x] Draft written (name, backstory, look, outfit, room, personality, catchphrases, do/don't, voice settings)
- [x] Name + opener + sign-off picked by you (D2, D3)
- [x] Rewritten for the cartoon reporter (D13): draft v2
- [x] Name picked by you: GameReporter
- [x] Approved by you (look; sign-off "Stay locked in.")
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V2.2 Master character sheet (talking pose + 4 reactions), drawn in code (D13)
- [x] Reporter drawn as SVG in `renderer/src/Reporter.tsx`: 5 poses + 9 Rhubarb mouth shapes; sheet in `assets/character/` ($0, reproducible by construction)
- [x] Approved by you; same character in every pose
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V2.3 Voice design + 3 sample lines (local Kokoro, D14)
- [x] Original mix of Kokoro preset voices (not cloned, no "sounds like <person>" prompts)
- [x] 3 samples in `assets/voice/` (`anchor`, `hype`, `warm`); `studio/voice.py` makes them. Local Whisper heard every word of all three.
- [x] Voice picked: `hype` (60% am_puck + 40% am_michael, speed 1.15), chosen by me on your go-ahead
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V2.4 Talking-clip test (replaces the paid avatar test): same 10 s line, Rhubarb lip-sync + blinks + pose swaps in Remotion
- [x] 1080x1920 MP4 of the reporter speaking the V2.3 voice: `assets/character/talk-test.mp4` ($0)
- [x] Lip-sync from Kokoro's own phoneme timings mapped to the 9 mouth shapes (`studio/voice.py: mouth_cues`), no extra tool. Rhubarb was blocked as an external binary; the cues use its format, so it can drop in later.
- [ ] You judge lip-sync and motion
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

## Phase V3 — Pipeline

### V3.1 Input: topic text or Trend Radar Content Package (`package.json` / `package.md`)
- [x] Both inputs parsed; package facts marked `verified`
- DoD: [x] Implemented [x] Tests/manual test [x] Docs [x] Committed & pushed [x] Verified — how: `POST /jobs` on the running API with today's real, untrimmed package from the local Trend Radar (`GET /api/admin/content-package`), as JSON and as the Markdown Trend Radar renders from it. Both jobs got the same 24 `verified` facts word for word (SQL `except` of the two sets is empty). A topic line became a topic job; an empty input and a 5 s length were refused with a reason. Tests: `test_inputs.py` (fixture = trimmed real package; its `.md` rendered by Trend Radar's own `markdown()`).
- Notes: Trend Radar's `official` facts (primary-source URL) are stored as cited `unverified-context`, so their numbers stay off screen until we add an `official` kind. The package's `daily_radar` format maps to Radar Report; its length (40 s) wins over the format default.

### V3.2 Research step (your headless Claude Code + web search, D15): cited notes, kept apart from verified facts
- [x] Every added claim has a source URL; stored as `unverified-context`
- DoD: [x] Implemented [x] Tests/manual test [x] Docs [x] Committed & pushed [x] Verified — how: real runs with Haiku on your Pro login. Today's Trend Radar package (job 1) got 8 cited notes in 56 s (Xbox News, Destructoid, KeenGamer, IBTimes, GameIndustry); the topic "Why everyone is talking about the GTA 6 map size" (job 3) got 7 in 51 s, and a note about "leaked measurements" was dropped. Every stored note has a `source_url` (SQL check), and the llm cost log shows $0.00. Tests: `test_research.py` (blocked domains, rumour/leak wording, missing or homepage URLs, package facts untouched, no `ANTHROPIC_API_KEY` passed on, denied tools raise).
- Notes: code-enforced, not just prompted. Sources from YouTube, TikTok, Twitch, Reddit, X, Facebook, Instagram, Bluesky, Discord, fandom and similar are dropped (`RESEARCH_BLOCKED_DOMAINS`), as are claims worded as leaks/rumours/insiders/piracy/cheats and homepage citations. Claude Code runs on the Mac (where it's logged in), in an empty folder with no settings, hooks or MCP servers, and only WebSearch and WebFetch available. The first live run returned nothing because WebSearch was available but not allowed, so a denied tool now fails the step instead of passing silently.

### V3.3 Script step: format structure, character voice, narrative arc, timed scenes with visual cues
- [x] Validator: no invented numbers; verified facts unchanged; arc (hook → what → why → next) present
- [x] Title/thumbnail text differs from last 7 videos
- DoD: [x] Implemented [x] Tests/manual test [x] Docs [x] Committed & pushed [x] Verified — how: real Haiku scripts on your Pro login, $0. Today's package (job 1): a Radar Report of ~44 s for a 40 s target, every number traced to a verified fact (#1/68, #3/36, #2/42, #5 → #4), cards citing fact IDs, the reporter on the desk at the start and end, opener and sign-off added by code; it passed on the first try in 40 s. The map-size topic (job 3, Myth or Real?): ~38 s, no numbers at all (the topic has no verified data), ending "Verdict: Not confirmed yet." Tests: `test_script.py`, one broken copy of a valid script per rule (invented 70, rounded 12%, spelled "twice", missing or reordered arc, hook not on the desk or over 10 words, no card, unknown fact/note IDs, on-screen text over 6 words, 2 titles, titles/thumbnail too close to a recent video, too long), plus retry-then-store and give-up-after-3.
- Notes: numbers must be digits and come from the verified facts (labels included, e.g. "6 hours", "GTA 6"), or be the package date. Research notes can be attributed ("Destructoid reports…") but their numbers can't be used. "Similar" title = difflib ratio ≥ 0.75 against the latest script of the 7 most recent other jobs plus the package's published titles. Speech length is estimated at 2.9 words/s (±25 %) until V3.5 measures the real voice. A failed draft goes back to Claude Code with its list of problems, at most 3 tries in all.

### V3.4 Safety gate: blocklist + classifier for sensitive topics; sensational-word check
- [x] Test: a finance topic is blocked with a clear reason
- [x] Test: "LEAKED"/"CANCELLED"/"CONFIRMED" without a cited source is rejected
- DoD: [x] Implemented [x] Tests/manual test [x] Docs [x] Committed & pushed [x] Verified — how: real gate runs. "Take-Two share price after the GTA 6 trailer" has no blocklist word, and the AI classifier blocked it: "finance topic (AI classifier: …about stock market performance and investing rather than ordinary game news.)". "How to invest your GTA 6 money in crypto" was blocked by the blocklist (`'invest'`) without calling the AI. Today's package and the map-size topic passed. Both blocked jobs show `status = blocked` with the reason in `jobs.error`. A real script re-run with the word check active passed on the first try ("Until then? Not confirmed yet."). Tests: `test_safety.py` (blocklist, classifier, "health bar" not blocked, 10 sensational cases rejected, 5 honest lines passing, validator wiring).
- Notes: the order is blocklist (free, instant) → classifier (one tool-less Haiku call) → research. Stricter than the brief on purpose: leaks, rumours, insiders, "breaking" and fake urgency are never allowed, even cited (brief: "No rumours or leaks"; D10: no BREAKING banners). "Confirmed", "cancelled" and "delayed" need a note that says so positively, in the same scene. Negated uses ("not confirmed yet", "hasn't officially confirmed", "unconfirmed") are fine. Titles and thumbnails never use any of these words. All-caps words of 5+ letters are rejected everywhere; short acronyms (GTA, DLC) are fine.

### V3.5 Voice generation + word timestamps
- [x] Cost logged per clip; cap enforced
- DoD: [x] Implemented [x] Tests/manual test [x] Docs [x] Committed & pushed [x] Verified — how: real track for today's package (job 1): 8 scenes, 42.4 s against a 40 s target, in 23 s on the Mac. Whisper large-v3-turbo heard it at 0.957 word match; the only differences are whisper splitting "GameReporter" and "Bluesky" into two words. The first run read "#1" as "hash one", so lines now get speech-only fixes (`#1` → "number 1", `→` → "to", `1.2x` → "1.2 times"). The first track also ran 50.6 s for a 44 s estimate: the real rate is 2.5 script words/s, not 2.9, so the script step now uses the measured value. Provenance row (`voice`, `tts`, Apache-2.0) and a $0 `tts` cost row are written per track, after `ensure_budget`. Tests: `test_voice.py` (speech fixes, whisper diff, track joining with 0.3 s pauses, provenance and cost rows).
- Output: `storage/jobs/<id>/voice.wav` (one track: your pipeline's A-roll audio) and `voice.json` with real scene start/end times, mouth cues for the talking clip, whisper word timestamps (same model as your FilmCraft pipeline) and the match score.

### V3.6 Talking-character generation through the chosen provider (adapter interface)
- [x] Cost logged per clip; cap enforced
- DoD: [x] Implemented [x] Tests/manual test [x] Docs [x] Committed & pushed [x] Verified — how: rendered today's package (job 1) in 51 s: `storage/jobs/1/reporter.mp4`, 1080×1920, 30 fps, 42.9 s with audio. An 8-frame grid shows varied mouth shapes, the thinking pose on its desk scene, and the same character and set throughout. Whisper on the MP4 matches the script at 0.957, the same as the voice track, so no audio was lost in the render. Provenance (`avatar_clip`, `own`) and a $0 `avatar` cost row are written, after `ensure_budget`. Tests: `test_clip.py` (reaction poses only on desk scenes, held 2 s; render command mounts; provenance and cost).
- Notes: the provider is Remotion with our drawn character (D16, $0). One full-length clip covers the whole voice track, like your phone A-roll; the FilmCraft edit cuts to full-frame cards and headlines on non-desk scenes while the voice continues. The adapter is the function contract `talking_clip(job_id)`: `voice.json` in, `reporter.mp4` out. A second provider is a second function behind a config switch, added when one exists.

### V3.7 B-roll: our own Remotion scenes per script cue (D18; Pexels paused); provenance logged as `own`
- [ ] Render refused if any asset lacks a licence entry (tested)
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V3.8 Data cards: import Trend Radar card images from the package (or render our own from facts)
- [ ] Cards logged in provenance as own data
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

## Phase V4 — Editing and output

### V4.1 Remotion signature template (intro sting, character PiP/full-frame, data cards, B-roll, captions, SFX, outro)
- [x] Licence question D4 answered
- [ ] News-format scenes (D10): anchor desk spots, full-screen B-roll and data cards with voice-over, lower-thirds. No "BREAKING" banners.
- [ ] Renders a 1080×1920 30 fps MP4 from a sample job
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V4.2 Captions: word-by-word animated, readable on mobile
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V4.3 Output bundle: MP4, own thumbnail options, 3 titles, caption, hashtags, description, posting checklist
- [ ] Description has AI disclosure ("<CHARACTER_NAME> is an AI character."), sources, and a stock-site credit link only if stock footage was used
- [ ] Posting checklist includes the AI-label step for YouTube Shorts, TikTok, Instagram Reels and Facebook Reels (D11)
- [ ] Titles/thumbnail differ from the last 7 videos (checked)
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V4.4 Admin review page: preview, approve/reject, download bundle
- [ ] Nothing publishes automatically
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

## Phase V5 — Quality and safety

### V5.1 End-to-end: Content Package → approved video in under 15 minutes
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V5.2 Weekly channel audit: last 10 videos side by side; flag look-alikes
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V5.3 Cost report: per video and month-to-date per service
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V5.4 Five sample videos (one per format + one extra) for your review before launch
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

## Phase V6 — Later (only after you approve)

### V6.1 Multi-language versions (same facts, translated script, voice in that language)
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V6.2 Pull directly from Trend Radar `GET /api/content-packages/{date}` with admin token
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V6.3 Telegram bot input ("send a topic, get a draft video back")
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V6.4 Your own gameplay as B-roll (after D9)
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:
