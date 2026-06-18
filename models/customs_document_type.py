# -*- coding: utf-8 -*-

from odoo import models, fields

class CustomsDocumentType(models.Model):
    _name = 'customs.document.type'
    _description = 'Customs Document Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    name = fields.Char(string='Document Name', required=True, translate=True, tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True)
    name_tr = fields.Char(string='Turkish Name', tracking=True, help="Turkish translation label for the document type.")
    description = fields.Text(string='Description', tracking=True)
    default_responsible_party = fields.Selection([
        ('supplier', 'Supplier/Vendor'),
        ('broker', 'Customs Broker'),
        ('forwarder', 'Freight Forwarder'),
        ('carrier', 'Carrier'),
        ('manufacturer', 'Manufacturer'),
        ('internal', 'Internal'),
    ], string='Default Responsible Party', default='supplier', tracking=True)
    default_requirement_level = fields.Selection([
        ('mandatory', 'Mandatory'),
        ('optional', 'Optional'),
    ], string='Default Requirement Level', default='mandatory', tracking=True)
    original_normally_required = fields.Boolean(string='Original Normally Required', default=False, tracking=True)
    sequence = fields.Integer(string='Sequence', default=10, tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        index=True,
        tracking=True,
        help="If set, this document type is specific to the company. Otherwise, it is shared globally."
    )

    _sql_constraints = [
        ('code_unique', 'unique(code, company_id)', 'The code of the document type must be unique per company (or global).')
    ]
