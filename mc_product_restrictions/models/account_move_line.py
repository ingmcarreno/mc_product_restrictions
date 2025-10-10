# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def create(self, vals):
        if isinstance(vals, list):
            for value in vals:
                self._check_account(value)
        else:
            self._check_account(vals)
        return super(AccountMoveLine, self).create(vals)

    @api.multi
    def write(self, vals):
        self._check_account(vals)
        return super(AccountMoveLine, self).write(vals)

    def _check_account(self, vals):
        user = self.env.user
        if user._has_restriction_bypass() or not isinstance(vals, dict):
            return
        account_id = vals.get('account_id')
        if not account_id:
            return
        account = self.env['account.account'].browse(account_id)
        if account and not user._is_account_allowed(account):
            raise ValidationError(
                "You are not allowed to use the account '%s' in journal entries." % account.display_name
            )
