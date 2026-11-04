# Video Studio

Turns a topic (or a Trend Radar Content Package) into a finished 1080×1920 short hosted by our AI gamer-dog character. It researches, writes, voices, animates and edits the video, then hands it over for human review. **Nothing is published automatically.**

- Spec: [docs/BRIEF.md](docs/BRIEF.md)
- Plan & progress: [docs/PLAN.md](docs/PLAN.md)
- Character bible: [docs/CHARACTER.md](docs/CHARACTER.md)

## Status

Phase V1 is done (repo, Docker Compose, database, config), along with the V2.1 draft (character bible). Next comes V2.2 (character sheet), once you approve the bible.

## Config

```bash
cp .env.example .env   # then paste your API keys
```

All settings live in `api/studio/config.py`, which reads `.env`. They are the character name, provider and model choices, monthly cost caps per service ($20 total by default), the sensitive-topic blocklist and the sensational-word list. `studio/costs.py` checks the cap before every paid call (`ensure_budget`) and logs every spend (`record_cost`).

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
