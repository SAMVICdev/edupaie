from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton,
    QFileDialog, QHBoxLayout, QVBoxLayout, QMessageBox,
    QLabel, QCheckBox, QScrollArea, QWidget, QFrame,
    QSizePolicy
)
from PySide6.QtCore import Qt
from src.database.parametres_dao import ParametresDAO
from src.services.securite_service import SecuriteService


class ParametresDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres de l'Établissement")
        self.setMinimumWidth(560)
        self.resize(580, 680)

        # Layout principal : scroll + boutons fixes en bas
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Zone scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background-color: #f1f5f8; border: none; }")

        container = QWidget()
        container.setStyleSheet("background-color: #f1f5f8;")
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.form = QFormLayout(container)
        self.form.setContentsMargins(24, 20, 24, 16)
        self.form.setSpacing(10)
        self.form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        scroll.setWidget(container)
        main_layout.addWidget(scroll, 1)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #d6e0e5; max-height: 1px; border: none;")
        main_layout.addWidget(sep)

        # Boutons fixes en bas — toujours visibles
        btn_bar = QWidget()
        btn_bar.setStyleSheet("background-color: #edf1f4; border-top: 1px solid #d6e0e5;")
        btn_bar_layout = QHBoxLayout(btn_bar)
        btn_bar_layout.setContentsMargins(24, 10, 24, 10)
        self.btn_enregistrer = QPushButton("Enregistrer les modifications")
        self.btn_enregistrer.setObjectName("primaryAction")
        self.btn_enregistrer.setMinimumHeight(38)
        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.setMinimumHeight(38)
        btn_bar_layout.addStretch()
        btn_bar_layout.addWidget(self.btn_annuler)
        btn_bar_layout.addWidget(self.btn_enregistrer)
        main_layout.addWidget(btn_bar)

        # ── Champs du formulaire ──────────────────────────────────
        params = ParametresDAO.obtenir_parametres()

        # Infos école
        self._section("INFORMATIONS DE L'ÉTABLISSEMENT")
        self.input_nom = QLineEdit(params.get("nom_ecole", ""))
        self.input_adresse = QLineEdit(params.get("adresse", ""))
        self.input_telephone = QLineEdit(params.get("telephone", ""))
        self.input_email = QLineEdit(params.get("email", ""))
        self.form.addRow("Nom de l'école :", self.input_nom)
        self.form.addRow("Adresse :", self.input_adresse)
        self.form.addRow("Téléphone :", self.input_telephone)
        self.form.addRow("Email :", self.input_email)

        # Logo / Signature
        self._section("LOGO & SIGNATURE")
        self.input_logo = QLineEdit(params.get("chemin_logo", ""))
        self.btn_browse_logo = QPushButton("Parcourir…")
        self.btn_browse_logo.setFixedWidth(110)
        self.btn_browse_logo.clicked.connect(self.choisir_logo)
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.input_logo)
        logo_layout.addWidget(self.btn_browse_logo)

        self.input_signature = QLineEdit(params.get("chemin_signature", ""))
        self.btn_browse_signature = QPushButton("Parcourir…")
        self.btn_browse_signature.setFixedWidth(110)
        self.btn_browse_signature.clicked.connect(self.choisir_signature)
        sig_layout = QHBoxLayout()
        sig_layout.addWidget(self.input_signature)
        sig_layout.addWidget(self.btn_browse_signature)

        self.form.addRow("Tampon / Logo :", logo_layout)
        self.form.addRow("Signature :", sig_layout)

        # Scolarité
        self._section("SCOLARITÉ")
        self.input_annee_scolaire = QLineEdit(params.get("annee_scolaire", "2025-2026"))
        self.input_annee_scolaire.setPlaceholderText("ex: 2025-2026")
        self.input_format_matricule = QLineEdit(
            params.get("format_matricule", "{annee}-{classe}-{numero:03d}")
        )
        self.input_format_matricule.setPlaceholderText("{annee}-{classe}-{numero:03d}")
        self.btn_echeances = QPushButton("Gérer les échéances scolaires →")
        self.btn_echeances.clicked.connect(self.ouvrir_echeances)
        self.form.addRow("Année scolaire :", self.input_annee_scolaire)
        self.form.addRow("Format matricule :", self.input_format_matricule)
        self.form.addRow("", self.btn_echeances)

        # Assistance
        self._section("ASSISTANCE EDUPAIE")
        self.input_support_email = QLineEdit(params.get("support_email", ""))
        self.input_support_email.setPlaceholderText("email1@example.com,email2@example.com")
        self.input_support_telephone = QLineEdit(params.get("support_telephone", ""))
        self.input_support_telephone.setPlaceholderText("+228...")
        self.form.addRow("Courriel de support :", self.input_support_email)
        self.form.addRow("Téléphone de support :", self.input_support_telephone)

        # Sécurité
        self._section("SÉCURITÉ")
        self.protection_initiale = ParametresDAO.protection_active()
        self.recuperation_initiale = ParametresDAO.obtenir_identifiants_recuperation() is not None

        self.checkbox_securite = QCheckBox("Protéger l'application au démarrage")
        self.checkbox_securite.setChecked(self.protection_initiale)
        self.checkbox_securite.toggled.connect(self.actualiser_champs_securite)

        self.input_mot_de_passe_actuel = QLineEdit()
        self.input_mot_de_passe_actuel.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_mot_de_passe_actuel.setPlaceholderText("Requis pour modifier la sécurité")
        self.input_nouveau_mot_de_passe = QLineEdit()
        self.input_nouveau_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirmation_mot_de_passe = QLineEdit()
        self.input_confirmation_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)

        self.form.addRow("", self.checkbox_securite)
        self.form.addRow("Mot de passe actuel :", self.input_mot_de_passe_actuel)
        self.form.addRow("Nouveau mot de passe :", self.input_nouveau_mot_de_passe)
        self.form.addRow("Confirmer :", self.input_confirmation_mot_de_passe)

        self.actualiser_champs_securite()

        # Connexions boutons
        self.btn_enregistrer.clicked.connect(self.enregistrer)
        self.btn_annuler.clicked.connect(self.reject)
        self.input_nom.setFocus()

    def _section(self, titre):
        """Ajoute un titre de section dans le formulaire."""
        lbl = QLabel(titre)
        lbl.setStyleSheet(
            "color: #247f83; font-size: 11px; font-weight: 700; "
            "padding-top: 12px; padding-bottom: 2px; background: transparent;"
        )
        # Label vide pour aligner la colonne de gauche
        vide = QLabel("")
        vide.setStyleSheet("background: transparent;")
        self.form.addRow(vide, lbl)

    def actualiser_champs_securite(self):
        securite_active = self.checkbox_securite.isChecked()
        self.input_mot_de_passe_actuel.setEnabled(self.protection_initiale)
        self.input_nouveau_mot_de_passe.setEnabled(securite_active)
        self.input_confirmation_mot_de_passe.setEnabled(securite_active)

    def choisir_logo(self):
        f, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner une image", "", "Images (*.png *.jpg *.jpeg)"
        )
        if f:
            self.input_logo.setText(f)

    def choisir_signature(self):
        f, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner la signature", "", "Images (*.png *.jpg *.jpeg)"
        )
        if f:
            self.input_signature.setText(f)

    def ouvrir_echeances(self):
        from src.ui.echeance_dialog import EcheanceDialog
        EcheanceDialog(self).exec()

    def enregistrer(self):
        mot_de_passe_actuel = self.input_mot_de_passe_actuel.text()
        nouveau_mot_de_passe = self.input_nouveau_mot_de_passe.text()
        confirmation = self.input_confirmation_mot_de_passe.text()
        securite_demandee = self.checkbox_securite.isChecked()
        format_matricule = self.input_format_matricule.text().strip()

        if not all(token in format_matricule for token in ("{annee}", "{classe}", "{numero")):
            QMessageBox.warning(
                self,
                "Format matricule invalide",
                "Le format doit contenir {annee}, {classe} et {numero}.",
            )
            return
        try:
            format_matricule.format(annee="2026", classe="6E", numero=1)
        except (KeyError, ValueError, IndexError):
            QMessageBox.warning(
                self, "Format matricule invalide", "Vérifiez la syntaxe du format matricule."
            )
            return

        if self.protection_initiale and (
            not securite_demandee
            or nouveau_mot_de_passe
            or confirmation
            or not self.recuperation_initiale
        ):
            if not SecuriteService.verifier_mot_de_passe(mot_de_passe_actuel):
                QMessageBox.warning(self, "Sécurité", "Le mot de passe actuel est incorrect.")
                return

        if securite_demandee and (
            not self.protection_initiale or nouveau_mot_de_passe or confirmation
        ):
            try:
                SecuriteService.valider_mot_de_passe(nouveau_mot_de_passe)
            except ValueError as exc:
                QMessageBox.warning(self, "Sécurité", str(exc))
                return
            if nouveau_mot_de_passe != confirmation:
                QMessageBox.warning(
                    self, "Sécurité", "La confirmation du mot de passe ne correspond pas."
                )
                return

        definir_securite = securite_demandee and (
            not self.protection_initiale
            or bool(nouveau_mot_de_passe)
            or not self.recuperation_initiale
        )
        code_recuperation = None
        if definir_securite:
            from src.ui.code_recuperation_dialog import CodeRecuperationDialog
            code_recuperation = SecuriteService.generer_code_recuperation()
            confirmation_code = CodeRecuperationDialog(code_recuperation, self)
            if confirmation_code.exec() != QDialog.DialogCode.Accepted:
                return

        ParametresDAO.sauvegarder_parametres(
            self.input_nom.text().strip(),
            self.input_adresse.text().strip(),
            self.input_telephone.text().strip(),
            self.input_email.text().strip(),
            self.input_logo.text().strip(),
            self.input_signature.text().strip(),
            self.input_annee_scolaire.text().strip() or "2025-2026",
            format_matricule,
            self.input_support_email.text().strip(),
            self.input_support_telephone.text().strip(),
        )

        if definir_securite:
            mot_de_passe = nouveau_mot_de_passe or mot_de_passe_actuel
            SecuriteService.definir_mot_de_passe(mot_de_passe, code_recuperation)
        elif self.protection_initiale and not securite_demandee:
            ParametresDAO.supprimer_mot_de_passe()

        QMessageBox.information(self, "Succès", "Paramètres enregistrés avec succès !")
        self.accept()
