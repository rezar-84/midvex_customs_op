# UI/UX Specification

## UX objective

A purchasing or logistics user should understand the status and next required action without searching chatter, attachments, or WhatsApp.

## Main navigation

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

## Customs File form

### Header

Show:

- Reference
- Stage statusbar
- Priority
- Responsible user
- Readiness state
- Primary actions

### Readiness block

Show:

- Completion percentage
- Missing-document count
- Rejected-document count
- Expired-document count
- Original-document issues
- Human-readable blocking reasons

### Smart buttons

- Purchase Orders
- Incoming Shipments
- Documents
- Missing Documents
- Activities
- Attachments

### Tabs

1. Overview
2. Products
3. Documents
4. Shipment
5. Customs
6. Original Documents
7. Notes

## Kanban

Show:

- Reference
- Main supplier
- Responsible employee
- Planned arrival
- Stage
- Completion percentage
- Missing count
- Rejected count
- Readiness
- Priority

Avoid overcrowding.

## Document list

Columns:

- Document type
- Customs File
- Supplier
- Status
- Requirement level
- Deadline
- Original required
- Original progress
- Reviewer
- Blocking

## Visual states

- Red: rejected, expired, or overdue mandatory document
- Orange: correction required or approaching deadline
- Green: approved, accepted, or complete
- Muted: not applicable

Always show text or icon status in addition to color.

## Forms

- Hide irrelevant fields.
- Use business language.
- Add concise help text.
- Group related fields.
- Avoid giant forms.
- Require confirmation for destructive actions.
- Avoid excessive modal dialogs.
- Use informative empty states.

## End-user review

For each screen, verify:

- Is the next action clear?
- Is the responsible person clear?
- Is the deadline visible?
- Are blocking reasons readable?
- Can users distinguish copy, approved version, and original?
- Can users reach related PO and stock records quickly?
- Is unnecessary technical terminology hidden?
