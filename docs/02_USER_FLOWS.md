# User Flows

## 1. Purchase Order Confirmation & Customs File Creation

### Path A: Automatic Creation
1. Purchasing employee creates an import Purchase Order (PO).
2. The user confirms the PO.
3. Odoo automatically checks creation rules (vendor country, is_import_purchase flag, or product template settings).
4. If eligible, Odoo creates a Customs File:
   * Assigns a unique reference (`CUS/YYYY/NNNN`).
   * Automatically copies header information: vendor, company, currency, incoterm, expected arrival.
   * Automatically imports PO lines as Customs Operation Lines (mapping products, quantities, UoMs, HS codes, weights).
   * Automatically links all generated stock receipts (incoming pickings) to the Customs File.
   * Triggers the Document Requirement Template Engine, auto-generating required documents (Commercial Invoice, Packing List, Certificate of Origin, and product-specific certificates like COAs or Health Certificates based on product customs profiles).
5. Odoo records the auto-creation in the PO chatter.

### Path B: Manual Creation / Trigger
1. Purchasing employee views a draft or confirmed PO.
2. The user clicks **Create Import Operation**.
3. Odoo checks if a Customs File already exists.
   * If yes: Opens the existing Customs File (prevents duplication).
   * If no: Creates a new Customs File, syncs all headers and lines, and opens the new record.

## 2. Add and request documents

1. User opens the Customs File's **Documents** tab or clicks the smart button.
2. Odoo has already generated default document records based on the product customs profiles.
3. User adds any additional required document records.
4. User assigns deadlines, vendors, and responsible employees.
5. User marks documents as requested.
6. Chatter logs the request status and date.
7. Odoo schedules follow-up activities.

## 3. Receive and review a document

1. User uploads one or more attachments.
2. Document status changes to **Draft Received**, and Odoo automatically increments the document version number.
3. Approver marks the document as **Under Review**.
4. Approver reviews and either:
   * Approves it (marks as **Approved** / **Accepted**).
   * Requests correction or rejects it (requires a rejection reason, logged in the notes).
5. Chatter records the action, approver name, and timestamp.

## 4. Track original documents

1. User flags whether a physical original document is required.
2. When original is issued by the supplier, user records the issue date.
3. When dispatched, user records the courier name, tracking number, and dispatch date.
4. When physical copy is received, user marks it as received.
5. Odoo recalculates shipment readiness using the original document status.

## 5. Approve shipment readiness

1. Odoo dynamically calculates shipment readiness.
2. If blocking requirements are missing, expired, or rejected, readiness remains blocked.
3. Odoo displays human-readable blocking reasons directly on the form.
4. Once all compliance rules are met, readiness becomes `True` automatically.
5. Managers may bypass blocking with a mandatory override reason, which is permanently logged in chatter.

## 6. Track departure, arrival, and inventory sync

1. Logistics records departure country, destination country, transport mode, and planned dates.
2. Operation stage transitions to **Shipped** upon departure.
3. Operation stage transitions to **Arrived** upon planned or actual arrival.
4. Odoo keeps the linked stock pickings synchronized with the Customs File (visible from stock receipts).
5. **Warning Control on Receipt:** If warehouse staff attempts to receive an incoming picking whose Customs Operation is not cleared, Odoo shows a warning or log in chatter stating: *"Goods are being received before Customs Operation is cleared."*
6. Once cleared and received, Odoo updates the actual warehouse delivery date.

## 7. Customs clearance & final costs

1. Customs declaration number, date, and customs release date are recorded.
2. If inspections or laboratory analyses are required, progress and dates are logged.
3. **Billing Integration:** When vendor bills are generated from the PO, they are automatically linked to the Customs File.
4. User manually associates customs-related expense bills (freight invoices, broker fees, taxes).
5. Manager reviews final compliance, documents, and costs.
6. Manager moves the Customs File to the **Closed** stage.
