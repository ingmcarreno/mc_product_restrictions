# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    restricted_user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='res_users_account_account_rel',
        column1='account_id',
        column2='user_id',
        string='Restricted Users',
        help='Users allowed to access this account when account restrictions are enabled.')

    @api.model
    def create(self, vals):
        account = super(AccountAccount, self).create(vals)
        account._add_creator_to_restricted_users(vals)
        return account

    def _add_creator_to_restricted_users(self, vals):
        if (
            self.env.user.has_group('mc_product_restrictions.group_product_restriction')
            and 'restricted_user_ids' not in vals
        ):
            self.sudo().write({'restricted_user_ids': [(4, self.env.user.id)]})
