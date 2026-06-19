# -*- coding: utf-8 -*-

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    customs_block_receipt_before_clearance = fields.Boolean(
        string='Block Warehouse Receipt Before Customs Clearance',
        config_parameter='midvex_customs_op.customs_block_receipt_before_clearance',
        default=False,
        help="If checked, warehouse workers cannot validate stock receipts until the linked customs operation is released/cleared."
    )
