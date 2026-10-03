@echo off
cd /d C:\Users\ADN\Desktop\edupaie
set GIT_TERMINAL_PROMPT=0
echo === BRANCH ===
git branch
echo === STATUS ===
git status --short
echo === LOG ===
git log --oneline -6
echo === DONE ===
