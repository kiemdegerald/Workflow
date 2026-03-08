# -*- coding: utf-8 -*-

import re
import unicodedata

from odoo import models, fields, api
from odoo.exceptions import ValidationError


def _sanitize_code(value):
    """Convertit un nom en code technique : majuscules, sans accents, sans espaces."""
    # Supprimer les accents
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    # Majuscules, garder uniquement lettres/chiffres/underscores
    value = re.sub(r'[^\w]', '_', value.strip().upper())
    # Supprimer underscores multiples et ceux en début/fin
    value = re.sub(r'_+', '_', value).strip('_')
    return value


class WorkflowType(models.Model):
    _name = 'workflow.type'
    _description = 'Type de Workflow'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nom', required=True, tracking=True)
    code = fields.Char(
        string='Code technique',
        required=True,
        tracking=True,
        help="Généré automatiquement depuis le nom. Référence interne.",
    )
    category = fields.Selection([
        ('credit',   '💳 Crédit Bancaire'),
        ('courrier', '📬 Courrier Entrant'),
        ('other',    '📋 Autre'),
    ], string='Catégorie', required=True, default='other', tracking=True,
       help="Détermine dans quel tableau de bord et quelle liste ce type apparaît.")
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Actif', default=True, tracking=True)
    custom_field_ids = fields.One2many(
        'workflow.custom.field',
        'workflow_type_id',
        string='Champs du formulaire',
        help='Champs personnalisés que l\'utilisateur devra remplir lors de la création d\'une demande de ce type.',
    )

    @api.onchange('name')
    def _onchange_name_generate_code(self):
        """Génère automatiquement le code depuis le nom (aperçu client-side)."""
        if self.name:
            self.code = _sanitize_code(self.name)

    @api.model_create_multi
    def create(self, vals_list):
        """Génère le code côté serveur si absent (sécurité supplémentaire)."""
        for vals in vals_list:
            if not vals.get('code') and vals.get('name'):
                vals['code'] = _sanitize_code(vals['name'])
        return super().create(vals_list)

    @api.constrains('code')
    def _check_code_format(self):
        """Vérifie que le code ne contient que des caractères valides."""
        for record in self:
            if record.code and not re.match(r'^[A-Z0-9_]+$', record.code):
                raise ValidationError(
                    f"Le code « {record.code} » est invalide. "
                    "Il doit contenir uniquement des majuscules, chiffres et underscores (ex: CREDIT, COURRIER_ENTRANT)."
                )

    @api.constrains('code')
    def _check_code_unique(self):
        """Vérifie que le code est unique."""
        for record in self:
            duplicate = self.search([('code', '=', record.code), ('id', '!=', record.id)], limit=1)
            if duplicate:
                raise ValidationError(
                    f"Le code « {record.code} » est déjà utilisé par le type « {duplicate.name} »."
                )
