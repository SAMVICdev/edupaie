import os
from fpdf import FPDF

class PDFService:

    @staticmethod
    def generer_recu(paiement_info, eleve_nom, eleve_prenom, classe):
        """
        Génère un fichier PDF pour un reçu de paiement.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)

        # En-tête de l'établissement
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.cell(0, 10, text="ÉTABLISSEMENT SCOLAIRE EDUPAIE", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 5, text="Reçu officiel de paiement de scolarité", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(10)

        # Informations du Reçu
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.cell(0, 8, text=f"Reçu N° : {paiement_info['numero_recu']}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        pdf.cell(0, 6, text=f"Élève : {eleve_nom} {eleve_prenom}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, text=f"Classe : {classe}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, text=f"Mode de règlement : {paiement_info.get('mode_paiement', 'Espèces')}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Détails financiers
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.cell(0, 8, text=f"Montant Versé : {paiement_info['montant']:,.0f} FCFA", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, text=f"Reste à Payer : {paiement_info['nouveau_reste']:,.0f} FCFA", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(15)

        # Pied de page / Signature
        pdf.set_font("Helvetica", style="I", size=10)
        pdf.cell(0, 6, text="Merci pour votre règlement.", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.cell(0, 6, text="La Direction", new_x="LMARGIN", new_y="NEXT", align="R")

        # Dossier de destination des reçus
        dossier_recus = os.path.join(os.getcwd(), "recus")
        os.makedirs(dossier_recus, exist_ok=True)

        nom_fichier = f"Recu_{paiement_info['numero_recu']}.pdf"
        chemin_pdf = os.path.join(dossier_recus, nom_fichier)

        pdf.output(chemin_pdf)
        return chemin_pdf