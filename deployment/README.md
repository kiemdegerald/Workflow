# 🚀 Dossier Deployment - Scripts de Déploiement Odoo

Outils de déploiement automatisés pour le module **workflow** Odoo.

## 📁 Fichiers Disponibles

| Fichier | Description |
|---------|-------------|
| `deploy.ps1` | Déploiement complet du module |
| `deploy-file.ps1` | Déploiement d'un fichier unique |
| `restart.ps1` | Redémarrage rapide d'Odoo |
| `logs.ps1` | Visualisation des logs en temps réel |
| `GUIDE_CURSOR.md` | Guide complet pour Cursor AI (⭐ **À lire en premier**) |
| `DEPLOIEMENT.md` | Documentation détaillée des scripts |
| `ssh_config_exemple.txt` | Template de configuration SSH |
| `README.md` | Ce fichier |

---

## ⚡ Quick Start

### Déploiement Complet
```powershell
cd C:\Users\user\Desktop\addon_custom
.\deployment\deploy.ps1
```

### Déploiement d'un Fichier
```powershell
.\deployment\deploy-file.ps1 -FilePath "models\workflow_request.py"
.\deployment\restart.ps1
```

### Voir les Logs
```powershell
.\deployment\logs.ps1
```

---

## 🎯 Deux Approches de Développement

### Option 1 : Remote-SSH (Recommandé)
- Éditer directement sur le serveur via Cursor AI
- Pas de déploiement nécessaire
- Configuration : voir `ssh_config_exemple.txt`

### Option 2 : Local + Scripts
- Éditer en local, déployer avec les scripts PowerShell
- Workflow : Éditer → `deploy.ps1` → Tester
- Plus rapide pour l'édition, nécessite déploiement

---

## 📚 Documentation

| Guide | Usage |
|-------|-------|
| **GUIDE_CURSOR.md** | Configuration Cursor AI, workflows de développement |
| **DEPLOIEMENT.md** | Documentation complète des 4 scripts PowerShell |

---

## 🔧 Configuration Serveur

- **Serveur** : `ubuntu@130.61.235.163`
- **Base de données** : `odoo_2026_01_27`
- **Clé SSH** : `C:\Users\user\Desktop\wfssh\ssh-key-serveur-odoo-dev - Copie.key`
- **Chemin module** : `/opt/odoo/custom_addons/workflow`

---

## 💡 Aide Rapide

### Problème : Module non mis à jour
```powershell
.\deployment\restart.ps1
# Puis Ctrl+F5 dans le navigateur
```

### Problème : Erreur après déploiement
```powershell
.\deployment\logs.ps1
# Ctrl+C pour quitter
```

### Connexion SSH manuelle
```powershell
ssh -i "C:\Users\user\Desktop\wfssh\ssh-key-serveur-odoo-dev - Copie.key" ubuntu@130.61.235.163
```

---

## 📖 Ressources Complémentaires

- **Documentation Technique** : `../exemple_page/PROJET_WORKFLOW_DOCUMENTATION.md`
- **README Principal** : `../README.md`
- **GitHub Repository** : https://github.com/kiemdegerald/Workflow.git

---

**🎯 Pour commencer** : Lisez `GUIDE_CURSOR.md` pour choisir votre approche de développement !
