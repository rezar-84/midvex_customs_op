# Customs Operations (Odoo 19 Module)

Customs Operations is an Odoo 19 module designed to manage international shipments, track required compliance documents, verify originals, and automate readiness calculations. It serves as the single source of truth for import operations, replacing manual tracking systems like spreadsheets and WhatsApp chats.

## Installation

1. Place this directory (or clone it) directly inside your Odoo `addons` path as a folder named `midvex_customs_op`.
2. Enable developer mode in your Odoo database.
3. Go to Apps > Update Apps List.
4. Search for `Customs Operations` (technical name: `midvex_customs_op`) and click **Install**.

## Configuration

* **Stages**: Define stages of shipment progress under Configuration > Stages.
* **Document Types**: Define document types (like Certificate of Analysis, Health Certificate) under Configuration > Document Types.

## License

GPL-3. See the `LICENSE` file at the repository root.

***

# Developer & AI Agent Guidelines

This repository includes a documentation pack that defines the specifications and planning for development.

## Folder Structure

* `docs/`: Project specifications, PRD, security rules, and milestone tracking.
* `models/`, `views/`, `data/`, `security/`, `tests/`: Standard Odoo module directories.
* `AGENTS.md`: High-level guidelines for AI coding agents.

## AI Recommended Usage

1. Copy `AGENTS.md` and the `/docs` directory into the root of your workspace.
2. Provide the coding agent with the content of `docs/00_MASTER_AGENT_PROMPT.md`.
3. Ask the agent to follow the instructions in `docs/13_MILESTONE_EXECUTION_PROMPT.md` for each milestone.
