from src.database.connection import get_connection

class ParametresDAO:

    @staticmethod
    def obtenir_parametres():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature FROM parametres WHERE id = 1")
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
            "chemin_signature": ""
        }

    @staticmethod
    def sauvegarder_parametres(nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO parametres (id, nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature)
            VALUES (1, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                nom_ecole=excluded.nom_ecole,
                adresse=excluded.adresse,
                telephone=excluded.telephone,
                email=excluded.email,
                chemin_logo=excluded.chemin_logo,
                chemin_signature=excluded.chemin_signature
        """, (nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature))
        conn.commit()
        conn.close()