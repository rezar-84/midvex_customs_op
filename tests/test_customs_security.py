# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError

class TestCustomsSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCustomsSecurity, cls).setUpClass()
        
        # Find the groups
        cls.group_user = cls.env.ref('midvex_customs_op.group_customs_user')
        cls.group_approver = cls.env.ref('midvex_customs_op.group_customs_approver')
        cls.group_manager = cls.env.ref('midvex_customs_op.group_customs_manager')
        cls.group_admin = cls.env.ref('midvex_customs_op.group_customs_admin')

        # Create test users for different roles
        cls.user_customs_user = cls.env['res.users'].create({
            'name': 'Test Customs User',
            'login': 'customs_user_test',
            'email': 'user@test.com',
            'group_ids': [(6, 0, [cls.group_user.id])]
        })

        cls.user_customs_approver = cls.env['res.users'].create({
            'name': 'Test Customs Approver',
            'login': 'customs_approver_test',
            'email': 'approver@test.com',
            'group_ids': [(6, 0, [cls.group_approver.id])]
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

    def test_document_requirement_state_transitions(self):
        """Test document requirement state change protections."""
        user_manager = self.env['res.users'].create({
            'name': 'Customs Manager',
            'login': 'customs_manager_state_test',
            'email': 'manager_state@test.com',
            'group_ids': [(6, 0, [self.group_manager.id])]
        })
        op = self.env['customs.operation'].create({'name': 'CUS/DOC/001'})
        doc_type = self.env['customs.document.type'].create({'name': 'Invoice', 'code': 'INV'})
        
        req = self.env['customs.document.requirement'].create({
            'operation_id': op.id,
            'document_type_id': doc_type.id,
            'name': 'Test Invoice',
        })

        # 1. Customs User cannot approve the document
        with self.assertRaises(AccessError):
            req.with_user(self.user_customs_user).write({'state': 'approved'})

        # 2. Document Approver can approve
        req.with_user(self.user_customs_approver).write({'state': 'approved'})
        self.assertEqual(req.state, 'approved')

        # 3. Document Approver cannot reset back to requested
        with self.assertRaises(AccessError):
            req.with_user(self.user_customs_approver).write({'state': 'requested'})

        # 4. Customs Manager can reset back to requested
        req.with_user(user_manager).write({'state': 'requested'})
        self.assertEqual(req.state, 'requested')

    def test_stage_transition_restrictions(self):
        """Test that regular users cannot perform backward or large forward transitions on operations."""
        user_manager = self.env['res.users'].create({
            'name': 'Customs Manager',
            'login': 'customs_manager_stage_test',
            'email': 'manager_stage@test.com',
            'group_ids': [(6, 0, [self.group_manager.id])]
        })
        stage_draft = self.env.ref('midvex_customs_op.stage_draft')
        stage_waiting = self.env.ref('midvex_customs_op.stage_waiting_docs')
        stage_doc_review = self.env.ref('midvex_customs_op.stage_doc_review')
        stage_ready = self.env.ref('midvex_customs_op.stage_ready_ship') # sequence 5
        stage_closed = self.env.ref('midvex_customs_op.stage_closed') # sequence 12 (is_closed=True)

        op = self.env['customs.operation'].create({
            'stage_id': stage_draft.id,
        })

        # 1. Customs User moves Draft (1) -> Waiting (2) -> Document Review (3): Succeeds (linear forward)
        op.with_user(self.user_customs_user).write({'stage_id': stage_waiting.id})
        op.with_user(self.user_customs_user).write({'stage_id': stage_doc_review.id})
        self.assertEqual(op.stage_id, stage_doc_review)

        # 2. Customs User moves backward Document Review (3) -> Waiting (2): Fails with AccessError
        with self.assertRaises(AccessError):
            op.with_user(self.user_customs_user).write({'stage_id': stage_waiting.id})

        # 3. Manager moves backward: Succeeds
        op.with_user(user_manager).write({'stage_id': stage_waiting.id})
        self.assertEqual(op.stage_id, stage_waiting)

        # Move forward to Ready to Ship (5)
        op.with_user(user_manager).write({'stage_id': stage_ready.id})

        # 4. Customs User tries to jump Ready to Ship (5) -> Closed (12, skip > 3): Fails with ValidationError/AccessError
        with self.assertRaises(ValidationError):
            op.with_user(self.user_customs_user).write({'stage_id': stage_closed.id})

    def test_active_archiving_restrictions(self):
        """Test that regular users cannot archive Customs Files."""
        user_manager = self.env['res.users'].create({
            'name': 'Customs Manager',
            'login': 'customs_manager_active_test',
            'email': 'manager_active@test.com',
            'group_ids': [(6, 0, [self.group_manager.id])]
        })
        op = self.env['customs.operation'].create({'name': 'CUS/ACTIVE/001'})

        # 1. Customs User cannot archive
        with self.assertRaises(AccessError):
            op.with_user(self.user_customs_user).write({'active': False})

        # 2. Customs Manager can archive
        op.with_user(user_manager).write({'active': False})
        self.assertFalse(op.active)
