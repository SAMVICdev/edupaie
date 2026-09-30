import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "edupaie.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "schema.sql")

def get_connection():
    """Établit et retourne une connexion SQLite avec support des clés étrangères."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialise la base de données en exécutant le fichier schema.sql."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parametres'")
    table_exists = cursor.fetchone() is not None
    if table_exists:
        cursor.execute("PRAGMA table_info(parametres)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'annee_scolaire' not in columns:
            cursor.execute("ALTER TABLE parametres ADD COLUMN annee_scolaire TEXT NOT NULL DEFAULT '2025-2026'")
            conn.commit()
    conn.close()

    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn = get_connection()
        conn.executescript(schema_sql)
        conn.commit()
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Base de données initialisée avec succès.")