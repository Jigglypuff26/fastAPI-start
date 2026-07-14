from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.limiter import limiter
from app.main import app
from app.routers.http.root import ROOT_PATH

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_limiter_state() -> Generator[None, None, None]:
    # limiter — общий синглтон на весь процесс: хранилище лимитов ключуется по
    # паттерну роута, а не по экземпляру приложения, поэтому без сброса
    # до/после теста расход квоты здесь протекает в тесты из других файлов
    # (test_root.py тоже дёргает ROOT_PATH).
    limiter.reset()
    yield
    limiter.reset()


def test_allows_requests_within_limit() -> None:
    response = client.get(ROOT_PATH)

    assert response.status_code == 200


def test_rejects_requests_over_limit() -> None:
    limit = int(settings.rate_limit.split("/")[0])

    for _ in range(limit):
        assert client.get(ROOT_PATH).status_code == 200

    response = client.get(ROOT_PATH)

    assert response.status_code == 429
