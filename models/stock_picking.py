# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    mrp_ids = fields.Many2many('mrp.production','sta_stock_mrp_rel',string='Producciones')
