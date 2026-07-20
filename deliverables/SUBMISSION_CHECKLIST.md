# Phase-2 Submission Checklist — deadline 22 July 2026 (confirmed in workshop)

> Workshop Q&A confirmations (18 Jul): public GitHub URL is the submission format ·
> evaluation = the brief's rubric ("refer to the brief") · laptop-run prototypes are
> fully acceptable — cloud deployment earns no extra points (Vercel step = optional
> convenience) · synthetic data allowed for others, we exceed with real DGCIS records ·
> support email: anil.kumar…@timesinternet.in (exact id in the meeting chat).

## A. GitHub (public)
- [ ] `cd karnadhar && git init && git add -A && git status`  ← **review the file list**
- [ ] CONFIRM `.env` is NOT in the list (it's git-ignored; contains the aisstream key)
- [ ] CONFIRM `node_modules/` absent (root + frontend), engine caches absent
- [ ] `git commit -m "KARNADHAR — ET AI Hackathon 2026 Phase 2"`
- [ ] Create **public** repo `karnadhar` on github.com → push
- [ ] Open the repo in an incognito window: README renders, no secrets, code visible

## A2. Live deployment (strongly recommended — judges click, don't clone)
- [ ] Follow `DEPLOY.md` (Vercel ~5 min, or Google Cloud Run for the GCP story)
- [ ] Test the live URL in incognito; put it in the Unstop form AND at the top of README

## B. Demo video
- [ ] Record per `DEMO_SCRIPT.md` (~3 min)
- [ ] Upload to YouTube → set **Public** (rules: "all files and links must be public")
- [ ] Test the link in incognito

## C. Deck
- [ ] `deliverables/KARNADHAR_Deck.pptx` — export to PDF too (File → Save As → PDF)
- [ ] If the form wants a link: upload PDF to Google Drive → "Anyone with the link"

## D. Unstop form (submit EARLY — by 21 July evening, not the last hour)
- [ ] Working prototype link → GitHub repo URL (README explains 2-command run)
- [ ] Pitch deck → PDF upload or Drive link
- [ ] Demo video → YouTube link
- [ ] Architecture diagram → it's inside the deck (slide 4) + repo README; attach
      `deliverables/renders/Slide4.PNG` if a separate image is required
- [ ] Re-open the submission after saving to verify every link works logged-out

## E. Post-submission (optional, high value)
- [ ] Email Prof. Bhui the written questions + Russian-crude table (draft in chat)
- [ ] Thank-you note to Lydia Powell with the deck attached — permission to credit
- [ ] Rotate the aisstream API key (it appeared in a chat transcript)
