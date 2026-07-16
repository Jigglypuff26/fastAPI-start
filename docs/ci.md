# 🤖 CI

Обзор пайплайна CI и того, где это находится в коде.

## Когда запускается

Только на pull request в `main` (`on: pull_request: branches: [main]`) — прямые push в ветки CI не гоняет. Повторный push в тот же PR отменяет предыдущий незавершённый запуск (`concurrency`), чтобы не тратить время раннеров на устаревший коммит.

Настроено в [.github/workflows/ci.yml](../.github/workflows/ci.yml).

## Что проверяется

Две независимые джобы, выполняются параллельно:

- **lint** — `black --check .`, `flake8`, `mypy app` (те же команды, что и `python scripts/lint.py`, но без авто-форматирования — CI только проверяет, не меняет файлы).
- **test** — `pytest`.

PR нельзя смёрджить, пока обе джобы не позеленеют (при включённой настройке branch protection на `main`, см. ниже).

## Локально до пуша

Чтобы не ждать CI на каждую мелочь:

```powershell
python scripts/lint.py
pytest
```

Или поставить [pre-commit hooks](../README.md#-pre-commit-hooks) — тогда часть проверок (black, flake8, mypy) выполнится ещё до коммита.

## Ограничения / что не входит

- Нет джобы, которая реально поднимает PostgreSQL/Redis — текущие тесты их не требуют (см. [docs/logging.md](logging.md) и `tests/`). Если появятся тесты, дёргающие `/api/v1/postgre-check`/`/api/v1/redis-check` или БД напрямую, понадобится `services:` (`postgres`, `redis`) в джобе `test`.
- Branch protection (запрет мёрджа без зелёного CI, запрет push напрямую в `main`) настраивается в GitHub UI (Settings → Branches) — сам workflow этого не enforce'ит.
- Нет автосборки/паблиша Docker-образа — только lint и тесты.
