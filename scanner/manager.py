from __future__ import annotations

import asyncio
import json
import os
import time

import aiohttp

from scanner.bitmart import fetch_symbols, scan_symbol

ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(ROOT, "data", "markets.json")
CONFIG_FILE = os.path.join(ROOT, "config.json")


def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(markets: list[dict], total: int, status: str) -> None:
    payload = {
        "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "count": len(markets),
        "total": total,
        "markets": markets,
    }

    temp_file = DATA_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    os.replace(temp_file, DATA_FILE)


async def run_scan():
    config = load_config()
    scanner_config = config.get("scanner", {})

    trade_limit = int(scanner_config.get("trade_limit", 30))
    concurrency = int(scanner_config.get("concurrency", 10))
    dev_symbol_limit = scanner_config.get("dev_symbol_limit")

    async with aiohttp.ClientSession() as session:
        print("Получение списка пар BitMart...")

        symbols = await fetch_symbols(session)

        if dev_symbol_limit:
            symbols = symbols[: int(dev_symbol_limit)]

        total = len(symbols)

        print(f"К проверке: {total} USDT пар")

        markets: list[dict] = []
        semaphore = asyncio.Semaphore(concurrency)

        save(markets, total, "running")

        async def worker(symbol: str):
            async with semaphore:
                row = await scan_symbol(session, symbol, trade_limit)
                markets.append(row.to_dict())

                if len(markets) % 5 == 0:
                    save(markets, total, "running")
                    print(f"{len(markets)}/{total}")

        await asyncio.gather(*(worker(symbol) for symbol in symbols))

        save(markets, total, "complete")
        print(f"Scan complete: {len(markets)}/{total}")
