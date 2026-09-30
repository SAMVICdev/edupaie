import os
import re
import subprocess
import sys
from html import escape
from reportlab.lib.pagesizes import A6, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from src.database.parametres_dao import ParametresDAO

class PDFService:
    @staticmethod
    def _formater_montant(montant):
        return f"{float(montant):,.0f} FCFA"

    @staticmethod
    def generer_recu(paiement=None, eleve=None, chemin_sortie=None, **kwargs):
        """Génère un reçu PDF à partir d'un dict de paiement et d'un dict élève.

        Compatibilité :
        - PDFService.generer_recu(paiement_dict, eleve_dict)
        - PDFService.generer_recu(paiement_dict, {"nom": ..., "prenom": ..., "classe": ...})
        - PDFService.generer_recu(numero_recu=..., nom_eleve=..., prenom_eleve=..., classe=..., montant_paye=..., mode_paiement=...)
        """
        if isinstance(paiement, dict):
            numero_recu = paiement.get('numero_recu') or kwargs.get('numero_recu') or 'RECU'
            montant = paiement.get('montant', kwargs.get('montant_paye', 0))
            date_paiement = paiement.get('date_paiement') or kwargs.get('date_paiement') or ''
            mode_paiement = paiement.get('mode_paiement') or kwargs.get('mode_paiement') or ''
        else:
            numero_recu = kwargs.get('numero_recu') or 'RECU'
            montant = kwargs.get('montant_paye', 0)
            date_paiement = kwargs.get('date_paiement') or ''
            mode_paiement = kwargs.get('mode_paiement') or ''

        if isinstance(eleve, dict):
            nom_eleve = eleve.get('nom', kwargs.get('nom_eleve', ''))
            prenom_eleve = eleve.get('prenom', kwargs.get('prenom_eleve', ''))
            classe = eleve.get('classe', kwargs.get('classe', ''))
        else:
            nom_eleve = kwargs.get('nom_eleve', '') if eleve is None else str(eleve)
            prenom_eleve = kwargs.get('prenom_eleve', '')
            classe = kwargs.get('classe', '')

        if chemin_sortie is None:
            base_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'recu')
            identifiant = re.sub(r'[^A-Za-z0-9_-]+', '_', str(numero_recu))
            chemin_sortie = os.path.join(base_dir, f'{identifiant}.pdf')
        os.makedirs(os.path.dirname(os.path.abspath(chemin_sortie)), exist_ok=True)

        params = ParametresDAO.obtenir_parametres() or {}
        nom_ecole = params.get('nom_ecole', 'ÉTABLISSEMENT SCOLAIRE')
        adresse = params.get('adresse', '')
        telephone = params.get('telephone', '')
        email = params.get('email', '')
        logo_path = params.get('chemin_logo', '')
        signature_path = params.get('chemin_signature', '')

        doc = SimpleDocTemplate(
            chemin_sortie,
            pagesize=landscape(A6),
            rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20
        )
        elements = []
        styles = getSampleStyleSheet()

        style_titre = ParagraphStyle('Titre', parent=styles['Heading1'], fontSize=12, leading=14, textColor=colors.HexColor('#1E3A8A'))
        style_entete = ParagraphStyle('Entete', parent=styles['Normal'], fontSize=7, leading=9)

        col_logo = Image(logo_path, width=40, height=40) if logo_path and os.path.exists(logo_path) else Paragraph('<b>[LOGO]</b>', style_entete)
        texte_ecole = (
            f"<b>{escape(str(nom_ecole))}</b><br/>"
            f"{escape(str(adresse))}<br/>"
            f"Tél: {escape(str(telephone))} | Email: {escape(str(email))}"
        )
        col_info = Paragraph(texte_ecole, style_entete)

        table_entete = Table([[col_logo, col_info]], colWidths=[50, 300])
        table_entete.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
        ]))
        elements.append(table_entete)
        elements.append(Spacer(1, 10))

        elements.append(Paragraph(f"<b>REÇU DE PAIEMENT N° {escape(str(numero_recu))}</b>", style_titre))
        elements.append(Spacer(1, 8))

        data_details = [
            ['Élève :', escape(f'{nom_eleve} {prenom_eleve}'.strip())],
            ['Classe :', escape(str(classe))],
            ['Montant payé :', PDFService._formater_montant(montant)],
            ['Date :', escape(str(date_paiement))],
            ['Mode de règlement :', escape(str(mode_paiement))]
        ]

        t_details = Table(data_details, colWidths=[100, 250])
        t_details.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        elements.append(t_details)
        elements.append(Spacer(1, 10))

        if signature_path and os.path.exists(signature_path):
            img_sig = Image(signature_path, width=60, height=30)
            t_sig = Table([['', img_sig]], colWidths=[250, 100])
            elements.append(t_sig)

        doc.build(elements)
        return chemin_sortie

    @staticmethod
    def ouvrir_recu(chemin_pdf):
        if not os.path.isfile(chemin_pdf):
            raise FileNotFoundError(f"Reçu introuvable : {chemin_pdf}")
        if sys.platform == 'win32':
            os.startfile(os.path.abspath(chemin_pdf))
        else:
            subprocess.Popen(['xdg-open', chemin_pdf])

    @staticmethod
    def imprimer_recu(chemin_pdf):
        if not os.path.isfile(chemin_pdf):
            raise FileNotFoundError(f"Reçu introuvable : {chemin_pdf}")
        if sys.platform == 'win32':
            os.startfile(os.path.abspath(chemin_pdf), 'print')
        else:
            subprocess.Popen(['lp', chemin_pdf])