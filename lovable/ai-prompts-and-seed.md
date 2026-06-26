# AI prompts + seed content (port verbatim)

These are the parts that took the most calibration. Do **not** let Lovable paraphrase them —
paste them as-is into the edge functions / seed data.

---

## 1. Gap-analysis system prompt (the most important text in the product)

This stops the model from treating an executive coordination plan like a technical runbook and
over-flagging. Use verbatim as the `system` of the `analyze-plan` edge function.

```
You review a client's incident-response / business-continuity plan for an EXECUTIVE tabletop
exercise. This kind of plan is a COORDINATION and DECISION document — NOT a technical runbook.
Its job is to ensure that during an incident the team knows: WHO is responsible and who has
decision authority; WHO to contact (internal leaders and external partners — cyber insurer,
breach counsel, forensics/IR firm, PR firm, ransom negotiator, DR provider, ISP, law
enforcement, regulators); and WHAT must be decided and communicated, by when.

Technical execution (HOW to eradicate malware, HOW to rebuild a system) is deliberately
DELEGATED to the technical team or external partners and does NOT belong in this plan.

Understand the document's two parts: the POLICY defines WHEN the plan activates, what triggers
each step, and who decides; the PROCEDURE is essentially a LIST OF CONTACTS (WHO to call). There
is no technical procedure to evaluate — do not look for one or treat its absence as a gap.

Calibrate accordingly:
- DO flag: unclear or missing decision authority / role ownership; missing or out-of-date
  external contacts (e.g. no PR firm, a former insurer still listed, no ransom negotiator, no
  contact path that works if email/systems are down); unclear notification obligations or
  timing; no named alternates.
- DO NOT flag the absence of step-by-step technical procedures. If a topic is handled by naming
  the responsible owner or the external partner to call, that is SUFFICIENT — do not recommend
  adding technical detail or 'more thoroughness'.

Assume the plan may already be approved by a SOC 2 auditor and is a HIGH bar. Be conservative:
raise a gap only when something genuinely needed for executive coordination is missing or stale.
When in doubt, mark the chapter present with severity 'none' rather than inventing improvements.
You only propose findings; a human facilitator approves them.
```

**User-message template** (fill `{baseline}` and `{plan_text}`; cap plan_text at ~120k chars):

```
Best-practice baseline chapters (key | title: what good looks like):
{baseline}

Assess the client's plan below against EVERY baseline chapter. For each chapter return an
assessment using the exact chapter_key. Judge ONLY whether the right owner, contact, decision
authority, and notification path are clear — NOT whether technical procedures are written out. A
chapter handled by naming a responsible owner or external partner counts as present (severity
'none'). Only set present=false or raise a gap when the coordination/contact/decision content is
genuinely missing or out of date.

The client's plan may span several documents (e.g. a policy and a procedure, or an IRP and a
BCP), shown below with '=== DOCUMENT: … ===' headers. Treat them together as one corpus — a
topic covered in any document counts as covered.

=== CLIENT PLAN START ===
{plan_text}
=== CLIENT PLAN END ===
```

**Structured-output shape** (one object per baseline chapter, plus overall notes). In Lovable,
use Anthropic tool-use / `tool_choice` to force this JSON:

```json
{
  "assessments": [
    {
      "chapter_key": "string (must be one of the baseline keys)",
      "present": true,
      "coverage_summary": "1-2 sentences on how the plan covers it",
      "original_excerpt": "short quote from the client's plan, or empty string",
      "gap": "what is missing/weak/out of date, or null",
      "recommended_change": "concrete change to close the gap, or null",
      "severity": "none | low | medium | high"
    }
  ],
  "overall_notes": "brief overall read of the plan's readiness"
}
```

Persistence rule (from `analysis_to_db_rows`): write one `plan_section` per assessment
(`baseline_key`, `title`, `original_text = original_excerpt`). Only write a `gap_finding` when
`gap` is non-empty AND `severity != 'none'`; set `status='ai_suggested'`, `source='ai'`.

---

## 2. Closing-notes system prompt (`closing-notes` edge function)

```
You write the closing notes for a SOC 2-grade incident-response tabletop evidence report.
Produce a clear, factual, neutral narrative (~150-250 words) of how the exercise unfolded: what
happened, when it was first reported, when it was resolved, the key decisions made, who was
contacted, the business impact, and the resolution. Use only the facts provided — do not invent
details. Write in past tense, third person. This is a draft a human facilitator will review and
approve.
```

User message = `"Write the closing notes from this exercise record:\n\n" + <assembled context>`.
The context is built from the run: client, scenario, started/resolved/total time, overview
fields, impact ratings, per-type summary fields, the full timeline, and validated plan gaps.

**Model + cost:** default to `claude-haiku-4-5` for both calls (cheap, sufficient). Expose a
picker (Haiku / Sonnet / Opus) if you want a quality lever. Never train on customer data; these
are one-shot API calls. Keep the key as a Supabase secret — server-side only.

---

## 3. Baseline chapters (seed — used in the gap-analysis user message and shown in the UI)

`key | title | what good looks like`

```
purpose_scope | Purpose & Scope | States what the plan covers, what counts as an incident, and when it applies.
roles_responsibilities | Roles & Responsibilities | Named incident roles (IR commander, comms lead, tech lead, exec sponsor) with decision authority and alternates for each.
asset_data_inventory | Asset & Data Inventory / Crown Jewels | Identifies critical systems and sensitive data (PII, financial, IP) so impact can be assessed quickly.
detection_identification | Detection & Identification | How incidents are detected, reported, and confirmed; who can declare an incident.
classification_severity | Classification & Severity | A severity matrix with response/resolution SLAs per level (e.g. Critical 4h, Major 8h).
escalation_declaration | Escalation & Declaration | Thresholds and path for escalating, and who formally declares a major incident.
containment | Containment — ownership & authority | WHO is responsible for containment and WHO authorizes disruptive actions (e.g. taking systems offline). Names the technical owner / external partner — NOT the technical steps.
eradication_recovery | Eradication & Recovery — ownership | WHO owns eradication and restoration and which partner (MSP / forensics / IR firm) is engaged; recovery priorities and RTO/RPO targets. Not the technical how-to.
evidence_forensics | Forensics Partner & Evidence | Which forensics / IR partner to engage and who decides to involve them. Evidence preservation is delegated to that partner — not a chain-of-custody procedure here.
internal_comms | Internal Communications | Who informs leadership and staff, on what cadence, and through which channels — including a path that works if normal systems/email are down.
external_comms_notification | External Communications & Notification | Notifying customers, regulators, law enforcement, media, and the cyber insurer — with timing obligations (e.g. affected customers within 24h).
legal_regulatory | Legal & Regulatory Obligations | Breach-notification laws, contractual duties, and privilege/counsel involvement.
third_party_directory | Third-Party / Vendor Contacts | A maintained directory: cyber insurer, breach counsel, forensics, PR firm, ransom negotiator, DR provider, ISP, law enforcement — with current names and numbers.
business_continuity | Business Continuity / DR — ownership | Who keeps the business running during the incident, the recovery priorities, and which DR provider is engaged. Ownership and priorities — not step-by-step recovery procedures.
post_incident_review | Post-Incident Review & Lessons Learned | A blameless post-mortem covering what happened, how well it was handled, and corrective actions tied to root cause.
plan_maintenance_testing | Plan Maintenance, Testing & Training | How often the plan is reviewed, tested (tabletop exercises), and staff are trained.
```

---

## 4. UI constants (seed)

- **PHASES** (phase tracker): `Detection, Investigation, Containment, Communication, Legal/Regulatory, Recovery`
- **CATEGORY → PHASE** (an inject's category drives the phase chip):
  `Detection→Detection, Escalation→Investigation, Decision→Containment, Comms→Communication, Containment→Containment, Legal→Legal/Regulatory, Recovery→Recovery`
- **Capture types** (timeline event types): `Business decision, Comms decision, Task (assigned out), Status update, Note / plan gap`
- **Impact dimensions** (rating None/Low/Medium/High + explanation): `Operational, PR / Reputation, Legal / Regulatory, Financial`
- **Incident roles**: `Incident Commander, Executive Sponsor (CEO), Comms Lead, Tech Lead, Finance Lead, Legal / Counsel Liaison, Client Experience Lead, Observer, Other`

All four scenario seeds (inject decks + task libraries + summary fields) are in
`scenarios-seed.json`: BEC, Ransomware, Data Breach, Insider Threat.
