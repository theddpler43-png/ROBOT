from __future__ import annotations

import aiohttp

from scanner.metrics import (
    calc_execution_pct,
    calc_market_score,
    calc_price_and_spread,
    calc_price_smoothness,
    calc_top5_depth,
    calc_uniformity,
)
from scanner.models import MarketRow


BASE_URL = "https://api-cloud.bitmart.com"


async def fetch_json(
    session: aiohttp.ClientSession,
    url: str,
    params: dict | None = None,
) -> dict:
    async with session.get(url, params=params, timeout=15) as response:
        response.raise_for_status()
        return await response.json()


async def fetch_symbols(session: aiohttp.ClientSession) -> list[str]:
    data = await fetch_json(
        session,
        f"{BASE_URL}/spot/v1/symbols/details",
    )

    symbols: list[str] = []

    for item in data.get("data", {}).get("symbols", []):
        symbol = item.get("symbol")
        trade_status = item.get("trade_status")

        if not symbol:
            continue

        if not symbol.endswith("_USDT"):
            continue

        if trade_status and str(trade_status).lower() not in {"trading", "1"}:
            continue

        symbols.append(symbol)

    return symbols


async def fetch_orderbook(
    session: aiohttp.ClientSession,
    symbol: str,
) -> dict:
    data = await fetch_json(
        session,
        f"{BASE_URL}/spot/quotation/v3/books",
        params={
            "symbol": symbol,
            "limit": 5,
        },
    )

    book = data.get("data") or {}

    return {
        "bids": [[item[0], item[1]] for item in book.get("bids", [])],
        "asks": [[item[0], item[1]] for item in book.get("asks", [])],
    }


async def fetch_trades(
    session: aiohttp.ClientSession,
    symbol: str,
    limit: int = 30,
) -> list[dict]:
    data = await fetch_json(
        session,
        f"{BASE_URL}/spot/quotation/v3/trades",
        params={
            "symbol": symbol,
            "limit": limit,
        },
    )

    rows = data.get("data") or []
    trades: list[dict] = []

    for row in rows:
        trades.append(
            {
                "price": row.get("price"),
                "amount": row.get("size"),
            }
        )

    return trades


async def scan_symbol(
    session: aiohttp.ClientSession,
    symbol: str,
    trade_limit: int = 30,
) -> MarketRow:
    try:
        orderbook = await fetch_orderbook(session, symbol)
        trades = await fetch_trades(session, symbol, trade_limit)

        price, _, _, spread = calc_price_and_spread(orderbook)
        top5_bid, top5_ask, top5_total = calc_top5_depth(orderbook)

        execution_ratio = calc_execution_pct(trades, orderbook)
        uniformity = calc_uniformity(trades)
        price_smoothness = calc_price_smoothness(trades)

        score = calc_market_score(
            execution_ratio,
            uniformity,
            price_smoothness,
        )

        return MarketRow(
            exchange="BitMart",
            symbol=symbol.replace("_", "/"),
            execution_ratio=execution_ratio,
            uniformity=uniformity,
            price_smoothness=price_smoothness,
            score=score,
            spread=spread,
            top5_bid=round(top5_bid, 2),
            top5_ask=round(top5_ask, 2),
            top5_total=round(top5_total, 2),
            price=price,
        )

    except Exception:
        return MarketRow(
            exchange="BitMart",
            symbol=symbol.replace("_", "/"),
            execution_ratio=None,
            uniformity=None,
            price_smoothness=None,
            score=None,
            spread=None,
            top5_bid=0.0,
            top5_ask=0.0,
            top5_total=0.0,
            price=None,
        )
