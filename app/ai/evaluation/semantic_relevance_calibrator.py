from dataclasses import dataclass


@dataclass
class SemanticCalibrationResult:
    relevant_scores: list[float]
    unrelated_scores: list[float]
    relevant_average: float
    unrelated_average: float
    separation: float


def calibrate(
    relevant_scores: list[float],
    unrelated_scores: list[float],
) -> SemanticCalibrationResult:
    relevant_average = (
        sum(relevant_scores) / len(relevant_scores) if relevant_scores else 0.0
    )

    unrelated_average = (
        sum(unrelated_scores) / len(unrelated_scores) if unrelated_scores else 0.0
    )

    return SemanticCalibrationResult(
        relevant_scores=relevant_scores,
        unrelated_scores=unrelated_scores,
        relevant_average=relevant_average,
        unrelated_average=unrelated_average,
        separation=(relevant_average - unrelated_average),
    )


def relevance_band(score: float) -> str:
    """
    Classify a semantic relevance score using the
    current project calibration bands.
    """

    if score >= 0.60:
        return "strong"

    if score >= 0.35:
        return "review"

    return "likely_unrelated"
