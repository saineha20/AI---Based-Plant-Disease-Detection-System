# backend/database.py
"""
SQLite Database Layer for Kisan Mitra
Manages agricultural disease catalogues, verified treatments, and diagnosis history.
"""
import os
import json
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "kisan_mitra.db")
DISEASES_JSON = os.path.join(DATA_DIR, "diseases.json")
TREATMENTS_JSON = os.path.join(DATA_DIR, "treatments.json")

def get_db_connection():
    """Returns a SQLite connection with dict-like row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_database():
    """Initializes tables and seeds initial data if database is empty."""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Diseases Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diseases (
        id TEXT PRIMARY KEY,
        crop_en TEXT NOT NULL,
        crop_hi TEXT NOT NULL,
        crop_te TEXT NOT NULL,
        disease_name_en TEXT NOT NULL,
        disease_name_hi TEXT NOT NULL,
        disease_name_te TEXT NOT NULL,
        pathogen_type TEXT NOT NULL,
        scientific_name TEXT,
        is_healthy INTEGER DEFAULT 0,
        summary_en TEXT,
        summary_hi TEXT,
        summary_te TEXT,
        symptoms_json TEXT,
        favorable_conditions_json TEXT,
        immediate_actions_json TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Treatments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS treatments (
        disease_id TEXT PRIMARY KEY,
        cultural_controls_json TEXT,
        organic_controls_json TEXT,
        chemical_controls_json TEXT,
        fertilizer_guidance_json TEXT,
        safety_precautions_json TEXT,
        expert_consultation_json TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (disease_id) REFERENCES diseases (id) ON DELETE CASCADE
    )
    """)

    # 3. Diagnosis History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diagnosis_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disease_id TEXT NOT NULL,
        crop TEXT NOT NULL,
        disease_name TEXT NOT NULL,
        confidence REAL NOT NULL,
        confidence_rating TEXT,
        diagnosis_status TEXT,
        language TEXT DEFAULT 'en',
        thumbnail TEXT,
        quality_metrics_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (disease_id) REFERENCES diseases (id)
    )
    """)

    # 4. Farmer Feedback Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farmer_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        diagnosis_id INTEGER,
        is_accurate INTEGER DEFAULT 1,
        comments TEXT,
        contact_mandat TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (diagnosis_id) REFERENCES diagnosis_history (id) ON DELETE SET NULL
    )
    """)

    conn.commit()

    # Seed data if diseases table is empty
    cursor.execute("SELECT COUNT(*) FROM diseases")
    count = cursor.fetchone()[0]
    if count == 0:
        logger.info("Database empty. Seeding from JSON catalogues...")
        seed_database_from_json(conn)

    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")

def seed_database_from_json(conn=None):
    """Populates SQLite database from existing diseases.json and treatments.json."""
    close_after = False
    if conn is None:
        conn = get_db_connection()
        close_after = True

    cursor = conn.cursor()

    if os.path.exists(DISEASES_JSON) and os.path.exists(TREATMENTS_JSON):
        with open(DISEASES_JSON, "r", encoding="utf-8") as f:
            diseases_data = json.load(f)

        with open(TREATMENTS_JSON, "r", encoding="utf-8") as f:
            treatments_data = json.load(f)

        for d_id, d in diseases_data.items():
            crop = d.get("crop", {})
            name = d.get("disease_name", {})
            summary = d.get("summary", {})

            cursor.execute("""
            INSERT OR REPLACE INTO diseases (
                id, crop_en, crop_hi, crop_te,
                disease_name_en, disease_name_hi, disease_name_te,
                pathogen_type, scientific_name, is_healthy,
                summary_en, summary_hi, summary_te,
                symptoms_json, favorable_conditions_json, immediate_actions_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                d_id,
                crop.get("en", "Unknown"),
                crop.get("hi", crop.get("en", "Unknown")),
                crop.get("te", crop.get("en", "Unknown")),
                name.get("en", "Unknown"),
                name.get("hi", name.get("en", "Unknown")),
                name.get("te", name.get("en", "Unknown")),
                d.get("pathogen_type", "unknown"),
                d.get("scientific_name", "N/A"),
                1 if d.get("is_healthy", False) else 0,
                summary.get("en", ""),
                summary.get("hi", summary.get("en", "")),
                summary.get("te", summary.get("en", "")),
                json.dumps(d.get("symptoms", {}), ensure_ascii=False),
                json.dumps(d.get("favorable_conditions", {}), ensure_ascii=False),
                json.dumps(d.get("immediate_actions", {}), ensure_ascii=False)
            ))

        for t_id, t in treatments_data.items():
            cursor.execute("""
            INSERT OR REPLACE INTO treatments (
                disease_id,
                cultural_controls_json,
                organic_controls_json,
                chemical_controls_json,
                fertilizer_guidance_json,
                safety_precautions_json,
                expert_consultation_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                t_id,
                json.dumps(t.get("cultural_controls", {}), ensure_ascii=False),
                json.dumps(t.get("organic_controls", {}), ensure_ascii=False),
                json.dumps(t.get("chemical_controls", {}), ensure_ascii=False),
                json.dumps(t.get("fertilizer_guidance", {}), ensure_ascii=False),
                json.dumps(t.get("safety_precautions", {}), ensure_ascii=False),
                json.dumps(t.get("expert_consultation", {}), ensure_ascii=False)
            ))

        conn.commit()
        logger.info(f"Seeded {len(diseases_data)} diseases and treatments into SQLite database.")

    if close_after:
        conn.close()

# Database Query Helper Methods
def query_disease_by_id(disease_id: str, lang: str = "en") -> dict:
    """Retrieves single disease from SQLite database localized to requested language."""
    lang = lang if lang in ["en", "hi", "te"] else "en"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM diseases WHERE id = ?", (disease_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    symptoms_all = json.loads(row["symptoms_json"] or "{}")
    favorable_all = json.loads(row["favorable_conditions_json"] or "{}")
    actions_all = json.loads(row["immediate_actions_json"] or "{}")

    return {
        "id": row["id"],
        "crop": row[f"crop_{lang}"] or row["crop_en"],
        "disease_name": row[f"disease_name_{lang}"] or row["disease_name_en"],
        "pathogen_type": row["pathogen_type"],
        "scientific_name": row["scientific_name"],
        "is_healthy": bool(row["is_healthy"]),
        "summary": row[f"summary_{lang}"] or row["summary_en"],
        "symptoms": symptoms_all.get(lang, symptoms_all.get("en", [])),
        "favorable_conditions": favorable_all.get(lang, favorable_all.get("en", [])),
        "immediate_actions": actions_all.get(lang, actions_all.get("en", []))
    }

def query_treatment_by_id(disease_id: str, lang: str = "en") -> dict:
    """Retrieves treatment protocols from SQLite database localized to requested language."""
    lang = lang if lang in ["en", "hi", "te"] else "en"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM treatments WHERE disease_id = ?", (disease_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    cult = json.loads(row["cultural_controls_json"] or "{}")
    org = json.loads(row["organic_controls_json"] or "{}")
    chem = json.loads(row["chemical_controls_json"] or "{}")
    fert = json.loads(row["fertilizer_guidance_json"] or "{}")
    safe = json.loads(row["safety_precautions_json"] or "{}")
    exp = json.loads(row["expert_consultation_json"] or "{}")

    explanation = fert.get("explanation", {})
    fert_text = explanation.get(lang, explanation.get("en", "")) if isinstance(explanation, dict) else str(explanation)

    return {
        "disease_id": disease_id,
        "cultural_controls": cult.get(lang, cult.get("en", [])),
        "organic_controls": org.get(lang, org.get("en", [])),
        "chemical_controls": chem.get(lang, chem.get("en", [])),
        "fertilizer_guidance": {
            "is_fertilizer_cure": fert.get("is_fertilizer_cure", False),
            "explanation": fert_text
        },
        "safety_precautions": safe.get(lang, safe.get("en", [])),
        "expert_consultation": exp.get(lang, exp.get("en", ""))
    }

def query_all_diseases(lang: str = "en") -> list:
    """Returns catalog of all supported crop conditions from SQLite database."""
    lang = lang if lang in ["en", "hi", "te"] else "en"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, crop_{lang} as crop, disease_name_{lang} as disease_name, pathogen_type, is_healthy FROM diseases ORDER BY crop, disease_name")
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r["id"],
            "crop": r["crop"],
            "disease_name": r["disease_name"],
            "pathogen_type": r["pathogen_type"],
            "is_healthy": bool(r["is_healthy"])
        }
        for r in rows
    ]

def save_diagnosis_to_db(record: dict) -> int:
    """Inserts a diagnosis session into diagnosis_history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO diagnosis_history (
        disease_id, crop, disease_name, confidence,
        confidence_rating, diagnosis_status, language, thumbnail, quality_metrics_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record.get("disease_id"),
        record.get("crop"),
        record.get("disease_name"),
        record.get("confidence"),
        record.get("confidence_rating"),
        record.get("diagnosis_status"),
        record.get("language", "en"),
        record.get("thumbnail", ""),
        json.dumps(record.get("quality_metrics", {}))
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def get_diagnosis_history_from_db(limit: int = 20) -> list:
    """Retrieves recent diagnosis history records."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, disease_id, crop, disease_name, confidence, confidence_rating,
           diagnosis_status, language, thumbnail, created_at
    FROM diagnosis_history
    ORDER BY created_at DESC
    LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r["id"],
            "disease_id": r["disease_id"],
            "crop": r["crop"],
            "disease": r["disease_name"],
            "confidence": round(r["confidence"], 1),
            "confidence_rating": r["confidence_rating"],
            "diagnosis_status": r["diagnosis_status"],
            "language": r["language"],
            "thumbnail": r["thumbnail"],
            "date": r["created_at"]
        }
        for r in rows
    ]

def clear_diagnosis_history_db():
    """Clears all records in diagnosis_history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM diagnosis_history")
    conn.commit()
    conn.close()

def save_farmer_feedback_db(diagnosis_id: int, is_accurate: bool, comments: str) -> int:
    """Saves user feedback for a diagnosis."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO farmer_feedback (diagnosis_id, is_accurate, comments)
    VALUES (?, ?, ?)
    """, (diagnosis_id, 1 if is_accurate else 0, comments))
    f_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return f_id

