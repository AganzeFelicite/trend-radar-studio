"""All tunable settings. Values come from .env (see .env.example); defaults match docs/PLAN.md decisions."""

import os
from decimal import Decimal

CHARACTER_NAME = os.environ.get("CHARACTER_NAME", "GameReporter")

# --- Providers: none paid (D14-D16). Scripts/research run on your Claude Code (`claude -p`),
# voice on local Kokoro, the reporter is drawn in code. Add a setting here only when a real choice appears.

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
    "legal": ("lawsuit", "legal advice", "attorney", "lawyer", "court case", "sue ", "custody"),
}
# Allowed only when a cited, reputable source supports them; rumours/leaks are never allowed.
SENSATIONAL_WORDS = ("cancelled", "canceled", "leaked", "leak", "confirmed", "breaking", "insider",
                     "rumor", "rumour", "exposed", "you won't believe", "before it's too late",
                     "last chance", "urgent")
