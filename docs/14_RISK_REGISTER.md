# Risk Register

| Risk | Category | Likelihood | Impact | Mitigation | Status |
|---|---|---:|---:|---|---|
| Requirements vary by product and origin country | Product | High | High | Keep MVP manual but prepare requirement-template extension | Mitigated |
| Users continue using WhatsApp as the official record | Adoption | High | High | Define Odoo as the official approval and document-status source | Closed |
| Access rights expose files across companies | Security | Medium | High | Added multi-company record rules and automated tests | Mitigated |
| Readiness calculation becomes too rigid | Product | Medium | High | Showed blocking reasons and controlled manager override wizard | Mitigated |
| Large attachment volume affects performance | Technical | Medium | Medium | Review attachment storage and Documents integration | Mitigated |
| Hard-coded workflow blocks future customization | Architecture | Medium | Medium | Configurable stages database model loaded | Mitigated |
| Document status and original status are conflated | UX | Medium | High | Copy approval and original tracking kept separate | Closed |
| Incorrect use of sudo bypasses controls | Security | Medium | High | Enforced clean code reviews and automated security tests | Closed |
| Repository license text conflicts with documented module license | Legal | Medium | High | Resolved licensing to GPL-3 in manifest and files | Closed |
| No local Odoo runtime config is documented | Delivery | Medium | Medium | Static analysis and manual test procedures documented | Closed |
| No existing addon conventions are present in the repo | Technical | Low | Medium | Established standard Odoo addon layout | Closed |
