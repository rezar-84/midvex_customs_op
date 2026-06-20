# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    customs_block_receipt_before_clearance = fields.Boolean(
        string='Block Warehouse Receipt Before Customs Clearance',
        config_parameter='midvex_customs_op.customs_block_receipt_before_clearance',
        default=False,
        help="If checked, warehouse workers cannot validate stock receipts until the linked customs operation is released/cleared."
    )

    def action_generate_sample_data(self):
        # 1. Create Sample Partners
        partner_obj = self.env['res.partner']
        supplier = partner_obj.create({
            'name': 'SAMPLE: Nippon Aqua Feed Corp.',
            'is_company': True,
            'company_id': self.env.company.id,
        })
        broker = partner_obj.create({
            'name': 'SAMPLE: Gümrükçü Ahmet ve Ortakları Müşavirlik',
            'is_company': True,
            'company_id': self.env.company.id,
        })
        forwarder = partner_obj.create({
            'name': 'SAMPLE: Global Logistics Solutions LLC',
            'is_company': True,
            'company_id': self.env.company.id,
        })
        carrier = partner_obj.create({
            'name': 'SAMPLE: Mediterranean Shipping Line',
            'is_company': True,
            'company_id': self.env.company.id,
        })
        manufacturer = partner_obj.create({
            'name': 'SAMPLE: Hokkaido Bio Production Factory',
            'is_company': True,
            'company_id': self.env.company.id,
        })

        # 2. Create Sample Product
        product = self.env['product.product'].create({
            'name': 'SAMPLE: Aquaculture Starter Feed EX-10',
            'type': 'consu',
        })

        # 3. Create Sample Operations
        op_obj = self.env['customs.operation']
        line_obj = self.env['customs.operation.line']
        
        stage_shipped = self.env.ref('midvex_customs_op.stage_shipped', raise_if_not_found=False)
        stage_customs = self.env.ref('midvex_customs_op.stage_customs_clearance', raise_if_not_found=False)
        stage_delivered = self.env.ref('midvex_customs_op.stage_delivered', raise_if_not_found=False)
        
        jp = self.env.ref('base.jp', raise_if_not_found=False)
        tr = self.env.ref('base.tr', raise_if_not_found=False)

        # A. Shipped Operation
        op_shipped = op_obj.create({
            'company_id': self.env.company.id,
            'production_status': 'loaded',
            'loading_date': fields.Date.today() - datetime.timedelta(days=5),
            'planned_departure_date': fields.Date.today() - datetime.timedelta(days=3),
            'actual_departure_date': fields.Date.today() - datetime.timedelta(days=3),
            'planned_arrival_date': fields.Date.today() + datetime.timedelta(days=7),
            'bl_number': 'SAMPLE-BL-98765',
            'container_number': 'CONT-9876543',
            'seal_number': 'SEAL-0001',
            'vessel_name': 'OCEAN EXPLORER',
            'tracking_link': 'https://www.searates.com/container/tracking/?container=CONT-9876543',
            'supplier_ids': [(4, supplier.id)],
            'broker_id': broker.id,
            'forwarder_id': forwarder.id,
            'carrier_id': carrier.id,
            'transport_mode': 'sea',
            'origin_country_id': jp.id if jp else False,
            'departure_country_id': jp.id if jp else False,
            'destination_country_id': tr.id if tr else False,
            'is_sample_data': True,
        })
        line_obj.create({
            'operation_id': op_shipped.id,
            'product_id': product.id,
            'quantity': 12000.0,
            'health_certificate_required': True,
            'analysis_required': True,
            'import_permit_required': False,
        })
        op_shipped._generate_default_document_requirements()
        if stage_shipped:
            op_shipped.write({'stage_id': stage_shipped.id})

        # B. Customs Clearance Operation with Correction Required
        op_customs = op_obj.create({
            'company_id': self.env.company.id,
            'customs_status': 'opened',
            'customs_declaration_number': '26340500IM012345',
            'customs_declaration_date': fields.Date.today(),
            'planned_arrival_date': fields.Date.today() - datetime.timedelta(days=3),
            'actual_arrival_date': fields.Date.today() - datetime.timedelta(days=3),
            'bl_number': 'SAMPLE-BL-11223',
            'supplier_ids': [(4, supplier.id)],
            'broker_id': broker.id,
            'transport_mode': 'sea',
            'origin_country_id': jp.id if jp else False,
            'departure_country_id': jp.id if jp else False,
            'destination_country_id': tr.id if tr else False,
            'is_sample_data': True,
        })
        line_obj.create({
            'operation_id': op_customs.id,
            'product_id': product.id,
            'quantity': 15000.0,
            'health_certificate_required': True,
            'analysis_required': True,
        })
        op_customs._generate_default_document_requirements()
        
        # Set some document states to showcase correction required
        for req in op_customs.document_requirement_ids:
            if req.document_type_id.code == 'INV':
                req.write({'state': 'approved'})
            elif req.document_type_id.code == 'HC':
                req.write({
                    'state': 'correction_required',
                    'rejection_reason': 'Health certificate signature is missing on page 2.'
                })
        if stage_customs:
            op_customs.write({'stage_id': stage_customs.id})

        # C. Delivered Operation with Damages
        op_delivered = op_obj.create({
            'company_id': self.env.company.id,
            'warehouse_received': True,
            'warehouse_received_date': fields.Date.today(),
            'missing_packages': True,
            'damaged_product': True,
            'damage_description': 'Torn bags during discharge. 5 bags of feed damaged.',
            'cost_freight': 1200.00,
            'cost_customs_tax': 450.00,
            'cost_broker_expenses': 250.00,
            'cost_stamp_tax': 75.00,
            'cost_storage': 150.00,
            'cost_exchange_diff': 0.00,
            'cost_other': 50.00,
            'accounting_status': 'waiting_invoice',
            'supplier_ids': [(4, supplier.id)],
            'broker_id': broker.id,
            'transport_mode': 'sea',
            'origin_country_id': jp.id if jp else False,
            'departure_country_id': jp.id if jp else False,
            'destination_country_id': tr.id if tr else False,
            'is_sample_data': True,
        })
        line_obj.create({
            'operation_id': op_delivered.id,
            'product_id': product.id,
            'quantity': 10000.0,
            'health_certificate_required': False,
            'analysis_required': False,
        })
        op_delivered._generate_default_document_requirements()
        if stage_delivered:
            op_delivered.write({'stage_id': stage_delivered.id})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Sample data generated successfully.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_cleanup_sample_data(self):
        # Delete sample operations (cascade deletes lines and requirements)
        sample_ops = self.env['customs.operation'].search([('is_sample_data', '=', True)])
        sample_ops.unlink()

        # Delete sample partners
        sample_partners = self.env['res.partner'].search([('name', '=like', 'SAMPLE:%')])
        sample_partners.unlink()

        # Delete sample product
        sample_products = self.env['product.product'].search([('name', '=like', 'SAMPLE:%')])
        sample_templates = self.env['product.template'].search([('name', '=like', 'SAMPLE:%')])
        sample_products.unlink()
        sample_templates.unlink()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Sample data cleaned up successfully.'),
                'type': 'success',
                'sticky': False,
            }
        }

