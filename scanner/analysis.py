from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AnalysisResult:
    score: float | None
    confidence: str
    pattern: str


def analyze_market(
    execution: float |None,
    uniformity: float | None,
    smoothness: float | None,
    execution_rhythm: float | None = None,
) -> AnalysisResult:
    score = _calc_score(
        execution,
        uniformity,
        smoothness,
        execution_rhythm,
    )

    confidence = _calc_confidence(score)

    pattern = _detect_pattern(score)

    return AnalysisResult(
        score=score,
        confidence=confidence,
        pattern=pattern,
    )


def _calc_score(
    execution: float | None,
    uniformity: float | None,
    smoothness: float | None,
    execution_rhythm: float | None,
) -> float | None:
    metrics: list[tuple[float, float]] = []

    if execution is not None:
        metrics.append((execution, 0.40))

    if uniformity is not None:
        metrics.append((uniformity, 0.20))

    if smoothness is not None:
        metrics.append((smoothness, 0.25))

    if execution_rhythm is not None:
        metrics.append((execution_rhythm, 0.15))

    if not metrics:
        return None

    weight_sum = sum(weight for _, weight in metrics)

    score = sum(
        value * weight
        for value, weight in metrics
    ) / weight_sum

    return round(score, 2)


def _calc_confidence(
    score: float | None,
) -> str:
    if score is None:
        return "LOW"

    if score >= 80:
        return "HIGH"

    if score >= 60:
        return "MEDIUM"

    return "LOW"


def _detect_pattern(
    score: float | None,
) -> str:
    if score is None:
        return "UNKNOWN"

    if score >= 85:
        return "MARKET_MAKER"

    if score >= 70:
        return "ACCUMULATION"

    if score >= 55:
        return "BALANCED"

    if score >= 40:
        return "ACTIVE"

    return "NOISE"
