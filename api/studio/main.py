import os

from fastapi import FastAPI, Response
from redis import Redis
from rq import Worker
from sqlalchemy import text

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
