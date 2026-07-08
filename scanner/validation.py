from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from scanner.models import MarketRow


ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT / "logs"


def export_validation(markets: list[MarketRow]) -> Path:
    """
    Сохраняет результаты полного сканирования
    для последующего анализа качества алгоритма.
    """

    LOGS_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = LOGS_DIR / f"validation_{timestamp}.json"

    payload = {
        "created": datetime.now().isoformat(),
        "count": len(markets),
        "markets": [
            market.to_dict()
            for market in sorted(
                markets,
                key=lambda m: (
                    m.score is None,
                    -(m.score or 0),
                ),
            )
        ],
    }

    with filename.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return filename
