from datetime import datetime, timezone, date
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud.firestore import AsyncClient

from db import get_firestore_client

router = APIRouter(prefix="/decisions/{decision_id}/outcome")
templates = Jinja2Templates(directory="templates")


@router.get("/new")
async def new_outcome(
    request: Request,
    decision_id: str,
    db: AsyncClient = Depends(get_firestore_client),
):
    doc = await db.collection("decisions").document(decision_id).get()
    if not doc.exists:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    decision = {"id": doc.id, **doc.to_dict()}
    if decision.get("status") != "open":
        return RedirectResponse(url=f"/decisions/{decision_id}", status_code=303)
    return templates.TemplateResponse("outcomes/new.html", {
        "request": request,
        "decision": decision,
    })


@router.post("")
async def create_outcome(
    request: Request,
    decision_id: str,
    implementation_date: str = Form(...),
    actual_result: str = Form(...),
    outcome_valence: str = Form(...),
    postmortem_notes: str = Form(""),
    db: AsyncClient = Depends(get_firestore_client),
):
    doc_ref = db.collection("decisions").document(decision_id)
    doc = await doc_ref.get()
    if not doc.exists:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    if doc.to_dict().get("status") != "open":
        return RedirectResponse(url=f"/decisions/{decision_id}", status_code=303)

    # Get last confidence value (from updates or initial)
    update_docs = await doc_ref.collection("updates").order_by("created_at", direction="DESCENDING").limit(1).get()
    if update_docs:
        final_confidence = update_docs[0].to_dict().get("confidence_adjusted")
    else:
        final_confidence = doc.to_dict().get("confidence_initial")

    ts = datetime.now(timezone.utc)
    outcome_ref = db.collection("outcomes").document()
    await outcome_ref.set({
        "decision_id": decision_id,
        "implementation_date": implementation_date,
        "actual_result": actual_result,
        "outcome_valence": outcome_valence,
        "postmortem_notes": postmortem_notes,
        "final_confidence": final_confidence,
        "created_at": ts,
    })

    await doc_ref.update({
        "status": "executed",
        "updated_at": ts,
    })

    return RedirectResponse(url=f"/decisions/{decision_id}", status_code=303)
