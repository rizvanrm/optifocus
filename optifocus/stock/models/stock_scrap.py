from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class StockScrap(models.Model):

    _inherit = ['stock.scrap']
    employee_id = fields.Many2one('hr.employee', string='Employee',  required=True,
                                 states={'done': [('readonly', True)]})
    product_barcode_id = fields.Char(related='product_id.barcode', string='Barcode')
    product_standard_price_id = fields.Float(related='product_id.standard_price', string='Cost')
    total = fields.Float(string='Total',compute='_compute_total')

    @api.depends('scrap_qty','product_id')
    def _compute_total(self):
        for rec in self:
            rec.total=rec.scrap_qty*rec.product_standard_price_id


