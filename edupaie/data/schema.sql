PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS eleves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    classe TEXT NOT NULL,
    annee_scolaire TEXT NOT NULL,
    montant_total_due REAL NOT NULL CHECK(montant_total_due >= 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS paiements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_recu TEXT UNIQUE NOT NULL,
    eleve_id INTEGER NOT NULL,
    montant REAL NOT NULL CHECK(montant > 0),
    date_paiement DATE NOT NULL,
    mode_paiement TEXT NOT NULL CHECK(mode_paiement IN ('Espèces', 'Chèque', 'Virement', 'Mobile Money')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (eleve_id) REFERENCES eleves(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS parametres (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    nom_ecole TEXT NOT NULL,
    adresse TEXT,
    telephone TEXT,
    email TEXT,
    chemin_logo TEXT,
    chemin_signature TEXT,
    annee_scolaire TEXT NOT NULL DEFAULT '2025-2026'
);

CREATE TABLE IF NOT EXISTS tarifs_classe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    classe TEXT NOT NULL UNIQUE,
    montant REAL NOT NULL CHECK(montant >= 0)
);

CREATE TABLE IF NOT EXISTS echeances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    annee_scolaire TEXT NOT NULL,
    classe TEXT NOT NULL,
    date_echeance DATE NOT NULL,
    UNIQUE(annee_scolaire, classe)
);

-- Insertion de la configuration par défaut de l'établissement
INSERT OR IGNORE INTO parametres (id, nom_ecole, adresse, telephone, email, chemin_logo, chemin_signature, annee_scolaire)
VALUES (1, 'Nom de l''Établissement', 'Adresse de l''école', '+228 00 00 00 00', 'contact@ecole.com', '', '', '2025-2026');