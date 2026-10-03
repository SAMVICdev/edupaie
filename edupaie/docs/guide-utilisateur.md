# Guide utilisateur EDUPAIE

EDUPAIE sert à gérer les inscriptions, les frais scolaires et les versements des élèves. Ce guide décrit les opérations disponibles dans l’application de bureau.

## Démarrer l’application

Ouvrez EDUPAIE depuis son raccourci ou, depuis le dossier du projet, lancez `python -m src.ui.main_window`. Si la protection est activée dans les paramètres, saisissez le mot de passe pour accéder au tableau de bord.

La base de données locale se trouve dans `data/edupaie.db`. Fermez l’application avant de copier ce fichier pour en faire une sauvegarde. Le mot de passe protège l’ouverture de l’application, mais ne chiffre pas ce fichier.

## Tableau de bord

La barre latérale donne accès au tableau de bord, aux élèves, aux paiements, à l’import/export, aux échéances, aux paramètres et à l’aide.

Les indicateurs affichent le total encaissé, le reste à recouvrer et le nombre d’élèves correspondant aux filtres actifs. Le graphique en barres présente les encaissements des six derniers mois selon la date locale; il se rafraîchit au changement de mois. Le graphique en anneau compare les frais payés et restants. Un trop-perçu n’augmente pas le montant payé au-delà des frais dus.

La liste affiche le matricule, l’identité, la classe, les frais, le total versé, le reste et le statut. Les montants sont en FCFA. Le statut est `Soldé` lorsque le reste est nul, `En cours` avant l’échéance ou sans échéance configurée, et `En retard` après l’échéance configurée.

La recherche filtre par nom et prénom. Les listes `Classe` et `Statut` permettent de préciser le résultat.

## Élèves

### Inscrire un élève

1. Choisissez `+ Nouvel Élève`.
2. Vérifiez le matricule proposé; il est généré à partir de l’année scolaire et de la classe.
3. Renseignez le nom, le prénom, la classe, l’année scolaire et les frais totaux.
4. Validez avec `Inscrire`.

Le nom est automatiquement converti en majuscules. Les classes déjà utilisées sont proposées, mais une nouvelle classe peut être saisie. Un matricule déjà utilisé est signalé et refusé à l’enregistrement.

### Modifier ou supprimer

Sélectionnez une ligne, puis utilisez `Modifier` ou double-cliquez sur la ligne pour modifier la fiche. `Supprimer` demande confirmation et supprime également les paiements associés à l’élève.

### Matricules

Dans `Paramètres`, le format est personnalisable avec les champs `{annee}`, `{classe}` et `{numero}`. Par exemple, `{annee}-{classe}-{numero:03d}` produit `2026-6EME-001`. Les doublons ne sont pas autorisés.

## Paiements et reçus

Sélectionnez `Payer` sur la ligne d’un élève ou sélectionnez l’élève et utilisez `Ctrl+P`. Le formulaire propose le reste exact à payer, la date du jour et les modes `Espèces`, `TMoney`, `Moov Money`, `Chèque` et `Virement`. Vous pouvez modifier la date ou le montant, sans dépasser le solde.

Après validation, EDUPAIE enregistre le versement et génère automatiquement un reçu PDF A5 paysage dans le dossier `recus`. Le reçu indique l’établissement, la date, le numéro, l’élève, le montant, le mode de paiement et le récapitulatif des frais dus, payés et restants. Le logo et la signature configurés sont ajoutés s’ils existent.

`Voir` ouvre l’historique des versements. Les boutons `Ouvrir PDF` et `Imprimer` permettent de consulter ou réimprimer un reçu. L’ouverture et l’impression utilisent les applications et imprimantes configurées sur l’ordinateur.

## Échéances scolaires

Ouvrez `Échéances scolaires` dans la barre latérale. Enregistrez une date limite au format année scolaire `AAAA-AAAA` pour une classe précise, ou choisissez `Toutes les classes (*)` pour définir la date générale de l’année.

Une échéance de classe prend priorité sur l’échéance générale. Pour changer une règle, sélectionnez-la dans le tableau, choisissez `Modifier la sélection`, ajustez la date et enregistrez. La suppression d’une règle de classe fait réapparaître l’échéance générale, si elle existe.

Sans échéance correspondant à l’année et à la classe, un élève non soldé reste au statut `En cours`.

## Importer des élèves

Choisissez `Importer` dans la barre latérale et sélectionnez un fichier CSV ou Excel (`.xlsx`). Pour l’Excel, EDUPAIE lit la première feuille. Le fichier doit contenir les colonnes suivantes :

- `Nom`
- `Prénom`
- `Classe` (ou `Niveau`)
- `Année scolaire` (ou `Année`)
- `Frais totaux` (ou `Montant total dû`, `Scolarité`)

La colonne `Matricule` est facultative. Si elle est absente ou vide, EDUPAIE génère un matricule. Les fichiers CSV avec séparateur virgule, point-virgule ou tabulation sont pris en charge.

À la fin de l’import, le nombre de lignes importées et les erreurs par ligne sont affichés. Les lignes valides sont enregistrées même si d’autres lignes contiennent des erreurs; corrigez uniquement les lignes signalées avant de les réimporter. Les matricules en doublon sont refusés.

## Exporter des rapports

Choisissez `Exporter`, puis `Liste des élèves` ou `Historique des paiements`. Enregistrez le rapport en CSV (`.csv`) ou Excel (`.xlsx`). L’export de la liste contient les matricules, noms, classes, années et frais totaux. L’historique inclut l’élève, le numéro de reçu, la date, le montant et le mode de paiement.

## Paramètres de l’établissement

Dans `Paramètres`, vous pouvez définir le nom, l’adresse, le téléphone, l’adresse e-mail, le format des matricules et les coordonnées d’assistance. Les champs `Tampon / Logo` et `Signature` acceptent les images PNG ou JPEG; ces images apparaissent sur les reçus.

Le bouton `Gérer les échéances scolaires` ouvre la configuration des dates limites décrite plus haut.

## Sécurité et mot de passe oublié

Cochez `Protéger l’application au démarrage`, définissez un mot de passe d’au moins 8 caractères et confirmez-le. Le mot de passe est stocké sous forme d’empreinte, pas en clair.

EDUPAIE affiche alors un code de secours. Conservez-le hors de l’ordinateur : il ne sera pas réaffiché. Depuis l’écran de connexion, `Mot de passe oublié` permet de saisir ce code et de définir un nouveau mot de passe. La récupération émet un nouveau code et invalide l’ancien. Si vous perdez le code de secours, contactez l’assistance configurée dans l’application.

Le verrouillage par mot de passe ne chiffre pas la base SQLite; protégez également l’accès au compte Windows et sauvegardez la base dans un emplacement sûr.

## Aide et raccourcis

`Aide / assistance` affiche les courriels et le numéro WhatsApp configurés. `Écrire à l’assistance` ouvre le client de messagerie s’il est disponible; sinon, les destinataires et le texte du message sont copiés afin de pouvoir les coller dans votre messagerie. N’envoyez jamais votre mot de passe ni votre code de secours.

- `Ctrl+N` : inscrire un élève.
- `Ctrl+P` : enregistrer un paiement pour l’élève sélectionné.
- `Ctrl+F` : placer le curseur dans la recherche.
- `Tab` / `Entrée` : passer aux champs suivants dans les formulaires.
- `Échap` : fermer ou annuler une fenêtre de dialogue.
