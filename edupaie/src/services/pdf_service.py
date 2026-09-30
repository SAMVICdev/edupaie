import os
from fpdf import FPDF
from src.database.parametres_dao import ParametresDAO

class PDFService:

    @staticmethod
    def generer_recu(paiement_info, eleve_nom, eleve_prenom, classe):
        # Récupération dynamique des paramètres depuis SQLite
        params = ParametresDAO.obtenir_parametres()

        pdf = FPDF()
        pdf.add_page()

        # Logo / Tampon s'il est configuré
        if params.get('chemin_logo') and os.path.exists(params['chemin_logo']):
            pdf.image(params['chemin_logo'], x=10, y=10, w=30)

        # En-tête dynamique
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.cell(0, 10, text=params['nom_ecole'], new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", size=9)
        pdf.cell(0, 5, text=f"Adresse : {params['adresse']} | Tél : {params['telephone']} | Email : {params['email']}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(10)

        # Corps du reçu
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.cell(0, 8, text=f"Reçu N° : {paiement_info['numero_recu']}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        pdf.cell(0, 6, text=f"Élève : {eleve_nom} {eleve_prenom} (Classe: {classe})", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, text=f"Mode de paiement : {paiement_info.get('mode_paiement', 'Espèces')}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        pdf.cell(0, 8, text=f"Montant Versé : {paiement_info['montant']:,.0f} FCFA", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, text=f"Reste à Payer : {paiement_info['nouveau_reste']:,.0f} FCFA", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        # Signature si elle existe
        if params.get('chemin_signature') and os.path.exists(params['chemin_signature']):
            pdf.image(params['chemin_signature'], x=150, y=pdf.get_y(), w=40)

        dossier_recus = os.path.join(os.getcwd(), "recus")
        os.makedirs(dossier_recus, exist_ok=True)
        chemin_pdf = os.path.join(dossier_recus, f"Recu_{paiement_info['numero_recu']}.pdf")
        pdf.output(chemin_pdf)
        return chemin_pdf