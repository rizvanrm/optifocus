from odoo import _, api, Command, fields, models
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    approval_code = fields.Char(string="Approval Code")

    @api.constrains('approval_code')
    def _constrains_approval_code(self):
        for record in self:
            if record.journal_id.type == 'bank' and not record.approval_code:
                raise ValidationError("Invalid field: Approval Code")


