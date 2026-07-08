from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AnalysisResult:
    score: float | None
    confidence: str
    pattern: str


PATTERNS = [
    {
        "name": "MARKET_MAKER",
        "execution": 85,
        "uniformity": 80,
        "smoothness": 80,
        "score": 85,
    },
    {
        "name": "TREND",
        "execution": 75,
        "uniformity": 50,
        "smoothness": 70,
        "score": 70,
    },
    {
        "name": "LOW_ACTIVITY",
        "execution": 40,
        "uniformity": 40,
        "smoothness": 40,
        "score": 40,
    },
]


def analyze_market(
    execution: float | None,
    uniformity: float | None,
    smoothness: float | None,
) -> AnalysisResult:
    score = _calc_score(
        execution,
        uniformity,
        smoothness,
    )

    confidence = _calc_confidence(
        execution,
        uniformity,
        smoothness,
    )

    pattern = _detect_pattern(
        execution,
        uniformity,
        smoothness,
        score,
    )

    return AnalysisResult(
        score=score,
        confidence=confidence,
        pattern=pattern,
    )


def _calc_score(
    execution: float | None,
    uniformity: float | None,
    smoothness: float | None,
) -> float | None:
    if (
        execution is None
        or uniformity is None
        or smoothness is None
    ):
        return None

    base_score = _calc_base_score(
        execution,
        uniformity,
        smoothness,
    )

    final_score = _apply_penalties(
        base_score=base_score,
        execution=execution,
        uniformity=uniformity,
        smoothness=smoothness,
    )

    return round(
        max(0.0, min(final_score, 100.0)),
        2,
    )


def _calc_base_score(
    execution: float,
    uniformity: float,
    smoothness: float,
) -> float:
    return (
        execution * 0.45
        + uniformity * 0.30
        + smoothness * 0.25
    )


def _apply_penalties(
    base_score: float,
    execution: float,
    uniformity: float,
    smoothness: float,
) -> float:
    score = base_score

    if execution < 60:
        score *= 0.50

    if uniformity < 40:
        score *= 0.60

    if smoothness < 40:
        score *= 0.70

    return score


def _calc_confidence(
    execution: float | None,
    uniformity: float | None,
    smoothness: float | None,
) -> str:
    if (
        execution is None
        or uniformity is None
        or smoothness is None
    ):
        return "LOW"

    minimum = min(
        execution,
        uniformity,
        smoothness,
    )

    average = (
        execution
        + uniformity
        + smoothness
    ) / 3

    if minimum >= 80 and average >= 85:
        return "HIGH"

    if minimum >= 60 and average >= 70:
        return "MEDIUM"

    return "LOW"


def _detect_pattern(
    execution: float | None,
    uniformity: float | None,
    smoothness: float | None,
    score: float | None,
) -> str:
    if (
        execution is None
        or uniformity is None
        or smoothness is None
        or score is None
    ):
        return "UNKNOWN"

    for pattern in PATTERNS:
        if (
            execution >= pattern["execution"]
            and uniformity >= pattern["uniformity"]
            and smoothness >= pattern["smoothness"]
            and score >= pattern["score"]
        ):
            return pattern["name"]

    return "UNKNOWN"
