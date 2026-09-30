from src.database.eleve_dao import EleveDAO
from src.database.paiement_dao import PaiementDAO

class EleveService:
    
    @staticmethod
    def inscrire_eleve(nom, prenom, classe, annee_scolaire, montant_du):
        """Valide les données et enregistre un nouvel élève."""
        # 1. Validations métier
        if not nom or not nom.strip():
            raise ValueError("Le nom de l'élève est obligatoire.")
        if not prenom or not prenom.strip():
            raise ValueError("Le prénom de l'élève est obligatoire.")
        if montant_du <= 0:
            raise ValueError("Le montant dû doit être supérieur à 0.")
            
        # 2. Appel au DAO
        return EleveDAO.ajouter_eleve(nom.strip(), prenom.strip(), classe, annee_scolaire, montant_du)

    @staticmethod
    def obtenir_details_eleve(eleve_id):
        """Récupère l'élève et calcule son reste à payer."""
        eleve = EleveDAO.obtenir_par_id(eleve_id)
        if not eleve:
            return None
            
        paiements = PaiementDAO.obtenir_par_eleve(eleve_id)
        total_paye = sum(p['montant'] for p in paiements)
        reste_a_payer = eleve['montant_du'] - total_paye
        
        return {
            "eleve": eleve,
            "total_paye": total_paye,
            "reste_a_payer": max(0, reste_a_payer),
            "est_solde": reste_a_payer <= 0
        }