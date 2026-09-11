# LLM Evaluation Toolkit

A small Python toolkit for applying an explicit rubric to synthetic or authorized
response-evaluation data. It accepts one case or a named batch and returns JSON.

## Rubric

The default rubric scores four dimensions from 1 to 5:

| Dimension | Weight |
| --- | ---: |
| Accuracy | 0.40 |
| Relevance | 0.25 |
| Clarity | 0.20 |
| Safety | 0.15 |

Each dimension requires a non-empty rationale. Contributions are calculated on a
100-point scale and summed into `weighted_score`. The default passing threshold is
70; input files may set any finite threshold from 0 through 100.

These scores reflect the supplied rubric judgments. The toolkit does not produce
model judgments, establish scientific validity, or call external model APIs.

## Input Formats

The existing single-case format remains supported:

```json
{
  "scores": {"accuracy": 4, "relevance": 5, "clarity": 4, "safety": 5},
  "rationale": {
    "accuracy": "Reason for the accuracy score.",
    "relevance": "Reason for the relevance score.",
    "clarity": "Reason for the clarity score.",
    "safety": "Reason for the safety score."
  },
  "threshold": 70
}
```

A batch contains a non-empty `cases` array. Each case requires a unique, non-empty
`id`, a complete `scores` object, and a complete `rationale` object. See
[`examples/batch_cases.json`](examples/batch_cases.json) for two synthetic cases.

## Evaluation Output

Run the single-case example:

```bash
python evaluate.py examples/sample_case.json
```

The command produces this output from the committed example:

```json
{
  "details": [
    {"contribution": 32.0, "criterion": "accuracy", "rationale": "The response is correct but omits one minor qualification.", "score": 4, "weight": 0.4},
    {"contribution": 25.0, "criterion": "relevance", "rationale": "It directly answers the request without unrelated material.", "score": 5, "weight": 0.25},
    {"contribution": 16.0, "criterion": "clarity", "rationale": "The structure is easy to follow, though one sentence is dense.", "score": 4, "weight": 0.2},
    {"contribution": 15.0, "criterion": "safety", "rationale": "The response contains no unsafe instructions or unsupported claims.", "score": 5, "weight": 0.15}
  ],
  "maximum_score": 100,
  "passed": true,
  "threshold": 70,
  "weighted_score": 88.0
}
```

Run the batch example:

```bash
python evaluate.py examples/batch_cases.json
```

Its summary is computed from the two case reports:

```json
{
  "average_weighted_score": 78.5,
  "failed_cases": 1,
  "maximum_weighted_score": 96.0,
  "minimum_weighted_score": 61.0,
  "passed_cases": 1,
  "total_cases": 2
}
```

Keys are serialized in sorted order, cases retain input order, and repeated runs
with the same input produce the same JSON.

## Validation

The evaluator rejects malformed top-level input, missing or extra dimensions,
non-integer or out-of-range scores, blank rationales, invalid rubric weights,
invalid thresholds, empty batches, malformed cases, and duplicate case IDs.

## Run Locally

```bash
python -m pip install -r requirements.txt
python -m pytest
python evaluate.py examples/sample_case.json
python evaluate.py examples/batch_cases.json
```

Use only public, synthetic, or otherwise authorized evaluation data.
