"""Command-line interface for the LLM evaluation toolkit."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

from evaluator import evaluate_batch, evaluate_scores


def evaluate_payload(payload: Any) -> dict:
    """Validate a single-case or batch payload and return its report."""
    if not isinstance(payload, dict):
        raise ValueError("input must be a JSON object")
    threshold = payload.get("threshold", 70)
    if "cases" in payload:
        allowed = {"cases", "threshold"}
        if set(payload) - allowed:
            raise ValueError(f"batch input fields must be: {sorted(allowed)}")
        return evaluate_batch(payload["cases"], threshold=threshold)

    allowed = {"scores", "rationale", "threshold"}
    if set(payload) - allowed or not {"scores", "rationale"} <= set(payload):
        raise ValueError(f"single-case input fields must be: {sorted(allowed)}")
    return evaluate_scores(payload["scores"], payload["rationale"], threshold=threshold)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a scored LLM response.")
    parser.add_argument("input_file", type=Path, help="Path to a JSON evaluation file")
    args = parser.parse_args()

    try:
        payload = json.loads(args.input_file.read_text(encoding="utf-8"))
        report = evaluate_payload(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
        return 2

    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
