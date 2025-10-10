# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.exceptions import ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def create(self, vals):
        if isinstance(vals, list):
            for value in vals:
                self._check_restrictions(value)
        else:
            self._check_restrictions(vals)
        return super(AccountInvoiceLine, self).create(vals)

    @api.multi
    def write(self, vals):
        self._check_restrictions(vals)
        return super(AccountInvoiceLine, self).write(vals)

    def _check_restrictions(self, vals):
        user = self.env.user
        if user._has_restriction_bypass() or not isinstance(vals, dict):
            return
        product_id = vals.get('product_id')
        if product_id:
            product = self.env['product.product'].browse(product_id)
            if product and not user._is_product_allowed(product):
                raise ValidationError(
                    "You are not allowed to use the product '%s' in invoices." % product.display_name
                )
        account_id = vals.get('account_id')
        if account_id:
            account = self.env['account.account'].browse(account_id)
            if account and not user._is_account_allowed(account):
                raise ValidationError(
                    "You are not allowed to use the account '%s' in invoices." % account.display_name
                )
