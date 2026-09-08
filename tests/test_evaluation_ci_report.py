from app.ai.evaluation.evaluation_ci_report import (
    build_evaluation_ci_report,
)


def test_ci_report_when_deployment_is_ready():
    report = build_evaluation_ci_report(
        quality_gate_passed=True,
        deployment_ready=True,
    )

    assert report.status == "passed"
    assert report.quality_gate_passed is True
    assert report.deployment_ready is True
    assert report.message == ("Evaluation passed and deployment is allowed.")


def test_ci_report_when_quality_gate_fails():
    report = build_evaluation_ci_report(
        quality_gate_passed=False,
        deployment_ready=False,
    )

    assert report.status == "failed"
    assert report.quality_gate_passed is False
    assert report.deployment_ready is False
    assert report.message == ("Evaluation quality gate failed.")


def test_ci_report_when_deployment_is_blocked_after_quality_pass():
    report = build_evaluation_ci_report(
        quality_gate_passed=True,
        deployment_ready=False,
    )

    assert report.status == "failed"
    assert report.quality_gate_passed is True
    assert report.deployment_ready is False
    assert report.message == (
        "Evaluation passed the quality gate but deployment is blocked."
    )
