from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command


class InsuranceCompany(models.Model):
    _name = "insurance.company"
    _description = "Insurance Company"

    name = fields.Char(string="Insurance Company", required=True)
    policy_count = fields.Integer(string="Policy Count", compute='_get_policy')
    member_count = fields.Integer(string="Member Count", compute='_get_member')
    sale_count = fields.Integer(string="Sale Count", compute='_get_sale')
    claim_count = fields.Integer(string="Claim Count", compute='_get_claim')
    short_name = fields.Char(string="Short Name")
    provider_id=fields.Char(string="Provider ID", required=True)
    partner_id = fields.Many2one('res.partner', string="Customer", required=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist',required=True)
    insurance_company_line = fields.One2many('insurance.plan', 'insurance_company_id', string='Insurance Lines')

    def _get_policy(self):
        policy_count = self.env['insurance.policy'].search_count([('insurance_company', '=', self.id)])
        self.policy_count = policy_count
    def _get_member(self):
        member_count = self.env['insurance.member'].search_count([('insurance_company_id', '=', self.id)])
        self.member_count = member_count
    def _get_claim(self):
        claim_count = self.env['insurance.claim'].search_count([('insurance_id', '=', self.id)])
        self.claim_count = claim_count
    def _get_sale(self):
        sale_count = self.env['sale.order'].search_count([('insurance_id', '=', self.id)])
        self.sale_count = sale_count

    def action_open_policies(self):
        self.ensure_one()
        return {
            'name': _('Insurance Policies'),
            'type': 'ir.actions.act_window',
            'res_model': 'insurance.policy',
            'views': [(self.env.ref('optifocus.insurance_policy_list_view').id, "list"),
                      (self.env.ref('optifocus.insurance_policy_form_view').id, "form")],
            'domain': [('insurance_company', '=', self.id)],
        }


    def action_open_members(self):
        self.ensure_one()
        return {
            'name': _('Insurance Members'),
            'type': 'ir.actions.act_window',
            'res_model': 'insurance.member',
            'views': [(self.env.ref('optifocus.insurance_member_list_view').id, "list"),
                      (self.env.ref('optifocus.insurance_member_form_view').id, "form")],
            'domain': [('insurance_company_id', '=', self.id)],
        }

    def action_open_sales(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales'),
            'res_model': 'sale.order',
            'domain': [('insurance_id', '=', self.id)],
            'views': [(self.env.ref('optifocus.view_order_tree').id, "list"),
                      (self.env.ref('optifocus.sale_order_form_view').id, "form")],
        }

    def action_open_claims(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Claims'),
            'res_model': 'insurance.claim',
            'domain': [('insurance_id', '=', self.id)],
            'views': [(self.env.ref('optifocus.insurance_claim_list_view').id, "list"),
                      (self.env.ref('optifocus.claim_form_view').id, "form")],
        }

    # Constraint - at least one Child Record required
    @api.constrains('insurance_company_line')
    def _constrains_insurance_company_line(self):
        if not self.insurance_company_line or len(self.insurance_company_line) == 0:
            raise ValidationError("At least one Plan to the Insurance Company is a must.")

    def copy_data(self, default=None):
        if default is None:
            default = {}
        if 'name' not in default:
            default['name'] = _("%s (copy)", self.name)
        if 'insurance_company_line' not in default:
            default['insurance_company_line'] = [
                Command.create(line.copy_data()[0])
                for line in self.insurance_company_line
            ]
        return super().copy_data(default)

    # Constraint Unique Record
    _sql_constraints = [
        ('insurance_company_uniq', 'unique (name)', 'Insurance Company must be unique.'),
    ]


class InsurancePlan(models.Model):
    _name = "insurance.plan"
    _description = "Insurance Plan"

    name = fields.Char(string="Plan", required=True)
    insurance_discount = fields.Float(string="Insurance Discount")
    member_discount = fields.Float(string="Member Discount")
    insurance_company_id = fields.Many2one('insurance.company', string='Insurance Company')

    # Constraint Unique Line Record
    _sql_constraints = [('insurance_plan_uniq', 'unique (insurance_company_id,name)',
                         'A Plan name must be unique per Insurance Company.')
                        ]


