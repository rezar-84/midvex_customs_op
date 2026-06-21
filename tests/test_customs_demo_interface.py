# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestCustomsDemoInterface(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCustomsDemoInterface, cls).setUpClass()
        cls.stage_draft = cls.env.ref('midvex_customs_op.stage_draft')
        cls.doc_type_invoice = cls.env.ref('midvex_customs_op.doc_type_inv')

    def test_document_correction_count(self):
        """Test that correction pending documents are correctly counted and stored."""
        operation = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
        })
        self.assertEqual(operation.document_correction_count, 0)

        # Create document requirement
        req = self.env['customs.document.requirement'].create({
            'operation_id': operation.id,
            'document_type_id': self.doc_type_invoice.id,
            'name': 'Commercial Invoice',
            'state': 'correction_required',
            'rejection_reason': 'Need correction',
        })
        
        # Trigger recompute
        operation._compute_document_stats()
        self.assertEqual(operation.document_correction_count, 1)

        # Change state back
        req.write({'state': 'approved'})
        operation._compute_document_stats()
        self.assertEqual(operation.document_correction_count, 0)

    def test_sample_data_generator_and_cleanup(self):
        """Test the sample data generation and cleanup config actions."""
        config = self.env['res.config.settings'].create({})
        
        # Count initial matching sample records in the database
        sample_ops_before = self.env['customs.operation'].search_count([('is_sample_data', '=', True)])
        sample_partners_before = self.env['res.partner'].search_count([('name', '=like', 'SAMPLE:%')])
        sample_products_before = self.env['product.product'].search_count([('name', '=like', 'SAMPLE:%')])

        # Generate sample data
        config.action_generate_sample_data()

        # Check that operations were created
        sample_ops_after = self.env['customs.operation'].search_count([('is_sample_data', '=', True)])
        self.assertGreater(sample_ops_after, sample_ops_before)

        # Check that partners and products with SAMPLE: prefix were created
        sample_partners_after = self.env['res.partner'].search_count([('name', '=like', 'SAMPLE:%')])
        self.assertGreater(sample_partners_after, sample_partners_before)

        sample_products_after = self.env['product.product'].search_count([('name', '=like', 'SAMPLE:%')])
        self.assertGreater(sample_products_after, sample_products_before)

        # Clean up sample data
        config.action_cleanup_sample_data()

        # Verify they are deleted
        sample_ops_final = self.env['customs.operation'].search_count([('is_sample_data', '=', True)])
        self.assertEqual(sample_ops_final, 0)

        # Partners and products should return to their pre-existing counts
        sample_partners_final = self.env['res.partner'].search_count([('name', '=like', 'SAMPLE:%')])
        self.assertEqual(sample_partners_final, sample_partners_before)

        sample_products_final = self.env['product.product'].search_count([('name', '=like', 'SAMPLE:%')])
        self.assertEqual(sample_products_final, sample_products_before)
