import pytest
from evaluator import evaluate_scores


def valid_payload():
    scores = {"accuracy": 4, "relevance": 5, "clarity": 4, "safety": 5}
    rationale = {name: "Clear justification." for name in scores}
    return scores, rationale


def test_weighted_score():
    scores, rationale = valid_payload()
    result = evaluate_scores(scores, rationale)
    assert result["weighted_score"] == 88.0


def test_rejects_out_of_range_score():
    scores, rationale = valid_payload()
    scores["accuracy"] = 6
    with pytest.raises(ValueError):
        evaluate_scores(scores, rationale)
