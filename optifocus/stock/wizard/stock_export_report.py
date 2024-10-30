from odoo import api, fields, models, _
from odoo.tools import date_utils


class StockExport(models.TransientModel):

    _name = 'stock.export.report.wizard'
    _description = 'Stock Export Report'

    categ_ids=fields.Many2many('product.category', string='Product Categories')
    brand_ids = fields.Many2many('product.brand', string='Product Brands')
    model_ids = fields.Many2many('product.model1', string='Product Models')
    on_hand_qty = fields.Boolean('On Hand Qty',default=True)

    report_type = fields.Selection([
        ('detail', 'Detail'),
        ('summary', 'Summary'),
    ], string="Report Type", required=True,default='detail')
    group_by = fields.Selection([
        ('category', 'Product Category'),
        ('brand', 'Brand'),
        ('model', 'Model'),
    ], string="Group By",  required=True,default='category')

    export_format = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'XLSX'),
    ], string="Export Format", required=True, default='pdf')

    def generate_report(self):
        data = {
            'form_data': self.read()[0],
        }

        if self.export_format == 'pdf':
            return self.env.ref('optifocus.stock_pdf_report').report_action(self, data=data)
        else:
            return self.env.ref('optifocus.stock_xlsx_report').report_action(self, data=data)



