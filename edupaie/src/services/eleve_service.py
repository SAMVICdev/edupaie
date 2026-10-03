import re
import unicodedata
import math
from datetime import date

from src.database.eleve_dao import EleveDAO
from src.database.echeance_dao import EcheanceDAO
from src.database.paiement_dao import PaiementDAO
from src.database.parametres_dao import ParametresDAO

class EleveService:
    @staticmethod
    def generer_matricule(classe, annee_scolaire):
        classe_ascii = unicodedata.normalize("NFKD", classe.upper())
        classe_ascii = "".join(
            caractere for caractere in classe_ascii
            if not unicodedata.combining(caractere)
        )
        classe_normalisee = re.sub(r"[^A-Z0-9]+", "", classe_ascii) or "CLASSE"
        annee = (annee_scolaire.split("-")[0] if annee_scolaire else str(date.today().year))
        params = ParametresDAO.obtenir_parametres()
        format_matricule = params.get("format_matricule", "{annee}-{classe}-{numero:03d}")
        if not all(token in format_matricule for token in ("{annee}", "{classe}", "{numero")):
            raise ValueError("Le format du matricule doit contenir {annee}, {classe} et {numero}.")
        for numero in range(1, 1_000_000):
            try:
                matricule = format_matricule.format(
                    annee=annee, classe=classe_normalisee, numero=numero
                )
            except (KeyError, ValueError) as exc:
                raise ValueError("Le format du matricule contient un champ invalide.") from exc
            if not EleveDAO.matricule_existe(matricule):
                return matricule
        raise ValueError("Impossible de générer un matricule unique.")

    @staticmethod
    def inscrire_eleve(nom, prenom, classe, annee_scolaire, montant_total_due, matricule=None):
        """Valide et enregistre un nouvel élève via le DAO."""
        if not nom or not prenom or not classe:
            raise ValueError("Le nom, le prénom et la classe sont obligatoires.")
        
        try:
            montant_total_due = float(montant_total_due)
            if not math.isfinite(montant_total_due) or montant_total_due < 0:
                raise ValueError()
        except ValueError:
            raise ValueError("Le montant dû doit être un nombre positif.")

        matricule = (matricule or EleveService.generer_matricule(classe.strip(), annee_scolaire.strip())).strip()
        if EleveDAO.matricule_existe(matricule):
            raise ValueError(f"Le matricule {matricule} est déjà utilisé.")

        return EleveDAO.ajouter(
            nom.strip(),
            prenom.strip(),
            classe.strip(),
            annee_scolaire.strip(),
            montant_total_due,
            matricule
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
    def filtrer_eleves(recherche='', classe='', statut='Tous'):
        """Filtre les élèves par nom/prénom, classe et statut de paiement."""
        eleves = EleveDAO.obtenir_tous()
        terme = (recherche or '').strip().lower()
        classe = (classe or '').strip()
        statut = statut or 'Tous'

        resultat = []
        for eleve in eleves:
            nom = (eleve.get('nom') or '').lower()
            prenom = (eleve.get('prenom') or '').lower()
            classe_eleve = (eleve.get('classe') or '')

            if terme and terme not in f"{nom} {prenom}":
                continue
            if classe and classe_eleve != classe:
                continue

            details = EleveService.obtenir_eleve_par_id(eleve['id'])
            reste = details.get('reste_a_payer', eleve.get('montant_total_due', 0.0)) if details else eleve.get('montant_total_due', 0.0)

            statut_eleve = EleveService.calculer_statut(eleve, reste)
            if statut == 'Soldé' and statut_eleve != 'Soldé':
                continue
            if statut == 'En cours' and statut_eleve != 'En cours':
                continue
            if statut == 'En retard' and statut_eleve != 'En retard':
                continue
            if statut == 'Non soldé' and statut_eleve == 'Soldé':
                continue

            resultat.append(eleve)

        return resultat

    @staticmethod
    def modifier_eleve(eleve_id, nom, prenom, classe, annee_scolaire, montant_total_due, matricule=None):
        """Met à jour les informations d'un élève."""
        if not nom or not prenom or not classe:
            raise ValueError("Le nom, le prénom et la classe sont obligatoires.")
        eleve = EleveDAO.obtenir_par_id(eleve_id)
        if not eleve:
            raise ValueError("L'élève demandé n'existe pas.")
        try:
            montant_total_due = float(montant_total_due)
            if not math.isfinite(montant_total_due) or montant_total_due < 0:
                raise ValueError()
        except (TypeError, ValueError):
            raise ValueError("Le montant dû doit être un nombre positif.")
        matricule = (matricule or eleve.get("matricule") or EleveService.generer_matricule(classe, annee_scolaire)).strip()
        if EleveDAO.matricule_existe(matricule, sauf_eleve_id=eleve_id):
            raise ValueError(f"Le matricule {matricule} est déjà utilisé.")
        if EleveDAO.matricule_existe(matricule, sauf_eleve_id=eleve_id):
            raise ValueError(f"Le matricule {matricule} est déjà utilisé.")
        return EleveDAO.modifier(
            eleve_id,
            nom.strip(),
            prenom.strip(),
            classe.strip(),
            annee_scolaire.strip(),
            montant_total_due,
            matricule,
        )

    @staticmethod
    def calculer_statut(eleve, reste=None):
        if reste is None:
            reste = EleveService.obtenir_eleve_par_id(eleve["id"])["reste_a_payer"]
        if reste <= 0:
            return "Soldé"
        date_echeance = EcheanceDAO.obtenir_date_echeance(
            eleve.get("annee_scolaire", ""), eleve.get("classe", "")
        )
        if not date_echeance:
            return "En cours"
        try:
            echeance = date.fromisoformat(date_echeance)
        except (ValueError, TypeError):
            return "En cours"
        return "En retard" if date.today() > echeance else "En cours"

    @staticmethod
    def supprimer_eleve(eleve_id):
        """Supprime un élève de la base de données."""
        return EleveDAO.supprimer(eleve_id)