from src.database.connection import get_connection

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
        conn.commit()

    @staticmethod
    def obtenir_parametres():
        conn = get_connection()
        ParametresDAO._assurer_colonnes_securite(conn)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature, format_matricule,
                   (password_salt IS NOT NULL AND password_hash IS NOT NULL) AS protection_active
            FROM parametres WHERE id = 1
        """)
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
            "format_matricule": "{annee}-{classe}-{numero:03d}",
            "protection_active": False
        }

    @staticmethod
    def sauvegarder_parametres(nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature,
                               format_matricule="{annee}-{classe}-{numero:03d}"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO parametres (id, nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature, format_matricule)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                nom_ecole=excluded.nom_ecole,
                adresse=excluded.adresse,
                telephone=excluded.telephone,
                email=excluded.email,
                chemin_logo=excluded.chemin_logo,
                chemin_signature=excluded.chemin_signature,
                format_matricule=excluded.format_matricule
            """, (nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature, format_matricule))
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
    def supprimer_mot_de_passe():
        conn = get_connection()
        ParametresDAO._assurer_colonnes_securite(conn)
        conn.execute(
            "UPDATE parametres SET password_salt = NULL, password_hash = NULL WHERE id = 1"
        )
        conn.commit()
        conn.close()