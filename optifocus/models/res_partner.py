from odoo import models, _, fields, api
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
    insurance_membership_count=fields.Integer(compute='_compute_insurance_membership_count', string='Insurance Memberships')
    birth_date = fields.Date(string="Date of Birth")
    is_commercial_partner = fields.Boolean('Is Commercial Partner', default=False)

    def _compute_prescription_count(self):
        prescription_count = self.env['optical.prescription'].search_count([('partner_id', '=', self.id)])
        self.prescription_count = prescription_count

    def _compute_insurance_membership_count(self):
        insurance_membership_count = self.env['insurance.member'].search_count([('partner_id','=',self.id)])
        self.insurance_membership_count = insurance_membership_count

    def action_open_prescriptions(self):
        self.ensure_one()
        if self.prescription_count > 1:
            return {
                'name': _('Prescriptions'),
                'type': 'ir.actions.act_window',
                'res_model': 'optical.prescription',
                'views': [(self.env.ref('optifocus.optical_prescription_list_view').id, "list"),
                      (self.env.ref('optifocus.optical_prescription_form_view').id, "form")],
                'domain': [('partner_id', '=', self.id)],
            }

        return {
            'name': _('Prescription'),
            'type': 'ir.actions.act_window',
            'res_model': 'optical.prescription',
            'view_mode': 'form',
            'res_id':  self.env['optical.prescription'].search([('partner_id', '=', self.id)], limit=1).id
        }

    def action_open_insurance_memberships(self):
        self.ensure_one()
        if self.insurance_membership_count > 1:
            return {
                'name': _('Insurance Memberships'),
                'type': 'ir.actions.act_window',
                'res_model': 'insurance.member',
                'views': [(self.env.ref('optifocus.insurance_member_list_view').id, "list"),
                          (self.env.ref('optifocus.insurance_member_list_view').id, "form")],
                'domain': [('partner_id', '=', self.id)],
            }

        return {
            'name': _('Insurance Membership'),
            'type': 'ir.actions.act_window',
            'res_model': 'insurance.member',
            'view_mode': 'form',
            'res_id': self.env['insurance.member'].search([('partner_id', '=', self.id)], limit=1).id
        }

    
    def name_get(self):
        """Custom name_get to return name with mobile or ID if available"""
        result = []
        for rec in self:
            name = rec.name
            result.append((rec.id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []

        if name:
            domain = ['|', '|','|', ('name', operator, name), ('mobile', operator, name),('phone', operator, name),('id_no', operator, name)]
        else:
            domain = []

        records = self.search(domain + args, limit=limit)
        return records.name_get()





