<div align="center">

<img src="src/assets/logo.png" alt="EDUPAIE Logo" width="120"/>

# EDUPAIE
### Logiciel de gestion des paiements scolaires

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![PySide6](https://img.shields.io/badge/PySide6-6.11.2-green?style=flat-square&logo=qt)
![SQLite](https://img.shields.io/badge/SQLite-Local-lightgrey?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/Licence-MIT-orange?style=flat-square)
![Status](https://img.shields.io/badge/Statut-En%20développement-yellow?style=flat-square)

*Application de bureau pour la gestion complète des paiements scolaires en FCFA*

### 📥 Télécharger la documentation complète

[![Documentation complète](https://img.shields.io/badge/📄_Télécharger-Documentation_Complète_EDUPAIE.docx-1a73e8?style=for-the-badge)](docs/EDUPAIE_Documentation_Complete.docx)

</div>

---

## 👤 À propos de l'auteur

<div align="center">

<img src="https://res.cloudinary.com/ohiqyayo/image/upload/v1788458405/7f37d8fb-3409-49fa-a05c-e5d4b9ce2e45.png" alt="Kossi Victoire AZONOUTSOU" width="150" style="border-radius: 50%;"/>

### **AZONOUTSOU Kossi Victoire**
*« Samuel »* — Étudiant en Développement Web & Mobile

</div>

Né le **7 mai 2006** à Lomé, Togo. Étudiant en développement web et mobile à l'**Académie Digitale Numérique (ADN) Golfe 1**, dans le cadre d'une formation certifiée **Simplon.co**. Motivé, curieux et engagé, il combine compétences numériques et techniques pour construire des solutions innovantes.

EDUPAIE répond à un besoin concret des établissements togolais : suivre la scolarité en FCFA, encaisser par les moyens de paiement utilisés localement (TMoney, Moov Money, espèces) et remettre un reçu fiable à chaque parent.

### 📋 Profil

| Rubrique | Détail |
|---|---|
| 🎓 **Formation** | Baccalauréat scientifique, série D – Lycée de Gbenyedzi, Lomé (2024-2025) |
| 💻 **Formation actuelle** | Développement web & mobile – Simplon.co / ADN Golfe 1 (en cours) |
| 🏆 **Certification 1** | Attestation « IA & création de produits » – Togo DataLab / TDEV Community (Nov. 2025) — Projet MEDIGENI |
| 🌱 **Certification 2** | Attestation « Agroécologie digitale » – Plateforme FAO (Nov. 2025) |
| 🛠️ **Compétences numériques** | HTML / CSS / JavaScript / React.js / Python / SQL / Git / Node.js / Laravel / PHP |
| 🔧 **Compétences techniques** | Frigoriste (montage, entretien, dépannage), Électricité, Plomberie |
| 🌍 **Langues** | Français (intermédiaire professionnel), Éwé (langue maternelle), Anglais (notions) |

### 📞 Contact

| | |
|---|---|
| 📱 Téléphone | +228 97 90 67 11 |
| 📧 Email | samuelazovic@gmail.com |
| 🐙 GitHub | [SAMVICdev](https://github.com/SAMVICdev) |
| 💼 LinkedIn | SAMVICdev |
| 🎵 TikTok | SAMVICdev |

---

## 📖 Table des matières

1. [Présentation du logiciel](#1-présentation-du-logiciel)
2. [Technologies utilisées](#2-technologies-utilisées)
3. [Architecture du projet](#3-architecture-du-projet)
4. [Base de données](#4-base-de-données)
5. [Installation et lancement](#5-installation-et-lancement)
6. [Guide des fonctionnalités](#6-guide-des-fonctionnalités)
   - [6.1 Connexion sécurisée](#61-connexion-sécurisée-et-récupération-daccès)
   - [6.2 Tableau de bord](#62-tableau-de-bord-et-liste-des-élèves)
   - [6.3 Recherche et filtres](#63-recherche-et-filtres)
   - [6.4 Inscription d'un élève](#64-inscription-dun-élève)
   - [6.5 Modification et suppression](#65-modification-et-suppression-dun-élève)
   - [6.6 Enregistrement d'un paiement](#66-enregistrement-dun-paiement)
   - [6.7 Reçu PDF](#67-reçu-de-paiement-pdf)
   - [6.8 Historique des paiements](#68-historique-des-paiements)
   - [6.9 Tarifs et échéances](#69-tarifs-par-classe-et-échéances-scolaires)
   - [6.10 Paramètres](#610-paramètres-de-létablissement)
   - [6.11 Import / Export](#611-import-et-export-des-données)
   - [6.12 Aide et guide](#612-aide-assistance-et-guide-utilisateur)
7. [Règles de gestion](#7-règles-de-gestion-et-contrôles)
8. [Perspectives d'évolution](#8-perspectives-dévolution)
9. [Description des fichiers](#9-description-des-fichiers)

---

## 1. Présentation du logiciel

### Contexte et objectif

**EDUPAIE** est une application de bureau destinée aux établissements scolaires pour gérer le paiement de la scolarité. Elle remplace le suivi sur cahier ou sur tableur par un outil unique, fiable et rapide : chaque élève a une scolarité à payer, chaque versement est enregistré, le reste à payer et le statut de l'élève sont calculés automatiquement et un reçu officiel est généré à chaque paiement.

> Tous les montants sont exprimés en **francs CFA (FCFA)**. Le logiciel fonctionne **hors ligne** sur un seul poste, sans serveur : toutes les données sont stockées dans un fichier local.

### Fonctionnalités principales

| # | Fonctionnalité | Description |
|---|---|---|
| 1 | 🔐 **Accès protégé** | Mot de passe au démarrage (optionnel), code de secours et assistance intégrée |
| 2 | 📊 **Tableau de bord** | Total encaissé, reste à recouvrer, graphiques des 6 derniers mois |
| 3 | 👨‍🎓 **Gestion des élèves** | Inscription, modification, suppression, matricule automatique |
| 4 | 💰 **Tarifs par classe** | Montant pré-rempli automatiquement selon la classe choisie |
| 5 | 📅 **Échéances et retards** | Date limite par classe ; élèves en retard repérés automatiquement |
| 6 | 💳 **Paiements** | Espèces, TMoney, Moov Money, Chèque, Virement |
| 7 | 🧾 **Reçus PDF** | Numérotation automatique REC-AAAA-NNNN, logo, signature |
| 8 | 🔍 **Recherche et filtres** | Par nom, classe et statut en temps réel |
| 9 | 📤 **Import / Export** | CSV et Excel pour les élèves et l'historique des paiements |
| 10 | ⚙️ **Paramètres** | Établissement, logo, signature, sécurité, graphique |

### Utilisateurs visés

Personnel administratif et comptable d'un établissement (secrétariat, économat, direction) qui encaisse les frais de scolarité et suit les impayés.

---

## 2. Technologies utilisées

| Domaine | Technologie | Rôle dans EDUPAIE |
|---|---|---|
| Langage | **Python 3** | Logique métier, accès aux données, interface |
| Interface graphique | **PySide6 6.11.2** (Qt) | Fenêtres, tableaux, formulaires, feuille de style |
| Graphiques | **PySide6 QtCharts** | Histogramme et graphique en anneau |
| Base de données | **SQLite** (sqlite3) | Stockage local des données |
| Reçus PDF | **fpdf2** | Génération des reçus (format A5 paysage) |
| Import / Export | **openpyxl 3.1.5**, csv | Lecture et écriture Excel et CSV |
| Images | **Pillow 12.3.0** | Gestion des images logo et signature |
| Impression Windows | **pywin32 310** | Envoi direct à l'imprimante par défaut |
| Sécurité | **hashlib** (PBKDF2-SHA256) | Mot de passe et code de secours chiffrés |
| Versionnement | **Git / GitHub** | Dépôt [SAMVICdev/edupaie](https://github.com/SAMVICdev/edupaie) |

---

## 3. Architecture du projet

Le code est organisé en **trois couches indépendantes**. Chaque couche ne parle qu'à la couche située juste en dessous.

```
┌──────────────────────────────────┐
│         Interface (UI)           │  src/ui/
│   Fenêtres, formulaires, style   │
└─────────────┬────────────────────┘
              │
┌─────────────▼────────────────────┐
│        Services (Métier)         │  src/services/
│  Validations, PDF, matricule...  │
└─────────────┬────────────────────┘
              │
┌─────────────▼────────────────────┐
│      Accès aux données (DAO)     │  src/database/
│     Requêtes SQL vers SQLite     │
└──────────────────────────────────┘
```

### Arborescence complète

```
edupaie/
├── README.md
├── requirements.txt
├── data/
│   ├── schema.sql              ← structure de la base
│   └── edupaie.db              ← base SQLite locale
└── src/
    ├── assets/
    │   └── logo.png            ← logo de l'écran de connexion
    ├── database/
    │   ├── connection.py       ← connexion, création et migrations
    │   ├── eleve_dao.py
    │   ├── paiement_dao.py
    │   ├── parametres_dao.py
    │   ├── tarif_dao.py
    │   └── echeance_dao.py
    ├── services/
    │   ├── eleve_service.py
    │   ├── paiement_service.py
    │   ├── pdf_service.py
    │   ├── securite_service.py
    │   ├── import_export_service.py
    │   └── export_service.py
    └── ui/
        ├── main_window.py      ← fenêtre principale + démarrage
        ├── style.qss           ← apparence de l'application
        ├── connexion_dialog.py
        ├── reinitialisation_dialog.py
        ├── code_recuperation_dialog.py
        ├── eleve_dialog.py
        ├── paiement_dialog.py
        ├── historique_dialog.py
        ├── tarifs_dialog.py
        ├── echeance_dialog.py
        ├── parametres_dialog.py
        ├── assistance_dialog.py
        └── guide_dialog.py
```

### Exemple de parcours : enregistrer un paiement

```
1. Clic sur « Payer »
        ↓
2. PaiementDialog  →  saisie montant, mode, date
        ↓
3. PaiementService →  validation, calcul reste, numéro reçu
        ↓
4. PaiementDAO     →  INSERT dans SQLite
        ↓
5. PDFService      →  génération reçu PDF
        ↓
6. MainWindow      →  tableau de bord mis à jour
```

---

## 4. Base de données

La base SQLite (`data/edupaie.db`) est créée et mise à jour automatiquement au démarrage. Elle comporte **5 tables**.

> **Calcul du reste à payer :** `reste = montant_total_due − somme des paiements` (jamais négatif). Un élève est **« Soldé »** quand son reste = 0.

### Table `eleves`

| Colonne | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Identifiant automatique |
| matricule | TEXT, unique | Ex. 2026-6EMEA-001 |
| nom, prenom | TEXT, obligatoires | Nom en majuscules |
| classe | TEXT | Ex. 6ème A, Tle D |
| annee_scolaire | TEXT | Ex. 2026-2027 |
| montant_total_due | REAL ≥ 0 | Frais de scolarité |
| created_at | DATETIME | Date d'inscription |

### Table `paiements`

| Colonne | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Identifiant |
| numero_recu | TEXT, unique | Ex. REC-2026-0001 |
| eleve_id | INTEGER (FK) | Cascade sur suppression |
| montant | REAL > 0 | Montant versé |
| date_paiement | DATE | Date du versement |
| mode_paiement | TEXT | Espèces / TMoney / Moov Money / Chèque / Virement |
| total_paye_apres | REAL | Total payé après ce versement |
| reste_apres | REAL | Reste après ce versement |

### Table `tarifs_classe`

| Colonne | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Identifiant |
| classe | TEXT, unique | Nom de la classe |
| montant | REAL ≥ 0 | Frais de scolarité de cette classe |

### Table `echeances`

| Colonne | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Identifiant |
| annee_scolaire | TEXT | Ex. 2026-2027 |
| classe | TEXT | Classe ou `*` pour toutes |
| date_echeance | DATE | Date limite de paiement |

### Table `parametres`

| Colonne | Description |
|---|---|
| nom_ecole, adresse, telephone, email | Identité de l'établissement (en-tête des reçus) |
| chemin_logo, chemin_signature | Images PNG/JPG |
| annee_scolaire | Année scolaire active |
| format_matricule | Modèle : `{annee}-{classe}-{numero:03d}` |
| graphique_y_max | Échelle max axe Y (vide = automatique) |
| support_email, support_telephone | Coordonnées assistance |
| password_salt, password_hash | Mot de passe chiffré (PBKDF2-SHA256) |
| recovery_salt, recovery_hash | Code de secours chiffré |

---

## 5. Installation et lancement

### Prérequis

- **Python 3.10** ou plus récent
- Les bibliothèques de `requirements.txt`
- Aucun serveur de base de données (SQLite intégré à Python)
- Pour l'impression directe : Windows avec `pywin32`

### Étapes d'installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/SAMVICdev/edupaie.git
cd edupaie

# 2. Créer et activer l'environnement virtuel
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer le logiciel
python -m src.ui.main_window
```

> **À savoir :** La base de données est créée automatiquement au premier lancement. Les reçus générés sont enregistrés dans le dossier `recus/`.

---

## 6. Guide des fonctionnalités

### 6.1 Connexion sécurisée et récupération d'accès

Si la protection est activée dans les paramètres, l'écran de connexion s'affiche à chaque démarrage.

- **Champ mot de passe** avec bouton 👁 pour afficher/masquer
- **Déverrouiller** : valide le mot de passe (touche Entrée possible)
- **Mot de passe oublié ?** : disponible si un code de secours a été créé
- **Aide / assistance** : ouvre les coordonnées du support

> **Sécurité :** Le mot de passe (8 caractères minimum) et le code de secours ne sont jamais stockés en clair — seule une empreinte **PBKDF2-SHA256** (310 000 itérations, sel aléatoire) est conservée.

---

### 6.2 Tableau de bord et liste des élèves

L'écran principal regroupe toutes les actions de l'application en 5 zones :

1. **Menu latéral** — Tableau de bord, Élèves, Paiement, Importer, Exporter, Échéances, Guide, Paramètres, Aide
2. **En-tête** — boutons `+ Nouvel Élève`, `Modifier`, `Supprimer`
3. **Filtres** — recherche, classe, statut
4. **3 cartes** — Total Encaissé, Reste à Recouvrer, Élèves Inscrits
5. **2 graphiques** — Encaissements 6 derniers mois + Répartition payé/restant

**Raccourcis clavier :**

| Raccourci | Action |
|---|---|
| `Ctrl+N` | Inscrire un nouvel élève |
| `Ctrl+P` | Payer l'élève sélectionné |
| `Ctrl+F` | Aller à la recherche |
| Double-clic | Modifier la fiche de l'élève |

---

### 6.3 Recherche et filtres

Les trois filtres se combinent et le tableau se met à jour **immédiatement**, sans bouton de validation.

| Statut | Signification |
|---|---|
| ✅ **Soldé** | Reste à payer = 0 |
| 🔵 **En cours** | Reste > 0, date limite non dépassée |
| 🔴 **En retard** | Reste > 0 et date limite dépassée |
| ⚪ **Non soldé** | Regroupe « En cours » et « En retard » |

---

### 6.4 Inscription d'un élève

Le bouton `+ Nouvel Élève` (ou `Ctrl+N`) ouvre le formulaire d'inscription.

| Champ | Comportement |
|---|---|
| Matricule | Généré automatiquement — modifiable manuellement |
| Nom | Converti automatiquement en MAJUSCULES |
| Classe | Liste modifiable — saisie libre possible |
| Année scolaire | Préremplie avec l'année en cours |
| Montant scolarité | **Rempli automatiquement** selon le tarif de la classe |

> **Exemple :** Inscrire KOUASSI Ablavi en 6ème B → matricule `2026-6EMEB-001` et montant `150 000 FCFA` apparaissent automatiquement si le tarif de la classe est défini.

---

### 6.5 Modification et suppression d'un élève

- **Modifier** (ou double-clic) : ouvre la fiche avec les valeurs actuelles. Le montant n'est pas écrasé en mode modification.
- **Supprimer** : demande une confirmation (supprime aussi tous les paiements de l'élève via CASCADE).

---

### 6.6 Enregistrement d'un paiement

Le bouton `Payer` (ou `Ctrl+P`) ouvre la fenêtre de paiement.

- **Montant** : prérempli avec le reste à payer, modifiable pour un paiement partiel
- **Mode** : Espèces, TMoney, Moov Money, Chèque, Virement
- **Date** : aujourd'hui par défaut, modifiable

> Quand le reste atteint 0, le bouton `Payer` devient `Soldé` et se désactive.

---

### 6.7 Reçu de paiement PDF

Chaque paiement génère automatiquement un reçu **PDF A5 paysage**.

Le reçu contient :
- Bandeau d'en-tête avec **logo**, nom, adresse, téléphone, email de l'établissement
- Mention `REÇU DE PAIEMENT`, date et numéro (REC-AAAA-NNNN)
- Montant versé, mode de paiement, nom, classe, matricule de l'élève
- Récapitulatif : somme due / somme payée / reste à payer
- Zone `Reçu par` et zone `Signature`

---

### 6.8 Historique des paiements

Le bouton `Voir` d'un élève liste tous ses versements avec :
- N° de reçu, date, montant, mode de paiement
- Bouton **📄 PDF** : régénère et ouvre le reçu
- Bouton **🖨 Impr.** : envoie directement à l'imprimante par défaut Windows

---

### 6.9 Tarifs par classe et échéances scolaires

**Tarifs par classe** — `Paramètres > Gérer les tarifs par classe`

Définir une fois les frais de chaque niveau. Les cellules se modifient par double-clic. Le montant s'applique automatiquement à l'inscription d'un nouvel élève.

**Échéances scolaires** — `Menu > Échéances scolaires`

Fixer une date limite par année et par classe (ou `*` pour toutes les classes). Une règle de classe précise prime sur la règle générale.

> **Exemple :** Date limite générale au 30/09/2026, exception Tle D au 15/12/2026 → les élèves de Terminale D restent « En cours » jusqu'au 15 décembre.

---

### 6.10 Paramètres de l'établissement

Fenêtre organisée en sections, avec boutons toujours visibles en bas (scrollable).

| Section | Contenu |
|---|---|
| Informations établissement | Nom, adresse, téléphone, email |
| Logo & Signature | Images PNG/JPG (bouton Parcourir…) |
| Graphique tableau de bord | Échelle max axe Y (vide = automatique) |
| Scolarité | Année scolaire, format matricule, tarifs, échéances |
| Assistance EDUPAIE | Emails et téléphone de support |
| Sécurité | Mot de passe (8 car. min) + code de secours |

---

### 6.11 Import et export des données

**Import** — bouton `Importer` du menu latéral

Lit un fichier CSV ou Excel et inscrit les élèves en masse.

Colonnes obligatoires : `Nom`, `Prénom`, `Classe`, `Année scolaire`, `Frais totaux`
Colonne facultative : `Matricule` (généré si absent)

**Export** — bouton `Exporter` du menu latéral

Deux rapports disponibles :
- **Liste des élèves** : matricule, nom, prénom, classe, année, frais
- **Historique des paiements** : matricule, nom, prénom, classe, reçu, date, montant, mode

Formats : **CSV** (séparateur `;`) ou **Excel** (en-tête figé, filtres, colonnes ajustées)

---

### 6.12 Aide, assistance et guide utilisateur

- **Fenêtre d'aide** : coordonnées support, bouton copier email, écrire par email, contacter sur WhatsApp
- **Guide utilisateur** : lecteur intégré du fichier `docs/guide-utilisateur.md`

---

## 7. Règles de gestion et contrôles

| Règle | Mise en œuvre |
|---|---|
| Nom, prénom et classe obligatoires | EleveService |
| Montant scolarité ≥ 0 | EleveService + CHECK SQL |
| Matricule unique, généré selon le format | EleveService + index UNIQUE SQL |
| Paiement > 0 | PaiementService + CHECK SQL |
| Paiement ≤ reste à payer | PaiementService + limite du champ |
| Mode de paiement dans la liste autorisée | Liste déroulante + PaiementService + CHECK SQL |
| Numéro de reçu unique et auto-incrémenté | PaiementService + UNIQUE SQL |
| Suppression élève = suppression paiements | Clé étrangère ON DELETE CASCADE |
| Reste = scolarité − total payé, jamais négatif | EleveService |
| Statut « En retard » si reste > 0 et date dépassée | EleveService + table echeances |
| Mot de passe ≥ 8 caractères, jamais en clair | SecuriteService (PBKDF2-SHA256) |
| Année scolaire au format AAAA-AAAA | EcheanceDialog |

---

## 8. Perspectives d'évolution

1. **Comptes utilisateurs et rôles** (administrateur, comptable)
2. **Sauvegarde automatique** de la base de données et restauration
3. **Échéancier par tranches** (plusieurs dates limites par élève)
4. **Statistiques avancées** par classe et par mode de paiement
5. **Envoi des reçus** par email ou WhatsApp aux parents
6. **Installateur Windows (.exe)** via PyInstaller pour déploiement sans Python

---

## 9. Description des fichiers

### Base de données (`src/database/`)

| Fichier | Rôle |
|---|---|
| `connection.py` | Connexion SQLite, création des tables et migrations |
| `eleve_dao.py` | Requêtes SQL sur les élèves, vérification unicité matricule |
| `paiement_dao.py` | Paiements, totaux, encaissements mensuels, répartition |
| `parametres_dao.py` | Paramètres établissement, sécurité, récupération |
| `tarif_dao.py` | Tarifs par classe (CRUD complet) |
| `echeance_dao.py` | Échéances par année scolaire et classe |

### Services (`src/services/`)

| Fichier | Rôle |
|---|---|
| `eleve_service.py` | Validation, génération matricule, calcul statut, filtrage |
| `paiement_service.py` | Validation paiements, numéro de reçu, enregistrement |
| `pdf_service.py` | Création, ouverture et impression du reçu PDF |
| `securite_service.py` | Mot de passe et code de secours (hachage PBKDF2) |
| `import_export_service.py` | Import élèves, export élèves et historique (CSV, XLSX) |

### Interface (`src/ui/`)

| Fichier | Rôle |
|---|---|
| `main_window.py` | Fenêtre principale, graphiques, filtres, point d'entrée |
| `style.qss` | Feuille de style de toute l'application |
| `connexion_dialog.py` | Écran de connexion sécurisé |
| `reinitialisation_dialog.py` | Récupération d'accès avec code de secours |
| `code_recuperation_dialog.py` | Affichage unique du code de secours |
| `eleve_dialog.py` | Inscription et modification d'un élève |
| `paiement_dialog.py` | Enregistrement d'un paiement |
| `historique_dialog.py` | Historique des paiements d'un élève |
| `tarifs_dialog.py` | Gestion des tarifs par classe |
| `echeance_dialog.py` | Gestion des échéances scolaires |
| `parametres_dialog.py` | Paramètres établissement et sécurité |
| `assistance_dialog.py` | Aide et contact de l'assistance |
| `guide_dialog.py` | Lecteur du guide utilisateur |

---

<div align="center">

---

**EDUPAIE** — Conçu et développé par **Kossi Victoire AZONOUTSOU** (Samuel)

Académie Digitale Numérique (ADN) Golfe 1 — Simplon.co — Lomé, Togo — Octobre 2026

📧 samuelazovic@gmail.com &nbsp;|&nbsp; 📱 +228 97 90 67 11 &nbsp;|&nbsp; 🐙 [SAMVICdev](https://github.com/SAMVICdev)

</div>
