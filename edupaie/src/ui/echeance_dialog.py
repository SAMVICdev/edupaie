import re
from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHeaderView,
)

from src.database.echeance_dao import EcheanceDAO
from src.database.eleve_dao import EleveDAO


class EcheanceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Échéances scolaires")
        self.resize(680, 500)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        annee_courante = date.today().year
        self.input_annee = QLineEdit(f"{annee_courante}-{annee_courante + 1}")
        self.input_classe = QComboBox()
        self.input_classe.setEditable(True)
        self.input_classe.addItem("Toutes les classes (*)", "*")
        for classe in sorted({
            eleve["classe"] for eleve in EleveDAO.obtenir_tous() if eleve.get("classe")
        }):
            self.input_classe.addItem(classe, classe)
        self.input_date = QDateEdit(QDate.currentDate())
        self.input_date.setCalendarPopup(True)
        self.input_date.setDisplayFormat("dd/MM/yyyy")

        form.addRow("Année scolaire :", self.input_annee)
        form.addRow("Classe :", self.input_classe)
        form.addRow("Date limite :", self.input_date)
        layout.addLayout(form)

        actions = QHBoxLayout()
        self.btn_enregistrer = QPushButton("Enregistrer l'échéance")
        self.btn_charger = QPushButton("Modifier la sélection")
        self.btn_supprimer = QPushButton("Supprimer la règle sélectionnée")
        actions.addWidget(self.btn_enregistrer)
        actions.addWidget(self.btn_charger)
        actions.addWidget(self.btn_supprimer)
        layout.addLayout(actions)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Année scolaire", "Classe", "Date limite"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.cellDoubleClicked.connect(self.charger_regle_selectionnee)
        layout.addWidget(self.table)

        self.btn_enregistrer.clicked.connect(self.enregistrer)
        self.btn_charger.clicked.connect(self.charger_regle_selectionnee)
        self.btn_supprimer.clicked.connect(self.supprimer)
        self.input_annee.returnPressed.connect(self.input_classe.setFocus)
        self.input_classe.lineEdit().returnPressed.connect(self.input_date.setFocus)
        self.input_date.lineEdit().returnPressed.connect(self.btn_enregistrer.click)
        self.input_annee.setFocus()
        self.charger_echeances()

    def _obtenir_classe(self):
        classe = self.input_classe.currentText().strip()
        if classe == "Toutes les classes (*)":
            return "*"
        return classe.strip()

    def charger_echeances(self):
        echeances = EcheanceDAO.obtenir_toutes()
        self.table.setRowCount(len(echeances))
        for index, echeance in enumerate(echeances):
            classe = "Toutes les classes (*)" if echeance["classe"] == "*" else echeance["classe"]
            valeurs = (echeance["annee_scolaire"], classe, echeance["date_echeance"])
            for colonne, valeur in enumerate(valeurs):
                self.table.setItem(index, colonne, QTableWidgetItem(valeur))

    def charger_regle_selectionnee(self, ligne=None, _colonne=None):
        if ligne is None:
            ligne = self.table.currentRow()
        if ligne < 0:
            return
        self.input_annee.setText(self.table.item(ligne, 0).text())
        classe = self.table.item(ligne, 1).text()
        if classe == "Toutes les classes (*)":
            self.input_classe.setCurrentIndex(0)
        else:
            self.input_classe.setCurrentText(classe)
        echeance = date.fromisoformat(self.table.item(ligne, 2).text())
        self.input_date.setDate(QDate(echeance.year, echeance.month, echeance.day))

    def enregistrer(self):
        annee = self.input_annee.text().strip()
        classe = self._obtenir_classe()
        try:
            if not re.fullmatch(r"\d{4}-\d{4}", annee):
                raise ValueError("L'année scolaire doit utiliser le format AAAA-AAAA.")
            debut, fin = (int(partie) for partie in annee.split("-"))
            if fin != debut + 1:
                raise ValueError("Les années doivent être consécutives.")
            if not classe:
                raise ValueError("Indiquez une classe ou choisissez toutes les classes.")
            date_echeance = self.input_date.date().toString("yyyy-MM-dd")
            EcheanceDAO.enregistrer(annee, classe, date_echeance)
        except ValueError as exc:
            QMessageBox.warning(self, "Échéance invalide", str(exc))
            return

        self.charger_echeances()
        QMessageBox.information(self, "Échéance enregistrée", "La date limite a été enregistrée.")

    def supprimer(self):
        ligne = self.table.currentRow()
        if ligne < 0:
            QMessageBox.information(self, "Échéances", "Sélectionnez une règle à supprimer.")
            return
        annee = self.table.item(ligne, 0).text()
        classe_affichee = self.table.item(ligne, 1).text()
        classe = "*" if classe_affichee == "Toutes les classes (*)" else classe_affichee
        confirmation = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Supprimer l'échéance {annee} / {classe_affichee} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return
        EcheanceDAO.supprimer(annee, classe)
        self.charger_echeances()
