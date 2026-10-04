"""
MetaBoundary Scoring Functions
All metrics computed from scratch — zero external dependencies.

Metrics:
  - Brier Score: mean squared error between confidence and correctness
  - ECE (Expected Calibration Error): bin-based calibration gap
  - AUROC: discrimination between correct and incorrect predictions
  - MetaScore: weighted composite
  - Selective Coverage: accuracy at varying confidence thresholds
"""


def brier_score(confidences, corrects):
    n = len(confidences)
    if n == 0:
        return 0.0
    return sum((confidences[i] - corrects[i]) ** 2 for i in range(n)) / n


def expected_calibration_error(confidences, corrects, n_bins=15):
    n = len(confidences)
    if n == 0:
        return 0.0

    bin_edges = [i / n_bins for i in range(n_bins + 1)]
    ece = 0.0

    for b in range(n_bins):
        lo, hi = bin_edges[b], bin_edges[b + 1]
        indices = [i for i in range(n) if lo <= confidences[i] < hi or (b == n_bins - 1 and confidences[i] == hi)]
        if not indices:
            continue
        bin_conf = sum(confidences[i] for i in indices) / len(indices)
        bin_acc = sum(corrects[i] for i in indices) / len(indices)
        ece += (len(indices) / n) * abs(bin_acc - bin_conf)

    return ece


def _compute_auc(confidences, corrects):
    pairs = list(zip(confidences, corrects))
    pos = [(c, lab) for c, lab in pairs if lab == 1]
    neg = [(c, lab) for c, lab in pairs if lab == 0]

    if not pos or not neg:
        return float("nan")

    n_pos = len(pos)
    n_neg = len(neg)
    count = 0.0
    ties = 0.0

    for pc, _ in pos:
        for nc, _ in neg:
            if pc > nc:
                count += 1.0
            elif pc == nc:
                ties += 1.0

    return (count + 0.5 * ties) / (n_pos * n_neg)


def auroc(confidences, corrects):
    return _compute_auc(confidences, corrects)


def accuracy(corrects):
    if not corrects:
        return 0.0
    return sum(corrects) / len(corrects)


def selective_coverage(confidences, corrects, thresholds=None):
    if thresholds is None:
        thresholds = [0.1 * i for i in range(11)]

    results = []
    for t in thresholds:
        selected = [(confidences[i], corrects[i]) for i in range(len(confidences)) if confidences[i] >= t]
        if not selected:
            cov = 0.0
            acc = 0.0
        else:
            cov = len(selected) / len(confidences)
            acc = sum(c for _, c in selected) / len(selected)
        results.append({"threshold": round(t, 2), "coverage": round(cov, 4), "accuracy": round(acc, 4)})
    return results


def compute_all_metrics(confidences, corrects, question_meta=None):
    metrics = {}

    metrics["brier_score"] = round(brier_score(confidences, corrects), 6)
    metrics["ece"] = round(expected_calibration_error(confidences, corrects), 6)
    metrics["auroc"] = round(auroc(confidences, corrects), 6) if len(set(corrects)) > 1 else None
    metrics["accuracy"] = round(accuracy(corrects), 4)
    metrics["n_total"] = len(confidences)
    metrics["n_correct"] = sum(corrects)

    metrics["selective_coverage"] = selective_coverage(confidences, corrects)

    if question_meta:
        by_cat = {}
        for i, meta in enumerate(question_meta):
            cat = meta.get("category", "unknown")
            if cat not in by_cat:
                by_cat[cat] = {"confidences": [], "corrects": []}
            by_cat[cat]["confidences"].append(confidences[i])
            by_cat[cat]["corrects"].append(corrects[i])

        by_category = {}
        for cat, data in by_cat.items():
            by_category[cat] = {
                "n": len(data["corrects"]),
                "accuracy": round(accuracy(data["corrects"]), 4),
                "brier": round(brier_score(data["confidences"], data["corrects"]), 6),
                "mean_confidence": round(sum(data["confidences"]) / len(data["confidences"]), 4),
            }
        metrics["by_category"] = by_category

        by_diff = {}
        for i, meta in enumerate(question_meta):
            diff = meta.get("difficulty", "unknown")
            if diff not in by_diff:
                by_diff[diff] = {"confidences": [], "corrects": []}
            by_diff[diff]["confidences"].append(confidences[i])
            by_diff[diff]["corrects"].append(corrects[i])

        by_difficulty = {}
        for diff, data in by_diff.items():
            by_difficulty[diff] = {
                "n": len(data["corrects"]),
                "accuracy": round(accuracy(data["corrects"]), 4),
                "brier": round(brier_score(data["confidences"], data["corrects"]), 6),
                "mean_confidence": round(sum(data["confidences"]) / len(data["confidences"]), 4),
            }
        metrics["by_difficulty"] = by_difficulty

    brier = metrics["brier_score"]
    ece = metrics["ece"]
    auroc_val = metrics["auroc"]
    if auroc_val is None:
        if metrics["accuracy"] == 1.0:
            auroc_val = 1.0
        elif metrics["accuracy"] == 0.0:
            auroc_val = 0.0
        else:
            auroc_val = 0.5
    metrics["metascore"] = round(
        0.4 * (1 - brier) + 0.3 * (1 - ece) + 0.3 * auroc_val,
        4
    )

    return metrics


def format_metrics(metrics):
    lines = []
    lines.append("=" * 60)
    lines.append("MetaBoundary Evaluation Results")
    lines.append("=" * 60)
    lines.append(f"Total questions:  {metrics['n_total']}")
    lines.append(f"Correct:          {metrics['n_correct']}")
    lines.append(f"Accuracy:         {metrics['accuracy']:.4f}")
    lines.append(f"Brier Score:      {metrics['brier_score']:.6f}  (lower = better, 0 = perfect)")
    lines.append(f"ECE:              {metrics['ece']:.6f}  (lower = better, 0 = perfect)")
    lines.append(f"AUROC:            {metrics['auroc']:.6f}" if metrics['auroc'] is not None else "AUROC:            N/A (no variance in correctness)")
    lines.append(f"MetaScore:        {metrics['metascore']:.4f}  (higher = better, 1 = perfect)")
    lines.append("")

    if "by_category" in metrics:
        lines.append("-" * 60)
        lines.append("Breakdown by Category")
        lines.append("-" * 60)
        for cat, stats in sorted(metrics["by_category"].items()):
            lines.append(f"  {cat:20s}  n={stats['n']:3d}  acc={stats['accuracy']:.4f}  brier={stats['brier']:.6f}  conf={stats['mean_confidence']:.4f}")
        lines.append("")

    if "by_difficulty" in metrics:
        lines.append("-" * 60)
        lines.append("Breakdown by Difficulty")
        lines.append("-" * 60)
        for diff, stats in sorted(metrics["by_difficulty"].items()):
            lines.append(f"  {diff:10s}  n={stats['n']:3d}  acc={stats['accuracy']:.4f}  brier={stats['brier']:.6f}  conf={stats['mean_confidence']:.4f}")
        lines.append("")

    lines.append("-" * 60)
    lines.append("Selective Coverage")
    lines.append("-" * 60)
    for sc in metrics["selective_coverage"]:
        lines.append(f"  threshold={sc['threshold']:.1f}  coverage={sc['coverage']:.4f}  accuracy={sc['accuracy']:.4f}")

    lines.append("=" * 60)
    return "\n".join(lines)
