
from collections import defaultdict

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderDiscount(models.TransientModel):
    _inherit = 'sale.order.discount'

    def _create_discount_lines(self):
        """Create SOline(s) according to wizard configuration"""
        self.ensure_one()
        discount_product = self._get_discount_product()
        user_id = self.env['res.users'].browse(self.env.context.get('uid'))
        global_discount_exist = False
        amount_total=0

        total_price_per_tax_groups = defaultdict(float)

        for line in self.sale_order_id.order_line:
            if not line.product_uom_qty or not line.price_unit or line.product_id == discount_product:
                continue

            total_price_per_tax_groups[line.tax_id] += (line.price_unit * line.product_uom_qty) - (
                    line.price_unit * line.product_uom_qty) * line.discount / 100

        for taxes, subtotal in total_price_per_tax_groups.items():
            amount_total=subtotal


        if self.discount_type == 'amount':


            vals_list = [
                self._prepare_discount_line_values(
                    product=discount_product,
                    amount=self.discount_amount,
                    taxes=self.tax_ids,
                )
            ]
        else:  # so_discount

            if not total_price_per_tax_groups:
                # No valid lines on which the discount can be applied
                return
            elif len(total_price_per_tax_groups) == 1:
                # No taxes, or all lines have the exact same taxes
                taxes = next(iter(total_price_per_tax_groups.keys()))
                subtotal = total_price_per_tax_groups[taxes]

                vals_list = [{
                    **self._prepare_discount_line_values(
                        product=discount_product,
                        amount=subtotal * self.discount_percentage,
                        taxes=taxes,
                        description=_(
                            "Discount %(percent)s%%",
                            percent=self.discount_percentage * 100
                        ),
                    ),
                }]
            else:
                vals_list = [
                    self._prepare_discount_line_values(
                        product=discount_product,
                        amount=subtotal * self.discount_percentage,
                        taxes=taxes,
                        description=_(
                            "Discount %(percent)s%%"
                            "- On products with the following taxes %(taxes)s",
                            percent=self.discount_percentage * 100,
                            taxes=", ".join(taxes.mapped('name'))
                        ),
                    ) for taxes, subtotal in total_price_per_tax_groups.items()
                ]



        if  (self.discount_type == "so_discount" and self.discount_percentage <= 0 )or (self.discount_type == "amount" and  self.discount_amount <=0):
            raise ValidationError(
                "Discount must be positive and greater than 0.")

        if self.discount_type == "amount":
            if self.discount_amount > user_id.max_global_discount_percentage * (amount_total) / 100:
                raise ValidationError(
                    "Max allowed Global Discount is upto (" + str(user_id.max_global_discount_percentage) + "%)")
        if self.discount_type == "so_discount":
            if self.discount_percentage*100 > user_id.max_global_discount_percentage:
                raise ValidationError(
                    "Max allowed Global Discount is upto (" + str(user_id.max_global_discount_percentage) + "%)")

        for line in self.sale_order_id.order_line:
            if line.product_id == discount_product:
                global_discount_exist = True
                result = line.update(vals_list[0])
                break

        if not global_discount_exist:
            result=self.env['sale.order.line'].create(vals_list)

        return result

    def action_apply_discount(self):
        self.ensure_one()
        self = self.with_company(self.company_id)
        line_discount_flag=False

        if self.discount_type == 'sol_discount':
            lines_to_update = self.sale_order_id.order_line.filtered(
                lambda line: line.product_id != self._get_discount_product() )

            for line in lines_to_update:
                if self.sale_order_id.sale_type == "retail":
                    if self.discount_percentage*100 > line.product_template_id.max_retail_line_discount:
                        line_discount_flag = True
                        break

                elif self.sale_order_id.sale_type == "wholesale":
                    if self.discount_percentage*100 > line.product_template_id.max_wholesale_line_discount:
                        line_discount_flag = True
                        break

            if line_discount_flag:
                raise ValidationError(
                    "The discount applied exceeds the maximum allowed discount for one or more products.")
            else:
                lines_to_update.update({'discount': self.discount_percentage*100})

        else:
            self._create_discount_lines()
