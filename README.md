# Video Studio

Turns a topic (or a Trend Radar Content Package) into a finished 1080×1920 short hosted by GameReporter, our cartoon AI news reporter. It researches, writes, voices, animates and edits the video, then hands it over for human review. **Nothing is published automatically.**

- Spec: [docs/BRIEF.md](docs/BRIEF.md)
- Plan & progress: [docs/PLAN.md](docs/PLAN.md)
- Character bible: [docs/CHARACTER.md](docs/CHARACTER.md)

## Status

Phases V1 (foundation) and V2 (character: GameReporter, voice, talking clip) are done, all at $0 per video. Next comes Phase V3 (the pipeline).

## Config

```bash
cp .env.example .env   # no API keys needed
```

All settings live in `api/studio/config.py`, which reads `.env`. They are the character name, the Claude Code model, monthly cost caps per service ($0 by default, so nothing paid runs), the sensitive-topic blocklist, the sensational-word list and the research source rules. `studio/costs.py` checks the cap before every paid call (`ensure_budget`) and logs every spend (`record_cost`).

## Run locally

```bash
docker compose up -d --build
./scripts/smoke.sh          # checks every service; prints ALL OK
```

| Service | What | URL (localhost only) |
|---|---|---|
| api | FastAPI job API; `GET /health` checks db, redis and the worker count | http://127.0.0.1:8400/health |
| worker | RQ worker (same image as api), queue `default` | — |
| admin | Next.js admin page | http://127.0.0.1:3400 |
| renderer | Remotion + Chrome headless shell; `GET /health` | http://127.0.0.1:3500/health |
| postgres | Postgres 17, volume `pgdata` | `127.0.0.1:5442` (for host-side alembic/pytest) |
| redis | Redis 7 (job queue) | Docker network only |

The ports avoid the gta-radar and numa stacks already running on this machine.

## Database

SQLAlchemy models live in `api/studio/db.py`, and Alembic migrations in `api/migrations/`. The api container runs `alembic upgrade head` on startup.

| Table | Holds | Hard rules enforced by Postgres |
|---|---|---|
| `jobs` | topic or Content Package input, format, target length, status/step | format and status from fixed lists |
| `facts` | `verified` (Trend Radar) vs `unverified-context` (research) | unverified facts **must** have `source_url` |
| `scripts` | versioned script JSON per job | — |
| `assets` | provenance log: source, source ref, licence, path, meta | licence required; source must be `own`, `trend_radar`, `pexels`, `ai_generated`, `tts` or `royalty_free`. YouTube and gameplay are rejected. |
| `costs` | every paid call: service, provider, USD, quantity | `usd >= 0`; indexed for month-to-date per service |
| `outputs` | MP4, thumbnails, titles, description, checklist, review | exactly 3 titles; description must contain "is an AI character."; review defaults to `pending` |

```bash
cd api
uv sync
uv run alembic upgrade head        # or: alembic revision --autogenerate -m "..."
uv run pytest                      # uses its own studio_test database
```

## Secrets

Secrets go in `.env` only, which git ignores. `.env.example` lists every variable, and a test fails if the code reads one that isn't listed.

## Input (V3.1)

`POST /jobs` takes `{"input": "...", "format": "radar_report", "target_seconds": 50}` (format and length are optional). `input` is one topic line, or a whole Trend Radar Content Package: the JSON from Trend Radar's `GET /api/admin/content-package`, or the Markdown it renders. The package's facts are stored as `verified`, word for word.

```bash
curl -s localhost:8000/api/admin/content-package | jq '{input: tojson}' | curl -s -X POST 127.0.0.1:8400/jobs -H 'content-type: application/json' -d @-
```

## Research (V3.2, runs on the Mac)

Research runs on **your own Claude Code** (`claude -p`, your claude.ai login; `ANTHROPIC_API_KEY` is never passed on), with web search, so it costs $0. The model is `CLAUDE_MODEL` (default `haiku`). It returns up to 8 one-sentence notes, each with the URL of the page that says it, stored as `unverified-context` facts. The code drops user-generated platforms (YouTube, Reddit, X...), rumour/leak wording and homepage citations.

```bash
cd api && uv run python -m studio.research <job_id>   # prints kept and dropped notes
```

## Script (V3.3, runs on the Mac)

```bash
cd api && uv run python -m studio.script <job_id>   # prints titles, thumbnail text and the timed scenes
```

Claude Code drafts the script as structured JSON: scenes in arc order (hook → what → why → next), each on a `desk` (reporter + pose), `card` (fact/note IDs) or `headline` shot. `studio/script.py: validate` then checks the hard rules in code: every number is a verified fact, the arc is complete, the reporter is on screen at the start and end, at least one data card, on-screen text ≤ 6 words, and 3 titles plus thumbnail text unlike the last 7 videos. A failed draft goes back with its problems (3 tries). The opener and sign-off are added by code, word for word.

## Voice and talking clip (free)

```bash
# one-time model download (data only, git-ignored): the v1.1 export includes phoneme durations for lip-sync
mkdir -p models/kokoro && cd models/kokoro
curl -fsSLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.onnx
curl -fsSLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd ../../api
uv run python -m studio.voice            # test line -> renderer/public/test/line.wav + renderer/out/props.json
cd .. && docker compose run --rm -T -v "$PWD/renderer/src:/app/src" -v "$PWD/renderer/public:/app/public" \
  -v "$PWD/renderer/out:/app/out" renderer npx remotion render src/index.ts TalkingClip out/talk-test.mp4 --props=out/props.json
```
