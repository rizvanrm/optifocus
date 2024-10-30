from odoo import fields,Command, models, api, _

from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model_create_multi
    def create(self, vals_list):
        products = super().create(vals_list)

        for product in products:

            if not product.barcode:
                product.barcode=''
                if product.categ_id.barcode_prefix:
                    product.barcode = product.categ_id.barcode_prefix
                if product.brand_id.barcode_prefix:
                    product.barcode = product.barcode + product.brand_id.barcode_prefix
                product.barcode = product.barcode + self.env['ir.sequence'].next_by_code('product.barcode')

        return products

    # Be aware that the exact same function exists in product.template
    def action_open_quants(self):
        action = super().action_open_quants()
        hide_location = not self.user_has_groups('stock.group_stock_multi_locations')
        hide_lot = all(product.tracking == 'none' for product in self)
        self = self.with_context(
            hide_location=hide_location, hide_lot=hide_lot,
            no_at_date=True,search_default_internal_loc =True
        )
        # If user have rights to write on quant, we define the view as editable.
        if self.user_has_groups('stock.group_stock_manager'):
            self = self.with_context(inventory_mode=True)
            # Set default location id if multilocations is inactive
            if not self.user_has_groups('stock.group_stock_multi_locations'):
                user_company = self.env.company
                warehouse = self.env['stock.warehouse'].search(
                    [('company_id', '=', user_company.id)], limit=1
                )
                if warehouse:
                    self = self.with_context(default_location_id=warehouse.lot_stock_id.id)
        # Set default product id if quants concern only one product
        if len(self) == 1:
            self = self.with_context(
                default_product_id=self.id,
                single_product=True
            )
        else:
            self = self.with_context(product_tmpl_ids=self.product_tmpl_id.ids)
        action = self.env['stock.quant'].action_view_inventory_cust()
        # note that this action is used by different views w/varying customizations
        if not self.env.context.get('is_stock_report'):
            action['domain'] = [('product_id', 'in', self.ids)]
            action["name"] = _('Update Quantity')
        return action




