from odoo import models, fields, api, _
from odoo.tools import format_date,ValidationError
from datetime import datetime

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _domain_company_dest_ids(self):
        return [('id', '!=', self.env.company.id)]

    company_dest_id = fields.Many2one(
        'res.company', string='Destination Company',domain=_domain_company_dest_ids)

    state = fields.Selection(selection_add=[('waiting2', 'Waiting'), ('workshop', 'Workshop')],
                             help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
                                  " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
                                  " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
                                  " * To Workshop: The transfer is sent to Workshop for fitting.\n"
                                  " * Finished product to shop : The transfer is ready sent to Shop.\n"
                                  " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
                                  " * Done: The transfer has been processed.\n"
                                  " * Cancelled: The transfer has been cancelled.")


    location_type = fields.Selection(related='location_id.usage')
    location_dest_type = fields.Selection(related='location_dest_id.usage')
    sale_type = fields.Selection(related='sale_id.sale_type')
    power_lens_flag = fields.Boolean(string='Product Category Flag',compute='_compute_power_lens_flag',store=True)

    @api.depends('move_ids')
    def _compute_power_lens_flag(self):
        for line in self.move_ids:
            if line.product_id.categ_id.name=='POWER LENS':
                self.power_lens_flag=True
                break

    @api.constrains('company_dest_id')
    def _constrains_company_dest_id(self):
        if self.picking_type_id.code == 'internal' and self.location_id.usage == 'internal' and self.location_dest_id.usage == 'transit' and not self.company_dest_id:
            raise ValidationError("Invalid Destination Company.")

    def button_validate(self):
        res = super(StockPicking, self).button_validate()

        if self.state=='done' and self.picking_type_id.code == 'internal' and self.location_id.usage == 'internal' and self.location_dest_id.usage == 'transit' and self.company_dest_id:
            transfer=self.get_transfer()
            self.env['stock.picking'].sudo().create(transfer)
        return res

    def get_transfer(self):
        global picking_type_dest_id
        picking_type_dest_id= self.env['stock.picking.type'].sudo().search([('company_id','=',self.company_dest_id.id),
                                                               ('code','=', 'internal') ], order='sequence',limit=1)
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
                            'company_id': self.company_dest_id.id,
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.product_uom_qty,
                            'product_uom': line.product_id.uom_id.id,
                            'location_id': self.location_dest_id.id,
                            'location_dest_id': picking_type_dest_id.default_location_src_id.id,
                           })]
        return value

    def action_confirm(self):
        res = super(StockPicking, self).action_confirm()
        for picking in self:
            if picking.picking_type_code == 'outgoing' and picking.products_availability_state=='available' and picking.sale_type in ('retail','insurance') and picking.power_lens_flag:
                picking.state='waiting2'
        return res

    def action_assign(self):
        res = super(StockPicking, self).action_assign()

        for picking in self:
            if picking.picking_type_code == 'outgoing' and picking.products_availability_state=='available' and picking.sale_type in ('retail','insurance') and picking.power_lens_flag:
                picking.state='waiting2'
        return res

    def action_to_workshop(self):
        for picking in self:
            if picking.picking_type_code == 'outgoing' and picking.sale_type in ('retail', 'insurance') and picking.power_lens_flag:
                picking.state = 'workshop'

    def action_to_shop(self):
        for picking in self:
            if picking.picking_type_code == 'outgoing' and picking.sale_type in ('retail', 'insurance') and picking.power_lens_flag:
                picking.state = 'assigned'

    @api.depends('move_type', 'immediate_transfer', 'move_ids.state', 'move_ids.picking_id')
    def _compute_state(self):

        res = super(StockPicking, self)._compute_state()

        for picking in self:
            if picking.picking_type_code == 'outgoing' and picking.products_availability_state=='available' and picking.sale_type in ('retail', 'insurance') and picking.power_lens_flag:
                picking.state = 'waiting2'
        return res