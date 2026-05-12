from __future__ import annotations

import re


_HIGH_RISK_TERMS = frozenset({
    "casino", "gambling", "bet", "lottery", "crypto", "bitcoin", "wire transfer",
    "western union", "moneygram", "gift card", "prepaid card", "offshore",
    "anonymous", "untraceable", "urgent", "immediate transfer", "advance fee",
    "inheritance", "prize", "won", "winner", "claim",
})

_MEDIUM_RISK_TERMS = frozenset({
    "foreign", "international", "overseas", "unknown", "unverified",
    "atm", "cash", "withdrawal", "refund", "dispute", "chargeback",
    "duplicate", "multiple", "unusual", "large amount",
})

_SUSPICIOUS_PATTERNS: list[tuple[str, str]] = [
    (r"\b\d{1,3}(?:,\d{3})+\b|\b\d{5,}\b", "large_numeric_amount"),
    (r"\b(?:asap|immediately|right now|today only|limited time)\b", "urgency_language"),
    (r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "email_in_description"),
    (r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b", "card_number_pattern"),
]


def analyze_transaction(description: str) -> dict:
    """Analyze a transaction description and return fraud risk indicators.

    Args:
        description: Free-text description of the transaction.

    Returns:
        A dict with keys:
            risk_level (str): "low", "medium", or "high"
            score (int): 0–100 risk score
            flags (list[str]): specific risk indicators detected
    """
    if not isinstance(description, str):
        raise TypeError(f"description must be str, got {type(description).__name__}")

    lowered = description.lower()
    flags: list[str] = []
    score = 0

    high_hits = [term for term in _HIGH_RISK_TERMS if term in lowered]
    for term in high_hits:
        flags.append(f"high_risk_term:{term}")
        score += 20

    medium_hits = [term for term in _MEDIUM_RISK_TERMS if term in lowered]
    for term in medium_hits:
        flags.append(f"medium_risk_term:{term}")
        score += 10

    for pattern, label in _SUSPICIOUS_PATTERNS:
        if re.search(pattern, description, re.IGNORECASE):
            flags.append(f"pattern:{label}")
            score += 15

    score = min(score, 100)

    if score >= 60:
        risk_level = "high"
    elif score >= 25:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "risk_level": risk_level,
        "score": score,
        "flags": sorted(set(flags)),
    }
