# CLAUDE.md — project self-report & handoff

> **Read me first.** This file exists so a fresh Claude session (or a new Claude account) can
> pick this project up cold, with zero prior conversation. It says **what this is, why, where it
> stands, how to continue, and the rules that must not be broken.** Keep it current when the
> state changes.
>
> _Last updated: 2026-09-28._

---

## 1. What this project is (in one paragraph)

A software platform that runs **executive incident-response (IR) tabletop exercises** and produces
a **SOC 2‑grade, timestamped evidence report** at the end. It is delivered as a **facilitated
service** (an MSP runs the sessions), co-marketed with a **PR partner** as an
emergency-preparedness package, and sold **direct to the mid-market**. It is a full replacement
for the team's current tooling (Exigence). The differentiation is the **decision layer** and the
**readiness-improvement evidence** — *rehearsing executive judgment under pressure*, not the IT
runbook.

**Planning is complete** (all 40 scoping decisions answered). The current phase is **building the
real app on Lovable + Supabase**, using the local Streamlit app as a working reference prototype.

## 2. Why it exists / who it's for

- The operating company ("**the MSP**" in all docs — see the de-identification note in §6) currently
  runs these tabletops using a competitor tool and wants to own the whole experience and the
  evidence artifact.
- Buyer = mid-market executives (the security decision-maker). The exec is the *participant*, not a
  guest. Value = an auditable readiness trend a manual consultant can't reproduce repeatably.

## 3. Repo map — where everything lives

```
README.md                     Short public-facing intro (repo is PUBLIC — see §6)
CLAUDE.md                     This file
planning/                     The full thinking. Start here to understand decisions.
  00-PROJECT-OVERVIEW.md        Vision, positioning, competitive read, business shape
  01-DECISIONS-LOG.md           All 40 scoping Q&A (S1–S3, Q1–Q40) — the source of truth for "why"
  02-EVIDENCE-REPORT-SPEC.md    The evidence-report / redline deliverable spec
  03-PRODUCT-REQUIREMENTS.md    v1 functional spec, Supabase data model, screen flows, roadmap
  04-REFERENCE-NOTES.md         Distilled notes from the (now-removed) source docs + prior-art
app/                          Local Streamlit REFERENCE PROTOTYPE (Python). Not the ship target.
  Home.py, pages/, irp/         Multi-page Streamlit app: clients, plan+gaps, run exercise, report
  irp/ai.py                     Anthropic calls (gap analysis + closing notes)
  irp/baseline.py               The 16-chapter best-practice IR baseline (gap-analysis target)
  irp/scenarios.py              Seeded scenario inject decks (BEC, ransomware, data breach, insider)
lovable/                     THE BUILD KIT for the real app (React + Supabase via Lovable)
  00-START-HERE.md              How to move from prototype → Lovable. Read before building.
  lovable-prompts.md            Ordered prompts to paste into Lovable, screen by screen
  ai-prompts-and-seed.md        The calibrated AI prompts + baseline + scenario seed ("crown jewels")
  supabase-schema.sql           Real multi-tenant schema with auth + RLS
  edge-functions.md             Server-side edge functions (AI calls + doc extraction)
  scenarios-seed.json           Structured scenario seed data
```

## 4. Current state (as of last update)

- ✅ All **40/40** scoping decisions locked (`planning/01-DECISIONS-LOG.md`).
- ✅ Requirements + Supabase data model drafted (`planning/03-PRODUCT-REQUIREMENTS.md`).
- ✅ Local **Streamlit prototype** works end-to-end (reference only, not the ship target).
- ✅ **Lovable handoff kit** complete (`lovable/`).
- ✅ Repo fully **de-identified** in working tree AND git history (see §6).
- ⏳ **Next up:** build the real app on Lovable + Supabase, in the order in
  `lovable/00-START-HERE.md` → `lovable/lovable-prompts.md`:
  1. Create Lovable project, connect Supabase.
  2. Apply `supabase-schema.sql`.
  3. Add Anthropic key as an **edge-function secret**; create the two edge functions.
  4. Build screens one prompt at a time: auth+tenant switcher → clients → plan & gaps →
     people roster → run exercise console → evidence report.
- 🅿️ Parked business item: data residency / SOC 2 posture (decision Q24).

## 5. How to continue — practical rules

- **Git:** work on `main`. It is the only branch; the old `claude/…` feature branch was retired
  and everything is merged into `main`. Commit with clear messages; push to `main`.
- **Ship target is Lovable, not Streamlit.** Do NOT try to port the `.py` files — Lovable
  generates its own React + Supabase code from the prompts in `lovable/`. The Streamlit app is
  there to show intended behavior.
- **Security architecture that MUST hold:** the Anthropic API key runs **server-side only** (a
  Supabase Edge Function secret). In the prototype the key was in the sidebar — that cannot ship.
  Document text extraction (`pypdf`/`python-docx`) also moves server-side (`unpdf`/`mammoth`) or
  accepts pasted text in v1. See `lovable/edge-functions.md`.
- **The AI prompts are calibrated IP.** The gap-analysis prompt was tuned over several rounds to
  stop over-flagging (it reviews an *executive coordination* doc, not a technical runbook). Hand
  them to Lovable **verbatim** from `lovable/ai-prompts-and-seed.md`.
- **When in doubt about "why," read `planning/01-DECISIONS-LOG.md`** — every choice is recorded
  there with its reasoning.

## 6. ⚠️ Critical: this repo is PUBLIC and de-identified — keep it that way

- **The repo is intentionally public** so Lovable can read/import it. Assume anything committed
  here is world-visible.
- **All real identities were deliberately removed** and replaced with **generic role/type labels**.
  These placeholders are intentional — **do not "restore" real names, and do not add new PII**
  (real people, client names, vendor names, addresses, contact details) to any tracked file.
  The standard placeholders in use:

  | Placeholder | Means |
  |---|---|
  | **the MSP** | the operating company / first user |
  | **the PR partner** | the co-marketing PR firm |
  | **the CTO / the owner** | the product owner / lead |
  | role labels (CEO, CFO, VP…, a senior engineer) | the real people from the sample roster |
  | vendor *types* (a cyber insurer, breach counsel, an IR firm, a DR provider, an ISP…) | the MSP's real named vendors |
  | the holding company | the parent company |
  | `Acme Corp` | placeholder client name in UI examples |

- **Removed from the repo entirely** (working tree *and* history, via `git filter-repo`): the real
  IR/BCP policy PDFs, a competitor's sample post-incident report, and competitor marketing PDFs.
  Don't expect them to be present and don't re-add them. Their reusable, de-identified substance
  lives in `planning/04-REFERENCE-NOTES.md`. `.gitignore` blocks `*.pdf`, `*.docx`, `*.xlsx`,
  `app/data/`, and local DB files so they can't be committed by accident.
- **History was rewritten twice** (doc purge, then name scrub) and force-pushed. Consequence: any
  clone taken before that still holds the old PII, and if the repo was public earlier with the
  originals, that exposure already happened — treat it as such. **Forks** would retain the old
  history; worth checking if privacy matters.
- **Environment gotcha:** deleting a remote branch through the git proxy returns **HTTP 403**
  (blocked). Branch deletion must be done from the GitHub UI. Pushes work fine.
- **Never commit secrets** (Anthropic key, Supabase keys). Use `app/.env.example` as the template
  locally and Supabase Edge Function secrets in production.

## 7. Glossary / prior art

- **Exigence** — the incumbent tool being replaced (practitioner/IT war-room platform).
- **Field Effect** — a human-led tabletop *service*; high fidelity but doesn't scale.
- **BEC** — Business Email Compromise (the flagship launch scenario).
- **Evidence report** — the timestamped, auditable output that proves the exercise happened and
  what was decided; plus a **redline punch-list** of plan changes needed.
- **Baseline** — the 16 best-practice IR chapters the ingested client plan is gap-analyzed against.
