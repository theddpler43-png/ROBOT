from __future__ import annotations

import asyncio
import json

import aiohttp


BASE_URL = "https://api-cloud.bitmart.com"


async def main() -> None:
    symbol = "BTC_USDT"

    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}/spot/quotation/v3/trades"

        async with session.get(
            url,
            params={
                "symbol": symbol,
                "limit": 10,
            },
            timeout=15,
        ) as response:
            response.raise_for_status()
            data = await response.json()

    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
