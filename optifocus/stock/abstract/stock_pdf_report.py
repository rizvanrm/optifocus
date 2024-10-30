from odoo import api, fields, models


class StockPDFReportAB(models.AbstractModel):
    _name = 'report.optifocus.report_stock_pdf'
    _description = 'Stock result as PDF.'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []

        categ_ids = data.get('form_data').get('categ_ids')
        brand_ids = data.get('form_data').get('brand_ids')
        model_ids = data.get('form_data').get('model_ids')
        on_hand_qty = data.get('form_data').get('on_hand_qty')
        group_by = data.get('form_data').get('group_by')
        report_type = data.get('form_data').get('report_type')

        if categ_ids:
            domain += [('categ_id', 'in', categ_ids)]
        if brand_ids:
            domain += [('brand_id', 'in', brand_ids)]
        if model_ids:
            domain += [('model1_id', 'in', model_ids)]
        if on_hand_qty:
            domain += [('qty_available', '!=', 0)]

        product_ids=self.env['product.product'].search(domain).sorted(key=lambda r: r.name)
        categ_ids=product_ids.categ_id.sorted(key=lambda r: r.name)
        brand_ids = product_ids.brand_id.sorted(key=lambda r: r.name)
        model_ids = product_ids.model1_id.sorted(key=lambda r: r.name)

        return {
            'product_ids':product_ids,
            'categ_ids': categ_ids,
            'brand_ids': brand_ids,
            'model_ids': model_ids,
            'group_by': group_by,
            'report_type': report_type
        }

