from unittest.mock import AsyncMock


def test_health_ok(client):
    c, mock_db = client
    mock_db.collection.return_value.limit.return_value.get = AsyncMock(return_value=[])
    response = c.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["firestore"] == "connected"
