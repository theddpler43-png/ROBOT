from __future__ import annotations

import math
import statistics


def safe_float(value) -> float | None:
    try:
        if value is None:
            return None

        number = float(value)

        if not math.isfinite(number):
            return None

        return number

    except Exception:
        return None


def calc_price_and_spread(
    orderbook: dict,
) -> tuple[float | None, float | None, float | None, float | None]:
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

    bids = _prices_from_levels(orderbook.get("bids") or [])
    asks = _prices_from_levels(orderbook.get("asks") or [])

    if not bids or not asks:
        return None

    bid1 = bids[0]
    ask1 = asks[0]

    if bid1 <= 0 or ask1 <= 0 or ask1 < bid1:
        return None

    mid = (bid1 + ask1) / 2
    spread = ask1 - bid1
    tick_tolerance = _estimate_tick_tolerance(bids, asks, mid)

    scores: list[float] = []

    visible_levels = bids[:5] + asks[:5]
    low_book = min(visible_levels)
    high_book = max(visible_levels)

    for trade in trades:
        trade_price = safe_float(trade.get("price"))

        if trade_price is None or trade_price <= 0:
            continue

        nearest_distance = min(
            abs(trade_price - level)
            for level in visible_levels
        )

        if nearest_distance <= tick_tolerance:
            scores.append(1.0)
            continue

        if bid1 <= trade_price <= ask1:
            edge_distance = min(
                abs(trade_price - bid1),
                abs(trade_price - ask1),
            )

            edge_score = 1.0 - min(
                1.0,
                edge_distance / max(spread, tick_tolerance),
            )

            scores.append(0.45 + edge_score * 0.35)
            continue

        if low_book <= trade_price <= high_book:
            book_range = max(
                high_book - low_book,
                tick_tolerance,
            )

            book_score = 1.0 - min(
                1.0,
                nearest_distance / book_range,
            )

            scores.append(0.20 + book_score * 0.35)
            continue

        scores.append(0.0)

    if not scores:
        return None

    return round(statistics.mean(scores) * 100, 2)


def calc_uniformity(trades: list[dict]) -> float | None:
    sizes: list[float] = []

    for trade in trades:
        amount = safe_float(trade.get("amount"))

        if amount is not None and amount > 0:
            sizes.append(amount)

    if len(sizes) < 3:
        return None

    rounded_sizes = [
        _smart_round_size(size)
        for size in sizes
    ]

    most_common_count = 0

    for size in set(rounded_sizes):
        most_common_count = max(
            most_common_count,
            rounded_sizes.count(size),
        )

    repeat_score = most_common_count / len(rounded_sizes)

    mean = statistics.mean(sizes)

    if mean <= 0:
        return None

    stdev = statistics.pstdev(sizes)
    cv = stdev / mean

    stability_score = 1.0 / (1.0 + cv * 3.0)

    score = repeat_score * 70.0 + stability_score * 30.0

    return round(max(0.0, min(100.0, score)), 2)


def calc_price_smoothness(trades: list[dict]) -> float | None:
    prices: list[float] = []

    for trade in trades:
        price = safe_float(trade.get("price"))

        if price is not None and price > 0:
            prices.append(price)

    if len(prices) < 4:
        return None

    changes: list[float] = []

    for previous, current in zip(prices, prices[1:]):
        if previous <= 0:
            continue

        changes.append(abs(current - previous) / previous)

    if len(changes) < 3:
        return None

    mean_change = statistics.mean(changes)

    if mean_change <= 0:
        return 100.0

    stdev_change = statistics.pstdev(changes)
    jump_ratio = stdev_change / mean_change

    score = 100.0 / (1.0 + jump_ratio * 2.5)

    return round(max(0.0, min(100.0, score)), 2)


def calc_execution_rhythm(trades: list[dict]) -> float | None:
    """
    Execution Rhythm.

    Оценивает, насколько сделки идут ритмично.

    Использует:
    - timestamp;
    - side.

    100 = сделки идут с регулярными интервалами
          и повторяемым buy/sell паттерном.

    0 = интервалы и стороны сделок хаотичны.
    """
    prepared = _prepare_trades_with_time_and_side(trades)

    if len(prepared) < 5:
        return None

    intervals = _trade_intervals(prepared)

    if len(intervals) < 4:
        return None

    interval_score = _interval_stability_score(intervals)
    side_score = _side_sequence_score(prepared)

    score = (
        interval_score * 0.70
        + side_score * 0.30
    )

    return round(max(0.0, min(100.0, score)), 2)


def _prepare_trades_with_time_and_side(
    trades: list[dict],
) -> list[dict]:
    prepared: list[dict] = []

    for trade in trades:
        timestamp = safe_float(trade.get("timestamp"))
        side = str(trade.get("side") or "").lower()

        if timestamp is None:
            continue

        if side not in {"buy", "sell"}:
            continue

        prepared.append(
            {
                "timestamp": timestamp,
                "side": side,
            }
        )

    prepared.sort(
        key=lambda item: item["timestamp"]
    )

    return prepared


def _trade_intervals(
    trades: list[dict],
) -> list[float]:
    intervals: list[float] = []

    for previous, current in zip(trades, trades[1:]):
        interval = current["timestamp"] - previous["timestamp"]

        if interval > 0:
            intervals.append(interval)

    return intervals


def _interval_stability_score(
    intervals: list[float],
) -> float:
    if len(intervals) < 2:
        return 0.0

    mean = statistics.mean(intervals)

    if mean <= 0:
        return 0.0

    stdev = statistics.pstdev(intervals)
    cv = stdev / mean

    return 100.0 / (1.0 + cv * 4.0)


def _side_sequence_score(
    trades: list[dict],
) -> float:
    sides = [
        trade["side"]
        for trade in trades
    ]

    if len(sides) < 4:
        return 0.0

    same_side_score = _same_side_streak_score(sides)
    alternating_score = _alternating_side_score(sides)

    return max(
        same_side_score,
        alternating_score,
    )


def _same_side_streak_score(
    sides: list[str],
) -> float:
    longest = 1
    current = 1

    for previous, side in zip(sides, sides[1:]):
        if side == previous:
            current += 1
        else:
            longest = max(longest, current)
            current = 1

    longest = max(longest, current)

    return min(
        100.0,
        longest / len(sides) * 100.0,
    )


def _alternating_side_score(
    sides: list[str],
) -> float:
    if len(sides) < 2:
        return 0.0

    switches = 0

    for previous, side in zip(sides, sides[1:]):
        if side != previous:
            switches += 1

    return switches / (len(sides) - 1) * 100.0


def _prices_from_levels(levels: list) -> list[float]:
    prices: list[float] = []

    for level in levels:
        if not level:
            continue

        price = safe_float(level[0])

        if price is not None and price > 0:
            prices.append(price)

    return prices


def _estimate_tick_tolerance(
    bids: list[float],
    asks: list[float],
    mid: float,
) -> float:
    diffs: list[float] = []

    for levels in (bids, asks):
        for left, right in zip(levels, levels[1:]):
            diff = abs(left - right)

            if diff > 0:
                diffs.append(diff)

    if diffs:
        return max(min(diffs), mid * 0.000001)

    return mid * 0.000001


def _smart_round_size(size: float) -> float:
    if size >= 100:
        return round(size, 0)

    if size >= 10:
        return round(size, 1)

    if size >= 1:
        return round(size, 2)

    if size >= 0.01:
        return round(size, 4)

    return round(size, 8)
