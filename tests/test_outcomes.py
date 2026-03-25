from unittest.mock import AsyncMock
from tests.conftest import make_doc, DECISION_DATA, DECISION_ID, UPDATE_DATA


def test_new_outcome_form(client):
    c, mock_db = client
    mock_db.collection.return_value.document.return_value.get = AsyncMock(
        return_value=make_doc(data=DECISION_DATA)
    )
    response = c.get(f"/decisions/{DECISION_ID}/outcome/new")
    assert response.status_code == 200
    assert "Record Outcome" in response.text
    assert "Accept job offer" in response.text


def test_new_outcome_form_blocks_executed(client):
    c, mock_db = client
    mock_db.collection.return_value.document.return_value.get = AsyncMock(
        return_value=make_doc(data={**DECISION_DATA, "status": "executed"})
    )
    response = c.get(f"/decisions/{DECISION_ID}/outcome/new", follow_redirects=False)
    assert response.status_code == 303


def test_create_outcome_redirects(client):
    c, mock_db = client
    mock_db.collection.return_value.document.return_value.get = AsyncMock(
        return_value=make_doc(data=DECISION_DATA)
    )
    mock_db.collection.return_value.document.return_value.collection.return_value.order_by.return_value.limit.return_value.get = AsyncMock(
        return_value=[make_doc(data=UPDATE_DATA, doc_id="update-id")]
    )
    mock_db.collection.return_value.document.return_value.set = AsyncMock()
    mock_db.collection.return_value.document.return_value.update = AsyncMock()

    response = c.post(f"/decisions/{DECISION_ID}/outcome", data={
        "implementation_date": "2026-03-01",
        "actual_result": "Worked out well",
        "outcome_valence": "positive",
        "postmortem_notes": "Good decision",
    }, follow_redirects=False)
    assert response.status_code == 303
    assert f"/decisions/{DECISION_ID}" in response.headers["location"]
