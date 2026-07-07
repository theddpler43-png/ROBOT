from __future__ import annotations

import statistics


def safe_float(value) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def calc_price_and_spread(orderbook: dict) -> tuple[float | None, float | None, float | None, float | None]:
    bids = orderbook.get("bids") or []
    asks = orderbook.get("asks") or []

    if not bids or not asks:
        return None, None, None, None

    bid1 = safe_float(bids[0][0])
    ask1 = safe_float(asks[0][0])

    if not bid1 or not ask1:
        return None, bid1, ask1, None

    price = (bid1 + ask1) / 2
    spread_pct = ((ask1 - bid1) / price) * 100 if price else None

    return price, bid1, ask1, spread_pct


def calc_top5_depth(orderbook: dict) -> tuple[float, float, float]:
    bids = orderbook.get("bids") or []
    asks = orderbook.get("asks") or []

    bid_usdt = 0.0
    ask_usdt = 0.0

    for price, amount in bids[:5]:
        p = safe_float(price) or 0.0
        a = safe_float(amount) or 0.0
        bid_usdt += p * a

    for price, amount in asks[:5]:
        p = safe_float(price) or 0.0
        a = safe_float(amount) or 0.0
        ask_usdt += p * a

    return bid_usdt, ask_usdt, bid_usdt + ask_usdt


def calc_execution_pct(trades: list[dict], orderbook: dict) -> float | None:
    if not trades:
        return None

    bids = orderbook.get("bids") or []
    asks = orderbook.get("asks") or []

    levels = set()

    for price, _amount in bids[:5]:
        p = safe_float(price)
        if p is not None:
            levels.add(round(p, 12))

    for price, _amount in asks[:5]:
        p = safe_float(price)
        if p is not None:
            levels.add(round(p, 12))

    if not levels:
        return None

    matched = 0

    for trade in trades:
        price = safe_float(trade.get("price"))
        if price is None:
            continue

        if round(price, 12) in levels:
            matched += 1

    return round((matched / len(trades)) * 100, 2)


def calc_uniformity(trades: list[dict]) -> float | None:
    """
    100 = сделки по размеру очень похожи.
    0 = размеры сделок хаотичные.
    """
    sizes = []

    for trade in trades:
        price = safe_float(trade.get("price"))
        amount = safe_float(trade.get("amount"))

        if price and amount:
            sizes.append(price * amount)

    if len(sizes) < 3:
        return None

    mean = statistics.mean(sizes)
    if mean <= 0:
        return None

    stdev = statistics.pstdev(sizes)
    cv = stdev / mean

    score = max(0.0, min(100.0, 100.0 * (1.0 - cv)))
    return round(score, 2)
