from odoo import api, fields, models


class StockXLSXReportAB(models.AbstractModel):
    _name = 'report.optifocus.report_stock_xlsx'
    _inherit='report.report_xlsx.abstract'
    _description = 'Stock result as XLSX.'

    def generate_xlsx_report(self, workbook, data,product_ids1):

        domain = []
        categ_ids = data.get('form_data').get('categ_ids')
        brand_ids = data.get('form_data').get('brand_ids')
        on_hand_qty = data.get('form_data').get('on_hand_qty')

        if categ_ids:
            domain += [('categ_id', 'in', categ_ids)]
        if brand_ids:
            domain += [('brand_id', 'in', brand_ids)]
        if on_hand_qty:
            domain += [('qty_available', '!=', 0)]

        product_ids = self.env['product.product'].search(domain).sorted(key=lambda r: r.name)

        report_name = 'Products'
        sheet=workbook.add_worksheet(report_name[:31])
        bold=workbook.add_format({'bold':True})
        sheet.write(0,0,'Barcode',bold)
        sheet.write(0, 1,'Product Name', bold)
        sheet.write(0, 2, 'Product Category', bold)
        sheet.write(0, 3, 'Brand', bold)
        sheet.write(0, 4, 'Model', bold)
        sheet.write(0, 5, 'Sales Price', bold)
        sheet.write(0, 6, 'Quantity on Hand', bold)
        sheet.write(0, 7, 'Attribute Values', bold)

        row=0

        for product_id in product_ids:

            row += 1
            sheet.write(row,0,product_id.barcode)
            sheet.write(row, 1, product_id.name)
            sheet.write(row, 2, product_id.categ_id.name )
            sheet.write(row, 3,  product_id.brand_id.name)
            sheet.write(row, 4,product_id.model1_id.name)
            sheet.write(row, 5, product_id.lst_price)
            sheet.write(row, 6, product_id.qty_available )
            attribute_value_id=""
            for product_attribute_value_id in product_id.product_template_attribute_value_ids:
                attribute_value_id = attribute_value_id + ("" if attribute_value_id =="" else ", ")+  product_attribute_value_id.display_name
            sheet.write(row, 7, attribute_value_id)




