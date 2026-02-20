# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta


class WorkflowDashboardController(http.Controller):
    """
    Contrôleur pour le tableau de bord Workflow
    Fournit les statistiques et données pour l'interface dashboard
    """

    @http.route('/workflow/dashboard', type='http', auth='user', website=True)
    def workflow_dashboard(self, page=1, **kwargs):
        """
        Affiche le tableau de bord avec statistiques et demandes récentes
        """
        # Pagination
        try:
            page = int(page)
        except:
            page = 1
        
        limit = 10  # Nombre d'éléments par page
        offset = (page - 1) * limit
        
        # Récupération du modèle
        WorkflowRequest = request.env['workflow.request']
        
        # Calcul des statistiques
        stats = self._compute_statistics(WorkflowRequest)
        
        # Comptage total pour la pagination
        total_requests = WorkflowRequest.search_count([])
        total_pages = (total_requests + limit - 1) // limit  # Arrondi supérieur
        
        # Récupération des demandes récentes avec pagination
        recent_requests = self._get_recent_requests(WorkflowRequest, limit=limit, offset=offset)
        
        return request.render('workflow.workflow_dashboard', {
            'stats': stats,
            'recent_requests': recent_requests,
            'page': page,
            'total_pages': total_pages,
            'total_requests': total_requests,
        })

    def _compute_statistics(self, model):
        """
        Calcule les statistiques pour les cartes du dashboard
        """
        # Date du début du mois actuel
        now = datetime.now()
        first_day_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Date du mois précédent
        if now.month == 1:
            first_day_last_month = first_day_current_month.replace(year=now.year - 1, month=12)
        else:
            first_day_last_month = first_day_current_month.replace(month=now.month - 1)

        # Total de toutes les demandes
        total = model.search_count([])
        
        # Demandes du mois actuel
        total_current_month = model.search_count([
            ('create_date', '>=', first_day_current_month.strftime('%Y-%m-%d'))
        ])
        
        # Demandes du mois précédent
        total_last_month = model.search_count([
            ('create_date', '>=', first_day_last_month.strftime('%Y-%m-%d')),
            ('create_date', '<', first_day_current_month.strftime('%Y-%m-%d'))
        ])
        
        # Calcul de la tendance mensuelle
        if total_last_month > 0:
            total_trend = round(((total_current_month - total_last_month) / total_last_month) * 100)
        else:
            total_trend = 100 if total_current_month > 0 else 0

        # Demandes en cours
        in_progress = model.search_count([('state', 'in', ['submitted', 'in_progress'])])
        
        # Demandes approuvées
        approved = model.search_count([('state', '=', 'approved')])
        
        # Demandes refusées
        rejected = model.search_count([('state', '=', 'rejected')])
        
        # Taux d'approbation
        total_processed = approved + rejected
        approval_rate = round((approved / total_processed * 100)) if total_processed > 0 else 0
        
        # Tendance des rejets (fictive pour l'instant)
        rejection_trend = -5  # À améliorer avec vrais calculs plus tard

        return {
            'total': total,
            'total_trend': total_trend,
            'in_progress': in_progress,
            'approved': approved,
            'rejected': rejected,
            'approval_rate': approval_rate,
            'rejection_trend': rejection_trend,
        }

    def _get_recent_requests(self, model, limit=10, offset=0):
        """
        Récupère les demandes récentes avec leurs informations formatées
        """
        # Dictionnaire de traduction des types de crédit
        credit_types = {
            'salary': 'Crédit salaire',
            'housing': 'Crédit logement',
            'consumption': 'Crédit consommation',
            'business': 'Crédit entreprise',
            'other': 'Autre',
        }
        
        # Dictionnaire de traduction des statuts
        state_labels = {
            'draft': 'Brouillon',
            'submitted': 'Soumise',
            'in_progress': 'En cours',
            'approved': 'Approuvée',
            'rejected': 'Refusée',
            'cancelled': 'Annulée',
        }
        
        # Recherche des demandes récentes avec pagination
        requests = model.search([], order='create_date desc', limit=limit, offset=offset)
        
        result = []
        for req in requests:
            result.append({
                'name': req.name or 'Brouillon',
                'requester': req.requester_id.name if req.requester_id else 'Système',
                'client_name': req.client_name,
                'amount': req.amount or 0,
                'credit_type_label': credit_types.get(req.credit_type, '-'),
                'state': req.state,
                'state_label': state_labels.get(req.state, req.state.capitalize()),
                'date': req.create_date.strftime('%d/%m/%Y') if req.create_date else '-',
            })
        
        return result
