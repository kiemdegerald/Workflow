# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkflowRequestComment(models.Model):
    _name = 'workflow.request.comment'
    _description = 'Commentaire d\'Échange de Demande de Workflow'
    _order = 'create_date desc, exchange_number desc'

    name = fields.Char(string='Référence', required=True, default='Nouveau Commentaire')
    request_id = fields.Many2one('workflow.request', string='Demande de Workflow', required=True, ondelete='cascade', index=True)
    approval_id = fields.Many2one('workflow.request.approval', string='Ligne d\'Approbation', ondelete='set null', index=True)
    user_id = fields.Many2one('res.users', string='Auteur', required=True, default=lambda self: self.env.user, ondelete='restrict')
    author_level_sequence = fields.Integer(string='Niveau de l\'Auteur')
    comment_type = fields.Selection([
        ('return', 'Retour avec Demande de Correction'),
        ('response', 'Réponse à un Retour'),
        ('clarification', 'Demande de Clarification'),
        ('information', 'Information'),
        ('rejection_reason', 'Justification de Rejet'),
        ('approval_note', 'Note d\'Approbation'),
    ], string='Type de Commentaire', required=True, default='information')
    subject = fields.Char(string='Objet')
    message = fields.Text(string='Message', required=True)
    returned_from_level = fields.Integer(string='Retourné depuis le Niveau')
    returned_to_level = fields.Integer(string='Retourné vers le Niveau')
    exchange_number = fields.Integer(string='Numéro d\'Échange', default=1, help='Compteur d\'allers-retours pour cette demande')
    is_internal = fields.Boolean(string='Commentaire Interne', default=False, help='Visible uniquement par les validateurs')
    create_date = fields.Datetime(string='Date de Création', readonly=True)
