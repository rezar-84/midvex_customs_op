# -*- coding: utf-8 -*-

from odoo import models, fields, api

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                # Generate sequence on creation
                vals['name'] = self.env['ir.sequence'].next_by_code('customs.operation') or 'New'
        return super(CustomsOperation, self).create(vals_list)

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        # Retrieve all stages for the kanban column expansion, respecting active company
        company_id = self.env.context.get('default_company_id') or self.env.company.id
        return self.env['customs.stage'].search([
            '|', ('company_id', '=', False), ('company_id', '=', company_id)
        ])
