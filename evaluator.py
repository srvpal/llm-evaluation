"""Transparent rubric-based evaluation utilities."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping


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
) -> dict:
    """Validate criterion scores and return a structured weighted report."""
    expected = {criterion.name for criterion in rubric}
    if set(scores) != expected:
        raise ValueError(f"scores must contain exactly: {sorted(expected)}")
    if set(rationale) != expected:
        raise ValueError(f"rationale must contain exactly: {sorted(expected)}")

    weight_total = sum(item.weight for item in rubric)
    if abs(weight_total - 1.0) > 1e-9:
        raise ValueError("rubric weights must sum to 1.0")

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

    return {
        "weighted_score": round(weighted_score, 2),
        "maximum_score": 100,
        "details": details,
    }
