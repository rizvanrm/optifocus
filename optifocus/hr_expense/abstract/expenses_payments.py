from odoo import api, fields, models


class ExpensesPaymentsAB(models.AbstractModel):
    _name = 'report.optifocus.report_expenses_payments'
    _description = 'Expenses Payments'

    @api.model
    def _get_report_values(self, docids, data=None):

        date_from = data.get('form_data').get('date_from')
        date_to = data.get('form_data').get('date_to')
        employee_id = data.get('form_data').get('employee_id')
        payment_mode = data.get('form_data').get('payment_mode')


        domain = []
        domain += [('date', '>=', date_from)]
        domain += [('date', '<=', date_to)]
        domain += [('state', '=', 'paid')]
        domain += [('partner_type', '=', 'supplier')]

        payment_ids = self.env['account.payment'].search(domain, order='id desc')

        return {
            'request': self,
            'payment_ids':payment_ids,
            'employee_id': employee_id,
            'payment_mode': payment_mode,
            'date_from':date_from,
            'date_to': date_to,
        }

