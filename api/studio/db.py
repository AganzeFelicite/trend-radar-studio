import os
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    Text,
    UniqueConstraint,
    create_engine,
    func,
    select,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from studio.config import COST_CAPS_USD

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://studio:studio@localhost:5442/studio")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

FORMATS = ("radar_report", "make_this_now", "myth_or_real", "weekly_recap")
JOB_STATUSES = ("queued", "running", "blocked", "failed", "review")
FACT_KINDS = ("verified", "unverified-context")
ASSET_KINDS = ("character", "cutaway", "voice", "avatar_clip", "broll", "data_card", "music", "sfx", "thumbnail")
# Allowed visual/audio sources (brief §2). "gameplay" is deliberately absent until V6.4 is approved.
ASSET_SOURCES = ("own", "trend_radar", "pexels", "pixabay", "official_rockstar", "ai_generated", "tts", "royalty_free")
REVIEW_STATES = ("pending", "approved", "rejected")
COST_SERVICES = tuple(COST_CAPS_USD)  # one list: every paid service has a cap


def one_of(column: str, values: tuple[str, ...]) -> CheckConstraint:
    return CheckConstraint(f"{column} in ({', '.join(repr(v) for v in values)})", name=f"{column}_allowed")


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(table_name)s_%(column_0_name)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


def _now() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now())


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        one_of("input_kind", ("topic", "package")),
        one_of("format", FORMATS),
        one_of("status", JOB_STATUSES),
        CheckConstraint("target_seconds between 15 and 120", name="target_seconds_range"),
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    input_kind: Mapped[str] = mapped_column(Text)
    input: Mapped[dict] = mapped_column(JSONB)  # {"topic": ...} or the parsed Content Package
    format: Mapped[str] = mapped_column(Text)
    target_seconds: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(Text, server_default="queued")
    step: Mapped[str | None] = mapped_column(Text)  # current pipeline step, for the progress view
    error: Mapped[str | None] = mapped_column(Text)  # failure or safety-gate reason
    created_at: Mapped[datetime] = _now()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Fact(Base):
    __tablename__ = "facts"
    __table_args__ = (
        one_of("kind", FACT_KINDS),
        # Brief §2: every claim beyond Trend Radar's verified facts must be cited.
        CheckConstraint("kind = 'verified' or source_url is not null", name="unverified_needs_source"),
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(Text)
    text: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = _now()


class Script(Base):
    __tablename__ = "scripts"
    __table_args__ = (UniqueConstraint("job_id", "version"),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer)
    body: Mapped[dict] = mapped_column(JSONB)  # validated script: timed scenes, lines, visual cues
    created_at: Mapped[datetime] = _now()


class Asset(Base):
    """Provenance log: one row per asset used anywhere. No licence, no row."""

    __tablename__ = "assets"
    __table_args__ = (
        one_of("kind", ASSET_KINDS),
        one_of("source", ASSET_SOURCES),
        CheckConstraint("license <> ''", name="license_present"),
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    # Nullable: master character assets are shared by every job. No cascade: provenance outlives jobs.
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"), index=True)
    kind: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(Text)
    source_ref: Mapped[str] = mapped_column(Text)  # URL or provider ID
    license: Mapped[str] = mapped_column(Text)
    license_url: Mapped[str | None] = mapped_column(Text)
    path: Mapped[str | None] = mapped_column(Text)
    meta: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))  # prompt, seed, photographer...
    acquired_at: Mapped[datetime] = _now()


class Cost(Base):
    __tablename__ = "costs"
    __table_args__ = (
        one_of("service", COST_SERVICES),
        CheckConstraint("usd >= 0", name="usd_non_negative"),
        Index("ix_costs_service_created_at", "service", "created_at"),  # month-to-date per service
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"), index=True)  # null = tests, subscriptions
    service: Mapped[str] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(Text)
    usd: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    unit: Mapped[str | None] = mapped_column(Text)  # seconds, characters, tokens, images
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = _now()


class Output(Base):
    __tablename__ = "outputs"
    __table_args__ = (
        one_of("review", REVIEW_STATES),
        CheckConstraint("cardinality(titles) = 3", name="three_titles"),
        # Brief §2: AI disclosure in every description ("<CHARACTER_NAME> is an AI character.").
        CheckConstraint("description like '%is an AI character.%'", name="ai_disclosure"),
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), index=True)
    video_path: Mapped[str] = mapped_column(Text)
    thumbnail_paths: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default=text("'{}'::text[]"))
    titles: Mapped[list[str]] = mapped_column(ARRAY(Text))
    caption: Mapped[str | None] = mapped_column(Text)
    hashtags: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default=text("'{}'::text[]"))
    description: Mapped[str] = mapped_column(Text)
    checklist: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    review: Mapped[str] = mapped_column(Text, server_default="pending")  # nothing publishes automatically
    review_note: Mapped[str | None] = mapped_column(Text)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = _now()


class Unlicensed(RuntimeError):
    """Raised before a render that would use a file with no licence entry in the provenance log."""


def ensure_licensed(job_id: int, paths) -> None:
    """Brief §2: refuse to render if any asset lacks a licence entry. Shared assets (job_id null) count for every job."""
    with Session(engine) as s:
        logged = set(s.scalars(select(Asset.path).where((Asset.job_id == job_id) | Asset.job_id.is_(None))))
    if missing := sorted(str(p) for p in paths if str(p) not in logged):
        raise Unlicensed(f"refusing to render: no licence entry for {', '.join(missing)}")
