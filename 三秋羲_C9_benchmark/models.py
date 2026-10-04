"""
MetaBoundary Mock Model Runners
Simulates different metacognitive profiles for benchmark validation.
Each runner takes a question and returns (answer, confidence).
Zero external dependencies.
"""

import random
import hashlib
from generator import check_answer


class BaseRunner:
    def __init__(self, name, seed=42):
        self.name = name
        self.rng = random.Random(seed)
        self.results = []

    def run(self, question):
        raise NotImplementedError

    def run_all(self, questions):
        self.results = []
        for q in questions:
            answer, confidence = self.run(q)
            is_correct = check_answer(answer, q["answer"], q.get("accept_alternatives", []))
            self.results.append({
                "id": q["id"],
                "question": q["question"],
                "category": q["category"],
                "difficulty": q["difficulty"],
                "ground_truth": q["answer"],
                "model_answer": answer,
                "confidence": confidence,
                "correct": is_correct,
            })
        return self.results


class WellCalibratedRunner(BaseRunner):
    """Answers with confidence proportional to actual knowledge."""

    def __init__(self, seed=42):
        super().__init__("WellCalibrated", seed)

    def run(self, question):
        if question["answer"] == "UNANSWERABLE":
            conf = self.rng.gauss(0.85, 0.08)
            conf = max(0.01, min(0.99, conf))
            return "UNANSWERABLE", round(conf, 4)

        if question["difficulty"] == "easy":
            base_acc = 0.88
        else:
            base_acc = 0.52

        noise = self.rng.gauss(0, 0.12)
        conf = base_acc + noise
        conf = max(0.01, min(0.99, conf))

        correct = self.rng.random() < base_acc
        if correct:
            return question["answer"], round(conf, 4)
        else:
            return f"WRONG_{question['id']}", round(conf, 4)


class OverconfidentRunner(BaseRunner):
    """Systematically overestimates confidence — simulates hallucination-prone behavior."""

    def __init__(self, seed=42):
        super().__init__("Overconfident", seed)

    def run(self, question):
        if question["answer"] == "UNANSWERABLE":
            conf = self.rng.gauss(0.45, 0.15)
            conf = max(0.05, min(0.99, conf))
            sometimes_detect = self.rng.random() < 0.3
            if sometimes_detect:
                return "UNANSWERABLE", round(1 - conf, 4)
            return f"CONFIDENT_WRONG_{question['id']}", round(conf, 4)

        if question["difficulty"] == "easy":
            base_acc = 0.82
        else:
            base_acc = 0.38

        noise = self.rng.gauss(0, 0.15)
        conf = base_acc + 0.25 + noise
        conf = max(0.05, min(0.99, conf))

        correct = self.rng.random() < base_acc
        if correct:
            return question["answer"], round(conf, 4)
        else:
            return f"WRONG_{question['id']}", round(conf, 4)


class UnderconfidentRunner(BaseRunner):
    """Systematically underestimates confidence — knows more than it thinks."""

    def __init__(self, seed=42):
        super().__init__("Underconfident", seed)

    def run(self, question):
        if question["answer"] == "UNANSWERABLE":
            conf = self.rng.gauss(0.6, 0.1)
            conf = max(0.01, min(0.99, conf))
            return "UNANSWERABLE", round(conf, 4)

        if question["difficulty"] == "easy":
            base_acc = 0.85
        else:
            base_acc = 0.55

        noise = self.rng.gauss(0, 0.1)
        conf = base_acc - 0.25 + noise
        conf = max(0.01, min(0.99, conf))

        correct = self.rng.random() < base_acc
        if correct:
            return question["answer"], round(conf, 4)
        else:
            return f"WRONG_{question['id']}", round(conf, 4)


class RandomRunner(BaseRunner):
    """Random confidence — baseline for comparison."""

    def __init__(self, seed=42):
        super().__init__("Random", seed)

    def run(self, question):
        conf = self.rng.random()
        conf = max(0.01, min(0.99, conf))

        if question["answer"] == "UNANSWERABLE":
            detect = self.rng.random() < 0.5
            if detect:
                return "UNANSWERABLE", round(1 - conf, 4)
            return f"RANDOM_WRONG_{question['id']}", round(conf, 4)

        correct = self.rng.random() < 0.5
        if correct:
            return question["answer"], round(conf, 4)
        else:
            return f"WRONG_{question['id']}", round(conf, 4)


class PerfectRunner(BaseRunner):
    """Always correct and perfectly calibrated — theoretical upper bound."""

    def __init__(self, seed=42):
        super().__init__("Perfect", seed)

    def run(self, question):
        if question["answer"] == "UNANSWERABLE":
            return "UNANSWERABLE", 0.99

        return question["answer"], 0.99


ALL_RUNNERS = {
    "well_calibrated": WellCalibratedRunner,
    "overconfident": OverconfidentRunner,
    "underconfident": UnderconfidentRunner,
    "random": RandomRunner,
    "perfect": PerfectRunner,
}


def get_runner(name, seed=42):
    if name not in ALL_RUNNERS:
        raise ValueError(f"Unknown runner: {name}. Available: {list(ALL_RUNNERS.keys())}")
    return ALL_RUNNERS[name](seed=seed)
