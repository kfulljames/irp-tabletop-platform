import json

import streamlit as st

from irp import db
from irp.scenarios import SCENARIOS, INCIDENT_ROLES
from irp.ui import sidebar_api_key, sidebar_client_picker, tenant_banner

st.set_page_config(page_title="Run Exercise · IRP Tabletop", page_icon="🛡️", layout="wide")
db.init_db()
client_id = sidebar_client_picker()
sidebar_api_key()

if client_id is None:
    st.warning("Add a client on the **Clients** page first, then pick it in the sidebar.")
    st.stop()

tenant_banner(db.get_client(client_id))
st.title("Run Exercise")

# Timezone choices for the exercise — all timestamps are stamped/shown in the chosen zone.
TIMEZONES = {
    "Pacific (Vancouver / Los Angeles)": "America/Vancouver",
    "Mountain (Calgary / Denver)": "America/Edmonton",
    "Central (Winnipeg / Chicago)": "America/Winnipeg",
    "Eastern (Toronto / New York)": "America/Toronto",
    "Atlantic (Halifax)": "America/Halifax",
    "Newfoundland (St. John's)": "America/St_Johns",
    "UTC": "UTC",
}
TZ_LABEL = {v: k for k, v in TIMEZONES.items()}


# ==========================================================================
# People roster (setup wizard slice, Q10) — needed for act-as attribution.
# ==========================================================================
people = db.list_people(client_id)
with st.expander(f"👥 People & roles  ·  {len(people)} on roster", expanded=not people):
    st.caption("Add the real people who'll take part. Scenarios use their actual names (Q9).")
    with st.form("add_person", clear_on_submit=True):
        cols = st.columns([3, 3, 3, 1])
        name = cols[0].text_input("Full name", placeholder="e.g. the CEO")
        title = cols[1].text_input("Title", placeholder="e.g. CEO")
        role = cols[2].selectbox("Incident role", INCIDENT_ROLES)
        cols[3].markdown("&nbsp;")
        if cols[3].form_submit_button("Add") and name.strip():
            db.add_person(client_id, name.strip(), title.strip() or None, role)
            st.rerun()
    for p in people:
        c = st.columns([5, 4, 1])
        c[0].markdown(f"**{p['full_name']}**")
        c[1].caption(f"{p['title'] or '—'} · {p['incident_role'] or '—'}")
        if c[2].button("🗑️", key=f"delp_{p['id']}", help="Remove person"):
            db.delete_person(p["id"])
            st.rerun()

active = db.active_run_for_client(client_id)

# ==========================================================================
# START a new exercise
# ==========================================================================
if not active:
    st.subheader("Start a new exercise")
    if not people:
        st.info("Add at least one person above before starting.")
        st.stop()

    runnable = {k: s for k, s in SCENARIOS.items() if s["injects"]}
    labels = {f"{s['title']}": k for k, s in SCENARIOS.items()}
    chosen = st.selectbox("Scenario", list(labels.keys()))
    skey = labels[chosen]
    scenario = SCENARIOS[skey]
    st.caption(scenario["summary"])
    if not scenario["injects"]:
        st.warning("This scenario isn't authored yet. Pick BEC to run a full exercise.")
        st.stop()

    st.markdown("**Who's in the room?**")
    opts = {f"{p['full_name']} — {p['title'] or p['incident_role'] or ''}": p["id"] for p in people}
    chosen_parts = st.multiselect("Participants (act on their own behalf)", list(opts.keys()),
                                  default=list(opts.keys()))
    chosen_obs = st.multiselect("Observers (present, non-acting)", list(opts.keys()))

    tz_label = st.selectbox("Timezone for this exercise (all timestamps use it)",
                            list(TIMEZONES.keys()))
    tz = TIMEZONES[tz_label]

    if st.button("▶️ Start exercise", type="primary"):
        run_id = db.create_run(client_id, skey, scenario["title"], timezone=tz)
        for lab in chosen_parts:
            db.add_participant(run_id, opts[lab], "participant")
        for lab in chosen_obs:
            if lab not in chosen_parts:
                db.add_participant(run_id, opts[lab], "observer")
        db.add_event(run_id, "Incident start", None,
                     f"Exercise started: {scenario['title']}", timezone=tz)
        st.rerun()

    runs = db.list_runs(client_id)
    done = [r for r in runs if r["status"] == "complete"]
    if done:
        st.divider()
        st.markdown("**Past exercises**")
        for r in done:
            st.caption(f"• {r['scenario_title']} — started {r['started_at']}, "
                       f"resolved {r['resolved_at']}")
    st.stop()

# ==========================================================================
# LIVE CONSOLE
# ==========================================================================
run = active
scenario = SCENARIOS.get(run["scenario_key"], {"title": run["scenario_title"], "injects": []})
injects = scenario["injects"]
participants = db.list_participants(run["id"])
actors = [p for p in participants if p["role"] == "participant"]
observers = [p for p in participants if p["role"] == "observer"]

# --- header ---
run_tz = run["timezone"] if "timezone" in run.keys() else None
tz_friendly = TZ_LABEL.get(run_tz, run_tz or "local")
hcol = st.columns([4, 3])
hcol[0].markdown(f"**Running:** {run['scenario_title']}")
hcol[1].caption(f"Started {run['started_at']} · 🌐 All times: {tz_friendly}")

names = " · ".join(p["full_name"] for p in actors) or "—"
obs_names = " · ".join(p["full_name"] for p in observers)
st.caption(f"👥 In the room: {names}" + (f"   |   👁️ Observers: {obs_names}" if obs_names else ""))

st.divider()
left, right = st.columns([1, 1])

# --- LEFT: inject deck ---
with left:
    st.subheader("Inject deck")
    if injects:
        idx = max(0, min(run["current_inject"], len(injects) - 1))
        inj = injects[idx]
        nav = st.columns([1, 2, 1])
        if nav[0].button("◀ Prev", disabled=idx == 0):
            db.set_current_inject(run["id"], idx - 1)
            st.rerun()
        nav[1].markdown(f"<div style='text-align:center'>Inject <b>{idx + 1}</b> of {len(injects)}"
                        f" · <i>{inj['category']}</i></div>", unsafe_allow_html=True)
        if nav[2].button("Next ▶", disabled=idx >= len(injects) - 1):
            new_idx = idx + 1
            db.set_current_inject(run["id"], new_idx)
            db.add_event(run["id"], "Inject", None,
                         f"Inject {new_idx + 1}: {injects[new_idx]['title']}", timezone=run_tz)
            st.rerun()

        with st.container(border=True):
            st.markdown(f"### {inj['title']}")
            st.markdown(inj["room"])
        with st.expander("🎙️ Facilitator guidance (don't read aloud)"):
            st.markdown(inj["guidance"])
    else:
        st.info("This scenario has no injects authored yet.")

# --- RIGHT: capture ---
with right:
    st.subheader("Capture")
    actor_opts = {f"{p['full_name']} ({p['incident_role'] or p['title'] or 'participant'})": p["id"]
                  for p in actors}
    actor_opts["Facilitator (you)"] = None

    # Capture type as a row of buttons (faster + reads better than a dropdown).
    TYPE_BUTTONS = [
        ("Business decision", "⚖️ Decision"),
        ("Comms decision", "📣 Comms"),
        ("Task (assigned out)", "🛠️ Task"),
        ("Status update", "📋 Status"),
        ("Note / plan gap", "📝 Plan gap"),
    ]
    sel_key = f"ctype_{run['id']}"
    active = st.session_state.get(sel_key, TYPE_BUTTONS[0][0])
    st.caption("What happened? Pick a type:")
    bcols = st.columns(len(TYPE_BUTTONS))
    for i, (t, label) in enumerate(TYPE_BUTTONS):
        if bcols[i].button(label, key=f"typ_{run['id']}_{i}", use_container_width=True,
                           type="primary" if t == active else "secondary"):
            st.session_state[sel_key] = t
            st.rerun()
    ctype = st.session_state.get(sel_key, TYPE_BUTTONS[0][0])

    with st.form(f"cap_{run['id']}", clear_on_submit=True):
        st.markdown(f"**{ctype}**")
        act_label = st.selectbox(
            "Acting as", list(actor_opts.keys()),
            help="The facilitator logs each action on behalf of the person who made it (Q6). "
                 "When participants log in themselves, this auto-fills to them.",
        )
        desc, payload, gap = "", None, None

        if ctype == "Business decision":
            desc = st.text_area("Decision & reasoning",
                                placeholder="e.g. CEO authorized engaging breach counsel and notifying the insurer.")
        elif ctype == "Comms decision":
            who = st.text_input("Who (audience)", placeholder="e.g. All clients")
            what = st.text_input("What (message)", placeholder="e.g. Verify banking details by phone before paying")
            how = st.selectbox("How (channel)", ["Phone", "Email", "SMS", "In person", "Public statement", "Other"])
            reasoning = st.text_area("Reasoning", placeholder="Why this, why now")
            desc = f"To {who or '—'}: {what or '—'} (via {how}). Reason: {reasoning or '—'}"
            payload = {"who": who, "what": what, "how": how, "reasoning": reasoning}
        elif ctype == "Task (assigned out)":
            task = st.text_input("Task", placeholder="e.g. Remove mailbox forwarding rules; confirm no other mailboxes affected")
            assignee = st.text_input("Assigned to", placeholder="e.g. MSP / forensics partner")
            desc = f"{task or '—'} → assigned to {assignee or '—'}"
            payload = {"task": task, "assigned_to": assignee}
        elif ctype == "Status update":
            desc = st.text_area("Status / overview update")
        elif ctype == "Note / plan gap":
            desc = st.text_area("What was unclear, missing, or needs to change in the plan?")
            sev = st.selectbox("Severity", ["high", "medium", "low"], index=1)
            add_pl = st.checkbox("Add to the change punch-list", value=True)
            gap = (sev, add_pl)

        if st.form_submit_button("➕ Log to timeline") and desc.strip():
            db.add_event(run["id"], ctype, actor_opts[act_label], desc.strip(),
                         json.dumps(payload) if payload else None, timezone=run_tz)
            if ctype == "Note / plan gap" and gap and gap[1]:
                db.add_room_gap(client_id, title=desc.strip()[:80], description=desc.strip(),
                                severity=gap[0])
            st.rerun()

# --- timeline ---
st.divider()
st.subheader("Timeline (evidence)")
events = db.list_events(run["id"], newest_first=True)
if not events:
    st.caption("No events captured yet.")
else:
    badge = {
        "Incident start": "🟢", "Inject": "📨", "Business decision": "⚖️",
        "Comms decision": "📣", "Task (assigned out)": "🛠️", "Status update": "📋",
        "Note / plan gap": "📝", "Resolution": "✅",
    }
    for e in events:
        t = e["occurred_at"].split(" ")[-1] if e["occurred_at"] else ""
        who = f" · **{e['acting_name']}**" if e["acting_name"] else ""
        c = st.columns([11, 1])
        c[0].markdown(f"{badge.get(e['type'], '•')} `{t}`  _{e['type']}_{who}  \n{e['description']}")
        if c[1].button("🗑️", key=f"dele_{e['id']}", help="Delete event"):
            db.delete_event(e["id"])
            st.rerun()

# --- end ---
st.divider()
if st.button("⏹️ Resolve & end exercise"):
    db.add_event(run["id"], "Resolution", None, "Incident resolved; exercise ended.",
                 timezone=run_tz)
    db.resolve_run(run["id"], timezone=run_tz)
    st.success("Exercise ended. Head to **Evidence Report** to generate the report.")
    st.rerun()
