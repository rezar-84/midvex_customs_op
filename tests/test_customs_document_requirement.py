# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo import fields

class TestCustomsDocumentRequirement(TransactionCase):

    def setUp(self):
        super(TestCustomsDocumentRequirement, self).setUp()

        self.stage_draft = self.env.ref('midvex_customs_op.stage_draft')
        self.stage_waiting_docs = self.env.ref('midvex_customs_op.stage_waiting_docs')
        self.stage_doc_review = self.env.ref('midvex_customs_op.stage_doc_review')

        # Create document type
        self.doc_type_invoice = self.env['customs.document.type'].create({
            'name': 'Invoice',
            'code': 'INV',
            'default_requirement_level': 'mandatory',
            'default_responsible_party': 'supplier',
        })

        # Partners
        self.partner_supplier = self.env['res.partner'].create({'name': 'Vendor Supplier'})
        self.partner_broker = self.env['res.partner'].create({'name': 'Customs Broker Partner'})
        self.partner_unrelated = self.env['res.partner'].create({'name': 'Unrelated Partner'})

        # Customs File (operation)
        self.operation = self.env['customs.operation'].create({
            'stage_id': self.stage_draft.id,
            'supplier_ids': [(4, self.partner_supplier.id)],
            'broker_id': self.partner_broker.id,
        })

    def test_rejection_reason_constraint(self):
        """Test that setting state to rejected/correction_required requires a rejection reason."""
        # Failure: No rejection reason on create
        with self.assertRaises(ValidationError):
            self.env['customs.document.requirement'].create({
                'operation_id': self.operation.id,
                'document_type_id': self.doc_type_invoice.id,
                'name': 'Invoice Document',
                'state': 'rejected',
            })

        # Success: With rejection reason
        req = self.env['customs.document.requirement'].create({
            'operation_id': self.operation.id,
            'document_type_id': self.doc_type_invoice.id,
            'name': 'Invoice Document',
            'state': 'rejected',
            'rejection_reason': 'Missing supplier signature',
        })
        self.assertEqual(req.state, 'rejected')

        # Failure: Writing state to correction_required without clearing or providing reason
        with self.assertRaises(ValidationError):
            req.write({
                'state': 'correction_required',
                'rejection_reason': False
            })

    def test_vendor_id_constraint(self):
        """Test that vendor_id is restricted to related parties of the Customs File."""
        # Failure: Assigning unrelated partner
        with self.assertRaises(ValidationError):
            self.env['customs.document.requirement'].create({
                'operation_id': self.operation.id,
                'document_type_id': self.doc_type_invoice.id,
                'name': 'Invoice',
                'vendor_id': self.partner_unrelated.id,
            })

        # Success: Assigning supplier partner
        req = self.env['customs.document.requirement'].create({
            'operation_id': self.operation.id,
            'document_type_id': self.doc_type_invoice.id,
            'name': 'Invoice',
            'vendor_id': self.partner_supplier.id,
        })
        self.assertEqual(req.vendor_id, self.partner_supplier)

        # Success: Assigning broker partner
        req.write({'vendor_id': self.partner_broker.id})
        self.assertEqual(req.vendor_id, self.partner_broker)

    def test_deletion_restrictions(self):
        """Test deletion restrictions based on attachments and stages."""
        req = self.env['customs.document.requirement'].create({
            'operation_id': self.operation.id,
            'document_type_id': self.doc_type_invoice.id,
            'name': 'Invoice',
        })

        # Deletion succeeds in draft/waiting stages with no attachments
        self.operation.write({'stage_id': self.stage_waiting_docs.id})
        req.unlink()

        # Re-create requirement
        req2 = self.env['customs.document.requirement'].create({
            'operation_id': self.operation.id,
            'document_type_id': self.doc_type_invoice.id,
            'name': 'Invoice 2',
        })

        # Failure: Attempting to delete when stage is past Waiting for Documents (e.g. Document Review)
        self.operation.write({'stage_id': self.stage_doc_review.id})
        with self.assertRaises(ValidationError):
            req2.unlink()

        # Move stage back to Draft
        self.operation.write({'stage_id': self.stage_draft.id})

        # Create mock attachment
        attachment = self.env['ir.attachment'].create({
            'name': 'test.pdf',
            'datas': b'dGVzdA==', # 'test' in base64
            'res_model': 'customs.document.requirement',
            'res_id': req2.id,
        })
        req2.write({'attachment_ids': [(4, attachment.id)]})

        # Failure: Attempting to delete when requirement has attachments
        with self.assertRaises(ValidationError):
            req2.unlink()

    def test_version_number_auto_increment(self):
        """Test that uploading new attachments automatically increments version_number."""
        req = self.env['customs.document.requirement'].create({
            'operation_id': self.operation.id,
            'document_type_id': self.doc_type_invoice.id,
            'name': 'Invoice',
        })
        self.assertEqual(req.version_number, 1)

        # Upload first attachment
        attachment1 = self.env['ir.attachment'].create({
            'name': 'v1.pdf',
            'datas': b'dGVzdA==',
            'res_model': 'customs.document.requirement',
            'res_id': req.id,
        })
        req.write({'attachment_ids': [(4, attachment1.id)]})
        self.assertEqual(req.version_number, 2)

        # Upload second attachment
        attachment2 = self.env['ir.attachment'].create({
            'name': 'v2.pdf',
            'datas': b'dGVzdA==',
            'res_model': 'customs.document.requirement',
            'res_id': req.id,
        })
        req.write({'attachment_ids': [(4, attachment2.id)]})
        self.assertEqual(req.version_number, 3)

        # Removing an attachment does not increment version
        req.write({'attachment_ids': [(3, attachment2.id)]})
        self.assertEqual(req.version_number, 3)

    def test_computed_fields_completion_and_overdue(self):
        """Test computed fields: is_complete, is_overdue, is_expired."""
        req = self.env['customs.document.requirement'].create({
            'operation_id': self.operation.id,
            'document_type_id': self.doc_type_invoice.id,
            'name': 'Invoice',
            'deadline': '2026-06-10', # past deadline
            'expiry_date': '2026-06-10', # past expiry
        })

        req.flush_recordset()
        self.assertFalse(req.is_complete)
        self.assertTrue(req.is_overdue)
        self.assertTrue(req.is_expired)

        # Approve the document -> marks it complete, stops being overdue/expired
        req.write({'state': 'approved'})
        req.flush_recordset()
        self.assertTrue(req.is_complete)
        self.assertFalse(req.is_overdue)
        self.assertFalse(req.is_expired)
