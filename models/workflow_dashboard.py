# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

class WorkflowDashboard(models.TransientModel):
    _name = 'workflow.dashboard'
    _description = 'Tableau de bord Workflow'

    name = fields.Char(default='Tableau de bord')
    # mode = credit (par défaut) ou courrier
    mode = fields.Selection([
        ('credit', 'Crédit bancaire'),
        ('courrier', 'Courrier entrant'),
    ], string='Type de tableau de bord', default='credit')

    stats_html = fields.Html('Statistiques', compute='_compute_stats_html')
    page = fields.Integer('Page courante', default=1)

    @api.model
    def action_open_dashboard(self, page=1, mode='credit'):
        """Créer et ouvrir le dashboard (crédit ou courrier)."""
        title = 'Tableau de bord Crédit' if mode == 'credit' else 'Tableau de bord Courrier'
        dashboard = self.create({
            'page': page,
            'mode': mode,
            'name': title,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': title,
            'res_model': 'workflow.dashboard',
            'view_mode': 'form',
            'res_id': dashboard.id,
            'target': 'current',
        }
    
    def action_switch_to_courrier(self):
        """Basculer vers le tableau de bord Courrier (section Courrier du module Workflow)."""
        action = self.action_open_dashboard(page=1, mode='courrier')
        action['menu_id'] = self.env.ref('workflow.menu_courrier_section').id
        return action

    def action_switch_to_credit(self):
        """Basculer vers le tableau de bord Crédit (section Crédit du module Workflow)."""
        action = self.action_open_dashboard(page=1, mode='credit')
        action['menu_id'] = self.env.ref('workflow.menu_credit_section').id
        return action

    def action_previous_page(self):
        """Page précédente"""
        if self.page <= 1:
            return
        return self.action_open_dashboard(page=self.page - 1, mode=self.mode or 'credit')
    
    def action_next_page(self):
        """Page suivante"""
        mode = self.mode or 'credit'
        if mode == 'courrier':
            Model = self.env['workflow.courrier.entrant']
            total = Model.search_count([])
        else:
            Request = self.env['workflow.request']
            total = Request.search_count([('workflow_type_id.category', '=', 'credit')])

        total_pages = max(1, (total + 9) // 10)
        if self.page >= total_pages:
            return
        return self.action_open_dashboard(page=self.page + 1, mode=mode)

    @api.depends('page', 'mode')
    def _compute_stats_html(self):
        """Génère le HTML du dashboard avec statistiques et listes récentes,
        en séparant Crédit et Courrier.
        """
        for rec in self:
            mode = rec.mode or 'credit'
            page = rec.page or 1
            limit = 10
            offset = (page - 1) * limit

            # ── TABLEAU DE BORD CRÉDIT ─────────────────────────────────────
            if mode == 'credit':
                Request = self.env['workflow.request']
                base_domain = [('workflow_type_id.category', '=', 'credit')]

                total_requests = Request.search_count(base_domain)
                in_progress_requests = Request.search_count(base_domain + [('state', 'in', ['submitted', 'in_progress'])])
                approved_requests = Request.search_count(base_domain + [('state', '=', 'approved')])
                rejected_requests = Request.search_count(base_domain + [('state', '=', 'rejected')])

                approval_rate = int((approved_requests / total_requests * 100)) if total_requests > 0 else 0
                total_pages = (total_requests + limit - 1) // limit if total_requests > 0 else 1

                recent_requests = Request.search(base_domain, order='create_date desc', limit=limit, offset=offset)

                html = '''
                <div style="padding: 30px; background: #f8f9fa;">
                    <!-- En-tête -->
                    <div style="margin-bottom: 30px;">
                        <h2 style="font-size: 24px; font-weight: 700; margin: 0 0 8px 0; color: #1a1a1a;">Tableau de bord Crédit</h2>
                        <p style="color: #6c757d; margin: 0; font-size: 14px;">Vue d'ensemble des demandes de crédit et validations en cours</p>
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
                        
                        <!-- Indicateur de page (les boutons sont dans la vue Odoo) -->
                        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #dee2e6; text-align: center;">
                            <span style="color: #495057; font-weight: 600; font-size: 14px;">Page {0} sur {1}</span>
                        </div>
                    </div>
                </div>
            '''.format(page, total_pages)
            
                rec.stats_html = html
                continue

            # ── TABLEAU DE BORD COURRIER ───────────────────────────────────
            Courrier = self.env['workflow.courrier.entrant']
            total_courriers = Courrier.search_count([])
            en_validation = Courrier.search_count([('state', '=', 'en_validation')])
            traites = Courrier.search_count([('state', '=', 'traite')])
            clotures = Courrier.search_count([('state', '=', 'cloture')])
            total_pages = (total_courriers + limit - 1) // limit if total_courriers > 0 else 1

            recent_courriers = Courrier.search([], order='date_reception desc', limit=limit, offset=offset)

            html = '''
                <div style="padding: 30px; background: #f8f9fa;">
                    <!-- En-tête -->
                    <div style="margin-bottom: 30px;">
                        <h2 style="font-size: 24px; font-weight: 700; margin: 0 0 8px 0; color: #1a1a1a;">Tableau de bord Courriers</h2>
                        <p style="color: #6c757d; margin: 0; font-size: 14px;">Vue d'ensemble des courriers entrants et de leur traitement</p>
                    </div>
                    
                    <!-- Cartes statistiques -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 30px;">
                        <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                                <div>
                                    <div style="color: #6c757d; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">TOTAL COURRIERS</div>
                                    <div style="font-size: 36px; font-weight: 700; color: #1a1a1a;">{0}</div>
                                </div>
                                <div style="width: 48px; height: 48px; background: #e7f0ff; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">📬</div>
                            </div>
                        </div>
                        
                        <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                                <div>
                                    <div style="color: #6c757d; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">EN VALIDATION</div>
                                    <div style="font-size: 36px; font-weight: 700; color: #1a1a1a;">{1}</div>
                                </div>
                                <div style="width: 48px; height: 48px; background: #fff3e0; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">⏳</div>
                            </div>
                        </div>
                        
                        <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                                <div>
                                    <div style="color: #6c757d; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">TRAITÉS</div>
                                    <div style="font-size: 36px; font-weight: 700; color: #1a1a1a;">{2}</div>
                                </div>
                                <div style="width: 48px; height: 48px; background: #e8f5e9; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">✓</div>
                            </div>
                        </div>
                        
                        <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                                <div>
                                    <div style="color: #6c757d; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">CLÔTURÉS</div>
                                    <div style="font-size: 36px; font-weight: 700; color: #1a1a1a;">{3}</div>
                                </div>
                                <div style="width: 48px; height: 48px; background: #f8d7da; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">✔</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Liste des courriers récents -->
                    <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                            <h5 style="margin: 0; font-size: 18px; font-weight: 700; color: #1a1a1a;">Courriers récents</h5>
                            <a href="/web#action=workflow.action_courrier_entrant"
                               style="background: #0d6efd; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px; display: inline-block;">
                               + Nouveau courrier
                            </a>
                        </div>
                        
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="border-bottom: 2px solid #dee2e6;">
                                    <th style="padding: 12px; text-align: left; color: #6c757d; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">RÉFÉRENCE</th>
                                    <th style="padding: 12px; text-align: left; color: #6c757d; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">EXPÉDITEUR</th>
                                    <th style="padding: 12px; text-align: left; color: #6c757d; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">OBJET</th>
                                    <th style="padding: 12px; text-align: left; color: #6c757d; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">TYPE</th>
                                    <th style="padding: 12px; text-align: left; color: #6c757d; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">PRIORITÉ</th>
                                    <th style="padding: 12px; text-align: left; color: #6c757d; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">STATUT</th>
                                    <th style="padding: 12px; text-align: left; color: #6c757d; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">DATE RÉCEPTION</th>
                                </tr>
                            </thead>
                            <tbody>
            '''.format(total_courriers, en_validation, traites, clotures)

            state_labels = {
                'recu': ('● Reçu', '#6c757d'),
                'en_validation': ('● En validation', '#0d6efd'),
                'traite': ('● Traité', '#28a745'),
                'cloture': ('● Clôturé', '#6c757d'),
            }

            type_labels = {
                'lettre': 'Lettre',
                'email': 'Email',
                'rapport': 'Rapport',
                'facture': 'Facture',
                'demande': 'Demande',
                'notification': 'Notification',
                'autre': 'Autre',
            }

            priorite_labels = {'0': 'Normal', '1': 'Urgent', '2': 'Critique'}

            for c in recent_courriers:
                state_label, state_color = state_labels.get(c.state, ('● ' + c.state, '#6c757d'))
                date_str = c.date_reception.strftime('%d/%m/%Y') if c.date_reception else '-'
                type_label = type_labels.get(c.type_courrier, c.type_courrier or '-')
                priorite_label = priorite_labels.get(c.priorite, c.priorite or '-')

                html += '''
                                <tr style="border-bottom: 1px solid #f0f0f0;">
                                    <td style="padding: 16px 12px;"><strong style="color: #1a1a1a;">{0}</strong></td>
                                    <td style="padding: 16px 12px; color: #495057;">{1}</td>
                                    <td style="padding: 16px 12px; color: #495057;">{2}</td>
                                    <td style="padding: 16px 12px; color: #495057;">{3}</td>
                                    <td style="padding: 16px 12px; color: #495057;">{4}</td>
                                    <td style="padding: 16px 12px;"><span style="color: {5}; font-weight: 600; font-size: 13px;">{6}</span></td>
                                    <td style="padding: 16px 12px; color: #6c757d; font-size: 13px;">{7}</td>
                                </tr>
                '''.format(
                    c.name,
                    c.expediteur or '-',
                    (c.objet or '-')[:80],
                    type_label,
                    priorite_label,
                    state_color,
                    state_label,
                    date_str,
                )

            html += '''
                            </tbody>
                        </table>
                        
                        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #dee2e6; text-align: center;">
                            <span style="color: #495057; font-weight: 600; font-size: 14px;">Page {0} sur {1}</span>
                        </div>
                    </div>
                </div>
            '''.format(page, total_pages)

            rec.stats_html = html
