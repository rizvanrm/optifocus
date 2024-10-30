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

    insurance_id = fields.Many2one('insurance.company', string='Insurance Company')
    insurance_pricelist_id = fields.Many2one(related='insurance_id.pricelist_id')
    policy_id = fields.Many2one('insurance.policy',
                                compute='_compute_policy_id',
                                string='Policy No', store=True,readonly=False)
    policy_class_id = fields.Many2one('insurance.policy.class', string='Class', store=True)
    policy_holder = fields.Char(related='policy_id.policy_holder', store=True)
    inception_date = fields.Date(related='policy_id.inception_date')
    expiry_date = fields.Date(related='policy_id.expiry_date')
    insurance_company_plan = fields.Many2one(related='policy_id.insurance_company_plan', store=True)
    insurance_discount = fields.Float(related='policy_id.insurance_discount', store=True)
    member_discount = fields.Float(related='policy_id.member_discount')
    co_insurance_type = fields.Selection(related='policy_class_id.co_insurance_type')
    co_insurance_percent = fields.Float(related='policy_class_id.co_insurance_percent')
    up_to = fields.Float(related='policy_class_id.up_to')
    prescription_id = fields.Many2one('optical.prescription', string='Prescription')
    doctor = fields.Many2one(related='prescription_id.doctor_id')
    prescription_type = fields.Selection(related='prescription_id.prescription_type')
    r_sph = fields.Float(related='prescription_id.r_sph')
    r_cyl = fields.Float(related='prescription_id.r_cyl')
    r_axis = fields.Float(related='prescription_id.r_axis')
    r_va = fields.Float(related='prescription_id.r_va')
    r_add = fields.Float(related='prescription_id.r_add')
    l_sph = fields.Float(related='prescription_id.l_sph')
    l_cyl = fields.Float(related='prescription_id.l_cyl')
    l_axis = fields.Float(related='prescription_id.l_axis')
    l_va = fields.Float(related='prescription_id.l_va')
    l_add = fields.Float(related='prescription_id.l_add')
    ipd_distance = fields.Float(related='prescription_id.ipd_distance')
    ipd_addition = fields.Float(related='prescription_id.ipd_addition')
    notes = fields.Text(related='prescription_id.notes')
    partner_id = fields.Many2one('res.partner',string="Customer")
    birth_date = fields.Date(related='partner_id.birth_date')
    gender = fields.Selection(related='partner_id.gender')
    mobile = fields.Char(related='partner_id.mobile')
    id_no = fields.Char(related='partner_id.id_no')
    membership_no = fields.Char(string="Membership No")
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

    approved_total = fields.Float(string="Total Approved Amount",store=True,
                                  compute='_compute_amounts')
    discount_total = fields.Float(string='Total Discount',store=True,compute='_compute_amounts')
    claim_untaxed = fields.Float(string="Untaxed Claim", store=True,compute='_compute_amounts')
    claim_tax = fields.Float(string="Taxes Claim", store=True, compute='_compute_amounts')
    claim_total = fields.Float(string="Total Claim", store=True, compute='_compute_amounts')
    co_insurance_untaxed = fields.Float(string="Untaxed Co-Insurance", store=True, compute='_compute_amounts')
    co_insurance_tax = fields.Float(string="Taxes Co-Insurance", store=True, compute='_compute_amounts')
    co_insurance_total = fields.Float(string="Total Co-Insurance", store=True, compute='_compute_amounts')
    additional_untaxed = fields.Float(string="Untaxed Additional", store=True, compute='_compute_amounts')
    additional_tax = fields.Float(string="Taxes Additional", store=True, compute='_compute_amounts')
    additional_total = fields.Float(string="Total Additional", store=True, compute='_compute_amounts')
    member_untaxed = fields.Float(string="Untaxed Member", store=True, compute='_compute_amounts')
    member_tax = fields.Float(string="Taxes Member", store=True, compute='_compute_amounts')
    member_total = fields.Float(string="Total Member", store=True, compute='_compute_amounts')

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

    @api.onchange('insurance_id')
    def onchange_insurance_id(self):
        self.policy_id = None

    @api.onchange('policy_id')
    def onchange_policy_id(self):
        self.policy_class_id = None

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
            claim.pricelist_id = claim.insurance_pricelist_id
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
    @api.depends('insurance_id', 'policy_id', 'policy_class_id',
                 'claim_line.price_subtotal', 'claim_line.price_tax', 'claim_line.price_total',
                 'claim_line.claim_subtotal', 'claim_line.claim_tax', 'claim_line.claim_total',
                 'claim_line.co_insurance_subtotal', 'claim_line.co_insurance_tax', 'claim_line.co_insurance_total',
                 'claim_line.additional_subtotal', 'claim_line.additional_tax', 'claim_line.additional_total',
                 'claim_line.member_subtotal', 'claim_line.member_tax', 'claim_line.member_total',
                 'claim_line.price_subtotal', 'claim_line.price_tax', 'claim_line.price_total')
    def _compute_amounts(self):

        for claim in self:
            claim_lines = claim.claim_line

            approved_total = sum(claim_lines.mapped('approved_subtotal'))
            discount_total=sum(claim_lines.mapped('claim_discount_subtotal') +
                               claim_lines.mapped('member_discount_subtotal'))

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

    @api.onchange( "insurance_id", "policy_id", "policy_class_id", "claim_line")
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

    approved_subtotal = fields.Float(
        string="Approved",
        store=True)

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

    @api.depends('product_id','product_uom_qty')
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

    @api.depends('product_uom_qty',  'price_unit','claim_subtotal', 'member_subtotal')
    def _compute_amount(self):

        """
        Compute the amounts of the SO line.

        """
        for line in self:

            tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict(
               line.claim_subtotal / line.product_uom_qty, line.claim_subtotal)])

            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']
            line.update({
                'claim_subtotal': amount_untaxed,
                'claim_tax': amount_tax,
                'claim_total': amount_untaxed + amount_tax,
            })

            tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict(
                line.co_insurance_subtotal / line.product_uom_qty, line.co_insurance_subtotal)])
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']
            line.update({
                'co_insurance_subtotal': amount_untaxed,
                'co_insurance_tax': amount_tax,
                'co_insurance_total': amount_untaxed + amount_tax,
            })

            tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict(
                line.additional_subtotal / line.product_uom_qty, line.additional_subtotal)])
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']
            line.update({
                'additional_subtotal': amount_untaxed,
                'additional_tax': amount_tax,
                'additional_total': amount_untaxed + amount_tax,
            })

            tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict(
                line.member_subtotal / line.product_uom_qty, line.member_subtotal)])
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']
            line.update({
                'member_subtotal': amount_untaxed,
                'member_tax': amount_tax,
                'member_total': amount_untaxed + amount_tax,
            })

            tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict(
                (line.claim_subtotal + line.member_subtotal) / line.product_uom_qty,
                (line.claim_subtotal + line.member_subtotal))])
            totals = list(tax_results['totals'].values())[0]

            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']
            line.update({
                'price_subtotal': amount_untaxed,
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
            })

    #
    def _convert_to_tax_base_line_dict(self, price_unit=None, price_subtotal=None):

        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
       """
        if price_unit == None:
            self.ensure_one()
            return self.env['account.tax']._convert_to_tax_base_line_dict(
                self,
                partner=self.claim_id.partner_id,
                currency=self.claim_id.currency_id,
                product=self.product_id,
                taxes=self.tax_id,
                price_unit=self.claim_subtotal + self.member_subtotal,
                quantity=1,
                discount=0,
                price_subtotal=self.claim_subtotal + self.member_subtotal,
            )
        else:
            self.ensure_one()
            return self.env['account.tax']._convert_to_tax_base_line_dict(
                self,
                partner=self.claim_id.partner_id,
                currency=self.claim_id.currency_id,
                product=self.product_id,
                taxes=self.tax_id,
                price_unit=price_unit,
                quantity=self.product_uom_qty,
                discount=0,
                price_subtotal=price_subtotal,
            )
