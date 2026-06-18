# Customs Operations - User and Administration Manual

This manual details how to configure and use the **Customs Operations** module in Odoo 19.

---

## 1. Setup & Security Configuration (Administrator)

Before general users can access the application, an administrator must assign user access rights:

### User Role Assignment
1. Navigate to **Settings** > **Users & Companies** > **Users**.
2. Select the target user.
3. Locate the **Customs Operations** category in the access rights section:
   * **Customs User:** Can create and edit Customs Files, upload attachments, and log chatter messages.
   * **Customs Document Approver:** Inherits user rights and can approve, reject, or request corrections on documents.
   * **Customs Manager:** Inherits approver rights and can override readiness checks or close Customs Files.
   * **Customs Administrator:** Full configuration rights (can modify workflow stages and document types).
4. Save the user record and refresh the browser (**F5**).

---

## 2. Master Data Configuration (Administrator / Manager)

### Configuring Workflow Stages
Customs Files move through a sequence of stages. To view or add stages:
1. Navigate to **Customs Operations** > **Configuration** > **Stages**.
2. Create or edit a stage:
   * **Stage Name:** The displayed name of the stage (translatable).
   * **Sequence:** Integer representing order (smaller sequence appears first).
   * **Folded in Kanban:** Check this to collapse the stage column by default.
   * **Closed/Cancelled Stage:** Mark these flags to define terminal stages for files.
   * **Company:** Leave empty for global stages, or select a specific company to restrict it.

### Configuring Document Types
Document types define the category of files required for compliance:
1. Navigate to **Customs Operations** > **Configuration** > **Document Types**.
2. Create a new document type:
   * **Code:** Short identifier (e.g., `COA`, `HC`, `COO`). Must be unique.
   * **Document Name:** Full English label.
   * **Turkish Name:** Translation label.
   * **Default Responsible Party:** Who normally provides this document (e.g., Supplier, Broker).
   * **Default Requirement Level:** Mandatory (blocks shipment if missing) or Optional.
   * **Original Normally Required:** Check this if physical copies are legally required.

---

## 3. Creating & Managing Customs Files (Customs User)

### Step 1: Create a Customs File
1. Go to **Customs Operations** > **Operations** > **All Customs Files** and click **New**.
2. The reference number is set to `New` and will automatically generate as `CUS/YYYY/NNNN` (e.g., `CUS/2026/0001`) on first save.
3. Assign the **Responsible Employee** (defaults to the current user) and the **Priority**.

### Step 2: Set Up Related Parties & Integrations
1. Under the **Overview** tab:
   * Select one or more **Suppliers** (vendor selection is restricted to related parties on save).
   * Choose the **Customs Broker**, **Freight Forwarder**, and **Carrier**.
   * Link the corresponding **Purchase Orders** and **Incoming Shipments (Stock Receipts)**.

### Step 3: Add Product Lines
1. Go to the **Product Lines** tab and click **Add a line**.
2. Select the **Product** (HS code and unit of measure will auto-populate).
3. Fill in:
   * **Quantity**, **Net Weight (kg)**, and **Gross Weight (kg)** (validation prevents negative weights or net exceeding gross).
   * **Batch Number**, **Production Date**, and **Expiry Date** (validation prevents expiry before production).
   * Facility approval details and notes.
4. *Note: Product lines become read-only and locked once the Customs File moves to the "Document Review" stage or later to preserve data stability.*

---

## 4. Compliance Document Tracking (Customs User / Approver)

### Step 1: Create Document Requirements
1. Go to the **Required Documents** tab or click the **Required Docs** smart button in the header.
2. Add a line:
   * Select the **Document Type**.
   * Set **Blocking Requirement** to `True` if this document is critical for shipment readiness.
   * Save the file.

### Step 2: Upload and Review
1. To upload a document, click the line to open the **Document Requirement** form.
2. Use Odoo's standard attachment widget to upload draft or copy files. The system automatically increments the **Version Number** when attachments change.
3. Update the **Status**:
   * **Requested / Vendor Preparing:** Under preparation by the supplier.
   * **Draft Received:** Copy uploaded, waiting for verification.
   * **Under Review:** Mark this when starting verification.
4. **Approval / Rejection (Approver Only):**
   * **Approved / Accepted:** The copy is valid (counts towards completion percentage).
   * **Correction Required / Rejected:** Enter a rejection reason in the notes and set the status.

---

## 5. Shipment & Customs Entry (Logistics / Manager)

1. Under the **Shipment Details** tab, record departure/arrival countries, planned/actual transportation dates, container numbers, and transport document references (e.g. Bill of Lading).
2. Under **Customs & Laboratory**, record:
   * **Customs Declaration Number** & **Declaration Date**.
   * Inspection or laboratory status details and dates.
   * **Customs Release Date** and **Warehouse Delivery Date**.

---

## 6. Closing the File (Customs Manager)

1. Once the shipment has been delivered to the warehouse, move the stage to **Closed**.
2. **Closing Validation:**
   * If mandatory documents are incomplete or critical activities remain open, Odoo will raise blocking errors.
   * If customs entry numbers or actual dates are missing, warnings will be posted to the chatter to remind the team, though closing is not database-blocked to maintain operational flexibility.
