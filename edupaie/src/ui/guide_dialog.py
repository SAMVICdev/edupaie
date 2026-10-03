import sys
from pathlib import Path

from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QTextBrowser, QVBoxLayout


class GuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guide utilisateur EDUPAIE")
        self.resize(900, 720)

        layout = QVBoxLayout(self)
        self.lecteur = QTextBrowser()
        self.lecteur.setObjectName("userGuideView")
        self.lecteur.setOpenExternalLinks(True)
        layout.addWidget(self.lecteur)

        self.btn_fermer = QPushButton("Fermer")
        self.btn_fermer.clicked.connect(self.accept)
        layout.addWidget(self.btn_fermer)

        racine = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
        chemin_guide = racine / "docs" / "guide-utilisateur.md"
        if chemin_guide.is_file():
            self.lecteur.setMarkdown(chemin_guide.read_text(encoding="utf-8"))
        else:
            self.lecteur.setPlainText(
                "Le guide utilisateur n'est pas inclus dans cette installation. "
                "Consultez le fichier docs/guide-utilisateur.md du projet."
            )
