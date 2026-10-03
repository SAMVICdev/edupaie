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
        colonnes_eleves = {row[1] for row in conn.execute("PRAGMA table_info(eleves)")}
        if "matricule" not in colonnes_eleves:
            conn.execute("ALTER TABLE eleves ADD COLUMN matricule TEXT")
        eleves_sans_matricule = conn.execute(
            "SELECT id FROM eleves WHERE matricule IS NULL OR matricule = ''"
        ).fetchall()
        for eleve in eleves_sans_matricule:
            conn.execute(
                "UPDATE eleves SET matricule = ? WHERE id = ?",
                (f"EDU-{eleve[0]:06d}", eleve[0]),
            )
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_eleves_matricule ON eleves(matricule)")
        schema_paiements = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'paiements'"
        ).fetchone()
        if schema_paiements and "TMoney" not in schema_paiements[0]:
            conn.commit()
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute("BEGIN")
            conn.execute("""
                CREATE TABLE paiements_migration (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_recu TEXT UNIQUE NOT NULL,
                    eleve_id INTEGER NOT NULL,
                    montant REAL NOT NULL CHECK(montant > 0),
                    date_paiement DATE NOT NULL,
                    mode_paiement TEXT NOT NULL CHECK(mode_paiement IN (
                        'Espèces', 'Chèque', 'Virement', 'Mobile Money', 'TMoney', 'Moov Money'
                    )),
                    total_paye_apres REAL,
                    reste_apres REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (eleve_id) REFERENCES eleves(id) ON DELETE CASCADE
                )
            """)
            conn.execute("""
                INSERT INTO paiements_migration
                (id, numero_recu, eleve_id, montant, date_paiement, mode_paiement, created_at)
                SELECT id, numero_recu, eleve_id, montant, date_paiement, mode_paiement, created_at
                FROM paiements
            """)
            conn.execute("DROP TABLE paiements")
            conn.execute("ALTER TABLE paiements_migration RENAME TO paiements")
            conn.commit()
            conn.execute("PRAGMA foreign_keys = ON")
        colonnes_paiements = {row[1] for row in conn.execute("PRAGMA table_info(paiements)")}
        if "total_paye_apres" not in colonnes_paiements:
            conn.execute("ALTER TABLE paiements ADD COLUMN total_paye_apres REAL")
        if "reste_apres" not in colonnes_paiements:
            conn.execute("ALTER TABLE paiements ADD COLUMN reste_apres REAL")
        conn.commit()
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Base de données initialisée avec succès.")