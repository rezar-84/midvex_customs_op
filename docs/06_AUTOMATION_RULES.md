# Automation Rules

## MVP automations

### Reference generation

Generate:

`CUS/YYYY/NNNN`

### Readiness recalculation

Recalculate when:

- Document requirement is created or removed
- Document status changes
- Attachment changes
- Expiry date changes
- Original-required flag changes
- Original-issued state changes
- Required shipment information changes

### Overdue detection

A document is overdue when:

- Deadline is before today
- It is not complete
- It is not Not Applicable

### Expiry detection

A document is expired when:

- Expiry date is before today
- It is not Not Applicable

### Stage and chatter

Track important changes:

- Stage
- Responsible user
- Broker
- Planned and actual departure
- Planned and actual arrival
- Declaration number
- Document status
- Deadline
- Approval or rejection

## Future automations

- Generate requirements from templates
- Vendor email reminders
- Escalation activities
- Certificate expiry warnings
- Original-document dispatch reminders
- Arrival and customs-delay warnings
- Supplier and broker portal notifications
