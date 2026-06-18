# Risk Register

| Risk | Category | Likelihood | Impact | Mitigation | Status |
|---|---|---:|---:|---|---|
| Requirements vary by product and origin country | Product | High | High | Keep MVP manual but prepare requirement-template extension | Open |
| Users continue using WhatsApp as the official record | Adoption | High | High | Define Odoo as the official approval and document-status source | Open |
| Access rights expose files across companies | Security | Medium | High | Add multi-company record rules and automated tests | Open |
| Readiness calculation becomes too rigid | Product | Medium | High | Show blocking reasons and controlled manager override | Open |
| Large attachment volume affects performance | Technical | Medium | Medium | Review attachment storage and Documents integration | Open |
| Hard-coded workflow blocks future customization | Architecture | Medium | Medium | Prefer configurable stages | Open |
| Document status and original status are conflated | UX | Medium | High | Keep copy approval and original tracking separate | Open |
| Incorrect use of sudo bypasses controls | Security | Medium | High | Enforce code-review and security tests | Open |
| Repository license text conflicts with documented module license | Legal | Medium | High | Resolve GPL-3 versus LGPL-3 decision before release packaging | Open |
| No local Odoo runtime config is documented | Delivery | Medium | Medium | Capture install, upgrade, and test commands before or during Milestone 1 | Open |
| No existing addon conventions are present in the repo | Technical | Low | Medium | Establish standard Odoo addon layout in Milestone 1 | Open |
