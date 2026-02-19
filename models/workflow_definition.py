# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkflowDefinition(models.Model):
    _name = 'workflow.definition'
    _description = 'Définition de Circuit de Workflow'

    name = fields.Char(string='Nom du Circuit', required=True)
    code = fields.Char(string='Code', required=True)
    workflow_type_id = fields.Many2one('workflow.type', string='Type de Workflow', required=True, ondelete='restrict')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Actif', default=True)
