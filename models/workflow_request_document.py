# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkflowRequestDocument(models.Model):
    _name = 'workflow.request.document'
    _description = 'Document Attaché à une Demande de Workflow'

    name = fields.Char(string='Nom du Document', required=True)
    workflow_request_id = fields.Many2one('workflow.request', string='Demande de Workflow', required=True, ondelete='cascade')
    attachment_id = fields.Many2one('ir.attachment', string='Pièce Jointe', ondelete='cascade')
    document_type = fields.Char(string='Type de Document')
    description = fields.Text(string='Description')
