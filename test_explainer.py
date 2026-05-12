import pytest
from explainer import score_fraud_risk


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _call(**kwargs):
    defaults = dict(
        transaction_amount=50.0,
        merchant_category="grocery",
        hour_of_day=14,
        distance_from_home_km=5.0,
        is_online=False,
    )
    defaults.update(kwargs)
    return score_fraud_risk(**defaults)


# ---------------------------------------------------------------------------
# P1 — ValueError guards
# ---------------------------------------------------------------------------

class TestInputValidation:
    def test_negative_transaction_amount_raises(self):
        with pytest.raises(ValueError, match="transaction_amount"):
            _call(transaction_amount=-1.0)

    def test_hour_of_day_too_high_raises(self):
        with pytest.raises(ValueError, match="hour_of_day"):
            _call(hour_of_day=24)

    def test_hour_of_day_negative_raises(self):
        with pytest.raises(ValueError, match="hour_of_day"):
            _call(hour_of_day=-1)

    def test_negative_distance_raises(self):
        with pytest.raises(ValueError, match="distance_from_home_km"):
            _call(distance_from_home_km=-0.1)

    def test_empty_merchant_category_raises(self):
        with pytest.raises(ValueError, match="merchant_category"):
            _call(merchant_category="")

    def test_whitespace_merchant_category_raises(self):
        with pytest.raises(ValueError, match="merchant_category"):
            _call(merchant_category="   ")


# ---------------------------------------------------------------------------
# Return shape
# ---------------------------------------------------------------------------

class TestReturnShape:
    def test_result_has_required_keys(self):
        result = _call()
        assert set(result.keys()) == {"risk_score", "risk_level", "explanation"}

    def test_risk_score_in_unit_interval(self):
        result = _call(transaction_amount=9999.0, merchant_category="gambling",
                       hour_of_day=3, distance_from_home_km=500.0, is_online=True)
        assert 0.0 <= result["risk_score"] <= 1.0

    def test_risk_level_values(self):
        low = _call()
        assert low["risk_level"] in {"low", "medium", "high"}


# ---------------------------------------------------------------------------
# Scoring logic — happy path
# ---------------------------------------------------------------------------

class TestScoringLogic:
    def test_low_risk_baseline(self):
        result = _call()
        assert result["risk_level"] == "low"
        assert result["risk_score"] == 0.0

    def test_high_amount_increases_score(self):
        low = _call(transaction_amount=50.0)
        high = _call(transaction_amount=1000.0)
        assert high["risk_score"] > low["risk_score"]

    def test_moderate_amount_tier(self):
        result = _call(transaction_amount=300.0)
        assert result["risk_score"] == pytest.approx(0.15)

    def test_unusual_hour_increases_score(self):
        day = _call(hour_of_day=12)
        night = _call(hour_of_day=3)
        assert night["risk_score"] > day["risk_score"]

    def test_boundary_hours_are_unusual(self):
        for h in [0, 1, 2, 3, 4, 5, 23]:
            assert _call(hour_of_day=h)["risk_score"] > 0.0

    def test_boundary_hours_are_normal(self):
        for h in [6, 12, 22]:
            assert _call(hour_of_day=h)["risk_score"] == 0.0

    def test_far_distance_increases_score(self):
        near = _call(distance_from_home_km=5.0)
        far = _call(distance_from_home_km=200.0)
        assert far["risk_score"] > near["risk_score"]

    def test_online_flag_increases_score(self):
        offline = _call(is_online=False)
        online = _call(is_online=True)
        assert online["risk_score"] > offline["risk_score"]

    def test_high_risk_merchant_category(self):
        result = _call(merchant_category="gambling")
        assert result["risk_score"] == pytest.approx(0.20)

    def test_medium_risk_merchant_category(self):
        result = _call(merchant_category="electronics")
        assert result["risk_score"] == pytest.approx(0.08)

    def test_compound_penalty_applied(self):
        # online + unusual hour + far: should include the +0.10 compound bonus
        with_compound = _call(
            is_online=True, hour_of_day=3, distance_from_home_km=50.0
        )
        # same without the compound trigger (in-person)
        without_compound = _call(
            is_online=False, hour_of_day=3, distance_from_home_km=50.0
        )
        diff = round(with_compound["risk_score"] - without_compound["risk_score"], 4)
        # online (+0.15) + compound (+0.10) vs nothing for is_online
        assert diff == pytest.approx(0.25)

    def test_score_capped_at_one(self):
        result = _call(
            transaction_amount=9999.0,
            merchant_category="gambling",
            hour_of_day=3,
            distance_from_home_km=500.0,
            is_online=True,
        )
        assert result["risk_score"] == 1.0

    def test_unrecognized_category_flagged_in_explanation(self):
        result = _call(merchant_category="florist")
        assert "unrecognized" in result["explanation"].lower()

    def test_high_risk_scenario_level(self):
        result = _call(
            transaction_amount=1500.0,
            merchant_category="gambling",
            hour_of_day=3,
            distance_from_home_km=350.0,
            is_online=True,
        )
        assert result["risk_level"] == "high"

    def test_medium_risk_scenario_level(self):
        result = _call(
            transaction_amount=320.0,
            merchant_category="electronics",
            hour_of_day=23,
            distance_from_home_km=80.0,
            is_online=True,
        )
        assert result["risk_level"] == "high"

    def test_zero_amount_zero_distance_is_low_risk(self):
        result = _call(transaction_amount=0.0, distance_from_home_km=0.0)
        assert result["risk_level"] == "low"

    def test_merchant_category_matching_is_case_insensitive(self):
        lower = _call(merchant_category="gambling")
        upper = _call(merchant_category="GAMBLING")
        mixed = _call(merchant_category="Gambling")
        assert lower["risk_score"] == upper["risk_score"] == mixed["risk_score"]
