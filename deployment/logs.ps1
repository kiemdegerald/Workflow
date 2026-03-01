# Script pour voir les logs Odoo en temps réel
# Usage: .\logs.ps1

$SSH_KEY = "C:\Users\user\Desktop\wfssh\ssh-key-serveur-odoo-dev - Copie.key"
$SERVER = "ubuntu@130.61.235.163"

Write-Host "📋 Logs Odoo en temps réel (Ctrl+C pour quitter)..." -ForegroundColor Yellow
ssh -i $SSH_KEY $SERVER "sudo journalctl -u odoo -f"
