import json
from pathlib import Path

import pytest

from evaluate import evaluate_payload, main


ROOT = Path(__file__).resolve().parents[1]


def test_batch_example_produces_expected_summary():
    payload = json.loads((ROOT / "examples/batch_cases.json").read_text(encoding="utf-8"))
    report = evaluate_payload(payload)

    assert report["summary"] == {
        "total_cases": 2,
        "passed_cases": 1,
        "failed_cases": 1,
        "average_weighted_score": 78.5,
        "minimum_weighted_score": 61.0,
        "maximum_weighted_score": 96.0,
    }


def test_existing_single_case_format_still_works():
    payload = json.loads((ROOT / "examples/sample_case.json").read_text(encoding="utf-8"))
    report = evaluate_payload(payload)

    assert report["weighted_score"] == 88.0
    assert report["passed"] is True


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {},
        {"cases": [], "unexpected": True},
        {"scores": {}, "rationale": {}, "unexpected": True},
    ],
)
def test_rejects_malformed_top_level_payload(payload):
    with pytest.raises(ValueError):
        evaluate_payload(payload)


def test_cli_output_is_sorted_deterministic_json(monkeypatch, capsys):
    example = ROOT / "examples/batch_cases.json"
    monkeypatch.setattr("sys.argv", ["evaluate.py", str(example)])

    assert main() == 0
    first = capsys.readouterr().out
    monkeypatch.setattr("sys.argv", ["evaluate.py", str(example)])
    assert main() == 0
    second = capsys.readouterr().out

    assert first == second
    assert json.loads(first)["summary"]["total_cases"] == 2
