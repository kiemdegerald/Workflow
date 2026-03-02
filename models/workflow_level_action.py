# -*- coding: utf-8 -*-
from odoo import models, fields, api


class WorkflowLevelAction(models.Model):
    _name = 'workflow.level.action'
    _description = 'Action disponible à un niveau de validation'
    _order = 'sequence, id'

    # ── Libellé ───────────────────────────────────────────────────────────
    name = fields.Char(
        string='Libellé du bouton',
        required=True,
        help='Texte affiché sur le bouton (ex: Approuver, Valider, Refuser...)',
    )

    sequence = fields.Integer(string='Ordre', default=10)

    # ── Niveau parent ─────────────────────────────────────────────────────
    level_id = fields.Many2one(
        'workflow.level',
        string='Étape',
        required=True,
        ondelete='cascade',
    )

    # Champ dérivé pour pouvoir faire des domaines sur la cible
    workflow_definition_id = fields.Many2one(
        'workflow.definition',
        related='level_id.workflow_definition_id',
        store=True,
        readonly=True,
    )

    # ── Type d'action ─────────────────────────────────────────────────────
    action_type = fields.Selection([
        ('go_next',      'Approuver → passer au niveau suivant'),
        ('go_back',      'Retourner au niveau précédent'),
        ('reject',       'Refuser définitivement'),
        ('request_info', 'Demander des informations complémentaires'),
        ('complete',     'Valider (fin de circuit — dernier niveau)'),
    ], string="Type d'action", required=True, default='go_next',
       help=(
           "Détermine ce que fait le moteur quand l'approbateur clique ce bouton :\n"
           "• Approuver → active le niveau suivant dans la séquence\n"
           "• Retourner → réactive le niveau précédent\n"
           "• Refuser → clôture le circuit avec état 'Rejeté'\n"
           "• Demander info → garde le niveau actuel, notifie le demandeur\n"
           "• Valider fin → clôture le circuit avec état 'Approuvé'"
       ))

    # ── Étape cible (optionnel) ───────────────────────────────────────────
    target_level_id = fields.Many2one(
        'workflow.level',
        string='Étape cible (optionnel)',
        domain="[('workflow_definition_id', '=', workflow_definition_id)]",
        help=(
            "Étape précise vers laquelle diriger après cette action.\n"
            "Laisser vide : le moteur choisit automatiquement\n"
            "  • go_next → étape de séquence supérieure la plus proche\n"
            "  • go_back → étape de séquence inférieure la plus proche"
        ),
    )

    # ── Options d'affichage ───────────────────────────────────────────────
    color = fields.Selection([
        ('primary',   'Bleu (action principale)'),
        ('success',   'Vert (validation positive)'),
        ('danger',    'Rouge (refus / alerte)'),
        ('warning',   'Orange (retour / prudence)'),
        ('secondary', 'Gris (action neutre)'),
        ('info',      'Cyan (information)'),
    ], string='Couleur', default='primary')

    requires_comment = fields.Boolean(
        string='Commentaire obligatoire',
        default=True,
        help="L'approbateur doit saisir un commentaire avant de valider cette action.",
    )

    # ── Couleur CSS dérivée (utile pour la vue approbateur) ───────────────
    @api.depends('color')
    def _compute_css_class(self):
        mapping = {
            'primary':   'btn-primary',
            'success':   'btn-success',
            'danger':    'btn-danger',
            'warning':   'btn-warning',
            'secondary': 'btn-secondary',
            'info':      'btn-info',
        }
        for rec in self:
            rec.css_class = mapping.get(rec.color, 'btn-primary')

    css_class = fields.Char(
        string='Classe CSS',
        compute='_compute_css_class',
        store=False,
    )
