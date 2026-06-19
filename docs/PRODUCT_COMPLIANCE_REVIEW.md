# Product Compliance Review - midvex_customs_op

This document reviews the product customs profiles, evaluating what properties are tracked, what is missing, and how configuration is distributed between master templates and operational lines.

---

## 1. Existing Product Compliance Fields

The module currently implements product compliance profile extensions directly on **`product.template`**:

* `customs_required` (Boolean): Master trigger to identify if the product goes through import tracking.
* `hs_code` (Char): HS/GTİP tariff code.
* `country_of_origin_id` (Many2one -> `res.country`): Default origin country.
* `manufacturer_id` (Many2one -> `res.partner`): Default manufacturer.
* `health_certificate_required` (Boolean): Triggers Health Certificate requirement.
* `analysis_required` (Boolean): Triggers Certificate of Analysis (COA) requirement.
* `import_permit_required` (Boolean): Triggers Import Permit requirement.
* `original_documents_required` (Boolean): Flags physical document validation requirement.

---

## 2. Dynamic Requirement Generation

When a Customs File is initialized or lines are synced from a purchase order, `_generate_default_document_requirements()` runs. 
If `health_certificate_required` or `analysis_required` is enabled on any product line, the system automatically instantiates a document requirement record specific to that line (e.g. "Health Certificate - Aquaculture Starter Feed EX-10").

This logic is highly functional but has some design limitations.

---

## 3. Gap Analysis & Missing Features

* **Facility Approval Number Validation**: For feeds and animal products (like Artemia, Salmon Eggs), Turkish Ministry of Agriculture regulations require the manufacturer's facility to have an active approval/registration number. While `manufacturer_approval_number` is on `customs.operation.line`, it is not tracked on the partner record or validated against a blacklist.
* **Certificate Expirations**: The product compliance profile tracks if a certificate is *required*, but does not track the *validity period* or *reference number* of global permits (e.g., a yearly Import Permit from the ministry).
* **Country-Specific Rules**: Some products only require a health certificate if imported from specific countries. Currently, the flag is global on the product template.
* **Product-Specific Attachments**: Product compliance documents (like general analysis test sheets or factory ISO certificates) should be uploadable directly to `product.template` as reference files.

---

## 4. Architectural Separation: Template vs. Operation

To maintain clean data structures and avoid pollution, we evaluate which compliance properties belong to the **Product Template** (static master data) versus the **Customs Operation Line** (dynamic shipment data):

| Field / Attribute | Product Template (Master) | Operation Line (Shipment-specific) | Rationale |
|---|---|---|---|
| **GTİP / HS Code** | **Yes** | No (inherited) | GTİP is static per product type. |
| **Default Country of Origin** | **Yes** | No (inherited) | Standard default for vendor planning. |
| **Default Manufacturer** | **Yes** | No (inherited) | Standard default for compliance auditing. |
| **Required Document Flags** | **Yes** | No (inherited) | Regulatory rules are product-category static. |
| **Batch / Lot Number** | No | **Yes** | Unique per production run/container. |
| **Production / Expiry Dates** | No | **Yes** | Unique to the manufactured batch in transit. |
| **Net / Gross Weights** | No | **Yes** | Changes per package load / order quantity. |
| **Facility Approval No.** | **Yes** (on Partner) | **Yes** (recorded in line) | The factory approval is static, but the specific registration used in the shipment is logged. |
| **Compliance Certificates** | **Yes** (if global) | **Yes** (if shipment-specific) | Master import permits belong to template; shipment-specific COAs/HCs belong to operation lines. |
