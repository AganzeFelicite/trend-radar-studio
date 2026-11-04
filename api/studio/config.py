"""All tunable settings. Values come from .env (see .env.example); defaults match docs/PLAN.md decisions."""

import os
from decimal import Decimal

CHARACTER_NAME = os.environ.get("CHARACTER_NAME", "Big Dog")

# --- Providers (D5-D7) ---
LLM_MODEL = os.environ.get("LLM_MODEL", "claude-opus-5-5")  # research + script
CLASSIFIER_MODEL = os.environ.get("CLASSIFIER_MODEL", "claude-opus-5-5")  # sensitive-topic gate
TTS_PROVIDER = os.environ.get("TTS_PROVIDER", "elevenlabs")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "")  # set in V2.3
AVATAR_MODEL = os.environ.get("AVATAR_MODEL", "fal-ai/kling-video/ai-avatar/v2/standard")  # V2.4 picks std/pro
IMAGE_MODEL = os.environ.get("IMAGE_MODEL", "")  # set after D5

# --- Monthly cost caps in USD (D8: $20 total). Jobs stop with a clear reason when a cap is hit. ---
_DEFAULT_CAPS = {"llm": "4", "tts": "6", "avatar": "8", "image": "2", "video": "0"}
COST_CAPS_USD = {s: Decimal(os.environ.get(f"CAP_{s.upper()}_USD", d)) for s, d in _DEFAULT_CAPS.items()}

# --- Safety gate inputs (brief §2; V3.4 adds the matcher and the AI classifier on top) ---
SENSITIVE_TOPICS = {
    "finance": ("stock market", "stocks", "crypto", "bitcoin", "ethereum", "nft", "invest", "investing",
                "investment", "trading", "forex", "loan", "mortgage", "taxes", "retirement", "dividend"),
    "money-making": ("make money", "side hustle", "passive income", "get rich", "earn money", "income stream"),
    "health": ("diet", "weight loss", "supplement", "vaccine", "mental health", "therapy", "symptom",
               "disease", "cancer", "fitness plan"),
    "medical": ("medical", "medicine", "medication", "dosage", "diagnosis", "treatment", "prescription"),
    "legal": ("lawsuit", "legal advice", "attorney", "lawyer", "court case", "sue ", "custody"),
}
# Allowed only when a cited, reputable source supports them; rumours/leaks are never allowed.
SENSATIONAL_WORDS = ("cancelled", "canceled", "leaked", "leak", "confirmed", "breaking", "insider",
                     "rumor", "rumour", "exposed", "you won't believe", "before it's too late",
                     "last chance", "urgent")
