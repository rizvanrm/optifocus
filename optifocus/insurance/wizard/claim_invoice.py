from odoo import api, fields, models, _
from odoo.tools import date_utils


class ClaimInvoice(models.TransientModel):

    _name = 'claim.invoice.wizard'
    _description = 'Claim Invoice Report'

    date_from = fields.Date(string="Date From", required=True,
                            default=date_utils.start_of(date_utils.subtract(fields.date.today(), months=1), "month"))
    date_to = fields.Date(string="Date To", required=True,
                          default=date_utils.end_of(date_utils.subtract(fields.date.today(), months=1), "month"))
    insurance_id = fields.Many2one('insurance.company', string='Insurance Company', required=True)

    def generate_report(self):
        data = {
            'form_data': self.read()[0],
        }
        return self.env.ref('optifocus.claim_invoice_report').report_action(self, data=data)

