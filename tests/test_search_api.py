from fastapi.testclient import TestClient

from backend.app.main import app


def test_search_returns_entities_with_aliases():
    client = TestClient(app)

    response = client.get("/search", params={"q": "Zeus"})

    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert "aliases" in payload[0]
