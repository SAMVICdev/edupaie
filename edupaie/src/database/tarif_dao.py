from src.database.connection import get_connection


class TarifDAO:

    @staticmethod
    def obtenir_tous() -> list[dict]:
        """Retourne tous les tarifs triés par classe."""
        conn = get_connection()
        rows = conn.execute(
            "SELECT id, classe, montant FROM tarifs_classe ORDER BY classe"
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def obtenir_par_classe(classe: str) -> float | None:
        """Retourne le montant associé à une classe, ou None si non défini."""
        conn = get_connection()
        row = conn.execute(
            "SELECT montant FROM tarifs_classe WHERE LOWER(classe) = LOWER(?)",
            (classe.strip(),),
        ).fetchone()
        conn.close()
        return float(row["montant"]) if row else None

    @staticmethod
    def enregistrer(classe: str, montant: float) -> None:
        """Insère ou met à jour le tarif d'une classe (UPSERT)."""
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO tarifs_classe (classe, montant)
            VALUES (?, ?)
            ON CONFLICT(classe) DO UPDATE SET montant = excluded.montant
            """,
            (classe.strip(), montant),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def supprimer(classe: str) -> None:
        """Supprime le tarif d'une classe."""
        conn = get_connection()
        conn.execute(
            "DELETE FROM tarifs_classe WHERE LOWER(classe) = LOWER(?)",
            (classe.strip(),),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def supprimer_par_id(tarif_id: int) -> None:
        """Supprime un tarif par son ID."""
        conn = get_connection()
        conn.execute("DELETE FROM tarifs_classe WHERE id = ?", (tarif_id,))
        conn.commit()
        conn.close()
