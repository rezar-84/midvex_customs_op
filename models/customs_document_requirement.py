# -*- coding: utf-8 -*-

from odoo import models, fields

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
    ], string='Status', default='not_requested', required=True, tracking=True)
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
