import json

import pytest
from alembic import command
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from studio.db import engine

TABLES = {"jobs", "facts", "scripts", "assets", "costs", "outputs"}


def tables() -> set[str]:
    return set(inspect(engine).get_table_names()) - {"alembic_version"}


def run(sql: str, **params):
    with engine.begin() as c:
        return c.execute(text(sql), params)


def violates(sql: str, **params):
    with pytest.raises(IntegrityError):
        run(sql, **params)


@pytest.fixture
def job_id() -> int:
    return run(
        "insert into jobs (input_kind, input, format, target_seconds)"
        " values ('topic', cast(:input as jsonb), 'radar_report', 45) returning id",
        input=json.dumps({"topic": "test"}),
    ).scalar_one()


def test_migrations_down_and_up_clean(alembic_cfg):
    command.downgrade(alembic_cfg, "base")
    assert tables() == set()
    command.upgrade(alembic_cfg, "head")
    assert tables() == TABLES


ASSET = "insert into assets (kind, source, source_ref, license) values (:kind, :source, 'ref-1', :license)"
GOOD_ASSET = {"kind": "broll", "source": "pexels", "license": "Pexels License"}


@pytest.mark.parametrize(
    "bad",
    [
        {"license": None},  # no licence entry, no asset
        {"license": ""},
        {"source": "youtube"},  # third-party footage is never an allowed source
        {"source": "gameplay"},  # blocked until V6.4 is approved
    ],
)
def test_asset_provenance_rules(bad):
    violates(ASSET, **{**GOOD_ASSET, **bad})


def test_licensed_asset_is_accepted():
    run(ASSET, **GOOD_ASSET)


def test_unverified_fact_needs_source(job_id):
    violates("insert into facts (job_id, kind, text) values (:j, 'unverified-context', 'a claim')", j=job_id)
    run("insert into facts (job_id, kind, text) values (:j, 'verified', 'a Trend Radar fact')", j=job_id)
    run(
        "insert into facts (job_id, kind, text, source_url) values (:j, 'unverified-context', 'a claim', 'https://example.org')",
        j=job_id,
    )


OUTPUT = "insert into outputs (job_id, video_path, titles, description) values (:j, 'v.mp4', :titles, :d)"


def test_output_needs_ai_disclosure_and_three_titles(job_id):
    disclosed = "Big Dog is an AI character."
    violates(OUTPUT, j=job_id, titles=["a", "b", "c"], d="no disclosure")
    violates(OUTPUT, j=job_id, titles=["a", "b"], d=disclosed)
    row = run(OUTPUT + " returning review", j=job_id, titles=["a", "b", "c"], d=disclosed).scalar_one()
    assert row == "pending"  # nothing is approved by default


def test_cost_cannot_be_negative():
    violates("insert into costs (service, provider, usd) values ('tts', 'elevenlabs', -1)")
    run("insert into costs (service, provider, usd) values ('tts', 'elevenlabs', 0.0123)")
