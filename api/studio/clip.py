"""V3.6: the talking reporter. Remotion renders renderer/src/TalkingClip.tsx over the job's whole voice track:
the character drawn in code, lip-synced from the mouth cues, with reaction poses on desk scenes. It's the A-roll
your FilmCraft edit cuts away from on card and headline scenes. $0, local.
The swap point for another avatar provider is this one function: voice.json in, reporter.mp4 out.
Run on the host (needs Docker): `uv run python -m studio.clip <job_id>`."""

import json
import subprocess
import sys
from pathlib import Path

from sqlalchemy.orm import Session

from studio.config import STORAGE
from studio.costs import ensure_budget, record_cost
from studio.db import Asset, engine

REPO = Path(__file__).parents[2]
REACTION = 2.0  # seconds a reaction pose holds at the start of its desk scene, then back to talking
LICENSE = "Own work: character drawn in code (renderer/src/Reporter.tsx); voice Apache-2.0 (Kokoro)"


def props(track: dict) -> dict:
    poses = [{"start": s["start"], "end": round(min(s["end"], s["start"] + REACTION), 3), "pose": s["pose"]}
             for s in track["scenes"] if s["shot"] == "desk" and s.get("pose", "talk") != "talk"]
    return {"audio": "job/voice.wav", "duration": track["duration"], "cues": track["cues"], "poses": poses}


def talking_clip(job_id: int) -> Path:
    ensure_budget("avatar", 0)
    job_dir = STORAGE / "jobs" / str(job_id)
    track = json.loads((job_dir / "voice.json").read_text())
    (job_dir / "talk-props.json").write_text(json.dumps(props(track)))
    run = subprocess.run(
        ["docker", "compose", "-f", str(REPO / "docker-compose.yml"), "run", "--rm", "-T",
         "-v", f"{REPO / 'renderer' / 'src'}:/app/src:ro",
         "-v", f"{job_dir / 'voice.wav'}:/app/public/job/voice.wav:ro",
         "-v", f"{job_dir}:/app/out", "renderer",
         "npx", "remotion", "render", "src/index.ts", "TalkingClip", "out/reporter.mp4", "--props=out/talk-props.json"],
        capture_output=True, text=True, timeout=1800)
    out = job_dir / "reporter.mp4"
    if run.returncode or not out.exists():
        raise RuntimeError(f"remotion render failed: {(run.stderr or run.stdout)[-800:]}")
    with Session(engine) as s, s.begin():
        s.add(Asset(job_id=job_id, kind="avatar_clip", source="own", source_ref="remotion TalkingClip + voice.wav",
                    license=LICENSE, path=str(out), meta={"seconds": track["duration"]}))
    record_cost("avatar", "remotion-local", 0, job_id=job_id, quantity=track["duration"], unit="seconds",
                note="drawn in code, local, free")
    return out


if __name__ == "__main__":
    print(talking_clip(int(sys.argv[1])))
