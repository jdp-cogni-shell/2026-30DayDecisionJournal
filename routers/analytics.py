import asyncio
from collections import Counter
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from google.cloud.firestore import AsyncClient

from db import get_firestore_client

router = APIRouter(prefix="/analytics")
templates = Jinja2Templates(directory="templates")

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "was", "are", "were", "be", "been", "my", "i",
    "it", "this", "that", "could", "might", "may", "would", "will", "if",
    "not", "no", "by", "as", "we", "they", "our", "their", "its", "can",
    "do", "did", "have", "has", "had", "from", "about", "which", "when",
}

BUCKET_LABELS = ["0–20%", "21–40%", "41–60%", "61–80%", "81–100%"]


def _confidence_bucket(confidence: int) -> int:
    if confidence <= 20:
        return 0
    elif confidence <= 40:
        return 1
    elif confidence <= 60:
        return 2
    elif confidence <= 80:
        return 3
    return 4


@router.get("")
async def analytics_dashboard(request: Request):
    return templates.TemplateResponse(request, "analytics/dashboard.html")


@router.get("/calibration")
async def calibration(request: Request, db: AsyncClient = Depends(get_firestore_client)):
    outcome_docs = await db.collection("outcomes").get()
    outcomes = [{"id": d.id, **d.to_dict()} for d in outcome_docs]

    buckets = [{"label": l, "count": 0, "positive": 0} for l in BUCKET_LABELS]
    brier_sum = 0.0

    for o in outcomes:
        confidence = o.get("final_confidence", 50)
        valence = o.get("outcome_valence", "unknown")
        forecast = confidence / 100.0
        actual = 1.0 if valence == "positive" else (0.5 if valence == "mixed" else 0.0)
        brier_sum += (forecast - actual) ** 2
        idx = _confidence_bucket(confidence)
        buckets[idx]["count"] += 1
        if valence == "positive":
            buckets[idx]["positive"] += 1

    brier_score = round(brier_sum / len(outcomes), 3) if outcomes else None

    # Compute actual rate per bucket
    for b in buckets:
        b["actual_rate"] = round(b["positive"] / b["count"] * 100) if b["count"] else None

    return templates.TemplateResponse(request, "analytics/_calibration.html", {
        "buckets": buckets,
        "brier_score": brier_score,
        "total": len(outcomes),
    })


@router.get("/bias")
async def bias_flags(request: Request, db: AsyncClient = Depends(get_firestore_client)):
    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(days=7)

    decision_docs = await db.collection("decisions").get()
    decisions = [{"id": d.id, **d.to_dict()} for d in decision_docs]

    outcome_docs = await db.collection("outcomes").get()
    outcomes = [{"id": d.id, **d.to_dict()} for d in outcome_docs]

    # --- Stale decisions: open, > 7 days old, 0 updates ---
    open_decisions = [d for d in decisions if d.get("status") == "open"]

    async def count_updates(decision_id):
        docs = await db.collection("decisions").document(decision_id).collection("updates").limit(1).get()
        return decision_id, len(docs)

    update_counts = dict(await asyncio.gather(*[count_updates(d["id"]) for d in open_decisions]))

    stale = [
        d for d in open_decisions
        if update_counts.get(d["id"], 0) == 0
        and d.get("created_at") and d["created_at"] < stale_cutoff
    ]

    # --- Overconfidence: final_confidence >= 80, outcome negative ---
    overconfident = [
        o for o in outcomes
        if o.get("final_confidence", 0) >= 80 and o.get("outcome_valence") == "negative"
    ]
    # Enrich with decision title
    decision_map = {d["id"]: d for d in decisions}
    for o in overconfident:
        d = decision_map.get(o.get("decision_id"), {})
        o["decision_title"] = d.get("title", "Unknown")

    # --- Anchoring: executed decisions where confidence never moved > 10 points ---
    executed_decisions = [d for d in decisions if d.get("status") == "executed"]

    async def get_updates(decision_id):
        docs = await db.collection("decisions").document(decision_id).collection("updates").order_by("created_at").get()
        return decision_id, [{"id": u.id, **u.to_dict()} for u in docs]

    updates_by_decision = dict(await asyncio.gather(*[get_updates(d["id"]) for d in executed_decisions]))

    anchored = []
    for d in executed_decisions:
        updates = updates_by_decision.get(d["id"], [])
        if not updates:
            continue
        initial = d.get("confidence_initial", 50)
        all_confidences = [initial] + [u.get("confidence_adjusted", initial) for u in updates]
        if max(all_confidences) - min(all_confidences) <= 10:
            anchored.append(d)

    return templates.TemplateResponse(request, "analytics/_bias_flags.html", {
        "stale": stale,
        "overconfident": overconfident,
        "anchored": anchored,
    })


@router.get("/premortem")
async def premortem_patterns(request: Request, db: AsyncClient = Depends(get_firestore_client)):
    decision_docs = await db.collection("decisions").get()
    decisions = [d.to_dict() for d in decision_docs]

    all_text = []
    for d in decisions:
        for field in ["premortem_reason_1", "premortem_reason_2", "premortem_reason_3"]:
            text = d.get(field, "")
            if text:
                all_text.append(text.lower())

    words = []
    for text in all_text:
        for word in text.split():
            clean = word.strip(".,!?;:\"'()-")
            if clean and clean not in STOP_WORDS and len(clean) > 2:
                words.append(clean)

    top_words = Counter(words).most_common(10)

    return templates.TemplateResponse(request, "analytics/_premortem.html", {
        "top_words": top_words,
        "total_reasons": len(all_text),
    })
