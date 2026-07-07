from __future__ import annotations

import asyncio
import json
import os

import aiohttp

from scanner.bitmart import fetch_symbols, scan_symbol

ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(ROOT, "data", "markets.json")


async def run_scan():

    async with aiohttp.ClientSession() as session:

        print("Получение списка пар BitMart...")

        symbols = await fetch_symbols(session)

        print(f"Найдено {len(symbols)} USDT пар")

        markets = []

        semaphore = asyncio.Semaphore(10)

        async def worker(symbol):

            async with semaphore:
                row = await scan_symbol(session, symbol)

                markets.append(row.to_dict())

                if len(markets) % 25 == 0:

                    save(markets)

                    print(f"{len(markets)}/{len(symbols)}")

        await asyncio.gather(
            *(worker(symbol) for symbol in symbols)
        )

        save(markets)


def save(markets):

    with open(DATA_FILE, "w", encoding="utf-8") as f:

        json.dump(
            {
                "count": len(markets),
                "markets": markets
            },
            f,
            indent=2,
            ensure_ascii=False
        )
