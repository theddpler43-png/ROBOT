def calc_market_score(
    execution: float | None,
    uniformity: float | None,
    smoothness: float | None,
) -> float | None:
    """
    Итоговая оценка рынка.

    Использует взвешенную модель с понижающими коэффициентами,
    чтобы одна слабая метрика не позволяла получить высокий Score.
    """

    values = (execution, uniformity, smoothness)

    if any(v is None for v in values):
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

    return round(min(score, 100.0), 2)
