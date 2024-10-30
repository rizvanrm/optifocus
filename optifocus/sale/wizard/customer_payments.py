from odoo import api, fields, models, _
from odoo.tools import date_utils


class CustomerPayments(models.TransientModel):

    _name = 'customer.payments.wizard'
    _description = 'Customer Payments'

    date_from = fields.Date(string="Date From", required=True,
                            default=date_utils.start_of(date_utils.subtract(fields.date.today(), months=1), "month"))
    date_to = fields.Date(string="Date To", required=True,
                          default=date_utils.end_of(date_utils.subtract(fields.date.today(), months=1), "month"))
    invoice_type = fields.Selection([
        ('all', 'All'),
        ('retail', 'Retail'),
        ('member', 'Member'),
        ('claim', 'Claim'),
        ('wholesale', 'Wholesale')
    ], string="Invoice Type", default='retail')



    def generate_report(self):
        data = {
            'form_data': self.read()[0],
        }
        return self.env.ref('optifocus.customer_payments_report').report_action(self, data=data)

