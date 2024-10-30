from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class ProductBrand(models.Model):
    _name = "product.brand"
    _description = "Product Band"
    _rec_name = 'complete_name'

    name = fields.Char(string="Brand", required=True)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', recursive=True,
        store=True)
    short_name = fields.Char(string="Short Name")
    parent_brand = fields.Many2one('product.brand', string='Parent Brand')
    barcode_prefix=fields.Char(string="Barcode Prefix" )

    model_ids = fields.One2many('product.model1', 'brand_id', string='Model')

    # Constraint - at least one Child Record required
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals['barcode_prefix']:
                vals['barcode_prefix'] =self.env['ir.sequence'].next_by_code('product.brand')
        return super(ProductBrand, self).create(vals_list)

    @api.constrains('model_ids')
    def _constrains_model_ids(self):
        if not self.model_ids or len(self.model_ids) == 0:
            raise ValidationError("At least one Model per Brand is a must.")

    @api.depends('name', 'parent_brand.complete_name')
    def _compute_complete_name(self):
        for brand in self:
            if brand.parent_brand:
                brand.complete_name = '%s / %s' % (brand.parent_brand.complete_name, brand.name)
            else:
                brand.complete_name = brand.name

    # Constraint Unique Record
    _sql_constraints = [
        ('brand_uniq', 'unique (name)', 'Brand must be unique.'),
    ]


class BrandModel(models.Model):
    _name = "product.model1"
    _description = "Brand Models"

    name = fields.Char(string="Model", required=True)
    short_name = fields.Char(string="Short Name")
    brand_id = fields.Many2one('product.brand', string='Brand')

    # Constraint Unique Line Record
    _sql_constraints = [('brand_model_uniq', 'unique (name,brand_id)',
                         'A Model name must be unique per Brand.')
                        ]
