# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo import fields

class TestCustomsIntegration(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCustomsIntegration, cls).setUpClass()

        # Companies
        cls.company_main = cls.env.company
        cls.company_other = cls.env['res.company'].create({'name': 'Other Company'})

        # Ensure company main country is set to Turkey (not US) to differentiate import purchases
        cls.country_tr = cls.env.ref('base.tr', raise_if_not_found=False)
        if not cls.country_tr:
            cls.country_tr = cls.env['res.country'].create({'name': 'Turkey', 'code': 'TR'})
        cls.company_main.partner_id.write({'country_id': cls.country_tr.id})

        # Partners
        cls.vendor_domestic = cls.env['res.partner'].create({
            'name': 'Domestic Vendor',
            'country_id': cls.company_main.partner_id.country_id.id,
            'company_id': False,
        })
        
        cls.country_us = cls.env.ref('base.us', raise_if_not_found=False)
        if not cls.country_us:
            cls.country_us = cls.env['res.country'].create({'name': 'United States', 'code': 'US'})
            
        cls.vendor_foreign = cls.env['res.partner'].create({
            'name': 'Foreign Vendor',
            'country_id': cls.country_us.id,
            'company_id': False,
        })

        # Stages
        cls.stage_draft = cls.env.ref('midvex_customs_op.stage_draft')
        cls.stage_waiting_docs = cls.env.ref('midvex_customs_op.stage_waiting_docs')
        cls.stage_cleared = cls.env.ref('midvex_customs_op.stage_cleared')

        # Document Types
        cls.doc_type_inv = cls.env.ref('midvex_customs_op.doc_type_inv', raise_if_not_found=False)
        if not cls.doc_type_inv:
            cls.doc_type_inv = cls.env['customs.document.type'].create({
                'name': 'Commercial Invoice',
                'code': 'INV',
            })

        # Product Templates and Products
        cls.product_customs_req = cls.env['product.product'].create({
            'name': 'Imported Feed A',
            'type': 'consu',
            'customs_required': True,
        })
        cls.product_normal = cls.env['product.product'].create({
            'name': 'Local Feed B',
            'type': 'consu',
            'customs_required': False,
        })

    def test_po_confirm_auto_create_operation(self):
        """Test PO confirmation auto-creates Customs Operation for foreign vendor."""
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor_foreign.id,
            'company_id': self.company_main.id,
            'order_line': [(0, 0, {
                'product_id': self.product_normal.id,
                'name': self.product_normal.name,
                'product_qty': 10,
                'price_unit': 100,
            })]
        })
        
        po._compute_is_import_purchase()
        po._compute_customs_required()
        self.assertTrue(po.is_import_purchase, "Foreign vendor should make it an import purchase")
        self.assertTrue(po.customs_required, "Import purchase requires customs tracking")

        po.button_confirm()
        
        self.assertEqual(po.customs_operation_count, 1, "Customs File should be auto-created on confirmation")
        op = po.customs_operation_ids[0]
        self.assertEqual(op.origin_country_id, self.vendor_foreign.country_id, "Origin country should match vendor country")
        self.assertEqual(len(op.operation_line_ids), 1, "Lines should be imported")
        self.assertEqual(op.operation_line_ids[0].quantity, 10, "Quantity should match PO line")

    def test_po_confirm_no_auto_create_for_domestic(self):
        """Test PO confirmation does not auto-create Customs Operation for domestic vendor unless flagged."""
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor_domestic.id,
            'company_id': self.company_main.id,
            'order_line': [(0, 0, {
                'product_id': self.product_normal.id,
                'name': self.product_normal.name,
                'product_qty': 10,
                'price_unit': 100,
            })]
        })
        
        po._compute_is_import_purchase()
        po._compute_customs_required()
        self.assertFalse(po.is_import_purchase)
        self.assertFalse(po.customs_required)

        po.button_confirm()
        self.assertEqual(po.customs_operation_count, 0, "Domestic PO with normal products should not auto-create Customs File")

    def test_po_confirm_domestic_with_customs_product(self):
        """Test PO confirmation auto-creates Customs Operation for domestic vendor if product requires it."""
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor_domestic.id,
            'company_id': self.company_main.id,
            'order_line': [(0, 0, {
                'product_id': self.product_customs_req.id,
                'name': self.product_customs_req.name,
                'product_qty': 5,
                'price_unit': 100,
            })]
        })
        
        po._compute_is_import_purchase()
        po._compute_customs_required()
        self.assertTrue(po.customs_required, "Domestic PO with customs required product should flag customs_required")

        po.button_confirm()
        self.assertEqual(po.customs_operation_count, 1, "Domestic PO with customs required product should auto-create Customs File")

    def test_lines_and_quantities_sync(self):
        """Test PO line creations, updates, and deletes are synced to the Customs File."""
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor_foreign.id,
            'company_id': self.company_main.id,
            'order_line': [(0, 0, {
                'product_id': self.product_normal.id,
                'name': self.product_normal.name,
                'product_qty': 10,
                'price_unit': 100,
            })]
        })
        po.button_confirm()
        op = po.customs_operation_ids[0]
        line_col = op.operation_line_ids[0]
        po_line = po.order_line[0]

        # 1. Update quantity on PO line
        po_line.write({'product_qty': 15})
        self.assertEqual(line_col.quantity, 15, "Quantity changes should be synced")

        # 2. Add new line to PO
        new_po_line = self.env['purchase.order.line'].create({
            'order_id': po.id,
            'product_id': self.product_customs_req.id,
            'name': self.product_customs_req.name,
            'product_qty': 8,
            'price_unit': 120,
        })
        self.assertEqual(len(op.operation_line_ids), 2, "Adding PO line should sync to customs operation")
        col_new = op.operation_line_ids.filtered(lambda l: l.purchase_order_line_id == new_po_line)
        self.assertTrue(col_new, "New customs line should link to the new PO line")
        self.assertEqual(col_new.quantity, 8)

        # 3. Delete a PO line
        po.state = 'draft'
        new_po_line.unlink()
        po.state = 'purchase'
        self.assertEqual(len(op.operation_line_ids), 1, "Deleting PO line should sync to customs operation")

        # 4. Lock lines (move past Waiting for Docs)
        stage_doc_review = self.env.ref('midvex_customs_op.stage_doc_review')
        op.write({'stage_id': stage_doc_review.id})

        # Try to modify quantity on PO line - should not propagate to locked lines
        po_line.write({'product_qty': 20})
        self.assertEqual(line_col.quantity, 15, "Locked lines should not sync changes")

        # Try to manually edit customs line when locked - should raise ValidationError
        with self.assertRaises(ValidationError):
            line_col.write({'quantity': 25})

    def test_stock_picking_warnings_and_blocks(self):
        """Test stock picking receipt warning and strict block setting."""
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor_foreign.id,
            'company_id': self.company_main.id,
            'order_line': [(0, 0, {
                'product_id': self.product_normal.id,
                'name': self.product_normal.name,
                'product_qty': 10,
                'price_unit': 100,
            })]
        })
        po.button_confirm()
        op = po.customs_operation_ids[0]
        
        picking = po.picking_ids[0]
        self.assertIn(picking, op.picking_ids, "Stock picking should be auto-linked to Customs File")

        stage_shipped = self.env.ref('midvex_customs_op.stage_shipped')
        op.write({'stage_id': stage_shipped.id})

        # 1. Test soft warning (block_receipt is False)
        self.env['ir.config_parameter'].sudo().set_param('midvex_customs_op.customs_block_receipt_before_clearance', False)
        
        picking.button_validate()
        self.assertEqual(picking.state, 'done', "Picking should be validated with soft warning setting")

        # 2. Test strict block (block_receipt is True)
        po_2 = self.env['purchase.order'].create({
            'partner_id': self.vendor_foreign.id,
            'company_id': self.company_main.id,
            'order_line': [(0, 0, {
                'product_id': self.product_normal.id,
                'name': self.product_normal.name,
                'product_qty': 5,
                'price_unit': 100,
            })]
        })
        po_2.button_confirm()
        op_2 = po_2.customs_operation_ids[0]
        op_2.write({'stage_id': stage_shipped.id})
        picking_2 = po_2.picking_ids[0]

        self.env['ir.config_parameter'].sudo().set_param('midvex_customs_op.customs_block_receipt_before_clearance', True)

        with self.assertRaises(ValidationError):
            picking_2.button_validate()

        op_2.write({'stage_id': self.stage_cleared.id})
        picking_2.button_validate()
        self.assertEqual(picking_2.state, 'done', "Picking validation should succeed after customs clearance")

    def test_vendor_bill_linkages(self):
        """Test vendor bill auto-linking."""
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor_foreign.id,
            'company_id': self.company_main.id,
            'order_line': [(0, 0, {
                'product_id': self.product_normal.id,
                'name': self.product_normal.name,
                'product_qty': 10,
                'price_unit': 100,
            })]
        })
        po.button_confirm()
        op = po.customs_operation_ids[0]

        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.vendor_foreign.id,
            'company_id': self.company_main.id,
            'invoice_line_ids': [(0, 0, {
                'purchase_line_id': po.order_line[0].id,
                'product_id': self.product_normal.id,
                'quantity': 10,
                'price_unit': 100,
            })]
        })

        self.assertEqual(bill.customs_operation_id, op, "Vendor bill should be auto-linked to the PO's Customs File")
        op.flush_recordset()
        self.assertEqual(op.vendor_bill_count, 1, "Customs File should count the linked bill")
        self.assertIn(bill, op.vendor_bill_ids, "Bill should appear in the customs operation's bills list")
