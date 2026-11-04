"""All tunable settings. Values come from .env (see .env.example); defaults match docs/PLAN.md decisions."""

import os
from pathlib import Path
from decimal import Decimal

CHARACTER_NAME = os.environ.get("CHARACTER_NAME", "GameReporter")
OPENER = f"Ping check — {CHARACTER_NAME}'s online!"  # your picks (docs/CHARACTER.md §8)
SIGNOFF = f"{CHARACTER_NAME}, logging off. Stay locked in."

# --- Providers: none paid (D14-D16). Scripts/research run on your Claude Code (`claude -p`),
# voice on local Kokoro, the reporter is drawn in code. Add a setting here only when a real choice appears.
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "haiku")  # your pick; lightest on the Pro plan's limits
RESEARCH_MAX_SEARCHES = 3  # your pick: up to 3 searches per video

# --- Monthly cost caps in USD. Default $0: any paid call is refused until you raise its cap in .env. ---
_DEFAULT_CAPS = {"llm": "0", "tts": "0", "avatar": "0", "image": "0", "video": "0"}
COST_CAPS_USD = {s: Decimal(os.environ.get(f"CAP_{s.upper()}_USD", d)) for s, d in _DEFAULT_CAPS.items()}

# --- Safety gate inputs (brief §2; V3.4 adds the matcher and the AI classifier on top) ---
SENSITIVE_TOPICS = {
    "finance": ("stock market", "stocks", "crypto", "bitcoin", "ethereum", "nft", "invest", "investing",
                "investment", "trading", "forex", "loan", "mortgage", "taxes", "retirement", "dividend"),
    "money-making": ("make money", "side hustle", "passive income", "get rich", "earn money", "income stream"),
    "health": ("diet", "weight loss", "supplement", "vaccine", "mental health", "therapy", "symptom",
               "disease", "cancer", "fitness plan"),
    "medical": ("medical", "medicine", "medication", "dosage", "diagnosis", "treatment", "prescription"),
    "legal": ("lawsuit", "legal advice", "attorney", "lawyer", "court case", "sue", "custody"),
}
# Sensational framing (V3.4). These need a cited note that says so, in the same scene; never in titles or thumbnails.
# Negated uses ("not confirmed yet") are always fine: that's the honest line.
SENSATIONAL_CITED_ONLY = ("confirmed", "cancelled", "canceled", "delayed")
# Never allowed, cited or not: no rumours, leaks, "BREAKING" banners or fake urgency (brief §2, D10).
SENSATIONAL_NEVER = ("leaked", "leaks", "leak", "rumor", "rumors", "rumour", "rumours", "insider", "breaking", "exposed",
                     "you won't believe", "before it's too late", "last chance", "urgent", "act now")

# --- Research (V3.2): only reputable, citable sources. User-generated platforms are for reading trends, never a source.
RESEARCH_BLOCKED_DOMAINS = ("youtube.com", "youtu.be", "tiktok.com", "twitch.tv", "reddit.com", "x.com", "twitter.com",
                            "facebook.com", "instagram.com", "threads.net", "bsky.app", "discord.com", "discord.gg",
                            "4chan.org", "pastebin.com", "fandom.com")
RESEARCH_EXCLUDE_WORDS = r"\b(leak\w*|rumou?r\w*|insider|pira\w+|jailbreak\w*|cheat\w*|datamin\w+)"

# --- Files and local tools (all on this Mac) ---
STORAGE = Path(os.environ.get("STORAGE_DIR", Path(__file__).parents[2] / "storage"))  # per-job files, git-ignored
WHISPER_PYTHON = os.environ.get("WHISPER_PYTHON", str(Path.home() / ".local/share/uv/tools/mlx-whisper/bin/python"))
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "mlx-community/whisper-large-v3-turbo")  # same as your FilmCraft pipeline
_HOME = Path.home()
# The final edit runs your FilmCraft pipeline headless (D16): the filmcraft-commentary-short skill's build.py, the
# Studio repo's render.py (picture from FilmCraft, audio mixed by ffmpeg) and the cleared Sound Library.
FILMCRAFT_CLI = os.environ.get("FILMCRAFT_CLI", str(_HOME / ".local/bin/filmcraft-cli"))
FILMCRAFT_SKILL = Path(os.environ.get("FILMCRAFT_SKILL", _HOME / ".claude/skills/filmcraft-commentary-short"))
FILMCRAFT_RENDER = Path(os.environ.get("FILMCRAFT_RENDER", _HOME / "Desktop/thevault/content-creation/editing/Studio/render.py"))
SOUND_LIBRARY = Path(os.environ.get("SOUND_LIBRARY", _HOME / "Desktop/thevault/content-creation/editing/Video Editing Sound Library"))
