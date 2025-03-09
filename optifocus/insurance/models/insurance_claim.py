from collections import defaultdict

from odoo import api, fields, models, _ , Command
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, float_round

class InsuranceClaim(models.Model):
    _name = "insurance.claim"
    _description = "Insurance Claim"

    name = fields.Char(
        string="Claim Reference",
        required = True,
        index = 'trigram',
        states = {'draft': [('readonly', False)]},
        default = lambda self: _('New'))
    sale_count = fields.Integer(string="Sale Count", compute='_get_sale')

    sale_id = fields.Many2one('sale.order', string='Sale', store=True)
    claim_origin = fields.Char(
        string='Origin',
        readonly=True,
        tracking=True,
        help="The document(s) that generated the claim.",
    )
    member_id = fields.Many2one('insurance.member')
    insurance_id = fields.Many2one(related='member_id.insurance_company_id', store=True)
    insurance_company_plan = fields.Many2one(related='member_id.insurance_company_plan_id', store=True)
    insurance_discount = fields.Float(string="Insurance Discount", store=True, readonly=True)
    member_discount = fields.Float(string="Member Discount", store=True, readonly=True)

    policy_id = fields.Many2one(related='member_id.policy_id', store=True)
    policy_class_id = fields.Many2one(related='member_id.policy_class_id', store=True)
    policy_holder = fields.Char(related='member_id.policy_holder', store=True)
    inception_date = fields.Date(string="Inception Date", store=True, readonly=True)
    expiry_date = fields.Date(string="Expiry Date", store=True, readonly=True)
    co_insurance_type = fields.Selection([('percentage', '%'), ('fixed', 'Fixed')], string="Co-Insurance Type",
                                         store=True, readonly=True)
    co_insurance_percent = fields.Float(string="Co-Insurance %", store=True, readonly=True)
    up_to = fields.Float(string="Up To", store=True, readonly=True)
    co_insurance = fields.Char(string="Co-Insurance", readonly=True)
    partner_id = fields.Many2one(related='member_id.partner_id', string="Customer")
    mobile = fields.Char(related='member_id.mobile', store=True)
    id_no = fields.Char(string='Identification No', store=True,readonly=True)
    birth_date = fields.Date(related='member_id.birth_date', store=True)
    gender = fields.Selection(related='member_id.gender', store=True)
    prescription_id = fields.Many2one('optical.prescription', string='Prescription')

    prescription_filename = fields.Char(related='sale_id.prescription_filename')
    prescription_attach_id = fields.Binary(related='sale_id.prescription_attach_id')
    request_filename = fields.Char(related='sale_id.request_filename')
    request_attach_id = fields.Binary(related='sale_id.request_attach_id')
    approval_filename = fields.Char(related='sale_id.approval_filename')
    approval_attach_id = fields.Binary(related='sale_id.approval_attach_id')

    doctor = fields.Many2one(related='prescription_id.doctor_id')
    prescription_type = fields.Selection(related='prescription_id.prescription_type')
    r_sph = fields.Float(related='prescription_id.r_sph')
    r_cyl = fields.Float(related='prescription_id.r_cyl')
    r_axis = fields.Float(related='prescription_id.r_axis')
    r_va = fields.Char(related='prescription_id.r_va')
    r_add = fields.Float(related='prescription_id.r_add')
    l_sph = fields.Float(related='prescription_id.l_sph')
    l_cyl = fields.Float(related='prescription_id.l_cyl')
    l_axis = fields.Float(related='prescription_id.l_axis')
    l_va = fields.Char(related='prescription_id.l_va')
    l_add = fields.Float(related='prescription_id.l_add')
    ipd_distance = fields.Float(related='prescription_id.ipd_distance')
    ipd_addition = fields.Float(related='prescription_id.ipd_addition')
    notes = fields.Text(related='prescription_id.notes')


    approval_no = fields.Char(string="Approval No",)
    create_date = fields.Datetime(
        string="Create Date",
        )

    approval_date = fields.Datetime(string="Approval Date")
    company_id = fields.Many2one(
        comodel_name='res.company',
         index=True)

    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        compute='_compute_pricelist_id',
        readonly=True,   # Unrequired company
        #states=READONLY_FIELD_STATES,
        #tracking=1,
        #domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")
    currency_id = fields.Many2one(
        related='pricelist_id.currency_id',
        depends=["pricelist_id"],
        store=True,  ondelete="restrict")

    discount_total = fields.Float(string='Total Discount',store=True,compute='_compute_amounts')

    gross_untaxed = fields.Monetary(string="Untaxed Gross", store=True, compute='_compute_amounts')
    gross_tax = fields.Monetary(string="Taxes Gross", store=True, compute='_compute_amounts')
    gross_total = fields.Monetary(string="Total Gross Amount", store=True, compute='_compute_amounts')

    approved_untaxed = fields.Monetary(string="Untaxed Approved", store=True, compute='_compute_amounts')
    approved_tax = fields.Monetary(string="Taxes Approved", store=True, compute='_compute_amounts')
    approved_total = fields.Float(string="Total Approved Amount", store=True, compute='_compute_amounts')
    claim_untaxed = fields.Monetary(string="Untaxed Claim", store=True,compute='_compute_amounts')
    claim_tax = fields.Monetary(string="Taxes Claim", store=True, compute='_compute_amounts')
    claim_total = fields.Monetary(string="Total Claim", store=True, compute='_compute_amounts')
    co_insurance_untaxed = fields.Monetary(string="Untaxed Co-Insurance", store=True, compute='_compute_amounts')
    co_insurance_tax = fields.Monetary(string="Taxes Co-Insurance", store=True, compute='_compute_amounts')
    co_insurance_total = fields.Monetary(string="Total Co-Insurance", store=True, compute='_compute_amounts')
    additional_untaxed = fields.Monetary(string="Untaxed Additional", store=True, compute='_compute_amounts')
    additional_tax = fields.Monetary(string="Taxes Additional", store=True, compute='_compute_amounts')
    additional_total = fields.Monetary(string="Total Additional", store=True, compute='_compute_amounts')
    member_untaxed = fields.Monetary(string="Untaxed Member", store=True, compute='_compute_amounts')
    member_tax = fields.Monetary(string="Taxes Member", store=True, compute='_compute_amounts')
    member_total = fields.Monetary(string="Total Member", store=True, compute='_compute_amounts')

    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts')

    amount_tax = fields.Monetary(string="Taxes", store=True, compute='_compute_amounts')
    amount_total = fields.Monetary(string="Total", store=True, compute='_compute_amounts')

    tax_totals = fields.Binary()
    tax_country_id = fields.Many2one(
        comodel_name='res.country',
        compute='_compute_tax_country_id',
        # Avoid access error on fiscal position when reading a sale order with company != user.company_ids
        compute_sudo=True)  # used to filter available taxes depending on the fiscal country and position
    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Fiscal Position",
        compute='_compute_fiscal_position_id',
        store=True, readonly=False, precompute=True, check_company=True,
        help="Fiscal positions are used to adapt taxes and accounts for particular customers or sales orders/invoices."
             "The default value comes from the customer.",
        domain="[('company_id', '=', company_id)]")
    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string="Delivery Address",
        compute='_compute_partner_shipping_id',
        store=True, readonly=False,  precompute=True,
    #    states=LOCKED_FIELD_STATES,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )

    claim_line = fields.One2many('insurance.claim.line', 'claim_id', string='Insurance Claim Lines')

    @api.onchange('member_id')
    def _onchange_member_id(self):
        for record in self:
            if record.member_id:
                record.partner_id = record.member_id.partner_id
                record.pricelist_id = record.member_id.insurance_company_id.pricelist_id
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

    def _get_sale(self):
        sale_count = self.env['sale.order'].search_count([('name', '=', self.claim_origin)])
        self.sale_count = sale_count

    def action_view_sale(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sales',
            'res_model': 'sale.order',
            'domain': [('name', '=', self.claim_origin)],
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.sale_id.id
        }

    def copy_data(self, default=None):
        if default is None:
            default = {}
        if 'name' not in default:
            default['name'] = _("%s (copy)", self.name)
        if 'claim_line' not in default:
            default['claim_line'] = [
                Command.create(line.copy_data()[0])
                for line in self.claim_line
            ]
        return super().copy_data(default)

    # Constraint Unique Record
    _sql_constraints = [
        ('claim_uniq', 'unique (name)', 'Claim must be unique.'),
    ]

    @api.depends('currency_id', 'create_date', 'company_id')
    def _compute_currency_rate(self):
        cache = {}
        for order in self:
            order_date = order.create_date.date()
            if not order.company_id:
                order.currency_rate = order.currency_id.with_context(date=order_date).rate or 1.0
                continue
            elif not order.currency_id:
                order.currency_rate = 1.0
            else:
                key = (order.company_id.id, order_date, order.currency_id.id)
                if key not in cache:
                    cache[key] = self.env['res.currency']._get_conversion_rate(
                        from_currency=order.company_id.currency_id,
                        to_currency=order.currency_id,
                        company=order.company_id,
                        date=order_date,
                    )
                order.currency_rate = cache[key]

    @api.depends('insurance_id')
    def _compute_pricelist_id(self):
        for claim in self:
            if not claim.insurance_id:
                claim.pricelist_id = False
                continue
            claim.pricelist_id = claim.member_id.insurance_company_id.pricelist_id
    @api.depends('company_id', 'fiscal_position_id')
    def _compute_tax_country_id(self):
        for record in self:
            if record.fiscal_position_id.foreign_vat:
                record.tax_country_id = record.fiscal_position_id.country_id
            else:
                record.tax_country_id = record.company_id.account_fiscal_country_id

    @api.depends('partner_shipping_id', 'partner_id', 'company_id')
    def _compute_fiscal_position_id(self):
        """
        Trigger the change of fiscal position when the shipping address is modified.
        """
        cache = {}
        for order in self:
            if not order.partner_id:
                order.fiscal_position_id = False
                continue
            key = (order.company_id.id, order.partner_id.id, order.partner_shipping_id.id)
            if key not in cache:
                cache[key] = self.env['account.fiscal.position'].with_company(
                    order.company_id
                )._get_fiscal_position(order.partner_id, order.partner_shipping_id)
            order.fiscal_position_id = cache[key]

    @api.depends('partner_id')
    def _compute_partner_shipping_id(self):
        for order in self:
            order.partner_shipping_id = order.partner_id.address_get(['delivery'])[
                'delivery'] if order.partner_id else False

    @api.depends('claim_line.tax_id', 'claim_line.price_unit', 'amount_total', 'amount_untaxed', 'currency_id')
    def _compute_tax_totals(self):
        for claim in self:
            claim_lines = claim.claim_line.filtered(lambda x: not x.display_type)
            claim.tax_totals = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in claim_lines],
                claim.currency_id or claim.company_id.currency_id,
            )
    @api.depends(
           'claim_line.gross_subtotal', 'claim_line.gross_tax', 'claim_line.gross_total',
                 'claim_line.price_subtotal', 'claim_line.price_tax', 'claim_line.price_total',
                 'claim_line.claim_subtotal', 'claim_line.claim_tax', 'claim_line.claim_total',
                 'claim_line.co_insurance_subtotal', 'claim_line.co_insurance_tax', 'claim_line.co_insurance_total',
                 'claim_line.additional_subtotal', 'claim_line.additional_tax', 'claim_line.additional_total',
                 'claim_line.member_subtotal', 'claim_line.member_tax', 'claim_line.member_total',
                 'claim_line.price_subtotal', 'claim_line.price_tax', 'claim_line.price_total')
    def _compute_amounts(self):

        for claim in self:
            claim_lines = claim.claim_line


            discount_total=sum(claim_lines.mapped('claim_discount_subtotal') +
                                claim_lines.mapped('member_discount_subtotal'))

            gross_untaxed = sum(claim_lines.mapped('gross_subtotal'))
            gross_tax = sum(claim_lines.mapped('gross_tax'))
            gross_total = sum(claim_lines.mapped('gross_total'))

            approved_untaxed = sum(claim_lines.mapped('approved_subtotal'))
            approved_tax = sum(claim_lines.mapped('approved_tax'))
            approved_total = sum(claim_lines.mapped('approved_total'))

            claim_untaxed = sum(claim_lines.mapped('claim_subtotal'))
            claim_tax = sum(claim_lines.mapped('claim_tax'))
            claim_total = sum(claim_lines.mapped('claim_total'))

            co_insurance_untaxed = sum(claim_lines.mapped('co_insurance_subtotal'))
            co_insurance_tax = sum(claim_lines.mapped('co_insurance_tax'))
            co_insurance_total = sum(claim_lines.mapped('co_insurance_total'))

            additional_untaxed = sum(claim_lines.mapped('additional_subtotal'))
            additional_tax = sum(claim_lines.mapped('additional_tax'))
            additional_total = sum(claim_lines.mapped('additional_total'))

            member_untaxed = sum(claim_lines.mapped('member_subtotal'))
            member_tax = sum(claim_lines.mapped('member_tax'))
            member_total = sum(claim_lines.mapped('member_total'))

            amount_untaxed = sum(claim_lines.mapped('price_subtotal'))
            amount_tax = sum(claim_lines.mapped('price_tax'))
            amount_total = sum(claim_lines.mapped('price_total'))

            claim.gross_untaxed = gross_untaxed
            claim.gross_tax = gross_tax
            claim.gross_total = gross_total

            claim.approved_untaxed = approved_untaxed
            claim.approved_tax = approved_tax
            claim.approved_total = approved_total


            claim.discount_total = discount_total



            claim.claim_untaxed = claim_untaxed
            claim.claim_tax = claim_tax
            claim.claim_total = claim_total

            claim.co_insurance_untaxed = co_insurance_untaxed
            claim.co_insurance_tax = co_insurance_tax
            claim.co_insurance_total = co_insurance_total

            claim.additional_untaxed = additional_untaxed
            claim.additional_tax = additional_tax
            claim.additional_total = additional_total

            claim.member_untaxed = member_untaxed
            claim.member_tax = member_tax
            claim.member_total = member_total

            claim.amount_untaxed = amount_untaxed
            claim.amount_tax = amount_tax
            claim.amount_total = claim.amount_untaxed + claim.amount_tax


    @api.onchange( "claim_line")
    def _compute_insurance(self):
        for claim in self:
            for line in claim.claim_line:
                line.approved_subtotal = line.approved_unit * line.product_uom_qty
                if claim.co_insurance_type == 'percentage':

                    if claim.approved_total * claim.co_insurance_percent / 100 * (
                                100 - claim.member_discount) / 100 > claim.up_to:
                            # Insurance Discount
                            line.claim_discount_subtotal = (
                                    line.approved_unit * line.product_uom_qty * claim.insurance_discount / 100)

                            # Member Discount
                            line.member_discount_subtotal = 0

                            # Claim Amount
                            line.claim_subtotal = ((line.approved_unit * line.product_uom_qty * (
                                    100 - claim.insurance_discount) / 100) - line.co_insurance_subtotal)
                            # Co-Insurance Amount
                            line.co_insurance_subtotal = (
                                    claim.up_to * line.approved_unit * line.product_uom_qty / claim.approved_total)
                    else:
                            # Member Discount
                            line.member_discount_subtotal = (
                                    line.approved_unit * line.product_uom_qty * claim.co_insurance_percent / 100 * claim.member_discount / 100)
                            line.co_insurance_subtotal = (line.approved_unit * line.product_uom_qty * (
                                claim.co_insurance_percent) / 100 * (100 - claim.member_discount) / 100)

                            if line.member_discount_subtotal == 0:
                                # Insurance Discount
                                line.claim_discount_subtotal = (
                                        line.approved_unit * line.product_uom_qty * claim.insurance_discount / 100)
                                # Claim Amount
                                line.claim_subtotal = ((line.approved_unit * line.product_uom_qty * (
                                        100 - claim.insurance_discount) / 100) - line.co_insurance_subtotal)
                            else:
                                line.claim_discount_subtotal = (line.approved_unit * line.product_uom_qty * (
                                        100 - claim.co_insurance_percent)
                                                                / 100 * claim.insurance_discount / 100)
                                line.claim_subtotal = ((line.approved_unit * line.product_uom_qty * (
                                        100 - claim.co_insurance_percent) / 100) * (
                                                               100 - claim.insurance_discount) / 100)
                else:
                        # Member Discount
                        line.member_discount_subtotal = 0
                        # Insurance Discount
                        line.claim_discount_subtotal = (
                                line.approved_unit * line.product_uom_qty * claim.insurance_discount / 100)

                        # Co-Insurance
                        line.co_insurance_subtotal = 0 if bool(claim.approved_total * claim.up_to == 0) \
                            else line.approved_unit * line.product_uom_qty / claim.approved_total * claim.up_to

                        # Claim Amount
                        line.claim_subtotal = ((line.approved_unit * line.product_uom_qty * (
                                100 - claim.insurance_discount) / 100) - line.co_insurance_subtotal)

                line.discount_subtotal = (line.member_discount_subtotal + line.claim_discount_subtotal)
                line.additional_subtotal = (line.price_unit - line.approved_unit) * line.product_uom_qty
                line.member_subtotal = (line.co_insurance_subtotal + line.additional_subtotal)



class InsuranceClaimLine(models.Model):
    _name = "insurance.claim.line"
    _description = "Insurance Claim Line"

    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        #change_default=True, ondelete='restrict', check_company=True, index='btree_not_null',
        domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        )
    product_template_id = fields.Many2one(
        string="Product Template",
        comodel_name='product.template',
        compute='_compute_product_template_id',
        store=True,
        readonly=False)

    name = fields.Char(related='product_template_id.name')

    product_uom_qty = fields.Float(
        string="Quantity",
        #compute='_compute_product_uom_qty',
        digits='Product Unit of Measure', default=1.0,
        store=True, readonly=False, required=True)

    price_unit = fields.Float(
        string="Unit Price",
        compute='_compute_price_unit',
        digits='Product Price',
        store=True, readonly=False, required=True, precompute=True)

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


    approved_subtotal = fields.Float(
        string="Approved",
        store=True)

    approved_tax = fields.Float(
        string="Approved Tax",
        compute='_compute_amount',
        store=True, precompute=True)

    approved_total = fields.Float(
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

    claim_subtotal = fields.Float(
        string="Claim",
        store=True)

    claim_tax = fields.Float(
        string="Claim Tax",
        compute='_compute_amount',
        store=True, precompute=True)

    claim_total = fields.Float(
        string="Claim Total",
        compute='_compute_amount',
        store=True, precompute=True)

    co_insurance_subtotal = fields.Float(
        string="Co-Insurance",
        store=True)

    co_insurance_tax = fields.Float(
        string="Co-Insurance Tax",
        compute='_compute_amount',
        store=True, precompute=True)

    co_insurance_total = fields.Float(
        string="Co-Insurance Total",
        compute='_compute_amount',
        store=True, precompute=True)

    additional_subtotal = fields.Float(
        string="Additional",
        store=True)

    additional_tax = fields.Float(
        string="Additional Tax",
        compute='_compute_amount',
        store=True, precompute=True)

    additional_total = fields.Float(
        string="Additional Total",
        compute='_compute_amount',
        store=True, precompute=True)

    member_subtotal = fields.Float(
        string="Member",
        store=True)

    member_tax = fields.Float(
        string="Member Tax",

        store=True)

    member_total = fields.Float(
        string="Member Total",
        compute='_compute_amount',
        store=True, precompute=True)

    company_id = fields.Many2one(
        related='claim_id.company_id',
        store=True, index=True, precompute=True)

    tax_id = fields.Many2many(
        comodel_name='account.tax',
        string="Taxes",
        compute='_compute_tax_id',
        store=True, readonly=False, precompute=True,
        context={'active_test': False},
        check_company=True)

    currency_id = fields.Many2one(
        related='claim_id.currency_id',
        depends=['claim_id.currency_id'],
        store=True, precompute=True)

    price_subtotal = fields.Float(
        string="Subtotal",
        compute='_compute_amount',
        store=True, precompute=True)

    price_tax = fields.Float(
        string="Total Tax",
        compute='_compute_amount',
        store=True, precompute=True)
    price_total = fields.Float(
        string="Total",
        compute='_compute_amount',
        store=True, precompute=True)
    company_id = fields.Many2one(
        related='claim_id.company_id',
        store=True, index=True, precompute=True)


    claim_id = fields.Many2one('insurance.claim', string='Insurance Claim')

    @api.depends('product_id')
    def _compute_price_unit(self):
        pricelist_item_fixed_price = self.env['product.pricelist.item'].search([('pricelist_id', '=', self.claim_id.pricelist_id.id),
                                                   ('product_tmpl_id', 'in', [self.product_template_id.id])
                                                   ]).mapped('fixed_price')
        if pricelist_item_fixed_price:
            self.price_unit = max(pricelist_item_fixed_price)
        else:
            self.price_unit = self.product_template_id.list_price

    @api.depends('product_id')
    def _compute_product_template_id(self):
        for line in self:
            line.product_template_id = line.product_id.product_tmpl_id


    @api.depends('product_id','company_id')
    def _compute_tax_id(self):
        taxes_by_product_company = defaultdict(lambda: self.env['account.tax'])
        lines_by_company = defaultdict(lambda: self.env['insurance.claim.line'])
        cached_taxes = {}
        for line in self:
            lines_by_company[line.company_id] += line
        for product in self.product_id:
            for tax in product.taxes_id:
                taxes_by_product_company[(product, tax.company_id)] += tax
        for company, lines in lines_by_company.items():
            for line in lines.with_company(company):
                taxes = taxes_by_product_company[(line.product_id, company)]
                if not line.product_id or not taxes:
                    # Nothing to map
                    line.tax_id = False
                    continue
                fiscal_position = line.claim_id.fiscal_position_id
                cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
                if cache_key in cached_taxes:
                    result = cached_taxes[cache_key]
                else:
                    result = fiscal_position.map_tax(taxes)
                    cached_taxes[cache_key] = result
                # If company_id is set, always filter taxes by the company
                line.tax_id = result


    @api.constrains('approved_unit')
    def _constrains_approved_unit_price_unit(self):
        for record in self:
            if record.approved_unit > record.price_unit and record.sale_type=='insurance':
                raise ValidationError("Unit Approved must be less than Unit Price.")

    @api.depends('product_uom_qty',  'price_unit','tax_id','gross_subtotal','claim_subtotal', 'member_subtotal')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        amount_untaxed = 0
        amount_tax = 0
        for line in self:

            tax_results = line.tax_id.compute_all(
                line.price_unit,
                currency=line.currency_id,
                quantity=line.product_uom_qty,
                product=line.product_id)

            amount_untaxed = tax_results['total_excluded']
            amount_total = tax_results['total_included']
            line.update({
                'gross_subtotal': amount_untaxed,
                'gross_tax': amount_total - amount_untaxed,
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
                'approved_tax': amount_total - amount_untaxed,
                'approved_total': amount_total,
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
                (line.claim_subtotal + line.member_subtotal) / line.product_uom_qty,
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


