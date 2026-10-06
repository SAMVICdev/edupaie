import sys
import os
import math
from datetime import date
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QHeaderView, QFrame,
                             QLineEdit, QComboBox, QDialog, QFileDialog, QInputDialog,
                             QButtonGroup, QScrollArea)
from PySide6.QtCore import Qt, QMargins, QTimer
from PySide6.QtGui import QColor, QFont, QFontDatabase, QKeySequence, QPainter, QShortcut
from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QPieSeries,
    QValueAxis,
)
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
from src.ui.assistance_dialog import AssistanceDialog
from src.ui.guide_dialog import GuideDialog


def charger_police_systeme(app):
    if sys.platform != "win32":
        return
    dossier_polices = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    for famille, fichier in (("Segoe UI", "segoeui.ttf"), ("Arial", "arial.ttf")):
        chemin = os.path.join(dossier_polices, fichier)
        if os.path.isfile(chemin) and QFontDatabase.addApplicationFont(chemin) >= 0:
            app.setFont(QFont(famille))
            return


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EDUPAIE - Gestion des Paiements Scolaires")
        self.resize(1200, 820)

        # Application shell: fixed navigation rail and scrollable work area.
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        self.shell_layout = QHBoxLayout(self.central_widget)
        self.shell_layout.setContentsMargins(0, 0, 0, 0)
        self.shell_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(228)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(14, 20, 14, 16)
        self.sidebar_layout.setSpacing(7)
        self.shell_layout.addWidget(self.sidebar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("dashboardScroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.content_widget = QWidget()
        self.content_widget.setObjectName("dashboardContent")
        self.scroll_area.setWidget(self.content_widget)
        self.shell_layout.addWidget(self.scroll_area, 1)

        self.main_layout = QVBoxLayout(self.content_widget)
        self.main_layout.setContentsMargins(24, 20, 24, 22)
        self.main_layout.setSpacing(14)

        # En-tête
        header_layout = QHBoxLayout()
        self.titre = QLabel("Tableau de Bord & Élèves")
        self.titre.setObjectName("pageTitle")
        
        self.btn_parametres = QPushButton("Paramètres")
        self.btn_parametres.clicked.connect(self.ouvrir_dialog_parametres)
        self.btn_aide = QPushButton("Aide")
        self.btn_aide.setObjectName("helpAction")
        self.btn_aide.clicked.connect(self.ouvrir_assistance)

        self.btn_ajouter = QPushButton("+ Nouvel Élève")
        self.btn_ajouter.setObjectName("primaryAction")
        self.btn_ajouter.clicked.connect(self.ouvrir_dialog_ajout)

        self.btn_modifier = QPushButton("Modifier")
        self.btn_modifier.clicked.connect(self.modifier_eleve_selectionne)
        self.btn_supprimer = QPushButton("Supprimer")
        self.btn_supprimer.setObjectName("dangerAction")
        self.btn_supprimer.clicked.connect(self.supprimer_eleve_selectionne)

        self.btn_importer = QPushButton("Importer")
        self.btn_importer.clicked.connect(self.importer_donnees)
        self.btn_exporter = QPushButton("Exporter")
        self.btn_exporter.setObjectName("exportAction")
        self.btn_exporter.clicked.connect(self.exporter_donnees)

        self.construire_barre_laterale()

        self.btn_ajouter.setObjectName("primaryAction")
        self.btn_supprimer.setObjectName("dangerAction")

        header_layout.addWidget(self.titre)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_ajouter)
        header_layout.addWidget(self.btn_modifier)
        header_layout.addWidget(self.btn_supprimer)
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

        self.charts_layout = QHBoxLayout()
        self.chart_encaissements = self.creer_graphique_encaissements()
        self.chart_repartition = self.creer_graphique_repartition()
        self.charts_layout.addWidget(self.chart_encaissements, 3)
        self.charts_layout.addWidget(self.chart_repartition, 2)
        self.main_layout.addLayout(self.charts_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "ID", "Matricule", "Nom", "Prénom", "Classe", "Frais",
            "Versé", "Reste", "Statut", "Paiement", "Historique"
        ])
        titre_liste = QHBoxLayout()
        self.lbl_titre_liste = QLabel("Élèves inscrits")
        self.lbl_titre_liste.setObjectName("sectionHeading")
        self.lbl_unite_montants = QLabel("Montants en FCFA")
        self.lbl_unite_montants.setObjectName("sectionNote")
        titre_liste.addWidget(self.lbl_titre_liste)
        titre_liste.addStretch()
        titre_liste.addWidget(self.lbl_unite_montants)
        self.main_layout.addLayout(titre_liste)
        self.table.setColumnHidden(0, True)
        self.table.setToolTip("Tous les montants sont exprimés en FCFA.")
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.itemSelectionChanged.connect(self.actualiser_actions_selection)
        self.table.cellDoubleClicked.connect(lambda _row, _column: self.modifier_eleve_selectionne())
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(False)
        for colonne, largeur in {
            1: 110,
            2: 92,
            3: 96,
            4: 74,
            5: 80,
            6: 80,
            7: 82,
            8: 88,
            9: 106,
            10: 76,
        }.items():
            self.table.setColumnWidth(colonne, largeur)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.main_layout.addWidget(self.table)

        self.raccourci_nouvel_eleve = QShortcut(QKeySequence("Ctrl+N"), self)
        self.raccourci_nouvel_eleve.activated.connect(self.ouvrir_dialog_ajout)
        self.raccourci_paiement = QShortcut(QKeySequence("Ctrl+P"), self)
        self.raccourci_paiement.activated.connect(self.payer_eleve_selectionne)
        self.raccourci_recherche = QShortcut(QKeySequence("Ctrl+F"), self)
        self.raccourci_recherche.activated.connect(self.focus_recherche)

        self.remplir_filtre_classes()
        self.charger_eleves()
        self._mois_graphique = date.today().strftime("%Y-%m")
        self.timer_verification_mois = QTimer(self)
        self.timer_verification_mois.setInterval(60_000)
        self.timer_verification_mois.timeout.connect(self.verifier_mise_a_jour_mois)
        self.timer_verification_mois.start()

    def construire_barre_laterale(self):
        self.groupe_navigation = QButtonGroup(self)
        self.groupe_navigation.setExclusive(True)

        marque = QLabel("EDUPAIE")
        marque.setObjectName("sidebarBrand")
        sous_titre = QLabel("GESTION SCOLAIRE")
        sous_titre.setObjectName("sidebarSubtitle")
        self.sidebar_layout.addWidget(marque)
        self.sidebar_layout.addWidget(sous_titre)
        self.sidebar_layout.addSpacing(24)

        section_menu = QLabel("ESPACE DE TRAVAIL")
        section_menu.setObjectName("sidebarSection")
        self.sidebar_layout.addWidget(section_menu)

        self.btn_nav_dashboard = self.ajouter_navigation(
            "Tableau de bord", self.aller_au_tableau_de_bord, selectionne=True
        )
        self.btn_nav_eleves = self.ajouter_navigation(
            "Élèves", self.aller_aux_eleves
        )
        self.btn_nav_paiement = self.ajouter_navigation(
            "Nouveau paiement", self.payer_eleve_selectionne
        )
        self.sidebar_layout.addWidget(self.btn_nav_dashboard)
        self.sidebar_layout.addWidget(self.btn_nav_eleves)
        self.sidebar_layout.addWidget(self.btn_nav_paiement)

        section_donnees = QLabel("DONNÉES")
        section_donnees.setObjectName("sidebarSection")
        self.sidebar_layout.addSpacing(18)
        self.sidebar_layout.addWidget(section_donnees)
        for bouton in (self.btn_importer, self.btn_exporter):
            bouton.setObjectName("sidebarNavButton")
            bouton.setCheckable(True)
            self.groupe_navigation.addButton(bouton)
            self.sidebar_layout.addWidget(bouton)

        section_reglages = QLabel("CONFIGURATION")
        section_reglages.setObjectName("sidebarSection")
        self.sidebar_layout.addSpacing(18)
        self.sidebar_layout.addWidget(section_reglages)
        self.btn_nav_echeances = self.ajouter_navigation(
            "Échéances scolaires", self.ouvrir_dialog_echeances
        )
        self.btn_nav_guide = self.ajouter_navigation(
            "Guide utilisateur", self.ouvrir_guide
        )
        for bouton in (self.btn_nav_echeances, self.btn_nav_guide, self.btn_parametres, self.btn_aide):
            if bouton not in (self.btn_nav_echeances, self.btn_nav_guide):
                bouton.setObjectName("sidebarNavButton")
                bouton.setCheckable(True)
                self.groupe_navigation.addButton(bouton)
            self.sidebar_layout.addWidget(bouton)

        self.sidebar_layout.addStretch()
        nom_ecole = ParametresDAO.obtenir_parametres().get("nom_ecole", "Établissement scolaire")
        self.sidebar_etablissement = QLabel(nom_ecole)
        self.sidebar_etablissement.setObjectName("sidebarSchool")
        self.sidebar_etablissement.setWordWrap(True)
        self.sidebar_layout.addWidget(self.sidebar_etablissement)

    def ajouter_navigation(self, texte, action, selectionne=False):
        bouton = QPushButton(texte)
        bouton.setObjectName("sidebarNavButton")
        bouton.setCheckable(True)
        bouton.setChecked(selectionne)
        bouton.clicked.connect(action)
        self.groupe_navigation.addButton(bouton)
        return bouton

    def aller_au_tableau_de_bord(self):
        self.scroll_area.verticalScrollBar().setValue(0)

    def aller_aux_eleves(self):
        self.scroll_area.ensureWidgetVisible(self.table, 0, 20)
        self.table.setFocus()

    def ouvrir_dialog_echeances(self):
        from src.ui.echeance_dialog import EcheanceDialog

        EcheanceDialog(self).exec()

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
            ["Liste des élèves (filtre actif)", "Historique des paiements"],
            0,
            False,
        )
        if not valide:
            return
        nom = "eleves" if "élèves" in choix else "historique_paiements"
        chemin, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les données",
            nom,
            "CSV (*.csv);;Excel (*.xlsx)",
        )
        if not chemin:
            return
        try:
            if "élèves" in choix:
                # Récupérer les filtres actifs exactement comme charger_eleves()
                recherche = self.search_input.text()
                classe = self.combo_classe.currentText()
                statut = self.combo_statut.currentText()

                # Normaliser — exactement comme dans charger_eleves
                if classe == "Toutes les classes":
                    classe = ""
                if statut == "Tous":
                    statut = "Tous"

                eleves_filtres = EleveService.filtrer_eleves(recherche, classe, statut)

                # Construire le résumé des filtres pour le message
                filtres_actifs = []
                if recherche:
                    filtres_actifs.append(f"Recherche : « {recherche} »")
                if classe:
                    filtres_actifs.append(f"Classe : {classe}")
                if statut != "Tous":
                    filtres_actifs.append(f"Statut : {statut}")
                resume_filtres = " | ".join(filtres_actifs) if filtres_actifs else "Aucun filtre (tous les élèves)"

                resultat = ImportExportService.exporter_eleves(eleves_filtres, chemin)
                QMessageBox.information(
                    self, "Export terminé",
                    f"{len(eleves_filtres)} élève(s) exporté(s)\n"
                    f"Filtres : {resume_filtres}\n\n"
                    f"Fichier : {resultat}"
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
            for colonne, montant in ((5, eleve['montant_total_due']), (6, total_paye), (7, reste)):
                item_montant = QTableWidgetItem(f"{montant:,.0f}".replace(",", " "))
                item_montant.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_idx, colonne, item_montant)
            statut = EleveService.calculer_statut(eleve, reste)
            item_statut = QTableWidgetItem(statut)
            item_statut.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            couleurs_statut = {
                "Soldé": ("#e5f3ec", "#25684b"),
                "En retard": ("#fff0ed", "#a9473d"),
                "En cours": ("#edf4fa", "#315f86"),
            }
            fond, texte = couleurs_statut.get(statut, ("#f1f5f8", "#526273"))
            item_statut.setBackground(QColor(fond))
            item_statut.setForeground(QColor(texte))
            self.table.setItem(row_idx, 8, item_statut)

            btn_payer = QPushButton("Payer")
            if reste <= 0:
                btn_payer.setText("Soldé")
                btn_payer.setEnabled(False)
            else:
                btn_payer.clicked.connect(lambda _, e=eleve, r=reste: self.ouvrir_dialog_paiement(e, r))
            self.table.setCellWidget(row_idx, 9, btn_payer)

            btn_historique = QPushButton("Voir")
            btn_historique.clicked.connect(lambda _, e=eleve: self.ouvrir_dialog_historique(e))
            self.table.setCellWidget(row_idx, 10, btn_historique)

        self.mettre_a_jour_stats(total_encaisse_global, total_reste_global, len(eleves))
        self.actualiser_graphiques()
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

    def ouvrir_guide(self):
        GuideDialog(self).exec()

    def ouvrir_assistance(self):
        AssistanceDialog(self).exec()

    def creer_carte_stat(self, titre, valeur_initiale, couleur):
        frame = QFrame()
        frame.setObjectName("statCard")
        accent = {
            "#2e7d32": "green",
            "#c62828": "coral",
            "#1565c0": "blue",
        }.get(couleur, "teal")
        frame.setProperty("accent", accent)
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

    def creer_graphique_encaissements(self):
        self.chart_bar = QChart()
        self.chart_bar.setTitle("Encaissements des 6 derniers mois")
        self.chart_bar.setTitleFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        self.chart_bar.setTitleBrush(QColor("#214757"))
        self.chart_bar.setBackgroundBrush(QColor("#ffffff"))
        self.chart_bar.setBackgroundRoundness(7)
        self.chart_bar.setMargins(QMargins(14, 10, 14, 8))
        self.chart_bar.setPlotAreaBackgroundVisible(True)
        self.chart_bar.setPlotAreaBackgroundBrush(QColor("#fbfcfd"))
        self.chart_bar.legend().hide()
        self.series_bar = QBarSeries()
        self.bar_set = QBarSet("Montant encaissé")
        self.bar_set.setColor(QColor("#167d8d"))
        self.series_bar.append(self.bar_set)
        self.chart_bar.addSeries(self.series_bar)

        self.axis_mois = QBarCategoryAxis()
        self.axis_mois.setLabelsFont(QFont("Segoe UI", 9))
        self.axis_mois.setLabelsColor(QColor("#607382"))
        self.axis_mois.setGridLineColor(QColor("#e4eaee"))
        self.axis_mois.setLinePenColor(QColor("#cbd6dc"))
        self.chart_bar.addAxis(self.axis_mois, Qt.AlignmentFlag.AlignBottom)
        self.series_bar.attachAxis(self.axis_mois)
        self.axis_encaissement = QValueAxis()
        self.axis_encaissement.setLabelFormat("%.0f")
        self.axis_encaissement.setTitleText("FCFA")
        self.axis_encaissement.setTitleFont(QFont("Segoe UI", 8))
        self.axis_encaissement.setLabelsFont(QFont("Segoe UI", 8))
        self.axis_encaissement.setLabelsColor(QColor("#607382"))
        self.axis_encaissement.setGridLineColor(QColor("#e4eaee"))
        self.axis_encaissement.setLinePenColor(QColor("#cbd6dc"))
        self.axis_encaissement.setMin(0)
        self.chart_bar.addAxis(self.axis_encaissement, Qt.AlignmentFlag.AlignLeft)
        self.series_bar.attachAxis(self.axis_encaissement)

        view = QChartView(self.chart_bar)
        view.setObjectName("monthlyPaymentsChart")
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setMinimumHeight(235)
        return view

    def creer_graphique_repartition(self):
        self.chart_pie = QChart()
        self.chart_pie.setTitle("Situation des frais scolaires")
        self.chart_pie.setTitleFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        self.chart_pie.setTitleBrush(QColor("#214757"))
        self.chart_pie.setBackgroundBrush(QColor("#ffffff"))
        self.chart_pie.setBackgroundRoundness(7)
        self.chart_pie.setMargins(QMargins(14, 10, 14, 4))
        self.chart_pie.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.chart_pie.legend().setLabelColor(QColor("#526777"))
        self.chart_pie.legend().setFont(QFont("Segoe UI", 9))
        self.series_pie = QPieSeries()
        self.series_pie.setHoleSize(0.58)
        self.chart_pie.addSeries(self.series_pie)

        view = QChartView(self.chart_pie)
        view.setObjectName("tuitionDistributionChart")
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setMinimumHeight(235)
        return view

    def actualiser_graphiques(self, aujourd_hui=None):
        aujourd_hui = aujourd_hui or date.today()
        mois = []
        noms_mois = ("Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc")
        index_mois_courant = aujourd_hui.year * 12 + aujourd_hui.month - 1
        for decalage in reversed(range(6)):
            index = index_mois_courant - decalage
            annee, zero_mois = divmod(index, 12)
            numero_mois = zero_mois + 1
            mois.append((f"{annee:04d}-{numero_mois:02d}", f"{noms_mois[numero_mois - 1]} {annee % 100:02d}"))

        totaux = PaiementDAO.obtenir_encaissements_mensuels(mois[0][0], mois[-1][0])
        valeurs = [totaux.get(cle, 0.0) for cle, _ in mois]
        self.bar_set.remove(0, self.bar_set.count())
        self.bar_set.append(valeurs)
        self.axis_mois.clear()
        self.axis_mois.append([libelle for _, libelle in mois])
        maximum = max(valeurs, default=0)
        # Lire le max personnalisé depuis les paramètres
        params = ParametresDAO.obtenir_parametres()
        y_max_param = params.get("graphique_y_max")
        if y_max_param:
            try:
                maximum_axe = float(y_max_param)
            except (ValueError, TypeError):
                maximum_axe = None
        else:
            maximum_axe = None

        if maximum_axe is None:
            if maximum <= 0:
                maximum_axe = 100_000
            else:
                maximum_brut = maximum * 1.2
                magnitude = 10 ** math.floor(math.log10(maximum_brut))
                maximum_axe = math.ceil(maximum_brut / magnitude) * magnitude
        self.axis_encaissement.setRange(0, maximum_axe)
        self.axis_encaissement.setTickCount(5)

        repartition = PaiementDAO.obtenir_repartition_scolarite()
        self.series_pie.clear()
        total = repartition["total_du"]
        if total <= 0:
            aucune_dette = self.series_pie.append("Aucun frais inscrit", 1)
            aucune_dette.setColor(QColor("#d7dee8"))
        else:
            paye = self.series_pie.append("Payé", repartition["total_paye"])
            reste = self.series_pie.append("Restant", repartition["reste"])
            paye.setColor(QColor("#167d8d"))
            reste.setColor(QColor("#ee7865"))
            paye.setLabel(f"Payé · {repartition['total_paye']:,.0f} FCFA")
            reste.setLabel(f"Restant · {repartition['reste']:,.0f} FCFA")
            paye.setLabelVisible(False)
            reste.setLabelVisible(False)

    def verifier_mise_a_jour_mois(self, aujourd_hui=None):
        aujourd_hui = aujourd_hui or date.today()
        mois_local = aujourd_hui.strftime("%Y-%m")
        if mois_local != self._mois_graphique:
            self._mois_graphique = mois_local
            self.actualiser_graphiques(aujourd_hui)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    charger_police_systeme(app)
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