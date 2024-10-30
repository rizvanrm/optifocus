from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    max_global_discount_percentage = fields.Float(string="Global Discount (%)", digits='Discount')

    @api.constrains('max_global_discount_percentage')
    def _constrains_max_global_discount_percentage(self):
        if self.max_global_discount_percentage < 0.0 or self.max_global_discount_percentage > 100.0:
            raise ValidationError(_('Global Discount percentages must be between 0 and 100.'))


