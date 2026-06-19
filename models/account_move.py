# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    customs_operation_id = fields.Many2one(
        'customs.operation',
        string='Customs File',
        domain="[('company_id', '=', company_id)]",
        help="Link this invoice/bill to a Customs File for expense/cost tracking."
    )

    def action_view_customs_operations(self):
        self.ensure_one()
        if not self.customs_operation_id:
            return False
        return {
            'name': _('Customs File'),
            'type': 'ir.actions.act_window',
            'res_model': 'customs.operation',
            'view_mode': 'form',
            'res_id': self.customs_operation_id.id,
            'target': 'current',
        }

    @api.model_create_multi
    def create(self, vals_list):
        moves = super(AccountMove, self).create(vals_list)
        for move in moves:
            if move.move_type == 'in_invoice' and not move.customs_operation_id:
                # Tracing purchase orders associated with vendor bill lines
                pos = move.line_ids.mapped('purchase_line_id.order_id')
                if pos:
                    ops = self.env['customs.operation'].search([('purchase_order_ids', 'in', pos.ids)], limit=1)
                    if ops:
                        move.write({'customs_operation_id': ops.id})
        return moves

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        if 'line_ids' in vals:
            for move in self:
                if move.move_type == 'in_invoice' and not move.customs_operation_id:
                    pos = move.line_ids.mapped('purchase_line_id.order_id')
                    if pos:
                        ops = self.env['customs.operation'].search([('purchase_order_ids', 'in', pos.ids)], limit=1)
                        if ops:
                            move.write({'customs_operation_id': ops.id})
        return res
