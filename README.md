# Video Studio

Turns a topic (or a Trend Radar Content Package) into a finished 1080×1920 short hosted by our AI gamer-dog character. It researches, writes, voices, animates and edits the video, then hands it over for human review. **Nothing is published automatically.**

- Spec: [docs/BRIEF.md](docs/BRIEF.md)
- Plan & progress: [docs/PLAN.md](docs/PLAN.md)
- Character bible: [docs/CHARACTER.md](docs/CHARACTER.md)

## Status

Done: V1.1 (repo), V1.2 (Docker Compose), and the V2.1 draft (character bible). Next comes V1.3 (database).

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
| postgres | Postgres 17, volume `pgdata` | Docker network only |
| redis | Redis 7 (job queue) | Docker network only |

The ports avoid the gta-radar and numa stacks already running on this machine.

## Secrets

Secrets go in `.env` only, which git ignores. `.env.example` arrives in V1.4.
