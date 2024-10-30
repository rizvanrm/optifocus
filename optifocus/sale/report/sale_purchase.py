from odoo import api, fields, models, tools


class SalePurchase(models.Model):
    _name = "sale.purchase"
    _description = "Sales Purchase Analysis"
    _auto = False
    _rec_name = 'bill_date'
    _order = 'bill_date asc'

    @api.model
    def _get_done_states(self):
        return ['sale', 'done']

    vendor_bill = fields.Char('Vendor Bill', readonly=True)
    vendor_id = fields.Many2one('res.partner', 'Vendor', readonly=True)
    bill_date = fields.Datetime('Bill Date', readonly=True)
    ref = fields.Char('Bill Reference', readonly=True)
    purchase_order = fields.Char(
        string='Purchase Order',
        readonly=True,
        help="The document(s) that generated the invoice.",
    )
    sale_order = fields.Char('Sale Order', copy=False,
                         help="Reference of the document that generated this purchase order "
                              "request (e.g. a sales order)")
    customer_id = fields.Many2one( comodel_name='res.partner', string="Customer")
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    quantity=fields.Float('Quantity',readonly=True)
    price_unit = fields.Float('Price', readonly=True)
    discount = fields.Float('Discount', readonly=True)
    price_subtotal = fields.Float('Subtotal', readonly=True)

    def _with(self):
        return ""

    def _select(self):
        select_ = f"""
            aml.id AS id,
            am.name AS vendor_bill,
            am.partner_id AS vendor_id,
            am.invoice_date AS bill_date,
            am.ref AS ref,
            am.invoice_origin AS purchase_order,
            po.origin AS sale_order,
            so.partner_id as customer_id,
            aml.product_id AS product_id,
            aml.quantity AS quantity,
            aml.price_unit AS price_unit,
            aml.discount AS discount,
            aml.price_subtotal AS price_subtotal
            """
        additional_fields_info = self._select_additional_fields()
        template = """,
            %s AS %s"""
        for fname, query_info in additional_fields_info.items():
            select_ += template % (query_info, fname)

        return select_

    def _case_value_or_one(self, value):
        return f"""CASE COALESCE({value}, 0) WHEN 0 THEN 1.0 ELSE {value} END"""


    def _select_additional_fields(self):
        """Hook to return additional fields SQL specification for select part of the table query.

        :returns: mapping field -> SQL computation of field, will be converted to '_ AS _field' in the final table definition
        :rtype: dict
        """
        return {}

    def _from(self):
        return """
            account_move_line aml
            LEFT JOIN account_move am ON am.id=aml.move_id
            LEFT JOIN purchase_order po ON po.name=am.invoice_origin
            LEFT JOIN sale_order so ON so.name=po.origin
            """

    def _where(self):
        return """
           aml.display_type = 'product' 
           and am.move_type ='in_invoice'
           """

    def _query(self):
        with_ = self._with()
        return f"""
            {"WITH" + with_ + "(" if with_ else ""}
            SELECT {self._select()}
            FROM {self._from()}
            WHERE {self._where()}        
            {")" if with_ else ""}
        """

    @property
    def _table_query(self):
        return self._query()
