from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.error_handlers import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.main import app as real_app


def make_app() -> FastAPI:
    app = FastAPI()
    app.add_exception_handler(
        StarletteHTTPException, http_exception_handler  # type: ignore[arg-type]
    )
    app.add_exception_handler(
        RequestValidationError, validation_exception_handler  # type: ignore[arg-type]
    )
    app.add_exception_handler(Exception, unhandled_exception_handler)

    @app.get("/teapot")
    def teapot() -> None:
        raise HTTPException(status_code=418, detail="I'm a teapot")

    @app.get("/validate")
    def validate(n: int) -> dict[str, int]:
        return {"n": n}

    @app.get("/boom")
    def boom() -> None:
        raise ValueError("kaboom")

    return app


client = TestClient(make_app(), raise_server_exceptions=False)


def test_http_exception_uses_envelope() -> None:
    response = client.get("/teapot")

    assert response.status_code == 418
    body = response.json()
    assert body["error"] == {"type": "http_error", "message": "I'm a teapot"}
    assert "request_id" in body


def test_validation_error_uses_envelope() -> None:
    response = client.get("/validate")

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["type"] == "validation_error"
    assert isinstance(body["error"]["details"], list)


def test_unhandled_exception_hides_details() -> None:
    response = client.get("/boom")

    assert response.status_code == 500
    body = response.json()
    assert body["error"] == {
        "type": "internal_error",
        "message": "Internal server error",
    }
    assert "kaboom" not in response.text


def test_real_app_404_uses_envelope() -> None:
    real_client = TestClient(real_app)

    response = real_client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json()["error"]["type"] == "http_error"
