# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkflowAuditLog(models.Model):
    _name = 'workflow.audit.log'
    _description = 'Journal d\'Audit de Workflow'

    name = fields.Char(string='Référence', required=True)
    workflow_request_id = fields.Many2one('workflow.request', string='Demande de Workflow', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Utilisateur', required=True, ondelete='restrict')
    action = fields.Char(string='Action', required=True)
    old_value = fields.Text(string='Ancienne Valeur')
    new_value = fields.Text(string='Nouvelle Valeur')
    timestamp = fields.Datetime(string='Horodatage', required=True, default=fields.Datetime.now)
    details = fields.Text(string='Détails')
