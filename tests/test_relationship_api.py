from fastapi.testclient import TestClient

from backend.app.main import app


def test_relationships_include_related_entity_names():
    client = TestClient(app)

    response = client.get("/relationships", params={"limit": 1})

    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert payload[0]["source_name"]
    assert payload[0]["target_name"]


def test_entity_relationships_include_related_entity_names():
    client = TestClient(app)
    relationship = client.get("/relationships", params={"limit": 1}).json()[0]

    response = client.get(f"/entities/{relationship['source_entity_id']}/relationships")

    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert payload[0]["source_name"]
    assert payload[0]["target_name"]
