import math

import pytest
from evaluator import Criterion, evaluate_batch, evaluate_scores


def valid_payload():
    scores = {"accuracy": 4, "relevance": 5, "clarity": 4, "safety": 5}
    rationale = {name: "Clear justification." for name in scores}
    return scores, rationale


def test_weighted_score():
    scores, rationale = valid_payload()
    result = evaluate_scores(scores, rationale)
    assert result["weighted_score"] == 88.0
    assert result["threshold"] == 70
    assert result["passed"] is True
    assert [detail["criterion"] for detail in result["details"]] == [
        "accuracy",
        "relevance",
        "clarity",
        "safety",
    ]


def test_rejects_out_of_range_score():
    scores, rationale = valid_payload()
    scores["accuracy"] = 6
    with pytest.raises(ValueError):
        evaluate_scores(scores, rationale)


@pytest.mark.parametrize("score", [True, 0, 6, 3.5, "4", None])
def test_rejects_invalid_dimension_scores(score):
    scores, rationale = valid_payload()
    scores["accuracy"] = score
    with pytest.raises(ValueError):
        evaluate_scores(scores, rationale)


def test_rejects_missing_extra_and_malformed_dimensions():
    scores, rationale = valid_payload()
    del scores["accuracy"]
    with pytest.raises(ValueError):
        evaluate_scores(scores, rationale)

    scores, rationale = valid_payload()
    rationale["extra"] = "Not in the rubric."
    with pytest.raises(ValueError):
        evaluate_scores(scores, rationale)

    with pytest.raises(ValueError):
        evaluate_scores([], rationale)


@pytest.mark.parametrize("explanation", ["", "   ", None, 4])
def test_rejects_invalid_rationale(explanation):
    scores, rationale = valid_payload()
    rationale["accuracy"] = explanation
    with pytest.raises(ValueError):
        evaluate_scores(scores, rationale)


@pytest.mark.parametrize("threshold", [-1, 101, True, "70", math.inf, math.nan])
def test_rejects_invalid_threshold(threshold):
    scores, rationale = valid_payload()
    with pytest.raises(ValueError):
        evaluate_scores(scores, rationale, threshold=threshold)


def test_configurable_threshold_controls_pass_status():
    scores, rationale = valid_payload()
    assert evaluate_scores(scores, rationale, threshold=88)["passed"] is True
    assert evaluate_scores(scores, rationale, threshold=88.01)["passed"] is False


def test_batch_results_and_summary_statistics():
    high_scores, high_rationale = valid_payload()
    low_scores = {name: 1 for name in high_scores}
    low_rationale = {name: "Synthetic low-scoring case." for name in low_scores}

    report = evaluate_batch(
        [
            {"id": "high", "scores": high_scores, "rationale": high_rationale},
            {"id": "low", "scores": low_scores, "rationale": low_rationale},
        ],
        threshold=75,
    )

    assert [case["case_id"] for case in report["case_results"]] == ["high", "low"]
    assert report["summary"] == {
        "total_cases": 2,
        "passed_cases": 1,
        "failed_cases": 1,
        "average_weighted_score": 54.0,
        "minimum_weighted_score": 20.0,
        "maximum_weighted_score": 88.0,
    }


@pytest.mark.parametrize("cases", [None, [], {}, "cases"])
def test_rejects_invalid_batch_container(cases):
    with pytest.raises(ValueError):
        evaluate_batch(cases)


def test_rejects_malformed_or_duplicate_cases():
    scores, rationale = valid_payload()
    valid = {"id": "case", "scores": scores, "rationale": rationale}
    with pytest.raises(ValueError):
        evaluate_batch([{"id": "missing-fields"}])
    with pytest.raises(ValueError):
        evaluate_batch([valid, valid])


@pytest.mark.parametrize(
    "rubric",
    [
        (),
        ("accuracy",),
        (Criterion("same", 0.5), Criterion("same", 0.5)),
        (Criterion("accuracy", 0.8),),
        (Criterion("accuracy", float("inf")),),
    ],
)
def test_rejects_invalid_rubrics(rubric):
    scores, rationale = valid_payload()
    with pytest.raises(ValueError):
        evaluate_scores(scores, rationale, rubric=rubric)
