from __future__ import annotations

import aiohttp

from scanner.metrics import (
    calc_execution_pct,
    calc_price_and_spread,
    calc_top5_depth,
    calc_uniformity,
)
from scanner.models import MarketRow


BASE_URL = "https://api-cloud.bitmart.com"


async def fetch_json(session: aiohttp.ClientSession, url: str, params: dict | None = None) -> dict:
    async with session.get(url, params=params, timeout=15) as response:
        response.raise_for_status()
        return await response.json()


async def fetch_symbols(session: aiohttp.ClientSession) -> list[str]:
    data = await fetch_json(session, f"{BASE_URL}/spot/v1/symbols/details")
    symbols = []

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


async def fetch_orderbook(session: aiohttp.ClientSession, symbol: str) -> dict:
    data = await fetch_json(
        session,
        f"{BASE_URL}/spot/quotation/v3/books",
        params={"symbol": symbol, "limit": 5},
    )

    book = data.get("data") or {}

    return {
        "bids": [[x[0], x[1]] for x in book.get("bids", [])],
        "asks": [[x[0], x[1]] for x in book.get("asks", [])],
    }


async def fetch_trades(session: aiohttp.ClientSession, symbol: str, limit: int = 30) -> list[dict]:
    data = await fetch_json(
        session,
        f"{BASE_URL}/spot/quotation/v3/trades",
        params={"symbol": symbol, "limit": limit},
    )

    rows = data.get("data") or []
    trades = []

    for row in rows:
        trades.append(
            {
                "price": row.get("price"),
                "amount": row.get("size"),
            }
        )

    return trades


async def scan_symbol(session: aiohttp.ClientSession, symbol: str, trade_limit: int = 30) -> MarketRow:
    try:
        orderbook = await fetch_orderbook(session, symbol)
        trades = await fetch_trades(session, symbol, trade_limit)

        price, bid1, ask1, spread_pct = calc_price_and_spread(orderbook)
        top5_bid, top5_ask, top5_total = calc_top5_depth(orderbook)
        execution = calc_execution_pct(trades, orderbook)
        uniformity = calc_uniformity(trades)

        return MarketRow(
            exchange="BitMart",
            symbol=symbol.replace("_", "/"),
            price=price,
            bid1=bid1,
            ask1=ask1,
            spread_pct=spread_pct,
            top5_bid_usdt=round(top5_bid, 2),
            top5_ask_usdt=round(top5_ask, 2),
            top5_total_usdt=round(top5_total, 2),
            execution_pct=execution,
            uniformity=uniformity,
            trades_count=len(trades),
        )

    except Exception as e:
        return MarketRow(
            exchange="BitMart",
            symbol=symbol.replace("_", "/"),
            price=None,
            bid1=None,
            ask1=None,
            spread_pct=None,
            top5_bid_usdt=0.0,
            top5_ask_usdt=0.0,
            top5_total_usdt=0.0,
            execution_pct=None,
            uniformity=None,
            trades_count=0,
            error=str(e),
        )
