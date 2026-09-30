import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QHeaderView, QFrame,
                             QLineEdit, QComboBox)
from PySide6.QtCore import Qt
from src.database.eleve_dao import EleveDAO
from src.database.paiement_dao import PaiementDAO
from src.services.eleve_service import EleveService
from src.ui.eleve_dialog import EleveDialog
from src.ui.paiement_dialog import PaiementDialog
from src.ui.parametres_dialog import ParametresDialog
from src.ui.historique_dialog import HistoriqueDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EDUPAIE - Gestion des Paiements Scolaires")
        self.resize(1050, 600)

        # Widget Central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # En-tête
        header_layout = QHBoxLayout()
        self.titre = QLabel("Tableau de Bord & Élèves")
        self.titre.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        self.btn_parametres = QPushButton("⚙️ Paramètres")
        self.btn_parametres.clicked.connect(self.ouvrir_dialog_parametres)

        self.btn_ajouter = QPushButton("+ Nouvel Élève")
        self.btn_ajouter.clicked.connect(self.ouvrir_dialog_ajout)

        header_layout.addWidget(self.titre)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_parametres)
        header_layout.addWidget(self.btn_ajouter)
        self.main_layout.addLayout(header_layout)

        # Filtres de recherche
        self.filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom ou prénom...")
        self.search_input.textChanged.connect(self.appliquer_filtres)

        self.combo_classe = QComboBox()
        self.combo_classe.addItem("Toutes les classes")
        self.combo_classe.currentIndexChanged.connect(self.appliquer_filtres)

        self.combo_statut = QComboBox()
        self.combo_statut.addItems(["Tous", "Soldé", "Non soldé"])
        self.combo_statut.currentIndexChanged.connect(self.appliquer_filtres)

        self.filter_layout.addWidget(QLabel("Recherche :"))
        self.filter_layout.addWidget(self.search_input, 2)
        self.filter_layout.addWidget(QLabel("Classe :"))
        self.filter_layout.addWidget(self.combo_classe, 1)
        self.filter_layout.addWidget(QLabel("Statut :"))
        self.filter_layout.addWidget(self.combo_statut, 1)
        self.main_layout.addLayout(self.filter_layout)

        # Widgets de Statistiques
        self.stats_layout = QHBoxLayout()
        self.card_total_encaisse = self.creer_carte_stat("Total Encaissé", "0 FCFA", "#2e7d32")
        self.card_total_impayes = self.creer_carte_stat("Reste à Recouvrer", "0 FCFA", "#c62828")
        self.card_total_eleves = self.creer_carte_stat("Élèves Inscrits", "0", "#1565c0")
        
        self.stats_layout.addWidget(self.card_total_encaisse)
        self.stats_layout.addWidget(self.card_total_impayes)
        self.stats_layout.addWidget(self.card_total_eleves)
        self.main_layout.addLayout(self.stats_layout)

        # Tableau (8 colonnes avec Historique)
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Prénom", "Classe", "Scolarité Dûe", "Reste à Payer", "Paiement", "Historique"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_layout.addWidget(self.table)

        self.remplir_filtre_classes()
        self.charger_eleves()

    def remplir_filtre_classes(self):
        classes = sorted({eleve.get('classe', '') for eleve in EleveDAO.obtenir_tous() if eleve.get('classe')})
        self.combo_classe.blockSignals(True)
        self.combo_classe.clear()
        self.combo_classe.addItem("Toutes les classes")
        for classe in classes:
            self.combo_classe.addItem(classe)
        self.combo_classe.blockSignals(False)

    def appliquer_filtres(self):
        self.charger_eleves()

    def charger_eleves(self):
        recherche = self.search_input.text()
        classe_selectionnee = self.combo_classe.currentText()
        statut_selectionne = self.combo_statut.currentText()

        if classe_selectionnee == "Toutes les classes":
            classe_selectionnee = ""

        eleves = EleveService.filtrer_eleves(recherche, classe_selectionnee, statut_selectionne)
        self.table.setRowCount(0)

        total_encaisse_global = PaiementDAO.obtenir_total_encaisse()
        total_reste_global = 0.0

        for row_idx, eleve in enumerate(eleves):
            self.table.insertRow(row_idx)
            
            details = EleveService.obtenir_eleve_par_id(eleve['id'])
            reste = details['reste_a_payer'] if details else eleve['montant_total_due']
            total_reste_global += reste

            self.table.setItem(row_idx, 0, QTableWidgetItem(str(eleve['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(eleve['nom']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(eleve['prenom']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(eleve['classe']))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{eleve['montant_total_due']:,.0f} FCFA"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"{reste:,.0f} FCFA"))

            btn_payer = QPushButton("Payer")
            if reste <= 0:
                btn_payer.setText("Soldé")
                btn_payer.setEnabled(False)
            else:
                btn_payer.clicked.connect(lambda _, e=eleve, r=reste: self.ouvrir_dialog_paiement(e, r))
            self.table.setCellWidget(row_idx, 6, btn_payer)

            btn_historique = QPushButton("📜 Voir")
            btn_historique.clicked.connect(lambda _, e=eleve: self.ouvrir_dialog_historique(e))
            self.table.setCellWidget(row_idx, 7, btn_historique)

        self.mettre_a_jour_stats(total_encaisse_global, total_reste_global, len(eleves))

    def ouvrir_dialog_ajout(self):
        dialog = EleveDialog(self)
        if dialog.exec():
            self.remplir_filtre_classes()
            self.charger_eleves()

    def ouvrir_dialog_paiement(self, eleve, reste):
        dialog = PaiementDialog(
            eleve_id=eleve['id'],
            nom_eleve=eleve['nom'],
            prenom_eleve=eleve['prenom'],
            classe=eleve['classe'],
            reste_a_payer=reste,
            parent=self
        )
        if dialog.exec():
            self.remplir_filtre_classes()
            self.charger_eleves()

    def ouvrir_dialog_historique(self, eleve):
        dialog = HistoriqueDialog(eleve, self)
        dialog.exec()

    def ouvrir_dialog_parametres(self):
        dialog = ParametresDialog(self)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    def creer_carte_stat(self, titre, valeur_initiale, couleur):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #f8f9fa;
                border-left: 5px solid {couleur};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        layout = QVBoxLayout(frame)
        lbl_titre = QLabel(titre)
        lbl_titre.setStyleSheet("color: #555555; font-size: 12px;")
        lbl_valeur = QLabel(valeur_initiale)
        lbl_valeur.setObjectName("valeur")
        lbl_valeur.setStyleSheet(f"color: {couleur}; font-size: 16px; font-weight: bold;")
        
        layout.addWidget(lbl_titre)
        layout.addWidget(lbl_valeur)
        return frame

    def mettre_a_jour_stats(self, total_encaisse, total_reste, nbr_eleves):
        self.card_total_encaisse.findChild(QLabel, "valeur").setText(f"{total_encaisse:,.0f} FCFA")
        self.card_total_impayes.findChild(QLabel, "valeur").setText(f"{total_reste:,.0f} FCFA")
        self.card_total_eleves.findChild(QLabel, "valeur").setText(str(nbr_eleves))

    def charger_eleves(self):
        eleves = EleveDAO.obtenir_tous()
        self.table.setRowCount(0)

        total_encaisse_global = PaiementDAO.obtenir_total_encaisse()
        total_reste_global = 0.0

        for row_idx, eleve in enumerate(eleves):
            self.table.insertRow(row_idx)
            
            details = EleveService.obtenir_eleve_par_id(eleve['id'])
            reste = details['reste_a_payer'] if details else eleve['montant_total_due']
            total_reste_global += reste

            self.table.setItem(row_idx, 0, QTableWidgetItem(str(eleve['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(eleve['nom']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(eleve['prenom']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(eleve['classe']))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{eleve['montant_total_due']:,.0f} FCFA"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"{reste:,.0f} FCFA"))

            # Bouton Payer
            btn_payer = QPushButton("Payer")
            if reste <= 0:
                btn_payer.setText("Soldé")
                btn_payer.setEnabled(False)
            else:
                btn_payer.clicked.connect(lambda _, e=eleve, r=reste: self.ouvrir_dialog_paiement(e, r))
            self.table.setCellWidget(row_idx, 6, btn_payer)

            # Bouton Historique
            btn_historique = QPushButton("📜 Voir")
            btn_historique.clicked.connect(lambda _, e=eleve: self.ouvrir_dialog_historique(e))
            self.table.setCellWidget(row_idx, 7, btn_historique)

        self.mettre_a_jour_stats(total_encaisse_global, total_reste_global, len(eleves))

    def ouvrir_dialog_ajout(self):
        dialog = EleveDialog(self)
        if dialog.exec():
            self.charger_eleves()

    def ouvrir_dialog_paiement(self, eleve, reste):
        dialog = PaiementDialog(
            eleve_id=eleve['id'],
            nom_eleve=eleve['nom'],
            prenom_eleve=eleve['prenom'],
            classe=eleve['classe'],
            reste_a_payer=reste,
            parent=self
        )
        if dialog.exec():
            self.charger_eleves()

    def ouvrir_dialog_historique(self, eleve):
        dialog = HistoriqueDialog(eleve, self)
        dialog.exec()

    def ouvrir_dialog_parametres(self):
        dialog = ParametresDialog(self)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())