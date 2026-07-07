# Changelog

All notable changes to the Customs Operations module should be documented here.

## [Unreleased]

### Added

- **Integration Phase (Purchase, Inventory, Accounting, Sales Sync)**:
  - Extended `product.template` with default customs compliance profile settings (HS Code, country of origin, manufacturer, and compliance certificate toggles).
  - Extended `purchase.order` and `purchase.order.line` with sync actions, automatic creation hooks on confirmation, and status indicators.
  - Implemented dynamic line synchronization propagating PO line quantity/product edits to `customs.operation.line` until lines are locked.
  - Overrode `stock.picking` validation to check linked Customs File stage sequence, warning or blocking warehouse receipts prior to clearance depending on configuration.
  - Added new configuration model `res.config.settings` and settings view to control strict receipt validation blocking.
  - Associated PO-generated vendor bills (`account.move`) to Customs Files and supported manual external expense bill linkage with cross-navigation.
  - Implemented Sales Order tracing for MTO-procured shipments using origin field, stock move destinations, and procurement groups.
  - Added `tests/test_customs_integration.py` to cover all sync behaviors, warnings, and lock states.
  - Translated all new fields and options to Turkish in `tr_TR.po`.

- **Integration Phase (Purchase, Inventory, Accounting, Sales Sync) Planning**:
  - Created feature branch `feature/purchase-inventory-sales-sync`.
  - Added [docs/17_PO_INTEGRATION_REVIEW.md](file:///home/rubuntu/Projects/midvex_customs_op/docs/17_PO_INTEGRATION_REVIEW.md) documenting initial PM review findings and technical gaps before coding.
  - Updated [docs/01_PRD.md](file:///home/rubuntu/Projects/midvex_customs_op/docs/01_PRD.md) to add functional requirements (FR-020 through FR-026) for auto-creation triggers, PO data sync, stock warning alerts, vendor bill linkage, product profiles, and duplicate prevention.
  - Updated [docs/02_USER_FLOWS.md](file:///home/rubuntu/Projects/midvex_customs_op/docs/02_USER_FLOWS.md) to layout confirmed PO automatic creation paths, manual button action, warning logic, and cost tracking.
  - Updated [docs/03_DATA_MODEL.md](file:///home/rubuntu/Projects/midvex_customs_op/docs/03_DATA_MODEL.md) defining standard Odoo models extensions (`purchase.order`, `purchase.order.line`, `stock.picking`, `account.move`, `product.template`).
  - Updated [docs/04_UI_UX_SPEC.md](file:///home/rubuntu/Projects/midvex_customs_op/docs/04_UI_UX_SPEC.md) outlining smart buttons, clearance banners, and financial tabs.
  - Updated [docs/05_SECURITY_ACCESS.md](file:///home/rubuntu/Projects/midvex_customs_op/docs/05_SECURITY_ACCESS.md) specifying company consistency check rules and linear security boundaries.
  - Updated [docs/06_AUTOMATION_RULES.md](file:///home/rubuntu/Projects/midvex_customs_op/docs/06_AUTOMATION_RULES.md) with PO hooks, sync rules, receipt sub-status warnings, and document requirement template triggers.
  - Updated [docs/07_ACCEPTANCE_CRITERIA.md](file:///home/rubuntu/Projects/midvex_customs_op/docs/07_ACCEPTANCE_CRITERIA.md) and [docs/08_TEST_PLAN.md](file:///home/rubuntu/Projects/midvex_customs_op/docs/08_TEST_PLAN.md) defining criteria and test cases for integration.
  - Updated [docs/09_IMPLEMENTATION_PLAN.md](file:///home/rubuntu/Projects/midvex_customs_op/docs/09_IMPLEMENTATION_PLAN.md) with 5 new milestones for the integration phase.
  - Updated [docs/10_DECISIONS.md](file:///home/rubuntu/Projects/midvex_customs_op/docs/10_DECISIONS.md) to record five new architecture decisions for Odoo standard syncs.
  - Updated [docs/11_USER_GUIDE.md](file:///home/rubuntu/Projects/midvex_customs_op/docs/11_USER_GUIDE.md) detailing how to use integrated flows.
  - Updated [docs/14_RISK_REGISTER.md](file:///home/rubuntu/Projects/midvex_customs_op/docs/14_RISK_REGISTER.md) adding integration risk scenarios.

- Extended the main Customs File (`customs.operation`) model with 30+ fields for comprehensive import tracking: production tracking (status, ready date, loading date), logistics (vessel, tracking link, container/seal info, BL number), customs sub-status, simple cost accounting (freight, tax, storage, stamp, broker, exchange diff, other, total computed cost), and warehouse receiving checklist.
- Added dedicated relational photo attachments (`warehouse_photo_ids`) and delivery notes/POD (`delivery_note_ids`) to the Warehouse tab.
- Programmed automatic python mail activity triggers for key import milestones: Bill of Lading uploaded, warehouse delivery completed, discrepancies/damaged cargo recorded, and ETA approaching (under 3 days).
- Implemented comprehensive demonstration seed data in `demo/customs_demo_data.xml` with representative records at different stages (In Production, Shipped, Customs Clearance with missing documents, and Delivered with damages).
- Added step-by-step instructions and a safe python cleanup script to `README.md` to remove demo data via the Odoo shell.
- Added automated unit tests covering commercial PO computations, cost aggregation, and automatic activity generation.

### Changed

- Reorganized the client form view into 9 structured notebook tabs aligning with the import lifecycle (Overview, Purchase & Supplier, Production, Logistics, Product Lines, Required Documents, Customs & Laboratory, Warehouse, Accounting & Costs).
- Renamed the application, menus, and action labels to "Import & Customs Operations" to match its expanded scope.
- Translated all new fields, status selection options, tab titles, and activity log text into Turkish inside `i18n/tr_TR.po`.

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
- Milestone 7 Localization & Finalization: Added comprehensive Turkish translation files, suppressed validation warning ribbons and reason lists on draft files, conducted final role-based UX/UI audits, and aligned repository-level and manifest-level GPL-3 packaging licenses.

### Changed

- Aligned documented technical module name with repository name: `midvex_customs_op`
- Resolved initial pending architecture decisions (global/company-specific stages and document types, Odoo Documents scope, approved states, critical activities, versioning, licensing, and validation method) and detailed specific requirements (security inheritance, yearly sequence reset, product line locking, document requirement deletion, vendor restriction, expiration blocking, and non-mandatory closing warnings) in `docs/10_DECISIONS.md` after the `grill-me` design review interview.
- Suppressed readiness "Ready Blocked" ribbon and blocking reasons list on draft records (when `is_draft` is True) to reduce visual clutter on new forms.

### Fixed

- Fixed Odoo search view parse error in `customs.document.requirement` by replacing tuple syntax with standard list syntax in `state` domain filters in `views/customs_document_requirement_views.xml` and `views/customs_menus.xml`.
- Added missing Turkish translation mappings in `i18n/tr_TR.po` for all dynamic computed messages, warning text fragments, smart button names, and Python validation/error messages.
- Fixed `KeyError: 'group_id'` traceback on Purchase Order integration by removing the deprecated `group_id` mapped lookup on `purchase.order` in `_compute_sale_orders`, relying instead on origin string parsing and stock move destination chains.
- Fixed `AttributeError: 'res.groups' object has no attribute 'users'` traceback during activity creation by replacing direct group users references with explicit search queries on `res.users` using `groups_id` relation.

