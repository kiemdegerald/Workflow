# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

class WorkflowDashboard(models.TransientModel):
    _name = 'workflow.dashboard'
    _description = 'Tableau de bord Workflow'

    stats_html = fields.Html('Statistiques', compute='_compute_stats_html')
    page = fields.Integer('Page courante', default=1)
    total_pages = fields.Integer('Total pages', compute='_compute_stats_html')
    has_previous = fields.Boolean('A page précédente', compute='_compute_stats_html')
    has_next = fields.Boolean('A page suivante', compute='_compute_stats_html')

    @api.model
    def action_open_dashboard(self):
        """Créer et ouvrir le dashboard"""
        dashboard = self.create({'page': 1})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tableau de bord',
            'res_model': 'workflow.dashboard',
            'view_mode': 'form',
            'res_id': dashboard.id,
            'target': 'current',
        }
    
    def action_previous_page(self):
        """Page précédente"""
        if self.page > 1:
            self.page -= 1
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'workflow.dashboard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }
    
    def action_next_page(self):
        """Page suivante"""
        if self.has_next:
            self.page += 1
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'workflow.dashboard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    @api.depends('page')
    def _compute_stats_html(self):
        """Génère le HTML du dashboard avec statistiques et demandes récentes"""
        for rec in self:
            Request = self.env['workflow.request']
            
            # Statistiques
            total_requests = Request.search_count([])
            in_progress_requests = Request.search_count([('state', 'in', ['submitted', 'in_progress'])])
            approved_requests = Request.search_count([('state', '=', 'approved')])
            rejected_requests = Request.search_count([('state', '=', 'rejected')])
            
            # Calcul des pourcentages
            approval_rate = int((approved_requests / total_requests * 100)) if total_requests > 0 else 0
            
            # Pagination
            page = rec.page or 1
            limit = 10
            offset = (page - 1) * limit
            total_pages = (total_requests + limit - 1) // limit if total_requests > 0 else 1
            
            # Mettre à jour les champs de pagination
            rec.total_pages = total_pages
            rec.has_previous = page > 1
            rec.has_next = page < total_pages
            
            # Demandes récentes avec pagination
            recent_requests = Request.search([], order='create_date desc', limit=limit, offset=offset)
            
            # Construction du HTML moderne
            html = '''
                <div style="padding: 30px; background: #f8f9fa;">
                    <!-- En-tête -->
                    <div style="margin-bottom: 30px;">
                        <h2 style="font-size: 24px; font-weight: 700; margin: 0 0 8px 0; color: #1a1a1a;">Tableau de bord</h2>
                        <p style="color: #6c757d; margin: 0; font-size: 14px;">Vue d'ensemble des demandes et validations en cours</p>
                    </div>
                    
                    <!-- Cartes statistiques -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 30px;">
                        <!-- Carte Total -->
                        <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                                <div>
                                    <div style="color: #6c757d; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">TOTAL DEMANDES</div>
                                    <div style="font-size: 36px; font-weight: 700; color: #1a1a1a;">{0}</div>
                                </div>
                                <div style="width: 48px; height: 48px; background: #e7f0ff; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">📋</div>
                            </div>
                            <div style="color: #28a745; font-size: 13px; font-weight: 600;">↗ 100% ce mois</div>
                        </div>
                        
                        <!-- Carte En cours -->
                        <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                                <div>
                                    <div style="color: #6c757d; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">EN COURS</div>
                                    <div style="font-size: 36px; font-weight: 700; color: #1a1a1a;">{1}</div>
                                </div>
                                <div style="width: 48px; height: 48px; background: #fff3e0; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">⏳</div>
                            </div>
                            <div style="color: #6c757d; font-size: 13px; font-weight: 600;">→ Stable</div>
                        </div>
                        
                        <!-- Carte Approuvées -->
                        <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                                <div>
                                    <div style="color: #6c757d; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">APPROUVÉES</div>
                                    <div style="font-size: 36px; font-weight: 700; color: #1a1a1a;">{2}</div>
                                </div>
                                <div style="width: 48px; height: 48px; background: #e8f5e9; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">✓</div>
                            </div>
                            <div style="color: #28a745; font-size: 13px; font-weight: 600;">↗ {4}% taux d'approbation</div>
                        </div>
                        
                        <!-- Carte Refusées -->
                        <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                                <div>
                                    <div style="color: #6c757d; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">REFUSÉES</div>
                                    <div style="font-size: 36px; font-weight: 700; color: #1a1a1a;">{3}</div>
                                </div>
                                <div style="width: 48px; height: 48px; background: #ffebee; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">✗</div>
                            </div>
                            <div style="color: #6c757d; font-size: 13px; font-weight: 600;">↘ 0% vs mois dernier</div>
                        </div>
                    </div>
                    
                    <!-- Section demandes récentes -->
                    <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                            <h5 style="margin: 0; font-size: 18px; font-weight: 700; color: #1a1a1a;">Demandes récentes</h5>
                            <a href="/web#model=workflow.request&amp;view_type=list" style="background: #0d6efd; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px; display: inline-block;">+ Nouvelle demande</a>
                        </div>
                        
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="border-bottom: 2px solid #dee2e6;">
                                    <th style="padding: 12px; text-align: left; color: #6c757d; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">RÉFÉRENCE</th>
                                    <th style="padding: 12px; text-align: left; color: #6c757d; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">DEMANDEUR</th>
                                    <th style="padding: 12px; text-align: left; color: #6c757d; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">CLIENT</th>
                                    <th style="padding: 12px; text-align: left; color: #6c757d; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">MONTANT</th>
                                    <th style="padding: 12px; text-align: left; color: #6c757d; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">TYPE CRÉDIT</th>
                                    <th style="padding: 12px; text-align: left; color: #6c757d; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">STATUT</th>
                                    <th style="padding: 12px; text-align: left; color: #6c757d; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">DATE</th>
                                </tr>
                            </thead>
                            <tbody>
            '''.format(total_requests, in_progress_requests, approved_requests, rejected_requests, approval_rate)
            
            # Ajout des lignes de demandes
            state_labels = {
                'draft': ('● Brouillon', '#6c757d'),
                'submitted': ('● Soumis', '#0d6efd'),
                'in_progress': ('● En cours', '#ffc107'),
                'approved': ('● Approuvée', '#28a745'),
                'rejected': ('● Rejetée', '#dc3545'),
            }
            
            for req in recent_requests:
                state_label, state_color = state_labels.get(req.state, ('● ' + req.state, '#6c757d'))
                create_date = fields.Datetime.from_string(req.create_date).strftime('%d/%m/%Y')
                
                # Formatage du montant si disponible (depuis les champs personnalisés)
                amount_display = '-'
                if hasattr(req, 'amount') and req.amount:
                    amount_display = '{:,.0f} FCFA'.format(req.amount).replace(',', ' ')
                
                html += '''
                                <tr style="border-bottom: 1px solid #f0f0f0;">
                                    <td style="padding: 16px 12px;"><strong style="color: #1a1a1a;">{0}</strong></td>
                                    <td style="padding: 16px 12px; color: #495057;">{1}</td>
                                    <td style="padding: 16px 12px; color: #495057;">{2}</td>
                                    <td style="padding: 16px 12px; color: #495057; font-weight: 600;">{3}</td>
                                    <td style="padding: 16px 12px; color: #495057;">{4}</td>
                                    <td style="padding: 16px 12px;"><span style="color: {5}; font-weight: 600; font-size: 13px;">{6}</span></td>
                                    <td style="padding: 16px 12px; color: #6c757d; font-size: 13px;">{7}</td>
                                </tr>
                '''.format(
                    req.name,
                    req.requester_id.name if req.requester_id else 'Administrator',
                    req.subject or '-',
                    amount_display,
                    req.workflow_type_id.name if req.workflow_type_id else '-',
                    state_color,
                    state_label,
                    create_date
                )
            
            html += '''
                            </tbody>
                        </table>
                        <div style="margin-top: 20px; padding: 15px; text-align: center; color: #6c757d; font-size: 14px; border-top: 1px solid #dee2e6;">
                            Page {0} sur {1}
                        </div>
                    </div>
                </div>
            '''.format(page, total_pages)
            
            rec.stats_html = html
