# Security and Access Specification

## Groups

### Customs User

Can:

- Create Customs Files
- Edit permitted operational fields
- Add product lines
- Upload documents
- Update shipment information
- Schedule activities

Cannot:

- Approve or reject regulated documents
- Change configuration
- Override controls
- Close or cancel restricted files

### Customs Document Approver

Inherits Customs User where appropriate.

Can:

- Mark documents under review
- Approve
- Reject
- Request correction

### Customs Manager

Can:

- Access all allowed company Customs Files
- Close and cancel files
- Override readiness with a required reason
- Review operational reporting

### Customs Administrator

Can:

- Configure stages
- Configure document types
- Maintain module configuration
- Access all permitted company records

## Rules

- Enforce permissions in Python and access-control records.
- Do not rely on button visibility.
- Test direct ORM and RPC attempts.
- Respect `allowed_company_ids`.
- Do not expose records from unauthorized companies.
- Validate company consistency between Customs File, PO, picking, supplier, and related records.
- Avoid broad `sudo()`.
- Restrict deletion of confirmed, shipped, cleared, delivered, or closed records.
- Prefer archive where historical preservation matters.
- Log manager overrides.
- Record approver, action date, and reason.
