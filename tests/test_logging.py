import logging

from fastapi.testclient import TestClient

from app.core.request_logging import REQUEST_ID_HEADER
from app.main import app

client = TestClient(app)


def test_generates_request_id_when_missing() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER]


def test_echoes_incoming_request_id() -> None:
    response = client.get("/", headers={REQUEST_ID_HEADER: "test-id-123"})

    assert response.headers[REQUEST_ID_HEADER] == "test-id-123"


def test_logs_request_completion(caplog) -> None:
    with caplog.at_level(logging.INFO, logger="app.request"):
        client.get("/")

    assert any("GET / 200" in record.getMessage() for record in caplog.records)
