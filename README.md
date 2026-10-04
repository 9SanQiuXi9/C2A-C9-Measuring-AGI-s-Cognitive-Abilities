# MetaBoundary — Metacognitive Knowledge Boundary Benchmark

**Challenge:** C2A / C9 — Measuring AGI's Cognitive Abilities  
**Track:** Track 2 — Metacognition  
**Author:** 三秋羲  
**Course:** AI+X Elite 20 Program, SIAS University  
**Reference:** [DeepMind (2026) — Measuring Progress Toward AGI: A Cognitive Framework](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/measuring-progress-toward-agi/measuring-progress-toward-agi-a-cognitive-framework.pdf)

---

## Overview

MetaBoundary measures whether AI models know the boundary of their own knowledge. It presents 88 factual questions across 5 categories and evaluates how well a model's confidence tracks its actual correctness — the core of metacognitive calibration.

**Key property:** Two models with identical accuracy can score very differently. A model that is right 83% of the time and *knows* when it's wrong outperforms one that is right 83% but can't tell correct answers from mistakes.

---

## Repository Structure

```
C2A C9/
├── README.md                          # This file
│
├── # Phase 1: C2A Proposal
├── 三秋羲_C2A_proposal.md             # Track selection + benchmark design proposal
├── 三秋羲_C2A_AI日志.md               # AI usage log (proposal phase)
├── 三秋羲_C2A_拿来说明.md             # Reference sources and attribution
│
├── # Phase 2: C9 Implementation
├── 三秋羲_C9_task说明.md              # Task description + scoring criteria
├── 三秋羲_C9_测试结果.md              # Test results (32/32 pass, 5 model profiles)
├── 三秋羲_C9_反思报告.md              # Reflection report
├── 三秋羲_C9_AI日志.md                # AI usage log (implementation phase)
├── 三秋羲_C9_拿来说明.md              # Reference sources and attribution
│
└── 三秋羲_C9_benchmark/               # Runnable benchmark code
    ├── README.md                      # Code documentation
    ├── runner.py                      # CLI entry point
    ├── generator.py                   # 88 questions, 5 categories
    ├── scoring.py                     # Brier, ECE, AUROC, MetaScore
    ├── evaluator.py                   # Evaluation pipeline
    ├── models.py                      # 5 mock model profiles
    ├── requirements.txt               # Dependencies (none)
    ├── data/                          # Generated results
    └── tests/                         # Test suite (32 tests)
```

---

## Quick Start

```bash
cd 三秋羲_C9_benchmark

# Run all 5 model profiles
python runner.py

# Run a specific profile
python runner.py --model well_calibrated

# Export question dataset
python runner.py --export-data

# Run internal tests
python runner.py --test
```

**Requirements:** Python 3.8+, zero external dependencies  
**Runtime:** ~1 second (fixed seed=42)

---

## Metrics

| Metric | Range | Meaning |
|--------|-------|---------|
| **Brier Score** | 0–1 | Confidence–correctness mean squared error (lower = better) |
| **ECE** | 0–1 | Bin-based calibration gap (lower = better) |
| **AUROC** | 0–1 | Confidence discrimination ability (higher = better) |
| **MetaScore** | 0–1 | Composite: 0.4×(1−Brier) + 0.3×(1−ECE) + 0.3×AUROC |
| **Selective Coverage** | — | Accuracy at varying confidence thresholds |

---

## Model Comparison Results

| Model | Accuracy | Brier | ECE | AUROC | MetaScore |
|-------|----------|-------|-----|-------|-----------|
| Perfect | 1.0000 | 0.0001 | 0.0100 | N/A | 0.9970 |
| WellCalibrated | 0.8295 | 0.1579 | 0.1241 | 0.6785 | 0.8032 |
| Overconfident | 0.6250 | 0.2294 | 0.1855 | 0.6727 | 0.7544 |
| Underconfident | 0.8295 | 0.2592 | 0.3283 | 0.6452 | 0.6914 |
| Random | 0.4886 | 0.4079 | 0.3812 | 0.3845 | 0.5378 |

**Key finding:** WellCalibrated and Underconfident have identical accuracy (0.8295) but MetaScore differs by 0.11 — MetaBoundary captures calibration differences that accuracy alone misses.

---

## Design Alignment with DeepMind Framework

The DeepMind (2026) cognitive framework defines metacognition as a three-level taxonomy (§7.7):

| Level | Definition | MetaBoundary Metric |
|-------|-----------|-------------------|
| First-order | Task performance | Accuracy |
| Second-order | Confidence about performance | Brier Score, ECE, AUROC |
| Third-order | Strategic use of metacognition | Selective Coverage |

---

## Limitations

- **Simulated models:** All results use mock model runners; real LLM evaluation requires API access
- **English-only:** Questions are in English only
- **88 questions:** Sufficient for pipeline demonstration; production benchmark would need 500+
- **Static questions:** Hand-curated rather than procedurally generated

---

## License

Educational use. Created for the AI+X Elite 20 Program, SIAS University.
