# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ResCompany(models.Model):
    _name = 'res.company'
    _description = 'Companies'
    _inherit = 'res.company'

    chi_id = fields.Char(string="CHI ID", required=True)
    nphies_id = fields.Char(string="Nphies ID", required=True)

    # Constraint Unique Record
    _sql_constraints = [
        ('chi_id_uniq', 'unique (chi_id)', 'CHI ID must be unique.'),
        ('nphies_id_uniq', 'unique (nphies_id)', 'Nphies ID must be unique.'),
    ]

