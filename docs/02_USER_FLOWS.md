# User Flows

## 1. Create a Customs File

1. Purchasing or logistics user opens Customs Operations.
2. User creates a Customs File.
3. Odoo assigns a unique reference.
4. User selects company and responsible employee.
5. User links one or more purchase orders.
6. User adds or imports product lines.
7. User assigns supplier, broker, forwarder, and shipment details.
8. User saves the file.
9. Odoo records the creation in chatter.

## 2. Add and request documents

1. User opens the Documents tab.
2. User adds required document records.
3. User assigns requirement level, responsible party, vendor, and deadline.
4. User marks documents as requested.
5. Chatter records the request status and date.
6. An activity may be scheduled for follow-up.

## 3. Receive and review a document

1. User uploads one or more attachments.
2. Document status changes to Draft Received.
3. Approver marks it Under Review.
4. Approver either:
   - Approves it
   - Requests correction
   - Rejects it
5. Correction or rejection requires a reason.
6. Chatter records the action and responsible approver.

## 4. Track original documents

1. User marks whether an original is required.
2. When issued, user records issue date.
3. When dispatched, user records courier, tracking number, and dispatch date.
4. When received, user records receipt.
5. Shipment-readiness calculation uses the original status.

## 5. Approve shipment readiness

1. Odoo calculates readiness.
2. Odoo lists blocking reasons.
3. Users resolve missing or rejected documents.
4. Readiness becomes true automatically when requirements are satisfied.
5. Managers may override only with a reason.
6. Override is logged.

## 6. Track departure and arrival

1. Logistics records planned departure and arrival.
2. Logistics records actual departure.
3. Operation moves to Shipped.
4. Logistics records actual arrival.
5. Operation moves to Arrived.

## 7. Customs clearance

1. Customs declaration number and date are recorded.
2. Inspection or laboratory requirement is recorded.
3. Relevant documents are uploaded.
4. Release date and customs-cleared status are recorded.
5. Goods are delivered to the warehouse.
6. Warehouse delivery date is recorded.
7. Manager closes the Customs File after validations pass.
