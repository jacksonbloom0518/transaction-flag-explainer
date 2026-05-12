from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import pytest
from explainer import analyze_transaction


def test_low_risk_returns_expected_shape():
    result = analyze_transaction("Coffee at local cafe, $4.50")
    assert isinstance(result, dict)
    assert set(result.keys()) == {"risk_level", "score", "flags"}
    assert isinstance(result["score"], int)
    assert isinstance(result["flags"], list)


def test_low_risk_case():
    result = analyze_transaction("Grocery store purchase at Walmart, $52.10")
    assert result["risk_level"] == "low"
    assert result["score"] < 25
    assert result["flags"] == []


def test_high_risk_multiple_terms():
    result = analyze_transaction(
        "Urgent wire transfer to offshore casino account, buy bitcoin gift card immediately"
    )
    assert result["risk_level"] == "high"
    assert result["score"] >= 60
    assert len(result["flags"]) > 0


def test_high_risk_single_strong_term():
    result = analyze_transaction("Send advance fee to claim inheritance prize")
    assert result["risk_level"] == "high"


def test_medium_risk_case():
    result = analyze_transaction("International ATM cash withdrawal")
    assert result["risk_level"] in {"medium", "high"}
    assert result["score"] >= 25


def test_pattern_large_amount():
    result = analyze_transaction("Transfer of 50000 dollars to unknown account")
    assert any("large_numeric_amount" in f for f in result["flags"])


def test_pattern_urgency_language():
    result = analyze_transaction("Please send payment ASAP")
    assert any("urgency_language" in f for f in result["flags"])


def test_pattern_card_number():
    result = analyze_transaction("Transaction on card 4111 1111 1111 1111")
    assert any("card_number_pattern" in f for f in result["flags"])


def test_score_capped_at_100():
    very_risky = (
        "urgent immediate wire transfer bitcoin casino offshore anonymous "
        "gift card western union advance fee inheritance prize lottery"
    )
    result = analyze_transaction(very_risky)
    assert result["score"] <= 100


def test_flags_are_deduplicated():
    result = analyze_transaction("bitcoin bitcoin bitcoin")
    bitcoin_flags = [f for f in result["flags"] if "bitcoin" in f]
    assert len(bitcoin_flags) == 1


def test_empty_string_is_low_risk():
    result = analyze_transaction("")
    assert result["risk_level"] == "low"
    assert result["score"] == 0
    assert result["flags"] == []


def test_invalid_type_raises():
    with pytest.raises(TypeError):
        analyze_transaction(12345)  # type: ignore[arg-type]
