const state = {
    markets: [],
    sortKey: "execution_ratio",
    sortDirection: "desc",
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
    try {
        const response = await fetch("/markets", { cache: "no-store" });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const payload = await response.json();

        state.markets = normalizeMarkets(payload.markets || []);
        updateProgress(payload);
        updateExchangeOptions();
        render();
    } catch (error) {
        elements.scanStatus.textContent = "Connection error";
        console.error("Failed to load markets:", error);
    }
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
        price: numberValue(market.price),
    }));
}

function numberValue(value) {
    const number = Number(value);
    return Number.isFinite(number) ? number : 0;
}

function updateProgress(payload) {
    const count = numberValue(payload.count);
    const total = numberValue(payload.total);
    const status = payload.status || "Running";

    const percent = total > 0 ? Math.min(100, Math.round((count / total) * 100)) : 0;

    elements.scanStatus.textContent = status;
    elements.scanCount.textContent = `${count} / ${total}`;
    elements.scanProgressBar.style.width = `${percent}%`;
    elements.lastUpdate.textContent = new Date().toLocaleTimeString();
}

function updateExchangeOptions() {
    const currentValue = elements.exchangeFilter.value;
    const exchanges = Array.from(
        new Set(state.markets.map((market) => market.exchange).filter(Boolean))
    ).sort();

    const existingValues = Array.from(elements.exchangeFilter.options).map((option) => option.value);
    const nextValues = ["", ...exchanges];

    if (existingValues.join("|") === nextValues.join("|")) {
        return;
    }

    elements.exchangeFilter.innerHTML = `<option value="">All exchanges</option>`;

    exchanges.forEach((exchange) => {
        const option = document.createElement("option");
        option.value = exchange;
        option.textContent = exchange;
        elements.exchangeFilter.appendChild(option);
    });

    elements.exchangeFilter.value = exchanges.includes(currentValue) ? currentValue : "";
}

function getFilteredMarkets() {
    const exchange = elements.exchangeFilter.value;
    const symbol = elements.symbolFilter.value.trim().toUpperCase();
    const minExecution = numberValue(elements.minExecutionFilter.value);
    const minUniformity = numberValue(elements.minUniformityFilter.value);
    const maxSpreadRaw = elements.maxSpreadFilter.value;
    const maxSpread = maxSpreadRaw === "" ? null : numberValue(maxSpreadRaw);

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

function sortMarkets(markets) {
    return [...markets].sort((a, b) => {
        const left = a[state.sortKey];
        const right = b[state.sortKey];

        let result;

        if (typeof left === "string" || typeof right === "string") {
            result = String(left).localeCompare(String(right));
        } else {
            result = left - right;
        }

        return state.sortDirection === "asc" ? result : -result;
    });
}

function render() {
    const filteredMarkets = getFilteredMarkets();
    const sortedMarkets = sortMarkets(filteredMarkets);

    updateSummary(filteredMarkets);
    renderTable(sortedMarkets);
    updateSortIndicators();
}

function updateSummary(filteredMarkets) {
    elements.totalMarkets.textContent = state.markets.length;
    elements.visibleMarkets.textContent = filteredMarkets.length;

    if (!filteredMarkets.length) {
        elements.bestExecution.textContent = "—";
        return;
    }

    const best = Math.max(...filteredMarkets.map((market) => market.execution_ratio));
    elements.bestExecution.textContent = `${formatPercent(best)}%`;
}

function renderTable(markets) {
    if (!markets.length) {
        elements.marketsBody.innerHTML = `
            <tr>
                <td colspan="9" class="empty-state">No markets match current filters</td>
            </tr>
        `;
        return;
    }

    elements.marketsBody.innerHTML = markets.map((market) => `
        <tr>
            <td>${escapeHtml(market.exchange)}</td>
            <td class="symbol-cell">${escapeHtml(market.symbol)}</td>
            <td class="number ${metricClass(market.execution_ratio)}">${formatPercent(market.execution_ratio)}</td>
            <td class="number ${metricClass(market.uniformity)}">${formatPercent(market.uniformity)}</td>
            <td class="number ${spreadClass(market.spread)}">${formatPercent(market.spread)}</td>
            <td class="number">${formatNumber(market.top5_bid)}</td>
            <td class="number">${formatNumber(market.top5_ask)}</td>
            <td class="number">${formatNumber(market.top5_total)}</td>
            <td class="number">${formatPrice(market.price)}</td>
        </tr>
    `).join("");
}

function updateSortIndicators() {
    document.querySelectorAll("th[data-sort]").forEach((header) => {
        const key = header.dataset.sort;
        const label = header.dataset.label || header.textContent.replace(" ▲", "").replace(" ▼", "");

        header.dataset.label = label;

        if (key === state.sortKey) {
            header.textContent = `${label} ${state.sortDirection === "asc" ? "▲" : "▼"}`;
        } else {
            header.textContent = label;
        }
    });
}

function metricClass(value) {
    if (value >= 80) {
        return "metric-good";
    }

    if (value >= 50) {
        return "metric-mid";
    }

    return "metric-bad";
}

function spreadClass(value) {
    if (value <= 0.05) {
        return "metric-good";
    }

    if (value <= 0.2) {
        return "metric-mid";
    }

    return "metric-bad";
}

function formatPercent(value) {
    return numberValue(value).toFixed(2);
}

function formatNumber(value) {
    return numberValue(value).toLocaleString("en-US", {
        maximumFractionDigits: 2,
    });
}

function formatPrice(value) {
    const number = numberValue(value);

    if (number === 0) {
        return "0";
    }

    if (number < 0.0001) {
        return number.toFixed(10);
    }

    if (number < 1) {
        return number.toFixed(6);
    }

    return number.toLocaleString("en-US", {
        maximumFractionDigits: 4,
    });
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function setupEvents() {
    document.querySelectorAll("th[data-sort]").forEach((header) => {
        header.addEventListener("click", () => {
            const key = header.dataset.sort;

            if (state.sortKey === key) {
                state.sortDirection = state.sortDirection === "asc" ? "desc" : "asc";
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
