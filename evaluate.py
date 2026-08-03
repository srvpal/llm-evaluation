"""Command-line interface for the LLM evaluation toolkit."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from evaluator import evaluate_scores


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a scored LLM response.")
    parser.add_argument("input_file", type=Path, help="Path to a JSON evaluation file")
    args = parser.parse_args()

    try:
        payload = json.loads(args.input_file.read_text(encoding="utf-8"))
        report = evaluate_scores(payload["scores"], payload["rationale"])
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        parser.error(str(exc))
        return 2

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
