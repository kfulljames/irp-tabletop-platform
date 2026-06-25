import streamlit as st

from irp import db
from irp.ui import sidebar_api_key

st.set_page_config(page_title="Evidence Report · IRP Tabletop", page_icon="🛡️", layout="wide")
db.init_db()
sidebar_api_key()

st.title("Evidence Report")
st.info(
    "🚧 Coming next. At the end of a run this generates the SOC 2-grade evidence report — "
    "timestamped timeline, team + observers, decisions, EOS confidence vote, AI closing "
    "notes — plus the **change punch-list** (and later a redlined plan). Exports to "
    "PDF / Word / structured, with a facilitator approval gate before anything leaves."
)
