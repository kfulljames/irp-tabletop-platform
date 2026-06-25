# Decisions Log

_Structured Q&A to nail down the build. Each question carried my best-guess + confidence;
the recorded answer is what governs. Status: 14 of 40 answered (paused after Q14)._

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

---

## Remaining question queue (Q15–Q40) — _tentative, resume on "continue"_

These are the areas still to lock. Order/wording may adapt to prior answers.

15. **Gap/change output** — does the redline come from AI suggestions the facilitator
    approves, or facilitator-authored edits captured live? (guess: AI-proposed, facilitator-approved)
16. **Multi-tenancy** — each client is an isolated org (its people, plans, contacts, run
    history). Confirm scope. (guess: yes, multi-org from the start)
17. **Auth / access** — how facilitator vs. participants log in; magic-link low-friction for
    participants? (guess: facilitator accounts + optional magic-link participants)
18. **Session clock** — does the exercise run on a (compressed) clock with start/resolution
    like the sample? (guess: yes, real-time clock + manual time entry)
19. **Observers** — keep the Observer concept (e.g., "Executive leadership, Group")? (guess: yes)
20. **Facilitator guidance** — does the app give you a teleprompter / "what good looks like"
    prompts per inject (so others can facilitate)? (guess: yes — key to scaling beyond the CTO)
21. **Real-incident mode** — could the same tool run a real incident later (out-of-band)?
    (guess: not v1; architecture shouldn't preclude it)
22. **Export formats** — PDF primary; also editable Word? (guess: PDF + Word)
23. **Report generation timing** — real-time at session end vs. produced after? (guess: real-time)
24. **Data residency / security** — Canadian data, SOC 2 posture, hosting. (guess: Canadian region)
25. **Scenario authoring** — does the CTO author/edit scenarios in-app, or are they config/code?
    (guess: in-app authoring eventually; seed content first)
26. **AI provider & usage** — closing-notes generation, gap analysis, redline suggestions.
    (default: Claude / latest Anthropic models)
27. **Action-item tracking** — are post-exercise corrective actions tracked to closure
    (feeding the readiness loop)? (guess: yes)
28. **GRC integration** — ingest plans from / push evidence + actions back to ControlMap?
    (guess: import v1, push later)
29. **Cadence / scheduling** — annual/quarterly reminders, re-test trend. (guess: yes)
30. **EOS vote mechanics** — scale (1–10?), who votes, anonymous? (guess: 1–10, all participants)
31. **Third-party directory** — pre-load the client's vendor/contact list (insurer, breach
    counsel, forensics, PR, law enforcement) as in the BCP table. (guess: yes, structured)
32. **Best-practice baseline source** — seed from existing playbook/task library (the ~40
    Exigence tasks)? (guess: yes)
33. **Task library / playbook model** — reusable task templates with guidance text, grouped by
    phase/status, as in the sample. (guess: yes)
34. **Role model** — IRC, Security Analyst, etc.; role changes logged. (guess: mirror sample)
35. **Remote vs in-person** — presenter view + projector; remote participant view. (guess: both)
36. **Branding / white-label** — co-branded the MSP + the PR partner; per-client branding on report?
37. **the PR partner inject ownership** — how the PR partner authors/maintains the comms injects in the system.
38. **Participant device experience** — what (if anything) participants see on their phones.
39. **Notifications** — does the tool simulate/send anything, or purely log? (Q13 leans: log only)
40. **MVP cut** — the smallest first build that delivers a real engagement + report.
