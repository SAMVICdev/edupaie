from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
)

from src.services.securite_service import SecuriteService


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
        self.input_mot_de_passe.setFocus()

    def verifier(self):
        if SecuriteService.verifier_mot_de_passe(self.input_mot_de_passe.text()):
            self.accept()
            return

        self.input_mot_de_passe.clear()
        QMessageBox.warning(self, "Accès refusé", "Le mot de passe est incorrect.")
        self.input_mot_de_passe.setFocus()
