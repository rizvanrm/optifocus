# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import traceback
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    insurance_sales_order_workflow_selection = fields.Selection([
        ('centralized', 'Centralized'),
        ('decentralized', 'Individual')],
        string="Insurance Sales Order Workflow",
        required=True, default='decentralized',
        config_parameter='optifocus.insurance_sales_order_workflow_selection')

    invoicing_policy_insurance_selection = fields.Selection([
        ('invoice_member', 'Member Invoice'),
        ('invoice_member_claim', 'Member and Claim Invoice')],
        string="Define the invoicing policy for Insurnace sales orders.",
        required=True, default='invoice_member',
        config_parameter='optifocus.invoicing_policy_insurance_selection')

    commercial_partner = fields.Boolean(string='Commercial Partner', config_parameter='optifocus.commercial_partner')

    line_coupon_discount = fields.Boolean(string="Dual Discount (Line + Coupon)", config_parameter='sale.line_coupon_discount')
    line_global_discount = fields.Boolean(string="Dual Discount (Line + Global)", config_parameter='sale.line_global_discount')
    coupon_global_discount = fields.Boolean(string="Dual Discount (Coupon + Global)", config_parameter='sale.coupon_global_discount')
    # line_coupon_global_discount = fields.Boolean(string="Triple Discount (Line + Coupon + Global)",
    #                                         config_parameter='sale.line_coupon_global_discount')






