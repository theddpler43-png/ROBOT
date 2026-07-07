async function loadMarkets() {
  try {
    const response = await fetch("../data/markets.json?ts=" + Date.now());
    const data = await response.json();

    console.log("markets.json loaded:", data);
  } catch (error) {
    console.error("Ошибка загрузки markets.json:", error);
  }
}

loadMarkets();
setInterval(loadMarkets, 2000);
