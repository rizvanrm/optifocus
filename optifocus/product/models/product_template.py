from odoo import fields,Command, models, api
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('product.brand', string='Brand')
    model1_id = fields.Many2one('product.model1', string='Model',domain="[('brand_id', '=', brand_id)]")
    barcode = fields.Char( string='Barcode')
    insurance_sale_ok = fields.Boolean('Can be Sold in Insurance', default=True)

    max_retail_line_discount=fields.Float(string="Retail (%)",digits='Discount')
    max_wholesale_line_discount = fields.Float(string="Wholesale (%)",digits='Discount')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:

            if not vals.get('barcode'):
                vals['barcode'] = ''
                categ_id = self.env['product.category'].browse(vals.get('categ_id'))
                brand_id = self.env['product.brand'].browse(vals.get('brand_id'))

                if categ_id.barcode_prefix:
                    vals['barcode'] = categ_id.barcode_prefix
                else:
                    ''
                if brand_id.barcode_prefix:
                    vals['barcode'] = vals['barcode']  + brand_id.barcode_prefix
                else:
                    ''
                vals['barcode'] = vals['barcode'] + self.env['ir.sequence'].next_by_code('product.barcode')
        return super(ProductTemplate, self).create(vals_list)

    @api.onchange('brand_id')
    def onchange_brand_id(self):
        self.model1_id = None


    @api.onchange('brand_id','model1_id','attribute_line_ids')
    def onchange_auto_product_name(self):
        self.name = (self.brand_id.name if self.brand_id.name else '') +  (' , ' if self.brand_id.name and self.model1_id.name else '' )+ (self.model1_id.name if self.model1_id.name else '')
        for attribute_line_id in self.attribute_line_ids:
            if len(attribute_line_id.value_ids) == 1:
                self.name = self.name +   (' , ' if self.name and attribute_line_id.value_ids.name else '' ) + attribute_line_id.value_ids.name

    @api.constrains('categ_id')
    def _constrains_brand_model(self):

        if not self.brand_id and self.categ_id.id in (self.env.ref('optifocus.product_category_accessory').id,
                                                        self.env.ref('optifocus.product_category_contactlens').id,
                                                        self.env.ref('optifocus.product_category_frame').id,
                                                        self.env.ref('optifocus.product_category_powerlens').id,
                                                        self.env.ref('optifocus.product_category_sunglass').id,
                                                        self.env.ref('optifocus.product_category_sunlens').id,
                                                        self.env.ref('optifocus.product_category_solution').id):
            raise ValidationError("Invalid field: Brand")

        if not self.model1_id and self.categ_id.id in (self.env.ref('optifocus.product_category_accessory').id,
                                                        self.env.ref('optifocus.product_category_contactlens').id,
                                                        self.env.ref('optifocus.product_category_frame').id,
                                                        self.env.ref('optifocus.product_category_powerlens').id,
                                                        self.env.ref('optifocus.product_category_sunglass').id,
                                                        self.env.ref('optifocus.product_category_sunlens').id,
                                                        self.env.ref('optifocus.product_category_solution').id):
            raise ValidationError("Invalid field: Model")

