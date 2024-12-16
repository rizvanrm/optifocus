from odoo import models, fields,api, Command,_
from odoo.exceptions import UserError, ValidationError

class InsurancePolicy(models.Model):
    _name = "insurance.policy"
    _description = "Insurance Policy"

    name = fields.Char(string="Policy No", required=True)
    policy_holder = fields.Char(string="Policy Holder", required=True,store=True)
    inception_date = fields.Date(string="Inception Date", required=True)
    expiry_date = fields.Date(string="Expiry Date", required=True)
    policy_line = fields.One2many('insurance.policy.class', 'policy_id', string='Policy Lines')
    insurance_company = fields.Many2one('insurance.company',string='Insurance Company', required=True)
    insurance_company_plan = fields.Many2one('insurance.plan', string='Plan',required=True,domain="[('insurance_company_id', '=', insurance_company)]")
    insurance_discount = fields.Float(related='insurance_company_plan.insurance_discount')
    member_discount = fields.Float(related='insurance_company_plan.member_discount')
    member_count = fields.Integer(string="Member Count", compute='_get_member')
    sale_count = fields.Integer(string="Sale Count", compute='_get_sale')
    claim_count = fields.Integer(string="Claim Count", compute='_get_claim')


    def _get_member(self):
        member_count = self.env['insurance.member'].search_count([('insurance_company_id', '=', self.id)])
        self.member_count = member_count

    def _get_claim(self):
        claim_count = self.env['insurance.claim'].search_count([('insurance_id', '=', self.id)])
        self.claim_count = claim_count

    def _get_sale(self):
        sale_count = self.env['sale.order'].search_count([('insurance_id', '=', self.id)])
        self.sale_count = sale_count

    def action_view_member(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Members',
            'res_model': 'insurance.member',
            'domain': [('insurance_company_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_view_sale(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale',
            'res_model': 'sale.order',
            'domain': [('insurance_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_view_claim(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'claim',
            'res_model': 'insurance.claim',
            'domain': [('insurance_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }


    # Onchange - On change Parent Field, List associated Child Records.
    @api.onchange('insurance_company')
    def onchange_insurance_company_name(self):
        self.insurance_company_plan=None
        # for rec in self:
        #     return {'domain': {'insurance_company_plan': [('insurance_company_id', '=', rec.insurance_company.name)]}}

    # Constraint - at least one Child Record required
    @api.constrains('policy_line_ids')
    def _constrains_policy_line_ids(self):
        if not self.policy_line or len(self.policy_line) == 0:
            raise ValidationError("At least one Class to the Policy is a must")

    def copy_data(self, default=None):
        if default is None:
            default = {}
        if 'name' not in default:
            default['name'] = _("%s (copy)", self.name)
        if 'policy_line' not in default:
            default['policy_line'] = [
                Command.create(line.copy_data()[0])
                for line in self.policy_line
            ]
        return super().copy_data(default)

    _sql_constraints = [
        # Constraint Unique Record
        ('name_uniq', 'unique (name,insurance_company)', 'Policy No must be unique per Insurance Company.'),
        # Constraint Inception Date is less than Expiry Date
        ('date_check', "CHECK ( (inception_date <= expiry_date))", "The Expiry Date must be greater than or equal to the Inception Date.")
    ]


class InsurancePolicyClass(models.Model):
    _name = "insurance.policy.class"
    _description = "Insurance Policy Class"

    name = fields.Char(string="Class", required=True)
    co_insurance_type = fields.Selection([('percentage', '%'), ('fixed', 'Fixed')], string="Co-Insurance Type" , required=True)
    co_insurance_percent = fields.Float(string="Co-Insurance %")
    up_to = fields.Float(string="Up To")
    policy_id = fields.Many2one('insurance.policy', string='Insurance Policy')

    @api.onchange('co_insurance_type')
    def onchange_insurance_company_name(self):
        if self.co_insurance_type == "fixed":
            self.co_insurance_percent = 0

    # Constraint Unique Line Record
    _sql_constraints = [('policy_class_uniq', 'unique (policy_id,name)',
                          'A Class name must be unique per Policy.')
                         ]
