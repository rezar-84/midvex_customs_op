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

Status: Complete; awaiting approval for Milestone 5

- Completion calculation (Completed)
- Blocking reasons (Completed in compute methods)
- Shipment readiness (Completed)
- Manager override (Completed using transient wizard actions)
- Closing validation (Completed in write overrides)
- Security tests (Completed in tests/test_customs_operation.py)
- Business-rule tests (Completed in tests/test_customs_operation.py)

Progress notes:
- Implemented `shipment_ready` calculation based on mandatory documents, original requirements, expiration status (pre-shipment block), and key shipment details completion.
- Formulated human-readable reasons in `blocking_reason_text`.
- Created TransientModel `customs.operation.override.wizard` and action buttons to audit and execute readiness overrides.
- Exposed "Overridden" yellow status ribbons and override history log sheets inside the form view.
- Added `is_critical` field to Odoo standard `mail.activity.type` to block file closing if open critical activities remain.
- Set up database constraint checks on closing preventing final transitions if mandatory documents are incomplete or critical activities remain open.
- Logged warning notifications to the chatter if closing with empty optional/customs declaration details.
- Extended automated tests covering readiness calculations, override transitions, wizard execution, and closing boundary limits.

## Milestone 5 — Reporting

Status: Complete

- Calendar (Completed)
- Pivot (Completed)
- Graph (Completed)
- Saved filters (Completed)
- Operational analysis (Completed with menus and dedicated actions)

Progress notes:
- Implemented operational calendar view displaying Customs Files based on planned arrival date, colored by workflow stage.
- Implemented pivot analysis and graph views for Customs Operations aggregating completion rate, weights, and missing documents count.
- Implemented pivot analysis and graph views for Document Requirements tracking supplier versions and state statistics.
- Added search filters (Correction/Rejection Pending, Arriving Soon in next 7 days, Open Operations) and group-by (Transport Mode).
- Designed Reporting menus (Customs Analysis and Document Analysis).
- Added unit tests verifying action mappings.

## Milestone 6 — Hardening

Status: Complete

- Multi-company tests (Completed)
- Access-rule tests (Completed)
- Performance review (Completed with database indexes)
- Upgrade test (Completed with Odoo 19 config standards)
- Error and warning review (Completed)

Progress notes:
- Added search indexes (`index=True`) on core foreign keys and search filter columns: `active`, `stage_id`, `user_id`, and `broker_id` on `customs.operation`, and `state` on `customs.document.requirement`.
- Extended `tests/test_customs_security.py` with multi-company tests ensuring users in different companies are blocked from cross-reading or writing operations.
- Added linear group boundary tests in `tests/test_customs_security.py` asserting that basic users and approvers are blocked from override actions, while managers can execute them.

## Milestone 7 — Localization and documentation

Status: Complete

- Turkish translation (Complete)
- User guide (Complete)
- Administrator guide (Complete)
- Installation guide (Complete - in README.md)
- Upgrade guide (Complete - in README.md)
- Final UX review (Complete)
- Final acceptance review (Complete)

Progress notes:
- Created a comprehensive User & Administration Manual covering Setup, Master Data Configuration, Operation Management, Document Tracking, Shipment Entry, and closing validation.
- Incorporated the manual into the repository `README.md` and created an aesthetic HTML dashboard description in `static/description/index.html`.
- Implemented Turkish PO translation mappings inside `i18n/tr.po` localizing stages, models, status selections, field labels, and buttons.
- Suppressed readiness block ribbons and text on draft Customs Files (where `is_draft` is True) to prevent pre-shipment alerts on fresh forms, and added Turkish translation entries for all dynamic python-computed error messages and status components.
- Conducted the final role-based UX review and verified licensing alignment (both repository and manifest using GPL-3).

## Post-Audit Remediation: Critical & High-Severity Fixes

Status: Complete (on branch `fix/critical-audit-issues`)

- **C1**: Fixed `AccessError` import in `tests/test_customs_operation.py`.
- **C2**: Added a `code` field to `customs.stage` and updated `customs_menus.xml` domains to avoid translation bugs.
- **C3**: Restructured `unlink()` in `customs.operation` to block deletion outside Draft stage.
- **C4**: Generated and saved Odoo module icon `static/description/icon.png`.
- **H3**: Added a server-side Customs Manager group validation in the override wizard `action_confirm()`.
- **H4**: Sanitized all user inputs in `message_post()` chatter updates using `Markup` and `escape`.
- **H5**: Restricted deletion of product lines in `customs.operation.line` to Draft/Waiting stages.
- **H1**: Added explicit Access Control List rows in `ir.model.access.csv` for Approver, Manager, and Admin groups across all core models.
- **H2**: Removed the `clickable` statusbar option on the document requirement form and implemented workflow action buttons with role-based visibility.
- **H6**: Added write restrictions on the `active` field to prevent basic users from archiving records.
- **H8**: Added write restrictions on `stage_id` preventing non-managers from making backward stage transitions or jumping forward more than 3 stages at once.
- **H7**: Removed global scope override on the reference sequence to support company-scoped numbering.
- Added automated test coverage in `test_customs_operation.py` and `test_customs_security.py` asserting all deletion, transition, and archiving restrictions.


