"""
MetaBoundary Test Suite
Run with: python -m pytest tests/ -v
Or:       python runner.py --test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator import generate_questions, generate_dataset, check_answer
from scoring import brier_score, expected_calibration_error, auroc, compute_all_metrics, selective_coverage
from models import get_runner, ALL_RUNNERS, WellCalibratedRunner, OverconfidentRunner
from evaluator import evaluate, evaluate_all


class TestGenerator:
    def test_question_count(self):
        questions = generate_questions(seed=42)
        assert len(questions) >= 50

    def test_has_unanswerable(self):
        questions = generate_questions(seed=42)
        n_ua = sum(1 for q in questions if q["answer"] == "UNANSWERABLE")
        assert n_ua >= 10

    def test_unique_ids(self):
        questions = generate_questions(seed=42)
        ids = [q["id"] for q in questions]
        assert len(ids) == len(set(ids))

    def test_all_fields_present(self):
        questions = generate_questions(seed=42)
        required = {"id", "category", "difficulty", "question", "answer", "accept_alternatives"}
        for q in questions:
            assert required.issubset(set(q.keys())), f"Missing fields in {q['id']}"

    def test_deterministic(self):
        q1 = generate_questions(seed=42)
        q2 = generate_questions(seed=42)
        assert [q["id"] for q in q1] == [q["id"] for q in q2]

    def test_different_seeds_differ(self):
        q1 = generate_questions(seed=42)
        q2 = generate_questions(seed=99)
        ids1 = [q["id"] for q in q1]
        ids2 = [q["id"] for q in q2]
        assert ids1 != ids2

    def test_categories(self):
        questions = generate_questions(seed=42)
        cats = set(q["category"] for q in questions)
        assert "numerical" in cats
        assert "entity" in cats
        assert "unanswerable" in cats

    def test_difficulties(self):
        questions = generate_questions(seed=42)
        diffs = set(q["difficulty"] for q in questions)
        assert "easy" in diffs
        assert "hard" in diffs

    def test_dataset_export(self):
        dataset = generate_dataset(seed=42)
        assert "questions" in dataset
        assert "categories" in dataset
        assert dataset["num_questions"] == len(dataset["questions"])


class TestCheckAnswer:
    def test_exact_match(self):
        assert check_answer("Paris", "Paris") is True

    def test_case_insensitive(self):
        assert check_answer("paris", "Paris") is True

    def test_wrong_answer(self):
        assert check_answer("London", "Paris") is False

    def test_alternatives(self):
        assert check_answer("co2", "carbon dioxide", ["co2"]) is True

    def test_unanswerable_detected(self):
        assert check_answer("UNANSWERABLE", "UNANSWERABLE") is True

    def test_unanswerable_markers(self):
        assert check_answer("cannot answer", "UNANSWERABLE") is True
        assert check_answer("unknown", "UNANSWERABLE") is True
        assert check_answer("does not exist", "UNANSWERABLE") is True

    def test_unanswerable_not_false_positive(self):
        assert check_answer("Paris", "UNANSWERABLE") is False

    def test_partial_match(self):
        assert check_answer("Mount Everest", "Mount Everest") is True
        assert check_answer("Everest", "Mount Everest") is True


class TestScoring:
    def test_brier_perfect(self):
        assert brier_score([1.0, 0.0], [1, 0]) == 0.0

    def test_brier_worst(self):
        assert brier_score([0.0, 1.0], [1, 0]) == 1.0

    def test_brier_random(self):
        assert abs(brier_score([0.5, 0.5], [1, 0]) - 0.25) < 1e-10

    def test_ece_perfect_calibration(self):
        ece = expected_calibration_error([1.0, 1.0, 0.0, 0.0], [1, 1, 0, 0])
        assert ece < 0.02

    def test_ece_bad_calibration(self):
        ece = expected_calibration_error([0.99, 0.99, 0.99, 0.99], [1, 0, 0, 0])
        assert ece > 0.5

    def test_auroc_perfect(self):
        assert auroc([0.9, 0.8, 0.3, 0.1], [1, 1, 0, 0]) == 1.0

    def test_auroc_worst(self):
        assert auroc([0.1, 0.2, 0.8, 0.9], [1, 1, 0, 0]) == 0.0

    def test_auroc_random(self):
        auc = auroc([0.5, 0.5, 0.5, 0.5], [1, 0, 1, 0])
        assert abs(auc - 0.5) < 0.02

    def test_auroc_no_variance(self):
        import math
        auc = auroc([0.5, 0.5], [1, 1])
        assert math.isnan(auc)

    def test_selective_coverage(self):
        sc = selective_coverage([0.9, 0.5, 0.1], [1, 1, 0])
        assert len(sc) == 11
        assert sc[0]["threshold"] == 0.0
        assert sc[-1]["threshold"] == 1.0

    def test_compute_all_metrics(self):
        metrics = compute_all_metrics([0.9, 0.8, 0.2, 0.1], [1, 1, 0, 0])
        assert "brier_score" in metrics
        assert "ece" in metrics
        assert "auroc" in metrics
        assert "metascore" in metrics
        assert metrics["n_total"] == 4
        assert metrics["n_correct"] == 2

    def test_compute_simple(self):
        metrics = compute_all_metrics([0.9, 0.1], [1, 0])
        assert metrics["n_total"] == 2
        assert metrics["n_correct"] == 1

    def test_compute_with_meta(self):
        meta = [
            {"category": "numerical", "difficulty": "easy"},
            {"category": "entity", "difficulty": "hard"},
        ]
        metrics = compute_all_metrics([0.8, 0.3], [1, 0], meta)
        assert "by_category" in metrics
        assert "by_difficulty" in metrics


class TestModels:
    def test_all_runners_exist(self):
        expected = {"well_calibrated", "overconfident", "underconfident", "random", "perfect"}
        assert set(ALL_RUNNERS.keys()) == expected

    def test_get_runner(self):
        for name in ALL_RUNNERS:
            runner = get_runner(name)
            assert runner.name == name

    def test_get_runner_invalid(self):
        try:
            get_runner("nonexistent")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_runner_produces_results(self):
        questions = generate_questions(seed=42)
        for name in ALL_RUNNERS:
            runner = get_runner(name, seed=42)
            results = runner.run_all(questions[:5])
            assert len(results) == 5
            for r in results:
                assert "id" in r
                assert "confidence" in r
                assert 0 < r["confidence"] < 1
                assert "correct" in r

    def test_perfect_runner(self):
        questions = generate_questions(seed=42)
        runner = get_runner("perfect")
        results = runner.run_all(questions)
        corrects = [int(r["correct"]) for r in results]
        assert sum(corrects) == len(corrects)


class TestEvaluator:
    def test_evaluate_single(self):
        result = evaluate("perfect", seed=42)
        assert result["metrics"]["accuracy"] == 1.0
        assert result["metrics"]["n_total"] > 50

    def test_evaluate_all(self):
        all_results, comparison = evaluate_all(seed=42)
        assert len(all_results) == len(ALL_RUNNERS)
        assert len(comparison) == len(ALL_RUNNERS)

    def test_perfect_beats_random(self):
        all_results, comparison = evaluate_all(seed=42)
        scores = {c["model"]: c["metascore"] for c in comparison}
        assert scores["perfect"] > scores["random"]

    def test_well_calibrated_better_brier(self):
        result_wc = evaluate("well_calibrated", seed=42)
        result_oc = evaluate("overconfident", seed=42)
        assert result_wc["metrics"]["brier_score"] < result_oc["metrics"]["brier_score"]

    def test_perfect_low_brier(self):
        result = evaluate("perfect", seed=42)
        assert result["metrics"]["brier_score"] < 0.01
