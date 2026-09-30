import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QHeaderView)
from src.database.eleve_dao import EleveDAO
from src.services.eleve_service import EleveService
from src.ui.eleve_dialog import EleveDialog
from src.ui.paiement_dialog import PaiementDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EDUPAIE - Gestion des Paiements Scolaires")
        self.resize(950, 500)

        # Widget Central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # En-tête
        header_layout = QHBoxLayout()
        self.titre = QLabel("Liste des Élèves")
        self.titre.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.btn_ajouter = QPushButton("+ Nouvel Élève")
        self.btn_ajouter.clicked.connect(self.ouvrir_dialog_ajout)

        header_layout.addWidget(self.titre)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_ajouter)
        self.main_layout.addLayout(header_layout)

        # Tableau (7 colonnes avec la colonne Action)
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Prénom", "Classe", "Scolarité Dûe", "Reste à Payer", "Action"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_layout.addWidget(self.table)

        self.charger_eleves()

    def charger_eleves(self):
        """Récupère tous les élèves et affiche un bouton de paiement pour chacun."""
        eleves = EleveDAO.obtenir_tous()
        self.table.setRowCount(0)

        for row_idx, eleve in enumerate(eleves):
            self.table.insertRow(row_idx)
            
            details = EleveService.obtenir_details_eleve(eleve['id'])
            reste = details['reste_a_payer'] if details else eleve['montant_total_due']

            self.table.setItem(row_idx, 0, QTableWidgetItem(str(eleve['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(eleve['nom']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(eleve['prenom']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(eleve['classe']))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{eleve['montant_total_due']:,.0f} FCFA"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"{reste:,.0f} FCFA"))

            # Création du bouton Payer dans la 7ème colonne (Action)
            btn_payer = QPushButton("Payer")
            if reste <= 0:
                btn_payer.setText("Soldé")
                btn_payer.setEnabled(False)
            else:
                # Utilisation d'une lambda pour passer les infos de l'élève au clic
                btn_payer.clicked.connect(lambda _, e=eleve, r=reste: self.ouvrir_dialog_paiement(e, r))

            self.table.setCellWidget(row_idx, 6, btn_payer)

    def ouvrir_dialog_ajout(self):
        """Ouvre la pop-up d'inscription d'élève."""
        dialog = EleveDialog(self)
        if dialog.exec():
            self.charger_eleves()

    def ouvrir_dialog_paiement(self, eleve, reste):
        """Ouvre la pop-up d'enregistrement de règlement."""
        dialog = PaiementDialog(eleve['id'], f"{eleve['nom']} {eleve['prenom']}", reste, self)
        if dialog.exec():
            self.charger_eleves()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())