# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkflowRequestApproval(models.Model):
    _name = 'workflow.request.approval'
    _description = 'Approbation de Demande de Workflow'

    name = fields.Char(string='Référence', required=True, default='Nouvelle Approbation')
    workflow_request_id = fields.Many2one('workflow.request', string='Demande de Workflow', required=True, ondelete='cascade')
    workflow_level_id = fields.Many2one('workflow.level', string='Niveau de Validation', required=True, ondelete='restrict')
    level_id = fields.Many2one('workflow.level', string='Niveau', related='workflow_level_id', readonly=True)
    approver_id = fields.Many2one('res.users', string='Approbateur', required=True)
    state = fields.Selection([
        ('waiting', 'En attente du niveau précédent'),
        ('pending', 'En attente de validation'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('returned', 'Retourné'),
    ], string='État', required=True, default='waiting')
    comments = fields.Text(string='Commentaires')

    # Documents joints lors de l'action (pièces justificatives, documents manquants, etc.)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'workflow_approval_attachment_rel',
        'approval_id',
        'attachment_id',
        string='Documents joints',
    )

    def action_open_from_selector(self):
        """Ouvre la vue approbateur pour cette demande spécifique"""
        self.ensure_one()

        # Vérifier si l'étape a des actions configurées
        level = self.workflow_level_id
        has_actions = bool(level and level.action_ids)

        # Créer un enregistrement transient pour la vue approbateur
        approval_view = self.env['workflow.approval.view'].create({
            'request_id': self.workflow_request_id.id,
            'current_approval_id': self.id,
            'has_configured_actions': has_actions,
            'comment': '',
        })
        
        return {
            'name': 'Vue Approbateur',
            'type': 'ir.actions.act_window',
            'res_model': 'workflow.approval.view',
            'view_mode': 'form',
            'res_id': approval_view.id,
            'target': 'new',
            'context': self.env.context,
        }
