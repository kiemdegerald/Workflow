# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class WorkflowCourrierEntrant(models.Model):
    _name = 'workflow.courrier.entrant'
    _description = 'Courrier Entrant'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_reception desc, id desc'

    # ── Référence ────────────────────────────────────────────────────────
    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default='Nouveau',
        tracking=True,
    )

    # ── Informations courrier ─────────────────────────────────────────────
    objet = fields.Char(
        string='Objet',
        required=True,
        tracking=True,
    )
    date_reception = fields.Date(
        string='Date de réception',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    expediteur = fields.Char(
        string='Expéditeur',
        required=True,
        tracking=True,
    )
    origine = fields.Char(
        string='Origine / Organisation',
        tracking=True,
    )
    type_courrier = fields.Selection([
        ('lettre',      'Lettre'),
        ('email',       'Email'),
        ('rapport',     'Rapport'),
        ('facture',     'Facture'),
        ('demande',     'Demande'),
        ('notification','Notification'),
        ('autre',       'Autre'),
    ], string='Type de courrier', default='lettre', required=True, tracking=True)

    priorite = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Urgent'),
        ('2', 'Critique'),
    ], string='Priorité', default='0', tracking=True)

    # ── Attribution interne ───────────────────────────────────────────────
    destinataire_id = fields.Many2one(
        'res.users',
        string='Destinataire interne',
        tracking=True,
    )
    service_id = fields.Many2one(
        'res.partner',
        string='Service destinataire',
        domain=[('is_company', '=', True)],
        tracking=True,
    )
    secretaire_id = fields.Many2one(
        'res.users',
        string='Enregistré par',
        default=lambda self: self.env.user,
        readonly=True,
        tracking=True,
    )

    # ── Contenu ───────────────────────────────────────────────────────────
    description = fields.Text(
        string='Résumé / Observations',
        tracking=True,
    )
    instruction = fields.Text(
        string='Instructions de traitement',
        tracking=True,
    )

    # ── Pièces jointes ────────────────────────────────────────────────────
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'courrier_entrant_attachment_rel',
        'courrier_id',
        'attachment_id',
        string='Documents joints',
    )
    attachment_count = fields.Integer(
        string='Nombre de documents',
        compute='_compute_attachment_count',
    )

    # ── Circuit de validation ─────────────────────────────────────────────
    workflow_definition_id = fields.Many2one(
        'workflow.definition',
        string='Circuit de validation',
        tracking=True,
        domain="[('workflow_type_id.code', '=', 'COURRIER')]",
    )
    workflow_request_id = fields.Many2one(
        'workflow.request',
        string='Demande workflow liée',
        readonly=True,
        copy=False,
    )

    # ── Statut ────────────────────────────────────────────────────────────
    state = fields.Selection([
        ('recu',          'Reçu'),
        ('en_validation', 'En validation'),
        ('traite',        'Traité'),
        ('cloture',       'Clôturé'),
    ], string='État', default='recu', required=True, tracking=True)

    # ─────────────────────────────────────────────────────────────────────
    # Compute
    # ─────────────────────────────────────────────────────────────────────

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for rec in self:
            rec.attachment_count = len(rec.attachment_ids)

    # ─────────────────────────────────────────────────────────────────────
    # ORM
    # ─────────────────────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('workflow.courrier.entrant') or 'Nouveau'
        records = super().create(vals_list)
        records._link_attachments()
        return records

    def write(self, vals):
        result = super().write(vals)
        if 'attachment_ids' in vals:
            self._link_attachments()
        return result

    def unlink(self):
        """Supprimer le courrier et nettoyer toutes les données liées :
        approbations, demande workflow et pièces jointes.
        """
        # Collecter les workflow.request associés avant suppression
        requests = self.mapped('workflow_request_id').filtered(bool)

        # Supprimer les pièces jointes liées
        self.sudo().mapped('attachment_ids').unlink()

        # Supprimer d'abord le courrier lui-même
        result = super().unlink()

        # Supprimer les approbations puis la demande workflow orpheline
        if requests:
            requests.sudo().mapped('approval_ids').unlink()
            requests.sudo().unlink()

        return result

    def _link_attachments(self):
        """Lier les pièces jointes au record pour que les approbateurs y aient accès."""
        for rec in self:
            if rec.attachment_ids:
                rec.attachment_ids.sudo().write({
                    'res_model': self._name,
                    'res_id':    rec.id,
                })

    # ─────────────────────────────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────────────────────────────

    def action_soumettre(self):
        """Soumettre le courrier au circuit de validation."""
        self.ensure_one()
        if not self.workflow_definition_id:
            raise UserError("Veuillez sélectionner un circuit de validation avant de soumettre.")

        levels = self.workflow_definition_id.level_ids.sorted('sequence')
        if not levels:
            raise UserError("Le circuit sélectionné n'a aucun niveau configuré.")

        # Récupérer le type workflow COURRIER
        courrier_type = self.env['workflow.type'].search([('code', '=', 'COURRIER')], limit=1)
        if not courrier_type:
            raise UserError("Le type de workflow 'COURRIER' est introuvable. Vérifiez la configuration.")

        # Créer la demande workflow interne (moteur partagé)
        request = self.env['workflow.request'].create({
            'subject':                self.objet,
            'description':            self.description or '',
            'workflow_type_id':       courrier_type.id,
            'workflow_definition_id': self.workflow_definition_id.id,
            'requester_id':           self.env.user.id,
            'client_name':            self.expediteur,
            'state':                  'in_progress',
        })

        # Créer les approbations niveau par niveau
        first_seq = levels[0].sequence
        for level in levels:
            for approver in level.approver_ids:
                self.env['workflow.request.approval'].create({
                    'name':               '%s – %s – %s' % (self.name, level.name, approver.name),
                    'workflow_request_id': request.id,
                    'workflow_level_id':  level.id,
                    'approver_id':        approver.id,
                    'state':              'pending' if level.sequence == first_seq else 'waiting',
                })

        self.write({
            'workflow_request_id': request.id,
            'state':               'en_validation',
        })

        # Générer un token d'accès pour chaque pièce jointe
        # afin que les approbateurs puissent les visualiser sans droits spéciaux
        for att in self.attachment_ids:
            att_sudo = att.sudo()
            if not att_sudo.access_token:
                att_sudo._generate_access_token()

        self.message_post(
            body="Courrier soumis au circuit <b>%s</b>." % self.workflow_definition_id.name,
            subtype_xmlid='mail.mt_note',
        )
        return True

    def action_marquer_traite(self):
        """Marquer le courrier comme traité."""
        self.ensure_one()
        self.write({'state': 'traite'})
        self.message_post(body="Courrier marqué comme traité.", subtype_xmlid='mail.mt_note')

    def action_cloturer(self):
        """Clôturer le courrier."""
        self.ensure_one()
        self.write({'state': 'cloture'})
        self.message_post(body="Courrier clôturé.", subtype_xmlid='mail.mt_note')

    def action_reouvrir(self):
        """Remettre le courrier à l'état Reçu."""
        self.ensure_one()
        self.write({'state': 'recu', 'workflow_request_id': False})
        self.message_post(body="Courrier réouvert.", subtype_xmlid='mail.mt_note')

    def action_voir_documents(self):
        """Ouvrir les pièces jointes."""
        self.ensure_one()
        return {
            'type':      'ir.actions.act_window',
            'name':      'Documents joints',
            'res_model': 'ir.attachment',
            'view_mode': 'tree,form',
            'domain':    [('id', 'in', self.attachment_ids.ids)],
        }
