from odoo import models, fields,api
from odoo.exceptions import UserError, ValidationError


class SaleOrderDiscount(models.TransientModel):
    _name = "sale.order.discount"
    _description = "Sale Order Discount"
    order_id = fields.Many2one('sale.order', default=lambda self: self.env.context.get('active_id'), required=True)
    discount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percentage', '%'),
    ], string="Discount Type", default='fixed',required=True)
    discount=fields.Float(string="Discount")

    def action_apply(self):
        user_id = self.env['res.users'].browse(self.env.context.get('uid'))

        order_id=self.env['sale.order'].browse(self.env.context.get('active_id'))
        global_discount_exist=False

        product_id = self.env['ir.config_parameter'].sudo().get_param('optifocus.default_global_discount_product_id')

        if not product_id:
            raise ValidationError("Please set global discount product in sale configuration.")

        product_id = self.env['product.product'].browse(int(product_id)).exists()
        discount_value = self._compute_discount(product_id)

        for line in order_id.order_line:
            if line.product_id==product_id:
                global_discount_exist = True
                line.update({
                    'product_id': product_id.id,
                    'price_unit': discount_value,
                    'order_id': order_id
                })
                break

        if not global_discount_exist:
            self.env['sale.order.line'].create({
                'product_id': product_id.id,
                'price_unit': discount_value,
                'order_id': self.env.context.get('active_id')
            })

    def _compute_discount(self,product_id):
        user_id = self.env['res.users'].browse(self.env.context.get('uid'))
        order_id = self.env['sale.order'].browse(self.env.context.get('active_id'))
        amount_untaxed = 0
        discount_value = 0


        for line in order_id.order_line:
            if line.product_id.id!=product_id.id :
                amount_untaxed+=line.price_subtotal

        if self.discount <= 0:
            raise ValidationError(
                "Global Discount must be positive and greater than 0.")

        if self.discount_type == "fixed":
            if self.discount < 1 or  self.discount > user_id.max_global_discount_percentage * amount_untaxed / 100   :
                raise ValidationError("Max allowed Global Discount is upto (" + str(user_id.max_global_discount_percentage ) + "%)")
            else:
                discount_value = self.discount
        else:
            if self.discount < 1 or self.discount > user_id.max_global_discount_percentage:
                raise ValidationError(
                    "Max allowed Global Discount is upto (" + str(user_id.max_global_discount_percentage) + "%)")
            else:
                discount_value = amount_untaxed * self.discount / 100

        return discount_value*-1