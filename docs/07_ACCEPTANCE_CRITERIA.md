# Acceptance Criteria and Review Checklist

## Installation

- Installs on a clean Odoo 19 database.
- Upgrades without errors.
- No unresolved traceback appears.
- XML IDs are unique.
- Dependencies are valid.
- Menus are correctly restricted.

## Customs File

- A unique reference is generated.
- Company and responsible user are assigned correctly.
- Multiple purchase orders can be linked.
- Multiple incoming pickings can be linked.
- Multiple product lines can be added.
- Chatter and activities work.

## Product lines

- Product and PO line can be selected.
- Quantity and UoM work correctly.
- Batch, production date, expiry, GTİP, origin, and manufacturer can be stored.
- Regulatory flags work.

## Document types

- Administrators can manage types.
- Ordinary users cannot change configuration.
- Codes are unique.
- Inactive types are excluded from normal selection.
- Default data installs successfully.

## Document requirements

- Can link to a Customs File.
- Can optionally link to a product line.
- Supports mandatory, conditional, and optional.
- Supports supplier and responsible user.
- Supports deadline.
- Supports multiple attachments.
- Supports original tracking.
- Rejection and correction require reasons.

## Completion logic

A mandatory document is incomplete when:

- No attachment exists
- It is rejected
- It requires correction
- It is expired
- Required original has not been issued

A mandatory document is complete when:

- Attachment exists
- It is approved or later
- It is not expired
- Required original has been issued

Optional and Not Applicable documents do not reduce the mandatory completion percentage.

## Shipment readiness

Readiness is false when:

- Mandatory document is missing
- Mandatory document lacks an attachment
- Mandatory document is rejected
- Mandatory document is expired
- Required original is not issued
- Required shipment information is missing

The UI shows specific blocking reasons.

## Workflow

- All configured stages are available.
- Stage changes are tracked.
- Close and cancel are restricted.
- Manager override is restricted and audited.

## Security

Test every role and multi-company access.

## UI/UX

- Statusbar is visible.
- Readiness is visible without excessive scrolling.
- Blocking reasons are readable.
- Smart buttons work.
- Tabs are logically organized.
- Kanban is concise.
- Document statuses do not rely only on color.
- Empty states provide guidance.

## Reporting

- Group and filter by stage, supplier, broker, responsible user, document status, document type, deadline, and arrival date.
- Missing, correction-required, overdue, and arriving-soon filters work.

## Automated tests

Include tests for:

- Sequence
- Completion logic
- Missing attachment
- Rejection
- Expiry
- Required original
- Readiness
- Override
- Security
- Record rules
- Multi-company
- PO relationship
- Picking relationship
- Stage tracking

## Definition of done

- Code is implemented.
- Views are usable.
- Security is tested.
- Automated tests pass.
- Manual scenarios pass.
- Turkish translation is included.
- Documentation is updated.
- Known limitations are documented.
