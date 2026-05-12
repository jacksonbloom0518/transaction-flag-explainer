# transaction-explainer

A pure-Python CLI tool that analyzes a transaction description and returns heuristic fraud risk indicators — no ML, no external dependencies, no database.

## Usage

### From the command line

```
python app/main.py "Urgent wire transfer to offshore casino account"
```

### From stdin

```
echo "Coffee at local cafe" | python app/main.py
```

### Output

```json
{
  "risk_level": "high",
  "score": 80,
  "flags": [
    "high_risk_term:casino",
    "high_risk_term:offshore",
    "high_risk_term:urgent",
    "high_risk_term:wire transfer",
    "pattern:urgency_language"
  ]
}
```

Fields:

| Field        | Type         | Description                              |
|--------------|--------------|------------------------------------------|
| `risk_level` | `str`        | `"low"`, `"medium"`, or `"high"`         |
| `score`      | `int`        | 0–100 composite risk score               |
| `flags`      | `list[str]`  | Specific risk indicators that were found |

## Running tests

```
python -m pytest tests/
```

## Project layout

```
transaction-explainer/
├── app/
│   ├── main.py        # CLI entry point
│   └── explainer.py   # core analyze_transaction() function
├── tests/
│   └── test_explainer.py
└── README.md
```

## How scoring works

- Each matched high-risk keyword (e.g. "bitcoin", "casino", "wire transfer") adds **+20** to the score.
- Each matched medium-risk keyword (e.g. "international", "cash", "atm") adds **+10**.
- Each matched suspicious pattern (large amounts, urgency language, card numbers) adds **+15**.
- Score is capped at **100**.
- `low` = score < 25, `medium` = 25–59, `high` = 60+.
