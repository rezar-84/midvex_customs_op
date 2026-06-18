# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
from markupsafe import Markup, escape

class CustomsOperation(models.Model):
    _name = 'customs.operation'
    _description = 'Customs File'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

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
    is_draft = fields.Boolean(string='Is Draft Stage', compute='_compute_is_draft', store=True)

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

    @api.depends('stage_id')
    def _compute_is_draft(self):
        draft_stage = self.env.ref('midvex_customs_op.stage_draft', raise_if_not_found=False)
        for op in self:
            if draft_stage and op.stage_id == draft_stage:
                op.is_draft = True
            elif op.stage_id and op.stage_id.sequence == 1:
                op.is_draft = True
            elif not op.stage_id:
                op.is_draft = True
            else:
                op.is_draft = False

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

    def write(self, vals):
        is_manager = self.env.user.has_group('midvex_customs_op.group_customs_manager')
        
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
                            (op.name, "\n".join(("- %s (%s)" % (a.summary or a.activity_type_id.name, a.activity_type_id.name) for a in open_critical_activities)))
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
                        
        return super(CustomsOperation, self).write(vals)
 
    def unlink(self):
        draft_stage = self.env.ref('midvex_customs_op.stage_draft', raise_if_not_found=False)
        for op in self:
            is_draft = (op.stage_id == draft_stage) if (draft_stage and op.stage_id) else (not op.stage_id or op.stage_id.sequence == 1)
            if not is_draft:
                raise ValidationError(
                    _("You can only delete a Customs File when it is in the 'Draft' stage. Operation %s is currently in '%s'.") % 
                    (op.name, op.stage_id.name or '')
                )
        return super(CustomsOperation, self).unlink()

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
