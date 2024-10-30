from odoo import models, fields


class PurchaseReport(models.Model):
    _inherit = 'purchase.report'
    brand_id = fields.Many2one('product.brand', string='Brand',readonly=True)

    def _select(self):
        return super(PurchaseReport, self)._select() + ", t.brand_id as brand_id "

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ",t.brand_id"

