from __future__ import annotations


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


def detect_pattern(
    execution: float | None,
    uniformity: float | None,
    smoothness: float | None,
    score: float | None,
) -> str:
    """
    Определяет тип поведения рынка.

    Порядок правил имеет значение.
    Первое совпадение считается найденным паттерном.
    """

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
