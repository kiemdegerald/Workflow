# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WorkflowRequestWizard(models.TransientModel):
    _name = 'workflow.request.wizard'
    _description = 'Assistant de création de demande'

    # ==================== SECTION 1: INFORMATIONS CLIENT ====================
    client_number = fields.Char(
        string='Numéro client',
        required=True,
        help="Identifiant unique du client (ex. CLT-2026-00784)"
    )
    account_number = fields.Char(
        string='Numéro de compte',
        required=True,
        help="Numéro de compte bancaire (ex. 001-78459632-01)"
    )
    client_name = fields.Char(
        string='Nom du client',
        required=True,
        help="Nom complet du client"
    )
    credit_type = fields.Selection([
        ('salary', 'Crédit salarié'),
        ('housing', 'Crédit habitat'),
        ('consumption', 'Crédit consommation'),
        ('business', 'Crédit entreprise'),
        ('other', 'Autre'),
    ], string='Type de crédit', required=True)

    # ==================== SECTION 2: DÉTAILS FINANCIERS ====================
    subject = fields.Char(
        string='Objet de la demande',
        required=True,
        help="Ex. Prêt personnel logement"
    )
    amount = fields.Monetary(
        string='Montant demandé (FCFA)',
        required=True,
        currency_field='currency_id',
        help="Montant du crédit demandé"
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    duration_months = fields.Integer(
        string='Durée (mois)',
        help="Durée de remboursement en mois"
    )
    priority = fields.Selection([
        ('0', 'Normale'),
        ('1', 'Urgente'),
        ('2', 'Critique'),
    ], string='Priorité', default='0', required=True)
    description = fields.Text(
        string='Description / Justification',
        help="Contexte et justification de la demande"
    )

    # ==================== SECTION 3: RÉFÉRENCE & CONFIGURATION ====================
    workflow_type_id = fields.Many2one(
        'workflow.type',
        string='Type de Workflow',
        required=True,
        help="Type de workflow (sera utilisé pour le routage automatique)"
    )
    reference_preview = fields.Char(
        string='Référence (aperçu)',
        compute='_compute_reference_preview',
        store=False,
        help="Aperçu de la référence qui sera générée"
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'workflow_wizard_attachment_rel',
        'wizard_id',
        'attachment_id',
        string='Pièces jointes'
    )

    # Champ technique pour afficher le circuit détecté
    detected_circuit_info = fields.Html(
        string='Circuit détecté',
        compute='_compute_detected_circuit',
        store=False
    )

    @api.depends('workflow_type_id')
    def _compute_reference_preview(self):
        """Génère un aperçu de la référence qui sera créée"""
        for wizard in self:
            if wizard.workflow_type_id:
                # Format: REQ/TYPE/YYYY/NNNN
                year = fields.Date.today().year
                type_code = wizard.workflow_type_id.code or 'REQ'
                wizard.reference_preview = f"{type_code}/{year}/XXXX (auto-généré)"
            else:
                wizard.reference_preview = "Sélectionnez un type de workflow"

    @api.depends('amount', 'workflow_type_id')
    def _compute_detected_circuit(self):
        """Détecte et affiche le circuit qui sera utilisé"""
        for wizard in self:
            if not wizard.amount or not wizard.workflow_type_id:
                wizard.detected_circuit_info = False
                continue
            
            # Recherche de la règle de routage applicable
            routing_rules = self.env['workflow.routing.rule'].search([
                ('workflow_type_id', '=', wizard.workflow_type_id.id),
                ('active', '=', True),
            ], order='sequence, id')
            
            circuit_found = None
            for rule in routing_rules:
                min_ok = not rule.amount_min or wizard.amount >= rule.amount_min
                max_ok = not rule.amount_max or wizard.amount < rule.amount_max
                
                if min_ok and max_ok:
                    circuit_found = rule.workflow_definition_id
                    break
            
            if circuit_found:
                # Compter les niveaux du circuit
                level_count = self.env['workflow.level'].search_count([
                    ('workflow_definition_id', '=', circuit_found.id),
                    ('active', '=', True)
                ])
                
                # Déterminer la couleur selon le nombre de niveaux
                if level_count <= 2:
                    color = "success"
                    icon = "✅"
                elif level_count == 3:
                    color = "warning"
                    icon = "⚠️"
                else:
                    color = "danger"
                    icon = "🔴"
                
                wizard.detected_circuit_info = f'''
                    <div class="alert alert-{color}" style="margin: 0; padding: 0.75rem; border-radius: 8px;">
                        <i class="fa fa-route"></i> {icon} <strong>{circuit_found.name}</strong> sera automatiquement assigné
                        <br/><small style="opacity: 0.85;">{level_count} niveau{"x" if level_count > 1 else ""} de validation</small>
                    </div>
                '''
            else:
                wizard.detected_circuit_info = '''
                    <div class="alert alert-warning" style="margin: 0; padding: 0.75rem; border-radius: 8px;">
                        <i class="fa fa-exclamation-triangle"></i> ⚠️ Aucune règle de routage ne correspond à ce montant.
                        <br/><small>Veuillez configurer les règles de routage dans Configuration → Règles de routage</small>
                    </div>
                '''

    def _generate_reference(self):
        """Génère une référence unique pour la demande"""
        self.ensure_one()
        
        # Récupération de la séquence
        sequence = self.env['ir.sequence'].sudo().search([
            ('code', '=', 'workflow.request')
        ], limit=1)
        
        if not sequence:
            raise UserError(_("La séquence pour les demandes n'existe pas. Veuillez contacter l'administrateur."))
        
        return sequence.next_by_id()

    def _detect_workflow_circuit(self):
        """Détecte automatiquement le circuit de validation selon les règles métier"""
        self.ensure_one()
        
        if not self.workflow_type_id or not self.amount:
            return None
        
        # Recherche des règles de routage pour ce type de workflow
        # Tri par séquence (priorité) - la première règle qui matche est utilisée
        routing_rules = self.env['workflow.routing.rule'].search([
            ('workflow_type_id', '=', self.workflow_type_id.id),
            ('active', '=', True),
        ], order='sequence, id')
        
        # Parcourir les règles et trouver celle qui correspond au montant
        for rule in routing_rules:
            # Vérifier les conditions de montant
            min_ok = not rule.amount_min or self.amount >= rule.amount_min
            max_ok = not rule.amount_max or self.amount < rule.amount_max
            
            if min_ok and max_ok:
                # Règle trouvée - retourner le circuit associé
                return rule.workflow_definition_id.id if rule.workflow_definition_id else None
        
        # Aucune règle ne correspond - retourner None
        return None

    def action_save_draft(self):
        """Sauvegarde la demande en brouillon"""
        self.ensure_one()
        
        # Génération de la référence
        reference = self._generate_reference()
        
        # Création de la demande en état brouillon
        request = self.env['workflow.request'].create({
            'name': reference,
            'client_number': self.client_number,
            'account_number': self.account_number,
            'client_name': self.client_name,
            'credit_type': self.credit_type,
            'subject': self.subject,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'duration_months': self.duration_months,
            'priority': self.priority,
            'description': self.description,
            'workflow_type_id': self.workflow_type_id.id,
            'workflow_definition_id': self._detect_workflow_circuit(),
            'requester_id': self.env.user.id,
            'state': 'draft',
            'attachment_ids': [(6, 0, self.attachment_ids.ids)],
        })
        
        # Message de confirmation dans le chatter
        request.message_post(
            body=_("✅ Demande créée en brouillon par %s") % self.env.user.name,
            message_type='notification'
        )
        
        # Retourne une redirection vers le backend Odoo avec menu
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#id={request.id}&model=workflow.request&view_type=form',
            'target': 'self',
        }

    def _create_workflow_approvals(self, request):
        """Crée automatiquement toutes les approbations pour les niveaux du circuit"""
        if not request.workflow_definition_id:
            return
        
        # Récupérer tous les niveaux du circuit, triés par séquence
        levels = self.env['workflow.level'].search([
            ('workflow_definition_id', '=', request.workflow_definition_id.id),
            ('active', '=', True)
        ], order='sequence, id')
        
        if not levels:
            return
        
        # Créer une approbation pour chaque niveau
        for idx, level in enumerate(levels):
            # IMPORTANT : Seul le premier niveau est actif (pending)
            # Les autres niveaux sont en attente du précédent (waiting)
            approval_state = 'pending' if idx == 0 else 'waiting'
            
            # Déterminer l'approbateur pour ce niveau
            # Si le niveau a des approbateurs assignés, prendre le premier
            # Sinon, utiliser l'admin par défaut
            if level.approver_ids:
                approver = level.approver_ids[0]
            else:
                approver = self.env.ref('base.user_admin', raise_if_not_found=False)
                if not approver:
                    approver = self.env['res.users'].search([('active', '=', True)], limit=1)
            
            self.env['workflow.request.approval'].create({
                'name': f"Approbation {level.name} - {request.name}",
                'workflow_request_id': request.id,
                'workflow_level_id': level.id,
                'approver_id': approver.id,
                'state': approval_state,
                'comments': '',
            })
        
        return len(levels)

    def action_submit_request(self):
        """Soumet la demande directement"""
        self.ensure_one()
        
        # Validation des champs obligatoires
        if not self.client_number or not self.account_number or not self.client_name:
            raise UserError(_("Veuillez remplir tous les champs obligatoires de la section Informations client."))
        
        if not self.subject or not self.amount:
            raise UserError(_("Veuillez renseigner l'objet et le montant de la demande."))
        
        # Génération de la référence
        reference = self._generate_reference()
        
        # Création de la demande en état soumis
        request = self.env['workflow.request'].create({
            'name': reference,
            'client_number': self.client_number,
            'account_number': self.account_number,
            'client_name': self.client_name,
            'credit_type': self.credit_type,
            'subject': self.subject,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'duration_months': self.duration_months,
            'priority': self.priority,
            'description': self.description,
            'workflow_type_id': self.workflow_type_id.id,
            'workflow_definition_id': self._detect_workflow_circuit(),
            'requester_id': self.env.user.id,
            'state': 'submitted',  # Directement en état soumis
            'attachment_ids': [(6, 0, self.attachment_ids.ids)],
        })
        
        # Créer automatiquement toutes les approbations pour les niveaux du circuit
        nb_levels = self._create_workflow_approvals(request)
        
        # Message de confirmation dans le chatter
        circuit_info = ""
        if request.workflow_definition_id:
            circuit_info = f"<br/>Circuit: <strong>{request.workflow_definition_id.name}</strong> ({nb_levels or 0} niveaux)"
        
        request.message_post(
            body=_("🚀 Demande soumise par %s%s") % (self.env.user.name, circuit_info),
            message_type='notification'
        )
        
        # Retourne une redirection vers le backend Odoo avec menu
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#id={request.id}&model=workflow.request&view_type=form',
            'target': 'self',
        }
