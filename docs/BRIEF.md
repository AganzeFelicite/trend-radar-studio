# Build Prompt: Video Studio (Wi-Fido, the gamer dog)

> The original brief, kept verbatim as the source of truth. Progress is tracked in [PLAN.md](PLAN.md).
> The character name is the config value `CHARACTER_NAME`; "Wi-Fido" below is the default from the brief.

You are my coding agent. Build **Video Studio**: a separate system that turns a topic (or a Trend Radar Content Package) into a finished short-form vertical video hosted by our character, a dog gamer. I type text; the Studio researches, writes, voices, animates, edits and hands me a video to review.

I'm a software engineer: Python, React/Next.js, PostgreSQL, Docker on a VPS. Explain decisions briefly. Ask me before anything that costs money, deletes data, or publishes anything.

---

## 0. How you work

- Create `docs/PLAN.md` with every phase and task below, each with this **Definition of Done** checklist plus the task-specific checks:
```
- [ ] Implemented
- [ ] Tests written and passing (or manual test documented)
- [ ] README / docs updated
- [ ] Committed and pushed (message references the task, e.g. "V3.2: voice generation")
- [ ] Verified working — write HOW it was verified
```
- One task at a time; report at the end of each phase.
- **Repo:** create a new **private** GitHub repo with my GitHub CLI: check `gh auth status`, confirm the name with me (default `video-studio`), add `.gitignore` (never commit `.env`), then `gh repo create <name> --private --source=. --remote=origin --push`, and verify with `gh repo view --json visibility` that it is `PRIVATE`.

---

## 1. The character (confirm the final name with me first)

- **Name:** default **Wi-Fido** (alternatives: Barkley Lagsalot, Ruff Respawn, Sir Fetchalot, Pugdate). Use a `CHARACTER_NAME` config value everywhere.
- **Look:** an original, realistic-looking dog (not the "Doge" meme dog or any existing famous animal or character) wearing big RGB gaming headphones with a mic, in a neon-lit gaming room (monitors, gaming chair, energy drink, LED strips). Same dog, same headset, same room in every video.
- **Personality:** hyped but honest, quick jokes, dog puns used sparingly ("that topic is barking up the charts"), gamer slang, never mean. Signature opening line and sign-off (propose 3 options each for me to pick).
- **Voice:** an original designed text-to-speech voice. Never clone or imitate a real person's voice.
- **Character bible:** write `docs/CHARACTER.md` with name, backstory (2–3 lines), look, outfit, room, personality, catchphrases, do/don't list, and voice settings.
- **Master assets:** generate a consistent character sheet (front-facing talking pose, 3–4 reaction poses: shocked, laughing, thinking, celebrating) using one image model with a fixed reference, so the dog looks identical everywhere. Store in `assets/character/` with the prompt and settings used.
- [ ] Character bible approved by me  - [ ] Character sheet approved by me (consistent look across all poses)

---

## 2. Hard rules (enforce in code, not just prompts)

- **No third-party footage, ever:** no YouTube/TikTok/Twitch clips, no creator thumbnails, no screenshots of other people's posts, no GTA trailers, no Rockstar logos, art, characters or music.
- **Allowed visuals only:** (a) our character, (b) Trend Radar data cards and charts, (c) Pexels stock video/photos via the official Pexels API, (d) AI-generated cutaways of our own character/room, (e) my own gameplay later, only after I confirm Rockstar's policy allows it.
- **Asset provenance log:** every asset in every video is recorded (source, URL/ID, license, date). Refuse to render if any asset lacks a license entry. For Pexels: follow the Pexels API guidelines (link back to Pexels in the description), avoid clips with visible brands, logos or identifiable people.
- **Facts:** Trend Radar verified facts are used exactly as given and are never changed. Extra research is allowed only from reputable sources, must be cited, and is stored as `unverified-context`. No rumours or "leaks".
- **No sensational framing:** no "CANCELLED", "LEAKED", "CONFIRMED" or fake urgency unless a cited, reputable source supports it.
- **Sensitive topics:** never cover finance, investing, money-making, health, medical or legal topics. A blocklist plus an AI classifier stops the job and tells me why.
- **AI disclosure:** every output includes a posting checklist reminding me to switch on platform AI labels, and the description includes "Wi-Fido is an AI character."
- **YouTube originality:** every video must include our own data or original commentary, follow a narrative arc (hook → what's happening → why it matters → what's next), and have a title/thumbnail different from the last 7 videos.
- **Human approval:** nothing is published automatically. I review every video.
- **Cost caps:** monthly caps per paid service (LLM, TTS, avatar, image/video generation) in config; jobs stop and alert me when reached. Log the cost of every video.

---

## 3. Tech stack

- **Orchestrator:** Python 3.12 + FastAPI (job API) + a worker with a simple job queue (Redis + RQ or similar). Postgres for jobs, assets, provenance and costs.
- **Research + scripting:** Claude API with web search, for cited research and script writing. Structured outputs validated with pydantic.
- **Voice:** a text-to-speech API with a designed (not cloned) voice; return word-level timestamps if supported.
- **Talking character:** image + audio → talking video through an adapter interface so providers can be swapped. Compare **Kling Avatar v2** (Standard and Pro; documented to animate animals) and **Hedra Character-3** on a 10-second test with our dog, and show me quality, lip-sync and cost per second before choosing.
- **Stock footage:** Pexels API (videos + photos).
- **Captions:** word timestamps from TTS, or Whisper on the voice track.
- **Editing/rendering:** **Remotion** (React) with one signature template: 1080×1920, 30fps, burned-in animated captions, character picture-in-picture or full-frame, data-card scenes, B-roll scenes, sound effects, intro sting, outro sign-off. (Remotion is free for individuals and companies up to 3 people; confirm we qualify.)
- **Music/SFX:** only royalty-free sources with a license that allows commercial use; logged in provenance.
- **Input UI:** a small Next.js admin page: text box (topic or paste/upload a Content Package), format picker, target length, "Generate" button, job progress, preview player, approve/reject, download.
- **Deployment:** Docker Compose; runs locally first, later on the same VPS as Trend Radar (or a second one if rendering is heavy). Secrets in `.env` only.

---

## 4. Video formats (rotate; one template, different structures)

- **Radar Report** (45–60s): top 3 trends today, with data cards.
- **Make This Now** (30–45s): one opportunity for creators, why it's hot.
- **Myth or Real?** (30–45s): a viral claim checked against data and reputable sources.
- **Weekly Recap** (60–90s, Sundays): biggest moves of the week.
- Every video: hook in the first 2 seconds, captions on screen, character on screen at least at the start and end, our data visible at least once.

---

## 5. Phases and tasks

### Phase V1 — Foundation
- **V1.1** Private repo via `gh` (section 0)
- **V1.2** Docker Compose: api, worker, postgres, redis, admin (Next.js), renderer (Remotion)
  - [ ] All services start  - [ ] Health endpoint OK
- **V1.3** Database: jobs, scripts, assets (with provenance), costs, outputs
  - [ ] Migrations up/down clean
- **V1.4** Config: character name, cost caps, blocklist, provider choices
  - [ ] `.env.example` complete; no secrets committed

### Phase V2 — Character
- **V2.1** Character bible (`docs/CHARACTER.md`)
  - [ ] Approved by me
- **V2.2** Master character sheet (talking pose + 4 reactions) with reproducible prompts/settings
  - [ ] Approved by me; same dog in every pose
- **V2.3** Voice design + 3 sample lines
  - [ ] I pick the voice
- **V2.4** Avatar provider test: same 10-second line through Kling Avatar v2 (Standard + Pro) and Hedra Character-3
  - [ ] Comparison table (quality, lip-sync, motion, cost/second) shown to me; I choose

### Phase V3 — Pipeline
- **V3.1** Input: topic text or Trend Radar Content Package (`package.json` / `package.md`)
  - [ ] Both inputs parsed; package facts marked verified
- **V3.2** Research step (Claude + web search): cited notes, separated from verified facts
  - [ ] Every added claim has a source URL
- **V3.3** Script step: format-specific structure, character voice, narrative arc, timed scenes with visual cues
  - [ ] Validator: no invented numbers; verified facts unchanged; arc present
- **V3.4** Safety gate: blocklist + classifier for sensitive topics; sensational-word check
  - [ ] Test: a finance topic is blocked with a clear reason
- **V3.5** Voice generation + word timestamps
- **V3.6** Talking-character generation through the chosen provider (adapter interface)
  - [ ] Cost logged per clip
- **V3.7** B-roll: Pexels search per scene; provenance logged; brand/people filter
  - [ ] Render refused if any asset lacks a license entry (tested)
- **V3.8** Data cards: import Trend Radar card images from the package (or render our own from facts)

### Phase V4 — Editing and output
- **V4.1** Remotion signature template (intro sting, character PiP/full-frame, data-card scenes, B-roll scenes, animated captions, SFX, outro)
  - [ ] Renders a 1080×1920 MP4 from a sample job
- **V4.2** Captions: word-by-word animated, readable on mobile
- **V4.3** Output bundle: MP4, thumbnail options (own design), 3 titles, caption, hashtags, description (with AI disclosure, sources, Pexels link), posting checklist
  - [ ] Titles/thumbnail differ from the last 7 videos (checked)
- **V4.4** Admin review page: preview, approve/reject, download bundle

### Phase V5 — Quality and safety
- **V5.1** End-to-end test: Content Package → approved video in under 15 minutes
- **V5.2** Weekly channel audit: last 10 videos side by side (titles, thumbnails, formats, first lines); flag look-alikes
- **V5.3** Cost report: cost per video and month-to-date per service
- **V5.4** Five sample videos (one per format + one extra) for my review before the channel launches

### Phase V6 — Later (only after I approve)
- Multi-language versions (same facts, translated script, voice in that language)
- Connect directly to Trend Radar's `GET /api/content-packages/{date}` with an admin token
- Telegram bot input ("send a topic, get a draft video back")
- My own gameplay as B-roll, after I confirm Rockstar's policy

---

**Start with V1.1 (private repo) and `docs/PLAN.md`, then the character bible (V2.1). Show me the character bible and three name/catchphrase options before generating any images.**
