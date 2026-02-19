# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WorkflowRequest(models.Model):
    _name = 'workflow.request'
    _description = 'Demande de Workflow'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    # Référence
    name = fields.Char(
        string='Référence', 
        required=True, 
        default='Nouveau', 
        copy=False,
        readonly=True,
        tracking=True
    )
    
    # Informations client
    client_number = fields.Char(string='Numéro Client', tracking=True)
    account_number = fields.Char(string='Numéro de compte', tracking=True)
    client_name = fields.Char(string='Nom du client', tracking=True)
    credit_type = fields.Selection([
        ('salary', 'Crédit salarié'),
        ('housing', 'Crédit habitat'),
        ('consumption', 'Crédit consommation'),
        ('business', 'Crédit entreprise'),
        ('other', 'Autre'),
    ], string='Type de crédit', tracking=True)
    
    # Détails financiers
    subject = fields.Char(string='Objet de la demande', required=True, tracking=True)
    amount = fields.Monetary(string='Montant demandé', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id)
    duration_months = fields.Integer(string='Durée (mois)', tracking=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Urgent'),
        ('2', 'Critique'),
    ], string='Priorité', default='0', tracking=True)
    description = fields.Text(string='Description / Justification', tracking=True)
    
    # Configuration workflow
    workflow_type_id = fields.Many2one('workflow.type', string='Type de Workflow', required=True, ondelete='restrict')
    workflow_definition_id = fields.Many2one('workflow.definition', string='Circuit de Validation', ondelete='restrict')
    requester_id = fields.Many2one('res.users', string='Demandeur', required=True, default=lambda self: self.env.user, tracking=True)
    
    # Statut
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('in_progress', 'En cours'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('cancelled', 'Annulé'),
    ], string='État', required=True, default='draft', tracking=True)
    
    # Pièces jointes
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'workflow_request_attachment_rel',
        'request_id',
        'attachment_id',
        string='Pièces jointes'
    )
    attachment_count = fields.Integer(string='Nombre de pièces', compute='_compute_attachment_count')
    
    active = fields.Boolean(string='Actif', default=True)
    
    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = len(record.attachment_ids)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('workflow.request') or 'REQ/NEW'
        return super(WorkflowRequest, self).create(vals)
    
    @api.model
    def get_dashboard_data(self):
        """
        Récupère les données pour le tableau de bord
        Retourne un dictionnaire avec les statistiques et les demandes récentes
        """
        from datetime import datetime, timedelta
        
        # Date du début du mois actuel
        now = datetime.now()
        first_day_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Date du mois précédent
        if now.month == 1:
            first_day_last_month = first_day_current_month.replace(year=now.year - 1, month=12)
        else:
            first_day_last_month = first_day_current_month.replace(month=now.month - 1)

        # Statistiques
        total = self.search_count([])
        total_current_month = self.search_count([
            ('create_date', '>=', first_day_current_month.strftime('%Y-%m-%d'))
        ])
        total_last_month = self.search_count([
            ('create_date', '>=', first_day_last_month.strftime('%Y-%m-%d')),
            ('create_date', '<', first_day_current_month.strftime('%Y-%m-%d'))
        ])
        
        if total_last_month > 0:
            total_trend = round(((total_current_month - total_last_month) / total_last_month) * 100)
        else:
            total_trend = 100 if total_current_month > 0 else 0

        in_progress = self.search_count([('state', 'in', ['submitted', 'in_progress'])])
        approved = self.search_count([('state', '=', 'approved')])
        rejected = self.search_count([('state', '=', 'rejected')])
        
        total_processed = approved + rejected
        approval_rate = round((approved / total_processed * 100)) if total_processed > 0 else 0
        rejection_trend = -5
        
        stats = {
            'total': total,
            'total_trend': total_trend,
            'in_progress': in_progress,
            'approved': approved,
            'rejected': rejected,
            'approval_rate': approval_rate,
            'rejection_trend': rejection_trend,
        }
        
        # Demandes récentes
        credit_types = {
            'salary': 'Crédit salaire',
            'housing': 'Crédit logement',
            'consumption': 'Crédit consommation',
            'business': 'Crédit entreprise',
            'other': 'Autre',
        }
        
        state_labels = {
            'draft': 'Brouillon',
            'submitted': 'Soumise',
            'in_progress': 'En cours',
            'approved': 'Approuvée',
            'rejected': 'Refusée',
            'cancelled': 'Annulée',
        }
        
        requests = self.search([], order='create_date desc', limit=10)
        recent_requests = []
        
        for req in requests:
            recent_requests.append({
                'id': req.id,
                'name': req.name or 'Brouillon',
                'requester': req.requester_id.name if req.requester_id else 'Système',
                'client_name': req.client_name,
                'amount': req.amount or 0,
                'credit_type_label': credit_types.get(req.credit_type, '-'),
                'state': req.state,
                'state_label': state_labels.get(req.state, req.state.capitalize()),
                'date': req.create_date.strftime('%d/%m/%Y') if req.create_date else '-',
            })
        
        return {
            'stats': stats,
            'recent_requests': recent_requests,
        }
