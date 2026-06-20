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
        
        # Locate sample partners and products
        sample_partners = self.env['res.partner'].search([('name', '=like', 'SAMPLE:%')])
        sample_products = self.env['product.product'].search([('name', '=like', 'SAMPLE:%')])
        
        # Locate and delete any referencing purchase orders, stock pickings, or vendor bills
        if sample_partners or sample_products:
            pos = self.env['purchase.order'].search([
                '|', 
                ('partner_id', 'in', sample_partners.ids),
                ('order_line.product_id', 'in', sample_products.ids)
            ])
            if pos:
                # Cancel and delete pickings first
                pickings = self.env['stock.picking'].search([('purchase_id', 'in', pos.ids)])
                for picking in pickings:
                    if picking.state not in ('done', 'cancel'):
                        try:
                            picking.action_cancel()
                        except Exception:
                            pass
                    try:
                        picking.unlink()
                    except Exception:
                        pass
                
                # Cancel and delete vendor bills
                invoices = self.env['account.move'].search([
                    '|',
                    ('partner_id', 'in', sample_partners.ids),
                    ('invoice_line_ids.product_id', 'in', sample_products.ids)
                ])
                for inv in invoices:
                    if inv.state != 'draft':
                        try:
                            inv.button_draft()
                        except Exception:
                            pass
                    try:
                        inv.unlink()
                    except Exception:
                        pass
                
                # Cancel and delete POs
                pos.write({'state': 'cancel'})
                pos.unlink()
        
        # Clean up any pre-existing sample data to ensure clean state
        config.action_cleanup_sample_data()
        
        # Count initial matching sample records
        sample_ops_before = self.env['customs.operation'].search_count([('is_sample_data', '=', True)])
        self.assertEqual(sample_ops_before, 0)

        # Generate sample data
        config.action_generate_sample_data()

        # Check that operations were created
        sample_ops_after = self.env['customs.operation'].search_count([('is_sample_data', '=', True)])
        self.assertGreater(sample_ops_after, 0)

        # Check that partners and products with SAMPLE: prefix were created
        sample_partners = self.env['res.partner'].search_count([('name', '=like', 'SAMPLE:%')])
        self.assertGreater(sample_partners, 0)

        sample_products = self.env['product.product'].search_count([('name', '=like', 'SAMPLE:%')])
        self.assertGreater(sample_products, 0)

        # Clean up sample data
        config.action_cleanup_sample_data()

        # Verify they are deleted
        sample_ops_final = self.env['customs.operation'].search_count([('is_sample_data', '=', True)])
        self.assertEqual(sample_ops_final, 0)

        sample_partners_final = self.env['res.partner'].search_count([('name', '=like', 'SAMPLE:%')])
        self.assertEqual(sample_partners_final, 0)

        sample_products_final = self.env['product.product'].search_count([('name', '=like', 'SAMPLE:%')])
        self.assertEqual(sample_products_final, 0)
