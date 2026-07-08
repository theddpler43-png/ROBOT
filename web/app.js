import { fetchMarkets } from "./api.js";
import {
    renderSummary,
    renderTable,
    sortMarkets,
    updateSortIndicators,
} from "./table.js";

import {
    getFilteredMarkets,
    resetFilters,
    updateExchangeOptions,
} from "./filters.js";

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
        updateExchangeOptions(state.markets, elements);
        render();

    } catch (error) {

        console.error(error);

        elements.scanStatus.textContent = "Connection error";

    } finally {

        state.isLoading = false;

    }
}

function updateProgress(payload) {

    const percent =
        payload.total > 0
            ? Math.min(
                  100,
                  Math.round(payload.count / payload.total * 100)
              )
            : 0;

    elements.scanStatus.textContent = payload.status;

    elements.scanCount.textContent =
        `${payload.count} / ${payload.total}`;

    elements.scanProgressBar.style.width =
        `${percent}%`;

    elements.lastUpdate.textContent =
        new Date().toLocaleTimeString();
}

function render() {

    const filteredMarkets =
        getFilteredMarkets(
            state.markets,
            elements
        );

    const sortedMarkets =
        sortMarkets(
            filteredMarkets,
            state.sortKey,
            state.sortDirection
        );

    renderSummary(
        elements,
        state.markets,
        filteredMarkets
    );

    renderTable(
        elements,
        sortedMarkets
    );

    updateSortIndicators(
        state.sortKey,
        state.sortDirection
    );
}

function setupSorting() {

    document
        .querySelectorAll("th[data-sort]")
        .forEach((header) => {

            header.addEventListener("click", () => {

                const key =
                    header.dataset.sort;

                if (
                    state.sortKey === key
                ) {

                    state.sortDirection =
                        state.sortDirection === "asc"
                            ? "desc"
                            : "asc";

                } else {

                    state.sortKey = key;
                    state.sortDirection = "desc";

                }

                render();

            });

        });

}

function setupFilters() {

    [
        elements.exchangeFilter,
        elements.symbolFilter,
        elements.minExecutionFilter,
        elements.minUniformityFilter,
        elements.maxSpreadFilter,
    ].forEach((element) => {

        element.addEventListener(
            "input",
            render
        );

        element.addEventListener(
            "change",
            render
        );

    });

    elements.resetFiltersBtn.addEventListener(
        "click",
        () => {

            resetFilters(elements);

            render();

        }
    );

}

setupSorting();
setupFilters();

loadMarkets();

setInterval(loadMarkets, 1000);
