from fastapi.testclient import TestClient

from backend.app.main import app


def test_entities_accept_large_limit_for_graph_views():
    client = TestClient(app)

    response = client.get("/entities", params={"limit": 1000})

    assert response.status_code == 200
    assert len(response.json()) <= 1000


def test_relationships_accept_large_limit_for_graph_views():
    client = TestClient(app)

    response = client.get("/relationships", params={"limit": 1000})

    assert response.status_code == 200
    assert len(response.json()) <= 1000
