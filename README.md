# Workflow - Système de Validation Hiérarchique Multi-Niveaux

## 📋 Description

Module Odoo Enterprise v17 générique de gestion de workflows de validation multi-niveaux, conçu pour les institutions bancaires et financières.

## 🚀 Développement & Déploiement

**Pour les développeurs utilisant Cursor AI / VS Code :**

📁 **Dossier [deployment/](deployment/)** - Tous les outils de déploiement
- 📖 [GUIDE_CURSOR.md](deployment/GUIDE_CURSOR.md) - Configuration Cursor AI (⭐ À lire en premier)
- 📚 [DEPLOIEMENT.md](deployment/DEPLOIEMENT.md) - Documentation des scripts PowerShell
- 🚀 Scripts : `deploy.ps1`, `deploy-file.ps1`, `restart.ps1`, `logs.ps1`

📚 **Documentation technique complète :** [PROJET_WORKFLOW_DOCUMENTATION.md](exemple_page/PROJET_WORKFLOW_DOCUMENTATION.md)

### Déploiement rapide

```powershell
# Déployer tout le module
cd C:\Users\user\Desktop\addon_custom
.\deployment\deploy.ps1

# Déployer un fichier modifié
.\deployment\deploy-file.ps1 -FilePath "models\workflow_request.py"
.\deployment\restart.ps1

# Voir les logs en temps réel
.\deployment\logs.ps1
```

**Serveur Odoo** : ubuntu@130.61.235.163  
**Base de données** : odoo_2026_01_27  
**GitHub** : https://github.com/kiemdegerald/Workflow.git

---

## 🏗️ Structure du Module

```
workflow/
├── __init__.py                          # Initialisation racine
├── __manifest__.py                      # Manifeste du module
├── models/                              # Modèles Python (12 fichiers)
│   ├── __init__.py
│   ├── workflow_type.py                 # Types de workflow
│   ├── workflow_definition.py           # Circuits de validation
│   ├── workflow_level.py                # Niveaux d'approbation
│   ├── workflow_routing_rule.py         # Règles de routage
│   ├── workflow_request.py              # Demandes de validation
│   ├── workflow_request_approval.py     # Approbations
│   ├── workflow_request_comment.py      # Commentaires d'échange
│   ├── workflow_instance.py             # Instances actives
│   ├── workflow_custom_field.py         # Champs personnalisés
│   ├── workflow_request_document.py     # Documents attachés
│   ├── workflow_notification.py         # Notifications
│   └── workflow_audit_log.py            # Journal d'audit
├── security/                            # Droits d'accès
│   ├── workflow_security.xml            # Groupes de sécurité
│   └── ir.model.access.csv              # Droits d'accès des modèles
├── views/                               # Vues XML
│   └── workflow_type_views.xml          # Vues pour Types de Workflow
└── static/
    └── description/
        └── index.html                   # Description du module

```

## 📦 Installation

### Prérequis
- Odoo Enterprise v17.0 ou supérieur
- PostgreSQL 12+
- Python 3.10+

### Étapes d'installation

1. **Copier le module dans le dossier addons**
   ```bash
   cp -r workflow /chemin/vers/odoo/addons/
   ```

2. **Redémarrer le service Odoo**
   ```bash
   sudo systemctl restart odoo
   # ou
   odoo-bin -c /etc/odoo/odoo.conf
   ```

3. **Activer le mode développeur**
   - Connectez-vous à Odoo
   - Allez dans Paramètres → Activer le mode développeur

4. **Mettre à jour la liste des applications**
   - Menu Apps → ⋮ (trois points) → Mettre à jour la liste des applications

5. **Installer le module**
   - Recherchez "Workflow" dans Apps
   - Cliquez sur "Installer"

## 🚀 Configuration Initiale

Après installation, suivez ces étapes :

### 1. Créer un Type de Workflow
- Menu : **Workflow → Configuration → Types de Workflow**
- Cliquez sur "Créer"
- Exemple :
  - **Nom** : Crédit Bancaire
  - **Code** : CREDIT
  - **Description** : Processus de validation des demandes de crédit

### 2. Définir un Circuit de Validation
- Menu : **Workflow → Configuration → Circuits de Validation**
- Créez votre premier circuit (ex: Circuit A pour crédits < 5M FCFA)

### 3. Configurer les Niveaux d'Approbation
- Ajoutez les niveaux de validation pour chaque circuit
- Définissez la séquence et les validateurs

### 4. Paramétrer les Règles de Routage
- Créez des règles pour router automatiquement les demandes
- Basez-vous sur des critères métier (montant, priorité, etc.)

## 📊 Architecture Technique

### Modèles de Données

| Modèle | Table PostgreSQL | Description |
|--------|------------------|-------------|
| `workflow.type` | workflow_type | Types de workflow |
| `workflow.definition` | workflow_definition | Circuits de validation |
| `workflow.level` | workflow_level | Niveaux d'approbation |
| `workflow.routing.rule` | workflow_routing_rule | Règles de routage |
| `workflow.request` | workflow_request | Demandes de validation |
| `workflow.request.approval` | workflow_request_approval | Approbations |
| `workflow.request.comment` | workflow_request_comment | Commentaires d'échange |
| `workflow.instance` | workflow_instance | Instances actives |
| `workflow.custom.field` | workflow_custom_field | Champs personnalisés |
| `workflow.request.document` | workflow_request_document | Documents attachés |
| `workflow.notification` | workflow_notification | Notifications |
| `workflow.audit.log` | workflow_audit_log | Journal d'audit |

### Groupes de Sécurité

- **Utilisateur Workflow** (`group_workflow_user`) : Accès en lecture/écriture aux demandes
- **Gestionnaire Workflow** (`group_workflow_manager`) : Configuration complète du système

## 🔍 Résolution de Problèmes

### Le module n'apparaît pas dans Apps
- Vérifiez que le dossier est bien dans `addons/`
- Redémarrez Odoo
- Mettez à jour la liste des applications

### Erreur lors de l'installation
- Vérifiez les logs Odoo : `/var/log/odoo/odoo.log`
- Assurez-vous que tous les fichiers sont présents
- Vérifiez les permissions (chmod -R 755)

### Erreurs de droits d'accès
- Vérifiez que `ir.model.access.csv` est bien chargé
- Assignez les utilisateurs aux bons groupes

## 📝 Phase 1 - Fonctionnalités Actuelles

✅ Structure minimale installable
✅ 11 modèles Python fonctionnels
✅ Tables PostgreSQL créées automatiquement
✅ Droits d'accès de base
✅ Interface de configuration (Types de Workflow)
✅ Groupes de sécurité
✅ Description HTML du module

## 🔜 Phase 2 - Développements Futurs

❌ Logique métier complète (validation, routage automatique)
❌ Vues XML pour tous les modèles
❌ Wizards de workflow
❌ Rapports QWeb
❌ Dashboard de suivi
❌ Notifications automatiques
❌ Tests automatisés
❌ Traductions (fr_FR, en_US)

## 👨‍💻 Développement

### Ajouter de nouveaux champs à un modèle

Éditez le fichier du modèle dans `models/` :

```python
# models/workflow_type.py
priority = fields.Integer(string='Priorité', default=10)
```

Mettez à jour le module :
```bash
odoo-bin -u workflow -c /etc/odoo/odoo.conf
```

### Créer une nouvelle vue

Créez un fichier dans `views/` et ajoutez-le dans `__manifest__.py` :

```python
'data': [
    'security/workflow_security.xml',
    'security/ir.model.access.csv',
    'views/workflow_type_views.xml',
    'views/workflow_request_views.xml',  # Nouveau
],
```

## 📄 Licence

**Odoo Proprietary License v1.0 (OPL-1)**

Ce module est la propriété de Liceli Technologies. Toute utilisation, copie, modification ou distribution non autorisée est strictement interdite.

## 🤝 Support

- **Éditeur** : Liceli Technologies
- **Website** : https://liceli-technologies.com
- **Email** : support@liceli-technologies.com
- **Documentation** : https://docs.liceli-technologies.com/workflow

## 📌 Version

**Version actuelle** : 17.0.1.0.0

### Changelog

#### v17.0.1.0.0 (2026-02-18)
- 🎉 Version initiale
- ✅ Structure de base installable
- ✅ 11 modèles de données
- ✅ Configuration minimale

---

© 2026 Liceli Technologies - Tous droits réservés
