from __future__ import annotations

import json
import sys

from explainer import analyze_transaction


def main() -> None:
    if len(sys.argv) > 1:
        description = " ".join(sys.argv[1:])
    else:
        description = sys.stdin.read().strip()

    if not description:
        print("Error: no transaction description provided.", file=sys.stderr)
        print("Usage: python main.py <description>", file=sys.stderr)
        print("       echo '<description>' | python main.py", file=sys.stderr)
        sys.exit(1)

    result = analyze_transaction(description)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
