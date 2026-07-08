import { COLUMNS } from "./columns.js";
import {
    escapeHtml,
    formatNumber,
    formatPercent,
    formatPrice,
    metricClass,
    spreadClass,
} from "./utils.js";

let headerInitialized = false;

export function initializeTable() {
    if (headerInitialized) {
        return;
    }

    const head = document.getElementById("marketsHead");

    const row = document.createElement("tr");

    for (const column of COLUMNS) {

        const th = document.createElement("th");

        th.textContent = column.title;

        if (column.sortable) {
            th.dataset.sort = column.key;
        }

        row.appendChild(th);

    }

    head.innerHTML = "";
    head.appendChild(row);

    headerInitialized = true;
}

export function sortMarkets(
    markets,
    sortKey,
    direction,
) {
    return [...markets].sort((a, b) => {

        const left = a[sortKey];
        const right = b[sortKey];

        if (
            typeof left === "string" ||
            typeof right === "string"
        ) {

            const result = String(left).localeCompare(
                String(right)
            );

            return direction === "asc"
                ? result
                : -result;
        }

        const result =
            Number(left ?? -999999) -
            Number(right ?? -999999);

        return direction === "asc"
            ? result
            : -result;

    });
}

export function renderSummary(
    elements,
    allMarkets,
    visibleMarkets,
) {
    elements.totalMarkets.textContent =
        allMarkets.length;

    elements.visibleMarkets.textContent =
        visibleMarkets.length;

    if (!visibleMarkets.length) {
        elements.bestExecution.textContent = "—";
        return;
    }

    const best = Math.max(
        ...visibleMarkets.map(
            m => Number(m.score ?? 0)
        )
    );

    elements.bestExecution.textContent =
        best.toFixed(2);
}

export function renderTable(
    elements,
    markets,
) {

    if (!markets.length) {

        elements.marketsBody.innerHTML = `
<tr>
<td colspan="${COLUMNS.length}" class="empty-state">
No markets match current filters
</td>
</tr>
`;

        return;
    }

    elements.marketsBody.innerHTML =
        markets
            .map(renderRow)
            .join("");
}

function renderRow(market) {

    const cells = COLUMNS
        .map(column => {

            const value =
                market[column.key];

            return `<td class="${cellClass(column, value)}">
${formatValue(column, value)}
</td>`;

        })
        .join("");

    return `<tr>${cells}</tr>`;
}

function formatValue(
    column,
    value,
) {

    switch (column.type) {

        case "metric":
            return `${formatPercent(value)}`;

        case "spread":
            return `${formatPercent(value)}`;

        case "price":
            return formatPrice(value);

        case "number":
            return formatNumber(value);

        case "score":
            return value == null
                ? "—"
                : Number(value).toFixed(2);

        case "confidence":
            return escapeHtml(
                value ?? "LOW"
            );

        case "symbol":
            return escapeHtml(
                value ?? ""
            );

        default:
            return escapeHtml(
                value ?? ""
            );
    }

}

function cellClass(
    column,
    value,
) {

    switch (column.type) {

        case "metric":
            return `number ${metricClass(value)}`;

        case "spread":
            return `number ${spreadClass(value)}`;

        case "number":
        case "price":
        case "score":
            return "number";

        case "symbol":
            return "symbol-cell";

        default:
            return "";
    }

}

export function updateSortIndicators(
    sortKey,
    direction,
) {

    document
        .querySelectorAll("th[data-sort]")
        .forEach(th => {

            const key =
                th.dataset.sort;

            const label =
                th.dataset.label ||
                th.textContent
                    .replace(" ▲", "")
                    .replace(" ▼", "");

            th.dataset.label = label;

            if (key === sortKey) {

                th.textContent =
                    `${label} ${
                        direction === "asc"
                            ? "▲"
                            : "▼"
                    }`;

            } else {

                th.textContent = label;

            }

        });

}
