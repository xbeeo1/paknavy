# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class StockLotInheritEmc(models.Model):
    _name = 'stock.lot'
    _inherit = ['stock.lot', 'pos.load.mixin']
    _description = 'stock.lot.inherit'


    def _load_pos_data_fields(self, config_id):
        return ['name', 'product_id','product_qty']