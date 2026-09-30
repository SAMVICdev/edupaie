from src.database.connection import get_connection

class EleveDAO:
    @staticmethod
    def ajouter(nom, prenom, classe, annee_scolaire, montant_total_due):
        """Ajoute un nouvel élève dans la BDD et retourne son ID."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO eleves (nom, prenom, classe, annee_scolaire, montant_total_due)
            VALUES (?, ?, ?, ?, ?)
            """,
            (nom, prenom, classe, annee_scolaire, montant_total_due)
        )
        conn.commit()
        eleve_id = cursor.lastrowid
        conn.close()
        return eleve_id

    @staticmethod
    def obtenir_tous():
        """Récupère tous les élèves ordonnés par nom et prénom."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM eleves ORDER BY nom, prenom")
        eleves = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return eleves

    @staticmethod
    def obtenir_par_id(eleve_id):
        """Récupère un élève par son ID unique."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM eleves WHERE id = ?", (eleve_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def modifier(eleve_id, nom, prenom, classe, annee_scolaire, montant_total_due):
        """Met à jour les données d'un élève existant."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE eleves 
            SET nom = ?, prenom = ?, classe = ?, annee_scolaire = ?, montant_total_due = ?
            WHERE id = ?
            """,
            (nom, prenom, classe, annee_scolaire, montant_total_due, eleve_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def supprimer(eleve_id):
        """Supprime un élève de la BDD."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM eleves WHERE id = ?", (eleve_id,))
        conn.commit()
        conn.close()