@echo off
cd /d C:\Users\ADN\Desktop\edupaie
set GIT_TERMINAL_PROMPT=0

echo === Branche actuelle ===
git branch --show-current

echo === Ajout des fichiers ===
git add src/database/tarif_dao.py
git add src/database/connection.py
git add src/database/parametres_dao.py
git add src/ui/tarifs_dialog.py
git add src/ui/parametres_dialog.py
git add src/ui/eleve_dialog.py
git add src/ui/main_window.py
git add data/schema.sql

echo === Commit ===
git commit -m "feat: tarifs par classe - table BDD, DAO, dialog, auto-remplissage, axe Y configurable"

echo === Push branche ===
git push -u origin fonction/12-tarifs-par-classe

echo === Switch main ===
git checkout main

echo === Merge ===
git merge fonction/12-tarifs-par-classe --no-edit -m "merge: integration tarifs par classe dans main"

echo === Push main ===
git push origin main

echo === FIN ===
