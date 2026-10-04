"""
MetaBoundary Evaluator
Orchestrates the full evaluation pipeline:
  1. Generate questions
  2. Run model
  3. Compute metrics
  4. Output structured results
"""

import json
import os
import time
from generator import generate_dataset, check_answer
from scoring import compute_all_metrics, format_metrics
from models import get_runner, ALL_RUNNERS


def evaluate(runner_name, seed=42, output_dir=None):
    start_time = time.time()

    dataset = generate_dataset(seed=seed)
    questions = dataset["questions"]

    runner = get_runner(runner_name, seed=seed)
    results = runner.run_all(questions)

    confidences = [r["confidence"] for r in results]
    corrects = [int(r["correct"]) for r in results]
    question_meta = [{"category": r["category"], "difficulty": r["difficulty"]} for r in results]

    metrics = compute_all_metrics(confidences, corrects, question_meta)

    elapsed = time.time() - start_time
    metrics["elapsed_seconds"] = round(elapsed, 3)
    metrics["model_profile"] = runner_name
    metrics["seed"] = seed

    output = {
        "benchmark": "MetaBoundary",
        "version": "1.0.0",
        "model_profile": runner_name,
        "seed": seed,
        "metrics": metrics,
        "detailed_results": results,
    }

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

        results_path = os.path.join(output_dir, f"results_{runner_name}.json")
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        summary_path = os.path.join(output_dir, f"summary_{runner_name}.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(format_metrics(metrics))
            f.write(f"\n\nElapsed: {elapsed:.3f}s\n")

    return output


def evaluate_all(seed=42, output_dir=None):
    all_results = {}
    for name in ALL_RUNNERS:
        result = evaluate(name, seed=seed, output_dir=output_dir)
        all_results[name] = result

    comparison = []
    for name, result in all_results.items():
        m = result["metrics"]
        comparison.append({
            "model": name,
            "accuracy": m["accuracy"],
            "brier": m["brier_score"],
            "ece": m["ece"],
            "auroc": m["auroc"],
            "metascore": m["metascore"],
        })

    comparison.sort(key=lambda x: x["metascore"], reverse=True)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        comp_path = os.path.join(output_dir, "comparison.json")
        with open(comp_path, "w", encoding="utf-8") as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)

        lines = []
        lines.append("=" * 80)
        lines.append("MetaBoundary — Model Comparison")
        lines.append("=" * 80)
        lines.append(f"{'Model':<20} {'Accuracy':>10} {'Brier':>10} {'ECE':>10} {'AUROC':>10} {'MetaScore':>10}")
        lines.append("-" * 80)
        for c in comparison:
            auroc_str = f"{c['auroc']:.4f}" if c['auroc'] is not None else "N/A"
            lines.append(f"{c['model']:<20} {c['accuracy']:>10.4f} {c['brier']:>10.6f} {c['ece']:>10.6f} {auroc_str:>10} {c['metascore']:>10.4f}")
        lines.append("=" * 80)

        comp_txt = "\n".join(lines)
        comp_txt_path = os.path.join(output_dir, "comparison.txt")
        with open(comp_txt_path, "w", encoding="utf-8") as f:
            f.write(comp_txt)

        print(comp_txt)

    return all_results, comparison
