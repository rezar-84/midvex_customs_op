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
- Milestone 4 Readiness and Approval Controls: Implemented core readiness calculation logic (`shipment_ready`) combining mandatory document completion, original document checks, pre-shipment expiration rules, and key shipment logistics data. Configured human-readable explanations inside `blocking_reason_text`. Developed the TransientModel `customs.operation.override.wizard` wizard allowing Customs Managers to bypass readiness controls with documented audit logging. Added view options including status ribbons and override logs. Inherited the standard `mail.activity.type` model to add `is_critical` tracking, blocking file closure if critical activities remain open. Added unit tests for readiness, override rules, and closing validations.
- Milestone 5 Reporting: Implemented operational Calendar views for tracking scheduled arrivals, Pivot grids, and Graph bar/pie visualizations for both Customs Files (aggregating weights, completion percentages, missing document counts) and Document Requirements (tracking version history and state statuses). Added saved filters ("Arriving Soon", "Correction/Rejection Pending", "Open Operations") and groupings ("Transport Mode"), and created dedicated "Customs Analysis" and "Document Analysis" menus under the new "Reporting" top section. Implemented view integration tests.
- Milestone 6 Hardening: Optimized database search performance by adding indexes (`index=True`) on core foreign keys (`stage_id`, `user_id`, `broker_id`) and selection status columns (`active` on operations, `state` on document requirements). Expanded automated test coverage in `tests/test_customs_security.py` with multi-company isolation checks (ensuring cross-company record blockages) and linear security action boundary audits (ensuring basic users/approvers cannot call override actions).

### Changed

- Aligned documented technical module name with repository name: `midvex_customs_op`
- Resolved initial pending architecture decisions (global/company-specific stages and document types, Odoo Documents scope, approved states, critical activities, versioning, licensing, and validation method) and detailed specific requirements (security inheritance, yearly sequence reset, product line locking, document requirement deletion, vendor restriction, expiration blocking, and non-mandatory closing warnings) in `docs/10_DECISIONS.md` after the `grill-me` design review interview.
- Suppressed readiness "Ready Blocked" ribbon and blocking reasons list on draft records (when `is_draft` is True) to reduce visual clutter on new forms.

### Fixed

- Fixed Odoo search view parse error in `customs.document.requirement` by replacing tuple syntax with standard list syntax in `state` domain filters in `views/customs_document_requirement_views.xml` and `views/customs_menus.xml`.
- Added missing Turkish translation mappings in `i18n/tr.po` for all dynamic computed messages, warning text fragments, smart button names, and Python validation/error messages.

