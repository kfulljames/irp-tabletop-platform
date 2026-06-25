"""Seeded scenario inject decks (decisions Q9, Q11, Q12, B7, B8, B14).

Linear, facilitator-revealed injects. Executive/coordination focus — judgment calls and
who-to-contact, not technical how-to. BEC is fully seeded; Ransomware and Data-breach are
scaffolded. Claude drafted these; the CTO + the PR partner refine later (B14).

Each inject:
  title    — short label for the deck
  category — Detection | Escalation | Decision | Comms | Containment | Legal | Recovery
  room     — what the facilitator reads/shows the room
  guidance — facilitator-only teleprompter: what good looks like + probing questions (B8)
"""

# Common incident roles to assign people to (Q34). Free-text also allowed in the UI.
INCIDENT_ROLES = [
    "Incident Commander",
    "Executive Sponsor (CEO)",
    "Comms Lead",
    "Tech Lead",
    "Finance Lead",
    "Legal / Counsel Liaison",
    "Client Experience Lead",
    "Observer",
    "Other",
]

CAPTURE_TYPES = [
    "Business decision",
    "Comms decision",
    "Task (assigned out)",
    "Status update",
    "Note / plan gap",
]

# Incident lifecycle phases for the phase tracker (Exigence-style).
PHASES = ["Detection", "Investigation", "Containment", "Communication", "Legal/Regulatory", "Recovery"]

# Map an inject's category to the lifecycle phase it represents (drives the phase bar).
CATEGORY_TO_PHASE = {
    "Detection": "Detection",
    "Escalation": "Investigation",
    "Decision": "Containment",
    "Comms": "Communication",
    "Containment": "Containment",
    "Legal": "Legal/Regulatory",
    "Recovery": "Recovery",
}

BEC = {
    "key": "bec",
    "title": "Business Email Compromise — fraudulent invoice / payment diversion",
    "summary": (
        "A client paid an invoice to bank details that were not yours. A mailbox appears "
        "compromised and altered invoices have gone to clients. Tests detection, escalation, "
        "money/comms/legal decisions, and who-to-contact under pressure."
    ),
    "injects": [
        {
            "title": "The first call",
            "category": "Detection",
            "room": (
                "A long-standing client emails your finance team: \"We paid the $48,000 "
                "invoice three weeks ago to the banking details on the invoice you sent — why "
                "are you now saying it's overdue?\" The bank details they paid are not yours."
            ),
            "guidance": (
                "Who in the room hears this first, and who do they tell? Is this treated as a "
                "one-off billing dispute or a potential incident? Probe: who has the authority "
                "to declare an incident here, and what would make them do it?"
            ),
        },
        {
            "title": "It came from us",
            "category": "Detection",
            "room": (
                "Finance confirms the client received an emailed invoice from a the MSP "
                "address with altered banking details. The email appears to have come from a "
                "real internal mailbox."
            ),
            "guidance": (
                "Now the concern is a compromised mailbox, not a billing error. Who investigates, "
                "and who decides to pull in IT/security? Watch for the team jumping to technical "
                "fixes — the executive job here is to confirm scope and assign an owner."
            ),
        },
        {
            "title": "Confirmed compromise",
            "category": "Escalation",
            "room": (
                "IT finds inbox rules quietly forwarding finance emails to an external address, "
                "and sign-in logs show the mailbox was accessed from an unfamiliar location three "
                "weeks ago."
            ),
            "guidance": (
                "This is now a confirmed breach. Who formally declares it? Who is named Incident "
                "Commander? Is leadership notified — and using what channel, given email itself "
                "may be untrustworthy? Probe the out-of-band contact path."
            ),
        },
        {
            "title": "The money is gone",
            "category": "Decision",
            "room": (
                "The $48,000 has likely already left the client's account to a fraudulent "
                "account. The client is asking, pointedly, what you are going to do about it."
            ),
            "guidance": (
                "Decisions to surface: who contacts the bank and law enforcement, and how fast? "
                "Who owns the client relationship through this? When do you notify the cyber "
                "insurer and engage breach counsel? Note who they say to call — that's the test."
            ),
        },
        {
            "title": "It's spreading",
            "category": "Comms",
            "room": (
                "A second client calls: they also received \"updated banking details\" last week "
                "and are about to pay a $30,000 invoice."
            ),
            "guidance": (
                "Containment is now also a communications problem. Who warns all clients, with "
                "what message, and who approves it going out? Is the PR/comms partner engaged? "
                "Speed vs. accuracy — what do they decide?"
            ),
        },
        {
            "title": "Make it stop",
            "category": "Containment",
            "room": (
                "You need confidence that no other mailboxes are compromised and that the "
                "forwarding rules and any persistence are gone."
            ),
            "guidance": (
                "Who OWNS the technical containment — internal IT, the MSP, or an external "
                "forensics/IR firm — and who authorizes it? The plan should name the owner and "
                "the partner to call; it does not need the technical steps."
            ),
        },
        {
            "title": "What are we obligated to do?",
            "category": "Legal",
            "room": (
                "Counsel asks whether client financial data or personal information was exposed, "
                "which may trigger breach-notification obligations and regulator timelines."
            ),
            "guidance": (
                "Who determines the data scope? What notification obligations and deadlines "
                "apply, and who owns them? Regulators, affected clients, timing. Watch for "
                "uncertainty about who actually makes this call."
            ),
        },
        {
            "title": "Stabilized — now account for it",
            "category": "Recovery",
            "room": (
                "Forwarding rules are removed, passwords reset, MFA enforced, and clients have "
                "been warned. The client who lost funds wants a written summary of what happened."
            ),
            "guidance": (
                "Who produces the written summary and what goes in it? Then the readiness "
                "question: what in the plan was unclear or missing during this exercise? Capture "
                "those as plan-gap notes — they feed the punch-list and the evidence report."
            ),
        },
    ],
    # Lean task library grouped by phase (B-checklist; kept short to avoid clutter).
    "tasks": [
        ("Detection", "Document the details of the detection"),
        ("Detection", "Confirm whether a mailbox/account is compromised"),
        ("Investigation", "Identify which accounts/systems were accessed, and from where"),
        ("Investigation", "Determine whether funds left the account; engage the bank"),
        ("Containment", "Reset credentials and enforce MFA on affected accounts"),
        ("Containment", "Remove malicious inbox rules / forwarding"),
        ("Containment", "Engage forensics / IR partner (decide owner)"),
        ("Communication", "Warn all clients to verify banking details before paying"),
        ("Communication", "Approve external / PR messaging (engage PR partner)"),
        ("Legal/Regulatory", "Determine data / PII exposure scope with counsel"),
        ("Legal/Regulatory", "Assess breach-notification obligations and deadlines"),
        ("Recovery", "Notify cyber insurer and engage breach counsel"),
        ("Recovery", "Produce written summary for the affected client"),
        ("Recovery", "Capture plan gaps and corrective actions"),
    ],
}

RANSOMWARE = {
    "key": "ransomware",
    "title": "Ransomware with data exfiltration (scaffold)",
    "summary": "Coming soon — to be authored with the CTO + the PR partner.",
    "injects": [],
}

DATA_BREACH = {
    "key": "data_breach",
    "title": "Data breach / PII exposure (scaffold)",
    "summary": "Coming soon — to be authored with the CTO + the PR partner.",
    "injects": [],
}

SCENARIOS = {s["key"]: s for s in (BEC, RANSOMWARE, DATA_BREACH)}
