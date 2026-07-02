# -*- coding: utf-8 -*-

from odoo import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _customs_portal_group_ids(self):
        return {
            self.env.ref('base.group_portal').id,
        }

    @api.model
    def _customs_backend_group_ids(self):
        xmlids = [
            'base.group_user',
            'midvex_customs_op.group_customs_user',
            'midvex_customs_op.group_customs_approver',
            'midvex_customs_op.group_customs_manager',
            'midvex_customs_op.group_customs_admin',
        ]
        return {
            group.id
            for group in (self.env.ref(xmlid, raise_if_not_found=False) for xmlid in xmlids)
            if group
        }

    @api.model
    def _customs_groups_assign_portal(self, commands):
        portal_ids = self._customs_portal_group_ids()
        for command in commands or []:
            if not isinstance(command, (list, tuple)) or not command:
                continue
            if command[0] == 6 and portal_ids.intersection(command[2] or []):
                return True
            if command[0] == 4 and command[1] in portal_ids:
                return True
        return False

    @api.model
    def _sanitize_customs_portal_group_vals(self, vals, remove_existing=False):
        sanitized_vals = dict(vals)
        backend_ids = self._customs_backend_group_ids()
        for field_name in ('groups_id', 'group_ids'):
            commands = sanitized_vals.get(field_name)
            if not self._customs_groups_assign_portal(commands):
                continue
            cleaned_commands = []
            for command in commands:
                if not isinstance(command, (list, tuple)) or not command:
                    cleaned_commands.append(command)
                elif command[0] == 6:
                    cleaned_commands.append((6, 0, list(set(command[2] or []) - backend_ids)))
                elif command[0] == 4 and command[1] in backend_ids:
                    continue
                else:
                    cleaned_commands.append(command)
            if remove_existing:
                cleaned_commands += [(3, group_id) for group_id in backend_ids]
            sanitized_vals[field_name] = cleaned_commands
        return sanitized_vals

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._sanitize_customs_portal_group_vals(vals) for vals in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        vals = self._sanitize_customs_portal_group_vals(vals, remove_existing=True)
        return super().write(vals)
