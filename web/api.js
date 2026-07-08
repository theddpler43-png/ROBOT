import { numberValue } from "./utils.js";

export async function fetchMarkets() {
    const response = await fetch("/markets", {
        cache: "no-store"
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    const payload = await response.json();

    return {
        status: payload.status || "Running",
        count: numberValue(payload.count),
        total: numberValue(payload.total),
        markets: normalizeMarkets(payload.markets || [])
    };
}

function normalizeMarkets(markets) {
    return markets.map((market) => ({
        exchange: market.exchange || "",
        symbol: market.symbol || "",

        execution_ratio: numberValue(market.execution_ratio),
        uniformity: numberValue(market.uniformity),

        spread: numberValue(market.spread),

        top5_bid: numberValue(market.top5_bid),
        top5_ask: numberValue(market.top5_ask),
        top5_total: numberValue(market.top5_total),

        price: numberValue(market.price)
    }));
}
