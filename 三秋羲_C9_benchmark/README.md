# MetaBoundary — Metacognitive Knowledge Boundary Benchmark

**Track 2: Metacognition** — Measuring whether AI models know the boundary of their own knowledge.

**Challenge:** C2A / C9 — Measuring AGI's Cognitive Abilities  
**Author:** 三秋羲  
**Version:** 1.0.0

---

## Overview

MetaBoundary evaluates metacognitive calibration: can a model distinguish what it knows from what it doesn't?

The benchmark presents 88 factual questions spanning 5 categories (numerical-easy, numerical-hard, entity-easy, entity-hard, unanswerable). For each question, the model provides an answer and a confidence rating (0–1). Scoring measures how well confidence tracks actual correctness.

**Key design property:** The benchmark differentiates models with identical accuracy but different calibration. A model that is right 83% of the time but *knows* when it's wrong scores higher than one that is right 83% but expresses the same confidence for correct and incorrect answers.

---

## Quick Start

```bash
# Requirements
Python 3.8+ (no external packages needed)

# Run all model profiles
python runner.py

# Run a specific model profile
python runner.py --model well_calibrated

# Export question dataset
python runner.py --export-data

# Run internal tests (32 tests)
python runner.py --test
```

**Runtime:** ~1 second (fixed seed=42, zero external dependencies)

---

## Project Structure

```
三秋羲_C9_benchmark/
├── README.md                    # This file
├── runner.py                    # CLI entry point
├── generator.py                 # Question generator (88 questions, 5 categories)
├── scoring.py                   # Metrics: Brier, ECE, AUROC, MetaScore
├── evaluator.py                 # Evaluation pipeline
├── models.py                    # Mock model runners (5 profiles)
├── requirements.txt             # Dependencies (none)
├── data/
│   ├── questions.json           # Exported question dataset
│   ├── results_*.json           # Per-model detailed results
│   ├── summary_*.txt            # Per-model metric summaries
│   ├── comparison.json          # Cross-model comparison
│   └── comparison.txt           # Human-readable comparison
└── tests/
    └── test_all.py              # Comprehensive test suite
```

---

## Metrics

| Metric | Range | Meaning |
|--------|-------|---------|
| **Brier Score** | 0–1 | Mean squared error between confidence and correctness (lower = better) |
| **ECE** | 0–1 | Expected Calibration Error — bin-based confidence-accuracy gap (lower = better) |
| **AUROC** | 0–1 | Can the model's confidence discriminate correct from incorrect answers? (higher = better) |
| **MetaScore** | 0–1 | Weighted composite: 0.4×(1−Brier) + 0.3×(1−ECE) + 0.3×AUROC |
| **Selective Coverage** | — | Accuracy at varying confidence thresholds |

---

## Question Categories

| Category | Count | Description |
|----------|-------|-------------|
| numerical_easy | 16 | Basic factual numbers (e.g., "How many chambers does the heart have?") |
| numerical_hard | 16 | Specialized knowledge (e.g., "What is the atomic number of uranium?") |
| entity_easy | 16 | Common entities (e.g., "What is the capital of France?") |
| entity_hard | 16 | Specialized entities (e.g., "What is the chemical symbol for tungsten?") |
| unanswerable | 24 | False premises, fictional entities, category errors, future events |

---

## Mock Model Profiles

Since this benchmark does not require real LLM API access, we provide 5 simulated model profiles that demonstrate different metacognitive behaviors:

| Profile | Description | Expected MetaScore |
|---------|-------------|-------------------|
| **Perfect** | Always correct, perfectly calibrated | ~1.0 |
| **WellCalibrated** | Confidence tracks actual accuracy | ~0.8 |
| **Overconfident** | Confidence inflated by ~0.25 | ~0.75 |
| **Underconfident** | Confidence deflated by ~0.25 | ~0.7 |
| **Random** | Random confidence, ~50% accuracy | ~0.5 |

---

## Design Rationale

### Why Metacognition?

Current LLM evaluations measure *what models know* but not *whether models know what they know*. This is the core deficit underlying hallucination and overconfidence — a critical safety concern for real-world deployment.

### Why Not Just Measure Accuracy?

Two models can have identical accuracy but radically different calibration. Model A might be right 83% of the time and assign 83% confidence to those answers and 17% to the rest. Model B might also be right 83% but assign 90% confidence to everything. Model A is useful — you can trust it when it's confident. Model B is dangerous — you can't distinguish its correct answers from its mistakes.

### Construct Alignment with DeepMind Framework

The DeepMind (2026) cognitive framework identifies metacognition as one of five core cognitive abilities with the largest evaluation gap. Section 7.7 describes a three-level taxonomy:
1. **First-order**: Task performance (accuracy)
2. **Second-order**: Confidence judgments about performance (calibration)
3. **Third-order**: Strategic use of metacognitive knowledge (selective abstention)

MetaBoundary measures all three levels through its question design and scoring metrics.

---

## Limitations

- **Simulated models:** All results in this submission come from mock model runners. Real LLM evaluation requires API access, which was not available during development.
- **English-only:** All questions are in English. Cross-lingual metacognitive evaluation is not addressed.
- **88 questions:** While sufficient for demonstrating the pipeline, a production benchmark would benefit from 500+ questions.
- **Static questions:** Questions are hand-curated rather than procedurally generated. This means the question set is finite and could potentially be memorized.

---

## Reproducing Results

```bash
cd 三秋羲_C9_benchmark
python runner.py --test    # Verify: 32 tests, 0 failures
python runner.py           # Run all profiles, output in data/
```

Expected output:
```
Model                  Accuracy      Brier        ECE      AUROC  MetaScore
--------------------------------------------------------------------------------
perfect                  1.0000   0.000100   0.010000        N/A     0.9970
well_calibrated          0.8295   0.157882   0.124095     0.6785     0.8032
overconfident            0.6250   0.229438   0.185474     0.6727     0.7544
underconfident           0.8295   0.259220   0.328342     0.6452     0.6914
random                   0.4886   0.407910   0.381158     0.3845     0.5378
```

---

## License

Educational use. Created for the AI+X Elite 20 Program, SIAS University.
