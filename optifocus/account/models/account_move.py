from odoo import models, fields, api,_
from odoo.exceptions import ValidationError, UserError

class AccountMove(models.Model):

    _inherit = 'account.move'

    cust_move_type = fields.Selection([
        ('retail', 'Retail'),
        ('member', 'Member'),
        ('claim', 'Claim'),
        ('wholesale', 'Wholesale')
    ], string="Invoice Type")
    cust_commercial_partner_id = fields.Many2one('res.partner', string='Commercial Partner',  domain = "['|', ('is_commercial_partner', '=', True), ('id', '=', partner_id)]",store=True)

    def _post(self, soft=True):
        result = super(AccountMove, self)._post()
        for invoice in self.filtered(lambda move: move.is_invoice(include_receipts=True)):
            invoice.commercial_partner_id = invoice.cust_commercial_partner_id
            if invoice.line_ids.sale_line_ids.order_id.sale_type=='insurance':
                invoice.line_ids.sale_line_ids.order_id.invoice_status = 'invoiced'

            if invoice.is_sale_document() and invoice.cust_move_type=='retail' and not invoice.cust_commercial_partner_id:
                raise UserError(
                _("The field 'Commercial Partner' is required, please complete it to validate the Customer Invoice."))

        return result