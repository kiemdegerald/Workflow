# Script de déploiement d'un fichier unique
# Usage: .\deploy-file.ps1 -FilePath "models\workflow_request.py"

param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath
)

$SSH_KEY = "C:\Users\user\Desktop\wfssh\ssh-key-serveur-odoo-dev - Copie.key"
$SERVER = "ubuntu@130.61.235.163"
$REMOTE_PATH = "/opt/odoo/custom_addons/workflow"

Write-Host "📤 Déploiement de $FilePath..." -ForegroundColor Yellow

# Upload du fichier
$FileName = Split-Path $FilePath -Leaf
scp -i $SSH_KEY $FilePath ${SERVER}:/tmp/$FileName

# Copier vers le bon emplacement
$RemoteFile = "$REMOTE_PATH/$($FilePath -replace '\\', '/')"
ssh -i $SSH_KEY $SERVER "sudo cp /tmp/$FileName $RemoteFile && sudo rm /tmp/$FileName"

Write-Host "✅ Fichier déployé !" -ForegroundColor Green
Write-Host "🔄 Redémarrez Odoo avec: .\restart.ps1" -ForegroundColor Cyan
