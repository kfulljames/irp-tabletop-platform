"""IRP Tabletop Platform — local prototype (Home / dashboard).

Run with:  streamlit run app/Home.py
"""
import streamlit as st

from irp import db
from irp.ui import sidebar_api_key

st.set_page_config(page_title="IRP Tabletop Platform", page_icon="🛡️", layout="wide")

db.init_db()
sidebar_api_key()

st.title("🛡️ IRP Tabletop Platform — prototype")
st.caption(
    "Executive incident-response tabletop exercises that produce a SOC 2-grade evidence "
    "report. Local prototype (v1 = tabletop)."
)

st.markdown(
    """
This early prototype proves the core flow end to end:

1. **Clients** — create a client organization.
2. **Plan & Gaps** — upload the client's IRP/BCP (PDF) and run an **AI gap analysis**
   against a best-practice baseline.
3. **Run Exercise** — _(coming next)_ drive the scenario with act-as attribution, a live
   clock, and typed capture.
4. **Evidence Report** — _(coming next)_ generate the timestamped report + change punch-list.

Use the pages in the left sidebar. Add your Anthropic API key in the sidebar to enable the
AI gap analysis.
"""
)

clients = db.list_clients()
col1, col2 = st.columns(2)
col1.metric("Clients", len(clients))
plans = 0
for c in clients:
    if db.list_documents(c["id"]):
        plans += 1
col2.metric("Clients with an ingested plan", plans)

if clients:
    st.subheader("Clients")
    st.table([{"id": c["id"], "name": c["name"], "industry": c["industry"] or "—"}
              for c in clients])
else:
    st.info("Start by adding a client on the **Clients** page (left sidebar).")
