# Future Integrations Guide - midvex_customs_op

This document provides architectural recommendations and technical feasibility assessments for future portals, tracking, and communication bridges.

---

## 1. Vendor Upload Portal

### A. Business Case
Expose a secure portal interface where international suppliers can view required document checklists for their active orders and upload invoice scans, packing lists, COAs, and Health Certificates directly.

### B. Technical Recommendation
* **Portal Controller**: Extend Odoo's standard `PortalChatter` and create a controller `customs.portal` inheriting from `CustomerPortal`.
* **Access Rights**: Portal users (type `portal`) belong to the supplier contact. Add record rules restricting portal users to see only `customs.operation` records where `supplier_ids` contains `portal_user.partner_id.id`.
* **Upload Mechanism**: Display the required document rows. When a vendor uploads a file, programmatically write the file as an attachment to `ir.attachment` linked to that `customs.document.requirement`, automatically incrementing the version and transitioning the state to `under_review`.
* **Passcode-based Direct Upload Links**: To avoid setting up portal users for every small supplier, generate a secure token on the `customs.operation` (e.g. uuid-based). Include a link in purchase emails (e.g. `/customs/upload/<token>`) allowing direct uploads via a public token-authorized route.

---

## 2. Customs Broker Portal

### A. Business Case
Allow external customs brokers to view approved compliance documents, download them as a ZIP package, and input customs declaration entries (Beyanname No, Muayene Hattı, release dates) directly.

### B. Technical Recommendation
* **Broker Portal Controller**: Expose a custom dashboard view for brokers (`partner_id` matches `broker_id` on active operations).
* **ZIP Packaging**: Create a controller method that aggregates all approved `ir.attachment` records for a Customs File into a single zip archive on-the-fly and returns it as a download stream.
* **Direct Input Form**: Provide simple input fields inside the portal interface mapping directly to:
  * `customs_declaration_number`
  * `customs_declaration_date`
  * `customs_status` (update to "Declaration Opened", "Tax Paid")
  * `inspection_date` (if Red/Yellow Line muayene scheduled)

---

## 3. Freight & Container Tracking

### A. Business Case
Connect to international logistics APIs to automatically retrieve vessel departures, container location updates, and ETA/ATA dates.

### B. Technical Recommendation
* **API Providers**: Integrate with multi-carrier tracking API aggregates (e.g. SeaRates, Project44, Vizion, or terminal-specific portals).
* **Sync Routine**: A nightly scheduled action (cron) queries operations in the `Shipped` stage that have a populated `container_number` or `bl_number`.
* **API Request**: Send tracking queries to the service endpoint.
* **Auto-Updates**: Parse the JSON payload and automatically update:
  * `vessel_name` (if changed)
  * `planned_arrival_date` (ETA)
  * `actual_arrival_date` (ATA, triggers stage change)
  * Add log updates directly to the chatter (e.g. "Vessel entered Gibraltar Strait").

---

## 4. Email Automation Rules

### A. Business Case
Auto-send weekly emails to suppliers requesting missing documents, or alert buyers if a document deadline is overdue.

### B. Technical Recommendation
* **Cron Actions**: Create an Odoo scheduled action `ir.cron` running daily.
* **Python Job**:
  ```python
  overdue_requirements = self.env['customs.document.requirement'].search([
      ('state', 'in', ['requested', 'vendor_preparing']),
      ('deadline', '<', fields.Date.today())
  ])
  ```
* **Mail Templates**: Build a stylized HTML mail template linked to the `customs.operation` model. Aggregate missing documents into a clean bulleted list inside the email body.
* **Trigger**: Trigger emails automatically to `supplier_ids` contacts.

---

## 5. WhatsApp Communication Bridge

### A. Business Case
Expose WhatsApp widgets for chat updates and create Odoo activities or notes directly from messages.

### B. Technical Recommendation
* **Odoo WhatsApp Integration**: Leverage Odoo 19's native `whatsapp` integration module.
* **Webhook Listeners**: Configure a webhook endpoint receiver mapping to incoming WhatsApp messages from verified partner phone numbers.
* **NLP / AI Parsing**: Use an LLM or parser to screen the text:
  * If a broker sends "Tax paid for CUS/2026/0014", parse the reference and automatically transition the operation's `customs_status` to `tax_paid`, logging the message in the chatter.
  * If a vendor sends a document photo/PDF via WhatsApp, extract the attachment and link it to the open requirement record.
