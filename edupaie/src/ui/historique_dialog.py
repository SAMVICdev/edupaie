import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QMessageBox, QHeaderView)
from src.database.paiement_dao import PaiementDAO
from src.services.pdf_service import PDFService

class HistoriqueDialog(QDialog):
    def __init__(self, eleve, parent=None):
        super().__init__(parent)
        self.eleve = eleve
        self.setWindowTitle(f"Historique des paiements - {eleve['nom']} {eleve['prenom']}")
        self.resize(600, 380)

        layout = QVBoxLayout(self)

        lbl_titre = QLabel(f"Historique pour : {eleve['nom']} {eleve['prenom']} ({eleve['classe']})")
        lbl_titre.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 8px;")
        layout.addWidget(lbl_titre)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "N° Reçu", "Date", "Montant", "Mode", "Action"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.charger_historique()

    def charger_historique(self):
        paiements = PaiementDAO.obtenir_par_eleve(self.eleve['id'])
        self.table.setRowCount(0)

        for row_idx, p in enumerate(paiements):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(p.get('numero_recu', f"REC-{p['id']:04d}"))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(p['date_paiement'])))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{p['montant']:,.0f} FCFA"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(p.get('mode_paiement', 'Espèces'))))

            btn_pdf = QPushButton("📄 Reçu PDF")
            btn_pdf.clicked.connect(lambda _, pai=p: self.reimprimer_recu(pai))
            self.table.setCellWidget(row_idx, 4, btn_pdf)

    def reimprimer_recu(self, paiement):
        try:
            num_recu = paiement.get('numero_recu', f"REC-{paiement['id']:04d}")
            fichier_pdf = PDFService.generer_recu(
                numero_recu=num_recu,
                nom_eleve=self.eleve['nom'],
                prenom_eleve=self.eleve['prenom'],
                classe=self.eleve['classe'],
                montant_paye=paiement['montant'],
                reste_a_payer=0,
                mode_paiement=paiement.get('mode_paiement', 'Espèces')
            )
            os.system(f'start "" "{fichier_pdf}"')
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de générer le reçu : {str(e)}")