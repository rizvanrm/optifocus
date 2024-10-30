from collections import defaultdict
from odoo import fields, models

class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    print_format = fields.Selection(selection_add=[
        ('ring', 'Ring')],ondelete={'ring': 'set default'},default='ring')

    def _prepare_report_data(self):
        xml_id, data = super()._prepare_report_data()
        if self.print_format == 'ring':
             xml_id = 'optifocus.report_product_template_label_ring'

        return xml_id, data


