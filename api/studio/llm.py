"""Your own Claude Code, headless (D15): research and scripts run on your claude.ai login, never a paid API key.
Runs on the Mac host, where Claude Code is installed and logged in."""

import json
import os
import subprocess
import tempfile

from studio.config import CLAUDE_MODEL
from studio.costs import record_cost


class LLMError(RuntimeError):
    pass


def ask(prompt: str, schema: dict, *, tools: str = "", max_turns: int = 4, job_id: int | None = None,
        step: str = "") -> dict:
    """One `claude -p` call whose final answer is validated against `schema`. Logged as a $0 llm cost."""
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}  # subscription only, never API billing
    with tempfile.TemporaryDirectory() as empty:  # no CLAUDE.md, no project settings, no hooks
        run = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json", "--json-schema", json.dumps(schema),
             "--tools", tools, "--allowedTools", tools, "--model", CLAUDE_MODEL, "--max-turns", str(max_turns), "--no-session-persistence",
             "--strict-mcp-config", "--setting-sources", "project"],
            cwd=empty, env=env, capture_output=True, text=True, timeout=900)
    try:
        out = json.loads(run.stdout)
    except ValueError:
        raise LLMError(f"claude -p failed ({run.returncode}): {(run.stderr or run.stdout)[-500:]}")
    if out.get("is_error") or out.get("structured_output") is None:
        raise LLMError(f"claude -p {out.get('subtype')}: {str(out.get('result'))[-500:]}")
    if out.get("permission_denials"):  # a blocked tool makes the answer silently empty
        raise LLMError(f"claude -p was denied {sorted({d['tool_name'] for d in out['permission_denials']})}")
    record_cost("llm", "claude-code", 0, job_id=job_id, quantity=out.get("num_turns"), unit="turns",
                note=f"{step} · {CLAUDE_MODEL} · subscription; API-equivalent ${out.get('total_cost_usd', 0):.4f}")
    return out["structured_output"]
