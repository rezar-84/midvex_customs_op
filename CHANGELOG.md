# Changelog

All notable changes to the Customs Operations module should be documented here.

## [Unreleased]

### Added

- Initial project requirements
- AI coding-agent instructions
- Product requirements
- UX and security specifications
- Acceptance criteria
- Test planning templates
- Master-agent repository review and Milestone 1 acceptance criteria
- Milestone 1 scaffold: technical Odoo 19 module skeleton, models (`customs.stage`, `customs.document.type`, `customs.operation`, `customs.document.requirement`), custom security category and user groups (`User`, `Approver`, `Manager`, `Admin`), global multi-company record rules, XML sequences (`CUS/YYYY/NNNN`), default stages, root/child menus, and security unit tests in `tests/test_customs_security.py`.
- Milestone 2 Customs Files and product lines: full python models for `customs.operation` (with computed document statistics, relationships to POs/pickings, transport modes, incoterms, and dates) and `customs.operation.line` (with product info, batch details, net/gross weights, and date/weight validations). Built tree/form/kanban/search views, smart buttons linking related records, and automated test cases checking sequence generation, line validation constraints, and computed stats.
- Added comprehensive User and Administration Manual to `README.md` and created an aesthetic Odoo app description in `static/description/index.html` detailing security setup, master data configuration, Customs File management, compliance document tracking, shipment entry, and file closing.
- Milestone 3 Document Management: Overhauled the document requirement model to support responsible users/parties, associated partners (restricted to Customs File parties), deadlines, and original tracking (dispatch date, courier, tracking number). Added automatic version increments when new attachments are uploaded. Implemented validation requiring rejection reasons, restricted deletion logic if attachments exist or if the file's stage is past "Waiting for Documents". Configured form tabs, dynamic partner domains, and tree/search/action views. Added a dedicated suite of unit tests in `tests/test_customs_document_requirement.py`.

### Changed

- Aligned documented technical module name with repository name: `midvex_customs_op`
- Resolved initial pending architecture decisions (global/company-specific stages and document types, Odoo Documents scope, approved states, critical activities, versioning, licensing, and validation method) and detailed specific requirements (security inheritance, yearly sequence reset, product line locking, document requirement deletion, vendor restriction, expiration blocking, and non-mandatory closing warnings) in `docs/10_DECISIONS.md` after the `grill-me` design review interview.

### Fixed

- Fixed Odoo search view parse error in `customs.document.requirement` by replacing tuple syntax with standard list syntax in `state` domain filters in `views/customs_document_requirement_views.xml` and `views/customs_menus.xml`.
