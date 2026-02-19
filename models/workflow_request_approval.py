# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkflowRequestApproval(models.Model):
    _name = 'workflow.request.approval'
    _description = 'Approbation de Demande de Workflow'

    name = fields.Char(string='Référence', required=True, default='Nouvelle Approbation')
    workflow_request_id = fields.Many2one('workflow.request', string='Demande de Workflow', required=True, ondelete='cascade')
    workflow_level_id = fields.Many2one('workflow.level', string='Niveau de Validation', required=True, ondelete='restrict')
    approver_id = fields.Many2one('res.users', string='Approbateur', required=True)
    state = fields.Selection([
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('returned', 'Retourné'),
    ], string='État', required=True, default='pending')
    comments = fields.Text(string='Commentaires')
