from odoo import models, fields, api,_
search_default_my_company=True
class StockQuant(models.Model):

    _inherit = ['stock.quant']

    barcode = fields.Char(related='product_id.barcode')
    product_categ_id = fields.Many2one(related='product_tmpl_id.categ_id',store=True)
    brand_id = fields.Many2one(related='product_tmpl_id.brand_id',store=True)


    list_price = fields.Float(related='product_tmpl_id.list_price')
    value = fields.Float(compute='_compute_values',string='On Hand Value')
    inventory_value = fields.Float(compute='_compute_values',string='Counted Value')
    inventory_diff_value = fields.Float(compute='_compute_values',string='Difference Value')

    @api.model
    def action_view_inventory_cust(self):
        global search_default_my_company
        search_default_my_company=False
        action = self.action_view_inventory()
        search_default_my_company = True
        return action


    @api.depends('list_price', 'quantity','inventory_quantity','inventory_diff_quantity')
    def _compute_values(self):

        for rec in self:
            rec.value = rec.quantity * rec.list_price
            rec.inventory_value = rec.inventory_quantity * rec.list_price
            rec.inventory_diff_value = rec.inventory_diff_quantity * rec.list_price

    @api.model
    def action_view_inventory(self):
        global search_default_my_company
        action = super().action_view_inventory()
        """ Similar to _get_quants_action except specific for inventory adjustments (i.e. inventory counts). """
        self = self._set_view_context()
        self._quant_tasks()

        ctx = dict(self.env.context or {})
        ctx['no_at_date'] = True

        ctx['search_default_my_company'] = search_default_my_company

        # if self.user_has_groups('stock.group_stock_user') and not self.user_has_groups('stock.group_stock_manager'):
        #     ctx['search_default_my_count'] = True
        action = {
            'name': _('Inventory Adjustments'),
            'view_mode': 'list',
            'view_id': self.env.ref('stock.view_stock_quant_tree_inventory_editable').id,
            'res_model': 'stock.quant',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('location_id.usage', 'in', ['internal', 'transit'])],
            'help': """
                <p class="o_view_nocontent_smiling_face">
                    {}
                </p><p>
                    {} <span class="fa fa-long-arrow-right"/> {}</p>
                """.format(_('Your stock is currently empty'),
                           _('Press the CREATE button to define quantity for each product in your stock or import them from a spreadsheet throughout Favorites'),
                           _('Import')),
        }
        return action

