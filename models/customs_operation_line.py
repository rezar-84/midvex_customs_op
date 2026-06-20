# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CustomsOperationLine(models.Model):
    _name = 'customs.operation.line'
    _description = 'Customs Operation Line'
    _order = 'id asc'

    operation_id = fields.Many2one(
        'customs.operation', 
        string='Customs File', 
        required=True, 
        ondelete='cascade', 
        index=True
    )
    purchase_order_line_id = fields.Many2one(
        'purchase.order.line', 
        string='Purchase Order Line'
    )
    product_id = fields.Many2one(
        'product.product', 
        string='Product', 
        required=True, 
        index=True
    )
    description = fields.Text(string='Product Description')
    customs_description = fields.Text(string='Customs Description')
    hs_code = fields.Char(string='HS/GTİP Code')
    country_of_origin_id = fields.Many2one(
        'res.country', 
        string='Country of Origin'
    )
    manufacturer_id = fields.Many2one(
        'res.partner', 
        string='Manufacturer',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )
    manufacturer_approval_number = fields.Char(string='Facility Approval Number')
    batch_number = fields.Char(string='Batch Number')
    production_date = fields.Date(string='Production Date')
    expiry_date = fields.Date(string='Expiry Date')
    quantity = fields.Float(string='Quantity', digits='Product Unit of Measure', default=1.0)
    uom_id = fields.Many2one(
        'uom.uom', 
        string='Unit of Measure'
    )
    net_weight = fields.Float(string='Net Weight (kg)', digits='Stock Weight', default=0.0)
    gross_weight = fields.Float(string='Gross Weight (kg)', digits='Stock Weight', default=0.0)
    package_count = fields.Integer(string='Package Count', default=1)
    package_type = fields.Char(string='Package Type')
    health_certificate_required = fields.Boolean(string='Health Certificate Required', default=False)
    analysis_required = fields.Boolean(string='Analysis Required', default=False)
    import_permit_required = fields.Boolean(string='Import Permit Required', default=False)
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one(
        'res.company', 
        related='operation_id.company_id', 
        string='Company', 
        store=True, 
        index=True
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            # Set default descriptions and HS code from product if available
            self.description = self.product_id.display_name
            self.uom_id = self.product_id.uom_id
            # Odoo 19 uses HS code field if defined, otherwise we just populate default values
            if hasattr(self.product_id, 'hs_code'):
                self.hs_code = self.product_id.hs_code

    @api.constrains('production_date', 'expiry_date')
    def _check_dates(self):
        for line in self:
            if line.production_date and line.expiry_date and line.production_date > line.expiry_date:
                raise ValidationError(_("The expiry date must be after the production date for product %s.", line.product_id.name))

    @api.constrains('hs_code', 'operation_id')
    def _check_gtip_format(self):
        import re
        for line in self:
            dest_country = line.operation_id.destination_country_id
            if dest_country and dest_country.code == 'TR' and line.hs_code:
                clean_hs = re.sub(r'[\s\.]', '', line.hs_code)
                if not clean_hs.isdigit() or len(clean_hs) != 12:
                    raise ValidationError(_("GTİP Code must consist of exactly 12 digits for Turkey imports. Product: %s") % line.product_id.name)

    @api.constrains('net_weight', 'gross_weight')
    def _check_weights(self):
        for line in self:
            if line.net_weight < 0 or line.gross_weight < 0:
                raise ValidationError(_("Weights cannot be negative values."))
            if line.net_weight > line.gross_weight:
                raise ValidationError(_("Net weight cannot exceed gross weight."))

    @api.constrains('quantity', 'package_count')
    def _check_quantities(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_("Quantity must be a positive value."))
            if line.package_count <= 0:
                raise ValidationError(_("Package count must be a positive value."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('operation_id'):
                op = self.env['customs.operation'].browse(vals['operation_id'])
                waiting_docs_stage = self.env.ref('midvex_customs_op.stage_waiting_docs', raise_if_not_found=False)
                waiting_docs_seq = waiting_docs_stage.sequence if waiting_docs_stage else 2
                if op.stage_id and op.stage_id.sequence > waiting_docs_seq:
                    raise ValidationError(
                        _("You cannot add product lines when the Customs File is past the 'Waiting for Documents' stage.")
                    )
        return super(CustomsOperationLine, self).create(vals_list)

    def write(self, vals):
        business_fields = {'product_id', 'description', 'hs_code', 'country_of_origin_id', 'manufacturer_id', 'quantity', 'net_weight', 'gross_weight'}
        if any(f in vals for f in business_fields):
            for line in self:
                op = line.operation_id
                waiting_docs_stage = self.env.ref('midvex_customs_op.stage_waiting_docs', raise_if_not_found=False)
                waiting_docs_seq = waiting_docs_stage.sequence if waiting_docs_stage else 2
                if op.stage_id and op.stage_id.sequence > waiting_docs_seq:
                    raise ValidationError(
                        _("You cannot modify product lines when the Customs File is past the 'Waiting for Documents' stage.")
                    )
        return super(CustomsOperationLine, self).write(vals)

    def unlink(self):
        for line in self:
            op = line.operation_id
            if op and op.is_sample_data:
                continue
            waiting_docs_stage = self.env.ref('midvex_customs_op.stage_waiting_docs', raise_if_not_found=False)
            waiting_docs_seq = waiting_docs_stage.sequence if waiting_docs_stage else 2
            if op.stage_id and op.stage_id.sequence > waiting_docs_seq:
                raise ValidationError(
                    _("You cannot delete product lines when the Customs File is past the 'Waiting for Documents' stage.")
                )
        return super(CustomsOperationLine, self).unlink()
