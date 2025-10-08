# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    restricted_user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='res_users_product_template_rel',
        column1='product_tmpl_id',
        column2='user_id',
        string='Restricted Users',
        help='Users allowed to access this product when product restrictions are enabled.')

    @api.model
    def create(self, vals):
        template = super(ProductTemplate, self).create(vals)
        template._add_creator_to_restricted_users(vals)
        return template

    def _add_creator_to_restricted_users(self, vals):
        if (
            self.env.user.has_group('mc_product_restrictions.group_product_restriction')
            and 'restricted_user_ids' not in vals
        ):
            self.sudo().write({'restricted_user_ids': [(4, self.env.user.id)]})
