@echo off
title Visualiseur de Modele de Donnees DSDB (super-er-diagram)
cd /d "%~dp0\viewer"
echo =====================================================================
echo  Lancement du Visualiseur Interactif super-er-diagram pour DSDB
echo =====================================================================
echo  - 208 Tables
echo  - 128 Relations Clés Etrangeres
echo  - 7 Domaines Metier
echo.
echo Ouverture dans votre navigateur par defaut...
start "" "index.html"
echo.
echo Si votre navigateur restreint les scripts locaux (CORS pour data.js),
echo un serveur local temporaire est egalement demarrable via :
echo    python -m http.server 8085
echo.
pause
