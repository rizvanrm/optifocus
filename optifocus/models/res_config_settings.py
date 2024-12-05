from odoo import api, fields, models
from odoo.exceptions import ValidationError
class OpticalConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sphere_min = fields.Float()
    sphere_max = fields.Float()
    cylinder_min = fields.Float()
    cylinder_max = fields.Float()
    axis_min = fields.Float()
    axis_max = fields.Float()
    addition_min = fields.Float()
    addition_max = fields.Float()
    ipd_min = fields.Float()
    ipd_max = fields.Float()

    @api.constrains(
        'sphere_min',   'sphere_max',
        'cylinder_min', 'cylinder_max',
        'axis_min',     'axis_max',
        'addition_min', 'addition_max',

    )
    def _constrains_min_max(self):
        for record in self:
            if record.sphere_min > record.sphere_max:
                raise ValidationError(
                    "Sphere Min[" + str(record.sphere_min) + "] cannot be greater than Max[" + str(record.sphere_max) + "].")
            if record.cylinder_min > record.cylinder_max:
                raise ValidationError(
                    "Cylinder Min[" + str(record.cylinder_min) + "] cannot be greater than Max[" + str(record.cylinder_max) + "].")
            if record.axis_min > record.axis_max:
                raise ValidationError(
                    "Axis Min[" + str(record.axis_min) + "] cannot be greater than Max[" + str(record.axis_max) + "].")
            if record.addition_min > record.addition_max:
                raise ValidationError(
                    "Addition Min[" + str(record.addition_min) + "] cannot be greater than Max[" + str(record.addition_max) + "].")

    def set_values(self):
        res = super(OpticalConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('optifocus.sphere_min', self.sphere_min)
        self.env['ir.config_parameter'].sudo().set_param('optifocus.sphere_max', self.sphere_max)

        self.env['ir.config_parameter'].sudo().set_param('optifocus.cylinder_min', self.cylinder_min)
        self.env['ir.config_parameter'].sudo().set_param('optifocus.cylinder_max', self.cylinder_max)

        self.env['ir.config_parameter'].sudo().set_param('optifocus.axis_min', self.axis_min)
        self.env['ir.config_parameter'].sudo().set_param('optifocus.axis_max', self.axis_max)

        self.env['ir.config_parameter'].sudo().set_param('optifocus.addition_min', self.addition_min)
        self.env['ir.config_parameter'].sudo().set_param('optifocus.addition_max', self.addition_max)

        self.env['ir.config_parameter'].sudo().set_param('optifocus.ipd_min', self.ipd_min)
        self.env['ir.config_parameter'].sudo().set_param('optifocus.ipd_max', self.ipd_max)

        return res

    @api.model
    def get_values(self):
        res = super(OpticalConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        res.update(sphere_min=ICPSudo.get_param('optifocus.sphere_min'),)
        res.update(sphere_max=ICPSudo.get_param('optifocus.sphere_max'), )

        res.update(cylinder_min=ICPSudo.get_param('optifocus.cylinder_min'), )
        res.update(cylinder_max=ICPSudo.get_param('optifocus.cylinder_max'), )

        res.update(axis_min=ICPSudo.get_param('optifocus.axis_min'), )
        res.update(axis_max=ICPSudo.get_param('optifocus.axis_max'), )

        res.update(addition_min=ICPSudo.get_param('optifocus.addition_min'), )
        res.update(addition_max=ICPSudo.get_param('optifocus.addition_max'), )

        res.update(ipd_min=ICPSudo.get_param('optifocus.ipd_min'), )
        res.update(ipd_max=ICPSudo.get_param('optifocus.ipd_max'), )

        return res

