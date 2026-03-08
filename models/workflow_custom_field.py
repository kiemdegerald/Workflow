# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkflowCustomField(models.Model):
    _name = 'workflow.custom.field'
    _description = 'Champ Personnalisé de Workflow'
    _order = 'sequence, id'

    name = fields.Char(string='Nom du Champ', required=True)
    workflow_type_id = fields.Many2one(
        'workflow.type',
        string='Type de Workflow',
        required=True,
        ondelete='cascade',
    )
    field_type = fields.Selection([
        ('char', 'Texte Court'),
        ('text', 'Texte Long'),
        ('integer', 'Entier'),
        ('float', 'Décimal'),
        ('boolean', 'Oui / Non'),
        ('date', 'Date'),
        ('datetime', 'Date et Heure'),
        ('selection', 'Liste déroulante'),
    ], string='Type de Champ', required=True, default='char')
    required = fields.Boolean(string='Obligatoire', default=False)
    active = fields.Boolean(string='Actif', default=True)
    sequence = fields.Integer(string='Séquence', default=10)
    placeholder = fields.Char(string='Texte indicatif', help='Exemple affiché dans le champ vide')
    selection_options = fields.Text(
        string='Options (une par ligne)',
        help='Pour le type Liste déroulante : saisissez une option par ligne',
    )

    def get_selection_options_list(self):
        """Retourne la liste des options pour un champ de type sélection."""
        self.ensure_one()
        if not self.selection_options:
            return []
        return [line.strip() for line in self.selection_options.split('\n') if line.strip()]
