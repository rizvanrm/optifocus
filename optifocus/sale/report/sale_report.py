from odoo import models,fields


class SaleReport(models.Model):
    _inherit = "sale.report"

    sale_type = fields.Selection([
        ('retail', 'Retail'),
        ('insurance', 'Insurance'),
        ('wholesale', 'Wholesale')
    ], string="Sale Type", default='retail',readonly=True)

    brand_id = fields.Many2one('product.brand', string='Brand', readonly=True)
    insurance_id = fields.Many2one('insurance.company', string='Insurance Company')
    policy_id = fields.Many2one('insurance.policy', string='Policy', store=True)
    policy_holder = fields.Char(related='policy_id.policy_holder', store=True)
    insurance_company_plan = fields.Many2one(related='policy_id.insurance_company_plan', store=True)
    approved_subtotal = fields.Float("Untaxed Approved Amount",readonly=True)
    claim_discount_subtotal = fields.Float("Claim Discount",readonly=True)
    member_discount_subtotal = fields.Float("Member Discount", readonly=True)
    discount_subtotal = fields.Float("Total Discount", readonly=True)
    claim_subtotal = fields.Float("Untaxed Claim Amount",readonly=True)
    co_insurance_subtotal = fields.Float("Untaxed Co-Insurance Amount")
    additional_subtotal = fields.Float("Untaxed Additional Amount")
    member_subtotal = fields.Float("Untaxed Member Amount")
    claim_total = fields.Float("Taxed Claim Amount",readonly=True)
    co_insurance_total = fields.Float("Taxed Co-Insurance Amount")
    additional_total = fields.Float("Taxed Additional Amount")
    member_total = fields.Float("Taxed Member Amouont")
    partner_id = fields.Many2one('res.partner')

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['brand_id'] = "t.brand_id"
        res['insurance_id'] = "s.insurance_id"
        res['sale_type'] = "s.sale_type"
        res['policy_id'] = "s.policy_id"
        res['policy_holder'] = "s.policy_holder"
        res['insurance_company_plan'] = "s.insurance_company_plan"

        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
              s.sale_type,s.insurance_id,s.policy_holder,s.insurance_company_plan,t.brand_id"""

        return res

    def _select_sale(self):
        return super(SaleReport,self)._select_sale() + ",sum(l.approved_subtotal) as approved_subtotal" + \
            ",sum(l.claim_discount_subtotal) as claim_discount_subtotal" + \
            ",sum(l.member_discount_subtotal) as member_discount_subtotal" + \
            ",sum(l.discount_subtotal) as discount_subtotal" + \
            ",sum(l.claim_subtotal) as claim_subtotal" + \
            ",sum(l.co_insurance_subtotal) as co_insurance_subtotal"+ \
            ",sum(l.additional_subtotal) as additional_subtotal" + \
            ",sum(l.member_subtotal) as member_subtotal" + \
            ",sum(l.claim_total) as claim_total" + \
            ",sum(l.co_insurance_total) as co_insurance_total" + \
            ",sum(l.additional_total) as additional_total" + \
            ",sum(l.member_total) as member_total"

