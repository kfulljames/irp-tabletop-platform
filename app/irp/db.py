"""SQLite storage for the local prototype.

Collapsed data model (per decision B0): single local facilitator, no multi-tenant RLS,
no auth. This mirrors a subset of the target Supabase model in 03-PRODUCT-REQUIREMENTS.md
so the concepts port later.
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

CREATE TABLE IF NOT EXISTS plan (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    client_org_id   INTEGER NOT NULL REFERENCES client_org(id) ON DELETE CASCADE,
    kind            TEXT NOT NULL DEFAULT 'IRP',   -- IRP | BCP
    source_filename TEXT,
    full_text       TEXT,
    uploaded_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

-- The client's plan mapped onto canonical baseline chapters (B3).
CREATE TABLE IF NOT EXISTS plan_section (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id       INTEGER NOT NULL REFERENCES plan(id) ON DELETE CASCADE,
    baseline_key  TEXT NOT NULL,
    title         TEXT NOT NULL,
    original_text TEXT      -- excerpt found in the client's plan (may be empty if missing)
);

-- AI pre-gap findings (Q8) + room-validated changes (B5 punch-list).
CREATE TABLE IF NOT EXISTS gap_finding (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    client_org_id      INTEGER NOT NULL REFERENCES client_org(id) ON DELETE CASCADE,
    plan_id            INTEGER REFERENCES plan(id) ON DELETE CASCADE,
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


def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    with get_conn() as conn:
        conn.executescript(SCHEMA)


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
        return conn.execute(
            "SELECT * FROM client_org ORDER BY created_at DESC"
        ).fetchall()


def get_client(client_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM client_org WHERE id = ?", (client_id,)
        ).fetchone()


def update_client(client_id, name, industry=None):
    with get_conn() as conn:
        conn.execute(
            "UPDATE client_org SET name = ?, industry = ? WHERE id = ?",
            (name, industry, client_id),
        )


def delete_client(client_id):
    # FK cascade (PRAGMA foreign_keys=ON) removes the client's plans/sections/gaps too.
    with get_conn() as conn:
        conn.execute("DELETE FROM client_org WHERE id = ?", (client_id,))


# ---- plans ---------------------------------------------------------------
def create_plan(client_org_id, kind, source_filename, full_text):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO plan (client_org_id, kind, source_filename, full_text) "
            "VALUES (?, ?, ?, ?)",
            (client_org_id, kind, source_filename, full_text),
        )
        return cur.lastrowid


def latest_plan_for_client(client_org_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM plan WHERE client_org_id = ? ORDER BY uploaded_at DESC LIMIT 1",
            (client_org_id,),
        ).fetchone()


def save_sections(plan_id, sections):
    """sections: list of dicts with baseline_key, title, original_text."""
    with get_conn() as conn:
        conn.execute("DELETE FROM plan_section WHERE plan_id = ?", (plan_id,))
        conn.executemany(
            "INSERT INTO plan_section (plan_id, baseline_key, title, original_text) "
            "VALUES (?, ?, ?, ?)",
            [(plan_id, s["baseline_key"], s["title"], s.get("original_text", "")) for s in sections],
        )


def sections_for_plan(plan_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM plan_section WHERE plan_id = ?", (plan_id,)
        ).fetchall()


# ---- gaps ----------------------------------------------------------------
def replace_ai_gaps(client_org_id, plan_id, gaps):
    """Replace AI-suggested gaps for a plan. gaps: list of dicts."""
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM gap_finding WHERE plan_id = ? AND source = 'ai'", (plan_id,)
        )
        conn.executemany(
            "INSERT INTO gap_finding "
            "(client_org_id, plan_id, baseline_key, title, description, "
            " recommended_change, severity, status, source) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, 'ai_suggested', 'ai')",
            [
                (
                    client_org_id, plan_id, g.get("baseline_key"), g["title"],
                    g.get("description", ""), g.get("recommended_change", ""),
                    g.get("severity", "medium"),
                )
                for g in gaps
            ],
        )


def gaps_for_plan(plan_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM gap_finding WHERE plan_id = ? "
            "ORDER BY CASE severity WHEN 'high' THEN 0 WHEN 'medium' THEN 1 "
            "WHEN 'low' THEN 2 ELSE 3 END",
            (plan_id,),
        ).fetchall()


def set_gap_status(gap_id, status):
    with get_conn() as conn:
        conn.execute("UPDATE gap_finding SET status = ? WHERE id = ?", (status, gap_id))
