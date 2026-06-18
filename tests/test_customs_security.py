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
