# 📚 Documentation des Scripts de Déploiement

## 🎯 Vue d'ensemble

Scripts PowerShell pour automatiser le déploiement du module **workflow** vers le serveur Odoo.

---

## 📜 Scripts Disponibles

### 1️⃣ `deploy.ps1` - Déploiement Complet

Déploie l'intégralité du module workflow vers le serveur.

#### Usage
```powershell
cd C:\Users\user\Desktop\addon_custom
.\deployment\deploy.ps1
```

#### Étapes exécutées
1. ✅ Upload des modèles Python (`models/*.py`)
2. ✅ Upload des vues XML (`views/*.xml`)
3. ✅ Upload de `__manifest__.py` et `__init__.py`
4. ✅ Upload du module courrier (`courrier/`)
5. ✅ Arrêt d'Odoo
6. ✅ Mise à jour du module (`-u workflow`)
7. ✅ Redémarrage d'Odoo

#### Durée estimée
⏱️ 30-60 secondes (selon la taille des fichiers et la connexion)

#### Sortie typique
```
🚀 Déploiement du module workflow...
📤 Upload des modèles...
📤 Upload des vues...
📤 Upload du manifest...
📤 Upload du module courrier...
🔄 Mise à jour du module...
✅ Déploiement terminé !
🌐 Actualisez votre navigateur avec Ctrl+F5
```

---

### 2️⃣ `deploy-file.ps1` - Déploiement de Fichier Unique

Déploie un seul fichier modifié vers le serveur (rapide pour les petites modifications).

#### Usage
```powershell
.\deployment\deploy-file.ps1 -FilePath "models\workflow_request.py"
```

#### Exemples
```powershell
# Déployer un modèle
.\deployment\deploy-file.ps1 -FilePath "models\workflow_dashboard.py"

# Déployer une vue
.\deployment\deploy-file.ps1 -FilePath "views\workflow_request_views.xml"

# Déployer le manifest
.\deployment\deploy-file.ps1 -FilePath "__manifest__.py"

# Déployer un fichier du module courrier
.\deployment\deploy-file.ps1 -FilePath "courrier\models\workflow_courrier_entrant.py"
```

#### Durée estimée
⏱️ 5-10 secondes

#### ⚠️ Important
Après le déploiement d'un fichier, **redémarrez Odoo** :
```powershell
.\deployment\restart.ps1
```

---

### 3️⃣ `restart.ps1` - Redémarrage Odoo

Redémarre le service Odoo rapidement.

#### Usage
```powershell
.\deployment\restart.ps1
```

#### Quand l'utiliser ?
- Après un déploiement de fichier unique
- Après modification du code Python
- Pour recharger les vues XML modifiées
- En cas de comportement étrange d'Odoo

#### Durée estimée
⏱️ 3-5 secondes

#### Sortie typique
```
🔄 Redémarrage d'Odoo...
✅ Odoo redémarré !
🕐 Attendez 5-10 secondes puis actualisez votre navigateur
```

---

### 4️⃣ `logs.ps1` - Voir les Logs en Temps Réel

Affiche les logs Odoo en continu pour le débogage.

#### Usage
```powershell
.\deployment\logs.ps1
```

#### Quitter
Appuyez sur `Ctrl+C` pour arrêter l'affichage des logs.

#### Cas d'usage
- Déboguer une erreur après déploiement
- Voir les requêtes SQL exécutées
- Vérifier que le module se charge correctement
- Observer les messages de warning/error

#### Filtrage des logs
Les logs Odoo sont très verbeux. Utilisez PowerShell pour filtrer :

```powershell
# Voir uniquement les erreurs
.\deployment\logs.ps1 | Select-String "ERROR"

# Voir les logs du module workflow
.\deployment\logs.ps1 | Select-String "workflow"
```

---

## 🔧 Configuration des Scripts

### Variables communes (présentes dans chaque script)

```powershell
$SSH_KEY = "C:\Users\user\Desktop\wfssh\ssh-key-serveur-odoo-dev - Copie.key"
$SERVER = "ubuntu@130.61.235.163"
$REMOTE_PATH = "/opt/odoo/custom_addons/workflow"
```

### Modifier la configuration

Si votre environnement change, éditez ces variables dans chaque script :

- **SSH_KEY** : Chemin vers votre clé SSH privée
- **SERVER** : Adresse du serveur (user@ip)
- **REMOTE_PATH** : Chemin du module sur le serveur

---

## 🚀 Workflows Recommandés

### 🟢 Développement quotidien (petites modifications)

```powershell
# 1. Éditer le fichier en local
# 2. Déployer le fichier modifié
.\deployment\deploy-file.ps1 -FilePath "models\workflow_request.py"

# 3. Redémarrer Odoo
.\deployment\restart.ps1

# 4. Voir les logs si nécessaire
.\deployment\logs.ps1
```

### 🟡 Modification importante (plusieurs fichiers)

```powershell
# 1. Éditer plusieurs fichiers
# 2. Déploiement complet
.\deployment\deploy.ps1

# 3. Les logs s'affichent automatiquement après la mise à jour
```

### 🔴 Débogage d'erreur

```powershell
# 1. Déployer
.\deployment\deploy.ps1

# 2. Voir les logs en temps réel
.\deployment\logs.ps1

# 3. Corriger le code
# 4. Redéployer le fichier corrigé
.\deployment\deploy-file.ps1 -FilePath "models\problematic_file.py"
.\deployment\restart.ps1
```

---

## 💡 Astuces PowerShell

### Alias pour gagner du temps

Ajoutez dans votre profil PowerShell (`$PROFILE`) :

```powershell
function Deploy-Full { 
    cd C:\Users\user\Desktop\addon_custom
    .\deployment\deploy.ps1 
}

function Deploy-File { 
    param([string]$File)
    cd C:\Users\user\Desktop\addon_custom
    .\deployment\deploy-file.ps1 -FilePath $File
    .\deployment\restart.ps1
}

function Restart-Odoo { 
    cd C:\Users\user\Desktop\addon_custom
    .\deployment\restart.ps1 
}

function Show-Logs { 
    cd C:\Users\user\Desktop\addon_custom
    .\deployment\logs.ps1 
}

# Utilisation
Deploy-Full
Deploy-File "models\workflow_request.py"
Restart-Odoo
Show-Logs
```

---

## 🐛 Dépannage

### Erreur : "Permission denied"

**Symptôme** : SCP ou SSH refuse la connexion

**Solutions** :
1. Vérifier que la clé SSH existe et a les bonnes permissions
2. Tester la connexion SSH manuellement :
   ```powershell
   ssh -i "C:\Users\user\Desktop\wfssh\ssh-key-serveur-odoo-dev - Copie.key" ubuntu@130.61.235.163
   ```

### Erreur : "Module not found after update"

**Symptôme** : Le module ne se met pas à jour après déploiement

**Solutions** :
1. Vérifier que les fichiers ont bien été copiés :
   ```bash
   sudo ls -lh /opt/odoo/custom_addons/workflow/models/
   ```
2. Forcer la mise à jour :
   ```bash
   sudo systemctl stop odoo
   sudo -u odoo /usr/bin/odoo -c /etc/odoo/odoo.conf -d odoo_2026_01_27 -u workflow --stop-after-init
   sudo systemctl start odoo
   ```
3. Redémarrer complètement le serveur Odoo

### Erreur : "Database lock"

**Symptôme** : Erreur lors de la mise à jour du module

**Solution** : Déconnecter tous les utilisateurs d'Odoo avant le déploiement, ou forcer l'arrêt :
```bash
sudo systemctl stop odoo
sudo pkill -9 -f odoo
sudo systemctl start odoo
```

---

## 📞 Informations Serveur

- **Serveur** : ubuntu@130.61.235.163
- **Base de données** : odoo_2026_01_27
- **Chemin module** : `/opt/odoo/custom_addons/workflow`
- **Service Odoo** : `odoo.service` (systemd)
- **Logs Odoo** : `journalctl -u odoo`

---

## 📚 Voir Aussi

- `GUIDE_CURSOR.md` - Guide complet pour Cursor AI
- `README.md` - Documentation du dossier deployment
- `../README.md` - Documentation principale du module
- `../exemple_page/PROJET_WORKFLOW_DOCUMENTATION.md` - Architecture technique
