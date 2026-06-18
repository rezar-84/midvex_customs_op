# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError
from markupsafe import Markup, escape

class CustomsOperationOverrideWizard(models.TransientModel):
    _name = 'customs.operation.override.wizard'
    _description = 'Override Customs File Readiness'

    operation_id = fields.Many2one(
        'customs.operation',
        string='Customs File',
        required=True
    )
    reason = fields.Text(
        string='Override Reason',
        required=True,
        help="Provide the reason for overriding the readiness block."
    )

    def action_confirm(self):
        self.ensure_one()
        if not self.env.user.has_group('midvex_customs_op.group_customs_manager'):
            raise AccessError(_("Only Customs Managers can override readiness controls."))
            
        self.operation_id.write({
            'is_overridden': True,
            'override_reason': self.reason,
            'override_user_id': self.env.user.id,
            'override_date': fields.Datetime.now(),
        })
        body = Markup(_("<strong>Readiness check overridden</strong><br/>"
                        "<strong>User:</strong> %s<br/>"
                        "<strong>Reason:</strong> %s")) % (escape(self.env.user.name), escape(self.reason))
        self.operation_id.message_post(body=body)
        return {'type': 'ir.actions.act_window_close'}
