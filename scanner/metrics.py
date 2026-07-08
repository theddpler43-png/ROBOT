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
    """
    Execution Ratio.

    100 = сделки исполняются по ценам, которые выглядят как реальные уровни стакана.
    0 = сделки далеко от видимой книги и выглядят хаотично.

    Логика:
    - точное совпадение с Top5 Bid/Ask = максимальный балл;
    - сделка внутри спреда рядом с Bid/Ask = средний балл;
    - сделка около Top5 диапазона = слабый балл;
    - всё остальное = 0.
    """
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

        nearest_distance = min(abs(trade_price - level) for level in visible_levels)

        if nearest_distance <= tick_tolerance:
            scores.append(1.0)
            continue

        if bid1 <= trade_price <= ask1:
            edge_distance = min(abs(trade_price - bid1), abs(trade_price - ask1))
            edge_score = 1.0 - min(1.0, edge_distance / max(spread, tick_tolerance))
            scores.append(0.45 + edge_score * 0.35)
            continue

        if low_book <= trade_price <= high_book:
            book_range = max(high_book - low_book, tick_tolerance)
            book_score = 1.0 - min(1.0, nearest_distance / book_range)
            scores.append(0.20 + book_score * 0.35)
            continue

        scores.append(0.0)

    if not scores:
        return None

    return round(statistics.mean(scores) * 100, 2)


def calc_uniformity(trades: list[dict]) -> float | None:
    """
    Uniformity.

    100 = большинство сделок имеет одинаковый или почти одинаковый размер.
    0 = размеры сделок хаотичные.

    Считаем по amount, а не по price * amount.
    Для поиска робота важнее повторяемость размера сделки.
    """
    sizes: list[float] = []

    for trade in trades:
        amount = safe_float(trade.get("amount"))

        if amount is not None and amount > 0:
            sizes.append(amount)

    if len(sizes) < 3:
        return None

    rounded_sizes = [_smart_round_size(size) for size in sizes]

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
    """
    Price Smoothness.

    100 = цена движется плавно, без хаотичных скачков.
    0 = цена резко прыгает между сделками.

    Пока метрика подготовлена, но не подключена к MarketRow.
    Подключим следующим коммитом через models.py и bitmart.py.
    """
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
