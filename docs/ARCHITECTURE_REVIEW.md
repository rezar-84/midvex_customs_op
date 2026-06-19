# Architecture Review - midvex_customs_op

This document reviews the data architecture of the **Import & Customs Operations** module, analyzing the core and extended models in Odoo 19.

---

## 1. Core Models

### A. customs.operation (Customs File)
* **Current Purpose**: Represents the master operational file for an import shipment, tracking parties, shipment logistics, dates, costs, warehouse receiving details, and overall compliance readiness.
* **Key Fields**:
  * `name` (Char): Reference sequence (e.g. CUS/YYYY/NNNN).
  * `stage_id` (Many2one -> customs.stage): Current workflow stage.
  * `supplier_ids` (Many2many -> res.partner): Foreign suppliers/vendors.
  * `broker_id` (Many2one -> res.partner): Assigned Customs Broker.
  * `transport_mode` (Selection): sea, air, road, rail.
  * `bl_number` / `container_number` / `seal_number` (Char): Shipping carrier tracking IDs.
  * `cost_total` (Monetary, Computed, Stored): Sum of freight, taxes, broker, storage, etc.
  * `shipment_ready` (Boolean, Computed, Stored): Overall readiness checking required and original documents.
  * `warehouse_received` (Boolean): Goods received in inventory.
  * `is_sample_data` (Boolean): Identifies mock operations.
* **Relationships**:
  * One2many -> `customs.operation.line` (Product Lines)
  * One2many -> `customs.document.requirement` (Document Requirements)
  * Many2many -> `purchase.order` (Linked purchase orders)
  * Many2many -> `stock.picking` (Linked warehouse receipts)
  * One2many -> `account.move` (Linked vendor bills & expenses)
* **Current Business Flow**: Initialized automatically from confirmed POs or manually. Product lines are synced, and default documents are generated. During transit and customs stages, quality reviews documents. Warehouse logs delivery, and accounting enters final costs.
* **Missing Capabilities**: 
  * Support for splitting one PO into multiple customs files (partial shipments).
  * Auto-recalculation of costs based on actual linked Vendor Bills instead of static manual entries.
  * Dynamic currency exchange rate locking.

### B. customs.operation.line (Customs Product Line)
* **Current Purpose**: Details the product batches, weights, packaging details, and specific regulatory flags (e.g. health certificate, COA requirements) for items in a shipment.
* **Key Fields**:
  * `product_id` (Many2one -> product.product): Synced import item.
  * `hs_code` (Char): Harmonized System/GTİP code.
  * `net_weight` / `gross_weight` (Float): Net & gross weights in kg.
  * `package_count` / `package_type` (Integer/Char): Box/bag details.
  * `batch_number` / `production_date` / `expiry_date` (Char/Date): Batch tracking.
  * `health_certificate_required` / `analysis_required` (Boolean): Profile requirements flags.
* **Relationships**:
  * Many2one -> `customs.operation` (Master Customs File, cascade deleted)
  * Many2one -> `purchase.order.line` (Linked PO line)
* **Current Business Flow**: Created automatically during PO sync. Once the operation transitions past "Waiting for Documents" stage, product lines are locked against user modifications or unlinks.
* **Missing Capabilities**:
  * Automatic generation of Odoo Inventory tracking Lots directly from the line batch inputs.
  * Weight reconciliation checks against shipping carrier declarations.

### C. customs.document.requirement (Customs Document Requirement)
* **Current Purpose**: Manages individual document compliance tracking, version history, attachments, courier tracking, and verification status.
* **Key Fields**:
  * `document_type_id` (Many2one -> customs.document.type): e.g. Commercial Invoice, COA.
  * `state` (Selection): draft_received, under_review, correction_required, approved, rejected, expired, etc.
  * `responsible_party` (Selection): supplier, broker, forwarder, carrier, manufacturer, internal.
  * `original_required` / `original_received` (Boolean): Controls physical document status.
  * `rejection_reason` (Text): Log of corrections needed.
  * `version_number` (Integer): Auto-incremented on attachment changes.
* **Relationships**:
  * Many2one -> `customs.operation` (Linked Customs File)
  * Many2one -> `customs.operation.line` (Optional link for product-specific certificates like COAs)
  * Many2many -> `ir.attachment` (Uploaded PDF/images)
* **Current Business Flow**: Quality / Approvers review uploads. Rejections lock actions until correction is resolved. Physical courier deliveries are logged.
* **Missing Capabilities**:
  * Expiry warning triggers in Odoo notifications/emails before certificate expiration.
  * PDF watermarking or stamp overlay indicating approval.

### D. customs.document.type (Customs Document Type)
* **Current Purpose**: Master metadata configuration for documents (e.g. Health Certificate, Invoice), controlling their defaults (responsibility, mandatory levels, original requirements).
* **Key Fields**:
  * `code` (Char): Unique lookup code (e.g. INV, COA).
  * `default_responsible_party` / `default_requirement_level` (Selection): Standard compliance levels.
  * `original_normally_required` (Boolean): Flag for original hardcopies.
* **Relationships**:
  * Many2one -> `res.company` (Allows company-scoped definitions).
* **Current Business Flow**: Setup by Administrators. Used to instantiate standard requirements when an Import Operation is initialized.
* **Missing Capabilities**:
  * Country-of-origin rules (e.g., automatically require Phytosanitary Certificate only if origin country is outside the EU).

### E. customs.stage (Customs File Stage)
* **Current Purpose**: Configures the linear workflow stages for Import Operations, supporting kanban visual tracking, company scopes, and closed/cancelled properties.
* **Key Fields**:
  * `code` (Char): Stage code for translation-safe search filters.
  * `sequence` (Integer): Defines linear ordering.
  * `fold` / `is_closed` / `is_cancelled` (Boolean): Controls card views and final close rules.
* **Current Business Flow**: Configured by Admins. Users move files sequentially. Managers can override rules.
* **Missing Capabilities**:
  * Automated stage transitions based on business events (e.g., transition to "Shipped" automatically when actual departure date is filled).

---

## 2. Extended Models

### A. purchase.order
* **Current Purpose**: Extended to auto-trigger Customs Operations on confirm, sync lines, and track customs summaries.
* **Key Fields**:
  * `is_import_purchase` (Boolean): Set if vendor country differs from company.
  * `customs_required` (Boolean): Set if import purchase or has customs-flagged products.
  * `customs_operation_ids` (Many2many): Linked Customs Files.
* **Relationships**:
  * Many2many -> `customs.operation`
* **Current Business Flow**: Standard PO confirmation triggers `_create_customs_operation_from_po()` if import rules apply.
* **Missing Capabilities**:
  * Handling PO revisions (prices/qty changes) when the Customs File is locked.
  * Splitting lines into multiple shipments.

### B. purchase.order.line
* **Current Purpose**: Feeds product compliance flags and synchronizes quantity/product changes to linked operation lines.
* **Current Business Flow**: Creation and edits propagate to open customs operation lines. Locked stages block edits.
* **Missing Capabilities**:
  * Tracking sync exclusions (e.g., sample lines/marketing materials that do not go through customs).

### C. stock.picking (Warehouse Receipt)
* **Current Purpose**: Intercepts receipt validation to ensure the linked customs clearance is complete before inventory storage.
* **Key Fields**:
  * `customs_not_cleared` (Boolean): Indicates linked operations are uncleared.
* **Current Business Flow**: `button_validate` blocks validation or prints warnings based on `customs_block_receipt_before_clearance` setting.
* **Missing Capabilities**:
  * Container-level receipt checks (e.g. block picking lines matching specific containers).

### D. account.move (Vendor Bill)
* **Current Purpose**: Links supplier invoices and freight/broker bills directly to Customs Files.
* **Current Business Flow**: Scans lines on bill creation and auto-populates `customs_operation_id` if linked to active PO operations.
* **Missing Capabilities**:
  * Apportioning bill line values to `stock.landed.cost` records automatically.

### E. product.template (Product Customs Profile)
* **Current Purpose**: Stores master customs profiles (GTİP/HS code, country of origin, required documents flags).
* **Key Fields**:
  * `hs_code` / `country_of_origin_id` / `manufacturer_id`
  * `health_certificate_required` / `analysis_required` / `import_permit_required` / `original_documents_required`
* **Current Business Flow**: Setup by Purchasing/Compliance. Propagates values to purchase lines and customs operations.
* **Missing Capabilities**:
  * Manufacturer compliance certificate attachments directly on the product template.

### F. sale.order (Sales Order - Traced)
* **Current Purpose**: Traces client orders linked to import shipments.
* **Current Business Flow**: Traced via MTO inventory routes or PO name parsing.
* **Missing Capabilities**:
  * Exposing shipment ETA dates directly on Sales Order views for sales team visibility.
