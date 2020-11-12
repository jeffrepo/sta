# -*- encoding: utf-8 -*-

from odoo import api, models, fields
import logging

class ReporteDiario(models.AbstractModel):
    _name = 'report.sta.reporte_inventario_produccion'

    def inventarios(self,datos):
        datos = []
        invenario_id = self.env['stock.quant'].search([('product_id','=',datos['producto_id'].id),('location_id','=',datos['ubicacion_id'].id)])
        lista_material_id = self.env['mrp.bom'].search([('product_id','=',datos['producto_id'].id)])
        if lista_material_id:
            for linea in lista_material_id.bom_line_ids:
                subproductos= {
                    'nombre': linea.product_id.name,
                    'cantidad': linea.product_qty
                }
        return datos

    @api.model
    def _get_report_values(self, docids, data=None):
        return self.get_report_values(docids, data)

    @api.model
    def get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))

        # diario = self.env['account.move.line'].browse(data['form']['cuentas_id'][0])

        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'inventarios': self.inventarios,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
