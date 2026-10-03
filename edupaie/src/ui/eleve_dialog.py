from datetime import date

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
)
from src.database.eleve_dao import EleveDAO
from src.services.eleve_service import EleveService

class EleveDialog(QDialog):
    def __init__(self, parent=None, eleve=None):
        super().__init__(parent)
        self.eleve = eleve
        self._matricule_manuel = eleve is not None
        self.setWindowTitle("Modifier un Élève" if eleve else "Inscrire un Élève")
        self.resize(430, 330)

        self.layout = QFormLayout(self)
        self.input_matricule = QLineEdit(eleve.get("matricule", "") if eleve else "")
        self.input_nom = QLineEdit(eleve.get("nom", "") if eleve else "")
        self.input_prenom = QLineEdit(eleve.get("prenom", "") if eleve else "")
        self.input_classe = QComboBox()
        self.input_classe.setEditable(True)
        self.input_classe.addItems(sorted({item["classe"] for item in EleveDAO.obtenir_tous() if item.get("classe")}))
        if eleve:
            self.input_classe.setCurrentText(eleve.get("classe", ""))
        self.input_annee = QLineEdit(eleve.get("annee_scolaire", f"{date.today().year}-{date.today().year + 1}") if eleve else f"{date.today().year}-{date.today().year + 1}")
        
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 10000000)
        self.input_montant.setSingleStep(5000)
        self.input_montant.setValue(eleve.get("montant_total_due", 100000) if eleve else 100000)

        self.layout.addRow("Matricule :", self.input_matricule)
        self.layout.addRow("Nom :", self.input_nom)
        self.layout.addRow("Prénom :", self.input_prenom)
        self.layout.addRow("Classe :", self.input_classe)
        self.layout.addRow("Année Scolaire :", self.input_annee)
        self.layout.addRow("Montant Scolarité (FCFA) :", self.input_montant)

        btn_layout = QHBoxLayout()
        self.btn_valider = QPushButton("Enregistrer les modifications" if eleve else "Inscrire")
        self.btn_annuler = QPushButton("Annuler")
        
        btn_layout.addWidget(self.btn_valider)
        btn_layout.addWidget(self.btn_annuler)
        self.layout.addRow(btn_layout)

        self.btn_valider.clicked.connect(self.enregistrer)
        self.btn_annuler.clicked.connect(self.reject)
        self.input_nom.textChanged.connect(self.mettre_nom_en_majuscules)
        self.input_matricule.textEdited.connect(self.definir_matricule_manuel)
        self.input_matricule.textChanged.connect(self.verifier_doublon_matricule)
        self.input_matricule.editingFinished.connect(
            lambda: self.verifier_doublon_matricule(self.input_matricule.text())
        )
        self.input_classe.currentTextChanged.connect(self.actualiser_matricule)
        self.input_annee.textChanged.connect(self.actualiser_matricule)

        if not eleve:
            self.actualiser_matricule()
        self.input_matricule.setFocus()
        self._lier_entree_au_champ_suivant()

    def _lier_entree_au_champ_suivant(self):
        champs = [
            self.input_matricule,
            self.input_nom,
            self.input_prenom,
            self.input_classe.lineEdit(),
            self.input_annee,
        ]
        for champ in champs:
            champ.returnPressed.connect(self.focusNextChild)
        self.input_montant.lineEdit().returnPressed.connect(self.btn_valider.click)

    def definir_matricule_manuel(self, _texte):
        self._matricule_manuel = True

    def actualiser_matricule(self, _texte=""):
        if self._matricule_manuel:
            return
        classe = self.input_classe.currentText().strip()
        if not classe:
            self.input_matricule.clear()
            return
        matricule = EleveService.generer_matricule(classe, self.input_annee.text().strip())
        self.input_matricule.setText(matricule)

    def verifier_doublon_matricule(self, matricule):
        eleve_id = self.eleve.get("id") if self.eleve else None
        existe = bool(matricule.strip()) and EleveDAO.matricule_existe(matricule.strip(), eleve_id)
        self.input_matricule.setStyleSheet("border: 2px solid #c62828;" if existe else "")
        self.input_matricule.setToolTip("Ce matricule est déjà utilisé." if existe else "Matricule unique")

    def mettre_nom_en_majuscules(self, nom):
        nom_majuscule = nom.upper()
        if nom != nom_majuscule:
            position = self.input_nom.cursorPosition()
            self.input_nom.blockSignals(True)
            self.input_nom.setText(nom_majuscule)
            self.input_nom.setCursorPosition(position)
            self.input_nom.blockSignals(False)

    def enregistrer(self):
        nom = self.input_nom.text().strip()
        prenom = self.input_prenom.text().strip()
        classe = self.input_classe.text().strip()
        annee = self.input_annee.text().strip()
        montant = self.input_montant.value()
        matricule = self.input_matricule.text().strip().upper()

        try:
            if self.eleve:
                EleveService.modifier_eleve(
                    self.eleve["id"], nom, prenom, classe, annee, montant, matricule
                )
                message = f"La fiche de {nom} {prenom} a été mise à jour."
            else:
                EleveService.inscrire_eleve(nom, prenom, classe, annee, montant, matricule)
                message = f"L'élève {nom} {prenom} a été inscrit avec succès !"
            QMessageBox.information(self, "Succès", message)
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erreur de Saisie", str(e))