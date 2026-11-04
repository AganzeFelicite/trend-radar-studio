"""V3.2: research notes are cited, reputable and stored as unverified-context; Claude Code never bills an API key."""

import json
import subprocess
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from studio import llm, research
from studio.db import Fact, engine
from studio.inputs import create_job

PKG = (Path(__file__).parent / "fixtures" / "package.json").read_text()
NOTES = [
    {"claim": "Pre-load opens November 10 on PS5 and Xbox Series X|S.", "source_url": "https://www.rockstargames.com/newswire/x"},
    {"claim": "The install needs about 200 GB.", "source_url": "https://www.ign.com/articles/gta-6-size"},
    {"claim": "A video says the map is huge.", "source_url": "https://www.youtube.com/watch?v=abc"},
    {"claim": "Insider claims a delay.", "source_url": "https://www.gamesradar.com/x"},
    {"claim": "Leaked footage shows a new city.", "source_url": "https://www.gamesradar.com/y"},
    {"claim": "No link for this one.", "source_url": "rockstargames.com"},
    {"claim": "Fan theory.", "source_url": "https://old.reddit.com/r/GTA6/abc"},
    {"claim": "A banner on the front page.", "source_url": "https://news.xbox.com/en-us/"},
]


def test_notes_are_cited_reputable_and_stored(monkeypatch):
    seen = {}
    monkeypatch.setattr(llm, "ask", lambda p, schema, **kw: seen.update(prompt=p, tools=kw["tools"]) or {"notes": NOTES})
    job = create_job(PKG)
    kept, dropped = research.research(job.id)
    assert [n["source_url"] for n in kept] == [NOTES[0]["source_url"], NOTES[1]["source_url"]]
    assert [why for _, why in dropped] == ["not a reputable source (youtube.com)", "rumour/leak/piracy wording",
                                           "rumour/leak/piracy wording", "no source URL", "not a reputable source (old.reddit.com)",
                                           "homepage, not the page that says it"]
    assert "Pre-load: share of the GTA 6 conversation, 24h: 11.5%" in seen["prompt"]  # verified data given as context
    assert seen["tools"] == "WebSearch,WebFetch"
    with Session(engine) as s:
        rows = s.scalars(select(Fact).where(Fact.job_id == job.id)).all()
    assert sum(f.kind == "verified" for f in rows) == 6  # package facts untouched
    research_rows = [f for f in rows if f.kind == "unverified-context" and "rockstargames.com/newswire/example" not in f.source_url]
    assert [(f.text, f.source_url) for f in research_rows] == [(n["claim"], n["source_url"]) for n in NOTES[:2]]


def test_ask_uses_the_subscription_and_logs_zero_cost(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-should-never-be-used")
    calls = []

    def fake_run(cmd, **kw):
        calls.append((cmd, kw))
        out = {"type": "result", "is_error": False, "structured_output": {"notes": []}, "num_turns": 3, "total_cost_usd": 0.12}
        return subprocess.CompletedProcess(cmd, 0, json.dumps(out), "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with engine.begin() as c:
        c.execute(text("delete from costs where service = 'llm'"))
    assert llm.ask("hi", {"type": "object"}, step="test") == {"notes": []}
    cmd, kw = calls[0]
    assert "ANTHROPIC_API_KEY" not in kw["env"]
    assert cmd[:2] == ["claude", "-p"] and "--json-schema" in cmd
    assert cmd[cmd.index("--tools") + 1] == cmd[cmd.index("--allowedTools") + 1]  # available tools are also allowed
    with engine.connect() as c:
        assert c.execute(text("select usd, note from costs where service = 'llm'")).one() == (0, "test · haiku · subscription; API-equivalent $0.1200")


def test_denied_tool_is_an_error(monkeypatch):
    out = {"is_error": False, "structured_output": {"notes": []}, "permission_denials": [{"tool_name": "WebSearch"}]}
    monkeypatch.setattr(subprocess, "run", lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, json.dumps(out), ""))
    try:
        llm.ask("hi", {}, tools="WebSearch")
    except llm.LLMError as e:
        assert "WebSearch" in str(e)
    else:
        raise AssertionError("denied tool not reported")
