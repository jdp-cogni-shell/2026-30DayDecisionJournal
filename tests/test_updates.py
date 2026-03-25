from unittest.mock import AsyncMock
from tests.conftest import DECISION_ID


def test_add_update_returns_partial(client):
    c, mock_db = client
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.set = AsyncMock()
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.id = "new-update-id"
    mock_db.collection.return_value.document.return_value.update = AsyncMock()

    response = c.post(f"/decisions/{DECISION_ID}/updates", data={
        "source": "News article",
        "summary": "New information emerged",
        "confidence_adjusted": "75",
        "confidence_rationale": "Evidence supports decision",
    })
    assert response.status_code == 200
    assert "News article" in response.text
    assert "75" in response.text
