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
st.caption("Click a client to rename it, change its industry, or delete it.")
clients = db.list_clients()
if not clients:
    st.info("No clients yet.")
else:
    for c in clients:
        plan = db.latest_plan_for_client(c["id"])
        status = f"plan ingested ({plan['source_filename']})" if plan else "no plan yet"
        with st.expander(f"{c['name']}  ·  {status}"):
            with st.form(f"edit_{c['id']}"):
                new_name = st.text_input("Name", value=c["name"], key=f"name_{c['id']}")
                new_industry = st.text_input(
                    "Industry", value=c["industry"] or "", key=f"ind_{c['id']}"
                )
                if st.form_submit_button("Save changes"):
                    if new_name.strip():
                        db.update_client(c["id"], new_name.strip(), new_industry.strip() or None)
                        st.success("Saved.")
                        st.rerun()
                    else:
                        st.error("Name can't be empty.")

            st.markdown("**Danger zone**")
            confirm = st.checkbox(
                "Yes, delete this client and all its plans/gaps",
                key=f"confdel_{c['id']}",
            )
            if st.button("Delete client", key=f"del_{c['id']}", disabled=not confirm):
                db.delete_client(c["id"])
                if st.session_state.get("client_id") == c["id"]:
                    st.session_state.pop("client_id", None)
                st.warning(f"Deleted '{c['name']}'.")
                st.rerun()
