from src.database.eleve_dao import EleveDAO
from src.database.paiement_dao import PaiementDAO

class EleveService:
    @staticmethod
    def inscrire_eleve(nom, prenom, classe, annee_scolaire, montant_total_due):
        """Valide et enregistre un nouvel élève via le DAO."""
        if not nom or not prenom or not classe:
            raise ValueError("Le nom, le prénom et la classe sont obligatoires.")
        
        try:
            montant_total_due = float(montant_total_due)
            if montant_total_due < 0:
                raise ValueError()
        except ValueError:
            raise ValueError("Le montant dû doit être un nombre positif.")

        return EleveDAO.ajouter(
            nom.strip(),
            prenom.strip(),
            classe.strip(),
            annee_scolaire.strip(),
            montant_total_due
        )

    @staticmethod
    def obtenir_tous_les_eleves():
        """Récupère la liste globale des élèves."""
        return EleveDAO.obtenir_tous()

    @staticmethod
    def obtenir_eleve_par_id(eleve_id):
        """Récupère un élève avec les montants calculés liés aux paiements."""
        eleve = EleveDAO.obtenir_par_id(eleve_id)
        if not eleve:
            return None

        total_paye = PaiementDAO.obtenir_total_paye_par_eleve(eleve_id)
        montant_du = eleve.get('montant_total_due', 0.0)
        eleve['total_paye'] = total_paye
        eleve['reste_a_payer'] = max(0.0, montant_du - total_paye)
        return eleve

    @staticmethod
    def obtenir_details_eleve(eleve_id):
        """Calcule et retourne les détails de l'élève avec son reste à payer."""
        return EleveService.obtenir_eleve_par_id(eleve_id)

    @staticmethod
    def modifier_eleve(eleve_id, nom, prenom, classe, annee_scolaire, montant_total_due):
        """Met à jour les informations d'un élève."""
        return EleveDAO.modifier(
            eleve_id,
            nom.strip(),
            prenom.strip(),
            classe.strip(),
            annee_scolaire.strip(),
            float(montant_total_due)
        )

    @staticmethod
    def supprimer_eleve(eleve_id):
        """Supprime un élève de la base de données."""
        return EleveDAO.supprimer(eleve_id)