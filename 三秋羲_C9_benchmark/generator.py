"""
MetaBoundary Question Generator
Generates factual questions with ground-truth answers for metacognitive evaluation.
Questions span 5 categories and 2 difficulty levels, plus unanswerable items.
Zero external dependencies. Deterministic with fixed seed.
"""

import random
import json
import os


def _numerical_easy():
    return [
        {"id": "NE01", "category": "numerical", "difficulty": "easy",
         "question": "How many continents are there on Earth?",
         "answer": "7", "accept_alternatives": ["seven"]},
        {"id": "NE02", "category": "numerical", "difficulty": "easy",
         "question": "How many sides does a hexagon have?",
         "answer": "6", "accept_alternatives": ["six"]},
        {"id": "NE03", "category": "numerical", "difficulty": "easy",
         "question": "How many legs does a spider have?",
         "answer": "8", "accept_alternatives": ["eight"]},
        {"id": "NE04", "category": "numerical", "difficulty": "easy",
         "question": "How many colors are in a rainbow?",
         "answer": "7", "accept_alternatives": ["seven"]},
        {"id": "NE05", "category": "numerical", "difficulty": "easy",
         "question": "How many strings does a standard guitar have?",
         "answer": "6", "accept_alternatives": ["six"]},
        {"id": "NE06", "category": "numerical", "difficulty": "easy",
         "question": "How many keys does a standard piano have?",
         "answer": "88", "accept_alternatives": ["eighty-eight", "eighty eight"]},
        {"id": "NE07", "category": "numerical", "difficulty": "easy",
         "question": "How many teeth does an adult human typically have?",
         "answer": "32", "accept_alternatives": ["thirty-two", "thirty two"]},
        {"id": "NE08", "category": "numerical", "difficulty": "easy",
         "question": "How many chambers does the human heart have?",
         "answer": "4", "accept_alternatives": ["four"]},
        {"id": "NE09", "category": "numerical", "difficulty": "easy",
         "question": "How many players are on a standard soccer team on the field?",
         "answer": "11", "accept_alternatives": ["eleven"]},
        {"id": "NE10", "category": "numerical", "difficulty": "easy",
         "question": "How many days are in a non-leap year?",
         "answer": "365", "accept_alternatives": ["three hundred sixty-five"]},
        {"id": "NE11", "category": "numerical", "difficulty": "easy",
         "question": "How many legs does an insect have?",
         "answer": "6", "accept_alternatives": ["six"]},
        {"id": "NE12", "category": "numerical", "difficulty": "easy",
         "question": "How many senses are traditionally recognized in humans?",
         "answer": "5", "accept_alternatives": ["five"]},
        {"id": "NE13", "category": "numerical", "difficulty": "easy",
         "question": "How many sides does an octagon have?",
         "answer": "8", "accept_alternatives": ["eight"]},
        {"id": "NE14", "category": "numerical", "difficulty": "easy",
         "question": "How many bones are in the adult human body (approximate count)?",
         "answer": "206", "accept_alternatives": ["two hundred six", "206"]},
        {"id": "NE15", "category": "numerical", "difficulty": "easy",
         "question": "How many faces does a cube have?",
         "answer": "6", "accept_alternatives": ["six"]},
        {"id": "NE16", "category": "numerical", "difficulty": "easy",
         "question": "How many faces does a standard die (singular of dice) have?",
         "answer": "6", "accept_alternatives": ["six"]},
    ]


def _numerical_hard():
    return [
        {"id": "NH01", "category": "numerical", "difficulty": "hard",
         "question": "What is the atomic number of oxygen?",
         "answer": "8", "accept_alternatives": ["eight"]},
        {"id": "NH02", "category": "numerical", "difficulty": "hard",
         "question": "What is the atomic number of gold?",
         "answer": "79", "accept_alternatives": ["seventy-nine"]},
        {"id": "NH03", "category": "numerical", "difficulty": "hard",
         "question": "What is the speed of light in vacuum, in meters per second (approximate, nearest power of 10)?",
         "answer": "300000000", "accept_alternatives": ["3×10^8", "3e8", "3*10^8", "299792458", "three hundred million"]},
        {"id": "NH04", "category": "numerical", "difficulty": "hard",
         "question": "What is the boiling point of water in degrees Fahrenheit at sea level?",
         "answer": "212", "accept_alternatives": ["212°F", "212 degrees"]},
        {"id": "NH05", "category": "numerical", "difficulty": "hard",
         "question": "How many bones does a shark have?",
         "answer": "0", "accept_alternatives": ["zero", "none", "no bones"]},
        {"id": "NH06", "category": "numerical", "difficulty": "hard",
         "question": "What is the approximate depth of the Mariana Trench in meters?",
         "answer": "11000", "accept_alternatives": ["10994", "10984", "11034", "~11000", "about 11000"]},
        {"id": "NH07", "category": "numerical", "difficulty": "hard",
         "question": "In what year was the Declaration of Independence signed?",
         "answer": "1776", "accept_alternatives": []},
        {"id": "NH08", "category": "numerical", "difficulty": "hard",
         "question": "How many chromosomes do humans have in each somatic cell?",
         "answer": "46", "accept_alternatives": ["forty-six"]},
        {"id": "NH09", "category": "numerical", "difficulty": "hard",
         "question": "What is the approximate distance from Earth to the Sun in million kilometers?",
         "answer": "150", "accept_alternatives": ["149.6", "~150", "about 150", "147", "152"]},
        {"id": "NH10", "category": "numerical", "difficulty": "hard",
         "question": "What is the atomic number of uranium?",
         "answer": "92", "accept_alternatives": ["ninety-two"]},
        {"id": "NH11", "category": "numerical", "difficulty": "hard",
         "question": "How many valence electrons does carbon have?",
         "answer": "4", "accept_alternatives": ["four"]},
        {"id": "NH12", "category": "numerical", "difficulty": "hard",
         "question": "What is the melting point of iron in degrees Celsius (approximate)?",
         "answer": "1538", "accept_alternatives": ["1535", "1540", "~1538", "about 1538"]},
        {"id": "NH13", "category": "numerical", "difficulty": "hard",
         "question": "How many planets in our solar system have rings?",
         "answer": "4", "accept_alternatives": ["four", "4 planets"]},
        {"id": "NH14", "category": "numerical", "difficulty": "hard",
         "question": "What is the approximate number of muscles in the human body?",
         "answer": "600", "accept_alternatives": ["640", "650", "~600", "about 600", "over 600"]},
        {"id": "NH15", "category": "numerical", "difficulty": "hard",
         "question": "In what year did the Berlin Wall fall?",
         "answer": "1989", "accept_alternatives": []},
        {"id": "NH16", "category": "numerical", "difficulty": "hard",
         "question": "What is the atomic number of iron?",
         "answer": "26", "accept_alternatives": ["twenty-six"]},
    ]


def _entity_easy():
    return [
        {"id": "EE01", "category": "entity", "difficulty": "easy",
         "question": "What is the capital of France?",
         "answer": "Paris", "accept_alternatives": []},
        {"id": "EE02", "category": "entity", "difficulty": "easy",
         "question": "What is the largest ocean on Earth?",
         "answer": "Pacific Ocean", "accept_alternatives": ["pacific", "the pacific", "pacific ocean"]},
        {"id": "EE03", "category": "entity", "difficulty": "easy",
         "question": "What gas do plants absorb from the atmosphere during photosynthesis?",
         "answer": "carbon dioxide", "accept_alternatives": ["co2", "carbon dioxide (co2)"]},
        {"id": "EE04", "category": "entity", "difficulty": "easy",
         "question": "What is the hardest natural mineral on the Mohs scale?",
         "answer": "diamond", "accept_alternatives": []},
        {"id": "EE05", "category": "entity", "difficulty": "easy",
         "question": "Who painted the Mona Lisa?",
         "answer": "Leonardo da Vinci", "accept_alternatives": ["da vinci", "leonardo"]},
        {"id": "EE06", "category": "entity", "difficulty": "easy",
         "question": "What is the largest planet in our solar system?",
         "answer": "Jupiter", "accept_alternatives": []},
        {"id": "EE07", "category": "entity", "difficulty": "easy",
         "question": "What is the chemical symbol for water?",
         "answer": "H2O", "accept_alternatives": ["h2o"]},
        {"id": "EE08", "category": "entity", "difficulty": "easy",
         "question": "What is the tallest mountain on Earth above sea level?",
         "answer": "Mount Everest", "accept_alternatives": ["everest", "mt everest"]},
        {"id": "EE09", "category": "entity", "difficulty": "easy",
         "question": "What is the largest mammal in the world?",
         "answer": "blue whale", "accept_alternatives": ["the blue whale"]},
        {"id": "EE10", "category": "entity", "difficulty": "easy",
         "question": "What is the currency of Japan?",
         "answer": "yen", "accept_alternatives": ["japanese yen", "¥"]},
        {"id": "EE11", "category": "entity", "difficulty": "easy",
         "question": "What is the main ingredient in bread (the flour base)?",
         "answer": "flour", "accept_alternatives": ["wheat flour", "wheat"]},
        {"id": "EE12", "category": "entity", "difficulty": "easy",
         "question": "What organ do fish use to breathe underwater?",
         "answer": "gills", "accept_alternatives": ["gill"]},
        {"id": "EE13", "category": "entity", "difficulty": "easy",
         "question": "What is the largest desert in the world?",
         "answer": "Antarctic Desert", "accept_alternatives": ["antarctica", "antarctic", "antarctic desert"]},
        {"id": "EE14", "category": "entity", "difficulty": "easy",
         "question": "What metal is primarily extracted from bauxite ore?",
         "answer": "aluminum", "accept_alternatives": ["aluminium"]},
        {"id": "EE15", "category": "entity", "difficulty": "easy",
         "question": "What is the largest organ in the human body?",
         "answer": "skin", "accept_alternatives": ["the skin"]},
        {"id": "EE16", "category": "entity", "difficulty": "easy",
         "question": "Who wrote the play 'Romeo and Juliet'?",
         "answer": "William Shakespeare", "accept_alternatives": ["shakespeare"]},
    ]


def _entity_hard():
    return [
        {"id": "EH01", "category": "entity", "difficulty": "hard",
         "question": "What is the chemical symbol for tungsten?",
         "answer": "W", "accept_alternatives": ["w"]},
        {"id": "EH02", "category": "entity", "difficulty": "hard",
         "question": "Who discovered the structure of DNA alongside Watson?",
         "answer": "Francis Crick", "accept_alternatives": ["crick", "francis crick"]},
        {"id": "EH03", "category": "entity", "difficulty": "hard",
         "question": "What is the deepest point in the world's oceans called?",
         "answer": "Challenger Deep", "accept_alternatives": ["the challenger deep"]},
        {"id": "EH04", "category": "entity", "difficulty": "hard",
         "question": "What is the rarest naturally occurring element in the Earth's crust?",
         "answer": "astatine", "accept_alternatives": ["at"]},
        {"id": "EH05", "category": "entity", "difficulty": "hard",
         "question": "Who composed 'The Rite of Spring' (Le Sacre du printemps)?",
         "answer": "Igor Stravinsky", "accept_alternatives": ["stravinsky"]},
        {"id": "EH06", "category": "entity", "difficulty": "hard",
         "question": "What is the capital of Bhutan?",
         "answer": "Thimphu", "accept_alternatives": []},
        {"id": "EH07", "category": "entity", "difficulty": "hard",
         "question": "What enzyme unwinds DNA during replication?",
         "answer": "helicase", "accept_alternatives": ["dna helicase"]},
        {"id": "EH08", "category": "entity", "difficulty": "hard",
         "question": "Who developed the first successful polio vaccine?",
         "answer": "Jonas Salk", "accept_alternatives": ["salk"]},
        {"id": "EH09", "category": "entity", "difficulty": "hard",
         "question": "What is the longest river in Africa?",
         "answer": "Nile", "accept_alternatives": ["the nile", "nile river"]},
        {"id": "EH10", "category": "entity", "difficulty": "hard",
         "question": "What is the SI unit of electrical resistance?",
         "answer": "ohm", "accept_alternatives": ["ohms", "Ω"]},
        {"id": "EH11", "category": "entity", "difficulty": "hard",
         "question": "Who painted 'Guernica'?",
         "answer": "Pablo Picasso", "accept_alternatives": ["picasso"]},
        {"id": "EH12", "category": "entity", "difficulty": "hard",
         "question": "What is the most abundant gas in Earth's atmosphere?",
         "answer": "nitrogen", "accept_alternatives": ["n2"]},
        {"id": "EH13", "category": "entity", "difficulty": "hard",
         "question": "What is the capital of New Zealand?",
         "answer": "Wellington", "accept_alternatives": []},
        {"id": "EH14", "category": "entity", "difficulty": "hard",
         "question": "Who is credited with inventing the first practical telephone?",
         "answer": "Alexander Graham Bell", "accept_alternatives": ["bell", "graham bell"]},
        {"id": "EH15", "category": "entity", "difficulty": "hard",
         "question": "What mineral has the lowest hardness on the Mohs scale?",
         "answer": "talc", "accept_alternatives": []},
        {"id": "EH16", "category": "entity", "difficulty": "hard",
         "question": "What is the largest moon of Saturn?",
         "answer": "Titan", "accept_alternatives": []},
    ]


def _unanswerable():
    return [
        {"id": "UA01", "category": "unanswerable", "difficulty": "easy",
         "question": "When did the United States land on the Sun?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "false_premise"},
        {"id": "UA02", "category": "unanswerable", "difficulty": "easy",
         "question": "What is the capital city of Atlantis?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "fictional_entity"},
        {"id": "UA03", "category": "unanswerable", "difficulty": "easy",
         "question": "What is the atomic number of unobtainium?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "fictional_entity"},
        {"id": "UA04", "category": "unanswerable", "difficulty": "easy",
         "question": "Who won the Super Bowl in 2035?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "future_event"},
        {"id": "UA05", "category": "unanswerable", "difficulty": "easy",
         "question": "What is the phone number of the President of France?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "private_info"},
        {"id": "UA06", "category": "unanswerable", "difficulty": "easy",
         "question": "How many horns does a triceratops have on its tail?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "false_premise"},
        {"id": "UA07", "category": "unanswerable", "difficulty": "easy",
         "question": "What color is the number 17?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "category_error"},
        {"id": "UA08", "category": "unanswerable", "difficulty": "easy",
         "question": "When was the last time a human walked on Mars?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "false_premise"},
        {"id": "UA09", "category": "unanswerable", "difficulty": "easy",
         "question": "What is the name of the dragon living in Loch Ness?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "false_premise"},
        {"id": "UA10", "category": "unanswerable", "difficulty": "easy",
         "question": "What year did dinosaurs go extinct on Jupiter?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "false_premise"},
        {"id": "UA11", "category": "unanswerable", "difficulty": "easy",
         "question": "Who is the current King of the United States?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "false_premise"},
        {"id": "UA12", "category": "unanswerable", "difficulty": "easy",
         "question": "What is the boiling point of the letter 'A'?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "category_error"},
        {"id": "UA13", "category": "unanswerable", "difficulty": "easy",
         "question": "What is the chemical formula for dragon blood?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "fictional_entity"},
        {"id": "UA14", "category": "unanswerable", "difficulty": "easy",
         "question": "How many goals did Brazil score in the 2030 FIFA World Cup final?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "future_event"},
        {"id": "UA15", "category": "unanswerable", "difficulty": "easy",
         "question": "What is the weight of an idea?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "category_error"},
        {"id": "UA16", "category": "unanswerable", "difficulty": "easy",
         "question": "Who was the first person to swim to the bottom of the Pacific Ocean without equipment?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "false_premise"},
        {"id": "UA17", "category": "unanswerable", "difficulty": "easy",
         "question": "What is the capital of Narnia?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "fictional_entity"},
        {"id": "UA18", "category": "unanswerable", "difficulty": "easy",
         "question": "When did the Moon produce its last volcanic eruption (in recorded history)?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "false_premise"},
        {"id": "UA19", "category": "unanswerable", "difficulty": "easy",
         "question": "What is the social security number of Albert Einstein?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "private_info"},
        {"id": "UA20", "category": "unanswerable", "difficulty": "easy",
         "question": "How many wings does a penguin have?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "false_premise",
         "note": "Penguins have flippers, not wings — but this is debatable. Marked unanswerable due to definitional ambiguity."},
        {"id": "UA21", "category": "unanswerable", "difficulty": "easy",
         "question": "What is the exact number of atoms in the universe?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "impossible_precision"},
        {"id": "UA22", "category": "unanswerable", "difficulty": "easy",
         "question": "Who will be the last human born?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "future_event"},
        {"id": "UA23", "category": "unanswerable", "difficulty": "easy",
         "question": "What did Abraham Lincoln eat for breakfast on his 10th birthday?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "unrecorded_detail"},
        {"id": "UA24", "category": "unanswerable", "difficulty": "easy",
         "question": "What is the square root of a cloud?",
         "answer": "UNANSWERABLE", "accept_alternatives": [],
         "unanswerable_type": "category_error"},
    ]


def generate_questions(seed=42):
    rng = random.Random(seed)

    all_questions = []
    all_questions.extend(_numerical_easy())
    all_questions.extend(_numerical_hard())
    all_questions.extend(_entity_easy())
    all_questions.extend(_entity_hard())
    all_questions.extend(_unanswerable())

    for q in all_questions:
        if "accept_alternatives" not in q:
            q["accept_alternatives"] = []

    shuffled = list(all_questions)
    rng.shuffle(shuffled)

    return shuffled


def generate_dataset(output_path=None, seed=42):
    questions = generate_questions(seed=seed)
    dataset = {
        "name": "MetaBoundary",
        "version": "1.0.0",
        "description": "Metacognitive knowledge boundary benchmark",
        "seed": seed,
        "num_questions": len(questions),
        "categories": {
            "numerical_easy": sum(1 for q in questions if q["category"] == "numerical" and q["difficulty"] == "easy"),
            "numerical_hard": sum(1 for q in questions if q["category"] == "numerical" and q["difficulty"] == "hard"),
            "entity_easy": sum(1 for q in questions if q["category"] == "entity" and q["difficulty"] == "easy"),
            "entity_hard": sum(1 for q in questions if q["category"] == "entity" and q["difficulty"] == "hard"),
            "unanswerable": sum(1 for q in questions if q["category"] == "unanswerable"),
        },
        "questions": questions,
    }

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)

    return dataset


def check_answer(model_answer, ground_truth, alternatives=None):
    if ground_truth == "UNANSWERABLE":
        normalized = model_answer.strip().lower()
        unanswerable_markers = [
            "unanswerable", "cannot answer", "can't answer",
            "no answer", "impossible to answer", "unknown",
            "does not exist", "doesn't exist", "n/a", "na",
            "not possible", "no such", "never happened",
            "fictional", "no record", "undefined",
        ]
        return any(marker in normalized for marker in unanswerable_markers)

    normalized_answer = ground_truth.strip().lower()
    normalized_model = model_answer.strip().lower()

    if normalized_answer in normalized_model or normalized_model in normalized_answer:
        return True

    if normalized_model == normalized_answer:
        return True

    if alternatives:
        for alt in alternatives:
            normalized_alt = alt.strip().lower()
            if normalized_alt in normalized_model or normalized_model in normalized_alt:
                return True

    return False


if __name__ == "__main__":
    dataset = generate_dataset()
    print(f"Generated {dataset['num_questions']} questions")
    for cat, count in dataset["categories"].items():
        print(f"  {cat}: {count}")
