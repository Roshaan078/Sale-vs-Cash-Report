# -*- coding: utf-8 -*-
from odoo import models
from datetime import datetime

class SaleVsCashReport(models.AbstractModel):
    _name = 'report.ask_sale_vs_cash_report.sale_vs_cash_template'
    _description = 'Sale vs Cash Report'

    def _get_report_values(self, docids, data=None):

        partner_ids = data.get('partner_ids', [])
        date_from = data.get('date_from') or '2000-01-01'
        date_to = data.get('date_to') or datetime.today().date()

        if not partner_ids:
            return {
                'docs': [],
                'company': self.env.company,
                'date_from': date_from,
                'date_to': date_to
            }

        partner_ids_tuple = tuple(partner_ids)

        query = """
                SELECT rp.id,
                       rp.name      AS partner_name,
                       rp.user_id   AS salesperson_id,
                       ru_partner.name AS salesperson_name,

                       COALESCE(SUM(CASE
                                        WHEN am.date < %s
                                            THEN aml.debit - aml.credit
                                        ELSE 0
                           END), 0) AS opening_balance,

                       COALESCE(SUM(CASE
                                        WHEN am.date BETWEEN %s AND %s
                                            AND (am.move_type = 'out_invoice'
                                                OR (am.move_type = 'entry' AND aml.debit > 0))
                                            THEN aml.debit
                                        ELSE 0
                           END), 0) AS total_sale,

                       COALESCE(SUM(CASE
                                        WHEN am.date BETWEEN %s AND %s
                                            AND (am.move_type = 'out_refund'
                                                OR (am.move_type = 'entry' AND aml.credit > 0))
                                            THEN aml.credit
                                        ELSE 0
                           END), 0) AS total_cash

                FROM account_move_line aml
                         JOIN account_move am ON am.id = aml.move_id
                         JOIN account_account acc ON acc.id = aml.account_id
                         JOIN res_partner rp ON rp.id = aml.partner_id
                         LEFT JOIN res_users ru ON ru.id = rp.user_id
                         LEFT JOIN res_partner ru_partner ON ru_partner.id = ru.partner_id


                WHERE aml.partner_id IN %s
                  AND am.state = 'posted'
                  AND acc.account_type = 'asset_receivable'
                  AND am.date <= %s

                   GROUP BY rp.id, rp.name, rp.user_id, ru_partner.name
                    ORDER BY rp.name
                """

        params = (
            date_from,
            date_from, date_to,
            date_from, date_to,
            partner_ids_tuple,
            date_to
        )

        # ✅ Execute first
        self.env.cr.execute(query, params)
        docs = self.env.cr.dictfetchall()

        # ✅ Then calculate balance
        for line in docs:
            line['balance'] = (
                    line.get('opening_balance', 0)
                    + line.get('total_sale', 0)
                    - line.get('total_cash', 0)
            )
            line['salesperson'] = line.get('salesperson_name')

        return {
            'docs': docs,
            'company': self.env.company,
            'date_from': date_from,
            'date_to': date_to,
        }
