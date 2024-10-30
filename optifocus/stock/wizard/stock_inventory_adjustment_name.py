from odoo import models, fields, api
from datetime import datetime


class StockInventoryAdjustmentName(models.TransientModel):
    _inherit = 'stock.inventory.adjustment.name'
    _rec_name = 'inventory_adjustment_name'



    @api.model
    def _default_inventory_adjustment_name(self):
        return "Quantity Update on " + str(datetime.today().strftime('%Y-%m-%d'))

    inventory_adjustment_name = fields.Char(default= _default_inventory_adjustment_name)
    company_id = fields.Many2one('res.company', string='Company',  default=lambda self: self.env.company)

    _sql_constraints = [('inventory_adjustment_name_uniq', 'unique (inventory_adjustment_name,company_id)',
                         'Inventory Reference must be unique.')
                        ]

    def action_apply(self):
        quants = self.quant_ids.filtered('inventory_quantity_set')
        self.generate_inventory_adjustment_history()

        return quants.with_context(inventory_name=self.inventory_adjustment_name).action_apply_inventory()

    def generate_inventory_adjustment_history(self):
        inventory_adjustment=self.get_inventory_adjustment()
        self.env['stock.inventory.adjustment.history'].create(inventory_adjustment)

    def get_inventory_adjustment(self):
        inventory_adjustment_lines = self.get_inventory_adjustment_lines()
        value={'name': self.inventory_adjustment_name,
               'company_id': self.company_id.id,
               'inventory_adjustment_history_line': inventory_adjustment_lines}
        return value

    def get_inventory_adjustment_lines(self):
        value=[]
        inventory_adjustment_line_ids = self.quant_ids.filtered('inventory_quantity_set')

        for line in inventory_adjustment_line_ids:
            value += [(0,0,   {
                            'location_id' : line.location_id.id,
                            'product_id': line.product_id.id,
                            'list_price': line.product_tmpl_id.list_price,
                            'quantity': line.quantity,
                            'inventory_quantity': line.inventory_quantity,
                            'inventory_diff_quantity': line.inventory_diff_quantity,
                            'value': line.quantity* line.product_tmpl_id.list_price,
                            'inventory_value': line.inventory_quantity * line.product_tmpl_id.list_price,
                            'inventory_diff_value': line.inventory_diff_quantity * line.product_tmpl_id.list_price
                           })]
        return value



