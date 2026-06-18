# Agent Rules

- Read `AGENTS.md` and every file under `/docs` before changing code.
- Do not modify unrelated modules or files.
- Never modify Odoo core.
- Use Odoo 19 APIs and conventions only.
- Keep the module upgrade-safe and multi-company safe.
- Run tests after every milestone.
- Record architecture decisions in `docs/10_DECISIONS.md`.
- Update `docs/09_IMPLEMENTATION_PLAN.md` as work progresses.
- Keep commits small, focused, and milestone-based.
- Do not add dependencies without documenting the reason and impact.
- Do not use `sudo()` as a shortcut for incorrect access rights.
- Do not weaken access rules to make tests pass.
- Enforce important permissions and business rules server-side.
- Review every main screen as an end user.
- Add tests together with each feature.
- Do not expose secrets, passwords, tokens, database credentials, or private server paths.
- Do not begin the next milestone automatically after completing the current one.
