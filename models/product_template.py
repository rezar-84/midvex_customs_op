# -*- coding: utf-8 -*-

from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    customs_required = fields.Boolean(
        string='Import Customs Required', 
        default=False, 
        help='Check this if this product requires import and customs compliance tracking.'
    )
    hs_code = fields.Char(
        string='HS/GTİP Code',
        help='Harmonized System Code used for customs declaration.'
    )
    country_of_origin_id = fields.Many2one(
        'res.country', 
        string='Default Country of Origin',
        help='The default country where the goods are produced.'
    )
    manufacturer_id = fields.Many2one(
        'res.partner', 
        string='Default Manufacturer',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help='The default manufacturer of this product.'
    )
    health_certificate_required = fields.Boolean(
        string='Health Certificate Required', 
        default=False,
        help='Check this if a Health Certificate is required for imports of this product.'
    )
    analysis_required = fields.Boolean(
        string='Certificate of Analysis (COA) Required', 
        default=False,
        help='Check this if a Certificate of Analysis (COA) is required for imports of this product.'
    )
    import_permit_required = fields.Boolean(
        string='Import Permit Required', 
        default=False,
        help='Check this if an Import Permit is required for imports of this product.'
    )
    original_documents_required = fields.Boolean(
        string='Original Documents Required', 
        default=False,
        help='Check this if physical original documents are required for imports of this product.'
    )


class ProductCategory(models.Model):
    _inherit = 'product.category'

    customs_required = fields.Boolean(
        string='Import Customs Required',
        default=False,
        help='Check this if products in this category require import and customs compliance tracking by default.'
    )
    health_certificate_required = fields.Boolean(
        string='Health Certificate Required',
        default=False,
        help='Default health certificate requirement for products in this category.'
    )
    analysis_required = fields.Boolean(
        string='Certificate of Analysis (COA) Required',
        default=False,
        help='Default certificate of analysis requirement for products in this category.'
    )
    import_permit_required = fields.Boolean(
        string='Import Permit Required',
        default=False,
        help='Default import permit requirement for products in this category.'
    )
    original_documents_required = fields.Boolean(
        string='Original Documents Required',
        default=False,
        help='Default physical original document requirement for products in this category.'
    )
