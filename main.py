from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from google.cloud.firestore import AsyncClient

from db import get_firestore_client
from routers import decisions, updates, outcomes

app = FastAPI(title="30 Day Decision Journal")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(decisions.router)
app.include_router(updates.router)
app.include_router(outcomes.router)


@app.get("/")
async def index(request: Request, db: AsyncClient = Depends(get_firestore_client)):
    docs = await db.collection("decisions").order_by("updated_at", direction="DESCENDING").get()
    all_decisions = [{"id": d.id, **d.to_dict()} for d in docs]
    counts = {
        "open": sum(1 for d in all_decisions if d.get("status") == "open"),
        "executed": sum(1 for d in all_decisions if d.get("status") == "executed"),
        "abandoned": sum(1 for d in all_decisions if d.get("status") == "abandoned"),
    }
    return templates.TemplateResponse("index.html", {
        "request": request,
        "decisions": all_decisions,
        "counts": counts,
    })


@app.get("/health")
async def health(db: AsyncClient = Depends(get_firestore_client)):
    try:
        await db.collection("decisions").limit(1).get()
        return {"status": "ok", "firestore": "connected"}
    except Exception as e:
        return {"status": "ok", "firestore": f"error: {e}"}
