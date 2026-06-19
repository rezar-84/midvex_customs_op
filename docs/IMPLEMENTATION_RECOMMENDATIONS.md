# Technical Implementation Recommendations - midvex_customs_op

This document maps out coding standards, optimization strategies, database guidelines, and architectural patterns recommended for the next development milestones of the module.

---

## 1. Odoo 19 Development Conventions

* **API Decoupling**: Do not add direct module dependencies in `__manifest__.py` unless strictly required. Use Odoo's dynamic hooks (`hasattr`, XML xpath priority overrides, and conditional imports) to ensure the core customs module can install and run standalone.
* **Inheritance Rules**: Always call `super()` in overrides. Ensure all method parameters are matched to maintain upgrade compatibility.
* **ORM Performance**:
  * Use `@api.depends_context` when computations vary based on user context (e.g. current company or currency formatting).
  * Set `store=True` on computed fields that are frequently queried in filters, kanban groups, or report pivots (like `document_correction_count`, `document_rejected_count`, etc.) to prevent slow database queries during page rendering.
  * Use `filtered_domain` or `search` on sub-fields instead of doing manual python loops when filtering records in memory.

---

## 2. Multi-Company & Multi-Currency Safety

* **Active Company Context**: Never hardcode `self.env.company`. Always check `self.company_id` on the record.
* **Record Rules**: Ensure all new models have an associated `company_id` field and a matching global record rule in XML.
* **Currency app**: When logging operational costs, utilize the monetary field definition (`Monetary`) mapped to `currency_id` to ensure proper symbol rendering in views:
  ```python
  cost_freight = fields.Monetary(string='Freight Cost', currency_field='currency_id')
  ```
  Ensure the currency field defaults to the current company's currency if not defined on the parent transaction.

---

## 3. Database Optimizations (Indexing Guidelines)

As operations grow, filtering and searching can become database bottlenecks. We recommend setting `index=True` on the following fields:

* `customs.operation`: `user_id`, `broker_id`, `planned_arrival_date`, and `is_sample_data`.
* `customs.operation.line`: `product_id`, `hs_code`, and `expiry_date`.
* `customs.document.requirement`: `state` and `deadline`.

These indexes speed up Kanban groupings, calendar rendering, and search filter execution.

---

## 4. Operational Logging (Chatter Integrity)

* **Audit Trail**: Any state transition or critical date change must write a history note to the Odoo chatter (`message_post`).
* **HTML Sanitization**: Never format chatter messages using direct string interpolation if they contain user input. Always use `Markup` and `escape` to protect against HTML injection:
  ```python
  from markupsafe import Markup, escape
  msg = Markup("<strong>Warning:</strong> Ref %s has expired.") % escape(self.name)
  self.message_post(body=msg)
  ```
