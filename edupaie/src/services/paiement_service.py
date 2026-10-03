from datetime import datetime
from src.database.paiement_dao import PaiementDAO
from src.services.eleve_service import EleveService

class PaiementService:

    @staticmethod
    def generer_numero_recu():
        """Génère un numéro de reçu automatique (ex: REC-2026-0001)."""
        dernier_recu = PaiementDAO.obtenir_dernier_recu()
        annee_courante = datetime.now().year

        if not dernier_recu:
            compteur = 1
        else:
            # Extrait le numéro à la fin du dernier reçu
            try:
                dernier_num = int(dernier_recu.split('-')[-1])
                compteur = dernier_num + 1
            except (ValueError, IndexError):
                compteur = 1

        return f"REC-{annee_courante}-{compteur:04d}"

    @staticmethod
    def enregistrer_paiement(eleve_id, montant, mode_paiement, date_paiement=None):
        """Valide et enregistre un versement."""
        modes_autorises = {"Espèces", "TMoney", "Moov Money", "Mobile Money", "Chèque", "Virement"}
        if mode_paiement not in modes_autorises:
            raise ValueError("Le mode de règlement sélectionné n'est pas valide.")
        if montant <= 0:
            raise ValueError("Le montant du paiement doit être supérieur à 0.")

        details = EleveService.obtenir_details_eleve(eleve_id)
        if not details:
            raise ValueError("L'élève spécifié n'existe pas.")

        if montant > details['reste_a_payer']:
            raise ValueError(f"Le montant ({montant}) dépasse le reste à payer ({details['reste_a_payer']}).")

        numero_recu = PaiementService.generer_numero_recu()
        date_paiement = date_paiement or datetime.now().strftime("%Y-%m-%d")
        nouveau_reste = details['reste_a_payer'] - montant
        total_paye_apres = details['total_paye'] + montant

        paiement_id = PaiementDAO.ajouter_paiement(
            eleve_id=eleve_id,
            montant=montant,
            date_paiement=date_paiement,
            mode_paiement=mode_paiement,
            numero_recu=numero_recu,
            total_paye_apres=total_paye_apres,
            reste_apres=nouveau_reste,
        )

        return {
            "paiement_id": paiement_id,
            "numero_recu": numero_recu,
            "montant": montant,
            "total_du": details['montant_total_due'],
            "total_paye_apres": total_paye_apres,
            "nouveau_reste": nouveau_reste,
            "date_paiement": date_paiement,
            "mode_paiement": mode_paiement,
        }