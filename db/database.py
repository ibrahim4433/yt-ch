#!/usr/bin/env python3
"""
db/database.py
SQLite + FTS5 Database Engine for Dawah Dialectics Q&A Knowledge Base.
Supports full dual-language (Arabic & English) indexing, premises, analogies, and search.
"""

import os
import json
import sqlite3
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent

# Persistent Google Drive support for Colab environment
COLAB_DRIVE_DATA = Path("/content/drive/MyDrive/yt-ch/data")
if os.path.exists("/content/drive/MyDrive"):
    DATA_DIR = COLAB_DRIVE_DATA
else:
    DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "dawah_knowledge.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                channel TEXT,
                title_ar TEXT,
                youtube_url TEXT,
                srt_file TEXT,
                file_size INTEGER,
                status TEXT
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS qa_units (
                id TEXT PRIMARY KEY,
                video_id TEXT,
                channel TEXT,
                video_title_ar TEXT,
                youtube_url TEXT,
                timestamp_url TEXT,
                timestamp_seconds INTEGER,
                timestamp_formatted TEXT,
                topic_category TEXT,
                topic_subcategory TEXT,
                interlocutor_type TEXT,
                question_en TEXT,
                question_ar TEXT,
                core_answer_summary_en TEXT,
                core_answer_summary_ar TEXT,
                logical_premises_json TEXT,
                logical_premises_ar_json TEXT,
                fallacy_or_misconception_exposed TEXT,
                fallacy_or_misconception_exposed_ar TEXT,
                analogy_or_metaphor TEXT,
                analogy_or_metaphor_ar TEXT,
                socratic_question TEXT,
                socratic_question_ar TEXT,
                verbatim_quote TEXT,
                verbatim_quote_ar TEXT,
                tags_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE SET NULL
            );
        """)

        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS qa_fts USING fts5(
                id UNINDEXED,
                question_en,
                question_ar,
                core_answer_summary_en,
                core_answer_summary_ar,
                logical_premises,
                logical_premises_ar,
                analogy_or_metaphor,
                analogy_or_metaphor_ar,
                socratic_question,
                socratic_question_ar,
                verbatim_quote,
                verbatim_quote_ar,
                tags,
                tokenize = 'unicode61 remove_diacritics 2'
            );
        """)

        # Drop old triggers to update with new fields
        conn.execute("DROP TRIGGER IF EXISTS qa_ai;")
        conn.execute("DROP TRIGGER IF EXISTS qa_ad;")
        conn.execute("DROP TRIGGER IF EXISTS qa_au;")

        conn.execute("""
            CREATE TRIGGER qa_ai AFTER INSERT ON qa_units BEGIN
                INSERT INTO qa_fts(
                    id, question_en, question_ar, core_answer_summary_en, core_answer_summary_ar,
                    logical_premises, logical_premises_ar, analogy_or_metaphor, analogy_or_metaphor_ar,
                    socratic_question, socratic_question_ar, verbatim_quote, verbatim_quote_ar, tags
                ) VALUES (
                    new.id, new.question_en, new.question_ar, new.core_answer_summary_en, new.core_answer_summary_ar,
                    new.logical_premises_json, new.logical_premises_ar_json, new.analogy_or_metaphor, new.analogy_or_metaphor_ar,
                    new.socratic_question, new.socratic_question_ar, new.verbatim_quote, new.verbatim_quote_ar, new.tags_json
                );
            END;
        """)

        conn.execute("""
            CREATE TRIGGER qa_ad AFTER DELETE ON qa_units BEGIN
                DELETE FROM qa_fts WHERE id = old.id;
            END;
        """)

        conn.execute("""
            CREATE TRIGGER qa_au AFTER UPDATE ON qa_units BEGIN
                DELETE FROM qa_fts WHERE id = old.id;
                INSERT INTO qa_fts(
                    id, question_en, question_ar, core_answer_summary_en, core_answer_summary_ar,
                    logical_premises, logical_premises_ar, analogy_or_metaphor, analogy_or_metaphor_ar,
                    socratic_question, socratic_question_ar, verbatim_quote, verbatim_quote_ar, tags
                ) VALUES (
                    new.id, new.question_en, new.question_ar, new.core_answer_summary_en, new.core_answer_summary_ar,
                    new.logical_premises_json, new.logical_premises_ar_json, new.analogy_or_metaphor, new.analogy_or_metaphor_ar,
                    new.socratic_question, new.socratic_question_ar, new.verbatim_quote, new.verbatim_quote_ar, new.tags_json
                );
            END;
        """)

        # Auto-seed videos from manifest if table is newly created and empty
        cur = conn.execute("SELECT COUNT(*) FROM videos")
        if cur.fetchone()[0] == 0:
            manifest_file = DATA_DIR / "video_manifest.json"
            if not manifest_file.exists():
                manifest_file = BASE_DIR / "data" / "video_manifest.json"
            if manifest_file.exists():
                try:
                    with open(manifest_file, "r", encoding="utf-8") as f:
                        manifest_data = json.load(f)
                    video_rows = [
                        (v.get("video_id", ""), v.get("channel", "SCDawah Arabic"), v.get("title_ar", ""),
                         v.get("youtube_url", ""), v.get("srt_file", ""), v.get("file_size", 0), "pending")
                        for v in manifest_data if v.get("video_id")
                    ]
                    conn.executemany(
                        "INSERT OR IGNORE INTO videos (video_id, channel, title_ar, youtube_url, srt_file, file_size, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        video_rows
                    )
                except Exception as e:
                    print(f"[-] Note on video manifest seeding: {e}")

    conn.close()

    # Auto-seed pilot QA units if qa_units table is empty
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT COUNT(*) FROM qa_units")
        if cur.fetchone()[0] == 0:
            pilot_file = DATA_DIR / "pilot_qa_dataset.json"
            if not pilot_file.exists():
                pilot_file = BASE_DIR / "data" / "pilot_qa_dataset.json"
            if pilot_file.exists():
                with open(pilot_file, "r", encoding="utf-8") as f:
                    pilots = json.load(f)
                for p in pilots:
                    insert_qa_unit(p)
    finally:
        conn.close()


def insert_qa_unit(unit: Dict[str, Any]):
    conn = get_db_connection()
    with conn:
        conn.execute("""
            INSERT OR REPLACE INTO qa_units (
                id, video_id, channel, video_title_ar, youtube_url, timestamp_url,
                timestamp_seconds, timestamp_formatted, topic_category, topic_subcategory,
                interlocutor_type, question_en, question_ar, core_answer_summary_en,
                core_answer_summary_ar, logical_premises_json, logical_premises_ar_json,
                fallacy_or_misconception_exposed, fallacy_or_misconception_exposed_ar,
                analogy_or_metaphor, analogy_or_metaphor_ar, socratic_question,
                socratic_question_ar, verbatim_quote, verbatim_quote_ar, tags_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            unit.get("id"),
            unit.get("video_id"),
            unit.get("channel", "SCDawah Arabic"),
            unit.get("video_title_ar", ""),
            unit.get("youtube_url", ""),
            unit.get("timestamp_url", ""),
            unit.get("timestamp_seconds", 0),
            unit.get("timestamp_formatted", "00:00"),
            unit.get("topic_category", "Theology & God's Existence"),
            unit.get("topic_subcategory", ""),
            unit.get("interlocutor_type", "Atheist / Skeptic"),
            unit.get("question_en", ""),
            unit.get("question_ar", ""),
            unit.get("core_answer_summary_en", ""),
            unit.get("core_answer_summary_ar", ""),
            json.dumps(unit.get("logical_premises", []), ensure_ascii=False),
            json.dumps(unit.get("logical_premises_ar", []), ensure_ascii=False),
            unit.get("fallacy_or_misconception_exposed", ""),
            unit.get("fallacy_or_misconception_exposed_ar", ""),
            unit.get("analogy_or_metaphor", ""),
            unit.get("analogy_or_metaphor_ar", ""),
            unit.get("socratic_question", ""),
            unit.get("socratic_question_ar", ""),
            unit.get("verbatim_quote", ""),
            unit.get("verbatim_quote_ar", ""),
            json.dumps(unit.get("tags", []), ensure_ascii=False)
        ))
    conn.close()


def sanitize_fts_query(query: str) -> str:
    cleaned = re.sub(r'[*":^()\[\]{}~-]', ' ', query)
    tokens = [t.strip() for t in cleaned.split() if len(t.strip()) > 1]
    if not tokens:
        return ""
    fts_parts = [f'"{token}"*' for token in tokens]
    return " OR ".join(fts_parts)


def search_qa(
    query: str = "",
    category: Optional[str] = None,
    interlocutor: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    results = []
    sql_parts = []
    params = []

    if query and query.strip():
        fts_query = sanitize_fts_query(query)
        if fts_query:
            sql_parts.append("""
                qa_units.id IN (
                    SELECT id FROM qa_fts WHERE qa_fts MATCH ? ORDER BY rank
                )
            """)
            params.append(fts_query)
        else:
            sql_parts.append("(question_en LIKE ? OR question_ar LIKE ? OR core_answer_summary_en LIKE ? OR core_answer_summary_ar LIKE ?)")
            like_q = f"%{query}%"
            params.extend([like_q, like_q, like_q, like_q])

    if category and category != "all":
        sql_parts.append("topic_category = ?")
        params.append(category)

    if interlocutor and interlocutor != "all":
        sql_parts.append("interlocutor_type = ?")
        params.append(interlocutor)

    where_clause = " AND ".join(sql_parts) if sql_parts else "1=1"

    sql = f"""
        SELECT * FROM qa_units
        WHERE {where_clause}
        ORDER BY timestamp_seconds ASC
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    cursor = conn.execute(sql, params)
    rows = cursor.fetchall()

    for row in rows:
        d = dict(row)
        try:
            d["logical_premises"] = json.loads(d.get("logical_premises_json") or "[]")
        except Exception:
            d["logical_premises"] = []
        try:
            d["logical_premises_ar"] = json.loads(d.get("logical_premises_ar_json") or "[]")
        except Exception:
            d["logical_premises_ar"] = []
        try:
            d["tags"] = json.loads(d.get("tags_json") or "[]")
        except Exception:
            d["tags"] = []
        results.append(d)

    conn.close()
    return results


def get_categories_breakdown() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.execute("""
        SELECT topic_category, COUNT(*) as count 
        FROM qa_units 
        GROUP BY topic_category 
        ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_interlocutor_breakdown() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.execute("""
        SELECT interlocutor_type, COUNT(*) as count 
        FROM qa_units 
        GROUP BY interlocutor_type 
        ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats() -> Dict[str, Any]:
    conn = get_db_connection()
    total_qa = conn.execute("SELECT COUNT(*) FROM qa_units").fetchone()[0]
    total_videos = conn.execute("SELECT COUNT(*) FROM videos").fetchone()[0]
    categories_count = conn.execute("SELECT COUNT(DISTINCT topic_category) FROM qa_units").fetchone()[0]
    conn.close()
    return {
        "total_qa": total_qa,
        "total_videos": total_videos,
        "categories_count": categories_count
    }
