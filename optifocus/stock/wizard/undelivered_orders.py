from odoo import api, fields, models, _
from odoo.tools import date_utils


class UnDeliveredOrders(models.TransientModel):

    _name = 'stock.picking.wizard'
    _description = 'Undelivered Orders'

    date_from = fields.Date(string="Date From", required=True,
                            default=date_utils.start_of(date_utils.subtract(fields.date.today(), months=1), "month"))
    date_to = fields.Date(string="Date To", required=True,
                          default=date_utils.end_of(date_utils.subtract(fields.date.today(), months=1), "month"))
    sale_type = fields.Selection([
        ('retail', 'Retail'),
        ('insurance', 'Insurance'),
        ('wholesale', 'Wholesale')
    ], string="Sale Type", default='retail')

    partially_or_not_paid = fields.Boolean('Partially / Not Paid Orders')



    def generate_report(self):
        data = {
            'form_data': self.read()[0],
        }
        return self.env.ref('optifocus.undelivered_orders_report').report_action(self, data=data)

