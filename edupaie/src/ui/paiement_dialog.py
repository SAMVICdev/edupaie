from PySide6.QtWidgets import (QDialog, QFormLayout, QDoubleSpinBox, 
                             QComboBox, QPushButton, QMessageBox, QHBoxLayout, QDateEdit)
from PySide6.QtCore import QDate
from src.services.paiement_service import PaiementService
from src.services.pdf_service import PDFService

class PaiementDialog(QDialog):
    def __init__(self, eleve_id, nom_eleve, prenom_eleve, classe, reste_a_payer, parent=None):
        super().__init__(parent)
        self.eleve_id = eleve_id
        self.nom_eleve = nom_eleve
        self.prenom_eleve = prenom_eleve
        self.classe = classe

        self.setWindowTitle(f"Enregistrer un Paiement - {nom_eleve} {prenom_eleve}")
        self.resize(380, 200)

        self.layout = QFormLayout(self)

        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(1, reste_a_payer)
        self.input_montant.setValue(reste_a_payer)
        self.input_montant.setSingleStep(1000)

        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Espèces", "TMoney", "Moov Money", "Chèque", "Virement"])

        self.input_date = QDateEdit(QDate.currentDate())
        self.input_date.setCalendarPopup(True)
        self.input_date.setDisplayFormat("dd/MM/yyyy")

        self.layout.addRow("Montant à verser (FCFA) :", self.input_montant)
        self.layout.addRow("Mode de paiement :", self.combo_mode)
        self.layout.addRow("Date du versement :", self.input_date)

        btn_layout = QHBoxLayout()
        self.btn_valider = QPushButton("Valider le paiement")
        self.btn_annuler = QPushButton("Annuler")

        btn_layout.addWidget(self.btn_valider)
        btn_layout.addWidget(self.btn_annuler)
        self.layout.addRow(btn_layout)

        self.btn_valider.clicked.connect(self.enregistrer)
        self.btn_annuler.clicked.connect(self.reject)
        self.input_montant.lineEdit().returnPressed.connect(self.combo_mode.setFocus)
        self.combo_mode.activated.connect(lambda: self.input_date.setFocus())
        self.input_date.lineEdit().returnPressed.connect(self.btn_valider.click)
        self.input_montant.setFocus()

    def enregistrer(self):
        montant = self.input_montant.value()
        mode_paiement = self.combo_mode.currentText()

        try:
            date_paiement = self.input_date.date().toString("yyyy-MM-dd")
            res = PaiementService.enregistrer_paiement(
                self.eleve_id, montant, mode_paiement, date_paiement
            )
            res['mode_paiement'] = mode_paiement

            eleve_data = {
                'nom': self.nom_eleve,
                'prenom': self.prenom_eleve,
                'classe': self.classe,
            }
            chemin_pdf = PDFService.generer_recu(res, eleve_data)

            QMessageBox.information(
                self, 
                "Succès", 
                f"Paiement enregistré avec succès !\n\n"
                f"N° Reçu : {res['numero_recu']}\n"
                f"Reste à payer : {res['nouveau_reste']} FCFA\n\n"
                f"Le reçu PDF a été généré sous :\n{chemin_pdf}"
            )
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))