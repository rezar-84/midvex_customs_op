# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CustomsOperation(models.Model):
    _name = 'customs.operation'
    _description = 'Customs File'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New', tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        required=True, 
        default=lambda self: self.env.company
    )
    stage_id = fields.Many2one(
        'customs.stage', 
        string='Stage', 
        tracking=True, 
        group_expand='_read_group_stage_ids',
        copy=False
    )
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string='Priority', default='0', tracking=True)
    user_id = fields.Many2one(
        'res.users', 
        string='Responsible Employee', 
        default=lambda self: self.env.user, 
        tracking=True
    )

    # Party Relationships
    supplier_ids = fields.Many2many(
        'res.partner', 
        'customs_operation_supplier_rel', 
        'operation_id', 
        'partner_id', 
        string='Suppliers',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        tracking=True
    )
    broker_id = fields.Many2one(
        'res.partner', 
        string='Customs Broker',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        tracking=True
    )
    forwarder_id = fields.Many2one(
        'res.partner', 
        string='Freight Forwarder',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        tracking=True
    )
    carrier_id = fields.Many2one(
        'res.partner', 
        string='Carrier',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        tracking=True
    )

    # Document & Lines Relations
    purchase_order_ids = fields.Many2many(
        'purchase.order', 
        'customs_operation_purchase_rel', 
        'operation_id', 
        'purchase_id', 
        string='Purchase Orders',
        domain="[('company_id', '=', company_id)]",
        tracking=True
    )
    picking_ids = fields.Many2many(
        'stock.picking', 
        'customs_operation_picking_rel', 
        'operation_id', 
        'picking_id', 
        string='Incoming Shipments',
        domain="[('company_id', '=', company_id)]",
        tracking=True
    )
    operation_line_ids = fields.One2many(
        'customs.operation.line', 
        'operation_id', 
        string='Product Lines'
    )
    document_requirement_ids = fields.One2many(
        'customs.document.requirement', 
        'operation_id', 
        string='Document Requirements'
    )

    # Shipment Information
    operation_type = fields.Selection([
        ('import', 'Import'),
        ('export', 'Export'),
        ('transit', 'Transit'),
    ], string='Operation Type', default='import', required=True, tracking=True)
    transport_mode = fields.Selection([
        ('sea', 'Sea'),
        ('air', 'Air'),
        ('road', 'Road'),
        ('rail', 'Rail'),
    ], string='Transport Mode', tracking=True)
    incoterm_id = fields.Many2one(
        'account.incoterms', 
        string='Incoterm',
        tracking=True
    )
    origin_country_id = fields.Many2one(
        'res.country', 
        string='Country of Origin',
        tracking=True
    )
    departure_country_id = fields.Many2one(
        'res.country', 
        string='Country of Departure',
        tracking=True
    )
    destination_country_id = fields.Many2one(
        'res.country', 
        string='Country of Destination',
        tracking=True
    )
    customs_office = fields.Char(string='Customs Office', tracking=True)
    container_number = fields.Char(string='Container Number', tracking=True)
    booking_number = fields.Char(string='Booking Number', tracking=True)
    transport_document_number = fields.Char(string='Transport Document No.', help="Bill of Lading, AWB, CMR, etc.", tracking=True)

    # Dates
    document_deadline = fields.Date(string='Document Deadline', tracking=True)
    planned_departure_date = fields.Date(string='Planned Departure', tracking=True)
    actual_departure_date = fields.Date(string='Actual Departure', tracking=True)
    planned_arrival_date = fields.Date(string='Planned Arrival (ETA)', tracking=True)
    actual_arrival_date = fields.Date(string='Actual Arrival (ATA)', tracking=True)
    planned_clearance_date = fields.Date(string='Planned Clearance', tracking=True)
    actual_clearance_date = fields.Date(string='Actual Clearance', tracking=True)
    warehouse_delivery_date = fields.Date(string='Warehouse Delivery', tracking=True)

    # Customs Information
    customs_declaration_number = fields.Char(string='Customs Declaration No.', tracking=True)
    customs_declaration_date = fields.Date(string='Declaration Date', tracking=True)
    inspection_required = fields.Boolean(string='Inspection Required', default=False, tracking=True)
    laboratory_required = fields.Boolean(string='Laboratory Required', default=False, tracking=True)
    inspection_date = fields.Date(string='Inspection Date', tracking=True)
    release_date = fields.Date(string='Customs Release Date', tracking=True)

    # Computed Controls (Stubs / Initial implementation for Milestone 2)
    document_total = fields.Integer(string='Total Documents', compute='_compute_document_stats', store=True)
    document_approved_count = fields.Integer(string='Approved Documents', compute='_compute_document_stats', store=True)
    document_missing_count = fields.Integer(string='Missing Documents', compute='_compute_document_stats', store=True)
    document_rejected_count = fields.Integer(string='Rejected Documents', compute='_compute_document_stats', store=True)
    document_completion_percentage = fields.Float(string='Document Completion %', compute='_compute_document_stats', store=True)
    shipment_ready = fields.Boolean(string='Ready to Ship', compute='_compute_readiness', store=True)
    blocking_document_count = fields.Integer(string='Blocking Documents', compute='_compute_readiness', store=True)
    blocking_reason_text = fields.Text(string='Blocking Reasons', compute='_compute_readiness', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('customs.operation') or 'New'
        return super(CustomsOperation, self).create(vals_list)

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        company_id = self.env.context.get('default_company_id') or self.env.company.id
        return self.env['customs.stage'].search([
            '|', ('company_id', '=', False), ('company_id', '=', company_id)
        ])

    @api.depends('document_requirement_ids', 'document_requirement_ids.state')
    def _compute_document_stats(self):
        approved_states = {'approved', 'original_issued', 'original_dispatched', 'original_received', 'submitted_to_customs', 'accepted'}
        missing_states = {'not_requested', 'requested', 'vendor_preparing'}
        for op in self:
            total = len(op.document_requirement_ids)
            approved = sum(1 for doc in op.document_requirement_ids if doc.state in approved_states)
            missing = sum(1 for doc in op.document_requirement_ids if doc.state in missing_states)
            rejected = sum(1 for doc in op.document_requirement_ids if doc.state == 'rejected')
            
            op.document_total = total
            op.document_approved_count = approved
            op.document_missing_count = missing
            op.document_rejected_count = rejected
            op.document_completion_percentage = (approved / total * 100.0) if total > 0 else 0.0

    @api.depends('document_requirement_ids', 'document_requirement_ids.state', 'document_requirement_ids.is_blocking')
    def _compute_readiness(self):
        # Initial stub for Milestone 2: Mark ready if no requirements or if all completed
        # Detailed business logic and blocking reason text will be implemented in Milestone 4
        for op in self:
            op.shipment_ready = op.document_total == op.document_approved_count
            op.blocking_document_count = op.document_total - op.document_approved_count
            op.blocking_reason_text = _("Documents incomplete: %d of %d approved.") % (op.document_approved_count, op.document_total) if op.blocking_document_count > 0 else ""

    def action_view_purchase_orders(self):
        self.ensure_one()
        return {
            'name': _('Purchase Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.purchase_order_ids.ids)],
            'target': 'current',
        }

    def action_view_incoming_shipments(self):
        self.ensure_one()
        return {
            'name': _('Incoming Shipments'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.picking_ids.ids)],
            'target': 'current',
        }

    def action_view_document_requirements(self):
        self.ensure_one()
        return {
            'name': _('Document Requirements'),
            'type': 'ir.actions.act_window',
            'res_model': 'customs.document.requirement',
            'view_mode': 'list,form',
            'domain': [('operation_id', '=', self.id)],
            'context': {'default_operation_id': self.id},
            'target': 'current',
        }

    def action_view_missing_document_requirements(self):
        self.ensure_one()
        missing_states = ('not_requested', 'requested', 'vendor_preparing')
        return {
            'name': _('Missing Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'customs.document.requirement',
            'view_mode': 'list,form',
            'domain': [('operation_id', '=', self.id), ('state', 'in', missing_states)],
            'context': {'default_operation_id': self.id},
            'target': 'current',
        }
