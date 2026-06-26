# Lovable build prompts (paste in order)

Work top to bottom. After each prompt, **test it before moving on** — Lovable degrades when you
pile features into one prompt. When a screen references data shapes, point Lovable at
`supabase-schema.sql`. Keep `ai-prompts-and-seed.md` open for the verbatim prompt text.

---

### Prompt 0 — project + design system

```
Build an internal web app called "IRP Tabletop Platform" for running executive incident-response
tabletop exercises and producing SOC 2-grade evidence reports. It's a facilitation tool used by a
managed-service provider (the MSP) to run a live exercise with a client's leadership
team, then export an evidence report.

Use a clean, professional dark UI with shadcn/ui + Tailwind. Calm, enterprise feel — not playful.
A persistent left nav with: Clients, Plan & Gaps, People, Run Exercise, Evidence Report. A
persistent top bar that always shows the currently selected CLIENT (tenant) in a colored chip —
this is a safety guardrail so the facilitator never works in the wrong client's data. Set up
routing for those five pages as empty placeholders for now.
```

### Prompt 1 — connect Supabase + schema

Use Lovable's native Supabase integration to connect a project, then:

```
Connect Supabase. Apply the schema in supabase-schema.sql exactly (tables, RLS policies, and the
new-user trigger). This app is multi-tenant: a facilitator (auth user) belongs to a workspace and
works across many client_orgs under it. All data access must go through the RLS policies in that
file. After applying, seed the scenario library from scenarios-seed.json (four scenarios: BEC,
Ransomware, Data Breach, Insider Threat — each with its injects and tasks) and the baseline
chapters / UI constants from ai-prompts-and-seed.md §3–4. Insert all scenarios, their injects,
and their scenario_tasks as global seed rows with workspace_id null.
```

### Prompt 2 — auth + tenant context

```
Add email/password auth (Supabase). On first sign-in, create the user's profile (the trigger
handles this) and, if they belong to no workspace, prompt them to create one (becomes owner).
Add a client (tenant) switcher in the top bar that lists client_orgs in the current workspace and
stores the selection; every page operates on the selected client. Show the selected client name
in the colored top-bar chip on every screen.
```

### Prompt 3 — Clients page

```
Build the Clients page: list client_orgs in the workspace (name, industry, created date) as
cards. Add/edit/delete a client (name + industry). Selecting a card sets it as the active client
in the top-bar chip. This is CRUD over the client_org table.
```

### Prompt 4 — People page

```
Build the People page for the active client: a roster of person rows (full_name, title,
incident_role). incident_role is a select from: Incident Commander, Executive Sponsor (CEO),
Comms Lead, Tech Lead, Finance Lead, Legal / Counsel Liaison, Client Experience Lead, Observer,
Other (free text allowed). Add/edit/delete people. These are the real participants used later for
attribution during a run.
```

### Prompt 5 — Plan & Gaps page

```
Build the Plan & Gaps page for the active client.
1. Multi-document upload: drag-and-drop one or more files (PDF/DOCX). On drop, immediately upload
   to Supabase Storage and call the extract-text edge function to fill document.full_text. Show
   each as a card with an editable label dropdown (Policy / Procedure / IRP / BCP) and a delete
   button. Also offer a "paste plan text" fallback that writes full_text directly.
2. "Run AI gap analysis" button calls the analyze-plan edge function over ALL the client's
   documents together. While running, show progress.
3. Render the results as the punch-list: one row per gap_finding (severity badge, title,
   description, recommended change) with Accept and Dismiss actions. Accept sets status=validated
   and collapses the row to green; Dismiss sets status=dismissed and collapses to red/grey.
   Only validated gaps flow into the evidence report.
```

### Prompt 6 — Run Exercise (the live console) — build in two passes

Pass A (structure):

```
Build the Run Exercise page for the active client. Two states:

START: if no running run exists, show a setup form — pick a scenario (BEC, Ransomware, Data
Breach, or Insider Threat), choose participants
(multi-select from People, acting on their own behalf) and observers, pick a timezone (default
America/Vancouver; all run timestamps use it). "Start exercise" creates a run (status=running),
adds run_participants, seeds run_task rows from the scenario's scenario_task list, and logs an
"Incident start" timeline_event.

LIVE CONSOLE (run is running): a two-column layout.
- A thin phase tracker across the top: chips for Detection, Investigation, Containment,
  Communication, Legal/Regulatory, Recovery. Highlight the phase mapped from the current inject's
  category (Detection→Detection, Escalation→Investigation, Decision→Containment,
  Comms→Communication, Containment→Containment, Legal→Legal/Regulatory, Recovery→Recovery).
- Directly under the chips: Prev / Next inject controls. Next advances current_inject and logs an
  "Inject" timeline_event.
- LEFT column (main): a collapsible structured Overview form (latest_status, detection_summary,
  how/when/who discovered, impacted, history; an Impact-to-Business block with rating
  None/Low/Medium/High + explanation for Operational, PR / Reputation, Legal / Regulatory,
  Financial; and the scenario's summary fields). Below it: the Capture panel and the Timeline.
- RIGHT column: a TRUE full-height vertical panel pinned to the viewport height, titled "Incident
  tasks", showing only the CURRENT phase's run_task items as checkboxes with an inline assignee
  field and a Save button, plus an "X/Y done across all phases" counter.
```

Pass B (the two things Streamlit couldn't do — call them out explicitly):

```
Refine the Run Exercise console:
1. Make the current inject a FLOATING, MINIMIZABLE card overlay (position: fixed, e.g. docked
   bottom-right) that the facilitator can collapse to a pill and reopen — it must stay open while
   they type into the Capture form and Timeline underneath, never pushing content around. It shows
   the inject's "room" text big, and a collapsible "Facilitator guidance (don't read aloud)"
   section.
2. Make the right-hand Incident tasks panel a genuinely full-height sticky column, flush to the
   right edge, scrolling independently of the main column.
```

Pass C (capture + timeline):

```
In the Capture panel: a row of type buttons — Business decision, Comms decision, Task (assigned
out), Status update, Note / plan gap — selecting one shows the right fields (e.g. Comms decision =
who/what/how/reasoning; Task = task + assigned-to; Note / plan gap = text + severity + "add to
punch-list" checkbox). An "Acting as" select defaults to the logged-in participant or lets the
facilitator attribute the action to any participant. "Log to timeline" writes a timeline_event
(and, for a plan gap with the checkbox on, also a gap_finding with source='room'). The Timeline
shows events newest-first with a type badge, time (in the run's timezone), who, and description,
each deletable. A Close-out section captures debrief (right/wrong/improve) and a 1–10 confidence
vote per participant. "Resolve & end exercise" logs a Resolution event and sets status=complete.
```

### Prompt 7 — Evidence Report page

```
Build the Evidence Report page. Pick a run for the active client. "Generate closing notes" calls
the closing-notes edge function and stores the draft in run.meta.closing_notes; show it in an
editable textarea (facilitator can rewrite and save). Below, render an on-screen preview of the 8
report sections: 1 Executive summary (closing notes), 2 Debrief, 3 Overview (+ Impact-to-Business
table + scenario summary fields), 4 Team, 5 Incident tasks (X/Y done), 6 Timeline, 7 Plan-gap
punch-list (validated gap_findings only), 8 Confidence vote (with average). An "Approve this
report" checkbox (facilitator sign-off) is required before export is enabled. When approved, show
Download Word (.docx, via the docx npm package, mirroring the 8 sections) and Download JSON.
```

---

## After it works

- Compare against the prototype screens for parity (the prototype is the spec of record).
- Then pick up the deferred Exigence-inspired items if you want them: a guided "new engagement"
  wizard, and plan review cycles (6/12-month re-approval) feeding a readiness-trend view.
- Four scenario decks ship in the seed (BEC, Ransomware, Data Breach, Insider Threat). Author
  more (e.g. MSP supply-chain / RMM compromise) using BEC as the template.
