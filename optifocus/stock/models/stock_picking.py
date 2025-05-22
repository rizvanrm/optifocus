
from odoo import models, fields, api, _

from odoo.exceptions  import ValidationError,UserError
from odoo.tools.float_utils import float_compare, float_is_zero
from datetime import datetime
from collections import defaultdict

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    company_dest_id = fields.Selection(
        selection=lambda self: self._get_company_dest_selection(),
        string="Destination Company",
    )

    state = fields.Selection(selection_add=[('workshop', 'Workshop'),('shop', 'FP @ Shop'),('done',)],
                             help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
                                  " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
                                  " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
                                  " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
                                  " * To Workshop: The transfer is sent to Workshop for fitting.\n"
                                  " * Finished product to shop : The transfer is ready sent to Shop.\n"
                                  " * Done: The transfer has been processed.\n"
                                  " * Cancelled: The transfer has been cancelled.")

    location_type = fields.Selection(related='location_id.usage')
    location_dest_type = fields.Selection(related='location_dest_id.usage')
    sale_type = fields.Selection(related='sale_id.sale_type')
    show_to_workshop = fields.Boolean(
        compute='_compute_show_to_workshop',
        help='Technical field used to compute whether the button "To Workshop" should be displayed.')
    show_to_shop = fields.Boolean(
        compute='_compute_show_to_shop',
        help='Technical field used to compute whether the button "To Shop" should be displayed.')

    is_workshop_workflow =fields.Boolean(
        compute='_compute_is_workshop_workflow',default=False,
        help='Technical field used to determine whether the order follows the workshop workflow.')

    @api.model
    def _get_company_dest_selection(self):
        """ Fetch all companies and return as selection field choices. """
        company_dest_ids = self.env['res.company'].sudo().search([('id', '!=', self.env.company.id)])
        return [(str(company_dest_id.id), company_dest_id.name) for company_dest_id in company_dest_ids]

    @api.constrains('company_dest_id')
    def _constrains_company_dest_id(self):
        if self.picking_type_id.code == 'internal' and self.location_id.usage == 'internal' and self.location_dest_id.usage == 'transit' and not self.company_dest_id:
            raise ValidationError("Invalid Destination Company.")

    def button_validate(self):
        res = super(StockPicking, self).button_validate()

        if self.state=='done' and self.picking_type_id.code == 'internal' and self.location_id.usage == 'internal' and self.location_dest_id.usage == 'transit' and self.company_dest_id:
            transfer=self.get_transfer()
            self.env['stock.picking'].sudo().create(transfer)
        elif self.picking_type_id.code == 'outgoing' and self.sale_id.sale_type in ['retail', 'insurance']:
            if self.sale_id.invoice_status!='invoiced':
                raise UserError("You cannot validate this delivery order because the related sale order has not been invoiced.")
            else:
                if self.sale_id.invoice_ids.filtered(lambda inv: inv.payment_state not in ['in_payment', 'paid']):
                    raise UserError("You cannot validate this delivery order because the related invoice(s) are not fully paid.")
        return res

    def get_transfer(self):
        global picking_type_dest_id
        picking_type_dest_id= self.env['stock.picking.type'].sudo().search([
                                                               ('code','=', 'internal'),('company_id','=', int(self.company_dest_id)) ], order='sequence',limit=1)

        if not picking_type_dest_id :
            raise ValidationError("Invalid Destination Company/Operation Type.")

        stock_move = self.get_stock_move()
        move_ids = (self.env['stock.move'].sudo().create(stock_move)).ids

        value={
                'partner_id': self.partner_id.id,
                'picking_type_id':picking_type_dest_id.id,
                'location_id': self.location_dest_id.id,
                'location_dest_id': picking_type_dest_id.default_location_src_id.id,
                'scheduled_date': datetime.now(),
                'origin':self.name,
                'move_ids': move_ids,
                }
        return value

    def get_stock_move(self):
        value = []
        for transfer in self:
            for line in transfer.move_ids:
                if line.product_id.default_code :
                    line.name = _("[%s] %s") % (line.product_id.default_code,line.product_id.name)
                else:
                    line.name = _("%s") % line.product_id.name

                value += [({
                            'name': line.name,
                            'company_id': int(self.company_dest_id) ,
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.product_uom_qty,
                            'product_uom': line.product_id.uom_id.id,
                            'location_id': self.location_dest_id.id,
                            'location_dest_id': picking_type_dest_id.default_location_src_id.id,
                           })]
        return value

    def action_to_workshop(self):
        for picking in self:
            if picking.picking_type_code == 'outgoing' :
                picking.state = 'workshop'

    def action_to_shop(self):
        for picking in self:
            if picking.picking_type_code == 'outgoing':
                picking.state = 'shop'

    @api.depends('move_ids', 'picking_type_code')
    def _compute_show_to_workshop(self):
        for picking in self:
            picking.show_to_workshop=False
            if picking.picking_type_code == 'outgoing' and  picking.is_workshop_workflow and  picking.products_availability==_('Available') \
                    and picking.state=='assigned':
                picking.show_to_workshop= True

    @api.depends('move_ids', 'picking_type_code')
    def _compute_show_to_shop(self):
        for picking in self:
            picking.show_to_shop = False
            if picking.picking_type_code == 'outgoing' and picking.is_workshop_workflow and picking.state in ('workshop',):
                picking.show_to_shop= True

    @api.depends('state', 'picking_type_code', 'move_ids')
    def _compute_is_workshop_workflow(self):
        param_value = self.env['ir.config_parameter'].sudo().get_param('optifocus.workshop_categ_ids', '')
        allowed_categ_ids = [int(cid) for cid in param_value.split(',') if cid]

        for picking in self:
            picking.is_workshop_workflow = False
            if (any(m.product_id.categ_id.id in allowed_categ_ids for m in picking.move_ids)):
                picking.is_workshop_workflow = True

