# 30-Day Decision Journal — Build Plan

## Status Legend
- [ ] Not started
- [~] In progress
- [x] Complete

---

## Data Model

### Firestore Collections

**`decisions/{decision_id}`**
- `title` — str
- `description` — str
- `created_at` — timestamp
- `updated_at` — timestamp
- `status` — enum: `open` | `executed` | `abandoned`
- `confidence_initial` — int (0–100)
- `evidence_known` — str
- `evidence_unknown` — str
- `evidence_would_change` — str
- `premortem_reason_1` — str
- `premortem_reason_2` — str
- `premortem_reason_3` — str
- `tags` — list[str]

**`decisions/{decision_id}/updates/{update_id}`**
- `timestamp` — timestamp
- `source` — str
- `summary` — str
- `confidence_adjusted` — int (0–100)
- `confidence_rationale` — str
- `created_at` — timestamp

**`outcomes/{outcome_id}`**
- `decision_id` — str (ref to decisions/{id})
- `implementation_date` — date
- `actual_result` — str
- `postmortem_notes` — str
- `outcome_valence` — enum: `positive` | `negative` | `mixed` | `unknown`
- `final_confidence` — int (denormalized for analytics)
- `created_at` — timestamp

---

## Phase 1 — Firestore Infrastructure
**Goal**: Firestore connected, health check passes locally and on Cloud Run.

- [x] Add `google-cloud-firestore==2.19.0` and `pydantic==2.9.2` to `requirements.txt`
- [x] Create `db.py` — AsyncClient singleton with `get_firestore_client()` dependency
- [x] Update `cloudbuild.yaml` — add `GOOGLE_CLOUD_PROJECT` env var to Cloud Run deploy step
- [x] Update `GCP_SETUP.md` — add Firestore API enable + database creation steps
- [x] Update `/health` endpoint — verify Firestore connectivity
- [x] Enable Firestore API on GCP: `gcloud services enable firestore.googleapis.com`
- [x] Create Firestore database: `gcloud firestore databases create --location=us-central1`
- [x] Confirm health check passes locally and on Cloud Run

---

## Phase 2 — Core CRUD: Decisions
**Goal**: Create, view, list, and edit decisions.

- [x] Create `models.py` — `DecisionCreate`, `DecisionRead`, `DecisionUpdate` Pydantic models
- [x] Create `routers/decisions.py` — 6 decision routes
- [x] Create `templates/base.html` — layout shell (nav, Tailwind CDN, HTMX CDN, content block)
- [x] Update `templates/index.html` — dashboard with decision card list
- [x] Create `templates/decisions/new.html` — full entry form with confidence slider
- [x] Create `templates/decisions/detail.html` — read-only decision view
- [x] Create `templates/decisions/edit.html` — pre-populated edit form
- [x] Register decisions router in `main.py`
- [x] Confirm full round-trip: create → dashboard → detail → edit

---

## Phase 3 — Update Events
**Goal**: Add and view information updates inline without page reload.

- [x] Create `routers/updates.py`
- [x] Create `templates/updates/_update_item.html` — HTMX partial: single update row
- [x] Create `templates/updates/_update_form.html` — HTMX partial: inline add form
- [x] Wire HTMX in `decisions/detail.html` — POST to `/decisions/{id}/updates`, swap `beforeend` into `#update-list`
- [x] Register updates router in `main.py`
- [ ] Confirm: add 3 updates inline, confidence timeline updates without page reload

---

## Phase 4 — Outcomes
**Goal**: Record execution outcomes and close the decision loop.

- [ ] Create `routers/outcomes.py`
- [ ] Create `templates/outcomes/new.html` — outcome form
- [ ] Create `templates/outcomes/detail.html` — outcome + post-mortem view
- [ ] On POST outcome: write to `outcomes` collection, update decision `status` to `executed`, denormalize `final_confidence`
- [ ] Show outcome section on detail page if `status == executed`; show "Record Outcome" button if open
- [ ] Block editing executed decisions (server-side 403 + hide Edit link in template)
- [ ] Register outcomes router in `main.py`
- [ ] Confirm full lifecycle: create → update → record outcome → view post-mortem

---

## Phase 5 — Analytics
**Goal**: Calibration table, bias flags, pre-mortem patterns.

- [ ] Create `routers/analytics.py`
- [ ] Implement Brier score + calibration bucket table
- [ ] Implement bias flags: low update frequency, overconfidence, anchoring, confidence drift
- [ ] Implement pre-mortem word frequency (pure Python, no NLP library)
- [ ] Create `templates/analytics/dashboard.html` — three HTMX-loaded sections
- [ ] Create `templates/analytics/_calibration.html` — calibration table partial
- [ ] Create `templates/analytics/_bias_flags.html` — bias flag cards partial
- [ ] Add Analytics link to nav in `base.html`
- [ ] Register analytics router in `main.py`
- [ ] Confirm analytics load with real data from at least one completed decision

---

## Phase 6 — Polish & Hardening
**Goal**: Auth, error handling, UX improvements.

- [ ] Add Identity-Aware Proxy (IAP) — add setup steps to `GCP_SETUP.md`
- [ ] Add FastAPI exception handlers for 404 and 500 with Jinja2 error templates
- [ ] Add HTML5 form validation (`required`, `min`/`max` on confidence)
- [ ] Add HTMX form error partials (return 422 with `#form-errors` swap)
- [ ] Add `humanize` Jinja2 filter for relative timestamps ("3 days ago")
- [ ] Add Firestore composite indexes as needed, commit `firestore.indexes.json`
- [ ] Add tag filtering on dashboard (`?tag=xyz`)

---

## File Structure (Target)

```
main.py
models.py
db.py
routers/
  decisions.py
  updates.py
  outcomes.py
  analytics.py
templates/
  base.html
  index.html
  decisions/
    new.html
    detail.html
    edit.html
  updates/
    _update_item.html
    _update_form.html
  outcomes/
    new.html
    detail.html
  analytics/
    dashboard.html
    _calibration.html
    _bias_flags.html
requirements.txt
Dockerfile
cloudbuild.yaml
GCP_SETUP.md
PLAN.md
```

---

## New Dependencies
```
google-cloud-firestore==2.19.0
pydantic==2.9.2
```
