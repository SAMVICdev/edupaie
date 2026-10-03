from src.database.connection import get_connection

class EleveDAO:
    @staticmethod
    def ajouter(nom, prenom, classe, annee_scolaire, montant_total_due, matricule=None):
        """Ajoute un nouvel élève dans la BDD et retourne son ID."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
                INSERT INTO eleves (matricule, nom, prenom, classe, annee_scolaire, montant_total_due)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            (matricule, nom, prenom, classe, annee_scolaire, montant_total_due)
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
    def modifier(eleve_id, nom, prenom, classe, annee_scolaire, montant_total_due, matricule=None):
        """Met à jour les données d'un élève existant."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE eleves 
            SET matricule = ?, nom = ?, prenom = ?, classe = ?, annee_scolaire = ?, montant_total_due = ?
            WHERE id = ?
            """,
            (matricule, nom, prenom, classe, annee_scolaire, montant_total_due, eleve_id)
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

    @staticmethod
    def matricule_existe(matricule, sauf_eleve_id=None):
        conn = get_connection()
        if sauf_eleve_id is None:
            row = conn.execute("SELECT 1 FROM eleves WHERE LOWER(matricule) = LOWER(?) LIMIT 1", (matricule,)).fetchone()
        else:
            row = conn.execute(
                "SELECT 1 FROM eleves WHERE LOWER(matricule) = LOWER(?) AND id != ? LIMIT 1",
                (matricule, sauf_eleve_id),
            ).fetchone()
        conn.close()
        return row is not None