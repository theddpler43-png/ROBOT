from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class MarketRow:
    exchange: str
    symbol: str
    price: float | None
    bid1: float | None
    ask1: float | None
    spread_pct: float | None
    top5_bid_usdt: float
    top5_ask_usdt: float
    top5_total_usdt: float
    execution_pct: float | None
    uniformity: float | None
    trades_count: int
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
