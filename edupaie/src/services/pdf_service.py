import os
import re
import subprocess
import sys
from datetime import date
from fpdf import FPDF
from src.database.parametres_dao import ParametresDAO

class PDFService:

    @staticmethod
    def generer_recu(paiement_info, eleve_nom, eleve_prenom, classe):
        params = ParametresDAO.obtenir_parametres()
        numero_recu = str(paiement_info.get("numero_recu", "RECU"))
        montant = float(paiement_info.get("montant", 0) or 0)
        total_du = float(paiement_info.get("total_du", montant + float(paiement_info.get("nouveau_reste", 0) or 0)))
        total_paye = float(paiement_info.get("total_paye_apres", montant) or 0)
        reste = float(paiement_info.get("reste_apres", paiement_info.get("nouveau_reste", 0)) or 0)
        date_brute = str(paiement_info.get("date_paiement") or date.today().isoformat())
        try:
            date_affichee = date.fromisoformat(date_brute[:10]).strftime("%d/%m/%Y")
        except ValueError:
            date_affichee = date_brute

        pdf = FPDF(orientation="L", unit="mm", format="A5")
        pdf.set_margins(12, 10, 12)
        pdf.set_auto_page_break(False)
        pdf.add_page()
        largeur = pdf.w

        petrol = (29, 105, 103)
        petrol_fonce = (23, 59, 74)
        orange = (232, 112, 34)
        gris = (91, 103, 112)
        ligne = (205, 215, 217)

        # Header and school identity.
        pdf.set_fill_color(*petrol_fonce)
        pdf.rect(0, 0, largeur, 34, style="F")
        logo = params.get("chemin_logo") or ""
        x_ecole = 13
        if logo and os.path.isfile(logo):
            pdf.image(logo, x=12, y=7, w=24, h=20, keep_aspect_ratio=True)
            x_ecole = 42
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(x_ecole, 8)
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(87, 8, str(params.get("nom_ecole") or "ÉTABLISSEMENT SCOLAIRE"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(x_ecole)
        pdf.set_font("Helvetica", size=8)
        pdf.cell(88, 5, str(params.get("adresse") or ""), new_x="LMARGIN", new_y="NEXT")

        x_contact = 134
        pdf.set_draw_color(*orange)
        pdf.set_line_width(0.8)
        pdf.line(128, 7, 128, 28)
        pdf.set_text_color(242, 247, 248)
        pdf.set_font("Helvetica", size=8)
        pdf.set_xy(x_contact, 8)
        pdf.multi_cell(64, 5, f"Tél : {params.get('telephone') or '—'}\nEmail : {params.get('email') or '—'}")

        # Orange receipt label, date and receipt identifier.
        pdf.set_fill_color(*orange)
        pdf.set_draw_color(*orange)
        pdf.rect((largeur - 66) / 2, 39, 66, 10, style="F")
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_xy((largeur - 66) / 2, 40)
        pdf.cell(66, 7, "REÇU DE PAIEMENT", align="C")

        pdf.set_text_color(*gris)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_xy(13, 42)
        pdf.cell(35, 5, f"DATE : {date_affichee}")
        pdf.set_text_color(34, 48, 57)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_xy(13, 54)
        pdf.cell(32, 7, "Reçu N° :")
        pdf.set_font("Helvetica", size=10)
        pdf.cell(150, 7, numero_recu, border="B")

        # Payment details and student identity.
        pdf.set_xy(13, 67)
        pdf.set_text_color(*gris)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(31, 7, "Montant versé :")
        pdf.set_text_color(*petrol)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(61, 7, f"{PDFService._formater_montant(montant)}", border="B")
        pdf.set_text_color(*gris)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(39, 7, "Mode de paiement :")
        pdf.set_text_color(34, 48, 57)
        pdf.set_font("Helvetica", size=9)
        pdf.cell(55, 7, str(paiement_info.get("mode_paiement") or "Espèces"), border="B")

        nom_complet = f"{eleve_nom} {eleve_prenom}".strip()
        matricule = paiement_info.get("matricule")
        classe_affichee = f"{classe} · {matricule}" if matricule else str(classe)
        pdf.set_xy(13, 79)
        pdf.set_text_color(*gris)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(20, 7, "Pour :")
        pdf.set_text_color(34, 48, 57)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(112, 7, nom_complet, border="B")
        pdf.set_text_color(*gris)
        pdf.set_font("Helvetica", size=8)
        pdf.cell(54, 7, classe_affichee, border="B", align="C")

        # Three-line balance summary, matching the supplied ticket layout.
        x_table, y_table, largeur_table, hauteur_ligne = 13, 91, largeur - 26, 8
        resume = (
            ("Somme due", total_du),
            ("Somme payée", total_paye),
            ("Reste à payer", reste),
        )
        for index, (libelle, valeur) in enumerate(resume):
            y = y_table + index * hauteur_ligne
            pdf.set_fill_color(246, 249, 249 if index % 2 == 0 else 255)
            pdf.set_draw_color(*petrol if index == 2 else ligne)
            pdf.set_line_width(0.45 if index < 2 else 0.8)
            pdf.rect(x_table, y, largeur_table, hauteur_ligne, style="DF")
            pdf.set_xy(x_table + 3, y + 1)
            pdf.set_text_color(*petrol_fonce if index == 2 else (48, 62, 70))
            pdf.set_font("Helvetica", "B" if index == 2 else "", 9)
            pdf.cell(105, 6, f"{libelle} :")
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(largeur_table - 111, 6, PDFService._formater_montant(valeur), align="R")

        # Issuer and signature area.
        y_signature = 124
        pdf.set_draw_color(*gris)
        pdf.set_line_width(0.4)
        pdf.line(18, y_signature, 70, y_signature)
        pdf.line(140, y_signature, 192, y_signature)
        pdf.set_xy(18, y_signature + 1)
        pdf.set_text_color(*gris)
        pdf.set_font("Helvetica", size=8)
        pdf.cell(52, 5, f"Reçu par : {str(params.get('nom_ecole') or '')[:24]}", align="C")
        signature = params.get("chemin_signature") or ""
        if signature and os.path.isfile(signature):
            pdf.image(signature, x=157, y=113, w=28, h=10, keep_aspect_ratio=True)
        pdf.set_xy(140, y_signature + 1)
        pdf.cell(52, 5, "Signature", align="C")

        # Small teal footer band for print identity.
        pdf.set_fill_color(*petrol)
        pdf.rect(0, pdf.h - 5, largeur, 5, style="F")

        dossier_recus = os.path.join(os.getcwd(), "recus")
        os.makedirs(dossier_recus, exist_ok=True)
        identifiant = re.sub(r"[^A-Za-z0-9_-]+", "_", numero_recu)
        chemin_pdf = os.path.join(dossier_recus, f"Recu_{identifiant}.pdf")
        pdf.output(chemin_pdf)
        return chemin_pdf

    @staticmethod
    def _formater_montant(montant):
        return f"{float(montant):,.0f}".replace(",", " ") + " FCFA"

    @staticmethod
    def ouvrir_recu(chemin_pdf):
        if not os.path.isfile(chemin_pdf):
            raise FileNotFoundError(f"Reçu introuvable : {chemin_pdf}")
        chemin_absolu = os.path.abspath(chemin_pdf)
        if sys.platform == "win32":
            os.startfile(chemin_absolu)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", chemin_absolu])
        else:
            subprocess.Popen(["xdg-open", chemin_absolu])

    @staticmethod
    def imprimer_recu(chemin_pdf):
        """Envoie le PDF à l'imprimante par défaut de l'ordinateur."""
        if not os.path.isfile(chemin_pdf):
            raise FileNotFoundError(f"Reçu introuvable : {chemin_pdf}")
        chemin_absolu = os.path.abspath(chemin_pdf)

        if sys.platform == "win32":
            # Méthode 1 : win32api — envoie directement au spouleur Windows
            try:
                import win32api
                import win32print
                imprimante = win32print.GetDefaultPrinter()
                win32api.ShellExecute(
                    0, "print", chemin_absolu, f'/d:"{imprimante}"', ".", 0
                )
                return
            except ImportError:
                pass
            except Exception:
                pass

            # Méthode 2 : ShellExecute via ctypes
            try:
                import ctypes
                ret = ctypes.windll.shell32.ShellExecuteW(
                    None, "print", chemin_absolu, None, None, 0
                )
                if ret > 32:
                    return
            except Exception:
                pass

            # Fallback : ouvrir le PDF, demander impression manuelle
            os.startfile(chemin_absolu)
            raise RuntimeError(
                "Le reçu a été ouvert dans votre lecteur PDF.\n"
                "Utilisez Ctrl+P pour lancer l'impression."
            )
        else:
            # Linux / macOS
            subprocess.Popen(["lp", chemin_absolu])