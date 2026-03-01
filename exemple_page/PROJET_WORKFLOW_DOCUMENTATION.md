# 📚 Documentation Technique - Module Workflow Odoo

## 🎯 Vue d'ensemble

Module Odoo 17.0 Enterprise pour la gestion de workflows de validation hiérarchique multi-niveaux, spécialement conçu pour les institutions bancaires et financières.

**Version** : 17.0.1.0.0  
**Licence** : LGPL-3  
**Serveur** : ubuntu@130.61.235.163  
**Base de données** : odoo_2026_01_27  
**Chemin module** : `/opt/odoo/custom_addons/workflow`  

---

## 🏗️ Architecture du Module

### Structure des Dossiers

```
workflow/
├── __init__.py                          # Initialisation principale
├── __manifest__.py                      # Manifeste du module (dépendances, données)
├── models/                              # Modèles métier (9 fichiers)
│   ├── __init__.py
│   ├── workflow_type.py                 # Types de workflow (Crédit, Courrier)
│   ├── workflow_definition.py           # Circuits de validation
│   ├── workflow_level.py                # Niveaux hiérarchiques
│   ├── workflow_routing_rule.py         # Règles de routage conditionnelles
│   ├── workflow_request.py              # Demandes de validation
│   ├── workflow_request_approval.py     # Approbations individuelles
│   ├── workflow_request_comment.py      # Commentaires chronologiques
│   ├── workflow_approval_view.py        # Vue Approbateur (TransientModel)
│   └── workflow_dashboard.py            # Dashboard avec statistiques
├── views/                               # Interfaces utilisateur (6 fichiers XML)
│   ├── workflow_menus.xml               # Structure des menus
│   ├── workflow_type_views.xml          # Gestion des types
│   ├── workflow_definition_views.xml    # Configuration circuits
│   ├── workflow_routing_rule_views.xml  # Règles de routage
│   ├── workflow_request_views.xml       # Liste et formulaire demandes
│   ├── workflow_request_comment_views.xml # Popup commentaires
│   ├── workflow_approval_view_views.xml # Vue Approbateur
│   └── workflow_dashboard.xml           # Dashboard HTML
├── courrier/                            # Module courrier entrant/sortant
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── workflow_courrier_entrant.py # Gestion du courrier
│   └── views/
│       └── workflow_courrier_views.xml  # Interface courrier
├── security/                            # Droits d'accès
│   ├── workflow_security.xml            # Groupes de sécurité
│   └── ir.model.access.csv              # Permissions par modèle
├── data/                                # Données de démonstration
│   └── workflow_demo_data.xml           # Circuits et utilisateurs démo
├── static/                              # Assets (CSS/JS)
│   └── description/
│       └── icon.png                     # Icône du module
├── wizard/                              # Assistants
│   ├── __init__.py
│   └── workflow_request_wizard.py       # Wizard création demande
└── controllers/                         # Contrôleurs web
    ├── __init__.py
    └── main.py                          # Routes HTTP

```

---

## 📊 Modèles de Données

### 1. `workflow.type` - Types de Workflow

**Fichier** : `models/workflow_type.py`

Définit les différents types de workflow disponibles (Crédit, Courrier, Congés, etc.).

**Champs principaux** :
- `name` : Nom du type (ex: "Demande de Crédit")
- `code` : Code unique (ex: "credit", "courrier")
- `description` : Description détaillée
- `active` : Actif/Inactif
- `definition_ids` : Circuits associés à ce type

**Relations** :
- One2many → `workflow.definition` (circuits de validation)

---

### 2. `workflow.definition` - Circuits de Validation

**Fichier** : `models/workflow_definition.py`

Configure les circuits de validation avec leurs niveaux hiérarchiques.

**Champs principaux** :
- `name` : Nom du circuit (ex: "Circuit Standard Crédit")
- `workflow_type_id` : Type de workflow associé
- `level_ids` : Liste ordonnée des niveaux de validation
- `active` : Circuit actif/inactif
- `is_default` : Circuit par défaut pour ce type

**Relations** :
- Many2one → `workflow.type`
- One2many → `workflow.level` (niveaux du circuit)

---

### 3. `workflow.level` - Niveaux Hiérarchiques

**Fichier** : `models/workflow_level.py`

Définit chaque niveau de validation dans un circuit (Agent → Chef → Directeur).

**Champs principaux** :
- `name` : Nom du niveau (ex: "Niveau Chef de Service")
- `sequence` : Ordre d'exécution (10, 20, 30...)
- `workflow_definition_id` : Circuit parent
- `approver_ids` : Liste des validateurs à ce niveau
- `approval_type` : Type d'approbation
  - `all` : **TOUS** les validateurs doivent approuver
  - `any` : **UN SEUL** validateur suffit

**Relations** :
- Many2one → `workflow.definition`
- Many2many → `res.users` (validateurs)

**Logique clé** : Le système attend que TOUS les validateurs d'un même niveau approuvent avant de passer au niveau suivant (logique multi-validateur).

---

### 4. `workflow.request` - Demandes de Validation

**Fichier** : `models/workflow_request.py`

Demande principale soumise par un utilisateur.

**Champs principaux** :
- `name` : Numéro auto-généré (ex: "WF/2026/0001")
- `workflow_type_id` : Type de demande
- `workflow_definition_id` : Circuit utilisé
- `requester_id` : Demandeur
- `state` : État de la demande
  - `draft` : Brouillon
  - `submitted` : Soumis
  - `in_progress` : En cours de validation
  - `approved` : Approuvé
  - `rejected` : Rejeté
  - `cancelled` : Annulé
- `current_level_id` : Niveau de validation actuel
- `approval_ids` : Toutes les approbations de cette demande
- `comment_ids` : Historique des commentaires

**Champs spécifiques Crédit** :
- `montant` : Montant demandé
- `description` : Description de la demande
- `objet` : Objet du crédit

**Relations** :
- Many2one → `workflow.type`, `workflow.definition`, `workflow.level`, `res.users`
- One2many → `workflow.request.approval`, `workflow.request.comment`

**Méthodes importantes** :
- `action_submit()` : Soumettre la demande → crée les approbations du 1er niveau
- `action_cancel()` : Annuler la demande
- `_check_level_complete()` : Vérifie si tous les validateurs du niveau ont validé

---

### 5. `workflow.request.approval` - Approbations Individuelles

**Fichier** : `models/workflow_request_approval.py`

Enregistrement individuel pour chaque validateur à chaque niveau.

**Champs principaux** :
- `workflow_request_id` : Demande associée
- `workflow_level_id` : Niveau de validation
- `approver_id` : Validateur concerné
- `state` : État de l'approbation
  - `pending` : En attente
  - `approved` : Approuvé
  - `rejected` : Rejeté
- `approval_date` : Date de décision
- `comments` : Commentaire du validateur

**Relations** :
- Many2one → `workflow.request`, `workflow.level`, `res.users`

**Logique** : Un enregistrement est créé pour CHAQUE validateur à CHAQUE niveau.

---

### 6. `workflow.request.comment` - Commentaires Chronologiques

**Fichier** : `models/workflow_request_comment.py`

Historique complet de tous les échanges et décisions.

**Champs principaux** :
- `workflow_request_id` : Demande concernée
- `approval_id` : Approbation associée (si applicable)
- `user_id` : Auteur du commentaire
- `message` : Contenu du commentaire
- `comment_type` : Type de commentaire
  - `approval_note` : Note d'approbation (fond bleu)
  - `rejection_reason` : Motif de rejet (fond rouge)
  - `return` : Demande de complément (fond orange)
  - `general` : Commentaire général

**Relations** :
- Many2one → `workflow.request`, `workflow.request.approval`, `res.users`

**Vue spéciale** : Popup chronologique avec décorateurs de couleur selon le type.

---

### 7. `workflow.routing.rule` - Règles de Routage

**Fichier** : `models/workflow_routing_rule.py`

Règles conditionnelles pour router automatiquement selon le montant, etc.

**Champs principaux** :
- `name` : Nom de la règle
- `workflow_type_id` : Type concerné
- `condition_field` : Champ à évaluer (ex: "montant")
- `condition_operator` : Opérateur (`>`, `<`, `>=`, `<=`, `==`, `!=`)
- `condition_value` : Valeur seuil
- `target_definition_id` : Circuit cible si condition vraie

**Relations** :
- Many2one → `workflow.type`, `workflow.definition`

**Exemple** : Si montant > 1000000 → Circuit "Haut Montant"

---

### 8. `workflow.request.approval.view` - Vue Approbateur (TransientModel)

**Fichier** : `models/workflow_approval_view.py`

Interface de validation pour les approbateurs (pop-up).

**Champs principaux** :
- `request_id` : Demande à traiter
- `current_approval_id` : Approbation actuelle de l'utilisateur
- `comment` : Commentaire du validateur
- `action_type` : Type d'action
  - `approve` : Approuver
  - `reject` : Rejeter
  - `return` : Retourner

**Méthodes critiques** :

#### `action_approve()` - Logique Multi-Validateur

```python
def action_approve(self):
    # 1. Marquer l'approbation actuelle comme approuvée
    self.current_approval_id.write({
        'state': 'approved',
        'approval_date': fields.Datetime.now(),
        'comments': self.comment
    })
    
    # 2. Créer le commentaire d'approbation
    self.env['workflow.request.comment'].create({
        'workflow_request_id': self.request_id.id,
        'approval_id': self.current_approval_id.id,
        'user_id': self.env.user.id,
        'message': self.comment or "Approuvé",
        'comment_type': 'approval_note'
    })
    
    # 3. CRITIQUE : Vérifier si d'autres validateurs au MÊME niveau sont en attente
    current_level = self.current_approval_id.workflow_level_id
    pending_at_current_level = self.env['workflow.request.approval'].search([
        ('workflow_request_id', '=', self.request_id.id),
        ('workflow_level_id', '=', current_level.id),
        ('state', '=', 'pending')
    ])
    
    # 4. Si d'autres validateurs en attente → ATTENDRE
    if pending_at_current_level:
        self.request_id.write({'state': 'in_progress'})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Demande approuvée. En attente des autres validateurs du niveau.',
                'type': 'success',
                'sticky': False
            }
        }
    
    # 5. Tous validés au niveau → Passer au niveau suivant
    next_level = self.env['workflow.level'].search([
        ('workflow_definition_id', '=', self.request_id.workflow_definition_id.id),
        ('sequence', '>', current_level.sequence)
    ], order='sequence', limit=1)
    
    if next_level:
        # Créer les approbations pour le niveau suivant
        for approver in next_level.approver_ids:
            self.env['workflow.request.approval'].create({
                'workflow_request_id': self.request_id.id,
                'workflow_level_id': next_level.id,
                'approver_id': approver.id,
                'state': 'pending'
            })
        
        self.request_id.write({
            'current_level_id': next_level.id,
            'state': 'in_progress'
        })
    else:
        # Plus de niveau → Demande approuvée
        self.request_id.write({'state': 'approved'})
    
    return {'type': 'ir.actions.act_window_close'}
```

**Point clé** : Cette logique garantit que TOUS les validateurs d'un même niveau doivent approuver avant de passer au suivant.

---

### 9. `workflow.dashboard` - Dashboard avec Statistiques

**Fichier** : `models/workflow_dashboard.py`

Dashboard HTML avec statistiques et demandes récentes paginées.

**Champs principaux** :
- `name` : "Mon Dashboard"
- `html_content` : Contenu HTML généré dynamiquement
- `total_requests` : Nombre total de demandes
- `pending_approvals` : Approbations en attente pour l'utilisateur
- `approved_count` : Demandes approuvées (30 derniers jours)
- `rejected_count` : Demandes rejetées (30 derniers jours)

**Méthodes** :
- `_compute_html_dashboard()` : Génère le HTML avec stats + tableau paginé
- `action_refresh()` : Rafraîchit les données
- `action_previous_page()` / `action_next_page()` : Navigation pagination

**Pagination** :
- 10 demandes par page
- Boutons "Précédent" / "Suivant" avec styles conditionnels
- Indicateur "Page X sur Y"

---

## 🔄 Flux de Validation Complet

### Étape 1 : Création de la Demande

1. Utilisateur clique sur "Nouvelle Demande"
2. Wizard s'ouvre (`workflow.request.wizard`)
3. Sélection du type de workflow
4. Remplissage des champs (montant, description...)
5. État : `draft`

### Étape 2 : Soumission

1. Clic sur "Soumettre"
2. Méthode `action_submit()` :
   - Change état → `submitted`
   - Applique règles de routage (si montant spécifique)
   - Identifie le 1er niveau du circuit
   - Crée les `workflow.request.approval` pour TOUS les validateurs du 1er niveau
   - Change état → `in_progress`
   - Définit `current_level_id`

### Étape 3 : Validation Niveau 1 (Agent)

1. Agent reçoit notification (demande en attente)
2. Ouvre la demande → Bouton "Valider/Rejeter"
3. Vue Approbateur s'ouvre
4. Agent approuve avec commentaire
5. Méthode `action_approve()` :
   - Marque son approbation comme `approved`
   - Crée un commentaire type `approval_note`
   - **Vérifie si d'autres agents doivent encore valider** (si plusieurs agents)
   - Si d'autres agents en attente → RESTE au Niveau 1
   - Si tous les agents ont validé → PASSE au Niveau 2

### Étape 4 : Validation Niveau 2 (Chef) - Multi-Validateur

**Cas : 2 Chefs doivent valider**

1. **Chef 1 valide** :
   - Son approbation → `approved`
   - Système détecte Chef 2 encore en `pending`
   - **ATTEND** : Demande reste au Niveau 2
   - Message : "En attente des autres validateurs"

2. **Chef 2 valide** :
   - Son approbation → `approved`
   - Système vérifie : Plus personne en `pending` au Niveau 2
   - **AVANCE** : Crée approbations pour Niveau 3 (Directeur)
   - `current_level_id` → Niveau 3

### Étape 5 : Validation Niveau 3 (Directeur)

1. Directeur valide
2. Plus de niveau suivant
3. État demande → `approved`
4. Fin du workflow

### Rejet à n'importe quel niveau

1. Validateur clique "Rejeter"
2. Doit saisir motif obligatoire
3. Méthode `action_reject()` :
   - Approbation actuelle → `rejected`
   - Commentaire type `rejection_reason` (fond rouge)
   - **Toute la demande** → `rejected`
   - Workflow terminé

---

## 🎨 Vues et Interfaces

### 1. Liste des Demandes (`workflow_request_views.xml`)

**Vue Tree** :
- Colonnes : Numéro, Type, Demandeur, Montant, Niveau Actuel, État
- Filtres : Mes Demandes, À Valider, État
- Groupement : Par État, Par Type
- Pagination : 10 demandes par page
- Décorateurs couleur selon état

**Action** : `action_workflow_request`

### 2. Formulaire de Demande (`workflow_request_views.xml`)

**Structure en onglets** :
- **Informations Générales** : Type, Circuit, Demandeur, État
- **Détails de la Demande** : Montant, Description, Objet
- **Validation** : Niveau actuel, Historique approbations
- **Commentaires** : Bouton "Voir Historique" → Popup
- **Documents** : Pièces jointes (futur)

**Boutons d'action** :
- `action_submit` : Soumettre (visible si draft)
- `action_validate_or_reject` : Valider/Rejeter (visible si pending pour user)
- `action_cancel` : Annuler

### 3. Vue Approbateur (`workflow_approval_view_views.xml`)

**TransientModel** - Popup de validation

**Champs affichés** :
- Informations demande (readonly)
- Zone commentaire (obligatoire si rejet)
- Boutons : Approuver / Rejeter / Retourner

**Workflow** :
1. Clic sur "Valider/Rejeter" dans formulaire demande
2. Popup s'ouvre avec contexte
3. Validateur saisit commentaire
4. Choix : Approuver / Rejeter
5. Fermeture popup → Retour liste demandes

### 4. Popup Commentaires (`workflow_request_comment_views.xml`)

**Vue Tree des commentaires** :
- Colonnes : Date, Auteur, Niveau, Commentaire
- **PAS de colonne TYPE** (supprimée pour simplifier)
- Tri : Chronologique ascendant (du plus ancien au plus récent)
- Mode : Lecture seule (create="0", edit="0", delete="0")

**Décorateurs** :
- Bleu clair : Notes d'approbation (`approval_note`)
- Rouge clair : Motifs de rejet (`rejection_reason`)
- Orange clair : Demandes de retour (`return`)

### 5. Dashboard HTML (`workflow_dashboard.xml`)

**Composants** :
1. **Statistiques** (4 cartes) :
   - Total Demandes
   - En Attente pour Moi
   - Approuvées (30j)
   - Rejetées (30j)

2. **Tableau Demandes Récentes** :
   - 10 dernières demandes
   - Pagination avec boutons
   - Liens cliquables vers demandes

**Pagination** :
- Boutons "← Précédent" / "Suivant →"
- Styles dynamiques (désactivés si début/fin)
- Indicateur page actuelle

---

## 📁 Module Courrier

**Dossier** : `courrier/`

Module complémentaire pour gérer le courrier entrant/sortant.

**Modèle** : `workflow.courrier.entrant`

**Champs spécifiques** :
- `numero_courrier` : Numéro d'enregistrement
- `date_reception` : Date de réception
- `expediteur` : Expéditeur
- `objet` : Objet du courrier
- `type_courrier` : Entrant/Sortant
- `workflow_request_id` : Demande de workflow associée

**Intégration** :
- Le courrier peut déclencher un workflow de validation
- Lié au type "Courrier" dans `workflow.type`

---

## 🔐 Sécurité et Droits d'Accès

### Groupes (`security/workflow_security.xml`)

1. **Workflow User** : Utilisateur standard
   - Créer ses propres demandes
   - Voir ses demandes
   - Commenter ses demandes

2. **Workflow Manager** : Gestionnaire
   - Voir toutes les demandes
   - Configurer circuits et types
   - Gérer règles de routage

3. **Workflow Admin** : Administrateur
   - Accès complet
   - Gestion des droits
   - Configuration avancée

### Rules de Sécurité

**Enregistrement** : Un utilisateur peut :
- Voir ses propres demandes (créateur)
- Voir les demandes où il est validateur
- Managers voient tout

---

## 🧪 Données de Démonstration

**Fichier** : `data/workflow_demo_data.xml`

### Types de Workflow
1. **Demande de Crédit** (code: `credit`)
2. **Courrier** (code: `courrier`)

### Circuits de Validation

**Circuit Standard Crédit** :
- Niveau 10 : Agent Commercial (Jean Dupont, Marie Martin)
- Niveau 20 : Chef de Service (Pierre Durand, Sophie Bernard)
- Niveau 30 : Directeur (admin)

### Utilisateurs Démo

| Email | Mot de passe | Rôle | Niveau |
|-------|--------------|------|--------|
| jean.dupont@workflow.test | demo123 | Agent | 10 |
| marie.martin@workflow.test | demo123 | Agent | 10 |
| pierre.durand@workflow.test | demo123 | Chef | 20 |
| sophie.bernard@workflow.test | demo123 | Chef | 20 |
| admin@workflow.test | admin | Directeur | 30 |

### Scénario de Test

1. Se connecter avec `admin@workflow.test`
2. Créer une demande de crédit (montant: 500000)
3. Soumettre la demande
4. Se déconnecter et se connecter avec `jean.dupont@workflow.test`
5. Valider la demande (niveau Agent)
6. Se connecter avec `marie.martin@workflow.test`
7. Valider la demande (niveau Agent - 2ème validation du même niveau)
8. Se connecter avec `pierre.durand@workflow.test`
9. Valider (niveau Chef)
10. Se connecter avec `sophie.bernard@workflow.test`
11. Valider (niveau Chef - 2ème validation) → **Passe au Directeur**
12. Se connecter avec `admin@workflow.test`
13. Valider (niveau Directeur) → **Demande Approuvée**

---

## 🐛 Problèmes Connus et Solutions

### 1. Pagination ne s'affiche pas dans la liste

**Symptôme** : "Page 1 sur 2" apparaît mais pas de boutons < >

**Cause** : Problème d'affichage Odoo 17 avec pagination dans tree view

**Solution actuelle** :
- Pagination configurée dans `action` (limit="10")
- Indicateur de page visible
- Navigation possible via défiler

**Workaround** : Utiliser filtres pour réduire résultats

### 2. Python Format String Error dans Dashboard

**Symptôme** : `KeyError` avec conditionnels inline dans HTML

**Cause** : Python format() interprète `{condition}` comme placeholder

**Solution appliquée** :
```python
# ❌ AVANT (erreur)
html = '<button style="background: {\'red\' if page > 1 else \'gray\'}">

# ✅ APRÈS (correct)
prev_bg = '#0d6efd' if page > 1 else '#e9ecef'
html = '<button style="background: {0}">'.format(prev_bg)
```

Toujours pré-calculer les valeurs dynamiques avant insertion HTML.

### 3. Colonne TYPE toujours visible dans popup

**Symptôme** : `column_invisible="1"` ne fonctionne pas

**Solution** : Supprimer complètement le champ `comment_type` de la vue tree

**Note** : Les décorateurs fonctionnent toujours (définis au niveau `<tree>`)

### 4. Multi-validateur : Validation prématurée

**Symptôme** : Avec 2 chefs, la demande passe au directeur après 1 seule validation

**Cause** : Logique d'approbation ne vérifiait pas les autres approbations du même niveau

**Solution** : Ajout de la vérification `pending_at_current_level` dans `action_approve()`

---

## 🚀 Déploiement et Mise à Jour

### Connexion SSH

```bash
ssh -i "C:\Users\user\Desktop\wfssh\ssh-key-serveur-odoo-dev - Copie.key" ubuntu@130.61.235.163
```

### Mise à jour manuelle

```bash
# Arrêter Odoo
sudo systemctl stop odoo

# Mise à jour du module
sudo -u odoo /usr/bin/odoo -c /etc/odoo/odoo.conf -d odoo_2026_01_27 -u workflow --stop-after-init

# Redémarrer Odoo
sudo systemctl start odoo
```

### Voir les logs

```bash
sudo journalctl -u odoo -f
```

### Vérifier l'état du service

```bash
sudo systemctl status odoo
```

### Scripts automatisés

**Utiliser les scripts PowerShell** :
```powershell
# Déploiement complet
.\deployment\deploy.ps1

# Déployer un fichier
.\deployment\deploy-file.ps1 -FilePath "models\workflow_request.py"

# Redémarrer Odoo
.\deployment\restart.ps1

# Voir les logs
.\deployment\logs.ps1
```

**Documentation** : Voir `deployment/GUIDE_CURSOR.md`

---

## 📝 Commandes SQL Utiles

### Voir toutes les demandes

```sql
SELECT id, name, workflow_type_id, state, requester_id, montant 
FROM workflow_request 
ORDER BY create_date DESC;
```

### Voir les approbations en attente

```sql
SELECT wr.name, wl.name as level, ru.login as approver, wra.state
FROM workflow_request_approval wra
JOIN workflow_request wr ON wra.workflow_request_id = wr.id
JOIN workflow_level wl ON wra.workflow_level_id = wl.id
JOIN res_users ru ON wra.approver_id = ru.id
WHERE wra.state = 'pending'
ORDER BY wr.id, wl.sequence;
```

### Voir l'historique des commentaires d'une demande

```sql
SELECT wrc.create_date, ru.login, wrc.comment_type, wrc.message
FROM workflow_request_comment wrc
JOIN res_users ru ON wrc.user_id = ru.id
WHERE wrc.workflow_request_id = 1
ORDER BY wrc.create_date ASC;
```

### Statistiques par état

```sql
SELECT state, COUNT(*) as count
FROM workflow_request
GROUP BY state;
```

### Supprimer toutes les demandes (test)

```sql
DELETE FROM workflow_request_comment;
DELETE FROM workflow_request_approval;
DELETE FROM workflow_request;
ALTER SEQUENCE workflow_request_id_seq RESTART WITH 1;
```

---

## 🔄 Prochaines Évolutions

### Fonctionnalités en cours

- [x] Workflow crédit hiérarchique
- [x] Multi-validateur (attente tous validateurs d'un niveau)
- [x] Module courrier
- [x] Dashboard avec statistiques
- [x] Commentaires chronologiques
- [x] Vue Approbateur
- [x] Règles de routage conditionnelles
- [x] Multi-sélection demandes (actions groupées)

### Améliorations futures

- [ ] Notifications email automatiques
- [ ] Pièces jointes (documents)
- [ ] Workflows supplémentaires (Congés, Achats, Mails)
- [ ] Délégation de validation
- [ ] Rappels automatiques
- [ ] Rapports et analytics avancés
- [ ] API REST pour intégrations externes
- [ ] Signature électronique
- [ ] Historique des modifications (audit trail)
- [ ] Workflows parallèles (plusieurs branches)

---

## 📞 Support et Ressources

### Documentation

- **README principal** : `README.md`
- **Guide Cursor AI** : `deployment/GUIDE_CURSOR.md`
- **Scripts PowerShell** : `deployment/DEPLOIEMENT.md`
- **Ce document** : Documentation technique complète

### Informations Serveur

- **Serveur** : ubuntu@130.61.235.163
- **Base de données** : odoo_2026_01_27
- **Version Odoo** : 17.0+e (Enterprise)
- **Chemin module** : `/opt/odoo/custom_addons/workflow`
- **Clé SSH** : `C:\Users\user\Desktop\wfssh\ssh-key-serveur-odoo-dev - Copie.key`

### GitHub

- **Repository** : https://github.com/kiemdegerald/Workflow.git
- **Branche principale** : main

### Contact

Pour toute question technique, consulter la documentation ou les logs Odoo.

---

**Dernière mise à jour** : 1er mars 2026  
**Version du document** : 2.0
