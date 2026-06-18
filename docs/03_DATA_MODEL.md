# Data Model Specification

## `customs.operation`

Main Customs File record.

### Core fields

- `name`
- `active`
- `company_id`
- `stage_id`
- `priority`
- `user_id`
- `supplier_ids`
- `broker_id`
- `forwarder_id`
- `carrier_id`
- `purchase_order_ids`
- `picking_ids`
- `operation_line_ids`
- `document_requirement_ids`

### Shipment fields

- `operation_type`
- `transport_mode`
- `incoterm_id`
- `origin_country_id`
- `departure_country_id`
- `destination_country_id`
- `customs_office`
- `container_number`
- `booking_number`
- `transport_document_number`

### Date fields

- `document_deadline`
- `planned_departure_date`
- `actual_departure_date`
- `planned_arrival_date`
- `actual_arrival_date`
- `planned_clearance_date`
- `actual_clearance_date`
- `warehouse_delivery_date`

### Customs fields

- `customs_declaration_number`
- `customs_declaration_date`
- `inspection_required`
- `laboratory_required`
- `inspection_date`
- `release_date`

### Computed controls

- `document_total`
- `document_approved_count`
- `document_missing_count`
- `document_rejected_count`
- `document_completion_percentage`
- `shipment_ready`
- `blocking_document_count`
- `blocking_reason_text`

## `customs.operation.line`

- `operation_id`
- `purchase_order_line_id`
- `product_id`
- `description`
- `customs_description`
- `hs_code`
- `country_of_origin_id`
- `manufacturer_id`
- `manufacturer_approval_number`
- `batch_number`
- `production_date`
- `expiry_date`
- `quantity`
- `uom_id`
- `net_weight`
- `gross_weight`
- `package_count`
- `package_type`
- `health_certificate_required`
- `analysis_required`
- `import_permit_required`
- `notes`

## `customs.document.type`

- `name`
- `code`
- `name_tr`
- `description`
- `default_responsible_party`
- `default_requirement_level`
- `original_normally_required`
- `sequence`
- `active`
- `company_id` or explicit shared configuration strategy

## `customs.document.requirement`

- `operation_id`
- `operation_line_id`
- `document_type_id`
- `name`
- `state`
- `requirement_level`
- `responsible_party`
- `responsible_user_id`
- `vendor_id`
- `requested_date`
- `deadline`
- `received_date`
- `issued_date`
- `expiry_date`
- `reviewed_date`
- `reviewed_by`
- `original_required`
- `original_issued`
- `original_dispatched`
- `original_received`
- `dispatch_date`
- `courier_name`
- `tracking_number`
- `attachment_ids`
- `rejection_reason`
- `review_notes`
- `version_number`
- `is_blocking`
- `is_overdue`
- `is_expired`
- `is_complete`

## Optional configurable stage model

`customs.stage`

- `name`
- `sequence`
- `fold`
- `is_closed`
- `is_cancelled`
- `company_id`
- role-transition restrictions where required

## Relationship guidance

- Use explicit company consistency checks.
- Avoid unrestricted cross-company Many2many relationships.
- Define deletion behavior deliberately.
- Preserve audit history for confirmed or closed files.
- Consider restricting deletion and using archive instead.
