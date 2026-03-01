# Script de redémarrage Odoo
# Usage: .\restart.ps1

$SSH_KEY = "C:\Users\user\Desktop\wfssh\ssh-key-serveur-odoo-dev - Copie.key"
$SERVER = "ubuntu@130.61.235.163"

Write-Host "🔄 Redémarrage d'Odoo..." -ForegroundColor Yellow
ssh -i $SSH_KEY $SERVER "sudo systemctl restart odoo"

Write-Host "✅ Odoo redémarré !" -ForegroundColor Green
Write-Host "🕐 Attendez 5-10 secondes puis actualisez votre navigateur" -ForegroundColor Cyan
