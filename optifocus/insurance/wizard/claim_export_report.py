from odoo import api, fields, models, _
from odoo.tools import date_utils


class ClaimExport(models.TransientModel):

    _name = 'claim.export.report.wizard'
    _description = 'Claim Export Report'

    insurance_id = fields.Many2one('insurance.company', string='Insurance Company', required=True)
    date_from = fields.Date(string="Date From", required=True,
                            default=date_utils.start_of(date_utils.subtract(fields.date.today(), months=1), "month"))
    date_to = fields.Date(string="Date To", required=True,
                          default=date_utils.end_of(date_utils.subtract(fields.date.today(), months=1), "month"))


    def generate_report(self):
        data = {
            'form_data': self.read()[0],
        }
        return self.env.ref('optifocus.claim_report').report_action(self, data=data)



