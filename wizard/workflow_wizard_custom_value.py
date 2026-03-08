# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WorkflowWizardCustomValue(models.TransientModel):
    """Ligne de valeur de champ personnalisé dans le wizard de création de demande."""
    _name = 'workflow.wizard.custom.value'
    _description = 'Valeur champ personnalisé (wizard)'
    _order = 'sequence, id'

    wizard_id = fields.Many2one(
        'workflow.request.wizard',
        string='Wizard',
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
        string='Champ',
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
    placeholder = fields.Char(
        related='custom_field_id.placeholder',
        readonly=True,
    )
    selection_options = fields.Text(
        related='custom_field_id.selection_options',
        readonly=True,
    )

    # ── Valeurs saisies par l'utilisateur ────────────────────────────
    value_char = fields.Char(string='Valeur')
    value_text = fields.Text(string='Valeur')
    value_integer = fields.Integer(string='Valeur')
    value_float = fields.Float(string='Valeur')
    value_boolean = fields.Boolean(string='Valeur')
    value_date = fields.Date(string='Valeur')
    value_datetime = fields.Datetime(string='Valeur')
    value_selection = fields.Char(string='Valeur')

    # Champ calculé/écritable pour saisir la valeur dans la liste (évite column_invisible)
    value_display = fields.Char(
        string='Valeur',
        compute='_compute_value_display',
        inverse='_set_value_display',
        store=False,
    )
    value_hint = fields.Char(
        string='Indication',
        compute='_compute_value_hint',
        store=False,
    )
    type_label = fields.Char(
        string='Type',
        compute='_compute_type_label',
        store=False,
    )
    value_bool_sel = fields.Selection(
        selection=[('Oui', 'Oui'), ('Non', 'Non')],
        string='Valeur (Oui/Non)',
        compute='_compute_value_bool_sel',
        inverse='_set_value_bool_sel',
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

    def _set_value_display(self):
        """Inverse : stocke la valeur saisie dans le bon champ selon field_type."""
        for rec in self:
            val = rec.value_display or ''
            ft = rec.field_type
            if ft == 'char':
                rec.value_char = val
            elif ft == 'text':
                rec.value_text = val
            elif ft == 'integer':
                try:
                    rec.value_integer = int(val)
                except (ValueError, TypeError):
                    rec.value_integer = 0
            elif ft == 'float':
                try:
                    rec.value_float = float(val.replace(',', '.'))
                except (ValueError, TypeError):
                    rec.value_float = 0.0
            elif ft == 'boolean':
                rec.value_boolean = val.strip().lower() in ('oui', 'true', '1', 'yes')
            elif ft == 'date':
                rec.value_date = val or False
            elif ft == 'datetime':
                rec.value_datetime = val or False
            elif ft == 'selection':
                rec.value_selection = val

    @api.depends('placeholder', 'field_type')
    def _compute_value_hint(self):
        """Indication affichée sous forme de conseil : placeholder configuré ou texte par défaut selon le type."""
        defaults = {
            'char':     'Texte libre',
            'text':     'Texte long',
            'integer':  'Nombre entier (ex: 12)',
            'float':    'Décimal (ex: 3.5)',
            'boolean':  '→ Saisissez : Oui  ou  Non',
            'date':     'Date (AAAA-MM-JJ)',
            'datetime': 'Date et heure',
            'selection': 'Choisir une option',
        }
        for rec in self:
            rec.value_hint = rec.placeholder or defaults.get(rec.field_type, '')

    @api.depends('field_type')
    def _compute_type_label(self):
        labels = {
            'char': 'Texte court',
            'text': 'Texte long',
            'integer': 'Nombre entier',
            'float': 'Décimal',
            'boolean': 'Oui / Non',
            'date': 'Date',
            'datetime': 'Date et heure',
            'selection': 'Liste',
        }
        for rec in self:
            rec.type_label = labels.get(rec.field_type, rec.field_type or '')
    @api.depends('field_type', 'value_boolean')
    def _compute_value_bool_sel(self):
        for rec in self:
            if rec.field_type == 'boolean':
                rec.value_bool_sel = 'Oui' if rec.value_boolean else 'Non'
            else:
                rec.value_bool_sel = False

    def _set_value_bool_sel(self):
        for rec in self:
            rec.value_boolean = (rec.value_bool_sel == 'Oui')