from app.ai.evaluation.benchmark import EvaluationCase


RAG_EVALUATION_DATASET = [
    EvaluationCase(
        question="What do monkeys do?",
        expected_source="This Book Belongs To.pdf",
        expected_answer=("Monkeys swing from trees and love bananas."),
    ),
    EvaluationCase(
        question="What do reindeer have?",
        expected_source="This Book Belongs To.pdf",
        expected_answer=("Reindeer have antlers and pull sleds in stories."),
    ),
]
