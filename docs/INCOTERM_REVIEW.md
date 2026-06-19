# Incoterm Review - midvex_customs_op

This document reviews the Incoterm implementation within the Customs Operations module, mapping existing fields and outlining a recommended Responsibility Engine structure.

---

## 1. Existing Incoterm Capabilities

* **Model Linkage**: The model `customs.operation` has `incoterm_id` (Many2one -> `account.incoterms`) linking to Odoo's standard Incoterm dictionary.
* **Synchronization**: On purchase order confirmation, `incoterm_id` is synced from the PO to the Customs Operation.
* **Limitations**: The system treats the Incoterm purely as a text label. It does not enforce any logic, calculate financial duties, or map logistical responsibilities between the supplier and the importer.

---

## 2. Gap Analysis (Responsibilities Matrix)

Different Incoterms define who is responsible for each logistics step. The following responsibilities are currently missing from the module's logic:

* **Incoterm Named Location**: Most Incoterms require a named port or place (e.g., "FOB Tokyo" or "DAP Istanbul Warehouse"). The model has no field to capture this location.
* **Freight Responsibility**: Who pays for international shipping.
* **Insurance Responsibility**: Who insures the cargo in transit.
* **Customs Responsibility**: Who clears export and import customs.
* **Import Tax Responsibility**: Who pays customs duties and VAT.
* **Local Delivery Responsibility**: Who covers shipping from the port of discharge to the warehouse.

The table below shows how standard Incoterms map these responsibilities, which should be modeled in the system:

| Incoterm Code | Named Place | Export Customs | International Freight | Marine Insurance | Import Customs | Import Taxes | Local Delivery |
|---|---|---|---|---|---|---|---|
| **EXW** | Origin Point | Importer | Importer | Importer | Importer | Importer | Importer |
| **FOB** | Port of Loading | Supplier | Importer | Importer | Importer | Importer | Importer |
| **CFR** | Port of Discharge | Supplier | Supplier | Importer | Importer | Importer | Importer |
| **CIF** | Port of Discharge | Supplier | Supplier | Supplier | Importer | Importer | Importer |
| **DAP** | Destination Place | Supplier | Supplier | Supplier | Importer | Importer | Supplier |
| **DDP** | Destination Place | Supplier | Supplier | Supplier | Supplier | Supplier | Supplier |

---

## 3. Recommended Implementation Approach (Incoterm Responsibility Engine)

To move beyond plain text labels, we recommend introducing a metadata-driven **Incoterm Responsibility Engine** in Odoo.

### A. Model Extension
Extend `account.incoterms` to store responsibility metadata, or create a configuration mapping table `customs.incoterm.rule` linked to standard incoterms:
```python
class AccountIncoterms(models.Model):
    _inherit = 'account.incoterms'

    freight_responsible = fields.Selection([('supplier', 'Supplier'), ('importer', 'Importer')], default='importer')
    insurance_responsible = fields.Selection([('supplier', 'Supplier'), ('importer', 'Importer')], default='importer')
    import_customs_responsible = fields.Selection([('supplier', 'Supplier'), ('importer', 'Importer')], default='importer')
    import_tax_responsible = fields.Selection([('supplier', 'Supplier'), ('importer', 'Importer')], default='importer')
    local_delivery_responsible = fields.Selection([('supplier', 'Supplier'), ('importer', 'Importer')], default='importer')
```

### B. Customs Operation Fields
Add fields to `customs.operation` to track named location and dynamic responsibilities:
* `incoterm_location` (Char): The named place associated with the Incoterm (e.g. "Tokyo Port").
* `freight_paid_by` (Selection): Computed based on the selected incoterm, allowing manual manager adjustment.
* `insurance_paid_by` (Selection): Computed.

### C. Compliance Automation (Rules Integration)
* **Cost Warnings**: If the active Incoterm is `CIF`, the importer should not pay for freight. If a freight expense bill is linked, the system should flag a warning in the chatter.
* **Document Adjustments**: If `EXW` is selected, the system should automatically generate a document requirement for "Export Declaration Scan" (ihracat beyannamesi), which is typically handled by the seller in other terms.
