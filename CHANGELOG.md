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

### Changed

- Aligned documented technical module name with repository name: `midvex_customs_op`
- Resolved initial pending architecture decisions (global/company-specific stages and document types, Odoo Documents scope, approved states, critical activities, versioning, licensing, and validation method) and detailed specific requirements (security inheritance, yearly sequence reset, product line locking, document requirement deletion, vendor restriction, expiration blocking, and non-mandatory closing warnings) in `docs/10_DECISIONS.md` after the `grill-me` design review interview.

### Fixed

- None
