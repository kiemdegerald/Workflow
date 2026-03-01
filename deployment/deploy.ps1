# Script de déploiement automatique du module workflow
# Usage: .\deploy.ps1

$SSH_KEY = "C:\Users\user\Desktop\wfssh\ssh-key-serveur-odoo-dev - Copie.key"
$SERVER = "ubuntu@130.61.235.163"
$LOCAL_PATH = "C:\Users\user\Desktop\addon_custom"
$REMOTE_PATH = "/opt/odoo/custom_addons/workflow"

Write-Host "🚀 Déploiement du module workflow..." -ForegroundColor Green

# 1. Upload des fichiers Python
Write-Host "📤 Upload des modèles..." -ForegroundColor Yellow
scp -i $SSH_KEY -r models ${SERVER}:/tmp/workflow_models
ssh -i $SSH_KEY $SERVER "sudo cp -r /tmp/workflow_models/* $REMOTE_PATH/models/ && sudo rm -rf /tmp/workflow_models"

# 2. Upload des vues XML
Write-Host "📤 Upload des vues..." -ForegroundColor Yellow
scp -i $SSH_KEY -r views ${SERVER}:/tmp/workflow_views
ssh -i $SSH_KEY $SERVER "sudo cp -r /tmp/workflow_views/* $REMOTE_PATH/views/ && sudo rm -rf /tmp/workflow_views"

# 3. Upload du manifest et __init__.py
Write-Host "📤 Upload du manifest..." -ForegroundColor Yellow
scp -i $SSH_KEY __manifest__.py __init__.py ${SERVER}:/tmp/
ssh -i $SSH_KEY $SERVER "sudo cp /tmp/__manifest__.py /tmp/__init__.py $REMOTE_PATH/ && sudo rm /tmp/__manifest__.py /tmp/__init__.py"

# 4. Upload du module courrier
Write-Host "📤 Upload du module courrier..." -ForegroundColor Yellow
scp -i $SSH_KEY -r courrier ${SERVER}:/tmp/workflow_courrier
ssh -i $SSH_KEY $SERVER "sudo cp -r /tmp/workflow_courrier $REMOTE_PATH/courrier && sudo rm -rf /tmp/workflow_courrier"

# 5. Mise à jour du module
Write-Host "🔄 Mise à jour du module..." -ForegroundColor Yellow
ssh -i $SSH_KEY $SERVER "sudo systemctl stop odoo && sudo -u odoo /usr/bin/odoo -c /etc/odoo/odoo.conf -d odoo_2026_01_27 -u workflow --stop-after-init && sudo systemctl start odoo"

Write-Host "✅ Déploiement terminé !" -ForegroundColor Green
Write-Host "🌐 Actualisez votre navigateur avec Ctrl+F5" -ForegroundColor Cyan
