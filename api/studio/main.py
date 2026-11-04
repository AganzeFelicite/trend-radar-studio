import os

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
from redis import Redis
from rq import Worker
from sqlalchemy import text

from studio import inputs
from studio.db import engine

app = FastAPI(title="Video Studio API")
redis = Redis.from_url(os.environ["REDIS_URL"], socket_timeout=2)


@app.get("/health")
def health(response: Response):
    checks = {"db": "ok", "redis": "ok", "workers": 0}
    try:
        with engine.connect() as conn:
            conn.execute(text("select 1"))
    except Exception as e:
        checks["db"] = type(e).__name__  # class name only: never leak the DSN
    try:
        redis.ping()
        checks["workers"] = Worker.count(connection=redis)
    except Exception as e:
        checks["redis"] = type(e).__name__
    ok = checks["db"] == checks["redis"] == "ok"
    response.status_code = 200 if ok else 503
    return {"status": "ok" if ok else "degraded", **checks}


class JobIn(BaseModel):
    input: str  # a topic line, or a Content Package (JSON or Markdown)
    format: str | None = None
    target_seconds: int | None = Field(None, ge=15, le=120)


@app.post("/jobs", status_code=201)
def create_job(body: JobIn):
    try:
        job = inputs.create_job(body.input, body.format, body.target_seconds)
    except ValueError as e:
        raise HTTPException(422, str(e))
    facts = len(job.input.get("facts", []))
    return {"id": job.id, "input_kind": job.input_kind, "format": job.format, "target_seconds": job.target_seconds,
            "status": job.status, "facts": facts}
