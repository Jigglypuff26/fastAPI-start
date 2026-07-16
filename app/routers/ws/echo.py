from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from app.core.config import settings

router = APIRouter(prefix="/api/v1", tags=["websocket"])
_PATH = "/ws"
# Полный путь (с префиксом роутера) — не используется в этом файле, экспортируется
# для tests/test_ws_echo.py, которому нужен реальный адрес эндпоинта, а не
# относительный внутри роутера (аналогично ROOT_PATH в app/routers/http/healthcheck.py).
ROOT_PATH = f"{router.prefix}{_PATH}"


@router.websocket(_PATH)
async def websocket_echo(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(message)
    except WebSocketDisconnect:
        pass


_WS_TEST_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>WS echo demo</title>
</head>
<body>
    <h1>WebSocket echo demo</h1>
    <form onsubmit="sendMessage(event)">
        <input type="text" id="messageInput" autocomplete="off"/>
        <button type="submit">Send</button>
    </form>
    <ul id="messages"></ul>
    <script>
        const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
        const ws = new WebSocket(`${proto}//${window.location.host}/api/v1/ws`);

        ws.onmessage = (event) => {
            const messages = document.getElementById("messages");
            const item = document.createElement("li");
            item.textContent = event.data;
            messages.appendChild(item);
        };

        function sendMessage(event) {
            event.preventDefault();
            const input = document.getElementById("messageInput");
            ws.send(input.value);
            input.value = "";
        }
    </script>
</body>
</html>
"""


if settings.debug:

    @router.get(f"{_PATH}/test", response_class=HTMLResponse)
    def websocket_test_page() -> str:
        return _WS_TEST_PAGE
