# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class StockLotInheritEmc(models.Model):
    _name = 'stock.quant'
    _inherit = ['stock.quant', 'pos.load.mixin']
    _description = 'stock.lot.inherit'


    def _load_pos_data_fields(self, config_id):
        return ['location_id', 'product_id', 'lot_id','inventory_quantity_auto_apply','quantity']