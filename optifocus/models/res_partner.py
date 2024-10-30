from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    id_no = fields.Char(string='Identification No')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
        ])
    mobile = fields.Char(string='Mobile',required=True)
    prescription_count=fields.Integer(compute='_compute_prescription_count', string='Prescriptions')
    insurance_policy_count=fields.Integer(compute='_compute_insurance_policy_count', string='Insurance Policies')
    birth_date = fields.Date(string="Date of Birth")
    is_commercial_partner = fields.Boolean('Is Commercial Partner', default=False)


    @api.constrains('gender')
    def _constrains_gender(self):
        if self.company_type == 'person' and not self.gender:
            raise ValidationError("Invalid field: Gender.")

    def _compute_prescription_count(self):
        prescription_count = self.env['optical.prescription'].search_count([('partner_id', '=', self.id)])
        self.prescription_count = prescription_count

    def _compute_insurance_policy_count(self):
        insurance_policy_count = self.env['sale.order'].search_count([('partner_id','=',self.id),('sale_type','=','insurance')])
        self.insurance_policy_count = insurance_policy_count

    def action_open_prescriptions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'optical.prescription',
            'domain': [('partner_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_open_insurance_policies(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Insurance Policies',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'target' : 'current',
            'domain':[('partner_id','=',self.id),('sale_type','=','insurance')],
        }

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args += ['|', '|','|', ('name', operator, name), ('mobile', operator, name),
                     ('phone', operator, name),('id_no', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)