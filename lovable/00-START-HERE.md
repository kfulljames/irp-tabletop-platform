# Moving the IRP Tabletop prototype to Lovable

This folder is the **handoff kit**. Lovable does not import code — it generates its own
React + Supabase app from prompts. So you don't paste the Streamlit `.py` files in. You give
Lovable a build brief plus the three things it can't reinvent on its own:

1. **The data model** → `supabase-schema.sql` (real multi-tenant, with auth + RLS — the thing
   the local prototype deliberately skipped per decision B0).
2. **The calibrated AI prompts** → `ai-prompts-and-seed.md`. These are the crown jewels. The
   gap-analysis system prompt took several rounds to stop it over-flagging (executive
   coordination doc, NOT a technical runbook). Hand them over verbatim.
3. **The scenario content + baseline** → also in `ai-prompts-and-seed.md` (the BEC inject deck,
   the 16 baseline chapters, the task library). This is product IP, not boilerplate.

## The one architectural change you MUST make vs. the prototype

In Streamlit, the Anthropic API key lived in the sidebar and calls went straight from the app.
**That cannot ship.** In Lovable, the API key is a **Supabase Edge Function secret**, and the
two AI calls (`analyze-plan`, `closing-notes`) run server-side in edge functions. The browser
never sees the key. Same for **document text extraction** — `pypdf`/`python-docx` don't port;
do extraction in an edge function (e.g. `unpdf` for PDF, `mammoth` for .docx) or accept pasted
text in v1. See `edge-functions.md`.

## Recommended order (do NOT one-shot this)

Lovable builds best incrementally. Connect Supabase first, lay the schema, then build screen by
screen, testing each before moving on. The exact prompts to paste are in `lovable-prompts.md`,
in order:

1. Create the Lovable project, **connect Supabase** (Lovable has a native Supabase integration).
2. Run `supabase-schema.sql` in the Supabase SQL editor (or paste it and let Lovable apply it).
3. Add Anthropic key as an edge-function secret; create the two edge functions.
4. Build screens in this order — each is a separate prompt:
   - Auth + org/tenant switcher (the sticky tenant context — this is the "don't upload to the
     wrong tenant" guardrail from the prototype, now enforced by RLS, not just a green bar).
   - Clients (tenant) CRUD.
   - Plan & Gaps (multi-doc upload → AI gap analysis → accept/dismiss → punch-list).
   - People roster.
   - Run Exercise (the live console — this is where Lovable finally gives you the real floating
     inject card and the true full-height task column Streamlit couldn't).
   - Evidence Report (assemble → AI closing notes → approve gate → export).

## What finally gets fixed in Lovable (the Streamlit ceilings)

- The inject becomes a **real floating, minimizable card** (position:fixed overlay) that stays
  open while you type into the timeline below.
- The incident-task panel becomes a **true full-height right column**, flush to the viewport.
- Real **auth + multi-user + RLS** instead of single-local-facilitator.
- A clean **design system** (shadcn/ui + Tailwind) instead of fighting Streamlit's chrome.

## Map: prototype file → where its logic goes in Lovable

| Prototype (`app/...`)            | Lovable home                                              |
|----------------------------------|----------------------------------------------------------|
| `irp/db.py` (SQLite schema)      | `supabase-schema.sql` (Postgres + RLS)                   |
| `irp/ai.py` (prompts + calls)    | Supabase Edge Functions `analyze-plan`, `closing-notes`  |
| `irp/baseline.py`                | seed data / constant in `ai-prompts-and-seed.md`         |
| `irp/scenarios.py`               | `scenario` + `inject` tables, seeded (see schema + seed) |
| `irp/report.py` (docx/json)      | client-side export (e.g. `docx` npm pkg) or edge function|
| `irp/pdfutil.py`                 | edge-function text extraction (`unpdf`)                  |
| `pages/*.py`                     | React routes/screens (prompts in `lovable-prompts.md`)   |

Start with `lovable-prompts.md`.
