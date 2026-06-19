# Test Plan

## 1. Automated Test Categories

### Installation & Upgrade
- **Clean Install**: Install the module on a clean database and verify standard data loads.
- **Data Upgrade**: Verify upgrading works on a database containing pre-existing Customs Files and lines without data loss.

### Model Integration & Sync Tests
- **PO Confirm Trigger (Auto-Creation)**:
  - Confirm a PO with a vendor from a different country -> Verify a `customs.operation` is auto-created.
  - Confirm a PO with `customs_required = True` -> Verify operation is auto-created.
  - Confirm a PO with a local vendor and no flags -> Verify NO operation is created.
- **Duplicate Prevention**:
  - Run manual "Create Import Operation" twice on a PO -> Verify only one operation exists, and second call returns/redirects to the existing record.
- **Header & Lines Sync**:
  - Verify Vendor, Currency, Incoterm, and Total sync to the operation.
  - Verify PO product lines create `customs.operation.line` linked to `purchase.order.line`.
  - Verify PO note and section lines are ignored.
  - **Line Sync Button**: Edit a PO line quantity, add a line, and trigger "Sync Purchase Lines" -> Verify quantities update, new line appends, and manual fields on original lines remain unchanged.
- **Stock Receipt Link & Warnings**:
  - Confirm PO -> Verify generated stock pickings are linked to the operation.
  - Validate picking while operation is uncleared -> Verify a warning/chatter note is logged.
  - Validate picking with strict mode enabled -> Verify ValidationError blocks validation before clearance.
- **Vendor Bills Link**:
  - Create a bill from a linked PO -> Verify the bill is automatically linked to the Customs Operation.
- **Product Customs Profile Defaults**:
  - Set compliance flags on a product template -> Verify creating a Customs File from a PO containing this product automatically creates document requirements (COA, HC, or Import Permit).
- **Company Integrity (Constraints)**:
  - Attempt to link a PO or stock picking from Company B to a Customs Operation of Company A -> Verify a ValidationError blocks the save.

### Security & Access Control Tests
- **Permissions**: Verify that a Customs User can trigger creation, but only Approvers/Managers can approve documents or override readiness.
- **Record Rules**: Confirm multi-company record rules isolate operations, documents, stages, and standard linked records between Company A and Company B.
- **Bypass Check**: Confirm a user without Odoo Purchase privileges cannot read purchase records via the customs interfaces.

---

## 2. Manual Scenarios to Validate

### Scenario 1: Integrated Salmon Egg Import (Strict Mode)
1. Set up a salmon product template with HS code, origin = Norway, and health certificate + import permit required.
2. Create an import PO from a Norwegian supplier.
3. Confirm PO.
4. Verify Customs File is automatically created, product lines imported, and document requirements (Commercial Invoice, Packing List, Certificate of Origin, Health Certificate, and Import Permit) are generated.
5. Verify incoming stock receipt is linked.
6. Validate the stock receipt -> Verify strict mode prevents validation because the operation is in "Waiting for Documents" stage.
7. Approve document requirements, transition Customs File to "Customs Cleared", and validate receipt -> Verify it now succeeds.

### Scenario 2: Standard Chlorella Import & Expenses Sync
1. Create a PO from a Japanese vendor.
2. Manually click "Create Import Operation" from PO draft.
3. Confirm the PO. Verify no duplicate operation is created.
4. Upload documents, review, and approve.
5. Create a vendor bill for the Japanese vendor from the PO -> Verify it links to the Customs File.
6. Create an expense vendor bill for freight costs and manually link it -> Verify it is visible from the Customs File smart buttons.

---

## 3. Regression Checks
- Standard Odoo Purchase Order confirmation flows (domestic/local) are not altered.
- Stock picking receipts from local vendors process normally without warnings.
- Multi-company database configurations continue to isolate documents.
