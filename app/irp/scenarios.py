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

# Impact-to-Business dimensions for the Overview/report (Exigence-style: rating + explanation).
IMPACT_DIMENSIONS = [
    ("operational", "Operational"),
    ("reputation", "PR / Reputation"),
    ("legal", "Legal / Regulatory"),
    ("financial", "Financial"),
]
IMPACT_RATINGS = ["None", "Low", "Medium", "High"]

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
    # Incident-type-specific summary block (report spec Sec 3). kind: text | yesno | choice
    "summary_title": "BEC Summary",
    "summary_fields": [
        ("funds_lost", "Funds lost?", "yesno"),
        ("amount_lost", "Amount lost (USD)", "text"),
        ("mailboxes", "Mailboxes compromised (#)", "text"),
        ("funds_recovered", "Funds recovered?", "choice:Yes,No,Partial"),
        ("source", "Source of compromise", "text"),
        ("fraud_txns", "# fraudulent transactions", "text"),
    ],
}

RANSOMWARE = {
    "key": "ransomware",
    "title": "Ransomware with data exfiltration — double extortion",
    "summary": (
        "Multiple systems are encrypted and a ransom note demands cryptocurrency. The attacker "
        "also claims to have stolen client data and threatens to leak it. Tests the pay/no-pay "
        "decision authority, who-to-contact (insurer, negotiator, forensics, counsel, law "
        "enforcement), downtime/DR ownership, and breach-notification obligations."
    ),
    "injects": [
        {
            "title": "Systems are going dark",
            "category": "Detection",
            "room": (
                "Staff across several teams report that files won't open and shared drives are "
                "unreachable. Within minutes a message appears on multiple screens: your files "
                "have been encrypted, and a countdown demands payment to a crypto wallet."
            ),
            "guidance": (
                "Who hears this first and who do they tell? Is this treated as an IT outage or "
                "immediately as a security incident? Probe: who has the authority to declare a "
                "major incident, and what is the trigger that makes them do it right now?"
            ),
        },
        {
            "title": "It's ransomware, and we're spreading",
            "category": "Detection",
            "room": (
                "IT confirms multiple servers and endpoints are encrypted and the spread is "
                "ongoing. The ransom note names a known ransomware group and threatens to publish "
                "stolen data if you don't engage within 72 hours."
            ),
            "guidance": (
                "Who is named Incident Commander? Email and chat may be compromised or down — what "
                "is the OUT-OF-BAND channel to assemble leadership? Watch for the team diving into "
                "technical recovery before anyone has taken ownership and notified leadership."
            ),
        },
        {
            "title": "They have our data",
            "category": "Escalation",
            "room": (
                "The attacker's leak site shows samples that appear to be real client files — "
                "contracts and a spreadsheet of personal information. This is now double extortion: "
                "encryption plus stolen data."
            ),
            "guidance": (
                "Who owns determining what was actually taken vs. bluffed? This reframes the whole "
                "incident — it is now also a data breach. Probe: who decides the forensics/IR firm "
                "is engaged, and who authorizes it? The plan should name them, not the steps."
            ),
        },
        {
            "title": "Pay or don't pay?",
            "category": "Decision",
            "room": (
                "The demand is $750,000 in cryptocurrency for a decryptor and a 'promise' to delete "
                "the stolen data. The clock is ticking and the team is looking to leadership for a "
                "decision."
            ),
            "guidance": (
                "This is the signature decision. WHO has authority to approve or refuse payment — "
                "is it written down? Who must be in that conversation: cyber insurer, ransom "
                "negotiator, breach counsel, law enforcement? Probe whether the plan names these "
                "contacts and the decision owner, not whether anyone knows how to buy crypto."
            ),
        },
        {
            "title": "The business is stopped",
            "category": "Containment",
            "room": (
                "Core systems are offline and the business effectively cannot operate. People are "
                "asking how long until things are back and whether backups survived the attack."
            ),
            "guidance": (
                "Who OWNS containment and restoration — internal IT, the MSP, or the IR firm — and "
                "who authorizes disruptive actions like taking the network down? What are the "
                "recovery priorities and the RTO/RPO targets? The plan names the owner and DR "
                "provider; it does not contain the rebuild runbook."
            ),
        },
        {
            "title": "Why is everything down?",
            "category": "Comms",
            "room": (
                "Clients and staff are asking why systems are unavailable. A journalist has emailed "
                "asking to confirm a 'cyberattack'. Word is starting to travel."
            ),
            "guidance": (
                "Who approves internal and external messaging, and is the PR/comms partner engaged? "
                "What do you confirm vs. hold while facts are uncertain? Probe the approval path and "
                "whether a holding statement is ready — speed vs. accuracy under pressure."
            ),
        },
        {
            "title": "What are we obligated to report?",
            "category": "Legal",
            "room": (
                "Because personal information was exfiltrated, breach-notification laws and "
                "contractual duties may apply, with regulator deadlines measured in hours to days."
            ),
            "guidance": (
                "Who determines the data scope and the notification obligations? Which regulators, "
                "which clients, by when? Who owns each notification? Watch for uncertainty about who "
                "actually makes the call and tracks the deadlines."
            ),
        },
        {
            "title": "Restored — now account for it",
            "category": "Recovery",
            "room": (
                "Systems are being restored, the decision on payment has been made and executed, and "
                "affected parties are being notified. Leadership wants a written account of what "
                "happened and what it cost."
            ),
            "guidance": (
                "Who produces the written summary and what goes in it (timeline, decisions, cost, "
                "data impact)? Then the readiness question: what in the plan was unclear or missing "
                "during this exercise? Capture those as plan-gap notes for the punch-list and report."
            ),
        },
    ],
    "tasks": [
        ("Detection", "Document the ransom note and affected systems"),
        ("Detection", "Declare a major incident and name the Incident Commander"),
        ("Investigation", "Establish an out-of-band command/comms channel"),
        ("Investigation", "Determine spread and whether data was exfiltrated"),
        ("Investigation", "Confirm whether backups are intact and offline"),
        ("Containment", "Isolate affected systems to stop the spread (decide owner)"),
        ("Containment", "Engage forensics / IR partner (decide owner & authority)"),
        ("Containment", "Engage cyber insurer and ransom negotiator"),
        ("Communication", "Approve internal and client holding statements (PR partner)"),
        ("Communication", "Brief staff on what to say and not say externally"),
        ("Legal/Regulatory", "Determine data / PII exposure scope with counsel"),
        ("Legal/Regulatory", "Assess breach-notification obligations and deadlines"),
        ("Recovery", "Decide pay / no-pay with counsel, insurer, law enforcement"),
        ("Recovery", "Restore from backup and validate; produce written summary"),
        ("Recovery", "Capture plan gaps and corrective actions"),
    ],
    "summary_title": "Ransomware Summary",
    "summary_fields": [
        ("systems_encrypted", "Systems encrypted (#)", "text"),
        ("data_exfiltrated", "Data exfiltrated?", "yesno"),
        ("ransom_demanded", "Ransom demanded", "text"),
        ("ransom_paid", "Ransom paid?", "choice:Yes,No,Partial"),
        ("backups_viable", "Backups viable?", "yesno"),
        ("restored_from", "Restored from", "choice:Backup,Decryptor,Rebuild,Mixed"),
        ("downtime", "Business downtime", "text"),
    ],
}

DATA_BREACH = {
    "key": "data_breach",
    "title": "Data breach / PII exposure",
    "summary": (
        "Sensitive personal data you hold for clients has been exposed and may be in the wrong "
        "hands. Tests scope determination, breach-counsel and regulator timelines, notification "
        "of affected individuals and clients, and the decisions around credit monitoring, "
        "regulators, and law enforcement."
    ),
    "injects": [
        {
            "title": "An outside tip",
            "category": "Detection",
            "room": (
                "A security researcher emails your support inbox: they found a folder of files "
                "containing client personal information openly accessible on the internet, and they "
                "wanted to let you know before going public."
            ),
            "guidance": (
                "Who sees this message and how fast does it reach someone who can act? Is it taken "
                "seriously or dismissed as spam? Probe: who has authority to declare an incident on "
                "the strength of an external tip, and who owns the relationship with the reporter?"
            ),
        },
        {
            "title": "It's real, and it's ours",
            "category": "Detection",
            "room": (
                "IT confirms a storage location holding personal data was misconfigured and "
                "publicly reachable, and access logs show it was downloaded by unknown external "
                "parties."
            ),
            "guidance": (
                "Confirmed exposure. Who formally declares the breach and is named owner? Who is "
                "notified in leadership? Watch for the team rushing to close the hole before anyone "
                "has scoped what was exposed or preserved the access logs as evidence."
            ),
        },
        {
            "title": "Whose data, and how much?",
            "category": "Escalation",
            "room": (
                "Scoping shows the exposed records cover several thousand individuals across three "
                "client organizations, including names, dates of birth, and financial account "
                "details."
            ),
            "guidance": (
                "Who owns determining the exact scope — number of individuals, data types, which "
                "clients? This drives every downstream obligation. Probe whether the plan names who "
                "leads scoping and who the forensics partner is, not how the analysis is done."
            ),
        },
        {
            "title": "Counsel and the clock",
            "category": "Legal",
            "room": (
                "Because the data includes regulated personal and financial information, breach-"
                "notification laws are likely engaged, some with regulator deadlines as short as "
                "72 hours from awareness."
            ),
            "guidance": (
                "Who engages breach counsel and when? Who owns the notification obligations and the "
                "deadline clock? Which regulators apply across the affected clients' jurisdictions? "
                "Probe for a named owner and whether privilege is being protected."
            ),
        },
        {
            "title": "Telling the affected",
            "category": "Comms",
            "room": (
                "You must decide whether and how to notify the affected individuals and the three "
                "client organizations, and whether to offer credit monitoring."
            ),
            "guidance": (
                "Who drafts and who APPROVES the notifications to clients and individuals? Is the "
                "PR/comms partner engaged? Who decides on credit monitoring? Probe the approval path "
                "and the sequencing — clients usually expect to hear from you before their people do."
            ),
        },
        {
            "title": "Close the exposure",
            "category": "Containment",
            "room": (
                "The misconfiguration needs to be closed, credentials rotated, and confirmation "
                "obtained that there is no ongoing access or second exposed location."
            ),
            "guidance": (
                "Who OWNS containment and who authorizes it? Who confirms the exposure is fully "
                "closed and there isn't a second hole? The plan names the owner and any partner to "
                "call — it does not need the remediation steps themselves."
            ),
        },
        {
            "title": "Regulators and law enforcement",
            "category": "Decision",
            "room": (
                "Leadership must decide on formal reports to the relevant privacy regulator(s), "
                "whether to involve law enforcement, and when to notify the cyber insurer."
            ),
            "guidance": (
                "Who makes these calls and on what timeline? Is the sequence and authority clear, or "
                "is the team guessing? Probe whether the contacts (regulator, law enforcement liaison, "
                "insurer) are actually in the plan with current details."
            ),
        },
        {
            "title": "Closed out — account for it",
            "category": "Recovery",
            "room": (
                "The exposure is closed, notifications have gone out, and regulators have been "
                "informed. Affected clients want a written account of what happened and what you've "
                "changed."
            ),
            "guidance": (
                "Who produces the written summary and what goes in it? Then the readiness question: "
                "what in the plan was unclear or missing during this exercise? Capture those as "
                "plan-gap notes for the punch-list and the evidence report."
            ),
        },
    ],
    "tasks": [
        ("Detection", "Triage the report and confirm the exposure is genuine"),
        ("Detection", "Declare the breach and name the owner; notify leadership"),
        ("Investigation", "Preserve access logs and evidence before remediating"),
        ("Investigation", "Determine data types, record counts, and affected clients"),
        ("Investigation", "Engage forensics / IR partner (decide owner)"),
        ("Containment", "Close the exposure and rotate affected credentials (decide owner)"),
        ("Containment", "Confirm no ongoing access or second exposed location"),
        ("Communication", "Approve notifications to affected clients and individuals (PR partner)"),
        ("Communication", "Decide on credit monitoring / support offer"),
        ("Legal/Regulatory", "Engage breach counsel and protect privilege"),
        ("Legal/Regulatory", "Identify applicable regulators and notification deadlines"),
        ("Recovery", "File regulator reports; notify law enforcement and insurer"),
        ("Recovery", "Produce written summary for affected clients"),
        ("Recovery", "Capture plan gaps and corrective actions"),
    ],
    "summary_title": "Data Breach Summary",
    "summary_fields": [
        ("records_exposed", "Records exposed (#)", "text"),
        ("data_types", "Data types exposed", "text"),
        ("individuals_affected", "Individuals affected (#)", "text"),
        ("clients_affected", "Client orgs affected (#)", "text"),
        ("regulators_notified", "Regulators notified?", "yesno"),
        ("deadline_met", "Notification deadline met?", "choice:Yes,No,N/A"),
        ("credit_monitoring", "Credit monitoring offered?", "yesno"),
    ],
}

INSIDER_THREAT = {
    "key": "insider_threat",
    "title": "Insider threat — departing employee data theft",
    "summary": (
        "A departing employee appears to be taking sensitive data on the way out. Tests discreet "
        "coordination across HR, Legal, and IT; evidence preservation for possible legal action; "
        "the authority and timing of cutting access; and a deliberately quiet comms posture."
    ),
    "injects": [
        {
            "title": "A quiet word from a teammate",
            "category": "Detection",
            "room": (
                "A staff member quietly tells their manager that a colleague — who resigned last "
                "week and leaves in ten days — has been downloading large numbers of files and "
                "forwarding emails to a personal address."
            ),
            "guidance": (
                "Who does the manager take this to, and how quietly? This is sensitive and "
                "unconfirmed — handled wrong it tips off the employee or defames an innocent one. "
                "Probe: who decides this is an incident, and who is looped in first (HR? Legal? IT?)."
            ),
        },
        {
            "title": "The pattern is real",
            "category": "Detection",
            "room": (
                "A discreet review of logs confirms unusual activity over the past three weeks: "
                "bulk downloads from a client file share, a USB device, and sync to a personal "
                "cloud account."
            ),
            "guidance": (
                "Confirmed concern. Who owns the investigation, and who must be in the room — HR, "
                "Legal, IT, the employee's manager? Probe the need-to-know discipline: who is "
                "explicitly NOT told yet, and why, to protect the investigation and the person."
            ),
        },
        {
            "title": "What did they take?",
            "category": "Escalation",
            "room": (
                "Early scoping suggests client contact lists, pricing, and proprietary materials "
                "were copied. It's unclear whether any client's regulated data is among it."
            ),
            "guidance": (
                "Who owns determining exactly what was taken and how sensitive it is? This decides "
                "whether it's an internal HR matter or a client-notifiable breach. Probe whether "
                "evidence is being preserved properly in case of litigation."
            ),
        },
        {
            "title": "Cut access — when and how?",
            "category": "Decision",
            "room": (
                "There's pressure to immediately disable the employee's accounts. But they're still "
                "employed for ten days, and acting too soon could tip them off or create legal risk."
            ),
            "guidance": (
                "The signature decision: WHO authorizes revoking access and suspending the employee, "
                "and WHEN? How is it coordinated with HR and counsel so it's clean and defensible? "
                "Probe whether the plan gives anyone clear authority to make this call."
            ),
        },
        {
            "title": "Legal posture",
            "category": "Legal",
            "room": (
                "Counsel weighs the options: enforce the NDA, pursue civil action, involve law "
                "enforcement — each depends on preserved evidence and a clean chain of handling."
            ),
            "guidance": (
                "Who owns the legal strategy and the evidence preservation? Are HR and IT acting in "
                "a way that keeps options open, or have they already compromised the evidence? Probe "
                "for a named owner of the legal/HR coordination."
            ),
        },
        {
            "title": "Contain and confirm",
            "category": "Containment",
            "room": (
                "Once the decision is made, accounts must be disabled, tokens and shared "
                "credentials rotated, and a check done for any backdoors or lingering access — and "
                "the copied data secured or clawed back where possible."
            ),
            "guidance": (
                "Who OWNS the technical containment and who authorizes it? Who confirms there's no "
                "lingering access (e.g. a personal device still synced)? The plan names the owner; "
                "it does not need the step-by-step de-provisioning procedure."
            ),
        },
        {
            "title": "A deliberately quiet message",
            "category": "Comms",
            "room": (
                "People internally are starting to ask why the employee's access was cut. Separately, "
                "if a client's data was taken, that client may need to be told."
            ),
            "guidance": (
                "Who controls the internal narrative on a strict need-to-know basis, and who approves "
                "it? IF client data was taken, who decides whether and how to notify that client? "
                "Probe the restraint here — the default posture is quiet, not a public statement."
            ),
        },
        {
            "title": "Closed out — account for it",
            "category": "Recovery",
            "room": (
                "Access is revoked, the data is secured as far as possible, and legal and HR have a "
                "path forward. Leadership wants a written account of what happened and how exposed "
                "the business was."
            ),
            "guidance": (
                "Who produces the written summary and what goes in it? Then the readiness question: "
                "what in the plan was unclear or missing — especially around who has authority to act "
                "on an insider? Capture those as plan-gap notes for the punch-list and the report."
            ),
        },
    ],
    "tasks": [
        ("Detection", "Take the report to HR and Legal discreetly; decide it's an incident"),
        ("Detection", "Establish a strict need-to-know circle"),
        ("Investigation", "Preserve logs and evidence for possible legal action"),
        ("Investigation", "Determine what data was taken and how sensitive it is"),
        ("Investigation", "Assess whether any client's regulated data is involved"),
        ("Containment", "Decide and authorize timing of access revocation (HR + Legal + IT)"),
        ("Containment", "Disable accounts, rotate shared credentials, check for persistence"),
        ("Containment", "Secure or recover the copied data where possible"),
        ("Communication", "Control the internal narrative on need-to-know basis"),
        ("Communication", "Decide on client notification if their data was taken"),
        ("Legal/Regulatory", "Set legal strategy: NDA, civil action, or law enforcement"),
        ("Legal/Regulatory", "Confirm evidence handling keeps legal options open"),
        ("Recovery", "Produce written summary for leadership"),
        ("Recovery", "Capture plan gaps and corrective actions"),
    ],
    "summary_title": "Insider Threat Summary",
    "summary_fields": [
        ("employee_role", "Departing employee role", "text"),
        ("data_taken", "Data taken", "text"),
        ("exfil_method", "Exfiltration method", "text"),
        ("access_revoked", "Access revoked?", "yesno"),
        ("evidence_preserved", "Evidence preserved?", "yesno"),
        ("legal_action", "Legal action?", "choice:Yes,No,Undecided"),
        ("clients_notified", "Affected clients notified?", "yesno"),
    ],
}

SCENARIOS = {s["key"]: s for s in (BEC, RANSOMWARE, DATA_BREACH, INSIDER_THREAT)}
