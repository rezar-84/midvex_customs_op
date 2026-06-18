# -*- coding: utf-8 -*-
{
    'name': 'Customs Operations',
    'version': '19.0.1.0.0',
    'summary': 'Manage customs operations and required documents for imports',
    'description': """
Customs Operations Management
=============================
This module centralizes international import shipments, tracking required documents,
vendor follow-ups, customs-clearance progress, inspections, approvals, and warehouse handovers.
    """,
    'category': 'Operations/Customs',
    'author': 'Midvex',
    'website': 'https://www.varsaquaculture.com',
    'license': 'GPL-3',
    'depends': [
        'base',
        'mail',
        'purchase_stock',
    ],
    'data': [
        'security/customs_security.xml',
        'security/ir.model.access.csv',
        'data/customs_sequence.xml',
        'data/customs_stage_data.xml',
        'views/customs_operation_views.xml',
        'views/customs_menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
