"""Canonical best-practice IRP baseline (decisions B3/B4, Q8/Q32).

A single global set of chapters the AI gap analysis maps the client's plan against.
Distilled from the IR-plan key chapters (04-REFERENCE-NOTES), the the MSP ITIL-based
Incident Management Policy, and CISA/HSEEP conventions. The client's uploaded plan is
mapped into these chapters; missing or weak chapters surface as gaps.
"""

# key, title, "what good looks like" guidance shown to the facilitator + given to the AI
BASELINE_CHAPTERS = [
    ("purpose_scope", "Purpose & Scope",
     "States what the plan covers, what counts as an incident, and when it applies."),
    ("roles_responsibilities", "Roles & Responsibilities",
     "Named incident roles (IR commander, comms lead, tech lead, exec sponsor) with "
     "decision authority and alternates for each."),
    ("asset_data_inventory", "Asset & Data Inventory / Crown Jewels",
     "Identifies critical systems and sensitive data (PII, financial, IP) so impact can "
     "be assessed quickly."),
    ("detection_identification", "Detection & Identification",
     "How incidents are detected, reported, and confirmed; who can declare an incident."),
    ("classification_severity", "Classification & Severity",
     "A severity matrix with response/resolution SLAs per level (e.g. Critical 4h, Major 8h)."),
    ("escalation_declaration", "Escalation & Declaration",
     "Thresholds and path for escalating, and who formally declares a major incident."),
    ("containment", "Containment — ownership & authority",
     "WHO is responsible for containment and WHO authorizes disruptive actions (e.g. taking "
     "systems offline). Names the technical owner / external partner — NOT the technical steps."),
    ("eradication_recovery", "Eradication & Recovery — ownership",
     "WHO owns eradication and restoration and which partner (MSP / forensics / IR firm) is "
     "engaged; recovery priorities and RTO/RPO targets. Not the technical how-to."),
    ("evidence_forensics", "Forensics Partner & Evidence",
     "Which forensics / IR partner to engage and who decides to involve them. Evidence "
     "preservation is delegated to that partner — not a chain-of-custody procedure here."),
    ("internal_comms", "Internal Communications",
     "Who informs leadership and staff, on what cadence, and through which channels — "
     "including a path that works if normal systems/email are down."),
    ("external_comms_notification", "External Communications & Notification",
     "Notifying customers, regulators, law enforcement, media, and the cyber insurer — "
     "with timing obligations (e.g. affected customers within 24h)."),
    ("legal_regulatory", "Legal & Regulatory Obligations",
     "Breach-notification laws, contractual duties, and privilege/counsel involvement."),
    ("third_party_directory", "Third-Party / Vendor Contacts",
     "A maintained directory: cyber insurer, breach counsel, forensics, PR firm, ransom "
     "negotiator, DR provider, ISP, law enforcement — with current names and numbers."),
    ("business_continuity", "Business Continuity / DR — ownership",
     "Who keeps the business running during the incident, the recovery priorities, and which "
     "DR provider is engaged. Ownership and priorities — not step-by-step recovery procedures."),
    ("post_incident_review", "Post-Incident Review & Lessons Learned",
     "A blameless post-mortem covering what happened, how well it was handled, and "
     "corrective actions tied to root cause."),
    ("plan_maintenance_testing", "Plan Maintenance, Testing & Training",
     "How often the plan is reviewed, tested (tabletop exercises), and staff are trained."),
]

BASELINE_BY_KEY = {key: (title, guidance) for key, title, guidance in BASELINE_CHAPTERS}


def baseline_for_prompt() -> str:
    """Render the baseline as a compact list for the AI prompt."""
    lines = []
    for key, title, guidance in BASELINE_CHAPTERS:
        lines.append(f"- {key} | {title}: {guidance}")
    return "\n".join(lines)
