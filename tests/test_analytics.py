from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from tests.conftest import make_doc, DECISION_DATA, DECISION_ID, OUTCOME_DATA


def _make_outcome_doc(valence="positive", confidence=75):
    data = {**OUTCOME_DATA, "outcome_valence": valence, "final_confidence": confidence}
    return make_doc(data=data, doc_id="outcome-id")


def test_analytics_dashboard(client):
    c, mock_db = client
    response = c.get("/analytics")
    assert response.status_code == 200
    assert "Analytics" in response.text
    assert "hx-get" in response.text


def test_calibration_no_outcomes(client):
    c, mock_db = client
    mock_db.collection.return_value.get = AsyncMock(return_value=[])
    response = c.get("/analytics/calibration")
    assert response.status_code == 200
    assert "No completed decisions" in response.text


def test_calibration_with_outcomes(client):
    c, mock_db = client
    mock_db.collection.return_value.get = AsyncMock(
        return_value=[_make_outcome_doc("positive", 80)]
    )
    response = c.get("/analytics/calibration")
    assert response.status_code == 200
    assert "Brier Score" in response.text
    assert "81–100%" in response.text


def test_bias_no_flags(client):
    c, mock_db = client
    # No decisions, no outcomes
    mock_db.collection.return_value.get = AsyncMock(return_value=[])
    response = c.get("/analytics/bias")
    assert response.status_code == 200
    assert "No bias flags" in response.text


def test_bias_stale_decision(client):
    c, mock_db = client
    old_date = datetime.now(timezone.utc) - timedelta(days=10)
    stale_data = {**DECISION_DATA, "status": "open", "created_at": old_date}

    # decisions query returns stale open decision; outcomes query returns empty
    call_count = 0
    async def collection_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return [make_doc(data=stale_data)]  # decisions
        return []  # outcomes

    mock_db.collection.return_value.get = collection_get
    # updates subcollection returns 0 updates
    mock_db.collection.return_value.document.return_value.collection.return_value.limit.return_value.get = AsyncMock(return_value=[])

    response = c.get("/analytics/bias")
    assert response.status_code == 200
    assert "Stale" in response.text


def test_premortem_no_data(client):
    c, mock_db = client
    mock_db.collection.return_value.get = AsyncMock(return_value=[])
    response = c.get("/analytics/premortem")
    assert response.status_code == 200
    assert "No pre-mortem reasons" in response.text


def test_premortem_with_data(client):
    c, mock_db = client
    data = {
        **DECISION_DATA,
        "premortem_reason_1": "market conditions could change rapidly",
        "premortem_reason_2": "team capacity could be overestimated",
        "premortem_reason_3": "budget conditions might not hold",
    }
    mock_db.collection.return_value.get = AsyncMock(
        return_value=[make_doc(data=data)]
    )
    response = c.get("/analytics/premortem")
    assert response.status_code == 200
    assert "conditions" in response.text
