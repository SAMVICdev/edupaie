from PySide6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, 
                             QFileDialog, QHBoxLayout, QMessageBox, QLabel, QCheckBox)
from src.database.parametres_dao import ParametresDAO
from src.services.securite_service import SecuriteService

class ParametresDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres de l'Établissement")
        self.resize(520, 500)

        self.layout = QFormLayout(self)

        params = ParametresDAO.obtenir_parametres()

        self.input_nom = QLineEdit(params.get("nom_ecole", ""))
        self.input_adresse = QLineEdit(params.get("adresse", ""))
        self.input_telephone = QLineEdit(params.get("telephone", ""))
        self.input_email = QLineEdit(params.get("email", ""))
        self.input_format_matricule = QLineEdit(
            params.get("format_matricule", "{annee}-{classe}-{numero:03d}")
        )
        self.input_format_matricule.setPlaceholderText("{annee}-{classe}-{numero:03d}")
        self.btn_echeances = QPushButton("Gérer les échéances scolaires")
        self.btn_echeances.clicked.connect(self.ouvrir_echeances)
        self.protection_initiale = ParametresDAO.protection_active()

        self.checkbox_securite = QCheckBox("Protéger l'application au démarrage")
        self.checkbox_securite.setChecked(self.protection_initiale)
        self.checkbox_securite.toggled.connect(self.actualiser_champs_securite)
        self.input_mot_de_passe_actuel = QLineEdit()
        self.input_mot_de_passe_actuel.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_nouveau_mot_de_passe = QLineEdit()
        self.input_nouveau_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirmation_mot_de_passe = QLineEdit()
        self.input_confirmation_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Logo / Tampon
        self.input_logo = QLineEdit(params.get("chemin_logo", ""))
        self.btn_browse_logo = QPushButton("Parcourir...")
        self.btn_browse_logo.clicked.connect(self.choisir_logo)
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.input_logo)
        logo_layout.addWidget(self.btn_browse_logo)

        # Signature
        self.input_signature = QLineEdit(params.get("chemin_signature", ""))
        self.btn_browse_signature = QPushButton("Parcourir...")
        self.btn_browse_signature.clicked.connect(self.choisir_signature)
        sig_layout = QHBoxLayout()
        sig_layout.addWidget(self.input_signature)
        sig_layout.addWidget(self.btn_browse_signature)

        self.layout.addRow("Nom de l'école :", self.input_nom)
        self.layout.addRow("Adresse :", self.input_adresse)
        self.layout.addRow("Téléphone :", self.input_telephone)
        self.layout.addRow("Email :", self.input_email)
        self.layout.addRow("Format matricule :", self.input_format_matricule)
        self.layout.addRow(self.btn_echeances)
        self.layout.addRow("Tampon / Logo :", logo_layout)
        self.layout.addRow("Signature :", sig_layout)
        self.layout.addRow(QLabel("Sécurité"))
        self.layout.addRow(self.checkbox_securite)
        self.row_mot_de_passe_actuel = self.layout.addRow(
            "Mot de passe actuel :", self.input_mot_de_passe_actuel
        )
        self.layout.addRow("Nouveau mot de passe :", self.input_nouveau_mot_de_passe)
        self.layout.addRow("Confirmer le mot de passe :", self.input_confirmation_mot_de_passe)
        self.actualiser_champs_securite()

        # Boutons
        btn_layout = QHBoxLayout()
        self.btn_enregistrer = QPushButton("Enregistrer les modifications")
        self.btn_annuler = QPushButton("Annuler")
        
        btn_layout.addWidget(self.btn_enregistrer)
        btn_layout.addWidget(self.btn_annuler)
        self.layout.addRow(btn_layout)

        self.btn_enregistrer.clicked.connect(self.enregistrer)
        self.btn_annuler.clicked.connect(self.reject)
        self.input_nom.setFocus()

    def actualiser_champs_securite(self):
        securite_active = self.checkbox_securite.isChecked()
        self.input_mot_de_passe_actuel.setEnabled(self.protection_initiale)
        self.input_nouveau_mot_de_passe.setEnabled(securite_active)
        self.input_confirmation_mot_de_passe.setEnabled(securite_active)

    def choisir_logo(self):
        f, _ = QFileDialog.getOpenFileName(self, "Sélectionner une image", "", "Images (*.png *.jpg *.jpeg)")
        if f:
            self.input_logo.setText(f)

    def choisir_signature(self):
        f, _ = QFileDialog.getOpenFileName(self, "Sélectionner la signature", "", "Images (*.png *.jpg *.jpeg)")
        if f:
            self.input_signature.setText(f)

    def ouvrir_echeances(self):
        from src.ui.echeance_dialog import EcheanceDialog

        EcheanceDialog(self).exec()

    def enregistrer(self):
        mot_de_passe_actuel = self.input_mot_de_passe_actuel.text()
        nouveau_mot_de_passe = self.input_nouveau_mot_de_passe.text()
        confirmation = self.input_confirmation_mot_de_passe.text()
        securite_demandee = self.checkbox_securite.isChecked()
        format_matricule = self.input_format_matricule.text().strip()

        if not all(token in format_matricule for token in ("{annee}", "{classe}", "{numero")):
            QMessageBox.warning(
                self,
                "Format matricule invalide",
                "Le format doit contenir {annee}, {classe} et {numero}.",
            )
            return
        try:
            format_matricule.format(annee="2026", classe="6E", numero=1)
        except (KeyError, ValueError, IndexError):
            QMessageBox.warning(self, "Format matricule invalide", "Vérifiez la syntaxe du format matricule.")
            return

        if self.protection_initiale and (not securite_demandee or nouveau_mot_de_passe or confirmation):
            if not SecuriteService.verifier_mot_de_passe(mot_de_passe_actuel):
                QMessageBox.warning(self, "Sécurité", "Le mot de passe actuel est incorrect.")
                return

        if securite_demandee and (not self.protection_initiale or nouveau_mot_de_passe or confirmation):
            try:
                SecuriteService.valider_mot_de_passe(nouveau_mot_de_passe)
            except ValueError as exc:
                QMessageBox.warning(self, "Sécurité", str(exc))
                return
            if nouveau_mot_de_passe != confirmation:
                QMessageBox.warning(self, "Sécurité", "La confirmation du mot de passe ne correspond pas.")
                return

        ParametresDAO.sauvegarder_parametres(
            self.input_nom.text().strip(),
            self.input_adresse.text().strip(),
            self.input_telephone.text().strip(),
            self.input_email.text().strip(),
            self.input_logo.text().strip(),
            self.input_signature.text().strip(),
            format_matricule
        )

        if securite_demandee and (not self.protection_initiale or nouveau_mot_de_passe):
            SecuriteService.definir_mot_de_passe(nouveau_mot_de_passe)
        elif self.protection_initiale and not securite_demandee:
            ParametresDAO.supprimer_mot_de_passe()

        QMessageBox.information(self, "Succès", "Paramètres enregistrés avec succès !")
        self.accept()