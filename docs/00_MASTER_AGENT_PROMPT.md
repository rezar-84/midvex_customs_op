# AI Coding Agent Master Prompt
## Project: Odoo 19 Customs Operations Module

You are working as a senior Odoo 19 architect, backend developer, frontend developer, product manager, UI/UX designer, QA engineer, security reviewer, and end-user reviewer.

Your task is to design, implement, test, document, and review a production-ready Odoo 19 custom module for VARS Aquaculture.

## Project identity

- Application name: Customs Operations
- Technical name: `midvex_customs_op`
- Target platform: Odoo 19 Enterprise
- Deployment: On-premise
- Database: PostgreSQL
- Company: VARS Aquaculture
- Developer: Midvex
- License: GPL-3
- Source language: English
- Additional translation: Turkish

## Engineering principles

- Follow current Odoo 19 conventions.
- Do not modify Odoo core.
- Do not monkey patch unless strictly necessary and documented.
- Do not hard-code database IDs or company-specific record IDs.
- Avoid unsafe or unnecessary `sudo()`.
- Avoid direct SQL unless justified, reviewed, tested, and documented.
- Use Odoo ORM, access rights, record rules, constraints, and standard view architecture.
- Keep the implementation upgrade-safe and multi-company safe.
- Use translatable strings.
- Keep business logic separate from button and view code.
- Test positive and negative cases.
- Do not change unrelated code.

## Business problem

VARS Aquaculture currently coordinates customs-clearance work through WhatsApp groups, email, attachments, spreadsheets, and verbal follow-up.

Each international shipment may involve:

- Purchasing
- Logistics
- Finance
- Quality or regulatory employees
- Supplier
- Manufacturer
- Freight forwarder
- Customs-clearance company
- Courier
- Laboratory
- Government authority

The business needs one central Odoo Customs File that tracks:

- Purchase orders
- Incoming stock transfers
- Products and batches
- Suppliers
- Customs broker
- Freight forwarder
- Shipment dates and references
- Required customs documents
- Document drafts and versions
- Review and approval
- Corrections and rejection reasons
- Original document issue and dispatch
- Courier tracking
- Customs declaration
- Inspection and laboratory progress
- Customs release
- Warehouse delivery
- Activities, reminders, messages, and audit history

Odoo must become the official operational record. WhatsApp may remain a communication channel during transition, but it must not remain the primary document database or approval record.

## MVP scope

Implement:

1. Customs File
2. Customs File product lines
3. Configurable workflow stages
4. Document types
5. Document requirements
6. Purchase order relationships
7. Incoming stock-picking relationships
8. Supplier and customs-broker relationships
9. Shipment and customs dates
10. Document review workflow
11. Original-document tracking
12. Chatter
13. Activities
14. Sequence generation
15. List, form, kanban, search, calendar, pivot, and graph views where appropriate
16. Security groups, access rights, and record rules
17. Multi-company behavior
18. Turkish translations
19. Automated tests
20. Technical and user documentation

Do not implement in the MVP unless separately approved:

- Supplier portal
- Customs-broker portal
- WhatsApp synchronization
- Government APIs
- Courier APIs
- OCR validation
- AI document checking
- Full landed-cost allocation
- Automatic customs-tax calculation

Prepare clean extension points for future phases.

## Minimum models

Implement at minimum:

- `customs.operation`
- `customs.operation.line`
- `customs.document.type`
- `customs.document.requirement`

Consider adding these only when justified:

- `customs.stage`
- `customs.status.history`
- `customs.original.tracking`

Prefer configurable stage records over hard-coded workflow selections when this improves reporting, usability, and maintainability.

## Default workflow stages

1. Draft
2. Waiting for Documents
3. Document Review
4. Correction Required
5. Ready to Ship
6. Shipped
7. Arrived
8. Customs Clearance
9. Inspection / Laboratory
10. Customs Cleared
11. Delivered to Warehouse
12. Closed
13. On Hold
14. Cancelled

Track meaningful stage transitions in chatter.

## Customs File information

Include:

### Identity and ownership

- Reference
- Active
- Company
- Stage
- Priority
- Responsible user

### Parties

- Suppliers
- Customs broker
- Freight forwarder
- Carrier
- Manufacturer where relevant

### Related records

- Purchase orders
- Incoming stock pickings
- Customs document requirements
- Customs operation lines

### Shipment information

- Operation type
- Transport mode
- Incoterm
- Origin country
- Departure country
- Destination country
- Customs office
- Container number
- Booking number
- Transport document number

### Dates

- Document deadline
- Planned departure
- Actual departure
- Planned arrival
- Actual arrival
- Planned customs clearance
- Actual customs clearance
- Warehouse delivery

### Customs information

- Customs declaration number
- Customs declaration date
- Inspection required
- Laboratory required
- Inspection date
- Release date

### Computed controls

- Total required documents
- Approved document count
- Missing document count
- Rejected document count
- Completion percentage
- Shipment readiness
- Blocking document count
- Human-readable blocking reasons

## Shipment product-line information

Include:

- Customs operation
- Purchase order line
- Product
- Product description
- Customs description
- HS/GTİP code
- Country of origin
- Manufacturer
- Facility approval number
- Batch number
- Production date
- Expiry date
- Quantity
- Unit of measure
- Net weight
- Gross weight
- Package count
- Package type
- Health certificate required
- Analysis required
- Import permit required
- Notes

## Document types

Include:

- Name
- Code
- Turkish name
- Description
- Default responsible party
- Default requirement level
- Original normally required
- Sequence
- Active

Seed common import and customs document types.

## Document requirement information

Include:

- Customs operation
- Customs operation line
- Document type
- Name
- Status
- Requirement level
- Responsible party
- Responsible internal user
- Vendor
- Requested date
- Deadline
- Received date
- Issued date
- Expiry date
- Reviewed date
- Reviewed by
- Original required
- Original issued
- Original dispatched
- Original received
- Dispatch date
- Courier name
- Tracking number
- Attachments
- Rejection reason
- Review notes
- Version
- Blocking status

## Document statuses

Support at minimum:

- Not Requested
- Requested
- Vendor Preparing
- Draft Received
- Under Review
- Correction Required
- Approved
- Original Issued
- Original Dispatched
- Original Received
- Submitted to Customs
- Accepted
- Rejected
- Expired
- Not Applicable

Use clear business labels.

## Core business rules

### Mandatory document completion

A mandatory document counts as complete only when:

- It has at least one valid attachment.
- It is approved or beyond the approved state.
- It is not rejected.
- It is not expired.
- When an original is mandatory, the original has at least been issued.

### Shipment readiness

A shipment is ready only when:

- All mandatory documents are complete.
- No blocking document is rejected.
- No blocking document is expired.
- All required originals are issued.
- Required shipment data is complete.

The UI must explain why a shipment is blocked. Never expose only a boolean.

Examples:

- Two mandatory documents are missing.
- Health Certificate is rejected.
- Certificate of Analysis has no attachment.
- Original Certificate of Origin has not been issued.

### Closing

A Customs File should not close when:

- Mandatory documents remain incomplete.
- Customs release information is missing.
- Warehouse delivery is not recorded.
- Critical activities remain open.

Managers may override only with:

- Override reason
- Approving user
- Date and time
- Chatter log

## Security roles

Implement:

1. Customs User
2. Customs Document Approver
3. Customs Manager
4. Customs Administrator

Enforce security server-side. Hidden buttons alone are not security.

## UI/UX principles

The application must be usable by purchasing and logistics staff with limited technical knowledge.

### Navigation

Customs Operations

- Operations
  - All Customs Files
  - My Customs Files
  - Waiting for Documents
  - Ready to Ship
  - Arriving Soon
  - Customs Clearance
- Documents
  - All Requirements
  - Missing
  - Under Review
  - Correction Required
  - Expiring
- Reporting
  - Customs Analysis
  - Document Analysis
- Configuration
  - Document Types
  - Stages

### Customs File form

Header:

- Reference
- Stage statusbar
- Priority
- Responsible user
- Shipment readiness
- Main workflow actions

Smart buttons:

- Purchase Orders
- Incoming Shipments
- Documents
- Missing Documents
- Activities
- Attachments

Suggested tabs:

1. Overview
2. Products
3. Documents
4. Shipment
5. Customs
6. Original Documents
7. Notes

### Kanban card

Show only operationally important information:

- Reference
- Main supplier
- Responsible user
- ETA
- Stage
- Completion percentage
- Missing document count
- Rejected document count
- Readiness
- Priority

### Document requirement views

Show:

- Document type
- Customs File
- Supplier
- Status
- Requirement level
- Deadline
- Original required
- Original status
- Reviewer
- Blocking indicator

Use color as a supporting cue, never as the only status indicator.

## Product-management responsibilities

Before coding:

1. Read all files in `/docs`.
2. Inspect the repository and existing Odoo conventions.
3. Identify gaps and conflicts.
4. Record assumptions and decisions.
5. Break implementation into milestones.
6. Define acceptance criteria per milestone.
7. Do not silently expand or reduce scope.

During development:

- Update the implementation plan.
- Record significant architecture decisions.
- Track deferred features.
- Keep the MVP focused.
- Report requirement conflicts.

After each milestone, review as:

- Product manager
- Odoo developer
- UI/UX designer
- Purchasing user
- Logistics user
- Quality approver
- Customs manager
- Security reviewer
- QA engineer

## Development standards

- Use `mail.thread`.
- Use `mail.activity.mixin`.
- Track only meaningful fields.
- Store computed fields only when reporting or performance requires it.
- Add constraints for data integrity.
- Use clear method and field names.
- Add docstrings to non-obvious logic.
- Avoid duplicated domains and duplicated workflow logic.
- Make deletion policies explicit.
- Use correct `ondelete` behavior.
- Avoid inline Python in XML.
- Avoid deprecated APIs.
- Keep access checks server-side.
- Ensure multi-company isolation.

## Testing requirements

Automated tests must include:

- Sequence generation
- Customs File creation
- Document completion calculation
- Mandatory attachment validation
- Expiry detection
- Rejection blocking
- Original-document requirements
- Shipment readiness
- Manager override
- Access rights
- Record rules
- Multi-company isolation
- Purchase order linkage
- Incoming-picking linkage
- Stage transition tracking
- Installation and upgrade behavior where practical

## Required deliverables

- Installable module
- Manifest
- Models
- Views
- Security groups
- Access rights
- Record rules
- Sequences
- Default stages
- Default document types
- English source labels
- Turkish translation
- Automated tests
- README
- Changelog
- Installation guide
- Upgrade guide
- Administrator guide
- User guide
- Architecture notes
- Known limitations
- Future roadmap

## Milestones

### Milestone 1

- Module scaffold
- Manifest
- Security groups
- Sequence
- Base menus

### Milestone 2

- Customs File model
- Product lines
- Base form, list, search, and kanban views

### Milestone 3

- Document types
- Document requirements
- Attachments
- Document workflow

### Milestone 4

- Shipment-readiness logic
- Blocking reasons
- Approval actions
- Manager override

### Milestone 5

- Reporting views
- Calendar
- Pivot
- Graph
- Saved filters

### Milestone 6

- Security tests
- Business-logic tests
- Multi-company tests

### Milestone 7

- Turkish translation
- Documentation
- Final end-user review
- Final UI/UX review

At the end of each milestone:

- Run installation or upgrade.
- Run relevant tests.
- Review server logs.
- Review security.
- Review the UI using each affected role.
- Update documentation.
- Update CHANGELOG.
- Commit with a focused message.
- Stop before starting the next milestone.

## Required first action

Do not write implementation code immediately.

First:

1. Inspect the repository.
2. Inspect the current Odoo version and addon conventions.
3. Read `AGENTS.md` and every file under `/docs`.
4. Produce a gap analysis.
5. Recommend a final data model.
6. Create a milestone plan.
7. List assumptions and risks.
8. Record architecture decisions.
9. Update documentation.
10. Wait for milestone approval.

Do not mark the project complete while major acceptance criteria fail.
