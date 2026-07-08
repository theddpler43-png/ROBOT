from dataclasses import asdict, dataclass


@dataclass(slots=True)
class MarketRow:
    exchange: str
    symbol: str

    execution_ratio: float | None
    uniformity: float | None

    spread: float | None

    top5_bid: float
    top5_ask: float
    top5_total: float

    price: float | None

    price_smoothness: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)
