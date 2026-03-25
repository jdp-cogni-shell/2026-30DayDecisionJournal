import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from main import app
from db import get_firestore_client

DECISION_ID = "test-decision-id"

DECISION_DATA = {
    "title": "Accept job offer",
    "description": "Should I take the new role?",
    "status": "open",
    "confidence_initial": 70,
    "evidence_known": "Good salary",
    "evidence_unknown": "Team culture",
    "evidence_would_change": "Meeting the team",
    "premortem_reason_1": "Role may be misrepresented",
    "premortem_reason_2": "Company could downsize",
    "premortem_reason_3": "Commute might be worse",
    "tags": ["career"],
    "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
}

UPDATE_DATA = {
    "source": "Interview",
    "summary": "Met the team, culture seems good",
    "confidence_adjusted": 80,
    "confidence_rationale": "Team impressed me",
    "created_at": datetime(2026, 1, 2, tzinfo=timezone.utc),
}

OUTCOME_DATA = {
    "decision_id": DECISION_ID,
    "implementation_date": "2026-02-01",
    "actual_result": "Took the job, going well",
    "outcome_valence": "positive",
    "postmortem_notes": "Good call overall",
    "final_confidence": 80,
    "created_at": datetime(2026, 3, 1, tzinfo=timezone.utc),
}


def make_doc(exists=True, data=None, doc_id=DECISION_ID):
    doc = MagicMock()
    doc.exists = exists
    doc.id = doc_id
    doc.to_dict.return_value = data or {}
    return doc


@pytest.fixture
def mock_db():
    # MagicMock for sync chained calls; only terminal methods are AsyncMock
    db = MagicMock()
    return db


@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_firestore_client] = lambda: mock_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c, mock_db
    app.dependency_overrides.clear()
