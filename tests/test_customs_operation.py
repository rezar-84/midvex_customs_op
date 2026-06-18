# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestCustomsOperation(TransactionCase):

    def setUp(self):
        super(TestCustomsOperation, self).setUp()

        # Retrieve required base models for testing
        self.stage_draft = self.env.ref('midvex_customs_op.stage_draft')
        self.doc_type_invoice = self.env['customs.document.type'].create({
            'name': 'Invoice',
            'code': 'INV',
        })

        # Test product creation
        self.product_a = self.env['product.product'].create({
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
