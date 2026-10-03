from src.database.connection import get_connection

DEFAULT_SUPPORT_EMAIL = "samuelazovic@gmail.com,samvicdev@gmail.com"
DEFAULT_SUPPORT_TELEPHONE = "+228 97 90 67 11"


class ParametresDAO:

    @staticmethod
    def _assurer_colonnes_securite(conn):
        colonnes = {row['name'] for row in conn.execute("PRAGMA table_info(parametres)")}
        if 'password_salt' not in colonnes:
            conn.execute("ALTER TABLE parametres ADD COLUMN password_salt TEXT")
        if 'password_hash' not in colonnes:
            conn.execute("ALTER TABLE parametres ADD COLUMN password_hash TEXT")
        if 'format_matricule' not in colonnes:
            conn.execute(
                "ALTER TABLE parametres ADD COLUMN format_matricule TEXT NOT NULL DEFAULT '{annee}-{classe}-{numero:03d}'"
            )
        if 'annee_scolaire' not in colonnes:
            conn.execute(
                "ALTER TABLE parametres ADD COLUMN annee_scolaire TEXT DEFAULT '2025-2026'"
            )
        for colonne in ('recovery_salt', 'recovery_hash', 'support_email', 'support_telephone'):
            if colonne not in colonnes:
                conn.execute(f"ALTER TABLE parametres ADD COLUMN {colonne} TEXT")
        conn.commit()

    @staticmethod
    def obtenir_parametres():
        conn = get_connection()
        ParametresDAO._assurer_colonnes_securite(conn)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature,
                   annee_scolaire, format_matricule,
                   support_email, support_telephone,
                   (password_salt IS NOT NULL AND password_hash IS NOT NULL) AS protection_active,
                   (recovery_salt IS NOT NULL AND recovery_hash IS NOT NULL) AS recuperation_active
            FROM parametres WHERE id = 1
        """)
        row = cursor.fetchone()
        conn.close()
        if row:
            parametres = dict(row)
            if not parametres.get("support_email"):
                parametres["support_email"] = DEFAULT_SUPPORT_EMAIL
            if not parametres.get("support_telephone"):
                parametres["support_telephone"] = DEFAULT_SUPPORT_TELEPHONE
            return parametres

        return {
            "nom_ecole": "ÉTABLISSEMENT EDUPAIE",
            "adresse": "Lomé, Togo",
            "telephone": "+228 00 00 00 00",
            "email": "contact@edupaie.com",
            "chemin_logo": "",
            "chemin_signature": "",
            "annee_scolaire": "2025-2026",
            "format_matricule": "{annee}-{classe}-{numero:03d}",
            "support_email": DEFAULT_SUPPORT_EMAIL,
            "support_telephone": DEFAULT_SUPPORT_TELEPHONE,
            "protection_active": False,
            "recuperation_active": False,
        }

    @staticmethod
    def sauvegarder_parametres(nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature,
                               annee_scolaire="2025-2026",
                               format_matricule="{annee}-{classe}-{numero:03d}",
                               support_email="", support_telephone=""):
        conn = get_connection()
        ParametresDAO._assurer_colonnes_securite(conn)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO parametres (
                id, nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature,
                annee_scolaire, format_matricule, support_email, support_telephone
            )
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                nom_ecole=excluded.nom_ecole,
                adresse=excluded.adresse,
                telephone=excluded.telephone,
                email=excluded.email,
                chemin_logo=excluded.chemin_logo,
                chemin_signature=excluded.chemin_signature,
                annee_scolaire=excluded.annee_scolaire,
                format_matricule=excluded.format_matricule,
                support_email=excluded.support_email,
                support_telephone=excluded.support_telephone
        """, (nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature,
              annee_scolaire, format_matricule,
              support_email or DEFAULT_SUPPORT_EMAIL,
              support_telephone or DEFAULT_SUPPORT_TELEPHONE))
        conn.commit()
        conn.close()

    @staticmethod
    def obtenir_identifiants_securite():
        conn = get_connection()
        ParametresDAO._assurer_colonnes_securite(conn)
        row = conn.execute(
            "SELECT password_salt, password_hash FROM parametres WHERE id = 1"
        ).fetchone()
        conn.close()
        if not row or not row['password_salt'] or not row['password_hash']:
            return None
        return row['password_salt'], row['password_hash']

    @staticmethod
    def protection_active():
        return ParametresDAO.obtenir_identifiants_securite() is not None

    @staticmethod
    def sauvegarder_mot_de_passe(salt, password_hash):
        conn = get_connection()
        ParametresDAO._assurer_colonnes_securite(conn)
        conn.execute(
            "UPDATE parametres SET password_salt = ?, password_hash = ? WHERE id = 1",
            (salt, password_hash),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def sauvegarder_securite(password_salt, password_hash, recovery_salt, recovery_hash):
        conn = get_connection()
        ParametresDAO._assurer_colonnes_securite(conn)
        conn.execute(
            """UPDATE parametres
               SET password_salt = ?, password_hash = ?, recovery_salt = ?, recovery_hash = ?
               WHERE id = 1""",
            (password_salt, password_hash, recovery_salt, recovery_hash),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def supprimer_mot_de_passe():
        conn = get_connection()
        ParametresDAO._assurer_colonnes_securite(conn)
        conn.execute(
            """UPDATE parametres
               SET password_salt = NULL, password_hash = NULL,
                   recovery_salt = NULL, recovery_hash = NULL
               WHERE id = 1"""
        )
        conn.commit()
        conn.close()

    @staticmethod
    def obtenir_identifiants_recuperation():
        conn = get_connection()
        ParametresDAO._assurer_colonnes_securite(conn)
        row = conn.execute(
            "SELECT recovery_salt, recovery_hash FROM parametres WHERE id = 1"
        ).fetchone()
        conn.close()
        if not row or not row['recovery_salt'] or not row['recovery_hash']:
            return None
        return row['recovery_salt'], row['recovery_hash']

    @staticmethod
    def sauvegarder_code_recuperation(salt, recovery_hash):
        conn = get_connection()
        ParametresDAO._assurer_colonnes_securite(conn)
        conn.execute(
            "UPDATE parametres SET recovery_salt = ?, recovery_hash = ? WHERE id = 1",
            (salt, recovery_hash),
        )
        conn.commit()
        conn.close()
