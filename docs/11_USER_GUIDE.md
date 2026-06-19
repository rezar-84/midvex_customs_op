# Import & Customs Operations - User and Administration Manual

This manual details how to configure and use the **Import & Customs Operations** module, fully integrated with Odoo Purchase, Inventory, and Accounting.

---

## 1. Setup & Security Configuration (Administrator)

Before general users can access the application, an administrator must assign user access rights:

### User Role Assignment
1. Navigate to **Settings** > **Users & Companies** > **Users**.
2. Select the target user.
3. Locate the **Customs Operations** category in the access rights section:
   * **Customs User:** Can view/edit Customs Files, trigger manually from POs, sync lines, upload attachments, and view chatter.
   * **Customs Document Approver:** Inherits user rights and can approve, reject, or request corrections on document requirements.
   * **Customs Manager:** Inherits approver rights. Can override shipment readiness checks, close/cancel operations, archive files, and view financial/operational reporting.
   * **Customs Administrator:** Full configuration rights (can modify workflow stages and default document types).
4. *Note: Standard Odoo Purchase, Inventory, and Accounting security rights apply independently. A user must have access to Purchase or Accounting to view POs and Bills via the smart buttons.*
5. Save the user record and refresh the browser (**F5**).

---

## 2. Master Data & Configuration

### Configuring Workflow Stages
1. Navigate to **Import & Customs** > **Configuration** > **Stages**.
2. Create or edit a stage:
   * **Stage Name:** The displayed name of the stage (translatable).
   * **Sequence:** Integer representing order (smaller sequence appears first).
   * **Folded in Kanban:** Check this to collapse the stage column by default.
   * **Closed/Cancelled Stage:** Mark these flags to define terminal stages.
   * **Company:** Leave empty for global stages, or select a specific company to restrict it.

### Configuring Document Types
1. Navigate to **Import & Customs** > **Configuration** > **Document Types**.
2. Create a document type:
   * **Code:** Unique identifier (e.g., `COA`, `HC`, `COO`).
   * **Document Name:** Full English label.
   * **Turkish Name:** Translation label.
   * **Default Responsible Party:** Who normally provides this (Supplier, Broker, Forwarder, Carrier, Manufacturer, Internal).
   * **Default Requirement Level:** Mandatory (blocks shipment readiness) or Optional.
   * **Original Normally Required:** Check this if physical copies are legally required.

---

## 3. Product Customs Profiles (Manager / User)

To automate compliance document generation, you must configure product profiles:
1. Navigate to **Inventory** > **Products** > **Products** (or **Purchase** > **Products**).
2. Select the product template and click the **Import & Customs** tab.
3. Configure the settings:
   * **Customs Required (Boolean)**: Must be checked to trigger customs operations for this product.
   * **HS Code (Char)**: Harmonized Tariff code default.
   * **Country of Origin (Many2one)**: Default origin country.
   * **Manufacturer (Many2one)**: Default manufacturer partner.
   * **Health Certificate Required (Boolean)**: Triggers Health Certificate document requirement.
   * **Analysis Required (Boolean)**: Triggers Certificate of Analysis (COA) requirement.
   * **Import Permit Required (Boolean)**: Triggers Import Permit requirement.
   * **Original Documents Required (Boolean)**: Flags physical original requirements.

---

## 4. Creating & Syncing Import Operations from Purchase

The system provides automated and manual workflows to ensure purchase orders are linked to compliance files:

### Path A: Automatic Confirmation Flow
1. Navigate to **Purchase** and click **New** to create a Purchase Order.
2. Select an international vendor (vendor country different from the company country). This automatically sets **Is Import Purchase = True** and **Customs Required = True**.
3. Add products and click **Confirm Order**.
4. Odoo automatically creates one linked **Import & Customs Operation** (reference `CUS/YYYY/NNNN`).
5. The system automatically:
   * Syncs headers: vendor, incoterm, currency, company, expected receipt date, PO reference.
   * Syncs product lines: creates lines mapping products, quantities, UoMs, and default weights/HS codes.
   * Automatically generates standard document requirements (Commercial Invoice, Packing List, Bill of Lading, Certificate of Origin) and product-specific requirements based on product template compliance profiles.
   * Links generated Stock pickings (receipts) to the operation.

### Path B: Manual Action Button
1. If an operation was not auto-created, or if you need to force creation, open the PO.
2. Click the **Create Import Operation** button in the header.
3. If an operation is already linked, Odoo redirects you to the existing record (prevents duplicates).
4. If no operation is linked, Odoo creates, syncs lines/headers, and opens the new record.

### Syncing Line & Quantity Updates
If purchase order quantities or products change before the Customs File moves past the `Waiting for Documents` stage:
1. Open the Purchase Order or Customs File.
2. Click the **Sync Purchase Lines** button.
3. Odoo appends new lines and updates quantities. It *never* overwrites manually reviewed customs details (such as manually entered batch numbers or expiry dates) to protect data integrity.

---

## 5. Document Compliance Tracking (Customs User / Approver)

1. Open the Customs File form and click the **Documents** tab.
2. Default document requirements are already listed (auto-generated from product compliance profiles).
3. To upload a copy, click the line to open the form. Upload files using the attachment widget. Odoo automatically increments the **Version Number**.
4. **Approval Workflow (Approver/Manager Only):**
   * Change state using the form action buttons (e.g. **Mark Under Review**, **Approve**, **Reject**).
   * Transitioning to *Rejected* or *Correction Required* mandates filling in a **Rejection Reason**.
5. **Original Document Tracking:**
   * If an original is required, track states: *Original Issued*, *Original Dispatched*, *Original Received*.
   * Record dispatch date, courier name, and tracking number.

---

## 6. Stock Receipts (Inventory) & Warning Control

1. All incoming stock receipts (`stock.picking`) created from the PO are linked to the Customs File.
2. **Clearance Alert**: When validating a stock receipt, if the linked Customs Operation is not cleared (stage is before *Customs Cleared*):
   * Odoo logs a warning to the picking chatter: *"Goods are being received before Customs Operation is cleared."*
   * An automatic activity is assigned to the buyer.
3. **Strict Validation Control**: If the administration setting `customs_block_receipt_before_clearance` is enabled, Odoo raises a validation error blocking validation of stock receipts until the Customs File is cleared.

---

## 7. Accounting Linkage (Vendor Bills & Expenses)

1. **Vendor Bills**: All vendor bills (`account.move`) generated from the source Purchase Order are automatically linked to the Customs File.
2. **Customs Expense Bills**: When receiving separate invoices for customs expenses (e.g., broker fees, freight, duty):
   * Open the Vendor Bill and link it to the **Customs File** relation field.
3. Navigate the financial flows using the **Vendor Bills** smart button on the Customs File.

---

## 8. Closing the File (Customs Manager)

1. Once warehouse delivery is validated and all vendor bills/costs are linked, move the stage to **Closed**.
2. **Closing Validations**:
   * Odoo raises blocking errors if mandatory documents are incomplete or if open critical activities remain.
   * Logs warnings in chatter if customs declarations or delivery dates are missing, preserving operational flexibility.
