import os
from pathlib import Path

# Tests get their own database so they never touch real jobs or provenance.
ADMIN_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://studio:studio@localhost:5442/studio")
os.environ["DATABASE_URL"] = ADMIN_URL.rsplit("/", 1)[0] + "/studio_test"

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402

with create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT").connect() as c:
    if not c.scalar(text("select 1 from pg_database where datname = 'studio_test'")):
        c.execute(text("create database studio_test"))


@pytest.fixture(scope="session")
def alembic_cfg():
    return Config(str(Path(__file__).parents[1] / "alembic.ini"))


@pytest.fixture(scope="session", autouse=True)
def migrated(alembic_cfg):
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")  # schema comes from the migrations, not create_all
