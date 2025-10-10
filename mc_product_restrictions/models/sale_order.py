# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        if isinstance(vals, list):
            for value in vals:
                self._check_allowed_product(value)
        else:
            self._check_allowed_product(vals)
        return super(SaleOrderLine, self).create(vals)

    @api.multi
    def write(self, vals):
        self._check_allowed_product(vals)
        return super(SaleOrderLine, self).write(vals)

    def _check_allowed_product(self, vals):
        user = self.env.user
        if user._has_restriction_bypass():
            return
        if not isinstance(vals, dict):
            return
        product_id = vals.get('product_id')
        if not product_id:
            return
        product = self.env['product.product'].browse(product_id)
        if product and not user._is_product_allowed(product):
            raise ValidationError(
                "You are not allowed to use the product '%s' in sales orders." % product.display_name
            )
