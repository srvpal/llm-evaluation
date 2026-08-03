# LLM Evaluation Toolkit

A small, transparent toolkit for evaluating model responses with explicit criteria.

## What it demonstrates

- Rubric-based scoring
- Weighted dimensions
- Input validation
- Structured JSON reports
- Human-readable evaluation rationales
- Reproducible tests

This project does not claim to replace expert human judgment. It provides a consistent baseline that can support review workflows.

## Quick start

```bash
python -m pip install -r requirements.txt
python evaluate.py examples/sample_case.json
pytest
```

## Default dimensions

- Accuracy
- Relevance
- Clarity
- Safety

Each criterion receives a score from 1 to 5. The evaluator calculates a weighted score out of 100.

## Example input

See `examples/sample_case.json`.

## Privacy and confidentiality

Use only public, synthetic, or properly authorized evaluation data. Never commit confidential conversations or employer datasets.
