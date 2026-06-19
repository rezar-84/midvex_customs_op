# Data Model Specification

## 1. `customs.operation` (Customs File)

Main Customs File record.

### Core fields
- `name` (Char): Unique sequence-generated reference (`CUS/YYYY/NNNN`).
- `active` (Boolean): Archive flag.
- `company_id` (Many2one): Company record.
- `stage_id` (Many2one): Linked stage (`customs.stage`).
- `priority` (Selection): Priority level (Normal, Medium, High, Urgent).
- `user_id` (Many2one): Responsible user (`res.users`).
- `color` (Integer): Kanban card color.

### Party relationships
- `supplier_ids` (Many2many): Suppliers (`res.partner`).
- `broker_id` (Many2one): Customs Broker (`res.partner`).
- `forwarder_id` (Many2one): Freight Forwarder (`res.partner`).
- `carrier_id` (Many2one): Carrier (`res.partner`).

### Core integrations & standard links
- `purchase_order_ids` (Many2many): Linked purchase orders (`purchase.order`).
- `picking_ids` (Many2many): Linked stock receipts (`stock.picking`).
- `invoice_ids` (Many2many): Linked vendor bills (`account.move`).
- `sale_order_ids` (Many2many): Linked sales orders (`sale.order`).
- `sale_order_count` (Integer): Count of linked sales orders.
- `operation_line_ids` (One2many): Linked lines (`customs.operation.line`).
- `document_requirement_ids` (One2many): Linked documents (`customs.document.requirement`).

### Financial fields
- `currency_id` (Many2one): Currency (`res.currency`) synced from Purchase.
- `amount_total` (Monetary): Total commercial value of shipment.

### Shipment fields
- `operation_type` (Selection): Import, Export, Transit.
- `transport_mode` (Selection): Sea, Air, Road, Rail.
- `incoterm_id` (Many2one): Incoterm (`account.incoterms`).
- `origin_country_id` (Many2one): Country of Origin (`res.country`).
- `departure_country_id` (Many2one): Country of Departure (`res.country`).
- `destination_country_id` (Many2one): Country of Destination (`res.country`).
- `customs_office` (Char): Destination customs office name.
- `container_number` (Char): Shipping container reference.
- `booking_number` (Char): Carrier booking reference.
- `transport_document_number` (Char): Bill of Lading, AWB, CMR document number.

### Date fields
- `document_deadline` (Date): Document requirements deadline.
- `planned_departure_date` (Date): Expected departure.
- `actual_departure_date` (Date): Actual departure.
- `planned_arrival_date` (Date): Expected arrival (ETA).
- `actual_arrival_date` (Date): Actual arrival (ATA).
- `planned_clearance_date` (Date): Expected clearance date.
- `actual_clearance_date` (Date): Actual clearance date.
- `warehouse_delivery_date` (Date): Warehouse delivery date.

### Customs & laboratory fields
- `customs_declaration_number` (Char): Customs entry declaration number.
- `customs_declaration_date` (Date): Customs entry declaration date.
- `inspection_required` (Boolean): Inspection flag.
- `inspection_date` (Date): Inspection execution date.
- `laboratory_required` (Boolean): Lab analysis flag.
- `release_date` (Date): Official release date.

### Computed controls (stored)
- `document_total` (Integer): Total required documents.
- `document_approved_count` (Integer): Count of approved documents.
- `document_missing_count` (Integer): Count of missing documents.
- `document_rejected_count` (Integer): Count of rejected documents.
- `document_completion_percentage` (Float): Completion rate.
- `shipment_ready` (Boolean): Readiness flag.
- `blocking_document_count` (Integer): Count of blocking compliance issues.
- `blocking_reason_text` (Text): Human-readable list of blocking reasons.

---

## 2. `customs.operation.line` (Product Line)

Tracks batch and shipment line items.

- `operation_id` (Many2one): Parent Customs File (`customs.operation`, Cascade).
- `purchase_order_line_id` (Many2one): Linked Odoo PO line (`purchase.order.line`).
- `product_id` (Many2one): Product (`product.product`).
- `description` (Text): Product description.
- `customs_description` (Text): Customs compliance/declarative description.
- `hs_code` (Char): Harmonized System (HS / GTİP) code.
- `country_of_origin_id` (Many2one): Line origin country (`res.country`).
- `manufacturer_id` (Many2one): Manufacturer partner (`res.partner`).
- `manufacturer_approval_number` (Char): Facility registration approval code.
- `batch_number` (Char): Product batch reference.
- `production_date` (Date): Batch production date.
- `expiry_date` (Date): Batch expiry date.
- `quantity` (Float): Commercial quantity.
- `uom_id` (Many2one): Unit of Measure (`uom.uom`).
- `net_weight` (Float): Net weight in kg.
- `gross_weight` (Float): Gross weight in kg.
- `package_count` (Integer): Package count.
- `package_type` (Char): Package type description.
- `health_certificate_required` (Boolean): Special health cert requirement.
- `analysis_required` (Boolean): Quality cert/analysis requirement.
- `import_permit_required` (Boolean): Government import permit requirement.
- `notes` (Text): Line-level internal notes.
- `company_id` (Many2one): Related company.

---

## 3. `customs.document.type` (Document Type)

Master data document types.

- `name` (Char, Required): English document type name.
- `name_tr` (Char): Turkish translation label.
- `code` (Char, Required): Unique document type code (e.g. INV, COA, COO).
- `description` (Text): Details of the document type rules.
- `default_responsible_party` (Selection): Default party providing document.
- `default_requirement_level` (Selection): Mandatory, Optional.
- `original_normally_required` (Boolean): Flag for physical copy.
- `sequence` (Integer): Ordering sequence.
- `active` (Boolean): Active status.
- `company_id` (Many2one): Linked company (Null = Shared globally).

---

## 4. `customs.document.requirement` (Required Document)

The compliance document record.

- `operation_id` (Many2one, Required): Parent Customs File (`customs.operation`, Cascade).
- `operation_line_id` (Many2one): Linked product line (`customs.operation.line`).
- `document_type_id` (Many2one, Required): Base type (`customs.document.type`).
- `name` (Char, Required): Document requirement name.
- `state` (Selection): Draft, Under Review, Approved, Rejected, Expired, etc.
- `requirement_level` (Selection): Mandatory, Optional.
- `responsible_party` (Selection): Responsible supplier or internal party.
- `responsible_user_id` (Many2one): Internal staff responsible.
- `vendor_id` (Many2one): Vendor/Partner (`res.partner`) providing the document.
- `company_id` (Many2one): Related company.
- `is_blocking` (Boolean): True if this document blocks shipment departure.
- `is_overdue` (Boolean, Computed): Past deadline and incomplete.
- `is_expired` (Boolean, Computed): Past expiry date.
- `is_complete` (Boolean, Computed, Stored): Document is in approved/valid state.

### Dates
- `requested_date` (Date): Requested date.
- `deadline` (Date): Expected compliance date.
- `received_date` (Date): Copy receipt date.
- `issued_date` (Date): Document issuance date.
- `expiry_date` (Date): Document expiration date.
- `reviewed_date` (Date): Verification date.
- `reviewed_by` (Many2one): Verification employee.

### Original tracking
- `original_required` (Boolean): Is original required.
- `original_issued` (Boolean): Is original issued by issuer.
- `original_dispatched` (Boolean): Is original dispatched.
- `original_received` (Boolean): Is original received.
- `dispatch_date` (Date): Courier dispatch date.
- `courier_name` (Char): Courier firm name.
- `tracking_number` (Char): Courier tracking reference.

### Attachments & notes
- `attachment_ids` (Many2many): Attached files (`ir.attachment`).
- `version_number` (Integer): Increments automatically on attachment upload.
- `rejection_reason` (Text): Rejection/correction explanation.
- `review_notes` (Text): Internal notes.

---

## 5. Standard Odoo Model Extensions

The module extends the following standard Odoo models to implement synchronization:

### `purchase.order` (Purchase Orders)
- `customs_operation_ids` (Many2many): Related Customs Files.
- `customs_operation_count` (Integer, Computed): Number of linked Customs Files.
- `is_import_purchase` (Boolean): Checked if this is an import transaction.
- `customs_required` (Boolean): Checked if customs operations are required.
- `customs_operation_state` (Selection, Computed): Status state of linked Customs File.
- `customs_document_completion_percentage` (Float, Computed): Document completion % summary.
- `customs_shipment_ready` (Boolean, Computed): Summary shipment readiness state.
- `customs_blocking_reason_text` (Text, Computed): Summary of blockers.

### `purchase.order.line` (Purchase Order Lines)
- `customs_line_ids` (One2many): Back-link to Customs Operation Lines.

### `stock.picking` (Stock Receipts / Pickings)
- `customs_operation_ids` (Many2many): Linked Customs Files.
- `customs_state_summary` (Char, Computed): Text summary of linked Customs File stages (e.g. "Draft Received", "Cleared", "Blocked").

### `account.move` (Invoices & Vendor Bills)
- `customs_operation_id` (Many2one): Associated Customs File.

### `product.template` (Product Customs Profile)
- `customs_required` (Boolean): If checked, this product triggers customs tracking.
- `hs_code` (Char): Harmonized System / GTİP code default.
- `country_of_origin_id` (Many2one): Product default country of origin.
- `manufacturer_id` (Many2one): Default manufacturer partner.
- `health_certificate_required` (Boolean): Health certificate requirement flag.
- `analysis_required` (Boolean): COA requirement flag.
- `import_permit_required` (Boolean): Import Permit requirement flag.
- `original_documents_required` (Boolean): Physical original document required flag.
