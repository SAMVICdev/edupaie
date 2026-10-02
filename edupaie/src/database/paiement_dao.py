from src.database.connection import get_connection

class PaiementDAO:
    @staticmethod
    def ajouter(numero_recu, eleve_id, montant, date_paiement, mode_paiement,
                total_paye_apres=None, reste_apres=None):
        """Enregistre un nouveau paiement et retourne son ID."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO paiements (
                numero_recu, eleve_id, montant, date_paiement, mode_paiement,
                total_paye_apres, reste_apres
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (numero_recu, eleve_id, montant, date_paiement, mode_paiement,
             total_paye_apres, reste_apres)
        )
        conn.commit()
        paiement_id = cursor.lastrowid
        conn.close()
        return paiement_id

    @staticmethod
    def obtenir_par_eleve(eleve_id):
        """Récupère tous les paiements effectués par un élève donné."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM paiements 
            WHERE eleve_id = ? 
            ORDER BY date_paiement DESC, id DESC
            """, 
            (eleve_id,)
        )
        paiements = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return paiements

    @staticmethod
    def obtenir_dernier_numero_recu():
        """Récupère le dernier numéro de reçu enregistré pour incrémentation."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT numero_recu FROM paiements ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row["numero_recu"] if row else None

    @staticmethod
    def obtenir_dernier_recu():
        return PaiementDAO.obtenir_dernier_numero_recu()

    @staticmethod
    def ajouter_paiement(eleve_id, montant, date_paiement, mode_paiement, numero_recu,
                         total_paye_apres=None, reste_apres=None):
        return PaiementDAO.ajouter(
            numero_recu, eleve_id, montant, date_paiement, mode_paiement,
            total_paye_apres, reste_apres
        )

    @staticmethod
    def obtenir_total_paye_par_eleve(eleve_id):
        conn = get_connection()
        row = conn.execute(
            "SELECT COALESCE(SUM(montant), 0) FROM paiements WHERE eleve_id = ?",
            (eleve_id,),
        ).fetchone()
        conn.close()
        return float(row[0] or 0)

    @staticmethod
    def obtenir_total_encaisse():
        """Calcule la somme totale de tous les règlements enregistrés."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(montant) FROM paiements")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row[0] else 0.0

    @staticmethod
    def obtenir_encaissements_mensuels(mois_depart, mois_fin):
        conn = get_connection()
        rows = conn.execute(
            """
            SELECT substr(date_paiement, 1, 7) AS mois, COALESCE(SUM(montant), 0) AS total
            FROM paiements
            WHERE substr(date_paiement, 1, 7) BETWEEN ? AND ?
            GROUP BY substr(date_paiement, 1, 7)
            ORDER BY mois
            """,
            (mois_depart, mois_fin),
        ).fetchall()
        conn.close()
        return {row["mois"]: float(row["total"] or 0) for row in rows}

    @staticmethod
    def obtenir_repartition_scolarite():
        conn = get_connection()
        row = conn.execute(
            """
            SELECT
                COALESCE(SUM(eleves.montant_total_due), 0) AS total_du,
                COALESCE(SUM(MIN(eleves.montant_total_due, COALESCE(paiements.total_paye, 0))), 0) AS total_paye
            FROM eleves
            LEFT JOIN (
                SELECT eleve_id, SUM(montant) AS total_paye
                FROM paiements
                GROUP BY eleve_id
            ) AS paiements ON paiements.eleve_id = eleves.id
            """
        ).fetchone()
        conn.close()
        total_du = float(row["total_du"] or 0)
        total_paye = float(row["total_paye"] or 0)
        return {
            "total_du": total_du,
            "total_paye": total_paye,
            "reste": max(0.0, total_du - total_paye),
        }