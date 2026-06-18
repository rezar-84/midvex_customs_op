# -*- coding: utf-8 -*-

from odoo import models, fields

class CustomsStage(models.Model):
    _name = 'customs.stage'
    _description = 'Customs File Stage'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True, translate=True, tracking=True)
    sequence = fields.Integer(string='Sequence', default=10, tracking=True, help="Used to order stages.")
    fold = fields.Boolean(string='Folded in Kanban', default=False, tracking=True, help="This stage will be folded in the Kanban view.")
    is_closed = fields.Boolean(string='Closed Stage', default=False, tracking=True, help="Customs files in this stage are considered closed.")
    is_cancelled = fields.Boolean(string='Cancelled Stage', default=False, tracking=True, help="Customs files in this stage are considered cancelled.")
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        index=True,
        tracking=True,
        help="If set, this stage is specific to the company. Otherwise, it is shared globally."
    )
