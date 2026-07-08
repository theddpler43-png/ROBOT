from __future__ import annotations

from abc import ABC, abstractmethod

from scanner.models import MarketRow


class ExchangeAdapter(ABC):
    """
    Базовый интерфейс биржи.

    Все коннекторы (BitMart, MEXC и будущие)
    должны реализовывать одинаковый набор методов.
    """

    name: str

    @abstractmethod
    async def fetch_symbols(self) -> list[str]:
        """Получить список торговых пар."""
        raise NotImplementedError

    @abstractmethod
    async def fetch_orderbook(self, symbol: str) -> dict:
        """Получить стакан."""
        raise NotImplementedError

    @abstractmethod
    async def fetch_trades(
        self,
        symbol: str,
        limit: int,
    ) -> list[dict]:
        """Получить последние сделки."""
        raise NotImplementedError

    @abstractmethod
    async def scan_symbol(
        self,
        symbol: str,
        trade_limit: int,
    ) -> MarketRow:
        """Вернуть полностью рассчитанный MarketRow."""
        raise NotImplementedError
