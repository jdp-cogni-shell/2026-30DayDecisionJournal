# GCP Setup Instructions

Replace the placeholder values before running each command.

## Your Project Details

| Variable | Value |
|---|---|
| `YOUR_PROJECT_ID` | _(e.g. `decision-journal-2026`)_ |
| `BILLING_ACCOUNT_ID` | _(run step 2a to find this)_ |

---

## Prerequisites

Open the VS Code terminal (`Ctrl+`` `) and check gcloud is installed:
```bash
gcloud --version
```

If not installed: https://cloud.google.com/sdk/docs/install

Authenticate:
```bash
gcloud auth login
```

---

## 1. Create and configure the project

```bash
gcloud projects create YOUR_PROJECT_ID --name="30 Day Decision Journal"
gcloud config set project YOUR_PROJECT_ID
```

---

## 2. Link billing

```bash
# 2a. List billing accounts to find your BILLING_ACCOUNT_ID
gcloud billing accounts list

# 2b. Link billing
gcloud billing projects link YOUR_PROJECT_ID --billing-account=BILLING_ACCOUNT_ID
```

---

## 3. Enable required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

---

## 4. Create Artifact Registry repository

```bash
gcloud artifacts repositories create decision-journal \
  --repository-format=docker \
  --location=us-central1 \
  --description="Decision Journal container images"
```

---

## 5. Grant Cloud Build permission to deploy to Cloud Run

```bash
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format='value(projectNumber)')

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud iam service-accounts add-iam-policy-binding \
  ${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

---

## 6. Connect Cloud Build to GitHub

> **Note:** First-time GitHub connection must be done via the GCP Console at
> **Cloud Build > Repositories** before this command will work.

```bash
gcloud builds triggers create github \
  --repo-name=2026-30DayDecisionJournal \
  --repo-owner=jdp-cogni-shell \
  --branch-pattern="^master$" \
  --build-config=cloudbuild.yaml \
  --substitutions=_REGION=us-central1,_REPO=decision-journal,_SERVICE=decision-journal
```

---

## 7. Trigger first deploy manually

```bash
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_REGION=us-central1,_REPO=decision-journal,_SERVICE=decision-journal
```

After this completes, Cloud Build will print a Cloud Run URL like:
`https://decision-journal-xxxx-uc.a.run.app`

Every push to `master` will auto-deploy from this point on.
