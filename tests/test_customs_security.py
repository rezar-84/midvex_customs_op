# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError

class TestCustomsSecurity(TransactionCase):

    def setUp(self):
        super(TestCustomsSecurity, self).setUp()
        
        # Find the groups
        self.group_user = self.env.ref('midvex_customs_op.group_customs_user')
        self.group_approver = self.env.ref('midvex_customs_op.group_customs_approver')
        self.group_manager = self.env.ref('midvex_customs_op.group_customs_manager')
        self.group_admin = self.env.ref('midvex_customs_op.group_customs_admin')

        # Create test users for different roles
        self.user_customs_user = self.env['res.users'].create({
            'name': 'Test Customs User',
            'login': 'customs_user_test',
            'email': 'user@test.com',
            'group_ids': [(6, 0, [self.group_user.id])]
        })

        self.user_customs_approver = self.env['res.users'].create({
            'name': 'Test Customs Approver',
            'login': 'customs_approver_test',
            'email': 'approver@test.com',
            'group_ids': [(6, 0, [self.group_approver.id])]
        })

    def test_group_inheritance(self):
        """Test that linear inheritance is set up correctly."""
        # Approver should inherit User group
        self.assertIn(self.group_user, self.group_approver.implied_ids, "Document Approver must inherit Customs User group")
        
        # Manager should inherit Approver group
        self.assertIn(self.group_approver, self.group_manager.implied_ids, "Customs Manager must inherit Document Approver group")
        
        # Admin should inherit Manager group
        self.assertIn(self.group_manager, self.group_admin.implied_ids, "Customs Administrator must inherit Customs Manager group")

    def test_stages_read_access(self):
        """Test that users can read stages but not create or modify them."""
        # Stage check as basic Customs User
        stages_as_user = self.env['customs.stage'].with_user(self.user_customs_user).search([])
        self.assertTrue(len(stages_as_user) > 0, "Customs User should be able to read stages")

        # Basic user should not be able to create stages
        with self.assertRaises(AccessError):
            self.env['customs.stage'].with_user(self.user_customs_user).create({
                'name': 'Unauthorized Stage'
            })

    def test_multi_company_record_rules(self):
        """Test that multi-company record rules prevent cross-company access."""
        # 1. Create a Customs File in the default company (Company A)
        operation_comp_a = self.env['customs.operation'].create({
            'name': 'CUS/COMPA/001',
            'company_id': self.env.company.id,
        })

        # 2. Create Company B and a user inside Company B
        company_b = self.env['res.company'].create({'name': 'Company B'})
        user_comp_b = self.env['res.users'].create({
            'name': 'Company B User',
            'login': 'company_b_user_test',
            'email': 'compb@test.com',
            'company_id': company_b.id,
            'company_ids': [(6, 0, [company_b.id])],
            'group_ids': [(6, 0, [self.group_user.id])]
        })

        # 3. Read check as Company B user should fail or return empty list
        ops_as_user_b = self.env['customs.operation'].with_user(user_comp_b).search([('id', '=', operation_comp_a.id)])
        self.assertFalse(ops_as_user_b, "User in Company B must not see records from Company A")

        # 4. Write/Update check as Company B user must raise AccessError
        with self.assertRaises(AccessError):
            operation_comp_a.with_user(user_comp_b).write({'priority': '1'})

    def test_role_action_limits(self):
        """Test action limits for Customs User, Document Approver, and Manager."""
        # Create a manager user
        user_manager = self.env['res.users'].create({
            'name': 'Test Customs Manager',
            'login': 'customs_manager_test',
            'email': 'manager@test.com',
            'group_ids': [(6, 0, [self.group_manager.id])]
        })

        # Create a draft customs operation
        operation = self.env['customs.operation'].create({
            'name': 'CUS/TEST/001',
        })

        # 1. Customs User attempts to override readiness checks -> raises AccessError
        with self.assertRaises(AccessError):
            operation.with_user(self.user_customs_user).action_override_readiness()

        # 2. Document Approver attempts to override readiness checks -> raises AccessError
        with self.assertRaises(AccessError):
            operation.with_user(self.user_customs_approver).action_override_readiness()

        # 3. Customs Manager attempts to override readiness checks -> should NOT raise AccessError on permission checks
        try:
            res = operation.with_user(user_manager).action_override_readiness()
            self.assertEqual(res.get('res_model'), 'customs.operation.override.wizard')
        except AccessError:
            self.fail("Customs Manager should be allowed to override readiness check.")
