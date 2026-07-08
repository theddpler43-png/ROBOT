from __future__ import annotations

from dataclasses import dataclass

from scanner.models import MarketRow


@dataclass(slots=True)
class MarketContext:
    """
    Контекст анализа рынка.

    Содержит текущее состояние рынка
    и дополнительные данные (история,
    временные метрики и т.п.).

    Пока используется только current.

    В дальнейшем будет расширяться
    без изменения сигнатуры Analysis.
    """

    current: MarketRow

    history: dict | None = None
