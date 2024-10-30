from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class InventoryAdjustmentHistory(models.Model):
    _name = "stock.inventory.adjustment.history"
    _description = "Inventory Adjustment History"

    name = fields.Char(string="Inventory Adjustment Reference",)
    company_id = fields.Many2one('res.company', string='Company')
    inventory_adjustment_history_line = fields.One2many('stock.inventory.adjustment.history.line', 'inventory_adjustment_history_id', string='Inventory Adjustment History Lines')


class InventoryAdjustmentHistoryLine(models.Model):
    _name = "stock.inventory.adjustment.history.line"
    _description = "Inventory Adjustment History Line"

    inventory_adjustment_history_id = fields.Many2one('stock.inventory.adjustment.history', string='Inventory Adjustment History')

    location_id= fields.Many2one('stock.location', string='Location')
    product_id = fields.Many2one('product.product', string='Product')
    barcode = fields.Char(related='product_id.barcode',string='Barcode')

    list_price = fields.Float(string="Sales Price")
    quantity = fields.Float(string="On Hand Quantity")
    inventory_quantity=fields.Float(string="Counted Quantity")
    inventory_diff_quantity = fields.Float(string="Difference Quantity")

    value = fields.Float(string="On Hand Value")
    inventory_value = fields.Float(string="Counted Value")
    inventory_diff_value = fields.Float(string="Difference Value")



