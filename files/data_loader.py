"""
data_loader.py — Load private CSVs into local SQLite.
Run standalone first time:  python data_loader.py
"""

import sqlite3
import pandas as pd
import os
import logging
from config import DB_PATH, SHOWS_CSV, CHANNELS_CSV

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Schema definitions
# ─────────────────────────────────────────────────────────────────────────────

DDL_CHANNELS = """
CREATE TABLE IF NOT EXISTS channels (
    channel_id       TEXT PRIMARY KEY,
    channel_name     TEXT NOT NULL,
    language         TEXT,
    region           TEXT,
    category         TEXT,
    frequency_mhz    REAL,
    uplink_band      TEXT,
    downlink_band    TEXT,
    transponder      TEXT,
    empaneled        TEXT DEFAULT 'No',
    empanel_date     TEXT,
    compliance_score REAL,
    active           TEXT DEFAULT 'Yes'
);
"""

DDL_SHOWS = """
CREATE TABLE IF NOT EXISTS shows (
    show_id          TEXT PRIMARY KEY,
    title            TEXT NOT NULL,
    channel_id       TEXT,
    genre            TEXT,
    language         TEXT,
    runtime_mins     INTEGER,
    platform         TEXT,
    weekly_slots     INTEGER,
    avg_rating       REAL,
    total_episodes   INTEGER,
    first_aired      TEXT,
    last_aired       TEXT,
    status           TEXT DEFAULT 'Active',
    compliance_flag  TEXT DEFAULT 'Clear',
    prime_time       TEXT DEFAULT 'No',
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
);
"""

DDL_AUDIT = """
CREATE TABLE IF NOT EXISTS audit_log (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT DEFAULT (datetime('now','localtime')),
    username  TEXT,
    action    TEXT
);
"""


# ─────────────────────────────────────────────────────────────────────────────
# Core helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.executescript(DDL_CHANNELS + DDL_SHOWS + DDL_AUDIT)
        conn.commit()
        log.info("DB schema initialised at %s", DB_PATH)
    finally:
        conn.close()


def _upsert_df(df: pd.DataFrame, table: str, conn: sqlite3.Connection) -> int:
    """Replace-insert DataFrame rows; returns row count."""
    df.to_sql(table, conn, if_exists="replace", index=False, method="multi")
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return count


def load_channels() -> int:
    """Load private_channels.csv → SQLite channels table."""
    if not os.path.exists(CHANNELS_CSV):
        raise FileNotFoundError(f"Missing: {CHANNELS_CSV}")
    df = pd.read_csv(CHANNELS_CSV, dtype=str)
    df["compliance_score"] = pd.to_numeric(df["compliance_score"], errors="coerce")
    df["frequency_mhz"]    = pd.to_numeric(df["frequency_mhz"],    errors="coerce")
    conn = get_connection()
    try:
        n = _upsert_df(df, "channels", conn)
        conn.commit()
        log.info("Loaded %d channels", n)
        return n
    finally:
        conn.close()


def load_shows() -> int:
    """Load private_shows.csv → SQLite shows table."""
    if not os.path.exists(SHOWS_CSV):
        raise FileNotFoundError(f"Missing: {SHOWS_CSV}")
    df = pd.read_csv(SHOWS_CSV, dtype=str)
    for col in ("runtime_mins", "weekly_slots", "total_episodes"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["avg_rating"] = pd.to_numeric(df["avg_rating"], errors="coerce")
    conn = get_connection()
    try:
        n = _upsert_df(df, "shows", conn)
        conn.commit()
        log.info("Loaded %d shows", n)
        return n
    finally:
        conn.close()


def bootstrap() -> None:
    """Full init: schema + data load. Safe to call repeatedly."""
    init_db()
    load_channels()
    load_shows()
    log.info("Bootstrap complete.")


# ─────────────────────────────────────────────────────────────────────────────
# Query helpers (used by app.py and visuals.py)
# ─────────────────────────────────────────────────────────────────────────────

def query_df(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Execute a SELECT and return a DataFrame."""
    conn = get_connection()
    try:
        return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()


def get_channels(region: str = None, language: str = None,
                 category: str = None, search: str = None) -> pd.DataFrame:
    clauses, params = ["1=1"], []
    if region:
        clauses.append("c.region = ?"); params.append(region)
    if language:
        clauses.append("c.language = ?"); params.append(language)
    if category:
        clauses.append("c.category = ?"); params.append(category)
    if search:
        clauses.append("c.channel_name LIKE ?"); params.append(f"%{search}%")
    sql = f"""
        SELECT c.channel_id, c.channel_name, c.language, c.region,
               c.category, c.empaneled, c.empanel_date,
               c.compliance_score, c.active,
               COUNT(s.show_id) AS show_count
        FROM   channels c
        LEFT JOIN shows s ON c.channel_id = s.channel_id
        WHERE  {' AND '.join(clauses)}
        GROUP BY c.channel_id
        ORDER BY c.channel_name
    """
    return query_df(sql, tuple(params))


def get_shows(genre: str = None, platform: str = None, language: str = None,
              status: str = None, channel_id: str = None,
              search: str = None) -> pd.DataFrame:
    clauses, params = ["1=1"], []
    if genre:
        clauses.append("s.genre = ?"); params.append(genre)
    if platform:
        clauses.append("s.platform LIKE ?"); params.append(f"%{platform}%")
    if language:
        clauses.append("s.language = ?"); params.append(language)
    if status:
        clauses.append("s.status = ?"); params.append(status)
    if channel_id:
        clauses.append("s.channel_id = ?"); params.append(channel_id)
    if search:
        clauses.append("s.title LIKE ?"); params.append(f"%{search}%")
    sql = f"""
        SELECT s.show_id, s.title, c.channel_name, s.genre, s.language,
               s.runtime_mins, s.platform, s.weekly_slots, s.avg_rating,
               s.total_episodes, s.first_aired, s.last_aired,
               s.status, s.compliance_flag, s.prime_time
        FROM   shows s
        JOIN   channels c ON s.channel_id = c.channel_id
        WHERE  {' AND '.join(clauses)}
        ORDER BY s.avg_rating DESC
    """
    return query_df(sql, tuple(params))


def get_metrics() -> dict:
    """Return KPI metrics dict."""
    conn = get_connection()
    try:
        m = {}
        m["total_channels"]   = conn.execute("SELECT COUNT(*) FROM channels").fetchone()[0]
        m["empaneled"]        = conn.execute("SELECT COUNT(*) FROM channels WHERE empaneled='Yes'").fetchone()[0]
        m["total_shows"]      = conn.execute("SELECT COUNT(*) FROM shows").fetchone()[0]
        m["active_shows"]     = conn.execute("SELECT COUNT(*) FROM shows WHERE status='Active'").fetchone()[0]
        row = conn.execute("SELECT ROUND(AVG(runtime_mins),1), ROUND(AVG(avg_rating),2) FROM shows").fetchone()
        m["avg_runtime"]      = row[0] or 0
        m["avg_rating"]       = row[1] or 0
        m["compliance_flags"] = conn.execute("SELECT COUNT(*) FROM shows WHERE compliance_flag!='Clear'").fetchone()[0]
        row2 = conn.execute("SELECT ROUND(AVG(compliance_score),1) FROM channels").fetchone()
        m["avg_compliance"]   = row2[0] or 0
        return m
    finally:
        conn.close()


def write_audit(username: str, action: str) -> None:
    conn = get_connection()
    try:
        conn.execute("INSERT INTO audit_log(username,action) VALUES(?,?)", (username, action))
        conn.commit()
    finally:
        conn.close()


def clear_platform_table(table_name: str) -> int:
    """DELETE all rows from a platform table. Returns rows deleted."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
        ).fetchone()
        if not row or row[0] == 0:
            return 0
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        conn.execute(f"DELETE FROM {table_name}")
        conn.commit()
        return count
    finally:
        conn.close()


def drop_platform_table(table_name: str) -> None:
    """Fully DROP a platform table so it is recreated cleanly on next init."""
    conn = get_connection()
    try:
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
    finally:
        conn.close()


def clear_audit_log() -> int:
    """Delete all audit log entries. Returns count deleted."""
    conn = get_connection()
    try:
        count = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
        conn.execute("DELETE FROM audit_log")
        conn.commit()
        return count
    finally:
        conn.close()


def get_all_table_stats() -> list:
    """Return list of (table_name, row_count) for every table in the DB."""
    conn = get_connection()
    try:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        results = []
        for (tbl,) in tables:
            try:
                cnt = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            except Exception:
                cnt = 0
            results.append((tbl, cnt))
        return results
    finally:
        conn.close()


if __name__ == "__main__":
    bootstrap()
    print("\n✅  Database ready:", DB_PATH)
