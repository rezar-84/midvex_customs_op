# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

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
        self.operation_id.write({
            'is_overridden': True,
            'override_reason': self.reason,
            'override_user_id': self.env.user.id,
            'override_date': fields.Datetime.now(),
        })
        self.operation_id.message_post(
            body=_("<strong>Readiness check overridden</strong><br/>"
                   "<strong>User:</strong> %s<br/>"
                   "<strong>Reason:</strong> %s") % (self.env.user.name, self.reason)
        )
        return {'type': 'ir.actions.act_window_close'}
