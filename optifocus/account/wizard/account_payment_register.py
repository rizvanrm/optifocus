# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools import frozendict


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    approval_code = fields.Char(string="Approval Code")

    def action_create_payments(self):
        for record in self:
            if record.journal_id.type == 'bank' and not record.approval_code :
                raise ValidationError("Invalid field: Approval Code")
        result = super(AccountPaymentRegister, self).action_create_payments()
        return result

    def _create_payment_vals_from_wizard(self, batch_result):

        result = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        result['approval_code'] = self.approval_code
        return result
