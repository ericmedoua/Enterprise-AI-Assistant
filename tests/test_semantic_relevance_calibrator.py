import pytest

from app.ai.evaluation.semantic_relevance_calibrator import (
    calibrate,
    relevance_band,
)


def test_calibrate_semantic_relevance():
    result = calibrate(
        relevant_scores=[
            0.6827,
            0.3804,
        ],
        unrelated_scores=[
            0.2294,
        ],
    )

    assert result.relevant_average == pytest.approx(
        0.53155,
        rel=1e-4,
    )

    assert result.unrelated_average == pytest.approx(
        0.2294,
        rel=1e-4,
    )

    assert result.separation == pytest.approx(
        0.30215,
        rel=1e-4,
    )


def test_relevance_band_strong():
    assert relevance_band(0.6827) == "strong"


def test_relevance_band_review():
    assert relevance_band(0.3804) == "review"


def test_relevance_band_likely_unrelated():
    assert relevance_band(0.2294) == "likely_unrelated"
