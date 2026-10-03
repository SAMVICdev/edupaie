import os
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QWidget,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon

from src.services.securite_service import SecuriteService
from src.database.parametres_dao import ParametresDAO
from src.ui.assistance_dialog import AssistanceDialog


class ConnexionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EDUPAIE — Connexion")
        self.setModal(True)
        self.setFixedSize(420, 420)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint
        )

        # Fond sombre global
        self.setStyleSheet("""
            QDialog {
                background-color: #1a2535;
            }
            QWidget#loginCard {
                background-color: #1a2535;
            }
            QLabel#appName {
                color: #ffffff;
                font-size: 22px;
                font-weight: 700;
                letter-spacing: 2px;
            }
            QLabel#appSub {
                color: #8fa8b8;
                font-size: 12px;
            }
            QLabel#hint {
                color: #8fa8b8;
                font-size: 12px;
            }
            QLineEdit#passwordInput {
                background-color: #263445;
                color: #e8f0f5;
                border: none;
                border-bottom: 2px solid #3a4f62;
                border-radius: 0px;
                font-size: 16px;
                padding: 10px 44px 10px 14px;
                min-height: 44px;
            }
            QLineEdit#passwordInput:focus {
                border-bottom: 2px solid #4ecdc4;
            }
            QPushButton#toggleBtn {
                background: transparent;
                border: none;
                color: #6a8a9a;
                font-size: 18px;
                min-width: 36px;
                max-width: 36px;
                padding: 0;
            }
            QPushButton#toggleBtn:hover {
                color: #4ecdc4;
            }
            QPushButton#unlockBtn {
                background-color: #2ecc71;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 700;
                min-height: 46px;
                letter-spacing: 1px;
            }
            QPushButton#unlockBtn:hover {
                background-color: #27ae60;
            }
            QPushButton#unlockBtn:pressed {
                background-color: #1e8449;
            }
            QPushButton#linkBtn {
                background: transparent;
                border: none;
                color: #5dade2;
                font-size: 12px;
                text-decoration: underline;
                min-height: 28px;
            }
            QPushButton#linkBtn:hover {
                color: #85c1e9;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 32, 40, 28)
        root.setSpacing(0)

        # ── Logo ────────────────────────────────────────────────────
        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_charge = False

        # 1) Logo depuis les paramètres de l'école
        params = ParametresDAO.obtenir_parametres()
        chemin_logo = params.get("chemin_logo", "")
        if chemin_logo and os.path.isfile(chemin_logo):
            px = QPixmap(chemin_logo).scaled(
                100, 100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl.setPixmap(px)
            logo_charge = True

        # 2) Logo depuis src/assets/logo.png
        if not logo_charge:
            base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
            for candidat in (
                base / "src" / "assets" / "logo.png",
                base / "assets" / "logo.png",
                Path(__file__).resolve().parent / "assets" / "logo.png",
            ):
                if candidat.is_file():
                    px = QPixmap(str(candidat)).scaled(
                        100, 100,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    logo_lbl.setPixmap(px)
                    logo_charge = True
                    break

        # 3) Fallback : initiales stylisées
        if not logo_charge:
            logo_lbl.setText("💼")
            logo_lbl.setStyleSheet("font-size: 64px; color: #4ecdc4;")

        root.addWidget(logo_lbl)
        root.addSpacing(14)

        # ── Nom appli ───────────────────────────────────────────────
        nom = QLabel("EDUPAIE")
        nom.setObjectName("appName")
        nom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(nom)

        sub = QLabel("Gestion des Paiements Scolaires")
        sub.setObjectName("appSub")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(sub)
        root.addSpacing(28)

        # ── Champ mot de passe avec bouton œil ──────────────────────
        hint = QLabel("Saisissez votre mot de passe")
        hint.setObjectName("hint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hint)
        root.addSpacing(8)

        pwd_row = QHBoxLayout()
        pwd_row.setSpacing(0)
        self.input_mot_de_passe = QLineEdit()
        self.input_mot_de_passe.setObjectName("passwordInput")
        self.input_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_mot_de_passe.setPlaceholderText("••••••••")
        self.input_mot_de_passe.returnPressed.connect(self.verifier)

        self.btn_toggle = QPushButton("👁")
        self.btn_toggle.setObjectName("toggleBtn")
        self.btn_toggle.setCheckable(True)
        self.btn_toggle.toggled.connect(self._toggle_visibilite)

        pwd_row.addWidget(self.input_mot_de_passe)
        pwd_row.addWidget(self.btn_toggle)
        root.addLayout(pwd_row)
        root.addSpacing(20)

        # ── Bouton Déverrouiller ────────────────────────────────────
        self.btn_connexion = QPushButton("Déverrouiller")
        self.btn_connexion.setObjectName("unlockBtn")
        self.btn_connexion.clicked.connect(self.verifier)
        root.addWidget(self.btn_connexion)
        root.addSpacing(14)

        # ── Liens secondaires ───────────────────────────────────────
        liens = QHBoxLayout()
        self.btn_oublie = QPushButton("Mot de passe oublié ?")
        self.btn_oublie.setObjectName("linkBtn")
        self.btn_oublie.setEnabled(
            ParametresDAO.obtenir_identifiants_recuperation() is not None
        )
        self.btn_assistance = QPushButton("Aide / assistance")
        self.btn_assistance.setObjectName("linkBtn")
        self.btn_oublie.clicked.connect(self.ouvrir_recuperation)
        self.btn_assistance.clicked.connect(self.ouvrir_assistance)
        liens.addWidget(self.btn_oublie)
        liens.addStretch()
        liens.addWidget(self.btn_assistance)
        root.addLayout(liens)
        root.addStretch()

        self.input_mot_de_passe.setFocus()

    def _toggle_visibilite(self, visible):
        if visible:
            self.input_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle.setText("🙈")
        else:
            self.input_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle.setText("👁")

    def ouvrir_recuperation(self):
        from src.ui.reinitialisation_dialog import ReinitialisationDialog
        ReinitialisationDialog(self).exec()

    def ouvrir_assistance(self):
        AssistanceDialog(self).exec()

    def verifier(self):
        if SecuriteService.verifier_mot_de_passe(self.input_mot_de_passe.text()):
            self.accept()
            return
        self.input_mot_de_passe.clear()
        QMessageBox.warning(self, "Accès refusé", "Le mot de passe est incorrect.")
        self.input_mot_de_passe.setFocus()
