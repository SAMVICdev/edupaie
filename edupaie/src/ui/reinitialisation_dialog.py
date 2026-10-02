from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
)

from src.services.securite_service import SecuriteService
from src.ui.code_recuperation_dialog import CodeRecuperationDialog


class ReinitialisationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Récupérer l'accès à EDUPAIE")
        self.setFixedWidth(430)

        layout = QFormLayout(self)
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("XXXX-XXXX-XXXX-XXXX-XXXX")
        self.input_nouveau_mot_de_passe = QLineEdit()
        self.input_nouveau_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirmation = QLineEdit()
        self.input_confirmation.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("Code de secours :", self.input_code)
        layout.addRow("Nouveau mot de passe :", self.input_nouveau_mot_de_passe)
        layout.addRow("Confirmer le mot de passe :", self.input_confirmation)

        actions = QHBoxLayout()
        self.btn_reinitialiser = QPushButton("Réinitialiser")
        self.btn_annuler = QPushButton("Annuler")
        actions.addWidget(self.btn_reinitialiser)
        actions.addWidget(self.btn_annuler)
        layout.addRow(actions)

        self.btn_reinitialiser.clicked.connect(self.reinitialiser)
        self.btn_annuler.clicked.connect(self.reject)
        self.input_code.returnPressed.connect(self.input_nouveau_mot_de_passe.setFocus)
        self.input_nouveau_mot_de_passe.returnPressed.connect(self.input_confirmation.setFocus)
        self.input_confirmation.returnPressed.connect(self.btn_reinitialiser.click)
        self.input_code.setFocus()

    def reinitialiser(self):
        code_actuel = self.input_code.text().strip()
        nouveau_mot_de_passe = self.input_nouveau_mot_de_passe.text()
        confirmation = self.input_confirmation.text()

        try:
            SecuriteService.valider_mot_de_passe(nouveau_mot_de_passe)
        except ValueError as exc:
            QMessageBox.warning(self, "Mot de passe invalide", str(exc))
            return
        if nouveau_mot_de_passe != confirmation:
            QMessageBox.warning(self, "Confirmation", "Les mots de passe ne correspondent pas.")
            return
        if not SecuriteService.verifier_code_recuperation(code_actuel):
            QMessageBox.warning(self, "Code invalide", "Le code de secours est incorrect ou déjà utilisé.")
            return

        nouveau_code = SecuriteService.generer_code_recuperation()
        confirmation_code = CodeRecuperationDialog(nouveau_code, self)
        if confirmation_code.exec() != QDialog.DialogCode.Accepted:
            return
        if not SecuriteService.reinitialiser_mot_de_passe(
            code_actuel, nouveau_mot_de_passe, nouveau_code
        ):
            QMessageBox.warning(self, "Code invalide", "Le code de secours ne peut plus être utilisé.")
            return

        QMessageBox.information(
            self,
            "Mot de passe réinitialisé",
            "Votre mot de passe a été changé. Le code précédent est désormais invalide.",
        )
        self.accept()
