from src.database.connection import get_connection

class ParametresDAO:

    @staticmethod
    def _assurer_colonne_annee_scolaire():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(parametres)")
        colonnes = [row[1] for row in cursor.fetchall()]
        conn.close()

        if 'annee_scolaire' not in colonnes:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("ALTER TABLE parametres ADD COLUMN annee_scolaire TEXT DEFAULT '2025-2026'")
            conn.commit()
            conn.close()

    @staticmethod
    def obtenir_parametres():
        ParametresDAO._assurer_colonne_annee_scolaire()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature, annee_scolaire FROM parametres WHERE id = 1"
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return {
            "nom_ecole": "ÉTABLISSEMENT EDUPAIE",
            "adresse": "Lomé, Togo",
            "telephone": "+228 00 00 00 00",
            "email": "contact@edupaie.com",
            "chemin_logo": "",
            "chemin_signature": "",
            "annee_scolaire": "2025-2026"
        }

    @staticmethod
    def sauvegarder_parametres(nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature, annee_scolaire='2025-2026'):
        ParametresDAO._assurer_colonne_annee_scolaire()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO parametres (id, nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature, annee_scolaire)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                nom_ecole=excluded.nom_ecole,
                adresse=excluded.adresse,
                telephone=excluded.telephone,
                email=excluded.email,
                chemin_logo=excluded.chemin_logo,
                chemin_signature=excluded.chemin_signature,
                annee_scolaire=excluded.annee_scolaire
        """, (nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature, annee_scolaire))
        conn.commit()
        conn.close()