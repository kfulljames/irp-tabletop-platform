import streamlit as st

from irp import db, ai
from irp.pdfutil import extract_text
from irp.baseline import BASELINE_BY_KEY
from irp.ui import sidebar_api_key, sidebar_client_picker, tenant_banner, selected_model

st.set_page_config(page_title="Plan & Gaps · IRP Tabletop", page_icon="🛡️", layout="wide")
db.init_db()
client_id = sidebar_client_picker()
api_key = sidebar_api_key()

if client_id is None:
    st.warning("Add a client on the **Clients** page first, then pick it in the sidebar.")
    st.stop()

tenant_banner(db.get_client(client_id))

st.title("Plan & Gaps")
st.caption(
    "Upload the client's plan documents (e.g. the policy AND the procedure, or an IRP and a "
    "BCP), then run one AI gap analysis across all of them. The AI proposes; you review and "
    "accept (suggest-only, human-approved)."
)

# --- 1. Plan documents ----------------------------------------------------
st.subheader("1. Plan documents")

DOC_TYPES = ["Policy", "Procedure", "IRP", "BCP", "Other"]


def guess_type(filename: str) -> str:
    n = filename.lower()
    if "polic" in n:
        return "Policy"
    if "procedure" in n or "contact" in n:
        return "Procedure"
    if "continuity" in n or "bcp" in n or "disaster" in n or "recovery" in n:
        return "BCP"
    if "incident" in n or "irp" in n:
        return "IRP"
    return "Other"


# Existing documents, shown as tidy cards.
docs = db.list_documents(client_id)
if docs:
    st.caption("These are read together as one plan. Set each one's type, or remove it.")
    for d in docs:
        with st.container(border=True):
            c = st.columns([6, 2.5, 0.8])
            c[0].markdown(f"📄 **{d['source_filename']}**")
            c[0].caption(f"✓ text extracted · {len(d['full_text'] or ''):,} characters")
            cur = d["label"] if d["label"] in DOC_TYPES else "Other"
            picked = c[1].selectbox(
                "Type", DOC_TYPES, index=DOC_TYPES.index(cur),
                key=f"lbl_{d['id']}", label_visibility="collapsed",
            )
            if picked != (d["label"] or "Other"):
                db.update_document_label(d["id"], picked)
            if c[2].button("🗑️", key=f"rm_{d['id']}", help="Remove this document"):
                db.delete_document(d["id"])
                st.rerun()

# Drag-and-drop dropzone — ingests the moment files are selected, then resets.
flash = st.session_state.pop("upload_flash", None)
if flash:
    for level, msg in flash:
        getattr(st, level)(msg)

rev = st.session_state.get("uprev", 0)
files = st.file_uploader(
    "Drag & drop the plan PDFs here  —  or click to browse",
    type=["pdf"], accept_multiple_files=True, key=f"up_{client_id}_{rev}",
)
if files:
    existing = {d["source_filename"] for d in db.list_documents(client_id)}
    added, dup, img = 0, [], []
    for f in files:
        if f.name in existing:
            dup.append(f.name)
            continue
        text = extract_text(f.getvalue())
        if text:
            db.add_document(client_id, guess_type(f.name), f.name, text)
            added += 1
        else:
            img.append(f.name)
    msgs = []
    if added:
        msgs.append(("success", f"Added {added} document(s)."))
    if dup:
        msgs.append(("info", "Already on file (skipped): " + ", ".join(dup)))
    if img:
        msgs.append(("warning", "Couldn't read (scanned image?): " + ", ".join(img)))
    st.session_state["upload_flash"] = msgs
    st.session_state["uprev"] = rev + 1   # reset the dropzone so it's ready for more
    st.rerun()

docs = db.list_documents(client_id)
if not docs:
    st.info("Add the client's plan documents above to get started.")
    st.stop()

with st.expander("Preview the combined text the AI will read"):
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
