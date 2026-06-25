"""Small shared Streamlit UI helpers."""
import os

import streamlit as st

from . import db


def hide_running_indicator():
    """Hide Streamlit's built-in top-right 'running' animation.

    It's a generic Streamlit graphic some viewers find off-putting; our own inline
    st.spinner still shows during long operations like the gap analysis.
    """
    st.markdown(
        "<style>[data-testid='stStatusWidget']{visibility:hidden;}</style>",
        unsafe_allow_html=True,
    )


def sidebar_api_key():
    """Render the API-key input in the sidebar; persist to env for the SDK."""
    hide_running_indicator()
    with st.sidebar:
        st.subheader("Settings")
        existing = st.session_state.get("api_key", os.environ.get("ANTHROPIC_API_KEY", ""))
        key = st.text_input(
            "Anthropic API key",
            value=existing,
            type="password",
            help="Used for AI gap analysis. Get one at console.anthropic.com. "
                 "Stays on your machine.",
        )
        if key:
            st.session_state["api_key"] = key
            os.environ["ANTHROPIC_API_KEY"] = key

        # Model picker — defaults to the cheapest. Re-run a plan on a pricier model to compare.
        models = {
            "Haiku 4.5 — cheapest ($1/$5 per M)": "claude-haiku-4-5",
            "Sonnet 4.6 — balanced ($3/$15)": "claude-sonnet-4-6",
            "Opus 4.8 — most capable ($5/$25)": "claude-opus-4-8",
        }
        labels = list(models.keys())
        current = st.session_state.get("model", "claude-haiku-4-5")
        idx = next((i for i, m in enumerate(models.values()) if m == current), 0)
        chosen = st.selectbox(
            "AI model for analysis", labels, index=idx,
            help="Cheaper models cost less per run; pricier ones may catch more. "
                 "You can re-run the same plan and compare.",
        )
        st.session_state["model"] = models[chosen]
        return key


def selected_model():
    return st.session_state.get("model", "claude-haiku-4-5")


def client_picker(label="Client"):
    """Render a client selectbox; return the selected client_org id or None."""
    clients = db.list_clients()
    if not clients:
        st.info("No clients yet. Add one on the **Clients** page.")
        return None
    options = {f"{c['name']} (#{c['id']})": c["id"] for c in clients}
    default_id = st.session_state.get("client_id")
    keys = list(options.keys())
    index = 0
    if default_id is not None:
        for i, (_, cid) in enumerate(options.items()):
            if cid == default_id:
                index = i
                break
    chosen = st.selectbox(label, keys, index=index)
    cid = options[chosen]
    st.session_state["client_id"] = cid
    return cid
