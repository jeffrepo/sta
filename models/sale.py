# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import datetime
import dateutil.parser
from odoo.exceptions import UserError
import ast
import logging

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    mostrar_cotizacion = fields.Boolean('Mostrar')
    dias = fields.Float('Dias')
    noches = fields.Float('noches')


    @api.multi
    @api.onchange('dias','noches')
    def on_change_linea(self):
        for record in self:
            if record.dias > 0:
                record.price_unit = (record.product_uom_qty * record.price_unit )*record.dias
            elif record.noches > 0:
                record.price_unit = (record.product_uom_qty * record.price_unit )*record.noches
