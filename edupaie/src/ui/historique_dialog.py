from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QMessageBox, QHeaderView)
from src.database.paiement_dao import PaiementDAO
from src.services.eleve_service import EleveService
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "N° Reçu", "Date", "Montant", "Mode", "Ouvrir", "Imprimer"
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

            btn_ouvrir = QPushButton("Ouvrir PDF")
            btn_ouvrir.clicked.connect(lambda _, pai=p: self.ouvrir_recu(pai))
            self.table.setCellWidget(row_idx, 4, btn_ouvrir)

            btn_imprimer = QPushButton("Imprimer")
            btn_imprimer.clicked.connect(lambda _, pai=p: self.imprimer_recu(pai))
            self.table.setCellWidget(row_idx, 5, btn_imprimer)

    def generer_recu(self, paiement):
        try:
            num_recu = paiement.get('numero_recu', f"REC-{paiement['id']:04d}")
            paiement_info = dict(paiement)
            paiement_info['numero_recu'] = num_recu
            details = EleveService.obtenir_eleve_par_id(self.eleve['id']) or self.eleve
            paiement_info['total_du'] = details.get('montant_total_due', 0)
            if paiement_info.get('total_paye_apres') is None:
                paiement_info['total_paye_apres'] = details.get('total_paye', paiement['montant'])
            if paiement_info.get('reste_apres') is None:
                paiement_info['reste_apres'] = details.get('reste_a_payer', 0)
            paiement_info['nouveau_reste'] = paiement_info['reste_apres']
            paiement_info['matricule'] = details.get('matricule', '')
            fichier_pdf = PDFService.generer_recu(
                paiement_info,
                self.eleve['nom'],
                self.eleve['prenom'],
                self.eleve['classe'],
            )
            return fichier_pdf
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de générer le reçu : {str(e)}")
            return None

    def ouvrir_recu(self, paiement):
        fichier_pdf = self.generer_recu(paiement)
        if fichier_pdf:
            try:
                PDFService.ouvrir_recu(fichier_pdf)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le reçu : {str(e)}")

    def imprimer_recu(self, paiement):
        fichier_pdf = self.generer_recu(paiement)
        if fichier_pdf:
            try:
                PDFService.imprimer_recu(fichier_pdf)
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'impression", f"Impossible d'imprimer le reçu : {str(e)}")