from dataclasses import asdict, dataclass


@dataclass(slots=True)
class MarketRow:
    exchange: str
    symbol: str

    # Основные метрики
    execution_ratio: float | None
    uniformity: float | None
    price_smoothness: float | None

    # Итоговая оценка рынка
    score: float | None
    confidence: str

    # Рыночные данные
    spread: float | None

    top5_bid: float
    top5_ask: float
    top5_total: float

    price: float | None

    def to_dict(self) -> dict:
        return asdict(self)
