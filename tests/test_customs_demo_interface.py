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
        
        # Clean up any pre-existing unreferenced sample data to establish a clean baseline
        config.action_cleanup_sample_data()
        
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
        sample_partners_after_count = self.env['res.partner'].search_count([('name', '=like', 'SAMPLE:%')])
        self.assertGreater(sample_partners_after_count, sample_partners_before)

        # Verify that the newly created sample partners have country_id and contact fields set correctly
        new_supplier = self.env['res.partner'].search([('name', '=', 'SAMPLE: Nippon Aqua Feed Corp.')], order='id desc', limit=1)
        self.assertTrue(new_supplier.country_id, "Sample supplier should have a country_id set")
        self.assertEqual(new_supplier.country_id.code, 'JP')
        self.assertEqual(new_supplier.street, '1-1-1 Minato-ku, Shibaura')
        self.assertEqual(new_supplier.city, 'Tokyo')
        self.assertEqual(new_supplier.zip, '108-0023')
        self.assertEqual(new_supplier.phone, '+81-3-5555-0192')
        self.assertEqual(new_supplier.email, 'supplier@nipponaquafeed.co.jp')
        self.assertEqual(new_supplier.website, 'https://www.nipponaquafeed.co.jp')

        new_broker = self.env['res.partner'].search([('name', '=', 'SAMPLE: Gümrükçü Ahmet ve Ortakları Müşavirlik')], order='id desc', limit=1)
        self.assertTrue(new_broker.country_id, "Sample broker should have a country_id set")
        self.assertEqual(new_broker.country_id.code, 'TR')
        self.assertEqual(new_broker.street, 'Atatürk Caddesi, No: 45, Daire: 12, Alsancak')
        self.assertEqual(new_broker.city, 'İzmir')
        self.assertEqual(new_broker.zip, '35220')
        self.assertEqual(new_broker.phone, '+90-232-444-0123')
        self.assertEqual(new_broker.email, 'ahmet@ahmetgumruk.com.tr')
        self.assertEqual(new_broker.website, 'https://www.ahmetgumruk.com.tr')

        new_forwarder = self.env['res.partner'].search([('name', '=', 'SAMPLE: Global Logistics Solutions LLC')], order='id desc', limit=1)
        self.assertTrue(new_forwarder.country_id, "Sample forwarder should have a country_id set")
        self.assertEqual(new_forwarder.country_id.code, 'US')
        self.assertEqual(new_forwarder.street, '500 Fifth Avenue, Suite 1200')
        self.assertEqual(new_forwarder.city, 'New York')
        self.assertEqual(new_forwarder.zip, '10110')
        self.assertEqual(new_forwarder.phone, '+1-212-555-0145')
        self.assertEqual(new_forwarder.email, 'contact@globallogistics.com')
        self.assertEqual(new_forwarder.website, 'https://www.globallogistics.com')

        new_carrier = self.env['res.partner'].search([('name', '=', 'SAMPLE: Mediterranean Shipping Line')], order='id desc', limit=1)
        self.assertTrue(new_carrier.country_id, "Sample carrier should have a country_id set")
        self.assertEqual(new_carrier.country_id.code, 'CH')
        self.assertEqual(new_carrier.street, 'Chemin Rieu 12-14')
        self.assertEqual(new_carrier.city, 'Geneva')
        self.assertEqual(new_carrier.zip, '1208')
        self.assertEqual(new_carrier.phone, '+41-22-703-8888')
        self.assertEqual(new_carrier.email, 'info@msc.com')
        self.assertEqual(new_carrier.website, 'https://www.msc.com')

        new_manufacturer = self.env['res.partner'].search([('name', '=', 'SAMPLE: Hokkaido Bio Production Factory')], order='id desc', limit=1)
        self.assertTrue(new_manufacturer.country_id, "Sample manufacturer should have a country_id set")
        self.assertEqual(new_manufacturer.country_id.code, 'JP')
        self.assertEqual(new_manufacturer.street, '2-3 Kita 9-jo Nishi, Kita-ku')
        self.assertEqual(new_manufacturer.city, 'Sapporo')
        self.assertEqual(new_manufacturer.zip, '060-0809')
        self.assertEqual(new_manufacturer.phone, '+81-11-777-0155')
        self.assertEqual(new_manufacturer.email, 'hokkaido-bio@factory.co.jp')
        self.assertEqual(new_manufacturer.website, 'https://www.hokkaido-bio.co.jp')

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

    def test_demo_data_contacts(self):
        """Test that loaded demo data partners have their country_id and contact info set correctly."""
        supplier = self.env.ref('midvex_customs_op.partner_demo_supplier', raise_if_not_found=False)
        if supplier:
            self.assertEqual(supplier.country_id.code, 'JP')
            self.assertEqual(supplier.street, '1-1-1 Minato-ku, Shibaura')
            self.assertEqual(supplier.city, 'Tokyo')
            self.assertEqual(supplier.zip, '108-0023')
            self.assertEqual(supplier.phone, '+81-3-5555-0192')
            self.assertEqual(supplier.email, 'supplier@nipponaquafeed.co.jp')
            self.assertEqual(supplier.website, 'https://www.nipponaquafeed.co.jp')
        
        broker = self.env.ref('midvex_customs_op.partner_demo_broker', raise_if_not_found=False)
        if broker:
            self.assertEqual(broker.country_id.code, 'TR')
            self.assertEqual(broker.street, 'Atatürk Caddesi, No: 45, Daire: 12, Alsancak')
            self.assertEqual(broker.city, 'İzmir')
            self.assertEqual(broker.zip, '35220')
            self.assertEqual(broker.phone, '+90-232-444-0123')
            self.assertEqual(broker.email, 'ahmet@ahmetgumruk.com.tr')
            self.assertEqual(broker.website, 'https://www.ahmetgumruk.com.tr')

        forwarder = self.env.ref('midvex_customs_op.partner_demo_forwarder', raise_if_not_found=False)
        if forwarder:
            self.assertEqual(forwarder.country_id.code, 'US')
            self.assertEqual(forwarder.street, '500 Fifth Avenue, Suite 1200')
            self.assertEqual(forwarder.city, 'New York')
            self.assertEqual(forwarder.zip, '10110')
            self.assertEqual(forwarder.phone, '+1-212-555-0145')
            self.assertEqual(forwarder.email, 'contact@globallogistics.com')
            self.assertEqual(forwarder.website, 'https://www.globallogistics.com')

        carrier = self.env.ref('midvex_customs_op.partner_demo_carrier', raise_if_not_found=False)
        if carrier:
            self.assertEqual(carrier.country_id.code, 'CH')
            self.assertEqual(carrier.street, 'Chemin Rieu 12-14')
            self.assertEqual(carrier.city, 'Geneva')
            self.assertEqual(carrier.zip, '1208')
            self.assertEqual(carrier.phone, '+41-22-703-8888')
            self.assertEqual(carrier.email, 'info@msc.com')
            self.assertEqual(carrier.website, 'https://www.msc.com')

        manufacturer = self.env.ref('midvex_customs_op.partner_demo_manufacturer', raise_if_not_found=False)
        if manufacturer:
            self.assertEqual(manufacturer.country_id.code, 'JP')
            self.assertEqual(manufacturer.street, '2-3 Kita 9-jo Nishi, Kita-ku')
            self.assertEqual(manufacturer.city, 'Sapporo')
            self.assertEqual(manufacturer.zip, '060-0809')
            self.assertEqual(manufacturer.phone, '+81-11-777-0155')
            self.assertEqual(manufacturer.email, 'hokkaido-bio@factory.co.jp')
            self.assertEqual(manufacturer.website, 'https://www.hokkaido-bio.co.jp')
