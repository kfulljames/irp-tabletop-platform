# Evidence Report Spec

_The end deliverable. Decision Q14 = **full mirror of the Exigence report + plan-gaps section
+ EOS confidence vote + redlined IRP**. Must be SOC 2-auditor grade, fully timestamped,
exportable as a polished PDF (and likely editable Word). Reverse-engineered from
`5 2025 Tabletop May.docx`._

## Header — Incident Summary
- Incident name
- URL / reference id
- Start time, Resolution time, **Total time**, **Response time**
- (Timezone explicit — sample used PST/MST/GMT inconsistently → normalize + label)

## Section 1 — Executive Summary
- Incident name, start/resolution time, **incident type**
- **Incident Closing Notes** — AI-generated narrative of the whole exercise (the sample's
  closing notes are a good template for tone/length)

## Section 2 — Debrief (post-mortem)
- **What went right**
- **What went wrong**
- **What can be improved**
- _(maps to the IRP/BCP post-mortem question set — see 04-REFERENCE-NOTES)_

## Section 3 — Overview
- **Last Status / Latest update**
- **Detection Summary** (initial detection + details: who discovered, when, method)
- **Incident Declaration** (who approved name+title; is it a formal incident?)
- **Incident Scope** (info resources impacted, incident type, IOCs, classification, persons)
- **Impact to Business** — PR exposure, legal/regulatory, client relationship, operational,
  staff morale (each: rating + explanation)
- **Key 3rd-party contact info** (insurer/adjuster, breach counsel, etc.)
- **Incident-type-specific summary block** (e.g., "BEC Summary": funds lost?, email system,
  mailboxes compromised, $ losses, funds recovered, source, # fraudulent transactions).
  → Each scenario type defines its own structured summary schema.

## Section 4 — Team
- **Leads** with role + name/title + **join/role-change timestamp**
- **Observers** (groups, e.g., "Executive leadership, Group")
- Role-change history is part of the timeline

## Section 5 — Tasks
- Grouped by status: **Not applicable / Pending / Done** (mirror sample groupings)
- Per task: title, description/guidance, **Assigned to**, **Assigned at**, **Assigned by**,
  Notes, Linked items, Attachments
- Tasks come from a reusable **playbook/task library** per scenario (see Q32/Q33)

## Section 6 — Timeline (the timestamped evidence spine)
- Columns: **TIME (tz)**, **CATEGORY**, **DESCRIPTION**, **TEAM MEMBER**
- Categories observed in sample: Incident Start, Invitation, Team (joins/role changes),
  Overview Update, Status Update, **Business Decision**, Internal Update, Resolution
- Every action attributed to a person via **act-as** (Q6). This is what makes it auditable.

## NEW Section 7 — Plan Gaps & Recommended Changes _(net-new vs Exigence)_
- The AI pre-gap findings (Q8) **validated/expanded** during the exercise
- Each gap: plan section affected, what's missing/wrong, recommended change, severity, owner
- **Change count + severity = the readiness metric** trended across engagements

## NEW Section 8 — Team Confidence Vote _(net-new)_
- EOS-style vote (scale TBD, Q30 — guess 1–10), all participants
- Captured at session close; trended over time alongside the gap count

## NEW Deliverable — Redlined Plan _(net-new, Q14)_
- An actual **tracked-changes version of the client's IRP** (and/or BCP) reflecting the
  changes surfaced in the exercise
- Requires the ingested plan to be held as **editable structured content**, not a static PDF

---

## Build implications
- **Timestamp everything** at capture time; store tz; render normalized.
- **Act-as attribution** on every logged action.
- **Structured plan model**: parse ingested IRP/BCP into editable sections → enables both the
  redline and the gap mapping.
- **Per-scenario schemas**: the Overview "incident-type-specific summary" and the inject deck
  are scenario-scoped.
- **Export**: polished PDF (primary), editable Word (likely) — confirm Q22.
- **Generation timing**: aim for real-time at session end (Exigence does this) — confirm Q23.
- **Align to HSEEP / CISA CTEP After-Action Report / Improvement Plan (AAR/IP)** conventions so
  the report is instantly recognizable to a SOC 2 auditor. Our "Plan Gaps & Recommended
  Changes" + redlined plan == CTEP's **Improvement Plan**. (See 04-REFERENCE-NOTES.)
