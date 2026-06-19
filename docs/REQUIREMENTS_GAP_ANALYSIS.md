# Requirements Gap Analysis - midvex_customs_op

This document compares the current `midvex_customs_op` implementation against the operational requirements, detailing existing capabilities, gaps, and missing features.

---

## 1. Purchase Integration

### A. Existing Capabilities
* **Customs Smart Button**: Linked POs and Customs Operations are connected via M2M relationship with navigating smart buttons on both forms.
* **Auto-creation from PO**: confirming a PO automatically instantiates a Customs File if import rules are met.
* **Import Purchase Detection**: Automatically flags `is_import_purchase` as `True` if the partner's country differs from the company's country.
* **Product Line Synchronization**: Automatically imports PO lines (product, description, quantities, and compliance settings) to operation lines. It also propagates changes (quantities, updates, deletions) before the file lock stage.
* **Duplicate Prevention**: Redirection actions prevent creating multiple duplicate operations for the same purchase order when running manual generation checks.

### B. Gap Analysis & Missing Features
* **Split Shipment Support (G-P01)**: If a PO is split across multiple vessels or departure times, the system cannot distribute PO lines or quantities across multiple distinct Customs Files.
* **Multiple Customs Files per PO (G-P02)**: The data relationship allows multiple files (Many2many relation), but the python auto-creation and quantity sync engines assume a strictly 1-to-1 linkage, causing synchronization issues if a single PO line is shared or split.
* **PO Revision Handling (G-P03)**: If a PO is revised (e.g. quantities changed) after the customs file has moved past the "Waiting for Documents" stage, the sync blocks updates (ValidationError) rather than creating an audit trail or prompting review.
* **Supplier Confirmation Workflow (G-P04)**: No formal "Supplier Confirmed" tracking date or status exists between PO validation and Production.
* **Purchase Readiness Indicators (G-P05)**: No summary KPIs indicating if a PO is ready to be loaded at the origin port based on initial documents.

---

## 2. Inventory Integration

### A. Existing Capabilities
* **Picking Linkage**: Stock pickings (receipts) are linked to Customs Files automatically via the purchase order connection.
* **Receipt Linkage**: Warehouse staff can see linked Customs Files and statuses directly on the picking form.
* **Customs Clearance Warnings**: Stock picking validation checks if linked customs files are released/cleared. If strict settings are enabled, it blocks validation; otherwise, it logs a warning in the chatter.

### B. Gap Analysis & Missing Features
* **Partial Receipt Handling (G-I01)**: If a receipt is validated partially (backorders generated), the system does not dynamically link or track the backorders separately on the Customs File.
* **Container-level Receiving (G-I02)**: No ability to receive products by containers (e.g., validating only items belonging to Container A while keeping Container B pending).
* **Lot Tracking Integration (G-I03)**: Although lines track batch numbers, production dates, and expiry dates, this information is not pushed automatically to create standard Odoo inventory Lot records during stock receipt validation.
* **Damaged Inventory Workflows (G-I04)**: Damaged flag triggers notifications but does not automatically route damaged items to a distinct quality inspection location or quarantined inventory warehouse.

---

## 3. Accounting Integration

### A. Existing Capabilities
* **Vendor Bill Linkage**: Automatically connects vendor bills generated from purchase orders to the linked Customs Operation. It also enables manual lookup and linkage of external service invoices.
* **Customs Cost Tracking**: Simple manual monetary fields log freight, taxes, stamps, storage, and agent fees on the customs form.

### B. Gap Analysis & Missing Features
* **Landed Cost Integration (G-A01)**: The module tracks costs manually as floating-point fields on `customs.operation`, but it does not link to Odoo's native `stock.landed.cost` module to capitalize these costs into product unit costs.
* **Cost Allocation Rules (G-A02)**: No automatic cost distribution calculation (e.g. allocating freight costs based on weight or customs tax based on product value).
* **Multi-Currency & Exchange Rates (G-A03)**: Custom costs assume the master currency of the operation. There is no multi-currency breakdown (e.g. freight in USD, custom tax in TRY, storage in EUR) or exchange-rate date locking.
* **Customs Tax Reporting (G-A04)**: No dedicated accounting analysis reports comparing actual VAT/duties paid to customs against estimated costs.

---

## 4. Sales Integration

### A. Existing Capabilities
* **Sales Tracing**: Traces original client orders (`sale.order`) linked to the imported purchase orders via origin string parsing and stock move destination chains.
* **MTO Linkage**: MTO-procured goods show sales references in the Overview tab.

### B. Gap Analysis & Missing Features
* **Customer Order Visibility (G-S01)**: Sales teams cannot view active import file timelines directly from the Sales Order screen.
* **ETA Exposure (G-S02)**: ETA and shipment delays do not propagate back to the Sales Order or calculate dynamic commitment dates for clients.

---

## 5. Compliance & Documents

### A. Existing Capabilities
* **Approval Workflow**: Linear document status transitions (draft_received -> under_review -> approved / correction_required -> accepted).
* **Original Tracking**: Separates digital scans from physical hardcopies with courier details.
* **Versioning**: Auto-increments requirement `version_number` when attachments are added or updated.
* **Rejection Process**: Enforces entering a validation reason when marking records as rejected or correction required.

### B. Gap Analysis & Missing Features
* **Document Templates (G-C01)**: No standard templates or checklists for different categories of documents.
* **Auto-generation Rules (G-C02)**: Document requirements are hard-coded in python (`INV`, `PKL`, `COO`, `BL` plus product certifications). There is no configuration UI for administrators to define conditional document requirement rules.
* **Country/Product-Specific Rules (G-C03)**: Cannot define document requirements based on origin country rules or customer-specific compliance certificates.
* **Expiry Monitoring (G-C04)**: No active monitoring or scheduled alerts for document expiry; expired documents only show warnings during readiness checks.

---

## 6. Operational Workflow Coverage

The core operational steps map to stages as follows:

| Step | UI / Stage Representation | Reporting Capability | Gaps Identified |
|---|---|---|---|
| **Purchase** | Draft / Confirmed PO | PO reporting | None |
| **Production** | Stage: Draft (Production status) | Manual tracking | No production delay alerts |
| **Ready** | Stage: Waiting for Documents | Stats counters | No supplier readiness dashboard |
| **Loaded** | Production status: Loaded | Date tracking | None |
| **Shipped** | Stage: Shipped / In Transit | Calendar / ETA | No real-time carrier tracking |
| **Customs** | Stage: Customs Clearance | Pivot / Graph | No sub-status reporting |
| **Warehouse** | Stage: Warehouse Handover / Delivered | Damage descriptions | No lot link |
| **Accounting** | Accounting Closing Status | Manual entry | No landed cost generation |
| **Closed** | Stage: Closed | Operations pivot | None |
