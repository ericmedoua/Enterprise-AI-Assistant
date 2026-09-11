from app.ai.evaluation.evaluation_ci_report import (
    build_evaluation_ci_report,
)
from app.ai.evaluation.evaluation_comparator import EvaluationComparison
from app.ai.evaluation.evaluation_regression import EvaluationRegression


def test_ci_report_when_deployment_is_ready():
    report = build_evaluation_ci_report(
        quality_gate_passed=True,
        deployment_ready=True,
        retrieval_hit_rate=1.0,
        average_groundedness=0.9,
        average_semantic_relevance=0.8,
        overall_pass_rate=0.85,
        regressions=[],
    )

    assert report.status == "passed"
    assert report.quality_gate_passed is True
    assert report.deployment_ready is True
    assert report.message == ("Evaluation passed and deployment is allowed.")

    assert report.retrieval_hit_rate == 1.0
    assert report.average_groundedness == 0.9
    assert report.average_semantic_relevance == 0.8
    assert report.overall_pass_rate == 0.85


def test_ci_report_when_quality_gate_fails():
    report = build_evaluation_ci_report(
        quality_gate_passed=False,
        deployment_ready=False,
        retrieval_hit_rate=1.0,
        average_groundedness=0.9,
        average_semantic_relevance=0.8,
        overall_pass_rate=0.85,
        regressions=[],
    )

    assert report.status == "failed"
    assert report.quality_gate_passed is False
    assert report.deployment_ready is False
    assert report.message == ("Evaluation quality gate failed.")

    assert report.retrieval_hit_rate == 1.0
    assert report.average_groundedness == 0.9
    assert report.average_semantic_relevance == 0.8
    assert report.overall_pass_rate == 0.85


def test_ci_report_when_deployment_is_blocked_after_quality_pass():
    report = build_evaluation_ci_report(
        quality_gate_passed=True,
        deployment_ready=False,
        retrieval_hit_rate=1.0,
        average_groundedness=0.9,
        average_semantic_relevance=0.8,
        overall_pass_rate=0.85,
        regressions=[],
    )

    assert report.status == "failed"
    assert report.quality_gate_passed is True
    assert report.deployment_ready is False
    assert report.message == (
        "Evaluation passed the quality gate but deployment is blocked."
    )

    assert report.retrieval_hit_rate == 1.0
    assert report.average_groundedness == 0.9
    assert report.average_semantic_relevance == 0.8
    assert report.overall_pass_rate == 0.85


def test_build_evaluation_ci_report_includes_comparison():
    comparison = EvaluationComparison(
        retrieval_hit_rate_delta=-0.10,
        groundedness_delta=0.05,
        semantic_relevance_delta=0.02,
        source_count_delta=0.50,
        overall_pass_rate_delta=-0.10,
    )

    report = build_evaluation_ci_report(
        quality_gate_passed=True,
        deployment_ready=True,
        retrieval_hit_rate=1.0,
        average_groundedness=0.9,
        average_semantic_relevance=0.8,
        overall_pass_rate=0.95,
        comparison=comparison,
        regressions=[],
    )

    assert report.comparison == comparison
    assert report.regressions == []


def test_build_evaluation_ci_report_includes_regressions():
    regression = EvaluationRegression(
        metric_name="average_groundedness",
        previous_value=0.90,
        current_value=0.70,
        delta=-0.20,
        severity="critical",
    )

    report = build_evaluation_ci_report(
        quality_gate_passed=False,
        deployment_ready=False,
        retrieval_hit_rate=1.0,
        average_groundedness=0.70,
        average_semantic_relevance=0.60,
        overall_pass_rate=0.50,
        regressions=[regression],
    )

    assert report.regressions == [regression]


def test_build_evaluation_ci_report_with_regressions():
    regression = EvaluationRegression(
        metric_name="average_groundedness",
        previous_value=0.90,
        current_value=0.70,
        delta=-0.20,
        severity="critical",
    )

    report = build_evaluation_ci_report(
        quality_gate_passed=False,
        deployment_ready=False,
        retrieval_hit_rate=1.0,
        average_groundedness=0.70,
        average_semantic_relevance=0.60,
        overall_pass_rate=0.50,
        regressions=[regression],
    )

    assert report.status == "failed"
    assert report.regressions == [regression]
    assert report.message == (
        "Evaluation quality gate failed and evaluation regressions were detected."
    )


def test_build_evaluation_ci_report_when_regressions_block_deployment():
    regression = EvaluationRegression(
        metric_name="average_groundedness",
        previous_value=0.90,
        current_value=0.84,
        delta=-0.06,
        severity="warning",
    )

    report = build_evaluation_ci_report(
        quality_gate_passed=True,
        deployment_ready=False,
        retrieval_hit_rate=1.0,
        average_groundedness=0.84,
        average_semantic_relevance=0.80,
        overall_pass_rate=1.0,
        regressions=[regression],
    )

    assert report.status == "failed"
    assert report.quality_gate_passed is True
    assert report.deployment_ready is False
    assert report.regressions == [regression]
    assert report.message == (
        "Evaluation passed the quality gate but "
        "deployment is blocked by evaluation regressions."
    )
