from odoo import api, fields, models


class ClaimDetailsAB(models.AbstractModel):
    _name = 'report.optifocus.report_audit_claim'
    _description = 'Claim Details'

    @api.model
    def _get_report_values(self, docids, data=None):

        date_from = data.get('form_data').get('date_from')
        date_to = data.get('form_data').get('date_to')
        insurance_id = data.get('form_data').get('insurance_id')

        domain = []
        domain += [('insurance_id', '=', insurance_id[0])]
        domain += [('approval_date', '>=', date_from)]
        domain += [('approval_date', '<=', date_to)]

        claim_ids=self.env['insurance.claim'].search(domain)

        return {
            'request': self,
            'claim_ids': claim_ids,
            'insurance_id': insurance_id,
            'date_from':date_from,
            'date_to': date_to,
            'test' : 'test1'
        }

