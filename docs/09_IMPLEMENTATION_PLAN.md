# Implementation Plan

## Milestone 0 — Repository and requirements review

Status: Complete; awaiting approval for Milestone 1

- Inspect repository
- Read all documentation
- Review existing custom-module conventions
- Produce gap analysis
- Confirm module dependencies
- Record assumptions
- Record risks
- Record architecture decisions

Progress notes:

- Repository root and remote identify the project as `midvex_customs_op`.
- Documentation technical module name references were aligned to `midvex_customs_op`.
- Implementation has not started; Milestone 1 requires explicit approval.
- Master-agent repository review is recorded in `docs/16_MASTER_AGENT_REVIEW.md`.
- No existing Odoo addon, manifest, tests, security files, translation files, or local Odoo config were found.
- Milestone 1 should establish the addon structure and baseline conventions.
- Conducted the `grill-me` design review interview on 2026-06-18, resolving all initial pending architecture decisions and detailing specific requirements for security inheritance, sequence resetting, product locking, document deletion, vendor restriction, expiration stages, and closing conditions (all documented in `docs/10_DECISIONS.md`).
- Confirmed that Odoo is not installed on the development machine; validation will be handled via static analysis and AI review, with deployment and testing in the user's environment.

## Milestone 1 — Scaffold and security foundation

Status: Complete; awaiting approval for Milestone 2

- Module directory
- Manifest
- Init files
- Security groups
- Initial access rights
- Sequence
- Base menus
- Default stages

Progress notes:
- Created the module scaffold directly at the repository root with `__manifest__.py` and imports.
- Defined all base models (`customs.stage`, `customs.document.type`, `customs.operation`, `customs.document.requirement`) in `models/`.
- Created security category and linear groups (`User`, `Approver`, `Manager`, `Admin`) in `security/customs_security.xml`.
- Added global multi-company record rules to secure stages, document types, operations, and requirements.
- Configured data access rules in `ir.model.access.csv`.
- Loaded sequence prefix `CUS/%(year)s/` with yearly date-range reset.
- Seeded default workflow stages (`Draft` through `Cancelled`) with folding/closed settings.
- Structured base views, actions, and menu items in `views/customs_menus.xml`.
- Created basic unit test checking group inheritance and stage read restrictions in `tests/test_customs_security.py`.

Acceptance criteria:

- Odoo manifest and code files exist directly at the repository root (clonable as `midvex_customs_op`).
- Manifest installs with valid dependencies.
- Security groups and initial access rights are defined.
- Base menu and actions load.
- Sequence and default stage data are loaded.
- No unrelated files are modified.
- Documentation and changelog are updated.
- Install or upgrade test is attempted in the available Odoo environment. (N/A; no local Odoo instance, deployment/testing handled by user)

## Milestone 2 — Customs File and product lines

Status: Complete; awaiting approval for Milestone 3

- Main model (`customs.operation`)
- Product-line model (`customs.operation.line`)
- Purchase order relationships (`purchase.order`)
- Picking relationships (`stock.picking`)
- Form, list, search, and kanban views
- Chatter and activities
- Initial tests

Progress notes:
- Implemented core `customs.operation` model with fields for parties (suppliers, broker, forwarder, carrier), integration ids (POs and pickings), shipment logistics, dates, and customs data.
- Built Odoo 19 computed stats for total, approved, missing, and rejected documents, along with completion percentage.
- Implemented `customs.operation.line` model for product batching, HS code support, and weights, with constraints for dates and weight integrity.
- Created `action_view` methods to support stat/smart buttons linking to purchase orders, stock pickings, document requirements, and missing documents.
- Designed views in `views/customs_operation_views.xml` including:
  - List view with completion progressbar and status toggles.
  - Kanban view grouped by stage with colored card styles, ETA info, and user avatar.
  - Form view structured into header statusbar, smart buttons, ribbons, standard fields, and tabs (Overview, Product Lines, Documents, Shipment, Customs & Lab).
  - Search view with domain filters for My Operations, Ready/Blocked, Active/Archived, and groupings.
- Linked views to menus in `__manifest__.py`.
- Added unit tests in `tests/test_customs_operation.py` checking sequences, date/weight constraints, and document stat recomputations.

## Milestone 3 — Document management

Status: Complete; awaiting approval for Milestone 4

- Document-type model (Completed)
- Requirement model (Completed)
- Attachments (Completed using ir.attachment)
- Review workflow (Completed with rejection reason validation)
- Original-document fields (Completed with courier and dispatch info)
- Views and filters (Completed search, tree, and form view enhancements)
- Tests (Completed in tests/test_customs_document_requirement.py)

Progress notes:
- Overhauled `customs.document.requirement` model with fields for responsible employee, vendor/partner, deadlines, and courier dispatch data.
- Enforced rejection reason input validation on transitions to correction/rejection states.
- Restrained `vendor_id` on document requirements to related partners on the Customs File.
- Restricted the deletion of document requirements if attachments exist or if the file's stage is past `Waiting for Documents`.
- Hooked `write` to auto-increment the requirement `version_number` when attachments are added.
- Integrated a dynamic allowed-vendor filter for form view selections.
- Developed a comprehensive unit test suite covering constraints, deletion rules, and versioning.

## Milestone 4 — Readiness and approval controls

Status: Not started

- Completion calculation
- Blocking reasons
- Shipment readiness
- Manager override
- Closing validation
- Security tests
- Business-rule tests

## Milestone 5 — Reporting

Status: Not started

- Calendar
- Pivot
- Graph
- Saved filters
- Operational analysis

## Milestone 6 — Hardening

Status: Not started

- Multi-company tests
- Access-rule tests
- Performance review
- Upgrade test
- Error and warning review

## Milestone 7 — Localization and documentation

Status: In Progress

- Turkish translation (Not started)
- User guide (Complete)
- Administrator guide (Complete)
- Installation guide (Complete - in README.md)
- Upgrade guide (Complete - in README.md)
- Final UX review (Not started)
- Final acceptance review (Not started)

Progress notes:
- Created a comprehensive User & Administration Manual covering Setup, Master Data Configuration, Operation Management, Document Tracking, Shipment Entry, and closing validation.
- Incorporated the manual into the repository `README.md` and created an aesthetic HTML dashboard description in `static/description/index.html`.
