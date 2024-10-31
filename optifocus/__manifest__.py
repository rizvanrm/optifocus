{
    'name': 'Optifocus',
    'category': 'Healthcare/Optical',
    'summary': 'A complete solution to Multi Store Optical Clinic Business with features Insurance, Inventory, Sales, Purchase, Accounting, Patients,Prescriptions, Business Intelligence Report.',
    'version': '16.0.0',
    'author': 'Rizvan Mirza',
    'email': 'rizvan_rm@yahoo.co.in',
    'price': '999.99',
    'currency': 'USD',
    'license': 'LGPL-3',
    'data': [

        'security/security.xml',
        'data/user.xml',


        'views/res_config_settings_views.xml',

        'insurance/views/insurance_company.xml',
        'insurance/views/insurance_policy.xml',
        'insurance/views/insurance_report.xml',
        'insurance/views/insurance_claim_views.xml',
        'insurance/wizard/audit_claim.xml',
        'insurance/wizard/claim_invoice.xml',
        'insurance/wizard/group_summary_statement.xml',
        'insurance/wizard/claim_export_report.xml',
        'insurance/views/report_audit_claim.xml',
        'insurance/views/report_claim_invoice.xml',
        'insurance/views/report_claim.xml',
        'insurance/views/report_group_summary_statement.xml',
        'insurance/views/insurance_menus.xml',



        'optical/views/prescription.xml',
        'optical/report/prescription_reports.xml',
        'optical/report/report_prescription.xml',
        'optical/views/optical_menus.xml',



        'product/data/ir_sequence_data.xml',
        'product/views/product_template.xml',


        'product/views/product_category.xml',
        'product/views/product_brand.xml',
        'product/views/product_views.xml',
        'product/report/product_product_templates.xml',
        'product/report/product_reports.xml',
        'product/report/product_template_templates.xml',


        'stock/views/stock_scrap_views.xml',
        'stock/views/product_views.xml',
        'stock/views/stock_report.xml',
        'stock/views/inventory_adjustment_history.xml',
        'stock/views/stock_quant_views.xml',
        'stock/views/stock_picking_views.xml',
        'stock/views/stock_move_views.xml',



        'stock/wizard/stock_export_report.xml',
        'stock/wizard/undelivered_orders.xml',
        'stock/wizard/inventory_adjustment.xml',


        'stock/views/report_stock_pdf.xml',
        'stock/views/report_undelivered_orders.xml',
        'stock/views/report_inventory_adjustment.xml',
        'stock/views/report_inventory_adjustment_history.xml',
        'stock/report/report_stockpicking_operations.xml',
        'stock/report/report_deliveryslip.xml',


        'sale/views/res_partner_views.xml',

        'sale/views/sale_order_discount.xml',
        'sale/views/sale_report.xml',
        'sale/views/product_views.xml',
        'sale/views/res_config_settings_views.xml',
        'sale/wizard/customer_payments.xml',


        'sale/report/sale_report_views.xml',
        'sale/report/sale_purchase.xml',

        'sale/views/report_customer_payments.xml',

        'account/views/account_move_views.xml',
        'account/views/account_payment_view.xml',
        'account/views/partner_view.xml',
        'account/wizard/account_payment_register_views.xml',


        'settings/views/res_company_views.xml',

        'purchase/views/purchase_views.xml',
        'purchase/report/purchase_quotation_templates.xml',
        'purchase/report/purchase_order_templates.xml',

        'sale/views/sale_order.xml',
        'sale/report/ir_actions_report_templates.xml',
        'sale/report/patient_prescription_templates.xml',
        'sale/report/report_insurance_totals.xml',


        'l10n_gcc_invoice/views/report_invoice.xml',
        'account/views/report_invoice.xml',

        'users/views/res_users_views.xml',


        'data/product_attribute.xml',
        'data/product_category.xml',
        'data/product_brand.xml',
        'data/product_product.xml',
        'data/product_pricelist.xml',
        'data/res_partner.xml',
        'data/res_company.xml',
        'data/insurance_company.xml',
        'data/insurance_policy.xml',
        'data/hr_demo.xml',
        'data/hr_data.xml',
        'data/config_setting.xml',

        'security/ir.model.access.csv',




         ],
    # 'depends': ['stock','sale','hr', 'sale_loyalty','purchase','account','report_xlsx'],
        'depends': ['stock','sale','hr', 'sale_loyalty','purchase','account'],

    'installable': True,
    'images' : ['static/description/banner.png'],
}
