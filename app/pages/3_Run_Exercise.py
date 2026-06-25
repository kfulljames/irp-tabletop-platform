import streamlit as st

from irp import db
from irp.ui import sidebar_api_key

st.set_page_config(page_title="Run Exercise · IRP Tabletop", page_icon="🛡️", layout="wide")
db.init_db()
sidebar_api_key()

st.title("Run Exercise")
st.info(
    "🚧 Coming next. This is where the facilitator drives the scenario: a linear inject "
    "deck, **act-as attribution**, a live running clock, observers, and typed capture "
    "(business decisions, comms decisions, task assignments, plan-change notes).\n\n"
    "It builds on the same client + plan you set up on the **Plan & Gaps** page. The "
    "first seeded scenario will be **BEC**, with Ransomware and Data-breach to follow."
)
