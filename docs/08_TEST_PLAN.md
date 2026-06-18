# Test Plan

## Automated test categories

### Installation

- Install on clean database
- Upgrade after adding data
- Validate default records
- Validate menus and actions

### Model tests

- Customs File sequence
- Required fields
- Company consistency
- Product-line relationships
- Document-state transitions
- Completion calculations
- Expiry and overdue calculations
- Readiness calculation
- Override audit data

### Security tests

Test as:

- Customs User
- Document Approver
- Customs Manager
- Customs Administrator
- User from another company

Attempt permitted and forbidden operations through ORM methods.

### View and action smoke tests

- Actions open
- Domains are valid
- Search views load
- Kanban renders
- Calendar, pivot, and graph render
- Configuration menus are restricted

## Manual scenarios

### Scenario 1: Chlorella shipment from Japan

Test invoice, packing list, COA, health documentation, AWB, and original tracking.

### Scenario 2: Artemia shipment from Kazakhstan

Test batch-specific COA, origin certificate, health documentation, and correction cycles.

### Scenario 3: Fertilized salmon eggs

Test health certificate, disease declarations, transport dates, and strict readiness controls.

### Scenario 4: Seafood import

Test multiple product lines, inspection, laboratory progress, release, and warehouse delivery.

## Regression checks

- Existing Purchase functions remain operational.
- Existing Inventory functions remain operational.
- Existing contacts and chatter are not altered.
- No unrelated menus or permissions change.
