# Decisions Log

_Structured Q&A to nail down the build. Each question carried my best-guess + confidence;
the recorded answer is what governs. Status: **40 of 40 answered — series complete.**_

## Strategic decisions (pre-series)

| # | Decision | Answer |
|---|---|---|
| S1 | Operating model | **Facilitated service** — the CTO/the MSP runs every session; software is internal force-multiplier |
| S2 | Buyer / GTM | **Mid-market, direct** — the exec is the security decision-maker |
| S3 | Core wedge | **Readiness improvement over time** |

## 40-question series

### Q1 — PR firm's role in delivery
**Answer:** TBD. Start with **co-delivery** (the PR partner live in the room), may shift to
co-marketing later. the PR partner **builds the comms scenarios** and is heavily involved there. A
core goal: surface/sell the PR partner's emergency services through the process, and make clients
aware the PR partner is there to help in a real emergency.

### Q2 — Commercial structure (you ↔ the PR partner)
**Answer:** Deferred — user notes this doesn't change how the application is built. _(Park as
a business-model item, not a build input.)_

### Q3 — Where the evidence goes
**Answer:** Likely a **GRC platform**, but **a polished PDF report is all that's required** —
the full report as required by a **SOC 2 auditor**. (the CTO to share last year's report.)

### Q4 — Timestamp granularity
**Answer:** Base it on the **`5 2025 Tabletop May.docx`** sample — i.e., a full timestamped
timeline of every event/decision/update, plus start/resolution/total/response times.

### Q5 — Build scope
**Answer:** **Full replacement of Exigence.** Our platform runs the whole live tabletop and
generates the report. Stop using Exigence.

### Q6 — Run mode / participant interaction
**Answer:** **Configurable.** Critical mechanic: when the facilitator clicks on someone's
behalf, they must **select who they're acting as** (e.g., logged as the CFO). If the CFO
clicks themselves, it's logged as the CFO. → **act-as attribution** required for evidence
authenticity.

### Q7 — Readiness scoring
**Answer:** No rigid score. Maybe an **EOS-style end-of-session vote**. The real signal is the
**number/severity of changes the IRP/BCP needs** to be real-incident-ready. Also: must
**ingest plans from other sources** (e.g., download IRP/BCP PDFs from ControlMap and upload)
and run a **setup wizard** so the system understands who everyone is and clear
roles/responsibilities before the tabletop.

### Q8 — How the ingested plan is used
**Answer:** **AI pre-gap analysis** — compare the ingested plan to a best-practice baseline
and generate a gap list **before** the exercise; the tabletop validates/expands it.

### Q9 — Launch scenarios + personalization
**Answer:** **BEC, Ransomware (w/ data exfiltration), Data breach / PII** at launch (more
later). Must support **per-company customization with real named people and their access**
("Brenda in finance has data exfiltrated"; "Joey wired payroll to a hacker"; "Carrol in CS had
her identity compromised — what can she access?"). Make it feel real, not stock characters.

### Q10 — Setup-wizard capture
**Answer:** People/roles/responsibilities; **assets & data access map (general only**, not
folder-level); key third-party contacts; tech environment basics. Keep it **non-technical** —
the exercise is mostly about **who makes judgment calls and who to contact**; technical work is
"assigned out" and the tech team reports back. (Reference: the MSP IRP + BCP.)

### Q11 — Inject delivery
**Answer:** **Facilitator-revealed, pre-scripted.** You decide when to drop each pre-written
inject based on the room.

### Q12 — Branching
**Answer:** **Linear deck, facilitator adapts.** Ordered inject set per scenario; reveal/skip/
reorder live. No branching engine. Consequences discussed in the room, not computed.

### Q13 — Communications handling
**Answer:** **Capture the decision only** (who/what/when/how + reasoning). the PR partner coaches
verbally; the tool does not draft or transmit statements.

### Q14 — Evidence report contents
**Answer:** **Full mirror + redlined plan.** Mirror the Exigence report structure, add the
plan-gaps/recommended-changes section and the EOS confidence vote, AND include an actual
**redlined/updated version of the IRP** showing the changes.
→ Build implication: hold the ingested plan as **editable structured content**, not a static
PDF, so tracked changes can be rendered.

### Q15 — How the redline/gap changes get authored
**Answer:** **Live notes + AI review, output as an actionable update list.** During the
session the facilitator captures notes when something needs to change (e.g., "insurance
provider changed — update contact," "reorder this step"). Output can be a redlined plan
**or** just a clean list of "things to update later" — the point is to hand the facilitator
(or someone else) a concrete punch-list so the plan gets corrected. **Core purpose: see what
works, fix what doesn't.** AI review is explicitly wanted on top: flag gaps/staleness the
room didn't catch ("you have no PR firm listed," "corporate insurance shows a former
provider"). → Build implication: capture mechanism = lightweight in-session note/flag tied to
a plan element; report renders both human notes and AI-found gaps as an approvable change list.

### Q16 — Multi-tenancy
**Answer:** **Yes — multi-org from the start.** Each client is an isolated org (its own
people, plans, contacts, run history). Hard tenant isolation in the data model from v1.

### Q17 — Auth / access
**Answer:** **Facilitator accounts + magic-link participants.** Magic links for low-friction
participant join. **Critical requirement:** an **out-of-band login fallback** for staff in
case **email is down** — which is a realistic incident condition (can't depend on email to
authenticate during an exercise about email/systems being compromised). → Build implication:
secondary auth path independent of email (e.g., one-time code via facilitator, SMS, or
pre-shared access). _Hosting note:_ likely **Lovable** (lovable.dev) unless a stronger option
emerges — revisit under Q-stack; must support magic links + the email-down fallback.

### Q18 — Session clock
**Answer:** **Yes — live running clock + manual time entry.** Compressed-clock session with
start/resolution/total/response times per the `5 2025 Tabletop May.docx` sample; facilitator
can also set/adjust times manually. Drives the timestamped evidence timeline.

### Q19 — Observers
**Answer:** **Yes — keep the Observer role.** Non-acting attendees (e.g., "Executive
leadership, Group" in the sample) appear in attendance/evidence but are never logged as making
decisions. Distinct from act-as participants.

### Q20 — Facilitator guidance
**Answer:** **Yes — per-inject teleprompter.** Each inject carries facilitator-only guidance:
what to look for, "what good looks like," suggested probing questions. **This is the
scaling mechanism** — lets a trained non-the CTO facilitator run a quality session, supporting the
productization/light-facilitation trajectory (S1 tension resolution).

### Q21 — Real-incident mode
**Answer:** **v1 = tabletop; v2 = real incident management.** _(Refined 2026-06-25 — was
"first-class now"; resequenced into versions.)_ The same tool should eventually run a **real**
incident, but that is **v2**, not v1. v1 ships tabletop only. → Architecture directive stands:
build the v1 core (timeline/clock, contact directory, decision log, act-as attribution, evidence
output) so it **doesn't preclude** a real-incident mode later — exercise vs. real-incident is a
**mode** on shared infrastructure. But do **not** carry real-incident reliability/uptime/comms
scope into v1. Tabletop is the v1 product; incident management is the v2 expansion.

### Q22 — Export formats
**Answer:** **PDF + editable Word + structured export.** Polished PDF = primary SOC 2
deliverable; Word = hand-editable redline/punch-list (Q15); structured (JSON/CSV) = GRC upload
+ machine-readable evidence/trend data (feeds Q28 GRC integration and the readiness trend).

### Q23 — Report generation timing
**Answer:** **Live-built log, finalized at close.** The GUI shows the timestamps + event log
on a dedicated tab **in real time** as the session runs (you watch the timeline build). But the
**output documents** (PDF/Word/structured evidence) are **only generated/completed once the
incident/tabletop is marked complete.** → Build implication: live timeline view ≠ document
render; the export step is gated on session completion.

### Q24 — Data residency / security
**Answer:** **Deferred.** Not a v1 decision driver. (Will matter before external sale / SOC 2
of the platform itself; revisit alongside final hosting choice.)

### Q25 — Scenario authoring
**Answer:** **In-app authoring in v1.** the CTO (and the PR partner for comms injects, Q37) can
create/edit scenarios and injects in the app from the start — not config/code-only. Seed
content (BEC, Ransomware, Data breach) still ships, but the authoring UI is a v1 feature.

### Q26 — AI provider & usage
**Answer:** **Claude (latest Anthropic models).** Used for gap analysis (Q8), note/redline
review (Q15), and closing-notes generation. Keep integration provider-swappable.

### Q27 — Action-item tracking
**Answer:** **Yes — tracked to closure.** Corrective actions get owner + due date + status and
**persist across engagements** so the next session can verify closure. This is the spine of the
**readiness-improvement wedge (S3)** — plan-change/action volume trending down over time = the
core signal.

### Q28 — GRC integration
**Answer:** **v1 = import + structured export; two-way ControlMap sync = post-MVP.** _(Refined
2026-06-25 — was "two-way in v1.")_ v1: ingest client plans (PDF upload, Q7) and produce
structured export (Q22) for manual GRC upload. **Two-way ControlMap sync (pull plans / push
evidence + actions back) is built later, not MVP.** When built, it depends on ControlMap
exposing a usable API — confirm the API surface at that point.

### Q29 — Cadence / scheduling
**Answer:** **Manual scheduling in v1; trend computed from repeats.** No automated re-test
reminders v1 — engagements booked manually. The readiness trend is still plotted whenever
repeat sessions occur. (Automated cadence/reminders = later.)

### Q30 — EOS vote mechanics
**Answer:** **1–10 scale, all participants vote, individual votes recorded by name.** Named
because the vote is **audit evidence**. Report shows distribution + average. (Not anonymous.)

### Q31 — Third-party / vendor directory
**Answer:** **Yes — structured directory, pre-loaded per client.** Insurer, breach counsel,
forensics, PR, negotiator, DR, ISP, law enforcement, etc., as structured contacts (per the BCP
table). Used live to train the "who to contact" muscle and captured in evidence. Per-org (Q16).

### Q32 — Best-practice baseline source
**Answer:** **Yes — seed from the existing task/playbook library** (the ~40 Exigence-style
tasks), refined over time. This is the reference set the AI gap analysis (Q8) compares the
ingested client plan against.

### Q33 — Task library / playbook model
**Answer:** **Yes — reusable task templates with guidance text, grouped by phase/status**,
mirroring the sample report structure. Single source feeding both the baseline (Q32) and the
live run.

### Q34 — Role model
**Answer:** **Mirror the sample's incident roles** (IRC, Security Analyst, etc.). Role
assignments and changes are **logged as evidence** (ties to act-as attribution, Q6).

### Q35 — Remote vs in-person
**Answer:** **Both in v1.** Presenter/projector view for in-person sessions **and** a remote
participant view for distributed teams. (Pairs with Q38 light participant view.)

### Q36 — Branding / white-label
**Answer:** **Full white-label** (bigger than the co-branded guess). Configurable branding so
any facilitator/partner can run it under their own brand — directly supports the
**productization / licensable-to-other-facilitators trajectory (S1 resolution).** Per-client
branding on reports falls out of this. → Build implication: branding is a first-class
per-tenant config (logo, colors, report cover), not hardcoded the MSP/the PR partner.

### Q37 — the PR partner inject ownership
**Answer:** **the MSP authors everything.** the PR partner supplies comms/PR content **offline**; the CTO/
the MSP enters and maintains it via the in-app authoring (Q25). No separate scoped the PR partner
author role in v1. (Simplifies permissions; revisit if the PR partner volume grows.)

### Q38 — Participant device experience
**Answer:** **Light participant view.** On their own device participants see the current inject,
prompts for who they're acting as, and the EOS vote. **Facilitator still drives the flow** (Q6/
Q11). Not a full per-participant decision app — keeps the room facilitator-led while enabling
remote participation (Q35).

### Q39 — Notifications
**Answer:** **Email-only for v1; multi-email per user; richer channels later.** Lovable's
built-in magic link handles auth (Q17). **Every user has more than one email** — work + personal
— so that if work email is down (a realistic incident condition) they sign in via personal
email. → Build implication: account model supports **multiple email addresses per user**, any of
which can receive a magic link. **Deferred to real-incident mode (Q21), not v1:** SMS + WhatsApp
connectivity so an incident decision/alert can be pushed to people via SMS/email/WhatsApp to tell
them an incident is live and let them join. For v1, **email only**.

### Q40 — MVP cut
**Answer:** **Single end-to-end engagement.** Smallest first build delivers one full real
engagement on the multi-tenant core:
ingest plan → setup wizard → run a seeded scenario with act-as + live clock + observers →
capture decisions/notes/EOS vote → AI gap review → export evidence (PDF/Word) + redline
punch-list.
**Deferred past MVP:** two-way ControlMap sync (Q28), full white-label theming (Q36), automated
cadence/reminders (Q29), SMS/WhatsApp + real-incident management (Q21/Q39).
**Versioning:** **v1 = tabletop**, **v2 = real incident management**. The v1 architecture stays
real-incident-compatible (Q21) without carrying v2 scope.

---

_All 40 questions answered. Next: translate these decisions into the product requirements /
roadmap (`03-PRODUCT-REQUIREMENTS.md`) and the report spec (`02-EVIDENCE-REPORT-SPEC.md`)._
39. **Notifications** — does the tool simulate/send anything, or purely log? (Q13 leans: log only)
40. **MVP cut** — the smallest first build that delivers a real engagement + report.
