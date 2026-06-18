# -*- coding: utf-8 -*-

from odoo import models, fields

class MailActivityType(models.Model):
    _inherit = 'mail.activity.type'

    is_critical = fields.Boolean(
        string='Is Critical', 
        default=False, 
        help="If checked, any open activities of this type will block closing the associated Customs File."
    )
