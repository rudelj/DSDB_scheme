@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Deploiement DSDB_scheme vers tnm.etsi.org/DSDB_scheme

echo ======================================================================
echo   DEPLOIEMENT DSDB SCHEME -> tnm.etsi.org/DSDB_scheme
echo ======================================================================
echo.

if not exist "viewer\index.html" (
    echo [INFO] Generation du viewer super-er-diagram...
    call super-er-diagram generate --from-json schema.json --out viewer
    if errorlevel 1 (
        echo [ERREUR] Echec de generation du viewer.
        pause
        exit /b 1
    )
)

set /p USER_NAME="Nom d'utilisateur SSH [Appuyez sur Entree pour 'admjjr'] : "
if "%USER_NAME%"=="" set "USER_NAME=admjjr"

set /p SSH_PASS="Mot de passe SSH pour %USER_NAME%@tnm.etsi.org : "
if "%SSH_PASS%"=="" (
    echo [ERREUR] Aucun mot de passe saisi.
    pause
    exit /b 1
)

echo.
echo [1/4] Preparation du repertoire distant sur tnm.etsi.org (Port 29419)...
plink -P 29419 -l %USER_NAME% -pw "%SSH_PASS%" -batch tnm.etsi.org "rm -rf /tmp/dsdb-scheme-dist && mkdir -p /tmp/dsdb-scheme-dist"
if errorlevel 1 (
    echo [AVERTISSEMENT] Port 29419 indisponible, tentative sur le port standard 22...
    set "PORT=22"
    plink -P 22 -l %USER_NAME% -pw "%SSH_PASS%" -batch tnm.etsi.org "rm -rf /tmp/dsdb-scheme-dist && mkdir -p /tmp/dsdb-scheme-dist"
    if errorlevel 1 (
        echo [ERREUR] Connexion SSH echouee avec %USER_NAME%. Verifiez le mot de passe.
        pause
        exit /b 1
    )
) else (
    set "PORT=29419"
)

echo.
echo [2/4] Transfert des fichiers du viewer vers le serveur via pscp...
pscp -P %PORT% -l %USER_NAME% -pw "%SSH_PASS%" -r "viewer\*" tnm.etsi.org:/tmp/dsdb-scheme-dist/
if errorlevel 1 (
    echo [ERREUR] Echec du transfert de fichiers via pscp.
    pause
    exit /b 1
)

echo.
echo [3/4] Deploiement dans /var/www/html/DSDB_scheme et configuration Nginx...
plink -P %PORT% -l %USER_NAME% -pw "%SSH_PASS%" -batch tnm.etsi.org "echo '%SSH_PASS%' | sudo -S bash -c 'mkdir -p /var/www/html/DSDB_scheme && rm -rf /var/www/html/DSDB_scheme/* && cp -r /tmp/dsdb-scheme-dist/* /var/www/html/DSDB_scheme/ && chmod -R 755 /var/www/html/DSDB_scheme && chown -R www-data:www-data /var/www/html/DSDB_scheme 2>/dev/null; cat <<EOF > /etc/nginx/locations.d/tnm.DSDB_scheme.location
location /DSDB_scheme {
    alias /var/www/html/DSDB_scheme;
    try_files \$uri \$uri/ /DSDB_scheme/index.html;
}
EOF
nginx -t && systemctl reload nginx; rm -rf /tmp/dsdb-scheme-dist'"

echo.
echo [4/4] Verification de l'URL publique...
curl -k -I https://tnm.etsi.org/DSDB_scheme/

echo.
echo ======================================================================
echo  SUCCES : Le modele DSDB est en ligne sur https://tnm.etsi.org/DSDB_scheme/ !
echo ======================================================================
echo.
pause
