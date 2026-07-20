# Deploying the KARNADHAR war-room (live URL for judges)

The UI is self-contained: it serves `frontend/public/karnadhar.json` (pre-exported
from the engine) and needs **no database, no API keys, no backend** at runtime.
That makes deployment trivial. Two good paths — pick ONE.

> Before either path, regenerate the data and test a production build locally:
> ```bash
> cd karnadhar
> python export_ui.py
> cd frontend
> npm run build        # must finish clean
> npm start            # test at http://localhost:3000, then Ctrl-C
> ```

---

> **User's choice: Google Cloud Run (Path B).** Production build verified clean
> (`npm run build` passes; static page + guarded /api/snap). A `.gcloudignore` is in
> place so source uploads stay lean. Vercel (Path A) remains the quick fallback.

## Path A — Vercel (fastest: ~5 minutes, free, made for Next.js)
1. Create a free account at vercel.com (sign in with GitHub).
2. ```bash
   cd karnadhar/frontend
   npx vercel            # login → accept defaults → deploys
   npx vercel --prod     # promotes to the permanent URL
   ```
3. You get `https://karnadhar-<something>.vercel.app` — put it in the Unstop form
   and the README.

## Path B — Google Cloud Run (if you want the GCP story; ~30 min first time)
1. console.cloud.google.com → new project `karnadhar` → enable billing
   (free tier covers this easily) → enable **Cloud Run** + **Cloud Build** APIs.
2. Install the gcloud CLI, then:
   ```bash
   gcloud auth login
   gcloud config set project <YOUR_PROJECT_ID>
   cd karnadhar/frontend
   gcloud run deploy karnadhar --source . --region asia-south1 --allow-unauthenticated
   ```
   (Cloud Run's buildpacks detect Next.js automatically; `asia-south1` = Mumbai.)
3. It prints `https://karnadhar-<hash>-el.a.run.app` — that's your live URL.

## Notes
- The dev-only `/api/snap` capture route returns 404 in production (guarded).
- To refresh deployed data later: `python export_ui.py` → redeploy.
- Add the live URL to: Unstop form, GitHub README top, and the deck's closing slide
  if you have time (optional).

## Why NOT Google Maps JS / Directions API (if a judge asks)
- Directions API routes **roads**; our corridors are **maritime** (Hormuz, Suez,
  Cape) — Google has no sea routing, so it's the wrong tool for the domain.
- Maps JS needs a billed, exposed API key and would replace the free MapLibre
  cartography that already carries the war-room aesthetic, adding no analytical value.
- Cloud value comes from **deployment** (Cloud Run) — that IS the Google Cloud story.
