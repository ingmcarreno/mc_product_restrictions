# -*- coding: utf-8 -*-
from odoo import api, fields, models


def _to_product_template(product):
    if not product:
        return product
    if product._name == 'product.template':
        return product
    if product._name == 'product.product':
        return product.product_tmpl_id
    return product


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

    @api.multi
    def _is_product_restriction_active(self):
        self.ensure_one()
        return bool(self.restricted_product_ids)

    @api.multi
    def _is_account_restriction_active(self):
        self.ensure_one()
        return bool(self.restricted_account_ids)

    @api.multi
    def _is_product_allowed(self, product):
        self.ensure_one()
        if self.env.su:
            return True
        if not product:
            return True
        if not self._is_product_restriction_active():
            return True
        template = _to_product_template(product)
        return template in self.restricted_product_ids

    @api.multi
    def _is_account_allowed(self, account):
        self.ensure_one()
        if self.env.su:
            return True
        if not account:
            return True
        if not self._is_account_restriction_active():
            return True
        return account in self.restricted_account_ids
