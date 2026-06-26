# IRP Tabletop Platform — Project Overview

_Last updated: 2026-06-25 • Owner: the CTO (CTO, the MSP)_

## Status / progress

- **Decisions:** all **40 of 40** scoping questions answered (`01-DECISIONS-LOG.md`).
- **Versioning locked:** **v1 = tabletop exercises**, **v2 = real incident management** (same
  core; v1 architecture stays real-incident-compatible without carrying v2 scope).
- **MVP (Q40):** one full end-to-end engagement on the multi-tenant core — ingest plan → setup
  wizard → run a seeded scenario (act-as + live clock + observers) → capture decisions/notes/EOS
  vote → AI gap review → export evidence (PDF/Word) + redline punch-list.
- **Deferred past MVP:** two-way ControlMap sync, full white-label theming, automated
  cadence/reminders, SMS/WhatsApp + real-incident mode.
- **Source review done:** sample report, the MSP IRP/BCP, CISA CTEP, competitor (Exigence/Field
  Effect) + 6 Exigence/Spiceworks articles distilled into `04-REFERENCE-NOTES.md`.
- **Build round done:** B0–B15 (`01-DECISIONS-LOG.md`) — stack, tenancy, data shape, capture model.
- **Requirements drafted:** `03-PRODUCT-REQUIREMENTS.md` — v1 spec, Supabase data model, screen
  flows, phased roadmap; drafting questions Q-D1–Q-D4 resolved.
- **Next:** begin build on Lovable + Supabase (data model → setup wizard → BEC run → evidence);
  open business item parked = data residency / SOC 2 posture (Q24).

## What we're building

A software platform that runs **executive incident-response tabletop exercises** and
produces a **SOC 2-grade, timestamped evidence report** at the end. It is delivered as a
**facilitated service** (the MSP runs the sessions), co-marketed with a **PR firm
(the PR partner)** as an emergency-preparedness package, and sold **direct to the mid-market**.

It is a **full replacement** for the team's current tooling (Exigence) — the platform runs
the live exercise end to end and generates the evidence, the redlined plan, and the
readiness trend.

## The one-line positioning

> Not a tool for rehearsing the IT runbook — a tool for rehearsing **executive judgment
> under pressure**, and proving readiness improvement over time with auditable evidence.

The incident is the vehicle. Differentiation lives entirely in the **decision layer** and the
**evidence/readiness output**, not in technical-incident fidelity.

## Competitive read (from reference docs)

- **Exigence** — practitioner/war-room platform for IT/security/MSPs. Dense, multi-tenant,
  tabletop bolted onto live incident management. The executive is a guest. (We currently use
  it and are replacing it.)
- **Field Effect** — human-led tabletop *service* (a consultant as "master of ceremonies").
  High-fidelity but doesn't scale; calendar-bound; expensive.
- **White space we own:** the executive-first, decision-centric tabletop delivered as an
  efficient facilitated service, with a defensible readiness-improvement artifact that manual
  consultants can't produce repeatably.

## Business shape (decided)

| Dimension | Decision |
|---|---|
| Operating model | Facilitated service — the MSP runs sessions; software is the force-multiplier |
| Buyer / GTM | Mid-market, direct (the exec is the security decision-maker) |
| Core wedge | **Readiness improvement over time**, measured by volume/severity of plan changes needed |
| PR partner | **the PR partner** — builds the comms-heavy injects; co-markets emergency-preparedness package; goal is also to surface the PR partner's emergency services to clients |

### The central tension to keep managing
A facilitated service capped by the owner's calendar vs. a high-volume, lower-ACV mid-market
segment. **Resolution:** the software's #1 job is to collapse prep + reporting time per
engagement so the service scales beyond one person's hours; the service is the wedge,
productization (light-facilitation / licensable to other facilitators) is the trajectory.

## End-to-end flow (as designed so far)

1. **Pre-engagement** — Ingest client IRP/BCP (e.g., PDFs from ControlMap). AI runs a
   **pre-gap analysis** vs. a best-practice baseline. A **setup wizard** captures people,
   roles/responsibilities, general data access, third-party contacts, and tech basics.
2. **Personalize** — Scenario slots filled with the client's **real named employees** and
   their access ("Brenda in finance has data exfiltrated"). Feels real.
3. **Run** — Facilitator drives a **linear, pre-scripted inject deck** (configurable run mode,
   with act-as attribution). Non-technical; focused on judgment calls and who-to-contact. Tech
   tasks get "assigned out" and reported back. Comms decisions are captured (who/what/when/how).
4. **Close** — Capture what went right/wrong/can-improve; **EOS-style team confidence vote**.
5. **Output** — Generate the **evidence report** (full Exigence-structure mirror + gaps +
   EOS vote + **redlined IRP**), timestamped, SOC 2-auditor ready, exportable for GRC upload.
6. **Trend** — Track plan-change count/severity across repeat engagements = readiness improving.

## Key people & entities (context)

- **The MSP** (the operating company / first user). Parent: a **holding company** —
  potential portfolio-wide distribution path.
- Core team seen in the sample run (roles, not names): CEO, CTO/acting CISO, CFO,
  VP Client Experience, vCIO, VP Ops, Lead Engineer; plus named alternates.
- **The PR partner** — co-marketing partner for the product package.
- The MSP's own incumbent vendors (useful as realism + the contact-directory schema): a cyber
  insurer, breach counsel, a forensics/IR firm, a ransom negotiator, a DR provider, an ISP,
  and an incumbent PR firm.

## Document index (this folder)

- `00-PROJECT-OVERVIEW.md` — this file
- `01-DECISIONS-LOG.md` — **all 40 questions answered (Q1–Q40)**
- `02-EVIDENCE-REPORT-SPEC.md` — the report/redline deliverable spec
- `03-PRODUCT-REQUIREMENTS.md` — functional requirements + phased roadmap
- `04-REFERENCE-NOTES.md` — distilled notes from source documents
