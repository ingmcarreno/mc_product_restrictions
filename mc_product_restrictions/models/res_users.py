# -*- coding: utf-8 -*-
from odoo import fields, models


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
