from datetime import datetime, timezone
from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from google.cloud.firestore import AsyncClient

from db import get_firestore_client

router = APIRouter(prefix="/decisions/{decision_id}/updates")
templates = Jinja2Templates(directory="templates")


@router.post("")
async def add_update(
    request: Request,
    decision_id: str,
    source: str = Form(...),
    summary: str = Form(...),
    confidence_adjusted: int = Form(...),
    confidence_rationale: str = Form(""),
    db: AsyncClient = Depends(get_firestore_client),
):
    ts = datetime.now(timezone.utc)
    update_ref = db.collection("decisions").document(decision_id).collection("updates").document()
    await update_ref.set({
        "source": source,
        "summary": summary,
        "confidence_adjusted": confidence_adjusted,
        "confidence_rationale": confidence_rationale,
        "created_at": ts,
    })
    # Update parent decision's updated_at
    await db.collection("decisions").document(decision_id).update({"updated_at": ts})

    update = {
        "id": update_ref.id,
        "source": source,
        "summary": summary,
        "confidence_adjusted": confidence_adjusted,
        "confidence_rationale": confidence_rationale,
        "created_at": ts,
    }
    return templates.TemplateResponse(request, "updates/_update_item.html", {"update": update})
