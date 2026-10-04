#!/usr/bin/env python3
"""
MetaBoundary — Metacognitive Knowledge Boundary Benchmark
CLI entry point.

Usage:
  python runner.py                          Run all model profiles
  python runner.py --model well_calibrated  Run a specific model profile
  python runner.py --export-data            Export question dataset to data/
  python runner.py --test                   Run internal tests
"""

import argparse
import json
import os
import sys

from generator import generate_dataset, generate_questions, check_answer
from scoring import brier_score, expected_calibration_error, auroc, compute_all_metrics, format_metrics
from evaluator import evaluate, evaluate_all
from models import ALL_RUNNERS


def run_single(model_name, seed=42, output_dir="data"):
    print(f"\nRunning MetaBoundary with model profile: {model_name}")
    print("-" * 50)
    result = evaluate(model_name, seed=seed, output_dir=output_dir)
    print(format_metrics(result["metrics"]))
    print(f"\nResults saved to {output_dir}/")
    return result


def run_all_models(seed=42, output_dir="data"):
    print("\nRunning MetaBoundary — All Model Profiles")
    print("=" * 60)
    all_results, comparison = evaluate_all(seed=seed, output_dir=output_dir)
    print(f"\nAll results saved to {output_dir}/")
    return all_results, comparison


def export_data(seed=42, output_dir="data"):
    path = os.path.join(output_dir, "questions.json")
    dataset = generate_dataset(output_path=path, seed=seed)
    print(f"Exported {dataset['num_questions']} questions to {path}")
    print(f"Categories: {json.dumps(dataset['categories'], indent=2)}")
    return dataset


def run_tests():
    print("Running internal tests...\n")
    passed = 0
    failed = 0

    def assert_eq(actual, expected, msg=""):
        nonlocal passed, failed
        if actual == expected:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {msg} — expected {expected}, got {actual}")

    def assert_close(actual, expected, tol=0.01, msg=""):
        nonlocal passed, failed
        if abs(actual - expected) < tol:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {msg} — expected ~{expected}, got {actual}")

    print("[generator]")
    questions = generate_questions(seed=42)
    assert_eq(len(questions) > 50, True, "should have >50 questions")

    n_unanswerable = sum(1 for q in questions if q["answer"] == "UNANSWERABLE")
    assert_eq(n_unanswerable > 10, True, "should have >10 unanswerable questions")

    ids = [q["id"] for q in questions]
    assert_eq(len(ids), len(set(ids)), "IDs should be unique")

    assert_eq(check_answer("Paris", "Paris"), True, "exact match")
    assert_eq(check_answer("paris", "Paris"), True, "case insensitive")
    assert_eq(check_answer("UNANSWERABLE", "UNANSWERABLE"), True, "unanswerable detection")
    assert_eq(check_answer("cannot answer", "UNANSWERABLE"), True, "unanswerable marker")
    assert_eq(check_answer("London", "Paris"), False, "wrong answer")

    dataset = generate_dataset(seed=42)
    assert_eq(dataset["num_questions"], len(questions), "dataset count matches")

    print("[scoring]")
    assert_close(brier_score([1.0, 0.0], [1, 0]), 0.0, msg="perfect brier")
    assert_close(brier_score([0.5, 0.5], [1, 0]), 0.25, msg="random brier")
    assert_close(brier_score([0.0, 1.0], [1, 0]), 1.0, msg="worst brier")

    assert_close(expected_calibration_error([1.0, 1.0, 0.0, 0.0], [1, 1, 0, 0]), 0.0, tol=0.02, msg="perfect calibration ECE")
    assert_close(expected_calibration_error([0.99, 0.99, 0.99, 0.99], [1, 0, 0, 0]), 0.74, tol=0.02, msg="bad calibration ECE")

    auc = auroc([0.9, 0.8, 0.3, 0.1], [1, 1, 0, 0])
    assert_close(auc, 1.0, msg="perfect AUROC")

    auc2 = auroc([0.1, 0.2, 0.8, 0.9], [1, 1, 0, 0])
    assert_close(auc2, 0.0, msg="worst AUROC")

    auc3 = auroc([0.5, 0.5, 0.5, 0.5], [1, 0, 1, 0])
    assert_close(auc3, 0.5, tol=0.02, msg="random AUROC")

    metrics = compute_all_metrics([0.9, 0.1], [1, 0])
    assert_eq(metrics["n_total"], 2, "n_total")
    assert_eq(metrics["n_correct"], 1, "n_correct")

    print("[evaluator]")
    result = evaluate("perfect", seed=42)
    assert_eq(result["metrics"]["accuracy"], 1.0, "perfect model accuracy")
    assert_close(result["metrics"]["brier_score"], 0.01, tol=0.02, msg="perfect model brier")

    result2 = evaluate("random", seed=42)
    assert_eq(result2["metrics"]["n_total"], len(questions), "random model n_total")

    print("[models]")
    for name in ALL_RUNNERS:
        result = evaluate(name, seed=42)
        assert_eq(result["metrics"]["n_total"], len(questions), f"{name} n_total")
        confs = [r["confidence"] for r in result["detailed_results"]]
        assert_eq(all(0 < c < 1 for c in confs), True, f"{name} confidences in (0,1)")

    print(f"\n{'=' * 40}")
    print(f"Tests: {passed} passed, {failed} failed")
    print(f"{'=' * 40}")

    return failed == 0


def main():
    parser = argparse.ArgumentParser(description="MetaBoundary Benchmark Runner")
    parser.add_argument("--model", type=str, default=None,
                        help=f"Model profile to run. Options: {list(ALL_RUNNERS.keys())}")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output-dir", type=str, default="data", help="Output directory")
    parser.add_argument("--export-data", action="store_true", help="Export question dataset")
    parser.add_argument("--test", action="store_true", help="Run internal tests")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)

    if args.export_data:
        export_data(seed=args.seed, output_dir=args.output_dir)
        return

    if args.model:
        run_single(args.model, seed=args.seed, output_dir=args.output_dir)
    else:
        run_all_models(seed=args.seed, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
