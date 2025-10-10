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


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def create(self, vals):
        self._check_invoice_line_commands(vals)
        invoice = super(AccountInvoice, self).create(vals)
        invoice._check_existing_invoice_lines()
        return invoice

    @api.multi
    def write(self, vals):
        self._check_invoice_line_commands(vals)
        result = super(AccountInvoice, self).write(vals)
        self._check_existing_invoice_lines()
        return result

    def _check_invoice_line_commands(self, vals):
        if not isinstance(vals, dict):
            return
        commands = vals.get('invoice_line_ids')
        if not commands:
            return
        user = self.env.user
        bypass_products = user._has_restriction_bypass() or not user._is_product_restriction_active()
        bypass_accounts = user._has_restriction_bypass() or not user._is_account_restriction_active()
        product_model = self.env['product.product']
        account_model = self.env['account.account']
        for command in commands:
            if not isinstance(command, (list, tuple)) or len(command) < 3:
                continue
            command_type, _line_id, data = command
            if command_type not in (0, 1):
                continue
            if not isinstance(data, dict):
                continue
            product_id = data.get('product_id')
            if product_id and not bypass_products:
                product = product_model.browse(product_id)
                if product and not user._is_product_allowed(product):
                    raise ValidationError(
                        "You are not allowed to use the product '%s' in invoices." % product.display_name
                    )
            account_id = data.get('account_id')
            if account_id and not bypass_accounts:
                account = account_model.browse(account_id)
                if account and not user._is_account_allowed(account):
                    raise ValidationError(
                        "You are not allowed to use the account '%s' in invoices." % account.display_name
                    )

    @api.multi
    def _check_existing_invoice_lines(self):
        user = self.env.user
        bypass_products = user._has_restriction_bypass() or not user._is_product_restriction_active()
        bypass_accounts = user._has_restriction_bypass() or not user._is_account_restriction_active()
        for invoice in self:
            if not bypass_products:
                unauthorized_product = invoice.invoice_line_ids.filtered(
                    lambda line: not user._is_product_allowed(line.product_id)
                )
                if unauthorized_product:
                    raise ValidationError(
                        "You are not allowed to use the product '%s' in invoices." % unauthorized_product[0].product_id.display_name
                    )
            if not bypass_accounts:
                unauthorized_account = invoice.invoice_line_ids.filtered(
                    lambda line: not user._is_account_allowed(line.account_id)
                )
                if unauthorized_account:
                    raise ValidationError(
                        "You are not allowed to use the account '%s' in invoices." % unauthorized_account[0].account_id.display_name
                    )
        account_id = vals.get('account_id')
        if account_id:
            account = self.env['account.account'].browse(account_id)
            if account and not user._is_account_allowed(account):
                raise ValidationError(
                    "You are not allowed to use the account '%s' in invoices." % account.display_name
                )
