import { fetchMarkets } from "./api.js";
import {
    renderSummary,
    renderTable,
    sortMarkets,
    updateSortIndicators,
} from "./table.js";
import { numberValue } from "./utils.js";

const state = {
    markets: [],
    sortKey: "execution_ratio",
    sortDirection: "desc",
    isLoading: false,
};

const elements = {
    scanStatus: document.getElementById("scanStatus"),
    scanCount: document.getElementById("scanCount"),
    scanProgressBar: document.getElementById("scanProgressBar"),
    lastUpdate: document.getElementById("lastUpdate"),

    exchangeFilter: document.getElementById("exchangeFilter"),
    symbolFilter: document.getElementById("symbolFilter"),
    minExecutionFilter: document.getElementById("minExecutionFilter"),
    minUniformityFilter: document.getElementById("minUniformityFilter"),
    maxSpreadFilter: document.getElementById("maxSpreadFilter"),
    resetFiltersBtn: document.getElementById("resetFiltersBtn"),

    totalMarkets: document.getElementById("totalMarkets"),
    visibleMarkets: document.getElementById("visibleMarkets"),
    bestExecution: document.getElementById("bestExecution"),

    marketsBody: document.getElementById("marketsBody"),
};

async function loadMarkets() {
    if (state.isLoading) {
        return;
    }

    state.isLoading = true;

    try {
        const payload = await fetchMarkets();

        state.markets = payload.markets;

        updateProgress(payload);
        updateExchangeOptions();
        render();
    } catch (error) {
        elements.scanStatus.textContent = "Connection error";
        console.error("Failed to load markets:", error);
    } finally {
        state.isLoading = false;
    }
}

function updateProgress(payload) {
    const percent = payload.total > 0
        ? Math.min(100, Math.round((payload.count / payload.total) * 100))
        : 0;

    elements.scanStatus.textContent = payload.status;
    elements.scanCount.textContent = `${payload.count} / ${payload.total}`;
    elements.scanProgressBar.style.width = `${percent}%`;
    elements.lastUpdate.textContent = new Date().toLocaleTimeString();
}

function updateExchangeOptions() {
    const currentValue = elements.exchangeFilter.value;

    const exchanges = Array.from(
        new Set(state.markets.map((market) => market.exchange).filter(Boolean))
    ).sort();

    const existingValues = Array.from(elements.exchangeFilter.options)
        .map((option) => option.value);

    const nextValues = ["", ...exchanges];

    if (existingValues.join("|") === nextValues.join("|")) {
        return;
    }

    elements.exchangeFilter.innerHTML =
        `<option value="">All exchanges</option>`;

    exchanges.forEach((exchange) => {
        const option = document.createElement("option");
        option.value = exchange;
        option.textContent = exchange;
        elements.exchangeFilter.appendChild(option);
    });

    elements.exchangeFilter.value =
        exchanges.includes(currentValue) ? currentValue : "";
}

function getFilteredMarkets() {
    const exchange = elements.exchangeFilter.value;
    const symbol = elements.symbolFilter.value.trim().toUpperCase();

    const minExecution = numberValue(elements.minExecutionFilter.value);
    const minUniformity = numberValue(elements.minUniformityFilter.value);

    const maxSpreadRaw = elements.maxSpreadFilter.value;
    const maxSpread =
        maxSpreadRaw === "" ? null : numberValue(maxSpreadRaw);

    return state.markets.filter((market) => {
        if (exchange && market.exchange !== exchange) {
            return false;
        }

        if (symbol && !market.symbol.toUpperCase().includes(symbol)) {
            return false;
        }

        if (market.execution_ratio < minExecution) {
            return false;
        }

        if (market.uniformity < minUniformity) {
            return false;
        }

        if (maxSpread !== null && market.spread > maxSpread) {
            return false;
        }

        return true;
    });
}

function render() {
    const filteredMarkets = getFilteredMarkets();
    const sortedMarkets = sortMarkets(
        filteredMarkets,
        state.sortKey,
        state.sortDirection
    );

    renderSummary(elements, state.markets, filteredMarkets);
    renderTable(elements, sortedMarkets);
    updateSortIndicators(state.sortKey, state.sortDirection);
}

function setupEvents() {
    document.querySelectorAll("th[data-sort]").forEach((header) => {
        header.addEventListener("click", () => {
            const key = header.dataset.sort;

            if (state.sortKey === key) {
                state.sortDirection =
                    state.sortDirection === "asc" ? "desc" : "asc";
            } else {
                state.sortKey = key;
                state.sortDirection = "desc";
            }

            render();
        });
    });

    [
        elements.exchangeFilter,
        elements.symbolFilter,
        elements.minExecutionFilter,
        elements.minUniformityFilter,
        elements.maxSpreadFilter,
    ].forEach((element) => {
        element.addEventListener("input", render);
        element.addEventListener("change", render);
    });

    elements.resetFiltersBtn.addEventListener("click", () => {
        elements.exchangeFilter.value = "";
        elements.symbolFilter.value = "";
        elements.minExecutionFilter.value = "0";
        elements.minUniformityFilter.value = "0";
        elements.maxSpreadFilter.value = "";

        render();
    });
}

setupEvents();
loadMarkets();
setInterval(loadMarkets, 1000);
