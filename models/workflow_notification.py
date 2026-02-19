# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkflowNotification(models.Model):
    _name = 'workflow.notification'
    _description = 'Notification de Workflow'

    name = fields.Char(string='Sujet', required=True)
    workflow_request_id = fields.Many2one('workflow.request', string='Demande de Workflow', ondelete='cascade')
    recipient_id = fields.Many2one('res.users', string='Destinataire', required=True, ondelete='cascade')
    message = fields.Text(string='Message', required=True)
    notification_type = fields.Selection([
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('approval_request', 'Demande d\'Approbation'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ], string='Type de Notification', required=True, default='info')
    is_read = fields.Boolean(string='Lu', default=False)
    sent_date = fields.Datetime(string='Date d\'Envoi', default=fields.Datetime.now)
