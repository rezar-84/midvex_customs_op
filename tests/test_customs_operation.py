# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, AccessError

class TestCustomsOperation(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCustomsOperation, cls).setUpClass()

        # Retrieve required base models for testing
        cls.stage_draft = cls.env.ref('midvex_customs_op.stage_draft')
        cls.doc_type_invoice = cls.env['customs.document.type'].create({
            'name': 'Invoice',
            'code': 'INV',
        })

        # Test product creation
        cls.product_a = cls.env['product.product'].create({
            'name': 'Aquaculture Feed A',
            'type': 'consu',
        })

    def test_customs_operation_creation_and_sequence(self):
        """Test that creating a Customs File generates a CUS/ sequence reference."""
        operation = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
        })
        self.assertTrue(operation.name.startswith('CUS/'), "Customs File reference should start with 'CUS/' prefix")
        self.assertEqual(operation.stage_id, self.stage_draft, "Default stage should be Draft")

    def test_customs_operation_line_date_validation(self):
        """Test constraint: expiry date must be after production date."""
        operation = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
        })
        
        # This should fail: Expiry date is before production date
        with self.assertRaises(ValidationError):
            self.env['customs.operation.line'].create({
                'operation_id': operation.id,
                'product_id': self.product_a.id,
                'production_date': '2026-06-18',
                'expiry_date': '2026-06-10',
            })

    def test_customs_operation_line_weight_validation(self):
        """Test constraint: Net weight cannot exceed Gross weight and cannot be negative."""
        operation = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
        })

        # This should fail: Net weight > Gross weight
        with self.assertRaises(ValidationError):
            self.env['customs.operation.line'].create({
                'operation_id': operation.id,
                'product_id': self.product_a.id,
                'net_weight': 100.0,
                'gross_weight': 50.0,
            })

        # This should fail: Negative weight
        with self.assertRaises(ValidationError):
            self.env['customs.operation.line'].create({
                'operation_id': operation.id,
                'product_id': self.product_a.id,
                'net_weight': -10.0,
                'gross_weight': 50.0,
            })

    def test_customs_operation_document_statistics(self):
        """Test document completion statistics computation on Customs File."""
        operation = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
        })

        # Add 2 document requirements
        req_1 = self.env['customs.document.requirement'].create({
            'operation_id': operation.id,
            'document_type_id': self.doc_type_invoice.id,
            'name': 'Invoice Document',
            'state': 'requested',
        })
        req_2 = self.env['customs.document.requirement'].create({
            'operation_id': operation.id,
            'document_type_id': self.doc_type_invoice.id,
            'name': 'Invoice Document 2',
            'state': 'approved',
        })

        # Force recomputation of stored fields
        operation.flush_recordset()

        self.assertEqual(operation.document_total, 2, "Total documents count should be 2")
        self.assertEqual(operation.document_approved_count, 1, "Approved documents count should be 1")
        self.assertEqual(operation.document_missing_count, 1, "Missing documents count should be 1")
        self.assertEqual(operation.document_completion_percentage, 50.0, "Completion percentage should be 50%")

    def test_customs_operation_shipment_readiness(self):
        """Test the shipment readiness calculation logic."""
        # 1. Initially false due to missing logistics data
        operation = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
        })
        operation.flush_recordset()
        self.assertFalse(operation.shipment_ready)
        self.assertIn("Missing fields:", operation.blocking_reason_text)

        # 2. Add logistics data -> becomes true (as no doc requirements exist yet)
        country_tr = self.env['res.country'].search([], limit=1)
        incoterm_fob = self.env['account.incoterms'].search([], limit=1)
        operation.write({
            'transport_mode': 'sea',
            'origin_country_id': country_tr.id,
            'departure_country_id': country_tr.id,
            'destination_country_id': country_tr.id,
            'incoterm_id': incoterm_fob.id,
        })
        operation.flush_recordset()
        self.assertTrue(operation.shipment_ready)
        self.assertEqual(operation.blocking_reason_text, "")

        # 3. Add blocking document requirement -> becomes false
        req = self.env['customs.document.requirement'].create({
            'operation_id': operation.id,
            'document_type_id': self.doc_type_invoice.id,
            'name': 'Invoice Doc',
            'state': 'requested',
            'is_blocking': True,
        })
        operation.flush_recordset()
        self.assertFalse(operation.shipment_ready)
        self.assertIn("Document 'Invoice Doc': incomplete", operation.blocking_reason_text)

        # 4. Mark document as approved -> becomes true
        req.write({'state': 'approved'})
        operation.flush_recordset()
        self.assertTrue(operation.shipment_ready)

    def test_customs_operation_manager_override(self):
        """Test manager override controls and wizards."""
        # Setup operation blocked by missing fields
        operation = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
        })
        operation.flush_recordset()
        self.assertFalse(operation.shipment_ready)

        # Setup security groups
        group_manager = self.env.ref('midvex_customs_op.group_customs_manager')
        group_user = self.env.ref('midvex_customs_op.group_customs_user')
        
        manager_user = self.env['res.users'].create({
            'name': 'Manager User',
            'login': 'manager_override_test',
            'email': 'manager@test.com',
            'group_ids': [(6, 0, [group_manager.id])]
        })
        normal_user = self.env['res.users'].create({
            'name': 'Normal User',
            'login': 'normal_user_override_test',
            'email': 'normal@test.com',
            'group_ids': [(6, 0, [group_user.id])]
        })

        # 1. Normal user attempts override -> raises AccessError
        with self.assertRaises(AccessError):
            operation.with_user(normal_user).action_override_readiness()

        # 2. Manager user overrides using the wizard
        wizard_action = operation.with_user(manager_user).action_override_readiness()
        wizard = self.env[wizard_action['res_model']].with_user(manager_user).create({
            'operation_id': wizard_action['context']['default_operation_id'],
            'reason': 'Urgent shipment, documents incoming tomorrow.',
        })
        wizard.action_confirm()

        operation.flush_recordset()
        self.assertTrue(operation.shipment_ready)
        self.assertTrue(operation.is_overridden)
        self.assertEqual(operation.override_user_id, manager_user)

        # 3. Manager resets override
        operation.with_user(manager_user).action_reset_override()
        operation.flush_recordset()
        self.assertFalse(operation.shipment_ready)
        self.assertFalse(operation.is_overridden)

    def test_customs_operation_closing_validations(self):
        """Test validation controls when closing a Customs File."""
        stage_closed = self.env['customs.stage'].create({
            'name': 'Test Closed Stage',
            'sequence': 12,
            'is_closed': True,
        })
        operation = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
        })

        # Add incomplete mandatory document
        self.env['customs.document.requirement'].create({
            'operation_id': operation.id,
            'document_type_id': self.doc_type_invoice.id,
            'name': 'Invoice Doc',
            'state': 'requested',
            'requirement_level': 'mandatory',
        })

        # 1. Attempt to close fails due to incomplete documents
        with self.assertRaises(ValidationError):
            operation.write({'stage_id': stage_closed.id})

        # Approve the document requirement
        operation.document_requirement_ids[0].write({'state': 'approved'})

        # Create critical activity type and an activity
        act_type_critical = self.env['mail.activity.type'].create({
            'name': 'Critical Review',
            'is_critical': True,
        })
        self.env['mail.activity'].create({
            'res_model': 'customs.operation',
            'res_id': operation.id,
            'activity_type_id': act_type_critical.id,
            'user_id': self.env.user.id,
        })

        # 2. Attempt to close fails due to open critical activities
        with self.assertRaises(ValidationError):
            operation.write({'stage_id': stage_closed.id})

        # Complete the activity
        operation.activity_ids.action_done()

        # 3. Attempt to close succeeds
        operation.write({'stage_id': stage_closed.id})
        self.assertEqual(operation.stage_id, stage_closed)

    def test_customs_operation_reporting_views(self):
        """Smoke test verifying that reporting views and actions are correctly defined and loadable."""
        action_op_analysis = self.env.ref('midvex_customs_op.action_customs_operation_analysis')
        self.assertTrue(action_op_analysis)
        self.assertEqual(action_op_analysis.res_model, 'customs.operation')
        self.assertIn('pivot', action_op_analysis.view_mode)
        self.assertIn('graph', action_op_analysis.view_mode)
        self.assertIn('calendar', action_op_analysis.view_mode)

        action_doc_analysis = self.env.ref('midvex_customs_op.action_customs_document_analysis')
        self.assertTrue(action_doc_analysis)
        self.assertEqual(action_doc_analysis.res_model, 'customs.document.requirement')
        self.assertIn('pivot', action_doc_analysis.view_mode)
        self.assertIn('graph', action_doc_analysis.view_mode)

    def test_customs_operation_deletion_protection(self):
        """Test that Customs Files can only be deleted in Draft stage."""
        stage_waiting = self.env.ref('midvex_customs_op.stage_waiting_docs')
        
        # 1. Deleting a Draft operation succeeds
        op_draft = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
        })
        op_id = op_draft.id
        op_draft.unlink()
        self.assertFalse(self.env['customs.operation'].browse(op_id).exists())

        # 2. Deleting an operation in a non-Draft stage fails
        op_non_draft = self.env['customs.operation'].create({
            'stage_id': stage_waiting.id,
        })
        with self.assertRaises(ValidationError):
            op_non_draft.unlink()

    def test_customs_operation_line_deletion_protection(self):
        """Test that product lines can only be deleted in Draft and Waiting for Docs stages."""
        stage_waiting = self.env.ref('midvex_customs_op.stage_waiting_docs')
        stage_doc_review = self.env.ref('midvex_customs_op.stage_doc_review')

        op = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
        })
        line = self.env['customs.operation.line'].create({
            'operation_id': op.id,
            'product_id': self.product_a.id,
        })

        # 1. Delete succeeds in Draft stage
        line_id = line.id
        line.unlink()
        self.assertFalse(self.env['customs.operation.line'].browse(line_id).exists())

        # Create new line for Waiting for Docs stage
        line2 = self.env['customs.operation.line'].create({
            'operation_id': op.id,
            'product_id': self.product_a.id,
        })
        op.write({'stage_id': stage_waiting.id})
        
        # 2. Delete succeeds in Waiting for Documents stage
        line2_id = line2.id
        line2.unlink()
        self.assertFalse(self.env['customs.operation.line'].browse(line2_id).exists())

        # Create new line for Document Review stage
        line3 = self.env['customs.operation.line'].create({
            'operation_id': op.id,
            'product_id': self.product_a.id,
        })
        op.write({'stage_id': stage_doc_review.id})

        # 3. Delete fails in Document Review stage
        with self.assertRaises(ValidationError):
            line3.unlink()

    def test_customs_operation_name_unique_constraint(self):
        """Test SQL constraint: Customs File reference must be unique per company."""
        from psycopg2 import IntegrityError
        from odoo.tools import mute_logger

        self.env['customs.operation'].create({
            'name': 'CUS/UNIQUE/TEST',
            'stage_id': self.stage_draft.id,
        })

        # Creating another record with the same name and company should raise IntegrityError
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['customs.operation'].create({
                'name': 'CUS/UNIQUE/TEST',
                'stage_id': self.stage_draft.id,
            })

    def test_customs_operation_line_quantity_constraints(self):
        """Test constraints verifying positive range values for quantity and package_count."""
        op = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
        })

        # 1. Negative quantity fails
        with self.assertRaises(ValidationError):
            self.env['customs.operation.line'].create({
                'operation_id': op.id,
                'product_id': self.product_a.id,
                'quantity': -5.0,
                'package_count': 5,
            })

        # 2. Zero quantity fails
        with self.assertRaises(ValidationError):
            self.env['customs.operation.line'].create({
                'operation_id': op.id,
                'product_id': self.product_a.id,
                'quantity': 0.0,
                'package_count': 5,
            })

        # 3. Negative package count fails
        with self.assertRaises(ValidationError):
            self.env['customs.operation.line'].create({
                'operation_id': op.id,
                'product_id': self.product_a.id,
                'quantity': 10.0,
                'package_count': -1,
            })

        # 4. Zero package count fails
        with self.assertRaises(ValidationError):
            self.env['customs.operation.line'].create({
                'operation_id': op.id,
                'product_id': self.product_a.id,
                'quantity': 10.0,
                'package_count': 0,
            })

    def test_import_operation_feedback_fields_and_computes(self):
        """Test commercial default values and costs aggregation computes."""
        supplier = self.env['res.partner'].create({'name': 'Nevzat Test Supplier'})
        po = self.env['purchase.order'].create({
            'partner_id': supplier.id,
        })
        currency_eur = self.env.ref('base.EUR')
        po.write({
            'currency_id': currency_eur.id,
        })
        
        op = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
            'purchase_order_ids': [(4, po.id)],
        })
        op.flush_recordset()
        
        self.assertEqual(op.currency_id, currency_eur)
        
        op.write({
            'cost_freight': 500.0,
            'cost_customs_tax': 150.0,
            'cost_broker_expenses': 100.0,
            'cost_stamp_tax': 50.0,
            'cost_storage': 80.0,
            'cost_exchange_diff': 20.0,
            'cost_other': 10.0,
        })
        op.flush_recordset()
        self.assertEqual(op.cost_total, 910.0, "Total costs should sum up all cost items correctly.")

    def test_import_operation_automatic_activities(self):
        """Test that key changes automatically trigger mail activities."""
        op = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
        })
        op.flush_recordset()
        
        op.write({'bl_number': 'BL123456'})
        op.flush_recordset()
        
        activities = self.env['mail.activity'].search([
            ('res_model', '=', 'customs.operation'),
            ('res_id', '=', op.id),
        ])
        self.assertTrue(any(act.summary == "B/L Uploaded - Action Required" for act in activities))
        
        op.write({'warehouse_received': True})
        op.flush_recordset()
        activities = self.env['mail.activity'].search([
            ('res_model', '=', 'customs.operation'),
            ('res_id', '=', op.id),
        ])
        self.assertTrue(any(act.summary == "Warehouse Delivery Completed" for act in activities))

        op.write({'damaged_product': True, 'damage_description': 'Feed bags torn'})
        op.flush_recordset()
        activities = self.env['mail.activity'].search([
            ('res_model', '=', 'customs.operation'),
            ('res_id', '=', op.id),
        ])
        self.assertTrue(any(act.summary == "Discrepancy / Damaged Cargo Recorded" for act in activities))


