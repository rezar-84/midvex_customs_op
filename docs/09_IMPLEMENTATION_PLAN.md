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
- Created the module scaffold under `midvex_customs_op/` with `__manifest__.py` and imports.
- Defined all base models (`customs.stage`, `customs.document.type`, `customs.operation`, `customs.document.requirement`) in `models/`.
- Created security category and linear groups (`User`, `Approver`, `Manager`, `Admin`) in `security/customs_security.xml`.
- Added global multi-company record rules to secure stages, document types, operations, and requirements.
- Configured data access rules in `ir.model.access.csv`.
- Loaded sequence prefix `CUS/%(year)s/` with yearly date-range reset.
- Seeded default workflow stages (`Draft` through `Cancelled`) with folding/closed settings.
- Structured base views, actions, and menu items in `views/customs_menus.xml`.
- Created basic unit test checking group inheritance and stage read restrictions in `tests/test_customs_security.py`.

Acceptance criteria:

- Addon directory `midvex_customs_op/` exists.
- Manifest installs with valid dependencies.
- Security groups and initial access rights are defined.
- Base menu and actions load.
- Sequence and default stage data are loaded.
- No unrelated files are modified.
- Documentation and changelog are updated.
- Install or upgrade test is attempted in the available Odoo environment. (N/A; no local Odoo instance, deployment/testing handled by user)

## Milestone 2 — Customs File and product lines

Status: Not started

- Main model
- Product-line model
- Purchase order relationships
- Picking relationships
- Form, list, search, and kanban views
- Chatter and activities
- Initial tests

## Milestone 3 — Document management

Status: Not started

- Document-type model
- Requirement model
- Attachments
- Review workflow
- Original-document fields
- Views and filters
- Tests

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

Status: Not started

- Turkish translation
- User guide
- Administrator guide
- Installation guide
- Upgrade guide
- Final UX review
- Final acceptance review
