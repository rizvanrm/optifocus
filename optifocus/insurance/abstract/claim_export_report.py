from odoo import api, fields, models


class ClaimExportReportAB(models.AbstractModel):
    _name = 'report.optifocus.report_claim_export'
    _inherit='report.report_xlsx.abstract'
    _description = 'Claim Export.'

    def generate_xlsx_report(self, workbook, data,product_ids1):
        domain = []
        date_from = data.get('form_data').get('date_from')
        date_to = data.get('form_data').get('date_to')
        insurance_id = data.get('form_data').get('insurance_id')

        domain += [('claim_id.insurance_id', '=', insurance_id[0])]
        domain += [('claim_id.approval_date', '>=', date_from)]
        domain += [('claim_id.approval_date', '<=', date_to)]

        claim_line_ids = self.env['insurance.claim.line'].search(domain)

        report_name = 'Claims'
        sheet=workbook.add_worksheet(report_name[:31])
        bold=workbook.add_format({'bold':True})

        sheet.write(0, 0, 'Claim Reference',bold)
        sheet.write(0, 1, 'Member',bold)
        sheet.write(0, 2, 'Gender',bold)
        sheet.write(0, 3, 'Mobile',bold)
        sheet.write(0, 4, 'Doctor', bold)
        sheet.write(0, 5, 'Prescription Type', bold)
        sheet.write(0, 6, 'Right Sphere', bold)
        sheet.write(0, 7, 'Right Cylinder', bold)
        sheet.write(0, 8, 'Right Axis', bold)
        sheet.write(0, 9, 'Right VA', bold)
        sheet.write(0, 10, 'Right Addition', bold)
        sheet.write(0, 11, 'Left Sphere', bold)
        sheet.write(0, 12, 'Left Cylinder', bold)
        sheet.write(0, 13, 'Left Axis', bold)
        sheet.write(0, 14, 'Left VA', bold)
        sheet.write(0, 15, 'Left Addition', bold)
        sheet.write(0, 16, 'Distance IPD', bold)
        sheet.write(0, 17, 'Addition IPD', bold)
        sheet.write(0, 18, 'Insurance Company',bold)
        sheet.write(0, 19, 'Insurance Plan', bold)
        sheet.write(0, 20, 'Insurance Discount %', bold)
        sheet.write(0, 21, 'Member Discount %', bold)
        sheet.write(0, 22, 'Policy Holder',bold)
        sheet.write(0, 23, 'Policy Inception Date', bold)
        sheet.write(0, 24, 'Policy Expiry Date', bold)
        sheet.write(0, 25, 'Co-Insurance Type', bold)
        sheet.write(0, 26, 'Co-Insurance %', bold)
        sheet.write(0, 27, 'Co-Insurance Max Up To', bold)
        sheet.write(0, 28, 'Class',bold)
        sheet.write(0, 29, 'Membership No',bold)
        sheet.write(0, 30, 'Approval No',bold)
        sheet.write(0, 31, 'Approval Date',bold)
        sheet.write(0, 32, 'Branch',bold)
        sheet.write(0, 33,  'Service Code',bold)
        sheet.write(0, 34,  'Description',bold)
        sheet.write(0, 35,  'Quantity',bold)
        sheet.write(0, 36,  'Unit Price',bold)
        sheet.write(0, 37,  'Unit Approved',bold)
        sheet.write(0, 38,  'Approved',bold)
        sheet.write(0, 39,  'Claim Discount',bold)
        sheet.write(0, 40,  'Member Discount',bold)
        sheet.write(0, 41,  'Discount',bold)
        sheet.write(0, 42,  'Claim',bold)
        sheet.write(0, 43,  'Co-Insurance',bold)
        sheet.write(0, 44,  'Additional',bold)
        sheet.write(0, 45,  'Member Amount',bold)
        sheet.write(0, 46,  'Subtotal',bold)

        row=0
        for claim_line_id in claim_line_ids:
            row += 1
            sheet.write(row, 0,claim_line_id.claim_id.name)
            sheet.write(row, 1, claim_line_id.claim_id.partner_id.name)
            sheet.write(row, 2, dict(claim_line_id.claim_id._fields['gender']._description_selection(claim_line_id.claim_id.env))[claim_line_id.claim_id.gender])
            sheet.write(row, 3, claim_line_id.claim_id.mobile)
            sheet.write(row, 4, claim_line_id.claim_id.doctor.name)
            sheet.write(row, 5, dict(
                claim_line_id.claim_id._fields['prescription_type']._description_selection(claim_line_id.claim_id.env))[
                claim_line_id.claim_id.prescription_type])
            sheet.write(row, 6, claim_line_id.claim_id.r_sph)
            sheet.write(row, 7, claim_line_id.claim_id.r_cyl)
            sheet.write(row, 8, claim_line_id.claim_id.r_axis)
            sheet.write(row, 9, claim_line_id.claim_id.r_va)
            sheet.write(row, 10, claim_line_id.claim_id.r_add)
            sheet.write(row, 11, claim_line_id.claim_id.l_sph)
            sheet.write(row, 12, claim_line_id.claim_id.l_cyl)
            sheet.write(row, 13, claim_line_id.claim_id.l_axis)
            sheet.write(row, 14, claim_line_id.claim_id.l_va)
            sheet.write(row, 15, claim_line_id.claim_id.l_add)
            sheet.write(row, 16, claim_line_id.claim_id.ipd_distance)
            sheet.write(row, 17, claim_line_id.claim_id.ipd_addition)
            sheet.write(row, 18, claim_line_id.claim_id.insurance_id.name)
            sheet.write(row, 19, claim_line_id.claim_id.insurance_company_plan.name)
            sheet.write(row, 20, claim_line_id.claim_id.insurance_discount)
            sheet.write(row, 21, claim_line_id.claim_id.member_discount)
            sheet.write(row, 22, claim_line_id.claim_id.policy_id.policy_holder)
            sheet.write(row, 23, str(claim_line_id.claim_id.inception_date))
            sheet.write(row, 24, str(claim_line_id.claim_id.expiry_date))
            sheet.write(row, 25, claim_line_id.claim_id.co_insurance_type)
            sheet.write(row, 26, claim_line_id.claim_id.co_insurance_percent)
            sheet.write(row, 27, claim_line_id.claim_id.up_to)
            sheet.write(row, 28, claim_line_id.claim_id.policy_class_id.name)
            sheet.write(row, 29, claim_line_id.claim_id.membership_no)
            sheet.write(row, 30, claim_line_id.claim_id.approval_no)
            sheet.write(row, 31, str(claim_line_id.claim_id.approval_date))
            sheet.write(row, 32, claim_line_id.claim_id.company_id.name)
            sheet.write(row, 33, ('' if not claim_line_id.product_id.barcode else claim_line_id.product_id.barcode ))
            sheet.write(row, 34, claim_line_id.name)
            sheet.write(row, 35, claim_line_id.product_uom_qty)
            sheet.write(row, 36, claim_line_id.price_unit)
            sheet.write(row, 37, claim_line_id.approved_unit)
            sheet.write(row, 38, claim_line_id.approved_subtotal)
            sheet.write(row, 39, claim_line_id.claim_discount_subtotal)
            sheet.write(row, 40, claim_line_id.member_discount_subtotal)
            sheet.write(row, 41, claim_line_id.discount_subtotal)
            sheet.write(row, 42, claim_line_id.claim_subtotal)
            sheet.write(row, 43, claim_line_id.co_insurance_subtotal)
            sheet.write(row, 44, claim_line_id.additional_subtotal)
            sheet.write(row, 45, claim_line_id.member_subtotal)
            sheet.write(row, 46, claim_line_id.price_subtotal)

