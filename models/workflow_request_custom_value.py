# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WorkflowRequestCustomValue(models.Model):
    """Stocke les valeurs des champs personnalisés pour chaque demande."""
    _name = 'workflow.request.custom.value'
    _description = 'Valeur de champ personnalisé d\'une demande'
    _order = 'sequence, id'

    request_id = fields.Many2one(
        'workflow.request',
        string='Demande',
        required=True,
        ondelete='cascade',
    )
    custom_field_id = fields.Many2one(
        'workflow.custom.field',
        string='Champ',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        related='custom_field_id.sequence',
        store=True,
        readonly=True,
    )
    field_name = fields.Char(
        related='custom_field_id.name',
        string='Nom du champ',
        store=True,
        readonly=True,
    )
    field_type = fields.Selection(
        related='custom_field_id.field_type',
        string='Type',
        store=True,
        readonly=True,
    )
    required = fields.Boolean(
        related='custom_field_id.required',
        store=True,
        readonly=True,
    )

    # ── Champs de valeur (un seul sera rempli selon field_type) ──────
    value_char = fields.Char(string='Valeur texte')
    value_text = fields.Text(string='Valeur texte long')
    value_integer = fields.Integer(string='Valeur entier')
    value_float = fields.Float(string='Valeur décimal')
    value_boolean = fields.Boolean(string='Valeur oui/non')
    value_date = fields.Date(string='Valeur date')
    value_datetime = fields.Datetime(string='Valeur date/heure')
    value_selection = fields.Char(string='Valeur sélection')

    # Champ calculé pour l'affichage dans les listes (évite column_invisible)
    value_display = fields.Char(
        string='Valeur',
        compute='_compute_value_display',
        store=False,
    )

    @api.depends(
        'field_type', 'value_char', 'value_text', 'value_integer',
        'value_float', 'value_boolean', 'value_date', 'value_datetime', 'value_selection'
    )
    def _compute_value_display(self):
        for rec in self:
            ft = rec.field_type
            if ft == 'char':
                rec.value_display = rec.value_char or ''
            elif ft == 'text':
                rec.value_display = rec.value_text or ''
            elif ft == 'integer':
                rec.value_display = str(rec.value_integer) if rec.value_integer else ''
            elif ft == 'float':
                rec.value_display = str(rec.value_float) if rec.value_float else ''
            elif ft == 'boolean':
                rec.value_display = 'Oui' if rec.value_boolean else 'Non'
            elif ft == 'date':
                rec.value_display = str(rec.value_date) if rec.value_date else ''
            elif ft == 'datetime':
                rec.value_display = str(rec.value_datetime) if rec.value_datetime else ''
            elif ft == 'selection':
                rec.value_display = rec.value_selection or ''
            else:
                rec.value_display = ''
