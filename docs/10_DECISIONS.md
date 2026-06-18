# Architecture and Product Decisions

| Date | Decision | Reason | Alternatives | Impact |
|---|---|---|---|---|
| 2026-06-18 | Use a custom Odoo module rather than Studio-only customization | Version control, testing, maintainability, security, and upgrade safety | Odoo Studio | Requires development and deployment workflow |
| 2026-06-18 | Keep vendor portal, broker portal, WhatsApp, OCR, and government integrations outside the MVP | Reduce complexity and stabilize the operational core first | Build all integrations immediately | Faster and lower-risk MVP |
| 2026-06-18 | Treat each required document as a structured record rather than only an attachment | Enables status, deadline, responsibility, approval, and original tracking | Folder-only document storage | Adds a dedicated model and workflow |
| 2026-06-18 | Display human-readable readiness blocking reasons | Users need actionable explanations | Boolean readiness only | Additional computed logic and UI |
| 2026-06-18 | Enforce permissions server-side | UI visibility is not sufficient security | Button hiding only | Requires access, rules, and method checks |
| 2026-06-18 | Use `midvex_customs_op` as the Odoo technical module name | The repository folder and remote are named `midvex_customs_op`, and matching the addon technical name reduces deployment ambiguity | Use a longer descriptive technical name | Manifest, module directory, docs, tests, and upgrade commands should use `midvex_customs_op` |
| 2026-06-18 | Place the addon in a root-level `midvex_customs_op/` directory | The repository currently has no addon scaffold, and this keeps module code separate from planning docs | Put manifest files directly at repository root | Clear addon path and conventional Odoo packaging |
| 2026-06-18 | Start MVP dependencies with `base`, `mail`, and `purchase_stock` | The MVP needs chatter, activities, purchase orders, and incoming pickings | Add broader dependencies immediately | Keeps dependency surface narrow while supporting required integrations |
| 2026-06-18 | Use standard `ir.attachment` integration for MVP document files | It supports file uploads without adding Odoo Documents workflows before approval | Depend on Odoo Documents from Milestone 1 | Smaller MVP scope and fewer security surfaces |
| 2026-06-18 | Support both global and company-specific stages | Multi-company setups need flexible staging without duplicating configuration | strictly global or strictly company-specific | Use optional `company_id` on `customs.stage` (null = global) |
| 2026-06-18 | Support both global and company-specific document types | Allows standardized document types globally with company-level exceptions | strictly global or strictly company-specific | Use optional `company_id` on `customs.document.type` (null = global) |
| 2026-06-18 | Map approved-or-later document requirement states | Completeness checks need clear criteria for states beyond basic approval | Only 'Approved' and 'Accepted' | 'Approved', 'Original Issued', 'Original Dispatched', 'Original Received', 'Submitted to Customs', and 'Accepted' count as complete |
| 2026-06-18 | Identify critical activities using a custom field | Closing validation needs to identify critical blockages without hardcoding | Block on all open activities / no blocking | Add `is_critical` to `mail.activity.type`; block closing if critical activities are open |
| 2026-06-18 | Automatically increment document requirement version | Simplifies version tracking when uploading new file versions | Manual version input | Increment `version_number` field automatically when attachments change |
| 2026-06-18 | Use GPL-3 as the module license | Avoids licensing mismatch with the existing repository LICENSE file | LGPL-3 | Set license to GPL-3 in `__manifest__.py` |
| 2026-06-18 | Use static analysis and AI review for validation | No local Odoo runtime is available on the development machine | Local docker setup / mock testing | Strict code validation by AI; user validates in own environment |

## Pending decisions

None. All pending architectural decisions for the initial phase have been resolved.
