from PySide6.QtWidgets import (QDialog, QFormLayout, QLineEdit, 
                             QDoubleSpinBox, QPushButton, QMessageBox, QHBoxLayout)
from src.services.eleve_service import EleveService

class EleveDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un Élève")
        self.resize(350, 250)

        # Formulaire
        self.layout = QFormLayout(self)

        self.input_nom = QLineEdit()
        self.input_prenom = QLineEdit()
        self.input_classe = QLineEdit()
        self.input_annee = QLineEdit("2025-2026")
        
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 10000000)
        self.input_montant.setSingleStep(5000)
        self.input_montant.setValue(100000)

        self.layout.addRow("Nom :", self.input_nom)
        self.layout.addRow("Prénom :", self.input_prenom)
        self.layout.addRow("Classe :", self.input_classe)
        self.layout.addRow("Année Scolaire :", self.input_annee)
        self.layout.addRow("Montant Scolarité (FCFA) :", self.input_montant)

        # Boutons
        btn_layout = QHBoxLayout()
        self.btn_valider = QPushButton("Enregistrer")
        self.btn_annuler = QPushButton("Annuler")
        
        btn_layout.addWidget(self.btn_valider)
        btn_layout.addWidget(self.btn_annuler)
        self.layout.addRow(btn_layout)

        # Connexion des événements (Signals & Slots)
        self.btn_valider.clicked.connect(self.enregistrer)
        self.btn_annuler.clicked.connect(self.reject)

    def enregistrer(self):
        nom = self.input_nom.text().strip()
        prenom = self.input_prenom.text().strip()
        classe = self.input_classe.text().strip()
        annee = self.input_annee.text().strip()
        montant = self.input_montant.value()

        try:
            EleveService.inscrire_eleve(nom, prenom, classe, annee, montant)
            QMessageBox.information(self, "Succès", f"L'élève {nom} {prenom} a été inscrit avec succès !")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erreur de Saisie", str(e))