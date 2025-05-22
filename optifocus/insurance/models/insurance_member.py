from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command


class InsuranceMember(models.Model):
    _name = "insurance.member"
    _description = "Insurance Member"


    name = fields.Char(string="Membership No", required=True)
    partner_id = fields.Many2one('res.partner', string="Customer", required=True)
    birth_date = fields.Date(related='partner_id.birth_date', required=True)
    gender = fields.Selection(related='partner_id.gender', required=True)
    mobile = fields.Char(related='partner_id.mobile',store=True)
    id_no = fields.Char(related='partner_id.id_no', required=True)
    policy_id = fields.Many2one('insurance.policy',
                                string='Policy No', required=True)

    policy_holder = fields.Char(related='policy_id.policy_holder', store=True)
    inception_date = fields.Date(related='policy_id.inception_date',store=True)
    expiry_date = fields.Date(related='policy_id.expiry_date',store=True)

    policy_class_id = fields.Many2one('insurance.policy.class', string='Class', required=True,store=True,
                                      domain = "[('policy_id', '=', policy_id)]")


    co_insurance_type = fields.Selection(related='policy_class_id.co_insurance_type',store=True)
    co_insurance_percent = fields.Float(related='policy_class_id.co_insurance_percent',store=True)
    up_to = fields.Float(related='policy_class_id.up_to',store=True)
    co_insurance = fields.Char(string="Co-Insurance", compute="_compute_co_insurance",store=True)
    insurance_company_id = fields.Many2one(related='policy_id.insurance_company',store=True)
    insurance_company_plan_id = fields.Many2one(related='policy_id.insurance_company_plan',store=True)
    insurance_discount = fields.Float(related='policy_id.insurance_discount', store=True)
    member_discount = fields.Float(related='policy_id.member_discount',store=True)

    sale_count = fields.Integer(string="Sale Count", compute='_get_sale')
    claim_count = fields.Integer(string="Claim Count", compute='_get_claim')




    @api.depends('co_insurance_type', 'co_insurance_percent','up_to')
    def _compute_co_insurance(self):
        for record in self:
            if record.co_insurance_type == 'fixed':
                record.co_insurance = f" {record.up_to or ''}"
            else:
                record.co_insurance = f"{str(record.co_insurance_percent)+ '%' or ''} Upto {record.up_to or ''}"

    @api.onchange('policy_id')
    def _onchange_policy_id(self):
        """Clear the class_id field when policy_id changes."""
        self.policy_class_id = False

    def _get_claim(self):
        claim_count = self.env['insurance.claim'].search_count([('member_id', '=', self.id)])
        self.claim_count = claim_count
    def _get_sale(self):
        sale_count = self.env['sale.order'].search_count([('member_id', '=', self.id)])
        self.sale_count = sale_count

    def action_open_sales(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales'),
            'res_model': 'sale.order',
            'domain': [('member_id', '=', self.id)],
            'views': [(self.env.ref('optifocus.view_order_tree').id, "list"),
                      (self.env.ref('optifocus.sale_order_form_view').id, "form")],
        }

    def action_open_claims(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Claims'),
            'res_model': 'insurance.claim',
            'domain': [('member_id', '=', self.id)],
            'views': [(self.env.ref('optifocus.insurance_claim_list_view').id, "list"),
                      (self.env.ref('optifocus.claim_form_view').id, "form")],
        }


    def copy_data(self, default=None):
        if default is None:
            default = {}
        if 'name' not in default:
            default['name'] = _("%s (copy)", self.name)
        return super().copy_data(default)

    # Constraint Unique Record
    _sql_constraints = [
        ('membership_no_uniq', 'unique (name,insurance_company_id)', 'A Membership No must be unique per Insurnace Compnay.'),
    ]

    def name_get(self):
        """Display a combination of name and code as the record name."""
        result = []
        for record in self:
            display_name = f"{record.name or ''} [{record.insurance_company_id.name or ''}]"
            result.append((record.id, display_name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []

        if name:
            domain = ['|', '|', ('name', operator, name), ('mobile', operator, name), ('id_no', operator, name)]
        else:
            domain = []

        records = self.search(domain + args, limit=limit)
        return records.name_get()