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


def sidebar_client_picker(label="Client / tenant"):
    """Render the tenant selector in the sidebar; returns the selected client id or None."""
    clients = db.list_clients()
    with st.sidebar:
        st.subheader("Client")
        if not clients:
            st.info("No clients yet — add one on the **Clients** page.")
            return None
        labels, idmap = [], {}
        for c in clients:
            lab = c["name"]
            if lab in idmap:
                lab = f"{c['name']} (#{c['id']})"
            labels.append(lab)
            idmap[lab] = c["id"]
        default_id = st.session_state.get("client_id")
        index = next((i for i, lab in enumerate(labels) if idmap[lab] == default_id), 0)
        chosen = st.selectbox(label, labels, index=index, key="tenant_select")
        cid = idmap[chosen]
        st.session_state["client_id"] = cid
        return cid


def tenant_banner(client):
    """A sticky green bar pinned to the top showing the active tenant (avoids wrong-tenant uploads).

    Makes the Streamlit *element wrapper* that contains the bar sticky (via a :has() selector),
    rather than the inner div. The inner div's parent is too short for sticky to hold; the element
    wrapper is a direct child of the tall page-scroll block, so sticky pins across the whole page.
    Selector doesn't depend on Streamlit-generated class names.
    """
    name = client["name"] if client else "—"
    st.markdown(
        f"""
        <style>
        [data-testid="stElementContainer"]:has(#tenant-sticky),
        .element-container:has(#tenant-sticky) {{
            position: sticky; top: 0; z-index: 1000;
            background: #0e1117; padding: 0.4rem 0; margin-bottom: 0.5rem;
        }}
        #tenant-sticky {{
            background: #157347; color: #ffffff; font-weight: 600; font-size: 1.05rem;
            padding: 10px 16px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.35);
        }}
        </style>
        <div id="tenant-sticky">🏢 Working in: {name}</div>
        """,
        unsafe_allow_html=True,
    )


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
