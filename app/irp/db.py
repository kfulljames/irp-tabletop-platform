"""SQLite storage for the local prototype.

Collapsed data model (per decision B0): single local facilitator, no multi-tenant RLS,
no auth. A client can have MANY plan documents (e.g. a policy + a procedure, or an IRP +
a BCP); the gap analysis reads them together. Mirrors a subset of the target Supabase
model in 03-PRODUCT-REQUIREMENTS.md so the concepts port later.
"""
import os
import sqlite3
from contextlib import contextmanager

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DATA_DIR, "irp.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS client_org (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    industry     TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

-- One uploaded plan document. A client can have several (policy, procedure, IRP, BCP).
CREATE TABLE IF NOT EXISTS document (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    client_org_id   INTEGER NOT NULL REFERENCES client_org(id) ON DELETE CASCADE,
    label           TEXT,                 -- e.g. 'Policy', 'Procedure', 'IRP', 'BCP'
    source_filename TEXT,
    full_text       TEXT,
    uploaded_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

-- The client's plan corpus mapped onto canonical baseline chapters (B3). Per-client:
-- replaced each time the analysis is run over all the client's documents.
CREATE TABLE IF NOT EXISTS plan_section (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    client_org_id INTEGER NOT NULL REFERENCES client_org(id) ON DELETE CASCADE,
    baseline_key  TEXT NOT NULL,
    title         TEXT NOT NULL,
    original_text TEXT
);

-- AI pre-gap findings (Q8) + room-validated changes (B5 punch-list). Per-client.
CREATE TABLE IF NOT EXISTS gap_finding (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    client_org_id      INTEGER NOT NULL REFERENCES client_org(id) ON DELETE CASCADE,
    baseline_key       TEXT,
    title              TEXT NOT NULL,
    description        TEXT,
    recommended_change TEXT,
    severity           TEXT NOT NULL DEFAULT 'medium',   -- none | low | medium | high
    status             TEXT NOT NULL DEFAULT 'ai_suggested', -- ai_suggested | validated | dismissed
    source             TEXT NOT NULL DEFAULT 'ai',        -- ai | room
    created_at         TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def _has_table(conn, name):
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone() is not None


def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    with get_conn() as conn:
        # One-time migration from the older single-document schema (table 'plan').
        # The analysis tables held only re-derivable output, so rebuild them; the
        # uploaded documents carry over into the new 'document' table.
        legacy = _has_table(conn, "plan")
        if legacy:
            conn.execute("DROP TABLE IF EXISTS plan_section")  # old shape keyed by plan_id
            conn.execute("DROP TABLE IF EXISTS gap_finding")
        conn.executescript(SCHEMA)
        if legacy:
            conn.execute(
                "INSERT INTO document (client_org_id, label, source_filename, full_text, uploaded_at) "
                "SELECT client_org_id, kind, source_filename, full_text, uploaded_at FROM plan"
            )
            conn.execute("DROP TABLE plan")


@contextmanager
def get_conn():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ---- clients -------------------------------------------------------------
def create_client(name, industry=None):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO client_org (name, industry) VALUES (?, ?)", (name, industry)
        )
        return cur.lastrowid


def list_clients():
    with get_conn() as conn:
        return conn.execute("SELECT * FROM client_org ORDER BY created_at DESC").fetchall()


def get_client(client_id):
    with get_conn() as conn:
        return conn.execute("SELECT * FROM client_org WHERE id = ?", (client_id,)).fetchone()


def update_client(client_id, name, industry=None):
    with get_conn() as conn:
        conn.execute(
            "UPDATE client_org SET name = ?, industry = ? WHERE id = ?",
            (name, industry, client_id),
        )


def delete_client(client_id):
    # FK cascade (PRAGMA foreign_keys=ON) removes the client's documents/sections/gaps too.
    with get_conn() as conn:
        conn.execute("DELETE FROM client_org WHERE id = ?", (client_id,))


# ---- documents -----------------------------------------------------------
def add_document(client_org_id, label, source_filename, full_text):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO document (client_org_id, label, source_filename, full_text) "
            "VALUES (?, ?, ?, ?)",
            (client_org_id, label, source_filename, full_text),
        )
        return cur.lastrowid


def list_documents(client_org_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM document WHERE client_org_id = ? ORDER BY uploaded_at",
            (client_org_id,),
        ).fetchall()


def delete_document(doc_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM document WHERE id = ?", (doc_id,))


def combined_text(client_org_id):
    """Concatenate all of a client's documents, labelled, for the gap analysis."""
    docs = list_documents(client_org_id)
    parts = []
    for d in docs:
        label = d["label"] or ""
        header = f"=== DOCUMENT: {d['source_filename']}" + (f" ({label})" if label else "") + " ==="
        parts.append(f"{header}\n{d['full_text'] or ''}")
    return "\n\n".join(parts)


# ---- analysis output (per client) ----------------------------------------
def save_sections(client_org_id, sections):
    """sections: list of dicts with baseline_key, title, original_text."""
    with get_conn() as conn:
        conn.execute("DELETE FROM plan_section WHERE client_org_id = ?", (client_org_id,))
        conn.executemany(
            "INSERT INTO plan_section (client_org_id, baseline_key, title, original_text) "
            "VALUES (?, ?, ?, ?)",
            [(client_org_id, s["baseline_key"], s["title"], s.get("original_text", "")) for s in sections],
        )


def sections_for_client(client_org_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM plan_section WHERE client_org_id = ?", (client_org_id,)
        ).fetchall()


def replace_ai_gaps(client_org_id, gaps):
    """Replace AI-suggested gaps for a client. gaps: list of dicts."""
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM gap_finding WHERE client_org_id = ? AND source = 'ai'", (client_org_id,)
        )
        conn.executemany(
            "INSERT INTO gap_finding "
            "(client_org_id, baseline_key, title, description, recommended_change, severity, status, source) "
            "VALUES (?, ?, ?, ?, ?, ?, 'ai_suggested', 'ai')",
            [
                (
                    client_org_id, g.get("baseline_key"), g["title"], g.get("description", ""),
                    g.get("recommended_change", ""), g.get("severity", "medium"),
                )
                for g in gaps
            ],
        )


def gaps_for_client(client_org_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM gap_finding WHERE client_org_id = ? "
            "ORDER BY CASE severity WHEN 'high' THEN 0 WHEN 'medium' THEN 1 "
            "WHEN 'low' THEN 2 ELSE 3 END",
            (client_org_id,),
        ).fetchall()


def set_gap_status(gap_id, status):
    with get_conn() as conn:
        conn.execute("UPDATE gap_finding SET status = ? WHERE id = ?", (status, gap_id))
