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
        "rhythm": 75,
        "score": 85,
    },
    {
        "name": "TREND",
        "execution": 75,
        "uniformity": 50,
        "smoothness": 70,
        "rhythm": 50,
        "score": 70,
    },
    {
        "name": "LOW_ACTIVITY",
        "execution": 40,
        "uniformity": 40,
        "smoothness": 40,
        "rhythm": 30,
        "score": 40,
    },
]


def analyze_market(
    execution: float | None,
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

    confidence = _calc_confidence(
        execution,
        uniformity,
        smoothness,
        execution_rhythm,
    )

    pattern = _detect_pattern(
        execution,
        uniformity,
        smoothness,
        execution_rhythm,
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
    execution_rhythm: float | None,
) -> float | None:
    if (
        execution is None
        or uniformity is None
        or smoothness is None
    ):
        return None

    rhythm = execution_rhythm if execution_rhythm is not None else 50.0

    score = (
        execution * 0.40
        + uniformity * 0.25
        + smoothness * 0.20
        + rhythm * 0.15
    )

    if execution < 60:
        score *= 0.50

    if uniformity < 40:
        score *= 0.60

    if smoothness < 40:
        score *= 0.70

    if rhythm < 40:
        score *= 0.85

    return round(max(0.0, min(score, 100.0)), 2)


def _calc_confidence(
    execution: float | None,
    uniformity: float | None,
    smoothness: float | None,
    execution_rhythm: float | None,
) -> str:
    if (
        execution is None
        or uniformity is None
        or smoothness is None
    ):
        return "LOW"

    rhythm = execution_rhythm if execution_rhythm is not None else 50.0

    minimum = min(
        execution,
        uniformity,
        smoothness,
        rhythm,
    )

    average = (
        execution
        + uniformity
        + smoothness
        + rhythm
    ) / 4

    if minimum >= 75 and average >= 82:
        return "HIGH"

    if minimum >= 55 and average >= 68:
        return "MEDIUM"

    return "LOW"


def _detect_pattern(
    execution: float | None,
    uniformity: float | None,
    smoothness: float | None,
    execution_rhythm: float | None,
    score: float | None,
) -> str:
    if (
        execution is None
        or uniformity is None
        or smoothness is None
        or score is None
    ):
        return "UNKNOWN"

    rhythm = execution_rhythm if execution_rhythm is not None else 50.0

    for pattern in PATTERNS:
        if (
            execution >= pattern["execution"]
            and uniformity >= pattern["uniformity"]
            and smoothness >= pattern["smoothness"]
            and rhythm >= pattern["rhythm"]
            and score >= pattern["score"]
        ):
            return pattern["name"]

    return "UNKNOWN"
