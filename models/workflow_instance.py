# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkflowInstance(models.Model):
    _name = 'workflow.instance'
    _description = 'Instance de Workflow en Cours'

    name = fields.Char(string='Référence', required=True)
    workflow_request_id = fields.Many2one('workflow.request', string='Demande de Workflow', required=True, ondelete='cascade')
    workflow_definition_id = fields.Many2one('workflow.definition', string='Circuit Actif', required=True, ondelete='restrict')
    current_level_id = fields.Many2one('workflow.level', string='Niveau Actuel', ondelete='restrict')
    state = fields.Selection([
        ('active', 'Actif'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='État', required=True, default='active')
