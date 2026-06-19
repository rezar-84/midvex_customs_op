# Dashboard and Operational Usability Review - midvex_customs_op

This document reviews the user interface usability, auditing existing search filters, kanban setups, and reporting widgets, and outlines recommendations for a dedicated Import Dashboard.

---

## 1. Existing UI & Reporting Features

* **Kanban View**: Grouped visually by linear Customs Stages, showing key fields (ETA, Broker, Suppliers, Transport Mode, Priority stars), visual completeness progress bar, and user avatar. Cards are color-coded based on stage and priority.
* **Search View Filters**:
  * My Operations (Responsible).
  * In Production, In Transit, In Customs, and Delivered to Warehouse filters.
  * Waiting Documents (missing document count > 0).
  * Ready to Ship / Blocked (shipment_ready status).
  * Planned Arrival (date-based default groupings).
  * Correction/Rejection Pending (rejections or corrections > 0).
* **Reporting Views**: Pivot table and graph analysis for Customs Operations and Document Requirements.
* **Smart KPIs**: Form header shows ribbon statuses ("Overridden", "Closed", "Cancelled") and counters (Approved, Missing, Rejected, Completion %).

---

## 2. Operational Dashboards Requirements & Gaps

A logistics manager needs to instantly see the active volume of import shipments across different states. Below is the verification status of these metrics in the current UI:

| Operational State | Representation in Views / Filters | Usability Status | Gap / Recommendation |
|---|---|---|---|
| **In Production** | Filter `In Production` | **Supported** | Add a Kanban column filter. |
| **Waiting Documents** | Filter `Waiting Documents` | **Supported** | Show a counter badge in reporting. |
| **Corrections Required** | Filter `Correction/Rejection Pending` | **Supported** | Highlight count badge on main menu. |
| **Ready To Ship** | Filter `Ready to Ship` | **Supported** | Filter should be pre-applied on a dedicated menu. |
| **In Transit** | Filter `In Transit` | **Supported** | Map to calendar view dynamically. |
| **Arriving Soon** | Date filter `Planned Arrival` | **Supported** | Group into a "Next 7 Days" quick click filter. |
| **In Customs** | Filter `In Customs` | **Supported** | Display by Customs Sub-Status. |
| **Delivered** | Filter `Delivered to Warehouse` | **Supported** | Differentiate from final accounting closed. |
| **Accounting Pending** | Selection `accounting_status` | **No Search Filter** | Missing a specific search view filter for accounting closing status. |
| **Blocked** | Filter `Blocked` | **Supported** | Highlight operations where ETA is overdue. |

---

## 3. Recommended Dashboard Enhancements

To increase visibility and ease coordinate follow-ups, we recommend implementing a dedicated **Import & Customs Dashboard** (`ir.ui.view` model `spreadsheet.dashboard` or custom dashboard action):

### A. Dynamic KPI Cards (Overview Tiles)
Provide 4 main KPI statistic cards at the top of the reporting dashboard:
1. **Blocked Shipments**: Total active shipments where `shipment_ready = False` and planned arrival is within 10 days.
2. **Missing Documents Count**: Sum of all required documents in draft/requested state.
3. **Pending Corrections**: Total requirements in `correction_required` state.
4. **Vessels in Transit**: Count of operations in `Shipped` stage.

### B. Calendar View Improvements
Currently, the calendar view displays operations by planned arrival date. 
* **Recommendation**: Add colors corresponding to transport mode (e.g., blue for sea, light-blue for air, orange for road) to allow warehouse managers to easily plan cargo discharge equipment.

### C. Search Panel (Sidebar Filtering)
Odoo 19 supports search panels on the left-hand side of list/kanban views:
* **Recommendation**: Implement a `<searchpanel>` in the search view allowing users to quickly click and filter operations by **Supplier**, **Customs Broker**, or **Stage** without typing in the search box.
```xml
<searchpanel>
    <field name="stage_id" icon="fa-filter" groupby="stage_id"/>
    <field name="broker_id" icon="fa-users"/>
</searchpanel>
```
