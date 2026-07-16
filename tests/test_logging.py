import logging

from fastapi.testclient import TestClient

from app.core.request_logging import REQUEST_ID_HEADER
from app.main import app
from app.routers.http.healthcheck import ROOT_PATH

client = TestClient(app)


def test_generates_request_id_when_missing() -> None:
    response = client.get(ROOT_PATH)

    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER]


def test_echoes_incoming_request_id() -> None:
    response = client.get(ROOT_PATH, headers={REQUEST_ID_HEADER: "test-id-123"})

    assert response.headers[REQUEST_ID_HEADER] == "test-id-123"


def test_logs_request_completion(caplog) -> None:
    with caplog.at_level(logging.INFO, logger="app.request"):
        client.get(ROOT_PATH)

    assert any(
        f"GET {ROOT_PATH} 200" in record.getMessage() for record in caplog.records
    )
