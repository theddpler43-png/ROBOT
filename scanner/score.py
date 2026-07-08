from __future__ import annotations


def calc_market_score(
    execution: float | None,
    uniformity: float | None,
    smoothness: float | None,
) -> float | None:
    """
    Итоговая оценка рынка.

    Использует взвешенную модель с понижающими коэффициентами.
    """

    if execution is None:
        return None

    if uniformity is None:
        return None

    if smoothness is None:
        return None

    score = (
        execution * 0.45 +
        uniformity * 0.30 +
        smoothness * 0.25
    )

    if execution < 60:
        score *= 0.50

    if uniformity < 40:
        score *= 0.60

    if smoothness < 40:
        score *= 0.70

    return round(max(0.0, min(score, 100.0)), 2)


def calc_confidence(
    execution: float | None,
    uniformity: float | None,
    smoothness: float | None,
) -> str:
    """
    Оценка уверенности в том, что рынок
    действительно выглядит управляемым алгоритмом.
    """

    if execution is None:
        return "LOW"

    if uniformity is None:
        return "LOW"

    if smoothness is None:
        return "LOW"

    minimum = min(
        execution,
        uniformity,
        smoothness,
    )

    average = (
        execution +
        uniformity +
        smoothness
    ) / 3

    if minimum >= 80 and average >= 85:
        return "HIGH"

    if minimum >= 60 and average >= 70:
        return "MEDIUM"

    return "LOW"
