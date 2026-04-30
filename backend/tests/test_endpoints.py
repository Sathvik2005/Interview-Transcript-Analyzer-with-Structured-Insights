from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_providers():
    r = client.get("/api/providers")
    assert r.status_code == 200
    data = r.json()
    assert "preferred_provider" in data
    assert isinstance(data.get("gemini_configured"), bool)