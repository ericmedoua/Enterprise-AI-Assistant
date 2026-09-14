from app.ai.evaluation.benchmark import EvaluationCase


RAG_EVALUATION_DATASET = [
    EvaluationCase(
        question="What do rabbits like to eat?",
        expected_source="This Book Belongs To.pdf",
        expected_answer="Rabbits love to munch on carrots.",
    ),
    EvaluationCase(
        question="What can horses do?",
        expected_source="This Book Belongs To.pdf",
        expected_answer="Horses can run fast and carry people.",
    ),
    EvaluationCase(
        question="What do cows give us?",
        expected_source="This Book Belongs To.pdf",
        expected_answer="Cows give us milk.",
    ),
    EvaluationCase(
        question="What do ducks have that helps them swim?",
        expected_source="This Book Belongs To.pdf",
        expected_answer="Ducks have webbed feet.",
    ),
    EvaluationCase(
        question="What do monkeys do?",
        expected_source="This Book Belongs To.pdf",
        expected_answer="Monkeys swing from trees and love bananas.",
    ),
    EvaluationCase(
        question="What do giraffes have to help them reach tall trees?",
        expected_source="This Book Belongs To.pdf",
        expected_answer="Giraffes have very long necks.",
    ),
    EvaluationCase(
        question="What do penguins do on ice?",
        expected_source="This Book Belongs To.pdf",
        expected_answer="Penguins waddle and slide on ice.",
    ),
    EvaluationCase(
        question="What do octopuses have and what can they do?",
        expected_source="This Book Belongs To.pdf",
        expected_answer="Octopuses have eight arms and can squirt ink.",
    ),
]
