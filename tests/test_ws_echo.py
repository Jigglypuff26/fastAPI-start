from fastapi.testclient import TestClient

from app.main import app
from app.routers.ws.echo import ROOT_PATH

client = TestClient(app)


def test_websocket_echo() -> None:
    with client.websocket_connect(ROOT_PATH) as websocket:
        websocket.send_text("hello")
        assert websocket.receive_text() == "hello"

        websocket.send_text("another message")
        assert websocket.receive_text() == "another message"
