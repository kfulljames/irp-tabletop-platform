# Product Requirements — v1 (Tabletop)

_Reflects all 40 scoping decisions + build round B0–B15 (`01-DECISIONS-LOG.md`). Written against
the **Lovable + Supabase** stack (B0). v1 = tabletop exercises; v2 = real incident management
(Q21). Last updated 2026-06-25._

> **MVP definition (Q40):** one full end-to-end engagement on the multi-tenant core —
> ingest plan → setup wizard → run a seeded scenario (act-as + live clock + observers) →
> capture decisions/notes/EOS vote → AI gap review → export evidence (PDF/Word) + redline
> punch-list. Facilitator approves before anything exports (B12).

---

## 1. Scope & non-goals

**In scope (v1):**
- Multi-tenant core (facilitator workspace → client orgs), the MSP as the first/only workspace in use.
- Plan ingestion + AI pre-gap analysis against a single global baseline.
- Setup wizard (people, general data-access map, third-party directory, tech basics).
- One **fully seeded scenario (BEC)**, with Ransomware + Data-breach decks scaffolded (B14).
- Live run: linear inject deck, act-as attribution, real running clock, observers, typed capture,
  live remote participant view.
- Close: debrief, on-device EOS vote, gap validation.
- Evidence report (PDF + Word + structured export) with facilitator approval gate.
- Plan-change **punch-list** output (B5).
- Action-item tracking + a basic readiness trend across repeat runs.

**Explicitly deferred (fast-follow or v2):**
- Tracked-changes redline rendering (post-v1; data captured now — B5).
- Full white-label theming (Q36 — v1 ships the MSP/the PR partner co-brand; theming Phase 2, Q-D4).
- Automated cadence/reminders (Q29).
- Two-way ControlMap sync (Q28), SMS/WhatsApp (Q39), real-incident mode (Q21), searchable
  incident knowledge base — all **v2**.

**Non-goals (any version):** branching scenario engine (Q12); the tool drafting/sending the
actual victim/attacker/press communications (Q13 — capture decisions only); folder-level data
mapping (Q10 — general access only).

---

## 2. Architecture & stack (B0)

> **v1 is a local prototype (revised B0).** v1 runs locally on the CTO's machine as the **simplest
> prototype** that proves the core value flow; the Lovable + Supabase build below is the
> **productization target**, reached via a deliberate rewrite — not built now. The data model
> (§4) and roles (§3) describe the *target*; the prototype collapses them (single local
> facilitator, no auth, local SQLite/files, no remote participant view — see B0 in the decisions
> log). Everything else (typed capture, clock, gap analysis, punch-list, EOS vote, evidence
> export) is in the prototype.

**Productization target (Lovable + Supabase):**
- **Lovable** — app build + hosting; built-in **magic-link auth** (Q17).
- **Supabase** — Postgres (data model §4), Auth (magic link + multi-email per user, Q39),
  Storage (uploaded plan PDFs, exported reports), Row-Level Security for tenant isolation (Q16/B1).
- **Out-of-band auth fallback** (Q17/Q39): every user has ≥1 alternate email (personal) so a
  downed work inbox doesn't block magic-link sign-in. _(v1 = multi-email; SMS/WhatsApp = v2.)_

**Both prototype and target:**
- **Anthropic API (Claude, latest)** — gap analysis, closing-notes, punch-list suggestions;
  **suggest-only, human-approved** (B15); no training on customer data.

---

## 3. Roles & access (B2)

| Role | Scope | Can |
|---|---|---|
| **Facilitator** | Facilitator workspace | Full control; create client orgs; run sessions; act-as; own/sign-off all data (B6); approve/export reports (B12) |
| **Client Admin** | One client org | Create/edit own org's people, plans, contacts, tech basics (facilitator retains ownership, B6) |
| **Participant** | One run | Light live view: current inject, their act-as prompts, submit own EOS vote (Q38/B11/B13) |
| **Observer** | One run | Read-only presence; appears in evidence attendance (Q19) |

Tenant isolation: a facilitator workspace sees across **its own** client orgs only; client orgs
are isolated from each other (B1). Enforced via Supabase RLS on `workspace_id` / `client_org_id`.

---

## 4. Data model (Supabase / Postgres)

_Core tables. `*` = tenant-scoping column for RLS._

**Tenancy & identity**
- `facilitator_workspace` (id, name, branding_config jsonb)
- `app_user` (id, full_name, primary_email)
- `user_email` (id, user_id→app_user, email, kind `work|personal|other`, is_primary) — multi-email (Q39)
- `workspace_member` (workspace_id*, user_id, role `facilitator`)
- `client_org` (id, workspace_id*, name, industry, branding_config jsonb)
- `org_membership` (client_org_id*, user_id, role `client_admin|participant|observer`)

**Client roster & context (setup wizard, Q10)**
- `person` (id, client_org_id*, full_name, title, department, is_alternate, alternate_for→person,
  user_id→app_user nullable) — named employees for personalization; links to an auth user if they log in
- `person_access_tag` (person_id, tag) — general data/asset access ("finance: payroll", Q9/Q10)
- `third_party_contact` (id, client_org_id*, category, org_name, contact_name, phone, email,
  notes, alternate_contact) — directory mirrors BCP schema (Q31)
- `tech_basics` (client_org_id*, key, value) — environment basics, non-technical (Q10)

**Plans, baseline, gaps**
- `baseline_chapter` (id, key, title, guidance) — **global** canonical best-practice chapters (B4)
- `plan` (id, client_org_id*, kind `IRP|BCP`, source_filename, storage_path, version, uploaded_at)
- `plan_section` (id, plan_id, baseline_chapter_key, title, original_text, current_text) — canonical
  map + original text preserved (B3)
- `gap_finding` (id, client_org_id*, plan_id, baseline_chapter_key nullable, plan_section_id nullable,
  description, recommended_change, severity, status `ai_suggested|validated|dismissed`,
  source `ai|room`, owner_person_id, run_id nullable) — pre-gap (Q8) + validated in-run

**Scenario & content**
- `scenario` (id, workspace_id* nullable=global-seed, kind `BEC|Ransomware|DataBreach|...`, title,
  overview_schema jsonb) — per-type Overview fields (report spec §3)
- `inject` (id, scenario_id, order_index, title, room_content, facilitator_guidance nullable,
  category, capture_prompt jsonb) — optional teleprompter (B8); linear order (Q12)
- `inject_role_slot` (inject_id, slot_key, role_hint) — e.g. "the CFO"; resolved per run (B7)
- `task_template` (id, scenario_id nullable=library, title, guidance, phase, default_status) — reusable (Q33)

**Runs (engagements/sessions)**
- `run` (id, client_org_id*, scenario_id, facilitator_id, status `scheduled|running|complete`,
  scheduled_for, started_at, resolved_at) — real clock (B10); one run = one session (Q-D1)
- `run_role_slot_binding` (run_id, slot_key, person_id) — named-people personalization (B7)
- `run_participant` (run_id, person_id, role `participant|observer`, is_remote, joined_at) (B11)
- `run_role_assignment` (run_id, person_id, incident_role, assigned_at, ended_at) — role history (Q34)
- `run_inject_state` (run_id, inject_id, status `pending|revealed|skipped`, revealed_at) (Q11/Q12)

**Capture (typed timeline, B9)**
- `timeline_event` (id, run_id, type, description, acting_person_id `act-as` (Q6),
  created_by_user_id, occurred_at, payload jsonb)
  - types: `IncidentStart | Invitation | Team | OverviewUpdate | StatusUpdate | BusinessDecision
    | CommsDecision | Task | Note | Resolution` (mirrors report spec §6)
  - `CommsDecision` payload: who/what/when/how/reasoning (Q13)
  - `Task` payload: assigned_to_person, assigned_by, status, reported_back_text (Q10)
  - `Note` payload: plan_section_id?, proposed change → spawns a `change_item`
- `change_item` (id, run_id, client_org_id*, plan_section_id nullable, description,
  recommended_change, severity, owner_person_id, status) — **the punch-list** (B5)
- `vote` (run_id, person_id, score int 1–10, submitted_at) — on-device, named (Q30/B13)
- `debrief` (run_id, went_right, went_wrong, can_improve, postmortem jsonb) — optional 7-part
  structure (report spec §2)

**Output & follow-through**
- `report` (id, run_id, status `draft|approved|exported`, approved_by_user_id, approved_at,
  exports jsonb `{pdf,docx,structured}`) — approval gate (B12)
- `action_item` (id, client_org_id*, origin_run_id, description, owner_person_id, due_date,
  status `open|in_progress|closed`, closed_at) — tracked to closure across engagements (Q27/E3)

---

## 5. Functional requirements by area

### A. Onboarding & setup
- **A1** Facilitator creates a client org under the workspace (B1).
- **A2** Upload IRP/BCP PDF → Supabase Storage (Q7).
- **A3** AI parses the plan into `plan_section` rows mapped to `baseline_chapter` keys, preserving
  original text; unmapped/missing chapters flagged (B3).
- **A4** AI pre-gap analysis vs the global baseline → `gap_finding` rows (`ai_suggested`) (Q8).
- **A5** Setup wizard (multi-contributor, facilitator-owned, B6): people + roles, access tags,
  third-party directory, tech basics (Q10). Client Admin may pre-fill.

### B. Scenario & content
- **B1** Three launch scenarios (BEC fully seeded; Ransomware + Data-breach scaffolded) (Q9/B14).
- **B2** Injects = linear deck, optional facilitator guidance, role-slots (B7/B8/Q12).
- **B3** Role-slots auto-bind to the org's named people at run prep; facilitator can override (B7).
- **B4** In-app scenario/inject authoring (Q25); Claude drafts seed, the CTO + the PR partner refine (B14).
- **B5** Reusable task/playbook library, grouped by phase/status (Q32/Q33).

### C. Live run
- **C1** Facilitator console: deck control (reveal/skip/reorder), teleprompter pane, capture panel,
  running clock, **act-as selector**, live timeline (Q6/Q11/Q12/B10).
- **C2** Presenter/projector view (shared screen) + **live remote participant view** via magic link
  (current inject, their prompts, vote) (Q35/Q38/B11).
- **C3** Typed capture (BusinessDecision / CommsDecision / Task / StatusUpdate / Note) — each act-as
  attributed + timestamped (B9/Q6/Q13).
- **C4** Incident roles + logged role changes (Q34); observers present (Q19).
- **C5** Technical tasks "assigned out," tech team reports back (logged) (Q10).

### D. Close & evidence
- **D1** Debrief capture: went right / wrong / improve (+ optional 7-part post-mortem) (report spec §2).
- **D2** On-device EOS vote, 1–10, named, act-as fallback (Q30/B13).
- **D3** Gap validation: confirm/expand AI pre-gaps live; notes spawn `change_item`s (Q8/B5).
- **D4** Evidence report assembled at close: system-filled factual sections + AI-drafted narrative;
  **facilitator reviews/approves before export** (B12/Q23).
- **D5** Exports: PDF (primary) + Word + structured JSON/CSV (Q22).
- **D6** Punch-list of plan changes (redline render deferred, B5).

### E. Readiness over time (the wedge, S3)
- **E1** Plan-change count + severity per engagement (Q7).
- **E2** Action-item tracking to closure, carried across runs (Q27).
- **E3** Basic readiness trend across repeat runs per client (gap/action volume + vote trend).

### F. Platform
- **F1** Magic-link auth + multi-email fallback (Q17/Q39/B0).
- **F2** Tenant isolation via RLS (Q16/B1).
- **F3** Branding config per workspace/org (co-brand v1; full white-label fast-follow, Q36).
- **F4** Data residency / SOC 2 posture — **parked (Q24)**; Anthropic-API no-train as partial hook (B15).

---

## 6. Screen / flow map

**Facilitator (desktop):**
1. Workspace dashboard — clients, runs (scheduled/running/complete).
2. Client org — roster, plans, contacts, run history, **readiness trend**.
3. Setup wizard — 4 steps (people · access map · directory · tech basics).
4. Plan & gaps — ingested sections + AI gap list to review/accept.
5. Scenario library / inject authoring.
6. Run prep — pick scenario, bind role-slots → people, invite participants.
7. **Live run console** — deck + teleprompter + capture + clock + act-as + timeline.
8. Presenter view — projector-friendly shared screen.
9. Close — debrief, vote status, gap validation.
10. Report — review → approve → export.

**Participant / Observer (mobile, magic link):**
- Live session view — current inject, "you are acting as…" prompts, submit vote (participant);
  read-only (observer).

---

## 7. Phased roadmap

**Phase 0 — Deliver with thin tooling (now, in parallel):** keep running real engagements off the
slide/inject deck + report template to fund and shape the build (BEC alone suffices).

**Phase 1 — v1 MVP (the §Scope build):** multi-tenant core (the MSP workspace), plan ingest + AI
gap, setup wizard, BEC scenario fully + 2 scaffolded, live run (act-as / clock / observers / typed
capture / remote view), close (debrief / vote / gap validation), evidence PDF+Word+structured with
approval gate, punch-list, action tracking + basic trend.

**Phase 2 — v1 fast-follow:** Ransomware + Data-breach decks; tracked-changes redline render; full
white-label theming; in-app authoring polish; richer trend dashboard; automated cadence/reminders.

**Phase 3 — v2 (real incident management):** live-incident mode; plan + directory offline
availability; SMS/WhatsApp incident notifications; two-way ControlMap sync; searchable incident/
exercise knowledge base; the holding company portfolio rollout.

---

## 8. Resolved (drafting questions Q-D1–Q-D4, 2026-06-25)

- **Q-D1 — Run = single session.** One `run` = one session. Repeat engagements over time are new
  runs against the same client org; the readiness trend strings them together. (Multi-session
  containers not needed in v1.)
- **Q-D2 — Roster-first invite.** Participants must exist as `person` roster records (from the
  setup wizard) before a run; the magic link invites a known roster person. Keeps act-as
  attribution + evidence clean. No open self-join in v1.
- **Q-D3 — Facilitator-delivered only.** Clients receive the exported report file; no client
  login to evidence/trend in v1 (Client Admins can still pre-fill setup data). Client portal = later.
- **Q-D4 — Co-brand v1, theming Phase 2.** MVP ships a fixed the MSP/the PR partner co-brand; the full
  white-label theming engine (Q36) is Phase 2. `branding_config` columns exist now so theming
  drops in without a schema change.
