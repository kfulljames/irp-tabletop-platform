"""SQLite storage for the local prototype.

Collapsed data model (per decision B0): single local facilitator, no multi-tenant RLS,
no auth. A client can have MANY plan documents (e.g. a policy + a procedure, or an IRP +
a BCP); the gap analysis reads them together. Mirrors a subset of the target Supabase
model in 03-PRODUCT-REQUIREMENTS.md so the concepts port later.
"""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None


def now_str(tzname=None):
    """Timestamp in the chosen timezone (IANA name) so every event reads in one consistent zone."""
    if tzname and ZoneInfo is not None:
        try:
            return datetime.now(ZoneInfo(tzname)).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

-- People roster for a client (setup wizard, Q10). Used for act-as attribution (Q6).
CREATE TABLE IF NOT EXISTS person (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    client_org_id INTEGER NOT NULL REFERENCES client_org(id) ON DELETE CASCADE,
    full_name     TEXT NOT NULL,
    title         TEXT,
    incident_role TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- A single live exercise/session (Q-D1: one run = one session).
CREATE TABLE IF NOT EXISTS run (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    client_org_id  INTEGER NOT NULL REFERENCES client_org(id) ON DELETE CASCADE,
    scenario_key   TEXT NOT NULL,
    scenario_title TEXT,
    status         TEXT NOT NULL DEFAULT 'running',  -- running | complete
    current_inject INTEGER NOT NULL DEFAULT 0,
    timezone       TEXT,                              -- IANA tz; all run timestamps use this
    started_at     TEXT,
    resolved_at    TEXT,
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS run_participant (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id    INTEGER NOT NULL REFERENCES run(id) ON DELETE CASCADE,
    person_id INTEGER NOT NULL REFERENCES person(id) ON DELETE CASCADE,
    role      TEXT NOT NULL DEFAULT 'participant'  -- participant | observer
);

-- Structured Overview for the run (Exigence-style; feeds report Sec 3).
CREATE TABLE IF NOT EXISTS run_overview (
    run_id            INTEGER PRIMARY KEY REFERENCES run(id) ON DELETE CASCADE,
    latest_status     TEXT,
    detection_summary TEXT,
    how_discovered    TEXT,
    when_discovered   TEXT,
    who_discovered    TEXT,
    impacted          TEXT,
    history           TEXT,
    updated_at        TEXT
);

-- Incident task checklist (seeded per scenario, grouped by phase; report Sec 5).
CREATE TABLE IF NOT EXISTS run_task (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id   INTEGER NOT NULL REFERENCES run(id) ON DELETE CASCADE,
    phase    TEXT,
    title    TEXT NOT NULL,
    assignee TEXT,
    status   TEXT NOT NULL DEFAULT 'pending',   -- pending | done
    sort     INTEGER NOT NULL DEFAULT 0
);

-- Typed capture (B9) — the timestamped evidence spine (Q4, report spec Sec 6).
CREATE TABLE IF NOT EXISTS timeline_event (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id           INTEGER NOT NULL REFERENCES run(id) ON DELETE CASCADE,
    occurred_at      TEXT NOT NULL,
    type             TEXT NOT NULL,
    acting_person_id INTEGER REFERENCES person(id) ON DELETE SET NULL,  -- act-as (Q6)
    description      TEXT,
    payload          TEXT,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def _has_table(conn, name):
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone() is not None


def _has_column(conn, table, column):
    if not _has_table(conn, table):
        return False
    cols = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    return column in cols


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
        # Add the run.timezone column to pre-existing databases.
        if _has_table(conn, "run") and not _has_column(conn, "run", "timezone"):
            conn.execute("ALTER TABLE run ADD COLUMN timezone TEXT")


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


def update_document_label(doc_id, label):
    with get_conn() as conn:
        conn.execute("UPDATE document SET label = ? WHERE id = ?", (label, doc_id))


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


def add_room_gap(client_org_id, title, description, severity="medium",
                 recommended_change="", baseline_key=None):
    """A plan-gap captured live in the exercise (source='room', already validated)."""
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO gap_finding "
            "(client_org_id, baseline_key, title, description, recommended_change, severity, status, source) "
            "VALUES (?, ?, ?, ?, ?, ?, 'validated', 'room')",
            (client_org_id, baseline_key, title, description, recommended_change, severity),
        )


# ---- people --------------------------------------------------------------
def add_person(client_org_id, full_name, title=None, incident_role=None):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO person (client_org_id, full_name, title, incident_role) VALUES (?, ?, ?, ?)",
            (client_org_id, full_name, title, incident_role),
        )
        return cur.lastrowid


def list_people(client_org_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM person WHERE client_org_id = ? ORDER BY full_name", (client_org_id,)
        ).fetchall()


def delete_person(person_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM person WHERE id = ?", (person_id,))


# ---- runs ----------------------------------------------------------------
def create_run(client_org_id, scenario_key, scenario_title, timezone=None):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO run (client_org_id, scenario_key, scenario_title, status, timezone, started_at) "
            "VALUES (?, ?, ?, 'running', ?, ?)",
            (client_org_id, scenario_key, scenario_title, timezone, now_str(timezone)),
        )
        return cur.lastrowid


def active_run_for_client(client_org_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM run WHERE client_org_id = ? AND status = 'running' "
            "ORDER BY created_at DESC LIMIT 1",
            (client_org_id,),
        ).fetchone()


def get_run(run_id):
    with get_conn() as conn:
        return conn.execute("SELECT * FROM run WHERE id = ?", (run_id,)).fetchone()


def list_runs(client_org_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM run WHERE client_org_id = ? ORDER BY created_at DESC", (client_org_id,)
        ).fetchall()


def set_current_inject(run_id, idx):
    with get_conn() as conn:
        conn.execute("UPDATE run SET current_inject = ? WHERE id = ?", (idx, run_id))


def resolve_run(run_id, timezone=None):
    with get_conn() as conn:
        conn.execute(
            "UPDATE run SET status = 'complete', resolved_at = ? WHERE id = ?",
            (now_str(timezone), run_id),
        )


# ---- participants --------------------------------------------------------
def add_participant(run_id, person_id, role="participant"):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO run_participant (run_id, person_id, role) VALUES (?, ?, ?)",
            (run_id, person_id, role),
        )


def list_participants(run_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT rp.id AS rp_id, rp.role, p.* FROM run_participant rp "
            "JOIN person p ON p.id = rp.person_id WHERE rp.run_id = ? ORDER BY p.full_name",
            (run_id,),
        ).fetchall()


# ---- timeline ------------------------------------------------------------
def add_event(run_id, etype, acting_person_id, description, payload=None, timezone=None):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO timeline_event (run_id, occurred_at, type, acting_person_id, description, payload) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (run_id, now_str(timezone), etype, acting_person_id, description, payload),
        )


def list_events(run_id, newest_first=True):
    order = "DESC" if newest_first else "ASC"
    with get_conn() as conn:
        return conn.execute(
            f"SELECT te.*, p.full_name AS acting_name FROM timeline_event te "
            f"LEFT JOIN person p ON p.id = te.acting_person_id "
            f"WHERE te.run_id = ? ORDER BY te.occurred_at {order}, te.id {order}",
            (run_id,),
        ).fetchall()


def delete_event(event_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM timeline_event WHERE id = ?", (event_id,))


# ---- overview ------------------------------------------------------------
OVERVIEW_FIELDS = ["latest_status", "detection_summary", "how_discovered",
                   "when_discovered", "who_discovered", "impacted", "history"]


def get_overview(run_id):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM run_overview WHERE run_id = ?", (run_id,)).fetchone()
    return dict(row) if row else {}


def save_overview(run_id, fields):
    cols = ", ".join(OVERVIEW_FIELDS)
    placeholders = ", ".join("?" for _ in OVERVIEW_FIELDS)
    updates = ", ".join(f"{f} = excluded.{f}" for f in OVERVIEW_FIELDS)
    values = [run_id] + [fields.get(f, "") for f in OVERVIEW_FIELDS] + [now_str()]
    with get_conn() as conn:
        conn.execute(
            f"INSERT INTO run_overview (run_id, {cols}, updated_at) "
            f"VALUES (?, {placeholders}, ?) "
            f"ON CONFLICT(run_id) DO UPDATE SET {updates}, updated_at = excluded.updated_at",
            values,
        )


# ---- tasks ---------------------------------------------------------------
def seed_tasks(run_id, tasks):
    """Seed the run's task checklist from (phase, title) pairs, once."""
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT COUNT(*) AS n FROM run_task WHERE run_id = ?", (run_id,)
        ).fetchone()["n"]
        if existing:
            return
        conn.executemany(
            "INSERT INTO run_task (run_id, phase, title, sort) VALUES (?, ?, ?, ?)",
            [(run_id, phase, title, i) for i, (phase, title) in enumerate(tasks)],
        )


def list_tasks(run_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM run_task WHERE run_id = ? ORDER BY sort, id", (run_id,)
        ).fetchall()


def set_task(task_id, status, assignee):
    with get_conn() as conn:
        conn.execute(
            "UPDATE run_task SET status = ?, assignee = ? WHERE id = ?",
            (status, assignee, task_id),
        )


def add_task(run_id, phase, title):
    with get_conn() as conn:
        nxt = conn.execute(
            "SELECT COALESCE(MAX(sort), 0) + 1 AS s FROM run_task WHERE run_id = ?", (run_id,)
        ).fetchone()["s"]
        conn.execute(
            "INSERT INTO run_task (run_id, phase, title, sort) VALUES (?, ?, ?, ?)",
            (run_id, phase, title, nxt),
        )
