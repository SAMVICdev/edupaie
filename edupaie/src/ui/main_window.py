import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QHeaderView, QFrame,
                             QLineEdit, QComboBox, QDialog, QFileDialog, QInputDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from src.database.connection import init_db
from src.database.eleve_dao import EleveDAO
from src.database.paiement_dao import PaiementDAO
from src.database.parametres_dao import ParametresDAO
from src.services.eleve_service import EleveService
from src.services.import_export_service import ImportExportService
from src.ui.eleve_dialog import EleveDialog
from src.ui.paiement_dialog import PaiementDialog
from src.ui.parametres_dialog import ParametresDialog
from src.ui.historique_dialog import HistoriqueDialog
from src.ui.connexion_dialog import ConnexionDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EDUPAIE - Gestion des Paiements Scolaires")
        self.resize(1050, 600)

        # Widget Central
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # En-tête
        header_layout = QHBoxLayout()
        self.titre = QLabel("Tableau de Bord & Élèves")
        self.titre.setObjectName("pageTitle")
        
        self.btn_parametres = QPushButton("⚙️ Paramètres")
        self.btn_parametres.clicked.connect(self.ouvrir_dialog_parametres)

        self.btn_ajouter = QPushButton("+ Nouvel Élève")
        self.btn_ajouter.clicked.connect(self.ouvrir_dialog_ajout)

        self.btn_modifier = QPushButton("Modifier")
        self.btn_modifier.clicked.connect(self.modifier_eleve_selectionne)
        self.btn_supprimer = QPushButton("Supprimer")
        self.btn_supprimer.clicked.connect(self.supprimer_eleve_selectionne)

        self.btn_importer = QPushButton("Importer")
        self.btn_importer.clicked.connect(self.importer_donnees)
        self.btn_exporter = QPushButton("Exporter")
        self.btn_exporter.clicked.connect(self.exporter_donnees)

        header_layout.addWidget(self.titre)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_parametres)
        header_layout.addWidget(self.btn_ajouter)
        header_layout.addWidget(self.btn_modifier)
        header_layout.addWidget(self.btn_supprimer)
        header_layout.addWidget(self.btn_importer)
        header_layout.addWidget(self.btn_exporter)
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
        self.combo_statut.addItems(["Tous", "Soldé", "En cours", "En retard", "Non soldé"])
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

        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "ID", "Matricule", "Nom", "Prénom", "Classe", "Frais totaux",
            "Total versé", "Reste à payer", "Statut", "Paiement", "Historique"
        ])
        self.table.setColumnHidden(0, True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self.actualiser_actions_selection)
        self.table.cellDoubleClicked.connect(lambda _row, _column: self.modifier_eleve_selectionne())
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_layout.addWidget(self.table)

        self.raccourci_nouvel_eleve = QShortcut(QKeySequence("Ctrl+N"), self)
        self.raccourci_nouvel_eleve.activated.connect(self.ouvrir_dialog_ajout)
        self.raccourci_paiement = QShortcut(QKeySequence("Ctrl+P"), self)
        self.raccourci_paiement.activated.connect(self.payer_eleve_selectionne)
        self.raccourci_recherche = QShortcut(QKeySequence("Ctrl+F"), self)
        self.raccourci_recherche.activated.connect(self.focus_recherche)

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

    def actualiser_actions_selection(self):
        selectionne = self.table.currentRow() >= 0
        self.btn_modifier.setEnabled(selectionne)
        self.btn_supprimer.setEnabled(selectionne)

    def obtenir_eleve_selectionne(self):
        ligne = self.table.currentRow()
        if ligne < 0:
            return None
        item_id = self.table.item(ligne, 0)
        return EleveDAO.obtenir_par_id(int(item_id.text())) if item_id else None

    def modifier_eleve_selectionne(self):
        eleve = self.obtenir_eleve_selectionne()
        if not eleve:
            QMessageBox.information(self, "Élève", "Sélectionnez un élève à modifier.")
            return
        if EleveDialog(self, eleve).exec():
            self.remplir_filtre_classes()
            self.charger_eleves()

    def supprimer_eleve_selectionne(self):
        eleve = self.obtenir_eleve_selectionne()
        if not eleve:
            QMessageBox.information(self, "Élève", "Sélectionnez un élève à supprimer.")
            return
        confirmation = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Supprimer {eleve['nom']} {eleve['prenom']} et tous ses paiements ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            EleveService.supprimer_eleve(eleve["id"])
            self.remplir_filtre_classes()
            self.charger_eleves()

    def payer_eleve_selectionne(self):
        eleve = self.obtenir_eleve_selectionne()
        if not eleve:
            QMessageBox.information(self, "Paiement", "Sélectionnez un élève avant d'enregistrer un paiement.")
            return
        details = EleveService.obtenir_eleve_par_id(eleve["id"])
        if details and details["reste_a_payer"] > 0:
            self.ouvrir_dialog_paiement(eleve, details["reste_a_payer"])

    def focus_recherche(self):
        self.search_input.setFocus()
        self.search_input.selectAll()

    def importer_donnees(self):
        chemin, _ = QFileDialog.getOpenFileName(
            self, "Importer une liste d'élèves", "", "Fichiers CSV/Excel (*.csv *.xlsx)"
        )
        if not chemin:
            return
        try:
            resultat = ImportExportService.importer_eleves(chemin)
            message = f"{resultat['importes']} élève(s) importé(s)."
            if resultat["erreurs"]:
                message += "\n\nErreurs :\n" + "\n".join(resultat["erreurs"][:10])
            QMessageBox.information(self, "Import terminé", message)
            self.remplir_filtre_classes()
            self.charger_eleves()
        except Exception as exc:
            QMessageBox.critical(self, "Erreur d'import", str(exc))

    def exporter_donnees(self):
        choix, valide = QInputDialog.getItem(
            self,
            "Exporter les données",
            "Rapport à exporter :",
            ["Liste des élèves", "Historique des paiements"],
            0,
            False,
        )
        if not valide:
            return
        nom = "eleves" if choix == "Liste des élèves" else "historique_paiements"
        chemin, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les données",
            nom,
            "CSV (*.csv);;Excel (*.xlsx)",
        )
        if not chemin:
            return
        try:
            if choix == "Liste des élèves":
                resultat = ImportExportService.exporter_eleves(
                    EleveService.obtenir_tous_les_eleves(), chemin
                )
            else:
                resultat = ImportExportService.exporter_historique(chemin)
            QMessageBox.information(self, "Export terminé", f"Fichier créé :\n{resultat}")
        except Exception as exc:
            QMessageBox.critical(self, "Erreur d'export", str(exc))

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
            total_paye = details['total_paye'] if details else 0
            total_reste_global += reste

            self.table.setItem(row_idx, 0, QTableWidgetItem(str(eleve['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(eleve.get('matricule', '')))
            self.table.setItem(row_idx, 2, QTableWidgetItem(eleve['nom']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(eleve['prenom']))
            self.table.setItem(row_idx, 4, QTableWidgetItem(eleve['classe']))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"{eleve['montant_total_due']:,.0f} FCFA"))
            self.table.setItem(row_idx, 6, QTableWidgetItem(f"{total_paye:,.0f} FCFA"))
            self.table.setItem(row_idx, 7, QTableWidgetItem(f"{reste:,.0f} FCFA"))
            statut = EleveService.calculer_statut(eleve, reste)
            item_statut = QTableWidgetItem(statut)
            item_statut.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 8, item_statut)

            btn_payer = QPushButton("Payer")
            if reste <= 0:
                btn_payer.setText("Soldé")
                btn_payer.setEnabled(False)
            else:
                btn_payer.clicked.connect(lambda _, e=eleve, r=reste: self.ouvrir_dialog_paiement(e, r))
            self.table.setCellWidget(row_idx, 9, btn_payer)

            btn_historique = QPushButton("📜 Voir")
            btn_historique.clicked.connect(lambda _, e=eleve: self.ouvrir_dialog_historique(e))
            self.table.setCellWidget(row_idx, 10, btn_historique)

        self.mettre_a_jour_stats(total_encaisse_global, total_reste_global, len(eleves))
        self.actualiser_actions_selection()

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

    def creer_carte_stat(self, titre, valeur_initiale, couleur):
        frame = QFrame()
        frame.setObjectName("statCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 10, 14, 10)
        lbl_titre = QLabel(titre)
        lbl_titre.setObjectName("statLabel")
        lbl_valeur = QLabel(valeur_initiale)
        lbl_valeur.setObjectName("statValue")
        layout.addWidget(lbl_titre)
        layout.addWidget(lbl_valeur)
        return frame

    def mettre_a_jour_stats(self, total_encaisse, total_reste, nbr_eleves):
        self.card_total_encaisse.findChild(QLabel, "statValue").setText(f"{total_encaisse:,.0f} FCFA")
        self.card_total_impayes.findChild(QLabel, "statValue").setText(f"{total_reste:,.0f} FCFA")
        self.card_total_eleves.findChild(QLabel, "statValue").setText(str(nbr_eleves))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    init_db()
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    stylesheet_path = os.path.join(base_dir, "style.qss")
    if not os.path.exists(stylesheet_path):
        stylesheet_path = os.path.join(base_dir, "src", "ui", "style.qss")
    if os.path.exists(stylesheet_path):
        with open(stylesheet_path, "r", encoding="utf-8") as stylesheet_file:
            app.setStyleSheet(stylesheet_file.read())

    if ParametresDAO.protection_active():
        connexion = ConnexionDialog()
        if connexion.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())