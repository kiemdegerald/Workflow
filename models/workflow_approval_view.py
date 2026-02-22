# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class WorkflowApprovalView(models.TransientModel):
    _name = 'workflow.approval.view'
    _description = 'Vue Approbateur - Transient Model'

    request_id = fields.Many2one('workflow.request', string='Demande', required=True)
    approval_html = fields.Html(string='Vue Approbateur', compute='_compute_approval_html')
    comment = fields.Text(string='Commentaire', required=True)
    current_approval_id = fields.Many2one('workflow.request.approval', string='Approbation courante')

    @api.depends('request_id')
    def _compute_approval_html(self):
        """Génère le HTML de la vue approbateur"""
        for record in self:
            if not record.request_id:
                record.approval_html = '<p>Aucune demande sélectionnée</p>'
                continue

            req = record.request_id
            
            # Récupérer l'approbation courante pour l'utilisateur
            current_approval = self.env['workflow.request.approval'].search([
                ('workflow_request_id', '=', req.id),
                ('approver_id', '=', self.env.user.id),
                ('state', '=', 'pending')
            ], limit=1)
            
            # Récupérer toutes les approbations pour afficher l'historique
            all_approvals = self.env['workflow.request.approval'].search([
                ('workflow_request_id', '=', req.id)
            ], order='workflow_level_id')
            
            # Construire la barre de statut
            statusbar_html = self._build_statusbar(all_approvals, current_approval)
            
            # Historique des décisions
            history_html = self._build_approval_history(all_approvals)
            
            # Documents
            documents_html = self._build_documents_section(req)
            
            # État de la demande
            status_text = "En attente de votre validation" if current_approval else "Déjà validée par vous"
            
            # Montant formaté
            amount_formatted = f"{req.amount:,.0f}".replace(',', ' ') if req.amount else '0'
            
            # Type de crédit
            credit_types = {
                'salary': 'Crédit salarié',
                'housing': 'Crédit habitat',
                'consumption': 'Crédit consommation',
                'business': 'Crédit entreprise',
                'other': 'Autre',
            }
            credit_type_label = credit_types.get(req.credit_type, req.credit_type or '-')
            
            html = f'''
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; background: #f8f9fa; padding: 2rem;">
                
                <!-- En-tête -->
                <div style="margin-bottom: 2rem;">
                    <h1 style="margin: 0; font-size: 32px; font-weight: 700; color: #1a1a1a;">Vue Approbateur</h1>
                    <p style="margin: 0.5rem 0 0 0; color: #6c757d; font-size: 16px;">Validez, refusez ou retournez les demandes qui vous sont assignées</p>
                </div>

                <!-- Container principal -->
                <div style="background: white; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); overflow: hidden;">
                    
                    <!-- Header de la demande -->
                    <div style="background: linear-gradient(135deg, #0a4b78 0%, #0d5a8f 100%); padding: 1.5rem 2rem; color: white;">
                        <div style="font-size: 22px; font-weight: 600; margin-bottom: 0.5rem;">{req.subject or 'Sans objet'}</div>
                        <div style="font-size: 14px; opacity: 0.9;">{req.name} • {status_text}</div>
                    </div>
                    
                    <!-- Barre de statut -->
                    <div style="padding: 2rem; border-bottom: 1px solid #e9ecef;">
                        {statusbar_html}
                    </div>
                    
                    <!-- Corps -->
                    <div style="padding: 2rem;">
                        
                        <!-- Section: Dossier complet -->
                        <div style="background: rgba(10, 75, 120, 0.04); border: 2px solid #0a4b78; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem;">
                            <h3 style="margin: 0 0 1.5rem 0; font-size: 18px; color: #0a4b78; font-weight: 600;">📋 Dossier complet à examiner</h3>
                            
                            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin-bottom: 1.5rem;">
                                <div>
                                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 0.25rem; text-transform: uppercase; font-weight: 600;">Client</div>
                                    <div style="font-weight: 600; font-size: 15px;">{req.client_name or 'Non renseigné'}</div>
                                    {('<div style="font-size: 13px; color: #6c757d; margin-top: 0.25rem;">' + req.client_number + '</div>') if req.client_number else ''}
                                </div>
                                <div>
                                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 0.25rem; text-transform: uppercase; font-weight: 600;">Numéro de compte</div>
                                    <div style="font-weight: 600; font-size: 15px;">{req.account_number or 'Non renseigné'}</div>
                                </div>
                                <div>
                                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 0.25rem; text-transform: uppercase; font-weight: 600;">Type de crédit</div>
                                    <div style="font-weight: 600; font-size: 15px;">{credit_type_label}</div>
                                </div>
                                <div>
                                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 0.25rem; text-transform: uppercase; font-weight: 600;">Référence demande</div>
                                    <div style="font-weight: 600; font-size: 15px;">{req.name}</div>
                                </div>
                                <div>
                                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 0.25rem; text-transform: uppercase; font-weight: 600;">Montant demandé</div>
                                    <div style="font-size: 20px; font-weight: 700; color: #0a4b78;">{amount_formatted} FCFA</div>
                                </div>
                                <div>
                                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 0.25rem; text-transform: uppercase; font-weight: 600;">Durée</div>
                                    <div style="font-weight: 600; font-size: 15px;">{req.duration_months or 0} mois</div>
                                </div>
                            </div>

                            {('<div style="background: white; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem;"><strong style="display: block; margin-bottom: 0.5rem;">Objet du crédit :</strong><p style="margin: 0; color: #495057;">' + (req.description or 'Aucune description') + '</p></div>') if req.description else ''}

                            {history_html}
                        </div>

                        <!-- Documents -->
                        {documents_html}
                    </div>
                </div>
            </div>
            '''
            
            record.approval_html = html

    def _build_statusbar(self, all_approvals, current_approval):
        """Construit la barre de statut avec les niveaux de validation"""
        if not all_approvals:
            return '<div style="text-align: center; color: #6c757d;">Aucun niveau de validation configuré</div>'
        
        levels_html = []
        
        for idx, approval in enumerate(all_approvals):
            # Déterminer le statut
            if approval.state == 'approved':
                status_class = 'completed'
                icon = '✓'
                color = '#198754'
            elif approval.state == 'rejected':
                status_class = 'rejected'
                icon = '✗'
                color = '#dc3545'
            elif approval.state == 'returned':
                status_class = 'returned'
                icon = '↩'
                color = '#fd7e14'
            elif approval.id == current_approval.id:
                status_class = 'active'
                icon = '!'
                color = '#ffc107'
            else:
                status_class = 'pending'
                icon = str(idx + 1)
                color = '#6c757d'
            
            label = approval.workflow_level_id.name if approval.workflow_level_id else f'Niveau {idx + 1}'
            
            step_html = f'''
                <div style="display: flex; flex-direction: column; align-items: center; position: relative;">
                    <div style="width: 40px; height: 40px; border-radius: 50%; background: {color}; color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 18px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        {icon}
                    </div>
                    <span style="margin-top: 0.5rem; font-size: 13px; color: #495057; white-space: nowrap;">{label}</span>
                </div>
            '''
            levels_html.append(step_html)
            
            # Ajouter un connecteur sauf pour le dernier élément
            if idx < len(all_approvals) - 1:
                connector_html = f'<div style="flex: 1; height: 2px; background: #dee2e6; margin: 0 1rem; position: relative; top: -30px;"></div>'
                levels_html.append(connector_html)
        
        return '<div style="display: flex; align-items: flex-start; justify-content: center;">' + ''.join(levels_html) + '</div>'

    def _build_approval_history(self, all_approvals):
        """Construit l'historique des décisions précédentes"""
        approved_approvals = all_approvals.filtered(lambda a: a.state in ['approved', 'rejected', 'returned'])
        
        if not approved_approvals:
            return ''
        
        history_items = []
        
        for approval in approved_approvals:
            if approval.state == 'approved':
                border_color = '#198754'
                state_label = 'Approuvé'
            elif approval.state == 'rejected':
                border_color = '#dc3545'
                state_label = 'Refusé'
            else:
                border_color = '#fd7e14'
                state_label = 'Retourné'
            
            approver_name = approval.approver_id.name if approval.approver_id else 'Utilisateur inconnu'
            level_name = approval.workflow_level_id.name if approval.workflow_level_id else 'Niveau inconnu'
            comment = approval.comments or 'Aucun commentaire'
            
            item_html = f'''
                <div style="padding-left: 1rem; border-left: 3px solid {border_color}; margin-bottom: 1rem;">
                    <div style="font-size: 13px; color: #6c757d; margin-bottom: 0.25rem;">
                        <strong>{approver_name}</strong> ({level_name}) • {state_label}
                    </div>
                    <div style="color: #495057;">{comment}</div>
                </div>
            '''
            history_items.append(item_html)
        
        return f'''
            <div style="background: white; border-radius: 8px; padding: 1rem;">
                <strong style="display: block; margin-bottom: 0.75rem;">✓ Historique des décisions :</strong>
                {''.join(history_items)}
            </div>
        '''

    def _build_documents_section(self, req):
        """Construit la section des documents"""
        
        docs_html = []
        
        if req.attachment_ids:
            for attachment in req.attachment_ids:
                # Taille formatée
                size_kb = attachment.file_size / 1024 if attachment.file_size else 0
                if size_kb > 1024:
                    size_str = f"{size_kb/1024:.1f} MB"
                else:
                    size_str = f"{size_kb:.0f} KB"
                
                doc_html = f'''
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
                        <span style="font-size: 24px;">📄</span>
                        <div style="flex: 1;">
                            <div style="font-weight: 600;">{attachment.name}</div>
                            <div style="font-size: 12px; color: #6c757d;">{attachment.mimetype or 'Document'} • {size_str}</div>
                        </div>
                        <a href="/web/content/{attachment.id}?download=true" target="_blank" style="background: #6c757d; color: white; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; font-size: 14px;">Télécharger</a>
                    </div>
                '''
                docs_html.append(doc_html)
        else:
            docs_html.append('''
                <div style="text-align: center; padding: 2rem; color: #6c757d; background: #f8f9fa; border-radius: 8px;">
                    <span style="font-size: 48px; display: block; margin-bottom: 0.5rem;">📎</span>
                    <p style="margin: 0;">Aucun document attaché à cette demande</p>
                </div>
            ''')
        
        return f'''
            <div style="margin-top: 2rem; background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #dee2e6;">
                <h3 style="margin: 0 0 1.5rem 0; font-size: 18px; font-weight: 600;">📎 Documents à examiner</h3>
                {''.join(docs_html)}
            </div>
        '''

    @api.model
    def action_open_approval_view(self):
        """Ouvre la vue approbateur pour les demandes en attente"""
        # Récupérer les demandes en attente de validation par l'utilisateur
        pending_approvals = self.env['workflow.request.approval'].search([
            ('approver_id', '=', self.env.user.id),
            ('state', '=', 'pending')
        ])
        
        if not pending_approvals:
            # Afficher une notification informative au lieu d'une erreur
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Aucune demande en attente',
                    'message': 'Vous n\'avez aucune demande en attente de validation pour le moment.',
                    'type': 'info',
                    'sticky': False,
                    'next': {
                        'type': 'ir.actions.act_window_close',
                    }
                }
            }
        
        # Créer un enregistrement transient avec la première demande en attente
        approval_view = self.create({
            'request_id': pending_approvals[0].workflow_request_id.id,
            'current_approval_id': pending_approvals[0].id,
        })
        
        return {
            'name': 'Vue Approbateur',
            'type': 'ir.actions.act_window',
            'res_model': 'workflow.approval.view',
            'view_mode': 'form',
            'res_id': approval_view.id,
            'target': 'current',
            'context': self.env.context,
        }

    def action_approve(self):
        """Valider la demande"""
        self.ensure_one()
        
        if not self.current_approval_id:
            raise UserError("Aucune approbation en attente trouvée.")
        
        # Le commentaire est maintenant obligatoire (required=True)
        # Mettre à jour l'approbation
        self.current_approval_id.write({
            'state': 'approved',
            'comments': self.comment,
        })
        
        # Vérifier si c'est le dernier niveau
        next_approval = self.env['workflow.request.approval'].search([
            ('workflow_request_id', '=', self.request_id.id),
            ('state', '=', 'pending')
        ], limit=1)
        
        if not next_approval:
            # Tous les niveaux validés, approuver la demande
            self.request_id.write({'state': 'approved'})
        else:
            # Demande toujours en cours
            self.request_id.write({'state': 'in_progress'})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Demande validée avec succès',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_reject(self):
        """Refuser la demande"""
        self.ensure_one()
        
        if not self.current_approval_id:
            raise UserError("Aucune approbation en attente trouvée.")
        
        # Le commentaire est obligatoire (required=True dans le champ)
        # Mettre à jour l'approbation
        self.current_approval_id.write({
            'state': 'rejected',
            'comments': self.comment,
        })
        
        # Refuser la demande complète
        self.request_id.write({'state': 'rejected'})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Demande refusée',
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_return(self):
        """Retourner au niveau précédent"""
        self.ensure_one()
        
        if not self.current_approval_id:
            raise UserError("Aucune approbation en attente trouvée.")
        
        # Le commentaire est obligatoire (required=True dans le champ)
        # Mettre à jour l'approbation courante
        self.current_approval_id.write({
            'state': 'returned',
            'comments': self.comment,
        })
        
        # Trouver le niveau précédent
        current_level = self.current_approval_id.workflow_level_id
        previous_level = self.env['workflow.level'].search([
            ('workflow_definition_id', '=', current_level.workflow_definition_id.id),
            ('sequence', '<', current_level.sequence)
        ], order='sequence desc', limit=1)
        
        if previous_level:
            # Réactiver l'approbation du niveau précédent
            previous_approval = self.env['workflow.request.approval'].search([
                ('workflow_request_id', '=', self.request_id.id),
                ('workflow_level_id', '=', previous_level.id)
            ], limit=1)
            
            if previous_approval:
                previous_approval.write({'state': 'pending'})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Demande retournée au niveau précédent',
                'type': 'info',
                'sticky': False,
            }
        }
