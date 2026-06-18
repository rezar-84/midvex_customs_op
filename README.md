# Odoo 19 Customs Operations — AI Agent Documentation Pack

This repository documentation pack defines the requirements, architecture expectations, UX principles, security rules, testing requirements, and implementation workflow for the `midvex_customs_op` Odoo 19 module.

## Purpose

The module centralizes import shipment tracking, customs-clearance workflows, document requirements, approvals, original-document tracking, deadlines, activities, and warehouse handover.

## Recommended usage

1. Copy `AGENTS.md` and the `/docs` directory into the root of the development repository.
2. Give the coding agent the content of `docs/00_MASTER_AGENT_PROMPT.md`.
3. Ask the agent to complete the documentation review task in `docs/12_AGENT_START_TASK.md`.
4. Review the agent's assumptions and architecture decisions.
5. Approve Milestone 1 only after the documentation review is complete.
6. Use `docs/13_MILESTONE_EXECUTION_PROMPT.md` for every implementation milestone.

## Target

- Odoo 19 Enterprise
- On-premise deployment
- Technical module name: `midvex_customs_op`
- Company: VARS Aquaculture
- Developer: Midvex
- Source language: English
- Additional translation: Turkish
