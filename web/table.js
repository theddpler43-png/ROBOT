import {
    escapeHtml,
    formatNumber,
    formatPercent,
    formatPrice,
    metricClass,
    spreadClass,
} from "./utils.js";

export function sortMarkets(markets, sortKey, sortDirection) {
    return [...markets].sort((a, b) => {
        const left = a[sortKey];
        const right = b[sortKey];

        let result;

        if (typeof left === "string" || typeof right === "string") {
            result = String(left).localeCompare(String(right));
        } else {
            result = left - right;
        }

        return sortDirection === "asc" ? result : -result;
    });
}

export function renderSummary(elements, allMarkets, visibleMarkets) {
    elements.totalMarkets.textContent = allMarkets.length;
    elements.visibleMarkets.textContent = visibleMarkets.length;

    if (!visibleMarkets.length) {
        elements.bestExecution.textContent = "—";
        return;
    }

    const best = Math.max(
        ...visibleMarkets.map((market) => market.execution_ratio)
    );

    elements.bestExecution.textContent =
        `${formatPercent(best)}%`;
}

export function renderTable(elements, markets) {

    if (!markets.length) {
        elements.marketsBody.innerHTML = `
            <tr>
                <td colspan="9" class="empty-state">
                    No markets match current filters
                </td>
            </tr>
        `;
        return;
    }

    elements.marketsBody.innerHTML = markets.map((market) => `
        <tr>
            <td>${escapeHtml(market.exchange)}</td>

            <td class="symbol-cell">
                ${escapeHtml(market.symbol)}
            </td>

            <td class="number ${metricClass(market.execution_ratio)}">
                ${formatPercent(market.execution_ratio)}
            </td>

            <td class="number ${metricClass(market.uniformity)}">
                ${formatPercent(market.uniformity)}
            </td>

            <td class="number ${spreadClass(market.spread)}">
                ${formatPercent(market.spread)}
            </td>

            <td class="number">
                ${formatNumber(market.top5_bid)}
            </td>

            <td class="number">
                ${formatNumber(market.top5_ask)}
            </td>

            <td class="number">
                ${formatNumber(market.top5_total)}
            </td>

            <td class="number">
                ${formatPrice(market.price)}
            </td>

        </tr>
    `).join("");
}

export function updateSortIndicators(sortKey, sortDirection) {

    document
        .querySelectorAll("th[data-sort]")
        .forEach((header) => {

            const key = header.dataset.sort;

            const label =
                header.dataset.label ||
                header.textContent
                    .replace(" ▲", "")
                    .replace(" ▼", "");

            header.dataset.label = label;

            if (key === sortKey) {
                header.textContent =
                    `${label} ${sortDirection === "asc" ? "▲" : "▼"}`;
            } else {
                header.textContent = label;
            }

        });

}
