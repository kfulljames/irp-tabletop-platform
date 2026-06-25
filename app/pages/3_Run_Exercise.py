import json

import streamlit as st

from irp import db
from irp.scenarios import (SCENARIOS, INCIDENT_ROLES, PHASES, CATEGORY_TO_PHASE,
                           IMPACT_DIMENSIONS, IMPACT_RATINGS)
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
        db.seed_tasks(run_id, scenario.get("tasks", []))
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

# Current inject (computed once; used by phase bar + deck).
idx, inj = 0, None
if injects:
    idx = max(0, min(run["current_inject"], len(injects) - 1))
    inj = injects[idx]

# --- Phase tracker (thin, always on) ---
cur_phase = CATEGORY_TO_PHASE.get(inj["category"], "") if inj else ""
chips = []
for ph in PHASES:
    on = (ph == cur_phase)
    chips.append(
        f"<span style='display:inline-block;padding:5px 12px;margin:2px;border-radius:14px;"
        f"font-size:0.86rem;font-weight:600;"
        f"background:{'#157347' if on else '#2b2f36'};"
        f"color:{'#fff' if on else '#9aa0a6'};'>{ph}</span>"
    )
st.markdown("&nbsp;&nbsp;".join(chips), unsafe_allow_html=True)

# --- Overview + Task checklist (collapsed to keep the view simple) ---
with st.expander("📋 Overview — feeds the evidence report"):
    ov = db.get_overview(run["id"])
    ovkv = db.get_kv(run["id"])
    with st.form(f"ov_{run['id']}"):
        latest_status = st.text_area("Latest status", value=ov.get("latest_status", ""),
                                     placeholder="e.g. Identifying scope and containing the compromise.")
        detection_summary = st.text_input("Detection summary", value=ov.get("detection_summary", ""),
                                          placeholder="e.g. Client reported payment to fraudulent bank details.")
        c1, c2 = st.columns(2)
        how_discovered = c1.text_input("How discovered", value=ov.get("how_discovered", ""))
        when_discovered = c2.text_input("When discovered", value=ov.get("when_discovered", ""))
        who_discovered = c1.text_input("Who discovered it", value=ov.get("who_discovered", ""))
        impacted = c2.text_input("Users / assets impacted", value=ov.get("impacted", ""))
        history = st.text_area("Other pertinent history", value=ov.get("history", ""))

        st.markdown("**Impact to Business**")
        impact_vals = {}
        for key, label in IMPACT_DIMENSIONS:
            ic = st.columns([1, 3])
            cur_r = ovkv.get(f"impact_{key}_rating", "None")
            rating = ic[0].selectbox(
                label, IMPACT_RATINGS,
                index=IMPACT_RATINGS.index(cur_r) if cur_r in IMPACT_RATINGS else 0,
                key=f"imp_{run['id']}_{key}_r")
            expl = ic[1].text_input(
                f"{label} explanation", value=ovkv.get(f"impact_{key}_expl", ""),
                key=f"imp_{run['id']}_{key}_e", label_visibility="collapsed",
                placeholder=f"{label} impact — explanation")
            impact_vals[f"impact_{key}_rating"] = rating
            impact_vals[f"impact_{key}_expl"] = expl

        summary_vals = {}
        sfields = scenario.get("summary_fields", [])
        if sfields:
            st.markdown(f"**{scenario.get('summary_title', 'Summary')}**")
            for fkey, flabel, kind in sfields:
                cur = ovkv.get(f"summary_{fkey}", "")
                if kind == "yesno":
                    opts = ["", "Yes", "No"]
                    val = st.selectbox(flabel, opts, index=opts.index(cur) if cur in opts else 0,
                                       key=f"sum_{run['id']}_{fkey}")
                elif kind.startswith("choice:"):
                    opts = [""] + kind.split(":", 1)[1].split(",")
                    val = st.selectbox(flabel, opts, index=opts.index(cur) if cur in opts else 0,
                                       key=f"sum_{run['id']}_{fkey}")
                else:
                    val = st.text_input(flabel, value=cur, key=f"sum_{run['id']}_{fkey}")
                summary_vals[f"summary_{fkey}"] = val

        if st.form_submit_button("Save overview"):
            db.save_overview(run["id"], {
                "latest_status": latest_status, "detection_summary": detection_summary,
                "how_discovered": how_discovered, "when_discovered": when_discovered,
                "who_discovered": who_discovered, "impacted": impacted, "history": history,
            })
            db.set_kv_many(run["id"], {**impact_vals, **summary_vals})
            st.success("Overview saved.")

with st.expander("✅ Incident task checklist (optional)"):
    tasks = db.list_tasks(run["id"])
    if not tasks and scenario.get("tasks"):   # seed runs that predate the checklist
        db.seed_tasks(run["id"], scenario["tasks"])
        tasks = db.list_tasks(run["id"])
    done_n = sum(1 for t in tasks if t["status"] == "done")
    st.caption(f"{done_n}/{len(tasks)} done — tick off steps as the room covers them.")
    with st.form(f"tasks_{run['id']}"):
        new_vals = {}
        last_phase = None
        for t in tasks:
            if t["phase"] != last_phase:
                st.markdown(f"**{t['phase']}**")
                last_phase = t["phase"]
            cc = st.columns([0.6, 6, 3])
            done = cc[0].checkbox("done", value=(t["status"] == "done"),
                                  key=f"tk_{t['id']}", label_visibility="collapsed")
            title_md = f"~~{t['title']}~~" if done else t["title"]
            cc[1].markdown(title_md)
            asg = cc[2].text_input("assignee", value=t["assignee"] or "", key=f"ta_{t['id']}",
                                   placeholder="assign to…", label_visibility="collapsed")
            new_vals[t["id"]] = ("done" if done else "pending", asg)
        if st.form_submit_button("Save checklist"):
            for tid, (stat, asg) in new_vals.items():
                db.set_task(tid, stat, asg)
            st.rerun()

st.divider()

# --- Inject deck (full-width hero card) ---
st.subheader("Inject deck")
if injects:
    nav = st.columns([1, 3, 1, 4])
    if nav[0].button("◀ Prev", disabled=idx == 0, use_container_width=True):
        db.set_current_inject(run["id"], idx - 1)
        st.rerun()
    nav[1].markdown(f"<div style='text-align:center;padding-top:6px'>Inject "
                    f"<b>{idx + 1}</b> of {len(injects)} · <i>{inj['category']}</i></div>",
                    unsafe_allow_html=True)
    if nav[2].button("Next ▶", disabled=idx >= len(injects) - 1, use_container_width=True):
        new_idx = idx + 1
        db.set_current_inject(run["id"], new_idx)
        db.add_event(run["id"], "Inject", None,
                     f"Inject {new_idx + 1}: {injects[new_idx]['title']}", timezone=run_tz)
        st.rerun()

    with st.container(border=True):
        st.markdown(f"### {inj['title']}")
        st.markdown(
            f"<div style='font-size:1.15rem; line-height:1.7;'>{inj['room']}</div>",
            unsafe_allow_html=True,
        )
    with st.expander("🎙️ Facilitator guidance (don't read aloud)"):
        st.markdown(inj["guidance"])
else:
    st.info("This scenario has no injects authored yet.")

# --- Capture (full width) ---
st.divider()
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

with st.container(border=True):
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

# --- close-out: debrief + confidence vote ---
st.divider()
with st.expander("🏁 Close-out — debrief & confidence vote"):
    ckv = db.get_kv(run["id"])
    with st.form(f"debrief_{run['id']}"):
        st.markdown("**Debrief**")
        d_right = st.text_area("What went right", value=ckv.get("debrief_right", ""))
        d_wrong = st.text_area("What went wrong", value=ckv.get("debrief_wrong", ""))
        d_improve = st.text_area("What can be improved", value=ckv.get("debrief_improve", ""))
        if st.form_submit_button("Save debrief"):
            db.set_kv_many(run["id"], {"debrief_right": d_right, "debrief_wrong": d_wrong,
                                       "debrief_improve": d_improve})
            st.success("Debrief saved.")

    st.markdown("**Team confidence vote** (EOS-style, 1–10)")
    existing_votes = {v["person_id"]: v["score"] for v in db.list_votes(run["id"])}
    if not actors:
        st.caption("Add participants to collect votes.")
    else:
        with st.form(f"vote_{run['id']}"):
            vote_inputs = {}
            for p in actors:
                vote_inputs[p["id"]] = st.slider(
                    p["full_name"], 1, 10, value=existing_votes.get(p["id"], 7),
                    key=f"vote_{run['id']}_{p['id']}")
            if st.form_submit_button("Save votes"):
                for pid, sc in vote_inputs.items():
                    db.set_vote(run["id"], pid, sc)
                st.success("Votes saved.")

# --- end ---
st.divider()
if st.button("⏹️ Resolve & end exercise"):
    db.add_event(run["id"], "Resolution", None, "Incident resolved; exercise ended.",
                 timezone=run_tz)
    db.resolve_run(run["id"], timezone=run_tz)
    st.success("Exercise ended. Head to **Evidence Report** to generate the report.")
    st.rerun()
