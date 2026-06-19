# Security and Access Specification

## 1. Groups

### Customs User
- Can create and edit Customs Files.
- Can manually link POs, receipts, and bills.
- Can upload document attachments.
- Cannot approve/reject compliance documents.
- Cannot configure stages or document types.
- Cannot override blocking readiness controls.

### Customs Document Approver
- Inherits Customs User.
- Can mark document requirements under review, approved, or rejected/correction required.
- Cannot override shipment readiness controls.

### Customs Manager
- Inherits Customs Document Approver.
- Can close and cancel Customs Files.
- Can override shipment readiness blocking with a required override reason.
- Can view operational and financial reporting.

### Customs Administrator
- Inherits Customs Manager.
- Can configure stages, document types, and default requirements templates.

---

## 2. Multi-Company Security Rules

All operational models and their relations must behave correctly in multi-company environments:
- **`customs.operation`**: Record rule `[('company_id', 'in', company_ids)]` ensures users only see files for active/allowed companies.
- **`customs.document.requirement`**: Relies on related `company_id` to enforce same-company rules.
- **`customs.stage` & `customs.document.type`**: Support company-specific records (enforced via rules) or global share (`company_id = False`).

---

## 3. Integration Consistency & Integrity Rules

We must enforce security checks in python constraints (server-side) to ensure data integrity:
- **Company Consistency**:
  - Linked Purchase Orders (`purchase_order_ids`) must belong to the same `company_id` as the Customs Operation.
  - Linked Stock Pickings (`picking_ids`) must belong to the same `company_id` as the Customs Operation.
  - Linked Vendor Bills (`invoice_ids`) must belong to the same `company_id` as the Customs Operation.
  - Selected Suppliers, Broker, Forwarder, and Carrier partners must have consistent `company_id` settings (either matching the operation's company or set to global `False`).
- **Standard Group Controls**:
  - Creating or linking a Customs Operation does not bypass standard Odoo security. If a user does not have read access to Odoo Purchase or Accounting, they cannot view linked POs or Bills via smart buttons (standard Access Error is raised).
  - Standalone and hook operations must not use broad `sudo()` bypasses. Any retrieval of Odoo receipts or bills must run under the user's context.
