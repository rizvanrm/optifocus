from odoo import api, fields, models


class UndeliveredOrdersAB(models.AbstractModel):
    _name = 'report.optifocus.report_undelivered_orders'
    _description = 'Undelivered Orders'


    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []

        date_from = data.get('form_data').get('date_from')
        date_to = data.get('form_data').get('date_to')
        sale_type = data.get('form_data').get('sale_type')
        partially_or_not_paid = data.get('form_data').get('partially_or_not_paid')


        domain += [('date_order', '>=', date_from)]
        domain += [('date_order', '<=', date_to)]
        domain += [('delivery_status', '!=', 'full')]
        domain += [('state', '=', 'sale')]

        if sale_type :
            domain += [('sale_type', '=', sale_type)]

        order_ids=self.env['sale.order'].search(domain)
        invoice_id = self.env['account.move'].search_read([('id','=',14)])
        print(invoice_id)

        return {
            'request': self,
            'order_ids':order_ids,
            'date_from':date_from,
            'date_to': date_to,
            'partially_or_not_paid':partially_or_not_paid
        }

