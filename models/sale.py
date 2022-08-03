# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import datetime
import dateutil.parser
from odoo.exceptions import UserError
import ast
import logging

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('sale_order_option_ids')
    def on_change_linea_options(self):
        for record in self:
            total_gastos = 0
            if record.sale_order_option_ids:
                for linea in record.sale_order_option_ids:
                    total_gastos += linea.price_unit

            if record.order_line:
                for linea in record.order_line:
                    if linea.product_id.agrupar_gastos:
                        linea.product_uom_qty = 1
                        linea.price_unit = total_gastos


# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     mostrar_cotizacion = fields.Boolean('Mostrar')
#     dias = fields.Float('Dias')
#     noches = fields.Float('noches')

    # @api.multi
    # @api.onchange('dias','noches')
    # def on_change_linea(self):
    #     for record in self:
    #         if record.dias > 0:
    #             record.price_unit = (record.product_uom_qty * record.price_unit )*record.dias
    #         elif record.noches > 0:
    #             record.price_unit = (record.product_uom_qty * record.price_unit )*record.noches

class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    costo = fields.Float('Costo')

    @api.onchange('product_id','quantity','costo')
    def on_change_linea(self):
        for record in self:
            if record.product_id:
                product = record.product_id.with_context(
                    partner=record.order_id.partner_id,
                    quantity=record.quantity,
                    date=record.order_id.date_order,
                    pricelist=record.order_id.pricelist_id.id,
                    uom=record.uom_id.id,
                    standard_price = 2,
                )
                record.product_id.standard_price = record.costo
                precio = record.order_id.pricelist_id.get_product_price(product, record.uom_id, record.order_id.partner_id, record.order_id.date_order, record.uom_id.id)
                logging.warning('precio')
                logging.warning(precio)
                record.price_unit = precio
