# -*- coding: utf-8 -*-
from odoo import models, fields, api


class WorkflowLevel(models.Model):
    _name = 'workflow.level'
    _description = 'Étape de validation du Workflow'
    _order = 'workflow_definition_id, sequence, id'

    # ── Informations de base ──────────────────────────────────────────────
    name = fields.Char(string="Nom de l'étape", required=True)
    workflow_definition_id = fields.Many2one(
        'workflow.definition',
        string='Circuit de Workflow',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='Séquence', required=True, default=10)
    description = fields.Text(string='Description / Rôle de cette étape')
    active = fields.Boolean(string='Actif', default=True)

    # ── Approbateurs ──────────────────────────────────────────────────────
    approver_ids = fields.Many2many(
        'res.users',
        'workflow_level_approver_rel',
        'level_id',
        'user_id',
        string='Approbateurs',
        help=(
            'Utilisateurs autorisés à valider à cette étape.\n'
            'Si plusieurs : chacun reçoit sa propre demande de validation.'
        ),
    )
    require_all_approvers = fields.Boolean(
        string='Tous les approbateurs requis',
        default=True,
        help=(
            'Coché : tous les approbateurs de cette étape doivent valider.\n'
            'Décoché : un seul approbateur suffit pour passer à l\'étape suivante.'
        ),
    )

    # ── Actions configurables ─────────────────────────────────────────────
    action_ids = fields.One2many(
        'workflow.level.action',
        'level_id',
        string='Actions disponibles',
        help='Boutons que verront les approbateurs à cette étape.',
    )

    # ── Compteurs (affichage dans le tree du circuit) ─────────────────────
    approver_count = fields.Integer(
        string='Nb. Approbateurs',
        compute='_compute_counts',
        store=True,
    )
    action_count = fields.Integer(
        string='Nb. Actions',
        compute='_compute_counts',
        store=True,
    )

    @api.depends('approver_ids', 'action_ids')
    def _compute_counts(self):
        for rec in self:
            rec.approver_count = len(rec.approver_ids)
            rec.action_count = len(rec.action_ids)

    # ── Action pour ouvrir le formulaire en popup ────────────────────────
    def action_open_form(self):
        """Ouvre le formulaire de l'étape en popup.
        Les modifications sont sauvegardées directement en base de données,
        indépendamment du formulaire du circuit parent.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'⚙️ Étape — {self.name}',
            'res_model': 'workflow.level',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {'dialog_size': 'large'},
        }
