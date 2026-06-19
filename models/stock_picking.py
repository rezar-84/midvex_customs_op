# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    customs_operation_ids = fields.Many2many(
        'customs.operation',
        string='Customs Files',
        compute='_compute_customs_operations',
        help="Linked Customs Files for this incoming receipt."
    )
    customs_operation_count = fields.Integer(
        string='Customs File Count',
        compute='_compute_customs_operations'
    )
    customs_operation_state = fields.Char(
        string='Customs File Status',
        compute='_compute_customs_operations'
    )
    customs_not_cleared = fields.Boolean(
        string='Customs Not Cleared',
        compute='_compute_customs_operations'
    )

    @api.depends('purchase_id')
    def _compute_customs_operations(self):
        cleared_stage = self.env.ref('midvex_customs_op.stage_cleared', raise_if_not_found=False)
        cleared_seq = cleared_stage.sequence if cleared_stage else 10
        for picking in self:
            ops = self.env['customs.operation'].search([('picking_ids', 'in', picking.id)])
            picking.customs_operation_ids = ops
            picking.customs_operation_count = len(ops)
            if ops:
                picking.customs_operation_state = ", ".join(ops.mapped(lambda o: o.stage_id.name or _('New')))
                uncleared = ops.filtered(lambda o: (o.stage_id.sequence or 0) < cleared_seq and not o.stage_id.is_cancelled and not o.stage_id.is_closed)
                picking.customs_not_cleared = bool(uncleared)
            else:
                picking.customs_operation_state = _('No Link')
                picking.customs_not_cleared = False

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

    @api.model_create_multi
    def create(self, vals_list):
        pickings = super(StockPicking, self).create(vals_list)
        for picking in pickings:
            if picking.purchase_id:
                ops = self.env['customs.operation'].search([('purchase_order_ids', 'in', picking.purchase_id.id)])
                if ops:
                    ops.write({'picking_ids': [(4, picking.id)]})
        return pickings

    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        if 'purchase_id' in vals and vals['purchase_id']:
            for picking in self:
                ops = self.env['customs.operation'].search([('purchase_order_ids', 'in', vals['purchase_id'])])
                if ops:
                    ops.write({'picking_ids': [(4, picking.id)]})
        return res

    def button_validate(self):
        cleared_stage = self.env.ref('midvex_customs_op.stage_cleared', raise_if_not_found=False)
        cleared_seq = cleared_stage.sequence if cleared_stage else 10

        for picking in self:
            ops = self.env['customs.operation'].search([('picking_ids', 'in', picking.id)])
            uncleared_ops = ops.filtered(lambda o: (o.stage_id.sequence or 0) < cleared_seq and not o.stage_id.is_cancelled and not o.stage_id.is_closed)
            
            if uncleared_ops:
                block_setting = self.env['ir.config_parameter'].sudo().get_param('midvex_customs_op.customs_block_receipt_before_clearance', False)
                op_names = ", ".join(uncleared_ops.mapped('name'))
                if block_setting:
                    raise ValidationError(_(
                        "Validation blocked! The linked Customs File(s) [%s] must be cleared/released before validating this receipt."
                    ) % op_names)
                else:
                    msg = _("<strong>Warning:</strong> Receipt validated prior to customs clearance of linked Customs File(s): %s.") % op_names
                    picking.message_post(body=msg)
                    for op in uncleared_ops:
                        op.message_post(body=_("<strong>Warning:</strong> Linked incoming shipment %s was validated before customs clearance was completed.") % picking.name)
                        
        return super(StockPicking, self).button_validate()
