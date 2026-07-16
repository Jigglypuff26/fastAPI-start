from fastapi.testclient import TestClient

from app.main import app
from app.routers.http.healthcheck import ROOT_PATH

client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get(ROOT_PATH)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
