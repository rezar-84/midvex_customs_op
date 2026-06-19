# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
from markupsafe import Markup, escape

class CustomsOperation(models.Model):
    _name = 'customs.operation'
    _description = 'Customs File'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    _sql_constraints = [
        ('name_unique', 'unique(name, company_id)', 'The Customs File reference must be unique per company!')
    ]

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New', tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True, index=True)
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
        copy=False,
        index=True
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
        tracking=True,
        index=True
    )
    color = fields.Integer(string='Color Index', default=0)

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
        tracking=True,
        index=True
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

    # Computed Controls
    document_total = fields.Integer(string='Total Documents', compute='_compute_document_stats', store=True)
    document_approved_count = fields.Integer(string='Approved Documents', compute='_compute_document_stats', store=True)
    document_missing_count = fields.Integer(string='Missing Documents', compute='_compute_document_stats', store=True)
    document_rejected_count = fields.Integer(string='Rejected Documents', compute='_compute_document_stats', store=True)
    document_completion_percentage = fields.Float(string='Document Completion %', compute='_compute_document_stats', store=True)
    
    shipment_ready = fields.Boolean(string='Ready to Ship', compute='_compute_readiness', store=True)
    blocking_document_count = fields.Integer(string='Blocking Documents', compute='_compute_readiness', store=True)
    blocking_reason_text = fields.Text(string='Blocking Reasons', compute='_compute_readiness')

    # Override Fields
    is_overridden = fields.Boolean(string='Readiness Overridden', default=False, tracking=True)
    override_reason = fields.Text(string='Override Reason', tracking=True)
    override_user_id = fields.Many2one('res.users', string='Overridden By', readonly=True, tracking=True)
    override_date = fields.Datetime(string='Override Date', readonly=True, tracking=True)

    # Production & Preparation Fields
    production_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_production', 'In Production'),
        ('ready', 'Ready'),
        ('loaded', 'Loaded'),
        ('delayed', 'Delayed'),
        ('cancelled', 'Cancelled')
    ], string='Production Status', default='not_started', tracking=True)
    production_ready_date = fields.Date(string='Production Ready Date', tracking=True)
    goods_prepared_date = fields.Date(string='Goods Prepared Date', tracking=True)
    loading_date = fields.Date(string='Loading Date', tracking=True)

    # Purchase & Supplier Commercial Fields
    supplier_ref = fields.Char(string='Supplier Order Reference', tracking=True)
    manufacturer_id = fields.Many2one(
        'res.partner',
        string='Manufacturer/Factory',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        tracking=True
    )
    payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Payment Term',
        tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        compute='_compute_commercial_defaults',
        store=True,
        readonly=False,
        tracking=True
    )
    total_amount = fields.Monetary(
        string='Total Amount',
        currency_field='currency_id',
        compute='_compute_commercial_defaults',
        store=True,
        readonly=False,
        tracking=True
    )

    # Logistics & Tracking Additional Fields
    seal_number = fields.Char(string='Seal Number', tracking=True)
    bl_number = fields.Char(string='Bill of Lading (B/L) Number', tracking=True)
    vessel_name = fields.Char(string='Vessel Name', tracking=True)
    tracking_link = fields.Char(string='Logistics Tracking Link', tracking=True)

    # Customs Sub-Status (Process Stage details)
    customs_status = fields.Selection([
        ('waiting', 'Documents Waiting'),
        ('opened', 'Declaration Opened'),
        ('inspection', 'Inspection'),
        ('tax_paid', 'Tax Paid'),
        ('released', 'Released / Clearance Completed'),
        ('completed', 'Completed')
    ], string='Customs Sub-Status', tracking=True)

    # Accounting & Costs
    cost_freight = fields.Monetary(string='Freight Cost', currency_field='currency_id', tracking=True)
    cost_customs_tax = fields.Monetary(string='Customs Tax', currency_field='currency_id', tracking=True)
    cost_broker_expenses = fields.Monetary(string='Customs Broker Expenses', currency_field='currency_id', tracking=True)
    cost_stamp_tax = fields.Monetary(string='Stamp Tax', currency_field='currency_id', tracking=True)
    cost_storage = fields.Monetary(string='Storage / Demurrage', currency_field='currency_id', tracking=True)
    cost_exchange_diff = fields.Monetary(string='Exchange-Rate Difference', currency_field='currency_id', tracking=True)
    cost_other = fields.Monetary(string='Other Costs', currency_field='currency_id', tracking=True)
    cost_total = fields.Monetary(
        string='Total Costs',
        currency_field='currency_id',
        compute='_compute_cost_total',
        store=True
    )
    accounting_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('waiting_invoice', 'Waiting Invoice'),
        ('waiting_payment', 'Waiting Payment'),
        ('completed', 'Completed')
    ], string='Accounting Closing Status', default='not_started', tracking=True)

    # Warehouse Receiving
    warehouse_received = fields.Boolean(string='Warehouse Received', default=False, tracking=True)
    warehouse_received_date = fields.Date(string='Warehouse Received Date', tracking=True)
    missing_packages = fields.Boolean(string='Missing Packages/Boxes', default=False, tracking=True)
    damaged_product = fields.Boolean(string='Damaged Product', default=False, tracking=True)
    damage_description = fields.Text(string='Damage / Missing Description', tracking=True)
    warehouse_photo_ids = fields.Many2many(
        'ir.attachment',
        'customs_operation_warehouse_photo_rel',
        'operation_id',
        'attachment_id',
        string='Photo Attachments'
    )
    delivery_note_ids = fields.Many2many(
        'ir.attachment',
        'customs_operation_delivery_note_rel',
        'operation_id',
        'attachment_id',
        string='Delivery Notes / POD'
    )

    is_draft = fields.Boolean(string='Is Draft Stage', compute='_compute_is_draft', store=True)

    vendor_bill_ids = fields.One2many(
        'account.move',
        'customs_operation_id',
        string='Vendor Bills',
        domain=[('move_type', '=', 'in_invoice')]
    )
    vendor_bill_count = fields.Integer(
        string='Vendor Bills Count',
        compute='_compute_vendor_bill_count'
    )
    sale_order_ids = fields.Many2many(
        'sale.order',
        string='Sales Orders',
        compute='_compute_sale_orders',
        store=True,
        help="Sales orders linked to the purchase orders via procurement group or origin tracing."
    )
    sale_order_count = fields.Integer(
        string='Sales Orders Count',
        compute='_compute_sale_order_count'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('customs.operation') or 'New'
        records = super(CustomsOperation, self).create(vals_list)
        
        # Trigger activities for initial values if appropriate
        for op in records:
            if op.bl_number:
                op._create_operation_activity(
                    'mail.mail_activity_data_todo',
                    _("B/L Uploaded - Action Required"),
                    _("Bill of Lading %s has been uploaded. Please notify the customs broker to prepare the declaration.") % op.bl_number,
                    op.user_id.id
                )
            if op.warehouse_received:
                purchasing_user_id = op.user_id.id
                if op.purchase_order_ids:
                    purchasing_user_id = op.purchase_order_ids[0].user_id.id
                op._create_operation_activity(
                    'mail.mail_activity_data_todo',
                    _("Warehouse Delivery Completed"),
                    _("Warehouse entry has been recorded for operation %s. Please review and process for closing.") % op.name,
                    purchasing_user_id
                )
            if op.damaged_product or op.missing_packages:
                manager_group = self.env.ref('midvex_customs_op.group_customs_manager', raise_if_not_found=False)
                manager_users = manager_group.users if manager_group else self.env['res.users']
                notify_user = manager_users[0].id if manager_users else op.user_id.id
                op._create_operation_activity(
                    'mail.mail_activity_data_todo',
                    _("Discrepancy / Damaged Cargo Recorded"),
                    _("Damaged product or missing packages have been reported for operation %s. Description: %s") % (
                        op.name, op.damage_description or _("No description provided.")
                    ),
                    notify_user
                )
            if op.planned_arrival_date:
                eta_date = fields.Date.to_date(op.planned_arrival_date)
                days_left = (eta_date - fields.Date.today()).days
                if 0 <= days_left <= 3:
                    op._create_operation_activity(
                        'mail.mail_activity_data_todo',
                        _("ETA Approaching"),
                        _("The arrival date (ETA) for operation %s is approaching on %s.") % (op.name, op.planned_arrival_date),
                        op.user_id.id
                    )
                    if op.document_missing_count > 0:
                        op._create_operation_activity(
                            'mail.mail_activity_data_todo',
                            _("Missing Documents Near ETA Alert"),
                            _("The shipment is arriving soon on %s, but there are %s missing documents.") % (op.planned_arrival_date, op.document_missing_count),
                            op.user_id.id
                        )
        return records

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        company_id = self.env.context.get('default_company_id') or self.env.company.id
        return self.env['customs.stage'].search([
            '|', ('company_id', '=', False), ('company_id', '=', company_id)
        ])

    @api.depends('stage_id')
    def _compute_is_draft(self):
        for op in self:
            op.is_draft = not op.stage_id or op.stage_id.code == 'draft'

    @api.depends('vendor_bill_ids')
    def _compute_vendor_bill_count(self):
        for op in self:
            op.vendor_bill_count = len(op.vendor_bill_ids)

    @api.depends('purchase_order_ids')
    def _compute_sale_orders(self):
        for op in self:
            sale_orders = self.env['sale.order']
            if op.purchase_order_ids:
                po_origins = op.purchase_order_ids.mapped('origin')
                so_names = []
                for origin in po_origins:
                    if origin:
                        names = [x.strip() for x in origin.split(',')]
                        so_names.extend(names)
                if so_names:
                    sale_orders |= self.env['sale.order'].search([
                        ('name', 'in', so_names),
                        ('company_id', '=', op.company_id.id)
                    ])

                po_lines = op.purchase_order_ids.mapped('order_line')
                move_dest_ids = po_lines.mapped('move_ids.move_dest_ids')
                if move_dest_ids:
                    sale_orders |= move_dest_ids.mapped('sale_line_id.order_id')
                
                group_ids = op.purchase_order_ids.mapped('group_id')
                if group_ids:
                    moves = self.env['stock.move'].search([('group_id', 'in', group_ids.ids)])
                    sale_orders |= moves.mapped('sale_line_id.order_id')

            op.sale_order_ids = sale_orders

    @api.depends('sale_order_ids')
    def _compute_sale_order_count(self):
        for op in self:
            op.sale_order_count = len(op.sale_order_ids)

    @api.depends('purchase_order_ids', 'purchase_order_ids.amount_total', 'purchase_order_ids.currency_id')
    def _compute_commercial_defaults(self):
        for op in self:
            if op.purchase_order_ids:
                op.currency_id = op.purchase_order_ids[0].currency_id
                op.total_amount = sum(po.amount_total for po in op.purchase_order_ids)
            else:
                if not op.currency_id:
                    op.currency_id = op.company_id.currency_id or self.env.company.currency_id

    @api.depends('cost_freight', 'cost_customs_tax', 'cost_broker_expenses', 'cost_stamp_tax', 'cost_storage', 'cost_exchange_diff', 'cost_other')
    def _compute_cost_total(self):
        for op in self:
            op.cost_total = (
                op.cost_freight + op.cost_customs_tax + op.cost_broker_expenses +
                op.cost_stamp_tax + op.cost_storage + op.cost_exchange_diff + op.cost_other
            )

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

    @api.depends(
        'document_requirement_ids.state', 
        'document_requirement_ids.is_blocking', 
        'document_requirement_ids.original_required', 
        'document_requirement_ids.original_issued',
        'stage_id.sequence', 
        'transport_mode', 
        'origin_country_id', 
        'departure_country_id', 
        'destination_country_id', 
        'incoterm_id', 
        'is_overridden'
    )
    def _compute_readiness(self):
        approved_states = {'approved', 'original_issued', 'original_dispatched', 'original_received', 'submitted_to_customs', 'accepted'}
        shipped_stage = self.env.ref('midvex_customs_op.stage_shipped', raise_if_not_found=False)
        pre_shipment_seq = shipped_stage.sequence if shipped_stage else 6
        
        for op in self:
            reasons = []
            blocking_count = 0
            
            for doc in op.document_requirement_ids:
                if not doc.is_blocking:
                    continue
                
                is_complete = doc.state in approved_states
                
                is_pre_shipment = (op.stage_id.sequence or 0) < pre_shipment_seq
                is_expired = False
                if doc.expiry_date and doc.state != 'n_a' and not is_complete:
                    is_expired = doc.expiry_date < fields.Date.today()
                
                original_missing = doc.original_required and not doc.original_issued
                
                if not is_complete or (is_pre_shipment and is_expired) or original_missing:
                    blocking_count += 1
                    doc_reasons = []
                    if not is_complete:
                        doc_reasons.append(_("incomplete"))
                    if is_pre_shipment and is_expired:
                        doc_reasons.append(_("expired"))
                    if original_missing:
                        doc_reasons.append(_("original not issued"))
                    reasons.append(_("Document '%s': %s") % (doc.name, ", ".join(doc_reasons)))
            
            missing_fields = []
            if not op.transport_mode:
                missing_fields.append(_("Transport Mode"))
            if not op.origin_country_id:
                missing_fields.append(_("Country of Origin"))
            if not op.departure_country_id:
                missing_fields.append(_("Country of Departure"))
            if not op.destination_country_id:
                missing_fields.append(_("Country of Destination"))
            if not op.incoterm_id:
                missing_fields.append(_("Incoterm"))
            
            if missing_fields:
                reasons.append(_("Missing fields: %s") % ", ".join(missing_fields))
            
            op.blocking_document_count = blocking_count
            
            if reasons:
                op.blocking_reason_text = "\n".join(reasons)
                if op.is_overridden:
                    op.shipment_ready = True
                else:
                    op.shipment_ready = False
            else:
                op.blocking_reason_text = ""
                op.shipment_ready = True

    def action_override_readiness(self):
        self.ensure_one()
        if not self.env.user.has_group('midvex_customs_op.group_customs_manager'):
            raise AccessError(_("Only Customs Managers can override readiness controls."))
            
        return {
            'name': _('Override Readiness Check'),
            'type': 'ir.actions.act_window',
            'res_model': 'customs.operation.override.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_operation_id': self.id},
        }

    def action_reset_override(self):
        self.ensure_one()
        if not self.env.user.has_group('midvex_customs_op.group_customs_manager'):
            raise AccessError(_("Only Customs Managers can reset override settings."))
        self.write({
            'is_overridden': False,
            'override_reason': False,
            'override_user_id': False,
            'override_date': False,
        })
        body = Markup(_("Readiness check override reset by %s.")) % escape(self.env.user.name)
        self.message_post(body=body)

    def _create_operation_activity(self, activity_xml_id, summary, note, user_id):
        self.ensure_one()
        activity_type = self.env.ref(activity_xml_id, raise_if_not_found=False)
        if not activity_type:
            activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            activity_type = self.env['mail.activity.type'].search([], limit=1)
            
        if not activity_type:
            return
            
        model_id = self.env['ir.model']._get('customs.operation').id
        self.env['mail.activity'].create({
            'activity_type_id': activity_type.id,
            'summary': summary,
            'note': note,
            'res_id': self.id,
            'res_model_id': model_id,
            'user_id': user_id or self.user_id.id or self.env.user.id,
        })

    def write(self, vals):
        is_manager = self.env.user.has_group('midvex_customs_op.group_customs_manager')
        
        # Capture old values before write for trigger conditions
        old_values = {}
        trigger_fields = {'bl_number', 'warehouse_received', 'damaged_product', 'missing_packages', 'planned_arrival_date'}
        for op in self:
            old_values[op.id] = {f: op[f] for f in trigger_fields if f in op._fields}

        # 1. Enforce active/archiving permissions
        if 'active' in vals:
            if not is_manager:
                raise AccessError(_("Only Customs Managers or Administrators can archive or unarchive Customs Files."))

        if 'stage_id' in vals:
            new_stage = self.env['customs.stage'].browse(vals['stage_id'])
            
            for op in self:
                old_stage = op.stage_id
                if old_stage and new_stage and old_stage != new_stage:
                    # A. Reopening closed file protection
                    if old_stage.is_closed and not is_manager:
                        raise AccessError(_("Only Customs Managers or Administrators can reopen or move a Customs File out of a closed stage."))
                    
                    # B. Prevent backward transitions for regular users (unless cancelled or hold/folded)
                    if new_stage.sequence < old_stage.sequence and not is_manager:
                        if not (new_stage.is_cancelled or new_stage.fold):
                            raise AccessError(
                                _("You cannot move the Customs File backward from '%s' to '%s'. Only Customs Managers can perform backward transitions.") % 
                                (old_stage.name, new_stage.name)
                            )
                    
                    # C. Prevent large forward skips for regular users (skipping more than 3 stages)
                    if new_stage.sequence - old_stage.sequence > 3 and not is_manager:
                        if not (new_stage.is_cancelled or new_stage.is_closed or new_stage.fold):
                            raise ValidationError(
                                _("You cannot jump from stage '%s' to '%s'. Moving forward more than 3 stages at once requires a Customs Manager.") % 
                                (old_stage.name, new_stage.name)
                            )
            
            # 2. Existing closing stage validations
            if new_stage.is_closed:
                approved_states = {'approved', 'original_issued', 'original_dispatched', 'original_received', 'submitted_to_customs', 'accepted'}
                for op in self:
                    # Verify all mandatory document requirements are complete
                    incomplete_docs = op.document_requirement_ids.filtered(
                        lambda r: r.requirement_level == 'mandatory' and r.state not in approved_states
                    )
                    if incomplete_docs:
                        raise ValidationError(
                            _("You cannot close Customs File %s because the following mandatory documents are incomplete:\n%s") %
                            (op.name, "\n".join(("- %s" % d.name for d in incomplete_docs)))
                        )
                    
                    # Verify no critical activities are open
                    open_critical_activities = self.env['mail.activity'].search([
                        ('res_model', 'in', ('customs.operation', 'customs.document.requirement')),
                        ('res_id', 'in', [op.id] + op.document_requirement_ids.ids),
                        ('activity_type_id.is_critical', '=', True)
                    ])
                    if open_critical_activities:
                        raise ValidationError(
                            _("You cannot close Customs File %s because there are open critical activities:\n%s") %
                            (op.name, "\n".join(("- %s" % (a.summary or a.activity_type_id.name, a.activity_type_id.name) for a in open_critical_activities)))
                        )
                    
                    # Warning checks for missing optional fields:
                    missing_warn_fields = []
                    if not op.customs_declaration_number:
                        missing_warn_fields.append(_("Customs Declaration Number"))
                    if not op.customs_declaration_date:
                        missing_warn_fields.append(_("Declaration Date"))
                    if not op.release_date:
                        missing_warn_fields.append(_("Customs Release Date"))
                    if not op.warehouse_delivery_date:
                        missing_warn_fields.append(_("Warehouse Delivery Date"))
                    
                    if missing_warn_fields:
                        body = Markup(_("<strong>Warning:</strong> The Customs File was closed, but the following operational details are missing: %s")) % \
                            escape(", ".join(missing_warn_fields))
                        op.message_post(body=body)
                        
        res = super(CustomsOperation, self).write(vals)

        # Trigger automatic activities after write
        for op in self:
            old = old_values.get(op.id, {})
            # 1. BL Uploaded Trigger
            if 'bl_number' in vals and vals['bl_number'] and not old.get('bl_number'):
                op._create_operation_activity(
                    'mail.mail_activity_data_todo',
                    _("B/L Uploaded - Action Required"),
                    _("Bill of Lading %s has been uploaded. Please notify the customs broker to prepare the declaration.") % vals['bl_number'],
                    op.user_id.id
                )
            
            # 2. Warehouse Delivery Completed Trigger
            if 'warehouse_received' in vals and vals['warehouse_received'] and not old.get('warehouse_received'):
                purchasing_user_id = op.user_id.id
                if op.purchase_order_ids:
                    purchasing_user_id = op.purchase_order_ids[0].user_id.id
                op._create_operation_activity(
                    'mail.mail_activity_data_todo',
                    _("Warehouse Delivery Completed"),
                    _("Warehouse entry has been recorded for operation %s. Please review and process for closing.") % op.name,
                    purchasing_user_id
                )

            # 3. Discrepancy / Damaged Product Trigger
            if ('damaged_product' in vals and vals['damaged_product'] and not old.get('damaged_product')) or \
               ('missing_packages' in vals and vals['missing_packages'] and not old.get('missing_packages')):
                manager_group = self.env.ref('midvex_customs_op.group_customs_manager', raise_if_not_found=False)
                manager_users = manager_group.users if manager_group else self.env['res.users']
                notify_user = manager_users[0].id if manager_users else op.user_id.id
                op._create_operation_activity(
                    'mail.mail_activity_data_todo',
                    _("Discrepancy / Damaged Cargo Recorded"),
                    _("Damaged product or missing packages have been reported for operation %s. Description: %s") % (
                        op.name, vals.get('damage_description') or op.damage_description or _("No description provided.")
                    ),
                    notify_user
                )

            # 4. ETA Approaching Trigger (and Missing Documents check)
            if 'planned_arrival_date' in vals and vals['planned_arrival_date']:
                eta_date = fields.Date.to_date(vals['planned_arrival_date'])
                days_left = (eta_date - fields.Date.today()).days
                if 0 <= days_left <= 3:
                    op._create_operation_activity(
                        'mail.mail_activity_data_todo',
                        _("ETA Approaching"),
                        _("The arrival date (ETA) for operation %s is approaching on %s.") % (op.name, vals['planned_arrival_date']),
                        op.user_id.id
                    )
                    if op.document_missing_count > 0:
                        op._create_operation_activity(
                            'mail.mail_activity_data_todo',
                            _("Missing Documents Near ETA Alert"),
                            _("The shipment is arriving soon on %s, but there are %s missing documents.") % (vals['planned_arrival_date'], op.document_missing_count),
                            op.user_id.id
                        )

        return res
 
    def unlink(self):
        for op in self:
            is_draft = not op.stage_id or op.stage_id.code == 'draft'
            if not is_draft:
                raise ValidationError(
                    _("You can only delete a Customs File when it is in the 'Draft' stage. Operation %s is currently in '%s'.") % 
                    (op.name, op.stage_id.name or '')
                )
        return super(CustomsOperation, self).unlink()

    def action_view_vendor_bills(self):
        self.ensure_one()
        return {
            'name': _('Vendor Bills & Expenses'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.vendor_bill_ids.ids)],
            'context': {
                'default_move_type': 'in_invoice',
                'default_customs_operation_id': self.id,
            },
            'target': 'current',
        }

    def action_view_sales_orders(self):
        self.ensure_one()
        return {
            'name': _('Linked Sales Orders (MTO)'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.sale_order_ids.ids)],
            'target': 'current',
        }

    def action_sync_purchase_lines(self):
        self.ensure_one()
        waiting_docs_stage = self.env.ref('midvex_customs_op.stage_waiting_docs', raise_if_not_found=False)
        waiting_docs_seq = waiting_docs_stage.sequence if waiting_docs_stage else 2
        if self.stage_id and self.stage_id.sequence > waiting_docs_seq:
            raise ValidationError(
                _("You cannot sync product lines because this Customs File is past the 'Waiting for Documents' stage (locked).")
            )
        
        for po in self.purchase_order_ids:
            self._sync_lines_from_po(po)
            
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

    def _sync_lines_from_po(self, po):
        self.ensure_one()
        existing_lines = self.operation_line_ids.filtered(lambda l: l.purchase_order_line_id)
        existing_po_line_ids = existing_lines.mapped('purchase_order_line_id.id')
        
        po_lines = po.order_line.filtered(lambda l: not l.display_type)
        po_line_ids = po_lines.ids
        
        # 1. Delete lines that are no longer in the PO
        lines_to_delete = existing_lines.filtered(lambda l: l.purchase_order_line_id.id not in po_line_ids)
        if lines_to_delete:
            lines_to_delete.unlink()
            
        # 2. Update existing lines or create new ones
        for line in po_lines:
            existing_line = existing_lines.filtered(lambda l: l.purchase_order_line_id.id == line.id)
            if existing_line:
                if existing_line.quantity != line.product_qty:
                    existing_line.write({'quantity': line.product_qty})
            else:
                line_vals = {
                    'operation_id': self.id,
                    'purchase_order_line_id': line.id,
                    'product_id': line.product_id.id,
                    'description': line.name,
                    'quantity': line.product_qty,
                    'uom_id': line.product_uom_id.id,
                }
                
                tmpl = line.product_id.product_tmpl_id
                if tmpl:
                    line_vals.update({
                        'country_of_origin_id': tmpl.country_of_origin_id.id or self.origin_country_id.id,
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

    def _generate_default_document_requirements(self):
        self.ensure_one()
        doc_types = self.env['customs.document.type'].search([])
        types_by_code = {t.code: t for t in doc_types}
        
        req_vals = []
        
        # Standard Global Documents
        global_codes = ['INV', 'PKL', 'COO']
        for code in global_codes:
            if code in types_by_code:
                t = types_by_code[code]
                req_vals.append({
                    'operation_id': self.id,
                    'document_type_id': t.id,
                    'name': t.name,
                    'responsible_party': t.default_responsible_party,
                    'requirement_level': t.default_requirement_level,
                    'original_required': t.original_normally_required,
                    'state': 'not_requested',
                })
                
        # Transport Document (BL/AWB/CMR)
        t_code = 'BL'
        if self.transport_mode == 'air':
            t_code = 'AWB'
        elif self.transport_mode == 'road':
            t_code = 'CMR'
            
        if t_code in types_by_code:
            t = types_by_code[t_code]
            req_vals.append({
                'operation_id': self.id,
                'document_type_id': t.id,
                'name': t.name,
                'responsible_party': t.default_responsible_party,
                'requirement_level': t.default_requirement_level,
                'original_required': t.original_normally_required,
                'state': 'not_requested',
            })
            
        # Line Specific Documents (COA, HC, IP)
        for line in self.operation_line_ids:
            line_requirements = []
            if line.health_certificate_required:
                line_requirements.append('HC')
            if line.analysis_required:
                line_requirements.append('COA')
            if line.import_permit_required:
                line_requirements.append('IP')
                
            for code in line_requirements:
                if code in types_by_code:
                    t = types_by_code[code]
                    req_vals.append({
                        'operation_id': self.id,
                        'operation_line_id': line.id,
                        'document_type_id': t.id,
                        'name': "%s - %s" % (t.name, line.product_id.name),
                        'responsible_party': t.default_responsible_party,
                        'requirement_level': t.default_requirement_level,
                        'original_required': t.original_normally_required,
                        'state': 'not_requested',
                    })
                    
        if req_vals:
            self.env['customs.document.requirement'].create(req_vals)

