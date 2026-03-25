from unittest.mock import AsyncMock
from tests.conftest import make_doc, DECISION_DATA, DECISION_ID, UPDATE_DATA


def test_dashboard(client):
    c, mock_db = client
    mock_db.collection.return_value.order_by.return_value.get = AsyncMock(
        return_value=[make_doc(data=DECISION_DATA)]
    )
    response = c.get("/")
    assert response.status_code == 200
    assert "Accept job offer" in response.text


def test_new_decision_form(client):
    c, mock_db = client
    response = c.get("/decisions/new")
    assert response.status_code == 200
    assert "New Decision" in response.text


def test_create_decision_redirects(client):
    c, mock_db = client
    mock_db.collection.return_value.document.return_value.set = AsyncMock()
    mock_db.collection.return_value.document.return_value.id = DECISION_ID
    response = c.post("/decisions", data={
        "title": "Test decision",
        "confidence_initial": "60",
        "description": "",
        "evidence_known": "",
        "evidence_unknown": "",
        "evidence_would_change": "",
        "premortem_reason_1": "",
        "premortem_reason_2": "",
        "premortem_reason_3": "",
        "tags": "",
    }, follow_redirects=False)
    assert response.status_code == 303
    assert f"/decisions/{DECISION_ID}" in response.headers["location"]


def test_get_decision_detail(client):
    c, mock_db = client
    mock_db.collection.return_value.document.return_value.get = AsyncMock(
        return_value=make_doc(data=DECISION_DATA)
    )
    mock_db.collection.return_value.document.return_value.collection.return_value.order_by.return_value.get = AsyncMock(
        return_value=[make_doc(data=UPDATE_DATA, doc_id="update-id")]
    )
    mock_db.collection.return_value.where.return_value.limit.return_value.get = AsyncMock(return_value=[])
    response = c.get(f"/decisions/{DECISION_ID}")
    assert response.status_code == 200
    assert "Accept job offer" in response.text
    assert "Record Outcome" in response.text


def test_get_decision_not_found(client):
    c, mock_db = client
    mock_db.collection.return_value.document.return_value.get = AsyncMock(
        return_value=make_doc(exists=False)
    )
    response = c.get("/decisions/nonexistent")
    assert response.status_code == 404


def test_edit_decision_form(client):
    c, mock_db = client
    mock_db.collection.return_value.document.return_value.get = AsyncMock(
        return_value=make_doc(data=DECISION_DATA)
    )
    response = c.get(f"/decisions/{DECISION_ID}/edit")
    assert response.status_code == 200
    assert "Accept job offer" in response.text


def test_edit_executed_decision_redirects(client):
    c, mock_db = client
    mock_db.collection.return_value.document.return_value.get = AsyncMock(
        return_value=make_doc(data={**DECISION_DATA, "status": "executed"})
    )
    response = c.post(f"/decisions/{DECISION_ID}/edit", data={
        "title": "Updated",
        "confidence_initial": "80",
    }, follow_redirects=False)
    assert response.status_code == 303
