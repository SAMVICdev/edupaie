import hashlib
import hmac
import secrets

from src.database.parametres_dao import ParametresDAO


class SecuriteService:
    ITERATIONS = 310_000

    @staticmethod
    def valider_mot_de_passe(mot_de_passe):
        if len(mot_de_passe) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères.")

    @staticmethod
    def _calculer_hash(mot_de_passe, salt):
        return hashlib.pbkdf2_hmac(
            "sha256",
            mot_de_passe.encode("utf-8"),
            bytes.fromhex(salt),
            SecuriteService.ITERATIONS,
        ).hex()

    @staticmethod
    def definir_mot_de_passe(mot_de_passe):
        SecuriteService.valider_mot_de_passe(mot_de_passe)
        salt = secrets.token_hex(16)
        password_hash = SecuriteService._calculer_hash(mot_de_passe, salt)
        ParametresDAO.sauvegarder_mot_de_passe(salt, password_hash)

    @staticmethod
    def verifier_mot_de_passe(mot_de_passe):
        identifiants = ParametresDAO.obtenir_identifiants_securite()
        if not identifiants:
            return False
        salt, password_hash = identifiants
        candidat = SecuriteService._calculer_hash(mot_de_passe, salt)
        return hmac.compare_digest(candidat, password_hash)
