# Architecture and Product Decisions

| Date | Decision | Reason | Alternatives | Impact |
|---|---|---|---|---|
| 2026-06-18 | Use a custom Odoo module rather than Studio-only customization | Version control, testing, maintainability, security, and upgrade safety | Odoo Studio | Requires development and deployment workflow |
| 2026-06-18 | Keep vendor portal, broker portal, WhatsApp, OCR, and government integrations outside the MVP | Reduce complexity and stabilize the operational core first | Build all integrations immediately | Faster and lower-risk MVP |
| 2026-06-18 | Treat each required document as a structured record rather than only an attachment | Enables status, deadline, responsibility, approval, and original tracking | Folder-only document storage | Adds a dedicated model and workflow |
| 2026-06-18 | Display human-readable readiness blocking reasons | Users need actionable explanations | Boolean readiness only | Additional computed logic and UI |
| 2026-06-18 | Enforce permissions server-side | UI visibility is not sufficient security | Button hiding only | Requires access, rules, and method checks |
| 2026-06-18 | Use `midvex_customs_op` as the Odoo technical module name | The repository folder and remote are named `midvex_customs_op`, and matching the addon technical name reduces deployment ambiguity | Use a longer descriptive technical name | Manifest, module directory, docs, tests, and upgrade commands should use `midvex_customs_op` |

## Pending decisions

- Whether stages are shared globally or company-specific
- Whether document types are shared globally or company-specific
- Exact attachment implementation and relationship to Odoo Documents
- Exact approved-or-later state mapping
- Whether open critical activities should block closure in MVP
- Whether document versioning is manual or attachment-based
