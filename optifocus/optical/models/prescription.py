from odoo import models, fields,api
from odoo.exceptions import UserError, ValidationError


class Prescription(models.Model):
    _name = "optical.prescription"
    _description = "Prescription"
    _rec_name = 'prescription_date'

    doctor_id = fields.Many2one('hr.employee', string='Optometrist', required=True, domain="[('job_id', '=', 'Optometrist')]")
    prescription_date = fields.Datetime(string="Date", required=True,default=fields.datetime.now())

    prescription_type = fields.Selection([
        ('distance', 'DISTANCE'),
        ('reading', 'READING'),
        ('bifocal_progressive', 'BIFOCAL/PROGRESSIVE'),
    ], string="Prescription Type",required=True)
    partner_id = fields.Many2one('res.partner',
                                 string='Customer',required=True)
    mobile = fields.Char(related='partner_id.mobile')
    r_sph=fields.Float(string='Right Sphere')
    r_cyl=fields.Float(string='Right Cylinder')
    r_axis=fields.Float(string='Right Axis')
    r_va=fields.Float(string='Right Visual Acuity')
    r_add=fields.Float(string='Right Addition')
    l_sph = fields.Float(string='Lef Sphere')
    l_cyl = fields.Float(string='Left Cylinder')
    l_axis = fields.Float(string='Left Axis')
    l_va = fields.Float(string='Left Visual Acuity')
    l_add = fields.Float(string='Left Addition')
    ipd_distance=fields.Float(string='Interpupillary Distance Distance')
    ipd_addition = fields.Float(string=' Interpupillary Distance  Addition')
    notes=fields.Text()

    @api.constrains('r_sph','r_cyl','r_axis','r_add','l_sph','l_cyl','l_axis','l_add','ipd_distance','ipd_addition')
    def _constrains_from_to(self):

        sphere_min = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.sphere_min'))
        sphere_max = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.sphere_max'))

        cylinder_min = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.cylinder_min'))
        cylinder_max = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.cylinder_max'))

        axis_min = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.axis_min'))
        axis_max = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.axis_max'))

        addition_min = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.addition_min'))
        addition_max = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.addition_max'))

        va_min = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.va_min'))
        va_max = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.va_max'))

        ipd_min = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.ipd_min'))
        ipd_max = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.ipd_max'))

        for record in self:
            if self.r_sph < sphere_min or self.r_sph > sphere_max:
                raise ValidationError("Right Sphere Value not in the Range Specified in Settings.")
            if self.r_cyl < cylinder_min or self.r_cyl > cylinder_max:
                raise ValidationError("Right Cylinder Value not in the Range Specified in Settings.")
            if self.r_axis < axis_min or self.r_axis > axis_max:
                raise ValidationError("Right Axis Value not in the Range Specified in Settings.")
            if self.r_add < addition_min or self.r_add > addition_max:
                raise ValidationError("Right Addition Value not in the Range Specified in Settings.")
            if self.r_va < va_min or self.r_va > va_max:
                raise ValidationError("Right VA Value not in the Range Specified in Settings.")
            if self.ipd_distance < ipd_min or self.ipd_distance > ipd_max:
                raise ValidationError("Distance IPD Value not in the Range Specified in Settings.")

            if record.r_sph % 0.25 != 0:
                raise ValidationError("Right Sphere [" + str(record.r_sph) + "] must be a multiple of 0.25")
            if record.r_cyl % 0.25 != 0:
                raise ValidationError("Right Cylinder [" + str(record.r_cyl) + "] must be a multiple of 0.25")
            if record.r_add % 0.25 != 0:
                raise ValidationError("Right Addition [" + str(record.r_add) + "] must be a multiple of 0.25")

            if self.l_sph < sphere_min or self.l_sph > sphere_max:
                raise ValidationError("Left Sphere Value not in the Range Specified in Settings.")
            if self.l_cyl < cylinder_min or self.l_cyl > cylinder_max:
                raise ValidationError("Left Cylinder Value not in the Range Specified in Settings.")
            if self.l_axis < axis_min or self.l_axis > axis_max:
                raise ValidationError("Left Axis Value not in the Range Specified in Settings.")
            if self.l_add < addition_min or self.l_add > addition_max:
                raise ValidationError("Left Addition Value not in the Range Specified in Settings.")
            if self.l_va < va_min or self.l_va > va_max:
                raise ValidationError("Left VA Value not in the Range Specified in Settings.")
            if self.ipd_addition < ipd_min or self.ipd_addition > ipd_max:
                raise ValidationError("Addition IPD Value not in the Range Specified in Settings.")

            if record.l_sph % 0.25 != 0:
                raise ValidationError("Left Sphere [" + str(record.l_sph) + "] must be a multiple of 0.25")
            if record.l_cyl % 0.25 != 0:
                raise ValidationError("Left Cylinder [" + str(record.l_cyl) + "] must be a multiple of 0.25")
            if record.l_add % 0.25 != 0:
                raise ValidationError("Left Addition [" + str(record.l_add) + "] must be a multiple of 0.25")

