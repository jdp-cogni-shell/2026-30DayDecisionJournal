from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from db import get_firestore_client

app = FastAPI(title="30 Day Decision Journal")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    try:
        db = get_firestore_client()
        await db.collection("decisions").limit(1).get()
        return {"status": "ok", "firestore": "connected"}
    except Exception as e:
        return {"status": "ok", "firestore": f"error: {e}"}
