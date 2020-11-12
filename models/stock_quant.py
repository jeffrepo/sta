# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from psycopg2 import OperationalError, Error

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero

import logging

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    subproductos_ids = fields.One2many('stock.quant.subproducto_linea','quant_id','Subproductos Lineas', copy=True)

    # @api.multi
    # @api.onchange('product_id','quantity')
    # def _get_lista_materiales(self):
    #     logging.warn('jeje')
    #     for rec in self:
    #         vals = {}
    #         logging.warn('prueba lista stock')
    #         datos = []
    #         lista_material_id = self.env['mrp.bom'].search([('product_id','=',rec.product_id.id)])
    #         if lista_material_id:
    #             for linea in lista_material_id.bom_line_ids:
    #                 # vals.update({'subproductos_ids': [(0,0,{'producto_id': linea.product_id.id,'cantidad':linea.product_qty * rec.quantity})]  })
    #                 datos.append({'producto_id': linea.product_id.id,'cantidad':linea.product_qty})
    #                 # rec.subproductos_ids = [(0,0,{'producto_id': linea.product_id.id,'cantidad':linea.product_qty * rec.quantity})]
    #             rec.update({'subproductos_ids': [(0,0,datos)]  })

    @api.model
    def _update_available_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, in_date=None):
        res = super(StockQuant, self)._update_available_quantity(product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, in_date=None)
        self = self.sudo()
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=True)

        for quant in quants:
            logging.warn(self)
            lista_material_id = self.env['mrp.bom'].search([('product_tmpl_id','=',quant.product_id.product_tmpl_id.id)])
            datos = []
            logging.warn(lista_material_id)
            if lista_material_id:
                if len(quant.subproductos_ids) > 0:
                    quant.subproductos_ids.unlink()
                for linea in lista_material_id.bom_line_ids:
                    # vals.update({'subproductos_ids': [(0,0,{'producto_id': linea.product_id.id,'cantidad':linea.product_qty * rec.quantity})]  })
                    # datos.append({'producto_id': linea.product_tmpl_id.id,'cantidad':linea.product_qty})
                    # rec.subproductos_ids = [(0,0,{'producto_id': linea.product_id.id,'cantidad':linea.product_qty * rec.quantity})]
                    subproducto_linea = self.env['stock.quant.subproducto_linea'].create({
                        'quant_id': quant.id,
                        'producto_id': linea.product_id.id,
                        'cantidad':  linea.product_qty * quant.quantity
                    })
                    logging.warn(subproducto_linea)
                    datos.append(subproducto_linea.id)
                # quant.subproductos_ids = [(0,0,datos)]

            logging.warn(datos)
        return res


class StockQuantSubproductoLinea(models.Model):
    _name = 'stock.quant.subproducto_linea'

    quant_id = fields.Many2one('stock.quant','Quant')
    producto_id = fields.Many2one('product.product','Producto')
    cantidad = fields.Float('Cantidad')

    # @api.multi
    # def unlink(self):
    #     return super(MrpProduction, self).unlink()
