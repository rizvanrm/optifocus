# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    workshop_categ_ids = fields.Many2many(
        'product.category',
        string="Workshop Workflow in Delivery Orders",
    )

    workshop_categ_ids_str = fields.Char(string="Serialized Categories", config_parameter="optifocus.workshop_categ_ids")

    @api.onchange('workshop_categ_ids')
    def _onchange_workshop_categ_ids(self):
        """Convert Many2many categories to a comma-separated string for storage."""
        self.workshop_categ_ids_str = ",".join(str(cat.id) for cat in self.workshop_categ_ids)

    @api.model
    def get_values(self):
        """Load saved values from config_parameter and convert to Many2many."""
        res = super(ResConfigSettings, self).get_values()
        workshop_categ_ids_str = self.env['ir.config_parameter'].sudo().get_param('optifocus.workshop_categ_ids', '')
        workshop_categ_ids = [int(cid) for cid in workshop_categ_ids_str.split(',') if cid]
        res.update(workshop_categ_ids=[(6, 0, workshop_categ_ids)])
        return res

    def set_values(self):
        """Save selected product categories as a comma-separated string in ir.config_parameter"""
        super(ResConfigSettings, self).set_values()
        workshop_categ_ids_str = ",".join(str(cat.id) for cat in self.workshop_categ_ids)
        self.env['ir.config_parameter'].sudo().set_param('optifocus.workshop_categ_ids', workshop_categ_ids_str)
