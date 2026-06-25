import streamlit as st

from irp import db, ai
from irp.pdfutil import extract_text
from irp.baseline import BASELINE_BY_KEY
from irp.ui import sidebar_api_key, client_picker, selected_model

st.set_page_config(page_title="Plan & Gaps · IRP Tabletop", page_icon="🛡️", layout="wide")
db.init_db()
api_key = sidebar_api_key()

st.title("Plan & Gaps")
st.caption(
    "Upload the client's IRP/BCP, then run an AI gap analysis against the best-practice "
    "baseline. The AI proposes; you review and accept (suggest-only, human-approved)."
)

client_id = client_picker()
if client_id is None:
    st.stop()

# --- Upload / ingest ------------------------------------------------------
st.subheader("1. Ingest the plan")
existing = db.latest_plan_for_client(client_id)
if existing:
    st.success(f"Current plan: **{existing['source_filename']}** "
               f"(uploaded {existing['uploaded_at']}).")

uploaded = st.file_uploader("Upload an IRP or BCP (PDF)", type=["pdf"])
kind = st.radio("Document type", ["IRP", "BCP"], horizontal=True)
if uploaded is not None and st.button("Ingest plan"):
    with st.spinner("Extracting text…"):
        text = extract_text(uploaded.getvalue())
    if not text:
        st.error("Couldn't extract text from this PDF (it may be a scanned image).")
    else:
        plan_id = db.create_plan(client_id, kind, uploaded.name, text)
        st.session_state[f"plan_{client_id}"] = plan_id
        st.success(f"Ingested {uploaded.name} ({len(text):,} characters). Now run the gap analysis below.")
        existing = db.latest_plan_for_client(client_id)

if not existing:
    st.info("Ingest a plan to enable the gap analysis.")
    st.stop()

plan = existing
with st.expander("Preview extracted plan text"):
    st.text((plan["full_text"] or "")[:6000] or "(empty)")

# --- AI gap analysis ------------------------------------------------------
st.subheader("2. AI gap analysis")
st.caption(f"Runs on Anthropic ({selected_model()} — change it in the sidebar). "
           "No training on your data.")

if st.button("Run AI gap analysis", type="primary"):
    if not api_key:
        st.error("Add your Anthropic API key in the sidebar first.")
    else:
        try:
            with st.spinner("Analyzing the plan against the baseline… (~30s)"):
                analysis = ai.analyze_plan(
                    plan["full_text"], api_key=api_key, model=selected_model()
                )
                sections, gaps = ai.analysis_to_db_rows(analysis)
                db.save_sections(plan["id"], sections)
                db.replace_ai_gaps(client_id, plan["id"], gaps)
            st.session_state[f"overall_{plan['id']}"] = analysis.overall_notes
            st.success(f"Done — {len(gaps)} gaps found across {len(sections)} chapters.")
        except Exception as e:
            st.error(f"Analysis failed: {e}")

overall = st.session_state.get(f"overall_{plan['id']}")
if overall:
    st.info(f"**Overall read:** {overall}")

# --- Review gaps ----------------------------------------------------------
gaps = db.gaps_for_plan(plan["id"])
if gaps:
    st.subheader("3. Review gaps")
    st.caption("Accept the ones to act on, or dismiss. Accepted gaps feed the change punch-list.")
    sev_color = {"high": "🔴", "medium": "🟠", "low": "🟡", "none": "⚪"}

    pending = [g for g in gaps if g["status"] == "ai_suggested"]
    decided = [g for g in gaps if g["status"] != "ai_suggested"]

    def chapter_name(g):
        return BASELINE_BY_KEY.get(g["baseline_key"], (g["baseline_key"], ""))[0]

    # Pending gaps — full cards with Accept / Dismiss.
    for g in pending:
        with st.container(border=True):
            top = st.columns([6, 1, 1])
            top[0].markdown(
                f"{sev_color.get(g['severity'], '⚪')} **{chapter_name(g)}** — _{g['severity']}_  \n"
                f"{g['description']}"
            )
            if g["recommended_change"]:
                top[0].markdown(f"➡️ _Recommended:_ {g['recommended_change']}")
            if top[1].button("Accept", key=f"acc_{g['id']}"):
                db.set_gap_status(g["id"], "validated")
                st.rerun()
            if top[2].button("Dismiss", key=f"dis_{g['id']}"):
                db.set_gap_status(g["id"], "dismissed")
                st.rerun()

    if not pending and decided:
        st.success("All gaps reviewed. ✅")

    # Decided gaps — minimized green (accepted) / red (dismissed) lines with Reopen.
    if decided:
        st.markdown("**Reviewed**")
        for g in decided:
            row = st.columns([8, 1])
            if g["status"] == "validated":
                row[0].success(f"✅ **{chapter_name(g)}** — accepted · _{g['severity']}_")
            else:
                row[0].error(f"❌ **{chapter_name(g)}** — dismissed")
            if row[1].button("Reopen", key=f"re_{g['id']}"):
                db.set_gap_status(g["id"], "ai_suggested")
                st.rerun()

    accepted = [g for g in gaps if g["status"] == "validated"]
    if accepted:
        st.subheader("Change punch-list (accepted)")
        st.caption("This is the actionable output a facilitator hands off for plan updates (B5).")
        st.table([
            {
                "chapter": BASELINE_BY_KEY.get(g["baseline_key"], (g["baseline_key"],))[0],
                "severity": g["severity"],
                "change": g["recommended_change"] or g["description"],
            }
            for g in accepted
        ])
