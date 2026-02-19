# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkflowType(models.Model):
    _name = 'workflow.type'
    _description = 'Type de Workflow'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nom', required=True, tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Actif', default=True, tracking=True)
