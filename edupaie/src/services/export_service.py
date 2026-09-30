import csv
import os
from datetime import datetime

from src.services.eleve_service import EleveService

try:
    from openpyxl import Workbook
except ImportError:  # pragma: no cover - dépendance optionnelle
    Workbook = None


class ExportService:
    @staticmethod
    def _build_rows(eleves):
        rows = []
        for eleve in eleves:
            details = EleveService.obtenir_eleve_par_id(eleve['id'])
            montant_du = float(eleve.get('montant_total_due', 0.0) or 0.0)
            total_paye = float(details.get('total_paye', 0.0)) if details else 0.0
            reste = float(details.get('reste_a_payer', max(0.0, montant_du - total_paye))) if details else max(0.0, montant_du - total_paye)

            rows.append({
                'id': eleve.get('id', ''),
                'nom': eleve.get('nom', ''),
                'prenom': eleve.get('prenom', ''),
                'classe': eleve.get('classe', ''),
                'annee_scolaire': eleve.get('annee_scolaire', ''),
                'montant_total_due': f"{montant_du:,.0f}",
                'total_paye': f"{total_paye:,.0f}",
                'reste_a_payer': f"{reste:,.0f}",
                'statut': 'Soldé' if reste <= 0 else 'Non soldé',
            })
        return rows

    @staticmethod
    def exporter_eleves(eleves=None, chemin=None, format_export='auto'):
        """Exporte la liste des élèves en CSV ou XLSX."""
        if eleves is None:
            eleves = EleveService.obtenir_tous_les_eleves()

        if not eleves:
            eleves = []

        if chemin is None:
            dossier = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'exports')
            os.makedirs(dossier, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            chemin = os.path.join(dossier, f'eleves_{timestamp}.csv')

        if format_export == 'auto':
            ext = os.path.splitext(chemin)[1].lower()
            if ext in ('.xlsx', '.xls'):
                format_export = 'xlsx'
            else:
                format_export = 'csv'

        rows = ExportService._build_rows(eleves)

        if format_export == 'xlsx':
            if Workbook is None:
                raise ImportError("La bibliothèque openpyxl est requise pour exporter au format XLSX.")
            dossier = os.path.dirname(chemin)
            if dossier and not os.path.exists(dossier):
                os.makedirs(dossier, exist_ok=True)
            wb = Workbook()
            ws = wb.active
            ws.title = 'Eleves'
            headers = ['ID', 'Nom', 'Prénom', 'Classe', 'Année scolaire', 'Montant total dû', 'Total payé', 'Reste à payer', 'Statut']
            ws.append(headers)
            for row in rows:
                ws.append([
                    row['id'],
                    row['nom'],
                    row['prenom'],
                    row['classe'],
                    row['annee_scolaire'],
                    row['montant_total_due'],
                    row['total_paye'],
                    row['reste_a_payer'],
                    row['statut'],
                ])
            if not chemin.lower().endswith('.xlsx'):
                chemin = f"{chemin}.xlsx"
            wb.save(chemin)
            return chemin

        # CSV par défaut
        if not chemin.lower().endswith('.csv'):
            chemin = f"{os.path.splitext(chemin)[0]}.csv"
        dossier = os.path.dirname(chemin)
        if dossier and not os.path.exists(dossier):
            os.makedirs(dossier, exist_ok=True)
        with open(chemin, 'w', newline='', encoding='utf-8') as fichier:
            writer = csv.DictWriter(
                fichier,
                fieldnames=['id', 'nom', 'prenom', 'classe', 'annee_scolaire', 'montant_total_due', 'total_paye', 'reste_a_payer', 'statut'],
            )
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return chemin
