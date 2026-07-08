export function numberValue(value) {
    const number = Number(value);
    return Number.isFinite(number) ? number : 0;
}

export function formatPercent(value) {
    return numberValue(value).toFixed(2);
}

export function formatNumber(value) {
    return numberValue(value).toLocaleString("en-US", {
        maximumFractionDigits: 2,
    });
}

export function formatPrice(value) {
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

export function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

export function metricClass(value) {
    if (value >= 80) {
        return "metric-good";
    }

    if (value >= 50) {
        return "metric-mid";
    }

    return "metric-bad";
}

export function spreadClass(value) {
    if (value <= 0.05) {
        return "metric-good";
    }

    if (value <= 0.2) {
        return "metric-mid";
    }

    return "metric-bad";
}
