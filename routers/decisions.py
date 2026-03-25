from datetime import datetime, timezone
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud.firestore import AsyncClient

from db import get_firestore_client

router = APIRouter(prefix="/decisions")
templates = Jinja2Templates(directory="templates")


def now():
    return datetime.now(timezone.utc)


@router.get("/new")
async def new_decision(request: Request):
    return templates.TemplateResponse("decisions/new.html", {"request": request})


@router.post("")
async def create_decision(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    confidence_initial: int = Form(...),
    evidence_known: str = Form(""),
    evidence_unknown: str = Form(""),
    evidence_would_change: str = Form(""),
    premortem_reason_1: str = Form(""),
    premortem_reason_2: str = Form(""),
    premortem_reason_3: str = Form(""),
    tags: str = Form(""),
    db: AsyncClient = Depends(get_firestore_client),
):
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    ts = now()
    doc_ref = db.collection("decisions").document()
    await doc_ref.set({
        "title": title,
        "description": description,
        "status": "open",
        "confidence_initial": confidence_initial,
        "evidence_known": evidence_known,
        "evidence_unknown": evidence_unknown,
        "evidence_would_change": evidence_would_change,
        "premortem_reason_1": premortem_reason_1,
        "premortem_reason_2": premortem_reason_2,
        "premortem_reason_3": premortem_reason_3,
        "tags": tag_list,
        "created_at": ts,
        "updated_at": ts,
    })
    return RedirectResponse(url=f"/decisions/{doc_ref.id}", status_code=303)


@router.get("/{decision_id}")
async def get_decision(
    request: Request,
    decision_id: str,
    db: AsyncClient = Depends(get_firestore_client),
):
    doc = await db.collection("decisions").document(decision_id).get()
    if not doc.exists:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    decision = {"id": doc.id, **doc.to_dict()}
    return templates.TemplateResponse("decisions/detail.html", {"request": request, "decision": decision})


@router.get("/{decision_id}/edit")
async def edit_decision(
    request: Request,
    decision_id: str,
    db: AsyncClient = Depends(get_firestore_client),
):
    doc = await db.collection("decisions").document(decision_id).get()
    if not doc.exists:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    decision = {"id": doc.id, **doc.to_dict()}
    return templates.TemplateResponse("decisions/edit.html", {"request": request, "decision": decision})


@router.post("/{decision_id}/edit")
async def update_decision(
    request: Request,
    decision_id: str,
    title: str = Form(...),
    description: str = Form(""),
    confidence_initial: int = Form(...),
    evidence_known: str = Form(""),
    evidence_unknown: str = Form(""),
    evidence_would_change: str = Form(""),
    premortem_reason_1: str = Form(""),
    premortem_reason_2: str = Form(""),
    premortem_reason_3: str = Form(""),
    tags: str = Form(""),
    db: AsyncClient = Depends(get_firestore_client),
):
    doc_ref = db.collection("decisions").document(decision_id)
    doc = await doc_ref.get()
    if not doc.exists:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    if doc.to_dict().get("status") != "open":
        return RedirectResponse(url=f"/decisions/{decision_id}", status_code=303)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    await doc_ref.update({
        "title": title,
        "description": description,
        "confidence_initial": confidence_initial,
        "evidence_known": evidence_known,
        "evidence_unknown": evidence_unknown,
        "evidence_would_change": evidence_would_change,
        "premortem_reason_1": premortem_reason_1,
        "premortem_reason_2": premortem_reason_2,
        "premortem_reason_3": premortem_reason_3,
        "tags": tag_list,
        "updated_at": now(),
    })
    return RedirectResponse(url=f"/decisions/{decision_id}", status_code=303)
