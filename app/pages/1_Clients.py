import streamlit as st

from irp import db
from irp.ui import sidebar_api_key

st.set_page_config(page_title="Clients · IRP Tabletop", page_icon="🛡️", layout="wide")
db.init_db()
sidebar_api_key()

st.title("Clients")
st.caption("Each client is a separate organization (its own plans, contacts, run history).")

with st.form("new_client"):
    st.subheader("Add a client")
    name = st.text_input("Organization name", placeholder="e.g. the MSP")
    industry = st.text_input("Industry (optional)", placeholder="e.g. Managed IT services")
    submitted = st.form_submit_button("Create client")
    if submitted:
        if name.strip():
            cid = db.create_client(name.strip(), industry.strip() or None)
            st.session_state["client_id"] = cid
            st.success(f"Created '{name}'. Head to **Plan & Gaps** to ingest their plan.")
        else:
            st.error("Please enter an organization name.")

st.divider()
st.subheader("Existing clients")
clients = db.list_clients()
if not clients:
    st.info("No clients yet.")
else:
    for c in clients:
        plan = db.latest_plan_for_client(c["id"])
        status = f"plan ingested ({plan['source_filename']})" if plan else "no plan yet"
        st.markdown(f"**{c['name']}** — {c['industry'] or 'industry n/a'} · _{status}_")
