# -*- coding: utf-8 -*-

from odoo import models, fields

class Stocklocation(models.Model):
    _name = 'stock.location'
    _inherit = ['stock.location','pos.load.mixin']


    # This function is used to load fields into the POS.
    def _load_pos_data_fields(self, config_id):
        # Define which fields to send to the POS frontend
        return ['id', 'name']

