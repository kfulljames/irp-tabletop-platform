import streamlit as st

from irp import db, ai, report
from irp.ui import sidebar_api_key, sidebar_client_picker, tenant_banner, selected_model

st.set_page_config(page_title="Evidence Report · IRP Tabletop", page_icon="🛡️", layout="wide")
db.init_db()
client_id = sidebar_client_picker()
api_key = sidebar_api_key()

if client_id is None:
    st.warning("Add a client on the **Clients** page first, then pick it in the sidebar.")
    st.stop()

tenant_banner(db.get_client(client_id))
st.title("Evidence Report")
st.caption("Assemble the SOC 2-grade report from the exercise: summary, debrief, overview, "
           "team, tasks, timeline, plan-gap punch-list, and the confidence vote. AI drafts the "
           "closing notes; you review, approve, and export.")

runs = db.list_runs(client_id)
if not runs:
    st.info("No exercises yet for this client. Run one on the **Run Exercise** page.")
    st.stop()

# Pick a run (completed first, then running).
def run_label(r):
    state = "✅ complete" if r["status"] == "complete" else "▶️ running"
    return f"{r['scenario_title']} — started {r['started_at']} ({state})"

labels = {run_label(r): r["id"] for r in runs}
chosen = st.selectbox("Exercise", list(labels.keys()))
run_id = labels[chosen]

d = report.assemble(run_id)

# --- AI closing notes ---
st.subheader("Closing notes (AI draft)")
cols = st.columns([1, 3])
if cols[0].button("✨ Generate / regenerate", help=f"Drafts with {selected_model()}"):
    if not api_key:
        st.error("Add your Anthropic API key in the sidebar first.")
    else:
        try:
            with st.spinner("Drafting closing notes…"):
                text = ai.closing_notes(report.context_for_ai(d), api_key=api_key, model=selected_model())
                db.set_kv(run_id, "closing_notes", text)
            st.rerun()
        except Exception as e:
            st.error(f"Generation failed: {e}")

edited = st.text_area("Closing notes (editable)", value=d["closing_notes"], height=200,
                      placeholder="Click Generate, or write the closing notes yourself.")
if st.button("Save closing notes"):
    db.set_kv(run_id, "closing_notes", edited)
    st.success("Saved.")
    st.rerun()

# --- on-screen preview of the assembled report ---
st.divider()
st.subheader("Report preview")
d = report.assemble(run_id)  # refresh after edits

st.markdown(f"**{d['client']} · {d['scenario_title']}**  \n"
            f"Started {d['started_at']} · Resolved {d['resolved_at'] or '—'} · "
            f"Total {d['total_time']} · TZ {d['timezone'] or 'local'}")

with st.container(border=True):
    st.markdown("**1. Executive summary**")
    st.write(d["closing_notes"] or "_(not generated yet)_")

    st.markdown("**2. Debrief**")
    st.write(f"✅ Right: {d['debrief']['right'] or '—'}")
    st.write(f"⚠️ Wrong: {d['debrief']['wrong'] or '—'}")
    st.write(f"🔧 Improve: {d['debrief']['improve'] or '—'}")

    st.markdown("**3. Overview**")
    ov = d["overview"]
    if ov.get("latest_status") or ov.get("detection_summary"):
        st.write(f"Latest status: {ov.get('latest_status', '—')}")
        st.write(f"Detection: {ov.get('detection_summary', '—')}")
    if d["impact"]:
        st.write("Impact to business: " + " · ".join(
            f"{i['dimension']} **{i['rating']}**" for i in d["impact"]))
    if d["summary_fields"]:
        st.write(f"{d['summary_title']}: " + " · ".join(
            f"{s['label']}: {s['value']}" for s in d["summary_fields"]))

    st.markdown(f"**4. Team** ({len(d['participants'])})")
    st.caption(" · ".join(f"{p['full_name']} ({'Observer' if p['role']=='observer' else (p.get('incident_role') or 'participant')})"
                          for p in d["participants"]) or "—")

    done = sum(1 for t in d["tasks"] if t["status"] == "done")
    st.markdown(f"**5. Incident tasks** — {done}/{len(d['tasks'])} done")

    st.markdown(f"**6. Timeline** — {len(d['events'])} events")

    st.markdown(f"**7. Plan-gap punch-list** — {len(d['gaps'])} validated")
    for g in d["gaps"]:
        st.write(f"- ({g['severity']}) {g['recommended_change'] or g['description']}")

    st.markdown("**8. Confidence vote**")
    if d["votes"]:
        st.write(" · ".join(f"{v.get('voter') or 'Participant'}: {v['score']}" for v in d["votes"])
                 + (f"  →  **avg {d['vote_avg']}/10**" if d["vote_avg"] is not None else ""))
    else:
        st.write("—")

# --- approval gate + export (B12) ---
st.divider()
st.subheader("Approve & export")
approved = d["report_status"] == "approved"
new_approved = st.checkbox("✅ Approve this report (facilitator sign-off before export)", value=approved)
if new_approved != approved:
    db.set_kv(run_id, "report_status", "approved" if new_approved else "draft")
    st.rerun()

if not new_approved:
    st.info("Approve the report to enable export.")
else:
    fname = f"{d['client'].replace(' ', '_')}_evidence_report".lower()
    ecols = st.columns(2)
    ecols[0].download_button("⬇️ Download Word (.docx)", data=report.build_docx(d),
                             file_name=f"{fname}.docx",
                             mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    ecols[1].download_button("⬇️ Download structured (.json)", data=report.build_structured(d),
                             file_name=f"{fname}.json", mime="application/json")
    st.caption("PDF: open the Word file and 'Save as PDF' for now — native PDF export is a fast-follow.")
