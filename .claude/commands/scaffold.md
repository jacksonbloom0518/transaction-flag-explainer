Use the python-pro agent to scaffold a new Transaction Flag Explainer project with the following structure:

transaction-explainer/
├── app/
│   ├── main.py        ← CLI entry point, accepts transaction description as input
│   └── explainer.py   ← core logic, returns fraud risk indicators
├── tests/
│   └── test_explainer.py  ← basic unit tests
└── README.md

$ARGUMENTS

Keep it simple. No database, no frontend, no auth. Pure Python functions only.