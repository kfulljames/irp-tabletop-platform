# Reference Notes — distilled from source documents

_Source files live in the parent folder. This captures the reusable substance so we don't
re-derive it each session._

## Sample tabletop report — `5 2025 Tabletop May.docx`
- A **real Exigence-generated post-incident report** from a BEC tabletop the MSP ran
  (≈39 min total, 2 min response).
- Scenario: a client paid funds to fraudulent details; funds never received; routing numbers changed 3 months prior;
  $20,000 lost, 1 mailbox compromised, O365 cloud, funds not recovered, source = "our system."
- This is the **template for the evidence report** (see 02-EVIDENCE-REPORT-SPEC.md).
- Demonstrated structure: Incident Summary → Exec Summary + Closing Notes → went right/wrong/
  improve → Overview (detection, declaration, scope, business impact, 3rd-party, BEC summary) →
  Team (roles + timestamps) + Observers → Tasks (grouped by status) → full timestamped Timeline.
- Timeline categories: Incident Start, Invitation, Team, Overview Update, Status Update,
  **Business Decision**, Internal Update, Resolution.

## Incident Management Policy (IRP) — sample
- Based on **ITIL v4**. Owner: the IT/policy lead; approved by the CTO.
- Lifecycle: prepare → identify/report → assign → analyze/resolve → resolution comms →
  review/learnings. (Good basis for the **best-practice gap baseline**.)
- **Classification + SLAs** (use for severity model):
  - Critical — reputational/severe — **resolve 4h**
  - Major — one system, can cause damage — **resolve 8h**
  - Minor — noncompliance/best-practice deviation — **resolve 48h**
  - Cosmetic — documentation/policy — **resolve 7d**
- Evidence-class types: Privacy breach (PII), Proprietary breach (critical infra), Integrity loss.
- **Post-mortem questions** (→ maps to went right/wrong/improve + report): what happened &
  when; how well did staff/management perform; were procedures followed/adequate; what info was
  needed sooner; any steps that inhibited recovery; what to do differently; info-sharing
  improvements; corrective actions; precursors to watch.
- Senior management notified **before** customers; affected customers within **24h**.

## Business Continuity & DR Procedures (BCP) — sample
- DR workflow: occurrence → declaration (by exec team) → communicate → recovery → postmortem.
- **DR team table schema** (use for setup wizard + directory): Position | Responsibilities |
  Name & Contact | Alternates.
  - CEO (decision-making + PR/comms lead); alt the CTO
  - CTO/acting CISO (diagnosis/containment/restoration); alt a senior engineer
  - Lead Engineer; alt a backup engineer
- **Third-party directory** (rich — model the contact schema + realism on this):
  - Cyber insurer (with named broker contacts)
  - Legal / breach counsel
  - Forensics: a SOC partner + an IR firm (evergreen partnership)
  - Breach notification / call center; credit / identity-monitoring providers
  - ISP
  - **PR/Comms:** an incumbent PR firm (NOT the product partner; the product partner is **the PR partner**)
  - Crisis-management firms (several evaluated)
  - Forensic accounting; a ransom negotiator; a cyber/SOC partner; a DR provider
  - Law enforcement: local police, national anti-fraud reporting, and the national cyber-security centre
  - Parent: the holding company (a President/COO contact)
- Recovery procedures per type (Security breach/DoS/Ransomware; Infrastructure; Personnel;
  Physical; Pandemic) each with steps + people responsible + **RTO/RPO objectives**.
- Region: **Canadian** context (a regional MSP).

## Exigence (competitor we're replacing) — marketing docs
- Practitioner platform; multi-tenant for MSPs/MSSPs/IR firms + IT/security teams.
- Scenario topic taxonomy seen in UI: Ransomware, Insider threat, Phishing/social engineering,
  Data exfiltration, Malware/zero-day, BYOD risk, Third-party software compromise, Custom.
- Features: AI scenario generation, AI tabletop/drill guidance, AI closing-notes/RCA reports,
  situation room, automated playbooks (IF/THEN), role/template comms, status pages, analytics,
  out-of-band availability. Claims: "hours to minutes" prep, "real-time report generation."
- Certified ISO 27001 + SOC 2 Type 2.

### Source review 2026-06-25 — 5 Exigence blog posts + 1 Spiceworks post-mortem guide
_(Mostly **confirms** prior decisions; new/sharpening items flagged ⚑.)_
- **"END INCIDENT" close flow** (screenshot): modal "Great job! Normality has been restored.
  Are there any closing notes you'd like to add?" → an editable AI-Buddy narrative auto-fills.
  Exactly our close → AI-summary → editable-notes pattern (Q15/Q23/Q26). Sample narrative was a
  timestamped recap ("first reported 12:00 AM EST … resolved 07:27 PM EST … rolled back a
  password sync change…").
- ⚑ **Concrete incident-summary field schema** (use to tighten evidence report Sec 1/Sec 3):
  when it took place · **when first reported (internally vs to customers)** · when resolved ·
  what happened · systems affected · severity · customer impact (who/how many) · business impact
  (data breach / SLA-KPI miss) · **who was notified internally/externally** · **what was
  communicated to leadership vs customers** · resolution actions.
- ⚑ **Spiceworks post-mortem template** — 7 sections: **Leadup · Fault · Impact · Detection ·
  Response · Recovery · Timeline**, then **root cause** + **corrective actions linked to root
  cause**; **blameless** (process not people); hold **within 48h** of resolution; small group of
  responders + key stakeholders. Enriches our Debrief (Sec 2) + action tracking (Q27).
- **IM vs IR distinction** (Exigence's own framing): incident *management* = broad end-to-end
  logistics/comms/planning/aligning/reporting across stakeholders; incident *response* = the
  technical analysis/containment subset. **Validates our executive-judgment wedge** — we own the
  management layer, tech is "assigned out" (Q10). Their 9-step IM process (log → categorize →
  prioritize → assign → task → SLA/escalate → resolve → close → review) ≈ our run + close.
  Their IM roles: incident manager, first/second line, **comms lead**, tech lead.
- **IR-plan "key chapters"** (good gap-analysis baseline checklist, Q8/Q32): roles &
  responsibilities · identification/assessment framework · containment · eradication/recovery ·
  data collection for intel · post-mortem outline · notification requirements · comms guidelines
  (internal, customers, **law enforcement, media, regulators, insurer**) · IR checklist.
- ⚑ **Plan availability when systems are down**: "critical that the plan be available even if the
  enterprise system that stores it is down." Extends Q17/Q39 beyond auth — the **IRP + contact
  directory themselves** need offline/exportable access during a real incident. → v2/real-incident
  requirement, not v1-critical.
- ⚑ **AI data-privacy stance**: Exigence explicitly warns against public ChatGPT (prompts can
  surface to other parties); insists genAI be "private, local, contained." Our answer: the
  **Anthropic API does not train on customer data** — directly addresses this; make it a sales
  point. Ties Q26 ↔ deferred Q24.
- ⚑ **Searchable past-incident knowledge** ("query genAI for previous incidents — which actions
  resolved fast, which to avoid"). Adjacent to our readiness trend; **candidate v2 feature**
  (incident/exercise knowledge base for reuse).
- Confirmed-also: multi-tenant for MSP/MSSP delivery (Q16); playbook guidance during the
  exercise = our facilitator teleprompter (Q20); automated exercise scheduling + reminders +
  searchable scheduled/running/completed states (we **deferred** this as Q29 — fine, but note the
  incumbent has it); one-click report at close (Q23).

## Field Effect — tabletop as a human service
- Six incident types: Ransomware, Business Email Compromise, Malware, Information theft,
  Internet-facing service compromise, Unauthorized fund transfers.
- Readiness cycle: **secure → prepare → practice → review → repeat**.
- Evaluation areas: threat ecosystems, security solutions, roles & responsibilities, high-value
  assets, backup mgmt, log mgmt.
- What execs actually wrestle with: **decision thresholds** (when to notify; pay ransom?),
  **internal/external comms**, **legal/regulatory obligations**. Most value = the spur-of-the-
  moment cross-functional conversations a facilitator provokes. (This is the experience to
  replicate in software.)

## Prior art & external content sources (evaluated 2026-06-24)

**Strategic takeaway: scenario content is commoditized (CISA gives it away; builders exist).
Our moat is NOT scenarios — it's plan ingestion → AI gap analysis → redlined plan → SOC 2
evidence → readiness trend → facilitated delivery with the PR partner. Seed scenarios from CISA;
spend engineering on the evidence/readiness/ingestion layer.**

### CISA CTEP — highest value (free, public domain, authoritative)
- A CTEP package = **Situation Manual** (scenario + background + discussion questions) +
  **Facilitator/Evaluator Handbook** + **Exercise Brief slide deck** + **Feedback Form** +
  **After-Action Report / Improvement Plan (AAR/IP)**.
- Our evidence report ≈ their **AAR/IP**; our gaps + redlined plan ≈ their **Improvement Plan**.
- Follows **HSEEP** (Homeland Security Exercise & Evaluation Program) conventions → align our
  report to these for auditor credibility.
- Scenarios run in **modules** with discussion questions → matches our linear inject deck (Q12).
- 100+ situation manuals incl. ransomware, insider threat, phishing, ICS, plus sector packs
  (elections, local gov, water, healthcare, maritime). **Seed BEC/Ransomware/Data-breach here.**
- Links: https://www.cisa.gov/resources-tools/resources/ctep-package-documents •
  https://www.cisa.gov/resources-tools/services/cisa-tabletop-exercise-packages •
  Planner Handbook (PDF) and Facilitator/Evaluator Handbook (PDF) available on cisa.gov.
- _Note: U.S. government work — broadly public domain / free to customize. Verify license text._

### danhowett cyber-tabletop-exercise-builder — closest prior art (study its UX)
- Inputs: **client profile** (sector, size, geography, regulatory exposure) + **tech stack**
  (9 categories). Personalizes **12 pre-built scenarios** with real product names. Templating,
  not AI.
- Flow: **Setup → Scenario Library → Brief → Run → After-Action Report** (good UX reference).
- We differ via named-people personalization, plan ingestion, gap/redline, SOC 2 evidence,
  readiness trend, facilitated service. Free GitHub-pages tool, not a competitor.
- https://danhowett.github.io/useful/cyber-tabletop-exercise-builder.html

### dev.to "CyberTabletop CLI" — the AI-live-facilitator path we rejected (for now)
- Copilot acts as live facilitator: generates scenarios + consequences each turn; risk scored
  across **operational/data/legal** (echoes our Impact-to-Business categories).
- We chose authored linear decks (Q11/Q12) for determinism + defensibility. Keep its patterns
  (stateless state-passing, embedded JSON schemas, defensive parsing) for a possible future
  AI-adaptive premium mode.
- https://dev.to/enniob/cybertabletop-cli-...

### Lower priority / not deep-fetched
- **chan2git/tabletop-exercises** (GitHub) — early-stage, ~1 phishing scenario. Thin.
- **CIS MS-ISAC TTX** — ready-made TTX packages (member resource); more seed scenarios +
  credibility. Worth a look. https://www.cisecurity.org/ms-isac/tabletop-exercises-ttx
- **threatintelligence.com** example scenarios; **beyond1n0** AI-TTX thought piece — lower value.
- **ktaki8.github.io/tabletop.html** — not evaluated.
