from odoo import models, fields,api
from odoo.exceptions import UserError, ValidationError
import re

class Prescription(models.Model):
    _name = "optical.prescription"
    _description = "Prescription"
    _rec_name = 'prescription_date'

    doctor_id = fields.Many2one('hr.employee', string='Optometrist', required=True, domain="[('job_id', '=', 'Optometrist')]")
    prescription_date = fields.Datetime(string="Date", required=True, default = lambda self: fields.Datetime.now())


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
    # r_va_numerator = fields.Integer(string="Numerator")
    # r_va_denominator = fields.Integer(string="Denominator")
    # r_va = fields.Char(string="Right Visual Acuity", compute="_compute_r_va", store=True)
    r_va = fields.Char(string="Right Visual Acuity")
    r_add=fields.Float(string='Right Addition')
    l_sph = fields.Float(string='Lef Sphere')
    l_cyl = fields.Float(string='Left Cylinder')
    l_axis = fields.Float(string='Left Axis')
    # l_va_numerator = fields.Integer(string="Numerator")
    # l_va_denominator = fields.Integer(string="Denominator")
    l_va = fields.Char(string="Left Visual Acuity")
    # l_va = fields.Char(string="Left Visual Acuity", compute="_compute_l_va", store=True)
    l_add = fields.Float(string='Left Addition')
    ipd_distance=fields.Float(string='Interpupillary Distance Distance')
    ipd_addition = fields.Float(string=' Interpupillary Distance  Addition')
    notes=fields.Text()
    prescription_filename = fields.Char(compute='_compute_prescription_filename')
    prescription_attach_id = fields.Binary(string="Prescription Attachment")


    # @api.depends('l_va_numerator', 'l_va_denominator')
    # def _compute_l_va(self):
    #     for rec in self:
    #         rec.l_va = f"{rec.l_va_numerator } / {rec.l_va_denominator}"
    #
    # @api.depends('r_va_numerator', 'r_va_denominator')
    # def _compute_r_va(self):
    #     for rec in self:
    #         rec.r_va = f"{rec.r_va_numerator} / {rec.r_va_denominator}"


    @api.depends('prescription_date')
    def _compute_prescription_filename(self):
        for rec in self:
            rec.prescription_filename = 'P' + (str(rec.prescription_date) or '')

    @api.constrains('r_sph','r_cyl','r_axis','r_add','l_sph','l_cyl','l_axis','l_add','ipd_distance','ipd_addition','r_va','l_va')
    def _constrains_from_to(self):

        sphere_min = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.sphere_min'))
        sphere_max = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.sphere_max'))

        cylinder_min = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.cylinder_min'))
        cylinder_max = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.cylinder_max'))

        axis_min = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.axis_min'))
        axis_max = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.axis_max'))

        addition_min = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.addition_min'))
        addition_max = float(self.env['ir.config_parameter'].sudo().get_param('optifocus.addition_max'))

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
            if self.ipd_distance!=0 and (self.ipd_distance < ipd_min or self.ipd_distance > ipd_max)  :
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

            if self.ipd_addition != 0 and (self.ipd_addition < ipd_min or self.ipd_addition > ipd_max):
                raise ValidationError("Addition IPD Value not in the Range Specified in Settings.")

            if record.l_sph % 0.25 != 0:
                raise ValidationError("Left Sphere [" + str(record.l_sph) + "] must be a multiple of 0.25")
            if record.l_cyl % 0.25 != 0:
                raise ValidationError("Left Cylinder [" + str(record.l_cyl) + "] must be a multiple of 0.25")
            if record.l_add % 0.25 != 0:
                raise ValidationError("Left Addition [" + str(record.l_add) + "] must be a multiple of 0.25")

            if record.r_va and not re.match(r'^\d+/\d+$', record.r_va):
                raise ValidationError("Right Visual Acuity must be in the format Ex. 6/6.")
            elif record.r_va:
                r_numerator, r_denominator = record.r_va.split("/")
                if float(r_numerator) in [6,20]:
                    if float(r_numerator)==6:
                        if float(r_denominator) not in [6, 9, 12, 18, 24, 36, 60, 120]:
                            raise ValidationError("Right VA Denominator must be a standard value in [6, 9, 12, 18, 24, 36, 60, 120] (meters).")
                    elif float(r_numerator) == 20:
                        if float(r_denominator) not in [20, 25, 30, 40, 50, 70, 100, 200, 400]:
                            raise ValidationError(
                                "Right VA Denominator must be a standard value in [20, 25, 30, 40, 50, 70, 100, 200, 400] (feet).")

                else:
                    raise ValidationError("Right VA Numerator must be 6 (meters) or 20 (feet).")

            if record.l_va and not re.match(r'^\d+/\d+$', record.l_va):
                raise ValidationError("Left Visual Acuity must be in the format Ex. 6/6.")
            elif record.l_va:
                l_numerator, l_denominator = record.l_va.split("/")
                if float(l_numerator) in [6, 20]:
                    if float(l_numerator) == 6:
                        if float(l_denominator) not in [6, 9, 12, 18, 24, 36, 60, 120]:
                            raise ValidationError(
                                "Left VA Denominator must be a standard value in [6, 9, 12, 18, 24, 36, 60, 120] (meters).")
                    elif float(l_numerator) == 20:
                        if float(l_denominator) not in [20, 25, 30, 40, 50, 70, 100, 200, 400]:
                            raise ValidationError(
                                "Left VA Denominator must be a standard value in [20, 25, 30, 40, 50, 70, 100, 200, 400] (feet).")
                else:
                    raise ValidationError("Left VA Numerator must be 6 (meters) or 20 (feet).")


