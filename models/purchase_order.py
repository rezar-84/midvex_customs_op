# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    customs_operation_ids = fields.Many2many(
        'customs.operation', 
        'customs_operation_purchase_rel', 
        'purchase_id', 
        'operation_id', 
        string='Import & Customs Operations'
    )
    customs_operation_count = fields.Integer(
        string='Import Operations Count', 
        compute='_compute_customs_operation_count'
    )
    is_import_purchase = fields.Boolean(
        string='Is Import Purchase', 
        compute='_compute_is_import_purchase', 
        store=True, 
        readonly=False,
        help='Automatically checked if the vendor is foreign.'
    )
    customs_required = fields.Boolean(
        string='Import Customs Required', 
        compute='_compute_customs_required',
        store=True,
        readonly=False,
        help='Checked if this purchase requires import compliance tracking.'
    )
    customs_operation_state = fields.Char(
        string='Customs Status', 
        compute='_compute_customs_summaries'
    )
    customs_document_completion_percentage = fields.Float(
        string='Customs Doc Completion %', 
        compute='_compute_customs_summaries'
    )
    customs_shipment_ready = fields.Boolean(
        string='Customs Shipment Ready', 
        compute='_compute_customs_summaries'
    )
    customs_blocking_reason_text = fields.Text(
        string='Customs Blocking Reasons', 
        compute='_compute_customs_summaries'
    )

    @api.depends('partner_id', 'company_id')
    def _compute_is_import_purchase(self):
        for order in self:
            if order.partner_id and order.partner_id.country_id and order.company_id and order.company_id.partner_id and order.company_id.partner_id.country_id:
                order.is_import_purchase = order.partner_id.country_id != order.company_id.partner_id.country_id
            else:
                order.is_import_purchase = False

    @api.depends('is_import_purchase', 'order_line.product_id', 'order_line.product_id.product_tmpl_id.customs_required')
    def _compute_customs_required(self):
        for order in self:
            if order.is_import_purchase:
                order.customs_required = True
            elif any(line.product_id.product_tmpl_id.customs_required for line in order.order_line if line.product_id):
                order.customs_required = True
            else:
                order.customs_required = False

    @api.depends('customs_operation_ids')
    def _compute_customs_operation_count(self):
        for order in self:
            order.customs_operation_count = len(order.customs_operation_ids)

    @api.depends('customs_operation_ids', 'customs_operation_ids.stage_id', 'customs_operation_ids.document_completion_percentage', 'customs_operation_ids.shipment_ready', 'customs_operation_ids.blocking_reason_text')
    def _compute_customs_summaries(self):
        for order in self:
            # Take the primary/first operation linked to show summary details
            op = order.customs_operation_ids[:1]
            if op:
                order.customs_operation_state = op.stage_id.name or _('New')
                order.customs_document_completion_percentage = op.document_completion_percentage
                order.customs_shipment_ready = op.shipment_ready
                order.customs_blocking_reason_text = op.blocking_reason_text
            else:
                order.customs_operation_state = _('Not Created')
                order.customs_document_completion_percentage = 0.0
                order.customs_shipment_ready = False
                order.customs_blocking_reason_text = ""

    def action_view_customs_operations(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('midvex_customs_op.action_customs_operation_all')
        if len(self.customs_operation_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.customs_operation_ids[0].id,
            })
        else:
            action.update({
                'domain': [('id', 'in', self.customs_operation_ids.ids)],
            })
        return action

    def action_create_customs_operation(self):
        self.ensure_one()
        if self.customs_operation_ids:
            return self.action_view_customs_operations()
        
        # Create a new Import Operation
        op = self._create_customs_operation_from_po()
        return {
            'name': _('Import & Customs Operation'),
            'type': 'ir.actions.act_window',
            'res_model': 'customs.operation',
            'view_mode': 'form',
            'res_id': op.id,
            'target': 'current',
        }

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            # Auto-create import operation if required, not already linked, and is an import transaction
            if (order.customs_required or order.is_import_purchase) and not order.customs_operation_ids:
                order.with_context(mail_create_nosubscribe=True)._create_customs_operation_from_po()
        return res

    def action_sync_customs_lines(self):
        for order in self:
            for op in order.customs_operation_ids:
                waiting_docs_stage = self.env.ref('midvex_customs_op.stage_waiting_docs', raise_if_not_found=False)
                waiting_docs_seq = waiting_docs_stage.sequence if waiting_docs_stage else 2
                if op.stage_id and op.stage_id.sequence > waiting_docs_seq:
                    raise ValidationError(_("You cannot sync lines to operation %s because it is past the 'Waiting for Documents' stage.") % op.name)
                op._sync_lines_from_po(order)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sync Completed'),
                'message': _('Product lines have been successfully synchronized from the linked Purchase Orders.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def _create_customs_operation_from_po(self):
        self.ensure_one()
        
        # Get defaults
        stage_draft = self.env['customs.stage'].search([('fold', '=', False)], order='sequence, id', limit=1)
        
        # Create Customs Operation
        op_vals = {
            'company_id': self.company_id.id,
            'stage_id': stage_draft.id if stage_draft else False,
            'user_id': self.user_id.id or self.env.user.id,
            'supplier_ids': [(4, self.partner_id.id)],
            'purchase_order_ids': [(4, self.id)],
            'incoterm_id': self.incoterm_id.id,
            'payment_term_id': self.payment_term_id.id,
            'currency_id': self.currency_id.id,
            'total_amount': self.amount_total,
            'planned_arrival_date': self.date_planned and self.date_planned.date(),
        }
        
        # Try to extract country of origin from vendor
        if self.partner_id.country_id:
            op_vals['origin_country_id'] = self.partner_id.country_id.id
            
        op = self.env['customs.operation'].create(op_vals)
        
        # Import Purchase Lines
        op_lines = []
        for line in self.order_line:
            if line.display_type: # Skip note and section lines
                continue
            
            line_vals = {
                'operation_id': op.id,
                'purchase_order_line_id': line.id,
                'product_id': line.product_id.id,
                'description': line.name,
                'quantity': line.product_qty,
                'uom_id': line.product_uom_id.id,
            }
            
            tmpl = line.product_id.product_tmpl_id
            if tmpl:
                line_vals.update({
                    'country_of_origin_id': tmpl.country_of_origin_id.id or op.origin_country_id.id,
                    'manufacturer_id': tmpl.manufacturer_id.id,
                    'health_certificate_required': tmpl.health_certificate_required,
                    'analysis_required': tmpl.analysis_required,
                    'import_permit_required': tmpl.import_permit_required,
                })
                # Check for Odoo standard hs_code
                if hasattr(line.product_id, 'hs_code'):
                    line_vals['hs_code'] = line.product_id.hs_code
                elif hasattr(tmpl, 'hs_code'):
                    line_vals['hs_code'] = tmpl.hs_code
            
            op_lines.append(line_vals)
            
        if op_lines:
            self.env['customs.operation.line'].create(op_lines)
            
        # Link generated stock pickings if any are already created
        pickings = self.env['stock.picking'].search([('purchase_id', '=', self.id)])
        if pickings:
            op.write({'picking_ids': [(4, p.id) for p in pickings]})
            
        # Generate default document requirements
        op._generate_default_document_requirements()
        
        # Log to chatter
        self.message_post(body=_("Linked to auto-created Import & Customs Operation: <a href=# data-oe-model=customs.operation data-oe-id=%d>%s</a>") % (op.id, op.name))
        
        return op


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(PurchaseOrderLine, self).create(vals_list)
        for line in lines:
            if line.order_id and not line.display_type:
                for op in line.order_id.customs_operation_ids:
                    waiting_docs_stage = self.env.ref('midvex_customs_op.stage_waiting_docs', raise_if_not_found=False)
                    waiting_docs_seq = waiting_docs_stage.sequence if waiting_docs_stage else 2
                    if not op.stage_id or op.stage_id.sequence <= waiting_docs_seq:
                        line_vals = {
                            'operation_id': op.id,
                            'purchase_order_line_id': line.id,
                            'product_id': line.product_id.id,
                            'description': line.name,
                            'quantity': line.product_qty,
                            'uom_id': line.product_uom_id.id,
                        }
                        tmpl = line.product_id.product_tmpl_id
                        if tmpl:
                            line_vals.update({
                                'country_of_origin_id': tmpl.country_of_origin_id.id or op.origin_country_id.id,
                                'manufacturer_id': tmpl.manufacturer_id.id,
                                'health_certificate_required': tmpl.health_certificate_required,
                                'analysis_required': tmpl.analysis_required,
                                'import_permit_required': tmpl.import_permit_required,
                            })
                            if hasattr(line.product_id, 'hs_code'):
                                line_vals['hs_code'] = line.product_id.hs_code
                            elif hasattr(tmpl, 'hs_code'):
                                line_vals['hs_code'] = tmpl.hs_code
                        self.env['customs.operation.line'].create(line_vals)
        return lines

    def write(self, vals):
        res = super(PurchaseOrderLine, self).write(vals)
        if 'product_qty' in vals or 'product_id' in vals:
            for line in self:
                customs_lines = self.env['customs.operation.line'].search([('purchase_order_line_id', '=', line.id)])
                for col in customs_lines:
                    op = col.operation_id
                    waiting_docs_stage = self.env.ref('midvex_customs_op.stage_waiting_docs', raise_if_not_found=False)
                    waiting_docs_seq = waiting_docs_stage.sequence if waiting_docs_stage else 2
                    if not op.stage_id or op.stage_id.sequence <= waiting_docs_seq:
                        col_vals = {}
                        if 'product_qty' in vals:
                            col_vals['quantity'] = vals['product_qty']
                        if 'product_id' in vals:
                            col_vals['product_id'] = vals['product_id']
                        if col_vals:
                            col.write(col_vals)
        return res

    def unlink(self):
        for line in self:
            customs_lines = self.env['customs.operation.line'].search([('purchase_order_line_id', '=', line.id)])
            for col in customs_lines:
                op = col.operation_id
                waiting_docs_stage = self.env.ref('midvex_customs_op.stage_waiting_docs', raise_if_not_found=False)
                waiting_docs_seq = waiting_docs_stage.sequence if waiting_docs_stage else 2
                if not op.stage_id or op.stage_id.sequence <= waiting_docs_seq:
                    col.unlink()
        return super(PurchaseOrderLine, self).unlink()
