# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.tools import float_compare
import logging

# class MrpProduction(models.Model):
#     _inherit = 'mrp.production'
#
#     def _get_document_iterate_key(self, move_raw_id):
#         return super(MrpProduction, self)._get_document_iterate_key(move_raw_id) or 'created_purchase_line_id'
#
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    precio_original = fields.Float('Precio original')

#     def _update_received_qty(self):
#         super(PurchaseOrderLine, self)._update_received_qty()
#         albaran_id = False
#         fabricaciones = []
#         produccion = False
#         for line in self.filtered(lambda x: x.move_ids and x.product_id.id not in x.move_ids.mapped('product_id').ids):
#             bom = self.env['mrp.bom']._bom_find(product=line.product_id, company_id=line.company_id.id)
#             logging.warn(bom)
#             producto = self.env['product.product'].search([('product_tmpl_id','=',bom.product_tmpl_id.id)])
#             logging.warn(producto)
#             logging.warn(line)
#             if bom and bom.type == 'normal':
#                 logging.warn('prueba1')
#                 line.qty_received = line._get_bom_delivered(bom=bom)
#
#                 nueva_fabricacion = self.env['mrp.production'].create({
#                     'product_id': producto.id,
#                     'bom_id': bom.id,
#                     'origin': line.order_id.name,
#                     'product_qty': line._get_bom_delivered(bom=bom),
#                     'product_uom_id': bom.product_tmpl_id.uom_po_id.id,
#                     'state': 'confirmed'
#                 })
#                 nueva_fabricacion.action_assign()
#                 nueva_fabricacion.open_produce_product()
#                 albaran_id = self.env['stock.picking'].search([('origin','=',line.order_id.name)])
#
#                 if bom and bom.type == 'normal':
#                     line.qty_received = line._get_bom_delivered(bom=bom)
#
#                 fabricaciones.append(nueva_fabricacion.id)
#                 product_produce_id = self.env['mrp.product.produce'].search([('production_id','=',nueva_fabricacion.id)])
#                 product_produce_id.do_produce()
#
#         if albaran_id:
#             albaran_id.mrp_ids = [(6, 0, fabricaciones)]
#
#
#     # def _get_bom_delivered(self, bom=False):
#     #     self.ensure_one()
#     #     logging.warn('2')
#     #     # In the case of a kit, we need to check if all components are shipped. Since the BOM might
#     #     # have changed, we don't compute the quantities but verify the move state.
#     #     if bom:
#     #         logging.warn(bom)
#     #         moves = self.move_ids.filtered(lambda m: m.picking_id and m.picking_id.state != 'cancel')
#     #         logging.warn(moves)
#     #         bom_delivered = all([move.state == 'done' for move in moves])
#     #         logging.warn(bom_delivered)
#     #         if bom_delivered:
#     #             return self.product_qty
#     #         else:
#     #             return 0.0
#
#     # def _get_upstream_documents_and_responsibles(self, visited):
#     #     logging.warn('3')
#     #     return [(self.order_id, self.order_id.user_id, visited)]
#
# class StockMove(models.Model):
#     _inherit = 'stock.move'
#
#     def _prepare_phantom_move_values(self, bom_line, quantity):
#         logging.warn('4')
#         vals = super(StockMove, self)._prepare_phantom_move_values(bom_line, quantity)
#         logging.warn(vals)
#         if self.purchase_line_id:
#             vals['purchase_line_id'] = self.purchase_line_id.id
#         return vals
#
#     def action_explode(self):
#         if not self.picking_type_id:
#             return self
#         bom = self.env['mrp.bom'].sudo()._bom_find(product=self.product_id, company_id=self.company_id.id)
#         if 'PO' in self.origin:
#             if not bom or bom.type != 'normal':
#                 logging.warn('compra')
#                 return self
#         elif 'WH' in self.origin:
#             if (not bom or bom.type == 'normal'):
#                 logging.warn('fABTI')
#                 return self
#         phantom_moves = self.env['stock.move']
#         processed_moves = self.env['stock.move']
#         factor = self.product_uom._compute_quantity(self.product_uom_qty, bom.product_uom_id) / bom.product_qty
#         boms, lines = bom.sudo().explode(self.product_id, factor, picking_type=bom.picking_type_id)
#         for bom_line, line_data in lines:
#             phantom_moves += self._generate_move_phantom(bom_line, line_data['qty'])
#
#         for new_move in phantom_moves:
#             processed_moves |= new_move.action_explode()
# #         if not self.split_from and self.procurement_id:
# #             # Check if procurements have been made to wait for
# #             moves = self.procurement_id.move_ids
# #             if len(moves) == 1:
# #                 self.procurement_id.write({'state': 'done'})
#         if processed_moves and self.state == 'assigned':
#             # Set the state of resulting moves according to 'assigned' as the original move is assigned
#             processed_moves.write({'state': 'assigned'})
#         # delete the move with original product which is not relevant anymore
#         self.sudo().unlink()
#         return processed_moves
