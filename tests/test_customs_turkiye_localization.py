# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestCustomsTurkiyeLocalization(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCustomsTurkiyeLocalization, cls).setUpClass()

        # Get or create countries
        cls.country_tr = cls.env['res.country'].search([('code', '=', 'TR')], limit=1)
        if not cls.country_tr:
            cls.country_tr = cls.env['res.country'].create({
                'name': 'Turkey',
                'code': 'TR',
            })
            
        cls.country_us = cls.env['res.country'].search([('code', '=', 'US')], limit=1)
        if not cls.country_us:
            cls.country_us = cls.env['res.country'].create({
                'name': 'United States',
                'code': 'US',
            })

        cls.product_feed = cls.env['product.product'].create({
            'name': 'Artemia Feed',
            'type': 'consu',
        })

        cls.stage_draft = cls.env.ref('midvex_customs_op.stage_draft')

    def test_gtip_validation_turkey(self):
        """Test that GTİP code must be 12 digits for Turkey destination country."""
        # 1. Create operation with TR destination
        operation_tr = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
            'destination_country_id': self.country_tr.id,
        })

        # Valid 12-digit numeric code should succeed
        line_valid_1 = self.env['customs.operation.line'].create({
            'operation_id': operation_tr.id,
            'product_id': self.product_feed.id,
            'hs_code': '123456789012',
        })
        self.assertEqual(line_valid_1.hs_code, '123456789012')

        # Valid 12-digit code with spaces and dots should succeed (cleaned in constraints)
        line_valid_2 = self.env['customs.operation.line'].create({
            'operation_id': operation_tr.id,
            'product_id': self.product_feed.id,
            'hs_code': '1234.56.78.90 12',
        })
        self.assertEqual(line_valid_2.hs_code, '1234.56.78.90 12')

        # Invalid GTİP: less than 12 digits
        with self.assertRaises(ValidationError):
            self.env['customs.operation.line'].create({
                'operation_id': operation_tr.id,
                'product_id': self.product_feed.id,
                'hs_code': '1234567890',
            })

        # Invalid GTİP: contains letters
        with self.assertRaises(ValidationError):
            self.env['customs.operation.line'].create({
                'operation_id': operation_tr.id,
                'product_id': self.product_feed.id,
                'hs_code': '1234567890AB',
            })

    def test_gtip_validation_non_turkey(self):
        """Test that GTİP code format constraint is bypassed for non-Turkey destinations."""
        operation_us = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
            'destination_country_id': self.country_us.id,
        })

        # Standard HS code lengths (e.g. 6 or 10 digits) should succeed for US
        line_us = self.env['customs.operation.line'].create({
            'operation_id': operation_us.id,
            'product_id': self.product_feed.id,
            'hs_code': '123456',
        })
        self.assertEqual(line_us.hs_code, '123456')

    def test_declaration_number_validation_turkey(self):
        """Test Turkish Customs Declaration Number format validation."""
        # 16-character format: 2-digit year + 6-digit office code + 2-letter regime + 6-digit reg number
        # Example: 26340500IM012345 (26 = 2026, 340500 = Muratbey, IM = Import, 012345 = Number)

        # Valid declaration number for TR should succeed
        operation_tr_valid = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
            'destination_country_id': self.country_tr.id,
            'customs_declaration_number': '26340500IM012345',
        })
        self.assertEqual(operation_tr_valid.customs_declaration_number, '26340500IM012345')

        # Invalid: wrong length
        with self.assertRaises(ValidationError):
            self.env['customs.operation'].create({
                'stage_id': self.stage_draft.id,
                'destination_country_id': self.country_tr.id,
                'customs_declaration_number': '26340500IM0123',
            })

        # Invalid: wrong characters (e.g. regime contains digits instead of letters)
        with self.assertRaises(ValidationError):
            self.env['customs.operation'].create({
                'stage_id': self.stage_draft.id,
                'destination_country_id': self.country_tr.id,
                'customs_declaration_number': '2634050012012345',
            })

    def test_declaration_number_validation_non_turkey(self):
        """Test that validation is bypassed for non-Turkey operations."""
        operation_us = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
            'destination_country_id': self.country_us.id,
            'customs_declaration_number': 'SHORT-DECL-123',
        })
        self.assertEqual(operation_us.customs_declaration_number, 'SHORT-DECL-123')

    def test_turkiye_cost_computations(self):
        """Test that new specific cost fields are capitalized into cost_total, except KDV."""
        operation = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
            'cost_freight': 1000.0,
            'cost_customs_tax': 500.0,
            # Specific Turkey cost fields
            'cost_demurrage': 300.0,
            'cost_storage_warehouse': 200.0,
            'cost_kkdf': 150.0,
            'cost_delivery_order': 80.0,
            'cost_kdv': 1200.0, # KDV is deductible VAT, should be excluded from total
        })

        expected_total = (
            1000.0 + # Freight
            500.0 + # Customs Tax
            300.0 + # Demurrage
            200.0 + # Storage Warehouse
            150.0 + # KKDF
            80.0    # Delivery Order
        )

        self.assertEqual(operation.cost_total, expected_total)
        # Verify that KDV is recorded but not in total
        self.assertEqual(operation.cost_kdv, 1200.0)
        self.assertNotIn(1200.0, [operation.cost_total])
