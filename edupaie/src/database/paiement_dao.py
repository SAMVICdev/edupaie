from src.database.connection import get_connection

class PaiementDAO:
    @staticmethod
    def ajouter(numero_recu, eleve_id, montant, date_paiement, mode_paiement):
        """Enregistre un nouveau paiement et retourne son ID."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO paiements (numero_recu, eleve_id, montant, date_paiement, mode_paiement)
            VALUES (?, ?, ?, ?, ?)
            """,
            (numero_recu, eleve_id, montant, date_paiement, mode_paiement)
        )
        conn.commit()
        paiement_id = cursor.lastrowid
        conn.close()
        return paiement_id

    @staticmethod
    def ajouter_paiement(numero_recu, eleve_id, montant, date_paiement, mode_paiement):
        """Alias permettant d'utiliser la méthode attendue par le service."""
        return PaiementDAO.ajouter(numero_recu, eleve_id, montant, date_paiement, mode_paiement)

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
        """Alias compatible avec le service de paiement."""
        return PaiementDAO.obtenir_dernier_numero_recu()

    @staticmethod
    def obtenir_total_paye_par_eleve(eleve_id):
        """Calcule le montant payé par un élève."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(montant), 0) FROM paiements WHERE eleve_id = ?", (eleve_id,))
        row = cursor.fetchone()
        conn.close()
        return float(row[0]) if row and row[0] is not None else 0.0

    @staticmethod
    def obtenir_total_encaisse():
        """Calcule la somme totale de tous les règlements enregistrés."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(montant) FROM paiements")
        row = cursor.fetchone()
        conn.close()
        return float(row[0]) if row and row[0] is not None else 0.0