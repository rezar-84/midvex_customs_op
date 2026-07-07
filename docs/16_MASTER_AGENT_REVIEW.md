# Master Agent Review

Date: 2026-06-18

## Repository inspection

- Repository root: `/home/rubuntu/Projects/midvex_customs_op`
- Remote: `git@github.com:rezar-84/midvex_customs_op.git`
- Current tracked content is documentation plus repository metadata.
- No Odoo addon directory exists yet.
- No `__manifest__.py`, model files, XML views, security CSVs, tests, translations, or deployment config were found.
- `.agents` and `.codex` directories contain no project instruction files.

## Odoo version and conventions

- Target version is documented as Odoo 19 Enterprise.
- No local Odoo source tree, server config, addon path, or existing custom module convention is present in this repository.
- Because no implementation exists, Milestone 1 should establish the project convention rather than copy a local pattern.
- Use standard Odoo addon structure under `midvex_customs_op/`.

## Gap analysis

- Repository has requirements, UX, security, acceptance criteria, and test planning, but no installable addon.
- Repository license file is GPL-3 text, while the master prompt currently states LGPL-3 unless a dependency requires otherwise.
- Odoo runtime path, database name, and upgrade/test command are not documented in the repo.
- No implementation-level dependency decision has been recorded yet.
- No final decision exists for shared versus company-specific stage and document-type configuration.
- No final decision exists for attachment storage and document versioning.
- No final decision exists for whether open critical activities block closing in MVP.
- No final decision exists for the exact approved-or-later document state mapping.
- Default Turkish labels are not yet specified for document types and stages.
- Performance expectations are documented, but no indexing strategy exists yet.

## Recommended final data model

Milestone 1 should scaffold the addon and security foundation only. The full MVP model should remain:

- `customs.operation`
- `customs.operation.line`
- `customs.stage`
- `customs.document.type`
- `customs.document.requirement`

Use `mail.thread` and `mail.activity.mixin` on operational records. Keep stages and document types configurable from the start. Add `company_id` on operational records and configuration records where company-specific behavior is needed; allow shared configuration only through explicit empty-company records and record rules.

Document attachments should initially use standard `ir.attachment` relations on `customs.document.requirement`. Do not add an Odoo Documents dependency in MVP unless the project explicitly decides to use Documents workflows.

## Proposed module directory tree

```text
midvex_customs_op/
  __init__.py
  __manifest__.py
  data/
    customs_sequence.xml
    customs_stage_data.xml
    customs_document_type_data.xml
  demo/
  i18n/
    tr_TR.po
  models/
    __init__.py
    customs_document_requirement.py
    customs_document_type.py
    customs_operation.py
    customs_operation_line.py
    customs_stage.py
  security/
    customs_security.xml
    ir.model.access.csv
  tests/
    __init__.py
    test_customs_document_requirement.py
    test_customs_operation.py
    test_customs_security.py
  views/
    customs_document_requirement_views.xml
    customs_document_type_views.xml
    customs_menus.xml
    customs_operation_views.xml
    customs_stage_views.xml
```

## Recommended dependencies

Initial manifest dependencies for Milestone 1:

- `base`
- `mail`
- `purchase_stock`

Rationale:

- `mail` is required for chatter and activities.
- `purchase_stock` provides purchase and incoming stock-picking integration in one dependency path.
- Additional dependencies should be added only when a field requires them and should be recorded in `docs/10_DECISIONS.md`.

## Assumptions

- The addon technical name is `midvex_customs_op`.
- The user-visible application name remains `Customs Operations`.
- Odoo Enterprise is installed outside this repository.
- The repository itself should become an addon repository, with the addon folder at the repository root.
- MVP will not depend on Odoo Documents, portal, WhatsApp, OCR, courier APIs, or government APIs.
- Turkish translation can be added after source labels stabilize.

## Technical risks

- License mismatch must be resolved before release packaging.
- Without a local Odoo config, install and upgrade tests may require user-provided commands or an external environment.
- Odoo 19 API details must be verified against the actual server before relying on version-specific behavior.
- Multi-company configuration must be designed early to avoid unsafe shared records.
- Attachment volume could affect performance if requirements accumulate many large files.

## UX risks

- Readiness can become difficult to trust if blocking reasons are too vague.
- Configurable stages can confuse users if default stages are not seeded clearly.
- Document copy status and original-document status must remain visually separate.

## Security risks

- Access rules must prevent cross-company leakage for operations, lines, requirements, and attachments.
- Button visibility must not be the only enforcement for approve, reject, close, cancel, or override actions.
- Broad use of `sudo()` would undermine the security model and must be avoided.

## Proposed PRD changes

- Add the technical module name `midvex_customs_op` to the PRD.
- Add a release-blocking requirement to resolve the GPL-3 versus LGPL-3 license mismatch.
- Add an explicit MVP dependency policy: no Odoo Documents dependency unless approved.
- Add an explicit configuration strategy for shared versus company-specific stages and document types.
- Add a required install/upgrade command section once the local Odoo environment is known.

## Milestone 1 acceptance criteria

- Addon directory `midvex_customs_op/` exists.
- Manifest installs with valid dependencies.
- Security groups are defined.
- Initial access-control CSV exists.
- Main menu and base actions load.
- Sequence data is present.
- Default stages are present.
- No business workflow beyond Milestone 1 is implemented.
- Documentation and changelog are updated.
- Install or upgrade test is attempted in the available Odoo environment.
