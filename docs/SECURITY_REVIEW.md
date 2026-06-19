# Security and Access Audit - midvex_customs_op

This document reviews the security groups, access control lists (ACLs), multi-company isolation, record rules, and code execution safety for the Import & Customs Operations module.

---

## 1. Security Groups Audit

The module implements four linear security groups using Odoo 19's **Privilege** structure:

1. **Customs User (`group_customs_user`)**: Implies internal user permissions. Can create/edit active operations and upload files. Cannot delete operations or override checks.
2. **Customs Document Approver (`group_customs_approver`)**: Implies User. Can approve, reject, or mark documents for correction.
3. **Customs Manager (`group_customs_manager`)**: Implies Approver. Can close operations, trigger the override wizard to bypass readiness locks, delete draft records, and access reporting.
4. **Customs Administrator (`group_customs_admin`)**: Implies Manager. Full permissions including master configuration of workflow stages and document types.

---

## 2. Multi-Company Isolation

To ensure complete data isolation in multi-company environments:

* **Record Rules**: All core models have active global record rules filtering by `company_ids` (the user's allowed company list):
  * `customs.operation`: `[('company_id', 'in', company_ids)]`
  * `customs.operation.line`: `[('company_id', 'in', company_ids)]` (related to parent operation)
  * `customs.document.requirement`: `[('company_id', 'in', company_ids)]`
* **Configuration Scoping**: Master tables `customs.stage` and `customs.document.type` support shared global templates AND company-specific configurations:
  * Record Rule: `['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]` (null company means shared globally).
* **View Filters**: Selection inputs (such as choosing vendor bills or pickings) are limited by company constraints in XML definitions: `domain="[('company_id', '=', company_id)]"`.

---

## 3. Vulnerability & Sudo Scan

A detailed scan was performed for code-level vulnerabilities and potential privilege escalations:

* **Unsafe Sudo Usage**: There are **zero** unsafe `sudo()` calls in business logic. The only instance is a standard Odoo lookup in [stock_picking.py](file:///home/rubuntu/Projects/midvex_customs_op/models/stock_picking.py#L86) to fetch the system parameter `midvex_customs_op.customs_block_receipt_before_clearance`. This is safe and necessary since normal warehouse users lack permission to read configuration parameters.
* **Wizard Security**: The transient override wizard (`customs.operation.override.wizard`) restricts button actions to managers. In `action_confirm()`, a server-side validation checks group membership:
  ```python
  if not self.env.user.has_group('midvex_customs_op.group_customs_manager'):
      raise AccessError(_("Only Customs Managers are allowed to confirm readiness overrides."))
  ```
  This prevents front-end bypasses where a basic user attempts to execute the controller action directly.
* **Stage Transitions**: The `write()` method in [customs_operation.py](file:///home/rubuntu/Projects/midvex_customs_op/models/customs_operation.py#L663) restricts backward transitions or stage skipping to Customs Managers. This enforces strict workflow progression.
* **Sanitization**: All user-facing alerts and chatter logs generated in python models utilize `Markup` and `escape` from `markupsafe` to prevent Cross-Site Scripting (XSS) injections in chatter notifications.
