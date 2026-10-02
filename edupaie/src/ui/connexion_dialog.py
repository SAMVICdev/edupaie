from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
)

from src.services.securite_service import SecuriteService
from src.database.parametres_dao import ParametresDAO
from src.ui.assistance_dialog import AssistanceDialog


class ConnexionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connexion EDUPAIE")
        self.setModal(True)
        self.setFixedWidth(360)

        layout = QFormLayout(self)
        layout.addRow(QLabel("Saisissez le mot de passe pour ouvrir EDUPAIE."))

        self.input_mot_de_passe = QLineEdit()
        self.input_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_mot_de_passe.returnPressed.connect(self.verifier)
        layout.addRow("Mot de passe :", self.input_mot_de_passe)

        self.btn_connexion = QPushButton("Se connecter")
        self.btn_connexion.clicked.connect(self.verifier)
        layout.addRow(self.btn_connexion)

        actions = QHBoxLayout()
        self.btn_mot_de_passe_oublie = QPushButton("Mot de passe oublié")
        self.btn_mot_de_passe_oublie.setEnabled(
            ParametresDAO.obtenir_identifiants_recuperation() is not None
        )
        self.btn_assistance = QPushButton("Aide / assistance")
        self.btn_mot_de_passe_oublie.clicked.connect(self.ouvrir_recuperation)
        self.btn_assistance.clicked.connect(self.ouvrir_assistance)
        actions.addWidget(self.btn_mot_de_passe_oublie)
        actions.addWidget(self.btn_assistance)
        layout.addRow(actions)
        self.input_mot_de_passe.setFocus()

    def ouvrir_recuperation(self):
        from src.ui.reinitialisation_dialog import ReinitialisationDialog

        ReinitialisationDialog(self).exec()

    def ouvrir_assistance(self):
        AssistanceDialog(self).exec()

    def verifier(self):
        if SecuriteService.verifier_mot_de_passe(self.input_mot_de_passe.text()):
            self.accept()
            return

        self.input_mot_de_passe.clear()
        QMessageBox.warning(self, "Accès refusé", "Le mot de passe est incorrect.")
        self.input_mot_de_passe.setFocus()
