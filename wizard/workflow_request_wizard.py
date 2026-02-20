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
        """Détecte et affiche le circuit qui sera utilisé (simulation pour l'instant)"""
        for wizard in self:
            if wizard.amount and wizard.workflow_type_id:
                # Simulation de la détection du circuit
                amount = wizard.amount
                if amount < 5000000:
                    circuit = "Circuit A (< 5M)"
                    color = "info"
                elif amount < 25000000:
                    circuit = "Circuit B (5M - 25M)"
                    color = "primary"
                elif amount < 100000000:
                    circuit = "Circuit C (25M - 100M)"
                    color = "warning"
                else:
                    circuit = "Circuit D (> 100M)"
                    color = "danger"
                
                wizard.detected_circuit_info = f'''
                    <div class="alert alert-{color}" style="margin: 0; padding: 0.75rem; border-radius: 8px;">
                        <i class="fa fa-info-circle"></i> <strong>{circuit}</strong> sera automatiquement assigné
                    </div>
                '''
            else:
                wizard.detected_circuit_info = False

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
        
        # Pour l'instant, retourne None (logique métier sera implémentée plus tard)
        # La logique finale utilisera les règles de routage configurées
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
        
        # Message de confirmation dans le chatter
        circuit_info = ""
        if request.workflow_definition_id:
            circuit_info = f"<br/>Circuit: <strong>{request.workflow_definition_id.name}</strong>"
        
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
