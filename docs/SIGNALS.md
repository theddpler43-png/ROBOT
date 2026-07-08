# ROBOT Browser V9 — Signal Engine

## Цель

Метрики сами по себе не являются выводом.

Каждая метрика должна быть преобразована в сигнал.

---

## Execution Signal

| Execution | Signal |
|-----------:|--------|
| 90–100 | STRONG |
| 75–89 | GOOD |
| 60–74 | WEAK |
| <60 | BAD |

---

## Uniformity Signal

| Uniformity | Signal |
|-----------:|--------|
| 85–100 | STRONG |
| 70–84 | GOOD |
| 50–69 | WEAK |
| <50 | BAD |

---

## Smoothness Signal

| Smoothness | Signal |
|-----------:|--------|
| 85–100 | STRONG |
| 70–84 | GOOD |
| 50–69 | WEAK |
| <50 | BAD |

---

## Spread Signal

| Spread | Signal |
|--------:|--------|
| <0.05% | EXCELLENT |
| <0.15% | GOOD |
| <0.30% | ACCEPTABLE |
| >=0.30% | BAD |

---

## Depth Balance Signal

| Bid/Ask | Signal |
|----------|--------|
| 45–55 | BALANCED |
| 35–65 | NORMAL |
| иначе | IMBALANCED |

---

## Confidence

Определяется совокупностью сигналов.

### HIGH

- Execution = STRONG
- Uniformity = STRONG
- Smoothness = STRONG

### MEDIUM

Большинство сигналов GOOD.

### LOW

Хотя бы один основной сигнал BAD.

---

## Pattern

Pattern определяется только сигналами.

Не абсолютными значениями.

Например:

```
Execution = STRONG

Uniformity = STRONG

Smoothness = STRONG

↓

MARKET_MAKER
```

или

```
Execution = STRONG

Uniformity = BAD

↓

UNKNOWN
```

---

## Принцип

Metrics → Signals → Analysis → Pattern
