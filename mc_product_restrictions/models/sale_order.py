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


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        self._check_order_line_commands(vals)
        order = super(SaleOrder, self).create(vals)
        order._check_existing_line_products()
        return order

    @api.multi
    def write(self, vals):
        self._check_order_line_commands(vals)
        result = super(SaleOrder, self).write(vals)
        self._check_existing_line_products()
        return result

    def _check_order_line_commands(self, vals):
        if not isinstance(vals, dict):
            return
        commands = vals.get('order_line')
        if not commands:
            return
        user = self.env.user
        if user._has_restriction_bypass() or not user._is_product_restriction_active():
            return
        product_model = self.env['product.product']
        for command in commands:
            if not isinstance(command, (list, tuple)) or len(command) < 3:
                continue
            command_type, _line_id, data = command
            if command_type not in (0, 1):
                continue
            if not isinstance(data, dict):
                continue
            product_id = data.get('product_id')
            if not product_id:
                continue
            product = product_model.browse(product_id)
            if product and not user._is_product_allowed(product):
                raise ValidationError(
                    "You are not allowed to use the product '%s' in sales orders." % product.display_name
                )

    @api.multi
    def _check_existing_line_products(self):
        user = self.env.user
        if user._has_restriction_bypass() or not user._is_product_restriction_active():
            return
        for order in self:
            unauthorized = order.order_line.filtered(lambda line: not user._is_product_allowed(line.product_id))
            if unauthorized:
                raise ValidationError(
                    "You are not allowed to use the product '%s' in sales orders." % unauthorized[0].product_id.display_name
                )
