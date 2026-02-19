# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
from io import BytesIO
import base64
import xlwt


class AskSaleVsCashReport(models.TransientModel):
    _name = 'ask_sale_vs_cash_report.ask_sale_vs_cash_report'
    _description = 'ask_sale_vs_cash_report.ask_sale_vs_cash_report'

    partner_name = fields.Many2many('res.partner',string="Customer")
    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")
    opening_balance = fields.Boolean(string="Opening Balance")

    def action_print(self):
        if self.date_from > self.date_to:
            raise UserError("From Date must be less than To Date")

        data = {
            'partner_ids': self.partner_name.ids if self.partner_name else [],  # note `.ids`
            'date_from': self.date_from,
            'date_to': self.date_to,
            'opening_balance': self.opening_balance,  # add this
        }

        return self.env.ref('ask_sale_vs_cash_report.sale_vs_cash_report_action').report_action(self, data=data)

    def action_export_excel(self):
        self.ensure_one()

        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError("From Date must be less than To Date")

        report_model = self.env['report.ask_sale_vs_cash_report.sale_vs_cash_template']

        data = {
            'partner_ids': self.partner_name.ids if self.partner_name else [],
            'date_from': self.date_from,
            'date_to': self.date_to,
        }

        report_values = report_model._get_report_values([], data)
        docs = report_values.get('docs', [])

        docs = sorted(docs, key=lambda x: (x.get('salesperson') or '', x.get('partner_name') or ''))

        # Workbook
        workbook = xlwt.Workbook(encoding="UTF-8")
        sheet = workbook.add_sheet('Sale vs Cash Report', cell_overwrite_ok=True)

        # Styles
        header_style = xlwt.easyxf(
            'font: bold True; align: horiz center; '
            'borders: left thin, right thin, top thin, bottom thin;'
        )

        data_style = xlwt.easyxf(
            'align: horiz left; '
            'borders: left thin, right thin, top thin, bottom thin;'
        )
        grand_total_style = xlwt.easyxf(
            'font: bold True; '
            'pattern: pattern solid, fore_colour light_yellow; '
            'align: horiz right; '
            'borders: left thin, right thin, top thin, bottom thin;',
            num_format_str='#,##0'
        )

        grand_total_text_style = xlwt.easyxf(
            'font: bold True; '
            'pattern: pattern solid, fore_colour light_yellow; '
            'align: horiz left; '
            'borders: left thin, right thin, top thin, bottom thin;'
        )

        grand_total_amount_style = xlwt.easyxf(
            'font: bold True; '
            'pattern: pattern solid, fore_colour light_yellow; '
            'align: horiz right; '
            'borders: left thin, right thin, top thin, bottom thin;',
            num_format_str = '#,##0'
        )

        amount_style = xlwt.easyxf(
            'align: horiz right; '
            'borders: left thin, right thin, top thin, bottom thin;',
            num_format_str='#,##0'
        )

        # Column Width
        for col in range(6):
            sheet.col(col).width = 6000

        row = 0

        # Title
        sheet.write_merge(row, row, 0, 5, 'Sale vs Cash Report', header_style)
        row += 2

        # Period
        sheet.write_merge(row, row, 0, 5,
                          f"Period: {self.date_from} To {self.date_to}",
                          data_style)
        row += 2

        # Headers
        headers = [
            "Salesperson",
            "Customer",
            "Opening Balance",
            "Total Sale",
            "Total Cash",
            "Balance"
        ]

        for col, header in enumerate(headers):
            sheet.write(row, col, header, header_style)

        row += 1

        total_opening = 0
        total_sale = 0
        total_cash = 0
        total_balance = 0

        for line in docs:
            sheet.write(row, 0, line.get('salesperson', ''), data_style)
            sheet.write(row, 1, line.get('partner_name', ''), data_style)
            sheet.write(row, 2, line.get('opening_balance', 0), amount_style)
            sheet.write(row, 3, line.get('total_sale', 0), amount_style)
            sheet.write(row, 4, line.get('total_cash', 0), amount_style)
            sheet.write(row, 5, line.get('balance', 0), amount_style)

            total_opening += line.get('opening_balance', 0)
            total_sale += line.get('total_sale', 0)
            total_cash += line.get('total_cash', 0)
            total_balance += line.get('balance', 0)

            row += 1

        # Grand Total Row
        sheet.write_merge(row, row, 0, 1, "Grand Total", grand_total_text_style)
        sheet.write(row, 2, total_opening, grand_total_amount_style)
        sheet.write(row, 3, total_sale, grand_total_amount_style)
        sheet.write(row, 4, total_cash, grand_total_amount_style)
        sheet.write(row, 5, total_balance, grand_total_amount_style)

        # Save File
        stream = BytesIO()
        workbook.save(stream)

        filename = "Sale_vs_Cash_Report.xls"
        output = base64.encodebytes(stream.getvalue())

        attachment = self.env['ir.attachment'].sudo().create({
            'name': filename,
            'type': 'binary',
            'datas': output,
            'mimetype': 'application/vnd.ms-excel',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
