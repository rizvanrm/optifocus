# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    global_discount_default_product_id = fields.Many2one(
        'product.product',
        'Global Discount',
        domain="[('type', '=', 'service')]",
        config_parameter='optifocus.default_global_discount_product_id',
        help='Default product used for Global discount')

    invoicing_policy_insurance_selection = fields.Selection([
        ('invoice_member', 'Member Invoice'),
        ('invoice_member_claim', 'Member and Claim Invoice')],
        string="Define the invoicing policy for Insurnace sales orders.",
        required=True, default='invoice_member',
        config_parameter='optifocus.invoicing_policy_insurance_selection')

    commercial_partner = fields.Boolean(string='Commercial Partner', config_parameter='optifocus.commercial_partner')
