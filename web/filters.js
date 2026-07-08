import { numberValue } from "./utils.js";

export function getFilteredMarkets(markets, elements) {
    const exchange = elements.exchangeFilter.value;
    const symbol = elements.symbolFilter.value.trim().toUpperCase();

    const minExecution = numberValue(elements.minExecutionFilter.value);
    const minUniformity = numberValue(elements.minUniformityFilter.value);

    const maxSpreadRaw = elements.maxSpreadFilter.value;
    const maxSpread =
        maxSpreadRaw === ""
            ? null
            : numberValue(maxSpreadRaw);

    return markets.filter((market) => {

        if (
            exchange &&
            market.exchange !== exchange
        ) {
            return false;
        }

        if (
            symbol &&
            !market.symbol
                .toUpperCase()
                .includes(symbol)
        ) {
            return false;
        }

        if (
            market.execution_ratio < minExecution
        ) {
            return false;
        }

        if (
            market.uniformity < minUniformity
        ) {
            return false;
        }

        if (
            maxSpread !== null &&
            market.spread > maxSpread
        ) {
            return false;
        }

        return true;
    });
}

export function resetFilters(elements) {

    elements.exchangeFilter.value = "";
    elements.symbolFilter.value = "";

    elements.minExecutionFilter.value = "0";
    elements.minUniformityFilter.value = "0";

    elements.maxSpreadFilter.value = "";

}

export function updateExchangeOptions(markets, elements) {

    const currentValue =
        elements.exchangeFilter.value;

    const exchanges = Array.from(
        new Set(
            markets
                .map((m) => m.exchange)
                .filter(Boolean)
        )
    ).sort();

    const current = Array.from(
        elements.exchangeFilter.options
    ).map((o) => o.value);

    const next = [
        "",
        ...exchanges
    ];

    if (
        current.join("|") === next.join("|")
    ) {
        return;
    }

    elements.exchangeFilter.innerHTML =
        `<option value="">All exchanges</option>`;

    exchanges.forEach((exchange) => {

        const option =
            document.createElement("option");

        option.value = exchange;
        option.textContent = exchange;

        elements.exchangeFilter.appendChild(option);

    });

    elements.exchangeFilter.value =
        exchanges.includes(currentValue)
            ? currentValue
            : "";

}
