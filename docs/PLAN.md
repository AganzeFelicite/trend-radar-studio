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
| D4 | Remotion licence: free for individuals and companies of up to 3 people. Do we qualify? | V4.1 | open |
| D5 | Image model for the character sheet (paid) | V2.2 | open |
| D6 | TTS provider for the designed voice (paid) | V2.3 | open |
| D7 | Avatar provider: Kling Avatar v2 Std / Pro vs Hedra Character-3 (paid test) | V2.4 | open |
| D8 | Monthly cost caps per service (LLM, TTS, avatar, image/video gen) | V1.4 | open |
| D9 | Rockstar policy check before using your own gameplay | V6.4 | open |

---

## Phase V1 — Foundation

### V1.1 Private repo via `gh`
- [x] `gh auth status` OK (account `AganzeFelicite`)
- [x] Name confirmed by you (D1): `trend-radar-studio`
- [x] `.gitignore` excludes `.env` / `.env.*` (keeps `.env.example`)
- [x] `gh repo view --json visibility` returns `PRIVATE`
- DoD: [x] Implemented [x] Tests/manual test [x] Docs [x] Committed & pushed [x] Verified — how: ran `gh repo view AganzeFelicite/trend-radar-studio --json visibility` and got `{"visibility":"PRIVATE"}`; `main` pushed and tracking `origin/main`.

### V1.2 Docker Compose: api, worker, postgres, redis, admin (Next.js), renderer (Remotion)
- [ ] All services start
- [ ] Health endpoint OK
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V1.3 Database: jobs, scripts, assets (with provenance), costs, outputs
- [ ] Migrations up/down clean
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V1.4 Config: character name, cost caps, blocklist, provider choices
- [ ] `CHARACTER_NAME` used everywhere (no hard-coded name)
- [ ] `.env.example` complete; no secrets committed
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

## Phase V2 — Character

### V2.1 Character bible (`docs/CHARACTER.md`)
- [x] Draft written (name, backstory, look, outfit, room, personality, catchphrases, do/don't, voice settings)
- [x] Name + opener + sign-off picked by you (D2, D3)
- [ ] Approved by you
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V2.2 Master character sheet (talking pose + 4 reactions), reproducible prompts/settings
- [ ] One image model, fixed reference image, seeds/settings stored in `assets/character/`
- [ ] Approved by you; same dog in every pose
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V2.3 Voice design + 3 sample lines
- [ ] Designed voice (not cloned, no "sounds like <person>" prompts)
- [ ] You pick the voice
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V2.4 Avatar provider test: same 10 s line through Kling Avatar v2 (Std + Pro) and Hedra Character-3
- [ ] Comparison table (quality, lip-sync, motion, cost/second) shown to you; you choose
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

## Phase V3 — Pipeline

### V3.1 Input: topic text or Trend Radar Content Package (`package.json` / `package.md`)
- [ ] Both inputs parsed; package facts marked `verified`
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V3.2 Research step (Claude + web search): cited notes, kept apart from verified facts
- [ ] Every added claim has a source URL; stored as `unverified-context`
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V3.3 Script step: format structure, character voice, narrative arc, timed scenes with visual cues
- [ ] Validator: no invented numbers; verified facts unchanged; arc (hook → what → why → next) present
- [ ] Title/thumbnail text differs from last 7 videos
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V3.4 Safety gate: blocklist + classifier for sensitive topics; sensational-word check
- [ ] Test: a finance topic is blocked with a clear reason
- [ ] Test: "LEAKED"/"CANCELLED"/"CONFIRMED" without a cited source is rejected
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V3.5 Voice generation + word timestamps
- [ ] Cost logged per clip; cap enforced
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V3.6 Talking-character generation through the chosen provider (adapter interface)
- [ ] Cost logged per clip; cap enforced
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V3.7 B-roll: Pexels search per scene; provenance logged; brand/people filter
- [ ] Render refused if any asset lacks a licence entry (tested)
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V3.8 Data cards: import Trend Radar card images from the package (or render our own from facts)
- [ ] Cards logged in provenance as own data
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

## Phase V4 — Editing and output

### V4.1 Remotion signature template (intro sting, character PiP/full-frame, data cards, B-roll, captions, SFX, outro)
- [ ] Licence question D4 answered
- [ ] Renders a 1080×1920 30 fps MP4 from a sample job
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V4.2 Captions: word-by-word animated, readable on mobile
- DoD: [ ] Implemented [ ] Tests/manual test [ ] Docs [ ] Committed & pushed [ ] Verified — how:

### V4.3 Output bundle: MP4, own thumbnail options, 3 titles, caption, hashtags, description, posting checklist
- [ ] Description has AI disclosure ("<CHARACTER_NAME> is an AI character."), sources, Pexels link
- [ ] Posting checklist includes "switch on platform AI label"
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
