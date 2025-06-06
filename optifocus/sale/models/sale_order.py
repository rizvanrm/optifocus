from odoo import models ,_, fields, api
from odoo.exceptions import ValidationError, UserError
READONLY_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'sale', 'done', 'cancel'}
}
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    claim_count = fields.Integer(string="Claim Count", compute='_get_claim')
    state = fields.Selection(selection_add=[('waiting_approval', 'Waiting for Approval'), ('approve', 'Approved'),
                                            ('reject', 'Rejected'),
                                            ('revert', 'Reverted'),('sale',)
                                            ],tracking=True)

    claim_id=fields.Many2one('insurance.claim', string='Claim', store=True)

    sale_type = fields.Selection([
        ('retail', 'Retail'),
        ('insurance', 'Insurance'),
        ('wholesale', 'Wholesale')
    ], string="Sale Type", default='retail',required=True)


    member_id = fields.Many2one('insurance.member', string='Member',ondelete='restrict')
    insurance_id = fields.Many2one(related='member_id.insurance_company_id',store=True)
    insurance_company_plan = fields.Many2one(related='member_id.insurance_company_plan_id', store=True)
    insurance_discount = fields.Float(string="Insurance Discount", store=True,readonly=True)
    member_discount = fields.Float(string="Member Discount", store=True,readonly=True)
    policy_id = fields.Many2one(related='member_id.policy_id',store=True)
    policy_class_id = fields.Many2one(related='member_id.policy_class_id',store=True)
    policy_holder = fields.Char(related='member_id.policy_holder',store=True)
    inception_date = fields.Date(string="Inception Date", store=True,readonly=True)
    expiry_date = fields.Date(string="Expiry Date", store=True,readonly=True)
    co_insurance_type = fields.Selection([('percentage', '%'), ('fixed', 'Fixed')], string="Co-Insurance Type", store=True,readonly=True)
    co_insurance_percent = fields.Float(string="Co-Insurance %", store=True,readonly=True)
    up_to = fields.Float(string="Up To",store=True,readonly=True)
    co_insurance = fields.Char(string="Co-Insurance",readonly=True)

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        required=True,  change_default=True, index=True,
        readonly=False,
        tracking=1,
        states=READONLY_FIELD_STATES,
        domain="[('type', '!=', 'private'), ('company_id', 'in', (False, company_id))]",
        compute="_compute_partner_id",store=True)

    prescription_id = fields.Many2one('optical.prescription', string='Prescription')

    mobile = fields.Char(related='partner_id.mobile',store=True)
    id_no = fields.Char(string='Identification No', store=True,readonly=True)
    birth_date = fields.Date(related='member_id.birth_date',store=True)
    gender=fields.Selection(related='member_id.gender',store=True)

    request_attach_id = fields.Binary(string="Request Attachment")
    request_filename = fields.Char(compute='_compute_request_filename')
    approval_attach_id = fields.Binary(string="Approval Attachment")
    approval_filename = fields.Char(compute='_compute_approval_filename')
    prescription_attach_id = fields.Binary(related='prescription_id.prescription_attach_id')
    prescription_filename = fields.Char(compute='_compute_prescription_filename')
    approval_no = fields.Char(string="Approval No")
    approval_date = fields.Datetime(string="Approval Date")

    tray_no = fields.Char(string="Tray NO")

    gross_untaxed = fields.Monetary(string="Untaxed Gross", store=True, compute='_compute_amounts_op',
                                       precompute=True)
    gross_tax = fields.Monetary(string="Taxes Gross", store=True, compute='_compute_amounts_op', precompute=True)
    gross_total = fields.Monetary(string="Total Gross Amount", store=True, compute='_compute_amounts_op',
                                  precompute=True)

    approved_untaxed = fields.Monetary(string="Untaxed Approved", store=True, compute='_compute_amounts_op', precompute=True)
    approved_tax = fields.Monetary(string="Taxes Approved", store=True, compute='_compute_amounts_op', precompute=True)
    approved_total = fields.Float(string="Total Approved Amount", store=True, compute='_compute_amounts_op', precompute=True)

    claim_untaxed = fields.Monetary(string="Untaxed Claim", store=True, compute='_compute_amounts_op', precompute=True)
    claim_tax = fields.Monetary(string="Taxes Claim", store=True, compute='_compute_amounts_op', precompute=True)
    claim_total = fields.Monetary(string="Total Claim", store=True, compute='_compute_amounts_op', precompute=True)

    co_insurance_untaxed = fields.Monetary(
        string="Untaxed Co-Insurance", store=True, compute='_compute_amounts_op', precompute=True)
    co_insurance_tax = fields.Monetary(
        string="Taxes Co-Insurance", store=True, compute='_compute_amounts_op', precompute=True)
    co_insurance_total = fields.Monetary(
        string="Total Co-Insurance", store=True, compute='_compute_amounts_op', precompute=True)
    additional_untaxed = fields.Monetary(
        string="Untaxed Additional", store=True, compute='_compute_amounts_op', precompute=True)
    additional_tax = fields.Monetary(
        string="Taxes Additional", store=True, compute='_compute_amounts_op', precompute=True)
    additional_total = fields.Monetary(
        string="Total Additional", store=True, compute='_compute_amounts_op', precompute=True)

    member_untaxed = fields.Monetary(
        string="Untaxed Member", store=True, compute='_compute_amounts_op', precompute=True)
    member_tax = fields.Monetary(
        string="Taxes Member", store=True, compute='_compute_amounts_op', precompute=True)
    member_total = fields.Monetary(
        string="Total Member", store=True, compute='_compute_amounts_op', precompute=True)

    order_line_count = fields.Integer(string='Count', compute='_compute_order_line_count')

    insurance_sales_order_workflow_selection = fields.Selection([
        ('centralized', 'Centralized'),
        ('decentralized', 'Individual')],
        compute="_compute_insurance_sales_order_workflow",
        string="Insurance Sales Order Workflow",store=False)

    @api.model
    def get_discount_policy(self):
        """Fetch the configured discount settings from system parameters."""
        param_env = self.env['ir.config_parameter'].sudo()
        return {
            'line_coupon': param_env.get_param('sale.line_coupon_discount', 'False') == 'True',
            'line_global': param_env.get_param('sale.line_global_discount', 'False') == 'True',
            'coupon_global': param_env.get_param('sale.coupon_global_discount', 'False') == 'True',
            'line_coupon_global': param_env.get_param('sale.line_coupon_global_discount', 'False') == 'True',
        }

    @api.constrains('order_line')
    def _constrains_discount_policy(self):

        discount_policy = self.get_discount_policy()
        line_coupon = discount_policy.get('line_coupon', False)
        line_global = discount_policy.get('line_global', False)
        coupon_global = discount_policy.get('coupon_global', False)
        # line_coupon_global = discount_policy.get('line_coupon_global', False)
        has_line_discount = has_coupon_discount = has_global_discount = False

        for order in self:
            for line in order.order_line:
                if not has_line_discount and line.discount > 0:
                    has_line_discount = True
                if not has_coupon_discount and line.is_reward_line:
                    has_coupon_discount = True
                if not has_global_discount and line.product_template_id.name == 'Discount':
                    has_global_discount = True

            # if has_line_discount and has_coupon_discount and has_global_discount and not line_coupon_global:
            #     raise ValidationError("You cannot apply a Line Discount, Coupon Discount, and Global Discount together.")
            if has_line_discount and has_coupon_discount and not line_coupon:
                raise ValidationError("You cannot apply both a Line Discount and a Coupon Discount together.")
            if has_line_discount and has_global_discount and not line_global:
                raise ValidationError("You cannot apply both a Line Discount and a Global Discount together.")
            if has_coupon_discount and has_global_discount and not coupon_global:
                raise ValidationError("You cannot apply both a Coupon Discount and a Global Discount together.")

    @api.onchange('sale_type')
    def _compute_insurance_sales_order_workflow(self):
        config_param = self.env['ir.config_parameter'].sudo().get_param('optifocus.insurance_sales_order_workflow_selection')
        for record in self:
            record.insurance_sales_order_workflow_selection = config_param

    @api.onchange('member_id')
    def _onchange_member_id(self):

       for record in self:
            if record.sale_type == 'insurance' and record.member_id:
                record.partner_id = record.member_id.partner_id
                record.pricelist_id=record.member_id.insurance_company_id.pricelist_id
                record.id_no = record.partner_id.id_no
                record.inception_date = record.member_id.inception_date
                record.expiry_date = record.member_id.expiry_date
                record.co_insurance_type = record.member_id.co_insurance_type
                record.co_insurance_percent = record.member_id.co_insurance_percent
                record.up_to = record.member_id.up_to
                record.insurance_discount = record.member_id.insurance_discount
                record.member_discount = record.member_id.member_discount

                if record.co_insurance_type == 'fixed':
                    record.co_insurance = f"{record.up_to:.2f}"
                else:
                    record.co_insurance = f"{record.co_insurance_percent:.2f} % Upto {record.up_to:.2f}"
                self._compute_insurance()

                if record.expiry_date and record.expiry_date < fields.Date.today():
                    raise ValidationError("The insurance policy has expired.")

    @api.depends('member_id')
    def _compute_request_filename(self):
        for rec in self:
            rec.request_filename='R' + (rec.member_id.name or '')

    @api.depends('member_id')
    def _compute_prescription_filename(self):
        for rec in self:
            rec.prescription_filename = 'P' + (rec.member_id.name or '')

    @api.depends('member_id')
    def _compute_approval_filename(self):
        for rec in self:
            rec.approval_filename =  'A'+ (rec.approval_no or '')

    @api.depends('order_line')
    def _compute_order_line_count(self):
        for rec in self:
            count = 0
            for line in rec.order_line:
                if line.product_id.type in ('consu','service','combo'):
                    count += 1
            rec.order_line_count = count

    def _get_claim(self):
        claim_count = self.env['insurance.claim'].search_count([('claim_origin', '=', self.name)])
        self.claim_count = claim_count

    def action_open_claim(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Claims',
            'res_model': 'insurance.claim',
            'domain': [('claim_origin', '=', self.name)],
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.claim_id.id

        }

    def action_request_send_validation(self):
        if self.sale_type == 'insurance' and self.expiry_date < date.today():
            raise ValidationError("The insurance policy has expired.")
        if self.sale_type == 'insurance' and not self.id_no:
            raise ValidationError("Invalid field: Identification No")
        if self.sale_type == 'insurance' and not self.birth_date:
            raise ValidationError("Invalid field: Date of Birth")
        if self.sale_type == 'insurance' and not self.gender:
            raise ValidationError("Invalid field: Gender")
        if self.sale_type == 'insurance' and not self.prescription_id:
            raise ValidationError("Invalid field: Prescription")
        # if self.sale_type == 'insurance' and not self.insurance_id:
        #     raise ValidationError("Invalid field: Insurance Company")
        # if self.sale_type == 'insurance' and not self.policy_id:
        #     raise ValidationError("Invalid field: Policy")
        # if self.sale_type == 'insurance' and not self.policy_class_id:
        #     raise ValidationError("Invalid field: Class")
        if self.sale_type == 'insurance' and not self.member_id:
            raise ValidationError("Invalid field: Membership No")
        if self.sale_type == 'insurance' and not self.request_attach_id:
            raise ValidationError("Invalid field: Request Attachment")
        if self.sale_type == 'insurance' and not self.prescription_attach_id:
            raise ValidationError("Invalid field: Prescription Attachment")
        if self.sale_type == 'insurance' and self.order_line_count==0:
            raise ValidationError("A sales order must include at least one product line to proceed.")


    def action_request_send(self):
        self.action_request_send_validation()
        self.state = "waiting_approval"

    def action_approve_validation(self):
        if self.sale_type == 'insurance' and not self.approval_no:
            raise ValidationError("Invalid field: Approval No")
        if self.sale_type == 'insurance'  and not self.approval_date:
            raise ValidationError("Invalid field: Approval Date")
        if self.sale_type == 'insurance' and not self.approval_attach_id:
            raise ValidationError("Invalid field: Approval Attachment")

        for record in self:
            if record.sale_type == 'insurance' and record.approved_untaxed == 0:
                    raise ValidationError("The sum of the approved amounts must be greater than zero.")



    def action_approve(self):
        self.action_approve_validation()
        self.state = "approve"

    def action_reject(self):

        if self.sale_type == 'insurance' and self.state == 'waiting_approval' and not self.approval_no:
            raise ValidationError("Invalid field: Approval No")
        if self.sale_type == 'insurance' and self.state == 'waiting_approval' and not self.approval_date:
            raise ValidationError("Invalid field: Approval Date")
        if self.sale_type == 'insurance' and not self.approval_attach_id:
            raise ValidationError("Invalid field: Approval Attachment")
        self.state = "reject"

    def action_revert(self):
        self.state = "draft"

    def generate_claim(self):
        order_ids = self.search([('id','=',self._context.get('active_ids')),
                                 ('name', 'not in',self.env['insurance.claim'].sudo().search([]).mapped('name')),
                                 ('sale_type', '=', 'insurance')])
        order_ids_count=self.search_count([('id', 'in', self._context.get('active_ids')),
                     ('name', 'not in', self.env['insurance.claim'].sudo().search([]).mapped('name')),
                     ('sale_type', '=', 'insurance')])
        for rec in order_ids:
            claim=rec.get_claim()
            rec.claim_id=self.env['insurance.claim'].sudo().create(claim)



        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': str(order_ids_count) + " claims generated successfully.",
            }
        }

    def get_claim(self):
        claim_line = self.get_claim_line()
        value={'name': self.name,
              'sale_id': self.id,
              'claim_origin': self.name,
              'prescription_id':self.prescription_id.id,
              'member_id': self.member_id.id,
              'approval_no': self.approval_no,
              'approval_date': self.approval_date,
              'create_date': date.today(),
              'pricelist_id': self.pricelist_id.id,
              'id_no': self.id_no,
              'inception_date': self.inception_date,
              'expiry_date': self.expiry_date,
              'co_insurance_type' : self.co_insurance_type,
              'co_insurance_percent' : self.co_insurance_percent,
              'up_to' : self.up_to,
              'co_insurance': self.co_insurance,
              'insurance_discount' : self.insurance_discount,
              'member_discount' : self.member_discount,
              'company_id': self.company_id.id,
              'doctor' : self.prescription_id.doctor_id,
              'prescription_type': self.prescription_id.prescription_type,
              'r_sph': self.prescription_id.r_sph,
              'r_cyl': self.prescription_id.r_cyl,
              'r_axis': self.prescription_id.r_axis,
              'r_va': self.prescription_id.r_va,
              'r_add': self.prescription_id.r_add,
              'l_sph': self.prescription_id.l_sph,
              'l_cyl': self.prescription_id.l_cyl,
              'l_axis': self.prescription_id.l_axis,
              'l_va': self.prescription_id.l_va,
              'l_add': self.prescription_id.l_add,
              'ipd_distance': self.prescription_id.ipd_distance,
              'ipd_addition': self.prescription_id.ipd_addition,
              'claim_line': claim_line}
        return value

    def get_claim_line(self):
        value=[]
        for order in self:
            # for line in order.order_line:
            for line in order.order_line.filtered(lambda l: l.product_id):
                    value += [(0,0,   {

                            'product_id': line.product_id.id,
                            'product_uom_qty': line.product_uom_qty,
                            'price_unit': line.price_unit,
                            'gross_subtotal': line.gross_subtotal,
                            'approved_unit': line.approved_unit,
                            'approved_subtotal': line.approved_subtotal,
                            'claim_discount_subtotal': line.claim_discount_subtotal,
                            'member_discount_subtotal': line.member_discount_subtotal,
                            'discount_subtotal': line.discount_subtotal,
                            'discount_total': line.discount_total,
                            'claim_subtotal': line.claim_subtotal,
                            'claim_tax': line.claim_tax,
                            'claim_total': line.claim_total,
                            'co_insurance_subtotal': line.co_insurance_subtotal,
                            'co_insurance_tax': line.co_insurance_tax,
                            'co_insurance_total': line.co_insurance_total,
                            'additional_subtotal': line.additional_subtotal,
                            'additional_tax': line.additional_tax,
                            'additional_total': line.additional_total,
                            'member_subtotal': line.member_subtotal,
                            'member_tax': line.member_tax,
                            'member_total': line.member_total,
                            'tax_id':line.tax_id,
                            'price_subtotal': line.price_subtotal,
                            'price_tax': line.price_tax,
                            'price_total': line.price_total
                           })]
        return value

    @api.depends_context('lang')
    @api.depends('order_line.price_subtotal', 'currency_id', 'company_id')
    def _compute_tax_totals(self):
        AccountTax = self.env['account.tax']
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            base_lines = [line._prepare_base_line_for_taxes_computation(price_unit=(line.claim_subtotal+line.member_subtotal)/line.product_uom_qty if line.order_id.sale_type == 'insurance' else line.price_unit) for line in order_lines]
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            order.tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )


    @api.depends(
                  'order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total',
                  'order_line.gross_subtotal', 'order_line.gross_tax', 'order_line.gross_total',
                  'order_line.claim_subtotal', 'order_line.claim_tax', 'order_line.claim_total',
                  'order_line.co_insurance_subtotal', 'order_line.co_insurance_tax', 'order_line.co_insurance_total',
                  'order_line.additional_subtotal', 'order_line.additional_tax', 'order_line.additional_total',
                  'order_line.member_subtotal', 'order_line.member_tax', 'order_line.member_total')
    def _compute_amounts_op(self):

        gross_untaxed = 0.0
        gross_tax = 0
        gross_total = 0

        approved_untaxed = 0.0
        approved_tax = 0
        approved_total = 0

        claim_untaxed = 0
        claim_tax = 0
        claim_total = 0

        co_insurance_untaxed = 0
        co_insurance_tax = 0
        co_insurance_total = 0

        additional_untaxed = 0
        additional_tax = 0
        additional_total = 0

        member_untaxed = 0
        member_tax = 0
        member_total = 0

        for order in self:
            for line in order.order_line:


                gross_untaxed += line.gross_subtotal
                gross_tax += line.gross_tax
                gross_total += line.gross_total

                approved_untaxed += line.approved_subtotal
                approved_tax += line.approved_tax
                approved_total += line.approved_total

                claim_untaxed += line.claim_subtotal
                claim_tax += line.claim_tax
                claim_total +=line.claim_total

                co_insurance_untaxed += line.co_insurance_subtotal
                co_insurance_tax += line.co_insurance_tax
                co_insurance_total += line.co_insurance_total

                additional_untaxed += line.additional_subtotal
                additional_tax += line.additional_tax
                additional_total += line.additional_total

                member_untaxed += line.member_subtotal
                member_tax += line.member_tax
                member_total += line.member_total

                order['gross_untaxed'] = gross_untaxed
                order['gross_tax'] = gross_tax
                order['gross_total'] = gross_total

                order['approved_untaxed'] = approved_untaxed
                order['approved_tax'] = approved_tax
                order['approved_total'] = approved_total


                order['claim_untaxed'] = claim_untaxed
                order['claim_tax'] = claim_tax
                order['claim_total'] = claim_total

                order['co_insurance_untaxed'] = co_insurance_untaxed
                order['co_insurance_tax'] = co_insurance_tax
                order['co_insurance_total'] = co_insurance_total

                order['additional_untaxed'] = additional_untaxed
                order['additional_tax'] = additional_tax
                order['additional_total'] = additional_total

                order['member_untaxed'] = member_untaxed
                order['member_tax'] = member_tax
                order['member_total'] = member_total



    @api.onchange("sale_type", 'order_line', )
    def _compute_insurance(self):

       for order in self:
            co_insurance_difference_amount = order.up_to
            co_insurance_beyond_up_to_flag = False

            for line in order.order_line:
                co_insurance_beyond_up_to_flag=False
                if order.sale_type == 'insurance':
                    last_line = line
                    line.approved_subtotal=line.approved_unit * line.product_uom_qty

                    if order.co_insurance_type == 'percentage':

                        if order.approved_untaxed*order.co_insurance_percent/100*(100-order.member_discount)/100 > order.up_to :
                            # Insurance Discount
                            line.claim_discount_subtotal = (line.approved_unit*line.product_uom_qty*order.insurance_discount/100)

                            # Member Discount
                            line.member_discount_subtotal = 0

                            # Claim Amount

                            line.co_insurance_subtotal=round((order.up_to*line.approved_unit*line.product_uom_qty/order.approved_untaxed),2)
                            line.claim_subtotal = ((line.approved_unit * line.product_uom_qty * (
                                    100 - order.insurance_discount) / 100) - line.co_insurance_subtotal)
                            co_insurance_beyond_up_to_flag=True
                            co_insurance_difference_amount -= line.co_insurance_subtotal



                        else:
                            # Member Discount
                            line.member_discount_subtotal =  (line.approved_unit*line.product_uom_qty*order.co_insurance_percent/100*order.member_discount/100)
                            line.co_insurance_subtotal = (line.approved_unit*line.product_uom_qty*(order.co_insurance_percent)/100*(100-order.member_discount)/100)

                            if line.member_discount_subtotal == 0:
                                # Insurance Discount
                                line.claim_discount_subtotal= (line.approved_unit*line.product_uom_qty * order.insurance_discount / 100)
                                # Claim Amount
                                line.claim_subtotal = ((line.approved_unit*line.product_uom_qty * (
                                        100 - order.insurance_discount) / 100) - line.co_insurance_subtotal)
                            else:
                                line.claim_discount_subtotal = (line.approved_unit*line.product_uom_qty*(100-order.co_insurance_percent)
                                                                  / 100 * order.insurance_discount/100)
                                line.claim_subtotal = ((line.approved_unit *line.product_uom_qty* (
                                        100 - order.co_insurance_percent) / 100) * (100-order.insurance_discount)/100)

                    else:
                        # Member Discount
                        line.member_discount_subtotal = 0
                        # Insurance Discount
                        line.claim_discount_subtotal = (line.approved_unit*line.product_uom_qty * order.insurance_discount/100)

                        # Co-Insurance
                        line.co_insurance_subtotal = 0 if bool(order.approved_untaxed * order.up_to == 0) \
                            else line.approved_unit * line.product_uom_qty / order.approved_untaxed * order.up_to

                        # Claim Amount
                        line.claim_subtotal = ((line.approved_unit*line.product_uom_qty * (
                                100 - order.insurance_discount) / 100) - line.co_insurance_subtotal)


                    line.discount_subtotal = (line.member_discount_subtotal + line.claim_discount_subtotal)
                    line.additional_subtotal = (line.price_unit - line.approved_unit)*line.product_uom_qty
                    line.member_subtotal = (line.co_insurance_subtotal + line.additional_subtotal)

            if co_insurance_beyond_up_to_flag and last_line and co_insurance_difference_amount != 0:
                last_line.claim_subtotal +=round(co_insurance_difference_amount, 2)*-1
                print(round(co_insurance_difference_amount, 2))
                last_line.co_insurance_subtotal += round(co_insurance_difference_amount, 2)
                last_line.member_subtotal = (last_line.co_insurance_subtotal + last_line.additional_subtotal)


    @api.constrains('sale_type','order_line')
    def _constrains_discount_sale_type(self):

        for order in self:
            for line in order.order_line:
                if order.sale_type == "retail":
                    if line.discount > line.product_template_id.max_retail_line_discount:
                        raise ValidationError("For product, " + line.product_template_id.name +", Max. allowed discount is " + str(
                            line.product_template_id.max_retail_line_discount) + "%")

                elif order.sale_type == "wholesale":
                    if line.discount > line.product_template_id.max_wholesale_line_discount:
                        raise ValidationError("For Product, " + line.product_template_id.name +", Max. allowed discount is " + str(
                            line.product_template_id.max_wholesale_line_discount) + "%")

    def _create_invoices(self, grouped=False, final=False, date=None):
        result = super(SaleOrder, self)._create_invoices()
        move_line = []
        #create Insurnace Company Invoice
        if self.sale_type=='insurance':

            for move_id in result:
                for line in move_id.invoice_line_ids:
                    line.price_unit=line.sale_line_ids.member_subtotal/line.sale_line_ids.product_uom_qty

            for order in self:
                for line in order.order_line:
                    move_line += [(0, None, {
                        'name': line.name,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom.id,
                        'quantity': line.product_uom_qty,
                        'price_unit': line.claim_subtotal/line.product_uom_qty,
                        'tax_ids': line.tax_id,
                        'sale_line_ids': [(6, 0, [line.id for line in order.order_line])]
                                   })]

            if self.env['ir.config_parameter'].sudo().get_param('optifocus.invoicing_policy_insurance_selection')=='invoice_member_claim':
                move = self.env['account.move'].create({
                                'move_type': 'out_invoice',
                                'invoice_origin': self.name,
                                'cust_move_type': 'claim',
                                'date': self.date_order,
                                'partner_id': self.insurance_id.partner_id.id,
                                'invoice_date': self.date_order,
                                'currency_id': self.currency_id.id,
                                # 'invoice_payment_term_id': self.payment_term_id,
                                'ref': '',
                                'sale_order_count':1,
                                'invoice_line_ids': move_line })
            self.invoice_status='invoiced'

        return result

    def _prepare_invoice(self):
        result = super(SaleOrder, self)._prepare_invoice()
        if self.sale_type=='retail':
            cust_move_type='retail'
        elif self.sale_type=='insurance':
            cust_move_type='member'
        elif self.sale_type=='wholesale':
            cust_move_type = 'wholesale'

        result.update({'cust_move_type': cust_move_type})
        return result

    def _confirmation_error_message(self):
        """ Return whether order can be confirmed or not if not then returm error message. """

        result = super(SaleOrder, self)._confirmation_error_message()

        self.ensure_one()
        if self.state not in {'draft', 'sent','approve'}:
            return _("Some orders are not in a state requiring confirmation.")
        if any(
                not line.display_type
                and not line.is_downpayment
                and not line.product_id
                for line in self.order_line
        ):
            return _("A line on these orders missing a product, you cannot confirm it.")

        return False



    def _action_confirm(self):

        result=super(SaleOrder, self)._action_confirm()

        self.action_request_send_validation()
        self.action_approve_validation()

        order_ids = self.search([('id','=',self.id),
                                 ('state', 'in', ['sale']),
                                 ('name', 'not in', self.env['insurance.claim'].sudo().search([]).mapped('name')),
                                 ('sale_type', '=', 'insurance')])

        for rec in order_ids:
            claim = rec.get_claim()
            rec.claim_id=self.env['insurance.claim'].sudo().create(claim)

        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    order_partner_id = fields.Many2one(
        related='order_id.partner_id',
        string="Customer",
        store=True, index=True, precompute=True)

    approved_unit = fields.Float(
        string="Unit Approved")

    gross_subtotal = fields.Monetary(
        string="Gross",
        store=True)

    gross_tax = fields.Float(
        string="Gross Tax",
        compute='_compute_amount',
        store=True, precompute=True)

    gross_total = fields.Monetary(
        string="Gross Total",
        compute='_compute_amount',
        store=True, precompute=True)

    approved_subtotal = fields.Monetary(
        string="Approved",
        store=True)

    approved_tax = fields.Float(
        string="Approved Tax",
        compute='_compute_amount',
        store=True, precompute=True)

    approved_total = fields.Monetary(
        string="Approved Total",
        compute='_compute_amount',
        store=True, precompute=True)

    claim_discount_subtotal = fields.Float(
        string="Claim Discount",
        store=True)

    member_discount_subtotal = fields.Float(
        string="Member Discount",
        store=True)

    discount_subtotal = fields.Float(
        string="Discount",
        store=True)

    discount_total = fields.Float(
        string="Total Discount",
        store=True)

    claim_subtotal = fields.Monetary(
        string="Claim",
        store=True)

    claim_tax = fields.Float(
        string="Claim Tax",
        compute='_compute_amount',
        store=True, precompute=True)

    claim_total = fields.Monetary(
        string="Claim Total",
        compute='_compute_amount',
        store=True, precompute=True)

    co_insurance_subtotal = fields.Monetary(
        string="Co-Insurance",
        store=True)

    co_insurance_tax = fields.Float(
        string="Co-Insurance Tax",
        compute='_compute_amount',
        store=True, precompute=True)

    co_insurance_total = fields.Monetary(
        string="Co-Insurance Total",
        compute='_compute_amount',
        store=True, precompute=True)

    additional_subtotal = fields.Monetary(
        string="Additional",
        store=True)

    additional_tax = fields.Float(
        string="Additional Tax",
        compute='_compute_amount',
        store=True, precompute=True)

    additional_total = fields.Monetary(
        string="Additional Total",
        compute='_compute_amount',
        store=True, precompute=True)

    member_subtotal = fields.Monetary(
        string="Member",
        store=True)

    member_tax = fields.Float(
        string="Member Tax",
        compute='_compute_amount',
        store=True,precompute=True)

    member_total = fields.Monetary(
        string="Member Total",
        compute='_compute_amount',
        store=True, precompute=True)


    lead_time=fields.Boolean(string="Lead Time", default=False)

    @api.onchange('product_template_id')
    def _onchange_product_template_id(self):
        for record in self:
            if record.product_template_id and  record.order_id.sale_type=='insurance' and record.product_template_id.insurance_sale_ok == False:
                raise ValidationError("Product " + record.product_template_id.name + ", cannot be sold in Insurance Sales.")

    @api.constrains('approved_unit')
    def _constrains_approved_unit_price_unit(self):
        for record in self:
            if record.approved_unit > record.price_unit and record.order_id.sale_type == 'insurance':
                raise ValidationError("Unit Approved must be less than Unit Price.")

    @api.onchange( 'order_id.sale_type')
    def _onchange_discount_sale_type(self):
        for record in self:
            if record.order_id.sale_type == "retail":
                if record.discount > record.product_template_id.max_retail_line_discount:
                    raise ValidationError("Max. allowed Discount is " + str(record.product_template_id.max_retail_line_discount) + "%")

            elif record.order_id.sale_type == "wholesale":
                if record.discount > record.product_template_id.max_wholesale_line_discount:
                    raise ValidationError("Max. allowed Discount is " +  str(record.product_template_id.max_wholesale_line_discount) + "%")

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id','gross_subtotal','claim_subtotal','member_subtotal','order_id.sale_type')
    def _compute_amount(self):
        super(SaleOrderLine, self)._compute_amount()
        """
        Compute the amounts of the SO line.
      

        """

        # for line in self:
        for line in self.filtered(lambda l: l.product_id):

            if line.order_id.sale_type == "insurance":

                tax_results = line.tax_id.compute_all(
                    line.price_unit,
                    currency=line.currency_id,
                    quantity=line.product_uom_qty,
                    product=line.product_id)

                amount_untaxed = tax_results['total_excluded']
                amount_total = tax_results['total_included']
                line.update({
                    'gross_subtotal': amount_untaxed,
                    'gross_tax': amount_total-amount_untaxed,
                    'gross_total': amount_total,
                })

                tax_results = line.tax_id.compute_all(
                    line.approved_unit,
                    currency=line.currency_id,
                    quantity=line.product_uom_qty,
                    product=line.product_id)
                amount_untaxed = tax_results['total_excluded']
                amount_total = tax_results['total_included']
                line.update({
                    'approved_subtotal': amount_untaxed,
                    'approved_tax':amount_total - amount_untaxed,
                    'approved_total': amount_total ,
                })
                tax_results = line.tax_id.compute_all(
                    line.claim_subtotal / line.product_uom_qty,
                    currency=line.currency_id,
                    quantity=line.product_uom_qty,
                    product=line.product_id)
                amount_untaxed = tax_results['total_excluded']
                amount_total = tax_results['total_included']
                line.update({
                    'claim_subtotal': amount_untaxed,
                    'claim_tax': amount_total - amount_untaxed,
                    'claim_total': amount_total,
                })
                tax_results = line.tax_id.compute_all(
                    line.co_insurance_subtotal / line.product_uom_qty,
                    currency=line.currency_id,
                    quantity=line.product_uom_qty,
                    product=line.product_id)
                amount_untaxed = tax_results['total_excluded']
                amount_total = tax_results['total_included']
                line.update({
                    'co_insurance_subtotal': amount_untaxed,
                    'co_insurance_tax': amount_total - amount_untaxed,
                    'co_insurance_total': amount_total,
                })
                tax_results = line.tax_id.compute_all(
                    line.additional_subtotal / line.product_uom_qty,
                    currency=line.currency_id,
                    quantity=line.product_uom_qty,
                    product=line.product_id)
                amount_untaxed = tax_results['total_excluded']
                amount_total = tax_results['total_included']
                line.update({
                    'additional_subtotal': amount_untaxed,
                    'additional_tax': amount_total - amount_untaxed,
                    'additional_total': amount_total,
                })
                tax_results = line.tax_id.compute_all(
                    line.member_subtotal / line.product_uom_qty,
                    currency=line.currency_id,
                    quantity=line.product_uom_qty,
                    product=line.product_id)
                amount_untaxed = tax_results['total_excluded']
                amount_total = tax_results['total_included']
                line.update({
                    'member_subtotal': amount_untaxed,
                    'member_tax': amount_total - amount_untaxed,
                    'member_total': amount_total,
                })
                tax_results = line.tax_id.compute_all(
                    (line.claim_subtotal+line.member_subtotal) / line.product_uom_qty,
                    currency=line.currency_id,
                    quantity=line.product_uom_qty,
                    product=line.product_id)
                amount_untaxed = tax_results['total_excluded']
                amount_total = tax_results['total_included']
                line.update({
                    'price_subtotal': amount_untaxed,
                    'price_tax': amount_total - amount_untaxed,
                    'price_total': amount_total,
                })


