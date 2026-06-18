# Product Requirements Document

## Odoo Customs Operations

## 1. Product summary

*Customs Operations is an Odoo 19 application for managing international shipments, required customs documents, vendor follow-up, customs-clearance progress, original document delivery, inspections, approvals, and warehouse handover.*

It provides a single source of truth for import operations that are currently coordinated through WhatsApp, email, and manually stored files.

## 2. Primary users

### Purchasing employee

Needs to:

- Link purchase orders
- Identify required supplier documents
- Request missing documents
- Follow supplier deadlines
- Request corrections

### Logistics employee

Needs to:

- Track departure and arrival
- Track transport documents
- Track containers
- Track original documents
- Follow customs and warehouse delivery

### Quality or regulatory approver

Needs to:

- Review COA
- Review health certificates
- Approve or reject documents
- Record correction reasons
- Verify batch and product information

### Customs manager

Needs to:

- See all open customs files
- Identify blocked shipments
- Review delays
- Override controls when justified
- Close customs operations

### System administrator

Needs to:

- Configure document types
- Configure stages
- Manage security
- Maintain master data

## 3. User problems

Users currently cannot easily answer:

- Which documents are required for this shipment?
- Which documents are still missing?
- Has the supplier sent a draft?
- Has the document been approved?
- Was the original issued?
- Was the original dispatched?
- Where is the original document?
- Is the shipment ready to depart?
- Why is shipment readiness blocked?
- Has the customs declaration been opened?
- Is the shipment waiting for laboratory results?
- Who is responsible for the next action?
- Which deadline is overdue?
- Which supplier causes repeated document delays?

## 4. Product goals

- Centralize customs records
- Reduce reliance on WhatsApp
- Prevent shipments leaving with missing documents
- Track scanned and original documents separately
- Improve supplier accountability
- Improve internal responsibility
- Create an audit trail
- Reduce customs delays
- Enable reporting

## 5. Non-goals for MVP

The MVP will not include:

- Full customs authority integration
- Government API integration
- Automated courier tracking
- Supplier portal
- Customs broker portal
- WhatsApp message synchronization
- OCR document validation
- AI certificate validation
- Full landed-cost allocation
- Automatic tax calculation

These may be added later.

## 6. Core entities

### Customs File

One customs file represents one physical or operational shipment.

It may include:

- One purchase order
- Multiple purchase orders
- One supplier
- Multiple suppliers
- One or more products
- Multiple batches
- One or more stock receipts

### Customs Document Requirement

A structured required-document record.

It is not only an attachment.

It tracks:

- Requirement
- Responsibility
- Deadline
- Attachment
- Review
- Approval
- Rejection
- Original document status
- Courier tracking
- Final customs acceptance

## 7. Core user flow

1. User creates Customs File
2. User links purchase orders
3. User adds or imports product lines
4. User adds required documents
5. User requests documents from suppliers
6. Supplier files are uploaded
7. Internal user reviews documents
8. Document is approved or correction is requested
9. Original document status is tracked
10. Shipment readiness is calculated
11. Shipment departs
12. Shipment arrives
13. Customs declaration is recorded
14. Inspection or laboratory status is tracked
15. Customs release is recorded
16. Warehouse delivery is recorded
17. Customs File is closed

## 8. Functional requirements

### FR-001 Customs File creation

The system must generate a unique Customs File reference.

Format:

`CUS/YYYY/NNNN`

### FR-002 Purchase order relationship

Users must be able to link one or more purchase orders.

### FR-003 Incoming picking relationship

Users must be able to link one or more incoming stock pickings.

### FR-004 Product lines

Users must be able to add shipment product lines.

### FR-005 Document requirements

Users must be able to create document requirements linked to:

- Entire shipment
- Specific product line
- Supplier
- Internal responsible user

### FR-006 Attachments

Users must be able to upload one or more attachments to a document requirement.

### FR-007 Document review

Authorized users must be able to:

- Mark under review
- Approve
- Reject
- Request correction

### FR-008 Rejection reason

Rejection or correction must require a reason.

### FR-009 Original documents

The system must track:

- Original required
- Original issued
- Original dispatched
- Original received
- Courier
- Tracking number
- Dispatch date

### FR-010 Shipment readiness

The system must calculate whether a shipment is ready.

### FR-011 Blocking reasons

The system must provide readable blocking reasons.

### FR-012 Chatter

Important changes must be visible in chatter.

### FR-013 Activities

Users must be able to schedule activities.

### FR-014 Deadlines

Document requirements must support deadlines.

### FR-015 Overdue status

The system must identify overdue document requirements.

### FR-016 Expiry

The system must identify expired documents.

### FR-017 Stage management

Users must be able to move Customs Files through operational stages.

### FR-018 Manager override

Managers may override readiness blocking only with a reason.

### FR-019 Reporting

Users must be able to analyze:

- Open customs files
- Stage
- Supplier
- Customs broker
- Responsible employee
- Missing documents
- Rejected documents
- Document deadlines
- Planned arrival
- Actual clearance

## 9. Non-functional requirements

### NFR-001 Security

Users must only access records allowed by their groups and companies.

### NFR-002 Auditability

Important actions must be traceable.

### NFR-003 Performance

List and kanban views should remain responsive for at least 10,000 Customs Files and 100,000 document requirements.

### NFR-004 Maintainability

The module must follow standard Odoo architecture.

### NFR-005 Upgrade safety

The module must avoid modifications to Odoo core.

### NFR-006 Multi-company

All operational and configuration records must behave correctly in multi-company environments.

### NFR-007 Translation

All user-facing strings must be translatable.

### NFR-008 Accessibility

Status must not depend only on color.

## 10. Success metrics

The first release is successful when:

- All active import shipments are entered into Odoo
- Users can identify missing documents without searching WhatsApp
- All document approvals are recorded in Odoo
- Shipment readiness is visible
- Original documents are traceable
- Customs managers can identify blocked shipments
- The system prevents accidental shipment readiness when mandatory documents are incomplete

## 11. Future roadmap

Phase 2:

- Document requirement templates
- Automatic requirement generation
- Vendor email reminders
- Activity automation
- Certificate expiry warnings

Phase 3:

- Vendor portal
- Broker portal
- Secure external upload

Phase 4:

- Customs costs
- Vendor bills
- Landed costs
- Cost allocation

Phase 5:

- WhatsApp integration
- Courier APIs
- Freight tracking
- AI-assisted document checking
