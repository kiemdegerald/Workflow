# 🚀 Guide de Configuration Cursor AI pour le Développement Odoo

## 📋 Vue d'ensemble

Ce guide vous aide à configurer **Cursor AI** pour développer et déployer le module **workflow** Odoo efficacement.

## 🎯 Deux approches de développement

### Option 1 : Remote-SSH (Recommandé pour débutants)

Éditer directement les fichiers sur le serveur via SSH.

#### ✅ Avantages
- Code toujours synchronisé avec le serveur
- Pas besoin de déploiement manuel
- Redémarrage Odoo direct depuis Cursor

#### 📦 Installation
1. Installer l'extension **Remote-SSH** dans VS Code/Cursor
2. Configurer le fichier SSH config (voir `ssh_config_exemple.txt`)
3. Se connecter au serveur via la palette de commandes

#### ⚙️ Configuration SSH

Créer/éditer le fichier : `C:\Users\user\.ssh\config`

```ssh
Host odoo-server
    HostName 130.61.235.163
    User ubuntu
    IdentityFile C:\Users\user\Desktop\wfssh\ssh-key-serveur-odoo-dev - Copie.key
    StrictHostKeyChecking no
```

#### 🔗 Connexion
1. Ouvrir Cursor AI
2. `Ctrl+Shift+P` → "Remote-SSH: Connect to Host"
3. Sélectionner `odoo-server`
4. Ouvrir le dossier : `/opt/odoo/custom_addons/workflow`

#### 🔄 Workflow de développement
1. Éditer les fichiers directement dans Cursor
2. Redémarrer Odoo : `sudo systemctl restart odoo`
3. Voir les logs : `sudo journalctl -u odoo -f`

---

### Option 2 : Développement Local + Scripts de Déploiement

Éditer en local et déployer avec des scripts PowerShell automatisés.

#### ✅ Avantages
- Travail hors-ligne possible
- Git et version control plus faciles
- Performance d'édition optimale

#### 📦 Scripts disponibles

| Script | Usage | Description |
|--------|-------|-------------|
| `deploy.ps1` | `.\deploy.ps1` | Déploiement complet du module |
| `deploy-file.ps1` | `.\deploy-file.ps1 -FilePath "models\workflow_request.py"` | Déployer un seul fichier |
| `restart.ps1` | `.\restart.ps1` | Redémarrer Odoo rapidement |
| `logs.ps1` | `.\logs.ps1` | Voir les logs en temps réel |

#### 🔄 Workflow de développement
1. Éditer les fichiers en local dans `C:\Users\user\Desktop\addon_custom\`
2. Déployer : `.\deployment\deploy.ps1`
3. Tester dans le navigateur
4. Répéter

#### ⚡ Déploiement rapide d'un fichier
```powershell
cd C:\Users\user\Desktop\addon_custom
.\deployment\deploy-file.ps1 -FilePath "models\workflow_request.py"
.\deployment\restart.ps1
```

---

## 🐛 Débogage

### Voir les logs Odoo
```powershell
# Avec script
.\deployment\logs.ps1

# Ou via SSH direct
ssh -i "C:\Users\user\Desktop\wfssh\ssh-key-serveur-odoo-dev - Copie.key" ubuntu@130.61.235.163 "sudo journalctl -u odoo -f"
```

### Vérifier l'état du service
```bash
sudo systemctl status odoo
```

### Mise à jour manuelle du module
```bash
sudo systemctl stop odoo
sudo -u odoo /usr/bin/odoo -c /etc/odoo/odoo.conf -d odoo_2026_01_27 -u workflow --stop-after-init
sudo systemctl start odoo
```

---

## 📚 Ressources

- **Documentation technique** : `../exemple_page/PROJET_WORKFLOW_DOCUMENTATION.md`
- **Scripts PowerShell** : `DEPLOIEMENT.md`
- **Serveur Odoo** : ubuntu@130.61.235.163
- **Base de données** : odoo_2026_01_27
- **Clé SSH** : `C:\Users\user\Desktop\wfssh\ssh-key-serveur-odoo-dev - Copie.key`

---

## 💡 Conseils Cursor AI

### Commandes utiles dans le terminal Cursor
```powershell
# Déployer tout
cd C:\Users\user\Desktop\addon_custom
.\deployment\deploy.ps1

# Déployer un fichier modifié
.\deployment\deploy-file.ps1 -FilePath "views\workflow_request_views.xml"

# Redémarrer Odoo
.\deployment\restart.ps1

# Voir les logs
.\deployment\logs.ps1
```

### Demander à Cursor AI
- "Déploie le fichier workflow_request.py sur le serveur"
- "Redémarre Odoo et montre-moi les logs"
- "Quelle est la différence entre le code local et le serveur?"

---

## 🔧 Dépannage

### Problème : Permission denied lors du SCP
**Solution** : Les scripts utilisent `sudo` pour copier dans `/opt/odoo/`

### Problème : Module non mis à jour après déploiement
**Solutions** :
1. Redémarrer Odoo : `.\deployment\restart.ps1`
2. Mise à jour forcée : `.\deployment\deploy.ps1` (inclut `-u workflow`)
3. Vider le cache navigateur : `Ctrl+F5`

### Problème : Impossible de se connecter en SSH
**Vérifications** :
1. Clé SSH au bon emplacement
2. Permissions de la clé correctes
3. Serveur accessible : `ping 130.61.235.163`

---

## 📞 Support

Pour plus d'informations, consultez :
- `DEPLOIEMENT.md` - Documentation détaillée des scripts
- `PROJET_WORKFLOW_DOCUMENTATION.md` - Architecture du module
- README.md principal du module
