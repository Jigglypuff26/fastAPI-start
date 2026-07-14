from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.ip_allowlist import IPAllowlistMiddleware


def make_app(allowed_ips: list[str]) -> FastAPI:
    app = FastAPI()
    app.add_middleware(IPAllowlistMiddleware, allowed_ips=allowed_ips)

    @app.get("/")
    def read_root() -> dict[str, str]:
        return {"message": "ok"}

    return app


def test_no_restriction_when_allowlist_empty() -> None:
    client = TestClient(make_app([]), client=("203.0.113.5", 12345))

    response = client.get("/")

    assert response.status_code == 200


def test_allows_ip_in_allowlist() -> None:
    client = TestClient(make_app(["203.0.113.5"]), client=("203.0.113.5", 12345))

    response = client.get("/")

    assert response.status_code == 200


def test_allows_ip_in_cidr_range() -> None:
    client = TestClient(make_app(["10.0.0.0/24"]), client=("10.0.0.42", 12345))

    response = client.get("/")

    assert response.status_code == 200


def test_rejects_ip_not_in_allowlist() -> None:
    client = TestClient(make_app(["203.0.113.5"]), client=("198.51.100.9", 12345))

    response = client.get("/")

    assert response.status_code == 403
