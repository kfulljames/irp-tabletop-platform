# Product Requirements (working draft)

_Functional requirements grouped by capability, plus a phased roadmap. Reflects decisions
through Q14; items tied to unanswered questions are marked (open: Qn)._

## A. Client setup & onboarding
- **A1. Multi-org / multi-tenant** — each client is an isolated org with its own people,
  plans, contacts, and run history. (open: Q16)
- **A2. Document ingestion** — upload IRP/BCP PDFs (e.g., exported from ControlMap). (Q7)
- **A3. Structured plan model** — parse ingested plans into editable sections (enables redline
  + gap mapping). (Q14)
- **A4. AI pre-gap analysis** — compare ingested plan to a best-practice baseline; produce a
  pre-exercise gap list. (Q8)
- **A5. Setup wizard** captures: people + roles/responsibilities; **general** data-access tags
  (not folder-level); third-party contact directory; tech-environment basics. Non-technical
  framing. (Q10)
- **A6. Third-party directory** — structured (insurer, breach counsel, forensics, PR/the PR partner,
  negotiator, DR, law enforcement, parent co). Schema mirrors the BCP table. (open: Q31)

## B. Scenario & content
- **B1. Launch scenarios**: BEC, Ransomware (w/ data exfiltration), Data breach / PII. (Q9)
  → **Seed from CISA CTEP situation manuals (public domain)** rather than authoring from
  scratch. Scenario content is commoditized; do not over-invest here. (See 04-REFERENCE-NOTES.)
- **B2. Per-company personalization** — scenario slots bind to **real named employees** and
  their general access ("Brenda in finance…"). (Q9)
- **B3. Linear inject deck per scenario** — ordered, facilitator reveals/skips/reorders; no
  branching engine. (Q11, Q12)
- **B4. the PR partner-authored comms injects** — the PR-heavy curveballs (journalist calls, go-public
  threats, ransom-deadline moves). (Q1, open: Q37)
- **B5. Scenario-specific Overview schema** (e.g., BEC Summary fields). (report spec)
- **B6. Reusable task/playbook library** with guidance text, grouped by phase/status (seed from
  the ~40 Exigence tasks). (open: Q32, Q33)
- **B7. Scenario authoring** — in-app eventually; seed content first. (open: Q25)

## C. Live run
- **C1. Configurable run mode** — facilitator-only, hybrid, or full multi-user. (Q6)
- **C2. Act-as attribution** — facilitator selects whom they act on behalf of; self-clicks log
  as self. (Q6)
- **C3. Session clock** — start/resolution/total/response times; compressed time. (open: Q18)
- **C4. Roles + role changes** — IRC, Security Analyst, etc.; logged to timeline. (open: Q34)
- **C5. Observers** — group observers (e.g., "Executive leadership"). (open: Q19)
- **C6. Decision/comms capture** — comms = capture the decision only (who/what/when/how).
  Technical tasks "assigned out," tech team reports back. (Q10, Q13)
- **C7. Facilitator guidance** — per-inject prompts / "what good looks like" so others can
  facilitate (scaling lever). (open: Q20)
- **C8. Full timeline capture** — every event timestamped + attributed. (Q4)

## D. Close & evidence
- **D1. Debrief capture** — what went right / wrong / can-improve. (report spec)
- **D2. EOS confidence vote** — at close; trended. (Q14, open: Q30)
- **D3. Gap validation** — confirm/expand the AI pre-gap list during the exercise. (Q8)
- **D4. Evidence report** — full Exigence mirror + gaps + EOS vote. (Q14)
- **D5. Redlined plan** — tracked-changes IRP/BCP. (Q14)
- **D6. Export** — polished PDF (primary); editable Word likely. (open: Q22)
- **D7. AI narrative** — closing notes / exec summary generation. (open: Q26)

## E. Readiness over time (the wedge)
- **E1. Plan-change metric** — count + severity of changes needed per engagement. (Q7)
- **E2. Trend dashboard** — across repeat engagements per client. (open: Q29)
- **E3. Action-item tracking** — corrective actions tracked to closure. (open: Q27)

## F. Platform
- **F1. Auth** — facilitator accounts; low-friction participant access. (open: Q17)
- **F2. Data residency / security** — Canadian, SOC 2 posture. (open: Q24)
- **F3. GRC integration** — import plans (ControlMap) v1; push evidence/actions later. (open: Q28)
- **F4. Branding** — the MSP + the PR partner co-brand; per-client report branding. (open: Q36)
- **F5. (Future) real-incident mode** — out-of-band live use; not v1. (open: Q21)

---

## Phased roadmap (service-led — exploit "earn while you learn")

**Phase 0 — Deliver with thin tooling (now)**
Run real engagements with a polished slide/inject deck + the report template. One scenario
(BEC) is enough. Real clients fund and shape the build.

**Phase 1 — MVP platform**
Setup wizard + document ingestion + AI pre-gap analysis; linear inject runner with act-as
attribution + timeline capture; evidence report generator (full mirror + gaps + EOS vote +
redline); BEC + one more scenario. Goal: collapse prep + reporting to minutes.

**Phase 2 — Library & trend**
Ransomware + Data breach scenarios; per-company personalization; readiness trend dashboard;
action-item tracking; in-app scenario authoring; third-party directory.

**Phase 3 — Productize & scale**
Light-facilitation / licensable to other facilitators; GRC push integration; the holding company
portfolio rollout; optional real-incident mode.

## Open architecture decisions (not yet asked)
- Build vs low-code: recommend **custom engine** (state machine + content renderer + report/
  redline generator) on commodity infra (web stack + Postgres/Supabase-class + auth provider).
- AI: use for gap analysis, closing-notes/exec-summary narrative, redline suggestions. Default
  to latest Anthropic (Claude) models. Keep the live run deterministic (authored), AI assists
  authoring + reporting. (confirm Q26)
