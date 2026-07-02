# -*- coding: utf-8 -*-

import base64
import zipfile
from io import BytesIO

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class CustomsPortal(portal.CustomerPortal):

    def _portal_partner(self):
        return request.env.user.partner_id.commercial_partner_id

    def _is_related_partner(self, candidate):
        partner = self._portal_partner()
        return bool(candidate and candidate.commercial_partner_id == partner)

    def _is_supplier_operation(self, operation):
        return any(self._is_related_partner(partner) for partner in operation.supplier_ids)

    def _is_broker_operation(self, operation):
        return self._is_related_partner(operation.broker_id)

    def _check_operation_access(self, operation_id):
        operation = request.env['customs.operation'].browse(int(operation_id)).exists()
        if not operation:
            raise MissingError(_("Customs Operation not found."))
        if not (self._is_supplier_operation(operation) or self._is_broker_operation(operation)):
            raise AccessError(_("You do not have access to this Customs Operation."))
        return operation

    def _check_requirement_access(self, requirement_id):
        requirement = request.env['customs.document.requirement'].browse(int(requirement_id)).exists()
        if not requirement:
            raise MissingError(_("Document requirement not found."))
        self._check_operation_access(requirement.operation_id.id)
        return requirement

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'customs_operation_count' in counters:
            Operation = request.env['customs.operation']
            values['customs_operation_count'] = Operation.search_count([]) if Operation.has_access('read') else 0
        return values

    @http.route(['/my/customs', '/my/customs/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_customs_operations(self, page=1, sortby='date', **kw):
        values = self._prepare_portal_layout_values()
        Operation = request.env['customs.operation']
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
            'name': {'label': _('Reference'), 'order': 'name asc, id desc'},
            'eta': {'label': _('ETA'), 'order': 'planned_arrival_date asc, id desc'},
        }
        sortby = sortby if sortby in searchbar_sortings else 'date'
        operation_count = Operation.search_count([])
        pager = portal_pager(
            url='/my/customs',
            url_args={'sortby': sortby},
            total=operation_count,
            page=page,
            step=self._items_per_page,
        )
        operations = Operation.search(
            [],
            order=searchbar_sortings[sortby]['order'],
            limit=self._items_per_page,
            offset=pager['offset'],
        )
        request.session['my_customs_history'] = operations.ids[:100]
        values.update({
            'operations': operations,
            'page_name': 'customs_operations',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'default_url': '/my/customs',
        })
        return request.render('midvex_customs_op.portal_my_customs_operations', values)

    @http.route(['/my/customs/<int:operation_id>'], type='http', auth='user', website=True)
    def portal_customs_operation(self, operation_id, success=None, error=None, **kw):
        operation = self._check_operation_access(operation_id)
        values = self._prepare_portal_layout_values()
        values.update({
            'operation': operation,
            'is_supplier': self._is_supplier_operation(operation),
            'is_broker': self._is_broker_operation(operation),
            'page_name': 'customs_operation',
            'success': success,
            'error': error,
        })
        return request.render('midvex_customs_op.portal_customs_operation', values)

    @http.route(['/my/customs/document/<int:requirement_id>/upload'], type='http', auth='user', methods=['POST'], website=True)
    def portal_upload_customs_document(self, requirement_id, **post):
        requirement = self._check_requirement_access(requirement_id)
        operation = requirement.operation_id
        if not self._is_supplier_operation(operation):
            raise AccessError(_("Only suppliers assigned to this Customs Operation can upload supplier documents."))
        if requirement.responsible_party not in ('supplier', 'manufacturer'):
            raise AccessError(_("This document is not assigned to the supplier portal."))

        upload = request.httprequest.files.get('document_file')
        if not upload or not upload.filename:
            return request.redirect('/my/customs/%s?error=missing_file' % operation.id)

        attachment = request.env['ir.attachment'].sudo().create({
            'name': upload.filename,
            'datas': base64.b64encode(upload.read()),
            'res_model': 'customs.document.requirement',
            'res_id': requirement.id,
            'type': 'binary',
        })
        requirement.sudo().write({'attachment_ids': [(4, attachment.id)]})
        requirement.action_submit()
        return request.redirect('/my/customs/%s?success=document_uploaded' % operation.id)

    @http.route(['/my/customs/<int:operation_id>/broker/update'], type='http', auth='user', methods=['POST'], website=True)
    def portal_broker_update_customs(self, operation_id, **post):
        operation = self._check_operation_access(operation_id)
        if not self._is_broker_operation(operation):
            raise AccessError(_("Only the assigned broker can update customs declaration details."))

        allowed_statuses = dict(operation._fields['customs_status'].selection)
        vals = {}
        if post.get('customs_declaration_number'):
            vals['customs_declaration_number'] = post.get('customs_declaration_number')
        if post.get('customs_declaration_date'):
            vals['customs_declaration_date'] = post.get('customs_declaration_date')
        if post.get('customs_status') in allowed_statuses:
            vals['customs_status'] = post.get('customs_status')
        if vals:
            operation.sudo().write(vals)

        upload = request.httprequest.files.get('declaration_file')
        if upload and upload.filename:
            attachment = request.env['ir.attachment'].sudo().create({
                'name': upload.filename,
                'datas': base64.b64encode(upload.read()),
                'res_model': 'customs.operation',
                'res_id': operation.id,
                'type': 'binary',
            })
            operation.sudo().message_post(
                body=_("Customs declaration uploaded from the broker portal."),
                attachment_ids=[attachment.id],
            )
        return request.redirect('/my/customs/%s?success=broker_updated' % operation.id)

    @http.route(['/my/customs/<int:operation_id>/documents.zip'], type='http', auth='user', website=True)
    def portal_customs_document_zip(self, operation_id, **kw):
        operation = self._check_operation_access(operation_id)
        if not self._is_broker_operation(operation):
            raise AccessError(_("Only the assigned broker can download the approved document package."))

        complete_states = {
            'approved', 'original_issued', 'original_dispatched',
            'original_received', 'submitted_to_customs', 'accepted',
        }
        requirements = operation.document_requirement_ids.filtered(lambda r: r.state in complete_states and r.attachment_ids)
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
            for requirement in requirements:
                for attachment in requirement.attachment_ids:
                    if not attachment.datas:
                        continue
                    filename = '%s/%s' % (requirement.document_type_id.code or requirement.name, attachment.name)
                    archive.writestr(filename, base64.b64decode(attachment.datas))
        buffer.seek(0)
        headers = [
            ('Content-Type', 'application/zip'),
            ('Content-Disposition', 'attachment; filename="%s-documents.zip"' % operation.name.replace('/', '-')),
        ]
        return request.make_response(buffer.read(), headers=headers)
