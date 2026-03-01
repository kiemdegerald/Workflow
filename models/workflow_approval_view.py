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
        """Génère le HTML de la vue approbateur — adapté selon le type (CREDIT ou COURRIER)"""
        for record in self:
            if not record.request_id:
                record.approval_html = '<p>Aucune demande sélectionnée</p>'
                continue

            req = record.request_id
            workflow_type_code = req.workflow_type_id.code if req.workflow_type_id else ''

            # Approbation courante
            current_approval = self.env['workflow.request.approval'].search([
                ('workflow_request_id', '=', req.id),
                ('approver_id', '=', self.env.user.id),
                ('state', '=', 'pending'),
            ], limit=1)

            all_approvals = self.env['workflow.request.approval'].search([
                ('workflow_request_id', '=', req.id),
            ], order='workflow_level_id')

            statusbar_html        = self._build_statusbar(all_approvals, current_approval)
            history_html          = self._build_approval_history(all_approvals)
            previous_comments_html = self._build_previous_comments(all_approvals, current_approval)
            status_text = "En attente de votre validation" if current_approval else "Déjà validée par vous"

            # ── Contenu du dossier selon le type ─────────────────────────
            if workflow_type_code == 'COURRIER':
                dossier_html = record._build_dossier_courrier(req)
                documents_html = record._build_documents_courrier(req)
                header_color = 'linear-gradient(135deg, #1a5276 0%, #2471a3 100%)'
                dossier_title = '📬 Courrier à examiner'
            else:
                dossier_html = record._build_dossier_credit(req)
                documents_html = self._build_documents_section(req)
                header_color = 'linear-gradient(135deg, #0a4b78 0%, #0d5a8f 100%)'
                dossier_title = '📋 Dossier crédit à examiner'

            html = f'''
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; background: #f8f9fa; padding: 2rem;">

                <div style="margin-bottom: 2rem;">
                    <h1 style="margin: 0; font-size: 32px; font-weight: 700; color: #1a1a1a;">Vue Approbateur</h1>
                    <p style="margin: 0.5rem 0 0 0; color: #6c757d; font-size: 16px;">Validez, refusez ou retournez les demandes qui vous sont assignées</p>
                </div>

                <div style="background: white; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); overflow: hidden;">

                    <div style="background: {header_color}; padding: 1.5rem 2rem; color: white;">
                        <div style="font-size: 22px; font-weight: 600; margin-bottom: 0.5rem;">{req.subject or 'Sans objet'}</div>
                        <div style="font-size: 14px; opacity: 0.9;">{req.name} • {status_text}</div>
                    </div>

                    <div style="padding: 2rem; border-bottom: 1px solid #e9ecef;">
                        {statusbar_html}
                    </div>

                    <div style="padding: 2rem;">

                        <div style="background: rgba(10, 75, 120, 0.04); border: 2px solid #0a4b78; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem;">
                            <h3 style="margin: 0 0 1.5rem 0; font-size: 18px; color: #0a4b78; font-weight: 600;">{dossier_title}</h3>
                            {dossier_html}
                            {history_html}
                        </div>

                        {previous_comments_html}
                        {documents_html}
                    </div>
                </div>
            </div>
            '''

            record.approval_html = html

    def _build_dossier_credit(self, req):
        """HTML du dossier pour un crédit bancaire."""
        credit_types = {
            'salary': 'Crédit salarié',
            'housing': 'Crédit habitat',
            'consumption': 'Crédit consommation',
            'business': 'Crédit entreprise',
            'other': 'Autre',
        }
        credit_type_label = credit_types.get(req.credit_type, req.credit_type or '-')
        amount_formatted = f"{req.amount:,.0f}".replace(',', ' ') if req.amount else '0'

        description_block = ''
        if req.description:
            description_block = f'''
                <div style="background: white; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem;">
                    <strong style="display: block; margin-bottom: 0.5rem;">Objet du crédit :</strong>
                    <p style="margin: 0; color: #495057;">{req.description}</p>
                </div>'''

        return f'''
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
                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 0.25rem; text-transform: uppercase; font-weight: 600;">Référence</div>
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
            {description_block}'''

    def _build_dossier_courrier(self, req):
        """HTML du dossier pour un courrier entrant."""
        courrier = self.env['workflow.courrier.entrant'].search([
            ('workflow_request_id', '=', req.id)
        ], limit=1)

        if not courrier:
            return f'''
                <div style="background: #fff3cd; border-radius: 8px; padding: 1rem; color: #856404;">
                    ⚠️ Courrier lié introuvable (référence : {req.name}).
                </div>'''

        type_labels = {
            'lettre':       'Lettre',
            'email':        'Email',
            'rapport':      'Rapport',
            'facture':      'Facture',
            'demande':      'Demande',
            'notification': 'Notification',
            'autre':        'Autre',
        }
        type_label = type_labels.get(courrier.type_courrier, courrier.type_courrier or '-')

        priorite_labels = {'0': 'Normal', '1': 'Urgent', '2': 'Critique'}
        priorite_colors  = {'0': '#6c757d', '1': '#fd7e14', '2': '#dc3545'}
        priorite_label = priorite_labels.get(courrier.priorite, '-')
        priorite_color = priorite_colors.get(courrier.priorite, '#6c757d')

        date_str = courrier.date_reception.strftime('%d/%m/%Y') if courrier.date_reception else '-'

        description_block = ''
        if courrier.description:
            description_block = f'''
                <div style="background: white; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <strong style="display: block; margin-bottom: 0.5rem;">Résumé du courrier :</strong>
                    <p style="margin: 0; color: #495057;">{courrier.description}</p>
                </div>'''

        instruction_block = ''
        if courrier.instruction:
            instruction_block = f'''
                <div style="background: #fff8e1; border-left: 4px solid #ffc107; border-radius: 8px; padding: 1rem;">
                    <strong style="display: block; margin-bottom: 0.5rem;">📌 Instructions de traitement :</strong>
                    <p style="margin: 0; color: #495057;">{courrier.instruction}</p>
                </div>'''

        return f'''
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin-bottom: 1.5rem;">
                <div>
                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 0.25rem; text-transform: uppercase; font-weight: 600;">Référence courrier</div>
                    <div style="font-weight: 600; font-size: 15px;">{courrier.name}</div>
                </div>
                <div>
                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 0.25rem; text-transform: uppercase; font-weight: 600;">Date de réception</div>
                    <div style="font-weight: 600; font-size: 15px;">{date_str}</div>
                </div>
                <div>
                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 0.25rem; text-transform: uppercase; font-weight: 600;">Expéditeur</div>
                    <div style="font-weight: 600; font-size: 15px;">{courrier.expediteur or 'Non renseigné'}</div>
                    {('<div style="font-size: 13px; color: #6c757d; margin-top: 0.25rem;">' + courrier.origine + '</div>') if courrier.origine else ''}
                </div>
                <div>
                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 0.25rem; text-transform: uppercase; font-weight: 600;">Type de courrier</div>
                    <div style="font-weight: 600; font-size: 15px;">{type_label}</div>
                </div>
                <div>
                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 0.25rem; text-transform: uppercase; font-weight: 600;">Priorité</div>
                    <div style="font-weight: 700; font-size: 15px; color: {priorite_color};">{priorite_label}</div>
                </div>
                <div>
                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 0.25rem; text-transform: uppercase; font-weight: 600;">Enregistré par</div>
                    <div style="font-weight: 600; font-size: 15px;">{courrier.secretaire_id.name if courrier.secretaire_id else '-'}</div>
                </div>
            </div>
            {description_block}
            {instruction_block}'''

    def _build_documents_courrier(self, req):
        """Documents attachés au courrier entrant avec token d'accès et prévisualisation."""
        # Tout se fait en sudo pour éviter les erreurs d'accès
        courrier = self.env['workflow.courrier.entrant'].sudo().search([
            ('workflow_request_id', '=', req.id)
        ], limit=1)

        if not courrier:
            return ''

        # Récupérer les IDs des pièces jointes puis les charger en sudo
        att_ids = courrier.attachment_ids.ids
        if not att_ids:
            return f'''
                <div style="margin-top: 2rem; background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #dee2e6;">
                    <h3 style="margin: 0 0 1rem 0; font-size: 18px; font-weight: 600;">📎 Documents du courrier</h3>
                    <div style="text-align: center; padding: 2rem; color: #6c757d; background: #f8f9fa; border-radius: 8px;">
                        <span style="font-size: 48px; display: block; margin-bottom: 0.5rem;">📎</span>
                        <p style="margin: 0;">Aucun document joint à ce courrier</p>
                    </div>
                </div>'''

        attachments = self.env['ir.attachment'].sudo().browse(att_ids)

        docs_html = []
        preview_html = ''

        for idx, att in enumerate(attachments):
            token    = att.access_token or ''
            size_kb  = att.file_size / 1024 if att.file_size else 0
            size_str = f"{size_kb/1024:.1f} MB" if size_kb > 1024 else f"{size_kb:.0f} KB"
            mimetype = att.mimetype or ''
            name     = att.name or 'Document'

            # URL simple — le res_model/res_id est désormais défini sur l'attachment
            # donc tout utilisateur pouvant lire le courrier peut lire le fichier
            url_view     = f"/web/content/{att.id}/{name}"
            url_download = f"/web/content/{att.id}/{name}?download=true"

            is_pdf   = 'pdf' in mimetype
            is_image = mimetype.startswith('image/')
            icon     = '🖼️' if is_image else ('📄' if is_pdf else '📎')

            # Prévisualisation inline pour le 1er document
            if idx == 0:
                if is_pdf:
                    preview_html = f'''
                        <div style="margin-bottom: 1.5rem; border: 2px solid #1a5276; border-radius: 10px; overflow: hidden;">
                            <div style="background: #1a5276; color: white; padding: 0.75rem 1rem; font-weight: 600; font-size: 14px;">
                                👁️ Aperçu — {name}
                            </div>
                            <iframe src="{url_view}"
                                    style="width: 100%; height: 700px; border: none; display: block;"
                                    title="{name}">
                            </iframe>
                        </div>'''
                elif is_image:
                    preview_html = f'''
                        <div style="margin-bottom: 1.5rem; border: 2px solid #1a5276; border-radius: 10px; overflow: hidden;">
                            <div style="background: #1a5276; color: white; padding: 0.75rem 1rem; font-weight: 600; font-size: 14px;">
                                👁️ Aperçu — {name}
                            </div>
                            <div style="text-align: center; padding: 1rem; background: #f8f9fa;">
                                <img src="{url_view}"
                                     style="max-width: 100%; max-height: 700px; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);"
                                     alt="{name}"/>
                            </div>
                        </div>'''

            docs_html.append(f'''
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 24px;">{icon}</span>
                    <div style="flex: 1;">
                        <div style="font-weight: 600;">{name}</div>
                        <div style="font-size: 12px; color: #6c757d;">{mimetype or 'Document'} • {size_str}</div>
                    </div>
                    <div style="display: flex; gap: 0.5rem;">
                        <a href="{url_view}" target="_blank"
                           style="background: #1a5276; color: white; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 600;">
                           👁 Visualiser
                        </a>
                        <a href="{url_download}" target="_blank"
                           style="background: #6c757d; color: white; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 600;">
                           ⬇ Télécharger
                        </a>
                    </div>
                </div>''')

        return f'''
            <div style="margin-top: 2rem; background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #dee2e6;">
                <h3 style="margin: 0 0 1.5rem 0; font-size: 18px; font-weight: 600;">📎 Document(s) du courrier à examiner</h3>
                {preview_html}
                {''.join(docs_html)}
            </div>'''

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
        """Construit le bouton et le modal pour afficher l'historique complet des commentaires"""
        # Récupérer TOUTES les approbations triées par séquence
        all_approvals_sorted = all_approvals.sorted(key=lambda a: a.workflow_level_id.sequence)
        
        if not all_approvals_sorted:
            return '<div style="background: #f8f9fa; border-radius: 8px; padding: 1rem; text-align: center; color: #6c757d; font-style: italic;">Aucun niveau d\'approbation configuré</div>'
        
        # Compter les commentaires non vides
        comment_count = len([a for a in all_approvals_sorted if a.comments and a.comments.strip() != ''])
        
        # Construire les items du modal
        history_items = []
        
        for approval in all_approvals_sorted:
            if approval.state == 'approved':
                border_color = '#198754'
                icon = '✅'
                state_label = 'Approuvé'
                bg_color = '#d1e7dd'
            elif approval.state == 'rejected':
                border_color = '#dc3545'
                icon = '❌'
                state_label = 'Refusé'
                bg_color = '#f8d7da'
            elif approval.state == 'returned':
                border_color = '#fd7e14'
                icon = '🔙'
                state_label = 'Retourné au niveau précédent'
                bg_color = '#fff3cd'
            elif approval.state == 'waiting':
                border_color = '#6c757d'
                icon = '⏳'
                state_label = 'En attente du niveau précédent'
                bg_color = '#e9ecef'
            else:  # pending
                border_color = '#0d6efd'
                icon = '⏸️'
                state_label = 'En cours de validation'
                bg_color = '#cfe2ff'
            
            approver_name = approval.approver_id.name if approval.approver_id else 'Utilisateur inconnu'
            level_name = approval.workflow_level_id.name if approval.workflow_level_id else 'Niveau inconnu'
            comment = approval.comments if approval.comments and approval.comments.strip() else 'Pas encore de commentaire'
            
            # Formater la date
            date_str = ''
            if approval.write_date:
                date_obj = approval.write_date
                date_str = date_obj.strftime('%d/%m/%Y à %H:%M')
            elif approval.create_date:
                date_obj = approval.create_date
                date_str = date_obj.strftime('%d/%m/%Y à %H:%M')
            
            # Style différent si pas de commentaire
            comment_style = 'font-style: italic; color: #6c757d;' if comment == 'Pas encore de commentaire' else 'font-style: italic; color: #495057;'
            
            item_html = f'''
                <div style="background: {bg_color}; border-left: 4px solid {border_color}; border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                        <div style="flex: 1;">
                            <div style="margin-bottom: 0.5rem;">
                                <span style="font-size: 20px; margin-right: 0.5rem;">{icon}</span>
                                <strong style="color: {border_color}; font-size: 15px;">{state_label}</strong>
                            </div>
                            <div style="font-size: 14px; color: #495057; margin-bottom: 0.25rem;">
                                <strong>{approver_name}</strong> • <span style="color: #6c757d;">{level_name}</span>
                            </div>
                            {('<div style="font-size: 12px; color: #6c757d;">' + date_str + '</div>') if date_str else ''}
                        </div>
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 6px; color: #212529; line-height: 1.6; border: 1px solid rgba(0,0,0,0.05);">
                        <div style="{comment_style}">"{comment}"</div>
                    </div>
                </div>
            '''
            history_items.append(item_html)
        
        # Modal HTML + Bouton
        modal_html = f'''
            <!-- Bouton pour ouvrir le modal -->
            <div style="margin-top: 1rem;">
                <button onclick="document.getElementById('historyModal').style.display = 'flex'" 
                        style="background: #0a4b78; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; box-shadow: 0 2px 4px rgba(10,75,120,0.2); transition: all 0.2s;"
                        onmouseover="this.style.background='#083a5e'; this.style.boxShadow='0 4px 8px rgba(10,75,120,0.3)'"
                        onmouseout="this.style.background='#0a4b78'; this.style.boxShadow='0 2px 4px rgba(10,75,120,0.2)'">
                    <span style="font-size: 18px;">�</span>
                    Voir l'état du workflow ({len(all_approvals_sorted)} niveaux{' • ' + str(comment_count) + ' commentaire(s)' if comment_count > 0 else ''})
                </button>
            </div>
            
            <!-- Modal -->
            <div id="historyModal" style="display: none; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.6); align-items: center; justify-content: center;">
                <div style="background: white; border-radius: 16px; width: 90%; max-width: 800px; max-height: 85vh; display: flex; flex-direction: column; box-shadow: 0 10px 40px rgba(0,0,0,0.2);">
                    
                    <!-- En-tête du modal -->
                    <div style="background: linear-gradient(135deg, #0a4b78 0%, #0d5a8f 100%); color: white; padding: 1.5rem 2rem; border-radius: 16px 16px 0 0; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h2 style="margin: 0; font-size: 22px; font-weight: 700;">� État du Workflow & Commentaires</h2>
                            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 14px;">{len(all_approvals_sorted)} niveau(x) • {comment_count} commentaire(s)</p>
                        </div>
                        <button onclick="document.getElementById('historyModal').style.display = 'none'" 
                                style="background: rgba(255,255,255,0.2); border: none; color: white; font-size: 28px; cursor: pointer; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.2s;"
                                onmouseover="this.style.background='rgba(255,255,255,0.3)'"
                                onmouseout="this.style.background='rgba(255,255,255,0.2)'">×</button>
                    </div>
                    
                    <!-- Corps du modal (scrollable) -->
                    <div style="padding: 2rem; overflow-y: auto; flex: 1;">
                        {''.join(history_items)}
                    </div>
                    
                    <!-- Pied du modal -->
                    <div style="padding: 1rem 2rem; border-top: 1px solid #e9ecef; text-align: right;">
                        <button onclick="document.getElementById('historyModal').style.display = 'none'" 
                                style="background: #6c757d; color: white; border: none; padding: 0.75rem 2rem; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; transition: all 0.2s;"
                                onmouseover="this.style.background='#5a6268'"
                                onmouseout="this.style.background='#6c757d'">Fermer</button>
                    </div>
                </div>
            </div>
            
            <!-- Script pour fermer le modal en cliquant en dehors -->
            <script>
                document.getElementById('historyModal').addEventListener('click', function(event) {{
                    if (event.target === this) {{
                        this.style.display = 'none';
                    }}
                }});
            </script>
        '''

    def _build_previous_comments(self, all_approvals, current_approval):
        """Affiche TOUS les commentaires en ordre chronologique depuis workflow.request.comment"""
        # Récupérer TOUS les commentaires de cette demande, triés par date de création
        all_comments = self.env['workflow.request.comment'].search([
            ('request_id', '=', self.request_id.id)
        ], order='create_date asc')
        
        if not all_comments:
            return ''
        
        # Construire les commentaires
        comment_items = []
        for comment in all_comments:
            # Icône et couleur selon le type
            if comment.comment_type == 'approval_note':
                icon = '✅'
                border_color = '#198754'
                bg_color = '#d1e7dd'
                state_label = 'Approuvé'
            elif comment.comment_type == 'rejection_reason':
                icon = '❌'
                border_color = '#dc3545'
                bg_color = '#f8d7da'
                state_label = 'Refusé'
            elif comment.comment_type == 'return':
                icon = '🔙'
                border_color = '#fd7e14'
                bg_color = '#fff3cd'
                state_label = 'Retourné au niveau précédent'
            elif comment.comment_type == 'clarification':
                icon = '❓'
                border_color = '#0dcaf0'
                bg_color = '#cff4fc'
                state_label = 'Demande de clarification'
            elif comment.comment_type == 'response':
                icon = '💬'
                border_color = '#6f42c1'
                bg_color = '#e0cffc'
                state_label = 'Réponse'
            else:
                icon = '📝'
                border_color = '#6c757d'
                bg_color = '#f8f9fa'
                state_label = 'Information'
            
            author_name = comment.user_id.name if comment.user_id else 'Utilisateur inconnu'
            level_name = comment.approval_id.workflow_level_id.name if comment.approval_id and comment.approval_id.workflow_level_id else 'N/A'
            
            # Indiquer si c'est l'utilisateur connecté
            is_current_user = (comment.user_id.id == self.env.user.id)
            user_badge = ' <span style="background: #0a4b78; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 11px; font-weight: 700;">VOUS</span>' if is_current_user else ''
            
            # Formater la date
            date_str = ''
            if comment.create_date:
                date_obj = comment.create_date
                date_str = date_obj.strftime('%d/%m/%Y à %H:%M')
            
            comment_html = f'''
                <div style="background: {bg_color}; border-left: 4px solid {border_color}; border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                        <div style="flex: 1;">
                            <div style="margin-bottom: 0.5rem;">
                                <span style="font-size: 18px; margin-right: 0.5rem;">{icon}</span>
                                <strong style="color: {border_color}; font-size: 14px;">{state_label}</strong>
                            </div>
                            <div style="font-size: 13px; color: #495057; margin-bottom: 0.25rem;">
                                <strong>{author_name}</strong>{user_badge} • <span style="color: #6c757d;">{level_name}</span>
                            </div>
                            {('<div style="font-size: 12px; color: #6c757d;">' + date_str + '</div>') if date_str else ''}
                        </div>
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 6px; border: 1px solid rgba(0,0,0,0.05);">
                        <div style="color: #212529; line-height: 1.6; font-style: italic;">"{comment.message}"</div>
                    </div>
                </div>
            '''
            comment_items.append(comment_html)
        
        return f'''
            <div style="background: #fff; border: 2px solid #0d6efd; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem;">
                <h3 style="margin: 0 0 1.5rem 0; font-size: 18px; color: #0d6efd; font-weight: 600; display: flex; align-items: center; gap: 0.5rem;">
                    💬 Historique complet des commentaires ({len(comment_items)})
                </h3>
                <p style="margin: 0 0 1rem 0; font-size: 13px; color: #6c757d;">Affichage chronologique de tous les commentaires laissés sur cette demande</p>
                <div style="max-height: 500px; overflow-y: auto;">
                    {''.join(comment_items)}
                </div>
            </div>
        '''
        
        return modal_html

    def _build_documents_section(self, req):
        """Construit la section des documents"""
        
        docs_html = []
        
        # Utiliser sudo() pour accéder aux pièces jointes
        attachments = req.sudo().attachment_ids
        if attachments:
            for attachment in attachments:
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
        ], order='create_date desc')
        
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
        
        # Si plusieurs demandes, afficher d'abord la liste de sélection
        if len(pending_approvals) > 1:
            return {
                'name': f'Sélectionnez une demande à traiter ({len(pending_approvals)} en attente)',
                'type': 'ir.actions.act_window',
                'res_model': 'workflow.request.approval',
                'view_mode': 'tree',
                'domain': [('approver_id', '=', self.env.user.id), ('state', '=', 'pending')],
                'target': 'new',
                'context': self.env.context,
            }
        
        # Créer un enregistrement transient avec la seule demande en attente
        approval_view = self.create({
            'request_id': pending_approvals[0].workflow_request_id.id,
            'current_approval_id': pending_approvals[0].id,
            'comment': '',  # Valeur par défaut vide, sera rempli par l'utilisateur
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
        
        # Créer un commentaire dans l'historique
        self.env['workflow.request.comment'].create({
            'name': f"Validation - {self.current_approval_id.workflow_level_id.name}",
            'request_id': self.request_id.id,
            'approval_id': self.current_approval_id.id,
            'user_id': self.env.user.id,
            'comment_type': 'approval_note',
            'message': self.comment,
            'author_level_sequence': self.current_approval_id.workflow_level_id.sequence,
        })
        
        # IMPORTANT: Vérifier si toutes les approbations du niveau actuel sont validées
        current_level = self.current_approval_id.workflow_level_id
        pending_at_current_level = self.env['workflow.request.approval'].search([
            ('workflow_request_id', '=', self.request_id.id),
            ('workflow_level_id', '=', current_level.id),
            ('state', '=', 'pending')
        ])
        
        if pending_at_current_level:
            # Il reste des validateurs à ce niveau qui n'ont pas encore approuvé
            # On garde la demande en "in_progress" et on attend les autres
            self.request_id.write({'state': 'in_progress'})
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Demande approuvée',
                    'message': f'Votre validation a été enregistrée. En attente des autres validateurs du niveau {current_level.name}.',
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        
        # Toutes les approbations du niveau actuel sont validées
        # Chercher s'il y a un niveau suivant dans le circuit
        next_level = self.env['workflow.level'].search([
            ('workflow_definition_id', '=', current_level.workflow_definition_id.id),
            ('sequence', '>', current_level.sequence)
        ], order='sequence asc', limit=1)
        
        if next_level:
            # Chercher l'approbation du niveau suivant
            next_approval = self.env['workflow.request.approval'].search([
                ('workflow_request_id', '=', self.request_id.id),
                ('workflow_level_id', '=', next_level.id)
            ], limit=1)
            
            if next_approval:
                if next_approval.state in ['returned', 'waiting']:
                    # Le niveau suivant avait retourné la demande, ou était en attente du niveau précédent
                    # On l'active maintenant
                    next_approval.write({'state': 'pending'})
                    self.request_id.write({'state': 'in_progress'})
                elif next_approval.state == 'pending':
                    # Le niveau suivant est déjà en attente
                    self.request_id.write({'state': 'in_progress'})
                else:
                    # Le niveau suivant a déjà validé (ne devrait pas arriver)
                    # Vérifier s'il reste des niveaux en attente
                    pending_approvals = self.env['workflow.request.approval'].search([
                        ('workflow_request_id', '=', self.request_id.id),
                        ('state', '=', 'pending')
                    ])
                    if pending_approvals:
                        self.request_id.write({'state': 'in_progress'})
                    else:
                        self.request_id.write({'state': 'approved'})
            else:
                # Pas d'approbation suivante trouvée, approuver
                self.request_id.write({'state': 'approved'})
        else:
            # Pas de niveau suivant, c'est le dernier niveau, approuver
            self.request_id.write({'state': 'approved'})
        
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
        
        # Créer un commentaire dans l'historique
        self.env['workflow.request.comment'].create({
            'name': f"Rejet - {self.current_approval_id.workflow_level_id.name}",
            'request_id': self.request_id.id,
            'approval_id': self.current_approval_id.id,
            'user_id': self.env.user.id,
            'comment_type': 'rejection_reason',
            'message': self.comment,
            'author_level_sequence': self.current_approval_id.workflow_level_id.sequence,
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
        
        # Créer un commentaire dans l'historique
        self.env['workflow.request.comment'].create({
            'name': f"Retour - {self.current_approval_id.workflow_level_id.name}",
            'request_id': self.request_id.id,
            'approval_id': self.current_approval_id.id,
            'user_id': self.env.user.id,
            'comment_type': 'return',
            'message': self.comment,
            'author_level_sequence': self.current_approval_id.workflow_level_id.sequence,
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
