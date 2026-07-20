# Deploying the KARNADHAR war-room to Google Cloud Run

The UI is self-contained: it serves the pre-exported `frontend/public/karnadhar.json`
and needs **no database, no API keys, no backend** at runtime. It ships with a
tested multi-stage **Dockerfile** (Next.js standalone output), so the Cloud Run
deploy is deterministic — verified locally: home page 200, data served, `/api/snap`
correctly 404s in production.

> **Deploy target: Google Cloud Run** (your choice). Vercel remains a 5-minute
> fallback — see the bottom of this file.

---

## Step 0 — one-time local check (30 seconds, optional but reassuring)
```bash
cd karnadhar
python export_ui.py            # refresh the data the UI serves
cd frontend
npm run build                  # must end "✓ Compiled successfully"
```
(The Dockerfile does exactly this in the cloud; if the build is clean, the deploy is clean.)

---

## Step 1 — install the gcloud CLI (one time)
Download **Google Cloud CLI** for Windows and run the installer:
https://cloud.google.com/sdk/docs/install  → tick "Run gcloud init" at the end.
Verify in a **new** terminal:
```bash
gcloud --version
```

## Step 2 — create a project + turn on billing (one time)
1. Go to https://console.cloud.google.com → project picker → **New Project** →
   name it `karnadhar` → Create.
2. **Billing**: Billing → link a card. Cloud Run's free tier (2M requests/month)
   easily covers a demo; an always-idle service costs ~₹0.
3. Note your **Project ID** (looks like `karnadhar-472310`, shown under the project name).

## Step 3 — point gcloud at the project & enable the APIs (one time)
```bash
gcloud auth login                       # opens your browser to sign in
gcloud config set project <YOUR_PROJECT_ID>
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

## Step 4 — DEPLOY (this is the whole thing)
```bash
cd karnadhar/frontend
gcloud run deploy karnadhar --source . --region asia-south1 --allow-unauthenticated
```
- `--source .` → Cloud Build sees the **Dockerfile** and builds the image for you.
- `asia-south1` = Mumbai (lowest latency for Indian judges).
- `--allow-unauthenticated` → the URL is public, no login wall for judges.
- First run takes ~4–6 minutes (it builds the container). Answer **Y** if it asks
  to create an Artifact Registry repo.

When it finishes it prints:
```
Service URL: https://karnadhar-xxxxxxxxxx-el.a.run.app
```
**That is your live link.** Open it — you should see the globe war-room.

## Step 5 — put the link where it counts
- **Unstop** submission form (the deliverable link).
- **GitHub** → repo **About ⚙️** → Website field.
- The deck's closing slide, if you have a minute.

---

## Updating the data or UI later
Re-export and redeploy — same one command:
```bash
cd karnadhar && python export_ui.py
cd frontend && gcloud run deploy karnadhar --source . --region asia-south1 --allow-unauthenticated
```
Cloud Run keeps the **same URL** across redeploys.

## Troubleshooting (fast answers)
| Symptom | Fix |
|---|---|
| `gcloud: command not found` | Open a **new** terminal after installing; re-run `gcloud --version`. |
| Prompt to enable an API | Answer **Y** — or re-run the Step 3 `services enable` line. |
| Build fails on `npm ci` | You edited deps but didn't commit `package-lock.json`; run `npm install` in `frontend/` first, then redeploy. |
| Page loads but map is blank | Hard-refresh (Ctrl-Shift-R); MapLibre tiles are CDN-loaded and need internet. |
| "billing account required" | Step 2 — link a card; the free tier still won't charge for a demo. |

## Notes
- The dev-only `/api/snap` capture route returns **404 in production** (verified).
- No secrets are in the image: `.dockerignore` excludes `.env*`; the app needs none.
- The `.gcloudignore` keeps the upload lean (node_modules/.next rebuild in the cloud).

---

## Fallback — Vercel (if gcloud gives you trouble on the night)
```bash
cd karnadhar/frontend
npx vercel          # sign in with GitHub → accept defaults
npx vercel --prod   # promotes to the permanent URL
```
You get `https://karnadhar-<hash>.vercel.app`. Same app, 5 minutes, zero config.
(Vercel ignores the Dockerfile and builds Next.js natively — both paths work.)

## Why Cloud Run is the right Google-Cloud story (if a judge asks)
- The value is in **deployment**, not swapping our maritime cartography for Google
  Maps (which routes roads, not sea lanes through Hormuz/Suez/Cape — wrong tool).
- Containerised + standalone = portable and cloud-agnostic: the same image runs on
  Cloud Run, any Kubernetes cluster, or a laptop. That's the production story.
