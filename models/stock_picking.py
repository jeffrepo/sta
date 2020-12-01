# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api
import logging

# class StockPicking(models.Model):
#     _inherit = 'stock.picking'
#
#     mrp_ids = fields.Many2many('mrp.production','sta_stock_mrp_rel',string='Producciones')

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _get_price_unit(self):
        self.ensure_one()
        if self.purchase_line_id:
            costo = 0
            prorrateos = self.env['purchase.prorrateo'].search([('compra_ids','!=',False)])
            if prorrateos:
                for prorrateo in prorrateos:
                    if self.purchase_line_id.order_id.id in prorrateo.compra_ids.ids:
                        for linea in prorrateo.compra_prorrateo_linea:
                            if self.product_id.id == linea.product_id.id:
                                costo = linea.costo_unidad
                                logging.warn('si lo encuentra')
                                return costo
            # for l in self.purchase_line_id.order_id.poliza_id.lineas_ids:
            #     if l.producto_id.id == self.product_id.id:

        return super(StockMove, self)._get_price_unit()
