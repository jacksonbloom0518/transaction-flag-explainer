from ibm_watsonx_orchestrate.agent_builder.tools import tool


@tool
def score_fraud_risk(
    transaction_amount: float,
    merchant_category: str,
    hour_of_day: int,
    distance_from_home_km: float,
    is_online: bool,
) -> dict:
    """Score the fraud risk of a payment transaction and return a risk score, level, and explanation."""
    if transaction_amount < 0:
        raise ValueError(f"transaction_amount must be >= 0, got {transaction_amount}")
    if not 0 <= hour_of_day <= 23:
        raise ValueError(f"hour_of_day must be in [0, 23], got {hour_of_day}")
    if distance_from_home_km < 0:
        raise ValueError(f"distance_from_home_km must be >= 0, got {distance_from_home_km}")
    if not merchant_category or not merchant_category.strip():
        raise ValueError("merchant_category must be a non-empty string")

    score: float = 0.0
    factors: list[str] = []

    # Amount-based risk
    if transaction_amount >= 1000.0:
        score += 0.30
        factors.append(f"high transaction amount (${transaction_amount:.2f})")
    elif transaction_amount >= 300.0:
        score += 0.15
        factors.append(f"moderate transaction amount (${transaction_amount:.2f})")

    # Hour-based risk (unusual hours: 23:00–05:00)
    unusual_hours = set(range(0, 6)) | {23}
    if hour_of_day in unusual_hours:
        score += 0.20
        factors.append(f"transaction at unusual hour ({hour_of_day:02d}:00)")

    # Distance-based risk
    if distance_from_home_km >= 200.0:
        score += 0.25
        factors.append(f"very far from home ({distance_from_home_km:.1f} km)")
    elif distance_from_home_km >= 50.0:
        score += 0.10
        factors.append(f"moderately far from home ({distance_from_home_km:.1f} km)")

    # Online transaction risk
    if is_online:
        score += 0.15
        factors.append("online (card-not-present) transaction")

    # High-risk merchant categories
    high_risk_categories = {"gambling", "crypto", "wire_transfer", "pawn", "jewelry"}
    medium_risk_categories = {"electronics", "travel", "hotel", "car_rental"}
    category_lower = merchant_category.strip().lower()
    if category_lower in high_risk_categories:
        score += 0.20
        factors.append(f"high-risk merchant category ({merchant_category})")
    elif category_lower in medium_risk_categories:
        score += 0.08
        factors.append(f"elevated-risk merchant category ({merchant_category})")
    else:
        factors.append(f"unrecognized merchant category ({merchant_category}); treated as standard risk")

    # Compound penalty: online + unusual hour + far from home
    if is_online and hour_of_day in unusual_hours and distance_from_home_km >= 50.0:
        score += 0.10
        factors.append("compound risk: online purchase at unusual hour far from home")

    score = min(score, 1.0)

    if score >= 0.65:
        risk_level = "high"
    elif score >= 0.30:
        risk_level = "medium"
    else:
        risk_level = "low"

    if factors:
        explanation = "Risk factors identified: " + "; ".join(factors) + "."
    else:
        explanation = "No significant risk factors detected; transaction appears normal."

    return {
        "risk_score": round(score, 4),
        "risk_level": risk_level,
        "explanation": explanation,
    }


if __name__ == "__main__":
    test_cases = [
        {
            "transaction_amount": 1500.00,
            "merchant_category": "gambling",
            "hour_of_day": 3,
            "distance_from_home_km": 350.0,
            "is_online": True,
        },
        {
            "transaction_amount": 45.00,
            "merchant_category": "grocery",
            "hour_of_day": 14,
            "distance_from_home_km": 2.5,
            "is_online": False,
        },
        {
            "transaction_amount": 320.00,
            "merchant_category": "electronics",
            "hour_of_day": 23,
            "distance_from_home_km": 80.0,
            "is_online": True,
        },
    ]

    for i, params in enumerate(test_cases, start=1):
        result = score_fraud_risk(**params)
        print(f"Test {i}: {result}")
