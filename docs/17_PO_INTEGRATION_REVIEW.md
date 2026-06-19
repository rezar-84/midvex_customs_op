# PM Review: Import & Customs Integration Status

Date: 2026-06-19
Task: Integrate Import & Customs Operations with Odoo Purchase, Inventory, Accounting, and Sales

Below is the initial Product Manager review of the current `midvex_customs_op` module capabilities in relation to the new sync requirements:

## 1. Does `customs.operation` already have `purchase_order_ids`?
**Yes.** The `customs.operation` model includes a `purchase_order_ids` Many2many relationship field to `purchase.order` (`customs_operation_purchase_rel`).

## 2. Does `purchase.order` have a smart button to Customs Operations?
**No.** The `purchase.order` model and form view have not yet been extended in the current implementation.

## 3. Is a Customs Operation auto-created when a PO is confirmed?
**No.** There are currently no hooks or method overrides on `purchase.order` confirmation.

## 4. Is there a manual “Create Customs Operation” button on Purchase Order?
**No.** This button does not yet exist.

## 5. Are PO lines imported into Customs Operation lines?
**No.** Standalone creation requires lines to be manually added. No PO-to-operation-line synchronization exists.

## 6. Are incoming pickings linked automatically?
**No.** Standalone operation tracking currently requires selecting pickings manually.

## 7. Are receipts updated when goods arrive or customs clears?
**No.** The stock pickings and operations do not exchange state updates.

## 8. Are vendor bills linked or visible from the Customs Operation?
**No.** There is no accounting integration implemented in the current standalone module.

## 9. Are sales orders linked when the purchase is for a customer order?
**No.** There is no sales integration or lookup implemented.

## 10. Are document requirements generated from product/category/origin data?
**No.** Document requirements are currently created manually for each file. There is no automated document template engine or product customs profile default processing.

## 11. Is multi-company behavior safe?
**Partial.** Multi-company record rules exist on the standalone models (`customs.operation`, `customs.document.requirement`, `customs.stage`, `customs.document.type`). However, company consistency checks for the new purchase, inventory, and accounting linkages have not yet been designed or implemented.

## 12. Are duplicate Customs Operations prevented?
**No.** Since there is no automated creation flow or single-operation constraint per purchase order, duplicate operations can currently be manually created or linked.

---

## Technical and Architectural Path to Integration

To support this vision, we must design extensions for standard Odoo models using clean inheritances, keeping the module upgrade-safe:
1. **`product.template`**: Add fields for product customs profile defaults.
2. **`purchase.order`**: Add sync state fields, action buttons, and smart buttons. Hook `button_confirm` to auto-create operations.
3. **`purchase.order.line`**: Link line changes and sync defaults to operation lines.
4. **`stock.picking`**: Add many-to-one/many-to-many relationship back to `customs.operation` and implement state update triggers.
5. **`account.move`**: Link bills created from POs back to `customs.operation`.
6. **`customs.operation`**: Add fields to hold currency, vendor bill, and sales order relationships.
