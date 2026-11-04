"""V3.7 + V3.8: our own B-roll (D18). Every card or headline scene of the script becomes a full-frame clip from
renderer/src/Broll.tsx, timed to the voice. Data cards show Trend Radar's verified facts exactly as given. Note cards
show only the outlets as receipts, never a research number. Each clip is logged in provenance as our own work.
Run on the host (needs Docker): `uv run python -m studio.broll <job_id>`."""

import json
import subprocess
import sys
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from studio import script
from studio.clip import REPO
from studio.config import STORAGE
from studio.costs import ensure_budget, record_cost
from studio.db import Asset, Job, engine
from studio.voice import PAUSE

LICENSE = "Own work: our graphics (renderer/src/Broll.tsx), Anton font (SIL OFL 1.1)"


def scene_props(scene: dict, facts: dict[str, dict], notes: dict[str, tuple[str, str]], scores_at: str | None) -> dict:
    rows = [{"topic": f["label"].split(": ", 1)[0], "metric": f["label"].split(": ", 1)[-1], "value": f["value"]}
            for i in scene.get("fact_ids", []) if (f := facts.get(i))]
    urls = [notes[n][1] for n in scene.get("note_ids", []) if n in notes]
    sources = list(dict.fromkeys((urlparse(u).hostname or "").removeprefix("www.") for u in urls))
    title = scene.get("text") or " & ".join(dict.fromkeys(r["topic"] for r in rows)) or "What the sources say"
    footer = f"Data: Trend Radar · {scores_at}" if rows else "Sources linked in the description"
    return {"kind": "card" if scene["shot"] == "card" else "headline", "title": title, "rows": rows,
            "sources": sources, "footer": footer if scene["shot"] == "card" else "",
            "duration": round(scene["end"] - scene["start"] + PAUSE, 3)}


def broll(job_id: int) -> list[dict]:
    """-> [{scene, start, end, path}] for every card/headline scene, rendered with one Remotion bundle."""
    ensure_budget("video", 0)
    job_dir = STORAGE / "jobs" / str(job_id)
    track = json.loads((job_dir / "voice.json").read_text())
    ctx = script.context(job_id)
    with Session(engine) as s:
        pkg = s.get(Job, job_id).input
    facts = {f["id"]: f for f in pkg.get("facts", []) if f["type"] == "verified"}
    items = [{"id": f"scene-{i:02d}", "scene": i, "start": sc["start"], "end": sc["end"],
              "props": scene_props(sc, facts, ctx["notes"], pkg.get("scores_at")), "cites": sc}
             for i, sc in enumerate(track["scenes"]) if sc["shot"] in ("card", "headline")]
    (job_dir / "broll.json").write_text(json.dumps([{"id": x["id"], "props": x["props"]} for x in items]))
    run = subprocess.run(
        ["docker", "compose", "-f", str(REPO / "docker-compose.yml"), "run", "--rm", "-T",
         "-v", f"{REPO / 'renderer' / 'src'}:/app/src:ro",
         "-v", f"{REPO / 'renderer' / 'render-scenes.mjs'}:/app/render-scenes.mjs:ro",
         "-v", f"{REPO / 'renderer' / 'public' / 'fonts'}:/app/public/fonts:ro",
         "-v", f"{job_dir}:/app/out", "renderer", "node", "render-scenes.mjs", "out/broll.json", "out/broll"],
        capture_output=True, text=True, timeout=3600)
    if run.returncode:
        raise RuntimeError(f"broll render failed: {(run.stderr or run.stdout)[-800:]}")
    out = []
    with Session(engine) as s, s.begin():
        for x in items:
            path = job_dir / "broll" / f"{x['id']}.mp4"
            if not path.exists():
                raise RuntimeError(f"broll render produced no {path.name}")
            kind = "data_card" if x["props"]["rows"] else "broll"
            s.add(Asset(job_id=job_id, kind=kind, source="own", license=LICENSE, path=str(path),
                        source_ref=f"remotion Broll · scene {x['scene']} · facts {x['cites'].get('fact_ids', [])}",
                        meta={"title": x["props"]["title"], "facts": x["cites"].get("fact_ids", []),
                              "notes": [ctx["notes"][n][1] for n in x["cites"].get("note_ids", []) if n in ctx["notes"]]}))
            out.append({"scene": x["scene"], "start": x["start"], "end": x["end"], "path": str(path)})
    record_cost("video", "remotion-local", 0, job_id=job_id, quantity=sum(x["props"]["duration"] for x in items),
                unit="seconds", note=f"{len(items)} B-roll clips, local, free")
    return out


if __name__ == "__main__":
    for x in broll(int(sys.argv[1])):
        print(f"{x['start']:6.2f}-{x['end']:6.2f}  {x['path']}")
