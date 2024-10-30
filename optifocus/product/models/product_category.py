from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    barcode_prefix = fields.Char(string="Barcode Prefix")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('barcode_prefix'):
                vals['barcode_prefix'] = self.env['ir.sequence'].next_by_code('product.category')
        return super(ProductCategory, self).create(vals_list)
