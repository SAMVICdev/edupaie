from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)
from PySide6.QtCore import Qt


class CodeRecuperationDialog(QDialog):
    def __init__(self, code, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Conserver le code de secours")
        self.setFixedWidth(480)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Ce code ne sera pas réaffiché. Conservez-le hors de l'ordinateur "
            "pour pouvoir récupérer l'accès à EDUPAIE."
        ))

        self.input_code = QLineEdit(code)
        self.input_code.setReadOnly(True)
        self.input_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_code.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.input_code)

        self.btn_copier = QPushButton("Copier le code")
        self.btn_copier.clicked.connect(self.copier_code)
        layout.addWidget(self.btn_copier)

        self.checkbox_conserve = QCheckBox("J'ai conservé ce code dans un endroit sûr")
        self.checkbox_conserve.toggled.connect(self.actualiser_validation)
        layout.addWidget(self.checkbox_conserve)

        boutons = QHBoxLayout()
        self.btn_annuler = QPushButton("Annuler")
        self.btn_confirmer = QPushButton("Continuer")
        self.btn_confirmer.setEnabled(False)
        self.btn_annuler.clicked.connect(self.reject)
        self.btn_confirmer.clicked.connect(self.accept)
        boutons.addWidget(self.btn_annuler)
        boutons.addWidget(self.btn_confirmer)
        layout.addLayout(boutons)

    def copier_code(self):
        QApplication.clipboard().setText(self.input_code.text())
        QMessageBox.information(self, "Code copié", "Le code de secours a été copié.")

    def actualiser_validation(self, conserve):
        self.btn_confirmer.setEnabled(conserve)
