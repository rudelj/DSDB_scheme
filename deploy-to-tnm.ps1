[CmdletBinding()]
param(
    [string]$Server = "tnm.etsi.org",
    [int]$Port = 29419,
    [string]$User = "admjjr",
    [string]$Password = "",
    [string]$DestPath = "/var/www/html/DSDB_scheme"
)

$DistDir = Join-Path $PSScriptRoot "viewer"
$RemoteTemp = "/tmp/dsdb-scheme-dist"

if (-not (Test-Path (Join-Path $DistDir "index.html"))) {
    Write-Host "Le viewer n'existe pas. Generation en cours..." -ForegroundColor Yellow
    Set-Location $PSScriptRoot
    super-er-diagram generate --from-json schema.json --out viewer
}

if ([string]::IsNullOrWhiteSpace($Password)) {
    $secPass = Read-Host "Mot de passe pour $User@$Server" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secPass)
    $Password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
}

Write-Host "==> [1/3] Nettoyage et preparation distante sur $Server (Port $Port)..." -ForegroundColor Cyan
& plink -P $Port -l $User -pw $Password -batch $Server "rm -rf $RemoteTemp && mkdir -p $RemoteTemp"

Write-Host "==> [2/3] Transfert direct via pscp vers $RemoteTemp..." -ForegroundColor Cyan
& pscp -P $Port -l $User -pw $Password -r "$DistDir\*" "${Server}:${RemoteTemp}/"

Write-Host "==> [3/3] Installation vers $DestPath et configuration Nginx..." -ForegroundColor Cyan
$remoteCmd = @"
echo '$Password' | sudo -S bash -c 'mkdir -p $DestPath && rm -rf $DestPath/* && cp -r $RemoteTemp/* $DestPath/ && chmod -R 755 $DestPath && chown -R www-data:www-data $DestPath 2>/dev/null; cat <<EOF > /etc/nginx/locations.d/tnm.DSDB_scheme.location
location /DSDB_scheme {
    alias $DestPath;
    try_files \$uri \$uri/ /DSDB_scheme/index.html;
}
EOF
nginx -t && systemctl reload nginx; rm -rf $RemoteTemp'
"@

& plink -P $Port -l $User -pw $Password -batch $Server $remoteCmd

Write-Host "`nTest HTTP..." -ForegroundColor Green
try {
    $res = Invoke-WebRequest -Uri "https://$Server/DSDB_scheme/" -UseBasicParsing -TimeoutSec 5
    Write-Host "Status: $($res.StatusCode) $($res.StatusDescription)" -ForegroundColor Green
    Write-Host "Application disponible sur : https://$Server/DSDB_scheme/" -ForegroundColor Green
} catch {
    Write-Host "Verification termine : https://$Server/DSDB_scheme/" -ForegroundColor Yellow
}
