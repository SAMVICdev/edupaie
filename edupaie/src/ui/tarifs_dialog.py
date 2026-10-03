from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QLabel, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.database.tarif_dao import TarifDAO


class TarifsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tarifs par classe")
        self.setMinimumSize(480, 420)
        self.resize(520, 460)
        self.setStyleSheet("background-color: #f1f5f8;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # Titre
        titre = QLabel("Définir les frais scolaires par classe")
        titre.setStyleSheet("font-size: 14px; font-weight: 700; color: #173b4a; background: transparent;")
        layout.addWidget(titre)

        sous_titre = QLabel("Double-cliquez sur une cellule pour la modifier.")
        sous_titre.setStyleSheet("font-size: 11px; color: #6a8090; background: transparent;")
        layout.addWidget(sous_titre)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Classe / Niveau", "Montant (FCFA)"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(38)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)

        # Boutons d'action
        btn_row = QHBoxLayout()
        self.btn_ajouter = QPushButton("+ Ajouter une ligne")
        self.btn_ajouter.setObjectName("primaryAction")
        self.btn_ajouter.clicked.connect(self.ajouter_ligne)

        self.btn_supprimer = QPushButton("Supprimer la sélection")
        self.btn_supprimer.setObjectName("dangerAction")
        self.btn_supprimer.clicked.connect(self.supprimer_ligne)

        btn_row.addWidget(self.btn_ajouter)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_supprimer)
        layout.addLayout(btn_row)

        # Séparateur
        from PySide6.QtWidgets import QFrame
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #d6e0e5; max-height: 1px; border: none;")
        layout.addWidget(sep)

        # Boutons bas
        bas_row = QHBoxLayout()
        self.btn_enregistrer = QPushButton("Enregistrer")
        self.btn_enregistrer.setObjectName("primaryAction")
        self.btn_enregistrer.setMinimumHeight(38)
        self.btn_enregistrer.clicked.connect(self.enregistrer)

        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.setMinimumHeight(38)
        self.btn_annuler.clicked.connect(self.reject)

        bas_row.addStretch()
        bas_row.addWidget(self.btn_annuler)
        bas_row.addWidget(self.btn_enregistrer)
        layout.addLayout(bas_row)

        self.charger()

    def charger(self):
        """Charge les tarifs existants dans le tableau."""
        self.table.setRowCount(0)
        for tarif in TarifDAO.obtenir_tous():
            self._ajouter_ligne_tableau(tarif["classe"], tarif["montant"])

    def _ajouter_ligne_tableau(self, classe="", montant=""):
        row = self.table.rowCount()
        self.table.insertRow(row)
        item_classe = QTableWidgetItem(str(classe))
        item_classe.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item_montant = QTableWidgetItem(str(int(montant)) if montant != "" else "")
        item_montant.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 0, item_classe)
        self.table.setItem(row, 1, item_montant)

    def ajouter_ligne(self):
        self._ajouter_ligne_tableau("", "")
        # Mettre le focus sur la nouvelle ligne
        new_row = self.table.rowCount() - 1
        self.table.setCurrentCell(new_row, 0)
        self.table.editItem(self.table.item(new_row, 0))

    def supprimer_ligne(self):
        rows = sorted(
            set(idx.row() for idx in self.table.selectedIndexes()),
            reverse=True
        )
        if not rows:
            QMessageBox.information(self, "Sélection", "Sélectionnez une ligne à supprimer.")
            return
        for row in rows:
            classe_item = self.table.item(row, 0)
            if classe_item and classe_item.text().strip():
                TarifDAO.supprimer(classe_item.text().strip())
            self.table.removeRow(row)

    def enregistrer(self):
        """Valide et sauvegarde tous les tarifs du tableau."""
        erreurs = []
        classes_vues = set()

        for row in range(self.table.rowCount()):
            classe_item = self.table.item(row, 0)
            montant_item = self.table.item(row, 1)

            classe = classe_item.text().strip() if classe_item else ""
            montant_str = montant_item.text().strip() if montant_item else ""

            # Ignorer les lignes vides
            if not classe and not montant_str:
                continue

            if not classe:
                erreurs.append(f"Ligne {row + 1} : le nom de la classe est vide.")
                continue

            if classe.lower() in classes_vues:
                erreurs.append(f"Ligne {row + 1} : la classe « {classe} » est en double.")
                continue
            classes_vues.add(classe.lower())

            try:
                montant = float(montant_str.replace(" ", "").replace(",", "."))
                if montant < 0:
                    raise ValueError
            except ValueError:
                erreurs.append(f"Ligne {row + 1} — {classe} : montant invalide « {montant_str} ».")
                continue

            TarifDAO.enregistrer(classe, montant)

        if erreurs:
            QMessageBox.warning(
                self, "Erreurs de saisie",
                "Certaines lignes n'ont pas été enregistrées :\n\n" + "\n".join(erreurs)
            )
        else:
            QMessageBox.information(self, "Succès", "Tarifs enregistrés avec succès !")
            self.accept()
