# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError

class CustomsDocumentRequirement(models.Model):
    _name = 'customs.document.requirement'
    _description = 'Customs Document Requirement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    operation_id = fields.Many2one(
        'customs.operation', 
        string='Customs File', 
        required=True, 
        ondelete='cascade',
        index=True
    )
    operation_line_id = fields.Many2one(
        'customs.operation.line',
        string='Product Line',
        domain="[('operation_id', '=', operation_id)]"
    )
    document_type_id = fields.Many2one(
        'customs.document.type', 
        string='Document Type', 
        required=True,
        index=True
    )
    name = fields.Char(string='Description', required=True)
    state = fields.Selection([
        ('not_requested', 'Not Requested'),
        ('requested', 'Requested'),
        ('vendor_preparing', 'Vendor Preparing'),
        ('draft_received', 'Draft Received'),
        ('under_review', 'Under Review'),
        ('correction_required', 'Correction Required'),
        ('approved', 'Approved'),
        ('original_issued', 'Original Issued'),
        ('original_dispatched', 'Original Dispatched'),
        ('original_received', 'Original Received'),
        ('submitted_to_customs', 'Submitted to Customs'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
        ('n_a', 'Not Applicable'),
    ], string='Status', default='not_requested', required=True, tracking=True, index=True)
    
    requirement_level = fields.Selection([
        ('mandatory', 'Mandatory'),
        ('optional', 'Optional'),
    ], string='Requirement Level', default='mandatory', tracking=True)
    
    responsible_party = fields.Selection([
        ('supplier', 'Supplier/Vendor'),
        ('broker', 'Customs Broker'),
        ('forwarder', 'Freight Forwarder'),
        ('carrier', 'Carrier'),
        ('manufacturer', 'Manufacturer'),
        ('internal', 'Internal'),
    ], string='Responsible Party', default='supplier', tracking=True)
    
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible Employee',
        default=lambda self: self.env.user,
        tracking=True
    )
    
    vendor_id = fields.Many2one(
        'res.partner',
        string='Vendor/Partner',
        tracking=True
    )
    
    company_id = fields.Many2one(
        'res.company', 
        related='operation_id.company_id', 
        string='Company', 
        store=True, 
        index=True
    )
    is_blocking = fields.Boolean(
        string='Blocking Requirement', 
        default=True,
        tracking=True,
        help="If set, this document requirement will block shipment readiness if not completed."
    )
    
    # Dates
    requested_date = fields.Date(string='Requested Date')
    deadline = fields.Date(string='Deadline', tracking=True)
    received_date = fields.Date(string='Received Date')
    issued_date = fields.Date(string='Issued Date')
    expiry_date = fields.Date(string='Expiry Date', tracking=True)
    reviewed_date = fields.Date(string='Reviewed Date')
    reviewed_by = fields.Many2one(
        'res.users',
        string='Reviewed By'
    )
    
    # Original tracking fields
    original_required = fields.Boolean(string='Original Required', default=False, tracking=True)
    original_issued = fields.Boolean(string='Original Issued', default=False, tracking=True)
    original_dispatched = fields.Boolean(string='Original Dispatched', default=False, tracking=True)
    original_received = fields.Boolean(string='Original Received', default=False, tracking=True)
    dispatch_date = fields.Date(string='Original Dispatch Date')
    courier_name = fields.Char(string='Courier')
    tracking_number = fields.Char(string='Tracking Number')
    
    # Attachments & Versioning
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'customs_document_requirement_attachment_rel',
        'requirement_id',
        'attachment_id',
        string='Attachments'
    )
    version_number = fields.Integer(string='Version Number', default=1, required=True, tracking=True)
    
    # Rejection & review notes
    rejection_reason = fields.Text(string='Rejection Reason', tracking=True)
    review_notes = fields.Text(string='Review Notes')
    
    # Computed status helper fields
    is_complete = fields.Boolean(string='Is Complete', compute='_compute_is_complete', store=True)
    is_overdue = fields.Boolean(string='Is Overdue', compute='_compute_is_overdue')
    is_expired = fields.Boolean(string='Is Expired', compute='_compute_is_expired')
    
    # Helper dynamic domain for vendor
    allowed_vendor_ids = fields.Many2many(
        'res.partner',
        compute='_compute_allowed_vendor_ids',
        string='Allowed Vendors'
    )

    @api.depends('state')
    def _compute_is_complete(self):
        complete_states = {'approved', 'original_issued', 'original_dispatched', 'original_received', 'submitted_to_customs', 'accepted'}
        for rec in self:
            rec.is_complete = rec.state in complete_states

    @api.depends('state', 'deadline')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for rec in self:
            if rec.deadline and not rec.is_complete and rec.state != 'n_a':
                rec.is_overdue = rec.deadline < today
            else:
                rec.is_overdue = False

    @api.depends('state', 'expiry_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for rec in self:
            if rec.expiry_date and not rec.is_complete and rec.state != 'n_a':
                rec.is_expired = rec.expiry_date < today
            else:
                rec.is_expired = False

    @api.depends('operation_id.supplier_ids', 'operation_id.broker_id', 'operation_id.forwarder_id', 'operation_id.carrier_id', 'operation_id.operation_line_ids.manufacturer_id')
    def _compute_allowed_vendor_ids(self):
        for rec in self:
            op = rec.operation_id
            if op:
                partners = op.supplier_ids | op.broker_id | op.forwarder_id | op.carrier_id | op.operation_line_ids.mapped('manufacturer_id')
                rec.allowed_vendor_ids = partners
            else:
                rec.allowed_vendor_ids = self.env['res.partner']

    @api.onchange('document_type_id')
    def _onchange_document_type_id(self):
        if self.document_type_id:
            self.name = self.document_type_id.name
            if self.document_type_id.default_requirement_level == 'mandatory':
                self.requirement_level = 'mandatory'
                self.is_blocking = True
            else:
                self.requirement_level = 'optional'
                self.is_blocking = False
            self.responsible_party = self.document_type_id.default_responsible_party
            self.original_required = self.document_type_id.original_normally_required

    @api.constrains('vendor_id', 'operation_id')
    def _check_vendor_id(self):
        for rec in self:
            if rec.vendor_id:
                op = rec.operation_id
                allowed_partners = op.supplier_ids | op.broker_id | op.forwarder_id | op.carrier_id | op.operation_line_ids.mapped('manufacturer_id')
                if rec.vendor_id not in allowed_partners:
                    raise ValidationError(
                        _("The selected vendor/partner (%s) must be one of the related parties on the Customs File (Suppliers, Broker, Forwarder, Carrier, or Manufacturers).") % rec.vendor_id.display_name
                    )

    @api.model_create_multi
    def create(self, vals_list):
        approver_states = {'approved', 'original_issued', 'original_dispatched', 'original_received', 'submitted_to_customs', 'accepted', 'rejected', 'correction_required'}
        is_approver = self.env.user.has_group('midvex_customs_op.group_customs_approver')
        
        for vals in vals_list:
            state = vals.get('state', 'not_requested')
            if state in approver_states and not is_approver:
                raise AccessError(_("Only Customs Document Approvers or Managers can create compliance documents in approved or rejected states."))
            if state in ('rejected', 'correction_required') and not vals.get('rejection_reason'):
                raise ValidationError(
                    _("A rejection reason is required when the document state is set to '%s'.") % state
                )
            if state in ('approved', 'accepted', 'rejected', 'correction_required'):
                vals['reviewed_by'] = self.env.user.id
                vals['reviewed_date'] = fields.Date.today()
        return super(CustomsDocumentRequirement, self).create(vals_list)

    def write(self, vals):
        records_pre_write = {}
        for rec in self:
            records_pre_write[rec.id] = {
                'attachment_ids': set(rec.attachment_ids.ids),
                'state': rec.state,
            }
        
        if 'state' in vals:
            new_state = vals['state']
            approver_states = {'approved', 'original_issued', 'original_dispatched', 'original_received', 'submitted_to_customs', 'accepted', 'rejected', 'correction_required'}
            is_approver = self.env.user.has_group('midvex_customs_op.group_customs_approver')
            is_manager = self.env.user.has_group('midvex_customs_op.group_customs_manager')
            
            for rec in self:
                # 1. Permission Check: basic Customs User cannot set an approver/manager state directly
                if new_state in approver_states and not is_approver:
                    raise AccessError(_("Only Customs Document Approvers or Managers can approve, reject, or require corrections on compliance documents."))
                
                # 2. Permission Check: only Customs Manager can reset already approved documents
                approved_states = {'approved', 'original_issued', 'original_dispatched', 'original_received', 'submitted_to_customs', 'accepted'}
                if rec.state in approved_states and new_state not in approved_states and not is_manager:
                    raise AccessError(_("Only Customs Managers can reset or modify the state of an already approved compliance document."))

            if new_state in ('approved', 'accepted', 'rejected', 'correction_required'):
                vals['reviewed_by'] = self.env.user.id
                vals['reviewed_date'] = fields.Date.today()
            if new_state in ('draft_received', 'under_review'):
                vals['rejection_reason'] = False
        
        res = super(CustomsDocumentRequirement, self).write(vals)
        
        for rec in self:
            pre_vals = records_pre_write.get(rec.id)
            if not pre_vals:
                continue
            
            current_attachments = set(rec.attachment_ids.ids)
            added_attachments = current_attachments - pre_vals['attachment_ids']
            if added_attachments:
                super(CustomsDocumentRequirement, rec).write({'version_number': rec.version_number + 1})
            
            if rec.state in ('rejected', 'correction_required') and not rec.rejection_reason:
                raise ValidationError(
                    _("A rejection reason is required when the document state is set to '%s'.") % rec.state
                )
        
        return res

    def unlink(self):
        for rec in self:
            if rec.attachment_ids:
                raise ValidationError(
                    _("You cannot delete a document requirement (%s) that has uploaded attachments. Please remove the attachments or mark the status as 'Not Applicable' instead.") % rec.name
                )
            waiting_docs_stage = self.env.ref('midvex_customs_op.stage_waiting_docs', raise_if_not_found=False)
            waiting_docs_seq = waiting_docs_stage.sequence if waiting_docs_stage else 2
            if rec.operation_id.stage_id and rec.operation_id.stage_id.sequence > waiting_docs_seq:
                raise ValidationError(
                    _("You cannot delete a document requirement (%s) when the Customs File is past the 'Waiting for Documents' stage. Please mark the status as 'Not Applicable' instead.") % rec.name
                )
        return super(CustomsDocumentRequirement, self).unlink()

    # Dynamic action transition methods
    def action_request(self):
        self.write({'state': 'requested', 'requested_date': fields.Date.today()})

    def action_prepare(self):
        self.write({'state': 'vendor_preparing'})

    def action_submit(self):
        self.write({'state': 'under_review'})

    def action_approve(self):
        self.write({'state': 'approved', 'received_date': fields.Date.today()})

    def action_require_correction(self):
        self.write({'state': 'correction_required'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_reset_to_draft(self):
        self.write({
            'state': 'not_requested',
            'requested_date': False,
            'received_date': False,
            'reviewed_by': False,
            'reviewed_date': False,
            'rejection_reason': False,
        })
