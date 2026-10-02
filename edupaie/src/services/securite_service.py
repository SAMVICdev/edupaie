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
    def _empreinte(secret):
        salt = secrets.token_hex(16)
        return salt, SecuriteService._calculer_hash(secret, salt)

    @staticmethod
    def definir_mot_de_passe(mot_de_passe, code_recuperation=None):
        SecuriteService.valider_mot_de_passe(mot_de_passe)
        password_salt, password_hash = SecuriteService._empreinte(mot_de_passe)
        if code_recuperation:
            recovery_salt, recovery_hash = SecuriteService._empreinte(
                SecuriteService._normaliser_code(code_recuperation)
            )
            ParametresDAO.sauvegarder_securite(
                password_salt, password_hash, recovery_salt, recovery_hash
            )
        else:
            ParametresDAO.sauvegarder_mot_de_passe(password_salt, password_hash)

    @staticmethod
    def verifier_mot_de_passe(mot_de_passe):
        identifiants = ParametresDAO.obtenir_identifiants_securite()
        if not identifiants:
            return False
        salt, password_hash = identifiants
        candidat = SecuriteService._calculer_hash(mot_de_passe, salt)
        return hmac.compare_digest(candidat, password_hash)

    @staticmethod
    def generer_code_recuperation():
        valeur = secrets.token_hex(10).upper()
        return "-".join(valeur[index:index + 4] for index in range(0, len(valeur), 4))

    @staticmethod
    def _normaliser_code(code):
        return "".join(caractere for caractere in code.upper() if caractere.isalnum())

    @staticmethod
    def verifier_code_recuperation(code):
        identifiants = ParametresDAO.obtenir_identifiants_recuperation()
        if not identifiants or not code:
            return False
        salt, recovery_hash = identifiants
        candidat = SecuriteService._calculer_hash(
            SecuriteService._normaliser_code(code), salt
        )
        return hmac.compare_digest(candidat, recovery_hash)

    @staticmethod
    def reinitialiser_mot_de_passe(code_actuel, nouveau_mot_de_passe, nouveau_code):
        SecuriteService.valider_mot_de_passe(nouveau_mot_de_passe)
        if not SecuriteService.verifier_code_recuperation(code_actuel):
            return False
        password_salt, password_hash = SecuriteService._empreinte(nouveau_mot_de_passe)
        recovery_salt, recovery_hash = SecuriteService._empreinte(
            SecuriteService._normaliser_code(nouveau_code)
        )
        ParametresDAO.sauvegarder_securite(
            password_salt, password_hash, recovery_salt, recovery_hash
        )
        return True
