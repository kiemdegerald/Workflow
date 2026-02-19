# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkflowCustomField(models.Model):
    _name = 'workflow.custom.field'
    _description = 'Champ Personnalisé de Workflow'

    name = fields.Char(string='Nom du Champ', required=True)
    workflow_type_id = fields.Many2one('workflow.type', string='Type de Workflow', required=True, ondelete='cascade')
    field_type = fields.Selection([
        ('char', 'Texte'),
        ('text', 'Texte Long'),
        ('integer', 'Entier'),
        ('float', 'Décimal'),
        ('boolean', 'Booléen'),
        ('date', 'Date'),
        ('datetime', 'Date et Heure'),
        ('selection', 'Sélection'),
    ], string='Type de Champ', required=True, default='char')
    required = fields.Boolean(string='Obligatoire', default=False)
    active = fields.Boolean(string='Actif', default=True)
