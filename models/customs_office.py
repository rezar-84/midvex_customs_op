# -*- coding: utf-8 -*-

from odoo import models, fields

class CustomsOffice(models.Model):
    _name = 'customs.office'
    _description = 'Customs Office'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'code, name'

    name = fields.Char(string='Office Name', required=True, translate=True, tracking=True)
    code = fields.Char(string='Office Code', required=True, copy=False, index=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        index=True,
        help="If set, this customs office is specific to the company. Otherwise, it is shared globally."
    )

    _code_uniq = models.Constraint('unique(code, company_id)', 'The customs office code must be unique per company!')
