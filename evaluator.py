"""Transparent rubric-based evaluation utilities."""

from __future__ import annotations
from collections.abc import Mapping
from dataclasses import dataclass
import math
from typing import Any


@dataclass(frozen=True)
class Criterion:
    name: str
    weight: float


DEFAULT_RUBRIC = (
    Criterion("accuracy", 0.40),
    Criterion("relevance", 0.25),
    Criterion("clarity", 0.20),
    Criterion("safety", 0.15),
)


def evaluate_scores(
    scores: Mapping[str, int],
    rationale: Mapping[str, str],
    rubric: tuple[Criterion, ...] = DEFAULT_RUBRIC,
    threshold: float = 70,
) -> dict:
    """Validate criterion scores and return a structured weighted report."""
    _validate_rubric(rubric)
    threshold = _validate_threshold(threshold)
    if not isinstance(scores, Mapping) or not isinstance(rationale, Mapping):
        raise ValueError("scores and rationale must be objects")
    expected = {criterion.name for criterion in rubric}
    if set(scores) != expected:
        raise ValueError(f"scores must contain exactly: {sorted(expected)}")
    if set(rationale) != expected:
        raise ValueError(f"rationale must contain exactly: {sorted(expected)}")

    details = []
    weighted_score = 0.0

    for criterion in rubric:
        score = scores[criterion.name]
        explanation = rationale[criterion.name]

        if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
            raise ValueError(f"{criterion.name} must be an integer from 1 to 5")
        if not isinstance(explanation, str) or not explanation.strip():
            raise ValueError(f"{criterion.name} requires a rationale")

        contribution = (score / 5) * criterion.weight * 100
        weighted_score += contribution
        details.append(
            {
                "criterion": criterion.name,
                "score": score,
                "weight": criterion.weight,
                "contribution": round(contribution, 2),
                "rationale": explanation.strip(),
            }
        )

    weighted_score = round(weighted_score, 2)
    return {
        "weighted_score": weighted_score,
        "maximum_score": 100,
        "threshold": threshold,
        "passed": weighted_score >= threshold,
        "details": details,
    }


def evaluate_batch(
    cases: list[Mapping[str, Any]],
    threshold: float = 70,
    rubric: tuple[Criterion, ...] = DEFAULT_RUBRIC,
) -> dict:
    """Evaluate named cases and return their reports with summary statistics."""
    threshold = _validate_threshold(threshold)
    _validate_rubric(rubric)
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty array")

    results = []
    seen_ids = set()
    required = {"id", "scores", "rationale"}
    for index, case in enumerate(cases):
        if not isinstance(case, Mapping) or set(case) != required:
            raise ValueError(f"case {index} must contain exactly: {sorted(required)}")
        case_id = case["id"]
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"case {index} requires a non-empty string id")
        case_id = case_id.strip()
        if case_id in seen_ids:
            raise ValueError(f"duplicate case id: {case_id}")
        seen_ids.add(case_id)
        result = evaluate_scores(case["scores"], case["rationale"], rubric, threshold)
        results.append({"case_id": case_id, **result})

    scores = [result["weighted_score"] for result in results]
    passed = sum(result["passed"] for result in results)
    return {
        "threshold": threshold,
        "case_results": results,
        "summary": {
            "total_cases": len(results),
            "passed_cases": passed,
            "failed_cases": len(results) - passed,
            "average_weighted_score": round(sum(scores) / len(scores), 2),
            "minimum_weighted_score": min(scores),
            "maximum_weighted_score": max(scores),
        },
    }


def _validate_threshold(threshold: float) -> float:
    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not math.isfinite(threshold)
        or not 0 <= threshold <= 100
    ):
        raise ValueError("threshold must be a finite number from 0 to 100")
    return threshold


def _validate_rubric(rubric: tuple[Criterion, ...]) -> None:
    if not isinstance(rubric, tuple) or not rubric:
        raise ValueError("rubric must be a non-empty tuple")
    if any(not isinstance(criterion, Criterion) for criterion in rubric):
        raise ValueError("rubric entries must be Criterion objects")
    names = [criterion.name for criterion in rubric]
    if any(not isinstance(name, str) or not name.strip() for name in names):
        raise ValueError("criterion names must be non-empty strings")
    if len(names) != len(set(names)):
        raise ValueError("criterion names must be unique")
    if any(
        isinstance(criterion.weight, bool)
        or not isinstance(criterion.weight, (int, float))
        or not math.isfinite(criterion.weight)
        or criterion.weight <= 0
        for criterion in rubric
    ):
        raise ValueError("criterion weights must be positive finite numbers")
    if abs(sum(item.weight for item in rubric) - 1.0) > 1e-9:
        raise ValueError("rubric weights must sum to 1.0")
