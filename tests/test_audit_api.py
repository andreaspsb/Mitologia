from fastapi.testclient import TestClient

from backend.app.main import app


def test_audit_summary_exposes_counts_and_review_items():
    client = TestClient(app)

    response = client.get("/audit/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["totals"]["entities"] >= 1
    assert payload["entity_type_counts"]
    assert payload["relationship_type_counts"]
    assert "unknown_entities" in payload
    assert "associated_relationships" in payload
