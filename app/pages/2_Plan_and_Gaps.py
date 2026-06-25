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
    "Upload the client's plan documents (e.g. the policy AND the procedure, or an IRP and a "
    "BCP), then run one AI gap analysis across all of them. The AI proposes; you review and "
    "accept (suggest-only, human-approved)."
)

client_id = client_picker()
if client_id is None:
    st.stop()

# --- 1. Ingest documents --------------------------------------------------
st.subheader("1. Ingest the plan documents")

docs = db.list_documents(client_id)
if docs:
    st.markdown("**Documents on file** (all are read together):")
    for d in docs:
        cols = st.columns([7, 2, 1])
        cols[0].markdown(f"📄 **{d['source_filename']}**")
        cols[1].caption(f"{len(d['full_text'] or ''):,} chars")
        if cols[2].button("Remove", key=f"rmdoc_{d['id']}"):
            db.delete_document(d["id"])
            st.rerun()
else:
    st.info("No documents yet — upload at least one below.")

uploaded = st.file_uploader(
    "Upload one or more PDFs (policy, procedure, IRP, BCP…)",
    type=["pdf"],
    accept_multiple_files=True,
)
default_label = st.text_input(
    "Label for these uploads (optional)", placeholder="e.g. Policy, Procedure, IRP, BCP"
)
if uploaded and st.button("Add document(s)"):
    added, skipped = 0, []
    for f in uploaded:
        text = extract_text(f.getvalue())
        if text:
            db.add_document(client_id, default_label.strip() or None, f.name, text)
            added += 1
        else:
            skipped.append(f.name)
    if added:
        st.success(f"Added {added} document(s).")
    if skipped:
        st.warning("Couldn't extract text (scanned image?): " + ", ".join(skipped))
    st.rerun()

docs = db.list_documents(client_id)
if not docs:
    st.stop()

with st.expander("Preview combined text the AI will read"):
    st.text(db.combined_text(client_id)[:8000] or "(empty)")

# --- 2. AI gap analysis ---------------------------------------------------
st.subheader("2. AI gap analysis")
st.caption(f"Reads all {len(docs)} document(s) together. Runs on Anthropic "
           f"({selected_model()} — change it in the sidebar). No training on your data.")

if st.button("Run AI gap analysis", type="primary"):
    if not api_key:
        st.error("Add your Anthropic API key in the sidebar first.")
    else:
        try:
            with st.spinner("Analyzing the plan against the baseline… (~30s)"):
                analysis = ai.analyze_plan(
                    db.combined_text(client_id), api_key=api_key, model=selected_model()
                )
                sections, gaps = ai.analysis_to_db_rows(analysis)
                db.save_sections(client_id, sections)
                db.replace_ai_gaps(client_id, gaps)
            st.session_state[f"overall_{client_id}"] = analysis.overall_notes
            st.success(f"Done — {len(gaps)} gaps found across {len(sections)} chapters.")
        except Exception as e:
            st.error(f"Analysis failed: {e}")

overall = st.session_state.get(f"overall_{client_id}")
if overall:
    st.info(f"**Overall read:** {overall}")

# --- 3. Review gaps -------------------------------------------------------
gaps = db.gaps_for_client(client_id)
if gaps:
    st.subheader("3. Review gaps")
    st.caption("Accept the ones to act on, or dismiss. Accepted gaps feed the change punch-list.")
    sev_color = {"high": "🔴", "medium": "🟠", "low": "🟡", "none": "⚪"}

    pending = [g for g in gaps if g["status"] == "ai_suggested"]
    decided = [g for g in gaps if g["status"] != "ai_suggested"]

    def chapter_name(g):
        return BASELINE_BY_KEY.get(g["baseline_key"], (g["baseline_key"], ""))[0]

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
                "chapter": chapter_name(g),
                "severity": g["severity"],
                "change": g["recommended_change"] or g["description"],
            }
            for g in accepted
        ])
