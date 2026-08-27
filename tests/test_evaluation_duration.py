from datetime import datetime, timedelta

import pytest

from app.ai.evaluation.evaluation_duration import (
    calculate_duration_seconds,
)


def test_calculate_duration_seconds():
    started = datetime(
        2026,
        8,
        26,
        10,
        0,
        0,
    )

    completed = started + timedelta(seconds=12.5)

    result = calculate_duration_seconds(
        started,
        completed,
    )

    assert result == pytest.approx(12.5)


def test_duration_returns_none_when_not_started():
    completed = datetime(
        2026,
        8,
        26,
        10,
        0,
        0,
    )

    assert (
        calculate_duration_seconds(
            None,
            completed,
        )
        is None
    )


def test_duration_returns_none_when_not_completed():
    started = datetime(
        2026,
        8,
        26,
        10,
        0,
        0,
    )

    assert (
        calculate_duration_seconds(
            started,
            None,
        )
        is None
    )
