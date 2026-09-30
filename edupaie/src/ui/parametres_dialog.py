from PySide6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, 
                             QFileDialog, QHBoxLayout, QMessageBox, QLabel)
from src.database.parametres_dao import ParametresDAO

class ParametresDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres de l'Établissement")
        self.resize(450, 350)

        self.layout = QFormLayout(self)

        params = ParametresDAO.obtenir_parametres()

        self.input_nom = QLineEdit(params.get("nom_ecole", ""))
        self.input_adresse = QLineEdit(params.get("adresse", ""))
        self.input_telephone = QLineEdit(params.get("telephone", ""))
        self.input_email = QLineEdit(params.get("email", ""))
        self.input_annee = QLineEdit(params.get("annee_scolaire", "2025-2026"))
        
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
        self.layout.addRow("Année scolaire active :", self.input_annee)
        self.layout.addRow("Tampon / Logo :", logo_layout)
        self.layout.addRow("Signature :", sig_layout)

        # Boutons
        btn_layout = QHBoxLayout()
        self.btn_enregistrer = QPushButton("Enregistrer les modifications")
        self.btn_annuler = QPushButton("Annuler")
        
        btn_layout.addWidget(self.btn_enregistrer)
        btn_layout.addWidget(self.btn_annuler)
        self.layout.addRow(btn_layout)

        self.btn_enregistrer.clicked.connect(self.enregistrer)
        self.btn_annuler.clicked.connect(self.reject)

    def choisir_logo(self):
        f, _ = QFileDialog.getOpenFileName(self, "Sélectionner une image", "", "Images (*.png *.jpg *.jpeg)")
        if f:
            self.input_logo.setText(f)

    def choisir_signature(self):
        f, _ = QFileDialog.getOpenFileName(self, "Sélectionner la signature", "", "Images (*.png *.jpg *.jpeg)")
        if f:
            self.input_signature.setText(f)

    def enregistrer(self):
        annee_scolaire = self.input_annee.text().strip() or "2025-2026"
        ParametresDAO.sauvegarder_parametres(
            self.input_nom.text().strip(),
            self.input_adresse.text().strip(),
            self.input_telephone.text().strip(),
            self.input_email.text().strip(),
            self.input_logo.text().strip(),
            self.input_signature.text().strip(),
            annee_scolaire
        )
        QMessageBox.information(self, "Succès", "Paramètres enregistrés avec succès !")
        self.accept()