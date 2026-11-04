import re
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import text

from studio import config
from studio.costs import BudgetExceeded, ensure_budget, month_to_date, record_cost
from studio.db import engine

REPO = Path(__file__).parents[2]


def test_default_caps_are_zero():
    # nothing paid happens unless you raise a cap in .env
    assert sum(config.COST_CAPS_USD.values()) == 0


def test_env_example_lists_every_setting_the_code_reads():
    example = set(re.findall(r"^#?\s*([A-Z][A-Z0-9_]+)=", (REPO / ".env.example").read_text(), re.M))
    code = "".join(p.read_text() for p in (REPO / "api/studio").glob("*.py"))
    read = set(re.findall(r'os\.environ(?:\.get\(|\[)"([A-Z0-9_]+)"', code))
    read |= {f"CAP_{s.upper()}_USD" for s in config.COST_CAPS_USD}  # built with an f-string
    compose = set(re.findall(r"\$\{([A-Z0-9_]+)", (REPO / "docker-compose.yml").read_text()))
    assert read | compose <= example, f"missing from .env.example: {(read | compose) - example}"


def test_character_name_is_only_hardcoded_in_config():
    sources = [*(REPO / "api/studio").glob("*.py"), *(REPO / "admin/app").glob("*.tsx"), *(REPO / "renderer/src").glob("*.tsx")]
    offenders = [p.name for p in sources if config.CHARACTER_NAME in p.read_text() and p.name != "config.py"]
    assert offenders == []


def test_budget_guard_stops_at_cap(monkeypatch):
    monkeypatch.setitem(config.COST_CAPS_USD, "llm", Decimal("4"))
    with engine.begin() as c:
        c.execute(text("delete from costs where service = 'llm'"))
        # last month's spend must not count against this month
        c.execute(text("insert into costs (service, provider, usd, created_at) values ('llm', 'anthropic', 100, now() - interval '40 days')"))
    record_cost("llm", "anthropic", "3.99", unit="tokens")
    assert month_to_date("llm") == Decimal("3.99")
    ensure_budget("llm", "0.01")  # exactly at the cap is fine
    with pytest.raises(BudgetExceeded, match="llm monthly cap"):
        ensure_budget("llm", "0.02")
