# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    restricted_product_ids = fields.Many2many(
        comodel_name='product.template',
        relation='res_users_product_template_rel',
        column1='user_id',
        column2='product_tmpl_id',
        string='Allowed Products',
        help='Products that this user is allowed to access.')

    restricted_account_ids = fields.Many2many(
        comodel_name='account.account',
        relation='res_users_account_account_rel',
        column1='user_id',
        column2='account_id',
        string='Allowed Accounts',
        help='Accounts that this user is allowed to access.')

    @api.model
    def create(self, vals):
        users = super(ResUsers, self).create(vals)
        users._sync_restriction_group_membership()
        return users

    @api.multi
    def write(self, vals):
        result = super(ResUsers, self).write(vals)
        self._sync_restriction_group_membership()
        return result

    @api.multi
    def _sync_restriction_group_membership(self):
        group = self.env.ref('mc_product_restrictions.group_product_restriction', raise_if_not_found=False)
        if not group:
            return

        to_add = self.browse()
        to_remove = self.browse()
        for user in self:
            if user.restricted_product_ids or user.restricted_account_ids:
                to_add |= user
            else:
                to_remove |= user

        if to_add:
            group.sudo().write({'users': [(4, uid) for uid in to_add.ids]})
        if to_remove:
            group.sudo().write({'users': [(3, uid) for uid in to_remove.ids]})
