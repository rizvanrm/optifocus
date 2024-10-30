from odoo import api, fields, models


class InventoryAdjustmentAB(models.AbstractModel):
    _name = 'report.optifocus.report_inventory_adjustment'
    _description = 'Inventory Adjustment'



    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []
        inventory_adjustment_history_id = data.get('form_data').get('inventory_adjustment_history_id')
        state = data.get('form_data').get('state')
        group_by = data.get('form_data').get('group_by')
        report_type = data.get('form_data').get('report_type')




        if state=="draft":
            inventory_adjustment_history_id=self.env['stock.quant'].search([('inventory_quantity_set','=',True)])
        elif state=="confirmed":
            domain += [('id', '=', inventory_adjustment_history_id[0])]
            inventory_adjustment_history_id=self.env['stock.inventory.adjustment.history'].search(domain)


        return {
            'request': self,
            'inventory_adjustment_history_id':inventory_adjustment_history_id,
            'state': state,
            'group_by': group_by,
            'report_type': report_type
        }


