async function loadMarkets() {
  try {
    const response = await fetch("/markets?ts=" + Date.now());

    if (!response.ok) {
      console.warn("markets endpoint error:", response.status);
      return;
    }

    const data = await response.json();

    console.clear();
    console.log("status:", data.status, "count:", data.count, "total:", data.total);
    console.table((data.markets || []).slice(0, 10));
  } catch (error) {
    console.error("Ошибка загрузки markets:", error);
  }
}

loadMarkets();
setInterval(loadMarkets, 1000);
