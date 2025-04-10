from odoo import api, fields, models, _
from odoo.tools import date_utils



class ExpensesPayments(models.TransientModel):

    _name = 'expenses.payments.wizard'
    _description = 'Expense Payments'

    date_from = fields.Date(string="Date From", required=True,
                            default=date_utils.start_of(date_utils.subtract(fields.date.today(), months=1), "month"))
    date_to = fields.Date(string="Date To", required=True,
                          default=date_utils.end_of(date_utils.subtract(fields.date.today(), months=1), "month"))
    employee_id = fields.Many2one('hr.employee', string='Employee')
    payment_mode = fields.Selection([
        ("own_account", "Employee (to reimburse)"),
        ("company_account", "Company")
        ], default='own_account',string="Paid By")

    def generate_report(self):
        data = {
            'form_data': self.read()[0],
        }
        return self.env.ref('optifocus.expenses_payments_report').report_action(self, data=data)

