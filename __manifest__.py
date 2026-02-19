# -*- coding: utf-8 -*-
{
    'name': 'Workflow',
    'version': '17.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Système générique de validation hiérarchique multi-niveaux pour institutions financières',
    'description': """
        Workflow - Gestion de Validation Multi-Niveaux
        ================================================
        
        Module générique de gestion de workflows de validation hiérarchique
        conçu pour les institutions bancaires et financières.
        
        Fonctionnalités principales :
        -----------------------------
        * Configuration flexible de circuits de validation (A/B/C/D...)
        * Routage automatique selon règles métier configurables
        * Validation multi-niveaux avec logique de retour N-1
        * Traçabilité complète des approbations
        * Gestion de pièces jointes par demande
        * Système de notifications intégré
        * Journal d'audit immuable
        * Champs personnalisés dynamiques
        
        Cas d'usage :
        -------------
        * Validation de crédits bancaires
        * Processus d'approbation de congés
        * Validation de bons de commande
        * Demandes de mission
        * Tout processus métier nécessitant une validation hiérarchique
        
        Technique :
        -----------
        * Compatible Odoo Enterprise v17
        * Architecture modulaire (11 modèles)
        * Intégration complète avec le système de messagerie Odoo
        * Support multi-entreprises
    """,
    'author': 'Liceli Technologies',
    'website': '',
    'license': 'OPL-1',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        # Security
        'security/workflow_security.xml',
        'security/ir.model.access.csv',
        
        # Views
        'views/workflow_type_views.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
