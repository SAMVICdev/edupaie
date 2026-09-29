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