import sys

from PySide6.QtCore import QUrl, QUrlQuery
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFormLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
)

from src.database.parametres_dao import ParametresDAO


class AssistanceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aide et assistance EDUPAIE")
        self.setFixedWidth(440)

        params = ParametresDAO.obtenir_parametres()
        email = params.get("support_email", "")
        telephone = params.get("support_telephone", "")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Pour signaler un problème, contactez l'assistance de votre établissement. "
            "N'envoyez jamais votre mot de passe."
        ))
        form = QFormLayout()
        self.lbl_email = QLabel(email or "Non configuré")
        self.lbl_telephone = QLabel(telephone or "Non configuré")
        form.addRow("Courriel(s) :", self.lbl_email)
        form.addRow("Téléphone :", self.lbl_telephone)
        layout.addLayout(form)

        actions = QHBoxLayout()
        self.btn_copier_email = QPushButton("Copier le courriel")
        self.btn_ecrire = QPushButton("Écrire à l'assistance")
        self.btn_whatsapp = QPushButton("Contacter sur WhatsApp")
        self.btn_copier_email.setEnabled(bool(email))
        self.btn_ecrire.setEnabled(bool(email))
        self.btn_whatsapp.setEnabled(bool(telephone))
        actions.addWidget(self.btn_copier_email)
        actions.addWidget(self.btn_ecrire)
        actions.addWidget(self.btn_whatsapp)
        layout.addLayout(actions)

        self.btn_fermer = QPushButton("Fermer")
        layout.addWidget(self.btn_fermer)
        self.btn_copier_email.clicked.connect(lambda: self.copier(email))
        self.btn_ecrire.clicked.connect(lambda: self.ecrire(email))
        self.btn_whatsapp.clicked.connect(lambda: self.ouvrir_whatsapp(telephone))
        self.btn_fermer.clicked.connect(self.accept)

    @staticmethod
    def copier(texte):
        QApplication.clipboard().setText(texte)

    def ecrire(self, email):
        destinataires = ",".join(
            adresse.strip() for adresse in email.replace(";", ",").split(",") if adresse.strip()
        )
        sujet = "Demande d'assistance EDUPAIE"
        corps = "Bonjour,\n\nJe rencontre le problème suivant dans EDUPAIE :\n\n"
        if not self.gestionnaire_courriel_disponible():
            self.copier(f"À : {destinataires}\nObjet : {sujet}\n\n{corps}")
            QMessageBox.information(
                self,
                "Courriel préparé",
                "Aucun logiciel de courriel n'est configuré. Le destinataire et le modèle "
                "du message ont été copiés; ouvrez votre messagerie et collez-les.",
            )
            return

        url = QUrl(f"mailto:{destinataires}")
        query = QUrlQuery()
        query.addQueryItem("subject", sujet)
        query.addQueryItem("body", corps)
        url.setQuery(query)
        if not QDesktopServices.openUrl(url):
            self.copier(f"À : {destinataires}\nObjet : {sujet}\n\n{corps}")
            QMessageBox.information(
                self,
                "Courriel préparé",
                "Le lancement de votre messagerie a échoué. Le destinataire et le modèle "
                "du message ont été copiés dans le presse-papiers.",
            )

    @staticmethod
    def gestionnaire_courriel_disponible():
        if sys.platform != "win32":
            return True
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CLASSES_ROOT, r"mailto\shell\open\command"
            ) as cle:
                commande, _ = winreg.QueryValueEx(cle, "")
            return bool(commande)
        except (OSError, ImportError):
            return False

    def ouvrir_whatsapp(self, telephone):
        numero = "".join(caractere for caractere in telephone if caractere.isdigit())
        if not QDesktopServices.openUrl(QUrl(f"https://wa.me/{numero}")):
            QMessageBox.warning(
                self,
                "WhatsApp indisponible",
                "Impossible d'ouvrir WhatsApp sur cet ordinateur.",
            )
