# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkflowRequest(models.Model):
    _name = 'workflow.request'
    _description = 'Demande de Workflow'

    name = fields.Char(string='Référence', required=True, default='Nouveau')
    workflow_type_id = fields.Many2one('workflow.type', string='Type de Workflow', required=True, ondelete='restrict')
    workflow_definition_id = fields.Many2one('workflow.definition', string='Circuit de Validation', ondelete='restrict')
    requester_id = fields.Many2one('res.users', string='Demandeur', required=True, default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('in_progress', 'En cours'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('cancelled', 'Annulé'),
    ], string='État', required=True, default='draft')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Actif', default=True)
