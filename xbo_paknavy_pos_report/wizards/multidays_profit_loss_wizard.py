# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, date, datetime
from odoo.exceptions import ValidationError
from collections import defaultdict
from datetime import datetime , time , timedelta
from pytz import timezone, UTC
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from collections import defaultdict


class MultidaysProfitLossWizard(models.TransientModel):
    _name = "multidays.profit.loss.wizard"
    _description = "Multidays Profit Loss Wizard"

    date_from = fields.Date(string='Date From', required= True)
    date_to = fields.Date(string='Date To', required= True)
    pos_payment_method = fields.Many2one(comodel_name='pos.payment.method', string='Payment Method')
    pos_config_id = fields.Many2one(comodel_name='pos.config', string='POS')



    def action_print(self):
        datas = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'pos_payment_method': self.pos_payment_method.id if self.pos_payment_method else False,
            'pos_config_id': self.pos_config_id.id if self.pos_config_id else False,
        }
        domain = []
        domain.append(('date_order', '>=', self.date_from))
        domain.append(('date_order', '<=', self.date_to))

        if self.pos_payment_method:
            domain.append((
                'payment_ids.payment_method_id',
                '=',
                self.pos_payment_method.id
            ))
        if self.pos_config_id:
            domain.append((
                'session_id.config_id',
                '=',
                self.pos_config_id.id
            ))

        pos_order_object = self.env['pos.order'].search(domain)

        if pos_order_object:

            return self.env.ref('xbo_paknavy_pos_report.action_multidays_profit_loss_report').report_action(self,datas)
        else:
            raise ValidationError('No Record Found!')


class action_multidays_profit_loss_report(models.AbstractModel):
    _name = 'report.xbo_paknavy_pos_report.multidays_profit_loss_template'
    _description = 'MultiDays Profit/Loss Report'

    @api.model
    def _get_report_values(self, docids, data):
        domain = []
        date_from = data['date_from']
        date_to = data['date_to']
        pos_payment_method = data.get('pos_payment_method')
        pos_config_id = data.get('pos_config_id')

        if isinstance(date_from, str):
            date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        if isinstance(date_to, str):
            date_to = datetime.strptime(date_to, "%Y-%m-%d").date()

        if date_from and date_to:
            domain.append(('date_order', '>=', date_from))
            domain.append(('date_order', '<=', date_to))

        if pos_payment_method:
            domain.append((
                'payment_ids.payment_method_id',
                '=',
                pos_payment_method
            ))

        if pos_config_id:
            domain.append((
                'session_id.config_id',
                '=',
                pos_config_id
            ))
        orders = self.env['pos.order'].search(domain)

        payment_method_name = ''
        if pos_payment_method:
            payment_method = self.env['pos.payment.method'].browse(
                pos_payment_method
            )
            payment_method_name = payment_method.name

        pos_config_name = ''
        if pos_config_id:
            pos_conf = self.env['pos.config'].browse(
                pos_config_id
            )
            pos_config_name = pos_conf.name

        # user_tz = self.env.user.tz or 'UTC'
        # local_tz = timezone(user_tz)
        #
        # # localize date_from & date_to into UTC
        # date_from_local = datetime.strptime(data['date_from'], "%Y-%m-%d")
        # date_to_local = datetime.strptime(data['date_to'], "%Y-%m-%d")
        #
        # # full day range in local tz
        # date_from_dt = local_tz.localize(datetime.combine(date_from_local, datetime.min.time())).astimezone(UTC)
        # date_to_dt = local_tz.localize(datetime.combine(date_to_local, datetime.max.time())).astimezone(UTC)
        #
        # # search orders in UTC range
        # orders = self.env['pos.order'].search([
        #     ('date_order', '>=', date_from_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
        #     ('date_order', '<=', date_to_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
        # ])

        print(len(orders))




        code_names = ['Sr', 'Product', 'Quantity', 'Unit Price', 'Discount', 'Total']
        products = []
        sr_no = 1

        # group orders by date
        orders_by_date = defaultdict(list)
        for order in orders:
            order_date = order.date_order.date()
            orders_by_date[order_date].append(order)

        # sort by date
        for order_date in sorted(orders_by_date.keys()):
            lines_in_date = self.env['pos.order.line'].browse([])
            for order in orders_by_date[order_date]:
                lines_in_date |= order.lines

            if not lines_in_date:
                continue

            # date header row
            products.append({'date_name': order_date.strftime('%d-%m-%Y')})

            # product-wise totals for this date (key = product_id.id)
            product_totals = defaultdict(lambda: {
                'name': '',
                'quantity': 0.0,
                'sale_price': 0.0,
                'discount': 0.0,
                'margin': 0.0,
            })

            for line in lines_in_date:
                p = product_totals[line.product_id.id]
                p['name'] = line.product_id.display_name
                p['quantity'] += line.qty
                p['sale_price'] = line.price_unit
                p['discount'] += ((line.price_unit * line.qty) * line.discount) / 100
                p['margin'] += (line.price_unit * line.qty) - (((line.price_unit * line.qty) * line.discount) / 100)

            # product rows
            for pid, vals in product_totals.items():
                products.append({
                    'Sr': sr_no,
                    'Product': vals['name'],
                    'Quantity': "{:,.1f}".format(vals['quantity']),
                    'Unit Price': "{:,.1f}".format(vals['sale_price']),
                    'Discount': "{:,.1f}".format(vals['discount']),
                    'Total': "{:,.1f}".format(vals['margin']),
                    'Product_wise': True,
                })
                sr_no += 1

            # date subtotal
            date_total = defaultdict(float)
            for vals in product_totals.values():
                for key in ['quantity', 'sale_price', 'discount', 'margin']:
                    date_total[key] += vals[key]

            products.append({
                'Sr': '',
                'Product': 'Total',
                'Quantity': "{:,.1f}".format(date_total['quantity']),
                'Discount': "{:,.1f}".format(date_total['discount']),
                'Total': "{:,.1f}".format(date_total['margin']),
                'datewise': True,
            })

        # grand total
        grand_total = defaultdict(float)
        all_lines = orders.mapped('lines')
        for line in all_lines:
            grand_total['quantity'] += line.qty
            grand_total['sale_price'] = line.price_unit
            grand_total['discount'] += ((line.price_unit * line.qty) * line.discount) / 100
            grand_total['margin'] += (line.price_unit * line.qty) - (((line.price_unit * line.qty) * line.discount) / 100)

        grand_total_row = {
            'Sr': '',
            'Product': 'Grand Total',
            'Quantity': "{:,.1f}".format(grand_total['quantity']),
            'Discount': "{:,.1f}".format(grand_total['discount']),
            'Total': "{:,.1f}".format(grand_total['margin']),
        }

        return {
            'from_date': date_from.strftime('%d-%m-%Y') if date_from else '',
            'to_date': date_to.strftime('%d-%m-%Y') if date_to else '',
            'code_names': code_names,
            'products': products,
            'grand_total': grand_total_row,
            'pos_payment_method': payment_method_name,
            'pos_config_name': pos_config_name,
        }