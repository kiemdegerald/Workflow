# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkflowRoutingRule(models.Model):
    _name = 'workflow.routing.rule'
    _description = 'Règle de Routage Automatique'

    name = fields.Char(string='Nom de la Règle', required=True)
    workflow_type_id = fields.Many2one('workflow.type', string='Type de Workflow', required=True, ondelete='cascade')
    workflow_definition_id = fields.Many2one('workflow.definition', string='Circuit de Destination', required=True, ondelete='restrict')
    sequence = fields.Integer(string='Priorité', required=True, default=10)
    active = fields.Boolean(string='Actif', default=True)
