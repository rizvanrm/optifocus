from odoo import api, fields, models, _
from odoo.tools import date_utils


class GroupSummaryStatement(models.TransientModel):

    _name = 'group.summary.statement.wizard'
    _description = 'Group Summary Statement Report'

    date_from = fields.Date(string="Date From", required=True,
                            default=date_utils.start_of(date_utils.subtract(fields.date.today(), months=1), "month"))
    date_to = fields.Date(string="Date To", required=True,
                          default=date_utils.end_of(date_utils.subtract(fields.date.today(), months=1), "month"))
    insurance_id = fields.Many2one('insurance.company', string='Insurance Company', required=True)

    def generate_report(self):
        provider_id=self.env['insurance.company'].search_read(domain=[('id','=',self.insurance_id.id )],fields=['provider_id'])
        provider_data=self.env['res.company'].search_read(domain=[('id','=',self.env.company.id )],fields=['name','company_registry','chi_id','mobile','email',])
        data = {
            'insurance_company': self.insurance_id.name,
            'insurance_id': self.insurance_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'provider_id': provider_id,
            'provider_data': provider_data
               }
        return self.env.ref('optifocus.group_summary_statement_report').report_action(self, data=data)

    def run_sql(self,qry):
        self._cr.execute(qry)
        _res = self._cr.dictfetchall()
        return _res



