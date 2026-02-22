# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkflowDefinition(models.Model):
    _name = 'workflow.definition'
    _description = 'Définition de Circuit de Workflow'
    _order = 'code, name'

    name = fields.Char(string='Nom du Circuit', required=True)
    code = fields.Char(string='Code', required=True)
    workflow_type_id = fields.Many2one('workflow.type', string='Type de Workflow', required=True, ondelete='restrict')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Actif', default=True)
    
    # Relation avec les niveaux
    level_ids = fields.One2many('workflow.level', 'workflow_definition_id', string='Niveaux de Validation')
