from src.database.connection import get_connection


class EcheanceDAO:
    @staticmethod
    def obtenir_toutes():
        conn = get_connection()
        rows = conn.execute(
            "SELECT annee_scolaire, classe, date_echeance FROM echeances "
            "ORDER BY annee_scolaire DESC, classe"
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def obtenir_date_echeance(annee_scolaire, classe):
        conn = get_connection()
        row = conn.execute(
            "SELECT date_echeance FROM echeances "
            "WHERE annee_scolaire = ? AND classe = ?",
            (annee_scolaire, classe),
        ).fetchone()
        if not row:
            row = conn.execute(
                "SELECT date_echeance FROM echeances "
                "WHERE annee_scolaire = ? AND classe = '*'",
                (annee_scolaire,),
            ).fetchone()
        conn.close()
        return row["date_echeance"] if row else None

    @staticmethod
    def enregistrer(annee_scolaire, classe, date_echeance):
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO echeances (annee_scolaire, classe, date_echeance)
            VALUES (?, ?, ?)
            ON CONFLICT(annee_scolaire, classe)
            DO UPDATE SET date_echeance = excluded.date_echeance
            """,
            (annee_scolaire, classe, date_echeance),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def supprimer(annee_scolaire, classe):
        conn = get_connection()
        conn.execute(
            "DELETE FROM echeances WHERE annee_scolaire = ? AND classe = ?",
            (annee_scolaire, classe),
        )
        conn.commit()
        conn.close()
