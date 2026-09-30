from PySide6.QtWidgets import (QDialog, QFormLayout, QDoubleSpinBox, 
                             QComboBox, QPushButton, QMessageBox, QHBoxLayout)
from src.services.paiement_service import PaiementService

class PaiementDialog(QDialog):
    def __init__(self, eleve_id, nom_eleve, reste_a_payer, parent=None):
        super().__init__(parent)
        self.eleve_id = eleve_id
        self.setWindowTitle(f"Enregistrer un Paiement - {nom_eleve}")
        self.resize(380, 200)

        self.layout = QFormLayout(self)

        # Montant à payer
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(1, reste_a_payer)
        self.input_montant.setValue(reste_a_payer)
        self.input_montant.setSingleStep(1000)

        # Choix du mode de paiement
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Espèces", "Chèque", "Virement", "Mobile Money"])

        self.layout.addRow("Montant à verser (FCFA) :", self.input_montant)
        self.layout.addRow("Mode de paiement :", self.combo_mode)

        # Boutons d'action
        btn_layout = QHBoxLayout()
        self.btn_valider = QPushButton("Valider le paiement")
        self.btn_annuler = QPushButton("Annuler")

        btn_layout.addWidget(self.btn_valider)
        btn_layout.addWidget(self.btn_annuler)
        self.layout.addRow(btn_layout)

        # Signal / Slot connexions
        self.btn_valider.clicked.connect(self.enregistrer)
        self.btn_annuler.clicked.connect(self.reject)

    def enregistrer(self):
        montant = self.input_montant.value()
        mode_paiement = self.combo_mode.currentText()

        try:
            res = PaiementService.enregistrer_paiement(self.eleve_id, montant, mode_paiement)
            QMessageBox.information(
                self, 
                "Succès", 
                f"Paiement enregistré !\nN° Reçu : {res['numero_recu']}\nReste à payer : {res['nouveau_reste']} FCFA"
            )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erreur", str(e))