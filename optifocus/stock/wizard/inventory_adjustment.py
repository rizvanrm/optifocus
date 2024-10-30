from odoo import api, fields, models
from odoo.tools import date_utils
from odoo.exceptions import UserError, ValidationError


class InventoryAdjustment(models.TransientModel):

    _name = 'inventory.adjustment.wizard'
    _description = 'Inventory Adjustment'

    inventory_adjustment_history_id = fields.Many2one('stock.inventory.adjustment.history', string='Inventory Adjustment Reference')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string="State", default='draft')
    report_type = fields.Selection([
        ('detail', 'Detail'),
        ('summary', 'Summary'),
    ], string="Report Type", required=True, default='detail')
    group_by = fields.Selection([
        ('category', 'Product Category'),
        ('brand', 'Brand'),
    ], string="Group By",  required=True,default='category')

    def generate_report(self):
        if self.state=="confirmed" and not self.inventory_adjustment_history_id:
            raise ValidationError("Invalid Inventory Adjustment Reference.")

        data = {
            'form_data': self.read()[0],
        }
        return self.env.ref('optifocus.inventory_adjustment_report').with_context(landscape=True).report_action(self, data=data)

