# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError, ValidationError


class TestCustomsPortal(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_portal = cls.env.ref('base.group_portal')
        cls.group_customs_user = cls.env.ref('midvex_customs_op.group_customs_user')
        cls.stage_waiting = cls.env.ref('midvex_customs_op.stage_waiting_docs')

        cls.supplier = cls.env['res.partner'].create({'name': 'Portal Supplier'})
        cls.broker = cls.env['res.partner'].create({'name': 'Portal Broker'})
        cls.other_partner = cls.env['res.partner'].create({'name': 'Other Portal Partner'})

        cls.supplier_user = cls.env['res.users'].create({
            'name': 'Portal Supplier User',
            'login': 'portal_supplier_customs',
            'email': 'portal_supplier_customs@example.com',
            'partner_id': cls.supplier.id,
            'group_ids': [(6, 0, [cls.group_portal.id])],
        })
        cls.broker_user = cls.env['res.users'].create({
            'name': 'Portal Broker User',
            'login': 'portal_broker_customs',
            'email': 'portal_broker_customs@example.com',
            'partner_id': cls.broker.id,
            'group_ids': [(6, 0, [cls.group_portal.id])],
        })
        cls.other_user = cls.env['res.users'].create({
            'name': 'Other Portal User',
            'login': 'portal_other_customs',
            'email': 'portal_other_customs@example.com',
            'partner_id': cls.other_partner.id,
            'group_ids': [(6, 0, [cls.group_portal.id])],
        })

        cls.operation = cls.env['customs.operation'].create({
            'name': 'CUS/PORTAL/001',
            'stage_id': cls.stage_waiting.id,
            'supplier_ids': [(4, cls.supplier.id)],
            'broker_id': cls.broker.id,
        })
        cls.other_operation = cls.env['customs.operation'].create({
            'name': 'CUS/PORTAL/002',
            'stage_id': cls.stage_waiting.id,
            'supplier_ids': [(4, cls.other_partner.id)],
        })
        cls.doc_type = cls.env['customs.document.type'].create({
            'name': 'Portal Invoice',
            'code': 'PINV',
        })
        cls.requirement = cls.env['customs.document.requirement'].create({
            'operation_id': cls.operation.id,
            'document_type_id': cls.doc_type.id,
            'name': 'Portal Invoice',
            'responsible_party': 'supplier',
            'state': 'requested',
        })

    def test_supplier_portal_sees_only_assigned_operations(self):
        operations = self.env['customs.operation'].with_user(self.supplier_user).search([])
        self.assertIn(self.operation, operations)
        self.assertNotIn(self.other_operation, operations)

    def test_broker_portal_sees_only_assigned_operations(self):
        operations = self.env['customs.operation'].with_user(self.broker_user).search([])
        self.assertIn(self.operation, operations)
        self.assertNotIn(self.other_operation, operations)

    def test_unrelated_portal_user_cannot_read_operation(self):
        operations = self.env['customs.operation'].with_user(self.other_user).search([('id', '=', self.operation.id)])
        self.assertFalse(operations)
        with self.assertRaises(AccessError):
            self.operation.with_user(self.other_user).read(['name'])

    def test_supplier_portal_can_submit_supplier_requirement(self):
        requirement = self.requirement.with_user(self.supplier_user)
        requirement.write({'state': 'under_review'})
        self.assertEqual(self.requirement.state, 'under_review')

    def test_broker_portal_cannot_write_operation_directly(self):
        operation = self.operation.with_user(self.broker_user)
        with self.assertRaises(AccessError):
            operation.write({
                'customs_declaration_number': '25240100IM000001',
                'customs_status': 'opened',
            })

    def test_broker_portal_cannot_submit_supplier_requirement(self):
        with self.assertRaises(AccessError):
            self.requirement.with_user(self.broker_user).write({'state': 'under_review'})

    def test_portal_users_cannot_create_or_delete_operations(self):
        with self.assertRaises(AccessError):
            self.env['customs.operation'].with_user(self.supplier_user).create({'name': 'CUS/PORTAL/CREATE'})
        with self.assertRaises(ValidationError):
            self.operation.with_user(self.supplier_user).unlink()

    def test_portal_user_creation_strips_backend_customs_groups(self):
        user = self.env['res.users'].create({
            'name': 'SAMPLE: Portal Broker Conflict',
            'login': 'sample_portal_broker_conflict',
            'email': 'sample_portal_broker_conflict@example.com',
            'group_ids': [(6, 0, [self.group_portal.id, self.group_customs_user.id])],
        })

        self.assertTrue(user.has_group('base.group_portal'))
        self.assertFalse(user.has_group('base.group_user'))
        self.assertFalse(user.has_group('midvex_customs_op.group_customs_user'))

    def test_portal_conversion_strips_existing_backend_customs_groups(self):
        user = self.env['res.users'].create({
            'name': 'SAMPLE: Internal Broker To Portal',
            'login': 'sample_internal_broker_to_portal',
            'email': 'sample_internal_broker_to_portal@example.com',
            'group_ids': [(6, 0, [self.group_customs_user.id])],
        })

        user.write({'group_ids': [(4, self.group_portal.id)]})

        self.assertTrue(user.has_group('base.group_portal'))
        self.assertFalse(user.has_group('base.group_user'))
        self.assertFalse(user.has_group('midvex_customs_op.group_customs_user'))
