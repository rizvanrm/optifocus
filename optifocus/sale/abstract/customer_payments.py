from odoo import api, fields, models


class CustomerPaymentsAB(models.AbstractModel):
    _name = 'report.optifocus.report_customer_payments'
    _description = 'Customer Payments'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []

        date_from = data.get('form_data').get('date_from')
        date_to = data.get('form_data').get('date_to')
        invoice_type = data.get('form_data').get('invoice_type')

        domain += [('date', '>=', date_from)]
        domain += [('date', '<=', date_to)]
        domain += [('state', '=', 'posted')]
        domain += [('partner_type', '=', 'customer')]

        payment_ids = self.env['account.payment'].search(domain,order='id desc')
        payment_id = self.env['account.payment'].search_read([('id','=',9)])
        invoice_id = self.env['account.move'].search_read([('id', '=', 30)])
        return {
            'request': self,
            'payment_ids':payment_ids,
            'invoice_type':invoice_type,
            'date_from':date_from,
            'date_to': date_to,
        }

